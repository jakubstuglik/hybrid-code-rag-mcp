# RAG Validation Results - Production Index

**Date:** 2026-03-11  
**Config:** production  
**Hybrid Alpha:** 0.5  
**Total Tests:** 56  
**Rating:** Excellent

---

## Summary

| Metric | Value |
|--------|-------|
| **Score** | **101 / 112** |
| **Percentage** | **90.2%** |
| **PASS** | 48 |
| **PARTIAL** | 5 |
| **FAIL** | 3 |

---

## Category Summary

| Category | Tests | PASS | PARTIAL | FAIL | Pass Rate |
|----------|-------|------|---------|------|-----------|
| Class Overview Queries | 11 | 10 | 1 | 0 | 91% |
| Precise Identifier Search | 12 | 11 | 1 | 0 | 92% |
| Cross-File / Dependency | 6 | 5 | 1 | 0 | 83% |
| DFM Form Queries | 7 | 6 | 1 | 0 | 86% |
| SQL Schema / Procedure | 6 | 6 | 0 | 0 | 100% |
| Natural Language Code Understanding | 5 | 3 | 0 | 2 | 60% |
| Edge Cases / Stress Tests | 4 | 4 | 0 | 0 | 100% |
| AI Agent Workflow | 5 | 3 | 1 | 1 | 60% |

---

## Detailed Results by Category

### Class Overview Queries

#### T01 - "What is TdmMain?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview}, file matches `MainDM.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary_split in MainDM.pas (score: 0.2145) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary_split** | **MainDM.pas** | **0.2145** | **TdmMain** |
| 2 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 3 | dfm_form_header | MainDM.dfm | 0.7436 | TdmMain |
| 4 | method_group | MainDM.pas | 0.6946 | TdmMain |
| 5 | class_summary_split | SalesReport.Classes.pas | 0.3635 | TSalesReport |
| 6 | method_group | MainDM.pas | 0.6087 | TdmMain |
| 7 | method_group | MainDM.pas | 0.5023 | TdmMain |
| 8 | method_group | MainDM.pas | 0.4930 | TdmMain |

---

#### T02 - "What classes are in emar105.classes.pas?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_overview}, file matches `emar105`, within top 2 (partial: top 5) |
| **Matched** | #1 - class_summary in emar105.classes.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **emar105.classes.pas** | **0.5000** | **TEmar105_ExchangeRateAfterChangeCurrencyList** |
| 2 | class_summary | emar105.classes.pas | 0.3327 | TEmar105_AcceptedTradeReliefCardOwnerList |
| 3 | class_summary | emar105.classes.pas | 0.2935 | TEmar105_Driver |
| 4 | class_summary | emar105.classes.pas | 0.1851 | TEmar105_DriverList |
| 5 | declUses | emar105.classes.pas | 0.3758 | |
| 6 | declUses | emar105.classes.pas | 0.3471 | |
| 7 | declClass | emar105.classes.pas | 0.5323 | TEmar105_Driver |
| 8 | declClass | emar105.classes.pas | 0.5000 | TEmar105_ExchangeRateAfterChangeCurrencyList |

---

#### T03 - "What is TfrmMainTurdus?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `MainTurdus.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_overview in MainTurdus.pas (score: 0.1181) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_overview** | **MainTurdus.pas** | **0.1181** | **TfrmMainTurdus** |
| 2 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | method_group | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 4 | declProc | MainTurdus.pas | 0.4477 | TfrmMainTurdus |
| 5 | dfm_form_header | MainTurdus.dfm | 0.4267 | TfrmMainTurdus |
| 6 | declVar | MainTurdus.pas | 0.4632 | |
| 7 | declProc | MainTurdus.pas | 0.2952 | TfrmMainTurdus |
| 8 | defProc | MainTurdus.pas | 0.2315 | TfrmMainTurdus |

---

#### T04 - "Describe TfrmSplash" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `Splash.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in Splash.pas (score: 0.7400) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **Splash.pas** | **0.7400** | **TfrmSplash** |
| 2 | dfm_form_header | Splash.dfm | 0.9129 | TfrmSplash |
| 3 | defProc | Splash.pas | 0.8154 | TfrmSplash |
| 4 | method_group | Splash.pas | 0.7394 | TfrmSplash |
| 5 | declProc | Splash.pas | 0.7357 | TfrmSplash |
| 6 | dfm_object | Splash.dfm | 0.6392 | TfrmSplash |
| 7 | declVar | Splash.pas | 0.8010 | |
| 8 | declProc | Splash.pas | 0.6420 | TfrmSplash |

---

#### T05 - "What does TfrmBaseEditor do?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `BaseEditorForm.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_overview in BaseEditorForm.pas (score: 0.5284) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_overview** | **BaseEditorForm.pas** | **0.5284** | **TfrmBaseEditor** |
| 2 | class_summary_split | BaseEditorForm.pas | 0.3995 | TfrmBaseEditor |
| 3 | class_summary_split | BaseEditorForm.pas | 0.3037 | TfrmBaseEditor |
| 4 | declProc | BaseEditorForm.pas | 0.9022 | TfrmBaseEditor |
| 5 | class_summary_split | BaseEditorForm.pas | 0.1503 | TfrmBaseEditor |
| 6 | declProc | BaseEditorForm.pas | 0.8318 | TfrmBaseEditor |
| 7 | class_summary_split | BaseEditorForm.pas | 0.1231 | TfrmBaseEditor |
| 8 | class_summary_split | BaseEditorForm.pas | 0.0804 | TfrmBaseEditor |

---

#### T06 - "How does TBasicMainForm work?" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary, class_summary_split}, file matches `FormBasicMain.pas`, within top 3 (partial: top 5) |
| **Detail** | Partial: file_path match at #1, node_type match at #4 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | method_group | FormBasicMain.pas | 0.5315 | TBasicMainForm |
| 2 | method_group | FormBasicMain.pas | 0.5300 | TBasicMainForm |
| 3 | declProc | FormBasicMain.pas | 0.4883 | TBasicMainForm |
| 4 | class_overview | MainTurdus.pas | 0.1704 | TfrmMainTurdus |
| 5 | declVar | FormBasicMain.pas | 0.5374 | |
| 6 | defProc | FormBasicMain.pas | 0.3552 | TBasicMainForm |
| 7 | defProc | FormBasicMain.pas | 0.3225 | TBasicMainForm |
| 8 | defProc | FormBasicMain.pas | 0.3185 | TBasicMainForm |

> Right file found at #1 but wrong node_type (method_group instead of class_overview/class_summary). The class_overview appeared at #4 but for the wrong file (MainTurdus.pas). Reranker did not boost the correct overview chunk.

---

#### T07 - "Tell me about TSalesReport" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `SalesReport`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in SalesReport.Classes.pas (score: 0.3028) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **SalesReport.Classes.pas** | **0.3028** | **TSalesReport** |
| 2 | class_summary | SalesReport.Classes.pas | 0.1523 | TSalesReportList |
| 3 | class_summary_split | SalesReport.Classes.pas | 0.1032 | TSalesReport |
| 4 | method_group | SalesReport.Classes.pas | 0.5848 | TSalesReport |
| 5 | method_group | SalesReport.Classes.pas | 0.4947 | TSalesReport |
| 6 | method_group | SalesReport.Classes.pas | 0.4919 | TSalesReport |
| 7 | method_group | SalesReport.Classes.pas | 0.4590 | TSalesReport |
| 8 | defProc | SalesReport.Classes.pas | 0.4484 | TSalesReport |

---

#### T08 - "Overview of TEmar105_OIK class" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_overview, class_summary}, file matches `emar105`, class_name matches `TEmar105_OIK`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in emar105.classes.pas (score: 0.9509) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **emar105.classes.pas** | **0.9509** | **TEmar105_OIK** |
| 2 | class_summary_split | emar105.classes.pas | 0.7190 | TEmar105_OIK |
| 3 | class_overview | emar105.classes.pas | 0.6824 | TEmar105_OIK |
| 4 | class_summary_split | emar105.classes.pas | 0.4527 | TEmar105_OIK |
| 5 | class_summary_split | emar105.classes.pas | 0.3898 | TEmar105_OIK |
| 6 | class_summary_split | emar105.classes.pas | 0.3319 | TEmar105_OIK |
| 7 | method_group | emar105.classes.pas | 0.9810 | TEmar105_OIK |
| 8 | declClass | emar105.classes.pas | 0.9143 | TEmar105_OIK |

---

#### T09 - "What fields does TdmMain have?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, declSection}, file matches `MainDM.pas`, within top 3 (partial: top 5) |
| **Matched** | #2 - class_summary_split in MainDM.pas (score: 0.3600) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_overview | MainDM.pas | 0.6083 | TdmMain |
| **2** | **class_summary_split** | **MainDM.pas** | **0.3600** | **TdmMain** |
| 3 | class_summary_split | MainDM.pas | 0.0517 | TdmMain |
| 4 | dfm_form_header | MainDM.dfm | 0.5644 | TdmMain |
| 5 | class_overview | SalesReport.Classes.pas | 0.2065 | TSalesReport |
| 6 | class_summary_split | SalesReport.Classes.pas | 0.1412 | TSalesReport |
| 7 | class_summary_split | SalesReport.Classes.pas | 0.1003 | TSalesReport |
| 8 | method_group | MainDM.pas | 0.2748 | TdmMain |

---

#### T45 - "What is TDataSnapSchedule?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, class_overview_split}, file matches `DataSnapSchedule.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in DataSnapSchedule.pas (score: 0.4530) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **DataSnapSchedule.pas** | **0.4530** | **TDataSnapSchedule** |
| 2 | defProc | DataSnapSchedule.pas | 0.8640 | TDataSnapSchedule |
| 3 | defProc | DataSnapSchedule.pas | 0.7548 | TDataSnapSchedule |
| 4 | defProc | DataSnapSchedule.pas | 0.7278 | TDataSnapSchedule |
| 5 | defProc | DataSnapSchedule.pas | 0.6430 | TDataSnapSchedule |
| 6 | declSection | DataSnapSchedule.pas | 0.5938 | TDataSnapSchedule |
| 7 | defProc | DataSnapSchedule.pas | 0.5903 | TDataSnapSchedule |
| 8 | defProc | DataSnapSchedule.pas | 0.5627 | TDataSnapSchedule |

---

#### T46 - "Describe TframeBaseCreator" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, class_overview_split}, file matches `Creator_BaseFrame.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - class_summary in Creator_BaseFrame.pas (score: 0.1760) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **class_summary** | **Creator_BaseFrame.pas** | **0.1760** | **TframeBaseCreator** |
| 2 | method_group | Creator_BaseFrame.pas | 0.7441 | TframeBaseCreator |
| 3 | method_group | Creator_BaseFrame.pas | 0.6630 | TframeBaseCreator |
| 4 | method_group | Creator_BaseFrame.pas | 0.6340 | TframeBaseCreator |
| 5 | method_group | Creator_BaseFrame.pas | 0.6299 | TframeBaseCreator |
| 6 | defProc | Creator_BaseFrame.pas | 0.5780 | TframeBaseCreator |
| 7 | defProc | Creator_BaseFrame.pas | 0.5776 | TframeBaseCreator |
| 8 | defProc | Creator_BaseFrame.pas | 0.5682 | TframeBaseCreator |

---

### Precise Identifier Search

#### T10 - "REPORT_TYPE_PUNCTUALITY_RIDES" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | file matches `.pas`, text contains `REPORT_TYPE_PUNCTUALITY_RIDES`, within top 2 (partial: top 5) |
| **Matched** | #1 - defProc in MainTurdus.pas (score: 1.3756) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **MainTurdus.pas** | **1.3756** | **TfrmMainTurdus** |
| 2 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | declConst | ResourceStrings.pas | 0.1054 | |
| 4 | declConst | ResourceStrings.pas | 0.0573 | |
| 5 | declConst | ResourceStrings.pas | 0.0215 | |
| 6 | declConst | ResourceStrings.pas | 0.0064 | |
| 7 | declConst | ResourceStrings.pas | 0.0020 | |
| 8 | declConst | ResourceStrings.pas | 0.0000 | |

---

#### T11 - "PrepareDataSet" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split, method_group}, text contains `PrepareDataSet`, within top 2 (partial: top 5) |
| **Detail** | Partial: node_type match at #1 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | MainDM.pas | 0.5741 | TdmMain |
| 2 | defProc | MainDM.pas | 0.5683 | TdmMain |
| 3 | defProc | MainDM.pas | 0.4743 | TdmMain |
| 4 | defProc | MainDM.pas | 0.4714 | TdmMain |
| 5 | defProc | MainDM.pas | 0.4584 | TdmMain |
| 6 | class_summary_split | MainDM.pas | 0.4488 | TdmMain |
| 7 | defProc | MainDM.pas | 0.4465 | TdmMain |
| 8 | class_summary_split | MainDM.pas | 0.4422 | TdmMain |

> Found defProc chunks from MainDM.pas at #1, but the text_pattern `PrepareDataSet` was not confirmed in the top result. The dense embedding found related code but the specific method may be in a different defProc chunk. Multiple similar-scoring defProc chunks suggest BM25 couldn't distinguish which one contains the exact identifier.

---

#### T12 - "OpenConnection" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split}, file matches `MainDM.pas`, text contains `OpenConnection`, within top 2 (partial: top 5) |
| **Matched** | #1 - defProc in MainDM.pas (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **MainDM.pas** | **1.0000** | **TdmMain** |
| 2 | dfm_object | MainDM.dfm | 0.2126 | TdmMain |
| 3 | class_overview | MainDM.pas | 0.1881 | TdmMain |
| 4 | class_summary_split | MainDM.pas | 0.1294 | TdmMain |
| 5 | dfm_object | MainDM.dfm | 0.0783 | TdmMain |
| 6 | class_summary | PWebService.pas | 0.0749 | connection2 |
| 7 | comment | Informica.dpr | 0.0732 | |
| 8 | class_summary | PWebService.pas | 0.0386 | connection |

---

#### T13 - "GetCardSerialNumber" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | node_type in {method_group, method_group_split, defProc}, file matches `emar`, text contains `GetCardSerialNumber`, within top 4 (partial: top 6) |
| **Matched** | #3 - method_group in emar105.classes.pas (score: 0.3825) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | emar105.classes.pas | 0.5000 | TEmar105_File |
| 2 | class_summary_split | emar105.classes.pas | 0.5000 | TEmar105_OIK |
| **3** | **method_group** | **emar105.classes.pas** | **0.3825** | **TEmar105_OIK** |
| 4 | class_summary_split | emar105.classes.pas | 0.2999 | TEmar105_OIK |
| 5 | class_summary_split | emar105.classes.pas | 0.2805 | TEmar105_OIK |
| 6 | declSection | emar105.classes.pas | 0.1505 | TEmar105_OIK |
| 7 | defProc | MainDM.pas | 0.0683 | TdmMain |
| 8 | method_group | emar.base.classes.pas | 0.0630 | TEmar_ProprietaryMIFAREcard |

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
| 3 | comment | SalesReport.Classes.pas | 0.4973 | |
| 4 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2831 | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2831 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2700 | |
| 7 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2446 | |
| 8 | defProc | SalesReport.Classes.pas | 0.1032 | TSalesReport |

---

#### T15 - "TCK_FarePrice_GetPriceForXDesignation" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {function_header, function_full, procedure_header}, file matches `TCK_FarePrice`, within top 2 (partial: top 5) |
| **Matched** | #1 - function_header in dbo.TCK_FarePrice_GetPriceForXDesignation.sql (score: 0.8414) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **function_header** | **dbo.TCK_FarePrice_GetPriceForXDesignation.sql** | **0.8414** | |
| 2 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.7995 | |
| 3 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.2218 | |
| 4 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.2124 | |
| 5 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.1646 | |
| 6 | defProc_split | SalesReport.Classes.pas | 0.0034 | TSalesReportEmar105 |
| 7 | defProc_split | SalesReport.Classes.pas | 0.0005 | TSalesReport |
| 8 | method_group | emar.base.classes.pas | 0.0000 | TEmar_CityTariffPrice |

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
| 3 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.4960 | |
| 4 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.4213 | |
| 5 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.3774 | |
| 6 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.3765 | |
| 7 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.3373 | |
| 8 | procedure_body | ADMIN_ReportDef_AnalysisRoute.sql | 0.3290 | |

---

#### T17 - "ADMIN_CompanyAllBranches" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `ADMIN_CompanyAllBranches`, within top 3 (partial: top 5) |
| **Matched** | #1 - procedure_header in dbo.ADMIN_CompanyAllBranches.sql (score: 0.8925) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_header** | **dbo.ADMIN_CompanyAllBranches.sql** | **0.8925** | |
| 2 | procedure_body | dbo.ADMIN_CompanyAllBranches.sql | 0.5113 | |
| 3 | procedure_body | dbo.ADMIN_CompanyAllBranches.sql | 0.4361 | |
| 4 | comment | emar.base.classes.pas | 0.0111 | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.0089 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.0079 | |
| 7 | declConst | ResourceStrings.pas | 0.0047 | |
| 8 | declConst | ResourceStrings.pas | 0.0000 | |

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
| 3 | declProc | Licence.pas | 0.4711 | IXMLTprivilage |
| 4 | defProc | emar.base.classes.pas | 0.4639 | TEmar_ReportEvent |
| 5 | declConst | ResourceStrings.pas | 0.1581 | |
| 6 | declConst | ResourceStrings.pas | 0.1118 | |
| 7 | declConst | ResourceStrings.pas | 0.0913 | |
| 8 | declConst | ResourceStrings.pas | 0.0585 | |

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
| 2 | declConst | SalesReport.Classes.pas | 0.6222 | |
| 3 | declConst | SalesReport.Classes.pas | 0.6207 | |
| 4 | declConst | SalesReport.Classes.pas | 0.6131 | |
| 5 | comment | SalesReport.Classes.pas | 0.6084 | |
| 6 | declConst | ResourceStrings.pas | 0.5917 | |
| 7 | declConst | SalesReport.Classes.pas | 0.5852 | |
| 8 | declConst | ResourceStrings.pas | 0.5771 | |

---

#### T47 - "FindFiles" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {defProc, defProc_split, declProc}, file matches `KMFilesUtil.pas`, text contains `FindFiles`, within top 3 (partial: top 5) |
| **Matched** | #1 - declProc in KMFilesUtil.pas (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declProc** | **KMFilesUtil.pas** | **1.0000** | |
| 2 | defProc | KMFilesUtil.pas | 0.6571 | |
| 3 | declType | KMFilesUtil.pas | 0.1861 | |
| 4 | defProc | KMFilesUtil.pas | 0.1431 | |
| 5 | defProc | KMFilesUtil.pas | 0.0297 | |
| 6 | comment | KMFilesUtil.pas | 0.0082 | |
| 7 | comment | KMFilesUtil.pas | 0.0082 | |
| 8 | declType | KMFilesUtil.pas | 0.0000 | |

---

#### T48 - "EMKFile_Emar105_Create" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `EMKFile_Emar105_Create`, within top 2 (partial: top 5) |
| **Matched** | #1 - procedure_header in dbo.EMKFile_Emar105_Create.sql (score: 0.6127) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_header** | **dbo.EMKFile_Emar105_Create.sql** | **0.6127** | |
| 2 | defProc | emar105.classes.pas | 0.5000 | |
| 3 | declProc | emar105.classes.pas | 0.2837 | |
| 4 | defProc | emar105.classes.pas | 0.1496 | |
| 5 | declProc | emar105.classes.pas | 0.0763 | |
| 6 | defProc | emar.base.classes.pas | 0.0707 | TEmar_Consts |
| 7 | defProc | emar.base.classes.pas | 0.0547 | TEmar_Fat |
| 8 | declSection | emar.base.classes.pas | 0.0000 | TEmar_NA_File |

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
| 3 | defProc_split | SalesReport.Classes.pas | 0.4599 | TSalesReportEmar105 |
| 4 | defProc | SalesReport.Classes.pas | 0.3603 | TSalesReport |
| 5 | defProc_split | SalesReport.Classes.pas | 0.3250 | TSalesReportEmar105 |
| 6 | procedure_body | dbo.TT_Rides4EPO_GetRideCalendar.sql | 0.2178 | |
| 7 | defProc_split | SalesReport.Classes.pas | 0.1252 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.0233 | TSalesReportEmar105 |

---

### Cross-File / Dependency

#### T20 - "uses clause MainDM" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {declUses}, file matches `MainDM.pas`, within top 2 (partial: top 5) |
| **Matched** | #1 - declUses in MainDM.pas (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declUses** | **MainDM.pas** | **1.0000** | |
| 2 | declUses | MainDM.pas | 0.6179 | |
| 3 | declUses | DataSnapSchedule.pas | 0.3655 | |
| 4 | declUses | Creator_BaseFrame.pas | 0.3553 | |
| 5 | declUses | DriveExamWizardStep1.pas | 0.3157 | |
| 6 | comment | Informica.dpr | 0.3114 | |
| 7 | declUses | FormBasicMain.pas | 0.3109 | |
| 8 | declUses | MainTurdus.pas | 0.1558 | |

---

#### T21 - "what units does MainTurdus use" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {declUses}, file matches `MainTurdus.pas`, within top 3 (partial: top 5) |
| **Matched** | #2 - declUses in MainTurdus.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | MainTurdus.pas | 0.5000 | |
| **2** | **declUses** | **MainTurdus.pas** | **0.5000** | |
| 3 | declUses | MainTurdus.pas | 0.4876 | |
| 4 | comment | emar.base.classes.pas | 0.2674 | |
| 5 | comment | Informica.dpr | 0.1731 | |
| 6 | comment | emar.base.classes.pas | 0.1583 | |
| 7 | declVar | MainTurdus.pas | 0.0851 | |
| 8 | declProc | MainTurdus.pas | 0.0268 | TfrmMainTurdus |

---

#### T22 - "TClientDataSet cdsStoredProc" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Sparse |
| **Criteria** | file matches `MainDM`, text contains `cdsStoredProc`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_object_group in MainDM.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_object_group** | **MainDM.dfm** | **0.5000** | **TdmMain** |
| 2 | class_summary_split | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_summary_split | MainDM.pas | 0.4929 | TdmMain |
| 4 | defProc | DataSnapSchedule.pas | 0.3104 | TDataSnapSchedule |
| 5 | defProc | MainDM.pas | 0.2902 | TdmMain |
| 6 | class_summary_split | MainDM.pas | 0.2327 | TdmMain |
| 7 | defProc | MainDM.pas | 0.2170 | TdmMain |
| 8 | defProc | MainDM.pas | 0.1924 | TdmMain |

---

#### T23 - "classes that inherit from TForm" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | text contains `TForm`, results from multiple files (>=2), within top 5 (partial: top 8) |
| **Detail** | Only 1 file matched (need >=2): {'BaseEditorForm.pas'} |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | declProc | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 2 | class_overview | BaseEditorForm.pas | 0.5000 | TfrmBaseEditor |
| 3 | declProc | BaseEditorForm.pas | 0.3585 | TfrmBaseEditor |
| 4 | method_group | SalesReport.Classes.pas | 0.2029 | TSalesReportEmar105 |
| 5 | declProc | BaseEditorForm.pas | 0.1359 | TfrmBaseEditor |
| 6 | method_group | SalesReport.Classes.pas | 0.1349 | TSalesReport |
| 7 | method_group | emar.base.classes.pas | 0.1117 | TEmar_ByteArray |
| 8 | declProc | BaseEditorForm.pas | 0.0969 | TfrmBaseEditor |

> Multi-file query expected results from >=2 files containing "TForm". Only BaseEditorForm.pas appeared. Other forms (Splash, MainTurdus) inherit from TForm but their chunks don't contain the literal string "TForm" prominently enough for hybrid search to surface them.

---

#### T24 - "classes that inherit from TDataModule" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `MainDM`, text contains `TDataModule`, within top 5 (partial: top 8) |
| **Matched** | #1 - declProc in MainDM.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declProc** | **MainDM.pas** | **0.5000** | **TdmMain** |
| 2 | defProc | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_overview | MainDM.pas | 0.4141 | TdmMain |
| 4 | method_group | MainDM.pas | 0.1286 | TdmMain |
| 5 | method_group | SalesReport.Classes.pas | 0.0670 | TSalesReportEmar105 |
| 6 | class_summary | emar105.classes.pas | 0.0575 | TEmar105_ReportEvent_30 |
| 7 | comment | emar.base.classes.pas | 0.0569 | |
| 8 | method_group | SalesReport.Classes.pas | 0.0436 | TSalesReport |

---

#### T50 - "uses clause KMFilesUtil" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {declUses}, file matches `KMFilesUtil.pas`, within top 3 (partial: top 5) |
| **Matched** | #1 - declUses in KMFilesUtil.pas (score: 0.8731) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declUses** | **KMFilesUtil.pas** | **0.8731** | |
| 2 | declUses | KMFilesUtil.pas | 0.8480 | |
| 3 | comment | KMFilesUtil.pas | 0.5000 | |
| 4 | comment | KMFilesUtil.pas | 0.4296 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.3287 | TSalesReportEmar105 |
| 6 | declUses | SalesReport.Classes.pas | 0.2628 | |
| 7 | defProc | KMFilesUtil.pas | 0.2475 | |
| 8 | defProc | KMFilesUtil.pas | 0.1118 | |

---

### DFM Form Queries

#### T25 - "MainTurdus form components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header}, file matches `MainTurdus.dfm`, within top 2 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in MainTurdus.dfm (score: 0.7335) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **MainTurdus.dfm** | **0.7335** | **TfrmMainTurdus** |
| 2 | declUses | MainTurdus.pas | 0.4668 | |
| 3 | dfm_object | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 4 | declProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 5 | dfm_object | MainTurdus.dfm | 0.3915 | TfrmMainTurdus |
| 6 | class_summary_split | MainTurdus.pas | 0.2380 | TfrmMainTurdus |
| 7 | dfm_object | MainTurdus.dfm | 0.3207 | TfrmMainTurdus |
| 8 | declVar | MainTurdus.pas | 0.3464 | |

---

#### T26 - "Splash form layout" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header, dfm_object}, file matches `Splash.dfm`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in Splash.dfm (score: 0.8574) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **Splash.dfm** | **0.8574** | **TfrmSplash** |
| 2 | declUses | Splash.pas | 0.6099 | |
| 3 | dfm_object | Splash.dfm | 0.4676 | TfrmSplash |
| 4 | dfm_object | Splash.dfm | 0.4115 | TfrmSplash |
| 5 | dfm_object | Splash.dfm | 0.4038 | TfrmSplash |
| 6 | dfm_object_group | Splash.dfm | 0.3108 | TfrmSplash |
| 7 | declProc | Splash.pas | 0.2859 | TfrmSplash |
| 8 | declVar | Splash.pas | 0.1988 | |

---

#### T27 - "SFTP frame components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header}, file matches `WithFrame_SFTP.dfm`, within top 2 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in WithFrame_SFTP.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **WithFrame_SFTP.dfm** | **0.5000** | **TframeSFTP_Send** |
| 2 | dfm_object | WithFrame_SFTP.dfm | 0.4769 | TframeSFTP_Send |
| 3 | dfm_object | WithFrame_SFTP.dfm | 0.4159 | TframeSFTP_Send |
| 4 | dfm_object | WithFrame_SFTP.dfm | 0.3519 | TframeSFTP_Send |
| 5 | dfm_object | WithFrame_SFTP.dfm | 0.2998 | TframeSFTP_Send |
| 6 | declUses_split | Informica.dpr | 0.4120 | |
| 7 | dfm_object | WithFrame_SFTP.dfm | 0.2561 | TframeSFTP_Send |
| 8 | declUses_split | Informica.dpr | 0.3925 | |

---

#### T28 - "TActionList in MainTurdus" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `MainTurdus.dfm`, text contains `TActionList`, within top 5 (partial: top 8) |
| **Detail** | Partial: file_path match at #1 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | dfm_object | MainTurdus.dfm | 0.5000 | TfrmMainTurdus |
| 2 | declVar | MainTurdus.pas | 0.5000 | |
| 3 | defProc | MainTurdus.pas | 0.3386 | TfrmMainTurdus |
| 4 | comment | MainTurdus.pas | 0.3151 | |
| 5 | comment | MainTurdus.pas | 0.3151 | |
| 6 | defProc | MainTurdus.pas | 0.2540 | TfrmMainTurdus |
| 7 | defProc | MainTurdus.pas | 0.0412 | TfrmMainTurdus |
| 8 | comment | MainTurdus.pas | 0.0261 | |

> Found a dfm_object from MainTurdus.dfm at #1, but the text_pattern `TActionList` was not confirmed in the matched chunk. The TActionList component may be in a different DFM chunk or grouped into a dfm_object_group that wasn't surfaced.

---

#### T51 - "login form components" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Reranker |
| **Criteria** | node_type in {dfm_form_header, dfm_object, dfm_object_group}, file matches `LoginFrm.dfm`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in LoginFrm.dfm (score: 0.8634) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **LoginFrm.dfm** | **0.8634** | **TfrmLogin** |
| 2 | dfm_form_header | BusStandActionWizardStep1.dfm | 0.4185 | TframeBusStandActionWizardStep1 |
| 3 | dfm_form_header | MainDM.dfm | 0.4152 | TdmMain |
| 4 | dfm_form_header | WithFrame_SFTP.dfm | 0.4152 | TframeSFTP_Send |
| 5 | dfm_form_header | TGeoPointEditorFrame.dfm | 0.4070 | TframeGeoPoint |
| 6 | dfm_form_header | Splash.dfm | 0.4043 | TfrmSplash |
| 7 | dfm_form_header | MainTurdus.dfm | 0.3837 | TfrmMainTurdus |
| 8 | declUses | HistoryThread.pas | 0.4270 | |

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
| 3 | dfm_object | TGeoPointEditorFrame.dfm | 0.4818 | TframeGeoPoint |
| 4 | dfm_form_header | TGeoPointEditorFrame.dfm | 0.4306 | TframeGeoPoint |
| 5 | dfm_object_group | TGeoPointEditorFrame.dfm | 0.4219 | TframeGeoPoint |
| 6 | dfm_object | TGeoPointEditorFrame.dfm | 0.3376 | TframeGeoPoint |
| 7 | declSection | emar.base.classes.pas | 0.3073 | TEmar_BusStopStand |
| 8 | defProc | emar105.classes.pas | 0.2637 | TEmar105_BusStopStand |

---

### SQL Schema / Procedure

#### T29 - "SLS_Ticket table columns" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {create_table, sql_batch, ddl_group}, file matches `SLS_Ticket`, within top 3 (partial: top 5) |
| **Matched** | #1 - ddl_group in dbo.SLS_Ticket.sql (score: 0.6823) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **ddl_group** | **dbo.SLS_Ticket.sql** | **0.6823** | |
| 2 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 3 | defProc_split | SalesReport.Classes.pas | 0.3284 | TSalesReportEmar105 |
| 4 | create_table | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.3162 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.2914 | TSalesReportEmar105 |
| 6 | defProc_split | SalesReport.Classes.pas | 0.2859 | TSalesReportEmar105 |
| 7 | ddl_group | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.2369 | |
| 8 | create_table | dbo.SLS_Ticket.sql | 0.1314 | |

---

#### T30 - "parameters of ADMIN_ReportDef_ReliefTicketPayments" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {procedure_header, procedure_full, procedure_body}, file matches `ADMIN_ReportDef_ReliefTicketPayments`, within top 3 (partial: top 5) |
| **Matched** | #1 - procedure_body in dbo.ADMIN_ReportDef_ReliefTicketPayments.sql (score: 0.8795) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_body** | **dbo.ADMIN_ReportDef_ReliefTicketPayments.sql** | **0.8795** | |
| 2 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.6658 | |
| 3 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.3948 | |
| 4 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.3816 | |
| 5 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.3214 | |
| 6 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.1658 | |
| 7 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.0632 | |
| 8 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.0453 | |

---

#### T31 - "body of SLS_ReliefExport_Bilety_Get procedure" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | node_type in {procedure_body, procedure_full}, file matches `SLS_ReliefExport_Bilety_Get`, within top 4 (partial: top 6) |
| **Matched** | #4 - procedure_body in dbo.SLS_ReliefExport_Bilety_Get.sql (score: 0.2831) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | procedure_header | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.7747 | |
| 2 | comment | emar.base.classes.pas | 0.5000 | |
| 3 | comment | SalesReport.Classes.pas | 0.4857 | |
| **4** | **procedure_body** | **dbo.SLS_ReliefExport_Bilety_Get.sql** | **0.2831** | |
| 5 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2831 | |
| 6 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2700 | |
| 7 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.2446 | |
| 8 | procedure_body | dbo.SLS_ReliefExport_Bilety_Get.sql | 0.0885 | |

---

#### T32 - "SELECT statements in TCK_FarePrice_GetPriceForXDesignation" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Hybrid |
| **Criteria** | file matches `TCK_FarePrice`, text contains `SELECT`, within top 5 (partial: top 8) |
| **Matched** | #1 - function_body in dbo.TCK_FarePrice_GetPriceForXDesignation.sql (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **function_body** | **dbo.TCK_FarePrice_GetPriceForXDesignation.sql** | **1.0000** | |
| 2 | function_header | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.2471 | |
| 3 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.2307 | |
| 4 | function_body | dbo.TCK_FarePrice_GetPriceForXDesignation.sql | 0.2170 | |
| 5 | procedure_body | dbo.EMKFile_Emar105_Create.sql | 0.1515 | |
| 6 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.1420 | |
| 7 | procedure_body | dbo.ADMIN_ReportDef_ReliefTicketPayments.sql | 0.1393 | |
| 8 | defProc_split | SalesReport.Classes.pas | 0.0584 | TSalesReport |

---

#### T53 - "SLS_TicketPaymentTypeEMAR205 table columns" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {create_table, sql_batch}, file matches `SLS_TicketPaymentTypeEMAR205`, within top 3 (partial: top 5) |
| **Matched** | #1 - create_table in dbo.SLS_TicketPaymentTypeEMAR205.sql (score: 0.8247) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **create_table** | **dbo.SLS_TicketPaymentTypeEMAR205.sql** | **0.8247** | |
| 2 | ddl_group | dbo.SLS_TicketPaymentTypeEMAR205.sql | 0.8225 | |
| 3 | ddl_group | dbo.SLS_Ticket.sql | 0.3340 | |
| 4 | create_table | dbo.SLS_Ticket.sql | 0.1713 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.1121 | TSalesReportEmar105 |
| 6 | defProc_split | SalesReport.Classes.pas | 0.0919 | TSalesReportEmar105 |
| 7 | defProc | DataSnapSchedule.pas | 0.0740 | TDataSnapSchedule |
| 8 | defProc | HistoryThread.pas | 0.0295 | THistoryThread |

---

#### T54 - "parameters of TCK_FarePriceScaleCopyFromDatabase" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | node_type in {procedure_header, procedure_full, sql_batch}, file matches `TCK_FarePriceScaleCopyFromDatabase`, within top 3 (partial: top 5) |
| **Matched** | #1 - procedure_header in dbo.TCK_FarePriceScaleCopyFromDatabase.sql (score: 1.0000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_header** | **dbo.TCK_FarePriceScaleCopyFromDatabase.sql** | **1.0000** | |
| 2 | defProc | MainDM.pas | 0.2334 | TdmMain |
| 3 | defProc_split | SalesReport.Classes.pas | 0.1654 | TSalesReport |
| 4 | procedure_body | dbo.TCK_FarePriceScaleCopyFromDatabase.sql | 0.0635 | |
| 5 | defProc_split | SalesReport.Classes.pas | 0.0572 | TSalesReport |
| 6 | defProc | DataSnapSchedule.pas | 0.0397 | TDataSnapSchedule |
| 7 | declUses_split | Informica.dpr | 0.0333 | |
| 8 | declUses_split | Informica.dpr | 0.0297 | |

---

### Natural Language Code Understanding

#### T33 - "How to connect to the database" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `MainDM.pas`, text contains `Connection`, `Connect`, or `database` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #5 - defProc in MainDM.pas (score: 0.1551) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | Informica.dpr | 1.0000 | |
| 2 | comment | Informica.dpr | 0.9391 | |
| 3 | dfm_object | MainDM.dfm | 0.2667 | TdmMain |
| 4 | dfm_object | MainDM.dfm | 0.2426 | TdmMain |
| **5** | **defProc** | **MainDM.pas** | **0.1551** | **TdmMain** |
| 6 | method_group | PWebService.pas | 0.1158 | connection |
| 7 | defProc | MainDM.pas | 0.0748 | TdmMain |
| 8 | class_summary | PWebService.pas | 0.0699 | connection |

---

#### T34 - "Where are ticket prices calculated" - FAIL &#x274C;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `FarePrice`, `Ticket`, or `SLS_Ticket` (case-insensitive), within top 5 (partial: top 8) |
| **Detail** | No matching nodes found in top results |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 2 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 3 | defProc_split | SalesReport.Classes.pas | 0.4057 | TSalesReportEmar105 |
| 4 | defProc | SalesReport.Classes.pas | 0.3956 | TSalesReportEmar105 |
| 5 | defProc | emar105.classes.pas | 0.3643 | TEmar105_ReportEvent_36 |
| 6 | defProc_split | SalesReport.Classes.pas | 0.3150 | TSalesReportEmar105 |
| 7 | defProc_split | SalesReport.Classes.pas | 0.2644 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.1256 | TSalesReportEmar105 |

> Dense embedding failed to connect the natural language concept "ticket prices calculated" to the actual files `dbo.TCK_FarePrice_GetPriceForXDesignation.sql` or `dbo.SLS_Ticket.sql`. The embedding model lacks domain knowledge to bridge "ticket prices" to "FarePrice" or "SLS_Ticket". All results came from SalesReport.Classes.pas which is tangentially related.

---

#### T35 - "How to export relief tickets" - FAIL &#x274C;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `ReliefExport` or `Bilety` (case-insensitive), within top 5 (partial: top 8) |
| **Detail** | No matching nodes found in top results |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc_split | SalesReport.Classes.pas | 0.5000 | TSalesReportEmar105 |
| 2 | method_group | PWebService.pas | 0.5000 | ticket |
| 3 | defProc_split | SalesReport.Classes.pas | 0.4807 | TSalesReportEmar105 |
| 4 | defProc_split | SalesReport.Classes.pas | 0.4232 | TSalesReportEmar105 |
| 5 | defProc_split | SalesReport.Classes.pas | 0.4152 | TSalesReportEmar105 |
| 6 | declUses_split | Informica.dpr | 0.3389 | |
| 7 | defProc_split | SalesReport.Classes.pas | 0.3189 | TSalesReportEmar105 |
| 8 | defProc_split | SalesReport.Classes.pas | 0.2495 | TSalesReportEmar105 |

> Dense embedding could not bridge "export relief tickets" to the file `dbo.SLS_ReliefExport_Bilety_Get.sql`. The Polish word "Bilety" (tickets) and domain-specific naming convention make this a hard semantic gap. BM25 couldn't help either since no chunk contains the exact phrase "export relief tickets".

---

#### T36 - "Where is the splash screen shown" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `Splash.pas` or `Splash.dfm` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - declProc in Splash.pas (score: 0.6798) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declProc** | **Splash.pas** | **0.6798** | **TfrmSplash** |
| 2 | declVar | Splash.pas | 0.5715 | |
| 3 | declUses | Splash.pas | 0.5656 | |
| 4 | dfm_form_header | Splash.dfm | 0.5000 | TfrmSplash |
| 5 | defProc | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 6 | declProc | Splash.pas | 0.4905 | TfrmSplash |
| 7 | defProc | Splash.pas | 0.4093 | TfrmSplash |
| 8 | declUses | Splash.pas | 0.3192 | |

---

#### T55 - "How to delete files older than a certain time" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Dense |
| **Criteria** | file matches `KMFilesUtil.pas`, text contains `purge`, `delete`, or `older` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #2 - defProc in KMFilesUtil.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | comment | SalesReport.Classes.pas | 0.6369 | |
| **2** | **defProc** | **KMFilesUtil.pas** | **0.5000** | |
| 3 | comment | KMFilesUtil.pas | 0.4871 | |
| 4 | declProc | KMFilesUtil.pas | 0.4754 | |
| 5 | defProc | SalesReport.Classes.pas | 0.4375 | TSalesReport |
| 6 | comment | KMFilesUtil.pas | 0.3610 | |
| 7 | defProc | KMFilesUtil.pas | 0.3531 | TPurgeFileThread |
| 8 | comment | KMFilesUtil.pas | 0.3244 | |

---

### Edge Cases / Stress Tests

#### T37 - "TdmMain" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Easy |
| **Aspect** | Sparse |
| **Criteria** | file matches `MainDM`, within top 3 (partial: top 5) |
| **Matched** | #1 - dfm_form_header in MainDM.dfm (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **MainDM.dfm** | **0.5000** | **TdmMain** |
| 2 | class_summary_split | SalesReport.Classes.pas | 0.5000 | TSalesReport |
| 3 | method_group | MainDM.pas | 0.3522 | TdmMain |
| 4 | method_group | MainDM.pas | 0.3414 | TdmMain |
| 5 | declVar | MainDM.pas | 0.2856 | |
| 6 | method_group | MainDM.pas | 0.2729 | TdmMain |
| 7 | declProc | MainDM.pas | 0.2674 | TdmMain |
| 8 | method_group | MainDM.pas | 0.2432 | TdmMain |

---

#### T38 - "I need to understand the complete architecture..." - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview}, file matches `MainDM.pas`, within top 5 (partial: top 8) |
| **Query** | "I need to understand the complete architecture of the main data module TdmMain in MainDM.pas including all its published components, stored procedures, database connections, event handlers, and how it interacts with other forms in the application" |
| **Matched** | #5 - class_overview in MainDM.pas (score: 0.2403) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | defProc | MainDM.pas | 0.6354 | TdmMain |
| 2 | declProc | MainDM.pas | 0.5000 | TdmMain |
| 3 | class_summary | PWebService.pas | 0.2941 | connection |
| 4 | method_group | MainDM.pas | 0.2481 | TdmMain |
| **5** | **class_overview** | **MainDM.pas** | **0.2403** | **TdmMain** |
| 6 | class_summary | PWebService.pas | 0.1636 | PWSStick |
| 7 | declUses | MainDM.pas | 0.1592 | |
| 8 | dfm_form_header | MainDM.dfm | 0.1168 | TdmMain |

---

#### T39 - "TdmMian" (typo) - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `MainDM`, within top 8 |
| **Matched** | #1 - dfm_form_header in MainDM.dfm (score: 0.5424) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **dfm_form_header** | **MainDM.dfm** | **0.5424** | **TdmMain** |
| 2 | comment | emar.base.classes.pas | 0.4765 | |
| 3 | comment | emar.base.classes.pas | 0.4764 | |
| 4 | defProc | emar.base.classes.pas | 0.4696 | TEmar_InterfacedObject |
| 5 | comment | emar.base.classes.pas | 0.4628 | |
| 6 | comment | emar.base.classes.pas | 0.4628 | |
| 7 | defProc | emar105.classes.pas | 0.4625 | TEmar205_Texts |
| 8 | defProc | emar.base.classes.pas | 0.4538 | TEmar_InterfacedObject |

---

#### T40 - "procedure" (generic) - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Sparse |
| **Criteria** | results from multiple files (>=2), within top 8 |
| **Matched** | #1 - pascal_script in SettlementWithCarriersByRides.fr3 (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **pascal_script** | **SettlementWithCarriersByRides.fr3** | **0.5000** | |
| 2 | class_summary_split | MainTurdus.pas | 0.5000 | TfrmMainTurdus |
| 3 | class_summary_split | MainTurdus.pas | 0.3781 | TfrmMainTurdus |
| 4 | class_summary_split | MainTurdus.pas | 0.3684 | TfrmMainTurdus |
| 5 | declSection | MainDM.pas | 0.2878 | TdmMain |
| 6 | comment | Informica.dpr | 0.2348 | |
| 7 | class_summary_split | emar105.classes.pas | 0.2139 | TEmar105_Consts |
| 8 | procedure_header | dbo.ADMIN_CompanyAllBranches.sql | 0.0883 | |

---

### AI Agent Workflow

#### T41 - "I need to modify the ticket export logic, where should I look?" - FAIL &#x274C;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Dense |
| **Criteria** | file matches `ReliefExport`, `Bilety`, or `Ticket` (case-insensitive), within top 5 (partial: top 8) |
| **Detail** | No matching nodes found in top results |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | SalesReport.Classes.pas | 0.2685 | TSalesReportEmar105 |
| 2 | procedure_body | dbo.EMKFile_Emar105_Create.sql | 0.9122 | |
| 3 | class_summary | PWebService.pas | 0.2599 | ticket |
| 4 | class_summary | emar.base.classes.pas | 0.2582 | TEmar_PA_File_Ticket |
| 5 | class_summary_split | SalesReport.Classes.pas | 0.2202 | TSalesReport |
| 6 | class_summary | PWebService.pas | 0.1930 | ticket |
| 7 | class_summary | PWebService.pas | 0.1654 | order |
| 8 | class_summary | PWebService.pas | 0.1421 | PWSTiDetailedReservation |

> Similar to T35 -- dense embedding cannot bridge "ticket export logic" to `dbo.SLS_ReliefExport_Bilety_Get.sql`. The results show ticket-related classes from PWebService.pas (class_name: "ticket") but these are WSDL proxy classes, not the actual export logic. The domain-specific naming convention (Polish "Bilety" = tickets, "Relief" = a specific fare type) is opaque to the embedding model.

---

#### T42 - "Where are report types defined?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Hybrid |
| **Criteria** | text contains `REPORT_TYPE` or `C_REPORT_` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - declConst in ResourceStrings.pas (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **declConst** | **ResourceStrings.pas** | **0.5000** | |
| 2 | declUses | SalesReport.Classes.pas | 0.5000 | |
| 3 | declUses | SalesReport.Classes.pas | 0.4343 | |
| 4 | defProc | SalesReport.Classes.pas | 0.3107 | TSalesReportAction |
| 5 | defProc | SalesReport.Classes.pas | 0.2283 | TSalesReportEmar105 |
| 6 | class_summary_split | MainDM.pas | 0.1735 | TdmMain |
| 7 | defProc_split | SalesReport.Classes.pas | 0.1718 | TSalesReportEmar105 |
| 8 | declSection | SalesReport.Classes.pas | 0.1516 | TSalesReportEmar105 |

---

#### T43 - "I need to add a new field to the main data module, show me the structure" - PARTIAL &#x26A0;&#xFE0F;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Reranker |
| **Criteria** | node_type in {class_summary, class_summary_split, class_overview, declSection}, file matches `MainDM`, within top 5 (partial: top 8) |
| **Detail** | Partial: node_type match at #1 |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| 1 | class_summary_split | SalesReport.Classes.pas | 0.4487 | TSalesReport |
| 2 | class_summary_split | emar105.classes.pas | 0.4073 | TEmar105_OIK |
| 3 | class_summary_split | SalesReport.Classes.pas | 0.3641 | TSalesReport |
| 4 | class_summary_split | SalesReport.Classes.pas | 0.3165 | TSalesReport |
| 5 | class_summary_split | emar.base.classes.pas | 0.2866 | TEmar_BaseFile |
| 6 | class_summary_split | emar.base.classes.pas | 0.2864 | TEmar_Ride |
| 7 | class_summary_split | SalesReport.Classes.pas | 0.2597 | TSalesReport |
| 8 | class_summary_split | SalesReport.Classes.pas | 0.2582 | TSalesReport |

> The query "add a new field to the main data module" is a natural language description that the embedding model partially understood (found class_summary_split chunks) but failed to target MainDM specifically. All 8 results are class_summary_split chunks from other files. The reranker did not detect "main data module" as referring to MainDM.pas.

---

#### T44 - "What SQL procedures handle company data?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Hard |
| **Aspect** | Hybrid |
| **Criteria** | file matches `Company` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - procedure_header in dbo.ADMIN_CompanyAllBranches.sql (score: 0.5000) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **procedure_header** | **dbo.ADMIN_CompanyAllBranches.sql** | **0.5000** | |
| 2 | class_summary_split | emar.base.classes.pas | 0.5000 | TEmar_TicketNextPeriod |
| 3 | procedure_header | import.LPC_LicenceFeeStartData2Insert.sql | 0.4188 | |
| 4 | declSection | emar.base.classes.pas | 0.3711 | TEmar_ByteArray |
| 5 | comment | Informica.dpr | 0.3567 | |
| 6 | comment | Informica.dpr | 0.2442 | |
| 7 | class_summary | emar.base.classes.pas | 0.2307 | TEmar_ByteArray |
| 8 | defProc | MainTurdus.pas | 0.1838 | TfrmMainTurdus |

---

#### T56 - "I need to run a scheduled report as CSV, where is that logic?" - PASS &#x2705;

| | |
|---|---|
| **Difficulty** | Medium |
| **Aspect** | Dense |
| **Criteria** | file matches `DataSnapSchedule.pas`, text contains `CSV`, `RunReport`, or `SaveAs` (case-insensitive), within top 5 (partial: top 8) |
| **Matched** | #1 - defProc in DataSnapSchedule.pas (score: 0.7141) |

| # | node_type | file | score | class_name |
|---|-----------|------|-------|------------|
| **1** | **defProc** | **DataSnapSchedule.pas** | **0.7141** | **TDataSnapSchedule** |
| 2 | report_props | SettlementWithCarriersByRides.fr3 | 0.5118 | |
| 3 | declConst | DataSnapSchedule.pas | 0.5000 | |
| 4 | report_props | ListOfPrintOut.fr3 | 0.5000 | |
| 5 | declUses_split | Informica.dpr | 0.3038 | |
| 6 | class_summary_split | SalesReport.Classes.pas | 0.1752 | TSalesReport |
| 7 | defProc | DataSnapSchedule.pas | 0.1382 | TDataSnapSchedule |
| 8 | defProc_split | SalesReport.Classes.pas | 0.1337 | TSalesReportEmar105 |

---

## Analysis: PARTIAL and FAIL Results

### PARTIAL Results (5 tests)

| Test | Query | Root Cause |
|------|-------|------------|
| **T06** | "How does TBasicMainForm work?" | **Reranker gap**: FormBasicMain.pas doesn't have a class_overview/class_summary chunk surfacing in top 3. Method_group chunks dominated. The reranker boost for overview types wasn't enough to overcome the raw hybrid scores. |
| **T11** | "PrepareDataSet" | **BM25 ambiguity**: Multiple defProc chunks from MainDM.pas scored similarly. The specific chunk containing "PrepareDataSet" wasn't confirmed as the #1 result. Dense embeddings couldn't differentiate between method implementations in the same class. |
| **T23** | "classes that inherit from TForm" | **Multi-file coverage**: Only BaseEditorForm.pas appeared with TForm references. Other form units (Splash, MainTurdus) inherit from TForm but the literal string doesn't appear prominently in their chunks since class_overview uses the parent class name. |
| **T28** | "TActionList in MainTurdus" | **Specific component search**: Found MainTurdus.dfm at #1 but couldn't confirm the TActionList text pattern. The TActionList may be in a dfm_object chunk that wasn't in the top 8, or grouped into a larger chunk where it's diluted. |
| **T43** | "...add a new field to the main data module..." | **Target identification**: Reranker failed to identify "main data module" as referring to MainDM.pas. The natural language description was too indirect -- all results were class_summary_split chunks from other files. |

### FAIL Results (3 tests)

| Test | Query | Root Cause |
|------|-------|------------|
| **T34** | "Where are ticket prices calculated" | **Semantic gap**: The embedding model cannot bridge "ticket prices" to `TCK_FarePrice` or `SLS_Ticket`. These are domain-specific naming conventions that require business knowledge the model doesn't have. |
| **T35** | "How to export relief tickets" | **Domain vocabulary**: "Bilety" is Polish for "tickets" and "ReliefExport" is a domain compound. The embedding model has no way to connect English natural language to these mixed-language identifiers. |
| **T41** | "...modify the ticket export logic..." | **Same as T35**: The concept "ticket export" cannot be resolved to `SLS_ReliefExport_Bilety_Get` by the embedding model. The PWebService.pas "ticket" class appeared but is a WSDL proxy, not the export logic. |

### Common Theme

All 3 FAILs are **dense embedding limitations** on Hard difficulty queries requiring domain-specific vocabulary bridging. The embedding model (jinaai/jina-embeddings-v2-base-code) doesn't understand the project's mixed Polish/English naming conventions. These queries would succeed with exact identifier search (e.g., "SLS_ReliefExport_Bilety_Get") but fail when phrased as natural language questions.

**Potential mitigations:**
- Add synonym/alias metadata to chunks (e.g., "ticket export" -> "SLS_ReliefExport_Bilety_Get")
- Improve context prefix with English descriptions of what procedures do
- Use a multi-step retrieval: first find related identifiers, then search for them
