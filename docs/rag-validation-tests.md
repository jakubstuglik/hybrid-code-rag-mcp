# RAG Validation Test Scenarios

Comprehensive test suite for validating hybrid search quality.
Covers Delphi Pascal, T-SQL, DFM, FR3, and DPROJ file types across dense
(Jina v2 base code), sparse (BM25), hybrid fusion, and post-retrieval reranking.

The test corpus uses the **FleetOps** domain — a fictional fleet management and dispatch
platform — to keep all tests generic and domain-independent.

## Purpose

This document defines **78 test queries** organized into 14 categories that exercise every
aspect of the RAG retrieval pipeline:

1. **Chunking quality** — do the readers produce semantically meaningful chunks?
2. **Hybrid search** — does the 50/50 dense+sparse fusion return the right results?
3. **Reranker** — does `is_overview_query()` fire correctly and do the score adjustments
   promote the right chunk types?
4. **Cross-file relevance** — do results come from the correct file, not cross-file interlopers?

## How to Run

### Against the test index (quick iteration)

```bash
# Ensure the test index is built from test_sources/
python src/index_rag.py --config test

# Run the validation script
python src/validate_rag.py --config test
python src/validate_rag.py --config test --alpha 0.5
```

### Against the production index (final validation)

```bash
python src/validate_rag.py --config production
python src/validate_rag.py --config production --alpha 0.5
```

### Manual spot-check with query_test_index.py

```bash
python query_test_index.py --alpha 0.5
```

## Scoring System

Each test query is evaluated against its pass criteria and assigned one of three results:

| Result | Definition | Points |
|--------|-----------|--------|
| **PASS** | Most relevant chunk in top `max_position` results AND meets all criteria | 2 |
| **PARTIAL** | Chunk found within `partial_position` results OR correct file but wrong node_type | 1 |
| **FAIL** | Not found within `partial_position` results or completely wrong file | 0 |

### Overall Score

```
score = (PASS_count * 2 + PARTIAL_count * 1) / (total_tests * 2) * 100%
```

### Thresholds

| Rating | Score | Meaning |
|--------|-------|---------|
| Excellent | >= 90% | Ship it. No regressions. |
| Good | 75–89% | Acceptable. Review PARTIAL results for low-hanging improvements. |
| Needs work | 60–74% | Significant gaps. Check alpha, reranker, or chunking changes. |
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

## Category 1: Class Overview Queries (T01–T08)

Tests the reranker's ability to detect overview intent and promote `class_overview`,
`class_summary`, and `class_summary_split` chunks to the top positions.

All queries should trigger `is_overview_query() == True`.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T01 | `What is TdmFleet?` | class_summary/overview for TdmFleet from MainDataMod.pas | node_type in {class_summary, class_summary_split, class_overview}, file contains MainDataMod.pas, pos <= 3 | Medium |
| T02 | `What is TfrmMain?` | class_summary/overview for TfrmMain from MainForm.pas | same node_types, file contains MainForm.pas, pos <= 3 | Medium |
| T03 | `What does TReportScheduler do?` | class_overview/summary from ReportScheduler.pas | same node_types, file contains ReportScheduler.pas, pos <= 3 | Medium |
| T04 | `Describe TJobHistoryThread` | class_overview/summary from JobHistoryThread.pas | node_types in {class_overview, class_summary}, file contains JobHistoryThread.pas, pos <= 3 | Medium |
| T05 | `Overview of TWizardBaseFrame` | class_overview/summary from WizardBaseFrame.pas | same node_types, file contains WizardBaseFrame.pas, pos <= 3 | Medium |
| T06 | `What does TfrmBaseEditor do?` | class_overview/summary from BaseEditorForm.pas (class ≠ filename) | same node_types, file contains BaseEditorForm.pas, pos <= 3 | Medium |
| T07 | `Tell me about TPurgeFilesThread` | class_overview/summary from FileUtils.pas | node_types in {class_overview, class_summary}, file contains FileUtils.pas, pos <= 3 | Medium |
| T08 | `What fields does TdmFleet have?` | class_summary/declSection listing datasets from MainDataMod.pas | node_types in {class_summary, class_summary_split, class_overview, declSection}, file contains MainDataMod.pas, pos <= 3 | Medium |

**Notes:**
- T06 tests that the reranker can match `TfrmBaseEditor` to `BaseEditorForm.pas` via
  `class_name` metadata when the class name differs from the filename.
- T08 tests the "what fields" pattern which should trigger overview detection.

---

## Category 2: Precise Identifier Search (T09–T16)

Tests BM25/keyword matching for exact code identifiers. These should **NOT** trigger
the reranker. Results depend heavily on BM25 term frequency and context prefixes.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T09 | `REPORT_TYPE_DRIVER_PAYROLL` | Constant definition in AppConst.pas or JobReports.Classes.pas | file contains .pas, text contains identifier, pos <= 2 | Easy |
| T10 | `cdsVehicles` | cdsVehicles field declaration in MainDataMod.pas | file contains MainDataMod.pas, text contains cdsVehicles, pos <= 2 | Easy |
| T11 | `RunReport` | RunReport method in ReportScheduler.pas | file contains ReportScheduler.pas, text contains RunReport, pos <= 3 | Easy |
| T12 | `SaveAsCSV` | SaveAsCSV method in ReportScheduler.pas | file contains ReportScheduler.pas, text contains SaveAsCSV, pos <= 3 | Easy |
| T13 | `TJobHistoryThread.Execute` | Execute implementation in JobHistoryThread.pas | file contains JobHistoryThread.pas, text contains Execute, pos <= 3 | Easy |
| T14 | `FindFiles` | Standalone FindFiles procedure in FileUtils.pas | file contains FileUtils.pas, text contains FindFiles, pos <= 3 | Easy |
| T15 | `IXMLDeviceLicences` | Interface definition in DeviceLicence.pas | file contains DeviceLicence.pas, text contains IXMLDeviceLicences, pos <= 2 | Easy |
| T16 | `ValidateStep` | ValidateStep method in WizardBaseFrame.pas or JobWizardStep1.pas | file matches (WizardBaseFrame\|JobWizardStep1).pas, text contains ValidateStep, pos <= 3 | Easy |

---

## Category 3: Method & Procedure Search (T17–T22)

Tests finding specific named methods and SQL procedures.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T17 | `PrepareDataSet` | PrepareDataSet implementation in any .pas file | file contains .pas, text contains PrepareDataSet, pos <= 3 | Medium |
| T18 | `GetVehicle` | GetVehicle method in WebApiService.pas | file contains WebApiService.pas, text contains GetVehicle, pos <= 3 | Easy |
| T19 | `PurgeOldFiles procedure FileUtils` | PurgeOldFiles in FileUtils.pas | file contains FileUtils.pas, text contains PurgeOldFiles, pos <= 3 | Easy |
| T20 | `dbo.RPT_DriverPayrollGet` | DriverPayrollGet table-valued function in SQL file | file contains RPT_DriverPayrollGet, text contains RPT_DriverPayrollGet, pos <= 2 | Easy |
| T21 | `dbo.ORD_DispatchExport_Get` | ORD_DispatchExport_Get procedure in SQL file | file contains ORD_DispatchExport_Get, text contains identifier, pos <= 2 | Easy |
| T22 | `dbo.VEH_FuelCostCalc` | VEH_FuelCostCalc function in SQL file | file contains VEH_FuelCostCalc, text contains identifier, pos <= 2 | Easy |

---

## Category 4: SQL Object Lookup (T23–T28)

Tests retrieval of T-SQL objects including tables, procedures, and functions.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T23 | `What columns does Fleet_Vehicles table have?` | CREATE TABLE dbo.Fleet_Vehicles | file contains Fleet_Vehicles, text contains CREATE TABLE, pos <= 3 | Medium |
| T24 | `How to create a job order in SQL?` | dbo.ORD_CreateJobOrder procedure | file contains ORD_CreateJobOrder, pos <= 3 | Medium |
| T25 | `Driver payroll calculation SQL` | dbo.RPT_DriverPayrollGet table-valued function | file contains RPT_DriverPayrollGet, pos <= 3 | Medium |
| T26 | `vehicle service calendar stored procedure` | dbo.VEH_ServiceRecord_GetCalendar | file contains VEH_ServiceRecord_GetCalendar, pos <= 3 | Medium |
| T27 | `copy fuel price scale between branches` | dbo.VEH_FuelCostScaleCopyFromDB | file contains VEH_FuelCostScaleCopyFromDB, pos <= 3 | Medium |
| T28 | `initial data seed inserts Fleet` | import.Fleet_InitialData_Insert.sql | file contains Fleet_InitialData_Insert, pos <= 3 | Medium |

---

## Category 5: DFM & Form Search (T29–T34)

Tests retrieval of DFM form layout chunks including headers, component groups, and
specific UI widgets.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T29 | `main application form layout FleetOps` | dfm_form_header for TfrmMain in MainForm.dfm | node_type == dfm_form_header, file contains MainForm.dfm, pos <= 3 | Medium |
| T30 | `login dialog username password` | LoginForm.dfm with credential fields | file contains LoginForm.dfm, pos <= 3 | Medium |
| T31 | `GPS coordinate input frame latitude longitude` | CoordEditorFrame.dfm with lat/lon fields | file contains CoordEditorFrame.dfm, pos <= 3 | Medium |
| T32 | `splash screen form` | SplashForm.dfm form header | node_type == dfm_form_header, file contains SplashForm.dfm, pos <= 3 | Medium |
| T33 | `SFTP connection frame log viewer` | SFTPConnFrame.dfm | file contains SFTPConnFrame.dfm, pos <= 3 | Medium |
| T34 | `job wizard step 1 form pickup delivery address` | JobWizardStep1.dfm with address fields | file contains JobWizardStep1.dfm, pos <= 3 | Medium |

---

## Category 6: Cross-Concern / Multi-File (T35–T39)

Tests that queries requiring results from multiple files return appropriately diverse results.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T35 | `TWizardBaseFrame and its subclass TframeJobWizardStep1` | Results from both WizardBaseFrame.pas and JobWizardStep1.pas | file matches either, multi_file=True, pos <= 5 | Hard |
| T36 | `Where is REPORT_TYPE_DRIVER_PAYROLL used?` | Results from AppConst.pas and JobReports.Classes.pas | file matches either, text contains identifier, multi_file=True, pos <= 5 | Hard |
| T37 | `classes in VehicleData.classes.pas` | class_summary chunks from VehicleData.classes.pas | node_type in {class_summary, class_overview}, file contains VehicleData.classes.pas, pos <= 3 | Medium |
| T38 | `TDriverPayReport inherits from what class?` | TDriverPayReport class definition in JobReports.Classes.pas | file contains JobReports.Classes.pas, text contains TDriverPayReport, pos <= 3 | Medium |
| T39 | `login and main form interaction` | Results from both LoginForm and MainForm | file matches (LoginForm\|MainForm), multi_file=True, pos <= 5 | Hard |

---

## Category 7: Uses & Dependency Queries (T40–T43)

Tests retrieval of `declUses` chunks and import/dependency information.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T40 | `uses clause MainDataMod` | declUses chunk from MainDataMod.pas | node_type == declUses, file contains MainDataMod.pas, pos <= 3 | Medium |
| T41 | `units imported by ReportScheduler` | declUses chunk from ReportScheduler.pas | node_type == declUses, file contains ReportScheduler.pas, pos <= 4 | Medium |
| T42 | `What units does JobHistoryThread import?` | declUses chunk from JobHistoryThread.pas | node_type == declUses, file contains JobHistoryThread.pas, pos <= 4 | Medium |
| T43 | `What does FleetOps.dpr use and start up?` | FleetOps.dpr with Application.CreateForm | file contains FleetOps.dpr, text contains Application.CreateForm, pos <= 3 | Medium |

---

## Category 8: Negative / Edge Cases (T44–T48)

Tests boundary conditions: very short queries, typos, partial names, and ambiguous terms.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T44 | `procedure` | Generic query — should return SQL procedure results | file contains .sql, pos <= 5 | Hard |
| T45 | `TdmFlete` | Typo for TdmFleet — dense should still find MainDataMod.pas | file contains MainDataMod.pas, pos <= 5 | Hard |
| T46 | `fleet` | Very short — should match fleet-related files | file matches fleet (case-insensitive), pos <= 5 | Hard |
| T47 | `tfrmmain` | Lowercase class name — should find TfrmMain in MainForm.pas | file contains MainForm.pas, pos <= 5 | Hard |
| T48 | `SaveAsXLSX` | Method without class context — should find ReportScheduler.pas | file contains ReportScheduler.pas, text contains SaveAsXLSX, pos <= 3 | Medium |

---

## Category 9: AI Agent Queries (T49–T53)

Simulates real queries an AI coding agent would make when working on tasks.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T49 | `I need to add a new vehicle type constant — where should I add it?` | AppConst.pas as the place for constants | file contains AppConst.pas, pos <= 4 | Medium |
| T50 | `How do I schedule a report to run and export it to CSV?` | ReportScheduler.pas with Execute/SaveAsCSV | file contains ReportScheduler.pas, pos <= 4 | Medium |
| T51 | `What SQL procedure creates a job order?` | dbo.ORD_CreateJobOrder | file contains ORD_CreateJobOrder, pos <= 3 | Easy |
| T52 | `Which base class should I inherit from for a multi-step wizard?` | WizardBaseFrame.pas with TWizardBaseFrame | file contains WizardBaseFrame.pas, pos <= 4 | Medium |
| T53 | `Which unit contains XML data binding for device licences?` | DeviceLicence.pas | file contains DeviceLicence.pas, pos <= 4 | Medium |

---

## Category 10: FR3 Report Queries (T54–T58)

Tests the FR3 reader's ability to extract band content, labels, data bindings, Pascal
scripts, and report variables from FastReport `.fr3` XML files.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T54 | `DriverPayrollByTrips report overview` | fr3_report_overview from DriverPayrollByTrips.fr3 | node_type == fr3_report_overview, file contains DriverPayrollByTrips.fr3, pos <= 3 | Medium |
| T55 | `payroll report data band trips` | fr3_band_content from DriverPayrollByTrips.fr3 | node_type == fr3_band_content, file contains DriverPayrollByTrips.fr3, pos <= 4 | Medium |
| T56 | `Pascal script in driver payroll report` | fr3_pascal_script from DriverPayrollByTrips.fr3 | node_type == fr3_pascal_script, file contains DriverPayrollByTrips.fr3, pos <= 4 | Medium |
| T57 | `ListOfJobOrders report` | ListOfJobOrders.fr3 report overview | node_type in {fr3_report_overview, fr3_band_content}, file contains ListOfJobOrders.fr3, pos <= 3 | Medium |
| T58 | `report variables DriverName PeriodFrom` | fr3_variables in DriverPayrollByTrips.fr3 | node_type == fr3_variables, file contains DriverPayrollByTrips.fr3, pos <= 5 | Medium |

---

## Category 11: DPROJ Queries (T59–T62)

Tests the DPROJ reader's ability to extract project metadata, build configurations, and
unit references from Delphi `.dproj` files.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T59 | `FleetOps project GUID` | dproj_project_overview from FleetOps.dproj with ProjectGuid | node_type == dproj_project_overview, file contains FleetOps.dproj, pos <= 3 | Medium |
| T60 | `Debug build configuration defines FleetOps` | dproj_build_config from FleetOps.dproj with DEBUG/FLEETOPS_VCL | node_type == dproj_build_config, file contains FleetOps.dproj, pos <= 3 | Medium |
| T61 | `all units in the FleetOps project` | dproj_unit_group from FleetOps.dproj | node_type == dproj_unit_group, file contains FleetOps.dproj, pos <= 3 | Medium |
| T62 | `FleetOps main program entry point startup` | FleetOps.dpr with Application.CreateForm | file contains FleetOps.dpr, text contains Application, pos <= 3 | Medium |

---

## Category 12: File Disambiguation (T63–T66)

Tests the retrieval system's ability to prefer the correct file extension when a query
implies either the code file (`.pas`) or the form file (`.dfm`).

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T63 | `MainForm.pas source code class definition` | MainForm.pas (not .dfm) | file contains MainForm.pas, pos <= 3 | Medium |
| T64 | `MainForm form layout components design` | MainForm.dfm (not .pas) | node_type in {dfm_form_header, dfm_object, dfm_object_group}, file contains MainForm.dfm, pos <= 3 | Medium |
| T65 | `JobWizardStep1 Pascal code logic validation` | JobWizardStep1.pas (not .dfm) | file contains JobWizardStep1.pas, pos <= 3 | Medium |
| T66 | `SplashForm form design layout` | SplashForm.dfm (not .pas) | node_type in {dfm_form_header, dfm_object, dfm_object_group}, file contains SplashForm.dfm, pos <= 3 | Medium |

---

## Category 13: Semantic Paraphrase (T67–T72)

Tests the dense embedding model's ability to match paraphrased natural language to code,
with no exact token overlap between query and source identifier.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T67 | `fleet data module datasets` | TdmFleet in MainDataMod.pas | file contains MainDataMod.pas, pos <= 4 | Medium |
| T68 | `job dispatch stored procedure` | dbo.ORD_DispatchExport_Get | file contains ORD_DispatchExport_Get, pos <= 4 | Medium |
| T69 | `authentication screen user credentials` | LoginForm.dfm | file contains LoginForm.dfm, pos <= 4 | Medium |
| T70 | `driver earnings report template` | DriverPayrollByTrips.fr3 | file contains DriverPayrollByTrips.fr3, pos <= 4 | Medium |
| T71 | `vehicle maintenance service schedule` | dbo.VEH_ServiceRecord_GetCalendar | file contains VEH_ServiceRecord_GetCalendar, pos <= 4 | Medium |
| T72 | `background worker populates list view with history` | TJobHistoryThread in JobHistoryThread.pas | file contains JobHistoryThread.pas, pos <= 4 | Medium |

---

## Category 14: Multilingual / Domain Language (T73–T78)

Tests handling of non-English text embedded in reports and form labels. The FleetOps
report template (`DriverPayrollByTrips.fr3`) uses German column headers.

| ID | Query | Expected | Pass Criteria | Difficulty |
|----|-------|----------|---------------|------------|
| T73 | `Bezahlt column payroll report` | German label Bezahlt (paid) in DriverPayrollByTrips.fr3 | file contains DriverPayrollByTrips.fr3, text contains Bezahlt, pos <= 5 | Hard |
| T74 | `Gesamt total footer payroll` | German label Gesamt (total) in summary band | file contains DriverPayrollByTrips.fr3, text contains Gesamt, pos <= 5 | Hard |
| T75 | `Fahrer driver report header` | German label Fahrer (driver) in page header | file contains DriverPayrollByTrips.fr3, text contains Fahrer, pos <= 5 | Hard |
| T76 | `Strecke Datum report columns` | German labels Strecke (route) and Datum (date) | file contains DriverPayrollByTrips.fr3, text matches (Strecke\|Datum), pos <= 5 | Hard |
| T77 | `report with non-English column headers fleet` | DriverPayrollByTrips.fr3 with German labels | file contains DriverPayrollByTrips.fr3, pos <= 5 | Hard |
| T78 | `Seite von Seitenangabe Seitennummer Bericht` | German page footer: Seite … von … in DriverPayrollByTrips.fr3 | file contains DriverPayrollByTrips.fr3, text contains Seite, pos <= 5 | Hard |

**Notes:**
- T73–T76 test mixed German/English queries against a German-language report template.
- T78 is a **pure German** query with no English tokens — BM25 can help only if the
  German text is in the index; dense embedding handles cross-lingual similarity.

---

## Summary Table

| Category | Count | IDs | Primary Signal |
|----------|-------|-----|---------------|
| 1. Class Overview Queries | 8 | T01–T08 | Reranker + Dense |
| 2. Precise Identifier Search | 8 | T09–T16 | Sparse/BM25 |
| 3. Method & Procedure Search | 6 | T17–T22 | Sparse/BM25 |
| 4. SQL Object Lookup | 6 | T23–T28 | Dense + Hybrid |
| 5. DFM & Form Search | 6 | T29–T34 | Reranker + Dense |
| 6. Cross-Concern / Multi-File | 5 | T35–T39 | Hybrid |
| 7. Uses & Dependency Queries | 4 | T40–T43 | Sparse + Hybrid |
| 8. Negative / Edge Cases | 5 | T44–T48 | Mixed |
| 9. AI Agent Queries | 5 | T49–T53 | Dense |
| 10. FR3 Report Queries | 5 | T54–T58 | Sparse + Reranker |
| 11. DPROJ Queries | 4 | T59–T62 | Sparse + Reranker |
| 12. File Disambiguation | 4 | T63–T66 | Hybrid |
| 13. Semantic Paraphrase | 6 | T67–T72 | Dense |
| 14. Multilingual / Domain Language | 6 | T73–T78 | Dense + Sparse |
| **Total** | **78** | T01–T78 | |

### Difficulty Distribution

| Difficulty | Count |
|------------|-------|
| Easy | 16 (T09–T16, T18–T22, T51) |
| Medium | 46 (T01–T08, T17, T23–T34, T37–T43, T48–T50, T52–T62, T67–T72) |
| Hard | 16 (T35–T36, T39, T44–T47, T73–T78) |

### Search Aspect Coverage

| Aspect | Primary Tests |
|--------|--------------|
| Dense embeddings | T30–T31, T33, T35, T37–T39, T49–T53, T67–T72, T73–T78 |
| Sparse/BM25 | T09–T22, T40, T43–T44, T48, T58 |
| Hybrid synergy | T23–T28, T41–T42, T60–T61, T63–T66 |
| Reranker (overview) | T01–T08, T29, T32, T54, T57, T59 |

---

## Appendix A: Test Source Files

The test index is built from 37 files in `test_sources/` (FleetOps domain):

### Pascal (.pas) — 15 files

| File | Key Classes / Content |
|------|-----------------------|
| `MainDataMod.pas` | `TdmFleet(TDataModule)` — 50+ cds* datasets, connections |
| `MainForm.pas` | `TfrmMain(TForm)` — main window, menus, toolbar, auto-logout |
| `BaseEditorForm.pas` | `TfrmBaseEditor` — base editor form (class ≠ filename) |
| `BasicMainForm.pas` | `TBasicMainForm` — minimal main form base |
| `VehicleData.classes.pas` | 20+ classes: TVehicleRecord, TDriverRecord, TRouteRecord, TJobOrder, TFuelRecord, etc. |
| `JobReports.Classes.pas` | TJobReportItem, TDriverPayReport, TFuelCostReport + REPORT_TYPE_* constants |
| `AppConst.pas` | App-wide constants: REPORT_TYPE_*, REPORT_FORMAT_*, paths |
| `JobHistoryThread.pas` | `TJobHistoryThread(TThread)` — background job history loader |
| `WizardBaseFrame.pas` | `TWizardBaseFrame(TFrame)` — multi-step wizard navigation base |
| `JobWizardStep1.pas` | `TframeJobWizardStep1(TWizardBaseFrame)` — job order wizard step 1 |
| `ReportScheduler.pas` | `TReportScheduler` — RunReport, SaveAsCSV, SaveAsXLSX, SaveAsXML |
| `FileUtils.pas` | `TPurgeFilesThread`, standalone `FindFiles`, `PurgeOldFiles` |
| `DeviceLicence.pas` | XML data binding: `IXMLDeviceLicences` hierarchy |
| `WebApiService.pas` | WSDL/SOAP stub: `IFleetWebService`, FWS* types |
| `SplashForm.pas` | `TfrmSplash` — splash screen |

### DFM — 6 files

| File | Root Form / Key Widgets |
|------|------------------------|
| `MainForm.dfm` | TfrmMain — menu, toolbar, status bar, auto-logout panel |
| `LoginForm.dfm` | TfrmLogin — username/password fields, OK/Cancel |
| `CoordEditorFrame.dfm` | frameCoordEditor — latitude/longitude inputs |
| `SplashForm.dfm` | TfrmSplash — logo, progress bar |
| `SFTPConnFrame.dfm` | frameSFTPConn — SFTP log memo, progress |
| `JobWizardStep1.dfm` | frameJobWizardStep1 — pickup/delivery addresses, stop list |

### SQL — 12 files

| File | Object Type | Purpose |
|------|-------------|---------|
| `dbo.Fleet_Vehicles.sql` | TABLE | Vehicle registry |
| `dbo.Fleet_VehiclePayloadType.sql` | TABLE | Payload type reference |
| `dbo.ORD_CreateJobOrder.sql` | PROCEDURE | Creates a job order with driver/vehicle validation |
| `dbo.ORD_DispatchExport_Get.sql` | PROCEDURE | Dispatch export |
| `dbo.RPT_DriverPayrollGet.sql` | FUNCTION (TVF) | Driver payroll by trip period |
| `dbo.RPT_ReportDef_Analysis.sql` | PROCEDURE | Report definition analysis |
| `dbo.VEH_FuelCostCalc.sql` | FUNCTION | Fuel cost calculation |
| `dbo.VEH_FuelCostScaleCopyFromDB.sql` | PROCEDURE | Copy fuel price scale between branches |
| `dbo.VEH_ServiceRecord_GetCalendar.sql` | PROCEDURE | Vehicle service calendar |
| `dbo.ADMIN_AllBranches.sql` | PROCEDURE | All branches query |
| `dbo.ADMIN_ReportDef_PayrollSummary.sql` | PROCEDURE | Payroll summary report definition |
| `import.Fleet_InitialData_Insert.sql` | DATA | Initial seed data inserts |

### FR3 — 2 files

| File | Content |
|------|---------|
| `DriverPayrollByTrips.fr3` | Driver payroll report with German column headers (Bezahlt, Gesamt, Fahrer, Strecke, Datum), Pascal script, report variables |
| `ListOfJobOrders.fr3` | Job orders list report with DrillDown group |

### DPROJ — 2 files

| File | Content |
|------|---------|
| `FleetOps.dproj` | Project GUID, Debug/Release configs, unit group |
| `FleetOps.dpr` | Program entry: Application.CreateForm for TdmFleet + TfrmMain |

---

## Appendix B: Node Types Reference

Complete list of `node_type` metadata values by reader, used in pass criteria:

### Pascal Reader (27 types)

`defProc`, `declProc`, `declSection`, `declVar`, `declConst`, `declUses`, `comment`,
`declType`, `declClass`, `class_summary`, `class_overview`, `method_group`, `full_file`,
plus `_split` variants: `defProc_split`, `class_summary_split`, `class_overview_split`, etc.

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

---

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
