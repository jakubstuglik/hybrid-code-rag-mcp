"""Sample GPU power/utilization via NVML (ctypes, no deps) to CSV.

Usage: python tools/gpu_trace.py OUT.csv [--interval 0.1] [--gpu 0] [--duration S]
       python tools/gpu_trace.py --summary OUT.csv [--start ISO] [--end ISO]
Columns: t (unix s), gpu, power_w, util_gpu, util_mem, mem_used_mib, sm_clock
"""
import argparse, ctypes, csv, sys, time, statistics, os

class _Util(ctypes.Structure):
    _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]
class _Mem(ctypes.Structure):
    _fields_ = [("total", ctypes.c_ulonglong), ("free", ctypes.c_ulonglong), ("used", ctypes.c_ulonglong)]

def _lib():
    for p in ("nvml.dll", r"C:\Windows\System32\nvml.dll", "libnvidia-ml.so.1"):
        try:
            return ctypes.CDLL(p)
        except OSError:
            pass
    raise SystemExit("NVML not found")

class NVML:
    def __init__(self):
        self.l = _lib()
        self._chk(self.l.nvmlInit_v2())
    def _chk(self, r):
        if r != 0:
            raise RuntimeError("NVML error %d" % r)
    def handle(self, i):
        h = ctypes.c_void_p(); self._chk(self.l.nvmlDeviceGetHandleByIndex_v2(i, ctypes.byref(h))); return h
    def name(self, h):
        b = ctypes.create_string_buffer(96); self._chk(self.l.nvmlDeviceGetName(h, b, 96)); return b.value.decode()
    def power_limit_w(self, h):
        v = ctypes.c_uint(); self._chk(self.l.nvmlDeviceGetEnforcedPowerLimit(h, ctypes.byref(v))); return v.value / 1000
    def sample(self, h):
        p = ctypes.c_uint(); u = _Util(); m = _Mem(); c = ctypes.c_uint()
        self._chk(self.l.nvmlDeviceGetPowerUsage(h, ctypes.byref(p)))
        self._chk(self.l.nvmlDeviceGetUtilizationRates(h, ctypes.byref(u)))
        self._chk(self.l.nvmlDeviceGetMemoryInfo(h, ctypes.byref(m)))
        self.l.nvmlDeviceGetClockInfo(h, 1, ctypes.byref(c))
        return p.value / 1000, u.gpu, u.memory, m.used // (1 << 20), c.value

def record(out, interval, gpu, duration):
    n = NVML(); h = n.handle(gpu)
    print("GPU%d %s power limit %.1f W" % (gpu, n.name(h), n.power_limit_w(h)), flush=True)
    t_end = time.time() + duration if duration else None
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "gpu", "power_w", "util_gpu", "util_mem", "mem_used_mib", "sm_clock", "power_limit_w"])
        lim = n.power_limit_w(h); nxt = time.time()
        while t_end is None or time.time() < t_end:
            w.writerow([round(time.time(), 3), gpu, *n.sample(h), lim]); f.flush()
            nxt += interval; time.sleep(max(0, nxt - time.time()))

def summary(path, start=None, end=None, idle_w=None):
    rows = list(csv.DictReader(open(path)))
    rows = [r for r in rows if (start is None or float(r["t"]) >= start) and (end is None or float(r["t"]) <= end)]
    if not rows:
        return {}
    pw = sorted(float(r["power_w"]) for r in rows); ut = [int(r["util_gpu"]) for r in rows]
    lim = float(rows[0]["power_limit_w"]); q = lambda p: pw[int((len(pw) - 1) * p)]
    res = {"samples": len(rows), "seconds": round(float(rows[-1]["t"]) - float(rows[0]["t"]), 1),
           "power_limit_w": lim, "mean_w": round(statistics.mean(pw), 1), "p10_w": round(q(0.10), 1),
           "p50_w": round(q(0.5), 1), "p90_w": round(q(0.9), 1),
           "pct_time_ge_90pct_tdp": round(100 * sum(p >= 0.9 * lim for p in pw) / len(pw), 1),
           "pct_time_ge_75pct_tdp": round(100 * sum(p >= 0.75 * lim for p in pw) / len(pw), 1),
           "pct_time_lt_40pct_tdp": round(100 * sum(p < 0.4 * lim for p in pw) / len(pw), 1),
           "mean_util": round(statistics.mean(ut), 1),
           "pct_time_util_ge_95": round(100 * sum(u >= 95 for u in ut) / len(ut), 1)}
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--interval", type=float, default=0.1)
    ap.add_argument("--gpu", type=int, default=0); ap.add_argument("--duration", type=float, default=0)
    ap.add_argument("--summary", action="store_true"); ap.add_argument("--start", type=float); ap.add_argument("--end", type=float)
    a = ap.parse_args()
    if a.summary:
        import json; print(json.dumps(summary(a.out, a.start, a.end), indent=1))
    else:
        record(a.out, a.interval, a.gpu, a.duration)
