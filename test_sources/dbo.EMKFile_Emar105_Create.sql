SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
CREATE PROCEDURE [dbo].[EMKFile_Emar105_Create]
    @result TINYINT OUT
    , @DateFrom NVARCHAR(23)
    , @DateTo NVARCHAR(23)
/*
    Zwraca 1, gdy w niektórych tabelach, potrzecnych do generowania pliku 'EMK', coś się zmieniło
*/
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @bFirstTimeRunning BIT,
			@dDateFrom DATETIME,
            @dDateTo DATETIME,
            @dActiveDate DATE;

    SELECT
        @bFirstTimeRunning =
            CASE
                WHEN @DateFrom IS NOT NULL AND CAST(@DateFrom AS DATE) != '1900-01-01' THEN 0
                ELSE 1
            END,
		@dDateFrom =
            CASE
                WHEN CONVERT(DATETIME, @DateFrom, 121) > '1900-01-01' THEN CONVERT(DATETIME, @DateFrom, 121)
                ELSE '1900-01-01'
            END,
        @dDateTo =
            CASE
                WHEN CONVERT(DATETIME, @DateTo, 121) > '1900-01-01' THEN CONVERT(DATETIME, @DateTo, 121)
                ELSE '1900-01-01'
            END,
        @dActiveDate = CAST(GETDATE() AS DATE);

-- BEGIN to samo powinno byc w ExportTicketsToJSON
    CREATE TABLE #Tickets_ExportTicketsToJSON (Ticket_ID BIGINT, EmCard_ID INT, TicketNumberBM VARCHAR(50), ValidFrom DATETIME, TicketCancelDate DATETIME);
    CREATE NONCLUSTERED INDEX tmpTickets_ExportTicketsToJSON_TicketID_idx ON #Tickets_ExportTicketsToJSON (Ticket_ID);
    CREATE NONCLUSTERED INDEX tmpTickets_ExportTicketsToJSON_EmCardIDTicketNumberBM_idx ON #Tickets_ExportTicketsToJSON (EmCard_ID, TicketNumberBM);
	CREATE NONCLUSTERED INDEX tmpTickets_ExportTicketsToJSON_TicketCancelDate_idx ON #Tickets_ExportTicketsToJSON (TicketCancelDate) WHERE TicketCancelDate IS NOT NULL;
    CREATE TABLE #PETickets_ExportTicketsToJSON (Ticket_ID BIGINT);
    CREATE NONCLUSTERED INDEX tmpPETickets_ExportTicketsToJSON_idx ON #PETickets_ExportTicketsToJSON (Ticket_ID);

	-- wybierany ostatni bilet dla ValidFrom-ValidTo
    ;WITH CTE_T_All AS
    (
        SELECT
              RowNumberEmCard = ROW_NUMBER() OVER (PARTITION BY T.EmCard_ID ORDER BY T.ValidFrom DESC, T.SaleDate DESC)
			, RowNumberEmCardValidFrom = ROW_NUMBER() OVER (PARTITION BY T.EmCard_ID, T.ValidFrom ORDER BY T.ValidFrom DESC, T.SaleDate DESC)
            , T.ID
            , T.EmCard_ID
            , T.TicketNumberBM
            , T.ValidFrom
            , T.ValidTo
            , T.CREATED
            , T.MODIFIED
        FROM dbo.SLS_Ticket AS T WITH (NOLOCK)
        WHERE T.Emcard_ID > 0
            AND T.TicketNumberBM LIKE '[A-Z]%'
            AND T.ValidFrom IS NOT NULL -- exclude f.e. Paragon
            AND T.ValidTo IS NOT NULL -- exclude f.e. Paragon
            AND T.TicketCancelled_ID IS NULL -- nie zwrot
            AND T.TicketType_ID NOT IN (14/*zwrot kaucji za EM-Kartę*/, 23/*kaucja za wyd. EM-Karty*/)
    )
    , CTE_T AS (
        SELECT 
            ID
            , EmCard_ID
            , TicketNumberBM
            , ValidFrom
            , ValidTo
            , CREATED
            , MODIFIED
        FROM CTE_T_All
            WHERE
                RowNumberEmCard = 1 -- ostatni bilet dla karty
				AND @bFirstTimeRunning = 1 -- po raz pierwszy uruchamiana
                OR
                RowNumberEmCardValidFrom = 1 -- ostatnia para ValidFrom-ValidTo dla danej Em-Karty (n.p., gdy anulowany a potem kupiony nowy na ten sam okres)
                AND @dActiveDate <= ValidTo -- ważny +
    )
    -- This single INSERT statement replaces the two separate versions from the IF/ELSE block.
    INSERT INTO #Tickets_ExportTicketsToJSON (Ticket_ID, EmCard_ID, TicketNumberBM, ValidFrom, TicketCancelDate)
    SELECT
        T.ID
        , T.EmCard_ID
        , T.TicketNumberBM
        , T.ValidFrom
        , TicketCancelDate =
            CASE
                WHEN PETC.DateCancelled IS NOT NULL THEN PETC.DateCancelled
                ELSE
                    CASE
                        WHEN TC.ID IS NOT NULL THEN TC.SaleDate
                        ELSE NULL
                    END
            END
    FROM CTE_T AS T
        INNER JOIN dbo.SLS_EmCard AS EC WITH (NOLOCK) ON T.Emcard_ID = EC.ID
        LEFT JOIN dbo.SLS_TicketRoute AS TR WITH (NOLOCK) ON T.ID = TR.Ticket_ID
        LEFT JOIN dbo.SLS_EmCardSaleOnBus AS ECSOB WITH (NOLOCK) ON T.ID = ECSOB.Ticket_ID
        LEFT JOIN dbo.SLS_EmCardTicketProlonging AS ECTP WITH (NOLOCK) ON EC.CardNumber = ECTP.CardNumber AND T.TicketNumberBM = ECTP.TicketNumberBM
        LEFT JOIN dbo.SLS_EmCardXPassanger AS ECXP WITH (NOLOCK) ON EC.ID = ECXP.EmCard_ID
        LEFT JOIN dbo.SLS_PETicketDuplicate AS PETD WITH (NOLOCK) ON EC.CardNumber = PETD.EmCardNumber AND T.TicketNumberBM = PETD.TicketNumberBM
        LEFT JOIN dbo.SLS_PETicketCancel AS PETC WITH (NOLOCK) ON EC.CardNumber = PETC.EmCardNumber AND T.TicketNumberBM = PETC.TicketNumberBM
        LEFT JOIN dbo.SLS_SalesReportEventD AS SRED WITH (NOLOCK) ON EC.CardNumber = SRED.OldEmCardNumber AND T.TicketNumberBM = SRED.NumberBM
        LEFT JOIN dbo.SLS_Ticket AS TC WITH (NOLOCK) ON T.ID = TC.TicketCancelled_ID
    WHERE
        -- If date parameters are NULL, this condition is true, and no date filtering occurs (original ELSE logic)
        @dDateFrom = '1900-01-01' AND @dDateTo = '1900-01-01'
        OR
        -- If date parameters are provided, this block applies the filters (original IF logic)
        (
            (T.CREATED BETWEEN @dDateFrom AND @dDateTo OR T.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (TR.CREATED BETWEEN @dDateFrom AND @dDateTo OR TR.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (ECSOB.CREATED BETWEEN @dDateFrom AND @dDateTo OR ECSOB.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (ECXP.CREATED BETWEEN @dDateFrom AND @dDateTo OR ECXP.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (ECXP.CREATED BETWEEN @dDateFrom AND @dDateTo OR ECXP.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (PETD.CREATED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (PETC.CREATED BETWEEN @dDateFrom AND @dDateTo)
            OR
            (SRED.CREATED BETWEEN @dDateFrom AND @dDateTo OR SRED.MODIFIED BETWEEN @dDateFrom AND @dDateTo)
        )
        --AND NOT EXISTS(SELECT Ticket_ID FROM dbo.SLS_TicketRoute WITH (NOLOCK) WHERE Ticket_ID = T.ID AND Ride_ID IS NULL) -- ATY: temporary condition until incorrect data has been resolved
    GROUP BY T.ID, T.EmCard_ID, T.TicketNumberBM, T.ValidFrom
          , CASE
                WHEN PETC.DateCancelled IS NOT NULL THEN PETC.DateCancelled
                ELSE
                    CASE
                        WHEN TC.ID IS NOT NULL THEN TC.SaleDate
                        ELSE NULL
                    END
            END;
    
    ;WITH CTE_T AS
    (
        SELECT
			TicketNumberBM = MAX(PET.TicketNumberBM) -- in case 2 or more tickets sold for the same EmCardNumber and ValidFrom-ValidTo
			, PET.EmCardNumber
			, PET.ValidFrom
		FROM dbo.SLS_PEData AS D WITH (NOLOCK)
			INNER JOIN dbo.SLS_PETicket AS PET WITH (NOLOCK) ON D.ID = PET.PEData_ID
            LEFT JOIN dbo.SLS_PETicketDuplicate AS PETD WITH (NOLOCK) ON PET.EmCardNumber = PETD.EmCardNumber AND PET.TicketNumberBM = PETD.TicketNumberBM
            LEFT JOIN dbo.SLS_PETicketCancel AS PETC WITH (NOLOCK) ON PET.EmCardNumber = PETC.EmCardNumber AND PET.TicketNumberBM = PETC.TicketNumberBM
		WHERE
			-- Combined condition: checks D.CREATED only if date parameters are not NULL.
			(
				@dDateFrom = '1900-01-01' AND @dDateTo = '1900-01-01'
				OR
				D.CREATED BETWEEN @dDateFrom AND @dDateTo
                OR
				PETD.CREATED BETWEEN @dDateFrom AND @dDateTo
                OR
				PETC.CREATED BETWEEN @dDateFrom AND @dDateTo
			)
			AND @dActiveDate <= PET.ValidTo
		GROUP BY PET.EmCardNumber, PET.ValidFrom -- Assuming ValidTo refers to PET.ValidTo
    )
    -- This INSERT is also refactored to handle both cases.
    INSERT INTO #PETickets_ExportTicketsToJSON (Ticket_ID)
    SELECT
        MAX(PET.ID) -- eliminate duplicated information about the same ticket
    FROM dbo.SLS_PETicket AS PET WITH (NOLOCK)
		INNER JOIN CTE_T ON PET.EmCardNumber = CTE_T.EmCardNumber
			AND PET.TicketNumberBM = CTE_T.TicketNumberBM
			AND PET.ValidFrom = CTE_T.ValidFrom
		OUTER APPLY(
			SELECT T.ID FROM dbo.SLS_Ticket AS T WITH (NOLOCK)
				INNER JOIN SLS_EmCard AS EC ON PET.EmCardNumber = EC.CardNumber AND T.Emcard_ID = EC.ID
			WHERE PET.TicketNumberBM = T.TicketNumberBM AND PET.ValidFrom = T.ValidFrom
			) AS T
    WHERE
        T.ID IS NULL
    GROUP BY PET.EmCardNumber, PET.TicketNumberBM, PET.ValidFrom;

    /*
        usuwanie biletu, anulowanie którego już jest w SLS_PETicketCancel, ale sam bilet jeszcze nie został fizycznie anulowany (brak ID w TicketCancelled_ID)
        lub
        bilet został anulowany (jest na to RZ), w PE została umieszczona informacja o sprzedaży nowego biletu ta ten okres, ale jeszcze brak RZ z nowym biletem (przypadek, gdy jednocześnie 2-a bilety są sprzedane)
        => do JSON trafi rekord z SLS_PETicket
    */
    DELETE TJSON FROM #Tickets_ExportTicketsToJSON AS TJSON
        INNER JOIN SLS_EmCard AS EC ON TJSON.Emcard_ID = EC.ID
        INNER JOIN dbo.SLS_PETicket AS PET WITH (NOLOCK) ON PET.ValidFrom = TJSON.ValidFrom AND PET.EmCardNumber = EC.CardNumber
        INNER JOIN #PETickets_ExportTicketsToJSON AS PEJSON ON PET.ID = PEJSON.Ticket_ID
    WHERE TJSON.TicketCancelDate IS NOT NULL;
-- END to samo powinno byc w ExportTicketsToJSON

    SET NOCOUNT OFF;

    IF EXISTS(SELECT Ticket_ID FROM #Tickets_ExportTicketsToJSON)
        OR EXISTS(SELECT Ticket_ID FROM #PETickets_ExportTicketsToJSON)
        SELECT @result = 1
    ELSE
        SELECT @result = 0;

    SET NOCOUNT ON;
    
    IF OBJECT_ID('tempdb..#Tickets_ExportTicketsToJSON') IS NOT NULL
        DROP TABLE #Tickets_ExportTicketsToJSON;
    IF OBJECT_ID('tempdb..#PETickets_ExportTicketsToJSON') IS NOT NULL
        DROP TABLE #PETickets_ExportTicketsToJSON;
END
GO
