import ctypes, struct, time, functools, itertools, collections, contextlib, sys
from tinygrad.runtime.autogen import libusb
from tinygrad.helpers import DEBUG, DEV, to_mv, round_up, ceildiv, getenv
from tinygrad.runtime.support.hcq import MMIOInterface
from tinygrad.runtime.support import c

def alloc_cbuffer(sz:int) -> tuple[ctypes.Array, memoryview]: return (buf:=(ctypes.c_ubyte * sz)()), to_mv(ctypes.addressof(buf), sz)
def checked(fn, msg=None):
  @functools.wraps(fn)
  def wrapper(*args):
    if (rc:=fn(*args)) < 0: raise RuntimeError(f"{msg or fn.__name__}: {ctypes.string_at(libusb.libusb_strerror(rc)).decode()}")
    return rc
  return wrapper

class USB3:
  @staticmethod
  @functools.cache
  def ctx():
    ctx = c.init_c_var(ctypes.POINTER(libusb.struct_libusb_context), checked(libusb.libusb_init))
    if DEBUG >= 6: checked(libusb.libusb_set_option)(ctx, libusb.LIBUSB_OPTION_LOG_LEVEL, 4)
    return ctx

  @classmethod
  @functools.cache
  def list_devices(cls, vendor:int, dev:int) -> list[tuple[c.POINTER[libusb.struct_libusb_device], str]]:
    ret = []
    for i in range(checked(libusb.libusb_get_device_list)(cls.ctx(), devs:=ctypes.POINTER(ctypes.POINTER(libusb.struct_libusb_device))())):
      desc = c.init_c_var(libusb.struct_libusb_device_descriptor, lambda x: checked(libusb.libusb_get_device_descriptor)(devs[i], x))
      if (desc.idVendor, desc.idProduct) == (vendor, dev):
        ret.append((libusb.libusb_ref_device(devs[i]), f"usb:{libusb.libusb_get_bus_number(devs[i])}-{libusb.libusb_get_device_address(devs[i])}"))
    libusb.libusb_free_device_list(devs, 1)
    return ret

  def __init__(self, dev:c.POINTER[libusb.struct_libusb_device], *args, **kwargs):
    self._tags, self._transferred = itertools.count(1), ctypes.c_int(0)
    self._bulk_buf, self._bulk_mv = alloc_cbuffer(4 << 20)
    self._ctrl_buf, self._ctrl_mv = alloc_cbuffer(0x1000)

    self.handle = c.init_c_var(c.POINTER[libusb.struct_libusb_device_handle], lambda x: checked(libusb.libusb_open)(dev, x))

    # Read product string descriptor
    _buf = (ctypes.c_ubyte * 256)()
    _desc = libusb.struct_libusb_device_descriptor()
    checked(libusb.libusb_get_device_descriptor)(libusb.libusb_get_device(self.handle), ctypes.byref(_desc))
    _ret = checked(libusb.libusb_get_string_descriptor_ascii)(self.handle, _desc.iProduct, _buf, 256)
    self.product = bytes(_buf[:_ret]).decode("ascii", errors="replace")
    assert self.product.startswith("custom") or self.product.startswith("AS2462")

    # Detach kernel driver if needed
    if checked(libusb.libusb_kernel_driver_active)(self.handle, 0):
      checked(libusb.libusb_detach_kernel_driver)(self.handle, 0)
      checked(libusb.libusb_reset_device)(self.handle)

    # Set configuration and claim interface
    checked(libusb.libusb_set_configuration)(self.handle, 1)
    checked(libusb.libusb_claim_interface)(self.handle, 0)
    checked(libusb.libusb_set_interface_alt_setting)(self.handle, 0, 0)

  def control_write(self, request:int, value:int=0, index:int=0, data:bytes=b'', timeout:int=1000):
    assert len(data) <= len(self._ctrl_mv)
    self._ctrl_mv[:len(data)] = data
    assert checked(libusb.libusb_control_transfer)(self.handle, 0x40, request, value, index, self._ctrl_buf, len(data), timeout) == len(data)

  def control_read(self, request:int, length:int, value:int=0, index:int=0, timeout:int=1000) -> memoryview:
    assert length <= len(self._ctrl_mv)
    assert checked(libusb.libusb_control_transfer)(self.handle, 0xC0, request, value, index, self._ctrl_buf, length, timeout) == length
    return self._ctrl_mv[:length]

  def bulk_write(self, payload:bytes, timeout:int=1000):
    if len(payload) > len(self._bulk_mv): self._bulk_buf, self._bulk_mv = alloc_cbuffer(len(payload))
    self._bulk_mv[:len(payload)] = payload
    checked(libusb.libusb_bulk_transfer, "bulk OUT 0x02 failed") \
      (self.handle, 0x02, self._bulk_buf, len(payload), self._transferred, timeout)
    assert self._transferred.value == len(payload), f"bulk OUT short write: {self._transferred.value}/{len(payload)} bytes"

  def bulk_read(self, length:int, timeout:int=1000) -> memoryview:
    if length > len(self._bulk_mv): self._bulk_buf, self._bulk_mv = alloc_cbuffer(length)
    checked(libusb.libusb_bulk_transfer, "bulk IN 0x81 failed")(self.handle, 0x81, self._bulk_buf, length, self._transferred, timeout)
    return self._bulk_mv[:self._transferred.value]

  # NOTE: keep it for flash.py
  def send_batch(self, cdbs:list[bytes], odata:list[bytes|None]|None=None):
    for cdb, data in zip(cdbs, odata or [None] * len(cdbs)):
      self.bulk_write(struct.pack("<IIIBBB16s", 0x43425355, tag:=next(self._tags), len(data) if data is not None else 0, 0, 0, len(cdb), cdb))
      if data is not None: self.bulk_write(data)
      sig, rtag, _, status = struct.unpack("<IIIB", self.bulk_read(13, timeout=2000))
      assert (sig, rtag, status) == (0x53425355, tag, 0)

class CustomASM24Controller:
  def __init__(self, usb:USB3):
    self.usb = usb

    # Custom firmware now boots with PCIe off. Power it on before probing the link.
    ltssm = self.read(0xB450, 1)[0]
    if ltssm != 0x78: self.set_pcie_power(True)
    ltssm = self.read(0xB450, 1)[0]
    if ltssm != 0x78: raise RuntimeError(f"PCIe link not up (LTSSM=0x{ltssm:02X}), custom firmware not ready")

  def set_pcie_power(self, enabled:bool, timeout:int=10000): self.usb.control_write(0xF3, value=int(enabled), timeout=timeout)

  def _f0_out(self, fmt_type:int, byte_en:int, address:int, value:int, mode:int=0):
    self.usb.control_write(0xF0, fmt_type | (byte_en << 8), mode & 0x03, struct.pack('<III', address & 0xFFFFFFFF, address >> 32, value), 5000)

  def _f0_in(self) -> tuple[int, int, int]:
    data = self.usb.control_read(0xF0, 8, timeout=5000)
    return struct.unpack_from('<I', data)[0], (data[4] >> 5) & 0x7, data[7]

  def pcie_request(self, fmt_type:int, address:int, value:int|None=None, size:int=4, cnt:int=10):
    assert size > 0 and size <= 4, f"Invalid size {size}"
    if DEBUG >= 5: print("pcie_request", hex(fmt_type), hex(address), value, size)

    offset = address & 0x3
    byte_en = ((1 << size) - 1) << offset
    self._f0_out(fmt_type, byte_en, address & ~0x3, (value << (8 * offset)) if value is not None else 0)

    # Fast path: memory writes and messages don't return completions.
    if ((fmt_type & 0b11011111) == 0b01000000) or ((fmt_type & 0b10111000) == 0b00110000): return

    # Read TLPs and config writes: read completion via 0xF0 IN. Retry on error/timeout.
    data, cpl_status, ret_status = self._f0_in()
    if ret_status != 0:
      time.sleep(0.001)  # TODO: this sleep is very picky
      if cnt > 0: return self.pcie_request(fmt_type, address, value, size, cnt=cnt-1)
      raise RuntimeError(f"TLP error after retries: ret_status={ret_status}, address={address:#x}")

    if cpl_status:
      status_map = {0b001: f"Unsupported Request: {address:#x}", 0b100: "Completer Abort", 0b010: "Config Retry"}
      raise RuntimeError(f"TLP completion status: {status_map.get(cpl_status, f'Reserved (0b{cpl_status:03b})')}")

    if value is None: return (data >> (8 * offset)) & ((1 << (8 * size)) - 1)

  def pcie_cfg_req(self, byte_addr:int, bus:int=1, dev:int=0, fn:int=0, value:int|None=None, size:int=4):
    assert byte_addr >> 12 == 0 and bus >> 8 == 0 and dev >> 5 == 0 and fn >> 3 == 0
    fmt_type = (0x44 if value is not None else 0x4) | int(bus > 0)
    address = (bus << 24) | (dev << 19) | (fn << 16) | (byte_addr & 0xfff)
    return self.pcie_request(fmt_type, address, value, size)

  def pcie_mem_write(self, address:int, data:bytes):
    """Streaming PCIe memory write via 0xF0 mode 1 + bulk OUT. Data is little-endian dwords on the wire."""
    if not data: return
    assert len(data) % 4 == 0, f"pcie_mem_write requires 4-byte aligned size, got {len(data)}"
    self._f0_out(0x60, 0x0F, address, len(data) // 4, mode=1)
    self.usb.bulk_write(data)

  def pcie_mem_read(self, address:int, nbytes:int) -> memoryview:
    """Streaming PCIe memory read via 0xF0 mode 2 + bulk IN. Returns little-endian bytes."""
    assert nbytes % 4 == 0, f"pcie_mem_read requires 4-byte aligned size, got {nbytes}"
    self._f0_out(0x20, 0x0F, address, nbytes // 4, mode=2)
    return self.usb.bulk_read(nbytes, timeout=30000)

  def read(self, base_addr:int, length:int) -> bytes:
    """Read from chip XDATA via vendor control IN (bRequest=0xE4). wValue=addr, wLength=size."""
    result = b''
    for off in range(0, length, 0xFF):
      chunk = min(0xFF, length - off)
      result += self.usb.control_read(0xE4, chunk, value=base_addr + off)
    return result

  def write(self, base_addr:int, data:bytes):
    """Write to chip XDATA via vendor control OUT (bRequest=0xE5). wValue=addr, wIndex=val."""
    for off, val in enumerate(data): self.usb.control_write(0xE5, value=base_addr + off, index=val)

  def scsi_write(self, buf:bytes):
    """Write to SRAM via 0xF2 vendor command + bulk OUT."""
    buf_padded = buf + b'\x00' * (round_up(len(buf), 512) - len(buf))
    sectors = len(buf_padded) // 512
    num_slots = ceildiv(len(buf_padded), 0x4000)  # 16KB per slot
    windex = (num_slots & 0xFF) << 8
    self.usb.control_write(0xF2, value=sectors, index=windex)
    self.usb.bulk_write(buf_padded)

  def scsi_read_arm(self, size:int):
    windex = (ceildiv(size, 0x4000) & 0xFF) << 8
    self.usb.control_write(0xF2, value=(ceildiv(size, 512) & 0x7FFF) | 0x8000, index=windex)

  def scsi_read(self, size:int) -> memoryview: return self.usb.bulk_read(round_up(size, 512), timeout=10000)[:size]

class USBMMIOInterface(MMIOInterface):
  def __init__(self, usb, addr, size, fmt, pcimem=True): # pylint: disable=super-init-not-called
    self.usb, self.addr, self.nbytes, self.fmt, self.el_sz, self.pcimem = usb, addr, size, fmt, struct.calcsize(fmt), pcimem

  def _off_from_index(self, index):
    if isinstance(index, slice): return ((index.start or 0) * self.el_sz, ((index.stop or len(self))-(index.start or 0)) * self.el_sz)
    return (index * self.el_sz, self.el_sz)

  def __getitem__(self, index):
    off, sz = self._off_from_index(index)
    if self.pcimem:
      assert sz % 4 == 0 and off % 4 == 0, f"pcie_mem_read requires 4-byte aligned access, got off={off}, sz={sz}"
      data = self.usb.pcie_mem_read(self.addr + off, sz)
    else: data = self.usb.scsi_read(sz) if self.addr == 0xf000 else self.usb.read(self.addr + off, sz)
    return int.from_bytes(data, "little") if sz == self.el_sz else data

  def __setitem__(self, index, data):
    off, _ = self._off_from_index(index)
    data = struct.pack(self.fmt, data) if isinstance(data, int) else bytes(data)
    if not self.pcimem: self.usb.scsi_write(data) if self.addr == 0xf000 else self.usb.write(self.addr + off, data)
    else: self.usb.pcie_mem_write(self.addr+off, data)

  def view(self, offset:int=0, size:int|None=None, fmt=None):
    return USBMMIOInterface(self.usb, self.addr+offset, self.nbytes-offset if size is None else size, fmt=fmt or self.fmt, pcimem=self.pcimem)

if DEV.interface.startswith("MOCK"): from test.mockgpu.usb import MockUSB3 as USB3  # type: ignore  # noqa: F811

# ***** USB transport statistics *****
#
# Every access this GPU's driver makes crosses this file, and over USB a single 64-bit store can
# become eight control transfers. USB_STATS makes that visible. Three layers are counted:
#
#   mmio        USBMMIOInterface item access -- one device memory read/write, as the rest of tinygrad sees it
#   controller  CustomASM24Controller ops    -- the bridge operation that access turned into
#   transport   USB3 libusb transfers        -- the URBs actually on the wire
#
# Only the transport layer's time is wall time on the link; the two outer layers contain it and are
# there to say who asked for it. With USB_STATS=2 every call additionally records the first stack
# frame outside this file, so a hot call site is named by file:line instead of guessed at -- that
# frame walk is not free, so use USB_STATS=1 for headline timings and 2 for attribution.
#
# Nothing is wrapped unless USB_STATS is set, so a normal run keeps the original methods.

USB_STATS = getenv("USB_STATS", 0)
_STATS_FILE = __file__

class USBStats:
  """Process-global USB counters. counters[method] and sites[key] are [calls, payload_bytes, seconds]."""

  LAYERS: dict[str, tuple[str, ...]] = {
    "mmio": ("__getitem__", "__setitem__"),
    "controller": ("pcie_request", "pcie_cfg_req", "pcie_mem_write", "pcie_mem_read", "read", "write",
                   "scsi_write", "scsi_read_arm", "scsi_read"),
    "transport": ("control_write", "control_read", "bulk_write", "bulk_read"),
  }

  counters: dict[str, list] = collections.defaultdict(lambda: [0, 0, 0.0])
  sites: dict[str, list] = collections.defaultdict(lambda: [0, 0, 0.0])
  regions: dict[str, list] = collections.defaultdict(lambda: [0, 0.0, 0.0]) # [entries, wall_s, usb_wall_s]

  @classmethod
  def reset(cls):
    """Drop everything counted so far. Call after warmup so setup traffic is not mixed into a frame."""
    cls.counters.clear()
    cls.sites.clear()
    cls.regions.clear()

  @classmethod
  def transport_secs(cls) -> float: return sum(cls.counters[m][2] for m in cls.LAYERS["transport"])

  @classmethod
  @contextlib.contextmanager
  def region(cls, name:str):
    """Time a caller-defined region together with the USB wall time spent inside it. The difference
    between the two is the region's own host-side time, which is the only way to separate python
    from the link without a profiler that would itself dominate."""
    st, usb_st = time.perf_counter(), cls.transport_secs()
    try: yield
    finally:
      r = cls.regions[name]
      r[0], r[1], r[2] = r[0] + 1, r[1] + (time.perf_counter() - st), r[2] + (cls.transport_secs() - usb_st)

  @classmethod
  def report(cls, per:int=1, top_sites:int=30) -> str:
    """Format the counters, divided by `per` (pass the frame count to get per-frame numbers)."""
    out = [f"--- USB_STATS ({per} frame(s), transport wall {cls.transport_secs()/per*1e3:.3f} ms/frame) ---"]
    for layer, names in cls.LAYERS.items():
      if not (rows:=[(n, *cls.counters[n]) for n in names if cls.counters[n][0]]): continue
      out.append(f"  {layer}:")
      out += [f"    {n:<16}{c/per:12.1f} calls {b/per:12.1f} B {s/per*1e3:10.3f} ms" for n, c, b, s in rows]
    if cls.sites:
      out.append(f"  by call site (top {top_sites} by time):")
      for k, (c, b, s) in sorted(cls.sites.items(), key=lambda kv: -kv[1][2])[:top_sites]:
        out.append(f"    {k:<58}{c/per:12.1f} calls {b/per:12.1f} B {s/per*1e3:10.3f} ms")
    if cls.regions:
      out.append("  regions (wall / usb / host):")
      for k, (n, w, u) in sorted(cls.regions.items(), key=lambda kv: -kv[1][1]):
        out.append(f"    {k:<40}{n/per:8.1f}x {w/per*1e3:9.3f} ms {u/per*1e3:9.3f} ms {(w-u)/per*1e3:9.3f} ms")
    return "\n".join(out)

def _stats_arg(args, kwargs, idx, name, default):
  return kwargs[name] if name in kwargs else (args[idx] if len(args) > idx else default)

def _stats_site() -> str:
  # frame 0 is this function, 1 is the wrapper, 2 is whoever called the wrapped method. Skip on past
  # any frame still inside this file so a transport call is attributed to its tinygrad caller.
  f = sys._getframe(2)
  while f is not None and f.f_code.co_filename == _STATS_FILE: f = f.f_back
  return "?" if f is None else f"{f.f_code.co_filename.rsplit('/', 1)[-1]}:{f.f_lineno}"

def _stats_wrap(cls, name, nbytes):
  fn = getattr(cls, name)
  @functools.wraps(fn)
  def wrapper(self, *args, **kwargs):
    st = time.perf_counter()
    ret = fn(self, *args, **kwargs)
    dt, n = time.perf_counter() - st, nbytes(self, args, kwargs, ret)
    rows = (USBStats.counters[name],) if USB_STATS < 2 else (USBStats.counters[name], USBStats.sites[f"{name} <- {_stats_site()}"])
    for r in rows: r[0], r[1], r[2] = r[0] + 1, r[1] + n, r[2] + dt
    return ret
  setattr(cls, name, wrapper)

def _stats_install():
  # NOTE: USB3 is read from the module globals so the MOCK swap above is honoured.
  for cls, name, nbytes in (
    (USB3, "control_write", lambda s, a, k, r: len(_stats_arg(a, k, 3, "data", b""))),
    (USB3, "control_read", lambda s, a, k, r: _stats_arg(a, k, 1, "length", 0)),
    (USB3, "bulk_write", lambda s, a, k, r: len(_stats_arg(a, k, 0, "payload", b""))),
    (USB3, "bulk_read", lambda s, a, k, r: len(r)),
    (CustomASM24Controller, "pcie_request", lambda s, a, k, r: _stats_arg(a, k, 3, "size", 4)),
    (CustomASM24Controller, "pcie_cfg_req", lambda s, a, k, r: _stats_arg(a, k, 5, "size", 4)),
    (CustomASM24Controller, "pcie_mem_write", lambda s, a, k, r: len(_stats_arg(a, k, 1, "data", b""))),
    (CustomASM24Controller, "pcie_mem_read", lambda s, a, k, r: _stats_arg(a, k, 1, "nbytes", 0)),
    (CustomASM24Controller, "read", lambda s, a, k, r: _stats_arg(a, k, 1, "length", 0)),
    (CustomASM24Controller, "write", lambda s, a, k, r: len(_stats_arg(a, k, 1, "data", b""))),
    (CustomASM24Controller, "scsi_write", lambda s, a, k, r: len(_stats_arg(a, k, 0, "buf", b""))),
    (CustomASM24Controller, "scsi_read_arm", lambda s, a, k, r: 0),
    (CustomASM24Controller, "scsi_read", lambda s, a, k, r: _stats_arg(a, k, 0, "size", 0)),
    (USBMMIOInterface, "__getitem__", lambda s, a, k, r: s._off_from_index(a[0])[1]),
    (USBMMIOInterface, "__setitem__", lambda s, a, k, r: s._off_from_index(a[0])[1]),
  ): _stats_wrap(cls, name, nbytes)

if USB_STATS: _stats_install()
