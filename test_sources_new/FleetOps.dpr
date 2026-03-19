program FleetOps;

uses
  Forms,
  MainForm in 'MainForm.pas' {frmMain},
  MainDataMod in 'MainDataMod.pas' {dmFleet: TDataModule},
  SplashForm in 'SplashForm.pas' {frmSplash},
  LoginForm in 'LoginForm.pas' {frmLogin},
  BaseEditorForm in 'BaseEditorForm.pas' {frmBaseEditor},
  BasicMainForm in 'BasicMainForm.pas' {frmBasicMain},
  VehicleData.classes in 'VehicleData.classes.pas',
  JobReports.Classes in 'JobReports.Classes.pas',
  AppConst in 'AppConst.pas',
  JobHistoryThread in 'JobHistoryThread.pas',
  WizardBaseFrame in 'WizardBaseFrame.pas' {TWizardBaseFrame: TFrame},
  ReportScheduler in 'ReportScheduler.pas',
  FileUtils in 'FileUtils.pas',
  DeviceLicence in 'DeviceLicence.pas',
  WebApiService in 'WebApiService.pas',
  JobWizardStep1 in 'JobWizardStep1.pas' {frameJobWizardStep1: TFrame},
  CoordEditorFrame in 'CoordEditorFrame.pas' {frameCoordEditor: TFrame},
  SFTPConnFrame in 'SFTPConnFrame.pas' {frameSFTPConn: TFrame};

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskBar := True;
  Application.Title := 'FleetOps';
  Application.CreateForm(TdmFleet, dmFleet);
  Application.CreateForm(TfrmMain, frmMain);
  Application.Run;
end.
