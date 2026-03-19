-- ============================================================
-- Function: dbo.VEH_FuelCostCalc
-- Description: Calculates the estimated fuel cost for a vehicle
--              over a given distance using the current fuel price scale.
-- Parameters:
--   @VehicleID      INT           - Vehicle to calculate for
--   @DistanceKm     DECIMAL(10,2) - Distance to calculate
--   @FuelPricePerL  DECIMAL(8,4)  - Override fuel price; NULL = use current scale
-- Returns:
--   DECIMAL(12,2) - Estimated fuel cost
-- ============================================================

IF OBJECT_ID(N'dbo.VEH_FuelCostCalc', N'FN') IS NOT NULL
    DROP FUNCTION dbo.VEH_FuelCostCalc
GO

CREATE FUNCTION dbo.VEH_FuelCostCalc
(
    @VehicleID      INT,
    @DistanceKm     DECIMAL(10,2),
    @FuelPricePerL  DECIMAL(8,4) = NULL
)
RETURNS DECIMAL(12,2)
AS
BEGIN
    DECLARE @Result         DECIMAL(12,2) = 0
    DECLARE @FuelL100km     DECIMAL(6,2)
    DECLARE @EffectivePrice DECIMAL(8,4)

    -- Get vehicle fuel consumption rate
    SELECT @FuelL100km = v.FuelConsumptionL100km
    FROM dbo.Fleet_Vehicles v
    WHERE v.VehicleID = @VehicleID

    IF @FuelL100km IS NULL OR @FuelL100km = 0
        RETURN 0

    -- Get effective fuel price
    IF @FuelPricePerL IS NOT NULL
        SET @EffectivePrice = @FuelPricePerL
    ELSE
        SELECT TOP 1 @EffectivePrice = fs.PricePerLitre
        FROM dbo.VEH_FuelPriceScale fs
        WHERE fs.ValidFrom <= GETDATE()
          AND (fs.ValidTo IS NULL OR fs.ValidTo >= GETDATE())
        ORDER BY fs.ValidFrom DESC

    IF @EffectivePrice IS NULL OR @EffectivePrice = 0
        RETURN 0

    -- Cost = (distance / 100) * consumption * price
    SET @Result = (@DistanceKm / 100.0) * @FuelL100km * @EffectivePrice

    RETURN @Result
END
GO
