"""Analyze diagnostic data from indexer log, GPU CSV, and RAM CSV."""
import re
from datetime import datetime, timedelta

# Read the log file
with open("diag_indexer.log", "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

# Parse timestamps
def parse_ts(line):
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line.strip())
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
    return None

# ─── DENSE EMBEDDING ANALYSIS ───
print("=" * 80)
print("DENSE EMBEDDING BATCH TIMING ANALYSIS")
print("=" * 80)

dense_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+Embedded (\d+)/(\d+) nodes')
proc_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Processing \((\d+)/12\) (.+)\.\.\.')

# Build file processing timeline
files_dense = {}  # file_name -> [(timestamp, count, total)]
current_file = None
for line in lines:
    pm = proc_pattern.match(line.strip())
    if pm:
        current_file = pm.group(3)
        files_dense[current_file] = []
        continue
    dm = dense_pattern.match(line.strip())
    if dm and current_file:
        ts = datetime.strptime(dm.group(1), "%Y-%m-%d %H:%M:%S")
        count = int(dm.group(2))
        total = int(dm.group(3))
        files_dense[current_file].append((ts, count, total))

# For each file with dense embeddings, compute timing for groups of batches
for fname, entries in files_dense.items():
    if len(entries) < 2:
        continue
    total_nodes = entries[0][2]
    duration = (entries[-1][0] - entries[0][0]).total_seconds()
    
    # Sample: show throughput for first quarter vs last quarter
    n = len(entries)
    q1_end = n // 4
    q3_start = 3 * n // 4
    
    if q1_end < 1 or q3_start >= n - 1:
        print(f"\n{fname} ({total_nodes} nodes, {duration:.0f}s total, {n} batches)")
        print(f"  Too few batches for quartile analysis")
        continue
    
    # First quarter throughput
    q1_dur = (entries[q1_end][0] - entries[0][0]).total_seconds()
    q1_nodes = entries[q1_end][1] - entries[0][1] + 64  # first batch starts at 64
    q1_rate = q1_nodes / q1_dur if q1_dur > 0 else float('inf')
    
    # Last quarter throughput
    q4_dur = (entries[-1][0] - entries[q3_start][0]).total_seconds()
    q4_nodes = entries[-1][1] - entries[q3_start][1]
    q4_rate = q4_nodes / q4_dur if q4_dur > 0 else float('inf')
    
    print(f"\n{fname} ({total_nodes} nodes, {duration:.0f}s, {n} log entries)")
    print(f"  First quarter: {q1_rate:.0f} nodes/sec")
    print(f"  Last  quarter: {q4_rate:.0f} nodes/sec")
    print(f"  Slowdown ratio: {q1_rate/q4_rate:.2f}x" if q4_rate > 0 else "  N/A")
    
    # Show last 10 batch intervals for large files
    if total_nodes > 1000:
        print(f"  Last 10 batch intervals:")
        for i in range(max(0, n-10), n):
            if i > 0:
                dt = (entries[i][0] - entries[i-1][0]).total_seconds()
                print(f"    {entries[i][1]:6d}/{total_nodes} -> {dt:.1f}s")


# ─── SPARSE EMBEDDING ANALYSIS ───
print("\n" + "=" * 80)
print("SPARSE EMBEDDING BATCH TIMING ANALYSIS")
print("=" * 80)

sparse_hdr = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Sparse embedding \((\d+)/12\) (.+)\.\.\.')
sparse_batch = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+Sparse embedded (\d+)/(\d+) nodes')

files_sparse = {}
current_file = None
for line in lines:
    hm = sparse_hdr.match(line.strip())
    if hm:
        current_file = hm.group(3)
        files_sparse[current_file] = []
        continue
    sm = sparse_batch.match(line.strip())
    if sm and current_file:
        ts = datetime.strptime(sm.group(1), "%Y-%m-%d %H:%M:%S")
        count = int(sm.group(2))
        total = int(sm.group(3))
        files_sparse[current_file].append((ts, count, total))

for fname, entries in files_sparse.items():
    if len(entries) < 2:
        total_nodes = entries[0][2] if entries else 0
        print(f"\n{fname} ({total_nodes} nodes) - too few batches")
        continue
    total_nodes = entries[0][2]
    duration = (entries[-1][0] - entries[0][0]).total_seconds()
    n = len(entries)
    
    q1_end = n // 4
    q3_start = 3 * n // 4
    
    if q1_end < 1 or q3_start >= n - 1:
        print(f"\n{fname} ({total_nodes} nodes, {duration:.0f}s total, {n} batches)")
        continue
    
    # First quarter throughput
    q1_dur = (entries[q1_end][0] - entries[0][0]).total_seconds()
    q1_nodes = entries[q1_end][1] - entries[0][1] + 32  
    q1_rate = q1_nodes / q1_dur if q1_dur > 0 else float('inf')
    
    # Last quarter throughput
    q4_dur = (entries[-1][0] - entries[q3_start][0]).total_seconds()
    q4_nodes = entries[-1][1] - entries[q3_start][1]
    q4_rate = q4_nodes / q4_dur if q4_dur > 0 else float('inf')
    
    print(f"\n{fname} ({total_nodes} nodes, {duration:.0f}s, {n} log entries)")
    print(f"  First quarter: {q1_rate:.0f} nodes/sec")
    print(f"  Last  quarter: {q4_rate:.0f} nodes/sec")
    print(f"  Slowdown ratio: {q1_rate/q4_rate:.2f}x" if q4_rate > 0 else "  N/A")
    
    # For the big file, show throughput evolution in detail
    if total_nodes > 1000:
        print(f"\n  Detailed throughput evolution (32-node batches):")
        # Group into windows of ~50 batches
        window = max(20, n // 10)
        for start_idx in range(0, n - window, window):
            end_idx = start_idx + window
            w_dur = (entries[end_idx][0] - entries[start_idx][0]).total_seconds()
            w_nodes = entries[end_idx][1] - entries[start_idx][1]
            w_rate = w_nodes / w_dur if w_dur > 0 else float('inf')
            pct = entries[start_idx][1] * 100 / total_nodes
            print(f"    Nodes {entries[start_idx][1]:6d}-{entries[end_idx][1]:6d} ({pct:5.1f}%): {w_rate:7.0f} nodes/sec  ({w_dur:.1f}s for {w_nodes} nodes)")

# ─── GPU ANALYSIS ───
print("\n" + "=" * 80)
print("GPU VRAM DURING SPARSE EMBEDDING PHASES")
print("=" * 80)

# Sparse phase: 13:34:24 to 13:37:53 (from headers)
sparse_start = datetime(2026, 3, 7, 13, 34, 24)
sparse_end = datetime(2026, 3, 7, 13, 37, 53)

# Dense phase: 13:32:49 to 13:34:23
dense_start = datetime(2026, 3, 7, 13, 32, 49)
dense_end = datetime(2026, 3, 7, 13, 34, 23)

with open("diag_gpu.csv", "r") as f:
    gpu_lines = f.readlines()

print("\nDuring DENSE embedding (13:32:49 - 13:34:23):")
print(f"  {'Timestamp':<24} {'GPU%':>5} {'Mem%':>5} {'VRAM_MB':>8}")
for line in gpu_lines[1:]:  # skip header
    parts = [p.strip() for p in line.strip().split(',')]
    if len(parts) < 6:
        continue
    ts = datetime.strptime(parts[0].strip(), "%Y/%m/%d %H:%M:%S.%f")
    if dense_start <= ts <= dense_end:
        print(f"  {parts[0]:<24} {parts[1]:>5} {parts[2]:>5} {parts[3]:>8}")

print(f"\nDuring SPARSE embedding (13:34:24 - 13:37:53):")
print(f"  {'Timestamp':<24} {'GPU%':>5} {'Mem%':>5} {'VRAM_MB':>8}")
sparse_vram_values = []
for line in gpu_lines[1:]:
    parts = [p.strip() for p in line.strip().split(',')]
    if len(parts) < 6:
        continue
    ts = datetime.strptime(parts[0].strip(), "%Y/%m/%d %H:%M:%S.%f")
    if sparse_start <= ts <= sparse_end:
        print(f"  {parts[0]:<24} {parts[1]:>5} {parts[2]:>5} {parts[3]:>8}")
        sparse_vram_values.append(int(parts[3]))

if sparse_vram_values:
    print(f"\n  VRAM during sparse: min={min(sparse_vram_values)} MB, max={max(sparse_vram_values)} MB, avg={sum(sparse_vram_values)/len(sparse_vram_values):.0f} MB")

# File-1 sparse: 13:34:24 - 13:36:44
# File-2 sparse: 13:36:48 - 13:37:25
f1_sparse_start = datetime(2026, 3, 7, 13, 34, 24)
f1_sparse_end = datetime(2026, 3, 7, 13, 36, 44)

print(f"\n  VRAM during emar.base.classes.pas sparse (13:34:24 - 13:36:44):")
f1_vrams = []
for line in gpu_lines[1:]:
    parts = [p.strip() for p in line.strip().split(',')]
    if len(parts) < 6:
        continue
    ts = datetime.strptime(parts[0].strip(), "%Y/%m/%d %H:%M:%S.%f")
    if f1_sparse_start <= ts <= f1_sparse_end:
        f1_vrams.append((parts[0], int(parts[3])))

# Show in groups
for t, v in f1_vrams:
    print(f"    {t}: {v} MB")


# ─── RAM ANALYSIS ───
print("\n" + "=" * 80)
print("RAM DURING SPARSE EMBEDDING")
print("=" * 80)

with open("diag_ram.csv", "r") as f:
    ram_lines = f.readlines()

print("  Note: RAM CSV columns appear to be: timestamp, working_set_MB(?), private_memory_MB(?)")
print("  Sample during sparse phase:")
for line in ram_lines:
    parts = [p.strip() for p in line.strip().split(',')]
    if len(parts) < 3:
        continue
    try:
        ts = datetime.strptime(parts[0], "%Y-%m-%d %H:%M")
    except:
        try:
            ts = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        except:
            continue
    if sparse_start <= ts <= sparse_end:
        print(f"    {parts[0]}: working_set={parts[1]} MB, private={parts[2]} MB")

# ─── KEY TIMING COMPARISON ───
print("\n" + "=" * 80)
print("KEY TIMING COMPARISON: DENSE vs SPARSE per file")
print("=" * 80)

# Dense file timings
dense_times = {}
for fname, entries in files_dense.items():
    if entries:
        dense_times[fname] = (entries[-1][0] - entries[0][0]).total_seconds() if len(entries) > 1 else 0
        
sparse_times = {}
for fname, entries in files_sparse.items():
    if entries:
        sparse_times[fname] = (entries[-1][0] - entries[0][0]).total_seconds() if len(entries) > 1 else 0

print(f"\n{'File':<55} {'Nodes':>6} {'Dense(s)':>9} {'Sparse(s)':>10} {'Ratio':>6}")
print("-" * 92)
all_files_ordered = [
    "test_sources/emar.base.classes.pas",
    "test_sources/emar105.classes.pas",
    "test_sources/MainDM.pas",
    "test_sources/MainTurdus.pas",
    "test_sources/Splash.pas",
    "test_sources/MainDM.dfm",
    "test_sources/MainTurdus.dfm",
    "test_sources/Splash.dfm",
    "test_sources/WithFrame_SFTP.dfm",
    "test_sources/dbo.ADMIN_ReportDef_ReliefTicketPayments.sql",
    "test_sources/dbo.SLS_ReliefExport_Bilety_Get.sql",
    "test_sources/Informica.dproj",
]

for fname in all_files_ordered:
    nodes = 0
    if fname in files_dense and files_dense[fname]:
        nodes = files_dense[fname][0][2]
    elif fname in files_sparse and files_sparse[fname]:
        nodes = files_sparse[fname][0][2]
    dt = dense_times.get(fname, 0)
    st = sparse_times.get(fname, 0)
    ratio = st / dt if dt > 0 else float('inf')
    print(f"{fname:<55} {nodes:>6} {dt:>9.1f} {st:>10.1f} {ratio:>6.1f}x")
