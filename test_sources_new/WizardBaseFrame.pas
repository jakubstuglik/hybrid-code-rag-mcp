unit WizardBaseFrame;

interface

uses
  SysUtils, Classes, Windows, Messages,
  Forms, Controls, StdCtrls, ExtCtrls,
  Buttons, ActnList, AppConst;

type
  TWizardBaseFrame = class(TFrame)
    // ── Navigation buttons ────────────────────────────────────────────
    pnlNav: TPanel;
    btnBack: TBitBtn;
    btnNext: TBitBtn;
    btnFinish: TBitBtn;
    btnCancel: TBitBtn;

    // ── Content panel ─────────────────────────────────────────────────
    pnlContent: TPanel;

    // ── Step indicator ────────────────────────────────────────────────
    pnlSteps: TPanel;
    lblStepTitle: TLabel;
    lblStepDesc: TLabel;
    lblStepProgress: TLabel;

    // ── Action list ───────────────────────────────────────────────────
    ActionList1: TActionList;
    actBack: TAction;
    actNext: TAction;
    actFinish: TAction;
    actCancel: TAction;

    procedure FormCreate(Sender: TObject);
    procedure btnBackClick(Sender: TObject);
    procedure btnNextClick(Sender: TObject);
    procedure btnFinishClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure actBackExecute(Sender: TObject);
    procedure actNextExecute(Sender: TObject);
    procedure actFinishExecute(Sender: TObject);
    procedure actCancelExecute(Sender: TObject);

  private
    FCurrentStep: Integer;
    FTotalSteps: Integer;
    FCompleted: Boolean;
    FCancelled: Boolean;

    procedure UpdateStepLabel;
    procedure UpdateButtonStates;
    procedure GoToStep(AStep: Integer);

  protected
    // Override to define wizard behaviour
    function GetStepTitle(AStep: Integer): string; virtual; abstract;
    function GetStepDescription(AStep: Integer): string; virtual; abstract;
    function GetStepCount: Integer; virtual; abstract;
    function CanGoForward: Boolean; virtual;
    function CanGoBack: Boolean; virtual;
    procedure OnEnterStep(AStep: Integer); virtual;
    procedure OnLeaveStep(AStep: Integer); virtual;
    procedure OnFinish; virtual; abstract;
    procedure OnCancel; virtual;
    function ValidateStep(AStep: Integer): Boolean; virtual;

  public
    procedure StartWizard;
    procedure ResetWizard;

    property CurrentStep: Integer read FCurrentStep;
    property TotalSteps: Integer read FTotalSteps;
    property Completed: Boolean read FCompleted;
    property Cancelled: Boolean read FCancelled;
  end;

implementation

{$R *.dfm}

procedure TWizardBaseFrame.FormCreate(Sender: TObject);
begin
  FCurrentStep := 0;
  FTotalSteps := GetStepCount;
  FCompleted := False;
  FCancelled := False;
  UpdateButtonStates;
end;

procedure TWizardBaseFrame.StartWizard;
begin
  FCurrentStep := 1;
  FTotalSteps := GetStepCount;
  FCompleted := False;
  FCancelled := False;
  GoToStep(1);
end;

procedure TWizardBaseFrame.ResetWizard;
begin
  FCurrentStep := 0;
  FCompleted := False;
  FCancelled := False;
  UpdateButtonStates;
end;

procedure TWizardBaseFrame.GoToStep(AStep: Integer);
begin
  if FCurrentStep > 0 then
    OnLeaveStep(FCurrentStep);
  FCurrentStep := AStep;
  UpdateStepLabel;
  UpdateButtonStates;
  OnEnterStep(AStep);
end;

procedure TWizardBaseFrame.UpdateStepLabel;
begin
  lblStepTitle.Caption := GetStepTitle(FCurrentStep);
  lblStepDesc.Caption := GetStepDescription(FCurrentStep);
  lblStepProgress.Caption := Format('Step %d of %d',
    [FCurrentStep, FTotalSteps]);
end;

procedure TWizardBaseFrame.UpdateButtonStates;
begin
  btnBack.Enabled := CanGoBack;
  btnNext.Enabled := CanGoForward and (FCurrentStep < FTotalSteps);
  btnFinish.Enabled := CanGoForward and (FCurrentStep = FTotalSteps);
  btnCancel.Enabled := not FCompleted;
end;

function TWizardBaseFrame.CanGoForward: Boolean;
begin
  Result := True;
end;

function TWizardBaseFrame.CanGoBack: Boolean;
begin
  Result := FCurrentStep > 1;
end;

function TWizardBaseFrame.ValidateStep(AStep: Integer): Boolean;
begin
  Result := True;
end;

procedure TWizardBaseFrame.OnEnterStep(AStep: Integer);
begin
  // Default: nothing
end;

procedure TWizardBaseFrame.OnLeaveStep(AStep: Integer);
begin
  // Default: nothing
end;

procedure TWizardBaseFrame.OnCancel;
begin
  FCancelled := True;
end;

procedure TWizardBaseFrame.btnBackClick(Sender: TObject);
begin
  actBack.Execute;
end;

procedure TWizardBaseFrame.btnNextClick(Sender: TObject);
begin
  actNext.Execute;
end;

procedure TWizardBaseFrame.btnFinishClick(Sender: TObject);
begin
  actFinish.Execute;
end;

procedure TWizardBaseFrame.btnCancelClick(Sender: TObject);
begin
  actCancel.Execute;
end;

procedure TWizardBaseFrame.actBackExecute(Sender: TObject);
begin
  if CanGoBack then
    GoToStep(FCurrentStep - 1);
end;

procedure TWizardBaseFrame.actNextExecute(Sender: TObject);
begin
  if ValidateStep(FCurrentStep) and CanGoForward then
    GoToStep(FCurrentStep + 1);
end;

procedure TWizardBaseFrame.actFinishExecute(Sender: TObject);
begin
  if ValidateStep(FCurrentStep) and CanGoForward then
  begin
    OnFinish;
    FCompleted := True;
    UpdateButtonStates;
  end;
end;

procedure TWizardBaseFrame.actCancelExecute(Sender: TObject);
begin
  if MessageDlg('Cancel this wizard?', mtConfirmation, [mbYes, mbNo], 0) = mrYes then
    OnCancel;
end;

end.
