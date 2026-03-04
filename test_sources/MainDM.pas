unit MainDM;

interface

uses
  SysUtils, Classes, WideStrings, DBXDataSnap,
  DBClient, DSConnect, DB, SqlExpr
  , TCPIPServerMethods
  , Events
  , GlobalTypes
  , Generics.Collections
  , KMDSPParams
  , IPPeerClient, Data.DBXCommon, Data.DbxHTTPLayer
{$IFDEF USE_PIPES}
  , Pipes
{$ENDIF}
  , UTForwardOnlyClientDataSet
  ;

type

  TdmMain = class(TDataModule)
    cdsStoredProcCustom1: TClientDataSet;
    cdsStoredProcCustom2: TClientDataSet;
    cdsStoredProcCustom3: TClientDataSet;
    cdsStoredProcCustom4: TClientDataSet;
    cdsStoredProcCustom5: TClientDataSet;
    cdsStoredProcCustom6: TClientDataSet;
    cdsStoredProcCustom7: TClientDataSet;

    SQLConnection: TSQLConnection;
    DSProviderConnection: TDSProviderConnection;
    cdsStoredProcAdmin_Log: TClientDataSet;
    cdsCommitAndResult: TClientDataSet;
    cdsStoredProcBasicSearch: TClientDataSet;
    cdsStoredProcProvinces: TClientDataSet;
    cdsStoredProcRoads: TClientDataSet;
    cdsStoredProcPlaces: TClientDataSet;
    cdsStoredProcCountries: TClientDataSet;
    cdsStoredProcDistricts: TClientDataSet;
    cdsStoredProcBoroughs: TClientDataSet;
    cdsStoredProcRoadPoints: TClientDataSet;
    cdsBusStopStands: TClientDataSet;
    cdsLineRoadPoints: TClientDataSet;
    cdsCombustionStandards: TClientDataSet;
    cdsStoredProcRoadPointsType8: TClientDataSet;
    cdsStoredProcBusPCNotUse: TClientDataSet;
    cdsStorProcTicketRegister4Buses2Assign: TClientDataSet;
    cdsPersonHistory: TClientDataSet;
    cdsCompanyHistory: TClientDataSet;
    cdsStoredProcLPC_CompaniesByType: TClientDataSet;
    cdsStoredProcCompaniesWithoutHistory: TClientDataSet;
    cdsStoredProcDriverGroups: TClientDataSet;
    cdsTicketRegisterCardNotAssigned: TClientDataSet;
    cdsStoredProcCompanies: TClientDataSet;
    cdsStorProcDriversWithoutTicketCard: TClientDataSet;
    cdsStoredProcAllCompanyHierarchy: TClientDataSet;
    cdsStoredProcBusStops: TClientDataSet;
    cdsStorProcAutoCashier: TClientDataSet;
    cdsTicketControlDev: TClientDataSet;
    cdsStoredProcEmCardLoader: TClientDataSet;
    cdsBusPCNotAssignedToDriver: TClientDataSet;
    cdsStoredProcCalendar: TClientDataSet;
    cdsStoredProcRideDesignation: TClientDataSet;
    cdsStoredProcPriceLists: TClientDataSet;
    cdsRideTypeCommunication: TClientDataSet;
    cdsRideServiceType: TClientDataSet;
    cdsRideCommunicationNetwork: TClientDataSet;
    cdsRideBusTableConfPrefSet: TClientDataSet;
    cdsRideExpPrefSets: TClientDataSet;
    cdsRideSalePrefSets: TClientDataSet;
    cdsTT_TimeTableGetAll: TClientDataSet;
    cdsLine: TClientDataSet;
    cdsRide: TClientDataSet;
    cdsStoredProcTicketZoneBusStops: TClientDataSet;
    cdsStoredProcFarePriceReductionCities: TClientDataSet;
    cdsStoredProcPriceBasicCitiesScales: TClientDataSet;
    cdsStoredProcPriceCitiesScales: TClientDataSet;
    cdsStoredProcTicketZones: TClientDataSet;
    cdsStoredProcPriceMonthTypes: TClientDataSet;
    cdsStoredProcPriceMonthScales: TClientDataSet;
    cdsStoredProcPriceOnesScales: TClientDataSet;
    cdsStoredProcPriceMonthCityScales: TClientDataSet;
    cdsStoredProcFarePriceReductionMonthCities: TClientDataSet;
    cdsStoredProcFarePriceMonthReductionAmounts: TClientDataSet;
    cdsStoredProcFarePriceReductionAmountsNotUse: TClientDataSet;
    cdsStoredProcFarePriceReductionAmounts: TClientDataSet;
    cdsStoredProcFarePriceReductionRoundMethod: TClientDataSet;
    cdsStoredProcVatRates: TClientDataSet;
    cdsStoredProcCurrenciesHistory: TClientDataSet;
    cdsStoredProcPLAN_BusRunResultAnalyze: TClientDataSet;
    cdsStoredProcCurrencies: TClientDataSet;
    cdsStoredProcFarePriceReductionWorkers: TClientDataSet;
    cdsStoredProcFarePriceReductionAct: TClientDataSet;
    cdsStoredProcFarePriceReductionGroup: TClientDataSet;
    cdsStoredProcPassanger: TClientDataSet;
    cdsStoredProcEmCard: TClientDataSet;
    cdsStoredProcLine: TClientDataSet;
    cdsStoredProcCompanyLine: TClientDataSet;
    cdsStorProcTicketRegister4Buses: TClientDataSet;
    cdsStoredProcBusGroups: TClientDataSet;
    cdsStoredProcDrivers: TClientDataSet;
    cdsStoredProcBuses: TClientDataSet;
    cdsStoredProcBusPCStatus: TClientDataSet;
    cdsDISPFile: TClientDataSet;
    cdsStoredProcTicketRegisterCard: TClientDataSet;
    cdsStorProcLineRides: TClientDataSet;
    cdsStorProcLines2AssignFarePriceScale: TClientDataSet;
    cdsDISP_BusRun_GetAll: TClientDataSet;
    cdsFileXTicketRegister: TClientDataSet;
    cdsStoredProcGovOffice: TClientDataSet;
    cdsAdditionalFees: TClientDataSet;
    cdsStoredProcHist: TClientDataSet;
    cdsDriverTicketRegPrefSet: TClientDataSet;
    cdsStoredProcDriverTicketRegPrefSet: TClientDataSet;
    cdsBusStandNamePrefSets: TClientDataSet;
    cdsRideReductions: TClientDataSet;
    cdsRideBusStops: TClientDataSet;
    cdsStoredProcTicketRegPrefSet: TClientDataSet;
    cdsTicketRegisterHistory: TClientDataSet;
    cdsCashDeskSettings: TClientDataSet;
    cdsStorProcTicketRegister4SaleDevices: TClientDataSet;
    cdsStoredProcCashDesks: TClientDataSet;
    cdsStoredProcLPC_Parameters: TClientDataSet;
    cdsBusHistory: TClientDataSet;
    cdsStoredProcTechnicalRide: TClientDataSet;
    cdsStoredProcContractRide: TClientDataSet;
    cdsStoredProcPlacesForRide: TClientDataSet;
    cdsStoredProcCircuit: TClientDataSet;
    cdsStoredProcPLAN_RideRoadPoints: TClientDataSet;
    cdsFileXTicketRegisterCard: TClientDataSet;
    cdsStoredProcAdminUserAll: TClientDataSet;
    cdsSalesReportOfTicketRegister: TClientDataSet;
    cdsSalesReportOfTicketRegisterCard: TClientDataSet;
    cdsStoredProcPlacesPagination: TClientDataSet;
    cdsStoredProcFreeEmCard: TClientDataSet;
    cdsChoiceBusStop: TClientDataSet;
    cdsChoiceCompany: TClientDataSet;
    cdsStoredProcRoadsPagination: TClientDataSet;
    cdsStoredProcBusStopsPagination: TClientDataSet;
    cdsStoredProcBusStopSelectAssignedOrderByName: TClientDataSet;
    cdsCommunityPagination: TClientDataSet;
    cdsStoredProcTimeTableResult: TClientDataSet;
    cdsStoredProcBusStopTablePatternChoice: TClientDataSet;
    cdsStoredProcBusStopTablePattern: TClientDataSet;
    cdsStoredProcAdmin_ReportResultWhereReportTypeId: TClientDataSet;
    cdsStoredProcTimeTable_IDDesc: TClientDataSet;
    cdsStoredProcBusStopsDuplicatesPagination: TClientDataSet;
    cdsStoredProcFarePriceReductionCommercial: TClientDataSet;
    cdsSalesReportPagination: TClientDataSet;
    cdsTrackingMS_AUTOOBSERWACJA: TClientDataSet;
    cdsTrackingBusListWithGPS: TClientDataSet;
    cdsAnalysisRJAGPS: TClientDataSet;
    cdsStoredProcRideForPair: TClientDataSet;
    cdsStoredProcAdmin_ReportDefWhereReportTypeId: TClientDataSet;
    cdsStoredProcLineRoute: TClientDataSet;
    cdsStoredProcBusStopFeeInvoice_SelectAll: TClientDataSet;
    cdsStoredProcFeeType_GetBusStopFee: TClientDataSet;
    cdsStoredProcBusStopCompanySelectAll: TClientDataSet;
    cdsStoredProcBusStopFeeList: TClientDataSet;
    cdsStoredProcTT_RideGetAllForCEDULA: TClientDataSet;
    cdsRidePagination: TClientDataSet;
    cdsLinePagination: TClientDataSet;
    cdsStoredProcCashReport: TClientDataSet;
    cdsStoredProcSalesReportNoCashReport: TClientDataSet;
    dsProviderFarePriceReduction_SelectAll: TClientDataSet;
    cdsStoredProcFarePriceReduction_SelectAll: TClientDataSet;
    cdsStoredProcLPC_CompaniesByBusStopManager: TClientDataSet;
    cdsStoredProcDrivers1: TClientDataSet;
    cdsStoredProcLineFeeDefinition: TClientDataSet;
    cdsStoredProcDriversChoice: TClientDataSet;
    cdsStoredProcPlacesForBusStop: TClientDataSet;
    cdsStoredProcRideGroup: TClientDataSet;
    cdsStoredProcTask: TClientDataSet;
    cdsStoredProcTaskGroup: TClientDataSet;

    procedure DataModuleDestroy(Sender: TObject);
    procedure DataModuleCreate(Sender: TObject);
    procedure SQLConnectionValidatePeerCertificate(Owner: TObject; Certificate:
        TX509Certificate; const ADepth: Integer; var Ok: Boolean);

  private
    { Private declarations }
    FTCPIPServerMethods: TdmTCPIPServerMethodsClient;
    FRemoteDataClient: TdmRemoteDataClient;
    FOnUserAfterLoginEvent: TUserAfterLoginEvent;
    fPrivileges: TObjectList<TObject>;
{$IFDEF USE_PIPES}
    fPipeServer: TPipeServer;
{$ENDIF}
    // JS Dataset do obs³ugi raportów. Nie œci¹ga wszystkich danych i nie kumuluje
    // w pamiêci - œci¹ga po kawa³ku. Pozwala tylko na jedno przelecenie przez
    // zbiór danych.
    cdsStoredProcReports: TForwardOnlyClientDataSet;

    procedure PreapreDataSet(ADataSet: TDataSet; Params: string); overload;
{$HINTS OFF}
    procedure PreapreDataSet(ADataSet: TDataSet; aDSPParams: TDSPParams); overload;
{$HINTS ON}
    procedure PreparePagination_BASE(AClientDataSet: TClientDataSet; const AParams : String);
    procedure PrepareRideRoadPoints(Params: string);
    procedure PreparePlaces(Params: string);
    procedure PreparePlacesPagination(Params: string);
    procedure PreparePlacesForRide(Params: string);
    procedure PrepareEmCardLoader( AParams: String);
    procedure PrepareEmCard( AParams: String);
    procedure PrepareProviderAutoCashier(Params: string);
    procedure PrepareCalendar(Params: string);
    procedure PrepareRideDesignation(Params: string);
    procedure PrepareRoads(Params: string);
    procedure PrepareBusStops(Params: string);
    procedure PrepareBusStopsDuplicates(Params: string);
    procedure PreparePriceOnesScales(Params: string);
    procedure PreparePriceReductionAmountsNotUse(Params: string);
    procedure PreparePriceCitiesScales(Params: string);
    procedure PreparePriceReductionCities(Params: string);
    procedure PreparePriceReductionAmounts(Params: string);
    procedure PreparePriceBasicCitiesScales(Params: string);
    procedure PrepareBuses(Params: string);
    procedure PrepareTicketZoneBusStops(Params: string);
    procedure PreparePriceMonthScales(Params: string);
    procedure PreparePriceMonthCityScales(Params: string);
    procedure PrepareBasicSearch(Params: string); overload;
    procedure PrepareCurrenciesHistory(Params: string);
    procedure PrepareLine(aDataSet: TClientDataSet; AParams: string);
    procedure PrepareLinePagination(AParams: string);
    procedure PrepareRide(aDataSet: TClientDataSet; AParams: string);
    procedure PrepareRidePagination(AParams: string);
    procedure PrepareDrivers(Params: string; TypeDS : Integer);
    procedure PrepareBusPC(Params: string);
    procedure PrepareTT_RideGetAllForCEDULA(Params: string);
    procedure PrepareCompaniesByType(AParams: string); overload;
    procedure PrepareGovOffice(AParams: string);
    procedure PrepareHistory(Params: string);
    procedure PreparePassanger(Params: string);
    procedure PrepareTicketRegisterHistory(Params: string);
    procedure PrepareTicketRegisterCardNotAssigned(Params: string);
    procedure PrepareTicketRegister4SaleDevices(Params: string);
    procedure PrepareCashDesks(Params: string);
    function GetPrivileges: TObjectList<TObject>;
    procedure SetPrivileges(const Value: TObjectList<TObject>);
    procedure PrepareCommunityPagination(AParams: string);
    procedure PrepareReportResultType(AParams: string);
    procedure PrepareBusStopTablePattern(AParams: string);
    procedure PrepareBusStopTablePatternChoice(AParams: string);
    procedure PrepareTimeTableResult(AParams: string);
    procedure PrepareCompaniesWithoutHistory(Params: string);
    procedure PrepareSalesReportPagination(Params: string);
    procedure PrepareRideForPair(Params: string);
    procedure PrepareReportDefType(AParams: string);
    procedure PrepareBusStopFeeListPagination(const AParams : String);
    procedure PrepareLPC_Parameters(Params: string);
    procedure PrepareBusStopSelectAssignedOrderByName(Params : String);
    procedure PreparePlacesForBusStop(AParams: string);
    procedure PrepareCompanyHistory(AParams: string);
    procedure PrepareDriverGroups(Params: string);
    function GetCdsStoredProcReports(const aDesiredPacketRecords: Integer;
      const aInitialPacketRecords: Integer): TForwardOnlyClientDataSet;

  public
    { Public declarations }
    const REPORTS_DS_DEFAULT_FETCH_SIZE = 1000;

    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;

    procedure cdsStoredProcAfterOpen(DataSet: TDataSet);
    function GetClientDataSet(aTag: integer): TClientDataSet;
    function CloseConnection: boolean;
    function OpenConnection: boolean;
    function TestConnection: boolean;
    procedure CloseDatasets;
    function StoredProcReportsOpen(SchemaName, StroredProcName,
      Params: string;
      const aDesiredPacketRecords: Integer = REPORTS_DS_DEFAULT_FETCH_SIZE;
      const aInitialPacketRecords: Integer = -1;
      const aParametersSeparator: String = #13#10;
      const aLineBreak: String = #13): boolean;
    function StoredProcOpen(SchemaName, StroredProcName,
      Params: string; Tag: Integer;
      const aParametersSeparator: String = #13#10;
      const aLineBreak: String = #13): boolean; overload;
    function StoredProcOpen(aClientDataSet: TClientDataSet; Params: string;
      const aParametersSeparator: String = #13#10;
      const aLineBreak: String = #13): boolean; overload;
    function StoredProcOpen(SchemaName, StroredProcName: string; Params: TStringList;
      Tag: Integer; const aParametersSeparator: String = #13#10;
      const aLineBreak: String = #13): boolean; overload;
    function StoredProcReportsClose: boolean;
    function StoredProcClose(Tag: Integer): boolean; overload;
    function StoredProcClose(DS: TDataSet): boolean; overload;
    function DataSetRequery(ADataSet: TDataSet; aDSPParams: TDSPParams): Boolean; overload;
    function DataSetRequery(ADataSet: TDataSet; Params: string = ''): Boolean; overload;
    function DataSetOpen(ADataSet: TDataSet; aDSPParams: TDSPParams): boolean; overload;
    function DataSetOpen(ADataSet: TDataSet; Params: string = ''): boolean; overload;
    function DataSetOpen(ADataSet: TDataSet; Params: string;
      SchemaName: string; StroredProcName: string): boolean; overload;
    procedure DataSetClose(ADataSet: TDataSet);
    function DBOpenCustomSQL(ADataSet: TDataSet; ACustomSQL: string = ''): boolean;
    function StoredFunc(SchemaName: string;
      StroredProcName: string; Params: string;
      aParametersSeparator: String = #13#10; aLineBreak: string = #13): string;
    function StoredProc(SchemaName: string;
      StroredProcName: string; Params: string): Integer;
    function DBTransBegin: String;
    function DBTransStoredProc(Guid, SchemaName: string;
      StroredProcName: string; Params: string; AResultIndex: Integer;
      AScriptGlobalParamName, AStoredProcOutParamName: String;
      const ARunPriority: Integer): string;
    function DBTransCommit(Guid: String): boolean;
    function DBTransRollback(Guid: String): boolean;
    function DBTransScript(Guid: string; Script: string; const ARunPriority: Integer): Integer;
    function DBTransCommitAndResult(Guid: string): boolean;
    function DBTransResultClose: boolean;
    function ADMIN_LogClose: boolean;
    function ADMIN_LogOpen(ProcName: String; DataOd, DataDo: TDate;
      Key_Id: Integer): boolean;
    procedure SendDebugPipeMessage(aMessage: string);
    function LogonAndCheckForceLogoff: Boolean;
    function UserLogin(aId: integer;  AOnUserLoginProc : TOnUserLoginProc): boolean;
    procedure UserAfterLogin(Sender, AUser: TObject; var ALogged: boolean;
      var AMessage: String);
    function DataSnapConnectionCount: Integer;
    function ReadFile(aFileStream: TStream; aFileName, AGuid, ASubdir: string): boolean;
    function SaveFile(aFileStream: TMemoryStream;aFileName, AGuid, ASubdir: string): boolean;
    function ReadRegFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
    function SaveRegFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReadCardFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
    function SaveCardFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReplaceCardFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function NextCardFileName(ACardSerialNumber: Int64; AYear: SmallInt; AMonth, ADay: Byte;
      ACompany_ID: Integer): String;
    function ReadSalesReportFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
    function SaveSalesReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReplaceSalesReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReadEmar205File(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
    function SaveEmar205File(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReplaceEmar205File(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReadBusTabletFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
    function SaveBusTabletFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
    function ReplaceBusTabletFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;

    /// <summary>
    ///  Lista plików do rejestracji lub po b³êdnej rejestracji.
    ///  S¹ pobierane z folderów z config.ini DataSnapa.
    /// <summary>
    /// <param name="AServerSalesReportsType">
    ///   Reports type
    /// <remarks>
    ///   parameter "AServerSalesReportsType": 0 - all; 1 - without .error file; 2- with .error file
    /// </remarks>
    /// <returns>
    ///   list of files in JSON format
    /// </returns>
    function GetServerSalesReportsList(AServerSalesReportsType: Byte; ACountOnly: Boolean): String;
    /// <summary>
    ///   True - gdy istnieje przynajmniej jeden raport z b³edem
    /// </summary>
    function GetReportsForRegistrationInServerSalesReportsList(): Boolean;

    /// <summary>
    ///  Removes report's error file only
    /// <summary>
    function DeleteErrorFile(AFileType: Byte; AFileWithSubDir: String): Boolean;

    /// <summary>
    ///  Removes report with the error file
    /// <summary>
    function DeleteIncorrectReportFile(AFileType: Byte; AFileWithSubDir: String): Boolean;
    procedure AutServerStart(AForceKillProcess: Boolean);
    function AutServerIsRunning(): Boolean;
    function AutServerIsStopping(): Boolean;
    function AutServerName(): String;
    function AutServerDisplayName(): String;
    function AllCompanyHierarchyOpen(ACompany_Id: Integer;
      ACompanyHierarchy_Id: Integer = 0; AAndCompany:integer = 0): boolean;
    function CheckClientVersion(AClientVersion : String) : Boolean;
    function CheckCompanyCodeInDB(ACompanyCode : string) : Boolean;
    function CheckInformicaVersion : String;
    function DataSnapVersion: string;
    function HttpUserPrivilege(aTag: integer): boolean;
    function RideDesignationOpen(Params: string): boolean;
    function PrepareBasicSearch: boolean; overload;
    function PrepareCompaniesByType: Boolean; overload;
    procedure GetClientAuthentication;
    function TryOpenConnection(Var BError : String) : boolean;
    function IsAttachmentsDirectoryWriteable: Boolean;
    function IsCardFilesDirectoryWriteable: Boolean;
    function IsSalesReportFilesDirectoryWriteable: Boolean;
    function ParamsForRoadCardsSynchroExists: Boolean;
    function DBVersionGet(var DBVer : Integer) : boolean;

    property TCPIPServerMethods: TdmTCPIPServerMethodsClient read FTCPIPServerMethods;
    property RemoteDataClient: TdmRemoteDataClient read FRemoteDataClient;
    property OnUserAfterLoginEvent
      : TUserAfterLoginEvent read FOnUserAfterLoginEvent write
      FOnUserAfterLoginEvent;
    property Privileges: TObjectList<TObject> read GetPrivileges write SetPrivileges;
{$IFDEF USE_PIPES}
    property PipeServer: TPipeServer read fPipeServer write fPipeServer;
{$ENDIF}
    property CDSReports: TForwardOnlyClientDataSet read cdsStoredProcReports;
  end;

threadvar
  dmMainGlobal: TdmMain;

implementation

{$region 'uses'}
uses
  ClientMainDMUtil
  , LoginFrm
  , Globals
  , KMUtils
  , IniFiles
  , Forms
  , ClientDataSetPrepareUtil
  , Types
  , KMStrUtils
  , DBTransClasses
  , DBProcedures
  , Math
  , superobject
  ;
{$endregion}

{$R *.dfm}

{ TdmMain }

{$region 'Connection operations}

function TdmMain.OpenConnection(): boolean;
begin
  if Assigned(SQLConnection) then
  begin
    Result := ClientMainDMUtil.OpenConnection(SQLConnection, FTCPIPServerMethods);
    if Result and not Assigned(FRemoteDataClient) then
      FRemoteDataClient := TdmRemoteDataClient.Create(SQLConnection.DBXConnection);
  end
  else
    Result := False;
end;


function TdmMain.TestConnection: boolean;
begin
  Result := ClientMainDMUtil.TestConnection(SQLConnection, FTCPIPServerMethods);
end;

function TdmMain.CloseConnection: boolean;
begin
  try
    if Assigned(SQLConnection) then
      Result := ClientMainDMUtil.CloseConnection(SQLConnection, FTCPIPServerMethods)
    else
    begin
        Result := True;
    end;
    if Result and Assigned(FRemoteDataClient) then
    begin
      FreeAndNil(FRemoteDataClient);
    end;
  except
    on E: exception do begin
      Result := False;
    end;
  end;
end;
{$endregion}

{$region 'ADMINistrative operations'}
function TdmMain.ADMIN_LogClose: boolean;
begin
  Result := ClientMainDMUtil.ADMIN_LogClose(FTCPIPServerMethods);
end;

function TdmMain.ADMIN_LogOpen(ProcName: String; DataOd, DataDo: TDate;
  Key_Id: Integer): boolean;
begin
  Result := ClientMainDMUtil.ADMIN_LogOpen(ProcName, DataOd, DataDo, Key_Id, FTCPIPServerMethods);
end;

function TdmMain.AllCompanyHierarchyOpen(ACompany_Id, ACompanyHierarchy_Id: Integer; AAndCompany: integer): boolean;
begin
  Result := ClientMainDMUtil.AllCompanyHierarchyOpen(ACompany_Id,
    cdsStoredProcAllCompanyHierarchy, ACompanyHierarchy_Id, AAndCompany);
end;

procedure TdmMain.cdsStoredProcAfterOpen(DataSet: TDataSet);
begin
  if Assigned(DataSet) and (DataSet is TClientDataSet) and
     Assigned(FTCPIPServerMethods) and (TClientDataSet(DataSet).ProviderName <> '') then
    FTCPIPServerMethods.CloseSQLDataset(TClientDataSet(DataSet).ProviderName);
end;

{$endregion}

{$region 'Check Client\Version operations'}

function TdmMain.CheckClientVersion(AClientVersion: String): Boolean;
begin
  Result := ClientMainDMUtil.CheckClientVersion(AClientVersion, FTCPIPServerMethods);
end;

function TdmMain.CheckCompanyCodeInDB(ACompanyCode: string): Boolean;
begin
  Result := ClientMainDMUtil.CheckCompanyCodeInDB(ACompanyCode, FTCPIPServerMethods);
end;

function TdmMain.CheckInformicaVersion: String;
begin
  Result := ClientMainDMUtil.CheckInformicaVersion(FTCPIPServerMethods);
end;

{$endregion}

{$region 'DataSet operations'}

procedure TdmMain.CloseDatasets;
begin
  ClientMainDMUtil.CloseDatasets(Self);
end;

constructor TdmMain.Create(AOwner: TComponent);
begin
  inherited;
  if SQLConnection.Connected then
         raise Exception.Create('SprawdŸ SQLConnection w MainDM!');
end;

destructor TdmMain.Destroy;
begin
  CloseConnection;
  if Assigned(fPrivileges) then
    FreeAndNil(fPrivileges);
  if Assigned(cdsStoredProcReports) then
    StoredProcReportsClose;
  inherited;
end;

procedure TdmMain.DataModuleDestroy(Sender: TObject);
begin
  SQLConnection.Close;
end;

procedure TdmMain.DataModuleCreate(Sender: TObject);
var
  i: integer;
begin
  ClientMainDMUtil.DataModuleSQLConnect(Self);
  for i := 0 to ComponentCount - 1 do
    if Components[i] is TClientDataSet then
      TClientDataSet(Components[i]).AfterOpen := cdsStoredProcAfterOpen;
end;

procedure TdmMain.DataSetClose(ADataSet: TDataSet);
begin
  ClientMainDMUtil.DataSetClose(ADataSet);
end;

function TdmMain.DataSetOpen(ADataSet: TDataSet; Params, SchemaName,
  StroredProcName: string): boolean;
begin
  Result := DataSetOpen(ADataSet, Params);
end;

function TdmMain.DataSetOpen(ADataSet: TDataSet; aDSPParams: TDSPParams): boolean;
begin
  if assigned(ADataSet) then
    TClientDataSet(ADataSet).IndexName:= '';
  Result := ClientMainDMUtil.DataSetRequery(ADataSet, aDSPParams, Self.PreapreDataSet);
end;

function TdmMain.DataSetOpen(ADataSet: TDataSet; Params: string): boolean;
begin
  if assigned(ADataSet) then
    TClientDataSet(ADataSet).IndexName:= '';
  Result := ClientMainDMUtil.DataSetRequery(ADataSet, Params, PreapreDataSet);
end;

function TdmMain.DataSetRequery(ADataSet: TDataSet; Params: string): Boolean;
begin
  Result := ClientMainDMUtil.DataSetRequery(ADataSet, Params, PreapreDataSet);
end;

function TdmMain.DataSetRequery(ADataSet: TDataSet; aDSPParams: TDSPParams): Boolean;
begin
  Result := ClientMainDMUtil.DataSetRequery(ADataSet, aDSPParams, PreapreDataSet);
end;

function TdmMain.GetClientDataSet(aTag: integer): TClientDataSet;
begin
  case aTag of
    2: Result := cdsStoredProcCustom2;
    3: Result := cdsStoredProcCustom3;
    4: Result := cdsStoredProcCustom4;
    5: Result := cdsStoredProcCustom5;
    6: Result := cdsStoredProcCustom6;
    7: Result := cdsStoredProcCustom7;
    else Result := cdsStoredProcCustom1;
  end;
end;

function TdmMain.GetPrivileges: TObjectList<TObject>;
begin
  Result := fPrivileges;
end;

function TdmMain.HttpUserPrivilege(aTag: integer): boolean;
begin
  Result := FTCPIPServerMethods.HttpUserPrivilege(aTag);
end;

function TdmMain.IsAttachmentsDirectoryWriteable: Boolean;
begin
  Result := FTCPIPServerMethods.IsAttachmentsDirectoryWriteable;
end;

function TdmMain.IsCardFilesDirectoryWriteable: Boolean;
begin
  Result := FTCPIPServerMethods.IsCardFilesDirectoryWriteable;
end;

function TdmMain.IsSalesReportFilesDirectoryWriteable: Boolean;
begin
  Result := FTCPIPServerMethods.IsSalesReportFilesDirectoryWriteable;
end;

{$endregion}

{$region 'DataSnap Informations'}

function TdmMain.DataSnapConnectionCount: Integer;
begin
  Result := ClientMainDMUtil.DataSnapConnectionCount(FTCPIPServerMethods)
end;

function TdmMain.DataSnapVersion: string;
begin
  Result := ClientMainDMUtil.DataSnapVersion(FTCPIPServerMethods);
end;
{$endregion}


{$region 'DBTrans operations'}

function TdmMain.DBOpenCustomSQL(ADataSet: TDataSet;
  ACustomSQL: string): boolean;
begin
  DataSetClose(ADataSet);
  DataSetOpen(ADataSet,ACustomSQL);
  Result := ADataSet.Active;
end;

function TdmMain.DBTransBegin: String;
begin
  Result := ClientMainDMUtil.DBTransBegin;
  TSQLTransScriptRowList.Init(Result); // will be stored scripts for this new global transaction
end;

function TdmMain.DBTransCommit(Guid: String): boolean;
begin
  Result := TDBTransActions.TransScriptListCommit(Self) // save scripts from the list first
    and ClientMainDMUtil.DBTransCommit(Guid, FTCPIPServerMethods);
end;

function TdmMain.DBTransCommitAndResult(Guid: string): boolean;
begin
  Result := TDBTransActions.TransScriptListCommit(Self) // save scripts from the list first
    and ClientMainDMUtil.DBTransCommitAndResult(Guid, FTCPIPServerMethods);
end;

function TdmMain.DBTransResultClose: boolean;
begin
  Result := ClientMainDMUtil.DBTransResultClose(FTCPIPServerMethods);
end;

function TdmMain.DBTransRollback(Guid: String): boolean;
begin
  Result := ClientMainDMUtil.DBTransRollback(Guid, FTCPIPServerMethods);
end;

function TdmMain.DBTransScript(Guid, Script: string; const ARunPriority: Integer): Integer;
begin
  Result := ClientMainDMUtil.DBTransScript(Guid, Script, ARunPriority, FTCPIPServerMethods);
end;

function TdmMain.DBTransStoredProc(Guid, SchemaName, StroredProcName,
  Params: string; AResultIndex: Integer; AScriptGlobalParamName,
  AStoredProcOutParamName: String; const ARunPriority: Integer): string;
begin
  Result := ClientMainDMUtil.DBTransStoredProc(Guid, SchemaName,
    StroredProcName, Params, AResultIndex,
    AScriptGlobalParamName, AStoredProcOutParamName,
    ARunPriority,
    FTCPIPServerMethods);
end;

{$endregion}


{$region 'Prepare DataSets'}

//{$IFNDEF TURDUS}
function TdmMain.ParamsForRoadCardsSynchroExists: Boolean;
begin
  Result := FTCPIPServerMethods.ParamsForRoadCardsSynchroExists;
end;

procedure TdmMain.PreapreDataSet(ADataSet: TDataSet; aDSPParams: TDSPParams);
begin
  if not ClientDataSetPrepareUtil.ClientDataSetPrepare( ADataSet, aDSPParams ) then
  begin
     raise Exception.CreateFmt('There is not any paremter preparer for dataset "%s"!',[ADataSet.NAme]);
  end;
end;
//{$ENDIF}

procedure TdmMain.PreapreDataSet(ADataSet: TDataSet; Params: string);
begin
  if not ClientDataSetPrepareUtil.ClientDataSetPrepare( ADataSet, Params ) then
  begin
  if ADataSet.Name = 'cdsStoredProcPlaces' then PreparePlaces(Params)
  else if ADataSet.Name = 'cdsStoredProcPlacesPagination' then PreparePlacesPagination(Params)
  else if ADataSet.Name = 'cdsStoredProcPlacesForRide' then PreparePlacesForRide(Params)
  else if ADataSet.Name = 'cdsStorProcAutoCashier' then PrepareProviderAutoCashier(Params)
  else if ADataSet.Name = 'cdsStoredProcEmCardLoader' then PrepareEmCardLoader(Params)
  else if ADataSet.Name = 'cdsStoredProcEmCard' then PrepareEmCard(Params)
  else if ADataSet.Name = 'cdsStoredProcCalendar' then PrepareCalendar(Params)
  else if ADataSet.Name = 'cdsStoredProcRideDesignation' then PrepareRideDesignation(Params)
  else if ADataSet.Name = 'cdsStoredProcRoadsPagination' then PrepareRoads(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopsPagination' then PrepareBusStops(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopsDuplicatesPagination' then PrepareBusStopsDuplicates(Params)

  else if ADataSet.Name = 'cdsStoredProcPriceOnesScales' then PreparePriceOnesScales(Params)
  else if ADataSet.Name = 'cdsStoredProcFarePriceReductionAmountsNotUse' then PreparePriceReductionAmountsNotUse(Params)

  else if ADataSet.Name = 'cdsStoredProcPriceCitiesScales' then PreparePriceCitiesScales(Params)
  else if ADataSet.Name = 'cdsStoredProcFarePriceReductionCities' then PreparePriceReductionCities(Params)
  else if ADataSet.Name = 'cdsStoredProcFarePriceReductionAmounts' then PreparePriceReductionAmounts(Params)

  else if ADataSet.Name = 'cdsStoredProcPriceBasicCitiesScales' then PreparePriceBasicCitiesScales(Params)
  else if ADataSet.Name = 'cdsStoredProcBuses' then PrepareBuses(Params)
  else if ADataSet.Name = 'cdsStoredProcPriceMonthScales' then PreparePriceMonthScales(Params)
  else if ADataSet.Name = 'cdsStoredProcTicketZoneBusStops' then PrepareTicketZoneBusStops(Params)
  else if ADataSet.Name = 'cdsStoredProcPriceMonthCityScales' then PreparePriceMonthCityScales(Params)

  else if ADataSet.Name = 'cdsStoredProcLine' then PrepareLine(cdsStoredProcLine, Params)
  else if ADataSet.Name = 'cdsLine' then PrepareLine(cdsLine, Params)
  else if ADataSet.Name = 'cdsLinePagination' then PrepareLinePagination(Params)
  else if ADataSet.Name = 'cdsRide' then PrepareRide(cdsRide, Params)
  else if ADataSet.Name = 'cdsRidePagination' then PrepareRidePagination(Params)

  else if ADataSet.Name = 'cdsStoredProcBasicSearch' then PrepareBasicSearch(Params)
  else if ADataSet.Name = 'cdsStoredProcCurrenciesHistory' then PrepareCurrenciesHistory(Params)

  else if ADataSet.Name = 'cdsStoredProcDrivers' then PrepareDrivers(Params,0)
  else if ADataSet.Name = 'cdsStoredProcDrivers1' then PrepareDrivers(Params,1)
  else if ADataSet.Name = 'cdsStoredProcDriversChoice' then PrepareDrivers(Params,2)

  else if ADataSet.Name = 'cdsStoredProcBusPCStatus' then  PrepareBusPC(Params)
  else if ADataSet.Name = 'cdsStoredProcLPC_CompaniesByType' then  PrepareCompaniesByType(Params)
  else if ADataSet.Name = 'cdsStoredProcGovOffice' then PrepareGovOffice(Params)
  else if ADataSet.Name = 'cdsStoredProcHist' then PrepareHistory(Params)
  else if ADataSet.Name = 'cdsStoredProcPassanger' then PreparePassanger(Params)
  else if ADataSet.Name = 'cdsTicketRegisterHistory' then PrepareTicketRegisterHistory(Params)
  else if ADataSet.Name = 'cdsTicketRegisterCardNotAssigned' then PrepareTicketRegisterCardNotAssigned(Params)
  else if ADataSet.Name = 'cdsStorProcTicketRegister4SaleDevices' then PrepareTicketRegister4SaleDevices(Params)
  else if ADataSet.Name = 'cdsStoredProcCashDesks' then PrepareCashDesks(Params)
  else if ADataSet.Name = 'cdsStoredProcPLAN_RideRoadPoints' then PrepareRideRoadPoints(Params)
  else if ADataSet.Name = 'cdsCommunityPagination' then PrepareCommunityPagination(Params)
  else if ADataSet.Name = 'cdsStoredProcAdmin_ReportResultWhereReportTypeId' then PrepareReportResultType(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopTablePattern' then PrepareBusStopTablePattern(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopTablePatternChoice' then PrepareBusStopTablePatternChoice(Params)
  else if ADataSet.Name = 'cdsStoredProcTimeTableResult' then PrepareTimeTableResult(Params)
  else if ADataSet.Name = 'cdsStoredProcCompaniesWithoutHistory' then PrepareCompaniesWithoutHistory(Params)
  else if ADataSet.Name = 'cdsSalesReportPagination' then PrepareSalesReportPagination(Params)
  else if ADataSet.Name = 'cdsStoredProcRideForPair' then PrepareRideForPair(Params)
  else if ADataSet.Name = 'cdsStoredProcAdmin_ReportDefWhereReportTypeId' then PrepareReportDefType(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopFeeList' then PrepareBusStopFeeListPagination(Params)
  else if ADataSet.Name = 'cdsStoredProcTT_RideGetAllForCEDULA' then PrepareTT_RideGetAllForCEDULA(Params)
  else if ADataSet.Name = 'cdsStoredProcLPC_Parameters' then PrepareLPC_Parameters(Params)
  else if ADataSet.Name = 'cdsStoredProcBusStopSelectAssignedOrderByName' then PrepareBusStopSelectAssignedOrderByName(Params)
  else if ADataSet.Name = 'cdsStoredProcPlacesForBusStop' then PreparePlacesForBusStop(Params)
  else if ADataSet.Name = 'cdsCompanyHistory' then PrepareCompanyHistory(Params)
  else if ADataSet.Name = 'cdsStoredProcDriverGroups' then PrepareDriverGroups(Params)
 ;

  end;
end;

{$region 'detailed'}

procedure TdmMain.PreparePagination_BASE(AClientDataSet: TClientDataSet; const AParams: String);
var
  _Search: string;
  _countonly: String;
  _rowfrom: String;
  _rowto: String;
  _sortby: String;
  _filter: String;
  _Params: TStringDynArray;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  AClientDataSet.Params.Clear;
  if AClientDataSet.Params.Count = 0 then
    AClientDataSet.FetchParams;

  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@countonly', _Params, _countonly) then
    _countonly := '0';
  if not GetStrValueFromArrayVarName('@rowfrom', _Params, _rowfrom) then
    _rowfrom := '0';
  if not GetStrValueFromArrayVarName('@rowto', _Params, _rowto) then
    _rowto := IntToStr(MaxInt);
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';

  AClientDataSet.Params.ParamByName('@search').Value := _Search;
  AClientDataSet.Params.ParamByName('@countonly').Value := _countonly;
  AClientDataSet.Params.ParamByName('@rowfrom').Value := _rowfrom;
  AClientDataSet.Params.ParamByName('@rowto').Value := _rowto;
  AClientDataSet.Params.ParamByName('@sortby').Value := _sortby;
  AClientDataSet.Params.ParamByName('@filter').Value := _filter;


end;

procedure TdmMain.PreparePriceBasicCitiesScales(Params: string);
begin
  if cdsStoredProcPriceBasicCitiesScales.Params.Count = 0 then
    cdsStoredProcPriceBasicCitiesScales.FetchParams;
  cdsStoredProcPriceBasicCitiesScales.Params.ParamByName('@ID').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceCitiesScales(Params: string);
begin
    if cdsStoredProcPriceCitiesScales.Params.Count = 0 then
    cdsStoredProcPriceCitiesScales.FetchParams;
  cdsStoredProcPriceCitiesScales.Params.ParamByName('@ID').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceMonthCityScales(Params: string);
begin
  if cdsStoredProcPriceMonthCityScales.Params.Count = 0 then
    cdsStoredProcPriceMonthCityScales.FetchParams;
  cdsStoredProcPriceMonthCityScales.Params.ParamByName('@ID').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceMonthScales(Params: string);
begin
  if cdsStoredProcPriceMonthScales.Params.Count = 0 then
    cdsStoredProcPriceMonthScales.FetchParams;
  cdsStoredProcPriceMonthScales.Params.ParamByName('@ID').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceOnesScales(Params: string);
begin
  if cdsStoredProcPriceOnesScales.Params.Count = 0 then
    cdsStoredProcPriceOnesScales.FetchParams;
  cdsStoredProcPriceOnesScales.Params.ParamByName('@ID').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceReductionAmounts(Params: string);
begin
  if cdsStoredProcFarePriceReductionAmounts.Params.Count = 0 then
    cdsStoredProcFarePriceReductionAmounts.FetchParams;
  cdsStoredProcFarePriceReductionAmounts.Params.ParamByName('@PriceListId').AsString := Trim(Params);
end;

procedure TdmMain.PreparePriceReductionAmountsNotUse(Params: string);
begin
    if cdsStoredProcFarePriceReductionAmountsNotUse.Params.Count = 0 then
    cdsStoredProcFarePriceReductionAmountsNotUse.FetchParams;
  cdsStoredProcFarePriceReductionAmountsNotUse.Params.ParamByName('@PriceListId').AsString :=
    Trim(Params);
end;

procedure TdmMain.PreparePriceReductionCities(Params: string);
var
  _Params: TStringDynArray;
  _CompanyId, _ValidFrom, _ValidTo: string;
  _VFrom, _VTo: TDateTime;
begin
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@Company_id', _Params, _CompanyId) then
    _CompanyId := '';
  if not KMUtils.GetStrValueFromArrayVarName('@ValidFrom', _Params, _ValidFrom) then
    _ValidFrom := '';
  if not KMUtils.GetStrValueFromArrayVarName('@ValidTo', _Params, _ValidTo) then
    _ValidTo := '';

  if cdsStoredProcFarePriceReductionCities.Params.Count = 0 then
    cdsStoredProcFarePriceReductionCities.FetchParams;

  cdsStoredProcFarePriceReductionCities.Params.ParamByName('@Company_id').AsString := _CompanyId;
  if _ValidFrom <> '' then
    begin
      _VFrom := StrToDateTime(_ValidFrom);
      cdsStoredProcFarePriceReductionCities.Params.ParamByName('@ValidFrom').AsString :=
      FormatDateTime('yyyy-mm-dd hh:nn:ss', _VFrom);
    end
  else
    cdsStoredProcFarePriceReductionCities.Params.ParamByName('@ValidFrom').AsString := _ValidFrom;

  if _ValidTo <> '' then
    begin
      _VTo := StrToDateTime(_ValidTo);
      if _VTo = 0 then
        cdsStoredProcFarePriceReductionCities.Params.ParamByName('@ValidTo').AsString := ''
      else
        cdsStoredProcFarePriceReductionCities.Params.ParamByName('@ValidTo').AsString :=
        FormatDateTime('yyyy-mm-dd hh:nn:ss', _VTo);
    end
  else
    cdsStoredProcFarePriceReductionCities.Params.ParamByName('@ValidTo').AsString := _ValidTo;
end;

procedure TdmMain.PrepareProviderAutoCashier(Params: string);
begin
  if cdsStorProcAutoCashier.Params.Count = 0 then
    cdsStorProcAutoCashier.FetchParams;
  if StrToIntDef(Params, -1) <> -1 then
    cdsStorProcAutoCashier.Params.ParamByName('@ACType').AsString := Trim(Params);
end;

procedure TdmMain.PrepareReportResultType(AParams: string);
var
  PR : TStringDynArray;
begin
  if cdsStoredProcAdmin_ReportResultWhereReportTypeId.Params.Count = 0 then
    cdsStoredProcAdmin_ReportResultWhereReportTypeId.FetchParams;

  PR := SplitString(AParams, ',');
  if Length(PR) = 1 then
  begin
    SetLength(PR, 2);
    PR[1] := '0';
  end;

  cdsStoredProcAdmin_ReportResultWhereReportTypeId.Params.ParamByName
    ('@ReportType_Id').AsString := PR[0];
  cdsStoredProcAdmin_ReportResultWhereReportTypeId.Params.ParamByName
      ('@ReportOwner_ID').AsString := PR[1];
end;

procedure TdmMain.PrepareRide(aDataSet: TClientDataSet; AParams: string);
begin
  if aDataSet.Params.Count=0 then
    aDataSet.FetchParams;
  if Trim(AParams)='' then
    AParams := '0';
  aDataSet.Params.ParamByName('@tt_id').AsString := AParams;
end;

procedure TdmMain.PrepareRideDesignation(Params: string);
begin
  if cdsStoredProcRideDesignation.Params.Count = 0 then
    cdsStoredProcRideDesignation.FetchParams;
  StoredProcPrepareParams(cdsStoredProcRideDesignation.Params, Params, #13#10, #13);
end;

procedure TdmMain.PrepareReportDefType(AParams: string);
begin
  if cdsStoredProcAdmin_ReportDefWhereReportTypeId.Params.Count = 0 then
    cdsStoredProcAdmin_ReportDefWhereReportTypeId.FetchParams;
  cdsStoredProcAdmin_ReportDefWhereReportTypeId.Params.ParamByName('@ReportType_Id').AsString := Trim(AParams);
end;

procedure TdmMain.PrepareRideForPair(Params: string);
var
  _Params: TStringDynArray;
  _Search: string;
  _RideId: integer;
begin
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetIntValueFromArrayVarName('@ride_id', _Params, _RideId) then
    _RideId := 0;

  if cdsStoredProcRideForPair.Params.Count = 0 then
    cdsStoredProcRideForPair.FetchParams;

  cdsStoredProcRideForPair.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcRideForPair.Params.ParamByName('@ride_id').AsInteger := _RideId;
end;

procedure TdmMain.PrepareRidePagination(AParams: string);
var
  _Params: TStringDynArray;
  _search, _sortby, _filter: string;
  i, j, k, x: integer;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  if cdsRidePagination.Params.Count = 0 then
    cdsRidePagination.FetchParams;


  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, j) then
    j := 0;
  if not GetIntValueFromArrayVarName('@tt_id', _Params, k) then
    k := 0;
  if not GetIntValueFromArrayVarName('@countonly', _Params, x) then
    x := 0;

  cdsRidePagination.Params.ParamByName('@search').AsString := _Search;
  cdsRidePagination.Params.ParamByName('@sortby').AsString := _sortby;
  cdsRidePagination.Params.ParamByName('@filter').AsString := _filter;
  cdsRidePagination.Params.ParamByName('@rowfrom').AsInteger := i;
  cdsRidePagination.Params.ParamByName('@rowto').AsInteger := j;
  cdsRidePagination.Params.ParamByName('@tt_id').AsInteger := k;
  cdsRidePagination.Params.ParamByName('@countonly').AsInteger := x;
end;

procedure TdmMain.PrepareRideRoadPoints(Params: string);
var
  _Params: TStringDynArray;
  _CompanyId, _PlaceId: string;
begin
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@company_id', _Params, _CompanyId) then
    _CompanyId := '';
  if not KMUtils.GetStrValueFromArrayVarName('@place_id', _Params, _PlaceId) then
    _PlaceId := '';

  if cdsStoredProcPLAN_RideRoadPoints.Params.Count = 0 then
    cdsStoredProcPLAN_RideRoadPoints.FetchParams;

  cdsStoredProcPLAN_RideRoadPoints.Params.ParamByName('@company_id').AsString := _CompanyId;
  cdsStoredProcPLAN_RideRoadPoints.Params.ParamByName('@place_id').AsString := _PlaceId;
end;


procedure TdmMain.PrepareRoads(Params: string);
begin
  if cdsStoredProcRoadsPagination.Params.Count = 0 then
    cdsStoredProcRoadsPagination.FetchParams;
  StoredProcPrepareParams(cdsStoredProcRoadsPagination.Params, Params, #13#10, #13);
end;

procedure TdmMain.PrepareSalesReportPagination(Params: string);
begin
  PreparePagination_BASE(cdsSalesReportPagination, Params);
end;

procedure TdmMain.PrepareTicketRegister4SaleDevices(Params: string);
begin
    if cdsStorProcTicketRegister4SaleDevices.Params.Count = 0 then
    cdsStorProcTicketRegister4SaleDevices.FetchParams;
  if StrToIntDef(Params, -1) <> -1 then
    cdsStorProcTicketRegister4SaleDevices.Params.ParamByName('@Status')
      .AsString := Trim(Params);
end;

procedure TdmMain.PrepareTicketRegisterCardNotAssigned(Params: string);
begin
  if cdsTicketRegisterCardNotAssigned.Params.Count = 0 then
    cdsTicketRegisterCardNotAssigned.FetchParams;
  cdsTicketRegisterCardNotAssigned.Params.ParamByName('@DriverID').AsString :=  Trim(Params);
end;

procedure TdmMain.PrepareTicketRegisterHistory(Params: string);
begin
  if cdsTicketRegisterHistory.Params.Count = 0 then
    cdsTicketRegisterHistory.FetchParams;
  cdsTicketRegisterHistory.Params.ParamByName('@ID').AsString :=  Trim(Params);
end;

procedure TdmMain.PrepareTicketZoneBusStops(Params: string);
var
  _ID, _Search: string;
  _Params: TStringDynArray;
begin
  cdsStoredProcTicketZoneBusStops.Params.clear;
  if cdsStoredProcTicketZoneBusStops.Params.Count = 0 then
    cdsStoredProcTicketZoneBusStops.FetchParams;
  _Params := SplitString(Params, ',');

  if not KMUtils.GetStrValueFromArrayVarName('ID', _Params, _ID) then
    _ID := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Search', _Params, _Search) then
    _Search := '';

  cdsStoredProcTicketZoneBusStops.Params.ParamByName('@ID').AsString := _ID;
  cdsStoredProcTicketZoneBusStops.Params.ParamByName('@Search').AsString := _Search;
end;

procedure TdmMain.PrepareTimeTableResult(AParams: string);
var
  _Params: TStringDynArray;
  _search, _sortby, _filter: string;
  i, j, k, l: integer;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');
  cdsStoredProcTimeTableResult.Params.Clear;
  if cdsStoredProcTimeTableResult.Params.Count = 0 then
    cdsStoredProcTimeTableResult.FetchParams;

  if not GetIntValueFromArrayVarName('@Type', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@TimeTableID', _Params, j) then
    j := 0;
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, k) then
    k := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, l) then
    l := 0;
  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';

  cdsStoredProcTimeTableResult.Params.ParamByName('@Type').AsInteger := i;

  cdsStoredProcTimeTableResult.Params.ParamByName('@TimeTableID').AsInteger := j;
  cdsStoredProcTimeTableResult.Params.ParamByName('@rowfrom').AsInteger := k;
  cdsStoredProcTimeTableResult.Params.ParamByName('@rowto').AsInteger := l;
  cdsStoredProcTimeTableResult.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcTimeTableResult.Params.ParamByName('@sortby').AsString := _sortby;
  cdsStoredProcTimeTableResult.Params.ParamByName('@filter').AsString := _filter;
end;

procedure TdmMain.PreparePassanger(Params: string);
begin
  if cdsStoredProcPassanger.Params.Count = 0 then
    cdsStoredProcPassanger.FetchParams;
  cdsStoredProcPassanger.Params.ParamByName('@search').AsString := Trim(Params);
end;

procedure TdmMain.PreparePlaces(Params: string);
begin
  if cdsStoredProcPlaces.Params.Count = 0 then
    cdsStoredProcPlaces.FetchParams;
  cdsStoredProcPlaces.Params.ParamByName('@search').AsString := Trim(Params);
end;

procedure TdmMain.PreparePlacesForBusStop(AParams: string);
var
  _Params: TStringDynArray;
  _search, _sortby, _filter: string;
  i, j: integer;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  if cdsStoredProcPlacesForBusStop.Params.Count=0 then
  cdsStoredProcPlacesForBusStop.FetchParams;

 _search :=  cdsStoredProcPlacesForBusStop.CommandText;

  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, j) then
    j := 0;

  cdsStoredProcPlacesForBusStop.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcPlacesForBusStop.Params.ParamByName('@sortby').AsString := _sortby;
  cdsStoredProcPlacesForBusStop.Params.ParamByName('@filter').AsString := _filter;
  cdsStoredProcPlacesForBusStop.Params.ParamByName('@rowfrom').AsInteger := i;
  cdsStoredProcPlacesForBusStop.Params.ParamByName('@rowto').AsInteger := j;

end;

procedure TdmMain.PreparePlacesForRide(Params: string);
var
  _Params: TStringDynArray;
  _Search, _CompanyId, _TimeTableId: string;
begin
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetStrValueFromArrayVarName('@company_id', _Params, _CompanyId) then
    _CompanyId := '';
  if not KMUtils.GetStrValueFromArrayVarName('@timetable_id', _Params, _TimeTableId) then
    _TimeTableId := '';

  if cdsStoredProcPlacesForRide.Params.Count = 0 then
    cdsStoredProcPlacesForRide.FetchParams;

  cdsStoredProcPlaces.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcPlaces.Params.ParamByName('@company_id').AsString := _CompanyId;
  cdsStoredProcPlaces.Params.ParamByName('@timetable_id').AsString := Trim(_TimeTableId);
end;

procedure TdmMain.PreparePlacesPagination(Params: string);
var
  _Params: TStringDynArray;
  _search, _sortby, _filter: string;
  i, j: integer;
begin
  if Pos('|', Params) > 0 then
    _Params := SplitString(Params, '|')
  else
    _Params := SplitString(Params, ',');

  if cdsStoredProcPlacesPagination.Params.Count = 0 then
    cdsStoredProcPlacesPagination.FetchParams;


  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, j) then
    j := 0;

  cdsStoredProcPlacesPagination.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcPlacesPagination.Params.ParamByName('@sortby').AsString := _sortby;
  cdsStoredProcPlacesPagination.Params.ParamByName('@filter').AsString := _filter;
  cdsStoredProcPlacesPagination.Params.ParamByName('@rowfrom').AsInteger := i;
  cdsStoredProcPlacesPagination.Params.ParamByName('@rowto').AsInteger := j;
end;

function TdmMain.PrepareBasicSearch: boolean;
begin
  Result := FTCPIPServerMethods.PrepareBasicSearch;
end;

procedure TdmMain.PrepareBuses(Params: string);
var
  SL: TStringList;
begin
  SL := TStringList.Create;
  try
    SL.Delimiter := ',';
    SL.DelimitedText := Params;

    if cdsStoredProcBuses.Params.Count = 0 then
      cdsStoredProcBuses.FetchParams;

    cdsStoredProcBuses.Params.ParamByName('@Type').AsString := Trim(SL.Strings[0]);

    if SL.Count > 1 then
      cdsStoredProcBuses.Params.ParamByName('@Company_ID').AsString := Trim(SL.Strings[1])
    else
      cdsStoredProcBuses.Params.ParamByName('@Company_ID').AsString := '0';


    if SL.Count > 2 then
    cdsStoredProcBuses.Params.ParamByName('@search').AsString := Trim(SL.Strings[2]);

  finally
    SL.Free;
  end;
end;

procedure TdmMain.PrepareBasicSearch(Params: string);
var
  _Tbl: string;
  _Search, _Param, _CompanyId: string;
  _Params: TStringDynArray;
begin
  if cdsStoredProcBasicSearch.Params.Count = 0 then
    cdsStoredProcBasicSearch.FetchParams;
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@Tbl', _Params, _Tbl) then
    _Tbl := '';
  if not KMUtils.GetStrValueFromArrayVarName('@Search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetStrValueFromArrayVarName('@Param', _Params, _Param) then
    _Param := '';
  if not KMUtils.GetStrValueFromArrayVarName('@CompanyId', _Params, _CompanyId) then
    _CompanyId := '';

  cdsStoredProcBasicSearch.Params.ParamByName('@Tbl').AsString := _Tbl;
  cdsStoredProcBasicSearch.Params.ParamByName('@Search').AsString := _Search;
  cdsStoredProcBasicSearch.Params.ParamByName('@Param').AsString := _Param;
  cdsStoredProcBasicSearch.Params.ParamByName('@CompanyId').AsString := _CompanyId;
end;

procedure TdmMain.PrepareCalendar(Params: string);
begin
  if cdsStoredProcCalendar.Params.Count = 0 then
    cdsStoredProcCalendar.FetchParams;
  cdsStoredProcCalendar.Params.ParamByName('@year').AsString := Trim(Params);
end;

procedure TdmMain.PrepareCashDesks(Params: string);
begin
  if cdsStoredProcCashDesks.Params.Count = 0 then
    cdsStoredProcCashDesks.FetchParams;
  cdsStoredProcCashDesks.Params.ParamByName('@Company_ID').AsString := Trim
    (Params);
end;

procedure TdmMain.PrepareCompaniesByType(AParams: string);
var
  _CompanyType_Id: string;
  _LicenceCompany_Id: string;
  _Params: TStringDynArray;
begin
  cdsStoredProcLPC_CompaniesByType.Params.Clear;
  if cdsStoredProcLPC_CompaniesByType.Params.Count = 0 then
    cdsStoredProcLPC_CompaniesByType.FetchParams;

  _Params := SplitString(AParams, ',');

  if not KMUtils.GetStrValueFromArrayVarName('CompanyType_Id', _Params, _CompanyType_Id) then
    _CompanyType_Id := '0';
  if not KMUtils.GetStrValueFromArrayVarName('LicenceCompany_Id', _Params, _LicenceCompany_Id) then
    _LicenceCompany_Id := '0';


  cdsStoredProcLPC_CompaniesByType.Params.ParamByName('@CompanyType_Id').Value := _CompanyType_Id;
  cdsStoredProcLPC_CompaniesByType.Params.ParamByName('@LicenceCompany_Id').Value := _LicenceCompany_ID;
end;

procedure TdmMain.PrepareCommunityPagination(AParams: string);
var
  _Params: TStringDynArray;
  _Search, _Filter, _Sortby: string;
  i, j: Integer;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  if cdsCommunityPagination.Params.Count = 0 then
    cdsCommunityPagination.FetchParams;

  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, j) then
    j := 0;
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _Filter := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _Sortby := '';

  cdsCommunityPagination.Params.ParamByName('@search').AsString := _Search;
  cdsCommunityPagination.Params.ParamByName('@sortby').AsString := _Sortby;
  cdsCommunityPagination.Params.ParamByName('@filter').AsString := _Filter;
  cdsCommunityPagination.Params.ParamByName('@rowfrom').AsInteger := i;
  cdsCommunityPagination.Params.ParamByName('@rowto').AsInteger := j;
end;

function TdmMain.PrepareCompaniesByType: Boolean;
begin
  Result := FTCPIPServerMethods.PrepareCompaniesByType;
end;

procedure TdmMain.PrepareCompaniesWithoutHistory(Params: string);
var
  _Params : TStringDynArray;
  _Search, _Filter: string;
  _LicCompany: integer;
  _HierachyType: integer;
begin

  if cdsStoredProcCompaniesWithoutHistory.Params.Count = 0 then
    cdsStoredProcCompaniesWithoutHistory.FetchParams;
  _Params := SplitString(Params, ',');
  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _Filter := '';
  if not GetIntValueFromArrayVarName('@Parent_ID', _Params, _LicCompany) then
    _LicCompany := 0;
  if not GetIntValueFromArrayVarName('@CompanyHierarchy_ID', _Params, _HierachyType) then
    _HierachyType := 0;

  cdsStoredProcCompaniesWithoutHistory.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcCompaniesWithoutHistory.Params.ParamByName('@filter').AsString := _Filter;
  cdsStoredProcCompaniesWithoutHistory.Params.ParamByName('@Parent_ID').AsInteger := _LicCompany;
  cdsStoredProcCompaniesWithoutHistory.Params.ParamByName('@CompanyHierarchy_ID').AsInteger := _HierachyType;
end;

procedure TdmMain.PrepareCompanyHistory(AParams: string);
begin
  if cdsCompanyHistory.Params.Count = 0 then
    cdsCompanyHistory.FetchParams;

  cdsCompanyHistory.Params.ParamByName('@ID').AsString := Trim(AParams);
end;

procedure TdmMain.PrepareCurrenciesHistory(Params: string);
begin
  if cdsStoredProcCurrenciesHistory.Params.Count = 0 then
    cdsStoredProcCurrenciesHistory.FetchParams;
  cdsStoredProcCurrenciesHistory.Params.ParamByName('@Currency_ID').AsString := Trim(Params);
end;

procedure TdmMain.PrepareDriverGroups(Params: string);
var
  _Search : string;
  _Mode : integer;
  _Params : TStringDynArray;
begin
  if cdsStoredProcDriverGroups.Params.Count = 0 then
    cdsStoredProcDriverGroups.FetchParams;
  _Params := SplitString(Params, ',');
  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetIntValueFromArrayVarName('@Mode', _Params, _Mode) then
    _Mode:=3;

  cdsStoredProcDriverGroups.Params.ParamByName('@search').AsString := _Search;
  cdsStoredProcDriverGroups.Params.ParamByName('@Mode').AsInteger := _Mode;
end;

procedure TdmMain.PrepareDrivers(Params: string; TypeDS : Integer);
var
  _Params: TStringDynArray;
  _DriverType_ID, _Company_ID, _CheckHRSystemEndDate, _Has_DriveExamXDriver, _rowfrom, _rowto, _sortby, _CntOnly, _Filter, _Turdus: string;
{$IFNDEF ADMINTOOL}
  _EmployValue: string;
  {$ENDIF}
  _search : String;
  A_cdsStoredProcDrivers : TClientDataSet;
begin
  case TypeDS of
    0: A_cdsStoredProcDrivers:=cdsStoredProcDrivers;
    1: A_cdsStoredProcDrivers:=cdsStoredProcDrivers1;
    2: A_cdsStoredProcDrivers:=cdsStoredProcDriversChoice;
  else
    Exit;
  end;

  A_cdsStoredProcDrivers.Filtered := false;
  if A_cdsStoredProcDrivers.Params.Count = 0 then
    A_cdsStoredProcDrivers.FetchParams;

  if Pos('|', Params) > 0 then
    _Params := SplitString(Params, '|')
  else
    _Params := SplitString(Params, #13'');

  if not KMUtils.GetStrValueFromArrayVarName('DriverType_ID', _Params,
    _DriverType_ID) then
    _DriverType_ID := IntToStr(Integer(ptDriver));
  if not KMUtils.GetStrValueFromArrayVarName('Company_ID', _Params,
    _Company_ID) then
    _Company_ID := '0';
  if not KMUtils.GetStrValueFromArrayVarName('CheckHRSystemEndDate', _Params,
    _CheckHRSystemEndDate) then
    _CheckHRSystemEndDate := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetStrValueFromArrayVarName('Has_DriveExamXDriver', _Params, _Has_DriveExamXDriver) then
    _Has_DriveExamXDriver := '';
  if not KMUtils.GetStrValueFromArrayVarName('rowfrom', _Params, _rowfrom) then
    _rowfrom := '0';
  if not KMUtils.GetStrValueFromArrayVarName('rowto', _Params, _rowto) then
    _rowto := IntToStr(High(Integer));
  if not KMUtils.GetStrValueFromArrayVarName('sortby', _Params, _sortby) then
    _sortby := '';
  if not KMUtils.GetStrValueFromArrayVarName('CntOnly', _Params, _CntOnly) then
    _CntOnly := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Filter', _Params, _Filter) then
    _Filter := '';

  if not KMUtils.GetStrValueFromArrayVarName('Turdus', _Params, _Turdus) then
    _Turdus := '0';
{$IFNDEF ADMINTOOL}
  if not KMUtils.GetStrValueFromArrayVarName('EmployValue', _Params, _EmployValue) then
    _EmployValue := '0';
{$ENDIF}

  A_cdsStoredProcDrivers.Params.ParamByName('@DriverType_ID').AsString :=
    _DriverType_ID;
  A_cdsStoredProcDrivers.Params.ParamByName('@Company_ID').AsString :=
    _Company_ID;
  A_cdsStoredProcDrivers.Params.ParamByName('@CheckHRSystemEndDate').AsString :=
    _CheckHRSystemEndDate;
  A_cdsStoredProcDrivers.Params.ParamByName('@Search').Value := _Search;
  A_cdsStoredProcDrivers.Params.ParamByName('@Has_DriveExamXDriver').AsString :=
    _Has_DriveExamXDriver;
  A_cdsStoredProcDrivers.Params.ParamByName('@rowfrom').AsString :=
    _rowfrom;
  A_cdsStoredProcDrivers.Params.ParamByName('@rowto').AsString :=
    _rowto;
  A_cdsStoredProcDrivers.Params.ParamByName('@sortby').AsString :=
    _sortby;
  A_cdsStoredProcDrivers.Params.ParamByName('@CntOnly').AsString :=
    _CntOnly;
  A_cdsStoredProcDrivers.Params.ParamByName('@Filter').AsString :=
    _Filter;
  A_cdsStoredProcDrivers.Params.ParamByName('@Turdus').AsString :=
    _Turdus;
{$IFNDEF ADMINTOOL}
  A_cdsStoredProcDrivers.Params.ParamByName('@EmployValue').AsString := _EmployValue
{$ENDIF}
end;

procedure TdmMain.PrepareBusPC(Params: string);
begin
  if cdsStoredProcBusPCStatus.Params.Count = 0 then
    cdsStoredProcBusPCStatus.FetchParams;
  if StrToIntDef(Params, -1) <> -1 then
    cdsStoredProcBusPCStatus.Params.ParamByName('@BusPCType').AsString := Trim(Params);
end;

procedure TdmMain.PrepareTT_RideGetAllForCEDULA(Params: string);
begin
  if cdsStoredProcTT_RideGetAllForCEDULA.Params.Count = 0 then
    cdsStoredProcTT_RideGetAllForCEDULA.FetchParams;
end;

procedure TdmMain.PrepareBusStopFeeListPagination(const AParams: String);
var
  _Search: string;
  _countonly: String;
  _rowfrom: String;
  _rowto: String;
  _sortby: String;
  _id: String;
  _Params: TStringDynArray;
begin
  cdsStoredProcBusStopFeeList.Params.Clear;
  if cdsStoredProcBusStopFeeList.Params.Count = 0 then
    cdsStoredProcBusStopFeeList.FetchParams;

  _Params := SplitString(AParams, '|');
  if not KMUtils.GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetStrValueFromArrayVarName('@countonly', _Params, _countonly) then
    _countonly := '0';
  if not KMUtils.GetStrValueFromArrayVarName('@rowfrom', _Params, _rowfrom) then
    _rowfrom := '0';
  if not KMUtils.GetStrValueFromArrayVarName('@rowto', _Params, _rowto) then
    _rowto := IntToStr(MaxInt);
  if not KMUtils.GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not KMUtils.GetStrValueFromArrayVarName('@id', _Params, _id) then
    _id := '';

  cdsStoredProcBusStopFeeList.Params.ParamByName('@search').Value := _Search;
  cdsStoredProcBusStopFeeList.Params.ParamByName('@countonly').Value := _countonly;
  cdsStoredProcBusStopFeeList.Params.ParamByName('@rowfrom').Value := _rowfrom;
  cdsStoredProcBusStopFeeList.Params.ParamByName('@rowto').Value := _rowto;
  cdsStoredProcBusStopFeeList.Params.ParamByName('@sortby').Value := _sortby;
  cdsStoredProcBusStopFeeList.Params.ParamByName('@id').Value := _id;
end;

procedure TdmMain.PrepareBusStops(Params: string);
begin
  if cdsStoredProcBusStopsPagination.Params.Count = 0 then
    cdsStoredProcBusStopsPagination.FetchParams;
  StoredProcPrepareParams(cdsStoredProcBusStopsPagination.Params, Params, #13#10, #13);
end;

procedure TdmMain.PrepareBusStopsDuplicates(Params: string);
begin
  if cdsStoredProcBusStopsDuplicatesPagination.Params.Count = 0 then
    cdsStoredProcBusStopsDuplicatesPagination.FetchParams;
  StoredProcPrepareParams(cdsStoredProcBusStopsDuplicatesPagination.Params, Params, #13#10, #13);
end;

procedure TdmMain.PrepareBusStopSelectAssignedOrderByName(Params: String);
var
  _Search, _kind, _Company_ID: string;
  _Params: TStringDynArray;
begin
  if cdsStoredProcBusStopSelectAssignedOrderByName.Params.Count = 0 then
    cdsStoredProcBusStopSelectAssignedOrderByName.FetchParams;
  _Params := SplitString(Params, ', ');
  if not KMUtils.GetStrValueFromArrayVarName('@Company_Id', _Params, _Company_ID) then
    _Company_ID := '0';
  if not KMUtils.GetStrValueFromArrayVarName('@Search', _Params, _Search) then
    _Search := '%';
  if not KMUtils.GetStrValueFromArrayVarName('@kind', _Params, _kind) then
    _kind := '0';

  cdsStoredProcBusStopSelectAssignedOrderByName.Params.ParamByName('@Company_Id').AsString := _Company_ID;
  cdsStoredProcBusStopSelectAssignedOrderByName.Params.ParamByName('@kind').AsString := _kind;
  cdsStoredProcBusStopSelectAssignedOrderByName.Params.ParamByName('@Search').AsString := _Search;
end;


procedure TdmMain.PrepareBusStopTablePattern(AParams: string);
var
  _Type_ID, _Search: string;
  _Params: TStringDynArray;
begin
  cdsStoredProcBusStopTablePattern.Params.clear;
  if cdsStoredProcBusStopTablePattern.Params.Count = 0 then
    cdsStoredProcBusStopTablePattern.FetchParams;
  _Params := SplitString(AParams, ',');

  if not KMUtils.GetStrValueFromArrayVarName('Type_ID', _Params, _Type_ID) then
    _Type_ID := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Search', _Params, _Search) then
    _Search := '';

  cdsStoredProcBusStopTablePattern.Params.ParamByName('@Type').AsString := _Type_ID;
  cdsStoredProcBusStopTablePattern.Params.ParamByName('@Search').AsString := _Search;
end;

procedure TdmMain.PrepareBusStopTablePatternChoice(AParams: string);
var
  _Type_ID, _Search: string;
  _Params: TStringDynArray;
begin
  cdsStoredProcBusStopTablePatternChoice.Params.clear;
  if cdsStoredProcBusStopTablePatternChoice.Params.Count = 0 then
    cdsStoredProcBusStopTablePatternChoice.FetchParams;
  _Params := SplitString(AParams, ',');

  if not KMUtils.GetStrValueFromArrayVarName('Type_ID', _Params, _Type_ID) then
    _Type_ID := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Search', _Params, _Search) then
    _Search := '';

  cdsStoredProcBusStopTablePatternChoice.Params.ParamByName('@Type').AsString := _Type_ID;
  cdsStoredProcBusStopTablePatternChoice.Params.ParamByName('@Search').AsString := _Search;
end;

procedure TdmMain.PrepareEmCard(AParams: String);
var
  _Search: string;
  _rowfrom, _rowto, _sortby, _cnt : string;
  _Params: TStringDynArray;
begin
  cdsStoredProcEmCard.Params.Clear;
  if cdsStoredProcEmCard.Params.Count = 0 then
    cdsStoredProcEmCard.FetchParams;

  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
  _Params := SplitString(AParams, #13'');

  if not KMUtils.GetStrValueFromArrayVarName('@Search', _Params, _Search) then
    _Search := '';

  if not KMUtils.GetStrValueFromArrayVarName('@rowfrom', _Params, _rowfrom) then
    _rowfrom := '0';
  if not KMUtils.GetStrValueFromArrayVarName('@rowto', _Params, _rowto) then
    _rowto := IntToStr(High(Integer));
  if not KMUtils.GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not KMUtils.GetStrValueFromArrayVarName('@CountOnly', _Params, _cnt) then
    _cnt := '0';

  cdsStoredProcEmCard.Params.ParamByName('@Search').AsString := _Search;
  cdsStoredProcEmCard.Params.ParamByName('@rowfrom').AsString := _rowfrom;
  cdsStoredProcEmCard.Params.ParamByName('@rowto').AsString := _rowto;
  cdsStoredProcEmCard.Params.ParamByName('@sortby').AsString := _sortby;
  cdsStoredProcEmCard.Params.ParamByName('@CountOnly').AsString := _cnt;

end;

procedure TdmMain.PrepareEmCardLoader( AParams: String);
begin
  if cdsStoredProcEmCardLoader.Params.Count = 0 then cdsStoredProcEmCardLoader.FetchParams;
  cdsStoredProcEmCardLoader.Params.ParamByName('@Type').AsString := AParams;
end;

procedure TdmMain.PrepareGovOffice(AParams: string);
var
  _GovType: string;
  _Company_Id: string;
  _Search: string;
  _Deleted, _rowfrom, _rowto, _sortby, _Filter, _cnt : string;
  _Params: TStringDynArray;
begin
  cdsStoredProcGovOffice.Params.Clear;
  if cdsStoredProcGovOffice.Params.Count = 0 then
    cdsStoredProcGovOffice.FetchParams;

  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
  {if Pos(',', AParams) > 0 then
    _Params := SplitString(AParams, ',') -- w nazwie firmy mog¹ byæ przecinki
  else
    _Params := SplitString(AParams, #13''); }
  _Params := SplitString(AParams, #13'');

  if not KMUtils.GetStrValueFromArrayVarName('GovType', _Params, _GovType) then
    _GovType := '0';
  if not KMUtils.GetStrValueFromArrayVarName('Search', _Params, _Search) then
    _Search := '';
  if not KMUtils.GetStrValueFromArrayVarName('Deleted', _Params, _Deleted) then
    _Deleted := '2';
  if not KMUtils.GetStrValueFromArrayVarName('Company_Id', _Params, _Company_Id) then
    _Company_Id := '0';
  if not KMUtils.GetStrValueFromArrayVarName('rowfrom', _Params, _rowfrom) then
    _rowfrom := '0';
  if not KMUtils.GetStrValueFromArrayVarName('rowto', _Params, _rowto) then
    _rowto := IntToStr(High(Integer));
  if not KMUtils.GetStrValueFromArrayVarName('sortby', _Params, _sortby) then
    _sortby := '';
  if not KMUtils.GetStrValueFromArrayVarName('Filter', _Params, _Filter) then
    _Filter := '';
  if not KMUtils.GetStrValueFromArrayVarName('CntOnly', _Params, _cnt) then
    _cnt := '0';

  cdsStoredProcGovOffice.Params.ParamByName('@GovType').AsString := _GovType;
  cdsStoredProcGovOffice.Params.ParamByName('@Search').AsString := _Search;
  cdsStoredProcGovOffice.Params.ParamByName('@Deleted').AsString := _Deleted;
  cdsStoredProcGovOffice.Params.ParamByName('@Company_Id').AsString := _Company_Id;
  cdsStoredProcGovOffice.Params.ParamByName('@rowfrom').AsString := _rowfrom;
  cdsStoredProcGovOffice.Params.ParamByName('@rowto').AsString := _rowto;
  cdsStoredProcGovOffice.Params.ParamByName('@sortby').AsString := _sortby;
  cdsStoredProcGovOffice.Params.ParamByName('@Filter').AsString := _Filter;
  cdsStoredProcGovOffice.Params.ParamByName('@CntOnly').AsString := _cnt;
end;

procedure TdmMain.PrepareHistory(Params: string);
var
  SL: TStringList;
  i: Integer;
begin
  if cdsStoredProcHist.Params.Count = 0 then
    cdsStoredProcHist.FetchParams;
  if Trim(Params) <> '' then
  begin
    SL := TStringList.Create;
    try
      SL.Text := Trim(Params);
      try
        cdsStoredProcHist.Params.ParamByName('@date_from').Value := SL.Strings[0];
      except
        cdsStoredProcHist.Params.ParamByName('@date_from').Value := MSSQLFormatDate(date(), 0);
      end;
      try
        cdsStoredProcHist.Params.ParamByName('@date_to').Value := SL.Strings[1];
      except
        cdsStoredProcHist.Params.ParamByName('@date_to').Value := MSSQLFormatDate(date(), 0);
      end;
      try
        cdsStoredProcHist.Params.ParamByName('@only_errors').Value :=
          StrToIntDef(SL.Strings[2], 0);
      except
        cdsStoredProcHist.Params.ParamByName('@only_errors').Value := 0;
      end;
      try
        if SL.Count > 3 then begin
          i := StrToIntDef(SL.Strings[3], 0);
          if i > 0 then
            cdsStoredProcHist.Params.ParamByName('@user_id').Value := i
          else
            cdsStoredProcHist.Params.ParamByName('@user_id').Clear;
        end
        else cdsStoredProcHist.Params.ParamByName('@user_id').Clear;
      except
        cdsStoredProcHist.Params.ParamByName('@user_id').Clear;
      end;
    finally
      SL.Free;
    end;
  end;
end;

procedure TdmMain.PrepareLine(aDataSet: TClientDataSet; AParams: string);
var
  _Params: TStringDynArray;
  _timeTable : string;
  _lineStatus : string;
  _ValidFrom, _ValidTo, CompanyIDs: string;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  if aDataSet.Params.Count=0 then
    aDataSet.FetchParams;


 if not KMUtils.GetStrValueFromArrayVarName('@timetable_id', _Params, _timeTable) then
    _timeTable := '0';

 if not KMUtils.GetStrValueFromArrayVarName('@LineStatus', _Params, _lineStatus) then
    _lineStatus := '';

  if not KMUtils.GetStrValueFromArrayVarName('@ValidFrom', _Params, _ValidFrom) then
  _ValidFrom := '';
 if not KMUtils.GetStrValueFromArrayVarName('@ValidTo', _Params, _ValidTo) then
  _ValidTo := '';

   if not KMUtils.GetStrValueFromArrayVarName('@CompanyIDs', _Params, CompanyIDs) then
    CompanyIDs := '';

  {
  if Length(_Params) = 2 then
  begin
    _timeTable := _Params[0];
    _lineStatus := _Params[1];
  end
  else
  if Length(_Params) = 1 then
    _timeTable := _Params[0];
  }
  CompanyIDs := StringReplace(CompanyIDs,';',',',[rfReplaceAll]);

  if Trim(AParams)='' then
    _timeTable := '0';

  aDataSet.Params.ParamByName('@TimeTable_ID').AsString := _timeTable;
  aDataSet.Params.ParamByName('@LineStatus').AsString := _lineStatus; // AParams;
  aDataSet.Params.ParamByName('@ValidFrom').AsString := _ValidFrom;
  aDataSet.Params.ParamByName('@ValidTo').AsString := _ValidTo;
  aDataSet.Params.ParamByName('@CompanyIDs').AsString := CompanyIDs;
end;

procedure TdmMain.PrepareLinePagination(AParams: string);
var
  _Params: TStringDynArray;
  _search, _sortby, _filter: string;
  i, j, k, x: integer;
begin
  if Pos('|', AParams) > 0 then
    _Params := SplitString(AParams, '|')
  else
    _Params := SplitString(AParams, ',');

  if cdsLinePagination.Params.Count=0 then
  cdsLinePagination.FetchParams;


  if not GetStrValueFromArrayVarName('@search', _Params, _Search) then
    _Search := '';
  if not GetStrValueFromArrayVarName('@sortby', _Params, _sortby) then
    _sortby := '';
  if not GetStrValueFromArrayVarName('@filter', _Params, _filter) then
    _filter := '';
  if not GetIntValueFromArrayVarName('@rowfrom', _Params, i) then
    i := 0;
  if not GetIntValueFromArrayVarName('@rowto', _Params, j) then
    j := 0;
  if not GetIntValueFromArrayVarName('@timetable_id', _Params, k) then
    k := 0;
  if not GetIntValueFromArrayVarName('@countonly', _Params, x) then
    x := 0;

  cdsLinePagination.Params.ParamByName('@search').AsString := _Search;
  cdsLinePagination.Params.ParamByName('@sortby').AsString := _sortby;
  cdsLinePagination.Params.ParamByName('@filter').AsString := _filter;
  cdsLinePagination.Params.ParamByName('@rowfrom').AsInteger := i;
  cdsLinePagination.Params.ParamByName('@rowto').AsInteger := j;
  cdsLinePagination.Params.ParamByName('@timetable_id').AsInteger := k;
  cdsLinePagination.Params.ParamByName('@countonly').AsInteger := x;
end;

procedure TdmMain.PrepareLPC_Parameters(Params: string);
begin
  if cdsStoredProcLPC_Parameters.Params.Count = 0 then
    cdsStoredProcLPC_Parameters.FetchParams;
  cdsStoredProcLPC_Parameters.Params.ParamByName('@App_ID').AsString := Trim(Params);
end;

{$endregion}

{$endregion}


{$region 'File (attachments) operations'}
function TdmMain.ReadFile(aFileStream: TStream; aFileName, AGuid, ASubdir: string): boolean;
begin
  Result := ClientMainDMUtil.ReadFile(aFileStream, aFileName, AGuid, ASubdir, TCPIPServerMethods);
end;

function TdmMain.ReadBusTabletFile(aFileStream: TStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReadBusTabletFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReadRegFile(aFileStream: TStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReadRegFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReadCardFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReadCardFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReadSalesReportFile(aFileStream: TStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReadSalesReportFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReadEmar205File(aFileStream: TStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReadEmar205File(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.RideDesignationOpen(Params: string): boolean;
begin
  Result := DataSetOpen(cdsStoredProcRideDesignation, Params);
end;

function TdmMain.SaveFile(aFileStream: TMemoryStream; aFileName,
  AGuid, ASubdir: string): boolean;
begin
  Result := ClientMainDMUtil.SaveFile(aFileStream, aFileName, AGuid, ASubdir, TCPIPServerMethods);
end;

function TdmMain.SaveBusTabletFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.SaveBusTabletFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.SaveRegFile(aFileStream: TMemoryStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.SaveRegFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.SaveSalesReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.SaveSalesReportFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.SaveEmar205File(aFileStream: TMemoryStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.SaveEmar205File(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.SaveCardFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.SaveCardFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReplaceCardFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReplaceCardFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReplaceSalesReportFile(aFileStream: TMemoryStream; aFileName, ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReplaceSalesReportFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReplaceEmar205File(aFileStream: TMemoryStream; aFileName,
  ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReplaceEmar205File(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.ReplaceBusTabletFile(aFileStream: TMemoryStream; aFileName
  , ASubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.ReplaceBusTabletFile(aFileStream, aFileName, ASubDir, TCPIPServerMethods);
end;

function TdmMain.NextCardFileName(ACardSerialNumber: Int64;
  AYear: SmallInt; AMonth, ADay: Byte; ACompany_ID: Integer): String;
var
  iDigitsNumber: Byte;
  iNextFileNo: Integer;
  sParams, sBeginFileName, sFileNameTemplate: String;
begin
  Result := '';

  // Kssnnnnnnrrrrmmddkk.DAT
  sBeginFileName :=
    Format('K%.2d%.6d%s',
      [
        GetUserStationParam
        , ACardSerialNumber
        , FormatDateTime('yyyymmdd', Now)
      ]);
  iDigitsNumber := 2;
  sFileNameTemplate := sBeginFileName + '%.' + IntToStr(iDigitsNumber) + 'd.DAT';
  sParams :=
    '@BeginFileName=' + sBeginFileName
    + #13#10'@DigitsNumber=' + IntToStr(iDigitsNumber)
    + #13#10'@Company_ID=' + IntToStr(ACompany_ID);

  if AnsiCompareText(sParams, '') <> 0 then
  begin
    iNextFileNo := StrToIntDef(Self.StoredFunc('dbo', 'GetNextFileNo', sParams), 0);
    if (iNextFileNo > 0)and(iNextFileNo < Power(10, iDigitsNumber)) then
      Result := Format(sFileNameTemplate, [iNextFileNo]);
  end;
end;

function TdmMain.GetServerSalesReportsList(AServerSalesReportsType: Byte; ACountOnly: Boolean): String;
begin
  Result := ClientMainDMUtil.GetServerSalesReportsList(TCPIPServerMethods, AServerSalesReportsType, ACountOnly);
end;

function TdmMain.GetReportsForRegistrationInServerSalesReportsList(): Boolean;
var
  JSON: String;
  iso: ISuperObject;
begin
  Result := False;
  JSON := dmMainGlobal.GetServerSalesReportsList(1, True); // without error
  iso := SO(JSON);
  if Assigned(iso) then
    if Assigned(iso.O['files_without_error_count']) then
      Result := iso.I['files_without_error_count'] > 0;
end;

function TdmMain.DeleteErrorFile(AFileType: Byte; AFileWithSubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.DeleteErrorFile(TCPIPServerMethods, AFileType, AFileWithSubDir);
end;

function TdmMain.DeleteIncorrectReportFile(AFileType: Byte; AFileWithSubDir: String): Boolean;
begin
  Result := ClientMainDMUtil.DeleteIncorrectReportFile(TCPIPServerMethods, AFileType, AFileWithSubDir);
end;

procedure TdmMain.AutServerStart(AForceKillProcess: Boolean);
begin
  ClientMainDMUtil.AutServerStart(TCPIPServerMethods, AForceKillProcess);
end;

function TdmMain.AutServerIsRunning(): Boolean;
begin
  Result := ClientMainDMUtil.AutServerIsRunning(TCPIPServerMethods);
end;

function TdmMain.AutServerIsStopping(): Boolean;
begin
  Result := ClientMainDMUtil.AutServerIsStopping(TCPIPServerMethods);
end;

function TdmMain.AutServerName(): String;
begin
  Result := ClientMainDMUtil.AutServerName(TCPIPServerMethods);
end;

function TdmMain.AutServerDisplayName(): String;
begin
  Result := ClientMainDMUtil.AutServerDisplayName(TCPIPServerMethods);
end;

procedure TdmMain.SendDebugPipeMessage(aMessage: string);
begin
{$IFDEF USE_PIPES}
  if
    Assigned(fPipeServer)
    and fPipeServer.Active
    and (fPipeServer.ClientCount > 0)
    and (aMessage<>'')
  then
  begin
    aMessage := Format('[%s]: %s', [FormatDateTime('hh:nn:ss.zzz', Now()), aMessage]);
    fPipeServer.Broadcast(aMessage[1], Length(aMessage) * SizeOf(Char));
  end;
{$ENDIF}
end;

procedure TdmMain.SetPrivileges(const Value: TObjectList<TObject>);
begin
  fPrivileges := Value;
end;

{$endregion}

{$region 'Stored proc/func operations}
function TdmMain.StoredFunc(SchemaName, StroredProcName,
  Params: string; aParametersSeparator: String = #13#10; aLineBreak: string = #13): string;
begin
  Result :=
    TCPIPServerMethods.StoredFunc(SchemaName, StroredProcName, Params, aParametersSeparator, aLineBreak);
end;

function TdmMain.StoredProc(SchemaName, StroredProcName,
  Params: string): Integer;
begin
  Result :=
    TCPIPServerMethods.StoredProc(SchemaName, StroredProcName, Params);
end;

function TdmMain.StoredProcReportsClose: boolean;
begin
  Result := True;
  if Assigned(cdsStoredProcReports) then
  begin
    Result := ClientMainDMUtil.StoredProcClose(cdsStoredProcReports);
    FreeAndNil(cdsStoredProcReports);
  end;
end;

function TdmMain.StoredProcClose(Tag: Integer): boolean;
var
  st: TClientDataSet;
begin
  st := GetClientDataSet(Tag);
  Result := ClientMainDMUtil.StoredProcClose(st);
end;

function TdmMain.StoredProcClose(DS: TDataSet): boolean;
begin
  if GetClientDataSet(DS.Tag) = DS then
      Result := ClientMainDMUtil.StoredProcClose(GetClientDataSet(DS.Tag))
  else
    raise Exception.Create('MainDM: Illegal dataset closeing attempt.');
end;

function TdmMain.GetCdsStoredProcReports(const aDesiredPacketRecords: Integer;
   const aInitialPacketRecords: Integer): TForwardOnlyClientDataSet;
begin
  if not Assigned(cdsStoredProcReports) then
  begin
    // JS Tworzymy niecacheuj¹cy ClientDataSet do raportów.
    cdsStoredProcReports := TForwardOnlyClientDataSet.Create(
      aDesiredPacketRecords, nil, aInitialPacketRecords);
    cdsStoredProcReports.FetchOnDemand := True;
    cdsStoredProcReports.ProviderName := 'dsProviderReports';
    cdsStoredProcReports.RemoteServer := DSProviderConnection;
  end;

  Result := cdsStoredProcReports;
end;

function TdmMain.StoredProcReportsOpen(SchemaName, StroredProcName,
      Params: string;
      const aDesiredPacketRecords: Integer = REPORTS_DS_DEFAULT_FETCH_SIZE;
      const aInitialPacketRecords: Integer = -1;
      const aParametersSeparator: String = #13#10;
      const aLineBreak: String = #13): boolean;
begin
  var cdsForReports := GetCdsStoredProcReports(aDesiredPacketRecords,
    aInitialPacketRecords);
  Result := ClientMainDMUtil.StoredProcReportOpen(SchemaName, StroredProcName,
    Params, cdsForReports, TCPIPServerMethods, aParametersSeparator,
    aLineBreak);
end;

function TdmMain.StoredProcOpen(aClientDataSet: TClientDataSet; Params: string;
  const aParametersSeparator, aLineBreak: String): boolean;
begin
  Result := ClientMainDMUtil.StoredProcOpen(aClientDataSet, Params, aParametersSeparator, aLineBreak);
end;

function TdmMain.StoredProcOpen(SchemaName, StroredProcName, Params: string;
  Tag: Integer;
  const aParametersSeparator: String = #13#10;
  const aLineBreak: String = #13): boolean;
var
  st: TClientDataSet;
begin
  st := GetClientDataSet(Tag);
  Result := ClientMainDMUtil.StoredProcOpen(SchemaName, StroredProcName,
    Params, st, TCPIPServerMethods, aParametersSeparator, aLineBreak);
end;

function TdmMain.StoredProcOpen(SchemaName, StroredProcName: string; Params: TStringList;
  Tag: Integer;
  const aParametersSeparator: String = #13#10;
  const aLineBreak: String = #13): boolean;
begin
  Result := StoredProcOpen(SchemaName, StroredProcName, Trim(Params.Text), Tag,
    aParametersSeparator, aLineBreak);
end;
{$endregion}

{$region 'user operations'}

function TdmMain.LogonAndCheckForceLogoff: Boolean;
begin
  Result := ClientMainDMUtil.LogonAndCheckForceLogoff(FTCPIPServerMethods);
end;

procedure TdmMain.UserAfterLogin(Sender, AUser: TObject; var ALogged: boolean;
  var AMessage: String);
begin
  if Assigned(FOnUserAfterLoginEvent) then
    FOnUserAfterLoginEvent(Self, CurrentUser, ALogged, AMessage);
end;

function TdmMain.UserLogin(aId: integer; AOnUserLoginProc : TOnUserLoginProc): boolean;
begin
  Result := ClientMainDMUtil.UserLogin(aId, Self, FTCPIPServerMethods, AOnUserLoginProc);
end;

procedure TdmMain.GetClientAuthentication;
begin
  ClientMainDMUtil.GetClientAuthentication(SQLConnection, FTCPIPServerMethods);
end;

procedure TdmMain.SQLConnectionValidatePeerCertificate(Owner: TObject;
    Certificate: TX509Certificate; const ADepth: Integer; var Ok: Boolean);
begin
  Ok := True;
end;

function TdmMain.TryOpenConnection(Var BError : String) : boolean;
begin
  Result := ClientMainDMUtil.TryOpenConnection( self, BError )
end;


function TdmMain.DBVersionGet(var DBVer : Integer) : boolean;
begin
  Result := false;
  DBVer:=0;
  try
    Result := StoredProcOpen('dbo', 'ADMIN_DBVer_Get', '', 1);
    if result then
      DBVer:=cdsStoredProcCustom1.FieldByName('DBVer').AsInteger;
    StoredProcClose(1);
  except
  end;
end;

{$endregion}

end.
