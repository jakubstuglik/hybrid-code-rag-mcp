"""Analyze GPU stats from nvidia-smi CSV with phase detection."""
import csv

with open("qdrant/index_bge_m3_20260307_informica_2_0/nvidia_stats_20260307190702.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Parse all data
parsed = []
for r in rows:
    ts = r[0].strip()  # "2026/03/07 19:07:01.234"
    gpu_util = int(r[1].strip())
    vram = int(r[3].strip())
    # Parse timestamp to seconds from midnight
    time_part = ts.split(" ")[1].split(".")[0]
    h, m, s = map(int, time_part.split(":"))
    secs = h * 3600 + m * 60 + s
    parsed.append((secs, gpu_util, vram))

# Detect phases by VRAM pattern
# Phase 1: Loading/warmup (VRAM < 3000)
# Phase 2: Dense embedding (VRAM 3000-6000)
# Phase 3: Sparse embedding (VRAM oscillates 2000-7000)

loading = []
dense = []
sparse = []

for secs, gpu, vram in parsed:
    if vram < 3000:
        loading.append((secs, gpu, vram))
    elif vram < 6000:
        dense.append((secs, gpu, vram))
    else:
        sparse.append((secs, gpu, vram))

# But we know from the log that:
# - Dense started ~19:07
# - Sparse started ~21:01 (secs = 21*3600 + 1*60 = 75660)
# Let me use timestamp boundaries

dense_start = 19 * 3600 + 7 * 60  # 19:07
sparse_start = 21 * 3600 + 1 * 60  # 21:01

dense = [(s, g, v) for s, g, v in parsed if dense_start <= s < sparse_start]
sparse = [(s, g, v) for s, g, v in parsed if s >= sparse_start]

print(f"Total samples: {len(parsed)}")
print(f"Dense samples (~19:07-21:01): {len(dense)} ({len(dense)*2/60:.1f} min)")
print(f"Sparse samples (21:01+): {len(sparse)} ({len(sparse)*2/60:.1f} min)")
print()

def stats(label, phase):
    if not phase:
        print(f"{label}: no data")
        return
    utils = [g for _, g, _ in phase]
    avg = sum(utils) / len(utils)
    idle = sum(1 for u in utils if u <= 5)
    active = sum(1 for u in utils if u > 50)
    saturated = sum(1 for u in utils if u >= 90)
    vram = [v for _, _, v in phase]
    print(f"{label}:")
    print(f"  GPU util: avg={avg:.0f}%  max={max(utils)}%")
    print(f"  Idle (<=5%): {idle}/{len(phase)} = {100*idle/len(phase):.0f}%")
    print(f"  Active (>50%): {active}/{len(phase)} = {100*active/len(phase):.0f}%")
    print(f"  Saturated (>=90%): {saturated}/{len(phase)} = {100*saturated/len(phase):.0f}%")
    print(f"  VRAM: avg={sum(vram)/len(vram):.0f} MiB  peak={max(vram)} MiB")
    print()

stats("DENSE embedding", dense)
stats("SPARSE embedding", sparse)
stats("OVERALL", parsed)
