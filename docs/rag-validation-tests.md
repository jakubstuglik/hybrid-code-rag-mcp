# RAG Validation Test Scenarios

Comprehensive test suite for validating hybrid search quality in the informica-rag system.
Covers Delphi Pascal, T-SQL, and DFM file types across dense (Jina v2 base code), sparse (BM25),
hybrid fusion, and post-retrieval reranking.

## Purpose

This document defines **63 test queries** organized into 10 categories that exercise every
aspect of the RAG retrieval pipeline:

1. **Chunking quality** -- do the readers produce semantically meaningful chunks?
2. **Hybrid search** -- does the 50/50 dense+sparse fusion return the right results?
3. **Reranker** -- does `is_overview_query()` fire correctly and do the score adjustments
   promote the right chunk types?
4. **Cross-file relevance** -- do results come from the correct file, not cross-file interlopers?

## How to Run

### Against the test index (quick iteration)

```bash
# Ensure the test index is built (40 files, ~10K+ chunks)
python index_rag.py --config test

# Run the validation script
python validate_rag.py --config test
python validate_rag.py --config test --alpha 0.5
```

### Against the production index (final validation)

```bash
# Production index (~12,400 files, ~140K chunks)
python validate_rag.py --config production
python validate_rag.py --config production --alpha 0.5
```

### Manual spot-check with query_test_index.py

```bash
python query_test_index.py --alpha 0.5
```

## Scoring System

Each test query is evaluated against its pass criteria and assigned one of three results:

| Result | Definition | Points |
|--------|-----------|--------|
| **PASS** | Most relevant chunk in top 3 results AND has expected `node_type` AND `file_path` matches | 2 |
| **PARTIAL** | Most relevant chunk in top 5 results OR correct file but wrong `node_type` | 1 |
| **FAIL** | Most relevant chunk not in top 8 results or completely wrong file | 0 |

### Overall Score

```
score = (PASS_count * 2 + PARTIAL_count * 1) / (total_tests * 2) * 100%
```

### Thresholds

| Rating | Score | Meaning |
|--------|-------|---------|
| Excellent | >= 90% | Ship it. No regressions. |
| Good | 75-89% | Acceptable. Review PARTIAL results for low-hanging improvements. |
| Needs work | 60-74% | Significant gaps. Check alpha, reranker, or chunking changes. |
| Broken | < 60% | Something is fundamentally wrong. Check embedding model, collection mode. |

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Embedding model | `jinaai/jina-embeddings-v2-base-code` |
| Sparse model | BM25 (Qdrant built-in) |
| `HYBRID_ALPHA` | `0.5` (50% dense, 50% sparse) |
| `desired_top_k` | `8` (default retrieval count) |
| `OVERFETCH_MULTIPLIER` | `5` (for overview queries: fetch 40 candidates) |
| Reranker | `shared/reranker.py` with overview detection + score adjustments |

---

## Category 1: Class Overview Queries

Tests the reranker's ability to detect overview intent and promote `class_overview`,
`class_summary`, and `class_summary_split` chunks to the top positions.

All queries in this category **should** trigger `is_overview_query() == True` and
receive the `OVERFETCH_MULTIPLIER` treatment.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T01 | `What is TdmMain?` | class_summary or class_summary_split from MainDM.pas. Should describe the data module with its published datasets and connections. | `node_type` in {`class_summary`, `class_summary_split`, `class_overview`}, `file_path` contains `MainDM.pas`, position <= 3 | Easy | Reranker: overview detection, primary overview bonus (+0.50), target match (+0.15) |
| T02 | `What classes are in emar105.classes.pas?` | class_summary for TEmar105_OIK or TEmar105_File. Top results should all be from emar105.classes.pas. | `node_type` in {`class_summary`, `class_overview`}, `file_path` contains `emar105`, position <= 2 | Easy | Reranker: "what classes" pattern, file-stem target extraction |
| T03 | `What is TfrmMainTurdus?` | class_overview or class_summary from MainTurdus.pas describing the main application form. | `node_type` in {`class_overview`, `class_summary`, `class_summary_split`}, `file_path` contains `MainTurdus.pas`, position <= 3 | Easy | Reranker: primary overview bonus, T-prefixed class extraction |
| T04 | `Describe TfrmSplash` | class_overview or class_summary from Splash.pas. Small form class. | `node_type` in {`class_overview`, `class_summary`}, `file_path` contains `Splash.pas`, position <= 3 | Easy | Reranker: "describe" pattern triggers overview |
| T05 | `What does TfrmBaseEditor do?` | class_overview or class_summary from BaseEditorForm.pas describing the base editor form. | `node_type` in {`class_overview`, `class_summary`, `class_summary_split`}, `file_path` contains `BaseEditorForm.pas`, position <= 3 | Medium | Reranker: "what does X do" pattern, class name differs from filename |
| T06 | `How does TBasicMainForm work?` | class_overview or class_summary from FormBasicMain.pas. Tests "how does X work" pattern. | `node_type` in {`class_overview`, `class_summary`, `class_summary_split`}, `file_path` contains `FormBasicMain.pas`, position <= 3 | Medium | Reranker: "how does X work" pattern, class-to-file mapping mismatch |
| T07 | `Tell me about TSalesReport` | class_overview or class_summary from SalesReport.Classes.pas. | `node_type` in {`class_overview`, `class_summary`}, `file_path` contains `SalesReport`, position <= 3 | Medium | Reranker: "tell me about" pattern, dotted filename |
| T08 | `Overview of TEmar105_OIK class` | class_overview or class_summary from emar105.classes.pas for the OIK class specifically. | `node_type` in {`class_overview`, `class_summary`}, `file_path` contains `emar105`, `class_name` contains `TEmar105_OIK`, position <= 3 | Medium | Reranker: "overview of" pattern, specific class within multi-class file |
| T09 | `What fields does TdmMain have?` | class_summary or class_summary_split from MainDM.pas showing published field declarations. | `node_type` in {`class_summary`, `class_summary_split`, `declSection`}, `file_path` contains `MainDM.pas`, position <= 3 | Medium | Reranker: "what fields" pattern, large class with many fields |

### Category 1 Notes

- T05 and T06 are **Medium** difficulty because the class name (`TfrmBaseEditor`, `TBasicMainForm`)
  does not directly match the filename (`BaseEditorForm.pas`, `FormBasicMain.pas`). The reranker
  must rely on the `class_name` metadata field for target matching, not just `file_path`.
- T08 tests disambiguation within a multi-class file -- emar105.classes.pas contains multiple
  classes and the result should prefer the one matching `TEmar105_OIK`.

---

## Category 2: Precise Identifier Search

Tests BM25/keyword matching for exact code identifiers. These are **non-overview** queries
that should **NOT** trigger the reranker (`is_overview_query() == False`). Results depend
heavily on BM25 term frequency and the context prefixes embedded in each chunk.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T10 | `REPORT_TYPE_PUNCTUALITY_RIDES` | The constant definition or usage. Should be an exact BM25 keyword hit. | `file_path` contains `.pas`, text content contains `REPORT_TYPE_PUNCTUALITY_RIDES`, position <= 2 | Easy | Sparse/BM25: exact token match, no reranker interference |
| T11 | `PreapreDataSet` | Method implementation (`defProc`) in one of the Pascal units. Note: typo in source code — actual identifier is `PreapreDataSet`, not `PrepareDataSet`. | `node_type` in {`defProc`, `defProc_split`, `method_group`}, text content contains `PreapreDataSet`, position <= 2 | Easy | Sparse/BM25: method name as single token |
| T12 | `OpenConnection` | TdmMain.OpenConnection implementation from MainDM.pas. | `node_type` in {`defProc`, `defProc_split`}, `file_path` contains `MainDM.pas`, text content contains `OpenConnection`, position <= 2 | Easy | Hybrid: BM25 finds name, dense helps disambiguate file |
| T13 | `GetCardSerialNumber` | Method in emar105.classes.pas, likely in a `method_group` chunk (trivial getter). | `node_type` in {`method_group`, `method_group_split`, `defProc`}, `file_path` contains `emar105` or `emar`, position <= 4 | Medium | Sparse/BM25: getter method collapsed into method_group |
| T14 | `SLS_ReliefExport_Bilety_Get` | T-SQL procedure definition from dbo.SLS_ReliefExport_Bilety_Get.sql. | `node_type` in {`procedure_header`, `procedure_full`, `function_header`}, `file_path` contains `SLS_ReliefExport_Bilety_Get`, position <= 3 | Easy | Sparse/BM25: exact procedure name match |
| T15 | `TCK_FarePrice_GetPriceForXDesignation` | T-SQL function definition from dbo.TCK_FarePrice_GetPriceForXDesignation.sql. | `node_type` in {`function_header`, `function_full`, `procedure_header`}, `file_path` contains `TCK_FarePrice`, position <= 2 | Easy | Sparse/BM25: long compound procedure name |
| T16 | `ADMIN_ReportDef_AnalysisRoute` | SQL procedure from ADMIN_ReportDef_AnalysisRoute.sql. | `node_type` in {`procedure_header`, `procedure_full`, `sql_batch`}, `file_path` contains `ADMIN_ReportDef_AnalysisRoute`, position <= 3 | Easy | Sparse/BM25: underscore-separated SQL identifier |
| T17 | `ADMIN_CompanyAllBranches` | SQL procedure from dbo.ADMIN_CompanyAllBranches.sql. | `node_type` in {`procedure_header`, `procedure_full`, `sql_batch`}, `file_path` contains `ADMIN_CompanyAllBranches`, position <= 3 | Easy | Sparse/BM25: exact SQL procedure name |
| T18 | `GetInfoText` | Pascal method, should find implementation in one of the .pas files. | `node_type` in {`defProc`, `defProc_split`, `method_group`}, text content contains `GetInfoText`, position <= 4 | Medium | Sparse/BM25: common getter pattern name |
| T19 | `C_REPORT_` | Constant declarations containing the C_REPORT_ prefix pattern. | `node_type` in {`declConst`, `declConst_split`, `declSection`}, text content matches `C_REPORT_`, position <= 5 | Medium | Sparse/BM25: partial prefix search, BM25 token splitting on underscore |

### Category 2 Notes

- T13 is **Medium** because `GetCardSerialNumber` is a trivial getter that gets merged into
  a `method_group` chunk. The query must match within the group's text, not a standalone chunk.
- T19 is **Medium** because `C_REPORT_` is a prefix pattern -- BM25 may or may not tokenize
  on underscores. The test validates that constant blocks are findable by prefix.

---

## Category 3: Cross-File / Dependency Queries

Tests the ability to find relationships between files: uses clauses, component types,
and inheritance hierarchies.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T20 | `uses clause MainDM` | The `declUses` chunk from MainDM.pas showing interface or implementation uses. | `node_type` == `declUses`, `file_path` contains `MainDM.pas`, position <= 2 | Easy | Hybrid: BM25 matches "uses" + "MainDM", declUses node_type |
| T21 | `what units does MainTurdus use` | The `declUses` chunk from MainTurdus.pas. This IS an overview query ("what units"). | `node_type` == `declUses`, `file_path` contains `MainTurdus.pas`, position <= 3 | Medium | Reranker: overview pattern "what units", declUses gets +0.25 bonus |
| T22 | `TClientDataSet cdsStoredProc` | DFM object or object_group from MainDM.dfm containing cdsStoredProc component declaration. | `file_path` contains `MainDM.dfm` or `MainDM.pas`, text content contains `cdsStoredProc`, position <= 3 | Medium | Hybrid: two-token query, component type + instance name |
| T23 | `classes that inherit from TForm` | Class summaries or overviews that mention `TForm` in their class declaration. Multiple results from different files expected. | text content contains `TForm`, position <= 5, results from >= 2 different files | Hard | Dense: semantic understanding of inheritance concept + BM25 for `TForm` token |
| T24 | `classes that inherit from TDataModule` | Should find TdmMain from MainDM.pas which inherits from TDataModule. | text content contains `TDataModule`, `file_path` contains `MainDM`, position <= 5 | Hard | Dense: semantic "inherit" concept + BM25 for TDataModule |

### Category 3 Notes

- T23 and T24 are **Hard** because they require combining semantic understanding of
  "inherit" with keyword matching for the parent class name. The dense embedding must
  contribute meaningfully here.
- T21 is interesting because "what units does X use" triggers `is_overview_query()` via
  the "what" pattern, and `declUses` is in `_OVERVIEW_CHUNK_TYPES` so it gets the +0.25 bonus.

---

## Category 4: DFM Form Queries

Tests retrieval of DFM (Delphi Form Markup) chunks -- form headers, component objects,
and grouped components.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T25 | `MainTurdus form components` | dfm_form_header from MainTurdus.dfm showing the root form object and its properties. | `node_type` == `dfm_form_header`, `file_path` contains `MainTurdus.dfm`, position <= 2 | Easy | Reranker: "form components" triggers overview, dfm_form_header gets +0.25 |
| T26 | `Splash form layout` | dfm_form_header from Splash.dfm showing the splash screen form definition. | `node_type` in {`dfm_form_header`, `dfm_object`}, `file_path` contains `Splash.dfm`, position <= 3 | Easy | Hybrid: BM25 "Splash" + form context, dense embedding for "layout" concept |
| T27 | `SFTP frame components` | dfm_form_header from WithFrame_SFTP.dfm showing the SFTP frame definition. | `node_type` == `dfm_form_header`, `file_path` contains `WithFrame_SFTP.dfm`, position <= 2 | Easy | Reranker: "frame components" triggers overview |
| T28 | `TActionList in MainTurdus` | dfm_object or dfm_object_group from MainTurdus.dfm containing TActionList components. | `file_path` contains `MainTurdus.dfm`, text content contains `TActionList`, position <= 5 | Medium | Hybrid: specific component type within a large DFM file |

### Category 4 Notes

- T25 and T27 trigger the reranker because "form components" and "frame components" match
  `_OVERVIEW_PATTERNS`. The `dfm_form_header` node_type gets the +0.25 overview bonus.
- T28 is **Medium** because TActionList is a common component type that may appear in
  multiple DFM files. The query must resolve to MainTurdus specifically.

---

## Category 5: SQL Schema / Procedure Queries

Tests retrieval of T-SQL chunks including procedure headers, function bodies, and
table definitions.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T29 | `SLS_Ticket table columns` | Table definition from dbo.SLS_Ticket.sql showing column definitions. | `node_type` in {`create_table`, `sql_batch`}, `file_path` contains `SLS_Ticket`, position <= 3 | Easy | Sparse/BM25: exact table name match |
| T30 | `parameters of ADMIN_ReportDef_ReliefTicketPayments` | procedure_header chunk from dbo.ADMIN_ReportDef_ReliefTicketPayments.sql showing parameter declarations. | `node_type` in {`procedure_header`, `procedure_full`}, `file_path` contains `ADMIN_ReportDef_ReliefTicketPayments`, position <= 3 | Easy | Sparse/BM25: procedure name match, header contains parameters |
| T31 | `body of SLS_ReliefExport_Bilety_Get procedure` | procedure_body chunk(s) from dbo.SLS_ReliefExport_Bilety_Get.sql. | `node_type` in {`procedure_body`, `procedure_full`}, `file_path` contains `SLS_ReliefExport_Bilety_Get`, position <= 4 | Medium | Hybrid: "body" is semantic, procedure name is BM25 |
| T32 | `SELECT statements in TCK_FarePrice_GetPriceForXDesignation` | Function body or sql_batch from the fare price function showing SELECT logic. | `file_path` contains `TCK_FarePrice`, text content contains `SELECT`, position <= 5 | Medium | Hybrid: BM25 for procedure name, dense for SELECT context |

### Category 5 Notes

- T31 is **Medium** because the user is asking for the "body" specifically, not the header.
  The `procedure_body` node_type should appear, but BM25 will also match `procedure_header`
  (which contains the procedure name more prominently). Dense embeddings help here.
- T32 requires finding specific logic within a procedure body, which tests chunk granularity.

---

## Category 6: Natural Language Code Understanding

Tests the dense embedding model's ability to match natural language descriptions to code.
These queries use everyday language, not code identifiers. Dense embeddings are the primary
retrieval signal here; BM25 contributes only incidentally.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T33 | `How to connect to the database` | Should find OpenConnection or related database connection code in MainDM.pas. | `file_path` contains `MainDM.pas`, text content matches `(Connection\|Connect\|database)`, position <= 5 | Medium | Dense: semantic matching "connect to database" -> OpenConnection |
| T34 | `Where are ticket prices calculated` | Should find TCK_FarePrice_GetPriceForXDesignation.sql or related fare/price code. | `file_path` matches `(FarePrice\|Ticket\|SLS_Ticket)`, position <= 5 | Medium | Dense: semantic "prices calculated" -> fare price function |
| T35 | `How to export relief tickets` | Should find SLS_ReliefExport_Bilety_Get.sql or related export procedure. | `file_path` contains `ReliefExport` or `Bilety`, position <= 5 | Medium | Dense: semantic "export relief tickets" -> relief export procedure |
| T36 | `Where is the splash screen shown` | Should find Splash.pas or Splash.dfm -- the splash screen form. | `file_path` matches `Splash\.(pas\|dfm)`, position <= 5 | Easy | Dense: "splash screen" is a clear semantic concept |

### Category 6 Notes

- These tests specifically validate that the Jina embedding model produces meaningful
  dense vectors for natural language queries against code. If the model is broken
  (e.g., `trust_remote_code=False`), these tests will **all fail** because dense
  embeddings will be noise and BM25 alone won't match the natural language terms.
- T33 is the classic test case: the word "connect" should embed close to `OpenConnection`
  in the dense vector space.
- T34 and T35 test cross-language matching (English query -> code identifiers).

---

## Category 7: Edge Cases and Stress Tests

Tests boundary conditions: very short queries, very long queries, typos, partial names,
and queries that match many files.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T37 | `TdmMain` | Single identifier query. Should find class overview/summary from MainDM.pas despite minimal context. | `file_path` contains `MainDM`, position <= 3 | Easy | Sparse/BM25: single-token exact match (high BM25 score) |
| T38 | `I need to understand the complete architecture of the main data module TdmMain in MainDM.pas including all its published components, stored procedures, database connections, event handlers, and how it interacts with other forms in the application` | Long verbose query. Should still find TdmMain class overview despite query length diluting term frequencies. | `file_path` contains `MainDM.pas`, `node_type` in {`class_summary`, `class_summary_split`, `class_overview`}, position <= 5 | Hard | Dense: long query embedding quality, Reranker: overview detection in verbose text |
| T39 | `TdmMian` | Typo for TdmMain. Dense embedding might still be close enough; BM25 will miss entirely. | `file_path` contains `MainDM`, position <= 8 | Hard | Dense: typo resilience in embedding space |
| T40 | `procedure` | Extremely generic single word. Should return procedure-related chunks but from diverse files. Results should span multiple SQL files. | Results from >= 2 different `.sql` files, position <= 8 | Hard | Hybrid: generic query tests result diversity, not dominated by one file |

### Category 7 Notes

- T37 tests that a bare identifier without any context words still retrieves the right file.
  BM25 should handle this easily since `TdmMain` appears in context prefixes.
- T38 is the opposite extreme: a 40-word query. The concern is that term frequency is
  diluted across many tokens, and the dense embedding of a very long query may not
  be as focused. The reranker should still detect this as an overview query.
- T39 tests **typo resilience** -- a strength of dense embeddings over BM25. With
  `HYBRID_ALPHA=0.5`, even if BM25 returns nothing for "TdmMian", the dense embedding
  should be close enough to "TdmMain" to surface relevant results. This is **Hard**
  because it depends on the embedding model's character-level sensitivity.
- T40 tests that the system doesn't over-concentrate results from a single file when
  the query is extremely generic.

---

## Category 8: AI Agent Workflow Queries

These simulate real queries an AI coding agent would make when working on tasks. They
combine natural language intent with domain-specific terms.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T41 | `I need to modify the ticket export logic, where should I look?` | Should find SLS_ReliefExport_Bilety_Get.sql (ticket export procedure). May also surface related Pascal code. | `file_path` matches `(ReliefExport\|Bilety\|Ticket)`, position <= 5 | Medium | Dense: semantic "ticket export logic" -> export procedure, Hybrid: "ticket" token helps |
| T42 | `Where are report types defined?` | Should find constant declarations containing REPORT_TYPE_* or C_REPORT_* patterns. | text content matches `(REPORT_TYPE\|C_REPORT_)`, position <= 5 | Medium | Hybrid: BM25 for "report" + "type", dense for "defined" concept |
| T43 | `I need to add a new field to the main data module, show me the structure` | Should find TdmMain class summary or published section from MainDM.pas. Triggers overview query. | `file_path` contains `MainDM`, `node_type` in {`class_summary`, `class_summary_split`, `class_overview`, `declSection`}, position <= 5 | Medium | Reranker: "structure of" or "show me" might trigger overview, Dense: "data module" -> TDataModule |
| T44 | `What SQL procedures handle company data?` | Should find ADMIN_CompanyAllBranches.sql. May surface multiple company-related procedures. | `file_path` contains `Company` or text content contains `Company`, position <= 5 | Medium | Hybrid: BM25 for "company", dense for "SQL procedures handle" concept |

### Category 8 Notes

- These are the most realistic queries because AI agents tend to ask in natural language
  with a specific task in mind, rather than using bare identifiers.
- T43 is interesting because it contains both intent ("add a new field") and a target
  ("main data module"). The reranker should detect "show me the structure" as an
  overview pattern and promote class_summary chunks.
- T41 tests whether the system can bridge the gap between the abstract concept "ticket
  export logic" and the concrete procedure name `SLS_ReliefExport_Bilety_Get`.

---

## Expanded Test Set (T45-T56) — New Files

These tests target the 15 files added to test_sources in iteration 004 prep. They are
distributed across the existing categories to expand coverage without creating separate
categories.

### Category 1 Additions: Class Overview Queries

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T45 | `What is TDataSnapSchedule?` | class_overview or class_summary from DataSnapSchedule.pas describing the scheduled task runner. | `node_type` in {`class_summary`, `class_summary_split`, `class_overview`, `class_overview_split`}, `file_path` contains `DataSnapSchedule.pas`, position <= 3 | Medium | Reranker: "what is" pattern, implicit TObject class |
| T46 | `Describe TframeBaseCreator` | class_overview or class_summary from Creator_BaseFrame.pas describing the abstract wizard frame base. | `node_type` in {`class_summary`, `class_summary_split`, `class_overview`, `class_overview_split`}, `file_path` contains `Creator_BaseFrame.pas`, position <= 3 | Medium | Reranker: "describe" pattern, class name differs from filename |

### Category 2 Additions: Precise Identifier Search

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T47 | `FindFiles` | The FindFiles function implementation in KMFilesUtil.pas. Standalone utility function (not class method). | `node_type` in {`defProc`, `defProc_split`, `declProc`}, `file_path` contains `KMFilesUtil.pas`, text content contains `FindFiles`, position <= 3 | Easy | Sparse/BM25: exact function name match in utility module |
| T48 | `EMKFile_Emar105_Create` | T-SQL procedure definition from dbo.EMKFile_Emar105_Create.sql. | `node_type` in {`procedure_header`, `procedure_full`, `sql_batch`}, `file_path` contains `EMKFile_Emar105_Create`, position <= 2 | Easy | Sparse/BM25: exact procedure name match, cross-domain (emar) |
| T49 | `TT_Rides4EPO_GetRideCalendar` | T-SQL procedure definition for ride calendar generation. | `node_type` in {`procedure_header`, `procedure_full`, `sql_batch`}, `file_path` contains `TT_Rides4EPO_GetRideCalendar`, position <= 2 | Easy | Sparse/BM25: exact procedure name match, EPO domain |

### Category 3 Additions: Cross-File / Dependency

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T50 | `uses clause KMFilesUtil` | The declUses chunk from KMFilesUtil.pas showing interface/implementation imports. | `node_type` == `declUses`, `file_path` contains `KMFilesUtil.pas`, position <= 3 | Easy | Hybrid: BM25 matches "uses" + "KMFilesUtil", declUses node_type |

### Category 4 Additions: DFM Form Queries

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T51 | `login form components` | dfm_form_header from LoginFrm.dfm showing the login dialog with username/password fields. | `node_type` in {`dfm_form_header`, `dfm_object`, `dfm_object_group`}, `file_path` contains `LoginFrm.dfm`, position <= 3 | Medium | Reranker: "form components" triggers DFM query detection, bonus swapping |
| T52 | `TGeoPointEditorFrame latitude longitude` | DFM content from TGeoPointEditorFrame.dfm showing coordinate input fields. | `file_path` contains `TGeoPointEditorFrame.dfm`, text content matches `(latitude\|longitude)`, position <= 3 | Medium | Hybrid: BM25 for frame name + coordinate field names |

### Category 5 Additions: SQL Schema / Procedure

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T53 | `SLS_TicketPaymentTypeEMAR205 table columns` | Table definition from dbo.SLS_TicketPaymentTypeEMAR205.sql showing column definitions. | `node_type` in {`create_table`, `sql_batch`}, `file_path` contains `SLS_TicketPaymentTypeEMAR205`, position <= 3 | Easy | Sparse/BM25: exact table name match |
| T54 | `parameters of TCK_FarePriceScaleCopyFromDatabase` | procedure_header chunk showing fare price scale copy parameters. | `node_type` in {`procedure_header`, `procedure_full`, `sql_batch`}, `file_path` contains `TCK_FarePriceScaleCopyFromDatabase`, position <= 3 | Easy | Sparse/BM25: procedure name match, header contains parameters |

### Category 6 Additions: Natural Language Code Understanding

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T55 | `How to delete files older than a certain time` | Should find PurgeFiles or ForceDeleteFile in KMFilesUtil.pas. Dense embedding must match natural language to code utility functions. | `file_path` contains `KMFilesUtil.pas`, text content matches `(purge\|delete\|older)`, position <= 5 | Medium | Dense: semantic "delete files older than" -> PurgeFiles function |

### Category 8 Additions: AI Agent Workflow

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T56 | `I need to run a scheduled report as CSV, where is that logic?` | Should find DataSnapSchedule.pas with RunReport/SaveAsCSV methods. | `file_path` contains `DataSnapSchedule.pas`, text content matches `(CSV\|RunReport\|SaveAs)`, position <= 5 | Medium | Dense: "scheduled report as CSV" -> TDataSnapSchedule.RunReport/SaveAsCSV |

### Expanded Test Notes

- T45 tests a class that inherits from TObject (implicit), unlike most existing tests that
  target TFrame/TDataModule/TForm subclasses. The class name `TDataSnapSchedule` directly
  matches the filename `DataSnapSchedule.pas`, making this an Easy-Medium test.
- T46 mirrors the difficulty of T05/T06 — class name `TframeBaseCreator` differs from
  filename `Creator_BaseFrame.pas`. The reranker must match via `class_name` metadata.
- T47 tests a standalone function (not a class method) in a utility module — a different
  code pattern from form classes and data modules.
- T51 tests whether the DFM query detector (`is_dfm_query()`) fires for "login form" and
  correctly promotes `LoginFrm.dfm` over class summaries from .pas files.
- T55 is the hardest new test — pure natural language with no code identifiers. The dense
  embedding must semantically match "delete files older than" to `PurgeFiles`.
- T56 tests an AI-style question with mixed natural language and technical terms ("CSV",
  "scheduled report"). Tests whether hybrid search can bridge to DataSnapSchedule.pas.

---

## Category 9: FR3 Report Queries

Tests the FR3 reader's ability to extract band content, memo text labels, data bindings,
and Pascal scripts from FastReport .fr3 XML files. Validates context prefix, band grouping,
and correct extraction of `Text` attributes from `TfrxMemoView` elements.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T57 | `SettlementWithCarriersByRides report structure` | fr3_report_overview from SettlementWithCarriersByRides.fr3 describing bands, memo counts, data source. | `node_type` in {`fr3_report_overview`, `fr3_band_content`}, `file_path` contains `SettlementWithCarriersByRides.fr3`, position <= 3 | Medium | Reranker: report overview detection |
| T58 | `MasterDataSet NormalTicketVal` | Band content chunk containing the data binding `[MasterDataSet."NormalTicketVal"]`. | `file_path` contains `SettlementWithCarriersByRides.fr3`, text contains `NormalTicketVal`, position <= 3 | Easy | Sparse: exact identifier match in data binding |
| T59 | `report drilldown print out list` | Band or overview chunk from ListOfPrintOut.fr3 mentioning DrillDown. | `file_path` contains `ListOfPrintOut.fr3`, text contains `DrillDown` or `druk`, position <= 5 | Medium | Dense: natural language to report feature |
| T60 | `Bilety normalne header in report` | PageHeader band chunk containing the Polish label "Bilety normalne". | `file_path` contains `SettlementWithCarriersByRides.fr3`, text contains `Bilety normalne`, position <= 5 | Medium | Sparse: Polish label text match |

### Design Notes (Category 9)

- T57 tests overview detection for FR3 reports — the reranker should promote `fr3_report_overview`
  chunks the same way it promotes `class_overview` for Pascal files.
- T58 tests exact BM25 match for data binding identifiers embedded in band content chunks.
  The FR3 reader must extract `Text` from XML **attributes** (not child elements) to pass.
- T59 is a natural language query testing whether "drilldown" and "print out list" can
  semantically match to `ListOfPrintOut.fr3` which uses `DrillDown="True"` on GroupHeader bands.
- T60 tests a mixed Polish/English query for a specific label in the report header band.

---

## Category 10: DPROJ Project Queries

Tests the DPROJ reader's ability to extract project metadata, build configurations, and
unit references from Delphi .dproj XML files with MSBuild namespace handling.

| ID | Query | Expected Result | Pass Criteria | Difficulty | Tests |
|----|-------|-----------------|---------------|------------|-------|
| T61 | `Informica project configuration` | dproj_project_overview from Informica.dproj with GUID, MainSource, FrameworkType. | `node_type` in {`dproj_project_overview`, `dproj_build_config`}, `file_path` contains `Informica.dproj`, position <= 3 | Medium | Reranker: project overview detection |
| T62 | `MainTurdus.pas form reference in project` | Unit group chunk containing DCCReference for MainTurdus.pas -> frmMainTurdus. | `file_path` contains `Informica.dproj`, text contains `MainTurdus`, position <= 5 | Easy | Sparse: exact identifier match in unit reference |
| T63 | `RELEASE configuration defines in Delphi project` | Build config chunk with RELEASE;CLIENT;SYNCHRO defines. | `node_type` in {`dproj_build_config`}, `file_path` contains `Informica.dproj`, text contains `RELEASE` or `SYNCHRO` or `CLIENT`, position <= 5 | Medium | Hybrid: config name + defines match |

### Design Notes (Category 10)

- T61 tests overview detection for DPROJ files — the reranker should promote
  `dproj_project_overview` chunks for "project configuration" queries.
- T62 tests BM25 exact match for a specific unit reference within grouped DCCReference chunks.
  The DPROJ reader must handle the MSBuild XML namespace to extract any content at all.
- T63 tests whether build configuration chunks correctly capture DCC_Define values
  and are findable via both config name ("RELEASE") and define symbols ("SYNCHRO").

---

## Summary Table

| Category | Count | IDs | Primary Signal |
|----------|-------|-----|---------------|
| 1. Class Overview | 9+2 | T01-T09, T45-T46 | Reranker + Dense |
| 2. Precise Identifier | 10+3 | T10-T19, T47-T49 | Sparse/BM25 |
| 3. Cross-File / Dependency | 5+1 | T20-T24, T50 | Hybrid |
| 4. DFM Form | 4+2 | T25-T28, T51-T52 | Reranker + Hybrid |
| 5. SQL Schema / Procedure | 4+2 | T29-T32, T53-T54 | Sparse/BM25 + Hybrid |
| 6. Natural Language | 4+1 | T33-T36, T55 | Dense |
| 7. Edge Cases | 4 | T37-T40 | Mixed |
| 8. AI Agent Workflow | 4+1 | T41-T44, T56 | Hybrid + Dense |
| 9. FR3 Report | 4 | T57-T60 | Sparse + Reranker |
| 10. DPROJ Project | 3 | T61-T63 | Sparse + Reranker |
| **Total** | **63** | T01-T63 | |

### Difficulty Distribution

| Difficulty | Count | Tests |
|------------|-------|-------|
| Easy | 20 | T01-T04, T10-T12, T14-T17, T20, T25-T27, T29-T30, T36-T37, T47-T50, T53-T54 |
| Medium | 27 | T05-T09, T13, T18-T19, T21-T22, T28, T31-T35, T38, T41-T44, T45-T46, T51-T52, T55-T56 |
| Hard | 9 | T23-T24, T38-T40 |

### Search Aspect Coverage

| Aspect | Primary Tests | Secondary Tests |
|--------|--------------|-----------------|
| Dense embeddings | T33-T36, T39, T55, T56 | T23-T24, T38, T41-T44 |
| Sparse/BM25 | T10-T19, T37, T47-T49, T53-T54 | T20, T22, T29-T30, T40, T42 |
| Hybrid synergy | T20-T24, T28, T31-T32, T50, T52 | T12, T41-T44 |
| Reranker (overview detection) | T01-T09, T25-T27, T45-T46, T51 | T21, T38, T43 |
| Reranker (target matching) | T05-T06, T08 | T01-T04, T07, T09, T45-T46 |
| Reranker (cross-file penalty) | T08, T23 | T02, T40 |

---

## Appendix A: Test Source Files

The test index is built from 38 files in `test_sources/`:

### Original Files (23)

| File | Type | Key Content |
|------|------|-------------|
| `MainDM.pas` | Pascal | TdmMain data module, OpenConnection, ~500 published datasets |
| `MainTurdus.pas` | Pascal | TfrmMainTurdus main form, menu actions, UI components |
| `emar105.classes.pas` | Pascal | TEmar105_OIK, TEmar105_File, many getter/setter methods |
| `emar.base.classes.pas` | Pascal | Base classes for emar module |
| `Splash.pas` | Pascal | TfrmSplash splash screen form |
| `BaseEditorForm.pas` | Pascal | TfrmBaseEditor base class for editor forms |
| `FormBasicMain.pas` | Pascal | TBasicMainForm base class for main forms |
| `SalesReport.Classes.pas` | Pascal | TSalesReport and related types |
| `Licence.pas` | Pascal | Licensing logic |
| `PWebService.pas` | Pascal | Web service proxy classes |
| `ResourceStrings.pas` | Pascal | Resource string constants (REPORT_TYPE_*, C_REPORT_*) |
| `Informica.dpr` | Delphi project | Main project file with uses clause |
| `Informica.dproj` | DPROJ | Project configuration XML |
| `MainDM.dfm` | DFM | TdmMain form: dataset components, connections |
| `MainTurdus.dfm` | DFM | TfrmMainTurdus form: menus, toolbars, panels |
| `Splash.dfm` | DFM | TfrmSplash form: image, labels, progress bar |
| `WithFrame_SFTP.dfm` | DFM | SFTP frame: file transfer components |
| `dbo.SLS_ReliefExport_Bilety_Get.sql` | T-SQL | Ticket export stored procedure |
| `dbo.SLS_Ticket.sql` | T-SQL | SLS_Ticket table definition |
| `dbo.TCK_FarePrice_GetPriceForXDesignation.sql` | T-SQL | Fare price calculation function |
| `dbo.ADMIN_ReportDef_ReliefTicketPayments.sql` | T-SQL | Report definition procedure |
| `dbo.ADMIN_CompanyAllBranches.sql` | T-SQL | Company branches query procedure |
| `ADMIN_ReportDef_AnalysisRoute.sql` | T-SQL | Route analysis report procedure |

### Expanded Files (15) — Added in iteration 004 prep

| File | Type | Key Content | Targeted By |
|------|------|-------------|-------------|
| `HistoryThread.pas` | Pascal | THistoryThread background thread, ListView population | — |
| `Creator_BaseFrame.pas` | Pascal | TframeBaseCreator abstract wizard frame base, page navigation | T46 |
| `DataSnapSchedule.pas` | Pascal | TDataSnapSchedule task runner, RunReport, SaveAsCSV, GPS analysis | T45, T56 |
| `KMFilesUtil.pas` | Pascal | File utility library: FindFiles, PurgeFiles, encoding detection | T47, T50, T55 |
| `DriveExamWizardStep1.pas` | Pascal | Driving exam wizard step, TDriveExam, PORTALOSK conditionals | — |
| `LoginFrm.dfm` | DFM | TfrmLogin login dialog, username/password fields, 252KB | T51 |
| `TGeoPointEditorFrame.dfm` | DFM | TframeGeoPoint GPS coordinate editor, latitude/longitude | T52 |
| `BusStandActionWizardStep1.dfm` | DFM | Bus stand action wizard, maintenance management | — |
| `dbo.TT_Rides4EPO_GetRideCalendar.sql` | T-SQL | Ride calendar matrix procedure, EPO | T49 |
| `dbo.EMKFile_Emar105_Create.sql` | T-SQL | EMK file creation, EMAR 105 ticket export check | T48 |
| `dbo.TCK_FarePriceScaleCopyFromDatabase.sql` | T-SQL | Fare price scale/tariff copying, 782 lines | T54 |
| `dbo.SLS_TicketPaymentTypeEMAR205.sql` | T-SQL | Table: ticket payment types for EMAR 205 | T53 |
| `import.LPC_LicenceFeeStartData2Insert.sql` | T-SQL | Licence fee seed data import (import schema) | — |
| `SettlementWithCarriersByRides.fr3` | FR3 | Carrier settlement report: ticket breakdown by ride | — |
| `ListOfPrintOut.fr3` | FR3 | Print-out inventory report: series tracking, drill-down | — |

### Test Source Rotation Policy

The test_sources set should be periodically rotated to prevent overfitting:

1. **Permanent files** — Keep files that proved most difficult or exercised edge cases:
   MainDM.pas/dfm, MainTurdus.pas/dfm, emar105.classes.pas, BaseEditorForm.pas,
   ResourceStrings.pas, FormBasicMain.pas, LoginFrm.dfm
2. **Rotatable files** — Other files can be swapped out every 3-5 iterations for fresh
   random selections from the production set
3. **New file additions** — When adding files, prefer diversity: different file sizes,
   different code patterns (threads, wizards, utilities, data modules), different SQL
   schemas (dbo, import), and underrepresented types (.fr3, .dproj)

## Appendix B: Node Types Reference

Complete list of `node_type` metadata values by reader, used in pass criteria:

### Pascal Reader (27 types)

`defProc`, `declProc`, `declSection`, `declVar`, `declConst`, `declUses`, `comment`,
`declType`, `declClass`, `class_summary`, `class_overview`, `method_group`, `full_file`,
plus `_split` variants of each: `defProc_split`, `declProc_split`, `declSection_split`,
`declVar_split`, `declConst_split`, `comment_split`, `declType_split`, `declClass_split`,
`class_summary_split`, `class_overview_split`, `method_group_split`, `full_file_split`

### DFM Reader (4 types)

`dfm_form_header`, `dfm_object`, `dfm_object_group`, `full_file`

### SQL Reader (12 types)

`create_function`, `create_procedure`, `create_trigger`, `create_view`, `create_table`,
`alter_table`, `drop_table`, `select`, `statement`, `set_statement`, `create_index`, `full_file`

### T-SQL Chunker (19 types)

`sql_batch`, `procedure_full`, `function_full`, `procedure_header`, `function_header`,
`procedure_body`, `function_body`, plus various `_group` variants

### Python Reader (16 types)

`function_definition`, `decorated_definition`, `import_statement`, `class_definition`,
`full_file`, plus `_split` variants

### FR3 Reader (4 types)

`fr3_report_overview`, `fr3_band_content`, `fr3_pascal_script`, `fr3_variables`

### DPROJ Reader (3 types)

`dproj_project_overview`, `dproj_build_config`, `dproj_unit_group`

## Appendix C: Reranker Score Adjustments

Reference values from `shared/reranker.py` (active only for overview queries):

| Adjustment | Value | Applies To |
|------------|-------|-----------|
| Primary overview bonus | `+0.50` | `class_overview`, `class_summary`, `class_summary_split` |
| Overview bonus | `+0.25` | `dfm_form_header`, `procedure_header`, `function_header`, `procedure_full`, `function_full`, `declUses` |
| Target match bonus | `+0.15` | Any chunk whose `file_path`, `class_name`, `unit_name`, or `object_name` matches extracted target |
| Non-target overview penalty | `-0.20` | Overview chunks from files that don't match the target |
| Cross-file comment penalty | `-0.30` | `comment`, `comment_split` chunks from non-target files |
| Detail type penalty | `-0.05` | `defProc`, `method_group`, `declSection`, `declVar`, `declConst`, etc. |

## Appendix D: validate_rag.py Output Format (Specification)

The `validate_rag.py` script (to be created separately) should produce output in this format:

```
RAG Validation: 56 tests, alpha=0.50, index=test
============================================================

Category 1: Class Overview Queries
  T01  PASS   [#2] class_summary_split  MainDM.pas          "What is TdmMain?"
  T02  PASS   [#1] class_summary        emar105.classes.pas  "What classes are in emar105?"
  T03  PASS   [#2] class_overview        MainTurdus.pas       "What is TfrmMainTurdus?"
  ...

Category 2: Precise Identifier Search
  T10  PASS   [#1] declConst            ResourceStrings.pas  "REPORT_TYPE_PUNCTUALITY_RIDES"
  T11  PASS   [#1] defProc              MainDM.pas           "PrepareDataSet"
  ...

============================================================
Results: 38 PASS, 4 PARTIAL, 2 FAIL
Score:  90.9%  (80 / 88 points)
Rating: Excellent
============================================================
```

Each line shows:
- Test ID
- Result (PASS/PARTIAL/FAIL)
- Position of best matching result `[#N]`
- `node_type` of that result
- File name (basename only)
- Query text (truncated to 60 chars)

Failed tests should print additional detail showing what was found vs. what was expected.
