import math, time, json, re, multiprocessing, traceback, signal, atexit
from dataclasses import replace
from tinygrad.uop.ops import sym_infer, AxisType, UOp, Ops
from tinygrad.uop.render import pyrender
from tinygrad.device import Device, Buffer
from tinygrad.helpers import prod, flatten, DEBUG, CACHELEVEL, diskcache_get, diskcache_put, getenv, Context, colored, time_to_str
from tinygrad.helpers import IGNORE_BEAM_CACHE
from tinygrad.codegen.opt import Opt, OptOps, KernelOptError
from tinygrad.engine.realize import time_call
from tinygrad.codegen import to_program
from tinygrad.codegen.opt.postrange import Scheduler

actions = [Opt(op=OptOps.UPCAST, axis=axis, arg=amt) for amt in [0,2,3,4,5,7] for axis in range(8)]
actions += [Opt(op=OptOps.UNROLL, axis=axis, arg=amt) for amt in [0,4,7] for axis in range(5)]
actions += [Opt(op=OptOps.LOCAL, axis=axis, arg=amt) for amt in [2,3,4,8,13,16,29] for axis in range(6)]
actions += [Opt(op=OptOps.GROUPTOP, axis=axis, arg=amt) for amt in [13,16,28,29,32,49,64,256] for axis in range(3)]
actions += [Opt(op=OptOps.GROUP, axis=axis, arg=amt) for amt in [0,4,8,16] for axis in range(3)]
if getenv("BEAM_PADTO", 0): actions += [Opt(op=OptOps.PADTO, axis=axis, arg=amt) for amt in [32] for axis in range(7)]
actions += [Opt(op=OptOps.LOCAL, axis=0, arg=32), Opt(op=OptOps.LOCAL, axis=6, arg=2)]
actions += [Opt(op=OptOps.TC, axis=0, arg=(-1, 0, getenv("TC", 1)))]
# covers resnet kernels (3 global * 3 reduce)
actions += [Opt(op=OptOps.TC, axis=axis, arg=(-1, getenv("TC_OPT", 2), getenv("TC", 1))) for axis in range(9)]
actions += [Opt(op=OptOps.SWAP, axis=axis_0, arg=axis_1) for axis_0 in range(5) for axis_1 in range(axis_0+1, 5)]
actions += [Opt(op=OptOps.THREAD, axis=axis, arg=amt) for amt in [2,3,4,5,8,12,16,24,32,64] for axis in range(3)]
if getenv("NOLOCALS"): actions += [Opt(op=OptOps.NOLOCALS)]

def get_test_global_size(global_size, max_global_size, var_vals):
  test_global_size = [sym_infer(sz, var_vals) for sz in global_size]
  input_size = prod(test_global_size)
  while prod(test_global_size) > max_global_size:
    for j in range(len(global_size)-1,-1,-1):
      if test_global_size[j] > 16:
        test_global_size[j] //= 2
        break
  return test_global_size, input_size / prod(test_global_size)

def _time_program(prg:UOp, var_vals:dict[str, int], rawbufs:list[Buffer], early_stop:float|None=None,
                  allow_test_size:int=True, max_global_size:int|None=65536, clear_l2=False, cnt=3, name="test", dev_timeout=False) -> list[float]:
  # A device-side deadline below the transport's own round-trip floor times out every candidate,
  # however fast the kernel actually is. Over a USB-attached card one round trip measures 1.5-2.9 ms
  # while early_stop lands near 1 ms for small kernels, so the search dies with
  # "Wait timeout: 1 ms! (the signal is not set to N, but N)" -- naming a value that had arrived.
  # Turning the deadline off instead is worse: a pathological candidate then runs all the way to
  # HCQDEV_WAIT_TIMEOUT_MS and is indistinguishable from a real GPU hang, which on an ASIC whose
  # recover() path is incomplete takes the whole search down. This floor keeps early_stop's pruning
  # while refusing to set a deadline the link cannot physically meet. 0 keeps upstream behaviour.
  timeout = (max(int(early_stop * 1e3), getenv("BEAM_DEV_TIMEOUT_MIN_MS", 0))
             if dev_timeout and early_stop is not None and early_stop < math.inf else None)
  factor = 1
  if allow_test_size and max_global_size is not None:
    global_size, factor = get_test_global_size(prg.arg.global_size, max_global_size, var_vals)
    prg = prg.replace(arg=replace(prg.arg, global_size=tuple(global_size)))
  call = prg.call(*[UOp.from_buffer(b) for b in rawbufs])
  tms = []
  for _ in range(cnt):
    try: tms.append(time_call(call, var_vals, timeout=timeout, clear_l2=clear_l2) * factor)
    except AssertionError: return [math.inf] * cnt
    if early_stop is not None and early_stop < min(tms): break
  return tms

class TimeoutException(Exception): pass
def timeout_handler(signum, frame):
  if DEBUG >= 2: print("*** BEAM COMPILE TIMEOUT")
  raise TimeoutException()

def _try_compile(x:tuple[int,Scheduler]) -> tuple[int, tuple[UOp, float]|None]:
  if hasattr(signal, "alarm"):
    signal.signal(getattr(signal, 'SIGALRM'), timeout_handler)
    # set timeout
    signal.alarm(getenv("BEAM_TIMEOUT_SEC", 10))
  ret = None
  try:
    st = time.perf_counter()
    ast, dev = x[1].copy().get_optimized_ast(name_override="test"), x[1].ren.target.device
    prg = to_program(ast.substitute({p: p.replace(arg=replace(p.arg, device=dev)) for p in ast.toposort() if p.op is Ops.PARAM}), x[1].ren)
    et = time.perf_counter() - st
    uops = prg.src[1].src
    if len(uops) >= (uops_max:=getenv("BEAM_UOPS_MAX", 3000)) > 0:
      if getenv("BEAM_LOG_SURPASS_MAX"): print(f"too many uops. {len(uops)=}, {uops_max=}")
      raise RuntimeError("too many uops")
    ret = (prg, et)
  except RuntimeError:
    if DEBUG >= 4: traceback.print_exc()
  except Exception as e:
    if getenv("BEAM_STRICT_MODE"): raise e
  finally:
    if hasattr(signal, "alarm"): signal.alarm(0)
  return x[0], ret

# workers should not open devices and should ignore ctrl c and should not launch VIZ
def _init_worker():
  Context(ALLOW_DEVICE_USAGE=0, VIZ=0, TRACK_MATCH_STATS=0).__enter__()
  signal.signal(signal.SIGINT, signal.SIG_IGN)

def _ensure_buffer_alloc(bufs:list[Buffer]) -> list[Buffer]: return [buf.ensure_allocated() if buf is not None else buf for buf in bufs]

# *** external API ***

# get dictionary of all possible actions
def get_kernel_actions(s:Scheduler, include_0=True, max_up:int|None=None) -> dict[int, Scheduler]:
  acted, max_up, max_lcl = {0:s} if include_0 else {}, getenv("BEAM_UPCAST_MAX", 256) if max_up is None else max_up, getenv("BEAM_LOCAL_MAX", 1024)
  kernel_actions = actions.copy()

  for i,a in enumerate(kernel_actions):
    if a.axis is not None and a.op is not OptOps.TC:
      try: ax = s.real_axis(a.op, a.axis)
      except KernelOptError: continue
      if (ax >= s.shape_len) or (s.full_shape[ax] == a.arg and Opt(a.op, a.axis, 0) in kernel_actions): continue
    s2 = s.copy()
    try:
      s2.apply_opt(a)
      up, lcl, tc_up = 1, 1, prod(tc.dims)//tc.threads if hasattr(s2, 'tensor_core') and (tc:=s2.tensor_core) else 1
      for x,t in zip(s2.full_shape, s2.axis_types):
        if t in (AxisType.UPCAST, AxisType.UNROLL): up *= x
        elif t in (AxisType.WARP, AxisType.LOCAL, AxisType.GROUP_REDUCE): lcl *= x
      if up//tc_up > max_up or lcl > max_lcl:
        if getenv("BEAM_LOG_SURPASS_MAX"): print(f"too many upcast/local. {up//tc_up=}, {max_up=}, {lcl=}, {max_lcl=}")
        continue
      acted[i+1] = s2
    except KernelOptError: pass
  return acted

# ***** kernel audit *****

# beam_search_22 is keyed on an opaque 32-byte ast.key hash, and the compile cache is keyed on IR
# text. Neither table records which kernel a row belongs to, so a bad schedule is undiagnosable:
# you can see from the compiled ELF that some kernel launched one work-item per workgroup, and
# there is no way to find the cache row that decided that, or to tell a kernel that searched badly
# from one that never searched at all.
#
# KERNEL_AUDIT=<path> writes the missing join: one JSON line per compiled kernel with its name, the
# beam key it looked up, whether that key hit the cache, the opts that came back, and the
# local_size those opts actually produced. `beam: null` means the kernel never reached beam_search.
# tinygrad colours a kernel name with ANSI codes and keeps them *inside* KernelInfo.name, so
# the name in a DEBUG log or an ELF note does not match a plain grep for it. Strip them here:
# an audit you cannot grep is not an audit.
_ANSI = re.compile("\x1b\\[[0-9;]*m")
_audit_pending: dict|None = None

def _audit_beam(key:dict, opts, cached:bool) -> None:
  global _audit_pending
  if not getenv("KERNEL_AUDIT", ""): return
  ast_key = key["ast"]
  _audit_pending = {"ast_key": ast_key.hex() if isinstance(ast_key, (bytes, bytearray)) else str(ast_key),
                    "device": key["device"], "amt": key["amt"], "cached": cached,
                    "nopts": len(opts), "opts": [str(o) for o in opts]}

def audit_program(prog_info) -> None:
  """Emit one audit line for a compiled kernel. Called from do_to_program, which is the only place
  the kernel's name and its final local_size exist at the same time as the beam result."""
  global _audit_pending
  pending, _audit_pending = _audit_pending, None
  if not (path:=getenv("KERNEL_AUDIT", "")): return
  # BEAM's own candidates are all named "test" (_time_program's default) and there are tens of
  # thousands of them; they are not kernels that ship.
  if prog_info.name == "test": return
  rec = {"name": _ANSI.sub("", prog_info.name), "global_size": list(prog_info.global_size),
         "local_size": None if prog_info.local_size is None else list(prog_info.local_size),
         "threads": None if prog_info.local_size is None else prod(prog_info.local_size), "beam": pending}
  with open(path, "a") as f: f.write(json.dumps(rec) + "\n")

def _never_empty(s, beam_result):
  """Never let an empty opt list stand in for a schedule.

  When every candidate fails to time -- the device hiccuped, or the caps excluded everything, which
  is exactly what `infs from N -> 0 actions` in the BEAM log means -- `beam` is still the
  unoptimised Scheduler it was seeded with, and its applied_opts is []. Caching that is strictly
  worse than caching nothing: [] is a cache HIT forever after, apply_opts takes the `elif beam >= 1`
  branch and so never falls through to hand_coded_optimizations, and the kernel ships with
  local_size (1,1,1) -- one work item per workgroup, 1/32 of a wave32. That is how a single 7x7
  depthwise conv came to own 38% of this model's frame, and a wider-cap search reproduced it twice
  in one run.

  The heuristic is what BEAM's absence should fall back to, so fall back to it here, explicitly, and
  cache and return that instead.
  """
  if beam_result.applied_opts: return beam_result
  from tinygrad.codegen.opt.heuristic import hand_coded_optimizations
  # Same guard apply_opts uses: the heuristic does not handle multiblock kernels.
  if any(u.op is Ops.STAGE for u in s.ast.backward_slice): return beam_result
  # Name the kernel. A silent fallback is how the previous occurrence of this went unnoticed:
  # the log said "infs from 24 -> 0 actions" and nothing said which shape it belonged to.
  if DEBUG >= 1: print(f"BEAM timed no candidate for {s.colored_shape()}; using hand_coded_optimizations")
  return hand_coded_optimizations(s.copy())

beam_pool, BEAM_DEBUG = None, getenv("BEAM_DEBUG")
def beam_search(s:Scheduler, rawbufs:list[Buffer], var_vals:dict[str,int], amt:int, allow_test_size=True, disable_cache=IGNORE_BEAM_CACHE.value):
  global beam_pool
  key = {"ast": s.ast.key, "amt": amt, "allow_test_size": allow_test_size, "device": s.ren.target.device, "suffix": s.ren.suffix}
  if not disable_cache and CACHELEVEL >= 1 and (val:=diskcache_get("beam_search", key)) is not None and len(val):
    ret = s.copy()
    for o in val[len(s.applied_opts):]: ret.apply_opt(o)
    _audit_beam(key, val, True)
    return ret

  beam: list[tuple[Scheduler, float]] = [(s, float("inf"))]
  seen_libs = set()

  default_parallel = multiprocessing.cpu_count() if s.ren.target.device in {"CUDA", "AMD", "NV", "METAL", "HIP"} else 0
  if beam_pool is None and (workers := getenv("PARALLEL", default_parallel)):
    beam_pool = multiprocessing.get_context("spawn").Pool(workers, _init_worker, (), getenv("BEAM_MAX_TASKS_PER_CHILD", 16))
    @atexit.register
    def close_pool(): beam_pool.close()

  min_progress = getenv("BEAM_MIN_PROGRESS", 0.01)/1e6
  if BEAM_DEBUG:
    print("BEAM_SEARCH:")
    print(pyrender(s.ast.replace(arg=None)))
  if DEBUG >= 2: print(f"   0.00s:                from   1 ->   1 actions {s.colored_shape()}")

  try:
    rawbufs = _ensure_buffer_alloc(rawbufs)
    exiting, st = False, time.perf_counter()
    dev = Device[s.ren.target.device]
    while not exiting:
      candidates: list[Scheduler] = flatten([get_kernel_actions(si, include_0=False).values() for si,_ in beam])
      timed: list[tuple[Scheduler, float]] = []
      least_compute_ops = math.inf
      for i, proc in ((map if beam_pool is None else beam_pool.imap_unordered)(_try_compile, enumerate(candidates))):
        if proc is None: continue
        prg, compile_et = proc
        if (lib:=prg.src[3].arg) in seen_libs: continue
        # filter out kernels that use 1000x more compute than the smallest
        estimates = prg.src[0].arg.estimates
        least_compute_ops = min(this_compute_ops:=sym_infer(estimates.ops if estimates is not None else 0, var_vals), least_compute_ops)
        if least_compute_ops*1000 < this_compute_ops:
          if getenv("BEAM_LOG_SURPASS_MAX"): print(f"too much compute. {this_compute_ops} when least is {least_compute_ops}")
          continue
        seen_libs.add(lib)
        try: tms = _time_program(prg, var_vals, rawbufs, early_stop=beam[0][1]*3 if len(beam) else 1.0,
                                 allow_test_size=allow_test_size, clear_l2=hasattr(dev, 'invalidate_caches'),
                                 dev_timeout=getenv("BEAM_DEV_TIMEOUT", 1))
        except Exception as e:
          if BEAM_DEBUG: print(f"BEAM failed for opts: {candidates[i].applied_opts}\n{e}")
          if isinstance(e, RuntimeError): continue
          raise
        timed.append((candidates[i], min(tms)))
        if BEAM_DEBUG > 1:
          print(f"{time.perf_counter() - st:7.2f}s: {i:5d} {len(prg.src[1].src):5d} uops",
                f"{time_to_str(compile_et, w=12)} compile/{time_to_str(timed[-1][1], w=12)} run",
                f"      {len(timed):4d}/{len(candidates):4d}         {timed[-1][0].colored_shape()}")
        elif DEBUG >= 2:
          print(f"\r{time.perf_counter() - st:7.2f}s: {time_to_str(timed[-1][1], w=12)}",
                f"      {len(timed):4d}/{len(candidates):4d}         {timed[-1][0].colored_shape()}\033[K", end="")

      # done
      opts = sorted(timed, key=lambda x: x[1])
      exiting = len(opts) == 0 or (opts[0][1] < min_progress) or (len(beam) > 0 and ((beam[0][1]-opts[0][1]) < min_progress))
      if not exiting: beam = opts[:amt]
      elif len(opts) > 0 and opts[0][1] < beam[0][1]: beam = opts[:1]
      if DEBUG >= 2:
        print(f"\r{time.perf_counter() - st:7.2f}s:", colored(time_to_str(beam[0][1], w=12), "green" if exiting else None),
              f"from {len(candidates):3d} -> {len(opts):3d} actions\033[K", beam[0][0].colored_shape())
  except KeyboardInterrupt as e:
    if beam_pool is not None: beam_pool.terminate()
    raise e
  except Exception:
    # Reaching here means the device died, not that a candidate was bad -- the per-candidate
    # handler above already swallows RuntimeError and moves on. On an ASIC whose recover() cannot
    # actually recover (Navi 23 raises KeyError: 'regBIF_BX_PF0_RSMU_INDEX' out of the indirect
    # register path, because amdev.rreg falls back to an RSMU window this part does not have) a
    # single hung candidate ends the whole compile. Nothing is cached for this kernel, so the next
    # attempt reaches the same kernel and hangs on it again: the search never advances past it,
    # however many times it is restarted.
    #
    # Cache the best schedule found so far -- the un-searched baseline if nothing timed -- so a
    # restart skips this kernel and the remaining ones still get tuned. Then let the error
    # propagate: the device really is unusable now, and carrying on would time kernels against a
    # dead card and cache the garbage.
    beam = [(_never_empty(s, beam[0][0]), beam[0][1])]
    if CACHELEVEL >= 1: diskcache_put("beam_search", key, beam[0][0].applied_opts)
    _audit_beam(key, beam[0][0].applied_opts, False)
    raise

  beam = [(_never_empty(s, beam[0][0]), beam[0][1])]
  if CACHELEVEL >= 1: diskcache_put("beam_search", key, beam[0][0].applied_opts)
  _audit_beam(key, beam[0][0].applied_opts, False)
  if BEAM_DEBUG: print(f"BEAM_SEARCH: final tm={time_to_str(beam[0][1], w=0)}, applied_opts={beam[0][0].applied_opts}")
  return beam[0][0]
