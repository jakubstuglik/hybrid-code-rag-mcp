unit MainDataMod;

interface

uses
  SysUtils, Classes, WideStrings,
  DBClient, DB, SqlExpr, DSConnect,
  ServerMethods, GlobalTypes,
  Generics.Collections,
  IPPeerClient, Data.DBXCommon, Data.DbxHTTPLayer,
  KMDSPParams,
{$IFDEF USE_PIPES}
  Pipes,
{$ENDIF}
  UTForwardOnlyClientDataSet;

type

  TdmFleet = class(TDataModule)
    // ── Core connection ──────────────────────────────────────────────
    SQLConnection: TSQLConnection;
    DSProviderConnection: TDSProviderConnection;
    cdsStoredProcCustom1: TClientDataSet;
    cdsStoredProcCustom2: TClientDataSet;
    cdsStoredProcCustom3: TClientDataSet;
    cdsStoredProcCustom4: TClientDataSet;
    cdsStoredProcCustom5: TClientDataSet;
    cdsStoredProcCustom6: TClientDataSet;
    cdsStoredProcCustom7: TClientDataSet;
    cdsStoredProcAdmin_Log: TClientDataSet;
    cdsCommitAndResult: TClientDataSet;
    cdsStoredProcBasicSearch: TClientDataSet;

    // ── Vehicle datasets ─────────────────────────────────────────────
    cdsVehicles: TClientDataSet;
    cdsVehicleGroups: TClientDataSet;
    cdsVehicleTypes: TClientDataSet;
    cdsVehicleStatus: TClientDataSet;
    cdsVehicleHistory: TClientDataSet;
    cdsVehicleFuelTypes: TClientDataSet;
    cdsVehicleServiceRecords: TClientDataSet;
    cdsVehicleInspections: TClientDataSet;
    cdsVehicleInsurance: TClientDataSet;
    cdsVehicleDocuments: TClientDataSet;
    cdsVehicleAlerts: TClientDataSet;
    cdsVehicleGpsTrack: TClientDataSet;
    cdsVehicleOdometer: TClientDataSet;
    cdsVehicleAssignment: TClientDataSet;
    cdsVehicleMaintenance: TClientDataSet;
    cdsVehicleCompliance: TClientDataSet;
    cdsVehicleReplaceParts: TClientDataSet;
    cdsVehicleRepairOrders: TClientDataSet;
    cdsVehicleTachograph: TClientDataSet;
    cdsVehicleSpecifications: TClientDataSet;

    // ── Driver datasets ──────────────────────────────────────────────
    cdsDrivers: TClientDataSet;
    cdsDriverGroups: TClientDataSet;
    cdsDriverSchedule: TClientDataSet;
    cdsDriverLicences: TClientDataSet;
    cdsDriverHistory: TClientDataSet;
    cdsDriverPayroll: TClientDataSet;
    cdsDriverAssignment: TClientDataSet;
    cdsDriverTraining: TClientDataSet;
    cdsDriverMedical: TClientDataSet;
    cdsDriverPerformance: TClientDataSet;
    cdsDriverViolations: TClientDataSet;
    cdsDriverLeave: TClientDataSet;
    cdsDriverShifts: TClientDataSet;
    cdsDriverTachograph: TClientDataSet;
    cdsDriverCards: TClientDataSet;
    cdsDriverBonuses: TClientDataSet;
    cdsDriverDeductions: TClientDataSet;
    cdsDriverContracts: TClientDataSet;
    cdsDriverCertificates: TClientDataSet;
    cdsDriverEmergencyContacts: TClientDataSet;

    // ── Route / trip datasets ────────────────────────────────────────
    cdsRoutes: TClientDataSet;
    cdsRouteStops: TClientDataSet;
    cdsRouteCalendar: TClientDataSet;
    cdsTrips: TClientDataSet;
    cdsTripLog: TClientDataSet;
    cdsTripFuelConsumption: TClientDataSet;
    cdsTripDelay: TClientDataSet;
    cdsPlannedTrips: TClientDataSet;
    cdsCompletedTrips: TClientDataSet;
    cdsTripPassengers: TClientDataSet;
    cdsTripIncidents: TClientDataSet;
    cdsTripWaypoints: TClientDataSet;
    cdsRouteTimetable: TClientDataSet;
    cdsTripPayments: TClientDataSet;
    cdsTripDispatch: TClientDataSet;
    cdsTripVariances: TClientDataSet;
    cdsTripComments: TClientDataSet;
    cdsRouteVariants: TClientDataSet;
    cdsRouteMap: TClientDataSet;
    cdsTripBilling: TClientDataSet;

    // ── Job order datasets ───────────────────────────────────────────
    cdsJobOrders: TClientDataSet;
    cdsJobOrderItems: TClientDataSet;
    cdsJobOrderStatus: TClientDataSet;
    cdsJobDispatch: TClientDataSet;
    cdsJobDispatchHistory: TClientDataSet;
    cdsJobPriority: TClientDataSet;
    cdsJobTypes: TClientDataSet;
    cdsJobComments: TClientDataSet;
    cdsJobDocuments: TClientDataSet;
    cdsJobBilling: TClientDataSet;
    cdsJobTracking: TClientDataSet;
    cdsJobAlerts: TClientDataSet;
    cdsJobRecurring: TClientDataSet;
    cdsJobTemplates: TClientDataSet;
    cdsJobCalendar: TClientDataSet;

    // ── Location / geography ─────────────────────────────────────────
    cdsDepots: TClientDataSet;
    cdsDepotZones: TClientDataSet;
    cdsGeoPoints: TClientDataSet;
    cdsDistricts: TClientDataSet;
    cdsRegions: TClientDataSet;
    cdsCountries: TClientDataSet;
    cdsPostalCodes: TClientDataSet;
    cdsGeoFences: TClientDataSet;
    cdsBusStops: TClientDataSet;
    cdsWaypoints: TClientDataSet;
    cdsRoads: TClientDataSet;
    cdsMapLayers: TClientDataSet;
    cdsGpsHistory: TClientDataSet;
    cdsTollPoints: TClientDataSet;
    cdsRestrictions: TClientDataSet;

    // ── Fuel / costs ─────────────────────────────────────────────────
    cdsFuelPrices: TClientDataSet;
    cdsFuelTypes: TClientDataSet;
    cdsFuelSuppliers: TClientDataSet;
    cdsCostCentres: TClientDataSet;
    cdsCostAllocation: TClientDataSet;
    cdsFuelOrders: TClientDataSet;
    cdsMaintenanceCosts: TClientDataSet;
    cdsFuelBudgets: TClientDataSet;
    cdsFuelConsumption: TClientDataSet;
    cdsFuelReports: TClientDataSet;
    cdsFuelTankReadings: TClientDataSet;
    cdsCostAnalysis: TClientDataSet;
    cdsFuelCards: TClientDataSet;
    cdsFuelInvoices: TClientDataSet;
    cdsFuelReconciliation: TClientDataSet;

    // ── Customer / company ───────────────────────────────────────────
    cdsCustomers: TClientDataSet;
    cdsCustomerContracts: TClientDataSet;
    cdsCustomerInvoices: TClientDataSet;
    cdsCompanies: TClientDataSet;
    cdsCompanyBranches: TClientDataSet;
    cdsContacts: TClientDataSet;
    cdsCustomerRates: TClientDataSet;
    cdsCustomerDiscounts: TClientDataSet;
    cdsCustomerDocuments: TClientDataSet;
    cdsCustomerHistory: TClientDataSet;
    cdsContractLines: TClientDataSet;
    cdsCustomerPagination: TClientDataSet;
    cdsContractAmendments: TClientDataSet;
    cdsCustomerCreditNotes: TClientDataSet;
    cdsCustomerStatements: TClientDataSet;

    // ── Reports / analytics ──────────────────────────────────────────
    cdsReportDef: TClientDataSet;
    cdsReportParams: TClientDataSet;
    cdsReportResults: TClientDataSet;
    cdsReportSchedule: TClientDataSet;
    cdsKPIDaily: TClientDataSet;
    cdsKPIMonthly: TClientDataSet;
    cdsKPITargets: TClientDataSet;
    cdsDashboardData: TClientDataSet;
    cdsAnalysisData: TClientDataSet;
    cdsReportsPagination: TClientDataSet;

    // ── Audit / system ───────────────────────────────────────────────
    cdsAuditLog: TClientDataSet;
    cdsSystemSettings: TClientDataSet;
    cdsUserPermissions: TClientDataSet;
    cdsNotifications: TClientDataSet;
    cdsAlerts: TClientDataSet;
    cdsSystemUsers: TClientDataSet;
    cdsUserRoles: TClientDataSet;
    cdsUserGroups: TClientDataSet;
    cdsSessionLog: TClientDataSet;
    cdsChangeHistory: TClientDataSet;

    // ── Event handlers ───────────────────────────────────────────────
    procedure DataModuleCreate(Sender: TObject);
    procedure DataModuleDestroy(Sender: TObject);
    procedure SQLConnectionAfterConnect(Sender: TObject);
    procedure SQLConnectionBeforeDisconnect(Sender: TObject);
    procedure SQLConnectionValidatePeerCertificate(Owner: TObject; Certificate:
        TX509Certificate; const ADepth: Integer; var Ok: Boolean);

  private
    FTCPIPServerMethods: TdmTCPIPServerMethodsClient;
    FRemoteDataClient: TdmRemoteDataClient;
    FOnUserAfterLoginEvent: TUserAfterLoginEvent;
    fPrivileges: TObjectList<TObject>;
{$IFDEF USE_PIPES}
    fPipeServer: TPipeServer;
{$ENDIF}
    // Forward-only dataset for large report result sets
    cdsStoredProcReports: TForwardOnlyClientDataSet;

    procedure PreapreDataSet(ADataSet: TDataSet; Params: string); overload;
{$HINTS OFF}
    procedure PreapreDataSet(ADataSet: TDataSet; aDSPParams: TDSPParams); overload;
{$HINTS ON}
    procedure PreparePagination_BASE(AClientDataSet: TClientDataSet; const AParams: string);
    procedure PrepareVehicles(Params: string);
    procedure PrepareVehicleGroups(Params: string);
    procedure PrepareVehicleTypes(Params: string);
    procedure PrepareVehicleStatus(Params: string);
    procedure PrepareVehicleHistory(Params: string);
    procedure PrepareVehicleServiceRecords(Params: string);
    procedure PrepareVehicleInspections(Params: string);
    procedure PrepareVehicleMaintenance(Params: string);
    procedure PrepareVehicleCompliance(Params: string);
    procedure PrepareVehicleGpsTrack(AVehicleId: Integer);
    procedure PrepareVehicleAssignment(Params: string);
    procedure PrepareVehicleTachograph(AVehicleId: Integer);
    procedure PrepareDrivers(Params: string; TypeDS: Integer);
    procedure PrepareDriverGroups(Params: string);
    procedure PrepareDriverSchedule(Params: string);
    procedure PrepareDriverPayroll(AFromDate, AToDate: TDateTime; DriverId: Integer);
    procedure PrepareDriverTraining(Params: string);
    procedure PrepareDriverMedical(Params: string);
    procedure PrepareDriverViolations(Params: string);
    procedure PrepareDriverLeave(ADriverId: Integer; AFromDate, AToDate: TDateTime);
    procedure PrepareDriverShifts(Params: string);
    procedure PrepareDriverCertificates(Params: string);
    procedure PrepareRoutes(Params: string);
    procedure PrepareRouteStops(Params: string);
    procedure PrepareRouteCalendar(Params: string);
    procedure PrepareTrips(Params: string);
    procedure PrepareTripLog(ADataSet: TClientDataSet; AParams: string);
    procedure PrepareTripFuelConsumption(ATripId: Integer);
    procedure PrepareTripWaypoints(ATripId: Integer);
    procedure PrepareTripIncidents(ATripId: Integer);
    procedure PreparePlannedTrips(Params: string);
    procedure PrepareCompletedTrips(Params: string);
    procedure PrepareJobOrders(Params: string);
    procedure PrepareJobDispatch(Params: string);
    procedure PrepareJobDispatchHistory(Params: string);
    procedure PrepareJobTracking(AJobId: Integer);
    procedure PrepareJobBilling(AJobId: Integer);
    procedure PrepareDepots(Params: string);
    procedure PrepareDepotZones(ADepotId: Integer);
    procedure PrepareGeoPoints(Params: string);
    procedure PrepareGeoFences(Params: string);
    procedure PrepareGpsHistory(AParams: string);
    procedure PrepareBusStops(Params: string);
    procedure PrepareTollPoints(Params: string);
    procedure PrepareFuelPrices(Params: string);
    procedure PrepareFuelConsumption(Params: string);
    procedure PrepareFuelOrders(Params: string);
    procedure PrepareFuelInvoices(Params: string);
    procedure PrepareMaintenanceCosts(Params: string);
    procedure PrepareCostCentres(Params: string);
    procedure PrepareCostAllocation(Params: string);
    procedure PrepareCustomers(Params: string);
    procedure PrepareCustomerContracts(Params: string);
    procedure PrepareCustomerInvoices(Params: string);
    procedure PrepareCustomerRates(ACustomerId: Integer);
    procedure PrepareCustomerHistory(Params: string);
    procedure PrepareContractAmendments(AContractId: Integer);
    procedure PrepareCompanyBranches(Params: string);
    procedure PrepareReportDef(Params: string);
    procedure PrepareReportDefType(AParams: string);
    procedure PrepareReportResults(AParams: string);
    procedure PrepareReportSchedule(Params: string);
    procedure PrepareKPIData(AParams: string);
    procedure PrepareKPITargets(AParams: string);
    procedure PrepareDashboardData(AUserId: Integer);
    procedure PrepareAuditLog(Params: string);
    procedure PrepareSystemSettings(Params: string);
    procedure PrepareUserPermissions(Params: string);
    procedure PrepareAlerts(AParams: string);
    procedure PrepareNotifications(AParams: string);
    procedure PrepareBasicSearch(Params: string); overload;
    procedure PrepareBasicSearch(ADataSet: TClientDataSet; Params: string); overload;
    procedure PrepareVehiclesPagination(AParams: string);
    procedure PrepareDriversPagination(AParams: string);
    procedure PrepareJobOrdersPagination(AParams: string);
    procedure PrepareCustomersPagination(AParams: string);
    procedure PrepareRoutePagination(AParams: string);
    procedure PrepareTachographData(AVehicleId: Integer);

    function GetPrivileges: TObjectList<TObject>;
    procedure SetPrivileges(const Value: TObjectList<TObject>);
    function GetCdsReports(const aDesiredPacketRecords: Integer;
      const aInitialPacketRecords: Integer): TForwardOnlyClientDataSet;

  public
    const REPORTS_DS_DEFAULT_FETCH_SIZE = 1000;

    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;

    procedure cdsStoredProcAfterOpen(DataSet: TDataSet);
    function GetClientDataSet(aTag: integer): TClientDataSet;

    // Connection management
    function OpenConnection: boolean;
    function CloseConnection: boolean;
    function TestConnection: boolean;
    procedure CloseDatasets;
    procedure ReconnectIfNeeded;

    // StoredProc open/close
    function StoredProcOpen(SchemaName, StoredProcName,
      Params: string; Tag: Integer;
      const aParametersSeparator: string = #13#10;
      const aLineBreak: string = #13): boolean; overload;
    function StoredProcOpen(aClientDataSet: TClientDataSet; Params: string;
      const aParametersSeparator: string = #13#10;
      const aLineBreak: string = #13): boolean; overload;
    function StoredProcOpen(SchemaName, StoredProcName: string; Params: TStringList;
      Tag: Integer;
      const aParametersSeparator: string = #13#10;
      const aLineBreak: string = #13): boolean; overload;
    function StoredProcReportsOpen(SchemaName, StoredProcName, Params: string;
      const aDesiredPacketRecords: Integer = REPORTS_DS_DEFAULT_FETCH_SIZE;
      const aInitialPacketRecords: Integer = -1;
      const aParametersSeparator: string = #13#10;
      const aLineBreak: string = #13): boolean;
    function StoredProcClose(Tag: Integer): boolean; overload;
    function StoredProcClose(DS: TDataSet): boolean; overload;
    function StoredProcReportsClose: boolean;

    // DataSet operations
    function DataSetOpen(ADataSet: TDataSet; Params: string = ''): boolean; overload;
    function DataSetOpen(ADataSet: TDataSet; aDSPParams: TDSPParams): boolean; overload;
    function DataSetOpen(ADataSet: TDataSet; Params: string;
      SchemaName: string; StoredProcName: string): boolean; overload;
    procedure DataSetClose(ADataSet: TDataSet);
    function DataSetRequery(ADataSet: TDataSet; Params: string = ''): Boolean; overload;
    function DataSetRequery(ADataSet: TDataSet; aDSPParams: TDSPParams): Boolean; overload;
    function DBOpenCustomSQL(ADataSet: TDataSet; ACustomSQL: string = ''): boolean;

    // Transactions
    function DBTransBegin: string;
    function DBTransStoredProc(Guid, SchemaName, StoredProcName, Params: string;
      AResultIndex: Integer;
      AScriptGlobalParamName, AStoredProcOutParamName: string;
      const ARunPriority: Integer): string;
    function DBTransCommit(Guid: string): boolean;
    function DBTransRollback(Guid: string): boolean;
    function DBTransScript(Guid, Script: string; const ARunPriority: Integer): Integer;
    function DBTransCommitAndResult(Guid: string): boolean;
    function DBTransResultClose: boolean;

    // DB stored functions
    function StoredFunc(SchemaName, StoredProcName, Params: string;
      aParametersSeparator: string = #13#10; aLineBreak: string = #13): string;
    function StoredProc(SchemaName, StoredProcName, Params: string): Integer;

    // File I/O
    function ReadFile(aFileStream: TStream; aFileName, AGuid, ASubdir: string): boolean;
    function SaveFile(aFileStream: TMemoryStream; aFileName, AGuid, ASubdir: string): boolean;
    function ReadDriverFile(aFileStream: TStream; aFileName, ASubDir: string): boolean;
    function SaveDriverFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReplaceDriverFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReadVehicleFile(aFileStream: TStream; aFileName, ASubDir: string): boolean;
    function SaveVehicleFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReplaceVehicleFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReadJobFile(aFileStream: TStream; aFileName, ASubDir: string): boolean;
    function SaveJobFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReadReportFile(aFileStream: TStream; aFileName, ASubDir: string): boolean;
    function SaveReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function ReplaceReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: string): boolean;
    function NextDriverFileName(ADriverId: Int64; AYear: SmallInt;
      AMonth, ADay: Byte; ADepot_ID: Integer): string;

    // Admin log
    function ADMIN_LogOpen(ProcName: string; DataOd, DataDo: TDate; Key_Id: Integer): boolean;
    function ADMIN_LogClose: boolean;

    // User / auth
    function UserLogin(aId: integer; AOnUserLoginProc: TOnUserLoginProc): boolean;
    procedure UserAfterLogin(Sender, AUser: TObject; var ALogged: boolean;
      var AMessage: string);
    function LogonAndCheckForceLogoff: Boolean;
    function GetServerVersion: string;

    // Misc
    procedure SendDebugPipeMessage(aMessage: string);
    function DataSnapConnectionCount: Integer;

    property Privileges: TObjectList<TObject>
      read   GetPrivileges
      write  SetPrivileges;
  end;

var
  dmFleet: TdmFleet;

implementation

{$R *.dfm}

uses
  Dialogs, AppConst, FileUtils, GlobalTypes;

// ────────────────────────────────────────────────────────────────────
// Lifecycle
// ────────────────────────────────────────────────────────────────────

constructor TdmFleet.Create(AOwner: TComponent);
begin
  inherited Create(AOwner);
  fPrivileges := TObjectList<TObject>.Create(True);
end;

destructor TdmFleet.Destroy;
begin
  fPrivileges.Free;
  inherited;
end;

procedure TdmFleet.DataModuleCreate(Sender: TObject);
begin
  FTCPIPServerMethods := nil;
  FRemoteDataClient := nil;
  cdsStoredProcReports := nil;
end;

procedure TdmFleet.DataModuleDestroy(Sender: TObject);
begin
  if cdsStoredProcReports <> nil then
  begin
    cdsStoredProcReports.Close;
    FreeAndNil(cdsStoredProcReports);
  end;
  if FTCPIPServerMethods <> nil then
    FreeAndNil(FTCPIPServerMethods);
end;

// ────────────────────────────────────────────────────────────────────
// Connection management
// ────────────────────────────────────────────────────────────────────

function TdmFleet.OpenConnection: boolean;
begin
  Result := False;
  try
    if not SQLConnection.Connected then
      SQLConnection.Open;
    Result := SQLConnection.Connected;
  except
    on E: Exception do
      raise Exception.CreateFmt('OpenConnection failed: %s', [E.Message]);
  end;
end;

function TdmFleet.CloseConnection: boolean;
begin
  Result := False;
  try
    CloseDatasets;
    if SQLConnection.Connected then
      SQLConnection.Close;
    Result := not SQLConnection.Connected;
  except
    on E: Exception do
      raise;
  end;
end;

function TdmFleet.TestConnection: boolean;
begin
  Result := SQLConnection.Connected;
end;

procedure TdmFleet.CloseDatasets;
var
  i: Integer;
begin
  for i := 0 to ComponentCount - 1 do
    if Components[i] is TClientDataSet then
      TClientDataSet(Components[i]).Close;
end;

procedure TdmFleet.ReconnectIfNeeded;
begin
  if not SQLConnection.Connected then
    OpenConnection;
end;

procedure TdmFleet.SQLConnectionAfterConnect(Sender: TObject);
begin
  StoredProc('dbo', 'sp_setapprole',
    'rolename=' + APP_ROLE_NAME + #13#10 +
    'password=' + APP_ROLE_PASSWORD + #13#10 +
    'fCreateCookie=none' + #13#10 +
    'encrypt=1');
end;

procedure TdmFleet.SQLConnectionBeforeDisconnect(Sender: TObject);
begin
  CloseDatasets;
end;

procedure TdmFleet.SQLConnectionValidatePeerCertificate(Owner: TObject;
  Certificate: TX509Certificate; const ADepth: Integer; var Ok: Boolean);
begin
  Ok := True;
end;

function TdmFleet.GetServerVersion: string;
var
  v: Variant;
begin
  v := StoredFunc('dbo', 'fn_GetVersion', '');
  if VarIsNull(v) then
    Result := 'Unknown'
  else
    Result := string(v);
end;

// ────────────────────────────────────────────────────────────────────
// PreapreDataSet (intentional typo preserved from original codebase)
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PreapreDataSet(ADataSet: TDataSet; Params: string);
begin
  if ADataSet = cdsVehicles then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleGroups then PrepareVehicleGroups(Params)
  else if ADataSet = cdsVehicleTypes then PrepareVehicleTypes(Params)
  else if ADataSet = cdsVehicleStatus then PrepareVehicleStatus(Params)
  else if ADataSet = cdsVehicleHistory then PrepareVehicleHistory(Params)
  else if ADataSet = cdsVehicleFuelTypes then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleServiceRecords then PrepareVehicleServiceRecords(Params)
  else if ADataSet = cdsVehicleInspections then PrepareVehicleInspections(Params)
  else if ADataSet = cdsVehicleInsurance then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleDocuments then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleAlerts then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleGpsTrack then PrepareVehicleGpsTrack(0)
  else if ADataSet = cdsVehicleOdometer then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleAssignment then PrepareVehicleAssignment(Params)
  else if ADataSet = cdsVehicleMaintenance then PrepareVehicleMaintenance(Params)
  else if ADataSet = cdsVehicleCompliance then PrepareVehicleCompliance(Params)
  else if ADataSet = cdsVehicleReplaceParts then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleRepairOrders then PrepareVehicles(Params)
  else if ADataSet = cdsVehicleTachograph then PrepareVehicleTachograph(0)
  else if ADataSet = cdsVehicleSpecifications then PrepareVehicles(Params)
  else if ADataSet = cdsDrivers then PrepareDrivers(Params, 0)
  else if ADataSet = cdsDriverGroups then PrepareDriverGroups(Params)
  else if ADataSet = cdsDriverSchedule then PrepareDriverSchedule(Params)
  else if ADataSet = cdsDriverLicences then PrepareDrivers(Params, 1)
  else if ADataSet = cdsDriverHistory then PrepareDrivers(Params, 2)
  else if ADataSet = cdsDriverPayroll then PrepareDriverPayroll(0, 0, 0)
  else if ADataSet = cdsDriverAssignment then PrepareDrivers(Params, 0)
  else if ADataSet = cdsDriverTraining then PrepareDriverTraining(Params)
  else if ADataSet = cdsDriverMedical then PrepareDriverMedical(Params)
  else if ADataSet = cdsDriverPerformance then PrepareDrivers(Params, 3)
  else if ADataSet = cdsDriverViolations then PrepareDriverViolations(Params)
  else if ADataSet = cdsDriverLeave then PrepareDriverLeave(0, 0, 0)
  else if ADataSet = cdsDriverShifts then PrepareDriverShifts(Params)
  else if ADataSet = cdsDriverTachograph then PrepareDrivers(Params, 4)
  else if ADataSet = cdsDriverCards then PrepareDrivers(Params, 5)
  else if ADataSet = cdsDriverBonuses then PrepareDrivers(Params, 6)
  else if ADataSet = cdsDriverDeductions then PrepareDrivers(Params, 7)
  else if ADataSet = cdsDriverContracts then PrepareDrivers(Params, 8)
  else if ADataSet = cdsDriverCertificates then PrepareDriverCertificates(Params)
  else if ADataSet = cdsDriverEmergencyContacts then PrepareDrivers(Params, 9)
  else if ADataSet = cdsRoutes then PrepareRoutes(Params)
  else if ADataSet = cdsRouteStops then PrepareRouteStops(Params)
  else if ADataSet = cdsRouteCalendar then PrepareRouteCalendar(Params)
  else if ADataSet = cdsTrips then PrepareTrips(Params)
  else if ADataSet = cdsTripLog then PrepareTripLog(cdsTripLog, Params)
  else if ADataSet = cdsTripFuelConsumption then PrepareTripFuelConsumption(0)
  else if ADataSet = cdsTripDelay then PrepareTrips(Params)
  else if ADataSet = cdsPlannedTrips then PreparePlannedTrips(Params)
  else if ADataSet = cdsCompletedTrips then PrepareCompletedTrips(Params)
  else if ADataSet = cdsTripPassengers then PrepareTrips(Params)
  else if ADataSet = cdsTripIncidents then PrepareTripIncidents(0)
  else if ADataSet = cdsTripWaypoints then PrepareTripWaypoints(0)
  else if ADataSet = cdsRouteTimetable then PrepareRoutes(Params)
  else if ADataSet = cdsTripPayments then PrepareTrips(Params)
  else if ADataSet = cdsTripDispatch then PrepareJobDispatch(Params)
  else if ADataSet = cdsTripVariances then PrepareTrips(Params)
  else if ADataSet = cdsTripComments then PrepareTrips(Params)
  else if ADataSet = cdsRouteVariants then PrepareRoutes(Params)
  else if ADataSet = cdsRouteMap then PrepareRoutes(Params)
  else if ADataSet = cdsTripBilling then PrepareTrips(Params)
  else if ADataSet = cdsJobOrders then PrepareJobOrders(Params)
  else if ADataSet = cdsJobOrderItems then PrepareJobOrders(Params)
  else if ADataSet = cdsJobOrderStatus then PrepareJobOrders(Params)
  else if ADataSet = cdsJobDispatch then PrepareJobDispatch(Params)
  else if ADataSet = cdsJobDispatchHistory then PrepareJobDispatchHistory(Params)
  else if ADataSet = cdsJobPriority then PrepareJobOrders(Params)
  else if ADataSet = cdsJobTypes then PrepareJobOrders(Params)
  else if ADataSet = cdsJobComments then PrepareJobOrders(Params)
  else if ADataSet = cdsJobDocuments then PrepareJobOrders(Params)
  else if ADataSet = cdsJobBilling then PrepareJobBilling(0)
  else if ADataSet = cdsJobTracking then PrepareJobTracking(0)
  else if ADataSet = cdsJobAlerts then PrepareJobOrders(Params)
  else if ADataSet = cdsJobRecurring then PrepareJobOrders(Params)
  else if ADataSet = cdsJobTemplates then PrepareJobOrders(Params)
  else if ADataSet = cdsJobCalendar then PrepareJobOrders(Params)
  else if ADataSet = cdsDepots then PrepareDepots(Params)
  else if ADataSet = cdsDepotZones then PrepareDepotZones(0)
  else if ADataSet = cdsGeoPoints then PrepareGeoPoints(Params)
  else if ADataSet = cdsDistricts then PrepareGeoPoints(Params)
  else if ADataSet = cdsRegions then PrepareGeoPoints(Params)
  else if ADataSet = cdsCountries then PrepareGeoPoints(Params)
  else if ADataSet = cdsPostalCodes then PrepareGeoPoints(Params)
  else if ADataSet = cdsGeoFences then PrepareGeoFences(Params)
  else if ADataSet = cdsBusStops then PrepareBusStops(Params)
  else if ADataSet = cdsWaypoints then PrepareGeoPoints(Params)
  else if ADataSet = cdsRoads then PrepareGeoPoints(Params)
  else if ADataSet = cdsMapLayers then PrepareGeoPoints(Params)
  else if ADataSet = cdsGpsHistory then PrepareGpsHistory(Params)
  else if ADataSet = cdsTollPoints then PrepareTollPoints(Params)
  else if ADataSet = cdsRestrictions then PrepareGeoPoints(Params)
  else if ADataSet = cdsFuelPrices then PrepareFuelPrices(Params)
  else if ADataSet = cdsFuelTypes then PrepareFuelPrices(Params)
  else if ADataSet = cdsFuelSuppliers then PrepareFuelPrices(Params)
  else if ADataSet = cdsCostCentres then PrepareCostCentres(Params)
  else if ADataSet = cdsCostAllocation then PrepareCostAllocation(Params)
  else if ADataSet = cdsFuelOrders then PrepareFuelOrders(Params)
  else if ADataSet = cdsMaintenanceCosts then PrepareMaintenanceCosts(Params)
  else if ADataSet = cdsFuelBudgets then PrepareFuelPrices(Params)
  else if ADataSet = cdsFuelConsumption then PrepareFuelConsumption(Params)
  else if ADataSet = cdsFuelReports then PrepareFuelPrices(Params)
  else if ADataSet = cdsFuelTankReadings then PrepareFuelPrices(Params)
  else if ADataSet = cdsCostAnalysis then PrepareCostAllocation(Params)
  else if ADataSet = cdsFuelCards then PrepareFuelPrices(Params)
  else if ADataSet = cdsFuelInvoices then PrepareFuelInvoices(Params)
  else if ADataSet = cdsFuelReconciliation then PrepareFuelPrices(Params)
  else if ADataSet = cdsCustomers then PrepareCustomers(Params)
  else if ADataSet = cdsCustomerContracts then PrepareCustomerContracts(Params)
  else if ADataSet = cdsCustomerInvoices then PrepareCustomerInvoices(Params)
  else if ADataSet = cdsCompanies then PrepareCustomers(Params)
  else if ADataSet = cdsCompanyBranches then PrepareCompanyBranches(Params)
  else if ADataSet = cdsContacts then PrepareCustomers(Params)
  else if ADataSet = cdsCustomerRates then PrepareCustomerRates(0)
  else if ADataSet = cdsCustomerDiscounts then PrepareCustomers(Params)
  else if ADataSet = cdsCustomerDocuments then PrepareCustomers(Params)
  else if ADataSet = cdsCustomerHistory then PrepareCustomerHistory(Params)
  else if ADataSet = cdsContractLines then PrepareCustomerContracts(Params)
  else if ADataSet = cdsContractAmendments then PrepareContractAmendments(0)
  else if ADataSet = cdsCustomerCreditNotes then PrepareCustomers(Params)
  else if ADataSet = cdsCustomerStatements then PrepareCustomers(Params)
  else if ADataSet = cdsReportDef then PrepareReportDef(Params)
  else if ADataSet = cdsReportParams then PrepareReportDef(Params)
  else if ADataSet = cdsReportResults then PrepareReportResults(Params)
  else if ADataSet = cdsReportSchedule then PrepareReportSchedule(Params)
  else if ADataSet = cdsKPIDaily then PrepareKPIData(Params)
  else if ADataSet = cdsKPIMonthly then PrepareKPIData(Params)
  else if ADataSet = cdsKPITargets then PrepareKPITargets(Params)
  else if ADataSet = cdsDashboardData then PrepareDashboardData(0)
  else if ADataSet = cdsAnalysisData then PrepareKPIData(Params)
  else if ADataSet = cdsReportsPagination then PrepareReportDef(Params)
  else if ADataSet = cdsAuditLog then PrepareAuditLog(Params)
  else if ADataSet = cdsSystemSettings then PrepareSystemSettings(Params)
  else if ADataSet = cdsUserPermissions then PrepareUserPermissions(Params)
  else if ADataSet = cdsNotifications then PrepareNotifications(Params)
  else if ADataSet = cdsAlerts then PrepareAlerts(Params)
  else if ADataSet = cdsSystemUsers then PrepareUserPermissions(Params)
  else if ADataSet = cdsUserRoles then PrepareUserPermissions(Params)
  else if ADataSet = cdsUserGroups then PrepareUserPermissions(Params)
  else if ADataSet = cdsSessionLog then PrepareAuditLog(Params)
  else if ADataSet = cdsChangeHistory then PrepareAuditLog(Params)
  else
    DataSetOpen(ADataSet, Params);
end;

procedure TdmFleet.PreapreDataSet(ADataSet: TDataSet; aDSPParams: TDSPParams);
begin
  PreapreDataSet(ADataSet, aDSPParams.AsString);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Vehicle group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareVehicles(Params: string);
begin
  cdsVehicles.Close;
  cdsVehicles.CommandText := 'VEH_GetAll';
  if Params <> '' then
    DataSetOpen(cdsVehicles, Params)
  else
    cdsVehicles.Open;
end;

procedure TdmFleet.PrepareVehicleGroups(Params: string);
begin
  cdsVehicleGroups.Close;
  cdsVehicleGroups.CommandText := 'VEH_GetGroups';
  DataSetOpen(cdsVehicleGroups, Params);
end;

procedure TdmFleet.PrepareVehicleTypes(Params: string);
begin
  cdsVehicleTypes.Close;
  cdsVehicleTypes.CommandText := 'VEH_GetTypes';
  DataSetOpen(cdsVehicleTypes, Params);
end;

procedure TdmFleet.PrepareVehicleStatus(Params: string);
begin
  cdsVehicleStatus.Close;
  cdsVehicleStatus.CommandText := 'VEH_GetStatus';
  DataSetOpen(cdsVehicleStatus, Params);
end;

procedure TdmFleet.PrepareVehicleHistory(Params: string);
begin
  cdsVehicleHistory.Close;
  cdsVehicleHistory.CommandText := 'VEH_GetHistory';
  if Params = '' then
    raise Exception.Create('PrepareVehicleHistory: Params required');
  DataSetOpen(cdsVehicleHistory, Params);
end;

procedure TdmFleet.PrepareVehicleServiceRecords(Params: string);
begin
  cdsVehicleServiceRecords.Close;
  cdsVehicleServiceRecords.CommandText := 'VEH_ServiceRecord_GetAll';
  DataSetOpen(cdsVehicleServiceRecords, Params);
end;

procedure TdmFleet.PrepareVehicleInspections(Params: string);
begin
  cdsVehicleInspections.Close;
  cdsVehicleInspections.CommandText := 'VEH_Inspection_GetAll';
  DataSetOpen(cdsVehicleInspections, Params);
end;

procedure TdmFleet.PrepareVehicleMaintenance(Params: string);
begin
  cdsVehicleMaintenance.Close;
  cdsVehicleMaintenance.CommandText := 'VEH_Maintenance_GetAll';
  DataSetOpen(cdsVehicleMaintenance, Params);
end;

procedure TdmFleet.PrepareVehicleCompliance(Params: string);
begin
  cdsVehicleCompliance.Close;
  cdsVehicleCompliance.CommandText := 'VEH_Compliance_GetAll';
  DataSetOpen(cdsVehicleCompliance, Params);
end;

procedure TdmFleet.PrepareVehicleGpsTrack(AVehicleId: Integer);
begin
  cdsVehicleGpsTrack.Close;
  cdsVehicleGpsTrack.CommandText := 'VEH_GpsTrack_Get';
  DataSetOpen(cdsVehicleGpsTrack,
    'vehicle_id=' + IntToStr(AVehicleId));
end;

procedure TdmFleet.PrepareVehicleAssignment(Params: string);
begin
  cdsVehicleAssignment.Close;
  cdsVehicleAssignment.CommandText := 'VEH_Assignment_GetAll';
  DataSetOpen(cdsVehicleAssignment, Params);
end;

procedure TdmFleet.PrepareVehicleTachograph(AVehicleId: Integer);
begin
  cdsVehicleTachograph.Close;
  cdsVehicleTachograph.CommandText := 'VEH_Tachograph_Get';
  DataSetOpen(cdsVehicleTachograph,
    'vehicle_id=' + IntToStr(AVehicleId));
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Driver group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareDrivers(Params: string; TypeDS: Integer);
const
  PROC_NAMES: array[0..9] of string = (
    'DRV_GetAll',           // 0 — base list
    'DRV_GetLicences',      // 1
    'DRV_GetHistory',       // 2
    'DRV_GetPerformance',   // 3
    'DRV_GetTachograph',    // 4
    'DRV_GetCards',         // 5
    'DRV_GetBonuses',       // 6
    'DRV_GetDeductions',    // 7
    'DRV_GetContracts',     // 8
    'DRV_GetEmergencyContacts' // 9
  );
begin
  cdsDrivers.Close;
  cdsDrivers.CommandText := PROC_NAMES[TypeDS];
  DataSetOpen(cdsDrivers, Params);
end;

procedure TdmFleet.PrepareDriverGroups(Params: string);
begin
  cdsDriverGroups.Close;
  cdsDriverGroups.CommandText := 'DRV_GetGroups';
  DataSetOpen(cdsDriverGroups, Params);
end;

procedure TdmFleet.PrepareDriverSchedule(Params: string);
begin
  cdsDriverSchedule.Close;
  cdsDriverSchedule.CommandText := 'DRV_Schedule_GetAll';
  DataSetOpen(cdsDriverSchedule, Params);
end;

procedure TdmFleet.PrepareDriverPayroll(AFromDate, AToDate: TDateTime; DriverId: Integer);
var
  sParams: string;
begin
  cdsDriverPayroll.Close;
  cdsDriverPayroll.CommandText := 'DRV_Payroll_Get';
  sParams :=
    'from_date=' + DateToStr(AFromDate) + #13#10 +
    'to_date='   + DateToStr(AToDate)   + #13#10 +
    'driver_id=' + IntToStr(DriverId);
  DataSetOpen(cdsDriverPayroll, sParams);
end;

procedure TdmFleet.PrepareDriverTraining(Params: string);
begin
  cdsDriverTraining.Close;
  cdsDriverTraining.CommandText := 'DRV_Training_GetAll';
  DataSetOpen(cdsDriverTraining, Params);
end;

procedure TdmFleet.PrepareDriverMedical(Params: string);
begin
  cdsDriverMedical.Close;
  cdsDriverMedical.CommandText := 'DRV_Medical_GetAll';
  DataSetOpen(cdsDriverMedical, Params);
end;

procedure TdmFleet.PrepareDriverViolations(Params: string);
begin
  cdsDriverViolations.Close;
  cdsDriverViolations.CommandText := 'DRV_Violations_GetAll';
  DataSetOpen(cdsDriverViolations, Params);
end;

procedure TdmFleet.PrepareDriverLeave(ADriverId: Integer;
  AFromDate, AToDate: TDateTime);
var
  sParams: string;
begin
  cdsDriverLeave.Close;
  cdsDriverLeave.CommandText := 'DRV_Leave_Get';
  sParams :=
    'driver_id=' + IntToStr(ADriverId)  + #13#10 +
    'from_date=' + DateToStr(AFromDate) + #13#10 +
    'to_date='   + DateToStr(AToDate);
  DataSetOpen(cdsDriverLeave, sParams);
end;

procedure TdmFleet.PrepareDriverShifts(Params: string);
begin
  cdsDriverShifts.Close;
  cdsDriverShifts.CommandText := 'DRV_Shifts_GetAll';
  DataSetOpen(cdsDriverShifts, Params);
end;

procedure TdmFleet.PrepareDriverCertificates(Params: string);
begin
  cdsDriverCertificates.Close;
  cdsDriverCertificates.CommandText := 'DRV_Certificates_GetAll';
  DataSetOpen(cdsDriverCertificates, Params);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Route / trip group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareRoutes(Params: string);
begin
  cdsRoutes.Close;
  cdsRoutes.CommandText := 'RTE_GetAll';
  DataSetOpen(cdsRoutes, Params);
end;

procedure TdmFleet.PrepareRouteStops(Params: string);
begin
  cdsRouteStops.Close;
  cdsRouteStops.CommandText := 'RTE_Stops_GetAll';
  if Params = '' then
    raise Exception.Create('PrepareRouteStops: route_id required');
  DataSetOpen(cdsRouteStops, Params);
end;

procedure TdmFleet.PrepareRouteCalendar(Params: string);
begin
  cdsRouteCalendar.Close;
  cdsRouteCalendar.CommandText := 'RTE_Calendar_Get';
  DataSetOpen(cdsRouteCalendar, Params);
end;

procedure TdmFleet.PrepareTrips(Params: string);
begin
  cdsTrips.Close;
  cdsTrips.CommandText := 'TRP_GetAll';
  DataSetOpen(cdsTrips, Params);
end;

procedure TdmFleet.PrepareTripLog(ADataSet: TClientDataSet; AParams: string);
begin
  ADataSet.Close;
  ADataSet.CommandText := 'TRP_Log_Get';
  if AParams = '' then
    raise Exception.Create('PrepareTripLog: trip_id required');
  DataSetOpen(ADataSet, AParams);
end;

procedure TdmFleet.PrepareTripFuelConsumption(ATripId: Integer);
begin
  cdsTripFuelConsumption.Close;
  cdsTripFuelConsumption.CommandText := 'TRP_FuelConsumption_Get';
  DataSetOpen(cdsTripFuelConsumption,
    'trip_id=' + IntToStr(ATripId));
end;

procedure TdmFleet.PrepareTripWaypoints(ATripId: Integer);
begin
  cdsTripWaypoints.Close;
  cdsTripWaypoints.CommandText := 'TRP_Waypoints_Get';
  DataSetOpen(cdsTripWaypoints,
    'trip_id=' + IntToStr(ATripId));
end;

procedure TdmFleet.PrepareTripIncidents(ATripId: Integer);
begin
  cdsTripIncidents.Close;
  cdsTripIncidents.CommandText := 'TRP_Incidents_Get';
  DataSetOpen(cdsTripIncidents,
    'trip_id=' + IntToStr(ATripId));
end;

procedure TdmFleet.PreparePlannedTrips(Params: string);
begin
  cdsPlannedTrips.Close;
  cdsPlannedTrips.CommandText := 'TRP_GetPlanned';
  DataSetOpen(cdsPlannedTrips, Params);
end;

procedure TdmFleet.PrepareCompletedTrips(Params: string);
begin
  cdsCompletedTrips.Close;
  cdsCompletedTrips.CommandText := 'TRP_GetCompleted';
  DataSetOpen(cdsCompletedTrips, Params);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Job order group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareJobOrders(Params: string);
begin
  cdsJobOrders.Close;
  cdsJobOrders.CommandText := 'ORD_GetAll';
  DataSetOpen(cdsJobOrders, Params);
end;

procedure TdmFleet.PrepareJobDispatch(Params: string);
begin
  cdsJobDispatch.Close;
  cdsJobDispatch.CommandText := 'ORD_Dispatch_GetAll';
  DataSetOpen(cdsJobDispatch, Params);
end;

procedure TdmFleet.PrepareJobDispatchHistory(Params: string);
begin
  cdsJobDispatchHistory.Close;
  cdsJobDispatchHistory.CommandText := 'ORD_Dispatch_GetHistory';
  DataSetOpen(cdsJobDispatchHistory, Params);
end;

procedure TdmFleet.PrepareJobTracking(AJobId: Integer);
begin
  cdsJobTracking.Close;
  cdsJobTracking.CommandText := 'ORD_Tracking_Get';
  DataSetOpen(cdsJobTracking,
    'job_id=' + IntToStr(AJobId));
end;

procedure TdmFleet.PrepareJobBilling(AJobId: Integer);
begin
  cdsJobBilling.Close;
  cdsJobBilling.CommandText := 'ORD_Billing_Get';
  DataSetOpen(cdsJobBilling,
    'job_id=' + IntToStr(AJobId));
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Location / geography group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareDepots(Params: string);
begin
  cdsDepots.Close;
  cdsDepots.CommandText := 'LOC_Depots_GetAll';
  DataSetOpen(cdsDepots, Params);
end;

procedure TdmFleet.PrepareDepotZones(ADepotId: Integer);
begin
  cdsDepotZones.Close;
  cdsDepotZones.CommandText := 'LOC_DepotZones_Get';
  DataSetOpen(cdsDepotZones,
    'depot_id=' + IntToStr(ADepotId));
end;

procedure TdmFleet.PrepareGeoPoints(Params: string);
begin
  cdsGeoPoints.Close;
  cdsGeoPoints.CommandText := 'LOC_GeoPoints_GetAll';
  DataSetOpen(cdsGeoPoints, Params);
end;

procedure TdmFleet.PrepareGeoFences(Params: string);
begin
  cdsGeoFences.Close;
  cdsGeoFences.CommandText := 'LOC_GeoFences_GetAll';
  DataSetOpen(cdsGeoFences, Params);
end;

procedure TdmFleet.PrepareGpsHistory(AParams: string);
begin
  cdsGpsHistory.Close;
  cdsGpsHistory.CommandText := 'LOC_GpsHistory_Get';
  if AParams = '' then
    raise Exception.Create('PrepareGpsHistory: vehicle_id and date range required');
  DataSetOpen(cdsGpsHistory, AParams);
end;

procedure TdmFleet.PrepareBusStops(Params: string);
begin
  cdsBusStops.Close;
  cdsBusStops.CommandText := 'LOC_BusStops_GetAll';
  DataSetOpen(cdsBusStops, Params);
end;

procedure TdmFleet.PrepareTollPoints(Params: string);
begin
  cdsTollPoints.Close;
  cdsTollPoints.CommandText := 'LOC_TollPoints_GetAll';
  DataSetOpen(cdsTollPoints, Params);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Fuel / costs group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareFuelPrices(Params: string);
begin
  cdsFuelPrices.Close;
  cdsFuelPrices.CommandText := 'FUEL_Prices_GetAll';
  DataSetOpen(cdsFuelPrices, Params);
end;

procedure TdmFleet.PrepareFuelConsumption(Params: string);
begin
  cdsFuelConsumption.Close;
  cdsFuelConsumption.CommandText := 'FUEL_Consumption_Get';
  if Params = '' then
    raise Exception.Create('PrepareFuelConsumption: date range required');
  DataSetOpen(cdsFuelConsumption, Params);
end;

procedure TdmFleet.PrepareFuelOrders(Params: string);
begin
  cdsFuelOrders.Close;
  cdsFuelOrders.CommandText := 'FUEL_Orders_GetAll';
  DataSetOpen(cdsFuelOrders, Params);
end;

procedure TdmFleet.PrepareFuelInvoices(Params: string);
begin
  cdsFuelInvoices.Close;
  cdsFuelInvoices.CommandText := 'FUEL_Invoices_GetAll';
  DataSetOpen(cdsFuelInvoices, Params);
end;

procedure TdmFleet.PrepareMaintenanceCosts(Params: string);
begin
  cdsMaintenanceCosts.Close;
  cdsMaintenanceCosts.CommandText := 'COST_Maintenance_GetAll';
  DataSetOpen(cdsMaintenanceCosts, Params);
end;

procedure TdmFleet.PrepareCostCentres(Params: string);
begin
  cdsCostCentres.Close;
  cdsCostCentres.CommandText := 'COST_Centres_GetAll';
  DataSetOpen(cdsCostCentres, Params);
end;

procedure TdmFleet.PrepareCostAllocation(Params: string);
begin
  cdsCostAllocation.Close;
  cdsCostAllocation.CommandText := 'COST_Allocation_GetAll';
  DataSetOpen(cdsCostAllocation, Params);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Customer / company group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareCustomers(Params: string);
begin
  cdsCustomers.Close;
  cdsCustomers.CommandText := 'CRM_Customers_GetAll';
  DataSetOpen(cdsCustomers, Params);
end;

procedure TdmFleet.PrepareCustomerContracts(Params: string);
begin
  cdsCustomerContracts.Close;
  cdsCustomerContracts.CommandText := 'CRM_Contracts_GetAll';
  DataSetOpen(cdsCustomerContracts, Params);
end;

procedure TdmFleet.PrepareCustomerInvoices(Params: string);
begin
  cdsCustomerInvoices.Close;
  cdsCustomerInvoices.CommandText := 'CRM_Invoices_GetAll';
  DataSetOpen(cdsCustomerInvoices, Params);
end;

procedure TdmFleet.PrepareCustomerRates(ACustomerId: Integer);
begin
  cdsCustomerRates.Close;
  cdsCustomerRates.CommandText := 'CRM_Rates_Get';
  DataSetOpen(cdsCustomerRates,
    'customer_id=' + IntToStr(ACustomerId));
end;

procedure TdmFleet.PrepareCustomerHistory(Params: string);
begin
  cdsCustomerHistory.Close;
  cdsCustomerHistory.CommandText := 'CRM_History_GetAll';
  DataSetOpen(cdsCustomerHistory, Params);
end;

procedure TdmFleet.PrepareContractAmendments(AContractId: Integer);
begin
  cdsContractAmendments.Close;
  cdsContractAmendments.CommandText := 'CRM_ContractAmendments_Get';
  DataSetOpen(cdsContractAmendments,
    'contract_id=' + IntToStr(AContractId));
end;

procedure TdmFleet.PrepareCompanyBranches(Params: string);
begin
  cdsCompanyBranches.Close;
  cdsCompanyBranches.CommandText := 'CRM_Branches_GetAll';
  DataSetOpen(cdsCompanyBranches, Params);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Reports / analytics group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareReportDef(Params: string);
begin
  cdsReportDef.Close;
  cdsReportDef.CommandText := 'RPT_ReportDef_GetAll';
  DataSetOpen(cdsReportDef, Params);
end;

procedure TdmFleet.PrepareReportDefType(AParams: string);
begin
  cdsReportDef.Close;
  cdsReportDef.CommandText := 'RPT_ReportDef_GetByType';
  if AParams = '' then
    raise Exception.Create('PrepareReportDefType: report_type required');
  DataSetOpen(cdsReportDef, AParams);
end;

procedure TdmFleet.PrepareReportResults(AParams: string);
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_Results_Get';
  if AParams = '' then
    raise Exception.Create('PrepareReportResults: report parameters required');
  DataSetOpen(cdsReportResults, AParams);
end;

procedure TdmFleet.PrepareReportSchedule(Params: string);
begin
  cdsReportSchedule.Close;
  cdsReportSchedule.CommandText := 'RPT_Schedule_GetAll';
  DataSetOpen(cdsReportSchedule, Params);
end;

procedure TdmFleet.PrepareKPIData(AParams: string);
begin
  cdsKPIDaily.Close;
  cdsKPIMonthly.Close;
  cdsKPIDaily.CommandText   := 'KPI_Daily_Get';
  cdsKPIMonthly.CommandText := 'KPI_Monthly_Get';
  DataSetOpen(cdsKPIDaily,   AParams);
  DataSetOpen(cdsKPIMonthly, AParams);
end;

procedure TdmFleet.PrepareKPITargets(AParams: string);
begin
  cdsKPITargets.Close;
  cdsKPITargets.CommandText := 'KPI_Targets_GetAll';
  DataSetOpen(cdsKPITargets, AParams);
end;

procedure TdmFleet.PrepareDashboardData(AUserId: Integer);
begin
  cdsDashboardData.Close;
  cdsDashboardData.CommandText := 'SYS_Dashboard_Get';
  DataSetOpen(cdsDashboardData,
    'user_id=' + IntToStr(AUserId));
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Audit / system group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareAuditLog(Params: string);
begin
  cdsAuditLog.Close;
  cdsAuditLog.CommandText := 'SYS_AuditLog_GetAll';
  DataSetOpen(cdsAuditLog, Params);
end;

procedure TdmFleet.PrepareSystemSettings(Params: string);
begin
  cdsSystemSettings.Close;
  cdsSystemSettings.CommandText := 'SYS_Settings_GetAll';
  DataSetOpen(cdsSystemSettings, Params);
end;

procedure TdmFleet.PrepareUserPermissions(Params: string);
begin
  cdsUserPermissions.Close;
  cdsUserPermissions.CommandText := 'SYS_Permissions_GetAll';
  DataSetOpen(cdsUserPermissions, Params);
end;

procedure TdmFleet.PrepareAlerts(AParams: string);
begin
  cdsAlerts.Close;
  cdsAlerts.CommandText := 'SYS_Alerts_GetAll';
  DataSetOpen(cdsAlerts, AParams);
end;

procedure TdmFleet.PrepareNotifications(AParams: string);
begin
  cdsNotifications.Close;
  cdsNotifications.CommandText := 'SYS_Notifications_GetAll';
  DataSetOpen(cdsNotifications, AParams);
end;

// ────────────────────────────────────────────────────────────────────
// PrepareXxx implementations — Search / pagination group
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareBasicSearch(Params: string);
begin
  PrepareBasicSearch(cdsStoredProcBasicSearch, Params);
end;

procedure TdmFleet.PrepareBasicSearch(ADataSet: TClientDataSet; Params: string);
begin
  ADataSet.Close;
  ADataSet.CommandText := 'SYS_BasicSearch';
  if Params = '' then
    raise Exception.Create('PrepareBasicSearch: search term required');
  DataSetOpen(ADataSet, Params);
end;

procedure TdmFleet.PreparePagination_BASE(AClientDataSet: TClientDataSet;
  const AParams: string);
begin
  AClientDataSet.Close;
  AClientDataSet.Params.Clear;
  if AParams <> '' then
    AClientDataSet.Params.Add.AsString := AParams;
end;

procedure TdmFleet.PrepareVehiclesPagination(AParams: string);
begin
  PreparePagination_BASE(cdsVehicles, AParams);
  cdsVehicles.CommandText := 'VEH_GetPaged';
  DataSetOpen(cdsVehicles, AParams);
end;

procedure TdmFleet.PrepareDriversPagination(AParams: string);
begin
  PreparePagination_BASE(cdsDrivers, AParams);
  cdsDrivers.CommandText := 'DRV_GetPaged';
  DataSetOpen(cdsDrivers, AParams);
end;

procedure TdmFleet.PrepareJobOrdersPagination(AParams: string);
begin
  PreparePagination_BASE(cdsJobOrders, AParams);
  cdsJobOrders.CommandText := 'ORD_GetPaged';
  DataSetOpen(cdsJobOrders, AParams);
end;

procedure TdmFleet.PrepareCustomersPagination(AParams: string);
begin
  PreparePagination_BASE(cdsCustomerPagination, AParams);
  cdsCustomerPagination.CommandText := 'CRM_Customers_GetPaged';
  DataSetOpen(cdsCustomerPagination, AParams);
end;

procedure TdmFleet.PrepareRoutePagination(AParams: string);
begin
  PreparePagination_BASE(cdsRoutes, AParams);
  cdsRoutes.CommandText := 'RTE_GetPaged';
  DataSetOpen(cdsRoutes, AParams);
end;

procedure TdmFleet.PrepareTachographData(AVehicleId: Integer);
begin
  cdsVehicleTachograph.Close;
  cdsDriverTachograph.Close;
  cdsVehicleTachograph.CommandText := 'VEH_Tachograph_Get';
  cdsDriverTachograph.CommandText  := 'DRV_Tachograph_Get';
  DataSetOpen(cdsVehicleTachograph, 'vehicle_id=' + IntToStr(AVehicleId));
  DataSetOpen(cdsDriverTachograph,  'vehicle_id=' + IntToStr(AVehicleId));
end;

// ────────────────────────────────────────────────────────────────────
// StoredProc open/close
// ────────────────────────────────────────────────────────────────────

function TdmFleet.StoredProcOpen(SchemaName, StoredProcName, Params: string;
  Tag: Integer;
  const aParametersSeparator: string = #13#10;
  const aLineBreak: string = #13): boolean;
var
  DS: TClientDataSet;
begin
  Result := False;
  DS := GetClientDataSet(Tag);
  if DS = nil then
    raise Exception.CreateFmt('StoredProcOpen: no dataset for tag %d', [Tag]);
  DS.Close;
  DS.CommandText := SchemaName + '.' + StoredProcName;
  Result := DataSetOpen(DS, Params);
end;

function TdmFleet.StoredProcOpen(aClientDataSet: TClientDataSet; Params: string;
  const aParametersSeparator: string = #13#10;
  const aLineBreak: string = #13): boolean;
begin
  Result := False;
  if aClientDataSet = nil then
    raise Exception.Create('StoredProcOpen: dataset is nil');
  aClientDataSet.Close;
  Result := DataSetOpen(aClientDataSet, Params);
end;

function TdmFleet.StoredProcOpen(SchemaName, StoredProcName: string;
  Params: TStringList; Tag: Integer;
  const aParametersSeparator: string = #13#10;
  const aLineBreak: string = #13): boolean;
begin
  Result := StoredProcOpen(SchemaName, StoredProcName,
    Params.Text, Tag, aParametersSeparator, aLineBreak);
end;

function TdmFleet.StoredProcReportsOpen(SchemaName, StoredProcName, Params: string;
  const aDesiredPacketRecords: Integer = REPORTS_DS_DEFAULT_FETCH_SIZE;
  const aInitialPacketRecords: Integer = -1;
  const aParametersSeparator: string = #13#10;
  const aLineBreak: string = #13): boolean;
var
  CDS: TForwardOnlyClientDataSet;
begin
  Result := False;
  StoredProcReportsClose;
  CDS := GetCdsReports(aDesiredPacketRecords, aInitialPacketRecords);
  CDS.CommandText := SchemaName + '.' + StoredProcName;
  Result := DataSetOpen(CDS, Params);
end;

function TdmFleet.StoredProcClose(Tag: Integer): boolean;
var
  DS: TClientDataSet;
begin
  Result := False;
  DS := GetClientDataSet(Tag);
  if DS <> nil then
  begin
    DS.Close;
    Result := True;
  end;
end;

function TdmFleet.StoredProcClose(DS: TDataSet): boolean;
begin
  Result := False;
  if DS <> nil then
  begin
    DS.Close;
    Result := True;
  end;
end;

function TdmFleet.StoredProcReportsClose: boolean;
begin
  Result := False;
  if cdsStoredProcReports <> nil then
  begin
    cdsStoredProcReports.Close;
    FreeAndNil(cdsStoredProcReports);
    Result := True;
  end;
end;

// ────────────────────────────────────────────────────────────────────
// DataSet operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.DataSetOpen(ADataSet: TDataSet; Params: string = ''): boolean;
begin
  Result := False;
  if ADataSet = nil then
    Exit;
  try
    ReconnectIfNeeded;
    if Params <> '' then
      PreapreDataSet(ADataSet, Params);
    ADataSet.Open;
    Result := ADataSet.Active;
  except
    on E: Exception do
      raise Exception.CreateFmt('DataSetOpen [%s]: %s',
        [ADataSet.Name, E.Message]);
  end;
end;

function TdmFleet.DataSetOpen(ADataSet: TDataSet; aDSPParams: TDSPParams): boolean;
begin
  Result := DataSetOpen(ADataSet, aDSPParams.AsString);
end;

function TdmFleet.DataSetOpen(ADataSet: TDataSet; Params: string;
  SchemaName: string; StoredProcName: string): boolean;
begin
  if ADataSet is TClientDataSet then
    TClientDataSet(ADataSet).CommandText := SchemaName + '.' + StoredProcName;
  Result := DataSetOpen(ADataSet, Params);
end;

procedure TdmFleet.DataSetClose(ADataSet: TDataSet);
begin
  if (ADataSet <> nil) and ADataSet.Active then
    ADataSet.Close;
end;

function TdmFleet.DataSetRequery(ADataSet: TDataSet; Params: string = ''): Boolean;
begin
  DataSetClose(ADataSet);
  Result := DataSetOpen(ADataSet, Params);
end;

function TdmFleet.DataSetRequery(ADataSet: TDataSet; aDSPParams: TDSPParams): Boolean;
begin
  Result := DataSetRequery(ADataSet, aDSPParams.AsString);
end;

function TdmFleet.DBOpenCustomSQL(ADataSet: TDataSet; ACustomSQL: string = ''): boolean;
begin
  Result := False;
  if ADataSet = nil then
    Exit;
  try
    ReconnectIfNeeded;
    if ACustomSQL <> '' then
    begin
      if ADataSet is TClientDataSet then
        TClientDataSet(ADataSet).CommandText := ACustomSQL;
    end;
    ADataSet.Open;
    Result := ADataSet.Active;
  except
    on E: Exception do
      raise Exception.CreateFmt('DBOpenCustomSQL [%s]: %s',
        [ADataSet.Name, E.Message]);
  end;
end;

procedure TdmFleet.cdsStoredProcAfterOpen(DataSet: TDataSet);
begin
  // Hook reserved for post-open field initialisation
  // Subclasses may override behaviour via event assignment
end;

function TdmFleet.GetClientDataSet(aTag: integer): TClientDataSet;
begin
  case aTag of
    1: Result := cdsStoredProcCustom1;
    2: Result := cdsStoredProcCustom2;
    3: Result := cdsStoredProcCustom3;
    4: Result := cdsStoredProcCustom4;
    5: Result := cdsStoredProcCustom5;
    6: Result := cdsStoredProcCustom6;
    7: Result := cdsStoredProcCustom7;
    8: Result := cdsStoredProcAdmin_Log;
    9: Result := cdsCommitAndResult;
   10: Result := cdsStoredProcBasicSearch;
  else
    Result := nil;
  end;
end;

// ────────────────────────────────────────────────────────────────────
// Transactions
// ────────────────────────────────────────────────────────────────────

function TdmFleet.DBTransBegin: string;
begin
  ReconnectIfNeeded;
  Result := FTCPIPServerMethods.DBTransBegin;
end;

function TdmFleet.DBTransStoredProc(Guid, SchemaName, StoredProcName, Params: string;
  AResultIndex: Integer;
  AScriptGlobalParamName, AStoredProcOutParamName: string;
  const ARunPriority: Integer): string;
begin
  Result := FTCPIPServerMethods.DBTransStoredProc(
    Guid, SchemaName, StoredProcName, Params,
    AResultIndex, AScriptGlobalParamName, AStoredProcOutParamName,
    ARunPriority);
end;

function TdmFleet.DBTransCommit(Guid: string): boolean;
begin
  Result := FTCPIPServerMethods.DBTransCommit(Guid);
end;

function TdmFleet.DBTransRollback(Guid: string): boolean;
begin
  Result := FTCPIPServerMethods.DBTransRollback(Guid);
end;

function TdmFleet.DBTransScript(Guid, Script: string;
  const ARunPriority: Integer): Integer;
begin
  Result := FTCPIPServerMethods.DBTransScript(Guid, Script, ARunPriority);
end;

function TdmFleet.DBTransCommitAndResult(Guid: string): boolean;
begin
  cdsCommitAndResult.Close;
  Result := FTCPIPServerMethods.DBTransCommitAndResult(Guid);
  if Result then
    cdsCommitAndResult.Open;
end;

function TdmFleet.DBTransResultClose: boolean;
begin
  cdsCommitAndResult.Close;
  Result := True;
end;

// ────────────────────────────────────────────────────────────────────
// DB stored functions / procedures
// ────────────────────────────────────────────────────────────────────

function TdmFleet.StoredFunc(SchemaName, StoredProcName, Params: string;
  aParametersSeparator: string = #13#10; aLineBreak: string = #13): string;
begin
  ReconnectIfNeeded;
  Result := FTCPIPServerMethods.StoredFunc(
    SchemaName, StoredProcName, Params,
    aParametersSeparator, aLineBreak);
end;

function TdmFleet.StoredProc(SchemaName, StoredProcName, Params: string): Integer;
begin
  ReconnectIfNeeded;
  Result := FTCPIPServerMethods.StoredProc(SchemaName, StoredProcName, Params);
end;

// ────────────────────────────────────────────────────────────────────
// File I/O
// ────────────────────────────────────────────────────────────────────

function TdmFleet.ReadFile(aFileStream: TStream; aFileName, AGuid,
  ASubdir: string): boolean;
begin
  Result := FRemoteDataClient.ReadFile(aFileStream, aFileName, AGuid, ASubdir);
end;

function TdmFleet.SaveFile(aFileStream: TMemoryStream; aFileName, AGuid,
  ASubdir: string): boolean;
begin
  Result := FRemoteDataClient.SaveFile(aFileStream, aFileName, AGuid, ASubdir);
end;

function TdmFleet.ReadDriverFile(aFileStream: TStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReadDriverFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.SaveDriverFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.SaveDriverFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReplaceDriverFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReplaceDriverFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReadVehicleFile(aFileStream: TStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReadVehicleFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.SaveVehicleFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.SaveVehicleFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReplaceVehicleFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReplaceVehicleFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReadJobFile(aFileStream: TStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReadJobFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.SaveJobFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.SaveJobFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReadReportFile(aFileStream: TStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReadReportFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.SaveReportFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.SaveReportFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.ReplaceReportFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: string): boolean;
begin
  Result := FRemoteDataClient.ReplaceReportFile(aFileStream, aFileName, ASubDir);
end;

function TdmFleet.NextDriverFileName(ADriverId: Int64; AYear: SmallInt;
  AMonth, ADay: Byte; ADepot_ID: Integer): string;
begin
  Result := FRemoteDataClient.NextDriverFileName(
    ADriverId, AYear, AMonth, ADay, ADepot_ID);
end;

// ────────────────────────────────────────────────────────────────────
// Admin log
// ────────────────────────────────────────────────────────────────────

function TdmFleet.ADMIN_LogOpen(ProcName: string; DataOd, DataDo: TDate;
  Key_Id: Integer): boolean;
var
  sParams: string;
begin
  cdsStoredProcAdmin_Log.Close;
  cdsStoredProcAdmin_Log.CommandText := 'ADMIN_Log_Get';
  sParams :=
    'proc_name=' + ProcName            + #13#10 +
    'data_od='   + DateToStr(DataOd)   + #13#10 +
    'data_do='   + DateToStr(DataDo)   + #13#10 +
    'key_id='    + IntToStr(Key_Id);
  Result := DataSetOpen(cdsStoredProcAdmin_Log, sParams);
end;

function TdmFleet.ADMIN_LogClose: boolean;
begin
  cdsStoredProcAdmin_Log.Close;
  Result := True;
end;

// ────────────────────────────────────────────────────────────────────
// User / auth
// ────────────────────────────────────────────────────────────────────

function TdmFleet.UserLogin(aId: integer;
  AOnUserLoginProc: TOnUserLoginProc): boolean;
begin
  Result := False;
  try
    ReconnectIfNeeded;
    Result := FTCPIPServerMethods.UserLogin(aId, AOnUserLoginProc);
  except
    on E: Exception do
      raise Exception.CreateFmt('UserLogin failed for id=%d: %s', [aId, E.Message]);
  end;
end;

procedure TdmFleet.UserAfterLogin(Sender, AUser: TObject; var ALogged: boolean;
  var AMessage: string);
begin
  ALogged := True;
  AMessage := '';
  if Assigned(FOnUserAfterLoginEvent) then
    FOnUserAfterLoginEvent(Sender, AUser, ALogged, AMessage);
end;

function TdmFleet.LogonAndCheckForceLogoff: Boolean;
begin
  Result := FTCPIPServerMethods.LogonAndCheckForceLogoff;
end;

// ────────────────────────────────────────────────────────────────────
// Privileges property
// ────────────────────────────────────────────────────────────────────

function TdmFleet.GetPrivileges: TObjectList<TObject>;
begin
  Result := fPrivileges;
end;

procedure TdmFleet.SetPrivileges(const Value: TObjectList<TObject>);
begin
  if fPrivileges <> Value then
  begin
    fPrivileges.Free;
    fPrivileges := Value;
  end;
end;

// ────────────────────────────────────────────────────────────────────
// Reports dataset helper
// ────────────────────────────────────────────────────────────────────

function TdmFleet.GetCdsReports(const aDesiredPacketRecords: Integer;
  const aInitialPacketRecords: Integer): TForwardOnlyClientDataSet;
begin
  if cdsStoredProcReports = nil then
    cdsStoredProcReports := TForwardOnlyClientDataSet.Create(Self);
  cdsStoredProcReports.PacketRecords := aDesiredPacketRecords;
  if aInitialPacketRecords >= 0 then
    cdsStoredProcReports.FetchOnDemand := True;
  Result := cdsStoredProcReports;
end;

// ────────────────────────────────────────────────────────────────────
// Misc
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.SendDebugPipeMessage(aMessage: string);
begin
{$IFDEF USE_PIPES}
  if fPipeServer <> nil then
    fPipeServer.SendMessage(aMessage);
{$ENDIF}
end;

function TdmFleet.DataSnapConnectionCount: Integer;
begin
  Result := 0;
  if FTCPIPServerMethods <> nil then
    Result := FTCPIPServerMethods.ConnectionCount;
end;

// ────────────────────────────────────────────────────────────────────
// Extended vehicle operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.GetVehicleOdometerReading(AVehicleId: Integer): Double;
var
  sResult: string;
begin
  Result := 0.0;
  sResult := StoredFunc('dbo', 'VEH_GetCurrentOdometer',
    'vehicle_id=' + IntToStr(AVehicleId));
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

function TdmFleet.UpdateVehicleOdometer(AVehicleId: Integer;
  AReading: Double; AReadingDate: TDateTime): boolean;
var
  sParams: string;
begin
  sParams :=
    'vehicle_id='    + IntToStr(AVehicleId)          + #13#10 +
    'reading='       + FloatToStr(AReading)           + #13#10 +
    'reading_date='  + DateTimeToStr(AReadingDate);
  Result := StoredProc('dbo', 'VEH_UpdateOdometer', sParams) = 0;
end;

function TdmFleet.GetVehicleNextServiceDate(AVehicleId: Integer): TDateTime;
var
  sResult: string;
begin
  Result := 0;
  sResult := StoredFunc('dbo', 'VEH_GetNextServiceDate',
    'vehicle_id=' + IntToStr(AVehicleId));
  if sResult <> '' then
    Result := StrToDateTimeDef(sResult, 0);
end;

procedure TdmFleet.PrepareVehicleOverdueServices(AAsOfDate: TDateTime);
var
  sParams: string;
begin
  cdsVehicleServiceRecords.Close;
  cdsVehicleServiceRecords.CommandText := 'VEH_ServiceRecord_GetOverdue';
  sParams := 'as_of_date=' + DateToStr(AAsOfDate);
  DataSetOpen(cdsVehicleServiceRecords, sParams);
end;

procedure TdmFleet.PrepareVehiclesByDepot(ADepotId: Integer; AActiveOnly: Boolean);
var
  sParams: string;
begin
  cdsVehicles.Close;
  cdsVehicles.CommandText := 'VEH_GetByDepot';
  sParams :=
    'depot_id='    + IntToStr(ADepotId)                    + #13#10 +
    'active_only=' + BoolToStr(AActiveOnly, True);
  DataSetOpen(cdsVehicles, sParams);
end;

procedure TdmFleet.PrepareVehicleDocumentsByType(AVehicleId: Integer;
  ADocumentType: string);
var
  sParams: string;
begin
  cdsVehicleDocuments.Close;
  cdsVehicleDocuments.CommandText := 'VEH_Documents_GetByType';
  sParams :=
    'vehicle_id='     + IntToStr(AVehicleId) + #13#10 +
    'document_type='  + ADocumentType;
  DataSetOpen(cdsVehicleDocuments, sParams);
end;

function TdmFleet.CreateRepairOrder(AVehicleId: Integer;
  ADescription: string; APriority: Integer): Integer;
var
  sParams, sResult: string;
begin
  Result := -1;
  sParams :=
    'vehicle_id='   + IntToStr(AVehicleId) + #13#10 +
    'description='  + ADescription         + #13#10 +
    'priority='     + IntToStr(APriority);
  sResult := StoredFunc('dbo', 'VEH_RepairOrder_Create', sParams);
  if sResult <> '' then
    Result := StrToIntDef(sResult, -1);
end;

function TdmFleet.CloseRepairOrder(ARepairOrderId: Integer;
  AActualCost: Double; AClosedDate: TDateTime): boolean;
var
  sParams: string;
begin
  sParams :=
    'repair_order_id=' + IntToStr(ARepairOrderId)    + #13#10 +
    'actual_cost='     + FloatToStr(AActualCost)      + #13#10 +
    'closed_date='     + DateTimeToStr(AClosedDate);
  Result := StoredProc('dbo', 'VEH_RepairOrder_Close', sParams) = 0;
end;

// ────────────────────────────────────────────────────────────────────
// Extended driver operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.GetDriverCurrentAssignment(ADriverId: Integer): string;
begin
  Result := StoredFunc('dbo', 'DRV_GetCurrentAssignment',
    'driver_id=' + IntToStr(ADriverId));
end;

function TdmFleet.AssignDriverToVehicle(ADriverId, AVehicleId: Integer;
  AAssignDate: TDateTime): boolean;
var
  sParams: string;
begin
  sParams :=
    'driver_id='   + IntToStr(ADriverId)            + #13#10 +
    'vehicle_id='  + IntToStr(AVehicleId)            + #13#10 +
    'assign_date=' + DateTimeToStr(AAssignDate);
  Result := StoredProc('dbo', 'DRV_AssignToVehicle', sParams) = 0;
end;

function TdmFleet.UnassignDriver(ADriverId: Integer;
  AUnassignDate: TDateTime; AReason: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'driver_id='      + IntToStr(ADriverId)             + #13#10 +
    'unassign_date='  + DateTimeToStr(AUnassignDate)     + #13#10 +
    'reason='         + AReason;
  Result := StoredProc('dbo', 'DRV_Unassign', sParams) = 0;
end;

procedure TdmFleet.PrepareDriverLicenceExpiry(ADaysAhead: Integer);
var
  sParams: string;
begin
  cdsDriverLicences.Close;
  cdsDriverLicences.CommandText := 'DRV_Licences_GetExpiring';
  sParams := 'days_ahead=' + IntToStr(ADaysAhead);
  DataSetOpen(cdsDriverLicences, sParams);
end;

procedure TdmFleet.PrepareDriversOnLeave(ACheckDate: TDateTime);
var
  sParams: string;
begin
  cdsDriverLeave.Close;
  cdsDriverLeave.CommandText := 'DRV_Leave_GetActive';
  sParams := 'check_date=' + DateToStr(ACheckDate);
  DataSetOpen(cdsDriverLeave, sParams);
end;

function TdmFleet.RecordDriverViolation(ADriverId: Integer;
  AViolationType, ADescription: string; AIncidentDate: TDateTime;
  APenaltyPoints: Integer): boolean;
var
  sParams: string;
begin
  sParams :=
    'driver_id='       + IntToStr(ADriverId)          + #13#10 +
    'violation_type='  + AViolationType                + #13#10 +
    'description='     + ADescription                  + #13#10 +
    'incident_date='   + DateTimeToStr(AIncidentDate)  + #13#10 +
    'penalty_points='  + IntToStr(APenaltyPoints);
  Result := StoredProc('dbo', 'DRV_Violation_Record', sParams) = 0;
end;

function TdmFleet.CalculateDriverBonus(ADriverId: Integer;
  AFromDate, AToDate: TDateTime): Double;
var
  sParams, sResult: string;
begin
  Result := 0.0;
  sParams :=
    'driver_id='  + IntToStr(ADriverId)        + #13#10 +
    'from_date='  + DateToStr(AFromDate)        + #13#10 +
    'to_date='    + DateToStr(AToDate);
  sResult := StoredFunc('dbo', 'DRV_CalculateBonus', sParams);
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

// ────────────────────────────────────────────────────────────────────
// Extended trip / route operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.StartTrip(ARouteId, AVehicleId, ADriverId: Integer;
  ADepartureTime: TDateTime): Integer;
var
  sParams, sResult: string;
begin
  Result := -1;
  sParams :=
    'route_id='       + IntToStr(ARouteId)            + #13#10 +
    'vehicle_id='     + IntToStr(AVehicleId)           + #13#10 +
    'driver_id='      + IntToStr(ADriverId)            + #13#10 +
    'departure_time=' + DateTimeToStr(ADepartureTime);
  sResult := StoredFunc('dbo', 'TRP_Start', sParams);
  if sResult <> '' then
    Result := StrToIntDef(sResult, -1);
end;

function TdmFleet.CompleteTrip(ATripId: Integer;
  AArrivalTime: TDateTime; AFinalOdometer: Double): boolean;
var
  sParams: string;
begin
  sParams :=
    'trip_id='         + IntToStr(ATripId)              + #13#10 +
    'arrival_time='    + DateTimeToStr(AArrivalTime)     + #13#10 +
    'final_odometer='  + FloatToStr(AFinalOdometer);
  Result := StoredProc('dbo', 'TRP_Complete', sParams) = 0;
end;

function TdmFleet.CancelTrip(ATripId: Integer; AReason: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'trip_id=' + IntToStr(ATripId) + #13#10 +
    'reason='  + AReason;
  Result := StoredProc('dbo', 'TRP_Cancel', sParams) = 0;
end;

function TdmFleet.RecordTripDelay(ATripId: Integer;
  ADelayMinutes: Integer; ADelayReason, ADelayCode: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'trip_id='        + IntToStr(ATripId)      + #13#10 +
    'delay_minutes='  + IntToStr(ADelayMinutes) + #13#10 +
    'delay_reason='   + ADelayReason            + #13#10 +
    'delay_code='     + ADelayCode;
  Result := StoredProc('dbo', 'TRP_RecordDelay', sParams) = 0;
end;

procedure TdmFleet.PrepareActiveTrips(ADepotId: Integer);
var
  sParams: string;
begin
  cdsTrips.Close;
  cdsTrips.CommandText := 'TRP_GetActive';
  sParams := 'depot_id=' + IntToStr(ADepotId);
  DataSetOpen(cdsTrips, sParams);
end;

procedure TdmFleet.PrepareTripsByDateRange(AFromDate, AToDate: TDateTime;
  ARouteId: Integer);
var
  sParams: string;
begin
  cdsTrips.Close;
  cdsTrips.CommandText := 'TRP_GetByDateRange';
  sParams :=
    'from_date=' + DateToStr(AFromDate)  + #13#10 +
    'to_date='   + DateToStr(AToDate)    + #13#10 +
    'route_id='  + IntToStr(ARouteId);
  DataSetOpen(cdsTrips, sParams);
end;

function TdmFleet.GetTripFuelEfficiency(ATripId: Integer): Double;
var
  sResult: string;
begin
  Result := 0.0;
  sResult := StoredFunc('dbo', 'TRP_GetFuelEfficiency',
    'trip_id=' + IntToStr(ATripId));
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

// ────────────────────────────────────────────────────────────────────
// Extended job order operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.CreateJobOrder(ACustomerId: Integer;
  AJobType, ADescription: string; ARequestedDate: TDateTime;
  APriority: Integer): Integer;
var
  sParams, sResult: string;
begin
  Result := -1;
  sParams :=
    'customer_id='    + IntToStr(ACustomerId)          + #13#10 +
    'job_type='       + AJobType                        + #13#10 +
    'description='    + ADescription                    + #13#10 +
    'requested_date=' + DateTimeToStr(ARequestedDate)  + #13#10 +
    'priority='       + IntToStr(APriority);
  sResult := StoredFunc('dbo', 'ORD_CreateJobOrder', sParams);
  if sResult <> '' then
    Result := StrToIntDef(sResult, -1);
end;

function TdmFleet.DispatchJob(AJobId, AVehicleId, ADriverId: Integer;
  ADispatchTime: TDateTime): boolean;
var
  sParams: string;
begin
  sParams :=
    'job_id='         + IntToStr(AJobId)                + #13#10 +
    'vehicle_id='     + IntToStr(AVehicleId)             + #13#10 +
    'driver_id='      + IntToStr(ADriverId)              + #13#10 +
    'dispatch_time='  + DateTimeToStr(ADispatchTime);
  Result := StoredProc('dbo', 'ORD_Dispatch', sParams) = 0;
end;

function TdmFleet.CompleteJob(AJobId: Integer;
  ACompletionDate: TDateTime; AActualCost: Double;
  ACompletionNotes: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'job_id='           + IntToStr(AJobId)                + #13#10 +
    'completion_date='  + DateTimeToStr(ACompletionDate)  + #13#10 +
    'actual_cost='      + FloatToStr(AActualCost)          + #13#10 +
    'notes='            + ACompletionNotes;
  Result := StoredProc('dbo', 'ORD_Complete', sParams) = 0;
end;

function TdmFleet.CancelJob(AJobId: Integer; ACancelReason: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'job_id='        + IntToStr(AJobId)  + #13#10 +
    'cancel_reason=' + ACancelReason;
  Result := StoredProc('dbo', 'ORD_Cancel', sParams) = 0;
end;

procedure TdmFleet.PrepareJobOrdersByStatus(AStatus: string; ADepotId: Integer);
var
  sParams: string;
begin
  cdsJobOrders.Close;
  cdsJobOrders.CommandText := 'ORD_GetByStatus';
  sParams :=
    'status='   + AStatus             + #13#10 +
    'depot_id=' + IntToStr(ADepotId);
  DataSetOpen(cdsJobOrders, sParams);
end;

procedure TdmFleet.PrepareJobOrdersByCustomer(ACustomerId: Integer;
  AFromDate, AToDate: TDateTime);
var
  sParams: string;
begin
  cdsJobOrders.Close;
  cdsJobOrders.CommandText := 'ORD_GetByCustomer';
  sParams :=
    'customer_id=' + IntToStr(ACustomerId) + #13#10 +
    'from_date='   + DateToStr(AFromDate)  + #13#10 +
    'to_date='     + DateToStr(AToDate);
  DataSetOpen(cdsJobOrders, sParams);
end;

// ────────────────────────────────────────────────────────────────────
// Extended KPI / reporting operations
// ────────────────────────────────────────────────────────────────────

procedure TdmFleet.PrepareFleetUtilisationReport(AFromDate, AToDate: TDateTime;
  ADepotId: Integer);
var
  sParams: string;
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_FleetUtilisation_Get';
  sParams :=
    'from_date=' + DateToStr(AFromDate) + #13#10 +
    'to_date='   + DateToStr(AToDate)   + #13#10 +
    'depot_id='  + IntToStr(ADepotId);
  DataSetOpen(cdsReportResults, sParams);
end;

procedure TdmFleet.PrepareDriverPerformanceReport(AFromDate, AToDate: TDateTime;
  ADriverId: Integer);
var
  sParams: string;
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_DriverPerformance_Get';
  sParams :=
    'from_date='  + DateToStr(AFromDate)    + #13#10 +
    'to_date='    + DateToStr(AToDate)      + #13#10 +
    'driver_id='  + IntToStr(ADriverId);
  DataSetOpen(cdsReportResults, sParams);
end;

procedure TdmFleet.PrepareRoutePunctualityReport(AFromDate, AToDate: TDateTime;
  ARouteId: Integer);
var
  sParams: string;
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_RoutePunctuality_Get';
  sParams :=
    'from_date=' + DateToStr(AFromDate) + #13#10 +
    'to_date='   + DateToStr(AToDate)   + #13#10 +
    'route_id='  + IntToStr(ARouteId);
  DataSetOpen(cdsReportResults, sParams);
end;

procedure TdmFleet.PrepareFuelCostReport(AFromDate, AToDate: TDateTime;
  AVehicleGroupId: Integer);
var
  sParams: string;
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_FuelCost_Get';
  sParams :=
    'from_date='        + DateToStr(AFromDate)        + #13#10 +
    'to_date='          + DateToStr(AToDate)          + #13#10 +
    'vehicle_group_id=' + IntToStr(AVehicleGroupId);
  DataSetOpen(cdsReportResults, sParams);
end;

procedure TdmFleet.PrepareMaintenanceCostReport(AFromDate, AToDate: TDateTime;
  AVehicleId: Integer);
var
  sParams: string;
begin
  cdsReportResults.Close;
  cdsReportResults.CommandText := 'RPT_MaintenanceCost_Get';
  sParams :=
    'from_date='   + DateToStr(AFromDate)    + #13#10 +
    'to_date='     + DateToStr(AToDate)      + #13#10 +
    'vehicle_id='  + IntToStr(AVehicleId);
  DataSetOpen(cdsReportResults, sParams);
end;

function TdmFleet.GetFleetKPISummary(AFromDate, AToDate: TDateTime): string;
var
  sParams: string;
begin
  sParams :=
    'from_date=' + DateToStr(AFromDate) + #13#10 +
    'to_date='   + DateToStr(AToDate);
  Result := StoredFunc('dbo', 'KPI_GetFleetSummary', sParams);
end;

// ────────────────────────────────────────────────────────────────────
// Extended system / admin operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.GetSystemSetting(AKey: string): string;
begin
  Result := StoredFunc('dbo', 'SYS_GetSetting',
    'setting_key=' + AKey);
end;

function TdmFleet.SetSystemSetting(AKey, AValue, AChangedBy: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'setting_key='   + AKey       + #13#10 +
    'setting_value=' + AValue     + #13#10 +
    'changed_by='    + AChangedBy;
  Result := StoredProc('dbo', 'SYS_SetSetting', sParams) = 0;
end;

procedure TdmFleet.PurgeAuditLog(ABeforeDate: TDateTime);
var
  sParams: string;
begin
  sParams := 'before_date=' + DateToStr(ABeforeDate);
  StoredProc('dbo', 'SYS_AuditLog_Purge', sParams);
end;

function TdmFleet.CreateSystemAlert(AAlertType, AMessage: string;
  ASeverity: Integer; AEntityId: Integer; AEntityType: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'alert_type='  + AAlertType         + #13#10 +
    'message='     + AMessage            + #13#10 +
    'severity='    + IntToStr(ASeverity) + #13#10 +
    'entity_id='   + IntToStr(AEntityId) + #13#10 +
    'entity_type=' + AEntityType;
  Result := StoredProc('dbo', 'SYS_Alert_Create', sParams) = 0;
end;

function TdmFleet.AcknowledgeAlert(AAlertId: Integer;
  AAcknowledgedBy: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'alert_id='         + IntToStr(AAlertId)  + #13#10 +
    'acknowledged_by='  + AAcknowledgedBy;
  Result := StoredProc('dbo', 'SYS_Alert_Acknowledge', sParams) = 0;
end;

procedure TdmFleet.PrepareUnacknowledgedAlerts(ASeverityMin: Integer);
var
  sParams: string;
begin
  cdsAlerts.Close;
  cdsAlerts.CommandText := 'SYS_Alerts_GetUnacknowledged';
  sParams := 'severity_min=' + IntToStr(ASeverityMin);
  DataSetOpen(cdsAlerts, sParams);
end;

procedure TdmFleet.PrepareUserNotificationsByType(AUserId: Integer;
  ANotificationType: string; AUnreadOnly: Boolean);
var
  sParams: string;
begin
  cdsNotifications.Close;
  cdsNotifications.CommandText := 'SYS_Notifications_GetByType';
  sParams :=
    'user_id='             + IntToStr(AUserId)            + #13#10 +
    'notification_type='   + ANotificationType             + #13#10 +
    'unread_only='         + BoolToStr(AUnreadOnly, True);
  DataSetOpen(cdsNotifications, sParams);
end;

function TdmFleet.MarkNotificationRead(ANotificationId: Integer): boolean;
begin
  Result := StoredProc('dbo', 'SYS_Notification_MarkRead',
    'notification_id=' + IntToStr(ANotificationId)) = 0;
end;

// ────────────────────────────────────────────────────────────────────
// Extended fuel / cost operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.RecordFuelFill(AVehicleId: Integer;
  AFuelTypeId: Integer; AQuantityLitres, AUnitPrice: Double;
  AFillDate: TDateTime; ADepotId: Integer; ADriverId: Integer): boolean;
var
  sParams: string;
begin
  sParams :=
    'vehicle_id='       + IntToStr(AVehicleId)          + #13#10 +
    'fuel_type_id='     + IntToStr(AFuelTypeId)          + #13#10 +
    'quantity_litres='  + FloatToStr(AQuantityLitres)    + #13#10 +
    'unit_price='       + FloatToStr(AUnitPrice)          + #13#10 +
    'fill_date='        + DateTimeToStr(AFillDate)        + #13#10 +
    'depot_id='         + IntToStr(ADepotId)              + #13#10 +
    'driver_id='        + IntToStr(ADriverId);
  Result := StoredProc('dbo', 'FUEL_RecordFill', sParams) = 0;
end;

function TdmFleet.GetCurrentFuelPrice(AFuelTypeId: Integer;
  ADepotId: Integer): Double;
var
  sParams, sResult: string;
begin
  Result := 0.0;
  sParams :=
    'fuel_type_id=' + IntToStr(AFuelTypeId) + #13#10 +
    'depot_id='     + IntToStr(ADepotId);
  sResult := StoredFunc('dbo', 'FUEL_GetCurrentPrice', sParams);
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

procedure TdmFleet.PrepareFuelConsumptionByVehicle(AVehicleId: Integer;
  AFromDate, AToDate: TDateTime);
var
  sParams: string;
begin
  cdsFuelConsumption.Close;
  cdsFuelConsumption.CommandText := 'FUEL_Consumption_GetByVehicle';
  sParams :=
    'vehicle_id=' + IntToStr(AVehicleId)    + #13#10 +
    'from_date='  + DateToStr(AFromDate)    + #13#10 +
    'to_date='    + DateToStr(AToDate);
  DataSetOpen(cdsFuelConsumption, sParams);
end;

procedure TdmFleet.PrepareFuelBudgetVsActual(ABudgetYear: Integer;
  ABudgetMonth: Integer; ADepotId: Integer);
var
  sParams: string;
begin
  cdsFuelBudgets.Close;
  cdsFuelReports.Close;
  cdsFuelBudgets.CommandText := 'FUEL_Budget_Get';
  cdsFuelReports.CommandText := 'FUEL_Actual_Get';
  sParams :=
    'budget_year='  + IntToStr(ABudgetYear)  + #13#10 +
    'budget_month=' + IntToStr(ABudgetMonth) + #13#10 +
    'depot_id='     + IntToStr(ADepotId);
  DataSetOpen(cdsFuelBudgets, sParams);
  DataSetOpen(cdsFuelReports, sParams);
end;

function TdmFleet.ReconcileFuelInvoice(AInvoiceId: Integer;
  AReconcileDate: TDateTime; AReconcileNotes: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'invoice_id='       + IntToStr(AInvoiceId)              + #13#10 +
    'reconcile_date='   + DateTimeToStr(AReconcileDate)      + #13#10 +
    'reconcile_notes='  + AReconcileNotes;
  Result := StoredProc('dbo', 'FUEL_Invoice_Reconcile', sParams) = 0;
end;

// ────────────────────────────────────────────────────────────────────
// Extended customer / contract operations
// ────────────────────────────────────────────────────────────────────

function TdmFleet.CreateCustomerInvoice(ACustomerId, AContractId: Integer;
  AInvoiceDate: TDateTime; APeriodFrom, APeriodTo: TDateTime): Integer;
var
  sParams, sResult: string;
begin
  Result := -1;
  sParams :=
    'customer_id='  + IntToStr(ACustomerId)           + #13#10 +
    'contract_id='  + IntToStr(AContractId)            + #13#10 +
    'invoice_date=' + DateToStr(AInvoiceDate)          + #13#10 +
    'period_from='  + DateToStr(APeriodFrom)           + #13#10 +
    'period_to='    + DateToStr(APeriodTo);
  sResult := StoredFunc('dbo', 'CRM_Invoice_Create', sParams);
  if sResult <> '' then
    Result := StrToIntDef(sResult, -1);
end;

function TdmFleet.PostCustomerInvoice(AInvoiceId: Integer): boolean;
begin
  Result := StoredProc('dbo', 'CRM_Invoice_Post',
    'invoice_id=' + IntToStr(AInvoiceId)) = 0;
end;

function TdmFleet.VoidCustomerInvoice(AInvoiceId: Integer;
  AVoidReason: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'invoice_id='  + IntToStr(AInvoiceId) + #13#10 +
    'void_reason=' + AVoidReason;
  Result := StoredProc('dbo', 'CRM_Invoice_Void', sParams) = 0;
end;

procedure TdmFleet.PrepareCustomerOutstandingInvoices(ACustomerId: Integer;
  AAsOfDate: TDateTime);
var
  sParams: string;
begin
  cdsCustomerInvoices.Close;
  cdsCustomerInvoices.CommandText := 'CRM_Invoices_GetOutstanding';
  sParams :=
    'customer_id=' + IntToStr(ACustomerId)  + #13#10 +
    'as_of_date='  + DateToStr(AAsOfDate);
  DataSetOpen(cdsCustomerInvoices, sParams);
end;

function TdmFleet.GetCustomerCreditLimit(ACustomerId: Integer): Double;
var
  sResult: string;
begin
  Result := 0.0;
  sResult := StoredFunc('dbo', 'CRM_GetCreditLimit',
    'customer_id=' + IntToStr(ACustomerId));
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

function TdmFleet.GetCustomerOutstandingBalance(ACustomerId: Integer): Double;
var
  sResult: string;
begin
  Result := 0.0;
  sResult := StoredFunc('dbo', 'CRM_GetOutstandingBalance',
    'customer_id=' + IntToStr(ACustomerId));
  if sResult <> '' then
    Result := StrToFloatDef(sResult, 0.0);
end;

function TdmFleet.RenewCustomerContract(AContractId: Integer;
  ANewExpiryDate: TDateTime; ANewRateCard: string): boolean;
var
  sParams: string;
begin
  sParams :=
    'contract_id='    + IntToStr(AContractId)          + #13#10 +
    'new_expiry_date='+ DateToStr(ANewExpiryDate)       + #13#10 +
    'new_rate_card='  + ANewRateCard;
  Result := StoredProc('dbo', 'CRM_Contract_Renew', sParams) = 0;
end;

end.
