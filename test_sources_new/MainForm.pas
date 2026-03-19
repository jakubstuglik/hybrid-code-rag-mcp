unit MainForm;

interface

uses
  SysUtils, Classes, Windows, Messages,
  Forms, Controls, StdCtrls, ExtCtrls,
  Menus, ActnList, ComCtrls, Dialogs,
  MainDataMod, AppConst;

type
  TfrmMain = class(TForm)
    // ── Main menu ────────────────────────────────────────────────────
    MainMenu1: TMainMenu;
    mnuFile: TMenuItem;
    mnuFileNew: TMenuItem;
    mnuFileOpen: TMenuItem;
    mnuFileSave: TMenuItem;
    mnuFilePrint: TMenuItem;
    mnuFileSep1: TMenuItem;
    mnuFileExit: TMenuItem;
    mnuView: TMenuItem;
    mnuViewVehicles: TMenuItem;
    mnuViewDrivers: TMenuItem;
    mnuViewRoutes: TMenuItem;
    mnuViewJobs: TMenuItem;
    mnuViewReports: TMenuItem;
    mnuTools: TMenuItem;
    mnuToolsSettings: TMenuItem;
    mnuToolsUserAdmin: TMenuItem;
    mnuHelp: TMenuItem;
    mnuHelpAbout: TMenuItem;

    // ── Toolbar ──────────────────────────────────────────────────────
    ToolBar1: TToolBar;
    tbtnNew: TToolButton;
    tbtnOpen: TToolButton;
    tbtnSave: TToolButton;
    tbtnSep1: TToolButton;
    tbtnRefresh: TToolButton;
    tbtnPrint: TToolButton;
    tbtnSep2: TToolButton;
    tbtnExit: TToolButton;
    ImageList1: TImageList;

    // ── Action list ──────────────────────────────────────────────────
    ActionList1: TActionList;
    actNew: TAction;
    actOpen: TAction;
    actSave: TAction;
    actPrint: TAction;
    actRefresh: TAction;
    actExit: TAction;
    actVehicleView: TAction;
    actDriverView: TAction;
    actRouteView: TAction;
    actJobView: TAction;
    actReportView: TAction;
    actSettings: TAction;
    actUserAdmin: TAction;
    actAbout: TAction;

    // ── Status bar ───────────────────────────────────────────────────
    StatusBar1: TStatusBar;

    // ── Main panel layout ────────────────────────────────────────────
    pnlLeft: TPanel;
    pnlMain: TPanel;
    pnlBottom: TPanel;
    Splitter1: TSplitter;

    // ── Navigation tree ──────────────────────────────────────────────
    tvNavigation: TTreeView;

    // ── Tab control for main content ─────────────────────────────────
    PageControl1: TPageControl;
    tabVehicles: TTabSheet;
    tabDrivers: TTabSheet;
    tabRoutes: TTabSheet;
    tabJobOrders: TTabSheet;
    tabReports: TTabSheet;

    // ── Form events ──────────────────────────────────────────────────
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);

    // ── Action handlers ──────────────────────────────────────────────
    procedure actNewExecute(Sender: TObject);
    procedure actOpenExecute(Sender: TObject);
    procedure actSaveExecute(Sender: TObject);
    procedure actPrintExecute(Sender: TObject);
    procedure actRefreshExecute(Sender: TObject);
    procedure actExitExecute(Sender: TObject);
    procedure actVehicleViewExecute(Sender: TObject);
    procedure actDriverViewExecute(Sender: TObject);
    procedure actRouteViewExecute(Sender: TObject);
    procedure actJobViewExecute(Sender: TObject);
    procedure actReportViewExecute(Sender: TObject);
    procedure actSettingsExecute(Sender: TObject);
    procedure actUserAdminExecute(Sender: TObject);
    procedure actAboutExecute(Sender: TObject);

    procedure tvNavigationClick(Sender: TObject);
    procedure tvNavigationDblClick(Sender: TObject);
    procedure PageControl1Change(Sender: TObject);

  private
    FCurrentModule: string;
    FModified: Boolean;
    FStatusMessage: string;

    procedure SetStatusMessage(const AMsg: string);
    procedure LoadNavigationTree;
    procedure ShowModule(const AModuleName: string);
    procedure RefreshCurrentView;
    procedure UpdateActionStates;

  public
    procedure ShowStatusMsg(const AMsg: string; ATimeoutMs: Integer = 3000);
    procedure SetModified(AValue: Boolean);
    function ConfirmDiscard: Boolean;

    property CurrentModule: string read FCurrentModule;
    property Modified: Boolean read FModified;
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

uses
  SplashForm, AboutForm, SettingsForm;

// ────────────────────────────────────────────────────────────────────
// Form lifecycle
// ────────────────────────────────────────────────────────────────────

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  FModified := False;
  FCurrentModule := '';
  LoadNavigationTree;
  UpdateActionStates;
end;

procedure TfrmMain.FormDestroy(Sender: TObject);
begin
  // nothing
end;

procedure TfrmMain.FormShow(Sender: TObject);
begin
  dmFleet.OpenConnection;
  SetStatusMessage('Connected to ' + dmFleet.GetServerVersion);
end;

procedure TfrmMain.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
begin
  CanClose := not FModified or ConfirmDiscard;
end;

// ────────────────────────────────────────────────────────────────────
// Navigation
// ────────────────────────────────────────────────────────────────────

procedure TfrmMain.LoadNavigationTree;
var
  root, child: TTreeNode;
begin
  tvNavigation.Items.BeginUpdate;
  try
    tvNavigation.Items.Clear;
    root := tvNavigation.Items.AddChild(nil, 'Fleet Management');
    tvNavigation.Items.AddChild(root, 'Vehicles');
    tvNavigation.Items.AddChild(root, 'Drivers');
    tvNavigation.Items.AddChild(root, 'Routes');
    root.Expand(False);
    child := tvNavigation.Items.AddChild(nil, 'Dispatch');
    tvNavigation.Items.AddChild(child, 'Job Orders');
    tvNavigation.Items.AddChild(child, 'Live Map');
    child.Expand(False);
    root := tvNavigation.Items.AddChild(nil, 'Reports');
    tvNavigation.Items.AddChild(root, 'Driver Payroll');
    tvNavigation.Items.AddChild(root, 'Fuel Costs');
    tvNavigation.Items.AddChild(root, 'KPIs');
  finally
    tvNavigation.Items.EndUpdate;
  end;
end;

procedure TfrmMain.tvNavigationClick(Sender: TObject);
begin
  if tvNavigation.Selected <> nil then
    ShowModule(tvNavigation.Selected.Text);
end;

procedure TfrmMain.tvNavigationDblClick(Sender: TObject);
begin
  tvNavigationClick(Sender);
end;

procedure TfrmMain.ShowModule(const AModuleName: string);
begin
  FCurrentModule := AModuleName;
  RefreshCurrentView;
end;

procedure TfrmMain.PageControl1Change(Sender: TObject);
begin
  RefreshCurrentView;
end;

procedure TfrmMain.RefreshCurrentView;
begin
  dmFleet.ReconnectIfNeeded;
  // Refresh active tab data
  UpdateActionStates;
end;

// ────────────────────────────────────────────────────────────────────
// Actions
// ────────────────────────────────────────────────────────────────────

procedure TfrmMain.actNewExecute(Sender: TObject);
begin
  if ConfirmDiscard then
  begin
    FModified := False;
    ShowModule('');
  end;
end;

procedure TfrmMain.actOpenExecute(Sender: TObject);
begin
  // open job order or record
end;

procedure TfrmMain.actSaveExecute(Sender: TObject);
begin
  FModified := False;
  ShowStatusMsg('Saved');
end;

procedure TfrmMain.actPrintExecute(Sender: TObject);
begin
  // print current view
end;

procedure TfrmMain.actRefreshExecute(Sender: TObject);
begin
  RefreshCurrentView;
  ShowStatusMsg('Refreshed');
end;

procedure TfrmMain.actExitExecute(Sender: TObject);
begin
  Close;
end;

procedure TfrmMain.actVehicleViewExecute(Sender: TObject);
begin
  PageControl1.ActivePage := tabVehicles;
end;

procedure TfrmMain.actDriverViewExecute(Sender: TObject);
begin
  PageControl1.ActivePage := tabDrivers;
end;

procedure TfrmMain.actRouteViewExecute(Sender: TObject);
begin
  PageControl1.ActivePage := tabRoutes;
end;

procedure TfrmMain.actJobViewExecute(Sender: TObject);
begin
  PageControl1.ActivePage := tabJobOrders;
end;

procedure TfrmMain.actReportViewExecute(Sender: TObject);
begin
  PageControl1.ActivePage := tabReports;
end;

procedure TfrmMain.actSettingsExecute(Sender: TObject);
var
  frm: TfrmSettings;
begin
  frm := TfrmSettings.Create(Self);
  try
    frm.ShowModal;
  finally
    frm.Free;
  end;
end;

procedure TfrmMain.actUserAdminExecute(Sender: TObject);
begin
  // open user admin
end;

procedure TfrmMain.actAboutExecute(Sender: TObject);
begin
  ShowMessage(APP_TITLE + ' v' + APP_VERSION);
end;

// ────────────────────────────────────────────────────────────────────
// Helpers
// ────────────────────────────────────────────────────────────────────

procedure TfrmMain.SetStatusMessage(const AMsg: string);
begin
  FStatusMessage := AMsg;
  StatusBar1.Panels[0].Text := AMsg;
end;

procedure TfrmMain.ShowStatusMsg(const AMsg: string; ATimeoutMs: Integer);
begin
  SetStatusMessage(AMsg);
end;

procedure TfrmMain.SetModified(AValue: Boolean);
begin
  FModified := AValue;
  UpdateActionStates;
end;

function TfrmMain.ConfirmDiscard: Boolean;
begin
  if FModified then
    Result := MessageDlg('Unsaved changes will be lost. Continue?',
      mtConfirmation, [mbYes, mbNo], 0) = mrYes
  else
    Result := True;
end;

procedure TfrmMain.UpdateActionStates;
begin
  actSave.Enabled := FModified;
  actPrint.Enabled := FCurrentModule <> '';
end;

end.
