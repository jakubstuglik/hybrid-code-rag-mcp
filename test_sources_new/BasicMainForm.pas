unit BasicMainForm;

interface

uses
  SysUtils, Classes, Windows, Messages,
  Forms, Controls, StdCtrls, ExtCtrls,
  ComCtrls, Menus, ActnList, AppConst,
  MainDataMod;

type
  TBasicMainForm = class(TForm)
    // ── Layout panels ─────────────────────────────────────────────────
    pnlTop: TPanel;
    pnlClient: TPanel;
    pnlStatusArea: TPanel;
    Splitter1: TSplitter;

    // ── Status bar ────────────────────────────────────────────────────
    StatusBar1: TStatusBar;

    // ── Timer for status reset ─────────────────────────────────────────
    tmrStatus: TTimer;

    // ── Main action list ──────────────────────────────────────────────
    ActionList1: TActionList;
    actClose: TAction;
    actRefresh: TAction;
    actExport: TAction;
    actPrint: TAction;
    actHelp: TAction;

    // ── Context menu ──────────────────────────────────────────────────
    PopupMenu1: TPopupMenu;
    mnuRefresh: TMenuItem;
    mnuExport: TMenuItem;
    mnuSep1: TMenuItem;
    mnuClose: TMenuItem;

    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure FormKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure tmrStatusTimer(Sender: TObject);
    procedure actCloseExecute(Sender: TObject);
    procedure actRefreshExecute(Sender: TObject);
    procedure actExportExecute(Sender: TObject);
    procedure actPrintExecute(Sender: TObject);
    procedure actHelpExecute(Sender: TObject);

  private
    FTitle: string;
    FDirty: Boolean;
    FStatusTimeout: Integer;

    procedure SetTitle(const AValue: string);
    procedure ClearStatus;

  protected
    procedure DoRefresh; virtual;
    procedure DoExport; virtual;
    procedure DoPrint; virtual;
    procedure DoHelp; virtual;
    function GetHelpContext: Integer; virtual;

  public
    procedure ShowInfo(const AMsg: string; ATimeout: Integer = 4000);
    procedure ShowError(const AMsg: string);
    procedure MarkDirty;
    procedure MarkClean;

    property Title: string read FTitle write SetTitle;
    property Dirty: Boolean read FDirty;
  end;

implementation

{$R *.dfm}

procedure TBasicMainForm.FormCreate(Sender: TObject);
begin
  FDirty := False;
  FStatusTimeout := 4000;
  FTitle := APP_TITLE;
  Caption := FTitle;
  StatusBar1.Panels[0].Text := 'Ready';
  tmrStatus.Interval := 1000;
  tmrStatus.Enabled := False;
end;

procedure TBasicMainForm.FormDestroy(Sender: TObject);
begin
  tmrStatus.Enabled := False;
end;

procedure TBasicMainForm.FormShow(Sender: TObject);
begin
  DoRefresh;
end;

procedure TBasicMainForm.FormKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  case Key of
    VK_F5: actRefresh.Execute;
    VK_F1: actHelp.Execute;
    VK_ESCAPE: Close;
  end;
end;

procedure TBasicMainForm.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caHide;
end;

procedure TBasicMainForm.tmrStatusTimer(Sender: TObject);
begin
  ClearStatus;
  tmrStatus.Enabled := False;
end;

procedure TBasicMainForm.SetTitle(const AValue: string);
begin
  FTitle := AValue;
  Caption := AValue;
end;

procedure TBasicMainForm.ClearStatus;
begin
  StatusBar1.Panels[0].Text := 'Ready';
end;

procedure TBasicMainForm.ShowInfo(const AMsg: string; ATimeout: Integer);
begin
  StatusBar1.Panels[0].Text := AMsg;
  FStatusTimeout := ATimeout div 1000;
  tmrStatus.Enabled := True;
end;

procedure TBasicMainForm.ShowError(const AMsg: string);
begin
  StatusBar1.Panels[0].Text := '[ERROR] ' + AMsg;
  MessageDlg(AMsg, mtError, [mbOK], 0);
end;

procedure TBasicMainForm.MarkDirty;
begin
  FDirty := True;
  Caption := FTitle + ' *';
end;

procedure TBasicMainForm.MarkClean;
begin
  FDirty := False;
  Caption := FTitle;
end;

procedure TBasicMainForm.DoRefresh;
begin
  // Override in subclass
end;

procedure TBasicMainForm.DoExport;
begin
  // Override in subclass
end;

procedure TBasicMainForm.DoPrint;
begin
  // Override in subclass
end;

procedure TBasicMainForm.DoHelp;
begin
  Application.HelpContext(GetHelpContext);
end;

function TBasicMainForm.GetHelpContext: Integer;
begin
  Result := 0;
end;

procedure TBasicMainForm.actCloseExecute(Sender: TObject);
begin
  Close;
end;

procedure TBasicMainForm.actRefreshExecute(Sender: TObject);
begin
  DoRefresh;
  ShowInfo('Refreshed');
end;

procedure TBasicMainForm.actExportExecute(Sender: TObject);
begin
  DoExport;
end;

procedure TBasicMainForm.actPrintExecute(Sender: TObject);
begin
  DoPrint;
end;

procedure TBasicMainForm.actHelpExecute(Sender: TObject);
begin
  DoHelp;
end;

end.
