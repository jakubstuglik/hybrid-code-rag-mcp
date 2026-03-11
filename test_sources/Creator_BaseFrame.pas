unit Creator_BaseFrame;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, MainDM, JvWizard
  , BasicClasses
  ;

type
  TCreatorStepReturns = array of Variant;
  TframeBaseCreator = class(TFrame)
  private
    FOnExitPage: TNotifyEvent;
    FOnPage: TNotifyEvent;
    FOnSelectNextPage: TJvWizardPageClickEvent;

    { Private declarations }
    function GetDatabaseItem: TDatabaseItem;
    procedure SetOnExitPage(const Value: TNotifyEvent);

    procedure SetOnPage(const Value: TNotifyEvent);
    function GetdmMain: TdmMain;
    procedure SetOnSelectNextPage(const Value: TJvWizardPageClickEvent);
  protected
    fdmMain: TdmMain;
    fPrepared: boolean;
    fSubTitle: String;
    fTitle: string;
    fEnabledButtons: TJvWizardButtonSet;
    fVisibleButtons: TJvWizardButtonSet;
    fReturns: TCreatorStepReturns;
    FAnyChanged   : Boolean;
    //fSkipped: boolean;
    function GetAnyChanged : Boolean; virtual;
    function GetCreator(aObj: TWinControl): TWinControl;
    function GetForm(aObj: TWinControl): TWinControl;
  public
    { Public declarations }
    procedure HideErrors;
    function ReturnCount: Integer;
    procedure Prepare(AdmMain: TdmMain); virtual; abstract;
    property Prepared: boolean read fPrepared write fPrepared;
    function Validate: boolean; virtual; abstract;
    function ErrorMessage: string; virtual; abstract;
    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;

    procedure DoExitPage;
    procedure DoPage;

    property Title: string read fTitle ;
    property Subtitle: String read fSubTitle;
    property EnabledButtons: TJvWizardButtonSet read fEnabledButtons;
    property VisibleButtons: TJvWizardButtonSet read fVisibleButtons;
    function Returns: TCreatorStepReturns; virtual; abstract;
    function Steps: TJvWizardPageList;
    function IntPageReturn( APageNum : Integer; AReturnNum : Integer) : Integer; overload;
    function PageReturn( APageNum : Integer; AReturnNum : Integer) : Variant; overload;
    function PageReturn( APageNum : Integer; AReturnName : String) : Variant; overload;
    function BoolPageReturn( APageNum : Integer; AReturnName : String) : Boolean;
    function IntPageReturn( APageNum : Integer; AReturnName : String) : Integer; overload;
    function StrPageReturn( APageNum : Integer; AReturnName : String) : String;
    function DateTimePageReturn( APageNum : Integer; AReturnName : String) : TDateTime;
    function Return( AReturnName : String ) : Variant;

    procedure ReturnDatabaseItemID( AID : Integer = -1);
    procedure FinishReturnObj(AReturnObject: TObject);
    procedure SetReturnObj(AReturnName: String; AReturnObject: TObject);
    procedure SetReturn(AIndex: integer; AReturnValue: Variant); overload;
    procedure SetReturn( AReturnName : String; AReturnValue : Variant); overload;
    procedure SetReturn( AReturnName : String; AReturnValue : String); overload;
    procedure AddReturn( AReturnValue : Variant);
    procedure ClearReturns;

    property DatabaseItem : TDatabaseItem read GetDatabaseItem;

    property OnExitPage : TNotifyEvent read FOnExitPage write SetOnExitPage;
    property OnBeforeNextButtonClick : TJvWizardPageClickEvent read FOnSelectNextPage write SetOnSelectNextPage;
    property OnPage : TNotifyEvent read FOnPage write SetOnPage;

    procedure StepEnabled( AStepNum : Integer; AEnabled : Boolean );
    function  ThisStep : TJvWizardInteriorPage;
    property AnyChanged : Boolean read GetAnyChanged;
    function Page(APageNum : Integer) : TframeBaseCreator;
    function NextPage: TframeBaseCreator;

    function BeforeClose : Boolean; virtual;
    property dmMain: TdmMain read GetdmMain;

    procedure GoToNextStep;
    procedure Clear; virtual;
  end;

  TframeBaseCreatorClass = class of TframeBaseCreator;

implementation

uses
  Creator_CreatorFrame
  , KMUtils
  , KMStrUtils
  , BaseEditorForm
  ;

{$R *.dfm}

{ TframeBaseCreator }

constructor TframeBaseCreator.Create(AOwner: TComponent);
begin
  inherited;
  fPrepared := False;
  fReturns := nil;
  fAnyChanged := false;
  FOnExitPage := nil;
  fEnabledButtons := [bkStart, bkLast, bkBack, bkNext, bkFinish, bkCancel, bkHelp];
end;


destructor TframeBaseCreator.Destroy;
begin
  fReturns := nil;
  OnPage := nil;
  OnExitPage := nil;
  OnBeforeNextButtonClick := nil;
  inherited;
end;

procedure TframeBaseCreator.DoExitPage;
var
  f: TWinControl;
begin
  Screen.Cursor := crHourGlass;

  f := GetForm(Self);
  if Assigned(f) then TfrmBaseEditor(f).MessagesClear;

  if Assigned(FOnExitPage) then FOnExitPage(Self)
end;

procedure TframeBaseCreator.DoPage;
begin
  if Assigned(FOnPage) then FOnPage(Self);
  Screen.Cursor := crDefault;
end;

function TframeBaseCreator.GetAnyChanged: Boolean;
begin
  result := FAnyChanged
end;

function TframeBaseCreator.GetCreator(aObj: TWinControl): TWinControl;
begin
  if not Assigned(aObj.Parent) then Result := nil
  else
  if aObj.Parent is TframeCreator then
    Result := aObj.Parent
  else Result := GetCreator(aObj.Parent);
end;

function TframeBaseCreator.GetDatabaseItem: TDatabaseItem;
var
  _frameCreator : TframeCreator;
begin
  _frameCreator := TframeCreator( GetCreator(self) );
  if Assigned(_frameCreator) then
    result := _frameCreator.DatabaseItem else result := nil;
end;

function TframeBaseCreator.GetdmMain: TdmMain;
var
  o: TDatabaseItem;
begin
  if Assigned(fdmMain) then
    Result := fdmMain
  else begin
    o := DatabaseItem;
    if Assigned(o) then Result := o.dmMain
    else Result := nil;
  end;
end;

function TframeBaseCreator.GetForm(aObj: TWinControl): TWinControl;
begin
  if not Assigned(aObj.Parent) then Result := nil
  else
  if aObj.Parent is TfrmBaseEditor then
    Result := aObj.Parent
  else Result := GetForm(aObj.Parent);
end;

procedure TframeBaseCreator.GoToNextStep;
begin
  TframeCreator(GetCreator(self)).GoToNextStep;
end;

procedure TframeBaseCreator.HideErrors;
var
  _frameCreator : TframeCreator;
begin
  _frameCreator := TframeCreator( GetCreator(self) );
  if Assigned(_frameCreator) then
    TMyJvWizardInteriorPage(_frameCreator.FindStepByFrame(Self)).HideMessage;
end;

procedure TframeBaseCreator.SetOnExitPage(const Value: TNotifyEvent);
begin
  FOnExitPage := Value;
end;

procedure TframeBaseCreator.SetOnPage(const Value: TNotifyEvent);
begin
  FOnPage := Value;
end;

procedure TframeBaseCreator.SetOnSelectNextPage(const Value: TJvWizardPageClickEvent);
begin
  FOnSelectNextPage := Value;
end;

procedure TframeBaseCreator.StepEnabled(AStepNum: Integer; AEnabled: Boolean);
begin
  TMyJvWizardInteriorPage(Steps.Items[AStepNum]).Enabled := AEnabled;
end;

function TframeBaseCreator.Steps: TJvWizardPageList;
var
  c: TObject;
begin
  c := GetCreator(Self.Parent);
  if Assigned(c) then
    Result := TframeCreator(c).Steps
  else Result := nil;
end;

procedure TframeBaseCreator.Clear;
begin

end;

procedure TframeBaseCreator.ClearReturns;
begin
  SetLength( fReturns, 0 );
end;

procedure TframeBaseCreator.FinishReturnObj(AReturnObject : TObject);
begin
  ClearReturns;
  SetReturn( 0, Integer( AReturnObject ) );
end;

procedure TframeBaseCreator.SetReturnObj(AReturnName: String; AReturnObject : TObject);
begin
  SetReturn( AReturnName, Integer( AReturnObject ) );
end;

procedure TframeBaseCreator.SetReturn(AReturnName: String; AReturnValue: Variant);
begin
  SetReturn( AReturnName, VarToStr(AReturnValue) );
end;

function TframeBaseCreator.ReturnCount : Integer;
begin
  result := Length ( fReturns )
end;

procedure TframeBaseCreator.ReturnDatabaseItemID;
begin
  ClearReturns;
  if AID > -1 then
    SetReturn( 0, AID )
    Else
    SetReturn( 0, DatabaseItem.ID );
end;

procedure TframeBaseCreator.SetReturn( AIndex : integer; AReturnValue: Variant);
begin
  if AIndex >= ReturnCount then
     SetLength( fReturns, AIndex + 1);
  fReturns[ AIndex ] := AReturnValue;
end;

procedure TframeBaseCreator.SetReturn(AReturnName, AReturnValue: String);
var
 i : integer;
  s: string;
begin
  for I := 0 to High(fReturns) do
     if StartWith( String(fReturns[i]), AReturnName+'=')  then
        begin
          s := String(fReturns[i]);
          Delete(s,Pos('=',s)+1,Length(s));
          s:=AReturnValue;
          Exit;
        end;
  SetLength( fReturns, High(fReturns) + 2);
  fReturns[ High(fReturns) ] := AReturnName +'=' +AReturnValue;
end;

procedure TframeBaseCreator.AddReturn( AReturnValue : Variant );
begin
  SetReturn( ReturnCount, AReturnValue );
end;

function TframeBaseCreator.Page(APageNum : Integer): TframeBaseCreator;
begin
  result := TframeCreator( GetCreator(self) ). Page( APageNum );
end;

function TframeBaseCreator.PageReturn(APageNum: Integer; AReturnName: String): Variant;
begin
  result := TframeBaseCreator(TMyJvWizardInteriorPage(Steps.Items[APageNum]).Frame).Return(AReturnName)
end;


function TframeBaseCreator.Return(AReturnName: String): Variant;
var
 i : integer;
begin
  result := null;
  for I := 0 to High(fReturns) do
     if StartWith( String(fReturns[i]), AReturnName+'=')  then
        begin
          result := Copy(fReturns[i],Length(AReturnName)+2,255);
          Exit;
        end;
end;

function TframeBaseCreator.PageReturn(APageNum, AReturnNum: Integer): Variant;
begin
  result := TframeBaseCreator(TMyJvWizardInteriorPage(Steps.Items[APageNum]).Frame).Returns[AReturnNum]
end;

function TframeBaseCreator.BeforeClose: Boolean;
begin
  result := true;
end;

function TframeBaseCreator.BoolPageReturn(APageNum: Integer; AReturnName: String): Boolean;
begin
  result := Boolean(PageReturn(APageNum,AReturnName));
end;

function TframeBaseCreator.StrPageReturn(APageNum: Integer; AReturnName: String): String;
begin
  result := String(PageReturn(APageNum,AReturnName));
end;

function TframeBaseCreator.ThisStep: TJvWizardInteriorPage;
var
  o: TWinControl;
begin
  o := GetCreator(self);
  if Assigned(o) and (o is TframeCreator ) then
    result := TframeCreator( o ). FindStepByFrame( self )
  else Result := nil;
end;

function TframeBaseCreator.IntPageReturn(APageNum, AReturnNum: Integer): Integer;
begin
  result := integer(PageReturn(APageNum, AReturnNum))
end;

function TframeBaseCreator.IntPageReturn(APageNum: Integer; AReturnName: String): Integer;
begin
  result := Integer(PageReturn(APageNum,AReturnName));
end;

function TframeBaseCreator.NextPage: TframeBaseCreator;
begin
  Result := TframeCreator(GetCreator(self)).NextPage(Self);
end;

function TframeBaseCreator.DateTimePageReturn(APageNum: Integer; AReturnName: String): TDateTime;
begin
  result := TDateTime(PageReturn(APageNum,AReturnName));
end;

end.
