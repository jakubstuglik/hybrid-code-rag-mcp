"""Compare two Qdrant collections point-by-point (IDs, payloads, dense + sparse vectors).

Usage:
  python tools/verify_collections.py --ref localhost:6340/informica_tei_jinaai \
      --new localhost:6343/informica_jina_gpusat [--min-cos 0.9999] [--json out.json]
Read-only on both collections. Exit code 0 = identical within tolerance.
"""
import argparse, json, sys, time
import numpy as np
from qdrant_client import QdrantClient

def parse(s):
    hp, coll = s.split("/", 1); h, p = hp.split(":"); return QdrantClient(host=h, port=int(p), timeout=300), coll

def all_ids(c, coll):
    ids, off = [], None
    while True:
        pts, off = c.scroll(coll, limit=5000, offset=off, with_payload=False, with_vectors=False)
        ids += [str(p.id) for p in pts]
        if off is None: return ids

def norm_payload(p):
    return json.dumps(p, sort_keys=True, ensure_ascii=False, default=str)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ref", required=True); ap.add_argument("--new", required=True)
    ap.add_argument("--min-cos", type=float, default=0.9999); ap.add_argument("--sparse-tol", type=float, default=1e-4)
    ap.add_argument("--json"); ap.add_argument("--ignore-payload-keys", default="")
    a = ap.parse_args(); t0 = time.time()
    rc, rcoll = parse(a.ref); nc, ncoll = parse(a.new)
    ign = set(k for k in a.ignore_payload_keys.split(",") if k)
    rids, nids = set(all_ids(rc, rcoll)), set(all_ids(nc, ncoll))
    common = sorted(rids & nids)
    rep = {"ref": a.ref, "new": a.new, "ref_count": len(rids), "new_count": len(nids),
           "only_in_ref": len(rids - nids), "only_in_new": len(nids - rids),
           "only_in_ref_sample": sorted(rids - nids)[:10], "only_in_new_sample": sorted(nids - rids)[:10],
           "compared": 0, "payload_mismatch": 0, "payload_mismatch_by_keys": {}, "payload_mismatch_sample": [], "vector_names_mismatch": 0,
           "dense_cos_min": 1.0, "dense_cos_below_threshold": 0, "dense_maxabs_max": 0.0,
           "sparse_index_mismatch": 0, "sparse_value_maxabs": 0.0, "low_cos_sample": []}
    cosines = []
    for i in range(0, len(common), 500):
        batch = common[i:i + 500]
        R = {str(p.id): p for p in rc.retrieve(rcoll, batch, with_payload=True, with_vectors=True)}
        N = {str(p.id): p for p in nc.retrieve(ncoll, batch, with_payload=True, with_vectors=True)}
        for pid in batch:
            r, n = R[pid], N[pid]; rep["compared"] += 1
            rp = {k: v for k, v in (r.payload or {}).items() if k not in ign}
            np_ = {k: v for k, v in (n.payload or {}).items() if k not in ign}
            if norm_payload(rp) != norm_payload(np_):
                rep["payload_mismatch"] += 1
                diff = sorted(k for k in set(rp) | set(np_) if rp.get(k) != np_.get(k))
                kk = ",".join(diff) + " @branch=" + str(rp.get("branch")); rep["payload_mismatch_by_keys"][kk] = rep["payload_mismatch_by_keys"].get(kk, 0) + 1
                if len(rep["payload_mismatch_sample"]) < 5:
                    rep["payload_mismatch_sample"].append({"id": pid, "keys": diff})
            rv, nv = r.vector or {}, n.vector or {}
            if not isinstance(rv, dict): rv = {"": rv}
            if not isinstance(nv, dict): nv = {"": nv}
            if set(rv) != set(nv):
                rep["vector_names_mismatch"] += 1; continue
            for name in rv:
                x, y = rv[name], nv[name]
                if isinstance(x, list):
                    x, y = np.asarray(x, np.float32), np.asarray(y, np.float32)
                    nx, ny = np.linalg.norm(x), np.linalg.norm(y)
                    cos = 1.0 if nx == 0 and ny == 0 else float(x @ y / (nx * ny + 1e-30))
                    cosines.append(cos)
                    rep["dense_maxabs_max"] = max(rep["dense_maxabs_max"], float(np.abs(x - y).max()))
                    if cos < rep["dense_cos_min"]: rep["dense_cos_min"] = cos
                    if cos < a.min_cos:
                        rep["dense_cos_below_threshold"] += 1
                        if len(rep["low_cos_sample"]) < 5: rep["low_cos_sample"].append({"id": pid, "cos": cos})
                else:
                    if list(x.indices) != list(y.indices): rep["sparse_index_mismatch"] += 1
                    else:
                        d = float(np.abs(np.asarray(x.values) - np.asarray(y.values)).max()) if len(x.values) else 0.0
                        rep["sparse_value_maxabs"] = max(rep["sparse_value_maxabs"], d)
        if (i // 500) % 40 == 0: print("  compared %d/%d" % (rep["compared"], len(common)), file=sys.stderr, flush=True)
    if cosines:
        c = np.asarray(cosines); rep["dense_cos_mean"] = float(c.mean()); rep["dense_cos_p001"] = float(np.quantile(c, 0.001))
    rep["seconds"] = round(time.time() - t0, 1)
    ok = (rep["only_in_ref"] == 0 and rep["only_in_new"] == 0 and rep["payload_mismatch"] == 0 and rep["vector_names_mismatch"] == 0
          and rep["dense_cos_below_threshold"] == 0 and rep["sparse_index_mismatch"] == 0 and rep["sparse_value_maxabs"] <= a.sparse_tol)
    rep["VERDICT"] = "IDENTICAL (within tolerance)" if ok else "DIFFERENT"
    out = json.dumps(rep, indent=1); print(out)
    if a.json: open(a.json, "w", encoding="utf-8").write(out)
    sys.exit(0 if ok else 1)

if __name__ == "__main__": main()
