unit BaseEditorForm;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, BaseEditorFrame, BasicClasses, Buttons, StdCtrls, ExtCtrls,
  JvExControls, JvNavigationPane, ComCtrls, JvExExtCtrls, JvNetscapeSplitter,
  ImgList, KMMessages, DB, ActnList, Grids, DBGrids, VirtualTrees
  , System.ImageList, System.Actions, System.UITypes,
  uCEFChromiumCore, uCEFChromium, uCEFConstants, uCEFInterfaces, uCEFTypes,
  uCEFWindowParent, uCEFApplication
  ;

const
  MYBROWSER_OnMapClick                         = WM_APP + $101;
  MYBROWSER_OnGoogleMapTilesLoaded             = WM_APP + $102;
  MYBROWSER_OnRoadPointAdd                     = WM_APP + $103;
  MYBROWSER_OnGoogleMapDirectionsChanged       = WM_APP + $104;
  MYBROWSER_OnGoogleMapRoadPointMarkerDragEnd  = WM_APP + $105;
  MYBROWSER_OnGoogleMapRoadPointMarkerDblClick = WM_APP + $106;
  MYBROWSER_OnGoogleMapRoadPointMarkerClick    = WM_APP + $107;
  MYBROWSER_OnLoadOK                           = WM_APP + $108;
  MYBROWSER_OnMapViewChanged                   = WM_APP + $109;

  MYBROWSER_CEF_AFTERCREATED2                  = WM_APP + $110;
  MYBROWSER_CEF_DESTROY2                       = WM_APP + $111;
  MYBROWSER_OnGoogleMapRoadPointMarkerClick2   = WM_APP + $112;
  MYBROWSER_OnLoadOK2                          = WM_APP + $113;
  MYBROWSER_OnGoogleMapTilesLoaded2            = WM_APP + $114;
  MYBROWSER_OnMapViewChanged2                  = WM_APP + $115;

  MYBROWSER_ToMap3_Add                         = $10;
  MYBROWSER_CEF_AFTERCREATED3                  = MYBROWSER_CEF_AFTERCREATED2 + MYBROWSER_ToMap3_Add;
  MYBROWSER_CEF_DESTROY3                       = MYBROWSER_CEF_DESTROY2 + MYBROWSER_ToMap3_Add;
  MYBROWSER_OnGoogleMapRoadPointMarkerClick3   = MYBROWSER_OnGoogleMapRoadPointMarkerClick2 + MYBROWSER_ToMap3_Add;
  MYBROWSER_OnLoadOK3                          = MYBROWSER_OnLoadOK2 + MYBROWSER_ToMap3_Add;
  MYBROWSER_OnGoogleMapTilesLoaded3            = MYBROWSER_OnGoogleMapTilesLoaded2 + MYBROWSER_ToMap3_Add;
  MYBROWSER_OnMapViewChanged3                  = MYBROWSER_OnMapViewChanged2 + MYBROWSER_ToMap3_Add;

type

  TMySendData=class
    MessageText: string;
  	idr: Integer;
	  lat: double;
  	lon: double;
	  NElat: double;
  	NElon: double;
    SWlat: double;
    SWlon: double;
  	CurrentZoom: Integer;
    FirstMap : boolean;
	  json: string;
    FreeObject : boolean;
  end;

type
  TOnAfterDatabaseItemWrite = procedure of Object;
  TOnDatabaseItemWriteError = procedure(Sender: TObject; DatabaseItem : TDatabaseItem) of object;
  TProcAfterDock = procedure of object;

  TOnGeoPoint = procedure(index: integer; lat, lan: double) of object;
  TOnEvent = procedure(AParam: Variant) of object;
  TOnRoadPointEvent = procedure(Id: integer; lat, Lng: double) of object;
  TOnTilesLoaded = procedure of object;

  TOnRoadPointAdd = procedure of object;
  TOnMapClick = procedure(lat, Lng: double) of object;
  TOnMapDirectionsChanged = procedure(jasonobj: string) of object;

  TOnFirstPageLoad = procedure of object; //start page first time
  TOnFirstMapLoaded = procedure of object;//check first init page
  TOnLoadOK = procedure of object; //Load map ok
  TOnMapViewChanged = procedure(Zoom: integer; CenterLat, CenterLon, NorthEastLat, NorthEastLng, SouthWestLat, SouthWestLng: variant; aWait: integer = 1500) of object;

  TfrmBaseEditor = class(TForm)
    pCaption: TJvNavPanelHeader;
    pBottom: TPanel;
    btnOk: TButton;
    bitbtnSave: TBitBtn;
    bitbtnCancel: TBitBtn;
    lvMessage: TListView;
    jvMessage: TJvNetscapeSplitter;
    pMessage: TPanel;
    imglMessage: TImageList;
    btnHelp: TSpeedButton;
    img1: TImage;
    btnPrevItemOnList: TBitBtn;
    btnNextItemOnList: TBitBtn;
    CustomTitleButton1: TSpeedButton;
    ChromiumBase: TChromium;
    TimerBase: TTimer;
    ChromiumBase2: TChromium;
    TimerBase2: TTimer;
    ChromiumBase3: TChromium;
    TimerBase3: TTimer;
    procedure bitbtnSaveClick(Sender: TObject);
    procedure bitbtnCancelMouseActivate(Sender: TObject; Button: TMouseButton;
      Shift: TShiftState; X, Y, HitTest: Integer;
      var MouseActivate: TMouseActivate);
    procedure FormResize(Sender: TObject);
    procedure btnHelpClick(Sender: TObject);
    procedure btnPrevItemOnListClick(Sender: TObject);
    procedure btnNextItemOnListClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);
    procedure ChromiumBaseAfterCreated(Sender: TObject; const browser: ICefBrowser);
    procedure ChromiumBaseBeforeClose(Sender: TObject; const browser: ICefBrowser);
    procedure ChromiumBaseClose(Sender: TObject; const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
    procedure TimerBaseTimer(Sender: TObject);
    procedure ChromiumBaseProcessMessageReceived(Sender: TObject;
      const browser: ICefBrowser; const frame: ICefFrame;
      sourceProcess: TCefProcessId; const message: ICefProcessMessage;
      out Result: Boolean);
    procedure ChromiumBase2AfterCreated(Sender: TObject; const browser: ICefBrowser);
    procedure ChromiumBase2Close(Sender: TObject; const browser: ICefBrowser;  var aAction: TCefCloseBrowserAction);
    procedure ChromiumBase2ProcessMessageReceived(Sender: TObject; const browser: ICefBrowser; const frame: ICefFrame;
      sourceProcess: TCefProcessId; const message: ICefProcessMessage; out Result: Boolean);
    procedure ChromiumBase3AfterCreated(Sender: TObject; const browser: ICefBrowser);
    procedure ChromiumBase3Close(Sender: TObject; const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
  private
    { Private declarations }
    fReadOnly: Boolean;
    fInitGrid: boolean;
    fCurrentUserId: integer;
    FUseBrowser : Boolean;
    FUseBrowser2: Boolean;
    FUseBrowser3: Boolean;
    FAutoLogout : Boolean;
    FFrame: TframeBaseEditor;
    FAfterDatabaseItemWrite: TOnAfterDatabaseItemWrite;
    FSaveToDatabase: boolean;
    FWasSaveToDatabase: boolean; //do obs³ugi Chromium
    FSaveToDatabaseInTransaction: boolean;
    FDestroyItemOnExit : boolean;
    FApplicationUseHistory : Boolean;
    fMainFormDock: boolean;
    fParentOnClose: TCloseEvent;
    fParentWidth, fParentHeight: integer;
    fShowModalOldStyle: boolean;
    FDatabaseItemWriteError: TOnDatabaseItemWriteError;
    lCaption: TCaption;
    FOnBeforeClose: TOnBeforeCloseEvent;
    FOnBeforeWrite: TNotifyEvent;
    FOnAfterWrite: TNotifyEvent;
    FGridDataSet: TDataSet;
    FParams: array of Variant;
    FOnAfterShow: TNotifyEvent;
    fBeforeChangeItemOnList: TNotifyEvent;

    fOnGeoPoint: TOnGeoPoint;
    fOnEvent: TOnEvent;
    fRoadPointMarkerDblClick: TOnRoadPointEvent;
    fRoadPointMarkerClick: TOnRoadPointEvent;
    fRoadPointMarkerDragEnd: TOnRoadPointEvent;
    fOnTilesLoaded: TOnTilesLoaded;
    fOnRoadPointAdd: TOnRoadPointAdd;
    fOnMapClick: TOnMapClick;

    fOnMapDirectionsChanged: TOnMapDirectionsChanged;
    fOnFirstPageLoad: TOnFirstPageLoad;
    fOnFirstMapLoaded: TOnFirstMapLoaded;
    fOnLoadOK: TOnLoadOK;
    fTilesLoaded: boolean;
    fOnMapViewChanged: TOnMapViewChanged;

    fTilesLoaded2: boolean;
    fTilesLoaded3: boolean;
    fOnTilesLoaded2: TOnTilesLoaded;
    fOnTilesLoaded3: TOnTilesLoaded;
    fRoadPointMarkerClick2: TOnRoadPointEvent;
    fRoadPointMarkerClick3: TOnRoadPointEvent;
    fOnFirstPageLoad2: TOnFirstPageLoad;
    fOnFirstPageLoad3: TOnFirstPageLoad;
    fOnFirstMapLoaded2: TOnFirstMapLoaded;
    fOnFirstMapLoaded3: TOnFirstMapLoaded;
    fOnLoadOK2: TOnLoadOK;
    fOnLoadOK3: TOnLoadOK;
    fOnMapViewChanged2: TOnMapViewChanged;
    fOnMapViewChanged3: TOnMapViewChanged;

    procedure FreeObjectSendData(send_data: TMySendData);
    procedure FreeEvents;
    procedure SetFrame(const Value: TframeBaseEditor);
    function GetTitle: string;
    procedure SetTitle(const Value: string);
    procedure SetButtonsEnabled(const Value: Boolean);
    function GetButtonsEnabled: Boolean;
    procedure ParentClose(Sender: TObject; var Action: TCloseAction);
    function CreateFloatingPanel(AShowHelpButton : Boolean) : TPanel;
    procedure DestroyFloatingPanel(APanel : TPanel);
    procedure FloatingPanelMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X,
      Y: Integer);
    procedure FloatingPanelResize(Sender: TObject);
    procedure CloseBaseEditor;
    procedure SetBeforeClose(const Value: TOnBeforeCloseEvent);
    procedure DoBeforeClose(Sender: TObject; aModalResult: TModalResult; var AContinueClose: Boolean);
    procedure DoAfterShow;
    procedure OnHelpButtonClick(Sender : TObject);
    procedure SetOnAfterWrite(const Value: TNotifyEvent);
    procedure SetOnBeforeWrite(const Value: TNotifyEvent);
    function GetCaption: TCaption;
    procedure SetCaption(const Value: TCaption);
    procedure SetButtonNextPrevEnabled;
    procedure ModifyDatePickerFormat(const AControl: TControl);
    function CanSend_WM_CLOSE: boolean;

    { Map events - for all maps }
    procedure _BrowserCreatedMsg(aCEFWindowParentBase: TCEFWindowParent; aOnFirstPageLoad: TOnFirstPageLoad);
    function  _GetParamsFromMessage(var aMessage: TMessage; var aParams: TMySendData): boolean;
    procedure _OnMapLoaded(var aMessage: TMessage; aOnLoadOK: TOnLoadOK);
    procedure _OnMapRoadPointMarkerEvent(var aMessage: TMessage; aRoadPointMarkerEvent: TOnRoadPointEvent);
    procedure _OnMapTilesLoaded(var aMessage: TMessage; aOnFirstMapLoaded: TOnFirstMapLoaded; aOnTilesLoaded: TOnTilesLoaded);
    procedure _OnMapViewChanged(var aMessage: TMessage; aOnMapViewChanged: TOnMapViewChanged);
  protected
    FDatabaseItem: TDatabaseItem;
    FModalResult : Integer;
    FContinueClose : boolean;

    FCanClose : boolean;  // Set to True in TChromium.OnBeforeClose
    FCanClose2: boolean;  // Set to True in TChromium.OnBeforeClose
    FCanClose3: boolean;  // Set to True in TChromium.OnBeforeClose
    FClosing  : boolean;  // Set to True in the CloseQuery event.

    procedure BrowserDestroyMsg(var aMessage: TMessage); message CEF_DESTROY;
    procedure BrowserDestroyMsg2(var aMessage: TMessage); message MYBROWSER_CEF_DESTROY2;
    procedure BrowserDestroyMsg3(var aMessage: TMessage); message MYBROWSER_CEF_DESTROY3;

    procedure MSG_OnMapClick(var aMessage: TMessage); message MYBROWSER_OnMapClick;
    procedure MSG_OnRoadPointAdd(var aMessage: TMessage); message MYBROWSER_OnRoadPointAdd;
    procedure MSG_OnGoogleMapDirectionsChanged(var aMessage: TMessage); message MYBROWSER_OnGoogleMapDirectionsChanged;

    // served with _BrowserCreatedMsg
    procedure BrowserCreatedMsg(var aMessage: TMessage); message CEF_AFTERCREATED;
    procedure BrowserCreatedMsg2(var aMessage: TMessage); message MYBROWSER_CEF_AFTERCREATED2;
    procedure BrowserCreatedMsg3(var aMessage: TMessage); message MYBROWSER_CEF_AFTERCREATED3;

    // served with _OnMapViewChanged
    procedure MSG_OnMapViewChanged(var aMessage: TMessage); message MYBROWSER_OnMapViewChanged;
    procedure MSG_OnMapViewChanged2(var aMessage: TMessage); message MYBROWSER_OnMapViewChanged2;
    procedure MSG_OnMapViewChanged3(var aMessage: TMessage); message MYBROWSER_OnMapViewChanged3;

    // served with _OnMapRoadPointMarkerEvent
    procedure MSG_OnGoogleMapRoadPointMarkerDblClick(var aMessage: TMessage); message MYBROWSER_OnGoogleMapRoadPointMarkerDblClick;
    procedure MSG_OnGoogleMapRoadPointMarkerDragEnd(var aMessage: TMessage); message MYBROWSER_OnGoogleMapRoadPointMarkerDragEnd;
    procedure MSG_OnGoogleMapRoadPointMarkerClick(var aMessage: TMessage); message MYBROWSER_OnGoogleMapRoadPointMarkerClick;
    procedure MSG_OnGoogleMapRoadPointMarkerClick2(var aMessage: TMessage); message MYBROWSER_OnGoogleMapRoadPointMarkerClick2;
    procedure MSG_OnGoogleMapRoadPointMarkerClick3(var aMessage: TMessage); message MYBROWSER_OnGoogleMapRoadPointMarkerClick3;

    // served with _OnMapLoaded
    procedure MSG_OnLoadOK(var aMessage: TMessage); message MYBROWSER_OnLoadOK;
    procedure MSG_OnLoadOK2(var aMessage: TMessage); message MYBROWSER_OnLoadOK2;
    procedure MSG_OnLoadOK3(var aMessage: TMessage); message MYBROWSER_OnLoadOK3;

    // served with _OnMapTilesLoaded
    procedure MSG_OnGoogleMapTilesLoaded(var aMessage: TMessage); message MYBROWSER_OnGoogleMapTilesLoaded;
    procedure MSG_OnGoogleMapTilesLoaded2(var aMessage: TMessage); message MYBROWSER_OnGoogleMapTilesLoaded2;
    procedure MSG_OnGoogleMapTilesLoaded3(var aMessage: TMessage); message MYBROWSER_OnGoogleMapTilesLoaded3;
  public
    { Public declarations }
    FvstData: TVirtualStringTree;
    HideBtnSave: boolean;
    fIsInternet: boolean;
    CEFWindowParentBase : TCEFWindowParent;
    CEFWindowParentBase2: TCEFWindowParent;
    CEFWindowParentBase3: TCEFWindowParent;

    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;

    procedure DisableFormButtons(Sender : TObject; ADisable : Boolean);
    procedure Initialize(DatabaseItem: TDatabaseItem; AReadOnly: Boolean; AParams: array of Variant; AGridDataSet: TDataSet = nil); overload;
    procedure Initialize(DatabaseItem : TDatabaseItem; AFrameMode : TFrameEditorMode; AParams: array of Variant); overload;
    procedure Maximize;
    procedure MessageAdd(aType: TKMMessageType; aMessag: string; aData: Pointer);
    function MessageCount(aType: TKMMessageType): integer;
    procedure MessageInsert(aIndex: integer; aType: TKMMessageType; aMessag: string; aData: Pointer);
    procedure MessageRemove(aData: Pointer);
    procedure MessagesClear;
    procedure ResizeWindow(aWidth, aHeight: integer);
    procedure SetCustomTitleButton(aNo, aImageIndex: integer; aOnClick: TNotifyEvent; aHint: string = '');
    function ShowModal: Integer; override;
    function ShowModalWizard(ADockParent : TWinControl; AProcAfterDock : TProcAfterDock = nil; AShowHelpButton : Boolean = false) : Integer;

    property Caption: TCaption read GetCaption write SetCaption;
    property Title: string read GetTitle write SetTitle;
    property Frame: TframeBaseEditor read FFrame write SetFrame;
    property DatabaseItem: TDatabaseItem read FDatabaseItem;
    property OnAfterDatabaseItemWrite: TOnAfterDatabaseItemWrite read FAfterDatabaseItemWrite write FAfterDatabaseItemWrite;
    property OnDatabaseItemWriteError: TOnDatabaseItemWriteError read FDatabaseItemWriteError write FDatabaseItemWriteError;
    property SaveToDatabase: boolean read FSaveToDatabase write FSaveToDatabase default True;
    property SaveToDatabaseInTransaction: boolean read FSaveToDatabaseInTransaction write FSaveToDatabaseInTransaction default False;
    property DestroyItemOnExit : boolean read FDestroyItemOnExit write FDestroyItemOnExit default True;
    property ButtonsEnabled : Boolean read GetButtonsEnabled write SetButtonsEnabled;
    property MainFormDock: boolean read fMainFormDock write fMainFormDock;
    property ShowModalOldStyle: boolean read fShowModalOldStyle write fShowModalOldStyle;
    property AutoLogout : Boolean read FAutoLogout write FAutoLogout;
    property OnBeforeClose : TOnBeforeCloseEvent read FOnBeforeClose write SetBeforeClose;
    property OnAfterShow : TNotifyEvent read FOnAfterShow write FOnAfterShow;
    property OnBeforeWrite : TNotifyEvent read FOnBeforeWrite write SetOnBeforeWrite;
    property OnAfterWrite : TNotifyEvent read FOnAfterWrite write SetOnAfterWrite;
    property ReadOnly: boolean read fReadOnly;
    property OnBeforeChangeItemOnList: TNotifyEvent read fBeforeChangeItemOnList write fBeforeChangeItemOnList;

    // Google Maps
    property TilesLoaded : Boolean read fTilesLoaded write fTilesLoaded;
    property TilesLoaded2 : Boolean read fTilesLoaded2 write fTilesLoaded2;
    property TilesLoaded3 : Boolean read fTilesLoaded3 write fTilesLoaded3;
    property UseBrowser : Boolean read FUseBrowser write FUseBrowser;
    property UseBrowser2: Boolean read FUseBrowser2 write FUseBrowser2;
    property UseBrowser3: Boolean read FUseBrowser3 write FUseBrowser3;

    property OnEvent: TOnEvent read fOnEvent write fOnEvent;
    property OnGeoPoint: TOnGeoPoint read fOnGeoPoint write fOnGeoPoint;

    // Map 1
    property OnFirstMapLoaded: TOnFirstMapLoaded read fOnFirstMapLoaded write fOnFirstMapLoaded; //check first init map
    property OnFirstPageLoad: TOnFirstPageLoad read fOnFirstPageLoad write fOnFirstPageLoad; //after initialize Chromium
    property OnLoadOK: TOnLoadOK read fOnLoadOK write fOnLoadOK; //check first init map
    property OnMapClick: TOnMapClick read fOnMapClick write fOnMapClick;
    property OnMapDirectionsChanged: TOnMapDirectionsChanged read fOnMapDirectionsChanged write fOnMapDirectionsChanged;
    property OnMapViewChanged: TOnMapViewChanged read fOnMapViewChanged write fOnMapViewChanged;
    property OnRoadPointAdd: TOnRoadPointAdd read fOnRoadPointAdd write fOnRoadPointAdd;
    property OnRoadPointMarkerClick: TOnRoadPointEvent read fRoadPointMarkerClick write fRoadPointMarkerClick;
    property OnRoadPointMarkerDblClick: TOnRoadPointEvent read fRoadPointMarkerDblClick write fRoadPointMarkerDblClick;
    property OnRoadPointMarkerDragEnd: TOnRoadPointEvent read fRoadPointMarkerDragEnd write fRoadPointMarkerDragEnd;
    property OnTilesLoaded: TOnTilesLoaded read fOnTilesLoaded write fOnTilesLoaded;

    // Map 2
    property OnFirstMapLoaded2: TOnFirstMapLoaded read fOnFirstMapLoaded2 write fOnFirstMapLoaded2; //check first init map
    property OnFirstPageLoad2: TOnFirstPageLoad read fOnFirstPageLoad2 write fOnFirstPageLoad2; //after initialize Chromium
    property OnLoadOK2: TOnLoadOK read fOnLoadOK2 write fOnLoadOK2; //check first init map
    property OnMapViewChanged2: TOnMapViewChanged read fOnMapViewChanged2 write fOnMapViewChanged2;
    property OnMarkerClick2: TOnRoadPointEvent read fRoadPointMarkerClick2 write fRoadPointMarkerClick2;
    property OnTilesLoaded2: TOnTilesLoaded read fOnTilesLoaded2 write fOnTilesLoaded2;

    //Map 3
    property OnFirstMapLoaded3: TOnFirstMapLoaded read fOnFirstMapLoaded3 write fOnFirstMapLoaded3; //check first init map
    property OnFirstPageLoad3: TOnFirstPageLoad read fOnFirstPageLoad3 write fOnFirstPageLoad3; //after initialize Chromium
    property OnLoadOK3: TOnLoadOK read fOnLoadOK3 write fOnLoadOK3; //check first init map
    property OnMapViewChanged3: TOnMapViewChanged read fOnMapViewChanged3 write fOnMapViewChanged3;
    property OnMarkerClick3: TOnRoadPointEvent read fRoadPointMarkerClick3 write fRoadPointMarkerClick3;
    property OnTilesLoaded3: TOnTilesLoaded read fOnTilesLoaded3 write fOnTilesLoaded3;
  end;

implementation

{$R *.dfm}

uses
  Globals
  , KMUtils
{$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
  , TreeViewWithSearchFrame
{$IFEND}
{$IF Defined(FORIS) or Defined(PORTALOSK) or Defined(KARTY)}
  ,HelpContextHelpers
{$IFEND}
  , CommonDM
  , KMBasicUtil;

{ TfrmBaseEditor }

procedure TfrmBaseEditor.bitbtnCancelMouseActivate(Sender: TObject;
  Button: TMouseButton; Shift: TShiftState; X, Y, HitTest: Integer;
  var MouseActivate: TMouseActivate);
begin
  if Assigned(frame.OnCancelBtnActivate) then
    frame.OnCancelBtnActivate(Sender);
end;

procedure TfrmBaseEditor.bitbtnSaveClick(Sender: TObject);
begin
  ModalResult := (Sender As TCustomButton).ModalResult;
end;

procedure TfrmBaseEditor.btnHelpClick(Sender: TObject);
begin
  ExecuteHelpContext(Self);
end;

procedure TfrmBaseEditor.btnNextItemOnListClick(Sender: TObject);
{$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
var
  pom: PVirtualNode;
  p: TUserNodeData;
{$IFEND}
begin
  if Assigned(fBeforeChangeItemOnList) then
    fBeforeChangeItemOnList(Sender);

  Screen.Cursor := crHourGlass;
  if Assigned(MainFrm) then
    LockWindowUpdate(MainFrm.Handle);
  Application.ProcessMessages;
  try

    FDatabaseItem := DatabaseItem;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    pom := nil;
     if assigned(FvstData) then
       begin
         pom := FvstData.GetNext(FvstData.GetFirstSelected);
         FvstData.Selected[pom] := true;
       end
     else begin
  {$IFEND}
      FGridDataSet.DisableControls;
      try
        FGridDataSet.Next;
      finally
        FGridDataSet.EnableControls;
      end;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    end;
  {$IFEND}
    SetButtonNextPrevEnabled;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    if assigned(FvstData) then
      begin
        p:= TUserNodeData(FvstData.GetNodeData(pom)^);
        FDatabaseItem.ReadFromDatabase(p.id)
      end
    else
  {$IFEND}
      FDatabaseItem.ReadFromDatabase(FGridDataSet.FieldByName('id').AsInteger);

    FFrame.PrepareInterface(FDatabaseItem, true, FParams);
  finally
    LockWindowUpdate(0);
    Screen.Cursor := crDefault;
    DoAfterShow;
  end;
end;

procedure TfrmBaseEditor.btnPrevItemOnListClick(Sender: TObject);
{$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
var
  pom: PVirtualNode;
  p: TUserNodeData;
{$IFEND}
begin
  if Assigned(fBeforeChangeItemOnList) then
    fBeforeChangeItemOnList(Sender);

  Screen.Cursor := crHourGlass;
  if Assigned(MainFrm) then
    LockWindowUpdate(MainFrm.Handle);
  Application.ProcessMessages;
  try
    FDatabaseItem := DatabaseItem;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    pom := nil;
     if assigned(FvstData) then
       begin
         pom := FvstData.GetPrevious(FvstData.GetFirstSelected);
         FvstData.Selected[pom] := true;
       end
     else begin
  {$IFEND}
      FGridDataSet.DisableControls;
      try
        FGridDataSet.Prior;
      finally
        FGridDataSet.EnableControls;
      end;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    end;
  {$IFEND}
    SetButtonNextPrevEnabled;
  {$IF not(Defined(ADMINTOOL) OR DEFINED(IMPORT))}
    if assigned(FvstData) then
      begin
        p:= TUserNodeData(FvstData.GetNodeData(pom)^);
        FDatabaseItem.ReadFromDatabase(p.id)
      end
    else
  {$IFEND}
      FDatabaseItem.ReadFromDatabase(FGridDataSet.FieldByName('id').AsInteger);

    FFrame.PrepareInterface(FDatabaseItem, true, FParams);
  finally
    LockWindowUpdate(0);
    Screen.Cursor := crDefault;
    DoAfterShow;
  end;
end;

constructor TfrmBaseEditor.Create(AOwner: TComponent);
begin
  inherited;
  if Assigned(CurrentUser) then
    fCurrentUserId := CurrentUser.Id
  else fCurrentUserId := 0;
  fIsInternet := IsInternetConnection;
  HideBtnSave := false;
  FAutoLogout := False;
  FUseBrowser := False;
  FUseBrowser2:= False;
  FUseBrowser3:= False;
  pCaption.TabStop := false;
  pCaption.Caption := '';
  FSaveToDatabase := True;
  FWasSaveToDatabase := FALSE;
  FSaveToDatabaseInTransaction := False;
  FDestroyItemOnExit := True;
  fMainFormDock := False;
  fShowModalOldStyle := False;
  FOnBeforeClose := DoBeforeClose;
  FOnAfterWrite := nil;
  FOnBeforeWrite := nil;
  fTilesLoaded := false;
  fTilesLoaded2 := false;
  fTilesLoaded3 := false;
end;

procedure TfrmBaseEditor.FormCreate(Sender: TObject);
begin
  fInitGrid := true;
  FCanClose := False;
  FCanClose2 := False;
  FCanClose3 := False;
  FClosing := False;
  FContinueClose := true;
  FModalResult :=0;
  FreeEvents;
end;

destructor TfrmBaseEditor.Destroy;
begin
  FreeEvents;

  if Assigned(FFrame) then FreeAndNil(FFrame);
  if FDestroyItemOnExit and Assigned(FDatabaseItem) then
          FreeAndNil(FDatabaseItem);
  MessagesClear;

{$IFNDEF FORIS_AP}
  if Assigned(CurrentUser) and (CurrentUser.Id <> fCurrentUserId)
     and Assigned(StartAct) then StartAct.Execute;
{$ENDIF}

  inherited;
end;

procedure TfrmBaseEditor.DestroyFloatingPanel(APanel: TPanel);
begin
  if Assigned(APanel) then
  begin
    FloatingPanelsList.Remove(APanel);
    if FloatingPanelsList.Count > 0 then
      FloatingPanelsList.Last.Enabled := True;
  end;
end;

procedure TfrmBaseEditor.DisableFormButtons(Sender : TObject; ADisable: Boolean);
begin
  SetButtonsEnabled(not ADisable);
end;

procedure TfrmBaseEditor.FloatingPanelMouseDown(Sender: TObject; Button: TMouseButton;
  Shift: TShiftState; X, Y: Integer);
begin
  ReleaseCapture;
  if Sender is TPanel then
    TPanel(Sender).Perform(WM_SysCommand, $F012, 0)
  else
  if Sender is TStaticText then
    TPanel(TStaticText(Sender).Owner.Owner).Perform(WM_SysCommand, $F012, 0)
end;

procedure TfrmBaseEditor.FloatingPanelResize(Sender: TObject);
begin
  if TPanel(Sender).Visible then
  begin
    if TPanel(Sender).Top < 0 then
      TPanel(Sender).Top := 0;
    if TPanel(Sender).Left < 0 then
      TPanel(Sender).Left := 0;
    if TPanel(Sender).Top + TPanel(Sender).Height > Height then
      TPanel(Sender).Top := Height - TPanel(Sender).Height;
    if TPanel(Sender).Left + TPanel(Sender).Width > Width then
      TPanel(Sender).Left := Width - TPanel(Sender).Width;
  end;
end;

procedure TfrmBaseEditor.DoAfterShow;
begin
  if Assigned(FOnAfterShow) then
    FOnAfterShow(self);
end;

procedure TfrmBaseEditor.DoBeforeClose(Sender: TObject; aModalResult: TModalResult; Var AContinueClose : Boolean);
begin
//  if FFrame is TframeBaseEditor then TframeBaseEditor( FFrame ).
  AContinueClose := FFrame.BeforeClose;
  FContinueClose := AContinueClose;
end;

procedure TfrmBaseEditor.FormActivate(Sender: TObject);
 var i: integer;
begin
  if Assigned(Frame) then
    if TframeBaseEditor(Frame).MultiInsert then
      with Frame do
      begin
        for i := 0 to ControlCount-1 do
        begin
          if (Controls[i] is TWinControl) and ((Controls[i] as TWinControl).TabOrder =0) then
          begin
            if (Controls[i] as TWinControl).CanFocus then
              try
               (Controls[i] as TWinControl).SetFocus;
              except

              end;
            exit;
          end;
        end;
      end;
  //SendMessage(Handle, WM_NEXTDLGCTL, 0, 0);
end;

procedure TfrmBaseEditor.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
begin
  if
    fIsInternet
    and (FUseBrowser or FUseBrowser2 or FUseBrowser3)
    and not NoChromiumOnStart
  then begin
    if not FContinueClose then begin
      CanClose := false;
      Exit;
    end;
    if not FClosing and (ModalResult = mrOk) and not FFrame.Validate then
      CanClose := false
    else begin
      CanClose := CanSend_WM_CLOSE;
      if not FClosing then begin
        FModalResult := ModalResult;
        FreeEvents;
        FClosing := True;
        Visible  := False;
        if FUseBrowser then
          ChromiumBase.CloseBrowser(True);
        if FUseBrowser2 then
          ChromiumBase2.CloseBrowser(True);
        if FUseBrowser3 then
          ChromiumBase3.CloseBrowser(True);
      end else
        if FModalResult <> 0 then
          ModalResult := FModalResult;
    end;
  end else
    FModalResult := ModalResult;
end;

procedure TfrmBaseEditor.FormClose(Sender: TObject; var Action: TCloseAction);
var AContinueClose : Boolean;
    r: integer;
    mr: TModalResult;
begin
  if (Not FWasSaveToDatabase) then
  begin
    if Assigned(FOnBeforeClose) then
    Begin
      AContinueClose := true;
      if fReadOnly then mr := mrNone
      else mr := ModalResult;
      FOnBeforeClose( Sender, mr, AContinueClose );
      if not AContinueClose then begin
        Action := caNone;
        Exit;
      end;
    End;

    if (ModalResult = mrOk) then
    begin
      if FFrame.Validate then
      begin
        Screen.Cursor := crHourGlass;
        Application.ProcessMessages;
        try
          if (not useBrowser)
              and (lvMessage.Items.Count > 0)
              and (MessageDlg('Zignoruj ostrze¿enia lub podpowiedzi?', mtConfirmation, [mbYes, mbNo], 0) <> mrYes) then
          begin
            Action := caNone;
            Exit;
          end;
          FFrame.GetValuesFromInterface(FDatabaseItem);
          if FSaveToDatabase then
          begin
            if FSaveToDatabaseInTransaction then begin
              r := 0;
              if not FDatabaseItem.WriteToDatabase(r, '') then
              Begin
                 if Assigned(FDatabaseItemWriteError) then
                       FDatabaseItemWriteError(self, FDatabaseItem);
                Action := caNone;
                Exit;
              End
              else
                FWasSaveToDatabase:=true;
            end
            else
            begin
              if not FDatabaseItem.WriteToDatabase then
              Begin
                if Assigned(FDatabaseItemWriteError) then
                      FDatabaseItemWriteError(self, FDatabaseItem);
                Action := caNone;
                Exit;
              End
              else
                FWasSaveToDatabase:=true;
             end
           end
           else if Assigned(FAfterDatabaseItemWrite) then
             FAfterDatabaseItemWrite;
        finally
           Screen.Cursor := crDefault;
           Application.ProcessMessages;
        end;
      end
      else begin
        Action := caNone;
        Exit;
      end;
    end
    else
      if not fShowModalOldStyle and Assigned(MainPanel) then CloseBaseEditor;
  end;
end;


procedure TfrmBaseEditor.FreeEvents;
begin
  OnTilesLoaded:=nil;
  OnRoadPointAdd:=nil;
  OnFirstPageLoad:=nil;
  OnFirstMapLoaded:=nil;
  OnMapClick:= nil;

  OnMapDirectionsChanged:=nil;
  OnRoadPointMarkerDragEnd:=nil;
  OnRoadPointMarkerDblClick:=nil;

  OnRoadPointMarkerClick:=nil;
  OnEvent:=nil;
  OnGeoPoint:=nil;
  OnMapViewChanged:=nil;

  OnMapViewChanged2:=nil;
  OnMarkerClick2:=nil;
  OnTilesLoaded2:=nil;
  OnFirstPageLoad2:=nil;
  OnFirstMapLoaded2:=nil;
  OnLoadOK2:=nil;

  OnMapViewChanged3:=nil;
  OnMarkerClick3:=nil;
  OnTilesLoaded3:=nil;
  OnFirstPageLoad3:=nil;
  OnFirstMapLoaded3:=nil;
  OnLoadOK3:=nil;
end;

procedure TfrmBaseEditor.FormResize(Sender: TObject);
begin
  pMessage.Constraints.MaxHeight := Round((Self.ClientHeight - pCaption.Height - pBottom.Height)/2);
end;

procedure TfrmBaseEditor.FormShow(Sender: TObject);
begin
  if fInitGrid then begin
    fInitGrid := false;
    if Assigned(Frame) then
      Frame.LoadGridSettings;
  end;
  if fIsInternet then begin
    if FUseBrowser
       and not(ChromiumBase.CreateBrowser(CEFWindowParentBase, ''))
    then TimerBase.Enabled := True;
    if FUseBrowser2
       and not(ChromiumBase2.CreateBrowser(CEFWindowParentBase2, ''))
    then TimerBase2.Enabled := True;
    if FUseBrowser3
       and not(ChromiumBase3.CreateBrowser(CEFWindowParentBase3, ''))
    then TimerBase3.Enabled := True;
  end;
end;

function TfrmBaseEditor.GetButtonsEnabled: Boolean;
begin
  Result := bitbtnSave.Enabled
end;

function TfrmBaseEditor.GetCaption: TCaption;
begin
  Result := inherited Caption;
end;

function TfrmBaseEditor.GetTitle: string;
begin
  Result := pCaption.Caption;
end;

procedure TfrmBaseEditor.Initialize(DatabaseItem: TDatabaseItem;
  AFrameMode: TFrameEditorMode; AParams: array of Variant);
begin
  Frame.FrameEditorMode := AFrameMode;
  case AFrameMode of
    femInsert :
      begin
        DatabaseItem.Clear;
        Initialize(DatabaseItem, False, AParams);
      end;
    femEdit : Initialize(DatabaseItem, False, AParams);
    femProperties : Initialize(DatabaseItem, True, AParams);
  end;
end;


procedure TfrmBaseEditor.MessageAdd(aType: TKMMessageType; aMessag: string;
  aData: Pointer);
var
  m: TKMMessage;
begin
  lvMessage.Items.BeginUpdate;
  try
    m := TKMMessage.Create;
    m.MessageType := aType;
    m.Message := aMessag;
    m.Data := aData;
    with lvMessage.Items.Add do begin
      Caption := m.Message;
      Data := m;
      ImageIndex := Integer(m.MessageType);
      MakeVisible(True);
    end;
  finally
    lvMessage.Items.EndUpdate;
    if not jvMessage.Visible then begin
      pMessage.Visible := true;
      jvMessage.Visible := True;
    end;
  end;
end;

procedure TfrmBaseEditor.MessageInsert(aIndex: integer; aType: TKMMessageType;
  aMessag: string; aData: Pointer);
var
  m: TKMMessage;
begin
  lvMessage.Items.BeginUpdate;
  try
    m := TKMMessage.Create;
    m.MessageType := aType;
    m.Message := aMessag;
    m.Data := aData;
    with lvMessage.Items.Insert(aIndex) do begin
      Caption := m.Message;
      Data := m;
      ImageIndex := Integer(m.MessageType);
      MakeVisible(True);
    end;
  finally
    lvMessage.Items.EndUpdate;
    if not jvMessage.Visible then begin
      pMessage.Visible := true;
      jvMessage.Visible := True;
    end;
  end;
end;

function TfrmBaseEditor.MessageCount(aType: TKMMessageType): integer;
var i: integer;
begin
  Result := 0;
  for i := 0 to lvMessage.Items.Count - 1 do
    if
      Assigned(lvMessage.Items[i].Data)
      and (TKMMessage(lvMessage.Items[i].Data).MessageType = aType)
    then
      Inc(Result);
end;

procedure TfrmBaseEditor.MessagesClear;
var
  i: Integer;
begin
  if not Assigned(self) then
    exit;
  if Assigned(lvMessage) then begin
    for i := 0 to lvMessage.Items.Count - 1 do
      if Assigned(lvMessage.Items[i].Data) then
        TKMMessage(lvMessage.Items[i].Data).Free;
    lvMessage.Items.Clear;
  end;
  if Assigned(jvMessage) then
    jvMessage.Visible := False;
  if Assigned(pMessage) then
    pMessage.Visible := False;
end;

procedure TfrmBaseEditor.ModifyDatePickerFormat(const AControl: TControl);
var
  i: Integer;
begin
  if AControl=nil then Exit;
  if AControl is TWinControl then
  begin
    for i := 0 to TWinControl(AControl).ControlCount-1 do
    begin
         ModifyDatePickerFormat(TWinControl(AControl).Controls[i]);
    end;
  end;

  if AControl is TDateTimePicker then
  begin
     if (TDateTimePicker(AControl).Kind = dtkDate) then
        TDateTimePicker(AControl).Format := StringReplace(FormatSettings.ShortDateFormat,'m','M',[rfReplaceAll]);
  end;

end;

procedure TfrmBaseEditor.OnHelpButtonClick(Sender: TObject);
begin
  ExecuteHelpContext(Self);
end;

//function TfrmBaseEditor.GetWidth: Integer;
//begin
//  Result := inherited Width; ///
//end;

procedure TfrmBaseEditor.Initialize(DatabaseItem: TDatabaseItem; AReadOnly: Boolean; AParams: array of Variant; AGridDataSet: TDataSet = nil);
Var
  _ApplicationUseHistory : Integer;
  i: integer;
begin
  fReadOnly := AReadOnly;

  FDatabaseItem := DatabaseItem;
  FGridDataSet := AGridDataSet;

  if assigned(FGridDataSet) then
    begin
      btnPrevItemOnList.Visible := true;
      btnNextItemOnList.Visible := true;
      SetButtonNextPrevEnabled;
    end;

  for I := 0 to length(AParams) - 1 do
    begin
      Setlength(FParams, length(FParams)+1);
      FParams[i] := AParams[i]
    end;

  if not KMUtils.GetIntValueFromArrayVarName('ApplicationUseHistory',AParams,_ApplicationUseHistory) then
                 FApplicationUseHistory := False
                 Else
                  FApplicationUseHistory := _ApplicationUseHistory = 1;      // do czego to ???

  if Assigned(FFrame) then
    FFrame.PrepareInterface(DatabaseItem, AReadOnly, AParams);
  btnOk.Visible := AReadOnly;
  btnOk.Enabled := AReadOnly;
  bitbtnSave.Visible := (not AReadOnly) and (not HideBtnSave);
  bitbtnSave.Enabled := not AReadOnly;
  bitbtnCancel.Visible := not AReadOnly;
  bitbtnCancel.Enabled := not AReadOnly;
  if Assigned(FFrame) then
        FFrame.TabStop := not AReadOnly;
  if AReadOnly then pBottom.TabOrder := 0;


  {$IF Defined(FORIS) or Defined(PORTALOSK) or Defined(KARTY)}
  HelpContext := GetHelpContextForBaseEditor(FFrame, FDatabaseItem)
  {$IFEND}
end;

procedure TfrmBaseEditor.ParentClose(Sender: TObject; var Action: TCloseAction);
begin
  Self.ModalResult := mrCancel;
  if not (Application.Terminated or AppTerminated or AppIsClosed) then
    Action := caNone;
end;

procedure TfrmBaseEditor.MessageRemove(aData: Pointer);
var
  i: integer;
begin
  lvMessage.Items.BeginUpdate;
  try
    i := 0;
    while i < lvMessage.Items.Count do begin
      if Assigned(lvMessage.Items[i].Data) and
         (TKMMessage(lvMessage.Items[i].Data).Data = aData) then begin
        TKMMessage(lvMessage.Items[i].Data).Free;
        lvMessage.Items.Delete(i);
      end
      else Inc(i);
    end;
  finally
    lvMessage.Items.EndUpdate;
    jvMessage.Visible := lvMessage.Items.Count > 0;
    pMessage.Visible := lvMessage.Items.Count > 0;
  end;
end;

procedure TfrmBaseEditor.ResizeWindow(aWidth, aHeight: integer);
begin
  if (aHeight > Screen.Height) or
     (aWidth > Screen.Width) then begin
    if aWidth >  Screen.Width then
      Width := Screen.Width
    else Width := aWidth;
    if aHeight >  Screen.Height then
      Height := Screen.Height - 60
    else Height := aHeight
  end
  else begin
    Width := aWidth;
    Height := aHeight;
  end;
end;

procedure TfrmBaseEditor.SetBeforeClose(const Value: TOnBeforeCloseEvent);
begin
  FOnBeforeClose := Value;
end;

procedure TfrmBaseEditor.SetButtonNextPrevEnabled;
begin
 if assigned(FvstData) then
   begin
     btnPrevItemOnList.Enabled := assigned(FvstData.GetPrevious(FvstData.GetFirstSelected));
     btnNextItemOnList.Enabled := assigned(FvstData.GetNext(FvstData.GetFirstSelected));
   end
 else
   begin
     btnPrevItemOnList.Enabled := not FGridDataSet.Bof;
     btnNextItemOnList.Enabled := not FGridDataSet.Eof;
   end;
end;

procedure TfrmBaseEditor.SetButtonsEnabled(const Value: Boolean);
begin
  bitbtnSave.Enabled := Value;
  bitbtnCancel.Enabled := Value;
end;

procedure TfrmBaseEditor.SetCaption(const Value: TCaption);
begin
  inherited Caption := Value;
  if not fShowModalOldStyle and Assigned(MainPanel) then
    if Assigned(FloatingPanelCaption) then
      FloatingPanelCaption.Caption := Value;
end;

procedure TfrmBaseEditor.SetCustomTitleButton(aNo, aImageIndex: integer;
  aOnClick: TNotifyEvent; aHint: string);
var
  sb: TSpeedButton;
  b: TBitmap;
begin
  if aNo < 1 then
    CustomTitleButton1.Visible := false
  else begin
    sb := TSpeedButton(FindComponent('CustomTitleButton' + IntToStr(aNo)));
    if Assigned(sb) then begin
      b := dmCommon.GetGlossaryBaseGlyph(aImageIndex);
      if Assigned(b) then
        try
          sb.Glyph := b;
          sb.NumGlyphs := 2;
        finally
          b.Free;
        end;
      sb.Hint := aHint;
      sb.ShowHint := true;
      sb.OnClick := aOnClick;
      sb.Visible := true;
    end;
  end;
end;

procedure TfrmBaseEditor.SetFrame(const Value: TframeBaseEditor);
begin
  FFrame := Value;
  if Assigned(FFrame) then begin
    ClientWidth := FFrame.Width;
    ClientHeight := FFrame.Height + pCaption.Height + pBottom.Height;
    //FFrame := Value;
    FFrame.Parent := Self;
    FFrame.Align := alClient;
    FFrame.TabOrder := 0;
    FFrame.OnDisableButtons := DisableFormButtons;
  end;
end;

procedure TfrmBaseEditor.SetOnAfterWrite(const Value: TNotifyEvent);
begin
  FOnAfterWrite := Value;
end;

procedure TfrmBaseEditor.SetOnBeforeWrite(const Value: TNotifyEvent);
begin
  FOnBeforeWrite := Value;
end;

procedure TfrmBaseEditor.SetTitle(const Value: string);
begin
  if assigned(self) then
    pCaption.Caption := Value;
end;

procedure TfrmBaseEditor.CloseBaseEditor;
begin
  Application.MainForm.Caption := lCaption;
  if Assigned(FloatingPanel) then
    FloatingPanel.Visible := False;
  if Assigned(MainPanel) then
    MainPanel.Enabled := True;
  if Assigned(ActionManager) then
    ActionManager.State := asNormal;
  if Assigned(MainPanel) and Assigned(MainPanel.Parent) then begin
    if fMainFormDock then
      TForm(MainPanel.Parent).OnClose := fParentOnClose
    else begin
      TForm(MainPanel.Parent).Constraints.MinWidth := fParentWidth;
      TForm(MainPanel.Parent).Constraints.MinHeight := fParentHeight;
    end;
  end;
end;

procedure TfrmBaseEditor.Maximize;
begin
  if Parent = FloatingPanel then
     Begin
        BorderStyle := bsNone;
        FloatingPanel.Top := 0;
        FloatingPanel.Left := 0;
        FloatingPanel.Width := MainPanel.ClientWidth;
        FloatingPanel.Height := MainPanel.ClientHeight;
     End;
end;


function TfrmBaseEditor.ShowModal: Integer;
begin
  ModifyDatePickerFormat(self);
  if not fShowModalOldStyle and Assigned(MainPanel) then begin
    lCaption := Application.MainForm.Caption;
    MainPanel.Enabled := False;
    if Assigned(ActionManager) then
      ActionManager.State := asSuspended;
    try
      BorderStyle := bsNone;
      FloatingPanel.Width := Width + Margins.Left + Margins.Right;
      FloatingPanel.Height := Height + Margins.Top + Margins.Bottom;
      FloatingPanel.Left :=
        Round((TForm(FloatingPanel.Parent).Width - FloatingPanel.Width)/2);
      FloatingPanel.Top :=
        Round((TForm(FloatingPanel.Parent).Height - FloatingPanel.Height)/2);
      AlignWithMargins := not fMainFormDock;
      if not fMainFormDock then begin
        FloatingPanel.Visible := True;
        FloatingPanel.BringToFront;
        DrawRounded(FloatingPanel);
        ManualDock(FloatingPanel, nil);
        {$IFNDEF IMPORT}
        Editor := Self;
        {$ENDIF}
        Align := alClient;
        DrawRounded(Self, 3);
        pCaption.OnMouseDown := FloatingPanel.OnMouseDown;

        fParentWidth := TForm(MainPanel.Parent).Constraints.MinWidth;
        fParentHeight := TForm(MainPanel.Parent).Constraints.MinHeight;
        TForm(MainPanel.Parent).Constraints.MinWidth := FloatingPanel.Width +
          TForm(MainPanel.Parent).Width - TForm(MainPanel.Parent).ClientWidth;
        TForm(MainPanel.Parent).Constraints.MinHeight := FloatingPanel.Height +
          TForm(MainPanel.Parent).Height - TForm(MainPanel.Parent).ClientHeight;
        if Assigned(FloatingPanelCaption) then
          FloatingPanelCaption.Caption := Caption;
      end
      else begin
        Application.MainForm.Caption := Caption;
        ManualDock(MainPanel.Parent, nil);
        Align := alClient;
        BringToFront;
        fParentOnClose := TForm(MainPanel.Parent).OnClose;
        TForm(MainPanel.Parent).OnClose := ParentClose;
      end;
      Application.ProcessMessages;
      DoAfterShow;
      Visible := True;
      ModalResult := 0;
      repeat
        Application.HandleMessage;
        if Application.Terminated or AppTerminated or AppIsClosed or FAutoLogout then
          ModalResult := mrCancel
        else
          if ModalResult <> 0 then
            CloseModal;
      until ModalResult <> 0;
      Result := ModalResult;
    finally
      CloseBaseEditor;
    end;
  end
  else
    Result := inherited ShowModal;
end;


function TfrmBaseEditor.CreateFloatingPanel(AShowHelpButton : Boolean) : TPanel;
var
  pFloatingPanel: TPanel;
  stdtxtFloatingPanelCaption: TStaticText;
  btnHelp : TSpeedButton;
  pnl1: TPanel;
begin
    //pFloatingPanel
  pFloatingPanel := TPanel.Create(Self);
  if FloatingPanelsList.Count > 0 then
    FloatingPanelsList.Last.Enabled := False;

  FloatingPanelsList.Add(pFloatingPanel);

  //pnl1
  pnl1 := TPanel.Create(pFloatingPanel);

  //btnHelp
  btnHelp := TSpeedButton.Create(pFloatingPanel);

  //stdtxtFloatingPanelCaption
  stdtxtFloatingPanelCaption := TStaticText.Create(pnl1);

  //pFloatingPanel
  pFloatingPanel.Name := 'pFloatingPanel';
  pFloatingPanel.Parent := FloatingPanel.Parent;
  pFloatingPanel.Left := 217;
  pFloatingPanel.Top := 124;
  pFloatingPanel.Width := 460;
  pFloatingPanel.Height := 294;
  pFloatingPanel.BevelOuter := bvNone;
  pFloatingPanel.Color := clActiveCaption;
  pFloatingPanel.ParentBackground := False;
  pFloatingPanel.TabOrder := 1;
  pFloatingPanel.Visible := False;
  pFloatingPanel.Tag := Integer(stdtxtFloatingPanelCaption);
  pFloatingPanel.OnMouseDown := FloatingPanelMouseDown;
  pFloatingPanel.OnResize := FloatingPanelResize;

  //pnl1
  pnl1.Parent := pFloatingPanel;
  pnl1.Left := 0;
  pnl1.Top := 0;
  pnl1.Width := 467;
  pnl1.Height := 25;
  pnl1.Align := alTop;
  pnl1.BevelOuter := bvNone;
  pnl1.Color := clActiveCaption;
  pnl1.ParentBackground := False;
  pnl1.TabOrder := 0;

  //btnHelp
  btnHelp.Parent := pnl1;
  btnHelp.Left := 439;
  btnHelp.Top := 3;
  btnHelp.Width := 25;
  btnHelp.Height := 25;
  btnHelp.Align := alRight;
  btnHelp.AlignWithMargins := True;
  btnHelp.Margins.Left := 10;
  btnHelp.Margins.Top := 2;
  btnHelp.Margins.Right := 6;
  btnHelp.Margins.Bottom := 0;
  btnHelp.Flat := True;
  btnHelp.NumGlyphs := 2;
  btnHelp.Glyph.Assign(img1.Picture);
  btnHelp.Visible := AShowHelpButton;
  btnHelp.OnClick := OnHelpButtonClick;

  //stdtxtFloatingPanelCaption
  stdtxtFloatingPanelCaption.Name := 'stdtxtFloatingPanelCaption';
  stdtxtFloatingPanelCaption.Parent := pnl1;
  stdtxtFloatingPanelCaption.AlignWithMargins := True;
  stdtxtFloatingPanelCaption.Left := 10;
  stdtxtFloatingPanelCaption.Top := 8;
  stdtxtFloatingPanelCaption.Width := pFloatingPanel.Width - 40;
  stdtxtFloatingPanelCaption.Height := 17;
  stdtxtFloatingPanelCaption.Margins.Left := 10;
  stdtxtFloatingPanelCaption.Margins.Top := 8;
  stdtxtFloatingPanelCaption.Margins.Right := 10;
  stdtxtFloatingPanelCaption.Margins.Bottom := 4;
  stdtxtFloatingPanelCaption.Align := alClient;
  stdtxtFloatingPanelCaption.Caption := 'txtFloatingPanelCaption';
  stdtxtFloatingPanelCaption.Font.Charset := DEFAULT_CHARSET;
  stdtxtFloatingPanelCaption.Font.Color := clCaptionText;
  stdtxtFloatingPanelCaption.Font.Height := -11;
  stdtxtFloatingPanelCaption.Font.Name := 'Tahoma';
  stdtxtFloatingPanelCaption.Font.Style := [];
  stdtxtFloatingPanelCaption.ParentFont := False;
  stdtxtFloatingPanelCaption.TabOrder := 0;
  stdtxtFloatingPanelCaption.OnMouseDown := FloatingPanelMouseDown;

  Result := pFloatingPanel;
end;

function TfrmBaseEditor.ShowModalWizard(ADockParent : TWinControl; AProcAfterDock : TProcAfterDock; AShowHelpButton : Boolean): Integer;
var
  lCaption: string;
  FP : TPanel;
begin
  ModifyDatePickerFormat(self);
  FP := nil;
  if not fShowModalOldStyle and Assigned(MainPanel) then begin
    lCaption := Application.MainForm.Caption;
    if Assigned(ActionManager) then
      ActionManager.State := asSuspended;
    FP := CreateFloatingPanel(AShowHelpButton);
    try
      BorderStyle := bsNone;

      FP.Width := Width + Margins.Left + Margins.Right;
      FP.Height := Height + Margins.Top + Margins.Bottom;
      FP.Left := Round((TForm(FP.Parent).Width - FP.Width)/2);
      FP.Top := Round((TForm(FP.Parent).Height - FP.Height)/2);
      AlignWithMargins := not fMainFormDock;
      if not fMainFormDock then begin
        FP.Visible := True;
        FP.BringToFront;
        DrawRounded(FP);
        ManualDock(FP, nil);

        Align := alClient;
        Visible := True;
        DrawRounded(Self, 3);
        pCaption.OnMouseDown := FP.OnMouseDown;

        fParentWidth := TForm(MainPanel.Parent).Constraints.MinWidth;
        fParentHeight := TForm(MainPanel.Parent).Constraints.MinHeight;
        TForm(MainPanel.Parent).Constraints.MinWidth := FP.Width +
          TForm(MainPanel.Parent).Width - TForm(MainPanel.Parent).ClientWidth;
        TForm(MainPanel.Parent).Constraints.MinHeight := FP.Height +
          TForm(MainPanel.Parent).Height - TForm(MainPanel.Parent).ClientHeight;

        TStaticText(FP.Tag).Caption := Caption;
        MainPanel.Enabled := False;
      end
      else begin
        Application.MainForm.Caption := Caption;

        if not Assigned(ADockParent)  then
          ManualDock(MainPanel.Parent, nil)
        else
          ManualDock(ADockParent, nil);

        if Assigned(AProcAfterDock) then
          AProcAfterDock;

        Align := alClient;
        Visible := True;
        BringToFront;
        fParentOnClose := TForm(MainPanel.Parent).OnClose;
        TForm(MainPanel.Parent).OnClose := ParentClose;
      end;

      Application.ProcessMessages;
      DoAfterShow;
      ModalResult := 0;
      repeat
        Application.HandleMessage;
        if Application.Terminated or AppTerminated or AppIsClosed then ModalResult := mrCancel
        else
        if ModalResult <> 0 then CloseModal;
      until ModalResult <> 0;
      Result := ModalResult;
    finally
      Application.MainForm.Caption := lCaption;
      FP.Visible := False;
      if Assigned(MainPanel) then
        MainPanel.Enabled := FloatingPanelsList.Count = 1; // 1 bo zniszczenie i usuniêcie z listy bedize na konciu procedury
      if Assigned(ActionManager) then
        ActionManager.State := asNormal;
      if Assigned(MainPanel) and Assigned(MainPanel.Parent) then begin
        if fMainFormDock then
          TForm(MainPanel.Parent).OnClose := fParentOnClose
        else begin
          TForm(MainPanel.Parent).Constraints.MinWidth := fParentWidth;
          TForm(MainPanel.Parent).Constraints.MinHeight := fParentHeight;
        end;
      end;
    end;
  end
  else Result := inherited ShowModal;
  DestroyFloatingPanel(FP);
//  FP.Free;
end;

procedure TfrmBaseEditor.TimerBaseTimer(Sender: TObject);
begin
  case TComponent(Sender).Tag of
    2: begin
      TimerBase2.Enabled := False;
      if
        not NoChromiumOnStart
        and not(ChromiumBase2.CreateBrowser(CEFWindowParentBase2, ''))
        and not(ChromiumBase2.Initialized)
      then
        TimerBase2.Enabled := True;
    end;
    3: begin
      TimerBase3.Enabled := False;
      if
        not NoChromiumOnStart
        and not(ChromiumBase3.CreateBrowser(CEFWindowParentBase3, ''))
        and not(ChromiumBase3.Initialized)
      then
        TimerBase3.Enabled := True;
    end
    else begin
      TimerBase.Enabled := False;
      if
        not NoChromiumOnStart
        and not(ChromiumBase.CreateBrowser(CEFWindowParentBase, ''))
        and not(ChromiumBase.Initialized)
      then
        TimerBase.Enabled := True;
    end;
  end;
end;

procedure TfrmBaseEditor._BrowserCreatedMsg(aCEFWindowParentBase: TCEFWindowParent; aOnFirstPageLoad: TOnFirstPageLoad);
begin
  aCEFWindowParentBase.UpdateSize;
  if Assigned(aOnFirstPageLoad) then
    aOnFirstPageLoad;
end;

function TfrmBaseEditor._GetParamsFromMessage(var aMessage: TMessage; var aParams: TMySendData): boolean;
begin
  if (aMessage.wParam = 0) and (GlobalCEFApp <> nil) then begin
    aParams := TMySendData(aMessage.LParam);
    Exit(true);
  end;
  Result := false;
end;

procedure TfrmBaseEditor._OnMapLoaded(var aMessage: TMessage; aOnLoadOK: TOnLoadOK);
begin
  if (aMessage.wParam = 0) and (GlobalCEFApp <> nil) and Assigned(aOnLoadOK) then
    aOnLoadOK;
end;

procedure TfrmBaseEditor._OnMapRoadPointMarkerEvent(var aMessage: TMessage; aRoadPointMarkerEvent: TOnRoadPointEvent);
var
  get_data: TMySendData;
begin
  if _GetParamsFromMessage(aMessage, get_data) then
    try
      if Assigned(aRoadPointMarkerEvent) then
        aRoadPointMarkerEvent(get_data.idr,get_data.lat,get_data.lon);
    finally
      FreeObjectSendData(get_data);
    end;
end;

procedure TfrmBaseEditor._OnMapTilesLoaded(var aMessage: TMessage; aOnFirstMapLoaded: TOnFirstMapLoaded;
  aOnTilesLoaded: TOnTilesLoaded);
var
  get_data: TMySendData;
begin
  if _GetParamsFromMessage(aMessage, get_data) then
    try
      if get_data.FirstMap and Assigned(aOnFirstMapLoaded) then
        aOnFirstMapLoaded;
      if Assigned(aOnTilesLoaded) then
        aOnTilesLoaded;
    finally
      FreeObjectSendData(get_data);
    end;
end;

procedure TfrmBaseEditor._OnMapViewChanged(var aMessage: TMessage; aOnMapViewChanged: TOnMapViewChanged);
var
  get_data: TMySendData;
begin
  if _GetParamsFromMessage(aMessage, get_data) then
    try
      if Assigned(aOnMapViewChanged) then with get_data do
        aOnMapViewChanged(
          CurrentZoom,
          lat,    // center latitude
          lon,    // center longitude
          NElat,  // NorthEast latitude
          NElon,  // NorthEast longitude
          SWlat,  // SouthWest latitude
          SWlon   // SouthWest longitude
        );
    finally
      FreeObjectSendData(get_data);
    end;
end;

procedure TfrmBaseEditor.FreeObjectSendData(send_data: TMySendData);
begin
  if Assigned(send_data) then
  begin
    try
      if not send_data.FreeObject then
      begin
        send_data.FreeObject:=true;
        FreeAndNil(send_data);
      end;
    except

    end;
  end;
end;

procedure TfrmBaseEditor.ChromiumBaseProcessMessageReceived(Sender: TObject;
  const browser: ICefBrowser; const frame: ICefFrame;
  sourceProcess: TCefProcessId; const message: ICefProcessMessage;
  out Result: Boolean);
var send_data: TMySendData;
begin
  Result := false;
  if message.Name = 'OnMapClick' then begin
    Result := true;
    send_data:= TMySendData.Create;
    send_data.FreeObject := false;
    send_data.lat := message.ArgumentList.GetDouble(1);
    send_data.lon := message.ArgumentList.GetDouble(2);
    if not PostMessage(Handle, MYBROWSER_OnMapClick, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if (not fTilesLoaded) and (message.Name = 'OnGoogleMapTilesLoaded') then begin
    Result := true;
    fTilesLoaded := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.FirstMap := true;
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapTilesLoaded, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnGoogleMapTilesLoaded' then begin
    Result := true;
    fTilesLoaded := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.FirstMap := false;
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapTilesLoaded, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnRoadPointAdd' then begin
    Result := true;
    PostMessage(Handle, MYBROWSER_OnRoadPointAdd, 0, 0);
  end else if message.Name = 'OnGoogleMapDirectionsChanged' then begin
    Result := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.json := message.ArgumentList.GetString(1);
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapDirectionsChanged, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnGoogleMapRoadPointMarkerDragEnd' then begin
    Result := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.idr := message.ArgumentList.GetInt(1);
    send_data.lat := message.ArgumentList.GetDouble(2);
    send_data.lon := message.ArgumentList.GetDouble(3);
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapRoadPointMarkerDragEnd, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnGoogleMapRoadPointMarkerDblClick' then begin
    Result := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.idr := message.ArgumentList.GetInt(1);
    send_data.lat := message.ArgumentList.GetDouble(2);
    send_data.lon := message.ArgumentList.GetDouble(3);
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapRoadPointMarkerDblClick, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnGoogleMapRoadPointMarkerClick' then begin
    Result:=true;
    send_data := TMySendData.Create;
    send_data.FreeObject :=false;
    send_data.idr := message.ArgumentList.GetInt(1);
    send_data.lat := message.ArgumentList.GetDouble(2);
    send_data.lon := message.ArgumentList.GetDouble(3);
    if not PostMessage(Handle, MYBROWSER_OnGoogleMapRoadPointMarkerClick, 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
  end else if message.Name = 'OnLoadOK' then begin
    Result:=true;
    PostMessage(Handle, MYBROWSER_OnLoadOK, 0, 0);
  end;
end;

function TfrmBaseEditor.CanSend_WM_CLOSE: boolean;
begin
  Result :=
    ((FUseBrowser and FCanClose) or not FUseBrowser)
    and ((FUseBrowser2 and FCanClose2) or not FUseBrowser2)
    and ((FUseBrowser3 and FCanClose3) or not FUseBrowser3);
end;

procedure TfrmBaseEditor.ChromiumBase2AfterCreated(Sender: TObject; const browser: ICefBrowser);
begin
  PostMessage(Handle, MYBROWSER_CEF_AFTERCREATED2, 0, 0);
end;


procedure TfrmBaseEditor.ChromiumBaseAfterCreated(Sender: TObject; const browser: ICefBrowser);
begin
  PostMessage(Handle, CEF_AFTERCREATED, 0, 0);
end;

procedure TfrmBaseEditor.ChromiumBaseBeforeClose(Sender: TObject;
  const browser: ICefBrowser);
begin
  case TComponent(Sender).Tag of
    1: FCanClose := true;
    2: FCanClose2 := true;
    3: FCanClose3 := true;
  end;
  if CanSend_WM_CLOSE then
    PostMessage(Handle, WM_CLOSE, 0, 0);
end;

procedure TfrmBaseEditor.ChromiumBase2Close(Sender: TObject;
  const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
begin
  PostMessage(Handle, MYBROWSER_CEF_DESTROY2, 0, 0);
  aAction := cbaDelay;
end;

procedure TfrmBaseEditor.ChromiumBase2ProcessMessageReceived(Sender: TObject;
  const browser: ICefBrowser; const frame: ICefFrame;
  sourceProcess: TCefProcessId; const message: ICefProcessMessage;
  out Result: Boolean);
var
  send_data: TMySendData;
  tag: integer;
  function _m(aMsgID: cardinal): cardinal;
  begin
    if tag=2 then Exit(aMsgID);
    case aMsgID of
      MYBROWSER_OnMapViewChanged2,
      MYBROWSER_OnGoogleMapTilesLoaded2,
      MYBROWSER_OnGoogleMapRoadPointMarkerClick2,
      MYBROWSER_OnLoadOK2: Exit(aMsgID + MYBROWSER_ToMap3_Add);
    end;
    Result := 0;
  end;
begin
  // ChromiumBase2 and ChromiumBase3 only
  tag := TComponent(Sender).Tag;
  if (tag<2) or (tag>3) then begin
    Result := false;
    Exit;
  end;
  Result := true;
  if ((not fTilesLoaded2 and (tag=2)) or (not fTilesLoaded3 and (tag=3)))
    and (message.Name = 'OnGoogleMapTilesLoaded')
  then begin
    if tag=2 then fTilesLoaded2 := true
    else fTilesLoaded3 := true;
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.FirstMap := true;
    if not PostMessage(Handle, _m(MYBROWSER_OnGoogleMapTilesLoaded2), 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
    Exit;
  end;
  if message.Name = 'OnGoogleMapTilesLoaded' then begin
    send_data := TMySendData.Create;
    send_data.FreeObject := false;
    send_data.FirstMap := false;
    if not PostMessage(Handle, _m(MYBROWSER_OnGoogleMapTilesLoaded2), 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
    Exit;
  end;
  if message.Name = 'OnGoogleMapViewChanged' then begin
    send_data:= TMySendData.Create;
    send_data.FreeObject := false;
    send_data.CurrentZoom := message.ArgumentList.GetInt(1);
    send_data.lat := message.ArgumentList.GetDouble(2);
    send_data.lon := message.ArgumentList.GetDouble(3);
    send_data.NElat := message.ArgumentList.GetDouble(4);
    send_data.NElon := message.ArgumentList.GetDouble(5);
    send_data.SWlat := message.ArgumentList.GetDouble(6);
    send_data.SWlon := message.ArgumentList.GetDouble(7);
    if not PostMessage(Handle, _m(MYBROWSER_OnMapViewChanged2), 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
    Exit;
  end;

  if message.Name = 'OnGoogleMapRoadPointMarkerClick' then begin
    send_data:= TMySendData.Create;
    send_data.FreeObject := false;
    send_data.idr := message.ArgumentList.GetInt(1);
    send_data.lat := message.ArgumentList.GetDouble(2);
    send_data.lon := message.ArgumentList.GetDouble(3);
    if not PostMessage(Handle, _m(MYBROWSER_OnGoogleMapRoadPointMarkerClick2), 0, LPARAM(send_data)) then
      FreeObjectSendData(send_data);
    Exit;
  end;
  if message.Name = 'OnLoadOK' then begin
    PostMessage(Handle, _m(MYBROWSER_OnLoadOK2), 0, 0);
    Exit;
  end;
  Result := false;
end;

procedure TfrmBaseEditor.ChromiumBase3AfterCreated(Sender: TObject;
  const browser: ICefBrowser);
begin
  PostMessage(Handle, MYBROWSER_CEF_AFTERCREATED3, 0, 0);
end;

procedure TfrmBaseEditor.ChromiumBase3Close(Sender: TObject;
  const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
begin
  PostMessage(Handle, MYBROWSER_CEF_DESTROY3, 0, 0);
  aAction := cbaDelay;
end;

procedure TfrmBaseEditor.ChromiumBaseClose(Sender: TObject;
  const browser: ICefBrowser; var aAction: TCefCloseBrowserAction);
begin
  PostMessage(Handle, CEF_DESTROY, 0, 0);
  aAction := cbaDelay;
end;

procedure TfrmBaseEditor.BrowserCreatedMsg(var aMessage: TMessage);
begin
  _BrowserCreatedMsg(CEFWindowParentBase, fOnFirstPageLoad);
end;

procedure TfrmBaseEditor.BrowserDestroyMsg(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentBase) then FreeAndNil(CEFWindowParentBase);
end;

procedure TfrmBaseEditor.BrowserCreatedMsg2(var aMessage: TMessage);
begin
  _BrowserCreatedMsg(CEFWindowParentBase2, fOnFirstPageLoad2);
end;

procedure TfrmBaseEditor.BrowserCreatedMsg3(var aMessage: TMessage);
begin
  _BrowserCreatedMsg(CEFWindowParentBase3, fOnFirstPageLoad3);
end;

procedure TfrmBaseEditor.BrowserDestroyMsg2(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentBase2) then FreeAndNil(CEFWindowParentBase2);
end;

procedure TfrmBaseEditor.BrowserDestroyMsg3(var aMessage: TMessage);
begin
  if Assigned(CEFWindowParentBase3) then FreeAndNil(CEFWindowParentBase3);
end;

procedure TfrmBaseEditor.MSG_OnMapClick(var aMessage: TMessage);
var
  get_data: TMySendData;
begin
  if _GetParamsFromMessage(aMessage, get_data) then
    try
      if Assigned(fOnMapClick) then
        fOnMapClick(get_data.lat,get_data.lon);
    finally
      FreeObjectSendData(get_data);
    end;
end;

procedure TfrmBaseEditor.MSG_OnMapViewChanged(var aMessage: TMessage);
begin
  _OnMapViewChanged(aMessage, fOnMapViewChanged);
end;

procedure TfrmBaseEditor.MSG_OnMapViewChanged2(var aMessage: TMessage);
begin
  _OnMapViewChanged(aMessage, fOnMapViewChanged2);
end;

procedure TfrmBaseEditor.MSG_OnMapViewChanged3(var aMessage: TMessage);
begin
  _OnMapViewChanged(aMessage, fOnMapViewChanged3);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapTilesLoaded(var aMessage: TMessage);
begin
  _OnMapTilesLoaded(aMessage, fOnFirstMapLoaded, fOnTilesLoaded);
end;

procedure TfrmBaseEditor.MSG_OnRoadPointAdd(var aMessage: TMessage);
begin
  if (aMessage.wParam = 0) and (GlobalCEFApp <> nil)
    and Assigned(fOnFirstMapLoaded) and Assigned(fOnRoadPointAdd)
  then  begin
    fOnFirstMapLoaded;
    fOnRoadPointAdd;
  end;
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapDirectionsChanged(var aMessage: TMessage);
var
  get_data: TMySendData;
begin
  if _GetParamsFromMessage(aMessage, get_data) then
    try
      if Assigned(fOnMapDirectionsChanged) then
        fOnMapDirectionsChanged(get_data.json);
    finally
      FreeObjectSendData(get_data);
    end;
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapRoadPointMarkerDragEnd(var aMessage: TMessage);
begin
  _OnMapRoadPointMarkerEvent(aMessage, fRoadPointMarkerDragEnd);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapRoadPointMarkerDblClick(var aMessage: TMessage);
begin
  _OnMapRoadPointMarkerEvent(aMessage, fRoadPointMarkerDblClick);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapRoadPointMarkerClick(var aMessage: TMessage);
begin
  _OnMapRoadPointMarkerEvent(aMessage, fRoadPointMarkerClick);
end;

procedure TfrmBaseEditor.MSG_OnLoadOK(var aMessage: TMessage);
begin
  _OnMapLoaded(aMessage, fOnLoadOK);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapTilesLoaded2(var aMessage: TMessage);
begin
  _OnMapTilesLoaded(aMessage, fOnFirstMapLoaded2, fOnTilesLoaded2);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapTilesLoaded3(var aMessage: TMessage);
begin
  _OnMapTilesLoaded(aMessage, fOnFirstMapLoaded3, fOnTilesLoaded3);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapRoadPointMarkerClick2(var aMessage: TMessage);
begin
  _OnMapRoadPointMarkerEvent(aMessage, fRoadPointMarkerClick2);
end;

procedure TfrmBaseEditor.MSG_OnGoogleMapRoadPointMarkerClick3(var aMessage: TMessage);
begin
  _OnMapRoadPointMarkerEvent(aMessage, fRoadPointMarkerClick3);
end;

procedure TfrmBaseEditor.MSG_OnLoadOK2(var aMessage: TMessage);
begin
  _OnMapLoaded(aMessage, fOnLoadOK2);
end;

procedure TfrmBaseEditor.MSG_OnLoadOK3(var aMessage: TMessage);
begin
  _OnMapLoaded(aMessage, fOnLoadOK3);
end;

end.
