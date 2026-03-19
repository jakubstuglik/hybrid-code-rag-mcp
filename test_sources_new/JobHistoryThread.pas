unit JobHistoryThread;

interface

uses
  Classes, SysUtils, Windows,
  ComCtrls, MainDataMod, AppConst;

type
  TJobHistoryThread = class(TThread)
  private
    FDriverId: Integer;
    FFromDate: TDateTime;
    FToDate: TDateTime;
    FListView: TListView;
    FStatusLabel: TLabel;
    FProgressBar: TProgressBar;
    FError: string;
    FRowCount: Integer;

    procedure DoUpdateListView;
    procedure DoUpdateStatus;
    procedure DoUpdateProgress;
    procedure DoShowError;

  protected
    procedure Execute; override;

  public
    constructor Create(ADriverId: Integer; AFromDate, AToDate: TDateTime;
      AListView: TListView; AStatusLabel: TLabel; AProgressBar: TProgressBar);

    property Error: string read FError;
    property RowCount: Integer read FRowCount;
  end;

implementation

constructor TJobHistoryThread.Create(ADriverId: Integer;
  AFromDate, AToDate: TDateTime;
  AListView: TListView; AStatusLabel: TLabel; AProgressBar: TProgressBar);
begin
  inherited Create(True);
  FDriverId := ADriverId;
  FFromDate := AFromDate;
  FToDate := AToDate;
  FListView := AListView;
  FStatusLabel := AStatusLabel;
  FProgressBar := AProgressBar;
  FError := '';
  FRowCount := 0;
  FreeOnTerminate := False;
end;

procedure TJobHistoryThread.Execute;
var
  dm: TdmFleet;
  cds: TClientDataSet;
  item: TListItem;
  i: Integer;
begin
  dm := TdmFleet.Create(nil);
  try
    try
      dm.OpenConnection;

      // Load historical job data for the driver
      cds := dm.cdsJobOrders;
      cds.CommandText := 'ORD_GetDriverHistory';
      cds.Params.ParamByName('DriverId').AsInteger := FDriverId;
      cds.Params.ParamByName('FromDate').AsDateTime := FFromDate;
      cds.Params.ParamByName('ToDate').AsDateTime := FToDate;
      cds.Open;

      FRowCount := cds.RecordCount;
      i := 0;

      Synchronize(DoUpdateStatus);

      cds.First;
      while not cds.Eof and not Terminated do
      begin
        Inc(i);
        // Populate list view item
        Synchronize(procedure
        begin
          item := FListView.Items.Add;
          item.Caption := cds.FieldByName('JobCode').AsString;
          item.SubItems.Add(cds.FieldByName('ScheduledTime').AsString);
          item.SubItems.Add(cds.FieldByName('RouteName').AsString);
          item.SubItems.Add(cds.FieldByName('VehicleReg').AsString);
          item.SubItems.Add(cds.FieldByName('Status').AsString);
          item.SubItems.Add(cds.FieldByName('DelayMinutes').AsString);
        end);

        if i mod 50 = 0 then
        begin
          // Update progress every 50 rows
          Synchronize(DoUpdateProgress);
        end;

        cds.Next;
      end;

    except
      on E: Exception do
      begin
        FError := E.Message;
        Synchronize(DoShowError);
      end;
    end;
  finally
    dm.Free;
  end;
end;

procedure TJobHistoryThread.DoUpdateListView;
begin
  FListView.Repaint;
end;

procedure TJobHistoryThread.DoUpdateStatus;
begin
  if Assigned(FStatusLabel) then
    FStatusLabel.Caption := Format('Loading %d records...', [FRowCount]);
end;

procedure TJobHistoryThread.DoUpdateProgress;
begin
  if Assigned(FProgressBar) then
    FProgressBar.StepIt;
end;

procedure TJobHistoryThread.DoShowError;
begin
  if Assigned(FStatusLabel) then
    FStatusLabel.Caption := 'Error: ' + FError;
end;

end.
