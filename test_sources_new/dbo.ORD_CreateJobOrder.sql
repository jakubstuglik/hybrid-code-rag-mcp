-- ============================================================
-- Procedure: dbo.ORD_CreateJobOrder
-- Description: Creates a new job order and returns its ID.
--              Validates driver/vehicle availability before insert.
--              Wraps the operation in a transaction.
-- Parameters:
--   @BranchID       INT           - Branch creating the order
--   @DriverID       INT           - Assigned driver
--   @VehicleID      INT           - Assigned vehicle
--   @ScheduledDate  DATETIME      - Planned departure
--   @CargoWeightKg  DECIMAL(10,2) - Cargo weight
--   @Notes          NVARCHAR(500) - Optional notes
--   @JobOrderID     INT OUTPUT    - Returns the new JobOrderID
-- ============================================================

IF OBJECT_ID(N'dbo.ORD_CreateJobOrder', N'P') IS NOT NULL
    DROP PROCEDURE dbo.ORD_CreateJobOrder
GO

CREATE PROCEDURE dbo.ORD_CreateJobOrder
    @BranchID       INT,
    @DriverID       INT,
    @VehicleID      INT,
    @ScheduledDate  DATETIME,
    @CargoWeightKg  DECIMAL(10,2)   = NULL,
    @Notes          NVARCHAR(500)   = NULL,
    @JobOrderID     INT             OUTPUT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @NewJobOrderNo NVARCHAR(20)
    DECLARE @ErrorMsg      NVARCHAR(500)

    -- Validate vehicle exists and is active
    IF NOT EXISTS (
        SELECT 1 FROM dbo.Fleet_Vehicles
        WHERE VehicleID = @VehicleID AND IsActive = 1
    )
    BEGIN
        SET @ErrorMsg = 'Vehicle ID ' + CAST(@VehicleID AS NVARCHAR) + ' not found or inactive'
        RAISERROR(@ErrorMsg, 16, 1)
        RETURN
    END

    -- Validate driver exists and is active
    IF NOT EXISTS (
        SELECT 1 FROM dbo.HR_Drivers
        WHERE DriverID = @DriverID AND IsActive = 1
    )
    BEGIN
        SET @ErrorMsg = 'Driver ID ' + CAST(@DriverID AS NVARCHAR) + ' not found or inactive'
        RAISERROR(@ErrorMsg, 16, 1)
        RETURN
    END

    -- Check vehicle is not already dispatched on the same day
    IF EXISTS (
        SELECT 1 FROM dbo.ORD_JobOrders
        WHERE VehicleID = @VehicleID
          AND CAST(ScheduledDate AS DATE) = CAST(@ScheduledDate AS DATE)
          AND JobStatusID NOT IN (4, 5) -- Not cancelled or completed
    )
    BEGIN
        RAISERROR('Vehicle is already assigned to another job on the scheduled date', 16, 1)
        RETURN
    END

    -- Generate job order number: JO-YYYYMMDD-BranchID-Seq
    SELECT @NewJobOrderNo = 'JO-'
        + CONVERT(NVARCHAR(8), @ScheduledDate, 112)
        + '-' + CAST(@BranchID AS NVARCHAR)
        + '-' + RIGHT('000' + CAST(
            ISNULL((
                SELECT COUNT(*) + 1 FROM dbo.ORD_JobOrders
                WHERE BranchID = @BranchID
                  AND CAST(ScheduledDate AS DATE) = CAST(@ScheduledDate AS DATE)
            ), 1) AS NVARCHAR), 3)

    BEGIN TRANSACTION

    BEGIN TRY
        INSERT INTO dbo.ORD_JobOrders
            (BranchID, DriverID, VehicleID, JobOrderNo, ScheduledDate,
             CargoWeightKg, JobStatusID, Notes, CreatedAt, CreatedBy)
        VALUES
            (@BranchID, @DriverID, @VehicleID, @NewJobOrderNo, @ScheduledDate,
             @CargoWeightKg, 1, @Notes, GETDATE(), SYSTEM_USER)

        SET @JobOrderID = SCOPE_IDENTITY()

        -- Update vehicle's assigned driver if different
        UPDATE dbo.Fleet_Vehicles
        SET DriverID = @DriverID, ModifiedAt = GETDATE(), ModifiedBy = SYSTEM_USER
        WHERE VehicleID = @VehicleID AND (DriverID IS NULL OR DriverID <> @DriverID)

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION
        SET @JobOrderID = NULL
        DECLARE @CatchMsg NVARCHAR(500) = ERROR_MESSAGE()
        RAISERROR(@CatchMsg, 16, 1)
    END CATCH

    SET NOCOUNT OFF
END
GO
