// ************************************************************************ //
// The types declared in this file were generated from data read from the
// WSDL File described below:
// WSDL     : http://83.15.136.94:54321/axis2/services/PWebService?wsdl
//  >Import : http://83.15.136.94:54321/axis2/services/PWebService?wsdl>0
//  >Import : http://83.15.136.94:54321/axis2/services/PWebService?xsd=services.xsd
// Encoding : UTF-8
// Version  : 1.0
// (4/25/2014 9:58:15 AM - - $Rev: 25127 $)
// ************************************************************************ //

unit PWebService;

interface

uses InvokeRegistry, SOAPHTTPClient, Types, XSBuiltIns;

const
  IS_OPTN = $0001;
  IS_UNBD = $0002;
  IS_ATTR = $0010;
  IS_REF  = $0080;


type

  // ************************************************************************ //
  // The following types, referred to in the WSDL document are not being represented
  // in this file. They are either aliases[@] of other types represented or were referred
  // to but never[!] declared in the document. The types from the latter category
  // typically map to predefined/known XML or Embarcadero types; however, they could also 
  // indicate incorrect WSDL documents that failed to declare or import a schema type.
  // ************************************************************************ //
  // !:dateTime        - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:string          - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:boolean         - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:long            - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:float           - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:int             - "http://www.w3.org/2001/XMLSchema"[Gbl]
  // !:double          - "http://www.w3.org/2001/XMLSchema"[Gbl]

  PTiStopInTime        = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSUserCreateParams  = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTTSearchingParams = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSEnumParam         = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiDiscount        = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiTariffPriceAfterDiscount = class;        { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiDocType         = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSStop              = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCostForPeriod     = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCarrierId         = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiOrderWithCustomerData = class;           { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiHolderForTicket = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  place                = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  periodicTicket       = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiPeriodicCardIdentyfier = class;          { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiSendingData     = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  customerData         = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSMessage           = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSFullyQualifiedStop = class;                { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSFullyQualifiedCity = class;                { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSInformicaCarrier  = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSNamePrincipal     = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSConnSearchingDetails = class;              { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  holder               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiPeriodicTicketInfo = class;              { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  section              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiBusCourse       = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSConnection        = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  type_2               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  passenger            = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSPasswordCredential = class;                { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSSessionIdPrincipal = class;                { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSUserInfo          = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSStopInTime        = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  param                = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSFullyQualifiedCityExt = class;             { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSVehiclePosition   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSVehicle           = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiReservationId   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiVendingParams   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSStick             = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  stickId              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSInfKurs           = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSChangeUserDataParams = class;              { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSRelation          = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  price                = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  country              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PTiHolderForTicket   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  role                 = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiReservationCancelInfo = class;           { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  discount             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSWebServiceUser    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiReservationDone = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSRelationParams    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCarrierDetails    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCarrier           = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  card                 = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  address              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiSendTicketInfo  = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  relation             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSStopInTimeForTimeTable = class;            { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  price2               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  country2             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiSendTicketFormat = class;                { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  opinion              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSWaypoint          = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  driver               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  reservation          = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  payer                = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  place2               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  connection           = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiStopInTime      = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  holder2              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSCityId            = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  listOfRecord         = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  param2               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSMessageFromDriver = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  carrierType2         = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  discount2            = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PTiPlace             = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  connection2          = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  holder3              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiVendingEvent    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  stickId2             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiSellingReport2  = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSEmptyTimeTable    = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSMoreThanOneCarrier = class;                { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSStops             = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoSuchRecording   = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoSuchCarrier     = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSTiVendingParams2  = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSChangeUserData    = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSChangePassword    = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNotYourUser       = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoSuchInfCarrier  = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoSuchInfCourse   = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoConn            = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSNoVehicle         = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSCreateUser        = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSLogin             = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSTiCommitResrvation = class;                { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  placesNumsBounds     = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  cause3               = class;                 { "http://83.15.136.94:54321/axis2/services"[Alias] }
  sit                  = class;                 { "http://83.15.136.94:54321/axis2/services"[Alias] }
  stick                = class;                 { "http://83.15.136.94:54321/axis2/services"[Alias] }
  connId               = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Alias] }
  carrierid            = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Alias] }
  vehicle              = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Alias] }
  PWSTiSellingData     = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  sellingDataForStick  = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiTariffForStick  = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCosts             = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCarrierSearcherParams = class;             { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  order                = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  ticket               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSFullyQualifiedCityWithStops = class;       { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  lineStop             = class;                 { "http://83.15.136.94:54321/axis2/services"[Alias] }
  cityStop             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiPeriodicTicketLineInfo = class;          { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiSendNormalTicketData = class;            { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  placeCause           = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiTicketUnavailableFaultData = class;      { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSGetStopParam      = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  cityName             = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Alias] }
  PWSTiReservationCancelRange = class;          { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSSearchingParams   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiWebServiceUserSellingConfig = class;     { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  carriers             = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiSearchingResultWithSellingData = class;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  result2              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  stick2               = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  holdersForStick      = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  ticket2              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  holder4              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSCarrierLines      = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  machineConfig        = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSUser              = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  stickDiscount        = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSCarrierRelations  = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTimeTable         = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  departure            = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PTiTariffForStick    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTrackRecording    = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiDetailedReservation = class;             { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  ticket3              = class;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSResultPriceDetailsParams = class;          { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSSearchingResult   = class;                 { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSTiSendTickets     = class;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSTiOrderUnavailable = class;                { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }

  {$SCOPEDENUMS ON}
  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  type_ = (
      AUT_NORMAL, 
      AUT_FAST, 
      AUT_FASTER, 
      AUT_EXPRESS, 
      POC_OSOBOWY, 
      POC_POSP, 
      POC_TLK, 
      POC_INTERR, 
      POC_EX, 
      POC_IC, 
      POC_EC, 
      POC_ICE, 
      POC_AUT, 
      POC_EURON, 
      POC_MPN, 
      POC_KKZ, 
      POC_RE, 
      POC_ICEURO2012, 
      POC_MUSICREGIO, 
      POC_IRBUS, 
      POC_SPEC, 
      POC_REGIO, 
      NORMAL, 
      FAST, 
      FASTER, 
      EXPRESS
  );

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  version = (VER_1_0, VER_1_1, VER_1_2);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  docType = (ID, PASSPORT, DRIVING_LICENCE, STUDENT_ID, INTERNATIONAL_PASSPORT, INTERNATIONAL_ID, INTERNATIONAL_DRIVING_LICENCE);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  optimizationMode = (DURATION, PRICE, DEPARTURE_TIME, OPINIONS);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  carrierType = (ALL, MINIBUS, COACH, RAIL);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  tariffType = (PASSENGER, LAGGUAGE);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  roundType = (NO_ROUNDING, T5GR_ROUNDING, T10GR_ROUNDING, T5GR_CUTDOWN, T10GR_CUTDOWN, BOUNDED_ROUNDING);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  cancelState = (NEW, TRANSFER_DEFINED, TRANSFER_DONE, UNKNOWN);

  { "http://83.15.136.94:54321/axis2/services"[Smpl] }
  defaultSendingType = (SMS, EMAIL, PAPER);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault = (TIMETABLE_EMPTY);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault2 = (NO_MATCHING_CITIES, NO_STOPS_IN_CITIES);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  cause2 = (CONNECTION_NOT_EXISTS, CONNECTION_UNAVAILABLE_FOR_DATE, CONNECTION_UNAVAILABLE_FOR_SELLING, INF_NR_KURSU_NOT_UNIQUE);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault3 = (USER_EXISTS);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault4 = (PASSWORD_NOT_EQUAL);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault5 = (NO_CONNECTIONS_FOUND);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault6 = (USER_EXISTS, PASSWORDS_NOT_EQUAL);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  fault7 = (ACCOUNT_EXPIRED, ACCOUNT_LOCKED, ACCOUNT_NOT_FOUND, INCORRECT_CREDENTIAL, INSUFFICENT_PRIVILEGES, UNKNOWN);

  { "http://83.15.136.94:54321/axis2/services/PWebService"[Smpl] }
  error = (
      GETCONN_FROM_STOP_ID_NO_STOP, 
      GETCONN_TO_STOP_ID_NO_STOP, 
      GETCONN_FROM_CITY_ID_NO_CITY, 
      GETCONN_TO_CITY_ID_NO_CITY, 
      GETCONN_FROM_TO_REQUIRED, 
      GETCONN_TIME_REQUIRED, 
      GETCONN_OFFSET_LE_GT, 
      GETCONN_MAXIMAL_NUMBER_CHANGES_LE_GT, 
      GETCONN_MINIMAL_TIME_CHANGE_LE_GT, 
      GETCONN_MAXIMAL_TIME_CHANGE_LE_GT, 
      GETTT_STOP_ID_NO_STOP, 
      GETTT_CARRIER_ID_NO_CARRIER, 
      GETSTOPS_CITY_NAME_TOO_SHORT, 
      GETSTOPS_CITY_ID_REQUIRED, 
      VENDING_MACHINE_LOCKED, 
      VENDING_MACHINE_WRONG_FROM_STOP, 
      VENDING_MACHINE_CASH_LOCKED, 
      VENDING_MACHINE_NOT_CASH_NOT_CARD, 
      VENDING_MACHINE_CARD_LOCKED, 
      VENDING_MACHINE_NORMAL_TICKET_LOCKED, 
      VENDING_MACHINE_TICKET_MANAGEMENT_LOCKED
  );

  {$SCOPEDENUMS OFF}



  // ************************************************************************ //
  // XML       : PTiStopInTime, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PTiStopInTime = class(TRemotable)
  private
    FarrivalTime: TXSDateTime;
    FarrivalTime_Specified: boolean;
    FdepartureTime: TXSDateTime;
    FdepartureTime_Specified: boolean;
    FstopName: string;
    FstopName_Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    FcommuneName: string;
    FcommuneName_Specified: boolean;
    FdistrictName: string;
    FdistrictName_Specified: boolean;
    FprovinceName: string;
    FprovinceName_Specified: boolean;
    FcountryName: string;
    FcountryName_Specified: boolean;
    procedure SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  arrivalTime_Specified(Index: Integer): boolean;
    procedure SetdepartureTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  departureTime_Specified(Index: Integer): boolean;
    procedure SetstopName(Index: Integer; const Astring: string);
    function  stopName_Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
    procedure SetcommuneName(Index: Integer; const Astring: string);
    function  communeName_Specified(Index: Integer): boolean;
    procedure SetdistrictName(Index: Integer; const Astring: string);
    function  districtName_Specified(Index: Integer): boolean;
    procedure SetprovinceName(Index: Integer; const Astring: string);
    function  provinceName_Specified(Index: Integer): boolean;
    procedure SetcountryName(Index: Integer; const Astring: string);
    function  countryName_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property arrivalTime:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FarrivalTime write SetarrivalTime stored arrivalTime_Specified;
    property departureTime: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdepartureTime write SetdepartureTime stored departureTime_Specified;
    property stopName:      string       Index (IS_OPTN) read FstopName write SetstopName stored stopName_Specified;
    property cityName:      string       Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
    property communeName:   string       Index (IS_OPTN) read FcommuneName write SetcommuneName stored communeName_Specified;
    property districtName:  string       Index (IS_OPTN) read FdistrictName write SetdistrictName stored districtName_Specified;
    property provinceName:  string       Index (IS_OPTN) read FprovinceName write SetprovinceName stored provinceName_Specified;
    property countryName:   string       Index (IS_OPTN) read FcountryName write SetcountryName stored countryName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSUserCreateParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSUserCreateParams = class(TRemotable)
  private
    Fblocked: Boolean;
    Fblocked_Specified: boolean;
    FvalidFrom: TXSDateTime;
    FvalidFrom_Specified: boolean;
    FvalidTo: TXSDateTime;
    FvalidTo_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    Flogin: string;
    Flogin_Specified: boolean;
    Fpassword: string;
    Fpassword_Specified: boolean;
    Fpassword2: string;
    Fpassword2_Specified: boolean;
    procedure Setblocked(Index: Integer; const ABoolean: Boolean);
    function  blocked_Specified(Index: Integer): boolean;
    procedure SetvalidFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validFrom_Specified(Index: Integer): boolean;
    procedure SetvalidTo(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validTo_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
    procedure Setlogin(Index: Integer; const Astring: string);
    function  login_Specified(Index: Integer): boolean;
    procedure Setpassword(Index: Integer; const Astring: string);
    function  password_Specified(Index: Integer): boolean;
    procedure Setpassword2(Index: Integer; const Astring: string);
    function  password2_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property blocked:   Boolean      Index (IS_ATTR or IS_OPTN) read Fblocked write Setblocked stored blocked_Specified;
    property validFrom: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidFrom write SetvalidFrom stored validFrom_Specified;
    property validTo:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidTo write SetvalidTo stored validTo_Specified;
    property forename:  string       Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:   string       Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property phone:     string       Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property email:     string       Index (IS_OPTN) read Femail write Setemail stored email_Specified;
    property login:     string       Index (IS_OPTN) read Flogin write Setlogin stored login_Specified;
    property password:  string       Index (IS_OPTN) read Fpassword write Setpassword stored password_Specified;
    property password2: string       Index (IS_OPTN) read Fpassword2 write Setpassword2 stored password2_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTTSearchingParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTTSearchingParams = class(TRemotable)
  private
    FcarrierTypeId: Int64;
    FcarrierTypeId_Specified: boolean;
    FcarrierId: Int64;
    FcarrierId_Specified: boolean;
    FstopId: Int64;
    FfromTime: TXSDateTime;
    FfromTime_Specified: boolean;
    FtoTime: TXSDateTime;
    FtoTime_Specified: boolean;
    Fdate: TXSDateTime;
    Fdate_Specified: boolean;
    FfilterCode: string;
    FfilterCode_Specified: boolean;
    procedure SetcarrierTypeId(Index: Integer; const AInt64: Int64);
    function  carrierTypeId_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const AInt64: Int64);
    function  carrierId_Specified(Index: Integer): boolean;
    procedure SetfromTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  fromTime_Specified(Index: Integer): boolean;
    procedure SettoTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  toTime_Specified(Index: Integer): boolean;
    procedure Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  date_Specified(Index: Integer): boolean;
    procedure SetfilterCode(Index: Integer; const Astring: string);
    function  filterCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property carrierTypeId: Int64        Index (IS_ATTR or IS_OPTN) read FcarrierTypeId write SetcarrierTypeId stored carrierTypeId_Specified;
    property carrierId:     Int64        Index (IS_ATTR or IS_OPTN) read FcarrierId write SetcarrierId stored carrierId_Specified;
    property stopId:        Int64        Index (IS_ATTR) read FstopId write FstopId;
    property fromTime:      TXSDateTime  Index (IS_ATTR or IS_OPTN) read FfromTime write SetfromTime stored fromTime_Specified;
    property toTime:        TXSDateTime  Index (IS_ATTR or IS_OPTN) read FtoTime write SettoTime stored toTime_Specified;
    property date:          TXSDateTime  Index (IS_ATTR or IS_OPTN) read Fdate write Setdate stored date_Specified;
    property filterCode:    string       Index (IS_OPTN) read FfilterCode write SetfilterCode stored filterCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSEnumParam, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSEnumParam = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    Fvalue: string;
    Fvalue_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setvalue(Index: Integer; const Astring: string);
    function  value_Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property value: string  Index (IS_OPTN) read Fvalue write Setvalue stored value_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiDiscount, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiDiscount = class(TRemotable)
  private
    FtravelGroupId: Int64;
    FtravelGroupId_Specified: boolean;
    FvalueAfterDiscount: Single;
    FvalueAfterDiscount_Specified: boolean;
    FdiscountValue: Single;
    FdiscountValue_Specified: boolean;
    Fpercent: Boolean;
    Fpercent_Specified: boolean;
    FdefaultDis: Boolean;
    FdefaultDis_Specified: boolean;
    Ft5grRoundBound: Single;
    Ft5grRoundBound_Specified: boolean;
    Ft10grRoundBound: Single;
    Ft10grRoundBound_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    Fdescription: string;
    Fdescription_Specified: boolean;
    FroundType: PWSEnumParam;
    FroundType_Specified: boolean;
    procedure SettravelGroupId(Index: Integer; const AInt64: Int64);
    function  travelGroupId_Specified(Index: Integer): boolean;
    procedure SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
    function  valueAfterDiscount_Specified(Index: Integer): boolean;
    procedure SetdiscountValue(Index: Integer; const ASingle: Single);
    function  discountValue_Specified(Index: Integer): boolean;
    procedure Setpercent(Index: Integer; const ABoolean: Boolean);
    function  percent_Specified(Index: Integer): boolean;
    procedure SetdefaultDis(Index: Integer; const ABoolean: Boolean);
    function  defaultDis_Specified(Index: Integer): boolean;
    procedure Sett5grRoundBound(Index: Integer; const ASingle: Single);
    function  t5grRoundBound_Specified(Index: Integer): boolean;
    procedure Sett10grRoundBound(Index: Integer; const ASingle: Single);
    function  t10grRoundBound_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
    procedure Setdescription(Index: Integer; const Astring: string);
    function  description_Specified(Index: Integer): boolean;
    procedure SetroundType(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  roundType_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property travelGroupId:      Int64         Index (IS_ATTR or IS_OPTN) read FtravelGroupId write SettravelGroupId stored travelGroupId_Specified;
    property valueAfterDiscount: Single        Index (IS_ATTR or IS_OPTN) read FvalueAfterDiscount write SetvalueAfterDiscount stored valueAfterDiscount_Specified;
    property discountValue:      Single        Index (IS_ATTR or IS_OPTN) read FdiscountValue write SetdiscountValue stored discountValue_Specified;
    property percent:            Boolean       Index (IS_ATTR or IS_OPTN) read Fpercent write Setpercent stored percent_Specified;
    property defaultDis:         Boolean       Index (IS_ATTR or IS_OPTN) read FdefaultDis write SetdefaultDis stored defaultDis_Specified;
    property t5grRoundBound:     Single        Index (IS_ATTR or IS_OPTN) read Ft5grRoundBound write Sett5grRoundBound stored t5grRoundBound_Specified;
    property t10grRoundBound:    Single        Index (IS_ATTR or IS_OPTN) read Ft10grRoundBound write Sett10grRoundBound stored t10grRoundBound_Specified;
    property name_:              string        Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:               string        Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
    property description:        string        Index (IS_OPTN) read Fdescription write Setdescription stored description_Specified;
    property roundType:          PWSEnumParam  Index (IS_OPTN) read FroundType write SetroundType stored roundType_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiTariffPriceAfterDiscount, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiTariffPriceAfterDiscount = class(TRemotable)
  private
    FpriceId: Int64;
    FpriceId_Specified: boolean;
    FtravelGroupId: Int64;
    FtravelGroupId_Specified: boolean;
    Fvalue: Single;
    Fvalue_Specified: boolean;
    procedure SetpriceId(Index: Integer; const AInt64: Int64);
    function  priceId_Specified(Index: Integer): boolean;
    procedure SettravelGroupId(Index: Integer; const AInt64: Int64);
    function  travelGroupId_Specified(Index: Integer): boolean;
    procedure Setvalue(Index: Integer; const ASingle: Single);
    function  value_Specified(Index: Integer): boolean;
  published
    property priceId:       Int64   Index (IS_ATTR or IS_OPTN) read FpriceId write SetpriceId stored priceId_Specified;
    property travelGroupId: Int64   Index (IS_ATTR or IS_OPTN) read FtravelGroupId write SettravelGroupId stored travelGroupId_Specified;
    property value:         Single  Index (IS_ATTR or IS_OPTN) read Fvalue write Setvalue stored value_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiDocType, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiDocType = class(TRemotable)
  private
    FlongCode: string;
    FlongCode_Specified: boolean;
    FshortCode: string;
    FshortCode_Specified: boolean;
    FlongPrinatble: string;
    FlongPrinatble_Specified: boolean;
    FshortPrinatble: string;
    FshortPrinatble_Specified: boolean;
    procedure SetlongCode(Index: Integer; const Astring: string);
    function  longCode_Specified(Index: Integer): boolean;
    procedure SetshortCode(Index: Integer; const Astring: string);
    function  shortCode_Specified(Index: Integer): boolean;
    procedure SetlongPrinatble(Index: Integer; const Astring: string);
    function  longPrinatble_Specified(Index: Integer): boolean;
    procedure SetshortPrinatble(Index: Integer; const Astring: string);
    function  shortPrinatble_Specified(Index: Integer): boolean;
  published
    property longCode:       string  Index (IS_OPTN) read FlongCode write SetlongCode stored longCode_Specified;
    property shortCode:      string  Index (IS_OPTN) read FshortCode write SetshortCode stored shortCode_Specified;
    property longPrinatble:  string  Index (IS_OPTN) read FlongPrinatble write SetlongPrinatble stored longPrinatble_Specified;
    property shortPrinatble: string  Index (IS_OPTN) read FshortPrinatble write SetshortPrinatble stored shortPrinatble_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSStop, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSStop = class(TRemotable)
  private
    Fid: Int64;
    FcityId: Int64;
    Fdepot: Boolean;
    Fname_: string;
    Fname__Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
  published
    property id:       Int64    Index (IS_ATTR) read Fid write Fid;
    property cityId:   Int64    Index (IS_ATTR) read FcityId write FcityId;
    property depot:    Boolean  Index (IS_ATTR) read Fdepot write Fdepot;
    property name_:    string   Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property cityName: string   Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCostForPeriod, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCostForPeriod = class(TRemotable)
  private
    FfromDate: TXSDateTime;
    FfromDate_Specified: boolean;
    FtoDate: TXSDateTime;
    FtoDate_Specified: boolean;
    Fnumber: Int64;
    Fnumber_Specified: boolean;
    Fcost: Single;
    Fcost_Specified: boolean;
    procedure SetfromDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  fromDate_Specified(Index: Integer): boolean;
    procedure SettoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  toDate_Specified(Index: Integer): boolean;
    procedure Setnumber(Index: Integer; const AInt64: Int64);
    function  number_Specified(Index: Integer): boolean;
    procedure Setcost(Index: Integer; const ASingle: Single);
    function  cost_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property fromDate: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FfromDate write SetfromDate stored fromDate_Specified;
    property toDate:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FtoDate write SettoDate stored toDate_Specified;
    property number:   Int64        Index (IS_ATTR or IS_OPTN) read Fnumber write Setnumber stored number_Specified;
    property cost:     Single       Index (IS_ATTR or IS_OPTN) read Fcost write Setcost stored cost_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCarrierId, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrierId = class(TRemotable)
  private
    FcarrierId: Int64;
    FcarrierId_Specified: boolean;
    procedure SetcarrierId(Index: Integer; const AInt64: Int64);
    function  carrierId_Specified(Index: Integer): boolean;
  published
    property carrierId: Int64  Index (IS_ATTR or IS_OPTN) read FcarrierId write SetcarrierId stored carrierId_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiOrderWithCustomerData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiOrderWithCustomerData = class(TRemotable)
  private
    FdistributorId: Int64;
    FdistributorId_Specified: boolean;
    FvendingMachineId: Int64;
    FvendingMachineId_Specified: boolean;
    Forder: order;
    Forder_Specified: boolean;
    FcustomerData: customerData;
    FcustomerData_Specified: boolean;
    FpaymentForm: PWSEnumParam;
    FpaymentForm_Specified: boolean;
    procedure SetdistributorId(Index: Integer; const AInt64: Int64);
    function  distributorId_Specified(Index: Integer): boolean;
    procedure SetvendingMachineId(Index: Integer; const AInt64: Int64);
    function  vendingMachineId_Specified(Index: Integer): boolean;
    procedure Setorder(Index: Integer; const Aorder: order);
    function  order_Specified(Index: Integer): boolean;
    procedure SetcustomerData(Index: Integer; const AcustomerData: customerData);
    function  customerData_Specified(Index: Integer): boolean;
    procedure SetpaymentForm(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  paymentForm_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property distributorId:    Int64         Index (IS_ATTR or IS_OPTN) read FdistributorId write SetdistributorId stored distributorId_Specified;
    property vendingMachineId: Int64         Index (IS_ATTR or IS_OPTN) read FvendingMachineId write SetvendingMachineId stored vendingMachineId_Specified;
    property order:            order         Index (IS_OPTN) read Forder write Setorder stored order_Specified;
    property customerData:     customerData  Index (IS_OPTN) read FcustomerData write SetcustomerData stored customerData_Specified;
    property paymentForm:      PWSEnumParam  Index (IS_OPTN) read FpaymentForm write SetpaymentForm stored paymentForm_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiHolderForTicket, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiHolderForTicket = class(TRemotable)
  private
    FdocType: PWSTiDocType;
    FdocType_Specified: boolean;
    FidentifyingDocValue: string;
    FidentifyingDocValue_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    FcontactPhone: string;
    FcontactPhone_Specified: boolean;
    procedure SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
    function  docType_Specified(Index: Integer): boolean;
    procedure SetidentifyingDocValue(Index: Integer; const Astring: string);
    function  identifyingDocValue_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure SetcontactPhone(Index: Integer; const Astring: string);
    function  contactPhone_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property docType:             PWSTiDocType  Index (IS_OPTN) read FdocType write SetdocType stored docType_Specified;
    property identifyingDocValue: string        Index (IS_OPTN) read FidentifyingDocValue write SetidentifyingDocValue stored identifyingDocValue_Specified;
    property forename:            string        Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:             string        Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property contactPhone:        string        Index (IS_OPTN) read FcontactPhone write SetcontactPhone stored contactPhone_Specified;
  end;



  // ************************************************************************ //
  // XML       : place, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  place = class(TRemotable)
  private
    FplaceNumber: Integer;
    FplaceNumber_Specified: boolean;
    FtravelGroupId: Int64;
    FtravelGroupId_Specified: boolean;
    FlagguagePriceId: Int64;
    FlagguagePriceId_Specified: boolean;
    FholderData: PWSTiHolderForTicket;
    FholderData_Specified: boolean;
    procedure SetplaceNumber(Index: Integer; const AInteger: Integer);
    function  placeNumber_Specified(Index: Integer): boolean;
    procedure SettravelGroupId(Index: Integer; const AInt64: Int64);
    function  travelGroupId_Specified(Index: Integer): boolean;
    procedure SetlagguagePriceId(Index: Integer; const AInt64: Int64);
    function  lagguagePriceId_Specified(Index: Integer): boolean;
    procedure SetholderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
    function  holderData_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property placeNumber:     Integer               Index (IS_ATTR or IS_OPTN) read FplaceNumber write SetplaceNumber stored placeNumber_Specified;
    property travelGroupId:   Int64                 Index (IS_ATTR or IS_OPTN) read FtravelGroupId write SettravelGroupId stored travelGroupId_Specified;
    property lagguagePriceId: Int64                 Index (IS_ATTR or IS_OPTN) read FlagguagePriceId write SetlagguagePriceId stored lagguagePriceId_Specified;
    property holderData:      PWSTiHolderForTicket  Index (IS_OPTN) read FholderData write SetholderData stored holderData_Specified;
  end;



  // ************************************************************************ //
  // XML       : periodicTicket, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  periodicTicket = class(TRemotable)
  private
    FperiodicCardIdentyfier: PWSTiPeriodicCardIdentyfier;
    FperiodicCardIdentyfier_Specified: boolean;
    procedure SetperiodicCardIdentyfier(Index: Integer; const APWSTiPeriodicCardIdentyfier: PWSTiPeriodicCardIdentyfier);
    function  periodicCardIdentyfier_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property periodicCardIdentyfier: PWSTiPeriodicCardIdentyfier  Index (IS_OPTN) read FperiodicCardIdentyfier write SetperiodicCardIdentyfier stored periodicCardIdentyfier_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiPeriodicCardIdentyfier, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiPeriodicCardIdentyfier = class(TRemotable)
  private
    FperiodicCardIdentyfier: Int64;
    FperiodicCardIdentyfier_Specified: boolean;
    procedure SetperiodicCardIdentyfier(Index: Integer; const AInt64: Int64);
    function  periodicCardIdentyfier_Specified(Index: Integer): boolean;
  published
    property periodicCardIdentyfier: Int64  Index (IS_ATTR or IS_OPTN) read FperiodicCardIdentyfier write SetperiodicCardIdentyfier stored periodicCardIdentyfier_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiSendingData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSendingData = class(TRemotable)
  private
    FsendingAddres: string;
    FsendingAddres_Specified: boolean;
    Ftype_: PWSEnumParam;
    Ftype__Specified: boolean;
    procedure SetsendingAddres(Index: Integer; const Astring: string);
    function  sendingAddres_Specified(Index: Integer): boolean;
    procedure Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  type__Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property sendingAddres: string        Index (IS_OPTN) read FsendingAddres write SetsendingAddres stored sendingAddres_Specified;
    property type_:         PWSEnumParam  Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
  end;



  // ************************************************************************ //
  // XML       : customerData, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  customerData = class(TRemotable)
  private
    FpayerId: Int64;
    FpayerId_Specified: boolean;
    FcityId: Int64;
    FcityId_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    Fnip: string;
    Fnip_Specified: boolean;
    FpostalCode: string;
    FpostalCode_Specified: boolean;
    Fstreet: string;
    Fstreet_Specified: boolean;
    FbuildingNumber: string;
    FbuildingNumber_Specified: boolean;
    FinvoiceSendingAddress: string;
    FinvoiceSendingAddress_Specified: boolean;
    procedure SetpayerId(Index: Integer; const AInt64: Int64);
    function  payerId_Specified(Index: Integer): boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setnip(Index: Integer; const Astring: string);
    function  nip_Specified(Index: Integer): boolean;
    procedure SetpostalCode(Index: Integer; const Astring: string);
    function  postalCode_Specified(Index: Integer): boolean;
    procedure Setstreet(Index: Integer; const Astring: string);
    function  street_Specified(Index: Integer): boolean;
    procedure SetbuildingNumber(Index: Integer; const Astring: string);
    function  buildingNumber_Specified(Index: Integer): boolean;
    procedure SetinvoiceSendingAddress(Index: Integer; const Astring: string);
    function  invoiceSendingAddress_Specified(Index: Integer): boolean;
  published
    property payerId:               Int64   Index (IS_ATTR or IS_OPTN) read FpayerId write SetpayerId stored payerId_Specified;
    property cityId:                Int64   Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property name_:                 string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property nip:                   string  Index (IS_OPTN) read Fnip write Setnip stored nip_Specified;
    property postalCode:            string  Index (IS_OPTN) read FpostalCode write SetpostalCode stored postalCode_Specified;
    property street:                string  Index (IS_OPTN) read Fstreet write Setstreet stored street_Specified;
    property buildingNumber:        string  Index (IS_OPTN) read FbuildingNumber write SetbuildingNumber stored buildingNumber_Specified;
    property invoiceSendingAddress: string  Index (IS_OPTN) read FinvoiceSendingAddress write SetinvoiceSendingAddress stored invoiceSendingAddress_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSMessage, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSMessage = class(TRemotable)
  private
    Fdate: TXSDateTime;
    Fdate_Specified: boolean;
    Fcontents: string;
    Fcontents_Specified: boolean;
    procedure Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  date_Specified(Index: Integer): boolean;
    procedure Setcontents(Index: Integer; const Astring: string);
    function  contents_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property date:     TXSDateTime  Index (IS_ATTR or IS_OPTN) read Fdate write Setdate stored date_Specified;
    property contents: string       Index (IS_OPTN) read Fcontents write Setcontents stored contents_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSFullyQualifiedStop, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSFullyQualifiedStop = class(TRemotable)
  private
    Fid: Int64;
    FcityId: Int64;
    Fdepot: Boolean;
    Fcity: PWSFullyQualifiedCity;
    Fcity_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    procedure Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  city_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:       Int64                  Index (IS_ATTR) read Fid write Fid;
    property cityId:   Int64                  Index (IS_ATTR) read FcityId write FcityId;
    property depot:    Boolean                Index (IS_ATTR) read Fdepot write Fdepot;
    property city:     PWSFullyQualifiedCity  Index (IS_OPTN) read Fcity write Setcity stored city_Specified;
    property name_:    string                 Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property cityName: string                 Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSFullyQualifiedCity, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSFullyQualifiedCity = class(TRemotable)
  private
    Fid: Int64;
    FcommuneId: Int64;
    Fname_: string;
    Fname__Specified: boolean;
    FprovinceName: string;
    FprovinceName_Specified: boolean;
    FcommuneName: string;
    FcommuneName_Specified: boolean;
    FdistrictName: string;
    FdistrictName_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetprovinceName(Index: Integer; const Astring: string);
    function  provinceName_Specified(Index: Integer): boolean;
    procedure SetcommuneName(Index: Integer; const Astring: string);
    function  communeName_Specified(Index: Integer): boolean;
    procedure SetdistrictName(Index: Integer; const Astring: string);
    function  districtName_Specified(Index: Integer): boolean;
  published
    property id:           Int64   Index (IS_ATTR) read Fid write Fid;
    property communeId:    Int64   Index (IS_ATTR) read FcommuneId write FcommuneId;
    property name_:        string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property provinceName: string  Index (IS_OPTN) read FprovinceName write SetprovinceName stored provinceName_Specified;
    property communeName:  string  Index (IS_OPTN) read FcommuneName write SetcommuneName stored communeName_Specified;
    property districtName: string  Index (IS_OPTN) read FdistrictName write SetdistrictName stored districtName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSInformicaCarrier, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSInformicaCarrier = class(TRemotable)
  private
    FnrF: Integer;
    FcompanyCode: string;
    FcompanyCode_Specified: boolean;
    procedure SetcompanyCode(Index: Integer; const Astring: string);
    function  companyCode_Specified(Index: Integer): boolean;
  published
    property nrF:         Integer  Index (IS_ATTR) read FnrF write FnrF;
    property companyCode: string   Index (IS_OPTN) read FcompanyCode write SetcompanyCode stored companyCode_Specified;
  end;

  PWSCitiesStops = array of cityStop;           { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : PWSNamePrincipal, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSNamePrincipal = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    FfullName: string;
    FfullName_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetfullName(Index: Integer; const Astring: string);
    function  fullName_Specified(Index: Integer): boolean;
  published
    property name_:    string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property fullName: string  Index (IS_OPTN) read FfullName write SetfullName stored fullName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSConnSearchingDetails, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSConnSearchingDetails = class(TRemotable)
  private
    FdateRangeFrom: TXSDateTime;
    FdateRangeFrom_Specified: boolean;
    FdateRangeTo: TXSDateTime;
    FdateRangeTo_Specified: boolean;
    FtimeRangeFrom: TXSDateTime;
    FtimeRangeFrom_Specified: boolean;
    FtimeRangeTo: TXSDateTime;
    FtimeRangeTo_Specified: boolean;
    FstartCity: PWSFullyQualifiedCity;
    FstartCity_Specified: boolean;
    FendCity: PWSFullyQualifiedCity;
    FendCity_Specified: boolean;
    procedure SetdateRangeFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dateRangeFrom_Specified(Index: Integer): boolean;
    procedure SetdateRangeTo(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dateRangeTo_Specified(Index: Integer): boolean;
    procedure SettimeRangeFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  timeRangeFrom_Specified(Index: Integer): boolean;
    procedure SettimeRangeTo(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  timeRangeTo_Specified(Index: Integer): boolean;
    procedure SetstartCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  startCity_Specified(Index: Integer): boolean;
    procedure SetendCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  endCity_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property dateRangeFrom: TXSDateTime            Index (IS_ATTR or IS_OPTN) read FdateRangeFrom write SetdateRangeFrom stored dateRangeFrom_Specified;
    property dateRangeTo:   TXSDateTime            Index (IS_ATTR or IS_OPTN) read FdateRangeTo write SetdateRangeTo stored dateRangeTo_Specified;
    property timeRangeFrom: TXSDateTime            Index (IS_ATTR or IS_OPTN) read FtimeRangeFrom write SettimeRangeFrom stored timeRangeFrom_Specified;
    property timeRangeTo:   TXSDateTime            Index (IS_ATTR or IS_OPTN) read FtimeRangeTo write SettimeRangeTo stored timeRangeTo_Specified;
    property startCity:     PWSFullyQualifiedCity  Index (IS_OPTN) read FstartCity write SetstartCity stored startCity_Specified;
    property endCity:       PWSFullyQualifiedCity  Index (IS_OPTN) read FendCity write SetendCity stored endCity_Specified;
  end;



  // ************************************************************************ //
  // XML       : holder, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  holder = class(TRemotable)
  private
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    FkasaHolderId: string;
    FkasaHolderId_Specified: boolean;
    FidentifyingDocValue: string;
    FidentifyingDocValue_Specified: boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure SetkasaHolderId(Index: Integer; const Astring: string);
    function  kasaHolderId_Specified(Index: Integer): boolean;
    procedure SetidentifyingDocValue(Index: Integer; const Astring: string);
    function  identifyingDocValue_Specified(Index: Integer): boolean;
  published
    property forename:            string  Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:             string  Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property kasaHolderId:        string  Index (IS_OPTN) read FkasaHolderId write SetkasaHolderId stored kasaHolderId_Specified;
    property identifyingDocValue: string  Index (IS_OPTN) read FidentifyingDocValue write SetidentifyingDocValue stored identifyingDocValue_Specified;
  end;

  linesInfo  = array of PWSTiPeriodicTicketLineInfo;   { "http://83.15.136.94:54321/axis2/services"[Cplx] }


  // ************************************************************************ //
  // XML       : PWSTiPeriodicTicketInfo, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiPeriodicTicketInfo = class(TRemotable)
  private
    FendOfValidity: TXSDateTime;
    FendOfValidity_Specified: boolean;
    FperiodLengthInDays: Integer;
    FperiodLengthInDays_Specified: boolean;
    FgrossPriceForPeriod: Single;
    FgrossPriceForPeriod_Specified: boolean;
    FcommitTimestamp: TXSDateTime;
    FcommitTimestamp_Specified: boolean;
    FperiodicCardId: PWSTiPeriodicCardIdentyfier;
    FperiodicCardId_Specified: boolean;
    Fholder: holder;
    Fholder_Specified: boolean;
    FlinesInfo: linesInfo;
    FlinesInfo_Specified: boolean;
    FverifyingCode: string;
    FverifyingCode_Specified: boolean;
    Fdiscount: PWSTiDiscount;
    Fdiscount_Specified: boolean;
    FticketLoginCode: string;
    FticketLoginCode_Specified: boolean;
    procedure SetendOfValidity(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  endOfValidity_Specified(Index: Integer): boolean;
    procedure SetperiodLengthInDays(Index: Integer; const AInteger: Integer);
    function  periodLengthInDays_Specified(Index: Integer): boolean;
    procedure SetgrossPriceForPeriod(Index: Integer; const ASingle: Single);
    function  grossPriceForPeriod_Specified(Index: Integer): boolean;
    procedure SetcommitTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  commitTimestamp_Specified(Index: Integer): boolean;
    procedure SetperiodicCardId(Index: Integer; const APWSTiPeriodicCardIdentyfier: PWSTiPeriodicCardIdentyfier);
    function  periodicCardId_Specified(Index: Integer): boolean;
    procedure Setholder(Index: Integer; const Aholder: holder);
    function  holder_Specified(Index: Integer): boolean;
    procedure SetlinesInfo(Index: Integer; const AlinesInfo: linesInfo);
    function  linesInfo_Specified(Index: Integer): boolean;
    procedure SetverifyingCode(Index: Integer; const Astring: string);
    function  verifyingCode_Specified(Index: Integer): boolean;
    procedure Setdiscount(Index: Integer; const APWSTiDiscount: PWSTiDiscount);
    function  discount_Specified(Index: Integer): boolean;
    procedure SetticketLoginCode(Index: Integer; const Astring: string);
    function  ticketLoginCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property endOfValidity:       TXSDateTime                  Index (IS_ATTR or IS_OPTN) read FendOfValidity write SetendOfValidity stored endOfValidity_Specified;
    property periodLengthInDays:  Integer                      Index (IS_ATTR or IS_OPTN) read FperiodLengthInDays write SetperiodLengthInDays stored periodLengthInDays_Specified;
    property grossPriceForPeriod: Single                       Index (IS_ATTR or IS_OPTN) read FgrossPriceForPeriod write SetgrossPriceForPeriod stored grossPriceForPeriod_Specified;
    property commitTimestamp:     TXSDateTime                  Index (IS_ATTR or IS_OPTN) read FcommitTimestamp write SetcommitTimestamp stored commitTimestamp_Specified;
    property periodicCardId:      PWSTiPeriodicCardIdentyfier  Index (IS_OPTN) read FperiodicCardId write SetperiodicCardId stored periodicCardId_Specified;
    property holder:              holder                       Index (IS_OPTN) read Fholder write Setholder stored holder_Specified;
    property linesInfo:           linesInfo                    Index (IS_OPTN) read FlinesInfo write SetlinesInfo stored linesInfo_Specified;
    property verifyingCode:       string                       Index (IS_OPTN) read FverifyingCode write SetverifyingCode stored verifyingCode_Specified;
    property discount:            PWSTiDiscount                Index (IS_OPTN) read Fdiscount write Setdiscount stored discount_Specified;
    property ticketLoginCode:     string                       Index (IS_OPTN) read FticketLoginCode write SetticketLoginCode stored ticketLoginCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : section, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  section = class(TRemotable)
  private
    FfromCode: Int64;
    FfromCode_Specified: boolean;
    FfromZone: Boolean;
    FfromZone_Specified: boolean;
    FtoCode: Int64;
    FtoCode_Specified: boolean;
    FtoZone: Boolean;
    FtoZone_Specified: boolean;
    Ftype_: PWSEnumParam;
    Ftype__Specified: boolean;
    Fcourse: PWSTiBusCourse;
    Fcourse_Specified: boolean;
    procedure SetfromCode(Index: Integer; const AInt64: Int64);
    function  fromCode_Specified(Index: Integer): boolean;
    procedure SetfromZone(Index: Integer; const ABoolean: Boolean);
    function  fromZone_Specified(Index: Integer): boolean;
    procedure SettoCode(Index: Integer; const AInt64: Int64);
    function  toCode_Specified(Index: Integer): boolean;
    procedure SettoZone(Index: Integer; const ABoolean: Boolean);
    function  toZone_Specified(Index: Integer): boolean;
    procedure Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  type__Specified(Index: Integer): boolean;
    procedure Setcourse(Index: Integer; const APWSTiBusCourse: PWSTiBusCourse);
    function  course_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property fromCode: Int64           Index (IS_ATTR or IS_OPTN) read FfromCode write SetfromCode stored fromCode_Specified;
    property fromZone: Boolean         Index (IS_ATTR or IS_OPTN) read FfromZone write SetfromZone stored fromZone_Specified;
    property toCode:   Int64           Index (IS_ATTR or IS_OPTN) read FtoCode write SettoCode stored toCode_Specified;
    property toZone:   Boolean         Index (IS_ATTR or IS_OPTN) read FtoZone write SettoZone stored toZone_Specified;
    property type_:    PWSEnumParam    Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
    property course:   PWSTiBusCourse  Index (IS_OPTN) read Fcourse write Setcourse stored course_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiBusCourse, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiBusCourse = class(TRemotable)
  private
    FnrKursu: Integer;
    FnrKursu_Specified: boolean;
    FkierTam: Boolean;
    FkierTam_Specified: boolean;
    FwaznyOd: TXSDateTime;
    FwaznyOd_Specified: boolean;
    FinfNrf: Integer;
    FinfNrf_Specified: boolean;
    Fwariant: string;
    Fwariant_Specified: boolean;
    FrodzKom: string;
    FrodzKom_Specified: boolean;
    procedure SetnrKursu(Index: Integer; const AInteger: Integer);
    function  nrKursu_Specified(Index: Integer): boolean;
    procedure SetkierTam(Index: Integer; const ABoolean: Boolean);
    function  kierTam_Specified(Index: Integer): boolean;
    procedure SetwaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  waznyOd_Specified(Index: Integer): boolean;
    procedure SetinfNrf(Index: Integer; const AInteger: Integer);
    function  infNrf_Specified(Index: Integer): boolean;
    procedure Setwariant(Index: Integer; const Astring: string);
    function  wariant_Specified(Index: Integer): boolean;
    procedure SetrodzKom(Index: Integer; const Astring: string);
    function  rodzKom_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property nrKursu: Integer      Index (IS_ATTR or IS_OPTN) read FnrKursu write SetnrKursu stored nrKursu_Specified;
    property kierTam: Boolean      Index (IS_ATTR or IS_OPTN) read FkierTam write SetkierTam stored kierTam_Specified;
    property waznyOd: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FwaznyOd write SetwaznyOd stored waznyOd_Specified;
    property infNrf:  Integer      Index (IS_ATTR or IS_OPTN) read FinfNrf write SetinfNrf stored infNrf_Specified;
    property wariant: string       Index (IS_OPTN) read Fwariant write Setwariant stored wariant_Specified;
    property rodzKom: string       Index (IS_OPTN) read FrodzKom write SetrodzKom stored rodzKom_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSConnection, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSConnection = class(TRemotable)
  private
    Fid: Int64;
    FvalidFromTimestamp: TXSDateTime;
    FvalidFromTimestamp_Specified: boolean;
    FvalidToTimestamp: TXSDateTime;
    FvalidToTimestamp_Specified: boolean;
    Ftype_: type_2;
    Ftype__Specified: boolean;
    Flegend: string;
    Flegend_Specified: boolean;
    procedure SetvalidFromTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validFromTimestamp_Specified(Index: Integer): boolean;
    procedure SetvalidToTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validToTimestamp_Specified(Index: Integer): boolean;
    procedure Settype_(Index: Integer; const Atype_2: type_2);
    function  type__Specified(Index: Integer): boolean;
    procedure Setlegend(Index: Integer; const Astring: string);
    function  legend_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:                 Int64        Index (IS_ATTR) read Fid write Fid;
    property validFromTimestamp: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidFromTimestamp write SetvalidFromTimestamp stored validFromTimestamp_Specified;
    property validToTimestamp:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidToTimestamp write SetvalidToTimestamp stored validToTimestamp_Specified;
    property type_:              type_2       Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
    property legend:             string       Index (IS_OPTN) read Flegend write Setlegend stored legend_Specified;
  end;



  // ************************************************************************ //
  // XML       : type, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  type_2 = class(TRemotable)
  private
    Ftype_: type_;
    Ftype__Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    procedure Settype_(Index: Integer; const Atype_: type_);
    function  type__Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
  published
    property type_: type_   Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
  end;



  // ************************************************************************ //
  // XML       : passenger, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  passenger = class(TRemotable)
  private
    Fnumber: Integer;
    Fnumber_Specified: boolean;
    FgroupName: string;
    FgroupName_Specified: boolean;
    procedure Setnumber(Index: Integer; const AInteger: Integer);
    function  number_Specified(Index: Integer): boolean;
    procedure SetgroupName(Index: Integer; const Astring: string);
    function  groupName_Specified(Index: Integer): boolean;
  published
    property number:    Integer  Index (IS_ATTR or IS_OPTN) read Fnumber write Setnumber stored number_Specified;
    property groupName: string   Index (IS_OPTN) read FgroupName write SetgroupName stored groupName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSPasswordCredential, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSPasswordCredential = class(TRemotable)
  private
    Fpassword: string;
    Fpassword_Specified: boolean;
    procedure Setpassword(Index: Integer; const Astring: string);
    function  password_Specified(Index: Integer): boolean;
  published
    property password: string  Index (IS_OPTN) read Fpassword write Setpassword stored password_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSSessionIdPrincipal, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSSessionIdPrincipal = class(TRemotable)
  private
    FsessionId: string;
    FsessionId_Specified: boolean;
    procedure SetsessionId(Index: Integer; const Astring: string);
    function  sessionId_Specified(Index: Integer): boolean;
  published
    property sessionId: string  Index (IS_OPTN) read FsessionId write SetsessionId stored sessionId_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSUserInfo, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSUserInfo = class(TRemotable)
  private
    Fusername: PWSNamePrincipal;
    Fusername_Specified: boolean;
    Fpassword: PWSPasswordCredential;
    Fpassword_Specified: boolean;
    FsessionId: PWSSessionIdPrincipal;
    FsessionId_Specified: boolean;
    Fversion: version;
    Fversion_Specified: boolean;
    procedure Setusername(Index: Integer; const APWSNamePrincipal: PWSNamePrincipal);
    function  username_Specified(Index: Integer): boolean;
    procedure Setpassword(Index: Integer; const APWSPasswordCredential: PWSPasswordCredential);
    function  password_Specified(Index: Integer): boolean;
    procedure SetsessionId(Index: Integer; const APWSSessionIdPrincipal: PWSSessionIdPrincipal);
    function  sessionId_Specified(Index: Integer): boolean;
    procedure Setversion(Index: Integer; const Aversion: version);
    function  version_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property username:  PWSNamePrincipal       Index (IS_OPTN) read Fusername write Setusername stored username_Specified;
    property password:  PWSPasswordCredential  Index (IS_OPTN) read Fpassword write Setpassword stored password_Specified;
    property sessionId: PWSSessionIdPrincipal  Index (IS_OPTN) read FsessionId write SetsessionId stored sessionId_Specified;
    property version:   version                Index (IS_OPTN) read Fversion write Setversion stored version_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSStopInTime, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSStopInTime = class(TRemotable)
  private
    FsequenceNumber: Int64;
    Ftime: TXSDateTime;
    Ftime_Specified: boolean;
    FarrivalTime: TXSDateTime;
    FarrivalTime_Specified: boolean;
    FdistanceFromFirst: Int64;
    Fid: Int64;
    Fprice: Single;
    Fprice_Specified: boolean;
    Fstop: PWSStop;
    Fstop_Specified: boolean;
    procedure Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  time_Specified(Index: Integer): boolean;
    procedure SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  arrivalTime_Specified(Index: Integer): boolean;
    procedure Setprice(Index: Integer; const ASingle: Single);
    function  price_Specified(Index: Integer): boolean;
    procedure Setstop(Index: Integer; const APWSStop: PWSStop);
    function  stop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property sequenceNumber:    Int64        Index (IS_ATTR) read FsequenceNumber write FsequenceNumber;
    property time:              TXSDateTime  Index (IS_ATTR or IS_OPTN) read Ftime write Settime stored time_Specified;
    property arrivalTime:       TXSDateTime  Index (IS_ATTR or IS_OPTN) read FarrivalTime write SetarrivalTime stored arrivalTime_Specified;
    property distanceFromFirst: Int64        Index (IS_ATTR) read FdistanceFromFirst write FdistanceFromFirst;
    property id:                Int64        Index (IS_ATTR) read Fid write Fid;
    property price:             Single       Index (IS_ATTR or IS_OPTN) read Fprice write Setprice stored price_Specified;
    property stop:              PWSStop      Index (IS_OPTN) read Fstop write Setstop stored stop_Specified;
  end;

  PWSResultRouteDetailsParams = array of param;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : param, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  param = class(TRemotable)
  private
    FfromRouteId: Int64;
    FfromRouteId_Specified: boolean;
    FtoRouteId: Int64;
    FtoRouteId_Specified: boolean;
    procedure SetfromRouteId(Index: Integer; const AInt64: Int64);
    function  fromRouteId_Specified(Index: Integer): boolean;
    procedure SettoRouteId(Index: Integer; const AInt64: Int64);
    function  toRouteId_Specified(Index: Integer): boolean;
  published
    property fromRouteId: Int64  Index (IS_ATTR or IS_OPTN) read FfromRouteId write SetfromRouteId stored fromRouteId_Specified;
    property toRouteId:   Int64  Index (IS_ATTR or IS_OPTN) read FtoRouteId write SettoRouteId stored toRouteId_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSFullyQualifiedCityExt, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSFullyQualifiedCityExt = class(TRemotable)
  private
    FstopsCount: Int64;
    FstopsCount_Specified: boolean;
    FbigCity: Boolean;
    FveryBigCity: Boolean;
    Fmetropolis: Boolean;
    FbigTown: Boolean;
    Flatitude: Single;
    Flatitude_Specified: boolean;
    Flongitude: Single;
    Flongitude_Specified: boolean;
    Faltitude: Single;
    Faltitude_Specified: boolean;
    Ffqc: PWSFullyQualifiedCity;
    Ffqc_Specified: boolean;
    FsettlementType: string;
    FsettlementType_Specified: boolean;
    procedure SetstopsCount(Index: Integer; const AInt64: Int64);
    function  stopsCount_Specified(Index: Integer): boolean;
    procedure Setlatitude(Index: Integer; const ASingle: Single);
    function  latitude_Specified(Index: Integer): boolean;
    procedure Setlongitude(Index: Integer; const ASingle: Single);
    function  longitude_Specified(Index: Integer): boolean;
    procedure Setaltitude(Index: Integer; const ASingle: Single);
    function  altitude_Specified(Index: Integer): boolean;
    procedure Setfqc(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  fqc_Specified(Index: Integer): boolean;
    procedure SetsettlementType(Index: Integer; const Astring: string);
    function  settlementType_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property stopsCount:     Int64                  Index (IS_ATTR or IS_OPTN) read FstopsCount write SetstopsCount stored stopsCount_Specified;
    property bigCity:        Boolean                Index (IS_ATTR) read FbigCity write FbigCity;
    property veryBigCity:    Boolean                Index (IS_ATTR) read FveryBigCity write FveryBigCity;
    property metropolis:     Boolean                Index (IS_ATTR) read Fmetropolis write Fmetropolis;
    property bigTown:        Boolean                Index (IS_ATTR) read FbigTown write FbigTown;
    property latitude:       Single                 Index (IS_ATTR or IS_OPTN) read Flatitude write Setlatitude stored latitude_Specified;
    property longitude:      Single                 Index (IS_ATTR or IS_OPTN) read Flongitude write Setlongitude stored longitude_Specified;
    property altitude:       Single                 Index (IS_ATTR or IS_OPTN) read Faltitude write Setaltitude stored altitude_Specified;
    property fqc:            PWSFullyQualifiedCity  Index (IS_OPTN) read Ffqc write Setfqc stored fqc_Specified;
    property settlementType: string                 Index (IS_OPTN) read FsettlementType write SetsettlementType stored settlementType_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSVehiclePosition, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSVehiclePosition = class(TRemotable)
  private
    Fvehicle: PWSVehicle;
    Fvehicle_Specified: boolean;
    Fposition: PWSWaypoint;
    Fposition_Specified: boolean;
    procedure Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
    function  vehicle_Specified(Index: Integer): boolean;
    procedure Setposition(Index: Integer; const APWSWaypoint: PWSWaypoint);
    function  position_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property vehicle:  PWSVehicle   Index (IS_OPTN) read Fvehicle write Setvehicle stored vehicle_Specified;
    property position: PWSWaypoint  Index (IS_OPTN) read Fposition write Setposition stored position_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSVehicle, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSVehicle = class(TRemotable)
  private
    FvehicleNumber: string;
    FvehicleNumber_Specified: boolean;
    procedure SetvehicleNumber(Index: Integer; const Astring: string);
    function  vehicleNumber_Specified(Index: Integer): boolean;
  published
    property vehicleNumber: string  Index (IS_OPTN) read FvehicleNumber write SetvehicleNumber stored vehicleNumber_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiReservationId, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiReservationId = class(TRemotable)
  private
    Fid: Int64;
    Fid_Specified: boolean;
    procedure Setid(Index: Integer; const AInt64: Int64);
    function  id_Specified(Index: Integer): boolean;
  published
    property id: Int64  Index (IS_ATTR or IS_OPTN) read Fid write Setid stored id_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiVendingParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiVendingParams = class(TRemotable)
  private
    FvendingMachineId: Int64;
    FvendingMachineId_Specified: boolean;
    FsystemUserId: Int64;
    FsystemUserId_Specified: boolean;
    FfromStopId: Int64;
    FfromStopId_Specified: boolean;
    FlockedFromStopEditing: Boolean;
    FlockedFromStopEditing_Specified: boolean;
    FlockedMachine: Boolean;
    FlockedMachine_Specified: boolean;
    FlockedCardPayment: Boolean;
    FlockedCardPayment_Specified: boolean;
    FlockedCashPayment: Boolean;
    FlockedCashPayment_Specified: boolean;
    FlockedTicketManagement: Boolean;
    FlockedTicketManagement_Specified: boolean;
    FlockedPerTicketSelling: Boolean;
    FlockedPerTicketSelling_Specified: boolean;
    FlockedNorTicketSelling: Boolean;
    FlockedNorTicketSelling_Specified: boolean;
    FlockedResultsWithChange: Boolean;
    FlockedResultsWithChange_Specified: boolean;
    FlockedResultsWithoutSelling: Boolean;
    FlockedResultsWithoutSelling_Specified: boolean;
    FtraceModifyTimestamp: TXSDateTime;
    FtraceModifyTimestamp_Specified: boolean;
    FowningDistributorId: Int64;
    FowningDistributorId_Specified: boolean;
    FincludeNotSalesConnections: Boolean;
    FincludeNotSalesConnections_Specified: boolean;
    Fcarriers: carriers;
    Fcarriers_Specified: boolean;
    procedure SetvendingMachineId(Index: Integer; const AInt64: Int64);
    function  vendingMachineId_Specified(Index: Integer): boolean;
    procedure SetsystemUserId(Index: Integer; const AInt64: Int64);
    function  systemUserId_Specified(Index: Integer): boolean;
    procedure SetfromStopId(Index: Integer; const AInt64: Int64);
    function  fromStopId_Specified(Index: Integer): boolean;
    procedure SetlockedFromStopEditing(Index: Integer; const ABoolean: Boolean);
    function  lockedFromStopEditing_Specified(Index: Integer): boolean;
    procedure SetlockedMachine(Index: Integer; const ABoolean: Boolean);
    function  lockedMachine_Specified(Index: Integer): boolean;
    procedure SetlockedCardPayment(Index: Integer; const ABoolean: Boolean);
    function  lockedCardPayment_Specified(Index: Integer): boolean;
    procedure SetlockedCashPayment(Index: Integer; const ABoolean: Boolean);
    function  lockedCashPayment_Specified(Index: Integer): boolean;
    procedure SetlockedTicketManagement(Index: Integer; const ABoolean: Boolean);
    function  lockedTicketManagement_Specified(Index: Integer): boolean;
    procedure SetlockedPerTicketSelling(Index: Integer; const ABoolean: Boolean);
    function  lockedPerTicketSelling_Specified(Index: Integer): boolean;
    procedure SetlockedNorTicketSelling(Index: Integer; const ABoolean: Boolean);
    function  lockedNorTicketSelling_Specified(Index: Integer): boolean;
    procedure SetlockedResultsWithChange(Index: Integer; const ABoolean: Boolean);
    function  lockedResultsWithChange_Specified(Index: Integer): boolean;
    procedure SetlockedResultsWithoutSelling(Index: Integer; const ABoolean: Boolean);
    function  lockedResultsWithoutSelling_Specified(Index: Integer): boolean;
    procedure SettraceModifyTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  traceModifyTimestamp_Specified(Index: Integer): boolean;
    procedure SetowningDistributorId(Index: Integer; const AInt64: Int64);
    function  owningDistributorId_Specified(Index: Integer): boolean;
    procedure SetincludeNotSalesConnections(Index: Integer; const ABoolean: Boolean);
    function  includeNotSalesConnections_Specified(Index: Integer): boolean;
    procedure Setcarriers(Index: Integer; const Acarriers: carriers);
    function  carriers_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property vendingMachineId:            Int64        Index (IS_ATTR or IS_OPTN) read FvendingMachineId write SetvendingMachineId stored vendingMachineId_Specified;
    property systemUserId:                Int64        Index (IS_ATTR or IS_OPTN) read FsystemUserId write SetsystemUserId stored systemUserId_Specified;
    property fromStopId:                  Int64        Index (IS_ATTR or IS_OPTN) read FfromStopId write SetfromStopId stored fromStopId_Specified;
    property lockedFromStopEditing:       Boolean      Index (IS_ATTR or IS_OPTN) read FlockedFromStopEditing write SetlockedFromStopEditing stored lockedFromStopEditing_Specified;
    property lockedMachine:               Boolean      Index (IS_ATTR or IS_OPTN) read FlockedMachine write SetlockedMachine stored lockedMachine_Specified;
    property lockedCardPayment:           Boolean      Index (IS_ATTR or IS_OPTN) read FlockedCardPayment write SetlockedCardPayment stored lockedCardPayment_Specified;
    property lockedCashPayment:           Boolean      Index (IS_ATTR or IS_OPTN) read FlockedCashPayment write SetlockedCashPayment stored lockedCashPayment_Specified;
    property lockedTicketManagement:      Boolean      Index (IS_ATTR or IS_OPTN) read FlockedTicketManagement write SetlockedTicketManagement stored lockedTicketManagement_Specified;
    property lockedPerTicketSelling:      Boolean      Index (IS_ATTR or IS_OPTN) read FlockedPerTicketSelling write SetlockedPerTicketSelling stored lockedPerTicketSelling_Specified;
    property lockedNorTicketSelling:      Boolean      Index (IS_ATTR or IS_OPTN) read FlockedNorTicketSelling write SetlockedNorTicketSelling stored lockedNorTicketSelling_Specified;
    property lockedResultsWithChange:     Boolean      Index (IS_ATTR or IS_OPTN) read FlockedResultsWithChange write SetlockedResultsWithChange stored lockedResultsWithChange_Specified;
    property lockedResultsWithoutSelling: Boolean      Index (IS_ATTR or IS_OPTN) read FlockedResultsWithoutSelling write SetlockedResultsWithoutSelling stored lockedResultsWithoutSelling_Specified;
    property traceModifyTimestamp:        TXSDateTime  Index (IS_ATTR or IS_OPTN) read FtraceModifyTimestamp write SettraceModifyTimestamp stored traceModifyTimestamp_Specified;
    property owningDistributorId:         Int64        Index (IS_ATTR or IS_OPTN) read FowningDistributorId write SetowningDistributorId stored owningDistributorId_Specified;
    property includeNotSalesConnections:  Boolean      Index (IS_ATTR or IS_OPTN) read FincludeNotSalesConnections write SetincludeNotSalesConnections stored includeNotSalesConnections_Specified;
    property carriers:                    carriers     Index (IS_OPTN) read Fcarriers write Setcarriers stored carriers_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSStick, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSStick = class(TRemotable)
  private
    Fconnection: PWSConnection;
    Fconnection_Specified: boolean;
    Fcarrier: PWSCarrier;
    Fcarrier_Specified: boolean;
    FsourceStop: PWSStopInTime;
    FsourceStop_Specified: boolean;
    FtargetStop: PWSStopInTime;
    FtargetStop_Specified: boolean;
    procedure Setconnection(Index: Integer; const APWSConnection: PWSConnection);
    function  connection_Specified(Index: Integer): boolean;
    procedure Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
    function  carrier_Specified(Index: Integer): boolean;
    procedure SetsourceStop(Index: Integer; const APWSStopInTime: PWSStopInTime);
    function  sourceStop_Specified(Index: Integer): boolean;
    procedure SettargetStop(Index: Integer; const APWSStopInTime: PWSStopInTime);
    function  targetStop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property connection: PWSConnection  Index (IS_OPTN) read Fconnection write Setconnection stored connection_Specified;
    property carrier:    PWSCarrier     Index (IS_OPTN) read Fcarrier write Setcarrier stored carrier_Specified;
    property sourceStop: PWSStopInTime  Index (IS_OPTN) read FsourceStop write SetsourceStop stored sourceStop_Specified;
    property targetStop: PWSStopInTime  Index (IS_OPTN) read FtargetStop write SettargetStop stored targetStop_Specified;
  end;

  PTiHoldersMatrix = array of holdersForStick;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : stickId, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  stickId = class(TRemotable)
  private
    FfromRouteId: Int64;
    FfromRouteId_Specified: boolean;
    FtoRouteId: Int64;
    FtoRouteId_Specified: boolean;
    procedure SetfromRouteId(Index: Integer; const AInt64: Int64);
    function  fromRouteId_Specified(Index: Integer): boolean;
    procedure SettoRouteId(Index: Integer; const AInt64: Int64);
    function  toRouteId_Specified(Index: Integer): boolean;
  published
    property fromRouteId: Int64  Index (IS_ATTR or IS_OPTN) read FfromRouteId write SetfromRouteId stored fromRouteId_Specified;
    property toRouteId:   Int64  Index (IS_ATTR or IS_OPTN) read FtoRouteId write SettoRouteId stored toRouteId_Specified;
  end;

  cause      = array of cause3;                 { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSTiPeriodicCardIdsExceptionFaultData = array of cause;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }
  PWSCarrierLine = array of lineStop;           { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : PWSInfKurs, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSInfKurs = class(TRemotable)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : PWSChangeUserDataParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSChangeUserDataParams = class(TRemotable)
  private
    Flogin: string;
    Flogin_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    procedure Setlogin(Index: Integer; const Astring: string);
    function  login_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
  published
    property login:    string  Index (IS_OPTN) read Flogin write Setlogin stored login_Specified;
    property forename: string  Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:  string  Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property phone:    string  Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property email:    string  Index (IS_OPTN) read Femail write Setemail stored email_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSRelation, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSRelation = class(TRemotable)
  private
    FsourceStop: PWSFullyQualifiedStop;
    FsourceStop_Specified: boolean;
    FtargetStop: PWSFullyQualifiedStop;
    FtargetStop_Specified: boolean;
    procedure SetsourceStop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
    function  sourceStop_Specified(Index: Integer): boolean;
    procedure SettargetStop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
    function  targetStop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property sourceStop: PWSFullyQualifiedStop  Index (IS_OPTN) read FsourceStop write SetsourceStop stored sourceStop_Specified;
    property targetStop: PWSFullyQualifiedStop  Index (IS_OPTN) read FtargetStop write SettargetStop stored targetStop_Specified;
  end;



  // ************************************************************************ //
  // XML       : price, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  price = class(TRemotable)
  private
    FgrossPrice: Single;
    FgrossPrice_Specified: boolean;
    FvatRate: Single;
    FvatRate_Specified: boolean;
    FvatValue: Single;
    FvatValue_Specified: boolean;
    Fcountry: country;
    Fcountry_Specified: boolean;
    procedure SetgrossPrice(Index: Integer; const ASingle: Single);
    function  grossPrice_Specified(Index: Integer): boolean;
    procedure SetvatRate(Index: Integer; const ASingle: Single);
    function  vatRate_Specified(Index: Integer): boolean;
    procedure SetvatValue(Index: Integer; const ASingle: Single);
    function  vatValue_Specified(Index: Integer): boolean;
    procedure Setcountry(Index: Integer; const Acountry: country);
    function  country_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property grossPrice: Single   Index (IS_ATTR or IS_OPTN) read FgrossPrice write SetgrossPrice stored grossPrice_Specified;
    property vatRate:    Single   Index (IS_ATTR or IS_OPTN) read FvatRate write SetvatRate stored vatRate_Specified;
    property vatValue:   Single   Index (IS_ATTR or IS_OPTN) read FvatValue write SetvatValue stored vatValue_Specified;
    property country:    country  Index (IS_OPTN) read Fcountry write Setcountry stored country_Specified;
  end;



  // ************************************************************************ //
  // XML       : country, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  country = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:  string  Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
  end;



  // ************************************************************************ //
  // XML       : PTiHolderForTicket, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PTiHolderForTicket = class(TRemotable)
  private
    FidentifyingDocValue: string;
    FidentifyingDocValue_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    FdocType: docType;
    FdocType_Specified: boolean;
    FcontactPhone: string;
    FcontactPhone_Specified: boolean;
    procedure SetidentifyingDocValue(Index: Integer; const Astring: string);
    function  identifyingDocValue_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure SetdocType(Index: Integer; const AdocType: docType);
    function  docType_Specified(Index: Integer): boolean;
    procedure SetcontactPhone(Index: Integer; const Astring: string);
    function  contactPhone_Specified(Index: Integer): boolean;
  published
    property identifyingDocValue: string   Index (IS_OPTN) read FidentifyingDocValue write SetidentifyingDocValue stored identifyingDocValue_Specified;
    property forename:            string   Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:             string   Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property docType:             docType  Index (IS_OPTN) read FdocType write SetdocType stored docType_Specified;
    property contactPhone:        string   Index (IS_OPTN) read FcontactPhone write SetcontactPhone stored contactPhone_Specified;
  end;



  // ************************************************************************ //
  // XML       : role, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  role = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiReservationCancelInfo, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiReservationCancelInfo = class(TRemotable)
  private
    FbankAccountNumber: string;
    FbankAccountNumber_Specified: boolean;
    procedure SetbankAccountNumber(Index: Integer; const Astring: string);
    function  bankAccountNumber_Specified(Index: Integer): boolean;
  published
    property bankAccountNumber: string  Index (IS_OPTN) read FbankAccountNumber write SetbankAccountNumber stored bankAccountNumber_Specified;
  end;

  PWSResultPriceDetails = array of stickDiscount;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : discount, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  discount = class(TRemotable)
  private
    Fpercent: Boolean;
    FdefaultDis: Boolean;
    FvalueAfterDiscount: Single;
    FvalueAfterDiscount_Specified: boolean;
    FdiscountValue: Single;
    FdiscountValue_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    Fdescription: string;
    Fdescription_Specified: boolean;
    procedure SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
    function  valueAfterDiscount_Specified(Index: Integer): boolean;
    procedure SetdiscountValue(Index: Integer; const ASingle: Single);
    function  discountValue_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
    procedure Setdescription(Index: Integer; const Astring: string);
    function  description_Specified(Index: Integer): boolean;
  published
    property percent:            Boolean  Index (IS_ATTR) read Fpercent write Fpercent;
    property defaultDis:         Boolean  Index (IS_ATTR) read FdefaultDis write FdefaultDis;
    property valueAfterDiscount: Single   Index (IS_ATTR or IS_OPTN) read FvalueAfterDiscount write SetvalueAfterDiscount stored valueAfterDiscount_Specified;
    property discountValue:      Single   Index (IS_ATTR or IS_OPTN) read FdiscountValue write SetdiscountValue stored discountValue_Specified;
    property name_:              string   Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:               string   Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
    property description:        string   Index (IS_OPTN) read Fdescription write Setdescription stored description_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSWebServiceUser, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSWebServiceUser = class(TRemotable)
  private
    Fblocked: Boolean;
    Fblocked_Specified: boolean;
    FvalidFrom: TXSDateTime;
    FvalidFrom_Specified: boolean;
    FvalidTo: TXSDateTime;
    FvalidTo_Specified: boolean;
    FsystemUserId: Int64;
    FsystemUserId_Specified: boolean;
    Flogin: string;
    Flogin_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    procedure Setblocked(Index: Integer; const ABoolean: Boolean);
    function  blocked_Specified(Index: Integer): boolean;
    procedure SetvalidFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validFrom_Specified(Index: Integer): boolean;
    procedure SetvalidTo(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  validTo_Specified(Index: Integer): boolean;
    procedure SetsystemUserId(Index: Integer; const AInt64: Int64);
    function  systemUserId_Specified(Index: Integer): boolean;
    procedure Setlogin(Index: Integer; const Astring: string);
    function  login_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property blocked:      Boolean      Index (IS_ATTR or IS_OPTN) read Fblocked write Setblocked stored blocked_Specified;
    property validFrom:    TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidFrom write SetvalidFrom stored validFrom_Specified;
    property validTo:      TXSDateTime  Index (IS_ATTR or IS_OPTN) read FvalidTo write SetvalidTo stored validTo_Specified;
    property systemUserId: Int64        Index (IS_ATTR or IS_OPTN) read FsystemUserId write SetsystemUserId stored systemUserId_Specified;
    property login:        string       Index (IS_OPTN) read Flogin write Setlogin stored login_Specified;
    property forename:     string       Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:      string       Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property phone:        string       Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property email:        string       Index (IS_OPTN) read Femail write Setemail stored email_Specified;
  end;

  PWSTiPeriodicTickets = array of PWSTiPeriodicTicketInfo;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : PWSTiReservationDone, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiReservationDone = class(TRemotable)
  private
    Fid: PWSTiReservationId;
    Fid_Specified: boolean;
    FPWSTiPeriodicTicketInfo: PWSTiPeriodicTickets;
    FPWSTiPeriodicTicketInfo_Specified: boolean;
    procedure Setid(Index: Integer; const APWSTiReservationId: PWSTiReservationId);
    function  id_Specified(Index: Integer): boolean;
    procedure SetPWSTiPeriodicTicketInfo(Index: Integer; const APWSTiPeriodicTickets: PWSTiPeriodicTickets);
    function  PWSTiPeriodicTicketInfo_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:                      PWSTiReservationId    Index (IS_OPTN) read Fid write Setid stored id_Specified;
    property PWSTiPeriodicTicketInfo: PWSTiPeriodicTickets  Index (IS_OPTN or IS_UNBD) read FPWSTiPeriodicTicketInfo write SetPWSTiPeriodicTicketInfo stored PWSTiPeriodicTicketInfo_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSRelationParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSRelationParams = class(TRemotable)
  private
    FconnectionId: Int64;
    FconnectionId_Specified: boolean;
    procedure SetconnectionId(Index: Integer; const AInt64: Int64);
    function  connectionId_Specified(Index: Integer): boolean;
  published
    property connectionId: Int64  Index (IS_ATTR or IS_OPTN) read FconnectionId write SetconnectionId stored connectionId_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCarrierDetails, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrierDetails = class(TRemotable)
  private
    Fcarrier: PWSCarrier;
    Fcarrier_Specified: boolean;
    Fcard: card;
    Fcard_Specified: boolean;
    procedure Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
    function  carrier_Specified(Index: Integer): boolean;
    procedure Setcard(Index: Integer; const Acard: card);
    function  card_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property carrier: PWSCarrier  Index (IS_OPTN) read Fcarrier write Setcarrier stored carrier_Specified;
    property card:    card        Index (IS_OPTN) read Fcard write Setcard stored card_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCarrier, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrier = class(TRemotable)
  private
    Fid: Int64;
    Fname_: string;
    Fname__Specified: boolean;
    FcarrierType: carrierType2;
    FcarrierType_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetcarrierType(Index: Integer; const AcarrierType2: carrierType2);
    function  carrierType_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:          Int64         Index (IS_ATTR) read Fid write Fid;
    property name_:       string        Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property carrierType: carrierType2  Index (IS_OPTN) read FcarrierType write SetcarrierType stored carrierType_Specified;
  end;



  // ************************************************************************ //
  // XML       : card, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  card = class(TRemotable)
  private
    FcarrierId: Int64;
    Faddress: address;
    Faddress_Specified: boolean;
    FcarrierName: string;
    FcarrierName_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    Ffax: string;
    Ffax_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    Fwww: string;
    Fwww_Specified: boolean;
    FcompanyDescription: string;
    FcompanyDescription_Specified: boolean;
    procedure Setaddress(Index: Integer; const Aaddress: address);
    function  address_Specified(Index: Integer): boolean;
    procedure SetcarrierName(Index: Integer; const Astring: string);
    function  carrierName_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
    procedure Setfax(Index: Integer; const Astring: string);
    function  fax_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure Setwww(Index: Integer; const Astring: string);
    function  www_Specified(Index: Integer): boolean;
    procedure SetcompanyDescription(Index: Integer; const Astring: string);
    function  companyDescription_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property carrierId:          Int64    Index (IS_ATTR) read FcarrierId write FcarrierId;
    property address:            address  Index (IS_OPTN) read Faddress write Setaddress stored address_Specified;
    property carrierName:        string   Index (IS_OPTN) read FcarrierName write SetcarrierName stored carrierName_Specified;
    property email:              string   Index (IS_OPTN) read Femail write Setemail stored email_Specified;
    property fax:                string   Index (IS_OPTN) read Ffax write Setfax stored fax_Specified;
    property phone:              string   Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property www:                string   Index (IS_OPTN) read Fwww write Setwww stored www_Specified;
    property companyDescription: string   Index (IS_OPTN) read FcompanyDescription write SetcompanyDescription stored companyDescription_Specified;
  end;



  // ************************************************************************ //
  // XML       : address, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  address = class(TRemotable)
  private
    FbuildingNumber: string;
    FbuildingNumber_Specified: boolean;
    FlocalNumber: string;
    FlocalNumber_Specified: boolean;
    FpostalCode: string;
    FpostalCode_Specified: boolean;
    Fstreet: string;
    Fstreet_Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    procedure SetbuildingNumber(Index: Integer; const Astring: string);
    function  buildingNumber_Specified(Index: Integer): boolean;
    procedure SetlocalNumber(Index: Integer; const Astring: string);
    function  localNumber_Specified(Index: Integer): boolean;
    procedure SetpostalCode(Index: Integer; const Astring: string);
    function  postalCode_Specified(Index: Integer): boolean;
    procedure Setstreet(Index: Integer; const Astring: string);
    function  street_Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
  published
    property buildingNumber: string  Index (IS_OPTN) read FbuildingNumber write SetbuildingNumber stored buildingNumber_Specified;
    property localNumber:    string  Index (IS_OPTN) read FlocalNumber write SetlocalNumber stored localNumber_Specified;
    property postalCode:     string  Index (IS_OPTN) read FpostalCode write SetpostalCode stored postalCode_Specified;
    property street:         string  Index (IS_OPTN) read Fstreet write Setstreet stored street_Specified;
    property cityName:       string  Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiSendTicketInfo, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSendTicketInfo = class(TRemotable)
  private
    FignoreSmsCountBounds: Boolean;
    FsendingData: PWSTiSendingData;
    FsendingData_Specified: boolean;
    FsendingCode: string;
    FsendingCode_Specified: boolean;
    procedure SetsendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
    function  sendingData_Specified(Index: Integer): boolean;
    procedure SetsendingCode(Index: Integer; const Astring: string);
    function  sendingCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ignoreSmsCountBounds: Boolean           Index (IS_ATTR) read FignoreSmsCountBounds write FignoreSmsCountBounds;
    property sendingData:          PWSTiSendingData  Index (IS_OPTN) read FsendingData write SetsendingData stored sendingData_Specified;
    property sendingCode:          string            Index (IS_OPTN) read FsendingCode write SetsendingCode stored sendingCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : relation, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  relation = class(TRemotable)
  private
    FfirstStopId: Int64;
    FfirstStopId_Specified: boolean;
    FlastStopId: Int64;
    FlastStopId_Specified: boolean;
    FbunchesCount: Int64;
    FfirstCity: PWSFullyQualifiedCity;
    FfirstCity_Specified: boolean;
    FlastCity: PWSFullyQualifiedCity;
    FlastCity_Specified: boolean;
    procedure SetfirstStopId(Index: Integer; const AInt64: Int64);
    function  firstStopId_Specified(Index: Integer): boolean;
    procedure SetlastStopId(Index: Integer; const AInt64: Int64);
    function  lastStopId_Specified(Index: Integer): boolean;
    procedure SetfirstCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  firstCity_Specified(Index: Integer): boolean;
    procedure SetlastCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  lastCity_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property firstStopId:  Int64                  Index (IS_ATTR or IS_OPTN) read FfirstStopId write SetfirstStopId stored firstStopId_Specified;
    property lastStopId:   Int64                  Index (IS_ATTR or IS_OPTN) read FlastStopId write SetlastStopId stored lastStopId_Specified;
    property bunchesCount: Int64                  Index (IS_ATTR) read FbunchesCount write FbunchesCount;
    property firstCity:    PWSFullyQualifiedCity  Index (IS_OPTN) read FfirstCity write SetfirstCity stored firstCity_Specified;
    property lastCity:     PWSFullyQualifiedCity  Index (IS_OPTN) read FlastCity write SetlastCity stored lastCity_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSStopInTimeForTimeTable, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSStopInTimeForTimeTable = class(TRemotable)
  private
    FsequenceNumber: Int64;
    Ftime: TXSDateTime;
    Ftime_Specified: boolean;
    FarrivalTime: TXSDateTime;
    FarrivalTime_Specified: boolean;
    FdistanceFromFirst: Int64;
    Fid: Int64;
    Fprice: Single;
    Fprice_Specified: boolean;
    Fconnection: PWSConnection;
    Fconnection_Specified: boolean;
    Fcarrier: PWSCarrier;
    Fcarrier_Specified: boolean;
    Fstop: PWSStop;
    Fstop_Specified: boolean;
    procedure Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  time_Specified(Index: Integer): boolean;
    procedure SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  arrivalTime_Specified(Index: Integer): boolean;
    procedure Setprice(Index: Integer; const ASingle: Single);
    function  price_Specified(Index: Integer): boolean;
    procedure Setconnection(Index: Integer; const APWSConnection: PWSConnection);
    function  connection_Specified(Index: Integer): boolean;
    procedure Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
    function  carrier_Specified(Index: Integer): boolean;
    procedure Setstop(Index: Integer; const APWSStop: PWSStop);
    function  stop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property sequenceNumber:    Int64          Index (IS_ATTR) read FsequenceNumber write FsequenceNumber;
    property time:              TXSDateTime    Index (IS_ATTR or IS_OPTN) read Ftime write Settime stored time_Specified;
    property arrivalTime:       TXSDateTime    Index (IS_ATTR or IS_OPTN) read FarrivalTime write SetarrivalTime stored arrivalTime_Specified;
    property distanceFromFirst: Int64          Index (IS_ATTR) read FdistanceFromFirst write FdistanceFromFirst;
    property id:                Int64          Index (IS_ATTR) read Fid write Fid;
    property price:             Single         Index (IS_ATTR or IS_OPTN) read Fprice write Setprice stored price_Specified;
    property connection:        PWSConnection  Index (IS_OPTN) read Fconnection write Setconnection stored connection_Specified;
    property carrier:           PWSCarrier     Index (IS_OPTN) read Fcarrier write Setcarrier stored carrier_Specified;
    property stop:              PWSStop        Index (IS_OPTN) read Fstop write Setstop stored stop_Specified;
  end;



  // ************************************************************************ //
  // XML       : price, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  price2 = class(TRemotable)
  private
    FgrossPrice: Single;
    FgrossPrice_Specified: boolean;
    FvatRate: Single;
    FvatRate_Specified: boolean;
    Fcountry: country2;
    Fcountry_Specified: boolean;
    procedure SetgrossPrice(Index: Integer; const ASingle: Single);
    function  grossPrice_Specified(Index: Integer): boolean;
    procedure SetvatRate(Index: Integer; const ASingle: Single);
    function  vatRate_Specified(Index: Integer): boolean;
    procedure Setcountry(Index: Integer; const Acountry2: country2);
    function  country_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property grossPrice: Single    Index (IS_ATTR or IS_OPTN) read FgrossPrice write SetgrossPrice stored grossPrice_Specified;
    property vatRate:    Single    Index (IS_ATTR or IS_OPTN) read FvatRate write SetvatRate stored vatRate_Specified;
    property country:    country2  Index (IS_OPTN) read Fcountry write Setcountry stored country_Specified;
  end;



  // ************************************************************************ //
  // XML       : country, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  country2 = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:  string  Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiSendTicketFormat, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSendTicketFormat = class(TRemotable)
  private
    FpathToJasperFormatFile: string;
    FpathToJasperFormatFile_Specified: boolean;
    FpathToLogoImage: string;
    FpathToLogoImage_Specified: boolean;
    procedure SetpathToJasperFormatFile(Index: Integer; const Astring: string);
    function  pathToJasperFormatFile_Specified(Index: Integer): boolean;
    procedure SetpathToLogoImage(Index: Integer; const Astring: string);
    function  pathToLogoImage_Specified(Index: Integer): boolean;
  published
    property pathToJasperFormatFile: string  Index (IS_OPTN) read FpathToJasperFormatFile write SetpathToJasperFormatFile stored pathToJasperFormatFile_Specified;
    property pathToLogoImage:        string  Index (IS_OPTN) read FpathToLogoImage write SetpathToLogoImage stored pathToLogoImage_Specified;
  end;

  PWSOpinionsForCarrier = array of opinion;     { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : opinion, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  opinion = class(TRemotable)
  private
    FopinionDeegree: Integer;
    FaddingDateTime: TXSDateTime;
    FaddingDateTime_Specified: boolean;
    FopinionText: string;
    FopinionText_Specified: boolean;
    FipAddress: string;
    FipAddress_Specified: boolean;
    Fnickname: string;
    Fnickname_Specified: boolean;
    procedure SetaddingDateTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  addingDateTime_Specified(Index: Integer): boolean;
    procedure SetopinionText(Index: Integer; const Astring: string);
    function  opinionText_Specified(Index: Integer): boolean;
    procedure SetipAddress(Index: Integer; const Astring: string);
    function  ipAddress_Specified(Index: Integer): boolean;
    procedure Setnickname(Index: Integer; const Astring: string);
    function  nickname_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property opinionDeegree: Integer      Index (IS_ATTR) read FopinionDeegree write FopinionDeegree;
    property addingDateTime: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FaddingDateTime write SetaddingDateTime stored addingDateTime_Specified;
    property opinionText:    string       Index (IS_OPTN) read FopinionText write SetopinionText stored opinionText_Specified;
    property ipAddress:      string       Index (IS_OPTN) read FipAddress write SetipAddress stored ipAddress_Specified;
    property nickname:       string       Index (IS_OPTN) read Fnickname write Setnickname stored nickname_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSWaypoint, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSWaypoint = class(TRemotable)
  private
    Flatitude: Double;
    Flatitude_Specified: boolean;
    Flongitude: Double;
    Flongitude_Specified: boolean;
    FtimeOfRecording: TXSDateTime;
    FtimeOfRecording_Specified: boolean;
    Fstatus: Integer;
    Fstatus_Specified: boolean;
    FroadPointNumber: Integer;
    FroadPointNumber_Specified: boolean;
    FlastRoadPointNo: Integer;
    FlastRoadPointNo_Specified: boolean;
    FLRPTime: TXSDateTime;
    FLRPTime_Specified: boolean;
    procedure Setlatitude(Index: Integer; const ADouble: Double);
    function  latitude_Specified(Index: Integer): boolean;
    procedure Setlongitude(Index: Integer; const ADouble: Double);
    function  longitude_Specified(Index: Integer): boolean;
    procedure SettimeOfRecording(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  timeOfRecording_Specified(Index: Integer): boolean;
    procedure Setstatus(Index: Integer; const AInteger: Integer);
    function  status_Specified(Index: Integer): boolean;
    procedure SetroadPointNumber(Index: Integer; const AInteger: Integer);
    function  roadPointNumber_Specified(Index: Integer): boolean;
    procedure SetlastRoadPointNo(Index: Integer; const AInteger: Integer);
    function  lastRoadPointNo_Specified(Index: Integer): boolean;
    procedure SetLRPTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  LRPTime_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property latitude:        Double       Index (IS_ATTR or IS_OPTN) read Flatitude write Setlatitude stored latitude_Specified;
    property longitude:       Double       Index (IS_ATTR or IS_OPTN) read Flongitude write Setlongitude stored longitude_Specified;
    property timeOfRecording: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FtimeOfRecording write SettimeOfRecording stored timeOfRecording_Specified;
    property status:          Integer      Index (IS_ATTR or IS_OPTN) read Fstatus write Setstatus stored status_Specified;
    property roadPointNumber: Integer      Index (IS_ATTR or IS_OPTN) read FroadPointNumber write SetroadPointNumber stored roadPointNumber_Specified;
    property lastRoadPointNo: Integer      Index (IS_ATTR or IS_OPTN) read FlastRoadPointNo write SetlastRoadPointNo stored lastRoadPointNo_Specified;
    property LRPTime:         TXSDateTime  Index (IS_ATTR or IS_OPTN) read FLRPTime write SetLRPTime stored LRPTime_Specified;
  end;



  // ************************************************************************ //
  // XML       : driver, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  driver = class(TRemotable)
  private
    Fforname: string;
    Fforname_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    FdriverId: string;
    FdriverId_Specified: boolean;
    procedure Setforname(Index: Integer; const Astring: string);
    function  forname_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure SetdriverId(Index: Integer; const Astring: string);
    function  driverId_Specified(Index: Integer): boolean;
  published
    property forname:  string  Index (IS_OPTN) read Fforname write Setforname stored forname_Specified;
    property surname:  string  Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property driverId: string  Index (IS_OPTN) read FdriverId write SetdriverId stored driverId_Specified;
  end;



  // ************************************************************************ //
  // XML       : reservation, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  reservation = class(TRemotable)
  private
    FreservationDate: TXSDateTime;
    FreservationDate_Specified: boolean;
    FrollbackDate: TXSDateTime;
    FrollbackDate_Specified: boolean;
    FcommitDate: TXSDateTime;
    FcommitDate_Specified: boolean;
    FpaymentDate: TXSDateTime;
    FpaymentDate_Specified: boolean;
    FsmsSendCount: Integer;
    FsmsSendCount_Specified: boolean;
    Fid: PWSTiReservationId;
    Fid_Specified: boolean;
    Fnip: string;
    Fnip_Specified: boolean;
    procedure SetreservationDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  reservationDate_Specified(Index: Integer): boolean;
    procedure SetrollbackDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  rollbackDate_Specified(Index: Integer): boolean;
    procedure SetcommitDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  commitDate_Specified(Index: Integer): boolean;
    procedure SetpaymentDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  paymentDate_Specified(Index: Integer): boolean;
    procedure SetsmsSendCount(Index: Integer; const AInteger: Integer);
    function  smsSendCount_Specified(Index: Integer): boolean;
    procedure Setid(Index: Integer; const APWSTiReservationId: PWSTiReservationId);
    function  id_Specified(Index: Integer): boolean;
    procedure Setnip(Index: Integer; const Astring: string);
    function  nip_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property reservationDate: TXSDateTime         Index (IS_ATTR or IS_OPTN) read FreservationDate write SetreservationDate stored reservationDate_Specified;
    property rollbackDate:    TXSDateTime         Index (IS_ATTR or IS_OPTN) read FrollbackDate write SetrollbackDate stored rollbackDate_Specified;
    property commitDate:      TXSDateTime         Index (IS_ATTR or IS_OPTN) read FcommitDate write SetcommitDate stored commitDate_Specified;
    property paymentDate:     TXSDateTime         Index (IS_ATTR or IS_OPTN) read FpaymentDate write SetpaymentDate stored paymentDate_Specified;
    property smsSendCount:    Integer             Index (IS_ATTR or IS_OPTN) read FsmsSendCount write SetsmsSendCount stored smsSendCount_Specified;
    property id:              PWSTiReservationId  Index (IS_OPTN) read Fid write Setid stored id_Specified;
    property nip:             string              Index (IS_OPTN) read Fnip write Setnip stored nip_Specified;
  end;



  // ************************************************************************ //
  // XML       : payer, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  payer = class(TRemotable)
  private
    Fid: Int64;
    Fid_Specified: boolean;
    FcityId: Int64;
    FcityId_Specified: boolean;
    FdefaultPeriodicCardId: Int64;
    FdefaultPeriodicCardId_Specified: boolean;
    FcompanyCityId: Int64;
    FcompanyCityId_Specified: boolean;
    FdefaultSendingType: PWSEnumParam;
    FdefaultSendingType_Specified: boolean;
    FdefaultSendingAddres: string;
    FdefaultSendingAddres_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    FdocType: PWSTiDocType;
    FdocType_Specified: boolean;
    FidentifyingDocValue: string;
    FidentifyingDocValue_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    FpostalCode: string;
    FpostalCode_Specified: boolean;
    Fstreet: string;
    Fstreet_Specified: boolean;
    FbuildingNumber: string;
    FbuildingNumber_Specified: boolean;
    FcompanyName: string;
    FcompanyName_Specified: boolean;
    FcompanyStreet: string;
    FcompanyStreet_Specified: boolean;
    FcompanyBuildingNumber: string;
    FcompanyBuildingNumber_Specified: boolean;
    FcompanyPostalCode: string;
    FcompanyPostalCode_Specified: boolean;
    FcompanyNip: string;
    FcompanyNip_Specified: boolean;
    procedure Setid(Index: Integer; const AInt64: Int64);
    function  id_Specified(Index: Integer): boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
    function  defaultPeriodicCardId_Specified(Index: Integer): boolean;
    procedure SetcompanyCityId(Index: Integer; const AInt64: Int64);
    function  companyCityId_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingType(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  defaultSendingType_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingAddres(Index: Integer; const Astring: string);
    function  defaultSendingAddres_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
    function  docType_Specified(Index: Integer): boolean;
    procedure SetidentifyingDocValue(Index: Integer; const Astring: string);
    function  identifyingDocValue_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure SetpostalCode(Index: Integer; const Astring: string);
    function  postalCode_Specified(Index: Integer): boolean;
    procedure Setstreet(Index: Integer; const Astring: string);
    function  street_Specified(Index: Integer): boolean;
    procedure SetbuildingNumber(Index: Integer; const Astring: string);
    function  buildingNumber_Specified(Index: Integer): boolean;
    procedure SetcompanyName(Index: Integer; const Astring: string);
    function  companyName_Specified(Index: Integer): boolean;
    procedure SetcompanyStreet(Index: Integer; const Astring: string);
    function  companyStreet_Specified(Index: Integer): boolean;
    procedure SetcompanyBuildingNumber(Index: Integer; const Astring: string);
    function  companyBuildingNumber_Specified(Index: Integer): boolean;
    procedure SetcompanyPostalCode(Index: Integer; const Astring: string);
    function  companyPostalCode_Specified(Index: Integer): boolean;
    procedure SetcompanyNip(Index: Integer; const Astring: string);
    function  companyNip_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:                    Int64         Index (IS_ATTR or IS_OPTN) read Fid write Setid stored id_Specified;
    property cityId:                Int64         Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property defaultPeriodicCardId: Int64         Index (IS_ATTR or IS_OPTN) read FdefaultPeriodicCardId write SetdefaultPeriodicCardId stored defaultPeriodicCardId_Specified;
    property companyCityId:         Int64         Index (IS_ATTR or IS_OPTN) read FcompanyCityId write SetcompanyCityId stored companyCityId_Specified;
    property defaultSendingType:    PWSEnumParam  Index (IS_OPTN) read FdefaultSendingType write SetdefaultSendingType stored defaultSendingType_Specified;
    property defaultSendingAddres:  string        Index (IS_OPTN) read FdefaultSendingAddres write SetdefaultSendingAddres stored defaultSendingAddres_Specified;
    property forename:              string        Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property surname:               string        Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property docType:               PWSTiDocType  Index (IS_OPTN) read FdocType write SetdocType stored docType_Specified;
    property identifyingDocValue:   string        Index (IS_OPTN) read FidentifyingDocValue write SetidentifyingDocValue stored identifyingDocValue_Specified;
    property email:                 string        Index (IS_OPTN) read Femail write Setemail stored email_Specified;
    property phone:                 string        Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property postalCode:            string        Index (IS_OPTN) read FpostalCode write SetpostalCode stored postalCode_Specified;
    property street:                string        Index (IS_OPTN) read Fstreet write Setstreet stored street_Specified;
    property buildingNumber:        string        Index (IS_OPTN) read FbuildingNumber write SetbuildingNumber stored buildingNumber_Specified;
    property companyName:           string        Index (IS_OPTN) read FcompanyName write SetcompanyName stored companyName_Specified;
    property companyStreet:         string        Index (IS_OPTN) read FcompanyStreet write SetcompanyStreet stored companyStreet_Specified;
    property companyBuildingNumber: string        Index (IS_OPTN) read FcompanyBuildingNumber write SetcompanyBuildingNumber stored companyBuildingNumber_Specified;
    property companyPostalCode:     string        Index (IS_OPTN) read FcompanyPostalCode write SetcompanyPostalCode stored companyPostalCode_Specified;
    property companyNip:            string        Index (IS_OPTN) read FcompanyNip write SetcompanyNip stored companyNip_Specified;
  end;



  // ************************************************************************ //
  // XML       : place, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  place2 = class(TRemotable)
  private
    Fid: Int64;
    Fid_Specified: boolean;
    FplaceNumber: Integer;
    FplaceNumber_Specified: boolean;
    FcancelDate: TXSDateTime;
    FcancelDate_Specified: boolean;
    Fdiscount: PWSTiDiscount;
    Fdiscount_Specified: boolean;
    Fluggage: PWSTiTariffForStick;
    Fluggage_Specified: boolean;
    procedure Setid(Index: Integer; const AInt64: Int64);
    function  id_Specified(Index: Integer): boolean;
    procedure SetplaceNumber(Index: Integer; const AInteger: Integer);
    function  placeNumber_Specified(Index: Integer): boolean;
    procedure SetcancelDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  cancelDate_Specified(Index: Integer): boolean;
    procedure Setdiscount(Index: Integer; const APWSTiDiscount: PWSTiDiscount);
    function  discount_Specified(Index: Integer): boolean;
    procedure Setluggage(Index: Integer; const APWSTiTariffForStick: PWSTiTariffForStick);
    function  luggage_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property id:          Int64                Index (IS_ATTR or IS_OPTN) read Fid write Setid stored id_Specified;
    property placeNumber: Integer              Index (IS_ATTR or IS_OPTN) read FplaceNumber write SetplaceNumber stored placeNumber_Specified;
    property cancelDate:  TXSDateTime          Index (IS_ATTR or IS_OPTN) read FcancelDate write SetcancelDate stored cancelDate_Specified;
    property discount:    PWSTiDiscount        Index (IS_OPTN) read Fdiscount write Setdiscount stored discount_Specified;
    property luggage:     PWSTiTariffForStick  Index (IS_OPTN) read Fluggage write Setluggage stored luggage_Specified;
  end;



  // ************************************************************************ //
  // XML       : connection, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  connection = class(TRemotable)
  private
    FmillisBeforeFinish: Int64;
    FmillisBeforeFinish_Specified: boolean;
    FfromStop: PWSTiStopInTime;
    FfromStop_Specified: boolean;
    FtoStop: PWSTiStopInTime;
    FtoStop_Specified: boolean;
    procedure SetmillisBeforeFinish(Index: Integer; const AInt64: Int64);
    function  millisBeforeFinish_Specified(Index: Integer): boolean;
    procedure SetfromStop(Index: Integer; const APWSTiStopInTime: PWSTiStopInTime);
    function  fromStop_Specified(Index: Integer): boolean;
    procedure SettoStop(Index: Integer; const APWSTiStopInTime: PWSTiStopInTime);
    function  toStop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property millisBeforeFinish: Int64            Index (IS_ATTR or IS_OPTN) read FmillisBeforeFinish write SetmillisBeforeFinish stored millisBeforeFinish_Specified;
    property fromStop:           PWSTiStopInTime  Index (IS_OPTN) read FfromStop write SetfromStop stored fromStop_Specified;
    property toStop:             PWSTiStopInTime  Index (IS_OPTN) read FtoStop write SettoStop stored toStop_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiStopInTime, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiStopInTime = class(TRemotable)
  private
    FarrivalTime: TXSDateTime;
    FarrivalTime_Specified: boolean;
    FdepartureTime: TXSDateTime;
    FdepartureTime_Specified: boolean;
    FstopName: string;
    FstopName_Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    FcommuneName: string;
    FcommuneName_Specified: boolean;
    FdistrictName: string;
    FdistrictName_Specified: boolean;
    FprovinceName: string;
    FprovinceName_Specified: boolean;
    FcountryName: string;
    FcountryName_Specified: boolean;
    procedure SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  arrivalTime_Specified(Index: Integer): boolean;
    procedure SetdepartureTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  departureTime_Specified(Index: Integer): boolean;
    procedure SetstopName(Index: Integer; const Astring: string);
    function  stopName_Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
    procedure SetcommuneName(Index: Integer; const Astring: string);
    function  communeName_Specified(Index: Integer): boolean;
    procedure SetdistrictName(Index: Integer; const Astring: string);
    function  districtName_Specified(Index: Integer): boolean;
    procedure SetprovinceName(Index: Integer; const Astring: string);
    function  provinceName_Specified(Index: Integer): boolean;
    procedure SetcountryName(Index: Integer; const Astring: string);
    function  countryName_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property arrivalTime:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FarrivalTime write SetarrivalTime stored arrivalTime_Specified;
    property departureTime: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdepartureTime write SetdepartureTime stored departureTime_Specified;
    property stopName:      string       Index (IS_OPTN) read FstopName write SetstopName stored stopName_Specified;
    property cityName:      string       Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
    property communeName:   string       Index (IS_OPTN) read FcommuneName write SetcommuneName stored communeName_Specified;
    property districtName:  string       Index (IS_OPTN) read FdistrictName write SetdistrictName stored districtName_Specified;
    property provinceName:  string       Index (IS_OPTN) read FprovinceName write SetprovinceName stored provinceName_Specified;
    property countryName:   string       Index (IS_OPTN) read FcountryName write SetcountryName stored countryName_Specified;
  end;



  // ************************************************************************ //
  // XML       : holder, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  holder2 = class(TRemotable)
  private
    FcityId: Int64;
    FcityId_Specified: boolean;
    FdefaultPeriodicCardId: Int64;
    FdefaultPeriodicCardId_Specified: boolean;
    FholderData: PWSTiHolderForTicket;
    FholderData_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    FpostalCode: string;
    FpostalCode_Specified: boolean;
    Fstreet: string;
    Fstreet_Specified: boolean;
    FbuildingNumber: string;
    FbuildingNumber_Specified: boolean;
    FdefaultSendingType: PWSEnumParam;
    FdefaultSendingType_Specified: boolean;
    FdefaultSendingAddress: string;
    FdefaultSendingAddress_Specified: boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
    function  defaultPeriodicCardId_Specified(Index: Integer): boolean;
    procedure SetholderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
    function  holderData_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure SetpostalCode(Index: Integer; const Astring: string);
    function  postalCode_Specified(Index: Integer): boolean;
    procedure Setstreet(Index: Integer; const Astring: string);
    function  street_Specified(Index: Integer): boolean;
    procedure SetbuildingNumber(Index: Integer; const Astring: string);
    function  buildingNumber_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingType(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  defaultSendingType_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingAddress(Index: Integer; const Astring: string);
    function  defaultSendingAddress_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property cityId:                Int64                 Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property defaultPeriodicCardId: Int64                 Index (IS_ATTR or IS_OPTN) read FdefaultPeriodicCardId write SetdefaultPeriodicCardId stored defaultPeriodicCardId_Specified;
    property holderData:            PWSTiHolderForTicket  Index (IS_OPTN) read FholderData write SetholderData stored holderData_Specified;
    property email:                 string                Index (IS_OPTN) read Femail write Setemail stored email_Specified;
    property phone:                 string                Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property postalCode:            string                Index (IS_OPTN) read FpostalCode write SetpostalCode stored postalCode_Specified;
    property street:                string                Index (IS_OPTN) read Fstreet write Setstreet stored street_Specified;
    property buildingNumber:        string                Index (IS_OPTN) read FbuildingNumber write SetbuildingNumber stored buildingNumber_Specified;
    property defaultSendingType:    PWSEnumParam          Index (IS_OPTN) read FdefaultSendingType write SetdefaultSendingType stored defaultSendingType_Specified;
    property defaultSendingAddress: string                Index (IS_OPTN) read FdefaultSendingAddress write SetdefaultSendingAddress stored defaultSendingAddress_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCityId, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCityId = class(TRemotable)
  private
    FcityId: Int64;
    FcityId_Specified: boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
  published
    property cityId: Int64  Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
  end;

  PWSTiSellingReport = array of listOfRecord;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : listOfRecord, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  listOfRecord = class(TRemotable)
  private
    FdataSprz: TXSDateTime;
    FdataSprz_Specified: boolean;
    FfirmaSP: Integer;
    FfirmaSP_Specified: boolean;
    FfirmaP: Integer;
    FfirmaP_Specified: boolean;
    FnrKursu: Integer;
    FnrKursu_Specified: boolean;
    FbWaznyOd: TXSDateTime;
    FbWaznyOd_Specified: boolean;
    FbWaznyDo: TXSDateTime;
    FbWaznyDo_Specified: boolean;
    FnrPP: Integer;
    FnrPP_Specified: boolean;
    FkodPP: Int64;
    FkodPP_Specified: boolean;
    FnrPD: Integer;
    FnrPD_Specified: boolean;
    FkodPD: Int64;
    FkodPD_Specified: boolean;
    Fkraj: Integer;
    Fkraj_Specified: boolean;
    FkierWL: Integer;
    FkierWL_Specified: boolean;
    FnrLinii: Integer;
    FnrLinii_Specified: boolean;
    FwarLinii: Integer;
    FwarLinii_Specified: boolean;
    FnrKier: Integer;
    FnrKier_Specified: boolean;
    FnrKP: Int64;
    FnrKP_Specified: boolean;
    FnrRF: Integer;
    FnrRF_Specified: boolean;
    FnrRZ: Integer;
    FnrRZ_Specified: boolean;
    FlpKier: Integer;
    FlpKier_Specified: boolean;
    FnrStan: Integer;
    FnrStan_Specified: boolean;
    FdataRej: TXSDateTime;
    FdataRej_Specified: boolean;
    FnrKBil: Int64;
    FnrKBil_Specified: boolean;
    FnrDok: Int64;
    FnrDok_Specified: boolean;
    FlPas: Integer;
    FlPas_Specified: boolean;
    FrodzBil: Integer;
    FrodzBil_Specified: boolean;
    FrodzBM: Integer;
    FrodzBM_Specified: boolean;
    FzapisRK: Integer;
    FzapisRK_Specified: boolean;
    Fzaokr: Integer;
    Fzaokr_Specified: boolean;
    Fdoplata: Integer;
    Fdoplata_Specified: boolean;
    FtypUlgi: Integer;
    FtypUlgi_Specified: boolean;
    FkodBind: Integer;
    FkodBind_Specified: boolean;
    FgrUlgi: Integer;
    FgrUlgi_Specified: boolean;
    FnrUlgi: Integer;
    FnrUlgi_Specified: boolean;
    FstawkaUl: Integer;
    FstawkaUl_Specified: boolean;
    FcenaBil1: Double;
    FcenaBil1_Specified: boolean;
    FkwotaBon1: Double;
    FkwotaBon1_Specified: boolean;
    FkwotaUl1: Double;
    FkwotaUl1_Specified: boolean;
    FkwotaOM1: Double;
    FkwotaOM1_Specified: boolean;
    FnrStPTU1: Integer;
    FnrStPTU1_Specified: boolean;
    FstPTU1: Double;
    FstPTU1_Specified: boolean;
    FbrutPTU1: Double;
    FbrutPTU1_Specified: boolean;
    FcenaBil2: Double;
    FcenaBil2_Specified: boolean;
    FkwotaBon2: Double;
    FkwotaBon2_Specified: boolean;
    FkwotaUl2: Double;
    FkwotaUl2_Specified: boolean;
    FkwotaOM2: Double;
    FkwotaOM2_Specified: boolean;
    FnrStPTU2: Integer;
    FnrStPTU2_Specified: boolean;
    FstPTU2: Double;
    FstPTU2_Specified: boolean;
    FbrutPTU2: Double;
    FbrutPTU2_Specified: boolean;
    FnrStPTUD: Integer;
    FnrStPTUD_Specified: boolean;
    FstPTUD: Double;
    FstPTUD_Specified: boolean;
    FkwotaDoPL: Double;
    FkwotaDoPL_Specified: boolean;
    FwartBil: Double;
    FwartBil_Specified: boolean;
    FdoZapl: Double;
    FdoZapl_Specified: boolean;
    FspZapl: Integer;
    FspZapl_Specified: boolean;
    Fwaluta: Integer;
    Fwaluta_Specified: boolean;
    Fsmb: Integer;
    Fsmb_Specified: boolean;
    FjedWal: Integer;
    FjedWal_Specified: boolean;
    FmnWal: Double;
    FmnWal_Specified: boolean;
    Fmnoznik: Double;
    Fmnoznik_Specified: boolean;
    FmnUdzPrz: Double;
    FmnUdzPrz_Specified: boolean;
    FkwotaZwr: Double;
    FkwotaZwr_Specified: boolean;
    FdataAnul: TXSDateTime;
    FdataAnul_Specified: boolean;
    FnrKasjA: Integer;
    FnrKasjA_Specified: boolean;
    FnrRapZadA: Integer;
    FnrRapZadA_Specified: boolean;
    FkmBil: Double;
    FkmBil_Specified: boolean;
    FkmKBil: Double;
    FkmKBil_Specified: boolean;
    FlKursowB: Integer;
    FlKursowB_Specified: boolean;
    FlpKursuB: Integer;
    FlpKursuB_Specified: boolean;
    FlPrzewB: Integer;
    FlPrzewB_Specified: boolean;
    FlPPrzewB: Integer;
    FlPPrzewB_Specified: boolean;
    FnrTrasy: Integer;
    FnrTrasy_Specified: boolean;
    FrelBil: Integer;
    FrelBil_Specified: boolean;
    FfirmaKM: Integer;
    FfirmaKM_Specified: boolean;
    FnrKartyM: Int64;
    FnrKartyM_Specified: boolean;
    FdokUWBezT: Boolean;
    FdokUWBezT_Specified: boolean;
    FdataWDU: TXSDateTime;
    FdataWDU_Specified: boolean;
    FdokTWBezT: Boolean;
    FdokTWBezT_Specified: boolean;
    FdataWDT: TXSDateTime;
    FdataWDT_Specified: boolean;
    FlPrzBO: Integer;
    FlPrzBO_Specified: boolean;
    FnrSTPROW: Integer;
    FnrSTPROW_Specified: boolean;
    FfirmaK: Integer;
    FfirmaK_Specified: boolean;
    FkOBCE: Integer;
    FkOBCE_Specified: boolean;
    FdataKursu: TXSDateTime;
    FdataKursu_Specified: boolean;
    Fwdk: Integer;
    Fwdk_Specified: boolean;
    FkmKursu: Double;
    FkmKursu_Specified: boolean;
    FzmKartyM: Boolean;
    FzmKartyM_Specified: boolean;
    FpominDoPL: Boolean;
    FpominDoPL_Specified: boolean;
    FnrFU: Integer;
    FnrFU_Specified: boolean;
    FdataOP: TXSDateTime;
    FdataOP_Specified: boolean;
    FnrSluzbOP: Integer;
    FnrSluzbOP_Specified: boolean;
    FgodzSprz: string;
    FgodzSprz_Specified: boolean;
    Fwariant: string;
    Fwariant_Specified: boolean;
    FgodzOdj: string;
    FgodzOdj_Specified: boolean;
    FnazwaPP: string;
    FnazwaPP_Specified: boolean;
    FnazwaPD: string;
    FnazwaPD_Specified: boolean;
    FrodzKom: string;
    FrodzKom_Specified: boolean;
    FnrZad: string;
    FnrZad_Specified: boolean;
    FliniaKm: string;
    FliniaKm_Specified: boolean;
    Fimie: string;
    Fimie_Specified: boolean;
    Fnazwisko: string;
    Fnazwisko_Specified: boolean;
    Flogo: string;
    Flogo_Specified: boolean;
    FidentRZ: string;
    FidentRZ_Specified: boolean;
    FtypRZ: string;
    FtypRZ_Specified: boolean;
    FmiesSprz: string;
    FmiesSprz_Specified: boolean;
    FmiesWazn: string;
    FmiesWazn_Specified: boolean;
    FnrBiletu: string;
    FnrBiletu_Specified: boolean;
    FtypBiletu: string;
    FtypBiletu_Specified: boolean;
    FgodzPocz: string;
    FgodzPocz_Specified: boolean;
    FgodzKon: string;
    FgodzKon_Specified: boolean;
    FnazUlgi: string;
    FnazUlgi_Specified: boolean;
    FnazSpZapl: string;
    FnazSpZapl_Specified: boolean;
    FoznWal: string;
    FoznWal_Specified: boolean;
    FidentRZA: string;
    FidentRZA_Specified: boolean;
    FoznaczK: string;
    FoznaczK_Specified: boolean;
    FdniRelBM: string;
    FdniRelBM_Specified: boolean;
    FnrDokUlgi: string;
    FnrDokUlgi_Specified: boolean;
    FnrPas: string;
    FnrPas_Specified: boolean;
    FnrDokTOZS: string;
    FnrDokTOZS_Specified: boolean;
    FszyfrBil: string;
    FszyfrBil_Specified: boolean;
    FrelacjaK: string;
    FrelacjaK_Specified: boolean;
    FrodzSP: string;
    FrodzSP_Specified: boolean;
    FkodKBil: string;
    FkodKBil_Specified: boolean;
    FnrKursuE: string;
    FnrKursuE_Specified: boolean;
    FgodzPrzyj: string;
    FgodzPrzyj_Specified: boolean;
    FzbiorA: string;
    FzbiorA_Specified: boolean;
    FgodzOdjK: string;
    FgodzOdjK_Specified: boolean;
    FgodzOP: string;
    FgodzOP_Specified: boolean;
    FcompanyCode: string;
    FcompanyCode_Specified: boolean;
    procedure SetdataSprz(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataSprz_Specified(Index: Integer): boolean;
    procedure SetfirmaSP(Index: Integer; const AInteger: Integer);
    function  firmaSP_Specified(Index: Integer): boolean;
    procedure SetfirmaP(Index: Integer; const AInteger: Integer);
    function  firmaP_Specified(Index: Integer): boolean;
    procedure SetnrKursu(Index: Integer; const AInteger: Integer);
    function  nrKursu_Specified(Index: Integer): boolean;
    procedure SetbWaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  bWaznyOd_Specified(Index: Integer): boolean;
    procedure SetbWaznyDo(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  bWaznyDo_Specified(Index: Integer): boolean;
    procedure SetnrPP(Index: Integer; const AInteger: Integer);
    function  nrPP_Specified(Index: Integer): boolean;
    procedure SetkodPP(Index: Integer; const AInt64: Int64);
    function  kodPP_Specified(Index: Integer): boolean;
    procedure SetnrPD(Index: Integer; const AInteger: Integer);
    function  nrPD_Specified(Index: Integer): boolean;
    procedure SetkodPD(Index: Integer; const AInt64: Int64);
    function  kodPD_Specified(Index: Integer): boolean;
    procedure Setkraj(Index: Integer; const AInteger: Integer);
    function  kraj_Specified(Index: Integer): boolean;
    procedure SetkierWL(Index: Integer; const AInteger: Integer);
    function  kierWL_Specified(Index: Integer): boolean;
    procedure SetnrLinii(Index: Integer; const AInteger: Integer);
    function  nrLinii_Specified(Index: Integer): boolean;
    procedure SetwarLinii(Index: Integer; const AInteger: Integer);
    function  warLinii_Specified(Index: Integer): boolean;
    procedure SetnrKier(Index: Integer; const AInteger: Integer);
    function  nrKier_Specified(Index: Integer): boolean;
    procedure SetnrKP(Index: Integer; const AInt64: Int64);
    function  nrKP_Specified(Index: Integer): boolean;
    procedure SetnrRF(Index: Integer; const AInteger: Integer);
    function  nrRF_Specified(Index: Integer): boolean;
    procedure SetnrRZ(Index: Integer; const AInteger: Integer);
    function  nrRZ_Specified(Index: Integer): boolean;
    procedure SetlpKier(Index: Integer; const AInteger: Integer);
    function  lpKier_Specified(Index: Integer): boolean;
    procedure SetnrStan(Index: Integer; const AInteger: Integer);
    function  nrStan_Specified(Index: Integer): boolean;
    procedure SetdataRej(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataRej_Specified(Index: Integer): boolean;
    procedure SetnrKBil(Index: Integer; const AInt64: Int64);
    function  nrKBil_Specified(Index: Integer): boolean;
    procedure SetnrDok(Index: Integer; const AInt64: Int64);
    function  nrDok_Specified(Index: Integer): boolean;
    procedure SetlPas(Index: Integer; const AInteger: Integer);
    function  lPas_Specified(Index: Integer): boolean;
    procedure SetrodzBil(Index: Integer; const AInteger: Integer);
    function  rodzBil_Specified(Index: Integer): boolean;
    procedure SetrodzBM(Index: Integer; const AInteger: Integer);
    function  rodzBM_Specified(Index: Integer): boolean;
    procedure SetzapisRK(Index: Integer; const AInteger: Integer);
    function  zapisRK_Specified(Index: Integer): boolean;
    procedure Setzaokr(Index: Integer; const AInteger: Integer);
    function  zaokr_Specified(Index: Integer): boolean;
    procedure Setdoplata(Index: Integer; const AInteger: Integer);
    function  doplata_Specified(Index: Integer): boolean;
    procedure SettypUlgi(Index: Integer; const AInteger: Integer);
    function  typUlgi_Specified(Index: Integer): boolean;
    procedure SetkodBind(Index: Integer; const AInteger: Integer);
    function  kodBind_Specified(Index: Integer): boolean;
    procedure SetgrUlgi(Index: Integer; const AInteger: Integer);
    function  grUlgi_Specified(Index: Integer): boolean;
    procedure SetnrUlgi(Index: Integer; const AInteger: Integer);
    function  nrUlgi_Specified(Index: Integer): boolean;
    procedure SetstawkaUl(Index: Integer; const AInteger: Integer);
    function  stawkaUl_Specified(Index: Integer): boolean;
    procedure SetcenaBil1(Index: Integer; const ADouble: Double);
    function  cenaBil1_Specified(Index: Integer): boolean;
    procedure SetkwotaBon1(Index: Integer; const ADouble: Double);
    function  kwotaBon1_Specified(Index: Integer): boolean;
    procedure SetkwotaUl1(Index: Integer; const ADouble: Double);
    function  kwotaUl1_Specified(Index: Integer): boolean;
    procedure SetkwotaOM1(Index: Integer; const ADouble: Double);
    function  kwotaOM1_Specified(Index: Integer): boolean;
    procedure SetnrStPTU1(Index: Integer; const AInteger: Integer);
    function  nrStPTU1_Specified(Index: Integer): boolean;
    procedure SetstPTU1(Index: Integer; const ADouble: Double);
    function  stPTU1_Specified(Index: Integer): boolean;
    procedure SetbrutPTU1(Index: Integer; const ADouble: Double);
    function  brutPTU1_Specified(Index: Integer): boolean;
    procedure SetcenaBil2(Index: Integer; const ADouble: Double);
    function  cenaBil2_Specified(Index: Integer): boolean;
    procedure SetkwotaBon2(Index: Integer; const ADouble: Double);
    function  kwotaBon2_Specified(Index: Integer): boolean;
    procedure SetkwotaUl2(Index: Integer; const ADouble: Double);
    function  kwotaUl2_Specified(Index: Integer): boolean;
    procedure SetkwotaOM2(Index: Integer; const ADouble: Double);
    function  kwotaOM2_Specified(Index: Integer): boolean;
    procedure SetnrStPTU2(Index: Integer; const AInteger: Integer);
    function  nrStPTU2_Specified(Index: Integer): boolean;
    procedure SetstPTU2(Index: Integer; const ADouble: Double);
    function  stPTU2_Specified(Index: Integer): boolean;
    procedure SetbrutPTU2(Index: Integer; const ADouble: Double);
    function  brutPTU2_Specified(Index: Integer): boolean;
    procedure SetnrStPTUD(Index: Integer; const AInteger: Integer);
    function  nrStPTUD_Specified(Index: Integer): boolean;
    procedure SetstPTUD(Index: Integer; const ADouble: Double);
    function  stPTUD_Specified(Index: Integer): boolean;
    procedure SetkwotaDoPL(Index: Integer; const ADouble: Double);
    function  kwotaDoPL_Specified(Index: Integer): boolean;
    procedure SetwartBil(Index: Integer; const ADouble: Double);
    function  wartBil_Specified(Index: Integer): boolean;
    procedure SetdoZapl(Index: Integer; const ADouble: Double);
    function  doZapl_Specified(Index: Integer): boolean;
    procedure SetspZapl(Index: Integer; const AInteger: Integer);
    function  spZapl_Specified(Index: Integer): boolean;
    procedure Setwaluta(Index: Integer; const AInteger: Integer);
    function  waluta_Specified(Index: Integer): boolean;
    procedure Setsmb(Index: Integer; const AInteger: Integer);
    function  smb_Specified(Index: Integer): boolean;
    procedure SetjedWal(Index: Integer; const AInteger: Integer);
    function  jedWal_Specified(Index: Integer): boolean;
    procedure SetmnWal(Index: Integer; const ADouble: Double);
    function  mnWal_Specified(Index: Integer): boolean;
    procedure Setmnoznik(Index: Integer; const ADouble: Double);
    function  mnoznik_Specified(Index: Integer): boolean;
    procedure SetmnUdzPrz(Index: Integer; const ADouble: Double);
    function  mnUdzPrz_Specified(Index: Integer): boolean;
    procedure SetkwotaZwr(Index: Integer; const ADouble: Double);
    function  kwotaZwr_Specified(Index: Integer): boolean;
    procedure SetdataAnul(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataAnul_Specified(Index: Integer): boolean;
    procedure SetnrKasjA(Index: Integer; const AInteger: Integer);
    function  nrKasjA_Specified(Index: Integer): boolean;
    procedure SetnrRapZadA(Index: Integer; const AInteger: Integer);
    function  nrRapZadA_Specified(Index: Integer): boolean;
    procedure SetkmBil(Index: Integer; const ADouble: Double);
    function  kmBil_Specified(Index: Integer): boolean;
    procedure SetkmKBil(Index: Integer; const ADouble: Double);
    function  kmKBil_Specified(Index: Integer): boolean;
    procedure SetlKursowB(Index: Integer; const AInteger: Integer);
    function  lKursowB_Specified(Index: Integer): boolean;
    procedure SetlpKursuB(Index: Integer; const AInteger: Integer);
    function  lpKursuB_Specified(Index: Integer): boolean;
    procedure SetlPrzewB(Index: Integer; const AInteger: Integer);
    function  lPrzewB_Specified(Index: Integer): boolean;
    procedure SetlPPrzewB(Index: Integer; const AInteger: Integer);
    function  lPPrzewB_Specified(Index: Integer): boolean;
    procedure SetnrTrasy(Index: Integer; const AInteger: Integer);
    function  nrTrasy_Specified(Index: Integer): boolean;
    procedure SetrelBil(Index: Integer; const AInteger: Integer);
    function  relBil_Specified(Index: Integer): boolean;
    procedure SetfirmaKM(Index: Integer; const AInteger: Integer);
    function  firmaKM_Specified(Index: Integer): boolean;
    procedure SetnrKartyM(Index: Integer; const AInt64: Int64);
    function  nrKartyM_Specified(Index: Integer): boolean;
    procedure SetdokUWBezT(Index: Integer; const ABoolean: Boolean);
    function  dokUWBezT_Specified(Index: Integer): boolean;
    procedure SetdataWDU(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataWDU_Specified(Index: Integer): boolean;
    procedure SetdokTWBezT(Index: Integer; const ABoolean: Boolean);
    function  dokTWBezT_Specified(Index: Integer): boolean;
    procedure SetdataWDT(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataWDT_Specified(Index: Integer): boolean;
    procedure SetlPrzBO(Index: Integer; const AInteger: Integer);
    function  lPrzBO_Specified(Index: Integer): boolean;
    procedure SetnrSTPROW(Index: Integer; const AInteger: Integer);
    function  nrSTPROW_Specified(Index: Integer): boolean;
    procedure SetfirmaK(Index: Integer; const AInteger: Integer);
    function  firmaK_Specified(Index: Integer): boolean;
    procedure SetkOBCE(Index: Integer; const AInteger: Integer);
    function  kOBCE_Specified(Index: Integer): boolean;
    procedure SetdataKursu(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataKursu_Specified(Index: Integer): boolean;
    procedure Setwdk(Index: Integer; const AInteger: Integer);
    function  wdk_Specified(Index: Integer): boolean;
    procedure SetkmKursu(Index: Integer; const ADouble: Double);
    function  kmKursu_Specified(Index: Integer): boolean;
    procedure SetzmKartyM(Index: Integer; const ABoolean: Boolean);
    function  zmKartyM_Specified(Index: Integer): boolean;
    procedure SetpominDoPL(Index: Integer; const ABoolean: Boolean);
    function  pominDoPL_Specified(Index: Integer): boolean;
    procedure SetnrFU(Index: Integer; const AInteger: Integer);
    function  nrFU_Specified(Index: Integer): boolean;
    procedure SetdataOP(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  dataOP_Specified(Index: Integer): boolean;
    procedure SetnrSluzbOP(Index: Integer; const AInteger: Integer);
    function  nrSluzbOP_Specified(Index: Integer): boolean;
    procedure SetgodzSprz(Index: Integer; const Astring: string);
    function  godzSprz_Specified(Index: Integer): boolean;
    procedure Setwariant(Index: Integer; const Astring: string);
    function  wariant_Specified(Index: Integer): boolean;
    procedure SetgodzOdj(Index: Integer; const Astring: string);
    function  godzOdj_Specified(Index: Integer): boolean;
    procedure SetnazwaPP(Index: Integer; const Astring: string);
    function  nazwaPP_Specified(Index: Integer): boolean;
    procedure SetnazwaPD(Index: Integer; const Astring: string);
    function  nazwaPD_Specified(Index: Integer): boolean;
    procedure SetrodzKom(Index: Integer; const Astring: string);
    function  rodzKom_Specified(Index: Integer): boolean;
    procedure SetnrZad(Index: Integer; const Astring: string);
    function  nrZad_Specified(Index: Integer): boolean;
    procedure SetliniaKm(Index: Integer; const Astring: string);
    function  liniaKm_Specified(Index: Integer): boolean;
    procedure Setimie(Index: Integer; const Astring: string);
    function  imie_Specified(Index: Integer): boolean;
    procedure Setnazwisko(Index: Integer; const Astring: string);
    function  nazwisko_Specified(Index: Integer): boolean;
    procedure Setlogo(Index: Integer; const Astring: string);
    function  logo_Specified(Index: Integer): boolean;
    procedure SetidentRZ(Index: Integer; const Astring: string);
    function  identRZ_Specified(Index: Integer): boolean;
    procedure SettypRZ(Index: Integer; const Astring: string);
    function  typRZ_Specified(Index: Integer): boolean;
    procedure SetmiesSprz(Index: Integer; const Astring: string);
    function  miesSprz_Specified(Index: Integer): boolean;
    procedure SetmiesWazn(Index: Integer; const Astring: string);
    function  miesWazn_Specified(Index: Integer): boolean;
    procedure SetnrBiletu(Index: Integer; const Astring: string);
    function  nrBiletu_Specified(Index: Integer): boolean;
    procedure SettypBiletu(Index: Integer; const Astring: string);
    function  typBiletu_Specified(Index: Integer): boolean;
    procedure SetgodzPocz(Index: Integer; const Astring: string);
    function  godzPocz_Specified(Index: Integer): boolean;
    procedure SetgodzKon(Index: Integer; const Astring: string);
    function  godzKon_Specified(Index: Integer): boolean;
    procedure SetnazUlgi(Index: Integer; const Astring: string);
    function  nazUlgi_Specified(Index: Integer): boolean;
    procedure SetnazSpZapl(Index: Integer; const Astring: string);
    function  nazSpZapl_Specified(Index: Integer): boolean;
    procedure SetoznWal(Index: Integer; const Astring: string);
    function  oznWal_Specified(Index: Integer): boolean;
    procedure SetidentRZA(Index: Integer; const Astring: string);
    function  identRZA_Specified(Index: Integer): boolean;
    procedure SetoznaczK(Index: Integer; const Astring: string);
    function  oznaczK_Specified(Index: Integer): boolean;
    procedure SetdniRelBM(Index: Integer; const Astring: string);
    function  dniRelBM_Specified(Index: Integer): boolean;
    procedure SetnrDokUlgi(Index: Integer; const Astring: string);
    function  nrDokUlgi_Specified(Index: Integer): boolean;
    procedure SetnrPas(Index: Integer; const Astring: string);
    function  nrPas_Specified(Index: Integer): boolean;
    procedure SetnrDokTOZS(Index: Integer; const Astring: string);
    function  nrDokTOZS_Specified(Index: Integer): boolean;
    procedure SetszyfrBil(Index: Integer; const Astring: string);
    function  szyfrBil_Specified(Index: Integer): boolean;
    procedure SetrelacjaK(Index: Integer; const Astring: string);
    function  relacjaK_Specified(Index: Integer): boolean;
    procedure SetrodzSP(Index: Integer; const Astring: string);
    function  rodzSP_Specified(Index: Integer): boolean;
    procedure SetkodKBil(Index: Integer; const Astring: string);
    function  kodKBil_Specified(Index: Integer): boolean;
    procedure SetnrKursuE(Index: Integer; const Astring: string);
    function  nrKursuE_Specified(Index: Integer): boolean;
    procedure SetgodzPrzyj(Index: Integer; const Astring: string);
    function  godzPrzyj_Specified(Index: Integer): boolean;
    procedure SetzbiorA(Index: Integer; const Astring: string);
    function  zbiorA_Specified(Index: Integer): boolean;
    procedure SetgodzOdjK(Index: Integer; const Astring: string);
    function  godzOdjK_Specified(Index: Integer): boolean;
    procedure SetgodzOP(Index: Integer; const Astring: string);
    function  godzOP_Specified(Index: Integer): boolean;
    procedure SetcompanyCode(Index: Integer; const Astring: string);
    function  companyCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property dataSprz:    TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataSprz write SetdataSprz stored dataSprz_Specified;
    property firmaSP:     Integer      Index (IS_ATTR or IS_OPTN) read FfirmaSP write SetfirmaSP stored firmaSP_Specified;
    property firmaP:      Integer      Index (IS_ATTR or IS_OPTN) read FfirmaP write SetfirmaP stored firmaP_Specified;
    property nrKursu:     Integer      Index (IS_ATTR or IS_OPTN) read FnrKursu write SetnrKursu stored nrKursu_Specified;
    property bWaznyOd:    TXSDateTime  Index (IS_ATTR or IS_OPTN) read FbWaznyOd write SetbWaznyOd stored bWaznyOd_Specified;
    property bWaznyDo:    TXSDateTime  Index (IS_ATTR or IS_OPTN) read FbWaznyDo write SetbWaznyDo stored bWaznyDo_Specified;
    property nrPP:        Integer      Index (IS_ATTR or IS_OPTN) read FnrPP write SetnrPP stored nrPP_Specified;
    property kodPP:       Int64        Index (IS_ATTR or IS_OPTN) read FkodPP write SetkodPP stored kodPP_Specified;
    property nrPD:        Integer      Index (IS_ATTR or IS_OPTN) read FnrPD write SetnrPD stored nrPD_Specified;
    property kodPD:       Int64        Index (IS_ATTR or IS_OPTN) read FkodPD write SetkodPD stored kodPD_Specified;
    property kraj:        Integer      Index (IS_ATTR or IS_OPTN) read Fkraj write Setkraj stored kraj_Specified;
    property kierWL:      Integer      Index (IS_ATTR or IS_OPTN) read FkierWL write SetkierWL stored kierWL_Specified;
    property nrLinii:     Integer      Index (IS_ATTR or IS_OPTN) read FnrLinii write SetnrLinii stored nrLinii_Specified;
    property warLinii:    Integer      Index (IS_ATTR or IS_OPTN) read FwarLinii write SetwarLinii stored warLinii_Specified;
    property nrKier:      Integer      Index (IS_ATTR or IS_OPTN) read FnrKier write SetnrKier stored nrKier_Specified;
    property nrKP:        Int64        Index (IS_ATTR or IS_OPTN) read FnrKP write SetnrKP stored nrKP_Specified;
    property nrRF:        Integer      Index (IS_ATTR or IS_OPTN) read FnrRF write SetnrRF stored nrRF_Specified;
    property nrRZ:        Integer      Index (IS_ATTR or IS_OPTN) read FnrRZ write SetnrRZ stored nrRZ_Specified;
    property lpKier:      Integer      Index (IS_ATTR or IS_OPTN) read FlpKier write SetlpKier stored lpKier_Specified;
    property nrStan:      Integer      Index (IS_ATTR or IS_OPTN) read FnrStan write SetnrStan stored nrStan_Specified;
    property dataRej:     TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataRej write SetdataRej stored dataRej_Specified;
    property nrKBil:      Int64        Index (IS_ATTR or IS_OPTN) read FnrKBil write SetnrKBil stored nrKBil_Specified;
    property nrDok:       Int64        Index (IS_ATTR or IS_OPTN) read FnrDok write SetnrDok stored nrDok_Specified;
    property lPas:        Integer      Index (IS_ATTR or IS_OPTN) read FlPas write SetlPas stored lPas_Specified;
    property rodzBil:     Integer      Index (IS_ATTR or IS_OPTN) read FrodzBil write SetrodzBil stored rodzBil_Specified;
    property rodzBM:      Integer      Index (IS_ATTR or IS_OPTN) read FrodzBM write SetrodzBM stored rodzBM_Specified;
    property zapisRK:     Integer      Index (IS_ATTR or IS_OPTN) read FzapisRK write SetzapisRK stored zapisRK_Specified;
    property zaokr:       Integer      Index (IS_ATTR or IS_OPTN) read Fzaokr write Setzaokr stored zaokr_Specified;
    property doplata:     Integer      Index (IS_ATTR or IS_OPTN) read Fdoplata write Setdoplata stored doplata_Specified;
    property typUlgi:     Integer      Index (IS_ATTR or IS_OPTN) read FtypUlgi write SettypUlgi stored typUlgi_Specified;
    property kodBind:     Integer      Index (IS_ATTR or IS_OPTN) read FkodBind write SetkodBind stored kodBind_Specified;
    property grUlgi:      Integer      Index (IS_ATTR or IS_OPTN) read FgrUlgi write SetgrUlgi stored grUlgi_Specified;
    property nrUlgi:      Integer      Index (IS_ATTR or IS_OPTN) read FnrUlgi write SetnrUlgi stored nrUlgi_Specified;
    property stawkaUl:    Integer      Index (IS_ATTR or IS_OPTN) read FstawkaUl write SetstawkaUl stored stawkaUl_Specified;
    property cenaBil1:    Double       Index (IS_ATTR or IS_OPTN) read FcenaBil1 write SetcenaBil1 stored cenaBil1_Specified;
    property kwotaBon1:   Double       Index (IS_ATTR or IS_OPTN) read FkwotaBon1 write SetkwotaBon1 stored kwotaBon1_Specified;
    property kwotaUl1:    Double       Index (IS_ATTR or IS_OPTN) read FkwotaUl1 write SetkwotaUl1 stored kwotaUl1_Specified;
    property kwotaOM1:    Double       Index (IS_ATTR or IS_OPTN) read FkwotaOM1 write SetkwotaOM1 stored kwotaOM1_Specified;
    property nrStPTU1:    Integer      Index (IS_ATTR or IS_OPTN) read FnrStPTU1 write SetnrStPTU1 stored nrStPTU1_Specified;
    property stPTU1:      Double       Index (IS_ATTR or IS_OPTN) read FstPTU1 write SetstPTU1 stored stPTU1_Specified;
    property brutPTU1:    Double       Index (IS_ATTR or IS_OPTN) read FbrutPTU1 write SetbrutPTU1 stored brutPTU1_Specified;
    property cenaBil2:    Double       Index (IS_ATTR or IS_OPTN) read FcenaBil2 write SetcenaBil2 stored cenaBil2_Specified;
    property kwotaBon2:   Double       Index (IS_ATTR or IS_OPTN) read FkwotaBon2 write SetkwotaBon2 stored kwotaBon2_Specified;
    property kwotaUl2:    Double       Index (IS_ATTR or IS_OPTN) read FkwotaUl2 write SetkwotaUl2 stored kwotaUl2_Specified;
    property kwotaOM2:    Double       Index (IS_ATTR or IS_OPTN) read FkwotaOM2 write SetkwotaOM2 stored kwotaOM2_Specified;
    property nrStPTU2:    Integer      Index (IS_ATTR or IS_OPTN) read FnrStPTU2 write SetnrStPTU2 stored nrStPTU2_Specified;
    property stPTU2:      Double       Index (IS_ATTR or IS_OPTN) read FstPTU2 write SetstPTU2 stored stPTU2_Specified;
    property brutPTU2:    Double       Index (IS_ATTR or IS_OPTN) read FbrutPTU2 write SetbrutPTU2 stored brutPTU2_Specified;
    property nrStPTUD:    Integer      Index (IS_ATTR or IS_OPTN) read FnrStPTUD write SetnrStPTUD stored nrStPTUD_Specified;
    property stPTUD:      Double       Index (IS_ATTR or IS_OPTN) read FstPTUD write SetstPTUD stored stPTUD_Specified;
    property kwotaDoPL:   Double       Index (IS_ATTR or IS_OPTN) read FkwotaDoPL write SetkwotaDoPL stored kwotaDoPL_Specified;
    property wartBil:     Double       Index (IS_ATTR or IS_OPTN) read FwartBil write SetwartBil stored wartBil_Specified;
    property doZapl:      Double       Index (IS_ATTR or IS_OPTN) read FdoZapl write SetdoZapl stored doZapl_Specified;
    property spZapl:      Integer      Index (IS_ATTR or IS_OPTN) read FspZapl write SetspZapl stored spZapl_Specified;
    property waluta:      Integer      Index (IS_ATTR or IS_OPTN) read Fwaluta write Setwaluta stored waluta_Specified;
    property smb:         Integer      Index (IS_ATTR or IS_OPTN) read Fsmb write Setsmb stored smb_Specified;
    property jedWal:      Integer      Index (IS_ATTR or IS_OPTN) read FjedWal write SetjedWal stored jedWal_Specified;
    property mnWal:       Double       Index (IS_ATTR or IS_OPTN) read FmnWal write SetmnWal stored mnWal_Specified;
    property mnoznik:     Double       Index (IS_ATTR or IS_OPTN) read Fmnoznik write Setmnoznik stored mnoznik_Specified;
    property mnUdzPrz:    Double       Index (IS_ATTR or IS_OPTN) read FmnUdzPrz write SetmnUdzPrz stored mnUdzPrz_Specified;
    property kwotaZwr:    Double       Index (IS_ATTR or IS_OPTN) read FkwotaZwr write SetkwotaZwr stored kwotaZwr_Specified;
    property dataAnul:    TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataAnul write SetdataAnul stored dataAnul_Specified;
    property nrKasjA:     Integer      Index (IS_ATTR or IS_OPTN) read FnrKasjA write SetnrKasjA stored nrKasjA_Specified;
    property nrRapZadA:   Integer      Index (IS_ATTR or IS_OPTN) read FnrRapZadA write SetnrRapZadA stored nrRapZadA_Specified;
    property kmBil:       Double       Index (IS_ATTR or IS_OPTN) read FkmBil write SetkmBil stored kmBil_Specified;
    property kmKBil:      Double       Index (IS_ATTR or IS_OPTN) read FkmKBil write SetkmKBil stored kmKBil_Specified;
    property lKursowB:    Integer      Index (IS_ATTR or IS_OPTN) read FlKursowB write SetlKursowB stored lKursowB_Specified;
    property lpKursuB:    Integer      Index (IS_ATTR or IS_OPTN) read FlpKursuB write SetlpKursuB stored lpKursuB_Specified;
    property lPrzewB:     Integer      Index (IS_ATTR or IS_OPTN) read FlPrzewB write SetlPrzewB stored lPrzewB_Specified;
    property lPPrzewB:    Integer      Index (IS_ATTR or IS_OPTN) read FlPPrzewB write SetlPPrzewB stored lPPrzewB_Specified;
    property nrTrasy:     Integer      Index (IS_ATTR or IS_OPTN) read FnrTrasy write SetnrTrasy stored nrTrasy_Specified;
    property relBil:      Integer      Index (IS_ATTR or IS_OPTN) read FrelBil write SetrelBil stored relBil_Specified;
    property firmaKM:     Integer      Index (IS_ATTR or IS_OPTN) read FfirmaKM write SetfirmaKM stored firmaKM_Specified;
    property nrKartyM:    Int64        Index (IS_ATTR or IS_OPTN) read FnrKartyM write SetnrKartyM stored nrKartyM_Specified;
    property dokUWBezT:   Boolean      Index (IS_ATTR or IS_OPTN) read FdokUWBezT write SetdokUWBezT stored dokUWBezT_Specified;
    property dataWDU:     TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataWDU write SetdataWDU stored dataWDU_Specified;
    property dokTWBezT:   Boolean      Index (IS_ATTR or IS_OPTN) read FdokTWBezT write SetdokTWBezT stored dokTWBezT_Specified;
    property dataWDT:     TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataWDT write SetdataWDT stored dataWDT_Specified;
    property lPrzBO:      Integer      Index (IS_ATTR or IS_OPTN) read FlPrzBO write SetlPrzBO stored lPrzBO_Specified;
    property nrSTPROW:    Integer      Index (IS_ATTR or IS_OPTN) read FnrSTPROW write SetnrSTPROW stored nrSTPROW_Specified;
    property firmaK:      Integer      Index (IS_ATTR or IS_OPTN) read FfirmaK write SetfirmaK stored firmaK_Specified;
    property kOBCE:       Integer      Index (IS_ATTR or IS_OPTN) read FkOBCE write SetkOBCE stored kOBCE_Specified;
    property dataKursu:   TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataKursu write SetdataKursu stored dataKursu_Specified;
    property wdk:         Integer      Index (IS_ATTR or IS_OPTN) read Fwdk write Setwdk stored wdk_Specified;
    property kmKursu:     Double       Index (IS_ATTR or IS_OPTN) read FkmKursu write SetkmKursu stored kmKursu_Specified;
    property zmKartyM:    Boolean      Index (IS_ATTR or IS_OPTN) read FzmKartyM write SetzmKartyM stored zmKartyM_Specified;
    property pominDoPL:   Boolean      Index (IS_ATTR or IS_OPTN) read FpominDoPL write SetpominDoPL stored pominDoPL_Specified;
    property nrFU:        Integer      Index (IS_ATTR or IS_OPTN) read FnrFU write SetnrFU stored nrFU_Specified;
    property dataOP:      TXSDateTime  Index (IS_ATTR or IS_OPTN) read FdataOP write SetdataOP stored dataOP_Specified;
    property nrSluzbOP:   Integer      Index (IS_ATTR or IS_OPTN) read FnrSluzbOP write SetnrSluzbOP stored nrSluzbOP_Specified;
    property godzSprz:    string       Index (IS_OPTN) read FgodzSprz write SetgodzSprz stored godzSprz_Specified;
    property wariant:     string       Index (IS_OPTN) read Fwariant write Setwariant stored wariant_Specified;
    property godzOdj:     string       Index (IS_OPTN) read FgodzOdj write SetgodzOdj stored godzOdj_Specified;
    property nazwaPP:     string       Index (IS_OPTN) read FnazwaPP write SetnazwaPP stored nazwaPP_Specified;
    property nazwaPD:     string       Index (IS_OPTN) read FnazwaPD write SetnazwaPD stored nazwaPD_Specified;
    property rodzKom:     string       Index (IS_OPTN) read FrodzKom write SetrodzKom stored rodzKom_Specified;
    property nrZad:       string       Index (IS_OPTN) read FnrZad write SetnrZad stored nrZad_Specified;
    property liniaKm:     string       Index (IS_OPTN) read FliniaKm write SetliniaKm stored liniaKm_Specified;
    property imie:        string       Index (IS_OPTN) read Fimie write Setimie stored imie_Specified;
    property nazwisko:    string       Index (IS_OPTN) read Fnazwisko write Setnazwisko stored nazwisko_Specified;
    property logo:        string       Index (IS_OPTN) read Flogo write Setlogo stored logo_Specified;
    property identRZ:     string       Index (IS_OPTN) read FidentRZ write SetidentRZ stored identRZ_Specified;
    property typRZ:       string       Index (IS_OPTN) read FtypRZ write SettypRZ stored typRZ_Specified;
    property miesSprz:    string       Index (IS_OPTN) read FmiesSprz write SetmiesSprz stored miesSprz_Specified;
    property miesWazn:    string       Index (IS_OPTN) read FmiesWazn write SetmiesWazn stored miesWazn_Specified;
    property nrBiletu:    string       Index (IS_OPTN) read FnrBiletu write SetnrBiletu stored nrBiletu_Specified;
    property typBiletu:   string       Index (IS_OPTN) read FtypBiletu write SettypBiletu stored typBiletu_Specified;
    property godzPocz:    string       Index (IS_OPTN) read FgodzPocz write SetgodzPocz stored godzPocz_Specified;
    property godzKon:     string       Index (IS_OPTN) read FgodzKon write SetgodzKon stored godzKon_Specified;
    property nazUlgi:     string       Index (IS_OPTN) read FnazUlgi write SetnazUlgi stored nazUlgi_Specified;
    property nazSpZapl:   string       Index (IS_OPTN) read FnazSpZapl write SetnazSpZapl stored nazSpZapl_Specified;
    property oznWal:      string       Index (IS_OPTN) read FoznWal write SetoznWal stored oznWal_Specified;
    property identRZA:    string       Index (IS_OPTN) read FidentRZA write SetidentRZA stored identRZA_Specified;
    property oznaczK:     string       Index (IS_OPTN) read FoznaczK write SetoznaczK stored oznaczK_Specified;
    property dniRelBM:    string       Index (IS_OPTN) read FdniRelBM write SetdniRelBM stored dniRelBM_Specified;
    property nrDokUlgi:   string       Index (IS_OPTN) read FnrDokUlgi write SetnrDokUlgi stored nrDokUlgi_Specified;
    property nrPas:       string       Index (IS_OPTN) read FnrPas write SetnrPas stored nrPas_Specified;
    property nrDokTOZS:   string       Index (IS_OPTN) read FnrDokTOZS write SetnrDokTOZS stored nrDokTOZS_Specified;
    property szyfrBil:    string       Index (IS_OPTN) read FszyfrBil write SetszyfrBil stored szyfrBil_Specified;
    property relacjaK:    string       Index (IS_OPTN) read FrelacjaK write SetrelacjaK stored relacjaK_Specified;
    property rodzSP:      string       Index (IS_OPTN) read FrodzSP write SetrodzSP stored rodzSP_Specified;
    property kodKBil:     string       Index (IS_OPTN) read FkodKBil write SetkodKBil stored kodKBil_Specified;
    property nrKursuE:    string       Index (IS_OPTN) read FnrKursuE write SetnrKursuE stored nrKursuE_Specified;
    property godzPrzyj:   string       Index (IS_OPTN) read FgodzPrzyj write SetgodzPrzyj stored godzPrzyj_Specified;
    property zbiorA:      string       Index (IS_OPTN) read FzbiorA write SetzbiorA stored zbiorA_Specified;
    property godzOdjK:    string       Index (IS_OPTN) read FgodzOdjK write SetgodzOdjK stored godzOdjK_Specified;
    property godzOP:      string       Index (IS_OPTN) read FgodzOP write SetgodzOP stored godzOP_Specified;
    property companyCode: string       Index (IS_OPTN) read FcompanyCode write SetcompanyCode stored companyCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : param, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  param2 = class(TRemotable)
  private
    FfromRouteId: Int64;
    FtoRouteId: Int64;
  published
    property fromRouteId: Int64  Index (IS_ATTR) read FfromRouteId write FfromRouteId;
    property toRouteId:   Int64  Index (IS_ATTR) read FtoRouteId write FtoRouteId;
  end;

  stickRoute = array of sit;                    { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSResultRouteDetails = array of stickRoute;   { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : PWSMessageFromDriver, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSMessageFromDriver = class(TRemotable)
  private
    Fvehicle: PWSVehicle;
    Fvehicle_Specified: boolean;
    Fmessage_: PWSMessage;
    Fmessage__Specified: boolean;
    procedure Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
    function  vehicle_Specified(Index: Integer): boolean;
    procedure Setmessage_(Index: Integer; const APWSMessage: PWSMessage);
    function  message__Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property vehicle:  PWSVehicle  Index (IS_OPTN) read Fvehicle write Setvehicle stored vehicle_Specified;
    property message_: PWSMessage  Index (IS_OPTN) read Fmessage_ write Setmessage_ stored message__Specified;
  end;



  // ************************************************************************ //
  // XML       : carrierType, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  carrierType2 = class(TRemotable)
  private
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:  string  Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
  end;



  // ************************************************************************ //
  // XML       : discount, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  discount2 = class(TRemotable)
  private
    FvalueAfterDiscount: Single;
    FvalueAfterDiscount_Specified: boolean;
    FdiscountValue: Single;
    FdiscountValue_Specified: boolean;
    Fpercent: Boolean;
    FdefaultDis: Boolean;
    FdefaultDis_Specified: boolean;
    FtravelGroupId: Int64;
    FtravelGroupId_Specified: boolean;
    Ft5grRoundBound: Single;
    Ft10grRoundBound: Single;
    Fname_: string;
    Fname__Specified: boolean;
    Fcode: string;
    Fcode_Specified: boolean;
    Fdescription: string;
    Fdescription_Specified: boolean;
    FroundType: roundType;
    FroundType_Specified: boolean;
    Fudot: string;
    Fudot_Specified: boolean;
    FdiscountType: string;
    FdiscountType_Specified: boolean;
    procedure SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
    function  valueAfterDiscount_Specified(Index: Integer): boolean;
    procedure SetdiscountValue(Index: Integer; const ASingle: Single);
    function  discountValue_Specified(Index: Integer): boolean;
    procedure SetdefaultDis(Index: Integer; const ABoolean: Boolean);
    function  defaultDis_Specified(Index: Integer): boolean;
    procedure SettravelGroupId(Index: Integer; const AInt64: Int64);
    function  travelGroupId_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure Setcode(Index: Integer; const Astring: string);
    function  code_Specified(Index: Integer): boolean;
    procedure Setdescription(Index: Integer; const Astring: string);
    function  description_Specified(Index: Integer): boolean;
    procedure SetroundType(Index: Integer; const AroundType: roundType);
    function  roundType_Specified(Index: Integer): boolean;
    procedure Setudot(Index: Integer; const Astring: string);
    function  udot_Specified(Index: Integer): boolean;
    procedure SetdiscountType(Index: Integer; const Astring: string);
    function  discountType_Specified(Index: Integer): boolean;
  published
    property valueAfterDiscount: Single     Index (IS_ATTR or IS_OPTN) read FvalueAfterDiscount write SetvalueAfterDiscount stored valueAfterDiscount_Specified;
    property discountValue:      Single     Index (IS_ATTR or IS_OPTN) read FdiscountValue write SetdiscountValue stored discountValue_Specified;
    property percent:            Boolean    Index (IS_ATTR) read Fpercent write Fpercent;
    property defaultDis:         Boolean    Index (IS_ATTR or IS_OPTN) read FdefaultDis write SetdefaultDis stored defaultDis_Specified;
    property travelGroupId:      Int64      Index (IS_ATTR or IS_OPTN) read FtravelGroupId write SettravelGroupId stored travelGroupId_Specified;
    property t5grRoundBound:     Single     Index (IS_ATTR) read Ft5grRoundBound write Ft5grRoundBound;
    property t10grRoundBound:    Single     Index (IS_ATTR) read Ft10grRoundBound write Ft10grRoundBound;
    property name_:              string     Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property code:               string     Index (IS_OPTN) read Fcode write Setcode stored code_Specified;
    property description:        string     Index (IS_OPTN) read Fdescription write Setdescription stored description_Specified;
    property roundType:          roundType  Index (IS_OPTN) read FroundType write SetroundType stored roundType_Specified;
    property udot:               string     Index (IS_OPTN) read Fudot write Setudot stored udot_Specified;
    property discountType:       string     Index (IS_OPTN) read FdiscountType write SetdiscountType stored discountType_Specified;
  end;



  // ************************************************************************ //
  // XML       : PTiPlace, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PTiPlace = class(TRemotable)
  private
    FplaceNumber: Integer;
    FplaceNumber_Specified: boolean;
    FcancelDate: TXSDateTime;
    FcancelDate_Specified: boolean;
    Fid: Int64;
    Fid_Specified: boolean;
    Fdiscount: discount2;
    Fdiscount_Specified: boolean;
    FbankAccountNumber: string;
    FbankAccountNumber_Specified: boolean;
    FcancelState: cancelState;
    FcancelState_Specified: boolean;
    Fticket: ticket2;
    Fticket_Specified: boolean;
    Fluggage: PTiTariffForStick;
    Fluggage_Specified: boolean;
    procedure SetplaceNumber(Index: Integer; const AInteger: Integer);
    function  placeNumber_Specified(Index: Integer): boolean;
    procedure SetcancelDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  cancelDate_Specified(Index: Integer): boolean;
    procedure Setid(Index: Integer; const AInt64: Int64);
    function  id_Specified(Index: Integer): boolean;
    procedure Setdiscount(Index: Integer; const Adiscount2: discount2);
    function  discount_Specified(Index: Integer): boolean;
    procedure SetbankAccountNumber(Index: Integer; const Astring: string);
    function  bankAccountNumber_Specified(Index: Integer): boolean;
    procedure SetcancelState(Index: Integer; const AcancelState: cancelState);
    function  cancelState_Specified(Index: Integer): boolean;
    procedure Setticket(Index: Integer; const Aticket2: ticket2);
    function  ticket_Specified(Index: Integer): boolean;
    procedure Setluggage(Index: Integer; const APTiTariffForStick: PTiTariffForStick);
    function  luggage_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property placeNumber:       Integer            Index (IS_ATTR or IS_OPTN) read FplaceNumber write SetplaceNumber stored placeNumber_Specified;
    property cancelDate:        TXSDateTime        Index (IS_ATTR or IS_OPTN) read FcancelDate write SetcancelDate stored cancelDate_Specified;
    property id:                Int64              Index (IS_ATTR or IS_OPTN) read Fid write Setid stored id_Specified;
    property discount:          discount2          Index (IS_OPTN) read Fdiscount write Setdiscount stored discount_Specified;
    property bankAccountNumber: string             Index (IS_OPTN) read FbankAccountNumber write SetbankAccountNumber stored bankAccountNumber_Specified;
    property cancelState:       cancelState        Index (IS_OPTN) read FcancelState write SetcancelState stored cancelState_Specified;
    property ticket:            ticket2            Index (IS_OPTN) read Fticket write Setticket stored ticket_Specified;
    property luggage:           PTiTariffForStick  Index (IS_OPTN) read Fluggage write Setluggage stored luggage_Specified;
  end;



  // ************************************************************************ //
  // XML       : connection, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  connection2 = class(TRemotable)
  private
    FmillisBeforeFinish: Int64;
    FmillisBeforeFinish_Specified: boolean;
    FfromStop: PTiStopInTime;
    FfromStop_Specified: boolean;
    FtoStop: PTiStopInTime;
    FtoStop_Specified: boolean;
    procedure SetmillisBeforeFinish(Index: Integer; const AInt64: Int64);
    function  millisBeforeFinish_Specified(Index: Integer): boolean;
    procedure SetfromStop(Index: Integer; const APTiStopInTime: PTiStopInTime);
    function  fromStop_Specified(Index: Integer): boolean;
    procedure SettoStop(Index: Integer; const APTiStopInTime: PTiStopInTime);
    function  toStop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property millisBeforeFinish: Int64          Index (IS_ATTR or IS_OPTN) read FmillisBeforeFinish write SetmillisBeforeFinish stored millisBeforeFinish_Specified;
    property fromStop:           PTiStopInTime  Index (IS_OPTN) read FfromStop write SetfromStop stored fromStop_Specified;
    property toStop:             PTiStopInTime  Index (IS_OPTN) read FtoStop write SettoStop stored toStop_Specified;
  end;



  // ************************************************************************ //
  // XML       : holder, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  holder3 = class(TRemotable)
  private
    FcityId: Int64;
    FcityId_Specified: boolean;
    FdefaultPeriodicCardId: Int64;
    FdefaultPeriodicCardId_Specified: boolean;
    FholderData: PTiHolderForTicket;
    FholderData_Specified: boolean;
    Femail: string;
    Femail_Specified: boolean;
    Fphone: string;
    Fphone_Specified: boolean;
    FpostalCode: string;
    FpostalCode_Specified: boolean;
    Fstreet: string;
    Fstreet_Specified: boolean;
    FbuildingNumber: string;
    FbuildingNumber_Specified: boolean;
    FdefaultSendingType: defaultSendingType;
    FdefaultSendingType_Specified: boolean;
    FdefaultSendingAddress: string;
    FdefaultSendingAddress_Specified: boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
    function  defaultPeriodicCardId_Specified(Index: Integer): boolean;
    procedure SetholderData(Index: Integer; const APTiHolderForTicket: PTiHolderForTicket);
    function  holderData_Specified(Index: Integer): boolean;
    procedure Setemail(Index: Integer; const Astring: string);
    function  email_Specified(Index: Integer): boolean;
    procedure Setphone(Index: Integer; const Astring: string);
    function  phone_Specified(Index: Integer): boolean;
    procedure SetpostalCode(Index: Integer; const Astring: string);
    function  postalCode_Specified(Index: Integer): boolean;
    procedure Setstreet(Index: Integer; const Astring: string);
    function  street_Specified(Index: Integer): boolean;
    procedure SetbuildingNumber(Index: Integer; const Astring: string);
    function  buildingNumber_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingType(Index: Integer; const AdefaultSendingType: defaultSendingType);
    function  defaultSendingType_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingAddress(Index: Integer; const Astring: string);
    function  defaultSendingAddress_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property cityId:                Int64               Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property defaultPeriodicCardId: Int64               Index (IS_ATTR or IS_OPTN) read FdefaultPeriodicCardId write SetdefaultPeriodicCardId stored defaultPeriodicCardId_Specified;
    property holderData:            PTiHolderForTicket  Index (IS_OPTN) read FholderData write SetholderData stored holderData_Specified;
    property email:                 string              Index (IS_OPTN) read Femail write Setemail stored email_Specified;
    property phone:                 string              Index (IS_OPTN) read Fphone write Setphone stored phone_Specified;
    property postalCode:            string              Index (IS_OPTN) read FpostalCode write SetpostalCode stored postalCode_Specified;
    property street:                string              Index (IS_OPTN) read Fstreet write Setstreet stored street_Specified;
    property buildingNumber:        string              Index (IS_OPTN) read FbuildingNumber write SetbuildingNumber stored buildingNumber_Specified;
    property defaultSendingType:    defaultSendingType  Index (IS_OPTN) read FdefaultSendingType write SetdefaultSendingType stored defaultSendingType_Specified;
    property defaultSendingAddress: string              Index (IS_OPTN) read FdefaultSendingAddress write SetdefaultSendingAddress stored defaultSendingAddress_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiVendingEvent, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiVendingEvent = class(TRemotable)
  private
    FticketOrderId: Int64;
    FticketOrderId_Specified: boolean;
    FcreationTimestamp: TXSDateTime;
    FcreationTimestamp_Specified: boolean;
    FeventLevel: string;
    FeventLevel_Specified: boolean;
    Fmessage_: string;
    Fmessage__Specified: boolean;
    Fstate: string;
    Fstate_Specified: boolean;
    FstackTrace: string;
    FstackTrace_Specified: boolean;
    Ftype_: string;
    Ftype__Specified: boolean;
    Fvalue: string;
    Fvalue_Specified: boolean;
    Fsource: string;
    Fsource_Specified: boolean;
    procedure SetticketOrderId(Index: Integer; const AInt64: Int64);
    function  ticketOrderId_Specified(Index: Integer): boolean;
    procedure SetcreationTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  creationTimestamp_Specified(Index: Integer): boolean;
    procedure SeteventLevel(Index: Integer; const Astring: string);
    function  eventLevel_Specified(Index: Integer): boolean;
    procedure Setmessage_(Index: Integer; const Astring: string);
    function  message__Specified(Index: Integer): boolean;
    procedure Setstate(Index: Integer; const Astring: string);
    function  state_Specified(Index: Integer): boolean;
    procedure SetstackTrace(Index: Integer; const Astring: string);
    function  stackTrace_Specified(Index: Integer): boolean;
    procedure Settype_(Index: Integer; const Astring: string);
    function  type__Specified(Index: Integer): boolean;
    procedure Setvalue(Index: Integer; const Astring: string);
    function  value_Specified(Index: Integer): boolean;
    procedure Setsource(Index: Integer; const Astring: string);
    function  source_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ticketOrderId:     Int64        Index (IS_ATTR or IS_OPTN) read FticketOrderId write SetticketOrderId stored ticketOrderId_Specified;
    property creationTimestamp: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FcreationTimestamp write SetcreationTimestamp stored creationTimestamp_Specified;
    property eventLevel:        string       Index (IS_OPTN) read FeventLevel write SeteventLevel stored eventLevel_Specified;
    property message_:          string       Index (IS_OPTN) read Fmessage_ write Setmessage_ stored message__Specified;
    property state:             string       Index (IS_OPTN) read Fstate write Setstate stored state_Specified;
    property stackTrace:        string       Index (IS_OPTN) read FstackTrace write SetstackTrace stored stackTrace_Specified;
    property type_:             string       Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
    property value:             string       Index (IS_OPTN) read Fvalue write Setvalue stored value_Specified;
    property source:            string       Index (IS_OPTN) read Fsource write Setsource stored source_Specified;
  end;

  PWSTiStickIds = array of stickId2;            { "http://83.15.136.94:54321/axis2/services"[GblCplx] }


  // ************************************************************************ //
  // XML       : stickId, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  stickId2 = class(TRemotable)
  private
    FfromRouteId: Int64;
    FfromRouteId_Specified: boolean;
    FtoRouteId: Int64;
    FtoRouteId_Specified: boolean;
    procedure SetfromRouteId(Index: Integer; const AInt64: Int64);
    function  fromRouteId_Specified(Index: Integer): boolean;
    procedure SettoRouteId(Index: Integer; const AInt64: Int64);
    function  toRouteId_Specified(Index: Integer): boolean;
  published
    property fromRouteId: Int64  Index (IS_ATTR or IS_OPTN) read FfromRouteId write SetfromRouteId stored fromRouteId_Specified;
    property toRouteId:   Int64  Index (IS_ATTR or IS_OPTN) read FtoRouteId write SettoRouteId stored toRouteId_Specified;
  end;

  result     = array of stick;                  { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  PWSVehiclePositionList = array of PWSVehiclePosition;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSWebServiceUserList = array of PWSWebServiceUser;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSRelationParamsList = array of connId;      { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSMessageFromDriverList = array of PWSMessageFromDriver;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSInfKursList = array of PWSInfKurs;         { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSCarrierIdList = array of carrierid;        { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSOpinionsForCarrierList = array of PWSOpinionsForCarrier;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSTiBusCourseList = array of PWSTiBusCourse;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSFullyQualifiedCityList = array of PWSFullyQualifiedCity;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSTrackRecordingList = array of PWSTrackRecording;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSRelationList = array of PWSRelation;       { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSCitiesStopsList = array of PWSCitiesStops;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSCarrierDetailsList = array of PWSCarrierDetails;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSVehicleList = array of vehicle;            { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSTiSendNormalTicketDataList = array of PWSTiSendNormalTicketData;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSGetStopParamList = array of cityName;      { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }
  PWSFullyQualifiedCityExtList = array of PWSFullyQualifiedCityExt;   { "http://83.15.136.94:54321/axis2/services/PWebService"[GblCplx] }


  // ************************************************************************ //
  // XML       : PWSTiSellingReport, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSTiSellingReport2 = class(ERemotableException)
  private
    FfaultDescription: string;
    FfaultDescription_Specified: boolean;
    procedure SetfaultDescription(Index: Integer; const Astring: string);
    function  faultDescription_Specified(Index: Integer): boolean;
  published
    property faultDescription: string  Index (IS_OPTN) read FfaultDescription write SetfaultDescription stored faultDescription_Specified;
  end;

  causesForTicket = array of cause3;            { "http://83.15.136.94:54321/axis2/services/PWebService"[Cplx] }
  PWSTiChangeHolderData = array of cause3;      { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }


  // ************************************************************************ //
  // XML       : PWSEmptyTimeTable, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSEmptyTimeTable = class(ERemotableException)
  private
    Ffault: fault;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault: fault);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSMoreThanOneCarrier, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSMoreThanOneCarrier = class(ERemotableException)
  private
    Fname_: string;
    Fname__Specified: boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
  published
    property name_: string  Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSStops, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSStops = class(ERemotableException)
  private
    Ffault: fault2;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault2: fault2);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault2  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;

  PWSTiKasaUnavailable = array of cause3;       { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSTiRollbackResrvation = array of cause3;    { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PTiHoldersMatrix2 = array of cause2;          { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }


  // ************************************************************************ //
  // XML       : PWSNoSuchRecording, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoSuchRecording = class(ERemotableException)
  private
    FrecordingNo: string;
    FrecordingNo_Specified: boolean;
    procedure SetrecordingNo(Index: Integer; const Astring: string);
    function  recordingNo_Specified(Index: Integer): boolean;
  published
    property recordingNo: string  Index (IS_OPTN) read FrecordingNo write SetrecordingNo stored recordingNo_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSNoSuchCarrier, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoSuchCarrier = class(ERemotableException)
  private
    FcarrierId: Int64;
  published
    property carrierId: Int64  Index (IS_ATTR) read FcarrierId write FcarrierId;
  end;

  PWSTiReservation = array of cause3;           { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }


  // ************************************************************************ //
  // XML       : PWSTiVendingParams, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSTiVendingParams2 = class(ERemotableException)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : PWSChangeUserData, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSChangeUserData = class(ERemotableException)
  private
    Ffault: fault3;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault3: fault3);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault3  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSChangePassword, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSChangePassword = class(ERemotableException)
  private
    Ffault: fault4;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault4: fault4);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault4  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSNotYourUser, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNotYourUser = class(ERemotableException)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : PWSNoSuchInfCarrier, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoSuchInfCarrier = class(ERemotableException)
  private
    FinfNrf: Integer;
    FcompanyCode: string;
    FcompanyCode_Specified: boolean;
    procedure SetcompanyCode(Index: Integer; const Astring: string);
    function  companyCode_Specified(Index: Integer): boolean;
  published
    property infNrf:      Integer  Index (IS_ATTR) read FinfNrf write FinfNrf;
    property companyCode: string   Index (IS_OPTN) read FcompanyCode write SetcompanyCode stored companyCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSNoSuchInfCourse, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoSuchInfCourse = class(ERemotableException)
  private
    FnrKursu: Integer;
    FnrKursu_Specified: boolean;
    FwaznyOd: TXSDateTime;
    FwaznyOd_Specified: boolean;
    FkierTam: Boolean;
    FkierTam_Specified: boolean;
    FinfNrf: Integer;
    FinfNrf_Specified: boolean;
    Fwariant: string;
    Fwariant_Specified: boolean;
    FrodzKom: string;
    FrodzKom_Specified: boolean;
    procedure SetnrKursu(Index: Integer; const AInteger: Integer);
    function  nrKursu_Specified(Index: Integer): boolean;
    procedure SetwaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  waznyOd_Specified(Index: Integer): boolean;
    procedure SetkierTam(Index: Integer; const ABoolean: Boolean);
    function  kierTam_Specified(Index: Integer): boolean;
    procedure SetinfNrf(Index: Integer; const AInteger: Integer);
    function  infNrf_Specified(Index: Integer): boolean;
    procedure Setwariant(Index: Integer; const Astring: string);
    function  wariant_Specified(Index: Integer): boolean;
    procedure SetrodzKom(Index: Integer; const Astring: string);
    function  rodzKom_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property nrKursu: Integer      Index (IS_ATTR or IS_OPTN) read FnrKursu write SetnrKursu stored nrKursu_Specified;
    property waznyOd: TXSDateTime  Index (IS_ATTR or IS_OPTN) read FwaznyOd write SetwaznyOd stored waznyOd_Specified;
    property kierTam: Boolean      Index (IS_ATTR or IS_OPTN) read FkierTam write SetkierTam stored kierTam_Specified;
    property infNrf:  Integer      Index (IS_ATTR or IS_OPTN) read FinfNrf write SetinfNrf stored infNrf_Specified;
    property wariant: string       Index (IS_OPTN) read Fwariant write Setwariant stored wariant_Specified;
    property rodzKom: string       Index (IS_OPTN) read FrodzKom write SetrodzKom stored rodzKom_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSNoConn, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoConn = class(ERemotableException)
  private
    Ffault: fault5;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault5: fault5);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault5  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSNoVehicle, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSNoVehicle = class(ERemotableException)
  private
    FregistrationNumber: string;
    FregistrationNumber_Specified: boolean;
    FvehicleNumber: string;
    FvehicleNumber_Specified: boolean;
    procedure SetregistrationNumber(Index: Integer; const Astring: string);
    function  registrationNumber_Specified(Index: Integer): boolean;
    procedure SetvehicleNumber(Index: Integer; const Astring: string);
    function  vehicleNumber_Specified(Index: Integer): boolean;
  published
    property registrationNumber: string  Index (IS_OPTN) read FregistrationNumber write SetregistrationNumber stored registrationNumber_Specified;
    property vehicleNumber:      string  Index (IS_OPTN) read FvehicleNumber write SetvehicleNumber stored vehicleNumber_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSCreateUser, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSCreateUser = class(ERemotableException)
  private
    Ffault: fault6;
    Ffault_Specified: boolean;
    procedure Setfault(Index: Integer; const Afault6: fault6);
    function  fault_Specified(Index: Integer): boolean;
  published
    property fault: fault6  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSLogin, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSLogin = class(ERemotableException)
  private
    Ffault: fault7;
    Ffault_Specified: boolean;
    Fmessage_: string;
    Fmessage__Specified: boolean;
    procedure Setfault(Index: Integer; const Afault7: fault7);
    function  fault_Specified(Index: Integer): boolean;
    procedure Setmessage_(Index: Integer; const Astring: string);
    function  message__Specified(Index: Integer): boolean;
  published
    property fault:    fault7  Index (IS_OPTN) read Ffault write Setfault stored fault_Specified;
    property message_: string  Index (IS_OPTN) read Fmessage_ write Setmessage_ stored message__Specified;
  end;

  causeData  = array of cause3;                 { "http://83.15.136.94:54321/axis2/services/PWebService"[Cplx] }


  // ************************************************************************ //
  // XML       : PWSTiCommitResrvation, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSTiCommitResrvation = class(ERemotableException)
  private
    FPWSTiOrderUnavailable: PWSTiOrderUnavailable;
    FPWSTiOrderUnavailable_Specified: boolean;
    FcauseData: causeData;
    FcauseData_Specified: boolean;
    procedure SetPWSTiOrderUnavailable(Index: Integer; const APWSTiOrderUnavailable: PWSTiOrderUnavailable);
    function  PWSTiOrderUnavailable_Specified(Index: Integer): boolean;
    procedure SetcauseData(Index: Integer; const AcauseData: causeData);
    function  causeData_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property PWSTiOrderUnavailable: PWSTiOrderUnavailable  Index (IS_OPTN or IS_REF) read FPWSTiOrderUnavailable write SetPWSTiOrderUnavailable stored PWSTiOrderUnavailable_Specified;
    property causeData:             causeData              Index (IS_OPTN) read FcauseData write SetcauseData stored causeData_Specified;
  end;

  PWSTiChangeTicketDates = array of cause3;     { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSValidation = array of error;               { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  PWSTiCancelReservation = array of cause3;     { "http://83.15.136.94:54321/axis2/services/PWebService"[Flt][GblElm] }
  elem            =  type Boolean;      { "http://83.15.136.94:54321/axis2/services"[Alias] }
  PWSTiVehicleMatrixRow = array of elem;        { "http://83.15.136.94:54321/axis2/services"[Cplx] }
  matrix     = array of PWSTiVehicleMatrixRow;   { "http://83.15.136.94:54321/axis2/services"[Cplx] }


  // ************************************************************************ //
  // XML       : placesNumsBounds, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  placesNumsBounds = class(TRemotable)
  private
    FminPlaceNumber: Integer;
    FminPlaceNumber_Specified: boolean;
    FmaxPlaceNumber: Integer;
    FmaxPlaceNumber_Specified: boolean;
    FnumberOfPlacesInVeh: Integer;
    FnumberOfPlacesInVeh_Specified: boolean;
    Fmatrix: matrix;
    Fmatrix_Specified: boolean;
    procedure SetminPlaceNumber(Index: Integer; const AInteger: Integer);
    function  minPlaceNumber_Specified(Index: Integer): boolean;
    procedure SetmaxPlaceNumber(Index: Integer; const AInteger: Integer);
    function  maxPlaceNumber_Specified(Index: Integer): boolean;
    procedure SetnumberOfPlacesInVeh(Index: Integer; const AInteger: Integer);
    function  numberOfPlacesInVeh_Specified(Index: Integer): boolean;
    procedure Setmatrix(Index: Integer; const Amatrix: matrix);
    function  matrix_Specified(Index: Integer): boolean;
  published
    property minPlaceNumber:      Integer  Index (IS_ATTR or IS_OPTN) read FminPlaceNumber write SetminPlaceNumber stored minPlaceNumber_Specified;
    property maxPlaceNumber:      Integer  Index (IS_ATTR or IS_OPTN) read FmaxPlaceNumber write SetmaxPlaceNumber stored maxPlaceNumber_Specified;
    property numberOfPlacesInVeh: Integer  Index (IS_ATTR or IS_OPTN) read FnumberOfPlacesInVeh write SetnumberOfPlacesInVeh stored numberOfPlacesInVeh_Specified;
    property matrix:              matrix   Index (IS_OPTN) read Fmatrix write Setmatrix stored matrix_Specified;
  end;



  // ************************************************************************ //
  // XML       : cause, alias
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  cause3 = class(PWSEnumParam)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : sit, alias
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  sit = class(PWSStopInTime)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : stick, alias
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  stick = class(PWSStick)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : connId, alias
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // ************************************************************************ //
  connId = class(PWSRelationParams)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : carrierid, alias
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // ************************************************************************ //
  carrierid = class(PWSCarrierId)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : vehicle, alias
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // ************************************************************************ //
  vehicle = class(PWSVehicle)
  private
  published
  end;

  Array_Of_sellingDataForStick = array of sellingDataForStick;   { "http://83.15.136.94:54321/axis2/services"[Ubnd] }
  Array_Of_PWSTiDocType = array of PWSTiDocType;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSTiSellingData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSellingData = class(TRemotable)
  private
    FsellingDataForStick: Array_Of_sellingDataForStick;
    FsellingDataForStick_Specified: boolean;
    FdocType: Array_Of_PWSTiDocType;
    FdocType_Specified: boolean;
    procedure SetsellingDataForStick(Index: Integer; const AArray_Of_sellingDataForStick: Array_Of_sellingDataForStick);
    function  sellingDataForStick_Specified(Index: Integer): boolean;
    procedure SetdocType(Index: Integer; const AArray_Of_PWSTiDocType: Array_Of_PWSTiDocType);
    function  docType_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property sellingDataForStick: Array_Of_sellingDataForStick  Index (IS_OPTN or IS_UNBD) read FsellingDataForStick write SetsellingDataForStick stored sellingDataForStick_Specified;
    property docType:             Array_Of_PWSTiDocType         Index (IS_OPTN or IS_UNBD) read FdocType write SetdocType stored docType_Specified;
  end;

  Array_Of_PWSTiDiscount = array of PWSTiDiscount;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }
  Array_Of_PWSTiTariffForStick = array of PWSTiTariffForStick;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }
  Array_Of_PWSTiTariffPriceAfterDiscount = array of PWSTiTariffPriceAfterDiscount;   { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : sellingDataForStick, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  sellingDataForStick = class(TRemotable)
  private
    FticketWithoutHolderOkInVM: Boolean;
    FticketWithoutHolderOkInVM_Specified: boolean;
    Fdiscount: Array_Of_PWSTiDiscount;
    Fdiscount_Specified: boolean;
    Ftariffe: Array_Of_PWSTiTariffForStick;
    Ftariffe_Specified: boolean;
    FplacesNumsBounds: placesNumsBounds;
    FplacesNumsBounds_Specified: boolean;
    FPWSTiTariffPriceAfterDiscount: Array_Of_PWSTiTariffPriceAfterDiscount;
    FPWSTiTariffPriceAfterDiscount_Specified: boolean;
    procedure SetticketWithoutHolderOkInVM(Index: Integer; const ABoolean: Boolean);
    function  ticketWithoutHolderOkInVM_Specified(Index: Integer): boolean;
    procedure Setdiscount(Index: Integer; const AArray_Of_PWSTiDiscount: Array_Of_PWSTiDiscount);
    function  discount_Specified(Index: Integer): boolean;
    procedure Settariffe(Index: Integer; const AArray_Of_PWSTiTariffForStick: Array_Of_PWSTiTariffForStick);
    function  tariffe_Specified(Index: Integer): boolean;
    procedure SetplacesNumsBounds(Index: Integer; const AplacesNumsBounds: placesNumsBounds);
    function  placesNumsBounds_Specified(Index: Integer): boolean;
    procedure SetPWSTiTariffPriceAfterDiscount(Index: Integer; const AArray_Of_PWSTiTariffPriceAfterDiscount: Array_Of_PWSTiTariffPriceAfterDiscount);
    function  PWSTiTariffPriceAfterDiscount_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ticketWithoutHolderOkInVM:     Boolean                                 Index (IS_ATTR or IS_OPTN) read FticketWithoutHolderOkInVM write SetticketWithoutHolderOkInVM stored ticketWithoutHolderOkInVM_Specified;
    property discount:                      Array_Of_PWSTiDiscount                  Index (IS_OPTN or IS_UNBD) read Fdiscount write Setdiscount stored discount_Specified;
    property tariffe:                       Array_Of_PWSTiTariffForStick            Index (IS_OPTN or IS_UNBD) read Ftariffe write Settariffe stored tariffe_Specified;
    property placesNumsBounds:              placesNumsBounds                        Index (IS_OPTN) read FplacesNumsBounds write SetplacesNumsBounds stored placesNumsBounds_Specified;
    property PWSTiTariffPriceAfterDiscount: Array_Of_PWSTiTariffPriceAfterDiscount  Index (IS_OPTN or IS_UNBD) read FPWSTiTariffPriceAfterDiscount write SetPWSTiTariffPriceAfterDiscount stored PWSTiTariffPriceAfterDiscount_Specified;
  end;

  Array_Of_price = array of price;              { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiTariffForStick, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiTariffForStick = class(TRemotable)
  private
    FpriceId: Int64;
    FpriceId_Specified: boolean;
    FepTariff: Boolean;
    FepTariff_Specified: boolean;
    FkasaTariff: Boolean;
    FkasaTariff_Specified: boolean;
    FhoursToStartB: Int64;
    FhoursToStartB_Specified: boolean;
    FhoursToStartE: Int64;
    FhoursToStartE_Specified: boolean;
    FbackTariff: Boolean;
    FbackTariff_Specified: boolean;
    FreturnMoneyHours: Int64;
    FreturnMoneyHours_Specified: boolean;
    FreturnMoneyPercent: Single;
    FreturnMoneyPercent_Specified: boolean;
    FpayerMonthNo: Integer;
    FpayerMonthNo_Specified: boolean;
    FpayerYearNo: Integer;
    FpayerYearNo_Specified: boolean;
    FpayerNoOr: Boolean;
    FpayerNoOr_Specified: boolean;
    FpayerMonthVal: Single;
    FpayerMonthVal_Specified: boolean;
    FpayerYearVal: Single;
    FpayerYearVal_Specified: boolean;
    FpayerValOr: Boolean;
    FpayerValOr_Specified: boolean;
    FholderMonthNo: Integer;
    FholderMonthNo_Specified: boolean;
    FholderYearNo: Integer;
    FholderYearNo_Specified: boolean;
    FholderNoOr: Boolean;
    FholderNoOr_Specified: boolean;
    FholderMonthVal: Single;
    FholderMonthVal_Specified: boolean;
    FholderYearVal: Single;
    FholderYearVal_Specified: boolean;
    FholderValOr: Boolean;
    FholderValOr_Specified: boolean;
    Flegal: Boolean;
    Flegal_Specified: boolean;
    FnotGovDiscountValid: Boolean;
    FnotGovDiscountValid_Specified: boolean;
    FsmsSendTypeEnable: Boolean;
    FsmsSendTypeEnable_Specified: boolean;
    Fprice: Array_Of_price;
    Fprice_Specified: boolean;
    FlagguageDescription: string;
    FlagguageDescription_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    FtariffType: PWSEnumParam;
    FtariffType_Specified: boolean;
    FtariffTypeCode: string;
    FtariffTypeCode_Specified: boolean;
    procedure SetpriceId(Index: Integer; const AInt64: Int64);
    function  priceId_Specified(Index: Integer): boolean;
    procedure SetepTariff(Index: Integer; const ABoolean: Boolean);
    function  epTariff_Specified(Index: Integer): boolean;
    procedure SetkasaTariff(Index: Integer; const ABoolean: Boolean);
    function  kasaTariff_Specified(Index: Integer): boolean;
    procedure SethoursToStartB(Index: Integer; const AInt64: Int64);
    function  hoursToStartB_Specified(Index: Integer): boolean;
    procedure SethoursToStartE(Index: Integer; const AInt64: Int64);
    function  hoursToStartE_Specified(Index: Integer): boolean;
    procedure SetbackTariff(Index: Integer; const ABoolean: Boolean);
    function  backTariff_Specified(Index: Integer): boolean;
    procedure SetreturnMoneyHours(Index: Integer; const AInt64: Int64);
    function  returnMoneyHours_Specified(Index: Integer): boolean;
    procedure SetreturnMoneyPercent(Index: Integer; const ASingle: Single);
    function  returnMoneyPercent_Specified(Index: Integer): boolean;
    procedure SetpayerMonthNo(Index: Integer; const AInteger: Integer);
    function  payerMonthNo_Specified(Index: Integer): boolean;
    procedure SetpayerYearNo(Index: Integer; const AInteger: Integer);
    function  payerYearNo_Specified(Index: Integer): boolean;
    procedure SetpayerNoOr(Index: Integer; const ABoolean: Boolean);
    function  payerNoOr_Specified(Index: Integer): boolean;
    procedure SetpayerMonthVal(Index: Integer; const ASingle: Single);
    function  payerMonthVal_Specified(Index: Integer): boolean;
    procedure SetpayerYearVal(Index: Integer; const ASingle: Single);
    function  payerYearVal_Specified(Index: Integer): boolean;
    procedure SetpayerValOr(Index: Integer; const ABoolean: Boolean);
    function  payerValOr_Specified(Index: Integer): boolean;
    procedure SetholderMonthNo(Index: Integer; const AInteger: Integer);
    function  holderMonthNo_Specified(Index: Integer): boolean;
    procedure SetholderYearNo(Index: Integer; const AInteger: Integer);
    function  holderYearNo_Specified(Index: Integer): boolean;
    procedure SetholderNoOr(Index: Integer; const ABoolean: Boolean);
    function  holderNoOr_Specified(Index: Integer): boolean;
    procedure SetholderMonthVal(Index: Integer; const ASingle: Single);
    function  holderMonthVal_Specified(Index: Integer): boolean;
    procedure SetholderYearVal(Index: Integer; const ASingle: Single);
    function  holderYearVal_Specified(Index: Integer): boolean;
    procedure SetholderValOr(Index: Integer; const ABoolean: Boolean);
    function  holderValOr_Specified(Index: Integer): boolean;
    procedure Setlegal(Index: Integer; const ABoolean: Boolean);
    function  legal_Specified(Index: Integer): boolean;
    procedure SetnotGovDiscountValid(Index: Integer; const ABoolean: Boolean);
    function  notGovDiscountValid_Specified(Index: Integer): boolean;
    procedure SetsmsSendTypeEnable(Index: Integer; const ABoolean: Boolean);
    function  smsSendTypeEnable_Specified(Index: Integer): boolean;
    procedure Setprice(Index: Integer; const AArray_Of_price: Array_Of_price);
    function  price_Specified(Index: Integer): boolean;
    procedure SetlagguageDescription(Index: Integer; const Astring: string);
    function  lagguageDescription_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SettariffType(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  tariffType_Specified(Index: Integer): boolean;
    procedure SettariffTypeCode(Index: Integer; const Astring: string);
    function  tariffTypeCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property priceId:             Int64           Index (IS_ATTR or IS_OPTN) read FpriceId write SetpriceId stored priceId_Specified;
    property epTariff:            Boolean         Index (IS_ATTR or IS_OPTN) read FepTariff write SetepTariff stored epTariff_Specified;
    property kasaTariff:          Boolean         Index (IS_ATTR or IS_OPTN) read FkasaTariff write SetkasaTariff stored kasaTariff_Specified;
    property hoursToStartB:       Int64           Index (IS_ATTR or IS_OPTN) read FhoursToStartB write SethoursToStartB stored hoursToStartB_Specified;
    property hoursToStartE:       Int64           Index (IS_ATTR or IS_OPTN) read FhoursToStartE write SethoursToStartE stored hoursToStartE_Specified;
    property backTariff:          Boolean         Index (IS_ATTR or IS_OPTN) read FbackTariff write SetbackTariff stored backTariff_Specified;
    property returnMoneyHours:    Int64           Index (IS_ATTR or IS_OPTN) read FreturnMoneyHours write SetreturnMoneyHours stored returnMoneyHours_Specified;
    property returnMoneyPercent:  Single          Index (IS_ATTR or IS_OPTN) read FreturnMoneyPercent write SetreturnMoneyPercent stored returnMoneyPercent_Specified;
    property payerMonthNo:        Integer         Index (IS_ATTR or IS_OPTN) read FpayerMonthNo write SetpayerMonthNo stored payerMonthNo_Specified;
    property payerYearNo:         Integer         Index (IS_ATTR or IS_OPTN) read FpayerYearNo write SetpayerYearNo stored payerYearNo_Specified;
    property payerNoOr:           Boolean         Index (IS_ATTR or IS_OPTN) read FpayerNoOr write SetpayerNoOr stored payerNoOr_Specified;
    property payerMonthVal:       Single          Index (IS_ATTR or IS_OPTN) read FpayerMonthVal write SetpayerMonthVal stored payerMonthVal_Specified;
    property payerYearVal:        Single          Index (IS_ATTR or IS_OPTN) read FpayerYearVal write SetpayerYearVal stored payerYearVal_Specified;
    property payerValOr:          Boolean         Index (IS_ATTR or IS_OPTN) read FpayerValOr write SetpayerValOr stored payerValOr_Specified;
    property holderMonthNo:       Integer         Index (IS_ATTR or IS_OPTN) read FholderMonthNo write SetholderMonthNo stored holderMonthNo_Specified;
    property holderYearNo:        Integer         Index (IS_ATTR or IS_OPTN) read FholderYearNo write SetholderYearNo stored holderYearNo_Specified;
    property holderNoOr:          Boolean         Index (IS_ATTR or IS_OPTN) read FholderNoOr write SetholderNoOr stored holderNoOr_Specified;
    property holderMonthVal:      Single          Index (IS_ATTR or IS_OPTN) read FholderMonthVal write SetholderMonthVal stored holderMonthVal_Specified;
    property holderYearVal:       Single          Index (IS_ATTR or IS_OPTN) read FholderYearVal write SetholderYearVal stored holderYearVal_Specified;
    property holderValOr:         Boolean         Index (IS_ATTR or IS_OPTN) read FholderValOr write SetholderValOr stored holderValOr_Specified;
    property legal:               Boolean         Index (IS_ATTR or IS_OPTN) read Flegal write Setlegal stored legal_Specified;
    property notGovDiscountValid: Boolean         Index (IS_ATTR or IS_OPTN) read FnotGovDiscountValid write SetnotGovDiscountValid stored notGovDiscountValid_Specified;
    property smsSendTypeEnable:   Boolean         Index (IS_ATTR or IS_OPTN) read FsmsSendTypeEnable write SetsmsSendTypeEnable stored smsSendTypeEnable_Specified;
    property price:               Array_Of_price  Index (IS_OPTN or IS_UNBD) read Fprice write Setprice stored price_Specified;
    property lagguageDescription: string          Index (IS_OPTN) read FlagguageDescription write SetlagguageDescription stored lagguageDescription_Specified;
    property name_:               string          Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property tariffType:          PWSEnumParam    Index (IS_OPTN) read FtariffType write SettariffType stored tariffType_Specified;
    property tariffTypeCode:      string          Index (IS_OPTN) read FtariffTypeCode write SettariffTypeCode stored tariffTypeCode_Specified;
  end;

  Array_Of_PWSCostForPeriod = array of PWSCostForPeriod;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSCosts, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCosts = class(TRemotable)
  private
    FttPeriod: Array_Of_PWSCostForPeriod;
    FttPeriod_Specified: boolean;
    FconnPeriod: Array_Of_PWSCostForPeriod;
    FconnPeriod_Specified: boolean;
    FaddConnPeriod: Array_Of_PWSCostForPeriod;
    FaddConnPeriod_Specified: boolean;
    procedure SetttPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
    function  ttPeriod_Specified(Index: Integer): boolean;
    procedure SetconnPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
    function  connPeriod_Specified(Index: Integer): boolean;
    procedure SetaddConnPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
    function  addConnPeriod_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ttPeriod:      Array_Of_PWSCostForPeriod  Index (IS_OPTN or IS_UNBD) read FttPeriod write SetttPeriod stored ttPeriod_Specified;
    property connPeriod:    Array_Of_PWSCostForPeriod  Index (IS_OPTN or IS_UNBD) read FconnPeriod write SetconnPeriod stored connPeriod_Specified;
    property addConnPeriod: Array_Of_PWSCostForPeriod  Index (IS_OPTN or IS_UNBD) read FaddConnPeriod write SetaddConnPeriod stored addConnPeriod_Specified;
  end;

  Array_Of_PWSCarrierId = array of PWSCarrierId;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSCarrierSearcherParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrierSearcherParams = class(TRemotable)
  private
    FprovinceId: Int64;
    FprovinceId_Specified: boolean;
    FdistrictId: Int64;
    FdistrictId_Specified: boolean;
    FcommuneId: Int64;
    FcommuneId_Specified: boolean;
    FcityId: Int64;
    FcityId_Specified: boolean;
    FcarrierTypeId: Int64;
    FcarrierTypeId_Specified: boolean;
    FnameFilter: string;
    FnameFilter_Specified: boolean;
    FcarrierId: Array_Of_PWSCarrierId;
    FcarrierId_Specified: boolean;
    procedure SetprovinceId(Index: Integer; const AInt64: Int64);
    function  provinceId_Specified(Index: Integer): boolean;
    procedure SetdistrictId(Index: Integer; const AInt64: Int64);
    function  districtId_Specified(Index: Integer): boolean;
    procedure SetcommuneId(Index: Integer; const AInt64: Int64);
    function  communeId_Specified(Index: Integer): boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure SetcarrierTypeId(Index: Integer; const AInt64: Int64);
    function  carrierTypeId_Specified(Index: Integer): boolean;
    procedure SetnameFilter(Index: Integer; const Astring: string);
    function  nameFilter_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const AArray_Of_PWSCarrierId: Array_Of_PWSCarrierId);
    function  carrierId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property provinceId:    Int64                  Index (IS_ATTR or IS_OPTN) read FprovinceId write SetprovinceId stored provinceId_Specified;
    property districtId:    Int64                  Index (IS_ATTR or IS_OPTN) read FdistrictId write SetdistrictId stored districtId_Specified;
    property communeId:     Int64                  Index (IS_ATTR or IS_OPTN) read FcommuneId write SetcommuneId stored communeId_Specified;
    property cityId:        Int64                  Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property carrierTypeId: Int64                  Index (IS_ATTR or IS_OPTN) read FcarrierTypeId write SetcarrierTypeId stored carrierTypeId_Specified;
    property nameFilter:    string                 Index (IS_OPTN) read FnameFilter write SetnameFilter stored nameFilter_Specified;
    property carrierId:     Array_Of_PWSCarrierId  Index (IS_OPTN or IS_UNBD) read FcarrierId write SetcarrierId stored carrierId_Specified;
  end;

  Array_Of_ticket = array of ticket;            { "http://83.15.136.94:54321/axis2/services"[Ubnd] }
  Array_Of_periodicTicket = array of periodicTicket;   { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : order, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  order = class(TRemotable)
  private
    Fticket: Array_Of_ticket;
    Fticket_Specified: boolean;
    FperiodicTicket: Array_Of_periodicTicket;
    FperiodicTicket_Specified: boolean;
    FsendingData: PWSTiSendingData;
    FsendingData_Specified: boolean;
    procedure Setticket(Index: Integer; const AArray_Of_ticket: Array_Of_ticket);
    function  ticket_Specified(Index: Integer): boolean;
    procedure SetperiodicTicket(Index: Integer; const AArray_Of_periodicTicket: Array_Of_periodicTicket);
    function  periodicTicket_Specified(Index: Integer): boolean;
    procedure SetsendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
    function  sendingData_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ticket:         Array_Of_ticket          Index (IS_OPTN or IS_UNBD) read Fticket write Setticket stored ticket_Specified;
    property periodicTicket: Array_Of_periodicTicket  Index (IS_OPTN or IS_UNBD) read FperiodicTicket write SetperiodicTicket stored periodicTicket_Specified;
    property sendingData:    PWSTiSendingData         Index (IS_OPTN) read FsendingData write SetsendingData stored sendingData_Specified;
  end;

  Array_Of_place = array of place;              { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : ticket, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  ticket = class(TRemotable)
  private
    FpriceId: Int64;
    FpriceId_Specified: boolean;
    FgoDate: TXSDateTime;
    FgoDate_Specified: boolean;
    FconnectionDate: TXSDateTime;
    FconnectionDate_Specified: boolean;
    FwithHolder: Boolean;
    FwithHolder_Specified: boolean;
    FmainHolderData: PWSTiHolderForTicket;
    FmainHolderData_Specified: boolean;
    Fplace: Array_Of_place;
    Fplace_Specified: boolean;
    procedure SetpriceId(Index: Integer; const AInt64: Int64);
    function  priceId_Specified(Index: Integer): boolean;
    procedure SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  goDate_Specified(Index: Integer): boolean;
    procedure SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionDate_Specified(Index: Integer): boolean;
    procedure SetwithHolder(Index: Integer; const ABoolean: Boolean);
    function  withHolder_Specified(Index: Integer): boolean;
    procedure SetmainHolderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
    function  mainHolderData_Specified(Index: Integer): boolean;
    procedure Setplace(Index: Integer; const AArray_Of_place: Array_Of_place);
    function  place_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property priceId:        Int64                 Index (IS_ATTR or IS_OPTN) read FpriceId write SetpriceId stored priceId_Specified;
    property goDate:         TXSDateTime           Index (IS_ATTR or IS_OPTN) read FgoDate write SetgoDate stored goDate_Specified;
    property connectionDate: TXSDateTime           Index (IS_ATTR or IS_OPTN) read FconnectionDate write SetconnectionDate stored connectionDate_Specified;
    property withHolder:     Boolean               Index (IS_ATTR or IS_OPTN) read FwithHolder write SetwithHolder stored withHolder_Specified;
    property mainHolderData: PWSTiHolderForTicket  Index (IS_OPTN) read FmainHolderData write SetmainHolderData stored mainHolderData_Specified;
    property place:          Array_Of_place        Index (IS_OPTN or IS_UNBD) read Fplace write Setplace stored place_Specified;
  end;

  Array_Of_PWSStop = array of PWSStop;          { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSFullyQualifiedCityWithStops, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSFullyQualifiedCityWithStops = class(TRemotable)
  private
    FcommuneId: Int64;
    Fid: Int64;
    Fstop: Array_Of_PWSStop;
    Fstop_Specified: boolean;
    Fcity: PWSFullyQualifiedCity;
    Fcity_Specified: boolean;
    FcommuneName: string;
    FcommuneName_Specified: boolean;
    FdistrictName: string;
    FdistrictName_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    FprovinceName: string;
    FprovinceName_Specified: boolean;
    procedure Setstop(Index: Integer; const AArray_Of_PWSStop: Array_Of_PWSStop);
    function  stop_Specified(Index: Integer): boolean;
    procedure Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  city_Specified(Index: Integer): boolean;
    procedure SetcommuneName(Index: Integer; const Astring: string);
    function  communeName_Specified(Index: Integer): boolean;
    procedure SetdistrictName(Index: Integer; const Astring: string);
    function  districtName_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SetprovinceName(Index: Integer; const Astring: string);
    function  provinceName_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property communeId:    Int64                  Index (IS_ATTR) read FcommuneId write FcommuneId;
    property id:           Int64                  Index (IS_ATTR) read Fid write Fid;
    property stop:         Array_Of_PWSStop       Index (IS_OPTN or IS_UNBD) read Fstop write Setstop stored stop_Specified;
    property city:         PWSFullyQualifiedCity  Index (IS_OPTN) read Fcity write Setcity stored city_Specified;
    property communeName:  string                 Index (IS_OPTN) read FcommuneName write SetcommuneName stored communeName_Specified;
    property districtName: string                 Index (IS_OPTN) read FdistrictName write SetdistrictName stored districtName_Specified;
    property name_:        string                 Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property provinceName: string                 Index (IS_OPTN) read FprovinceName write SetprovinceName stored provinceName_Specified;
  end;



  // ************************************************************************ //
  // XML       : lineStop, alias
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  lineStop = class(PWSFullyQualifiedCityWithStops)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : cityStop, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  cityStop = class(TRemotable)
  private
    Fstop: Array_Of_PWSStop;
    Fstop_Specified: boolean;
    Fcity: PWSFullyQualifiedCity;
    Fcity_Specified: boolean;
    procedure Setstop(Index: Integer; const AArray_Of_PWSStop: Array_Of_PWSStop);
    function  stop_Specified(Index: Integer): boolean;
    procedure Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  city_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property stop: Array_Of_PWSStop       Index (IS_OPTN or IS_UNBD) read Fstop write Setstop stored stop_Specified;
    property city: PWSFullyQualifiedCity  Index (IS_OPTN) read Fcity write Setcity stored city_Specified;
  end;

  Array_Of_section = array of section;          { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiPeriodicTicketLineInfo, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiPeriodicTicketLineInfo = class(TRemotable)
  private
    FvaildFromTime: TXSDateTime;
    FvaildFromTime_Specified: boolean;
    FvaildToTime: TXSDateTime;
    FvaildToTime_Specified: boolean;
    Fsection: Array_Of_section;
    Fsection_Specified: boolean;
    Ftype_: PWSEnumParam;
    Ftype__Specified: boolean;
    procedure SetvaildFromTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  vaildFromTime_Specified(Index: Integer): boolean;
    procedure SetvaildToTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  vaildToTime_Specified(Index: Integer): boolean;
    procedure Setsection(Index: Integer; const AArray_Of_section: Array_Of_section);
    function  section_Specified(Index: Integer): boolean;
    procedure Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
    function  type__Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property vaildFromTime: TXSDateTime       Index (IS_ATTR or IS_OPTN) read FvaildFromTime write SetvaildFromTime stored vaildFromTime_Specified;
    property vaildToTime:   TXSDateTime       Index (IS_ATTR or IS_OPTN) read FvaildToTime write SetvaildToTime stored vaildToTime_Specified;
    property section:       Array_Of_section  Index (IS_OPTN or IS_UNBD) read Fsection write Setsection stored section_Specified;
    property type_:         PWSEnumParam      Index (IS_OPTN) read Ftype_ write Settype_ stored type__Specified;
  end;

  Array_Of_passenger = array of passenger;      { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiSendNormalTicketData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSendNormalTicketData = class(TRemotable)
  private
    FconnectionDate: TXSDateTime;
    FconnectionDate_Specified: boolean;
    FconnectionTime: TXSDateTime;
    FconnectionTime_Specified: boolean;
    FcommitTimestamp: TXSDateTime;
    FcommitTimestamp_Specified: boolean;
    FnrKursu: Int64;
    FnrKursu_Specified: boolean;
    FwithHolderData: Boolean;
    FwithHolderData_Specified: boolean;
    FgrossPrice: Single;
    FgrossPrice_Specified: boolean;
    FvatValue: Single;
    FvatValue_Specified: boolean;
    FvatRate: Single;
    FvatRate_Specified: boolean;
    FfromCityName: string;
    FfromCityName_Specified: boolean;
    FtoCityName: string;
    FtoCityName_Specified: boolean;
    FfromStopName: string;
    FfromStopName_Specified: boolean;
    FtoStopName: string;
    FtoStopName_Specified: boolean;
    FfromRelationName: string;
    FfromRelationName_Specified: boolean;
    FtoRelationName: string;
    FtoRelationName_Specified: boolean;
    FcarrierName: string;
    FcarrierName_Specified: boolean;
    FdocType: PWSTiDocType;
    FdocType_Specified: boolean;
    FidDocValue: string;
    FidDocValue_Specified: boolean;
    Fsurname: string;
    Fsurname_Specified: boolean;
    Fforename: string;
    Fforename_Specified: boolean;
    FticketLoginCode: string;
    FticketLoginCode_Specified: boolean;
    FticketCodeToVerify: string;
    FticketCodeToVerify_Specified: boolean;
    Fpassenger: Array_Of_passenger;
    Fpassenger_Specified: boolean;
    FluggageNumber: string;
    FluggageNumber_Specified: boolean;
    procedure SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionDate_Specified(Index: Integer): boolean;
    procedure SetconnectionTime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionTime_Specified(Index: Integer): boolean;
    procedure SetcommitTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  commitTimestamp_Specified(Index: Integer): boolean;
    procedure SetnrKursu(Index: Integer; const AInt64: Int64);
    function  nrKursu_Specified(Index: Integer): boolean;
    procedure SetwithHolderData(Index: Integer; const ABoolean: Boolean);
    function  withHolderData_Specified(Index: Integer): boolean;
    procedure SetgrossPrice(Index: Integer; const ASingle: Single);
    function  grossPrice_Specified(Index: Integer): boolean;
    procedure SetvatValue(Index: Integer; const ASingle: Single);
    function  vatValue_Specified(Index: Integer): boolean;
    procedure SetvatRate(Index: Integer; const ASingle: Single);
    function  vatRate_Specified(Index: Integer): boolean;
    procedure SetfromCityName(Index: Integer; const Astring: string);
    function  fromCityName_Specified(Index: Integer): boolean;
    procedure SettoCityName(Index: Integer; const Astring: string);
    function  toCityName_Specified(Index: Integer): boolean;
    procedure SetfromStopName(Index: Integer; const Astring: string);
    function  fromStopName_Specified(Index: Integer): boolean;
    procedure SettoStopName(Index: Integer; const Astring: string);
    function  toStopName_Specified(Index: Integer): boolean;
    procedure SetfromRelationName(Index: Integer; const Astring: string);
    function  fromRelationName_Specified(Index: Integer): boolean;
    procedure SettoRelationName(Index: Integer; const Astring: string);
    function  toRelationName_Specified(Index: Integer): boolean;
    procedure SetcarrierName(Index: Integer; const Astring: string);
    function  carrierName_Specified(Index: Integer): boolean;
    procedure SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
    function  docType_Specified(Index: Integer): boolean;
    procedure SetidDocValue(Index: Integer; const Astring: string);
    function  idDocValue_Specified(Index: Integer): boolean;
    procedure Setsurname(Index: Integer; const Astring: string);
    function  surname_Specified(Index: Integer): boolean;
    procedure Setforename(Index: Integer; const Astring: string);
    function  forename_Specified(Index: Integer): boolean;
    procedure SetticketLoginCode(Index: Integer; const Astring: string);
    function  ticketLoginCode_Specified(Index: Integer): boolean;
    procedure SetticketCodeToVerify(Index: Integer; const Astring: string);
    function  ticketCodeToVerify_Specified(Index: Integer): boolean;
    procedure Setpassenger(Index: Integer; const AArray_Of_passenger: Array_Of_passenger);
    function  passenger_Specified(Index: Integer): boolean;
    procedure SetluggageNumber(Index: Integer; const Astring: string);
    function  luggageNumber_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property connectionDate:     TXSDateTime         Index (IS_ATTR or IS_OPTN) read FconnectionDate write SetconnectionDate stored connectionDate_Specified;
    property connectionTime:     TXSDateTime         Index (IS_ATTR or IS_OPTN) read FconnectionTime write SetconnectionTime stored connectionTime_Specified;
    property commitTimestamp:    TXSDateTime         Index (IS_ATTR or IS_OPTN) read FcommitTimestamp write SetcommitTimestamp stored commitTimestamp_Specified;
    property nrKursu:            Int64               Index (IS_ATTR or IS_OPTN) read FnrKursu write SetnrKursu stored nrKursu_Specified;
    property withHolderData:     Boolean             Index (IS_ATTR or IS_OPTN) read FwithHolderData write SetwithHolderData stored withHolderData_Specified;
    property grossPrice:         Single              Index (IS_ATTR or IS_OPTN) read FgrossPrice write SetgrossPrice stored grossPrice_Specified;
    property vatValue:           Single              Index (IS_ATTR or IS_OPTN) read FvatValue write SetvatValue stored vatValue_Specified;
    property vatRate:            Single              Index (IS_ATTR or IS_OPTN) read FvatRate write SetvatRate stored vatRate_Specified;
    property fromCityName:       string              Index (IS_OPTN) read FfromCityName write SetfromCityName stored fromCityName_Specified;
    property toCityName:         string              Index (IS_OPTN) read FtoCityName write SettoCityName stored toCityName_Specified;
    property fromStopName:       string              Index (IS_OPTN) read FfromStopName write SetfromStopName stored fromStopName_Specified;
    property toStopName:         string              Index (IS_OPTN) read FtoStopName write SettoStopName stored toStopName_Specified;
    property fromRelationName:   string              Index (IS_OPTN) read FfromRelationName write SetfromRelationName stored fromRelationName_Specified;
    property toRelationName:     string              Index (IS_OPTN) read FtoRelationName write SettoRelationName stored toRelationName_Specified;
    property carrierName:        string              Index (IS_OPTN) read FcarrierName write SetcarrierName stored carrierName_Specified;
    property docType:            PWSTiDocType        Index (IS_OPTN) read FdocType write SetdocType stored docType_Specified;
    property idDocValue:         string              Index (IS_OPTN) read FidDocValue write SetidDocValue stored idDocValue_Specified;
    property surname:            string              Index (IS_OPTN) read Fsurname write Setsurname stored surname_Specified;
    property forename:           string              Index (IS_OPTN) read Fforename write Setforename stored forename_Specified;
    property ticketLoginCode:    string              Index (IS_OPTN) read FticketLoginCode write SetticketLoginCode stored ticketLoginCode_Specified;
    property ticketCodeToVerify: string              Index (IS_OPTN) read FticketCodeToVerify write SetticketCodeToVerify stored ticketCodeToVerify_Specified;
    property passenger:          Array_Of_passenger  Index (IS_OPTN or IS_UNBD) read Fpassenger write Setpassenger stored passenger_Specified;
    property luggageNumber:      string              Index (IS_OPTN) read FluggageNumber write SetluggageNumber stored luggageNumber_Specified;
  end;

  Array_Of_placeCause = array of placeCause;    { "http://83.15.136.94:54321/axis2/services"[Ubnd] }
  Array_Of_PWSEnumParam = array of PWSEnumParam;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : placeCause, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  placeCause = class(TRemotable)
  private
    FfreePlaces: Integer;
    FfreePlaces_Specified: boolean;
    FPWSEnumParam: Array_Of_PWSEnumParam;
    FPWSEnumParam_Specified: boolean;
    procedure SetfreePlaces(Index: Integer; const AInteger: Integer);
    function  freePlaces_Specified(Index: Integer): boolean;
    procedure SetPWSEnumParam(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  PWSEnumParam_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property freePlaces:   Integer                Index (IS_ATTR or IS_OPTN) read FfreePlaces write SetfreePlaces stored freePlaces_Specified;
    property PWSEnumParam: Array_Of_PWSEnumParam  Index (IS_OPTN or IS_UNBD) read FPWSEnumParam write SetPWSEnumParam stored PWSEnumParam_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiTicketUnavailableFaultData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiTicketUnavailableFaultData = class(TRemotable)
  private
    FplaceCause: Array_Of_placeCause;
    FplaceCause_Specified: boolean;
    FcommonCause: Array_Of_PWSEnumParam;
    FcommonCause_Specified: boolean;
    procedure SetplaceCause(Index: Integer; const AArray_Of_placeCause: Array_Of_placeCause);
    function  placeCause_Specified(Index: Integer): boolean;
    procedure SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  commonCause_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property placeCause:  Array_Of_placeCause    Index (IS_OPTN or IS_UNBD) read FplaceCause write SetplaceCause stored placeCause_Specified;
    property commonCause: Array_Of_PWSEnumParam  Index (IS_OPTN or IS_UNBD) read FcommonCause write SetcommonCause stored commonCause_Specified;
  end;

  Array_Of_long = array of Int64;               { "http://www.w3.org/2001/XMLSchema"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSGetStopParam, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSGetStopParam = class(TRemotable)
  private
    FcityId: Int64;
    FcityId_Specified: boolean;
    FcityName: string;
    FcityName_Specified: boolean;
    FcarrierId: Array_Of_long;
    FcarrierId_Specified: boolean;
    procedure SetcityId(Index: Integer; const AInt64: Int64);
    function  cityId_Specified(Index: Integer): boolean;
    procedure SetcityName(Index: Integer; const Astring: string);
    function  cityName_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  carrierId_Specified(Index: Integer): boolean;
  published
    property cityId:    Int64          Index (IS_ATTR or IS_OPTN) read FcityId write SetcityId stored cityId_Specified;
    property cityName:  string         Index (IS_OPTN) read FcityName write SetcityName stored cityName_Specified;
    property carrierId: Array_Of_long  Index (IS_OPTN or IS_UNBD) read FcarrierId write SetcarrierId stored carrierId_Specified;
  end;



  // ************************************************************************ //
  // XML       : cityName, alias
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // ************************************************************************ //
  cityName = class(PWSGetStopParam)
  private
  published
  end;



  // ************************************************************************ //
  // XML       : PWSTiReservationCancelRange, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiReservationCancelRange = class(TRemotable)
  private
    FreservationId: Int64;
    FreservationId_Specified: boolean;
    FticketId: Array_Of_long;
    FticketId_Specified: boolean;
    FplacesId: Array_Of_long;
    FplacesId_Specified: boolean;
    procedure SetreservationId(Index: Integer; const AInt64: Int64);
    function  reservationId_Specified(Index: Integer): boolean;
    procedure SetticketId(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  ticketId_Specified(Index: Integer): boolean;
    procedure SetplacesId(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  placesId_Specified(Index: Integer): boolean;
  published
    property reservationId: Int64          Index (IS_ATTR or IS_OPTN) read FreservationId write SetreservationId stored reservationId_Specified;
    property ticketId:      Array_Of_long  Index (IS_OPTN or IS_UNBD) read FticketId write SetticketId stored ticketId_Specified;
    property placesId:      Array_Of_long  Index (IS_OPTN or IS_UNBD) read FplacesId write SetplacesId stored placesId_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSSearchingParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSSearchingParams = class(TRemotable)
  private
    FfromStopId: Int64;
    FfromStopId_Specified: boolean;
    FtoStopId: Int64;
    FtoStopId_Specified: boolean;
    Fdate: TXSDateTime;
    Fdate_Specified: boolean;
    Ftime: TXSDateTime;
    Ftime_Specified: boolean;
    Foffset: Integer;
    FradioArrival: Boolean;
    FmaximalNumberOfChanges: Integer;
    FminimalTimeForChangeInMinutes: Integer;
    FmaximalTimeForChangeInMinutes: Integer;
    FchangeOfStopPossible: Boolean;
    FfromCityId: Int64;
    FfromCityId_Specified: boolean;
    FtoCityId: Int64;
    FtoCityId_Specified: boolean;
    FsellingTickets: Boolean;
    FsellingTickets_Specified: boolean;
    FoptimizationMode: optimizationMode;
    FoptimizationMode_Specified: boolean;
    FcarrierType: carrierType;
    FcarrierType_Specified: boolean;
    FcarrierId: Array_Of_long;
    FcarrierId_Specified: boolean;
    FfilterCode: string;
    FfilterCode_Specified: boolean;
    procedure SetfromStopId(Index: Integer; const AInt64: Int64);
    function  fromStopId_Specified(Index: Integer): boolean;
    procedure SettoStopId(Index: Integer; const AInt64: Int64);
    function  toStopId_Specified(Index: Integer): boolean;
    procedure Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  date_Specified(Index: Integer): boolean;
    procedure Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  time_Specified(Index: Integer): boolean;
    procedure SetfromCityId(Index: Integer; const AInt64: Int64);
    function  fromCityId_Specified(Index: Integer): boolean;
    procedure SettoCityId(Index: Integer; const AInt64: Int64);
    function  toCityId_Specified(Index: Integer): boolean;
    procedure SetsellingTickets(Index: Integer; const ABoolean: Boolean);
    function  sellingTickets_Specified(Index: Integer): boolean;
    procedure SetoptimizationMode(Index: Integer; const AoptimizationMode: optimizationMode);
    function  optimizationMode_Specified(Index: Integer): boolean;
    procedure SetcarrierType(Index: Integer; const AcarrierType: carrierType);
    function  carrierType_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  carrierId_Specified(Index: Integer): boolean;
    procedure SetfilterCode(Index: Integer; const Astring: string);
    function  filterCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property fromStopId:                    Int64             Index (IS_ATTR or IS_OPTN) read FfromStopId write SetfromStopId stored fromStopId_Specified;
    property toStopId:                      Int64             Index (IS_ATTR or IS_OPTN) read FtoStopId write SettoStopId stored toStopId_Specified;
    property date:                          TXSDateTime       Index (IS_ATTR or IS_OPTN) read Fdate write Setdate stored date_Specified;
    property time:                          TXSDateTime       Index (IS_ATTR or IS_OPTN) read Ftime write Settime stored time_Specified;
    property offset:                        Integer           Index (IS_ATTR) read Foffset write Foffset;
    property radioArrival:                  Boolean           Index (IS_ATTR) read FradioArrival write FradioArrival;
    property maximalNumberOfChanges:        Integer           Index (IS_ATTR) read FmaximalNumberOfChanges write FmaximalNumberOfChanges;
    property minimalTimeForChangeInMinutes: Integer           Index (IS_ATTR) read FminimalTimeForChangeInMinutes write FminimalTimeForChangeInMinutes;
    property maximalTimeForChangeInMinutes: Integer           Index (IS_ATTR) read FmaximalTimeForChangeInMinutes write FmaximalTimeForChangeInMinutes;
    property changeOfStopPossible:          Boolean           Index (IS_ATTR) read FchangeOfStopPossible write FchangeOfStopPossible;
    property fromCityId:                    Int64             Index (IS_ATTR or IS_OPTN) read FfromCityId write SetfromCityId stored fromCityId_Specified;
    property toCityId:                      Int64             Index (IS_ATTR or IS_OPTN) read FtoCityId write SettoCityId stored toCityId_Specified;
    property sellingTickets:                Boolean           Index (IS_ATTR or IS_OPTN) read FsellingTickets write SetsellingTickets stored sellingTickets_Specified;
    property optimizationMode:              optimizationMode  Index (IS_OPTN) read FoptimizationMode write SetoptimizationMode stored optimizationMode_Specified;
    property carrierType:                   carrierType       Index (IS_OPTN) read FcarrierType write SetcarrierType stored carrierType_Specified;
    property carrierId:                     Array_Of_long     Index (IS_OPTN or IS_UNBD) read FcarrierId write SetcarrierId stored carrierId_Specified;
    property filterCode:                    string            Index (IS_OPTN) read FfilterCode write SetfilterCode stored filterCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : PWSTiWebServiceUserSellingConfig, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiWebServiceUserSellingConfig = class(TRemotable)
  private
    FdistributorId: Int64;
    FdistributorId_Specified: boolean;
    FmachineConfig: machineConfig;
    FmachineConfig_Specified: boolean;
    FcarrierId: Array_Of_long;
    FcarrierId_Specified: boolean;
    procedure SetdistributorId(Index: Integer; const AInt64: Int64);
    function  distributorId_Specified(Index: Integer): boolean;
    procedure SetmachineConfig(Index: Integer; const AmachineConfig: machineConfig);
    function  machineConfig_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  carrierId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property distributorId: Int64          Index (IS_ATTR or IS_OPTN) read FdistributorId write SetdistributorId stored distributorId_Specified;
    property machineConfig: machineConfig  Index (IS_OPTN) read FmachineConfig write SetmachineConfig stored machineConfig_Specified;
    property carrierId:     Array_Of_long  Index (IS_OPTN or IS_UNBD) read FcarrierId write SetcarrierId stored carrierId_Specified;
  end;



  // ************************************************************************ //
  // XML       : carriers, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  carriers = class(TRemotable)
  private
    FvendingMachineId: Int64;
    FvendingMachineId_Specified: boolean;
    FshowAllCarriers: Boolean;
    FshowAllCarriers_Specified: boolean;
    FsellAllCarriers: Boolean;
    FsellAllCarriers_Specified: boolean;
    FshowCarrier: Array_Of_long;
    FshowCarrier_Specified: boolean;
    FsellCarrier: Array_Of_long;
    FsellCarrier_Specified: boolean;
    procedure SetvendingMachineId(Index: Integer; const AInt64: Int64);
    function  vendingMachineId_Specified(Index: Integer): boolean;
    procedure SetshowAllCarriers(Index: Integer; const ABoolean: Boolean);
    function  showAllCarriers_Specified(Index: Integer): boolean;
    procedure SetsellAllCarriers(Index: Integer; const ABoolean: Boolean);
    function  sellAllCarriers_Specified(Index: Integer): boolean;
    procedure SetshowCarrier(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  showCarrier_Specified(Index: Integer): boolean;
    procedure SetsellCarrier(Index: Integer; const AArray_Of_long: Array_Of_long);
    function  sellCarrier_Specified(Index: Integer): boolean;
  published
    property vendingMachineId: Int64          Index (IS_ATTR or IS_OPTN) read FvendingMachineId write SetvendingMachineId stored vendingMachineId_Specified;
    property showAllCarriers:  Boolean        Index (IS_ATTR or IS_OPTN) read FshowAllCarriers write SetshowAllCarriers stored showAllCarriers_Specified;
    property sellAllCarriers:  Boolean        Index (IS_ATTR or IS_OPTN) read FsellAllCarriers write SetsellAllCarriers stored sellAllCarriers_Specified;
    property showCarrier:      Array_Of_long  Index (IS_OPTN or IS_UNBD) read FshowCarrier write SetshowCarrier stored showCarrier_Specified;
    property sellCarrier:      Array_Of_long  Index (IS_OPTN or IS_UNBD) read FsellCarrier write SetsellCarrier stored sellCarrier_Specified;
  end;

  Array_Of_result = array of result2;           { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiSearchingResultWithSellingData, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiSearchingResultWithSellingData = class(TRemotable)
  private
    Fresult: Array_Of_result;
    Fresult_Specified: boolean;
    FresultsId: string;
    FresultsId_Specified: boolean;
    procedure Setresult(Index: Integer; const AArray_Of_result: Array_Of_result);
    function  result_Specified(Index: Integer): boolean;
    procedure SetresultsId(Index: Integer; const Astring: string);
    function  resultsId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property result:    Array_Of_result  Index (IS_OPTN or IS_UNBD) read Fresult write Setresult stored result_Specified;
    property resultsId: string           Index (IS_OPTN) read FresultsId write SetresultsId stored resultsId_Specified;
  end;

  Array_Of_stick = array of stick2;             { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : result, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  result2 = class(TRemotable)
  private
    FgoDate: TXSDateTime;
    FgoDate_Specified: boolean;
    FconnectionDate: TXSDateTime;
    FconnectionDate_Specified: boolean;
    FsystemLocked: Boolean;
    FsystemLocked_Specified: boolean;
    FresultCanBeBought: Integer;
    FresultCanBeBought_Specified: boolean;
    Fstick: Array_Of_stick;
    Fstick_Specified: boolean;
    procedure SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  goDate_Specified(Index: Integer): boolean;
    procedure SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionDate_Specified(Index: Integer): boolean;
    procedure SetsystemLocked(Index: Integer; const ABoolean: Boolean);
    function  systemLocked_Specified(Index: Integer): boolean;
    procedure SetresultCanBeBought(Index: Integer; const AInteger: Integer);
    function  resultCanBeBought_Specified(Index: Integer): boolean;
    procedure Setstick(Index: Integer; const AArray_Of_stick: Array_Of_stick);
    function  stick_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property goDate:            TXSDateTime     Index (IS_ATTR or IS_OPTN) read FgoDate write SetgoDate stored goDate_Specified;
    property connectionDate:    TXSDateTime     Index (IS_ATTR or IS_OPTN) read FconnectionDate write SetconnectionDate stored connectionDate_Specified;
    property systemLocked:      Boolean         Index (IS_ATTR or IS_OPTN) read FsystemLocked write SetsystemLocked stored systemLocked_Specified;
    property resultCanBeBought: Integer         Index (IS_ATTR or IS_OPTN) read FresultCanBeBought write SetresultCanBeBought stored resultCanBeBought_Specified;
    property stick:             Array_Of_stick  Index (IS_OPTN or IS_UNBD) read Fstick write Setstick stored stick_Specified;
  end;

  Array_Of_int = array of Integer;              { "http://www.w3.org/2001/XMLSchema"[GblUbnd] }


  // ************************************************************************ //
  // XML       : stick, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  stick2 = class(TRemotable)
  private
    FfreePlaces: Integer;
    FfreePlaces_Specified: boolean;
    Fsellable: Boolean;
    Fsellable_Specified: boolean;
    FsimpleStick: PWSStick;
    FsimpleStick_Specified: boolean;
    FsoldPlacesNumber: Array_Of_int;
    FsoldPlacesNumber_Specified: boolean;
    FticketCause: Array_Of_PWSEnumParam;
    FticketCause_Specified: boolean;
    FplaceCause: Array_Of_PWSEnumParam;
    FplaceCause_Specified: boolean;
    FrelationFrom: PWSStop;
    FrelationFrom_Specified: boolean;
    FrelationTo: PWSStop;
    FrelationTo_Specified: boolean;
    procedure SetfreePlaces(Index: Integer; const AInteger: Integer);
    function  freePlaces_Specified(Index: Integer): boolean;
    procedure Setsellable(Index: Integer; const ABoolean: Boolean);
    function  sellable_Specified(Index: Integer): boolean;
    procedure SetsimpleStick(Index: Integer; const APWSStick: PWSStick);
    function  simpleStick_Specified(Index: Integer): boolean;
    procedure SetsoldPlacesNumber(Index: Integer; const AArray_Of_int: Array_Of_int);
    function  soldPlacesNumber_Specified(Index: Integer): boolean;
    procedure SetticketCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  ticketCause_Specified(Index: Integer): boolean;
    procedure SetplaceCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  placeCause_Specified(Index: Integer): boolean;
    procedure SetrelationFrom(Index: Integer; const APWSStop: PWSStop);
    function  relationFrom_Specified(Index: Integer): boolean;
    procedure SetrelationTo(Index: Integer; const APWSStop: PWSStop);
    function  relationTo_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property freePlaces:       Integer                Index (IS_ATTR or IS_OPTN) read FfreePlaces write SetfreePlaces stored freePlaces_Specified;
    property sellable:         Boolean                Index (IS_ATTR or IS_OPTN) read Fsellable write Setsellable stored sellable_Specified;
    property simpleStick:      PWSStick               Index (IS_OPTN) read FsimpleStick write SetsimpleStick stored simpleStick_Specified;
    property soldPlacesNumber: Array_Of_int           Index (IS_OPTN or IS_UNBD) read FsoldPlacesNumber write SetsoldPlacesNumber stored soldPlacesNumber_Specified;
    property ticketCause:      Array_Of_PWSEnumParam  Index (IS_OPTN or IS_UNBD) read FticketCause write SetticketCause stored ticketCause_Specified;
    property placeCause:       Array_Of_PWSEnumParam  Index (IS_OPTN or IS_UNBD) read FplaceCause write SetplaceCause stored placeCause_Specified;
    property relationFrom:     PWSStop                Index (IS_OPTN) read FrelationFrom write SetrelationFrom stored relationFrom_Specified;
    property relationTo:       PWSStop                Index (IS_OPTN) read FrelationTo write SetrelationTo stored relationTo_Specified;
  end;

  Array_Of_holder = array of holder4;           { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : holdersForStick, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  holdersForStick = class(TRemotable)
  private
    FfromRouteSqNumber: Int64;
    FfromRouteSqNumber_Specified: boolean;
    FtoRouteSqNumber: Int64;
    FtoRouteSqNumber_Specified: boolean;
    FfromStopName: string;
    FfromStopName_Specified: boolean;
    FtoStopName: string;
    FtoStopName_Specified: boolean;
    Fholder: Array_Of_holder;
    Fholder_Specified: boolean;
    FstickId: stickId;
    FstickId_Specified: boolean;
    procedure SetfromRouteSqNumber(Index: Integer; const AInt64: Int64);
    function  fromRouteSqNumber_Specified(Index: Integer): boolean;
    procedure SettoRouteSqNumber(Index: Integer; const AInt64: Int64);
    function  toRouteSqNumber_Specified(Index: Integer): boolean;
    procedure SetfromStopName(Index: Integer; const Astring: string);
    function  fromStopName_Specified(Index: Integer): boolean;
    procedure SettoStopName(Index: Integer; const Astring: string);
    function  toStopName_Specified(Index: Integer): boolean;
    procedure Setholder(Index: Integer; const AArray_Of_holder: Array_Of_holder);
    function  holder_Specified(Index: Integer): boolean;
    procedure SetstickId(Index: Integer; const AstickId: stickId);
    function  stickId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property fromRouteSqNumber: Int64            Index (IS_ATTR or IS_OPTN) read FfromRouteSqNumber write SetfromRouteSqNumber stored fromRouteSqNumber_Specified;
    property toRouteSqNumber:   Int64            Index (IS_ATTR or IS_OPTN) read FtoRouteSqNumber write SettoRouteSqNumber stored toRouteSqNumber_Specified;
    property fromStopName:      string           Index (IS_OPTN) read FfromStopName write SetfromStopName stored fromStopName_Specified;
    property toStopName:        string           Index (IS_OPTN) read FtoStopName write SettoStopName stored toStopName_Specified;
    property holder:            Array_Of_holder  Index (IS_OPTN or IS_UNBD) read Fholder write Setholder stored holder_Specified;
    property stickId:           stickId          Index (IS_OPTN) read FstickId write SetstickId stored stickId_Specified;
  end;

  Array_Of_PTiPlace = array of PTiPlace;        { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : ticket, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  ticket2 = class(TRemotable)
  private
    FgoDate: TXSDateTime;
    FgoDate_Specified: boolean;
    FticketId: Int64;
    FticketId_Specified: boolean;
    FconnectionDate: TXSDateTime;
    FconnectionDate_Specified: boolean;
    FviaKasa: Boolean;
    FcurrentSellViaKasa: Boolean;
    FcurrentSellViaKasa_Specified: boolean;
    Fplace: Array_Of_PTiPlace;
    Fplace_Specified: boolean;
    Fconnection: connection2;
    Fconnection_Specified: boolean;
    Fholder: holder3;
    Fholder_Specified: boolean;
    Ftariff: PTiTariffForStick;
    Ftariff_Specified: boolean;
    FcodeToVerify: string;
    FcodeToVerify_Specified: boolean;
    FticketLoginCode: string;
    FticketLoginCode_Specified: boolean;
    procedure SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  goDate_Specified(Index: Integer): boolean;
    procedure SetticketId(Index: Integer; const AInt64: Int64);
    function  ticketId_Specified(Index: Integer): boolean;
    procedure SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionDate_Specified(Index: Integer): boolean;
    procedure SetcurrentSellViaKasa(Index: Integer; const ABoolean: Boolean);
    function  currentSellViaKasa_Specified(Index: Integer): boolean;
    procedure Setplace(Index: Integer; const AArray_Of_PTiPlace: Array_Of_PTiPlace);
    function  place_Specified(Index: Integer): boolean;
    procedure Setconnection(Index: Integer; const Aconnection2: connection2);
    function  connection_Specified(Index: Integer): boolean;
    procedure Setholder(Index: Integer; const Aholder3: holder3);
    function  holder_Specified(Index: Integer): boolean;
    procedure Settariff(Index: Integer; const APTiTariffForStick: PTiTariffForStick);
    function  tariff_Specified(Index: Integer): boolean;
    procedure SetcodeToVerify(Index: Integer; const Astring: string);
    function  codeToVerify_Specified(Index: Integer): boolean;
    procedure SetticketLoginCode(Index: Integer; const Astring: string);
    function  ticketLoginCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property goDate:             TXSDateTime        Index (IS_ATTR or IS_OPTN) read FgoDate write SetgoDate stored goDate_Specified;
    property ticketId:           Int64              Index (IS_ATTR or IS_OPTN) read FticketId write SetticketId stored ticketId_Specified;
    property connectionDate:     TXSDateTime        Index (IS_ATTR or IS_OPTN) read FconnectionDate write SetconnectionDate stored connectionDate_Specified;
    property viaKasa:            Boolean            Index (IS_ATTR) read FviaKasa write FviaKasa;
    property currentSellViaKasa: Boolean            Index (IS_ATTR or IS_OPTN) read FcurrentSellViaKasa write SetcurrentSellViaKasa stored currentSellViaKasa_Specified;
    property place:              Array_Of_PTiPlace  Index (IS_OPTN or IS_UNBD) read Fplace write Setplace stored place_Specified;
    property connection:         connection2        Index (IS_OPTN) read Fconnection write Setconnection stored connection_Specified;
    property holder:             holder3            Index (IS_OPTN) read Fholder write Setholder stored holder_Specified;
    property tariff:             PTiTariffForStick  Index (IS_OPTN) read Ftariff write Settariff stored tariff_Specified;
    property codeToVerify:       string             Index (IS_OPTN) read FcodeToVerify write SetcodeToVerify stored codeToVerify_Specified;
    property ticketLoginCode:    string             Index (IS_OPTN) read FticketLoginCode write SetticketLoginCode stored ticketLoginCode_Specified;
  end;



  // ************************************************************************ //
  // XML       : holder, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  holder4 = class(TRemotable)
  private
    FgrossPriceBeforeDiscount: Single;
    FgrossPriceBeforeDiscount_Specified: boolean;
    FholderData: PTiHolderForTicket;
    FholderData_Specified: boolean;
    FcodeToVerifyForTicket: string;
    FcodeToVerifyForTicket_Specified: boolean;
    Fplace: Array_Of_PTiPlace;
    Fplace_Specified: boolean;
    FticketLoginCode: string;
    FticketLoginCode_Specified: boolean;
    procedure SetgrossPriceBeforeDiscount(Index: Integer; const ASingle: Single);
    function  grossPriceBeforeDiscount_Specified(Index: Integer): boolean;
    procedure SetholderData(Index: Integer; const APTiHolderForTicket: PTiHolderForTicket);
    function  holderData_Specified(Index: Integer): boolean;
    procedure SetcodeToVerifyForTicket(Index: Integer; const Astring: string);
    function  codeToVerifyForTicket_Specified(Index: Integer): boolean;
    procedure Setplace(Index: Integer; const AArray_Of_PTiPlace: Array_Of_PTiPlace);
    function  place_Specified(Index: Integer): boolean;
    procedure SetticketLoginCode(Index: Integer; const Astring: string);
    function  ticketLoginCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property grossPriceBeforeDiscount: Single              Index (IS_ATTR or IS_OPTN) read FgrossPriceBeforeDiscount write SetgrossPriceBeforeDiscount stored grossPriceBeforeDiscount_Specified;
    property holderData:               PTiHolderForTicket  Index (IS_OPTN) read FholderData write SetholderData stored holderData_Specified;
    property codeToVerifyForTicket:    string              Index (IS_OPTN) read FcodeToVerifyForTicket write SetcodeToVerifyForTicket stored codeToVerifyForTicket_Specified;
    property place:                    Array_Of_PTiPlace   Index (IS_OPTN or IS_UNBD) read Fplace write Setplace stored place_Specified;
    property ticketLoginCode:          string              Index (IS_OPTN) read FticketLoginCode write SetticketLoginCode stored ticketLoginCode_Specified;
  end;

  Array_Of_PWSCarrierLine = array of PWSCarrierLine;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSCarrierLines, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrierLines = class(TRemotable)
  private
    FfromCity: PWSFullyQualifiedCity;
    FfromCity_Specified: boolean;
    FtoCity: PWSFullyQualifiedCity;
    FtoCity_Specified: boolean;
    Fline: Array_Of_PWSCarrierLine;
    Fline_Specified: boolean;
    FcarrierId: PWSCarrierId;
    FcarrierId_Specified: boolean;
    procedure SetfromCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  fromCity_Specified(Index: Integer): boolean;
    procedure SettoCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  toCity_Specified(Index: Integer): boolean;
    procedure Setline(Index: Integer; const AArray_Of_PWSCarrierLine: Array_Of_PWSCarrierLine);
    function  line_Specified(Index: Integer): boolean;
    procedure SetcarrierId(Index: Integer; const APWSCarrierId: PWSCarrierId);
    function  carrierId_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property fromCity:  PWSFullyQualifiedCity    Index (IS_OPTN) read FfromCity write SetfromCity stored fromCity_Specified;
    property toCity:    PWSFullyQualifiedCity    Index (IS_OPTN) read FtoCity write SettoCity stored toCity_Specified;
    property line:      Array_Of_PWSCarrierLine  Index (IS_OPTN or IS_UNBD) read Fline write Setline stored line_Specified;
    property carrierId: PWSCarrierId             Index (IS_OPTN) read FcarrierId write SetcarrierId stored carrierId_Specified;
  end;

  Array_Of_PWSSearchingParams = array of PWSSearchingParams;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : machineConfig, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  machineConfig = class(TRemotable)
  private
    FquickSearche: Array_Of_PWSSearchingParams;
    FquickSearche_Specified: boolean;
    Fstop: PWSStop;
    Fstop_Specified: boolean;
    procedure SetquickSearche(Index: Integer; const AArray_Of_PWSSearchingParams: Array_Of_PWSSearchingParams);
    function  quickSearche_Specified(Index: Integer): boolean;
    procedure Setstop(Index: Integer; const APWSStop: PWSStop);
    function  stop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property quickSearche: Array_Of_PWSSearchingParams  Index (IS_OPTN or IS_UNBD) read FquickSearche write SetquickSearche stored quickSearche_Specified;
    property stop:         PWSStop                      Index (IS_OPTN) read Fstop write Setstop stored stop_Specified;
  end;

  Array_Of_role = array of role;                { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSUser, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSUser = class(TRemotable)
  private
    Frole: Array_Of_role;
    Frole_Specified: boolean;
    FuserInfo: PWSUserInfo;
    FuserInfo_Specified: boolean;
    procedure Setrole(Index: Integer; const AArray_Of_role: Array_Of_role);
    function  role_Specified(Index: Integer): boolean;
    procedure SetuserInfo(Index: Integer; const APWSUserInfo: PWSUserInfo);
    function  userInfo_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property role:     Array_Of_role  Index (IS_OPTN or IS_UNBD) read Frole write Setrole stored role_Specified;
    property userInfo: PWSUserInfo    Index (IS_OPTN) read FuserInfo write SetuserInfo stored userInfo_Specified;
  end;

  Array_Of_discount = array of discount;        { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : stickDiscount, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  stickDiscount = class(TRemotable)
  private
    FwholePrice: Single;
    FwholePrice_Specified: boolean;
    Fdiscount: Array_Of_discount;
    Fdiscount_Specified: boolean;
    procedure SetwholePrice(Index: Integer; const ASingle: Single);
    function  wholePrice_Specified(Index: Integer): boolean;
    procedure Setdiscount(Index: Integer; const AArray_Of_discount: Array_Of_discount);
    function  discount_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property wholePrice: Single             Index (IS_ATTR or IS_OPTN) read FwholePrice write SetwholePrice stored wholePrice_Specified;
    property discount:   Array_Of_discount  Index (IS_OPTN or IS_UNBD) read Fdiscount write Setdiscount stored discount_Specified;
  end;

  Array_Of_relation = array of relation;        { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSCarrierRelations, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSCarrierRelations = class(TRemotable)
  private
    Frelation: Array_Of_relation;
    Frelation_Specified: boolean;
    Fcarrier: PWSCarrier;
    Fcarrier_Specified: boolean;
    FhomeCity: PWSFullyQualifiedCity;
    FhomeCity_Specified: boolean;
    procedure Setrelation(Index: Integer; const AArray_Of_relation: Array_Of_relation);
    function  relation_Specified(Index: Integer): boolean;
    procedure Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
    function  carrier_Specified(Index: Integer): boolean;
    procedure SethomeCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  homeCity_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property relation: Array_Of_relation      Index (IS_OPTN or IS_UNBD) read Frelation write Setrelation stored relation_Specified;
    property carrier:  PWSCarrier             Index (IS_OPTN) read Fcarrier write Setcarrier stored carrier_Specified;
    property homeCity: PWSFullyQualifiedCity  Index (IS_OPTN) read FhomeCity write SethomeCity stored homeCity_Specified;
  end;

  Array_Of_departure = array of departure;      { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTimeTable, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTimeTable = class(TRemotable)
  private
    Fdeparture: Array_Of_departure;
    Fdeparture_Specified: boolean;
    Fstop: PWSFullyQualifiedStop;
    Fstop_Specified: boolean;
    procedure Setdeparture(Index: Integer; const AArray_Of_departure: Array_Of_departure);
    function  departure_Specified(Index: Integer): boolean;
    procedure Setstop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
    function  stop_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property departure: Array_Of_departure     Index (IS_OPTN or IS_UNBD) read Fdeparture write Setdeparture stored departure_Specified;
    property stop:      PWSFullyQualifiedStop  Index (IS_OPTN) read Fstop write Setstop stored stop_Specified;
  end;

  Array_Of_PWSStopInTimeForTimeTable = array of PWSStopInTimeForTimeTable;   { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : departure, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  departure = class(TRemotable)
  private
    FPWSStopInTimeForTimeTable: Array_Of_PWSStopInTimeForTimeTable;
    FPWSStopInTimeForTimeTable_Specified: boolean;
    Fcity: PWSFullyQualifiedCity;
    Fcity_Specified: boolean;
    FthroughCity: PWSFullyQualifiedCityList;
    FthroughCity_Specified: boolean;
    procedure SetPWSStopInTimeForTimeTable(Index: Integer; const AArray_Of_PWSStopInTimeForTimeTable: Array_Of_PWSStopInTimeForTimeTable);
    function  PWSStopInTimeForTimeTable_Specified(Index: Integer): boolean;
    procedure Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
    function  city_Specified(Index: Integer): boolean;
    procedure SetthroughCity(Index: Integer; const APWSFullyQualifiedCityList: PWSFullyQualifiedCityList);
    function  throughCity_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property PWSStopInTimeForTimeTable: Array_Of_PWSStopInTimeForTimeTable  Index (IS_OPTN or IS_UNBD) read FPWSStopInTimeForTimeTable write SetPWSStopInTimeForTimeTable stored PWSStopInTimeForTimeTable_Specified;
    property city:                      PWSFullyQualifiedCity               Index (IS_OPTN) read Fcity write Setcity stored city_Specified;
    property throughCity:               PWSFullyQualifiedCityList           Index (IS_OPTN or IS_UNBD) read FthroughCity write SetthroughCity stored throughCity_Specified;
  end;

  Array_Of_price2 = array of price2;            { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PTiTariffForStick, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PTiTariffForStick = class(TRemotable)
  private
    FpriceId: Int64;
    FpriceId_Specified: boolean;
    FepTariff: Boolean;
    FepTariff_Specified: boolean;
    FkasaTariff: Boolean;
    FkasaTariff_Specified: boolean;
    FhoursToStartB: Int64;
    FhoursToStartB_Specified: boolean;
    FhoursToStartE: Int64;
    FhoursToStartE_Specified: boolean;
    FbackTariff: Boolean;
    FbackTariff_Specified: boolean;
    FreturnMoneyHours: Int64;
    FreturnMoneyHours_Specified: boolean;
    FreturnMoneyPercent: Single;
    FreturnMoneyPercent_Specified: boolean;
    FpayerMonthNo: Integer;
    FpayerMonthNo_Specified: boolean;
    FpayerYearNo: Integer;
    FpayerYearNo_Specified: boolean;
    FpayerNoOr: Boolean;
    FpayerNoOr_Specified: boolean;
    FpayerMonthVal: Single;
    FpayerMonthVal_Specified: boolean;
    FpayerYearVal: Single;
    FpayerYearVal_Specified: boolean;
    FpayerValOr: Boolean;
    FpayerValOr_Specified: boolean;
    FholderMonthNo: Integer;
    FholderMonthNo_Specified: boolean;
    FholderYearNo: Integer;
    FholderYearNo_Specified: boolean;
    FholderNoOr: Boolean;
    FholderNoOr_Specified: boolean;
    FholderMonthVal: Single;
    FholderMonthVal_Specified: boolean;
    FholderYearVal: Single;
    FholderYearVal_Specified: boolean;
    FholderValOr: Boolean;
    FholderValOr_Specified: boolean;
    Flegal: Boolean;
    Flegal_Specified: boolean;
    FnotGovDiscountValid: Boolean;
    FnotGovDiscountValid_Specified: boolean;
    FsmsSendTypeEnable: Boolean;
    FsmsSendTypeEnable_Specified: boolean;
    Fprice: Array_Of_price2;
    Fprice_Specified: boolean;
    FlagguageDescription: string;
    FlagguageDescription_Specified: boolean;
    Fname_: string;
    Fname__Specified: boolean;
    FtariffType: tariffType;
    FtariffType_Specified: boolean;
    FtariffTypeCode: string;
    FtariffTypeCode_Specified: boolean;
    procedure SetpriceId(Index: Integer; const AInt64: Int64);
    function  priceId_Specified(Index: Integer): boolean;
    procedure SetepTariff(Index: Integer; const ABoolean: Boolean);
    function  epTariff_Specified(Index: Integer): boolean;
    procedure SetkasaTariff(Index: Integer; const ABoolean: Boolean);
    function  kasaTariff_Specified(Index: Integer): boolean;
    procedure SethoursToStartB(Index: Integer; const AInt64: Int64);
    function  hoursToStartB_Specified(Index: Integer): boolean;
    procedure SethoursToStartE(Index: Integer; const AInt64: Int64);
    function  hoursToStartE_Specified(Index: Integer): boolean;
    procedure SetbackTariff(Index: Integer; const ABoolean: Boolean);
    function  backTariff_Specified(Index: Integer): boolean;
    procedure SetreturnMoneyHours(Index: Integer; const AInt64: Int64);
    function  returnMoneyHours_Specified(Index: Integer): boolean;
    procedure SetreturnMoneyPercent(Index: Integer; const ASingle: Single);
    function  returnMoneyPercent_Specified(Index: Integer): boolean;
    procedure SetpayerMonthNo(Index: Integer; const AInteger: Integer);
    function  payerMonthNo_Specified(Index: Integer): boolean;
    procedure SetpayerYearNo(Index: Integer; const AInteger: Integer);
    function  payerYearNo_Specified(Index: Integer): boolean;
    procedure SetpayerNoOr(Index: Integer; const ABoolean: Boolean);
    function  payerNoOr_Specified(Index: Integer): boolean;
    procedure SetpayerMonthVal(Index: Integer; const ASingle: Single);
    function  payerMonthVal_Specified(Index: Integer): boolean;
    procedure SetpayerYearVal(Index: Integer; const ASingle: Single);
    function  payerYearVal_Specified(Index: Integer): boolean;
    procedure SetpayerValOr(Index: Integer; const ABoolean: Boolean);
    function  payerValOr_Specified(Index: Integer): boolean;
    procedure SetholderMonthNo(Index: Integer; const AInteger: Integer);
    function  holderMonthNo_Specified(Index: Integer): boolean;
    procedure SetholderYearNo(Index: Integer; const AInteger: Integer);
    function  holderYearNo_Specified(Index: Integer): boolean;
    procedure SetholderNoOr(Index: Integer; const ABoolean: Boolean);
    function  holderNoOr_Specified(Index: Integer): boolean;
    procedure SetholderMonthVal(Index: Integer; const ASingle: Single);
    function  holderMonthVal_Specified(Index: Integer): boolean;
    procedure SetholderYearVal(Index: Integer; const ASingle: Single);
    function  holderYearVal_Specified(Index: Integer): boolean;
    procedure SetholderValOr(Index: Integer; const ABoolean: Boolean);
    function  holderValOr_Specified(Index: Integer): boolean;
    procedure Setlegal(Index: Integer; const ABoolean: Boolean);
    function  legal_Specified(Index: Integer): boolean;
    procedure SetnotGovDiscountValid(Index: Integer; const ABoolean: Boolean);
    function  notGovDiscountValid_Specified(Index: Integer): boolean;
    procedure SetsmsSendTypeEnable(Index: Integer; const ABoolean: Boolean);
    function  smsSendTypeEnable_Specified(Index: Integer): boolean;
    procedure Setprice(Index: Integer; const AArray_Of_price2: Array_Of_price2);
    function  price_Specified(Index: Integer): boolean;
    procedure SetlagguageDescription(Index: Integer; const Astring: string);
    function  lagguageDescription_Specified(Index: Integer): boolean;
    procedure Setname_(Index: Integer; const Astring: string);
    function  name__Specified(Index: Integer): boolean;
    procedure SettariffType(Index: Integer; const AtariffType: tariffType);
    function  tariffType_Specified(Index: Integer): boolean;
    procedure SettariffTypeCode(Index: Integer; const Astring: string);
    function  tariffTypeCode_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property priceId:             Int64            Index (IS_ATTR or IS_OPTN) read FpriceId write SetpriceId stored priceId_Specified;
    property epTariff:            Boolean          Index (IS_ATTR or IS_OPTN) read FepTariff write SetepTariff stored epTariff_Specified;
    property kasaTariff:          Boolean          Index (IS_ATTR or IS_OPTN) read FkasaTariff write SetkasaTariff stored kasaTariff_Specified;
    property hoursToStartB:       Int64            Index (IS_ATTR or IS_OPTN) read FhoursToStartB write SethoursToStartB stored hoursToStartB_Specified;
    property hoursToStartE:       Int64            Index (IS_ATTR or IS_OPTN) read FhoursToStartE write SethoursToStartE stored hoursToStartE_Specified;
    property backTariff:          Boolean          Index (IS_ATTR or IS_OPTN) read FbackTariff write SetbackTariff stored backTariff_Specified;
    property returnMoneyHours:    Int64            Index (IS_ATTR or IS_OPTN) read FreturnMoneyHours write SetreturnMoneyHours stored returnMoneyHours_Specified;
    property returnMoneyPercent:  Single           Index (IS_ATTR or IS_OPTN) read FreturnMoneyPercent write SetreturnMoneyPercent stored returnMoneyPercent_Specified;
    property payerMonthNo:        Integer          Index (IS_ATTR or IS_OPTN) read FpayerMonthNo write SetpayerMonthNo stored payerMonthNo_Specified;
    property payerYearNo:         Integer          Index (IS_ATTR or IS_OPTN) read FpayerYearNo write SetpayerYearNo stored payerYearNo_Specified;
    property payerNoOr:           Boolean          Index (IS_ATTR or IS_OPTN) read FpayerNoOr write SetpayerNoOr stored payerNoOr_Specified;
    property payerMonthVal:       Single           Index (IS_ATTR or IS_OPTN) read FpayerMonthVal write SetpayerMonthVal stored payerMonthVal_Specified;
    property payerYearVal:        Single           Index (IS_ATTR or IS_OPTN) read FpayerYearVal write SetpayerYearVal stored payerYearVal_Specified;
    property payerValOr:          Boolean          Index (IS_ATTR or IS_OPTN) read FpayerValOr write SetpayerValOr stored payerValOr_Specified;
    property holderMonthNo:       Integer          Index (IS_ATTR or IS_OPTN) read FholderMonthNo write SetholderMonthNo stored holderMonthNo_Specified;
    property holderYearNo:        Integer          Index (IS_ATTR or IS_OPTN) read FholderYearNo write SetholderYearNo stored holderYearNo_Specified;
    property holderNoOr:          Boolean          Index (IS_ATTR or IS_OPTN) read FholderNoOr write SetholderNoOr stored holderNoOr_Specified;
    property holderMonthVal:      Single           Index (IS_ATTR or IS_OPTN) read FholderMonthVal write SetholderMonthVal stored holderMonthVal_Specified;
    property holderYearVal:       Single           Index (IS_ATTR or IS_OPTN) read FholderYearVal write SetholderYearVal stored holderYearVal_Specified;
    property holderValOr:         Boolean          Index (IS_ATTR or IS_OPTN) read FholderValOr write SetholderValOr stored holderValOr_Specified;
    property legal:               Boolean          Index (IS_ATTR or IS_OPTN) read Flegal write Setlegal stored legal_Specified;
    property notGovDiscountValid: Boolean          Index (IS_ATTR or IS_OPTN) read FnotGovDiscountValid write SetnotGovDiscountValid stored notGovDiscountValid_Specified;
    property smsSendTypeEnable:   Boolean          Index (IS_ATTR or IS_OPTN) read FsmsSendTypeEnable write SetsmsSendTypeEnable stored smsSendTypeEnable_Specified;
    property price:               Array_Of_price2  Index (IS_OPTN or IS_UNBD) read Fprice write Setprice stored price_Specified;
    property lagguageDescription: string           Index (IS_OPTN) read FlagguageDescription write SetlagguageDescription stored lagguageDescription_Specified;
    property name_:               string           Index (IS_OPTN) read Fname_ write Setname_ stored name__Specified;
    property tariffType:          tariffType       Index (IS_OPTN) read FtariffType write SettariffType stored tariffType_Specified;
    property tariffTypeCode:      string           Index (IS_OPTN) read FtariffTypeCode write SettariffTypeCode stored tariffTypeCode_Specified;
  end;

  Array_Of_PWSWaypoint = array of PWSWaypoint;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSTrackRecording, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTrackRecording = class(TRemotable)
  private
    FbeginOfRecording: TXSDateTime;
    FbeginOfRecording_Specified: boolean;
    FtrackRecordingType: Integer;
    FtrackRecordingType_Specified: boolean;
    FrecordingNo: string;
    FrecordingNo_Specified: boolean;
    Fdriver: driver;
    Fdriver_Specified: boolean;
    Fvehicle: PWSVehicle;
    Fvehicle_Specified: boolean;
    FbusCourse: PWSTiBusCourse;
    FbusCourse_Specified: boolean;
    FlastRecordedPoint: Array_Of_PWSWaypoint;
    FlastRecordedPoint_Specified: boolean;
    procedure SetbeginOfRecording(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  beginOfRecording_Specified(Index: Integer): boolean;
    procedure SettrackRecordingType(Index: Integer; const AInteger: Integer);
    function  trackRecordingType_Specified(Index: Integer): boolean;
    procedure SetrecordingNo(Index: Integer; const Astring: string);
    function  recordingNo_Specified(Index: Integer): boolean;
    procedure Setdriver(Index: Integer; const Adriver: driver);
    function  driver_Specified(Index: Integer): boolean;
    procedure Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
    function  vehicle_Specified(Index: Integer): boolean;
    procedure SetbusCourse(Index: Integer; const APWSTiBusCourse: PWSTiBusCourse);
    function  busCourse_Specified(Index: Integer): boolean;
    procedure SetlastRecordedPoint(Index: Integer; const AArray_Of_PWSWaypoint: Array_Of_PWSWaypoint);
    function  lastRecordedPoint_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property beginOfRecording:   TXSDateTime           Index (IS_ATTR or IS_OPTN) read FbeginOfRecording write SetbeginOfRecording stored beginOfRecording_Specified;
    property trackRecordingType: Integer               Index (IS_ATTR or IS_OPTN) read FtrackRecordingType write SettrackRecordingType stored trackRecordingType_Specified;
    property recordingNo:        string                Index (IS_OPTN) read FrecordingNo write SetrecordingNo stored recordingNo_Specified;
    property driver:             driver                Index (IS_OPTN) read Fdriver write Setdriver stored driver_Specified;
    property vehicle:            PWSVehicle            Index (IS_OPTN) read Fvehicle write Setvehicle stored vehicle_Specified;
    property busCourse:          PWSTiBusCourse        Index (IS_OPTN) read FbusCourse write SetbusCourse stored busCourse_Specified;
    property lastRecordedPoint:  Array_Of_PWSWaypoint  Index (IS_OPTN or IS_UNBD) read FlastRecordedPoint write SetlastRecordedPoint stored lastRecordedPoint_Specified;
  end;

  Array_Of_ticket2 = array of ticket3;          { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiDetailedReservation, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSTiDetailedReservation = class(TRemotable)
  private
    Freservation: reservation;
    Freservation_Specified: boolean;
    Fpayer: payer;
    Fpayer_Specified: boolean;
    Fticket: Array_Of_ticket2;
    Fticket_Specified: boolean;
    FperTicket: PWSTiPeriodicTickets;
    FperTicket_Specified: boolean;
    FdefaultSendingData: PWSTiSendingData;
    FdefaultSendingData_Specified: boolean;
    procedure Setreservation(Index: Integer; const Areservation: reservation);
    function  reservation_Specified(Index: Integer): boolean;
    procedure Setpayer(Index: Integer; const Apayer: payer);
    function  payer_Specified(Index: Integer): boolean;
    procedure Setticket(Index: Integer; const AArray_Of_ticket2: Array_Of_ticket2);
    function  ticket_Specified(Index: Integer): boolean;
    procedure SetperTicket(Index: Integer; const APWSTiPeriodicTickets: PWSTiPeriodicTickets);
    function  perTicket_Specified(Index: Integer): boolean;
    procedure SetdefaultSendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
    function  defaultSendingData_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property reservation:        reservation           Index (IS_OPTN) read Freservation write Setreservation stored reservation_Specified;
    property payer:              payer                 Index (IS_OPTN) read Fpayer write Setpayer stored payer_Specified;
    property ticket:             Array_Of_ticket2      Index (IS_OPTN or IS_UNBD) read Fticket write Setticket stored ticket_Specified;
    property perTicket:          PWSTiPeriodicTickets  Index (IS_OPTN or IS_UNBD) read FperTicket write SetperTicket stored perTicket_Specified;
    property defaultSendingData: PWSTiSendingData      Index (IS_OPTN) read FdefaultSendingData write SetdefaultSendingData stored defaultSendingData_Specified;
  end;

  Array_Of_place2 = array of place2;            { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : ticket, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  ticket3 = class(TRemotable)
  private
    FticketId: Int64;
    FticketId_Specified: boolean;
    FgoDate: TXSDateTime;
    FgoDate_Specified: boolean;
    FconnectionDate: TXSDateTime;
    FconnectionDate_Specified: boolean;
    FgrossPrice: Single;
    FgrossPrice_Specified: boolean;
    FvatRate: Single;
    FvatRate_Specified: boolean;
    FvatValue: Single;
    FvatValue_Specified: boolean;
    FcodeToVerify: string;
    FcodeToVerify_Specified: boolean;
    FticketLoginCode: string;
    FticketLoginCode_Specified: boolean;
    Fplace: Array_Of_place2;
    Fplace_Specified: boolean;
    Fconnection: connection;
    Fconnection_Specified: boolean;
    Fholder: holder2;
    Fholder_Specified: boolean;
    Ftariff: PWSTiTariffForStick;
    Ftariff_Specified: boolean;
    procedure SetticketId(Index: Integer; const AInt64: Int64);
    function  ticketId_Specified(Index: Integer): boolean;
    procedure SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  goDate_Specified(Index: Integer): boolean;
    procedure SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  connectionDate_Specified(Index: Integer): boolean;
    procedure SetgrossPrice(Index: Integer; const ASingle: Single);
    function  grossPrice_Specified(Index: Integer): boolean;
    procedure SetvatRate(Index: Integer; const ASingle: Single);
    function  vatRate_Specified(Index: Integer): boolean;
    procedure SetvatValue(Index: Integer; const ASingle: Single);
    function  vatValue_Specified(Index: Integer): boolean;
    procedure SetcodeToVerify(Index: Integer; const Astring: string);
    function  codeToVerify_Specified(Index: Integer): boolean;
    procedure SetticketLoginCode(Index: Integer; const Astring: string);
    function  ticketLoginCode_Specified(Index: Integer): boolean;
    procedure Setplace(Index: Integer; const AArray_Of_place2: Array_Of_place2);
    function  place_Specified(Index: Integer): boolean;
    procedure Setconnection(Index: Integer; const Aconnection: connection);
    function  connection_Specified(Index: Integer): boolean;
    procedure Setholder(Index: Integer; const Aholder2: holder2);
    function  holder_Specified(Index: Integer): boolean;
    procedure Settariff(Index: Integer; const APWSTiTariffForStick: PWSTiTariffForStick);
    function  tariff_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property ticketId:        Int64                Index (IS_ATTR or IS_OPTN) read FticketId write SetticketId stored ticketId_Specified;
    property goDate:          TXSDateTime          Index (IS_ATTR or IS_OPTN) read FgoDate write SetgoDate stored goDate_Specified;
    property connectionDate:  TXSDateTime          Index (IS_ATTR or IS_OPTN) read FconnectionDate write SetconnectionDate stored connectionDate_Specified;
    property grossPrice:      Single               Index (IS_ATTR or IS_OPTN) read FgrossPrice write SetgrossPrice stored grossPrice_Specified;
    property vatRate:         Single               Index (IS_ATTR or IS_OPTN) read FvatRate write SetvatRate stored vatRate_Specified;
    property vatValue:        Single               Index (IS_ATTR or IS_OPTN) read FvatValue write SetvatValue stored vatValue_Specified;
    property codeToVerify:    string               Index (IS_OPTN) read FcodeToVerify write SetcodeToVerify stored codeToVerify_Specified;
    property ticketLoginCode: string               Index (IS_OPTN) read FticketLoginCode write SetticketLoginCode stored ticketLoginCode_Specified;
    property place:           Array_Of_place2      Index (IS_OPTN or IS_UNBD) read Fplace write Setplace stored place_Specified;
    property connection:      connection           Index (IS_OPTN) read Fconnection write Setconnection stored connection_Specified;
    property holder:          holder2              Index (IS_OPTN) read Fholder write Setholder stored holder_Specified;
    property tariff:          PWSTiTariffForStick  Index (IS_OPTN) read Ftariff write Settariff stored tariff_Specified;
  end;

  Array_Of_param = array of param2;             { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSResultPriceDetailsParams, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSResultPriceDetailsParams = class(TRemotable)
  private
    FsearchDate: TXSDateTime;
    FsearchDate_Specified: boolean;
    Fparam: Array_Of_param;
    Fparam_Specified: boolean;
    procedure SetsearchDate(Index: Integer; const ATXSDateTime: TXSDateTime);
    function  searchDate_Specified(Index: Integer): boolean;
    procedure Setparam(Index: Integer; const AArray_Of_param: Array_Of_param);
    function  param_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property searchDate: TXSDateTime     Index (IS_ATTR or IS_OPTN) read FsearchDate write SetsearchDate stored searchDate_Specified;
    property param:      Array_Of_param  Index (IS_OPTN or IS_UNBD) read Fparam write Setparam stored param_Specified;
  end;

  Array_Of_result2 = array of result;           { "http://83.15.136.94:54321/axis2/services"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSSearchingResult, global, <complexType>
  // Namespace : http://83.15.136.94:54321/axis2/services
  // ************************************************************************ //
  PWSSearchingResult = class(TRemotable)
  private
    Fresult: Array_Of_result2;
    Fresult_Specified: boolean;
    FresultsId: string;
    FresultsId_Specified: boolean;
    procedure Setresult(Index: Integer; const AArray_Of_result2: Array_Of_result2);
    function  result_Specified(Index: Integer): boolean;
    procedure SetresultsId(Index: Integer; const Astring: string);
    function  resultsId_Specified(Index: Integer): boolean;
  published
    property result:    Array_Of_result2  Index (IS_OPTN or IS_UNBD) read Fresult write Setresult stored result_Specified;
    property resultsId: string            Index (IS_OPTN) read FresultsId write SetresultsId stored resultsId_Specified;
  end;

  Array_Of_causesForTicket = array of causesForTicket;   { "http://83.15.136.94:54321/axis2/services/PWebService"[Ubnd] }


  // ************************************************************************ //
  // XML       : PWSTiSendTickets, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSTiSendTickets = class(ERemotableException)
  private
    FcausesForTicket: Array_Of_causesForTicket;
    FcausesForTicket_Specified: boolean;
    FcommonCause: Array_Of_PWSEnumParam;
    FcommonCause_Specified: boolean;
    procedure SetcausesForTicket(Index: Integer; const AArray_Of_causesForTicket: Array_Of_causesForTicket);
    function  causesForTicket_Specified(Index: Integer): boolean;
    procedure SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  commonCause_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property causesForTicket: Array_Of_causesForTicket  Index (IS_OPTN or IS_UNBD) read FcausesForTicket write SetcausesForTicket stored causesForTicket_Specified;
    property commonCause:     Array_Of_PWSEnumParam     Index (IS_OPTN or IS_UNBD) read FcommonCause write SetcommonCause stored commonCause_Specified;
  end;

  Array_Of_PWSTiTicketUnavailableFaultData = array of PWSTiTicketUnavailableFaultData;   { "http://83.15.136.94:54321/axis2/services"[GblUbnd] }


  // ************************************************************************ //
  // XML       : PWSTiOrderUnavailable, global, <element>
  // Namespace : http://83.15.136.94:54321/axis2/services/PWebService
  // Info      : Fault
  // ************************************************************************ //
  PWSTiOrderUnavailable = class(ERemotableException)
  private
    FPWSTiTicketUnavailableFaultData: Array_Of_PWSTiTicketUnavailableFaultData;
    FPWSTiTicketUnavailableFaultData_Specified: boolean;
    FperiodicCauses: PWSTiPeriodicCardIdsExceptionFaultData;
    FperiodicCauses_Specified: boolean;
    FcommonCause: Array_Of_PWSEnumParam;
    FcommonCause_Specified: boolean;
    procedure SetPWSTiTicketUnavailableFaultData(Index: Integer; const AArray_Of_PWSTiTicketUnavailableFaultData: Array_Of_PWSTiTicketUnavailableFaultData);
    function  PWSTiTicketUnavailableFaultData_Specified(Index: Integer): boolean;
    procedure SetperiodicCauses(Index: Integer; const APWSTiPeriodicCardIdsExceptionFaultData: PWSTiPeriodicCardIdsExceptionFaultData);
    function  periodicCauses_Specified(Index: Integer): boolean;
    procedure SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
    function  commonCause_Specified(Index: Integer): boolean;
  public
    destructor Destroy; override;
  published
    property PWSTiTicketUnavailableFaultData: Array_Of_PWSTiTicketUnavailableFaultData  Index (IS_OPTN or IS_UNBD) read FPWSTiTicketUnavailableFaultData write SetPWSTiTicketUnavailableFaultData stored PWSTiTicketUnavailableFaultData_Specified;
    property periodicCauses:                  PWSTiPeriodicCardIdsExceptionFaultData    Index (IS_OPTN) read FperiodicCauses write SetperiodicCauses stored periodicCauses_Specified;
    property commonCause:                     Array_Of_PWSEnumParam                     Index (IS_OPTN or IS_UNBD) read FcommonCause write SetcommonCause stored commonCause_Specified;
  end;


  // ************************************************************************ //
  // Namespace : http://inno.com/epodroznik/businessLogic/webService/impl/PWebService
  // soapAction: urn:%operationName%
  // transport : http://schemas.xmlsoap.org/soap/http
  // style     : document
  // binding   : PWebServiceBinding
  // service   : PWebService
  // port      : PWebServicePort
  // URL       : http://10.22.171.64:8080/axis2/services/PWebService/
  // ************************************************************************ //
  PWebServicePortType = interface(IInvokable)
  ['{49AE7350-C455-A8D5-300F-52CE34689B0D}']
    function  connExists(const params: PWSSearchingParams; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getOpinionsDetails(const carrierids: PWSCarrierIdList; const wsUser: PWSUserInfo): PWSOpinionsForCarrierList; stdcall;
    function  getCarriers(const params: PWSCarrierSearcherParams; const wsUser: PWSUserInfo): PWSCarrierDetailsList; stdcall;
    function  getCarriersWithUrbanFilter(const params: PWSCarrierSearcherParams; const wsUser: PWSUserInfo; const withUrban: Boolean): PWSCarrierDetailsList; stdcall;
    function  getConns(const params: PWSSearchingParams; const wsUser: PWSUserInfo): PWSSearchingResult; stdcall;
    function  getAddConns(const params: PWSSearchingParams; const wsUser: PWSUserInfo; const resultId: string): PWSSearchingResult; stdcall;
    function  getPriceDetails(const params: PWSResultPriceDetailsParams; const wsUser: PWSUserInfo): PWSResultPriceDetails; stdcall;
    function  getRelationDetails(const connIds: PWSRelationParamsList; const wsUser: PWSUserInfo): PWSRelationList; stdcall;
    function  getRouteDetails(const params: PWSResultRouteDetailsParams; const wsUser: PWSUserInfo): PWSResultRouteDetails; stdcall;
    function  getStops(const cityNames: PWSGetStopParamList; const wsUser: PWSUserInfo): PWSCitiesStopsList; stdcall;
    function  getTimeTable(const params: PWSTTSearchingParams; const wsUser: PWSUserInfo): PWSTimeTable; stdcall;
    function  login(const username: string; const password: string): PWSUser; stdcall;
    function  logout(const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getCosts(const fromDate: TXSDateTime; const toDate: TXSDateTime; const wsUser: PWSUserInfo): PWSCosts; stdcall;
    function  createSearchingAccount(const newUserParams: PWSUserCreateParams; const wsUser: PWSUserInfo): Int64; stdcall;
    function  createSUsersManAccount(const params: PWSUserCreateParams; const wsUser: PWSUserInfo): Int64; stdcall;
    function  removeSearchingAccount(const systemUserId: Int64; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  lockSearchingAccount(const systemUserId: Int64; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  unlockSearchingAccount(const systemUserId: Int64; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  setSearchingAccountValidity(const systemUserId: Int64; const from: TXSDateTime; const to_: TXSDateTime; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  changeUserPassword(const systemUserId: Int64; const newPassword: string; const newPasswdRep: string; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getSearchingAccounts(const wsUser: PWSUserInfo): PWSWebServiceUserList; stdcall;
    function  getSearchingAccount(const wsUser: PWSUserInfo): PWSWebServiceUser; stdcall;
    function  changePassword(const newPassword: string; const newPasswdRep: string; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  changeUserData(const newUserData: PWSChangeUserDataParams; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getHoldersMatrixByConnId(const connectionId: Int64; const date: TXSDateTime; const wsUser: PWSUserInfo): PTiHoldersMatrix; stdcall;
    function  getHoldersMatrixByInfNrKursu(const infNrKursu: Int64; const date: TXSDateTime; const wsUser: PWSUserInfo): PTiHoldersMatrix; stdcall;
    function  getHoldersMatrixByInfNrKursuAndCarrierId(const infNrKursu: Int64; const carrierId: Int64; const date: TXSDateTime; const wsUser: PWSUserInfo): PTiHoldersMatrix; stdcall;
    function  getCarriersByUserData(const wsUser: PWSUserInfo): PWSCarrierDetailsList; stdcall;
    function  getRelationsForCarrier(const carrierId: PWSCarrierId; const wsUser: PWSUserInfo): PWSCarrierRelations; stdcall;
    function  getLinesForCarrier(const carrierId: PWSCarrierId; const fromCityId: PWSCityId; const toCityId: PWSCityId; const wsUser: PWSUserInfo): PWSCarrierLines; stdcall;
    function  getConnectionsForLine(const carrierId: PWSCarrierId; const carrierLine: PWSCarrierLine; const date: TXSDateTime; const wsUser: PWSUserInfo): PWSSearchingResult; stdcall;
    function  getInfKursy(const infNrKursu: string; const carrierId: Int64; const wsUser: PWSUserInfo): PWSInfKursList; stdcall;
    function  getCitySuggestion(const pattern: string; const perfectMatch: Boolean; const getStopsCount: Boolean; const getSettlementType: Boolean; const getCoordinates: Boolean; const getAllCities: Boolean; 
                                const wsUser: PWSUserInfo): PWSFullyQualifiedCityExtList; stdcall;
    function  getCitySuggestionForAddress(const pattern: string; const wsUser: PWSUserInfo): PWSFullyQualifiedCityList; stdcall;
    function  getWebServiceUserSellingConfig(const wsUser: PWSUserInfo): PWSTiWebServiceUserSellingConfig; stdcall;
    function  getConnsWithSellingData(const params: PWSSearchingParams; const wsUser: PWSUserInfo; const resultId: string; const withSellingData: Boolean): PWSTiSearchingResultWithSellingData; stdcall;
    function  getSellingData(const sticksIds: PWSTiStickIds; const goDate: TXSDateTime; const wsUser: PWSUserInfo): PWSTiSellingData; stdcall;
    function  makeOrder(const order: PWSTiOrderWithCustomerData; const wsUser: PWSUserInfo): PWSTiReservationDone; stdcall;
    function  commitOrder(const reservationId: PWSTiReservationId; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  rollbackOrder(const reservationId: PWSTiReservationId; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getTicket(const ticketLoginCode: string; const wsUser: PWSUserInfo): PWSTiDetailedReservation; stdcall;
    function  getTicketByReservationId(const reservationId: PWSTiReservationId; const wsUser: PWSUserInfo): PWSTiDetailedReservation; stdcall;
    function  cancelTicket(const range: PWSTiReservationCancelRange; const cancelInfo: PWSTiReservationCancelInfo; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  changeTicketConnectionDate(const ticketId: Int64; const newConnectionDate: TXSDateTime; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  sendTicket(const ticketId: Int64; const sendTicketInfo: PWSTiSendTicketInfo; const wsFormat: PWSTiSendTicketFormat; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  sendTickets(const wsReservationId: PWSTiReservationId; const wsSendTicketInfo: PWSTiSendTicketInfo; const wsFormat: PWSTiSendTicketFormat; const invoice: Boolean; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  changeTicketHolderData(const ticketId: Int64; const holderData: PWSTiHolderForTicket; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  logVendingMachineEvent(const vendingEvent: PWSTiVendingEvent; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getVendingMachineParams(const traceModifyTimestamp: TXSDateTime; const wsUser: PWSUserInfo): PWSTiVendingParams; stdcall;
    function  getCarrierRegulations(const carrierId: Int64; const wsUser: PWSUserInfo): string; stdcall;
    function  getSendNormalTicketDataByReservationId(const resId: PWSTiReservationId; const userInfo: PWSUserInfo): PWSTiSendNormalTicketDataList; stdcall;
    function  getConnSearchingDetails(const params: PWSSearchingParams; const wsUser: PWSUserInfo): PWSConnSearchingDetails; stdcall;
    function  getLastVehiclePosition(const vehicle: PWSVehicle; const wsUser: PWSUserInfo): PWSVehiclePosition; stdcall;
    function  getLastVehiclesPositions(const vehicles: PWSVehicleList; const wsUser: PWSUserInfo): PWSVehiclePositionList; stdcall;
    function  getLastVehiclesPositionsForCompany(const carrier: PWSInformicaCarrier; const wsUser: PWSUserInfo): PWSVehiclePositionList; stdcall;
    function  getTrackRecordingsForCarrierInTimeInterval(const carrier: PWSInformicaCarrier; const fromDate: TXSDateTime; const toDate: TXSDateTime; const wsUser: PWSUserInfo): PWSTrackRecordingList; stdcall;
    function  getLastTrackRecordingDataForCarrierInTimeInterval(const carrier: PWSInformicaCarrier; const fromDate: TXSDateTime; const toDate: TXSDateTime; const wsUser: PWSUserInfo): PWSTrackRecordingList; stdcall;
    function  getDataForCourseTrackRecording(const carrier: PWSInformicaCarrier; const busCourse: PWSTiBusCourse; const runDate: TXSDateTime; const fullTrack: Boolean; const wsUser: PWSUserInfo): PWSTrackRecording; stdcall;
    function  getDataForTrackRecording(const carrier: PWSInformicaCarrier; const recordingNo: string; const runDate: TXSDateTime; const fullTrack: Boolean; const wsUser: PWSUserInfo): PWSTrackRecording; stdcall;
    function  getLastTrackRecordingsData(const courseList: PWSTiBusCourseList; const date: TXSDateTime; const wsUser: PWSUserInfo): PWSTrackRecordingList; stdcall;
    function  getDataForTrackRecordings(const courseList: PWSTiBusCourseList; const date: TXSDateTime; const fullTrack: Boolean; const wsUser: PWSUserInfo): PWSTrackRecordingList; stdcall;
    function  sendMessageToDriver(const message_: PWSMessage; const vehicle: PWSVehicle; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getMessagesFromDriversSinceTime(const carrier: PWSInformicaCarrier; const time: TXSDateTime; const wsUser: PWSUserInfo): PWSMessageFromDriverList; stdcall;
    function  savePeriodicTicketsData(const periodicTickets: PWSTiPeriodicTickets; const wsUser: PWSUserInfo): Boolean; stdcall;
    function  getSellingReportForDay(const date: TXSDateTime; const carrier: PWSInformicaCarrier; const wsUser: PWSUserInfo): PWSTiSellingReport; stdcall;
  end;

function GetPWebServicePortType(UseWSDL: Boolean=System.False; Addr: string=''; HTTPRIO: THTTPRIO = nil): PWebServicePortType;


implementation
  uses SysUtils;

function GetPWebServicePortType(UseWSDL: Boolean; Addr: string; HTTPRIO: THTTPRIO): PWebServicePortType;
const
  defWSDL = 'http://83.15.136.94:54321/axis2/services/PWebService?wsdl';
  defURL  = 'http://83.15.136.94:54321/axis2/services/PWebService';
  defSvc  = 'PWebService';
  defPrt  = 'PWebServicePort';
var
  RIO: THTTPRIO;
begin
  Result := nil;
  if (Addr = '') then
  begin
    if UseWSDL then
      Addr := defWSDL
    else
      Addr := defURL;
  end;
  if HTTPRIO = nil then
    RIO := THTTPRIO.Create(nil)
  else
    RIO := HTTPRIO;
  try
    Result := (RIO as PWebServicePortType);
    if UseWSDL then
    begin
      RIO.WSDLLocation := Addr;
      RIO.Service := defSvc;
      RIO.Port := defPrt;
    end else
      RIO.URL := Addr;
  finally
    if (Result = nil) and (HTTPRIO = nil) then
      RIO.Free;
  end;
end;


destructor PTiStopInTime.Destroy;
begin
  SysUtils.FreeAndNil(FarrivalTime);
  SysUtils.FreeAndNil(FdepartureTime);
  inherited Destroy;
end;

procedure PTiStopInTime.SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FarrivalTime := ATXSDateTime;
  FarrivalTime_Specified := True;
end;

function PTiStopInTime.arrivalTime_Specified(Index: Integer): boolean;
begin
  Result := FarrivalTime_Specified;
end;

procedure PTiStopInTime.SetdepartureTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdepartureTime := ATXSDateTime;
  FdepartureTime_Specified := True;
end;

function PTiStopInTime.departureTime_Specified(Index: Integer): boolean;
begin
  Result := FdepartureTime_Specified;
end;

procedure PTiStopInTime.SetstopName(Index: Integer; const Astring: string);
begin
  FstopName := Astring;
  FstopName_Specified := True;
end;

function PTiStopInTime.stopName_Specified(Index: Integer): boolean;
begin
  Result := FstopName_Specified;
end;

procedure PTiStopInTime.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function PTiStopInTime.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

procedure PTiStopInTime.SetcommuneName(Index: Integer; const Astring: string);
begin
  FcommuneName := Astring;
  FcommuneName_Specified := True;
end;

function PTiStopInTime.communeName_Specified(Index: Integer): boolean;
begin
  Result := FcommuneName_Specified;
end;

procedure PTiStopInTime.SetdistrictName(Index: Integer; const Astring: string);
begin
  FdistrictName := Astring;
  FdistrictName_Specified := True;
end;

function PTiStopInTime.districtName_Specified(Index: Integer): boolean;
begin
  Result := FdistrictName_Specified;
end;

procedure PTiStopInTime.SetprovinceName(Index: Integer; const Astring: string);
begin
  FprovinceName := Astring;
  FprovinceName_Specified := True;
end;

function PTiStopInTime.provinceName_Specified(Index: Integer): boolean;
begin
  Result := FprovinceName_Specified;
end;

procedure PTiStopInTime.SetcountryName(Index: Integer; const Astring: string);
begin
  FcountryName := Astring;
  FcountryName_Specified := True;
end;

function PTiStopInTime.countryName_Specified(Index: Integer): boolean;
begin
  Result := FcountryName_Specified;
end;

destructor PWSUserCreateParams.Destroy;
begin
  SysUtils.FreeAndNil(FvalidFrom);
  SysUtils.FreeAndNil(FvalidTo);
  inherited Destroy;
end;

procedure PWSUserCreateParams.Setblocked(Index: Integer; const ABoolean: Boolean);
begin
  Fblocked := ABoolean;
  Fblocked_Specified := True;
end;

function PWSUserCreateParams.blocked_Specified(Index: Integer): boolean;
begin
  Result := Fblocked_Specified;
end;

procedure PWSUserCreateParams.SetvalidFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidFrom := ATXSDateTime;
  FvalidFrom_Specified := True;
end;

function PWSUserCreateParams.validFrom_Specified(Index: Integer): boolean;
begin
  Result := FvalidFrom_Specified;
end;

procedure PWSUserCreateParams.SetvalidTo(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidTo := ATXSDateTime;
  FvalidTo_Specified := True;
end;

function PWSUserCreateParams.validTo_Specified(Index: Integer): boolean;
begin
  Result := FvalidTo_Specified;
end;

procedure PWSUserCreateParams.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PWSUserCreateParams.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PWSUserCreateParams.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PWSUserCreateParams.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PWSUserCreateParams.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function PWSUserCreateParams.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure PWSUserCreateParams.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function PWSUserCreateParams.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

procedure PWSUserCreateParams.Setlogin(Index: Integer; const Astring: string);
begin
  Flogin := Astring;
  Flogin_Specified := True;
end;

function PWSUserCreateParams.login_Specified(Index: Integer): boolean;
begin
  Result := Flogin_Specified;
end;

procedure PWSUserCreateParams.Setpassword(Index: Integer; const Astring: string);
begin
  Fpassword := Astring;
  Fpassword_Specified := True;
end;

function PWSUserCreateParams.password_Specified(Index: Integer): boolean;
begin
  Result := Fpassword_Specified;
end;

procedure PWSUserCreateParams.Setpassword2(Index: Integer; const Astring: string);
begin
  Fpassword2 := Astring;
  Fpassword2_Specified := True;
end;

function PWSUserCreateParams.password2_Specified(Index: Integer): boolean;
begin
  Result := Fpassword2_Specified;
end;

destructor PWSTTSearchingParams.Destroy;
begin
  SysUtils.FreeAndNil(FfromTime);
  SysUtils.FreeAndNil(FtoTime);
  SysUtils.FreeAndNil(Fdate);
  inherited Destroy;
end;

procedure PWSTTSearchingParams.SetcarrierTypeId(Index: Integer; const AInt64: Int64);
begin
  FcarrierTypeId := AInt64;
  FcarrierTypeId_Specified := True;
end;

function PWSTTSearchingParams.carrierTypeId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierTypeId_Specified;
end;

procedure PWSTTSearchingParams.SetcarrierId(Index: Integer; const AInt64: Int64);
begin
  FcarrierId := AInt64;
  FcarrierId_Specified := True;
end;

function PWSTTSearchingParams.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

procedure PWSTTSearchingParams.SetfromTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FfromTime := ATXSDateTime;
  FfromTime_Specified := True;
end;

function PWSTTSearchingParams.fromTime_Specified(Index: Integer): boolean;
begin
  Result := FfromTime_Specified;
end;

procedure PWSTTSearchingParams.SettoTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtoTime := ATXSDateTime;
  FtoTime_Specified := True;
end;

function PWSTTSearchingParams.toTime_Specified(Index: Integer): boolean;
begin
  Result := FtoTime_Specified;
end;

procedure PWSTTSearchingParams.Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Fdate := ATXSDateTime;
  Fdate_Specified := True;
end;

function PWSTTSearchingParams.date_Specified(Index: Integer): boolean;
begin
  Result := Fdate_Specified;
end;

procedure PWSTTSearchingParams.SetfilterCode(Index: Integer; const Astring: string);
begin
  FfilterCode := Astring;
  FfilterCode_Specified := True;
end;

function PWSTTSearchingParams.filterCode_Specified(Index: Integer): boolean;
begin
  Result := FfilterCode_Specified;
end;

procedure PWSEnumParam.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSEnumParam.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSEnumParam.Setvalue(Index: Integer; const Astring: string);
begin
  Fvalue := Astring;
  Fvalue_Specified := True;
end;

function PWSEnumParam.value_Specified(Index: Integer): boolean;
begin
  Result := Fvalue_Specified;
end;

destructor PWSTiDiscount.Destroy;
begin
  SysUtils.FreeAndNil(FroundType);
  inherited Destroy;
end;

procedure PWSTiDiscount.SettravelGroupId(Index: Integer; const AInt64: Int64);
begin
  FtravelGroupId := AInt64;
  FtravelGroupId_Specified := True;
end;

function PWSTiDiscount.travelGroupId_Specified(Index: Integer): boolean;
begin
  Result := FtravelGroupId_Specified;
end;

procedure PWSTiDiscount.SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
begin
  FvalueAfterDiscount := ASingle;
  FvalueAfterDiscount_Specified := True;
end;

function PWSTiDiscount.valueAfterDiscount_Specified(Index: Integer): boolean;
begin
  Result := FvalueAfterDiscount_Specified;
end;

procedure PWSTiDiscount.SetdiscountValue(Index: Integer; const ASingle: Single);
begin
  FdiscountValue := ASingle;
  FdiscountValue_Specified := True;
end;

function PWSTiDiscount.discountValue_Specified(Index: Integer): boolean;
begin
  Result := FdiscountValue_Specified;
end;

procedure PWSTiDiscount.Setpercent(Index: Integer; const ABoolean: Boolean);
begin
  Fpercent := ABoolean;
  Fpercent_Specified := True;
end;

function PWSTiDiscount.percent_Specified(Index: Integer): boolean;
begin
  Result := Fpercent_Specified;
end;

procedure PWSTiDiscount.SetdefaultDis(Index: Integer; const ABoolean: Boolean);
begin
  FdefaultDis := ABoolean;
  FdefaultDis_Specified := True;
end;

function PWSTiDiscount.defaultDis_Specified(Index: Integer): boolean;
begin
  Result := FdefaultDis_Specified;
end;

procedure PWSTiDiscount.Sett5grRoundBound(Index: Integer; const ASingle: Single);
begin
  Ft5grRoundBound := ASingle;
  Ft5grRoundBound_Specified := True;
end;

function PWSTiDiscount.t5grRoundBound_Specified(Index: Integer): boolean;
begin
  Result := Ft5grRoundBound_Specified;
end;

procedure PWSTiDiscount.Sett10grRoundBound(Index: Integer; const ASingle: Single);
begin
  Ft10grRoundBound := ASingle;
  Ft10grRoundBound_Specified := True;
end;

function PWSTiDiscount.t10grRoundBound_Specified(Index: Integer): boolean;
begin
  Result := Ft10grRoundBound_Specified;
end;

procedure PWSTiDiscount.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSTiDiscount.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSTiDiscount.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function PWSTiDiscount.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure PWSTiDiscount.Setdescription(Index: Integer; const Astring: string);
begin
  Fdescription := Astring;
  Fdescription_Specified := True;
end;

function PWSTiDiscount.description_Specified(Index: Integer): boolean;
begin
  Result := Fdescription_Specified;
end;

procedure PWSTiDiscount.SetroundType(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  FroundType := APWSEnumParam;
  FroundType_Specified := True;
end;

function PWSTiDiscount.roundType_Specified(Index: Integer): boolean;
begin
  Result := FroundType_Specified;
end;

procedure PWSTiTariffPriceAfterDiscount.SetpriceId(Index: Integer; const AInt64: Int64);
begin
  FpriceId := AInt64;
  FpriceId_Specified := True;
end;

function PWSTiTariffPriceAfterDiscount.priceId_Specified(Index: Integer): boolean;
begin
  Result := FpriceId_Specified;
end;

procedure PWSTiTariffPriceAfterDiscount.SettravelGroupId(Index: Integer; const AInt64: Int64);
begin
  FtravelGroupId := AInt64;
  FtravelGroupId_Specified := True;
end;

function PWSTiTariffPriceAfterDiscount.travelGroupId_Specified(Index: Integer): boolean;
begin
  Result := FtravelGroupId_Specified;
end;

procedure PWSTiTariffPriceAfterDiscount.Setvalue(Index: Integer; const ASingle: Single);
begin
  Fvalue := ASingle;
  Fvalue_Specified := True;
end;

function PWSTiTariffPriceAfterDiscount.value_Specified(Index: Integer): boolean;
begin
  Result := Fvalue_Specified;
end;

procedure PWSTiDocType.SetlongCode(Index: Integer; const Astring: string);
begin
  FlongCode := Astring;
  FlongCode_Specified := True;
end;

function PWSTiDocType.longCode_Specified(Index: Integer): boolean;
begin
  Result := FlongCode_Specified;
end;

procedure PWSTiDocType.SetshortCode(Index: Integer; const Astring: string);
begin
  FshortCode := Astring;
  FshortCode_Specified := True;
end;

function PWSTiDocType.shortCode_Specified(Index: Integer): boolean;
begin
  Result := FshortCode_Specified;
end;

procedure PWSTiDocType.SetlongPrinatble(Index: Integer; const Astring: string);
begin
  FlongPrinatble := Astring;
  FlongPrinatble_Specified := True;
end;

function PWSTiDocType.longPrinatble_Specified(Index: Integer): boolean;
begin
  Result := FlongPrinatble_Specified;
end;

procedure PWSTiDocType.SetshortPrinatble(Index: Integer; const Astring: string);
begin
  FshortPrinatble := Astring;
  FshortPrinatble_Specified := True;
end;

function PWSTiDocType.shortPrinatble_Specified(Index: Integer): boolean;
begin
  Result := FshortPrinatble_Specified;
end;

procedure PWSStop.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSStop.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSStop.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function PWSStop.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

destructor PWSCostForPeriod.Destroy;
begin
  SysUtils.FreeAndNil(FfromDate);
  SysUtils.FreeAndNil(FtoDate);
  inherited Destroy;
end;

procedure PWSCostForPeriod.SetfromDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FfromDate := ATXSDateTime;
  FfromDate_Specified := True;
end;

function PWSCostForPeriod.fromDate_Specified(Index: Integer): boolean;
begin
  Result := FfromDate_Specified;
end;

procedure PWSCostForPeriod.SettoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtoDate := ATXSDateTime;
  FtoDate_Specified := True;
end;

function PWSCostForPeriod.toDate_Specified(Index: Integer): boolean;
begin
  Result := FtoDate_Specified;
end;

procedure PWSCostForPeriod.Setnumber(Index: Integer; const AInt64: Int64);
begin
  Fnumber := AInt64;
  Fnumber_Specified := True;
end;

function PWSCostForPeriod.number_Specified(Index: Integer): boolean;
begin
  Result := Fnumber_Specified;
end;

procedure PWSCostForPeriod.Setcost(Index: Integer; const ASingle: Single);
begin
  Fcost := ASingle;
  Fcost_Specified := True;
end;

function PWSCostForPeriod.cost_Specified(Index: Integer): boolean;
begin
  Result := Fcost_Specified;
end;

procedure PWSCarrierId.SetcarrierId(Index: Integer; const AInt64: Int64);
begin
  FcarrierId := AInt64;
  FcarrierId_Specified := True;
end;

function PWSCarrierId.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

destructor PWSTiOrderWithCustomerData.Destroy;
begin
  SysUtils.FreeAndNil(Forder);
  SysUtils.FreeAndNil(FcustomerData);
  SysUtils.FreeAndNil(FpaymentForm);
  inherited Destroy;
end;

procedure PWSTiOrderWithCustomerData.SetdistributorId(Index: Integer; const AInt64: Int64);
begin
  FdistributorId := AInt64;
  FdistributorId_Specified := True;
end;

function PWSTiOrderWithCustomerData.distributorId_Specified(Index: Integer): boolean;
begin
  Result := FdistributorId_Specified;
end;

procedure PWSTiOrderWithCustomerData.SetvendingMachineId(Index: Integer; const AInt64: Int64);
begin
  FvendingMachineId := AInt64;
  FvendingMachineId_Specified := True;
end;

function PWSTiOrderWithCustomerData.vendingMachineId_Specified(Index: Integer): boolean;
begin
  Result := FvendingMachineId_Specified;
end;

procedure PWSTiOrderWithCustomerData.Setorder(Index: Integer; const Aorder: order);
begin
  Forder := Aorder;
  Forder_Specified := True;
end;

function PWSTiOrderWithCustomerData.order_Specified(Index: Integer): boolean;
begin
  Result := Forder_Specified;
end;

procedure PWSTiOrderWithCustomerData.SetcustomerData(Index: Integer; const AcustomerData: customerData);
begin
  FcustomerData := AcustomerData;
  FcustomerData_Specified := True;
end;

function PWSTiOrderWithCustomerData.customerData_Specified(Index: Integer): boolean;
begin
  Result := FcustomerData_Specified;
end;

procedure PWSTiOrderWithCustomerData.SetpaymentForm(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  FpaymentForm := APWSEnumParam;
  FpaymentForm_Specified := True;
end;

function PWSTiOrderWithCustomerData.paymentForm_Specified(Index: Integer): boolean;
begin
  Result := FpaymentForm_Specified;
end;

destructor PWSTiHolderForTicket.Destroy;
begin
  SysUtils.FreeAndNil(FdocType);
  inherited Destroy;
end;

procedure PWSTiHolderForTicket.SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
begin
  FdocType := APWSTiDocType;
  FdocType_Specified := True;
end;

function PWSTiHolderForTicket.docType_Specified(Index: Integer): boolean;
begin
  Result := FdocType_Specified;
end;

procedure PWSTiHolderForTicket.SetidentifyingDocValue(Index: Integer; const Astring: string);
begin
  FidentifyingDocValue := Astring;
  FidentifyingDocValue_Specified := True;
end;

function PWSTiHolderForTicket.identifyingDocValue_Specified(Index: Integer): boolean;
begin
  Result := FidentifyingDocValue_Specified;
end;

procedure PWSTiHolderForTicket.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PWSTiHolderForTicket.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PWSTiHolderForTicket.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PWSTiHolderForTicket.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PWSTiHolderForTicket.SetcontactPhone(Index: Integer; const Astring: string);
begin
  FcontactPhone := Astring;
  FcontactPhone_Specified := True;
end;

function PWSTiHolderForTicket.contactPhone_Specified(Index: Integer): boolean;
begin
  Result := FcontactPhone_Specified;
end;

destructor place.Destroy;
begin
  SysUtils.FreeAndNil(FholderData);
  inherited Destroy;
end;

procedure place.SetplaceNumber(Index: Integer; const AInteger: Integer);
begin
  FplaceNumber := AInteger;
  FplaceNumber_Specified := True;
end;

function place.placeNumber_Specified(Index: Integer): boolean;
begin
  Result := FplaceNumber_Specified;
end;

procedure place.SettravelGroupId(Index: Integer; const AInt64: Int64);
begin
  FtravelGroupId := AInt64;
  FtravelGroupId_Specified := True;
end;

function place.travelGroupId_Specified(Index: Integer): boolean;
begin
  Result := FtravelGroupId_Specified;
end;

procedure place.SetlagguagePriceId(Index: Integer; const AInt64: Int64);
begin
  FlagguagePriceId := AInt64;
  FlagguagePriceId_Specified := True;
end;

function place.lagguagePriceId_Specified(Index: Integer): boolean;
begin
  Result := FlagguagePriceId_Specified;
end;

procedure place.SetholderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
begin
  FholderData := APWSTiHolderForTicket;
  FholderData_Specified := True;
end;

function place.holderData_Specified(Index: Integer): boolean;
begin
  Result := FholderData_Specified;
end;

destructor periodicTicket.Destroy;
begin
  SysUtils.FreeAndNil(FperiodicCardIdentyfier);
  inherited Destroy;
end;

procedure periodicTicket.SetperiodicCardIdentyfier(Index: Integer; const APWSTiPeriodicCardIdentyfier: PWSTiPeriodicCardIdentyfier);
begin
  FperiodicCardIdentyfier := APWSTiPeriodicCardIdentyfier;
  FperiodicCardIdentyfier_Specified := True;
end;

function periodicTicket.periodicCardIdentyfier_Specified(Index: Integer): boolean;
begin
  Result := FperiodicCardIdentyfier_Specified;
end;

procedure PWSTiPeriodicCardIdentyfier.SetperiodicCardIdentyfier(Index: Integer; const AInt64: Int64);
begin
  FperiodicCardIdentyfier := AInt64;
  FperiodicCardIdentyfier_Specified := True;
end;

function PWSTiPeriodicCardIdentyfier.periodicCardIdentyfier_Specified(Index: Integer): boolean;
begin
  Result := FperiodicCardIdentyfier_Specified;
end;

destructor PWSTiSendingData.Destroy;
begin
  SysUtils.FreeAndNil(Ftype_);
  inherited Destroy;
end;

procedure PWSTiSendingData.SetsendingAddres(Index: Integer; const Astring: string);
begin
  FsendingAddres := Astring;
  FsendingAddres_Specified := True;
end;

function PWSTiSendingData.sendingAddres_Specified(Index: Integer): boolean;
begin
  Result := FsendingAddres_Specified;
end;

procedure PWSTiSendingData.Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  Ftype_ := APWSEnumParam;
  Ftype__Specified := True;
end;

function PWSTiSendingData.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

procedure customerData.SetpayerId(Index: Integer; const AInt64: Int64);
begin
  FpayerId := AInt64;
  FpayerId_Specified := True;
end;

function customerData.payerId_Specified(Index: Integer): boolean;
begin
  Result := FpayerId_Specified;
end;

procedure customerData.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function customerData.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure customerData.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function customerData.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure customerData.Setnip(Index: Integer; const Astring: string);
begin
  Fnip := Astring;
  Fnip_Specified := True;
end;

function customerData.nip_Specified(Index: Integer): boolean;
begin
  Result := Fnip_Specified;
end;

procedure customerData.SetpostalCode(Index: Integer; const Astring: string);
begin
  FpostalCode := Astring;
  FpostalCode_Specified := True;
end;

function customerData.postalCode_Specified(Index: Integer): boolean;
begin
  Result := FpostalCode_Specified;
end;

procedure customerData.Setstreet(Index: Integer; const Astring: string);
begin
  Fstreet := Astring;
  Fstreet_Specified := True;
end;

function customerData.street_Specified(Index: Integer): boolean;
begin
  Result := Fstreet_Specified;
end;

procedure customerData.SetbuildingNumber(Index: Integer; const Astring: string);
begin
  FbuildingNumber := Astring;
  FbuildingNumber_Specified := True;
end;

function customerData.buildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FbuildingNumber_Specified;
end;

procedure customerData.SetinvoiceSendingAddress(Index: Integer; const Astring: string);
begin
  FinvoiceSendingAddress := Astring;
  FinvoiceSendingAddress_Specified := True;
end;

function customerData.invoiceSendingAddress_Specified(Index: Integer): boolean;
begin
  Result := FinvoiceSendingAddress_Specified;
end;

destructor PWSMessage.Destroy;
begin
  SysUtils.FreeAndNil(Fdate);
  inherited Destroy;
end;

procedure PWSMessage.Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Fdate := ATXSDateTime;
  Fdate_Specified := True;
end;

function PWSMessage.date_Specified(Index: Integer): boolean;
begin
  Result := Fdate_Specified;
end;

procedure PWSMessage.Setcontents(Index: Integer; const Astring: string);
begin
  Fcontents := Astring;
  Fcontents_Specified := True;
end;

function PWSMessage.contents_Specified(Index: Integer): boolean;
begin
  Result := Fcontents_Specified;
end;

destructor PWSFullyQualifiedStop.Destroy;
begin
  SysUtils.FreeAndNil(Fcity);
  inherited Destroy;
end;

procedure PWSFullyQualifiedStop.Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  Fcity := APWSFullyQualifiedCity;
  Fcity_Specified := True;
end;

function PWSFullyQualifiedStop.city_Specified(Index: Integer): boolean;
begin
  Result := Fcity_Specified;
end;

procedure PWSFullyQualifiedStop.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSFullyQualifiedStop.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSFullyQualifiedStop.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function PWSFullyQualifiedStop.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

procedure PWSFullyQualifiedCity.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSFullyQualifiedCity.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSFullyQualifiedCity.SetprovinceName(Index: Integer; const Astring: string);
begin
  FprovinceName := Astring;
  FprovinceName_Specified := True;
end;

function PWSFullyQualifiedCity.provinceName_Specified(Index: Integer): boolean;
begin
  Result := FprovinceName_Specified;
end;

procedure PWSFullyQualifiedCity.SetcommuneName(Index: Integer; const Astring: string);
begin
  FcommuneName := Astring;
  FcommuneName_Specified := True;
end;

function PWSFullyQualifiedCity.communeName_Specified(Index: Integer): boolean;
begin
  Result := FcommuneName_Specified;
end;

procedure PWSFullyQualifiedCity.SetdistrictName(Index: Integer; const Astring: string);
begin
  FdistrictName := Astring;
  FdistrictName_Specified := True;
end;

function PWSFullyQualifiedCity.districtName_Specified(Index: Integer): boolean;
begin
  Result := FdistrictName_Specified;
end;

procedure PWSInformicaCarrier.SetcompanyCode(Index: Integer; const Astring: string);
begin
  FcompanyCode := Astring;
  FcompanyCode_Specified := True;
end;

function PWSInformicaCarrier.companyCode_Specified(Index: Integer): boolean;
begin
  Result := FcompanyCode_Specified;
end;

procedure PWSNamePrincipal.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSNamePrincipal.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSNamePrincipal.SetfullName(Index: Integer; const Astring: string);
begin
  FfullName := Astring;
  FfullName_Specified := True;
end;

function PWSNamePrincipal.fullName_Specified(Index: Integer): boolean;
begin
  Result := FfullName_Specified;
end;

destructor PWSConnSearchingDetails.Destroy;
begin
  SysUtils.FreeAndNil(FdateRangeFrom);
  SysUtils.FreeAndNil(FdateRangeTo);
  SysUtils.FreeAndNil(FtimeRangeFrom);
  SysUtils.FreeAndNil(FtimeRangeTo);
  SysUtils.FreeAndNil(FstartCity);
  SysUtils.FreeAndNil(FendCity);
  inherited Destroy;
end;

procedure PWSConnSearchingDetails.SetdateRangeFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdateRangeFrom := ATXSDateTime;
  FdateRangeFrom_Specified := True;
end;

function PWSConnSearchingDetails.dateRangeFrom_Specified(Index: Integer): boolean;
begin
  Result := FdateRangeFrom_Specified;
end;

procedure PWSConnSearchingDetails.SetdateRangeTo(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdateRangeTo := ATXSDateTime;
  FdateRangeTo_Specified := True;
end;

function PWSConnSearchingDetails.dateRangeTo_Specified(Index: Integer): boolean;
begin
  Result := FdateRangeTo_Specified;
end;

procedure PWSConnSearchingDetails.SettimeRangeFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtimeRangeFrom := ATXSDateTime;
  FtimeRangeFrom_Specified := True;
end;

function PWSConnSearchingDetails.timeRangeFrom_Specified(Index: Integer): boolean;
begin
  Result := FtimeRangeFrom_Specified;
end;

procedure PWSConnSearchingDetails.SettimeRangeTo(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtimeRangeTo := ATXSDateTime;
  FtimeRangeTo_Specified := True;
end;

function PWSConnSearchingDetails.timeRangeTo_Specified(Index: Integer): boolean;
begin
  Result := FtimeRangeTo_Specified;
end;

procedure PWSConnSearchingDetails.SetstartCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FstartCity := APWSFullyQualifiedCity;
  FstartCity_Specified := True;
end;

function PWSConnSearchingDetails.startCity_Specified(Index: Integer): boolean;
begin
  Result := FstartCity_Specified;
end;

procedure PWSConnSearchingDetails.SetendCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FendCity := APWSFullyQualifiedCity;
  FendCity_Specified := True;
end;

function PWSConnSearchingDetails.endCity_Specified(Index: Integer): boolean;
begin
  Result := FendCity_Specified;
end;

procedure holder.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function holder.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure holder.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function holder.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure holder.SetkasaHolderId(Index: Integer; const Astring: string);
begin
  FkasaHolderId := Astring;
  FkasaHolderId_Specified := True;
end;

function holder.kasaHolderId_Specified(Index: Integer): boolean;
begin
  Result := FkasaHolderId_Specified;
end;

procedure holder.SetidentifyingDocValue(Index: Integer; const Astring: string);
begin
  FidentifyingDocValue := Astring;
  FidentifyingDocValue_Specified := True;
end;

function holder.identifyingDocValue_Specified(Index: Integer): boolean;
begin
  Result := FidentifyingDocValue_Specified;
end;

destructor PWSTiPeriodicTicketInfo.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FlinesInfo)-1 do
    SysUtils.FreeAndNil(FlinesInfo[I]);
  System.SetLength(FlinesInfo, 0);
  SysUtils.FreeAndNil(FendOfValidity);
  SysUtils.FreeAndNil(FcommitTimestamp);
  SysUtils.FreeAndNil(FperiodicCardId);
  SysUtils.FreeAndNil(Fholder);
  SysUtils.FreeAndNil(Fdiscount);
  inherited Destroy;
end;

procedure PWSTiPeriodicTicketInfo.SetendOfValidity(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FendOfValidity := ATXSDateTime;
  FendOfValidity_Specified := True;
end;

function PWSTiPeriodicTicketInfo.endOfValidity_Specified(Index: Integer): boolean;
begin
  Result := FendOfValidity_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetperiodLengthInDays(Index: Integer; const AInteger: Integer);
begin
  FperiodLengthInDays := AInteger;
  FperiodLengthInDays_Specified := True;
end;

function PWSTiPeriodicTicketInfo.periodLengthInDays_Specified(Index: Integer): boolean;
begin
  Result := FperiodLengthInDays_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetgrossPriceForPeriod(Index: Integer; const ASingle: Single);
begin
  FgrossPriceForPeriod := ASingle;
  FgrossPriceForPeriod_Specified := True;
end;

function PWSTiPeriodicTicketInfo.grossPriceForPeriod_Specified(Index: Integer): boolean;
begin
  Result := FgrossPriceForPeriod_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetcommitTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcommitTimestamp := ATXSDateTime;
  FcommitTimestamp_Specified := True;
end;

function PWSTiPeriodicTicketInfo.commitTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FcommitTimestamp_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetperiodicCardId(Index: Integer; const APWSTiPeriodicCardIdentyfier: PWSTiPeriodicCardIdentyfier);
begin
  FperiodicCardId := APWSTiPeriodicCardIdentyfier;
  FperiodicCardId_Specified := True;
end;

function PWSTiPeriodicTicketInfo.periodicCardId_Specified(Index: Integer): boolean;
begin
  Result := FperiodicCardId_Specified;
end;

procedure PWSTiPeriodicTicketInfo.Setholder(Index: Integer; const Aholder: holder);
begin
  Fholder := Aholder;
  Fholder_Specified := True;
end;

function PWSTiPeriodicTicketInfo.holder_Specified(Index: Integer): boolean;
begin
  Result := Fholder_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetlinesInfo(Index: Integer; const AlinesInfo: linesInfo);
begin
  FlinesInfo := AlinesInfo;
  FlinesInfo_Specified := True;
end;

function PWSTiPeriodicTicketInfo.linesInfo_Specified(Index: Integer): boolean;
begin
  Result := FlinesInfo_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetverifyingCode(Index: Integer; const Astring: string);
begin
  FverifyingCode := Astring;
  FverifyingCode_Specified := True;
end;

function PWSTiPeriodicTicketInfo.verifyingCode_Specified(Index: Integer): boolean;
begin
  Result := FverifyingCode_Specified;
end;

procedure PWSTiPeriodicTicketInfo.Setdiscount(Index: Integer; const APWSTiDiscount: PWSTiDiscount);
begin
  Fdiscount := APWSTiDiscount;
  Fdiscount_Specified := True;
end;

function PWSTiPeriodicTicketInfo.discount_Specified(Index: Integer): boolean;
begin
  Result := Fdiscount_Specified;
end;

procedure PWSTiPeriodicTicketInfo.SetticketLoginCode(Index: Integer; const Astring: string);
begin
  FticketLoginCode := Astring;
  FticketLoginCode_Specified := True;
end;

function PWSTiPeriodicTicketInfo.ticketLoginCode_Specified(Index: Integer): boolean;
begin
  Result := FticketLoginCode_Specified;
end;

destructor section.Destroy;
begin
  SysUtils.FreeAndNil(Ftype_);
  SysUtils.FreeAndNil(Fcourse);
  inherited Destroy;
end;

procedure section.SetfromCode(Index: Integer; const AInt64: Int64);
begin
  FfromCode := AInt64;
  FfromCode_Specified := True;
end;

function section.fromCode_Specified(Index: Integer): boolean;
begin
  Result := FfromCode_Specified;
end;

procedure section.SetfromZone(Index: Integer; const ABoolean: Boolean);
begin
  FfromZone := ABoolean;
  FfromZone_Specified := True;
end;

function section.fromZone_Specified(Index: Integer): boolean;
begin
  Result := FfromZone_Specified;
end;

procedure section.SettoCode(Index: Integer; const AInt64: Int64);
begin
  FtoCode := AInt64;
  FtoCode_Specified := True;
end;

function section.toCode_Specified(Index: Integer): boolean;
begin
  Result := FtoCode_Specified;
end;

procedure section.SettoZone(Index: Integer; const ABoolean: Boolean);
begin
  FtoZone := ABoolean;
  FtoZone_Specified := True;
end;

function section.toZone_Specified(Index: Integer): boolean;
begin
  Result := FtoZone_Specified;
end;

procedure section.Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  Ftype_ := APWSEnumParam;
  Ftype__Specified := True;
end;

function section.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

procedure section.Setcourse(Index: Integer; const APWSTiBusCourse: PWSTiBusCourse);
begin
  Fcourse := APWSTiBusCourse;
  Fcourse_Specified := True;
end;

function section.course_Specified(Index: Integer): boolean;
begin
  Result := Fcourse_Specified;
end;

destructor PWSTiBusCourse.Destroy;
begin
  SysUtils.FreeAndNil(FwaznyOd);
  inherited Destroy;
end;

procedure PWSTiBusCourse.SetnrKursu(Index: Integer; const AInteger: Integer);
begin
  FnrKursu := AInteger;
  FnrKursu_Specified := True;
end;

function PWSTiBusCourse.nrKursu_Specified(Index: Integer): boolean;
begin
  Result := FnrKursu_Specified;
end;

procedure PWSTiBusCourse.SetkierTam(Index: Integer; const ABoolean: Boolean);
begin
  FkierTam := ABoolean;
  FkierTam_Specified := True;
end;

function PWSTiBusCourse.kierTam_Specified(Index: Integer): boolean;
begin
  Result := FkierTam_Specified;
end;

procedure PWSTiBusCourse.SetwaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FwaznyOd := ATXSDateTime;
  FwaznyOd_Specified := True;
end;

function PWSTiBusCourse.waznyOd_Specified(Index: Integer): boolean;
begin
  Result := FwaznyOd_Specified;
end;

procedure PWSTiBusCourse.SetinfNrf(Index: Integer; const AInteger: Integer);
begin
  FinfNrf := AInteger;
  FinfNrf_Specified := True;
end;

function PWSTiBusCourse.infNrf_Specified(Index: Integer): boolean;
begin
  Result := FinfNrf_Specified;
end;

procedure PWSTiBusCourse.Setwariant(Index: Integer; const Astring: string);
begin
  Fwariant := Astring;
  Fwariant_Specified := True;
end;

function PWSTiBusCourse.wariant_Specified(Index: Integer): boolean;
begin
  Result := Fwariant_Specified;
end;

procedure PWSTiBusCourse.SetrodzKom(Index: Integer; const Astring: string);
begin
  FrodzKom := Astring;
  FrodzKom_Specified := True;
end;

function PWSTiBusCourse.rodzKom_Specified(Index: Integer): boolean;
begin
  Result := FrodzKom_Specified;
end;

destructor PWSConnection.Destroy;
begin
  SysUtils.FreeAndNil(FvalidFromTimestamp);
  SysUtils.FreeAndNil(FvalidToTimestamp);
  SysUtils.FreeAndNil(Ftype_);
  inherited Destroy;
end;

procedure PWSConnection.SetvalidFromTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidFromTimestamp := ATXSDateTime;
  FvalidFromTimestamp_Specified := True;
end;

function PWSConnection.validFromTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FvalidFromTimestamp_Specified;
end;

procedure PWSConnection.SetvalidToTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidToTimestamp := ATXSDateTime;
  FvalidToTimestamp_Specified := True;
end;

function PWSConnection.validToTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FvalidToTimestamp_Specified;
end;

procedure PWSConnection.Settype_(Index: Integer; const Atype_2: type_2);
begin
  Ftype_ := Atype_2;
  Ftype__Specified := True;
end;

function PWSConnection.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

procedure PWSConnection.Setlegend(Index: Integer; const Astring: string);
begin
  Flegend := Astring;
  Flegend_Specified := True;
end;

function PWSConnection.legend_Specified(Index: Integer): boolean;
begin
  Result := Flegend_Specified;
end;

procedure type_2.Settype_(Index: Integer; const Atype_: type_);
begin
  Ftype_ := Atype_;
  Ftype__Specified := True;
end;

function type_2.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

procedure type_2.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function type_2.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure passenger.Setnumber(Index: Integer; const AInteger: Integer);
begin
  Fnumber := AInteger;
  Fnumber_Specified := True;
end;

function passenger.number_Specified(Index: Integer): boolean;
begin
  Result := Fnumber_Specified;
end;

procedure passenger.SetgroupName(Index: Integer; const Astring: string);
begin
  FgroupName := Astring;
  FgroupName_Specified := True;
end;

function passenger.groupName_Specified(Index: Integer): boolean;
begin
  Result := FgroupName_Specified;
end;

procedure PWSPasswordCredential.Setpassword(Index: Integer; const Astring: string);
begin
  Fpassword := Astring;
  Fpassword_Specified := True;
end;

function PWSPasswordCredential.password_Specified(Index: Integer): boolean;
begin
  Result := Fpassword_Specified;
end;

procedure PWSSessionIdPrincipal.SetsessionId(Index: Integer; const Astring: string);
begin
  FsessionId := Astring;
  FsessionId_Specified := True;
end;

function PWSSessionIdPrincipal.sessionId_Specified(Index: Integer): boolean;
begin
  Result := FsessionId_Specified;
end;

destructor PWSUserInfo.Destroy;
begin
  SysUtils.FreeAndNil(Fusername);
  SysUtils.FreeAndNil(Fpassword);
  SysUtils.FreeAndNil(FsessionId);
  inherited Destroy;
end;

procedure PWSUserInfo.Setusername(Index: Integer; const APWSNamePrincipal: PWSNamePrincipal);
begin
  Fusername := APWSNamePrincipal;
  Fusername_Specified := True;
end;

function PWSUserInfo.username_Specified(Index: Integer): boolean;
begin
  Result := Fusername_Specified;
end;

procedure PWSUserInfo.Setpassword(Index: Integer; const APWSPasswordCredential: PWSPasswordCredential);
begin
  Fpassword := APWSPasswordCredential;
  Fpassword_Specified := True;
end;

function PWSUserInfo.password_Specified(Index: Integer): boolean;
begin
  Result := Fpassword_Specified;
end;

procedure PWSUserInfo.SetsessionId(Index: Integer; const APWSSessionIdPrincipal: PWSSessionIdPrincipal);
begin
  FsessionId := APWSSessionIdPrincipal;
  FsessionId_Specified := True;
end;

function PWSUserInfo.sessionId_Specified(Index: Integer): boolean;
begin
  Result := FsessionId_Specified;
end;

procedure PWSUserInfo.Setversion(Index: Integer; const Aversion: version);
begin
  Fversion := Aversion;
  Fversion_Specified := True;
end;

function PWSUserInfo.version_Specified(Index: Integer): boolean;
begin
  Result := Fversion_Specified;
end;

destructor PWSStopInTime.Destroy;
begin
  SysUtils.FreeAndNil(Ftime);
  SysUtils.FreeAndNil(FarrivalTime);
  SysUtils.FreeAndNil(Fstop);
  inherited Destroy;
end;

procedure PWSStopInTime.Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Ftime := ATXSDateTime;
  Ftime_Specified := True;
end;

function PWSStopInTime.time_Specified(Index: Integer): boolean;
begin
  Result := Ftime_Specified;
end;

procedure PWSStopInTime.SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FarrivalTime := ATXSDateTime;
  FarrivalTime_Specified := True;
end;

function PWSStopInTime.arrivalTime_Specified(Index: Integer): boolean;
begin
  Result := FarrivalTime_Specified;
end;

procedure PWSStopInTime.Setprice(Index: Integer; const ASingle: Single);
begin
  Fprice := ASingle;
  Fprice_Specified := True;
end;

function PWSStopInTime.price_Specified(Index: Integer): boolean;
begin
  Result := Fprice_Specified;
end;

procedure PWSStopInTime.Setstop(Index: Integer; const APWSStop: PWSStop);
begin
  Fstop := APWSStop;
  Fstop_Specified := True;
end;

function PWSStopInTime.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

procedure param.SetfromRouteId(Index: Integer; const AInt64: Int64);
begin
  FfromRouteId := AInt64;
  FfromRouteId_Specified := True;
end;

function param.fromRouteId_Specified(Index: Integer): boolean;
begin
  Result := FfromRouteId_Specified;
end;

procedure param.SettoRouteId(Index: Integer; const AInt64: Int64);
begin
  FtoRouteId := AInt64;
  FtoRouteId_Specified := True;
end;

function param.toRouteId_Specified(Index: Integer): boolean;
begin
  Result := FtoRouteId_Specified;
end;

destructor PWSFullyQualifiedCityExt.Destroy;
begin
  SysUtils.FreeAndNil(Ffqc);
  inherited Destroy;
end;

procedure PWSFullyQualifiedCityExt.SetstopsCount(Index: Integer; const AInt64: Int64);
begin
  FstopsCount := AInt64;
  FstopsCount_Specified := True;
end;

function PWSFullyQualifiedCityExt.stopsCount_Specified(Index: Integer): boolean;
begin
  Result := FstopsCount_Specified;
end;

procedure PWSFullyQualifiedCityExt.Setlatitude(Index: Integer; const ASingle: Single);
begin
  Flatitude := ASingle;
  Flatitude_Specified := True;
end;

function PWSFullyQualifiedCityExt.latitude_Specified(Index: Integer): boolean;
begin
  Result := Flatitude_Specified;
end;

procedure PWSFullyQualifiedCityExt.Setlongitude(Index: Integer; const ASingle: Single);
begin
  Flongitude := ASingle;
  Flongitude_Specified := True;
end;

function PWSFullyQualifiedCityExt.longitude_Specified(Index: Integer): boolean;
begin
  Result := Flongitude_Specified;
end;

procedure PWSFullyQualifiedCityExt.Setaltitude(Index: Integer; const ASingle: Single);
begin
  Faltitude := ASingle;
  Faltitude_Specified := True;
end;

function PWSFullyQualifiedCityExt.altitude_Specified(Index: Integer): boolean;
begin
  Result := Faltitude_Specified;
end;

procedure PWSFullyQualifiedCityExt.Setfqc(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  Ffqc := APWSFullyQualifiedCity;
  Ffqc_Specified := True;
end;

function PWSFullyQualifiedCityExt.fqc_Specified(Index: Integer): boolean;
begin
  Result := Ffqc_Specified;
end;

procedure PWSFullyQualifiedCityExt.SetsettlementType(Index: Integer; const Astring: string);
begin
  FsettlementType := Astring;
  FsettlementType_Specified := True;
end;

function PWSFullyQualifiedCityExt.settlementType_Specified(Index: Integer): boolean;
begin
  Result := FsettlementType_Specified;
end;

destructor PWSVehiclePosition.Destroy;
begin
  SysUtils.FreeAndNil(Fvehicle);
  SysUtils.FreeAndNil(Fposition);
  inherited Destroy;
end;

procedure PWSVehiclePosition.Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
begin
  Fvehicle := APWSVehicle;
  Fvehicle_Specified := True;
end;

function PWSVehiclePosition.vehicle_Specified(Index: Integer): boolean;
begin
  Result := Fvehicle_Specified;
end;

procedure PWSVehiclePosition.Setposition(Index: Integer; const APWSWaypoint: PWSWaypoint);
begin
  Fposition := APWSWaypoint;
  Fposition_Specified := True;
end;

function PWSVehiclePosition.position_Specified(Index: Integer): boolean;
begin
  Result := Fposition_Specified;
end;

procedure PWSVehicle.SetvehicleNumber(Index: Integer; const Astring: string);
begin
  FvehicleNumber := Astring;
  FvehicleNumber_Specified := True;
end;

function PWSVehicle.vehicleNumber_Specified(Index: Integer): boolean;
begin
  Result := FvehicleNumber_Specified;
end;

procedure PWSTiReservationId.Setid(Index: Integer; const AInt64: Int64);
begin
  Fid := AInt64;
  Fid_Specified := True;
end;

function PWSTiReservationId.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

destructor PWSTiVendingParams.Destroy;
begin
  SysUtils.FreeAndNil(FtraceModifyTimestamp);
  SysUtils.FreeAndNil(Fcarriers);
  inherited Destroy;
end;

procedure PWSTiVendingParams.SetvendingMachineId(Index: Integer; const AInt64: Int64);
begin
  FvendingMachineId := AInt64;
  FvendingMachineId_Specified := True;
end;

function PWSTiVendingParams.vendingMachineId_Specified(Index: Integer): boolean;
begin
  Result := FvendingMachineId_Specified;
end;

procedure PWSTiVendingParams.SetsystemUserId(Index: Integer; const AInt64: Int64);
begin
  FsystemUserId := AInt64;
  FsystemUserId_Specified := True;
end;

function PWSTiVendingParams.systemUserId_Specified(Index: Integer): boolean;
begin
  Result := FsystemUserId_Specified;
end;

procedure PWSTiVendingParams.SetfromStopId(Index: Integer; const AInt64: Int64);
begin
  FfromStopId := AInt64;
  FfromStopId_Specified := True;
end;

function PWSTiVendingParams.fromStopId_Specified(Index: Integer): boolean;
begin
  Result := FfromStopId_Specified;
end;

procedure PWSTiVendingParams.SetlockedFromStopEditing(Index: Integer; const ABoolean: Boolean);
begin
  FlockedFromStopEditing := ABoolean;
  FlockedFromStopEditing_Specified := True;
end;

function PWSTiVendingParams.lockedFromStopEditing_Specified(Index: Integer): boolean;
begin
  Result := FlockedFromStopEditing_Specified;
end;

procedure PWSTiVendingParams.SetlockedMachine(Index: Integer; const ABoolean: Boolean);
begin
  FlockedMachine := ABoolean;
  FlockedMachine_Specified := True;
end;

function PWSTiVendingParams.lockedMachine_Specified(Index: Integer): boolean;
begin
  Result := FlockedMachine_Specified;
end;

procedure PWSTiVendingParams.SetlockedCardPayment(Index: Integer; const ABoolean: Boolean);
begin
  FlockedCardPayment := ABoolean;
  FlockedCardPayment_Specified := True;
end;

function PWSTiVendingParams.lockedCardPayment_Specified(Index: Integer): boolean;
begin
  Result := FlockedCardPayment_Specified;
end;

procedure PWSTiVendingParams.SetlockedCashPayment(Index: Integer; const ABoolean: Boolean);
begin
  FlockedCashPayment := ABoolean;
  FlockedCashPayment_Specified := True;
end;

function PWSTiVendingParams.lockedCashPayment_Specified(Index: Integer): boolean;
begin
  Result := FlockedCashPayment_Specified;
end;

procedure PWSTiVendingParams.SetlockedTicketManagement(Index: Integer; const ABoolean: Boolean);
begin
  FlockedTicketManagement := ABoolean;
  FlockedTicketManagement_Specified := True;
end;

function PWSTiVendingParams.lockedTicketManagement_Specified(Index: Integer): boolean;
begin
  Result := FlockedTicketManagement_Specified;
end;

procedure PWSTiVendingParams.SetlockedPerTicketSelling(Index: Integer; const ABoolean: Boolean);
begin
  FlockedPerTicketSelling := ABoolean;
  FlockedPerTicketSelling_Specified := True;
end;

function PWSTiVendingParams.lockedPerTicketSelling_Specified(Index: Integer): boolean;
begin
  Result := FlockedPerTicketSelling_Specified;
end;

procedure PWSTiVendingParams.SetlockedNorTicketSelling(Index: Integer; const ABoolean: Boolean);
begin
  FlockedNorTicketSelling := ABoolean;
  FlockedNorTicketSelling_Specified := True;
end;

function PWSTiVendingParams.lockedNorTicketSelling_Specified(Index: Integer): boolean;
begin
  Result := FlockedNorTicketSelling_Specified;
end;

procedure PWSTiVendingParams.SetlockedResultsWithChange(Index: Integer; const ABoolean: Boolean);
begin
  FlockedResultsWithChange := ABoolean;
  FlockedResultsWithChange_Specified := True;
end;

function PWSTiVendingParams.lockedResultsWithChange_Specified(Index: Integer): boolean;
begin
  Result := FlockedResultsWithChange_Specified;
end;

procedure PWSTiVendingParams.SetlockedResultsWithoutSelling(Index: Integer; const ABoolean: Boolean);
begin
  FlockedResultsWithoutSelling := ABoolean;
  FlockedResultsWithoutSelling_Specified := True;
end;

function PWSTiVendingParams.lockedResultsWithoutSelling_Specified(Index: Integer): boolean;
begin
  Result := FlockedResultsWithoutSelling_Specified;
end;

procedure PWSTiVendingParams.SettraceModifyTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtraceModifyTimestamp := ATXSDateTime;
  FtraceModifyTimestamp_Specified := True;
end;

function PWSTiVendingParams.traceModifyTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FtraceModifyTimestamp_Specified;
end;

procedure PWSTiVendingParams.SetowningDistributorId(Index: Integer; const AInt64: Int64);
begin
  FowningDistributorId := AInt64;
  FowningDistributorId_Specified := True;
end;

function PWSTiVendingParams.owningDistributorId_Specified(Index: Integer): boolean;
begin
  Result := FowningDistributorId_Specified;
end;

procedure PWSTiVendingParams.SetincludeNotSalesConnections(Index: Integer; const ABoolean: Boolean);
begin
  FincludeNotSalesConnections := ABoolean;
  FincludeNotSalesConnections_Specified := True;
end;

function PWSTiVendingParams.includeNotSalesConnections_Specified(Index: Integer): boolean;
begin
  Result := FincludeNotSalesConnections_Specified;
end;

procedure PWSTiVendingParams.Setcarriers(Index: Integer; const Acarriers: carriers);
begin
  Fcarriers := Acarriers;
  Fcarriers_Specified := True;
end;

function PWSTiVendingParams.carriers_Specified(Index: Integer): boolean;
begin
  Result := Fcarriers_Specified;
end;

destructor PWSStick.Destroy;
begin
  SysUtils.FreeAndNil(Fconnection);
  SysUtils.FreeAndNil(Fcarrier);
  SysUtils.FreeAndNil(FsourceStop);
  SysUtils.FreeAndNil(FtargetStop);
  inherited Destroy;
end;

procedure PWSStick.Setconnection(Index: Integer; const APWSConnection: PWSConnection);
begin
  Fconnection := APWSConnection;
  Fconnection_Specified := True;
end;

function PWSStick.connection_Specified(Index: Integer): boolean;
begin
  Result := Fconnection_Specified;
end;

procedure PWSStick.Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
begin
  Fcarrier := APWSCarrier;
  Fcarrier_Specified := True;
end;

function PWSStick.carrier_Specified(Index: Integer): boolean;
begin
  Result := Fcarrier_Specified;
end;

procedure PWSStick.SetsourceStop(Index: Integer; const APWSStopInTime: PWSStopInTime);
begin
  FsourceStop := APWSStopInTime;
  FsourceStop_Specified := True;
end;

function PWSStick.sourceStop_Specified(Index: Integer): boolean;
begin
  Result := FsourceStop_Specified;
end;

procedure PWSStick.SettargetStop(Index: Integer; const APWSStopInTime: PWSStopInTime);
begin
  FtargetStop := APWSStopInTime;
  FtargetStop_Specified := True;
end;

function PWSStick.targetStop_Specified(Index: Integer): boolean;
begin
  Result := FtargetStop_Specified;
end;

procedure stickId.SetfromRouteId(Index: Integer; const AInt64: Int64);
begin
  FfromRouteId := AInt64;
  FfromRouteId_Specified := True;
end;

function stickId.fromRouteId_Specified(Index: Integer): boolean;
begin
  Result := FfromRouteId_Specified;
end;

procedure stickId.SettoRouteId(Index: Integer; const AInt64: Int64);
begin
  FtoRouteId := AInt64;
  FtoRouteId_Specified := True;
end;

function stickId.toRouteId_Specified(Index: Integer): boolean;
begin
  Result := FtoRouteId_Specified;
end;

procedure PWSChangeUserDataParams.Setlogin(Index: Integer; const Astring: string);
begin
  Flogin := Astring;
  Flogin_Specified := True;
end;

function PWSChangeUserDataParams.login_Specified(Index: Integer): boolean;
begin
  Result := Flogin_Specified;
end;

procedure PWSChangeUserDataParams.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PWSChangeUserDataParams.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PWSChangeUserDataParams.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PWSChangeUserDataParams.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PWSChangeUserDataParams.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function PWSChangeUserDataParams.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure PWSChangeUserDataParams.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function PWSChangeUserDataParams.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

destructor PWSRelation.Destroy;
begin
  SysUtils.FreeAndNil(FsourceStop);
  SysUtils.FreeAndNil(FtargetStop);
  inherited Destroy;
end;

procedure PWSRelation.SetsourceStop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
begin
  FsourceStop := APWSFullyQualifiedStop;
  FsourceStop_Specified := True;
end;

function PWSRelation.sourceStop_Specified(Index: Integer): boolean;
begin
  Result := FsourceStop_Specified;
end;

procedure PWSRelation.SettargetStop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
begin
  FtargetStop := APWSFullyQualifiedStop;
  FtargetStop_Specified := True;
end;

function PWSRelation.targetStop_Specified(Index: Integer): boolean;
begin
  Result := FtargetStop_Specified;
end;

destructor price.Destroy;
begin
  SysUtils.FreeAndNil(Fcountry);
  inherited Destroy;
end;

procedure price.SetgrossPrice(Index: Integer; const ASingle: Single);
begin
  FgrossPrice := ASingle;
  FgrossPrice_Specified := True;
end;

function price.grossPrice_Specified(Index: Integer): boolean;
begin
  Result := FgrossPrice_Specified;
end;

procedure price.SetvatRate(Index: Integer; const ASingle: Single);
begin
  FvatRate := ASingle;
  FvatRate_Specified := True;
end;

function price.vatRate_Specified(Index: Integer): boolean;
begin
  Result := FvatRate_Specified;
end;

procedure price.SetvatValue(Index: Integer; const ASingle: Single);
begin
  FvatValue := ASingle;
  FvatValue_Specified := True;
end;

function price.vatValue_Specified(Index: Integer): boolean;
begin
  Result := FvatValue_Specified;
end;

procedure price.Setcountry(Index: Integer; const Acountry: country);
begin
  Fcountry := Acountry;
  Fcountry_Specified := True;
end;

function price.country_Specified(Index: Integer): boolean;
begin
  Result := Fcountry_Specified;
end;

procedure country.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function country.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure country.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function country.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure PTiHolderForTicket.SetidentifyingDocValue(Index: Integer; const Astring: string);
begin
  FidentifyingDocValue := Astring;
  FidentifyingDocValue_Specified := True;
end;

function PTiHolderForTicket.identifyingDocValue_Specified(Index: Integer): boolean;
begin
  Result := FidentifyingDocValue_Specified;
end;

procedure PTiHolderForTicket.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PTiHolderForTicket.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PTiHolderForTicket.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PTiHolderForTicket.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PTiHolderForTicket.SetdocType(Index: Integer; const AdocType: docType);
begin
  FdocType := AdocType;
  FdocType_Specified := True;
end;

function PTiHolderForTicket.docType_Specified(Index: Integer): boolean;
begin
  Result := FdocType_Specified;
end;

procedure PTiHolderForTicket.SetcontactPhone(Index: Integer; const Astring: string);
begin
  FcontactPhone := Astring;
  FcontactPhone_Specified := True;
end;

function PTiHolderForTicket.contactPhone_Specified(Index: Integer): boolean;
begin
  Result := FcontactPhone_Specified;
end;

procedure role.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function role.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSTiReservationCancelInfo.SetbankAccountNumber(Index: Integer; const Astring: string);
begin
  FbankAccountNumber := Astring;
  FbankAccountNumber_Specified := True;
end;

function PWSTiReservationCancelInfo.bankAccountNumber_Specified(Index: Integer): boolean;
begin
  Result := FbankAccountNumber_Specified;
end;

procedure discount.SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
begin
  FvalueAfterDiscount := ASingle;
  FvalueAfterDiscount_Specified := True;
end;

function discount.valueAfterDiscount_Specified(Index: Integer): boolean;
begin
  Result := FvalueAfterDiscount_Specified;
end;

procedure discount.SetdiscountValue(Index: Integer; const ASingle: Single);
begin
  FdiscountValue := ASingle;
  FdiscountValue_Specified := True;
end;

function discount.discountValue_Specified(Index: Integer): boolean;
begin
  Result := FdiscountValue_Specified;
end;

procedure discount.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function discount.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure discount.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function discount.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure discount.Setdescription(Index: Integer; const Astring: string);
begin
  Fdescription := Astring;
  Fdescription_Specified := True;
end;

function discount.description_Specified(Index: Integer): boolean;
begin
  Result := Fdescription_Specified;
end;

destructor PWSWebServiceUser.Destroy;
begin
  SysUtils.FreeAndNil(FvalidFrom);
  SysUtils.FreeAndNil(FvalidTo);
  inherited Destroy;
end;

procedure PWSWebServiceUser.Setblocked(Index: Integer; const ABoolean: Boolean);
begin
  Fblocked := ABoolean;
  Fblocked_Specified := True;
end;

function PWSWebServiceUser.blocked_Specified(Index: Integer): boolean;
begin
  Result := Fblocked_Specified;
end;

procedure PWSWebServiceUser.SetvalidFrom(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidFrom := ATXSDateTime;
  FvalidFrom_Specified := True;
end;

function PWSWebServiceUser.validFrom_Specified(Index: Integer): boolean;
begin
  Result := FvalidFrom_Specified;
end;

procedure PWSWebServiceUser.SetvalidTo(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvalidTo := ATXSDateTime;
  FvalidTo_Specified := True;
end;

function PWSWebServiceUser.validTo_Specified(Index: Integer): boolean;
begin
  Result := FvalidTo_Specified;
end;

procedure PWSWebServiceUser.SetsystemUserId(Index: Integer; const AInt64: Int64);
begin
  FsystemUserId := AInt64;
  FsystemUserId_Specified := True;
end;

function PWSWebServiceUser.systemUserId_Specified(Index: Integer): boolean;
begin
  Result := FsystemUserId_Specified;
end;

procedure PWSWebServiceUser.Setlogin(Index: Integer; const Astring: string);
begin
  Flogin := Astring;
  Flogin_Specified := True;
end;

function PWSWebServiceUser.login_Specified(Index: Integer): boolean;
begin
  Result := Flogin_Specified;
end;

procedure PWSWebServiceUser.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PWSWebServiceUser.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PWSWebServiceUser.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PWSWebServiceUser.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PWSWebServiceUser.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function PWSWebServiceUser.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure PWSWebServiceUser.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function PWSWebServiceUser.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

destructor PWSTiReservationDone.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FPWSTiPeriodicTicketInfo)-1 do
    SysUtils.FreeAndNil(FPWSTiPeriodicTicketInfo[I]);
  System.SetLength(FPWSTiPeriodicTicketInfo, 0);
  SysUtils.FreeAndNil(Fid);
  inherited Destroy;
end;

procedure PWSTiReservationDone.Setid(Index: Integer; const APWSTiReservationId: PWSTiReservationId);
begin
  Fid := APWSTiReservationId;
  Fid_Specified := True;
end;

function PWSTiReservationDone.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

procedure PWSTiReservationDone.SetPWSTiPeriodicTicketInfo(Index: Integer; const APWSTiPeriodicTickets: PWSTiPeriodicTickets);
begin
  FPWSTiPeriodicTicketInfo := APWSTiPeriodicTickets;
  FPWSTiPeriodicTicketInfo_Specified := True;
end;

function PWSTiReservationDone.PWSTiPeriodicTicketInfo_Specified(Index: Integer): boolean;
begin
  Result := FPWSTiPeriodicTicketInfo_Specified;
end;

procedure PWSRelationParams.SetconnectionId(Index: Integer; const AInt64: Int64);
begin
  FconnectionId := AInt64;
  FconnectionId_Specified := True;
end;

function PWSRelationParams.connectionId_Specified(Index: Integer): boolean;
begin
  Result := FconnectionId_Specified;
end;

destructor PWSCarrierDetails.Destroy;
begin
  SysUtils.FreeAndNil(Fcarrier);
  SysUtils.FreeAndNil(Fcard);
  inherited Destroy;
end;

procedure PWSCarrierDetails.Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
begin
  Fcarrier := APWSCarrier;
  Fcarrier_Specified := True;
end;

function PWSCarrierDetails.carrier_Specified(Index: Integer): boolean;
begin
  Result := Fcarrier_Specified;
end;

procedure PWSCarrierDetails.Setcard(Index: Integer; const Acard: card);
begin
  Fcard := Acard;
  Fcard_Specified := True;
end;

function PWSCarrierDetails.card_Specified(Index: Integer): boolean;
begin
  Result := Fcard_Specified;
end;

destructor PWSCarrier.Destroy;
begin
  SysUtils.FreeAndNil(FcarrierType);
  inherited Destroy;
end;

procedure PWSCarrier.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSCarrier.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSCarrier.SetcarrierType(Index: Integer; const AcarrierType2: carrierType2);
begin
  FcarrierType := AcarrierType2;
  FcarrierType_Specified := True;
end;

function PWSCarrier.carrierType_Specified(Index: Integer): boolean;
begin
  Result := FcarrierType_Specified;
end;

destructor card.Destroy;
begin
  SysUtils.FreeAndNil(Faddress);
  inherited Destroy;
end;

procedure card.Setaddress(Index: Integer; const Aaddress: address);
begin
  Faddress := Aaddress;
  Faddress_Specified := True;
end;

function card.address_Specified(Index: Integer): boolean;
begin
  Result := Faddress_Specified;
end;

procedure card.SetcarrierName(Index: Integer; const Astring: string);
begin
  FcarrierName := Astring;
  FcarrierName_Specified := True;
end;

function card.carrierName_Specified(Index: Integer): boolean;
begin
  Result := FcarrierName_Specified;
end;

procedure card.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function card.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

procedure card.Setfax(Index: Integer; const Astring: string);
begin
  Ffax := Astring;
  Ffax_Specified := True;
end;

function card.fax_Specified(Index: Integer): boolean;
begin
  Result := Ffax_Specified;
end;

procedure card.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function card.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure card.Setwww(Index: Integer; const Astring: string);
begin
  Fwww := Astring;
  Fwww_Specified := True;
end;

function card.www_Specified(Index: Integer): boolean;
begin
  Result := Fwww_Specified;
end;

procedure card.SetcompanyDescription(Index: Integer; const Astring: string);
begin
  FcompanyDescription := Astring;
  FcompanyDescription_Specified := True;
end;

function card.companyDescription_Specified(Index: Integer): boolean;
begin
  Result := FcompanyDescription_Specified;
end;

procedure address.SetbuildingNumber(Index: Integer; const Astring: string);
begin
  FbuildingNumber := Astring;
  FbuildingNumber_Specified := True;
end;

function address.buildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FbuildingNumber_Specified;
end;

procedure address.SetlocalNumber(Index: Integer; const Astring: string);
begin
  FlocalNumber := Astring;
  FlocalNumber_Specified := True;
end;

function address.localNumber_Specified(Index: Integer): boolean;
begin
  Result := FlocalNumber_Specified;
end;

procedure address.SetpostalCode(Index: Integer; const Astring: string);
begin
  FpostalCode := Astring;
  FpostalCode_Specified := True;
end;

function address.postalCode_Specified(Index: Integer): boolean;
begin
  Result := FpostalCode_Specified;
end;

procedure address.Setstreet(Index: Integer; const Astring: string);
begin
  Fstreet := Astring;
  Fstreet_Specified := True;
end;

function address.street_Specified(Index: Integer): boolean;
begin
  Result := Fstreet_Specified;
end;

procedure address.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function address.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

destructor PWSTiSendTicketInfo.Destroy;
begin
  SysUtils.FreeAndNil(FsendingData);
  inherited Destroy;
end;

procedure PWSTiSendTicketInfo.SetsendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
begin
  FsendingData := APWSTiSendingData;
  FsendingData_Specified := True;
end;

function PWSTiSendTicketInfo.sendingData_Specified(Index: Integer): boolean;
begin
  Result := FsendingData_Specified;
end;

procedure PWSTiSendTicketInfo.SetsendingCode(Index: Integer; const Astring: string);
begin
  FsendingCode := Astring;
  FsendingCode_Specified := True;
end;

function PWSTiSendTicketInfo.sendingCode_Specified(Index: Integer): boolean;
begin
  Result := FsendingCode_Specified;
end;

destructor relation.Destroy;
begin
  SysUtils.FreeAndNil(FfirstCity);
  SysUtils.FreeAndNil(FlastCity);
  inherited Destroy;
end;

procedure relation.SetfirstStopId(Index: Integer; const AInt64: Int64);
begin
  FfirstStopId := AInt64;
  FfirstStopId_Specified := True;
end;

function relation.firstStopId_Specified(Index: Integer): boolean;
begin
  Result := FfirstStopId_Specified;
end;

procedure relation.SetlastStopId(Index: Integer; const AInt64: Int64);
begin
  FlastStopId := AInt64;
  FlastStopId_Specified := True;
end;

function relation.lastStopId_Specified(Index: Integer): boolean;
begin
  Result := FlastStopId_Specified;
end;

procedure relation.SetfirstCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FfirstCity := APWSFullyQualifiedCity;
  FfirstCity_Specified := True;
end;

function relation.firstCity_Specified(Index: Integer): boolean;
begin
  Result := FfirstCity_Specified;
end;

procedure relation.SetlastCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FlastCity := APWSFullyQualifiedCity;
  FlastCity_Specified := True;
end;

function relation.lastCity_Specified(Index: Integer): boolean;
begin
  Result := FlastCity_Specified;
end;

destructor PWSStopInTimeForTimeTable.Destroy;
begin
  SysUtils.FreeAndNil(Ftime);
  SysUtils.FreeAndNil(FarrivalTime);
  SysUtils.FreeAndNil(Fconnection);
  SysUtils.FreeAndNil(Fcarrier);
  SysUtils.FreeAndNil(Fstop);
  inherited Destroy;
end;

procedure PWSStopInTimeForTimeTable.Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Ftime := ATXSDateTime;
  Ftime_Specified := True;
end;

function PWSStopInTimeForTimeTable.time_Specified(Index: Integer): boolean;
begin
  Result := Ftime_Specified;
end;

procedure PWSStopInTimeForTimeTable.SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FarrivalTime := ATXSDateTime;
  FarrivalTime_Specified := True;
end;

function PWSStopInTimeForTimeTable.arrivalTime_Specified(Index: Integer): boolean;
begin
  Result := FarrivalTime_Specified;
end;

procedure PWSStopInTimeForTimeTable.Setprice(Index: Integer; const ASingle: Single);
begin
  Fprice := ASingle;
  Fprice_Specified := True;
end;

function PWSStopInTimeForTimeTable.price_Specified(Index: Integer): boolean;
begin
  Result := Fprice_Specified;
end;

procedure PWSStopInTimeForTimeTable.Setconnection(Index: Integer; const APWSConnection: PWSConnection);
begin
  Fconnection := APWSConnection;
  Fconnection_Specified := True;
end;

function PWSStopInTimeForTimeTable.connection_Specified(Index: Integer): boolean;
begin
  Result := Fconnection_Specified;
end;

procedure PWSStopInTimeForTimeTable.Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
begin
  Fcarrier := APWSCarrier;
  Fcarrier_Specified := True;
end;

function PWSStopInTimeForTimeTable.carrier_Specified(Index: Integer): boolean;
begin
  Result := Fcarrier_Specified;
end;

procedure PWSStopInTimeForTimeTable.Setstop(Index: Integer; const APWSStop: PWSStop);
begin
  Fstop := APWSStop;
  Fstop_Specified := True;
end;

function PWSStopInTimeForTimeTable.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

destructor price2.Destroy;
begin
  SysUtils.FreeAndNil(Fcountry);
  inherited Destroy;
end;

procedure price2.SetgrossPrice(Index: Integer; const ASingle: Single);
begin
  FgrossPrice := ASingle;
  FgrossPrice_Specified := True;
end;

function price2.grossPrice_Specified(Index: Integer): boolean;
begin
  Result := FgrossPrice_Specified;
end;

procedure price2.SetvatRate(Index: Integer; const ASingle: Single);
begin
  FvatRate := ASingle;
  FvatRate_Specified := True;
end;

function price2.vatRate_Specified(Index: Integer): boolean;
begin
  Result := FvatRate_Specified;
end;

procedure price2.Setcountry(Index: Integer; const Acountry2: country2);
begin
  Fcountry := Acountry2;
  Fcountry_Specified := True;
end;

function price2.country_Specified(Index: Integer): boolean;
begin
  Result := Fcountry_Specified;
end;

procedure country2.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function country2.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure country2.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function country2.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure PWSTiSendTicketFormat.SetpathToJasperFormatFile(Index: Integer; const Astring: string);
begin
  FpathToJasperFormatFile := Astring;
  FpathToJasperFormatFile_Specified := True;
end;

function PWSTiSendTicketFormat.pathToJasperFormatFile_Specified(Index: Integer): boolean;
begin
  Result := FpathToJasperFormatFile_Specified;
end;

procedure PWSTiSendTicketFormat.SetpathToLogoImage(Index: Integer; const Astring: string);
begin
  FpathToLogoImage := Astring;
  FpathToLogoImage_Specified := True;
end;

function PWSTiSendTicketFormat.pathToLogoImage_Specified(Index: Integer): boolean;
begin
  Result := FpathToLogoImage_Specified;
end;

destructor opinion.Destroy;
begin
  SysUtils.FreeAndNil(FaddingDateTime);
  inherited Destroy;
end;

procedure opinion.SetaddingDateTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FaddingDateTime := ATXSDateTime;
  FaddingDateTime_Specified := True;
end;

function opinion.addingDateTime_Specified(Index: Integer): boolean;
begin
  Result := FaddingDateTime_Specified;
end;

procedure opinion.SetopinionText(Index: Integer; const Astring: string);
begin
  FopinionText := Astring;
  FopinionText_Specified := True;
end;

function opinion.opinionText_Specified(Index: Integer): boolean;
begin
  Result := FopinionText_Specified;
end;

procedure opinion.SetipAddress(Index: Integer; const Astring: string);
begin
  FipAddress := Astring;
  FipAddress_Specified := True;
end;

function opinion.ipAddress_Specified(Index: Integer): boolean;
begin
  Result := FipAddress_Specified;
end;

procedure opinion.Setnickname(Index: Integer; const Astring: string);
begin
  Fnickname := Astring;
  Fnickname_Specified := True;
end;

function opinion.nickname_Specified(Index: Integer): boolean;
begin
  Result := Fnickname_Specified;
end;

destructor PWSWaypoint.Destroy;
begin
  SysUtils.FreeAndNil(FtimeOfRecording);
  SysUtils.FreeAndNil(FLRPTime);
  inherited Destroy;
end;

procedure PWSWaypoint.Setlatitude(Index: Integer; const ADouble: Double);
begin
  Flatitude := ADouble;
  Flatitude_Specified := True;
end;

function PWSWaypoint.latitude_Specified(Index: Integer): boolean;
begin
  Result := Flatitude_Specified;
end;

procedure PWSWaypoint.Setlongitude(Index: Integer; const ADouble: Double);
begin
  Flongitude := ADouble;
  Flongitude_Specified := True;
end;

function PWSWaypoint.longitude_Specified(Index: Integer): boolean;
begin
  Result := Flongitude_Specified;
end;

procedure PWSWaypoint.SettimeOfRecording(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FtimeOfRecording := ATXSDateTime;
  FtimeOfRecording_Specified := True;
end;

function PWSWaypoint.timeOfRecording_Specified(Index: Integer): boolean;
begin
  Result := FtimeOfRecording_Specified;
end;

procedure PWSWaypoint.Setstatus(Index: Integer; const AInteger: Integer);
begin
  Fstatus := AInteger;
  Fstatus_Specified := True;
end;

function PWSWaypoint.status_Specified(Index: Integer): boolean;
begin
  Result := Fstatus_Specified;
end;

procedure PWSWaypoint.SetroadPointNumber(Index: Integer; const AInteger: Integer);
begin
  FroadPointNumber := AInteger;
  FroadPointNumber_Specified := True;
end;

function PWSWaypoint.roadPointNumber_Specified(Index: Integer): boolean;
begin
  Result := FroadPointNumber_Specified;
end;

procedure PWSWaypoint.SetlastRoadPointNo(Index: Integer; const AInteger: Integer);
begin
  FlastRoadPointNo := AInteger;
  FlastRoadPointNo_Specified := True;
end;

function PWSWaypoint.lastRoadPointNo_Specified(Index: Integer): boolean;
begin
  Result := FlastRoadPointNo_Specified;
end;

procedure PWSWaypoint.SetLRPTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FLRPTime := ATXSDateTime;
  FLRPTime_Specified := True;
end;

function PWSWaypoint.LRPTime_Specified(Index: Integer): boolean;
begin
  Result := FLRPTime_Specified;
end;

procedure driver.Setforname(Index: Integer; const Astring: string);
begin
  Fforname := Astring;
  Fforname_Specified := True;
end;

function driver.forname_Specified(Index: Integer): boolean;
begin
  Result := Fforname_Specified;
end;

procedure driver.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function driver.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure driver.SetdriverId(Index: Integer; const Astring: string);
begin
  FdriverId := Astring;
  FdriverId_Specified := True;
end;

function driver.driverId_Specified(Index: Integer): boolean;
begin
  Result := FdriverId_Specified;
end;

destructor reservation.Destroy;
begin
  SysUtils.FreeAndNil(FreservationDate);
  SysUtils.FreeAndNil(FrollbackDate);
  SysUtils.FreeAndNil(FcommitDate);
  SysUtils.FreeAndNil(FpaymentDate);
  SysUtils.FreeAndNil(Fid);
  inherited Destroy;
end;

procedure reservation.SetreservationDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FreservationDate := ATXSDateTime;
  FreservationDate_Specified := True;
end;

function reservation.reservationDate_Specified(Index: Integer): boolean;
begin
  Result := FreservationDate_Specified;
end;

procedure reservation.SetrollbackDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FrollbackDate := ATXSDateTime;
  FrollbackDate_Specified := True;
end;

function reservation.rollbackDate_Specified(Index: Integer): boolean;
begin
  Result := FrollbackDate_Specified;
end;

procedure reservation.SetcommitDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcommitDate := ATXSDateTime;
  FcommitDate_Specified := True;
end;

function reservation.commitDate_Specified(Index: Integer): boolean;
begin
  Result := FcommitDate_Specified;
end;

procedure reservation.SetpaymentDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FpaymentDate := ATXSDateTime;
  FpaymentDate_Specified := True;
end;

function reservation.paymentDate_Specified(Index: Integer): boolean;
begin
  Result := FpaymentDate_Specified;
end;

procedure reservation.SetsmsSendCount(Index: Integer; const AInteger: Integer);
begin
  FsmsSendCount := AInteger;
  FsmsSendCount_Specified := True;
end;

function reservation.smsSendCount_Specified(Index: Integer): boolean;
begin
  Result := FsmsSendCount_Specified;
end;

procedure reservation.Setid(Index: Integer; const APWSTiReservationId: PWSTiReservationId);
begin
  Fid := APWSTiReservationId;
  Fid_Specified := True;
end;

function reservation.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

procedure reservation.Setnip(Index: Integer; const Astring: string);
begin
  Fnip := Astring;
  Fnip_Specified := True;
end;

function reservation.nip_Specified(Index: Integer): boolean;
begin
  Result := Fnip_Specified;
end;

destructor payer.Destroy;
begin
  SysUtils.FreeAndNil(FdefaultSendingType);
  SysUtils.FreeAndNil(FdocType);
  inherited Destroy;
end;

procedure payer.Setid(Index: Integer; const AInt64: Int64);
begin
  Fid := AInt64;
  Fid_Specified := True;
end;

function payer.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

procedure payer.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function payer.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure payer.SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
begin
  FdefaultPeriodicCardId := AInt64;
  FdefaultPeriodicCardId_Specified := True;
end;

function payer.defaultPeriodicCardId_Specified(Index: Integer): boolean;
begin
  Result := FdefaultPeriodicCardId_Specified;
end;

procedure payer.SetcompanyCityId(Index: Integer; const AInt64: Int64);
begin
  FcompanyCityId := AInt64;
  FcompanyCityId_Specified := True;
end;

function payer.companyCityId_Specified(Index: Integer): boolean;
begin
  Result := FcompanyCityId_Specified;
end;

procedure payer.SetdefaultSendingType(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  FdefaultSendingType := APWSEnumParam;
  FdefaultSendingType_Specified := True;
end;

function payer.defaultSendingType_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingType_Specified;
end;

procedure payer.SetdefaultSendingAddres(Index: Integer; const Astring: string);
begin
  FdefaultSendingAddres := Astring;
  FdefaultSendingAddres_Specified := True;
end;

function payer.defaultSendingAddres_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingAddres_Specified;
end;

procedure payer.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function payer.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure payer.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function payer.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure payer.SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
begin
  FdocType := APWSTiDocType;
  FdocType_Specified := True;
end;

function payer.docType_Specified(Index: Integer): boolean;
begin
  Result := FdocType_Specified;
end;

procedure payer.SetidentifyingDocValue(Index: Integer; const Astring: string);
begin
  FidentifyingDocValue := Astring;
  FidentifyingDocValue_Specified := True;
end;

function payer.identifyingDocValue_Specified(Index: Integer): boolean;
begin
  Result := FidentifyingDocValue_Specified;
end;

procedure payer.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function payer.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

procedure payer.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function payer.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure payer.SetpostalCode(Index: Integer; const Astring: string);
begin
  FpostalCode := Astring;
  FpostalCode_Specified := True;
end;

function payer.postalCode_Specified(Index: Integer): boolean;
begin
  Result := FpostalCode_Specified;
end;

procedure payer.Setstreet(Index: Integer; const Astring: string);
begin
  Fstreet := Astring;
  Fstreet_Specified := True;
end;

function payer.street_Specified(Index: Integer): boolean;
begin
  Result := Fstreet_Specified;
end;

procedure payer.SetbuildingNumber(Index: Integer; const Astring: string);
begin
  FbuildingNumber := Astring;
  FbuildingNumber_Specified := True;
end;

function payer.buildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FbuildingNumber_Specified;
end;

procedure payer.SetcompanyName(Index: Integer; const Astring: string);
begin
  FcompanyName := Astring;
  FcompanyName_Specified := True;
end;

function payer.companyName_Specified(Index: Integer): boolean;
begin
  Result := FcompanyName_Specified;
end;

procedure payer.SetcompanyStreet(Index: Integer; const Astring: string);
begin
  FcompanyStreet := Astring;
  FcompanyStreet_Specified := True;
end;

function payer.companyStreet_Specified(Index: Integer): boolean;
begin
  Result := FcompanyStreet_Specified;
end;

procedure payer.SetcompanyBuildingNumber(Index: Integer; const Astring: string);
begin
  FcompanyBuildingNumber := Astring;
  FcompanyBuildingNumber_Specified := True;
end;

function payer.companyBuildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FcompanyBuildingNumber_Specified;
end;

procedure payer.SetcompanyPostalCode(Index: Integer; const Astring: string);
begin
  FcompanyPostalCode := Astring;
  FcompanyPostalCode_Specified := True;
end;

function payer.companyPostalCode_Specified(Index: Integer): boolean;
begin
  Result := FcompanyPostalCode_Specified;
end;

procedure payer.SetcompanyNip(Index: Integer; const Astring: string);
begin
  FcompanyNip := Astring;
  FcompanyNip_Specified := True;
end;

function payer.companyNip_Specified(Index: Integer): boolean;
begin
  Result := FcompanyNip_Specified;
end;

destructor place2.Destroy;
begin
  SysUtils.FreeAndNil(FcancelDate);
  SysUtils.FreeAndNil(Fdiscount);
  SysUtils.FreeAndNil(Fluggage);
  inherited Destroy;
end;

procedure place2.Setid(Index: Integer; const AInt64: Int64);
begin
  Fid := AInt64;
  Fid_Specified := True;
end;

function place2.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

procedure place2.SetplaceNumber(Index: Integer; const AInteger: Integer);
begin
  FplaceNumber := AInteger;
  FplaceNumber_Specified := True;
end;

function place2.placeNumber_Specified(Index: Integer): boolean;
begin
  Result := FplaceNumber_Specified;
end;

procedure place2.SetcancelDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcancelDate := ATXSDateTime;
  FcancelDate_Specified := True;
end;

function place2.cancelDate_Specified(Index: Integer): boolean;
begin
  Result := FcancelDate_Specified;
end;

procedure place2.Setdiscount(Index: Integer; const APWSTiDiscount: PWSTiDiscount);
begin
  Fdiscount := APWSTiDiscount;
  Fdiscount_Specified := True;
end;

function place2.discount_Specified(Index: Integer): boolean;
begin
  Result := Fdiscount_Specified;
end;

procedure place2.Setluggage(Index: Integer; const APWSTiTariffForStick: PWSTiTariffForStick);
begin
  Fluggage := APWSTiTariffForStick;
  Fluggage_Specified := True;
end;

function place2.luggage_Specified(Index: Integer): boolean;
begin
  Result := Fluggage_Specified;
end;

destructor connection.Destroy;
begin
  SysUtils.FreeAndNil(FfromStop);
  SysUtils.FreeAndNil(FtoStop);
  inherited Destroy;
end;

procedure connection.SetmillisBeforeFinish(Index: Integer; const AInt64: Int64);
begin
  FmillisBeforeFinish := AInt64;
  FmillisBeforeFinish_Specified := True;
end;

function connection.millisBeforeFinish_Specified(Index: Integer): boolean;
begin
  Result := FmillisBeforeFinish_Specified;
end;

procedure connection.SetfromStop(Index: Integer; const APWSTiStopInTime: PWSTiStopInTime);
begin
  FfromStop := APWSTiStopInTime;
  FfromStop_Specified := True;
end;

function connection.fromStop_Specified(Index: Integer): boolean;
begin
  Result := FfromStop_Specified;
end;

procedure connection.SettoStop(Index: Integer; const APWSTiStopInTime: PWSTiStopInTime);
begin
  FtoStop := APWSTiStopInTime;
  FtoStop_Specified := True;
end;

function connection.toStop_Specified(Index: Integer): boolean;
begin
  Result := FtoStop_Specified;
end;

destructor PWSTiStopInTime.Destroy;
begin
  SysUtils.FreeAndNil(FarrivalTime);
  SysUtils.FreeAndNil(FdepartureTime);
  inherited Destroy;
end;

procedure PWSTiStopInTime.SetarrivalTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FarrivalTime := ATXSDateTime;
  FarrivalTime_Specified := True;
end;

function PWSTiStopInTime.arrivalTime_Specified(Index: Integer): boolean;
begin
  Result := FarrivalTime_Specified;
end;

procedure PWSTiStopInTime.SetdepartureTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdepartureTime := ATXSDateTime;
  FdepartureTime_Specified := True;
end;

function PWSTiStopInTime.departureTime_Specified(Index: Integer): boolean;
begin
  Result := FdepartureTime_Specified;
end;

procedure PWSTiStopInTime.SetstopName(Index: Integer; const Astring: string);
begin
  FstopName := Astring;
  FstopName_Specified := True;
end;

function PWSTiStopInTime.stopName_Specified(Index: Integer): boolean;
begin
  Result := FstopName_Specified;
end;

procedure PWSTiStopInTime.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function PWSTiStopInTime.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

procedure PWSTiStopInTime.SetcommuneName(Index: Integer; const Astring: string);
begin
  FcommuneName := Astring;
  FcommuneName_Specified := True;
end;

function PWSTiStopInTime.communeName_Specified(Index: Integer): boolean;
begin
  Result := FcommuneName_Specified;
end;

procedure PWSTiStopInTime.SetdistrictName(Index: Integer; const Astring: string);
begin
  FdistrictName := Astring;
  FdistrictName_Specified := True;
end;

function PWSTiStopInTime.districtName_Specified(Index: Integer): boolean;
begin
  Result := FdistrictName_Specified;
end;

procedure PWSTiStopInTime.SetprovinceName(Index: Integer; const Astring: string);
begin
  FprovinceName := Astring;
  FprovinceName_Specified := True;
end;

function PWSTiStopInTime.provinceName_Specified(Index: Integer): boolean;
begin
  Result := FprovinceName_Specified;
end;

procedure PWSTiStopInTime.SetcountryName(Index: Integer; const Astring: string);
begin
  FcountryName := Astring;
  FcountryName_Specified := True;
end;

function PWSTiStopInTime.countryName_Specified(Index: Integer): boolean;
begin
  Result := FcountryName_Specified;
end;

destructor holder2.Destroy;
begin
  SysUtils.FreeAndNil(FholderData);
  SysUtils.FreeAndNil(FdefaultSendingType);
  inherited Destroy;
end;

procedure holder2.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function holder2.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure holder2.SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
begin
  FdefaultPeriodicCardId := AInt64;
  FdefaultPeriodicCardId_Specified := True;
end;

function holder2.defaultPeriodicCardId_Specified(Index: Integer): boolean;
begin
  Result := FdefaultPeriodicCardId_Specified;
end;

procedure holder2.SetholderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
begin
  FholderData := APWSTiHolderForTicket;
  FholderData_Specified := True;
end;

function holder2.holderData_Specified(Index: Integer): boolean;
begin
  Result := FholderData_Specified;
end;

procedure holder2.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function holder2.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

procedure holder2.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function holder2.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure holder2.SetpostalCode(Index: Integer; const Astring: string);
begin
  FpostalCode := Astring;
  FpostalCode_Specified := True;
end;

function holder2.postalCode_Specified(Index: Integer): boolean;
begin
  Result := FpostalCode_Specified;
end;

procedure holder2.Setstreet(Index: Integer; const Astring: string);
begin
  Fstreet := Astring;
  Fstreet_Specified := True;
end;

function holder2.street_Specified(Index: Integer): boolean;
begin
  Result := Fstreet_Specified;
end;

procedure holder2.SetbuildingNumber(Index: Integer; const Astring: string);
begin
  FbuildingNumber := Astring;
  FbuildingNumber_Specified := True;
end;

function holder2.buildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FbuildingNumber_Specified;
end;

procedure holder2.SetdefaultSendingType(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  FdefaultSendingType := APWSEnumParam;
  FdefaultSendingType_Specified := True;
end;

function holder2.defaultSendingType_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingType_Specified;
end;

procedure holder2.SetdefaultSendingAddress(Index: Integer; const Astring: string);
begin
  FdefaultSendingAddress := Astring;
  FdefaultSendingAddress_Specified := True;
end;

function holder2.defaultSendingAddress_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingAddress_Specified;
end;

procedure PWSCityId.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function PWSCityId.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

destructor listOfRecord.Destroy;
begin
  SysUtils.FreeAndNil(FdataSprz);
  SysUtils.FreeAndNil(FbWaznyOd);
  SysUtils.FreeAndNil(FbWaznyDo);
  SysUtils.FreeAndNil(FdataRej);
  SysUtils.FreeAndNil(FdataAnul);
  SysUtils.FreeAndNil(FdataWDU);
  SysUtils.FreeAndNil(FdataWDT);
  SysUtils.FreeAndNil(FdataKursu);
  SysUtils.FreeAndNil(FdataOP);
  inherited Destroy;
end;

procedure listOfRecord.SetdataSprz(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataSprz := ATXSDateTime;
  FdataSprz_Specified := True;
end;

function listOfRecord.dataSprz_Specified(Index: Integer): boolean;
begin
  Result := FdataSprz_Specified;
end;

procedure listOfRecord.SetfirmaSP(Index: Integer; const AInteger: Integer);
begin
  FfirmaSP := AInteger;
  FfirmaSP_Specified := True;
end;

function listOfRecord.firmaSP_Specified(Index: Integer): boolean;
begin
  Result := FfirmaSP_Specified;
end;

procedure listOfRecord.SetfirmaP(Index: Integer; const AInteger: Integer);
begin
  FfirmaP := AInteger;
  FfirmaP_Specified := True;
end;

function listOfRecord.firmaP_Specified(Index: Integer): boolean;
begin
  Result := FfirmaP_Specified;
end;

procedure listOfRecord.SetnrKursu(Index: Integer; const AInteger: Integer);
begin
  FnrKursu := AInteger;
  FnrKursu_Specified := True;
end;

function listOfRecord.nrKursu_Specified(Index: Integer): boolean;
begin
  Result := FnrKursu_Specified;
end;

procedure listOfRecord.SetbWaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FbWaznyOd := ATXSDateTime;
  FbWaznyOd_Specified := True;
end;

function listOfRecord.bWaznyOd_Specified(Index: Integer): boolean;
begin
  Result := FbWaznyOd_Specified;
end;

procedure listOfRecord.SetbWaznyDo(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FbWaznyDo := ATXSDateTime;
  FbWaznyDo_Specified := True;
end;

function listOfRecord.bWaznyDo_Specified(Index: Integer): boolean;
begin
  Result := FbWaznyDo_Specified;
end;

procedure listOfRecord.SetnrPP(Index: Integer; const AInteger: Integer);
begin
  FnrPP := AInteger;
  FnrPP_Specified := True;
end;

function listOfRecord.nrPP_Specified(Index: Integer): boolean;
begin
  Result := FnrPP_Specified;
end;

procedure listOfRecord.SetkodPP(Index: Integer; const AInt64: Int64);
begin
  FkodPP := AInt64;
  FkodPP_Specified := True;
end;

function listOfRecord.kodPP_Specified(Index: Integer): boolean;
begin
  Result := FkodPP_Specified;
end;

procedure listOfRecord.SetnrPD(Index: Integer; const AInteger: Integer);
begin
  FnrPD := AInteger;
  FnrPD_Specified := True;
end;

function listOfRecord.nrPD_Specified(Index: Integer): boolean;
begin
  Result := FnrPD_Specified;
end;

procedure listOfRecord.SetkodPD(Index: Integer; const AInt64: Int64);
begin
  FkodPD := AInt64;
  FkodPD_Specified := True;
end;

function listOfRecord.kodPD_Specified(Index: Integer): boolean;
begin
  Result := FkodPD_Specified;
end;

procedure listOfRecord.Setkraj(Index: Integer; const AInteger: Integer);
begin
  Fkraj := AInteger;
  Fkraj_Specified := True;
end;

function listOfRecord.kraj_Specified(Index: Integer): boolean;
begin
  Result := Fkraj_Specified;
end;

procedure listOfRecord.SetkierWL(Index: Integer; const AInteger: Integer);
begin
  FkierWL := AInteger;
  FkierWL_Specified := True;
end;

function listOfRecord.kierWL_Specified(Index: Integer): boolean;
begin
  Result := FkierWL_Specified;
end;

procedure listOfRecord.SetnrLinii(Index: Integer; const AInteger: Integer);
begin
  FnrLinii := AInteger;
  FnrLinii_Specified := True;
end;

function listOfRecord.nrLinii_Specified(Index: Integer): boolean;
begin
  Result := FnrLinii_Specified;
end;

procedure listOfRecord.SetwarLinii(Index: Integer; const AInteger: Integer);
begin
  FwarLinii := AInteger;
  FwarLinii_Specified := True;
end;

function listOfRecord.warLinii_Specified(Index: Integer): boolean;
begin
  Result := FwarLinii_Specified;
end;

procedure listOfRecord.SetnrKier(Index: Integer; const AInteger: Integer);
begin
  FnrKier := AInteger;
  FnrKier_Specified := True;
end;

function listOfRecord.nrKier_Specified(Index: Integer): boolean;
begin
  Result := FnrKier_Specified;
end;

procedure listOfRecord.SetnrKP(Index: Integer; const AInt64: Int64);
begin
  FnrKP := AInt64;
  FnrKP_Specified := True;
end;

function listOfRecord.nrKP_Specified(Index: Integer): boolean;
begin
  Result := FnrKP_Specified;
end;

procedure listOfRecord.SetnrRF(Index: Integer; const AInteger: Integer);
begin
  FnrRF := AInteger;
  FnrRF_Specified := True;
end;

function listOfRecord.nrRF_Specified(Index: Integer): boolean;
begin
  Result := FnrRF_Specified;
end;

procedure listOfRecord.SetnrRZ(Index: Integer; const AInteger: Integer);
begin
  FnrRZ := AInteger;
  FnrRZ_Specified := True;
end;

function listOfRecord.nrRZ_Specified(Index: Integer): boolean;
begin
  Result := FnrRZ_Specified;
end;

procedure listOfRecord.SetlpKier(Index: Integer; const AInteger: Integer);
begin
  FlpKier := AInteger;
  FlpKier_Specified := True;
end;

function listOfRecord.lpKier_Specified(Index: Integer): boolean;
begin
  Result := FlpKier_Specified;
end;

procedure listOfRecord.SetnrStan(Index: Integer; const AInteger: Integer);
begin
  FnrStan := AInteger;
  FnrStan_Specified := True;
end;

function listOfRecord.nrStan_Specified(Index: Integer): boolean;
begin
  Result := FnrStan_Specified;
end;

procedure listOfRecord.SetdataRej(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataRej := ATXSDateTime;
  FdataRej_Specified := True;
end;

function listOfRecord.dataRej_Specified(Index: Integer): boolean;
begin
  Result := FdataRej_Specified;
end;

procedure listOfRecord.SetnrKBil(Index: Integer; const AInt64: Int64);
begin
  FnrKBil := AInt64;
  FnrKBil_Specified := True;
end;

function listOfRecord.nrKBil_Specified(Index: Integer): boolean;
begin
  Result := FnrKBil_Specified;
end;

procedure listOfRecord.SetnrDok(Index: Integer; const AInt64: Int64);
begin
  FnrDok := AInt64;
  FnrDok_Specified := True;
end;

function listOfRecord.nrDok_Specified(Index: Integer): boolean;
begin
  Result := FnrDok_Specified;
end;

procedure listOfRecord.SetlPas(Index: Integer; const AInteger: Integer);
begin
  FlPas := AInteger;
  FlPas_Specified := True;
end;

function listOfRecord.lPas_Specified(Index: Integer): boolean;
begin
  Result := FlPas_Specified;
end;

procedure listOfRecord.SetrodzBil(Index: Integer; const AInteger: Integer);
begin
  FrodzBil := AInteger;
  FrodzBil_Specified := True;
end;

function listOfRecord.rodzBil_Specified(Index: Integer): boolean;
begin
  Result := FrodzBil_Specified;
end;

procedure listOfRecord.SetrodzBM(Index: Integer; const AInteger: Integer);
begin
  FrodzBM := AInteger;
  FrodzBM_Specified := True;
end;

function listOfRecord.rodzBM_Specified(Index: Integer): boolean;
begin
  Result := FrodzBM_Specified;
end;

procedure listOfRecord.SetzapisRK(Index: Integer; const AInteger: Integer);
begin
  FzapisRK := AInteger;
  FzapisRK_Specified := True;
end;

function listOfRecord.zapisRK_Specified(Index: Integer): boolean;
begin
  Result := FzapisRK_Specified;
end;

procedure listOfRecord.Setzaokr(Index: Integer; const AInteger: Integer);
begin
  Fzaokr := AInteger;
  Fzaokr_Specified := True;
end;

function listOfRecord.zaokr_Specified(Index: Integer): boolean;
begin
  Result := Fzaokr_Specified;
end;

procedure listOfRecord.Setdoplata(Index: Integer; const AInteger: Integer);
begin
  Fdoplata := AInteger;
  Fdoplata_Specified := True;
end;

function listOfRecord.doplata_Specified(Index: Integer): boolean;
begin
  Result := Fdoplata_Specified;
end;

procedure listOfRecord.SettypUlgi(Index: Integer; const AInteger: Integer);
begin
  FtypUlgi := AInteger;
  FtypUlgi_Specified := True;
end;

function listOfRecord.typUlgi_Specified(Index: Integer): boolean;
begin
  Result := FtypUlgi_Specified;
end;

procedure listOfRecord.SetkodBind(Index: Integer; const AInteger: Integer);
begin
  FkodBind := AInteger;
  FkodBind_Specified := True;
end;

function listOfRecord.kodBind_Specified(Index: Integer): boolean;
begin
  Result := FkodBind_Specified;
end;

procedure listOfRecord.SetgrUlgi(Index: Integer; const AInteger: Integer);
begin
  FgrUlgi := AInteger;
  FgrUlgi_Specified := True;
end;

function listOfRecord.grUlgi_Specified(Index: Integer): boolean;
begin
  Result := FgrUlgi_Specified;
end;

procedure listOfRecord.SetnrUlgi(Index: Integer; const AInteger: Integer);
begin
  FnrUlgi := AInteger;
  FnrUlgi_Specified := True;
end;

function listOfRecord.nrUlgi_Specified(Index: Integer): boolean;
begin
  Result := FnrUlgi_Specified;
end;

procedure listOfRecord.SetstawkaUl(Index: Integer; const AInteger: Integer);
begin
  FstawkaUl := AInteger;
  FstawkaUl_Specified := True;
end;

function listOfRecord.stawkaUl_Specified(Index: Integer): boolean;
begin
  Result := FstawkaUl_Specified;
end;

procedure listOfRecord.SetcenaBil1(Index: Integer; const ADouble: Double);
begin
  FcenaBil1 := ADouble;
  FcenaBil1_Specified := True;
end;

function listOfRecord.cenaBil1_Specified(Index: Integer): boolean;
begin
  Result := FcenaBil1_Specified;
end;

procedure listOfRecord.SetkwotaBon1(Index: Integer; const ADouble: Double);
begin
  FkwotaBon1 := ADouble;
  FkwotaBon1_Specified := True;
end;

function listOfRecord.kwotaBon1_Specified(Index: Integer): boolean;
begin
  Result := FkwotaBon1_Specified;
end;

procedure listOfRecord.SetkwotaUl1(Index: Integer; const ADouble: Double);
begin
  FkwotaUl1 := ADouble;
  FkwotaUl1_Specified := True;
end;

function listOfRecord.kwotaUl1_Specified(Index: Integer): boolean;
begin
  Result := FkwotaUl1_Specified;
end;

procedure listOfRecord.SetkwotaOM1(Index: Integer; const ADouble: Double);
begin
  FkwotaOM1 := ADouble;
  FkwotaOM1_Specified := True;
end;

function listOfRecord.kwotaOM1_Specified(Index: Integer): boolean;
begin
  Result := FkwotaOM1_Specified;
end;

procedure listOfRecord.SetnrStPTU1(Index: Integer; const AInteger: Integer);
begin
  FnrStPTU1 := AInteger;
  FnrStPTU1_Specified := True;
end;

function listOfRecord.nrStPTU1_Specified(Index: Integer): boolean;
begin
  Result := FnrStPTU1_Specified;
end;

procedure listOfRecord.SetstPTU1(Index: Integer; const ADouble: Double);
begin
  FstPTU1 := ADouble;
  FstPTU1_Specified := True;
end;

function listOfRecord.stPTU1_Specified(Index: Integer): boolean;
begin
  Result := FstPTU1_Specified;
end;

procedure listOfRecord.SetbrutPTU1(Index: Integer; const ADouble: Double);
begin
  FbrutPTU1 := ADouble;
  FbrutPTU1_Specified := True;
end;

function listOfRecord.brutPTU1_Specified(Index: Integer): boolean;
begin
  Result := FbrutPTU1_Specified;
end;

procedure listOfRecord.SetcenaBil2(Index: Integer; const ADouble: Double);
begin
  FcenaBil2 := ADouble;
  FcenaBil2_Specified := True;
end;

function listOfRecord.cenaBil2_Specified(Index: Integer): boolean;
begin
  Result := FcenaBil2_Specified;
end;

procedure listOfRecord.SetkwotaBon2(Index: Integer; const ADouble: Double);
begin
  FkwotaBon2 := ADouble;
  FkwotaBon2_Specified := True;
end;

function listOfRecord.kwotaBon2_Specified(Index: Integer): boolean;
begin
  Result := FkwotaBon2_Specified;
end;

procedure listOfRecord.SetkwotaUl2(Index: Integer; const ADouble: Double);
begin
  FkwotaUl2 := ADouble;
  FkwotaUl2_Specified := True;
end;

function listOfRecord.kwotaUl2_Specified(Index: Integer): boolean;
begin
  Result := FkwotaUl2_Specified;
end;

procedure listOfRecord.SetkwotaOM2(Index: Integer; const ADouble: Double);
begin
  FkwotaOM2 := ADouble;
  FkwotaOM2_Specified := True;
end;

function listOfRecord.kwotaOM2_Specified(Index: Integer): boolean;
begin
  Result := FkwotaOM2_Specified;
end;

procedure listOfRecord.SetnrStPTU2(Index: Integer; const AInteger: Integer);
begin
  FnrStPTU2 := AInteger;
  FnrStPTU2_Specified := True;
end;

function listOfRecord.nrStPTU2_Specified(Index: Integer): boolean;
begin
  Result := FnrStPTU2_Specified;
end;

procedure listOfRecord.SetstPTU2(Index: Integer; const ADouble: Double);
begin
  FstPTU2 := ADouble;
  FstPTU2_Specified := True;
end;

function listOfRecord.stPTU2_Specified(Index: Integer): boolean;
begin
  Result := FstPTU2_Specified;
end;

procedure listOfRecord.SetbrutPTU2(Index: Integer; const ADouble: Double);
begin
  FbrutPTU2 := ADouble;
  FbrutPTU2_Specified := True;
end;

function listOfRecord.brutPTU2_Specified(Index: Integer): boolean;
begin
  Result := FbrutPTU2_Specified;
end;

procedure listOfRecord.SetnrStPTUD(Index: Integer; const AInteger: Integer);
begin
  FnrStPTUD := AInteger;
  FnrStPTUD_Specified := True;
end;

function listOfRecord.nrStPTUD_Specified(Index: Integer): boolean;
begin
  Result := FnrStPTUD_Specified;
end;

procedure listOfRecord.SetstPTUD(Index: Integer; const ADouble: Double);
begin
  FstPTUD := ADouble;
  FstPTUD_Specified := True;
end;

function listOfRecord.stPTUD_Specified(Index: Integer): boolean;
begin
  Result := FstPTUD_Specified;
end;

procedure listOfRecord.SetkwotaDoPL(Index: Integer; const ADouble: Double);
begin
  FkwotaDoPL := ADouble;
  FkwotaDoPL_Specified := True;
end;

function listOfRecord.kwotaDoPL_Specified(Index: Integer): boolean;
begin
  Result := FkwotaDoPL_Specified;
end;

procedure listOfRecord.SetwartBil(Index: Integer; const ADouble: Double);
begin
  FwartBil := ADouble;
  FwartBil_Specified := True;
end;

function listOfRecord.wartBil_Specified(Index: Integer): boolean;
begin
  Result := FwartBil_Specified;
end;

procedure listOfRecord.SetdoZapl(Index: Integer; const ADouble: Double);
begin
  FdoZapl := ADouble;
  FdoZapl_Specified := True;
end;

function listOfRecord.doZapl_Specified(Index: Integer): boolean;
begin
  Result := FdoZapl_Specified;
end;

procedure listOfRecord.SetspZapl(Index: Integer; const AInteger: Integer);
begin
  FspZapl := AInteger;
  FspZapl_Specified := True;
end;

function listOfRecord.spZapl_Specified(Index: Integer): boolean;
begin
  Result := FspZapl_Specified;
end;

procedure listOfRecord.Setwaluta(Index: Integer; const AInteger: Integer);
begin
  Fwaluta := AInteger;
  Fwaluta_Specified := True;
end;

function listOfRecord.waluta_Specified(Index: Integer): boolean;
begin
  Result := Fwaluta_Specified;
end;

procedure listOfRecord.Setsmb(Index: Integer; const AInteger: Integer);
begin
  Fsmb := AInteger;
  Fsmb_Specified := True;
end;

function listOfRecord.smb_Specified(Index: Integer): boolean;
begin
  Result := Fsmb_Specified;
end;

procedure listOfRecord.SetjedWal(Index: Integer; const AInteger: Integer);
begin
  FjedWal := AInteger;
  FjedWal_Specified := True;
end;

function listOfRecord.jedWal_Specified(Index: Integer): boolean;
begin
  Result := FjedWal_Specified;
end;

procedure listOfRecord.SetmnWal(Index: Integer; const ADouble: Double);
begin
  FmnWal := ADouble;
  FmnWal_Specified := True;
end;

function listOfRecord.mnWal_Specified(Index: Integer): boolean;
begin
  Result := FmnWal_Specified;
end;

procedure listOfRecord.Setmnoznik(Index: Integer; const ADouble: Double);
begin
  Fmnoznik := ADouble;
  Fmnoznik_Specified := True;
end;

function listOfRecord.mnoznik_Specified(Index: Integer): boolean;
begin
  Result := Fmnoznik_Specified;
end;

procedure listOfRecord.SetmnUdzPrz(Index: Integer; const ADouble: Double);
begin
  FmnUdzPrz := ADouble;
  FmnUdzPrz_Specified := True;
end;

function listOfRecord.mnUdzPrz_Specified(Index: Integer): boolean;
begin
  Result := FmnUdzPrz_Specified;
end;

procedure listOfRecord.SetkwotaZwr(Index: Integer; const ADouble: Double);
begin
  FkwotaZwr := ADouble;
  FkwotaZwr_Specified := True;
end;

function listOfRecord.kwotaZwr_Specified(Index: Integer): boolean;
begin
  Result := FkwotaZwr_Specified;
end;

procedure listOfRecord.SetdataAnul(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataAnul := ATXSDateTime;
  FdataAnul_Specified := True;
end;

function listOfRecord.dataAnul_Specified(Index: Integer): boolean;
begin
  Result := FdataAnul_Specified;
end;

procedure listOfRecord.SetnrKasjA(Index: Integer; const AInteger: Integer);
begin
  FnrKasjA := AInteger;
  FnrKasjA_Specified := True;
end;

function listOfRecord.nrKasjA_Specified(Index: Integer): boolean;
begin
  Result := FnrKasjA_Specified;
end;

procedure listOfRecord.SetnrRapZadA(Index: Integer; const AInteger: Integer);
begin
  FnrRapZadA := AInteger;
  FnrRapZadA_Specified := True;
end;

function listOfRecord.nrRapZadA_Specified(Index: Integer): boolean;
begin
  Result := FnrRapZadA_Specified;
end;

procedure listOfRecord.SetkmBil(Index: Integer; const ADouble: Double);
begin
  FkmBil := ADouble;
  FkmBil_Specified := True;
end;

function listOfRecord.kmBil_Specified(Index: Integer): boolean;
begin
  Result := FkmBil_Specified;
end;

procedure listOfRecord.SetkmKBil(Index: Integer; const ADouble: Double);
begin
  FkmKBil := ADouble;
  FkmKBil_Specified := True;
end;

function listOfRecord.kmKBil_Specified(Index: Integer): boolean;
begin
  Result := FkmKBil_Specified;
end;

procedure listOfRecord.SetlKursowB(Index: Integer; const AInteger: Integer);
begin
  FlKursowB := AInteger;
  FlKursowB_Specified := True;
end;

function listOfRecord.lKursowB_Specified(Index: Integer): boolean;
begin
  Result := FlKursowB_Specified;
end;

procedure listOfRecord.SetlpKursuB(Index: Integer; const AInteger: Integer);
begin
  FlpKursuB := AInteger;
  FlpKursuB_Specified := True;
end;

function listOfRecord.lpKursuB_Specified(Index: Integer): boolean;
begin
  Result := FlpKursuB_Specified;
end;

procedure listOfRecord.SetlPrzewB(Index: Integer; const AInteger: Integer);
begin
  FlPrzewB := AInteger;
  FlPrzewB_Specified := True;
end;

function listOfRecord.lPrzewB_Specified(Index: Integer): boolean;
begin
  Result := FlPrzewB_Specified;
end;

procedure listOfRecord.SetlPPrzewB(Index: Integer; const AInteger: Integer);
begin
  FlPPrzewB := AInteger;
  FlPPrzewB_Specified := True;
end;

function listOfRecord.lPPrzewB_Specified(Index: Integer): boolean;
begin
  Result := FlPPrzewB_Specified;
end;

procedure listOfRecord.SetnrTrasy(Index: Integer; const AInteger: Integer);
begin
  FnrTrasy := AInteger;
  FnrTrasy_Specified := True;
end;

function listOfRecord.nrTrasy_Specified(Index: Integer): boolean;
begin
  Result := FnrTrasy_Specified;
end;

procedure listOfRecord.SetrelBil(Index: Integer; const AInteger: Integer);
begin
  FrelBil := AInteger;
  FrelBil_Specified := True;
end;

function listOfRecord.relBil_Specified(Index: Integer): boolean;
begin
  Result := FrelBil_Specified;
end;

procedure listOfRecord.SetfirmaKM(Index: Integer; const AInteger: Integer);
begin
  FfirmaKM := AInteger;
  FfirmaKM_Specified := True;
end;

function listOfRecord.firmaKM_Specified(Index: Integer): boolean;
begin
  Result := FfirmaKM_Specified;
end;

procedure listOfRecord.SetnrKartyM(Index: Integer; const AInt64: Int64);
begin
  FnrKartyM := AInt64;
  FnrKartyM_Specified := True;
end;

function listOfRecord.nrKartyM_Specified(Index: Integer): boolean;
begin
  Result := FnrKartyM_Specified;
end;

procedure listOfRecord.SetdokUWBezT(Index: Integer; const ABoolean: Boolean);
begin
  FdokUWBezT := ABoolean;
  FdokUWBezT_Specified := True;
end;

function listOfRecord.dokUWBezT_Specified(Index: Integer): boolean;
begin
  Result := FdokUWBezT_Specified;
end;

procedure listOfRecord.SetdataWDU(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataWDU := ATXSDateTime;
  FdataWDU_Specified := True;
end;

function listOfRecord.dataWDU_Specified(Index: Integer): boolean;
begin
  Result := FdataWDU_Specified;
end;

procedure listOfRecord.SetdokTWBezT(Index: Integer; const ABoolean: Boolean);
begin
  FdokTWBezT := ABoolean;
  FdokTWBezT_Specified := True;
end;

function listOfRecord.dokTWBezT_Specified(Index: Integer): boolean;
begin
  Result := FdokTWBezT_Specified;
end;

procedure listOfRecord.SetdataWDT(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataWDT := ATXSDateTime;
  FdataWDT_Specified := True;
end;

function listOfRecord.dataWDT_Specified(Index: Integer): boolean;
begin
  Result := FdataWDT_Specified;
end;

procedure listOfRecord.SetlPrzBO(Index: Integer; const AInteger: Integer);
begin
  FlPrzBO := AInteger;
  FlPrzBO_Specified := True;
end;

function listOfRecord.lPrzBO_Specified(Index: Integer): boolean;
begin
  Result := FlPrzBO_Specified;
end;

procedure listOfRecord.SetnrSTPROW(Index: Integer; const AInteger: Integer);
begin
  FnrSTPROW := AInteger;
  FnrSTPROW_Specified := True;
end;

function listOfRecord.nrSTPROW_Specified(Index: Integer): boolean;
begin
  Result := FnrSTPROW_Specified;
end;

procedure listOfRecord.SetfirmaK(Index: Integer; const AInteger: Integer);
begin
  FfirmaK := AInteger;
  FfirmaK_Specified := True;
end;

function listOfRecord.firmaK_Specified(Index: Integer): boolean;
begin
  Result := FfirmaK_Specified;
end;

procedure listOfRecord.SetkOBCE(Index: Integer; const AInteger: Integer);
begin
  FkOBCE := AInteger;
  FkOBCE_Specified := True;
end;

function listOfRecord.kOBCE_Specified(Index: Integer): boolean;
begin
  Result := FkOBCE_Specified;
end;

procedure listOfRecord.SetdataKursu(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataKursu := ATXSDateTime;
  FdataKursu_Specified := True;
end;

function listOfRecord.dataKursu_Specified(Index: Integer): boolean;
begin
  Result := FdataKursu_Specified;
end;

procedure listOfRecord.Setwdk(Index: Integer; const AInteger: Integer);
begin
  Fwdk := AInteger;
  Fwdk_Specified := True;
end;

function listOfRecord.wdk_Specified(Index: Integer): boolean;
begin
  Result := Fwdk_Specified;
end;

procedure listOfRecord.SetkmKursu(Index: Integer; const ADouble: Double);
begin
  FkmKursu := ADouble;
  FkmKursu_Specified := True;
end;

function listOfRecord.kmKursu_Specified(Index: Integer): boolean;
begin
  Result := FkmKursu_Specified;
end;

procedure listOfRecord.SetzmKartyM(Index: Integer; const ABoolean: Boolean);
begin
  FzmKartyM := ABoolean;
  FzmKartyM_Specified := True;
end;

function listOfRecord.zmKartyM_Specified(Index: Integer): boolean;
begin
  Result := FzmKartyM_Specified;
end;

procedure listOfRecord.SetpominDoPL(Index: Integer; const ABoolean: Boolean);
begin
  FpominDoPL := ABoolean;
  FpominDoPL_Specified := True;
end;

function listOfRecord.pominDoPL_Specified(Index: Integer): boolean;
begin
  Result := FpominDoPL_Specified;
end;

procedure listOfRecord.SetnrFU(Index: Integer; const AInteger: Integer);
begin
  FnrFU := AInteger;
  FnrFU_Specified := True;
end;

function listOfRecord.nrFU_Specified(Index: Integer): boolean;
begin
  Result := FnrFU_Specified;
end;

procedure listOfRecord.SetdataOP(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FdataOP := ATXSDateTime;
  FdataOP_Specified := True;
end;

function listOfRecord.dataOP_Specified(Index: Integer): boolean;
begin
  Result := FdataOP_Specified;
end;

procedure listOfRecord.SetnrSluzbOP(Index: Integer; const AInteger: Integer);
begin
  FnrSluzbOP := AInteger;
  FnrSluzbOP_Specified := True;
end;

function listOfRecord.nrSluzbOP_Specified(Index: Integer): boolean;
begin
  Result := FnrSluzbOP_Specified;
end;

procedure listOfRecord.SetgodzSprz(Index: Integer; const Astring: string);
begin
  FgodzSprz := Astring;
  FgodzSprz_Specified := True;
end;

function listOfRecord.godzSprz_Specified(Index: Integer): boolean;
begin
  Result := FgodzSprz_Specified;
end;

procedure listOfRecord.Setwariant(Index: Integer; const Astring: string);
begin
  Fwariant := Astring;
  Fwariant_Specified := True;
end;

function listOfRecord.wariant_Specified(Index: Integer): boolean;
begin
  Result := Fwariant_Specified;
end;

procedure listOfRecord.SetgodzOdj(Index: Integer; const Astring: string);
begin
  FgodzOdj := Astring;
  FgodzOdj_Specified := True;
end;

function listOfRecord.godzOdj_Specified(Index: Integer): boolean;
begin
  Result := FgodzOdj_Specified;
end;

procedure listOfRecord.SetnazwaPP(Index: Integer; const Astring: string);
begin
  FnazwaPP := Astring;
  FnazwaPP_Specified := True;
end;

function listOfRecord.nazwaPP_Specified(Index: Integer): boolean;
begin
  Result := FnazwaPP_Specified;
end;

procedure listOfRecord.SetnazwaPD(Index: Integer; const Astring: string);
begin
  FnazwaPD := Astring;
  FnazwaPD_Specified := True;
end;

function listOfRecord.nazwaPD_Specified(Index: Integer): boolean;
begin
  Result := FnazwaPD_Specified;
end;

procedure listOfRecord.SetrodzKom(Index: Integer; const Astring: string);
begin
  FrodzKom := Astring;
  FrodzKom_Specified := True;
end;

function listOfRecord.rodzKom_Specified(Index: Integer): boolean;
begin
  Result := FrodzKom_Specified;
end;

procedure listOfRecord.SetnrZad(Index: Integer; const Astring: string);
begin
  FnrZad := Astring;
  FnrZad_Specified := True;
end;

function listOfRecord.nrZad_Specified(Index: Integer): boolean;
begin
  Result := FnrZad_Specified;
end;

procedure listOfRecord.SetliniaKm(Index: Integer; const Astring: string);
begin
  FliniaKm := Astring;
  FliniaKm_Specified := True;
end;

function listOfRecord.liniaKm_Specified(Index: Integer): boolean;
begin
  Result := FliniaKm_Specified;
end;

procedure listOfRecord.Setimie(Index: Integer; const Astring: string);
begin
  Fimie := Astring;
  Fimie_Specified := True;
end;

function listOfRecord.imie_Specified(Index: Integer): boolean;
begin
  Result := Fimie_Specified;
end;

procedure listOfRecord.Setnazwisko(Index: Integer; const Astring: string);
begin
  Fnazwisko := Astring;
  Fnazwisko_Specified := True;
end;

function listOfRecord.nazwisko_Specified(Index: Integer): boolean;
begin
  Result := Fnazwisko_Specified;
end;

procedure listOfRecord.Setlogo(Index: Integer; const Astring: string);
begin
  Flogo := Astring;
  Flogo_Specified := True;
end;

function listOfRecord.logo_Specified(Index: Integer): boolean;
begin
  Result := Flogo_Specified;
end;

procedure listOfRecord.SetidentRZ(Index: Integer; const Astring: string);
begin
  FidentRZ := Astring;
  FidentRZ_Specified := True;
end;

function listOfRecord.identRZ_Specified(Index: Integer): boolean;
begin
  Result := FidentRZ_Specified;
end;

procedure listOfRecord.SettypRZ(Index: Integer; const Astring: string);
begin
  FtypRZ := Astring;
  FtypRZ_Specified := True;
end;

function listOfRecord.typRZ_Specified(Index: Integer): boolean;
begin
  Result := FtypRZ_Specified;
end;

procedure listOfRecord.SetmiesSprz(Index: Integer; const Astring: string);
begin
  FmiesSprz := Astring;
  FmiesSprz_Specified := True;
end;

function listOfRecord.miesSprz_Specified(Index: Integer): boolean;
begin
  Result := FmiesSprz_Specified;
end;

procedure listOfRecord.SetmiesWazn(Index: Integer; const Astring: string);
begin
  FmiesWazn := Astring;
  FmiesWazn_Specified := True;
end;

function listOfRecord.miesWazn_Specified(Index: Integer): boolean;
begin
  Result := FmiesWazn_Specified;
end;

procedure listOfRecord.SetnrBiletu(Index: Integer; const Astring: string);
begin
  FnrBiletu := Astring;
  FnrBiletu_Specified := True;
end;

function listOfRecord.nrBiletu_Specified(Index: Integer): boolean;
begin
  Result := FnrBiletu_Specified;
end;

procedure listOfRecord.SettypBiletu(Index: Integer; const Astring: string);
begin
  FtypBiletu := Astring;
  FtypBiletu_Specified := True;
end;

function listOfRecord.typBiletu_Specified(Index: Integer): boolean;
begin
  Result := FtypBiletu_Specified;
end;

procedure listOfRecord.SetgodzPocz(Index: Integer; const Astring: string);
begin
  FgodzPocz := Astring;
  FgodzPocz_Specified := True;
end;

function listOfRecord.godzPocz_Specified(Index: Integer): boolean;
begin
  Result := FgodzPocz_Specified;
end;

procedure listOfRecord.SetgodzKon(Index: Integer; const Astring: string);
begin
  FgodzKon := Astring;
  FgodzKon_Specified := True;
end;

function listOfRecord.godzKon_Specified(Index: Integer): boolean;
begin
  Result := FgodzKon_Specified;
end;

procedure listOfRecord.SetnazUlgi(Index: Integer; const Astring: string);
begin
  FnazUlgi := Astring;
  FnazUlgi_Specified := True;
end;

function listOfRecord.nazUlgi_Specified(Index: Integer): boolean;
begin
  Result := FnazUlgi_Specified;
end;

procedure listOfRecord.SetnazSpZapl(Index: Integer; const Astring: string);
begin
  FnazSpZapl := Astring;
  FnazSpZapl_Specified := True;
end;

function listOfRecord.nazSpZapl_Specified(Index: Integer): boolean;
begin
  Result := FnazSpZapl_Specified;
end;

procedure listOfRecord.SetoznWal(Index: Integer; const Astring: string);
begin
  FoznWal := Astring;
  FoznWal_Specified := True;
end;

function listOfRecord.oznWal_Specified(Index: Integer): boolean;
begin
  Result := FoznWal_Specified;
end;

procedure listOfRecord.SetidentRZA(Index: Integer; const Astring: string);
begin
  FidentRZA := Astring;
  FidentRZA_Specified := True;
end;

function listOfRecord.identRZA_Specified(Index: Integer): boolean;
begin
  Result := FidentRZA_Specified;
end;

procedure listOfRecord.SetoznaczK(Index: Integer; const Astring: string);
begin
  FoznaczK := Astring;
  FoznaczK_Specified := True;
end;

function listOfRecord.oznaczK_Specified(Index: Integer): boolean;
begin
  Result := FoznaczK_Specified;
end;

procedure listOfRecord.SetdniRelBM(Index: Integer; const Astring: string);
begin
  FdniRelBM := Astring;
  FdniRelBM_Specified := True;
end;

function listOfRecord.dniRelBM_Specified(Index: Integer): boolean;
begin
  Result := FdniRelBM_Specified;
end;

procedure listOfRecord.SetnrDokUlgi(Index: Integer; const Astring: string);
begin
  FnrDokUlgi := Astring;
  FnrDokUlgi_Specified := True;
end;

function listOfRecord.nrDokUlgi_Specified(Index: Integer): boolean;
begin
  Result := FnrDokUlgi_Specified;
end;

procedure listOfRecord.SetnrPas(Index: Integer; const Astring: string);
begin
  FnrPas := Astring;
  FnrPas_Specified := True;
end;

function listOfRecord.nrPas_Specified(Index: Integer): boolean;
begin
  Result := FnrPas_Specified;
end;

procedure listOfRecord.SetnrDokTOZS(Index: Integer; const Astring: string);
begin
  FnrDokTOZS := Astring;
  FnrDokTOZS_Specified := True;
end;

function listOfRecord.nrDokTOZS_Specified(Index: Integer): boolean;
begin
  Result := FnrDokTOZS_Specified;
end;

procedure listOfRecord.SetszyfrBil(Index: Integer; const Astring: string);
begin
  FszyfrBil := Astring;
  FszyfrBil_Specified := True;
end;

function listOfRecord.szyfrBil_Specified(Index: Integer): boolean;
begin
  Result := FszyfrBil_Specified;
end;

procedure listOfRecord.SetrelacjaK(Index: Integer; const Astring: string);
begin
  FrelacjaK := Astring;
  FrelacjaK_Specified := True;
end;

function listOfRecord.relacjaK_Specified(Index: Integer): boolean;
begin
  Result := FrelacjaK_Specified;
end;

procedure listOfRecord.SetrodzSP(Index: Integer; const Astring: string);
begin
  FrodzSP := Astring;
  FrodzSP_Specified := True;
end;

function listOfRecord.rodzSP_Specified(Index: Integer): boolean;
begin
  Result := FrodzSP_Specified;
end;

procedure listOfRecord.SetkodKBil(Index: Integer; const Astring: string);
begin
  FkodKBil := Astring;
  FkodKBil_Specified := True;
end;

function listOfRecord.kodKBil_Specified(Index: Integer): boolean;
begin
  Result := FkodKBil_Specified;
end;

procedure listOfRecord.SetnrKursuE(Index: Integer; const Astring: string);
begin
  FnrKursuE := Astring;
  FnrKursuE_Specified := True;
end;

function listOfRecord.nrKursuE_Specified(Index: Integer): boolean;
begin
  Result := FnrKursuE_Specified;
end;

procedure listOfRecord.SetgodzPrzyj(Index: Integer; const Astring: string);
begin
  FgodzPrzyj := Astring;
  FgodzPrzyj_Specified := True;
end;

function listOfRecord.godzPrzyj_Specified(Index: Integer): boolean;
begin
  Result := FgodzPrzyj_Specified;
end;

procedure listOfRecord.SetzbiorA(Index: Integer; const Astring: string);
begin
  FzbiorA := Astring;
  FzbiorA_Specified := True;
end;

function listOfRecord.zbiorA_Specified(Index: Integer): boolean;
begin
  Result := FzbiorA_Specified;
end;

procedure listOfRecord.SetgodzOdjK(Index: Integer; const Astring: string);
begin
  FgodzOdjK := Astring;
  FgodzOdjK_Specified := True;
end;

function listOfRecord.godzOdjK_Specified(Index: Integer): boolean;
begin
  Result := FgodzOdjK_Specified;
end;

procedure listOfRecord.SetgodzOP(Index: Integer; const Astring: string);
begin
  FgodzOP := Astring;
  FgodzOP_Specified := True;
end;

function listOfRecord.godzOP_Specified(Index: Integer): boolean;
begin
  Result := FgodzOP_Specified;
end;

procedure listOfRecord.SetcompanyCode(Index: Integer; const Astring: string);
begin
  FcompanyCode := Astring;
  FcompanyCode_Specified := True;
end;

function listOfRecord.companyCode_Specified(Index: Integer): boolean;
begin
  Result := FcompanyCode_Specified;
end;

destructor PWSMessageFromDriver.Destroy;
begin
  SysUtils.FreeAndNil(Fvehicle);
  SysUtils.FreeAndNil(Fmessage_);
  inherited Destroy;
end;

procedure PWSMessageFromDriver.Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
begin
  Fvehicle := APWSVehicle;
  Fvehicle_Specified := True;
end;

function PWSMessageFromDriver.vehicle_Specified(Index: Integer): boolean;
begin
  Result := Fvehicle_Specified;
end;

procedure PWSMessageFromDriver.Setmessage_(Index: Integer; const APWSMessage: PWSMessage);
begin
  Fmessage_ := APWSMessage;
  Fmessage__Specified := True;
end;

function PWSMessageFromDriver.message__Specified(Index: Integer): boolean;
begin
  Result := Fmessage__Specified;
end;

procedure carrierType2.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function carrierType2.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure carrierType2.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function carrierType2.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure discount2.SetvalueAfterDiscount(Index: Integer; const ASingle: Single);
begin
  FvalueAfterDiscount := ASingle;
  FvalueAfterDiscount_Specified := True;
end;

function discount2.valueAfterDiscount_Specified(Index: Integer): boolean;
begin
  Result := FvalueAfterDiscount_Specified;
end;

procedure discount2.SetdiscountValue(Index: Integer; const ASingle: Single);
begin
  FdiscountValue := ASingle;
  FdiscountValue_Specified := True;
end;

function discount2.discountValue_Specified(Index: Integer): boolean;
begin
  Result := FdiscountValue_Specified;
end;

procedure discount2.SetdefaultDis(Index: Integer; const ABoolean: Boolean);
begin
  FdefaultDis := ABoolean;
  FdefaultDis_Specified := True;
end;

function discount2.defaultDis_Specified(Index: Integer): boolean;
begin
  Result := FdefaultDis_Specified;
end;

procedure discount2.SettravelGroupId(Index: Integer; const AInt64: Int64);
begin
  FtravelGroupId := AInt64;
  FtravelGroupId_Specified := True;
end;

function discount2.travelGroupId_Specified(Index: Integer): boolean;
begin
  Result := FtravelGroupId_Specified;
end;

procedure discount2.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function discount2.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure discount2.Setcode(Index: Integer; const Astring: string);
begin
  Fcode := Astring;
  Fcode_Specified := True;
end;

function discount2.code_Specified(Index: Integer): boolean;
begin
  Result := Fcode_Specified;
end;

procedure discount2.Setdescription(Index: Integer; const Astring: string);
begin
  Fdescription := Astring;
  Fdescription_Specified := True;
end;

function discount2.description_Specified(Index: Integer): boolean;
begin
  Result := Fdescription_Specified;
end;

procedure discount2.SetroundType(Index: Integer; const AroundType: roundType);
begin
  FroundType := AroundType;
  FroundType_Specified := True;
end;

function discount2.roundType_Specified(Index: Integer): boolean;
begin
  Result := FroundType_Specified;
end;

procedure discount2.Setudot(Index: Integer; const Astring: string);
begin
  Fudot := Astring;
  Fudot_Specified := True;
end;

function discount2.udot_Specified(Index: Integer): boolean;
begin
  Result := Fudot_Specified;
end;

procedure discount2.SetdiscountType(Index: Integer; const Astring: string);
begin
  FdiscountType := Astring;
  FdiscountType_Specified := True;
end;

function discount2.discountType_Specified(Index: Integer): boolean;
begin
  Result := FdiscountType_Specified;
end;

destructor PTiPlace.Destroy;
begin
  SysUtils.FreeAndNil(FcancelDate);
  SysUtils.FreeAndNil(Fdiscount);
  SysUtils.FreeAndNil(Fticket);
  SysUtils.FreeAndNil(Fluggage);
  inherited Destroy;
end;

procedure PTiPlace.SetplaceNumber(Index: Integer; const AInteger: Integer);
begin
  FplaceNumber := AInteger;
  FplaceNumber_Specified := True;
end;

function PTiPlace.placeNumber_Specified(Index: Integer): boolean;
begin
  Result := FplaceNumber_Specified;
end;

procedure PTiPlace.SetcancelDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcancelDate := ATXSDateTime;
  FcancelDate_Specified := True;
end;

function PTiPlace.cancelDate_Specified(Index: Integer): boolean;
begin
  Result := FcancelDate_Specified;
end;

procedure PTiPlace.Setid(Index: Integer; const AInt64: Int64);
begin
  Fid := AInt64;
  Fid_Specified := True;
end;

function PTiPlace.id_Specified(Index: Integer): boolean;
begin
  Result := Fid_Specified;
end;

procedure PTiPlace.Setdiscount(Index: Integer; const Adiscount2: discount2);
begin
  Fdiscount := Adiscount2;
  Fdiscount_Specified := True;
end;

function PTiPlace.discount_Specified(Index: Integer): boolean;
begin
  Result := Fdiscount_Specified;
end;

procedure PTiPlace.SetbankAccountNumber(Index: Integer; const Astring: string);
begin
  FbankAccountNumber := Astring;
  FbankAccountNumber_Specified := True;
end;

function PTiPlace.bankAccountNumber_Specified(Index: Integer): boolean;
begin
  Result := FbankAccountNumber_Specified;
end;

procedure PTiPlace.SetcancelState(Index: Integer; const AcancelState: cancelState);
begin
  FcancelState := AcancelState;
  FcancelState_Specified := True;
end;

function PTiPlace.cancelState_Specified(Index: Integer): boolean;
begin
  Result := FcancelState_Specified;
end;

procedure PTiPlace.Setticket(Index: Integer; const Aticket2: ticket2);
begin
  Fticket := Aticket2;
  Fticket_Specified := True;
end;

function PTiPlace.ticket_Specified(Index: Integer): boolean;
begin
  Result := Fticket_Specified;
end;

procedure PTiPlace.Setluggage(Index: Integer; const APTiTariffForStick: PTiTariffForStick);
begin
  Fluggage := APTiTariffForStick;
  Fluggage_Specified := True;
end;

function PTiPlace.luggage_Specified(Index: Integer): boolean;
begin
  Result := Fluggage_Specified;
end;

destructor connection2.Destroy;
begin
  SysUtils.FreeAndNil(FfromStop);
  SysUtils.FreeAndNil(FtoStop);
  inherited Destroy;
end;

procedure connection2.SetmillisBeforeFinish(Index: Integer; const AInt64: Int64);
begin
  FmillisBeforeFinish := AInt64;
  FmillisBeforeFinish_Specified := True;
end;

function connection2.millisBeforeFinish_Specified(Index: Integer): boolean;
begin
  Result := FmillisBeforeFinish_Specified;
end;

procedure connection2.SetfromStop(Index: Integer; const APTiStopInTime: PTiStopInTime);
begin
  FfromStop := APTiStopInTime;
  FfromStop_Specified := True;
end;

function connection2.fromStop_Specified(Index: Integer): boolean;
begin
  Result := FfromStop_Specified;
end;

procedure connection2.SettoStop(Index: Integer; const APTiStopInTime: PTiStopInTime);
begin
  FtoStop := APTiStopInTime;
  FtoStop_Specified := True;
end;

function connection2.toStop_Specified(Index: Integer): boolean;
begin
  Result := FtoStop_Specified;
end;

destructor holder3.Destroy;
begin
  SysUtils.FreeAndNil(FholderData);
  inherited Destroy;
end;

procedure holder3.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function holder3.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure holder3.SetdefaultPeriodicCardId(Index: Integer; const AInt64: Int64);
begin
  FdefaultPeriodicCardId := AInt64;
  FdefaultPeriodicCardId_Specified := True;
end;

function holder3.defaultPeriodicCardId_Specified(Index: Integer): boolean;
begin
  Result := FdefaultPeriodicCardId_Specified;
end;

procedure holder3.SetholderData(Index: Integer; const APTiHolderForTicket: PTiHolderForTicket);
begin
  FholderData := APTiHolderForTicket;
  FholderData_Specified := True;
end;

function holder3.holderData_Specified(Index: Integer): boolean;
begin
  Result := FholderData_Specified;
end;

procedure holder3.Setemail(Index: Integer; const Astring: string);
begin
  Femail := Astring;
  Femail_Specified := True;
end;

function holder3.email_Specified(Index: Integer): boolean;
begin
  Result := Femail_Specified;
end;

procedure holder3.Setphone(Index: Integer; const Astring: string);
begin
  Fphone := Astring;
  Fphone_Specified := True;
end;

function holder3.phone_Specified(Index: Integer): boolean;
begin
  Result := Fphone_Specified;
end;

procedure holder3.SetpostalCode(Index: Integer; const Astring: string);
begin
  FpostalCode := Astring;
  FpostalCode_Specified := True;
end;

function holder3.postalCode_Specified(Index: Integer): boolean;
begin
  Result := FpostalCode_Specified;
end;

procedure holder3.Setstreet(Index: Integer; const Astring: string);
begin
  Fstreet := Astring;
  Fstreet_Specified := True;
end;

function holder3.street_Specified(Index: Integer): boolean;
begin
  Result := Fstreet_Specified;
end;

procedure holder3.SetbuildingNumber(Index: Integer; const Astring: string);
begin
  FbuildingNumber := Astring;
  FbuildingNumber_Specified := True;
end;

function holder3.buildingNumber_Specified(Index: Integer): boolean;
begin
  Result := FbuildingNumber_Specified;
end;

procedure holder3.SetdefaultSendingType(Index: Integer; const AdefaultSendingType: defaultSendingType);
begin
  FdefaultSendingType := AdefaultSendingType;
  FdefaultSendingType_Specified := True;
end;

function holder3.defaultSendingType_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingType_Specified;
end;

procedure holder3.SetdefaultSendingAddress(Index: Integer; const Astring: string);
begin
  FdefaultSendingAddress := Astring;
  FdefaultSendingAddress_Specified := True;
end;

function holder3.defaultSendingAddress_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingAddress_Specified;
end;

destructor PWSTiVendingEvent.Destroy;
begin
  SysUtils.FreeAndNil(FcreationTimestamp);
  inherited Destroy;
end;

procedure PWSTiVendingEvent.SetticketOrderId(Index: Integer; const AInt64: Int64);
begin
  FticketOrderId := AInt64;
  FticketOrderId_Specified := True;
end;

function PWSTiVendingEvent.ticketOrderId_Specified(Index: Integer): boolean;
begin
  Result := FticketOrderId_Specified;
end;

procedure PWSTiVendingEvent.SetcreationTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcreationTimestamp := ATXSDateTime;
  FcreationTimestamp_Specified := True;
end;

function PWSTiVendingEvent.creationTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FcreationTimestamp_Specified;
end;

procedure PWSTiVendingEvent.SeteventLevel(Index: Integer; const Astring: string);
begin
  FeventLevel := Astring;
  FeventLevel_Specified := True;
end;

function PWSTiVendingEvent.eventLevel_Specified(Index: Integer): boolean;
begin
  Result := FeventLevel_Specified;
end;

procedure PWSTiVendingEvent.Setmessage_(Index: Integer; const Astring: string);
begin
  Fmessage_ := Astring;
  Fmessage__Specified := True;
end;

function PWSTiVendingEvent.message__Specified(Index: Integer): boolean;
begin
  Result := Fmessage__Specified;
end;

procedure PWSTiVendingEvent.Setstate(Index: Integer; const Astring: string);
begin
  Fstate := Astring;
  Fstate_Specified := True;
end;

function PWSTiVendingEvent.state_Specified(Index: Integer): boolean;
begin
  Result := Fstate_Specified;
end;

procedure PWSTiVendingEvent.SetstackTrace(Index: Integer; const Astring: string);
begin
  FstackTrace := Astring;
  FstackTrace_Specified := True;
end;

function PWSTiVendingEvent.stackTrace_Specified(Index: Integer): boolean;
begin
  Result := FstackTrace_Specified;
end;

procedure PWSTiVendingEvent.Settype_(Index: Integer; const Astring: string);
begin
  Ftype_ := Astring;
  Ftype__Specified := True;
end;

function PWSTiVendingEvent.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

procedure PWSTiVendingEvent.Setvalue(Index: Integer; const Astring: string);
begin
  Fvalue := Astring;
  Fvalue_Specified := True;
end;

function PWSTiVendingEvent.value_Specified(Index: Integer): boolean;
begin
  Result := Fvalue_Specified;
end;

procedure PWSTiVendingEvent.Setsource(Index: Integer; const Astring: string);
begin
  Fsource := Astring;
  Fsource_Specified := True;
end;

function PWSTiVendingEvent.source_Specified(Index: Integer): boolean;
begin
  Result := Fsource_Specified;
end;

procedure stickId2.SetfromRouteId(Index: Integer; const AInt64: Int64);
begin
  FfromRouteId := AInt64;
  FfromRouteId_Specified := True;
end;

function stickId2.fromRouteId_Specified(Index: Integer): boolean;
begin
  Result := FfromRouteId_Specified;
end;

procedure stickId2.SettoRouteId(Index: Integer; const AInt64: Int64);
begin
  FtoRouteId := AInt64;
  FtoRouteId_Specified := True;
end;

function stickId2.toRouteId_Specified(Index: Integer): boolean;
begin
  Result := FtoRouteId_Specified;
end;

procedure PWSTiSellingReport2.SetfaultDescription(Index: Integer; const Astring: string);
begin
  FfaultDescription := Astring;
  FfaultDescription_Specified := True;
end;

function PWSTiSellingReport2.faultDescription_Specified(Index: Integer): boolean;
begin
  Result := FfaultDescription_Specified;
end;

procedure PWSEmptyTimeTable.Setfault(Index: Integer; const Afault: fault);
begin
  Ffault := Afault;
  Ffault_Specified := True;
end;

function PWSEmptyTimeTable.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSMoreThanOneCarrier.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSMoreThanOneCarrier.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSStops.Setfault(Index: Integer; const Afault2: fault2);
begin
  Ffault := Afault2;
  Ffault_Specified := True;
end;

function PWSStops.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSNoSuchRecording.SetrecordingNo(Index: Integer; const Astring: string);
begin
  FrecordingNo := Astring;
  FrecordingNo_Specified := True;
end;

function PWSNoSuchRecording.recordingNo_Specified(Index: Integer): boolean;
begin
  Result := FrecordingNo_Specified;
end;

procedure PWSChangeUserData.Setfault(Index: Integer; const Afault3: fault3);
begin
  Ffault := Afault3;
  Ffault_Specified := True;
end;

function PWSChangeUserData.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSChangePassword.Setfault(Index: Integer; const Afault4: fault4);
begin
  Ffault := Afault4;
  Ffault_Specified := True;
end;

function PWSChangePassword.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSNoSuchInfCarrier.SetcompanyCode(Index: Integer; const Astring: string);
begin
  FcompanyCode := Astring;
  FcompanyCode_Specified := True;
end;

function PWSNoSuchInfCarrier.companyCode_Specified(Index: Integer): boolean;
begin
  Result := FcompanyCode_Specified;
end;

destructor PWSNoSuchInfCourse.Destroy;
begin
  SysUtils.FreeAndNil(FwaznyOd);
  inherited Destroy;
end;

procedure PWSNoSuchInfCourse.SetnrKursu(Index: Integer; const AInteger: Integer);
begin
  FnrKursu := AInteger;
  FnrKursu_Specified := True;
end;

function PWSNoSuchInfCourse.nrKursu_Specified(Index: Integer): boolean;
begin
  Result := FnrKursu_Specified;
end;

procedure PWSNoSuchInfCourse.SetwaznyOd(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FwaznyOd := ATXSDateTime;
  FwaznyOd_Specified := True;
end;

function PWSNoSuchInfCourse.waznyOd_Specified(Index: Integer): boolean;
begin
  Result := FwaznyOd_Specified;
end;

procedure PWSNoSuchInfCourse.SetkierTam(Index: Integer; const ABoolean: Boolean);
begin
  FkierTam := ABoolean;
  FkierTam_Specified := True;
end;

function PWSNoSuchInfCourse.kierTam_Specified(Index: Integer): boolean;
begin
  Result := FkierTam_Specified;
end;

procedure PWSNoSuchInfCourse.SetinfNrf(Index: Integer; const AInteger: Integer);
begin
  FinfNrf := AInteger;
  FinfNrf_Specified := True;
end;

function PWSNoSuchInfCourse.infNrf_Specified(Index: Integer): boolean;
begin
  Result := FinfNrf_Specified;
end;

procedure PWSNoSuchInfCourse.Setwariant(Index: Integer; const Astring: string);
begin
  Fwariant := Astring;
  Fwariant_Specified := True;
end;

function PWSNoSuchInfCourse.wariant_Specified(Index: Integer): boolean;
begin
  Result := Fwariant_Specified;
end;

procedure PWSNoSuchInfCourse.SetrodzKom(Index: Integer; const Astring: string);
begin
  FrodzKom := Astring;
  FrodzKom_Specified := True;
end;

function PWSNoSuchInfCourse.rodzKom_Specified(Index: Integer): boolean;
begin
  Result := FrodzKom_Specified;
end;

procedure PWSNoConn.Setfault(Index: Integer; const Afault5: fault5);
begin
  Ffault := Afault5;
  Ffault_Specified := True;
end;

function PWSNoConn.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSNoVehicle.SetregistrationNumber(Index: Integer; const Astring: string);
begin
  FregistrationNumber := Astring;
  FregistrationNumber_Specified := True;
end;

function PWSNoVehicle.registrationNumber_Specified(Index: Integer): boolean;
begin
  Result := FregistrationNumber_Specified;
end;

procedure PWSNoVehicle.SetvehicleNumber(Index: Integer; const Astring: string);
begin
  FvehicleNumber := Astring;
  FvehicleNumber_Specified := True;
end;

function PWSNoVehicle.vehicleNumber_Specified(Index: Integer): boolean;
begin
  Result := FvehicleNumber_Specified;
end;

procedure PWSCreateUser.Setfault(Index: Integer; const Afault6: fault6);
begin
  Ffault := Afault6;
  Ffault_Specified := True;
end;

function PWSCreateUser.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSLogin.Setfault(Index: Integer; const Afault7: fault7);
begin
  Ffault := Afault7;
  Ffault_Specified := True;
end;

function PWSLogin.fault_Specified(Index: Integer): boolean;
begin
  Result := Ffault_Specified;
end;

procedure PWSLogin.Setmessage_(Index: Integer; const Astring: string);
begin
  Fmessage_ := Astring;
  Fmessage__Specified := True;
end;

function PWSLogin.message__Specified(Index: Integer): boolean;
begin
  Result := Fmessage__Specified;
end;

destructor PWSTiCommitResrvation.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FcauseData)-1 do
    SysUtils.FreeAndNil(FcauseData[I]);
  System.SetLength(FcauseData, 0);
  SysUtils.FreeAndNil(FPWSTiOrderUnavailable);
  inherited Destroy;
end;

procedure PWSTiCommitResrvation.SetPWSTiOrderUnavailable(Index: Integer; const APWSTiOrderUnavailable: PWSTiOrderUnavailable);
begin
  FPWSTiOrderUnavailable := APWSTiOrderUnavailable;
  FPWSTiOrderUnavailable_Specified := True;
end;

function PWSTiCommitResrvation.PWSTiOrderUnavailable_Specified(Index: Integer): boolean;
begin
  Result := FPWSTiOrderUnavailable_Specified;
end;

procedure PWSTiCommitResrvation.SetcauseData(Index: Integer; const AcauseData: causeData);
begin
  FcauseData := AcauseData;
  FcauseData_Specified := True;
end;

function PWSTiCommitResrvation.causeData_Specified(Index: Integer): boolean;
begin
  Result := FcauseData_Specified;
end;

procedure placesNumsBounds.SetminPlaceNumber(Index: Integer; const AInteger: Integer);
begin
  FminPlaceNumber := AInteger;
  FminPlaceNumber_Specified := True;
end;

function placesNumsBounds.minPlaceNumber_Specified(Index: Integer): boolean;
begin
  Result := FminPlaceNumber_Specified;
end;

procedure placesNumsBounds.SetmaxPlaceNumber(Index: Integer; const AInteger: Integer);
begin
  FmaxPlaceNumber := AInteger;
  FmaxPlaceNumber_Specified := True;
end;

function placesNumsBounds.maxPlaceNumber_Specified(Index: Integer): boolean;
begin
  Result := FmaxPlaceNumber_Specified;
end;

procedure placesNumsBounds.SetnumberOfPlacesInVeh(Index: Integer; const AInteger: Integer);
begin
  FnumberOfPlacesInVeh := AInteger;
  FnumberOfPlacesInVeh_Specified := True;
end;

function placesNumsBounds.numberOfPlacesInVeh_Specified(Index: Integer): boolean;
begin
  Result := FnumberOfPlacesInVeh_Specified;
end;

procedure placesNumsBounds.Setmatrix(Index: Integer; const Amatrix: matrix);
begin
  Fmatrix := Amatrix;
  Fmatrix_Specified := True;
end;

function placesNumsBounds.matrix_Specified(Index: Integer): boolean;
begin
  Result := Fmatrix_Specified;
end;

destructor PWSTiSellingData.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FsellingDataForStick)-1 do
    SysUtils.FreeAndNil(FsellingDataForStick[I]);
  System.SetLength(FsellingDataForStick, 0);
  for I := 0 to System.Length(FdocType)-1 do
    SysUtils.FreeAndNil(FdocType[I]);
  System.SetLength(FdocType, 0);
  inherited Destroy;
end;

procedure PWSTiSellingData.SetsellingDataForStick(Index: Integer; const AArray_Of_sellingDataForStick: Array_Of_sellingDataForStick);
begin
  FsellingDataForStick := AArray_Of_sellingDataForStick;
  FsellingDataForStick_Specified := True;
end;

function PWSTiSellingData.sellingDataForStick_Specified(Index: Integer): boolean;
begin
  Result := FsellingDataForStick_Specified;
end;

procedure PWSTiSellingData.SetdocType(Index: Integer; const AArray_Of_PWSTiDocType: Array_Of_PWSTiDocType);
begin
  FdocType := AArray_Of_PWSTiDocType;
  FdocType_Specified := True;
end;

function PWSTiSellingData.docType_Specified(Index: Integer): boolean;
begin
  Result := FdocType_Specified;
end;

destructor sellingDataForStick.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fdiscount)-1 do
    SysUtils.FreeAndNil(Fdiscount[I]);
  System.SetLength(Fdiscount, 0);
  for I := 0 to System.Length(Ftariffe)-1 do
    SysUtils.FreeAndNil(Ftariffe[I]);
  System.SetLength(Ftariffe, 0);
  for I := 0 to System.Length(FPWSTiTariffPriceAfterDiscount)-1 do
    SysUtils.FreeAndNil(FPWSTiTariffPriceAfterDiscount[I]);
  System.SetLength(FPWSTiTariffPriceAfterDiscount, 0);
  SysUtils.FreeAndNil(FplacesNumsBounds);
  inherited Destroy;
end;

procedure sellingDataForStick.SetticketWithoutHolderOkInVM(Index: Integer; const ABoolean: Boolean);
begin
  FticketWithoutHolderOkInVM := ABoolean;
  FticketWithoutHolderOkInVM_Specified := True;
end;

function sellingDataForStick.ticketWithoutHolderOkInVM_Specified(Index: Integer): boolean;
begin
  Result := FticketWithoutHolderOkInVM_Specified;
end;

procedure sellingDataForStick.Setdiscount(Index: Integer; const AArray_Of_PWSTiDiscount: Array_Of_PWSTiDiscount);
begin
  Fdiscount := AArray_Of_PWSTiDiscount;
  Fdiscount_Specified := True;
end;

function sellingDataForStick.discount_Specified(Index: Integer): boolean;
begin
  Result := Fdiscount_Specified;
end;

procedure sellingDataForStick.Settariffe(Index: Integer; const AArray_Of_PWSTiTariffForStick: Array_Of_PWSTiTariffForStick);
begin
  Ftariffe := AArray_Of_PWSTiTariffForStick;
  Ftariffe_Specified := True;
end;

function sellingDataForStick.tariffe_Specified(Index: Integer): boolean;
begin
  Result := Ftariffe_Specified;
end;

procedure sellingDataForStick.SetplacesNumsBounds(Index: Integer; const AplacesNumsBounds: placesNumsBounds);
begin
  FplacesNumsBounds := AplacesNumsBounds;
  FplacesNumsBounds_Specified := True;
end;

function sellingDataForStick.placesNumsBounds_Specified(Index: Integer): boolean;
begin
  Result := FplacesNumsBounds_Specified;
end;

procedure sellingDataForStick.SetPWSTiTariffPriceAfterDiscount(Index: Integer; const AArray_Of_PWSTiTariffPriceAfterDiscount: Array_Of_PWSTiTariffPriceAfterDiscount);
begin
  FPWSTiTariffPriceAfterDiscount := AArray_Of_PWSTiTariffPriceAfterDiscount;
  FPWSTiTariffPriceAfterDiscount_Specified := True;
end;

function sellingDataForStick.PWSTiTariffPriceAfterDiscount_Specified(Index: Integer): boolean;
begin
  Result := FPWSTiTariffPriceAfterDiscount_Specified;
end;

destructor PWSTiTariffForStick.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fprice)-1 do
    SysUtils.FreeAndNil(Fprice[I]);
  System.SetLength(Fprice, 0);
  SysUtils.FreeAndNil(FtariffType);
  inherited Destroy;
end;

procedure PWSTiTariffForStick.SetpriceId(Index: Integer; const AInt64: Int64);
begin
  FpriceId := AInt64;
  FpriceId_Specified := True;
end;

function PWSTiTariffForStick.priceId_Specified(Index: Integer): boolean;
begin
  Result := FpriceId_Specified;
end;

procedure PWSTiTariffForStick.SetepTariff(Index: Integer; const ABoolean: Boolean);
begin
  FepTariff := ABoolean;
  FepTariff_Specified := True;
end;

function PWSTiTariffForStick.epTariff_Specified(Index: Integer): boolean;
begin
  Result := FepTariff_Specified;
end;

procedure PWSTiTariffForStick.SetkasaTariff(Index: Integer; const ABoolean: Boolean);
begin
  FkasaTariff := ABoolean;
  FkasaTariff_Specified := True;
end;

function PWSTiTariffForStick.kasaTariff_Specified(Index: Integer): boolean;
begin
  Result := FkasaTariff_Specified;
end;

procedure PWSTiTariffForStick.SethoursToStartB(Index: Integer; const AInt64: Int64);
begin
  FhoursToStartB := AInt64;
  FhoursToStartB_Specified := True;
end;

function PWSTiTariffForStick.hoursToStartB_Specified(Index: Integer): boolean;
begin
  Result := FhoursToStartB_Specified;
end;

procedure PWSTiTariffForStick.SethoursToStartE(Index: Integer; const AInt64: Int64);
begin
  FhoursToStartE := AInt64;
  FhoursToStartE_Specified := True;
end;

function PWSTiTariffForStick.hoursToStartE_Specified(Index: Integer): boolean;
begin
  Result := FhoursToStartE_Specified;
end;

procedure PWSTiTariffForStick.SetbackTariff(Index: Integer; const ABoolean: Boolean);
begin
  FbackTariff := ABoolean;
  FbackTariff_Specified := True;
end;

function PWSTiTariffForStick.backTariff_Specified(Index: Integer): boolean;
begin
  Result := FbackTariff_Specified;
end;

procedure PWSTiTariffForStick.SetreturnMoneyHours(Index: Integer; const AInt64: Int64);
begin
  FreturnMoneyHours := AInt64;
  FreturnMoneyHours_Specified := True;
end;

function PWSTiTariffForStick.returnMoneyHours_Specified(Index: Integer): boolean;
begin
  Result := FreturnMoneyHours_Specified;
end;

procedure PWSTiTariffForStick.SetreturnMoneyPercent(Index: Integer; const ASingle: Single);
begin
  FreturnMoneyPercent := ASingle;
  FreturnMoneyPercent_Specified := True;
end;

function PWSTiTariffForStick.returnMoneyPercent_Specified(Index: Integer): boolean;
begin
  Result := FreturnMoneyPercent_Specified;
end;

procedure PWSTiTariffForStick.SetpayerMonthNo(Index: Integer; const AInteger: Integer);
begin
  FpayerMonthNo := AInteger;
  FpayerMonthNo_Specified := True;
end;

function PWSTiTariffForStick.payerMonthNo_Specified(Index: Integer): boolean;
begin
  Result := FpayerMonthNo_Specified;
end;

procedure PWSTiTariffForStick.SetpayerYearNo(Index: Integer; const AInteger: Integer);
begin
  FpayerYearNo := AInteger;
  FpayerYearNo_Specified := True;
end;

function PWSTiTariffForStick.payerYearNo_Specified(Index: Integer): boolean;
begin
  Result := FpayerYearNo_Specified;
end;

procedure PWSTiTariffForStick.SetpayerNoOr(Index: Integer; const ABoolean: Boolean);
begin
  FpayerNoOr := ABoolean;
  FpayerNoOr_Specified := True;
end;

function PWSTiTariffForStick.payerNoOr_Specified(Index: Integer): boolean;
begin
  Result := FpayerNoOr_Specified;
end;

procedure PWSTiTariffForStick.SetpayerMonthVal(Index: Integer; const ASingle: Single);
begin
  FpayerMonthVal := ASingle;
  FpayerMonthVal_Specified := True;
end;

function PWSTiTariffForStick.payerMonthVal_Specified(Index: Integer): boolean;
begin
  Result := FpayerMonthVal_Specified;
end;

procedure PWSTiTariffForStick.SetpayerYearVal(Index: Integer; const ASingle: Single);
begin
  FpayerYearVal := ASingle;
  FpayerYearVal_Specified := True;
end;

function PWSTiTariffForStick.payerYearVal_Specified(Index: Integer): boolean;
begin
  Result := FpayerYearVal_Specified;
end;

procedure PWSTiTariffForStick.SetpayerValOr(Index: Integer; const ABoolean: Boolean);
begin
  FpayerValOr := ABoolean;
  FpayerValOr_Specified := True;
end;

function PWSTiTariffForStick.payerValOr_Specified(Index: Integer): boolean;
begin
  Result := FpayerValOr_Specified;
end;

procedure PWSTiTariffForStick.SetholderMonthNo(Index: Integer; const AInteger: Integer);
begin
  FholderMonthNo := AInteger;
  FholderMonthNo_Specified := True;
end;

function PWSTiTariffForStick.holderMonthNo_Specified(Index: Integer): boolean;
begin
  Result := FholderMonthNo_Specified;
end;

procedure PWSTiTariffForStick.SetholderYearNo(Index: Integer; const AInteger: Integer);
begin
  FholderYearNo := AInteger;
  FholderYearNo_Specified := True;
end;

function PWSTiTariffForStick.holderYearNo_Specified(Index: Integer): boolean;
begin
  Result := FholderYearNo_Specified;
end;

procedure PWSTiTariffForStick.SetholderNoOr(Index: Integer; const ABoolean: Boolean);
begin
  FholderNoOr := ABoolean;
  FholderNoOr_Specified := True;
end;

function PWSTiTariffForStick.holderNoOr_Specified(Index: Integer): boolean;
begin
  Result := FholderNoOr_Specified;
end;

procedure PWSTiTariffForStick.SetholderMonthVal(Index: Integer; const ASingle: Single);
begin
  FholderMonthVal := ASingle;
  FholderMonthVal_Specified := True;
end;

function PWSTiTariffForStick.holderMonthVal_Specified(Index: Integer): boolean;
begin
  Result := FholderMonthVal_Specified;
end;

procedure PWSTiTariffForStick.SetholderYearVal(Index: Integer; const ASingle: Single);
begin
  FholderYearVal := ASingle;
  FholderYearVal_Specified := True;
end;

function PWSTiTariffForStick.holderYearVal_Specified(Index: Integer): boolean;
begin
  Result := FholderYearVal_Specified;
end;

procedure PWSTiTariffForStick.SetholderValOr(Index: Integer; const ABoolean: Boolean);
begin
  FholderValOr := ABoolean;
  FholderValOr_Specified := True;
end;

function PWSTiTariffForStick.holderValOr_Specified(Index: Integer): boolean;
begin
  Result := FholderValOr_Specified;
end;

procedure PWSTiTariffForStick.Setlegal(Index: Integer; const ABoolean: Boolean);
begin
  Flegal := ABoolean;
  Flegal_Specified := True;
end;

function PWSTiTariffForStick.legal_Specified(Index: Integer): boolean;
begin
  Result := Flegal_Specified;
end;

procedure PWSTiTariffForStick.SetnotGovDiscountValid(Index: Integer; const ABoolean: Boolean);
begin
  FnotGovDiscountValid := ABoolean;
  FnotGovDiscountValid_Specified := True;
end;

function PWSTiTariffForStick.notGovDiscountValid_Specified(Index: Integer): boolean;
begin
  Result := FnotGovDiscountValid_Specified;
end;

procedure PWSTiTariffForStick.SetsmsSendTypeEnable(Index: Integer; const ABoolean: Boolean);
begin
  FsmsSendTypeEnable := ABoolean;
  FsmsSendTypeEnable_Specified := True;
end;

function PWSTiTariffForStick.smsSendTypeEnable_Specified(Index: Integer): boolean;
begin
  Result := FsmsSendTypeEnable_Specified;
end;

procedure PWSTiTariffForStick.Setprice(Index: Integer; const AArray_Of_price: Array_Of_price);
begin
  Fprice := AArray_Of_price;
  Fprice_Specified := True;
end;

function PWSTiTariffForStick.price_Specified(Index: Integer): boolean;
begin
  Result := Fprice_Specified;
end;

procedure PWSTiTariffForStick.SetlagguageDescription(Index: Integer; const Astring: string);
begin
  FlagguageDescription := Astring;
  FlagguageDescription_Specified := True;
end;

function PWSTiTariffForStick.lagguageDescription_Specified(Index: Integer): boolean;
begin
  Result := FlagguageDescription_Specified;
end;

procedure PWSTiTariffForStick.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSTiTariffForStick.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSTiTariffForStick.SettariffType(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  FtariffType := APWSEnumParam;
  FtariffType_Specified := True;
end;

function PWSTiTariffForStick.tariffType_Specified(Index: Integer): boolean;
begin
  Result := FtariffType_Specified;
end;

procedure PWSTiTariffForStick.SettariffTypeCode(Index: Integer; const Astring: string);
begin
  FtariffTypeCode := Astring;
  FtariffTypeCode_Specified := True;
end;

function PWSTiTariffForStick.tariffTypeCode_Specified(Index: Integer): boolean;
begin
  Result := FtariffTypeCode_Specified;
end;

destructor PWSCosts.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FttPeriod)-1 do
    SysUtils.FreeAndNil(FttPeriod[I]);
  System.SetLength(FttPeriod, 0);
  for I := 0 to System.Length(FconnPeriod)-1 do
    SysUtils.FreeAndNil(FconnPeriod[I]);
  System.SetLength(FconnPeriod, 0);
  for I := 0 to System.Length(FaddConnPeriod)-1 do
    SysUtils.FreeAndNil(FaddConnPeriod[I]);
  System.SetLength(FaddConnPeriod, 0);
  inherited Destroy;
end;

procedure PWSCosts.SetttPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
begin
  FttPeriod := AArray_Of_PWSCostForPeriod;
  FttPeriod_Specified := True;
end;

function PWSCosts.ttPeriod_Specified(Index: Integer): boolean;
begin
  Result := FttPeriod_Specified;
end;

procedure PWSCosts.SetconnPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
begin
  FconnPeriod := AArray_Of_PWSCostForPeriod;
  FconnPeriod_Specified := True;
end;

function PWSCosts.connPeriod_Specified(Index: Integer): boolean;
begin
  Result := FconnPeriod_Specified;
end;

procedure PWSCosts.SetaddConnPeriod(Index: Integer; const AArray_Of_PWSCostForPeriod: Array_Of_PWSCostForPeriod);
begin
  FaddConnPeriod := AArray_Of_PWSCostForPeriod;
  FaddConnPeriod_Specified := True;
end;

function PWSCosts.addConnPeriod_Specified(Index: Integer): boolean;
begin
  Result := FaddConnPeriod_Specified;
end;

destructor PWSCarrierSearcherParams.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FcarrierId)-1 do
    SysUtils.FreeAndNil(FcarrierId[I]);
  System.SetLength(FcarrierId, 0);
  inherited Destroy;
end;

procedure PWSCarrierSearcherParams.SetprovinceId(Index: Integer; const AInt64: Int64);
begin
  FprovinceId := AInt64;
  FprovinceId_Specified := True;
end;

function PWSCarrierSearcherParams.provinceId_Specified(Index: Integer): boolean;
begin
  Result := FprovinceId_Specified;
end;

procedure PWSCarrierSearcherParams.SetdistrictId(Index: Integer; const AInt64: Int64);
begin
  FdistrictId := AInt64;
  FdistrictId_Specified := True;
end;

function PWSCarrierSearcherParams.districtId_Specified(Index: Integer): boolean;
begin
  Result := FdistrictId_Specified;
end;

procedure PWSCarrierSearcherParams.SetcommuneId(Index: Integer; const AInt64: Int64);
begin
  FcommuneId := AInt64;
  FcommuneId_Specified := True;
end;

function PWSCarrierSearcherParams.communeId_Specified(Index: Integer): boolean;
begin
  Result := FcommuneId_Specified;
end;

procedure PWSCarrierSearcherParams.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function PWSCarrierSearcherParams.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure PWSCarrierSearcherParams.SetcarrierTypeId(Index: Integer; const AInt64: Int64);
begin
  FcarrierTypeId := AInt64;
  FcarrierTypeId_Specified := True;
end;

function PWSCarrierSearcherParams.carrierTypeId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierTypeId_Specified;
end;

procedure PWSCarrierSearcherParams.SetnameFilter(Index: Integer; const Astring: string);
begin
  FnameFilter := Astring;
  FnameFilter_Specified := True;
end;

function PWSCarrierSearcherParams.nameFilter_Specified(Index: Integer): boolean;
begin
  Result := FnameFilter_Specified;
end;

procedure PWSCarrierSearcherParams.SetcarrierId(Index: Integer; const AArray_Of_PWSCarrierId: Array_Of_PWSCarrierId);
begin
  FcarrierId := AArray_Of_PWSCarrierId;
  FcarrierId_Specified := True;
end;

function PWSCarrierSearcherParams.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

destructor order.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fticket)-1 do
    SysUtils.FreeAndNil(Fticket[I]);
  System.SetLength(Fticket, 0);
  for I := 0 to System.Length(FperiodicTicket)-1 do
    SysUtils.FreeAndNil(FperiodicTicket[I]);
  System.SetLength(FperiodicTicket, 0);
  SysUtils.FreeAndNil(FsendingData);
  inherited Destroy;
end;

procedure order.Setticket(Index: Integer; const AArray_Of_ticket: Array_Of_ticket);
begin
  Fticket := AArray_Of_ticket;
  Fticket_Specified := True;
end;

function order.ticket_Specified(Index: Integer): boolean;
begin
  Result := Fticket_Specified;
end;

procedure order.SetperiodicTicket(Index: Integer; const AArray_Of_periodicTicket: Array_Of_periodicTicket);
begin
  FperiodicTicket := AArray_Of_periodicTicket;
  FperiodicTicket_Specified := True;
end;

function order.periodicTicket_Specified(Index: Integer): boolean;
begin
  Result := FperiodicTicket_Specified;
end;

procedure order.SetsendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
begin
  FsendingData := APWSTiSendingData;
  FsendingData_Specified := True;
end;

function order.sendingData_Specified(Index: Integer): boolean;
begin
  Result := FsendingData_Specified;
end;

destructor ticket.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fplace)-1 do
    SysUtils.FreeAndNil(Fplace[I]);
  System.SetLength(Fplace, 0);
  SysUtils.FreeAndNil(FgoDate);
  SysUtils.FreeAndNil(FconnectionDate);
  SysUtils.FreeAndNil(FmainHolderData);
  inherited Destroy;
end;

procedure ticket.SetpriceId(Index: Integer; const AInt64: Int64);
begin
  FpriceId := AInt64;
  FpriceId_Specified := True;
end;

function ticket.priceId_Specified(Index: Integer): boolean;
begin
  Result := FpriceId_Specified;
end;

procedure ticket.SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FgoDate := ATXSDateTime;
  FgoDate_Specified := True;
end;

function ticket.goDate_Specified(Index: Integer): boolean;
begin
  Result := FgoDate_Specified;
end;

procedure ticket.SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionDate := ATXSDateTime;
  FconnectionDate_Specified := True;
end;

function ticket.connectionDate_Specified(Index: Integer): boolean;
begin
  Result := FconnectionDate_Specified;
end;

procedure ticket.SetwithHolder(Index: Integer; const ABoolean: Boolean);
begin
  FwithHolder := ABoolean;
  FwithHolder_Specified := True;
end;

function ticket.withHolder_Specified(Index: Integer): boolean;
begin
  Result := FwithHolder_Specified;
end;

procedure ticket.SetmainHolderData(Index: Integer; const APWSTiHolderForTicket: PWSTiHolderForTicket);
begin
  FmainHolderData := APWSTiHolderForTicket;
  FmainHolderData_Specified := True;
end;

function ticket.mainHolderData_Specified(Index: Integer): boolean;
begin
  Result := FmainHolderData_Specified;
end;

procedure ticket.Setplace(Index: Integer; const AArray_Of_place: Array_Of_place);
begin
  Fplace := AArray_Of_place;
  Fplace_Specified := True;
end;

function ticket.place_Specified(Index: Integer): boolean;
begin
  Result := Fplace_Specified;
end;

destructor PWSFullyQualifiedCityWithStops.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fstop)-1 do
    SysUtils.FreeAndNil(Fstop[I]);
  System.SetLength(Fstop, 0);
  SysUtils.FreeAndNil(Fcity);
  inherited Destroy;
end;

procedure PWSFullyQualifiedCityWithStops.Setstop(Index: Integer; const AArray_Of_PWSStop: Array_Of_PWSStop);
begin
  Fstop := AArray_Of_PWSStop;
  Fstop_Specified := True;
end;

function PWSFullyQualifiedCityWithStops.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

procedure PWSFullyQualifiedCityWithStops.Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  Fcity := APWSFullyQualifiedCity;
  Fcity_Specified := True;
end;

function PWSFullyQualifiedCityWithStops.city_Specified(Index: Integer): boolean;
begin
  Result := Fcity_Specified;
end;

procedure PWSFullyQualifiedCityWithStops.SetcommuneName(Index: Integer; const Astring: string);
begin
  FcommuneName := Astring;
  FcommuneName_Specified := True;
end;

function PWSFullyQualifiedCityWithStops.communeName_Specified(Index: Integer): boolean;
begin
  Result := FcommuneName_Specified;
end;

procedure PWSFullyQualifiedCityWithStops.SetdistrictName(Index: Integer; const Astring: string);
begin
  FdistrictName := Astring;
  FdistrictName_Specified := True;
end;

function PWSFullyQualifiedCityWithStops.districtName_Specified(Index: Integer): boolean;
begin
  Result := FdistrictName_Specified;
end;

procedure PWSFullyQualifiedCityWithStops.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PWSFullyQualifiedCityWithStops.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PWSFullyQualifiedCityWithStops.SetprovinceName(Index: Integer; const Astring: string);
begin
  FprovinceName := Astring;
  FprovinceName_Specified := True;
end;

function PWSFullyQualifiedCityWithStops.provinceName_Specified(Index: Integer): boolean;
begin
  Result := FprovinceName_Specified;
end;

destructor cityStop.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fstop)-1 do
    SysUtils.FreeAndNil(Fstop[I]);
  System.SetLength(Fstop, 0);
  SysUtils.FreeAndNil(Fcity);
  inherited Destroy;
end;

procedure cityStop.Setstop(Index: Integer; const AArray_Of_PWSStop: Array_Of_PWSStop);
begin
  Fstop := AArray_Of_PWSStop;
  Fstop_Specified := True;
end;

function cityStop.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

procedure cityStop.Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  Fcity := APWSFullyQualifiedCity;
  Fcity_Specified := True;
end;

function cityStop.city_Specified(Index: Integer): boolean;
begin
  Result := Fcity_Specified;
end;

destructor PWSTiPeriodicTicketLineInfo.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fsection)-1 do
    SysUtils.FreeAndNil(Fsection[I]);
  System.SetLength(Fsection, 0);
  SysUtils.FreeAndNil(FvaildFromTime);
  SysUtils.FreeAndNil(FvaildToTime);
  SysUtils.FreeAndNil(Ftype_);
  inherited Destroy;
end;

procedure PWSTiPeriodicTicketLineInfo.SetvaildFromTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvaildFromTime := ATXSDateTime;
  FvaildFromTime_Specified := True;
end;

function PWSTiPeriodicTicketLineInfo.vaildFromTime_Specified(Index: Integer): boolean;
begin
  Result := FvaildFromTime_Specified;
end;

procedure PWSTiPeriodicTicketLineInfo.SetvaildToTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FvaildToTime := ATXSDateTime;
  FvaildToTime_Specified := True;
end;

function PWSTiPeriodicTicketLineInfo.vaildToTime_Specified(Index: Integer): boolean;
begin
  Result := FvaildToTime_Specified;
end;

procedure PWSTiPeriodicTicketLineInfo.Setsection(Index: Integer; const AArray_Of_section: Array_Of_section);
begin
  Fsection := AArray_Of_section;
  Fsection_Specified := True;
end;

function PWSTiPeriodicTicketLineInfo.section_Specified(Index: Integer): boolean;
begin
  Result := Fsection_Specified;
end;

procedure PWSTiPeriodicTicketLineInfo.Settype_(Index: Integer; const APWSEnumParam: PWSEnumParam);
begin
  Ftype_ := APWSEnumParam;
  Ftype__Specified := True;
end;

function PWSTiPeriodicTicketLineInfo.type__Specified(Index: Integer): boolean;
begin
  Result := Ftype__Specified;
end;

destructor PWSTiSendNormalTicketData.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fpassenger)-1 do
    SysUtils.FreeAndNil(Fpassenger[I]);
  System.SetLength(Fpassenger, 0);
  SysUtils.FreeAndNil(FconnectionDate);
  SysUtils.FreeAndNil(FconnectionTime);
  SysUtils.FreeAndNil(FcommitTimestamp);
  SysUtils.FreeAndNil(FdocType);
  inherited Destroy;
end;

procedure PWSTiSendNormalTicketData.SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionDate := ATXSDateTime;
  FconnectionDate_Specified := True;
end;

function PWSTiSendNormalTicketData.connectionDate_Specified(Index: Integer): boolean;
begin
  Result := FconnectionDate_Specified;
end;

procedure PWSTiSendNormalTicketData.SetconnectionTime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionTime := ATXSDateTime;
  FconnectionTime_Specified := True;
end;

function PWSTiSendNormalTicketData.connectionTime_Specified(Index: Integer): boolean;
begin
  Result := FconnectionTime_Specified;
end;

procedure PWSTiSendNormalTicketData.SetcommitTimestamp(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FcommitTimestamp := ATXSDateTime;
  FcommitTimestamp_Specified := True;
end;

function PWSTiSendNormalTicketData.commitTimestamp_Specified(Index: Integer): boolean;
begin
  Result := FcommitTimestamp_Specified;
end;

procedure PWSTiSendNormalTicketData.SetnrKursu(Index: Integer; const AInt64: Int64);
begin
  FnrKursu := AInt64;
  FnrKursu_Specified := True;
end;

function PWSTiSendNormalTicketData.nrKursu_Specified(Index: Integer): boolean;
begin
  Result := FnrKursu_Specified;
end;

procedure PWSTiSendNormalTicketData.SetwithHolderData(Index: Integer; const ABoolean: Boolean);
begin
  FwithHolderData := ABoolean;
  FwithHolderData_Specified := True;
end;

function PWSTiSendNormalTicketData.withHolderData_Specified(Index: Integer): boolean;
begin
  Result := FwithHolderData_Specified;
end;

procedure PWSTiSendNormalTicketData.SetgrossPrice(Index: Integer; const ASingle: Single);
begin
  FgrossPrice := ASingle;
  FgrossPrice_Specified := True;
end;

function PWSTiSendNormalTicketData.grossPrice_Specified(Index: Integer): boolean;
begin
  Result := FgrossPrice_Specified;
end;

procedure PWSTiSendNormalTicketData.SetvatValue(Index: Integer; const ASingle: Single);
begin
  FvatValue := ASingle;
  FvatValue_Specified := True;
end;

function PWSTiSendNormalTicketData.vatValue_Specified(Index: Integer): boolean;
begin
  Result := FvatValue_Specified;
end;

procedure PWSTiSendNormalTicketData.SetvatRate(Index: Integer; const ASingle: Single);
begin
  FvatRate := ASingle;
  FvatRate_Specified := True;
end;

function PWSTiSendNormalTicketData.vatRate_Specified(Index: Integer): boolean;
begin
  Result := FvatRate_Specified;
end;

procedure PWSTiSendNormalTicketData.SetfromCityName(Index: Integer; const Astring: string);
begin
  FfromCityName := Astring;
  FfromCityName_Specified := True;
end;

function PWSTiSendNormalTicketData.fromCityName_Specified(Index: Integer): boolean;
begin
  Result := FfromCityName_Specified;
end;

procedure PWSTiSendNormalTicketData.SettoCityName(Index: Integer; const Astring: string);
begin
  FtoCityName := Astring;
  FtoCityName_Specified := True;
end;

function PWSTiSendNormalTicketData.toCityName_Specified(Index: Integer): boolean;
begin
  Result := FtoCityName_Specified;
end;

procedure PWSTiSendNormalTicketData.SetfromStopName(Index: Integer; const Astring: string);
begin
  FfromStopName := Astring;
  FfromStopName_Specified := True;
end;

function PWSTiSendNormalTicketData.fromStopName_Specified(Index: Integer): boolean;
begin
  Result := FfromStopName_Specified;
end;

procedure PWSTiSendNormalTicketData.SettoStopName(Index: Integer; const Astring: string);
begin
  FtoStopName := Astring;
  FtoStopName_Specified := True;
end;

function PWSTiSendNormalTicketData.toStopName_Specified(Index: Integer): boolean;
begin
  Result := FtoStopName_Specified;
end;

procedure PWSTiSendNormalTicketData.SetfromRelationName(Index: Integer; const Astring: string);
begin
  FfromRelationName := Astring;
  FfromRelationName_Specified := True;
end;

function PWSTiSendNormalTicketData.fromRelationName_Specified(Index: Integer): boolean;
begin
  Result := FfromRelationName_Specified;
end;

procedure PWSTiSendNormalTicketData.SettoRelationName(Index: Integer; const Astring: string);
begin
  FtoRelationName := Astring;
  FtoRelationName_Specified := True;
end;

function PWSTiSendNormalTicketData.toRelationName_Specified(Index: Integer): boolean;
begin
  Result := FtoRelationName_Specified;
end;

procedure PWSTiSendNormalTicketData.SetcarrierName(Index: Integer; const Astring: string);
begin
  FcarrierName := Astring;
  FcarrierName_Specified := True;
end;

function PWSTiSendNormalTicketData.carrierName_Specified(Index: Integer): boolean;
begin
  Result := FcarrierName_Specified;
end;

procedure PWSTiSendNormalTicketData.SetdocType(Index: Integer; const APWSTiDocType: PWSTiDocType);
begin
  FdocType := APWSTiDocType;
  FdocType_Specified := True;
end;

function PWSTiSendNormalTicketData.docType_Specified(Index: Integer): boolean;
begin
  Result := FdocType_Specified;
end;

procedure PWSTiSendNormalTicketData.SetidDocValue(Index: Integer; const Astring: string);
begin
  FidDocValue := Astring;
  FidDocValue_Specified := True;
end;

function PWSTiSendNormalTicketData.idDocValue_Specified(Index: Integer): boolean;
begin
  Result := FidDocValue_Specified;
end;

procedure PWSTiSendNormalTicketData.Setsurname(Index: Integer; const Astring: string);
begin
  Fsurname := Astring;
  Fsurname_Specified := True;
end;

function PWSTiSendNormalTicketData.surname_Specified(Index: Integer): boolean;
begin
  Result := Fsurname_Specified;
end;

procedure PWSTiSendNormalTicketData.Setforename(Index: Integer; const Astring: string);
begin
  Fforename := Astring;
  Fforename_Specified := True;
end;

function PWSTiSendNormalTicketData.forename_Specified(Index: Integer): boolean;
begin
  Result := Fforename_Specified;
end;

procedure PWSTiSendNormalTicketData.SetticketLoginCode(Index: Integer; const Astring: string);
begin
  FticketLoginCode := Astring;
  FticketLoginCode_Specified := True;
end;

function PWSTiSendNormalTicketData.ticketLoginCode_Specified(Index: Integer): boolean;
begin
  Result := FticketLoginCode_Specified;
end;

procedure PWSTiSendNormalTicketData.SetticketCodeToVerify(Index: Integer; const Astring: string);
begin
  FticketCodeToVerify := Astring;
  FticketCodeToVerify_Specified := True;
end;

function PWSTiSendNormalTicketData.ticketCodeToVerify_Specified(Index: Integer): boolean;
begin
  Result := FticketCodeToVerify_Specified;
end;

procedure PWSTiSendNormalTicketData.Setpassenger(Index: Integer; const AArray_Of_passenger: Array_Of_passenger);
begin
  Fpassenger := AArray_Of_passenger;
  Fpassenger_Specified := True;
end;

function PWSTiSendNormalTicketData.passenger_Specified(Index: Integer): boolean;
begin
  Result := Fpassenger_Specified;
end;

procedure PWSTiSendNormalTicketData.SetluggageNumber(Index: Integer; const Astring: string);
begin
  FluggageNumber := Astring;
  FluggageNumber_Specified := True;
end;

function PWSTiSendNormalTicketData.luggageNumber_Specified(Index: Integer): boolean;
begin
  Result := FluggageNumber_Specified;
end;

destructor placeCause.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FPWSEnumParam)-1 do
    SysUtils.FreeAndNil(FPWSEnumParam[I]);
  System.SetLength(FPWSEnumParam, 0);
  inherited Destroy;
end;

procedure placeCause.SetfreePlaces(Index: Integer; const AInteger: Integer);
begin
  FfreePlaces := AInteger;
  FfreePlaces_Specified := True;
end;

function placeCause.freePlaces_Specified(Index: Integer): boolean;
begin
  Result := FfreePlaces_Specified;
end;

procedure placeCause.SetPWSEnumParam(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FPWSEnumParam := AArray_Of_PWSEnumParam;
  FPWSEnumParam_Specified := True;
end;

function placeCause.PWSEnumParam_Specified(Index: Integer): boolean;
begin
  Result := FPWSEnumParam_Specified;
end;

destructor PWSTiTicketUnavailableFaultData.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FplaceCause)-1 do
    SysUtils.FreeAndNil(FplaceCause[I]);
  System.SetLength(FplaceCause, 0);
  for I := 0 to System.Length(FcommonCause)-1 do
    SysUtils.FreeAndNil(FcommonCause[I]);
  System.SetLength(FcommonCause, 0);
  inherited Destroy;
end;

procedure PWSTiTicketUnavailableFaultData.SetplaceCause(Index: Integer; const AArray_Of_placeCause: Array_Of_placeCause);
begin
  FplaceCause := AArray_Of_placeCause;
  FplaceCause_Specified := True;
end;

function PWSTiTicketUnavailableFaultData.placeCause_Specified(Index: Integer): boolean;
begin
  Result := FplaceCause_Specified;
end;

procedure PWSTiTicketUnavailableFaultData.SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FcommonCause := AArray_Of_PWSEnumParam;
  FcommonCause_Specified := True;
end;

function PWSTiTicketUnavailableFaultData.commonCause_Specified(Index: Integer): boolean;
begin
  Result := FcommonCause_Specified;
end;

procedure PWSGetStopParam.SetcityId(Index: Integer; const AInt64: Int64);
begin
  FcityId := AInt64;
  FcityId_Specified := True;
end;

function PWSGetStopParam.cityId_Specified(Index: Integer): boolean;
begin
  Result := FcityId_Specified;
end;

procedure PWSGetStopParam.SetcityName(Index: Integer; const Astring: string);
begin
  FcityName := Astring;
  FcityName_Specified := True;
end;

function PWSGetStopParam.cityName_Specified(Index: Integer): boolean;
begin
  Result := FcityName_Specified;
end;

procedure PWSGetStopParam.SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FcarrierId := AArray_Of_long;
  FcarrierId_Specified := True;
end;

function PWSGetStopParam.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

procedure PWSTiReservationCancelRange.SetreservationId(Index: Integer; const AInt64: Int64);
begin
  FreservationId := AInt64;
  FreservationId_Specified := True;
end;

function PWSTiReservationCancelRange.reservationId_Specified(Index: Integer): boolean;
begin
  Result := FreservationId_Specified;
end;

procedure PWSTiReservationCancelRange.SetticketId(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FticketId := AArray_Of_long;
  FticketId_Specified := True;
end;

function PWSTiReservationCancelRange.ticketId_Specified(Index: Integer): boolean;
begin
  Result := FticketId_Specified;
end;

procedure PWSTiReservationCancelRange.SetplacesId(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FplacesId := AArray_Of_long;
  FplacesId_Specified := True;
end;

function PWSTiReservationCancelRange.placesId_Specified(Index: Integer): boolean;
begin
  Result := FplacesId_Specified;
end;

destructor PWSSearchingParams.Destroy;
begin
  SysUtils.FreeAndNil(Fdate);
  SysUtils.FreeAndNil(Ftime);
  inherited Destroy;
end;

procedure PWSSearchingParams.SetfromStopId(Index: Integer; const AInt64: Int64);
begin
  FfromStopId := AInt64;
  FfromStopId_Specified := True;
end;

function PWSSearchingParams.fromStopId_Specified(Index: Integer): boolean;
begin
  Result := FfromStopId_Specified;
end;

procedure PWSSearchingParams.SettoStopId(Index: Integer; const AInt64: Int64);
begin
  FtoStopId := AInt64;
  FtoStopId_Specified := True;
end;

function PWSSearchingParams.toStopId_Specified(Index: Integer): boolean;
begin
  Result := FtoStopId_Specified;
end;

procedure PWSSearchingParams.Setdate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Fdate := ATXSDateTime;
  Fdate_Specified := True;
end;

function PWSSearchingParams.date_Specified(Index: Integer): boolean;
begin
  Result := Fdate_Specified;
end;

procedure PWSSearchingParams.Settime(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  Ftime := ATXSDateTime;
  Ftime_Specified := True;
end;

function PWSSearchingParams.time_Specified(Index: Integer): boolean;
begin
  Result := Ftime_Specified;
end;

procedure PWSSearchingParams.SetfromCityId(Index: Integer; const AInt64: Int64);
begin
  FfromCityId := AInt64;
  FfromCityId_Specified := True;
end;

function PWSSearchingParams.fromCityId_Specified(Index: Integer): boolean;
begin
  Result := FfromCityId_Specified;
end;

procedure PWSSearchingParams.SettoCityId(Index: Integer; const AInt64: Int64);
begin
  FtoCityId := AInt64;
  FtoCityId_Specified := True;
end;

function PWSSearchingParams.toCityId_Specified(Index: Integer): boolean;
begin
  Result := FtoCityId_Specified;
end;

procedure PWSSearchingParams.SetsellingTickets(Index: Integer; const ABoolean: Boolean);
begin
  FsellingTickets := ABoolean;
  FsellingTickets_Specified := True;
end;

function PWSSearchingParams.sellingTickets_Specified(Index: Integer): boolean;
begin
  Result := FsellingTickets_Specified;
end;

procedure PWSSearchingParams.SetoptimizationMode(Index: Integer; const AoptimizationMode: optimizationMode);
begin
  FoptimizationMode := AoptimizationMode;
  FoptimizationMode_Specified := True;
end;

function PWSSearchingParams.optimizationMode_Specified(Index: Integer): boolean;
begin
  Result := FoptimizationMode_Specified;
end;

procedure PWSSearchingParams.SetcarrierType(Index: Integer; const AcarrierType: carrierType);
begin
  FcarrierType := AcarrierType;
  FcarrierType_Specified := True;
end;

function PWSSearchingParams.carrierType_Specified(Index: Integer): boolean;
begin
  Result := FcarrierType_Specified;
end;

procedure PWSSearchingParams.SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FcarrierId := AArray_Of_long;
  FcarrierId_Specified := True;
end;

function PWSSearchingParams.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

procedure PWSSearchingParams.SetfilterCode(Index: Integer; const Astring: string);
begin
  FfilterCode := Astring;
  FfilterCode_Specified := True;
end;

function PWSSearchingParams.filterCode_Specified(Index: Integer): boolean;
begin
  Result := FfilterCode_Specified;
end;

destructor PWSTiWebServiceUserSellingConfig.Destroy;
begin
  SysUtils.FreeAndNil(FmachineConfig);
  inherited Destroy;
end;

procedure PWSTiWebServiceUserSellingConfig.SetdistributorId(Index: Integer; const AInt64: Int64);
begin
  FdistributorId := AInt64;
  FdistributorId_Specified := True;
end;

function PWSTiWebServiceUserSellingConfig.distributorId_Specified(Index: Integer): boolean;
begin
  Result := FdistributorId_Specified;
end;

procedure PWSTiWebServiceUserSellingConfig.SetmachineConfig(Index: Integer; const AmachineConfig: machineConfig);
begin
  FmachineConfig := AmachineConfig;
  FmachineConfig_Specified := True;
end;

function PWSTiWebServiceUserSellingConfig.machineConfig_Specified(Index: Integer): boolean;
begin
  Result := FmachineConfig_Specified;
end;

procedure PWSTiWebServiceUserSellingConfig.SetcarrierId(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FcarrierId := AArray_Of_long;
  FcarrierId_Specified := True;
end;

function PWSTiWebServiceUserSellingConfig.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

procedure carriers.SetvendingMachineId(Index: Integer; const AInt64: Int64);
begin
  FvendingMachineId := AInt64;
  FvendingMachineId_Specified := True;
end;

function carriers.vendingMachineId_Specified(Index: Integer): boolean;
begin
  Result := FvendingMachineId_Specified;
end;

procedure carriers.SetshowAllCarriers(Index: Integer; const ABoolean: Boolean);
begin
  FshowAllCarriers := ABoolean;
  FshowAllCarriers_Specified := True;
end;

function carriers.showAllCarriers_Specified(Index: Integer): boolean;
begin
  Result := FshowAllCarriers_Specified;
end;

procedure carriers.SetsellAllCarriers(Index: Integer; const ABoolean: Boolean);
begin
  FsellAllCarriers := ABoolean;
  FsellAllCarriers_Specified := True;
end;

function carriers.sellAllCarriers_Specified(Index: Integer): boolean;
begin
  Result := FsellAllCarriers_Specified;
end;

procedure carriers.SetshowCarrier(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FshowCarrier := AArray_Of_long;
  FshowCarrier_Specified := True;
end;

function carriers.showCarrier_Specified(Index: Integer): boolean;
begin
  Result := FshowCarrier_Specified;
end;

procedure carriers.SetsellCarrier(Index: Integer; const AArray_Of_long: Array_Of_long);
begin
  FsellCarrier := AArray_Of_long;
  FsellCarrier_Specified := True;
end;

function carriers.sellCarrier_Specified(Index: Integer): boolean;
begin
  Result := FsellCarrier_Specified;
end;

destructor PWSTiSearchingResultWithSellingData.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fresult)-1 do
    SysUtils.FreeAndNil(Fresult[I]);
  System.SetLength(Fresult, 0);
  inherited Destroy;
end;

procedure PWSTiSearchingResultWithSellingData.Setresult(Index: Integer; const AArray_Of_result: Array_Of_result);
begin
  Fresult := AArray_Of_result;
  Fresult_Specified := True;
end;

function PWSTiSearchingResultWithSellingData.result_Specified(Index: Integer): boolean;
begin
  Result := Fresult_Specified;
end;

procedure PWSTiSearchingResultWithSellingData.SetresultsId(Index: Integer; const Astring: string);
begin
  FresultsId := Astring;
  FresultsId_Specified := True;
end;

function PWSTiSearchingResultWithSellingData.resultsId_Specified(Index: Integer): boolean;
begin
  Result := FresultsId_Specified;
end;

destructor result2.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fstick)-1 do
    SysUtils.FreeAndNil(Fstick[I]);
  System.SetLength(Fstick, 0);
  SysUtils.FreeAndNil(FgoDate);
  SysUtils.FreeAndNil(FconnectionDate);
  inherited Destroy;
end;

procedure result2.SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FgoDate := ATXSDateTime;
  FgoDate_Specified := True;
end;

function result2.goDate_Specified(Index: Integer): boolean;
begin
  Result := FgoDate_Specified;
end;

procedure result2.SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionDate := ATXSDateTime;
  FconnectionDate_Specified := True;
end;

function result2.connectionDate_Specified(Index: Integer): boolean;
begin
  Result := FconnectionDate_Specified;
end;

procedure result2.SetsystemLocked(Index: Integer; const ABoolean: Boolean);
begin
  FsystemLocked := ABoolean;
  FsystemLocked_Specified := True;
end;

function result2.systemLocked_Specified(Index: Integer): boolean;
begin
  Result := FsystemLocked_Specified;
end;

procedure result2.SetresultCanBeBought(Index: Integer; const AInteger: Integer);
begin
  FresultCanBeBought := AInteger;
  FresultCanBeBought_Specified := True;
end;

function result2.resultCanBeBought_Specified(Index: Integer): boolean;
begin
  Result := FresultCanBeBought_Specified;
end;

procedure result2.Setstick(Index: Integer; const AArray_Of_stick: Array_Of_stick);
begin
  Fstick := AArray_Of_stick;
  Fstick_Specified := True;
end;

function result2.stick_Specified(Index: Integer): boolean;
begin
  Result := Fstick_Specified;
end;

destructor stick2.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FticketCause)-1 do
    SysUtils.FreeAndNil(FticketCause[I]);
  System.SetLength(FticketCause, 0);
  for I := 0 to System.Length(FplaceCause)-1 do
    SysUtils.FreeAndNil(FplaceCause[I]);
  System.SetLength(FplaceCause, 0);
  SysUtils.FreeAndNil(FsimpleStick);
  SysUtils.FreeAndNil(FrelationFrom);
  SysUtils.FreeAndNil(FrelationTo);
  inherited Destroy;
end;

procedure stick2.SetfreePlaces(Index: Integer; const AInteger: Integer);
begin
  FfreePlaces := AInteger;
  FfreePlaces_Specified := True;
end;

function stick2.freePlaces_Specified(Index: Integer): boolean;
begin
  Result := FfreePlaces_Specified;
end;

procedure stick2.Setsellable(Index: Integer; const ABoolean: Boolean);
begin
  Fsellable := ABoolean;
  Fsellable_Specified := True;
end;

function stick2.sellable_Specified(Index: Integer): boolean;
begin
  Result := Fsellable_Specified;
end;

procedure stick2.SetsimpleStick(Index: Integer; const APWSStick: PWSStick);
begin
  FsimpleStick := APWSStick;
  FsimpleStick_Specified := True;
end;

function stick2.simpleStick_Specified(Index: Integer): boolean;
begin
  Result := FsimpleStick_Specified;
end;

procedure stick2.SetsoldPlacesNumber(Index: Integer; const AArray_Of_int: Array_Of_int);
begin
  FsoldPlacesNumber := AArray_Of_int;
  FsoldPlacesNumber_Specified := True;
end;

function stick2.soldPlacesNumber_Specified(Index: Integer): boolean;
begin
  Result := FsoldPlacesNumber_Specified;
end;

procedure stick2.SetticketCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FticketCause := AArray_Of_PWSEnumParam;
  FticketCause_Specified := True;
end;

function stick2.ticketCause_Specified(Index: Integer): boolean;
begin
  Result := FticketCause_Specified;
end;

procedure stick2.SetplaceCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FplaceCause := AArray_Of_PWSEnumParam;
  FplaceCause_Specified := True;
end;

function stick2.placeCause_Specified(Index: Integer): boolean;
begin
  Result := FplaceCause_Specified;
end;

procedure stick2.SetrelationFrom(Index: Integer; const APWSStop: PWSStop);
begin
  FrelationFrom := APWSStop;
  FrelationFrom_Specified := True;
end;

function stick2.relationFrom_Specified(Index: Integer): boolean;
begin
  Result := FrelationFrom_Specified;
end;

procedure stick2.SetrelationTo(Index: Integer; const APWSStop: PWSStop);
begin
  FrelationTo := APWSStop;
  FrelationTo_Specified := True;
end;

function stick2.relationTo_Specified(Index: Integer): boolean;
begin
  Result := FrelationTo_Specified;
end;

destructor holdersForStick.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fholder)-1 do
    SysUtils.FreeAndNil(Fholder[I]);
  System.SetLength(Fholder, 0);
  SysUtils.FreeAndNil(FstickId);
  inherited Destroy;
end;

procedure holdersForStick.SetfromRouteSqNumber(Index: Integer; const AInt64: Int64);
begin
  FfromRouteSqNumber := AInt64;
  FfromRouteSqNumber_Specified := True;
end;

function holdersForStick.fromRouteSqNumber_Specified(Index: Integer): boolean;
begin
  Result := FfromRouteSqNumber_Specified;
end;

procedure holdersForStick.SettoRouteSqNumber(Index: Integer; const AInt64: Int64);
begin
  FtoRouteSqNumber := AInt64;
  FtoRouteSqNumber_Specified := True;
end;

function holdersForStick.toRouteSqNumber_Specified(Index: Integer): boolean;
begin
  Result := FtoRouteSqNumber_Specified;
end;

procedure holdersForStick.SetfromStopName(Index: Integer; const Astring: string);
begin
  FfromStopName := Astring;
  FfromStopName_Specified := True;
end;

function holdersForStick.fromStopName_Specified(Index: Integer): boolean;
begin
  Result := FfromStopName_Specified;
end;

procedure holdersForStick.SettoStopName(Index: Integer; const Astring: string);
begin
  FtoStopName := Astring;
  FtoStopName_Specified := True;
end;

function holdersForStick.toStopName_Specified(Index: Integer): boolean;
begin
  Result := FtoStopName_Specified;
end;

procedure holdersForStick.Setholder(Index: Integer; const AArray_Of_holder: Array_Of_holder);
begin
  Fholder := AArray_Of_holder;
  Fholder_Specified := True;
end;

function holdersForStick.holder_Specified(Index: Integer): boolean;
begin
  Result := Fholder_Specified;
end;

procedure holdersForStick.SetstickId(Index: Integer; const AstickId: stickId);
begin
  FstickId := AstickId;
  FstickId_Specified := True;
end;

function holdersForStick.stickId_Specified(Index: Integer): boolean;
begin
  Result := FstickId_Specified;
end;

destructor ticket2.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fplace)-1 do
    SysUtils.FreeAndNil(Fplace[I]);
  System.SetLength(Fplace, 0);
  SysUtils.FreeAndNil(FgoDate);
  SysUtils.FreeAndNil(FconnectionDate);
  SysUtils.FreeAndNil(Fconnection);
  SysUtils.FreeAndNil(Fholder);
  SysUtils.FreeAndNil(Ftariff);
  inherited Destroy;
end;

procedure ticket2.SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FgoDate := ATXSDateTime;
  FgoDate_Specified := True;
end;

function ticket2.goDate_Specified(Index: Integer): boolean;
begin
  Result := FgoDate_Specified;
end;

procedure ticket2.SetticketId(Index: Integer; const AInt64: Int64);
begin
  FticketId := AInt64;
  FticketId_Specified := True;
end;

function ticket2.ticketId_Specified(Index: Integer): boolean;
begin
  Result := FticketId_Specified;
end;

procedure ticket2.SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionDate := ATXSDateTime;
  FconnectionDate_Specified := True;
end;

function ticket2.connectionDate_Specified(Index: Integer): boolean;
begin
  Result := FconnectionDate_Specified;
end;

procedure ticket2.SetcurrentSellViaKasa(Index: Integer; const ABoolean: Boolean);
begin
  FcurrentSellViaKasa := ABoolean;
  FcurrentSellViaKasa_Specified := True;
end;

function ticket2.currentSellViaKasa_Specified(Index: Integer): boolean;
begin
  Result := FcurrentSellViaKasa_Specified;
end;

procedure ticket2.Setplace(Index: Integer; const AArray_Of_PTiPlace: Array_Of_PTiPlace);
begin
  Fplace := AArray_Of_PTiPlace;
  Fplace_Specified := True;
end;

function ticket2.place_Specified(Index: Integer): boolean;
begin
  Result := Fplace_Specified;
end;

procedure ticket2.Setconnection(Index: Integer; const Aconnection2: connection2);
begin
  Fconnection := Aconnection2;
  Fconnection_Specified := True;
end;

function ticket2.connection_Specified(Index: Integer): boolean;
begin
  Result := Fconnection_Specified;
end;

procedure ticket2.Setholder(Index: Integer; const Aholder3: holder3);
begin
  Fholder := Aholder3;
  Fholder_Specified := True;
end;

function ticket2.holder_Specified(Index: Integer): boolean;
begin
  Result := Fholder_Specified;
end;

procedure ticket2.Settariff(Index: Integer; const APTiTariffForStick: PTiTariffForStick);
begin
  Ftariff := APTiTariffForStick;
  Ftariff_Specified := True;
end;

function ticket2.tariff_Specified(Index: Integer): boolean;
begin
  Result := Ftariff_Specified;
end;

procedure ticket2.SetcodeToVerify(Index: Integer; const Astring: string);
begin
  FcodeToVerify := Astring;
  FcodeToVerify_Specified := True;
end;

function ticket2.codeToVerify_Specified(Index: Integer): boolean;
begin
  Result := FcodeToVerify_Specified;
end;

procedure ticket2.SetticketLoginCode(Index: Integer; const Astring: string);
begin
  FticketLoginCode := Astring;
  FticketLoginCode_Specified := True;
end;

function ticket2.ticketLoginCode_Specified(Index: Integer): boolean;
begin
  Result := FticketLoginCode_Specified;
end;

destructor holder4.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fplace)-1 do
    SysUtils.FreeAndNil(Fplace[I]);
  System.SetLength(Fplace, 0);
  SysUtils.FreeAndNil(FholderData);
  inherited Destroy;
end;

procedure holder4.SetgrossPriceBeforeDiscount(Index: Integer; const ASingle: Single);
begin
  FgrossPriceBeforeDiscount := ASingle;
  FgrossPriceBeforeDiscount_Specified := True;
end;

function holder4.grossPriceBeforeDiscount_Specified(Index: Integer): boolean;
begin
  Result := FgrossPriceBeforeDiscount_Specified;
end;

procedure holder4.SetholderData(Index: Integer; const APTiHolderForTicket: PTiHolderForTicket);
begin
  FholderData := APTiHolderForTicket;
  FholderData_Specified := True;
end;

function holder4.holderData_Specified(Index: Integer): boolean;
begin
  Result := FholderData_Specified;
end;

procedure holder4.SetcodeToVerifyForTicket(Index: Integer; const Astring: string);
begin
  FcodeToVerifyForTicket := Astring;
  FcodeToVerifyForTicket_Specified := True;
end;

function holder4.codeToVerifyForTicket_Specified(Index: Integer): boolean;
begin
  Result := FcodeToVerifyForTicket_Specified;
end;

procedure holder4.Setplace(Index: Integer; const AArray_Of_PTiPlace: Array_Of_PTiPlace);
begin
  Fplace := AArray_Of_PTiPlace;
  Fplace_Specified := True;
end;

function holder4.place_Specified(Index: Integer): boolean;
begin
  Result := Fplace_Specified;
end;

procedure holder4.SetticketLoginCode(Index: Integer; const Astring: string);
begin
  FticketLoginCode := Astring;
  FticketLoginCode_Specified := True;
end;

function holder4.ticketLoginCode_Specified(Index: Integer): boolean;
begin
  Result := FticketLoginCode_Specified;
end;

destructor PWSCarrierLines.Destroy;
begin
  SysUtils.FreeAndNil(FfromCity);
  SysUtils.FreeAndNil(FtoCity);
  SysUtils.FreeAndNil(FcarrierId);
  inherited Destroy;
end;

procedure PWSCarrierLines.SetfromCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FfromCity := APWSFullyQualifiedCity;
  FfromCity_Specified := True;
end;

function PWSCarrierLines.fromCity_Specified(Index: Integer): boolean;
begin
  Result := FfromCity_Specified;
end;

procedure PWSCarrierLines.SettoCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FtoCity := APWSFullyQualifiedCity;
  FtoCity_Specified := True;
end;

function PWSCarrierLines.toCity_Specified(Index: Integer): boolean;
begin
  Result := FtoCity_Specified;
end;

procedure PWSCarrierLines.Setline(Index: Integer; const AArray_Of_PWSCarrierLine: Array_Of_PWSCarrierLine);
begin
  Fline := AArray_Of_PWSCarrierLine;
  Fline_Specified := True;
end;

function PWSCarrierLines.line_Specified(Index: Integer): boolean;
begin
  Result := Fline_Specified;
end;

procedure PWSCarrierLines.SetcarrierId(Index: Integer; const APWSCarrierId: PWSCarrierId);
begin
  FcarrierId := APWSCarrierId;
  FcarrierId_Specified := True;
end;

function PWSCarrierLines.carrierId_Specified(Index: Integer): boolean;
begin
  Result := FcarrierId_Specified;
end;

destructor machineConfig.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FquickSearche)-1 do
    SysUtils.FreeAndNil(FquickSearche[I]);
  System.SetLength(FquickSearche, 0);
  SysUtils.FreeAndNil(Fstop);
  inherited Destroy;
end;

procedure machineConfig.SetquickSearche(Index: Integer; const AArray_Of_PWSSearchingParams: Array_Of_PWSSearchingParams);
begin
  FquickSearche := AArray_Of_PWSSearchingParams;
  FquickSearche_Specified := True;
end;

function machineConfig.quickSearche_Specified(Index: Integer): boolean;
begin
  Result := FquickSearche_Specified;
end;

procedure machineConfig.Setstop(Index: Integer; const APWSStop: PWSStop);
begin
  Fstop := APWSStop;
  Fstop_Specified := True;
end;

function machineConfig.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

destructor PWSUser.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Frole)-1 do
    SysUtils.FreeAndNil(Frole[I]);
  System.SetLength(Frole, 0);
  SysUtils.FreeAndNil(FuserInfo);
  inherited Destroy;
end;

procedure PWSUser.Setrole(Index: Integer; const AArray_Of_role: Array_Of_role);
begin
  Frole := AArray_Of_role;
  Frole_Specified := True;
end;

function PWSUser.role_Specified(Index: Integer): boolean;
begin
  Result := Frole_Specified;
end;

procedure PWSUser.SetuserInfo(Index: Integer; const APWSUserInfo: PWSUserInfo);
begin
  FuserInfo := APWSUserInfo;
  FuserInfo_Specified := True;
end;

function PWSUser.userInfo_Specified(Index: Integer): boolean;
begin
  Result := FuserInfo_Specified;
end;

destructor stickDiscount.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fdiscount)-1 do
    SysUtils.FreeAndNil(Fdiscount[I]);
  System.SetLength(Fdiscount, 0);
  inherited Destroy;
end;

procedure stickDiscount.SetwholePrice(Index: Integer; const ASingle: Single);
begin
  FwholePrice := ASingle;
  FwholePrice_Specified := True;
end;

function stickDiscount.wholePrice_Specified(Index: Integer): boolean;
begin
  Result := FwholePrice_Specified;
end;

procedure stickDiscount.Setdiscount(Index: Integer; const AArray_Of_discount: Array_Of_discount);
begin
  Fdiscount := AArray_Of_discount;
  Fdiscount_Specified := True;
end;

function stickDiscount.discount_Specified(Index: Integer): boolean;
begin
  Result := Fdiscount_Specified;
end;

destructor PWSCarrierRelations.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Frelation)-1 do
    SysUtils.FreeAndNil(Frelation[I]);
  System.SetLength(Frelation, 0);
  SysUtils.FreeAndNil(Fcarrier);
  SysUtils.FreeAndNil(FhomeCity);
  inherited Destroy;
end;

procedure PWSCarrierRelations.Setrelation(Index: Integer; const AArray_Of_relation: Array_Of_relation);
begin
  Frelation := AArray_Of_relation;
  Frelation_Specified := True;
end;

function PWSCarrierRelations.relation_Specified(Index: Integer): boolean;
begin
  Result := Frelation_Specified;
end;

procedure PWSCarrierRelations.Setcarrier(Index: Integer; const APWSCarrier: PWSCarrier);
begin
  Fcarrier := APWSCarrier;
  Fcarrier_Specified := True;
end;

function PWSCarrierRelations.carrier_Specified(Index: Integer): boolean;
begin
  Result := Fcarrier_Specified;
end;

procedure PWSCarrierRelations.SethomeCity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  FhomeCity := APWSFullyQualifiedCity;
  FhomeCity_Specified := True;
end;

function PWSCarrierRelations.homeCity_Specified(Index: Integer): boolean;
begin
  Result := FhomeCity_Specified;
end;

destructor PWSTimeTable.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fdeparture)-1 do
    SysUtils.FreeAndNil(Fdeparture[I]);
  System.SetLength(Fdeparture, 0);
  SysUtils.FreeAndNil(Fstop);
  inherited Destroy;
end;

procedure PWSTimeTable.Setdeparture(Index: Integer; const AArray_Of_departure: Array_Of_departure);
begin
  Fdeparture := AArray_Of_departure;
  Fdeparture_Specified := True;
end;

function PWSTimeTable.departure_Specified(Index: Integer): boolean;
begin
  Result := Fdeparture_Specified;
end;

procedure PWSTimeTable.Setstop(Index: Integer; const APWSFullyQualifiedStop: PWSFullyQualifiedStop);
begin
  Fstop := APWSFullyQualifiedStop;
  Fstop_Specified := True;
end;

function PWSTimeTable.stop_Specified(Index: Integer): boolean;
begin
  Result := Fstop_Specified;
end;

destructor departure.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FPWSStopInTimeForTimeTable)-1 do
    SysUtils.FreeAndNil(FPWSStopInTimeForTimeTable[I]);
  System.SetLength(FPWSStopInTimeForTimeTable, 0);
  for I := 0 to System.Length(FthroughCity)-1 do
    SysUtils.FreeAndNil(FthroughCity[I]);
  System.SetLength(FthroughCity, 0);
  SysUtils.FreeAndNil(Fcity);
  inherited Destroy;
end;

procedure departure.SetPWSStopInTimeForTimeTable(Index: Integer; const AArray_Of_PWSStopInTimeForTimeTable: Array_Of_PWSStopInTimeForTimeTable);
begin
  FPWSStopInTimeForTimeTable := AArray_Of_PWSStopInTimeForTimeTable;
  FPWSStopInTimeForTimeTable_Specified := True;
end;

function departure.PWSStopInTimeForTimeTable_Specified(Index: Integer): boolean;
begin
  Result := FPWSStopInTimeForTimeTable_Specified;
end;

procedure departure.Setcity(Index: Integer; const APWSFullyQualifiedCity: PWSFullyQualifiedCity);
begin
  Fcity := APWSFullyQualifiedCity;
  Fcity_Specified := True;
end;

function departure.city_Specified(Index: Integer): boolean;
begin
  Result := Fcity_Specified;
end;

procedure departure.SetthroughCity(Index: Integer; const APWSFullyQualifiedCityList: PWSFullyQualifiedCityList);
begin
  FthroughCity := APWSFullyQualifiedCityList;
  FthroughCity_Specified := True;
end;

function departure.throughCity_Specified(Index: Integer): boolean;
begin
  Result := FthroughCity_Specified;
end;

destructor PTiTariffForStick.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fprice)-1 do
    SysUtils.FreeAndNil(Fprice[I]);
  System.SetLength(Fprice, 0);
  inherited Destroy;
end;

procedure PTiTariffForStick.SetpriceId(Index: Integer; const AInt64: Int64);
begin
  FpriceId := AInt64;
  FpriceId_Specified := True;
end;

function PTiTariffForStick.priceId_Specified(Index: Integer): boolean;
begin
  Result := FpriceId_Specified;
end;

procedure PTiTariffForStick.SetepTariff(Index: Integer; const ABoolean: Boolean);
begin
  FepTariff := ABoolean;
  FepTariff_Specified := True;
end;

function PTiTariffForStick.epTariff_Specified(Index: Integer): boolean;
begin
  Result := FepTariff_Specified;
end;

procedure PTiTariffForStick.SetkasaTariff(Index: Integer; const ABoolean: Boolean);
begin
  FkasaTariff := ABoolean;
  FkasaTariff_Specified := True;
end;

function PTiTariffForStick.kasaTariff_Specified(Index: Integer): boolean;
begin
  Result := FkasaTariff_Specified;
end;

procedure PTiTariffForStick.SethoursToStartB(Index: Integer; const AInt64: Int64);
begin
  FhoursToStartB := AInt64;
  FhoursToStartB_Specified := True;
end;

function PTiTariffForStick.hoursToStartB_Specified(Index: Integer): boolean;
begin
  Result := FhoursToStartB_Specified;
end;

procedure PTiTariffForStick.SethoursToStartE(Index: Integer; const AInt64: Int64);
begin
  FhoursToStartE := AInt64;
  FhoursToStartE_Specified := True;
end;

function PTiTariffForStick.hoursToStartE_Specified(Index: Integer): boolean;
begin
  Result := FhoursToStartE_Specified;
end;

procedure PTiTariffForStick.SetbackTariff(Index: Integer; const ABoolean: Boolean);
begin
  FbackTariff := ABoolean;
  FbackTariff_Specified := True;
end;

function PTiTariffForStick.backTariff_Specified(Index: Integer): boolean;
begin
  Result := FbackTariff_Specified;
end;

procedure PTiTariffForStick.SetreturnMoneyHours(Index: Integer; const AInt64: Int64);
begin
  FreturnMoneyHours := AInt64;
  FreturnMoneyHours_Specified := True;
end;

function PTiTariffForStick.returnMoneyHours_Specified(Index: Integer): boolean;
begin
  Result := FreturnMoneyHours_Specified;
end;

procedure PTiTariffForStick.SetreturnMoneyPercent(Index: Integer; const ASingle: Single);
begin
  FreturnMoneyPercent := ASingle;
  FreturnMoneyPercent_Specified := True;
end;

function PTiTariffForStick.returnMoneyPercent_Specified(Index: Integer): boolean;
begin
  Result := FreturnMoneyPercent_Specified;
end;

procedure PTiTariffForStick.SetpayerMonthNo(Index: Integer; const AInteger: Integer);
begin
  FpayerMonthNo := AInteger;
  FpayerMonthNo_Specified := True;
end;

function PTiTariffForStick.payerMonthNo_Specified(Index: Integer): boolean;
begin
  Result := FpayerMonthNo_Specified;
end;

procedure PTiTariffForStick.SetpayerYearNo(Index: Integer; const AInteger: Integer);
begin
  FpayerYearNo := AInteger;
  FpayerYearNo_Specified := True;
end;

function PTiTariffForStick.payerYearNo_Specified(Index: Integer): boolean;
begin
  Result := FpayerYearNo_Specified;
end;

procedure PTiTariffForStick.SetpayerNoOr(Index: Integer; const ABoolean: Boolean);
begin
  FpayerNoOr := ABoolean;
  FpayerNoOr_Specified := True;
end;

function PTiTariffForStick.payerNoOr_Specified(Index: Integer): boolean;
begin
  Result := FpayerNoOr_Specified;
end;

procedure PTiTariffForStick.SetpayerMonthVal(Index: Integer; const ASingle: Single);
begin
  FpayerMonthVal := ASingle;
  FpayerMonthVal_Specified := True;
end;

function PTiTariffForStick.payerMonthVal_Specified(Index: Integer): boolean;
begin
  Result := FpayerMonthVal_Specified;
end;

procedure PTiTariffForStick.SetpayerYearVal(Index: Integer; const ASingle: Single);
begin
  FpayerYearVal := ASingle;
  FpayerYearVal_Specified := True;
end;

function PTiTariffForStick.payerYearVal_Specified(Index: Integer): boolean;
begin
  Result := FpayerYearVal_Specified;
end;

procedure PTiTariffForStick.SetpayerValOr(Index: Integer; const ABoolean: Boolean);
begin
  FpayerValOr := ABoolean;
  FpayerValOr_Specified := True;
end;

function PTiTariffForStick.payerValOr_Specified(Index: Integer): boolean;
begin
  Result := FpayerValOr_Specified;
end;

procedure PTiTariffForStick.SetholderMonthNo(Index: Integer; const AInteger: Integer);
begin
  FholderMonthNo := AInteger;
  FholderMonthNo_Specified := True;
end;

function PTiTariffForStick.holderMonthNo_Specified(Index: Integer): boolean;
begin
  Result := FholderMonthNo_Specified;
end;

procedure PTiTariffForStick.SetholderYearNo(Index: Integer; const AInteger: Integer);
begin
  FholderYearNo := AInteger;
  FholderYearNo_Specified := True;
end;

function PTiTariffForStick.holderYearNo_Specified(Index: Integer): boolean;
begin
  Result := FholderYearNo_Specified;
end;

procedure PTiTariffForStick.SetholderNoOr(Index: Integer; const ABoolean: Boolean);
begin
  FholderNoOr := ABoolean;
  FholderNoOr_Specified := True;
end;

function PTiTariffForStick.holderNoOr_Specified(Index: Integer): boolean;
begin
  Result := FholderNoOr_Specified;
end;

procedure PTiTariffForStick.SetholderMonthVal(Index: Integer; const ASingle: Single);
begin
  FholderMonthVal := ASingle;
  FholderMonthVal_Specified := True;
end;

function PTiTariffForStick.holderMonthVal_Specified(Index: Integer): boolean;
begin
  Result := FholderMonthVal_Specified;
end;

procedure PTiTariffForStick.SetholderYearVal(Index: Integer; const ASingle: Single);
begin
  FholderYearVal := ASingle;
  FholderYearVal_Specified := True;
end;

function PTiTariffForStick.holderYearVal_Specified(Index: Integer): boolean;
begin
  Result := FholderYearVal_Specified;
end;

procedure PTiTariffForStick.SetholderValOr(Index: Integer; const ABoolean: Boolean);
begin
  FholderValOr := ABoolean;
  FholderValOr_Specified := True;
end;

function PTiTariffForStick.holderValOr_Specified(Index: Integer): boolean;
begin
  Result := FholderValOr_Specified;
end;

procedure PTiTariffForStick.Setlegal(Index: Integer; const ABoolean: Boolean);
begin
  Flegal := ABoolean;
  Flegal_Specified := True;
end;

function PTiTariffForStick.legal_Specified(Index: Integer): boolean;
begin
  Result := Flegal_Specified;
end;

procedure PTiTariffForStick.SetnotGovDiscountValid(Index: Integer; const ABoolean: Boolean);
begin
  FnotGovDiscountValid := ABoolean;
  FnotGovDiscountValid_Specified := True;
end;

function PTiTariffForStick.notGovDiscountValid_Specified(Index: Integer): boolean;
begin
  Result := FnotGovDiscountValid_Specified;
end;

procedure PTiTariffForStick.SetsmsSendTypeEnable(Index: Integer; const ABoolean: Boolean);
begin
  FsmsSendTypeEnable := ABoolean;
  FsmsSendTypeEnable_Specified := True;
end;

function PTiTariffForStick.smsSendTypeEnable_Specified(Index: Integer): boolean;
begin
  Result := FsmsSendTypeEnable_Specified;
end;

procedure PTiTariffForStick.Setprice(Index: Integer; const AArray_Of_price2: Array_Of_price2);
begin
  Fprice := AArray_Of_price2;
  Fprice_Specified := True;
end;

function PTiTariffForStick.price_Specified(Index: Integer): boolean;
begin
  Result := Fprice_Specified;
end;

procedure PTiTariffForStick.SetlagguageDescription(Index: Integer; const Astring: string);
begin
  FlagguageDescription := Astring;
  FlagguageDescription_Specified := True;
end;

function PTiTariffForStick.lagguageDescription_Specified(Index: Integer): boolean;
begin
  Result := FlagguageDescription_Specified;
end;

procedure PTiTariffForStick.Setname_(Index: Integer; const Astring: string);
begin
  Fname_ := Astring;
  Fname__Specified := True;
end;

function PTiTariffForStick.name__Specified(Index: Integer): boolean;
begin
  Result := Fname__Specified;
end;

procedure PTiTariffForStick.SettariffType(Index: Integer; const AtariffType: tariffType);
begin
  FtariffType := AtariffType;
  FtariffType_Specified := True;
end;

function PTiTariffForStick.tariffType_Specified(Index: Integer): boolean;
begin
  Result := FtariffType_Specified;
end;

procedure PTiTariffForStick.SettariffTypeCode(Index: Integer; const Astring: string);
begin
  FtariffTypeCode := Astring;
  FtariffTypeCode_Specified := True;
end;

function PTiTariffForStick.tariffTypeCode_Specified(Index: Integer): boolean;
begin
  Result := FtariffTypeCode_Specified;
end;

destructor PWSTrackRecording.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FlastRecordedPoint)-1 do
    SysUtils.FreeAndNil(FlastRecordedPoint[I]);
  System.SetLength(FlastRecordedPoint, 0);
  SysUtils.FreeAndNil(FbeginOfRecording);
  SysUtils.FreeAndNil(Fdriver);
  SysUtils.FreeAndNil(Fvehicle);
  SysUtils.FreeAndNil(FbusCourse);
  inherited Destroy;
end;

procedure PWSTrackRecording.SetbeginOfRecording(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FbeginOfRecording := ATXSDateTime;
  FbeginOfRecording_Specified := True;
end;

function PWSTrackRecording.beginOfRecording_Specified(Index: Integer): boolean;
begin
  Result := FbeginOfRecording_Specified;
end;

procedure PWSTrackRecording.SettrackRecordingType(Index: Integer; const AInteger: Integer);
begin
  FtrackRecordingType := AInteger;
  FtrackRecordingType_Specified := True;
end;

function PWSTrackRecording.trackRecordingType_Specified(Index: Integer): boolean;
begin
  Result := FtrackRecordingType_Specified;
end;

procedure PWSTrackRecording.SetrecordingNo(Index: Integer; const Astring: string);
begin
  FrecordingNo := Astring;
  FrecordingNo_Specified := True;
end;

function PWSTrackRecording.recordingNo_Specified(Index: Integer): boolean;
begin
  Result := FrecordingNo_Specified;
end;

procedure PWSTrackRecording.Setdriver(Index: Integer; const Adriver: driver);
begin
  Fdriver := Adriver;
  Fdriver_Specified := True;
end;

function PWSTrackRecording.driver_Specified(Index: Integer): boolean;
begin
  Result := Fdriver_Specified;
end;

procedure PWSTrackRecording.Setvehicle(Index: Integer; const APWSVehicle: PWSVehicle);
begin
  Fvehicle := APWSVehicle;
  Fvehicle_Specified := True;
end;

function PWSTrackRecording.vehicle_Specified(Index: Integer): boolean;
begin
  Result := Fvehicle_Specified;
end;

procedure PWSTrackRecording.SetbusCourse(Index: Integer; const APWSTiBusCourse: PWSTiBusCourse);
begin
  FbusCourse := APWSTiBusCourse;
  FbusCourse_Specified := True;
end;

function PWSTrackRecording.busCourse_Specified(Index: Integer): boolean;
begin
  Result := FbusCourse_Specified;
end;

procedure PWSTrackRecording.SetlastRecordedPoint(Index: Integer; const AArray_Of_PWSWaypoint: Array_Of_PWSWaypoint);
begin
  FlastRecordedPoint := AArray_Of_PWSWaypoint;
  FlastRecordedPoint_Specified := True;
end;

function PWSTrackRecording.lastRecordedPoint_Specified(Index: Integer): boolean;
begin
  Result := FlastRecordedPoint_Specified;
end;

destructor PWSTiDetailedReservation.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fticket)-1 do
    SysUtils.FreeAndNil(Fticket[I]);
  System.SetLength(Fticket, 0);
  for I := 0 to System.Length(FperTicket)-1 do
    SysUtils.FreeAndNil(FperTicket[I]);
  System.SetLength(FperTicket, 0);
  SysUtils.FreeAndNil(Freservation);
  SysUtils.FreeAndNil(Fpayer);
  SysUtils.FreeAndNil(FdefaultSendingData);
  inherited Destroy;
end;

procedure PWSTiDetailedReservation.Setreservation(Index: Integer; const Areservation: reservation);
begin
  Freservation := Areservation;
  Freservation_Specified := True;
end;

function PWSTiDetailedReservation.reservation_Specified(Index: Integer): boolean;
begin
  Result := Freservation_Specified;
end;

procedure PWSTiDetailedReservation.Setpayer(Index: Integer; const Apayer: payer);
begin
  Fpayer := Apayer;
  Fpayer_Specified := True;
end;

function PWSTiDetailedReservation.payer_Specified(Index: Integer): boolean;
begin
  Result := Fpayer_Specified;
end;

procedure PWSTiDetailedReservation.Setticket(Index: Integer; const AArray_Of_ticket2: Array_Of_ticket2);
begin
  Fticket := AArray_Of_ticket2;
  Fticket_Specified := True;
end;

function PWSTiDetailedReservation.ticket_Specified(Index: Integer): boolean;
begin
  Result := Fticket_Specified;
end;

procedure PWSTiDetailedReservation.SetperTicket(Index: Integer; const APWSTiPeriodicTickets: PWSTiPeriodicTickets);
begin
  FperTicket := APWSTiPeriodicTickets;
  FperTicket_Specified := True;
end;

function PWSTiDetailedReservation.perTicket_Specified(Index: Integer): boolean;
begin
  Result := FperTicket_Specified;
end;

procedure PWSTiDetailedReservation.SetdefaultSendingData(Index: Integer; const APWSTiSendingData: PWSTiSendingData);
begin
  FdefaultSendingData := APWSTiSendingData;
  FdefaultSendingData_Specified := True;
end;

function PWSTiDetailedReservation.defaultSendingData_Specified(Index: Integer): boolean;
begin
  Result := FdefaultSendingData_Specified;
end;

destructor ticket3.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fplace)-1 do
    SysUtils.FreeAndNil(Fplace[I]);
  System.SetLength(Fplace, 0);
  SysUtils.FreeAndNil(FgoDate);
  SysUtils.FreeAndNil(FconnectionDate);
  SysUtils.FreeAndNil(Fconnection);
  SysUtils.FreeAndNil(Fholder);
  SysUtils.FreeAndNil(Ftariff);
  inherited Destroy;
end;

procedure ticket3.SetticketId(Index: Integer; const AInt64: Int64);
begin
  FticketId := AInt64;
  FticketId_Specified := True;
end;

function ticket3.ticketId_Specified(Index: Integer): boolean;
begin
  Result := FticketId_Specified;
end;

procedure ticket3.SetgoDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FgoDate := ATXSDateTime;
  FgoDate_Specified := True;
end;

function ticket3.goDate_Specified(Index: Integer): boolean;
begin
  Result := FgoDate_Specified;
end;

procedure ticket3.SetconnectionDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FconnectionDate := ATXSDateTime;
  FconnectionDate_Specified := True;
end;

function ticket3.connectionDate_Specified(Index: Integer): boolean;
begin
  Result := FconnectionDate_Specified;
end;

procedure ticket3.SetgrossPrice(Index: Integer; const ASingle: Single);
begin
  FgrossPrice := ASingle;
  FgrossPrice_Specified := True;
end;

function ticket3.grossPrice_Specified(Index: Integer): boolean;
begin
  Result := FgrossPrice_Specified;
end;

procedure ticket3.SetvatRate(Index: Integer; const ASingle: Single);
begin
  FvatRate := ASingle;
  FvatRate_Specified := True;
end;

function ticket3.vatRate_Specified(Index: Integer): boolean;
begin
  Result := FvatRate_Specified;
end;

procedure ticket3.SetvatValue(Index: Integer; const ASingle: Single);
begin
  FvatValue := ASingle;
  FvatValue_Specified := True;
end;

function ticket3.vatValue_Specified(Index: Integer): boolean;
begin
  Result := FvatValue_Specified;
end;

procedure ticket3.SetcodeToVerify(Index: Integer; const Astring: string);
begin
  FcodeToVerify := Astring;
  FcodeToVerify_Specified := True;
end;

function ticket3.codeToVerify_Specified(Index: Integer): boolean;
begin
  Result := FcodeToVerify_Specified;
end;

procedure ticket3.SetticketLoginCode(Index: Integer; const Astring: string);
begin
  FticketLoginCode := Astring;
  FticketLoginCode_Specified := True;
end;

function ticket3.ticketLoginCode_Specified(Index: Integer): boolean;
begin
  Result := FticketLoginCode_Specified;
end;

procedure ticket3.Setplace(Index: Integer; const AArray_Of_place2: Array_Of_place2);
begin
  Fplace := AArray_Of_place2;
  Fplace_Specified := True;
end;

function ticket3.place_Specified(Index: Integer): boolean;
begin
  Result := Fplace_Specified;
end;

procedure ticket3.Setconnection(Index: Integer; const Aconnection: connection);
begin
  Fconnection := Aconnection;
  Fconnection_Specified := True;
end;

function ticket3.connection_Specified(Index: Integer): boolean;
begin
  Result := Fconnection_Specified;
end;

procedure ticket3.Setholder(Index: Integer; const Aholder2: holder2);
begin
  Fholder := Aholder2;
  Fholder_Specified := True;
end;

function ticket3.holder_Specified(Index: Integer): boolean;
begin
  Result := Fholder_Specified;
end;

procedure ticket3.Settariff(Index: Integer; const APWSTiTariffForStick: PWSTiTariffForStick);
begin
  Ftariff := APWSTiTariffForStick;
  Ftariff_Specified := True;
end;

function ticket3.tariff_Specified(Index: Integer): boolean;
begin
  Result := Ftariff_Specified;
end;

destructor PWSResultPriceDetailsParams.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(Fparam)-1 do
    SysUtils.FreeAndNil(Fparam[I]);
  System.SetLength(Fparam, 0);
  SysUtils.FreeAndNil(FsearchDate);
  inherited Destroy;
end;

procedure PWSResultPriceDetailsParams.SetsearchDate(Index: Integer; const ATXSDateTime: TXSDateTime);
begin
  FsearchDate := ATXSDateTime;
  FsearchDate_Specified := True;
end;

function PWSResultPriceDetailsParams.searchDate_Specified(Index: Integer): boolean;
begin
  Result := FsearchDate_Specified;
end;

procedure PWSResultPriceDetailsParams.Setparam(Index: Integer; const AArray_Of_param: Array_Of_param);
begin
  Fparam := AArray_Of_param;
  Fparam_Specified := True;
end;

function PWSResultPriceDetailsParams.param_Specified(Index: Integer): boolean;
begin
  Result := Fparam_Specified;
end;

procedure PWSSearchingResult.Setresult(Index: Integer; const AArray_Of_result2: Array_Of_result2);
begin
  Fresult := AArray_Of_result2;
  Fresult_Specified := True;
end;

function PWSSearchingResult.result_Specified(Index: Integer): boolean;
begin
  Result := Fresult_Specified;
end;

procedure PWSSearchingResult.SetresultsId(Index: Integer; const Astring: string);
begin
  FresultsId := Astring;
  FresultsId_Specified := True;
end;

function PWSSearchingResult.resultsId_Specified(Index: Integer): boolean;
begin
  Result := FresultsId_Specified;
end;

destructor PWSTiSendTickets.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FcommonCause)-1 do
    SysUtils.FreeAndNil(FcommonCause[I]);
  System.SetLength(FcommonCause, 0);
  inherited Destroy;
end;

procedure PWSTiSendTickets.SetcausesForTicket(Index: Integer; const AArray_Of_causesForTicket: Array_Of_causesForTicket);
begin
  FcausesForTicket := AArray_Of_causesForTicket;
  FcausesForTicket_Specified := True;
end;

function PWSTiSendTickets.causesForTicket_Specified(Index: Integer): boolean;
begin
  Result := FcausesForTicket_Specified;
end;

procedure PWSTiSendTickets.SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FcommonCause := AArray_Of_PWSEnumParam;
  FcommonCause_Specified := True;
end;

function PWSTiSendTickets.commonCause_Specified(Index: Integer): boolean;
begin
  Result := FcommonCause_Specified;
end;

destructor PWSTiOrderUnavailable.Destroy;
var
  I: Integer;
begin
  for I := 0 to System.Length(FPWSTiTicketUnavailableFaultData)-1 do
    SysUtils.FreeAndNil(FPWSTiTicketUnavailableFaultData[I]);
  System.SetLength(FPWSTiTicketUnavailableFaultData, 0);
  for I := 0 to System.Length(FcommonCause)-1 do
    SysUtils.FreeAndNil(FcommonCause[I]);
  System.SetLength(FcommonCause, 0);
  inherited Destroy;
end;

procedure PWSTiOrderUnavailable.SetPWSTiTicketUnavailableFaultData(Index: Integer; const AArray_Of_PWSTiTicketUnavailableFaultData: Array_Of_PWSTiTicketUnavailableFaultData);
begin
  FPWSTiTicketUnavailableFaultData := AArray_Of_PWSTiTicketUnavailableFaultData;
  FPWSTiTicketUnavailableFaultData_Specified := True;
end;

function PWSTiOrderUnavailable.PWSTiTicketUnavailableFaultData_Specified(Index: Integer): boolean;
begin
  Result := FPWSTiTicketUnavailableFaultData_Specified;
end;

procedure PWSTiOrderUnavailable.SetperiodicCauses(Index: Integer; const APWSTiPeriodicCardIdsExceptionFaultData: PWSTiPeriodicCardIdsExceptionFaultData);
begin
  FperiodicCauses := APWSTiPeriodicCardIdsExceptionFaultData;
  FperiodicCauses_Specified := True;
end;

function PWSTiOrderUnavailable.periodicCauses_Specified(Index: Integer): boolean;
begin
  Result := FperiodicCauses_Specified;
end;

procedure PWSTiOrderUnavailable.SetcommonCause(Index: Integer; const AArray_Of_PWSEnumParam: Array_Of_PWSEnumParam);
begin
  FcommonCause := AArray_Of_PWSEnumParam;
  FcommonCause_Specified := True;
end;

function PWSTiOrderUnavailable.commonCause_Specified(Index: Integer): boolean;
begin
  Result := FcommonCause_Specified;
end;

initialization
  InvRegistry.RegisterInterface(TypeInfo(PWebServicePortType), 'http://83.15.136.94:54321/axis2/services/PWebService', 'UTF-8');
  InvRegistry.RegisterDefaultSOAPAction(TypeInfo(PWebServicePortType), 'urn:%operationName%');
  InvRegistry.RegisterInvokeOptions(TypeInfo(PWebServicePortType), ioDocument);
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'connExists', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'logout', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'removeSearchingAccount', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'lockSearchingAccount', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'unlockSearchingAccount', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'setSearchingAccountValidity', 'to_', 'to');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'setSearchingAccountValidity', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'changeUserPassword', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'changePassword', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'changeUserData', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'commitOrder', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'rollbackOrder', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'cancelTicket', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'changeTicketConnectionDate', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'sendTicket', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'sendTickets', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'changeTicketHolderData', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'logVendingMachineEvent', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'getCarrierRegulations', 'string_', 'string');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'sendMessageToDriver', 'message_', 'message');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'sendMessageToDriver', 'boolean_', 'boolean');
  InvRegistry.RegisterExternalParamName(TypeInfo(PWebServicePortType), 'savePeriodicTicketsData', 'boolean_', 'boolean');
  RemClassRegistry.RegisterXSClass(PTiStopInTime, 'http://83.15.136.94:54321/axis2/services', 'PTiStopInTime');
  RemClassRegistry.RegisterXSClass(PWSUserCreateParams, 'http://83.15.136.94:54321/axis2/services', 'PWSUserCreateParams');
  RemClassRegistry.RegisterXSClass(PWSTTSearchingParams, 'http://83.15.136.94:54321/axis2/services', 'PWSTTSearchingParams');
  RemClassRegistry.RegisterXSClass(PWSEnumParam, 'http://83.15.136.94:54321/axis2/services', 'PWSEnumParam');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSEnumParam), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSTiDiscount, 'http://83.15.136.94:54321/axis2/services', 'PWSTiDiscount');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiDiscount), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSTiTariffPriceAfterDiscount, 'http://83.15.136.94:54321/axis2/services', 'PWSTiTariffPriceAfterDiscount');
  RemClassRegistry.RegisterXSClass(PWSTiDocType, 'http://83.15.136.94:54321/axis2/services', 'PWSTiDocType');
  RemClassRegistry.RegisterXSClass(PWSStop, 'http://83.15.136.94:54321/axis2/services', 'PWSStop');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSStop), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSCostForPeriod, 'http://83.15.136.94:54321/axis2/services', 'PWSCostForPeriod');
  RemClassRegistry.RegisterXSClass(PWSCarrierId, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierId');
  RemClassRegistry.RegisterXSClass(PWSTiOrderWithCustomerData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiOrderWithCustomerData');
  RemClassRegistry.RegisterXSClass(PWSTiHolderForTicket, 'http://83.15.136.94:54321/axis2/services', 'PWSTiHolderForTicket');
  RemClassRegistry.RegisterXSClass(place, 'http://83.15.136.94:54321/axis2/services', 'place');
  RemClassRegistry.RegisterXSClass(periodicTicket, 'http://83.15.136.94:54321/axis2/services', 'periodicTicket');
  RemClassRegistry.RegisterXSClass(PWSTiPeriodicCardIdentyfier, 'http://83.15.136.94:54321/axis2/services', 'PWSTiPeriodicCardIdentyfier');
  RemClassRegistry.RegisterXSClass(PWSTiSendingData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSendingData');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiSendingData), 'type_', 'type');
  RemClassRegistry.RegisterXSClass(customerData, 'http://83.15.136.94:54321/axis2/services', 'customerData');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(customerData), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSMessage, 'http://83.15.136.94:54321/axis2/services', 'PWSMessage');
  RemClassRegistry.RegisterXSClass(PWSFullyQualifiedStop, 'http://83.15.136.94:54321/axis2/services', 'PWSFullyQualifiedStop');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSFullyQualifiedStop), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSFullyQualifiedCity, 'http://83.15.136.94:54321/axis2/services', 'PWSFullyQualifiedCity');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSFullyQualifiedCity), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSInformicaCarrier, 'http://83.15.136.94:54321/axis2/services', 'PWSInformicaCarrier');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSCitiesStops), 'http://83.15.136.94:54321/axis2/services', 'PWSCitiesStops');
  RemClassRegistry.RegisterXSClass(PWSNamePrincipal, 'http://83.15.136.94:54321/axis2/services', 'PWSNamePrincipal');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSNamePrincipal), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSConnSearchingDetails, 'http://83.15.136.94:54321/axis2/services', 'PWSConnSearchingDetails');
  RemClassRegistry.RegisterXSClass(holder, 'http://83.15.136.94:54321/axis2/services', 'holder');
  RemClassRegistry.RegisterXSInfo(TypeInfo(linesInfo), 'http://83.15.136.94:54321/axis2/services', 'linesInfo');
  RemClassRegistry.RegisterXSClass(PWSTiPeriodicTicketInfo, 'http://83.15.136.94:54321/axis2/services', 'PWSTiPeriodicTicketInfo');
  RemClassRegistry.RegisterXSClass(section, 'http://83.15.136.94:54321/axis2/services', 'section');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(section), 'type_', 'type');
  RemClassRegistry.RegisterXSClass(PWSTiBusCourse, 'http://83.15.136.94:54321/axis2/services', 'PWSTiBusCourse');
  RemClassRegistry.RegisterXSClass(PWSConnection, 'http://83.15.136.94:54321/axis2/services', 'PWSConnection');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSConnection), 'type_', 'type');
  RemClassRegistry.RegisterXSInfo(TypeInfo(type_), 'http://83.15.136.94:54321/axis2/services', 'type_', 'type');
  RemClassRegistry.RegisterXSClass(type_2, 'http://83.15.136.94:54321/axis2/services', 'type_2', 'type');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(type_2), 'type_', 'type');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(type_2), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(passenger, 'http://83.15.136.94:54321/axis2/services', 'passenger');
  RemClassRegistry.RegisterXSClass(PWSPasswordCredential, 'http://83.15.136.94:54321/axis2/services', 'PWSPasswordCredential');
  RemClassRegistry.RegisterXSClass(PWSSessionIdPrincipal, 'http://83.15.136.94:54321/axis2/services', 'PWSSessionIdPrincipal');
  RemClassRegistry.RegisterXSInfo(TypeInfo(version), 'http://83.15.136.94:54321/axis2/services', 'version');
  RemClassRegistry.RegisterXSClass(PWSUserInfo, 'http://83.15.136.94:54321/axis2/services', 'PWSUserInfo');
  RemClassRegistry.RegisterXSClass(PWSStopInTime, 'http://83.15.136.94:54321/axis2/services', 'PWSStopInTime');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSResultRouteDetailsParams), 'http://83.15.136.94:54321/axis2/services', 'PWSResultRouteDetailsParams');
  RemClassRegistry.RegisterXSClass(param, 'http://83.15.136.94:54321/axis2/services', 'param');
  RemClassRegistry.RegisterXSClass(PWSFullyQualifiedCityExt, 'http://83.15.136.94:54321/axis2/services', 'PWSFullyQualifiedCityExt');
  RemClassRegistry.RegisterXSClass(PWSVehiclePosition, 'http://83.15.136.94:54321/axis2/services', 'PWSVehiclePosition');
  RemClassRegistry.RegisterXSClass(PWSVehicle, 'http://83.15.136.94:54321/axis2/services', 'PWSVehicle');
  RemClassRegistry.RegisterXSClass(PWSTiReservationId, 'http://83.15.136.94:54321/axis2/services', 'PWSTiReservationId');
  RemClassRegistry.RegisterXSClass(PWSTiVendingParams, 'http://83.15.136.94:54321/axis2/services', 'PWSTiVendingParams');
  RemClassRegistry.RegisterXSClass(PWSStick, 'http://83.15.136.94:54321/axis2/services', 'PWSStick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PTiHoldersMatrix), 'http://83.15.136.94:54321/axis2/services', 'PTiHoldersMatrix');
  RemClassRegistry.RegisterXSClass(stickId, 'http://83.15.136.94:54321/axis2/services', 'stickId');
  RemClassRegistry.RegisterXSInfo(TypeInfo(cause), 'http://83.15.136.94:54321/axis2/services', 'cause');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiPeriodicCardIdsExceptionFaultData), 'http://83.15.136.94:54321/axis2/services', 'PWSTiPeriodicCardIdsExceptionFaultData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSCarrierLine), 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierLine');
  RemClassRegistry.RegisterXSClass(PWSInfKurs, 'http://83.15.136.94:54321/axis2/services', 'PWSInfKurs');
  RemClassRegistry.RegisterXSClass(PWSChangeUserDataParams, 'http://83.15.136.94:54321/axis2/services', 'PWSChangeUserDataParams');
  RemClassRegistry.RegisterXSClass(PWSRelation, 'http://83.15.136.94:54321/axis2/services', 'PWSRelation');
  RemClassRegistry.RegisterXSClass(price, 'http://83.15.136.94:54321/axis2/services', 'price');
  RemClassRegistry.RegisterXSClass(country, 'http://83.15.136.94:54321/axis2/services', 'country');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(country), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(docType), 'http://83.15.136.94:54321/axis2/services', 'docType');
  RemClassRegistry.RegisterXSClass(PTiHolderForTicket, 'http://83.15.136.94:54321/axis2/services', 'PTiHolderForTicket');
  RemClassRegistry.RegisterXSClass(role, 'http://83.15.136.94:54321/axis2/services', 'role');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(role), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSTiReservationCancelInfo, 'http://83.15.136.94:54321/axis2/services', 'PWSTiReservationCancelInfo');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSResultPriceDetails), 'http://83.15.136.94:54321/axis2/services', 'PWSResultPriceDetails');
  RemClassRegistry.RegisterXSClass(discount, 'http://83.15.136.94:54321/axis2/services', 'discount');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(discount), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(PWSWebServiceUser, 'http://83.15.136.94:54321/axis2/services', 'PWSWebServiceUser');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiPeriodicTickets), 'http://83.15.136.94:54321/axis2/services', 'PWSTiPeriodicTickets');
  RemClassRegistry.RegisterXSClass(PWSTiReservationDone, 'http://83.15.136.94:54321/axis2/services', 'PWSTiReservationDone');
  RemClassRegistry.RegisterXSClass(PWSRelationParams, 'http://83.15.136.94:54321/axis2/services', 'PWSRelationParams');
  RemClassRegistry.RegisterXSInfo(TypeInfo(optimizationMode), 'http://83.15.136.94:54321/axis2/services', 'optimizationMode');
  RemClassRegistry.RegisterXSInfo(TypeInfo(carrierType), 'http://83.15.136.94:54321/axis2/services', 'carrierType');
  RemClassRegistry.RegisterXSClass(PWSCarrierDetails, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierDetails');
  RemClassRegistry.RegisterXSClass(PWSCarrier, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrier');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSCarrier), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(card, 'http://83.15.136.94:54321/axis2/services', 'card');
  RemClassRegistry.RegisterXSClass(address, 'http://83.15.136.94:54321/axis2/services', 'address');
  RemClassRegistry.RegisterXSClass(PWSTiSendTicketInfo, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSendTicketInfo');
  RemClassRegistry.RegisterXSClass(relation, 'http://83.15.136.94:54321/axis2/services', 'relation');
  RemClassRegistry.RegisterXSClass(PWSStopInTimeForTimeTable, 'http://83.15.136.94:54321/axis2/services', 'PWSStopInTimeForTimeTable');
  RemClassRegistry.RegisterXSClass(price2, 'http://83.15.136.94:54321/axis2/services', 'price2', 'price');
  RemClassRegistry.RegisterXSClass(country2, 'http://83.15.136.94:54321/axis2/services', 'country2', 'country');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(country2), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(tariffType), 'http://83.15.136.94:54321/axis2/services', 'tariffType');
  RemClassRegistry.RegisterXSClass(PWSTiSendTicketFormat, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSendTicketFormat');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSOpinionsForCarrier), 'http://83.15.136.94:54321/axis2/services', 'PWSOpinionsForCarrier');
  RemClassRegistry.RegisterXSClass(opinion, 'http://83.15.136.94:54321/axis2/services', 'opinion');
  RemClassRegistry.RegisterXSClass(PWSWaypoint, 'http://83.15.136.94:54321/axis2/services', 'PWSWaypoint');
  RemClassRegistry.RegisterXSClass(driver, 'http://83.15.136.94:54321/axis2/services', 'driver');
  RemClassRegistry.RegisterXSClass(reservation, 'http://83.15.136.94:54321/axis2/services', 'reservation');
  RemClassRegistry.RegisterXSClass(payer, 'http://83.15.136.94:54321/axis2/services', 'payer');
  RemClassRegistry.RegisterXSClass(place2, 'http://83.15.136.94:54321/axis2/services', 'place2', 'place');
  RemClassRegistry.RegisterXSClass(connection, 'http://83.15.136.94:54321/axis2/services', 'connection');
  RemClassRegistry.RegisterXSClass(PWSTiStopInTime, 'http://83.15.136.94:54321/axis2/services', 'PWSTiStopInTime');
  RemClassRegistry.RegisterXSClass(holder2, 'http://83.15.136.94:54321/axis2/services', 'holder2', 'holder');
  RemClassRegistry.RegisterXSClass(PWSCityId, 'http://83.15.136.94:54321/axis2/services', 'PWSCityId');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiSellingReport), 'http://83.15.136.94:54321/axis2/services', 'PWSTiSellingReport');
  RemClassRegistry.RegisterXSClass(listOfRecord, 'http://83.15.136.94:54321/axis2/services', 'listOfRecord');
  RemClassRegistry.RegisterXSClass(param2, 'http://83.15.136.94:54321/axis2/services', 'param2', 'param');
  RemClassRegistry.RegisterXSInfo(TypeInfo(stickRoute), 'http://83.15.136.94:54321/axis2/services', 'stickRoute');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSResultRouteDetails), 'http://83.15.136.94:54321/axis2/services', 'PWSResultRouteDetails');
  RemClassRegistry.RegisterXSClass(PWSMessageFromDriver, 'http://83.15.136.94:54321/axis2/services', 'PWSMessageFromDriver');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSMessageFromDriver), 'message_', 'message');
  RemClassRegistry.RegisterXSClass(carrierType2, 'http://83.15.136.94:54321/axis2/services', 'carrierType2', 'carrierType');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(carrierType2), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(roundType), 'http://83.15.136.94:54321/axis2/services', 'roundType');
  RemClassRegistry.RegisterXSClass(discount2, 'http://83.15.136.94:54321/axis2/services', 'discount2', 'discount');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(discount2), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(cancelState), 'http://83.15.136.94:54321/axis2/services', 'cancelState');
  RemClassRegistry.RegisterXSClass(PTiPlace, 'http://83.15.136.94:54321/axis2/services', 'PTiPlace');
  RemClassRegistry.RegisterXSClass(connection2, 'http://83.15.136.94:54321/axis2/services', 'connection2', 'connection');
  RemClassRegistry.RegisterXSInfo(TypeInfo(defaultSendingType), 'http://83.15.136.94:54321/axis2/services', 'defaultSendingType');
  RemClassRegistry.RegisterXSClass(holder3, 'http://83.15.136.94:54321/axis2/services', 'holder3', 'holder');
  RemClassRegistry.RegisterXSClass(PWSTiVendingEvent, 'http://83.15.136.94:54321/axis2/services', 'PWSTiVendingEvent');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiVendingEvent), 'message_', 'message');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiVendingEvent), 'type_', 'type');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiStickIds), 'http://83.15.136.94:54321/axis2/services', 'PWSTiStickIds');
  RemClassRegistry.RegisterXSClass(stickId2, 'http://83.15.136.94:54321/axis2/services', 'stickId2', 'stickId');
  RemClassRegistry.RegisterXSInfo(TypeInfo(result), 'http://83.15.136.94:54321/axis2/services', 'result');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSVehiclePositionList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSVehiclePositionList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSWebServiceUserList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSWebServiceUserList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSRelationParamsList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSRelationParamsList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSMessageFromDriverList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSMessageFromDriverList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSInfKursList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSInfKursList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSCarrierIdList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSCarrierIdList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSOpinionsForCarrierList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSOpinionsForCarrierList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiBusCourseList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiBusCourseList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSFullyQualifiedCityList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSFullyQualifiedCityList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTrackRecordingList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTrackRecordingList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSRelationList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSRelationList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSCitiesStopsList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSCitiesStopsList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSCarrierDetailsList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSCarrierDetailsList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSVehicleList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSVehicleList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiSendNormalTicketDataList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiSendNormalTicketDataList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSGetStopParamList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSGetStopParamList');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSFullyQualifiedCityExtList), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSFullyQualifiedCityExtList');
  RemClassRegistry.RegisterXSClass(PWSTiSellingReport2, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiSellingReport2', 'PWSTiSellingReport');
  RemClassRegistry.RegisterXSInfo(TypeInfo(causesForTicket), 'http://83.15.136.94:54321/axis2/services/PWebService', 'causesForTicket');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiChangeHolderData), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiChangeHolderData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault');
  RemClassRegistry.RegisterXSClass(PWSEmptyTimeTable, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSEmptyTimeTable');
  RemClassRegistry.RegisterXSClass(PWSMoreThanOneCarrier, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSMoreThanOneCarrier');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSMoreThanOneCarrier), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault2), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault2', 'fault');
  RemClassRegistry.RegisterXSClass(PWSStops, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSStops');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiKasaUnavailable), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiKasaUnavailable');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiRollbackResrvation), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiRollbackResrvation');
  RemClassRegistry.RegisterXSInfo(TypeInfo(cause2), 'http://83.15.136.94:54321/axis2/services/PWebService', 'cause2', 'cause');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PTiHoldersMatrix2), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PTiHoldersMatrix2', 'PTiHoldersMatrix');
  RemClassRegistry.RegisterXSClass(PWSNoSuchRecording, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoSuchRecording');
  RemClassRegistry.RegisterXSClass(PWSNoSuchCarrier, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoSuchCarrier');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiReservation), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiReservation');
  RemClassRegistry.RegisterXSClass(PWSTiVendingParams2, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiVendingParams2', 'PWSTiVendingParams');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault3), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault3', 'fault');
  RemClassRegistry.RegisterXSClass(PWSChangeUserData, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSChangeUserData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault4), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault4', 'fault');
  RemClassRegistry.RegisterXSClass(PWSChangePassword, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSChangePassword');
  RemClassRegistry.RegisterXSClass(PWSNotYourUser, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNotYourUser');
  RemClassRegistry.RegisterXSClass(PWSNoSuchInfCarrier, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoSuchInfCarrier');
  RemClassRegistry.RegisterXSClass(PWSNoSuchInfCourse, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoSuchInfCourse');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault5), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault5', 'fault');
  RemClassRegistry.RegisterXSClass(PWSNoConn, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoConn');
  RemClassRegistry.RegisterXSClass(PWSNoVehicle, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSNoVehicle');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault6), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault6', 'fault');
  RemClassRegistry.RegisterXSClass(PWSCreateUser, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSCreateUser');
  RemClassRegistry.RegisterXSInfo(TypeInfo(fault7), 'http://83.15.136.94:54321/axis2/services/PWebService', 'fault7', 'fault');
  RemClassRegistry.RegisterXSClass(PWSLogin, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSLogin');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSLogin), 'message_', 'message');
  RemClassRegistry.RegisterXSInfo(TypeInfo(causeData), 'http://83.15.136.94:54321/axis2/services/PWebService', 'causeData');
  RemClassRegistry.RegisterXSClass(PWSTiCommitResrvation, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiCommitResrvation');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiChangeTicketDates), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiChangeTicketDates');
  RemClassRegistry.RegisterXSInfo(TypeInfo(error), 'http://83.15.136.94:54321/axis2/services/PWebService', 'error');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSValidation), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSValidation');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiCancelReservation), 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiCancelReservation');
  RemClassRegistry.RegisterXSInfo(TypeInfo(elem), 'http://83.15.136.94:54321/axis2/services', 'elem');
  RemClassRegistry.RegisterXSInfo(TypeInfo(PWSTiVehicleMatrixRow), 'http://83.15.136.94:54321/axis2/services', 'PWSTiVehicleMatrixRow');
  RemClassRegistry.RegisterXSInfo(TypeInfo(matrix), 'http://83.15.136.94:54321/axis2/services', 'matrix');
  RemClassRegistry.RegisterXSClass(placesNumsBounds, 'http://83.15.136.94:54321/axis2/services', 'placesNumsBounds');
  RemClassRegistry.RegisterXSClass(cause3, 'http://83.15.136.94:54321/axis2/services', 'cause3', 'cause');
  RemClassRegistry.RegisterXSClass(sit, 'http://83.15.136.94:54321/axis2/services', 'sit');
  RemClassRegistry.RegisterXSClass(stick, 'http://83.15.136.94:54321/axis2/services', 'stick');
  RemClassRegistry.RegisterXSClass(connId, 'http://83.15.136.94:54321/axis2/services/PWebService', 'connId');
  RemClassRegistry.RegisterXSClass(carrierid, 'http://83.15.136.94:54321/axis2/services/PWebService', 'carrierid');
  RemClassRegistry.RegisterXSClass(vehicle, 'http://83.15.136.94:54321/axis2/services/PWebService', 'vehicle');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_sellingDataForStick), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_sellingDataForStick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSTiDocType), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSTiDocType');
  RemClassRegistry.RegisterXSClass(PWSTiSellingData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSellingData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSTiDiscount), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSTiDiscount');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSTiTariffForStick), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSTiTariffForStick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSTiTariffPriceAfterDiscount), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSTiTariffPriceAfterDiscount');
  RemClassRegistry.RegisterXSClass(sellingDataForStick, 'http://83.15.136.94:54321/axis2/services', 'sellingDataForStick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_price), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_price');
  RemClassRegistry.RegisterXSClass(PWSTiTariffForStick, 'http://83.15.136.94:54321/axis2/services', 'PWSTiTariffForStick');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiTariffForStick), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSCostForPeriod), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSCostForPeriod');
  RemClassRegistry.RegisterXSClass(PWSCosts, 'http://83.15.136.94:54321/axis2/services', 'PWSCosts');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSCarrierId), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSCarrierId');
  RemClassRegistry.RegisterXSClass(PWSCarrierSearcherParams, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierSearcherParams');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_ticket), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_ticket');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_periodicTicket), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_periodicTicket');
  RemClassRegistry.RegisterXSClass(order, 'http://83.15.136.94:54321/axis2/services', 'order');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_place), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_place');
  RemClassRegistry.RegisterXSClass(ticket, 'http://83.15.136.94:54321/axis2/services', 'ticket');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSStop), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSStop');
  RemClassRegistry.RegisterXSClass(PWSFullyQualifiedCityWithStops, 'http://83.15.136.94:54321/axis2/services', 'PWSFullyQualifiedCityWithStops');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSFullyQualifiedCityWithStops), 'name_', 'name');
  RemClassRegistry.RegisterXSClass(lineStop, 'http://83.15.136.94:54321/axis2/services', 'lineStop');
  RemClassRegistry.RegisterXSClass(cityStop, 'http://83.15.136.94:54321/axis2/services', 'cityStop');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_section), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_section');
  RemClassRegistry.RegisterXSClass(PWSTiPeriodicTicketLineInfo, 'http://83.15.136.94:54321/axis2/services', 'PWSTiPeriodicTicketLineInfo');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PWSTiPeriodicTicketLineInfo), 'type_', 'type');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_passenger), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_passenger');
  RemClassRegistry.RegisterXSClass(PWSTiSendNormalTicketData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSendNormalTicketData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_placeCause), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_placeCause');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSEnumParam), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSEnumParam');
  RemClassRegistry.RegisterXSClass(placeCause, 'http://83.15.136.94:54321/axis2/services', 'placeCause');
  RemClassRegistry.RegisterXSClass(PWSTiTicketUnavailableFaultData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiTicketUnavailableFaultData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_long), 'http://www.w3.org/2001/XMLSchema', 'Array_Of_long');
  RemClassRegistry.RegisterXSClass(PWSGetStopParam, 'http://83.15.136.94:54321/axis2/services', 'PWSGetStopParam');
  RemClassRegistry.RegisterXSClass(cityName, 'http://83.15.136.94:54321/axis2/services/PWebService', 'cityName');
  RemClassRegistry.RegisterXSClass(PWSTiReservationCancelRange, 'http://83.15.136.94:54321/axis2/services', 'PWSTiReservationCancelRange');
  RemClassRegistry.RegisterXSClass(PWSSearchingParams, 'http://83.15.136.94:54321/axis2/services', 'PWSSearchingParams');
  RemClassRegistry.RegisterXSClass(PWSTiWebServiceUserSellingConfig, 'http://83.15.136.94:54321/axis2/services', 'PWSTiWebServiceUserSellingConfig');
  RemClassRegistry.RegisterXSClass(carriers, 'http://83.15.136.94:54321/axis2/services', 'carriers');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_result), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_result');
  RemClassRegistry.RegisterXSClass(PWSTiSearchingResultWithSellingData, 'http://83.15.136.94:54321/axis2/services', 'PWSTiSearchingResultWithSellingData');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_stick), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_stick');
  RemClassRegistry.RegisterXSClass(result2, 'http://83.15.136.94:54321/axis2/services', 'result2', 'result');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_int), 'http://www.w3.org/2001/XMLSchema', 'Array_Of_int');
  RemClassRegistry.RegisterXSClass(stick2, 'http://83.15.136.94:54321/axis2/services', 'stick2', 'stick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_holder), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_holder');
  RemClassRegistry.RegisterXSClass(holdersForStick, 'http://83.15.136.94:54321/axis2/services', 'holdersForStick');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PTiPlace), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PTiPlace');
  RemClassRegistry.RegisterXSClass(ticket2, 'http://83.15.136.94:54321/axis2/services', 'ticket2', 'ticket');
  RemClassRegistry.RegisterXSClass(holder4, 'http://83.15.136.94:54321/axis2/services', 'holder4', 'holder');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSCarrierLine), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSCarrierLine');
  RemClassRegistry.RegisterXSClass(PWSCarrierLines, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierLines');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSSearchingParams), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSSearchingParams');
  RemClassRegistry.RegisterXSClass(machineConfig, 'http://83.15.136.94:54321/axis2/services', 'machineConfig');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_role), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_role');
  RemClassRegistry.RegisterXSClass(PWSUser, 'http://83.15.136.94:54321/axis2/services', 'PWSUser');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_discount), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_discount');
  RemClassRegistry.RegisterXSClass(stickDiscount, 'http://83.15.136.94:54321/axis2/services', 'stickDiscount');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_relation), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_relation');
  RemClassRegistry.RegisterXSClass(PWSCarrierRelations, 'http://83.15.136.94:54321/axis2/services', 'PWSCarrierRelations');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_departure), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_departure');
  RemClassRegistry.RegisterXSClass(PWSTimeTable, 'http://83.15.136.94:54321/axis2/services', 'PWSTimeTable');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSStopInTimeForTimeTable), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSStopInTimeForTimeTable');
  RemClassRegistry.RegisterXSClass(departure, 'http://83.15.136.94:54321/axis2/services', 'departure');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_price2), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_price2', 'Array_Of_price');
  RemClassRegistry.RegisterXSClass(PTiTariffForStick, 'http://83.15.136.94:54321/axis2/services', 'PTiTariffForStick');
  RemClassRegistry.RegisterExternalPropName(TypeInfo(PTiTariffForStick), 'name_', 'name');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSWaypoint), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSWaypoint');
  RemClassRegistry.RegisterXSClass(PWSTrackRecording, 'http://83.15.136.94:54321/axis2/services', 'PWSTrackRecording');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_ticket2), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_ticket2', 'Array_Of_ticket');
  RemClassRegistry.RegisterXSClass(PWSTiDetailedReservation, 'http://83.15.136.94:54321/axis2/services', 'PWSTiDetailedReservation');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_place2), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_place2', 'Array_Of_place');
  RemClassRegistry.RegisterXSClass(ticket3, 'http://83.15.136.94:54321/axis2/services', 'ticket3', 'ticket');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_param), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_param');
  RemClassRegistry.RegisterXSClass(PWSResultPriceDetailsParams, 'http://83.15.136.94:54321/axis2/services', 'PWSResultPriceDetailsParams');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_result2), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_result2', 'Array_Of_result');
  RemClassRegistry.RegisterXSClass(PWSSearchingResult, 'http://83.15.136.94:54321/axis2/services', 'PWSSearchingResult');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_causesForTicket), 'http://83.15.136.94:54321/axis2/services/PWebService', 'Array_Of_causesForTicket');
  RemClassRegistry.RegisterXSClass(PWSTiSendTickets, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiSendTickets');
  RemClassRegistry.RegisterXSInfo(TypeInfo(Array_Of_PWSTiTicketUnavailableFaultData), 'http://83.15.136.94:54321/axis2/services', 'Array_Of_PWSTiTicketUnavailableFaultData');
  RemClassRegistry.RegisterXSClass(PWSTiOrderUnavailable, 'http://83.15.136.94:54321/axis2/services/PWebService', 'PWSTiOrderUnavailable');


end.