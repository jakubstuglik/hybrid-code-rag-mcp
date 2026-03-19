unit JobReports.Classes;

interface

uses
  Classes, SysUtils, Generics.Collections,
  job_report_base, report_consts;

type

  TJobReportItem    = class;
  TJobReportList    = class;
  TDriverPayReport  = class;
  TFuelCostReport   = class;

// ────────────────────────────────────────────────────────────────────
// Constants
// ────────────────────────────────────────────────────────────────────

const
  REPORT_TYPE_DRIVER_PAYROLL      = 1;
  REPORT_TYPE_FUEL_COSTS          = 2;
  REPORT_TYPE_ROUTE_PERFORMANCE   = 3;
  REPORT_TYPE_JOB_SUMMARY         = 4;
  REPORT_TYPE_VEHICLE_UTILISATION = 5;
  REPORT_TYPE_INCIDENT_LOG        = 6;
  REPORT_TYPE_MAINTENANCE_COSTS   = 7;
  REPORT_TYPE_CUSTOMER_BILLING    = 8;
  REPORT_TYPE_KPI_DASHBOARD       = 9;
  REPORT_TYPE_DRIVER_HOURS        = 10;

  C_REPORT_DATE_FORMAT    = 'YYYY-MM-DD';
  C_REPORT_CURRENCY_PREC  = 2;
  C_REPORT_MAX_ROWS       = 50000;

// ────────────────────────────────────────────────────────────────────
// TJobReportItem
// ────────────────────────────────────────────────────────────────────

  TJobReportItem = class(TBaseReportItem)
  private
    FJobId: Integer;
    FJobCode: string;
    FDriverName: string;
    FVehicleReg: string;
    FRouteCode: string;
    FScheduledTime: TDateTime;
    FActualTime: TDateTime;
    FDelayMinutes: Integer;
    FPassengerCount: Integer;
    FDistanceKm: Double;
    FFuelLitres: Double;
    FCostTotal: Double;
  public
    constructor Create(AJobId: Integer);
    function GetDelayText: string;
    function GetEfficiencyScore: Double;
    function GetInfoText: string;
    property JobId: Integer read FJobId;
    property JobCode: string read FJobCode write FJobCode;
    property DriverName: string read FDriverName write FDriverName;
    property VehicleReg: string read FVehicleReg write FVehicleReg;
    property RouteCode: string read FRouteCode write FRouteCode;
    property ScheduledTime: TDateTime read FScheduledTime write FScheduledTime;
    property ActualTime: TDateTime read FActualTime write FActualTime;
    property DelayMinutes: Integer read FDelayMinutes write FDelayMinutes;
    property PassengerCount: Integer read FPassengerCount write FPassengerCount;
    property DistanceKm: Double read FDistanceKm write FDistanceKm;
    property FuelLitres: Double read FFuelLitres write FFuelLitres;
    property CostTotal: Double read FCostTotal write FCostTotal;
  end;

  TJobReportList = class(TObjectList<TJobReportItem>)
  public
    function FindByJobCode(const ACode: string): TJobReportItem;
    function FilterByDriver(const ADriverName: string): TJobReportList;
    function FilterByDateRange(AFrom, ATo: TDateTime): TJobReportList;
    function GetTotalDistance: Double;
    function GetTotalPassengers: Integer;
    function GetTotalCost: Double;
    function GetAverageDelay: Double;
    procedure SortByScheduledTime;
    procedure SortByDelayDescending;
  end;

// ────────────────────────────────────────────────────────────────────
// TDriverPayReport
// ────────────────────────────────────────────────────────────────────

  TDriverPayReport = class(TBaseReportItem)
  private
    FDriverId: Integer;
    FDriverName: string;
    FEmployeeCode: string;
    FFromDate: TDateTime;
    FToDate: TDateTime;
    FTotalTrips: Integer;
    FTotalHours: Double;
    FTotalKm: Double;
    FBasePay: Double;
    FKmAllowance: Double;
    FOvertimePay: Double;
    FDeductions: Double;
    FNetPay: Double;
  public
    constructor Create(ADriverId: Integer);
    function GetGrossPay: Double;
    function GetPaySummaryText: string;
    function GetHourlyRate: Double;
    property DriverId: Integer read FDriverId;
    property DriverName: string read FDriverName write FDriverName;
    property EmployeeCode: string read FEmployeeCode write FEmployeeCode;
    property FromDate: TDateTime read FFromDate write FFromDate;
    property ToDate: TDateTime read FToDate write FToDate;
    property TotalTrips: Integer read FTotalTrips write FTotalTrips;
    property TotalHours: Double read FTotalHours write FTotalHours;
    property TotalKm: Double read FTotalKm write FTotalKm;
    property BasePay: Double read FBasePay write FBasePay;
    property KmAllowance: Double read FKmAllowance write FKmAllowance;
    property OvertimePay: Double read FOvertimePay write FOvertimePay;
    property Deductions: Double read FDeductions write FDeductions;
    property NetPay: Double read FNetPay write FNetPay;
  end;

// ────────────────────────────────────────────────────────────────────
// TFuelCostReport
// ────────────────────────────────────────────────────────────────────

  TFuelCostReport = class(TBaseReportItem)
  private
    FVehicleId: Integer;
    FVehicleReg: string;
    FVehicleType: string;
    FFromDate: TDateTime;
    FToDate: TDateTime;
    FTotalFillUps: Integer;
    FTotalLitres: Double;
    FTotalCost: Double;
    FAvgPricePerLitre: Double;
    FTotalKm: Double;
    FConsumptionRatePer100Km: Double;
    FCostPerKm: Double;
  public
    constructor Create(AVehicleId: Integer);
    function GetCostSummaryText: string;
    function IsHighConsumption: Boolean;
    property VehicleId: Integer read FVehicleId;
    property VehicleReg: string read FVehicleReg write FVehicleReg;
    property VehicleType: string read FVehicleType write FVehicleType;
    property FromDate: TDateTime read FFromDate write FFromDate;
    property ToDate: TDateTime read FToDate write FToDate;
    property TotalFillUps: Integer read FTotalFillUps write FTotalFillUps;
    property TotalLitres: Double read FTotalLitres write FTotalLitres;
    property TotalCost: Double read FTotalCost write FTotalCost;
    property AvgPricePerLitre: Double read FAvgPricePerLitre write FAvgPricePerLitre;
    property TotalKm: Double read FTotalKm write FTotalKm;
    property ConsumptionRatePer100Km: Double read FConsumptionRatePer100Km
      write FConsumptionRatePer100Km;
    property CostPerKm: Double read FCostPerKm write FCostPerKm;
  end;

implementation

// ── TJobReportItem ────────────────────────────────────────────────────

constructor TJobReportItem.Create(AJobId: Integer);
begin
  inherited Create;
  FJobId := AJobId;
  FDelayMinutes := 0;
  FPassengerCount := 0;
  FDistanceKm := 0;
  FFuelLitres := 0;
  FCostTotal := 0;
end;

function TJobReportItem.GetDelayText: string;
begin
  if FDelayMinutes = 0 then
    Result := 'On time'
  else if FDelayMinutes > 0 then
    Result := IntToStr(FDelayMinutes) + ' min late'
  else
    Result := IntToStr(Abs(FDelayMinutes)) + ' min early';
end;

function TJobReportItem.GetEfficiencyScore: Double;
begin
  // Score 0-100 based on delay, fuel, passenger load
  if FDistanceKm > 0 then
    Result := Max(0, 100 - (FDelayMinutes * 2) - (FFuelLitres / FDistanceKm * 100 - 8) * 5)
  else
    Result := 0;
end;

function TJobReportItem.GetInfoText: string;
begin
  Result := Format('Job %s | %s | Route %s | %s | %d pax | %.1f km',
    [FJobCode, FDriverName, FRouteCode, GetDelayText, FPassengerCount, FDistanceKm]);
end;

// ── TJobReportList ────────────────────────────────────────────────────

function TJobReportList.FindByJobCode(const ACode: string): TJobReportItem;
var
  item: TJobReportItem;
begin
  Result := nil;
  for item in Self do
    if SameText(item.JobCode, ACode) then Exit(item);
end;

function TJobReportList.FilterByDriver(const ADriverName: string): TJobReportList;
var
  item: TJobReportItem;
begin
  Result := TJobReportList.Create(False);
  for item in Self do
    if SameText(item.DriverName, ADriverName) then Result.Add(item);
end;

function TJobReportList.FilterByDateRange(AFrom, ATo: TDateTime): TJobReportList;
var
  item: TJobReportItem;
begin
  Result := TJobReportList.Create(False);
  for item in Self do
    if (item.ScheduledTime >= AFrom) and (item.ScheduledTime <= ATo) then
      Result.Add(item);
end;

function TJobReportList.GetTotalDistance: Double;
var
  item: TJobReportItem;
begin
  Result := 0;
  for item in Self do Result := Result + item.DistanceKm;
end;

function TJobReportList.GetTotalPassengers: Integer;
var
  item: TJobReportItem;
begin
  Result := 0;
  for item in Self do Inc(Result, item.PassengerCount);
end;

function TJobReportList.GetTotalCost: Double;
var
  item: TJobReportItem;
begin
  Result := 0;
  for item in Self do Result := Result + item.CostTotal;
end;

function TJobReportList.GetAverageDelay: Double;
begin
  if Count > 0 then
  begin
    var total: Double := 0;
    var item: TJobReportItem;
    for item in Self do total := total + item.DelayMinutes;
    Result := total / Count;
  end
  else
    Result := 0;
end;

procedure TJobReportList.SortByScheduledTime;
begin
  Sort(TComparer<TJobReportItem>.Construct(
    function(const A, B: TJobReportItem): Integer
    begin
      if A.ScheduledTime < B.ScheduledTime then Result := -1
      else if A.ScheduledTime > B.ScheduledTime then Result := 1
      else Result := 0;
    end));
end;

procedure TJobReportList.SortByDelayDescending;
begin
  Sort(TComparer<TJobReportItem>.Construct(
    function(const A, B: TJobReportItem): Integer
    begin
      Result := B.DelayMinutes - A.DelayMinutes;
    end));
end;

// ── TDriverPayReport ─────────────────────────────────────────────────

constructor TDriverPayReport.Create(ADriverId: Integer);
begin
  inherited Create;
  FDriverId := ADriverId;
  FTotalTrips := 0;
  FTotalHours := 0;
  FTotalKm := 0;
  FBasePay := 0;
  FKmAllowance := 0;
  FOvertimePay := 0;
  FDeductions := 0;
  FNetPay := 0;
end;

function TDriverPayReport.GetGrossPay: Double;
begin
  Result := FBasePay + FKmAllowance + FOvertimePay;
end;

function TDriverPayReport.GetPaySummaryText: string;
begin
  Result := Format('%s (%s) | Trips: %d | Hours: %.1f | Km: %.0f | Net: %.2f',
    [FDriverName, FEmployeeCode, FTotalTrips, FTotalHours, FTotalKm, FNetPay]);
end;

function TDriverPayReport.GetHourlyRate: Double;
begin
  if FTotalHours > 0 then
    Result := GetGrossPay / FTotalHours
  else
    Result := 0;
end;

// ── TFuelCostReport ───────────────────────────────────────────────────

constructor TFuelCostReport.Create(AVehicleId: Integer);
begin
  inherited Create;
  FVehicleId := AVehicleId;
  FTotalFillUps := 0;
  FTotalLitres := 0;
  FTotalCost := 0;
  FAvgPricePerLitre := 0;
  FTotalKm := 0;
  FConsumptionRatePer100Km := 0;
  FCostPerKm := 0;
end;

function TFuelCostReport.GetCostSummaryText: string;
begin
  Result := Format('%s (%s) | Fill-ups: %d | Litres: %.1f | Cost: %.2f | %.2f L/100km',
    [FVehicleReg, FVehicleType, FTotalFillUps, FTotalLitres, FTotalCost,
     FConsumptionRatePer100Km]);
end;

function TFuelCostReport.IsHighConsumption: Boolean;
begin
  Result := FConsumptionRatePer100Km > HIGH_CONSUMPTION_THRESHOLD;
end;

end.
