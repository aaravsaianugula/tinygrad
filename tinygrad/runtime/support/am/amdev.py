from __future__ import annotations
import ctypes, collections, contextlib, dataclasses, functools, hashlib, array
from tinygrad.helpers import mv_address, getenv, DEBUG, lo32, hi32, fetch_fw
from tinygrad.runtime.autogen import pci
from tinygrad.runtime.autogen.am import am, fw
from tinygrad.runtime.support.amd import AMDReg, import_module, import_asic_regs
from tinygrad.runtime.support.memory import TLSFAllocator, MemoryManager, AddrSpace
from tinygrad.runtime.support.system import PCIDevice
from tinygrad.runtime.support.am.ip import AM_IP, AM_SOC, AM_GMC, AM_IH, AM_PSP, AM_SMU, AM_GFX, AM_SDMA, psp_autoload_supported, SMUError

AM_DEBUG = getenv("AM_DEBUG", 0)

@dataclasses.dataclass
class AMRegister(AMDReg):
  adev:AMDev

  def read(self, inst=0): return self.adev.rreg(self.addr[inst])
  def read_bitfields(self, inst=0) -> dict[str, int]: return self.decode(self.read(inst=inst))

  def write(self, _am_val:int=0, inst=0, **kwargs): self.adev.wreg(self.addr[inst], _am_val | self.encode(**kwargs))

  def update(self, inst=0, **kwargs): self.write(self.read(inst=inst) & ~self.fields_mask(*kwargs.keys()), inst=inst, **kwargs)

# The board-specific tail of PPTable_t -- I2cControllers through BoardReserved -- ships ZEROED in
# AMD's SMU firmware and is filled by the driver from the card's own VBIOS
# (sienna_cichlid_append_powerplay_table). Without it the SMU has no voltage-regulator mapping, and
# on a part whose GFXCLK is driven by a DFLL rather than a PLL the clock follows the voltage the VR
# supplies -- so the SMU accepts every SetSoftMinByFreq and cannot act on one. Measured on a Navi 23:
# gfxclk pinned at GfxclkFidle, 497 MHz of an available 2350, AverageSocketPower reporting 2 W
# because the current telemetry is uncalibrated for the same reason.
SMC_DPM_INFO_INDEX = 2                      # 0-based index in atom_master_list_of_data_tables_v2_1
SMC_DPM_INFO_V4_9 = (296, 4, 9)             # structuresize, format_revision, content_revision
SMC_DPM_INFO_BOARD_OFF = 4                  # offsetof(atom_smc_dpm_info_v4_9, I2cControllers)
PPTABLE_BOARD_OFF, PPTABLE_BOARD_LEN = 1344, 292   # PPTable_t I2cControllers .. end of BoardReserved

# ROM_INDEX / ROM_DATA within the SMUIO block, in dwords. smuio_11_0_6_offset.h shifts these one
# dword up from smuio_11_0_0_offset.h, and amdgpu picks between the two by SMUIO IP version
# (amdgpu_discovery.c:3575-3592). A Navi 23 reports SMUIO 11.0.10 and therefore takes the *_6 map;
# using the other one would write the ROM index into CGTT_ROM_CLK_CTRL0 -- the ROM clock-gating
# control -- on a live card. Only the versions the kernel names are listed, because an unknown
# SMUIO here has to be a refusal rather than a guess.
SMUIO_ROM_REGS: dict[tuple[int, ...], tuple[int, int]] = {
  **{v: (0xe4, 0xe5) for v in ((11,0,0), (11,0,2), (11,0,3), (11,0,4), (11,0,7), (11,0,8))},
  **{v: (0xe5, 0xe6) for v in ((11,0,6), (11,0,10), (11,0,11), (11,5,0), (11,5,2),
                               (13,0,1), (13,0,9), (13,0,10))},
}

def vbios_reader(adev):
  """A `read(offset, nbytes)` over the card's VBIOS, through SMUIO's ROM_INDEX/ROM_DATA window.

  amdgpu_soc15_read_bios_from_rom: write a byte offset to ROM_INDEX once, then read ROM_DATA
  repeatedly and the index auto-increments four bytes per dword. nbio_v2_3 has no get_rom_offset,
  so the base offset is zero. Reads only -- the index register is the single write, and nothing
  needs restoring afterwards.

  Before writing anything it identifies the pair without writing: reading ROM_DATA advances
  ROM_INDEX, so N reads must move the index by exactly 4N. If the register map were wrong that
  check fails and nothing has been written yet.
  """
  # RuntimeError rather than KeyError throughout: the caller degrades on RuntimeError, and a card
  # whose discovery table has no SMUIO block must lose its clocks, not fail to open at all.
  if am.SMUIO_HWIP not in adev.ip_ver or am.SMUIO_HWIP not in adev.regs_offset:
    raise RuntimeError("this card's discovery table has no SMUIO block, so there is no ROM window")
  if (ver:=tuple(adev.ip_ver[am.SMUIO_HWIP])) not in SMUIO_ROM_REGS:
    raise RuntimeError(f"no known ROM_INDEX/ROM_DATA map for SMUIO {'.'.join(map(str, ver))}")
  base = adev.regs_offset[am.SMUIO_HWIP][0][0]
  rom_index, rom_data = (base + off for off in SMUIO_ROM_REGS[ver])

  # Identify the window before writing to it, by reading only. Watching ROM_INDEX for the +4 the
  # kernel's loop relies on does not work here: on this part the index register reads back
  # unchanged while ROM_DATA streams. What does hold is that ROM_DATA is a moving window -- four
  # reads of a ROM return four different dwords, where any ordinary register returns one value
  # four times. If that fails we have the wrong pair and nothing has been written yet.
  if len(set(probe:=[adev.rreg(rom_data) for _ in range(4)])) == 1:
    raise RuntimeError(f"SMUIO {'.'.join(map(str, ver))} ROM window at {rom_index:#x}/{rom_data:#x} is not "
                       + f"streaming: four reads all returned {probe[0]:#x}. Not writing to it.")

  def read(off:int, n:int) -> bytes:
    # Seek to the containing dword and trim, so callers can ask for any byte range.
    adev.wreg(rom_index, start:=off & ~3)
    data = b''.join(adev.rreg(rom_data).to_bytes(4, 'little') for _ in range((off - start + n + 3) // 4))
    return data[off - start:off - start + n]
  return read

def atom_board_data(read) -> bytes:
  """The 292 board bytes for PPTable_t, walked out of a VBIOS through `read(offset, nbytes)`.

  Takes a reader rather than an image because on a USB-attached card every MMIO access is a round
  trip: pulling the whole 64 KiB to reach four small tables would add thousands of them to every
  device open. Every pointer in the ATOM chain is a u16, so the walk only ever seeks within the
  first 64 KiB, and this touches about a hundred dwords instead of sixteen thousand.

  The traversal is amdgpu_atom_parse_data_header's: the ROM header pointer at 0x48, its data-table
  pointer at +0x20, then entry SMC_DPM_INFO_INDEX of the master list, which sits after that
  table's own 4-byte common header. Every offset is relative to byte 0 of the image, never to its
  parent.

  Raises ValueError naming the specific check that failed. Nothing here may fall back to a
  plausible answer: these bytes are blitted over the voltage-regulator mapping and the current
  telemetry calibration, so a wrong 292 bytes is worse than none.
  """
  def rd(off:int, n:int) -> bytes:
    if len(b:=bytes(read(off, n))) != n: raise ValueError(f"VBIOS read at {off:#x} wanted {n} bytes, got {len(b)}")
    return b
  def u16(off:int) -> int: return int.from_bytes(rd(off, 2), 'little')

  if (sig:=rd(0, 2)) != bytes((0x55, 0xAA)): raise ValueError(f"not a PCI option ROM: starts {sig.hex()}, want 55aa")
  # atom.c compares 10 bytes and the leading space is part of the string. amdgpu_bios.c's
  # AMD_VBIOS_SIGNATURE_SIZE is a sizeof() and counts the NUL, which is why the two disagree by one.
  if (ati:=rd(0x30, 10)) != b" 761295520": raise ValueError(f"missing ATI signature at 0x30: {ati!r}")
  if not (base:=u16(0x48)): raise ValueError("ROM header pointer at 0x48 is zero")
  if (magic:=rd(base + 4, 4)) == b"MOTA":
    # A genuinely byte-swapped image is not a thing on a PCIe card. Far likelier the read path
    # transposed u16s, and a swapping parser would paper over a broken read.
    raise ValueError("ATOM magic reads 'MOTA': the ROM read is byte-swapping u16s, fix the read")
  if magic != b"ATOM": raise ValueError(f"no ATOM magic at ROM header + 4: {magic!r}")
  if not (data_table:=u16(base + 0x20)): raise ValueError("master data table pointer is zero")
  # +4 skips the master table's own atom_common_table_header. get_index_into_master_table
  # deliberately excludes it -- it offsets into the inner list -- so it is added exactly here.
  if not (smc:=u16(data_table + 4 + SMC_DPM_INFO_INDEX * 2)):
    raise ValueError("this VBIOS carries no smc_dpm_info table")

  hdr = rd(smc, 4)
  size, frev, crev = int.from_bytes(hdr[:2], 'little'), hdr[2], hdr[3]
  if (size, frev, crev) != SMC_DPM_INFO_V4_9:
    # atom_smc_dpm_info_v4_10 has a different shape entirely -- no I2cControllers at the front --
    # so reading it as v4_9 would silently produce garbage rather than fail.
    raise ValueError(f"smc_dpm_info is {size} bytes rev {frev}.{crev}, want {SMC_DPM_INFO_V4_9[0]} "
                     + f"rev {SMC_DPM_INFO_V4_9[1]}.{SMC_DPM_INFO_V4_9[2]}; refusing to read it as v4_9")
  board = rd(smc + SMC_DPM_INFO_BOARD_OFF, size - SMC_DPM_INFO_BOARD_OFF)
  if len(board) != PPTABLE_BOARD_LEN: raise ValueError(f"board span {len(board)} != {PPTABLE_BOARD_LEN}")
  # Sanity, so a table of zeros cannot be blitted in and look like the fix landed. Checked on
  # GfxMaxCurrent -- the current-telemetry slope, whose absence is precisely what stops PPT and TDC
  # asserting -- and on the memory channel mask. Deliberately NOT on VddGfxVrMapping: that is a
  # small rail index and zero is legitimate, as this card shows (gfx 0, soc 2, mem0 1, mem1 3).
  gfx_max_current = int.from_bytes(board[144 - SMC_DPM_INFO_BOARD_OFF:146 - SMC_DPM_INFO_BOARD_OFF], 'little')
  channels = int.from_bytes(board[196 - SMC_DPM_INFO_BOARD_OFF:200 - SMC_DPM_INFO_BOARD_OFF], 'little')
  if not gfx_max_current or not channels:
    raise ValueError(f"VBIOS board data reads empty (GfxMaxCurrent={gfx_max_current}, "
                     + f"MemoryChannelEnabled={channels:#x}); this table is not the missing data")
  return board

class AMFirmware:
  # linux-firmware ships Navi 2x discrete parts under AMD's codenames, not under the discovery IP
  # version AM builds names from, so psp_11_0_12_sos.bin and friends simply do not exist there.
  # This mirrors the kernel's amdgpu_ucode_legacy_naming(), which short-circuits numeric naming
  # for exactly these parts. The gfx10.3.3/10.3.6/10.3.7 APUs are deliberately absent from the
  # kernel's table and keep numeric names, so they stay absent here too.
  legacy_fw_names = {(am.MP0_HWIP, (11,0,12)): "dimgrey_cavefish", (am.MP1_HWIP, (11,0,12)): "dimgrey_cavefish_smc",
                     (am.SDMA0_HWIP, (5,2,4)): "dimgrey_cavefish_sdma", (am.GC_HWIP, (10,3,4)): "dimgrey_cavefish"}

  def __init__(self, adev):
    self.adev = adev
    def fmt_ver(hwip): return '_'.join(map(str, adev.ip_ver[hwip]))
    def fw_file(hwip, numeric, suffix=""):
      return self.legacy_fw_names.get((hwip, adev.ip_ver[hwip]), numeric) + suffix + ".bin"
    self.fw_file = fw_file

    # Load SOS firmware
    self.sos_fw = {}

    blob, sos_hdr = self.load_fw(fw_file(am.MP0_HWIP, f"psp_{fmt_ver(am.MP0_HWIP)}", "_sos"),
                                 versioned_header='struct_psp_firmware_header')

    if hasattr(sos_hdr, 'psp_fw_bin'):
      # v2.x: a packed descriptor table, each entry naming its own PSP_FW_TYPE.
      ucode_start = sos_hdr.header.ucode_array_offset_bytes
      for fw_i in range(sos_hdr.psp_fw_bin_count):
        fw_bin_desc = am.struct_psp_fw_bin_desc.from_address(ctypes.addressof(sos_hdr.psp_fw_bin)
                                                             + fw_i * ctypes.sizeof(am.struct_psp_fw_bin_desc))
        off = fw_bin_desc.offset_bytes + ucode_start
        self.sos_fw[fw_bin_desc.fw_type] = blob[off:off+fw_bin_desc.size_bytes]
    else:
      # v1.x: named legacy descriptors instead of a table. These are two entirely different
      # formats, which is why the kernel switches on header_version_major (amdgpu_psp.c:3443)
      # rather than treating it as a layout tweak. Navi 2x ships v1.3.
      v1_1 = getattr(sos_hdr, 'v1_1', sos_hdr)
      v1_0 = getattr(v1_1, 'v1_0', v1_1)
      ucode_start = v1_0.header.ucode_array_offset_bytes
      # sys is everything ahead of sos rather than a descriptor of its own (amdgpu_psp.c:3390).
      descs = [(am.PSP_FW_TYPE_PSP_SYS_DRV, 0, v1_0.sos.offset_bytes),
               (am.PSP_FW_TYPE_PSP_SOS, v1_0.sos.offset_bytes, v1_0.sos.size_bytes)]
      for fw_type, attr, holder in ((am.PSP_FW_TYPE_PSP_TOC, 'toc', v1_1), (am.PSP_FW_TYPE_PSP_KDB, 'kdb', v1_1),
                                    (am.PSP_FW_TYPE_PSP_SPL, 'spl', sos_hdr), (am.PSP_FW_TYPE_PSP_RL, 'rl', sos_hdr)):
        if (d:=getattr(holder, attr, None)) is not None: descs.append((fw_type, d.offset_bytes, d.size_bytes))
      # A zero-size descriptor means this part does not carry that component -- Navi 23's RL is
      # empty. Offering it anyway would hand the PSP a zero-length load, so it is left out and
      # the callers that need it test membership instead.
      for fw_type, off, size in descs:
        if size: self.sos_fw[fw_type] = blob[ucode_start+off:ucode_start+off+size]

    # Load other fw
    self.ucode_start: dict[str, int] = {}
    self.descs: list[tuple[list[int], memoryview]] = []
    # The SMU 11 pptable, when this part ships one. None everywhere else, and AM_SMU treats
    # None as "this SMU does not need a table", which is true of 13 and 14.
    self.smu_pptable: bytes|None = None

    # SMU firmware
    if adev.ip_ver[am.MP1_HWIP] != (13,0,12):
      blob, hdr = self.load_fw(fw_file(am.MP1_HWIP, f"smu_{fmt_ver(am.MP1_HWIP)}"), versioned_header="struct_smc_firmware_header")
      # The P2S branch below reads hdr.pptable_count, a field that exists only on
      # smc_firmware_header v2_1 -- the MI300 format. Navi 2x ships v2_0 (ppt_offset_bytes, no
      # pptable_count), so the old GC >= (11,0,0) split sent gfx10.3 down the MI path and raised
      # AttributeError. MI300 is GC 9.4.3, so >= (10,0,0) is the split that separates the two.
      if self.adev.ip_ver[am.GC_HWIP] >= (10,0,0):
        self.smu_psp_desc = self.desc(blob, hdr.v1_0.header.ucode_array_offset_bytes, hdr.v1_0.header.ucode_size_bytes, am.GFX_FW_TYPE_SMU)
        # SMU 11 will not release its DPM tables until the driver uploads a pptable, and the
        # blob carries one. The region ppt_offset_bytes points at is not a bare PPTable_t: it is
        # a `struct smu_11_0_7_powerplay_table` wrapper whose own table_size field is documented
        # as "the offset to smc_pptable including header size", so the firmware states where its
        # inner table begins rather than this having to encode a packed struct layout. On a Navi
        # 23 that reads 802 -- which is what summing the header, power_saving_clock_table and
        # overdrive_table gives -- and 802 + sizeof(PPTable_t) = 802 + 1668 is exactly the
        # 2470-byte region. SMU 13/14 boot with a usable soft pptable already loaded and need
        # none of this, so it is not extracted for them.
        if adev.ip_ver[am.MP1_HWIP][0] == 11 and hasattr(hdr, 'ppt_offset_bytes'):
          wrapper = bytes(blob[hdr.ppt_offset_bytes:hdr.ppt_offset_bytes + hdr.ppt_size_bytes])
          inner_off = int.from_bytes(wrapper[5:7], 'little')
          if 0 < inner_off < len(wrapper): self.smu_pptable = wrapper[inner_off:]
          else: print(f"am {adev.devfmt}: smc pptable header says smc_pptable starts at {inner_off}"
                      f" of {len(wrapper)} bytes; not uploading a table this driver cannot locate")
      else:
        p2stables = (am.struct_smc_soft_pptable_entry * hdr.pptable_count).from_buffer(blob[hdr.pptable_entry_offset:])
        for p2stable in p2stables:
          if p2stable.id == (__P2S_TABLE_ID_X:=0x50325358):
            self.descs += [self.desc(blob, p2stable.ppt_offset_bytes, p2stable.ppt_size_bytes, am.GFX_FW_TYPE_P2S_TABLE)]

    # SDMA firmware
    blob, hdr = self.load_fw(fw_file(am.SDMA0_HWIP, f"sdma_{fmt_ver(am.SDMA0_HWIP)}"), versioned_header="struct_sdma_firmware_header")
    if hdr.header.header_version_major == 1:
      # Sienna Cichlid's PSP takes exactly one SDMA blob and applies it to every engine -- the
      # kernel skips SDMA1/2/3 for MP0 11.0.7/11.0.11/11.0.12 by name, "as all four sdma fw are
      # same" (amdgpu_psp.c:2839-2848). Sending the other three would be three LOAD_IP_FW
      # commands for engines this part does not have.
      one_sdma = self.adev.ip_ver[am.MP0_HWIP] in {(11,0,7), (11,0,11), (11,0,12)}
      sdma_types = (am.GFX_FW_TYPE_SDMA0,) if one_sdma else (am.GFX_FW_TYPE_SDMA0, am.GFX_FW_TYPE_SDMA1,
                                                             am.GFX_FW_TYPE_SDMA2, am.GFX_FW_TYPE_SDMA3)
      self.descs += [self.desc(blob, hdr.header.ucode_array_offset_bytes, hdr.header.ucode_size_bytes, *sdma_types)]
    elif hdr.header.header_version_major == 2:
      self.descs += [self.desc(blob, hdr.ctl_ucode_offset, hdr.ctl_ucode_size_bytes, am.GFX_FW_TYPE_SDMA_UCODE_TH1)]
      self.descs += [self.desc(blob, hdr.header.ucode_array_offset_bytes, hdr.ctx_ucode_size_bytes, am.GFX_FW_TYPE_SDMA_UCODE_TH0)]
    else: self.descs += [self.desc(blob, hdr.header.ucode_array_offset_bytes, hdr.ucode_size_bytes, am.GFX_FW_TYPE_SDMA_UCODE_TH0)]

    # PFP, ME, CE, MEC firmware
    # gfx11 has the RLC load the graphics engines out of its autoload image, so AM never needed
    # PFP/ME there. gfx10.3 does not work that way: gfx_v10_0.c:4138-4174 hands CP_PFP, CP_ME,
    # CP_CE and CP_MEC1(+JT) to the PSP individually, and gfx10 keeps a separate CE that gfx11
    # dropped. They go ahead of MEC to match the order the kernel walks (amdgpu_ucode.h:478-492).
    gfx10_cp = [('PFP', 1), ('ME', 1), ('CE', 1)] if (10,0,0) <= self.adev.ip_ver[am.GC_HWIP] < (11,0,0) else []
    for (fw_name, fw_cnt) in ([('PFP', 1), ('ME', 1)] if self.adev.ip_ver[am.GC_HWIP] >= (12,0,0) else []) + gfx10_cp + [('MEC', 1)]:
      blob, hdr = self.load_fw(fw_file(am.GC_HWIP, f"gc_{fmt_ver(am.GC_HWIP)}", f"_{fw_name.lower()}"), versioned_header="struct_gfx_firmware_header")

      ucode_off = hdr.header.ucode_array_offset_bytes
      if hdr.header.header_version_major == 1:
        if fw_name == 'MEC':
          # Only MEC carries a jump table the PSP wants as a load of its own, and only MEC has
          # it subtracted from the main ucode (amdgpu_ucode.c:872-878; PFP/ME/CE fall to the
          # default case at :1024 and keep their full size). There is also no
          # GFX_FW_TYPE_CP_PFP_ME1 to name, so the JT desc cannot be built by string for them.
          self.descs += [self.desc(blob, ucode_off, hdr.header.ucode_size_bytes - hdr.jt_size * 4, am.GFX_FW_TYPE_CP_MEC)]
          # An autoload PSP builds the jump table itself and rejects being handed one --
          # fw_load_skip_check() drops CP_MEC1_JT for exactly these parts (amdgpu_psp.c:2780).
          if not psp_autoload_supported(self.adev.ip_ver[am.MP0_HWIP]):
            self.descs += [self.desc(blob, ucode_off + hdr.jt_offset * 4, hdr.jt_size * 4, am.GFX_FW_TYPE_CP_MEC_ME1)]
        else:
          self.descs += [self.desc(blob, ucode_off, hdr.header.ucode_size_bytes, getattr(am, f'GFX_FW_TYPE_CP_{fw_name}'))]
      else:
        # Code
        self.descs += [self.desc(blob, ucode_off, hdr.ucode_size_bytes, getattr(am, f'GFX_FW_TYPE_RS64_{fw_name}'))]
        # Stack
        stack_fws = [getattr(am, f'GFX_FW_TYPE_RS64_{fw_name}_P{fwnum}_STACK') for fwnum in range(fw_cnt)]
        self.descs += [self.desc(blob, hdr.data_offset_bytes, hdr.data_size_bytes, *stack_fws)]
        self.ucode_start[fw_name] = hdr.ucode_start_addr_lo | (hdr.ucode_start_addr_hi << 32)

    # IMU firmware
    if self.adev.ip_ver[am.GC_HWIP] >= (11,0,0):
      blob, hdr = self.load_fw(fw_file(am.GC_HWIP, f"gc_{fmt_ver(am.GC_HWIP)}", "_imu"), am.struct_imu_firmware_header_v1_0)
      imu_i_off, imu_i_sz, imu_d_sz = hdr.header.ucode_array_offset_bytes, hdr.imu_iram_ucode_size_bytes, hdr.imu_dram_ucode_size_bytes
      self.descs += [self.desc(blob, imu_i_off, imu_i_sz, am.GFX_FW_TYPE_IMU_I), self.desc(blob, imu_i_off+imu_i_sz, imu_d_sz, am.GFX_FW_TYPE_IMU_D)]

    # RLC firmware
    blob, hdr0, hdr1, hdr2, hdr3 = self.load_fw(fw_file(am.GC_HWIP, f"gc_{fmt_ver(am.GC_HWIP)}", "_rlc"), am.struct_rlc_firmware_header_v2_0,
      am.struct_rlc_firmware_header_v2_1, am.struct_rlc_firmware_header_v2_2, am.struct_rlc_firmware_header_v2_3)

    if hdr0.header.header_version_minor == 1:
      for mem,fmem in [('LIST_SRM_CNTL', 'list_cntl'), ('LIST_GPM_MEM', 'list_gpm'), ('LIST_SRM_MEM', 'list_srm')]:
        off, sz = getattr(hdr1, f'save_restore_{fmem}_offset_bytes'), getattr(hdr1, f'save_restore_{fmem}_size_bytes')
        self.descs += [self.desc(blob, off, sz, getattr(am, f'GFX_FW_TYPE_RLC_RESTORE_{mem}'))]

    if hdr0.header.header_version_minor >= 2:
      for mem,fmem in [('IRAM', 'iram'), ('DRAM_BOOT', 'dram')]:
        off, sz = getattr(hdr2, f'rlc_{fmem}_ucode_offset_bytes'), getattr(hdr2, f'rlc_{fmem}_ucode_size_bytes')
        self.descs += [self.desc(blob, off, sz, getattr(am, f'GFX_FW_TYPE_RLC_{mem}'))]

    if hdr0.header.header_version_minor == 3:
      for mem in ['P', 'V']:
        off, sz = getattr(hdr3, f'rlc{mem.lower()}_ucode_offset_bytes'), getattr(hdr3, f'rlc{mem.lower()}_ucode_size_bytes')
        self.descs += [self.desc(blob, off, sz, getattr(am, f'GFX_FW_TYPE_RLC_{mem}'))]

    self.descs += [self.desc(blob, hdr0.header.ucode_array_offset_bytes, hdr0.header.ucode_size_bytes, am.GFX_FW_TYPE_RLC_G)]

  def load_fw(self, fname:str, *headers, versioned_header:str|None=None):
    blob = memoryview(bytearray(fetch_fw("amdgpu", fname, fw.hashes[fname])))
    if AM_DEBUG >= 1: print(f"am {self.adev.devfmt}: loading firmware {fname}: {hashlib.sha256(blob).hexdigest()}")
    if versioned_header:
      chdr = am.struct_common_firmware_header.from_address(mv_address(blob))
      headers += (getattr(am, versioned_header + f"_v{chdr.header_version_major}_{chdr.header_version_minor}"),)
    return tuple([blob] + [hdr.from_address(mv_address(blob)) for hdr in headers])

  def desc(self, blob:memoryview, offset:int, size:int, *types:int) -> tuple[list[int], memoryview]: return (list(types), blob[offset:offset+size])

class AMPageTableEntry:
  def __init__(self, adev, paddr, lv): self.adev, self.paddr, self.lv, self.entries = adev, paddr, lv, adev.vram.view(paddr, 0x1000, fmt='Q')

  def set_entry(self, entry_id:int, paddr:int, table=False, uncached=False, aspace=AddrSpace.PHYS, snooped=False, frag=0, valid=True):
    is_sys = aspace is AddrSpace.SYS
    if aspace is AddrSpace.PHYS: paddr = self.adev.paddr2xgmi(paddr)
    assert paddr & self.adev.gmc.address_space_mask == paddr, f"Invalid physical address {paddr:#x}"
    self.entries[entry_id] = self.adev.gmc.get_pte_flags(self.lv, table, frag, uncached, is_sys, snooped, valid) | (paddr & 0x0000FFFFFFFFF000)

  def entry(self, entry_id:int) -> int: return self.entries[entry_id]
  def valid(self, entry_id:int) -> bool: return (self.entries[entry_id] & am.AMDGPU_PTE_VALID) != 0
  def address(self, entry_id:int) -> int:
    assert self.entries[entry_id] & am.AMDGPU_PTE_SYSTEM == 0, "should not be system address"
    return self.adev.xgmi2paddr(self.entries[entry_id] & 0x0000FFFFFFFFF000)
  def is_page(self, entry_id:int) -> bool: return self.lv == am.AMDGPU_VM_PTB or self.adev.gmc.is_pte_huge_page(self.lv, self.entries[entry_id])
  def supports_huge_page(self, paddr:int): return self.lv >= am.AMDGPU_VM_PDB2

class AMMemoryManager(MemoryManager):
  va_allocator = TLSFAllocator((1 << 44), base=0x200000000000) # global for all devices.

  def on_range_mapped(self):
    # Invalidate TLB after mappings.
    self.dev.gmc.flush_tlb(ip='GC', vmid=0)
    self.dev.gmc.flush_tlb(ip='MM', vmid=0)

class AMDev:
  Version = 0xA0000008

  def __init__(self, pci_dev:PCIDevice, reset_mode=False):
    self.pci_dev, self.devfmt = pci_dev, pci_dev.pcibus
    self.vram, self.doorbell64, self.mmio = self.pci_dev.map_bar(0), self.pci_dev.map_bar(2, fmt='Q'), self.pci_dev.map_bar(5, fmt='I')

    self._run_discovery()
    self._build_regs()

    # AM boot Process:
    # The GPU being passed can be in one of several states: 1. Not initialized. 2. Initialized by amdgpu. 3. Initialized by AM.
    # The 1st and 2nd states require a full GPU setup since their states are unknown. The 2nd state also requires a mode1 reset to
    # reinitialize all components.
    #
    # The 3rd state can be set up partially to optimize boot time. In this case, only the GFX and SDMA IPs need to be initialized.
    # To enable this, AM uses a separate boot memory that is guaranteed not to be overwritten. This physical memory is utilized for
    # all blocks that are initialized only during the initial AM boot.
    # To determine if the GPU is in the third state, AM uses regSCRATCH_REG7 as a flag.
    # To determine if the previous AM session finalized correctly, AM uses regSCRATCH_REG6 as a flag.
    self.is_booting = True # During boot only boot memory can be allocated. This flag is to validate this.
    self.init_sw(smi_dev=False)

    self.partial_boot = (self.reg("regSCRATCH_REG7").read() == AMDev.Version) and (getenv("AM_RESET", 0) != 1)
    if self.partial_boot and (self.reg("regSCRATCH_REG6").read() != 0 or self.reg(self.gmc.pf_status_reg("GC")).read() != 0):
      if DEBUG >= 2: print(f"am {self.devfmt}: Malformed state. Issuing a full reset.")
      self.partial_boot = False

    # Init hw for IP blocks where it is needed
    if not self.partial_boot:
      if self.psp.is_sos_alive() and self.smu.is_smu_alive():
        self.pci_dev.write_config_flush(pci.PCI_COMMAND, self.pci_dev.read_config(pci.PCI_COMMAND, 2) & ~pci.PCI_COMMAND_MASTER, 2)
        if self.is_hive():
          if reset_mode: return # in reset mode, do not raise
          raise RuntimeError("Malformed state. Use extra/amdpci/hive_reset.py to reset the hive")
        self.smu.mode1_reset()
      self.pci_dev.write_config_flush(pci.PCI_COMMAND, self.pci_dev.read_config(pci.PCI_COMMAND, 2) | pci.PCI_COMMAND_MASTER, 2)
      self.init_hw(self.soc, self.gmc, self.ih, self.psp, self.smu)

    # Booting done
    self.is_booting = False

    # Re-initialize main blocks
    self.init_hw(self.gfx, self.sdma)

    # Clock control is a performance step, not a correctness one: a card whose SMU declines to
    # hand over its DPM tables still executes kernels, it just may not boost. Refusing to build
    # the device over that would be worse than running slow, so a refusal is caught -- and said
    # out loud, because a card silently stuck at boot clocks is its own kind of wrong answer.
    # Only SMUError is caught: that is the SMU answering "no", which is a fact about the card.
    # A timeout still propagates, because that is the SMU not answering at all.
    if (max_power:=getenv("AM_POWER_LIMIT", 0.0)) > 0:
      # A refused power limit must not skip the clocks. They are independent requests, and the
      # card is more use pinned-and-uncapped than capped-and-idle.
      try: self.smu.set_power_limit(max_power)
      except SMUError as e: print(f"am {self.devfmt}: the SMU refused a {max_power:.0f}W power limit: {e}")
      level = None
    else: level = -1 # last level, max perf.
    try: took = self.smu.set_clocks(level=level)
    except SMUError as e:
      took = {}
      print(f"am {self.devfmt}: running at the SMU's default clocks, it refused to set them: {e}")
    # Which domains answered is the whole point: a card that took GFXCLK and refused UCLK performs
    # nothing like one that refused both, and both used to print the same single line.
    #
    # "accepted", not "pinned", and the difference is not pedantry. A Sienna Cichlid whose pptable
    # still has its board section zeroed accepts every SetSoftMin/MaxByFreq and then does not move
    # -- measured at gfxclk 497 of an available 2350 MHz with all four domains reporting success.
    # Claiming the clocks are pinned is how a card silently stuck at boot clocks reads as healthy,
    # which is the exact failure this reporting exists to prevent.
    if (refused:=[k for k,v in took.items() if not v]):
      ok = ", ".join(k for k,v in took.items() if v)
      print(f"am {self.devfmt}: the SMU refused {', '.join(refused)}; accepted {ok or 'nothing'}")
    elif took and DEBUG >= 2: print(f"am {self.devfmt}: clock request accepted for {', '.join(took)}")
    for ip in [self.soc, self.gfx]: ip.set_clockgating_state()
    self.reg("regSCRATCH_REG7").write(AMDev.Version)
    self.reg("regSCRATCH_REG6").write(1) # set initialized state.
    if DEBUG >= 2: print(f"am {self.devfmt}: boot done")

  def init_sw(self, smi_dev=False):
    self.smi_dev, self.is_err_state = smi_dev, False

    # Memory manager & firmware
    self.mm = AMMemoryManager(self, self.vram_size - self.reserved_vram_size, boot_size=(32 << 20), pt_t=AMPageTableEntry, va_shifts=[12, 21, 30, 39],
      va_bits=48, first_lv=am.AMDGPU_VM_PDB2, va_base=AMMemoryManager.va_allocator.base, reserve_ptable=not self.large_bar,
      palloc_ranges=[(1 << (i + 12), (2 << 20) if i >= 9 else 0x1000) for i in range(9 * (3 - am.AMDGPU_VM_PDB2), -1, -1)])
    self.fw = AMFirmware(self)

    # Initialize IP blocks
    self.soc:AM_SOC = AM_SOC(self)
    self.gmc:AM_GMC = AM_GMC(self)
    self.ih:AM_IH = AM_IH(self)
    self.psp:AM_PSP = AM_PSP(self)
    self.smu:AM_SMU = AM_SMU(self)
    self.gfx:AM_GFX = AM_GFX(self)
    self.sdma:AM_SDMA = AM_SDMA(self)

    # Init sw for all IP blocks
    for ip in [self.soc, self.gmc, self.ih, self.psp, self.smu, self.gfx, self.sdma]: ip.init_sw()

  def init_hw(self, *blocks:AM_IP):
    for ip in blocks:
      ip.init_hw()
      if DEBUG >= 2: print(f"am {self.devfmt}: {ip.__class__.__name__} initialized")

  def fini(self):
    if DEBUG >= 2: print(f"am {self.devfmt}: Finalizing")
    for ip in [self.sdma, self.gfx]: ip.fini_hw()
    # Dropping to the lowest clock on the way out is courtesy, not teardown: a card whose SMU
    # would not set clocks on the way in will not set them on the way out either, and an SMUError
    # escaping here surfaces as an "exception ignored in atexit callback" traceback that says
    # nothing about the run that just finished. The rest of fini still has to happen.
    with contextlib.suppress(SMUError): self.smu.set_clocks(level=0)
    self.ih.interrupt_handler()
    self.reg("regSCRATCH_REG6").write(self.is_err_state) # set finalized state.

  def recover(self, force=False) -> bool:
    if not force and not self.is_err_state: return False
    if DEBUG >= 3: print(f"am {self.devfmt}: Start recovery")
    self.ih.interrupt_handler()
    self.gfx.reset_mec()
    self.is_err_state = False
    if DEBUG >= 3: print(f"am {self.devfmt}: Recovery complete")
    return True

  def is_hive(self) -> bool: return self.gmc.xgmi_seg_sz > 0

  def paddr2mc(self, paddr:int) -> int: return self.gmc.mc_base + paddr
  def paddr2xgmi(self, paddr:int) -> int: return self.gmc.paddr_base + paddr
  def xgmi2paddr(self, xgmi_paddr:int) -> int: return xgmi_paddr - self.gmc.paddr_base

  def reg(self, reg:str) -> AMRegister: return self.__dict__[reg]

  def rreg(self, reg:int) -> int:
    val = self.indirect_rreg(reg) if reg >= len(self.mmio) else self.mmio[reg]
    if AM_DEBUG >= 4 and getattr(self, '_prev_rreg', None) != (reg, val): print(f"am {self.devfmt}: Reading register {reg:#x} with value {val:#x}")
    self._prev_rreg = (reg, val)
    return val

  def wreg(self, reg:int, val:int):
    if AM_DEBUG >= 4: print(f"am {self.devfmt}: Writing register {reg:#x} with value {val:#x}")
    if reg >= len(self.mmio): self.indirect_wreg(reg, val)
    else: self.mmio[reg] = val

  def wreg_pair(self, reg_base:str, lo_suffix:str, hi_suffix:str, val:int, inst:int=0):
    self.reg(f"{reg_base}{lo_suffix}").write(lo32(val), inst=inst)
    self.reg(f"{reg_base}{hi_suffix}").write(hi32(val), inst=inst)

  def _rsmu(self, reg:int) -> AMRegister:
    # Not every ASIC has an RSMU window. nbio 2.3 (Navi 2x) has no regBIF_BX_PF0_RSMU_* at all --
    # not merely missing from tinygrad's table, absent from the register set -- so an out-of-
    # aperture access here cannot be served. Say that, instead of surfacing as a bare KeyError
    # from __dict__ several frames away from the register that was actually out of range.
    if "regBIF_BX_PF0_RSMU_INDEX" not in self.__dict__:
      nbio = '.'.join(map(str, self.ip_ver.get(am.NBIO_HWIP, ()))) or "unknown"
      raise RuntimeError(f"register {reg:#x} is outside the {len(self.mmio):#x}-dword MMIO aperture and "
                         f"this ASIC has no RSMU window to reach it through (nbio {nbio})")
    return self.reg("regBIF_BX_PF0_RSMU_INDEX")

  def indirect_rreg(self, reg:int) -> int:
    self._rsmu(reg).write(reg * 4)
    return self.reg("regBIF_BX_PF0_RSMU_DATA").read()

  def indirect_wreg(self, reg:int, val:int):
    self._rsmu(reg).write(reg * 4)
    self.reg("regBIF_BX_PF0_RSMU_DATA").write(val)

  def indirect_wreg_pcie(self, reg:int, val:int, aid:int=0):
    reg_addr = reg * 4 + ((((aid & 0b11) << 32) | (1 << 34)) if aid > 0 else 0)
    self.reg("regBIF_BX0_PCIE_INDEX2").write(lo32(reg_addr))
    if hi32(reg_addr) > 0: self.reg("regBIF_BX0_PCIE_INDEX2_HI").write(hi32(reg_addr) & 0xff)
    self.reg("regBIF_BX0_PCIE_DATA2").write(val)
    if hi32(reg_addr) > 0: self.reg("regBIF_BX0_PCIE_INDEX2_HI").write(0)

  def _read_vram(self, addr, size) -> bytes:
    assert addr % 4 == 0 and size % 4 == 0, f"Invalid address {addr:#x} or size {size:#x}"
    res = []
    for caddr in range(addr, addr + size, 4):
      self.wreg(0x06, caddr >> 31)
      self.wreg(0x00, (caddr & 0x7FFFFFFF) | 0x80000000)
      res.append(self.rreg(0x01))
    return bytes(array.array('I', res))

  def _run_discovery(self):
    # NOTE: Fixed register to query memory size without known ip bases to find the discovery table.
    #       The table is located at the end of VRAM - 64KB and is 10KB in size.
    mmRCC_CONFIG_MEMSIZE = 0xde3
    self.vram_size = self.rreg(mmRCC_CONFIG_MEMSIZE) << 20
    self.large_bar = self.vram.nbytes >= self.vram_size
    tmr_offset, tmr_size = self.vram_size - (64 << 10), (10 << 10)

    disc_tbl = self.vram.view(tmr_offset, tmr_size)[:] if self.large_bar else self._read_vram(tmr_offset, tmr_size)
    self.bhdr = am.struct_binary_header.from_buffer(bytearray(disc_tbl))
    ihdr = am.struct_ip_discovery_header.from_address(ctypes.addressof(self.bhdr) + self.bhdr.table_list[am.IP_DISCOVERY].offset)
    assert self.bhdr.binary_signature == am.BINARY_SIGNATURE and ihdr.signature == am.DISCOVERY_TABLE_SIGNATURE, "discovery signatures mismatch"

    self.regs_offset:dict[int, dict[int, tuple]] = collections.defaultdict(dict)
    self.ip_ver:dict[int, tuple[int, int, int]] = {}

    for num_die in range(ihdr.num_dies):
      dhdr = am.struct_die_header.from_address(ctypes.addressof(self.bhdr) + ihdr.die_info[num_die].die_offset)

      ip_offset = ctypes.addressof(self.bhdr) + ctypes.sizeof(dhdr) + ihdr.die_info[num_die].die_offset
      for _ in range(dhdr.num_ips):
        ip = am.struct_ip_v4.from_address(ip_offset)
        ba = ((ctypes.c_uint64 if ihdr.base_addr_64_bit else ctypes.c_uint32) * ip.num_base_address).from_address(ip_offset + 8)
        for hw_ip in range(1, am.MAX_HWIP):
          if hw_ip in am.hw_id_map and am.hw_id_map[hw_ip] == ip.hw_id:
            self.regs_offset[hw_ip][ip.instance_number] = tuple(list(ba))
            self.ip_ver[hw_ip] = (ip.major, ip.minor, ip.revision)

        ip_offset += 8 + (8 if ihdr.base_addr_64_bit else 4) * ip.num_base_address

    gc_info = am.struct_gc_info_v1_0.from_address(gc_addr:=ctypes.addressof(self.bhdr) + self.bhdr.table_list[am.GC].offset)
    self.gc_info = getattr(am, f"struct_gc_info_v{gc_info.header.version_major}_{gc_info.header.version_minor}").from_address(gc_addr)
    self.reserved_vram_size = (384 << 20) if self.ip_ver[am.GC_HWIP][:2] in {(9,4), (9,5)} else (64 << 20)

  @functools.cached_property
  def hwid_names(self) -> dict[int, str]: return {v:k.removesuffix('_HWID') for k,v in vars(am).items() if k.endswith('_HWID') and isinstance(v, int)}

  def _ip_module(self, prefix:str, hwip): return import_module(prefix, self.ip_ver[hwip])

  def _build_regs(self):
    mods = [("mp", am.MP0_HWIP), ("hdp", am.HDP_HWIP), ("gc", am.GC_HWIP), ("mmhub", am.MMHUB_HWIP), ("osssys", am.OSSSYS_HWIP),
      ("nbio" if self.ip_ver[am.GC_HWIP] < (12,0,0) else "nbif", am.NBIO_HWIP)]
    if self.ip_ver[am.SDMA0_HWIP] in {(4,4,2), (4,4,4)}: mods += [("sdma", am.SDMA0_HWIP)]

    for prefix, hwip in mods:
      self.__dict__.update(import_asic_regs(prefix, self.ip_ver[hwip], cls=functools.partial(AMRegister, adev=self, bases=self.regs_offset[hwip])))
    self.__dict__.update(import_asic_regs('mp', (11, 0, 0), cls=functools.partial(AMRegister, adev=self, bases=self.regs_offset[am.MP1_HWIP])))
