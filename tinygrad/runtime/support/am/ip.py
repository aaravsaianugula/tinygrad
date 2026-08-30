import ctypes, time, contextlib, functools
from typing import Literal
from tinygrad.helpers import to_mv, data64, lo32, hi32, DEBUG, wait_cond, pad_bytes, getbits
from tinygrad.runtime.autogen.am import am
from tinygrad.runtime.support.amd import import_soc
from tinygrad.runtime.support.memory import AddrSpace

class AM_IP:
  def __init__(self, adev): self.adev = adev
  def init_sw(self): pass # Prepare sw/allocations for this IP
  def init_hw(self): pass # Initialize hw for this IP
  def fini_hw(self): pass # Finalize hw for this IP
  def set_clockgating_state(self): pass # Set clockgating state for this IP

class AM_SOC(AM_IP):
  def init_sw(self):
    self.module = import_soc(self.adev.ip_ver[am.GC_HWIP])
    self.ih_clients = am.enum_soc21_ih_clientid if (ih_soc21:=self.adev.ip_ver[am.GC_HWIP][0] >= 11) else am.enum_soc15_ih_clientid

    self.gfx_ih_clients = [am.SOC21_IH_CLIENTID_GRBM_CP, am.SOC21_IH_CLIENTID_GFX] \
      if ih_soc21 else [am.SOC15_IH_CLIENTID_GRBM_CP] + [getattr(am, f'SOC15_IH_CLIENTID_SE{i}SH') for i in range(4)]
    self.sdma_ih_clients = [] if ih_soc21 else [getattr(am, f'SOC15_IH_CLIENTID_SDMA{i}') for i in range(8)]

    def _ih_srcs(pref:str, hwip:int) -> dict[int, str]:
      gen = self.adev.ip_ver[hwip][0]
      # The autogen SRCID tables cover GFX 9, 11 and 12 but not 10, so on RDNA1/RDNA2 every GFX
      # interrupt resolved to '' -- which is not in the benign set in interrupt_handler, so an
      # ordinary end-of-pipe interrupt set is_err_state and made a healthy device look hung.
      # gfx10's source IDs are the same SOC15 numbers as gfx9: checked against the kernel's
      # ivsrcid/gfx/irqsrcs_gfx_10_1.h, all 24 constants tinygrad carries have identical values,
      # and gfx10 adds only CP_GENERIC_INT=177, which aliases CP_IB1_INTERRUPT_PKT.
      if pref == 'GFX' and gen == 10: gen = 9
      return {getattr(am, k): k[off+9:] for k in dir(am) if k.startswith(f'{pref}_{gen}') and (off:=k.find('__SRCID__')) != -1}

    gfx_srcs, sdma_srcs = _ih_srcs('GFX', am.GC_HWIP), _ih_srcs('SDMA0', am.SDMA0_HWIP)
    self.ih_srcs_names:dict[int, dict[int, str]] = {**{k: gfx_srcs for k in self.gfx_ih_clients}, **{k: sdma_srcs for k in self.sdma_ih_clients}}

  def init_hw(self):
    if self.adev.ip_ver[am.NBIO_HWIP] in {(7,9,0), (7,9,1)}:
      self.adev.regXCC_DOORBELL_FENCE.write(0x0)
      for aid in range(1, self.adev.gmc.vmhubs):
        self.adev.indirect_wreg_pcie(self.adev.regXCC_DOORBELL_FENCE.addr[0], self.adev.regXCC_DOORBELL_FENCE.encode(shub_slv_mode=1), aid=aid)
      self.adev.regBIFC_GFX_INT_MONITOR_MASK.write(0x7ff)
      self.adev.regBIFC_DOORBELL_ACCESS_EN_PF.write(0xfffff)
    # nbio 2.3 has no such register and nbio_v2_3.c never writes one: this is an errata write
    # that arrives with nbio 4.3 (nbio_v4_3.c:337) and nbif 6.3 (nbif_v6_3_1.c:295). MI300's
    # nbio 7.9 takes the branch above.
    elif self.adev.ip_ver[am.NBIO_HWIP] >= (4,0,0): self.adev.regRCC_DEV0_EPF2_STRAP2.update(strap_no_soft_reset_dev0_f2=0x0)
    self.adev.regRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN.write(0x1)
  def set_clockgating_state(self):
    if self.adev.ip_ver[am.HDP_HWIP] >= (5,2,1): self.adev.regHDP_MEM_POWER_CTRL.update(atomic_mem_power_ctrl_en=1, atomic_mem_power_ds_en=1)

  def doorbell_enable(self, port, awid=0, awaddr_31_28_value=0, offset=0, size=0, aid=0):
    # The S2A doorbell router arrives with nbio 4.3. nbio 2.3 has no router and no port to
    # address -- it ranges doorbells per client instead, which is doorbell_range() below. The
    # two are complementary: each generation gets exactly one of them, and each no-ops on the
    # other's hardware rather than pretending to be portable.
    if self.adev.ip_ver[am.NBIO_HWIP] < (4,0,0): return
    reg = self.adev.reg(f"{'regGDC_S2A0_S2A' if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0) else 'regS2A'}_DOORBELL_ENTRY_{port}_CTRL")
    val = reg.encode(**{f"s2a_doorbell_port{port}_enable":1, f"s2a_doorbell_port{port}_awid":awid,  f"s2a_doorbell_port{port}_range_size":size,
      f"s2a_doorbell_port{port}_awaddr_31_28_value":awaddr_31_28_value, f"s2a_doorbell_port{port}_range_offset":offset})

    if self.adev.ip_ver[am.NBIO_HWIP] in {(7,9,0), (7,9,1)}: self.adev.indirect_wreg_pcie(reg.addr[0], val, aid=aid)
    else: reg.write(val)

  def doorbell_range(self, client:str, offset:int, size:int):
    """Give one client its window in the doorbell aperture, on nbio that ranges per client.

    nbio_v2_3.c:109 programs BIF_<client>_DOORBELL_RANGE with the ring's doorbell index and the
    window size. A no-op where the S2A router already did this by port. IH needs no entry here:
    AM disables the IH doorbell outright (regIH_DOORBELL_RPTR.enable=0).
    """
    if self.adev.ip_ver[am.NBIO_HWIP] < (4,0,0):
      self.adev.reg(f"regBIF_{client}_DOORBELL_RANGE").update(offset=offset, size=size)

class AM_GMC(AM_IP):
  def init_sw(self):
    self.vmhubs = len(self.adev.regs_offset[am.MMHUB_HWIP])

    # XGMI (for supported systems)
    self.xgmi_phys_id = self.adev.regMMMC_VM_XGMI_LFB_CNTL.read_bitfields()['pf_lfb_region'] if hasattr(self.adev, 'regMMMC_VM_XGMI_LFB_CNTL') else 0
    self.xgmi_seg_sz = self.adev.regMMMC_VM_XGMI_LFB_SIZE.read_bitfields()['pf_lfb_size']<<24 if hasattr(self.adev, 'regMMMC_VM_XGMI_LFB_SIZE') else 0

    self.paddr_base = self.xgmi_phys_id * self.xgmi_seg_sz

    self.fb_base = (self.adev.regMMMC_VM_FB_LOCATION_BASE.read() & 0xFFFFFF) << 24
    self.fb_end = (self.adev.regMMMC_VM_FB_LOCATION_TOP.read() & 0xFFFFFF) << 24

    # Memory controller aperture
    self.mc_base = self.fb_base + self.paddr_base

    # VM aperture
    self.vm_base = self.adev.mm.va_base
    self.vm_end = min(self.vm_base + (1 << self.adev.mm.va_bits) - 1, 0x7fffffffffff)

    self.trans_futher = self.adev.ip_ver[am.GC_HWIP] < (10, 0, 0)

    # mi3xx has 48-bit, others have 44-bit address space
    self.address_space_mask = (1 << (48 if self.adev.ip_ver[am.GC_HWIP][:2] in {(9,4), (9,5)} else 44)) - 1

    self.memscratch_xgmi_paddr = self.adev.paddr2xgmi(self.adev.mm.palloc(0x1000, zero=False, boot=True))
    self.dummy_page_xgmi_paddr = self.adev.paddr2xgmi(self.adev.mm.palloc(0x1000, zero=False, boot=True))

    # MM hub is inited before any tlb flushes and is still valid during partial_boot, so set it to true
    self.hub_initted = {"MM": True, "GC": False}

    self.pf_status_reg = lambda ip: f"reg{ip}VM_L2_PROTECTION_FAULT_STATUS{'_LO32' if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0) else ''}"

  def init_hw(self): self.init_hub("MM", inst_cnt=self.vmhubs)

  def flush_hdp(self):
    # Only bits 2..18 of this register are the remapped flush address (the autogen table gives the
    # field as 'address': (2, 18)); the rest is not part of it. Taking the whole dword and dividing
    # by four happens to be right when the upper bits read back zero, and on Navi 23 they do not --
    # the index then lands outside the mapped MMIO aperture, AMDev.rreg falls through to the
    # indirect RSMU window, and nbio 2.3 has no regBIF_BX_PF0_RSMU_INDEX, so this raises KeyError.
    # That is what made a hung kernel unrecoverable here: flush_hdp is on the recover() path.
    self.adev.wreg(self.adev.reg("regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL").read_bitfields()["address"], 0x0)
  def flush_tlb(self, ip:Literal["MM", "GC"], vmid, flush_type=0):
    self.flush_hdp()

    # Can't issue TLB invalidation if the hub isn't initialized.
    if not self.hub_initted[ip]: return

    for inst in range(self.adev.gmc.vmhubs if ip == "MM" else self.adev.gfx.xccs):
      if ip == "MM": wait_cond(lambda: self.adev.regMMVM_INVALIDATE_ENG17_SEM.read(inst=inst) & 0x1, value=1, msg="mm flush_tlb timeout")

      self.adev.reg(f"reg{ip}VM_INVALIDATE_ENG17_REQ").write(flush_type=flush_type, per_vmid_invalidate_req=(1 << vmid), invalidate_l2_ptes=1,
        invalidate_l2_pde0=1, invalidate_l2_pde1=1, invalidate_l2_pde2=1, invalidate_l1_ptes=1, clear_protection_fault_status_addr=0, inst=inst)

      wait_cond(lambda: self.adev.reg(f"reg{ip}VM_INVALIDATE_ENG17_ACK").read(inst=inst) & (1 << vmid), value=(1 << vmid), msg="flush_tlb timeout")

      if ip == "MM": self.adev.regMMVM_INVALIDATE_ENG17_SEM.write(0x0, inst=inst)
      if self.adev.ip_ver[am.GC_HWIP] >= (11,0,0) and ip == "MM":
        self.adev.regMMVM_L2_BANK_SELECT_RESERVED_CID2.update(reserved_cache_private_invalidation=1, inst=inst)

        # Read back the register to ensure the invalidation is complete
        self.adev.regMMVM_L2_BANK_SELECT_RESERVED_CID2.read(inst=inst)

  def enable_vm_addressing(self, page_table, ip:Literal["MM", "GC"], vmid, inst):
    self.adev.wreg_pair(f"reg{ip}VM_CONTEXT{vmid}_PAGE_TABLE_START_ADDR", "_LO32", "_HI32", self.vm_base >> 12, inst=inst)
    self.adev.wreg_pair(f"reg{ip}VM_CONTEXT{vmid}_PAGE_TABLE_END_ADDR", "_LO32", "_HI32", self.vm_end >> 12, inst=inst)
    self.adev.wreg_pair(f"reg{ip}VM_CONTEXT{vmid}_PAGE_TABLE_BASE_ADDR", "_LO32", "_HI32", self.adev.paddr2xgmi(page_table.paddr) | 1, inst=inst)

    fault_flags = {f'{x}_protection_fault_enable_interrupt':1 for x in ['pde0', 'dummy_page', 'range', 'valid', 'read', 'write', 'execute']}
    en_def_flags = {f'{x}_protection_fault_enable_default':1 for x in ['pde0', 'dummy_page', 'range', 'valid', 'read', 'write', 'execute']}
    self.adev.reg(f"reg{ip}VM_CONTEXT{vmid}_CNTL").write(0x1800000, **fault_flags, **en_def_flags, enable_context=1,
      page_table_depth=((2 if self.trans_futher else 3) - page_table.lv), page_table_block_size=9 if self.trans_futher else 0, inst=inst)

  def init_hub(self, ip:Literal["MM", "GC"], inst_cnt:int):
    # Init system apertures
    for inst in range(inst_cnt):
      self.adev.reg(f"reg{ip}MC_VM_AGP_BASE").write(0, inst=inst)
      self.adev.reg(f"reg{ip}MC_VM_AGP_BOT").write(0xffffffffffff >> 24, inst=inst) # disable AGP
      self.adev.reg(f"reg{ip}MC_VM_AGP_TOP").write(0, inst=inst)

      self.adev.reg(f"reg{ip}MC_VM_SYSTEM_APERTURE_LOW_ADDR").write(self.fb_base >> 18, inst=inst)
      self.adev.reg(f"reg{ip}MC_VM_SYSTEM_APERTURE_HIGH_ADDR").write(self.fb_end >> 18, inst=inst)
      self.adev.wreg_pair(f"reg{ip}MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR", "_LSB", "_MSB", self.memscratch_xgmi_paddr >> 12, inst=inst)
      self.adev.wreg_pair(f"reg{ip}VM_L2_PROTECTION_FAULT_DEFAULT_ADDR", "_LO32", "_HI32", self.dummy_page_xgmi_paddr >> 12, inst=inst)

      self.adev.reg(f"reg{ip}VM_L2_PROTECTION_FAULT_CNTL2").update(active_page_migration_pte_read_retry=1, inst=inst)

      # Init TLB and cache
      self.adev.reg(f"reg{ip}MC_VM_MX_L1_TLB_CNTL").update(enable_l1_tlb=1, system_access_mode=3, enable_advanced_driver_model=1,
        system_aperture_unmapped_access=0, mtype=self.adev.soc.module.MTYPE_UC, inst=inst)

      self.adev.reg(f"reg{ip}VM_L2_CNTL").update(enable_l2_cache=1, enable_default_page_out_to_system_memory=1,
        l2_pde0_cache_tag_generation_mode=0, pde_fault_classification=0, context1_identity_access_mode=1, identity_mode_fragment_size=0,
        enable_l2_fragment_processing=int(self.adev.ip_ver[am.GC_HWIP] < (10,0,0)), inst=inst)
      self.adev.reg(f"reg{ip}VM_L2_CNTL2").update(invalidate_all_l1_tlbs=1, invalidate_l2_cache=1, inst=inst)
      self.adev.reg(f"reg{ip}VM_L2_CNTL3").write(l2_cache_4k_associativity=1, l2_cache_bigk_associativity=1,
        bank_select=12 if self.trans_futher else 9, l2_cache_bigk_fragment_size=9 if self.trans_futher else 6, inst=inst)
      self.adev.reg(f"reg{ip}VM_L2_CNTL4").write(l2_cache_4k_partition_count=1, inst=inst)
      if self.adev.ip_ver[am.GC_HWIP] >= (10,0,0): self.adev.reg(f"reg{ip}VM_L2_CNTL5").write(walker_priority_client_id=0x1ff, inst=inst)

      self.enable_vm_addressing(self.adev.mm.root_page_table, ip, vmid=0, inst=inst)

      # Disable identity aperture
      self.adev.wreg_pair(f"reg{ip}VM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR", "_LO32", "_HI32", 0xfffffffff, inst=inst)
      self.adev.wreg_pair(f"reg{ip}VM_L2_CONTEXT1_IDENTITY_APERTURE_HIGH_ADDR", "_LO32", "_HI32", 0x0, inst=inst)
      self.adev.wreg_pair(f"reg{ip}VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET", "_LO32", "_HI32", 0x0, inst=inst)

      for eng_i in range(18): self.adev.wreg_pair(f"reg{ip}VM_INVALIDATE_ENG{eng_i}_ADDR_RANGE", "_LO32", "_HI32", 0x1fffffffff, inst=inst)
    self.hub_initted[ip] = True

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def get_pte_flags(self, pte_lv, is_table, frag, uncached, system, snooped, valid, extra=0):
    extra |= (am.AMDGPU_PTE_SYSTEM * system) | (am.AMDGPU_PTE_SNOOPED * snooped) | (am.AMDGPU_PTE_VALID * valid) | am.AMDGPU_PTE_FRAG(frag)
    if not is_table: extra |= (am.AMDGPU_PTE_WRITEABLE | am.AMDGPU_PTE_READABLE | am.AMDGPU_PTE_EXECUTABLE)
    if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0):
      extra |= am.AMDGPU_PTE_MTYPE_GFX12(0, self.adev.soc.module.MTYPE_UC if uncached else 0)
      extra |= (am.AMDGPU_PDE_PTE_GFX12 if not is_table and pte_lv != am.AMDGPU_VM_PTB else (am.AMDGPU_PTE_IS_PTE if not is_table else 0))
    elif self.adev.ip_ver[am.GC_HWIP] >= (10,0,0):
      extra |= am.AMDGPU_PTE_MTYPE_NV10(0, self.adev.soc.module.MTYPE_UC if uncached else 0)
      extra |= (am.AMDGPU_PDE_PTE if not is_table and pte_lv != am.AMDGPU_VM_PTB else 0)
    else:
      extra |= am.AMDGPU_PTE_MTYPE_VG10(0, self.adev.soc.module.MTYPE_UC if uncached else 0)
      if is_table and pte_lv == am.AMDGPU_VM_PDB1: extra |= am.AMDGPU_PDE_BFS(0x9)
      if is_table and pte_lv == am.AMDGPU_VM_PDB0: extra |= am.AMDGPU_PTE_TF
      if not is_table and pte_lv not in {am.AMDGPU_VM_PTB, am.AMDGPU_VM_PDB0}: extra |= am.AMDGPU_PDE_PTE
    return extra
  def is_pte_huge_page(self, pte_lv, pte):
    if self.adev.ip_ver[am.GC_HWIP] < (10,0,0): return (pte & am.AMDGPU_PDE_PTE) if pte_lv != am.AMDGPU_VM_PDB0 else not (pte & am.AMDGPU_PTE_TF)
    return pte & (am.AMDGPU_PDE_PTE_GFX12 if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0) else am.AMDGPU_PDE_PTE)

class SMUError(RuntimeError):
  """The SMU answered, and said no. Distinct from a timeout, where it did not answer at all."""

class AM_SMU(AM_IP):
  def init_sw(self):
    self.smu_mod = self.adev._ip_module("smu", am.MP1_HWIP)
    self.driver_table_paddr = self.adev.mm.palloc(0x4000, zero=False, boot=True)

  # smu11_driver_if_sienna_cichlid.h bits that power-gate or deep-sleep a block AM drives.
  # amdgpu enables these because it implements the handshakes that bring the block back
  # (smu_v11_0_gfx_off_control and friends). AM has none, so an engine that powers itself down
  # between submissions never comes back and the next one hangs -- observed on a Navi 23, where
  # enabling the pptable's own FeaturesToRun verbatim wedged the GFX ring on the first kernel
  # after boot, and clearing these ran it.
  SMU11_UNSERVICEABLE_FEATURES = {12: "DS_GFXCLK", 18: "GFX_ULV", 20: "GFXOFF", 22: "MM_DPM_PG",
                                  34: "GFX_DCS", 40: "MMHUB_PG", 41: "ATHUB_PG"}

  def _setup_pptable(self):
    """Hand SMU 11 its pptable. Without it there are no DPM tables and the card stays at boot clocks.

    SMU 13 and 14 come up with a usable soft pptable already loaded, which is why AM never needed
    this. SMU 11 does not: every GetDpmFreqByIndex and every SetSoftMaxByFreq answers CMD_FAIL,
    set_clocks pins nothing, and a Navi 23 sits at 500 MHz against a 2350 MHz top DPM entry.

    amdgpu's order, from smu_smc_hw_setup: upload the table, run BTC, set the allowed feature
    mask, then enable features. BTC is the AVFS voltage calibration -- boosting without it is
    how you get a card that runs for one kernel.
    """
    if (ppt:=self.adev.fw.smu_pptable) is None: return
    try: self._upload_pptable(ppt)
    except SMUError as e:
      # Same call the clocks make: this is a performance step, not a correctness one. A card
      # whose SMU declines the table still executes kernels, it just will not leave boot clocks,
      # and refusing to build the device over that is worse than running slow. A TimeoutError
      # still propagates -- that is the SMU not answering at all, which is not about the table.
      print(f"am {self.adev.devfmt}: the SMU refused its pptable, so there will be no DPM: {e}")

  def _patch_board_data(self, ppt:bytes) -> bytes:
    """Fill PPTable_t's board section from the card's own VBIOS, as amdgpu does before upload.

    AMD ships I2cControllers..BoardReserved zeroed in the SMU firmware and expects the driver to
    supply it (sienna_cichlid_append_powerplay_table). It carries the voltage-regulator mapping
    and the current-telemetry calibration, so without it the SMU cannot command a rail: on a part
    whose GFXCLK is a DFLL the clock follows the voltage the VR supplies, and the SMU ends up
    accepting every SetSoftMinByFreq while sitting at GfxclkFidle.

    A failure here is reported and survived, not raised. Uploading the table with its board
    section still zeroed is exactly today's behaviour -- DPM tables exist, clocks do not rise --
    and that is strictly better than no table at all.
    """
    from tinygrad.runtime.support.am.amdev import PPTABLE_BOARD_LEN, PPTABLE_BOARD_OFF, atom_board_data, vbios_reader
    try: board = atom_board_data(vbios_reader(self.adev))
    except (ValueError, RuntimeError) as e:
      print(f"am {self.adev.devfmt}: no board data from the VBIOS, so the SMU will have no voltage-regulator "
            + f"mapping and the clocks will stay at boot: {e}")
      return ppt
    if DEBUG >= 2: print(f"am {self.adev.devfmt}: patched {len(board)} bytes of VBIOS board data into the pptable")
    return ppt[:PPTABLE_BOARD_OFF] + board + ppt[PPTABLE_BOARD_OFF + PPTABLE_BOARD_LEN:]

  def _upload_pptable(self, ppt:bytes):
    ppt = self._patch_board_data(ppt)
    # The USB bridge issues PCIe memory writes as whole dwords, so the payload has to be dword
    # sized. sizeof(PPTable_t) already is; padding costs nothing and does not assume that.
    padded = pad_bytes(ppt, 4)
    self.adev.vram.view(self.driver_table_paddr, len(padded))[:] = memoryview(padded)
    self._send_msg(self.smu_mod.PPSMC_MSG_TransferTableDram2Smu, self.smu_mod.TABLE_PPTABLE)
    self._send_msg(self.smu_mod.PPSMC_MSG_RunDcBtc, 0, timeout=30000)

    # PPTable_t is {uint32 Version; uint32 FeaturesToRun[2]; ...} -- the firmware's own answer for
    # which features this part should run. Start there rather than from all-ones, then drop what
    # this driver cannot service.
    feat = int.from_bytes(ppt[4:12], 'little')
    unserviceable = sum(1 << b for b in self.SMU11_UNSERVICEABLE_FEATURES)
    if DEBUG >= 2 and (dropped:=feat & unserviceable):
      names = ', '.join(n for b, n in self.SMU11_UNSERVICEABLE_FEATURES.items() if dropped >> b & 1)
      print(f"am {self.adev.devfmt}: not enabling {names}: no handshake to wake a gated block")
    feat &= ~unserviceable
    # High before Low, which is smu_v11_0_set_allowed_mask's order across every SMU generation.
    self._send_msg(self.smu_mod.PPSMC_MSG_SetAllowedFeaturesMaskHigh, (feat >> 32) & 0xffffffff)
    self._send_msg(self.smu_mod.PPSMC_MSG_SetAllowedFeaturesMaskLow, feat & 0xffffffff)
    self.requested_features = feat

  def init_hw(self):
    self._send_msg(self.smu_mod.PPSMC_MSG_SetDriverDramAddrHigh, hi32(self.adev.paddr2mc(self.driver_table_paddr)))
    self._send_msg(self.smu_mod.PPSMC_MSG_SetDriverDramAddrLow, lo32(self.adev.paddr2mc(self.driver_table_paddr)))
    self.requested_features = 0
    self._setup_pptable()
    self._send_msg(self.smu_mod.PPSMC_MSG_EnableAllSmuFeatures, 0, timeout=30000)
    # "Explicitly notify PMFW the power mode the system in. Since the PMFW may boot the ASIC with
    # a different mode" -- smu_late_init. amdgpu sends this whenever the ACDC feature is not
    # GPIO-controlled, which is every plain dGPU, and a card that booted believing DC applies a
    # different set of limits. Suppressed rather than raised: it is a hint, not a dependency.
    # Only on the pptable path. amdgpu sends this on every ASIC, but SMU 13/14 work today and are
    # what comma ships, so they keep their existing message sequence byte for byte.
    if self.requested_features and hasattr(self.smu_mod, 'PPSMC_MSG_NotifyPowerSource'):
      with contextlib.suppress(TimeoutError, SMUError):
        self._send_msg(self.smu_mod.PPSMC_MSG_NotifyPowerSource, self.smu_mod.SMU_POWER_SOURCE_AC)
    self._check_running_features()

  # Features whose absence means a clock request will be silently ignored. smu_cmn_clk_dpm_is_enabled
  # maps each clock domain to one of these, and smu_v11_0_set_soft_freq_limited_range returns 0
  # without sending anything when its bit is not running -- because the SMU ACKs the message and
  # does nothing. If one of these is requested and not running, say so by name.
  DPM_CLOCK_FEATURES = {1: "DPM_GFXCLK", 3: "DPM_UCLK", 4: "DPM_FCLK", 5: "DPM_SOCCLK"}

  def _check_running_features(self):
    """Close the loop: ask which features are actually running, not which we asked for.

    Every smu_cmn_feature_is_enabled() in amdgpu reads this read-back list rather than the
    requested mask, and smu_smc_hw_setup calls it immediately after enabling. Without it a card
    that accepted the mask and started nothing looks identical to one that worked.
    """
    if not self.requested_features or not hasattr(self.smu_mod, 'PPSMC_MSG_GetRunningSmuFeaturesLow'): return
    try:
      lo = self._send_msg(self.smu_mod.PPSMC_MSG_GetRunningSmuFeaturesLow, 0, read_back_arg=True, timeout=5000)
      hi = self._send_msg(self.smu_mod.PPSMC_MSG_GetRunningSmuFeaturesHigh, 0, read_back_arg=True, timeout=5000)
    except (SMUError, TimeoutError) as e:
      print(f"am {self.adev.devfmt}: could not read back the running feature mask: {e}")
      return
    self.running_features = running = ((hi & 0xffffffff) << 32) | (lo & 0xffffffff)
    if (missing:=[n for b, n in self.DPM_CLOCK_FEATURES.items() if self.requested_features >> b & 1 and not running >> b & 1]):
      print(f"am {self.adev.devfmt}: the SMU did not start {', '.join(missing)}; clock requests for those "
            + "domains will be accepted and ignored")
    elif DEBUG >= 2: print(f"am {self.adev.devfmt}: running features {running:#018x}")

  def is_smu_alive(self):
    with contextlib.suppress(TimeoutError, SMUError): self._send_msg(self.smu_mod.PPSMC_MSG_GetSmuVersion, 0, timeout=100)
    return self.adev.mmMP1_SMN_C2PMSG_90.read() != 0

  def mode1_reset(self):
    if DEBUG >= 2: print(f"am {self.adev.devfmt}: mode1 reset")
    if self.adev.ip_ver[am.MP0_HWIP] >= (14,0,0) or self.adev.ip_ver[am.MP0_HWIP] in {(13,0,0), (13,0,7), (13,0,10)}:
      self._send_msg(__DEBUGSMC_MSG_Mode1Reset:=2, 0, debug=True)
    elif self.adev.ip_ver[am.MP0_HWIP] in {(13,0,6), (13,0,12)}: self._send_msg(self.smu_mod.PPSMC_MSG_GfxDriverReset, 1)
    else: self._send_msg(self.smu_mod.PPSMC_MSG_Mode1Reset, 0)

    if not self.adev.is_hive(): time.sleep(0.5) # 500ms

  def read_table(self, table_t, arg):
    if self.adev.ip_ver[am.MP0_HWIP] in {(13,0,6),(13,0,12)}: self._send_msg(self.smu_mod.PPSMC_MSG_GetMetricsTable, arg)
    else: self._send_msg(self.smu_mod.PPSMC_MSG_TransferTableSmu2Dram, arg)
    return table_t.from_buffer(bytearray(self.adev.vram.view(self.driver_table_paddr, ctypes.sizeof(table_t))[:]))

  # SmuMetrics is versioned, and the versions agree only up to offset 96: V1 has ThrottlerStatus
  # there, V2 has AccCnt followed by a 20-byte ThrottlingPercentage, and every field after it
  # shifts. amdgpu chooses by (MP1 IP version, smc_fw_version) in sienna_cichlid_get_smu_metrics_data
  # and these are its thresholds verbatim. Choosing wrong does not raise -- it reads the fan speed
  # out of a padding field -- so the version is looked up rather than assumed.
  SMU11_METRICS_V2_MIN_FW = {(11,0,7): 0x3A4300, (11,0,11): 0x412D00, (11,0,12): 0x3B2300, (11,0,13): 0x491100}
  SMU11_METRICS_V3_MIN_FW = {(11,0,7): 0x3A4900}

  @property
  def smc_fw_version(self) -> int:
    """The SMU firmware version, asked once. Only the SMU 11 metrics layout depends on it."""
    if getattr(self, '_smc_fw_version', None) is None:
      self._smc_fw_version = self._send_msg(self.smu_mod.PPSMC_MSG_GetSmuVersion, 0, read_back_arg=True, timeout=5000)
    return self._smc_fw_version

  def metrics(self) -> dict[str, int]:
    """The card's live clocks, activity, power and temperatures, by whatever this SMU calls them.

    SMU 13 keeps temperatures in an AvgTemperature[] indexed by TEMP_*, and the fan in AvgFanRpm.
    SMU 11 has neither name: they are TemperatureHotspot, TemperatureMem and CurrFanSpeed. Reading
    an SMU 11 card with SMU 13's names raises AttributeError, and a caller that wraps this in a
    broad except -- as modeld's ChestnutState did -- then publishes nothing at all and never says
    why. That is how every clock number on the 6600 XT came to be measured blind.

    CurrClock is the instantaneous per-domain clock indexed by PPCLK_e, which is what tells you
    whether a SetSoftMin/MaxByFreq the SMU accepted was actually applied. It is the only field
    here that answers that, so it is reported for every domain, memory included.
    """
    ext = self.read_table(self.smu_mod.SmuMetricsExternal_t, self.smu_mod.TABLE_SMU_METRICS)
    if (ver:=tuple(self.adev.ip_ver[am.MP1_HWIP]))[0] != 11:
      # SMU 13/14 work today and are what comma ships, so their read keeps its existing shape and
      # costs no extra round trip. They have no per-domain CurrClock enum in common with SMU 11.
      m = ext.SmuMetrics
      return {'gfxclk': m.AverageGfxclkFrequencyPostDs, 'gfx_activity': m.AverageGfxActivity,
              'socket_power': m.AverageSocketPower, 'temp_hotspot': m.AvgTemperature[self.smu_mod.TEMP_HOTSPOT],
              'temp_mem': m.AvgTemperature[self.smu_mod.TEMP_MEM], 'fan_rpm': m.AvgFanRpm}

    never = 1 << 62
    if self.smc_fw_version >= self.SMU11_METRICS_V3_MIN_FW.get(ver, never): m = ext.SmuMetrics_V3
    elif self.smc_fw_version >= self.SMU11_METRICS_V2_MIN_FW.get(ver, never): m = ext.SmuMetrics_V2
    else: m = ext.SmuMetrics
    return {'gfxclk': m.CurrClock[self.smu_mod.PPCLK_GFXCLK], 'socclk': m.CurrClock[self.smu_mod.PPCLK_SOCCLK],
            'uclk': m.CurrClock[self.smu_mod.PPCLK_UCLK], 'fclk': m.CurrClock[self.smu_mod.PPCLK_FCLK],
            'gfx_activity': m.AverageGfxActivity, 'uclk_activity': m.AverageUclkActivity,
            'socket_power': m.AverageSocketPower, 'temp_hotspot': m.TemperatureHotspot,
            'temp_mem': m.TemperatureMem, 'fan_rpm': m.CurrFanSpeed}

  @functools.cache  # pylint: disable=method-cache-max-size-none
  def read_clocks(self, clk_list:tuple[int]) -> dict[int, list[int]]:
    return {clck: [self._send_msg(self.smu_mod.PPSMC_MSG_GetDpmFreqByIndex, (clck<<16)|i, read_back_arg=True)&0x7fffffff for i in range(cnt)]
      for clck in clk_list if (cnt:=self._send_msg(self.smu_mod.PPSMC_MSG_GetDpmFreqByIndex, (clck<<16)|0xff, read_back_arg=True)&0x7fffffff)}

  # amdgpu's UMD "profiling" pstate per Navi 2x ASIC, from sienna_cichlid_ppt.h, keyed by MP1 IP
  # version: (GFXCLK, SOCCLK, MEMCLK) in MHz. These are the clocks AMD themselves validate a part
  # at. Navy Flounder (11,0,11) is deliberately absent -- the header has no constants for it, and
  # a guessed memory level is not a slow card, it is a dead one.
  SMU11_PROFILING_PSTATE = {(11,0,7): (1825, 960, 1000), (11,0,12): (1950, 960, 676), (11,0,13): (2200, 960, 1000)}

  def _set_clocks_smu11(self, level:int|None) -> dict[str, bool]:
    """SMU 11's clock request, shaped like smu_v11_0_set_performance_level rather than like a
    sweep over every domain the header defines.

    Three differences from the generic path, each measured on an RX 6600 XT:

    FCLK is never asked. smu_v11_0_set_performance_level sets soft limits on GFXCLK, MCLK and
    SOCCLK and leaves the Data Fabric clock to PMFW, and this driver asking for it is not a
    harmless extra.

    Memory is pinned to the ASIC's profiling level, not to the top of its DPM table. On this part
    the table is [96, 456, 675, 1000] and only 675 can be entered: 456 and 1000 are both accepted
    in about 1.5 ms and then the SMU never answers another message, under soft-min, hard-min and
    ceiling-then-floor, with GFXCLK and SOCCLK raised first or not, and with DS_UCLK, DS_FCLK,
    DF_CSTATE and both memory voltage-scaling features masked off. 675 is what AMD's own
    DIMGREY_CAVEFISH_UMD_PSTATE_PROFILING_MEMCLK of 676 snaps to. Since AM_POWER_LIMIT is unset in
    every path except the bench harness, `level=-1` -- the top entry -- is what a normal boot asked
    for, so a normal boot wedged the SMU.

    GFXCLK gets a ceiling and no floor. Its governor reaches 2340 MHz on its own under load;
    pinning it to the profiling 1950 measured slower on the same card in the same session.

    The ceiling goes before the floor, which is the order smu_v11_0_set_soft_freq_limited_range
    uses on every SMU generation.
    """
    gfx, soc, uclk = self.smu_mod.PPCLK_GFXCLK, self.smu_mod.PPCLK_SOCCLK, self.smu_mod.PPCLK_UCLK
    pstate = self.SMU11_PROFILING_PSTATE.get(tuple(self.adev.ip_ver[am.MP1_HWIP]))

    targets: dict[int, tuple[int, int]] = {}
    if level == 0:
      # Teardown. (0, 0) is the firmware minimum in the same encoding AUTO uses for the maximum,
      # so the lowest state is expressed without asking the SMU anything. That matters: fini runs
      # after a hang as often as after a clean run, read_clocks is cached per clk_list tuple so a
      # teardown-shaped key is a cache miss, and a miss here puts a GetDpmFreqByIndex round trip on
      # a possibly-wedged SMU. fini suppresses SMUError but not TimeoutError, so that lookup turned
      # every post-hang teardown into a 10 s timeout that escaped and buried the real failure.
      #
      # Memory is left where it is on purpose: dropping UCLK back to its boot level is the same
      # transition that wedges it on the way up, and there is nothing to reclaim at teardown.
      targets[gfx] = targets[soc] = (0, 0)
    else:
      # 0xffff is "the firmware maximum" and 0 is "the firmware minimum" -- the encoding
      # smu_v11_0_set_soft_freq_limited_range uses for AMD_DPM_FORCED_LEVEL_AUTO. Asking that way
      # costs no DPM-table round trips and leaves both governors free to do their job.
      targets[gfx] = targets[soc] = (0, 0xffff)
      # Memory is the exception: it has to land on a specific level, so its table is read. Snap
      # down, never up -- the level above the validated one is exactly the one that does not work.
      if pstate and (have:=self.read_clocks((uclk,))).get(uclk) and (fits:=[f for f in have[uclk] if f <= pstate[2]]):
        targets[uclk] = (max(fits), max(fits))

    took: dict[str, bool] = {}
    for clck, (fmin, fmax) in targets.items():
      try:
        self._send_msg(self.smu_mod.PPSMC_MSG_SetSoftMaxByFreq, clck << 16 | fmax)
        self._send_msg(self.smu_mod.PPSMC_MSG_SetSoftMinByFreq, clck << 16 | fmin)
        took[self.smu_mod.PPCLK_e[clck]] = True
      except SMUError: took[self.smu_mod.PPCLK_e[clck]] = False
    return took

  def set_clocks(self, level:int|None) -> dict[str, bool]:
    """Pin every clock domain -- to `level` in the card's own DPM table, or to max when None.

    Returns {domain name: was the ceiling accepted}, for the domains a ceiling was sent for.
    Accepted is not the same as applied: a Sienna Cichlid whose pptable still carries a zeroed
    board section takes every request and stays at its boot clock, because without the VR
    mapping it has no way to raise a voltage. Only SmuMetrics can tell you the clock moved.

    One domain refusing must not abandon the others. Sienna Cichlid's SMU answers CMD_FAIL for
    UCLK unless a PPTable has been uploaded, which AM does not do -- and UCLK is first in the
    list, so a single unguarded raise here left GFXCLK, the domain that decides whether the card
    runs at boot clocks or boost, never asked at all. On a 6600 XT that was the difference
    between 262 GFLOPS and the card's actual peak.

    SMUError is the SMU answering "no" about one domain, and is recorded rather than raised.
    TimeoutError is the SMU not answering -- a fact about the device, not one clock -- and still
    propagates from the ceiling. The floor keeps suppressing both, as it always has: it is a
    20 ms best-effort, and the ceiling is what actually pins the clock up.
    """
    # SMU 11 has its own shape; see _set_clocks_smu11. SMU 13/14 work today and are what comma
    # ships, so their message sequence is left exactly as it was.
    if self.adev.ip_ver[am.MP1_HWIP][0] == 11: return self._set_clocks_smu11(level)

    clks = tuple([self.smu_mod.PPCLK_UCLK, self.smu_mod.PPCLK_FCLK, self.smu_mod.PPCLK_SOCCLK])
    if self.adev.ip_ver[am.MP0_HWIP] not in {(13,0,6), (13,0,12)}: clks += (self.smu_mod.PPCLK_GFXCLK,)

    # None is "as fast as it will go": floor 0, ceiling 0xffff, which the SMU clamps to the top
    # DPM state. A level pins floor and ceiling together to one entry of the card's own table.
    if level is None: targets = {clck: (0, 0xffff) for clck in clks}
    else: targets = {clck: (vals[level], vals[level]) for clck, vals in self.read_clocks(clks).items()}

    took: dict[str, bool] = {}
    for clck, (fmin, fmax) in targets.items():
      with contextlib.suppress(TimeoutError, SMUError):
        self._send_msg(self.smu_mod.PPSMC_MSG_SetSoftMinByFreq, clck << 16 | fmin, timeout=20)
      # Pre-gfx10 parts take no ceiling, so there is nothing to report for them and took stays
      # empty -- distinct from a card that was asked and refused.
      if self.adev.ip_ver[am.GC_HWIP] < (10,0,0): continue
      try:
        self._send_msg(self.smu_mod.PPSMC_MSG_SetSoftMaxByFreq, clck << 16 | fmax)
        took[self.smu_mod.PPCLK_e[clck]] = True
      except SMUError: took[self.smu_mod.PPCLK_e[clck]] = False
    return took

  def set_power_limit(self, watts:float):
    ppt_limit = max(int(round(watts)), 1)
    self._send_msg(self.smu_mod.PPSMC_MSG_SetPptLimit, ppt_limit)
    if DEBUG >= 2: print(f"am {self.adev.devfmt}: GPU power limit set to {ppt_limit}W")

  def _aca_read_reg(self, bank_idx:int, reg_idx:int, ue=True) -> int:
    msg = self.smu_mod.PPSMC_MSG_McaBankDumpDW if ue else self.smu_mod.PPSMC_MSG_McaBankCeDumpDW
    return (self._send_msg(msg, (bank_idx << 16) | (reg_idx * 8 + 4), read_back_arg=True) << 32) | \
            self._send_msg(msg, (bank_idx << 16) | (reg_idx * 8), read_back_arg=True)

  def _aca_read_banks(self, ue=True) -> list[list[int]]:
    if not hasattr(self.smu_mod, 'PPSMC_MSG_QueryValidMcaCount'): return []
    count_msg = self.smu_mod.PPSMC_MSG_QueryValidMcaCount if ue else self.smu_mod.PPSMC_MSG_QueryValidMcaCeCount
    return [[self._aca_read_reg(idx, reg_idx, ue=ue) for reg_idx in range(16)] for idx in range(self._send_msg(count_msg, 0, read_back_arg=True))]

  def _smu_cmn_send_msg(self, msg:int, param=0, debug=False):
    (self.adev.mmMP1_SMN_C2PMSG_90 if not debug else self.adev.mmMP1_SMN_C2PMSG_54).write(0) # resp reg
    (self.adev.mmMP1_SMN_C2PMSG_82 if not debug else self.adev.mmMP1_SMN_C2PMSG_53).write(param)
    (self.adev.mmMP1_SMN_C2PMSG_66 if not debug else self.adev.mmMP1_SMN_C2PMSG_75).write(msg)

  # smu_cmn.c's response codes. The SMU sets one of these promptly, so treating anything that is
  # not SMU_RESP_OK as "keep waiting" burns the whole timeout and then blames the wrong thing:
  # a message the SMU refused in microseconds is reported as a ten-second hang.
  smu_resp = {0xFF: "CMD_FAIL", 0xFE: "CMD_UNKNOWN", 0xFD: "CMD_BAD_PREREQ", 0xFC: "BUSY_OTHER", 0xFB: "DEBUG_END"}

  def _send_msg(self, msg:int, param:int, read_back_arg=False, timeout=10000, debug=False): # default timeout is 10 seconds
    self._smu_cmn_send_msg(msg, param, debug=debug)
    resp_reg = self.adev.mmMP1_SMN_C2PMSG_90 if not debug else self.adev.mmMP1_SMN_C2PMSG_54
    wait_cond(lambda: resp_reg.read() in {1, *self.smu_resp}, value=True, timeout_ms=timeout, msg=f"SMU msg {msg:#x} timeout")
    if (resp:=resp_reg.read()) != 1:
      raise SMUError(f"SMU refused msg {msg:#x} (param {param:#x}): {self.smu_resp[resp]} [{resp:#x}]")
    return (self.adev.mmMP1_SMN_C2PMSG_82 if not debug else self.adev.mmMP1_SMN_C2PMSG_53).read() if read_back_arg else None

class AM_GFX(AM_IP):
  def init_sw(self):
    self.xccs = len(self.adev.regs_offset[am.GC_HWIP])
    self.mqd_paddr = [self.adev.mm.palloc(0x1000 * self.xccs, zero=False, boot=True) for i in range(2)]
    self.mqd_mc = [self.adev.paddr2mc(mqd_paddr) for mqd_paddr in self.mqd_paddr]

  def init_hw(self):
    # Wait for RLC autoload to complete
    wait_cond(lambda: self.adev.regCP_STAT.read() == 0 or self.adev.regRLC_RLCS_BOOTLOAD_STATUS.read_bitfields()['bootload_complete'] == 0,
              value=True, msg="RLC autoload timeout")

    self.adev.gmc.init_hub("GC", inst_cnt=self.xccs)
    if self.adev.partial_boot: return self.reset_mec()

    self._config_mec()

    # NOTE: Golden reg for gfx11. No values for this reg provided. The kernel just ors 0x20000000 to this reg.
    # Not gfx10: there 0x20000000 is DB_DEBUG's golden value, and mmTCP_CNTL's is 0x479c0010
    # (gfx_v10_0.c:492). Applying the gfx11 or-mask here would write the wrong value, so gfx10.3
    # skips it -- its golden registers are their own job.
    if self.adev.ip_ver[am.GC_HWIP][0] != 10:
      for xcc in range(self.xccs): self.adev.regTCP_CNTL.write(self.adev.regTCP_CNTL.read() | 0x20000000, inst=xcc)

    for xcc in range(self.xccs): self.adev.regRLC_CNTL.write(0x1, inst=xcc)

    for xcc in range(self.xccs): self.adev.regRLC_SRM_CNTL.update(srm_enable=1, auto_incr_addr=1, inst=xcc)

    for xcc in range(self.xccs): self.adev.regRLC_SPM_MC_CNTL.write(0xf, inst=xcc)

    if self.adev.ip_ver[am.NBIO_HWIP][:2] != (7,9):
      self.adev.soc.doorbell_enable(port=0, awid=0x3, awaddr_31_28_value=0x3)
      self.adev.soc.doorbell_enable(port=3, awid=0x6, awaddr_31_28_value=0x3)

    for xcc in range(self.xccs):
      if self.adev.ip_ver[am.GC_HWIP] in {(9,4,3), (9,5,0)}:
        self.adev.regGB_ADDR_CONFIG.write(0x2a114042, inst=xcc) # Golden value for mi300/mi350
        self.adev.regTCP_UTCL1_CNTL2.update(spare=1, inst=xcc)

      self.adev.regGRBM_CNTL.update(read_timeout=0xff, inst=xcc)
      for i in range(0, 16):
        self._grbm_select(vmid=i, inst=xcc)
        self.adev.regSH_MEM_CONFIG.write(**({'initial_inst_prefetch':3} if self.adev.ip_ver[am.GC_HWIP][0]>=10 else {'retry_disable':1}),
          **({'f8_mode':1} if self.adev.ip_ver[am.GC_HWIP][:2]==(9,4) else {}),
          address_mode=self.adev.soc.module.SH_MEM_ADDRESS_MODE_64, alignment_mode=self.adev.soc.module.SH_MEM_ALIGNMENT_MODE_UNALIGNED, inst=xcc)

        # Configure apertures:
        # LDS:         0x10000000'00000000 - 0x10000001'00000000 (4GB)
        # Scratch:     0x20000000'00000000 - 0x20000001'00000000 (4GB)
        self.adev.regSH_MEM_BASES.write(shared_base=0x1, private_base=0x2, inst=xcc)
      self._grbm_select(inst=xcc)

      # Configure MEC doorbell range
      self.adev.regCP_MEC_DOORBELL_RANGE_LOWER.write(0x100 * xcc, inst=xcc)
      self.adev.regCP_MEC_DOORBELL_RANGE_UPPER.write(0x100 * xcc + 0xf8, inst=xcc)

    self._enable_mec()

    # Set 1 partition
    if self.xccs > 1: self.adev.psp._spatial_partition_cmd(1)

  def fini_hw(self): self._dequeue_hqds()

  def reset_mec(self):
    self._dequeue_hqds()

    if self.adev.ip_ver[am.GC_HWIP] < (12,0,0): # gfx12+ uses mec_pipe0_reset
      for xcc in range(self.xccs): self.adev.regGRBM_SOFT_RESET.write(soft_reset_cp=1, soft_reset_cpc=1, inst=xcc)
      time.sleep(0.05)
      for xcc in range(self.xccs): self.adev.regGRBM_SOFT_RESET.write(0x0, inst=xcc)

    self._config_mec()
    self._enable_mec()

  def setup_ring(self, ring_addr:int, ring_size:int, rptr_addr:int, wptr_addr:int, eop_addr:int, eop_size:int, idx:int, aql:bool) -> int:
    pipe, queue, doorbell = idx // 4, idx % 4, am.AMDGPU_NAVI10_DOORBELL_MEC_RING0

    for xcc in range(self.xccs if aql else 1):
      self._grbm_select(me=1, pipe=pipe, queue=queue, inst=xcc)

      struct_t = getattr(am, f"struct_v{self.adev.ip_ver[am.GC_HWIP][0]}{'_compute' if self.adev.ip_ver[am.GC_HWIP][0] >= 10 else ''}_mqd")
      mqd_struct = struct_t(header=0xC0310800, cp_mqd_base_addr_lo=lo32(self.mqd_mc[queue] + 0x1000*xcc),
        cp_mqd_base_addr_hi=hi32(self.mqd_mc[queue] + 0x1000*xcc), cp_hqd_pipe_priority=0x2, cp_hqd_queue_priority=0xf, cp_hqd_quantum=0x111,
        cp_hqd_persistent_state=self.adev.regCP_HQD_PERSISTENT_STATE.encode(preload_size=0x55, preload_req=1),
        cp_hqd_pq_base_lo=lo32(ring_addr>>8), cp_hqd_pq_base_hi=hi32(ring_addr>>8),
        cp_hqd_pq_rptr_report_addr_lo=lo32(rptr_addr), cp_hqd_pq_rptr_report_addr_hi=hi32(rptr_addr),
        cp_hqd_pq_wptr_poll_addr_lo=lo32(wptr_addr), cp_hqd_pq_wptr_poll_addr_hi=hi32(wptr_addr),
        cp_hqd_pq_doorbell_control=self.adev.regCP_HQD_PQ_DOORBELL_CONTROL.encode(doorbell_offset=doorbell*2, doorbell_en=1),
        cp_hqd_pq_control=self.adev.regCP_HQD_PQ_CONTROL.encode(rptr_block_size=5, unord_dispatch=0, queue_size=(ring_size//4).bit_length()-2,
          **({'queue_full_en':1, 'slot_based_wptr':2, 'no_update_rptr':xcc!=0 or self.xccs==1} if aql else {})),
        cp_hqd_ib_control=self.adev.regCP_HQD_IB_CONTROL.encode(min_ib_avail_size=0x3), cp_hqd_hq_status0=0x20004000,
        cp_mqd_control=self.adev.regCP_MQD_CONTROL.encode(priv_state=1), cp_hqd_vmid=0, cp_hqd_aql_control=int(aql),
        cp_hqd_eop_base_addr_lo=lo32(eop_addr>>8), cp_hqd_eop_base_addr_hi=hi32(eop_addr>>8),
        cp_hqd_eop_control=self.adev.regCP_HQD_EOP_CONTROL.encode(eop_size=(eop_size//4).bit_length()-2),
        **({'compute_tg_chunk_size':1, 'compute_current_logic_xcc_id':xcc, 'cp_mqd_stride_size':0x1000} if aql and self.xccs > 1 else {}))
      for se in range(8 if self.adev.ip_ver[am.GC_HWIP][0] >= 10 else 4): setattr(mqd_struct, f'compute_static_thread_mgmt_se{se}', 0xffffffff)

      self.adev.vram.view(self.mqd_paddr[queue] + 0x1000*xcc, ctypes.sizeof(mqd_struct))[:] = memoryview(mqd_struct).cast('B')

      mqd_st_mv = to_mv(ctypes.addressof(mqd_struct), ctypes.sizeof(mqd_struct)).cast('I')
      for i, reg in enumerate(range(self.adev.regCP_MQD_BASE_ADDR.addr[xcc], self.adev.regCP_HQD_PQ_WPTR_HI.addr[xcc] + 1)):
        self.adev.wreg(reg, mqd_st_mv[0x80 + i])
      self.adev.regCP_HQD_ACTIVE.write(0x1, inst=xcc)

      self.adev.gmc.flush_hdp()
      self._grbm_select(inst=xcc)
    return doorbell

  def set_clockgating_state(self):
    if hasattr(self.adev, 'regMM_ATC_L2_MISC_CG'): self.adev.regMM_ATC_L2_MISC_CG.write(enable=1, mem_ls_enable=1)

    for xcc in range(self.xccs):
      self.adev.regRLC_SAFE_MODE.write(message=1, cmd=1, inst=xcc)
      wait_cond(lambda: self.adev.regRLC_SAFE_MODE.read(inst=xcc) & 0x1, value=0, msg="RLC safe mode timeout")

      self.adev.regRLC_CGCG_CGLS_CTRL.update(cgcg_gfx_idle_threshold=0x36, cgcg_en=1, cgls_rep_compansat_delay=0xf, cgls_en=1, inst=xcc)

      self.adev.regCP_RB_WPTR_POLL_CNTL.update(poll_frequency=0x100, idle_poll_count=0x90, inst=xcc)
      self.adev.regCP_INT_CNTL.update(cntx_busy_int_enable=1, cntx_empty_int_enable=1, cmp_busy_int_enable=1, inst=xcc)
      # These arrive with gfx11 -- they are absent from the gfx10.3 and gfx9.4 register sets, and
      # sdma_v5_2.c writes no SDMA CGCG register at all for Navi 2x.
      if self.adev.ip_ver[am.GC_HWIP] >= (11,0,0):
        self.adev.regSDMA0_RLC_CGCG_CTRL.update(cgcg_int_enable=1, inst=xcc)
        self.adev.regSDMA1_RLC_CGCG_CTRL.update(cgcg_int_enable=1, inst=xcc)

      feats_gfx9 = {'gfxip_mgls_override':0, 'gfxip_rep_fgcg_override':0} if self.adev.ip_ver[am.GC_HWIP][0] == 9 else {}
      feats_gfx11 = {'perfmon_clock_state':1, 'gfxip_repeater_fgcg_override':0} if self.adev.ip_ver[am.GC_HWIP][0] >= 11 else {}
      self.adev.regRLC_CGTT_MGCG_OVERRIDE.update(**feats_gfx9, **feats_gfx11, gfxip_fgcg_override=0, grbm_cgtt_sclk_override=0,
        rlc_cgtt_sclk_override=0, gfxip_mgcg_override=0, gfxip_cgls_override=0, gfxip_cgcg_override=0, inst=xcc)

      self.adev.regRLC_SAFE_MODE.write(message=0, cmd=1, inst=xcc)

  def _grbm_select(self, me=0, pipe=0, queue=0, vmid=0, inst=0):
    self.adev.regGRBM_GFX_CNTL.write(meid=me, pipeid=pipe, vmid=vmid, queueid=queue, inst=inst)

  def _enable_mec(self):
    for xcc in range(self.xccs):
      # RS64 microengines arrive with gfx11. gfx9 and gfx10 are both F32 and start the same
      # way: write CP_MEC_CNTL back to zero (gfx_v10_0.c:6460, gfx_v9_0 does the same).
      if self.adev.ip_ver[am.GC_HWIP] >= (11,0,0): self.adev.regCP_MEC_RS64_CNTL.update(mec_pipe0_reset=0, mec_pipe0_active=1, mec_halt=0, inst=xcc)
      else: self.adev.regCP_MEC_CNTL.write(0x0, inst=xcc)
    time.sleep(0.05)  # Wait for MEC to be ready

  def _config_mec(self):
    def _config_helper(eng_name, cntl_reg, eng_reg, pipe_cnt, me=0, xcc=0):
      for pipe in range(pipe_cnt):
        self._grbm_select(me=me, pipe=pipe, inst=xcc)
        self.adev.wreg_pair(f"regCP_{eng_reg}_PRGRM_CNTR_START", "", "_HI", self.adev.fw.ucode_start[eng_name] >> 2, inst=xcc)
      self._grbm_select(inst=xcc)
      self.adev.reg(f"regCP_{cntl_reg}_CNTL").update(**{f"{eng_name.lower()}_pipe{pipe}_reset": 1 for pipe in range(pipe_cnt)}, inst=xcc)
      self.adev.reg(f"regCP_{cntl_reg}_CNTL").update(**{f"{eng_name.lower()}_pipe{pipe}_reset": 0 for pipe in range(pipe_cnt)}, inst=xcc)

    for xcc in range(self.adev.gfx.xccs):
      if self.adev.ip_ver[am.GC_HWIP] < (10,0,0):
        self.adev.regCP_MEC_CNTL.update(mec_invalidate_icache=1, mec_me1_pipe0_reset=1, mec_me2_pipe0_reset=1, mec_me1_halt=1,mec_me2_halt=1,inst=xcc)
      elif self.adev.ip_ver[am.GC_HWIP] < (11,0,0):
        # gfx10.3's MEC is F32 with no program counter to point anywhere, so there is no
        # ucode_start for it and the RS64 helper below has nothing to write. The whole sequence
        # is halt here, zero in _enable_mec (gfx_v10_0.c:6460-6484) -- no icache invalidate and
        # no pipe reset, which belong to gfx9's direct-load path and not to the PSP path.
        self.adev.regCP_MEC_CNTL.update(mec_me1_halt=1, mec_me2_halt=1, inst=xcc)
      if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0):
        _config_helper(eng_name="PFP", cntl_reg="ME", eng_reg="PFP", pipe_cnt=1, xcc=xcc)
        _config_helper(eng_name="ME", cntl_reg="ME", eng_reg="ME", pipe_cnt=1, xcc=xcc)
      if self.adev.ip_ver[am.GC_HWIP] >= (11,0,0):
        _config_helper(eng_name="MEC", cntl_reg="MEC_RS64", eng_reg="MEC_RS64", pipe_cnt=1, me=1, xcc=xcc)

  def _dequeue_hqds(self):
    for q in range(2):
      for xcc in range(self.xccs):
        self._grbm_select(me=1, pipe=0, queue=q, inst=xcc)
        if self.adev.regCP_HQD_ACTIVE.read(inst=xcc) & 1:
          self.adev.regCP_HQD_DEQUEUE_REQUEST.write(0x2, inst=xcc) # 1 - DRAIN_PIPE; 2 - RESET_WAVES
          self.adev.regSPI_COMPUTE_QUEUE_RESET.write(0x1, inst=xcc)
          if not self.adev.is_err_state: wait_cond(lambda: self.adev.regCP_HQD_ACTIVE.read(inst=xcc) & 1, value=0, msg="HQD dequeue timeout")
    self._grbm_select()

class AM_IH(AM_IP):
  def init_sw(self):
    self.ring_size = 256 << 10
    def _alloc_ring(size): return (self.adev.mm.palloc(size, zero=False, boot=True), self.adev.mm.palloc(0x1000, zero=False, boot=True))
    self.rings = [(*_alloc_ring(self.ring_size), "", 0), (*_alloc_ring(self.ring_size), "_RING1", 1)]
    self.ring_view = self.adev.vram.view(offset=self.rings[0][0], size=self.ring_size, fmt='I')

  def init_hw(self):
    for ring_vm, rwptr_vm, suf, ring_id in self.rings:
      self.adev.wreg_pair("regIH_RB_BASE", suf, f"_HI{suf}", self.adev.paddr2mc(ring_vm) >> 8)

      self.adev.reg(f"regIH_RB_CNTL{suf}").write(mc_space=4, wptr_overflow_clear=1, rb_size=((self.ring_size//4)-1).bit_length(),
        mc_snoop=1, mc_ro=0, mc_vmid=0, **({'wptr_overflow_enable': 1, 'rptr_rearm': 1} if ring_id == 0 else {'rb_full_drain_enable': 1}))

      if ring_id == 0: self.adev.wreg_pair("regIH_RB_WPTR_ADDR", "_LO", "_HI", self.adev.paddr2mc(rwptr_vm))

      self.adev.reg(f"regIH_RB_WPTR{suf}").write(0)
      self.adev.reg(f"regIH_RB_RPTR{suf}").write(0)

      self.adev.reg(f"regIH_DOORBELL_RPTR{suf}").write(enable=0)

    if self.adev.ip_ver[am.OSSSYS_HWIP] != (4,4,2):
      self.adev.regIH_STORM_CLIENT_LIST_CNTL.update(client18_is_storm_client=1)
      self.adev.regIH_INT_FLOOD_CNTL.update(flood_cntl_enable=1)
      # OSSSYS 5 has no MSI storm register, and navi10_ih.c programs no storm block on Navi 2x.
      if self.adev.ip_ver[am.OSSSYS_HWIP] >= (6,0,0): self.adev.regIH_MSI_STORM_CTRL.update(delay=3)

    # toggle interrupts
    for _, rwptr_vm, suf, ring_id in self.rings:
      self.adev.reg(f"regIH_RB_CNTL{suf}").update(rb_enable=1, **({'enable_intr': 1} if ring_id == 0 else {}))

  def drain(self):
    _, _, suf, _ = self.rings[0]
    wptr = self.adev.reg(f"regIH_RB_WPTR{suf}").read_bitfields()
    self.adev.regIH_RB_RPTR.write(wptr['offset'] % (self.ring_size // 4))

    if wptr['rb_overflow']:
      self.adev.reg(f"regIH_RB_WPTR{suf}").update(rb_overflow=0)
      self.adev.reg(f"regIH_RB_CNTL{suf}").update(wptr_overflow_clear=1)
      self.adev.reg(f"regIH_RB_CNTL{suf}").update(wptr_overflow_clear=0)

  def interrupt_handler(self):
    _, _, suf, _ = self.rings[0]
    wptr = self.adev.reg(f"regIH_RB_WPTR{suf}").read_bitfields()
    rptr = self.adev.regIH_RB_RPTR.read()

    while rptr != wptr['offset']:
      entry = [self.ring_view[(rptr + i) % (self.ring_size // 4)] for i in range(8)]
      rptr = (rptr + 8) % (self.ring_size // 4)

      client, src, ring_id, vmid, vmid_type, pasid, node = \
        [getattr(am, f'SOC15_{n}_FROM_IH_ENTRY')(entry) for n in ['CLIENT_ID', 'SOURCE_ID', 'RING_ID', 'VMID', 'VMID_TYPE', 'PASID', 'NODEID']]
      ctx = [getattr(am, f'SOC15_CONTEXT_ID{i}_FROM_IH_ENTRY')(entry) for i in range(4)]

      src_name = self.adev.soc.ih_srcs_names.get(client, {}).get(src, '')
      # CP_EOP_INTERRUPT, not CP_EOP_INTR: no SRCID constant of any generation is spelled the
      # latter, so end-of-pipe -- the ordinary completion interrupt for every dispatch -- never
      # matched and fell through to `else: is_err_state = True` below. That is true on gfx9 and
      # gfx11 as well, not just here.
      if src_name in {"SDMA_TRAP", "CP_EOP_INTERRUPT"}: continue

      print(f"am {self.adev.devfmt}: IH ({rptr:#x}/{wptr['offset']:#x}) client={self.adev.soc.ih_clients.get(client)} src={src_name}({src}) "
            f"ring={ring_id} vmid={vmid}({vmid_type}) pasid={pasid} node={node} ctx=[{ctx[0]:#x}, {ctx[1]:#x}, {ctx[2]:#x}, {ctx[3]:#x}]")

      if src_name == "SQ_INTERRUPT_ID":
        enc_type = getbits(ctx[1], 6, 7) if (is_soc21:=self.adev.ip_ver[am.GC_HWIP][0] >= 11) else getbits(ctx[0], 26, 27)
        err_type = getbits(ctx[0], 21, 24) if is_soc21 else getbits((ctx[0] & 0xfff) | ((ctx[0]>>16) & 0xf000) | ((ctx[1]<<16) & 0xff0000), 20, 23)
        err_info = f" ({['EDC_FUE', 'ILLEGAL_INST', 'MEMVIOL', 'EDC_FED'][err_type]})" if enc_type == 2 else ""
        print(f"am {self.adev.devfmt}: sq_intr: {['auto', 'wave', 'error'][enc_type]}{err_info}")
        self.adev.is_err_state |= enc_type == 2
      elif src_name == "UTCL2_FAULT" or (self.adev.ip_ver[am.GC_HWIP][0] == 9 and client == am.SOC15_IH_CLIENTID_UTCL2):
        bf = self.adev.reg(self.adev.gmc.pf_status_reg('GC')).read_bitfields()
        va = (self.adev.reg('regGCVM_L2_PROTECTION_FAULT_ADDR_HI32').read()<<32) | self.adev.reg('regGCVM_L2_PROTECTION_FAULT_ADDR_LO32').read()
        print(f"am {self.adev.devfmt}: GCVM_L2_PROTECTION_FAULT_STATUS: {bf} {va<<12:#x}")
        self.adev.reg('regGCVM_L2_PROTECTION_FAULT_CNTL').update(clear_protection_fault_status_addr=1)
        self.adev.is_err_state = True
      else: self.adev.is_err_state = True

    self.drain()

    bif_intr = self.adev.regBIF_BX0_BIF_DOORBELL_INT_CNTL.read_bitfields()
    athub_err, cntlr_err = bif_intr['ras_athub_err_event_interrupt_status'], bif_intr['ras_cntlr_interrupt_status']
    if athub_err or cntlr_err:
      print(f"am {self.adev.devfmt}: fatal hardware error detected: {'RAS_ATHUB_ERR_EVENT ' if athub_err else ''}{'RAS_CNTLR' if cntlr_err else ''}")

      acas = self.adev.smu._aca_read_banks(ue=True) + self.adev.smu._aca_read_banks(ue=False)
      for regs in acas:
        acatyp = 'Uncorrectable' if (regs[1] >> 61) & 1 and (regs[1] >> 57) & 1 else 'Correctable'
        hwname = f'{self.adev.hwid_names.get((regs[5] >> 32) & 0xFFF, "")} ({(regs[5] >> 32) & 0xFFF:#03x})'
        print(f"am {self.adev.devfmt}: {acatyp} ACA: {hwname} mcatype={(regs[5] >> 48) & 0xFFFF:#06x} regs=[{', '.join(f'{r:#x}' for r in regs)}]")

      self.adev.regBIF_BX0_BIF_DOORBELL_INT_CNTL.write(ras_cntlr_interrupt_clear=cntlr_err, ras_athub_err_event_interrupt_clear=athub_err)
      self.adev.is_err_state = True

class AM_SDMA(AM_IP):
  def init_sw(self): self.sdma_reginst, self.sdma_name = [], "F32" if self.adev.ip_ver[am.SDMA0_HWIP] < (7,0,0) else "MCU"
  def init_hw(self):
    for pipe_id in range(16 if self.adev.ip_ver[am.SDMA0_HWIP] < (5,0,0) else 1):
      pipe, inst = ("", pipe_id) if self.adev.ip_ver[am.SDMA0_HWIP] < (5,0,0) else (str(pipe_id), 0)

      if self.adev.ip_ver[am.SDMA0_HWIP] >= (6,0,0):
        self.adev.reg(f"regSDMA{pipe}_WATCHDOG_CNTL").update(queue_hang_count=100, inst=inst) # 10s, 100ms per unit
        self.adev.reg(f"regSDMA{pipe}_UTCL1_CNTL").update(resp_mode=3, redo_delay=9, inst=inst)

        # rd=noa, wr=bypass
        self.adev.reg(f"regSDMA{pipe}_UTCL1_PAGE").update(rd_l2_policy=2, wr_l2_policy=3, **({'llc_noalloc':1} if self.sdma_name == "F32" else {}),
                                                          inst=inst)
        self.adev.reg(f"regSDMA{pipe}_{self.sdma_name}_CNTL").update(halt=0, **{f"{'th1_' if self.sdma_name == 'F32' else ''}reset":0}, inst=inst)

      self.adev.reg(f"regSDMA{pipe}_CNTL").update(trap_enable=1,
        **({'utc_l1_enable':1} if self.adev.ip_ver[am.SDMA0_HWIP] <= (5,2,0) else {}), inst=inst)

    if self.adev.ip_ver[am.NBIO_HWIP] in {(7,9,0), (7,9,1)}:
      for aid_id in range(4):
        for dev_inst, (port, awid, offset, awaddr) in enumerate([(1, 0xe, 0xe, 0x1), (2, 0x8, 0x8, 0x2), (5, 0x9, 0x9, 0x8), (6, 0xa, 0xa, 0x9)]):
          entry = dev_inst + 1 + 4 * aid_id
          self.adev.reg(f"regDOORBELL0_CTRL_ENTRY_{entry}").write(**{f"bif_doorbell{entry}_range_size_entry": 20,
            f"bif_doorbell{entry}_range_offset_entry": (am.AMDGPU_NAVI10_DOORBELL_sDMA_ENGINE0 + (entry - 1) * 0xA) * 2})
          self.adev.soc.doorbell_enable(port=port, awid=awid, awaddr_31_28_value=awaddr, offset=offset, size=4, aid=aid_id)
    else:
      self.adev.soc.doorbell_enable(port=2, awid=0xe, awaddr_31_28_value=0x3, offset=am.AMDGPU_NAVI10_DOORBELL_sDMA_ENGINE0*2, size=4)
      # Same routing expressed the way nbio 2.3 expresses it, one register per engine. The
      # window is 20 doorbells wide, matching adev->doorbell_index.sdma_doorbell_range, and the
      # offset is the ring's own doorbell index in dwords -- the value setup_ring() writes to
      # SDMA{i}_GFX_DOORBELL_OFFSET.
      for inst in range(2):
        self.adev.soc.doorbell_range(f"SDMA{inst}", (am.AMDGPU_NAVI10_DOORBELL_sDMA_ENGINE0 + inst * 0xA) * 2, 20)

  def fini_hw(self):
    for reg, inst in self.sdma_reginst:
      self.adev.reg(f"{reg}_RB_CNTL").update(rb_enable=0, inst=inst)
      self.adev.reg(f"{reg}_IB_CNTL").update(ib_enable=0, inst=inst)
      self.adev.reg(f"{reg}_DOORBELL").update(enable=0, inst=inst)
      self.adev.reg(f"{reg}_DOORBELL_OFFSET").update(offset=0, inst=inst)

    if self.adev.ip_ver[am.SDMA0_HWIP] >= (6,0,0):
      self.adev.regGRBM_SOFT_RESET.write(soft_reset_sdma0=1)
      time.sleep(0.01)
      self.adev.regGRBM_SOFT_RESET.write(0x0)

  def setup_ring(self, ring_addr:int, ring_size:int, rptr_addr:int, wptr_addr:int, idx:int) -> int:
    if self.adev.ip_ver[am.SDMA0_HWIP] >= (5,0,0) and idx > 0: raise RuntimeError(f"am {self.adev.devfmt}: sdma queue {idx} is not available")

    pipe, queue = idx // 4, idx % 4
    # Three different spellings of the same ring across three generations: MI300 (4.4) has one
    # SDMA_GFX block addressed by instance, SDMA 5.x names it SDMA{i}_GFX, and 6.x onward
    # names it SDMA{i}_QUEUE{q}. gc_10_3_0 carries 45 SDMA0_GFX_* registers and no QUEUE0 at all.
    if self.adev.ip_ver[am.SDMA0_HWIP][:2] == (4,4): reg, inst = "regSDMA_GFX", pipe+queue*4
    elif self.adev.ip_ver[am.SDMA0_HWIP] < (6,0,0): reg, inst = f"regSDMA{pipe}_GFX", 0
    else: reg, inst = f"regSDMA{pipe}_QUEUE{queue}", 0
    doorbell = am.AMDGPU_NAVI10_DOORBELL_sDMA_ENGINE0 + (pipe+queue*4) * 0xA
    self.sdma_reginst.append((reg, inst))

    self.adev.reg(f"{reg}_MINOR_PTR_UPDATE").write(0x1, inst=inst)
    self.adev.wreg_pair(f"{reg}_RB_RPTR", "", "_HI", 0, inst=inst)
    self.adev.wreg_pair(f"{reg}_RB_WPTR", "", "_HI", 0, inst=inst)
    self.adev.wreg_pair(f"{reg}_RB_BASE", "", "_HI", ring_addr >> 8, inst=inst)
    self.adev.wreg_pair(f"{reg}_RB_RPTR_ADDR", "_LO", "_HI", rptr_addr, inst=inst)
    self.adev.wreg_pair(f"{reg}_RB_WPTR_POLL_ADDR", "_LO", "_HI", wptr_addr, inst=inst)
    self.adev.reg(f"{reg}_DOORBELL_OFFSET").update(offset=doorbell * 2, inst=inst)
    self.adev.reg(f"{reg}_DOORBELL").update(enable=1, inst=inst)
    self.adev.reg(f"{reg}_MINOR_PTR_UPDATE").write(0x0, inst=inst)
    # SDMA 6.x folded wptr polling into RB_CNTL. 5.x has no such field -- it enables polling in
    # its own RB_WPTR_POLL_CNTL, read-modify-write, F32_POLL_ENABLE only (sdma_v5_2.c:573-579).
    poll_in_rb_cntl = self.adev.ip_ver[am.SDMA0_HWIP] >= (6,0,0)
    if not poll_in_rb_cntl and self.adev.ip_ver[am.SDMA0_HWIP][:2] != (4,4):
      self.adev.reg(f"{reg}_RB_WPTR_POLL_CNTL").update(f32_poll_enable=1, inst=inst)
    self.adev.reg(f"{reg}_RB_CNTL").write(**({f'{self.sdma_name.lower()}_wptr_poll_enable':1} if poll_in_rb_cntl else {}),
      rb_vmid=0, rptr_writeback_enable=1, rptr_writeback_timer=4, rb_enable=1, rb_priv=1, rb_size=(ring_size//4).bit_length()-1, inst=inst)
    self.adev.reg(f"{reg}_IB_CNTL").update(ib_enable=1, inst=inst)
    return doorbell

def psp_autoload_supported(mp0:tuple[int, int, int]) -> bool:
  """Whether the PSP builds the GFX image itself instead of taking a reg list.

  amdgpu_psp.c:167 turns this on by default and switches it off for a fixed list of MP0
  versions; this is that list. It decides three things, which is why it is worth naming once:
  the RLC autoload command, whether the MEC jump table is sent at all, and whether SMU goes
  through the ordinary firmware list.
  """
  return mp0 not in {(9,0,0), (10,0,0), (10,0,1), (11,0,2), (11,0,3), (11,0,4), (11,0,8),
                     (12,0,1), (13,0,2), (13,0,6), (13,0,14)}

class AM_PSP(AM_IP):
  def init_sw(self):
    self.reg_pref = "regMP0_SMN_C2PMSG" if self.adev.ip_ver[am.MP0_HWIP] < (14,0,0) else "regMPASP_SMN_C2PMSG"

    if self.adev.devfmt.startswith("usb:"):
      self.msg1_view, paddrs = self.adev.pci_dev.alloc_sysmem(512 << 10)
      self.msg1_addr = self.adev.mm.alloc_vaddr(size=self.msg1_view.nbytes, align=am.PSP_1_MEG)
      self.adev.mm.map_range(self.msg1_addr, self.msg1_view.nbytes, [(paddrs[0], self.msg1_view.nbytes)], AddrSpace.SYS, uncached=True, boot=True)
    else:
      self.msg1_paddr = self.adev.mm.palloc(am.PSP_1_MEG, align=am.PSP_1_MEG, zero=False, boot=True)
      self.msg1_addr, self.msg1_view = self.adev.paddr2mc(self.msg1_paddr), self.adev.vram.view(self.msg1_paddr, am.PSP_1_MEG, 'B')

    self.cmd_paddr = self.adev.mm.palloc(am.PSP_CMD_BUFFER_SIZE, zero=False, boot=True)
    self.fence_paddr = self.adev.mm.palloc(am.PSP_FENCE_BUFFER_SIZE, zero=True, boot=True)

    self.ring_size = 0x10000
    self.ring_paddr = self.adev.mm.palloc(self.ring_size, zero=False, boot=True)

    self.max_tmr_size, self.tmr_size = 0x1300000, 0
    self.boot_time_tmr = self.adev.ip_ver[am.MP0_HWIP] in {(13,0,6), (13,0,14), (14,0,2), (14,0,3)}
    self.autoload_tmr = self.adev.ip_ver[am.MP0_HWIP] not in {(13,0,6), (13,0,14)}
    self.tmr_paddr = self.adev.mm.palloc(self.max_tmr_size, align=am.PSP_TMR_ALIGNMENT, zero=False, boot=True) if not self.boot_time_tmr else 0

  def init_hw(self):
    # psp_v13 carries no separate SPL blob and reuses KDB for the SPL slot; psp_v11 and psp_v14
    # both ship a real one (Navi 23's is 928 bytes), and sending KDB twice leaves the SPL table
    # unloaded. Only MP0 13.x takes the substitution.
    spl_key = am.PSP_FW_TYPE_PSP_KDB if self.adev.ip_ver[am.MP0_HWIP][0] == 13 else am.PSP_FW_TYPE_PSP_SPL
    sos_components = [(am.PSP_FW_TYPE_PSP_KDB, am.PSP_BL__LOAD_KEY_DATABASE), (spl_key, am.PSP_BL__LOAD_TOS_SPL_TABLE),
      (am.PSP_FW_TYPE_PSP_SYS_DRV, am.PSP_BL__LOAD_SYSDRV), (am.PSP_FW_TYPE_PSP_SOC_DRV, am.PSP_BL__LOAD_SOCDRV),
      (am.PSP_FW_TYPE_PSP_INTF_DRV, am.PSP_BL__LOAD_INTFDRV), (am.PSP_FW_TYPE_PSP_DBG_DRV, am.PSP_BL__LOAD_DBGDRV),
      (am.PSP_FW_TYPE_PSP_RAS_DRV, am.PSP_BL__LOAD_RASDRV), (am.PSP_FW_TYPE_PSP_SOS, am.PSP_BL__LOAD_SOSDRV)]

    if not self.is_sos_alive():
      for fw, compid in sos_components: self._bootloader_load_component(fw, compid)
      wait_cond(self.is_sos_alive, value=True, msg="sOS failed to start")

    self._ring_create()
    if am.PSP_FW_TYPE_PSP_TOC in self.adev.fw.sos_fw: self._tmr_init()

    # SMU fw should be loaded before TMR.
    if hasattr(self.adev.fw, 'smu_psp_desc'): self._load_ip_fw_cmd(*self.adev.fw.smu_psp_desc)
    if not self.boot_time_tmr or not self.autoload_tmr: self._tmr_load_cmd()

    for psp_desc in self.adev.fw.descs: self._load_ip_fw_cmd(*psp_desc)

    # Autoload is a property of the PSP, not of GC: amdgpu leaves psp->autoload_supported set for
    # MP0 11.0.12 and psp_load_non_psp_fw() fires GFX_CMD_ID_AUTOLOAD_RLC for it by name
    # (amdgpu_psp.c:2800). Keying this on GC >= 11 sent Navi 23 down the gfx9 REG_LIST path
    # instead -- and its RL descriptor is empty, so that path could only ever have raised.
    if psp_autoload_supported(self.adev.ip_ver[am.MP0_HWIP]): self._rlc_autoload_cmd()
    elif am.PSP_FW_TYPE_PSP_RL in self.adev.fw.sos_fw:
      self._load_ip_fw_cmd([am.GFX_FW_TYPE_REG_LIST], self.adev.fw.sos_fw[am.PSP_FW_TYPE_PSP_RL])

  def is_sos_alive(self): return self.adev.reg(f"{self.reg_pref}_81").read() != 0x0

  def _wait_for_bootloader(self): wait_cond(lambda: self.adev.reg(f"{self.reg_pref}_35").read() & 0x80000000, value=0x80000000, msg="BL not ready")

  def _prep_msg1(self, data:memoryview):
    assert len(data) <= self.msg1_view.nbytes, f"msg1 buffer is too small {len(data):#x} > {self.msg1_view.nbytes:#x}"
    padded_data = pad_bytes(bytes(data) + b'\x00' * 4, 16) # HACK: apple's memcpy requires 16-bytes alignment
    self.msg1_view[:len(padded_data)] = padded_data
    self.adev.gmc.flush_hdp()

  def _bootloader_load_component(self, fw:int, compid:int):
    if fw not in self.adev.fw.sos_fw: return 0

    self._wait_for_bootloader()

    if DEBUG >= 2: print(f"am {self.adev.devfmt}: loading sos component: {am.enum_psp_fw_type.get(fw)}")

    self._prep_msg1(self.adev.fw.sos_fw[fw])
    self.adev.reg(f"{self.reg_pref}_36").write(self.msg1_addr >> 20)
    self.adev.reg(f"{self.reg_pref}_35").write(compid)

    return self._wait_for_bootloader() if compid != am.PSP_BL__LOAD_SOSDRV else 0

  def _tmr_init(self):
    # Load TOC and calculate TMR size
    self._prep_msg1(fwm:=self.adev.fw.sos_fw[am.PSP_FW_TYPE_PSP_TOC])
    self.tmr_size = self._load_toc_cmd(len(fwm)).resp.tmr_size
    assert self.tmr_size <= self.max_tmr_size

  def _ring_create(self):
    # If the ring is already created, destroy it
    if self.adev.reg(f"{self.reg_pref}_71").read() != 0:
      self.adev.reg(f"{self.reg_pref}_64").write(am.GFX_CTRL_CMD_ID_DESTROY_RINGS)

      # There might be handshake issue with hardware which needs delay
      time.sleep(0.02)

    # Wait until the sOS is ready
    wait_cond(lambda: self.adev.reg(f"{self.reg_pref}_64").read() & 0x80000000, value=0x80000000, msg="sOS not ready")

    self.adev.wreg_pair(self.reg_pref, "_69", "_70", self.adev.paddr2mc(self.ring_paddr))
    self.adev.reg(f"{self.reg_pref}_71").write(self.ring_size)
    self.adev.reg(f"{self.reg_pref}_64").write(am.PSP_RING_TYPE__KM << 16)

    # There might be handshake issue with hardware which needs delay
    time.sleep(0.02)

    wait_cond(lambda: self.adev.reg(f"{self.reg_pref}_64").read() & 0x8000FFFF, value=0x80000000, msg="sOS ring not created")

  def _ring_submit(self, cmd:am.struct_psp_gfx_cmd_resp) -> am.struct_psp_gfx_cmd_resp:
    msg = am.struct_psp_gfx_rb_frame(fence_value=(prev_wptr:=self.adev.reg(f"{self.reg_pref}_67").read()) + 1,
      cmd_buf_addr_lo=lo32(self.adev.paddr2mc(self.cmd_paddr)), cmd_buf_addr_hi=hi32(self.adev.paddr2mc(self.cmd_paddr)),
      fence_addr_lo=lo32(self.adev.paddr2mc(self.fence_paddr)), fence_addr_hi=hi32(self.adev.paddr2mc(self.fence_paddr)))

    self.adev.vram.view(self.cmd_paddr, ctypes.sizeof(cmd))[:] = memoryview(cmd).cast('B')
    self.adev.vram.view(self.ring_paddr + prev_wptr * 4, ctypes.sizeof(msg))[:] = memoryview(msg).cast('B')

    # Move the wptr
    self.adev.reg(f"{self.reg_pref}_67").write(prev_wptr + ctypes.sizeof(am.struct_psp_gfx_rb_frame) // 4)

    wait_cond(lambda: self.adev.vram.view(self.fence_paddr, 4, 'I')[0], value=msg.fence_value, msg="sOS ring not responding")

    resp = type(cmd).from_buffer(bytearray(self.adev.vram.view(self.cmd_paddr, ctypes.sizeof(cmd))[:]))
    if resp.resp.status != 0: raise RuntimeError(f"PSP command failed {resp.cmd_id} {resp.resp.status}")

    return resp

  def _load_ip_fw_cmd(self, fw_types:list[int], fw_bytes:memoryview):
    self._prep_msg1(fw_bytes)
    for fw_type in fw_types:
      if DEBUG >= 2: print(f"am {self.adev.devfmt}: loading fw: {am.enum_psp_gfx_fw_type.get(fw_type)}")
      cmd = am.struct_psp_gfx_cmd_resp(cmd_id=am.GFX_CMD_ID_LOAD_IP_FW)
      cmd.cmd.cmd_load_ip_fw.fw_phy_addr_hi, cmd.cmd.cmd_load_ip_fw.fw_phy_addr_lo = data64(self.msg1_addr)
      cmd.cmd.cmd_load_ip_fw.fw_size = len(fw_bytes)
      cmd.cmd.cmd_load_ip_fw.fw_type = fw_type
      self._ring_submit(cmd)

  def _tmr_load_cmd(self) -> am.struct_psp_gfx_cmd_resp:
    tmr_paddr = self.adev.paddr2xgmi(self.tmr_paddr) if self.tmr_paddr else 0

    cmd = am.struct_psp_gfx_cmd_resp(cmd_id=am.GFX_CMD_ID_SETUP_TMR)
    cmd.cmd.cmd_setup_tmr.buf_phy_addr_hi, cmd.cmd.cmd_setup_tmr.buf_phy_addr_lo = data64(self.adev.paddr2mc(self.tmr_paddr) if self.tmr_paddr else 0)
    cmd.cmd.cmd_setup_tmr.system_phy_addr_hi, cmd.cmd.cmd_setup_tmr.system_phy_addr_lo = data64(tmr_paddr)
    cmd.cmd.cmd_setup_tmr.bitfield.virt_phy_addr = 1
    cmd.cmd.cmd_setup_tmr.buf_size = self.tmr_size if self.tmr_paddr else 0
    return self._ring_submit(cmd)

  def _load_toc_cmd(self, toc_size:int) -> am.struct_psp_gfx_cmd_resp:
    cmd = am.struct_psp_gfx_cmd_resp(cmd_id=am.GFX_CMD_ID_LOAD_TOC)
    cmd.cmd.cmd_load_toc.toc_phy_addr_hi, cmd.cmd.cmd_load_toc.toc_phy_addr_lo = data64(self.msg1_addr)
    cmd.cmd.cmd_load_toc.toc_size = toc_size
    return self._ring_submit(cmd)

  def _spatial_partition_cmd(self, mode):
    cmd = am.struct_psp_gfx_cmd_resp(cmd_id=am.GFX_CMD_ID_SRIOV_SPATIAL_PART)
    cmd.cmd.cmd_spatial_part.mode = mode
    return self._ring_submit(cmd)

  def _rlc_autoload_cmd(self): return self._ring_submit(am.struct_psp_gfx_cmd_resp(cmd_id=am.GFX_CMD_ID_AUTOLOAD_RLC))
