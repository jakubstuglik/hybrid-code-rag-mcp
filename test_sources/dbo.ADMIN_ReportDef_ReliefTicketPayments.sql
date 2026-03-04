
 SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
CREATE PROCEDURE [dbo].[ADMIN_ReportDef_ReliefTicketPayments]
--ALTER PROCEDURE [dbo].[ADMIN_ReportDef_ReliefTicketPayments]
	@CompanyId								INT=0,
	@LicensedCompanyID						INT=0,
	@DateFrom								NVARCHAR(23)='1900-01-01',
	@DateTo									NVARCHAR(23)='1900-01-01',
	@RideIds								NVARCHAR(MAX)='',
	@PerLineMode							TINYINT =0,			--1 tryb z podziałem dla linii
	@OnlyPaymentsMode						TINYINT =0,			--0 tylko doplaty, 1 - sprzedaż i dopłaty 2 tylko sprzedaż
	@WithReturnsMode						TINYINT =0,			--SeparateReturns  Wydziel zwroty w oddzielnej lini zestawienia
	@OrderBy								TINYINT =0,			-- 0 - wielkość zniżki ,1 - kolejność ulg, 	2 - grupy ulg		
	@LineSkipNumberInLine					TINYINT =0,			--pomiń numer w nazwie linii
	@LineReplaceLineNumberEvidenceNumber	TINYINT =0,			--zastąp numer linii numerem ewidencyjnym
	@LineSeparateMonthAndSingleTickets		TINYINT =0,			--W zestawieniach na linie wydzielone bilety jednorazowe i miesięczne
	@ShowLineTicketReliefByRelief			TINYINT =0,			--Pokazuj dopłaty wg stawek ulg
	@Header									NVARCHAR(MAX)='',
	@Footer									NVARCHAR(MAX)='',
	@LineTicketJoin							TINYINT = 0,		--A1, A2, A3 W zestawieniach na linie bilet łączony na kilka kursów liczony jako
	@SkipCheckingRides						BIT = 0,			--Pomiń sprawdzanie rodzajów kursów dla biletów miesięcznych na relację
	@MonthTicketsSkipRelationsInvalidRides	BIT = 0,			--W biletach miesięcznych pomijaj tylko relacje z nieprawidłowym rodzajem kursu
	@CheckApperanceReturns					BIT = 0,			--Zaznacz wystepowanie zwrotów w lini zestawienia literką 'Z' 
	@Guid									NVARCHAR(50)='',
	@LineAddListOffices						BIT = 0,
	@LineShowOfficeCode						BIT = 0,
	@IncludeChildKeeper						BIT = 0,
	@AdditionalParams						NVARCHAR(50) = '',	--drukuj podsumowania ulg z identyczną wysokością ulgi,drukuj podsumowanie biletów jednorazowych, drukuj podsumowanie biletów miesięcznych, drukuj podsumowanie ogółem	
	@Statement								NVARCHAR(MAX)='',
	@RODO									TINYINT = 0,		-- 0 są dane po staremu, 1 - RODO
	@CompanyGovID							INT=0,
	@IfOrganizer							TINYINT=0,
	@CompanyIdS								NVARCHAR(MAX)='',
	@TicketLines							NVARCHAR(MAX)='',
	@CountingNettSum						TINYINT=0,
	@CountNettValuePerEachMonth				TINYINT=0,
	@TerritorialDiv							INT = 0, -- 0 - wszystkie 3 - województwo 2 - powiat 1 - gmina 
	@TerritoryIDs							VARCHAR(200) = '', --ID JST  jesli wybierzemy konkretne j.s.t, to początek lub koniec jednej z relacji biletu musi być w danej j.s.t. 
	@TerritorialDivType						TINYINT = 0,
	@TimeTableId							INT = 0, -- rozkład jazdy
	@lineIds								NVARCHAR(MAX), -- linie
	@LinePrintDiffVariant					BIT = 0,			--łaczenie linii z innymi wariantami
	@ForChosenLineMode						VARCHAR(600) = '',		--zahardkorowane parametry w wydruku dla linii min id raportu, idiki linii 
	@TicketValid							INT =0, -- 0 -wsystkie, 1- tylko bilety ważne w datach sprzedaży biletu 2-tylko bilety ważne na inny okres niż data sprzedaży biletu
	@SalePlace								INT =0,
	@UsersIds								NVARCHAR(MAX)='', -- Wybrani użytkownicy rejestrujący raport
	@DateValidFrom							VARCHAR(23) = '1900-01-01',   --filtr na daty ważności w połączeniu z @TicketValid=3
	@DateValidTo							VARCHAR(23) = '1900-01-01',
	@SpecialCountLineTickets				TINYINT = 0 --Czy liczba biletów ma być identyczna z wydrukiem zbiorczym, na podstawie którego jest wydruk na linię.
	WITH EXECUTE AS 'inf_seluser'
AS
BEGIN
	SET ANSI_WARNINGS OFF
	SET NOCOUNT ON

	DECLARE @Time DATETIME = GETDATE()
	--SET @CompanyId = 1
	--SET @LicensedCompanyID = @CompanyId
	SET @UsersIds = ISNULL(@UsersIds,'')
	SET @CountingNettSum = ISNULL(@CountingNettSum,0) 
	SET @CompanyGovID = ISNULL(@CompanyGovID,0)
	SET @IfOrganizer = ISNULL(@IfOrganizer,0)
	SET @CompanyIdS = ISNULL(@CompanyIdS,'')
	SET @CountNettValuePerEachMonth = ISNULL(@CountNettValuePerEachMonth,0)
	SET @TicketValid = ISNULL(@TicketValid,0)
	SET @SalePlace = ISNULL(@SalePlace,0)
	SET @UsersIds = ISNULL(@UsersIds,'')

	SET @TerritorialDiv = ISNULL(@TerritorialDiv,0)
	SET @TerritoryIDs = ISNULL(@TerritoryIDs,'')
	SET @TerritorialDivType = ISNULL(@TerritorialDivType,0)
	SET @SpecialCountLineTickets = 0  -- tylko dla trybu dla linii obsługa później
	SET @LinePrintDiffVariant	= ISNULL(@LinePrintDiffVariant,0)

	DECLARE @UnsetLineTicketReliefByRelief INT = 0 

	IF ISNULL(@ShowLineTicketReliefByRelief,0) = 0
	BEGIN
		SET @ShowLineTicketReliefByRelief = 1
			
		SET @UnsetLineTicketReliefByRelief = 1
	END

	IF @IfOrganizer=0
	BEGIN
		SET @CompanyIdS =''
	END

	IF ISNULL(@LineSeparateMonthAndSingleTickets,0)=1
		SET @OnlyPaymentsMode=0

	DECLARE @ReportResultID INT = NULL
	DECLARE @ReportResultExportDataID INT = NULL
	
	DECLARE @DateFromF DATETIME 
	DECLARE @DateToF DATETIME

	SET @DateFromF =CONVERT(DATE, @DateFrom,121)

	SET @DateToF =CONVERT(DATE, @DateTo,121)

	DECLARE @DateValidFromF DATE = CONVERT(DATE,@DateValidFrom,121)

	DECLARE @DateValidToF DATE = CONVERT(DATE,@DateValidTo,121)
	
	SET @IncludeChildKeeper = ISNULL(@IncludeChildKeeper,0)

	SET @LineShowOfficeCode = ISNULL(@LineShowOfficeCode,0)

	SET @LineAddListOffices = ISNULL(@LineAddListOffices,0)

	SET @LineSeparateMonthAndSingleTickets = ISNULL(@LineSeparateMonthAndSingleTickets,0)

	SET @ShowLineTicketReliefByRelief = ISNULL(@ShowLineTicketReliefByRelief,0)
	
	SET @TicketLines = ISNULL(@TicketLines,'')
	
	SET @TimeTableId = ISNULL(@TimeTableId,0)
	SET @lineIds = ISNULL(@lineIds,'')
	SET @RideIds = ISNULL(@RideIds,'') 
	SET @LineSkipNumberInLine = ISNULL(@LineSkipNumberInLine,0)
	SET @LineReplaceLineNumberEvidenceNumber = ISNULL(@LineReplaceLineNumberEvidenceNumber,0)

	SET @ShowLineTicketReliefByRelief = ISNULL(@ShowLineTicketReliefByRelief,0)
	SET @Header =ISNULL(@Header,'')
	SET @Footer =ISNULL(@Footer,'')
	SET @LineTicketJoin =ISNULL(@LineTicketJoin,0)
	SET @SkipCheckingRides=ISNULL(@SkipCheckingRides, 0)
	SET @MonthTicketsSkipRelationsInvalidRides=ISNULL(@MonthTicketsSkipRelationsInvalidRides, 0)
	SET @CheckApperancereturns=ISNULL(@CheckApperancereturns, 0)
	SET @OnlyPaymentsMode=ISNULL(@OnlyPaymentsMode, 0)

	DECLARE @Territorys TABLE (id INT);  
	DECLARE @TerritorysCount INT = 0;

	IF object_id('tempdb..#PomTicketsRoute') IS NOT NULL
		DROP TABLE #PomTicketsRoute
--wybranie ticketrout, które wezmą udział w analizie
	CREATE TABLE #PomTicketsRoute (TicketRouteId INT, PassangerNumber BIT, SkipInDoplaty BIT, ToDel TINYINT DEFAULT 0, Period VARCHAR(8) COLLATE POLISH_CI_AS DEFAULT '', JST MONEY DEFAULT 1, NotTake TINYINT DEFAULT 0)  -- 1/2-przystanek w JST, 1 - oba w JST, 0 - brak w JST 

	SET @ForChosenLineMode = ISNULL(@ForChosenLineMode,'')
	DECLARE @ReportID INT =0

	IF object_id('tempdb..#PomRelief') IS NOT NULL
		DROP TABLE #PomRelief

	IF object_id('tempdb..#PomRedIds') IS NOT NULL
		DROP TABLE #PomRedIds
	
	CREATE TABLE #PomRedIds (ReductionId INT, ReductionHistoryId INT, ReductionPercentage INT)	
	
	--wybranie ulg bioroących udział w analizie
	INSERT INTO #PomRedIds (ReductionId, ReductionHistoryId, ReductionPercentage)
		SELECT DISTINCT r.ID, h.Id, h.Reduction
		FROM TCK_FarePriceReductiON r WITH (NOLOCK)
		INNER JOIN TCK_FarePriceReductionLegalPref l  WITH (NOLOCK) ON l.FarePriceReduction_ID=r.id
		INNER JOIN TCK_FarePriceReductionHistory h WITH (NOLOCK) ON h.FarePriceReduction_ID=r.id
		WHERE r.FarePriceReductionGroup_ID IN (1, 2, 3, 12)
		AND ISNULL(l.SkipReduction, 0) = 0
		AND NOT (NOT h.ValidTo IS NULL AND CAST(h.ValidTo AS DATE) < CAST(@DateFromF AS DATE)) 
		AND NOT CAST(h.ValidFROM AS DATE) > CAST(@DateToF AS DATE)

	
	IF object_id('tempdb..#PomCompanyIds') IS NOT NULL
		DROP TABLE #PomCompanyIds	

	CREATE TABLE #PomCompanyIds (CompanyId INT)	
	
	IF @IfOrganizer >0
	BEGIN	
		IF @CompanyIdS <> ''
		BEGIN
			INSERT INTO #PomCompanyIds (CompanyId)
			SELECT value FROM [dbo].[ADMIN_SplitString]( @CompanyIdS, ',') 
		END
	END


	DECLARE @Users TABLE (id INT);

	IF ISNULL(@UsersIDs,'') <>''
	BEGIN
		INSERT INTO @Users
		SELECT value AS id
		FROM dbo.admin_splitstring(@UsersIDs, ';')

	END;

	CREATE TABLE #TicketRoutePom (TicketRouteIDPom INT)

	--CREATE TABLE #
	--tryb wydruku dla wybranych linii z istniejącego zestawienia
	IF @ForChosenLineMode <>'' AND CHARINDEX(';',@ForChosenLineMode) >0 
	BEGIN
		
		DECLARE @LineSIds VARCHAR(600) =''
		SET @TimeTableId = 0

		--@ForChosenLineMode - przykładowa wartość-   12345*1;3,56
		SET @LineSIds = SUBSTRING(@ForChosenLineMode,CHARINDEX(';',@ForChosenLineMode)+1, LEN(@ForChosenLineMode)) 
		SET @SpecialCountLineTickets =SUBSTRING(@ForChosenLineMode,CHARINDEX('*',@ForChosenLineMode)+1, 1)
		SET @RideIds = ''
		SET @lineIds = ''		
		SET @ReportID = SUBSTRING(@ForChosenLineMode,1, CHARINDEX('*',@ForChosenLineMode)-1)

		
		DECLARE @ForLines TABLE (id INT);

		IF ISNULL(@LineSIds,'') <>''
		BEGIN
			INSERT INTO @ForLines
			SELECT value AS id
			FROM dbo.admin_splitstring(@LineSIds, ',')

		END;


		INSERT INTO #PomTicketsRoute (TicketRouteId, SkipInDoplaty, PassangerNumber, Period, JST)
	
		SELECT x.Id, SkipInDoplaty, PassangerNumber, Period,
		CASE WHEN @TerritorysCount >0 AND @TerritorialDivType=0 AND IsNull(t1.id,0)>0 AND IsNull(t2.id,0)>0 THEN 1 
		ELSE
		CASE WHEN @TerritorysCount >0 AND @TerritorialDivType=1 AND IsNull(t1.id,0)=0 AND IsNull(t2.id,0)=0 THEN 1
		ELSE
			CASE WHEN @TerritorysCount >0 AND @TerritorialDivType IN (0,1)  AND (IsNull(t1.id,0)>0 AND IsNull(t2.id,0)=0 OR IsNull(t1.id,0)=0 AND IsNull(t2.id,0)>0) THEN 0.5   ELSE 1
			END 
		END 
		END AS JST
		FROM
		( 
			SELECT tr.id, tr.SkipInDoplaty, CASE WHEN t.PassangerNumber >0 THEN 1 ELSE 0 END AS PassangerNumber,
			CASE WHEN @CountNettValuePerEachMonth=1 THEN CAST(SaleMonth AS VARCHAR)+CAST(SaleYear AS VARCHAR) ELSE '' END AS Period,
		
		CASE ISNULL(@TERRITORIALDIV,0) 
			WHEN 0 THEN 0 
			WHEN 1 THEN PL_FROM.COMMUNITY_ID   --GMINY
			WHEN 2 THEN PL_FROM.DISTRICT_ID		--POWIATY
			WHEN 3 THEN PL_FROM.PROVINCE_ID  --WOJEWÓDZTWA
		END AS TERYT_ID_FROM, --PRZYSTANEK POCZĄTKOWY TAM LUB KOŃCOWY POWRÓT
		CASE ISNULL(@TERRITORIALDIV,0) 
			WHEN 0 THEN 0 
			WHEN 1 THEN PL_TO.COMMUNITY_ID   --GMINY
			WHEN 2 THEN PL_TO.DISTRICT_ID		--POWIATY
			WHEN 3 THEN PL_TO.PROVINCE_ID  --WOJEWÓDZTWA
		END AS TERYT_ID_TO --PRZYSTANEK KOŃCOWY TAM LUB POCZĄTKOWY POWRÓT
		FROM SLS_TicketRoute tr WITH (NOLOCK)
		INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON tr.Ticket_ID=t.id
		INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.ID = tr.RideRegistered_ID
		INNER JOIN  dbo.ADMIN_ReportResultXTicketRoute x  WITH (NOLOCK) ON x.TicketRoute_ID = tr.ID
		INNER JOIN dbo.ADMIN_ReportResultExportData e WITH (NOLOCK) ON x.ReportResultExportData_ID = e.ID
		LEFT JOIN dbo.TT_RideRoute ridetam1from WITH (NOLOCK) ON ridetam1from.ID=tr.RideRouteFrom_ID
		LEFT JOIN dbo.TT_RideRoute ridetam1to WITH (NOLOCK) ON ridetam1to.ID=tr.RideRouteTo_ID
		LEFT JOIN TT_RoadPoint rp_from WITH (NOLOCK) ON rp_from.ID=ridetam1from.RoadPoint_ID
		LEFT JOIN TT_RoadPoint rp_to WITH (NOLOCK) ON rp_to.ID=ridetam1to.RoadPoint_ID
		LEFT JOIN TT_Place pl_from WITH (NOLOCK) ON pl_from.ID=rp_from.Place_ID 
		LEFT JOIN TT_Place pl_to WITH (NOLOCK) ON pl_to.ID=rp_to.Place_ID 	
		INNER JOIN dbo.TT_Ride r ON rr.Ride_ID = r.ID
		INNER JOIN @ForLines l ON l.id = r.line_id
		WHERE ReportResult_ID = @ReportID
		) x
		LEFT JOIN @Territorys t1 ON t1.id = x.Teryt_ID_from
		LEFT JOIN @Territorys t2 ON t2.id = x.Teryt_ID_to
		WHERE
		(@TerritorysCount=0) OR --nie wybrano jednostek
		((@TerritorysCount>0) AND  --wybrano jednostki
		 (
		 ((@TerritorialDivType=0) AND (((IsNull(t1.id,0)>0)) OR (IsNull(t2.id,0)>0))) OR  --jest w jst
		 ((@TerritorialDivType=1) AND ((IsNull(t1.id,0)=0) OR (IsNull(t2.id,0)=0)))  --poza jst		 
		 )
		)		


		--TABELKA potrzebna do specjalnego wyliczania liczby biletów w trybie dopłat dla linii
		INSERT INTO #TicketRoutePom (TicketRouteIDPom)
		SELECT TR.id AS TicketRouteIDPom
		FROM SLS_TicketRoute tr WITH (NOLOCK)
		INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON tr.Ticket_ID=t.id
		INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.ID = tr.RideRegistered_ID
		INNER JOIN  dbo.ADMIN_ReportResultXTicketRoute x  WITH (NOLOCK) ON x.TicketRoute_ID = tr.ID
		INNER JOIN dbo.ADMIN_ReportResultExportData e WITH (NOLOCK) ON x.ReportResultExportData_ID = e.ID
		WHERE ReportResult_ID = @ReportID AND ISNULL(SkipInDoplaty,0)=0

		
		IF @PerLineMode >0
		BEGIN
			DECLARE @LCnt INT =0
			DECLARE @LineText VARCHAR(MAX)=''
			SELECT @LineText = @LineText+', '+LineNumber +' '+Name From dbo.TT_Line l INNER JOIN @ForLines fl ON l.id=fl.id

			SELECT @LCnt= COUNT(*) FROM @ForLines
			SET @LineText = CASE WHEN @LCnt=1 THEN 'Dla linii: ' ELSE 'Dla lini: ' END+  SUBSTRING(@LineText,2,LEN(@LineText)) 
			INSERT INTO admin_reportresult (Name, ReportType_ID, ReportDef_id, Report, Created, MODIFIED, ReportOwner_id, Company_ID, DateFrom, DateTo, Params)
			SELECT @LineText+','+Name, ReportType_ID, ReportDef_id, Report, GetDate(), GetDate(), ReportOwner_id, Company_ID, DateFrom, DateTo, CAST(@ReportID AS VARCHAR) FROM dbo.admin_reportresult WHERE id=@ReportID
		END

		

		GOTO ForChosenLineMode   --przeskakujemy
		
	END

	--zestawienie dla wybranych kursów
	--wówczas ta tablica będzie miała rekordy
	CREATE TABLE #PomRideIds (RideId INT)	
	
	IF @RideIds <> '' OR @lineIds <>'' OR @TimeTableId>0
	BEGIN
		INSERT INTO #PomRideIds (RideId)
		SELECT y.ID AS Ride_id FROM dbo.TT_Ride y WITH (NOLOCK)
		INNER JOIN  [dbo].[ADMIN_SplitString]( @RideIds, ',') x ON y.ID = x.value
		INNER JOIN dbo.TT_TimeTableParamsRide(@TimeTableID) z ON z.Ride_id = y.ID
		UNION
		SELECT y.ID AS Ride_Id
		FROM dbo.TT_Ride  y WITH (NOLOCK)
		INNER JOIN dbo.ADMIN_SplitString(@lineIds, ';') x ON y.Line_id = x.value AND ISNULL(@RideIds,'')=''
		INNER JOIN dbo.TT_TimeTableParamsRide(@TimeTableID) z ON z.Ride_id = y.ID
		UNION
		SELECT y.Ride_id FROM dbo.TT_TimeTableParamsRide(@TimeTableID) y
		WHERE @TimeTableID>0 AND ISNULL(@RideIds,'')='' AND  ISNULL(@lineIds,'')=''

	END

	-- numery linii z biletów
	CREATE TABLE #PomTicketLines (LineNumber NVARCHAR(20) COLLATE POLISH_CI_AS)	
	
	IF @TicketLines <> ''
	BEGIN
		INSERT INTO #PomTicketLines (LineNumber)
		SELECT value FROM [dbo].[ADMIN_SplitString]( @TicketLines, ',') 
	END



	IF ISNULL(@TerritoryIDs,'') <>''
	BEGIN
		INSERT INTO @Territorys
		SELECT value AS Id
		FROM dbo.ADMIN_SplitString(@TerritoryIDs, ';')
	END
	set @TerritorysCount = (select COUNT(*) from @Territorys as count)

	
	INSERT INTO #PomTicketsRoute (TicketRouteId, SkipInDoplaty, PassangerNumber, Period, JST)
	
	SELECT x.Id, SkipInDoplaty, PassangerNumber, Period,

	CASE WHEN @TerritorysCount >0 AND @TerritorialDivType=0 AND IsNull(t1.id,0)>0 AND IsNull(t2.id,0)>0 THEN 1 
	ELSE
		CASE WHEN @TerritorysCount >0 AND @TerritorialDivType=1 AND IsNull(t1.id,0)=0 AND IsNull(t2.id,0)=0 THEN 1
		ELSE
			CASE WHEN @TerritorysCount >0 AND @TerritorialDivType IN (0,1)  AND (IsNull(t1.id,0)>0 AND IsNull(t2.id,0)=0 OR IsNull(t1.id,0)=0 AND IsNull(t2.id,0)>0) THEN 0.5   ELSE 1
			END 
		END 
	END AS JST
	FROM
	( 
	SELECT tr.id, tr.SkipInDoplaty, CASE WHEN t.PassangerNumber >0 THEN 1 ELSE 0 END AS PassangerNumber,
		CASE WHEN @CountNettValuePerEachMonth=1 THEN CAST(SaleMonth AS VARCHAR)+CAST(SaleYear AS VARCHAR) ELSE '' END AS Period,
		
		CASE ISNULL(@TERRITORIALDIV,0) 
			WHEN 0 THEN 0 
			WHEN 1 THEN PL_FROM.COMMUNITY_ID   --GMINY
			WHEN 2 THEN PL_FROM.DISTRICT_ID		--POWIATY
			WHEN 3 THEN PL_FROM.PROVINCE_ID  --WOJEWÓDZTWA
		END AS TERYT_ID_FROM, --PRZYSTANEK POCZĄTKOWY TAM LUB KOŃCOWY POWRÓT
		CASE ISNULL(@TERRITORIALDIV,0) 
			WHEN 0 THEN 0 
			WHEN 1 THEN PL_TO.COMMUNITY_ID   --GMINY
			WHEN 2 THEN PL_TO.DISTRICT_ID		--POWIATY
			WHEN 3 THEN PL_TO.PROVINCE_ID  --WOJEWÓDZTWA
		END AS TERYT_ID_TO --PRZYSTANEK KOŃCOWY TAM LUB POCZĄTKOWY POWRÓT
		FROM SLS_TicketRoute tr WITH (NOLOCK)
		INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON tr.Ticket_ID=t.id
		INNER JOIN dbo.SLS_FiscalReport f WITH (NOLOCK) ON t.FiscalReport_ID = f.ID
		LEFT JOIN SLS_SalesReport salrep WITH(NOLOCK) ON f.SalesReport_ID=salrep.ID
		INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK)ON rr.Id=tr.RideRegistered_ID
		LEFT JOIN dbo.TCK_FarePriceReductionLegalPref l WITH (NOLOCK) ON l.FarePriceReduction_ID = t.FarePriceReduction_ID
		INNER JOIN (SELECT DISTINCT ReductionId FROM #PomRedIds) red ON red.ReductionId = t.FarePriceReduction_ID
		LEFT JOIN dbo.TT_ride r WITH (NOLOCK) ON r.ID = tr.Ride_ID
		LEFT JOIN dbo.TT_Line ln WITH (NOLOCK) ON ln.id = r.Line_ID
		LEFT JOIN #PomCompanyIds c WITH (NOLOCK) ON c.CompanyId = tr.CompanyOwner_ID
		LEFT JOIN #PomTicketLines tl WITH (NOLOCK) ON tl.LineNumber = rr.LineNumber 

		LEFT JOIN dbo.TT_RideRoute ridetam1from WITH (NOLOCK) ON ridetam1from.ID=tr.RideRouteFrom_ID
		LEFT JOIN dbo.TT_RideRoute ridetam1to WITH (NOLOCK) ON ridetam1to.ID=tr.RideRouteTo_ID

		LEFT JOIN TT_RoadPoint rp_from WITH (NOLOCK) ON rp_from.ID=ridetam1from.RoadPoint_ID
		LEFT JOIN TT_RoadPoint rp_to WITH (NOLOCK) ON rp_to.ID=ridetam1to.RoadPoint_ID

		LEFT JOIN TT_Place pl_from WITH (NOLOCK) ON pl_from.ID=rp_from.Place_ID 
		LEFT JOIN TT_Place pl_to WITH (NOLOCK) ON pl_to.ID=rp_to.Place_ID 

		WHERE 
		t.SalesReport_ID IS NULL AND --wzorce biletów
		--pomijanie biletów pomijanych i wzorców biletów
		ISNULL(tr.SkipInDoplaty, 0)=0 

		AND NOT t.FiscalReport_ID IS NULL AND t.FarePriceReduction_ID IS NOT NULL
		--wybieranie tras tylko konkretnej firmy
		AND (tr.CompanyOwner_ID=ISNULL(@companyid, 0) AND @IfOrganizer =0 OR @IfOrganizer =1)
		--okres sprzedazy
		AND (CAST(t.SaleDate AS DATE) BETWEEN @DateFromF AND @DateToF)
		AND (@TicketValid =0 OR @TicketValid =1 AND CAST(t.SaleDate AS DATE) BETWEEN t.ValidFrom AND t.ValidTo 
			OR @TicketValid =2 AND NOT CAST(t.SaleDate AS DATE) BETWEEN t.ValidFrom AND t.ValidTo
			OR @TicketValid =3 AND  CAST(t.ValidFrom AS DATE) BETWEEN @DateValidFromF AND @DateValidToF)

		AND t.TicketType_ID IN (1, 2, 3, 7, 8, 17, 18) AND t.TicketGenre_ID IN (2, 3)
		AND f.ReportNumber >0
		AND t.TicketUpdate_ID IS NULL

		AND (ln.CompanyGov_ID = @CompanyGovID OR @CompanyGovID = 0)
		AND (c.CompanyId IS NOT NULL AND @CompanyIdS <>'' AND @IfOrganizer =1 OR @IfOrganizer =0 OR @IfOrganizer =1 AND @CompanyIdS='')
		AND (@TicketLines <>'' AND tl.LineNumber IS NOT NULL OR @TicketLines ='')
		AND ((ISNULL(@UsersIDs,'')='') OR  (salrep.User_ID IN (SELECT ID FROM @Users)))
		AND (IsNull(@SalePlace, 0) = 0 or 1 =
	    (CASE 
		   WHEN @SalePlace = 1 and salrep.ReportType_ID in (6,8,9,15,30,34,35,36,51) THEN 1
		   WHEN @SalePlace = 2 and salrep.ReportType_ID in (3,32) THEN 1
		   WHEN @SalePlace = 3 and salrep.ReportType_ID in (7,31) THEN 1
		   ELSE 0
		 END))

		) x
		LEFT JOIN @Territorys t1 ON t1.id = x.Teryt_ID_from
		LEFT JOIN @Territorys t2 ON t2.id = x.Teryt_ID_to
		WHERE
		(@TerritorysCount=0) OR --nie wybrano jednostek
		((@TerritorysCount>0) AND  --wybrano jednostki
		 (
		 ((@TerritorialDivType=0) AND (((IsNull(t1.id,0)>0)) OR (IsNull(t2.id,0)>0))) OR  --jest w jst
		 ((@TerritorialDivType=1) AND ((IsNull(t1.id,0)=0) OR (IsNull(t2.id,0)=0)))  --poza jst		 
		 )
		)
	
	--	select * from #PomTicketsRoute


	DECLARE @c INT
	SELECT @c = Count(*) FROM #PomRideIds

	IF ISNULL(@c,0)=0 AND (@RideIds <> '' OR @lineIds <>'' OR @TimeTableId>0)--kiedy nie ma żadnego kursu

		DELETE FROM #PomTicketsRoute

	IF @c > 0
	BEGIN
		--branie pod uwage tylko okreslonych kursow
		DELETE FROM #PomTicketsRoute
			WHERE TicketRouteId NOT IN (
				SELECT TicketRouteId FROM #PomTicketsRoute
				INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.Id=#PomTicketsRoute.TicketRouteId
				INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON tr.RideRegistered_ID=rr.id
				WHERE rr.Ride_ID IN (SELECT RideId FROM #PomRideIds) 
			)
		
	END

	CREATE TABLE #Exclude (Ticket_ID INT, SaleDate DATE, RideDate DATETIME, INumber INT, RideNumber INT, RideVariant NVARCHAR(1) COLLATE POLISH_CI_AS, RideValidFrom DATETIME,
							BusStopCodeFrom INT, BusStopCodeTo INT, BusStopNoFrom INT, BusStopNoTo INT, FarePriceReductionGroup_ID INT, ReductionNumber INT, SkipInDoplaty BIT NULL)

	INSERT INTO #Exclude (Ticket_ID, SaleDate, RideDate, INumber, RideNumber, RideVariant, RideValidFrom,
							BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo, FarePriceReductionGroup_ID, ReductionNumber, SkipInDoplaty)
	SELECT 
				tr.Ticket_ID, CAST(t.SaleDate AS DATE) AS SaleDate, rr.RideDate, rr.INumber, rr.RideNumber, rr.RideVariant, ISNULL(rr.RideValidFrom,'1900-01-01') AS RideValidFrom,
				tr.BusStopCodeFrom, tr.BusStopCodeTo, tr.BusStopNoFrom, tr.BusStopNoTo,
				r.FarePriceReductionGroup_ID, r.ReductionNumber, tr.SkipInDoplaty
				FROM #PomTicketsRoute WITH (NOLOCK)
				INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
				INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.Id=tr.RideRegistered_ID
				INNER JOIN dbo.TCK_FarePriceReduction r WITH (NOLOCK) ON r.id = t.FarePriceReduction_ID

	
	----eliminowanie biletow ulgowych i miesiecznych, które mają typ kursu niepasujący do ulgi

	UPDATE #PomTicketsRoute
		SET ToDel=1
	WHERE TicketRouteId IN (	
		-- OPCJA: Pomiń sprawdzanie rodzajów komunikacji kursów dla biletów miesięcznych sprzedanych na relację
		SELECT TicketRouteId
		FROM #PomTicketsRoute WITH (NOLOCK)
		INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
		INNER JOIN SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
		INNER JOIN TCK_FarePriceReductiON frp WITH (NOLOCK) ON frp.Id=t.FarePriceReduction_ID
		INNER JOIN TCK_FarePriceReductionLegalPref l WITH (NOLOCK) ON l.FarePriceReduction_ID = frp.ID
		INNER JOIN SLS_RideRegistered rr WITH (NOLOCK) ON rr.id=tr.RideRegistered_ID
		WHERE 
			(@MonthTicketsSkipRelationsInvalidRides = 0 AND @SkipCheckingRides =0
			OR @SkipCheckingRides =1 AND MonthTicketType<>1			
			 )
			AND t.id IN (
				SELECT DISTINCT t.Id
				FROM #PomTicketsRoute WITH (NOLOCK)
				INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
				INNER JOIN SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
				INNER JOIN TCK_FarePriceReductiON frp WITH (NOLOCK) ON frp.Id=t.FarePriceReduction_ID
				INNER JOIN TCK_FarePriceReductionLegalPref l WITH (NOLOCK) ON l.FarePriceReduction_ID = frp.ID
				INNER JOIN SLS_RideRegistered rr WITH (NOLOCK) ON rr.id=tr.RideRegistered_ID
				WHERE t.TicketType_ID IN (2, 3) 
				AND -200 =
					CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationZwykla_ID, 0) THEN rr.RideTypeCommunication_ID 
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPrzyspieszona_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPospieszna_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationEkspresowa_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE -200 END END END END
			)
					
		UNION 
		-- OPCJA : W biletach miesięcznych pomijaj tylko relacje z nieprawidłowym rodzajem komunikacji kursu		
		SELECT TicketRouteId
		FROM #PomTicketsRoute WITH (NOLOCK)
		INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
		INNER JOIN SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
		INNER JOIN TCK_FarePriceReductiON frp WITH (NOLOCK) ON frp.Id=t.FarePriceReduction_ID
		INNER JOIN TCK_FarePriceReductionLegalPref l WITH (NOLOCK) ON l.FarePriceReduction_ID = frp.ID
		INNER JOIN SLS_RideRegistered rr WITH (NOLOCK) ON rr.id=tr.RideRegistered_ID
		WHERE 
			(@MonthTicketsSkipRelationsInvalidRides = 1 AND /* @SkipCheckingRides =0 AND*/ t.TicketType_ID IN (2, 3))
			AND -200 =
					CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationZwykla_ID, 0) THEN rr.RideTypeCommunication_ID 
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPrzyspieszona_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPospieszna_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationEkspresowa_ID, 0) THEN rr.RideTypeCommunication_ID
					ELSE -200 END END END END


		UNION 
		--rodzaje komunikacji :komunikacja miejska, komunikacja międzynarodowa, pozostała komunikacja - pomijamy
		SELECT TicketRouteId
		FROM #PomTicketsRoute WITH (NOLOCK)
		INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
		INNER JOIN SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
		INNER JOIN TCK_FarePriceReduction frp WITH (NOLOCK) ON frp.Id=t.FarePriceReduction_ID
		INNER JOIN SLS_RideRegistered rr WITH (NOLOCK) ON rr.id=tr.RideRegistered_ID
		WHERE rr.RideTypeCommunication_ID >4

		UNION ALL
		-- nieprawidłowy rodzaj komunikacji bilety jednorazowe - zawsze odhaczam
		SELECT TicketRouteId
		FROM #PomTicketsRoute WITH (NOLOCK)
		INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=#PomTicketsRoute.TicketRouteId
		INNER JOIN SLS_Ticket t WITH (NOLOCK) ON t.id=tr.Ticket_ID
		INNER JOIN TCK_FarePriceReduction frp WITH (NOLOCK) ON frp.Id=t.FarePriceReduction_ID
		INNER JOIN TCK_FarePriceReductionLegalPref l WITH (NOLOCK) ON l.FarePriceReduction_ID = frp.ID
		INNER JOIN SLS_RideRegistered rr WITH (NOLOCK) ON rr.id=tr.RideRegistered_ID
		WHERE
			(	(t.TicketType_ID = 1
				AND -200 =
				CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationZwykla_ID, 0) THEN rr.RideTypeCommunication_ID 
				ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPrzyspieszona_ID, 0) THEN rr.RideTypeCommunication_ID
				ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationPospieszna_ID, 0) THEN rr.RideTypeCommunication_ID
				ELSE CASE WHEN ISNULL(rr.RideTypeCommunication_ID, -1) = ISNULL(l.RideTypeCommunicationEkspresowa_ID, 0) THEN rr.RideTypeCommunication_ID
				ELSE -200 END END END END)-- OR  t.TicketType_ID <> 1 
			)

	)

	--sprawdzanie par opiekun podopieczny
	
	------------------------------	
	------------------------------
	--przewodnik niewidomego				OK
	------------------------------	
	------------------------------
	UPDATE #PomTicketsRoute
	 SET ToDel=1
		WHERE TicketRouteId IN
		(SELECT id FROM SLS_TicketRoute  WITH (NOLOCK)WHERE Ticket_ID IN (
			SELECT a.Ticket_ID  
			FROM
			(	SELECT ROW_NUMBER() OVER ( PARTITION BY r.SaleDate,r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpP,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 6
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
			) a
			LEFT JOIN
			(	
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(SaleDate AS DATE), RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo ORDER BY Ticket_ID) AS LpO,
				Ticket_ID, SaleDate, RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo	
				FROM
				(
					SELECT r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
					r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
					FROM #Exclude r
					WHERE ((r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber IN (20,27,31,32)) or
						(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (6,9,10)))
					AND NOT EXISTS(SELECT an.ID FROM dbo.SLS_Ticket an  WITH (NOLOCK) WHERE an.TicketCancelled_ID=r.Ticket_id)
					AND r.SkipInDoplaty IS NULL					
					GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo

					UNION ALL
					--EM-KARTY
					SELECT 	xpr.ID AS Ticket_ID, CAST(rr.RideDate AS DATE) AS SaleDate, rr.RideDate, rr.INumber, rr.RideNumber, rr.RideVariant, ISNULL(rr.RideValidFrom,'1900-01-01') AS RideValidFrom,
					xpr.StartBusStopCode AS BusStopCodeFrom, xpr.EndBusStopCode AS BusStopCodeTo, xpr.StartBusStopNo AS BusStopNoFrom, xpr.EndBusStopNo AS BusStopNoTo
					FROM dbo.SLS_EmCardXPassangerRecording xpr  WITH (NOLOCK)
					INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON xpr.RideRegistered_ID = rr.ID 
					INNER JOIN dbo.TCK_FarePriceReduction r WITH (NOLOCK) ON r.id = xpr.Reduction_ID
					WHERE (CAST(rr.RideDate AS DATE) BETWEEN @DateFromF AND @DateToF AND
							(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (6,9,10))
						)
					GROUP BY xpr.ID, CAST(rr.RideDate AS DATE), rr.INumber, rr.RideNumber, rr.rideDate, rr.rideVariant, ISNULL(rr.RideValidFrom,'1900-01-01'), xpr.StartBusStopCode, xpr.EndBusStopCode, xpr.StartBusStopNo, xpr.EndBusStopNo
				) x


			) b
			ON CAST(b.SaleDate AS DATE)=CAST(a.SaleDate AS DATE) AND a.INumber = b.Inumber ANd a.RideNumber = b.RideNumber ANd a.rideDate = b.RideDate AND a.rideVariant = b.RideVariant AND ISNULL(a.RideValidFrom,'1900-01-01') = ISNULL(b.RideValidFrom,'1900-01-01')
			AND a.BusStopCodeFrom = b.BusStopCodeFrom AND a.BusStopCodeTo = b.BusStopCodeTo 
			AND a.BusStopNoFrom = b.BusStopNoFrom AND a.BusStopNoTo = b.BusStopNoTo
			AND b.LpO = a.LpP
			WHERE b.LpO IS NULL
		))

	------------------------------------
	------------------------------------
	--opiekun opiekun INwalidy wojennego OK
	------------------------------------
	------------------------------------

	UPDATE #PomTicketsRoute
	 SET ToDel=1
		WHERE TicketRouteId IN
		(SELECT id FROM SLS_TicketRoute WHERE Ticket_ID IN (
			SELECT a.Ticket_ID  
			FROM
			(	SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpP,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 11
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo 
			) a
			LEFT JOIN
			(	
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpO,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 9
				AND NOT EXISTS(SELECT an.ID FROM dbo.SLS_Ticket an  WITH (NOLOCK) WHERE an.TicketCancelled_ID=r.Ticket_ID)
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				) b
			ON CAST(b.SaleDate AS DATE)=CAST(a.SaleDate AS DATE) AND a.INumber = b.Inumber ANd a.RideNumber = b.RideNumber ANd a.rideDate = b.RideDate AND a.rideVariant = b.RideVariant AND ISNULL(a.RideValidFrom,'1900-01-01') = ISNULL(b.RideValidFrom,'1900-01-01')
			AND a.BusStopCodeFrom = b.BusStopCodeFrom AND a.BusStopCodeTo = b.BusStopCodeTo
			AND a.BusStopNoFrom = b.BusStopNoFrom AND a.BusStopNoTo = b.BusStopNoTo
			AND b.LpO = a.LpP
			WHERE b.LpO IS NULL
		))

	------------------------------	
	------------------------------
	--OPIEKUN DZ.NIEP. 			OK
	------------------------------	
	------------------------------
	IF @IncludeChildKeeper=1
		UPDATE #PomTicketsRoute
		SET ToDel=1
		WHERE TicketRouteId in
		(SELECT id FROM SLS_TicketRoute WITH (NOLOCK) WHERE Ticket_ID IN (
			SELECT a.Ticket_ID  
			FROM
			(	SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpP,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 8
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
			) a
			LEFT JOIN
			(	
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(SaleDate AS DATE), RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo ORDER BY Ticket_ID) AS LpO,
				Ticket_ID, SaleDate, RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo	
				FROM
				(
				SELECT r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 7 OR r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber = 3
				AND r.SkipInDoplaty IS NULL
				AND NOT EXISTS(SELECT an.ID FROM dbo.SLS_Ticket an WITH (NOLOCK) WHERE an.TicketCancelled_ID=r.Ticket_ID)
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo

				UNION ALL
				--EM-KARTY
				SELECT 	xpr.ID AS Ticket_ID, CAST(rr.RideDate AS DATE) AS SaleDate, rr.RideDate, rr.INumber, rr.RideNumber, rr.RideVariant, ISNULL(rr.RideValidFrom,'1900-01-01') AS RideValidFrom,
				xpr.StartBusStopCode AS BusStopCodeFrom, xpr.EndBusStopCode AS BusStopCodeTo, xpr.StartBusStopNo AS BusStopNoFrom, xpr.EndBusStopNo AS BusStopNoTo
				FROM dbo.SLS_EmCardXPassangerRecording xpr WITH (NOLOCK) 
				INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON xpr.RideRegistered_ID = rr.ID 
				INNER JOIN dbo.TCK_FarePriceReduction r WITH (NOLOCK) ON r.id = xpr.Reduction_ID
				WHERE (CAST(rr.RideDate AS DATE) BETWEEN @DateFromF AND @DateToF AND
						(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (3))
					)
				GROUP BY xpr.ID, CAST(rr.RideDate AS DATE), rr.INumber, rr.RideNumber, rr.rideDate, rr.rideVariant, ISNULL(rr.RideValidFrom,'1900-01-01'), xpr.StartBusStopCode, xpr.EndBusStopCode, xpr.StartBusStopNo, xpr.EndBusStopNo
				) x

				) b
			ON CAST(b.SaleDate AS DATE)=CAST(a.SaleDate AS DATE) AND a.INumber = b.Inumber ANd a.RideNumber = b.RideNumber ANd a.rideDate = b.RideDate AND a.rideVariant = b.RideVariant AND ISNULL(a.RideValidFrom,'1900-01-01') = ISNULL(b.RideValidFrom,'1900-01-01')
			AND a.BusStopCodeFrom = b.BusStopCodeFrom AND a.BusStopCodeTo = b.BusStopCodeTo
			AND a.BusStopNoFrom = b.BusStopNoFrom AND a.BusStopNoTo = b.BusStopNoTo
			AND b.LpO = a.LpP
			WHERE b.LpO IS NULL
		))  


		-------------------------------------
		-------------------------------------
		--ODDZIELNIE 
		-------------------------------------
		-------------------------------------
		CREATE TABLE #PomTicketsOpiekun (TicketRouteId INT)

		INSERT INTO #PomTicketsOpiekun (TicketRouteId)
		SELECT id FROM SLS_TicketRoute tr WITH (NOLOCK)
		INNER JOIN
		 (
			SELECT b.Ticket_ID, b.Common  
			FROM
			(	SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpP,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 6
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
			) a
			INNER JOIN
			(	
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpO,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo,
				MAX(CASE WHEN (r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber IN (20,27)) OR (r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (6)) THEN 0 ELSE 1 END) AS Common
				FROM #Exclude r
				WHERE ((r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber IN (20,27,31,32)) or
					(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (6,9,10)))
				AND NOT EXISTS(SELECT an.ID FROM dbo.SLS_Ticket an WITH (NOLOCK) WHERE an.TicketCancelled_ID=r.Ticket_ID)					
				AND r.SkipInDoplaty IS NULL
			GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				) b
			ON CAST(b.SaleDate AS DATE)=CAST(a.SaleDate AS DATE) AND a.INumber = b.Inumber ANd a.RideNumber = b.RideNumber ANd a.rideDate = b.RideDate AND a.rideVariant = b.RideVariant AND ISNULL(a.RideValidFrom,'1900-01-01') = ISNULL(b.RideValidFrom,'1900-01-01')
			AND a.BusStopCodeFrom = b.BusStopCodeFrom AND a.BusStopCodeTo = b.BusStopCodeTo
			AND a.BusStopNoFrom = b.BusStopNoFrom AND a.BusStopNoTo = b.BusStopNoTo
			AND a.LpP = b.LpO
			) x
			ON tr.Ticket_ID =x.Ticket_Id AND Common=1


		------------------------------	
		------------------------------				
		--opiekun osoby niesamodzielnej
		------------------------------
		------------------------------


		UPDATE #PomTicketsRoute
		SET ToDel=1
		WHERE TicketRouteId IN
		(SELECT id FROM SLS_TicketRoute WITH (NOLOCK) WHERE Ticket_ID IN (
			SELECT a.Ticket_ID FROM 
			(
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(r.SaleDate AS DATE), r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo ORDER BY r.Ticket_ID) AS LpP,
				r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
				WHERE r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber = 17
				AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
			) a
			LEFT JOIN
			(	
				SELECT ROW_NUMBER() OVER (PARTITION BY CAST(SaleDate AS DATE), RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo ORDER BY Ticket_ID) AS LpO,
				Ticket_ID, SaleDate, RideDate, INumber, RideNumber, RideVariant, RideValidFrom, BusStopCodeFrom, BusStopCodeTo, BusStopNoFrom, BusStopNoTo	
				FROM
				(
				SELECT r.Ticket_ID, r.SaleDate, r.RideDate, r.INumber, r.RideNumber, r.RideVariant, ISNULL(r.RideValidFrom,'1900-01-01') AS RideValidFrom,
				r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo
				FROM #Exclude r
					INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON r.Ticket_ID = tr.Ticket_ID
					INNER JOIN #PomTicketsRoute x WITH (NOLOCK) ON x.TicketRouteId = tr.ID
					WHERE ((r.FarePriceReductionGroup_ID = 1 AND r.ReductionNumber IN (24,25,31,32)) or
					(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (9, 10)))
					AND NOT EXISTS(SELECT an.ID FROM dbo.SLS_Ticket an WITH (NOLOCK) WHERE an.TicketCancelled_ID=r.Ticket_ID)
					AND NOT EXISTS(SELECT y.TicketRouteId FROM #PomTicketsOpiekun y WITH (NOLOCK) WHERE y.TicketRouteId = tr.id)
					AND r.SkipInDoplaty IS NULL
				GROUP BY r.Ticket_ID, r.SaleDate, r.INumber, r.RideNumber, r.rideDate, r.rideVariant, ISNULL(r.RideValidFrom,'1900-01-01'), r.BusStopCodeFrom, r.BusStopCodeTo, r.BusStopNoFrom, r.BusStopNoTo

				UNION ALL
				--EM-KARTY
				SELECT 	xpr.ID AS Ticket_ID, CAST(rr.RideDate AS DATE) AS SaleDate, rr.RideDate, rr.INumber, rr.RideNumber, rr.RideVariant, ISNULL(rr.RideValidFrom,'1900-01-01') AS RideValidFrom,
				xpr.StartBusStopCode AS BusStopCodeFrom, xpr.EndBusStopCode AS BusStopCodeTo, xpr.StartBusStopNo AS BusStopNoFrom, xpr.EndBusStopNo AS BusStopNoTo
				FROM dbo.SLS_EmCardXPassangerRecording xpr WITH (NOLOCK)
				INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON xpr.RideRegistered_ID = rr.ID 
				INNER JOIN dbo.TCK_FarePriceReduction r WITH (NOLOCK) ON r.id = xpr.Reduction_ID
				WHERE (CAST(rr.RideDate AS DATE) BETWEEN @DateFromF AND @DateToF AND
						(r.FarePriceReductionGroup_ID = 3 AND r.ReductionNumber IN (9, 10))	)
				GROUP BY xpr.ID, CAST(rr.RideDate AS DATE), rr.INumber, rr.RideNumber, rr.rideDate, rr.rideVariant, ISNULL(rr.RideValidFrom,'1900-01-01'), xpr.StartBusStopCode, xpr.EndBusStopCode, xpr.StartBusStopNo, xpr.EndBusStopNo

				) x


				) b
				ON CAST(b.SaleDate AS DATE)=CAST(a.SaleDate AS DATE) AND a.INumber = b.Inumber ANd a.RideNumber = b.RideNumber ANd a.rideDate = b.RideDate AND a.rideVariant = b.RideVariant AND ISNULL(a.RideValidFrom,'1900-01-01') = ISNULL(b.RideValidFrom,'1900-01-01')
				AND a.BusStopCodeFrom = b.BusStopCodeFrom AND a.BusStopCodeTo = b.BusStopCodeTo
				AND a.BusStopNoFrom = b.BusStopNoFrom AND a.BusStopNoTo = b.BusStopNoTo
				AND b.LpO = a.LpP			
				WHERE b.LpO IS  NULL
		))

			

		------------------------------	
		------------------------------
		-----Automatyczne pomijanie biletów sprzedanych z nieprawidłowymi ulgami
		------------------------------	
		------------------------------

		UPDATE #PomTicketsRoute
		SET ToDel=1
		WHERE TicketRouteId IN
		(	SELECT tr.id
			FROM dbo.SLS_Ticket t WITH (NOLOCK)
			INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON t.id = tr.Ticket_ID
			INNER JOIN #PomTicketsRoute x WITH (NOLOCK) ON x.TicketRouteId = tr.Id
			INNER JOIN dbo.TCK_FarePriceReduction r WITH (NOLOCK) ON r.Id = t.FarePriceReduction_ID
			INNER JOIN dbo.TCK_FarePriceReductionHistory h WITH (NOLOCK) ON h.FarePriceReduction_ID = r.id 
			WHERE CONVERT(DATE,t.SaLeDate,121) BETWEEN CONVERT(DATE,h.ValidFrom,121) AND CONVERT(DATE,ISNULL(h.ValidTo,'2100-01-01'),121)
				AND h.Reduction <> t.ReductionPercentage
		)


	-- UZUPEŁNIANIE SKIPINDOPLATY
	--select * from #PomTicketsRoute order by ToDel desc

	UPDATE dbo.SLS_TicketRoute
	SET SkipInDoplaty = 1
	FROM
	(	SELECT tr.ID
		FROM #PomTicketsRoute r WITH (NOLOCK)
		INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=r.TicketRouteId
		WHERE r.ToDel=1 AND tr.SkipInDoplaty IS NULL

	) pom
	WHERE dbo.SLS_TicketRoute.Id = pom.ID 


	UPDATE dbo.SLS_TicketRoute
	SET SkipInDoplaty = 0
	FROM
	(	SELECT tr.ID
		FROM #PomTicketsRoute r WITH (NOLOCK)
		INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.id=r.TicketRouteId
		WHERE r.ToDel=0 AND tr.SkipInDoplaty IS NULL

	) pom
	WHERE dbo.SLS_TicketRoute.Id = pom.ID 
	--select * from #PomTicketsRoute
	DELETE FROM #PomTicketsRoute WHERE ToDel=1
	


	ForChosenLineMode:
		
	--	select * from #PomTicketsRoute
	---------------------------------------------------------------
	------------NAPISY Z FIRMAMI I BILETERKAMI---------------------
	---------------------------------------------------------------

		DECLARE @Bileterki NVARCHAR(MAX) =''
		DECLARE @FirmyOwn NVARCHAR(MAX)=''
		DECLARE @FirmyForeign NVARCHAR(MAX)=''
		DECLARE @Firmy NVARCHAR(MAX)=''

		SELECT
			@Bileterki = Bileterki,
			@FirmyForeign = @FirmyForeign + FirmyForeign,
			@Firmy = Firmy
		FROM
		(
			SELECT DISTINCT 
		
			CASE WHEN @IfOrganizer=1 THEN CASE WHEN @CompanyIdS<>'' THEN 'Sprzedaż zarejestrowana w bileterkach przewoźników: %'+Firmy+' %%Typy używanych bileterek: ' ELSE 'Sprzedaż zarejestrowana w bileterkach przewoźników: wszyscy %%Typy używanych bileterek: ' END ELSE FirmaLicencjaBil END + 
			ISNULL(SUBSTRING(BileterkaWlasna,2,LEN(BileterkaWlasna)),'') + CASE WHEN ISNULL(BileterkaWlasna,'')<>'' THEN ',' ELSE '' END + CASE WHEN BileterkaObca<>'' THEN ' OBCE ('+ SUBSTRING(BileterkaObca,2, LEN(BileterkaObca))+')' ELSE '' END AS Bileterki,
			CASE WHEN CzyWlasna=0 THEN ' - firmy '+Firma+' %%     - import diagramów z kas obcych za okres od '+ @DateFrom +' do '+ @DateTo+'%%' 
			 ELSE '' END  AS FirmyForeign,
			 Firmy AS Firmy,
			 BileterkaWlasna,
			 BileterkaObca
			FROM
			(
				SELECT DISTINCT STUFF((SELECT DISTINCT ','+ x.Name
				FROM dbo.MAT_TicketRegisterType x WITH (NOLOCK)
				INNER JOIN dbo.SLS_FiscalReport f WITH (NOLOCK) ON LEFT(f.FiscalLogo,3) =x.Prefix
				INNER JOIN dbo.SLS_Ticket y WITH (NOLOCK)ON y.FiscalReport_ID = f.ID
				INNER JOIN dbo.SLS_TicketRoute rt WITH (NOLOCK) ON y.id = rt.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered xt WITH (NOLOCK) ON rt.RideRegistered_ID = xt.ID
				INNER JOIN #PomTicketsRoute zt WITH (NOLOCK) ON zt.TicketRouteId = rt.Id
				WHERE  /*y.Company_ID = t.Company_ID AND*/ y.Company_ID = @LicensedCompanyID

			  FOR XML PATH (''))
			  ,1,1,',') AS BileterkaWlasna,

			  STUFF((SELECT DISTINCT '%%'+ISNULL(CAST(c.INumber AS NVARCHAR),'') +' '+ c.ShortName
				FROM dbo.ADMIN_Company c WITH (NOLOCK)
				INNER JOIN #PomCompanyIds x WITH (NOLOCK) ON x.CompanyId = c.ID
			  FOR XML PATH (''))
			  ,1,1,'') AS Firmy,

				STUFF((SELECT DISTINCT ','+ x.Name
				FROM dbo.MAT_TicketRegisterType x WITH (NOLOCK)
				INNER JOIN dbo.SLS_FiscalReport f WITH (NOLOCK) ON LEFT(f.FiscalLogo,3) =x.Prefix
				INNER JOIN dbo.SLS_Ticket y WITH (NOLOCK) ON y.FiscalReport_ID = f.ID
				INNER JOIN dbo.SLS_TicketRoute rt WITH (NOLOCK) ON y.id = rt.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered xt WITH (NOLOCK) ON rt.RideRegistered_ID = xt.ID
				INNER JOIN #PomTicketsRoute zt WITH (NOLOCK) ON zt.TicketRouteId = rt.Id
				WHERE  /*y.Company_ID = t.Company_ID AND*/ y.Company_ID <> @LicensedCompanyID
			  FOR XML PATH (''))
			  ,1,1,',') AS BileterkaObca,

			 'Sprzedaż zarejestrowana w bileterkach przewoźnika nr '+ ISNULL(CAST(l.INumber AS NVARCHAR),'') +' '+ISNULL(l.Name,'')
				
					 +' %%Typy używanych bileterek: ' AS FirmaLicencjaBil,

		
			 'Sprzedaż zarejestrowana w bileterkach przewoźnika nr '+ ISNULL(CAST(o.INumber AS NVARCHAR),'') +' '+ISNULL(o.Name,'')
				
					 +' %%Typy używanych bileterek: ' AS FirmaBil,	

			  ISNULL(CAST(c.INumber AS NVARCHAR),'') +' '+ISNULL(c.Name,'') + ' na kwotę:'+ REPLACE(STR(f.ReductionValue,8,2), '.',',')+' zł' AS Firma,

			  CASE WHEN t.Company_ID = @LicensedCompanyID THEN 1 ELSE 0 END AS CzyWlasna
			  FROM dbo.SLS_Ticket t WITH (NOLOCK)
			  INNER JOIN Admin_Company c WITH (NOLOCK) ON c.id = t.Company_id
			  INNER JOIN dbo.SLS_TicketRoute r WITH (NOLOCK) ON t.id = r.Ticket_ID
			  INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
			  INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id AND NotTake=0
			  INNER JOIN
			  (
				SELECT SUM(ISNULL(r.ReductionValue*JST,0.0))/100.00 AS ReductionValue, t.Company_id
				FROM dbo.SLS_TICKET t WITH (NOLOCK)
				INNER JOIN Admin_Company c WITH (NOLOCK) ON c.id = t.Company_id
				INNER JOIN dbo.SLS_TicketRoute r WITH (NOLOCK) ON t.id = r.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
				INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id AND NotTake=0
				GROUP BY Company_id

			  ) f ON t.Company_Id = f.Company_Id
			  INNER JOIN dbo.ADMIN_Company o WITH (NOLOCK) ON o.id =@CompanyId
			  INNER JOIN dbo.ADMIN_Company l WITH (NOLOCK) ON l.id = @LicensedCompanyID

		) Pom
		) p
		
		
	SET @FirmyForeign = CASE WHEN @FirmyForeign<>'' THEN 'Uwzględnione dopłaty do biletów sprzedanych w kasach obcych %%' ELSE '' END + @FirmyForeign

	--select @BileterkaWlasna, @BileterkaObca, @LicensedCompanyID
	---------------------------------------------------------------
	------------NAPISY Z FIRMAMI I BILETERKAMI---------------------
	---------------------------------------------------------------


	SET @Guid = ISNULL(@Guid,'')

	IF @Guid <>'' AND NOT EXISTS(SELECT r.ID FROM dbo.ADMIN_ReportResult r WITH (NOLOCK) INNER JOIN dbo.ADMIN_ReportResultExportData e WITH (NOLOCK) ON r.id = e.ReportResult_ID AND e.Guid =@Guid)
	BEGIN
		SELECT @ReportResultID = MAX(Id)+1 FROM dbo.ADMIN_ReportResult WITH (NOLOCK) WHERE ReportType_ID =21		---typ dopłat
	
		SET @ReportResultID = ISNULL(@ReportResultID,1)
	END
	

	DECLARE @XMLParams NVARCHAR(MAX)
	SET @XMLParams=
	'<Params>'
	+CASE WHEN @WithReturnsMode=1 THEN '<Wydzielzwroty>1</Wydzielzwroty>' ELSE '<Wydzielzwroty>0</Wydzielzwroty>' END

	+CASE WHEN @CheckApperanceReturns=1 THEN '<Znaczzwroty>1</Znaczzwroty>' ELSE '<Znaczzwroty>0</Znaczzwroty>' END	

	+CASE WHEN @OrderBy=0 THEN '<PostaćUM>1</PostaćUM>' ELSE CASE WHEN @OrderBy=2 THEN '<PostaćUM>2</PostaćUM>' ELSE '<PostaćUM>3</PostaćUM>' END END
	
	+'<ParamZest>111111112221111211'+CAST(@LineTicketJoin+1 AS NVARCHAR)+'2</ParamZest>'			--11 pozycja netto w podsumowaniach liczone od brutto
	
	+'<SumyUM>'+CAST(CASE @OnlyPaymentsMode WHEN  0 THEN 1 ELSE 3 END AS NVARCHAR)+'</SumyUM>'
	
	+'<ZaokrUM>0</ZaokrUM>'									--brak obsługi z groszami

	+'<Dopłatybruttood>'+'zawsze'+'</Dopłatybruttood>'

	+'<Tylkobrutto>0</Tylkobrutto>'							--brak obsługi w zestawieniu dla UM pomiń kolumny „Netto” i „PTU”  -1, 0-nie pomijaj

	+'<Typzestawieniadlalini>2</Typzestawieniadlalini>'		--brak obsługi		1-zwykłe typ1 , 2 - typ2
	
	+'<PokLiczBil>1</PokLiczBil>'								--brak obsługi		
	
	+'<ZestawienieUMnalinie>'+CAST(ISNULL(@LineSeparateMonthAndSingleTickets,0) AS VARCHAR)+'</ZestawienieUMnalinie>'		-- oddzielenie jednorazowych i miesięcznych biletów

	+'<Wariantynazwylini>0</Wariantynazwylini>'				--brak obsługi		

	+'<PodsumowanieWPostaci3>'+ SUBSTRING(@AdditionalParams, PATINDEX('%,%',@AdditionalParams)+1, LEN(@AdditionalParams))+'</PodsumowanieWPostaci3>'
	
	+'<ZestawienieUMnalinietyp2>'+
	CAST(CASE WHEN @LineShowOfficeCode >0 THEN 2 ELSE 0 END +
	CASE WHEN @LineAddListOffices >0 THEN 4 ELSE 0 END +
	CASE WHEN @ShowLineTicketReliefByRelief >0 AND @LineSeparateMonthAndSingleTickets >0 THEN 8 ELSE 0 END +			
	CASE WHEN @LineSkipNumberInLine >0 THEN 32 ELSE 0 END +
	+128+ --parametr 128 - nazwę linii pobierz z tabeli "Linie" nie istnieje
	CASE WHEN @LineReplaceLineNumberEvidenceNumber >0 THEN 512 ELSE 0 END +
	CASE WHEN ISNUMERIC(SUBSTRING(@AdditionalParams, 1, PATINDEX('%,%',@AdditionalParams)-1))=1 THEN  CAST(SUBSTRING(@AdditionalParams, 1, PATINDEX('%,%',@AdditionalParams)-1) AS INT) ELSE 0 END
	AS NVARCHAR)
	+'</ZestawienieUMnalinietyp2>'	

	+'<PomSprawRodzKomMiesRel>'+CAST(@SkipCheckingRides AS NVARCHAR)+'</PomSprawRodzKomMiesRel>'

	+'<PomTylkoZłeMiesRel>'+ CASE WHEN @MonthTicketsSkipRelationsInvalidRides=1 THEN '1' ELSE '0'END +'</PomTylkoZłeMiesRel>'

	+'<PomRodzKom>111</PomRodzKom>'									--brak obsługi

	+'<PodsumowaniaKolejności>'+ SUBSTRING(@AdditionalParams, PATINDEX('%,%',@AdditionalParams)+1, LEN(@AdditionalParams))+'</PodsumowaniaKolejności>'			
	+'<RODO>'+CAST(ISNULL(@Rodo,0) AS NVARCHAR)+'</RODO>'

	+'<TerritorialDiv>'+CAST(@TerritorialDiv AS NVARCHAR)+'</TerritorialDiv>'		--JST do zestawień powiązanych z dopłatami
	+'<TerritoryIDs>'+@TerritoryIDs+'</TerritoryIDs>'
	+'<TerritorialDivType>'+CAST(@TerritorialDivType AS NVARCHAR)+'</TerritorialDivType>'
	+'</Params>'


	--------FORMATOWANIE NAGŁÓWKÓW LINII
	IF @OnlyPaymentsMode=2 -- sprzedaż
	BEGIN
		SET @Header = REPLACE(@Header, 'wartości sprzedaży', 'wartości dopłat')
		SET @Footer = REPLACE(@Footer, 'Wartość sprzedaży', 'Wartość dopłat do biletów ulgowych')
	END

	SET @Header = REPLACE(@Header, 'o uprawnieniach' ,CHAR(13)+CHAR(10)+'o uprawnieniach')
	SET @Header = REPLACE(@Header, 'poz. 1440 ze zm.)' ,'poz. 1440 ze zm.)'+CHAR(13)+CHAR(10))
		
	------------------------------

		
	IF @ReportResultID IS NULL
	 SELECT @ReportResultID = r.ID FROM dbo.ADMIN_ReportResult r WITH (NOLOCK) INNER JOIN dbo.ADMIN_ReportResultExportData e WITH (NOLOCK) ON r.id = e.ReportResult_ID AND e.Guid =@Guid

	INSERT INTO dbo.ADMIN_ReportResultExportData
	(ReportResult_ID, CompanyReceiver_ID, CompanySender_ID, DateFrom, DateTo, Header, Footer, XMLParams, Guid, File_ID)

	SELECT @ReportResultID, @CompanyId, @LicensedCompanyID, @DateFromF, @DateToF,
	
	ISNULL('Arial='+CHAR(13)+CHAR(10)+'9='+CHAR(13)+CHAR(10)+'01'+CHAR(13)+CHAR(10)+@Header,'') AS Header,
	
	CASE WHEN PATINDEX('%&&&%', @Footer)>0 THEN
	ISNULL(SUBSTRING(@Footer,1,PATINDEX('%&&&%', @Footer)-1),'')
	ELSE @Footer END
	 +CHAR(13)+CHAR(10)+ISNULL(@FirmyForeign,'')
	+CHAR(13)+CHAR(10)+ISNULL(REPLACE(@Bileterki,'%%',CHAR(13)+CHAR(10)),'')
	+CHAR(13)+CHAR(10)+ISNULL(@Statement,'')+
	+CHAR(13)+CHAR(10)+
	REPLACE(SUBSTRING(@Footer, PATINDEX('%&&&%',@Footer)+3, LEN(@Footer)),'&&&',CHAR(13)+CHAR(10))			--data wydruku
	
	AS Footer,
	
	@XMLParams AS XMLParams, @Guid, NULL 
	WHERE NOT EXISTS(SELECT ID FROM dbo.ADMIN_ReportResultExportData WITH (NOLOCK) WHERE ReportResult_ID = @ReportResultID)

	
	SET @ReportResultExportDataID = SCOPE_IDENTITY()

	--select @ReportResultExportDataID


	IF @ReportResultExportDataID IS NULL
	SELECT @ReportResultExportDataID = ID FROM dbo.ADMIN_ReportResultExportData WITH (NOLOCK) WHERE ReportResult_ID = @ReportResultID

	--select @ReportResultExportDataID


	IF ISNULL(@PerLineMode,0) =0
	BEGIN	
		
		SELECT ReductionName, ReliefTicketOrder, ReductionPercentage, 
		CAST(ReturnKind AS VARCHAR) AS ReturnKind, ReductionKind,
		SUM(ISNULL(ReductionValue, 0))/100. AS ReductionValue, 
		SUM(ISNULL(TicketCount, 0)) AS TicketCount, SUM(Brutto)/100. AS Brutto, SUM(Netto)/100. AS Netto, SUM(Ptu)/100. AS Ptu,
		ReturnsX AS ReturnsX,
		@FirmyOwn + ' '+@FirmyForeign AS Firmy, @Bileterki AS Bileterki,

		ABS(SUM(BruttoSum)) AS BruttoSum,
		
		ABS(SUM(PriceSum)) AS PriceSum,
		ABS(SUM(PricePTUSum)) AS PricePTUSum,

		ABS(SUM(ReturnsPriceSum)) AS ReturnsPriceSum,
		ABS(SUM(ReturnsPricePTU)) AS ReturnsPricePTU,
		
		ABS(SUM(PTUSum)) AS PTUSum,
		ABS(SUM(ReductionValuePTU))  AS ReductionValuePTU,
		ABS(SUM(ReturnsReductionValue))  AS ReturnsReductionValue,
		ABS(SUM(ReturnsReductionValuePtu))  AS ReturnsReductionValuePtu,
		ABS(SUM(ReturnsTicketCount))  AS ReturnsTicketCount,
		
		ABS(SUM(ReturnsBruttoSum)) AS ReturnsBruttoSum,
		ABS(SUM(ReturnsPTU)) AS ReturnsPTU,
		FarePriceReductionID,
		ReductionHistoryId,
		@CountingNettSum AS CountingNettSum,
		Period
		INTO #PomRelief
		FROM
		(
			SELECT 
			
			ISNULL(d.Name,'') AS ReductionName,
			ISNULL(d.ReductionKind,0) AS ReductionKind,
			SUM(ISNULL(ReturnX.PassangerNumber, t.PassangerNumber)) AS TicketCount,			
			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) END)  AS Brutto,  
			SUM([dbo].[SLS_GetVatValueM](CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) END,
			ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS PTU,

			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE ISNULL(ReturnX.ReductionValue,ISNULL(t.ReductionValue, 0)) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) END-[dbo].[SLS_GetVatValueM](CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE ISNULL(ReturnX.ReductionValue,ISNULL(t.ReductionValue, 0)) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) END, ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS Netto,
			SUM(ISNULL(ReturnX.ReductionValue,ISNULL(t.ReductionValue, 0))) AS ReductionValue,
			ISNULL(d.ReliefTicketOrder,0) AS ReliefTicketOrder,
			ISNULL(d.ReductionPercentage,0) AS ReductionPercentage,
			MAX(CASE WHEN t.PassangerNumber < 0 AND @CheckApperancereturns = 1 OR ISNULL(ReturnX.Returns, 0) >0 AND @CheckApperancereturns = 1 THEN 'Z' ELSE '' END) AS ReturnKind,
			
			ISNULL(ReturnX.Returns, 0) AS ReturnsX,

			SUM(ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) + ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) )  AS BruttoSum,  

			SUM(ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) )  AS PriceSum,  

			SUM([dbo].[SLS_GetVatValueM](ISNULL(ReturnX.Price, ISNULL(t.Price, 0)),
			ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS PricePTUSum,


			SUM(CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END * (ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) ))  AS ReturnsPriceSum,  	

			SUM([dbo].[SLS_GetVatValueM](CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END *(ISNULL(ReturnX.Price, ISNULL(t.Price, 0))),
			ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS ReturnsPricePtu,


			SUM([dbo].[SLS_GetVatValueM](ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) + ISNULL(ReturnX.Price, ISNULL(t.Price, 0)),
			ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS PTUSum,
			
			SUM([dbo].[SLS_GetVatValueM]((ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0))),
			(ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0))))) AS ReductionValuePTU,
			SUM(CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END*ISNULL(ReturnX.ReductionValue,ISNULL(t.ReductionValue, 0))) AS ReturnsReductionValue,
			SUM(CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END) AS ReturnsTicketCount,
			SUM(CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END * (ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) + ISNULL(ReturnX.Price, ISNULL(t.Price, 0)) ))  AS ReturnsBruttoSum,  	

			SUM([dbo].[SLS_GetVatValueM](CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END *(ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0)) +  ISNULL(ReturnX.Price, ISNULL(t.Price, 0))),
			ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0)))) AS ReturnsPtu,

			SUM([dbo].[SLS_GetVatValueM](CASE WHEN t.PassangerNumber<0 THEN 1 ELSE 0 END * ABS(ISNULL(ReturnX.ReductionValue, ISNULL(t.ReductionValue, 0))),
			ABS(ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0))))) AS ReturnsReductionValuePtu,
			d.FarePriceReductionID,
			d.ReductionHistoryId,
			ISNULL(t.Period,'') AS Period
			FROM
			(
				SELECT d.Id AS FarePriceReductionId, d.Name, d.ReliefTicketOrder, ReductionPercentage, ReductionHistoryId,
				CASE WHEN d.FarePriceReductionGroup_ID IN (1, 2, 12) THEN 0 ELSE 1 END AS ReductionKind
				FROM dbo.TCK_FarePriceReduction d WITH (NOLOCK)
				INNER JOIN (SELECT DISTINCT ReductionId, ReductionPercentage, ReductionHistoryId FROM #PomRedIds) r
				ON r.ReductionId=d.Id
			) AS d
			LEFT JOIN (
				SELECT t.Id, t.FarePriceReduction_ID,
				ISNULL(SIGN(t.PassangerNumber),0) AS PassangerNumber, SUM(ISNULL(r.ReductionValue*ptr.JST,0)) AS ReductionValue, SUM(ISNULL(r.Price*ptr.JST,0)) AS Price, MAX(ISNULL(r.VatAmount,0)) AS VatAmount, ptr.Period 
				FROM dbo.SLS_Ticket t WITH (NOLOCK)
				INNER JOIN dbo.SLS_TicketRoute r WITH (NOLOCK) ON t.id = r.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
				INNER JOIN #PomTicketsRoute ptr WITH (NOLOCK) ON ptr.TicketRouteId = r.Id
				GROUP BY t.Id, t.FarePriceReduction_ID, t.ReductionPercentage, t.PassangerNumber, ptr.Period
			) AS t ON d.FarePriceReductionID = t.FarePriceReduction_ID

			-- zwroty oddzielne linie
			LEFT JOIN (
				-- dodatnie
				SELECT 1 AS Returns,
				t.id,
				t.FarePriceReduction_ID, t.ReductionPercentage, 
				ISNULL(SIGN(t.PassangerNumber),0) AS PassangerNumber, ISNULL(r.ReductionValue,0) AS ReductionValue, ISNULL(r.Price,0) AS Price, ISNULL(r.VatAmount,0) AS VatAmount
				FROM dbo.SLS_Ticket t WITH (NOLOCK)
				INNER JOIN 
				(	SELECT r.Ticket_ID, SUM(r.ReductionValue*rr.JST) AS ReductionValue, SUM(r.Price*rr.JST) AS Price, MAX(r.VatAmount) AS VatAmount 
					FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
					INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
					INNER JOIN #PomTicketsRoute rr WITH (NOLOCK) ON rr.TicketRouteId = r.Id
					INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id = r.Ticket_ID AND rr.PassangerNumber =1 -->0
					GROUP BY r.Ticket_ID
				) R on R.Ticket_ID = T.ID
				WHERE t.PassangerNumber >0 
						AND EXISTS( SELECT t1.id FROM dbo.SLS_Ticket t1 WITH (NOLOCK)
						INNER JOIN dbo.SLS_TicketRoute r1 WITH (NOLOCK) ON t1.id = r1.Ticket_ID
						INNER JOIN dbo.SLS_RideRegistered x1 WITH (NOLOCK) ON r1.RideRegistered_ID = x1.ID
						INNER JOIN #PomTicketsRoute tr1 WITH (NOLOCK) ON tr1.TicketRouteId = r1.Id
						WHERE t.FarePriceReduction_ID = t1.FarePriceReduction_ID AND tr1.PassangerNumber =0 --<0
						)
				
				UNION ALL

				SELECT DISTINCT 1 AS Returns,
				t.id,
				t.FarePriceReduction_ID, t.ReductionPercentage,
				0 AS PassangerNumber, 0.0 AS ReductionValue, 0.0 AS Price, 0.0 AS VatAmount
				FROM dbo.SLS_Ticket t WITH (NOLOCK)
				INNER JOIN dbo.SLS_TicketRoute r WITH (NOLOCK) ON t.id = r.Ticket_ID
				INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
				INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id
				WHERE t.PassangerNumber <0 
						AND NOT EXISTS( SELECT t1.id FROM dbo.SLS_Ticket t1 WITH (NOLOCK)
						INNER JOIN dbo.SLS_TicketRoute r1 WITH (NOLOCK) ON t1.id = r1.Ticket_ID
						INNER JOIN dbo.SLS_RideRegistered x1 WITH (NOLOCK) ON r1.RideRegistered_ID = x1.ID
						INNER JOIN #PomTicketsRoute tr1 WITH (NOLOCK) ON tr1.TicketRouteId = r1.Id
						WHERE t.FarePriceReduction_ID = t1.FarePriceReduction_ID AND tr1.PassangerNumber =1 -->0
						)

				UNION ALL
				-- ujemne
				SELECT 2 AS Returns,
				t.id,
				 t.FarePriceReduction_ID, t.ReductionPercentage, 
				ISNULL(SIGN(t.PassangerNumber),0) AS PassangerNumber, ISNULL(r.ReductionValue,0) AS ReductionValue, ISNULL(r.Price,0) AS Price, ISNULL(r.VatAmount,0) AS VatAmount
				FROM dbo.SLS_Ticket t WITH (NOLOCK)

				INNER JOIN 
				(	SELECT r.Ticket_ID, SUM(r.ReductionValue*rr.JST) AS ReductionValue, SUM(r.Price*rr.JST) AS Price, MAX(r.VatAmount) AS VatAmount 
					FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
					INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
					INNER JOIN #PomTicketsRoute rr WITH (NOLOCK) ON rr.TicketRouteId = r.Id
					INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id = r.Ticket_ID AND rr.PassangerNumber =0  --<0
					GROUP BY r.Ticket_ID
				) R on R.Ticket_ID = T.ID
				WHERE t.PassangerNumber <0 -- mniejsze od zera 

				UNION ALL
				-- łącznie
				SELECT 3 AS Returns,
				t.id,
				 t.FarePriceReduction_ID, t.ReductionPercentage,
				ISNULL(SIGN(t.PassangerNumber),0) AS PassangerNumber, ISNULL(r.ReductionValue,0) AS ReductionValue, ISNULL(r.Price,0) AS Price, ISNULL(r.VatAmount,0) AS VatAmount
				FROM dbo.SLS_Ticket t WITH (NOLOCK)
				INNER JOIN 
				(	SELECT r.Ticket_ID, SUM(r.ReductionValue*rr.JST) AS ReductionValue, SUM(r.Price*rr.JST) AS Price, MAX(r.VatAmount) AS VatAmount 
					FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
					INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
					INNER JOIN #PomTicketsRoute rr WITH (NOLOCK) ON rr.TicketRouteId = r.Id
					INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id = r.Ticket_ID
					GROUP BY r.Ticket_ID
				) R on R.Ticket_ID = T.ID
	
				WHERE 
				EXISTS( SELECT t1.id FROM dbo.SLS_Ticket t1 WITH (NOLOCK)
							INNER JOIN dbo.SLS_TicketRoute r1 WITH (NOLOCK) ON t1.id = r1.Ticket_ID
							INNER JOIN dbo.SLS_RideRegistered x1 WITH (NOLOCK) ON r1.RideRegistered_ID = x1.ID
							INNER JOIN #PomTicketsRoute tr1 WITH (NOLOCK) ON tr1.TicketRouteId = r1.Id AND tr1.PassangerNumber =0 --<0
							WHERE t.FarePriceReduction_ID = t1.FarePriceReduction_ID AND t1.ReductionPercentage = t.ReductionPercentage
							)

			) AS ReturnX ON
			ReturnX.id = t.id AND d.FarePriceReductionId = ReturnX.FarePriceReduction_ID AND ReturnX.FarePriceReduction_ID = t.FarePriceReduction_ID AND @WithReturnsMode= 1 

			--WHERE 1=0 --kupa
			GROUP BY
			ISNULL(d.Name,'')
			, d.ReductionHistoryId
			, d.FarePriceReductionId
			, ISNULL(ReturnX.VatAmount, ISNULL(t.VatAmount, 0))
			, ISNULL(d.ReductionPercentage,0)
			, ISNULL(d.ReliefTicketOrder,0)
			, ISNULL(d.ReductionKind,0)
			, ISNULL(ReturnX.Returns, 0)
			, ISNULL(t.Period,'')
		
		) Pom
		GROUP BY
		ReturnKind, ReductionKind,
		ReductionName,
		ReductionHistoryId,
		FarePriceReductionId,
		ReliefTicketOrder,
		ReductionPercentage,
		ReturnsX,
		Period 
	ORDER BY 
	ReductionKind,

	CASE @OrderBy WHEN 0 THEN ReductionPercentage ELSE 0 END DESC ,
	CASE @OrderBy WHEN 1 THEN ReliefTicketOrder ELSE 0 END ASC,

	ReductionName ASC,
	ReturnsX ASC

	
	--SPECIALNE WYLICZANIE Liczby biletów w trybi dla Linii
	UPDATE #PomRelief
	SET TicketCount=0
	WHERE @SpecialCountLineTickets=1 AND @LineTicketJoin=0

	UPDATE #PomRelief
	SET TicketCount = A1Rate.PassangerNumber
	FROM
	(
		SELECT FarePriceReduction_ID, SUM((PassangerNumber)) AS PassangerNumber
		FROM
		(
			SELECT t.id, t.FarePriceReduction_ID, (SIGN(t.PassangerNumber)) AS PassangerNumber, r.Line_ID, 
			ROW_NUMBER() OVER ( PARTITION BY t.id ORDER BY tr.RouteNumber, tr.RelationNumber ) as LP
			FROM sls_ticket t
			INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.Ticket_ID = t.id
			INNER JOIN #TicketRoutePom rr WITH (NOLOCK) ON rr.TicketRouteIDPom = tr.Id
			inner join SLS_RideRegistered x on x.id = tr.RideRegistered_ID
			inner join TT_Ride r ON r.id = x.Ride_ID 
		) x
		INNER JOIN @ForLines l ON l.id = x.Line_ID
		and lp=1
		GROUP BY FarePriceReduction_ID
		) A1Rate 
		WHERE
		A1Rate.FarePricereduction_id = #PomRelief.FarePriceReductionId AND  @SpecialCountLineTickets=1 AND @LineTicketJoin=0
	

	IF @CountNettValuePerEachMonth =1
	BEGIN
		
		UPDATE #PomRelief
		SET PricePTUSum =ROUND(PricePTUSum,2),
			PTUSum =ROUND(PTUSum,2),
			ReductionValuePTU = ROUND(ReductionValuePTU,2),
			Netto = ROUND(Netto,2),
			PTU = ROUND(PTU,2)
			
		
		INSERT INTO #PomRelief (ReductionName, ReliefTicketOrder, ReductionPercentage, 
		ReturnKind, ReductionKind, ReductionValue, TicketCount, Brutto, Netto, Ptu,
		ReturnsX, Firmy, Bileterki, BruttoSum, PriceSum, PricePTUSum, ReturnsPriceSum, ReturnsPricePTU, 
		PTUSum, ReductionValuePTU, ReturnsReductionValue, ReturnsReductionValuePtu, ReturnsTicketCount,
		ReturnsBruttoSum, ReturnsPTU, FarePriceReductionID, ReductionHistoryId, CountingNettSum, Period)
		
		SELECT
		 ReductionName, ReliefTicketOrder, ReductionPercentage, 
		ReturnKind, ReductionKind,
		SUM(ISNULL(ReductionValue, 0)) AS ReductionValue, 
		SUM(ISNULL(TicketCount, 0)) AS TicketCount, SUM(Brutto) AS Brutto, SUM(Netto) AS Netto, SUM(Ptu) AS Ptu,
		ReturnsX AS ReturnsX,
		Firmy, Bileterki,

		ABS(SUM(BruttoSum)) AS BruttoSum,
		
		ABS(SUM(PriceSum)) AS PriceSum,
		ABS(SUM(PricePTUSum)) AS PricePTUSum,

		ABS(SUM(ReturnsPriceSum)) AS ReturnsPriceSum,
		ABS(SUM(ReturnsPricePTU)) AS ReturnsPricePTU,
		
		ABS(SUM(PTUSum)) AS PTUSum,
		ABS(SUM(ReductionValuePTU))  AS ReductionValuePTU,
		ABS(SUM(ReturnsReductionValue))  AS ReturnsReductionValue,
		ABS(SUM(ReturnsReductionValuePtu))  AS ReturnsReductionValuePtu,
		ABS(SUM(ReturnsTicketCount))  AS ReturnsTicketCount,
		
		ABS(SUM(ReturnsBruttoSum)) AS ReturnsBruttoSum,
		ABS(SUM(ReturnsPTU)) AS ReturnsPTU,
		FarePriceReductionID,
		ReductionHistoryId,
		CountingNettSum,
		''
		FROM #PomRelief
		WHERE Period<>''
		GROUP BY
		ReductionName, ReliefTicketOrder, ReductionPercentage, 
		ReturnKind, ReductionKind, ReturnsX, Firmy, Bileterki, FarePriceReductionID,
		ReductionHistoryId, CountingNettSum

		DELETE FROM #PomRelief WHERE Period<>''
	END

	--xxxx
	--select * from #PomRelief
		---------------------------------------------------------------
		----------------------UZUPEŁNIENIE DANYCH----------------------
		---------------------------------------------------------------

		INSERT INTO dbo.ADMIN_ReportResultXTicketRoute (ReportResultExportData_ID, TicketRoute_ID)
		SELECT @ReportResultExportDataID, x.TicketRouteId
		FROM #PomTicketsRoute x
		LEFT JOIN
		(	SELECT Id FROM dbo.ADMIN_ReportResultXTicketRoute r WITH (NOLOCK) 
			WHERE r.ReportResultExportData_ID = @ReportResultExportDataID
		) r ON 1=1
		WHERE r.id IS NULL
			
		
		INSERT INTO dbo.ADMIN_ReportResultXFarePriceReductionSum (ReportResultExportData_ID, FarePriceReduction_ID, FarePriceReductionHistory_ID, TicketCount, PriceSum, VATAmountSum, DoplatySum,
							DoplatyVATAmountSum, DoplatyNettoSum, IncludesReturns, ReturnsTicketCount, ReturnsPriceSum, ReturnsVATAmountSum, ReturnsDoplatySum, ReturnsDoplatyVATAmountSum, ReturnsDoplatyNettoSum)	
	
		SELECT @ReportResultExportDataID, FarePriceReduction_ID, FarePriceReductionHistory_ID, TicketCount, PriceSum, VATAmountSum, DoplatySum,
				DoplatyVATAmountSum, DoplatyNettoSum, IncludesReturns,
				ReturnsTicketCount, ReturnsPriceSum, 
				ReturnsVATAmountSum, ReturnsDoplatySum, ReturnsDoplatyVATAmountSum, ReturnsDoplatyNettoSum
		
		FROM
		(SELECT FarePriceReductionID AS FarePriceReduction_ID, ReductionHistoryID AS FarePriceReductionHistory_ID, TicketCount, PriceSum AS PriceSum, PricePTUSum AS VATAmountSum, ReductionValue*100 AS DoplatySum,
				ReductionValuePtu AS DoplatyVATAmountSum, ReductionValue*100-ReductionValuePtu AS DoplatyNettoSum, CASE WHEN ReturnsTicketCount <>0 THEN 1 ELSE 0 END AS IncludesReturns,
				ReturnsTicketCount AS ReturnsTicketCount, ReturnsPriceSum AS ReturnsPriceSum,
				ReturnsPricePTU AS ReturnsVATAmountSum, ReturnsReductionValue AS ReturnsDoplatySum,
				ReturnsReductionValuePTU AS ReturnsDoplatyVATAmountSum, ReturnsReductionValue - ReturnsReductionValuePtu AS ReturnsDoplatyNettoSum
		
		FROM #PomRelief
		WHERE ReturnsX=0 OR (/*ReductionKind= 1 AND*/ ReturnsX = 3)
		) Pom
		WHERE NOT EXISTS(SELECT ID FROM dbo.ADMIN_ReportResultXFarePriceReductionSum WITH (NOLOCK) WHERE ReportResultExportData_ID = @ReportResultExportDataID)
	 

	--select * from #PomRelief
		---------------------------------------------------------------
		--------------------REZULTAT KOŃCOWY---------------------------
		---------------------------------------------------------------
		--SET NOCOUNT ON;

		SELECT *
		FROM
		(
		SELECT *, 
			100*CASE WHEN sm.Summ = 0.0 THEN 0.0 ELSE
				CASE WHEN @OnlyPaymentsMode=0 THEN ISNULL(ReductionValue*100,0.0) ELSE ISNULL(Brutto,0.0) END /sm.Summ
			END
			AS Part,
			0 AS ORD
			
		FROM #PomRelief
		INNER JOIN
	 (	SELECT 
		SUM(CASE WHEN @OnlyPaymentsMode=0 THEN ISNULL(ReductionValue*100,0.0) ELSE ISNULL(Brutto,0.0) END) AS Summ
		FROM #PomRelief WHERE ReturnsX IN (0,3) 
	 ) sm	
	  ON 1=1

	UNION ALL

	SELECT CASE WHEN ReductionKind=0 THEN 'Razem jednorazowe' ELSE 'Razem miesięczne' END AS ReductionName,	
	0 AS ReliefTicketOrder,	ReductionPercentage, '' AS ReturnKind, ReductionKind, SUM(ReductionValue) AS ReductionValue, 
	SUM(TicketCount) AS TicketCount, SUM(Brutto) AS Brutto,	SUM(Netto) AS Netto, SUM(Ptu) AS Ptu, 0 AS ReturnsX, '' AS Firmy, '' AS	Bileterki,
	SUM(BruttoSum) AS BruttoSum, SUM(PriceSum) AS PriceSum, SUM(PricePTUSum) AS	PricePTUSum, SUM(ReturnsPriceSum) AS ReturnsPriceSum, SUM(ReturnsPricePTU) AS ReturnsPricePTU,
	SUM(PTUSum) AS PTUSum, SUM(ReductionValuePTU) AS ReductionValuePTU, SUM(ReturnsReductionValue) AS ReturnsReductionValue, SUM(ReturnsReductionValuePtu) AS ReturnsReductionValuePtu,
	SUM(ReturnsTicketCount) AS ReturnsTicketCount, SUM(ReturnsBruttoSum) AS	ReturnsBruttoSum, SUM(ReturnsPTU) AS ReturnsPTU, 0 AS FarePriceReductionID, 0 AS ReductionHistoryId, 
	SUM(CountingNettSum) AS CountingNettSum,'' AS Period, 0 AS Summ, 0 AS Part, 1 AS Ord
	FROM #PomRelief
	WHERE @OrderBy=2 --wg grupy ulg
	GROUP BY ReductionPercentage, ReductionKind 

	UNION ALL

	SELECT CASE WHEN ReductionKind=0 THEN 'Razem samorząd jednorazowe' ELSE 'Razem samorząd miesięczne' END AS ReductionName,	
	0 AS ReliefTicketOrder,	NULL AS ReductionPercentage, '' AS ReturnKind, ReductionKind, SUM(ReductionValue) AS ReductionValue, 
	SUM(TicketCount) AS TicketCount, SUM(Brutto) AS Brutto,	SUM(Netto) AS Netto, SUM(Ptu) AS Ptu, 0 AS ReturnsX, '' AS Firmy, '' AS	Bileterki,
	SUM(BruttoSum) AS BruttoSum, SUM(PriceSum) AS PriceSum, SUM(PricePTUSum) AS	PricePTUSum, SUM(ReturnsPriceSum) AS ReturnsPriceSum, SUM(ReturnsPricePTU) AS ReturnsPricePTU,
	SUM(PTUSum) AS PTUSum, SUM(ReductionValuePTU) AS ReductionValuePTU, SUM(ReturnsReductionValue) AS ReturnsReductionValue, SUM(ReturnsReductionValuePtu) AS ReturnsReductionValuePtu,
	SUM(ReturnsTicketCount) AS ReturnsTicketCount, SUM(ReturnsBruttoSum) AS	ReturnsBruttoSum, SUM(ReturnsPTU) AS ReturnsPTU, 0 AS FarePriceReductionID, 0 AS ReductionHistoryId, 
	SUM(CountingNettSum) AS CountingNettSum,'' AS Period, 0 AS Summ, 0 AS Part, 2 AS Ord
	FROM #PomRelief r
	INNER JOIN TCK_FarePriceReductionLegalPref p on p.farePriceReduction_id = r.FarePriceReductionID
	WHERE p.GovOffice LIKE '%samorząd%' AND @OrderBy=2 --wg grupy ulg
	GROUP BY ReductionKind
	) pom
	ORDER BY 
	ReductionKind,
	CASE @OrderBy WHEN 0 THEN ReductionPercentage ELSE 0 END DESC,
	CASE @OrderBy WHEN 1 THEN ReliefTicketOrder ELSE 0 END ASC,
	CASE @OrderBy WHEN 2 THEN ORD ELSE 0 END ASC,
	ReductionName ASC,
	ReturnsX ASC
	 


	--SELECT * FROM #PomRelief

---------------------------------------------------------------------------------
---------------------------------------------------------------------------------
---------------------CZĘŚĆ DLA LINII --------------------------------------------



		DECLARE @OfficeList NVARCHAR(MAX)='Wykaz urzędów wydających zezwolenia:'
		IF ISNULL(@LineAddListOffices,0)=1
		BEGIN
		

			SELECT  @OfficeList =@OfficeList +'%%'+ ISNULL(o.Office,'')
						FROM dbo.TT_LinePermission p WITH (NOLOCK) 
						INNER JOIN
						(
							SELECT c.id AS CompanyGov_ID, CASE c.CompanyType_ID WHEN 5 THEN 'W' WHEN 6 THEN 'P' WHEN 7 THEN 'G' WHEN 8 THEN 'R' WHEN 9 THEN 'M' ELSE 'D' END + com.SYMBOL +' '+c.Name AS Office
							FROM dbo.ADMIN_Company c WITH (NOLOCK) 
							INNER JOIN dbo.ADMIN_CompanyAddress a WITH (NOLOCK) ON c.ID = a.Company_ID AND a.CompanyAddressType_ID=1 --tylko główny
							INNER JOIN dbo.TT_Place pl WITH (NOLOCK) ON a.Place_ID = pl.ID
							INNER JOIN dbo.TT_Community com WITH (NOLOCK) ON pl.COMMUNITY_ID = com.ID
						) o ON o.CompanyGov_Id = p.CompanyGov_Id
						INNER JOIN dbo.TT_Line l WITH (NOLOCK) ON l.id = p.Line_ID
						INNER JOIN 
						(
							SELECT DISTINCT rr.Line_ID
							FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
							INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
							INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id
							INNER JOIN dbo.TT_Ride rr WITH (NOLOCK) ON x.Ride_ID = rr.ID-- rr.RideNumber = x.RideNumber AND ISNULL(rr.ValidFrom,'1900-01-01') = ISNULL(x.RideValidFrom,'1900-01-01') AND rr.RideVariant= x.RideVariant 
							INNER JOIN dbo.Admin_Company c WITH (NOLOCK) ON c.INumber = x.INumber
						) X ON l.Id= x.Line_Id


		END 
		ELSE
			SET @OfficeList=''



	if object_id('tempdb..#PomReliefLine') is not null
		drop table #PomReliefLine

	if object_id('tempdb..#PomReliefxxx') is not null
		drop table #PomReliefxxx

		SELECT t.id AS Ticket_ID, tr.id AS RRID, LineNumber
		INTO #PomReliefxxx
		FROM dbo.SLS_Ticket t WITH (NOLOCK)
		INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON t.id = tr.Ticket_ID
		INNER JOIN #PomTicketsRoute rt WITH (NOLOCK) ON rt.TicketRouteId = tr.Id
		INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON tr.RideRegistered_ID = x.ID
		INNER JOIN (SELECT DISTINCT ReductionId FROM #PomRedIds) pr ON pr.ReductionId=t.FarePriceReduction_ID
		WHERE t.FarePriceReductionGroup_ID=3


		SELECT Lp, LineName,
		
		ROUND(CASE WHEN @ShowLineTicketReliefByRelief =0  THEN ISNULL(TicketCount,0.0) ELSE TicketCount END,2) 
		
		AS TicketCount,
		ROUND(CASE WHEN @ShowLineTicketReliefByRelief =0  THEN ISNULL(TicketCountMonth,0.0) ELSE TicketCountMonth END,2) AS TicketCountMonth,

		Brutto, BruttoMonth,
		Netto, NettoMonth,
		ReductionValue, 
		LineValidFrom, 
		ReductionMonth,
		Reduction,
		Firmy, Bileterki, OfficeList, PermissionNr, ReductionMonthOrd, ReductionOrd,

		--DANE DO ZASILENIA

		Line_id,
		LineNumber,
		LineNumberPom,
		LineNamePom,
		LineShortName,
		LineVariant,
		LineType_ID,
		MonthTicketCountA1,
		MonthTicketCountA2,
		MonthTicketCountA3,
		ReturnsTicketCount,
		PTUMonthData,
		PTUData,
		
		ReturnsTicketCountMonth,
		ReturnsPriceSumData,
		ReturnsPTUData,

		ReturnsReductionValueData,
		ReturnsReductionValuePTUData,

		ReturnsMonthTicketCountA1,
		ReturnsMonthTicketCountA2,
		ReturnsMonthTicketCountA3,

		ReturnsPriceSumMonthData,
		ReturnsPTUMonthData,
		ReturnsReductionValueMonthData, 
		ReturnsReductionValuePTUMonthData,
		ReductionValueMonthData,
		ReductionValuePTUMonthData,
		PriceMonthData, 
		
		ReductionValuePTUData,
		ReductionValueData,			
		PriceSumData,
		PriceSumPTUData,
		ReturnsTicketCountSingle AS ReturnsTicketCountSingle,
		TicketCountSingle AS TicketCountSingle,
		@CountingNettSum AS CountingNettSum,
		ReturnKind
		INTO #PomReliefLine
		FROM
		(
		SELECT 
			DENSE_RANK() OVER (ORDER BY MAX(LineNumber) ASC, MAX(LTRIM(RTRIM(LineName))) ASC)  AS LP,
			LTRIM(RTRIM(LineName)) AS LineName,
			MAX(LineNamePom) AS LineNamePom,
			MAX(LineNumber) AS LineNumber,
			MAX(LineNumberPom) AS LineNumberPom,
			MAX(LineFirstBusStopShortName+'-'+LineLastBusStopShortName) AS LineShortName,
			Line_ID,
			LineVariant AS LineVariant,
			MAX(LineType_ID) AS LineType_ID,
			CASE WHEN CONVERT(DECIMAL(8,2),ISNULL(SUM(TicketCount),0.00))=0.00 THEN NULL ELSE SUM(TicketCount) END AS TicketCount,
			SUM(Brutto)/100. AS Brutto, 
			SUM(
			case when @LineSeparateMonthAndSingleTickets=1 then isnull(ReductionValueData,0)-isnull(ReductionValuePTUData,0)
			else
				case when @OnlyPaymentsMode=0 then isnull(ReductionValueMonthData,0)-isnull(ReductionValuePTUMonthData,0)+ isnull(ReductionValueData,0)-isnull(ReductionValuePTUData,0)
				else
				case when @OnlyPaymentsMode=2 then isnull(PriceSumData,0)-isnull(PriceSumPTUData,0) +isnull(PriceMonthData,0)-isnull(PTUMonthData,0)
				else
					isnull(ReductionValueMonthData,0)-isnull(ReductionValuePTUMonthData,0)+ isnull(ReductionValueData,0)-isnull(ReductionValuePTUData,0)+isnull(PriceSumData,0)-isnull(PriceSumPTUData,0) +isnull(PriceMonthData,0)-isnull(PTUMonthData,0)
				end
				end
			end
			)/100. AS Netto, 
			CASE WHEN CONVERT(DECIMAL(8,2),ISNULL(SUM(TicketCountMonth),0.00))=0.00 THEN NULL ELSE SUM(TicketCountMonth) END AS TicketCountMonth,
			
			
				SUM(
			case when @LineSeparateMonthAndSingleTickets=1 then isnull(ReductionValueMonthData,0)-isnull(ReductionValuePTUMonthData,0)
			else
				case when @OnlyPaymentsMode=0 then isnull(ReductionValueMonthData,0)-isnull(ReductionValuePTUMonthData,0)
				else
				case when @OnlyPaymentsMode=2 then isnull(PriceMonthData,0)-isnull(PTUMonthData,0)
				else
					isnull(ReductionValueMonthData,0)-isnull(ReductionValuePTUMonthData,0)+ isnull(PriceMonthData,0)-isnull(PTUMonthData,0)
				end
				end
			end
			)/100. AS NettoMonth, 
			SUM(BruttoMonth)/100.00 AS BruttoMonth,
			SUM(ReductionValue)/100. AS ReductionValue,
			CAST(LineValidFrom AS DATE) AS LineValidFrom,
			ReductionMonth,
			Reduction,
			@FirmyOwn +  ' '+@FirmyForeign AS Firmy, @Bileterki AS Bileterki,
			@OfficeList AS OfficeList,
			MAX(PermissionNr) AS PermissionNr,
			MAX(ReductionMonthOrd) AS ReductionMonthOrd,
			MAX(ReductionOrd) AS ReductionOrd,

			--DANE DO ZASILENIA

			SUM(MonthTicketCountA1) AS MonthTicketCountA1,
			SUM(MonthTicketCountA2) AS MonthTicketCountA2,
			SUM(MonthTicketCountA3) AS MonthTicketCountA3,
			SUM(ReturnsTicketCount) AS ReturnsTicketCount,
			ABS(SUM(PTUMonthData)) AS PTUMonthData,
			ABS(SUM(PTUData)) AS PTUData,
			SUM(ReturnsTicketCountMonth) AS ReturnsTicketCountMonth,
			ABS(SUM(ReturnsPriceSumData)) AS ReturnsPriceSumData,
			ABS(SUM(ReturnsPTUData)) AS ReturnsPTUData,
			ABS(SUM(ReturnsMonthTicketCountA1)) AS ReturnsMonthTicketCountA1,
			ABS(SUM(ReturnsMonthTicketCountA2)) AS ReturnsMonthTicketCountA2,
			ABS(SUM(ReturnsMonthTicketCountA3)) AS ReturnsMonthTicketCountA3,
			ABS(SUM(ReturnsPriceSumMonthData)) AS ReturnsPriceSumMonthData,
			ABS(SUM(ReturnsPTUMonthData)) AS ReturnsPTUMonthData,
			ABS(SUM(ReturnsReductionValueMonthData)) AS ReturnsReductionValueMonthData, 
			ABS(SUM(ReturnsReductionValuePTUMonthData)) AS ReturnsReductionValuePTUMonthData,
			SUM(ReductionValueMonthData) AS ReductionValueMonthData,
			SUM(ReductionValuePTUMonthdata) AS ReductionValuePTUMonthData,
			SUM(PriceMonthData) AS PriceMonthData, 
			ABS(SUM(ReturnsReductionValuePTUData)) AS ReturnsReductionValuePTUData,
			ABS(SUM(ReturnsReductionValueData)) AS ReturnsReductionValueData, 
			ABS(SUM(ReductionValuePTUData)) AS ReductionValuePTUData,				
			ABS(SUM(PriceSumData)) AS PriceSumData,				
			ABS(SUM(ReductionValueData)) AS ReductionValueData,
			ABS(SUM(PriceSumPTUData)) AS PriceSumPTUData,

			ABS(SUM(ReturnsTicketCountSingle)) AS ReturnsTicketCountSingle,
			ABS(SUM(TicketCountSingle)) AS TicketCountSingle,

			MAX(CASE WHEN (ReturnsTicketCountMonth > 0 OR ReturnsTicketCount>0) AND @CheckApperancereturns = 1 /*OR ISNULL(ReturnX.Returns, 0) >0 AND @CheckApperancereturns = 1*/ THEN 'Z' ELSE '' END) AS ReturnKind				
		FROM
		(
			SELECT 
			t.LineValidFrom AS LineValidFrom, 
			SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 12) THEN 1 ELSE 0 END ELSE 1 END * t.PassangerNumber) AS TicketCount,
			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 12) THEN 1 ELSE 0 END ELSE 1 END * t.ReductionValue END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END-[dbo].[SLS_GetVatValueM](CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE  CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 12) THEN 1 ELSE 0 END ELSE 1 END *ISNULL(t.ReductionValue, 0) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END, ISNULL(t.VatAmount, 0))) AS Netto,
			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 12) THEN 1 ELSE 0 END ELSE 1 END * t.ReductionValue END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END)  AS Brutto,
			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * t.ReductionValue END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END-[dbo].[SLS_GetVatValueM](CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * ISNULL(t.ReductionValue, 0) END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END, ISNULL(t.VatAmount, 0))) AS NettoMonth,
			SUM(CASE WHEN @OnlyPaymentsMode = 2 THEN 0 ELSE CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END *t.ReductionValue END + CASE WHEN @OnlyPaymentsMode = 0 THEN 0 ELSE ISNULL(t.Price, 0) END)  AS BruttoMonth,
			SUM(t.ReductionValue) AS ReductionValue,
			SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * t.PassangerNumber) AS TicketCountMonth,
			ISNULL(t.LineNumber, 0) AS LineNumber,
			MAX(ISNULL(t.LineNumberPom, 0)) AS LineNumberPom,
			MAX(LineNamePom) AS LineNamePom,
			MAX(LineFirstBusStopShortName) AS LineFirstBusStopShortName,
			MAX(LineLastBusStopShortName) AS LineLastBusStopShortName,
			LineName,
			Line_id,
			LineVariant AS LineVariant,

			MAX(LineType_ID) AS LineType_ID,
			ReductionMonth,
			Reduction,
			MAX(ReductionMonthOrd) AS ReductionMonthOrd,
			MAX(ReductionOrd) AS ReductionOrd,
			MAX(PermissionNr) AS PermissionNr,

			--DANE DO ZASILENIA

			SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * MonthTicketCountA1) AS MonthTicketCountA1,
			SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * MonthTicketCountA2) AS MonthTicketCountA2,
			SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END ELSE 1 END * MonthTicketCountA3) AS MonthTicketCountA3,

			SUM(ReturnsTicketCount) AS ReturnsTicketCount,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *PTUMonthData) AS PTUMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*PTUData) AS PTUData,

			SUM(ReturnsTicketCountMonth) AS ReturnsTicketCountMonth,

			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*ReturnsReductionValueData) AS ReturnsReductionValueData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*ReturnsPriceSumData) AS ReturnsPriceSumData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*ReturnsPTUData) AS ReturnsPTUData,

			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END * ReturnsMonthTicketCountA1) AS ReturnsMonthTicketCountA1,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END * ReturnsMonthTicketCountA2) AS ReturnsMonthTicketCountA2,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END * ReturnsMonthTicketCountA3) AS ReturnsMonthTicketCountA3,

			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReturnsPriceSumMonthData) AS ReturnsPriceSumMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReturnsPTUMonthData) AS ReturnsPTUMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReturnsReductionValueMonthData) AS ReturnsReductionValueMonthData, 
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReturnsReductionValuePTUMonthData) AS ReturnsReductionValuePTUMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReductionValueMonthData) AS ReductionValueMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *ReductionValuePTUMonthData) AS ReductionValuePTUMonthData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (3) THEN 1 ELSE 0 END *PriceMonthData) AS PriceMonthData, 
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END* ReturnsReductionValuePTUData) AS ReturnsReductionValuePTUData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END* ReductionValuePTUData) AS ReductionValuePTUData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END* PriceSumData) AS PriceSumData,				
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END* ReductionValueData) AS ReductionValueData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END* PriceSumPTUData) AS PriceSumPTUData,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*ReturnsTicketCountSingle) AS ReturnsTicketCountSingle,
			SUM(CASE WHEN t.FarePriceReductionGroup_ID IN (1,2,12) THEN 1 ELSE 0 END*TicketCountSingle) AS TicketCountSingle,
			MAX(IsReturn)	AS IsReturn
			FROM
			(
				SELECT
				tt.LineName AS LineName,
				tt.LineNamePom AS LineNamePom,
				tt.Line_ID,
				tt.LineVariant,
				tt.LineType_ID,
				tt.LineValidFrom AS LineValidFrom,
				tt.FarePriceReductionGroup_ID,
				tt.Id, 
				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage OR red.MonthReduction =tt.ReductionPercentage THEN tt.PassangerNumber ELSE NULL END) AS PassangerNumber,
				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage OR red.MonthReduction =tt.ReductionPercentage THEN tt.ReductionValue ELSE NULL END) AS ReductionValue, 
				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage OR red.MonthReduction =tt.ReductionPercentage THEN tt.Price ELSE NULL END) AS Price, 
				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage OR red.MonthReduction =tt.ReductionPercentage THEN tt.VatAmount ELSE NULL END) AS VatAmount,
				ISNULL(tt.LineNumber, 0) AS LineNumber,
				MAX(ISNULL(tt.LineNumberPom, 0)) AS LineNumberPom,			
				--ISNULL(l.LineNumber, x.LineNumber) AS LineNumber,
				MAX(tt.LineFirstBusStopShortName) AS LineFirstBusStopShortName,
				MAX(tt.LineLastBusStopShortName) AS LineLastBusStopShortName,
				
				CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN CAST(Red.Reduction AS NVARCHAR)+'%' ELSE '' END AS Reduction,
				CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN CAST(Red.MonthReduction AS NVARCHAR)+'%' ELSE '' END AS ReductionMonth,

				MAX(CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN Red.Reduction ELSE 1 END) AS ReductionOrd,
				MAX(CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN Red.MonthReduction ELSE 1 END) AS ReductionMonthOrd,
				PermissionNr,
	



				--DANE DO ZASILENIA

				SUM(CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA1 ELSE 0 END) AS MonthTicketCountA1,
				SUM(CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA2 ELSE 0 END) AS MonthTicketCountA2,
				SUM(CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA3 ELSE 0 END) AS MonthTicketCountA3,

				SUM(CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.Price ELSE 0 END) AS ReturnsPriceSumData,
				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.Price ELSE 0 END), ((CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.VatAmount ELSE 0 END)))) AS ReturnsPTUData,
				
				(SUM(CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.ReductionValue ELSE 0 END)) AS ReturnsReductionValueData,
				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.ReductionValue ELSE 0 END), ((CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.VatAmount ELSE 0 END)))) AS ReturnsReductionValuePTUData,

				SUM(CASE WHEN IsReturn=1 THEN CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA1 ELSE 0 END ELSE 0 END) AS ReturnsMonthTicketCountA1,
				SUM(CASE WHEN IsReturn=1 THEN CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA2 ELSE 0 END ELSE 0 END) AS ReturnsMonthTicketCountA2,
				SUM(CASE WHEN IsReturn=1 THEN CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.MonthTicketCountA3 ELSE 0 END ELSE 0 END) AS ReturnsMonthTicketCountA3,

				SUM(CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.Price ELSE 0 END) AS ReturnsPriceSumMonthData,
				
				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.Price ELSE 0 END), ((CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.VatAmount ELSE 0 END)))) AS ReturnsPTUMonthData,

				SUM(CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.ReductionValue ELSE 0 END) AS ReductionValueMonthData,
				SUM(CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN CASE WHEN tt.PassangerNumber<0 THEN 1 ELSE 0 END ELSE 0 END) AS ReturnsTicketCount,	

				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.PassangerNumber ELSE 0 END) AS TicketCountSingle,

				SUM(CASE WHEN IsReturn=1 AND red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN CASE WHEN tt.PassangerNumber<0 THEN 1 ELSE 0 END ELSE 0 END) AS ReturnsTicketCountSingle,

				SUM([dbo].[SLS_GetVatValueM](CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.Price ELSE 0 END, (CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.VatAmount ELSE 0 END))) AS PTUMonthData,

				SUM([dbo].[SLS_GetVatValueM](CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.Price ELSE 0 END, (CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.VatAmount ELSE 0 END))) AS PTUData,
					--MONTH
				SUM(CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN CASE WHEN tt.PassangerNumber<0 THEN 1 ELSE 0 END ELSE 0 END) AS ReturnsTicketCountMonth,
				
				SUM(CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.ReductionValue ELSE 0 END) AS ReturnsReductionValueMonthData, 
				
				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.ReductionValue ELSE 0 END), ((CASE WHEN IsReturn=1 AND red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.VatAmount ELSE 0 END)))) AS ReturnsReductionValuePTUMonthData,
				--kuźwa
				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.ReductionValue ELSE 0 END), ((CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.VatAmount ELSE 0 END)))) AS ReductionValuePTUMonthData,

				SUM(CASE WHEN red.MonthReduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (3) THEN tt.Price ELSE 0 END) AS PriceMonthData, 

				SUM([dbo].[SLS_GetVatValueM](CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.ReductionValue ELSE 0 END, (CASE WHEN red.Reduction =tt.ReductionPercentage and FarePriceReductionGroup_ID in (1,2,12) THEN tt.VatAmount ELSE 0 END))) AS ReductionValuePTUData,
	
				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.ReductionValue ELSE NULL END) AS ReductionValueData, 

				SUM(CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.Price ELSE 0 END) AS PriceSumData, 

				SUM([dbo].[SLS_GetVatValueM]((CASE WHEN red.Reduction =tt.ReductionPercentage AND FarePriceReductionGroup_ID IN (1,2,12) THEN tt.Price ELSE 0 END), ((CASE WHEN  red.Reduction =tt.ReductionPercentage and FarePriceReductionGroup_ID in (1,2,12) THEN tt.VatAmount ELSE 0 END)))) AS PriceSumPTUData,

				IsReturn

				--/DANE DO ZASILENIA
				FROM
				(
					SELECT DISTINCT red.Reduction, RedMonth.Reduction AS MonthReduction--, red.ReductionId AS RedReductionId, RedMonth.ReductionId AS RedMonthReductionId
					FROM
					(
						SELECT --FarePriceReductionGroup_ID,
						rh.Reduction--, ReductionId
						FROM dbo.TCK_FarePriceReductionHistory rh WITH (NOLOCK)
						INNER JOIN #PomRedIds x WITH (NOLOCK) ON x.ReductionHistoryId = rh.id
						INNER JOIN dbo.TCK_FarePriceReductiON r WITH (NOLOCK) ON rh.FarePriceReduction_ID = r.ID 
						WHERE r.FarePriceReductionGroup_ID IN (1,2,12)
					) REd
					FULL JOIN
					(
						SELECT 
						DISTINCT
						--FarePriceReductionGroup_ID, 
						rh.Reduction --, ReductionId
						FROM dbo.TCK_FarePriceReductionHistory rh WITH (NOLOCK)
						INNER JOIN #PomRedIds x WITH (NOLOCK) ON x.ReductionHistoryId = rh.id
						INNER JOIN dbo.TCK_FarePriceReductiON r WITH (NOLOCK) ON rh.FarePriceReduction_ID = r.ID 
						WHERE r.FarePriceReductionGroup_ID IN (3)
					) RedMonth ON Red.Reduction = RedMonth.reduction
			 
				)  Red

				LEFT JOIN 

				(				
					SELECT

					CASE WHEN RTRIM(LTRIM(
					CASE WHEN @LineSkipNumberInLine =0 THEN 
						CASE WHEN @LineReplaceLineNumberEvidenceNumber =0 THEN ISNULL(l.LineNumber, x.LineNumber)
						ELSE ISNULL(p.LineNumberGov,'') 
					END 
					ELSE '0' END)) LIKE N'%[^0123456789]%' THEN 0
					ELSE
					CAST(RTRIM(LTRIM(CASE WHEN @LineSkipNumberInLine =0 THEN 
						CASE WHEN @LineReplaceLineNumberEvidenceNumber =0 THEN CASE WHEN ISNUMERIC(ISNULL(l.LineNumber, x.LineNumber)) =0 THEN '0' ELSE ISNULL(l.LineNumber, x.LineNumber) END
						ELSE ISNULL(p.LineNumberGov,'')
					END 
					ELSE '0' END))
					 AS INT)
					END					 AS LineNumber,

					CASE WHEN STUFF(LTRIM(ISNULL(l.LineNumber, x.LineNumber)),1,1,'') LIKE N'%[^0123456789]%' THEN 0
					ELSE
					CAST(CASE WHEN ISNUMERIC(ISNULL(l.LineNumber, x.LineNumber)) =0 THEN '0' ELSE ISNULL(l.LineNumber, x.LineNumber) END
					
					 AS INT)
					END
					 AS LineNumberPom,

					ISNULL(LineName,ISNULL(x.LineFirstBusStopName,'') + CASE WHEN ISNULL(x.LineLastBusStopName,'')='' THEN '' ELSE ISNULL(' - ' +x.LineLastBusStopName,'') END) AS LineNamePom,

					CASE WHEN @LineSkipNumberInLine =0 THEN 
						CASE WHEN @LineReplaceLineNumberEvidenceNumber =0 THEN ISNULL(l.LineNumber, x.LineNumber)
						ELSE ISNULL(p.LineNumberGov,'') 
					END 
					ELSE '' END+' '
					+ ' ' + ISNULL(LineName,ISNULL(x.LineFirstBusStopName,'') + CASE WHEN ISNULL(x.LineLastBusStopName,'')='' THEN '' ELSE ISNULL(' - ' +x.LineLastBusStopName,'') END) AS LineName,
					--l.ValidFrom AS LineValidFrom,
	
					--p.PermissionNr,
					CASE WHEN @LinePrintDiffVariant=0 THEN l.ValidFrom ELSE '1900-01-01' END	AS LineValidFrom,	
					CASE WHEN @LinePrintDiffVariant=0 THEN p.ApplicationDate ELSE '1900-01-01' END AS ApplicationDate,
					CASE WHEN @LinePrintDiffVariant=0 THEN p.PermissionNr ELSE '' END AS PermissionNr,

					t.FarePriceReductionGroup_ID,
					t.Id, 
					SIGN(t.PassangerNumber) * SUM(ISNULL(rate.Rate,CASE WHEN FarePriceReductionGroup_ID=3 THEN 0 ELSE 1 END))	AS PassangerNumber, 

					SUM(SIGN(t.PassangerNumber) * CASE WHEN FarePriceReductionGroup_ID=3 THEN 1 ELSE 0 END * ISNULL(rate.A1Rate,0)) AS MonthTicketCountA1,
					SUM(SIGN(t.PassangerNumber) * CASE WHEN FarePriceReductionGroup_ID=3 THEN 1 ELSE 0 END * ISNULL(rate.A2Rate,0)) AS MonthTicketCountA2,
					SUM(SIGN(t.PassangerNumber) * CASE WHEN FarePriceReductionGroup_ID=3 THEN 1 ELSE 0 END * ISNULL(rate.A3Rate,0)) AS MonthTicketCountA3,
									
					SUM(r.ReductionValue*JST) AS ReductionValue, 
					SUM(r.Price*JST) AS Price, 
					MAX(t.VatAmount) AS VatAmount,
					CASE WHEN SUM(t.PassangerNumber)<0 THEN 1 ELSE 0 END AS IsReturn,
					A1Rate,
					A2Rate,
					A3Rate,
					x.LineFirstBusStopShortName AS LineFirstBusStopShortName,
					x.LineLastBusStopShortName AS LineLastBusStopShortName,
					t.ReductionPercentage,
					l.Line_Id,
					CASE WHEN @LinePrintDiffVariant=0 THEN x.LineVariant ELSE 0 END AS LineVariant,
					x.LineType_ID
					FROM dbo.SLS_Ticket t WITH (NOLOCK) 
					INNER JOIN dbo.SLS_TicketRoute r WITH (NOLOCK) ON t.id = r.Ticket_ID
					INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
					INNER JOIN #PomTicketsRoute rt WITH (NOLOCK) ON rt.TicketRouteId = r.Id
					INNER JOIN (SELECT DISTINCT ReductionId FROM #PomRedIds) pr ON pr.ReductionId=t.FarePriceReduction_ID
					LEFT JOIN
					(	SELECT l.id AS Line_id, x.TicketRouteId, l.ValidFrom, l.Name AS LineName, LineNumber
						FROM dbo.TT_Line l WITH (NOLOCK) 
						INNER JOIN 
						(
							SELECT DISTINCT rr.Line_ID, TicketRouteId	
							FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
							INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
							INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id
							INNER JOIN dbo.TT_Ride rr WITH (NOLOCK) ON rr.ID = x.Ride_Id  -- rr.RideNumber = x.RideNumber AND ISNULL(rr.ValidFrom,'1900-01-01') = ISNULL(x.RideValidFrom,'1900-01-01') AND rr.RideVariant= x.RideVariant 
							--INNER JOIN dbo.Admin_Company c ON c.INumber = x.INumber
						) X ON l.Id= x.Line_Id
						
					 ) l ON rt.TicketRouteId = l.TicketRouteId
					LEFT JOIN
					(	SELECT x.ID AS XID, p.Line_ID, p.LineNumberGov, p.PermissionNumber, CAST(p.ApplicationDate AS DATE) AS ApplicationDate, CASE WHEN ISNULL(@LineShowOfficeCode,0)=0 THEN p.PermissionNumber ELSE ISNULL(p.PermissionNumber+'/','') + ISNULL(o.Office,'') END AS PermissionNr
						FROM dbo.TT_LinePermission p WITH (NOLOCK) 
						LEFT JOIN
						(
							SELECT c.id AS CompanyGov_ID, CASE c.CompanyType_ID WHEN 5 THEN 'W' WHEN 6 THEN 'P' WHEN 7 THEN 'G' WHEN 8 THEN 'R' WHEN 9 THEN 'M' ELSE 'D' END + com.SYMBOL AS Office
							FROM dbo.ADMIN_Company c WITH (NOLOCK) 
							INNER JOIN dbo.ADMIN_CompanyAddress a WITH (NOLOCK) ON c.ID = a.Company_ID AND a.CompanyAddressType_ID=1 --tylko główny
							INNER JOIN dbo.TT_Place pl WITH (NOLOCK) ON a.Place_ID = pl.ID
							INNER JOIN dbo.TT_Community com ON pl.COMMUNITY_ID = com.ID
						) o ON o.CompanyGov_Id = p.CompanyGov_Id
						INNER JOIN dbo.TT_Line l WITH (NOLOCK) ON l.id = p.Line_ID
						INNER JOIN 
						(
							SELECT DISTINCT rr.Line_Id, x.id
							FROM dbo.SLS_TicketRoute r WITH (NOLOCK)
							INNER JOIN dbo.SLS_RideRegistered x WITH (NOLOCK) ON r.RideRegistered_ID = x.ID
							INNER JOIN #PomTicketsRoute WITH (NOLOCK) ON #PomTicketsRoute.TicketRouteId = r.Id
							INNER JOIN dbo.TT_Ride rr WITH (NOLOCK) ON rr.id=x.Ride_id --rr.RideNumber = x.RideNumber AND ISNULL(rr.ValidFrom,'1900-01-01') = ISNULL(x.RideValidFrom,'1900-01-01') AND rr.RideVariant= x.RideVariant 
							INNER JOIN dbo.Admin_Company c WITH (NOLOCK) ON c.INumber = x.INumber

						) X ON l.ID= x.Line_ID

					) p ON p.XId = x.Id

				LEFT JOIN
				(	SELECT Line.Ticket_Id, Line.LineNumber, CASE @LineTicketJoin WHEN 0 THEN ISNULL(A1.Rate,0) WHEN 1 THEN ISNULL(A2.Rate,1) ELSE ISNULL(A3.Rate,0) END Rate, Line.RRID,
					ISNULL(A1.Rate,0) AS A1Rate, ISNULL(A2.Rate,1) AS A2Rate, ISNULL(A3.Rate,0) AS A3Rate
					FROM
					(
						SELECT t.Ticket_id, RRID, LineNumber
						FROM #PomReliefxxx t
						GROUP BY t.Ticket_ID, t.RRID, t.LineNumber
					) Line
					LEFT JOIN
					(	--jeden dla jednego kursu (reszta 0)
						
						SELECT 
						1 as Rate, y.Ticket_Id, RideRegisteredId AS RRID
						FROM
						(
							SELECT DISTINCT t.Ticket_id, (SELECT TOP 1 y.ID FROM dbo.SLS_TicketRoute y WITH (NOLOCK) INNER JOIN #PomTicketsRoute z ON z.TicketRouteId = y.ID WHERE y.Ticket_ID = t.Ticket_ID ORDER BY y.RouteNumber ASC, y.RelationNumber ASC) AS RideRegisteredId
							
							FROM #PomReliefxxx t

						) y
						
					) A1 ON A1.Ticket_Id = Line.Ticket_Id AND Line.RRID = A1.rrID --AND Line.RideNumber = A1.RideNumber
					LEFT JOIN
					(	--w częściach dla każdego 
						SELECT x1.LineNumber, x1.Ticket_Id,
						x1.Rate/CASE WHEN RecTicketCnt.RecTicketCnt=0 THEN 1 ELSE (RecTicketCnt.RecTicketCnt*1.00) END  AS Rate, RRID
						FROM
						(SELECT  COUNT(*) AS Rate, LineNumber, Pom.id AS Ticket_Id, (RRID) AS RRID 
							FROM
							(
								SELECT t.Ticket_id AS ID, RRID, LineNumber
								FROM #PomReliefxxx t
								GROUP BY t.Ticket_ID, t.RRID, t.LineNumber
							) Pom
							GROUP BY Pom.ID, Pom.RRID, Pom.LineNumber
						) x1
						INNER JOIN
						(	SELECT  COUNT(*) AS RecTicketCnt, Pom.id AS Ticket_Id 
							FROM
							(	SELECT t.Ticket_id AS ID, RRID, LineNumber
								FROM #PomReliefxxx t
								GROUP BY t.Ticket_ID, t.RRID, t.LineNumber
							) Pom GROUP BY Pom.ID
						) RecTicketCnt ON RecTicketCnt.Ticket_Id = x1.Ticket_Id

					) A2 ON  A2.Ticket_Id = Line.Ticket_Id AND A2.LineNumber = Line.LineNumber AND Line.RRID = A2.RRID

					LEFT JOIN
					(	--jeden dla jednego kursu 
						SELECT 1 AS Rate, t.Ticket_id, RRID
						FROM #PomReliefxxx t
						GROUP BY t.Ticket_ID, t.RRID, t.LineNumber
						
					) A3 ON A3.Ticket_Id = Line.Ticket_Id AND Line.RRID = A3.rrID
			
				) Rate ON Rate.LineNumber = x.LineNumber AND Rate.Ticket_Id = t.id AND Rate.RRID = r.id
			

				GROUP BY
				t.Id
				, t.FarePriceReduction_ID
				, t.FarePriceReductionGroup_ID
				, t.ReductionPercentage
				, rate.Rate
				, Rate.A1Rate
				, Rate.A2Rate
				, Rate.A3Rate
				, p.LineNumberGov
				, CASE WHEN @LinePrintDiffVariant=0 THEN l.ValidFrom ELSE '1900-01-01' END
				, CASE WHEN @LinePrintDiffVariant=0 THEN p.ApplicationDate ELSE '1900-01-01' END
				, CASE WHEN @LinePrintDiffVariant=0 THEN p.PermissionNr ELSE '' END
				, t.PassangerNumber 
				, ISNULL(l.LineNumber, x.LineNumber) 
				, ISNULL(LineName,ISNULL(x.LineFirstBusStopName,'') + CASE WHEN ISNULL(x.LineLastBusStopName,'')='' THEN '' ELSE ISNULL(' - ' +x.LineLastBusStopName,'') END)
				, x.LineFirstBusStopShortName
				, x.LineLastBusStopShortName
				, l.LineName
				, l.Line_ID
				, CASE WHEN @LinePrintDiffVariant=0 THEN x.LineVariant ELSE 0 END
				, x.LineType_ID

				) tt ON 1=1 

			GROUP BY
				tt.ID,
				tt.FarePriceReductionGroup_ID,
				tt.LineNumber,
				tt.LineName,
				tt.LineNamePom,
				tt.Line_ID,
				tt.LineVariant,
				tt.LineType_ID,
				tt.LineNumber,
				tt.IsReturn,
				tt.LineValidFrom,
				tt.VatAmount,
				tt.ReductionPercentage,
				Red.Reduction,
				Red.MonthReduction,
				CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN CAST(Red.Reduction AS NVARCHAR)+'%' ELSE '' END,
				CASE WHEN @ShowLineTicketReliefByRelief = 1 THEN CAST(Red.MonthReduction AS NVARCHAR)+'%' ELSE '' END,
				tt.PermissionNr
			) AS t

			WHERE @CountNettValuePerEachMonth =0

			GROUP BY 
			t.VatAmount
			, t.Line_ID
			, t.LineName
			, t.LineValidFrom
			, t.LineVariant
			, t.LineNumber
			, t.LineType_ID
			, Reduction
			, ReductionMonth,
			t.PermissionNr
		) Pom
		GROUP BY 
		LTRIM(RTRIM(LineName)),
		Line_ID,
		LineValidFrom,
		LineVariant,
		LineType_ID,
		ReductionMonth,
		Reduction

	) Pom
	ORDER BY 
	
	LineNumber ASC,
	LineNamePom ASC,
	
	ReductionOrd DESC,
	ReductionMonthOrd DESC
	
	---------------------------------------------------------------
	-------------------UZUPEŁNIANIE DANYCH-------------------------
	---------------------------------------------------------------

	

	

	INSERT INTO dbo.ADMIN_ReportResultXLineSum 
		(	ReportResultExportData_ID, Line_ID, LineNumber, LineName, LineShortName, LineVariant, LineValidFrom, LineType_ID, SingleReduction, MonthReduction, TicketCount, PriceSum, VATAmountSum,
			DoplatySum, DoplatyVATAmountSum, DoplatyNettoSum, MonthTicketCountA1, MonthTicketCountA2, MonthTicketCountA3,
			MonthPriceSum, MonthVATAmountSum, MonthDoplatySum, MonthDoplatyVATAmountSum, MonthDoplatyNettoSum,
			IncludesReturns, ReturnsTicketCount, ReturnsPriceSum, ReturnsVATAmountSum,
			ReturnsDoplatySum, ReturnsDoplatyVATAmountSum, ReturnsDoplatyNettoSum, ReturnsMonthTicketCountA1, ReturnsMonthTicketCountA2, ReturnsMonthTicketCountA3,
			ReturnsMonthPriceSum, ReturnsMonthVATAmountSum, ReturnsMonthDoplatySum, ReturnsMonthDoplatyVATAmountSum, ReturnsMonthDoplatyNettoSum
		)
		SELECT
			@ReportResultExportDataID, ISNULL(Line_ID,0), LineNumberPom, LineNamePom, ISNULL(LineShortName,''), LineVariant, LineValidFrom, LineType_ID, ISNULL(CAST(REPLACE(Reduction,'%','') AS INT),0), ISNULL(CAST(REPLACE(ReductionMonth,'%','') AS INT),0),
			
			ISNULL(TicketCountSingle,0), ISNULL(PriceSUMData,0), ISNULL(PriceSUMPTUData,0),
			ISNULL(ReductionValueData,0), ISNULL(ReductionValuePTUData,0), ISNULL(ReductionValueData-ReductionValuePTUData,0), ISNULL(MonthTicketCountA1,0), ISNULL(MonthTicketCountA2,0), ISNULL(MonthTicketCountA3,0),
			ISNULL(PriceMonthData,0), ISNULL(PTUMonthData,0), ISNULL(ReductionValueMonthData,0), ISNULL(ReductionValuePTUMonthData,0), ISNULL(ReductionValueMonthData-ReductionValuePTUMonthData,0),
			
			CASE WHEN ReturnsTicketCountSingle >0 OR ReturnsMonthTicketCountA1>0 THEN 1 ELSE 0 END AS IncludesReturns, ISNULL(ReturnsTicketCountSingle,0), ISNULL(ReturnsPriceSumData,0) AS ReturnsPriceData, ISNULL(ReturnsPTUData,0),
			ISNULL(ReturnsReductionValueData,0), ISNULL(ReturnsReductionValuePTUData,0), ISNULL(ReturnsReductionValueData - ReturnsReductionValuePTUData,0),
			ISNULL(ReturnsMonthTicketCountA1,0) AS ReturnsMonthTicketCountA1, ISNULL(ReturnsMonthTicketCountA2,0) AS ReturnsMonthTicketCountA2, ISNULL(ReturnsMonthTicketCountA3,0) AS ReturnsMonthTicketCountA3,
			ISNULL(ReturnsPriceSumMonthData,0), ISNULL(ReturnsPTUMonthData,0), ISNULL(ReturnsReductionValueMonthData,0), ISNULL(ReturnsReductionValuePTUMonthData,0), ISNULL(ReturnsReductionValueMonthData - ReturnsReductionValuePTUMonthData,0)
			
		--drop table #PomReliefLine
		FROM #PomReliefLine
		
		WHERE NOT EXISTS(SELECT ID FROM dbo.ADMIN_ReportResultXLineSum WITH (NOLOCK) WHERE ReportResultExportData_ID = @ReportResultExportDataID) 
		--AND Line_id IS NOT NULL


	---------------------------------------------------------------
	--------------------REZULTAT KOŃCOWY---------------------------
	---------------------------------------------------------------
	DELETE FROM dbo.SLS_ReliefLinePom WHERE Guid=@Guid

	--SELECT * FROM #PomReliefLine
	INSERT INTO dbo.SLS_ReliefLinePom (
		[Guid],
		[LP],
		[LineName],
		[TicketCount],
		[TicketCountMonth],
		[Brutto],
		[Netto],
		[NettoMonth],
		[BruttoMonth],
		[ReductionValue],
		[LineValidFrom],
		[ReductionMonth],
		[Reduction],
		[Firmy],
		[Bileterki],
		[OfficeList],
		[PermissionNr],
		[ReductionMonthOrd],
		[ReductionOrd],
		[Line_id],
		[LineNumber],
		[LineNamePom],
		[LineShortName],
		[LineVariant],
		[LineType_ID],
		[MonthTicketCountA1],
		[MonthTicketCountA2],
		[MonthTicketCountA3],
		[ReturnsTicketCount],
		[PTUMonthData],
		[PTUData],
		[ReturnsTicketCountMonth],
		[ReturnsPriceSumData],
		[ReturnsPTUData],
		[ReturnsReductionValueData],
		[ReturnsReductionValuePTUData],
		[ReturnsMonthTicketCountA1],
		[ReturnsMonthTicketCountA2],
		[ReturnsMonthTicketCountA3],
		[ReturnsPriceSumMonthData],
		[ReturnsPTUMonthData],
		[ReturnsReductionValueMonthData],
		[ReturnsReductionValuePTUMonthData],
		[ReductionValueMonthData],
		[ReductionValuePTUMonthData],
		[PriceMonthData],
		[ReductionValuePTUData],
		[ReductionValueData],
		[PriceSumData],
		[PriceSumPTUData],
		[ReturnsTicketCountSingle],
		[TicketCountSingle],
		[ReturnsReductionValueNettoData],
		[ReturnsReductionValueNettoMonthData],
		[ReturnsPriceSumNettoData],
		[ReturnsPriceSumNettoMonthData],
		[ReductionValueNettoData],
		[ReductionValueNettoMonthData],
		[PriceSumNettoData],
		[PriceMonthNettoData],
		[CountingNettSum],
		[ReturnKind]
		)

		SELECT 
		@Guid	AS Guid,
		MAX(Lp) AS LP, LineName,
		SUM(TicketCount) AS TicketCount,
		SUM(TicketCountMonth) AS TicketCountMonth,

		SUM(Brutto) AS Brutto, SUM(Netto) AS Netto, SUM(NettoMonth) AS NettoMonth, SUM(BruttoMonth) AS BruttoMonth, SUM(ReductionValue) AS ReductionValue, 
		MAX(LineValidFrom) AS LineValidFrom, 
		ReductionMonth,
		Reduction,
		MAX(Firmy) AS Firmy, MAX(Bileterki) AS Bileterki, MAX(OfficeList) AS OfficeList, MAX(PermissionNr) AS PermissionNr, MAX(ReductionMonthOrd) AS ReductionMonthOrd, MAX(ReductionOrd) AS ReductionOrd,

		Line_id,
		MAX(LineNumber) AS LineNumber,
		MAX(LineNamePom) AS LineNamePom,
		MAX(LineShortName) AS LineShortName,
		MAX(LineVariant) AS LineVariant,
		MAX(LineType_ID) AS LineType_ID,
		SUM(MonthTicketCountA1) AS MonthTicketCountA1,
		SUM(MonthTicketCountA2) AS MonthTicketCountA2,
		SUM(MonthTicketCountA3) AS MonthTicketCountA3,
		SUM(ReturnsTicketCount) AS ReturnsTicketCount,
		SUM(PTUMonthData) AS PTUMonthData,
		SUM(PTUData) AS PTUData,
		
		SUM(ReturnsTicketCountMonth) AS ReturnsTicketCountMonth,
		SUM(ReturnsPriceSumData) AS ReturnsPriceSumData,
		SUM(ReturnsPTUData) AS ReturnsPTUData,

		SUM(ReturnsReductionValueData) AS ReturnsReductionValueData,
		SUM(ReturnsReductionValuePTUData) AS ReturnsReductionValuePTUData,

		SUM(ReturnsMonthTicketCountA1) AS ReturnsMonthTicketCountA1,
		SUM(ReturnsMonthTicketCountA2) As ReturnsMonthTicketCountA2,
		SUM(ReturnsMonthTicketCountA3) AS ReturnsMonthTicketCountA3,

		SUM(ReturnsPriceSumMonthData) AS ReturnsPriceSumMonthData,
		SUM(ReturnsPTUMonthData) AS ReturnsPTUMonthData,
		SUM(ReturnsReductionValueMonthData) AS ReturnsReductionValueMonthData, 
		SUM(ReturnsReductionValuePTUMonthData) AS ReturnsReductionValuePTUMonthData,
		SUM(ReductionValueMonthData) AS ReductionValueMonthData,
		SUM(ReductionValuePTUMonthData) AS ReductionValuePTUMonthData,
		SUM(PriceMonthData) AS PriceMonthData, 
		
		SUM(ReductionValuePTUData) AS ReductionValuePTUData,
		SUM(ReductionValueData) AS ReductionValueData,			
		SUM(PriceSumData) AS PriceSumData,
		SUM(PriceSumPTUData) AS PriceSumPTUData,
		SUM(ReturnsTicketCountSingle) AS ReturnsTicketCountSingle,
		SUM(TicketCountSingle) AS TicketCountSingle,

		
		SUM(ReturnsReductionValueData - ReturnsReductionValuePTUData) AS ReturnsReductionValueNettoData,
		SUM(ReturnsReductionValueMonthData - ReturnsReductionValuePTUMonthData) AS ReturnsReductionValueNettoMonthData,
		
		SUM(ReturnsPriceSumData -ReturnsPTUData) AS ReturnsPriceSumNettoData,
		SUM(ReturnsPriceSumMonthData -ReturnsPTUMonthData) AS ReturnsPriceSumNettoMonthData,

		SUM(ReductionValueData -ReductionValuePTUData) AS ReductionValueNettoData,
		SUM(ReductionValueMonthData -ReductionValuePTUMonthData) AS ReductionValueNettoMonthData,

		SUM(PriceSumData- PriceSumPTUData) AS PriceSumNettoData,
		SUM(PriceMonthData -PTUMonthData) AS PriceMonthNettoData, 
		MAX(CountingNettSum) AS CountingNettSum,



		--ISNULL(ReturnX.Returns, 0) AS ReturnsX,
		MAX(CAST(ReturnKind AS VARCHAR)) AS ReturnKind
		FROM #PomReliefLine
		GROUP BY
		LineName,
		Line_ID,
		ReductionMonth,
		Reduction

		ORDER BY
		LineNumber ASC,
		LineNamePom ASC,
	
		ReductionOrd DESC,
		ReductionMonthOrd DESC



		

END
ELSE
BEGIN	


	IF @UnsetLineTicketReliefByRelief=1
	BEGIN
	

	SELECT 

		l.Lp														AS LP,
		l.LineName													AS LineName,
		
		MAX(ISNULL(l.PermissionNr,''))								AS PermissionNr,
		MAX(ISNULL(l.LineValidFrom,''))								AS LineValidFrom,
		SUM(ISNULL(l.ReductionValue,0))								AS ReductionValue,
		''															AS Reduction,
		''															AS ReductionMonth,
		CASE WHEN @SpecialCountLineTickets=0 THEN ISNULL(MAX(ReturnX.TicketCount), SUM(ISNULL(l.TicketCount,0))) ELSE 
		(SELECT  SUM((PassangerNumber)) AS PassangerNumber--, FarePriceReduction_ID
		from
		(
			SELECT t.FarePriceReduction_ID, t.PassangerNumber, r.Line_ID, 
			ROW_NUMBER() OVER ( PARTITION BY t.id ORDER BY tr.RouteNumber, tr.RelationNumber ) as LP
			FROM sls_ticket t
			INNER JOIN SLS_TicketRoute tr WITH (NOLOCK) ON tr.Ticket_ID = t.id
			INNER JOIN #TicketRoutePom rr WITH (NOLOCK) ON rr.TicketRouteIDPom = tr.Id
			inner join SLS_RideRegistered x on x.id = tr.RideRegistered_ID
			inner join TT_Ride r ON r.id = x.Ride_ID
		) x
		INNER JOIN @ForLines l ON l.id = x.Line_ID
		and lp=1 AND @SpecialCountLineTickets=1 
		) END				AS TicketCount,
		ISNULL(MAX(ReturnX.TicketCountMonth), SUM(ISNULL(l.TicketCountMonth,0)))	AS TicketCountMonth,
		ISNULL(MAX(ReturnX.Brutto), SUM(ISNULL(l.Brutto,0)))						AS Brutto,
		ISNULL(MAX(ReturnX.BruttoMonth), SUM(ISNULL(l.BruttoMonth,0)))				AS BruttoMonth,
		100*CASE WHEN MAX(sm.Summ) = 0.0 THEN 0 ELSE (ISNULL(ISNULL(MAX(ReturnX.Brutto), SUM(ISNULL(l.Brutto,0))),0) +ISNULL(MAX(ReturnX.BruttoMonth), SUM(ISNULL(l.BruttoMonth,0)))) /MAX(sm.Summ)
		END
	AS Part,
	
	ISNULL(MAX(ReturnX.Netto), SUM(ISNULL(l.Netto,0)))						AS Netto,
	ISNULL(MAX(ReturnX.NettoMonth), SUM(ISNULL(l.NettoMonth,0)))			AS NettoMonth,

	ISNULL(MAX(ReturnX.Brutto), SUM(ISNULL(l.Brutto,0)))-ISNULL(MAX(ReturnX.Netto), SUM(ISNULL(l.Netto,0))) AS PTU,
	ISNULL(MAX(ReturnX.BruttoMonth), SUM(ISNULL(l.BruttoMonth,0))) - ISNULL(MAX(ReturnX.NettoMonth), SUM(ISNULL(l.NettoMonth,0))) AS PTUMonth,
	--ISNULL(MAX(ReturnX.PTU), SUM(ISNULL(l.PTUData,0)))						AS PTU,
	--ISNULL(MAX(ReturnX.PTUMonth), SUM(ISNULL(l.PTUMonthData,0)))			AS PTUMonth,

	MAX(l.ReturnKind)												AS ReturnKind,
	MAX(l.Firmy)													AS Firmy,
	MAX(l.Bileterki)												AS Bileterki,
	MAX(l.OfficeList)												AS OfficeList,
	ISNULL(ReturnX.Returns, 0) AS ReturnsX,
	MAX(l.CountingNettSum) AS CountingNettSum

	FROM dbo.SLS_ReliefLinePom l
	INNER JOIN
	 (	SELECT
		SUM(ISNULL(Brutto,0))+ SUM(ISNULL(BruttoMonth,0)) AS Summ
		FROM dbo.SLS_ReliefLinePom WHERE Guid=@Guid 
	 ) sm	
	 ON 1=1
	 AND Guid=@Guid
	  -- zwroty oddzielne linie
	LEFT JOIN (

			 --dodatnie
		SELECT 1 AS Returns,
		l.LP,
		SUM(ISNULL(l.TicketCount,0) +ISNULL(l.ReturnsTicketCount,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=0 THEN ISNULL(l.ReturnsTicketCountMonth,0) ELSE 0 END) AS TicketCount,
		SUM(ISNULL(l.TicketCountMonth,0)+ISNULL(l.ReturnsTicketCountMonth,0)) AS TicketCountMonth,

		SUM(Brutto+CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsReductionValueData,0)+ ISNULL(ReturnsReductionValueMonthData,0) +ISNULL(ReturnsPriceSumMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumData,0)+ISNULL(ReturnsPriceSumMonthData,0))/100.0  END END)
			
		  AS Brutto,
		
		SUM(ISNULL(BruttoMonth,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueMonthData,0))/100.00 ELSE ISNULL(ReturnsPriceSumMonthData,0)/100.0 END) AS BruttoMonth,


		SUM(Netto+CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueNettoData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueNettoData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsReductionValueNettoData,0)+ ISNULL(ReturnsReductionValueNettoMonthData,0) +ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumNettoData,0)+ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END END)
			
		  AS Netto,
		
		SUM(ISNULL(NettoMonth,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueNettoMonthData,0))/100.00 ELSE ISNULL(ReturnsPriceSumNettoMonthData,0)/100.0 END) AS NettoMonth,


		SUM(PTUData+CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValuePTUData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsReductionValuePTUData,0)+ ISNULL(ReturnsReductionValuePTUMonthData,0) +ISNULL(ReturnsPTUMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPTUData,0)+ISNULL(ReturnsPTUMonthData,0))/100.0  END END)
			
		  AS PTU,
		
		SUM(ISNULL(PTUMonthData,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUMonthData,0))/100.00 ELSE ISNULL(ReturnsPTUMonthData,0)/100.0 END) AS PTUMonth,
		MAX(CountingNettSum) AS CountingNettSum
		FROM dbo.SLS_ReliefLinePom l
		WHERE (l.TicketCount >0 OR l.TicketCountMonth>0 OR l.ReturnsTicketCount >0 OR l.ReturnsTicketCountMonth>0 ) AND l.Guid=@Guid
		AND 
		EXISTS(SELECT x.Lp FROM dbo.SLS_ReliefLinePom x  WHERE x.Guid=@Guid AND (ReturnsTicketCount >0 OR ReturnsTicketCountMonth >0) AND x.LP = l.LP)
		GROUP BY l.Lp
				
		UNION ALL

		SELECT DISTINCT 1 AS Returns,
		l.Lp,
		0 AS TicketCount, 0 AS TicketCountMonth,
		0.0 AS Brutto, 0.0 AS BruttoMonth,
		0.0 AS Netto, 0.0 AS NettoMonth,
		0.0 AS PTU, 0.0 AS PTUMonth,
		@CountingNettSum AS CountingNettSum
		FROM dbo.SLS_ReliefLinePom l
		WHERE (ReturnsTicketCount >0 OR ReturnsTicketCountMonth >0) AND l.Guid=@Guid
				AND NOT EXISTS( SELECT t1.Lp 
								FROM dbo.SLS_ReliefLinePom t1
								WHERE Guid=@Guid AND t1.Lp = l.Lp AND (t1.TicketCount >0 OR t1.TicketCountMonth>0)
							)
		UNION ALL
		-- ujemne czyli zwroty
		SELECT 2 AS Returns,
		l.Lp,
		SUM(-ISNULL(l.ReturnsTicketCount,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=0 THEN -ISNULL(ReturnsTicketCountMonth,0) ELSE 0 END) AS TicketCount, 
		SUM(-ISNULL(l.ReturnsTicketCountMonth,0)) AS TicketCountMonth,

		SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsReductionValueData,0)+ ISNULL(ReturnsReductionValueMonthData,0) +ISNULL(ReturnsPriceSumMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsPriceSumMonthData,0))/100.0  END) END)
			
		  AS Brutto,
		
		
		SUM(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValueMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPriceSumMonthData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPriceSumMonthData,0))/100.0  END)		
		AS BruttoMonth,

		SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueNettoData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsReductionValueNettoData,0)+ ISNULL(ReturnsReductionValueNettoMonthData,0) +ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END) END)
			
		  AS Netto,
		
		
		SUM(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValueNettoMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPriceSumNettoMonthData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END)		
		AS NettoMonth,

		SUM(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValuePTUData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsReductionValuePTUData,0)+ ISNULL(ReturnsReductionValuePTUMonthData,0) +ISNULL(ReturnsPTUMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsPTUMonthData,0))/100.0  END) END)
			
		  AS PTU,
		
		
		SUM(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValuePTUMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPTUMonthData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPTUMonthData,0))/100.0  END)		
		AS PTUMonth,
		MAX(CountingNettSum) AS CountingNettSum
				
		FROM dbo.SLS_ReliefLinePom l
		WHERE (ReturnsTicketCount >0 OR ReturnsTicketCountMonth>0) AND l.Guid=@Guid
		GROUP BY l.Lp
		
		UNION ALL
		-- łącznie
		SELECT 3 AS Returns,
		l.LP,
		SUM(ISNULL(l.TicketCount,0)) AS TicketCount, 
		SUM(ISNULL(l.TicketCountMonth,0)) AS TicketCountMonth,
		SUM(ISNULL(Brutto,0))  AS Brutto,
		SUM(ISNULL(BruttoMonth,0)) AS BruttoMonth,
		SUM(ISNULL(Netto,0))  AS Netto,
		SUM(ISNULL(NettoMonth,0)) AS NettoMonth,
		SUM(ISNULL(PTUData,0))  AS PTU,
		SUM(ISNULL(PTUMonthData,0)) AS PTUMonth,
		MAX(CountingNettSum) AS CountingNettSum
		FROM dbo.SLS_ReliefLinePom l
		WHERE EXISTS( SELECT t1.Lp 
								FROM dbo.SLS_ReliefLinePom t1
								WHERE t1.Guid=@Guid AND t1.Lp = l.Lp AND (t1.ReturnsTicketCount >0 OR t1.ReturnsTicketCountMonth>0))
			AND  l.Guid=@Guid
		GROUP BY l.Lp

	) AS ReturnX ON
	ReturnX.LP = l.LP AND @WithReturnsMode= 1 AND (ISNULL(@ShowLineTicketReliefByRelief,0) =0 OR @UnsetLineTicketReliefByRelief=1)

	GROUP BY l.Lp, l.LineName, /*l.ReturnKind,*/ ISNULL(ReturnX.Returns, 0)

	ORDER BY l.Lp
	
	


	END
	ELSE
	BEGIN

	

	SELECT 

		l.Lp,
		l.LineName,
		l.PermissionNr,
		l.LineValidFrom,
		l.ReductionValue,
		l.Reduction,
		l.ReductionMonth,
		ISNULL(ReturnX.TicketCount, l.TicketCount) AS TicketCount,
		ISNULL(ReturnX.TicketCountMonth, l.TicketCountMonth) AS TicketCountMonth,

		ISNULL(ReturnX.Brutto, l.Brutto) AS Brutto,
		ISNULL(ReturnX.BruttoMonth, l.BruttoMonth) AS BruttoMonth,

		ISNULL(ReturnX.Netto, l.Netto) AS Netto,
		ISNULL(ReturnX.NettoMonth, l.NettoMonth) AS NettoMonth,
		
		--ISNULL(ReturnX.PTU, l.PTUData) AS PTU,
		--ISNULL(ReturnX.PTUMonth, l.PTUMonthData) AS PTUMonth,
		ISNULL(ReturnX.Brutto, ISNULL(l.Brutto,0))-ISNULL(ReturnX.Netto, ISNULL(l.Netto,0)) AS PTU,
		ISNULL(ReturnX.BruttoMonth, ISNULL(l.BruttoMonth,0)) - ISNULL(ReturnX.NettoMonth, ISNULL(l.NettoMonth,0)) AS PTUMonth,

		100*CASE WHEN sm.Summ = 0.0 THEN 0.0 ELSE (ISNULL(ISNULL(ReturnX.Brutto, l.Brutto),0.0) +ISNULL(ReturnX.BruttoMonth, l.BruttoMonth))  /sm.Summ
		END
	AS Part,
	
	l.ReturnKind,
	l.Firmy,
	l.Bileterki,
	l.OfficeList,
	ISNULL(ReturnX.Returns, 0) AS ReturnsX,
	l.CountingNettSum AS CountingNettSum
	FROM dbo.SLS_ReliefLinePom l
	INNER JOIN
	 (	SELECT 
		SUM(Brutto)+ SUM(BruttoMonth) AS Summ
		FROM dbo.SLS_ReliefLinePom WHERE Guid=@Guid
	 ) sm	
	 ON 1=1 AND l.Guid=@Guid
	  -- zwroty oddzielne linie
	LEFT JOIN (
		-- dodatnie
		SELECT 1 AS Returns,
		l.LP,
		ISNULL(l.TicketCount,0) +ISNULL(l.ReturnsTicketCount,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=0 THEN ISNULL(l.ReturnsTicketCountMonth,0) ELSE 0 END AS TicketCount,
		ISNULL(l.TicketCountMonth,0)+ISNULL(l.ReturnsTicketCountMonth,0) AS TicketCountMonth,

		ISNULL(brutto,0) +CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsReductionValueData,0)+ ISNULL(ReturnsReductionValueMonthData,0) +ISNULL(ReturnsPriceSumMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumData,0)  +ISNULL(ReturnsPriceSumMonthData,0))/100.0  END END
			
		  AS Brutto,

		ISNULL(BruttoMonth,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueMonthData,0))/100.00 ELSE ISNULL(ReturnsPriceSumMonthData,0)/100.0 END AS BruttoMonth,
		
		ISNULL(Netto,0) +CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueNettoData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueNettoData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsReductionValueNettoData,0)+ ISNULL(ReturnsReductionValueNettoMonthData,0) +ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumNettoData,0)  +ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END END
			
		  AS Netto,

		ISNULL(NettoMonth,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueNettoMonthData,0))/100.00 ELSE ISNULL(ReturnsPriceSumNettoMonthData,0)/100.0 END AS NettoMonth,

				
		ISNULL(PTUData,0) +CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUData,0))/100.00 ELSE
			
			CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValuePTUData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsReductionValuePTUData,0)+ ISNULL(ReturnsReductionValuePTUMonthData,0) +ISNULL(ReturnsPTUMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPTUData,0)  +ISNULL(ReturnsPTUMonthData,0))/100.0  END END
		  AS PTU,

		ISNULL(PTUMonthData,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUMonthData,0))/100.00 ELSE ISNULL(ReturnsPTUMonthData,0)/100.0 END AS PTUMonth,
		CountingNettSum AS CountingNettSum
		FROM dbo.SLS_ReliefLinePom l
		WHERE (l.TicketCount >0 OR l.TicketCountMonth>0) AND l.Guid=@Guid
		AND 
		EXISTS(SELECT x.Lp FROM dbo.SLS_ReliefLinePom x WHERE x.Guid=@Guid AND (ReturnsTicketCount >0 OR ReturnsTicketCountMonth >0) AND x.LP = l.LP)
				
		UNION ALL

		SELECT DISTINCT 1 AS Returns,
		l.Lp,
		0 AS PassangerNumber, 0.0 AS ReductionValue, 0.0 AS Price, 0.0 AS VatAmount,
		0.0 AS Netto, 0.0 AS NettoMonth,

		0.0 AS PTU, 0.0 AS PTUMonth,
		CountingNettSum AS CountingNettSum
		FROM dbo.SLS_ReliefLinePom l
		WHERE (ReturnsTicketCount >0 OR ReturnsTicketCountMonth >0) AND l.Guid=@Guid
				AND NOT EXISTS( SELECT t1.Lp 
								FROM dbo.SLS_ReliefLinePom t1
								WHERE t1.Guid=@Guid AND t1.Lp = l.Lp AND (t1.TicketCount >0 OR t1.TicketCountMonth>0)
							)
		UNION ALL
		-- ujemne czyli zwroty
		SELECT 2 AS Returns,
		l.Lp,
		-ISNULL(l.ReturnsTicketCount,0) + CASE WHEN @LineSeparateMonthAndSingleTickets=0 THEN -ISNULL(ReturnsTicketCountMonth,0) ELSE 0 END AS TicketCount, 
		-ISNULL(l.ReturnsTicketCountMonth,0) AS TicketCountMonth,

		(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsReductionValueData,0)+ ISNULL(ReturnsReductionValueMonthData,0) +ISNULL(ReturnsPriceSumMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumData,0)+ ISNULL(ReturnsPriceSumMonthData,0))/100.0  END) END)
			
		  AS Brutto,
		
		
		(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValueMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPriceSumMonthData,0)+ISNULL(ReturnsReductionValueMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPriceSumMonthData,0))/100.0  END)		
		AS BruttoMonth,

		(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValueNettoData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValueNettoData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsReductionValueNettoData,0)+ ISNULL(ReturnsReductionValueNettoMonthData,0) +ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPriceSumNettoData,0)+ ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END) END)
			
		  AS Netto,
		
		
		(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValueNettoMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPriceSumNettoMonthData,0)+ISNULL(ReturnsReductionValueNettoMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPriceSumNettoMonthData,0))/100.0  END)		
		AS NettoMonth,

		(CASE WHEN @LineSeparateMonthAndSingleTickets=1 THEN (ISNULL(ReturnsReductionValuePTUData,0))/100.00 ELSE
			
			-(CASE  @OnlyPaymentsMode WHEN 0 THEN (ISNULL(ReturnsReductionValuePTUData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0
									WHEN 1 THEN  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsReductionValuePTUData,0)+ ISNULL(ReturnsReductionValuePTUMonthData,0) +ISNULL(ReturnsPTUMonthData,0))/100.0 
									ELSE  (ISNULL(ReturnsPTUData,0)+ ISNULL(ReturnsPTUMonthData,0))/100.0  END) END)
			
		  AS PTU,
		
		
		(CASE  @OnlyPaymentsMode WHEN 0 THEN -ISNULL(ReturnsReductionValuePTUMonthData,0)/100.0
									WHEN 1 THEN -(ISNULL(ReturnsPTUMonthData,0)+ISNULL(ReturnsReductionValuePTUMonthData,0))/100.0 
									ELSE -(ISNULL(ReturnsPTUMonthData,0))/100.0  END)		
		AS PTUMonth,
		CountingNettSum AS CountingNettSum

		FROM dbo.SLS_ReliefLinePom l
		WHERE (ReturnsTicketCount >0 OR ReturnsTicketCountMonth>0) AND l.Guid=@Guid

		UNION ALL
		-- łącznie
		SELECT 3 AS Returns,
		l.LP,
		ISNULL(l.TicketCount,0) AS TicketCount, 
		ISNULL(l.TicketCountMonth,0) AS TicketCountMonth,
		Brutto  AS Brutto,
		BruttoMonth AS BruttoMonth,

		Netto  AS Netto,
		NettoMonth AS NettoMonth,
		PTUData  AS PTUData,
		PTUMonthData AS PTUMonthData,
		CountingNettSum AS CountingNettSum

		FROM dbo.SLS_ReliefLinePom l
		WHERE EXISTS( SELECT t1.Lp 
								FROM dbo.SLS_ReliefLinePom t1
								WHERE t1.Guid=@Guid AND t1.Lp = l.Lp AND (t1.ReturnsTicketCount >0 OR t1.ReturnsTicketCountMonth>0))
			AND l.Guid=@Guid

	) AS ReturnX ON
	ReturnX.LP = l.LP AND @WithReturnsMode= 1 AND ISNULL(@ShowLineTicketReliefByRelief,0) =0


	ORDER BY l.Lp

	DELETE FROM SLS_ReliefLinePom WHERE Guid =@Guid

	END

END	

INSERT INTO dbo.LPC_Log (ProcName, Duration, Created)
SELECT 'ADMIN_ReportDef_ReliefTicketPayments', CONVERT(varchar, DATEADD(ss, DATEDIFF(SS, @Time, GETDATE()) * 1, 0), 114) , GetDate()



--select * from #PomReliefLine2
--select * from #PomReliefLine
END

GO


