unit SplashForm;

interface

uses
  SysUtils, Classes, Windows, Messages,
  Forms, Controls, StdCtrls, ExtCtrls,
  Graphics, AppConst;

type
  TfrmSplash = class(TForm)
    imgLogo: TImage;
    lblAppTitle: TLabel;
    lblVersion: TLabel;
    lblCopyright: TLabel;
    lblStatus: TLabel;
    pnlBottom: TPanel;
    ProgressBar1: TProgressBar;
    Timer1: TTimer;

    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure Timer1Timer(Sender: TObject);

  private
    FProgress: Integer;
    FStatusText: string;
    FCloseAfterMs: Integer;

    procedure UpdateProgress(APercent: Integer; const AMsg: string);

  public
    procedure SetStatus(const AMsg: string);
    procedure AdvanceProgress(AStep: Integer = 10);
    procedure Close;

    class procedure ShowSplash;
    class procedure HideSplash;
  end;

var
  frmSplash: TfrmSplash;

implementation

{$R *.dfm}

procedure TfrmSplash.FormCreate(Sender: TObject);
begin
  FProgress := 0;
  FCloseAfterMs := 3000;
  lblAppTitle.Caption := APP_TITLE;
  lblVersion.Caption := 'Version ' + APP_VERSION;
  lblCopyright.Caption := APP_COPYRIGHT;
  ProgressBar1.Min := 0;
  ProgressBar1.Max := 100;
  ProgressBar1.Position := 0;
end;

procedure TfrmSplash.FormDestroy(Sender: TObject);
begin
  // nothing
end;

procedure TfrmSplash.FormShow(Sender: TObject);
begin
  UpdateProgress(0, 'Initialising...');
end;

procedure TfrmSplash.Timer1Timer(Sender: TObject);
begin
  Timer1.Enabled := False;
  Close;
end;

procedure TfrmSplash.UpdateProgress(APercent: Integer; const AMsg: string);
begin
  FProgress := APercent;
  FStatusText := AMsg;
  ProgressBar1.Position := APercent;
  lblStatus.Caption := AMsg;
  Application.ProcessMessages;
end;

procedure TfrmSplash.SetStatus(const AMsg: string);
begin
  UpdateProgress(FProgress, AMsg);
end;

procedure TfrmSplash.AdvanceProgress(AStep: Integer);
begin
  UpdateProgress(Min(FProgress + AStep, 100), FStatusText);
end;

class procedure TfrmSplash.ShowSplash;
begin
  frmSplash := TfrmSplash.Create(nil);
  frmSplash.Show;
  Application.ProcessMessages;
end;

class procedure TfrmSplash.HideSplash;
begin
  if Assigned(frmSplash) then
  begin
    frmSplash.Close;
    FreeAndNil(frmSplash);
  end;
end;

end.
