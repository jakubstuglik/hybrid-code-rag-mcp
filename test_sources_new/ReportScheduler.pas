unit ReportScheduler;

// ============================================================================
// ReportScheduler.pas  –  FleetOps report scheduling engine
// Provides TReportSchedule, TReportScheduleList, TScheduleTask,
// and the main TReportScheduler engine class.
// ============================================================================

interface

uses
  SysUtils, Classes, SyncObjs, DateUtils, Math;

// ── Enumerations ─────────────────────────────────────────────────────────────

type
  TScheduleFrequency = (
    sfOnce, sfHourly, sfDaily, sfWeekly, sfFortnightly,
    sfMonthly, sfQuarterly, sfYearly, sfCustom
  );

  TScheduleStatus = (
    ssActive, ssPaused, ssCompleted, ssError, ssCancelled
  );

  TOutputDestination = (
    odFile, odEmail, odFtp, odApi, odPrint
  );

// ── Constants ─────────────────────────────────────────────────────────────────

const
  SCHEDULE_MAX_RETRIES   = 3;
  SCHEDULE_RETRY_DELAY_S = 300;
  SCHEDULE_TIMEOUT_S     = 3600;
  SCHEDULE_MAX_QUEUED    = 100;
  REPORT_FORMAT_PDF      = 1;
  REPORT_FORMAT_EXCEL    = 2;
  REPORT_FORMAT_CSV      = 3;
  TASK_STATUS_PENDING    = 0;
  TASK_STATUS_RUNNING    = 1;
  TASK_STATUS_DONE       = 2;
  TASK_STATUS_FAILED     = 3;

// ── Forward declarations ──────────────────────────────────────────────────────

type
  TReportScheduleList = class;

// ── TReportSchedule ───────────────────────────────────────────────────────────

  TReportSchedule = class
  private
    FScheduleId   : Integer;
    FScheduleName : string;
    FReportType   : Integer;
    FFrequency    : TScheduleFrequency;
    FNextRun      : TDateTime;
    FLastRun      : TDateTime;
    FLastStatus   : TScheduleStatus;
    FEnabled      : Boolean;
    FOutputFormat : Integer;
    FOutputDest   : TOutputDestination;
    FEmailTo      : string;
    FFtpPath      : string;
    FOutputFile   : string;
    FParams       : TStringList;
    FRunCount     : Integer;
    FFailCount    : Integer;
    FMaxRuns      : Integer;
    FCreatedBy    : Integer;
    FCreatedAt    : TDateTime;
    FModifiedAt   : TDateTime;
    FDepotId      : Integer;
    FNotes        : string;

    function  GetParamValue(const AKey: string): string;
    procedure SetParamValue(const AKey, AValue: string);

  public
    constructor Create(AScheduleId: Integer);
    destructor  Destroy; override;

    // ── Scheduling logic ─────────────────────────────────────────────────────
    function  GetNextRun: TDateTime;
    procedure CalculateNextRun;
    function  IsRunDue: Boolean;
    procedure Enable;
    procedure Disable;
    procedure Reset;
    procedure IncrementRunCount;
    procedure IncrementFailCount;

    // ── Param persistence ─────────────────────────────────────────────────────
    procedure LoadParams(const AParamString: string);
    function  SaveParams: string;

    // ── Display helpers ───────────────────────────────────────────────────────
    function GetFrequencyText: string;
    function GetStatusText: string;

    // ── Cloning ───────────────────────────────────────────────────────────────
    function Clone: TReportSchedule;

    // ── Properties ────────────────────────────────────────────────────────────
    property ScheduleId   : Integer            read FScheduleId   write FScheduleId;
    property ScheduleName : string             read FScheduleName write FScheduleName;
    property ReportType   : Integer            read FReportType   write FReportType;
    property Frequency    : TScheduleFrequency read FFrequency    write FFrequency;
    property NextRun      : TDateTime          read FNextRun      write FNextRun;
    property LastRun      : TDateTime          read FLastRun      write FLastRun;
    property LastStatus   : TScheduleStatus    read FLastStatus   write FLastStatus;
    property Enabled      : Boolean            read FEnabled      write FEnabled;
    property OutputFormat : Integer            read FOutputFormat write FOutputFormat;
    property OutputDest   : TOutputDestination read FOutputDest   write FOutputDest;
    property EmailTo      : string             read FEmailTo      write FEmailTo;
    property FtpPath      : string             read FFtpPath      write FFtpPath;
    property OutputFile   : string             read FOutputFile   write FOutputFile;
    property Params       : TStringList        read FParams;
    property RunCount     : Integer            read FRunCount     write FRunCount;
    property FailCount    : Integer            read FFailCount    write FFailCount;
    property MaxRuns      : Integer            read FMaxRuns      write FMaxRuns;
    property CreatedBy    : Integer            read FCreatedBy    write FCreatedBy;
    property CreatedAt    : TDateTime          read FCreatedAt    write FCreatedAt;
    property ModifiedAt   : TDateTime          read FModifiedAt   write FModifiedAt;
    property DepotId      : Integer            read FDepotId      write FDepotId;
    property Notes        : string             read FNotes        write FNotes;
    property ParamValues[const AKey: string] : string
      read GetParamValue write SetParamValue;
  end;

// ── TReportScheduleList ───────────────────────────────────────────────────────

  TReportScheduleList = class
  private
    FList : TList;
    function GetCount: Integer;
    function GetItem(AIndex: Integer): TReportSchedule;
  public
    constructor Create;
    destructor  Destroy; override;

    procedure Add(ASchedule: TReportSchedule);
    procedure Remove(AScheduleId: Integer);
    procedure Clear;

    function FindById(AScheduleId: Integer): TReportSchedule;
    function FindByName(const AName: string): TReportSchedule;

    procedure GetEnabledSchedules(AResult: TList);
    procedure GetDueSchedules(AResult: TList);
    procedure SortByNextRun;
    procedure FilterByDepot(ADepotId: Integer; AResult: TList);
    function  GetActiveCount: Integer;

    property Count: Integer            read GetCount;
    property Items[AIndex: Integer]   : TReportSchedule read GetItem; default;
  end;

// ── TScheduleTask ─────────────────────────────────────────────────────────────

  TScheduleTask = class
  private
    FTaskId       : Integer;
    FScheduleId   : Integer;
    FStartedAt    : TDateTime;
    FCompletedAt  : TDateTime;
    FStatus       : Integer;
    FOutputFile   : string;
    FRowCount     : Integer;
    FErrorMessage : string;
    FAttemptCount : Integer;
    FScheduledFor : TDateTime;
  public
    constructor Create(ATaskId, AScheduleId: Integer; AScheduledFor: TDateTime);

    function IsComplete   : Boolean;
    function IsFailed     : Boolean;
    function IsRunning    : Boolean;
    function GetElapsedSeconds: Double;
    function GetStatusText: string;
    function GetSummary   : string;

    procedure MarkComplete(const AOutputFile: string; ARowCount: Integer);
    procedure MarkFailed(const AError: string);
    procedure MarkRunning;
    procedure IncrementAttempts;

    property TaskId       : Integer   read FTaskId       write FTaskId;
    property ScheduleId   : Integer   read FScheduleId   write FScheduleId;
    property StartedAt    : TDateTime read FStartedAt    write FStartedAt;
    property CompletedAt  : TDateTime read FCompletedAt  write FCompletedAt;
    property Status       : Integer   read FStatus       write FStatus;
    property OutputFile   : string    read FOutputFile   write FOutputFile;
    property RowCount     : Integer   read FRowCount     write FRowCount;
    property ErrorMessage : string    read FErrorMessage write FErrorMessage;
    property AttemptCount : Integer   read FAttemptCount write FAttemptCount;
    property ScheduledFor : TDateTime read FScheduledFor write FScheduledFor;
  end;

// ── TReportScheduler ──────────────────────────────────────────────────────────

  TSchedulerThread = class;   // forward

  TReportScheduler = class
  private
    FSchedules     : TReportScheduleList;
    FRunning       : Boolean;
    FThread        : TSchedulerThread;
    FLastCheck     : TDateTime;
    FCheckInterval : Integer;      // seconds
    FMaxConcurrent : Integer;
    FActiveTasks   : Integer;
    FTotalRun      : Integer;
    FTotalFailed   : Integer;
    FCritSec       : TCriticalSection;
    FTaskLog       : TList;        // history of TScheduleTask

    procedure ExecuteSchedule(ASchedule: TReportSchedule);
    procedure CleanTaskLog;

  public
    constructor Create;
    destructor  Destroy; override;

    // ── Lifecycle ─────────────────────────────────────────────────────────────
    procedure Start;
    procedure Stop;
    procedure Pause;
    procedure Resume;
    function  IsRunning: Boolean;

    // ── Schedule management ───────────────────────────────────────────────────
    procedure AddSchedule(ASchedule: TReportSchedule);
    procedure RemoveSchedule(AScheduleId: Integer);
    function  GetSchedule(AScheduleId: Integer): TReportSchedule;
    procedure LoadSchedules(const AFilePath: string);
    procedure SaveSchedules(const AFilePath: string);
    procedure RunNow(AScheduleId: Integer);

    // ── Internal polling ──────────────────────────────────────────────────────
    procedure CheckDue;

    // ── Metrics ───────────────────────────────────────────────────────────────
    function GetActiveTasks : Integer;
    function GetQueueDepth  : Integer;
    function GetTotalRun    : Integer;
    function GetTotalFailed : Integer;
    function GetStatus      : string;

    // ── Configuration ─────────────────────────────────────────────────────────
    procedure SetCheckInterval(ASecs: Integer);

    property Schedules     : TReportScheduleList read FSchedules;
    property CheckInterval : Integer             read FCheckInterval write FCheckInterval;
    property MaxConcurrent : Integer             read FMaxConcurrent write FMaxConcurrent;
  end;

// ── Background polling thread ─────────────────────────────────────────────────

  TSchedulerThread = class(TThread)
  private
    FScheduler : TReportScheduler;
  protected
    procedure Execute; override;
  public
    constructor Create(AScheduler: TReportScheduler);
  end;

implementation

// ════════════════════════════════════════════════════════════════════════════
// TReportSchedule
// ════════════════════════════════════════════════════════════════════════════

constructor TReportSchedule.Create(AScheduleId: Integer);
begin
  inherited Create;
  FScheduleId   := AScheduleId;
  FFrequency    := sfDaily;
  FLastStatus   := ssActive;
  FEnabled      := True;
  FOutputFormat := REPORT_FORMAT_CSV;
  FOutputDest   := odFile;
  FRunCount     := 0;
  FFailCount    := 0;
  FMaxRuns      := 0;   // 0 = unlimited
  FCreatedAt    := Now;
  FModifiedAt   := Now;
  FParams       := TStringList.Create;
  FParams.Delimiter       := '&';
  FParams.StrictDelimiter := True;
  FNextRun      := Now;
end;

destructor TReportSchedule.Destroy;
begin
  FreeAndNil(FParams);
  inherited;
end;

function TReportSchedule.GetParamValue(const AKey: string): string;
begin
  Result := FParams.Values[AKey];
end;

procedure TReportSchedule.SetParamValue(const AKey, AValue: string);
begin
  FParams.Values[AKey] := AValue;
  FModifiedAt := Now;
end;

function TReportSchedule.GetNextRun: TDateTime;
begin
  Result := FNextRun;
end;

procedure TReportSchedule.CalculateNextRun;
var
  base: TDateTime;
begin
  if FLastRun > 0 then
    base := FLastRun
  else
    base := Now;

  case FFrequency of
    sfOnce:
      FNextRun := 0;   // Will not run again automatically

    sfHourly:
      FNextRun := IncHour(base, 1);

    sfDaily:
      FNextRun := IncDay(base, 1);

    sfWeekly:
      FNextRun := IncDay(base, 7);

    sfFortnightly:
      FNextRun := IncDay(base, 14);

    sfMonthly:
      FNextRun := IncMonth(base, 1);

    sfQuarterly:
      FNextRun := IncMonth(base, 3);

    sfYearly:
      FNextRun := IncYear(base, 1);

    sfCustom:
      begin
        // Custom interval stored in Params['interval_hours']
        var hours := StrToIntDef(FParams.Values['interval_hours'], 24);
        FNextRun := IncHour(base, hours);
      end;
  end;

  FModifiedAt := Now;
end;

function TReportSchedule.IsRunDue: Boolean;
begin
  Result := FEnabled
    and (FNextRun > 0)
    and (Now >= FNextRun)
    and (FLastStatus <> ssCancelled)
    and ((FMaxRuns = 0) or (FRunCount < FMaxRuns));
end;

procedure TReportSchedule.Enable;
begin
  FEnabled    := True;
  FLastStatus := ssActive;
  FModifiedAt := Now;
end;

procedure TReportSchedule.Disable;
begin
  FEnabled    := False;
  FModifiedAt := Now;
end;

procedure TReportSchedule.Reset;
begin
  FRunCount  := 0;
  FFailCount := 0;
  FLastRun   := 0;
  FLastStatus := ssActive;
  CalculateNextRun;
  FModifiedAt := Now;
end;

procedure TReportSchedule.IncrementRunCount;
begin
  Inc(FRunCount);
  FLastRun    := Now;
  FModifiedAt := Now;
  CalculateNextRun;
  // If sfOnce, mark completed after first successful run
  if FFrequency = sfOnce then
  begin
    FEnabled    := False;
    FLastStatus := ssCompleted;
  end;
end;

procedure TReportSchedule.IncrementFailCount;
begin
  Inc(FFailCount);
  FLastStatus := ssError;
  FModifiedAt := Now;
  // After max retries, apply a delay before next attempt
  if FFailCount >= SCHEDULE_MAX_RETRIES then
    FNextRun := IncSecond(Now, SCHEDULE_RETRY_DELAY_S * FFailCount);
end;

procedure TReportSchedule.LoadParams(const AParamString: string);
begin
  FParams.Clear;
  FParams.DelimitedText := AParamString;
end;

function TReportSchedule.SaveParams: string;
begin
  Result := FParams.DelimitedText;
end;

function TReportSchedule.GetFrequencyText: string;
const
  FREQ_NAMES: array[TScheduleFrequency] of string = (
    'Once', 'Hourly', 'Daily', 'Weekly', 'Fortnightly',
    'Monthly', 'Quarterly', 'Yearly', 'Custom'
  );
begin
  Result := FREQ_NAMES[FFrequency];
end;

function TReportSchedule.GetStatusText: string;
const
  STATUS_NAMES: array[TScheduleStatus] of string = (
    'Active', 'Paused', 'Completed', 'Error', 'Cancelled'
  );
begin
  Result := STATUS_NAMES[FLastStatus];
end;

function TReportSchedule.Clone: TReportSchedule;
begin
  Result := TReportSchedule.Create(FScheduleId);
  Result.FScheduleName := FScheduleName;
  Result.FReportType   := FReportType;
  Result.FFrequency    := FFrequency;
  Result.FNextRun      := FNextRun;
  Result.FLastRun      := FLastRun;
  Result.FLastStatus   := FLastStatus;
  Result.FEnabled      := FEnabled;
  Result.FOutputFormat := FOutputFormat;
  Result.FOutputDest   := FOutputDest;
  Result.FEmailTo      := FEmailTo;
  Result.FFtpPath      := FFtpPath;
  Result.FOutputFile   := FOutputFile;
  Result.FRunCount     := FRunCount;
  Result.FFailCount    := FFailCount;
  Result.FMaxRuns      := FMaxRuns;
  Result.FCreatedBy    := FCreatedBy;
  Result.FCreatedAt    := FCreatedAt;
  Result.FModifiedAt   := FModifiedAt;
  Result.FDepotId      := FDepotId;
  Result.FNotes        := FNotes;
  Result.FParams.Assign(FParams);
end;

// ════════════════════════════════════════════════════════════════════════════
// TReportScheduleList
// ════════════════════════════════════════════════════════════════════════════

constructor TReportScheduleList.Create;
begin
  inherited Create;
  FList := TList.Create;
end;

destructor TReportScheduleList.Destroy;
begin
  Clear;
  FreeAndNil(FList);
  inherited;
end;

function TReportScheduleList.GetCount: Integer;
begin
  Result := FList.Count;
end;

function TReportScheduleList.GetItem(AIndex: Integer): TReportSchedule;
begin
  Result := TReportSchedule(FList[AIndex]);
end;

procedure TReportScheduleList.Add(ASchedule: TReportSchedule);
begin
  FList.Add(ASchedule);
end;

procedure TReportScheduleList.Remove(AScheduleId: Integer);
var
  sched: TReportSchedule;
  i: Integer;
begin
  for i := FList.Count - 1 downto 0 do
  begin
    sched := TReportSchedule(FList[i]);
    if sched.ScheduleId = AScheduleId then
    begin
      FList.Delete(i);
      sched.Free;
      Break;
    end;
  end;
end;

procedure TReportScheduleList.Clear;
var
  i: Integer;
begin
  for i := 0 to FList.Count - 1 do
    TReportSchedule(FList[i]).Free;
  FList.Clear;
end;

function TReportScheduleList.FindById(AScheduleId: Integer): TReportSchedule;
var
  i: Integer;
  sched: TReportSchedule;
begin
  Result := nil;
  for i := 0 to FList.Count - 1 do
  begin
    sched := TReportSchedule(FList[i]);
    if sched.ScheduleId = AScheduleId then
    begin
      Result := sched;
      Break;
    end;
  end;
end;

function TReportScheduleList.FindByName(const AName: string): TReportSchedule;
var
  i: Integer;
  sched: TReportSchedule;
begin
  Result := nil;
  for i := 0 to FList.Count - 1 do
  begin
    sched := TReportSchedule(FList[i]);
    if SameText(sched.ScheduleName, AName) then
    begin
      Result := sched;
      Break;
    end;
  end;
end;

procedure TReportScheduleList.GetEnabledSchedules(AResult: TList);
var
  i: Integer;
  sched: TReportSchedule;
begin
  AResult.Clear;
  for i := 0 to FList.Count - 1 do
  begin
    sched := TReportSchedule(FList[i]);
    if sched.Enabled then
      AResult.Add(sched);
  end;
end;

procedure TReportScheduleList.GetDueSchedules(AResult: TList);
var
  i: Integer;
  sched: TReportSchedule;
begin
  AResult.Clear;
  for i := 0 to FList.Count - 1 do
  begin
    sched := TReportSchedule(FList[i]);
    if sched.IsRunDue then
      AResult.Add(sched);
  end;
end;

procedure TReportScheduleList.SortByNextRun;
var
  i, j: Integer;
  a, b: TReportSchedule;
  tmp: Pointer;
begin
  // Bubble sort — list is small in practice
  for i := 0 to FList.Count - 2 do
    for j := 0 to FList.Count - 2 - i do
    begin
      a := TReportSchedule(FList[j]);
      b := TReportSchedule(FList[j + 1]);
      if (b.NextRun > 0) and ((a.NextRun = 0) or (a.NextRun > b.NextRun)) then
      begin
        tmp         := FList[j];
        FList[j]    := FList[j + 1];
        FList[j + 1] := tmp;
      end;
    end;
end;

procedure TReportScheduleList.FilterByDepot(ADepotId: Integer; AResult: TList);
var
  i: Integer;
  sched: TReportSchedule;
begin
  AResult.Clear;
  for i := 0 to FList.Count - 1 do
  begin
    sched := TReportSchedule(FList[i]);
    if (ADepotId = 0) or (sched.DepotId = ADepotId) then
      AResult.Add(sched);
  end;
end;

function TReportScheduleList.GetActiveCount: Integer;
var
  i: Integer;
begin
  Result := 0;
  for i := 0 to FList.Count - 1 do
    if TReportSchedule(FList[i]).Enabled then
      Inc(Result);
end;

// ════════════════════════════════════════════════════════════════════════════
// TScheduleTask
// ════════════════════════════════════════════════════════════════════════════

constructor TScheduleTask.Create(ATaskId, AScheduleId: Integer;
  AScheduledFor: TDateTime);
begin
  inherited Create;
  FTaskId       := ATaskId;
  FScheduleId   := AScheduleId;
  FScheduledFor := AScheduledFor;
  FStatus       := TASK_STATUS_PENDING;
  FAttemptCount := 0;
  FRowCount     := 0;
  FStartedAt    := 0;
  FCompletedAt  := 0;
end;

function TScheduleTask.IsComplete: Boolean;
begin
  Result := FStatus = TASK_STATUS_DONE;
end;

function TScheduleTask.IsFailed: Boolean;
begin
  Result := FStatus = TASK_STATUS_FAILED;
end;

function TScheduleTask.IsRunning: Boolean;
begin
  Result := FStatus = TASK_STATUS_RUNNING;
end;

function TScheduleTask.GetElapsedSeconds: Double;
var
  endTime: TDateTime;
begin
  if FStartedAt = 0 then
  begin
    Result := 0;
    Exit;
  end;
  endTime := IfThen(FCompletedAt > 0, FCompletedAt, Now);
  Result  := SecondsBetween(FStartedAt, endTime);
end;

function TScheduleTask.GetStatusText: string;
begin
  case FStatus of
    TASK_STATUS_PENDING : Result := 'Pending';
    TASK_STATUS_RUNNING : Result := 'Running';
    TASK_STATUS_DONE    : Result := 'Completed';
    TASK_STATUS_FAILED  : Result := 'Failed';
  else
    Result := 'Unknown';
  end;
end;

function TScheduleTask.GetSummary: string;
begin
  Result := Format(
    'Task %d (Schedule %d): %s, %d rows, %.1f s, attempt %d',
    [FTaskId, FScheduleId, GetStatusText, FRowCount,
     GetElapsedSeconds, FAttemptCount]);
  if FErrorMessage <> '' then
    Result := Result + ' — ' + FErrorMessage;
end;

procedure TScheduleTask.MarkComplete(const AOutputFile: string;
  ARowCount: Integer);
begin
  FOutputFile  := AOutputFile;
  FRowCount    := ARowCount;
  FStatus      := TASK_STATUS_DONE;
  FCompletedAt := Now;
end;

procedure TScheduleTask.MarkFailed(const AError: string);
begin
  FErrorMessage := AError;
  FStatus       := TASK_STATUS_FAILED;
  FCompletedAt  := Now;
end;

procedure TScheduleTask.MarkRunning;
begin
  FStatus    := TASK_STATUS_RUNNING;
  FStartedAt := Now;
end;

procedure TScheduleTask.IncrementAttempts;
begin
  Inc(FAttemptCount);
end;

// ════════════════════════════════════════════════════════════════════════════
// TSchedulerThread
// ════════════════════════════════════════════════════════════════════════════

constructor TSchedulerThread.Create(AScheduler: TReportScheduler);
begin
  inherited Create(True);
  FScheduler       := AScheduler;
  FreeOnTerminate  := False;
end;

procedure TSchedulerThread.Execute;
begin
  while not Terminated do
  begin
    if FScheduler.IsRunning then
      FScheduler.CheckDue;
    Sleep(FScheduler.CheckInterval * 1000);
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// TReportScheduler
// ════════════════════════════════════════════════════════════════════════════

constructor TReportScheduler.Create;
begin
  inherited Create;
  FSchedules     := TReportScheduleList.Create;
  FCritSec       := TCriticalSection.Create;
  FTaskLog       := TList.Create;
  FCheckInterval := 60;      // check every 60 seconds
  FMaxConcurrent := 4;
  FActiveTasks   := 0;
  FTotalRun      := 0;
  FTotalFailed   := 0;
  FRunning       := False;
  FThread        := nil;
  FLastCheck     := Now;
end;

destructor TReportScheduler.Destroy;
begin
  Stop;
  FreeAndNil(FSchedules);
  CleanTaskLog;
  FreeAndNil(FTaskLog);
  FreeAndNil(FCritSec);
  inherited;
end;

procedure TReportScheduler.CleanTaskLog;
var
  i: Integer;
begin
  for i := 0 to FTaskLog.Count - 1 do
    TScheduleTask(FTaskLog[i]).Free;
  FTaskLog.Clear;
end;

procedure TReportScheduler.Start;
begin
  FCritSec.Acquire;
  try
    if FRunning then Exit;
    FRunning := True;
    FThread  := TSchedulerThread.Create(Self);
    FThread.Start;
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.Stop;
begin
  FCritSec.Acquire;
  try
    FRunning := False;
    if Assigned(FThread) then
    begin
      FThread.Terminate;
      FThread.WaitFor;
      FreeAndNil(FThread);
    end;
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.Pause;
begin
  FCritSec.Acquire;
  try
    FRunning := False;
    // Thread stays alive but CheckDue will be skipped
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.Resume;
begin
  FCritSec.Acquire;
  try
    FRunning := True;
  finally
    FCritSec.Release;
  end;
end;

function TReportScheduler.IsRunning: Boolean;
begin
  FCritSec.Acquire;
  try
    Result := FRunning;
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.AddSchedule(ASchedule: TReportSchedule);
begin
  FCritSec.Acquire;
  try
    FSchedules.Add(ASchedule);
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.RemoveSchedule(AScheduleId: Integer);
begin
  FCritSec.Acquire;
  try
    FSchedules.Remove(AScheduleId);
  finally
    FCritSec.Release;
  end;
end;

function TReportScheduler.GetSchedule(AScheduleId: Integer): TReportSchedule;
begin
  FCritSec.Acquire;
  try
    Result := FSchedules.FindById(AScheduleId);
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.LoadSchedules(const AFilePath: string);
var
  sl: TStringList;
  i: Integer;
  sched: TReportSchedule;
  id: Integer;
begin
  if not FileExists(AFilePath) then Exit;

  FCritSec.Acquire;
  try
    FSchedules.Clear;
    sl := TStringList.Create;
    try
      sl.LoadFromFile(AFilePath);
      i := 0;
      while i < sl.Count do
      begin
        if sl[i].StartsWith('[Schedule:') then
        begin
          id := StrToIntDef(
            Copy(sl[i], 11, Length(sl[i]) - 11), 0);
          if id > 0 then
          begin
            sched := TReportSchedule.Create(id);
            Inc(i);
            while (i < sl.Count) and not sl[i].StartsWith('[Schedule:') do
            begin
              sched.FParams.Add(sl[i]);
              Inc(i);
            end;
            // Restore fields from params after loading
            sched.ScheduleName := sched.FParams.Values['Name'];
            sched.ReportType   := StrToIntDef(sched.FParams.Values['ReportType'], 0);
            sched.Enabled      := sched.FParams.Values['Enabled'] = '1';
            FSchedules.Add(sched);
          end;
        end
        else
          Inc(i);
      end;
    finally
      sl.Free;
    end;
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.SaveSchedules(const AFilePath: string);
var
  sl: TStringList;
  i: Integer;
  sched: TReportSchedule;
begin
  FCritSec.Acquire;
  try
    sl := TStringList.Create;
    try
      for i := 0 to FSchedules.Count - 1 do
      begin
        sched := FSchedules[i];
        sl.Add(Format('[Schedule:%d]', [sched.ScheduleId]));
        sl.Add('Name='        + sched.ScheduleName);
        sl.Add('ReportType='  + IntToStr(sched.ReportType));
        sl.Add('Frequency='   + IntToStr(Ord(sched.Frequency)));
        sl.Add('NextRun='     + FloatToStr(sched.NextRun));
        sl.Add('LastRun='     + FloatToStr(sched.LastRun));
        sl.Add('Enabled='     + IfThen(sched.Enabled, '1', '0'));
        sl.Add('OutputFormat='+ IntToStr(sched.OutputFormat));
        sl.Add('OutputDest='  + IntToStr(Ord(sched.OutputDest)));
        sl.Add('EmailTo='     + sched.EmailTo);
        sl.Add('OutputFile='  + sched.OutputFile);
        sl.Add('RunCount='    + IntToStr(sched.RunCount));
        sl.Add('FailCount='   + IntToStr(sched.FailCount));
        sl.Add('MaxRuns='     + IntToStr(sched.MaxRuns));
        sl.Add('DepotId='     + IntToStr(sched.DepotId));
        sl.Add('Notes='       + sched.Notes);
        sl.Add('Params='      + sched.SaveParams);
      end;
      ForceDirectories(ExtractFilePath(AFilePath));
      sl.SaveToFile(AFilePath, TEncoding.UTF8);
    finally
      sl.Free;
    end;
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.RunNow(AScheduleId: Integer);
var
  sched: TReportSchedule;
begin
  FCritSec.Acquire;
  try
    sched := FSchedules.FindById(AScheduleId);
    if not Assigned(sched) then
      raise Exception.CreateFmt('Schedule %d not found.', [AScheduleId]);
    if FActiveTasks >= FMaxConcurrent then
      raise Exception.Create('Maximum concurrent task limit reached.');
    Inc(FActiveTasks);
  finally
    FCritSec.Release;
  end;

  try
    ExecuteSchedule(sched);
  finally
    FCritSec.Acquire;
    Dec(FActiveTasks);
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.CheckDue;
var
  due: TList;
  i: Integer;
  sched: TReportSchedule;
begin
  FLastCheck := Now;
  due := TList.Create;
  try
    FCritSec.Acquire;
    try
      FSchedules.GetDueSchedules(due);
    finally
      FCritSec.Release;
    end;

    for i := 0 to due.Count - 1 do
    begin
      sched := TReportSchedule(due[i]);
      FCritSec.Acquire;
      try
        if FActiveTasks >= FMaxConcurrent then Break;
        Inc(FActiveTasks);
      finally
        FCritSec.Release;
      end;

      try
        ExecuteSchedule(sched);
      finally
        FCritSec.Acquire;
        Dec(FActiveTasks);
        FCritSec.Release;
      end;
    end;
  finally
    due.Free;
  end;
end;

procedure TReportScheduler.ExecuteSchedule(ASchedule: TReportSchedule);
var
  task: TScheduleTask;
  taskId: Integer;
  outFile: string;
begin
  FCritSec.Acquire;
  taskId := FTotalRun + FTotalFailed + 1;
  FCritSec.Release;

  task := TScheduleTask.Create(taskId, ASchedule.ScheduleId, ASchedule.NextRun);
  task.MarkRunning;
  task.IncrementAttempts;

  try
    // Build output file path
    outFile := Format('%s%s_%s.%s',
      [ExtractFilePath(ASchedule.OutputFile),
       ChangeFileExt(ExtractFileName(ASchedule.OutputFile), ''),
       FormatDateTime('YYYYMMDD_HHNNSS', Now),
       IfThen(ASchedule.OutputFormat = REPORT_FORMAT_CSV, 'csv',
              IfThen(ASchedule.OutputFormat = REPORT_FORMAT_EXCEL, 'xlsx', 'pdf'))]);

    // Ensure output directory exists
    ForceDirectories(ExtractFilePath(outFile));

    // Write a placeholder output (real implementation delegates to report engine)
    var sl := TStringList.Create;
    try
      sl.Add(Format('Report: %s', [ASchedule.ScheduleName]));
      sl.Add(Format('Generated: %s', [FormatDateTime('dd/mm/yyyy hh:nn:ss', Now)]));
      sl.Add(Format('Type: %d  Format: %d', [ASchedule.ReportType, ASchedule.OutputFormat]));
      sl.Add(Format('Params: %s', [ASchedule.SaveParams]));
      if outFile <> '' then
        sl.SaveToFile(outFile, TEncoding.UTF8);
    finally
      sl.Free;
    end;

    task.MarkComplete(outFile, 0);
    ASchedule.IncrementRunCount;

    FCritSec.Acquire;
    Inc(FTotalRun);
    FTaskLog.Add(task);
    FCritSec.Release;

  except
    on E: Exception do
    begin
      task.MarkFailed(E.Message);
      ASchedule.IncrementFailCount;

      FCritSec.Acquire;
      Inc(FTotalFailed);
      FTaskLog.Add(task);
      FCritSec.Release;
    end;
  end;
end;

function TReportScheduler.GetActiveTasks: Integer;
begin
  FCritSec.Acquire;
  try
    Result := FActiveTasks;
  finally
    FCritSec.Release;
  end;
end;

function TReportScheduler.GetQueueDepth: Integer;
var
  due: TList;
begin
  due := TList.Create;
  try
    FCritSec.Acquire;
    try
      FSchedules.GetDueSchedules(due);
    finally
      FCritSec.Release;
    end;
    Result := due.Count;
  finally
    due.Free;
  end;
end;

function TReportScheduler.GetTotalRun: Integer;
begin
  FCritSec.Acquire;
  try
    Result := FTotalRun;
  finally
    FCritSec.Release;
  end;
end;

function TReportScheduler.GetTotalFailed: Integer;
begin
  FCritSec.Acquire;
  try
    Result := FTotalFailed;
  finally
    FCritSec.Release;
  end;
end;

function TReportScheduler.GetStatus: string;
begin
  FCritSec.Acquire;
  try
    Result := Format(
      'Scheduler: %s | Active: %d/%d | Run: %d | Failed: %d | Schedules: %d | Due: %d',
      [IfThen(FRunning, 'Running', 'Stopped'),
       FActiveTasks, FMaxConcurrent,
       FTotalRun, FTotalFailed,
       FSchedules.Count,
       GetQueueDepth]);
  finally
    FCritSec.Release;
  end;
end;

procedure TReportScheduler.SetCheckInterval(ASecs: Integer);
begin
  FCritSec.Acquire;
  try
    FCheckInterval := Max(10, ASecs);
  finally
    FCritSec.Release;
  end;
end;

end.
