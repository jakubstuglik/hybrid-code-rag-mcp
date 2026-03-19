unit BaseEditorForm;

interface

uses
  SysUtils, Classes, Windows, Messages,
  Forms, Controls, StdCtrls, ExtCtrls,
  Buttons, ActnList, DBClient, DB,
  MainDataMod, AppConst;

type
  TfrmBaseEditor = class(TForm)
    // ── Standard button panel ─────────────────────────────────────────
    pnlButtons: TPanel;
    btnOK: TBitBtn;
    btnCancel: TBitBtn;
    btnApply: TBitBtn;
    btnHelp: TBitBtn;

    // ── Main content panel ────────────────────────────────────────────
    pnlMain: TPanel;

    // ── Action list ───────────────────────────────────────────────────
    ActionList1: TActionList;
    actSave: TAction;
    actClose: TAction;
    actNew: TAction;
    actDelete: TAction;
    actRefresh: TAction;

    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);
    procedure btnOKClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure btnApplyClick(Sender: TObject);
    procedure actSaveExecute(Sender: TObject);
    procedure actCloseExecute(Sender: TObject);
    procedure actDeleteExecute(Sender: TObject);
    procedure actRefreshExecute(Sender: TObject);

  private
    FModified: Boolean;
    FIsNew: Boolean;
    FRecordId: Integer;
    FCanDelete: Boolean;
    FCanSave: Boolean;

    procedure SetModified(AValue: Boolean);
    procedure UpdateButtonStates;

  protected
    // Override in subclasses
    procedure DoLoad; virtual; abstract;
    procedure DoSave; virtual; abstract;
    procedure DoDelete; virtual; abstract;
    procedure DoNew; virtual; abstract;
    procedure DoValidate; virtual;
    procedure DoAfterSave; virtual;
    procedure DoAfterDelete; virtual;
    function GetTitle: string; virtual;

  public
    procedure LoadRecord(ARecordId: Integer);
    procedure NewRecord;
    function Save: Boolean;
    function Delete: Boolean;
    function ConfirmDiscard: Boolean;

    property Modified: Boolean read FModified write SetModified;
    property IsNew: Boolean read FIsNew;
    property RecordId: Integer read FRecordId;
    property CanDelete: Boolean read FCanDelete write FCanDelete;
    property CanSave: Boolean read FCanSave write FCanSave;
  end;

implementation

{$R *.dfm}

procedure TfrmBaseEditor.FormCreate(Sender: TObject);
begin
  FModified := False;
  FIsNew := False;
  FRecordId := 0;
  FCanDelete := True;
  FCanSave := True;
  UpdateButtonStates;
end;

procedure TfrmBaseEditor.FormDestroy(Sender: TObject);
begin
  // nothing
end;

procedure TfrmBaseEditor.FormShow(Sender: TObject);
begin
  Caption := GetTitle;
  UpdateButtonStates;
end;

procedure TfrmBaseEditor.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
begin
  CanClose := not FModified or ConfirmDiscard;
end;

procedure TfrmBaseEditor.LoadRecord(ARecordId: Integer);
begin
  FRecordId := ARecordId;
  FIsNew := (ARecordId = 0);
  DoLoad;
  FModified := False;
  UpdateButtonStates;
end;

procedure TfrmBaseEditor.NewRecord;
begin
  FRecordId := 0;
  FIsNew := True;
  DoNew;
  FModified := False;
  UpdateButtonStates;
end;

function TfrmBaseEditor.Save: Boolean;
begin
  Result := False;
  try
    DoValidate;
    DoSave;
    FModified := False;
    FIsNew := False;
    DoAfterSave;
    Result := True;
    UpdateButtonStates;
  except
    on E: Exception do
      ShowMessage('Save failed: ' + E.Message);
  end;
end;

function TfrmBaseEditor.Delete: Boolean;
begin
  Result := False;
  if MessageDlg('Delete this record?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
  begin
    try
      DoDelete;
      DoAfterDelete;
      Result := True;
    except
      on E: Exception do
        ShowMessage('Delete failed: ' + E.Message);
    end;
  end;
end;

function TfrmBaseEditor.ConfirmDiscard: Boolean;
begin
  if FModified then
    Result := MessageDlg('Unsaved changes will be lost. Continue?',
      mtConfirmation, [mbYes, mbNo], 0) = mrYes
  else
    Result := True;
end;

procedure TfrmBaseEditor.SetModified(AValue: Boolean);
begin
  FModified := AValue;
  UpdateButtonStates;
end;

procedure TfrmBaseEditor.UpdateButtonStates;
begin
  btnOK.Enabled := FCanSave;
  btnApply.Enabled := FCanSave and FModified;
  actDelete.Enabled := FCanDelete and not FIsNew;
  actSave.Enabled := FCanSave;
end;

procedure TfrmBaseEditor.DoValidate;
begin
  // Default: no validation. Override to add validation rules.
end;

procedure TfrmBaseEditor.DoAfterSave;
begin
  // Default: nothing. Override for post-save actions.
end;

procedure TfrmBaseEditor.DoAfterDelete;
begin
  // Default: nothing. Override for post-delete actions.
end;

function TfrmBaseEditor.GetTitle: string;
begin
  if FIsNew then
    Result := 'New Record'
  else
    Result := 'Edit Record #' + IntToStr(FRecordId);
end;

procedure TfrmBaseEditor.btnOKClick(Sender: TObject);
begin
  if Save then
    ModalResult := mrOK;
end;

procedure TfrmBaseEditor.btnCancelClick(Sender: TObject);
begin
  ModalResult := mrCancel;
end;

procedure TfrmBaseEditor.btnApplyClick(Sender: TObject);
begin
  Save;
end;

procedure TfrmBaseEditor.actSaveExecute(Sender: TObject);
begin
  Save;
end;

procedure TfrmBaseEditor.actCloseExecute(Sender: TObject);
begin
  Close;
end;

procedure TfrmBaseEditor.actDeleteExecute(Sender: TObject);
begin
  if Delete then
    ModalResult := mrOK;
end;

procedure TfrmBaseEditor.actRefreshExecute(Sender: TObject);
begin
  if ConfirmDiscard then
    LoadRecord(FRecordId);
end;

end.
