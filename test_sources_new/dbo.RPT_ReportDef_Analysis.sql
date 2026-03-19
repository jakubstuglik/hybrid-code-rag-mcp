-- ============================================================
-- Procedure: dbo.RPT_ReportDef_Analysis
-- Description: Returns a summary of report definitions — their
--              schedule frequency, last run status, and failure count.
--              Used by the administration dashboard.
-- ============================================================

IF OBJECT_ID(N'dbo.RPT_ReportDef_Analysis', N'P') IS NOT NULL
    DROP PROCEDURE dbo.RPT_ReportDef_Analysis
GO

CREATE PROCEDURE dbo.RPT_ReportDef_Analysis
    @BranchID   INT = NULL,
    @IsActive   BIT = NULL
AS
BEGIN
    SET NOCOUNT ON

    SELECT
        rd.ReportDefID,
        rd.ReportName,
        rd.ReportType,
        rd.ScheduleType,
        rd.OutputFormat,
        rd.IsActive,
        b.BranchName,
        -- Run statistics
        COUNT(rl.RunLogID)                      AS TotalRuns,
        SUM(CASE WHEN rl.Success = 1 THEN 1 ELSE 0 END) AS SuccessfulRuns,
        SUM(CASE WHEN rl.Success = 0 THEN 1 ELSE 0 END) AS FailedRuns,
        MAX(rl.RunDateTime)                     AS LastRunAt,
        -- Last run outcome
        (
            SELECT TOP 1 rl2.Success
            FROM dbo.RPT_ReportRunLog rl2
            WHERE rl2.ReportDefID = rd.ReportDefID
            ORDER BY rl2.RunDateTime DESC
        )                                       AS LastRunSuccess,
        (
            SELECT TOP 1 rl2.ErrorMessage
            FROM dbo.RPT_ReportRunLog rl2
            WHERE rl2.ReportDefID = rd.ReportDefID
              AND rl2.Success = 0
            ORDER BY rl2.RunDateTime DESC
        )                                       AS LastErrorMessage,
        rd.CreatedAt,
        rd.ModifiedAt
    FROM
        dbo.RPT_ReportDef rd
        LEFT JOIN dbo.Fleet_Branches b
            ON b.BranchID = rd.BranchID
        LEFT JOIN dbo.RPT_ReportRunLog rl
            ON rl.ReportDefID = rd.ReportDefID
    WHERE
        (@BranchID IS NULL OR rd.BranchID = @BranchID)
        AND (@IsActive IS NULL OR rd.IsActive = @IsActive)
    GROUP BY
        rd.ReportDefID, rd.ReportName, rd.ReportType, rd.ScheduleType,
        rd.OutputFormat, rd.IsActive, b.BranchName, rd.CreatedAt, rd.ModifiedAt
    ORDER BY
        rd.ReportName

    SET NOCOUNT OFF
END
GO
