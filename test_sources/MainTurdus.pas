unit MainTurdus;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, StdCtrls, PlatformDefaultStyleActnCtrls, ActnList, ActnMan,
  ComCtrls, JvExComCtrls, JvStatusBar, ImgList, ToolWin, ActnCtrls, ActnMenus,
  StdActns, DB, CategoryButtons, BasicClasses, FormBasicMain, Buttons,
  JvProgressBar, JvExControls, JvSpecialProgress,
  JvComponentBase, CoordinationFrame, LPCReliefTicketPaymentsMAZParameters,
  HTMLHelpViewer, System.Actions, System.ImageList, System.UITypes,
  IdComponent, uCEFChromiumCore, uCEFChromium, uCEFConstants, uCEFInterfaces,
  uCEFTypes, uCEFWindowParent, uCEFApplication, uCEFWinControl, IdBaseComponent,
  IdTCPConnection, IdTCPClient, IdExplicitTLSClientServerBase, IdFTP,
  IdIOHandler, IdIOHandlerSocket, IdIOHandlerStack, IdSSL, IdSSLOpenSSL;

const
  MYBROWSER_CEF_AFTERCREATED2                  = WM_APP + $101;
  MYBROWSER_CEF_DESTROY2                       = WM_APP + $102;

type
  // Chyba nieu¿ywane w ¿adnym module ? MJ 2014-07-24
  // TViewProc = procedure(ADataSet: TDataSet; ADatabaseItem: TDatabaseItem);

  TfrmMainTurdus = class(TBasicMainForm)
    pMainPanel: TPanel;
    pFloatingPanel: TPanel;
    stdtxtFloatingPanelCaption: TStaticText;
    actmgrMain: TActionManager;
    tmrLive: TTimer;
    jvstbarMain: TJvStatusBar;
    actFileLogOut: TAction;
    actviewStart: TAction;
    tmrIdle: TTimer;
    tmrLogout: TTimer;
    imglErrorHint: TImageList;
    imglLargeActDis: TImageList;
    imglLargeActHot: TImageList;
    imglLargeAct: TImageList;
    imglAct: TImageList;
    imglActDis: TImageList;
    actmenubarMain: TActionMainMenuBar;
    toolbarMain: TToolBar;
    toolbtnStart: TToolButton;
    toolbtnSettings_Separator: TToolButton;
    actFileExit: TFileExit;
    pctrlMain: TPageControl;
    tsheetStart: TTabSheet;
    tsheetSettings: TTabSheet;
    toolbtnSettings: TToolButton;
    actviewSettings: TAction;
    actmgrSettings: TActionManager;
    actSettingsLicences: TAction;
    tsheetDict: TTabSheet;
    toolbtnDictionary: TToolButton;
    actviewDictionary: TAction;
    actFileUsersGroups: TAction;
    actFilePassword: TAction;
    toolbtnRoute_Separator: TToolButton;
    toolbtnTicket: TToolButton;
    actViewTickets: TAction;
    tsheetTickets: TTabSheet;
    actviewRoute: TAction;
    actmgrRoute: TActionManager;
    tsheetRoute: TTabSheet;
    actrouteRideTypeCommunication: TAction;
    actrouteRideCommunicationNetwork: TAction;
    actrouteRideServiceType: TAction;
    toolbtnRoute: TToolButton;
    actmgrDictionary: TActionManager;
    actdictCountry: TAction;
    actdictProvince: TAction;
    actdictDistrict: TAction;
    actdictBorough: TAction;
    actdictPlace: TAction;
    actdictBusStop: TAction;
    actdictRoadPoint: TAction;
    actdictRoad: TAction;
    actdictCalendar: TAction;
    actdictRideDesignation: TAction;
    actdictGovWoj: TAction;
    actdictGovPow: TAction;
    actdictGovGmi: TAction;
    actdictGovMie: TAction;
    actdictGovGro: TAction;
    actdictCompany: TAction;
    actdictCashDepositMachineGLOBE: TAction;
    actdictDeviceOfAccounting: TAction;
    actdictTicketControlDev: TAction;
    actdictEmCardLoader_SR: TAction;
    actdictEmCardLoader_CT: TAction;
    actmgrTariffAndTicket: TActionManager;
    actPriceList: TAction;
    actVatRate: TAction;
    actCurrency: TAction;
    actTicketsPriceScaleOne: TAction;
    actTicketsFarePriceReductionAmount: TAction;
    actFarePriceScaleXRefOne: TAction;
    actTicketsPriceScaleBasicCity: TAction;
    actticketsPriceScaleCity: TAction;
    actticketsPriceScaleMonth: TAction;
    actticketsPriceScaleMonthCity: TAction;
    actticketsFarePriceReductionRoundMethod: TAction;
    actticketsFarePriceReductionGroup: TAction;
    actticketsFarePriceReductionAct: TAction;
    actticketsFarePriceReductionCommercial: TAction;
    actticketsFarePriceReductionWorkers: TAction;
    actdictFarePriceScaleDesignation: TAction;
    actdictFarePriceReductionDesignation: TAction;
    // actdictCalendar: TAction;
    // actdictRideDesignation: TAction;
    // ToolButton4: TToolButton;
    // toolbtnTicket: TToolButton;
    // actViewTickets: TAction;
    // tsheetTickets: TTabSheet;
    actrouteLine: TAction;
    actrouteRide: TAction;
    actrouteTimeTablesManage: TAction;
    actrouteRideExpPrefSets: TAction;
    actrouteRideSalePrefSets: TAction;
    actrouteRideBusTableConfPrefSet: TAction;
    pFormDatabaseItemChoice: TPanel;
    tsheetSale: TTabSheet;
    toolbtnAccounts: TToolButton;
    actdictTicketRegister4Sales: TAction;
    actdictTicketRegister4Buses: TAction;
    actSettingsParameters: TAction;
    actSettingsImport: TAction;
    toolbtnDeviceManager_Separator: TToolButton;
    actmgrDeviceManager: TActionManager;
    actviewDeviceManager: TAction;
    toolbtnStart_Separator: TToolButton;
    toolbtnDeviceManager: TToolButton;
    tsheetDeviceManager: TTabSheet;
    actrouteTimeTablePrint: TAction;
    actrouteRideServiceDesignation: TAction;
    actdictMobileDevice: TAction;
    actviewAccounts: TAction;
    actviewAnalysis: TAction;
    actviewTicketControler: TAction;
    actviewInspection: TAction;
    actviewInformation: TAction;
    toolbtnInformation: TToolButton;
    toolbtnAnalysis_Separator: TToolButton;
    toolbtnAnalysis: TToolButton;
    toolbtnPlanning_Separator: TToolButton;
    toolbtnPlanning: TToolButton;
    toolbtnInspection_Separator: TToolButton;
    toolbtnInspection: TToolButton;
    toolbtnTicketControler_Separator: TToolButton;
    toolbtnTicketControler: TToolButton;
    toolbtnDictionary_Separator: TToolButton;
    tsheetAccounts: TTabSheet;
    tsheetAnalysis: TTabSheet;
    tsheetTicketControler: TTabSheet;
    tsheetInspection: TTabSheet;
    tsheetInformation: TTabSheet;
    actmgrAccounts: TActionManager;
    Action33: TAction;
    actmgrAnalysis: TActionManager;
    actAnalysesREPORT_TYPE_ACCOUNTS: TAction;
    actAnalysesREPORT_TYPE_TICKETS_ADDS: TAction;
    actAnalysesREPORT_TYPE_SALES_ANALYSES: TAction;
    actAnalysesREPORT_TYPE_TRANSPORT: TAction;
    actAnalysesREPORT_TYPE_PASSANGER_TRANSPORT: TAction;
    actdictDriver: TAction;
    actdictBusGroup: TAction;
    actdictBus: TAction;
    actdictCombustionStandards: TAction;
    actdictBusPC: TAction;
    actticketsFarePriceReductionNumberingBuses: TAction;
    actticketsFarePriceReductionNumberingStationary: TAction;
    actTicketRegisterCard: TAction;
    actmgrInspection: TActionManager;
    actInspection: TAction;
    actInspectionBusRuns: TAction;
    actdictDriverGroup: TAction;
    actTicketRegisterAdditionalFee: TAction;
    actdictDriverSelParams: TAction;
    actdictBusStandParams: TAction;
    actmgrPlanning: TActionManager;
    actviewPlanning: TAction;
    actPlanTechnicalRide: TAction;
    tsheetPlan: TTabSheet;
    actPlanContractRide: TAction;
    cbIdle: TCheckBox;
    actInspectionRJA: TAction;
    actExemplarTable: TAction;
    actrouteTableDefinition: TAction;
    actroutePrintRJATable: TAction;
    acttikcetsFarePriceReductionRideXRef: TAction;
    actRegistrationSettlements: TAction;
    actRegistrationParameters: TAction;
    actSalesReportLoader: TAction;
    actDISPFileList: TAction;
    actticketsTicketZone: TAction;
    actImportSettlements: TAction;
    actDISPFileListEP: TAction;
    actEmar105TicketsCancellation: TAction;
    actAccountsPassenger: TAction;
    actAccountsEmCards: TAction;
    actdictCashiers: TAction;
    actmgrInformation: TActionManager;
    actroutePrintTimeTablesManage: TAction;
    actcoordinationPlateDefinition: TAction;
    actcoordinationPrintPlate: TAction;
    actcoordinationTableDefinition: TAction;
    actcoordinationPrintRJATable: TAction;
    actBusStopManage: TAction;
    actBusStopFeeType: TAction;
    actBusStopFeePayment: TAction;
    actBusStopsCompanies: TAction;
    actBusStopReport: TAction;
    actDISPFileListRJA: TAction;
    actCashReports: TAction;
    actDISPFileListINF: TAction;
    actSalesReportTransport: TAction;
    actTicketReliefPayment: TAction;
    actAnalysesREPORT_TYPE_PUNCTUALITY_RIDES: TAction;
    actAnalysesREPORT_TYPE_BUS_STOP: TAction;
    actAnalysesRJA: TAction;
    actrouteCollisions: TAction;
    actHelpContents: TAction;
    actviewShowToolBar: TAction;
    actDataInformation: TAction;
    tsheetBusStops: TTabSheet;
    actmgrBusStops: TActionManager;
    actBusStopRegistry: TAction;
    actBusStandNamePrefSet: TAction;
    actBusStopsCompanies2: TAction;
    actBusStopsTransporters: TAction;
    actRoads: TAction;
    actBusStopManage2: TAction;
    actBusStopFeeType2: TAction;
    actBusStopFeePayment2: TAction;
    actBusStopReport2: TAction;
    actviewBusStops: TAction;
    toolbtnBusStops: TToolButton;
    ctDISPFileListEP_Information: TAction;
    actEPodroznik: TAction;
    toolbtnBusStops_Separator: TToolButton;
    actFileHistory: TAction;
    actBusStopTimeTable: TAction;
    actBusStopTimeTableAnalysis: TAction;
    actPlanTask: TAction;
    actPlanDriver: TAction;
    actPlanDriverGroup: TAction;
    actPlanDriverSelParams: TAction;
    actPlanCombustionStandards: TAction;
    actPlanBusGroup: TAction;
    actPlanBus: TAction;
    ChromiumMain: TChromium; //Chromium
    TimerMain: TTimer;
    Chromium2: TChromium;
    Timer2: TTimer;
    actPlanRideGroup: TAction;
    actPlanGroupTask: TAction;
    IdFTP1: TIdFTP;
    IdSSLIOHandlerSocketOpenSSL1: TIdSSLIOHandlerSocketOpenSSL;
    ToolButtonSepaM: TToolButton;
    actRJAInformation: TAction;       //Chromium
    procedure FormCreate(Sender: TObject);
    procedure pFloatingPanelMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
    procedure pFloatingPanelResize(Sender: TObject);
    procedure tmrLiveTimer(Sender: TObject);
    procedure actFileLogOutExecute(Sender: TObject);
    procedure tmrIdleTimer(Sender: TObject);
    procedure tmrLogoutTimer(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure actviewStartExecute(Sender: TObject);
    procedure actviewSettingsExecute(Sender: TObject);
    procedure actSettingsLicencesExecute(Sender: TObject);
    procedure actdictCountryExecute(Sender: TObject);
    procedure actviewDictionaryExecute(Sender: TObject);
    procedure actdictProvinceExecute(Sender: TObject);
    procedure actdictDistrictExecute(Sender: TObject);
    procedure actdictBoroughExecute(Sender: TObject);
    procedure actdictPlaceExecute(Sender: TObject);
    procedure actdictRoadExecute(Sender: TObject);
    procedure actdictRoadPointExecute(Sender: TObject);
    procedure actdictBusStopExecute(Sender: TObject);
    procedure actdictTicketControlDevExecute(Sender: TObject);
    procedure actdictEmCardLoaderExecute(Sender: TObject);
    procedure actdictAutocashier(Sender: TObject);
    procedure actdictGovWojExecute(Sender: TObject);
    procedure actdictCompanyExecute(Sender: TObject);
    procedure actFilePasswordExecute(Sender: TObject);
    procedure actFileUsersGroupsExecute(Sender: TObject);
    procedure actdictCalendarExecute(Sender: TObject);
    procedure actdictRideDesignationExecute(Sender: TObject);
    procedure actViewTicketsExecute(Sender: TObject);
    procedure actrouteRideTypeCommunicationExecute(Sender: TObject);
    procedure actviewRouteExecute(Sender: TObject);
    procedure actrouteRideCommunicationNetworkExecute(Sender: TObject);
    procedure actrouteRideServiceTypeExecute(Sender: TObject);
    procedure actrouteRideExpPrefSetsExecute(Sender: TObject);
    procedure actrouteRideSalePrefSetsExecute(Sender: TObject);
    procedure actrouteRideBusTableConfPrefSetExecute(Sender: TObject);
    procedure actrouteLineExecute(Sender: TObject);
    procedure actrouteRideExecute(Sender: TObject);
    procedure actPriceListExecute(Sender: TObject);
    procedure actVatRateExecute(Sender: TObject);
    procedure actCurrencyExecute(Sender: TObject);
    procedure actTicketsPriceScaleOneExecute(Sender: TObject);
    procedure actTicketsFarePriceReductionAmountExecute(Sender: TObject);
    procedure actFarePriceScaleXRefOneExecute(Sender: TObject);
    procedure actticketsPriceScaleCityExecute(Sender: TObject);
    procedure actTicketsPriceScaleBasicCityExecute(Sender: TObject);
    procedure actticketsTicketZoneExecute(Sender: TObject);
    procedure actticketsPriceScaleMonthExecute(Sender: TObject);
    procedure actticketsPriceScaleMonthCityExecute(Sender: TObject);
    procedure actticketsFarePriceReductionRoundMethodExecute(Sender: TObject);
    procedure actticketsFarePriceReductionGroupExecute(Sender: TObject);
    procedure actticketsFarePriceReductionActExecute(Sender: TObject);
    procedure actticketsFarePriceReductionCommercialExecute(Sender: TObject);
    procedure actticketsFarePriceReductionWorkersExecute(Sender: TObject);
    procedure acttikcetsFarePriceReductionRideXRefExecute(Sender: TObject);
    procedure actdictFarePriceScaleDesignationExecute(Sender: TObject);
    procedure actdictFarePriceReductionDesignationExecute(Sender: TObject);
    procedure FormResize(Sender: TObject);
    procedure actrouteTimeTablesManageExecute(Sender: TObject);
    procedure actdictTicketRegister(Sender: TObject);
    procedure actdictBusStopTicketZoneExecute(Sender: TObject);
    procedure actviewDeviceManagerExecute(Sender: TObject);
    procedure actrouteRideServiceDesignationExecute(Sender: TObject);
    procedure actviewAccountsExecute(Sender: TObject);
    procedure actviewAnalysisExecute(Sender: TObject);
    procedure actviewTicketControlerExecute(Sender: TObject);
    procedure actviewInspectionExecute(Sender: TObject);
    procedure actviewInformationExecute(Sender: TObject);
    procedure actdictDriverExecute(Sender: TObject);
    procedure actdictBusExecute(Sender: TObject);
    procedure actdictBusGroupExecute(Sender: TObject);
    procedure actdictCombustionStandardsExecute(Sender: TObject);
    procedure actdictBusPCExecute(Sender: TObject);
    procedure actticketsFarePriceReductionNumberingBusesExecute(Sender: TObject);
    procedure actticketsFarePriceReductionNumberingStationaryExecute(Sender: TObject);
    procedure actDISPFileSoloBusExecute(Sender: TObject);
    procedure actDISPFileEmar105Execute(Sender: TObject);
    procedure actTicketRegisterCardExecute(Sender: TObject);
    procedure actdictMobileDeviceExecute(Sender: TObject);
    procedure actInspectionExecute(Sender: TObject);
    procedure actInspectionBusRunsExecute(Sender: TObject);
    procedure actdictDriverGroupExecute(Sender: TObject);
    procedure actDeviceFarePriceScaleSingleTicketExecute(Sender: TObject);
    procedure actTRPSolobusExecute(Sender: TObject);
    procedure actTicketRegisterAdditionalFeeExecute(Sender: TObject);
    procedure actdictDriverSelParamsExecute(Sender: TObject);
    procedure actdictBusStandParamsExecute(Sender: TObject);
    procedure actSettingsImportExecute(Sender: TObject);
    procedure actSettingsParametersExecute(Sender: TObject);
    procedure actviewPlanningExecute(Sender: TObject);
    procedure actPlanTechnicalRideExecute(Sender: TObject);
    procedure actPlanContractRideExecute(Sender: TObject);
    procedure actSalesReportExecute(Sender: TObject);
    procedure actDISPFileListExecute(Sender: TObject);
//    procedure actTicketRegisterFileViewerExecute(Sender: TObject);
    procedure actSalesReportLoaderExecute(Sender: TObject);
    procedure cbIdleClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure actInspectionRJAExecute(Sender: TObject);
    procedure actrouteTableDefinitionExecute(Sender: TObject);
    procedure actroutePrintRJATableExecute(Sender: TObject);
    procedure actrouteOtherTablesExecute(Sender: TObject);
    procedure actRegistrationSettlementsExecute(Sender: TObject);
    procedure actImportSettlementsExecute(Sender: TObject);
    procedure actRegistrationParamsExecute(Sender: TObject);
    procedure actDISPFileListEPExecute(Sender: TObject);
    procedure actAccountsPassengerExecute(Sender: TObject);
    procedure actAccountsEmCardsExecute(Sender: TObject);
    procedure actdictCashiersExecute(Sender: TObject);
    procedure Action33Execute(Sender: TObject);
    procedure actroutePrintTimeTablesManageExecute(Sender: TObject);
    procedure actcoordinationPlateDefinitionExecute(Sender: TObject);
    procedure actcoordinationPrintPlateExecute(Sender: TObject);
    procedure actcoordinationTableDefinitionExecute(Sender: TObject);
    procedure actcoordinationPrintRJATableExecute(Sender: TObject);
    procedure actEPodroznikExecute(Sender: TObject);
    procedure actBusStopsCompaniesExecute(Sender: TObject);
    procedure actBusStopManageExecute(Sender: TObject);
    procedure actBusStopFeeTypeExecute(Sender: TObject);
    procedure actBusStopFeePaymentExecute(Sender: TObject);
    procedure actBusStopReportExecute(Sender: TObject);
    procedure actDISPFileListRJAExecute(Sender: TObject);
    procedure actEmar105TicketsCancellationExecute(Sender: TObject);
    procedure actDISPFileListINFExecute(Sender: TObject);
    procedure actCashReportsExecute(Sender: TObject);
    procedure actSalesReportTransportExecute(Sender: TObject);
    procedure actTicketReliefPaymentExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_PUNCTUALITY_RIDESExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_PASSANGER_TRANSPORTExecute(Sender: TObject);
    procedure actReportsTransportExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_BUS_STOPExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_ACCOUNTSExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_TICKETS_ADDSExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_TRANSPORTExecute(Sender: TObject);
    procedure actAnalysesRJAExecute(Sender: TObject);
    procedure actAnalysesREPORT_TYPE_SALES_ANALYSESExecute(Sender: TObject);
    procedure actrouteCollisionsExecute(Sender: TObject);
    procedure actHelpContentsExecute(Sender: TObject);
    procedure actviewShowToolBarExecute(Sender: TObject);
    procedure actDataInformationExecute(Sender: TObject);
    procedure actviewBusStopsExecute(Sender: TObject);
    procedure actBusStopRegistryExecute(Sender: TObject);
    procedure actBusStandNamePrefSetExecute(Sender: TObject);
    procedure actBusStopsTransportersExecute(Sender: TObject);
    procedure actRoadsExecute(Sender: TObject);
    procedure actBusStopsCompanies2Execute(Sender: TObject);
    procedure actBusStopManage2Execute(Sender: TObject);
    procedure actBusStopFeeType2Execute(Sender: TObject);
    procedure actBusStopFeePayment2Execute(Sender: TObject);
    procedure actBusStopReport2Execute(Sender: TObject);
    procedure ctDISPFileListEP_InformationExecute(Sender: TObject);
    procedure actRatesForWagonkilometerExecute(Sender: TObject);
    procedure actFileHistoryExecute(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure actBusStopTimeTableExecute(Sender: TObject);
    procedure actBusStopTimeTableAnalysisExecute(Sender: TObject);
    procedure actPlanDriverExecute(Sender: TObject);
    procedure actPlanDriverGroupExecute(Sender: TObject);
    procedure actPlanDriverSelParamsExecute(Sender: TObject);
    procedure actPlanCombustionStandardsExecute(Sender: TObject);
    procedure actPlanBusGroupExecute(Sender: TObject);
    procedure actPlanBusExecute(Sender: TObject);
    procedure actPlanTaskExecute(Sender: TObject);
    procedure TimerMainTimer(Sender: TObject);
    procedure ChromiumMainAfterCreated(Sender: TObject; const browser: ICefBrowser);
    procedure ChromiumMainBeforeClose(Sender: TObject;  const browser: ICefBrowser);
    procedure ChromiumMainClose(Sender: TObject; const browser: ICefBrowser;  var aAction: TCefCloseBrowserAction);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);
    procedure ChromiumMainLoadingStateChange(Sender: TObject; const browser: ICefBrowser; isLoading, canGoBack, canGoForward: Boolean);
    procedure Timer2Timer(Sender: TObject);
    procedure Chromium2AfterCreated(Sender: TObject; const browser: ICefBrowser);
    procedure Chromium2BeforeClose(Sender: TObject; const browser: ICefBrowser);
    procedure Chromium2Close(Sender: TObject; const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
    procedure actPlanRideGroupExecute(Sender: TObject);
    procedure actPlanGroupTaskExecute(Sender: TObject);
    procedure actRJAInformationExecute(Sender: TObject);
  private
    { Private declarations }
    fTimeonIDLE: TDateTime;
    frameStartChromium: TFrame;     //Chromium
    frameSettings: TFrame;
    frameDictionary: TFrame;
    frameRoute: TFrame;
    frameTariffAndTicket: TFrame;
    frameDeviceManager: TFrame;
    frameAccounts: TFrame;
    frameAnalysis: TFrame;
    frameInspection: TFrame;
    framePlan: TFrame;
    frameBusStops : TFrame;
    frameInformation : TframeCoordination;
    fFirstActive: Boolean;
    procedure ActionEnabled;
    procedure SQLConnectionAfterDisconnect(Sender: TObject);
    {$IFNDEF  EUREKALOG}
    procedure AppException(Sender: TObject; E: Exception);
    {$ENDIF}
    procedure CreateFrames;
    procedure DestroyFrames;
    procedure AfterLoadLicence(Sender: TObject);
    procedure SetMessage(AMessage: string);
    procedure AssignActions;
    procedure BeforeDictView(AProcName: String);
    procedure BeforeFuncView(AProcName: String);
    procedure BeforeView(AProcName, AMsg: String);
    procedure ExecuteFirstAction(actmgr: TActionManager);
    procedure RefreshPriceList(CompanyID: Integer = 0);
    procedure ViewDictTicketRegister(AType: Integer);
    procedure ViewDictSaleDeviceTicketRegister(AType: Integer);
    procedure AssignTagsToActions;

    {$IFNDEF TURDUS_AP}
    procedure StartDownload(ASender: TObject; AWorkMode: TWorkMode; AWorkCountMax: Int64);
    procedure Download(ASender: TObject; AWorkMode: TWorkMode; AWorkCount: Int64);
    {$ENDIF}

  protected
    procedure DoShowChoicePanelOwnerSettings(AParams: Array of Variant; Var BDoNotClearChoicePanel: Boolean); override;
    function DoChoicePanelButtonChoiceClick(Var AID: Integer; Var AName: String): Boolean; override;
  public
    { Public declarations }
    CEFWindowParentMain : TCEFWindowParent; //Chromium
    FCanClose : boolean;  //Chromium
    FClosing  : boolean;  //Chromium

    CEFWindowParentMain2 : TCEFWindowParent; //Chromium
    FCanClose2 : boolean;  //Chromium

    FFirstClosingAsk : boolean;

    procedure BrowserCreatedMsg(var aMessage : TMessage); message CEF_AFTERCREATED; //Chromium
    procedure BrowserDestroyMsg(var aMessage : TMessage); message CEF_DESTROY;      //Chromium

    procedure BrowserCreatedMsg2(var aMessage : TMessage); message MYBROWSER_CEF_AFTERCREATED2; //Chromium
    procedure BrowserDestroyMsg2(var aMessage : TMessage); message MYBROWSER_CEF_DESTROY2;      //Chromium

    constructor Create(AOwner: TComponent); override;

    procedure StopBusTraceTimer;

    procedure PrepareInterface; override;
    procedure UnPrepareInterface; override;

  end;

var
  frmMainTurdus: TfrmMainTurdus;

implementation

{$REGION 'uses'}

uses
  KMBasicUtil,
  DateUtils,
  FileLog, AppFileLog, Globals, ResourceStrings, MainDM, MainFormUtil, KMUtils,
  XMLLicences, LicenceUtil, Privilages, ClientLicence, ControlErrorFrame,
  CommonDM, SettingsFrame, AutoCashier, EmCardLoader, TurdusParameters,
  PasswordFrm, UsersGroupsFrm, KMLog, RouteFrame, DictionaryFrame, TicketFrame,
  TicketRegister, InfoFormatedHint, DeviceManagerFrame,
  AccountsFrame, AnalysisFrame, InspectionFrame, BusPC, Busses, KMControlUtils,
  HistoryForm, FramesHelpers, PlanFrame, Mask
//  {$IFNDEF DEBUG}
  ,ModuleAvaibility
//  {$ENDIF}
  , Generics.Collections
  , LicencesCompanyUnit
  , GlobalTypes
  , ComponentsVersion
  , ApplicationVersionChecking
  , UserSettings
  , IniFiles
  , ProductVersionUtil
  , BusStopsFrame
  , Splash
  , UpdaterDataModule
  , StartFrameChromium //Chromium
  ;

{$ENDREGION}
{$R *.dfm}

procedure TfrmMainTurdus.actTicketRegisterAdditionalFeeExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
  //    dmMainGlobal.DataSetOpen(dmMainGlobal.cdsAdditionalFees);
      TframeTicket(frameTariffAndTicket).ViewTicketRegisterAdditionalFee(dmMainGlobal.cdsAdditionalFees);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAccountsEmCardsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeAccounts(frameAccounts).ViewEmCards(dmMainGlobal.cdsStoredProcEmCard,[]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAccountsPassengerExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    LockWindowUpdate(Self.Handle);
    try
      LastView := (Sender as TAction);
      Params := Format('DriverType_ID=%d'#13'Company_ID=%d'#13'rowfrom=%d'#13'rowto=%d'#13'Filter=(Deleted=0)', [Integer(ptPassanger), GetChoicePanelDatabaseItemID,0,20]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      TframeAccounts(frameAccounts).ViewPassanger(dmMainGlobal.cdsStoredProcDrivers,[params]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_PASSANGER_TRANSPORTExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_PASSANGER_TRANSPORT]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameAnalysis,
                dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_PUNCTUALITY_RIDESExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_PUNCTUALITY_RIDES]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameAnalysis,
                dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_SALES_ANALYSESExecute(
  Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_SALES_ANALYSES]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameAnalysis,
                dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actInspectionRJAExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsDISP_BusRun_GetAll, IntToStr(GetLicencesCompanyID));
      //TframeAnalysis(frameAnalysis).ViewAnalysisRJA([]);
      TframeInspection(frameInspection).ViewAnalysisRJA([]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actBusStandNamePrefSetExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsBusStandNamePrefSets, TframeBusStops(FrameBusStops).ViewBusStandNamePrefSets)
  finally
    UnPrepareInterface;
    TFrameBusStops(FrameBusStops).FrameBaseGlossary.GridWithSearch.AutosizeGridColumns;
  end;
end;

procedure TfrmMainTurdus.actBusStopFeePayment2Execute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcBusStopFeeInvoice_SelectAll, TFrameBusStops(FrameBusStops).ViewBusStopFeeInvoice, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopFeePaymentExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameRoute, dmMainGlobal.cdsStoredProcBusStopFeeInvoice_SelectAll, TframeRoute(frameRoute).ViewBusStopFeeInvoice, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopFeeType2Execute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcFeeType_GetBusStopFee, TFrameBusStops(FrameBusStops).ViewFee, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopFeeTypeExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameRoute, dmMainGlobal.cdsStoredProcFeeType_GetBusStopFee, TframeRoute(frameRoute).ViewFee, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopManage2Execute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcBusStopCompanySelectAll, TFrameBusStops(FrameBusStops).ViewBusStopsManage, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopManageExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameRoute, dmMainGlobal.cdsStoredProcBusStopCompanySelectAll, TframeRoute(frameRoute).ViewBusStopsManage, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopRegistryExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    //ShowChoicePanel(ptCompany, [Format('companytype=%d', [Integer(kocOSK)])]);
    //Params := Format('DriverType_ID=%d,Company_ID=%d', [Integer(ptTrainer), GetChoicePanelDatabaseItemID]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    //dmMainGlobal.TCPIPServerMethods.PrepareBusStop;
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcBusStopsPagination, TframeBusStops(FrameBusStops).ViewBusStopsRegistry, Params, False)
  finally
    UnPrepareInterface;
    TframeBusStops(FrameBusStops).FrameBaseGlossary.GridWithSearch.AutosizeGridColumns;
  end;
end;

procedure TfrmMainTurdus.actBusStopReport2Execute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_BUS_STOP]);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameBusStops, dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId, TFrameBusStops(FrameBusStops).ViewReportBusStops, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopReportExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_BUS_STOP]);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameRoute, dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId, TframeRoute(frameRoute).ViewReportBusStops, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_BUS_STOPExecute(Sender: TObject);
var
  Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('%d', [REPORT_TYPE_BUS_STOP]);

    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameAnalysis, dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId, TframeAnalysis(frameAnalysis).ViewReportBusStops, Params);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopsCompanies2Execute(Sender: TObject);
var
   Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('GovType=%d|Company_ID=%d', [Integer(kocAdministrator), GetChoicePanelDatabaseItemID]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcGovOffice, TFrameBusStops(FrameBusStops).ViewBusStops, Params, False)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopsCompaniesExecute(Sender: TObject);
var
   Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    HideChoicePanel;
    Params := Format('GovType=%d|Company_ID=%d', [Integer(kocAdministrator), GetChoicePanelDatabaseItemID]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameRoute, dmMainGlobal.cdsStoredProcGovOffice, TframeRoute(frameRoute).ViewBusStops, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopsTransportersExecute(Sender: TObject);
var
   Params : string;
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
//    ShowChoicePanel(cptCompany, [Format('companytype=%d', [Integer(kocAdministrator)])]);
    HideChoicePanel;
    Params := Format('GovType=%d|Company_ID=%d', [Integer(kocPrzewoznik), GetChoicePanelDatabaseItemID]);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcGovOffice, TframeBusStops(FrameBusStops).ViewTransporters, Params, False)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopTimeTableAnalysisExecute(Sender: TObject);
var
   Params : string;
begin
  inherited;
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(frameAnalysis, dmMainGlobal.cdsTT_TimeTableGetAll, TframeAnalysis(frameAnalysis).ViewTimeTable, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actBusStopTimeTableExecute(Sender: TObject);
var
   Params : string;
begin
  inherited;
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
    ReloadFrame(FrameBusStops, dmMainGlobal.cdsTT_TimeTableGetAll, TFrameBusStops(FrameBusStops).ViewTimeTable, Params)
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actCashReportsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      TframeAccounts(frameAccounts).ViewCashReport(dmMainGlobal.cdsStoredProcCashReport, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actcoordinationPlateDefinitionExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    BeforeDictView((Sender As TAction).Caption);

    dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusStopTablePattern, 'Type_ID=0');
    frameInformation.viewPlateDefinition(dmMainGlobal.cdsStoredProcBusStopTablePattern);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actcoordinationPrintPlateExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    BeforeDictView((Sender As TAction).Caption);

 //   dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcTimeTableResult, '@Type=0');
    frameInformation.viewPrintPlate(dmMainGlobal.cdsStoredProcTimeTableResult);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actcoordinationPrintRJATableExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    BeforeDictView((Sender As TAction).Caption);

   // dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcTimeTableResult, '@Type=1');
    frameInformation.viewPrintRJATable(dmMainGlobal.cdsStoredProcTimeTableResult);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actcoordinationTableDefinitionExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    BeforeDictView((Sender As TAction).Caption);

    dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusStopTablePattern, 'Type_ID=1');
    frameInformation.viewTableDefinition(dmMainGlobal.cdsStoredProcBusStopTablePattern);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actCurrencyExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewCurrency(dmMainGlobal.cdsStoredProcCurrencies);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDeviceFarePriceScaleSingleTicketExecute(Sender: TObject);
// Var
// AParams: Array of Variant;
begin
  // SetLength(AParams, 4);
  // AParams[0] := StrParamChoicePanelType(cptCompany);
  // AParams[1] := cpDefaultLicenceCompany;
  // AParams[2] := cpDoNotSelect;
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
  {$IFNDEF PARUS}
//      if Sender = actDeviceFarePriceScaleSingleTicket then
//        TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskSingleTicket, [])
//        // TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskSingleTicket, AParams)
//      Else
//      if Sender = actDeviceFarePriceScaleCityTicket then
//        // TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskCityTicket, AParams)
//        TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskCityTicket, [])
//      Else
//      if Sender = actDeviceFarePriceScaleMonthTicket then
//        // TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskMonthTicket, AParams)
//        TframeRoute(frameRoute).ViewFarePriceScaleXRefManager(fpskMonthTicket, [])
  {$ENDIF}

    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictAutocashier(Sender: TObject);
var
  _ACType: TAutoCashierType;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      if Sender = actdictDeviceOfAccounting then
        _ACType := acDeviceOfAccounting
      else
        _ACType := acCashDepositMachineGLOBE;

      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStorProcAutoCashier, IntToStr(Ord(_ACType)));
      TframeDeviceManager(frameDeviceManager).ViewAutoCashier(dmMainGlobal.cdsStorProcAutoCashier, Ord(_ACType));
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBoroughExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsCommunityPagination);
      TFrameDictionary(frameDictionary).ViewBorough(dmMainGlobal.cdsCommunityPagination);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('%d', [Integer(VehicleType_Bus)]);

      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBuses, Params);
      TframeDeviceManager(frameDeviceManager).ViewBus(dmMainGlobal.cdsStoredProcBuses, [ { StrParamChoicePanelType(cptCompany) } ]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusGroupExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusGroups);
      TframeDeviceManager(frameDeviceManager).ViewBusGroup(dmMainGlobal.cdsStoredProcBusGroups, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusPCExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusPCStatus, bpcRequeryBoardComputers);
      TframeDeviceManager(frameDeviceManager).ViewBusPC(dmMainGlobal.cdsStoredProcBusPCStatus, StrToInt(bpcRequeryBoardComputers));
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusStandParamsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsBusStandNamePrefSets);
      TframeRoute(frameRoute).ViewBusStandNamePrefSets(dmMainGlobal.cdsBusStandNamePrefSets);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusStopExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      // dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusStops);
      TframeRoute(frameRoute).ViewBusStop(dmMainGlobal.cdsStoredProcBusStopsPagination);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictBusStopTicketZoneExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusStops);
      TframeTicket(frameTariffAndTicket).ViewBusStop(dmMainGlobal.cdsStoredProcBusStops);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictCalendarExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      TFrameDictionary(frameDictionary).ViewCalendar(dmMainGlobal.cdsStoredProcCalendar);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictCashiersExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('DriverType_ID=%d'#13'Company_ID=%d'#13'rowfrom=%d'#13'rowto=%d'#13'Filter=(Deleted=0)', [Integer(ptCashier), GetChoicePanelDatabaseItemID,0,20]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      dmMainGlobal.TCPIPServerMethods.PrepareDrivers;
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDrivers, Params);
      TframeDeviceManager(frameDeviceManager).ViewCashier(dmMainGlobal.cdsStoredProcDrivers, [
  {$IFDEF FORIS} StrParamChoicePanelType(cptCompany), {$ENDIF}
        cpDoNotSelect, cpDoNotClear]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictCombustionStandardsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      TframeDeviceManager(frameDeviceManager).ViewCombustionStandard(dmMainGlobal.cdsCombustionStandards, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictCompanyExecute(Sender: TObject);
var
 params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);

      Params := Format('GovType=%d'#13'rowfrom=%d'#13'rowto=%d', [Integer(kocPrzewoznik),0,20]);
      if dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcGovOffice, Params) then
        TFrameDictionary(frameDictionary).ViewCompany(dmMainGlobal.cdsStoredProcGovOffice);
    finally
      UnPrepareInterface;
    end;
  end;
end;


procedure TfrmMainTurdus.actdictCountryExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcCountries);
      TFrameDictionary(frameDictionary).ViewCountry(dmMainGlobal.cdsStoredProcCountries);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictDistrictExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDistricts);
      TFrameDictionary(frameDictionary).ViewDistrict(dmMainGlobal.cdsStoredProcDistricts);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictDriverExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('DriverType_ID=%d'#13'Company_ID=%d'#13'rowfrom=%d'#13'rowto=%d'#13'Filter=(Deleted=0)', [Integer(ptDriver), GetChoicePanelDatabaseItemID,0,20]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      dmMainGlobal.TCPIPServerMethods.PrepareDrivers;
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDrivers, Params);
      TframeDeviceManager(frameDeviceManager).ViewDriver(dmMainGlobal.cdsStoredProcDrivers, [
  {$IFDEF FORIS} StrParamChoicePanelType(cptCompany), {$ENDIF}
        cpDoNotSelect, cpDoNotClear]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictDriverGroupExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('@Mode=%d', [3]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);

      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDriverGroups, Params);
      TframeDeviceManager(frameDeviceManager).ViewDriverGroups(dmMainGlobal.cdsStoredProcDriverGroups, []);
    finally
      UnPrepareInterface
    end;
  end;
end;

procedure TfrmMainTurdus.actdictDriverSelParamsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDriverTicketRegPrefSet);
      TframeDeviceManager(frameDeviceManager).ViewDriverTicketRegPrefSet(dmMainGlobal.cdsStoredProcDriverTicketRegPrefSet, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictEmCardLoaderExecute(Sender: TObject);
var
  _ECLType: TEmCardLoaderType;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      if Sender = actdictEmCardLoader_SR then
        _ECLType := eclStationReader
      else
        _ECLType := eclChargeTerminal;

      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcEmCardLoader, IntToStr(Ord(_ECLType)));
      TframeDeviceManager(frameDeviceManager).ViewEmCardLoader(dmMainGlobal.cdsStoredProcEmCardLoader, Ord(_ECLType));
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictGovWojExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      TFrameDictionary(frameDictionary).ViewGovOffice(TAction(Sender).tag - 2001);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictMobileDeviceExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusPCStatus, bpcRequeryMobile);
      TframeDeviceManager(frameDeviceManager).ViewMobileBusPC(dmMainGlobal.cdsStoredProcBusPCStatus, StrToInt(bpcRequeryMobile));
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictTicketControlDevExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsTicketControlDev);
      TframeDeviceManager(frameDeviceManager).ViewTicketControlDev(dmMainGlobal.cdsTicketControlDev);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.ViewDictTicketRegister(AType: Integer);
begin
  dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStorProcTicketRegister4Buses, 'BusType=' + IntToStr(AType));
  TframeDeviceManager(frameDeviceManager).ViewTicketRegister(dmMainGlobal.cdsStorProcTicketRegister4Buses, AType);
end;

procedure TfrmMainTurdus.ViewDictSaleDeviceTicketRegister(AType: Integer);
begin
  dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStorProcTicketRegister4Buses, 'BusType=' + IntToStr(AType));
  TframeDeviceManager(frameDeviceManager).ViewSaleDeviceTicketRegister(dmMainGlobal.cdsStorProcTicketRegister4Buses, AType);
end;

procedure TfrmMainTurdus.actdictTicketRegister(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      if (Sender = actdictTicketRegister4Buses) then
        ViewDictTicketRegister(Ord(trEmar105))
//
//      else if (Sender = actdictTicketRegister4BusesSolo) then
//        ViewDictTicketRegister(Ord(trEmar305))
//
//      else if (Sender = actdictBusPC_EMAR205) then
//        ViewDictTicketRegister(Ord(trEmar205))

      else
        ViewDictSaleDeviceTicketRegister(Ord(trSaleDevice))
    finally
      UnPrepareInterface;
    end;
  end;
end;

//procedure TfrmMainTurdus.actdictTicketRegisterPrefSetExecute(Sender: TObject);
//begin
//  if LastView <> (Sender as TAction) then
//  begin
//    PrepareInterface;
//    try
//      LastView := (Sender as TAction);
//      BeforeFuncView((Sender As TAction).Caption);
//      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcTicketRegPrefSet);
//      TframeDeviceManager(frameDeviceManager).ViewTicketRegPrefSet(dmMainGlobal.cdsStoredProcTicketRegPrefSet, []);
//    finally
//      UnPrepareInterface;
//    end;
//  end;
//end;

procedure TfrmMainTurdus.actdictPlaceExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      TFrameDictionary(frameDictionary).ViewPlace(dmMainGlobal.cdsStoredProcPlacesPagination);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictProvinceExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcProvinces);
      TFrameDictionary(frameDictionary).ViewProvince(dmMainGlobal.cdsStoredProcProvinces);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictRideDesignationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcRideDesignation, '1');
      TFrameDictionary(frameDictionary).ViewRideDesignation(dmMainGlobal.cdsStoredProcRideDesignation);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictRoadExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcRoads);
      TframeRoute(frameRoute).ViewRoad(dmMainGlobal.cdsStoredProcRoadsPagination);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictRoadPointExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcRoadPoints);
      TframeRoute(frameRoute).ViewRoadPoint(dmMainGlobal.cdsStoredProcRoadPoints);
    finally
      UnPrepareInterface
    end;
  end;
end;

procedure TfrmMainTurdus.actFarePriceScaleXRefOneExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      if Sender = actFarePriceScaleXRefOne then
        TframeTicket(frameTariffAndTicket).ViewFarePriceScaleXRefManager(fpskSingleTicket, [])
//      Else
//       if Sender = actFarePriceScaleXRefCity then
//        TframeTicket(frameTariffAndTicket).ViewFarePriceScaleXRefManager(fpskCityTicket, [])
//      Else if Sender = actFarePriceScaleXRefMonthTicket then
//        TframeTicket(frameTariffAndTicket).ViewFarePriceScaleXRefManager(fpskMonthTicket, [])
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actFileLogOutExecute(Sender: TObject);
var
  b: Boolean;
begin
  b := Self.PasswordAlert;
  try
    LogoutUser(b, actFileLogOut, actviewStart, tmrLogout, tmrIdle, tmrLive, SQLConnectionAfterDisconnect, ActionEnabled);
  finally
    Self.PasswordAlert := b;
  end;
  Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
end;

procedure TfrmMainTurdus.actFilePasswordExecute(Sender: TObject);
begin
  PasswordChange(Sender as TAction, actFileLogout);
end;

procedure TfrmMainTurdus.actFileUsersGroupsExecute(Sender: TObject);
var
  frm: TfrmUsersGroups;
begin
  PrepareInterface;
  try
    frm := TfrmUsersGroups.Create(Self, CurrentUser, ClientAuthentication, AppParams.Id);
    try
      Log((Sender As TAction).Caption, _LOG_PROC_RUN);
      Screen.Cursor := crDefault;
      frm.ShowModal;
      Screen.Cursor := crHourGlass;
    finally
      frm.Free;
    end;
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actHelpContentsExecute(Sender: TObject);
begin
  inherited;
  Application.HelpContext(2400);
end;

procedure TfrmMainTurdus.actInspectionBusRunsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsDISP_BusRun_GetAll, IntToStr(GetLicencesCompanyID));
      TframeInspection(frameInspection).ViewBusRun(dmMainGlobal.cdsDISP_BusRun_GetAll, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actInspectionExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeInspection(frameInspection).InitializeGoogleMapBusesTrackingFrame;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.SetMessage(AMessage: string);
begin
  MessageStatusPanel.Text := AMessage;
  Application.ProcessMessages;
end;

procedure TfrmMainTurdus.actSettingsImportExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);
      TframeSettings(frameSettings).ImportFromFile;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actSettingsLicencesExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeSettings(frameSettings).ViewLicences;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actSettingsParametersExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameSettings, dmMainGlobal.cdsStoredProcLPC_Parameters, TframeSettings(frameSettings).ViewLPCParameters, IntToStr(AppParams.Id));
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionActExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionAct(dmMainGlobal.cdsStoredProcFarePriceReductionAct);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTicketsFarePriceReductionAmountExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 5;
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionAmount(dmMainGlobal.cdsStoredProcFarePriceReductionAmounts);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionCommercialExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionCommercial(dmMainGlobal.cdsStoredProcFarePriceReductionCommercial);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionGroupExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionGroup(dmMainGlobal.cdsStoredProcFarePriceReductionGroup);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionNumberingBusesExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionNumberingInBuses(nil);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionNumberingStationaryExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionNumberingInStationary(nil);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionRoundMethodExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionRoundMethod(dmMainGlobal.cdsStoredProcFarePriceReductionRoundMethod);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsFarePriceReductionWorkersExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionWorkers(dmMainGlobal.cdsStoredProcFarePriceReductionWorkers);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTicketsPriceScaleBasicCityExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 3;
      TframeTicket(frameTariffAndTicket).ViewPriceBasicCity(dmMainGlobal.cdsStoredProcPriceBasicCitiesScales);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsPriceScaleCityExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 2;
      TframeTicket(frameTariffAndTicket).ViewPriceCity(dmMainGlobal.cdsStoredProcPriceCitiesScales);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsPriceScaleMonthCityExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 6;
      TframeTicket(frameTariffAndTicket).ViewPriceMonthCity(dmMainGlobal.cdsStoredProcPriceMonthCityScales);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsPriceScaleMonthExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 4;
      TframeTicket(frameTariffAndTicket).ViewPriceMonth(dmMainGlobal.cdsStoredProcPriceMonthScales);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTicketsPriceScaleOneExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).PriceFrame.Mode := 1;
      TframeTicket(frameTariffAndTicket).ViewPriceScale(dmMainGlobal.cdsStoredProcPriceOnesScales);
      RefreshPriceList;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actticketsTicketZoneExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewTicketZone(dmMainGlobal.cdsStoredProcTicketZones);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.acttikcetsFarePriceReductionRideXRefExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionRideXRef;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTRPSolobusExecute(Sender: TObject);
begin   // programowanie bileterek
//  if LastView <> (Sender as TAction) then
//  begin
//    PrepareInterface;
//    try
//      LastView := (Sender as TAction);
//      BeforeFuncView((Sender As TAction).Caption);
//      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
//
//      // if Sender = actTRPSolobus then
//      // TframeDeviceManager(frameDeviceManager).ViewFileXSolobus(dmMainGlobal.cdsFileXTicketRegister, [  ] )
//      // else
//      if Sender = actTRPEmar105 then
//        TframeDeviceManager(frameDeviceManager).ViewFileXEmar105(dmMainGlobal.cdsFileXTicketRegisterCard, [])
//      else if Sender = actTRPEmar205 then
//        TframeDeviceManager(frameDeviceManager).ViewFileXEmar205(dmMainGlobal.cdsFileXTicketRegisterCard, []) finally UnPrepareInterface;
//    end;
//  end;
end;

procedure TfrmMainTurdus.actVatRateExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeTicket(frameTariffAndTicket).ViewVatRate(dmMainGlobal.cdsStoredProcVatRates);
    finally
      UnPrepareInterface;
    end;
  end;
end;
{$ENDREGION}
{$REGION 'BeforeViews & Prepare/Unprepare Intercface'}

procedure TfrmMainTurdus.BeforeView(AProcName, AMsg: String);
begin
  if AMsg = '' then
    Log(AProcName, _LOG_VIEW_RUN)
  else
    Log(AProcName, AMsg);
  dmMainGlobal.CloseDatasets;
end;

procedure TfrmMainTurdus.cbIdleClick(Sender: TObject);
begin
  tmrIdle.Enabled := cbIdle.Checked;
  if not cbIdle.Checked then
    cbIdle.Caption := 'Bez automatycznego roz³¹czania';
end;

procedure TfrmMainTurdus.BeforeDictView(AProcName: String);
begin
  BeforeView(AProcName, _LOG_DICT_RUN);
end;

procedure TfrmMainTurdus.BeforeFuncView(AProcName: String);
begin
  BeforeView(AProcName, _LOG_PROC_RUN);
end;

procedure TfrmMainTurdus.PrepareInterface;
begin
  if Assigned(frameDeviceManager) then
    TframeDeviceManager(frameDeviceManager).StopTimer;
  Screen.Cursor := crHourGlass;
  // frmMainTurdus.Enabled := false;
  // SetMessage(_PREPARE_INTERFACE);
  Application.ProcessMessages;
  // LockWindowUpdate(Self.Handle);
  frmMainTurdus.Enabled := false;
  SetMessage(_PREPARE_INTERFACE);
  inherited;
  LockWindowUpdate(Self.Handle);
end;

procedure TfrmMainTurdus.UnPrepareInterface;

begin
  // HelpContext := GetHelpContextForFrame(FLastView);
  Screen.Cursor := crDefault;
  // frmMainTurdus.Enabled := True;
  // SetMessage('');
  // LockWindowUpdate(0);
  Application.ProcessMessages;
  frmMainTurdus.Enabled := True;
  SetMessage('');
  inherited;
  LockWindowUpdate(0);
end;

procedure TfrmMainTurdus.actrouteCollisionsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframeRoute(frameRoute).ViewCollisions;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteLineExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);

      TframeRoute(frameRoute).ViewLine(dmMainGlobal.cdsLinePagination);
    ///
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteOtherTablesExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);

      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcTimeTableResult, '1');
      //TframeRoute(frameRoute).viewPrintRJATable(dmMainGlobal.cdsStoredProcTimeTableResult);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actroutePrintRJATableExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);

      TframeRoute(frameRoute).viewPrintRJATable(dmMainGlobal.cdsStoredProcTimeTableResult);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actroutePrintTimeTablesManageExecute(Sender: TObject);
begin
  PrepareInterface;
  try
    LastView := (Sender as TAction);
    BeforeFuncView((Sender As TAction).Caption);
    dmMainGlobal.DataSetOpen(dmMainGlobal.cdsTT_TimeTableGetAll);
    frameInformation.viewPrintTimeTable(dmMainGlobal.cdsTT_TimeTableGetAll);
  finally
    UnPrepareInterface;
  end;
end;

procedure TfrmMainTurdus.actrouteRideBusTableConfPrefSetExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideBusTableConfPrefSet);
      TframeRoute(frameRoute).ViewRideBusTableConfPrefSet(dmMainGlobal.cdsRideBusTableConfPrefSet);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.RefreshPriceList(CompanyID: Integer);
var
  fCompanyId: Integer;
begin
  if CompanyID > 0 then
    fCompanyId := CompanyID
  else
    fCompanyId := GPriceListCompanyId;

  TframeTicket(frameTariffAndTicket).SetPriceList(dmMainGlobal.cdsStoredProcPriceLists);
  TframeTicket(frameTariffAndTicket).PriceFrame.AddActivePriceList(fCompanyId);
end;
{$REGION 'actions for Settings frame '}

procedure TfrmMainTurdus.actPlanBusExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('%d', [Integer(VehicleType_Bus)]);

      Log((Sender as TAction).Caption, _LOG_VIEW_RUN);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBuses, Params);
      TframePlan(framePlan).ViewBus(dmMainGlobal.cdsStoredProcBuses, [ { StrParamChoicePanelType(cptCompany) } ]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanBusGroupExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender as TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusGroups);
      TframePlan(framePlan).ViewBusGroup(dmMainGlobal.cdsStoredProcBusGroups, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanRideGroupExecute(Sender: TObject);
begin
  inherited;
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframePlan(framePlan).ViewRideGroup(dmMainGlobal.cdsStoredProcRideGroup);
    finally
      UnPrepareInterface;
    end;
  end;
end;


procedure TfrmMainTurdus.actPlanCombustionStandardsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender as TAction).Caption);
      TframePlan(framePlan).ViewCombustionStandard(dmMainGlobal.cdsCombustionStandards, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanContractRideExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      TframePlan(framePlan).ViewContractRide(dmMainGlobal.cdsStoredProcContractRide
      , [cpDoNotSelect, cpDoNotClear]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanDriverExecute(Sender: TObject);
//var
//  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
//      Params := Format('DriverType_ID=%d'#13'Company_ID=%d'#13'rowfrom=%d'#13'rowto=%d'#13'Filter=(Deleted=0)', [Integer(ptDriver), GetChoicePanelDatabaseItemID,0,20]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      dmMainGlobal.TCPIPServerMethods.PrepareDrivers;
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDrivers, Params);
      TframePlan(framePlan).ViewDriver(dmMainGlobal.cdsStoredProcDrivers, [
  {$IFDEF FORIS} StrParamChoicePanelType(cptCompany), {$ENDIF}
        cpDoNotSelect, cpDoNotClear]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanDriverGroupExecute(Sender: TObject);
var
  Params: string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      Params := Format('@Mode=%d', [3]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);

      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDriverGroups, Params);
      TframePlan(framePlan).ViewDriverGroups(dmMainGlobal.cdsStoredProcDriverGroups, []);
    finally
      UnPrepareInterface
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanDriverSelParamsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcDriverTicketRegPrefSet);
      TframePlan(framePlan).ViewDriverTicketRegPrefSet(dmMainGlobal.cdsStoredProcDriverTicketRegPrefSet, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanGroupTaskExecute(Sender: TObject);
begin
  inherited;
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender as TAction).Caption);
      TframePlan(framePlan).ViewTaskGroup(dmMainGlobal.cdsStoredProcTaskGroup);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanTaskExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender as TAction).Caption);
      TframePlan(framePlan).ViewTask(dmMainGlobal.cdsStoredProcTask);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPlanTechnicalRideExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender as TAction).Caption);
      TframePlan(framePlan).ViewTechnicalRide(dmMainGlobal.cdsStoredProcTechnicalRide
        , [cpDoNotSelect, cpDoNotClear]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actPriceListExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcPriceLists);
      TframeTicket(frameTariffAndTicket).ViewPriceList(dmMainGlobal.cdsStoredProcPriceLists);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideCommunicationNetworkExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin

    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideCommunicationNetwork);
      TframeRoute(frameRoute).ViewRideCommunicationNetwork(dmMainGlobal.cdsRideCommunicationNetwork);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);

      TframeRoute(frameRoute).ViewRide(dmMainGlobal.cdsRidePagination);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideExpPrefSetsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideExpPrefSets);
      TframeRoute(frameRoute).ViewRideExpPrefSets(dmMainGlobal.cdsRideExpPrefSets);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideSalePrefSetsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideSalePrefSets);
      TframeRoute(frameRoute).ViewRideSalePrefSets(dmMainGlobal.cdsRideSalePrefSets);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideServiceDesignationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcRideDesignation, '1');
      TframeRoute(frameRoute).ViewRideDesignation(dmMainGlobal.cdsStoredProcRideDesignation);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideServiceTypeExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideServiceType);
      TframeRoute(frameRoute).ViewRideServiceType(dmMainGlobal.cdsRideServiceType);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteRideTypeCommunicationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsRideTypeCommunication);
      TframeRoute(frameRoute).ViewRideTypeCommuniaction(dmMainGlobal.cdsRideTypeCommunication);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteTableDefinitionExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeDictView((Sender As TAction).Caption);

      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcBusStopTablePattern, 'Type_ID=1');
      TframeRoute(frameRoute).viewTableDefinition(dmMainGlobal.cdsStoredProcBusStopTablePattern);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actrouteTimeTablesManageExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsTT_TimeTableGetAll);
      TframeRoute(frameRoute).ViewTimeTable(dmMainGlobal.cdsTT_TimeTableGetAll);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewStartExecute(Sender: TObject);
begin
  if Application.Terminated or AppTerminated or AppIsClosed then
    Exit;
  LastView := (Sender as TAction);
  BeforeView((Sender As TAction).Caption, '');
  TframeStartChromium(frameStartChromium).tbtnHome.Click;  //Chromium
  pctrlMain.ActivePage := tsheetStart;
end;

procedure TfrmMainTurdus.actViewTicketsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetTickets;
      ExecuteFirstAction(actmgrTariffAndTicket);

      TframeTicket(frameTariffAndTicket).catbtnTicket.SelectedItem := TframeTicket(frameTariffAndTicket).catbtnTicket.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewDictionaryExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetDict;
      ExecuteFirstAction(actmgrDictionary);

      TFrameDictionary(frameDictionary).catbtnDictionary.SelectedItem := TFrameDictionary(frameDictionary).catbtnDictionary.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewInformationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetInformation;
      ExecuteFirstAction(actmgrInformation);
      TframeCoordination(frameInformation).catbtnCoordination.SelectedItem :=
      TframeCoordination(frameInformation).catbtnCoordination.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewTicketControlerExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetTicketControler;

      // tu odpaliæ widok
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewInspectionExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetInspection;
      ExecuteFirstAction(actmgrInspection);

      TframeInspection(frameInspection).catbtnInspection.SelectedItem := TframeInspection(frameInspection).catbtnInspection.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewPlanningExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetPlan;
      ExecuteFirstAction(actmgrPlanning);
      TframePlan(framePlan).catbtnPlan.SelectedItem := TframePlan(framePlan).catbtnPlan.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewAnalysisExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetAnalysis;
      ExecuteFirstAction(actmgrAnalysis);

      TframeAnalysis(frameAnalysis).catButtons.SelectedItem := TframeAnalysis(frameAnalysis).catButtons.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewBusStopsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      ClearChoicePanel;
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ExecuteFrame(TAction(Sender), TframeBusStops(FrameBusStops), pctrlMain);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewDeviceManagerExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetDeviceManager;
      ExecuteFirstAction(actmgrDeviceManager);
      TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.SelectedItem := TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewRouteExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetRoute;
      ExecuteFirstAction(actmgrRoute);
      TframeRoute(frameRoute).catbtnRoute.SelectedItem := TframeRoute(frameRoute).catbtnRoute.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewAccountsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetAccounts;
      ExecuteFirstAction(actmgrAccounts);

      TframeAccounts(frameAccounts).catButtons.SelectedItem := TframeAccounts(frameAccounts).catButtons.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewSettingsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeView((Sender As TAction).Caption, '');
      pctrlMain.ActivePage := tsheetSettings;
      ExecuteFirstAction(actmgrSettings);

      TframeSettings(frameSettings).catButtons.SelectedItem := TframeSettings(frameSettings).catButtons.Categories[0].Items[0];
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actviewShowToolBarExecute(Sender: TObject);
begin
  inherited;
  toolbarMain.Visible:=not toolbarMain.Visible;
  actviewShowToolBar.Checked:=toolbarMain.Visible;
end;

procedure TfrmMainTurdus.AssignActions;

  procedure ActionsAssign(act: TActionManager; btns: TButtonCategories; cat: string; acolor: TColor);
  var
    b: Boolean;
    i: Integer;
  begin
    b := false;
    for i := 0 to act.ActionCount - 1 do
      if (AnsiLowerCase(TAction(act.Actions[i]).Category) = AnsiLowerCase(cat)) and TAction(act.Actions[i]).Enabled then
      begin
        b := True;
        break;
      end;
    if b then
      with btns.Add do
      begin
        Caption := cat;
        Color := acolor;
        for i := 0 to act.ActionCount - 1 do
          if (AnsiLowerCase(TAction(act.Actions[i]).Category) = AnsiLowerCase(cat)) and TAction(act.Actions[i]).Enabled then
          begin
            with Items.Add do
              Action := TAction(act.Actions[i]);
          end;
      end;
  end;

begin
  TframeSettings(frameSettings).catButtons.Categories.Clear;
  ActionsAssign(actmgrSettings, TframeSettings(frameSettings).catButtons.Categories, _CAPT_SETTINGS_BASIC, RGB(255, 213, 170));
  ActionsAssign(actmgrSettings, TframeSettings(frameSettings).catButtons.Categories, _CAPT_SETTINGS_Import, RGB(255, 213, 170));

  //S³owniki - podzia³ terytorialny
  TFrameDictionary(frameDictionary).catbtnDictionary.Categories.Clear;
  ActionsAssign(actmgrDictionary, TFrameDictionary(frameDictionary).catbtnDictionary.Categories, _CAPT_TERRITORIAL, clSkyBlue);
  ActionsAssign(actmgrDictionary, TFrameDictionary(frameDictionary).catbtnDictionary.Categories, _CAPT_ORG_DEV, RGB(220, 185, 255));
  ActionsAssign(actmgrDictionary, TFrameDictionary(frameDictionary).catbtnDictionary.Categories, _CAPT_CAL_DEV, RGB(255, 213, 170));



  TframeRoute(frameRoute).catbtnRoute.Categories.Clear;
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_ROAD_DEV, clMoneyGreen);
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_ROUTE_PARAMS, clSkyBlue);
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_ROUTE_TIMETABLE, RGB(255, 213, 213));
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_ROUTE_TARIF, clMoneyGreen);
  //zarz¹dzanie przystankami
  {$IFNDEF TURDUS_AP}
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_BusStopManager_DEV, RGB(220, 185, 255));
  ActionsAssign(actmgrRoute, TframeRoute(frameRoute).catbtnRoute.Categories, _CAPT_ROUTE_PRINT_TIMETABLE, RGB(255, 213, 170));
  {$ENDIF}

  //Cenniki
  TframeTicket(frameTariffAndTicket).catbtnTicket.Categories.Clear;
  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_PRICESCALE_DEV, RGB(255, 213, 170));
  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_TICKETZONE_DEV, clMoneyGreen);

  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_TARIF_DEV, RGB(255, 255, 200));

  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_REDUCTION_PRICE_DEV, RGB(220, 185, 255));
  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_REDUCTIONS_DEV, clMoneyGreen);
  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_CAL_DEV, clSkyBlue);

  ActionsAssign(actmgrTariffAndTicket, TframeTicket(frameTariffAndTicket).catbtnTicket.Categories, _CAPT_REDUCTION_NUMBERING_DEV, clSkyBlue);

  //zarz¹dzanie
  TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories.Clear;
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_Drivers_DEV, clAqua);
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_Cashiers_DEV, RGB(155, 213, 255));
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_BUSSES_DEV, RGB(255, 213, 170));
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_SALEDEVICES_DEV, RGB(255, 255, 200));
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_ZbioryDanych_DEV, $00EAEBFF);
//  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_TRP_DEV, clAqua);
  ActionsAssign(actmgrDeviceManager, TframeDeviceManager(frameDeviceManager).catbtnDeviceManager.Categories, _CAPT_REPORTS_DEV, clMoneyGreen);

  TframeAccounts(frameAccounts).catButtons.Categories.Clear;
  ActionsAssign(actmgrAccounts, TframeAccounts(frameAccounts).catButtons.Categories, _CAPT_SaleRegister_DEV, clMoneyGreen);
  ActionsAssign(actmgrAccounts, TframeAccounts(frameAccounts).catButtons.Categories, _CAPT_Passengers_DEV, RGB(255, 213, 170));
  ActionsAssign(actmgrAccounts, TframeAccounts(frameAccounts).catButtons.Categories, _CAPT_SaleReports_DEV, clSkyBlue);

  TframeInspection(frameInspection).catbtnInspection.Categories.Clear;
  ActionsAssign(actmgrInspection, TframeInspection(frameInspection).catbtnInspection.Categories, _CAPT_IncInspection_DEV, clMoneyGreen);
  // ActionsAssign(actmgrInspection, TframeInspection(frameInspection).catbtnInspection.Categories, _CAPT_RoudInspection_DEV, clSkyBlue);

  TframeAnalysis(frameAnalysis).catButtons.Categories.Clear;
  ActionsAssign(actmgrAnalysis, TframeAnalysis(frameAnalysis).catButtons.Categories, _CAPT_SaleAnalysis_DEV, clAqua);
  ActionsAssign(actmgrAnalysis, TframeAnalysis(frameAnalysis).catButtons.Categories, _CAPT_TransportAnalysis_DEV, clSkyBlue);
  ActionsAssign(actmgrAnalysis, TframeAnalysis(frameAnalysis).catButtons.Categories, _CAPT_TimelinessAnalysis_DEV, clMoneyGreen);

  frameInformation.catbtnCoordination.Categories.Clear;
  ActionsAssign(actmgrInformation, frameInformation.catbtnCoordination.Categories, _CAPT_COORDINATION_TIME_TABLE, RGB(255, 213, 170));
  ActionsAssign(actmgrInformation, frameInformation.catbtnCoordination.Categories, _CAPT_COORDINATION_BUSSTOP_PLATES, clMoneyGreen);
  ActionsAssign(actmgrInformation, frameInformation.catbtnCoordination.Categories, _CAPT_COORDINATION_RJA_TABLE, clSkyBlue);
  ActionsAssign(actmgrInformation, frameInformation.catbtnCoordination.Categories, _CAPT_COORDINATION_INFO_DATA, $00EAEBFF);
  ActionsAssign(actmgrInformation, frameInformation.catbtnCoordination.Categories, _CAPT_COORDINATION_EPodroznik, clAqua);

  // akcje planowania dopisaæ do interfejsu
  TframePlan(framePlan).catbtnPlan.Categories.Clear;
  ActionsAssign(actmgrPlanning, TframePlan(framePlan).catbtnPlan.Categories, _CAPT_TASK, clMoneyGreen);
  ActionsAssign(actmgrPlanning, TframePlan(framePlan).catbtnPlan.Categories, _CAPT_Drivers_DEV, clAqua);
  ActionsAssign(actmgrPlanning, TframePlan(framePlan).catbtnPlan.Categories, _CAPT_BUSSES_DEV, clSkyBlue);

  TframeBusStops(FrameBusStops).CategoryButtons.Categories.Clear;
  AddButtonGroup(actmgrBusStops, TframeBusStops(FrameBusStops), _CAPT_REGISTERS, C_TXT_REGISTERS);
  AddButtonGroup(actmgrBusStops, TframeBusStops(FrameBusStops), _CAPT_BusStopManager_DEV, CAPT_BusStopManager_DEV);
  AddButtonGroup(actmgrBusStops, TframeBusStops(FrameBusStops), _CAPT_REPORTS, _REPORTS);
end;

{ -----------------------------------------------------------------------------
  Procedure: AssignTagsToActions
  Author:    maciej.jablonski
  Date:      05-sie-2014
  Arguments: None
  Result:    None
  Wywolywana na starcie z FormCreate. Przydziela tagi do akcji w menu glownym.
  Mozna dzieki temu odroznic ostatnio wywolywane akcje.
  Tagi sa zdefiniowane w Globals.pas
  ----------------------------------------------------------------------------- }

procedure TfrmMainTurdus.AssignTagsToActions;
begin
  actInspection.tag := AC_TAG_INSPECTION;
  actInspectionBusRuns.tag := AC_TAG_INSPECTION_BUS_RUNS;
end;

procedure TfrmMainTurdus.actdictFarePriceReductionDesignationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
//      dmMainGlobal.RideDesignationOpen('3');
      TframeTicket(frameTariffAndTicket).ViewFarePriceReductionDesignation(dmMainGlobal.cdsStoredProcRideDesignation);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actdictFarePriceScaleDesignationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
//      dmMainGlobal.RideDesignationOpen('2');
      TframeTicket(frameTariffAndTicket).ViewFarePriceScaleDesignation(dmMainGlobal.cdsStoredProcRideDesignation);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actSalesReportExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actRatesForWagonkilometerExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcLineFeeDefinition);
      TframeRoute(frameRoute).ViewLineFeeDefinition(dmMainGlobal.cdsStoredProcLineFeeDefinition);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actRegistrationParamsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      TframeAccounts(frameAccounts).ViewRegistrationParams;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actRegistrationSettlementsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      TframeAccounts(frameAccounts).ViewSalesReports(dmMainGlobal.cdsSalesReportPagination, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actReportsTransportExecute(Sender: TObject);
begin
  inherited;
//

end;

procedure TfrmMainTurdus.actRJAInformationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      frameInformation.ViewDISPFileRJAList(dmMainGlobal.cdsDISPFile,0, []);
      //TframeDeviceManager(frameDeviceManager).ViewDISPFileINFList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actRoadsExecute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);

      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(FrameBusStops, dmMainGlobal.cdsStoredProcRoadsPagination, TframeBusStops(FrameBusStops).ViewRoad, Params, False)
    finally
      UnPrepareInterface;
      TframeBusStops(FrameBusStops).FrameBaseGlossary.GridWithSearch.AutosizeGridColumns;
    end;
  end;
end;

procedure TfrmMainTurdus.actImportSettlementsExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      TframeAccounts(frameAccounts).ViewImportSettlements();
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDISPFileListExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      TframeDeviceManager(frameDeviceManager).ViewDISPFileList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDISPFileListINFExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      TframeDeviceManager(frameDeviceManager).ViewDISPFileINFList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDISPFileListRJAExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      TframeDeviceManager(frameDeviceManager).ViewDISPFileRJAList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDISPFileListEPExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      TframeDeviceManager(frameDeviceManager).ViewDISPFileEPList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.ctDISPFileListEP_InformationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      frameInformation.ViewDISPFileEPList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;


procedure TfrmMainTurdus.actDataInformationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareFileXTicketRegister;
      frameInformation.ViewDISPFileINFList(dmMainGlobal.cdsDISPFile,0, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;



procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_TICKETS_ADDSExecute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_RELIEFTICKETS]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAnalysis,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_TRANSPORTExecute(
  Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_TRANSPORT]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAnalysis,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAnalysesRJAExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      //dmMainGlobal.DataSetOpen(dmMainGlobal.cdsDISP_BusRun_GetAll, IntToStr(GetLicencesCompanyID));
      TframeAnalysis(frameAnalysis).ViewAnalysisRJA([]);
      TframeInspection(frameInspection).ViewAnalysisRJA([]);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actAnalysesREPORT_TYPE_ACCOUNTSExecute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_ACCOUNTS]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAnalysis,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAnalysis(frameAnalysis).ViewAccountsReport, Params);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actFileHistoryExecute(Sender: TObject);
var
  frm: TfrmHistory;
begin
  Screen.Cursor := crHourGlass;
  frm := TfrmHistory.Create(Self);
  try
//    HideChoicePanel;
    Log((Sender As TAction).Caption, _LOG_PROC_RUN);
    StopBusTraceTimer;
    frm.Initialize(dmMainGlobal.cdsStoredProcHist, CurrentUser);
    Screen.Cursor := crDefault;
    frm.ShowModal;
    Screen.Cursor := crHourGlass;
  finally
    frm.Free;
    Screen.Cursor := crDefault;
    Application.ProcessMessages;
  end;
end;

procedure TfrmMainTurdus.Action33Execute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_ACCOUNTS]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAccounts,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAccounts(frameAccounts).ViewAccountsReport, Params);
    finally
      UnPrepareInterface;
    end;
  end;

end;

procedure TfrmMainTurdus.ActionEnabled;

  procedure ActionEnabled(actmgr: TActionManager);
  var
    i: Integer;
  begin
    for i := 0 to actmgr.ActionCount - 1 do
      if actmgr.Actions[i].tag > 0 then
        TAction(actmgr.Actions[i]).Enabled := Assigned(CurrentUser)
{$IFNDEF DEBUG}
        and CurrentUser.ActionEnabled(actmgr.Actions[i].tag)
{$ENDIF}
        ;
  end;

  procedure ParentActionEnabled(Action: TAction; actmgr: TActionManager);
  var
    b: Boolean;
    i: Integer;
  begin
    b := false;
    for i := 0 to actmgr.ActionCount - 1 do
      if TAction(actmgr.Actions[i]).Enabled then
      begin
        b := True;
        break;
      end;
    Action.Enabled := Action.Enabled and b;
  end;

begin
  ActionEnabled(actmgrMain);
  ActionEnabled(actmgrSettings);
  ActionEnabled(actmgrDictionary);
  ActionEnabled(actmgrTariffAndTicket);
  ActionEnabled(actmgrRoute);
//  ActionEnabled(actmgrSale);
  ActionEnabled(actmgrDeviceManager);
  ActionEnabled(actmgrAccounts);
  ActionEnabled(actmgrAnalysis);
  ActionEnabled(actmgrInspection);
  ActionEnabled(actmgrPlanning);
  ActionEnabled(actmgrInformation);
  ActionEnabled(actmgrBusStops);
{$IFNDEF DEBUG}

  actdictCashDepositMachineGLOBE.Enabled := actdictCashDepositMachineGLOBE.Enabled and XMLLicence_Avaible('AUTOCASHIERGLOBE');
  actdictDeviceOfAccounting.Enabled := actdictDeviceOfAccounting.Enabled and XMLLicence_Avaible('AUTOCASHIER');
  actdictEmCardLoader_SR.Enabled := actdictEmCardLoader_SR.Enabled and XMLLicence_Avaible('EMCARDLOADER_SR');
  actdictEmCardLoader_CT.Enabled := actdictEmCardLoader_CT.Enabled and XMLLicence_Avaible('EMCARDLOADER_CT');
  actdictTicketControlDev.Enabled := actdictTicketControlDev.Enabled and XMLLicence_Avaible('TICKETCONTROLDEV');

  ParentActionEnabled(actviewSettings, actmgrSettings);
  ParentActionEnabled(actviewDictionary, actmgrDictionary);
  ParentActionEnabled(actViewTickets, actmgrTariffAndTicket);
  ParentActionEnabled(actviewRoute, actmgrRoute);
//  ParentActionEnabled(actviewSale, actmgrSale);
  ParentActionEnabled(actviewDeviceManager, actmgrDeviceManager);
  ParentActionEnabled(actviewAccounts, actmgrAccounts);
  ParentActionEnabled(actviewAnalysis, actmgrAnalysis);
  ParentActionEnabled(actviewInspection, actmgrInspection);
  ParentActionEnabled(actviewPlanning, actmgrPlanning);
  ParentActionEnabled(actviewInformation, actmgrInformation);
  ParentActionEnabled(actviewBusStops, actmgrBusStops);
{$ENDIF}
  actFileLogOut.Enabled := ClientAuthentication = 0;
  actFilePassword.Enabled := ClientAuthentication = 0;

  AssignActions;
{$IFNDEF DEBUG}
  ModuleAvaibility.SetModuleAvaibility(actmgrMain, toolbarMain);
{$ENDIF}
end;


(*procedure TfrmMainTurdus.ActionEnabled;
  //{$IFNDEF DEBUG}
var
  I: Integer;
  z: Integer;
  k: Integer;
  actman: TActionManager;
  //{$ENDIF}
begin
  //{$IFNDEF DEBUG}
  for k := 0 to ComponentCount - 1 do
    if Components[k] is TActionManager then begin
      actman := TActionManager(Components[k]);
      for I := 0 to actman.ActionCount - 1 do
        if actman.Actions[i].Tag > 0 then begin
          TAction(actman.Actions[i]).Enabled :=
            Assigned(CurrentUser) and
            CurrentUser.ActionEnabled(actman.Actions[i].Tag);
          //TAction(actman.Actions[i]).Visible := TAction(actman.Actions[i]).Enabled;
        end;
    end;
  //{$ENDIF}
  AssignActions;
  //{$IFNDEF DEBUG}
  for I := 0 to actmgrMain.ActionCount - 1 do
     with
       actmgrMain.Actions[i] do
       Begin
          if  (Category = 'Widoki') and (actmgrMain.Actions[i].Tag > 0) then // (actmgrMain.Actions[i].Tag mod 1000) = 0 then
             Begin
                z := XMLLicence_ModuleVisibility(AppParams.ID,  actmgrMain.Actions[i].Tag);
                if z = 1 then TAction(actmgrMain.Actions[i]).Visible := False
                Else if z = 2 then TAction(actmgrMain.Actions[i]).Visible := False;
             End;

       End;
  //{$ENDIF}
  actFileLogOut.Enabled := ClientAuthentication = 0;
end;      *)

procedure TfrmMainTurdus.AfterLoadLicence(Sender: TObject);
begin
  if not Assigned(dmMainGlobal.Privileges) then
    dmMainGlobal.Privileges := TObjectList<TObject>.Create;
  UserGroupBasePriv(dmMainGlobal.Privileges);
end;

{$IFNDEF  EUREKALOG}
procedure TfrmMainTurdus.AppException(Sender: TObject; E: Exception);
begin
  if not(Sender is TMaskEdit) then
    MainFormUtil.AppException(E);
end;
{$ENDIF}

constructor TfrmMainTurdus.Create(AOwner: TComponent);
begin
  {$IFDEF TURDUS_AP}
  Application.Title := 'FORIS - Analiza Przewozów';
  Application.HelpFile := 'help\ForisAP.chm';
  {$ELSE}
  Application.Title := 'Informica';
  Application.HelpFile := 'help\Informica.chm';
  {$ENDIF}
  inherited Create(AOwner);
end;

procedure TfrmMainTurdus.CreateFrames;
begin
  frameStartChromium := TframeStartChromium.Create(nil);
  frameStartChromium.Parent := tsheetStart;
  frameStartChromium.Align := alClient;
  TframeStartChromium(frameStartChromium).URL := AppParams.HomePageURL;  //Chromium

  frameSettings := TframeSettings.Create(nil);
  frameSettings.Parent := tsheetSettings;
  frameSettings.Align := alClient;

  frameDictionary := TFrameDictionary.Create(nil);
  frameDictionary.Parent := tsheetDict;
  frameDictionary.Align := alClient;

  frameRoute := TframeRoute.Create(nil);
  frameRoute.Parent := tsheetRoute;
  frameRoute.Align := alClient;

  frameTariffAndTicket := TframeTicket.Create(nil);
  TframeTicket(frameTariffAndTicket).Parent := tsheetTickets;
  TframeTicket(frameTariffAndTicket).Align := alClient;

  frameDeviceManager := CreateFrameInTabSheet(TframeDeviceManager, tsheetDeviceManager);
  frameAccounts := CreateFrameInTabSheet(TframeAccounts, tsheetAccounts);
  frameAnalysis := CreateFrameInTabSheet(TframeAnalysis, tsheetAnalysis);
  frameInspection := CreateFrameInTabSheet(TframeInspection, tsheetInspection);
  framePlan := CreateFrameInTabSheet(TframePlan, tsheetPlan);

  frameInformation := TframeCoordination.Create(nil);
  TframeCoordination(frameInformation).Parent := tsheetInformation;
  TframeCoordination(frameInformation).Align := alClient;

  //TframeCoordination(frameInformation).BaseForm:=frmMainTurdus;     //Chromium
  CEFWindowParentMain2:=TframeCoordination(frameInformation).CEFWindowInformationFrame; //CHROMIUM

  frameBusStops := TframeBusStops.Create(nil);
  frameBusStops.Parent := tsheetBusStops;
  frameBusStops.Align := alClient;
end;

procedure TfrmMainTurdus.DestroyFrames;
begin
  if Assigned(frameStartChromium) then
    FreeAndNil(frameStartChromium);   //chromium
  if Assigned(frameSettings) then
    FreeAndNil(frameSettings);
  if Assigned(frameDictionary) then
    FreeAndNil(frameDictionary);
  if Assigned(frameRoute) then
    FreeAndNil(frameRoute);
  if Assigned(frameDeviceManager) then
    FreeAndNil(frameDeviceManager);
  if Assigned(frameAccounts) then
    FreeAndNil(frameAccounts);
  if Assigned(frameAnalysis) then
    FreeAndNil(frameAnalysis);
  if Assigned(frameInspection) then
    FreeAndNil(frameInspection);
  if Assigned(framePlan) then
    FreeAndNil(framePlan);
  if Assigned(frameTariffAndTicket) then
    FreeAndNil(frameTariffAndTicket);
  if Assigned(frameInformation) then
    FreeAndNil(frameInformation);
end;

function TfrmMainTurdus.DoChoicePanelButtonChoiceClick(var AID: Integer; var AName: String): Boolean;
begin
  result := MainFormUtil.DoChoicePanelButtonChoiceClick(Self, AID, AName);
end;

procedure TfrmMainTurdus.DoShowChoicePanelOwnerSettings(AParams: array of Variant; var BDoNotClearChoicePanel: Boolean);
begin
  MainFormUtil.DoShowChoicePanelOwnerSettings(Self, AParams, BDoNotClearChoicePanel);
end;

{$IFNDEF TURDUS_AP}
procedure TfrmMainTurdus.Download(ASender: TObject; AWorkMode: TWorkMode;
  AWorkCount: Int64);
begin
  if Assigned(frmSplash) then begin
    if (Length(frmSplash.InfoText) > 50) or (Pos('Nowa wersja', frmSplash.InfoText) > 0) then
      frmSplash.InfoText := 'Pobieram aktualizacjê...'
    else
      frmSplash.InfoText := frmSplash.InfoText + '.';
  end;
end;
{$ENDIF}

procedure TfrmMainTurdus.ExecuteFirstAction(actmgr: TActionManager);
var
  i: Integer;
begin
  for i := 0 to actmgr.ActionCount - 1 do
    if TAction(actmgr.Actions[i]).Enabled then
    begin
      TAction(actmgr.Actions[i]).Execute;
      break;
    end;
end;

procedure TfrmMainTurdus.FormActivate(Sender: TObject);
var
  f: TIniFile;
begin
  inherited;
  if fFirstActive then begin
    if WindowState <> wsMaximized then begin
      with Screen.WorkAreaRect do
        SetBounds(Left, Top, Right - Left, Bottom - Top);
      Application.ProcessMessages;
      WindowState := wsMaximized;
    end;
    CheckComponentsVersion;
    CheckApplicationVersion;
    fFirstActive := false;


    toolbtnSettings_Separator.Visible:=toolbtnSettings.Visible;
    toolbtnDictionary_Separator.Visible:=false;
    toolbtnRoute_Separator.Visible:=toolbtnRoute.Visible;
    //toolbtnTicket_Separator.Visible:=false;
    toolbtnDeviceManager_Separator.Visible:=false;

    //toolbtnInformation_Separator.Visible:=toolbtnInformation.Visible;
    toolbtnAnalysis_Separator.Visible:=toolbtnAnalysis.Visible;
    toolbtnPlanning_Separator.Visible:=toolbtnPlanning.Visible;
    toolbtnInspection_Separator.Visible:=toolbtnInspection.Visible;
    toolbtnTicketControler_Separator.Visible:=toolbtnTicketControler.Visible;
//    toolbtnSale_Separator.Visible:=toolbtnSale.Visible;
    toolbtnBusStops_Separator.Visible:=toolbtnBusStops.Visible;

   ToolButtonSepaM.Visible := False;
  {$IF (DEFINED(TURDUS_AP))}
    ToolButtonSepaM.Visible := True;
    toolbtnDeviceManager_Separator.Visible := false;
    toolbtnStart_Separator.visible := false;
  {$IFEND}

    f := IniFile;
    try
      if Assigned(f) then begin
        actviewShowToolBar.Checked := f.ReadBool('TfrmMainTurdus', 'actviewShowToolBar',true);
        cbIdle.Checked := f.ReadBool('TfrmMainTurdus', 'AutoLogout', true);
        cbIdleClick(nil);
      end;
      toolbarMain.Visible:=actviewShowToolBar.Checked;
    finally
      f.Free;
    end;
  end;
end;

procedure TfrmMainTurdus.FormClose(Sender: TObject; var Action: TCloseAction);
var
  f: TIniFile;
begin
{$IFDEF RELEASE}
  if AppTerminated or FFirstClosingAsk then
  begin
{$ENDIF}
    f := IniFile;
    try
      if Assigned(f)then begin
        f.WriteBool('TfrmMainTurdus', 'actviewShowToolBar', actviewShowToolBar.Checked);
        f.WriteBool('TfrmMainTurdus', 'AutoLogout', cbIdle.Checked);
      end;
    finally
      f.Free;
    end;
    AppIsClosed := True;
    try
      if Assigned(dmMainGlobal) and Assigned(dmMainGlobal.SQLConnection) then
        dmMainGlobal.SQLConnection.AfterDisconnect := nil;
      tmrLogout.Enabled := false;
      tmrLive.Enabled := false;
      tmrIdle.Enabled := false;

      // if Assigned(frameInspection) and Assigned() then
      // TframeInspection(frameInspection).DisableTimers;

      DestroyFrames;

      if Assigned(dmMainGlobal) then
      begin
        StopBusTraceTimer;
        dmMainGlobal.CloseDatasets;
        FreeAndNil(dmMainGlobal);
      end;
      if Assigned(dmCommon) then
        FreeAndNil(dmCommon);

      if Assigned(CurrentUser) then
        FreeAndNil(CurrentUser);

      if Assigned(Licences) then
        FreeAndNil(Licences);

      // if Assigned(dmMainGlobal) then
      // FreeAndNil(dmMainGlobal);
    except
    end;
{$IFDEF RELEASE}
  end
  else begin
    Action := caNone;
    Exit;
  end;
{$ENDIF}
end;

procedure TfrmMainTurdus.FormCreate(Sender: TObject);
{$IFNDEF TURDUS_AP}
var
  s: string;
  updater: TdmUpdater;
{$ENDIF}
begin
  FClosing  := False; //Chromium
  FCanClose := False;
  FCanClose2:= False;
  FFirstClosingAsk := False;
  {$IFNDEF TURDUS_AP}
  frmSplash := TfrmSplash.Create(Self);
  SplashFrm := frmSplash;
  frmSplash.Show;

  Application.ProcessMessages;
  s := ExtractFilePath(ParamStr(0));
  if FileExists(s + 'online.dat') then begin
    //automatyczna aktualizacja
    frmSplash.InfoText := 'Sprawdzanie aktualizacji...';
    updater := TdmUpdater.Create(Self);
    try
      if updater.IsUpdateAvailable then begin
        s := updater.NewProductVersion;
        frmSplash.InfoText := 'Nowa wersja: ' + s;
        updater.OnBeginUpdateDownload := StartDownload;
        updater.OnUpdateDownload := Download;
        updater.StartUpdate;
      end;
    finally
      updater.Free;
    end;
  end;
  frmSplash.InfoText := 'Uruchamianie programu...';

  actBusStopTimeTable.Visible:=false;
  actBusStopTimeTable.Category:='';
  {$ELSE}
  actBusStopTimeTable.Visible:=true;
  actBusStopTimeTable.Category:='Zarz¹dzanie przystankami';
  {$ENDIF}

  fFirstActive := True;
  MainFrm := Self;
  StatusBar := jvstbarMain;
  UserStatusPanel := jvstbarMain.Panels.Items[0];
  MessageStatusPanel := jvstbarMain.Panels.Items[2];

  HintWindowClass := TInfoFormatedHint;

  MainPanel := pMainPanel;
  FloatingPanel := pFloatingPanel;
  FloatingPanelCaption := stdtxtFloatingPanelCaption;
  ActionManager := actmgrMain;
  StartAct := actviewStart;
  {$IFNDEF EUREKALOG}
  Application.OnException := AppException;
  {$ENDIF}
  Caption := Application.Title + ' ' +'wersja '+ProductVersion;

  if MainFormUtil.OnFormCrete(AfterLoadLicence) then
  try
    fdmMain := dmMainGlobal;
    SetChoicePanelParent(pFormDatabaseItemChoice);

    Caption := Application.Title + ' ' +'wersja '+ProductVersion+' - '+XMLLicence_Name;

    tmrLive.Interval := AppParams.LivePingSecondsInterval * 1000;

    MainFormUtil.LoggedUser(actFileLogOut);
    if AppTerminated then
      Exit;
    tmrLogout.Enabled := True;
    tmrLive.Enabled := True;
    fTimeonIDLE := Now;
    tmrIdle.Enabled := True;

    ErrorHint.Images := imglErrorHint;
    ErrorHint.ImageIndex := 0;

    if Assigned(dmMainGlobal) and Assigned(dmMainGlobal.SQLConnection) then
      dmMainGlobal.SQLConnection.AfterDisconnect := SQLConnectionAfterDisconnect;



    LoadAppGlobalSettings;

    CreateFrames;

    CEFWindowParentMain:=TframeStartChromium(frameStartChromium).CEFWindowStartFrame; //CHROMIUM
    TframeStartChromium(frameStartChromium).BaseForm:=frmMainTurdus;     //Chromium

    AssignTagsToActions;

    ActionEnabled;

    actviewStart.Execute;
  finally
    Application.ShowMainForm := True;
  end
  else
  begin
    Application.Terminate;
    Sleep(1000);
  end;
end;

procedure TfrmMainTurdus.FormResize(Sender: TObject);
begin
  MainFormUtil.CenterFloatingPanel(Self)
end;

procedure TfrmMainTurdus.FormShow(Sender: TObject);
begin
  FreeAndNil(frmSplash);
  SplashFrm := nil;
  if not NoChromiumOnStart then  //chromium
  begin
    if not(ChromiumMain.CreateBrowser(CEFWindowParentMain, '')) then TimerMain.Enabled := True;
    if not(Chromium2.CreateBrowser(CEFWindowParentMain2, '')) then Timer2.Enabled := True;
  end;
end;

procedure TfrmMainTurdus.pFloatingPanelMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
  ReleaseCapture;
  pFloatingPanel.Perform(WM_SysCommand, $F012, 0);
end;

procedure TfrmMainTurdus.pFloatingPanelResize(Sender: TObject);
begin
  MainFormUtil.RevealFloatingPanel(Self)
end;

procedure TfrmMainTurdus.SQLConnectionAfterDisconnect(Sender: TObject);
var
  b: Boolean;
begin
  b := Self.PasswordAlert;
  try
    LogoutUser(b, actFileLogOut, actviewStart, tmrLogout, tmrIdle, tmrLive, SQLConnectionAfterDisconnect, ActionEnabled);
  finally
    Self.PasswordAlert := b;
  end;
end;

{$IFNDEF TURDUS_AP}
procedure TfrmMainTurdus.StartDownload(ASender: TObject; AWorkMode: TWorkMode;
  AWorkCountMax: Int64);
begin
  Application.ProcessMessages;
//  if Assigned(frmSplash) then
//    frmSplash.InfoText := 'Pobieram aktualizacjê...';
end;
{$ENDIF}

procedure TfrmMainTurdus.StopBusTraceTimer;
begin
  // if Assigned(frameDispatcher) then
  // frameDispatcher.StopBusTraceTimer;
end;

procedure TfrmMainTurdus.tmrIdleTimer(Sender: TObject);
var
  _SecondsIdle: Integer;
begin
  if cbIdle.Checked then
  begin
    MainFormUtil.OnIdleTimer(Sender, fTimeonIDLE, actFileLogOut, actviewStart, tmrLive, tmrLogout, tmrIdle, SQLConnectionAfterDisconnect, ActionEnabled);

    try
      _SecondsIdle := SecondsBetween(Now, fTimeonIDLE);
    except
      _SecondsIdle := 0;
    end;
    cbIdle.Caption := 'Automatyczne roz³¹czenie za ' + SecondsToStringTime(AppParams.AutoLogoffAfterSeconds - _SecondsIdle);
  end;
end;

procedure TfrmMainTurdus.tmrLiveTimer(Sender: TObject);
begin
  MainFormUtil.OnLiveTimer(actFileLogOut, actviewStart, tmrLive, tmrLogout, tmrIdle, SQLConnectionAfterDisconnect, ActionEnabled);
end;

procedure TfrmMainTurdus.tmrLogoutTimer(Sender: TObject);
begin
  MainFormUtil.OnLogOutTimer(actFileLogOut, actviewStart, tmrLive, tmrLogout, tmrIdle, SQLConnectionAfterDisconnect, ActionEnabled)
end;

procedure TfrmMainTurdus.actDISPFileEmar105Execute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareDISPFile;
      TframeDeviceManager(frameDeviceManager).ViewDISPFileEmar105(dmMainGlobal.cdsDISPFile, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actDISPFileSoloBusExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.TCPIPServerMethods.PrepareDISPFile;
      // TframeDeviceManager(frameDeviceManager).ViewDISPFileSoloBus(dmMainGlobal.cdsDISPFile, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actEmar105TicketsCancellationExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      TframeAccounts(frameAccounts).ViewTicketsCancellation(dmMainGlobal);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actEPodroznikExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      frameInformation.viewEPodroznik;
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTicketRegisterCardExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      BeforeFuncView((Sender As TAction).Caption);
      dmMainGlobal.DataSetOpen(dmMainGlobal.cdsStoredProcTicketRegisterCard);
      TframeDeviceManager(frameDeviceManager).ViewTicketRegisterCard(dmMainGlobal.cdsStoredProcTicketRegisterCard, []);
//      RefreshPriceList; // AT: by³ b³¹d, podej¿am ¿e to copy-paste z price-ów
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actTicketReliefPaymentExecute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_RELIEFTICKETS]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAnalysis,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAccounts(frameAccounts).ViewReportReliefTicketPayments, Params);
    finally
      UnPrepareInterface;
    end;
  end;
end;

//procedure TfrmMainTurdus.actTicketRegisterFileViewerExecute(Sender: TObject);
//begin
//  if LastView <> (Sender as TAction) then
//  begin
//    PrepareInterface;
//    try
//      LastView := (Sender as TAction);
//      TframeDeviceManager(frameDeviceManager).ViewTicketRegisterFileViewer;
//    finally
//      UnPrepareInterface;
//    end;
//  end;
//end;

procedure TfrmMainTurdus.actSalesReportLoaderExecute(Sender: TObject);
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
//      TframeDeviceManager(frameDeviceManager).ViewSaleReportsOfTicketRegisterCard(dmMainGlobal.cdsSalesReportOfTicketRegisterCard, []);
      TframeAccounts(frameAccounts).ViewSaleReportsOfTicketRegisterCard(dmMainGlobal.cdsSalesReportOfTicketRegisterCard, []);
    finally
      UnPrepareInterface;
    end;
  end;
end;

procedure TfrmMainTurdus.actSalesReportTransportExecute(Sender: TObject);
var
  Params : string;
begin
  if LastView <> (Sender as TAction) then
  begin
    PrepareInterface;
    try
      LastView := (Sender as TAction);
      HideChoicePanel;
      Params := Format('%d', [REPORT_TYPE_TRANSPORT]);
      Log((Sender As TAction).Caption, _LOG_VIEW_RUN);
      ReloadFrame(frameAccounts,
                  dmMainGlobal.cdsStoredProcAdmin_ReportDefWhereReportTypeId,
                  TframeAccounts(frameAccounts).ViewAccountsReport, Params);
    finally
      UnPrepareInterface;
    end;
  end;
end;


{$REGION 'Chromium main'}

procedure TfrmMainTurdus.Chromium2AfterCreated(Sender: TObject;
  const browser: ICefBrowser);
begin
  PostMessage(Handle, MYBROWSER_CEF_AFTERCREATED2, 0, 0);
end;

procedure TfrmMainTurdus.Chromium2BeforeClose(Sender: TObject;
  const browser: ICefBrowser);
begin
  FCanClose2 := True;
  if FCanClose then
    PostMessage(Handle, WM_CLOSE, 0, 0);
end;

procedure TfrmMainTurdus.Chromium2Close(Sender: TObject;
  const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
begin
  PostMessage(Handle, MYBROWSER_CEF_DESTROY2, 0, 0);
  aAction := cbaDelay;
end;

procedure TfrmMainTurdus.ChromiumMainAfterCreated(Sender: TObject;
  const browser: ICefBrowser);
begin
  PostMessage(Handle, CEF_AFTERCREATED, 0, 0);
end;

procedure TfrmMainTurdus.ChromiumMainBeforeClose(Sender: TObject;
  const browser: ICefBrowser);
begin
  FCanClose := True;
  if FCanClose2 then
    PostMessage(Handle, WM_CLOSE, 0, 0);
end;

procedure TfrmMainTurdus.ChromiumMainClose(Sender: TObject;
  const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
begin
  PostMessage(Handle, CEF_DESTROY, 0, 0);
  aAction := cbaDelay;
end;

procedure TfrmMainTurdus.ChromiumMainLoadingStateChange(Sender: TObject;
  const browser: ICefBrowser; isLoading, canGoBack, canGoForward: Boolean);
begin
  if not(ChromiumMain.IsSameBrowser(browser)) or FClosing then exit;

  TframeStartChromium(frameStartChromium).tbBack.Enabled    := canGoBack;
  TframeStartChromium(frameStartChromium).tbForward.Enabled := canGoForward;
  if isLoading then
    begin
      TframeStartChromium(frameStartChromium).pStatus.Caption := 'Wczytywanie...';
      TframeStartChromium(frameStartChromium).tbRefresh.Enabled:= False;
      TframeStartChromium(frameStartChromium).tbStop.Enabled   := True;
    end
   else
    begin
      TframeStartChromium(frameStartChromium).pStatus.Caption  := '';
      TframeStartChromium(frameStartChromium).tbRefresh.Enabled:= True;
      TframeStartChromium(frameStartChromium).tbStop.Enabled   := False;
    end;
end;

procedure TfrmMainTurdus.BrowserCreatedMsg(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentMain) then
    CEFWindowParentMain.UpdateSize;
  TframeStartChromium(frameStartChromium).tbtnHome.Click;
end;

procedure TfrmMainTurdus.BrowserDestroyMsg(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentMain) then begin
    CEFWindowParentMain.free;
    frameStartChromium.Free;
    frameStartChromium := nil;
  end;
end;

procedure TfrmMainTurdus.BrowserCreatedMsg2(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentMain2) then
    CEFWindowParentMain2.UpdateSize;
end;

procedure TfrmMainTurdus.BrowserDestroyMsg2(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentMain2) then begin
    CEFWindowParentMain2.free;
    frameInformation.Free;
    frameInformation := nil;
  end;
end;

procedure TfrmMainTurdus.Timer2Timer(Sender: TObject);
begin
  Timer2.Enabled := False;
  if not(Chromium2.CreateBrowser(CEFWindowParentMain2, '')) and not(Chromium2.Initialized) then
    Timer2.Enabled := True;
end;

procedure TfrmMainTurdus.TimerMainTimer(Sender: TObject);
begin
  TimerMain.Enabled := False;
  if not(ChromiumMain.CreateBrowser(CEFWindowParentMain, '')) and not(ChromiumMain.Initialized) then
    TimerMain.Enabled := True;
end;

procedure TfrmMainTurdus.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
begin
  if MainPanel.enabled then //nie jest zadokowana inna forma na formie Main
  begin
    {$IFDEF RELEASE}
    if AppTerminated then
      FFirstClosingAsk:=true
    else begin
      if (not FFirstClosingAsk) then
      begin
        if MessageDlg('Zamkn¹æ aplikacjê?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
          FFirstClosingAsk:=true
        else
          CanClose:=false;
      end;
    end;
    {$ENDIF}

    {$IFDEF DEBUG}
      FFirstClosingAsk:=true;
    {$ENDIF}
    if FFirstClosingAsk then
    begin
      if NoChromiumOnStart then
        CanClose := true
      else begin
        CanClose := FCanClose and FCanClose2;
        if not FClosing then begin
          FClosing := True;
          Visible  := False;
          ChromiumMain.CloseBrowser(True);
          Chromium2.CloseBrowser(True);
        end;
        if CanClose then begin
          Chromium2.Free;
          ChromiumMain.Free;
        end;
      end;
    end;
  end;
  // else
  //  CanClose := false;
end;
{$ENDREGION}

end.

