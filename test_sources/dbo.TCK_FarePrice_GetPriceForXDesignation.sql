SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO

CREATE FUNCTION dbo.TCK_FarePrice_GetPriceForXDesignation(@Guid NVARCHAR(36)='',  @RideId INT =NULL, @LineVariantID INT = 0, @FarePriceScaleXDesignationID INT =NULL, @LuggageFarePriceScaleXDesignationID INT = NULL, @BaseAbroadFarePriceScaleXDesignationID INT = NULL, @Period INT=0, @EPAmountReductionFarePriceScaleXDesignationID INT = NULL, @KMAssignment INT = NULL)
RETURNS 
 @Prices TABLE (Price FLOAT, PriceNumber INT, RideLineRouteFrom_ID INT, RideLineRouteTo_ID INT, Luggage INT)

AS
BEGIN


	DECLARE @RideDesignationExists BIT
	DECLARE @Price INT

	DECLARE @LineId INT

	IF @LineVariantID = 0
		SELECT @LineId = Line_Id FROM TT_Ride WHERE Id = @RideId
	ELSE
	BEGIN
		SET @LineId = @RideId
		SET @RideId = NULL
	END

	DECLARE @UsedPriceNumber INT -- EP
	DECLARE @MinPriceNumber INT

	DECLARE @TempPrices TABLE (Price FLOAT, FarePriceNumber INT, RideLineRouteFrom_ID INT, RideLineRouteTo_ID INT, Distance INT, Luggage INT, BaseAbroadPrice INT, PercentageDomestic INT)

	
	-- OKRESOWA (MIESIĘCZNA, OKRESOWA WIELOPRZEJAZDOWA) - PRZYPISANIE KILOMETROWE
	IF ISNULL(@KMAssignment,0) =1 AND @Period >0
	BEGIN


		DECLARE @IncrementP INT
		DECLARE @RateP INT

		DECLARE @MinPriceNumberP INT = NULL
		DECLARE @MaxPriceNumberP INT = NULL
		DECLARE @MAXNoIncrementDistanceP INT
	

		DECLARE @IncrementPriceP INT
		DECLARE @IncrementXDistanceP INT
		-- wielokrotność
			
		SELECT	@IncrementXDistanceP = p.XDistance,
				@IncrementPriceP = p.Price,
				@MaxPriceNumberP = PriceNumberMax
		FROM dbo.TCK_FarePrice p
		INNER JOIN 
		(	
		
			SELECT FarePriceScaleMonthTicketXType_ID, PriceNumberMax
			FROM
			(
				SELECT @FarePriceScaleXDesignationID AS FarePriceScaleMonthTicketXType_ID, MIN(PriceNumber)-1 AS PriceNumberMax
				FROM dbo.TCK_FarePrice p
				WHERE p.FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID AND ISNULL(p.XDistance,0) =0
				AND EXISTS(SELECT x.ID FROM dbo.TCK_FarePrice x WHERE x.FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID AND ISNULL(x.XDistance,0) =0)
			) y
			WHERE PriceNumberMax IS NOT NULL

			UNION ALL
			
			SELECT FarePriceScaleMonthTicketXType_ID, PriceNumberMax
			FROM
			(	SELECT @FarePriceScaleXDesignationID AS FarePriceScaleMonthTicketXType_ID, MAX(PriceNumber) AS PriceNumberMax
				FROM dbo.TCK_FarePrice p
				WHERE p.FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID
				AND NOT EXISTS(SELECT x.ID FROM dbo.TCK_FarePrice x WHERE x.FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID AND ISNULL(x.XDistance,0) =0)
			) x
			WHERE PriceNumberMax IS NOT NULL

		) Mx ON Mx.FarePriceScaleMonthTicketXType_ID = p.FarePriceScaleMonthTicketXType_ID AND mx.PriceNumberMax = p.PriceNumber
		WHERE p.FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID


		INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, Distance)
		SELECT CASE WHEN MinPriceNumber IS NOT NULL THEN  p.Price ELSE NULL END  AS Price, MinPriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, DistanceToChildPoint
		FROM
		(
			SELECT MIN( CASE WHEN r.DistanceToChildPoint <= XDistance AND PriceNumber< @MaxPriceNumberP THEN PriceNumber ELSE NULL END) AS MinPriceNumber, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteFrom_ID ELSE r.LineRouteFrom_ID END AS RideLineRouteFrom_ID, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteTo_ID ELSE r.LineRouteTo_ID END AS RideLineRouteTo_ID, DistanceToChildPoint
			FROM dbo.TCK_GetRideToPrices r 
			LEFT JOIN dbo.TCK_FarePrice p ON ISNULL(Increment,0)=0 AND FarePriceScaleMonthTicketXType_ID =@FarePriceScaleXDesignationID AND r.DistanceToChildPoint <= XDistance  AND PriceNumber< @MaxPriceNumberP
			WHERE r.Guid = @Guid
			GROUP BY CASE WHEN @RideId IS NOT NULL THEN r.RideRouteFrom_ID ELSE r.LineRouteFrom_ID END, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteTo_ID ELSE r.LineRouteTo_ID END, r.DistanceToChildPoint

		) Pom
		LEFT JOIN dbo.TCK_FarePrice p ON ISNULL(Increment,0)=0 AND FarePriceScaleMonthTicketXType_ID=@FarePriceScaleXDesignationID AND PriceNumber = Pom.MinPriceNumber
	
	
			IF @MaxPriceNumberP =1
				SELECT @Price = p.Price
				FROM TCK_FarePrice p
				WHERE p.FarePriceScaleMonthTicketXType_ID = @FarePriceScaleXDesignationID AND PriceNumber = 1
	
		UPDATE t 
			SET Price = CASE WHEN @MaxPriceNumberP =1 THEN @Price ELSE CEILING((((pom.Distance - pom.XDistance)/1.00)/@IncrementXDistanceP))*@IncrementPriceP+pom.Price END
		
		FROM @TempPrices t
		INNER JOIN 
		(
			SELECT p.Price, p.XDistance, pom.RideLineRouteFrom_ID, pom.RideLineRouteTo_ID, pom.Distance FROM TCK_FarePrice p
			INNER JOIN
			(	SELECT * FROM @TempPrices r 
				WHERE r.FarePriceNumber IS NULL
			) pom ON 1=1
			WHERE p.FarePriceScaleMonthTicketXType_ID = @FarePriceScaleXDesignationID AND p.PriceNumber = @MaxPriceNumberP-1
		) pom ON pom.RideLineRouteFrom_ID = t.RideLineRouteFrom_ID AND pom.RideLineRouteTo_ID = t.RideLineRouteTo_ID


	END
	ELSE
	-- OKRESOWA (MIESIĘCZNA, OKRESOWA WIELOPRZEJAZDOWA)
	IF @Period >0
	BEGIN

		IF EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp 
					INNER JOIN dbo.TCK_FarePriceScaleMonthTicketXType m ON frp.ID = m.FarePriceScaleMonthTicket_ID AND frp.FarePriceScaleType_ID IN (4, 21)
					INNER JOIN TCK_FarePriceScaleRideXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceRideRouteXREF rrx ON rrx.FarePriceScaleRideXREF_ID = rx.ID
					WHERE m.id = @FarePriceScaleXDesignationID AND rx.Ride_ID = @RideID) AND @LineVariantID=0
		BEGIN	
			SET	@RideDesignationExists = 1
		END
		ELSE
		BEGIN
			SET	@RideDesignationExists = 0

		END
		
		IF @RideDesignationExists =1
					OR
					EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp 
					INNER JOIN dbo.TCK_FarePriceScaleMonthTicketXType m ON frp.ID = m.FarePriceScaleMonthTicket_ID AND frp.FarePriceScaleType_ID IN (4, 21)
					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID
					WHERE m.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId)
		----- TABELOWA, MANIPULACYJNE, BONIFIKATY
		BEGIN

			IF @RideDesignationExists = 0
			BEGIN
				IF @LineVariantID >0
				BEGIN
					
					INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID)					
					SELECT	p.Price, rrx.FarePriceNumber, LineRouteFrom_ID AS RideLineRouteFrom_ID, LineRouteTo_ID AS RideLineRouteto_ID
					FROM TCK_FarePriceScale frp
					INNER JOIN dbo.TCK_FarePriceScaleMonthTicketXType m ON frp.ID = m.FarePriceScaleMonthTicket_ID AND frp.FarePriceScaleType_ID IN (4, 21)

					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID 
					--AND LineRouteFrom_ID=@RideLineRouteFrom_ID AND LineRouteTo_ID=@RideLineRouteto_ID
					INNER JOIN TCK_FarePrice p ON p.FarePriceScaleMonthTicketXType_ID = m.id AND rrx.FarePriceNumber = p.PriceNumber
					WHERE m.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId 
				END
				ELSE
				BEGIN
					INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID)
					SELECT	p.Price, rrx.FarePriceNumber, rr1.id AS RideLineRouteFrom_ID, rr2.id AS RideLineRouteto_ID							
					FROM TCK_FarePriceScale frp
					INNER JOIN dbo.TCK_FarePriceScaleMonthTicketXType m ON frp.ID = m.FarePriceScaleMonthTicket_ID AND frp.FarePriceScaleType_ID IN (4, 21)
					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID 
					INNER JOIN dbo.TT_LineRoute lr1 ON rrx.LineRouteFrom_ID = lr1.id
					INNER JOIN dbo.TT_RideRoute rr1 ON rr1.LineRoute_ID = lr1.ID --AND rr1.id = @RideLineRouteFrom_ID 
					INNER JOIN dbo.TT_LineRoute lr2  ON rrx.LineRouteTo_ID = lr2.id
					INNER JOIN dbo.TT_RideRoute rr2 ON rr2.LineRoute_ID = lr2.ID --AND rr2.id = @RideLineRouteTo_ID
					INNER JOIN TCK_FarePrice p ON p.FarePriceScaleMonthTicketXType_ID = m.id AND rrx.FarePriceNumber = p.PriceNumber
					WHERE m.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId AND rr1.Ride_ID=@RideId AND rr2.Ride_ID=@RideId
				END
			
			END
			ELSE
			BEGIN
				INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID)
				SELECT	p.Price, rrx.FarePriceNumber, RideRouteFrom_ID AS RideLineRouteFrom_ID,	RideRouteTo_ID AS RideLineRouteto_ID						
				FROM TCK_FarePriceScale frp
				INNER JOIN dbo.TCK_FarePriceScaleMonthTicketXType m ON frp.ID = m.FarePriceScaleMonthTicket_ID AND frp.FarePriceScaleType_ID IN (4, 21)
				INNER JOIN TCK_FarePriceScaleRideXREF rx ON rx.FarePriceScale_ID = frp.id
				INNER JOIN TCK_FarePriceRideRouteXREF rrx ON rrx.FarePriceScaleRideXREF_ID = rx.ID
				INNER JOIN TCK_FarePrice p ON p.FarePriceScaleMonthTicketXType_ID = m.id AND rrx.FarePriceNumber= p.PriceNumber
				WHERE m.id = @FarePriceScaleXDesignationID AND rx.Ride_ID = @RideID 
				--AND rrx.RideRouteFrom_ID =@RideLineRouteFrom_ID AND rrx.RideRouteTo_ID =@RideLineRouteTo_ID

			END
		END
		
	END

	ELSE
	
	----- KILOMETROWA
	
	IF EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID WHERE xdes.id = @FarePriceScaleXDesignationID AND frp.FarePriceScaleType_ID = 11)
	OR EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID 
				INNER JOIN TCK_FarePrice p ON xdes.id = p.FarePriceScaleXDesignation_ID WHERE xdes.id = @FarePriceScaleXDesignationID AND frp.FarePriceScaleType_ID=5 AND p.XDistance >0)
	BEGIN
		
		--DECLARE @tab TABLE (Price INT, MinPriceNumber INT, RideRouteFrom_ID INT, RideRouteTo_ID INT, DistanceToChildPoint INT)
		
		INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, Distance)

		SELECT CASE WHEN MinPriceNumber IS NOT NULL THEN  p.Price ELSE NULL END  AS Price, MinPriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, DistanceToChildPoint
		FROM
		(
			SELECT MIN( CASE WHEN r.DistanceToChildPoint <= XDistance  THEN  PriceNumber ELSE NULL END) AS MinPriceNumber, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteFrom_ID ELSE r.LineRouteFrom_ID END AS RideLineRouteFrom_ID, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteTo_ID ELSE r.LineRouteTo_ID END AS RideLineRouteTo_ID, DistanceToChildPoint
			FROM dbo.TCK_GetRideToPrices r 
			LEFT JOIN dbo.TCK_FarePrice p ON ISNULL(Increment,0)=0 AND FarePriceScaleXDesignation_ID =@FarePriceScaleXDesignationID AND r.DistanceToChildPoint <= XDistance 
			WHERE r.Guid = @Guid
			GROUP BY CASE WHEN @RideId IS NOT NULL THEN r.RideRouteFrom_ID ELSE r.LineRouteFrom_ID END, CASE WHEN @RideId IS NOT NULL THEN r.RideRouteTo_ID ELSE r.LineRouteTo_ID END, r.DistanceToChildPoint

		) Pom
		LEFT JOIN dbo.TCK_FarePrice p ON ISNULL(Increment,0)=0 AND FarePriceScaleXDesignation_ID=@FarePriceScaleXDesignationID AND PriceNumber = Pom.MinPriceNumber


		DECLARE @IncrementPrice INT
		DECLARE @IncrementXDistance INT
		DECLARE @MaxPriceNumber INT

		-- wielokrotność
		SELECT @IncrementXDistance =p.XDistance, @IncrementPrice =p.Price
		FROM TCK_FarePrice p
		WHERE p.Increment=1 AND p.FarePriceScaleXDesignation_ID =@FarePriceScaleXDesignationID

		SELECT @MaxPriceNumber = MAX(p.PriceNumber)
			FROM TCK_FarePrice p WHERE Increment=0 AND FarePriceScaleXDesignation_ID=@FarePriceScaleXDesignationID

		SET @MaxPriceNumber = ISNULL(@MaxPriceNumber,0)		

		UPDATE t 
			SET Price = CEILING((((pom.Distance - pom.XDistance)/1.00)/@IncrementXDistance))*@IncrementPrice+pom.Price
		
		FROM @TempPrices t
		INNER JOIN 
		(
			SELECT p.Price, p.XDistance, pom.RideLineRouteFrom_ID, pom.RideLineRouteTo_ID, pom.Distance FROM TCK_FarePrice p
			INNER JOIN
			(	SELECT * FROM @TempPrices r 
				WHERE r.FarePriceNumber IS NULL
			) pom ON 1=1
			WHERE p.FarePriceScaleXDesignation_ID = @FarePriceScaleXDesignationID AND p.PriceNumber = @MaxPriceNumber
		) pom ON pom.RideLineRouteFrom_ID = t.RideLineRouteFrom_ID AND pom.RideLineRouteTo_ID = t.RideLineRouteTo_ID
		
		
	----- KILOMETROWA	
	END
	ELSE 
	BEGIN

		IF EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp 
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID AND FarePriceScaleType_ID IN (1, 2, 3, 5, 6, 7, 20, 21)
					INNER JOIN TCK_FarePriceScaleRideXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceRideRouteXREF rrx ON rrx.FarePriceScaleRideXREF_ID = rx.ID
					WHERE xdes.id = @FarePriceScaleXDesignationID AND rx.Ride_ID = @RideID) AND @LineVariantID=0
		BEGIN	
			SET	@RideDesignationExists = 1
		END
		ELSE
		BEGIN
			SET	@RideDesignationExists = 0

		END
		
		IF @RideDesignationExists =1
					OR
					EXISTS(SELECT frp.id FROM TCK_FarePriceScale frp 
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID AND FarePriceScaleType_ID IN (1, 2, 3, 5, 6, 7, 20, 21)
					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID
					WHERE xdes.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId)
		----- TABELOWA, MANIPULACYJNE, BONIFIKATY
		BEGIN

			IF @RideDesignationExists = 0
			BEGIN
				IF @LineVariantID >0
				BEGIN
					INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, BaseAbroadPrice, PercentageDomestic)
					SELECT	
						CASE WHEN FarePriceScaleType_ID = 6 THEN - p.Price ELSE 
						CASE WHEN	@BaseAbroadFarePriceScaleXDesignationID <> 0 THEN
							CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <0 THEN p.Price - CAST(p.Price * (
										CASE WHEN PercentageDomestic IS NULL THEN 0 ELSE 
										CASE WHEN PercentageDomestic =1000000 THEN NULL ELSE PercentageDomestic END END / 1000000.0) +0.5 AS INT)
							ELSE
								CAST(Price*(
								CASE WHEN PercentageDomestic =0 THEN NULL ELSE PercentageDomestic END / 1000000.0) +0.5 AS INT)
							END
						ELSE
						p.Price END END AS Price, 
							rrx.FarePriceNumber,
							LineRouteFrom_ID AS RideLineRouteFrom_ID,
							LineRouteTo_ID AS RideLineRouteto_ID,
							CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN p.price ELSE 0 END AS BaseAbroadPrice,
							PercentageDomestic
					FROM TCK_FarePriceScale frp
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID AND FarePriceScaleType_ID IN (1, 2, 3, 5, 6, 7, 20, 21)
					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID 
					--AND LineRouteFrom_ID=@RideLineRouteFrom_ID AND LineRouteTo_ID=@RideLineRouteto_ID
					INNER JOIN TCK_FarePrice p ON p.FarePriceScaleXDesignation_ID = xdes.id AND rrx.FarePriceNumber = p.PriceNumber
					WHERE xdes.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId 
				END
				ELSE
				BEGIN
					INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, BaseAbroadPrice, PercentageDomestic)
					SELECT	
					CASE WHEN FarePriceScaleType_ID = 6 THEN - p.Price ELSE 
					CASE WHEN	@BaseAbroadFarePriceScaleXDesignationID <> 0 THEN
						CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <0 THEN p.Price - CAST(p.Price * (
									CASE WHEN PercentageDomestic IS NULL THEN 0 ELSE 
									CASE WHEN PercentageDomestic =1000000 THEN NULL ELSE PercentageDomestic END END / 1000000.0) +0.5 AS INT)
						ELSE
							CAST(Price*(
							CASE WHEN PercentageDomestic =0 THEN NULL ELSE PercentageDomestic END / 1000000.0) +0.5 AS INT)
						END
					ELSE
					p.Price END END AS Price, 
							rrx.FarePriceNumber,
							rr1.id AS RideLineRouteFrom_ID,
							rr2.id AS RideLineRouteto_ID,
							CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN p.price ELSE 0 END AS BaseAbroadPrice,
							PercentageDomestic
					FROM TCK_FarePriceScale frp
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID AND FarePriceScaleType_ID IN (1, 2, 3, 5, 6, 7, 20, 21)
					INNER JOIN TCK_FarePriceScaleLineXREF rx ON rx.FarePriceScale_ID = frp.id
					INNER JOIN TCK_FarePriceLineRouteXREF rrx ON rrx.FarePriceScaleLineXREF_ID = rx.ID 
					INNER JOIN dbo.TT_LineRoute lr1 ON rrx.LineRouteFrom_ID = lr1.id
					INNER JOIN dbo.TT_RideRoute rr1 ON rr1.LineRoute_ID = lr1.ID --AND rr1.id = @RideLineRouteFrom_ID 
					INNER JOIN dbo.TT_LineRoute lr2  ON rrx.LineRouteTo_ID = lr2.id
					INNER JOIN dbo.TT_RideRoute rr2 ON rr2.LineRoute_ID = lr2.ID --AND rr2.id = @RideLineRouteTo_ID
					INNER JOIN TCK_FarePrice p ON p.FarePriceScaleXDesignation_ID = xdes.id AND rrx.FarePriceNumber = p.PriceNumber
					WHERE xdes.id = @FarePriceScaleXDesignationID AND rx.Line_ID = @LineId AND rr1.Ride_ID = rr2.Ride_ID AND rr1.Ride_ID = @RideId		
				END
			
			END
			ELSE
			BEGIN
				INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, BaseAbroadPrice, PercentageDomestic)
				SELECT	
				CASE WHEN FarePriceScaleType_ID = 6 THEN - p.Price ELSE 
				CASE WHEN	@BaseAbroadFarePriceScaleXDesignationID <> 0 THEN
					CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <0 THEN p.Price - CAST(p.Price * (
								CASE WHEN PercentageDomestic IS NULL THEN 0 ELSE 
								CASE WHEN PercentageDomestic =1000000 THEN NULL ELSE PercentageDomestic END END / 1000000.0) +0.5 AS INT)
					ELSE
						CAST(Price*(
						CASE WHEN PercentageDomestic =0 THEN NULL ELSE PercentageDomestic END / 1000000.0) +0.5 AS INT)
					END
				ELSE
				p.Price END END AS Price, 
				rrx.FarePriceNumber, RideRouteFrom_ID AS RideLineRouteFrom_ID, RideRouteTo_ID AS RideLineRouteto_ID,
				CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN p.price ELSE 0 END AS BaseAbroadPrice,
				PercentageDomestic
				FROM TCK_FarePriceScale frp
				INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdes ON xdes.FarePriceScale_ID = frp.ID AND FarePriceScaleType_ID IN (1, 2, 3, 5, 6, 7, 20, 21)
				INNER JOIN TCK_FarePriceScaleRideXREF rx ON rx.FarePriceScale_ID = frp.id
				INNER JOIN TCK_FarePriceRideRouteXREF rrx ON rrx.FarePriceScaleRideXREF_ID = rx.ID
				INNER JOIN TCK_FarePrice p ON p.FarePriceScaleXDesignation_ID = xdes.id AND rrx.FarePriceNumber= p.PriceNumber
				WHERE xdes.id = @FarePriceScaleXDesignationID AND rx.Ride_ID = @RideID 
				--AND rrx.RideRouteFrom_ID =@RideLineRouteFrom_ID AND rrx.RideRouteTo_ID =@RideLineRouteTo_ID

			END
		END
		
	END
	

	--Do Taryfy EP podczepiona ulga kwotowa
	IF @EPAmountReductionFarePriceScaleXDesignationID > 0
	BEGIN
		
		INSERT INTO @TempPrices (Price, FarePriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID)
		SELECT 	p.Price,
				x.FarePriceNumber,
				x.RideLineRouteFrom_ID,
				x.RideLineRouteTo_ID
		FROM dbo.TCK_FarePrice p
		INNER JOIN @TempPrices x ON x.FarePriceNumber = p.PriceNumber
		WHERE p.FarePriceScaleXDesignation_ID = @EPAmountReductionFarePriceScaleXDesignationID
			--AND p.PriceNumber = @UsedPriceNumber
			
	END


	-- BAGAŻOWA OD CENY
	IF @LuggageFarePriceScaleXDesignationID > 0
	BEGIN

		UPDATE t 
			SET Luggage = 	CASE WHEN	@BaseAbroadFarePriceScaleXDesignationID <> 0 THEN
							CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <0 THEN pom.Price - CAST(pom.Price * (
										CASE WHEN PercentageDomestic IS NULL THEN 0 ELSE 
										CASE WHEN PercentageDomestic =1000000 THEN NULL ELSE PercentageDomestic END END / 1000000.0) +0.5 AS INT)
							ELSE
								CAST(pom.Price*(
								CASE WHEN PercentageDomestic =0 THEN NULL ELSE PercentageDomestic END / 1000000.0) +0.5 AS INT)
							END
						ELSE
						pom.Price END

		FROM @TempPrices t
		INNER JOIN 
		(
			SELECT p.Price, PricePom
			FROM TCK_FarePrice p
			INNER JOIN
			(
				
				SELECT MIN(p.PriceNumber) AS MinPriceNumber, pom.Price AS PricePom
				FROM TCK_FarePrice p
				INNER JOIN
				(	SELECT CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN BaseAbroadPrice ELSE Price END AS Price, PercentageDomestic FROM @TempPrices r 
				) pom ON 1=1
				WHERE FarePriceScaleXDesignation_ID =@LuggageFarePriceScaleXDesignationID AND pom.Price <= XTicketPrice 
				GROUP BY pom.Price

			) x ON p.PriceNumber = MinPriceNumber
			WHERE p.FarePriceScaleXDesignation_ID=@LuggageFarePriceScaleXDesignationID

		) pom ON CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN t.BaseAbroadPrice ELSE t.Price END = PricePom


		UPDATE t 
			SET Luggage = 

				CASE WHEN	@BaseAbroadFarePriceScaleXDesignationID <> 0 THEN
							CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <0 THEN pom.Price - CAST(pom.Price * (
										CASE WHEN PercentageDomestic IS NULL THEN 0 ELSE 
										CASE WHEN PercentageDomestic =1000000 THEN NULL ELSE PercentageDomestic END END / 1000000.0) +0.5 AS INT)
							ELSE
								CAST(pom.Price*(
								CASE WHEN PercentageDomestic =0 THEN NULL ELSE PercentageDomestic END / 1000000.0) +0.5 AS INT)
							END
						ELSE
						pom.Price END

		FROM @TempPrices t
		INNER JOIN 
		(
			SELECT p.Price,
			 PricePom, MinPriceNumber
			FROM TCK_FarePrice p
			INNER JOIN
			(
				SELECT MAX(p.PriceNumber) AS MinPriceNumber, pom.Price AS PricePom
				FROM TCK_FarePrice p
				INNER JOIN
				(	SELECT CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN BaseAbroadPrice ELSE Price END AS Price, PercentageDomestic FROM @TempPrices r WHERE r.Luggage IS NULL
				) pom ON 1=1
				WHERE FarePriceScaleXDesignation_ID =@LuggageFarePriceScaleXDesignationID AND pom.Price > XTicketPrice 
				GROUP BY pom.Price

			) x ON p.PriceNumber = MinPriceNumber
			WHERE p.FarePriceScaleXDesignation_ID=@LuggageFarePriceScaleXDesignationID
		) pom ON CASE WHEN @BaseAbroadFarePriceScaleXDesignationID <> 0 THEN t.BaseAbroadPrice ELSE t.Price END = PricePom 
	


						 
		
	END

	INSERT INTO @Prices (Price, PriceNumber, RideLineRouteFrom_ID, RideLineRouteTo_ID, Luggage)
	SELECT DISTINCT Price, 0, RideLineRouteFrom_ID, RideLineRouteTo_ID , Luggage  
	FROM @TempPrices

	RETURN
END
GO




