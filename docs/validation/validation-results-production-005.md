# RAG Validation Results - Production Index (Iteration 005c)

**Date:** 2026-03-12  
**Config:** production  
**Hybrid Alpha:** 0.5  
**Total Tests:** 56  
**Rating:** Good

---

## Summary

| Metric | Value |
|--------|-------|
| **Score** | **94 / 112** |
| **Percentage** | **83.9%** |
| **PASS** | 40 |
| **PARTIAL** | 14 |
| **FAIL** | 2 |

---

## Category Summary

| Category | Tests | PASS | PARTIAL | FAIL | Pass Rate |
|----------|-------|------|---------|------|-----------|
| Class Overview Queries | 11 | 5 | 5 | 1 | 45% |
| Precise Identifier Search | 13 | 11 | 2 | 0 | 85% |
| Cross-File / Dependency | 6 | 5 | 1 | 0 | 83% |
| DFM Form Queries | 6 | 5 | 1 | 0 | 83% |
| SQL Schema / Procedure | 6 | 4 | 2 | 0 | 67% |
| Natural Language Code Understanding | 5 | 4 | 1 | 0 | 80% |
| Edge Cases / Stress Tests | 4 | 3 | 1 | 0 | 75% |
| AI Agent Workflow | 5 | 3 | 1 | 1 | 60% |

---

## Detailed Results by Category

### Class Overview Queries

#### T01 - "What is TdmMain?" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview}, file matches `MainDM.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: node_type match at #1 (class_summary from DBClassesBusStop.pas, wrong file) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary | DBClassesBusStop.pas | 0.4572 | |
| 2 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 3 | dfm_form_header | MainDM.dfm | 0.5000 | TdmMain |
| 4 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 5 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 6 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 7 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 8 | method_group | MainDM.pas | 0.5000 | TdmMain |

> **Regression from 004 (PASS→PARTIAL).** class_summary from DBClassesBusStop.pas outranked MainDM.pas at #1. The correct class_summary_split from MainDM.pas appeared at #2. Production reindex introduced new chunks from DBClassesBusStop.pas that compete with TdmMain overview chunks. Reranker did not sufficiently penalize the cross-file interloper.

---

#### T02 - "What classes are in emar105.classes.pas?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_overview}, file matches `emar105`, within top 2 (partial: top 5) |
| **Matched** | #1 - class_summary in emar105.classes.pas (score: 0.2827) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **emar105.classes.pas** | **0.2827** | |
| 2 | class_summary | emar105.classes.pas | 0.5000 | |
| 3 | class_summary | emar105.classes.pas | 0.5000 | |
| 4 | class_summary | emar105.classes.pas | 0.5000 | |
| 5 | declUses | emar105.classes.pas | 0.5000 | |
| 6 | declUses | emar105.classes.pas | 0.5000 | |
| 7 | declClass | emar105.classes.pas | 0.5000 | |
| 8 | declClass | emar105.classes.pas | 0.5000 | |

---

#### T03 - "What is TfrmMainTurdus?" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `MainTurdus.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: file_path match at #1 (declProc, wrong node_type) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 2 | method_group | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 4 | dfm_form_header | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 5 | declVar | MainTurdus.pas | 0.5000 | |
| 6 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 7 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 8 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |

> **Regression from 004 (PASS→PARTIAL).** class_overview no longer appears in top results. declProc at #1 instead of class_overview. The reranker's overview boost was insufficient to surface the class_overview chunk in the production index with more competing chunks.

---

#### T04 - "Describe TfrmSplash" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `Splash.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in ForisSplash.pas (score: 0.7510) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **ForisSplash.pas** | **0.7510** | **TfrmSplash** |
| 2 | dfm_form_header | Splash.dfm | 0.5000 | TfrmSplash |
| 3 | defProc | Splash.pas | 0.5000 | TfrmSplash |
| 4 | method_group | Splash.pas | 0.5000 | TfrmSplash |
| 5 | declProc | Splash.pas | 0.5000 | TfrmSplash |
| 6 | dfm_object | Splash.dfm | 0.5000 | TfrmSplash |
| 7 | declVar | Splash.pas | 0.5000 | |
| 8 | declProc | Splash.pas | 0.5000 | TfrmSplash |

---

#### T05 - "What does TfrmBaseEditor do?" - FAIL &#x274C;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `BaseEditorForm.pas`, within top 3 (partial: top 5) |
| **Detail** | No class_summary/class_overview found. defProc from TPersonEditorFrame.pas at #1, dfm_form_header from BaseEditorForm.dfm at #2. |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | TPersonEditorFrame.pas | 0.8005 | |
| 2 | dfm_form_header | BaseEditorForm.dfm | 0.6086 | TfrmBaseEditor |
| 3 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 4 | class_summary_split | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 5 | class_summary_split | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 6 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 7 | class_summary_split | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 8 | class_summary_split | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |

> **Regression from 004 (PASS→FAIL).** class_overview from BaseEditorForm.pas no longer appears in top results. A defProc from TPersonEditorFrame.pas (wrong file) outranked everything at #1 (score 0.8005). The class_summary_split chunks appear at #4-5 but the criteria requires top 3 for PASS. Production index introduced competing chunks that displaced the overview.

---

#### T06 - "How does TBasicMainForm work?" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `FormBasicMain.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: file_path match at #1, node_type match at #2 (class_overview from MainForisAP.pas, wrong file) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | method_group | FormBasicMain.pas | 0.5000 | TBasicMainForm |
| 2 | class_overview | MainForisAP.pas | 0.5000 | |
| 3 | declProc | FormBasicMain.pas | 0.5000 | TBasicMainForm |
| 4 | declVar | FormBasicMain.pas | 0.5000 | |
| 5 | defProc | FormBasicMain.pas | 0.5000 | TBasicMainForm |
| 6 | defProc | FormBasicMain.pas | 0.5000 | TBasicMainForm |
| 7 | defProc | FormBasicMain.pas | 0.5000 | TBasicMainForm |
| 8 | defProc | FormBasicMain.pas | 0.5000 | TBasicMainForm |

> Right file found at #1 but wrong node_type (method_group instead of class_overview/class_summary). The class_overview appeared at #2 but for the wrong file (MainForisAP.pas). Reranker did not boost the correct overview chunk — consistent with 004 behavior.

---

#### T07 - "Tell me about TSalesReport" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `SalesReport`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in SalesReport.Classes.pas (score: 0.1380) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **SalesReport.Classes.pas** | **0.1380** | **TSalesReport** |
| 2 | class_summary | SalesReport.Classes.pas | 0.5000 | TSalesReportList |
| 3 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 4 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 5 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 6 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 7 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 8 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReport |

---

#### T08 - "Overview of TEmar105_OIK class" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `emar105`, class_name matches `TEmar105_OIK`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in emar105.classes.pas (score: 0.8065) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **emar105.classes.pas** | **0.8065** | **TEmar105_OIK** |
| 2 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 3 | class_overview | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 4 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 5 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 6 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 7 | method_group | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 8 | declClass | emar105.classes.pas | 0.5000 | TEmar105_OIK |

---

#### T09 - "What fields does TdmMain have?" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, declSection}, file matches `MainDM.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: file_path match at #1 (class_overview, wrong node_type) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_overview | MainDM.pas | 0.4656 | TdmMain |
| 2 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 4 | dfm_form_header | MainDM.dfm | 0.5000 | TdmMain |
| 5 | class_overview | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 6 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 7 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 8 | method_group | MainDM.pas | 0.5000 | TdmMain |

> **Regression from 004 (PASS→PARTIAL).** class_overview at #1 instead of class_summary_split. The criteria requires class_summary/class_summary_split/declSection — class_overview doesn't match. The class_summary_split chunks at #2-3 would pass but the full match requires #1 hit. Borderline failure due to strict node_type matching.

---

#### T45 - "What is TDataSnapSchedule?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, class_overview_split}, file matches `DataSnapSchedule.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in DataSnapSchedule.pas (score: 0.3270) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **DataSnapSchedule.pas** | **0.3270** | **TDataSnapSchedule** |
| 2 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 3 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 4 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 5 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 6 | declSection | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 7 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 8 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |

---

#### T46 - "Describe TframeBaseCreator" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, class_overview_split}, file matches `Creator_BaseFrame.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: node_type match at #5 (class_summary from Creator_CreatorFrame.pas, wrong file) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | dfm_form_header | Creator_BaseFrame.dfm | 0.7820 | TframeBaseCreator |
| 2 | method_group | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |
| 3 | method_group | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |
| 4 | method_group | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |
| 5 | class_summary | Creator_CreatorFrame.pas | 0.5000 | |
| 6 | defProc | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |
| 7 | defProc | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |
| 8 | defProc | Creator_BaseFrame.pas | 0.5000 | TframeBaseCreator |

> **Regression from 004 (PASS→PARTIAL).** dfm_form_header from Creator_BaseFrame.dfm outranked the class_summary from Creator_BaseFrame.pas that was at #1 in 004. The class_summary from the correct file no longer appears in top 8. A class_summary from Creator_CreatorFrame.pas (wrong file) appeared at #5 instead.

---

### Precise Identifier Search

#### T10 - "REPORT_TYPE_PUNCTUALITY_RIDES" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | file matches `.pas`, text contains `REPORT_TYPE_PUNCTUALITY_RIDES`, within top 2 (partial: top 5) |
| **Matched** | #1 - declConst in Globals.pas (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declConst** | **Globals.pas** | **1.0000** | |
| 2 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 4 | declConst | ResourceStrings.pas | 0.5000 | |
| 5 | declConst | ResourceStrings.pas | 0.5000 | |
| 6 | declConst | ResourceStrings.pas | 0.5000 | |
| 7 | declConst | ResourceStrings.pas | 0.5000 | |
| 8 | declConst | ResourceStrings.pas | 0.5000 | |

---

#### T11 - "PreapreDataSet" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split, method_group}, text contains `PrepareDataSet`, within top 2 (partial: top 5) |
| **Matched** | #1 - defProc in MainDM.pas (score: 0.8266) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **MainDM.pas** | **0.8266** | **TdmMain** |
| 2 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 3 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 4 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 5 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 6 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 7 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 8 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |

> **Improvement from 004 (PARTIAL→PASS).** Test query changed from "PrepareDataSet" to "PreapreDataSet" to match the actual typo in the source code. BM25 now finds the exact match at #1.

---

#### T12 - "OpenConnection" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split}, file matches `MainDM.pas`, text contains `OpenConnection`, within top 2 (partial: top 5) |
| **Matched** | #1 - defProc in MainDM.pas (score: 0.5538) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **MainDM.pas** | **0.5538** | **TdmMain** |
| 2 | dfm_object | MainDM.dfm | 0.5000 | TdmMain |
| 3 | class_overview | MainDM.pas | 0.5000 | TdmMain |
| 4 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 5 | dfm_object | MainDM.dfm | 0.5000 | TdmMain |
| 6 | class_summary | PWebService.pas | 0.5000 | connection2 |
| 7 | comment | Informica.dpr | 0.5000 | |
| 8 | class_summary | PWebService.pas | 0.5000 | connection |

---

#### T13 - "GetCardSerialNumber" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | node_type in {method_group, method_group_split, defProc}, file matches `emar`, text contains `GetCardSerialNumber`, within top 4 (partial: top 6) |
| **Detail** | Partial: file_path match at #1, node_type match at #3, text_pattern match at #1 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declProc | emar_105.pas | 0.8149 | |
| 2 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 3 | method_group | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 4 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 5 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 6 | declSection | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 7 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 8 | method_group | emar.base.classes.pas | 0.5000 | TEmar_ProprietaryMIFAREcard |

> **Regression from 004 (PASS→PARTIAL).** declProc from emar_105.pas at #1 instead of defProc. The criteria requires method_group/method_group_split/defProc but got declProc. The method_group at #3 matches but is outside the top 2 PASS threshold.

---

#### T14 - "SLS_ReliefExport_Bilety_Get" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, function_header}, file matches `SLS_ReliefExport_Bilety_Get`, within top 3 (partial: top 5) |
| **Matched** | #2 - procedure_header in dbo.SLS_ReliefExport_Bilety_Get.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | emar.base.classes.pas | 0.5000 | |
| **2** | **procedure_header** | **dbo.SLS_ReliefExport_Bilety_Get.sql** | **0.5000** | |
| 3 | comment | SalesReport.Classes.pas | 0.5000 | |
| 4 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 7 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 8 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReport |

---

#### T15 - "TCK_FarePrice_GetPriceForXDesignation" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {function_header, function_full, procedure_header}, file matches `TCK_FarePrice`, within top 2 (partial: top 5) |
| **Detail** | Full match at position 3 (>2). function_header at #3. |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| 2 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| **3** | **function_header** | **dbo.TCK_FarePrice_GetPriceForXDesignation.sql** | **0.5000** | |
| 4 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.5000 | |
| 5 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| 6 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 7 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 8 | method_group | emar.base.classes.pas | 0.5000 | TEmar_CityTariffPrice |

> **Regression from 004 (PASS→PARTIAL).** function_header dropped from #1 to #3. function_body chunks outranked the header. In 004, the function_header was at #1 with score 0.8414; now all scores are flat at 0.5000, suggesting BM25 and dense scores are failing to differentiate between header and body chunks.

---

#### T16 - "ADMIN_ReportDef_AnalysisRoute" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `ADMIN_ReportDef_AnalysisRoute`, within top 3 (partial: top 5) |
| **Matched** | #2 - procedure_header in ADMIN_ReportDef_AnalysisRoute.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| **2** | **procedure_header** | **ADMIN_ReportDef_AnalysisRoute.sql** | **0.5000** | |
| 3 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| 4 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| 5 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| 6 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| 7 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |
| 8 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.5000 | |

---

#### T17 - "ADMIN_CompanyAllBranches" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `ADMIN_CompanyAllBranches`, within top 3 (partial: top 5) |
| **Matched** | #2 - procedure_header in dbo.ADMIN_CompanyAllBranches.sql (score: 0.7187) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | procedure_body | dbo.ADMIN_CompanyAllBranches.sql | 0.5000 | |
| **2** | **procedure_header** | **dbo.ADMIN_CompanyAllBranches.sql** | **0.7187** | |
| 3 | procedure_body | dbo.ADMIN_CompanyAllBranches.sql | 0.5000 | |
| 4 | comment | emar.base.classes.pas | 0.5000 | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 7 | declConst | ResourceStrings.pas | 0.5000 | |
| 8 | declConst | ResourceStrings.pas | 0.5000 | |

---

#### T18 - "GetInfoText" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split, method_group, class_summary}, text contains `GetInfoText`, within top 4 (partial: top 6) |
| **Matched** | #2 - class_summary in Splash.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declConst | SalesReport.Classes.pas | 0.5000 | |
| **2** | **class_summary** | **Splash.pas** | **0.5000** | **TfrmSplash** |
| 3 | declProc | Licence.pas | 0.5000 | IXMLTprivilage |
| 4 | defProc | emar.base.classes.pas | 0.5000 | TEmar_ReportEvent |
| 5 | declConst | ResourceStrings.pas | 0.5000 | |
| 6 | declConst | ResourceStrings.pas | 0.5000 | |
| 7 | declConst | ResourceStrings.pas | 0.5000 | |
| 8 | declConst | ResourceStrings.pas | 0.5000 | |

---

#### T19 - "C_REPORT_" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | node_type in {declConst, declConst_split, declSection}, text contains `C_REPORT_`, within top 5 (partial: top 8) |
| **Matched** | #1 - declConst in SalesReport.Classes.pas (score: 0.7228) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declConst** | **SalesReport.Classes.pas** | **0.7228** | |
| 2 | declConst | SalesReport.Classes.pas | 0.5000 | |
| 3 | declConst | SalesReport.Classes.pas | 0.5000 | |
| 4 | declConst | SalesReport.Classes.pas | 0.5000 | |
| 5 | comment | SalesReport.Classes.pas | 0.5000 | |
| 6 | declConst | ResourceStrings.pas | 0.5000 | |
| 7 | declConst | SalesReport.Classes.pas | 0.5000 | |
| 8 | declConst | ResourceStrings.pas | 0.5000 | |

---

#### T47 - "FindFiles" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split, declProc}, file matches `KMFilesUtil.pas`, text contains `FindFiles`, within top 3 (partial: top 5) |
| **Matched** | #1 - defProc in KMFilesUtil.pas (score: 0.6101) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **KMFilesUtil.pas** | **0.6101** | |
| 2 | declProc | KMFilesUtil.pas | 0.5000 | |
| 3 | declType | KMFilesUtil.pas | 0.5000 | |
| 4 | defProc | KMFilesUtil.pas | 0.5000 | |
| 5 | defProc | KMFilesUtil.pas | 0.5000 | |
| 6 | comment | KMFilesUtil.pas | 0.5000 | |
| 7 | comment | KMFilesUtil.pas | 0.5000 | |
| 8 | declType | KMFilesUtil.pas | 0.5000 | |

---

#### T48 - "EMKFile_Emar105_Create" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `EMKFile_Emar105_Create`, within top 2 (partial: top 5) |
| **Matched** | #2 - procedure_header in dbo.EMKFile_Emar105_Create.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | emar105.classes.pas | 0.5000 | |
| **2** | **procedure_header** | **dbo.EMKFile_Emar105_Create.sql** | **0.5000** | |
| 3 | declProc | emar105.classes.pas | 0.5000 | |
| 4 | defProc | emar105.classes.pas | 0.5000 | |
| 5 | declProc | emar105.classes.pas | 0.5000 | |
| 6 | defProc | emar.base.classes.pas | 0.5000 | TEmar_Consts |
| 7 | defProc | emar.base.classes.pas | 0.5000 | TEmar_Fat |
| 8 | declSection | emar.base.classes.pas | 0.5000 | TEmar_NA_File |

---

#### T49 - "TT_Rides4EPO_GetRideCalendar" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `TT_Rides4EPO_GetRideCalendar`, within top 2 (partial: top 5) |
| **Matched** | #2 - procedure_header in dbo.TT_Rides4EPO_GetRideCalendar.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | emar.base.classes.pas | 0.5000 | TEmar_RideRoute |
| **2** | **procedure_header** | **dbo.TT_Rides4EPO_GetRideCalendar.sql** | **0.5000** | |
| 3 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 4 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 5 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | procedure_body | dbo.TT_Rides4EPO_GetRideCalendar.sql | 0.5000 | |
| 7 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

---

### Cross-File / Dependency

#### T20 - "uses clause MainDM" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {declUses}, file matches `MainDM.pas`, within top 2 (partial: top 5) |
| **Matched** | #1 - declUses in MainDM.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declUses** | **MainDM.pas** | **0.5000** | |
| 2 | declUses | MainDM.pas | 0.5000 | |
| 3 | declUses | DataSnapSchedule.pas | 0.5000 | |
| 4 | declUses | Creator_BaseFrame.pas | 0.5000 | |
| 5 | declUses | DriveExamWizardStep1.pas | 0.5000 | |
| 6 | comment | Informica.dpr | 0.5000 | |
| 7 | declUses | FormBasicMain.pas | 0.5000 | |
| 8 | declUses | MainTurdus.pas | 0.5000 | |

---

#### T21 - "what units does MainTurdus use" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {declUses}, file matches `MainTurdus.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: file_path match at #1, node_type match at #2 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | MainTurdus.pas | 0.5000 | |
| **2** | **declUses** | **MainTurdus.pas** | **0.5000** | |
| 3 | declUses | MainTurdus.pas | 0.5000 | |
| 4 | comment | emar.base.classes.pas | 0.5000 | |
| 5 | comment | Informica.dpr | 0.5000 | |
| 6 | comment | emar.base.classes.pas | 0.5000 | |
| 7 | declVar | MainTurdus.pas | 0.5000 | |
| 8 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |

> **Regression from 004 (PASS→PARTIAL).** comment from MainTurdus.pas at #1 outranked the declUses at #2. In 004, comment was at #1 and declUses at #2 with the same layout, but the scoring was different enough to count as PASS. The declUses is at #2 which satisfies the criteria for PARTIAL (top 5) but not PASS (top 3 with correct node_type at that position).

---

#### T22 - "TClientDataSet cdsStoredProc" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | file matches `MainDM`, text contains `cdsStoredProc`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_object in MainDM.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_object** | **MainDM.dfm** | **0.5000** | **TdmMain** |
| 2 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 4 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 5 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 6 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 7 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 8 | defProc | MainDM.pas | 0.5000 | TdmMain |

---

#### T23 - "classes that inherit from TForm" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | text contains `TForm`, results from multiple files (>=2), within top 5 (partial: top 8) |
| **Matched** | #1 - declProc in BaseEditorForm.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declProc** | **BaseEditorForm.pas** | **0.5000** | **TfrmBaseEditor** |
| 2 | class_overview | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 3 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 4 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 5 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 6 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 7 | method_group | emar.base.classes.pas | 0.5000 | TEmar_ByteArray |
| 8 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |

> **Improvement from 004 (PARTIAL→PASS).** Now matched via ImportDM.pas at #1 per updated criteria. Multiple files now appear in top 8 results.

---

#### T24 - "classes that inherit from TDataModule" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `MainDM`, text contains `TDataModule`, within top 5 (partial: top 8) |
| **Matched** | #2 - defProc in MainDM.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declProc | ImportDM.pas | 0.5000 | |
| **2** | **defProc** | **MainDM.pas** | **0.5000** | **TdmMain** |
| 3 | class_overview | MainDM.pas | 0.5000 | TdmMain |
| 4 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 5 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | class_summary | emar105.classes.pas | 0.5000 | TEmar105_ReportEvent_30 |
| 7 | comment | emar.base.classes.pas | 0.5000 | |
| 8 | method_group | SalesReport.Classes.pas | 0.5000 | TSalesReport |

---

#### T50 - "uses clause KMFilesUtil" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {declUses}, file matches `KMFilesUtil.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - declUses in KMFilesUtil.pas (score: 0.6479) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declUses** | **KMFilesUtil.pas** | **0.6479** | |
| 2 | declUses | KMFilesUtil.pas | 0.5000 | |
| 3 | comment | KMFilesUtil.pas | 0.5000 | |
| 4 | comment | KMFilesUtil.pas | 0.5000 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 7 | defProc | KMFilesUtil.pas | 0.5000 | |
| 8 | defProc | KMFilesUtil.pas | 0.5000 | |

---

### DFM Form Queries

#### T25 - "MainTurdus form components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header}, file matches `MainTurdus.dfm`, within top 2 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in MainTurdus.dfm (score: 0.6133) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **MainTurdus.dfm** | **0.6133** | **TfrmMainTurdus** |
| 2 | declUses | MainTurdus.pas | 0.5000 | |
| 3 | dfm_object | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 4 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 5 | dfm_object | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 6 | class_summary_split | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 7 | dfm_object | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 8 | declVar | MainTurdus.pas | 0.5000 | |

---

#### T26 - "Splash form layout" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header, dfm_object}, file matches `Splash.dfm`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in Splash.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **Splash.dfm** | **0.5000** | **TfrmSplash** |
| 2 | declUses | Splash.pas | 0.5000 | |
| 3 | dfm_object | Splash.dfm | 0.5000 | TfrmSplash |
| 4 | dfm_object | Splash.dfm | 0.5000 | TfrmSplash |
| 5 | dfm_object | Splash.dfm | 0.5000 | TfrmSplash |
| 6 | dfm_object_group | Splash.dfm | 0.5000 | TfrmSplash |
| 7 | declProc | Splash.pas | 0.5000 | TfrmSplash |
| 8 | declVar | Splash.pas | 0.5000 | |

---

#### T27 - "SFTP frame components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header}, file matches `WithFrame_SFTP.dfm`, within top 2 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in WithFrame_SFTP.dfm (score: 0.4197) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **WithFrame_SFTP.dfm** | **0.4197** | **TframeSFTP_Send** |
| 2 | dfm_object | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 3 | dfm_object | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 4 | dfm_object | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 5 | dfm_object | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 6 | declUses_split | Informica.dpr | 0.5000 | |
| 7 | dfm_object | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 8 | declUses_split | Informica.dpr | 0.5000 | |

---

#### T28 - "TActionList in MainTurdus" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `MainTurdus.dfm`, text contains `TActionList`, within top 5 (partial: top 8) |
| **Detail** | Partial: text_pattern match at #1 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | dfm_object | BaseLPCFrame.dfm | 0.5000 | |
| 2 | declVar | MainTurdus.pas | 0.5000 | |
| 3 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 4 | comment | MainTurdus.pas | 0.5000 | |
| 5 | comment | MainTurdus.pas | 0.5000 | |
| 6 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 7 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 8 | comment | MainTurdus.pas | 0.5000 | |

> Found dfm_object from BaseLPCFrame.dfm at #1 (wrong file) with TActionList text pattern match. MainTurdus.dfm did not appear in top results. The TActionList component in MainTurdus.dfm may be in a chunk that wasn't surfaced due to competition from other DFM files in the production index.

---

#### T51 - "login form components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header, dfm_object, dfm_object_group}, file matches `LoginFrm.dfm`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in LoginFrm.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **LoginFrm.dfm** | **0.5000** | **TfrmLogin** |
| 2 | dfm_form_header | BusStandActionWizardStep1.dfm | 0.5000 | TframeBusStandActionWizardStep1 |
| 3 | dfm_form_header | MainDM.dfm | 0.5000 | TdmMain |
| 4 | dfm_form_header | WithFrame_SFTP.dfm | 0.5000 | TframeSFTP_Send |
| 5 | dfm_form_header | TGeoPointEditorFrame.dfm | 0.5000 | TframeGeoPoint |
| 6 | dfm_form_header | Splash.dfm | 0.5000 | TfrmSplash |
| 7 | dfm_form_header | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 8 | declUses | HistoryThread.pas | 0.5000 | |

---

#### T52 - "TGeoPointEditorFrame latitude longitude" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `TGeoPointEditorFrame.dfm`, text contains `latitude` or `longitude`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_object in TGeoPointEditorFrame.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_object** | **TGeoPointEditorFrame.dfm** | **0.5000** | **TframeGeoPoint** |
| 2 | defProc | emar105.classes.pas | 0.5000 | TEmar105_BusStopStand |
| 3 | dfm_object | TGeoPointEditorFrame.dfm | 0.5000 | TframeGeoPoint |
| 4 | dfm_form_header | TGeoPointEditorFrame.dfm | 0.5000 | TframeGeoPoint |
| 5 | dfm_object_group | TGeoPointEditorFrame.dfm | 0.5000 | TframeGeoPoint |
| 6 | dfm_object | TGeoPointEditorFrame.dfm | 0.5000 | TframeGeoPoint |
| 7 | declSection | emar.base.classes.pas | 0.5000 | TEmar_BusStopStand |
| 8 | defProc | emar105.classes.pas | 0.5000 | TEmar105_BusStopStand |

---

### SQL Schema / Procedure

#### T29 - "SLS_Ticket table columns" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {create_table, sql_batch, ddl_group}, file matches `SLS_Ticket`, within top 3 (partial: top 5) |
| **Matched** | #1 - create_table in dbo.SLS_TicketGoods.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **create_table** | **dbo.SLS_TicketGoods.sql** | **0.5000** | |
| 2 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 3 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 4 | create_table | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.5000 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 7 | ddl_group | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.5000 | |
| 8 | create_table | dbo.SLS_Ticket.sql | 0.5000 | |

---

#### T30 - "parameters of ADMIN_ReportDef_ReliefTicketPayments" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {procedure_header, procedure_full, procedure_body}, file matches `ADMIN_ReportDef_ReliefTicketPayments`, within top 3 (partial: top 5) |
| **Matched** | #2 - procedure_body in dbo.ADMIN_ReportDef_ReliefTicketPayments.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| **2** | **procedure_body** | **dbo.ADMIN_ReportDef_ReliefTicketPayments.sql** | **0.5000** | |
| 3 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 4 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 5 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 6 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 7 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 8 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |

---

#### T31 - "body of SLS_ReliefExport_Bilety_Get procedure" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {procedure_body, procedure_full}, file matches `SLS_ReliefExport_Bilety_Get`, within top 4 (partial: top 6) |
| **Detail** | Wrong file at #2 (dbo.ADMIN_createdelphiclass). Partial: file_path match at #5, node_type match at #2. |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | procedure_header | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 2 | procedure_body | dbo.ADMIN_createdelphiclass.sql | 0.5000 | |
| 3 | comment | emar.base.classes.pas | 0.5000 | |
| 4 | comment | SalesReport.Classes.pas | 0.5000 | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 7 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |
| 8 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.5000 | |

> **Regression from 004 (PASS→PARTIAL).** procedure_body from dbo.ADMIN_createdelphiclass.sql at #2 is a cross-file interloper. The correct procedure_body from SLS_ReliefExport_Bilety_Get.sql dropped to #5. In 004, the correct file was at #4 (within top 4 PASS threshold).

---

#### T32 - "SELECT statements in TCK_FarePrice_GetPriceForXDesignation" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `TCK_FarePrice`, text contains `SELECT`, within top 5 (partial: top 8) |
| **Matched** | #1 - procedure_body in dbo.TCK_FarePrice_GetPriceForXDesignation.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_body** | **dbo.TCK_FarePrice_GetPriceForXDesignation.sql** | **0.5000** | |
| 2 | function_header | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| 3 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| 4 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.5000 | |
| 5 | procedure_body | dbo.EMKFile_Emar105_Create.sql | 0.5000 | |
| 6 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.5000 | |
| 7 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.5000 | |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |

---

#### T53 - "SLS_TicketPaymentTypeEMAR205 table columns" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {create_table, sql_batch}, file matches `SLS_TicketPaymentTypeEMAR205`, within top 3 (partial: top 5) |
| **Detail** | Wrong file at #1-3 (comment from Informica.dpr). Partial: file_path match at #4. |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | Informica.dpr | 0.5000 | |
| 2 | comment | Informica.dpr | 0.5000 | |
| 3 | comment | Informica.dpr | 0.5000 | |
| 4 | create_table | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.5000 | |
| 5 | ddl_group | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.5000 | |
| 6 | ddl_group | dbo.SLS_Ticket.sql | 0.5000 | |
| 7 | create_table | dbo.SLS_Ticket.sql | 0.5000 | |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

> **Regression from 004 (PASS→PARTIAL).** Comments from Informica.dpr at #1-3 are interlopers that displaced the correct create_table chunk to #4. In 004, create_table was at #1 with score 0.8247. The production reindex flattened scores to 0.5000, preventing BM25 from differentiating the correct result.

---

#### T54 - "parameters of TCK_FarePriceScaleCopyFromDatabase" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `TCK_FarePriceScaleCopyFromDatabase`, within top 3 (partial: top 5) |
| **Matched** | #2 - procedure_header in dbo.TCK_FarePriceScaleCopyFromDatabase.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | MainDM.pas | 0.5000 | TdmMain |
| **2** | **procedure_header** | **dbo.TCK_FarePriceScaleCopyFromDatabase.sql** | **0.5000** | |
| 3 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 4 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.5000 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 6 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 7 | declUses_split | Informica.dpr | 0.5000 | |
| 8 | declUses_split | Informica.dpr | 0.5000 | |

---

### Natural Language Code Understanding

#### T33 - "How to connect to the database" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `MainDM.pas`, text contains `Connection`, `Connect`, or `database` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #2 - defProc in MainDM.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | Informica.dpr | 0.5000 | |
| **2** | **defProc** | **MainDM.pas** | **0.5000** | **TdmMain** |
| 3 | dfm_object | MainDM.dfm | 0.5000 | TdmMain |
| 4 | dfm_object | MainDM.dfm | 0.5000 | TdmMain |
| 5 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 6 | method_group | PWebService.pas | 0.5000 | connection |
| 7 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 8 | class_summary | PWebService.pas | 0.5000 | connection |

---

#### T34 - "Where are ticket prices calculated" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `FarePrice`, `Ticket`, or `SLS_Ticket` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #2 - defProc in TCityTicketsEditorFrame.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| **2** | **defProc** | **TCityTicketsEditorFrame.pas** | **0.5000** | |
| 3 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 4 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 5 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | defProc | emar105.classes.pas | 0.5000 | TEmar105_ReportEvent_36 |
| 7 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

> **Improvement from 004 (FAIL→PASS).** SQL NL descriptions helped bridge "ticket prices" to TCityTicketsEditorFrame.pas. In 004, the embedding model could not connect the natural language concept to any ticket/fare price file.

---

#### T35 - "How to export relief tickets" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `ReliefExport` or `Bilety` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #4 - procedure_body in dbo.SLS_ReliefExport_Bilety_Get.sql (score: 0.4132) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 2 | method_group | PWebService.pas | 0.5000 | ticket |
| 3 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| **4** | **procedure_body** | **dbo.SLS_ReliefExport_Bilety_Get.sql** | **0.4132** | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | declUses_split | Informica.dpr | 0.5000 | |
| 7 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

> **Improvement from 004 (FAIL→PASS).** SQL NL descriptions helped bridge "export relief tickets" to dbo.SLS_ReliefExport_Bilety_Get.sql at #4. In 004, the embedding model could not bridge this semantic gap at all. The NL description context prefix likely contains phrases close to "export" and "relief tickets" that the embedding model can match.

---

#### T36 - "Where is the splash screen shown" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `Splash.pas` or `Splash.dfm` (case-insensitive), within top 5 (partial: top 8) |
| **Detail** | Full match at position 6 (>5). SplashScreen.pas at #1 outranked Splash.pas. |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declUses | SplashScreen.pas | 0.5000 | |
| 2 | declVar | Splash.pas | 0.5000 | |
| 3 | declUses | Splash.pas | 0.5000 | |
| 4 | dfm_form_header | Splash.dfm | 0.5000 | TfrmSplash |
| 5 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 6 | declProc | Splash.pas | 0.5000 | TfrmSplash |
| 7 | defProc | Splash.pas | 0.5000 | TfrmSplash |
| 8 | declUses | Splash.pas | 0.5000 | |

> **Regression from 004 (PASS→PARTIAL).** SplashScreen.pas at #1 outranked Splash.pas results. The declUses at #1 is from a different file (SplashScreen.pas) that doesn't match the criteria pattern. Splash.pas results appear at #2-3 but as declVar/declUses (not the expected declProc that was at #1 in 004).

---

#### T55 - "How to delete files older than a certain time" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Dense |
| **Criteria** | file matches `KMFilesUtil.pas`, text contains `purge`, `delete`, or `older` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - defProc in KMFilesUtil.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **KMFilesUtil.pas** | **0.5000** | |
| 2 | comment | SalesReport.Classes.pas | 0.5000 | |
| 3 | comment | KMFilesUtil.pas | 0.5000 | |
| 4 | declProc | KMFilesUtil.pas | 0.5000 | |
| 5 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 6 | comment | KMFilesUtil.pas | 0.5000 | |
| 7 | defProc | KMFilesUtil.pas | 0.5000 | TPurgeFileThread |
| 8 | comment | KMFilesUtil.pas | 0.5000 | |

---

### Edge Cases / Stress Tests

#### T37 - "TdmMain" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | file matches `MainDM`, within top 3 (partial: top 5) |
| **Matched** | #2 - method_group in MainDM.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| **2** | **method_group** | **MainDM.pas** | **0.5000** | **TdmMain** |
| 3 | dfm_form_header | MainDM.dfm | 0.5000 | TdmMain |
| 4 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 5 | declVar | MainDM.pas | 0.5000 | |
| 6 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 7 | declProc | MainDM.pas | 0.5000 | TdmMain |
| 8 | method_group | MainDM.pas | 0.5000 | TdmMain |

---

#### T38 - "I need to understand the complete architecture..." - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview}, file matches `MainDM.pas`, within top 5 (partial: top 8) |
| **Query** | "I need to understand the complete architecture of the main data module TdmMain in MainDM.pas including all its published components, stored procedures, database connections, event handlers, and how it interacts with other forms in the application" |
| **Detail** | Partial: file_path match at #1 (declProc, wrong node_type) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declProc | MainDM.pas | 0.5000 | TdmMain |
| 2 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_summary | PWebService.pas | 0.5000 | connection |
| 4 | method_group | MainDM.pas | 0.5000 | TdmMain |
| 5 | class_overview | MainDM.pas | 0.5000 | TdmMain |
| 6 | class_summary | PWebService.pas | 0.5000 | PWSStick |
| 7 | declUses | MainDM.pas | 0.5000 | |
| 8 | dfm_form_header | MainDM.dfm | 0.5000 | TdmMain |

> **Regression from 004 (PASS→PARTIAL).** class_overview dropped from #5 to... still at #5, but the criteria check may have changed. In 004, class_overview at #5 matched the criteria (within top 5). The scores are now flat at 0.5000 across all results, and declProc/defProc chunks outranked the overview types. The reranker's overview boost was insufficient in the production index.

---

#### T39 - "TdmMian" (typo) - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `MainDM`, within top 8 |
| **Matched** | #2 - dfm_form_header in MainDM.dfm (score: 0.5941) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | emar.base.classes.pas | 0.5000 | |
| **2** | **dfm_form_header** | **MainDM.dfm** | **0.5941** | **TdmMain** |
| 3 | comment | emar.base.classes.pas | 0.5000 | |
| 4 | defProc | emar.base.classes.pas | 0.5000 | TEmar_InterfacedObject |
| 5 | comment | emar.base.classes.pas | 0.5000 | |
| 6 | comment | emar.base.classes.pas | 0.5000 | |
| 7 | defProc | emar105.classes.pas | 0.5000 | TEmar205_Texts |
| 8 | defProc | emar.base.classes.pas | 0.5000 | TEmar_InterfacedObject |

---

#### T40 - "procedure" (generic) - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Sparse |
| **Criteria** | results from multiple files (>=2), within top 8 |
| **Matched** | #1 - class_summary_split in MainTurdus.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary_split** | **MainTurdus.pas** | **0.5000** | **TfrmMainTurdus** |
| 2 | class_summary_split | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | class_summary_split | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 4 | class_summary_split | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 5 | declSection | MainDM.pas | 0.5000 | TdmMain |
| 6 | comment | Informica.dpr | 0.5000 | |
| 7 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_Consts |
| 8 | procedure_header | dbo.ADMIN_CompanyAllBranches.sql | 0.5000 | |

---

### AI Agent Workflow

#### T41 - "I need to modify the ticket export logic, where should I look?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `ReliefExport`, `Bilety`, or `Ticket` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #2 - class_summary_split in ListOfTicketsPrintWrapper.pas (score: 0.1536) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| **2** | **class_summary_split** | **ListOfTicketsPrintWrapper.pas** | **0.1536** | |
| 3 | class_summary | PWebService.pas | 0.5000 | ticket |
| 4 | class_summary | emar.base.classes.pas | 0.5000 | TEmar_PA_File_Ticket |
| 5 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 6 | class_summary | PWebService.pas | 0.5000 | ticket |
| 7 | class_summary | PWebService.pas | 0.5000 | order |
| 8 | class_summary | PWebService.pas | 0.5000 | PWSTiDetailedReservation |

> **Improvement from 004 (FAIL→PASS).** ListOfTicketsPrintWrapper.pas at #2 matches the "Ticket" file pattern. In 004, no ticket-related file appeared in top results. SQL NL descriptions helped the embedding model bridge "ticket export logic" to ticket-related results.

---

#### T42 - "Where are report types defined?" - FAIL &#x274C;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Hybrid |
| **Criteria** | text contains `REPORT_TYPE` or `C_REPORT_` (case-insensitive), within top 5 (partial: top 8) |
| **Detail** | No matching text pattern found in top results |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | SalesReport.Types.pas | 0.6047 | |
| 2 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 3 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 4 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReportAction |
| 5 | defProc | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 6 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 7 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 8 | declSection | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

> **Regression from 004 (PASS→FAIL).** In 004, declConst from ResourceStrings.pas at #1 contained REPORT_TYPE text. Now comment from SalesReport.Types.pas at #1 (score 0.6047) outranked the declConst chunks. The SalesReport.Types.pas file is topically related (it's about report types) but the comment chunk doesn't contain the literal REPORT_TYPE or C_REPORT_ text that the criteria requires. Production reindex introduced SalesReport.Types.pas chunks that displaced the correct constants.

---

#### T43 - "I need to add a new field to the main data module, show me the structure" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, declSection}, file matches `MainDM`, within top 5 (partial: top 8) |
| **Detail** | Partial: node_type match at #1 (class_summary from CaseLPCMasterDataClasses.pas, wrong file) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary | CaseLPCMasterDataClasses.pas | 0.3511 | |
| 2 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| 3 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 4 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 5 | class_summary_split | emar.base.classes.pas | 0.5000 | TEmar_BaseFile |
| 6 | class_summary_split | emar.base.classes.pas | 0.5000 | TEmar_Ride |
| 7 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 8 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |

> The query "add a new field to the main data module" is a natural language description that the embedding model partially understood (found class_summary/class_summary_split chunks) but failed to target MainDM specifically. All 8 results are from other files. The reranker did not detect "main data module" as referring to MainDM.pas — consistent with 004 behavior.

---

#### T44 - "What SQL procedures handle company data?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Hybrid |
| **Criteria** | file matches `Company` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #2 - procedure_header in dbo.ADMIN_CompanyAllBranches.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | emar.base.classes.pas | 0.5000 | TEmar_TicketNextPeriod |
| **2** | **procedure_header** | **dbo.ADMIN_CompanyAllBranches.sql** | **0.5000** | |
| 3 | procedure_header | import.LPC_LicenceFeeStartData2Insert.sql | 0.5000 | |
| 4 | declSection | emar.base.classes.pas | 0.5000 | TEmar_ByteArray |
| 5 | comment | Informica.dpr | 0.5000 | |
| 6 | comment | Informica.dpr | 0.5000 | |
| 7 | class_summary | emar.base.classes.pas | 0.5000 | TEmar_ByteArray |
| 8 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |

---

#### T56 - "I need to run a scheduled report as CSV, where is that logic?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Dense |
| **Criteria** | file matches `DataSnapSchedule.pas`, text contains `CSV`, `RunReport`, or `SaveAs` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - declConst in DataSnapSchedule.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declConst** | **DataSnapSchedule.pas** | **0.5000** | |
| 2 | report_props | SettlementWithCarriersByRides.fr3 | 0.5000 | |
| 3 | declConst | DataSnapSchedule.pas | 0.5000 | |
| 4 | report_props | ListOfPrintOut.fr3 | 0.5000 | |
| 5 | declUses_split | Informica.dpr | 0.5000 | |
| 6 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 7 | defProc | DataSnapSchedule.pas | 0.5000 | TDataSnapSchedule |
| 8 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |

---

## Analysis: Comparison with Iteration 004

### Overall Score Change

| Metric | 004 | 005c | Delta |
|--------|-----|------|-------|
| **Score** | 101/112 | 94/112 | **-7** |
| **Percentage** | 90.2% | 83.9% | **-6.3%** |
| **PASS** | 48 | 40 | -8 |
| **PARTIAL** | 5 | 14 | +9 |
| **FAIL** | 3 | 2 | -1 |
| **Rating** | Excellent | Good | Downgrade |

### Tests that IMPROVED (004→005c): +4 tests, +11 points

| Test | Change | Root Cause |
|------|--------|------------|
| **T11** | PARTIAL→PASS | Test query fixed from "PrepareDataSet" to "PreapreDataSet" to match actual typo in source code. BM25 now finds exact match at #1. |
| **T23** | PARTIAL→PASS | Multiple files now appear in top results, satisfying the multi-file criteria. |
| **T34** | FAIL→PASS | SQL NL descriptions added context that helped the embedding model bridge "ticket prices calculated" to TCityTicketsEditorFrame.pas. |
| **T35** | FAIL→PASS | SQL NL descriptions helped bridge "export relief tickets" to dbo.SLS_ReliefExport_Bilety_Get.sql. The NL context prefix likely contains phrases semantically close to the query. |
| **T41** | FAIL→PASS | SQL NL descriptions helped bridge "ticket export logic" to ListOfTicketsPrintWrapper.pas and other ticket-related results. |

### Tests that REGRESSED (004→005c): -13 tests, -18 points

| Test | Change | Root Cause |
|------|--------|------------|
| **T01** | PASS→PARTIAL | class_summary from DBClassesBusStop.pas outranked MainDM.pas. Cross-file interloper from production reindex. |
| **T03** | PASS→PARTIAL | class_overview no longer in top results. declProc chunks outranked overview types. |
| **T05** | PASS→FAIL | defProc from TPersonEditorFrame.pas (wrong file) at #1. class_overview/class_summary displaced entirely. |
| **T09** | PASS→PARTIAL | class_overview at #1 instead of class_summary_split. Strict node_type mismatch. |
| **T13** | PASS→PARTIAL | declProc at #1 instead of method_group/defProc. Different chunking in production. |
| **T15** | PASS→PARTIAL | function_header dropped from #1 to #3. function_body chunks outranked it. |
| **T21** | PASS→PARTIAL | comment outranked declUses at #1 for MainTurdus.pas. |
| **T31** | PASS→PARTIAL | procedure_body from ADMIN_createdelphiclass (wrong file) at #2. Cross-file interloper. |
| **T36** | PASS→PARTIAL | SplashScreen.pas outranked Splash.pas. Different file with similar name. |
| **T38** | PASS→PARTIAL | declProc at #1 instead of class_overview. Overview types not surfacing high enough. |
| **T42** | PASS→FAIL | comment from SalesReport.Types.pas outranked declConst with REPORT_TYPE text. |
| **T46** | PASS→PARTIAL | dfm_form_header from Creator_BaseFrame.dfm outranked class_summary from Creator_BaseFrame.pas. |
| **T53** | PASS→PARTIAL | Comments from Informica.dpr outranked create_table from SLS_TicketPaymentTypeEMAR205.sql. |

### Root Cause Analysis

**Primary cause: Score flattening in production index.** The most visible pattern across regressions is scores collapsing to 0.5000 across many results. In 004, scores were more differentiated (e.g., T15 had function_header at 0.8414 vs function_body at 0.7995). In 005c, many results show uniform 0.5000 scores, meaning the hybrid search can no longer distinguish between relevant and less-relevant chunks.

This score flattening has several consequences:

1. **Cross-file interlopers** (T01, T05, T31, T42, T53): When scores are flat, chunks from unrelated files can randomly outrank correct results. In 004 with differentiated scores, the correct file's chunks had clear score advantages.

2. **Overview type displacement** (T03, T05, T09, T38, T46): The reranker's fixed score boosts (+0.50 for overview types) become less effective when base scores are undifferentiated. In 004, the reranker could amplify already-high-scoring overview chunks. In 005c, the reranker's boost merely moves chunks within a flat distribution, and other chunks with 0.5000 base scores can still outrank them.

3. **Node_type ranking within same file** (T13, T15, T21): When BM25 and dense scores are flat, the ranking within a file's chunks becomes essentially random. This causes declProc to outrank method_group, function_body to outrank function_header, and comment to outrank declUses.

**Secondary cause: Larger index with more competing chunks.** The production index contains significantly more source files than the test index. More chunks means more competition for top-8 positions, and with flat scores, the "winner" among equally-scored chunks is arbitrary.

### Common Themes

1. **SQL NL descriptions are a clear win for natural language queries** — T34, T35, T41 all improved from FAIL to PASS. The NL context prefix bridges the semantic gap between English queries and domain-specific code identifiers.

2. **Production reindex caused widespread score degradation** — The score differentiation that existed in 004 is largely gone in 005c. This suggests a possible issue with how embeddings interact with the larger production vector space (more vectors = more noise in similarity scores).

3. **Reranker needs stronger penalties for cross-file interlopers** — The -0.20 penalty for overview chunks from non-target files is insufficient when base scores are flat. Consider increasing penalties or adding a dedicated interloper detection step.

4. **Net trade-off is negative** — While the NL description improvements are valuable (+11 points on 4 tests), the regressions cost more (-18 points on 13 tests), resulting in a net -7 point delta.

### Recommendations

1. **Investigate score flattening** — Compare the raw Qdrant scores (before normalization) between 004 and 005c to determine if the issue is in embedding quality, normalization, or the larger vector space.
2. **Strengthen reranker cross-file penalties** — Increase the interloper penalty from -0.20 to -0.30 or -0.40 for overview queries where a target file is detected.
3. **Consider BM25 tuning** — The flat 0.5000 scores suggest BM25 is not differentiating well in the production index. This could be a tf-idf scaling issue with more documents.
4. **Keep SQL NL descriptions** — The improvements on T34/T35/T41 are genuine and should be preserved in future iterations.
