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

## 6. Full git diff based refresh calculate regardless on which branch repo currently is? This has to include somehow getting main branch context through git? Is it possible and feasible?
## 7. Other codebases indices, implement chunking of other filetypes, index other codebases, tweak embedding settings for it, validation tests for it etc.
## 8. QDrant own MCP server use? Check it and see how it does with our indices and validation tests.
## 9. Qdrant quantization testing, how it affects RAG quality and other factors (RAM usage, indexing upsert speed?)
## 10. Google TurboQuant implementation for Qdrant in fork? https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
## 11. Structural Metadata & Knowledge Graph for Relational Code Queries
Extract class hierarchies, method call graphs, import dependencies, and cross-domain links
(DFM events -> Pascal methods, Pascal code -> SQL procedures) as structured metadata. Phase 1
adds queryable fields (`parent_class`, `imports`, `calls`) to Qdrant payloads using data the
AST readers already parse but discard. Phase 2 (Neo4j) only if multi-hop traversal is proven
needed. Separately: AI-generated analysis docs about project mechanisms (reporting, data flow)
to be tracked as a distinct item.

[Analysis ->](docs/features/structural-metadata-graph/analysis.md)

## 12. Reranker pluggable rules for specific project config.
