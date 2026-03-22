# RAG Validation Results - All Configs (2026-03-22)

**Date:** 2026-03-22
**Configs:** `config_informica_tei_jinaai` (78 tests), `config_epodroznik` (30 tests)
**Hybrid Alpha:** 0.5
**Embedding:** jinaai/jina-embeddings-v2-base-code via TEI (GPU)

---

## Overall Summary

| Config | Tests | PASS | PARTIAL | FAIL | Score | Rating |
|--------|------:|-----:|--------:|-----:|------:|--------|
| `config_informica_tei_jinaai` | 78 | 62 | 13 | 3 | 137/156 (87.8%) | Good |
| `config_epodroznik` | 30 | 17 | 7 | 6 | 41/60 (68.3%) | Needs Improvement |
| **Combined** | **108** | **79** | **20** | **9** | **178/216 (82.4%)** | **Good** |

Previous informica score: 89.1% (2026-03-20). Delta: -1.3pp.

---

## Informica Results (87.8% Good)

### Category Summary

| Category | Tests | PASS | PARTIAL | FAIL |
|----------|------:|-----:|--------:|-----:|
| Class Overview Queries | 9 | 5 | 3 | 1 |
| Precise Identifier Search | 10 | 10 | 0 | 0 |
| Cross-File / Dependency | 6 | 6 | 0 | 0 |
| DFM Form Queries | 6 | 6 | 0 | 0 |
| T-SQL Stored Procedures | 6 | 5 | 1 | 0 |
| FR3 Report Queries | 5 | 4 | 1 | 0 |
| DPROJ Project Queries | 4 | 3 | 1 | 0 |
| Code Navigation (Grep-like) | 6 | 4 | 2 | 0 |
| Natural Language Understanding | 5 | 5 | 0 | 0 |
| Edge Cases | 4 | 4 | 0 | 0 |
| Semantic Paraphrase | 4 | 2 | 1 | 1 |
| Hard Identifier + Context | 5 | 2 | 2 | 1 |
| Polish / Domain Language | 4 | 2 | 2 | 0 |
| AI Agent Workflow | 4 | 4 | 0 | 0 |

### FAIL Tests (3)

#### T05 - "What classes are defined in emar105?" - FAIL

| | |
|---|---|
| **Expected** | `class_summary` or `class_overview` from `Emar105Classes.pas` |
| **Got** | #1: `declConst` from `Emar.Emar105Classes.pas` (0.50), #2: `full_file` from architecture doc (0.50) |
| **Root cause** | Class summary chunks exist but not surfacing; `declConst` and doc chunks with BM25 keyword matches ranked higher |

#### T69 - "authentication dialog for entering user credentials" - FAIL

| | |
|---|---|
| **Expected** | `dfm_form_header` or `class_summary` from `LoginFrm.dfm` or `LoginFrm.pas` |
| **Got** | #1-#8: `comment` chunks from various `Globals.pas` files (0.49-0.50) |
| **Root cause** | Dense embedding cannot connect semantic paraphrase "authentication dialog" to `LoginFrm`. No BM25 keyword overlap either. |

#### T76 - "SLS_ReliefExport_Bilety_Get input parameters" - FAIL

| | |
|---|---|
| **Expected** | `procedure_header` from `SLS_ReliefExport_Bilety_Get.sql` |
| **Got** | #1: `declConst` from Pascal file (0.50), no SQL procedure in top-8 |
| **Root cause** | Query adds "input parameters" context that dilutes the exact procedure name match. BM25 for the exact name should dominate but didn't. |

### PARTIAL Tests (13)

| ID | Category | Query | Issue | Position |
|----|----------|-------|-------|----------|
| T01 | Class Overview | "What is TdmMain?" | Overview at #4, needed top-3 | #1: `defProc` MainDM.pas |
| T03 | Class Overview | "TfrmMainTurdus overview" | Overview at #4, needed top-3 | #1: `defProc` MainTurdus.pas |
| T06 | Class Overview | "What does TfrmSplash do?" | Overview at #4, needed top-3 | #1: `defProc` Splash.pas |
| T28 | Code Navigation | "GetCardSerialNumber implementation" | Wrong file variant | #1: `defProc` emarBG_dll (expected emar_dll) |
| T31 | Code Navigation | "SELECT joining TCK_Ticket..." | text match at #3, needed top-2 | #1: `procedure_body` different SQL file |
| T34 | T-SQL Procedures | "TCK_FarePrice parameters" | node_type at #2, needed file match | #1: `declConst` from Pascal file |
| T43 | FR3 Reports | "ListOfPrintOut.fr3 template" | text at #5, needed top-3 | #1: wrong FR3 file |
| T63 | DPROJ Projects | "RELEASE config defines" | Wrong project file | #1: `dproj_build_config` from UpgradeLayouts.dproj |
| T67 | Semantic Paraphrase | "procedure for monthly bus schedule" | node_type at #3 | Semantically related but wrong procedure |
| T74 | Hard Identifier | "REPORT_TYPE_PUNCTUALITY_RIDES value" | Wrong file | #1: `declConst` TURDUS/Globals.pas (expected ResourceStrings.pas) |
| T75 | Hard Identifier | "OpenConnection implementation body" | Wrong file | #1: `defProc` ClientMainDMUtil.pas (expected MainDM.pas) |
| T77 | Polish/Domain | "Bilety ulgowe reduced fare tickets" | text at #2 | Polish terms not well embedded |
| T78 | Polish/Domain | "wydruk raportu drukuj" | text at #2 | Pure Polish query, dense embedding weak |

---

## E-Podroznik Results (68.3% Needs Improvement)

### Category Summary

| Category | Tests | PASS | PARTIAL | FAIL |
|----------|------:|-----:|--------:|-----:|
| Java Class Overview | 5 | 2 | 2 | 1 |
| Java Identifier Search | 5 | 2 | 0 | 3 |
| Hibernate Mapping | 4 | 1 | 3 | 0 |
| JasperReports | 2 | 0 | 2 | 0 |
| Spring Config | 3 | 3 | 0 | 0 |
| Cross-File / Architecture | 3 | 2 | 0 | 1 |
| Multi-Repo | 3 | 3 | 0 | 0 |
| Architecture Docs | 2 | 1 | 0 | 1 |
| Polish / Domain | 3 | 3 | 0 | 0 |

### FAIL Tests (6)

#### T02 - "What does PaymentManager do?" - FAIL

| | |
|---|---|
| **Expected** | `class_overview` or `class_declaration` with text matching `PaymentManager` |
| **Got** | #1: `class_summary` Payment.java (0.71), #2: `class_summary` P24Payment.java (0.68) |
| **Root cause** | No class literally named `PaymentManager` exists. Test criteria assume an identifier that may not exist in the codebase. **Needs test revision.** |

#### T06 - "processPayment" - FAIL

| | |
|---|---|
| **Expected** | Any chunk with text matching `processPayment` |
| **Got** | #1-#8: payment-related method/class chunks but none containing exact text `processPayment` |
| **Root cause** | Identifier `processPayment` may not exist as-is. Related methods use different naming. **Needs test revision** -- verify identifier exists. |

#### T07 - "getConnectionString" - FAIL

| | |
|---|---|
| **Expected** | Any chunk with text matching `getConnectionString` |
| **Got** | #1: `block_comment` PConnection.java (0.53), #2: `field_declaration` PHTiSellConnection.java (0.52) |
| **Root cause** | Identifier `getConnectionString` may not exist. Connection-related code uses different naming. **Needs test revision.** |

#### T09 - "TicketDAO" - FAIL

| | |
|---|---|
| **Expected** | Any chunk with text matching `TicketDAO` |
| **Got** | #1-#8: ticket-related business logic and persistence classes, none named `TicketDAO` |
| **Root cause** | Project uses `PH*` naming for Hibernate entities and `*BO` for business objects, not the `*DAO` pattern. **Needs test revision.** |

#### T20 - "What does Innowatorzy-Common module export?" - FAIL

| | |
|---|---|
| **Expected** | Chunks from `Innowatorzy-Common/` with `interface_declaration` or `class_overview` |
| **Got** | #1-#2: `import_group` chunks from consumer files importing Common classes |
| **Root cause** | Import groups from consuming code have higher BM25 scores for "Innowatorzy-Common" than the actual Common module's interface declarations. The query intent (find exports) isn't matched by the retrieval. |

#### T28 - "Architecture decision records or technical design documents" - FAIL

| | |
|---|---|
| **Expected** | `.md` files containing architecture documentation |
| **Got** | #1-#2: `class_overview` and `method_declaration` from HibernateUtil.java |
| **Root cause** | No architecture documentation files exist in the indexed repos. **Test is invalid** -- remove or replace with a query for something that exists. |

### PARTIAL Tests (7)

| ID | Category | Query | Issue | Position |
|----|----------|-------|-------|----------|
| T01 | Class Overview | "What is TicketService?" | `class_overview` not surfacing; `class_summary` of related classes instead | #5: correct `TicketsService` |
| T04 | Class Overview | "Interfaces in Moneybox" | Interface at #3, needed top-2 | #1-2: method_declaration from MoneyboxBO |
| T12 | Hibernate | "User entity mapping" | User HBM at #7 | Carrier.hbm.xml dominates |
| T13 | Hibernate | "Route entity mapping" | Route HBM at #7 | Carrier/Reservation HBMs dominate |
| T14 | Hibernate | "BusStop entity mapping" | BusStop-related at #3, needed top-2 | Carrier.hbm.xml at #1 |
| T15 | JasperReports | "ticket receipt report" | Related receipt at #1, wrong specific file | Correct node_type, sibling file |
| T16 | JasperReports | "monthly settlement report" | Subreport ranked above parent | #1: subreport variant |

---

## Cross-Cutting Analysis

### Pattern 1: Class Overview Ranking (both indexes)

The single most common issue. `class_overview` and `class_summary` chunks exist but are
outranked by `method_declaration`, `defProc`, or `field_declaration` chunks. The reranker
adds +0.50 to overview types, but method chunks with high BM25 keyword scores (0.50 from
exact name matches) still win.

**Affected tests:** T01, T03, T06 (informica); T01, T04 (epodroznik)

**Potential fix:** Increase overview boost in reranker, or add a penalty for detail chunks
when query intent is clearly "overview" (already partially done, but thresholds may need tuning).

### Pattern 2: Nonexistent Identifiers in E-Podroznik Tests

4 of 6 epodroznik FAILs (T02, T06, T07, T09) likely test for identifiers that don't exist
in the codebase (`PaymentManager`, `processPayment`, `getConnectionString`, `TicketDAO`).
The project uses different naming conventions (`PH*` for Hibernate entities, `*BO` for
business objects, `P*` prefix for project classes).

**Action required:** Verify these identifiers against the actual codebase and revise test
criteria to match real class/method names.

### Pattern 3: HBM Entity Overranking (epodroznik)

`Carrier.hbm.xml` and `ReservationWithDetails.hbm.xml` dominate HBM entity queries,
pushing target entities down. These mappings likely have more properties/associations,
giving them higher BM25 overlap with generic entity-related query terms.

**Affected tests:** T12, T13, T14

**Potential fix:** Add `class_name_pattern` criteria to these tests to require the target
entity name, or tune the reranker to boost HBM chunks matching the query's target entity.

### Pattern 4: Dense Embedding Limitations (informica)

Polish-language queries and semantic paraphrases consistently underperform. The Jina code
model is trained primarily on English code and documentation. Pure Polish queries (T77, T78)
and abstract paraphrases (T69) lack both BM25 keyword overlap and useful dense embeddings.

**This is a fundamental model limitation**, not a configuration issue. Mitigation options:
- Accept lower scores for Polish/paraphrase categories
- Add Polish keywords to chunk context prefixes
- Consider a multilingual embedding model (at the cost of code understanding)

### Pattern 5: File Disambiguation (informica)

When the same identifier exists in multiple files (e.g., `OpenConnection` in MainDM.pas
vs ClientMainDMUtil.pas), the index sometimes returns the wrong variant. The reranker's
target file matching helps but isn't always decisive when multiple files have equal BM25
scores.

**Affected tests:** T28, T74, T75

---

## Action Items

### High Priority (test suite fixes)

1. **Verify epodroznik identifiers** -- Check if `PaymentManager`, `processPayment`,
   `getConnectionString`, `TicketDAO` exist in the actual codebase. Revise T02, T06,
   T07, T09 with correct identifiers.
2. **Remove T28 (architecture docs)** -- No architecture docs exist in the indexed repos.
   Replace with a valid query or remove.
3. **Add `class_name_pattern` to HBM tests** -- T12, T13, T14 should require the target
   entity name to prevent generic HBM entities from satisfying the criteria.

### Medium Priority (reranker tuning)

4. **Increase overview boost for "What is X?" queries** -- Consider raising the primary
   overview bonus from +0.50 to +0.60, or adding a stronger penalty for detail chunks
   in overview-intent queries.
5. **Add overview query detection for Java** -- Verify `is_overview_query()` patterns
   work well for Java class names (no `T` prefix convention like Delphi).

### Low Priority (known limitations)

6. **Polish/domain language** -- Accept reduced scores or investigate multilingual models
   in a future iteration.
7. **Semantic paraphrase** -- T69 "authentication dialog" is a hard case; consider adding
   login/auth keywords to DFM form context prefixes.

---

## Environment

- **Qdrant containers:** informica (port 6340), epodroznik (port 6350), self-index (port 6973)
- **TEI container:** shared (port 8090), GPU, float16
- **Embedding model:** jinaai/jina-embeddings-v2-base-code
- **Index sizes:** informica ~93K vectors, epodroznik ~158K vectors
- **Run time:** ~3 minutes per suite (CPU embedding for queries)
