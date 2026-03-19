-- ============================================================
-- Procedure: dbo.ORD_DispatchExport_Get
-- Description: Returns dispatch export data for a branch and date range.
--              Joins vehicles, job orders, stops, and drivers.
--              Used by the Dispatch Export report and the SFTP export.
-- Parameters:
--   @BranchID    INT           - Branch to export (required)
--   @DateFrom    DATETIME      - Start of period (inclusive)
--   @DateTo      DATETIME      - End of period (inclusive)
--   @JobStatusID INT           - Filter by job status; NULL = all statuses
-- ============================================================

IF OBJECT_ID(N'dbo.ORD_DispatchExport_Get', N'P') IS NOT NULL
    DROP PROCEDURE dbo.ORD_DispatchExport_Get
GO

CREATE PROCEDURE dbo.ORD_DispatchExport_Get
    @BranchID       INT,
    @DateFrom       DATETIME,
    @DateTo         DATETIME,
    @JobStatusID    INT = NULL
AS
BEGIN
    SET NOCOUNT ON

    -- Validate required parameters
    IF @BranchID IS NULL
    BEGIN
        RAISERROR('BranchID is required', 16, 1)
        RETURN
    END

    IF @DateFrom > @DateTo
    BEGIN
        RAISERROR('DateFrom cannot be after DateTo', 16, 1)
        RETURN
    END

    -- Build result set joining all relevant tables
    SELECT
        jo.JobOrderID,
        jo.JobOrderNo,
        b.BranchName,
        v.RegistrationNo                AS VehicleReg,
        v.VehicleType,
        v.MaxPayloadKg,
        d.DriverCode,
        d.FirstName + ' ' + d.LastName  AS DriverName,
        d.LicenceNumber,
        jo.ScheduledDate,
        jo.ActualDepartureDate,
        jo.ActualArrivalDate,
        jo.JobStatusID,
        js.StatusName                   AS JobStatus,
        jo.TotalDistanceKm,
        jo.CargoWeightKg,
        jo.Notes,
        -- First stop (origin)
        orig.Address                    AS OriginAddress,
        orig.ScheduledArrival           AS OriginETA,
        orig.ActualArrival              AS OriginATA,
        -- Last stop (destination)
        dest.Address                    AS DestAddress,
        dest.ScheduledArrival           AS DestETA,
        dest.ActualArrival              AS DestATA,
        jo.CreatedAt,
        jo.ModifiedAt
    FROM
        dbo.ORD_JobOrders jo
        INNER JOIN dbo.Fleet_Branches b
            ON b.BranchID = jo.BranchID
        INNER JOIN dbo.Fleet_Vehicles v
            ON v.VehicleID = jo.VehicleID
        INNER JOIN dbo.HR_Drivers d
            ON d.DriverID = jo.DriverID
        INNER JOIN dbo.ORD_JobStatus js
            ON js.JobStatusID = jo.JobStatusID
        -- Origin: first stop in sequence
        LEFT JOIN dbo.ORD_JobStops orig
            ON orig.JobOrderID = jo.JobOrderID
            AND orig.StopSequence = 1
        -- Destination: last stop in sequence
        LEFT JOIN dbo.ORD_JobStops dest
            ON dest.JobOrderID = jo.JobOrderID
            AND dest.StopSequence = (
                SELECT MAX(s2.StopSequence)
                FROM dbo.ORD_JobStops s2
                WHERE s2.JobOrderID = jo.JobOrderID
            )
    WHERE
        jo.BranchID = @BranchID
        AND jo.ScheduledDate >= @DateFrom
        AND jo.ScheduledDate <= @DateTo
        AND (@JobStatusID IS NULL OR jo.JobStatusID = @JobStatusID)
    ORDER BY
        jo.ScheduledDate,
        jo.JobOrderNo

    SET NOCOUNT OFF
END
GO
