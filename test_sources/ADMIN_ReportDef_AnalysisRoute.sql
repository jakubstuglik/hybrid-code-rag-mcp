
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO

--exec [dbo].[ADMIN_ReportDef_AnalysisRoute] N'2020-02-01',N'2020-02-10',null,870,1,0,'0',0,1,0,1,'1111'
CREATE PROCEDURE [dbo].[ADMIN_ReportDef_AnalysisRoute](
--ALTER PROCEDURE [dbo].[ADMIN_ReportDef_AnalysisRoute](
  @DateFrom nvarchar(10),
  @DateTo nvarchar(10),
  @LineStr NVARCHAR(MAX),
  @LineRouteDetails_ID int  = 1,
  @TicketType_ID int = -1,
  @TerritorialDiv tinyint = 0,
  @TerritorialDiv_ID NVARCHAR(20) = '0',  
  @TimeTableId int = 0,
  @Brutto tinyint  =  1, --  0 - netto 1 - brutto
  @AddReductionValue tinyint  =  0, --  0 - bez dopłaty 1 - z dopłatą      Ticket_ReductionValue  
  @ReportType tinyint  =  0, --  0 - całe bilety z wybranej trasy 1 - wsiadania lub wysiadania na wybranej strasie
  @DaysStr NVARCHAR(MAX) --TODO 1111  - 4 kategorie (do rozbudowania): dni robocze, soboty,niedziele, święta
)
as
begin
  SET NOCOUNT ON;  

  declare @WorkDays tinyint = 1;
  declare @SatDays  tinyint = 1;
  declare @SunDays  tinyint = 1;
  declare @HoliDays tinyint = 1;

  if SUBSTRING(@DaysStr,1,1)='1' set @WorkDays=1 else set @WorkDays=0;
  if SUBSTRING(@DaysStr,2,1)='1' set @SatDays=1  else set @SatDays=0;
  if SUBSTRING(@DaysStr,3,1)='1' set @SunDays=1  else set @SunDays=0;
  if SUBSTRING(@DaysStr,4,1)='1' set @HoliDays=1 else set @HoliDays=0;

  declare @Rides table (id int);

  if isnull(@linestr,'') <>''
  begin
	insert into @Rides
	select y.Ride_ID as id
	from dbo.admin_splitstring(@linestr, ';') x
	LEFT JOIN dbo.TT_Ride r ON r.Line_ID = x.value
	LEFT JOIN dbo.TT_TimeTableParamsRide(@TimeTableID) y ON y.Ride_id = r.id
	WHERE ( (@TimeTableID = 0) OR ( (@TimeTableID <> 0) AND (y.Ride_id IS NOT NULL)) )
  end
  else 
  begin
	insert into @Rides
	select Ride_id as id from dbo.TT_TimeTableParamsRide(@timetableid)
	IF @TimeTableId >0
		SET @LineStr ='x' --sztuczne
  end;
	--------------------------------------------------------------------------------
	with MyBASERoute as
		(select ROW_NUMBER() OVER( ORDER BY lr.RoadPointNo) MyID, lr.RoadPointNo, 		
		lr.ID as LineRoute_ID,
		--bs.BusStop_ID,
		bst.Name as BASERouteBusStopName
		from TT_LineRoute lr
		left join TT_BusStand bs on bs.RoadPoint_ID=lr.RoadPoint_ID
		left join TT_BusStop bst on bst.ID=bs.BusStop_ID
		where lr.LineRouteDetails_ID=@LineRouteDetails_ID and (IsNull(bs.BusStop_ID,0)>0)		
		),
	--------------------------------------------------------------------------------
	DW_viewSalesFactBASE as
	(
	select
	  sf.ID,
	  sf.Dim_CalendarDate,
	  --sf.StartBusStop_ID, sf.EndBusStop_ID,
	  sf.RideRouteFrom_ID, sf.RideRouteTo_ID,
	  sf.StartBusStopName, sf.EndBusStopName,
	  sf.Dim_Ride_ID,
	  sf.Dim_TicketType_ID,
	  cast(sf.Dim_RideNumber as varchar) + '/' + cast(sf.Dim_RideVariant as varchar) + '/' + convert(char(10), sf.Dim_RideValidFrom, 120) as RideName,	  --+ '/' + sf.Dim_RideName
	  case 
	      when @TerritorialDiv = 0 then cast(case 
											when @AddReductionValue=0 and @Brutto=1 then sf.Price
											when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
											when @AddReductionValue=0 and @Brutto=0 then sf.Price-dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
											when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount) --netto
											end / 100. as money)
		  when 
		    @TerritorialDiv = 1 and 
			--IsNumeric(SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1)) = 1 AND 
			SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1) = @TerritorialDiv_ID and
		    --IsNumeric(SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1)) = 1 AND 
			SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1) = @TerritorialDiv_ID
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price-dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount) --netto
				end / 100. as money)
          when 
		    @TerritorialDiv = 1 and
			(--IsNumeric(SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1)) = 1 AND 
			 SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1) = @TerritorialDiv_ID or
			 --IsNumeric(SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1)) = 1 AND 
			 SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1) = @TerritorialDiv_ID) 		  
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount) --netto
					end / 2. / 100. as money)                  
		  when 
		    @TerritorialDiv = 2 and
			sf.Dim_StartDistrict_ID = @TerritorialDiv_ID and
			sf.Dim_EndDistrict_ID = @TerritorialDiv_ID 
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount) --netto
					end / 100. as money)
          when 
		    @TerritorialDiv = 2 and
			(sf.Dim_StartDistrict_ID = @TerritorialDiv_ID or
			sf.Dim_EndDistrict_ID = @TerritorialDiv_ID) 
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount)  --netto
					end / 2. / 100. as money)                  
          when 
		    @TerritorialDiv = 3 and
			sf.Dim_StartProvince_ID = @TerritorialDiv_ID and
		    sf.Dim_EndProvince_ID = @TerritorialDiv_ID
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount)  --netto
					end / 100. as money)
          when 
		    @TerritorialDiv = 3 and 
			(sf.Dim_StartProvince_ID = @TerritorialDiv_ID or
			sf.Dim_EndProvince_ID = @TerritorialDiv_ID)
		  then cast(case 
					when @AddReductionValue=0 and @Brutto=1 then sf.Price
					when @AddReductionValue=1 and @Brutto=1 then (sf.Price + sf.ReductionAmount)
					when @AddReductionValue=0 and @Brutto=0 then sf.Price - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) --netto
					when @AddReductionValue=1 and @Brutto=0 then (sf.Price + sf.ReductionAmount) - dbo.SLS_GetVatValue(sf.Price,sf.VatAmount) - dbo.SLS_GetVatValue(IsNull(sf.ReductionAmount,0),sf.VatAmount)  --netto
					end / 2. / 100. as money)		  
		  else 0
	    end as Price,	  	  
	  sf.Dim_RideDepartureTime,
	  ac.Monday,ac.Tuesday,ac.Wednesday,ac.Thursday,ac.Friday,
	  ac.Saturday,Sunday,
	  ac.Holiday,
	  --,sum(sf.ReductionAmount / 100.) as ReductionAmount	  
	  rr_start.LineRoute_ID as LineRouteFrom_ID, 
	  rr_end.LineRoute_ID as LineRouteTo_ID 
	from dbo.DW_viewSalesFact sf WITH (NOLOCK)	
	left join dbo.TT_RideRoute rr_start WITH (NOLOCK) on rr_start.ID=sf.RideRouteFrom_ID
	left join dbo.TT_RideRoute rr_end   WITH (NOLOCK) on rr_end.ID=sf.RideRouteTo_ID
	left join MyBaseRoute mbrs on (mbrs.LineRoute_ID=rr_start.LineRoute_ID)
	left join MyBaseRoute mbre on (mbre.LineRoute_ID=rr_end.LineRoute_ID)	
	left join dbo.ADMIN_Calendar ac on (sf.Dim_Calendar_ID=ac.ID)	
   where 
	((not mbrs.MyID is null) or (not mbre.MyID is null)) 		
	 and ((ISNULL(@LineStr,'')='') OR  (sf.Dim_Ride_ID in (select ID from @Rides)))
	 AND (CAST(sf.Dim_CalendarDate AS DATE)>=@DateFrom and CAST(sf.Dim_CalendarDate AS DATE)<=@DateTo)	 
	 and ((@TicketType_ID=-1) or 1 =
	       (case 
	          when (@TicketType_ID < 99) and (@TicketType_ID = sf.Dim_TicketType_ID) and (sf.EmCardXPassangerRecording_ID IS NULL) then 1
			  WHEN (@TicketType_ID = 199) AND (sf.Dim_TicketType_ID in (1,17)) and (sf.EmCardXPassangerRecording_ID IS NULL) THEN 1
	          when (@TicketType_ID = 99) and (sf.Dim_TicketType_ID in (2,3,7,8,18)) and (sf.EmCardXPassangerRecording_ID IS NULL) then 1
	          when (@TicketType_ID = 1000) and (sf.EmCardXPassangerRecording_ID IS NOT NULL) then 1
	          when (@TicketType_ID = 1001) and ((sf.EmCardXPassangerRecording_ID IS NOT NULL) or (sf.Dim_TicketType_ID in (1,17)) ) then 1
		      else 0
		    end))
	 and (
		  (((@TerritorialDiv = 1) and 
		    --(IsNumeric(SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1)) = 1) AND 
			(SUBSTRING(sf.Dim_StartCommunitySymbol, 1,LEN(sf.Dim_StartCommunitySymbol)-1) = @TerritorialDiv_ID)
		  )
		  or ((@TerritorialDiv = 2) and (sf.Dim_StartDistrict_ID = @TerritorialDiv_ID))
		  or ((@TerritorialDiv = 3) and (sf.Dim_StartProvince_ID = @TerritorialDiv_ID))
		  or (@TerritorialDiv_ID =0)
		)
		 or
		 (((@TerritorialDiv = 1) and 
		   --IsNumeric(SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1)) = 1 AND 
		   SUBSTRING(sf.Dim_EndCommunitySymbol, 1,LEN(sf.Dim_EndCommunitySymbol)-1) = @TerritorialDiv_ID
		  or ((@TerritorialDiv = 2) and sf.Dim_EndDistrict_ID = @TerritorialDiv_ID) 
		  or ((@TerritorialDiv = 3) and sf.Dim_EndProvince_ID = @TerritorialDiv_ID) 
		 ) or (@TerritorialDiv_ID =0)
		 ) 
	 	)
	 and
	 (
	  (@DaysStr='1111') or
	  (
	   ((@WorkDays=1)    and ((ac.Monday=1) or (ac.Tuesday=1) or (ac.Wednesday=1) or (ac.Thursday=1) or (ac.Friday=1)) and (ac.Holiday=0)) or
	   ((@SatDays=1)  and (ac.Saturday=1) and (ac.Holiday=0)) or
	   ((@SunDays=1)  and (ac.Sunday=1)   and (ac.Holiday=0)) or
	   ((@HoliDays=1) and (ac.Holiday=1)) 	  
	  )
	 )
	),
	--------------------------------------------------------------------------------
	DataDepart0 as
	(
	select sf.ID as DWid, mbrs.MyID, mbrs.BASERouteBusStopName as MyBusStopName,
			sf.RideName as RideName,
			sf.Dim_RideDepartureTime as RideDepartureTime,
			1 as MyCountDepart,
			0 as MyCountArrival,
			sf.Price/2 as MyHalfPrice
	from DW_viewSalesFactBASE sf WITH (NOLOCK)		
	left join MyBaseRoute mbrs on (mbrs.LineRoute_ID=sf.LineRouteFrom_ID)
	left join MyBaseRoute mbre on (mbre.LineRoute_ID=sf.LineRouteTo_ID)	
	where (@ReportType=0) and
	      (not mbrs.MyID is null) and
		  (not mbre.MyID is null) and
		  (mbrs.MyID<mbre.MyID)
	
	),
	--------------------------------------------------------------------------------
	DataArrival0 as
	(
	select sf.ID as DWid, mbre.MyID, mbre.BASERouteBusStopName as MyBusStopName,
			sf.RideName as RideName,
			sf.Dim_RideDepartureTime as RideDepartureTime,
			0 as MyCountDepart,
			1 as MyCountArrival,
			sf.Price/2 as MyHalfPrice
	from DW_viewSalesFactBASE sf
	left join MyBaseRoute mbrs on (mbrs.LineRoute_ID=sf.LineRouteFrom_ID)
	left join MyBaseRoute mbre on (mbre.LineRoute_ID=sf.LineRouteTo_ID)	
	where (@ReportType=0) and
	      (not mbrs.MyID is null) and
		  (not mbre.MyID is null) and
		  (mbrs.MyID<mbre.MyID)	
	),
	--------------------------------------------------------------------------------
	DataDepart1 as --wsiadło na przystankach z trasy bazowej
	(
	select  sf.ID as DWid, mbrs.MyID, mbrs.BASERouteBusStopName as MyBusStopName,
			sf.EndBusStopName as RideName,  --start z RideName end w MyBusStopName
			'' as RideDepartureTime,
			1 as MyCountDepart,
			0 as MyCountArrival,
			sf.Price/2 as MyHalfPrice
	from DW_viewSalesFactBASE sf
		inner join MyBaseRoute mbrs on (mbrs.LineRoute_ID=sf.LineRouteFrom_ID)	
	where (@ReportType=1)
	--where (not mbrs.MyID is null) 
	),
	--------------------------------------------------------------------------------
	DataArrival1 as --wysiadło na przystankach z trasy bazowej
	(
	select sf.ID as DWid, mbre.MyID, mbre.BASERouteBusStopName as MyBusStopName,
			sf.StartBusStopName as RideName,  --start z RideName end w MyBusStopName
			'' as RideDepartureTime,
			0 as MyCountDepart,
			1 as MyCountArrival,
			sf.Price/2 as MyHalfPrice
	from DW_viewSalesFactBASE sf		
	inner join MyBaseRoute mbre on (mbre.LineRoute_ID=sf.LineRouteTo_ID)	
	where (@ReportType=1)
	--where (not mbre.MyID is null)	
	)
	--------------------------------------------------------------------------------
	--------------------------------------------------------------------------------

	select * from DataDepart0 where @ReportType=0
	union 
	select * from DataArrival0 where @ReportType=0
	union 
	select * from DataDepart1 where @ReportType=1
	union 
	select * from DataArrival1 where @ReportType=1
	order by MyID,RideName
	
	--select * from MyBASERoute
	--select * from DW_viewSalesFactBASE
	--select * from DataDepart0
	
  SET NOCOUNT OFF;
end
GO
