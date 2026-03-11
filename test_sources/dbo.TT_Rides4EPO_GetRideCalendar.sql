SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
CREATE PROCEDURE [dbo].[TT_Rides4EPO_GetRideCalendar]
--ALTER PROCEDURE [dbo].[TT_Rides4EPO_GetRideCalendar]
(
@Ride_ID_Input int = null,
@date_from varchar(23),
@date_to varchar(23)
)
--uwaga dodać w Delphi brakujące miesiące gdzie nie ma wykonań
as
Begin	
set nocount on;
create table #tt(
RIDE_ID INT,
[ROK] [int] NULL,
[MIESIAC] [int] NULL,
[WYK1] [bit] NULL,
[WYK2] [bit] NULL,
[WYK3] [bit] NULL,
[WYK4] [bit] NULL,
[WYK5] [bit] NULL,
[WYK6] [bit] NULL,
[WYK7] [bit] NULL,
[WYK8] [bit] NULL,
[WYK9] [bit] NULL,
[WYK10] [bit] NULL,
[WYK11] [bit] NULL,
[WYK12] [bit] NULL,
[WYK13] [bit] NULL,
[WYK14] [bit] NULL,
[WYK15] [bit] NULL,
[WYK16] [bit] NULL,
[WYK17] [bit] NULL,
[WYK18] [bit] NULL,
[WYK19] [bit] NULL,
[WYK20] [bit] NULL,
[WYK21] [bit] NULL,
[WYK22] [bit] NULL,
[WYK23] [bit] NULL,
[WYK24] [bit] NULL,
[WYK25] [bit] NULL,
[WYK26] [bit] NULL,
[WYK27] [bit] NULL,
[WYK28] [bit] NULL,
[WYK29] [bit] NULL,
[WYK30] [bit] NULL,
[WYK31] [bit] NULL
)

	BEGIN TRY
	  EXEC [dbo].[TT_RideCalendar_PopulateByRide] 
				@ride_id		= @Ride_ID_Input,
				@fromdatestr	= @date_from,
				@todatestr		= @date_to
	END TRY
	BEGIN CATCH
	END CATCH; 

	--declare @ROK int=0;
	--declare @MIESIAC int=0;
	declare @WYK1 bit=0;
	declare @WYK2 bit=0;
	declare @WYK3 bit=0;
	declare @WYK4 bit=0;
	declare @WYK5 bit=0;
	declare @WYK6 bit=0;
	declare @WYK7 bit=0;
	declare @WYK8 bit=0;
	declare @WYK9 bit=0;
	declare @WYK10 bit=0;
	declare @WYK11 bit=0;
	declare @WYK12 bit=0;
	declare @WYK13 bit=0;
	declare @WYK14 bit=0;
	declare @WYK15 bit=0;
	declare @WYK16 bit=0;
	declare @WYK17 bit=0;
	declare @WYK18 bit=0;
	declare @WYK19 bit=0;
	declare @WYK20 bit=0;
	declare @WYK21 bit=0;
	declare @WYK22 bit=0;
	declare @WYK23 bit=0;
	declare @WYK24 bit=0;
	declare @WYK25 bit=0;
	declare @WYK26 bit=0;
	declare @WYK27 bit=0;
	declare @WYK28 bit=0;
	declare @WYK29 bit=0;
	declare @WYK30 bit=0;
	declare @WYK31 bit=0;   

	declare @RideDate date;
	declare @ADzien int=0;
	declare @AMiesiac int=0;
	declare @ARok int=0;	
	declare @DaysInMonth int=0;	

   

   DECLARE db_cursor CURSOR FOR  		
	   SELECT RideDate 
	   FROM dbo.TT_RideCalendar  with (nolock)
	   WHERE Ride_ID=@Ride_ID_Input and RideDate BETWEEN convert(datetime,@date_from,121) AND convert(datetime,@date_to,121)
	   order by RideDate;
   OPEN db_cursor

	FETCH NEXT FROM db_cursor INTO @RideDate;						
	WHILE @@FETCH_STATUS = 0  
	BEGIN  	
		--print @RideDate;
		if (@AMiesiac<>Month(@RideDate)) or (@ARok<>Year(@RideDate)) and (@ARok>0)  
		begin
			if @ARok>0
			  insert into #tt
	    		(RIDE_ID,ROK,MIESIAC,WYK1,WYK2,WYK3,WYK4,WYK5,WYK6,WYK7,WYK8,WYK9,WYK10,WYK11,WYK12,WYK13,WYK14,WYK15,
		    	                     WYK16,WYK17,WYK18,WYK19,WYK20,WYK21,WYK22,WYK23,WYK24,WYK25,WYK26,WYK27,WYK28,WYK29,WYK30,WYK31)
			  values
			  (@Ride_ID_Input,@AROK,@AMIESIAC,@WYK1,@WYK2,@WYK3,@WYK4,@WYK5,@WYK6,@WYK7,@WYK8,@WYK9,@WYK10,@WYK11,@WYK12,@WYK13,@WYK14,@WYK15,
			                                  @WYK16,@WYK17,@WYK18,@WYK19,@WYK20,@WYK21,@WYK22,@WYK23,@WYK24,@WYK25,@WYK26,@WYK27,@WYK28,@WYK29,@WYK30,@WYK31)
			
			--print '@DaysInMonth'+str(@AMIESIAC)+': '+str(@DaysInMonth);
			set @AROK=0;   set @AMIESIAC=0;
			set @WYK1=0;  set @WYK2=0;  set @WYK3=0;  set @WYK4=0;  set @WYK5=0;  set @WYK6=0;  set @WYK7=0;  set @WYK8=0;  set @WYK9=0;  set @WYK10=0; 
			set @WYK11=0; set @WYK12=0; set @WYK13=0; set @WYK14=0; set @WYK15=0; set @WYK16=0; set @WYK17=0; set @WYK18=0; set @WYK19=0; set @WYK20=0; 
			set @WYK21=0; set @WYK22=0; set @WYK23=0; set @WYK24=0; set @WYK25=0; set @WYK26=0; set @WYK27=0; set @WYK28=0; set @WYK29=0; set @WYK30=0; set @WYK31=0;
			
			set @DaysInMonth = 0;
			
		end;
		set @ADzien=Day(@RideDate);
		set @AMiesiac=Month(@RideDate);
		set @ARok=Year(@RideDate);
		
		if @ADzien=1  set @WYK1=1;  if @ADzien=2  set @WYK2=1;  if @ADzien=3  set @WYK3=1;  if @ADzien=4  set @WYK4=1;  if @ADzien=5 set @WYK5=1;
		if @ADzien=6  set @WYK6=1;  if @ADzien=7  set @WYK7=1;  if @ADzien=8  set @WYK8=1;  if @ADzien=9  set @WYK9=1;  if @ADzien=10 set @WYK10=1;
		if @ADzien=11 set @WYK11=1; if @ADzien=12 set @WYK12=1; if @ADzien=13 set @WYK13=1; if @ADzien=14 set @WYK14=1; if @ADzien=15 set @WYK15=1;
		if @ADzien=16 set @WYK16=1; if @ADzien=17 set @WYK17=1; if @ADzien=18 set @WYK18=1; if @ADzien=19 set @WYK19=1; if @ADzien=20 set @WYK20=1;
		if @ADzien=21 set @WYK21=1; if @ADzien=22 set @WYK22=1; if @ADzien=23 set @WYK23=1; if @ADzien=24 set @WYK24=1; if @ADzien=25 set @WYK25=1;
		if @ADzien=26 set @WYK26=1; if @ADzien=27 set @WYK27=1; if @ADzien=28 set @WYK28=1; if @ADzien=29 set @WYK29=1; if @ADzien=30 set @WYK30=1;
		if @ADzien=31 set @WYK31=1;		
		set @DaysInMonth = @DaysInMonth + 1;		
		FETCH NEXT FROM db_cursor INTO @RideDate;
	END;	
	CLOSE db_cursor  
	DEALLOCATE db_cursor 
	if @DaysInMonth>0 
	begin
		--print '@DaysInMonth'+str(@AMIESIAC)+': '+str(@DaysInMonth);
		insert into #tt
	    		(RIDE_ID,ROK,MIESIAC,WYK1,WYK2,WYK3,WYK4,WYK5,WYK6,WYK7,WYK8,WYK9,WYK10,WYK11,WYK12,WYK13,WYK14,WYK15,
		    	                     WYK16,WYK17,WYK18,WYK19,WYK20,WYK21,WYK22,WYK23,WYK24,WYK25,WYK26,WYK27,WYK28,WYK29,WYK30,WYK31)
			  values
			  (@Ride_ID_Input,@AROK,@AMIESIAC,@WYK1,@WYK2,@WYK3,@WYK4,@WYK5,@WYK6,@WYK7,@WYK8,@WYK9,@WYK10,@WYK11,@WYK12,@WYK13,@WYK14,@WYK15,
			                                  @WYK16,@WYK17,@WYK18,@WYK19,@WYK20,@WYK21,@WYK22,@WYK23,@WYK24,@WYK25,@WYK26,@WYK27,@WYK28,@WYK29,@WYK30,@WYK31)
	end;
	select * from #tt;
  --exec [TT_Rides4EPO_GetRideCalendar] 5,'2016-11-25 11:49:07','2018-11-25 11:49:07'  
end
GO
