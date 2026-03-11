unit HistoryThread;

interface

uses
  Classes, ComCtrls, SysUtils, DB, Forms;

type
  THistoryThread = class(TThread)
  private
    { Private declarations }
    FFrame: TFrame;
    FDataSet: TDataSet;
    procedure LoadHistBegin;
    procedure LoadHistEnd;
    procedure LoadHistAdd;
  protected
    procedure Execute; override;
  public
    property Frame: TFrame read FFrame write FFrame;
    property DataSet: TDataSet read FDataSet write FDataSet;
  end;

implementation

uses
  CommonDM, HistoryFrame;

{ 
  Important: Methods and properties of objects in visual components can only be
  used in a method called using Synchronize, for example,

      Synchronize(UpdateCaption);  

  and UpdateCaption could look like,

    procedure THistryThread.UpdateCaption;
    begin
      Form1.Caption := 'Updated in a thread';
    end; 
    
    or 
    
    Synchronize( 
      procedure 
      begin
        Form1.Caption := 'Updated in thread via an anonymous method' 
      end
      )
    );
    
  where an anonymous method is passed.
  
  Similarly, the developer can call the Queue method with similar parameters as 
  above, instead passing another TThread class as the first parameter, putting
  the calling thread in a queue with the other thread.
    
}

{ THistoryThread }

procedure THistoryThread.Execute;
//var
//  tmp: Cardinal;
begin
  { Place thread code here }
    try
      Synchronize(LoadHistBegin);
      try
        FDataSet.First;
        while not FDataSet.Eof do begin
          Synchronize(LoadHistAdd);
          if Terminated then Exit;
          FDataSet.Next;
        end;
      finally
        Synchronize(LoadHistEnd);
      end;
    except
    end;
end;

procedure THistoryThread.LoadHistAdd;
begin
  TframeHistory(FFrame).lviewHistry.Items.BeginUpdate;
  try
    with TframeHistory(FFrame).lviewHistry.Items.Add do begin
      Caption := ' ' +
        DateTimeToStr(FDataSet.FieldByName('CREATED').AsDateTime);
      SubItems.Add(FDataSet.FieldByName('PROC_NAME').AsString);
      SubItems.Add(FDataSet.FieldByName('MESSAGE').AsString);
      SubItems.Add(FDataSet.FieldByName('USER_NAME').AsString);
      if FDataSet.FieldByName('ERROR').AsInteger <> 0 then
        StateIndex := dmCommon.InfoMessageImages[imtError]
      else StateIndex := -1;
    end;
  finally
    TframeHistory(FFrame).lviewHistry.Items.EndUpdate;
  end;
end;

procedure THistoryThread.LoadHistBegin;
begin
  with TframeHistory(FFrame) do begin
    pgrbarHistry.Show;
    edSearch.Enabled := False;
    bitbtnSearch.Enabled := False;
    lviewHistry.OnChange := nil;
  end;
end;

procedure THistoryThread.LoadHistEnd;
var
  i: integer;
begin
  with TframeHistory(FFrame) do begin
    lviewHistry.Items.BeginUpdate;
    try
      for i := 0 to lviewHistry.Columns.Count - 1 do
        lviewHistry.Columns.Items[i].Width := -2;
    finally
      lviewHistry.Items.EndUpdate;
    end;
    pgrbarHistry.Hide;
    edSearch.Enabled := True;
    bitbtnSearch.Enabled := True;
    lviewHistry.OnChange := lviewHistryChange;
    lviewHistryChange(lviewHistry, lviewHistry.Selected,
     ctState);
  end;
end;

end.
