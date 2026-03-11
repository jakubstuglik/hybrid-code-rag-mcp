unit DataSnapSchedule;

interface

uses
  DBClient, MainDM, SysUtils, Classes, FileAttachmentClasses, FileAttachmentManager,
  SchedulerResultClasses
  , Data.DB
  , Windows;

const
  TASK_SUNDAY = 1;
  TASK_MONDAY = 2;
  TASK_TUESDAY = 4;
  TASK_WEDNESDAY = 8;
  TASK_THURSDAY = 16;
  TASK_FRIDAY = 32;
  TASK_SATURDAY = 64;

  REPORT_FORMAT_CSV = 0;
  REPORT_FORMAT_XML = 1;

  XML_ENCODING = 'UTF-8';
  XML_VERSION = '1.0';

type
  TDataSnapSchedule = class
  private
    FDM : TdmMain;
    FSQLProcParameters : TStringList;
    FReportName : string;
    FReportColumns : string;
    FError : string;
//    fFileFolder: string;

    procedure RunReport(AReportId, AReportFormat : integer; ASQLProcName: String;
      AParams : string; var AFileName : string; ANetworkPath, ANetworkUser, ANetworkPassword,
      AReportName, AReportColumns : string; ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean);
    procedure RunStoredProc(ASQLProcName: String; AParams : string);
    procedure RunAnalizaGPS(AParams : string);
    procedure RunDownloadDataForOnLineTracking(AParams : string);
    procedure RunDownloadChangedDataForOnLineTracking(AParams : string);
    procedure RunUpdateDataWarehouse(AParams, ACompanyCode : string);

    procedure RunWWWMastercode(aReferenceId: integer; ASQLProcName: String; aCompanyCode: string);

    procedure SaveAsCSV(myFileName: string; AColumnsInfo : TStringList; ADataSet: TClientDataSet);
    procedure SaveAsXML(myFileName: string; AColumnsInfo : TStringList; ADataSet: TClientDataSet);
    procedure CopyToNetworkPath(ANetworkFileName, AFileName, ANetworkPath, ANetworkUser, ANetworkPassword : string);

    function GetReportColumns : TStringList;

    function GetCSVFileName(ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean) : string;
    function GetXMLFileName(ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean) : string;

    procedure AddAttachment(AReferenceId : Integer; AFileName : string);
    function AddSchedulerResult(AScheduleId : Integer; AStartDate : TDateTime) : integer;
    procedure UpdateSchedulerResult(ASchedulerResultId : Integer; AEndDate : TDateTime);

  public
//    property FileFolder: string read fFileFolder write fFileFolder;

    constructor Create(ADataModule : TdmMain);
    destructor Destroy; override;
    procedure Run(ADataSnapStart : Boolean; ARunOnce: integer; ACompanyCode: string);
  end;

implementation

uses
  DateUtils, KMUtils, KMWinSysUtils, XMLLPC_ReportTemplate, XMLDoc, XMLIntf,
  ShellAPI, RemoteData, JSONSimpleObject, superobject, BusStop
  , StrUtilsEx, System.Types, System.IOUtils, DataWareHouseUploadClass
//  , EmCardSaleOnBus.Classes
  ;

{ TDataSnapSchedule }

procedure TDataSnapSchedule.AddAttachment(AReferenceId : Integer; AFileName : string);
var
  FileAttachment : TFileAttachment;
  Owner : TSchedulerResult;
begin
  Owner := TSchedulerResult.Create;
  Owner.Id := AReferenceId;

  FileAttachment := TFileAttachment.Create(Owner);

  try
    FileAttachment.dmMain := FDM;
    FileAttachment.RefType := 99;
    FileAttachment.Name := AFileName;
    FileAttachment.WriteToDatabase;
  finally
    FileAttachment.Free;
    Owner.Free;
  end;
end;

function TDataSnapSchedule.AddSchedulerResult(AScheduleId : Integer; AStartDate : TDateTime) : integer;
var
//  Params : String;
  SchedulerResult : TSchedulerResult;
begin
  //Result := 0;
  SchedulerResult := TSchedulerResult.Create;

  try
    SchedulerResult.dmMain := FDM;

    SchedulerResult.Scheduler.Id := AScheduleId;
    SchedulerResult.StartDate := AStartDate;

    SchedulerResult.WriteToDatabase;

    Result := SchedulerResult.Id;
  finally
    SchedulerResult.Free;
  end;
end;

procedure TDataSnapSchedule.CopyToNetworkPath(ANetworkFileName, AFileName, ANetworkPath, ANetworkUser, ANetworkPassword : string);
var
  dest : string;
  conn : integer;
  networkPath : boolean;
begin
  if (AFileName <> EmptyStr) and (ANetworkPath <> EmptyStr) then
  begin
    networkPath := True;
    if (ANetworkUser <> EmptyStr) and (ANetworkPassword <> EmptyStr) and
       (Pos('\\', ANetworkPath) = 1) then
      conn := ConnectShare('', ANetworkPath, ANetworkUser, ANetworkPassword)
    else
    begin
      networkPath := false;
      conn := NO_ERROR;
      if not DirectoryExists(ANetworkPath) then
        conn := ERROR_PATH_NOT_FOUND;
    end;

     if FileExists(AFileName) and (conn = NO_ERROR) then
    begin
      dest := IncludeTrailingPathDelimiter(ANetworkPath) + ExtractFileName(ANetworkFileName);
      CopyFile(PChar(AFileName), PChar(dest), False);

      if networkPath then
        DisconnectShare(ANetworkPath);
    end
    else
      FError := ErrorMessage(conn);
  end;
end;

constructor TDataSnapSchedule.Create(ADataModule: TdmMain);
begin
  FDM := ADataModule;
  FSQLProcParameters := TStringList.Create;
end;

destructor TDataSnapSchedule.Destroy;
begin
  FSQLProcParameters.Free;
  inherited;
end;

function TDataSnapSchedule.GetCSVFileName(ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean): string;
begin
  /// plik jest tworzony w folderze ScheduleResult
  if not DirectoryExists(AppDir + 'ScheduleResult') then
    ForceDirectories(AppDir + 'ScheduleResult');

  if ANetworkFileName <> EmptyStr then
  begin
    Result := AppDir + 'ScheduleResult\' + ANetworkFileName;

    if ANetworkFileNameWithDateTime then
      Result := Result   + '_' + FormatDateTime('yyyymmdd_hhMMss', now) + '.csv'
    else
      Result := Result + '.csv';
  end
  else
    Result := AppDir + 'ScheduleResult\' + FReportName + '_' + FormatDateTime('yyyymmdd_hhMMss', now) + '.csv';
end;

function TDataSnapSchedule.GetReportColumns: TStringList;
begin
  Result := TStringList.Create;
  if FReportColumns <> EmptyStr then
  begin
    Result.NameValueSeparator := '=';
    Result.Text := FReportColumns;
  end
  else
  begin
    FreeAndNil(Result);
  end;
end;

function TDataSnapSchedule.GetXMLFileName(ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean): string;
begin
  /// plik jest tworzony w folderze ScheduleResult
  if not DirectoryExists(AppDir + 'ScheduleResult') then
    ForceDirectories(AppDir + 'ScheduleResult');

  if ANetworkFileName <> EmptyStr then
  begin
    Result := AppDir + 'ScheduleResult\' + ANetworkFileName;

    if ANetworkFileNameWithDateTime then
      Result := Result   + '_' + FormatDateTime('yyyymmdd_hhMMss', now) + '.xml'
    else
      Result := Result + '.xml';
  end
  else
    Result := AppDir + 'ScheduleResult\' + FReportName + '_' + FormatDateTime('yyyymmdd_hhMMss', now) + '.xml';
end;

procedure TDataSnapSchedule.Run(ADataSnapStart : Boolean; ARunOnce: integer; ACompanyCode: string);
var
  Tasks : TClientDataSet;
  Day : integer;
  Params : string;
  StartTime : TDateTime;
  EndTime : TDateTime;
  ReferenceId : integer;
  FileName : string;
  taskT, taskID: integer;
//  aFiles: TStringDynArray;
//  fFile: string;
begin
  {$IF Defined(DEBUG) and Defined(SQLPROFILER)}
  //Exit;
  {$IFEND}
  Tasks := FDM.dsStoredProc_LPC_Scheduler_SelectForDate;

  Day := 0;
  case DayOfTheWeek(now) of
    1 : Day := TASK_MONDAY;
    2 : Day := TASK_TUESDAY;
    3 : Day := TASK_WEDNESDAY;
    4 : Day := TASK_THURSDAY;
    5 : Day := TASK_FRIDAY;
    6 : Day := TASK_SATURDAY;
    7 : Day := TASK_SUNDAY;
  end;
  /// pobranie zadañ do wykonania
  Params := Format('@Day=%d'#13#10 +
                   '@DataSnapRun=%d'#13#10 +
                   '@CurrentDateTime=%s'#13#10 +
                   '@RunOnce=%d',
                   [Day,
                    Integer(iif(ADataSnapStart, 1, 0)),
                    FormatDateTime('yyyy-mm-dd hh:MM:ss', Now)
                    , ARunOnce]);


  Tasks.Close;
  FDM.StoredProcOpen(Tasks, Params);

  //TESTBTR RunUpdateDataWarehouse
  {$IFDEF DEBUG}
  //RunUpdateDataWarehouse(
  //            Tasks.FieldByName('Params').AsString, aCompanyCode);
  //exit;  //TESTBTR
  {$ENDIF}
  //

  /// iteracja po zadaniach
  while not Tasks.Eof do
  begin
//    FDM.Log(Params);
    taskT := Tasks.FieldByName('Type').AsInteger;
    taskID := Tasks.FieldByName('ID').AsInteger;
    try

      if taskT = 8 then // ten typ zadania generuje codzienne pliki w us³udze iAutServer; w tym miejscu powinien byæ omijany
      begin
        Tasks.Next;
        Continue;
      end;

      StartTime := now;
      ReferenceId := AddSchedulerResult(Tasks.FieldByName('ID').AsInteger, StartTime);

      case taskT of
        1 : RunReport(
              Tasks.FieldByName('Report_ID').AsInteger,
              Tasks.FieldByName('ReportFormat').AsInteger,
              Tasks.FieldByName('SQLProcName').AsString,
              Tasks.FieldByName('Params').AsString,
              FileName,
              Tasks.FieldByName('NetworkPath').AsString,
              Tasks.FieldByName('NetworkUser').AsString,
              Tasks.FieldByName('NetworkPassword').AsString,
              Tasks.FieldByName('ReportName').AsString,
              Tasks.FieldByName('ReportColumns').AsString,
              Tasks.FieldByName('NetworkFileName').AsString,
              Tasks.FieldByName('NetworkFileNameWithDateTime').AsBoolean);
        2 : RunStoredProc(
              Tasks.FieldByName('SQLProcName').AsString,
              Tasks.FieldByName('Params').AsString);
        3 : RunAnalizaGPS(
              Tasks.FieldByName('Params').AsString);
        4 : RunWWWMastercode(
              ReferenceId,
              Tasks.FieldByName('SQLProcName').AsString,
              aCompanyCode
            );
        5 : RunDownloadDataForOnLineTracking(
              Tasks.FieldByName('Params').AsString);
        6 : RunDownloadChangedDataForOnLineTracking(
              Tasks.FieldByName('Params').AsString);
        7 : RunUpdateDataWarehouse(
              Tasks.FieldByName('Params').AsString, aCompanyCode);
        8 : ; // ten typ zadania jest zarezerwowany, generuje codzienne pliki w us³udze iAutServer; w tym miejscu powinien byæ omijany
      end;

      EndTime := now;
      UpdateSchedulerResult(ReferenceId, EndTime);

      if taskT = 1 then begin
        if FileExists(FileName) then
          AddAttachment(ReferenceId, FileName);
      end;

//      if ARunOnce = 0 then begin
//        //rejestracja plikow pp i pz
//        //
//        if DirectoryExists(fFileFolder) then begin
//          aFiles := TDirectory.GetFiles(fFileFolder, 'PA*.*',
//                         TSearchOption.soAllDirectories);
//
//          for fFile in aFiles do begin
//            if ReadPAFile(fFile) then
//              DeleteFile(fFile);
//
//          end;
//        end;
//      end;

    except
      on e: Exception do
      begin
        FDM.Log('TDataSnapSchedule.Run',
          'Parametry: ' + Params
            + '; taskT: ' + IntToStr(taskT)
            + '; task.Id: ' + IntToStr(taskID)
            + '; B³¹d: ' + e.Message,
          0, True);
        raise ;
      end;
    end;
    Tasks.Next;
  end;
  Tasks.Close;
end;

procedure TDataSnapSchedule.RunAnalizaGPS(AParams: string);
var
  tmpStartupInfo: TStartupInfo;
  tmpProcessInformation: TProcessInformation;
  input : String;
begin
  FError := '';

  input := GetEnvironmentVariable('COMSPEC') + ' /C AnalizaPKSGrodzisk.exe /Command AnalyzeRJA /RunSilent 1';
  FillChar(tmpStartupInfo, SizeOf(tmpStartupInfo), 0);
  with tmpStartupInfo do
  begin
    cb := SizeOf(TStartupInfo);
    wShowWindow := SW_HIDE;
  end;

  if CreateProcess(nil, PChar(input), nil, nil, true, CREATE_NO_WINDOW,
    nil, PChar(ExtractFilePath(ApplicationExeName)), tmpStartupInfo, tmpProcessInformation) then
  begin
    // loop every 10 ms
    while WaitForSingleObject(tmpProcessInformation.hProcess, 10) > 0 do
    begin
      //Application.ProcessMessages;
    end;
    CloseHandle(tmpProcessInformation.hProcess);
    CloseHandle(tmpProcessInformation.hThread);
  end
  else
  begin
    FError := FError + IntToStr(GetLastError);
    RaiseLastOSError;
  end;
end;

procedure TDataSnapSchedule.RunDownloadChangedDataForOnLineTracking(
  AParams: string);
var
  tmpStartupInfo: TStartupInfo;
  tmpProcessInformation: TProcessInformation;
  input : String;
begin
  FError := '';

  input := GetEnvironmentVariable('COMSPEC') + ' /C AnalizaPKSGrodzisk.exe /Command SynchronizeChangedDataForOnlineTracking /RunSilent 1';
  FillChar(tmpStartupInfo, SizeOf(tmpStartupInfo), 0);
  with tmpStartupInfo do
  begin
    cb := SizeOf(TStartupInfo);
    wShowWindow := SW_HIDE;
  end;

  if CreateProcess(nil, PChar(input), nil, nil, true, CREATE_NO_WINDOW,
    nil, PChar(ExtractFilePath(ApplicationExeName)), tmpStartupInfo, tmpProcessInformation) then
  begin
    // loop every 10 ms
    while WaitForSingleObject(tmpProcessInformation.hProcess, 10) > 0 do
    begin
      //Application.ProcessMessages;
    end;
    CloseHandle(tmpProcessInformation.hProcess);
    CloseHandle(tmpProcessInformation.hThread);
  end
  else
  begin
    FError := FError + IntToStr(GetLastError);
    RaiseLastOSError;
  end;
end;

procedure TDataSnapSchedule.RunDownloadDataForOnLineTracking(AParams: string);
var
  tmpStartupInfo: TStartupInfo;
  tmpProcessInformation: TProcessInformation;
  input : String;
begin
  FError := '';

  input := GetEnvironmentVariable('COMSPEC') + ' /C AnalizaPKSGrodzisk.exe /Command SynchronizeDataForOnlineTracking /RunSilent 1';
  FillChar(tmpStartupInfo, SizeOf(tmpStartupInfo), 0);
  with tmpStartupInfo do
  begin
    cb := SizeOf(TStartupInfo);
    wShowWindow := SW_HIDE;
  end;

  if CreateProcess(nil, PChar(input), nil, nil, true, CREATE_NO_WINDOW,
    nil, PChar(ExtractFilePath(ApplicationExeName)), tmpStartupInfo, tmpProcessInformation) then
  begin
    // loop every 10 ms
    while WaitForSingleObject(tmpProcessInformation.hProcess, 10) > 0 do
    begin
      //Application.ProcessMessages;
    end;
    CloseHandle(tmpProcessInformation.hProcess);
    CloseHandle(tmpProcessInformation.hThread);
  end
  else
  begin
    FError := FError + IntToStr(GetLastError);
    RaiseLastOSError;
  end;
end;

procedure TDataSnapSchedule.RunReport(AReportId, AReportFormat : integer; ASQLProcName: String;
  AParams : string; var AFileName : string; ANetworkPath, ANetworkUser, ANetworkPassword,
  AReportName, AReportColumns : string;  ANetworkFileName : string; ANetworkFileNameWithDateTime : boolean);
var
  ReportProc : TClientDataSet;
  FileName : String;
  NetworkFileName : String;
begin
  FError := '';
  AParams := FastStringReplace(AParams, '~~' , #$D, [rfReplaceAll]);
  FReportColumns := FastStringReplace(AReportColumns, '~~' , #$D, [rfReplaceAll]);
  FReportName := AReportName;
  FSQLProcParameters.Text := AParams;
  ReportProc := FDM.StoredProcOpen('dbo', ASQLProcName, FSQLProcParameters.Text);

  try
    try
      case AReportFormat of
        REPORT_FORMAT_CSV:
        begin
          FileName := GetCSVFileName('', false);
          NetworkFileName := GetCSVFileName(ANetworkFileName, ANetworkFileNameWithDateTime);
          SaveAsCSV(FileName, GetReportColumns, ReportProc);
        end;
        REPORT_FORMAT_XML:
        begin
          FileName := GetXMLFileName('', false);
          NetworkFileName := GetXMLFileName(ANetworkFileName, ANetworkFileNameWithDateTime);
          SaveAsXML(FileName, GetReportColumns, ReportProc);
        end;
      end;

      AFileName := FileName;

      CopyToNetworkPath(NetworkFileName, AFileName, ANetworkPath, ANetworkUser, ANetworkPassword);

      //if Assigned(ReportProc) then
      //  ReportProc.Close;
    finally
      ReportProc.Free;
    end;
  except
    on E : Exception do
      FError := FError + '; ' + E.Message;
  end;
end;

procedure TDataSnapSchedule.RunStoredProc(ASQLProcName,
  AParams: string);
//var
//  ReportProc : TClientDataSet;
begin
  AParams := FastStringReplace(AParams, '~~' , #$D, [rfReplaceAll]);
  FSQLProcParameters.Text := AParams;
  FDM.StoredProc('dbo', ASQLProcName, FSQLProcParameters.Text);
//  ReportProc := FDM.StoredProcOpen('dbo', ASQLProcName, FSQLProcParameters.Text);
//  try
//    ReportProc.Close;
//  finally
//    ReportProc.Free;
//  end;
end;

procedure TDataSnapSchedule.RunUpdateDataWarehouse(AParams, ACompanyCode: string);
begin
  with TDataWarehouseUpload.Create(FDM) do
  try
    UploadDataWarehouse(ACompanyCode);
  finally
    Free;
  end;
end;

procedure TDataSnapSchedule.RunWWWMastercode(aReferenceId: integer; ASQLProcName: String; aCompanyCode: string);
var
  cds : TClientDataSet;
  Scheduler_ID: integer;
  Scheduler_date: TDateTime;
  r: TdmRemoteData;
  s: string;
//  b: Boolean;
  d: TDatasetSimpleObj;
//  oldid, newid: integer;
  //bs: TBusStop;
//  result_id: integer;
begin
  Scheduler_ID := 0; Scheduler_date := 0; //result_id := 0;
  cds := FDM.StoredProcOpen('dbo', ASQLProcName, '');
  try
    try
      cds.First;
      Scheduler_ID := cds.FieldByName('Scheduler_ID').AsInteger;
      Scheduler_date := cds.FieldByName('StartDate').AsDateTime;
//      result_id :=  cds.FieldByName('ID').AsInteger;
    except
    end;
    //cds.Close;
  finally
    FreeAndNil(cds);
  end;
  if Scheduler_ID > 0 then begin
    r := TdmRemoteData.Create(nil);
    try
      s := r.MasterBusStopCodeChanges(Scheduler_date, aCompanyCode);
//      b := True;
      try
        d := TDatasetSimpleObj.FromJson(s);
        cds := TClientDataSet.Create(nil);
//        bs := TBusStop.Create;
        try
          d.ToClientDataSet(cds);
          cds.Open;
          cds.First;
          while not cds.Eof do begin
            if cds.FieldByName('OldKodWWW').AsLargeInt > 0 then
              TBusStop.WWWMasterCodeChange(cds.FieldByName('OldKodWWW').AsLargeInt,
                cds.FieldByName('NewKodWWW').AsLargeInt, FDM)
          else
              TBusStop.WWWMasterCodeSet(cds.FieldByName('BusStopCode').AsInteger, cds.FieldByName('CompanyCode').AsString,
                cds.FieldByName('NewKodWWW').AsLargeInt, FDM);

//            newid := TBusStop.IdFromWWWMasterCode(cds.FieldByName('NewKodWWW').AsInteger, FDM);
//            if newid = 0 then begin
//              oldid := TBusStop.IdFromWWWMasterCode(cds.FieldByName('OldKodWWW').AsInteger, FDM);
//              bs.Clear;
//              bs.dmMain := FDM;
//              if (oldid > 0) and bs.ReadFromDatabase(oldid) and (bs.Id > 0) then begin
//                bs.WWWMasterCode := cds.FieldByName('NewKodWWW').AsInteger;
//                b := bs.WriteToDatabase;
//                if not b then break;
//              end;
//            end;
            cds.Next;
          end;
        finally
          d.Free;
          cds.Free;
//          bs.Free;
        end;
      except
//        b := False;
      end;
//      if b and (result_id > 0) then
//        FDM.StoredProc('dbo', ASQLProcName + '_Done', '@id=' + IntToStr(result_id));
    finally
      r.Free;
    end;
  end;

end;

procedure TDataSnapSchedule.SaveAsCSV(myFileName: string; AColumnsInfo : TStringList; ADataSet: TClientDataSet);
var
  myTextFile: TextFile;
  i, rc: integer;
  s, s0: string;
  ColInfo : string;
//  ColName : string;
//  ColAlias : string;

  Columns : TStringList;

  procedure Replace13_i_10(var s: string);
  var Ai : Integer;
  begin
    for Ai := 1 to Length(s) do
    begin
      if s[Ai]=#13 then s[Ai]:=' ';
      if s[Ai]=#10 then s[Ai]:=' ';
    end;
  end;
begin
  if not Assigned(ADataSet) or not ADataSet.Active then exit;

  rc:=1;
  Columns := TStringList.Create;

  try
    ADataSet.DisableControls;
    ADataSet.First;

    //create a new file
    AssignFile(myTextFile, myFileName);
    Rewrite(myTextFile);

    s :='"Lp.";';
    try
      if Assigned(AColumnsInfo) then
      begin
        for i := 0 to AColumnsInfo.Count - 1 do
        begin
          ColInfo := AColumnsInfo[i];
          Columns.Add(Copy(ColInfo, 1, Pos('=', ColInfo) - 1));

          s := s + Format('"%s";', [Copy(ColInfo, Pos('=', ColInfo) + 1, Length(ColInfo))]);
        end;
      end
      else
      begin
        //write field names (as column headers)
        for i := 0 to ADataSet.FieldCount - 1 do
        begin
          s := s + Format('"%s";', [ADataSet.Fields[i].FieldName]);
          Columns.Add(ADataSet.Fields[i].FieldName);
        end;
      end;

      Writeln(myTextFile, s);
      //write field values

      while not ADataSet.Eof do
      begin
        s := Format('"%s";', [IntToStr(rc)]);

        for I := 0 to Columns.Count - 1 do
        begin
          begin
            s0:=ADataSet.FieldByName(Columns[i]).AsString;
            if (Length(s0)>0) and (Length(s0)<11) then
              s := s + Format('="%s";', [s0])
            else
              s := s + Format('"%s";', [s0]);
          end;
          Replace13_i_10(s);
        end;

        Writeln(myTextfile, s);
        ADataSet.Next;
        inc(rc);
      end;

    finally
      CloseFile(myTextFile);
    end;
  finally
    Columns.Free;
    AColumnsInfo.Free;
    ADataSet.EnableControls;
  end;
end;

procedure TDataSnapSchedule.SaveAsXML(myFileName: string;
  AColumnsInfo: TStringList; ADataSet: TClientDataSet);
var
  i : integer;
  s : string;
  ColInfo : string;
  DataSetColumns : TStringList;
  FXmlDoc : IXMLDocument;
  FXmlExport : IXMLReportType;
  sl : TStrings;
  st : WideString;
begin
  DataSetColumns := TStringList.Create;
  FXmlDoc := TXMLDocument.Create(nil) ;
  FXmlDoc.Active := true;

  FXmlExport := FXmlDoc.GetDocBinding('report', TXMLReportType) as IXMLReportType;
  try
    ADataSet.DisableControls;
    ADataSet.First;

    try
      with FXmlExport do
      begin
        Information.Created := DateTimeToStr(now);
        Information.Name := ExtractFileName(myFileName);

        if Assigned(AColumnsInfo) then
        begin
          for i := 0 to AColumnsInfo.Count - 1 do
          begin
            ColInfo := AColumnsInfo[i];
            Columns.Add(Copy(ColInfo, Pos('=', ColInfo) + 1, Length(ColInfo)));

            DataSetColumns.Add(Copy(ColInfo, 1, Pos('=', ColInfo) - 1));
          end;
        end
        else
        begin
          for i := 0 to ADataSet.FieldCount - 1 do
          begin
            Columns.Add(ADataSet.Fields[i].FieldName);
            DataSetColumns.Add(ADataSet.Fields[i].FieldName);
          end;
        end;

        while not ADataSet.Eof do
        begin
          with Rows.Add do
          for I := 0 to DataSetColumns.Count - 1 do
          begin
             s := ADataSet.FieldByName(DataSetColumns[i]).AsString;
             Add(s);
          end;

          ADataSet.Next;
        end;
      end;
    finally

    end;

    FXmlDoc.ParseOptions := FXmlDoc.ParseOptions + [poValidateOnParse] + [poPreserveWhiteSpace];
    FXmlDoc.XML.Text := xmlDoc.FormatXMLData(FXmlDoc.XML.Text);

    FXmlDoc.Active := True;
    FXmlDoc.Encoding := XML_ENCODING;
    FXmlDoc.Version := XML_VERSION;

    FXmlDoc.SaveToFile(myFileName);
    FXmlDoc.Active := False;

    sl := TStringList.Create;
    try
      sl.LoadFromFile(myFileName);
      st := sl.Text;
      Insert(#13#10, st, 39);
      sl.Text := st;
      sl.SaveToFile(myFileName);
    finally
      sl.Free;
    end;
  finally
    DataSetColumns.Free;
    AColumnsInfo.Free;
    ADataSet.EnableControls;
  end;
end;

procedure TDataSnapSchedule.UpdateSchedulerResult(ASchedulerResultId: Integer;
  AEndDate: TDateTime);
var
  SchedulerResult : TSchedulerResult;
begin
  SchedulerResult := TSchedulerResult.Create;
  try
    SchedulerResult.dmMain := FDM;

    SchedulerResult.ReadFromDatabase(ASchedulerResultId);
    SchedulerResult.EndDate := AEndDate;
    SchedulerResult.MessageStr := FError;
    SchedulerResult.Done := True;
    SchedulerResult.WriteToDatabase;
  finally
    SchedulerResult.Free;
  end;
end;

end.
