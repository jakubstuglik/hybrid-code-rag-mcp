unit FormBasicMain;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs
  , Events, StdCtrls, Buttons, ExtCtrls, ImgList,
  {$IFNDEF NO_CHOICE_PANEL}
  DatabaseItemChoiceFrame,
  {$ENDIF}
  MainDm, System.ImageList
  ;

resourcestring
  cpDefaultLicenceCompany = 'DefaultLicenceCompany';
  cpShowChoicePanel       = 'ShowChoicePanel';
  cpPanelTypeCompany      = 'Company';
  cpDoNotShowClearButton  = 'DoNotShowClearButton';
  cpDoNotSelect           = 'DoNotSelect';
  cpDoNotClear            = 'DoNotClear';


type
  TBasicMainForm = class(TForm)
    ilBasicMain: TImageList;
    procedure FormCreate(Sender: TObject);
    procedure FormKeyPress(Sender: TObject; var Key: Char);
    procedure FormKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
  private
    { Private declarations }
    FChoicePanelSubTypeOridinal : Integer;
    fPasswordAlert: Boolean;
    FFrameOnKeyPress: TKeyPressEvent;
    FFrameOnKeyEvent: TKeyEvent;

    {$IFNDEF NO_CHOICE_PANEL}
    FChoicePanelSwitchParentVisible: Boolean;
    procedure SetChoicePanelType(const Value: TChoicePanelType);
    procedure SetOnChoicePanelDatabaseItemChange(const Value: TOnComboDatabaseItemIDNameChange);
    function GetChoicePanelDatabaseItemChange: TOnComboDatabaseItemIDNameChange;
    function GetChoicePanelType: TChoicePanelType;
    function GetChoicePrompt: String;
    procedure SetChoicePrompt(const Value: String);
    procedure SetChoicePanelSwitchParentVisible(const Value: Boolean);
    {$ENDIF}


    procedure SetFrameOnKeyEvent(const Value: TKeyEvent);
    procedure SetFrameOnKeyPress(const Value: TKeyPressEvent);

  protected
    fdmMain: TdmMain;

    procedure DoShowChoicePanelOwnerSettings(AParams: Array of Variant; Var BDoNotClearChoicePanel : Boolean); virtual;
    function  DoChoicePanelButtonChoiceClick( Var AID : Integer; Var AName : String ) : Boolean; virtual;

    procedure DoChoicePanelDatabaseItemChange; virtual;

    procedure CreateChoicePanelType( AWinControl : TWinControl ); virtual;

  public
    { Public declarations }
    {$IFNDEF NO_CHOICE_PANEL}
    procedure ShowChoicePanel(AParams: Array of Variant; AChangeEvent : TOnComboDatabaseItemIDNameChange);
    procedure ClearChoicePanel(ADoChangeEvent : Boolean = true);
    procedure SetChoicePanelDatabaseItem(AID: Integer; AName: String; ADoChangeEvent : Boolean = true);
    procedure HideChoicePanel;
    function GetChoicePanelDatabaseItemID: Integer;
    function GetChoicePanelDatabaseItemName: String;
    property ChoicePanelType: TChoicePanelType read GetChoicePanelType write  SetChoicePanelType;
    property OnChoicePanelDatabaseItemChange : TOnComboDatabaseItemIDNameChange read GetChoicePanelDatabaseItemChange write SetOnChoicePanelDatabaseItemChange;
    function StrParamChoicePanelType(AChoicePanelType: TChoicePanelType): String;
    function ChoicePanelVisible : Boolean;
    property ChoicePrompt : String read GetChoicePrompt write SetChoicePrompt;
    property ChoicePanelSwitchParentVisible : Boolean read FChoicePanelSwitchParentVisible write SetChoicePanelSwitchParentVisible;
    procedure ButtonClearBehavior_SetToClear;
    procedure ButtonClearBehavior_SetToDefault(ADefaultID : Integer; ADefaultName : String);
    {$ENDIF}
    property ChoicePanelSubType : Integer read FChoicePanelSubTypeOridinal write FChoicePanelSubTypeOridinal;
    procedure SetChoicePanelParent( AWinControl : TWinControl ; AChoicePanelSwitchParentVisible : Boolean = true );

    property PasswordAlert: Boolean read fPasswordAlert write fPasswordAlert;

    procedure PrepareInterface; virtual;
    procedure UnPrepareInterface; virtual;

    property FrameOnKeyPress: TKeyPressEvent read FFrameOnKeyPress write SetFrameOnKeyPress;
    property FrameOnKeyEvent: TKeyEvent read FFrameOnKeyEvent write SetFrameOnKeyEvent;

    procedure ClearKeyEvents;
  end;

var
  BasicMainForm: TBasicMainForm;

implementation

{$R *.dfm}

uses
  KMUtils
  ;

{$region 'resourcestring'}
resourcestring
  btnClearGlyphData =
          '36060000424D3606000000000000360000002800000020000000100000000100' +
          '18000000000000060000EE0E0000EE0E00000000000000000000FF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF3C3C00' +
          '3C3C003C3C003C3C003C3C003C3C003C3C003C3C00FF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FF8484846B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B' +
          '6B6B848484FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF3C3C00' +
          '5B5B005B5B005B5B005B5B005B5B005B5B003C3C003C3C00FF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FF6B6B6BC6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6' +
          'C6C66B6B6B6B6B6BFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF3C3C00' +
          '5B5B005B5B005B5B005B5B005B5B005B5B003C3C003C3C003C3C00FF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FF6B6B6BC6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6' +
          'C6C66B6B6B8484846B6B6BFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF3C3C00' +
          '3C3C005B5B005B5B005B5B005B5B005B5B003C3C003C3C003C3C003C3C00FF00' +
          'FFFF00FFFF00FFFF00FFFF00FF8484846B6B6BC6C6C6C6C6C6C6C6C6C6C6C6C6' +
          'C6C66B6B6B8484848484846B6B6BFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF' +
          '3C3C008080008080008080008080008080008080003C3C003C3C003C3C003C3C' +
          '00FF00FFFF00FFFF00FFFF00FFFF00FF6B6B6BDEDEDEDEDEDEDEDEDEDEDEDEDE' +
          'DEDEDEDEDE6B6B6B8484848484846B6B6BFF00FFFF00FFFF00FFFF00FFFF00FF' +
          'FF00FF3C3C008080008080008080008080008080008080003C3C003C3C003C3C' +
          '003C3C00FF00FFFF00FFFF00FFFF00FFFF00FF6B6B6BDEDEDEDEDEDEDEDEDEDE' +
          'DEDEDEDEDEDEDEDE6B6B6B8484848484846B6B6BFF00FFFF00FFFF00FFFF00FF' +
          'FF00FFFF00FF3C3C008080008080008080008080008080008080003C3C003C3C' +
          '003C3C003C3C00FF00FFFF00FFFF00FFFF00FFFF00FF6B6B6BDEDEDEDEDEDEDE' +
          'DEDEDEDEDEDEDEDEDEDEDE6B6B6B8484848484846B6B6BFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FF3C3C008080008080008080008080008080008080003C3C' +
          '003C3C003C3C00FF00FFFF00FFFF00FFFF00FFFF00FFFF00FF6B6B6BDEDEDEDE' +
          'DEDEDEDEDEDEDEDEDEDEDEDEDEDE6B6B6B8484846B6B6BFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FF3C3C008080008080008080008080008080008080' +
          '003C3C003C3C00FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF6B6B6BDE' +
          'DEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDE6B6B6B6B6B6BFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FF3C3C008080008080008080008080008080' +
          '008080003C3C00FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF6B' +
          '6B6BDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDE6B6B6BFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FF3C3C003C3C003C3C003C3C003C3C' +
          '003C3C003C3C00FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FF8484846B6B6B6B6B6B6B6B6B6B6B6B848484848484FF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF' +
          'FF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00' +
          'FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF' +
          '00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FFFF00FF';
{$endregion}

{$IFNDEF NO_CHOICE_PANEL}
procedure TBasicMainForm.SetChoicePanelDatabaseItem(AID: Integer; AName: String; ADoChangeEvent : Boolean = true);
Begin
  if Assigned(frameChoicePanel) then
    frameChoicePanel.SetChoicePanelDatabaseItem(AID, AName, ADoChangeEvent);
End;

function TBasicMainForm.GetChoicePrompt: String;
begin
  if Assigned(frameChoicePanel) then
    Result := frameChoicePanel.EditLabel
  else
    Result := '';
end;

function TBasicMainForm.StrParamChoicePanelType(AChoicePanelType : TChoicePanelType) : String;
begin
  case AChoicePanelType of
    cptCompany : result := cpPanelTypeCompany;
  end;
  if result <> '' then result := cpShowChoicePanel + '=' + result;
end;

function TBasicMainForm.ChoicePanelVisible : Boolean;
begin
  Result := Assigned(frameChoicePanel) and frameChoicePanel.Visible;
end;

procedure TBasicMainForm.SetOnChoicePanelDatabaseItemChange(const Value: TOnComboDatabaseItemIDNameChange);
begin
  if Assigned(frameChoicePanel)then
    frameChoicePanel.OnChoicePanelDatabaseItemChange := Value
end;

procedure TBasicMainForm.HideChoicePanel;
begin
  if Assigned(frameChoicePanel) then begin
    frameChoicePanel.Visible := false;
    if FChoicePanelSwitchParentVisible then frameChoicePanel.Parent.Visible := frameChoicePanel.Visible;
  end;
end;

procedure TBasicMainForm.ButtonClearBehavior_SetToClear;
begin
  if Assigned(frameChoicePanel) then begin
    frameChoicePanel.DefaultID := -1;
    frameChoicePanel.DefaultName := '(wybierz)';
  end;
end;

procedure TBasicMainForm.ButtonClearBehavior_SetToDefault(ADefaultID: Integer; ADefaultName: String);
begin
  if Assigned(frameChoicePanel) then begin
    frameChoicePanel.DefaultID := ADefaultID;
    frameChoicePanel.DefaultName := ADefaultName;
  end;
end;

procedure TBasicMainForm.ClearChoicePanel(ADoChangeEvent: Boolean);
begin
  if Assigned(frameChoicePanel) then
    frameChoicePanel.ClearChoicePanel(ADoChangeEvent);
end;

procedure TBasicMainForm.SetChoicePanelType(const Value: TChoicePanelType);
begin
  if Assigned(frameChoicePanel) then
    frameChoicePanel.ChoicePanelType := Value;
end;

procedure TBasicMainForm.SetChoicePrompt(const Value: String);
begin
  if Assigned(frameChoicePanel) then
    frameChoicePanel.EditLabel := Value;
end;

procedure TBasicMainForm.ShowChoicePanel(AParams: Array of Variant; AChangeEvent : TOnComboDatabaseItemIDNameChange);
Var
  _dnscb: Boolean;
  _DoNotClearChoicePanel : Boolean;
  _ChoicePanelType: TChoicePanelType;
  _strChoicePanelType, s : String;
begin
  if not GetStrValueFromArrayVarName(cpShowChoicePanel,AParams,_strChoicePanelType) then
             Begin
               if Assigned(frameChoicePanel) then
                 frameChoicePanel.OnChoicePanelDatabaseItemChange := nil;
               Exit;
             End
             Else
             Begin
               if _strChoicePanelType = cpPanelTypeCompany then _ChoicePanelType := cptCompany
               Else _ChoicePanelType := cptUnknown;
               if (_ChoicePanelType <> cptUnknown) and Assigned(frameChoicePanel) then
                frameChoicePanel.OnChoicePanelDatabaseItemChange :=  AChangeEvent;
             End;

  _dnscb := GetStrValueFromArrayVarName(cpDoNotShowClearButton, AParams, s);

  if Assigned(frameChoicePanel) and (frameChoicePanel.Visible) and
     (_ChoicePanelType = frameChoicePanel.ChoicePanelType) and
     not ((not frameChoicePanel.bbClear.Visible) xor _dnscb) then Exit;

  if Assigned(frameChoicePanel) then begin
    frameChoicePanel.bbClear.Visible := not _dnscb;

    frameChoicePanel.Visible := _ChoicePanelType <> cptUnknown;
    frameChoicePanel.ChoicePanelType := _ChoicePanelType;
  end;

  _DoNotClearChoicePanel := false;

  DoShowChoicePanelOwnerSettings( AParams, _DoNotClearChoicePanel );

  if not _DoNotClearChoicePanel then
      _DoNotClearChoicePanel := GetStrValueFromArrayVarName(cpDoNotClear, AParams, s);

  if Assigned(frameChoicePanel) and not _DoNotClearChoicePanel then
    frameChoicePanel.ClearChoicePanel;
end;

function TBasicMainForm.GetChoicePanelDatabaseItemChange: TOnComboDatabaseItemIDNameChange;
begin
  if Assigned(frameChoicePanel) then
    Result := frameChoicePanel.OnChoicePanelDatabaseItemChange
  else Result := nil;
end;

function TBasicMainForm.GetChoicePanelDatabaseItemID: Integer;
begin
  if Assigned(frameChoicePanel) and frameChoicePanel.Visible then
    Result := frameChoicePanel.edDatabaseItemChosen.Tag
  Else
    Result := -1
end;

function TBasicMainForm.GetChoicePanelDatabaseItemName: String;
begin
  if Assigned(frameChoicePanel) and frameChoicePanel.Visible then
    Result := frameChoicePanel.edDatabaseItemChosen.Text
  Else
    Result := ''
end;

procedure TBasicMainForm.SetChoicePanelSwitchParentVisible(const Value: Boolean);
begin
  FChoicePanelSwitchParentVisible := Value
end;

function TBasicMainForm.GetChoicePanelType: TChoicePanelType;
begin
  if Assigned(frameChoicePanel) then
    Result := frameChoicePanel.ChoicePanelType
  else Result := cptUnknown;
end;
{$ENDIF}

//procedure TBasicMainForm.pDatabaseItemChoiceResize(Sender: TObject);
//begin
////  bbClear.Left := panel2.ClientWidth - bbClear.Width - 5;
////  bbChoice.Left := bbbClear.Left - 5 - bitbtnChoice.Width;
////  edDatabaseItemChosen.Left := lbDatabaseItemChosen.Left + lbDatabaseItemChosen.Width + 5;
////  edDatabaseItemChosen.Width :=   bbChoice.Left - 5 - edDatabaseItemChosen.Left;
//
//  bitbtnClear.Left := PanelContent.ClientWidth - bitbtnClear.Width - 5;
//  bitbtnChoice.Left := bitbtnClear.Left - 5 - bitbtnChoice.Width;
//  DatabaseItemEdit.Left := LabelPrompt.Left + LabelPrompt.Width + 5;
//  DatabaseItemEdit.Width :=   bitbtnChoice.Left - 5 - DatabaseItemEdit.Left;
//end;

//procedure TBasicMainForm.bbClearClick(Sender: TObject);
//begin
//  ClearChoicePanel;
//end;

//procedure TBasicMainForm.ClearChoicePanel(ADoChangeEvent : Boolean = true);
//Begin
//  SetChoicePanelDatabaseItem( FDefaultID,  FDefaultName, ADoChangeEvent );
//End;


procedure TBasicMainForm.ClearKeyEvents;
begin
  FrameOnKeyPress:=nil;
  FrameOnKeyEvent:=nil;
end;

procedure TBasicMainForm.CreateChoicePanelType(AWinControl: TWinControl);
begin
  {$IFNDEF NO_CHOICE_PANEL}
  if Assigned(frameChoicePanel) then Exit;

  frameChoicePanel := TframeDatabaseItemChoice.Create(Self, fdmMain, True);
  frameChoicePanel.Parent := AWinControl;
  frameChoicePanel.Align  := alTop;
  frameChoicePanel.Visible := False;
  {$ENDIF}
end;

procedure TBasicMainForm.SetChoicePanelParent(AWinControl: TWinControl; AChoicePanelSwitchParentVisible : Boolean = true);
begin
  {$IFNDEF NO_CHOICE_PANEL}
   ChoicePanelSwitchParentVisible := AChoicePanelSwitchParentVisible;
   CreateChoicePanelType( AWinControl );
  {$ENDIF}
end;


procedure TBasicMainForm.SetFrameOnKeyEvent(const Value: TKeyEvent);
begin
  FFrameOnKeyEvent := Value;
end;

procedure TBasicMainForm.SetFrameOnKeyPress(const Value: TKeyPressEvent);
begin
  FFrameOnKeyPress := Value;
end;

procedure TBasicMainForm.DoChoicePanelDatabaseItemChange;
begin
  {$IFNDEF NO_CHOICE_PANEL}
  if Assigned(frameChoicePanel) and Assigned(frameChoicePanel.OnChoicePanelDatabaseItemChange) then
    frameChoicePanel.OnChoicePanelDatabaseItemChange(Self,
      frameChoicePanel.edDatabaseItemChosen.tag, frameChoicePanel.edDatabaseItemChosen.Text);
  {$ENDIF}
end;

procedure TBasicMainForm.DoShowChoicePanelOwnerSettings(AParams: Array of Variant; Var BDoNotClearChoicePanel : Boolean);
begin
  //
end;



procedure TBasicMainForm.FormCreate(Sender: TObject);
begin
//  To musi byæ (puste), ¿eby FormCreate w klasach potomnych by³ uruchamiany -
// Delphi i tak nie "wchodzi" do tej metody
end;

{$REGION 'KeyEvents'}

procedure TBasicMainForm.FormKeyDown(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if Assigned(FFrameOnKeyEvent) then
    FFrameOnKeyEvent(Self, Key, Shift);
end;

procedure TBasicMainForm.FormKeyPress(Sender: TObject; var Key: Char);
begin
  if Assigned(FFrameOnKeyPress) then
    FFrameOnKeyPress(Self, Key);
end;
{$ENDREGION}

function TBasicMainForm.DoChoicePanelButtonChoiceClick( Var AID : Integer; Var AName : String ) : Boolean;
begin
  AID := 0;
  AName := '';
  result := false;
end;

procedure TBasicMainForm.PrepareInterface;
begin
  Screen.Cursor := crHourGlass;
  {$IFNDEF NO_CHOICE_PANEL}
  HideChoicePanel;
  {$ENDIF}
  Application.ProcessMessages;
end;

procedure TBasicMainForm.UnPrepareInterface;
begin
  Screen.Cursor := crDefault;
  {$IFNDEF NO_CHOICE_PANEL}
  if FChoicePanelSwitchParentVisible and  Assigned(frameChoicePanel) then
    TWinControl(frameChoicePanel.Parent).Visible := frameChoicePanel.Visible;
  {$ENDIF}
  Application.ProcessMessages;
end;

end.
