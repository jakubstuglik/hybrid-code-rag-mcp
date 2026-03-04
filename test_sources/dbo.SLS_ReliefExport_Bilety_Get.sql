SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
-----------------------------
-----------BILETY------------
-----------------------------

CREATE PROCEDURE [dbo].[SLS_ReliefExport_Bilety_Get]
--ALTER PROCEDURE [dbo].[SLS_ReliefExport_Bilety_Get]
(
    @ReportResultID INT,
    @Mode			TINYINT =0	--0 --tryb dopłat UM --1 --lista sprzedanych biletów 2 - Rozliczenie przewoźników wykaz biletów 3 - Export do VERITUM
)
AS
BEGIN

    DECLARE @S1Q1 TINYINT = 1;
    DECLARE @S1Q2 TINYINT = 1;
    DECLARE @S1Q3 TINYINT = 1;
    DECLARE @S1Q4 TINYINT = 1;
    DECLARE @S2Q1 TINYINT = 1;
    DECLARE @S2Q2 TINYINT = 1;
    DECLARE @S2Q3 TINYINT = 1;

    DECLARE @Ticket_ID INT = NULL;

    SET NOCOUNT ON

    DECLARE @ReportResultExportDataID INT
    DECLARE @XmlParams XML

    SELECT	@ReportResultExportDataID = ID,
              @XmlParams			= XMLParams
    FROM dbo.ADMIN_ReportResultExportData WITH (NOLOCK) WHERE ReportResult_ID = @ReportResultID

    DECLARE @RODO INT = 0
	DECLARE @LineReplaceLineNumberEvidenceNumber TINYINT=0
    SELECT
        @RODO =	ref.value('RODO[1]', 'int'),
		@LineReplaceLineNumberEvidenceNumber =ref.value('LineReplaceLineNumberEvidenceNumber[1]', 'int')
    FROM @XmlParams.nodes('/Params') xmlData( ref )

    SET @RODO = ISNULL(@RODO,0)
	SET @LineReplaceLineNumberEvidenceNumber = ISNULL(@LineReplaceLineNumberEvidenceNumber,0)

    DECLARE @Sql VARCHAR(MAX) = ''

    CREATE TABLE #PomTicket (TicketId INT)

    SET @Sql = '
		INSERT INTO #PomTicket (TicketId)
		SELECT '+CASE WHEN ISNULL(@Mode,0) IN (0,2,4) THEN 'tr.id ' ELSE 't.ID ' END+
               'FROM dbo.SLS_Ticket t WITH (NOLOCK)'

    IF ISNULL(@Mode,0) IN (0,1,2,4)
        SET @Sql = @Sql + '
		INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.Ticket_ID = t.ID
		INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id '

    IF ISNULL(@Mode,0) =0
        SET @Sql = @Sql + '
		INNER JOIN dbo.ADMIN_ReportResultXTicketRoute rr WITH (NOLOCK) ON tr.id =rr.TicketRoute_ID
		WHERE rr.ReportResultExportData_ID='+CAST(@ReportResultExportDataID AS VARCHAR)
    IF ISNULL(@Mode,0) =1
        SET @Sql = @Sql + '
		INNER JOIN dbo.ADMIN_ReportResultXTicket tt WITH (NOLOCK) ON t.id = tt.Ticket_ID
		WHERE tt.ReportResult_ID ='+CAST(@ReportResultID AS VARCHAR)
    IF ISNULL(@Mode,0) IN (2,4)
        SET @Sql = @Sql + '
		INNER JOIN dbo.ADMIN_ReportResultXTicket tx WITH (NOLOCK) ON tx.Ticket_ID = tr.ID
		WHERE tx.ReportResult_ID ='+CAST(@ReportResultID AS VARCHAR)

    IF ISNULL(@Mode,0) IN (3)
        SET @Sql = @Sql + '
		INNER JOIN dbo.ADMIN_ReportResultExportVeritum ev WITH (NOLOCK) ON ev.Ticket_ID = t.ID
		WHERE ev.ReportResult_ID ='+CAST(@ReportResultID AS VARCHAR)
    --+' and t.id = 38529'

    EXECUTE (@SQL)

    --print @SQL
    --select * from #PomTicket;

    SET NOCOUNT OFF

    -----------------------------------------------------------------------
    -----------------------------------------------------------------------
    --------------------------TRYB @MODE IN (1,3) ------------------------- Eksport do VERITUM/System-1 i mode=1 (lista - gdzie to jest w UX?)
    -----------------------------------------------------------------------
    -----------------------------------------------------------------------
    IF ISNULL(@Mode,0) IN (1,3)
        BEGIN
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                ISNULL(CAST(cr.INumberBranch AS VARCHAR),'')	AS ODDZKURSU,
                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS  DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS  GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                -- FIRMAP dla jednorazowych = FIRMAK
                rd.Inumber										AS   FIRMAP,
                rd.RideNumber									AS   NRKURSU,
                rd.RideVariant									AS   WARIANT,
                CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                CONVERT(VARCHAR(5),tr.DepartureTime,108)		AS   GODZODJ,
                CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                tr.BusStopNoFrom								AS   NRPP,
                tr.NameFrom										AS   NAZWAPP,
                tr.BusStopCodeFrom								AS   KODPP,
                tr.BusStopNoTo									AS   NRPD,
                tr.NameTo										AS   NAZWAPD,
                tr.BusStopCodeTo								AS   KODPD,
                rd.RideTypeCommunication_ID						AS   RODZKOM,
                CASE WHEN rd.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                CASE WHEN rd.OneWay=1 THEN 0 ELSE 1 END			AS   KIERWL,
                ''												AS   NRZAD,
                CASE WHEN ls.LineNumber IS NULL THEN rd.LineNumber ELSE
                    CASE WHEN ls.LineNumber LIKE N'%[^0123456789]%'
                             THEN
                             CASE WHEN r.Line_ID IS NULL THEN ''
                                  ELSE CAST(r.Line_ID AS NVARCHAR(10))
                                 END
                         ELSE
                             CASE WHEN ISNUMERIC(ls.LineNumber) =1 THEN rd.LineNumber
                                  ELSE
                                      CASE WHEN r.Line_ID IS NULL THEN ''
                                           ELSE CAST(r.Line_ID AS NVARCHAR(10))
                                          END
                                 END
                        END
                    END
																AS   NRLINII,
				''												AS	 NRLINIIEWID,																		
                rd.LineVariant									AS   WARLINII,
                rd.LineType_ID									AS   LINIAKM,
                -- JS Dla Veritum Gorzow prosil zeby jak jest internet to zeby bylo puste T33342. W kolejnym mailu miało być to samo co jest w FIRMASP
                -- i to tutaj ustawiam
                case WHEN ISNULL(@Mode,0) = 3 and d.IDNumber = 3005 THEN spr.INumber ELSE d.IDNumber END	AS NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE
                    CASE WHEN t.TicketType_ID in (1,17) THEN 1
                         WHEN t.TicketType_ID >= 9 THEN 9
                         ELSE t.TicketType_ID
                        END
                    END AS TYPBILETU,

                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),tr.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),tr.ArrivalTime,108) ELSE '99:99' END AS GODZKON,
                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,
                ABS(tr.NormalPrice)/100.00						AS   CENABIL1,
                ISNULL(tr.DiscountCharge,0)/100.00				AS   KWOTABON1,
                ABS(tr.ReductionValue)/100.00					AS   KWOTAUL1,
                tr.AdditionalFeeCharge/100.00					AS   KWOTAOM1,
                CASE tr.VatCode	WHEN 'A' THEN 1
                                   WHEN 'B' THEN 2
                                   WHEN 'C' THEN 3
                                   WHEN 'D' THEN 4
                                   WHEN 'E' THEN 5
                                   WHEN 'F' THEN 6
                                   WHEN 'G' THEN 7
                                   WHEN 'N' THEN 8
                                   ELSE 0 END											AS   NRSTPTU1,
                tr.VatAmount/100									AS   STPTU1,

                tr.Price/100.00									AS BRUTPTU1,

                ABS(tr.NormalPriceAbroad)/100.00				AS   CENABIL2,
                tr.DiscountChargeAbroad/100.00					AS   KWOTABON2,
                ABS(tr.ReductionValueAbroad)/100.00				AS   KWOTAUL2,
                tr.AdditionalFeeChargeAbroad/100.00				AS   KWOTAOM2,
                CASE tr.VatCodeAbroad	WHEN 'A' THEN 1
                                         WHEN 'B' THEN 2
                                         WHEN 'C' THEN 3
                                         WHEN 'D' THEN 4
                                         WHEN 'E' THEN 5
                                         WHEN 'F' THEN 6
                                         WHEN 'G' THEN 7
                                         WHEN 'N' THEN 8
                                         ELSE 0 END										AS   NRSTPTU2,
                tr.VatAmountAbroad/100							AS   STPTU2,
                tr.PriceAbroad/100.00							AS   BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(tr.ReductionValue + ISNULL(tr.ReductionValueAbroad,0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,
                (tr.Price + ISNULL(tr.PriceAbroad,0))/100.0		AS   WARTBIL,

                tr.AmountToPay/100.00							AS   DOZAPL,
                CASE
                    WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                    WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                    WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                    END                                             AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                tr.PriceRate									AS   MNOZNIK,
                1												AS   MNUDZPRZ,		--DO ZWERYFIKOWANIA
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                srCanc.ReportNumber								AS   NRRAPZADA,
                'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS   IDENTRZA,
                CAST(sm.SUMRoadDistance/1000.0 AS DECIMAL(10,1))	AS   KMBIL,			--SUMARYCZNA DLA CAŁEGO BILETU
                CAST(tr.RoadDistance/1000.0 AS DECIMAL(10,1))		AS   KMKBIL,		--DLA KURSU
                dbo.TT_GetRideDesignation_Tags (r.id,' ',0)		AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                --ROW_NUMBER() OVER(PARTITION BY t.ID, tr.RouteNumber ORDER BY tr.RelationNumber)	AS   LPKURSUB,
                DENSE_RANK() OVER(PARTITION BY t.ID, tr.RouteNumber ORDER BY tr.RelationNumber)	AS   LPKURSUB,

                xc.CompanyCnt									AS   LPRZEWB,
                DENSE_RANK() OVER(PARTITION BY tr.Ticket_ID, rd.Inumber ORDER BY rd.Inumber)	AS   LPPRZEWB,
                tr.RouteNumber									AS   NRTRASY,
                tr.RelationNumber								AS   RELBIL,
                CASE WHEN type.GroupType=2 THEN CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR) ELSE '' END AS DNIRELBM,
                ec.INumber										AS   FIRMAKM,
                e.CardNumber									AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                tr.NameFrom +'-'+tr.NameTo						AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                rd.INumber										AS   FIRMAK,
                CAST(rd.RideNumber AS VARCHAR(4))				AS   NRKURSU_E,	--?
                CASE WHEN spr.INumber = rd.INumber THEN 0 ELSE 1 END AS KOBCE,
                CONVERT(VARCHAR(10),rd.RideDate, 120)			AS   DATAKURSU,	--??
                CONVERT(VARCHAR(5),rd.RideStopTime, 108)		AS   GODZPRZYJ, --??
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                ISNULL(f.Name,f2.Name)							AS   ZBIORA,
                CAST(ISNULL(RideDistanceToEndStop,0)/1000.0	AS DECIMAL(10,1)) AS   KMKURSU,
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CASE WHEN ISNULL(@Mode,0) =1 THEN CAST(ISNULL(tr.SkipInDoplaty,0) AS BIT) ELSE CAST(0 AS BIT) END AS POMINDOPL,
                CONVERT(VARCHAR(5),rd.RideStartTime, 108)		AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,
                ISNULL(CONVERT(VARCHAR(10),rd.RideValidFrom, 120),CONVERT(VARCHAR(10),r.ValidFrom, 120))		AS	 KURSWO,

                ISNULL(RTRIM(LTRIM(CASE WHEN CHARINDEX('-',ln.LineName)>2
                                            THEN LEFT(LEFT(ln.LineName,CHARINDEX('-',ln.LineName)-1),30)
                                        ELSE LEFT(ln.LineName,30) END)), rd.LineFirstBusStopName)								AS LINIAPP,

                ISNULL(RTRIM(LTRIM(CASE WHEN CHARINDEX('-',ln.LineName)>2
                                            THEN LEFT(RIGHT(ln.LineName,LEN(ln.LineName)-CHARINDEX('-',ln.LineName)),80)
                                        ELSE CASE WHEN LEN(ln.LineName) <=80 THEN ' ' ELSE LEFT(RIGHT(ln.LineName,LEN(ln.LineName)-30),80) END END)), rd.LineLastBusStopName) AS LINIAOP,

                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.Ticket_ID = t.ID

                     INNER JOIN #PomTicket pt ON pt.TicketId =t.id

                     INNER JOIN dbo.SLS_RideRegistered rd WITH (NOLOCK)  On rd.id = tr.RideRegistered_ID

                     INNER JOIN
                 (	SELECT SUM(RoadDistance) AS SUMRoadDistance, COUNT(*) AS SUMTicketRoute, Ticket_ID FROM dbo.SLS_TicketRoute tr  WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) sm ON sm.Ticket_ID = t.ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.TT_Ride r WITH (NOLOCK) ON r.id = rd.Ride_ID
                     LEFT JOIN dbo.ADMIN_Company cr WITH (NOLOCK) ON r.CompanyBranch_ID = cr.id AND cr.CompanyMaster_ID IS NULL

                     LEFT JOIN (	SELECT MAX(l.Name) AS LineName, l.Id AS LineId
                                    FROM TT_Line l WITH (NOLOCK)
                                    GROUP BY ID
            ) Ln ON ln.LineId = r.Line_ID

                     LEFT JOIN
                 ( SELECT DISTINCT LineName, LineShortName, LineNumber, LineVariant, LineValidFrom, LineType_ID
                   FROM dbo.ADMIN_ReportResultXLineSum ls WITH (NOLOCK)
                   WHERE ls.ReportResultExportData_ID = @ReportResultExportDataID
                 ) ls ON rd.LineNumber = ls.LineNumber AND ls.LineVariant = rd.LineVariant AND ls.LineType_ID = rd.LineType_ID

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc WITH (NOLOCK) ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     LEFT JOIN
                 (
                     SELECT a.Ride_ID, f.Name
                     FROM
                         (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                              FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                              WHERE f.FileType_ID=2
                              GROUP BY Ride_ID
                         ) a
                             INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID
                 ) f2 ON f2.Ride_ID = r.id

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (	SELECT COUNT(*) AS CompanyCnt, Ticket_ID
                      FROM dbo.SLS_TicketXCompany WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) xc ON t.id = xc.Ticket_ID
            WHERE
                (
                    (
                        IsNull(@Mode,0)=3 and
                        ((tr.RelationNumber=0 and t.TicketType_ID>1) or (t.TicketType_ID=1) or t.TicketType_ID = 17)
                        )
                        or (IsNull(@Mode,0)<>3)
                    ) AND @S1Q1 = 1

              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)
            UNION ALL
--- PODSUMOWANIE BILETÓW MISIĘCZNYCH WEDŁUG PRZEWOŹNIKA (to jest dodawane tylko w mode=1 (co to jest - do ustalenia))
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                ISNULL(CAST(rcrn1.INumberBranch AS VARCHAR),ISNULL(rcrn2.INumberBranch, ''))	AS ODDZKURSU,
                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS	DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS	GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                0												AS   FIRMAP,
                0												AS   NRKURSU,
                ''												AS   WARIANT,
                CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                ''												AS   GODZODJ,
                CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                0												AS   NRPP,
                ''												AS   NAZWAPP,
                0												AS   KODPP,
                0												AS   NRPD,
                ''												AS   NAZWAPD,
                0												AS   KODPD,
                ''												AS   RODZKOM,
                CASE WHEN sm.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                0												AS   KIERWL,
                ''												AS   NRZAD,
                ''												AS   NRLINII,
				''												AS	 NRLINIIEWID,
                0												AS   WARLINII,
                0												AS   LINIAKM,
                d.IDNumber										AS   NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE t.TicketType_ID END AS TYPBILETU,
                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,

                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.ArrivalTime,108) ELSE '99:99' END AS GODZKON,

                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,
                --XXX
                ABS(xc.PriceNormal)/100.00						AS   CENABIL1,
                t.DiscountCharge/100.00							AS   KWOTABON1,
                ABS(xc.ReductionValue)/100.00					AS   KWOTAUL1,
                t.AdditionalFeeCharge/100.00					AS   KWOTAOM1,
                CASE t.VatCode	WHEN 'A' THEN 1
                                  WHEN 'B' THEN 2
                                  WHEN 'C' THEN 3
                                  WHEN 'D' THEN 4
                                  WHEN 'E' THEN 5
                                  WHEN 'F' THEN 6
                                  WHEN 'G' THEN 7
                                  WHEN 'N' THEN 8
                                  ELSE 0 END										AS   NRSTPTU1,
                t.VatAmount/100									AS   STPTU1,

                xc.Price/100.00									AS BRUTPTU1,
                xc.PriceNormalAbroad/100.00						AS   CENABIL2,
                t.DiscountChargeAbroad/100.00					AS   KWOTABON2,
                ABS(xc.ReductionValueAbroad)/100.00				AS   KWOTAUL2,
                t.AdditionalFeeChargeAbroad/100.00				AS   KWOTAOM2,
                CASE t.VatCodeAbroad WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2
                                     WHEN 'C' THEN 3
                                     WHEN 'D' THEN 4
                                     WHEN 'E' THEN 5
                                     WHEN 'F' THEN 6
                                     WHEN 'G' THEN 7
                                     WHEN 'N' THEN 8
                                     ELSE 0 END										AS   NRSTPTU2,
                t.VatAmountAbroad/100							AS   STPTU2,

                xc.PriceAbroad/100.00							AS   BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(xc.ReductionValue +ISNULL(xc.ReductionValueAbroad,0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,
                (xc.Price + ISNULL(xc.PriceAbroad,0))/100.0		AS   WARTBIL,
                xc.Price/100.00									AS   DOZAPL,
                CASE
                    WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                    WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                    WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                    END                                             AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                1												AS   MNOZNIK,
                xc.PriceRate									AS   MNUDZPRZ,
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                srCanc.ReportNumber								AS   NRRAPZADA,
                'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS   IDENTRZA,
                CAST(smAll.SUMRoadDistance/1000.0 AS DECIMAL(10,1))	AS   KMBIL,		--SUMARYCZNA DLA CAŁEGO BILETU
                0												AS   KMKBIL,		--DLA KURSU
                ''												AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                0												AS   LPKURSUB,		--DO ZWERYFIKOWANIA
                xc.CompanyCnt									AS   LPRZEWB,
                DENSE_RANK() OVER(PARTITION BY t.ID, pr.Inumber ORDER BY pr.Inumber)	AS   LPPRZEWB,
                1												AS   NRTRASY,		-- ??
                0												AS   RELBIL,
                DNIRELBM										AS	 DNIRELBM,
                ec.INumber										AS   FIRMAKM,
                e.CardNumber									AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                'Bilet miesięczny'								AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                pr.INumber										AS   FIRMAK, --w eksporcie do Veritum usupełniamy FIRMAK, ale nie eksportujemy rekordów relacji biletów okresowych
                ''												AS   NRKURSU_E,	--?
                CASE WHEN spr.INumber = pr.INumber THEN 0 ELSE 1 END AS   KOBCE,
                CONVERT(VARCHAR(10),sm.SUMRideDate, 120)		AS   DATAKURSU,	--??
                ''												AS   GODZPRZYJ,
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                ISNULL(f.Name, sm.FileName)						AS   ZBIORA,
                0												AS   KMKURSU,		--?? BRAK
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CAST(0 AS BIT)									AS	POMINDOPL,
                ''												AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,

                NULL											AS   KURSWO,
                ''												AS   LINIAPP,
                ''												AS	 LINIAOP,
                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN
                 (	SELECT SUM(tr.RoadDistance) AS SUMRoadDistance, MAX(rr.RideDate) AS SUMRideDate, COUNT(*) AS SUMTicketRoute,
                             MAX(CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR)) AS DNIRELBM,
                             MAX(rr.LineType_ID) AS LineType_ID,
                             tr.Ticket_ID, tr.Companyowner_id AS CompanyOwner_ID,

                             MAX(f2.Name) AS FileName,
                             MIN(tr.DepartureTime) AS DepartureTime,
                             MAX(tr.ArrivalTime) AS ArrivalTime,
                             MIN(CASE WHEN tr.RelationNumber = 1 and tr.RouteNumber = 1 THEN tr.Ride_ID ELSE null END) AS FirstRideId,
                             MIN(CASE WHEN tr.RelationNumber = 1 and tr.RouteNumber = 1 THEN tr.ID ELSE null END) AS FirstTRID

                      FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                               INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.id = tr.RideRegistered_ID
                               INNER JOIN #PomTicket pt WITH (NOLOCK) ON pt.TicketId =tr.Ticket_ID

                               LEFT JOIN
                           (
                               SELECT a.Ride_ID, f.Name
                               FROM
                                   (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                                        FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                                 INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                                        WHERE f.FileType_ID=2
                                        GROUP BY Ride_ID
                                   ) a
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID

                           ) f2 ON f2.Ride_ID = rr.Ride_id

                      GROUP BY tr.Ticket_ID, tr.CompanyOwner_ID
                 ) sm ON sm.Ticket_ID = t.ID
                     LEFT JOIN TT_Ride rrn1 on rrn1.id = sm.FirstRideId
                     LEFT JOIN ADMIN_Company rcrn1 on rcrn1.ID = rrn1.CompanyBranch_ID

                -- JS U Kubraka mozna sprzedac bilet tylko na powrot
                     LEFT JOIN SLS_TicketRoute trrn2 on trrn2.RouteNumber = 1 and trrn2.RelationNumber = 3 and sm.FirstRideId is null and trrn2.Ticket_ID = t.ID
                     LEFT JOIN TT_Ride rrn2 on rrn2.ID = trrn2.Ride_ID
                     LEFT JOIN ADMIN_Company rcrn2 on rcrn2.ID = rrn2.CompanyBranch_ID

                     INNER JOIN
                 (	SELECT SUM(RoadDistance) AS SUMRoadDistance, COUNT(*) AS SUMTicketRoute, Ticket_ID FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) smAll ON smAll.Ticket_ID = t.ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL
                     LEFT JOIN dbo.ADMIN_Company pr WITH (NOLOCK) ON pr.Id = sm.CompanyOwner_ID AND pr.CompanyMaster_ID IS NULL

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (
                     SELECT xc.Ticket_ID, xc.Company_ID,
                            SUM(ISNULL(xc.Price,0))											AS Price,
                            SUM(ISNULL(xc.Price,0)+ISNULL(xc.ReductionValue,0))				AS PriceNormal,
                            SUM(ABS(ISNULL(xc.ReductionValue,0)))							AS ReductionValue,
                            SUM(ISNULL(xc.PriceAbroad,0))									AS PriceAbroad,
                            SUM(ABS(ISNULL(xc.ReductionValueAbroad,0)))						AS ReductionValueAbroad,
                            SUM(ISNULL(xc.PriceAbroad,0)+ISNULL(xc.ReductionValueAbroad,0))	AS PriceNormalAbroad,
                            MAX(ISNULL(xc.PriceRate,0))										AS PriceRate,
                            COUNT(*)														AS CompanyCnt
                     FROM dbo.SLS_TicketXCompany xc WITH (NOLOCK)
                              INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id = xc.Ticket_ID
                              LEFT JOIN
                          (	SELECT DISTINCT tr.Ticket_ID, CompanyOwner_ID
                               FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                                        INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (2,4)

                               UNION ALL

                               SELECT DISTINCT tr.Ticket_ID, CompanyOwner_ID
                               FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                                        INNER JOIN #PomTicket pt WITH (NOLOCK) ON pt.TicketId = tr.Ticket_id AND ISNULL(@Mode,0) =3

                          ) p ON ISNULL(@Mode,0) IN (2,3,4) AND xc.Ticket_ID = p.Ticket_ID AND p.CompanyOwner_ID = xc.Company_ID

                     WHERE (ISNULL(@Mode,0) IN (2,3,4) AND p.Ticket_ID IS NOT NULL OR ISNULL(@Mode,0) IN (0,1))

                     GROUP BY xc.Ticket_ID, xc.Company_ID
                 ) xc ON xc.Company_ID = sm.CompanyOwner_ID AND xc.Ticket_ID = t.ID


            WHERE
                t.Id IN (
                    SELECT DISTINCT tr.Ticket_ID
                    FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                             INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (0,2,4)

                    UNION ALL

                    SELECT TicketId
                    FROM #PomTicket pt WHERE ISNULL(@Mode,0) =1)
              AND type.GroupType=2
              AND @S1Q2 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            UNION ALL
--- PODSUMOWANIE BILETÓW MISIĘCZNYCH (to jest dodawane w eksporcie dla Veritum (mode =3))
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                ISNULL(CAST(rcrn1.INumberBranch AS VARCHAR),ISNULL(rcrn2.INumberBranch, ''))	AS ODDZKURSU,
                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS	DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS	GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                0												AS   FIRMAP,
                0												AS   NRKURSU,
                ''												AS   WARIANT,
                CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                ''												AS   GODZODJ,
                CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                0												AS   NRPP,
                ''												AS   NAZWAPP,
                0												AS   KODPP,
                0												AS   NRPD,
                ''												AS   NAZWAPD,
                0												AS   KODPD,
                ''												AS   RODZKOM,
                CASE WHEN sm.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                0												AS   KIERWL,
                ''												AS   NRZAD,
                ''												AS   NRLINII,
				''												AS	 NRLINIIEWID,
                0												AS   WARLINII,
                0												AS   LINIAKM,
                d.IDNumber										AS   NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE t.TicketType_ID END AS TYPBILETU,
                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.ArrivalTime,108) ELSE '99:99' END AS GODZKON,
                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,

                --XXX
                ISNULL(tr.NormalPrice,t.NormalPrice)/100.00						AS   CENABIL1,
                ISNULL(tr.DiscountCharge,t.DiscountCharge)/100.00				AS   KWOTABON1,
                ABS(ISNULL(tr.ReductionValue,t.ReductionValue))/100.00			AS   KWOTAUL1,
                ISNULL(tr.AdditionalFeeCharge,t.AdditionalFeeCharge)/100.00		AS   KWOTAOM1,
                CASE t.VatCode	WHEN 'A' THEN 1
                                  WHEN 'B' THEN 2
                                  WHEN 'C' THEN 3
                                  WHEN 'D' THEN 4
                                  WHEN 'E' THEN 5
                                  WHEN 'F' THEN 6
                                  WHEN 'G' THEN 7
                                  WHEN 'N' THEN 8
                                  ELSE 0 END														AS   NRSTPTU1,
                t.VatAmount/100													AS   STPTU1,

                ISNULL(tr.Price,t.Price)/100.00					AS BRUTPTU1,

                ISNULL(tr.NormalPriceAbroad,t.NormalPriceAbroad)/100.00						AS   CENABIL2,
                ISNULL(tr.DiscountChargeAbroad,t.DiscountChargeAbroad)/100.00				AS   KWOTABON2,
                ABS(ISNULL(tr.ReductionValueAbroad,t.ReductionValueAbroad))/100.00			AS   KWOTAUL2,
                ISNULL(tr.AdditionalFeeChargeAbroad,t.AdditionalFeeChargeAbroad)/100.00 AS   KWOTAOM2,
                CASE t.VatCodeAbroad WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2
                                     WHEN 'C' THEN 3
                                     WHEN 'D' THEN 4
                                     WHEN 'E' THEN 5
                                     WHEN 'F' THEN 6
                                     WHEN 'G' THEN 7
                                     WHEN 'N' THEN 8
                                     ELSE 0 END										AS   NRSTPTU2,
                t.VatAmountAbroad/100							AS   STPTU2,

                ISNULL(tr.PriceAbroad,t.PriceAbroad)/100.00		AS  BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(ISNULL(tr.ReductionValue,t.ReductionValue) +ISNULL(ISNULL(tr.ReductionValueAbroad,t.ReductionValueAbroad),0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,

                (ISNULL(tr.Price,t.Price) + ISNULL(tr.PriceAbroad, ISNULL(tr.PriceAbroad,0)))/100.0 AS   WARTBIL,
                ISNULL(tr.AmountToPay,t.AmountToPay)/100.00		AS   DOZAPL,
                CASE
                    WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                    WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                    WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                    END                                             AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                1												AS   MNOZNIK,		--ile jest tras kursów/wszystko
                1												AS   MNUDZPRZ,		--DO ZWERYFIKOWANIA
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                srCanc.ReportNumber								AS   NRRAPZADA,
                'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS  IDENTRZA,
                CAST(sm.SUMRoadDistance/1000.0 AS DECIMAL(10,1)) AS	 KMBIL,			--SUMARYCZNA DLA CAŁEGO BILETU
                0												AS   KMKBIL,		--DLA KURSU
                ''												AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                0												AS   LPKURSUB,		--DO ZWERYFIKOWANIA
                xc.CompanyCnt									AS   LPRZEWB,
                0												AS   LPPRZEWB,
                1												AS   NRTRASY,		-- ??
                0												AS   RELBIL,
                DNIRELBM										AS	 DNIRELBM,
                ec.INumber										AS   FIRMAKM,
                e.CardNumber									AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                'Bilet miesięczny'								AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                pr.INumber										AS   FIRMAK, --w eksporcie do Veritum usupełniamy FIRMAK, ale nie eksportujemy rekordów relacji biletów okresowych
                ''												AS   NRKURSU_E,	--?
                CASE WHEN spr.INumber = pr.INumber THEN 0 ELSE 1 END AS   KOBCE,
                CONVERT(VARCHAR(10),sm.SUMRideDate, 120)		AS   DATAKURSU,	--??
                ''												AS   GODZPRZYJ,
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                ISNULL(f.Name, sm.FileName)						AS   ZBIORA,
                0												AS   KMKURSU,		--?? BRAK
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CAST(0 AS BIT)									AS	POMINDOPL,
                ''												AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,

                NULL											AS	 KURSWO,
                ''												AS   LINIAPP,
                ''												AS	 LINIAOP,
                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN
                 (	SELECT SUM(tr.RoadDistance) AS SUMRoadDistance, MAX(rr.RideDate) AS SUMRideDate, COUNT(*) AS SUMTicketRoute,
                             MAX(CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR)) AS DNIRELBM,
                             MAX(rr.LineType_ID) AS LineType_ID, tr.Ticket_ID, MAX(tr.Companyowner_id) AS CompanyOwner_ID,
                             MAX(f2.Name) AS FileName,
                             MIN(tr.DepartureTime) AS DepartureTime,
                             MAX(tr.ArrivalTime) AS ArrivalTime,
                             MIN(CASE WHEN tr.RelationNumber = 1 and tr.RouteNumber = 1 THEN tr.Ride_ID ELSE null END) AS FirstRideId,
                             MIN(CASE WHEN tr.RelationNumber = 1 and tr.RouteNumber = 1 THEN tr.ID ELSE null END) AS FirstTRID

                      FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                               INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.id = tr.RideRegistered_ID

                               LEFT JOIN
                           (
                               SELECT a.Ride_ID, f.Name
                               FROM
                                   (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                                        FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                                 INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                                        WHERE f.FileType_ID=2
                                        GROUP BY Ride_ID
                                   ) a
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID

                           ) f2 ON f2.Ride_ID = rr.Ride_id

                      GROUP BY tr.Ticket_ID
                 ) sm ON sm.Ticket_ID = t.ID
                     LEFT JOIN TT_Ride rrn1 on rrn1.id = sm.FirstRideId
                     LEFT JOIN ADMIN_Company rcrn1 on rcrn1.ID = rrn1.CompanyBranch_ID

                -- JS U Kubraka mozna sprzedac bilet tylko na powrot
                     LEFT JOIN SLS_TicketRoute trrn2 on trrn2.RouteNumber = 1 and trrn2.RelationNumber = 3 and sm.FirstRideId is null and trrn2.Ticket_ID = t.ID
                     LEFT JOIN TT_Ride rrn2 on rrn2.ID = trrn2.Ride_ID
                     LEFT JOIN ADMIN_Company rcrn2 on rcrn2.ID = rrn2.CompanyBranch_ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL
                     LEFT JOIN dbo.ADMIN_Company pr WITH (NOLOCK) ON pr.Id = sm.CompanyOwner_ID AND pr.CompanyMaster_ID IS NULL

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc WITH (NOLOCK) ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (
                     SELECT Ticket_ID, COUNT(*) AS CompanyCnt
                     FROM dbo.SLS_TicketXCompany xc WITH (NOLOCK)
                     GROUP BY Ticket_ID
                 ) xc ON xc.Ticket_ID = t.ID

                     LEFT JOIN
                 (
                     SELECT tr.Ticket_ID,
                            SUM(ISNULL(tr.Price,0))									AS Price,
                            SUM(ISNULL(tr.NormalPrice,0))							AS NormalPrice,
                            SUM(ISNULL(tr.ReductionValue,0))						AS ReductionValue,
                            SUM(ISNULL(tr.PriceAbroad,0))							AS PriceAbroad,
                            SUM(ISNULL(tr.ReductionValueAbroad,0))					AS ReductionValueAbroad,
                            SUM(ISNULL(tr.NormalPriceAbroad,0))						AS NormalPriceAbroad,
                            SUM(ISNULL(tr.PriceRate,0))								AS PriceRate,
                            SUM(ISNULL(DiscountCharge,0))							AS DiscountCharge,
                            SUM(ISNULL(DiscountChargeAbroad,0))						AS DiscountChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeChargeAbroad,0))				AS AdditionalFeeChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeCharge,0))					AS AdditionalFeeCharge,
                            SUM(ISNULL(tr.AmountToPay,0))							AS AmountToPay,
                            COUNT(*)												AS CompanyCnt
                     FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                              INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) =2
                     GROUP BY tr.Ticket_ID

                     UNION ALL

                     SELECT tr.Ticket_ID,
                            SUM(ISNULL(tr.Price,0))									AS Price,
                            SUM(ISNULL(tr.NormalPrice,0))							AS NormalPrice,
                            SUM(ISNULL(tr.ReductionValue,0))						AS ReductionValue,
                            SUM(ISNULL(tr.PriceAbroad,0))							AS PriceAbroad,
                            SUM(ISNULL(tr.ReductionValueAbroad,0))					AS ReductionValueAbroad,
                            SUM(ISNULL(tr.NormalPriceAbroad,0))						AS NormalPriceAbroad,
                            SUM(ISNULL(tr.PriceRate,0))								AS PriceRate,
                            SUM(ISNULL(DiscountCharge,0))							AS DiscountCharge,
                            SUM(ISNULL(DiscountChargeAbroad,0))						AS DiscountChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeChargeAbroad,0))				AS AdditionalFeeChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeCharge,0))					AS AdditionalFeeCharge,
                            SUM(ISNULL(tr.AmountToPay,0))							AS AmountToPay,
                            COUNT(*)												AS CompanyCnt
                     FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                              INNER JOIN #PomTicket pt ON pt.TicketId = tr.Ticket_ID AND ISNULL(@Mode,0) =3

                     GROUP BY tr.Ticket_ID
                 ) tr ON tr.Ticket_ID = t.ID AND ISNULL(@Mode,0) IN (2,4)


            WHERE
                t.Id IN (

                    SELECT DISTINCT tr.Ticket_ID
                    FROM dbo.SLS_TicketRoute tr  WITH (NOLOCK)
                             INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (0,2,4)

                    UNION ALL

                    SELECT TicketId
                    FROM #PomTicket pt WHERE ISNULL(@Mode,0) IN (1,3)

                )
              AND type.GroupType=2 AND type.ID not in (8)
              AND @S1Q3 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            UNION ALL
--- PODSUMOWANIE NIE-BILETÓW
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                -- JS Przepisanie ODDZSPRZED do ODDZKURSU - T33342
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')   AS ODDZKURSU,

                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS	DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS	GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                0												AS   FIRMAP,
                0												AS   NRKURSU,
                ''												AS   WARIANT,
                ''												AS   BWAZNYOD,
                ''												AS   GODZODJ,
                ''												AS   BWAZNYDO,
                0												AS   NRPP,
                ''												AS   NAZWAPP,
                0												AS   KODPP,
                0												AS   NRPD,
                ''												AS   NAZWAPD,
                0												AS   KODPD,
                ''												AS   RODZKOM,
                1												AS   KRAJ,
                0												AS   KIERWL,
                ''												AS   NRZAD,
                ''												AS   NRLINII,
				''												AS	 NRLINIIEWID,
                0												AS   WARLINII,
                0												AS   LINIAKM,
                d.IDNumber										AS   NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS   TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS   MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS   MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE
                    WHEN t.TicketType_ID = 17 THEN 1 -- jednorazowe miejskie jako jednorazowe
                    WHEN t.TicketType_ID >= 9 and t.TicketType_ID <> 17 THEN 9 -- reszta jako 9, bez jednorazowych miejskich
                    ELSE t.TicketType_ID
                    END												AS TYPBILETU,
                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,
                '99:99'											AS GODZPOCZ,
                '99:99'											AS GODZKON,
                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,

                --XXX
                t.NormalPrice/100.0								AS   CENABIL1,
                t.DiscountCharge/100.0							AS   KWOTABON1,
                ABS(t.ReductionValue)/100.0						AS   KWOTAUL1,
                t.AdditionalFeeCharge/100.0						AS   KWOTAOM1,
                CASE tg.VatCode	WHEN 'A' THEN 1
                                   WHEN 'B' THEN 2
                                   WHEN 'C' THEN 3
                                   WHEN 'D' THEN 4
                                   WHEN 'E' THEN 5
                                   WHEN 'F' THEN 6
                                   WHEN 'G' THEN 7
                                   WHEN 'N' THEN 8
                                   ELSE 0 END										AS   NRSTPTU1,
                tg.VatAmount/100									AS   STPTU1,
                ISNULL(tg.Price, t.Price)/100.00					AS   BRUTPTU1,
                t.NormalPriceAbroad/100.00						AS   CENABIL2,
                t.DiscountChargeAbroad/100.00					AS   KWOTABON2,
                ABS(t.ReductionValueAbroad)/100.00				AS   KWOTAUL2,
                t.AdditionalFeeChargeAbroad/100.00				AS   KWOTAOM2,
                CASE t.VatCodeAbroad WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2
                                     WHEN 'C' THEN 3
                                     WHEN 'D' THEN 4
                                     WHEN 'E' THEN 5
                                     WHEN 'F' THEN 6
                                     WHEN 'G' THEN 7
                                     WHEN 'N' THEN 8
                                     ELSE 0 END										AS   NRSTPTU2,
                t.VatAmountAbroad/100							AS   STPTU2,

                t.PriceAbroad/100.00							AS  BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(t.ReductionValue +ISNULL(t.ReductionValueAbroad ,0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,

                t.Price/100.0									AS   WARTBIL,
                t.AmountToPay/100.00							AS   DOZAPL,
                t.PaymentType_ID				                AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                1												AS   MNOZNIK,		--ile jest tras kursów/wszystko
                1												AS   MNUDZPRZ,		--DO ZWERYFIKOWANIA
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                ''												AS DATAANUL,
                ''												AS   NRKASJA,
                ''												AS   NRRAPZADA,
                ''												AS  IDENTRZA,
                0												AS	 KMBIL,			--SUMARYCZNA DLA CAŁEGO BILETU
                0												AS   KMKBIL,		--DLA KURSU
                ''												AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                0												AS   LKURSOWB,		-- LICZBA REK TicketRoute
                0												AS   LPKURSUB,		--DO ZWERYFIKOWANIA
                0												AS   LPRZEWB,
                0												AS   LPPRZEWB,
                ''												AS   NRTRASY,		-- ??
                0												AS   RELBIL,
                0												AS	 DNIRELBM,
                0												AS   FIRMAKM,
                0												AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                'Inne'											AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                ''												AS   KODKBIL,		--??
                0												AS   FIRMAK,
                ''												AS   NRKURSU_E,	--?
                0												AS   KOBCE,		--??
                ''												AS   DATAKURSU,	--??
                ''												AS   GODZPRZYJ,
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                f.Name											AS   ZBIORA,
                0												AS   KMKURSU,		--?? BRAK
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CAST(0 AS BIT)									AS	POMINDOPL,
                ''												AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,

                NULL											AS	 KURSWO,
                ''												AS   LINIAPP,
                ''												AS	 LINIAOP,
                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN #PomTicket pt on pt.TicketId = t.id
                     LEFT JOIN SLS_TicketGoods tg on tg.Ticket_ID = t.id

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

            WHERE (type.GroupType is null or type.GroupType not in (1,2))
              AND ISNULL(@Mode,0) =3
              AND @S1Q4 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            ORDER BY t.TicketNumberBM ASC, FIRMAP ASC , NRTRASY ASC, LPKURSUB ASC

        END

    ELSE

        BEGIN
            -----------------------------------------------------------------------
            -----------------------------------------------------------------------
            --------------------------TRYB @MODE IN (0,2,4) ------------------------- PLIK DO I DOPŁATY, 4 - ???
            -----------------------------------------------------------------------
            -----------------------------------------------------------------------

            SELECT DISTINCT -- bilety jednorazowe i trasy biletów okresowych (rekordy 3)
                            t.id											AS TICKET_ID,
                            rt.MiejsceSprz									AS MIEJSCESPRZ,
                            ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                            ISNULL(CAST(cr.INumberBranch AS VARCHAR),'')	AS ODDZKURSU,


                            CONVERT(VARCHAR(10),t.SaleDate, 120)			AS  DATASPRZ,
                            CONVERT(VARCHAR(8),t.SaleDate,108)				AS  GODZSPRZ,
                            spr.INumber										AS   FIRMASP,
                            rd.Inumber										AS   FIRMAP,
                            rd.RideNumber									AS   NRKURSU,
                            rd.RideVariant									AS   WARIANT,
                            CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                            CONVERT(VARCHAR(5),tr.DepartureTime,108)		AS   GODZODJ,
                            CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                            tr.BusStopNoFrom								AS   NRPP,
                            tr.NameFrom										AS   NAZWAPP,
                            tr.BusStopCodeFrom								AS   KODPP,
                            tr.BusStopNoTo									AS   NRPD,
                            tr.NameTo										AS   NAZWAPD,
                            tr.BusStopCodeTo								AS   KODPD,
                            rd.RideTypeCommunication_ID						AS   RODZKOM,
                            CASE WHEN rd.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                            CASE WHEN rd.OneWay=1 THEN 0 ELSE 1 END			AS   KIERWL,
                            ''												AS   NRZAD,
                            CASE WHEN ls.LineNumber IS NULL THEN rd.LineNumber ELSE
                                CASE WHEN ls.LineNumber LIKE N'%[^0123456789]%'
                                         THEN
                                         CASE WHEN r.Line_ID IS NULL THEN ''
                                              ELSE CAST(r.Line_ID AS NVARCHAR(10))
                                             END
                                     ELSE
                                         CASE WHEN ISNUMERIC(ls.LineNumber) =1 THEN rd.LineNumber
                                              ELSE
                                                  CASE WHEN r.Line_ID IS NULL THEN ''
                                                       ELSE CAST(r.Line_ID AS NVARCHAR(10))
                                                      END
                                             END
                                    END
                                END
																			AS   NRLINII,
							LnPermission.LineNumberGov						AS   NRLINIIEWID,  -- Nr ewidencyjny linii obsługiwany przez JSON
                            rd.LineVariant									AS   WARLINII,
                            rd.LineType_ID									AS   LINIAKM,
                            d.IDNumber										AS   NRKIER,
                            CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                            CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                            0												AS   NRKP,			--nie używamy tego
                            fr.FiscalLogo									AS   LOGO,
                            fr.ReportNumber									AS   NRRF,
                            sr.ReportNumber									AS   NRRZ,
                            1												AS   LPKIER,		--zawsze 1
                            sr.UserStationNumber							AS   NRSTAN,
                            CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                            'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                            rt.TypRz										AS TYPRZ,
                            CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                            CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                            t.TicketNumber									AS   NRKBIL,																		--???
                            t.PrintNumber									AS   NRDOK,
                            t.TicketNumberBM								AS   NRBILETU,
                            t.PassangerNumber								AS   LPAS,
                            CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE t.TicketType_ID END AS TYPBILETU,

                            t.TicketGenre_ID								AS   RODZBIL,
                            t.MonthTicketType								AS   RODZBM,
                            CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),tr.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                            CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),tr.ArrivalTime,108) ELSE '99:99' END AS GODZKON,
                            0												AS   ZAPISRK,
                            ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                            ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                            CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                                 ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                                           ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                            ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                            t.FarePriceReductionGroup_ID					AS   GRULGI,
                            t.ReductionNumber								AS   NRULGI,
                            t.ReductionName									AS   NAZULGI,
                            t.ReductionPercentage 							AS   STAWKAUL,
                            ABS(tr.NormalPrice)/100.00						AS   CENABIL1,
                            ISNULL(tr.DiscountCharge,0)/100.00				AS   KWOTABON1,
                            ABS(tr.ReductionValue)/100.00					AS   KWOTAUL1,
                            tr.AdditionalFeeCharge/100.00					AS   KWOTAOM1,
                            CASE tr.VatCode	WHEN 'A' THEN 1
                                               WHEN 'B' THEN 2
                                               WHEN 'C' THEN 3
                                               WHEN 'D' THEN 4
                                               WHEN 'E' THEN 5
                                               WHEN 'F' THEN 6
                                               WHEN 'G' THEN 7
                                               WHEN 'N' THEN 8
                                               ELSE 0 END											AS   NRSTPTU1,
                            tr.VatAmount/100									AS   STPTU1,

                            tr.Price/100.00									AS BRUTPTU1,

                            ABS(tr.NormalPriceAbroad)/100.00				AS   CENABIL2,
                            tr.DiscountChargeAbroad/100.00					AS   KWOTABON2,
                            ABS(tr.ReductionValueAbroad)/100.00				AS   KWOTAUL2,
                            tr.AdditionalFeeChargeAbroad/100.00				AS   KWOTAOM2,
                            CASE tr.VatCodeAbroad	WHEN 'A' THEN 1
                                                     WHEN 'B' THEN 2
                                                     WHEN 'C' THEN 3
                                                     WHEN 'D' THEN 4
                                                     WHEN 'E' THEN 5
                                                     WHEN 'F' THEN 6
                                                     WHEN 'G' THEN 7
                                                     WHEN 'N' THEN 8
                                                     ELSE 0 END										AS   NRSTPTU2,
                            tr.VatAmountAbroad/100							AS   STPTU2,
                            tr.PriceAbroad/100.00							AS   BRUTPTU2,
                            0												AS   NRSTPTUD,		--??
                            0												AS   STPTUD,
                            ABS(tr.ReductionValue + ISNULL(tr.ReductionValueAbroad,0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,
                            (tr.Price + ISNULL(tr.PriceAbroad,0))/100.0		AS   WARTBIL,

                            tr.AmountToPay/100.00							AS   DOZAPL,
                            CASE
                                WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                                WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                                WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                                END                                             AS   SPZAPL,
                            p.Name											AS   NAZSPZAPL,
                            t.Currency_ID-1									AS   WALUTA,
                            0												AS   SMB,
                            c.Symbol										AS   OZNWAL,
                            c.Unit											AS   JEDWAL,
                            1												AS   MNWAL,
                            tr.PriceRate									AS   MNOZNIK,
                            1												AS   MNUDZPRZ,		--DO ZWERYFIKOWANIA
                            t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                            CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                            ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                            srCanc.ReportNumber								AS   NRRAPZADA,
                            'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS   IDENTRZA,
                            CAST(sm.SUMRoadDistance/1000.0 AS DECIMAL(10,1))	AS   KMBIL,			--SUMARYCZNA DLA CAŁEGO BILETU
                            CAST(tr.RoadDistance/1000.0 AS DECIMAL(10,1))		AS   KMKBIL,		--DLA KURSU
                            dbo.TT_GetRideDesignation_Tags (r.id,' ',0)		AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                            sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                            --ROW_NUMBER() OVER(PARTITION BY t.ID, tr.RouteNumber ORDER BY tr.RelationNumber)	AS   LPKURSUB,
                            DENSE_RANK() OVER(PARTITION BY t.ID, tr.RouteNumber ORDER BY tr.RelationNumber)	AS   LPKURSUB,

                            xc.CompanyCnt									AS   LPRZEWB,
                            DENSE_RANK() OVER(PARTITION BY tr.Ticket_ID, rd.Inumber ORDER BY rd.Inumber)	AS   LPPRZEWB,
                            tr.RouteNumber									AS   NRTRASY,
                            tr.RelationNumber								AS   RELBIL,
                            CASE WHEN type.GroupType=2 THEN CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR) ELSE '' END AS DNIRELBM,
                            ec.INumber										AS   FIRMAKM,
                            e.CardNumber									AS   NRKARTYM,
                            t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                            CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                            CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                            dd.IDNumberHRSystem								AS   NRPAS,			--??
                            t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                            CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                            CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                            0												AS   LPRZBO,		--??
                            sr.ReportCode									AS   SZYFRBIL,		--??
                            tr.NameFrom +'-'+tr.NameTo						AS   RELACJAK,
                            0												AS   NRSTPROW,		--??
                            ''												AS   RODZSP,		--??
                            CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                            rd.INumber										AS   FIRMAK,
                            CAST(rd.RideNumber AS VARCHAR(4))				AS   NRKURSU_E,	--?
                            CASE WHEN spr.INumber = rd.INumber THEN 0 ELSE 1 END AS   KOBCE,
                            CONVERT(VARCHAR(10),rd.RideDate, 120)			AS   DATAKURSU,	--??
                            CONVERT(VARCHAR(5),rd.RideStopTime, 108)		AS   GODZPRZYJ, --??
                            0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                            ISNULL(f.Name,f2.Name)							AS   ZBIORA,
                            CAST(ISNULL(RideDistanceToEndStop,0)/1000.0	AS DECIMAL(10,1)) AS   KMKURSU,
                            CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                            CASE WHEN ISNULL(@Mode,0) =1 THEN CAST(ISNULL(tr.SkipInDoplaty,0) AS BIT) ELSE CAST(0 AS BIT) END AS POMINDOPL,
                            CONVERT(VARCHAR(5),rd.RideStartTime, 108)		AS   GODZODJK,		--?? BRAK
                            0												AS   NRFU,			---???????
                            t.BuyerNIP										AS   NIPNABYWCY,
                            CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                            CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                            u.IDNumber										AS   NR_SLUZBOP,
                            ISNULL(CONVERT(VARCHAR(10),rd.RideValidFrom, 120),CONVERT(VARCHAR(10),r.ValidFrom, 120))		AS	 KURSWO,

                            ISNULL(RTRIM(LTRIM(CASE WHEN CHARINDEX('-',ln.LineName)>2
                                                        THEN LEFT(LEFT(ln.LineName,CHARINDEX('-',ln.LineName)-1),30)
                                                    ELSE LEFT(ln.LineName,30) END)), rd.LineFirstBusStopName)								AS LINIAPP,

                            ISNULL(RTRIM(LTRIM(CASE WHEN CHARINDEX('-',ln.LineName)>2
                                                        THEN LEFT(RIGHT(ln.LineName,LEN(ln.LineName)-CHARINDEX('-',ln.LineName)),80)
                                                    ELSE CASE WHEN LEN(ln.LineName) <=80 THEN ' ' ELSE LEFT(RIGHT(ln.LineName,LEN(ln.LineName)-30),80) END END)), rd.LineLastBusStopName) AS LINIAOP,

                            0												AS	 DRIVERID,
                            ''												AS	 KODBIL,
                            t.QRCode										AS   QRCODE,
                            t.EPNumber										AS   EPNUMBER,
                            t.EPCode										AS   EPCODE

					FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN dbo.SLS_TicketRoute tr WITH (NOLOCK) ON tr.Ticket_ID = t.ID

                     INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID

                     INNER JOIN dbo.SLS_RideRegistered rd WITH (NOLOCK) On rd.id = tr.RideRegistered_ID

                     INNER JOIN
                 (	SELECT SUM(RoadDistance) AS SUMRoadDistance, COUNT(*) AS SUMTicketRoute, Ticket_ID FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) sm ON sm.Ticket_ID = t.ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.TT_Ride r WITH (NOLOCK) ON r.id = rd.Ride_ID
                     LEFT JOIN dbo.ADMIN_Company cr WITH (NOLOCK) ON r.CompanyBranch_ID = cr.id AND cr.CompanyMaster_ID IS NULL

                     LEFT JOIN (	SELECT MAX(l.Name) AS LineName, l.Id AS LineId
                                    FROM TT_Line l WITH (NOLOCK)
                                    GROUP BY ID
								) Ln ON ln.LineId = r.Line_ID
                     LEFT JOIN (	SELECT MAX(l.LineNumberGov) AS LineNumberGov, l.Line_ID AS LineId
                                    FROM TT_LinePermission l WITH (NOLOCK)
                                    GROUP BY Line_ID
								) LnPermission ON LnPermission.LineId = r.Line_ID
                     LEFT JOIN
					 ( SELECT DISTINCT LineName, LineShortName, LineNumber, LineVariant, LineValidFrom, LineType_ID
					   FROM dbo.ADMIN_ReportResultXLineSum ls WITH (NOLOCK)
					   WHERE ls.ReportResultExportData_ID = @ReportResultExportDataID
					 ) ls ON rd.LineNumber = ls.LineNumber AND ls.LineVariant = rd.LineVariant AND ls.LineType_ID = rd.LineType_ID

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc WITH (NOLOCK) ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     LEFT JOIN
                 (
                     SELECT a.Ride_ID, f.Name
                     FROM
                         (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                              FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                              WHERE f.FileType_ID=2
                              GROUP BY Ride_ID
                         ) a
                             INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID
                 ) f2 ON f2.Ride_ID = r.id

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (	SELECT COUNT(*) AS CompanyCnt, Ticket_ID
                      FROM dbo.SLS_TicketXCompany WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) xc ON t.id = xc.Ticket_ID
            WHERE (
                (
                    IsNull(@Mode,0)=3 and ((tr.RelationNumber=0 and t.TicketType_ID>1) or (t.TicketType_ID=1)) --tutaj jest mode=0,2,4, więc to nie jest nigdy wykonywane
                    ) or (IsNull(@Mode,0)<>3)
                )
              AND @S2Q1 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            UNION ALL
--- PODSUMOWANIE BILETÓW MIESIĘCZNYCH WEDŁUG PRZEWOŹNIKA (rekord 2 zawierający FIRMASP i FIRMAP)
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                ''												AS ODDZKURSU,
                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS	DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS	GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                pr.INumber										AS   FIRMAP,
                0												AS   NRKURSU,
                ''												AS   WARIANT,
                CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                ''												AS   GODZODJ,
                CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                0												AS   NRPP,
                ''												AS   NAZWAPP,
                0												AS   KODPP,
                0												AS   NRPD,
                ''												AS   NAZWAPD,
                0												AS   KODPD,
                ''												AS   RODZKOM,
                CASE WHEN sm.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                0												AS   KIERWL,
                ''												AS   NRZAD,
                ''												AS   NRLINII,
				''												AS	 NRLINIIEWID,
                0												AS   WARLINII,
                0												AS   LINIAKM,
                d.IDNumber										AS   NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE t.TicketType_ID END AS TYPBILETU,
                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,

                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.ArrivalTime,108) ELSE '99:99' END AS GODZKON,

                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,
                --XXX
                ABS(xc.PriceNormal)/100.00						AS   CENABIL1,
                t.DiscountCharge/100.00							AS   KWOTABON1,
                ABS(xc.ReductionValue)/100.00					AS   KWOTAUL1,
                t.AdditionalFeeCharge/100.00					AS   KWOTAOM1,
                CASE t.VatCode	WHEN 'A' THEN 1
                                  WHEN 'B' THEN 2
                                  WHEN 'C' THEN 3
                                  WHEN 'D' THEN 4
                                  WHEN 'E' THEN 5
                                  WHEN 'F' THEN 6
                                  WHEN 'G' THEN 7
                                  WHEN 'N' THEN 8
                                  ELSE 0 END										AS   NRSTPTU1,
                t.VatAmount/100									AS   STPTU1,

                xc.Price/100.00									AS BRUTPTU1,
                xc.PriceNormalAbroad/100.00						AS   CENABIL2,
                t.DiscountChargeAbroad/100.00					AS   KWOTABON2,
                ABS(xc.ReductionValueAbroad)/100.00				AS   KWOTAUL2,
                t.AdditionalFeeChargeAbroad/100.00				AS   KWOTAOM2,
                CASE t.VatCodeAbroad WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2
                                     WHEN 'C' THEN 3
                                     WHEN 'D' THEN 4
                                     WHEN 'E' THEN 5
                                     WHEN 'F' THEN 6
                                     WHEN 'G' THEN 7
                                     WHEN 'N' THEN 8
                                     ELSE 0 END										AS   NRSTPTU2,
                t.VatAmountAbroad/100							AS   STPTU2,

                xc.PriceAbroad/100.00							AS   BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(xc.ReductionValue +ISNULL(xc.ReductionValueAbroad,0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,
                (xc.Price + ISNULL(xc.PriceAbroad,0))/100.0		AS   WARTBIL,
                xc.Price/100.00									AS   DOZAPL,
                CASE
                    WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                    WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                    WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                    END                                             AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                1												AS   MNOZNIK,
                xc.PriceRate									AS   MNUDZPRZ,
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                srCanc.ReportNumber								AS   NRRAPZADA,
                'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS   IDENTRZA,
                CAST(smAll.SUMRoadDistance/1000.0 AS DECIMAL(10,1))	AS   KMBIL,		--SUMARYCZNA DLA CAŁEGO BILETU
                0												AS   KMKBIL,		--DLA KURSU
                ''												AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                0												AS   LPKURSUB,		--DO ZWERYFIKOWANIA
                xc.CompanyCnt									AS   LPRZEWB,
                DENSE_RANK() OVER(PARTITION BY t.ID, pr.Inumber ORDER BY pr.Inumber)	AS   LPPRZEWB,
                1												AS   NRTRASY,		-- ??
                0												AS   RELBIL,
                DNIRELBM										AS	 DNIRELBM,
                ec.INumber										AS   FIRMAKM,
                e.CardNumber									AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                'Bilet miesięczny'								AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                0												AS   FIRMAK,
                ''												AS   NRKURSU_E,	--?
                CASE WHEN spr.INumber = pr.INumber THEN 0 ELSE 1 END AS   KOBCE,
                CONVERT(VARCHAR(10),sm.SUMRideDate, 120)		AS   DATAKURSU,	--??
                ''												AS   GODZPRZYJ,
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                ISNULL(f.Name, sm.FileName)						AS   ZBIORA,
                0												AS   KMKURSU,		--?? BRAK
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CAST(0 AS BIT)									AS	POMINDOPL,
                ''												AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,

                NULL											AS   KURSWO,
                ''												AS   LINIAPP,
                ''												AS	 LINIAOP,
                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN
                 (	SELECT SUM(tr.RoadDistance) AS SUMRoadDistance, MAX(rr.RideDate) AS SUMRideDate, COUNT(*) AS SUMTicketRoute,
                             MAX(CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR)) AS DNIRELBM,
                             MAX(rr.LineType_ID) AS LineType_ID,
                             tr.Ticket_ID, tr.Companyowner_id AS CompanyOwner_ID,

                             MAX(f2.Name) AS FileName,
                             MIN(tr.DepartureTime) AS DepartureTime,
                             MAX(tr.ArrivalTime) AS ArrivalTime

                      FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                               INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.id = tr.RideRegistered_ID

                               INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID

                               LEFT JOIN
                           (
                               SELECT a.Ride_ID, f.Name
                               FROM
                                   (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                                        FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                                 INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                                        WHERE f.FileType_ID=2
                                        GROUP BY Ride_ID
                                   ) a
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID

                           ) f2 ON f2.Ride_ID = rr.Ride_id

                      GROUP BY tr.Ticket_ID, tr.CompanyOwner_ID
                 ) sm ON sm.Ticket_ID = t.ID

                     INNER JOIN
                 (	SELECT SUM(RoadDistance) AS SUMRoadDistance, COUNT(*) AS SUMTicketRoute, Ticket_ID FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                      GROUP BY Ticket_ID
                 ) smAll ON smAll.Ticket_ID = t.ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL
                     LEFT JOIN dbo.ADMIN_Company pr WITH (NOLOCK) ON pr.Id = sm.CompanyOwner_ID AND pr.CompanyMaster_ID IS NULL

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc WITH (NOLOCK) ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (
                     SELECT xc.Ticket_ID, xc.Company_ID,
                            SUM(ISNULL(xc.Price,0))											AS Price,
                            SUM(ISNULL(xc.Price,0)+ISNULL(xc.ReductionValue,0))				AS PriceNormal,
                            SUM(ABS(ISNULL(xc.ReductionValue,0)))							AS ReductionValue,
                            SUM(ISNULL(xc.PriceAbroad,0))									AS PriceAbroad,
                            SUM(ABS(ISNULL(xc.ReductionValueAbroad,0)))						AS ReductionValueAbroad,
                            SUM(ISNULL(xc.PriceAbroad,0)+ISNULL(xc.ReductionValueAbroad,0))	AS PriceNormalAbroad,
                            MAX(ISNULL(xc.PriceRate,0))										AS PriceRate,
                            COUNT(*)														AS CompanyCnt
                     FROM dbo.SLS_TicketXCompany xc WITH (NOLOCK)
                              INNER JOIN dbo.SLS_Ticket t WITH (NOLOCK) ON t.id = xc.Ticket_ID
                              LEFT JOIN
                          (	SELECT DISTINCT tr.Ticket_ID, CompanyOwner_ID
                               FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                                        INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (2,4)

                               UNION ALL

                               SELECT DISTINCT tr.Ticket_ID, CompanyOwner_ID
                               FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                                        INNER JOIN #PomTicket pt ON pt.TicketId = tr.Ticket_id AND ISNULL(@Mode,0) =3

                          ) p ON ISNULL(@Mode,0) IN (2,3,4) AND xc.Ticket_ID = p.Ticket_ID AND p.CompanyOwner_ID = xc.Company_ID

                     WHERE (ISNULL(@Mode,0) IN (2,3,4) AND p.Ticket_ID IS NOT NULL OR ISNULL(@Mode,0) IN (0,1))

                     GROUP BY xc.Ticket_ID, xc.Company_ID
                 ) xc ON xc.Company_ID = sm.CompanyOwner_ID AND xc.Ticket_ID = t.ID


            WHERE
                t.Id IN (
                    SELECT DISTINCT tr.Ticket_ID
                    FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                             INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (0,2,4)

                    UNION ALL

                    SELECT TicketId
                    FROM #PomTicket pt WHERE ISNULL(@Mode,0) =1)

              AND type.GroupType=2
              AND @S2Q2 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            UNION ALL
--- PODSUMOWANIE BILETÓW MISIĘCZNYCH - REKORD 1 zawierający tylko informację o firmie sprzedającej
            SELECT DISTINCT
                t.id											AS TICKET_ID,
                rt.MiejsceSprz									AS MIEJSCESPRZ,
                ISNULL(CAST(src.INumberBranch AS VARCHAR),'')	AS ODDZSPRZED,
                ''												AS ODDZKURSU,

                CONVERT(VARCHAR(10),t.SaleDate, 120)			AS	DATASPRZ,
                CONVERT(VARCHAR(8),t.SaleDate,108)				AS	GODZSPRZ,
                spr.INumber										AS   FIRMASP,
                0												AS   FIRMAP,
                0												AS   NRKURSU,
                ''												AS   WARIANT,
                CONVERT(VARCHAR(10),t.ValidFrom, 120)			AS   BWAZNYOD,
                ''												AS   GODZODJ,
                CONVERT(VARCHAR(10),t.ValidTo, 120)				AS   BWAZNYDO,
                0												AS   NRPP,
                ''												AS   NAZWAPP,
                0												AS   KODPP,
                0												AS   NRPD,
                ''												AS   NAZWAPD,
                0												AS   KODPD,
                ''												AS   RODZKOM,
                CASE WHEN sm.LineType_ID=5 THEN 1 ELSE 0 END	AS   KRAJ,
                0												AS   KIERWL,
                ''												AS   NRZAD,
                ''												AS   NRLINII,
				''												AS   NRLINIIEWID,  -- Nr ewidencyjny linii obsługiwany przez JSON
                0												AS   WARLINII,
                0												AS   LINIAKM,
                d.IDNumber										AS   NRKIER,
                CASE WHEN @RODO =1 THEN '' ELSE d.FirstName	END	AS   IMIE,
                CASE WHEN @RODO =1 THEN '' ELSE d.LastName END	AS   NAZWISKO,
                0												AS   NRKP,			--nie używamy tego
                fr.FiscalLogo									AS   LOGO,
                fr.ReportNumber									AS   NRRF,
                sr.ReportNumber									AS   NRRZ,
                1												AS   LPKIER,		--zawsze 1
                sr.UserStationNumber							AS   NRSTAN,
                CONVERT(VARCHAR(10),sr.RegistrationDate, 120)	AS   DATAREJ,
                'RZ'+CONVERT(VARCHAR(6),t.SaleDate,112)+'01'	AS   IDENTRZ,
                rt.TypRz										AS TYPRZ,
                CONVERT(VARCHAR(6), t.SaleDate, 112)			AS MIESSPRZ,
                CONVERT(VARCHAR(6), t.ValidFrom, 112)			AS MIESWAZN,
                t.TicketNumber									AS   NRKBIL,																		--???
                t.PrintNumber									AS   NRDOK,
                t.TicketNumberBM								AS   NRBILETU,
                t.PassangerNumber								AS   LPAS,
                CASE WHEN t.RideNumberDays IS NULL AND t.TicketType_ID=2 AND ISNULL(@Mode,0)=1 THEN 0 ELSE t.TicketType_ID END AS TYPBILETU,
                t.TicketGenre_ID								AS   RODZBIL,
                t.MonthTicketType								AS   RODZBM,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.DepartureTime,108) ELSE '99:99' END AS GODZPOCZ,
                CASE WHEN type.GroupType=1 THEN CONVERT(VARCHAR(5),sm.ArrivalTime,108) ELSE '99:99' END AS GODZKON,
                0												AS   ZAPISRK,
                ISNULL(t.ReductionRoundMethod_ID,1)-1			AS   ZAOKR,
                ISNULL(t.ReductionRefund,0)						AS   DOPLATA,
                CASE WHEN t.FarePriceReductionGroup_ID IN (1, 2, 3, 12) THEN 1
                     ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (5, 6, 7, 11, 4) THEN 2
                               ELSE CASE WHEN t.FarePriceReductionGroup_ID IN (8, 9, 10) THEN 2 ELSE 0 END END END AS TYPULGI,
                ISNULL(t.ReductionCode,0)						AS   KODBINB,					--???
                t.FarePriceReductionGroup_ID					AS   GRULGI,
                t.ReductionNumber								AS   NRULGI,
                t.ReductionName									AS   NAZULGI,
                t.ReductionPercentage 							AS   STAWKAUL,

                --XXX
                ISNULL(tr.NormalPrice,t.NormalPrice)/100.00						AS   CENABIL1,
                ISNULL(tr.DiscountCharge,t.DiscountCharge)/100.00				AS   KWOTABON1,
                ABS(ISNULL(tr.ReductionValue,t.ReductionValue))/100.00			AS   KWOTAUL1,
                ISNULL(tr.AdditionalFeeCharge,t.AdditionalFeeCharge)/100.00		AS   KWOTAOM1,
                CASE t.VatCode	WHEN 'A' THEN 1
                                  WHEN 'B' THEN 2
                                  WHEN 'C' THEN 3
                                  WHEN 'D' THEN 4
                                  WHEN 'E' THEN 5
                                  WHEN 'F' THEN 6
                                  WHEN 'G' THEN 7
                                  WHEN 'N' THEN 8
                                  ELSE 0 END														AS   NRSTPTU1,
                t.VatAmount/100													AS   STPTU1,

                ISNULL(tr.Price,t.Price)/100.00					AS BRUTPTU1,

                ISNULL(tr.NormalPriceAbroad,t.NormalPriceAbroad)/100.00						AS   CENABIL2,
                ISNULL(tr.DiscountChargeAbroad,t.DiscountChargeAbroad)/100.00				AS   KWOTABON2,
                ABS(ISNULL(tr.ReductionValueAbroad,t.ReductionValueAbroad))/100.00			AS   KWOTAUL2,
                ISNULL(tr.AdditionalFeeChargeAbroad,t.AdditionalFeeChargeAbroad)/100.00 AS   KWOTAOM2,
                CASE t.VatCodeAbroad WHEN 'A' THEN 1
                                     WHEN 'B' THEN 2
                                     WHEN 'C' THEN 3
                                     WHEN 'D' THEN 4
                                     WHEN 'E' THEN 5
                                     WHEN 'F' THEN 6
                                     WHEN 'G' THEN 7
                                     WHEN 'N' THEN 8
                                     ELSE 0 END										AS   NRSTPTU2,
                t.VatAmountAbroad/100							AS   STPTU2,

                ISNULL(tr.PriceAbroad,t.PriceAbroad)/100.00		AS  BRUTPTU2,
                0												AS   NRSTPTUD,		--??
                0												AS   STPTUD,
                ABS(ISNULL(tr.ReductionValue,t.ReductionValue) +ISNULL(ISNULL(tr.ReductionValueAbroad,t.ReductionValueAbroad),0))*SIGN(t.PassangerNumber)/100.00	AS   KWOTADOPL,

                (ISNULL(tr.Price,t.Price) + ISNULL(tr.PriceAbroad, ISNULL(tr.PriceAbroad,0)))/100.0 AS   WARTBIL,
                ISNULL(tr.AmountToPay,t.AmountToPay)/100.00		AS   DOZAPL,
                CASE
                    WHEN @Mode<>3 AND t.PaymentType_ID = -1/*mieszany*/ THEN 0
                    WHEN @Mode<>3 AND t.PaymentType_ID <> -1 THEN t.PaymentType_ID-1
                    WHEN @Mode=3 THEN t.PaymentType_ID --VERITUM
                    END                                             AS   SPZAPL,
                p.Name											AS   NAZSPZAPL,
                t.Currency_ID-1									AS   WALUTA,
                0												AS   SMB,
                c.Symbol										AS   OZNWAL,
                c.Unit											AS   JEDWAL,
                1												AS   MNWAL,
                1												AS   MNOZNIK,		--ile jest tras kursów/wszystko
                1												AS   MNUDZPRZ,		--DO ZWERYFIKOWANIA
                t.TicketReturnAmount/100.00						AS   KWOTAZWR,
                CONVERT(VARCHAR(10),t.TicketCancelled_SaleDate, 120) AS DATAANUL,
                ISNULL(dCanc.Idnumber,0)						AS   NRKASJA,
                srCanc.ReportNumber								AS   NRRAPZADA,
                'RZ'+CONVERT(VARCHAR(6),tCanc.SaleDate,112)+'01' AS  IDENTRZA,
                CAST(sm.SUMRoadDistance/1000.0 AS DECIMAL(10,1)) AS	 KMBIL,			--SUMARYCZNA DLA CAŁEGO BILETU
                0												AS   KMKBIL,		--DLA KURSU
                ''												AS   OZNACZK,		--DO ZWERYFIKOWANIA CZY JEST TO WYKORZYSTYWANE
                sm.SUMTicketRoute								AS   LKURSOWB,		-- LICZBA REK TicketRoute
                0												AS   LPKURSUB,		--DO ZWERYFIKOWANIA
                xc.CompanyCnt									AS   LPRZEWB,
                0												AS   LPPRZEWB,
                1												AS   NRTRASY,		-- ??
                0												AS   RELBIL,
                DNIRELBM										AS	 DNIRELBM,
                ec.INumber										AS   FIRMAKM,
                e.CardNumber									AS   NRKARTYM,
                t.PassangerReductionCardNumber					AS   NRDOKULGI,		--??
                CAST(CASE WHEN t.PassangerReductionCardValidDate IS NULL THEN 0 ELSE 1 END AS BIT)	AS   DOKUWBEZT,
                CONVERT(VARCHAR(10),t.PassangerReductionCardValidDate,120)							AS   DATAWDU,		--??
                dd.IDNumberHRSystem								AS   NRPAS,			--??
                t.PassangerIDCardNumber							AS   NRDOKTOZS,     --??
                CAST(0 AS BIT)									AS   DOKTWBEZT,		--??
                CONVERT(VARCHAR(10),GetDate(),120)				AS   DATAWDT,		--??
                0												AS   LPRZBO,		--??
                sr.ReportCode									AS   SZYFRBIL,		--??
                'Bilet miesięczny'								AS   RELACJAK,
                0												AS   NRSTPROW,		--??
                ''												AS   RODZSP,		--??
                CASE WHEN type.GroupType=1 THEN t.controlNumber ELSE '' END	AS   KODKBIL,		--??
                0												AS   FIRMAK,
                ''												AS   NRKURSU_E,	--?
                0												AS   KOBCE,		--??
                CONVERT(VARCHAR(10),sm.SUMRideDate, 120)		AS   DATAKURSU,	--??
                ''												AS   GODZPRZYJ,
                0												AS   WDK,			--?? PODOBNO NIE UZUEŁNIAMY
                ISNULL(f.Name, sm.FileName)						AS   ZBIORA,
                0												AS   KMKURSU,		--?? BRAK
                CAST(0 AS BIT)									AS   ZMKARTYM,		--?? BRAK
                CAST(0 AS BIT)									AS	POMINDOPL,
                ''												AS   GODZODJK,		--?? BRAK
                0												AS   NRFU,			---???????
                t.BuyerNIP										AS   NIPNABYWCY,
                CONVERT(VARCHAR(10),GETDATE(), 120)				AS   DATAOP,		---???????
                CONVERT(VARCHAR(5),GETDATE(),108)				AS   GODZOP,		---???????
                u.IDNumber										AS   NR_SLUZBOP,

                NULL											AS	 KURSWO,
                ''												AS   LINIAPP,
                ''												AS	 LINIAOP,
                0												AS	 DRIVERID,
                ''												AS	 KODBIL,
                t.QRCode										AS   QRCODE,
                t.EPNumber										AS   EPNUMBER,
                t.EPCode										AS   EPCODE

            FROM dbo.SLS_Ticket t WITH (NOLOCK)
                     INNER JOIN
                 (	SELECT SUM(tr.RoadDistance) AS SUMRoadDistance, MAX(rr.RideDate) AS SUMRideDate, COUNT(*) AS SUMTicketRoute,
                             MAX(CAST(ValidMonday AS VARCHAR)+CAST(ValidTuesday AS VARCHAR)+CAST(ValidWednesday AS VARCHAR)+CAST(ValidThursday AS VARCHAR)+CAST(ValidFriday AS VARCHAR)+CAST(ValidSaturday AS VARCHAR)+CAST(ValidSunday AS VARCHAR)) AS DNIRELBM,
                             MAX(rr.LineType_ID) AS LineType_ID, tr.Ticket_ID, MAX(tr.Companyowner_id) AS CompanyOwner_ID,
                             MAX(f2.Name) AS FileName,
                             MIN(tr.DepartureTime) AS DepartureTime,
                             MAX(tr.ArrivalTime) AS ArrivalTime

                      FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                               INNER JOIN dbo.SLS_RideRegistered rr WITH (NOLOCK) ON rr.id = tr.RideRegistered_ID

                               LEFT JOIN
                           (
                               SELECT a.Ride_ID, f.Name
                               FROM
                                   (	SELECT MAX(x.File_ID) AS fID,Ride_ID
                                        FROM dbo.DISP_FileXRide x WITH (NOLOCK)
                                                 INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON x.File_ID = f.ID
                                        WHERE f.FileType_ID=2
                                        GROUP BY Ride_ID
                                   ) a
                                       INNER JOIN dbo.DISP_File f WITH (NOLOCK) ON a.fID=f.ID

                           ) f2 ON f2.Ride_ID = rr.Ride_id

                      GROUP BY tr.Ticket_ID
                 ) sm ON sm.Ticket_ID = t.ID

                     INNER JOIN dbo.SLS_FiscalReport fr WITH (NOLOCK) ON t.FiscalReport_ID = fr.ID
                     INNER JOIN dbo.SLS_SalesReport sr WITH (NOLOCK) ON fr.SalesReport_ID=sr.ID
                     INNER JOIN dbo.SLS_ReportTypeTranslate rt WITH (NOLOCK) ON rt.ReportType_ID = sr.ReportType_ID

                     LEFT JOIN dbo.PLAN_Driver dd WITH (NOLOCK) ON dd.ID = t.Driver_ID
                     LEFT JOIN dbo.PLAN_Driver d WITH (NOLOCK) ON d.ID = sr.Driver_ID
                     LEFT JOIN dbo.ADMIN_Company src WITH (NOLOCK) ON src.ID = d.Company_ID AND src.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.ADMIN_Company spr WITH (NOLOCK) ON spr.Id = t.Company_ID AND spr.CompanyMaster_ID IS NULL

                     INNER JOIN dbo.SLS_PaymentType p WITH (NOLOCK) ON t.PaymentType_ID = p.ID
                     INNER JOIN dbo.TCK_Currency c WITH (NOLOCK) ON t.Currency_ID = c.ID

                     LEFT JOIN dbo.SLS_Ticket tCanc WITH (NOLOCK) ON tcanc.id = t.TicketCancelled_ID
                     LEFT JOIN dbo.PLAN_Driver dCanc WITH (NOLOCK) ON dCanc.ID = tCanc.Driver_ID

                     LEFT JOIN dbo.SLS_FiscalReport frCanc WITH (NOLOCK) ON tCanc.FiscalReport_ID = frCanc.ID
                     LEFT JOIN dbo.SLS_SalesReport srCanc WITH (NOLOCK) ON frCanc.SalesReport_ID=srCanc.ID

                     LEFT JOIN dbo.SLS_EmCard e WITH (NOLOCK) ON t.Emcard_ID = e.ID
                     LEFT JOIN dbo.ADMIN_Company ec WITH (NOLOCK) ON ec.ID = e.Company_ID AND ec.CompanyMaster_ID IS NULL

                     LEFT JOIN dbo.PLAN_Driver u WITH (NOLOCK) ON u.ID = sr.User_ID
                --pasażer
                --LEFT JOIN dbo.PLAN_Driver psg ON psg.ID = t.Driver_ID

                     LEFT JOIN DISP_File f WITH (NOLOCK) ON sr.FileOryg_ID = f.ID

                     INNER JOIN dbo.SLS_TicketType type WITH (NOLOCK) ON t.TicketType_ID = type.id

                     INNER JOIN
                 (
                     SELECT Ticket_ID, COUNT(*) AS CompanyCnt
                     FROM dbo.SLS_TicketXCompany xc WITH (NOLOCK)
                     GROUP BY Ticket_ID
                 ) xc ON xc.Ticket_ID = t.ID

                     LEFT JOIN
                 (
                     SELECT tr.Ticket_ID,
                            SUM(ISNULL(tr.Price,0))									AS Price,
                            SUM(ISNULL(tr.NormalPrice,0))							AS NormalPrice,
                            SUM(ISNULL(tr.ReductionValue,0))						AS ReductionValue,
                            SUM(ISNULL(tr.PriceAbroad,0))							AS PriceAbroad,
                            SUM(ISNULL(tr.ReductionValueAbroad,0))					AS ReductionValueAbroad,
                            SUM(ISNULL(tr.NormalPriceAbroad,0))						AS NormalPriceAbroad,
                            SUM(ISNULL(tr.PriceRate,0))								AS PriceRate,
                            SUM(ISNULL(DiscountCharge,0))							AS DiscountCharge,
                            SUM(ISNULL(DiscountChargeAbroad,0))						AS DiscountChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeChargeAbroad,0))				AS AdditionalFeeChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeCharge,0))					AS AdditionalFeeCharge,
                            SUM(ISNULL(tr.AmountToPay,0))							AS AmountToPay,
                            COUNT(*)												AS CompanyCnt
                     FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                              INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) =2
                     GROUP BY tr.Ticket_ID

                     UNION ALL

                     SELECT tr.Ticket_ID,
                            SUM(ISNULL(tr.Price,0))									AS Price,
                            SUM(ISNULL(tr.NormalPrice,0))							AS NormalPrice,
                            SUM(ISNULL(tr.ReductionValue,0))						AS ReductionValue,
                            SUM(ISNULL(tr.PriceAbroad,0))							AS PriceAbroad,
                            SUM(ISNULL(tr.ReductionValueAbroad,0))					AS ReductionValueAbroad,
                            SUM(ISNULL(tr.NormalPriceAbroad,0))						AS NormalPriceAbroad,
                            SUM(ISNULL(tr.PriceRate,0))								AS PriceRate,
                            SUM(ISNULL(DiscountCharge,0))							AS DiscountCharge,
                            SUM(ISNULL(DiscountChargeAbroad,0))						AS DiscountChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeChargeAbroad,0))				AS AdditionalFeeChargeAbroad,
                            SUM(ISNULL(tr.AdditionalFeeCharge,0))					AS AdditionalFeeCharge,
                            SUM(ISNULL(tr.AmountToPay,0))							AS AmountToPay,
                            COUNT(*)												AS CompanyCnt
                     FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                              INNER JOIN #PomTicket pt ON pt.TicketId = tr.Ticket_ID AND ISNULL(@Mode,0) =3

                     GROUP BY tr.Ticket_ID
                 ) tr ON tr.Ticket_ID = t.ID AND ISNULL(@Mode,0) IN (2,4)


            WHERE
                t.Id IN (

                    SELECT DISTINCT tr.Ticket_ID
                    FROM dbo.SLS_TicketRoute tr WITH (NOLOCK)
                             INNER JOIN #PomTicket pt ON pt.TicketId = tr.ID AND ISNULL(@Mode,0) IN (0,2,4)

                    UNION ALL

                    SELECT TicketId
                    FROM #PomTicket pt WHERE ISNULL(@Mode,0) IN (1,3)

                )
              AND type.GroupType=2
              AND @S2Q3 = 1
              and (@Ticket_ID IS NULL or t.ID = @Ticket_ID)

            ORDER BY t.TicketNumberBM ASC, FIRMAP ASC , NRTRASY ASC, LPKURSUB ASC
        END
END
GO
