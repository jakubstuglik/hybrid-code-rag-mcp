-- ============================================================
-- Procedure: dbo.ADMIN_ReportDef_PayrollSummary
-- Description: Returns a payroll summary report definition, aggregating
--              driver earnings by branch and period.
--              Used by the Payroll Summary scheduled report.
-- ============================================================

IF OBJECT_ID(N'dbo.ADMIN_ReportDef_PayrollSummary', N'P') IS NOT NULL
    DROP PROCEDURE dbo.ADMIN_ReportDef_PayrollSummary
GO

CREATE PROCEDURE dbo.ADMIN_ReportDef_PayrollSummary
    @BranchID   INT     = NULL,
    @PeriodFrom DATE    = NULL,
    @PeriodTo   DATE    = NULL
AS
BEGIN
    SET NOCOUNT ON

    -- Default to current month if not specified
    IF @PeriodFrom IS NULL
        SET @PeriodFrom = DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1)

    IF @PeriodTo IS NULL
        SET @PeriodTo = EOMONTH(GETDATE())

    SELECT
        b.BranchID,
        b.BranchName,
        d.DriverID,
        d.DriverCode,
        d.FirstName + ' ' + d.LastName          AS DriverName,
        d.PayRatePerKm,
        d.PayRatePerHour,
        COUNT(jo.JobOrderID)                     AS TripCount,
        SUM(ISNULL(jo.TotalDistanceKm, 0))       AS TotalDistanceKm,
        SUM(ISNULL(jo.ActualDurationMinutes, 0)) AS TotalDurationMin,
        -- Distance-based earnings
        SUM(ISNULL(jo.TotalDistanceKm, 0)
            * ISNULL(d.PayRatePerKm, 0))         AS DistanceEarnings,
        -- Hourly earnings
        SUM(ISNULL(jo.ActualDurationMinutes, 0) / 60.0
            * ISNULL(d.PayRatePerHour, 0))       AS HourlyEarnings,
        -- Total gross
        SUM(
            (ISNULL(jo.TotalDistanceKm, 0) * ISNULL(d.PayRatePerKm, 0))
            + (ISNULL(jo.ActualDurationMinutes, 0) / 60.0
               * ISNULL(d.PayRatePerHour, 0))
        )                                        AS TotalGrossEarnings
    FROM
        dbo.HR_Drivers d
        INNER JOIN dbo.Fleet_Branches b
            ON b.BranchID = d.BranchID
        LEFT JOIN dbo.ORD_JobOrders jo
            ON jo.DriverID = d.DriverID
            AND CAST(jo.ScheduledDate AS DATE) BETWEEN @PeriodFrom AND @PeriodTo
            AND jo.JobStatusID = 3  -- Completed
    WHERE
        d.IsActive = 1
        AND (@BranchID IS NULL OR d.BranchID = @BranchID)
    GROUP BY
        b.BranchID, b.BranchName,
        d.DriverID, d.DriverCode, d.FirstName, d.LastName,
        d.PayRatePerKm, d.PayRatePerHour
    ORDER BY
        b.BranchName, d.LastName, d.FirstName

    SET NOCOUNT OFF
END
GO
