SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
-- Kopiowanie taryf
CREATE PROCEDURE [dbo].[TCK_FarePriceScaleCopyFromDatabase]
--alter PROCEDURE [dbo].[TCK_FarePriceScaleCopy]
@INDEX					INT OUTPUT,
@FarePriceScale_id		INT,
@FarePriceScaleNumber	INT,
@FarePriceList_ID		INT,
@Name					NVARCHAR(50),
@NewTran				BIT = 1,
@FarePriceScaleType_ID	INT = 0, --umożliwienie zmiany typu przy kopiowaniu   
@CopyLineRideAssigments TINYINT = 0,
@TransferKmTariffToTab	TINYINT = 0

--WITH ENCRYPTION
AS BEGIN
	DECLARE @FarePriceListValidFrom DATETIME
	DECLARE @OldFarePriceList_ID	INT
    DECLARE @NewCompany_ID			INT
	DECLARE @OldCompany_ID			INT
	DECLARE @NewNumber				INT
	DECLARE @NewNumberID			INT
	
    DECLARE @EP_ID					INT
	DECLARE @s_isEP					BIT = 0
	DECLARE @s_is_ChangeTariff		BIT = 0
	DECLARE @s_is_SettlementTariff	BIT = 0
	DECLARE @s_Community_ID			INT

	DECLARE @s_isPriceNeeded		BIT = 0
	DECLARE @RideName				NVARCHAR(1000) = ''	-- logowanie dodanych kursów
	DECLARE @LineName				NVARCHAR(1000) = ''	-- logowanie dodanych linii
	DECLARE @Log					NVARCHAR(1000) = ''	-- informacja zwrotna do uzytkownika

	SET @TransferKmTariffToTab = ISNULL(@TransferKmTariffToTab,0)

	DECLARE @FarePriceListValidTo DATE = NULL

	SET NOCOUNT ON

	  
	SELECT	@FarePriceListValidFrom = ValidFrom, 
			@FarePriceListValidTo = ValidTo 
	FROM [DMKK].[dbo].[TCK_FarePriceList]
	WHERE [ID] = @FarePriceList_ID
	;
	IF (@NewTran = 1)
		BEGIN TRAN
	BEGIN TRY		
		SELECT
            @OldFarePriceList_ID	= [FarePriceList_ID],
			@OldCompany_ID			= [Company_id],
			@s_isEP					= CASE WHEN ISNULL(fps.FarePriceScaleEP_ID,0)=0 THEN 0 ELSE 1 END,
			@s_is_ChangeTariff      = CASE WHEN fps.ChangeTariff=0 THEN '0' ELSE '1' END,
			@s_is_SettlementTariff  = CASE WHEN fps.SettlementTariff=0 THEN '0' ELSE '1' END,
		    @s_Community_ID			= CAST(ISNULL(fps.Community_ID ,0) AS nvarchar),
			@s_isPriceNeeded		= CASE WHEN ISNULL(tfp1.XTicketPrice,ISNULL(tfp2.XTicketPrice,0))=0 THEN 0 ELSE 1 END

		FROM [DMKK].[dbo].[TCK_FarePriceScale] fps
		INNER JOIN [DMKK].[dbo].[TCK_FarePriceList] l ON fps.FarePriceList_ID = l.ID
		LEFT JOIN [DMKK].[dbo].TCK_FarePriceScaleXDesignation tfpsx ON tfpsx.FarePriceScale_ID = fps.ID AND FarePriceScaleType_ID IN (1, 2, 5, 6, 7, 20)		
		LEFT JOIN [DMKK].[dbo].TCK_FarePrice tfp2 ON (tfp2.FarePriceScaleXDesignation_ID = tfpsx.ID AND tfp2.XTicketPrice IS NOT NULL)

		LEFT JOIN [DMKK].dbo.TCK_FarePriceScaleMonthTicketXType m ON fps.ID = m.FarePriceScaleMonthTicket_ID AND fps.FarePriceScaleType_ID IN (4, 21)
		LEFT JOIN [DMKK].dbo.TCK_FarePrice tfp1 ON (tfp1.FarePriceScaleMonthTicketXType_ID = tfpsx.ID AND tfp1.XTicketPrice IS NOT NULL)

		WHERE fps.[ID] = @FarePriceScale_id


        SELECT
            @NewCompany_ID = [Company_ID]
		FROM [dbo].[TCK_FarePriceList]
		WHERE [ID] = @FarePriceList_ID

		SET @OldCompany_ID = @NewCompany_ID

		SET @NewNumberID  = (
			SELECT [ID]
			FROM [dbo].[TCK_FarePriceScale]
			WHERE (FarePriceList_ID=@FarePriceList_ID) AND (FarePriceScaleNumber = @FarePriceScaleNumber)
		) -- ID taryfy w nowym cenniku. Do sprawdzenia czy jest taki numer

		IF 
            @OldFarePriceList_ID = @FarePriceList_ID
            OR @NewNumberID > 0
        BEGIN
			SET @FarePriceScaleNumber = 1 
			DECLARE FirstFreeNumber CURSOR FOR
				SELECT FarePriceScaleNumber
				FROM dbo.TCK_FarePriceScale
				WHERE FarePriceList_ID = @FarePriceList_ID
				ORDER BY FarePriceScaleNumber			    

			OPEN FirstFreeNumber
			FETCH NEXT FROM FirstFreeNumber INTO @NewNumber;

			WHILE @@FETCH_STATUS = 0 and @NewNumber = @FarePriceScaleNumber BEGIN
				SET @FarePriceScaleNumber = @FarePriceScaleNumber + 1
				FETCH NEXT FROM FirstFreeNumber INTO @NewNumber;
			END
			CLOSE FirstFreeNumber;
			DEALLOCATE FirstFreeNumber;                   		    
		END

		--IF (@NewTran = 1) SET NOCOUNT OFF
				
        SELECT
            @EP_ID = FarePriceScaleEP_ID
        FROM [DMKK].[dbo].[TCK_FarePriceScale]
        WHERE ID = @FarePriceScale_id

        IF 
            ISNULL(@EP_ID,0) <> 0
        BEGIN
		    INSERT INTO [dbo].[TCK_FarePriceScaleEP] ( -- taryfaEP
			    [IsSale],
			    [IsESale],
			    [HourBeforeRideTo],
			    [OnlyTwoWay],
			    [HourToReturnTicket],
			    [PTicketCountYear],
			    [PTicketCountMonth],
			    [PCountYearOrMonth],
			    [STicketCountYear],
			    [STicketCountMonth],
			    [SCountYearOrMonth],
			    [PTicketValueYear],
			    [PTicketValueMonth],
			    [PValueYearOrMonth],
			    [STicketValueYear],
			    [STicketValueMonth],
			    [SValueYearOrMonth],
			    [MinCountPlace],
			    [LuggageDescription],
			    [MaxCount],
			    --[TarifGroup],
			    [MaxCountPlaceOrTicket],
			    [ReturnTicketType],
			    [FarePriceReduction_ID],
			    [OnlyTwoWayOPEN],
			    [OnlyTwoWayType],
			    [OnlyTwoWayDays]
		    )
		        SELECT
			        [IsSale],
			        [IsESale],
			        [HourBeforeRideTo],
			        [OnlyTwoWay],
			        [HourToReturnTicket],
			        [PTicketCountYear],
			        [PTicketCountMonth],
			        [PCountYearOrMonth],
			        [STicketCountYear],
			        [STicketCountMonth],
			        [SCountYearOrMonth],
			        [PTicketValueYear],
			        [PTicketValueMonth],
			        [PValueYearOrMonth],
			        [STicketValueYear],
			        [STicketValueMonth],
			        [SValueYearOrMonth],
			        [MinCountPlace],
			        [LuggageDescription],
			        [MaxCount],
			        --[TarifGroup],
			        [MaxCountPlaceOrTicket],
			        [ReturnTicketType],
			        [FarePriceReduction_ID],
			        [OnlyTwoWayOPEN],
			        [OnlyTwoWayType],
			        [OnlyTwoWayDays]
		        FROM [DMKK].[dbo].[TCK_FarePriceScaleEP]
		        WHERE
			        [ID] = @EP_ID
			SET @EP_ID = SCOPE_IDENTITY()
        END
        ELSE
            SET @EP_ID = null
            
		INSERT INTO [dbo].[TCK_FarePriceScale] ( -- taryfa
			[Name],
			[NameBusTicketMachine], 
			[FarePriceScaleNumber], 
			[FarePriceList_ID], 
			[FarePriceScaleType_ID],
			[VatRate_ID],
			[Abroad],
			[VatRateAbroad_ID],
			[PercentToReturn],
			[DynamicReturns],
			[IsValidReduction],
			[IsValidPriceReduction],
			[ActiveBusSale],
			[ActiveStationarySale],
			[ForEveryOne],
			[TarifName],
			[TarifGroup],
			[HourBeforeRide],
			[ChangeTariff],
			[SettlementTariff],
			[NotUseLuggage],
			[Community_ID],
			[SettlementTariffBase_ID],
			[FarePriceScaleEP_ID]			
		)
			SELECT
				@Name,--[Name],
				[NameBusTicketMachine], 
				@FarePriceScaleNumber, 
				@FarePriceList_ID, 
				CASE WHEN @FarePriceScaleType_ID=0 THEN  [FarePriceScaleType_ID] ELSE CASE WHEN @TransferKmTariffToTab>0 THEN 1 ELSE @FarePriceScaleType_ID END END,
				[VatRate_ID],
				[Abroad],
				[VatRateAbroad_ID],
				[PercentToReturn],
				[DynamicReturns],
				[IsValidReduction],
				[IsValidPriceReduction],
				[ActiveBusSale],
				[ActiveStationarySale],
				[ForEveryOne],
				[TarifName],
				[TarifGroup],
				[HourBeforeRide],
				[ChangeTariff],
				[SettlementTariff],
				[NotUseLuggage],
				[Community_ID],
				[SettlementTariffBase_ID],
				@EP_ID
			FROM
				[DMKK].[dbo].[TCK_FarePriceScale]
			WHERE
				[ID] = @FarePriceScale_id

		SET @INDEX = SCOPE_IDENTITY()

		

		IF (@NewTran = 1)
			SET NOCOUNT ON

		IF EXISTS(
			SELECT TOP 1 fps.ID
			FROM [DMKK].dbo.TCK_FarePriceScale fps
            INNER JOIN [DMKK].dbo.TCK_FarePriceList fpl
                ON fps.FarePriceList_ID = fpl.ID
			WHERE
				fps.[ID] = @FarePriceScale_id
                AND fpl.Company_ID = @NewCompany_ID -- cennik tej samej firmy
				AND fps.[FarePriceScaleType_ID] IN (20,21) -- ulga kwotowa (BJ,BM)
				AND fps.[FarePriceList_ID] <> @FarePriceList_ID
		) BEGIN
				
			INSERT INTO [dbo].[TCK_FarePriceReductionHistory] ( -- kopiuje ulgi
				[FarePriceReduction_ID],
				[ValidFrom],
				[Reduction],
				[ReductionAmountType_id],
				[RideDesignation_ID],
				[CompanyGovOffice_ID],
				[ReductionRoundMethod_ID],
				[FarePriceScale_ID],
				[FarePriceScaleMonthTicket_ID],
				[FarePriceList_ID]
			)
			SELECT
				[FarePriceReduction_ID],
				@FarePriceListValidFrom,
				[Reduction],
				[ReductionAmountType_id],
				CASE WHEN [RideDesignation_ID] IS NULL THEN NULL ELSE 1 END,
				[CompanyGovOffice_ID],
				[ReductionRoundMethod_ID],
				CASE WHEN [ReductionAmountType_id] = 1 THEN @INDEX ELSE NULL END, -- FarePriceScale_ID
				CASE WHEN [ReductionAmountType_id] = 2 THEN @INDEX ELSE NULL END, -- FarePriceScaleMonthTicket_ID
				@FarePriceList_ID
			FROM [DMKK].[dbo].[TCK_FarePriceReductionHistory] rh
			WHERE
                -- jeżeli ta ulga nie jest już przypisana do innej taryfy tego cennika
                NOT EXISTS (
                    SELECT TOP 1 1
                    FROM [dbo].[TCK_FarePriceReductionHistory]
                    WHERE 
                        rh.FarePriceReduction_ID = FarePriceReduction_ID
                        AND FarePriceList_ID = @FarePriceList_ID
                )
				AND @FarePriceScale_id = CASE 
					WHEN [ReductionAmountType_id] = 1 THEN [FarePriceScale_ID]
					WHEN [ReductionAmountType_id] = 2 THEN [FarePriceScaleMonthTicket_ID]
					ELSE -1
				END
	
				DECLARE @TempRed TABLE (FarePriceReductionID INT)
				-- przy tworzeniu nowego cennika dla tej samej firmy kopiowane już są ulgi więc potrzebny jest update
				INSERT INTO @TempRed (FarePriceReductionID)

				SELECT [FarePriceReduction_ID]
				FROM [dbo].[TCK_FarePriceReductionHistory] rh
				WHERE @FarePriceScale_id = CASE 
					WHEN [ReductionAmountType_id] = 1 THEN [FarePriceScale_ID]
					WHEN [ReductionAmountType_id] = 2 THEN [FarePriceScaleMonthTicket_ID]
					ELSE -1
				END
				
				UPDATE [dbo].[TCK_FarePriceReductionHistory]
					SET FarePriceScale_ID =	CASE WHEN [ReductionAmountType_id] = 1 THEN @INDEX ELSE NULL END, -- FarePriceScale_ID
						FarePriceScaleMonthTicket_ID =CASE WHEN [ReductionAmountType_id] = 2 THEN @INDEX ELSE NULL END -- FarePriceScaleMonthTicket_ID
	
				WHERE [dbo].[TCK_FarePriceReductionHistory].FarePriceList_ID = @FarePriceList_ID AND [dbo].[TCK_FarePriceReductionHistory].ValidFrom = @FarePriceListValidFrom	
					AND FarePriceReduction_ID IN (SELECT FarePriceReductionID FROM @TempRed) 
			
			END
			


		-- tabele nieokresowe
		IF NOT (@FarePriceScaleType_ID IN (4,21))
			INSERT INTO dbo.TCK_FarePriceScaleXDesignation (
				[Name],
				[FarePriceScale_ID],
				[RideDesignation_ID],
				[FarePriceTableNumber]
			)
				SELECT
					[Name],
					@INDEX,
					CASE WHEN [RideDesignation_ID] IS NULL THEN NULL ELSE 1 END,
					[FarePriceTableNumber]
				FROM [DMKK].[dbo].[TCK_FarePriceScaleXDesignation]
				WHERE [FarePriceScale_ID]= @FarePriceScale_id;  

		-- tabele okresowe
		IF (@FarePriceScaleType_ID IN (4,21))
			INSERT INTO dbo.TCK_FarePriceScaleMonthTicketXType (
				[Name],
				[FarePriceScaleMonthTicket_ID],
				[FarePriceScaleMonthTicketType_ID],
				[FarePriceTableNumber],
				[DaysNumber],
				[MonthsNumber],	
				[RidesNumber],
				[LuggageTicket],
				[RideRegistrationMandatory],
				[Monday],
				[Tuesday],
				[Wednesday],
				[Thursday],
				[Friday],
				[Saturday],
				[Sunday],
				[ValidToTime],
				[SkipPrice],
				[EPOnlyTwoWay],
				[EPMonthTicketOnlyFromFirst],
				[EPLimitTicketDates],
				[EPLimitTicketDatesDays],
				[EPLimitTicketDatesLastMonthDay],
				[EPOneWayExtraPriceValue],
				[EPOneWayExtraPercentValue],
				[EPDefaultFarePriceScale],
				[UnusedRidesToNextPeriod],
				[NumberDaysAfterExpires], 
				[ExtensionPeriodFrom], 
				[MaximumValidityPeriods]
			)
				SELECT
					[Name],
					@INDEX,
					[FarePriceScaleMonthTicketType_ID],
					[FarePriceTableNumber],
					[DaysNumber],
					[MonthsNumber],	
					[RidesNumber],
					[LuggageTicket],
					[RideRegistrationMandatory],
					[Monday],
					[Tuesday],
					[Wednesday],
					[Thursday],
					[Friday],
					[Saturday],
					[Sunday],
					[ValidToTime],
					[SkipPrice],
					[EPOnlyTwoWay],
					[EPMonthTicketOnlyFromFirst],
					[EPLimitTicketDates],
					[EPLimitTicketDatesDays],
					[EPLimitTicketDatesLastMonthDay],
					[EPOneWayExtraPriceValue],
					[EPOneWayExtraPercentValue],
					[EPDefaultFarePriceScale],
					[UnusedRidesToNextPeriod],
					[NumberDaysAfterExpires], 
					[ExtensionPeriodFrom], 
					[MaximumValidityPeriods]
				FROM [DMKK].[dbo].TCK_FarePriceScaleMonthTicketXType
				WHERE [FarePriceScaleMonthTicket_ID]= @FarePriceScale_id;  


		--ceny dla tabel nieokresowych
		IF NOT (@FarePriceScaleType_ID in (4,21))
			WITH yy ([id], [FarePriceTableNumber]) AS (
				SELECT
					[id],
					[FarePriceTableNumber]
				FROM [DMKK].[dbo].[TCK_FarePriceScaleXDesignation]
				WHERE [FarePriceScale_ID] = @FarePriceScale_id
			)
			INSERT INTO [dbo].[TCK_FarePrice] (
				[Name], 
				[FarePriceScaleXDesignation_ID],
				[Currency_ID],
				[Price],
				[PriceNumber],
				[XDistance],
				[XTicketPrice],
				[XBusStop],
				[Increment],
				[MinutesNumber],
				[DaysNumber],
				[RidesNumber],
				[ZoneNumber],
				[ValidFromTime],
				[ValidToTime],
				[FarePriceReduction_ID],
				[Parent_ID],
				[HandlingCharge],
				[Commission],
				[LuggageTicket],
				[FarePriceCityTicketType_ID],
				[FarePriceCityTicketGroup_ID],
				[ValidityArea],
				[LinesNumber],
				[PointsNumber],
				[TimeRestriction]
			)
				SELECT
					[Name], 
					(SELECT [id]
					 FROM [dbo].[TCK_FarePriceScaleXDesignation] x
					 WHERE 
						x.[FarePriceScale_ID]= @INDEX
						AND x.[FarePriceTableNumber] = yy.[FarePriceTableNumber]
					),
					[Currency_ID],
					[Price],
					[PriceNumber],
					[XDistance],
					[XTicketPrice],
					[XBusStop],
					CASE WHEN @TransferKmTariffToTab >0 THEN NULL ELSE [Increment] END,
					[MinutesNumber],
					[DaysNumber],
					[RidesNumber],
					[ZoneNumber],
					[ValidFromTime],
					[ValidToTime],
					CASE WHEN @FarePriceScaleType_ID=3 AND @OldCompany_ID<> @NewCompany_ID THEN NULL ELSE  [FarePriceReduction_ID] END, 
					(SELECT fp_p.[id]
					 FROM [DMKK].[dbo].[TCK_FarePrice] fp_p
					 WHERE
						fp_p.[PriceNumber] = (
							SELECT fp.[PriceNumber] 
							FROM [DMKK].[dbo].[TCK_FarePrice] fp
							WHERE
								fp.[ID] = fp1.[Parent_ID]
						)
						AND fp_p.[FarePriceScaleXDesignation_ID] = (
							SELECT xd.[id]
							FROM [DMKK].[dbo].[TCK_FarePriceScaleXDesignation] xd
							WHERE
								xd.[FarePriceTableNumber] = 1
								AND xd.[FarePriceScale_ID] = (
									SELECT fps.[id]
									FROM [DMKK].[dbo].[TCK_FarePriceScale] fps
									WHERE
										fps.[FarePriceScaleNumber] = 300
										AND fps.[FarePriceList_ID] = @FarePriceList_ID
								)
						)
					),
					[HandlingCharge],
					[Commission],
					[LuggageTicket],
					[FarePriceCityTicketType_ID],
					[FarePriceCityTicketGroup_ID],
					[ValidityArea],
					CASE WHEN @FarePriceScaleType_ID =3 THEN fp1.id ELSE NULL END,
					CASE WHEN @FarePriceScaleType_ID =3 THEN fp1.Parent_ID ELSE NULL END,
					[TimeRestriction]
				FROM [DMKK].[dbo].[TCK_FarePrice] fp1
				INNER JOIN yy ON (fp1.[FarePriceScaleXDesignation_ID] = yy.[id])
				WHERE (@TransferKmTariffToTab >0 AND Increment=0 OR @TransferKmTariffToTab = 0)
				

		--ceny dla tabel okresowych------------------------------------------------------------
		IF (@FarePriceScaleType_ID IN (4,21))
			WITH yy4([id],[FarePriceTableNumber]) AS (
				SELECT [id], [FarePriceTableNumber]
				FROM [DMKK].[dbo].[TCK_FarePriceScaleMonthTicketXType]
				WHERE [FarePriceScaleMonthTicket_ID] = @FarePriceScale_id
			)
			INSERT INTO [dbo].[TCK_FarePrice] (
				[Name], 
				[FarePriceScaleMonthTicketXType_ID],--okresowe
				[Currency_ID],
				[Price],
				[PriceNumber],
				[XDistance],
				[XTicketPrice],
				[XBusStop],
				[Increment],
				[MinutesNumber],
				[DaysNumber],
				[RidesNumber],
				[ZoneNumber],
				[ValidFromTime],
				[ValidToTime],
				[FarePriceReduction_ID],
				[Parent_ID],
				[HandlingCharge],
				[Commission],
				[LuggageTicket],
				[FarePriceCityTicketType_ID],
				[LinesNumber],
				[PointsNumber]
			)
				SELECT
					[Name],
					(SELECT [ID]
					 FROM [dbo].[TCK_FarePriceScaleMonthTicketXType] x
					 WHERE
						x.[FarePriceScaleMonthTicket_ID]= @INDEX
						AND x.[FarePriceTableNumber] = yy4.[FarePriceTableNumber]
					),
					[Currency_ID],
					[Price],
					[PriceNumber],
					[XDistance],
					[XTicketPrice],
					[XBusStop],
					[Increment],
					[MinutesNumber],
					[DaysNumber],
					[RidesNumber],
					[ZoneNumber],
					[ValidFromTime],
					[ValidToTime],
					[FarePriceReduction_ID], 
					(SELECT fp_p.[id]
					 FROM [dbo].[TCK_FarePrice] fp_p
					 WHERE
						fp_p.[PriceNumber] = (
							SELECT fp.[PriceNumber]
							FROM [DMKK].[dbo].[TCK_FarePrice] fp
							WHERE
								fp.[ID] = fp1.[Parent_ID]
						)
						AND fp_p.[FarePriceScaleMonthTicketXType_ID] = (
							SELECT xd.[id]
							FROM [DMKK].[dbo].[TCK_FarePriceScaleMonthTicketXType] xd
							WHERE
								xd.[FarePriceTableNumber] = 1
								AND xd.[FarePriceScaleMonthTicket_ID] = (
									SELECT fps.[id]
									FROM [DMKK].[dbo].[TCK_FarePriceScale] fps
									WHERE
										fps.[FarePriceScaleNumber] = 300 AND
										fps.[FarePriceList_ID] = @FarePriceList_ID
								)
						)
					),
					[HandlingCharge],
					[Commission],
					[LuggageTicket],
					[FarePriceCityTicketType_ID],
					CASE WHEN @FarePriceScaleType_ID =3 THEN fp1.id ELSE NULL END,
					CASE WHEN @FarePriceScaleType_ID =3 THEN fp1.Parent_ID ELSE NULL END
				FROM [DMKK].[dbo].[TCK_FarePrice] fp1
				INNER JOIN yy4 ON (fp1.[FarePriceScaleMonthTicketXType_ID] = yy4.[id])

		
				
		-- LOGOWANIE
		IF  @@ROWCOUNT >0
		BEGIN
			SET @Log = @Log+'Taryfa '+ @Name+' została skopiowana'


		IF EXISTS(
			SELECT TOP 1 fps.ID
			FROM dbo.TCK_FarePriceScale fps
            INNER JOIN dbo.TCK_FarePriceList fpl
                ON fps.FarePriceList_ID = fpl.ID
			WHERE
				fps.[ID] = @FarePriceScale_id
                AND fpl.Company_ID <> @NewCompany_ID -- cennik tej samej firmy
				AND fps.[FarePriceScaleType_ID] IN (20,21) -- ulga kwotowa (BJ,BM)
				--AND fps.[FarePriceList_ID] <> @FarePriceList_ID
				)
			SET @Log = @Log+'. Wejdź w edycję skopiowanej taryfy i sprawdź ulgę(-i)!'

		END	

		---uzupełniania wzorów biletów miejskich
		
		--select @OldFarePriceList_ID , @FarePriceList_ID

		IF @FarePriceScaleType_ID =3 AND @OldFarePriceList_ID <> @FarePriceList_ID
		BEGIN
		
			-- BRAK WZORCA BIL. MIEJSKIEGO W INNYM CENNIKU
			IF NOT EXISTS(
						SELECT p1.Id FROM [dbo].[TCK_FarePrice] p1 
						INNER JOIN [dbo].[TCK_FarePrice] p2 ON p1.Name = p2.Name AND p1.Price = p2.Price AND p1.FarePriceCityTicketType_Id = p2.FarePriceCityTicketType_Id AND p1.ValidityArea = p2.ValidityArea
						INNER JOIN dbo.TCK_FarePriceScaleXDesignation xd ON xd.id = p2.FarePriceScaleXDesignation_ID
						INNER JOIN dbo.TCK_FarePriceScale s ON s.id = xd.FarePriceScale_ID
						WHERE s.FarePriceList_ID = @FarePriceScale_id 
						AND @OldFarePriceList_ID <> @FarePriceList_ID AND FarePriceScaleType_ID = 3 AND s.Name ='#CityTickets#'
						) 
			BEGIN
			

				INSERT INTO [dbo].[TCK_FarePrice] (
				[Name], 
				[FarePriceScaleXDesignation_ID],
				[Currency_ID],
				[Price],
				[PriceNumber],
				[XDistance],
				[XTicketPrice],
				[XBusStop],
				[Increment],
				[MinutesNumber],
				[DaysNumber],
				[RidesNumber],
				[ZoneNumber],
				[ValidFromTime],
				[ValidToTime],
				[FarePriceReduction_ID],
				[Parent_ID],
				[HandlingCharge],
				[Commission],
				[LuggageTicket],
				[FarePriceCityTicketType_ID],
				[FarePriceCityTicketGroup_ID],
				[ValidityArea],
				[LinesNumber],
				[PointsNumber],
				[TimeRestriction]
				)

				SELECT DISTINCT
				f2.[Name],
				(
					SELECT TOP 1 xx.Id FROM dbo.TCK_FarePriceScaleXDesignation xx
					INNER JOIN [DMKK].dbo.TCK_FarePriceScale ss ON ss.id = xx.FarePriceScale_ID
					WHERE ss.FarePriceList_ID = @FarePriceList_ID 
					AND @OldFarePriceList_ID <> @FarePriceList_ID AND ss.FarePriceScaleType_ID = 3 
					AND  ss.FarePriceScaleNumber = 300 AND xx.[FarePriceTableNumber] = 1 AND ss.Name ='#CityTickets#'
					
				) AS FarePriceScaleXDesignation_ID,	

				f2.[Currency_ID],
				f2.[Price],
				f2.[PriceNumber],
				f2.[XDistance],
				f2.[XTicketPrice],
				f2.[XBusStop],
				f2.[Increment],
				f2.[MinutesNumber],
				f2.[DaysNumber],
				f2.[RidesNumber],
				f2.[ZoneNumber],
				f2.[ValidFromTime],
				f2.[ValidToTime],
				f2.[FarePriceReduction_ID], 
				f2.[PARENT_ID],
				f2.[HandlingCharge],
				f2.[Commission],
				f2.[LuggageTicket],
				f2.[FarePriceCityTicketType_ID],
				f2.[FarePriceCityTicketGroup_ID],
				f2.[ValidityArea],
				f2.ID,
				f2.ID,
				f2.[TimeRestriction] 
				FROM [DMKK].[dbo].[TCK_FarePrice] f1							-- bilet
				INNER JOIN [DMKK].dbo.TCK_FarePrice f2 ON f1.Parent_ID = f2.id	-- wzorzec
				INNER JOIN [DMKK].dbo.TCK_FarePriceScaleXDesignation xd ON xd.id = f2.FarePriceScaleXDesignation_ID
				INNER JOIN [DMKK].dbo.TCK_FarePriceScale s ON s.id = xd.FarePriceScale_ID

				WHERE s.FarePriceList_ID = @OldFarePriceList_ID
				AND s.FarePriceScaleNumber = 300 AND xd.[FarePriceTableNumber] = 1		-- definiuje wzr bil miejsk ??

				AND NOT EXISTS( SELECT x.id FROM [dbo].[TCK_FarePrice] x 
									INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdx ON xdx.id = x.FarePriceScaleXDesignation_ID
									INNER JOIN dbo.TCK_FarePriceScale sx ON sx.id = xdx.FarePriceScale_ID
									WHERE x.Name = f2.Name AND x.Price = f2.Price AND x.FarePriceCityTicketType_Id = f2.FarePriceCityTicketType_Id AND x.ValidityArea = f2.ValidityArea
									AND sx.FarePriceList_ID = @FarePriceList_ID
									AND sx.FarePriceScaleNumber = 300 AND xdx.[FarePriceTableNumber] = 1 
									-- w danym cenniku nie ma wzorców
							   )
	
			
				-- uaktualniam taryfy biletow miejskich wzorcem
				
				
				UPDATE [dbo].[TCK_FarePrice]
					SET Parent_ID = pom.PatternId,
						PointsNumber = NULL,
						LinesNumber = NULL
				FROM
				(
					SELECT  
					pp1.id AS PatternId,	-- id wzorca
					pp2.id AS TicketId		-- id biletów
					FROM [dbo].[TCK_FarePrice] f1							-- bilet
					INNER JOIN dbo.TCK_FarePrice f2 ON f1.Parent_ID = f2.id	-- wzorzec
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xd ON xd.id = f2.FarePriceScaleXDesignation_ID
					INNER JOIN dbo.TCK_FarePriceScale s ON s.id = xd.FarePriceScale_ID
					INNER JOIN [dbo].[TCK_FarePrice] pp1 ON pp1.LinesNumber = f2.id AND pp1.PointsNumber = f2.ID  AND pp1.Parent_ID IS NULL -- wzorzec nowy
					INNER JOIN [dbo].[TCK_FarePrice] pp2 ON pp2.LinesNumber = f1.id AND pp2.PointsNumber = f2.ID AND pp2.Parent_ID IS NULL -- bilet nowy
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdx ON xdx.id = pp2.FarePriceScaleXDesignation_ID AND xdx.FarePriceScale_ID = @INDEX

					WHERE s.FarePriceList_ID = @OldFarePriceList_ID
					AND s.FarePriceScaleNumber = 300 AND xd.[FarePriceTableNumber] = 1	--definiuje wzr bil miejsk ??
				) pom
				WHERE [dbo].[TCK_FarePrice].id = pom.TicketId


				UPDATE [dbo].[TCK_FarePrice]
				SET LinesNumber = NULL,
					PointsNumber = NULL
				FROM
				(
					SELECT pp2.Parent_ID FROM [dbo].[TCK_FarePrice] pp2
					INNER JOIN dbo.TCK_FarePriceScaleXDesignation xdx ON xdx.id = pp2.FarePriceScaleXDesignation_ID AND xdx.FarePriceScale_ID = @INDEX
				) p
				WHERE p.Parent_ID = [dbo].[TCK_FarePrice].ID
		
			END

		END


	IF	ISNULL(@CopyLineRideAssigments,0) =1 
		AND @OldCompany_ID <> @NewCompany_ID	
	
		SET @Log = @Log+'Przypisania linii i kursów do taryfy nie będą uzupełniane~'





	SET NOCOUNT OFF;

		SELECT @Log AS Log 
		--SELECT @Log AS Log, @LineName AS LineName, @RideName AS RideName 

		IF (@NewTran = 1)
			COMMIT TRAN
	END TRY
	BEGIN CATCH
		IF (@NewTran = 1)
			ROLLBACK TRANSACTION
		DECLARE @ErrorMessage nvarchar(4000);
		DECLARE @ErrorSeverity int;
		DECLARE @ErrorState int;
		SELECT
			@ErrorMessage = ERROR_MESSAGE(),
			@ErrorSeverity = ERROR_SEVERITY(),
			@ErrorState = ERROR_STATE();
		RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState)
	END CATCH
END
GO
