# Structural Metadata & Knowledge Graph for Code RAG

## Problem Statement

The current RAG system scores 89.1% on validation and handles entity lookups, overviews,
and forward dependencies well. However, it **cannot answer relational queries** about code
structure:

- "Who calls `OpenConnection`?" (reverse call lookup)
- "Full inheritance chain of `TfrmMainTurdus`" (transitive traversal)
- "Which Pascal code calls the SQL procedure `SLS_ReliefExport_Bilety_Get`?" (cross-domain linking)
- "Which classes implement `ITicketValidator`?" (interface discovery)
- "What DFM event handler triggers `btnSaveClick`?" (event wiring)

These queries are **currently impossible** -- not just low-scoring, but structurally
unsupported. Zero of the 108 validation tests cover them because the system has no
mechanism to answer them.

## Current State: What Readers Already Extract (and Discard)

The AST-based readers already parse structural relationships but only embed them as
natural-language text in context prefixes. They are not stored as queryable metadata.

| Reader | Structural Data Extracted | How It's Used Today | What's Discarded |
|--------|--------------------------|--------------------|--------------------|
| **Pascal** | `TFoo = class(TBar)` parent class, uses clauses, class-method ownership | Text in context prefix `// Class: TFoo = class(TBar)` | No `parent_class` field, no `imports` array |
| **Java** | `extends`, `implements`, package, imports, annotations | Text in context prefix, `_get_superclass()`, `_get_interfaces()` called but results only used for text | No `parent_class`, `implements`, `imports` fields |
| **JS/TS** | `extends`, prototype chains, exports | Text in context prefix, `_get_superclass_js()` | No `parent_class` field |
| **Python** | Class bases, imports | Text only | No structured metadata at all |
| **HBM** | Class-to-table, property-to-column, collection associations with `target_class` | Overview chunk text | Richest relational data -- all discarded as metadata |
| **DFM** | Event handler wiring (`OnClick = btnSaveClick`), component hierarchy | Text in chunks | No `event_handler` or `target_method` fields |
| **SQL/T-SQL** | Procedure/function names, parameters | `object_name`, `object_type` stored | No `called_by` or `calls` relationships |

**Key insight:** The expensive work (AST parsing) is already done. Emitting structured
metadata from the existing parse results is low-cost.

## Qdrant Payload Schema: What's Stored vs What's Missing

**Current payload per vector point:**
```
file_path, node_type, start_line, end_line, start_byte, end_byte,
file_datetime, branch, text, unit_name, class_name, package_name,
object_name, object_type, table_name, module_name, report_name,
group_count, split_part, split_total
```

**Missing (would enable relational queries via Qdrant payload filters):**
```
parent_class      -- direct superclass name
implements        -- list of interface names (Java)
imports           -- list of imported units/modules
calls             -- list of method/function names called within this chunk
event_handlers    -- dict of event->method mappings (DFM)
executes_sql      -- SQL object names referenced (cross-domain)
```

## Three-Phase Plan

### Phase 1: Structured Metadata in Qdrant (No Neo4j)

**Effort:** 2-3 days. No new infrastructure.
**Risk:** Minimal -- extends existing reader outputs, uses existing Qdrant payload filters.

#### What to do

1. **Extend reader metadata outputs:**
   - `pascal_reader.py`: Add `parent_class` from `_get_class_info()` (already parsed at line ~400).
     Add `imports` list from `declUses` chunks (already extracted).
   - `java_reader.py`: Add `parent_class` from `_get_superclass()` (line ~300), `implements`
     from `_get_interfaces()`. Add `imports` from `import_group` chunks.
   - `js_reader.py`: Add `parent_class` from `_get_superclass_js()` (line ~500).
   - `python_reader.py`: Add `parent_class` from class base extraction, `imports` list.
   - `dfm_reader.py`: Add `event_handlers` dict from property lines matching `On* = *`.
   - `hbm_reader.py`: Add `mapped_table`, `associations` (target class names from collections).

2. **Add `calls` extraction (new, requires AST walk):**
   - For method/function chunks, walk `call_expression` / `method_invocation` AST nodes
     within the chunk's byte range. Extract called function/method names.
   - This is the only genuinely new parsing work. The others reuse existing parse results.
   - Accuracy: Will capture direct calls visible in the AST. Will NOT capture dynamic
     dispatch, reflection, or string-based SQL execution. Accept this limitation.

3. **Qdrant payload indexing:**
   - Create payload indexes on `parent_class`, `imports`, `calls` fields for efficient filtering.
   - Use Qdrant `MatchAny` / `MatchValue` filters in queries.

4. **MCP query enhancement:**
   - Add filter parameters to `search_rag`: `--calls <name>`, `--inherits <name>`,
     `--imported-by <name>`.
   - Or: detect relational intent in natural language queries (extend reranker patterns)
     and auto-apply filters.

5. **Reranker enhancement:**
   - New intent patterns: "who calls X", "what calls X", "callers of X", "subclasses of X",
     "classes that inherit from X", "implementations of X".
   - When detected: query Qdrant with payload filter on `calls`/`parent_class`/`implements`
     instead of (or in addition to) vector search.

6. **Validation:**
   - Add 10-15 new test cases covering relational queries to both validation YAMLs.
   - Run validation. Measure improvement.

#### What this enables

| Query Type | Mechanism |
|-----------|-----------|
| "Who calls OpenConnection?" | Filter: `calls contains "OpenConnection"` |
| "Subclasses of TDataModule" | Filter: `parent_class == "TDataModule"` |
| "What implements IPaymentProcessor?" | Filter: `implements contains "IPaymentProcessor"` |
| "Files that import MainDM" | Filter: `imports contains "MainDM"` |
| "DFM events wired to btnSaveClick" | Filter: `event_handlers contains "btnSaveClick"` |

#### What this does NOT enable

- **Transitive queries:** "Full inheritance chain from TfrmMainTurdus to TObject" requires
  multi-hop traversal. Qdrant filters are single-hop only.
- **Path queries:** "Trace execution flow from FormCreate to database" requires following
  a chain of `calls` edges across multiple chunks.
- **Aggregation:** "How many classes inherit from TForm?" is awkward with vector search.

#### Decision gate

After Phase 1 validation:
- If single-hop filters answer 80%+ of relational queries agents ask --> **stop here**.
  Phase 1 is sufficient.
- If agents frequently need multi-hop traversal --> proceed to Phase 2.

---

### Phase 2: Neo4j Knowledge Graph (Multi-Hop Queries)

**Effort:** 1-2 weeks. Adds Neo4j Docker container.
**Risk:** Medium -- new infrastructure, sync complexity, branch overlay in two stores.

#### Prerequisites

- Phase 1 must be implemented first (metadata extraction is needed regardless).
- Phase 1 validation must show that multi-hop queries are actually needed.

#### Data model

```cypher
// Nodes
(:File       {path, unit_name, branch, language})
(:Class      {name, fqn, unit_name, file_path, branch, language})
(:Method     {name, fqn, class_name, unit_name, file_path, line_number, branch})
(:Interface  {name, fqn, file_path, branch})
(:SqlObject  {name, type, file_path, branch})
(:DfmForm    {name, root_class, file_path, branch})
(:DfmComponent {name, type, form_name, file_path, branch})

// Relationships
(:Class)-[:INHERITS]->(:Class)
(:Class)-[:IMPLEMENTS]->(:Interface)
(:Class)-[:DEFINED_IN]->(:File)
(:Method)-[:MEMBER_OF]->(:Class)
(:Method)-[:CALLS]->(:Method)
(:File)-[:IMPORTS]->(:File)
(:DfmComponent)-[:HANDLES {event: "OnClick"}]->(:Method)
(:Method)-[:EXECUTES]->(:SqlObject)
(:Class)-[:MAPS_TO {table: "t_payments"}]->(:SqlObject)  // from HBM
```

#### Architecture

- **Docker management:** New `ensure_neo4j_running(cfg)` in `shared/docker_utils.py`,
  analogous to `ensure_qdrant_running()` and `ensure_tei_running()`.
  Container name: `neo4j-{COLLECTION_NAME}`. Bolt port configurable.

- **Graph writer module:** New `shared/graph_writer.py` -- accepts relationship triples
  from readers, batches Cypher MERGE statements, writes to Neo4j during indexing.

- **Dual-write pipeline:** `index_rag.py` sends chunks to Qdrant (vectors) AND triples
  to Neo4j (graph) in the same flush cycle. Both stores share the manifest for
  consistency -- `--clear` clears both.

- **Branch awareness:** Every node and edge gets a `branch` property. Overlay indexing
  adds/removes graph nodes for branch-specific changes. Queries filter by branch.

- **New MCP tool:** `search_graph` for pure-graph queries:
  ```
  search_graph("inheritance chain of TfrmMainTurdus")
  --> Cypher: MATCH p=(c:Class {name:"TfrmMainTurdus"})-[:INHERITS*]->(parent) RETURN p
  ```

- **Graph-augmented vector search:** For hybrid queries, use Neo4j results to build
  Qdrant payload filters:
  ```
  1. Neo4j: MATCH (caller)-[:CALLS]->(m:Method {name:"OpenConnection"}) RETURN caller.file_path
  2. Qdrant: vector search with filter file_path IN [results from step 1]
  3. Return code chunks from callers
  ```

#### Config parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_NEO4J` | `False` | Enable knowledge graph |
| `NEO4J_DOCKER_PORT` | `7687` | Bolt protocol port |
| `NEO4J_HTTP_PORT` | `7474` | Browser/API port |
| `NEO4J_AUTH` | `neo4j/rag-graph` | Default credentials |
| `NEO4J_DOCKER_CONTAINER` | `None` | Container name override (auto-derived) |

---

### Phase 3: Graph-Enhanced Reranking

**Effort:** 3-5 days. Builds on Phase 2.
**Risk:** Low -- additive improvement to existing reranker.

Use graph proximity as a reranking signal in `shared/reranker.py`:

- When query mentions class X, query Neo4j for classes 1-2 hops from X in the
  inheritance graph. Boost chunks from those classes.
- When query mentions method Y, query Neo4j for methods that call or are called by Y.
  Boost chunks containing those methods.
- Graph distance becomes a score adjustment alongside existing overview/detail bonuses.

| Signal | Adjustment | Example |
|--------|-----------|---------|
| Direct relationship (1 hop) | +0.20 | Chunk is from a class that directly inherits from query target |
| Indirect relationship (2 hops) | +0.10 | Chunk is from a grandchild class |
| Same call cluster | +0.15 | Chunk calls or is called by query target method |

---

## AI-Generated Analysis Documents (Second Part of Original Idea)

The original TODO also mentioned generating AI-written analysis documents about
project mechanisms ("How does reporting work in informica_2_0?") and indexing them.

This is **orthogonal to the graph work** and should be tracked separately. Key
considerations:

- These would be "prose" documents generated by an LLM, not code chunks.
- They'd need a different chunking strategy (paragraph-level, not AST-based).
- Staleness is a real risk -- generated docs become wrong as code evolves.
- Could be implemented as a separate `doc_generator.py` that queries the existing RAG,
  synthesizes overview documents, and feeds them back into the index.
- The `library-docs-indexing` feature (TODO item 3) already handles external docs --
  AI-generated docs could reuse that pipeline.

**Recommendation:** Defer this to a separate TODO item. It's valuable but independent
of the structural metadata / graph work.

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Neo4j adds operational complexity | Medium | Phase 1 avoids it entirely. Phase 2 only if proven needed. |
| Call graph extraction is imprecise (dynamic dispatch, reflection) | Low | Partial graph > no graph. Log unresolved calls as warnings. |
| Branch overlay complexity in two stores | Medium | Both stores use same manifest. `--clear` clears both atomically. |
| Index consistency (Qdrant + Neo4j must stay in sync) | Medium | Single pipeline writes both. Never write to one without the other. |
| Performance impact on indexing | Low | Graph writes are <1ms per edge. Negligible vs. embedding cost. |
| AST call extraction may be noisy | Low | Filter to direct calls only. Skip string interpolation and reflection. |

## Recommendation

**Start with Phase 1.** It costs 2-3 days, requires zero new infrastructure, and
leverages AST data the readers already extract but discard. It will immediately answer
whether relational queries are valuable for AI agents.

If Phase 1 shows agents need multi-hop traversal (inheritance chains, call flow tracing),
then Phase 2 (Neo4j) is justified. Without Phase 1 validation data, adding Neo4j is
premature.

## Files That Will Be Modified

| File | Phase | Changes |
|------|-------|---------|
| `src/shared/readers/pascal_reader.py` | 1 | Add `parent_class`, `imports` metadata fields |
| `src/shared/readers/java_reader.py` | 1 | Add `parent_class`, `implements`, `imports` metadata fields |
| `src/shared/readers/js_reader.py` | 1 | Add `parent_class` metadata field |
| `src/shared/readers/python_reader.py` | 1 | Add `parent_class`, `imports` metadata fields |
| `src/shared/readers/dfm_reader.py` | 1 | Add `event_handlers` metadata field |
| `src/shared/readers/hbm_reader.py` | 1 | Add `mapped_table`, `associations` metadata fields |
| `src/shared/reranker.py` | 1 | Add relational intent detection patterns |
| `src/rag_mcp.py` | 1 | Add payload filter parameters to search tool |
| `src/index_rag.py` | 1 | Ensure new metadata fields pass through to Qdrant payload |
| `project-configs/*/validation_tests.yaml` | 1 | Add 10-15 relational test cases per config |
| `src/shared/docker_utils.py` | 2 | Add `ensure_neo4j_running()` |
| `src/shared/graph_writer.py` | 2 | New module: Neo4j batch writer |
| `src/index_rag.py` | 2 | Add dual-write to Neo4j alongside Qdrant |
| `src/rag_mcp.py` | 2 | Add `search_graph` MCP tool |
| `config.py` | 2 | Add `USE_NEO4J`, `NEO4J_*` config parameters |
| `src/shared/reranker.py` | 3 | Add graph-proximity score adjustments |
