import functools, tinygrad.runtime.autogen.am
from dataclasses import dataclass
from tinygrad.helpers import getbits

@dataclass
class AMDReg:
  name:str; offset:int; segment:int; fields:dict[str, tuple[int, int]]; bases:dict[int, tuple[int, ...]] # noqa: E702
  def __post_init__(self): self.addr:dict[int, int] = { inst: bases[self.segment] + self.offset for inst, bases in self.bases.items() }

  def encode(self, **kwargs) -> int: return functools.reduce(int.__or__, (value << self.fields[name][0] for name,value in kwargs.items()), 0)
  def decode(self, val: int) -> dict: return {name:getbits(val, start, end) for name,(start,end) in self.fields.items()}

  def fields_mask(self, *names) -> int:
    return functools.reduce(int.__or__, ((((1 << (self.fields[nm][1]-self.fields[nm][0]+1)) - 1) << self.fields[nm][0]) for nm in names), 0)

@dataclass
class AMDIP:
  name:str; version:tuple[int, int, int]; bases:dict[int, tuple[int, ...]] # noqa: E702

  @functools.cached_property
  def regs(self): return import_asic_regs(self.name, self.version, cls=functools.partial(AMDReg, bases=self.bases))

  def __getattr__(self, name:str):
    if name in self.regs: return self.regs[name]
    if (name10:=name.replace('reg', 'mm')) in self.regs: return self.regs[name10]
    raise AttributeError(f"{self.name.upper()} has no register {name}")

# load the greatest module with matching major version that's less than or equal to the target version
# this is not universally correct, see below for an example, but appears reliable for most recent gpus
# https://github.com/torvalds/linux/blob/9207d47f966be9f4d52e7e0119ac2b7a7e366f3e/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c#L3163
def import_module(name:str, target:tuple[int, int, int], submod=""):
  # version overrides. nbio on RDNA2 is the awkward one: discovery reports 3.3.x but AMD's header
  # is nbio_2_3, so not even the major matches and the "same major, <= target" rule below could
  # never find it. Navi 21/22/23/24 all report 3.3.0-3.3.2.
  target = {("smu", (13, 0, 7)): (13, 0, 0),
            ("nbio", (3, 3, 0)): (2, 3, 0), ("nbio", (3, 3, 1)): (2, 3, 0),
            ("nbio", (3, 3, 2)): (2, 3, 0)}.get((name, target), target)
  mod = getattr(tinygrad.runtime.autogen.am, submod) if submod else tinygrad.runtime.autogen.am
  if (children:=[c for c in mod.__all__ if c.startswith(name) and (v:=tuple(map(int, c.split('_')[1:])))[0] == target[0] and v <= target]):
    return getattr(mod, children[-1])
  raise ImportError(f"Failed to import {submod+'.' if submod else ''}{name} {'.'.join(map(str, target))}")

def import_soc(ip): return getattr(tinygrad.runtime.autogen.am, f"soc_{ip[0]}")

def import_pmc(ip) -> dict[str, tuple[str, int]]:
  from tinygrad.runtime.autogen.am import pmc
  # NOTE: precise arch for mi300+, generic for others, since rocm headers lack some archs
  return {k:x for k,v in pmc.counters.items() if (x:=v.get(f"gfx{ip[0]}{ip[1]:x}{ip[2]:x}" if ip[0] == 9 else f"gfx{ip[0]}", None)) is not None}

# gfx10-era AMD headers spell every register mm*; gfx11 and later spell them reg*, and AM is
# written entirely in reg*. AMDev.reg() is a bare __dict__ lookup, so without an alias not one
# register on a Navi 2x card resolves. A few registers moved rather than being re-spelled --
# nbio_2_3 predates the BIF_BX0_/BIF_BX_PF0_ prefixes -- and those need naming outright.
legacy_reg_renames = {"regBIF_BX0_PCIE_INDEX2": "mmPCIE_INDEX2", "regBIF_BX0_PCIE_DATA2": "mmPCIE_DATA2",
                      "regBIF_BX0_BIF_DOORBELL_INT_CNTL": "mmBIF_DOORBELL_INT_CNTL",
                      "regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL": "mmREMAP_HDP_MEM_FLUSH_CNTL"}

def alias_legacy_regs(regs:dict) -> dict:
  # Registers that do not exist on the older silicon are deliberately left absent rather than
  # aliased to something near them, so a code path that is wrong for this generation raises
  # instead of quietly reading an unrelated offset.
  if not any(name.startswith("mm") for name in regs): return regs
  aliased = dict(regs)
  for name, val in regs.items():
    if name.startswith("mm"): aliased.setdefault("reg"+name[2:], val)
  for new, old in legacy_reg_renames.items():
    if old in regs: aliased.setdefault(new, regs[old])
  return aliased

def import_asic_regs(prefix:str, version:tuple[int, int, int], cls=AMDReg) -> dict[str, AMDReg]:
  regs = alias_legacy_regs(import_module(prefix, version, submod="regs"))
  return {reg:cls(name=reg, offset=off, segment=seg, fields=fields) for reg,(off,seg,fields) in regs.items()}
