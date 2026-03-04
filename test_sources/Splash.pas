unit Splash;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, ComCtrls, StdCtrls, Vcl.Imaging.jpeg, JvExControls,
  JvLabel, JvExStdCtrls, JvBehaviorLabel;

type
  TfrmSplash = class(TForm)
    ProgressBar1: TProgressBar;
    lVersion: TLabel;
    Image1: TImage;
    Label1: TLabel;
    Timer1: TTimer;
    lInformicaNameAddress: TLabel;
    lInformicaEmailWWWTel: TLabel;
    procedure FormShow(Sender: TObject);
    procedure Timer1Timer(Sender: TObject);
  private
    function GetInfoText: string;
    procedure SetInfoText(const Value: string);
    { Private declarations }
  public
    { Public declarations }
    property InfoText: string read GetInfoText write SetInfoText;
  end;

var
  frmSplash: TfrmSplash;

implementation

uses ProductVersionUtil;

{$R *.dfm}

procedure TfrmSplash.FormShow(Sender: TObject);
begin
  lVersion.Caption := 'wersja '+ProductVersion;
  lInformicaNameAddress.Caption := InformicaNameAddress;
  lInformicaEmailWWWTel.Caption := InformicaEmailWWWTel;
  Application.ProcessMessages;
end;

function TfrmSplash.GetInfoText: string;
begin
  Result := Label1.Caption;
end;

procedure TfrmSplash.SetInfoText(const Value: string);
begin
  Label1.Caption := Value;
  Application.ProcessMessages;
end;

procedure TfrmSplash.Timer1Timer(Sender: TObject);
begin
  ProgressBar1.Repaint;
  Label1.Repaint;
  Application.ProcessMessages;
end;

end.
