-- ============================================================
-- Procedure: dbo.VEH_ServiceRecord_GetCalendar
-- Description: Returns vehicle service records formatted as a calendar
--              view for a given month. Includes overdue and upcoming
--              service events. Used by the service calendar widget.
-- Parameters:
--   @VehicleID  INT   - Filter to specific vehicle; NULL = all vehicles
--   @Year       INT   - Calendar year
--   @Month      INT   - Calendar month (1-12)
-- ============================================================

IF OBJECT_ID(N'dbo.VEH_ServiceRecord_GetCalendar', N'P') IS NOT NULL
    DROP PROCEDURE dbo.VEH_ServiceRecord_GetCalendar
GO

CREATE PROCEDURE dbo.VEH_ServiceRecord_GetCalendar
    @VehicleID  INT = NULL,
    @Year       INT = NULL,
    @Month      INT = NULL
AS
BEGIN
    SET NOCOUNT ON

    -- Default to current month
    IF @Year IS NULL  SET @Year  = YEAR(GETDATE())
    IF @Month IS NULL SET @Month = MONTH(GETDATE())

    DECLARE @PeriodStart DATE = DATEFROMPARTS(@Year, @Month, 1)
    DECLARE @PeriodEnd   DATE = EOMONTH(@PeriodStart)

    -- Extend window: show overdue (30 days before) and upcoming (30 days after)
    DECLARE @WindowStart DATE = DATEADD(DAY, -30, @PeriodStart)
    DECLARE @WindowEnd   DATE = DATEADD(DAY, 30, @PeriodEnd)

    SELECT
        sr.ServiceRecordID,
        sr.VehicleID,
        v.RegistrationNo,
        v.VehicleType,
        v.Make + ' ' + v.Model          AS VehicleDescription,
        b.BranchName,
        st.ServiceTypeName,
        st.IsRecurring,
        st.RecurrenceKm,
        st.RecurrenceDays,
        sr.ScheduledDate,
        sr.CompletedDate,
        sr.OdometerAtService,
        sr.NextServiceOdometerKm,
        sr.NextServiceDate,
        sr.ServiceProviderName,
        sr.CostAmount,
        sr.Notes,
        -- Calendar classification
        CASE
            WHEN sr.CompletedDate IS NOT NULL
                THEN 'COMPLETED'
            WHEN sr.ScheduledDate < CAST(GETDATE() AS DATE)
                THEN 'OVERDUE'
            WHEN sr.ScheduledDate BETWEEN @PeriodStart AND @PeriodEnd
                THEN 'THIS_MONTH'
            WHEN sr.ScheduledDate > @PeriodEnd
                THEN 'UPCOMING'
            ELSE 'PAST_WINDOW'
        END                             AS CalendarStatus,
        -- Days until/since scheduled
        DATEDIFF(DAY, CAST(GETDATE() AS DATE), sr.ScheduledDate) AS DaysUntilScheduled,
        -- Km until next service
        ISNULL(sr.NextServiceOdometerKm, 0) - ISNULL(v.OdometerKm, 0) AS KmUntilNextService
    FROM
        dbo.VEH_ServiceRecords sr
        INNER JOIN dbo.Fleet_Vehicles v
            ON v.VehicleID = sr.VehicleID
        INNER JOIN dbo.Fleet_Branches b
            ON b.BranchID = v.BranchID
        INNER JOIN dbo.VEH_ServiceTypes st
            ON st.ServiceTypeID = sr.ServiceTypeID
    WHERE
        (@VehicleID IS NULL OR sr.VehicleID = @VehicleID)
        AND (
            -- Completed this month
            (sr.CompletedDate BETWEEN @PeriodStart AND @PeriodEnd)
            OR
            -- Scheduled within window
            (sr.ScheduledDate BETWEEN @WindowStart AND @WindowEnd)
            OR
            -- Upcoming next service date in window
            (sr.NextServiceDate IS NOT NULL
             AND sr.NextServiceDate BETWEEN @WindowStart AND @WindowEnd)
        )
    ORDER BY
        sr.ScheduledDate,
        v.RegistrationNo

    SET NOCOUNT OFF
END
GO
