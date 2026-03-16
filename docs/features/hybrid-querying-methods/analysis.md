# Hybrid Querying Methods

**TODO #2** — Evaluate and test alternative hybrid retrieval fusion strategies beyond the current Relative Score Fusion (RSF).

---

## Current Setup

| Parameter | Value |
|---|---|
| Fusion strategy | Relative Score Fusion (RSF), fixed in Qdrant |
| Alpha | `HYBRID_ALPHA = 0.5` (50% dense, 50% sparse) |
| Dense model | `jinaai/jina-embeddings-v2-base-code` |
| Sparse model | `Qdrant/bm25` |
| Post-retrieval reranking | Yes — `shared/reranker.py` with over-fetch (5x) for overview queries |

Testing confirmed that `alpha = 0.7` (more dense weight) caused regressions — overview queries lost results because dense embeddings for large summary chunks are inherently weaker than BM25 keyword hits. The 50/50 balance is load-bearing.

---

## Fusion Strategies Under Consideration

### 1. RRF — Reciprocal Rank Fusion

**How it works:** Instead of combining raw scores, RRF combines the *ranks* of results from each retrieval source:

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

where `k` is a smoothing constant (typically 60) and `rank_i(d)` is the rank of document `d` in retrieval source `i`.

**Advantages over RSF:**
- Rank-based — immune to score scale differences between dense and sparse models
- No alpha tuning required; the `k` parameter is much less sensitive
- Qdrant supports RRF natively via `fusion=models.Fusion.RRF` in the prefetch API

**Disadvantages:**
- Loses score magnitude information — a document that scores 0.95 dense and 0.95 sparse gets the same weight as one that scores 0.51 and 0.51
- Can promote mediocre-but-consistent results over excellent single-source results

**Implementation effort:** Very low — a single parameter change in `src/rag_mcp.py` and `query_test_index.py`.

---

### 2. Weighted Score Fusion (current — alpha tuning)

**How it works:** Linear combination of normalized dense and sparse scores:

```
score = alpha * dense_score + (1 - alpha) * sparse_score
```

**Current state:** Already implemented with `HYBRID_ALPHA = 0.5`. Testing showed 0.7 regresses. This is the baseline.

**Remaining work:** Could test values in the 0.4–0.6 range more systematically using `validate_rag.py`.

---

### 3. Cascading + Rerank

**How it works:**
1. Retrieve a large candidate set using a fast/cheap retriever (e.g., BM25 sparse only, or a small dense model)
2. Rerank the candidates with a more expensive model (cross-encoder, or the full dense model)

**Current approximation:** `shared/reranker.py` already implements a partial version: for overview queries, it over-fetches 5x candidates and reranks by adjusting scores based on `node_type` and target identifier matching.

**Full implementation:** Would require a cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2` or `BAAI/bge-reranker-v2-m3`). Cross-encoders take (query, document) pairs as input and produce a relevance score — significantly more accurate than bi-encoder similarity but O(n) inference cost per candidate.

**Effort:** Medium. Requires loading a second model and integrating it into the retrieval pipeline.

---

### 4. Late Interaction — ColBERT

**How it works:** Instead of a single embedding vector per document, ColBERT stores one vector *per token* in the document. At query time, each query token attends to all document tokens via a MaxSim operation:

```
score(q, d) = Σ_{i∈query} max_{j∈doc} (q_i · d_j)
```

**Why it's better:** Captures fine-grained token-level interactions that single-vector embeddings miss. Especially useful for code where a single identifier in the query must match a specific token in the document.

**Requirements:**
- `BAAI/bge-m3` supports ColBERT output natively (alongside dense and sparse — all three from one model)
- Qdrant supports multi-vector collections (each point stores a list of vectors)
- Storage cost: ~30–100x more vectors per document compared to single-vector

**Effort:** High. Requires:
1. Switching to BGE-M3 (see TODO #1)
2. Re-indexing all documents with multi-vector storage
3. Updating the Qdrant collection schema (multi-vector field)
4. Updating the query path to use Qdrant's multi-vector search API

---

## Recommendation & Priority

| Strategy | Effort | Expected Gain | Try First? |
|---|---|---|---|
| RRF | Very low | Medium — more robust than RSF | Yes |
| Alpha sweep (0.4–0.6) | Very low | Low — narrow band already tested | Yes, quick |
| Cascading + cross-encoder rerank | Medium | High for precision queries | After RRF |
| ColBERT (BGE-M3) | High | High for token-level matching | After TODO #1 BGE-M3 migration |

**Suggested order:**
1. Run `validate_rag.py` as baseline
2. Switch `fusion=RRF` in the Qdrant query call, re-run validation
3. Compare scores — commit RRF if it improves or matches, revert if it degresses
4. Revisit ColBERT if/when BGE-M3 is adopted for TODO #1

---

## Implementation Notes

- Qdrant hybrid query with RRF: replace `models.FusionQuery(fusion=models.Fusion.RELATIVE_SCORE_FUSION)` with `models.FusionQuery(fusion=models.Fusion.RRF)` in `src/rag_mcp.py`
- `HYBRID_ALPHA` becomes irrelevant under RRF (RRF has no alpha parameter)
- The `validate_rag.py` harness is already set up to measure PASS/PARTIAL/FAIL across 44 queries — ideal for A/B testing fusion strategies
- Cross-encoder models can be loaded via `sentence-transformers` and integrated as a post-retrieval step in `shared/reranker.py`

---

## Related TODOs
- **TODO #1** — BGE-M3 adoption is a prerequisite for ColBERT late interaction
