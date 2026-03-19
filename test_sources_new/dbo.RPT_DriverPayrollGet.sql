-- ============================================================
-- Function: dbo.RPT_DriverPayrollGet
-- Description: Table-valued function that calculates driver payroll
--              for a given period based on completed trips.
--              Returns one row per trip with earned amount.
-- Parameters:
--   @DriverID    INT      - Driver to calculate payroll for
--   @PeriodFrom  DATE     - Start of payroll period (inclusive)
--   @PeriodTo    DATE     - End of payroll period (inclusive)
-- Returns:
--   Table with trip details and computed pay amounts
-- ============================================================

IF OBJECT_ID(N'dbo.RPT_DriverPayrollGet', N'TF') IS NOT NULL
    DROP FUNCTION dbo.RPT_DriverPayrollGet
GO

CREATE FUNCTION dbo.RPT_DriverPayrollGet
(
    @DriverID   INT,
    @PeriodFrom DATE,
    @PeriodTo   DATE
)
RETURNS TABLE
AS
RETURN
(
    SELECT
        jo.JobOrderID,
        jo.JobOrderNo,
        d.DriverCode,
        d.FirstName + ' ' + d.LastName          AS DriverName,
        d.PayRatePerKm,
        d.PayRatePerHour,
        CAST(jo.ScheduledDate AS DATE)           AS TripDate,
        v.RegistrationNo                         AS VehicleReg,
        jo.TotalDistanceKm,
        jo.ActualDurationMinutes,
        -- Distance-based pay
        ISNULL(jo.TotalDistanceKm, 0)
            * ISNULL(d.PayRatePerKm, 0)          AS DistancePay,
        -- Hourly pay
        ISNULL(jo.ActualDurationMinutes, 0) / 60.0
            * ISNULL(d.PayRatePerHour, 0)        AS HourlyPay,
        -- Total earned for this trip
        (ISNULL(jo.TotalDistanceKm, 0) * ISNULL(d.PayRatePerKm, 0))
            + (ISNULL(jo.ActualDurationMinutes, 0) / 60.0
               * ISNULL(d.PayRatePerHour, 0))    AS TotalEarned,
        jo.JobStatusID,
        js.StatusName                            AS JobStatus
    FROM
        dbo.ORD_JobOrders jo
        INNER JOIN dbo.HR_Drivers d
            ON d.DriverID = jo.DriverID
        INNER JOIN dbo.Fleet_Vehicles v
            ON v.VehicleID = jo.VehicleID
        INNER JOIN dbo.ORD_JobStatus js
            ON js.JobStatusID = jo.JobStatusID
    WHERE
        jo.DriverID = @DriverID
        AND CAST(jo.ScheduledDate AS DATE) BETWEEN @PeriodFrom AND @PeriodTo
        AND jo.JobStatusID = 3  -- Completed only
)
GO
