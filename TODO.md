# TODO

## 1. Embedding Model Exploration
Evaluate alternative embedding models for code and document (PDF, DOCX, XLS, TXT) indexing.
Current model (`jinaai/jina-embeddings-v2-base-code`) is code-specialized — how does it perform
on natural language docs, and are there better options?

[Analysis →](docs/features/embedding-model-exploration/analysis.md)

---

## 2. Hybrid Querying Methods
Test alternative retrieval fusion strategies beyond the current Relative Score Fusion (RSF).
Candidates: RRF, weighted score tuning, cascading + cross-encoder rerank, late interaction (ColBERT).

[Analysis →](docs/features/hybrid-querying-methods/analysis.md)

---

## 3. Library Docs Indexing
Index project library documentation at pinned versions (LlamaIndex, Qdrant client, etc.) so AI
agents can answer questions about exact API signatures. Options: scrape docs, clone source at tag,
or leverage community MCP servers.

[Analysis →](docs/features/library-docs-indexing/analysis.md)

---

## 4. Additional MCP Tool Methods
Add specialized search tools to the MCP server (`search_method_decl`, `search_method_def`,
`search_class`, `search_sql`, `search_form`, `search_uses`) with well-written descriptions
so AI agents know which tool to use when.

[Analysis →](docs/features/mcp-additional-tools/analysis.md)

---

## 5. Model Tracking in Qdrant Collections
Store which dense and sparse models were used to build each collection. Auto-detect at index
and query time to prevent silent vector space mismatches when switching models.

[Analysis →](docs/features/model-tracking/analysis.md)

---

## ~~6. indexing with flag --log-to-file - flush this regularly to disk, now it is rare~~ ✓ Done: `configure_tee()` now opens log file with `buffering=1` (line-buffered).
## ~~7. Write down a fine tuning indexing parameters skill. Params like embed batch size, batch max token, max seq length with GPU VRAM and shred VRAM monitoring on test_sources collection for a given model~~ ✓ Done: `.opencode/skills/tune-embed-params/SKILL.md` created.
## ~~8. Clear VRAM (CUDA) cache at the end of indexing, now it leaves some memory used.~~ ✓ Done: `cuda_clear_cache()` added to `finally` block in `src/index_rag.py`.
## 9. Generate bitchy test files for test_sources and change validation rag to use them
## ~~10. Add TEI (Text Embedding Inference) with Quantization embedding mechanism. Test more models with higher parameters count.~~ ✓ Done: TEI integration complete with auto-managed Docker containers, provenance tracking, and multi-model benchmark. See `docs/benchmark-tei-multimodel-2026-03-20.md`.
## 11. TEI performance - GPU not saturated. More text on batch - don't do it by file, collect chunks from multiple files to match specific batch size. Calculate chunks histogram for codebase to set seq_len according to it.
Group chunks for batches based on similar size to bring TEI padding to minimum.
## ~~12. Still no branch in [branch] when indexing. On the changes list I think only develop... Add cpu-stats gathering in CSV during indexing~~ ✓ Done: Branch label `[branch]` shown in all indexing progress messages. CPU/RAM stats added to `gpu_stats.py` CSV via `psutil`.
## ~~13. Single pass embedding - should be default with BM25 sparse. Test if it still works.~~ ✓ Done: `HYBRID_EMBED_SINGLE_PASS = True` is now the default. With TEI, dense goes through Docker — no VRAM contention.
