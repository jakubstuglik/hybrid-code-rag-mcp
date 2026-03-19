// ************************************************************************ //
// The types declared in this file were generated from data read from the
// WSDL File described below:
// WSDL     : http://fleet-api.internal:8080/services/FleetWebService?wsdl
//  >Import : http://fleet-api.internal:8080/services/FleetWebService?wsdl>0
//  >Import : http://fleet-api.internal:8080/services/FleetWebService?xsd=services.xsd
// Encoding : UTF-8
// Version  : 1.0
// (2023-09-18 14:22:07 - $Rev: 10234 $)
// ************************************************************************ //

unit WebApiService;

interface

uses InvokeRegistry, SOAPHTTPClient, Types, XSBuiltIns;

const
  IS_OPTN = $0001;
  IS_UNBD = $0002;
  IS_ATTR = $0010;
  IS_REF  = $0080;


type

  // ************************************************************************ //
  // The following types are SOAP-generated stubs for the FleetOps web service.
  // They provide access to vehicle tracking, job dispatch, and driver management
  // endpoints over HTTP/SOAP transport.
  // ************************************************************************ //
  // !:dateTime        - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:string          - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:boolean         - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:long            - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:float           - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:int             - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:double          - "http://www.w3.org/2001/XMLSchema"[Gbl]

  FWSVehiclePosition   = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSDriverInfo        = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSJobOrder          = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSJobOrderItem      = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSRouteSegment      = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSGeoCoordinate     = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSDispatchParams    = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSVehicleSearchParams = class; { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSEnumParam         = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSFuelRecord        = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSMaintenanceRecord = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSPaymentDetails    = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSDriverPaySummary  = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSVehicleStatus     = class;   { "http://fleet-api.internal:8080/services"[Cplx] }
  FWSCredential        = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSSessionToken      = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSUserInfo          = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSAlertRecord       = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSReportRequest     = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSReportResult      = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSZoneDefinition    = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSZonePoint         = class;   { "http://fleet-api.internal:8080/services"[Cplx] }
  FWSDepotInfo         = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSCallbackParams    = class;   { "http://fleet-api.internal:8080/services"[GblCplx] }
  FWSBatchJobRequest   = class;   { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSNoSuchVehicle     = class;   { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSNoSuchDriver      = class;   { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSNoSuchJob         = class;   { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSAuthFailed        = class;   { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSJobAlreadyAssigned = class;  { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }
  FWSVehicleOverCapacity = class; { "http://fleet-api.internal:8080/services/FleetWebService"[Flt][GblElm] }

  {$SCOPEDENUMS ON}
  { "http://fleet-api.internal:8080/services"[Smpl] }
  vehicleType = (VT_TRUCK, VT_VAN, VT_MOTORCYCLE, VT_TRACTOR, VT_TRAILER, VT_BUS, VT_MINIBUS);

  { "http://fleet-api.internal:8080/services"[Smpl] }
  jobStatus = (JS_PENDING, JS_ASSIGNED, JS_IN_PROGRESS, JS_COMPLETED, JS_CANCELLED, JS_FAILED);

  { "http://fleet-api.internal:8080/services"[Smpl] }
  driverStatus = (DS_AVAILABLE, DS_ON_DUTY, DS_OFF_DUTY, DS_SICK_LEAVE, DS_VACATION);

  { "http://fleet-api.internal:8080/services"[Smpl] }
  alertSeverity = (AS_INFO, AS_WARNING, AS_CRITICAL, AS_EMERGENCY);

  { "http://fleet-api.internal:8080/services"[Smpl] }
  reportType = (RT_MILEAGE, RT_FUEL, RT_DRIVER_PAY, RT_MAINTENANCE, RT_UTILIZATION, RT_EXCEPTION);

  { "http://fleet-api.internal:8080/services"[Smpl] }
  faultCode = (FC_VEHICLE_OFFLINE, FC_ROUTE_IMPASSABLE, FC_FUEL_LOW, FC_DRIVER_OVERTIME);

  { "http://fleet-api.internal:8080/services/FleetWebService"[Smpl] }
  authFault = (AF_INVALID_CREDENTIALS, AF_SESSION_EXPIRED, AF_ACCOUNT_LOCKED, AF_INSUFFICIENT_PRIVILEGES);

  { "http://fleet-api.internal:8080/services/FleetWebService"[Smpl] }
  jobFault = (JF_JOB_NOT_FOUND, JF_ALREADY_ASSIGNED, JF_OVER_CAPACITY, JF_ROUTE_UNAVAILABLE);
  {$SCOPEDENUMS OFF}


  // ************************************************************************ //
  // XML       : FWSGeoCoordinate, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSGeoCoordinate = class(TRemotable)
  private
    FLatitude: Double;
    FLongitude: Double;
    FAltitude: Double;
    FAltitude_Specified: boolean;
    FAccuracy: Single;
    FAccuracy_Specified: boolean;
    FTimestamp: TXSDateTime;
    FTimestamp_Specified: boolean;
    procedure SetAltitude(Index: Integer; const ADouble: Double);
    function  Altitude_Specified(Index: Integer): boolean;
    procedure SetAccuracy(Index: Integer; const ASingle: Single);
    function  Accuracy_Specified(Index: Integer): boolean;
    procedure SetTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  Timestamp_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property Latitude:  Double       Index (IS_ATTR) read FLatitude write FLatitude;
    property Longitude: Double       Index (IS_ATTR) read FLongitude write FLongitude;
    property Altitude:  Double       Index (IS_ATTR or IS_OPTN) read FAltitude write SetAltitude stored Altitude_Specified;
    property Accuracy:  Single       Index (IS_ATTR or IS_OPTN) read FAccuracy write SetAccuracy stored Accuracy_Specified;
    property Timestamp: TXSDateTime  Index (IS_OPTN) read FTimestamp write SetTimestamp stored Timestamp_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSVehiclePosition, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSVehiclePosition = class(TRemotable)
  private
    FVehicleId: Int64;
    FRegistrationPlate: string;
    FRegistrationPlate_Specified: boolean;
    FPosition: FWSGeoCoordinate;
    FPosition_Specified: boolean;
    FSpeedKmh: Single;
    FSpeedKmh_Specified: boolean;
    FHeading: Integer;
    FHeading_Specified: boolean;
    FCurrentJobId: Int64;
    FCurrentJobId_Specified: boolean;
    FDriverId: Int64;
    FDriverId_Specified: boolean;
    FEngineOn: Boolean;
    FMileageKm: Double;
    FMileageKm_Specified: boolean;
    FLastUpdate: TXSDateTime;
    FLastUpdate_Specified: boolean;
    procedure SetRegistrationPlate(Index: Integer; const Astring: string);
    function  RegistrationPlate_Specified(Index: Integer): boolean;
    procedure SetPosition(Index: Integer; const AFWSGeoCoordinate: FWSGeoCoordinate);
    function  Position_Specified(Index: Integer): boolean;
    procedure SetSpeedKmh(Index: Integer; const ASingle: Single);
    function  SpeedKmh_Specified(Index: Integer): boolean;
    procedure SetHeading(Index: Integer; const AInteger: Integer);
    function  Heading_Specified(Index: Integer): boolean;
    procedure SetCurrentJobId(Index: Integer; const AInt64: Int64);
    function  CurrentJobId_Specified(Index: Integer): boolean;
    procedure SetDriverId(Index: Integer; const AInt64: Int64);
    function  DriverId_Specified(Index: Integer): boolean;
    procedure SetMileageKm(Index: Integer; const ADouble: Double);
    function  MileageKm_Specified(Index: Integer): boolean;
    procedure SetLastUpdate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  LastUpdate_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property VehicleId:        Int64             Index (IS_ATTR) read FVehicleId write FVehicleId;
    property RegistrationPlate: string           Index (IS_OPTN) read FRegistrationPlate write SetRegistrationPlate stored RegistrationPlate_Specified;
    property Position:          FWSGeoCoordinate Index (IS_OPTN) read FPosition write SetPosition stored Position_Specified;
    property SpeedKmh:          Single           Index (IS_ATTR or IS_OPTN) read FSpeedKmh write SetSpeedKmh stored SpeedKmh_Specified;
    property Heading:           Integer          Index (IS_ATTR or IS_OPTN) read FHeading write SetHeading stored Heading_Specified;
    property CurrentJobId:      Int64            Index (IS_ATTR or IS_OPTN) read FCurrentJobId write SetCurrentJobId stored CurrentJobId_Specified;
    property DriverId:          Int64            Index (IS_ATTR or IS_OPTN) read FDriverId write SetDriverId stored DriverId_Specified;
    property EngineOn:          Boolean          Index (IS_ATTR) read FEngineOn write FEngineOn;
    property MileageKm:         Double           Index (IS_ATTR or IS_OPTN) read FMileageKm write SetMileageKm stored MileageKm_Specified;
    property LastUpdate:        TXSDateTime      Index (IS_OPTN) read FLastUpdate write SetLastUpdate stored LastUpdate_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSDriverInfo, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSDriverInfo = class(TRemotable)
  private
    FDriverId: Int64;
    FEmployeeCode: string;
    FEmployeeCode_Specified: boolean;
    FFirstName: string;
    FFirstName_Specified: boolean;
    FLastName: string;
    FLastName_Specified: boolean;
    FLicenceNumber: string;
    FLicenceNumber_Specified: boolean;
    FLicenceExpiry: TXSDateTime;
    FLicenceExpiry_Specified: boolean;
    FLicenceCategories: string;
    FLicenceCategories_Specified: boolean;
    FContactPhone: string;
    FContactPhone_Specified: boolean;
    FStatus: FWSEnumParam;
    FStatus_Specified: boolean;
    FCurrentVehicleId: Int64;
    FCurrentVehicleId_Specified: boolean;
    procedure SetEmployeeCode(Index: Integer; const Astring: string);
    function  EmployeeCode_Specified(Index: Integer): boolean;
    procedure SetFirstName(Index: Integer; const Astring: string);
    function  FirstName_Specified(Index: Integer): boolean;
    procedure SetLastName(Index: Integer; const Astring: string);
    function  LastName_Specified(Index: Integer): boolean;
    procedure SetLicenceNumber(Index: Integer; const Astring: string);
    function  LicenceNumber_Specified(Index: Integer): boolean;
    procedure SetLicenceExpiry(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  LicenceExpiry_Specified(Index: Integer): boolean;
    procedure SetLicenceCategories(Index: Integer; const Astring: string);
    function  LicenceCategories_Specified(Index: Integer): boolean;
    procedure SetContactPhone(Index: Integer; const Astring: string);
    function  ContactPhone_Specified(Index: Integer): boolean;
    procedure SetStatus(Index: Integer; const AFWSEnumParam: FWSEnumParam);
    function  Status_Specified(Index: Integer): boolean;
    procedure SetCurrentVehicleId(Index: Integer; const AInt64: Int64);
    function  CurrentVehicleId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property DriverId:          Int64         Index (IS_ATTR) read FDriverId write FDriverId;
    property EmployeeCode:      string        Index (IS_OPTN) read FEmployeeCode write SetEmployeeCode stored EmployeeCode_Specified;
    property FirstName:         string        Index (IS_OPTN) read FFirstName write SetFirstName stored FirstName_Specified;
    property LastName:          string        Index (IS_OPTN) read FLastName write SetLastName stored LastName_Specified;
    property LicenceNumber:     string        Index (IS_OPTN) read FLicenceNumber write SetLicenceNumber stored LicenceNumber_Specified;
    property LicenceExpiry:     TXSDateTime   Index (IS_ATTR or IS_OPTN) read FLicenceExpiry write SetLicenceExpiry stored LicenceExpiry_Specified;
    property LicenceCategories: string        Index (IS_OPTN) read FLicenceCategories write SetLicenceCategories stored LicenceCategories_Specified;
    property ContactPhone:      string        Index (IS_OPTN) read FContactPhone write SetContactPhone stored ContactPhone_Specified;
    property Status:            FWSEnumParam  Index (IS_OPTN) read FStatus write SetStatus stored Status_Specified;
    property CurrentVehicleId:  Int64         Index (IS_ATTR or IS_OPTN) read FCurrentVehicleId write SetCurrentVehicleId stored CurrentVehicleId_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSJobOrder, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSJobOrder = class(TRemotable)
  private
    FJobId: Int64;
    FJobReference: string;
    FJobReference_Specified: boolean;
    FOriginAddress: string;
    FOriginAddress_Specified: boolean;
    FDestAddress: string;
    FDestAddress_Specified: boolean;
    FOriginCoords: FWSGeoCoordinate;
    FOriginCoords_Specified: boolean;
    FDestCoords: FWSGeoCoordinate;
    FDestCoords_Specified: boolean;
    FScheduledPickup: TXSDateTime;
    FScheduledPickup_Specified: boolean;
    FScheduledDelivery: TXSDateTime;
    FScheduledDelivery_Specified: boolean;
    FPayloadKg: Double;
    FPayloadKg_Specified: boolean;
    FPayloadDescription: string;
    FPayloadDescription_Specified: boolean;
    FStatus: FWSEnumParam;
    FStatus_Specified: boolean;
    FAssignedVehicleId: Int64;
    FAssignedVehicleId_Specified: boolean;
    FAssignedDriverId: Int64;
    FAssignedDriverId_Specified: boolean;
    FCustomerRef: string;
    FCustomerRef_Specified: boolean;
    FPriority: Integer;
    FNotes: string;
    FNotes_Specified: boolean;
    procedure SetJobReference(Index: Integer; const Astring: string);
    function  JobReference_Specified(Index: Integer): boolean;
    procedure SetOriginAddress(Index: Integer; const Astring: string);
    function  OriginAddress_Specified(Index: Integer): boolean;
    procedure SetDestAddress(Index: Integer; const Astring: string);
    function  DestAddress_Specified(Index: Integer): boolean;
    procedure SetOriginCoords(Index: Integer; const AFWS: FWSGeoCoordinate);
    function  OriginCoords_Specified(Index: Integer): boolean;
    procedure SetDestCoords(Index: Integer; const AFWS: FWSGeoCoordinate);
    function  DestCoords_Specified(Index: Integer): boolean;
    procedure SetScheduledPickup(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  ScheduledPickup_Specified(Index: Integer): boolean;
    procedure SetScheduledDelivery(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  ScheduledDelivery_Specified(Index: Integer): boolean;
    procedure SetPayloadKg(Index: Integer; const ADouble: Double);
    function  PayloadKg_Specified(Index: Integer): boolean;
    procedure SetPayloadDescription(Index: Integer; const Astring: string);
    function  PayloadDescription_Specified(Index: Integer): boolean;
    procedure SetStatus(Index: Integer; const AFWSEnumParam: FWSEnumParam);
    function  Status_Specified(Index: Integer): boolean;
    procedure SetAssignedVehicleId(Index: Integer; const AInt64: Int64);
    function  AssignedVehicleId_Specified(Index: Integer): boolean;
    procedure SetAssignedDriverId(Index: Integer; const AInt64: Int64);
    function  AssignedDriverId_Specified(Index: Integer): boolean;
    procedure SetCustomerRef(Index: Integer; const Astring: string);
    function  CustomerRef_Specified(Index: Integer): boolean;
    procedure SetNotes(Index: Integer; const Astring: string);
    function  Notes_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property JobId:             Int64            Index (IS_ATTR) read FJobId write FJobId;
    property JobReference:      string           Index (IS_OPTN) read FJobReference write SetJobReference stored JobReference_Specified;
    property OriginAddress:     string           Index (IS_OPTN) read FOriginAddress write SetOriginAddress stored OriginAddress_Specified;
    property DestAddress:       string           Index (IS_OPTN) read FDestAddress write SetDestAddress stored DestAddress_Specified;
    property OriginCoords:      FWSGeoCoordinate Index (IS_OPTN) read FOriginCoords write SetOriginCoords stored OriginCoords_Specified;
    property DestCoords:        FWSGeoCoordinate Index (IS_OPTN) read FDestCoords write SetDestCoords stored DestCoords_Specified;
    property ScheduledPickup:   TXSDateTime      Index (IS_ATTR or IS_OPTN) read FScheduledPickup write SetScheduledPickup stored ScheduledPickup_Specified;
    property ScheduledDelivery: TXSDateTime      Index (IS_ATTR or IS_OPTN) read FScheduledDelivery write SetScheduledDelivery stored ScheduledDelivery_Specified;
    property PayloadKg:         Double           Index (IS_ATTR or IS_OPTN) read FPayloadKg write SetPayloadKg stored PayloadKg_Specified;
    property PayloadDescription: string          Index (IS_OPTN) read FPayloadDescription write SetPayloadDescription stored PayloadDescription_Specified;
    property Status:            FWSEnumParam     Index (IS_OPTN) read FStatus write SetStatus stored Status_Specified;
    property AssignedVehicleId: Int64            Index (IS_ATTR or IS_OPTN) read FAssignedVehicleId write SetAssignedVehicleId stored AssignedVehicleId_Specified;
    property AssignedDriverId:  Int64            Index (IS_ATTR or IS_OPTN) read FAssignedDriverId write SetAssignedDriverId stored AssignedDriverId_Specified;
    property CustomerRef:       string           Index (IS_OPTN) read FCustomerRef write SetCustomerRef stored CustomerRef_Specified;
    property Priority:          Integer          Index (IS_ATTR) read FPriority write FPriority;
    property Notes:             string           Index (IS_OPTN) read FNotes write SetNotes stored Notes_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSEnumParam, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSEnumParam = class(TRemotable)
  private
    FCode: string;
    FCode_Specified: boolean;
    FCaption: string;
    FCaption_Specified: boolean;
    procedure SetCode(Index: Integer; const Astring: string);
    function  Code_Specified(Index: Integer): boolean;
    procedure SetCaption(Index: Integer; const Astring: string);
    function  Caption_Specified(Index: Integer): boolean;
  published
    property Code:    string  Index (IS_OPTN) read FCode write SetCode stored Code_Specified;
    property Caption: string  Index (IS_OPTN) read FCaption write SetCaption stored Caption_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSCredential, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSCredential = class(TRemotable)
  private
    FUsername: string;
    FUsername_Specified: boolean;
    FPasswordHash: string;
    FPasswordHash_Specified: boolean;
    FApiKey: string;
    FApiKey_Specified: boolean;
    procedure SetUsername(Index: Integer; const Astring: string);
    function  Username_Specified(Index: Integer): boolean;
    procedure SetPasswordHash(Index: Integer; const Astring: string);
    function  PasswordHash_Specified(Index: Integer): boolean;
    procedure SetApiKey(Index: Integer; const Astring: string);
    function  ApiKey_Specified(Index: Integer): boolean;
  published
    property Username:     string  Index (IS_OPTN) read FUsername write SetUsername stored Username_Specified;
    property PasswordHash: string  Index (IS_OPTN) read FPasswordHash write SetPasswordHash stored PasswordHash_Specified;
    property ApiKey:       string  Index (IS_OPTN) read FApiKey write SetApiKey stored ApiKey_Specified;
  end;


  // ************************************************************************ //
  // XML       : FWSSessionToken, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSSessionToken = class(TRemotable)
  private
    FToken: string;
    FToken_Specified: boolean;
    FExpiresAt: TXSDateTime;
    FExpiresAt_Specified: boolean;
    FUserId: Int64;
    procedure SetToken(Index: Integer; const Astring: string);
    function  Token_Specified(Index: Integer): boolean;
    procedure SetExpiresAt(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  ExpiresAt_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property Token:     string      Index (IS_OPTN) read FToken write SetToken stored Token_Specified;
    property ExpiresAt: TXSDateTime Index (IS_ATTR or IS_OPTN) read FExpiresAt write SetExpiresAt stored ExpiresAt_Specified;
    property UserId:    Int64       Index (IS_ATTR) read FUserId write FUserId;
  end;


  // ************************************************************************ //
  // XML       : FWSFuelRecord, global, <complexType>
  // Namespace : http://fleet-api.internal:8080/services
  // ************************************************************************ //
  FWSFuelRecord = class(TRemotable)
  private
    FRecordId: Int64;
    FVehicleId: Int64;
    FDriverId: Int64;
    FDriverId_Specified: boolean;
    FFuelDate: TXSDateTime;
    FFuelDate_Specified: boolean;
    FLitres: Double;
    FLitres_Specified: boolean;
    FCostPerLitre: Double;
    FCostPerLitre_Specified: boolean;
    FTotalCost: Double;
    FTotalCost_Specified: boolean;
    FOdometerKm: Double;
    FOdometerKm_Specified: boolean;
    FFuelType: string;
    FFuelType_Specified: boolean;
    FStationName: string;
    FStationName_Specified: boolean;
    procedure SetDriverId(Index: Integer; const AInt64: Int64);
    function  DriverId_Specified(Index: Integer): boolean;
    procedure SetFuelDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  FuelDate_Specified(Index: Integer): boolean;
    procedure SetLitres(Index: Integer; const ADouble: Double);
    function  Litres_Specified(Index: Integer): boolean;
    procedure SetCostPerLitre(Index: Integer; const ADouble: Double);
    function  CostPerLitre_Specified(Index: Integer): boolean;
    procedure SetTotalCost(Index: Integer; const ADouble: Double);
    function  TotalCost_Specified(Index: Integer): boolean;
    procedure SetOdometerKm(Index: Integer; const ADouble: Double);
    function  OdometerKm_Specified(Index: Integer): boolean;
    procedure SetFuelType(Index: Integer; const Astring: string);
    function  FuelType_Specified(Index: Integer): boolean;
    procedure SetStationName(Index: Integer; const Astring: string);
    function  StationName_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property RecordId:     Int64        Index (IS_ATTR) read FRecordId write FRecordId;
    property VehicleId:    Int64        Index (IS_ATTR) read FVehicleId write FVehicleId;
    property DriverId:     Int64        Index (IS_ATTR or IS_OPTN) read FDriverId write SetDriverId stored DriverId_Specified;
    property FuelDate:     TXSDateTime  Index (IS_ATTR or IS_OPTN) read FFuelDate write SetFuelDate stored FuelDate_Specified;
    property Litres:       Double       Index (IS_ATTR or IS_OPTN) read FLitres write SetLitres stored Litres_Specified;
    property CostPerLitre: Double       Index (IS_ATTR or IS_OPTN) read FCostPerLitre write SetCostPerLitre stored CostPerLitre_Specified;
    property TotalCost:    Double       Index (IS_ATTR or IS_OPTN) read FTotalCost write SetTotalCost stored TotalCost_Specified;
    property OdometerKm:   Double       Index (IS_ATTR or IS_OPTN) read FOdometerKm write SetOdometerKm stored OdometerKm_Specified;
    property FuelType:     string       Index (IS_OPTN) read FFuelType write SetFuelType stored FuelType_Specified;
    property StationName:  string       Index (IS_OPTN) read FStationName write SetStationName stored StationName_Specified;
  end;


  // ************************************************************************ //
  // Service interface for FleetWebService
  // Namespace : http://fleet-api.internal:8080/services/FleetWebService
  // ************************************************************************ //
  IFleetWebService = interface(IInvokable)
    ['{E9A0B1C2-D3E4-F5A6-B7C8-D9E0F1A2B3C4}']

    { Authentication operations }
    function  Login(const Credentials: FWSCredential): FWSSessionToken; stdcall;
    procedure Logout(const Token: string); stdcall;
    function  RefreshToken(const Token: string): FWSSessionToken; stdcall;

    { Vehicle tracking operations }
    function  GetVehiclePosition(const Token: string; const VehicleId: Int64): FWSVehiclePosition; stdcall;
    function  GetAllVehiclePositions(const Token: string): FWSVehiclePosition; stdcall;
    function  GetVehiclesInZone(const Token: string; const Zone: FWSZoneDefinition): FWSVehiclePosition; stdcall;

    { Job dispatch operations }
    function  CreateJobOrder(const Token: string; const Job: FWSJobOrder): Int64; stdcall;
    procedure AssignJobToVehicle(const Token: string; const JobId: Int64; const VehicleId: Int64; const DriverId: Int64); stdcall;
    procedure UpdateJobStatus(const Token: string; const JobId: Int64; const NewStatus: FWSEnumParam); stdcall;
    function  GetJobOrder(const Token: string; const JobId: Int64): FWSJobOrder; stdcall;
    function  GetPendingJobs(const Token: string): FWSJobOrder; stdcall;

    { Driver management operations }
    function  GetDriverInfo(const Token: string; const DriverId: Int64): FWSDriverInfo; stdcall;
    function  GetAvailableDrivers(const Token: string): FWSDriverInfo; stdcall;
    procedure UpdateDriverStatus(const Token: string; const DriverId: Int64; const Status: FWSEnumParam); stdcall;

    { Fuel and maintenance operations }
    function  RecordFuelFill(const Token: string; const Record_: FWSFuelRecord): Int64; stdcall;
    function  GetFuelHistory(const Token: string; const VehicleId: Int64; const FromDate: TXSDateTime; const ToDate: TXSDateTime): FWSFuelRecord; stdcall;
    function  RecordMaintenance(const Token: string; const Record_: FWSMaintenanceRecord): Int64; stdcall;

    { Reporting operations }
    function  GenerateReport(const Token: string; const Request: FWSReportRequest): FWSReportResult; stdcall;
  end;

implementation

initialization
  InvRegistry.RegisterInterface(TypeInfo(IFleetWebService));
  InvRegistry.RegisterDefaultSOAPAction(TypeInfo(IFleetWebService),
    'http://fleet-api.internal:8080/services/FleetWebService');
  RemClassRegistry.RegisterXSClass(FWSVehiclePosition, 'http://fleet-api.internal:8080/services', 'FWSVehiclePosition');
  RemClassRegistry.RegisterXSClass(FWSDriverInfo, 'http://fleet-api.internal:8080/services', 'FWSDriverInfo');
  RemClassRegistry.RegisterXSClass(FWSJobOrder, 'http://fleet-api.internal:8080/services', 'FWSJobOrder');
  RemClassRegistry.RegisterXSClass(FWSGeoCoordinate, 'http://fleet-api.internal:8080/services', 'FWSGeoCoordinate');
  RemClassRegistry.RegisterXSClass(FWSEnumParam, 'http://fleet-api.internal:8080/services', 'FWSEnumParam');
  RemClassRegistry.RegisterXSClass(FWSFuelRecord, 'http://fleet-api.internal:8080/services', 'FWSFuelRecord');
  RemClassRegistry.RegisterXSClass(FWSCredential, 'http://fleet-api.internal:8080/services', 'FWSCredential');
  RemClassRegistry.RegisterXSClass(FWSSessionToken, 'http://fleet-api.internal:8080/services', 'FWSSessionToken');

end.
