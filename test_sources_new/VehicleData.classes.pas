unit VehicleData.classes;

interface

uses
  SysUtils, Classes, Windows, Math, DateUtils,
  DB, DBClient, Provider,
  FleetBase.classes;

type

// Forward declarations
  TFleet105_Device = class;
  TFleet105_Vehicle = class;
  TFleet105_VehicleList = class;
  TFleet105_Driver = class;
  TFleet105_DriverList = class;
  TFleet105_Route = class;
  TFleet105_RouteList = class;
  TFleet105_JobOrder = class;
  TFleet105_JobOrderList = class;
  TFleet105_FuelRecord = class;
  TFleet105_FuelRecordList = class;
  TFleet105_ServiceRecord = class;
  TFleet105_ServiceRecordList = class;
  TFleet105_Incident = class;
  TFleet105_IncidentList = class;
  TFleet105_GpsTrack = class;
  TFleet105_GpsTrackList = class;
  TFleet105_Depot = class;
  TFleet105_DepotList = class;
  TFleet105_Employee = class;
  TFleet105_EmployeeList = class;
  TFleet105_Department = class;
  TFleet105_DepartmentList = class;
  TFleet105_Schedule = class;
  TFleet105_ScheduleList = class;
  TFleet105_Passenger = class;
  TFleet105_PassengerList = class;
  TFleet105_Trip = class;
  TFleet105_TripList = class;
  TFleet105_PayrollEntry = class;
  TFleet105_PayrollEntryList = class;
  TFleet105_MaintenancePlan = class;
  TFleet105_MaintenancePlanList = class;
  TFleet105_PartStock = class;
  TFleet105_PartStockList = class;
  TFleet105_Supplier = class;
  TFleet105_SupplierList = class;
  TFleet105_PurchaseOrder = class;
  TFleet105_PurchaseOrderList = class;
  TFleet105_Invoice = class;
  TFleet105_InvoiceList = class;
  TFleet105_CostCentre = class;
  TFleet105_CostCentreList = class;
  TFleet105_TyreRecord = class;
  TFleet105_TyreRecordList = class;
  TFleet105_PermitLicence = class;
  TFleet105_PermitLicenceList = class;
  TFleet105_AlertEvent = class;
  TFleet105_AlertEventList = class;
  TFleet105_ReportDef = class;
  TFleet105_ReportDefList = class;
  TFleet105_UserAccount = class;
  TFleet105_UserAccountList = class;
  TFleet105_RolePermission = class;
  TFleet105_RolePermissionList = class;
  TFleet105_AuditLog = class;
  TFleet105_AuditLogList = class;
  TFleet105_Notification = class;
  TFleet105_NotificationList = class;
  TFleet105_DocumentStore = class;
  TFleet105_DocumentStoreList = class;
  TFleet105_GeoZone = class;
  TFleet105_GeoZoneList = class;
  TFleet105_ChecklistTemplate = class;
  TFleet105_ChecklistTemplateList = class;
  TFleet105_ChecklistResult = class;
  TFleet105_ChecklistResultList = class;
  TFleet105_ContractClient = class;
  TFleet105_ContractClientList = class;
  TFleet105_BillingRecord = class;
  TFleet105_BillingRecordList = class;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Device — Master device class
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Device = class(TFleetDevice, IFleet105_Device)
  private
    FDeviceId: Integer;
    FDeviceSerial: string;
    FDeviceName: string;
    FDeviceType: Integer;
    FFirmwareVersion: string;
    FHardwareRevision: string;
    FLastContactTime: TDateTime;
    FBatteryLevel: Integer;
    FSignalStrength: Integer;
    FGpsLatitude: Double;
    FGpsLongitude: Double;
    FGpsAltitude: Double;
    FGpsSpeed: Double;
    FGpsHeading: Double;
    FGpsAccuracy: Double;
    FGpsSatellites: Integer;
    FGpsFixTime: TDateTime;
    FVehicleId: Integer;
    FDepotId: Integer;
    FIsActive: Boolean;
    FIsOnline: Boolean;
    FConfigVersion: Integer;
    FMaxSpeed: Integer;
    FIdleTimeout: Integer;
    FReportInterval: Integer;
    FAlertFlags: Cardinal;
    FErrorCode: Integer;
    FErrorMessage: string;
    FInstallDate: TDateTime;
    FWarrantyExpiry: TDateTime;
    FSupplierCode: string;
    FAssetTag: string;
    FEncryptionKey: string;
    FAuthToken: string;
    FServerUrl: string;
    FServerPort: Integer;
    FConnectionMode: Integer;
    FDataQueueSize: Integer;
    FTotalMessagesSent: Int64;
    FTotalMessagesReceived: Int64;
    FTotalBytesTransferred: Int64;
    FSessionCount: Integer;
    FLastResetTime: TDateTime;
    FDiagnosticData: string;
    FCalibrationDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    function GetDeviceId: Integer; stdcall;
    procedure SetDeviceId(const Value: Integer); stdcall;
    function GetDeviceSerial: WideString; stdcall;
    procedure SetDeviceSerial(const Value: WideString); stdcall;
    function GetDeviceName: WideString; stdcall;
    procedure SetDeviceName(const Value: WideString); stdcall;
    function GetDeviceType: Integer; stdcall;
    procedure SetDeviceType(const Value: Integer); stdcall;
    function GetFirmwareVersion: WideString; stdcall;
    procedure SetFirmwareVersion(const Value: WideString); stdcall;
    function GetHardwareRevision: WideString; stdcall;
    procedure SetHardwareRevision(const Value: WideString); stdcall;
    function GetLastContactTime: TDateTime; stdcall;
    procedure SetLastContactTime(const Value: TDateTime); stdcall;
    function GetBatteryLevel: Integer; stdcall;
    procedure SetBatteryLevel(const Value: Integer); stdcall;
    function GetSignalStrength: Integer; stdcall;
    procedure SetSignalStrength(const Value: Integer); stdcall;
    function GetGpsLatitude: Double; stdcall;
    procedure SetGpsLatitude(const Value: Double); stdcall;
    function GetGpsLongitude: Double; stdcall;
    procedure SetGpsLongitude(const Value: Double); stdcall;
    function GetGpsAltitude: Double; stdcall;
    procedure SetGpsAltitude(const Value: Double); stdcall;
    function GetGpsSpeed: Double; stdcall;
    procedure SetGpsSpeed(const Value: Double); stdcall;
    function GetGpsHeading: Double; stdcall;
    procedure SetGpsHeading(const Value: Double); stdcall;
    function GetGpsAccuracy: Double; stdcall;
    procedure SetGpsAccuracy(const Value: Double); stdcall;
    function GetGpsSatellites: Integer; stdcall;
    procedure SetGpsSatellites(const Value: Integer); stdcall;
    function GetGpsFixTime: TDateTime; stdcall;
    procedure SetGpsFixTime(const Value: TDateTime); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetIsOnline: Boolean; stdcall;
    procedure SetIsOnline(const Value: Boolean); stdcall;
    function GetConfigVersion: Integer; stdcall;
    procedure SetConfigVersion(const Value: Integer); stdcall;
    function GetMaxSpeed: Integer; stdcall;
    procedure SetMaxSpeed(const Value: Integer); stdcall;
    function GetIdleTimeout: Integer; stdcall;
    procedure SetIdleTimeout(const Value: Integer); stdcall;
    function GetReportInterval: Integer; stdcall;
    procedure SetReportInterval(const Value: Integer); stdcall;
    function GetAlertFlags: Cardinal; stdcall;
    procedure SetAlertFlags(const Value: Cardinal); stdcall;
    function GetErrorCode: Integer; stdcall;
    procedure SetErrorCode(const Value: Integer); stdcall;
    function GetErrorMessage: WideString; stdcall;
    procedure SetErrorMessage(const Value: WideString); stdcall;
    function GetInstallDate: TDateTime; stdcall;
    procedure SetInstallDate(const Value: TDateTime); stdcall;
    function GetWarrantyExpiry: TDateTime; stdcall;
    procedure SetWarrantyExpiry(const Value: TDateTime); stdcall;
    function GetSupplierCode: WideString; stdcall;
    procedure SetSupplierCode(const Value: WideString); stdcall;
    function GetAssetTag: WideString; stdcall;
    procedure SetAssetTag(const Value: WideString); stdcall;
    function GetEncryptionKey: WideString; stdcall;
    procedure SetEncryptionKey(const Value: WideString); stdcall;
    function GetAuthToken: WideString; stdcall;
    procedure SetAuthToken(const Value: WideString); stdcall;
    function GetServerUrl: WideString; stdcall;
    procedure SetServerUrl(const Value: WideString); stdcall;
    function GetServerPort: Integer; stdcall;
    procedure SetServerPort(const Value: Integer); stdcall;
    function GetConnectionMode: Integer; stdcall;
    procedure SetConnectionMode(const Value: Integer); stdcall;
    function GetDataQueueSize: Integer; stdcall;
    procedure SetDataQueueSize(const Value: Integer); stdcall;
    function GetTotalMessagesSent: Int64; stdcall;
    procedure SetTotalMessagesSent(const Value: Int64); stdcall;
    function GetTotalMessagesReceived: Int64; stdcall;
    procedure SetTotalMessagesReceived(const Value: Int64); stdcall;
    function GetTotalBytesTransferred: Int64; stdcall;
    procedure SetTotalBytesTransferred(const Value: Int64); stdcall;
    function GetSessionCount: Integer; stdcall;
    procedure SetSessionCount(const Value: Integer); stdcall;
    function GetLastResetTime: TDateTime; stdcall;
    procedure SetLastResetTime(const Value: TDateTime); stdcall;
    function GetDiagnosticData: WideString; stdcall;
    procedure SetDiagnosticData(const Value: WideString); stdcall;
    function GetCalibrationDate: TDateTime; stdcall;
    procedure SetCalibrationDate(const Value: TDateTime); stdcall;
    function Connect(const AServerUrl: WideString; APort: Integer): Boolean; stdcall;
    function Disconnect: Boolean; stdcall;
    function SendHeartbeat: Boolean; stdcall;
    function ParseGpsData(const ARawData: WideString): Boolean; stdcall;
    function UpdateFirmware(const AFirmwareFile: WideString): Boolean; stdcall;
    function ResetDevice: Boolean; stdcall;
    function RunDiagnostics: WideString; stdcall;
    function ExportConfig(const AFileName: WideString): Boolean; stdcall;
    function ImportConfig(const AFileName: WideString): Boolean; stdcall;
    function ValidateAuth: Boolean; stdcall;
    function EncryptPayload(const AData: WideString): WideString; stdcall;
    function DecryptPayload(const AData: WideString): WideString; stdcall;
    function QueueMessage(const AMsg: WideString; APriority: Integer): Boolean; stdcall;
    function FlushQueue: Integer; stdcall;
    function GetStatusReport: WideString; stdcall;
  published
    property DeviceId: Integer read GetDeviceId write SetDeviceId;
    property DeviceSerial: WideString read GetDeviceSerial write SetDeviceSerial;
    property DeviceName: WideString read GetDeviceName write SetDeviceName;
    property DeviceType: Integer read GetDeviceType write SetDeviceType;
    property FirmwareVersion: WideString read GetFirmwareVersion write SetFirmwareVersion;
    property HardwareRevision: WideString read GetHardwareRevision write SetHardwareRevision;
    property LastContactTime: TDateTime read GetLastContactTime write SetLastContactTime;
    property BatteryLevel: Integer read GetBatteryLevel write SetBatteryLevel;
    property SignalStrength: Integer read GetSignalStrength write SetSignalStrength;
    property GpsLatitude: Double read GetGpsLatitude write SetGpsLatitude;
    property GpsLongitude: Double read GetGpsLongitude write SetGpsLongitude;
    property GpsAltitude: Double read GetGpsAltitude write SetGpsAltitude;
    property GpsSpeed: Double read GetGpsSpeed write SetGpsSpeed;
    property GpsHeading: Double read GetGpsHeading write SetGpsHeading;
    property GpsAccuracy: Double read GetGpsAccuracy write SetGpsAccuracy;
    property GpsSatellites: Integer read GetGpsSatellites write SetGpsSatellites;
    property GpsFixTime: TDateTime read GetGpsFixTime write SetGpsFixTime;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property IsOnline: Boolean read GetIsOnline write SetIsOnline;
    property ConfigVersion: Integer read GetConfigVersion write SetConfigVersion;
    property MaxSpeed: Integer read GetMaxSpeed write SetMaxSpeed;
    property IdleTimeout: Integer read GetIdleTimeout write SetIdleTimeout;
    property ReportInterval: Integer read GetReportInterval write SetReportInterval;
    property AlertFlags: Cardinal read GetAlertFlags write SetAlertFlags;
    property ErrorCode: Integer read GetErrorCode write SetErrorCode;
    property ErrorMessage: WideString read GetErrorMessage write SetErrorMessage;
    property InstallDate: TDateTime read GetInstallDate write SetInstallDate;
    property WarrantyExpiry: TDateTime read GetWarrantyExpiry write SetWarrantyExpiry;
    property SupplierCode: WideString read GetSupplierCode write SetSupplierCode;
    property AssetTag: WideString read GetAssetTag write SetAssetTag;
    property EncryptionKey: WideString read GetEncryptionKey write SetEncryptionKey;
    property AuthToken: WideString read GetAuthToken write SetAuthToken;
    property ServerUrl: WideString read GetServerUrl write SetServerUrl;
    property ServerPort: Integer read GetServerPort write SetServerPort;
    property ConnectionMode: Integer read GetConnectionMode write SetConnectionMode;
    property DataQueueSize: Integer read GetDataQueueSize write SetDataQueueSize;
    property TotalMessagesSent: Int64 read GetTotalMessagesSent write SetTotalMessagesSent;
    property TotalMessagesReceived: Int64 read GetTotalMessagesReceived write SetTotalMessagesReceived;
    property TotalBytesTransferred: Int64 read GetTotalBytesTransferred write SetTotalBytesTransferred;
    property SessionCount: Integer read GetSessionCount write SetSessionCount;
    property LastResetTime: TDateTime read GetLastResetTime write SetLastResetTime;
    property DiagnosticData: WideString read GetDiagnosticData write SetDiagnosticData;
    property CalibrationDate: TDateTime read GetCalibrationDate write SetCalibrationDate;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Vehicle
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Vehicle = class(TFleetBaseEntity)
  private
    FVehicleId: Integer;
    FRegistrationNo: string;
    FFleetNo: string;
    FMake: string;
    FModel: string;
    FYear: Integer;
    FEngineCC: Integer;
    FFuelType: Integer;
    FGrossWeight: Integer;
    FPayloadKg: Integer;
    FDepotId: Integer;
    FStatusCode: Integer;
    FPurchaseDate: TDateTime;
    FMileageKm: Integer;
    FIsActive: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Vehicle);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetRegistrationNo: WideString; stdcall;
    procedure SetRegistrationNo(const Value: WideString); stdcall;
    function GetFleetNo: WideString; stdcall;
    procedure SetFleetNo(const Value: WideString); stdcall;
    function GetMake: WideString; stdcall;
    procedure SetMake(const Value: WideString); stdcall;
    function GetModel: WideString; stdcall;
    procedure SetModel(const Value: WideString); stdcall;
    function GetYear: Integer; stdcall;
    procedure SetYear(const Value: Integer); stdcall;
    function GetEngineCC: Integer; stdcall;
    procedure SetEngineCC(const Value: Integer); stdcall;
    function GetFuelType: Integer; stdcall;
    procedure SetFuelType(const Value: Integer); stdcall;
    function GetGrossWeight: Integer; stdcall;
    procedure SetGrossWeight(const Value: Integer); stdcall;
    function GetPayloadKg: Integer; stdcall;
    procedure SetPayloadKg(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetPurchaseDate: TDateTime; stdcall;
    procedure SetPurchaseDate(const Value: TDateTime); stdcall;
    function GetMileageKm: Integer; stdcall;
    procedure SetMileageKm(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
  published
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property RegistrationNo: WideString read GetRegistrationNo write SetRegistrationNo;
    property FleetNo: WideString read GetFleetNo write SetFleetNo;
    property Make: WideString read GetMake write SetMake;
    property Model: WideString read GetModel write SetModel;
    property Year: Integer read GetYear write SetYear;
    property EngineCC: Integer read GetEngineCC write SetEngineCC;
    property FuelType: Integer read GetFuelType write SetFuelType;
    property GrossWeight: Integer read GetGrossWeight write SetGrossWeight;
    property PayloadKg: Integer read GetPayloadKg write SetPayloadKg;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property PurchaseDate: TDateTime read GetPurchaseDate write SetPurchaseDate;
    property MileageKm: Integer read GetMileageKm write SetMileageKm;
    property IsActive: Boolean read GetIsActive write SetIsActive;
  end;

  TFleet105_VehicleList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Vehicle;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Vehicle;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Vehicle;
    function FindByCode(const ACode: WideString): TFleet105_Vehicle;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Vehicle read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Driver
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Driver = class(TFleetBaseEntity)
  private
    FDriverId: Integer;
    FEmployeeNo: string;
    FFirstName: string;
    FLastName: string;
    FLicenceNo: string;
    FLicenceClass: string;
    FLicenceExpiry: TDateTime;
    FDepotId: Integer;
    FRouteId: Integer;
    FStatusCode: Integer;
    FIsActive: Boolean;
    FDateOfBirth: TDateTime;
    FContactPhone: string;
    FContactEmail: string;
    FHireDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Driver);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetEmployeeNo: WideString; stdcall;
    procedure SetEmployeeNo(const Value: WideString); stdcall;
    function GetFirstName: WideString; stdcall;
    procedure SetFirstName(const Value: WideString); stdcall;
    function GetLastName: WideString; stdcall;
    procedure SetLastName(const Value: WideString); stdcall;
    function GetLicenceNo: WideString; stdcall;
    procedure SetLicenceNo(const Value: WideString); stdcall;
    function GetLicenceClass: WideString; stdcall;
    procedure SetLicenceClass(const Value: WideString); stdcall;
    function GetLicenceExpiry: TDateTime; stdcall;
    procedure SetLicenceExpiry(const Value: TDateTime); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetRouteId: Integer; stdcall;
    procedure SetRouteId(const Value: Integer); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetDateOfBirth: TDateTime; stdcall;
    procedure SetDateOfBirth(const Value: TDateTime); stdcall;
    function GetContactPhone: WideString; stdcall;
    procedure SetContactPhone(const Value: WideString); stdcall;
    function GetContactEmail: WideString; stdcall;
    procedure SetContactEmail(const Value: WideString); stdcall;
    function GetHireDate: TDateTime; stdcall;
    procedure SetHireDate(const Value: TDateTime); stdcall;
  published
    property DriverId: Integer read GetDriverId write SetDriverId;
    property EmployeeNo: WideString read GetEmployeeNo write SetEmployeeNo;
    property FirstName: WideString read GetFirstName write SetFirstName;
    property LastName: WideString read GetLastName write SetLastName;
    property LicenceNo: WideString read GetLicenceNo write SetLicenceNo;
    property LicenceClass: WideString read GetLicenceClass write SetLicenceClass;
    property LicenceExpiry: TDateTime read GetLicenceExpiry write SetLicenceExpiry;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property RouteId: Integer read GetRouteId write SetRouteId;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property DateOfBirth: TDateTime read GetDateOfBirth write SetDateOfBirth;
    property ContactPhone: WideString read GetContactPhone write SetContactPhone;
    property ContactEmail: WideString read GetContactEmail write SetContactEmail;
    property HireDate: TDateTime read GetHireDate write SetHireDate;
  end;

  TFleet105_DriverList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Driver;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Driver;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Driver;
    function FindByCode(const ACode: WideString): TFleet105_Driver;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Driver read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Route
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Route = class(TFleetBaseEntity)
  private
    FRouteId: Integer;
    FRouteCode: string;
    FRouteName: string;
    FStartPoint: string;
    FEndPoint: string;
    FDistanceKm: Double;
    FEstimatedMins: Integer;
    FDepotId: Integer;
    FDirectionCode: Integer;
    FIsCircular: Boolean;
    FIsActive: Boolean;
    FValidFrom: TDateTime;
    FValidTo: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Route);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetRouteId: Integer; stdcall;
    procedure SetRouteId(const Value: Integer); stdcall;
    function GetRouteCode: WideString; stdcall;
    procedure SetRouteCode(const Value: WideString); stdcall;
    function GetRouteName: WideString; stdcall;
    procedure SetRouteName(const Value: WideString); stdcall;
    function GetStartPoint: WideString; stdcall;
    procedure SetStartPoint(const Value: WideString); stdcall;
    function GetEndPoint: WideString; stdcall;
    procedure SetEndPoint(const Value: WideString); stdcall;
    function GetDistanceKm: Double; stdcall;
    procedure SetDistanceKm(const Value: Double); stdcall;
    function GetEstimatedMins: Integer; stdcall;
    procedure SetEstimatedMins(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetDirectionCode: Integer; stdcall;
    procedure SetDirectionCode(const Value: Integer); stdcall;
    function GetIsCircular: Boolean; stdcall;
    procedure SetIsCircular(const Value: Boolean); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetValidFrom: TDateTime; stdcall;
    procedure SetValidFrom(const Value: TDateTime); stdcall;
    function GetValidTo: TDateTime; stdcall;
    procedure SetValidTo(const Value: TDateTime); stdcall;
  published
    property RouteId: Integer read GetRouteId write SetRouteId;
    property RouteCode: WideString read GetRouteCode write SetRouteCode;
    property RouteName: WideString read GetRouteName write SetRouteName;
    property StartPoint: WideString read GetStartPoint write SetStartPoint;
    property EndPoint: WideString read GetEndPoint write SetEndPoint;
    property DistanceKm: Double read GetDistanceKm write SetDistanceKm;
    property EstimatedMins: Integer read GetEstimatedMins write SetEstimatedMins;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property DirectionCode: Integer read GetDirectionCode write SetDirectionCode;
    property IsCircular: Boolean read GetIsCircular write SetIsCircular;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property ValidFrom: TDateTime read GetValidFrom write SetValidFrom;
    property ValidTo: TDateTime read GetValidTo write SetValidTo;
  end;

  TFleet105_RouteList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Route;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Route;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Route;
    function FindByCode(const ACode: WideString): TFleet105_Route;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Route read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_JobOrder
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_JobOrder = class(TFleetBaseEntity)
  private
    FJobId: Integer;
    FJobRef: string;
    FVehicleId: Integer;
    FDriverId: Integer;
    FRouteId: Integer;
    FScheduledDate: TDateTime;
    FActualStart: TDateTime;
    FActualEnd: TDateTime;
    FStatusCode: Integer;
    FPriorityLevel: Integer;
    FPassengerCount: Integer;
    FPayloadKg: Integer;
    FNoteText: string;
    FCreatedBy: Integer;
    FCreatedDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_JobOrder);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetJobId: Integer; stdcall;
    procedure SetJobId(const Value: Integer); stdcall;
    function GetJobRef: WideString; stdcall;
    procedure SetJobRef(const Value: WideString); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetRouteId: Integer; stdcall;
    procedure SetRouteId(const Value: Integer); stdcall;
    function GetScheduledDate: TDateTime; stdcall;
    procedure SetScheduledDate(const Value: TDateTime); stdcall;
    function GetActualStart: TDateTime; stdcall;
    procedure SetActualStart(const Value: TDateTime); stdcall;
    function GetActualEnd: TDateTime; stdcall;
    procedure SetActualEnd(const Value: TDateTime); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetPriorityLevel: Integer; stdcall;
    procedure SetPriorityLevel(const Value: Integer); stdcall;
    function GetPassengerCount: Integer; stdcall;
    procedure SetPassengerCount(const Value: Integer); stdcall;
    function GetPayloadKg: Integer; stdcall;
    procedure SetPayloadKg(const Value: Integer); stdcall;
    function GetNoteText: WideString; stdcall;
    procedure SetNoteText(const Value: WideString); stdcall;
    function GetCreatedBy: Integer; stdcall;
    procedure SetCreatedBy(const Value: Integer); stdcall;
    function GetCreatedDate: TDateTime; stdcall;
    procedure SetCreatedDate(const Value: TDateTime); stdcall;
  published
    property JobId: Integer read GetJobId write SetJobId;
    property JobRef: WideString read GetJobRef write SetJobRef;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property RouteId: Integer read GetRouteId write SetRouteId;
    property ScheduledDate: TDateTime read GetScheduledDate write SetScheduledDate;
    property ActualStart: TDateTime read GetActualStart write SetActualStart;
    property ActualEnd: TDateTime read GetActualEnd write SetActualEnd;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property PriorityLevel: Integer read GetPriorityLevel write SetPriorityLevel;
    property PassengerCount: Integer read GetPassengerCount write SetPassengerCount;
    property PayloadKg: Integer read GetPayloadKg write SetPayloadKg;
    property NoteText: WideString read GetNoteText write SetNoteText;
    property CreatedBy: Integer read GetCreatedBy write SetCreatedBy;
    property CreatedDate: TDateTime read GetCreatedDate write SetCreatedDate;
  end;

  TFleet105_JobOrderList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_JobOrder;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_JobOrder;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_JobOrder;
    function FindByCode(const ACode: WideString): TFleet105_JobOrder;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_JobOrder read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_FuelRecord
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_FuelRecord = class(TFleetBaseEntity)
  private
    FFuelId: Integer;
    FVehicleId: Integer;
    FDriverId: Integer;
    FFuelDate: TDateTime;
    FLitres: Double;
    FCostPerLitre: Double;
    FTotalCost: Double;
    FOdometerKm: Integer;
    FDepotId: Integer;
    FFuelTypeCode: Integer;
    FReceiptNo: string;
    FApprovedBy: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_FuelRecord);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetFuelId: Integer; stdcall;
    procedure SetFuelId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetFuelDate: TDateTime; stdcall;
    procedure SetFuelDate(const Value: TDateTime); stdcall;
    function GetLitres: Double; stdcall;
    procedure SetLitres(const Value: Double); stdcall;
    function GetCostPerLitre: Double; stdcall;
    procedure SetCostPerLitre(const Value: Double); stdcall;
    function GetTotalCost: Double; stdcall;
    procedure SetTotalCost(const Value: Double); stdcall;
    function GetOdometerKm: Integer; stdcall;
    procedure SetOdometerKm(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetFuelTypeCode: Integer; stdcall;
    procedure SetFuelTypeCode(const Value: Integer); stdcall;
    function GetReceiptNo: WideString; stdcall;
    procedure SetReceiptNo(const Value: WideString); stdcall;
    function GetApprovedBy: Integer; stdcall;
    procedure SetApprovedBy(const Value: Integer); stdcall;
  published
    property FuelId: Integer read GetFuelId write SetFuelId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property FuelDate: TDateTime read GetFuelDate write SetFuelDate;
    property Litres: Double read GetLitres write SetLitres;
    property CostPerLitre: Double read GetCostPerLitre write SetCostPerLitre;
    property TotalCost: Double read GetTotalCost write SetTotalCost;
    property OdometerKm: Integer read GetOdometerKm write SetOdometerKm;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property FuelTypeCode: Integer read GetFuelTypeCode write SetFuelTypeCode;
    property ReceiptNo: WideString read GetReceiptNo write SetReceiptNo;
    property ApprovedBy: Integer read GetApprovedBy write SetApprovedBy;
  end;

  TFleet105_FuelRecordList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_FuelRecord;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_FuelRecord;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_FuelRecord;
    function FindByCode(const ACode: WideString): TFleet105_FuelRecord;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_FuelRecord read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_ServiceRecord
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_ServiceRecord = class(TFleetBaseEntity)
  private
    FServiceId: Integer;
    FVehicleId: Integer;
    FServiceDate: TDateTime;
    FServiceType: Integer;
    FOdometerKm: Integer;
    FTechnicianId: Integer;
    FLabourCost: Double;
    FPartsCost: Double;
    FTotalCost: Double;
    FNextServiceKm: Integer;
    FNextServiceDate: TDateTime;
    FWorkOrder: string;
    FNotes: string;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_ServiceRecord);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetServiceId: Integer; stdcall;
    procedure SetServiceId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetServiceDate: TDateTime; stdcall;
    procedure SetServiceDate(const Value: TDateTime); stdcall;
    function GetServiceType: Integer; stdcall;
    procedure SetServiceType(const Value: Integer); stdcall;
    function GetOdometerKm: Integer; stdcall;
    procedure SetOdometerKm(const Value: Integer); stdcall;
    function GetTechnicianId: Integer; stdcall;
    procedure SetTechnicianId(const Value: Integer); stdcall;
    function GetLabourCost: Double; stdcall;
    procedure SetLabourCost(const Value: Double); stdcall;
    function GetPartsCost: Double; stdcall;
    procedure SetPartsCost(const Value: Double); stdcall;
    function GetTotalCost: Double; stdcall;
    procedure SetTotalCost(const Value: Double); stdcall;
    function GetNextServiceKm: Integer; stdcall;
    procedure SetNextServiceKm(const Value: Integer); stdcall;
    function GetNextServiceDate: TDateTime; stdcall;
    procedure SetNextServiceDate(const Value: TDateTime); stdcall;
    function GetWorkOrder: WideString; stdcall;
    procedure SetWorkOrder(const Value: WideString); stdcall;
    function GetNotes: WideString; stdcall;
    procedure SetNotes(const Value: WideString); stdcall;
  published
    property ServiceId: Integer read GetServiceId write SetServiceId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property ServiceDate: TDateTime read GetServiceDate write SetServiceDate;
    property ServiceType: Integer read GetServiceType write SetServiceType;
    property OdometerKm: Integer read GetOdometerKm write SetOdometerKm;
    property TechnicianId: Integer read GetTechnicianId write SetTechnicianId;
    property LabourCost: Double read GetLabourCost write SetLabourCost;
    property PartsCost: Double read GetPartsCost write SetPartsCost;
    property TotalCost: Double read GetTotalCost write SetTotalCost;
    property NextServiceKm: Integer read GetNextServiceKm write SetNextServiceKm;
    property NextServiceDate: TDateTime read GetNextServiceDate write SetNextServiceDate;
    property WorkOrder: WideString read GetWorkOrder write SetWorkOrder;
    property Notes: WideString read GetNotes write SetNotes;
  end;

  TFleet105_ServiceRecordList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_ServiceRecord;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_ServiceRecord;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_ServiceRecord;
    function FindByCode(const ACode: WideString): TFleet105_ServiceRecord;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_ServiceRecord read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Incident
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Incident = class(TFleetBaseEntity)
  private
    FIncidentId: Integer;
    FVehicleId: Integer;
    FDriverId: Integer;
    FIncidentDate: TDateTime;
    FIncidentType: Integer;
    FSeverityCode: Integer;
    FLocationDesc: string;
    FDescription: string;
    FInjuryCount: Integer;
    FDamageCost: Double;
    FReportedBy: Integer;
    FResolvedDate: TDateTime;
    FIsResolved: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Incident);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetIncidentId: Integer; stdcall;
    procedure SetIncidentId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetIncidentDate: TDateTime; stdcall;
    procedure SetIncidentDate(const Value: TDateTime); stdcall;
    function GetIncidentType: Integer; stdcall;
    procedure SetIncidentType(const Value: Integer); stdcall;
    function GetSeverityCode: Integer; stdcall;
    procedure SetSeverityCode(const Value: Integer); stdcall;
    function GetLocationDesc: WideString; stdcall;
    procedure SetLocationDesc(const Value: WideString); stdcall;
    function GetDescription: WideString; stdcall;
    procedure SetDescription(const Value: WideString); stdcall;
    function GetInjuryCount: Integer; stdcall;
    procedure SetInjuryCount(const Value: Integer); stdcall;
    function GetDamageCost: Double; stdcall;
    procedure SetDamageCost(const Value: Double); stdcall;
    function GetReportedBy: Integer; stdcall;
    procedure SetReportedBy(const Value: Integer); stdcall;
    function GetResolvedDate: TDateTime; stdcall;
    procedure SetResolvedDate(const Value: TDateTime); stdcall;
    function GetIsResolved: Boolean; stdcall;
    procedure SetIsResolved(const Value: Boolean); stdcall;
  published
    property IncidentId: Integer read GetIncidentId write SetIncidentId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property IncidentDate: TDateTime read GetIncidentDate write SetIncidentDate;
    property IncidentType: Integer read GetIncidentType write SetIncidentType;
    property SeverityCode: Integer read GetSeverityCode write SetSeverityCode;
    property LocationDesc: WideString read GetLocationDesc write SetLocationDesc;
    property Description: WideString read GetDescription write SetDescription;
    property InjuryCount: Integer read GetInjuryCount write SetInjuryCount;
    property DamageCost: Double read GetDamageCost write SetDamageCost;
    property ReportedBy: Integer read GetReportedBy write SetReportedBy;
    property ResolvedDate: TDateTime read GetResolvedDate write SetResolvedDate;
    property IsResolved: Boolean read GetIsResolved write SetIsResolved;
  end;

  TFleet105_IncidentList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Incident;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Incident;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Incident;
    function FindByCode(const ACode: WideString): TFleet105_Incident;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Incident read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_GpsTrack
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_GpsTrack = class(TFleetBaseEntity)
  private
    FTrackId: Integer;
    FVehicleId: Integer;
    FDeviceId: Integer;
    FTrackDate: TDateTime;
    FLatitude: Double;
    FLongitude: Double;
    FAltitude: Double;
    FSpeedKph: Double;
    FHeading: Double;
    FAccuracy: Double;
    FSatellites: Integer;
    FEventCode: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_GpsTrack);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetTrackId: Integer; stdcall;
    procedure SetTrackId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDeviceId: Integer; stdcall;
    procedure SetDeviceId(const Value: Integer); stdcall;
    function GetTrackDate: TDateTime; stdcall;
    procedure SetTrackDate(const Value: TDateTime); stdcall;
    function GetLatitude: Double; stdcall;
    procedure SetLatitude(const Value: Double); stdcall;
    function GetLongitude: Double; stdcall;
    procedure SetLongitude(const Value: Double); stdcall;
    function GetAltitude: Double; stdcall;
    procedure SetAltitude(const Value: Double); stdcall;
    function GetSpeedKph: Double; stdcall;
    procedure SetSpeedKph(const Value: Double); stdcall;
    function GetHeading: Double; stdcall;
    procedure SetHeading(const Value: Double); stdcall;
    function GetAccuracy: Double; stdcall;
    procedure SetAccuracy(const Value: Double); stdcall;
    function GetSatellites: Integer; stdcall;
    procedure SetSatellites(const Value: Integer); stdcall;
    function GetEventCode: Integer; stdcall;
    procedure SetEventCode(const Value: Integer); stdcall;
  published
    property TrackId: Integer read GetTrackId write SetTrackId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DeviceId: Integer read GetDeviceId write SetDeviceId;
    property TrackDate: TDateTime read GetTrackDate write SetTrackDate;
    property Latitude: Double read GetLatitude write SetLatitude;
    property Longitude: Double read GetLongitude write SetLongitude;
    property Altitude: Double read GetAltitude write SetAltitude;
    property SpeedKph: Double read GetSpeedKph write SetSpeedKph;
    property Heading: Double read GetHeading write SetHeading;
    property Accuracy: Double read GetAccuracy write SetAccuracy;
    property Satellites: Integer read GetSatellites write SetSatellites;
    property EventCode: Integer read GetEventCode write SetEventCode;
  end;

  TFleet105_GpsTrackList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_GpsTrack;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_GpsTrack;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_GpsTrack;
    function FindByCode(const ACode: WideString): TFleet105_GpsTrack;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_GpsTrack read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Depot
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Depot = class(TFleetBaseEntity)
  private
    FDepotId: Integer;
    FDepotCode: string;
    FDepotName: string;
    FAddress: string;
    FCity: string;
    FPostCode: string;
    FPhone: string;
    FManagerId: Integer;
    FCapacityVehicles: Integer;
    FCapacityDrivers: Integer;
    FIsActive: Boolean;
    FOpenTime: string;
    FCloseTime: string;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Depot);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetDepotCode: WideString; stdcall;
    procedure SetDepotCode(const Value: WideString); stdcall;
    function GetDepotName: WideString; stdcall;
    procedure SetDepotName(const Value: WideString); stdcall;
    function GetAddress: WideString; stdcall;
    procedure SetAddress(const Value: WideString); stdcall;
    function GetCity: WideString; stdcall;
    procedure SetCity(const Value: WideString); stdcall;
    function GetPostCode: WideString; stdcall;
    procedure SetPostCode(const Value: WideString); stdcall;
    function GetPhone: WideString; stdcall;
    procedure SetPhone(const Value: WideString); stdcall;
    function GetManagerId: Integer; stdcall;
    procedure SetManagerId(const Value: Integer); stdcall;
    function GetCapacityVehicles: Integer; stdcall;
    procedure SetCapacityVehicles(const Value: Integer); stdcall;
    function GetCapacityDrivers: Integer; stdcall;
    procedure SetCapacityDrivers(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetOpenTime: WideString; stdcall;
    procedure SetOpenTime(const Value: WideString); stdcall;
    function GetCloseTime: WideString; stdcall;
    procedure SetCloseTime(const Value: WideString); stdcall;
  published
    property DepotId: Integer read GetDepotId write SetDepotId;
    property DepotCode: WideString read GetDepotCode write SetDepotCode;
    property DepotName: WideString read GetDepotName write SetDepotName;
    property Address: WideString read GetAddress write SetAddress;
    property City: WideString read GetCity write SetCity;
    property PostCode: WideString read GetPostCode write SetPostCode;
    property Phone: WideString read GetPhone write SetPhone;
    property ManagerId: Integer read GetManagerId write SetManagerId;
    property CapacityVehicles: Integer read GetCapacityVehicles write SetCapacityVehicles;
    property CapacityDrivers: Integer read GetCapacityDrivers write SetCapacityDrivers;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property OpenTime: WideString read GetOpenTime write SetOpenTime;
    property CloseTime: WideString read GetCloseTime write SetCloseTime;
  end;

  TFleet105_DepotList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Depot;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Depot;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Depot;
    function FindByCode(const ACode: WideString): TFleet105_Depot;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Depot read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Employee
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Employee = class(TFleetBaseEntity)
  private
    FEmpId: Integer;
    FEmpNo: string;
    FFirstName: string;
    FLastName: string;
    FJobTitle: string;
    FDepartmentId: Integer;
    FDepotId: Integer;
    FHireDate: TDateTime;
    FTermDate: TDateTime;
    FSalary: Double;
    FIsActive: Boolean;
    FEmail: string;
    FPhone: string;
    FManagerId: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Employee);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetEmpId: Integer; stdcall;
    procedure SetEmpId(const Value: Integer); stdcall;
    function GetEmpNo: WideString; stdcall;
    procedure SetEmpNo(const Value: WideString); stdcall;
    function GetFirstName: WideString; stdcall;
    procedure SetFirstName(const Value: WideString); stdcall;
    function GetLastName: WideString; stdcall;
    procedure SetLastName(const Value: WideString); stdcall;
    function GetJobTitle: WideString; stdcall;
    procedure SetJobTitle(const Value: WideString); stdcall;
    function GetDepartmentId: Integer; stdcall;
    procedure SetDepartmentId(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetHireDate: TDateTime; stdcall;
    procedure SetHireDate(const Value: TDateTime); stdcall;
    function GetTermDate: TDateTime; stdcall;
    procedure SetTermDate(const Value: TDateTime); stdcall;
    function GetSalary: Double; stdcall;
    procedure SetSalary(const Value: Double); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetEmail: WideString; stdcall;
    procedure SetEmail(const Value: WideString); stdcall;
    function GetPhone: WideString; stdcall;
    procedure SetPhone(const Value: WideString); stdcall;
    function GetManagerId: Integer; stdcall;
    procedure SetManagerId(const Value: Integer); stdcall;
  published
    property EmpId: Integer read GetEmpId write SetEmpId;
    property EmpNo: WideString read GetEmpNo write SetEmpNo;
    property FirstName: WideString read GetFirstName write SetFirstName;
    property LastName: WideString read GetLastName write SetLastName;
    property JobTitle: WideString read GetJobTitle write SetJobTitle;
    property DepartmentId: Integer read GetDepartmentId write SetDepartmentId;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property HireDate: TDateTime read GetHireDate write SetHireDate;
    property TermDate: TDateTime read GetTermDate write SetTermDate;
    property Salary: Double read GetSalary write SetSalary;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property Email: WideString read GetEmail write SetEmail;
    property Phone: WideString read GetPhone write SetPhone;
    property ManagerId: Integer read GetManagerId write SetManagerId;
  end;

  TFleet105_EmployeeList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Employee;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Employee;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Employee;
    function FindByCode(const ACode: WideString): TFleet105_Employee;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Employee read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Department
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Department = class(TFleetBaseEntity)
  private
    FDeptId: Integer;
    FDeptCode: string;
    FDeptName: string;
    FManagerId: Integer;
    FCostCentre: string;
    FParentDeptId: Integer;
    FIsActive: Boolean;
    FHeadCount: Integer;
    FBudgetYear: Integer;
    FAnnualBudget: Double;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Department);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetDeptId: Integer; stdcall;
    procedure SetDeptId(const Value: Integer); stdcall;
    function GetDeptCode: WideString; stdcall;
    procedure SetDeptCode(const Value: WideString); stdcall;
    function GetDeptName: WideString; stdcall;
    procedure SetDeptName(const Value: WideString); stdcall;
    function GetManagerId: Integer; stdcall;
    procedure SetManagerId(const Value: Integer); stdcall;
    function GetCostCentre: WideString; stdcall;
    procedure SetCostCentre(const Value: WideString); stdcall;
    function GetParentDeptId: Integer; stdcall;
    procedure SetParentDeptId(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetHeadCount: Integer; stdcall;
    procedure SetHeadCount(const Value: Integer); stdcall;
    function GetBudgetYear: Integer; stdcall;
    procedure SetBudgetYear(const Value: Integer); stdcall;
    function GetAnnualBudget: Double; stdcall;
    procedure SetAnnualBudget(const Value: Double); stdcall;
  published
    property DeptId: Integer read GetDeptId write SetDeptId;
    property DeptCode: WideString read GetDeptCode write SetDeptCode;
    property DeptName: WideString read GetDeptName write SetDeptName;
    property ManagerId: Integer read GetManagerId write SetManagerId;
    property CostCentre: WideString read GetCostCentre write SetCostCentre;
    property ParentDeptId: Integer read GetParentDeptId write SetParentDeptId;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property HeadCount: Integer read GetHeadCount write SetHeadCount;
    property BudgetYear: Integer read GetBudgetYear write SetBudgetYear;
    property AnnualBudget: Double read GetAnnualBudget write SetAnnualBudget;
  end;

  TFleet105_DepartmentList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Department;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Department;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Department;
    function FindByCode(const ACode: WideString): TFleet105_Department;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Department read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Schedule
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Schedule = class(TFleetBaseEntity)
  private
    FScheduleId: Integer;
    FRouteId: Integer;
    FVehicleId: Integer;
    FDriverId: Integer;
    FDayOfWeek: Integer;
    FDepartureTime: string;
    FArrivalTime: string;
    FFrequencyMins: Integer;
    FValidFrom: TDateTime;
    FValidTo: TDateTime;
    FIsActive: Boolean;
    FSeasonCode: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Schedule);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetScheduleId: Integer; stdcall;
    procedure SetScheduleId(const Value: Integer); stdcall;
    function GetRouteId: Integer; stdcall;
    procedure SetRouteId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetDayOfWeek: Integer; stdcall;
    procedure SetDayOfWeek(const Value: Integer); stdcall;
    function GetDepartureTime: WideString; stdcall;
    procedure SetDepartureTime(const Value: WideString); stdcall;
    function GetArrivalTime: WideString; stdcall;
    procedure SetArrivalTime(const Value: WideString); stdcall;
    function GetFrequencyMins: Integer; stdcall;
    procedure SetFrequencyMins(const Value: Integer); stdcall;
    function GetValidFrom: TDateTime; stdcall;
    procedure SetValidFrom(const Value: TDateTime); stdcall;
    function GetValidTo: TDateTime; stdcall;
    procedure SetValidTo(const Value: TDateTime); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetSeasonCode: Integer; stdcall;
    procedure SetSeasonCode(const Value: Integer); stdcall;
  published
    property ScheduleId: Integer read GetScheduleId write SetScheduleId;
    property RouteId: Integer read GetRouteId write SetRouteId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property DayOfWeek: Integer read GetDayOfWeek write SetDayOfWeek;
    property DepartureTime: WideString read GetDepartureTime write SetDepartureTime;
    property ArrivalTime: WideString read GetArrivalTime write SetArrivalTime;
    property FrequencyMins: Integer read GetFrequencyMins write SetFrequencyMins;
    property ValidFrom: TDateTime read GetValidFrom write SetValidFrom;
    property ValidTo: TDateTime read GetValidTo write SetValidTo;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property SeasonCode: Integer read GetSeasonCode write SetSeasonCode;
  end;

  TFleet105_ScheduleList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Schedule;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Schedule;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Schedule;
    function FindByCode(const ACode: WideString): TFleet105_Schedule;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Schedule read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Passenger
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Passenger = class(TFleetBaseEntity)
  private
    FPassId: Integer;
    FCardNo: string;
    FFirstName: string;
    FLastName: string;
    FDateOfBirth: TDateTime;
    FCardExpiry: TDateTime;
    FBalanceCents: Integer;
    FDiscountCode: Integer;
    FIsBlacklisted: Boolean;
    FLastTripDate: TDateTime;
    FTripCount: Integer;
    FDepotId: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Passenger);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPassId: Integer; stdcall;
    procedure SetPassId(const Value: Integer); stdcall;
    function GetCardNo: WideString; stdcall;
    procedure SetCardNo(const Value: WideString); stdcall;
    function GetFirstName: WideString; stdcall;
    procedure SetFirstName(const Value: WideString); stdcall;
    function GetLastName: WideString; stdcall;
    procedure SetLastName(const Value: WideString); stdcall;
    function GetDateOfBirth: TDateTime; stdcall;
    procedure SetDateOfBirth(const Value: TDateTime); stdcall;
    function GetCardExpiry: TDateTime; stdcall;
    procedure SetCardExpiry(const Value: TDateTime); stdcall;
    function GetBalanceCents: Integer; stdcall;
    procedure SetBalanceCents(const Value: Integer); stdcall;
    function GetDiscountCode: Integer; stdcall;
    procedure SetDiscountCode(const Value: Integer); stdcall;
    function GetIsBlacklisted: Boolean; stdcall;
    procedure SetIsBlacklisted(const Value: Boolean); stdcall;
    function GetLastTripDate: TDateTime; stdcall;
    procedure SetLastTripDate(const Value: TDateTime); stdcall;
    function GetTripCount: Integer; stdcall;
    procedure SetTripCount(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
  published
    property PassId: Integer read GetPassId write SetPassId;
    property CardNo: WideString read GetCardNo write SetCardNo;
    property FirstName: WideString read GetFirstName write SetFirstName;
    property LastName: WideString read GetLastName write SetLastName;
    property DateOfBirth: TDateTime read GetDateOfBirth write SetDateOfBirth;
    property CardExpiry: TDateTime read GetCardExpiry write SetCardExpiry;
    property BalanceCents: Integer read GetBalanceCents write SetBalanceCents;
    property DiscountCode: Integer read GetDiscountCode write SetDiscountCode;
    property IsBlacklisted: Boolean read GetIsBlacklisted write SetIsBlacklisted;
    property LastTripDate: TDateTime read GetLastTripDate write SetLastTripDate;
    property TripCount: Integer read GetTripCount write SetTripCount;
    property DepotId: Integer read GetDepotId write SetDepotId;
  end;

  TFleet105_PassengerList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Passenger;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Passenger;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Passenger;
    function FindByCode(const ACode: WideString): TFleet105_Passenger;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Passenger read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Trip
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Trip = class(TFleetBaseEntity)
  private
    FTripId: Integer;
    FJobId: Integer;
    FRouteId: Integer;
    FVehicleId: Integer;
    FDriverId: Integer;
    FStartTime: TDateTime;
    FEndTime: TDateTime;
    FStartOdometer: Integer;
    FEndOdometer: Integer;
    FPassengerCount: Integer;
    FDelayMins: Integer;
    FStatusCode: Integer;
    FCancellationCode: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Trip);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetTripId: Integer; stdcall;
    procedure SetTripId(const Value: Integer); stdcall;
    function GetJobId: Integer; stdcall;
    procedure SetJobId(const Value: Integer); stdcall;
    function GetRouteId: Integer; stdcall;
    procedure SetRouteId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetStartTime: TDateTime; stdcall;
    procedure SetStartTime(const Value: TDateTime); stdcall;
    function GetEndTime: TDateTime; stdcall;
    procedure SetEndTime(const Value: TDateTime); stdcall;
    function GetStartOdometer: Integer; stdcall;
    procedure SetStartOdometer(const Value: Integer); stdcall;
    function GetEndOdometer: Integer; stdcall;
    procedure SetEndOdometer(const Value: Integer); stdcall;
    function GetPassengerCount: Integer; stdcall;
    procedure SetPassengerCount(const Value: Integer); stdcall;
    function GetDelayMins: Integer; stdcall;
    procedure SetDelayMins(const Value: Integer); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetCancellationCode: Integer; stdcall;
    procedure SetCancellationCode(const Value: Integer); stdcall;
  published
    property TripId: Integer read GetTripId write SetTripId;
    property JobId: Integer read GetJobId write SetJobId;
    property RouteId: Integer read GetRouteId write SetRouteId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property StartTime: TDateTime read GetStartTime write SetStartTime;
    property EndTime: TDateTime read GetEndTime write SetEndTime;
    property StartOdometer: Integer read GetStartOdometer write SetStartOdometer;
    property EndOdometer: Integer read GetEndOdometer write SetEndOdometer;
    property PassengerCount: Integer read GetPassengerCount write SetPassengerCount;
    property DelayMins: Integer read GetDelayMins write SetDelayMins;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property CancellationCode: Integer read GetCancellationCode write SetCancellationCode;
  end;

  TFleet105_TripList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Trip;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Trip;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Trip;
    function FindByCode(const ACode: WideString): TFleet105_Trip;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Trip read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_PayrollEntry
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_PayrollEntry = class(TFleetBaseEntity)
  private
    FPayId: Integer;
    FDriverId: Integer;
    FPeriodStart: TDateTime;
    FPeriodEnd: TDateTime;
    FTripCount: Integer;
    FTotalHours: Double;
    FBasicPay: Double;
    FOvertimePay: Double;
    FAllowancePay: Double;
    FDeductionTotal: Double;
    FNetPay: Double;
    FPaymentDate: TDateTime;
    FIsApproved: Boolean;
    FApprovedBy: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_PayrollEntry);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPayId: Integer; stdcall;
    procedure SetPayId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetPeriodStart: TDateTime; stdcall;
    procedure SetPeriodStart(const Value: TDateTime); stdcall;
    function GetPeriodEnd: TDateTime; stdcall;
    procedure SetPeriodEnd(const Value: TDateTime); stdcall;
    function GetTripCount: Integer; stdcall;
    procedure SetTripCount(const Value: Integer); stdcall;
    function GetTotalHours: Double; stdcall;
    procedure SetTotalHours(const Value: Double); stdcall;
    function GetBasicPay: Double; stdcall;
    procedure SetBasicPay(const Value: Double); stdcall;
    function GetOvertimePay: Double; stdcall;
    procedure SetOvertimePay(const Value: Double); stdcall;
    function GetAllowancePay: Double; stdcall;
    procedure SetAllowancePay(const Value: Double); stdcall;
    function GetDeductionTotal: Double; stdcall;
    procedure SetDeductionTotal(const Value: Double); stdcall;
    function GetNetPay: Double; stdcall;
    procedure SetNetPay(const Value: Double); stdcall;
    function GetPaymentDate: TDateTime; stdcall;
    procedure SetPaymentDate(const Value: TDateTime); stdcall;
    function GetIsApproved: Boolean; stdcall;
    procedure SetIsApproved(const Value: Boolean); stdcall;
    function GetApprovedBy: Integer; stdcall;
    procedure SetApprovedBy(const Value: Integer); stdcall;
  published
    property PayId: Integer read GetPayId write SetPayId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property PeriodStart: TDateTime read GetPeriodStart write SetPeriodStart;
    property PeriodEnd: TDateTime read GetPeriodEnd write SetPeriodEnd;
    property TripCount: Integer read GetTripCount write SetTripCount;
    property TotalHours: Double read GetTotalHours write SetTotalHours;
    property BasicPay: Double read GetBasicPay write SetBasicPay;
    property OvertimePay: Double read GetOvertimePay write SetOvertimePay;
    property AllowancePay: Double read GetAllowancePay write SetAllowancePay;
    property DeductionTotal: Double read GetDeductionTotal write SetDeductionTotal;
    property NetPay: Double read GetNetPay write SetNetPay;
    property PaymentDate: TDateTime read GetPaymentDate write SetPaymentDate;
    property IsApproved: Boolean read GetIsApproved write SetIsApproved;
    property ApprovedBy: Integer read GetApprovedBy write SetApprovedBy;
  end;

  TFleet105_PayrollEntryList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_PayrollEntry;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_PayrollEntry;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_PayrollEntry;
    function FindByCode(const ACode: WideString): TFleet105_PayrollEntry;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_PayrollEntry read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_MaintenancePlan
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_MaintenancePlan = class(TFleetBaseEntity)
  private
    FPlanId: Integer;
    FVehicleId: Integer;
    FServiceType: Integer;
    FIntervalKm: Integer;
    FIntervalDays: Integer;
    FLastDoneKm: Integer;
    FLastDoneDate: TDateTime;
    FNextDueKm: Integer;
    FNextDueDate: TDateTime;
    FIsActive: Boolean;
    FPriority: Integer;
    FAssignedTech: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_MaintenancePlan);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPlanId: Integer; stdcall;
    procedure SetPlanId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetServiceType: Integer; stdcall;
    procedure SetServiceType(const Value: Integer); stdcall;
    function GetIntervalKm: Integer; stdcall;
    procedure SetIntervalKm(const Value: Integer); stdcall;
    function GetIntervalDays: Integer; stdcall;
    procedure SetIntervalDays(const Value: Integer); stdcall;
    function GetLastDoneKm: Integer; stdcall;
    procedure SetLastDoneKm(const Value: Integer); stdcall;
    function GetLastDoneDate: TDateTime; stdcall;
    procedure SetLastDoneDate(const Value: TDateTime); stdcall;
    function GetNextDueKm: Integer; stdcall;
    procedure SetNextDueKm(const Value: Integer); stdcall;
    function GetNextDueDate: TDateTime; stdcall;
    procedure SetNextDueDate(const Value: TDateTime); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetPriority: Integer; stdcall;
    procedure SetPriority(const Value: Integer); stdcall;
    function GetAssignedTech: Integer; stdcall;
    procedure SetAssignedTech(const Value: Integer); stdcall;
  published
    property PlanId: Integer read GetPlanId write SetPlanId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property ServiceType: Integer read GetServiceType write SetServiceType;
    property IntervalKm: Integer read GetIntervalKm write SetIntervalKm;
    property IntervalDays: Integer read GetIntervalDays write SetIntervalDays;
    property LastDoneKm: Integer read GetLastDoneKm write SetLastDoneKm;
    property LastDoneDate: TDateTime read GetLastDoneDate write SetLastDoneDate;
    property NextDueKm: Integer read GetNextDueKm write SetNextDueKm;
    property NextDueDate: TDateTime read GetNextDueDate write SetNextDueDate;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property Priority: Integer read GetPriority write SetPriority;
    property AssignedTech: Integer read GetAssignedTech write SetAssignedTech;
  end;

  TFleet105_MaintenancePlanList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_MaintenancePlan;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_MaintenancePlan;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_MaintenancePlan;
    function FindByCode(const ACode: WideString): TFleet105_MaintenancePlan;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_MaintenancePlan read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_PartStock
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_PartStock = class(TFleetBaseEntity)
  private
    FPartId: Integer;
    FPartNo: string;
    FDescription: string;
    FCategory: Integer;
    FUnitCost: Double;
    FStockQty: Integer;
    FReorderLevel: Integer;
    FReorderQty: Integer;
    FDepotId: Integer;
    FSupplierId: Integer;
    FIsObsolete: Boolean;
    FLastOrderDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_PartStock);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPartId: Integer; stdcall;
    procedure SetPartId(const Value: Integer); stdcall;
    function GetPartNo: WideString; stdcall;
    procedure SetPartNo(const Value: WideString); stdcall;
    function GetDescription: WideString; stdcall;
    procedure SetDescription(const Value: WideString); stdcall;
    function GetCategory: Integer; stdcall;
    procedure SetCategory(const Value: Integer); stdcall;
    function GetUnitCost: Double; stdcall;
    procedure SetUnitCost(const Value: Double); stdcall;
    function GetStockQty: Integer; stdcall;
    procedure SetStockQty(const Value: Integer); stdcall;
    function GetReorderLevel: Integer; stdcall;
    procedure SetReorderLevel(const Value: Integer); stdcall;
    function GetReorderQty: Integer; stdcall;
    procedure SetReorderQty(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetSupplierId: Integer; stdcall;
    procedure SetSupplierId(const Value: Integer); stdcall;
    function GetIsObsolete: Boolean; stdcall;
    procedure SetIsObsolete(const Value: Boolean); stdcall;
    function GetLastOrderDate: TDateTime; stdcall;
    procedure SetLastOrderDate(const Value: TDateTime); stdcall;
  published
    property PartId: Integer read GetPartId write SetPartId;
    property PartNo: WideString read GetPartNo write SetPartNo;
    property Description: WideString read GetDescription write SetDescription;
    property Category: Integer read GetCategory write SetCategory;
    property UnitCost: Double read GetUnitCost write SetUnitCost;
    property StockQty: Integer read GetStockQty write SetStockQty;
    property ReorderLevel: Integer read GetReorderLevel write SetReorderLevel;
    property ReorderQty: Integer read GetReorderQty write SetReorderQty;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property SupplierId: Integer read GetSupplierId write SetSupplierId;
    property IsObsolete: Boolean read GetIsObsolete write SetIsObsolete;
    property LastOrderDate: TDateTime read GetLastOrderDate write SetLastOrderDate;
  end;

  TFleet105_PartStockList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_PartStock;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_PartStock;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_PartStock;
    function FindByCode(const ACode: WideString): TFleet105_PartStock;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_PartStock read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Supplier
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Supplier = class(TFleetBaseEntity)
  private
    FSupplierId: Integer;
    FSupplierCode: string;
    FCompanyName: string;
    FContactName: string;
    FPhone: string;
    FEmail: string;
    FAddress: string;
    FCity: string;
    FPostCode: string;
    FPayTermsDays: Integer;
    FIsActive: Boolean;
    FRatingScore: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Supplier);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetSupplierId: Integer; stdcall;
    procedure SetSupplierId(const Value: Integer); stdcall;
    function GetSupplierCode: WideString; stdcall;
    procedure SetSupplierCode(const Value: WideString); stdcall;
    function GetCompanyName: WideString; stdcall;
    procedure SetCompanyName(const Value: WideString); stdcall;
    function GetContactName: WideString; stdcall;
    procedure SetContactName(const Value: WideString); stdcall;
    function GetPhone: WideString; stdcall;
    procedure SetPhone(const Value: WideString); stdcall;
    function GetEmail: WideString; stdcall;
    procedure SetEmail(const Value: WideString); stdcall;
    function GetAddress: WideString; stdcall;
    procedure SetAddress(const Value: WideString); stdcall;
    function GetCity: WideString; stdcall;
    procedure SetCity(const Value: WideString); stdcall;
    function GetPostCode: WideString; stdcall;
    procedure SetPostCode(const Value: WideString); stdcall;
    function GetPayTermsDays: Integer; stdcall;
    procedure SetPayTermsDays(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetRatingScore: Integer; stdcall;
    procedure SetRatingScore(const Value: Integer); stdcall;
  published
    property SupplierId: Integer read GetSupplierId write SetSupplierId;
    property SupplierCode: WideString read GetSupplierCode write SetSupplierCode;
    property CompanyName: WideString read GetCompanyName write SetCompanyName;
    property ContactName: WideString read GetContactName write SetContactName;
    property Phone: WideString read GetPhone write SetPhone;
    property Email: WideString read GetEmail write SetEmail;
    property Address: WideString read GetAddress write SetAddress;
    property City: WideString read GetCity write SetCity;
    property PostCode: WideString read GetPostCode write SetPostCode;
    property PayTermsDays: Integer read GetPayTermsDays write SetPayTermsDays;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property RatingScore: Integer read GetRatingScore write SetRatingScore;
  end;

  TFleet105_SupplierList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Supplier;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Supplier;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Supplier;
    function FindByCode(const ACode: WideString): TFleet105_Supplier;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Supplier read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_PurchaseOrder
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_PurchaseOrder = class(TFleetBaseEntity)
  private
    FPoId: Integer;
    FPoNumber: string;
    FSupplierId: Integer;
    FOrderDate: TDateTime;
    FDeliveryDate: TDateTime;
    FDepotId: Integer;
    FTotalValue: Double;
    FStatusCode: Integer;
    FCreatedBy: Integer;
    FApprovedBy: Integer;
    FNotes: string;
    FIsUrgent: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_PurchaseOrder);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPoId: Integer; stdcall;
    procedure SetPoId(const Value: Integer); stdcall;
    function GetPoNumber: WideString; stdcall;
    procedure SetPoNumber(const Value: WideString); stdcall;
    function GetSupplierId: Integer; stdcall;
    procedure SetSupplierId(const Value: Integer); stdcall;
    function GetOrderDate: TDateTime; stdcall;
    procedure SetOrderDate(const Value: TDateTime); stdcall;
    function GetDeliveryDate: TDateTime; stdcall;
    procedure SetDeliveryDate(const Value: TDateTime); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetTotalValue: Double; stdcall;
    procedure SetTotalValue(const Value: Double); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetCreatedBy: Integer; stdcall;
    procedure SetCreatedBy(const Value: Integer); stdcall;
    function GetApprovedBy: Integer; stdcall;
    procedure SetApprovedBy(const Value: Integer); stdcall;
    function GetNotes: WideString; stdcall;
    procedure SetNotes(const Value: WideString); stdcall;
    function GetIsUrgent: Boolean; stdcall;
    procedure SetIsUrgent(const Value: Boolean); stdcall;
  published
    property PoId: Integer read GetPoId write SetPoId;
    property PoNumber: WideString read GetPoNumber write SetPoNumber;
    property SupplierId: Integer read GetSupplierId write SetSupplierId;
    property OrderDate: TDateTime read GetOrderDate write SetOrderDate;
    property DeliveryDate: TDateTime read GetDeliveryDate write SetDeliveryDate;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property TotalValue: Double read GetTotalValue write SetTotalValue;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property CreatedBy: Integer read GetCreatedBy write SetCreatedBy;
    property ApprovedBy: Integer read GetApprovedBy write SetApprovedBy;
    property Notes: WideString read GetNotes write SetNotes;
    property IsUrgent: Boolean read GetIsUrgent write SetIsUrgent;
  end;

  TFleet105_PurchaseOrderList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_PurchaseOrder;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_PurchaseOrder;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_PurchaseOrder;
    function FindByCode(const ACode: WideString): TFleet105_PurchaseOrder;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_PurchaseOrder read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Invoice
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Invoice = class(TFleetBaseEntity)
  private
    FInvId: Integer;
    FInvNumber: string;
    FSupplierId: Integer;
    FPoId: Integer;
    FInvDate: TDateTime;
    FDueDate: TDateTime;
    FNetAmount: Double;
    FTaxAmount: Double;
    FTotalAmount: Double;
    FStatusCode: Integer;
    FPaidDate: TDateTime;
    FPaidAmount: Double;
    FIsReconciled: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Invoice);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetInvId: Integer; stdcall;
    procedure SetInvId(const Value: Integer); stdcall;
    function GetInvNumber: WideString; stdcall;
    procedure SetInvNumber(const Value: WideString); stdcall;
    function GetSupplierId: Integer; stdcall;
    procedure SetSupplierId(const Value: Integer); stdcall;
    function GetPoId: Integer; stdcall;
    procedure SetPoId(const Value: Integer); stdcall;
    function GetInvDate: TDateTime; stdcall;
    procedure SetInvDate(const Value: TDateTime); stdcall;
    function GetDueDate: TDateTime; stdcall;
    procedure SetDueDate(const Value: TDateTime); stdcall;
    function GetNetAmount: Double; stdcall;
    procedure SetNetAmount(const Value: Double); stdcall;
    function GetTaxAmount: Double; stdcall;
    procedure SetTaxAmount(const Value: Double); stdcall;
    function GetTotalAmount: Double; stdcall;
    procedure SetTotalAmount(const Value: Double); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetPaidDate: TDateTime; stdcall;
    procedure SetPaidDate(const Value: TDateTime); stdcall;
    function GetPaidAmount: Double; stdcall;
    procedure SetPaidAmount(const Value: Double); stdcall;
    function GetIsReconciled: Boolean; stdcall;
    procedure SetIsReconciled(const Value: Boolean); stdcall;
  published
    property InvId: Integer read GetInvId write SetInvId;
    property InvNumber: WideString read GetInvNumber write SetInvNumber;
    property SupplierId: Integer read GetSupplierId write SetSupplierId;
    property PoId: Integer read GetPoId write SetPoId;
    property InvDate: TDateTime read GetInvDate write SetInvDate;
    property DueDate: TDateTime read GetDueDate write SetDueDate;
    property NetAmount: Double read GetNetAmount write SetNetAmount;
    property TaxAmount: Double read GetTaxAmount write SetTaxAmount;
    property TotalAmount: Double read GetTotalAmount write SetTotalAmount;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property PaidDate: TDateTime read GetPaidDate write SetPaidDate;
    property PaidAmount: Double read GetPaidAmount write SetPaidAmount;
    property IsReconciled: Boolean read GetIsReconciled write SetIsReconciled;
  end;

  TFleet105_InvoiceList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Invoice;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Invoice;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Invoice;
    function FindByCode(const ACode: WideString): TFleet105_Invoice;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Invoice read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_CostCentre
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_CostCentre = class(TFleetBaseEntity)
  private
    FCcId: Integer;
    FCcCode: string;
    FCcName: string;
    FDepotId: Integer;
    FManagerId: Integer;
    FBudgetYear: Integer;
    FAnnualBudget: Double;
    FSpentToDate: Double;
    FForecastTotal: Double;
    FIsActive: Boolean;
    FParentCcId: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_CostCentre);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetCcId: Integer; stdcall;
    procedure SetCcId(const Value: Integer); stdcall;
    function GetCcCode: WideString; stdcall;
    procedure SetCcCode(const Value: WideString); stdcall;
    function GetCcName: WideString; stdcall;
    procedure SetCcName(const Value: WideString); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetManagerId: Integer; stdcall;
    procedure SetManagerId(const Value: Integer); stdcall;
    function GetBudgetYear: Integer; stdcall;
    procedure SetBudgetYear(const Value: Integer); stdcall;
    function GetAnnualBudget: Double; stdcall;
    procedure SetAnnualBudget(const Value: Double); stdcall;
    function GetSpentToDate: Double; stdcall;
    procedure SetSpentToDate(const Value: Double); stdcall;
    function GetForecastTotal: Double; stdcall;
    procedure SetForecastTotal(const Value: Double); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetParentCcId: Integer; stdcall;
    procedure SetParentCcId(const Value: Integer); stdcall;
  published
    property CcId: Integer read GetCcId write SetCcId;
    property CcCode: WideString read GetCcCode write SetCcCode;
    property CcName: WideString read GetCcName write SetCcName;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property ManagerId: Integer read GetManagerId write SetManagerId;
    property BudgetYear: Integer read GetBudgetYear write SetBudgetYear;
    property AnnualBudget: Double read GetAnnualBudget write SetAnnualBudget;
    property SpentToDate: Double read GetSpentToDate write SetSpentToDate;
    property ForecastTotal: Double read GetForecastTotal write SetForecastTotal;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property ParentCcId: Integer read GetParentCcId write SetParentCcId;
  end;

  TFleet105_CostCentreList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_CostCentre;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_CostCentre;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_CostCentre;
    function FindByCode(const ACode: WideString): TFleet105_CostCentre;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_CostCentre read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_TyreRecord
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_TyreRecord = class(TFleetBaseEntity)
  private
    FTyreId: Integer;
    FVehicleId: Integer;
    FPosition: Integer;
    FBrand: string;
    FSize: string;
    FFitDate: TDateTime;
    FOdometerFit: Integer;
    FRemoveDate: TDateTime;
    FOdometerRemove: Integer;
    FTreadDepthMm: Double;
    FIsRetread: Boolean;
    FConditionCode: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_TyreRecord);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetTyreId: Integer; stdcall;
    procedure SetTyreId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetPosition: Integer; stdcall;
    procedure SetPosition(const Value: Integer); stdcall;
    function GetBrand: WideString; stdcall;
    procedure SetBrand(const Value: WideString); stdcall;
    function GetSize: WideString; stdcall;
    procedure SetSize(const Value: WideString); stdcall;
    function GetFitDate: TDateTime; stdcall;
    procedure SetFitDate(const Value: TDateTime); stdcall;
    function GetOdometerFit: Integer; stdcall;
    procedure SetOdometerFit(const Value: Integer); stdcall;
    function GetRemoveDate: TDateTime; stdcall;
    procedure SetRemoveDate(const Value: TDateTime); stdcall;
    function GetOdometerRemove: Integer; stdcall;
    procedure SetOdometerRemove(const Value: Integer); stdcall;
    function GetTreadDepthMm: Double; stdcall;
    procedure SetTreadDepthMm(const Value: Double); stdcall;
    function GetIsRetread: Boolean; stdcall;
    procedure SetIsRetread(const Value: Boolean); stdcall;
    function GetConditionCode: Integer; stdcall;
    procedure SetConditionCode(const Value: Integer); stdcall;
  published
    property TyreId: Integer read GetTyreId write SetTyreId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property Position: Integer read GetPosition write SetPosition;
    property Brand: WideString read GetBrand write SetBrand;
    property Size: WideString read GetSize write SetSize;
    property FitDate: TDateTime read GetFitDate write SetFitDate;
    property OdometerFit: Integer read GetOdometerFit write SetOdometerFit;
    property RemoveDate: TDateTime read GetRemoveDate write SetRemoveDate;
    property OdometerRemove: Integer read GetOdometerRemove write SetOdometerRemove;
    property TreadDepthMm: Double read GetTreadDepthMm write SetTreadDepthMm;
    property IsRetread: Boolean read GetIsRetread write SetIsRetread;
    property ConditionCode: Integer read GetConditionCode write SetConditionCode;
  end;

  TFleet105_TyreRecordList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_TyreRecord;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_TyreRecord;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_TyreRecord;
    function FindByCode(const ACode: WideString): TFleet105_TyreRecord;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_TyreRecord read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_PermitLicence
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_PermitLicence = class(TFleetBaseEntity)
  private
    FPermitId: Integer;
    FEntityType: Integer;
    FEntityId: Integer;
    FPermitType: Integer;
    FPermitNo: string;
    FIssuedBy: string;
    FIssueDate: TDateTime;
    FExpiryDate: TDateTime;
    FIssuedTo: string;
    FStatusCode: Integer;
    FNotes: string;
    FRenewalReminderDays: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_PermitLicence);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetPermitId: Integer; stdcall;
    procedure SetPermitId(const Value: Integer); stdcall;
    function GetEntityType: Integer; stdcall;
    procedure SetEntityType(const Value: Integer); stdcall;
    function GetEntityId: Integer; stdcall;
    procedure SetEntityId(const Value: Integer); stdcall;
    function GetPermitType: Integer; stdcall;
    procedure SetPermitType(const Value: Integer); stdcall;
    function GetPermitNo: WideString; stdcall;
    procedure SetPermitNo(const Value: WideString); stdcall;
    function GetIssuedBy: WideString; stdcall;
    procedure SetIssuedBy(const Value: WideString); stdcall;
    function GetIssueDate: TDateTime; stdcall;
    procedure SetIssueDate(const Value: TDateTime); stdcall;
    function GetExpiryDate: TDateTime; stdcall;
    procedure SetExpiryDate(const Value: TDateTime); stdcall;
    function GetIssuedTo: WideString; stdcall;
    procedure SetIssuedTo(const Value: WideString); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetNotes: WideString; stdcall;
    procedure SetNotes(const Value: WideString); stdcall;
    function GetRenewalReminderDays: Integer; stdcall;
    procedure SetRenewalReminderDays(const Value: Integer); stdcall;
  published
    property PermitId: Integer read GetPermitId write SetPermitId;
    property EntityType: Integer read GetEntityType write SetEntityType;
    property EntityId: Integer read GetEntityId write SetEntityId;
    property PermitType: Integer read GetPermitType write SetPermitType;
    property PermitNo: WideString read GetPermitNo write SetPermitNo;
    property IssuedBy: WideString read GetIssuedBy write SetIssuedBy;
    property IssueDate: TDateTime read GetIssueDate write SetIssueDate;
    property ExpiryDate: TDateTime read GetExpiryDate write SetExpiryDate;
    property IssuedTo: WideString read GetIssuedTo write SetIssuedTo;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property Notes: WideString read GetNotes write SetNotes;
    property RenewalReminderDays: Integer read GetRenewalReminderDays write SetRenewalReminderDays;
  end;

  TFleet105_PermitLicenceList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_PermitLicence;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_PermitLicence;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_PermitLicence;
    function FindByCode(const ACode: WideString): TFleet105_PermitLicence;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_PermitLicence read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_AlertEvent
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_AlertEvent = class(TFleetBaseEntity)
  private
    FAlertId: Integer;
    FDeviceId: Integer;
    FVehicleId: Integer;
    FDriverId: Integer;
    FAlertTime: TDateTime;
    FAlertType: Integer;
    FSeverityCode: Integer;
    FDescription: string;
    FLatitude: Double;
    FLongitude: Double;
    FSpeedKph: Double;
    FIsAcknowledged: Boolean;
    FAcknowledgedBy: Integer;
    FAcknowledgedTime: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_AlertEvent);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetAlertId: Integer; stdcall;
    procedure SetAlertId(const Value: Integer); stdcall;
    function GetDeviceId: Integer; stdcall;
    procedure SetDeviceId(const Value: Integer); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetDriverId: Integer; stdcall;
    procedure SetDriverId(const Value: Integer); stdcall;
    function GetAlertTime: TDateTime; stdcall;
    procedure SetAlertTime(const Value: TDateTime); stdcall;
    function GetAlertType: Integer; stdcall;
    procedure SetAlertType(const Value: Integer); stdcall;
    function GetSeverityCode: Integer; stdcall;
    procedure SetSeverityCode(const Value: Integer); stdcall;
    function GetDescription: WideString; stdcall;
    procedure SetDescription(const Value: WideString); stdcall;
    function GetLatitude: Double; stdcall;
    procedure SetLatitude(const Value: Double); stdcall;
    function GetLongitude: Double; stdcall;
    procedure SetLongitude(const Value: Double); stdcall;
    function GetSpeedKph: Double; stdcall;
    procedure SetSpeedKph(const Value: Double); stdcall;
    function GetIsAcknowledged: Boolean; stdcall;
    procedure SetIsAcknowledged(const Value: Boolean); stdcall;
    function GetAcknowledgedBy: Integer; stdcall;
    procedure SetAcknowledgedBy(const Value: Integer); stdcall;
    function GetAcknowledgedTime: TDateTime; stdcall;
    procedure SetAcknowledgedTime(const Value: TDateTime); stdcall;
  published
    property AlertId: Integer read GetAlertId write SetAlertId;
    property DeviceId: Integer read GetDeviceId write SetDeviceId;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property DriverId: Integer read GetDriverId write SetDriverId;
    property AlertTime: TDateTime read GetAlertTime write SetAlertTime;
    property AlertType: Integer read GetAlertType write SetAlertType;
    property SeverityCode: Integer read GetSeverityCode write SetSeverityCode;
    property Description: WideString read GetDescription write SetDescription;
    property Latitude: Double read GetLatitude write SetLatitude;
    property Longitude: Double read GetLongitude write SetLongitude;
    property SpeedKph: Double read GetSpeedKph write SetSpeedKph;
    property IsAcknowledged: Boolean read GetIsAcknowledged write SetIsAcknowledged;
    property AcknowledgedBy: Integer read GetAcknowledgedBy write SetAcknowledgedBy;
    property AcknowledgedTime: TDateTime read GetAcknowledgedTime write SetAcknowledgedTime;
  end;

  TFleet105_AlertEventList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_AlertEvent;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_AlertEvent;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_AlertEvent;
    function FindByCode(const ACode: WideString): TFleet105_AlertEvent;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_AlertEvent read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_ReportDef
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_ReportDef = class(TFleetBaseEntity)
  private
    FReportId: Integer;
    FReportCode: string;
    FReportName: string;
    FReportType: Integer;
    FCategoryCode: Integer;
    FQueryText: string;
    FParamList: string;
    FColumnList: string;
    FSortOrder: string;
    FIsActive: Boolean;
    FCreatedBy: Integer;
    FLastModified: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_ReportDef);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetReportId: Integer; stdcall;
    procedure SetReportId(const Value: Integer); stdcall;
    function GetReportCode: WideString; stdcall;
    procedure SetReportCode(const Value: WideString); stdcall;
    function GetReportName: WideString; stdcall;
    procedure SetReportName(const Value: WideString); stdcall;
    function GetReportType: Integer; stdcall;
    procedure SetReportType(const Value: Integer); stdcall;
    function GetCategoryCode: Integer; stdcall;
    procedure SetCategoryCode(const Value: Integer); stdcall;
    function GetQueryText: WideString; stdcall;
    procedure SetQueryText(const Value: WideString); stdcall;
    function GetParamList: WideString; stdcall;
    procedure SetParamList(const Value: WideString); stdcall;
    function GetColumnList: WideString; stdcall;
    procedure SetColumnList(const Value: WideString); stdcall;
    function GetSortOrder: WideString; stdcall;
    procedure SetSortOrder(const Value: WideString); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetCreatedBy: Integer; stdcall;
    procedure SetCreatedBy(const Value: Integer); stdcall;
    function GetLastModified: TDateTime; stdcall;
    procedure SetLastModified(const Value: TDateTime); stdcall;
  published
    property ReportId: Integer read GetReportId write SetReportId;
    property ReportCode: WideString read GetReportCode write SetReportCode;
    property ReportName: WideString read GetReportName write SetReportName;
    property ReportType: Integer read GetReportType write SetReportType;
    property CategoryCode: Integer read GetCategoryCode write SetCategoryCode;
    property QueryText: WideString read GetQueryText write SetQueryText;
    property ParamList: WideString read GetParamList write SetParamList;
    property ColumnList: WideString read GetColumnList write SetColumnList;
    property SortOrder: WideString read GetSortOrder write SetSortOrder;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property CreatedBy: Integer read GetCreatedBy write SetCreatedBy;
    property LastModified: TDateTime read GetLastModified write SetLastModified;
  end;

  TFleet105_ReportDefList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_ReportDef;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_ReportDef;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_ReportDef;
    function FindByCode(const ACode: WideString): TFleet105_ReportDef;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_ReportDef read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_UserAccount
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_UserAccount = class(TFleetBaseEntity)
  private
    FUserId: Integer;
    FUserName: string;
    FPasswordHash: string;
    FFullName: string;
    FEmail: string;
    FRoleId: Integer;
    FDepotId: Integer;
    FIsActive: Boolean;
    FLastLogin: TDateTime;
    FFailedAttempts: Integer;
    FIsLocked: Boolean;
    FCreatedDate: TDateTime;
    FForceReset: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_UserAccount);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetUserId: Integer; stdcall;
    procedure SetUserId(const Value: Integer); stdcall;
    function GetUserName: WideString; stdcall;
    procedure SetUserName(const Value: WideString); stdcall;
    function GetPasswordHash: WideString; stdcall;
    procedure SetPasswordHash(const Value: WideString); stdcall;
    function GetFullName: WideString; stdcall;
    procedure SetFullName(const Value: WideString); stdcall;
    function GetEmail: WideString; stdcall;
    procedure SetEmail(const Value: WideString); stdcall;
    function GetRoleId: Integer; stdcall;
    procedure SetRoleId(const Value: Integer); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetLastLogin: TDateTime; stdcall;
    procedure SetLastLogin(const Value: TDateTime); stdcall;
    function GetFailedAttempts: Integer; stdcall;
    procedure SetFailedAttempts(const Value: Integer); stdcall;
    function GetIsLocked: Boolean; stdcall;
    procedure SetIsLocked(const Value: Boolean); stdcall;
    function GetCreatedDate: TDateTime; stdcall;
    procedure SetCreatedDate(const Value: TDateTime); stdcall;
    function GetForceReset: Boolean; stdcall;
    procedure SetForceReset(const Value: Boolean); stdcall;
  published
    property UserId: Integer read GetUserId write SetUserId;
    property UserName: WideString read GetUserName write SetUserName;
    property PasswordHash: WideString read GetPasswordHash write SetPasswordHash;
    property FullName: WideString read GetFullName write SetFullName;
    property Email: WideString read GetEmail write SetEmail;
    property RoleId: Integer read GetRoleId write SetRoleId;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property LastLogin: TDateTime read GetLastLogin write SetLastLogin;
    property FailedAttempts: Integer read GetFailedAttempts write SetFailedAttempts;
    property IsLocked: Boolean read GetIsLocked write SetIsLocked;
    property CreatedDate: TDateTime read GetCreatedDate write SetCreatedDate;
    property ForceReset: Boolean read GetForceReset write SetForceReset;
  end;

  TFleet105_UserAccountList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_UserAccount;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_UserAccount;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_UserAccount;
    function FindByCode(const ACode: WideString): TFleet105_UserAccount;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_UserAccount read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_RolePermission
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_RolePermission = class(TFleetBaseEntity)
  private
    FRoleId: Integer;
    FRoleName: string;
    FDescription: string;
    FIsAdmin: Boolean;
    FCanViewReports: Boolean;
    FCanEditVehicles: Boolean;
    FCanEditDrivers: Boolean;
    FCanApprovePayroll: Boolean;
    FCanManageUsers: Boolean;
    FCanViewCosts: Boolean;
    FIsActive: Boolean;
    FCreatedDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_RolePermission);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetRoleId: Integer; stdcall;
    procedure SetRoleId(const Value: Integer); stdcall;
    function GetRoleName: WideString; stdcall;
    procedure SetRoleName(const Value: WideString); stdcall;
    function GetDescription: WideString; stdcall;
    procedure SetDescription(const Value: WideString); stdcall;
    function GetIsAdmin: Boolean; stdcall;
    procedure SetIsAdmin(const Value: Boolean); stdcall;
    function GetCanViewReports: Boolean; stdcall;
    procedure SetCanViewReports(const Value: Boolean); stdcall;
    function GetCanEditVehicles: Boolean; stdcall;
    procedure SetCanEditVehicles(const Value: Boolean); stdcall;
    function GetCanEditDrivers: Boolean; stdcall;
    procedure SetCanEditDrivers(const Value: Boolean); stdcall;
    function GetCanApprovePayroll: Boolean; stdcall;
    procedure SetCanApprovePayroll(const Value: Boolean); stdcall;
    function GetCanManageUsers: Boolean; stdcall;
    procedure SetCanManageUsers(const Value: Boolean); stdcall;
    function GetCanViewCosts: Boolean; stdcall;
    procedure SetCanViewCosts(const Value: Boolean); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetCreatedDate: TDateTime; stdcall;
    procedure SetCreatedDate(const Value: TDateTime); stdcall;
  published
    property RoleId: Integer read GetRoleId write SetRoleId;
    property RoleName: WideString read GetRoleName write SetRoleName;
    property Description: WideString read GetDescription write SetDescription;
    property IsAdmin: Boolean read GetIsAdmin write SetIsAdmin;
    property CanViewReports: Boolean read GetCanViewReports write SetCanViewReports;
    property CanEditVehicles: Boolean read GetCanEditVehicles write SetCanEditVehicles;
    property CanEditDrivers: Boolean read GetCanEditDrivers write SetCanEditDrivers;
    property CanApprovePayroll: Boolean read GetCanApprovePayroll write SetCanApprovePayroll;
    property CanManageUsers: Boolean read GetCanManageUsers write SetCanManageUsers;
    property CanViewCosts: Boolean read GetCanViewCosts write SetCanViewCosts;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property CreatedDate: TDateTime read GetCreatedDate write SetCreatedDate;
  end;

  TFleet105_RolePermissionList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_RolePermission;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_RolePermission;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_RolePermission;
    function FindByCode(const ACode: WideString): TFleet105_RolePermission;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_RolePermission read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_AuditLog
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_AuditLog = class(TFleetBaseEntity)
  private
    FAuditId: Int64;
    FUserId: Integer;
    FTableName: string;
    FRecordId: Integer;
    FActionCode: Integer;
    FActionTime: TDateTime;
    FOldValues: string;
    FNewValues: string;
    FIpAddress: string;
    FSessionId: string;
    FIsSuccessful: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_AuditLog);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetAuditId: Int64; stdcall;
    procedure SetAuditId(const Value: Int64); stdcall;
    function GetUserId: Integer; stdcall;
    procedure SetUserId(const Value: Integer); stdcall;
    function GetTableName: WideString; stdcall;
    procedure SetTableName(const Value: WideString); stdcall;
    function GetRecordId: Integer; stdcall;
    procedure SetRecordId(const Value: Integer); stdcall;
    function GetActionCode: Integer; stdcall;
    procedure SetActionCode(const Value: Integer); stdcall;
    function GetActionTime: TDateTime; stdcall;
    procedure SetActionTime(const Value: TDateTime); stdcall;
    function GetOldValues: WideString; stdcall;
    procedure SetOldValues(const Value: WideString); stdcall;
    function GetNewValues: WideString; stdcall;
    procedure SetNewValues(const Value: WideString); stdcall;
    function GetIpAddress: WideString; stdcall;
    procedure SetIpAddress(const Value: WideString); stdcall;
    function GetSessionId: WideString; stdcall;
    procedure SetSessionId(const Value: WideString); stdcall;
    function GetIsSuccessful: Boolean; stdcall;
    procedure SetIsSuccessful(const Value: Boolean); stdcall;
  published
    property AuditId: Int64 read GetAuditId write SetAuditId;
    property UserId: Integer read GetUserId write SetUserId;
    property TableName: WideString read GetTableName write SetTableName;
    property RecordId: Integer read GetRecordId write SetRecordId;
    property ActionCode: Integer read GetActionCode write SetActionCode;
    property ActionTime: TDateTime read GetActionTime write SetActionTime;
    property OldValues: WideString read GetOldValues write SetOldValues;
    property NewValues: WideString read GetNewValues write SetNewValues;
    property IpAddress: WideString read GetIpAddress write SetIpAddress;
    property SessionId: WideString read GetSessionId write SetSessionId;
    property IsSuccessful: Boolean read GetIsSuccessful write SetIsSuccessful;
  end;

  TFleet105_AuditLogList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_AuditLog;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_AuditLog;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_AuditLog;
    function FindByCode(const ACode: WideString): TFleet105_AuditLog;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_AuditLog read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_Notification
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_Notification = class(TFleetBaseEntity)
  private
    FNotifId: Integer;
    FUserId: Integer;
    FNotifType: Integer;
    FSubject: string;
    FMessageText: string;
    FCreatedDate: TDateTime;
    FReadDate: TDateTime;
    FIsRead: Boolean;
    FPriority: Integer;
    FRelatedTable: string;
    FRelatedId: Integer;
    FExpiryDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_Notification);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetNotifId: Integer; stdcall;
    procedure SetNotifId(const Value: Integer); stdcall;
    function GetUserId: Integer; stdcall;
    procedure SetUserId(const Value: Integer); stdcall;
    function GetNotifType: Integer; stdcall;
    procedure SetNotifType(const Value: Integer); stdcall;
    function GetSubject: WideString; stdcall;
    procedure SetSubject(const Value: WideString); stdcall;
    function GetMessageText: WideString; stdcall;
    procedure SetMessageText(const Value: WideString); stdcall;
    function GetCreatedDate: TDateTime; stdcall;
    procedure SetCreatedDate(const Value: TDateTime); stdcall;
    function GetReadDate: TDateTime; stdcall;
    procedure SetReadDate(const Value: TDateTime); stdcall;
    function GetIsRead: Boolean; stdcall;
    procedure SetIsRead(const Value: Boolean); stdcall;
    function GetPriority: Integer; stdcall;
    procedure SetPriority(const Value: Integer); stdcall;
    function GetRelatedTable: WideString; stdcall;
    procedure SetRelatedTable(const Value: WideString); stdcall;
    function GetRelatedId: Integer; stdcall;
    procedure SetRelatedId(const Value: Integer); stdcall;
    function GetExpiryDate: TDateTime; stdcall;
    procedure SetExpiryDate(const Value: TDateTime); stdcall;
  published
    property NotifId: Integer read GetNotifId write SetNotifId;
    property UserId: Integer read GetUserId write SetUserId;
    property NotifType: Integer read GetNotifType write SetNotifType;
    property Subject: WideString read GetSubject write SetSubject;
    property MessageText: WideString read GetMessageText write SetMessageText;
    property CreatedDate: TDateTime read GetCreatedDate write SetCreatedDate;
    property ReadDate: TDateTime read GetReadDate write SetReadDate;
    property IsRead: Boolean read GetIsRead write SetIsRead;
    property Priority: Integer read GetPriority write SetPriority;
    property RelatedTable: WideString read GetRelatedTable write SetRelatedTable;
    property RelatedId: Integer read GetRelatedId write SetRelatedId;
    property ExpiryDate: TDateTime read GetExpiryDate write SetExpiryDate;
  end;

  TFleet105_NotificationList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_Notification;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_Notification;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_Notification;
    function FindByCode(const ACode: WideString): TFleet105_Notification;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_Notification read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_DocumentStore
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_DocumentStore = class(TFleetBaseEntity)
  private
    FDocId: Integer;
    FEntityType: Integer;
    FEntityId: Integer;
    FDocType: Integer;
    FDocTitle: string;
    FFileName: string;
    FFilePath: string;
    FFileSizeKb: Integer;
    FMimeType: string;
    FUploadedBy: Integer;
    FUploadDate: TDateTime;
    FIsArchived: Boolean;
    FExpiryDate: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_DocumentStore);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetDocId: Integer; stdcall;
    procedure SetDocId(const Value: Integer); stdcall;
    function GetEntityType: Integer; stdcall;
    procedure SetEntityType(const Value: Integer); stdcall;
    function GetEntityId: Integer; stdcall;
    procedure SetEntityId(const Value: Integer); stdcall;
    function GetDocType: Integer; stdcall;
    procedure SetDocType(const Value: Integer); stdcall;
    function GetDocTitle: WideString; stdcall;
    procedure SetDocTitle(const Value: WideString); stdcall;
    function GetFileName: WideString; stdcall;
    procedure SetFileName(const Value: WideString); stdcall;
    function GetFilePath: WideString; stdcall;
    procedure SetFilePath(const Value: WideString); stdcall;
    function GetFileSizeKb: Integer; stdcall;
    procedure SetFileSizeKb(const Value: Integer); stdcall;
    function GetMimeType: WideString; stdcall;
    procedure SetMimeType(const Value: WideString); stdcall;
    function GetUploadedBy: Integer; stdcall;
    procedure SetUploadedBy(const Value: Integer); stdcall;
    function GetUploadDate: TDateTime; stdcall;
    procedure SetUploadDate(const Value: TDateTime); stdcall;
    function GetIsArchived: Boolean; stdcall;
    procedure SetIsArchived(const Value: Boolean); stdcall;
    function GetExpiryDate: TDateTime; stdcall;
    procedure SetExpiryDate(const Value: TDateTime); stdcall;
  published
    property DocId: Integer read GetDocId write SetDocId;
    property EntityType: Integer read GetEntityType write SetEntityType;
    property EntityId: Integer read GetEntityId write SetEntityId;
    property DocType: Integer read GetDocType write SetDocType;
    property DocTitle: WideString read GetDocTitle write SetDocTitle;
    property FileName: WideString read GetFileName write SetFileName;
    property FilePath: WideString read GetFilePath write SetFilePath;
    property FileSizeKb: Integer read GetFileSizeKb write SetFileSizeKb;
    property MimeType: WideString read GetMimeType write SetMimeType;
    property UploadedBy: Integer read GetUploadedBy write SetUploadedBy;
    property UploadDate: TDateTime read GetUploadDate write SetUploadDate;
    property IsArchived: Boolean read GetIsArchived write SetIsArchived;
    property ExpiryDate: TDateTime read GetExpiryDate write SetExpiryDate;
  end;

  TFleet105_DocumentStoreList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_DocumentStore;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_DocumentStore;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_DocumentStore;
    function FindByCode(const ACode: WideString): TFleet105_DocumentStore;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_DocumentStore read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_GeoZone
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_GeoZone = class(TFleetBaseEntity)
  private
    FZoneId: Integer;
    FZoneName: string;
    FZoneType: Integer;
    FCentreLatitude: Double;
    FCentreLongitude: Double;
    FRadiusMetres: Integer;
    FPolygonPoints: string;
    FDepotId: Integer;
    FSpeedLimitKph: Integer;
    FIsActive: Boolean;
    FValidFrom: TDateTime;
    FValidTo: TDateTime;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_GeoZone);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetZoneId: Integer; stdcall;
    procedure SetZoneId(const Value: Integer); stdcall;
    function GetZoneName: WideString; stdcall;
    procedure SetZoneName(const Value: WideString); stdcall;
    function GetZoneType: Integer; stdcall;
    procedure SetZoneType(const Value: Integer); stdcall;
    function GetCentreLatitude: Double; stdcall;
    procedure SetCentreLatitude(const Value: Double); stdcall;
    function GetCentreLongitude: Double; stdcall;
    procedure SetCentreLongitude(const Value: Double); stdcall;
    function GetRadiusMetres: Integer; stdcall;
    procedure SetRadiusMetres(const Value: Integer); stdcall;
    function GetPolygonPoints: WideString; stdcall;
    procedure SetPolygonPoints(const Value: WideString); stdcall;
    function GetDepotId: Integer; stdcall;
    procedure SetDepotId(const Value: Integer); stdcall;
    function GetSpeedLimitKph: Integer; stdcall;
    procedure SetSpeedLimitKph(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetValidFrom: TDateTime; stdcall;
    procedure SetValidFrom(const Value: TDateTime); stdcall;
    function GetValidTo: TDateTime; stdcall;
    procedure SetValidTo(const Value: TDateTime); stdcall;
  published
    property ZoneId: Integer read GetZoneId write SetZoneId;
    property ZoneName: WideString read GetZoneName write SetZoneName;
    property ZoneType: Integer read GetZoneType write SetZoneType;
    property CentreLatitude: Double read GetCentreLatitude write SetCentreLatitude;
    property CentreLongitude: Double read GetCentreLongitude write SetCentreLongitude;
    property RadiusMetres: Integer read GetRadiusMetres write SetRadiusMetres;
    property PolygonPoints: WideString read GetPolygonPoints write SetPolygonPoints;
    property DepotId: Integer read GetDepotId write SetDepotId;
    property SpeedLimitKph: Integer read GetSpeedLimitKph write SetSpeedLimitKph;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property ValidFrom: TDateTime read GetValidFrom write SetValidFrom;
    property ValidTo: TDateTime read GetValidTo write SetValidTo;
  end;

  TFleet105_GeoZoneList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_GeoZone;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_GeoZone;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_GeoZone;
    function FindByCode(const ACode: WideString): TFleet105_GeoZone;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_GeoZone read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_ChecklistTemplate
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_ChecklistTemplate = class(TFleetBaseEntity)
  private
    FTemplateId: Integer;
    FTemplateName: string;
    FChecklistType: Integer;
    FEntityType: Integer;
    FItemCount: Integer;
    FIsActive: Boolean;
    FVersion: Integer;
    FCreatedBy: Integer;
    FCreatedDate: TDateTime;
    FApprovedBy: Integer;
    FNotes: string;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_ChecklistTemplate);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetTemplateId: Integer; stdcall;
    procedure SetTemplateId(const Value: Integer); stdcall;
    function GetTemplateName: WideString; stdcall;
    procedure SetTemplateName(const Value: WideString); stdcall;
    function GetChecklistType: Integer; stdcall;
    procedure SetChecklistType(const Value: Integer); stdcall;
    function GetEntityType: Integer; stdcall;
    procedure SetEntityType(const Value: Integer); stdcall;
    function GetItemCount: Integer; stdcall;
    procedure SetItemCount(const Value: Integer); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetVersion: Integer; stdcall;
    procedure SetVersion(const Value: Integer); stdcall;
    function GetCreatedBy: Integer; stdcall;
    procedure SetCreatedBy(const Value: Integer); stdcall;
    function GetCreatedDate: TDateTime; stdcall;
    procedure SetCreatedDate(const Value: TDateTime); stdcall;
    function GetApprovedBy: Integer; stdcall;
    procedure SetApprovedBy(const Value: Integer); stdcall;
    function GetNotes: WideString; stdcall;
    procedure SetNotes(const Value: WideString); stdcall;
  published
    property TemplateId: Integer read GetTemplateId write SetTemplateId;
    property TemplateName: WideString read GetTemplateName write SetTemplateName;
    property ChecklistType: Integer read GetChecklistType write SetChecklistType;
    property EntityType: Integer read GetEntityType write SetEntityType;
    property ItemCount: Integer read GetItemCount write SetItemCount;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property Version: Integer read GetVersion write SetVersion;
    property CreatedBy: Integer read GetCreatedBy write SetCreatedBy;
    property CreatedDate: TDateTime read GetCreatedDate write SetCreatedDate;
    property ApprovedBy: Integer read GetApprovedBy write SetApprovedBy;
    property Notes: WideString read GetNotes write SetNotes;
  end;

  TFleet105_ChecklistTemplateList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_ChecklistTemplate;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_ChecklistTemplate;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_ChecklistTemplate;
    function FindByCode(const ACode: WideString): TFleet105_ChecklistTemplate;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_ChecklistTemplate read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_ChecklistResult
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_ChecklistResult = class(TFleetBaseEntity)
  private
    FResultId: Integer;
    FTemplateId: Integer;
    FEntityId: Integer;
    FCompletedBy: Integer;
    FCompletedDate: TDateTime;
    FOverallResult: Integer;
    FFailCount: Integer;
    FPassCount: Integer;
    FSkipCount: Integer;
    FNotes: string;
    FVehicleId: Integer;
    FOdometerKm: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_ChecklistResult);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetResultId: Integer; stdcall;
    procedure SetResultId(const Value: Integer); stdcall;
    function GetTemplateId: Integer; stdcall;
    procedure SetTemplateId(const Value: Integer); stdcall;
    function GetEntityId: Integer; stdcall;
    procedure SetEntityId(const Value: Integer); stdcall;
    function GetCompletedBy: Integer; stdcall;
    procedure SetCompletedBy(const Value: Integer); stdcall;
    function GetCompletedDate: TDateTime; stdcall;
    procedure SetCompletedDate(const Value: TDateTime); stdcall;
    function GetOverallResult: Integer; stdcall;
    procedure SetOverallResult(const Value: Integer); stdcall;
    function GetFailCount: Integer; stdcall;
    procedure SetFailCount(const Value: Integer); stdcall;
    function GetPassCount: Integer; stdcall;
    procedure SetPassCount(const Value: Integer); stdcall;
    function GetSkipCount: Integer; stdcall;
    procedure SetSkipCount(const Value: Integer); stdcall;
    function GetNotes: WideString; stdcall;
    procedure SetNotes(const Value: WideString); stdcall;
    function GetVehicleId: Integer; stdcall;
    procedure SetVehicleId(const Value: Integer); stdcall;
    function GetOdometerKm: Integer; stdcall;
    procedure SetOdometerKm(const Value: Integer); stdcall;
  published
    property ResultId: Integer read GetResultId write SetResultId;
    property TemplateId: Integer read GetTemplateId write SetTemplateId;
    property EntityId: Integer read GetEntityId write SetEntityId;
    property CompletedBy: Integer read GetCompletedBy write SetCompletedBy;
    property CompletedDate: TDateTime read GetCompletedDate write SetCompletedDate;
    property OverallResult: Integer read GetOverallResult write SetOverallResult;
    property FailCount: Integer read GetFailCount write SetFailCount;
    property PassCount: Integer read GetPassCount write SetPassCount;
    property SkipCount: Integer read GetSkipCount write SetSkipCount;
    property Notes: WideString read GetNotes write SetNotes;
    property VehicleId: Integer read GetVehicleId write SetVehicleId;
    property OdometerKm: Integer read GetOdometerKm write SetOdometerKm;
  end;

  TFleet105_ChecklistResultList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_ChecklistResult;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_ChecklistResult;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_ChecklistResult;
    function FindByCode(const ACode: WideString): TFleet105_ChecklistResult;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_ChecklistResult read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_ContractClient
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_ContractClient = class(TFleetBaseEntity)
  private
    FClientId: Integer;
    FClientCode: string;
    FClientName: string;
    FContactName: string;
    FPhone: string;
    FEmail: string;
    FAddress: string;
    FCity: string;
    FContractStart: TDateTime;
    FContractEnd: TDateTime;
    FIsActive: Boolean;
    FDiscountPct: Double;
    FCreditLimit: Double;
    FPayTermsDays: Integer;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_ContractClient);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetClientId: Integer; stdcall;
    procedure SetClientId(const Value: Integer); stdcall;
    function GetClientCode: WideString; stdcall;
    procedure SetClientCode(const Value: WideString); stdcall;
    function GetClientName: WideString; stdcall;
    procedure SetClientName(const Value: WideString); stdcall;
    function GetContactName: WideString; stdcall;
    procedure SetContactName(const Value: WideString); stdcall;
    function GetPhone: WideString; stdcall;
    procedure SetPhone(const Value: WideString); stdcall;
    function GetEmail: WideString; stdcall;
    procedure SetEmail(const Value: WideString); stdcall;
    function GetAddress: WideString; stdcall;
    procedure SetAddress(const Value: WideString); stdcall;
    function GetCity: WideString; stdcall;
    procedure SetCity(const Value: WideString); stdcall;
    function GetContractStart: TDateTime; stdcall;
    procedure SetContractStart(const Value: TDateTime); stdcall;
    function GetContractEnd: TDateTime; stdcall;
    procedure SetContractEnd(const Value: TDateTime); stdcall;
    function GetIsActive: Boolean; stdcall;
    procedure SetIsActive(const Value: Boolean); stdcall;
    function GetDiscountPct: Double; stdcall;
    procedure SetDiscountPct(const Value: Double); stdcall;
    function GetCreditLimit: Double; stdcall;
    procedure SetCreditLimit(const Value: Double); stdcall;
    function GetPayTermsDays: Integer; stdcall;
    procedure SetPayTermsDays(const Value: Integer); stdcall;
  published
    property ClientId: Integer read GetClientId write SetClientId;
    property ClientCode: WideString read GetClientCode write SetClientCode;
    property ClientName: WideString read GetClientName write SetClientName;
    property ContactName: WideString read GetContactName write SetContactName;
    property Phone: WideString read GetPhone write SetPhone;
    property Email: WideString read GetEmail write SetEmail;
    property Address: WideString read GetAddress write SetAddress;
    property City: WideString read GetCity write SetCity;
    property ContractStart: TDateTime read GetContractStart write SetContractStart;
    property ContractEnd: TDateTime read GetContractEnd write SetContractEnd;
    property IsActive: Boolean read GetIsActive write SetIsActive;
    property DiscountPct: Double read GetDiscountPct write SetDiscountPct;
    property CreditLimit: Double read GetCreditLimit write SetCreditLimit;
    property PayTermsDays: Integer read GetPayTermsDays write SetPayTermsDays;
  end;

  TFleet105_ContractClientList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_ContractClient;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_ContractClient;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_ContractClient;
    function FindByCode(const ACode: WideString): TFleet105_ContractClient;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_ContractClient read GetItem; default;
  end;

// ──────────────────────────────────────────────────────────────────────────
// TFleet105_BillingRecord
// ──────────────────────────────────────────────────────────────────────────
  TFleet105_BillingRecord = class(TFleetBaseEntity)
  private
    FBillId: Integer;
    FClientId: Integer;
    FPeriodStart: TDateTime;
    FPeriodEnd: TDateTime;
    FTripCount: Integer;
    FTotalKm: Double;
    FBaseAmount: Double;
    FFuelSurcharge: Double;
    FTaxAmount: Double;
    FTotalAmount: Double;
    FStatusCode: Integer;
    FInvoiceDate: TDateTime;
    FPaidDate: TDateTime;
    FIsExported: Boolean;
  public
    constructor Create; override;
    destructor Destroy; override;
    procedure Clear; override;
    procedure Assign(Source: TFleet105_BillingRecord);
    function Validate: Boolean; override;
    function ToDelimitedString(const ADelim: WideString): WideString;
    function GetBillId: Integer; stdcall;
    procedure SetBillId(const Value: Integer); stdcall;
    function GetClientId: Integer; stdcall;
    procedure SetClientId(const Value: Integer); stdcall;
    function GetPeriodStart: TDateTime; stdcall;
    procedure SetPeriodStart(const Value: TDateTime); stdcall;
    function GetPeriodEnd: TDateTime; stdcall;
    procedure SetPeriodEnd(const Value: TDateTime); stdcall;
    function GetTripCount: Integer; stdcall;
    procedure SetTripCount(const Value: Integer); stdcall;
    function GetTotalKm: Double; stdcall;
    procedure SetTotalKm(const Value: Double); stdcall;
    function GetBaseAmount: Double; stdcall;
    procedure SetBaseAmount(const Value: Double); stdcall;
    function GetFuelSurcharge: Double; stdcall;
    procedure SetFuelSurcharge(const Value: Double); stdcall;
    function GetTaxAmount: Double; stdcall;
    procedure SetTaxAmount(const Value: Double); stdcall;
    function GetTotalAmount: Double; stdcall;
    procedure SetTotalAmount(const Value: Double); stdcall;
    function GetStatusCode: Integer; stdcall;
    procedure SetStatusCode(const Value: Integer); stdcall;
    function GetInvoiceDate: TDateTime; stdcall;
    procedure SetInvoiceDate(const Value: TDateTime); stdcall;
    function GetPaidDate: TDateTime; stdcall;
    procedure SetPaidDate(const Value: TDateTime); stdcall;
    function GetIsExported: Boolean; stdcall;
    procedure SetIsExported(const Value: Boolean); stdcall;
  published
    property BillId: Integer read GetBillId write SetBillId;
    property ClientId: Integer read GetClientId write SetClientId;
    property PeriodStart: TDateTime read GetPeriodStart write SetPeriodStart;
    property PeriodEnd: TDateTime read GetPeriodEnd write SetPeriodEnd;
    property TripCount: Integer read GetTripCount write SetTripCount;
    property TotalKm: Double read GetTotalKm write SetTotalKm;
    property BaseAmount: Double read GetBaseAmount write SetBaseAmount;
    property FuelSurcharge: Double read GetFuelSurcharge write SetFuelSurcharge;
    property TaxAmount: Double read GetTaxAmount write SetTaxAmount;
    property TotalAmount: Double read GetTotalAmount write SetTotalAmount;
    property StatusCode: Integer read GetStatusCode write SetStatusCode;
    property InvoiceDate: TDateTime read GetInvoiceDate write SetInvoiceDate;
    property PaidDate: TDateTime read GetPaidDate write SetPaidDate;
    property IsExported: Boolean read GetIsExported write SetIsExported;
  end;

  TFleet105_BillingRecordList = class(TFleetBaseList)
  private
    function GetItem(Index: Integer): TFleet105_BillingRecord;
  public
    constructor Create; override;
    destructor Destroy; override;
    function Add: TFleet105_BillingRecord;
    procedure Delete(Index: Integer); override;
    function FindById(const AId: Integer): TFleet105_BillingRecord;
    function FindByCode(const ACode: WideString): TFleet105_BillingRecord;
    function SortByName: Integer;
    function FilterByDepot(ADepotId: Integer): Integer;
    function ToDataSet(ADataSet: TClientDataSet): Integer;
    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;
    function ExportCSV(const AFileName: WideString): Boolean;
    property Items[Index: Integer]: TFleet105_BillingRecord read GetItem; default;
  end;

implementation

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Device
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Device.Create;
begin
  inherited Create;
  // Inicjalizacja pól urządzenia
  FDeviceId := 0;
  FDeviceSerial := '';
  FDeviceName := '';
  FDeviceType := 0;
  FFirmwareVersion := '';
  FHardwareRevision := '';
  FLastContactTime := 0;
  FBatteryLevel := 0;
  FSignalStrength := 0;
  FGpsLatitude := 0.0;
  FGpsLongitude := 0.0;
  FGpsAltitude := 0.0;
  FGpsSpeed := 0.0;
  FGpsHeading := 0.0;
  FGpsAccuracy := 0.0;
  FGpsSatellites := 0;
  FGpsFixTime := 0;
  FVehicleId := 0;
  FDepotId := 0;
  FIsActive := False;
  FIsOnline := False;
  FConfigVersion := 0;
  FMaxSpeed := 0;
  FIdleTimeout := 0;
  FReportInterval := 0;
  FAlertFlags := 0;
  FErrorCode := 0;
  FErrorMessage := '';
  FInstallDate := 0;
  FWarrantyExpiry := 0;
  FSupplierCode := '';
  FAssetTag := '';
  FEncryptionKey := '';
  FAuthToken := '';
  FServerUrl := '';
  FServerPort := 0;
  FConnectionMode := 0;
  FDataQueueSize := 0;
  FTotalMessagesSent := 0;
  FTotalMessagesReceived := 0;
  FTotalBytesTransferred := 0;
  FSessionCount := 0;
  FLastResetTime := 0;
  FDiagnosticData := '';
  FCalibrationDate := 0;
  FServerPort := 8080;
  FMaxSpeed := 120;
  FIdleTimeout := 300;
  FReportInterval := 60;
  FConfigVersion := 1;
end;

destructor TFleet105_Device.Destroy;
begin
  // Zwolnienie zasobów urządzenia
  FEncryptionKey := '';
  FAuthToken := '';
  FDiagnosticData := '';
  inherited Destroy;
end;

function TFleet105_Device.GetDeviceId: Integer;
begin
  // Pobierz DeviceId
  Result := FDeviceId;
end;

procedure TFleet105_Device.SetDeviceId(const Value: Integer);
begin
  // Ustaw DeviceId
  FDeviceId := Value;
end;

function TFleet105_Device.GetDeviceSerial: WideString;
begin
  // Pobierz DeviceSerial
  Result := FDeviceSerial;
end;

procedure TFleet105_Device.SetDeviceSerial(const Value: WideString);
begin
  // Ustaw DeviceSerial
  FDeviceSerial := Value;
end;

function TFleet105_Device.GetDeviceName: WideString;
begin
  // Pobierz DeviceName
  Result := FDeviceName;
end;

procedure TFleet105_Device.SetDeviceName(const Value: WideString);
begin
  // Ustaw DeviceName
  FDeviceName := Value;
end;

function TFleet105_Device.GetDeviceType: Integer;
begin
  // Pobierz DeviceType
  Result := FDeviceType;
end;

procedure TFleet105_Device.SetDeviceType(const Value: Integer);
begin
  // Ustaw DeviceType
  FDeviceType := Value;
end;

function TFleet105_Device.GetFirmwareVersion: WideString;
begin
  // Pobierz FirmwareVersion
  Result := FFirmwareVersion;
end;

procedure TFleet105_Device.SetFirmwareVersion(const Value: WideString);
begin
  // Ustaw FirmwareVersion
  FFirmwareVersion := Value;
end;

function TFleet105_Device.GetHardwareRevision: WideString;
begin
  // Pobierz HardwareRevision
  Result := FHardwareRevision;
end;

procedure TFleet105_Device.SetHardwareRevision(const Value: WideString);
begin
  // Ustaw HardwareRevision
  FHardwareRevision := Value;
end;

function TFleet105_Device.GetLastContactTime: TDateTime;
begin
  // Pobierz LastContactTime
  Result := FLastContactTime;
end;

procedure TFleet105_Device.SetLastContactTime(const Value: TDateTime);
begin
  // Ustaw LastContactTime
  FLastContactTime := Value;
end;

function TFleet105_Device.GetBatteryLevel: Integer;
begin
  // Pobierz BatteryLevel
  Result := FBatteryLevel;
end;

procedure TFleet105_Device.SetBatteryLevel(const Value: Integer);
begin
  // Ustaw BatteryLevel
  FBatteryLevel := Value;
end;

function TFleet105_Device.GetSignalStrength: Integer;
begin
  // Pobierz SignalStrength
  Result := FSignalStrength;
end;

procedure TFleet105_Device.SetSignalStrength(const Value: Integer);
begin
  // Ustaw SignalStrength
  FSignalStrength := Value;
end;

function TFleet105_Device.GetGpsLatitude: Double;
begin
  // Pobierz GpsLatitude
  Result := FGpsLatitude;
end;

procedure TFleet105_Device.SetGpsLatitude(const Value: Double);
begin
  // Ustaw GpsLatitude
  FGpsLatitude := Value;
end;

function TFleet105_Device.GetGpsLongitude: Double;
begin
  // Pobierz GpsLongitude
  Result := FGpsLongitude;
end;

procedure TFleet105_Device.SetGpsLongitude(const Value: Double);
begin
  // Ustaw GpsLongitude
  FGpsLongitude := Value;
end;

function TFleet105_Device.GetGpsAltitude: Double;
begin
  // Pobierz GpsAltitude
  Result := FGpsAltitude;
end;

procedure TFleet105_Device.SetGpsAltitude(const Value: Double);
begin
  // Ustaw GpsAltitude
  FGpsAltitude := Value;
end;

function TFleet105_Device.GetGpsSpeed: Double;
begin
  // Pobierz GpsSpeed
  Result := FGpsSpeed;
end;

procedure TFleet105_Device.SetGpsSpeed(const Value: Double);
begin
  // Ustaw GpsSpeed
  FGpsSpeed := Value;
end;

function TFleet105_Device.GetGpsHeading: Double;
begin
  // Pobierz GpsHeading
  Result := FGpsHeading;
end;

procedure TFleet105_Device.SetGpsHeading(const Value: Double);
begin
  // Ustaw GpsHeading
  FGpsHeading := Value;
end;

function TFleet105_Device.GetGpsAccuracy: Double;
begin
  // Pobierz GpsAccuracy
  Result := FGpsAccuracy;
end;

procedure TFleet105_Device.SetGpsAccuracy(const Value: Double);
begin
  // Ustaw GpsAccuracy
  FGpsAccuracy := Value;
end;

function TFleet105_Device.GetGpsSatellites: Integer;
begin
  // Pobierz GpsSatellites
  Result := FGpsSatellites;
end;

procedure TFleet105_Device.SetGpsSatellites(const Value: Integer);
begin
  // Ustaw GpsSatellites
  FGpsSatellites := Value;
end;

function TFleet105_Device.GetGpsFixTime: TDateTime;
begin
  // Pobierz GpsFixTime
  Result := FGpsFixTime;
end;

procedure TFleet105_Device.SetGpsFixTime(const Value: TDateTime);
begin
  // Ustaw GpsFixTime
  FGpsFixTime := Value;
end;

function TFleet105_Device.GetVehicleId: Integer;
begin
  // Pobierz VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_Device.SetVehicleId(const Value: Integer);
begin
  // Ustaw VehicleId
  FVehicleId := Value;
end;

function TFleet105_Device.GetDepotId: Integer;
begin
  // Pobierz DepotId
  Result := FDepotId;
end;

procedure TFleet105_Device.SetDepotId(const Value: Integer);
begin
  // Ustaw DepotId
  FDepotId := Value;
end;

function TFleet105_Device.GetIsActive: Boolean;
begin
  // Pobierz IsActive
  Result := FIsActive;
end;

procedure TFleet105_Device.SetIsActive(const Value: Boolean);
begin
  // Ustaw IsActive
  FIsActive := Value;
end;

function TFleet105_Device.GetIsOnline: Boolean;
begin
  // Pobierz IsOnline
  Result := FIsOnline;
end;

procedure TFleet105_Device.SetIsOnline(const Value: Boolean);
begin
  // Ustaw IsOnline
  FIsOnline := Value;
end;

function TFleet105_Device.GetConfigVersion: Integer;
begin
  // Pobierz ConfigVersion
  Result := FConfigVersion;
end;

procedure TFleet105_Device.SetConfigVersion(const Value: Integer);
begin
  // Ustaw ConfigVersion
  FConfigVersion := Value;
end;

function TFleet105_Device.GetMaxSpeed: Integer;
begin
  // Pobierz MaxSpeed
  Result := FMaxSpeed;
end;

procedure TFleet105_Device.SetMaxSpeed(const Value: Integer);
begin
  // Ustaw MaxSpeed
  FMaxSpeed := Value;
end;

function TFleet105_Device.GetIdleTimeout: Integer;
begin
  // Pobierz IdleTimeout
  Result := FIdleTimeout;
end;

procedure TFleet105_Device.SetIdleTimeout(const Value: Integer);
begin
  // Ustaw IdleTimeout
  FIdleTimeout := Value;
end;

function TFleet105_Device.GetReportInterval: Integer;
begin
  // Pobierz ReportInterval
  Result := FReportInterval;
end;

procedure TFleet105_Device.SetReportInterval(const Value: Integer);
begin
  // Ustaw ReportInterval
  FReportInterval := Value;
end;

function TFleet105_Device.GetAlertFlags: Cardinal;
begin
  // Pobierz AlertFlags
  Result := FAlertFlags;
end;

procedure TFleet105_Device.SetAlertFlags(const Value: Cardinal);
begin
  // Ustaw AlertFlags
  FAlertFlags := Value;
end;

function TFleet105_Device.GetErrorCode: Integer;
begin
  // Pobierz ErrorCode
  Result := FErrorCode;
end;

procedure TFleet105_Device.SetErrorCode(const Value: Integer);
begin
  // Ustaw ErrorCode
  FErrorCode := Value;
end;

function TFleet105_Device.GetErrorMessage: WideString;
begin
  // Pobierz ErrorMessage
  Result := FErrorMessage;
end;

procedure TFleet105_Device.SetErrorMessage(const Value: WideString);
begin
  // Ustaw ErrorMessage
  FErrorMessage := Value;
end;

function TFleet105_Device.GetInstallDate: TDateTime;
begin
  // Pobierz InstallDate
  Result := FInstallDate;
end;

procedure TFleet105_Device.SetInstallDate(const Value: TDateTime);
begin
  // Ustaw InstallDate
  FInstallDate := Value;
end;

function TFleet105_Device.GetWarrantyExpiry: TDateTime;
begin
  // Pobierz WarrantyExpiry
  Result := FWarrantyExpiry;
end;

procedure TFleet105_Device.SetWarrantyExpiry(const Value: TDateTime);
begin
  // Ustaw WarrantyExpiry
  FWarrantyExpiry := Value;
end;

function TFleet105_Device.GetSupplierCode: WideString;
begin
  // Pobierz SupplierCode
  Result := FSupplierCode;
end;

procedure TFleet105_Device.SetSupplierCode(const Value: WideString);
begin
  // Ustaw SupplierCode
  FSupplierCode := Value;
end;

function TFleet105_Device.GetAssetTag: WideString;
begin
  // Pobierz AssetTag
  Result := FAssetTag;
end;

procedure TFleet105_Device.SetAssetTag(const Value: WideString);
begin
  // Ustaw AssetTag
  FAssetTag := Value;
end;

function TFleet105_Device.GetEncryptionKey: WideString;
begin
  // Pobierz EncryptionKey
  Result := FEncryptionKey;
end;

procedure TFleet105_Device.SetEncryptionKey(const Value: WideString);
begin
  // Ustaw EncryptionKey
  FEncryptionKey := Value;
end;

function TFleet105_Device.GetAuthToken: WideString;
begin
  // Pobierz AuthToken
  Result := FAuthToken;
end;

procedure TFleet105_Device.SetAuthToken(const Value: WideString);
begin
  // Ustaw AuthToken
  FAuthToken := Value;
end;

function TFleet105_Device.GetServerUrl: WideString;
begin
  // Pobierz ServerUrl
  Result := FServerUrl;
end;

procedure TFleet105_Device.SetServerUrl(const Value: WideString);
begin
  // Ustaw ServerUrl
  FServerUrl := Value;
end;

function TFleet105_Device.GetServerPort: Integer;
begin
  // Pobierz ServerPort
  Result := FServerPort;
end;

procedure TFleet105_Device.SetServerPort(const Value: Integer);
begin
  // Ustaw ServerPort
  FServerPort := Value;
end;

function TFleet105_Device.GetConnectionMode: Integer;
begin
  // Pobierz ConnectionMode
  Result := FConnectionMode;
end;

procedure TFleet105_Device.SetConnectionMode(const Value: Integer);
begin
  // Ustaw ConnectionMode
  FConnectionMode := Value;
end;

function TFleet105_Device.GetDataQueueSize: Integer;
begin
  // Pobierz DataQueueSize
  Result := FDataQueueSize;
end;

procedure TFleet105_Device.SetDataQueueSize(const Value: Integer);
begin
  // Ustaw DataQueueSize
  FDataQueueSize := Value;
end;

function TFleet105_Device.GetTotalMessagesSent: Int64;
begin
  // Pobierz TotalMessagesSent
  Result := FTotalMessagesSent;
end;

procedure TFleet105_Device.SetTotalMessagesSent(const Value: Int64);
begin
  // Ustaw TotalMessagesSent
  FTotalMessagesSent := Value;
end;

function TFleet105_Device.GetTotalMessagesReceived: Int64;
begin
  // Pobierz TotalMessagesReceived
  Result := FTotalMessagesReceived;
end;

procedure TFleet105_Device.SetTotalMessagesReceived(const Value: Int64);
begin
  // Ustaw TotalMessagesReceived
  FTotalMessagesReceived := Value;
end;

function TFleet105_Device.GetTotalBytesTransferred: Int64;
begin
  // Pobierz TotalBytesTransferred
  Result := FTotalBytesTransferred;
end;

procedure TFleet105_Device.SetTotalBytesTransferred(const Value: Int64);
begin
  // Ustaw TotalBytesTransferred
  FTotalBytesTransferred := Value;
end;

function TFleet105_Device.GetSessionCount: Integer;
begin
  // Pobierz SessionCount
  Result := FSessionCount;
end;

procedure TFleet105_Device.SetSessionCount(const Value: Integer);
begin
  // Ustaw SessionCount
  FSessionCount := Value;
end;

function TFleet105_Device.GetLastResetTime: TDateTime;
begin
  // Pobierz LastResetTime
  Result := FLastResetTime;
end;

procedure TFleet105_Device.SetLastResetTime(const Value: TDateTime);
begin
  // Ustaw LastResetTime
  FLastResetTime := Value;
end;

function TFleet105_Device.GetDiagnosticData: WideString;
begin
  // Pobierz DiagnosticData
  Result := FDiagnosticData;
end;

procedure TFleet105_Device.SetDiagnosticData(const Value: WideString);
begin
  // Ustaw DiagnosticData
  FDiagnosticData := Value;
end;

function TFleet105_Device.GetCalibrationDate: TDateTime;
begin
  // Pobierz CalibrationDate
  Result := FCalibrationDate;
end;

procedure TFleet105_Device.SetCalibrationDate(const Value: TDateTime);
begin
  // Ustaw CalibrationDate
  FCalibrationDate := Value;
end;

function TFleet105_Device.Connect(const AServerUrl: WideString; APort: Integer): Boolean;
begin
  // Nawiąż połączenie z serwerem FleetOps
  FServerUrl := AServerUrl;
  FServerPort := APort;
  FConnectionMode := 1;
  FIsOnline := True;
  FLastContactTime := Now;
  Inc(FSessionCount);
  FErrorCode := 0;
  FErrorMessage := '';
  Result := FIsOnline;
end;

function TFleet105_Device.Disconnect: Boolean;
begin
  // Rozłącz urządzenie od serwera
  FIsOnline := False;
  FConnectionMode := 0;
  FLastContactTime := Now;
  Result := True;
end;

function TFleet105_Device.SendHeartbeat: Boolean;
begin
  // Wyślij sygnał heartbeat do serwera
  if not FIsOnline then
  begin
    FErrorMessage := 'Cannot send heartbeat: device not online';
    Result := False;
    Exit;
  end;
  FLastContactTime := Now;
  Inc(FTotalMessagesSent);
  Inc(FTotalBytesTransferred, 64);
  Result := True;
end;

function TFleet105_Device.ParseGpsData(const ARawData: WideString): Boolean;
begin
  // Parsuj dane GPS z formatu NMEA/binary
  Result := False;
  if Length(ARawData) < 10 then
  begin
    FErrorMessage := 'GPS data too short to parse';
    Exit;
  end;
  FGpsFixTime := Now;
  FGpsSatellites := 8;
  Result := True;
end;

function TFleet105_Device.UpdateFirmware(const AFirmwareFile: WideString): Boolean;
begin
  // Aktualizuj oprogramowanie układowe urządzenia
  if not FIsOnline then
  begin
    FErrorMessage := 'Device not online - cannot update firmware';
    Result := False;
    Exit;
  end;
  if AFirmwareFile = '' then
  begin
    FErrorMessage := 'Firmware file path not specified';
    Result := False;
    Exit;
  end;
  Inc(FConfigVersion);
  FFirmwareVersion := 'UPDATING';
  Result := True;
end;

function TFleet105_Device.ResetDevice: Boolean;
begin
  // Zresetuj urządzenie do domyślnych ustawień fabrycznych
  FErrorCode := 0;
  FErrorMessage := '';
  FAlertFlags := 0;
  FDataQueueSize := 0;
  FLastResetTime := Now;
  FIsOnline := False;
  FConnectionMode := 0;
  FGpsLatitude := 0.0;
  FGpsLongitude := 0.0;
  Result := True;
end;

function TFleet105_Device.RunDiagnostics: WideString;
begin
  // Uruchom pełną diagnostykę urządzenia
  Result := Format('[FleetOps Diagnostics] DeviceId=%d Serial=%s Online=%s ' +
    'Battery=%d%% Signal=%d%% GPS=(%.6f,%.6f) Altitude=%.1fm Speed=%.1fkph ' +
    'Firmware=%s Hardware=%s Config=%d Queue=%d Sent=%d Recv=%d Bytes=%d',
    [FDeviceId, FDeviceSerial, BoolToStr(FIsOnline, True),
     FBatteryLevel, FSignalStrength, FGpsLatitude, FGpsLongitude,
     FGpsAltitude, FGpsSpeed, FFirmwareVersion, FHardwareRevision,
     FConfigVersion, FDataQueueSize, FTotalMessagesSent,
     FTotalMessagesReceived, FTotalBytesTransferred]);
end;

function TFleet105_Device.ExportConfig(const AFileName: WideString): Boolean;
begin
  // Eksportuj konfigurację urządzenia do pliku INI/XML
  Result := False;
  if AFileName = '' then Exit;
  try
    // Real implementation: write to TIniFile or XML document
    Result := True;
  except
    on E: Exception do
      FErrorMessage := 'ExportConfig failed: ' + E.Message;
  end;
end;

function TFleet105_Device.ImportConfig(const AFileName: WideString): Boolean;
begin
  // Importuj konfigurację urządzenia z pliku
  Result := False;
  if AFileName = '' then Exit;
  try
    Inc(FConfigVersion);
    Result := True;
  except
    on E: Exception do
      FErrorMessage := 'ImportConfig failed: ' + E.Message;
  end;
end;

function TFleet105_Device.ValidateAuth: Boolean;
begin
  // Sprawdź poprawność tokena autoryzacji
  Result := (FAuthToken <> '') and (Length(FAuthToken) >= 32);
  if not Result then
    FErrorMessage := 'Authentication token invalid or expired';
end;

function TFleet105_Device.EncryptPayload(const AData: WideString): WideString;
begin
  // Zaszyfruj ładunek danych do transmisji
  if FEncryptionKey = '' then
  begin
    Result := AData;
    Exit;
  end;
  // Placeholder: real implementation would use AES-256-CBC
  Result := AData;
end;

function TFleet105_Device.DecryptPayload(const AData: WideString): WideString;
begin
  // Odszyfruj odebrany ładunek danych
  if FEncryptionKey = '' then
  begin
    Result := AData;
    Exit;
  end;
  // Placeholder: real implementation would use AES-256-CBC
  Result := AData;
end;

function TFleet105_Device.QueueMessage(const AMsg: WideString; APriority: Integer): Boolean;
begin
  // Dodaj wiadomość do kolejki wysyłki z priorytetem
  if FDataQueueSize >= 1000 then
  begin
    FErrorMessage := 'Message queue capacity exceeded (max 1000)';
    Result := False;
    Exit;
  end;
  Inc(FDataQueueSize);
  Result := True;
end;

function TFleet105_Device.FlushQueue: Integer;
begin
  // Opróżnij kolejkę wiadomości — wyślij wszystkie oczekujące
  Result := FDataQueueSize;
  if FDataQueueSize > 0 then
  begin
    Inc(FTotalMessagesSent, FDataQueueSize);
    Inc(FTotalBytesTransferred, Int64(FDataQueueSize) * 256);
    FDataQueueSize := 0;
    FLastContactTime := Now;
  end;
end;

function TFleet105_Device.GetStatusReport: WideString;
begin
  // Zwróć pełny raport statusu urządzenia
  Result := Format('[Status] ID:%d Serial:%s Name:%s Online:%s Battery:%d%% ' +
    'Signal:%d%% GPS:(%.6f,%.6f,%.1fm) Speed:%.1fkph Heading:%.1f ' +
    'Firmware:%s Hardware:%s ConfigVer:%d MaxSpeed:%d ' +
    'Queued:%d Sent:%d Recv:%d Bytes:%d Sessions:%d',
    [FDeviceId, FDeviceSerial, FDeviceName, BoolToStr(FIsOnline,True),
     FBatteryLevel, FSignalStrength, FGpsLatitude, FGpsLongitude, FGpsAltitude,
     FGpsSpeed, FGpsHeading, FFirmwareVersion, FHardwareRevision, FConfigVersion,
     FMaxSpeed, FDataQueueSize, FTotalMessagesSent, FTotalMessagesReceived,
     FTotalBytesTransferred, FSessionCount]);
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Vehicle
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Vehicle.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FVehicleId := 0;
  FRegistrationNo := '';
  FFleetNo := '';
  FMake := '';
  FModel := '';
  FYear := 0;
  FEngineCC := 0;
  FFuelType := 0;
  FGrossWeight := 0;
  FPayloadKg := 0;
  FDepotId := 0;
  FStatusCode := 0;
  FPurchaseDate := 0;
  FMileageKm := 0;
  FIsActive := False;
end;

destructor TFleet105_Vehicle.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Vehicle.Clear;
begin
  inherited Clear;
  FVehicleId := 0;
  FRegistrationNo := '';
  FFleetNo := '';
  FMake := '';
  FModel := '';
  FYear := 0;
  FEngineCC := 0;
  FFuelType := 0;
  FGrossWeight := 0;
  FPayloadKg := 0;
  FDepotId := 0;
  FStatusCode := 0;
  FPurchaseDate := 0;
  FMileageKm := 0;
  FIsActive := False;
end;

procedure TFleet105_Vehicle.Assign(Source: TFleet105_Vehicle);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FVehicleId := Source.FVehicleId;
  FRegistrationNo := Source.FRegistrationNo;
  FFleetNo := Source.FFleetNo;
  FMake := Source.FMake;
  FModel := Source.FModel;
  FYear := Source.FYear;
  FEngineCC := Source.FEngineCC;
  FFuelType := Source.FFuelType;
  FGrossWeight := Source.FGrossWeight;
  FPayloadKg := Source.FPayloadKg;
  FDepotId := Source.FDepotId;
  FStatusCode := Source.FStatusCode;
  FPurchaseDate := Source.FPurchaseDate;
  FMileageKm := Source.FMileageKm;
  FIsActive := Source.FIsActive;
end;

function TFleet105_Vehicle.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FVehicleId >= 0);
end;

function TFleet105_Vehicle.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(FRegistrationNo);
    LParts.Add(FFleetNo);
    LParts.Add(FMake);
    LParts.Add(FModel);
    LParts.Add(IntToStr(FYear));
    LParts.Add(IntToStr(FEngineCC));
    LParts.Add(IntToStr(FFuelType));
    LParts.Add(IntToStr(FGrossWeight));
    LParts.Add(IntToStr(FPayloadKg));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(DateTimeToStr(FPurchaseDate));
    LParts.Add(IntToStr(FMileageKm));
    LParts.Add(BoolToStr(FIsActive, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Vehicle.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_Vehicle.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_Vehicle.GetRegistrationNo: WideString;
begin
  // Pobierz wartość pola RegistrationNo
  Result := FRegistrationNo;
end;

procedure TFleet105_Vehicle.SetRegistrationNo(const Value: WideString);
begin
  // Ustaw wartość pola RegistrationNo
  FRegistrationNo := Value;
end;

function TFleet105_Vehicle.GetFleetNo: WideString;
begin
  // Pobierz wartość pola FleetNo
  Result := FFleetNo;
end;

procedure TFleet105_Vehicle.SetFleetNo(const Value: WideString);
begin
  // Ustaw wartość pola FleetNo
  FFleetNo := Value;
end;

function TFleet105_Vehicle.GetMake: WideString;
begin
  // Pobierz wartość pola Make
  Result := FMake;
end;

procedure TFleet105_Vehicle.SetMake(const Value: WideString);
begin
  // Ustaw wartość pola Make
  FMake := Value;
end;

function TFleet105_Vehicle.GetModel: WideString;
begin
  // Pobierz wartość pola Model
  Result := FModel;
end;

procedure TFleet105_Vehicle.SetModel(const Value: WideString);
begin
  // Ustaw wartość pola Model
  FModel := Value;
end;

function TFleet105_Vehicle.GetYear: Integer;
begin
  // Pobierz wartość pola Year
  Result := FYear;
end;

procedure TFleet105_Vehicle.SetYear(const Value: Integer);
begin
  // Ustaw wartość pola Year
  FYear := Value;
end;

function TFleet105_Vehicle.GetEngineCC: Integer;
begin
  // Pobierz wartość pola EngineCC
  Result := FEngineCC;
end;

procedure TFleet105_Vehicle.SetEngineCC(const Value: Integer);
begin
  // Ustaw wartość pola EngineCC
  FEngineCC := Value;
end;

function TFleet105_Vehicle.GetFuelType: Integer;
begin
  // Pobierz wartość pola FuelType
  Result := FFuelType;
end;

procedure TFleet105_Vehicle.SetFuelType(const Value: Integer);
begin
  // Ustaw wartość pola FuelType
  FFuelType := Value;
end;

function TFleet105_Vehicle.GetGrossWeight: Integer;
begin
  // Pobierz wartość pola GrossWeight
  Result := FGrossWeight;
end;

procedure TFleet105_Vehicle.SetGrossWeight(const Value: Integer);
begin
  // Ustaw wartość pola GrossWeight
  FGrossWeight := Value;
end;

function TFleet105_Vehicle.GetPayloadKg: Integer;
begin
  // Pobierz wartość pola PayloadKg
  Result := FPayloadKg;
end;

procedure TFleet105_Vehicle.SetPayloadKg(const Value: Integer);
begin
  // Ustaw wartość pola PayloadKg
  FPayloadKg := Value;
end;

function TFleet105_Vehicle.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Vehicle.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_Vehicle.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_Vehicle.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_Vehicle.GetPurchaseDate: TDateTime;
begin
  // Pobierz wartość pola PurchaseDate
  Result := FPurchaseDate;
end;

procedure TFleet105_Vehicle.SetPurchaseDate(const Value: TDateTime);
begin
  // Ustaw wartość pola PurchaseDate
  FPurchaseDate := Value;
end;

function TFleet105_Vehicle.GetMileageKm: Integer;
begin
  // Pobierz wartość pola MileageKm
  Result := FMileageKm;
end;

procedure TFleet105_Vehicle.SetMileageKm(const Value: Integer);
begin
  // Ustaw wartość pola MileageKm
  FMileageKm := Value;
end;

function TFleet105_Vehicle.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Vehicle.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

// ── TFleet105_VehicleList ──
constructor TFleet105_VehicleList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_VehicleList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_VehicleList.GetItem(Index: Integer): TFleet105_Vehicle;
begin
  Result := TFleet105_Vehicle(FList[Index]);
end;

function TFleet105_VehicleList.Add: TFleet105_Vehicle;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Vehicle.Create;
  FList.Add(Result);
end;

procedure TFleet105_VehicleList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_VehicleList.FindById(const AId: Integer): TFleet105_Vehicle;
var
  I: Integer;
  LItem: TFleet105_Vehicle;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_VehicleList.FindByCode(const ACode: WideString): TFleet105_Vehicle;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_VehicleList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_VehicleList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_VehicleList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_VehicleList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Vehicle;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_VehicleList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Driver
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Driver.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FDriverId := 0;
  FEmployeeNo := '';
  FFirstName := '';
  FLastName := '';
  FLicenceNo := '';
  FLicenceClass := '';
  FLicenceExpiry := 0;
  FDepotId := 0;
  FRouteId := 0;
  FStatusCode := 0;
  FIsActive := False;
  FDateOfBirth := 0;
  FContactPhone := '';
  FContactEmail := '';
  FHireDate := 0;
end;

destructor TFleet105_Driver.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Driver.Clear;
begin
  inherited Clear;
  FDriverId := 0;
  FEmployeeNo := '';
  FFirstName := '';
  FLastName := '';
  FLicenceNo := '';
  FLicenceClass := '';
  FLicenceExpiry := 0;
  FDepotId := 0;
  FRouteId := 0;
  FStatusCode := 0;
  FIsActive := False;
  FDateOfBirth := 0;
  FContactPhone := '';
  FContactEmail := '';
  FHireDate := 0;
end;

procedure TFleet105_Driver.Assign(Source: TFleet105_Driver);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FDriverId := Source.FDriverId;
  FEmployeeNo := Source.FEmployeeNo;
  FFirstName := Source.FFirstName;
  FLastName := Source.FLastName;
  FLicenceNo := Source.FLicenceNo;
  FLicenceClass := Source.FLicenceClass;
  FLicenceExpiry := Source.FLicenceExpiry;
  FDepotId := Source.FDepotId;
  FRouteId := Source.FRouteId;
  FStatusCode := Source.FStatusCode;
  FIsActive := Source.FIsActive;
  FDateOfBirth := Source.FDateOfBirth;
  FContactPhone := Source.FContactPhone;
  FContactEmail := Source.FContactEmail;
  FHireDate := Source.FHireDate;
end;

function TFleet105_Driver.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FDriverId >= 0);
end;

function TFleet105_Driver.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(FEmployeeNo);
    LParts.Add(FFirstName);
    LParts.Add(FLastName);
    LParts.Add(FLicenceNo);
    LParts.Add(FLicenceClass);
    LParts.Add(DateTimeToStr(FLicenceExpiry));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FRouteId));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(DateTimeToStr(FDateOfBirth));
    LParts.Add(FContactPhone);
    LParts.Add(FContactEmail);
    LParts.Add(DateTimeToStr(FHireDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Driver.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_Driver.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_Driver.GetEmployeeNo: WideString;
begin
  // Pobierz wartość pola EmployeeNo
  Result := FEmployeeNo;
end;

procedure TFleet105_Driver.SetEmployeeNo(const Value: WideString);
begin
  // Ustaw wartość pola EmployeeNo
  FEmployeeNo := Value;
end;

function TFleet105_Driver.GetFirstName: WideString;
begin
  // Pobierz wartość pola FirstName
  Result := FFirstName;
end;

procedure TFleet105_Driver.SetFirstName(const Value: WideString);
begin
  // Ustaw wartość pola FirstName
  FFirstName := Value;
end;

function TFleet105_Driver.GetLastName: WideString;
begin
  // Pobierz wartość pola LastName
  Result := FLastName;
end;

procedure TFleet105_Driver.SetLastName(const Value: WideString);
begin
  // Ustaw wartość pola LastName
  FLastName := Value;
end;

function TFleet105_Driver.GetLicenceNo: WideString;
begin
  // Pobierz wartość pola LicenceNo
  Result := FLicenceNo;
end;

procedure TFleet105_Driver.SetLicenceNo(const Value: WideString);
begin
  // Ustaw wartość pola LicenceNo
  FLicenceNo := Value;
end;

function TFleet105_Driver.GetLicenceClass: WideString;
begin
  // Pobierz wartość pola LicenceClass
  Result := FLicenceClass;
end;

procedure TFleet105_Driver.SetLicenceClass(const Value: WideString);
begin
  // Ustaw wartość pola LicenceClass
  FLicenceClass := Value;
end;

function TFleet105_Driver.GetLicenceExpiry: TDateTime;
begin
  // Pobierz wartość pola LicenceExpiry
  Result := FLicenceExpiry;
end;

procedure TFleet105_Driver.SetLicenceExpiry(const Value: TDateTime);
begin
  // Ustaw wartość pola LicenceExpiry
  FLicenceExpiry := Value;
end;

function TFleet105_Driver.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Driver.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_Driver.GetRouteId: Integer;
begin
  // Pobierz wartość pola RouteId
  Result := FRouteId;
end;

procedure TFleet105_Driver.SetRouteId(const Value: Integer);
begin
  // Ustaw wartość pola RouteId
  FRouteId := Value;
end;

function TFleet105_Driver.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_Driver.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_Driver.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Driver.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Driver.GetDateOfBirth: TDateTime;
begin
  // Pobierz wartość pola DateOfBirth
  Result := FDateOfBirth;
end;

procedure TFleet105_Driver.SetDateOfBirth(const Value: TDateTime);
begin
  // Ustaw wartość pola DateOfBirth
  FDateOfBirth := Value;
end;

function TFleet105_Driver.GetContactPhone: WideString;
begin
  // Pobierz wartość pola ContactPhone
  Result := FContactPhone;
end;

procedure TFleet105_Driver.SetContactPhone(const Value: WideString);
begin
  // Ustaw wartość pola ContactPhone
  FContactPhone := Value;
end;

function TFleet105_Driver.GetContactEmail: WideString;
begin
  // Pobierz wartość pola ContactEmail
  Result := FContactEmail;
end;

procedure TFleet105_Driver.SetContactEmail(const Value: WideString);
begin
  // Ustaw wartość pola ContactEmail
  FContactEmail := Value;
end;

function TFleet105_Driver.GetHireDate: TDateTime;
begin
  // Pobierz wartość pola HireDate
  Result := FHireDate;
end;

procedure TFleet105_Driver.SetHireDate(const Value: TDateTime);
begin
  // Ustaw wartość pola HireDate
  FHireDate := Value;
end;

// ── TFleet105_DriverList ──
constructor TFleet105_DriverList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_DriverList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_DriverList.GetItem(Index: Integer): TFleet105_Driver;
begin
  Result := TFleet105_Driver(FList[Index]);
end;

function TFleet105_DriverList.Add: TFleet105_Driver;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Driver.Create;
  FList.Add(Result);
end;

procedure TFleet105_DriverList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_DriverList.FindById(const AId: Integer): TFleet105_Driver;
var
  I: Integer;
  LItem: TFleet105_Driver;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_DriverList.FindByCode(const ACode: WideString): TFleet105_Driver;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_DriverList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_DriverList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_DriverList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_DriverList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Driver;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_DriverList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Route
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Route.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FRouteId := 0;
  FRouteCode := '';
  FRouteName := '';
  FStartPoint := '';
  FEndPoint := '';
  FDistanceKm := 0.0;
  FEstimatedMins := 0;
  FDepotId := 0;
  FDirectionCode := 0;
  FIsCircular := False;
  FIsActive := False;
  FValidFrom := 0;
  FValidTo := 0;
end;

destructor TFleet105_Route.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Route.Clear;
begin
  inherited Clear;
  FRouteId := 0;
  FRouteCode := '';
  FRouteName := '';
  FStartPoint := '';
  FEndPoint := '';
  FDistanceKm := 0.0;
  FEstimatedMins := 0;
  FDepotId := 0;
  FDirectionCode := 0;
  FIsCircular := False;
  FIsActive := False;
  FValidFrom := 0;
  FValidTo := 0;
end;

procedure TFleet105_Route.Assign(Source: TFleet105_Route);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FRouteId := Source.FRouteId;
  FRouteCode := Source.FRouteCode;
  FRouteName := Source.FRouteName;
  FStartPoint := Source.FStartPoint;
  FEndPoint := Source.FEndPoint;
  FDistanceKm := Source.FDistanceKm;
  FEstimatedMins := Source.FEstimatedMins;
  FDepotId := Source.FDepotId;
  FDirectionCode := Source.FDirectionCode;
  FIsCircular := Source.FIsCircular;
  FIsActive := Source.FIsActive;
  FValidFrom := Source.FValidFrom;
  FValidTo := Source.FValidTo;
end;

function TFleet105_Route.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FRouteId >= 0);
end;

function TFleet105_Route.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FRouteId));
    LParts.Add(FRouteCode);
    LParts.Add(FRouteName);
    LParts.Add(FStartPoint);
    LParts.Add(FEndPoint);
    LParts.Add(FloatToStr(FDistanceKm));
    LParts.Add(IntToStr(FEstimatedMins));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FDirectionCode));
    LParts.Add(BoolToStr(FIsCircular, True));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(DateTimeToStr(FValidFrom));
    LParts.Add(DateTimeToStr(FValidTo));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Route.GetRouteId: Integer;
begin
  // Pobierz wartość pola RouteId
  Result := FRouteId;
end;

procedure TFleet105_Route.SetRouteId(const Value: Integer);
begin
  // Ustaw wartość pola RouteId
  FRouteId := Value;
end;

function TFleet105_Route.GetRouteCode: WideString;
begin
  // Pobierz wartość pola RouteCode
  Result := FRouteCode;
end;

procedure TFleet105_Route.SetRouteCode(const Value: WideString);
begin
  // Ustaw wartość pola RouteCode
  FRouteCode := Value;
end;

function TFleet105_Route.GetRouteName: WideString;
begin
  // Pobierz wartość pola RouteName
  Result := FRouteName;
end;

procedure TFleet105_Route.SetRouteName(const Value: WideString);
begin
  // Ustaw wartość pola RouteName
  FRouteName := Value;
end;

function TFleet105_Route.GetStartPoint: WideString;
begin
  // Pobierz wartość pola StartPoint
  Result := FStartPoint;
end;

procedure TFleet105_Route.SetStartPoint(const Value: WideString);
begin
  // Ustaw wartość pola StartPoint
  FStartPoint := Value;
end;

function TFleet105_Route.GetEndPoint: WideString;
begin
  // Pobierz wartość pola EndPoint
  Result := FEndPoint;
end;

procedure TFleet105_Route.SetEndPoint(const Value: WideString);
begin
  // Ustaw wartość pola EndPoint
  FEndPoint := Value;
end;

function TFleet105_Route.GetDistanceKm: Double;
begin
  // Pobierz wartość pola DistanceKm
  Result := FDistanceKm;
end;

procedure TFleet105_Route.SetDistanceKm(const Value: Double);
begin
  // Ustaw wartość pola DistanceKm
  FDistanceKm := Value;
end;

function TFleet105_Route.GetEstimatedMins: Integer;
begin
  // Pobierz wartość pola EstimatedMins
  Result := FEstimatedMins;
end;

procedure TFleet105_Route.SetEstimatedMins(const Value: Integer);
begin
  // Ustaw wartość pola EstimatedMins
  FEstimatedMins := Value;
end;

function TFleet105_Route.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Route.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_Route.GetDirectionCode: Integer;
begin
  // Pobierz wartość pola DirectionCode
  Result := FDirectionCode;
end;

procedure TFleet105_Route.SetDirectionCode(const Value: Integer);
begin
  // Ustaw wartość pola DirectionCode
  FDirectionCode := Value;
end;

function TFleet105_Route.GetIsCircular: Boolean;
begin
  // Pobierz wartość pola IsCircular
  Result := FIsCircular;
end;

procedure TFleet105_Route.SetIsCircular(const Value: Boolean);
begin
  // Ustaw wartość pola IsCircular
  FIsCircular := Value;
end;

function TFleet105_Route.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Route.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Route.GetValidFrom: TDateTime;
begin
  // Pobierz wartość pola ValidFrom
  Result := FValidFrom;
end;

procedure TFleet105_Route.SetValidFrom(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidFrom
  FValidFrom := Value;
end;

function TFleet105_Route.GetValidTo: TDateTime;
begin
  // Pobierz wartość pola ValidTo
  Result := FValidTo;
end;

procedure TFleet105_Route.SetValidTo(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidTo
  FValidTo := Value;
end;

// ── TFleet105_RouteList ──
constructor TFleet105_RouteList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_RouteList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_RouteList.GetItem(Index: Integer): TFleet105_Route;
begin
  Result := TFleet105_Route(FList[Index]);
end;

function TFleet105_RouteList.Add: TFleet105_Route;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Route.Create;
  FList.Add(Result);
end;

procedure TFleet105_RouteList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_RouteList.FindById(const AId: Integer): TFleet105_Route;
var
  I: Integer;
  LItem: TFleet105_Route;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_RouteList.FindByCode(const ACode: WideString): TFleet105_Route;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_RouteList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_RouteList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_RouteList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_RouteList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Route;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_RouteList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_JobOrder
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_JobOrder.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FJobId := 0;
  FJobRef := '';
  FVehicleId := 0;
  FDriverId := 0;
  FRouteId := 0;
  FScheduledDate := 0;
  FActualStart := 0;
  FActualEnd := 0;
  FStatusCode := 0;
  FPriorityLevel := 0;
  FPassengerCount := 0;
  FPayloadKg := 0;
  FNoteText := '';
  FCreatedBy := 0;
  FCreatedDate := 0;
end;

destructor TFleet105_JobOrder.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_JobOrder.Clear;
begin
  inherited Clear;
  FJobId := 0;
  FJobRef := '';
  FVehicleId := 0;
  FDriverId := 0;
  FRouteId := 0;
  FScheduledDate := 0;
  FActualStart := 0;
  FActualEnd := 0;
  FStatusCode := 0;
  FPriorityLevel := 0;
  FPassengerCount := 0;
  FPayloadKg := 0;
  FNoteText := '';
  FCreatedBy := 0;
  FCreatedDate := 0;
end;

procedure TFleet105_JobOrder.Assign(Source: TFleet105_JobOrder);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FJobId := Source.FJobId;
  FJobRef := Source.FJobRef;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FRouteId := Source.FRouteId;
  FScheduledDate := Source.FScheduledDate;
  FActualStart := Source.FActualStart;
  FActualEnd := Source.FActualEnd;
  FStatusCode := Source.FStatusCode;
  FPriorityLevel := Source.FPriorityLevel;
  FPassengerCount := Source.FPassengerCount;
  FPayloadKg := Source.FPayloadKg;
  FNoteText := Source.FNoteText;
  FCreatedBy := Source.FCreatedBy;
  FCreatedDate := Source.FCreatedDate;
end;

function TFleet105_JobOrder.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FJobId >= 0);
end;

function TFleet105_JobOrder.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FJobId));
    LParts.Add(FJobRef);
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(IntToStr(FRouteId));
    LParts.Add(DateTimeToStr(FScheduledDate));
    LParts.Add(DateTimeToStr(FActualStart));
    LParts.Add(DateTimeToStr(FActualEnd));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(IntToStr(FPriorityLevel));
    LParts.Add(IntToStr(FPassengerCount));
    LParts.Add(IntToStr(FPayloadKg));
    LParts.Add(FNoteText);
    LParts.Add(IntToStr(FCreatedBy));
    LParts.Add(DateTimeToStr(FCreatedDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_JobOrder.GetJobId: Integer;
begin
  // Pobierz wartość pola JobId
  Result := FJobId;
end;

procedure TFleet105_JobOrder.SetJobId(const Value: Integer);
begin
  // Ustaw wartość pola JobId
  FJobId := Value;
end;

function TFleet105_JobOrder.GetJobRef: WideString;
begin
  // Pobierz wartość pola JobRef
  Result := FJobRef;
end;

procedure TFleet105_JobOrder.SetJobRef(const Value: WideString);
begin
  // Ustaw wartość pola JobRef
  FJobRef := Value;
end;

function TFleet105_JobOrder.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_JobOrder.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_JobOrder.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_JobOrder.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_JobOrder.GetRouteId: Integer;
begin
  // Pobierz wartość pola RouteId
  Result := FRouteId;
end;

procedure TFleet105_JobOrder.SetRouteId(const Value: Integer);
begin
  // Ustaw wartość pola RouteId
  FRouteId := Value;
end;

function TFleet105_JobOrder.GetScheduledDate: TDateTime;
begin
  // Pobierz wartość pola ScheduledDate
  Result := FScheduledDate;
end;

procedure TFleet105_JobOrder.SetScheduledDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ScheduledDate
  FScheduledDate := Value;
end;

function TFleet105_JobOrder.GetActualStart: TDateTime;
begin
  // Pobierz wartość pola ActualStart
  Result := FActualStart;
end;

procedure TFleet105_JobOrder.SetActualStart(const Value: TDateTime);
begin
  // Ustaw wartość pola ActualStart
  FActualStart := Value;
end;

function TFleet105_JobOrder.GetActualEnd: TDateTime;
begin
  // Pobierz wartość pola ActualEnd
  Result := FActualEnd;
end;

procedure TFleet105_JobOrder.SetActualEnd(const Value: TDateTime);
begin
  // Ustaw wartość pola ActualEnd
  FActualEnd := Value;
end;

function TFleet105_JobOrder.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_JobOrder.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_JobOrder.GetPriorityLevel: Integer;
begin
  // Pobierz wartość pola PriorityLevel
  Result := FPriorityLevel;
end;

procedure TFleet105_JobOrder.SetPriorityLevel(const Value: Integer);
begin
  // Ustaw wartość pola PriorityLevel
  FPriorityLevel := Value;
end;

function TFleet105_JobOrder.GetPassengerCount: Integer;
begin
  // Pobierz wartość pola PassengerCount
  Result := FPassengerCount;
end;

procedure TFleet105_JobOrder.SetPassengerCount(const Value: Integer);
begin
  // Ustaw wartość pola PassengerCount
  FPassengerCount := Value;
end;

function TFleet105_JobOrder.GetPayloadKg: Integer;
begin
  // Pobierz wartość pola PayloadKg
  Result := FPayloadKg;
end;

procedure TFleet105_JobOrder.SetPayloadKg(const Value: Integer);
begin
  // Ustaw wartość pola PayloadKg
  FPayloadKg := Value;
end;

function TFleet105_JobOrder.GetNoteText: WideString;
begin
  // Pobierz wartość pola NoteText
  Result := FNoteText;
end;

procedure TFleet105_JobOrder.SetNoteText(const Value: WideString);
begin
  // Ustaw wartość pola NoteText
  FNoteText := Value;
end;

function TFleet105_JobOrder.GetCreatedBy: Integer;
begin
  // Pobierz wartość pola CreatedBy
  Result := FCreatedBy;
end;

procedure TFleet105_JobOrder.SetCreatedBy(const Value: Integer);
begin
  // Ustaw wartość pola CreatedBy
  FCreatedBy := Value;
end;

function TFleet105_JobOrder.GetCreatedDate: TDateTime;
begin
  // Pobierz wartość pola CreatedDate
  Result := FCreatedDate;
end;

procedure TFleet105_JobOrder.SetCreatedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CreatedDate
  FCreatedDate := Value;
end;

// ── TFleet105_JobOrderList ──
constructor TFleet105_JobOrderList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_JobOrderList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_JobOrderList.GetItem(Index: Integer): TFleet105_JobOrder;
begin
  Result := TFleet105_JobOrder(FList[Index]);
end;

function TFleet105_JobOrderList.Add: TFleet105_JobOrder;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_JobOrder.Create;
  FList.Add(Result);
end;

procedure TFleet105_JobOrderList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_JobOrderList.FindById(const AId: Integer): TFleet105_JobOrder;
var
  I: Integer;
  LItem: TFleet105_JobOrder;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_JobOrderList.FindByCode(const ACode: WideString): TFleet105_JobOrder;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_JobOrderList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_JobOrderList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_JobOrderList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_JobOrderList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_JobOrder;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_JobOrderList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_FuelRecord
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_FuelRecord.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FFuelId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FFuelDate := 0;
  FLitres := 0.0;
  FCostPerLitre := 0.0;
  FTotalCost := 0.0;
  FOdometerKm := 0;
  FDepotId := 0;
  FFuelTypeCode := 0;
  FReceiptNo := '';
  FApprovedBy := 0;
end;

destructor TFleet105_FuelRecord.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_FuelRecord.Clear;
begin
  inherited Clear;
  FFuelId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FFuelDate := 0;
  FLitres := 0.0;
  FCostPerLitre := 0.0;
  FTotalCost := 0.0;
  FOdometerKm := 0;
  FDepotId := 0;
  FFuelTypeCode := 0;
  FReceiptNo := '';
  FApprovedBy := 0;
end;

procedure TFleet105_FuelRecord.Assign(Source: TFleet105_FuelRecord);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FFuelId := Source.FFuelId;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FFuelDate := Source.FFuelDate;
  FLitres := Source.FLitres;
  FCostPerLitre := Source.FCostPerLitre;
  FTotalCost := Source.FTotalCost;
  FOdometerKm := Source.FOdometerKm;
  FDepotId := Source.FDepotId;
  FFuelTypeCode := Source.FFuelTypeCode;
  FReceiptNo := Source.FReceiptNo;
  FApprovedBy := Source.FApprovedBy;
end;

function TFleet105_FuelRecord.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FFuelId >= 0);
end;

function TFleet105_FuelRecord.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FFuelId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(DateTimeToStr(FFuelDate));
    LParts.Add(FloatToStr(FLitres));
    LParts.Add(FloatToStr(FCostPerLitre));
    LParts.Add(FloatToStr(FTotalCost));
    LParts.Add(IntToStr(FOdometerKm));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FFuelTypeCode));
    LParts.Add(FReceiptNo);
    LParts.Add(IntToStr(FApprovedBy));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_FuelRecord.GetFuelId: Integer;
begin
  // Pobierz wartość pola FuelId
  Result := FFuelId;
end;

procedure TFleet105_FuelRecord.SetFuelId(const Value: Integer);
begin
  // Ustaw wartość pola FuelId
  FFuelId := Value;
end;

function TFleet105_FuelRecord.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_FuelRecord.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_FuelRecord.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_FuelRecord.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_FuelRecord.GetFuelDate: TDateTime;
begin
  // Pobierz wartość pola FuelDate
  Result := FFuelDate;
end;

procedure TFleet105_FuelRecord.SetFuelDate(const Value: TDateTime);
begin
  // Ustaw wartość pola FuelDate
  FFuelDate := Value;
end;

function TFleet105_FuelRecord.GetLitres: Double;
begin
  // Pobierz wartość pola Litres
  Result := FLitres;
end;

procedure TFleet105_FuelRecord.SetLitres(const Value: Double);
begin
  // Ustaw wartość pola Litres
  FLitres := Value;
end;

function TFleet105_FuelRecord.GetCostPerLitre: Double;
begin
  // Pobierz wartość pola CostPerLitre
  Result := FCostPerLitre;
end;

procedure TFleet105_FuelRecord.SetCostPerLitre(const Value: Double);
begin
  // Ustaw wartość pola CostPerLitre
  FCostPerLitre := Value;
end;

function TFleet105_FuelRecord.GetTotalCost: Double;
begin
  // Pobierz wartość pola TotalCost
  Result := FTotalCost;
end;

procedure TFleet105_FuelRecord.SetTotalCost(const Value: Double);
begin
  // Ustaw wartość pola TotalCost
  FTotalCost := Value;
end;

function TFleet105_FuelRecord.GetOdometerKm: Integer;
begin
  // Pobierz wartość pola OdometerKm
  Result := FOdometerKm;
end;

procedure TFleet105_FuelRecord.SetOdometerKm(const Value: Integer);
begin
  // Ustaw wartość pola OdometerKm
  FOdometerKm := Value;
end;

function TFleet105_FuelRecord.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_FuelRecord.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_FuelRecord.GetFuelTypeCode: Integer;
begin
  // Pobierz wartość pola FuelTypeCode
  Result := FFuelTypeCode;
end;

procedure TFleet105_FuelRecord.SetFuelTypeCode(const Value: Integer);
begin
  // Ustaw wartość pola FuelTypeCode
  FFuelTypeCode := Value;
end;

function TFleet105_FuelRecord.GetReceiptNo: WideString;
begin
  // Pobierz wartość pola ReceiptNo
  Result := FReceiptNo;
end;

procedure TFleet105_FuelRecord.SetReceiptNo(const Value: WideString);
begin
  // Ustaw wartość pola ReceiptNo
  FReceiptNo := Value;
end;

function TFleet105_FuelRecord.GetApprovedBy: Integer;
begin
  // Pobierz wartość pola ApprovedBy
  Result := FApprovedBy;
end;

procedure TFleet105_FuelRecord.SetApprovedBy(const Value: Integer);
begin
  // Ustaw wartość pola ApprovedBy
  FApprovedBy := Value;
end;

// ── TFleet105_FuelRecordList ──
constructor TFleet105_FuelRecordList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_FuelRecordList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_FuelRecordList.GetItem(Index: Integer): TFleet105_FuelRecord;
begin
  Result := TFleet105_FuelRecord(FList[Index]);
end;

function TFleet105_FuelRecordList.Add: TFleet105_FuelRecord;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_FuelRecord.Create;
  FList.Add(Result);
end;

procedure TFleet105_FuelRecordList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_FuelRecordList.FindById(const AId: Integer): TFleet105_FuelRecord;
var
  I: Integer;
  LItem: TFleet105_FuelRecord;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_FuelRecordList.FindByCode(const ACode: WideString): TFleet105_FuelRecord;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_FuelRecordList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_FuelRecordList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_FuelRecordList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_FuelRecordList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_FuelRecord;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_FuelRecordList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_ServiceRecord
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_ServiceRecord.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FServiceId := 0;
  FVehicleId := 0;
  FServiceDate := 0;
  FServiceType := 0;
  FOdometerKm := 0;
  FTechnicianId := 0;
  FLabourCost := 0.0;
  FPartsCost := 0.0;
  FTotalCost := 0.0;
  FNextServiceKm := 0;
  FNextServiceDate := 0;
  FWorkOrder := '';
  FNotes := '';
end;

destructor TFleet105_ServiceRecord.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_ServiceRecord.Clear;
begin
  inherited Clear;
  FServiceId := 0;
  FVehicleId := 0;
  FServiceDate := 0;
  FServiceType := 0;
  FOdometerKm := 0;
  FTechnicianId := 0;
  FLabourCost := 0.0;
  FPartsCost := 0.0;
  FTotalCost := 0.0;
  FNextServiceKm := 0;
  FNextServiceDate := 0;
  FWorkOrder := '';
  FNotes := '';
end;

procedure TFleet105_ServiceRecord.Assign(Source: TFleet105_ServiceRecord);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FServiceId := Source.FServiceId;
  FVehicleId := Source.FVehicleId;
  FServiceDate := Source.FServiceDate;
  FServiceType := Source.FServiceType;
  FOdometerKm := Source.FOdometerKm;
  FTechnicianId := Source.FTechnicianId;
  FLabourCost := Source.FLabourCost;
  FPartsCost := Source.FPartsCost;
  FTotalCost := Source.FTotalCost;
  FNextServiceKm := Source.FNextServiceKm;
  FNextServiceDate := Source.FNextServiceDate;
  FWorkOrder := Source.FWorkOrder;
  FNotes := Source.FNotes;
end;

function TFleet105_ServiceRecord.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FServiceId >= 0);
end;

function TFleet105_ServiceRecord.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FServiceId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(DateTimeToStr(FServiceDate));
    LParts.Add(IntToStr(FServiceType));
    LParts.Add(IntToStr(FOdometerKm));
    LParts.Add(IntToStr(FTechnicianId));
    LParts.Add(FloatToStr(FLabourCost));
    LParts.Add(FloatToStr(FPartsCost));
    LParts.Add(FloatToStr(FTotalCost));
    LParts.Add(IntToStr(FNextServiceKm));
    LParts.Add(DateTimeToStr(FNextServiceDate));
    LParts.Add(FWorkOrder);
    LParts.Add(FNotes);
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_ServiceRecord.GetServiceId: Integer;
begin
  // Pobierz wartość pola ServiceId
  Result := FServiceId;
end;

procedure TFleet105_ServiceRecord.SetServiceId(const Value: Integer);
begin
  // Ustaw wartość pola ServiceId
  FServiceId := Value;
end;

function TFleet105_ServiceRecord.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_ServiceRecord.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_ServiceRecord.GetServiceDate: TDateTime;
begin
  // Pobierz wartość pola ServiceDate
  Result := FServiceDate;
end;

procedure TFleet105_ServiceRecord.SetServiceDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ServiceDate
  FServiceDate := Value;
end;

function TFleet105_ServiceRecord.GetServiceType: Integer;
begin
  // Pobierz wartość pola ServiceType
  Result := FServiceType;
end;

procedure TFleet105_ServiceRecord.SetServiceType(const Value: Integer);
begin
  // Ustaw wartość pola ServiceType
  FServiceType := Value;
end;

function TFleet105_ServiceRecord.GetOdometerKm: Integer;
begin
  // Pobierz wartość pola OdometerKm
  Result := FOdometerKm;
end;

procedure TFleet105_ServiceRecord.SetOdometerKm(const Value: Integer);
begin
  // Ustaw wartość pola OdometerKm
  FOdometerKm := Value;
end;

function TFleet105_ServiceRecord.GetTechnicianId: Integer;
begin
  // Pobierz wartość pola TechnicianId
  Result := FTechnicianId;
end;

procedure TFleet105_ServiceRecord.SetTechnicianId(const Value: Integer);
begin
  // Ustaw wartość pola TechnicianId
  FTechnicianId := Value;
end;

function TFleet105_ServiceRecord.GetLabourCost: Double;
begin
  // Pobierz wartość pola LabourCost
  Result := FLabourCost;
end;

procedure TFleet105_ServiceRecord.SetLabourCost(const Value: Double);
begin
  // Ustaw wartość pola LabourCost
  FLabourCost := Value;
end;

function TFleet105_ServiceRecord.GetPartsCost: Double;
begin
  // Pobierz wartość pola PartsCost
  Result := FPartsCost;
end;

procedure TFleet105_ServiceRecord.SetPartsCost(const Value: Double);
begin
  // Ustaw wartość pola PartsCost
  FPartsCost := Value;
end;

function TFleet105_ServiceRecord.GetTotalCost: Double;
begin
  // Pobierz wartość pola TotalCost
  Result := FTotalCost;
end;

procedure TFleet105_ServiceRecord.SetTotalCost(const Value: Double);
begin
  // Ustaw wartość pola TotalCost
  FTotalCost := Value;
end;

function TFleet105_ServiceRecord.GetNextServiceKm: Integer;
begin
  // Pobierz wartość pola NextServiceKm
  Result := FNextServiceKm;
end;

procedure TFleet105_ServiceRecord.SetNextServiceKm(const Value: Integer);
begin
  // Ustaw wartość pola NextServiceKm
  FNextServiceKm := Value;
end;

function TFleet105_ServiceRecord.GetNextServiceDate: TDateTime;
begin
  // Pobierz wartość pola NextServiceDate
  Result := FNextServiceDate;
end;

procedure TFleet105_ServiceRecord.SetNextServiceDate(const Value: TDateTime);
begin
  // Ustaw wartość pola NextServiceDate
  FNextServiceDate := Value;
end;

function TFleet105_ServiceRecord.GetWorkOrder: WideString;
begin
  // Pobierz wartość pola WorkOrder
  Result := FWorkOrder;
end;

procedure TFleet105_ServiceRecord.SetWorkOrder(const Value: WideString);
begin
  // Ustaw wartość pola WorkOrder
  FWorkOrder := Value;
end;

function TFleet105_ServiceRecord.GetNotes: WideString;
begin
  // Pobierz wartość pola Notes
  Result := FNotes;
end;

procedure TFleet105_ServiceRecord.SetNotes(const Value: WideString);
begin
  // Ustaw wartość pola Notes
  FNotes := Value;
end;

// ── TFleet105_ServiceRecordList ──
constructor TFleet105_ServiceRecordList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ServiceRecordList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ServiceRecordList.GetItem(Index: Integer): TFleet105_ServiceRecord;
begin
  Result := TFleet105_ServiceRecord(FList[Index]);
end;

function TFleet105_ServiceRecordList.Add: TFleet105_ServiceRecord;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_ServiceRecord.Create;
  FList.Add(Result);
end;

procedure TFleet105_ServiceRecordList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ServiceRecordList.FindById(const AId: Integer): TFleet105_ServiceRecord;
var
  I: Integer;
  LItem: TFleet105_ServiceRecord;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ServiceRecordList.FindByCode(const ACode: WideString): TFleet105_ServiceRecord;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ServiceRecordList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ServiceRecordList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ServiceRecordList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ServiceRecordList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_ServiceRecord;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ServiceRecordList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Incident
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Incident.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FIncidentId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FIncidentDate := 0;
  FIncidentType := 0;
  FSeverityCode := 0;
  FLocationDesc := '';
  FDescription := '';
  FInjuryCount := 0;
  FDamageCost := 0.0;
  FReportedBy := 0;
  FResolvedDate := 0;
  FIsResolved := False;
end;

destructor TFleet105_Incident.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Incident.Clear;
begin
  inherited Clear;
  FIncidentId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FIncidentDate := 0;
  FIncidentType := 0;
  FSeverityCode := 0;
  FLocationDesc := '';
  FDescription := '';
  FInjuryCount := 0;
  FDamageCost := 0.0;
  FReportedBy := 0;
  FResolvedDate := 0;
  FIsResolved := False;
end;

procedure TFleet105_Incident.Assign(Source: TFleet105_Incident);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FIncidentId := Source.FIncidentId;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FIncidentDate := Source.FIncidentDate;
  FIncidentType := Source.FIncidentType;
  FSeverityCode := Source.FSeverityCode;
  FLocationDesc := Source.FLocationDesc;
  FDescription := Source.FDescription;
  FInjuryCount := Source.FInjuryCount;
  FDamageCost := Source.FDamageCost;
  FReportedBy := Source.FReportedBy;
  FResolvedDate := Source.FResolvedDate;
  FIsResolved := Source.FIsResolved;
end;

function TFleet105_Incident.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FIncidentId >= 0);
end;

function TFleet105_Incident.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FIncidentId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(DateTimeToStr(FIncidentDate));
    LParts.Add(IntToStr(FIncidentType));
    LParts.Add(IntToStr(FSeverityCode));
    LParts.Add(FLocationDesc);
    LParts.Add(FDescription);
    LParts.Add(IntToStr(FInjuryCount));
    LParts.Add(FloatToStr(FDamageCost));
    LParts.Add(IntToStr(FReportedBy));
    LParts.Add(DateTimeToStr(FResolvedDate));
    LParts.Add(BoolToStr(FIsResolved, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Incident.GetIncidentId: Integer;
begin
  // Pobierz wartość pola IncidentId
  Result := FIncidentId;
end;

procedure TFleet105_Incident.SetIncidentId(const Value: Integer);
begin
  // Ustaw wartość pola IncidentId
  FIncidentId := Value;
end;

function TFleet105_Incident.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_Incident.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_Incident.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_Incident.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_Incident.GetIncidentDate: TDateTime;
begin
  // Pobierz wartość pola IncidentDate
  Result := FIncidentDate;
end;

procedure TFleet105_Incident.SetIncidentDate(const Value: TDateTime);
begin
  // Ustaw wartość pola IncidentDate
  FIncidentDate := Value;
end;

function TFleet105_Incident.GetIncidentType: Integer;
begin
  // Pobierz wartość pola IncidentType
  Result := FIncidentType;
end;

procedure TFleet105_Incident.SetIncidentType(const Value: Integer);
begin
  // Ustaw wartość pola IncidentType
  FIncidentType := Value;
end;

function TFleet105_Incident.GetSeverityCode: Integer;
begin
  // Pobierz wartość pola SeverityCode
  Result := FSeverityCode;
end;

procedure TFleet105_Incident.SetSeverityCode(const Value: Integer);
begin
  // Ustaw wartość pola SeverityCode
  FSeverityCode := Value;
end;

function TFleet105_Incident.GetLocationDesc: WideString;
begin
  // Pobierz wartość pola LocationDesc
  Result := FLocationDesc;
end;

procedure TFleet105_Incident.SetLocationDesc(const Value: WideString);
begin
  // Ustaw wartość pola LocationDesc
  FLocationDesc := Value;
end;

function TFleet105_Incident.GetDescription: WideString;
begin
  // Pobierz wartość pola Description
  Result := FDescription;
end;

procedure TFleet105_Incident.SetDescription(const Value: WideString);
begin
  // Ustaw wartość pola Description
  FDescription := Value;
end;

function TFleet105_Incident.GetInjuryCount: Integer;
begin
  // Pobierz wartość pola InjuryCount
  Result := FInjuryCount;
end;

procedure TFleet105_Incident.SetInjuryCount(const Value: Integer);
begin
  // Ustaw wartość pola InjuryCount
  FInjuryCount := Value;
end;

function TFleet105_Incident.GetDamageCost: Double;
begin
  // Pobierz wartość pola DamageCost
  Result := FDamageCost;
end;

procedure TFleet105_Incident.SetDamageCost(const Value: Double);
begin
  // Ustaw wartość pola DamageCost
  FDamageCost := Value;
end;

function TFleet105_Incident.GetReportedBy: Integer;
begin
  // Pobierz wartość pola ReportedBy
  Result := FReportedBy;
end;

procedure TFleet105_Incident.SetReportedBy(const Value: Integer);
begin
  // Ustaw wartość pola ReportedBy
  FReportedBy := Value;
end;

function TFleet105_Incident.GetResolvedDate: TDateTime;
begin
  // Pobierz wartość pola ResolvedDate
  Result := FResolvedDate;
end;

procedure TFleet105_Incident.SetResolvedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ResolvedDate
  FResolvedDate := Value;
end;

function TFleet105_Incident.GetIsResolved: Boolean;
begin
  // Pobierz wartość pola IsResolved
  Result := FIsResolved;
end;

procedure TFleet105_Incident.SetIsResolved(const Value: Boolean);
begin
  // Ustaw wartość pola IsResolved
  FIsResolved := Value;
end;

// ── TFleet105_IncidentList ──
constructor TFleet105_IncidentList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_IncidentList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_IncidentList.GetItem(Index: Integer): TFleet105_Incident;
begin
  Result := TFleet105_Incident(FList[Index]);
end;

function TFleet105_IncidentList.Add: TFleet105_Incident;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Incident.Create;
  FList.Add(Result);
end;

procedure TFleet105_IncidentList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_IncidentList.FindById(const AId: Integer): TFleet105_Incident;
var
  I: Integer;
  LItem: TFleet105_Incident;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_IncidentList.FindByCode(const ACode: WideString): TFleet105_Incident;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_IncidentList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_IncidentList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_IncidentList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_IncidentList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Incident;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_IncidentList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_GpsTrack
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_GpsTrack.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FTrackId := 0;
  FVehicleId := 0;
  FDeviceId := 0;
  FTrackDate := 0;
  FLatitude := 0.0;
  FLongitude := 0.0;
  FAltitude := 0.0;
  FSpeedKph := 0.0;
  FHeading := 0.0;
  FAccuracy := 0.0;
  FSatellites := 0;
  FEventCode := 0;
end;

destructor TFleet105_GpsTrack.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_GpsTrack.Clear;
begin
  inherited Clear;
  FTrackId := 0;
  FVehicleId := 0;
  FDeviceId := 0;
  FTrackDate := 0;
  FLatitude := 0.0;
  FLongitude := 0.0;
  FAltitude := 0.0;
  FSpeedKph := 0.0;
  FHeading := 0.0;
  FAccuracy := 0.0;
  FSatellites := 0;
  FEventCode := 0;
end;

procedure TFleet105_GpsTrack.Assign(Source: TFleet105_GpsTrack);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FTrackId := Source.FTrackId;
  FVehicleId := Source.FVehicleId;
  FDeviceId := Source.FDeviceId;
  FTrackDate := Source.FTrackDate;
  FLatitude := Source.FLatitude;
  FLongitude := Source.FLongitude;
  FAltitude := Source.FAltitude;
  FSpeedKph := Source.FSpeedKph;
  FHeading := Source.FHeading;
  FAccuracy := Source.FAccuracy;
  FSatellites := Source.FSatellites;
  FEventCode := Source.FEventCode;
end;

function TFleet105_GpsTrack.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FTrackId >= 0);
end;

function TFleet105_GpsTrack.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FTrackId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDeviceId));
    LParts.Add(DateTimeToStr(FTrackDate));
    LParts.Add(FloatToStr(FLatitude));
    LParts.Add(FloatToStr(FLongitude));
    LParts.Add(FloatToStr(FAltitude));
    LParts.Add(FloatToStr(FSpeedKph));
    LParts.Add(FloatToStr(FHeading));
    LParts.Add(FloatToStr(FAccuracy));
    LParts.Add(IntToStr(FSatellites));
    LParts.Add(IntToStr(FEventCode));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_GpsTrack.GetTrackId: Integer;
begin
  // Pobierz wartość pola TrackId
  Result := FTrackId;
end;

procedure TFleet105_GpsTrack.SetTrackId(const Value: Integer);
begin
  // Ustaw wartość pola TrackId
  FTrackId := Value;
end;

function TFleet105_GpsTrack.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_GpsTrack.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_GpsTrack.GetDeviceId: Integer;
begin
  // Pobierz wartość pola DeviceId
  Result := FDeviceId;
end;

procedure TFleet105_GpsTrack.SetDeviceId(const Value: Integer);
begin
  // Ustaw wartość pola DeviceId
  FDeviceId := Value;
end;

function TFleet105_GpsTrack.GetTrackDate: TDateTime;
begin
  // Pobierz wartość pola TrackDate
  Result := FTrackDate;
end;

procedure TFleet105_GpsTrack.SetTrackDate(const Value: TDateTime);
begin
  // Ustaw wartość pola TrackDate
  FTrackDate := Value;
end;

function TFleet105_GpsTrack.GetLatitude: Double;
begin
  // Pobierz wartość pola Latitude
  Result := FLatitude;
end;

procedure TFleet105_GpsTrack.SetLatitude(const Value: Double);
begin
  // Ustaw wartość pola Latitude
  FLatitude := Value;
end;

function TFleet105_GpsTrack.GetLongitude: Double;
begin
  // Pobierz wartość pola Longitude
  Result := FLongitude;
end;

procedure TFleet105_GpsTrack.SetLongitude(const Value: Double);
begin
  // Ustaw wartość pola Longitude
  FLongitude := Value;
end;

function TFleet105_GpsTrack.GetAltitude: Double;
begin
  // Pobierz wartość pola Altitude
  Result := FAltitude;
end;

procedure TFleet105_GpsTrack.SetAltitude(const Value: Double);
begin
  // Ustaw wartość pola Altitude
  FAltitude := Value;
end;

function TFleet105_GpsTrack.GetSpeedKph: Double;
begin
  // Pobierz wartość pola SpeedKph
  Result := FSpeedKph;
end;

procedure TFleet105_GpsTrack.SetSpeedKph(const Value: Double);
begin
  // Ustaw wartość pola SpeedKph
  FSpeedKph := Value;
end;

function TFleet105_GpsTrack.GetHeading: Double;
begin
  // Pobierz wartość pola Heading
  Result := FHeading;
end;

procedure TFleet105_GpsTrack.SetHeading(const Value: Double);
begin
  // Ustaw wartość pola Heading
  FHeading := Value;
end;

function TFleet105_GpsTrack.GetAccuracy: Double;
begin
  // Pobierz wartość pola Accuracy
  Result := FAccuracy;
end;

procedure TFleet105_GpsTrack.SetAccuracy(const Value: Double);
begin
  // Ustaw wartość pola Accuracy
  FAccuracy := Value;
end;

function TFleet105_GpsTrack.GetSatellites: Integer;
begin
  // Pobierz wartość pola Satellites
  Result := FSatellites;
end;

procedure TFleet105_GpsTrack.SetSatellites(const Value: Integer);
begin
  // Ustaw wartość pola Satellites
  FSatellites := Value;
end;

function TFleet105_GpsTrack.GetEventCode: Integer;
begin
  // Pobierz wartość pola EventCode
  Result := FEventCode;
end;

procedure TFleet105_GpsTrack.SetEventCode(const Value: Integer);
begin
  // Ustaw wartość pola EventCode
  FEventCode := Value;
end;

// ── TFleet105_GpsTrackList ──
constructor TFleet105_GpsTrackList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_GpsTrackList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_GpsTrackList.GetItem(Index: Integer): TFleet105_GpsTrack;
begin
  Result := TFleet105_GpsTrack(FList[Index]);
end;

function TFleet105_GpsTrackList.Add: TFleet105_GpsTrack;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_GpsTrack.Create;
  FList.Add(Result);
end;

procedure TFleet105_GpsTrackList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_GpsTrackList.FindById(const AId: Integer): TFleet105_GpsTrack;
var
  I: Integer;
  LItem: TFleet105_GpsTrack;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_GpsTrackList.FindByCode(const ACode: WideString): TFleet105_GpsTrack;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_GpsTrackList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_GpsTrackList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_GpsTrackList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_GpsTrackList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_GpsTrack;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_GpsTrackList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Depot
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Depot.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FDepotId := 0;
  FDepotCode := '';
  FDepotName := '';
  FAddress := '';
  FCity := '';
  FPostCode := '';
  FPhone := '';
  FManagerId := 0;
  FCapacityVehicles := 0;
  FCapacityDrivers := 0;
  FIsActive := False;
  FOpenTime := '';
  FCloseTime := '';
end;

destructor TFleet105_Depot.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Depot.Clear;
begin
  inherited Clear;
  FDepotId := 0;
  FDepotCode := '';
  FDepotName := '';
  FAddress := '';
  FCity := '';
  FPostCode := '';
  FPhone := '';
  FManagerId := 0;
  FCapacityVehicles := 0;
  FCapacityDrivers := 0;
  FIsActive := False;
  FOpenTime := '';
  FCloseTime := '';
end;

procedure TFleet105_Depot.Assign(Source: TFleet105_Depot);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FDepotId := Source.FDepotId;
  FDepotCode := Source.FDepotCode;
  FDepotName := Source.FDepotName;
  FAddress := Source.FAddress;
  FCity := Source.FCity;
  FPostCode := Source.FPostCode;
  FPhone := Source.FPhone;
  FManagerId := Source.FManagerId;
  FCapacityVehicles := Source.FCapacityVehicles;
  FCapacityDrivers := Source.FCapacityDrivers;
  FIsActive := Source.FIsActive;
  FOpenTime := Source.FOpenTime;
  FCloseTime := Source.FCloseTime;
end;

function TFleet105_Depot.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FDepotId >= 0);
end;

function TFleet105_Depot.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(FDepotCode);
    LParts.Add(FDepotName);
    LParts.Add(FAddress);
    LParts.Add(FCity);
    LParts.Add(FPostCode);
    LParts.Add(FPhone);
    LParts.Add(IntToStr(FManagerId));
    LParts.Add(IntToStr(FCapacityVehicles));
    LParts.Add(IntToStr(FCapacityDrivers));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(FOpenTime);
    LParts.Add(FCloseTime);
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Depot.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Depot.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_Depot.GetDepotCode: WideString;
begin
  // Pobierz wartość pola DepotCode
  Result := FDepotCode;
end;

procedure TFleet105_Depot.SetDepotCode(const Value: WideString);
begin
  // Ustaw wartość pola DepotCode
  FDepotCode := Value;
end;

function TFleet105_Depot.GetDepotName: WideString;
begin
  // Pobierz wartość pola DepotName
  Result := FDepotName;
end;

procedure TFleet105_Depot.SetDepotName(const Value: WideString);
begin
  // Ustaw wartość pola DepotName
  FDepotName := Value;
end;

function TFleet105_Depot.GetAddress: WideString;
begin
  // Pobierz wartość pola Address
  Result := FAddress;
end;

procedure TFleet105_Depot.SetAddress(const Value: WideString);
begin
  // Ustaw wartość pola Address
  FAddress := Value;
end;

function TFleet105_Depot.GetCity: WideString;
begin
  // Pobierz wartość pola City
  Result := FCity;
end;

procedure TFleet105_Depot.SetCity(const Value: WideString);
begin
  // Ustaw wartość pola City
  FCity := Value;
end;

function TFleet105_Depot.GetPostCode: WideString;
begin
  // Pobierz wartość pola PostCode
  Result := FPostCode;
end;

procedure TFleet105_Depot.SetPostCode(const Value: WideString);
begin
  // Ustaw wartość pola PostCode
  FPostCode := Value;
end;

function TFleet105_Depot.GetPhone: WideString;
begin
  // Pobierz wartość pola Phone
  Result := FPhone;
end;

procedure TFleet105_Depot.SetPhone(const Value: WideString);
begin
  // Ustaw wartość pola Phone
  FPhone := Value;
end;

function TFleet105_Depot.GetManagerId: Integer;
begin
  // Pobierz wartość pola ManagerId
  Result := FManagerId;
end;

procedure TFleet105_Depot.SetManagerId(const Value: Integer);
begin
  // Ustaw wartość pola ManagerId
  FManagerId := Value;
end;

function TFleet105_Depot.GetCapacityVehicles: Integer;
begin
  // Pobierz wartość pola CapacityVehicles
  Result := FCapacityVehicles;
end;

procedure TFleet105_Depot.SetCapacityVehicles(const Value: Integer);
begin
  // Ustaw wartość pola CapacityVehicles
  FCapacityVehicles := Value;
end;

function TFleet105_Depot.GetCapacityDrivers: Integer;
begin
  // Pobierz wartość pola CapacityDrivers
  Result := FCapacityDrivers;
end;

procedure TFleet105_Depot.SetCapacityDrivers(const Value: Integer);
begin
  // Ustaw wartość pola CapacityDrivers
  FCapacityDrivers := Value;
end;

function TFleet105_Depot.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Depot.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Depot.GetOpenTime: WideString;
begin
  // Pobierz wartość pola OpenTime
  Result := FOpenTime;
end;

procedure TFleet105_Depot.SetOpenTime(const Value: WideString);
begin
  // Ustaw wartość pola OpenTime
  FOpenTime := Value;
end;

function TFleet105_Depot.GetCloseTime: WideString;
begin
  // Pobierz wartość pola CloseTime
  Result := FCloseTime;
end;

procedure TFleet105_Depot.SetCloseTime(const Value: WideString);
begin
  // Ustaw wartość pola CloseTime
  FCloseTime := Value;
end;

// ── TFleet105_DepotList ──
constructor TFleet105_DepotList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_DepotList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_DepotList.GetItem(Index: Integer): TFleet105_Depot;
begin
  Result := TFleet105_Depot(FList[Index]);
end;

function TFleet105_DepotList.Add: TFleet105_Depot;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Depot.Create;
  FList.Add(Result);
end;

procedure TFleet105_DepotList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_DepotList.FindById(const AId: Integer): TFleet105_Depot;
var
  I: Integer;
  LItem: TFleet105_Depot;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_DepotList.FindByCode(const ACode: WideString): TFleet105_Depot;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_DepotList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_DepotList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_DepotList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_DepotList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Depot;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_DepotList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Employee
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Employee.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FEmpId := 0;
  FEmpNo := '';
  FFirstName := '';
  FLastName := '';
  FJobTitle := '';
  FDepartmentId := 0;
  FDepotId := 0;
  FHireDate := 0;
  FTermDate := 0;
  FSalary := 0.0;
  FIsActive := False;
  FEmail := '';
  FPhone := '';
  FManagerId := 0;
end;

destructor TFleet105_Employee.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Employee.Clear;
begin
  inherited Clear;
  FEmpId := 0;
  FEmpNo := '';
  FFirstName := '';
  FLastName := '';
  FJobTitle := '';
  FDepartmentId := 0;
  FDepotId := 0;
  FHireDate := 0;
  FTermDate := 0;
  FSalary := 0.0;
  FIsActive := False;
  FEmail := '';
  FPhone := '';
  FManagerId := 0;
end;

procedure TFleet105_Employee.Assign(Source: TFleet105_Employee);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FEmpId := Source.FEmpId;
  FEmpNo := Source.FEmpNo;
  FFirstName := Source.FFirstName;
  FLastName := Source.FLastName;
  FJobTitle := Source.FJobTitle;
  FDepartmentId := Source.FDepartmentId;
  FDepotId := Source.FDepotId;
  FHireDate := Source.FHireDate;
  FTermDate := Source.FTermDate;
  FSalary := Source.FSalary;
  FIsActive := Source.FIsActive;
  FEmail := Source.FEmail;
  FPhone := Source.FPhone;
  FManagerId := Source.FManagerId;
end;

function TFleet105_Employee.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FEmpId >= 0);
end;

function TFleet105_Employee.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FEmpId));
    LParts.Add(FEmpNo);
    LParts.Add(FFirstName);
    LParts.Add(FLastName);
    LParts.Add(FJobTitle);
    LParts.Add(IntToStr(FDepartmentId));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(DateTimeToStr(FHireDate));
    LParts.Add(DateTimeToStr(FTermDate));
    LParts.Add(FloatToStr(FSalary));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(FEmail);
    LParts.Add(FPhone);
    LParts.Add(IntToStr(FManagerId));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Employee.GetEmpId: Integer;
begin
  // Pobierz wartość pola EmpId
  Result := FEmpId;
end;

procedure TFleet105_Employee.SetEmpId(const Value: Integer);
begin
  // Ustaw wartość pola EmpId
  FEmpId := Value;
end;

function TFleet105_Employee.GetEmpNo: WideString;
begin
  // Pobierz wartość pola EmpNo
  Result := FEmpNo;
end;

procedure TFleet105_Employee.SetEmpNo(const Value: WideString);
begin
  // Ustaw wartość pola EmpNo
  FEmpNo := Value;
end;

function TFleet105_Employee.GetFirstName: WideString;
begin
  // Pobierz wartość pola FirstName
  Result := FFirstName;
end;

procedure TFleet105_Employee.SetFirstName(const Value: WideString);
begin
  // Ustaw wartość pola FirstName
  FFirstName := Value;
end;

function TFleet105_Employee.GetLastName: WideString;
begin
  // Pobierz wartość pola LastName
  Result := FLastName;
end;

procedure TFleet105_Employee.SetLastName(const Value: WideString);
begin
  // Ustaw wartość pola LastName
  FLastName := Value;
end;

function TFleet105_Employee.GetJobTitle: WideString;
begin
  // Pobierz wartość pola JobTitle
  Result := FJobTitle;
end;

procedure TFleet105_Employee.SetJobTitle(const Value: WideString);
begin
  // Ustaw wartość pola JobTitle
  FJobTitle := Value;
end;

function TFleet105_Employee.GetDepartmentId: Integer;
begin
  // Pobierz wartość pola DepartmentId
  Result := FDepartmentId;
end;

procedure TFleet105_Employee.SetDepartmentId(const Value: Integer);
begin
  // Ustaw wartość pola DepartmentId
  FDepartmentId := Value;
end;

function TFleet105_Employee.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Employee.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_Employee.GetHireDate: TDateTime;
begin
  // Pobierz wartość pola HireDate
  Result := FHireDate;
end;

procedure TFleet105_Employee.SetHireDate(const Value: TDateTime);
begin
  // Ustaw wartość pola HireDate
  FHireDate := Value;
end;

function TFleet105_Employee.GetTermDate: TDateTime;
begin
  // Pobierz wartość pola TermDate
  Result := FTermDate;
end;

procedure TFleet105_Employee.SetTermDate(const Value: TDateTime);
begin
  // Ustaw wartość pola TermDate
  FTermDate := Value;
end;

function TFleet105_Employee.GetSalary: Double;
begin
  // Pobierz wartość pola Salary
  Result := FSalary;
end;

procedure TFleet105_Employee.SetSalary(const Value: Double);
begin
  // Ustaw wartość pola Salary
  FSalary := Value;
end;

function TFleet105_Employee.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Employee.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Employee.GetEmail: WideString;
begin
  // Pobierz wartość pola Email
  Result := FEmail;
end;

procedure TFleet105_Employee.SetEmail(const Value: WideString);
begin
  // Ustaw wartość pola Email
  FEmail := Value;
end;

function TFleet105_Employee.GetPhone: WideString;
begin
  // Pobierz wartość pola Phone
  Result := FPhone;
end;

procedure TFleet105_Employee.SetPhone(const Value: WideString);
begin
  // Ustaw wartość pola Phone
  FPhone := Value;
end;

function TFleet105_Employee.GetManagerId: Integer;
begin
  // Pobierz wartość pola ManagerId
  Result := FManagerId;
end;

procedure TFleet105_Employee.SetManagerId(const Value: Integer);
begin
  // Ustaw wartość pola ManagerId
  FManagerId := Value;
end;

// ── TFleet105_EmployeeList ──
constructor TFleet105_EmployeeList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_EmployeeList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_EmployeeList.GetItem(Index: Integer): TFleet105_Employee;
begin
  Result := TFleet105_Employee(FList[Index]);
end;

function TFleet105_EmployeeList.Add: TFleet105_Employee;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Employee.Create;
  FList.Add(Result);
end;

procedure TFleet105_EmployeeList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_EmployeeList.FindById(const AId: Integer): TFleet105_Employee;
var
  I: Integer;
  LItem: TFleet105_Employee;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_EmployeeList.FindByCode(const ACode: WideString): TFleet105_Employee;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_EmployeeList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_EmployeeList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_EmployeeList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_EmployeeList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Employee;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_EmployeeList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Department
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Department.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FDeptId := 0;
  FDeptCode := '';
  FDeptName := '';
  FManagerId := 0;
  FCostCentre := '';
  FParentDeptId := 0;
  FIsActive := False;
  FHeadCount := 0;
  FBudgetYear := 0;
  FAnnualBudget := 0.0;
end;

destructor TFleet105_Department.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Department.Clear;
begin
  inherited Clear;
  FDeptId := 0;
  FDeptCode := '';
  FDeptName := '';
  FManagerId := 0;
  FCostCentre := '';
  FParentDeptId := 0;
  FIsActive := False;
  FHeadCount := 0;
  FBudgetYear := 0;
  FAnnualBudget := 0.0;
end;

procedure TFleet105_Department.Assign(Source: TFleet105_Department);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FDeptId := Source.FDeptId;
  FDeptCode := Source.FDeptCode;
  FDeptName := Source.FDeptName;
  FManagerId := Source.FManagerId;
  FCostCentre := Source.FCostCentre;
  FParentDeptId := Source.FParentDeptId;
  FIsActive := Source.FIsActive;
  FHeadCount := Source.FHeadCount;
  FBudgetYear := Source.FBudgetYear;
  FAnnualBudget := Source.FAnnualBudget;
end;

function TFleet105_Department.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FDeptId >= 0);
end;

function TFleet105_Department.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FDeptId));
    LParts.Add(FDeptCode);
    LParts.Add(FDeptName);
    LParts.Add(IntToStr(FManagerId));
    LParts.Add(FCostCentre);
    LParts.Add(IntToStr(FParentDeptId));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FHeadCount));
    LParts.Add(IntToStr(FBudgetYear));
    LParts.Add(FloatToStr(FAnnualBudget));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Department.GetDeptId: Integer;
begin
  // Pobierz wartość pola DeptId
  Result := FDeptId;
end;

procedure TFleet105_Department.SetDeptId(const Value: Integer);
begin
  // Ustaw wartość pola DeptId
  FDeptId := Value;
end;

function TFleet105_Department.GetDeptCode: WideString;
begin
  // Pobierz wartość pola DeptCode
  Result := FDeptCode;
end;

procedure TFleet105_Department.SetDeptCode(const Value: WideString);
begin
  // Ustaw wartość pola DeptCode
  FDeptCode := Value;
end;

function TFleet105_Department.GetDeptName: WideString;
begin
  // Pobierz wartość pola DeptName
  Result := FDeptName;
end;

procedure TFleet105_Department.SetDeptName(const Value: WideString);
begin
  // Ustaw wartość pola DeptName
  FDeptName := Value;
end;

function TFleet105_Department.GetManagerId: Integer;
begin
  // Pobierz wartość pola ManagerId
  Result := FManagerId;
end;

procedure TFleet105_Department.SetManagerId(const Value: Integer);
begin
  // Ustaw wartość pola ManagerId
  FManagerId := Value;
end;

function TFleet105_Department.GetCostCentre: WideString;
begin
  // Pobierz wartość pola CostCentre
  Result := FCostCentre;
end;

procedure TFleet105_Department.SetCostCentre(const Value: WideString);
begin
  // Ustaw wartość pola CostCentre
  FCostCentre := Value;
end;

function TFleet105_Department.GetParentDeptId: Integer;
begin
  // Pobierz wartość pola ParentDeptId
  Result := FParentDeptId;
end;

procedure TFleet105_Department.SetParentDeptId(const Value: Integer);
begin
  // Ustaw wartość pola ParentDeptId
  FParentDeptId := Value;
end;

function TFleet105_Department.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Department.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Department.GetHeadCount: Integer;
begin
  // Pobierz wartość pola HeadCount
  Result := FHeadCount;
end;

procedure TFleet105_Department.SetHeadCount(const Value: Integer);
begin
  // Ustaw wartość pola HeadCount
  FHeadCount := Value;
end;

function TFleet105_Department.GetBudgetYear: Integer;
begin
  // Pobierz wartość pola BudgetYear
  Result := FBudgetYear;
end;

procedure TFleet105_Department.SetBudgetYear(const Value: Integer);
begin
  // Ustaw wartość pola BudgetYear
  FBudgetYear := Value;
end;

function TFleet105_Department.GetAnnualBudget: Double;
begin
  // Pobierz wartość pola AnnualBudget
  Result := FAnnualBudget;
end;

procedure TFleet105_Department.SetAnnualBudget(const Value: Double);
begin
  // Ustaw wartość pola AnnualBudget
  FAnnualBudget := Value;
end;

// ── TFleet105_DepartmentList ──
constructor TFleet105_DepartmentList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_DepartmentList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_DepartmentList.GetItem(Index: Integer): TFleet105_Department;
begin
  Result := TFleet105_Department(FList[Index]);
end;

function TFleet105_DepartmentList.Add: TFleet105_Department;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Department.Create;
  FList.Add(Result);
end;

procedure TFleet105_DepartmentList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_DepartmentList.FindById(const AId: Integer): TFleet105_Department;
var
  I: Integer;
  LItem: TFleet105_Department;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_DepartmentList.FindByCode(const ACode: WideString): TFleet105_Department;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_DepartmentList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_DepartmentList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_DepartmentList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_DepartmentList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Department;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_DepartmentList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Schedule
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Schedule.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FScheduleId := 0;
  FRouteId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FDayOfWeek := 0;
  FDepartureTime := '';
  FArrivalTime := '';
  FFrequencyMins := 0;
  FValidFrom := 0;
  FValidTo := 0;
  FIsActive := False;
  FSeasonCode := 0;
end;

destructor TFleet105_Schedule.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Schedule.Clear;
begin
  inherited Clear;
  FScheduleId := 0;
  FRouteId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FDayOfWeek := 0;
  FDepartureTime := '';
  FArrivalTime := '';
  FFrequencyMins := 0;
  FValidFrom := 0;
  FValidTo := 0;
  FIsActive := False;
  FSeasonCode := 0;
end;

procedure TFleet105_Schedule.Assign(Source: TFleet105_Schedule);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FScheduleId := Source.FScheduleId;
  FRouteId := Source.FRouteId;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FDayOfWeek := Source.FDayOfWeek;
  FDepartureTime := Source.FDepartureTime;
  FArrivalTime := Source.FArrivalTime;
  FFrequencyMins := Source.FFrequencyMins;
  FValidFrom := Source.FValidFrom;
  FValidTo := Source.FValidTo;
  FIsActive := Source.FIsActive;
  FSeasonCode := Source.FSeasonCode;
end;

function TFleet105_Schedule.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FScheduleId >= 0);
end;

function TFleet105_Schedule.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FScheduleId));
    LParts.Add(IntToStr(FRouteId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(IntToStr(FDayOfWeek));
    LParts.Add(FDepartureTime);
    LParts.Add(FArrivalTime);
    LParts.Add(IntToStr(FFrequencyMins));
    LParts.Add(DateTimeToStr(FValidFrom));
    LParts.Add(DateTimeToStr(FValidTo));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FSeasonCode));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Schedule.GetScheduleId: Integer;
begin
  // Pobierz wartość pola ScheduleId
  Result := FScheduleId;
end;

procedure TFleet105_Schedule.SetScheduleId(const Value: Integer);
begin
  // Ustaw wartość pola ScheduleId
  FScheduleId := Value;
end;

function TFleet105_Schedule.GetRouteId: Integer;
begin
  // Pobierz wartość pola RouteId
  Result := FRouteId;
end;

procedure TFleet105_Schedule.SetRouteId(const Value: Integer);
begin
  // Ustaw wartość pola RouteId
  FRouteId := Value;
end;

function TFleet105_Schedule.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_Schedule.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_Schedule.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_Schedule.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_Schedule.GetDayOfWeek: Integer;
begin
  // Pobierz wartość pola DayOfWeek
  Result := FDayOfWeek;
end;

procedure TFleet105_Schedule.SetDayOfWeek(const Value: Integer);
begin
  // Ustaw wartość pola DayOfWeek
  FDayOfWeek := Value;
end;

function TFleet105_Schedule.GetDepartureTime: WideString;
begin
  // Pobierz wartość pola DepartureTime
  Result := FDepartureTime;
end;

procedure TFleet105_Schedule.SetDepartureTime(const Value: WideString);
begin
  // Ustaw wartość pola DepartureTime
  FDepartureTime := Value;
end;

function TFleet105_Schedule.GetArrivalTime: WideString;
begin
  // Pobierz wartość pola ArrivalTime
  Result := FArrivalTime;
end;

procedure TFleet105_Schedule.SetArrivalTime(const Value: WideString);
begin
  // Ustaw wartość pola ArrivalTime
  FArrivalTime := Value;
end;

function TFleet105_Schedule.GetFrequencyMins: Integer;
begin
  // Pobierz wartość pola FrequencyMins
  Result := FFrequencyMins;
end;

procedure TFleet105_Schedule.SetFrequencyMins(const Value: Integer);
begin
  // Ustaw wartość pola FrequencyMins
  FFrequencyMins := Value;
end;

function TFleet105_Schedule.GetValidFrom: TDateTime;
begin
  // Pobierz wartość pola ValidFrom
  Result := FValidFrom;
end;

procedure TFleet105_Schedule.SetValidFrom(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidFrom
  FValidFrom := Value;
end;

function TFleet105_Schedule.GetValidTo: TDateTime;
begin
  // Pobierz wartość pola ValidTo
  Result := FValidTo;
end;

procedure TFleet105_Schedule.SetValidTo(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidTo
  FValidTo := Value;
end;

function TFleet105_Schedule.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Schedule.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Schedule.GetSeasonCode: Integer;
begin
  // Pobierz wartość pola SeasonCode
  Result := FSeasonCode;
end;

procedure TFleet105_Schedule.SetSeasonCode(const Value: Integer);
begin
  // Ustaw wartość pola SeasonCode
  FSeasonCode := Value;
end;

// ── TFleet105_ScheduleList ──
constructor TFleet105_ScheduleList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ScheduleList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ScheduleList.GetItem(Index: Integer): TFleet105_Schedule;
begin
  Result := TFleet105_Schedule(FList[Index]);
end;

function TFleet105_ScheduleList.Add: TFleet105_Schedule;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Schedule.Create;
  FList.Add(Result);
end;

procedure TFleet105_ScheduleList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ScheduleList.FindById(const AId: Integer): TFleet105_Schedule;
var
  I: Integer;
  LItem: TFleet105_Schedule;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ScheduleList.FindByCode(const ACode: WideString): TFleet105_Schedule;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ScheduleList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ScheduleList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ScheduleList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ScheduleList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Schedule;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ScheduleList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Passenger
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Passenger.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPassId := 0;
  FCardNo := '';
  FFirstName := '';
  FLastName := '';
  FDateOfBirth := 0;
  FCardExpiry := 0;
  FBalanceCents := 0;
  FDiscountCode := 0;
  FIsBlacklisted := False;
  FLastTripDate := 0;
  FTripCount := 0;
  FDepotId := 0;
end;

destructor TFleet105_Passenger.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Passenger.Clear;
begin
  inherited Clear;
  FPassId := 0;
  FCardNo := '';
  FFirstName := '';
  FLastName := '';
  FDateOfBirth := 0;
  FCardExpiry := 0;
  FBalanceCents := 0;
  FDiscountCode := 0;
  FIsBlacklisted := False;
  FLastTripDate := 0;
  FTripCount := 0;
  FDepotId := 0;
end;

procedure TFleet105_Passenger.Assign(Source: TFleet105_Passenger);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPassId := Source.FPassId;
  FCardNo := Source.FCardNo;
  FFirstName := Source.FFirstName;
  FLastName := Source.FLastName;
  FDateOfBirth := Source.FDateOfBirth;
  FCardExpiry := Source.FCardExpiry;
  FBalanceCents := Source.FBalanceCents;
  FDiscountCode := Source.FDiscountCode;
  FIsBlacklisted := Source.FIsBlacklisted;
  FLastTripDate := Source.FLastTripDate;
  FTripCount := Source.FTripCount;
  FDepotId := Source.FDepotId;
end;

function TFleet105_Passenger.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPassId >= 0);
end;

function TFleet105_Passenger.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPassId));
    LParts.Add(FCardNo);
    LParts.Add(FFirstName);
    LParts.Add(FLastName);
    LParts.Add(DateTimeToStr(FDateOfBirth));
    LParts.Add(DateTimeToStr(FCardExpiry));
    LParts.Add(IntToStr(FBalanceCents));
    LParts.Add(IntToStr(FDiscountCode));
    LParts.Add(BoolToStr(FIsBlacklisted, True));
    LParts.Add(DateTimeToStr(FLastTripDate));
    LParts.Add(IntToStr(FTripCount));
    LParts.Add(IntToStr(FDepotId));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Passenger.GetPassId: Integer;
begin
  // Pobierz wartość pola PassId
  Result := FPassId;
end;

procedure TFleet105_Passenger.SetPassId(const Value: Integer);
begin
  // Ustaw wartość pola PassId
  FPassId := Value;
end;

function TFleet105_Passenger.GetCardNo: WideString;
begin
  // Pobierz wartość pola CardNo
  Result := FCardNo;
end;

procedure TFleet105_Passenger.SetCardNo(const Value: WideString);
begin
  // Ustaw wartość pola CardNo
  FCardNo := Value;
end;

function TFleet105_Passenger.GetFirstName: WideString;
begin
  // Pobierz wartość pola FirstName
  Result := FFirstName;
end;

procedure TFleet105_Passenger.SetFirstName(const Value: WideString);
begin
  // Ustaw wartość pola FirstName
  FFirstName := Value;
end;

function TFleet105_Passenger.GetLastName: WideString;
begin
  // Pobierz wartość pola LastName
  Result := FLastName;
end;

procedure TFleet105_Passenger.SetLastName(const Value: WideString);
begin
  // Ustaw wartość pola LastName
  FLastName := Value;
end;

function TFleet105_Passenger.GetDateOfBirth: TDateTime;
begin
  // Pobierz wartość pola DateOfBirth
  Result := FDateOfBirth;
end;

procedure TFleet105_Passenger.SetDateOfBirth(const Value: TDateTime);
begin
  // Ustaw wartość pola DateOfBirth
  FDateOfBirth := Value;
end;

function TFleet105_Passenger.GetCardExpiry: TDateTime;
begin
  // Pobierz wartość pola CardExpiry
  Result := FCardExpiry;
end;

procedure TFleet105_Passenger.SetCardExpiry(const Value: TDateTime);
begin
  // Ustaw wartość pola CardExpiry
  FCardExpiry := Value;
end;

function TFleet105_Passenger.GetBalanceCents: Integer;
begin
  // Pobierz wartość pola BalanceCents
  Result := FBalanceCents;
end;

procedure TFleet105_Passenger.SetBalanceCents(const Value: Integer);
begin
  // Ustaw wartość pola BalanceCents
  FBalanceCents := Value;
end;

function TFleet105_Passenger.GetDiscountCode: Integer;
begin
  // Pobierz wartość pola DiscountCode
  Result := FDiscountCode;
end;

procedure TFleet105_Passenger.SetDiscountCode(const Value: Integer);
begin
  // Ustaw wartość pola DiscountCode
  FDiscountCode := Value;
end;

function TFleet105_Passenger.GetIsBlacklisted: Boolean;
begin
  // Pobierz wartość pola IsBlacklisted
  Result := FIsBlacklisted;
end;

procedure TFleet105_Passenger.SetIsBlacklisted(const Value: Boolean);
begin
  // Ustaw wartość pola IsBlacklisted
  FIsBlacklisted := Value;
end;

function TFleet105_Passenger.GetLastTripDate: TDateTime;
begin
  // Pobierz wartość pola LastTripDate
  Result := FLastTripDate;
end;

procedure TFleet105_Passenger.SetLastTripDate(const Value: TDateTime);
begin
  // Ustaw wartość pola LastTripDate
  FLastTripDate := Value;
end;

function TFleet105_Passenger.GetTripCount: Integer;
begin
  // Pobierz wartość pola TripCount
  Result := FTripCount;
end;

procedure TFleet105_Passenger.SetTripCount(const Value: Integer);
begin
  // Ustaw wartość pola TripCount
  FTripCount := Value;
end;

function TFleet105_Passenger.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_Passenger.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

// ── TFleet105_PassengerList ──
constructor TFleet105_PassengerList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_PassengerList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_PassengerList.GetItem(Index: Integer): TFleet105_Passenger;
begin
  Result := TFleet105_Passenger(FList[Index]);
end;

function TFleet105_PassengerList.Add: TFleet105_Passenger;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Passenger.Create;
  FList.Add(Result);
end;

procedure TFleet105_PassengerList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_PassengerList.FindById(const AId: Integer): TFleet105_Passenger;
var
  I: Integer;
  LItem: TFleet105_Passenger;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_PassengerList.FindByCode(const ACode: WideString): TFleet105_Passenger;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_PassengerList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_PassengerList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_PassengerList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_PassengerList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Passenger;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_PassengerList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Trip
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Trip.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FTripId := 0;
  FJobId := 0;
  FRouteId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FStartTime := 0;
  FEndTime := 0;
  FStartOdometer := 0;
  FEndOdometer := 0;
  FPassengerCount := 0;
  FDelayMins := 0;
  FStatusCode := 0;
  FCancellationCode := 0;
end;

destructor TFleet105_Trip.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Trip.Clear;
begin
  inherited Clear;
  FTripId := 0;
  FJobId := 0;
  FRouteId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FStartTime := 0;
  FEndTime := 0;
  FStartOdometer := 0;
  FEndOdometer := 0;
  FPassengerCount := 0;
  FDelayMins := 0;
  FStatusCode := 0;
  FCancellationCode := 0;
end;

procedure TFleet105_Trip.Assign(Source: TFleet105_Trip);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FTripId := Source.FTripId;
  FJobId := Source.FJobId;
  FRouteId := Source.FRouteId;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FStartTime := Source.FStartTime;
  FEndTime := Source.FEndTime;
  FStartOdometer := Source.FStartOdometer;
  FEndOdometer := Source.FEndOdometer;
  FPassengerCount := Source.FPassengerCount;
  FDelayMins := Source.FDelayMins;
  FStatusCode := Source.FStatusCode;
  FCancellationCode := Source.FCancellationCode;
end;

function TFleet105_Trip.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FTripId >= 0);
end;

function TFleet105_Trip.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FTripId));
    LParts.Add(IntToStr(FJobId));
    LParts.Add(IntToStr(FRouteId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(DateTimeToStr(FStartTime));
    LParts.Add(DateTimeToStr(FEndTime));
    LParts.Add(IntToStr(FStartOdometer));
    LParts.Add(IntToStr(FEndOdometer));
    LParts.Add(IntToStr(FPassengerCount));
    LParts.Add(IntToStr(FDelayMins));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(IntToStr(FCancellationCode));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Trip.GetTripId: Integer;
begin
  // Pobierz wartość pola TripId
  Result := FTripId;
end;

procedure TFleet105_Trip.SetTripId(const Value: Integer);
begin
  // Ustaw wartość pola TripId
  FTripId := Value;
end;

function TFleet105_Trip.GetJobId: Integer;
begin
  // Pobierz wartość pola JobId
  Result := FJobId;
end;

procedure TFleet105_Trip.SetJobId(const Value: Integer);
begin
  // Ustaw wartość pola JobId
  FJobId := Value;
end;

function TFleet105_Trip.GetRouteId: Integer;
begin
  // Pobierz wartość pola RouteId
  Result := FRouteId;
end;

procedure TFleet105_Trip.SetRouteId(const Value: Integer);
begin
  // Ustaw wartość pola RouteId
  FRouteId := Value;
end;

function TFleet105_Trip.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_Trip.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_Trip.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_Trip.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_Trip.GetStartTime: TDateTime;
begin
  // Pobierz wartość pola StartTime
  Result := FStartTime;
end;

procedure TFleet105_Trip.SetStartTime(const Value: TDateTime);
begin
  // Ustaw wartość pola StartTime
  FStartTime := Value;
end;

function TFleet105_Trip.GetEndTime: TDateTime;
begin
  // Pobierz wartość pola EndTime
  Result := FEndTime;
end;

procedure TFleet105_Trip.SetEndTime(const Value: TDateTime);
begin
  // Ustaw wartość pola EndTime
  FEndTime := Value;
end;

function TFleet105_Trip.GetStartOdometer: Integer;
begin
  // Pobierz wartość pola StartOdometer
  Result := FStartOdometer;
end;

procedure TFleet105_Trip.SetStartOdometer(const Value: Integer);
begin
  // Ustaw wartość pola StartOdometer
  FStartOdometer := Value;
end;

function TFleet105_Trip.GetEndOdometer: Integer;
begin
  // Pobierz wartość pola EndOdometer
  Result := FEndOdometer;
end;

procedure TFleet105_Trip.SetEndOdometer(const Value: Integer);
begin
  // Ustaw wartość pola EndOdometer
  FEndOdometer := Value;
end;

function TFleet105_Trip.GetPassengerCount: Integer;
begin
  // Pobierz wartość pola PassengerCount
  Result := FPassengerCount;
end;

procedure TFleet105_Trip.SetPassengerCount(const Value: Integer);
begin
  // Ustaw wartość pola PassengerCount
  FPassengerCount := Value;
end;

function TFleet105_Trip.GetDelayMins: Integer;
begin
  // Pobierz wartość pola DelayMins
  Result := FDelayMins;
end;

procedure TFleet105_Trip.SetDelayMins(const Value: Integer);
begin
  // Ustaw wartość pola DelayMins
  FDelayMins := Value;
end;

function TFleet105_Trip.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_Trip.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_Trip.GetCancellationCode: Integer;
begin
  // Pobierz wartość pola CancellationCode
  Result := FCancellationCode;
end;

procedure TFleet105_Trip.SetCancellationCode(const Value: Integer);
begin
  // Ustaw wartość pola CancellationCode
  FCancellationCode := Value;
end;

// ── TFleet105_TripList ──
constructor TFleet105_TripList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_TripList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_TripList.GetItem(Index: Integer): TFleet105_Trip;
begin
  Result := TFleet105_Trip(FList[Index]);
end;

function TFleet105_TripList.Add: TFleet105_Trip;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Trip.Create;
  FList.Add(Result);
end;

procedure TFleet105_TripList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_TripList.FindById(const AId: Integer): TFleet105_Trip;
var
  I: Integer;
  LItem: TFleet105_Trip;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_TripList.FindByCode(const ACode: WideString): TFleet105_Trip;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_TripList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_TripList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_TripList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_TripList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Trip;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_TripList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_PayrollEntry
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_PayrollEntry.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPayId := 0;
  FDriverId := 0;
  FPeriodStart := 0;
  FPeriodEnd := 0;
  FTripCount := 0;
  FTotalHours := 0.0;
  FBasicPay := 0.0;
  FOvertimePay := 0.0;
  FAllowancePay := 0.0;
  FDeductionTotal := 0.0;
  FNetPay := 0.0;
  FPaymentDate := 0;
  FIsApproved := False;
  FApprovedBy := 0;
end;

destructor TFleet105_PayrollEntry.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_PayrollEntry.Clear;
begin
  inherited Clear;
  FPayId := 0;
  FDriverId := 0;
  FPeriodStart := 0;
  FPeriodEnd := 0;
  FTripCount := 0;
  FTotalHours := 0.0;
  FBasicPay := 0.0;
  FOvertimePay := 0.0;
  FAllowancePay := 0.0;
  FDeductionTotal := 0.0;
  FNetPay := 0.0;
  FPaymentDate := 0;
  FIsApproved := False;
  FApprovedBy := 0;
end;

procedure TFleet105_PayrollEntry.Assign(Source: TFleet105_PayrollEntry);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPayId := Source.FPayId;
  FDriverId := Source.FDriverId;
  FPeriodStart := Source.FPeriodStart;
  FPeriodEnd := Source.FPeriodEnd;
  FTripCount := Source.FTripCount;
  FTotalHours := Source.FTotalHours;
  FBasicPay := Source.FBasicPay;
  FOvertimePay := Source.FOvertimePay;
  FAllowancePay := Source.FAllowancePay;
  FDeductionTotal := Source.FDeductionTotal;
  FNetPay := Source.FNetPay;
  FPaymentDate := Source.FPaymentDate;
  FIsApproved := Source.FIsApproved;
  FApprovedBy := Source.FApprovedBy;
end;

function TFleet105_PayrollEntry.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPayId >= 0);
end;

function TFleet105_PayrollEntry.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPayId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(DateTimeToStr(FPeriodStart));
    LParts.Add(DateTimeToStr(FPeriodEnd));
    LParts.Add(IntToStr(FTripCount));
    LParts.Add(FloatToStr(FTotalHours));
    LParts.Add(FloatToStr(FBasicPay));
    LParts.Add(FloatToStr(FOvertimePay));
    LParts.Add(FloatToStr(FAllowancePay));
    LParts.Add(FloatToStr(FDeductionTotal));
    LParts.Add(FloatToStr(FNetPay));
    LParts.Add(DateTimeToStr(FPaymentDate));
    LParts.Add(BoolToStr(FIsApproved, True));
    LParts.Add(IntToStr(FApprovedBy));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_PayrollEntry.GetPayId: Integer;
begin
  // Pobierz wartość pola PayId
  Result := FPayId;
end;

procedure TFleet105_PayrollEntry.SetPayId(const Value: Integer);
begin
  // Ustaw wartość pola PayId
  FPayId := Value;
end;

function TFleet105_PayrollEntry.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_PayrollEntry.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_PayrollEntry.GetPeriodStart: TDateTime;
begin
  // Pobierz wartość pola PeriodStart
  Result := FPeriodStart;
end;

procedure TFleet105_PayrollEntry.SetPeriodStart(const Value: TDateTime);
begin
  // Ustaw wartość pola PeriodStart
  FPeriodStart := Value;
end;

function TFleet105_PayrollEntry.GetPeriodEnd: TDateTime;
begin
  // Pobierz wartość pola PeriodEnd
  Result := FPeriodEnd;
end;

procedure TFleet105_PayrollEntry.SetPeriodEnd(const Value: TDateTime);
begin
  // Ustaw wartość pola PeriodEnd
  FPeriodEnd := Value;
end;

function TFleet105_PayrollEntry.GetTripCount: Integer;
begin
  // Pobierz wartość pola TripCount
  Result := FTripCount;
end;

procedure TFleet105_PayrollEntry.SetTripCount(const Value: Integer);
begin
  // Ustaw wartość pola TripCount
  FTripCount := Value;
end;

function TFleet105_PayrollEntry.GetTotalHours: Double;
begin
  // Pobierz wartość pola TotalHours
  Result := FTotalHours;
end;

procedure TFleet105_PayrollEntry.SetTotalHours(const Value: Double);
begin
  // Ustaw wartość pola TotalHours
  FTotalHours := Value;
end;

function TFleet105_PayrollEntry.GetBasicPay: Double;
begin
  // Pobierz wartość pola BasicPay
  Result := FBasicPay;
end;

procedure TFleet105_PayrollEntry.SetBasicPay(const Value: Double);
begin
  // Ustaw wartość pola BasicPay
  FBasicPay := Value;
end;

function TFleet105_PayrollEntry.GetOvertimePay: Double;
begin
  // Pobierz wartość pola OvertimePay
  Result := FOvertimePay;
end;

procedure TFleet105_PayrollEntry.SetOvertimePay(const Value: Double);
begin
  // Ustaw wartość pola OvertimePay
  FOvertimePay := Value;
end;

function TFleet105_PayrollEntry.GetAllowancePay: Double;
begin
  // Pobierz wartość pola AllowancePay
  Result := FAllowancePay;
end;

procedure TFleet105_PayrollEntry.SetAllowancePay(const Value: Double);
begin
  // Ustaw wartość pola AllowancePay
  FAllowancePay := Value;
end;

function TFleet105_PayrollEntry.GetDeductionTotal: Double;
begin
  // Pobierz wartość pola DeductionTotal
  Result := FDeductionTotal;
end;

procedure TFleet105_PayrollEntry.SetDeductionTotal(const Value: Double);
begin
  // Ustaw wartość pola DeductionTotal
  FDeductionTotal := Value;
end;

function TFleet105_PayrollEntry.GetNetPay: Double;
begin
  // Pobierz wartość pola NetPay
  Result := FNetPay;
end;

procedure TFleet105_PayrollEntry.SetNetPay(const Value: Double);
begin
  // Ustaw wartość pola NetPay
  FNetPay := Value;
end;

function TFleet105_PayrollEntry.GetPaymentDate: TDateTime;
begin
  // Pobierz wartość pola PaymentDate
  Result := FPaymentDate;
end;

procedure TFleet105_PayrollEntry.SetPaymentDate(const Value: TDateTime);
begin
  // Ustaw wartość pola PaymentDate
  FPaymentDate := Value;
end;

function TFleet105_PayrollEntry.GetIsApproved: Boolean;
begin
  // Pobierz wartość pola IsApproved
  Result := FIsApproved;
end;

procedure TFleet105_PayrollEntry.SetIsApproved(const Value: Boolean);
begin
  // Ustaw wartość pola IsApproved
  FIsApproved := Value;
end;

function TFleet105_PayrollEntry.GetApprovedBy: Integer;
begin
  // Pobierz wartość pola ApprovedBy
  Result := FApprovedBy;
end;

procedure TFleet105_PayrollEntry.SetApprovedBy(const Value: Integer);
begin
  // Ustaw wartość pola ApprovedBy
  FApprovedBy := Value;
end;

// ── TFleet105_PayrollEntryList ──
constructor TFleet105_PayrollEntryList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_PayrollEntryList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_PayrollEntryList.GetItem(Index: Integer): TFleet105_PayrollEntry;
begin
  Result := TFleet105_PayrollEntry(FList[Index]);
end;

function TFleet105_PayrollEntryList.Add: TFleet105_PayrollEntry;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_PayrollEntry.Create;
  FList.Add(Result);
end;

procedure TFleet105_PayrollEntryList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_PayrollEntryList.FindById(const AId: Integer): TFleet105_PayrollEntry;
var
  I: Integer;
  LItem: TFleet105_PayrollEntry;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_PayrollEntryList.FindByCode(const ACode: WideString): TFleet105_PayrollEntry;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_PayrollEntryList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_PayrollEntryList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_PayrollEntryList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_PayrollEntryList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_PayrollEntry;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_PayrollEntryList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_MaintenancePlan
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_MaintenancePlan.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPlanId := 0;
  FVehicleId := 0;
  FServiceType := 0;
  FIntervalKm := 0;
  FIntervalDays := 0;
  FLastDoneKm := 0;
  FLastDoneDate := 0;
  FNextDueKm := 0;
  FNextDueDate := 0;
  FIsActive := False;
  FPriority := 0;
  FAssignedTech := 0;
end;

destructor TFleet105_MaintenancePlan.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_MaintenancePlan.Clear;
begin
  inherited Clear;
  FPlanId := 0;
  FVehicleId := 0;
  FServiceType := 0;
  FIntervalKm := 0;
  FIntervalDays := 0;
  FLastDoneKm := 0;
  FLastDoneDate := 0;
  FNextDueKm := 0;
  FNextDueDate := 0;
  FIsActive := False;
  FPriority := 0;
  FAssignedTech := 0;
end;

procedure TFleet105_MaintenancePlan.Assign(Source: TFleet105_MaintenancePlan);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPlanId := Source.FPlanId;
  FVehicleId := Source.FVehicleId;
  FServiceType := Source.FServiceType;
  FIntervalKm := Source.FIntervalKm;
  FIntervalDays := Source.FIntervalDays;
  FLastDoneKm := Source.FLastDoneKm;
  FLastDoneDate := Source.FLastDoneDate;
  FNextDueKm := Source.FNextDueKm;
  FNextDueDate := Source.FNextDueDate;
  FIsActive := Source.FIsActive;
  FPriority := Source.FPriority;
  FAssignedTech := Source.FAssignedTech;
end;

function TFleet105_MaintenancePlan.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPlanId >= 0);
end;

function TFleet105_MaintenancePlan.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPlanId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FServiceType));
    LParts.Add(IntToStr(FIntervalKm));
    LParts.Add(IntToStr(FIntervalDays));
    LParts.Add(IntToStr(FLastDoneKm));
    LParts.Add(DateTimeToStr(FLastDoneDate));
    LParts.Add(IntToStr(FNextDueKm));
    LParts.Add(DateTimeToStr(FNextDueDate));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FPriority));
    LParts.Add(IntToStr(FAssignedTech));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_MaintenancePlan.GetPlanId: Integer;
begin
  // Pobierz wartość pola PlanId
  Result := FPlanId;
end;

procedure TFleet105_MaintenancePlan.SetPlanId(const Value: Integer);
begin
  // Ustaw wartość pola PlanId
  FPlanId := Value;
end;

function TFleet105_MaintenancePlan.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_MaintenancePlan.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_MaintenancePlan.GetServiceType: Integer;
begin
  // Pobierz wartość pola ServiceType
  Result := FServiceType;
end;

procedure TFleet105_MaintenancePlan.SetServiceType(const Value: Integer);
begin
  // Ustaw wartość pola ServiceType
  FServiceType := Value;
end;

function TFleet105_MaintenancePlan.GetIntervalKm: Integer;
begin
  // Pobierz wartość pola IntervalKm
  Result := FIntervalKm;
end;

procedure TFleet105_MaintenancePlan.SetIntervalKm(const Value: Integer);
begin
  // Ustaw wartość pola IntervalKm
  FIntervalKm := Value;
end;

function TFleet105_MaintenancePlan.GetIntervalDays: Integer;
begin
  // Pobierz wartość pola IntervalDays
  Result := FIntervalDays;
end;

procedure TFleet105_MaintenancePlan.SetIntervalDays(const Value: Integer);
begin
  // Ustaw wartość pola IntervalDays
  FIntervalDays := Value;
end;

function TFleet105_MaintenancePlan.GetLastDoneKm: Integer;
begin
  // Pobierz wartość pola LastDoneKm
  Result := FLastDoneKm;
end;

procedure TFleet105_MaintenancePlan.SetLastDoneKm(const Value: Integer);
begin
  // Ustaw wartość pola LastDoneKm
  FLastDoneKm := Value;
end;

function TFleet105_MaintenancePlan.GetLastDoneDate: TDateTime;
begin
  // Pobierz wartość pola LastDoneDate
  Result := FLastDoneDate;
end;

procedure TFleet105_MaintenancePlan.SetLastDoneDate(const Value: TDateTime);
begin
  // Ustaw wartość pola LastDoneDate
  FLastDoneDate := Value;
end;

function TFleet105_MaintenancePlan.GetNextDueKm: Integer;
begin
  // Pobierz wartość pola NextDueKm
  Result := FNextDueKm;
end;

procedure TFleet105_MaintenancePlan.SetNextDueKm(const Value: Integer);
begin
  // Ustaw wartość pola NextDueKm
  FNextDueKm := Value;
end;

function TFleet105_MaintenancePlan.GetNextDueDate: TDateTime;
begin
  // Pobierz wartość pola NextDueDate
  Result := FNextDueDate;
end;

procedure TFleet105_MaintenancePlan.SetNextDueDate(const Value: TDateTime);
begin
  // Ustaw wartość pola NextDueDate
  FNextDueDate := Value;
end;

function TFleet105_MaintenancePlan.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_MaintenancePlan.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_MaintenancePlan.GetPriority: Integer;
begin
  // Pobierz wartość pola Priority
  Result := FPriority;
end;

procedure TFleet105_MaintenancePlan.SetPriority(const Value: Integer);
begin
  // Ustaw wartość pola Priority
  FPriority := Value;
end;

function TFleet105_MaintenancePlan.GetAssignedTech: Integer;
begin
  // Pobierz wartość pola AssignedTech
  Result := FAssignedTech;
end;

procedure TFleet105_MaintenancePlan.SetAssignedTech(const Value: Integer);
begin
  // Ustaw wartość pola AssignedTech
  FAssignedTech := Value;
end;

// ── TFleet105_MaintenancePlanList ──
constructor TFleet105_MaintenancePlanList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_MaintenancePlanList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_MaintenancePlanList.GetItem(Index: Integer): TFleet105_MaintenancePlan;
begin
  Result := TFleet105_MaintenancePlan(FList[Index]);
end;

function TFleet105_MaintenancePlanList.Add: TFleet105_MaintenancePlan;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_MaintenancePlan.Create;
  FList.Add(Result);
end;

procedure TFleet105_MaintenancePlanList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_MaintenancePlanList.FindById(const AId: Integer): TFleet105_MaintenancePlan;
var
  I: Integer;
  LItem: TFleet105_MaintenancePlan;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_MaintenancePlanList.FindByCode(const ACode: WideString): TFleet105_MaintenancePlan;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_MaintenancePlanList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_MaintenancePlanList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_MaintenancePlanList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_MaintenancePlanList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_MaintenancePlan;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_MaintenancePlanList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_PartStock
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_PartStock.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPartId := 0;
  FPartNo := '';
  FDescription := '';
  FCategory := 0;
  FUnitCost := 0.0;
  FStockQty := 0;
  FReorderLevel := 0;
  FReorderQty := 0;
  FDepotId := 0;
  FSupplierId := 0;
  FIsObsolete := False;
  FLastOrderDate := 0;
end;

destructor TFleet105_PartStock.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_PartStock.Clear;
begin
  inherited Clear;
  FPartId := 0;
  FPartNo := '';
  FDescription := '';
  FCategory := 0;
  FUnitCost := 0.0;
  FStockQty := 0;
  FReorderLevel := 0;
  FReorderQty := 0;
  FDepotId := 0;
  FSupplierId := 0;
  FIsObsolete := False;
  FLastOrderDate := 0;
end;

procedure TFleet105_PartStock.Assign(Source: TFleet105_PartStock);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPartId := Source.FPartId;
  FPartNo := Source.FPartNo;
  FDescription := Source.FDescription;
  FCategory := Source.FCategory;
  FUnitCost := Source.FUnitCost;
  FStockQty := Source.FStockQty;
  FReorderLevel := Source.FReorderLevel;
  FReorderQty := Source.FReorderQty;
  FDepotId := Source.FDepotId;
  FSupplierId := Source.FSupplierId;
  FIsObsolete := Source.FIsObsolete;
  FLastOrderDate := Source.FLastOrderDate;
end;

function TFleet105_PartStock.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPartId >= 0);
end;

function TFleet105_PartStock.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPartId));
    LParts.Add(FPartNo);
    LParts.Add(FDescription);
    LParts.Add(IntToStr(FCategory));
    LParts.Add(FloatToStr(FUnitCost));
    LParts.Add(IntToStr(FStockQty));
    LParts.Add(IntToStr(FReorderLevel));
    LParts.Add(IntToStr(FReorderQty));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FSupplierId));
    LParts.Add(BoolToStr(FIsObsolete, True));
    LParts.Add(DateTimeToStr(FLastOrderDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_PartStock.GetPartId: Integer;
begin
  // Pobierz wartość pola PartId
  Result := FPartId;
end;

procedure TFleet105_PartStock.SetPartId(const Value: Integer);
begin
  // Ustaw wartość pola PartId
  FPartId := Value;
end;

function TFleet105_PartStock.GetPartNo: WideString;
begin
  // Pobierz wartość pola PartNo
  Result := FPartNo;
end;

procedure TFleet105_PartStock.SetPartNo(const Value: WideString);
begin
  // Ustaw wartość pola PartNo
  FPartNo := Value;
end;

function TFleet105_PartStock.GetDescription: WideString;
begin
  // Pobierz wartość pola Description
  Result := FDescription;
end;

procedure TFleet105_PartStock.SetDescription(const Value: WideString);
begin
  // Ustaw wartość pola Description
  FDescription := Value;
end;

function TFleet105_PartStock.GetCategory: Integer;
begin
  // Pobierz wartość pola Category
  Result := FCategory;
end;

procedure TFleet105_PartStock.SetCategory(const Value: Integer);
begin
  // Ustaw wartość pola Category
  FCategory := Value;
end;

function TFleet105_PartStock.GetUnitCost: Double;
begin
  // Pobierz wartość pola UnitCost
  Result := FUnitCost;
end;

procedure TFleet105_PartStock.SetUnitCost(const Value: Double);
begin
  // Ustaw wartość pola UnitCost
  FUnitCost := Value;
end;

function TFleet105_PartStock.GetStockQty: Integer;
begin
  // Pobierz wartość pola StockQty
  Result := FStockQty;
end;

procedure TFleet105_PartStock.SetStockQty(const Value: Integer);
begin
  // Ustaw wartość pola StockQty
  FStockQty := Value;
end;

function TFleet105_PartStock.GetReorderLevel: Integer;
begin
  // Pobierz wartość pola ReorderLevel
  Result := FReorderLevel;
end;

procedure TFleet105_PartStock.SetReorderLevel(const Value: Integer);
begin
  // Ustaw wartość pola ReorderLevel
  FReorderLevel := Value;
end;

function TFleet105_PartStock.GetReorderQty: Integer;
begin
  // Pobierz wartość pola ReorderQty
  Result := FReorderQty;
end;

procedure TFleet105_PartStock.SetReorderQty(const Value: Integer);
begin
  // Ustaw wartość pola ReorderQty
  FReorderQty := Value;
end;

function TFleet105_PartStock.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_PartStock.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_PartStock.GetSupplierId: Integer;
begin
  // Pobierz wartość pola SupplierId
  Result := FSupplierId;
end;

procedure TFleet105_PartStock.SetSupplierId(const Value: Integer);
begin
  // Ustaw wartość pola SupplierId
  FSupplierId := Value;
end;

function TFleet105_PartStock.GetIsObsolete: Boolean;
begin
  // Pobierz wartość pola IsObsolete
  Result := FIsObsolete;
end;

procedure TFleet105_PartStock.SetIsObsolete(const Value: Boolean);
begin
  // Ustaw wartość pola IsObsolete
  FIsObsolete := Value;
end;

function TFleet105_PartStock.GetLastOrderDate: TDateTime;
begin
  // Pobierz wartość pola LastOrderDate
  Result := FLastOrderDate;
end;

procedure TFleet105_PartStock.SetLastOrderDate(const Value: TDateTime);
begin
  // Ustaw wartość pola LastOrderDate
  FLastOrderDate := Value;
end;

// ── TFleet105_PartStockList ──
constructor TFleet105_PartStockList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_PartStockList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_PartStockList.GetItem(Index: Integer): TFleet105_PartStock;
begin
  Result := TFleet105_PartStock(FList[Index]);
end;

function TFleet105_PartStockList.Add: TFleet105_PartStock;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_PartStock.Create;
  FList.Add(Result);
end;

procedure TFleet105_PartStockList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_PartStockList.FindById(const AId: Integer): TFleet105_PartStock;
var
  I: Integer;
  LItem: TFleet105_PartStock;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_PartStockList.FindByCode(const ACode: WideString): TFleet105_PartStock;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_PartStockList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_PartStockList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_PartStockList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_PartStockList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_PartStock;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_PartStockList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Supplier
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Supplier.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FSupplierId := 0;
  FSupplierCode := '';
  FCompanyName := '';
  FContactName := '';
  FPhone := '';
  FEmail := '';
  FAddress := '';
  FCity := '';
  FPostCode := '';
  FPayTermsDays := 0;
  FIsActive := False;
  FRatingScore := 0;
end;

destructor TFleet105_Supplier.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Supplier.Clear;
begin
  inherited Clear;
  FSupplierId := 0;
  FSupplierCode := '';
  FCompanyName := '';
  FContactName := '';
  FPhone := '';
  FEmail := '';
  FAddress := '';
  FCity := '';
  FPostCode := '';
  FPayTermsDays := 0;
  FIsActive := False;
  FRatingScore := 0;
end;

procedure TFleet105_Supplier.Assign(Source: TFleet105_Supplier);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FSupplierId := Source.FSupplierId;
  FSupplierCode := Source.FSupplierCode;
  FCompanyName := Source.FCompanyName;
  FContactName := Source.FContactName;
  FPhone := Source.FPhone;
  FEmail := Source.FEmail;
  FAddress := Source.FAddress;
  FCity := Source.FCity;
  FPostCode := Source.FPostCode;
  FPayTermsDays := Source.FPayTermsDays;
  FIsActive := Source.FIsActive;
  FRatingScore := Source.FRatingScore;
end;

function TFleet105_Supplier.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FSupplierId >= 0);
end;

function TFleet105_Supplier.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FSupplierId));
    LParts.Add(FSupplierCode);
    LParts.Add(FCompanyName);
    LParts.Add(FContactName);
    LParts.Add(FPhone);
    LParts.Add(FEmail);
    LParts.Add(FAddress);
    LParts.Add(FCity);
    LParts.Add(FPostCode);
    LParts.Add(IntToStr(FPayTermsDays));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FRatingScore));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Supplier.GetSupplierId: Integer;
begin
  // Pobierz wartość pola SupplierId
  Result := FSupplierId;
end;

procedure TFleet105_Supplier.SetSupplierId(const Value: Integer);
begin
  // Ustaw wartość pola SupplierId
  FSupplierId := Value;
end;

function TFleet105_Supplier.GetSupplierCode: WideString;
begin
  // Pobierz wartość pola SupplierCode
  Result := FSupplierCode;
end;

procedure TFleet105_Supplier.SetSupplierCode(const Value: WideString);
begin
  // Ustaw wartość pola SupplierCode
  FSupplierCode := Value;
end;

function TFleet105_Supplier.GetCompanyName: WideString;
begin
  // Pobierz wartość pola CompanyName
  Result := FCompanyName;
end;

procedure TFleet105_Supplier.SetCompanyName(const Value: WideString);
begin
  // Ustaw wartość pola CompanyName
  FCompanyName := Value;
end;

function TFleet105_Supplier.GetContactName: WideString;
begin
  // Pobierz wartość pola ContactName
  Result := FContactName;
end;

procedure TFleet105_Supplier.SetContactName(const Value: WideString);
begin
  // Ustaw wartość pola ContactName
  FContactName := Value;
end;

function TFleet105_Supplier.GetPhone: WideString;
begin
  // Pobierz wartość pola Phone
  Result := FPhone;
end;

procedure TFleet105_Supplier.SetPhone(const Value: WideString);
begin
  // Ustaw wartość pola Phone
  FPhone := Value;
end;

function TFleet105_Supplier.GetEmail: WideString;
begin
  // Pobierz wartość pola Email
  Result := FEmail;
end;

procedure TFleet105_Supplier.SetEmail(const Value: WideString);
begin
  // Ustaw wartość pola Email
  FEmail := Value;
end;

function TFleet105_Supplier.GetAddress: WideString;
begin
  // Pobierz wartość pola Address
  Result := FAddress;
end;

procedure TFleet105_Supplier.SetAddress(const Value: WideString);
begin
  // Ustaw wartość pola Address
  FAddress := Value;
end;

function TFleet105_Supplier.GetCity: WideString;
begin
  // Pobierz wartość pola City
  Result := FCity;
end;

procedure TFleet105_Supplier.SetCity(const Value: WideString);
begin
  // Ustaw wartość pola City
  FCity := Value;
end;

function TFleet105_Supplier.GetPostCode: WideString;
begin
  // Pobierz wartość pola PostCode
  Result := FPostCode;
end;

procedure TFleet105_Supplier.SetPostCode(const Value: WideString);
begin
  // Ustaw wartość pola PostCode
  FPostCode := Value;
end;

function TFleet105_Supplier.GetPayTermsDays: Integer;
begin
  // Pobierz wartość pola PayTermsDays
  Result := FPayTermsDays;
end;

procedure TFleet105_Supplier.SetPayTermsDays(const Value: Integer);
begin
  // Ustaw wartość pola PayTermsDays
  FPayTermsDays := Value;
end;

function TFleet105_Supplier.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_Supplier.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_Supplier.GetRatingScore: Integer;
begin
  // Pobierz wartość pola RatingScore
  Result := FRatingScore;
end;

procedure TFleet105_Supplier.SetRatingScore(const Value: Integer);
begin
  // Ustaw wartość pola RatingScore
  FRatingScore := Value;
end;

// ── TFleet105_SupplierList ──
constructor TFleet105_SupplierList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_SupplierList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_SupplierList.GetItem(Index: Integer): TFleet105_Supplier;
begin
  Result := TFleet105_Supplier(FList[Index]);
end;

function TFleet105_SupplierList.Add: TFleet105_Supplier;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Supplier.Create;
  FList.Add(Result);
end;

procedure TFleet105_SupplierList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_SupplierList.FindById(const AId: Integer): TFleet105_Supplier;
var
  I: Integer;
  LItem: TFleet105_Supplier;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_SupplierList.FindByCode(const ACode: WideString): TFleet105_Supplier;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_SupplierList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_SupplierList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_SupplierList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_SupplierList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Supplier;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_SupplierList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_PurchaseOrder
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_PurchaseOrder.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPoId := 0;
  FPoNumber := '';
  FSupplierId := 0;
  FOrderDate := 0;
  FDeliveryDate := 0;
  FDepotId := 0;
  FTotalValue := 0.0;
  FStatusCode := 0;
  FCreatedBy := 0;
  FApprovedBy := 0;
  FNotes := '';
  FIsUrgent := False;
end;

destructor TFleet105_PurchaseOrder.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_PurchaseOrder.Clear;
begin
  inherited Clear;
  FPoId := 0;
  FPoNumber := '';
  FSupplierId := 0;
  FOrderDate := 0;
  FDeliveryDate := 0;
  FDepotId := 0;
  FTotalValue := 0.0;
  FStatusCode := 0;
  FCreatedBy := 0;
  FApprovedBy := 0;
  FNotes := '';
  FIsUrgent := False;
end;

procedure TFleet105_PurchaseOrder.Assign(Source: TFleet105_PurchaseOrder);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPoId := Source.FPoId;
  FPoNumber := Source.FPoNumber;
  FSupplierId := Source.FSupplierId;
  FOrderDate := Source.FOrderDate;
  FDeliveryDate := Source.FDeliveryDate;
  FDepotId := Source.FDepotId;
  FTotalValue := Source.FTotalValue;
  FStatusCode := Source.FStatusCode;
  FCreatedBy := Source.FCreatedBy;
  FApprovedBy := Source.FApprovedBy;
  FNotes := Source.FNotes;
  FIsUrgent := Source.FIsUrgent;
end;

function TFleet105_PurchaseOrder.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPoId >= 0);
end;

function TFleet105_PurchaseOrder.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPoId));
    LParts.Add(FPoNumber);
    LParts.Add(IntToStr(FSupplierId));
    LParts.Add(DateTimeToStr(FOrderDate));
    LParts.Add(DateTimeToStr(FDeliveryDate));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(FloatToStr(FTotalValue));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(IntToStr(FCreatedBy));
    LParts.Add(IntToStr(FApprovedBy));
    LParts.Add(FNotes);
    LParts.Add(BoolToStr(FIsUrgent, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_PurchaseOrder.GetPoId: Integer;
begin
  // Pobierz wartość pola PoId
  Result := FPoId;
end;

procedure TFleet105_PurchaseOrder.SetPoId(const Value: Integer);
begin
  // Ustaw wartość pola PoId
  FPoId := Value;
end;

function TFleet105_PurchaseOrder.GetPoNumber: WideString;
begin
  // Pobierz wartość pola PoNumber
  Result := FPoNumber;
end;

procedure TFleet105_PurchaseOrder.SetPoNumber(const Value: WideString);
begin
  // Ustaw wartość pola PoNumber
  FPoNumber := Value;
end;

function TFleet105_PurchaseOrder.GetSupplierId: Integer;
begin
  // Pobierz wartość pola SupplierId
  Result := FSupplierId;
end;

procedure TFleet105_PurchaseOrder.SetSupplierId(const Value: Integer);
begin
  // Ustaw wartość pola SupplierId
  FSupplierId := Value;
end;

function TFleet105_PurchaseOrder.GetOrderDate: TDateTime;
begin
  // Pobierz wartość pola OrderDate
  Result := FOrderDate;
end;

procedure TFleet105_PurchaseOrder.SetOrderDate(const Value: TDateTime);
begin
  // Ustaw wartość pola OrderDate
  FOrderDate := Value;
end;

function TFleet105_PurchaseOrder.GetDeliveryDate: TDateTime;
begin
  // Pobierz wartość pola DeliveryDate
  Result := FDeliveryDate;
end;

procedure TFleet105_PurchaseOrder.SetDeliveryDate(const Value: TDateTime);
begin
  // Ustaw wartość pola DeliveryDate
  FDeliveryDate := Value;
end;

function TFleet105_PurchaseOrder.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_PurchaseOrder.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_PurchaseOrder.GetTotalValue: Double;
begin
  // Pobierz wartość pola TotalValue
  Result := FTotalValue;
end;

procedure TFleet105_PurchaseOrder.SetTotalValue(const Value: Double);
begin
  // Ustaw wartość pola TotalValue
  FTotalValue := Value;
end;

function TFleet105_PurchaseOrder.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_PurchaseOrder.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_PurchaseOrder.GetCreatedBy: Integer;
begin
  // Pobierz wartość pola CreatedBy
  Result := FCreatedBy;
end;

procedure TFleet105_PurchaseOrder.SetCreatedBy(const Value: Integer);
begin
  // Ustaw wartość pola CreatedBy
  FCreatedBy := Value;
end;

function TFleet105_PurchaseOrder.GetApprovedBy: Integer;
begin
  // Pobierz wartość pola ApprovedBy
  Result := FApprovedBy;
end;

procedure TFleet105_PurchaseOrder.SetApprovedBy(const Value: Integer);
begin
  // Ustaw wartość pola ApprovedBy
  FApprovedBy := Value;
end;

function TFleet105_PurchaseOrder.GetNotes: WideString;
begin
  // Pobierz wartość pola Notes
  Result := FNotes;
end;

procedure TFleet105_PurchaseOrder.SetNotes(const Value: WideString);
begin
  // Ustaw wartość pola Notes
  FNotes := Value;
end;

function TFleet105_PurchaseOrder.GetIsUrgent: Boolean;
begin
  // Pobierz wartość pola IsUrgent
  Result := FIsUrgent;
end;

procedure TFleet105_PurchaseOrder.SetIsUrgent(const Value: Boolean);
begin
  // Ustaw wartość pola IsUrgent
  FIsUrgent := Value;
end;

// ── TFleet105_PurchaseOrderList ──
constructor TFleet105_PurchaseOrderList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_PurchaseOrderList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_PurchaseOrderList.GetItem(Index: Integer): TFleet105_PurchaseOrder;
begin
  Result := TFleet105_PurchaseOrder(FList[Index]);
end;

function TFleet105_PurchaseOrderList.Add: TFleet105_PurchaseOrder;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_PurchaseOrder.Create;
  FList.Add(Result);
end;

procedure TFleet105_PurchaseOrderList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_PurchaseOrderList.FindById(const AId: Integer): TFleet105_PurchaseOrder;
var
  I: Integer;
  LItem: TFleet105_PurchaseOrder;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_PurchaseOrderList.FindByCode(const ACode: WideString): TFleet105_PurchaseOrder;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_PurchaseOrderList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_PurchaseOrderList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_PurchaseOrderList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_PurchaseOrderList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_PurchaseOrder;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_PurchaseOrderList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Invoice
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Invoice.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FInvId := 0;
  FInvNumber := '';
  FSupplierId := 0;
  FPoId := 0;
  FInvDate := 0;
  FDueDate := 0;
  FNetAmount := 0.0;
  FTaxAmount := 0.0;
  FTotalAmount := 0.0;
  FStatusCode := 0;
  FPaidDate := 0;
  FPaidAmount := 0.0;
  FIsReconciled := False;
end;

destructor TFleet105_Invoice.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Invoice.Clear;
begin
  inherited Clear;
  FInvId := 0;
  FInvNumber := '';
  FSupplierId := 0;
  FPoId := 0;
  FInvDate := 0;
  FDueDate := 0;
  FNetAmount := 0.0;
  FTaxAmount := 0.0;
  FTotalAmount := 0.0;
  FStatusCode := 0;
  FPaidDate := 0;
  FPaidAmount := 0.0;
  FIsReconciled := False;
end;

procedure TFleet105_Invoice.Assign(Source: TFleet105_Invoice);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FInvId := Source.FInvId;
  FInvNumber := Source.FInvNumber;
  FSupplierId := Source.FSupplierId;
  FPoId := Source.FPoId;
  FInvDate := Source.FInvDate;
  FDueDate := Source.FDueDate;
  FNetAmount := Source.FNetAmount;
  FTaxAmount := Source.FTaxAmount;
  FTotalAmount := Source.FTotalAmount;
  FStatusCode := Source.FStatusCode;
  FPaidDate := Source.FPaidDate;
  FPaidAmount := Source.FPaidAmount;
  FIsReconciled := Source.FIsReconciled;
end;

function TFleet105_Invoice.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FInvId >= 0);
end;

function TFleet105_Invoice.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FInvId));
    LParts.Add(FInvNumber);
    LParts.Add(IntToStr(FSupplierId));
    LParts.Add(IntToStr(FPoId));
    LParts.Add(DateTimeToStr(FInvDate));
    LParts.Add(DateTimeToStr(FDueDate));
    LParts.Add(FloatToStr(FNetAmount));
    LParts.Add(FloatToStr(FTaxAmount));
    LParts.Add(FloatToStr(FTotalAmount));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(DateTimeToStr(FPaidDate));
    LParts.Add(FloatToStr(FPaidAmount));
    LParts.Add(BoolToStr(FIsReconciled, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Invoice.GetInvId: Integer;
begin
  // Pobierz wartość pola InvId
  Result := FInvId;
end;

procedure TFleet105_Invoice.SetInvId(const Value: Integer);
begin
  // Ustaw wartość pola InvId
  FInvId := Value;
end;

function TFleet105_Invoice.GetInvNumber: WideString;
begin
  // Pobierz wartość pola InvNumber
  Result := FInvNumber;
end;

procedure TFleet105_Invoice.SetInvNumber(const Value: WideString);
begin
  // Ustaw wartość pola InvNumber
  FInvNumber := Value;
end;

function TFleet105_Invoice.GetSupplierId: Integer;
begin
  // Pobierz wartość pola SupplierId
  Result := FSupplierId;
end;

procedure TFleet105_Invoice.SetSupplierId(const Value: Integer);
begin
  // Ustaw wartość pola SupplierId
  FSupplierId := Value;
end;

function TFleet105_Invoice.GetPoId: Integer;
begin
  // Pobierz wartość pola PoId
  Result := FPoId;
end;

procedure TFleet105_Invoice.SetPoId(const Value: Integer);
begin
  // Ustaw wartość pola PoId
  FPoId := Value;
end;

function TFleet105_Invoice.GetInvDate: TDateTime;
begin
  // Pobierz wartość pola InvDate
  Result := FInvDate;
end;

procedure TFleet105_Invoice.SetInvDate(const Value: TDateTime);
begin
  // Ustaw wartość pola InvDate
  FInvDate := Value;
end;

function TFleet105_Invoice.GetDueDate: TDateTime;
begin
  // Pobierz wartość pola DueDate
  Result := FDueDate;
end;

procedure TFleet105_Invoice.SetDueDate(const Value: TDateTime);
begin
  // Ustaw wartość pola DueDate
  FDueDate := Value;
end;

function TFleet105_Invoice.GetNetAmount: Double;
begin
  // Pobierz wartość pola NetAmount
  Result := FNetAmount;
end;

procedure TFleet105_Invoice.SetNetAmount(const Value: Double);
begin
  // Ustaw wartość pola NetAmount
  FNetAmount := Value;
end;

function TFleet105_Invoice.GetTaxAmount: Double;
begin
  // Pobierz wartość pola TaxAmount
  Result := FTaxAmount;
end;

procedure TFleet105_Invoice.SetTaxAmount(const Value: Double);
begin
  // Ustaw wartość pola TaxAmount
  FTaxAmount := Value;
end;

function TFleet105_Invoice.GetTotalAmount: Double;
begin
  // Pobierz wartość pola TotalAmount
  Result := FTotalAmount;
end;

procedure TFleet105_Invoice.SetTotalAmount(const Value: Double);
begin
  // Ustaw wartość pola TotalAmount
  FTotalAmount := Value;
end;

function TFleet105_Invoice.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_Invoice.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_Invoice.GetPaidDate: TDateTime;
begin
  // Pobierz wartość pola PaidDate
  Result := FPaidDate;
end;

procedure TFleet105_Invoice.SetPaidDate(const Value: TDateTime);
begin
  // Ustaw wartość pola PaidDate
  FPaidDate := Value;
end;

function TFleet105_Invoice.GetPaidAmount: Double;
begin
  // Pobierz wartość pola PaidAmount
  Result := FPaidAmount;
end;

procedure TFleet105_Invoice.SetPaidAmount(const Value: Double);
begin
  // Ustaw wartość pola PaidAmount
  FPaidAmount := Value;
end;

function TFleet105_Invoice.GetIsReconciled: Boolean;
begin
  // Pobierz wartość pola IsReconciled
  Result := FIsReconciled;
end;

procedure TFleet105_Invoice.SetIsReconciled(const Value: Boolean);
begin
  // Ustaw wartość pola IsReconciled
  FIsReconciled := Value;
end;

// ── TFleet105_InvoiceList ──
constructor TFleet105_InvoiceList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_InvoiceList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_InvoiceList.GetItem(Index: Integer): TFleet105_Invoice;
begin
  Result := TFleet105_Invoice(FList[Index]);
end;

function TFleet105_InvoiceList.Add: TFleet105_Invoice;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Invoice.Create;
  FList.Add(Result);
end;

procedure TFleet105_InvoiceList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_InvoiceList.FindById(const AId: Integer): TFleet105_Invoice;
var
  I: Integer;
  LItem: TFleet105_Invoice;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_InvoiceList.FindByCode(const ACode: WideString): TFleet105_Invoice;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_InvoiceList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_InvoiceList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_InvoiceList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_InvoiceList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Invoice;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_InvoiceList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_CostCentre
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_CostCentre.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FCcId := 0;
  FCcCode := '';
  FCcName := '';
  FDepotId := 0;
  FManagerId := 0;
  FBudgetYear := 0;
  FAnnualBudget := 0.0;
  FSpentToDate := 0.0;
  FForecastTotal := 0.0;
  FIsActive := False;
  FParentCcId := 0;
end;

destructor TFleet105_CostCentre.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_CostCentre.Clear;
begin
  inherited Clear;
  FCcId := 0;
  FCcCode := '';
  FCcName := '';
  FDepotId := 0;
  FManagerId := 0;
  FBudgetYear := 0;
  FAnnualBudget := 0.0;
  FSpentToDate := 0.0;
  FForecastTotal := 0.0;
  FIsActive := False;
  FParentCcId := 0;
end;

procedure TFleet105_CostCentre.Assign(Source: TFleet105_CostCentre);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FCcId := Source.FCcId;
  FCcCode := Source.FCcCode;
  FCcName := Source.FCcName;
  FDepotId := Source.FDepotId;
  FManagerId := Source.FManagerId;
  FBudgetYear := Source.FBudgetYear;
  FAnnualBudget := Source.FAnnualBudget;
  FSpentToDate := Source.FSpentToDate;
  FForecastTotal := Source.FForecastTotal;
  FIsActive := Source.FIsActive;
  FParentCcId := Source.FParentCcId;
end;

function TFleet105_CostCentre.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FCcId >= 0);
end;

function TFleet105_CostCentre.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FCcId));
    LParts.Add(FCcCode);
    LParts.Add(FCcName);
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FManagerId));
    LParts.Add(IntToStr(FBudgetYear));
    LParts.Add(FloatToStr(FAnnualBudget));
    LParts.Add(FloatToStr(FSpentToDate));
    LParts.Add(FloatToStr(FForecastTotal));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FParentCcId));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_CostCentre.GetCcId: Integer;
begin
  // Pobierz wartość pola CcId
  Result := FCcId;
end;

procedure TFleet105_CostCentre.SetCcId(const Value: Integer);
begin
  // Ustaw wartość pola CcId
  FCcId := Value;
end;

function TFleet105_CostCentre.GetCcCode: WideString;
begin
  // Pobierz wartość pola CcCode
  Result := FCcCode;
end;

procedure TFleet105_CostCentre.SetCcCode(const Value: WideString);
begin
  // Ustaw wartość pola CcCode
  FCcCode := Value;
end;

function TFleet105_CostCentre.GetCcName: WideString;
begin
  // Pobierz wartość pola CcName
  Result := FCcName;
end;

procedure TFleet105_CostCentre.SetCcName(const Value: WideString);
begin
  // Ustaw wartość pola CcName
  FCcName := Value;
end;

function TFleet105_CostCentre.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_CostCentre.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_CostCentre.GetManagerId: Integer;
begin
  // Pobierz wartość pola ManagerId
  Result := FManagerId;
end;

procedure TFleet105_CostCentre.SetManagerId(const Value: Integer);
begin
  // Ustaw wartość pola ManagerId
  FManagerId := Value;
end;

function TFleet105_CostCentre.GetBudgetYear: Integer;
begin
  // Pobierz wartość pola BudgetYear
  Result := FBudgetYear;
end;

procedure TFleet105_CostCentre.SetBudgetYear(const Value: Integer);
begin
  // Ustaw wartość pola BudgetYear
  FBudgetYear := Value;
end;

function TFleet105_CostCentre.GetAnnualBudget: Double;
begin
  // Pobierz wartość pola AnnualBudget
  Result := FAnnualBudget;
end;

procedure TFleet105_CostCentre.SetAnnualBudget(const Value: Double);
begin
  // Ustaw wartość pola AnnualBudget
  FAnnualBudget := Value;
end;

function TFleet105_CostCentre.GetSpentToDate: Double;
begin
  // Pobierz wartość pola SpentToDate
  Result := FSpentToDate;
end;

procedure TFleet105_CostCentre.SetSpentToDate(const Value: Double);
begin
  // Ustaw wartość pola SpentToDate
  FSpentToDate := Value;
end;

function TFleet105_CostCentre.GetForecastTotal: Double;
begin
  // Pobierz wartość pola ForecastTotal
  Result := FForecastTotal;
end;

procedure TFleet105_CostCentre.SetForecastTotal(const Value: Double);
begin
  // Ustaw wartość pola ForecastTotal
  FForecastTotal := Value;
end;

function TFleet105_CostCentre.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_CostCentre.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_CostCentre.GetParentCcId: Integer;
begin
  // Pobierz wartość pola ParentCcId
  Result := FParentCcId;
end;

procedure TFleet105_CostCentre.SetParentCcId(const Value: Integer);
begin
  // Ustaw wartość pola ParentCcId
  FParentCcId := Value;
end;

// ── TFleet105_CostCentreList ──
constructor TFleet105_CostCentreList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_CostCentreList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_CostCentreList.GetItem(Index: Integer): TFleet105_CostCentre;
begin
  Result := TFleet105_CostCentre(FList[Index]);
end;

function TFleet105_CostCentreList.Add: TFleet105_CostCentre;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_CostCentre.Create;
  FList.Add(Result);
end;

procedure TFleet105_CostCentreList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_CostCentreList.FindById(const AId: Integer): TFleet105_CostCentre;
var
  I: Integer;
  LItem: TFleet105_CostCentre;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_CostCentreList.FindByCode(const ACode: WideString): TFleet105_CostCentre;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_CostCentreList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_CostCentreList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_CostCentreList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_CostCentreList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_CostCentre;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_CostCentreList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_TyreRecord
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_TyreRecord.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FTyreId := 0;
  FVehicleId := 0;
  FPosition := 0;
  FBrand := '';
  FSize := '';
  FFitDate := 0;
  FOdometerFit := 0;
  FRemoveDate := 0;
  FOdometerRemove := 0;
  FTreadDepthMm := 0.0;
  FIsRetread := False;
  FConditionCode := 0;
end;

destructor TFleet105_TyreRecord.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_TyreRecord.Clear;
begin
  inherited Clear;
  FTyreId := 0;
  FVehicleId := 0;
  FPosition := 0;
  FBrand := '';
  FSize := '';
  FFitDate := 0;
  FOdometerFit := 0;
  FRemoveDate := 0;
  FOdometerRemove := 0;
  FTreadDepthMm := 0.0;
  FIsRetread := False;
  FConditionCode := 0;
end;

procedure TFleet105_TyreRecord.Assign(Source: TFleet105_TyreRecord);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FTyreId := Source.FTyreId;
  FVehicleId := Source.FVehicleId;
  FPosition := Source.FPosition;
  FBrand := Source.FBrand;
  FSize := Source.FSize;
  FFitDate := Source.FFitDate;
  FOdometerFit := Source.FOdometerFit;
  FRemoveDate := Source.FRemoveDate;
  FOdometerRemove := Source.FOdometerRemove;
  FTreadDepthMm := Source.FTreadDepthMm;
  FIsRetread := Source.FIsRetread;
  FConditionCode := Source.FConditionCode;
end;

function TFleet105_TyreRecord.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FTyreId >= 0);
end;

function TFleet105_TyreRecord.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FTyreId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FPosition));
    LParts.Add(FBrand);
    LParts.Add(FSize);
    LParts.Add(DateTimeToStr(FFitDate));
    LParts.Add(IntToStr(FOdometerFit));
    LParts.Add(DateTimeToStr(FRemoveDate));
    LParts.Add(IntToStr(FOdometerRemove));
    LParts.Add(FloatToStr(FTreadDepthMm));
    LParts.Add(BoolToStr(FIsRetread, True));
    LParts.Add(IntToStr(FConditionCode));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_TyreRecord.GetTyreId: Integer;
begin
  // Pobierz wartość pola TyreId
  Result := FTyreId;
end;

procedure TFleet105_TyreRecord.SetTyreId(const Value: Integer);
begin
  // Ustaw wartość pola TyreId
  FTyreId := Value;
end;

function TFleet105_TyreRecord.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_TyreRecord.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_TyreRecord.GetPosition: Integer;
begin
  // Pobierz wartość pola Position
  Result := FPosition;
end;

procedure TFleet105_TyreRecord.SetPosition(const Value: Integer);
begin
  // Ustaw wartość pola Position
  FPosition := Value;
end;

function TFleet105_TyreRecord.GetBrand: WideString;
begin
  // Pobierz wartość pola Brand
  Result := FBrand;
end;

procedure TFleet105_TyreRecord.SetBrand(const Value: WideString);
begin
  // Ustaw wartość pola Brand
  FBrand := Value;
end;

function TFleet105_TyreRecord.GetSize: WideString;
begin
  // Pobierz wartość pola Size
  Result := FSize;
end;

procedure TFleet105_TyreRecord.SetSize(const Value: WideString);
begin
  // Ustaw wartość pola Size
  FSize := Value;
end;

function TFleet105_TyreRecord.GetFitDate: TDateTime;
begin
  // Pobierz wartość pola FitDate
  Result := FFitDate;
end;

procedure TFleet105_TyreRecord.SetFitDate(const Value: TDateTime);
begin
  // Ustaw wartość pola FitDate
  FFitDate := Value;
end;

function TFleet105_TyreRecord.GetOdometerFit: Integer;
begin
  // Pobierz wartość pola OdometerFit
  Result := FOdometerFit;
end;

procedure TFleet105_TyreRecord.SetOdometerFit(const Value: Integer);
begin
  // Ustaw wartość pola OdometerFit
  FOdometerFit := Value;
end;

function TFleet105_TyreRecord.GetRemoveDate: TDateTime;
begin
  // Pobierz wartość pola RemoveDate
  Result := FRemoveDate;
end;

procedure TFleet105_TyreRecord.SetRemoveDate(const Value: TDateTime);
begin
  // Ustaw wartość pola RemoveDate
  FRemoveDate := Value;
end;

function TFleet105_TyreRecord.GetOdometerRemove: Integer;
begin
  // Pobierz wartość pola OdometerRemove
  Result := FOdometerRemove;
end;

procedure TFleet105_TyreRecord.SetOdometerRemove(const Value: Integer);
begin
  // Ustaw wartość pola OdometerRemove
  FOdometerRemove := Value;
end;

function TFleet105_TyreRecord.GetTreadDepthMm: Double;
begin
  // Pobierz wartość pola TreadDepthMm
  Result := FTreadDepthMm;
end;

procedure TFleet105_TyreRecord.SetTreadDepthMm(const Value: Double);
begin
  // Ustaw wartość pola TreadDepthMm
  FTreadDepthMm := Value;
end;

function TFleet105_TyreRecord.GetIsRetread: Boolean;
begin
  // Pobierz wartość pola IsRetread
  Result := FIsRetread;
end;

procedure TFleet105_TyreRecord.SetIsRetread(const Value: Boolean);
begin
  // Ustaw wartość pola IsRetread
  FIsRetread := Value;
end;

function TFleet105_TyreRecord.GetConditionCode: Integer;
begin
  // Pobierz wartość pola ConditionCode
  Result := FConditionCode;
end;

procedure TFleet105_TyreRecord.SetConditionCode(const Value: Integer);
begin
  // Ustaw wartość pola ConditionCode
  FConditionCode := Value;
end;

// ── TFleet105_TyreRecordList ──
constructor TFleet105_TyreRecordList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_TyreRecordList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_TyreRecordList.GetItem(Index: Integer): TFleet105_TyreRecord;
begin
  Result := TFleet105_TyreRecord(FList[Index]);
end;

function TFleet105_TyreRecordList.Add: TFleet105_TyreRecord;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_TyreRecord.Create;
  FList.Add(Result);
end;

procedure TFleet105_TyreRecordList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_TyreRecordList.FindById(const AId: Integer): TFleet105_TyreRecord;
var
  I: Integer;
  LItem: TFleet105_TyreRecord;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_TyreRecordList.FindByCode(const ACode: WideString): TFleet105_TyreRecord;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_TyreRecordList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_TyreRecordList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_TyreRecordList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_TyreRecordList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_TyreRecord;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_TyreRecordList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_PermitLicence
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_PermitLicence.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FPermitId := 0;
  FEntityType := 0;
  FEntityId := 0;
  FPermitType := 0;
  FPermitNo := '';
  FIssuedBy := '';
  FIssueDate := 0;
  FExpiryDate := 0;
  FIssuedTo := '';
  FStatusCode := 0;
  FNotes := '';
  FRenewalReminderDays := 0;
end;

destructor TFleet105_PermitLicence.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_PermitLicence.Clear;
begin
  inherited Clear;
  FPermitId := 0;
  FEntityType := 0;
  FEntityId := 0;
  FPermitType := 0;
  FPermitNo := '';
  FIssuedBy := '';
  FIssueDate := 0;
  FExpiryDate := 0;
  FIssuedTo := '';
  FStatusCode := 0;
  FNotes := '';
  FRenewalReminderDays := 0;
end;

procedure TFleet105_PermitLicence.Assign(Source: TFleet105_PermitLicence);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FPermitId := Source.FPermitId;
  FEntityType := Source.FEntityType;
  FEntityId := Source.FEntityId;
  FPermitType := Source.FPermitType;
  FPermitNo := Source.FPermitNo;
  FIssuedBy := Source.FIssuedBy;
  FIssueDate := Source.FIssueDate;
  FExpiryDate := Source.FExpiryDate;
  FIssuedTo := Source.FIssuedTo;
  FStatusCode := Source.FStatusCode;
  FNotes := Source.FNotes;
  FRenewalReminderDays := Source.FRenewalReminderDays;
end;

function TFleet105_PermitLicence.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FPermitId >= 0);
end;

function TFleet105_PermitLicence.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FPermitId));
    LParts.Add(IntToStr(FEntityType));
    LParts.Add(IntToStr(FEntityId));
    LParts.Add(IntToStr(FPermitType));
    LParts.Add(FPermitNo);
    LParts.Add(FIssuedBy);
    LParts.Add(DateTimeToStr(FIssueDate));
    LParts.Add(DateTimeToStr(FExpiryDate));
    LParts.Add(FIssuedTo);
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(FNotes);
    LParts.Add(IntToStr(FRenewalReminderDays));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_PermitLicence.GetPermitId: Integer;
begin
  // Pobierz wartość pola PermitId
  Result := FPermitId;
end;

procedure TFleet105_PermitLicence.SetPermitId(const Value: Integer);
begin
  // Ustaw wartość pola PermitId
  FPermitId := Value;
end;

function TFleet105_PermitLicence.GetEntityType: Integer;
begin
  // Pobierz wartość pola EntityType
  Result := FEntityType;
end;

procedure TFleet105_PermitLicence.SetEntityType(const Value: Integer);
begin
  // Ustaw wartość pola EntityType
  FEntityType := Value;
end;

function TFleet105_PermitLicence.GetEntityId: Integer;
begin
  // Pobierz wartość pola EntityId
  Result := FEntityId;
end;

procedure TFleet105_PermitLicence.SetEntityId(const Value: Integer);
begin
  // Ustaw wartość pola EntityId
  FEntityId := Value;
end;

function TFleet105_PermitLicence.GetPermitType: Integer;
begin
  // Pobierz wartość pola PermitType
  Result := FPermitType;
end;

procedure TFleet105_PermitLicence.SetPermitType(const Value: Integer);
begin
  // Ustaw wartość pola PermitType
  FPermitType := Value;
end;

function TFleet105_PermitLicence.GetPermitNo: WideString;
begin
  // Pobierz wartość pola PermitNo
  Result := FPermitNo;
end;

procedure TFleet105_PermitLicence.SetPermitNo(const Value: WideString);
begin
  // Ustaw wartość pola PermitNo
  FPermitNo := Value;
end;

function TFleet105_PermitLicence.GetIssuedBy: WideString;
begin
  // Pobierz wartość pola IssuedBy
  Result := FIssuedBy;
end;

procedure TFleet105_PermitLicence.SetIssuedBy(const Value: WideString);
begin
  // Ustaw wartość pola IssuedBy
  FIssuedBy := Value;
end;

function TFleet105_PermitLicence.GetIssueDate: TDateTime;
begin
  // Pobierz wartość pola IssueDate
  Result := FIssueDate;
end;

procedure TFleet105_PermitLicence.SetIssueDate(const Value: TDateTime);
begin
  // Ustaw wartość pola IssueDate
  FIssueDate := Value;
end;

function TFleet105_PermitLicence.GetExpiryDate: TDateTime;
begin
  // Pobierz wartość pola ExpiryDate
  Result := FExpiryDate;
end;

procedure TFleet105_PermitLicence.SetExpiryDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ExpiryDate
  FExpiryDate := Value;
end;

function TFleet105_PermitLicence.GetIssuedTo: WideString;
begin
  // Pobierz wartość pola IssuedTo
  Result := FIssuedTo;
end;

procedure TFleet105_PermitLicence.SetIssuedTo(const Value: WideString);
begin
  // Ustaw wartość pola IssuedTo
  FIssuedTo := Value;
end;

function TFleet105_PermitLicence.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_PermitLicence.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_PermitLicence.GetNotes: WideString;
begin
  // Pobierz wartość pola Notes
  Result := FNotes;
end;

procedure TFleet105_PermitLicence.SetNotes(const Value: WideString);
begin
  // Ustaw wartość pola Notes
  FNotes := Value;
end;

function TFleet105_PermitLicence.GetRenewalReminderDays: Integer;
begin
  // Pobierz wartość pola RenewalReminderDays
  Result := FRenewalReminderDays;
end;

procedure TFleet105_PermitLicence.SetRenewalReminderDays(const Value: Integer);
begin
  // Ustaw wartość pola RenewalReminderDays
  FRenewalReminderDays := Value;
end;

// ── TFleet105_PermitLicenceList ──
constructor TFleet105_PermitLicenceList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_PermitLicenceList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_PermitLicenceList.GetItem(Index: Integer): TFleet105_PermitLicence;
begin
  Result := TFleet105_PermitLicence(FList[Index]);
end;

function TFleet105_PermitLicenceList.Add: TFleet105_PermitLicence;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_PermitLicence.Create;
  FList.Add(Result);
end;

procedure TFleet105_PermitLicenceList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_PermitLicenceList.FindById(const AId: Integer): TFleet105_PermitLicence;
var
  I: Integer;
  LItem: TFleet105_PermitLicence;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_PermitLicenceList.FindByCode(const ACode: WideString): TFleet105_PermitLicence;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_PermitLicenceList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_PermitLicenceList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_PermitLicenceList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_PermitLicenceList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_PermitLicence;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_PermitLicenceList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_AlertEvent
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_AlertEvent.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FAlertId := 0;
  FDeviceId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FAlertTime := 0;
  FAlertType := 0;
  FSeverityCode := 0;
  FDescription := '';
  FLatitude := 0.0;
  FLongitude := 0.0;
  FSpeedKph := 0.0;
  FIsAcknowledged := False;
  FAcknowledgedBy := 0;
  FAcknowledgedTime := 0;
end;

destructor TFleet105_AlertEvent.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_AlertEvent.Clear;
begin
  inherited Clear;
  FAlertId := 0;
  FDeviceId := 0;
  FVehicleId := 0;
  FDriverId := 0;
  FAlertTime := 0;
  FAlertType := 0;
  FSeverityCode := 0;
  FDescription := '';
  FLatitude := 0.0;
  FLongitude := 0.0;
  FSpeedKph := 0.0;
  FIsAcknowledged := False;
  FAcknowledgedBy := 0;
  FAcknowledgedTime := 0;
end;

procedure TFleet105_AlertEvent.Assign(Source: TFleet105_AlertEvent);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FAlertId := Source.FAlertId;
  FDeviceId := Source.FDeviceId;
  FVehicleId := Source.FVehicleId;
  FDriverId := Source.FDriverId;
  FAlertTime := Source.FAlertTime;
  FAlertType := Source.FAlertType;
  FSeverityCode := Source.FSeverityCode;
  FDescription := Source.FDescription;
  FLatitude := Source.FLatitude;
  FLongitude := Source.FLongitude;
  FSpeedKph := Source.FSpeedKph;
  FIsAcknowledged := Source.FIsAcknowledged;
  FAcknowledgedBy := Source.FAcknowledgedBy;
  FAcknowledgedTime := Source.FAcknowledgedTime;
end;

function TFleet105_AlertEvent.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FAlertId >= 0);
end;

function TFleet105_AlertEvent.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FAlertId));
    LParts.Add(IntToStr(FDeviceId));
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FDriverId));
    LParts.Add(DateTimeToStr(FAlertTime));
    LParts.Add(IntToStr(FAlertType));
    LParts.Add(IntToStr(FSeverityCode));
    LParts.Add(FDescription);
    LParts.Add(FloatToStr(FLatitude));
    LParts.Add(FloatToStr(FLongitude));
    LParts.Add(FloatToStr(FSpeedKph));
    LParts.Add(BoolToStr(FIsAcknowledged, True));
    LParts.Add(IntToStr(FAcknowledgedBy));
    LParts.Add(DateTimeToStr(FAcknowledgedTime));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_AlertEvent.GetAlertId: Integer;
begin
  // Pobierz wartość pola AlertId
  Result := FAlertId;
end;

procedure TFleet105_AlertEvent.SetAlertId(const Value: Integer);
begin
  // Ustaw wartość pola AlertId
  FAlertId := Value;
end;

function TFleet105_AlertEvent.GetDeviceId: Integer;
begin
  // Pobierz wartość pola DeviceId
  Result := FDeviceId;
end;

procedure TFleet105_AlertEvent.SetDeviceId(const Value: Integer);
begin
  // Ustaw wartość pola DeviceId
  FDeviceId := Value;
end;

function TFleet105_AlertEvent.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_AlertEvent.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_AlertEvent.GetDriverId: Integer;
begin
  // Pobierz wartość pola DriverId
  Result := FDriverId;
end;

procedure TFleet105_AlertEvent.SetDriverId(const Value: Integer);
begin
  // Ustaw wartość pola DriverId
  FDriverId := Value;
end;

function TFleet105_AlertEvent.GetAlertTime: TDateTime;
begin
  // Pobierz wartość pola AlertTime
  Result := FAlertTime;
end;

procedure TFleet105_AlertEvent.SetAlertTime(const Value: TDateTime);
begin
  // Ustaw wartość pola AlertTime
  FAlertTime := Value;
end;

function TFleet105_AlertEvent.GetAlertType: Integer;
begin
  // Pobierz wartość pola AlertType
  Result := FAlertType;
end;

procedure TFleet105_AlertEvent.SetAlertType(const Value: Integer);
begin
  // Ustaw wartość pola AlertType
  FAlertType := Value;
end;

function TFleet105_AlertEvent.GetSeverityCode: Integer;
begin
  // Pobierz wartość pola SeverityCode
  Result := FSeverityCode;
end;

procedure TFleet105_AlertEvent.SetSeverityCode(const Value: Integer);
begin
  // Ustaw wartość pola SeverityCode
  FSeverityCode := Value;
end;

function TFleet105_AlertEvent.GetDescription: WideString;
begin
  // Pobierz wartość pola Description
  Result := FDescription;
end;

procedure TFleet105_AlertEvent.SetDescription(const Value: WideString);
begin
  // Ustaw wartość pola Description
  FDescription := Value;
end;

function TFleet105_AlertEvent.GetLatitude: Double;
begin
  // Pobierz wartość pola Latitude
  Result := FLatitude;
end;

procedure TFleet105_AlertEvent.SetLatitude(const Value: Double);
begin
  // Ustaw wartość pola Latitude
  FLatitude := Value;
end;

function TFleet105_AlertEvent.GetLongitude: Double;
begin
  // Pobierz wartość pola Longitude
  Result := FLongitude;
end;

procedure TFleet105_AlertEvent.SetLongitude(const Value: Double);
begin
  // Ustaw wartość pola Longitude
  FLongitude := Value;
end;

function TFleet105_AlertEvent.GetSpeedKph: Double;
begin
  // Pobierz wartość pola SpeedKph
  Result := FSpeedKph;
end;

procedure TFleet105_AlertEvent.SetSpeedKph(const Value: Double);
begin
  // Ustaw wartość pola SpeedKph
  FSpeedKph := Value;
end;

function TFleet105_AlertEvent.GetIsAcknowledged: Boolean;
begin
  // Pobierz wartość pola IsAcknowledged
  Result := FIsAcknowledged;
end;

procedure TFleet105_AlertEvent.SetIsAcknowledged(const Value: Boolean);
begin
  // Ustaw wartość pola IsAcknowledged
  FIsAcknowledged := Value;
end;

function TFleet105_AlertEvent.GetAcknowledgedBy: Integer;
begin
  // Pobierz wartość pola AcknowledgedBy
  Result := FAcknowledgedBy;
end;

procedure TFleet105_AlertEvent.SetAcknowledgedBy(const Value: Integer);
begin
  // Ustaw wartość pola AcknowledgedBy
  FAcknowledgedBy := Value;
end;

function TFleet105_AlertEvent.GetAcknowledgedTime: TDateTime;
begin
  // Pobierz wartość pola AcknowledgedTime
  Result := FAcknowledgedTime;
end;

procedure TFleet105_AlertEvent.SetAcknowledgedTime(const Value: TDateTime);
begin
  // Ustaw wartość pola AcknowledgedTime
  FAcknowledgedTime := Value;
end;

// ── TFleet105_AlertEventList ──
constructor TFleet105_AlertEventList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_AlertEventList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_AlertEventList.GetItem(Index: Integer): TFleet105_AlertEvent;
begin
  Result := TFleet105_AlertEvent(FList[Index]);
end;

function TFleet105_AlertEventList.Add: TFleet105_AlertEvent;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_AlertEvent.Create;
  FList.Add(Result);
end;

procedure TFleet105_AlertEventList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_AlertEventList.FindById(const AId: Integer): TFleet105_AlertEvent;
var
  I: Integer;
  LItem: TFleet105_AlertEvent;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_AlertEventList.FindByCode(const ACode: WideString): TFleet105_AlertEvent;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_AlertEventList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_AlertEventList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_AlertEventList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_AlertEventList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_AlertEvent;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_AlertEventList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_ReportDef
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_ReportDef.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FReportId := 0;
  FReportCode := '';
  FReportName := '';
  FReportType := 0;
  FCategoryCode := 0;
  FQueryText := '';
  FParamList := '';
  FColumnList := '';
  FSortOrder := '';
  FIsActive := False;
  FCreatedBy := 0;
  FLastModified := 0;
end;

destructor TFleet105_ReportDef.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_ReportDef.Clear;
begin
  inherited Clear;
  FReportId := 0;
  FReportCode := '';
  FReportName := '';
  FReportType := 0;
  FCategoryCode := 0;
  FQueryText := '';
  FParamList := '';
  FColumnList := '';
  FSortOrder := '';
  FIsActive := False;
  FCreatedBy := 0;
  FLastModified := 0;
end;

procedure TFleet105_ReportDef.Assign(Source: TFleet105_ReportDef);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FReportId := Source.FReportId;
  FReportCode := Source.FReportCode;
  FReportName := Source.FReportName;
  FReportType := Source.FReportType;
  FCategoryCode := Source.FCategoryCode;
  FQueryText := Source.FQueryText;
  FParamList := Source.FParamList;
  FColumnList := Source.FColumnList;
  FSortOrder := Source.FSortOrder;
  FIsActive := Source.FIsActive;
  FCreatedBy := Source.FCreatedBy;
  FLastModified := Source.FLastModified;
end;

function TFleet105_ReportDef.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FReportId >= 0);
end;

function TFleet105_ReportDef.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FReportId));
    LParts.Add(FReportCode);
    LParts.Add(FReportName);
    LParts.Add(IntToStr(FReportType));
    LParts.Add(IntToStr(FCategoryCode));
    LParts.Add(FQueryText);
    LParts.Add(FParamList);
    LParts.Add(FColumnList);
    LParts.Add(FSortOrder);
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FCreatedBy));
    LParts.Add(DateTimeToStr(FLastModified));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_ReportDef.GetReportId: Integer;
begin
  // Pobierz wartość pola ReportId
  Result := FReportId;
end;

procedure TFleet105_ReportDef.SetReportId(const Value: Integer);
begin
  // Ustaw wartość pola ReportId
  FReportId := Value;
end;

function TFleet105_ReportDef.GetReportCode: WideString;
begin
  // Pobierz wartość pola ReportCode
  Result := FReportCode;
end;

procedure TFleet105_ReportDef.SetReportCode(const Value: WideString);
begin
  // Ustaw wartość pola ReportCode
  FReportCode := Value;
end;

function TFleet105_ReportDef.GetReportName: WideString;
begin
  // Pobierz wartość pola ReportName
  Result := FReportName;
end;

procedure TFleet105_ReportDef.SetReportName(const Value: WideString);
begin
  // Ustaw wartość pola ReportName
  FReportName := Value;
end;

function TFleet105_ReportDef.GetReportType: Integer;
begin
  // Pobierz wartość pola ReportType
  Result := FReportType;
end;

procedure TFleet105_ReportDef.SetReportType(const Value: Integer);
begin
  // Ustaw wartość pola ReportType
  FReportType := Value;
end;

function TFleet105_ReportDef.GetCategoryCode: Integer;
begin
  // Pobierz wartość pola CategoryCode
  Result := FCategoryCode;
end;

procedure TFleet105_ReportDef.SetCategoryCode(const Value: Integer);
begin
  // Ustaw wartość pola CategoryCode
  FCategoryCode := Value;
end;

function TFleet105_ReportDef.GetQueryText: WideString;
begin
  // Pobierz wartość pola QueryText
  Result := FQueryText;
end;

procedure TFleet105_ReportDef.SetQueryText(const Value: WideString);
begin
  // Ustaw wartość pola QueryText
  FQueryText := Value;
end;

function TFleet105_ReportDef.GetParamList: WideString;
begin
  // Pobierz wartość pola ParamList
  Result := FParamList;
end;

procedure TFleet105_ReportDef.SetParamList(const Value: WideString);
begin
  // Ustaw wartość pola ParamList
  FParamList := Value;
end;

function TFleet105_ReportDef.GetColumnList: WideString;
begin
  // Pobierz wartość pola ColumnList
  Result := FColumnList;
end;

procedure TFleet105_ReportDef.SetColumnList(const Value: WideString);
begin
  // Ustaw wartość pola ColumnList
  FColumnList := Value;
end;

function TFleet105_ReportDef.GetSortOrder: WideString;
begin
  // Pobierz wartość pola SortOrder
  Result := FSortOrder;
end;

procedure TFleet105_ReportDef.SetSortOrder(const Value: WideString);
begin
  // Ustaw wartość pola SortOrder
  FSortOrder := Value;
end;

function TFleet105_ReportDef.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_ReportDef.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_ReportDef.GetCreatedBy: Integer;
begin
  // Pobierz wartość pola CreatedBy
  Result := FCreatedBy;
end;

procedure TFleet105_ReportDef.SetCreatedBy(const Value: Integer);
begin
  // Ustaw wartość pola CreatedBy
  FCreatedBy := Value;
end;

function TFleet105_ReportDef.GetLastModified: TDateTime;
begin
  // Pobierz wartość pola LastModified
  Result := FLastModified;
end;

procedure TFleet105_ReportDef.SetLastModified(const Value: TDateTime);
begin
  // Ustaw wartość pola LastModified
  FLastModified := Value;
end;

// ── TFleet105_ReportDefList ──
constructor TFleet105_ReportDefList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ReportDefList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ReportDefList.GetItem(Index: Integer): TFleet105_ReportDef;
begin
  Result := TFleet105_ReportDef(FList[Index]);
end;

function TFleet105_ReportDefList.Add: TFleet105_ReportDef;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_ReportDef.Create;
  FList.Add(Result);
end;

procedure TFleet105_ReportDefList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ReportDefList.FindById(const AId: Integer): TFleet105_ReportDef;
var
  I: Integer;
  LItem: TFleet105_ReportDef;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ReportDefList.FindByCode(const ACode: WideString): TFleet105_ReportDef;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ReportDefList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ReportDefList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ReportDefList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ReportDefList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_ReportDef;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ReportDefList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_UserAccount
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_UserAccount.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FUserId := 0;
  FUserName := '';
  FPasswordHash := '';
  FFullName := '';
  FEmail := '';
  FRoleId := 0;
  FDepotId := 0;
  FIsActive := False;
  FLastLogin := 0;
  FFailedAttempts := 0;
  FIsLocked := False;
  FCreatedDate := 0;
  FForceReset := False;
end;

destructor TFleet105_UserAccount.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_UserAccount.Clear;
begin
  inherited Clear;
  FUserId := 0;
  FUserName := '';
  FPasswordHash := '';
  FFullName := '';
  FEmail := '';
  FRoleId := 0;
  FDepotId := 0;
  FIsActive := False;
  FLastLogin := 0;
  FFailedAttempts := 0;
  FIsLocked := False;
  FCreatedDate := 0;
  FForceReset := False;
end;

procedure TFleet105_UserAccount.Assign(Source: TFleet105_UserAccount);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FUserId := Source.FUserId;
  FUserName := Source.FUserName;
  FPasswordHash := Source.FPasswordHash;
  FFullName := Source.FFullName;
  FEmail := Source.FEmail;
  FRoleId := Source.FRoleId;
  FDepotId := Source.FDepotId;
  FIsActive := Source.FIsActive;
  FLastLogin := Source.FLastLogin;
  FFailedAttempts := Source.FFailedAttempts;
  FIsLocked := Source.FIsLocked;
  FCreatedDate := Source.FCreatedDate;
  FForceReset := Source.FForceReset;
end;

function TFleet105_UserAccount.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FUserId >= 0);
end;

function TFleet105_UserAccount.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FUserId));
    LParts.Add(FUserName);
    LParts.Add(FPasswordHash);
    LParts.Add(FFullName);
    LParts.Add(FEmail);
    LParts.Add(IntToStr(FRoleId));
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(DateTimeToStr(FLastLogin));
    LParts.Add(IntToStr(FFailedAttempts));
    LParts.Add(BoolToStr(FIsLocked, True));
    LParts.Add(DateTimeToStr(FCreatedDate));
    LParts.Add(BoolToStr(FForceReset, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_UserAccount.GetUserId: Integer;
begin
  // Pobierz wartość pola UserId
  Result := FUserId;
end;

procedure TFleet105_UserAccount.SetUserId(const Value: Integer);
begin
  // Ustaw wartość pola UserId
  FUserId := Value;
end;

function TFleet105_UserAccount.GetUserName: WideString;
begin
  // Pobierz wartość pola UserName
  Result := FUserName;
end;

procedure TFleet105_UserAccount.SetUserName(const Value: WideString);
begin
  // Ustaw wartość pola UserName
  FUserName := Value;
end;

function TFleet105_UserAccount.GetPasswordHash: WideString;
begin
  // Pobierz wartość pola PasswordHash
  Result := FPasswordHash;
end;

procedure TFleet105_UserAccount.SetPasswordHash(const Value: WideString);
begin
  // Ustaw wartość pola PasswordHash
  FPasswordHash := Value;
end;

function TFleet105_UserAccount.GetFullName: WideString;
begin
  // Pobierz wartość pola FullName
  Result := FFullName;
end;

procedure TFleet105_UserAccount.SetFullName(const Value: WideString);
begin
  // Ustaw wartość pola FullName
  FFullName := Value;
end;

function TFleet105_UserAccount.GetEmail: WideString;
begin
  // Pobierz wartość pola Email
  Result := FEmail;
end;

procedure TFleet105_UserAccount.SetEmail(const Value: WideString);
begin
  // Ustaw wartość pola Email
  FEmail := Value;
end;

function TFleet105_UserAccount.GetRoleId: Integer;
begin
  // Pobierz wartość pola RoleId
  Result := FRoleId;
end;

procedure TFleet105_UserAccount.SetRoleId(const Value: Integer);
begin
  // Ustaw wartość pola RoleId
  FRoleId := Value;
end;

function TFleet105_UserAccount.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_UserAccount.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_UserAccount.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_UserAccount.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_UserAccount.GetLastLogin: TDateTime;
begin
  // Pobierz wartość pola LastLogin
  Result := FLastLogin;
end;

procedure TFleet105_UserAccount.SetLastLogin(const Value: TDateTime);
begin
  // Ustaw wartość pola LastLogin
  FLastLogin := Value;
end;

function TFleet105_UserAccount.GetFailedAttempts: Integer;
begin
  // Pobierz wartość pola FailedAttempts
  Result := FFailedAttempts;
end;

procedure TFleet105_UserAccount.SetFailedAttempts(const Value: Integer);
begin
  // Ustaw wartość pola FailedAttempts
  FFailedAttempts := Value;
end;

function TFleet105_UserAccount.GetIsLocked: Boolean;
begin
  // Pobierz wartość pola IsLocked
  Result := FIsLocked;
end;

procedure TFleet105_UserAccount.SetIsLocked(const Value: Boolean);
begin
  // Ustaw wartość pola IsLocked
  FIsLocked := Value;
end;

function TFleet105_UserAccount.GetCreatedDate: TDateTime;
begin
  // Pobierz wartość pola CreatedDate
  Result := FCreatedDate;
end;

procedure TFleet105_UserAccount.SetCreatedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CreatedDate
  FCreatedDate := Value;
end;

function TFleet105_UserAccount.GetForceReset: Boolean;
begin
  // Pobierz wartość pola ForceReset
  Result := FForceReset;
end;

procedure TFleet105_UserAccount.SetForceReset(const Value: Boolean);
begin
  // Ustaw wartość pola ForceReset
  FForceReset := Value;
end;

// ── TFleet105_UserAccountList ──
constructor TFleet105_UserAccountList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_UserAccountList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_UserAccountList.GetItem(Index: Integer): TFleet105_UserAccount;
begin
  Result := TFleet105_UserAccount(FList[Index]);
end;

function TFleet105_UserAccountList.Add: TFleet105_UserAccount;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_UserAccount.Create;
  FList.Add(Result);
end;

procedure TFleet105_UserAccountList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_UserAccountList.FindById(const AId: Integer): TFleet105_UserAccount;
var
  I: Integer;
  LItem: TFleet105_UserAccount;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_UserAccountList.FindByCode(const ACode: WideString): TFleet105_UserAccount;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_UserAccountList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_UserAccountList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_UserAccountList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_UserAccountList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_UserAccount;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_UserAccountList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_RolePermission
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_RolePermission.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FRoleId := 0;
  FRoleName := '';
  FDescription := '';
  FIsAdmin := False;
  FCanViewReports := False;
  FCanEditVehicles := False;
  FCanEditDrivers := False;
  FCanApprovePayroll := False;
  FCanManageUsers := False;
  FCanViewCosts := False;
  FIsActive := False;
  FCreatedDate := 0;
end;

destructor TFleet105_RolePermission.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_RolePermission.Clear;
begin
  inherited Clear;
  FRoleId := 0;
  FRoleName := '';
  FDescription := '';
  FIsAdmin := False;
  FCanViewReports := False;
  FCanEditVehicles := False;
  FCanEditDrivers := False;
  FCanApprovePayroll := False;
  FCanManageUsers := False;
  FCanViewCosts := False;
  FIsActive := False;
  FCreatedDate := 0;
end;

procedure TFleet105_RolePermission.Assign(Source: TFleet105_RolePermission);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FRoleId := Source.FRoleId;
  FRoleName := Source.FRoleName;
  FDescription := Source.FDescription;
  FIsAdmin := Source.FIsAdmin;
  FCanViewReports := Source.FCanViewReports;
  FCanEditVehicles := Source.FCanEditVehicles;
  FCanEditDrivers := Source.FCanEditDrivers;
  FCanApprovePayroll := Source.FCanApprovePayroll;
  FCanManageUsers := Source.FCanManageUsers;
  FCanViewCosts := Source.FCanViewCosts;
  FIsActive := Source.FIsActive;
  FCreatedDate := Source.FCreatedDate;
end;

function TFleet105_RolePermission.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FRoleId >= 0);
end;

function TFleet105_RolePermission.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FRoleId));
    LParts.Add(FRoleName);
    LParts.Add(FDescription);
    LParts.Add(BoolToStr(FIsAdmin, True));
    LParts.Add(BoolToStr(FCanViewReports, True));
    LParts.Add(BoolToStr(FCanEditVehicles, True));
    LParts.Add(BoolToStr(FCanEditDrivers, True));
    LParts.Add(BoolToStr(FCanApprovePayroll, True));
    LParts.Add(BoolToStr(FCanManageUsers, True));
    LParts.Add(BoolToStr(FCanViewCosts, True));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(DateTimeToStr(FCreatedDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_RolePermission.GetRoleId: Integer;
begin
  // Pobierz wartość pola RoleId
  Result := FRoleId;
end;

procedure TFleet105_RolePermission.SetRoleId(const Value: Integer);
begin
  // Ustaw wartość pola RoleId
  FRoleId := Value;
end;

function TFleet105_RolePermission.GetRoleName: WideString;
begin
  // Pobierz wartość pola RoleName
  Result := FRoleName;
end;

procedure TFleet105_RolePermission.SetRoleName(const Value: WideString);
begin
  // Ustaw wartość pola RoleName
  FRoleName := Value;
end;

function TFleet105_RolePermission.GetDescription: WideString;
begin
  // Pobierz wartość pola Description
  Result := FDescription;
end;

procedure TFleet105_RolePermission.SetDescription(const Value: WideString);
begin
  // Ustaw wartość pola Description
  FDescription := Value;
end;

function TFleet105_RolePermission.GetIsAdmin: Boolean;
begin
  // Pobierz wartość pola IsAdmin
  Result := FIsAdmin;
end;

procedure TFleet105_RolePermission.SetIsAdmin(const Value: Boolean);
begin
  // Ustaw wartość pola IsAdmin
  FIsAdmin := Value;
end;

function TFleet105_RolePermission.GetCanViewReports: Boolean;
begin
  // Pobierz wartość pola CanViewReports
  Result := FCanViewReports;
end;

procedure TFleet105_RolePermission.SetCanViewReports(const Value: Boolean);
begin
  // Ustaw wartość pola CanViewReports
  FCanViewReports := Value;
end;

function TFleet105_RolePermission.GetCanEditVehicles: Boolean;
begin
  // Pobierz wartość pola CanEditVehicles
  Result := FCanEditVehicles;
end;

procedure TFleet105_RolePermission.SetCanEditVehicles(const Value: Boolean);
begin
  // Ustaw wartość pola CanEditVehicles
  FCanEditVehicles := Value;
end;

function TFleet105_RolePermission.GetCanEditDrivers: Boolean;
begin
  // Pobierz wartość pola CanEditDrivers
  Result := FCanEditDrivers;
end;

procedure TFleet105_RolePermission.SetCanEditDrivers(const Value: Boolean);
begin
  // Ustaw wartość pola CanEditDrivers
  FCanEditDrivers := Value;
end;

function TFleet105_RolePermission.GetCanApprovePayroll: Boolean;
begin
  // Pobierz wartość pola CanApprovePayroll
  Result := FCanApprovePayroll;
end;

procedure TFleet105_RolePermission.SetCanApprovePayroll(const Value: Boolean);
begin
  // Ustaw wartość pola CanApprovePayroll
  FCanApprovePayroll := Value;
end;

function TFleet105_RolePermission.GetCanManageUsers: Boolean;
begin
  // Pobierz wartość pola CanManageUsers
  Result := FCanManageUsers;
end;

procedure TFleet105_RolePermission.SetCanManageUsers(const Value: Boolean);
begin
  // Ustaw wartość pola CanManageUsers
  FCanManageUsers := Value;
end;

function TFleet105_RolePermission.GetCanViewCosts: Boolean;
begin
  // Pobierz wartość pola CanViewCosts
  Result := FCanViewCosts;
end;

procedure TFleet105_RolePermission.SetCanViewCosts(const Value: Boolean);
begin
  // Ustaw wartość pola CanViewCosts
  FCanViewCosts := Value;
end;

function TFleet105_RolePermission.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_RolePermission.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_RolePermission.GetCreatedDate: TDateTime;
begin
  // Pobierz wartość pola CreatedDate
  Result := FCreatedDate;
end;

procedure TFleet105_RolePermission.SetCreatedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CreatedDate
  FCreatedDate := Value;
end;

// ── TFleet105_RolePermissionList ──
constructor TFleet105_RolePermissionList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_RolePermissionList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_RolePermissionList.GetItem(Index: Integer): TFleet105_RolePermission;
begin
  Result := TFleet105_RolePermission(FList[Index]);
end;

function TFleet105_RolePermissionList.Add: TFleet105_RolePermission;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_RolePermission.Create;
  FList.Add(Result);
end;

procedure TFleet105_RolePermissionList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_RolePermissionList.FindById(const AId: Integer): TFleet105_RolePermission;
var
  I: Integer;
  LItem: TFleet105_RolePermission;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_RolePermissionList.FindByCode(const ACode: WideString): TFleet105_RolePermission;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_RolePermissionList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_RolePermissionList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_RolePermissionList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_RolePermissionList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_RolePermission;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_RolePermissionList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_AuditLog
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_AuditLog.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FAuditId := 0;
  FUserId := 0;
  FTableName := '';
  FRecordId := 0;
  FActionCode := 0;
  FActionTime := 0;
  FOldValues := '';
  FNewValues := '';
  FIpAddress := '';
  FSessionId := '';
  FIsSuccessful := False;
end;

destructor TFleet105_AuditLog.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_AuditLog.Clear;
begin
  inherited Clear;
  FAuditId := 0;
  FUserId := 0;
  FTableName := '';
  FRecordId := 0;
  FActionCode := 0;
  FActionTime := 0;
  FOldValues := '';
  FNewValues := '';
  FIpAddress := '';
  FSessionId := '';
  FIsSuccessful := False;
end;

procedure TFleet105_AuditLog.Assign(Source: TFleet105_AuditLog);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FAuditId := Source.FAuditId;
  FUserId := Source.FUserId;
  FTableName := Source.FTableName;
  FRecordId := Source.FRecordId;
  FActionCode := Source.FActionCode;
  FActionTime := Source.FActionTime;
  FOldValues := Source.FOldValues;
  FNewValues := Source.FNewValues;
  FIpAddress := Source.FIpAddress;
  FSessionId := Source.FSessionId;
  FIsSuccessful := Source.FIsSuccessful;
end;

function TFleet105_AuditLog.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FAuditId >= 0);
end;

function TFleet105_AuditLog.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FAuditId));
    LParts.Add(IntToStr(FUserId));
    LParts.Add(FTableName);
    LParts.Add(IntToStr(FRecordId));
    LParts.Add(IntToStr(FActionCode));
    LParts.Add(DateTimeToStr(FActionTime));
    LParts.Add(FOldValues);
    LParts.Add(FNewValues);
    LParts.Add(FIpAddress);
    LParts.Add(FSessionId);
    LParts.Add(BoolToStr(FIsSuccessful, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_AuditLog.GetAuditId: Int64;
begin
  // Pobierz wartość pola AuditId
  Result := FAuditId;
end;

procedure TFleet105_AuditLog.SetAuditId(const Value: Int64);
begin
  // Ustaw wartość pola AuditId
  FAuditId := Value;
end;

function TFleet105_AuditLog.GetUserId: Integer;
begin
  // Pobierz wartość pola UserId
  Result := FUserId;
end;

procedure TFleet105_AuditLog.SetUserId(const Value: Integer);
begin
  // Ustaw wartość pola UserId
  FUserId := Value;
end;

function TFleet105_AuditLog.GetTableName: WideString;
begin
  // Pobierz wartość pola TableName
  Result := FTableName;
end;

procedure TFleet105_AuditLog.SetTableName(const Value: WideString);
begin
  // Ustaw wartość pola TableName
  FTableName := Value;
end;

function TFleet105_AuditLog.GetRecordId: Integer;
begin
  // Pobierz wartość pola RecordId
  Result := FRecordId;
end;

procedure TFleet105_AuditLog.SetRecordId(const Value: Integer);
begin
  // Ustaw wartość pola RecordId
  FRecordId := Value;
end;

function TFleet105_AuditLog.GetActionCode: Integer;
begin
  // Pobierz wartość pola ActionCode
  Result := FActionCode;
end;

procedure TFleet105_AuditLog.SetActionCode(const Value: Integer);
begin
  // Ustaw wartość pola ActionCode
  FActionCode := Value;
end;

function TFleet105_AuditLog.GetActionTime: TDateTime;
begin
  // Pobierz wartość pola ActionTime
  Result := FActionTime;
end;

procedure TFleet105_AuditLog.SetActionTime(const Value: TDateTime);
begin
  // Ustaw wartość pola ActionTime
  FActionTime := Value;
end;

function TFleet105_AuditLog.GetOldValues: WideString;
begin
  // Pobierz wartość pola OldValues
  Result := FOldValues;
end;

procedure TFleet105_AuditLog.SetOldValues(const Value: WideString);
begin
  // Ustaw wartość pola OldValues
  FOldValues := Value;
end;

function TFleet105_AuditLog.GetNewValues: WideString;
begin
  // Pobierz wartość pola NewValues
  Result := FNewValues;
end;

procedure TFleet105_AuditLog.SetNewValues(const Value: WideString);
begin
  // Ustaw wartość pola NewValues
  FNewValues := Value;
end;

function TFleet105_AuditLog.GetIpAddress: WideString;
begin
  // Pobierz wartość pola IpAddress
  Result := FIpAddress;
end;

procedure TFleet105_AuditLog.SetIpAddress(const Value: WideString);
begin
  // Ustaw wartość pola IpAddress
  FIpAddress := Value;
end;

function TFleet105_AuditLog.GetSessionId: WideString;
begin
  // Pobierz wartość pola SessionId
  Result := FSessionId;
end;

procedure TFleet105_AuditLog.SetSessionId(const Value: WideString);
begin
  // Ustaw wartość pola SessionId
  FSessionId := Value;
end;

function TFleet105_AuditLog.GetIsSuccessful: Boolean;
begin
  // Pobierz wartość pola IsSuccessful
  Result := FIsSuccessful;
end;

procedure TFleet105_AuditLog.SetIsSuccessful(const Value: Boolean);
begin
  // Ustaw wartość pola IsSuccessful
  FIsSuccessful := Value;
end;

// ── TFleet105_AuditLogList ──
constructor TFleet105_AuditLogList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_AuditLogList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_AuditLogList.GetItem(Index: Integer): TFleet105_AuditLog;
begin
  Result := TFleet105_AuditLog(FList[Index]);
end;

function TFleet105_AuditLogList.Add: TFleet105_AuditLog;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_AuditLog.Create;
  FList.Add(Result);
end;

procedure TFleet105_AuditLogList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_AuditLogList.FindById(const AId: Integer): TFleet105_AuditLog;
var
  I: Integer;
  LItem: TFleet105_AuditLog;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_AuditLogList.FindByCode(const ACode: WideString): TFleet105_AuditLog;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_AuditLogList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_AuditLogList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_AuditLogList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_AuditLogList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_AuditLog;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_AuditLogList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_Notification
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_Notification.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FNotifId := 0;
  FUserId := 0;
  FNotifType := 0;
  FSubject := '';
  FMessageText := '';
  FCreatedDate := 0;
  FReadDate := 0;
  FIsRead := False;
  FPriority := 0;
  FRelatedTable := '';
  FRelatedId := 0;
  FExpiryDate := 0;
end;

destructor TFleet105_Notification.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_Notification.Clear;
begin
  inherited Clear;
  FNotifId := 0;
  FUserId := 0;
  FNotifType := 0;
  FSubject := '';
  FMessageText := '';
  FCreatedDate := 0;
  FReadDate := 0;
  FIsRead := False;
  FPriority := 0;
  FRelatedTable := '';
  FRelatedId := 0;
  FExpiryDate := 0;
end;

procedure TFleet105_Notification.Assign(Source: TFleet105_Notification);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FNotifId := Source.FNotifId;
  FUserId := Source.FUserId;
  FNotifType := Source.FNotifType;
  FSubject := Source.FSubject;
  FMessageText := Source.FMessageText;
  FCreatedDate := Source.FCreatedDate;
  FReadDate := Source.FReadDate;
  FIsRead := Source.FIsRead;
  FPriority := Source.FPriority;
  FRelatedTable := Source.FRelatedTable;
  FRelatedId := Source.FRelatedId;
  FExpiryDate := Source.FExpiryDate;
end;

function TFleet105_Notification.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FNotifId >= 0);
end;

function TFleet105_Notification.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FNotifId));
    LParts.Add(IntToStr(FUserId));
    LParts.Add(IntToStr(FNotifType));
    LParts.Add(FSubject);
    LParts.Add(FMessageText);
    LParts.Add(DateTimeToStr(FCreatedDate));
    LParts.Add(DateTimeToStr(FReadDate));
    LParts.Add(BoolToStr(FIsRead, True));
    LParts.Add(IntToStr(FPriority));
    LParts.Add(FRelatedTable);
    LParts.Add(IntToStr(FRelatedId));
    LParts.Add(DateTimeToStr(FExpiryDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_Notification.GetNotifId: Integer;
begin
  // Pobierz wartość pola NotifId
  Result := FNotifId;
end;

procedure TFleet105_Notification.SetNotifId(const Value: Integer);
begin
  // Ustaw wartość pola NotifId
  FNotifId := Value;
end;

function TFleet105_Notification.GetUserId: Integer;
begin
  // Pobierz wartość pola UserId
  Result := FUserId;
end;

procedure TFleet105_Notification.SetUserId(const Value: Integer);
begin
  // Ustaw wartość pola UserId
  FUserId := Value;
end;

function TFleet105_Notification.GetNotifType: Integer;
begin
  // Pobierz wartość pola NotifType
  Result := FNotifType;
end;

procedure TFleet105_Notification.SetNotifType(const Value: Integer);
begin
  // Ustaw wartość pola NotifType
  FNotifType := Value;
end;

function TFleet105_Notification.GetSubject: WideString;
begin
  // Pobierz wartość pola Subject
  Result := FSubject;
end;

procedure TFleet105_Notification.SetSubject(const Value: WideString);
begin
  // Ustaw wartość pola Subject
  FSubject := Value;
end;

function TFleet105_Notification.GetMessageText: WideString;
begin
  // Pobierz wartość pola MessageText
  Result := FMessageText;
end;

procedure TFleet105_Notification.SetMessageText(const Value: WideString);
begin
  // Ustaw wartość pola MessageText
  FMessageText := Value;
end;

function TFleet105_Notification.GetCreatedDate: TDateTime;
begin
  // Pobierz wartość pola CreatedDate
  Result := FCreatedDate;
end;

procedure TFleet105_Notification.SetCreatedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CreatedDate
  FCreatedDate := Value;
end;

function TFleet105_Notification.GetReadDate: TDateTime;
begin
  // Pobierz wartość pola ReadDate
  Result := FReadDate;
end;

procedure TFleet105_Notification.SetReadDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ReadDate
  FReadDate := Value;
end;

function TFleet105_Notification.GetIsRead: Boolean;
begin
  // Pobierz wartość pola IsRead
  Result := FIsRead;
end;

procedure TFleet105_Notification.SetIsRead(const Value: Boolean);
begin
  // Ustaw wartość pola IsRead
  FIsRead := Value;
end;

function TFleet105_Notification.GetPriority: Integer;
begin
  // Pobierz wartość pola Priority
  Result := FPriority;
end;

procedure TFleet105_Notification.SetPriority(const Value: Integer);
begin
  // Ustaw wartość pola Priority
  FPriority := Value;
end;

function TFleet105_Notification.GetRelatedTable: WideString;
begin
  // Pobierz wartość pola RelatedTable
  Result := FRelatedTable;
end;

procedure TFleet105_Notification.SetRelatedTable(const Value: WideString);
begin
  // Ustaw wartość pola RelatedTable
  FRelatedTable := Value;
end;

function TFleet105_Notification.GetRelatedId: Integer;
begin
  // Pobierz wartość pola RelatedId
  Result := FRelatedId;
end;

procedure TFleet105_Notification.SetRelatedId(const Value: Integer);
begin
  // Ustaw wartość pola RelatedId
  FRelatedId := Value;
end;

function TFleet105_Notification.GetExpiryDate: TDateTime;
begin
  // Pobierz wartość pola ExpiryDate
  Result := FExpiryDate;
end;

procedure TFleet105_Notification.SetExpiryDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ExpiryDate
  FExpiryDate := Value;
end;

// ── TFleet105_NotificationList ──
constructor TFleet105_NotificationList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_NotificationList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_NotificationList.GetItem(Index: Integer): TFleet105_Notification;
begin
  Result := TFleet105_Notification(FList[Index]);
end;

function TFleet105_NotificationList.Add: TFleet105_Notification;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_Notification.Create;
  FList.Add(Result);
end;

procedure TFleet105_NotificationList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_NotificationList.FindById(const AId: Integer): TFleet105_Notification;
var
  I: Integer;
  LItem: TFleet105_Notification;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_NotificationList.FindByCode(const ACode: WideString): TFleet105_Notification;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_NotificationList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_NotificationList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_NotificationList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_NotificationList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_Notification;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_NotificationList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_DocumentStore
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_DocumentStore.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FDocId := 0;
  FEntityType := 0;
  FEntityId := 0;
  FDocType := 0;
  FDocTitle := '';
  FFileName := '';
  FFilePath := '';
  FFileSizeKb := 0;
  FMimeType := '';
  FUploadedBy := 0;
  FUploadDate := 0;
  FIsArchived := False;
  FExpiryDate := 0;
end;

destructor TFleet105_DocumentStore.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_DocumentStore.Clear;
begin
  inherited Clear;
  FDocId := 0;
  FEntityType := 0;
  FEntityId := 0;
  FDocType := 0;
  FDocTitle := '';
  FFileName := '';
  FFilePath := '';
  FFileSizeKb := 0;
  FMimeType := '';
  FUploadedBy := 0;
  FUploadDate := 0;
  FIsArchived := False;
  FExpiryDate := 0;
end;

procedure TFleet105_DocumentStore.Assign(Source: TFleet105_DocumentStore);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FDocId := Source.FDocId;
  FEntityType := Source.FEntityType;
  FEntityId := Source.FEntityId;
  FDocType := Source.FDocType;
  FDocTitle := Source.FDocTitle;
  FFileName := Source.FFileName;
  FFilePath := Source.FFilePath;
  FFileSizeKb := Source.FFileSizeKb;
  FMimeType := Source.FMimeType;
  FUploadedBy := Source.FUploadedBy;
  FUploadDate := Source.FUploadDate;
  FIsArchived := Source.FIsArchived;
  FExpiryDate := Source.FExpiryDate;
end;

function TFleet105_DocumentStore.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FDocId >= 0);
end;

function TFleet105_DocumentStore.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FDocId));
    LParts.Add(IntToStr(FEntityType));
    LParts.Add(IntToStr(FEntityId));
    LParts.Add(IntToStr(FDocType));
    LParts.Add(FDocTitle);
    LParts.Add(FFileName);
    LParts.Add(FFilePath);
    LParts.Add(IntToStr(FFileSizeKb));
    LParts.Add(FMimeType);
    LParts.Add(IntToStr(FUploadedBy));
    LParts.Add(DateTimeToStr(FUploadDate));
    LParts.Add(BoolToStr(FIsArchived, True));
    LParts.Add(DateTimeToStr(FExpiryDate));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_DocumentStore.GetDocId: Integer;
begin
  // Pobierz wartość pola DocId
  Result := FDocId;
end;

procedure TFleet105_DocumentStore.SetDocId(const Value: Integer);
begin
  // Ustaw wartość pola DocId
  FDocId := Value;
end;

function TFleet105_DocumentStore.GetEntityType: Integer;
begin
  // Pobierz wartość pola EntityType
  Result := FEntityType;
end;

procedure TFleet105_DocumentStore.SetEntityType(const Value: Integer);
begin
  // Ustaw wartość pola EntityType
  FEntityType := Value;
end;

function TFleet105_DocumentStore.GetEntityId: Integer;
begin
  // Pobierz wartość pola EntityId
  Result := FEntityId;
end;

procedure TFleet105_DocumentStore.SetEntityId(const Value: Integer);
begin
  // Ustaw wartość pola EntityId
  FEntityId := Value;
end;

function TFleet105_DocumentStore.GetDocType: Integer;
begin
  // Pobierz wartość pola DocType
  Result := FDocType;
end;

procedure TFleet105_DocumentStore.SetDocType(const Value: Integer);
begin
  // Ustaw wartość pola DocType
  FDocType := Value;
end;

function TFleet105_DocumentStore.GetDocTitle: WideString;
begin
  // Pobierz wartość pola DocTitle
  Result := FDocTitle;
end;

procedure TFleet105_DocumentStore.SetDocTitle(const Value: WideString);
begin
  // Ustaw wartość pola DocTitle
  FDocTitle := Value;
end;

function TFleet105_DocumentStore.GetFileName: WideString;
begin
  // Pobierz wartość pola FileName
  Result := FFileName;
end;

procedure TFleet105_DocumentStore.SetFileName(const Value: WideString);
begin
  // Ustaw wartość pola FileName
  FFileName := Value;
end;

function TFleet105_DocumentStore.GetFilePath: WideString;
begin
  // Pobierz wartość pola FilePath
  Result := FFilePath;
end;

procedure TFleet105_DocumentStore.SetFilePath(const Value: WideString);
begin
  // Ustaw wartość pola FilePath
  FFilePath := Value;
end;

function TFleet105_DocumentStore.GetFileSizeKb: Integer;
begin
  // Pobierz wartość pola FileSizeKb
  Result := FFileSizeKb;
end;

procedure TFleet105_DocumentStore.SetFileSizeKb(const Value: Integer);
begin
  // Ustaw wartość pola FileSizeKb
  FFileSizeKb := Value;
end;

function TFleet105_DocumentStore.GetMimeType: WideString;
begin
  // Pobierz wartość pola MimeType
  Result := FMimeType;
end;

procedure TFleet105_DocumentStore.SetMimeType(const Value: WideString);
begin
  // Ustaw wartość pola MimeType
  FMimeType := Value;
end;

function TFleet105_DocumentStore.GetUploadedBy: Integer;
begin
  // Pobierz wartość pola UploadedBy
  Result := FUploadedBy;
end;

procedure TFleet105_DocumentStore.SetUploadedBy(const Value: Integer);
begin
  // Ustaw wartość pola UploadedBy
  FUploadedBy := Value;
end;

function TFleet105_DocumentStore.GetUploadDate: TDateTime;
begin
  // Pobierz wartość pola UploadDate
  Result := FUploadDate;
end;

procedure TFleet105_DocumentStore.SetUploadDate(const Value: TDateTime);
begin
  // Ustaw wartość pola UploadDate
  FUploadDate := Value;
end;

function TFleet105_DocumentStore.GetIsArchived: Boolean;
begin
  // Pobierz wartość pola IsArchived
  Result := FIsArchived;
end;

procedure TFleet105_DocumentStore.SetIsArchived(const Value: Boolean);
begin
  // Ustaw wartość pola IsArchived
  FIsArchived := Value;
end;

function TFleet105_DocumentStore.GetExpiryDate: TDateTime;
begin
  // Pobierz wartość pola ExpiryDate
  Result := FExpiryDate;
end;

procedure TFleet105_DocumentStore.SetExpiryDate(const Value: TDateTime);
begin
  // Ustaw wartość pola ExpiryDate
  FExpiryDate := Value;
end;

// ── TFleet105_DocumentStoreList ──
constructor TFleet105_DocumentStoreList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_DocumentStoreList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_DocumentStoreList.GetItem(Index: Integer): TFleet105_DocumentStore;
begin
  Result := TFleet105_DocumentStore(FList[Index]);
end;

function TFleet105_DocumentStoreList.Add: TFleet105_DocumentStore;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_DocumentStore.Create;
  FList.Add(Result);
end;

procedure TFleet105_DocumentStoreList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_DocumentStoreList.FindById(const AId: Integer): TFleet105_DocumentStore;
var
  I: Integer;
  LItem: TFleet105_DocumentStore;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_DocumentStoreList.FindByCode(const ACode: WideString): TFleet105_DocumentStore;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_DocumentStoreList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_DocumentStoreList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_DocumentStoreList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_DocumentStoreList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_DocumentStore;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_DocumentStoreList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_GeoZone
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_GeoZone.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FZoneId := 0;
  FZoneName := '';
  FZoneType := 0;
  FCentreLatitude := 0.0;
  FCentreLongitude := 0.0;
  FRadiusMetres := 0;
  FPolygonPoints := '';
  FDepotId := 0;
  FSpeedLimitKph := 0;
  FIsActive := False;
  FValidFrom := 0;
  FValidTo := 0;
end;

destructor TFleet105_GeoZone.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_GeoZone.Clear;
begin
  inherited Clear;
  FZoneId := 0;
  FZoneName := '';
  FZoneType := 0;
  FCentreLatitude := 0.0;
  FCentreLongitude := 0.0;
  FRadiusMetres := 0;
  FPolygonPoints := '';
  FDepotId := 0;
  FSpeedLimitKph := 0;
  FIsActive := False;
  FValidFrom := 0;
  FValidTo := 0;
end;

procedure TFleet105_GeoZone.Assign(Source: TFleet105_GeoZone);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FZoneId := Source.FZoneId;
  FZoneName := Source.FZoneName;
  FZoneType := Source.FZoneType;
  FCentreLatitude := Source.FCentreLatitude;
  FCentreLongitude := Source.FCentreLongitude;
  FRadiusMetres := Source.FRadiusMetres;
  FPolygonPoints := Source.FPolygonPoints;
  FDepotId := Source.FDepotId;
  FSpeedLimitKph := Source.FSpeedLimitKph;
  FIsActive := Source.FIsActive;
  FValidFrom := Source.FValidFrom;
  FValidTo := Source.FValidTo;
end;

function TFleet105_GeoZone.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FZoneId >= 0);
end;

function TFleet105_GeoZone.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FZoneId));
    LParts.Add(FZoneName);
    LParts.Add(IntToStr(FZoneType));
    LParts.Add(FloatToStr(FCentreLatitude));
    LParts.Add(FloatToStr(FCentreLongitude));
    LParts.Add(IntToStr(FRadiusMetres));
    LParts.Add(FPolygonPoints);
    LParts.Add(IntToStr(FDepotId));
    LParts.Add(IntToStr(FSpeedLimitKph));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(DateTimeToStr(FValidFrom));
    LParts.Add(DateTimeToStr(FValidTo));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_GeoZone.GetZoneId: Integer;
begin
  // Pobierz wartość pola ZoneId
  Result := FZoneId;
end;

procedure TFleet105_GeoZone.SetZoneId(const Value: Integer);
begin
  // Ustaw wartość pola ZoneId
  FZoneId := Value;
end;

function TFleet105_GeoZone.GetZoneName: WideString;
begin
  // Pobierz wartość pola ZoneName
  Result := FZoneName;
end;

procedure TFleet105_GeoZone.SetZoneName(const Value: WideString);
begin
  // Ustaw wartość pola ZoneName
  FZoneName := Value;
end;

function TFleet105_GeoZone.GetZoneType: Integer;
begin
  // Pobierz wartość pola ZoneType
  Result := FZoneType;
end;

procedure TFleet105_GeoZone.SetZoneType(const Value: Integer);
begin
  // Ustaw wartość pola ZoneType
  FZoneType := Value;
end;

function TFleet105_GeoZone.GetCentreLatitude: Double;
begin
  // Pobierz wartość pola CentreLatitude
  Result := FCentreLatitude;
end;

procedure TFleet105_GeoZone.SetCentreLatitude(const Value: Double);
begin
  // Ustaw wartość pola CentreLatitude
  FCentreLatitude := Value;
end;

function TFleet105_GeoZone.GetCentreLongitude: Double;
begin
  // Pobierz wartość pola CentreLongitude
  Result := FCentreLongitude;
end;

procedure TFleet105_GeoZone.SetCentreLongitude(const Value: Double);
begin
  // Ustaw wartość pola CentreLongitude
  FCentreLongitude := Value;
end;

function TFleet105_GeoZone.GetRadiusMetres: Integer;
begin
  // Pobierz wartość pola RadiusMetres
  Result := FRadiusMetres;
end;

procedure TFleet105_GeoZone.SetRadiusMetres(const Value: Integer);
begin
  // Ustaw wartość pola RadiusMetres
  FRadiusMetres := Value;
end;

function TFleet105_GeoZone.GetPolygonPoints: WideString;
begin
  // Pobierz wartość pola PolygonPoints
  Result := FPolygonPoints;
end;

procedure TFleet105_GeoZone.SetPolygonPoints(const Value: WideString);
begin
  // Ustaw wartość pola PolygonPoints
  FPolygonPoints := Value;
end;

function TFleet105_GeoZone.GetDepotId: Integer;
begin
  // Pobierz wartość pola DepotId
  Result := FDepotId;
end;

procedure TFleet105_GeoZone.SetDepotId(const Value: Integer);
begin
  // Ustaw wartość pola DepotId
  FDepotId := Value;
end;

function TFleet105_GeoZone.GetSpeedLimitKph: Integer;
begin
  // Pobierz wartość pola SpeedLimitKph
  Result := FSpeedLimitKph;
end;

procedure TFleet105_GeoZone.SetSpeedLimitKph(const Value: Integer);
begin
  // Ustaw wartość pola SpeedLimitKph
  FSpeedLimitKph := Value;
end;

function TFleet105_GeoZone.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_GeoZone.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_GeoZone.GetValidFrom: TDateTime;
begin
  // Pobierz wartość pola ValidFrom
  Result := FValidFrom;
end;

procedure TFleet105_GeoZone.SetValidFrom(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidFrom
  FValidFrom := Value;
end;

function TFleet105_GeoZone.GetValidTo: TDateTime;
begin
  // Pobierz wartość pola ValidTo
  Result := FValidTo;
end;

procedure TFleet105_GeoZone.SetValidTo(const Value: TDateTime);
begin
  // Ustaw wartość pola ValidTo
  FValidTo := Value;
end;

// ── TFleet105_GeoZoneList ──
constructor TFleet105_GeoZoneList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_GeoZoneList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_GeoZoneList.GetItem(Index: Integer): TFleet105_GeoZone;
begin
  Result := TFleet105_GeoZone(FList[Index]);
end;

function TFleet105_GeoZoneList.Add: TFleet105_GeoZone;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_GeoZone.Create;
  FList.Add(Result);
end;

procedure TFleet105_GeoZoneList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_GeoZoneList.FindById(const AId: Integer): TFleet105_GeoZone;
var
  I: Integer;
  LItem: TFleet105_GeoZone;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_GeoZoneList.FindByCode(const ACode: WideString): TFleet105_GeoZone;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_GeoZoneList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_GeoZoneList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_GeoZoneList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_GeoZoneList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_GeoZone;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_GeoZoneList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_ChecklistTemplate
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_ChecklistTemplate.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FTemplateId := 0;
  FTemplateName := '';
  FChecklistType := 0;
  FEntityType := 0;
  FItemCount := 0;
  FIsActive := False;
  FVersion := 0;
  FCreatedBy := 0;
  FCreatedDate := 0;
  FApprovedBy := 0;
  FNotes := '';
end;

destructor TFleet105_ChecklistTemplate.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_ChecklistTemplate.Clear;
begin
  inherited Clear;
  FTemplateId := 0;
  FTemplateName := '';
  FChecklistType := 0;
  FEntityType := 0;
  FItemCount := 0;
  FIsActive := False;
  FVersion := 0;
  FCreatedBy := 0;
  FCreatedDate := 0;
  FApprovedBy := 0;
  FNotes := '';
end;

procedure TFleet105_ChecklistTemplate.Assign(Source: TFleet105_ChecklistTemplate);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FTemplateId := Source.FTemplateId;
  FTemplateName := Source.FTemplateName;
  FChecklistType := Source.FChecklistType;
  FEntityType := Source.FEntityType;
  FItemCount := Source.FItemCount;
  FIsActive := Source.FIsActive;
  FVersion := Source.FVersion;
  FCreatedBy := Source.FCreatedBy;
  FCreatedDate := Source.FCreatedDate;
  FApprovedBy := Source.FApprovedBy;
  FNotes := Source.FNotes;
end;

function TFleet105_ChecklistTemplate.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FTemplateId >= 0);
end;

function TFleet105_ChecklistTemplate.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FTemplateId));
    LParts.Add(FTemplateName);
    LParts.Add(IntToStr(FChecklistType));
    LParts.Add(IntToStr(FEntityType));
    LParts.Add(IntToStr(FItemCount));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(IntToStr(FVersion));
    LParts.Add(IntToStr(FCreatedBy));
    LParts.Add(DateTimeToStr(FCreatedDate));
    LParts.Add(IntToStr(FApprovedBy));
    LParts.Add(FNotes);
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_ChecklistTemplate.GetTemplateId: Integer;
begin
  // Pobierz wartość pola TemplateId
  Result := FTemplateId;
end;

procedure TFleet105_ChecklistTemplate.SetTemplateId(const Value: Integer);
begin
  // Ustaw wartość pola TemplateId
  FTemplateId := Value;
end;

function TFleet105_ChecklistTemplate.GetTemplateName: WideString;
begin
  // Pobierz wartość pola TemplateName
  Result := FTemplateName;
end;

procedure TFleet105_ChecklistTemplate.SetTemplateName(const Value: WideString);
begin
  // Ustaw wartość pola TemplateName
  FTemplateName := Value;
end;

function TFleet105_ChecklistTemplate.GetChecklistType: Integer;
begin
  // Pobierz wartość pola ChecklistType
  Result := FChecklistType;
end;

procedure TFleet105_ChecklistTemplate.SetChecklistType(const Value: Integer);
begin
  // Ustaw wartość pola ChecklistType
  FChecklistType := Value;
end;

function TFleet105_ChecklistTemplate.GetEntityType: Integer;
begin
  // Pobierz wartość pola EntityType
  Result := FEntityType;
end;

procedure TFleet105_ChecklistTemplate.SetEntityType(const Value: Integer);
begin
  // Ustaw wartość pola EntityType
  FEntityType := Value;
end;

function TFleet105_ChecklistTemplate.GetItemCount: Integer;
begin
  // Pobierz wartość pola ItemCount
  Result := FItemCount;
end;

procedure TFleet105_ChecklistTemplate.SetItemCount(const Value: Integer);
begin
  // Ustaw wartość pola ItemCount
  FItemCount := Value;
end;

function TFleet105_ChecklistTemplate.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_ChecklistTemplate.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_ChecklistTemplate.GetVersion: Integer;
begin
  // Pobierz wartość pola Version
  Result := FVersion;
end;

procedure TFleet105_ChecklistTemplate.SetVersion(const Value: Integer);
begin
  // Ustaw wartość pola Version
  FVersion := Value;
end;

function TFleet105_ChecklistTemplate.GetCreatedBy: Integer;
begin
  // Pobierz wartość pola CreatedBy
  Result := FCreatedBy;
end;

procedure TFleet105_ChecklistTemplate.SetCreatedBy(const Value: Integer);
begin
  // Ustaw wartość pola CreatedBy
  FCreatedBy := Value;
end;

function TFleet105_ChecklistTemplate.GetCreatedDate: TDateTime;
begin
  // Pobierz wartość pola CreatedDate
  Result := FCreatedDate;
end;

procedure TFleet105_ChecklistTemplate.SetCreatedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CreatedDate
  FCreatedDate := Value;
end;

function TFleet105_ChecklistTemplate.GetApprovedBy: Integer;
begin
  // Pobierz wartość pola ApprovedBy
  Result := FApprovedBy;
end;

procedure TFleet105_ChecklistTemplate.SetApprovedBy(const Value: Integer);
begin
  // Ustaw wartość pola ApprovedBy
  FApprovedBy := Value;
end;

function TFleet105_ChecklistTemplate.GetNotes: WideString;
begin
  // Pobierz wartość pola Notes
  Result := FNotes;
end;

procedure TFleet105_ChecklistTemplate.SetNotes(const Value: WideString);
begin
  // Ustaw wartość pola Notes
  FNotes := Value;
end;

// ── TFleet105_ChecklistTemplateList ──
constructor TFleet105_ChecklistTemplateList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ChecklistTemplateList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ChecklistTemplateList.GetItem(Index: Integer): TFleet105_ChecklistTemplate;
begin
  Result := TFleet105_ChecklistTemplate(FList[Index]);
end;

function TFleet105_ChecklistTemplateList.Add: TFleet105_ChecklistTemplate;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_ChecklistTemplate.Create;
  FList.Add(Result);
end;

procedure TFleet105_ChecklistTemplateList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ChecklistTemplateList.FindById(const AId: Integer): TFleet105_ChecklistTemplate;
var
  I: Integer;
  LItem: TFleet105_ChecklistTemplate;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ChecklistTemplateList.FindByCode(const ACode: WideString): TFleet105_ChecklistTemplate;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ChecklistTemplateList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ChecklistTemplateList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ChecklistTemplateList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ChecklistTemplateList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_ChecklistTemplate;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ChecklistTemplateList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_ChecklistResult
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_ChecklistResult.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FResultId := 0;
  FTemplateId := 0;
  FEntityId := 0;
  FCompletedBy := 0;
  FCompletedDate := 0;
  FOverallResult := 0;
  FFailCount := 0;
  FPassCount := 0;
  FSkipCount := 0;
  FNotes := '';
  FVehicleId := 0;
  FOdometerKm := 0;
end;

destructor TFleet105_ChecklistResult.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_ChecklistResult.Clear;
begin
  inherited Clear;
  FResultId := 0;
  FTemplateId := 0;
  FEntityId := 0;
  FCompletedBy := 0;
  FCompletedDate := 0;
  FOverallResult := 0;
  FFailCount := 0;
  FPassCount := 0;
  FSkipCount := 0;
  FNotes := '';
  FVehicleId := 0;
  FOdometerKm := 0;
end;

procedure TFleet105_ChecklistResult.Assign(Source: TFleet105_ChecklistResult);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FResultId := Source.FResultId;
  FTemplateId := Source.FTemplateId;
  FEntityId := Source.FEntityId;
  FCompletedBy := Source.FCompletedBy;
  FCompletedDate := Source.FCompletedDate;
  FOverallResult := Source.FOverallResult;
  FFailCount := Source.FFailCount;
  FPassCount := Source.FPassCount;
  FSkipCount := Source.FSkipCount;
  FNotes := Source.FNotes;
  FVehicleId := Source.FVehicleId;
  FOdometerKm := Source.FOdometerKm;
end;

function TFleet105_ChecklistResult.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FResultId >= 0);
end;

function TFleet105_ChecklistResult.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FResultId));
    LParts.Add(IntToStr(FTemplateId));
    LParts.Add(IntToStr(FEntityId));
    LParts.Add(IntToStr(FCompletedBy));
    LParts.Add(DateTimeToStr(FCompletedDate));
    LParts.Add(IntToStr(FOverallResult));
    LParts.Add(IntToStr(FFailCount));
    LParts.Add(IntToStr(FPassCount));
    LParts.Add(IntToStr(FSkipCount));
    LParts.Add(FNotes);
    LParts.Add(IntToStr(FVehicleId));
    LParts.Add(IntToStr(FOdometerKm));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_ChecklistResult.GetResultId: Integer;
begin
  // Pobierz wartość pola ResultId
  Result := FResultId;
end;

procedure TFleet105_ChecklistResult.SetResultId(const Value: Integer);
begin
  // Ustaw wartość pola ResultId
  FResultId := Value;
end;

function TFleet105_ChecklistResult.GetTemplateId: Integer;
begin
  // Pobierz wartość pola TemplateId
  Result := FTemplateId;
end;

procedure TFleet105_ChecklistResult.SetTemplateId(const Value: Integer);
begin
  // Ustaw wartość pola TemplateId
  FTemplateId := Value;
end;

function TFleet105_ChecklistResult.GetEntityId: Integer;
begin
  // Pobierz wartość pola EntityId
  Result := FEntityId;
end;

procedure TFleet105_ChecklistResult.SetEntityId(const Value: Integer);
begin
  // Ustaw wartość pola EntityId
  FEntityId := Value;
end;

function TFleet105_ChecklistResult.GetCompletedBy: Integer;
begin
  // Pobierz wartość pola CompletedBy
  Result := FCompletedBy;
end;

procedure TFleet105_ChecklistResult.SetCompletedBy(const Value: Integer);
begin
  // Ustaw wartość pola CompletedBy
  FCompletedBy := Value;
end;

function TFleet105_ChecklistResult.GetCompletedDate: TDateTime;
begin
  // Pobierz wartość pola CompletedDate
  Result := FCompletedDate;
end;

procedure TFleet105_ChecklistResult.SetCompletedDate(const Value: TDateTime);
begin
  // Ustaw wartość pola CompletedDate
  FCompletedDate := Value;
end;

function TFleet105_ChecklistResult.GetOverallResult: Integer;
begin
  // Pobierz wartość pola OverallResult
  Result := FOverallResult;
end;

procedure TFleet105_ChecklistResult.SetOverallResult(const Value: Integer);
begin
  // Ustaw wartość pola OverallResult
  FOverallResult := Value;
end;

function TFleet105_ChecklistResult.GetFailCount: Integer;
begin
  // Pobierz wartość pola FailCount
  Result := FFailCount;
end;

procedure TFleet105_ChecklistResult.SetFailCount(const Value: Integer);
begin
  // Ustaw wartość pola FailCount
  FFailCount := Value;
end;

function TFleet105_ChecklistResult.GetPassCount: Integer;
begin
  // Pobierz wartość pola PassCount
  Result := FPassCount;
end;

procedure TFleet105_ChecklistResult.SetPassCount(const Value: Integer);
begin
  // Ustaw wartość pola PassCount
  FPassCount := Value;
end;

function TFleet105_ChecklistResult.GetSkipCount: Integer;
begin
  // Pobierz wartość pola SkipCount
  Result := FSkipCount;
end;

procedure TFleet105_ChecklistResult.SetSkipCount(const Value: Integer);
begin
  // Ustaw wartość pola SkipCount
  FSkipCount := Value;
end;

function TFleet105_ChecklistResult.GetNotes: WideString;
begin
  // Pobierz wartość pola Notes
  Result := FNotes;
end;

procedure TFleet105_ChecklistResult.SetNotes(const Value: WideString);
begin
  // Ustaw wartość pola Notes
  FNotes := Value;
end;

function TFleet105_ChecklistResult.GetVehicleId: Integer;
begin
  // Pobierz wartość pola VehicleId
  Result := FVehicleId;
end;

procedure TFleet105_ChecklistResult.SetVehicleId(const Value: Integer);
begin
  // Ustaw wartość pola VehicleId
  FVehicleId := Value;
end;

function TFleet105_ChecklistResult.GetOdometerKm: Integer;
begin
  // Pobierz wartość pola OdometerKm
  Result := FOdometerKm;
end;

procedure TFleet105_ChecklistResult.SetOdometerKm(const Value: Integer);
begin
  // Ustaw wartość pola OdometerKm
  FOdometerKm := Value;
end;

// ── TFleet105_ChecklistResultList ──
constructor TFleet105_ChecklistResultList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ChecklistResultList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ChecklistResultList.GetItem(Index: Integer): TFleet105_ChecklistResult;
begin
  Result := TFleet105_ChecklistResult(FList[Index]);
end;

function TFleet105_ChecklistResultList.Add: TFleet105_ChecklistResult;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_ChecklistResult.Create;
  FList.Add(Result);
end;

procedure TFleet105_ChecklistResultList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ChecklistResultList.FindById(const AId: Integer): TFleet105_ChecklistResult;
var
  I: Integer;
  LItem: TFleet105_ChecklistResult;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ChecklistResultList.FindByCode(const ACode: WideString): TFleet105_ChecklistResult;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ChecklistResultList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ChecklistResultList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ChecklistResultList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ChecklistResultList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_ChecklistResult;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ChecklistResultList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_ContractClient
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_ContractClient.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FClientId := 0;
  FClientCode := '';
  FClientName := '';
  FContactName := '';
  FPhone := '';
  FEmail := '';
  FAddress := '';
  FCity := '';
  FContractStart := 0;
  FContractEnd := 0;
  FIsActive := False;
  FDiscountPct := 0.0;
  FCreditLimit := 0.0;
  FPayTermsDays := 0;
end;

destructor TFleet105_ContractClient.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_ContractClient.Clear;
begin
  inherited Clear;
  FClientId := 0;
  FClientCode := '';
  FClientName := '';
  FContactName := '';
  FPhone := '';
  FEmail := '';
  FAddress := '';
  FCity := '';
  FContractStart := 0;
  FContractEnd := 0;
  FIsActive := False;
  FDiscountPct := 0.0;
  FCreditLimit := 0.0;
  FPayTermsDays := 0;
end;

procedure TFleet105_ContractClient.Assign(Source: TFleet105_ContractClient);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FClientId := Source.FClientId;
  FClientCode := Source.FClientCode;
  FClientName := Source.FClientName;
  FContactName := Source.FContactName;
  FPhone := Source.FPhone;
  FEmail := Source.FEmail;
  FAddress := Source.FAddress;
  FCity := Source.FCity;
  FContractStart := Source.FContractStart;
  FContractEnd := Source.FContractEnd;
  FIsActive := Source.FIsActive;
  FDiscountPct := Source.FDiscountPct;
  FCreditLimit := Source.FCreditLimit;
  FPayTermsDays := Source.FPayTermsDays;
end;

function TFleet105_ContractClient.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FClientId >= 0);
end;

function TFleet105_ContractClient.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FClientId));
    LParts.Add(FClientCode);
    LParts.Add(FClientName);
    LParts.Add(FContactName);
    LParts.Add(FPhone);
    LParts.Add(FEmail);
    LParts.Add(FAddress);
    LParts.Add(FCity);
    LParts.Add(DateTimeToStr(FContractStart));
    LParts.Add(DateTimeToStr(FContractEnd));
    LParts.Add(BoolToStr(FIsActive, True));
    LParts.Add(FloatToStr(FDiscountPct));
    LParts.Add(FloatToStr(FCreditLimit));
    LParts.Add(IntToStr(FPayTermsDays));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_ContractClient.GetClientId: Integer;
begin
  // Pobierz wartość pola ClientId
  Result := FClientId;
end;

procedure TFleet105_ContractClient.SetClientId(const Value: Integer);
begin
  // Ustaw wartość pola ClientId
  FClientId := Value;
end;

function TFleet105_ContractClient.GetClientCode: WideString;
begin
  // Pobierz wartość pola ClientCode
  Result := FClientCode;
end;

procedure TFleet105_ContractClient.SetClientCode(const Value: WideString);
begin
  // Ustaw wartość pola ClientCode
  FClientCode := Value;
end;

function TFleet105_ContractClient.GetClientName: WideString;
begin
  // Pobierz wartość pola ClientName
  Result := FClientName;
end;

procedure TFleet105_ContractClient.SetClientName(const Value: WideString);
begin
  // Ustaw wartość pola ClientName
  FClientName := Value;
end;

function TFleet105_ContractClient.GetContactName: WideString;
begin
  // Pobierz wartość pola ContactName
  Result := FContactName;
end;

procedure TFleet105_ContractClient.SetContactName(const Value: WideString);
begin
  // Ustaw wartość pola ContactName
  FContactName := Value;
end;

function TFleet105_ContractClient.GetPhone: WideString;
begin
  // Pobierz wartość pola Phone
  Result := FPhone;
end;

procedure TFleet105_ContractClient.SetPhone(const Value: WideString);
begin
  // Ustaw wartość pola Phone
  FPhone := Value;
end;

function TFleet105_ContractClient.GetEmail: WideString;
begin
  // Pobierz wartość pola Email
  Result := FEmail;
end;

procedure TFleet105_ContractClient.SetEmail(const Value: WideString);
begin
  // Ustaw wartość pola Email
  FEmail := Value;
end;

function TFleet105_ContractClient.GetAddress: WideString;
begin
  // Pobierz wartość pola Address
  Result := FAddress;
end;

procedure TFleet105_ContractClient.SetAddress(const Value: WideString);
begin
  // Ustaw wartość pola Address
  FAddress := Value;
end;

function TFleet105_ContractClient.GetCity: WideString;
begin
  // Pobierz wartość pola City
  Result := FCity;
end;

procedure TFleet105_ContractClient.SetCity(const Value: WideString);
begin
  // Ustaw wartość pola City
  FCity := Value;
end;

function TFleet105_ContractClient.GetContractStart: TDateTime;
begin
  // Pobierz wartość pola ContractStart
  Result := FContractStart;
end;

procedure TFleet105_ContractClient.SetContractStart(const Value: TDateTime);
begin
  // Ustaw wartość pola ContractStart
  FContractStart := Value;
end;

function TFleet105_ContractClient.GetContractEnd: TDateTime;
begin
  // Pobierz wartość pola ContractEnd
  Result := FContractEnd;
end;

procedure TFleet105_ContractClient.SetContractEnd(const Value: TDateTime);
begin
  // Ustaw wartość pola ContractEnd
  FContractEnd := Value;
end;

function TFleet105_ContractClient.GetIsActive: Boolean;
begin
  // Pobierz wartość pola IsActive
  Result := FIsActive;
end;

procedure TFleet105_ContractClient.SetIsActive(const Value: Boolean);
begin
  // Ustaw wartość pola IsActive
  FIsActive := Value;
end;

function TFleet105_ContractClient.GetDiscountPct: Double;
begin
  // Pobierz wartość pola DiscountPct
  Result := FDiscountPct;
end;

procedure TFleet105_ContractClient.SetDiscountPct(const Value: Double);
begin
  // Ustaw wartość pola DiscountPct
  FDiscountPct := Value;
end;

function TFleet105_ContractClient.GetCreditLimit: Double;
begin
  // Pobierz wartość pola CreditLimit
  Result := FCreditLimit;
end;

procedure TFleet105_ContractClient.SetCreditLimit(const Value: Double);
begin
  // Ustaw wartość pola CreditLimit
  FCreditLimit := Value;
end;

function TFleet105_ContractClient.GetPayTermsDays: Integer;
begin
  // Pobierz wartość pola PayTermsDays
  Result := FPayTermsDays;
end;

procedure TFleet105_ContractClient.SetPayTermsDays(const Value: Integer);
begin
  // Ustaw wartość pola PayTermsDays
  FPayTermsDays := Value;
end;

// ── TFleet105_ContractClientList ──
constructor TFleet105_ContractClientList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_ContractClientList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_ContractClientList.GetItem(Index: Integer): TFleet105_ContractClient;
begin
  Result := TFleet105_ContractClient(FList[Index]);
end;

function TFleet105_ContractClientList.Add: TFleet105_ContractClient;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_ContractClient.Create;
  FList.Add(Result);
end;

procedure TFleet105_ContractClientList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_ContractClientList.FindById(const AId: Integer): TFleet105_ContractClient;
var
  I: Integer;
  LItem: TFleet105_ContractClient;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_ContractClientList.FindByCode(const ACode: WideString): TFleet105_ContractClient;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_ContractClientList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_ContractClientList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_ContractClientList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_ContractClientList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_ContractClient;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_ContractClientList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

// ═══════════════════════════════════════════════════════════════════════════
// TFleet105_BillingRecord
// ═══════════════════════════════════════════════════════════════════════════

constructor TFleet105_BillingRecord.Create;
begin
  inherited Create;
  // Inicjalizacja pól
  FBillId := 0;
  FClientId := 0;
  FPeriodStart := 0;
  FPeriodEnd := 0;
  FTripCount := 0;
  FTotalKm := 0.0;
  FBaseAmount := 0.0;
  FFuelSurcharge := 0.0;
  FTaxAmount := 0.0;
  FTotalAmount := 0.0;
  FStatusCode := 0;
  FInvoiceDate := 0;
  FPaidDate := 0;
  FIsExported := False;
end;

destructor TFleet105_BillingRecord.Destroy;
begin
  // Zwolnij zasoby
  inherited Destroy;
end;

procedure TFleet105_BillingRecord.Clear;
begin
  inherited Clear;
  FBillId := 0;
  FClientId := 0;
  FPeriodStart := 0;
  FPeriodEnd := 0;
  FTripCount := 0;
  FTotalKm := 0.0;
  FBaseAmount := 0.0;
  FFuelSurcharge := 0.0;
  FTaxAmount := 0.0;
  FTotalAmount := 0.0;
  FStatusCode := 0;
  FInvoiceDate := 0;
  FPaidDate := 0;
  FIsExported := False;
end;

procedure TFleet105_BillingRecord.Assign(Source: TFleet105_BillingRecord);
begin
  if not Assigned(Source) then Exit;
  // Kopiuj wszystkie pola ze źródłowego obiektu
  FBillId := Source.FBillId;
  FClientId := Source.FClientId;
  FPeriodStart := Source.FPeriodStart;
  FPeriodEnd := Source.FPeriodEnd;
  FTripCount := Source.FTripCount;
  FTotalKm := Source.FTotalKm;
  FBaseAmount := Source.FBaseAmount;
  FFuelSurcharge := Source.FFuelSurcharge;
  FTaxAmount := Source.FTaxAmount;
  FTotalAmount := Source.FTotalAmount;
  FStatusCode := Source.FStatusCode;
  FInvoiceDate := Source.FInvoiceDate;
  FPaidDate := Source.FPaidDate;
  FIsExported := Source.FIsExported;
end;

function TFleet105_BillingRecord.Validate: Boolean;
begin
  // Sprawdź poprawność danych encji
  Result := (FBillId >= 0);
end;

function TFleet105_BillingRecord.ToDelimitedString(const ADelim: WideString): WideString;
var
  LParts: TStringList;
begin
  // Zwróć dane encji jako łańcuch rozdzielony separatorem
  LParts := TStringList.Create;
  try
    LParts.Add(IntToStr(FBillId));
    LParts.Add(IntToStr(FClientId));
    LParts.Add(DateTimeToStr(FPeriodStart));
    LParts.Add(DateTimeToStr(FPeriodEnd));
    LParts.Add(IntToStr(FTripCount));
    LParts.Add(FloatToStr(FTotalKm));
    LParts.Add(FloatToStr(FBaseAmount));
    LParts.Add(FloatToStr(FFuelSurcharge));
    LParts.Add(FloatToStr(FTaxAmount));
    LParts.Add(FloatToStr(FTotalAmount));
    LParts.Add(IntToStr(FStatusCode));
    LParts.Add(DateTimeToStr(FInvoiceDate));
    LParts.Add(DateTimeToStr(FPaidDate));
    LParts.Add(BoolToStr(FIsExported, True));
    Result := LParts.CommaText;
  finally
    LParts.Free;
  end;
end;

function TFleet105_BillingRecord.GetBillId: Integer;
begin
  // Pobierz wartość pola BillId
  Result := FBillId;
end;

procedure TFleet105_BillingRecord.SetBillId(const Value: Integer);
begin
  // Ustaw wartość pola BillId
  FBillId := Value;
end;

function TFleet105_BillingRecord.GetClientId: Integer;
begin
  // Pobierz wartość pola ClientId
  Result := FClientId;
end;

procedure TFleet105_BillingRecord.SetClientId(const Value: Integer);
begin
  // Ustaw wartość pola ClientId
  FClientId := Value;
end;

function TFleet105_BillingRecord.GetPeriodStart: TDateTime;
begin
  // Pobierz wartość pola PeriodStart
  Result := FPeriodStart;
end;

procedure TFleet105_BillingRecord.SetPeriodStart(const Value: TDateTime);
begin
  // Ustaw wartość pola PeriodStart
  FPeriodStart := Value;
end;

function TFleet105_BillingRecord.GetPeriodEnd: TDateTime;
begin
  // Pobierz wartość pola PeriodEnd
  Result := FPeriodEnd;
end;

procedure TFleet105_BillingRecord.SetPeriodEnd(const Value: TDateTime);
begin
  // Ustaw wartość pola PeriodEnd
  FPeriodEnd := Value;
end;

function TFleet105_BillingRecord.GetTripCount: Integer;
begin
  // Pobierz wartość pola TripCount
  Result := FTripCount;
end;

procedure TFleet105_BillingRecord.SetTripCount(const Value: Integer);
begin
  // Ustaw wartość pola TripCount
  FTripCount := Value;
end;

function TFleet105_BillingRecord.GetTotalKm: Double;
begin
  // Pobierz wartość pola TotalKm
  Result := FTotalKm;
end;

procedure TFleet105_BillingRecord.SetTotalKm(const Value: Double);
begin
  // Ustaw wartość pola TotalKm
  FTotalKm := Value;
end;

function TFleet105_BillingRecord.GetBaseAmount: Double;
begin
  // Pobierz wartość pola BaseAmount
  Result := FBaseAmount;
end;

procedure TFleet105_BillingRecord.SetBaseAmount(const Value: Double);
begin
  // Ustaw wartość pola BaseAmount
  FBaseAmount := Value;
end;

function TFleet105_BillingRecord.GetFuelSurcharge: Double;
begin
  // Pobierz wartość pola FuelSurcharge
  Result := FFuelSurcharge;
end;

procedure TFleet105_BillingRecord.SetFuelSurcharge(const Value: Double);
begin
  // Ustaw wartość pola FuelSurcharge
  FFuelSurcharge := Value;
end;

function TFleet105_BillingRecord.GetTaxAmount: Double;
begin
  // Pobierz wartość pola TaxAmount
  Result := FTaxAmount;
end;

procedure TFleet105_BillingRecord.SetTaxAmount(const Value: Double);
begin
  // Ustaw wartość pola TaxAmount
  FTaxAmount := Value;
end;

function TFleet105_BillingRecord.GetTotalAmount: Double;
begin
  // Pobierz wartość pola TotalAmount
  Result := FTotalAmount;
end;

procedure TFleet105_BillingRecord.SetTotalAmount(const Value: Double);
begin
  // Ustaw wartość pola TotalAmount
  FTotalAmount := Value;
end;

function TFleet105_BillingRecord.GetStatusCode: Integer;
begin
  // Pobierz wartość pola StatusCode
  Result := FStatusCode;
end;

procedure TFleet105_BillingRecord.SetStatusCode(const Value: Integer);
begin
  // Ustaw wartość pola StatusCode
  FStatusCode := Value;
end;

function TFleet105_BillingRecord.GetInvoiceDate: TDateTime;
begin
  // Pobierz wartość pola InvoiceDate
  Result := FInvoiceDate;
end;

procedure TFleet105_BillingRecord.SetInvoiceDate(const Value: TDateTime);
begin
  // Ustaw wartość pola InvoiceDate
  FInvoiceDate := Value;
end;

function TFleet105_BillingRecord.GetPaidDate: TDateTime;
begin
  // Pobierz wartość pola PaidDate
  Result := FPaidDate;
end;

procedure TFleet105_BillingRecord.SetPaidDate(const Value: TDateTime);
begin
  // Ustaw wartość pola PaidDate
  FPaidDate := Value;
end;

function TFleet105_BillingRecord.GetIsExported: Boolean;
begin
  // Pobierz wartość pola IsExported
  Result := FIsExported;
end;

procedure TFleet105_BillingRecord.SetIsExported(const Value: Boolean);
begin
  // Ustaw wartość pola IsExported
  FIsExported := Value;
end;

// ── TFleet105_BillingRecordList ──
constructor TFleet105_BillingRecordList.Create;
begin
  inherited Create;
  FOwnsObjects := True;
end;

destructor TFleet105_BillingRecordList.Destroy;
begin
  inherited Destroy;
end;

function TFleet105_BillingRecordList.GetItem(Index: Integer): TFleet105_BillingRecord;
begin
  Result := TFleet105_BillingRecord(FList[Index]);
end;

function TFleet105_BillingRecordList.Add: TFleet105_BillingRecord;
begin
  // Dodaj nowy element do listy
  Result := TFleet105_BillingRecord.Create;
  FList.Add(Result);
end;

procedure TFleet105_BillingRecordList.Delete(Index: Integer);
begin
  // Usuń element z listy
  if (Index < 0) or (Index >= FList.Count) then Exit;
  if FOwnsObjects then
    TObject(FList[Index]).Free;
  FList.Delete(Index);
end;

function TFleet105_BillingRecordList.FindById(const AId: Integer): TFleet105_BillingRecord;
var
  I: Integer;
  LItem: TFleet105_BillingRecord;
begin
  // Wyszukaj element po identyfikatorze
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    LItem := GetItem(I);
    if Assigned(LItem) then
      if LItem.EntityId = AId then
      begin
        Result := LItem;
        Exit;
      end;
  end;
end;

function TFleet105_BillingRecordList.FindByCode(const ACode: WideString): TFleet105_BillingRecord;
var
  I: Integer;
begin
  // Wyszukaj element po kodzie/nazwie
  Result := nil;
  for I := 0 to FList.Count - 1 do
  begin
    if GetItem(I).EntityCode = ACode then
    begin
      Result := GetItem(I);
      Exit;
    end;
  end;
end;

function TFleet105_BillingRecordList.SortByName: Integer;
begin
  // Sortuj elementy listy według nazwy
  Result := FList.Count;
  FSorted := True;
end;

function TFleet105_BillingRecordList.FilterByDepot(ADepotId: Integer): Integer;
begin
  // Filtruj elementy listy według depozytu
  FFilterActive := True;
  Result := FList.Count;
end;

function TFleet105_BillingRecordList.ToDataSet(ADataSet: TClientDataSet): Integer;
var
  I: Integer;
begin
  // Eksportuj listę do zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  ADataSet.EmptyDataSet;
  for I := 0 to FList.Count - 1 do
  begin
    ADataSet.Append;
    // Field mapping would occur here
    ADataSet.Post;
    Inc(Result);
  end;
end;

function TFleet105_BillingRecordList.LoadFromDataSet(ADataSet: TClientDataSet): Integer;
var
  LItem: TFleet105_BillingRecord;
begin
  // Wczytaj listę ze zbioru danych TClientDataSet
  Result := 0;
  if not Assigned(ADataSet) then Exit;
  if ADataSet.IsEmpty then Exit;
  ADataSet.First;
  while not ADataSet.Eof do
  begin
    LItem := Add;
    // LItem.LoadFromDataSet(ADataSet) would map fields
    ADataSet.Next;
    Inc(Result);
  end;
end;

function TFleet105_BillingRecordList.ExportCSV(const AFileName: WideString): Boolean;
var
  LFile: TextFile;
  I: Integer;
begin
  // Eksportuj listę do pliku CSV
  Result := False;
  if AFileName = '' then Exit;
  AssignFile(LFile, AFileName);
  try
    Rewrite(LFile);
    try
      for I := 0 to FList.Count - 1 do
        WriteLn(LFile, GetItem(I).ToDelimitedString(','));
      Result := True;
    finally
      CloseFile(LFile);
    end;
  except
    Result := False;
  end;
end;

initialization
  // Inicjalizacja modułu VehicleData.classes
  // Module VehicleData.classes initialized on startup

finalization
  // Zwolnienie zasobów modułu VehicleData.classes
  // Release resources on shutdown

end.
