-- ============================================================
-- Procedure: dbo.VEH_FuelCostScaleCopyFromDB
-- Description: Copies the fuel cost price scale from a source branch
--              to a target branch, optionally with a date offset.
--              Used to propagate fuel price updates across branches.
-- Parameters:
--   @SourceBranchID   INT     - Branch to copy scale from
--   @TargetBranchID   INT     - Branch to copy scale to
--   @DateOffsetDays   INT     - Shift ValidFrom/ValidTo by N days (default 0)
--   @OverwriteExisting BIT    - If 1, clear existing target scale first
-- ============================================================

IF OBJECT_ID(N'dbo.VEH_FuelCostScaleCopyFromDB', N'P') IS NOT NULL
    DROP PROCEDURE dbo.VEH_FuelCostScaleCopyFromDB
GO

CREATE PROCEDURE dbo.VEH_FuelCostScaleCopyFromDB
    @SourceBranchID     INT,
    @TargetBranchID     INT,
    @DateOffsetDays     INT = 0,
    @OverwriteExisting  BIT = 0
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @CopiedRows INT = 0

    -- Validate source branch
    IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_Branches WHERE BranchID = @SourceBranchID)
    BEGIN
        RAISERROR('Source branch not found', 16, 1)
        RETURN
    END

    -- Validate target branch
    IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_Branches WHERE BranchID = @TargetBranchID)
    BEGIN
        RAISERROR('Target branch not found', 16, 1)
        RETURN
    END

    BEGIN TRANSACTION

    BEGIN TRY
        -- Optionally clear existing target scale
        IF @OverwriteExisting = 1
        BEGIN
            DELETE FROM dbo.VEH_FuelPriceScale
            WHERE BranchID = @TargetBranchID
        END

        -- Copy rows with optional date offset
        INSERT INTO dbo.VEH_FuelPriceScale
            (BranchID, FuelType, PricePerLitre, ValidFrom, ValidTo, CreatedAt, CreatedBy)
        SELECT
            @TargetBranchID,
            fps.FuelType,
            fps.PricePerLitre,
            DATEADD(DAY, @DateOffsetDays, fps.ValidFrom),
            CASE WHEN fps.ValidTo IS NOT NULL
                 THEN DATEADD(DAY, @DateOffsetDays, fps.ValidTo)
                 ELSE NULL END,
            GETDATE(),
            SYSTEM_USER
        FROM
            dbo.VEH_FuelPriceScale fps
        WHERE
            fps.BranchID = @SourceBranchID
            -- Skip rows that would create duplicates in target
            AND NOT EXISTS (
                SELECT 1 FROM dbo.VEH_FuelPriceScale t
                WHERE t.BranchID = @TargetBranchID
                  AND t.FuelType = fps.FuelType
                  AND t.ValidFrom = DATEADD(DAY, @DateOffsetDays, fps.ValidFrom)
            )

        SET @CopiedRows = @@ROWCOUNT

        COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION
        DECLARE @ErrMsg NVARCHAR(500) = ERROR_MESSAGE()
        RAISERROR(@ErrMsg, 16, 1)
        RETURN
    END CATCH

    -- Return summary
    SELECT @CopiedRows AS RowsCopied, @SourceBranchID AS SourceBranchID,
           @TargetBranchID AS TargetBranchID

    SET NOCOUNT OFF
END
GO
