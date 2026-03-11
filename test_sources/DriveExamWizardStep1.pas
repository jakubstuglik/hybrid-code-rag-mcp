unit DriveExamWizardStep1;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms, Spin,
  ComCtrls, Dialogs, TBaseWizardStep, StdCtrls, BasicClasses, DriveExamClasses,
  Buttons, Person, DriveTrainingClasses, DriveExamDriverListClasses, BaseWizard
  , System.UITypes;

type
  TframeDriveExamWizardStep1 = class(TframeBaseWizardStep)
    lblDescription: TLabel;
    edtDescription: TMemo;
    lblExamDate: TLabel;
    dtpExamDate: TDateTimePicker;
    lblDateInformed: TLabel;
    dtpDateInformed: TDateTimePicker;
    lblDriveExamType: TLabel;
    cbDriveExamType: TComboBox;
    gpExamPlace: TGroupBox;
    Label1: TLabel;
    edPlace: TEdit;
    lblAddress: TLabel;
    edtAddress: TEdit;
    btnChoicePlace: TBitBtn;
    btnDeletePlace: TBitBtn;
    lblZipCode: TLabel;
    edZipCode: TEdit;
    gbLecturerTrainer: TGroupBox;
    edLecturer: TEdit;
    btnChoiceLecturer: TBitBtn;
    rbLecturer: TRadioButton;
    rbTrainer: TRadioButton;
    btnDeleteLecturer: TBitBtn;
    lblExamTime: TLabel;
    dtpExamTime: TDateTimePicker;
    chkSendData: TCheckBox;
    Label2: TLabel;
    cbDriveExamStatus: TComboBox;
    gbStudents: TGroupBox;
    lvDriveExamDriverList: TListView;
    btnChoiceDriverExamDriverList: TBitBtn;
    btnAddDriverExamDriverList: TBitBtn;
    btnDeleteDriverExamDriverList: TBitBtn;
    procedure btnChoiceDriverClick(Sender: TObject);
    procedure btnDeletePlaceClick(Sender: TObject);
    procedure btnChoicePlaceClick(Sender: TObject);
    procedure cbDriveExamTypeChange(Sender: TObject);
    procedure btnChoiceLecturerClick(Sender: TObject);
    procedure btnDeleteLecturerClick(Sender: TObject);
    procedure btnChoiceDriverExamDriverListClick(Sender: TObject);
    procedure btnAddDriverExamDriverListClick(Sender: TObject);
    procedure btnDeleteDriverExamDriverListClick(Sender: TObject);
  private
    fUsePagination: Boolean;
    function GetDriveExam: TDriveExam;
    function CheckLeadingPerson : Boolean;
    function CheckExamType: Boolean;
    procedure DriverDisplay(ADriver: TPerson);

    procedure AddDriveExamDriverList;
    procedure AddDriveExamDriverListItem(A: TDriveExamDriverList);
    procedure ChoiceDriveExamDriverList;
    procedure DeleteDriveExamDriverList;
    procedure FillDriveExamDriverList;
    function CanAddDriveExamDriverList(ADriverId : Integer): Boolean;

    procedure ValidateWarnings;
  protected
    procedure PrepareErrorList; override;
    procedure SetReadOnlyPropertiesMode; override;
    procedure SetReadOnlyEditMode; override;
    procedure SetReadOnlyInsertMode; override;
  public
    procedure AfterSaveInsertMode; override;
    constructor Create(AOwner: TComponent); override;
    procedure PrepareGUI; override;
    procedure ClearUnwantedProperties; override;
    procedure InitializeDatabaseItem(AParams : array of Variant); override;
    procedure PrepareInterface(DatabaseItem: TDatabaseItem; AReadOnly: Boolean;
      AParams: array of Variant); override;
    procedure GetValuesFromInterface(DatabaseItem: TDatabaseItem); override;
    function Validate: boolean; override;

    property DriveExam : TDriveExam read GetDriveExam;
  end;

implementation

{$R *.dfm}

uses Globals, DBClassesDriveExam, DBDictionaryClasses, KMChoiceForms, MainDM,
     GlobalTypes, {KMUtils,} DBTransClasses
     {$IFNDEF PORTALOSK} , LicencesCompanyUnit  {$ENDIF}
     , PersonDocument, Companies, PersonAction, DBClassesDriveExamStatus, KMUICIUtils
     , GlobalList, Generics.Collections ;

{ TframeDriveExamWizardStep1 }

function TframeDriveExamWizardStep1.GetDriveExam: TDriveExam;
begin
  Result := TDriveExam(DatabaseItem);
end;

procedure TframeDriveExamWizardStep1.GetValuesFromInterface(DatabaseItem: TDatabaseItem);
begin
  inherited;
  DriveExam.ExamDate := GetControlDateTimeValue(dtpExamDate);
  DriveExam.ExamDate := StrToDateTime(DateToStr(DriveExam.ExamDate) + ' ' + FormatDateTime('hh:mm:00', GetControlTimeValue(dtpExamTime)));

  DriveExam.Address := GetControlStringValue(edtAddress);
  DriveExam.Description := GetControlStringValue(edtDescription);
  DriveExam.DateInformed := GetControlDateTimeValue(dtpDateInformed);
  DriveExam.DriveExamType.Id := GetListSelectedItemId(cbDriveExamType);
  DriveExam.DriveExamStatus.Id := GetListSelectedItemId(cbDriveExamStatus);
  DriveExam.InstructorData := DriveExam.Person.IDNumberHRSystem + ' ' + DriveExam.Person.FirstName + ' ' + DriveExam.Person.LastName;
  {$IFDEF PORTALOSK}
  DriveExam.OSK_Mode := 1;
  DriveExam.AddHistory := 0;
  if chkSendData.Checked then
    DriveExam.AddHistory := 1;
  {$ELSE}
  DriveExam.OSK_Mode := 0;
  DriveExam.AddHistory := 0;
  {$ENDIF}
  DriveExam.Changed := true;
end;

procedure TframeDriveExamWizardStep1.InitializeDatabaseItem(AParams: array of Variant);
var
  D : TDriveExamDriverList;
  c: TCompany;
begin
  inherited;
  if DriveExam.IsNew then
  begin
    {$IFNDEF PORTALOSK}
      DriveExam.Company.Id := AParams[0];
      DriveExam.CompanyGov.Id := GetLicencesCompanyID;
      DriveExam.ExamID := LicencesCompany.CompanyCode;
    {$ELSE}
      DriveExam.Company.Id := CurrentUserCompany.Id;
      DriveExam.CompanyGov.Id := CurrentUserCompanyGov.Id;
      DriveExam.CompanyGov_ID := CurrentUserCompanyGov.Id;
      DriveExam.ExamID := CurrentUserCompany.CompanyCode;
   {$ENDIF}
    try
      Screen.Cursor := crHourGlass;
      c := TCompany(FindObjectInGlobalList(TObjectList<TDatabaseItem>(CompanyList), DriveExam.Company.Id));
      if not Assigned(c) then begin
        c := TCompany.Create;
        c.ReadFromDatabase(DriveExam.Company.Id);
        c := TCompany(AddObjectToGlobalList(TObjectList<TDatabaseItem>(CompanyList), TDatabaseItem(c)));
      end;
      DriveExam.Company.Assign(c);
//      DriveExam.User.Assign(CurrentUser);
      DriveExam.User_ID := CurrentUser.Id;

    finally
      Screen.Cursor := crDefault;
    end;
  end
  else
  begin
    {$IFDEF PORTALOSK}
    DriveExam.CompanyGov_ID := CurrentUserCompanyGov.Id;
    {$ENDIF}

    try
      Screen.Cursor := crHourGlass;
      //DriveExam.User.Assign(CurrentUser);
      DriveExam.User_Id := CurrentUser.Id;
      DriveExam.ReadPlaceFromDatabase;

      //DriveExam.ReadCompanyFromDatabase;
      c := TCompany(FindObjectInGlobalList(TObjectList<TDatabaseItem>(CompanyList), DriveExam.Company_ID));
      if not Assigned(c) then begin
        c := TCompany.Create;
        c.ReadFromDatabase(DriveExam.Company_ID);
        c := TCompany(AddObjectToGlobalList(TObjectList<TDatabaseItem>(CompanyList), TDatabaseItem(c)));
      end;
      DriveExam.Company.Assign(c);

      c := TCompany(FindObjectInGlobalList(TObjectList<TDatabaseItem>(CompanyList), DriveExam.CompanyGov_ID));
      if not Assigned(c) then begin
        c := TCompany.Create;
        c.ReadFromDatabase(DriveExam.CompanyGov_ID);
        c := TCompany(AddObjectToGlobalList(TObjectList<TDatabaseItem>(CompanyList), TDatabaseItem(c)));
      end;
      DriveExam.CompanyGov.Assign(c);

      DriveExam.ReadDriverFromDatabase;
      DriveExam.ReadDriveExamTypeFromDatabase;
      DriveExam.ReadDriveExamStatusFromDatabase;
      DriveExam.ReadDriveExamDriverList;
    finally
      Screen.Cursor := crDefault;
    end;

    {$IFDEF PORTALOSK}
    for D in DriveExam.DriveExamDriverList do
      D.Changed := false;
    {$ENDIF}


    {$IFNDEF PORTALOSK}
    DriveExam.InitializeMasterDriveExam(DriveExam);
    DriveExam.Master.Master_ID := DriveExam.Id;
    DriveExam.Master.Id := 0;
    //DriveExam.Master.User.Assign(CurrentUser);
    DriveExam.Master.User_Id := CurrentUser.Id;
    DriveExam.Master.AddHistory := 0;
    DriveExam.Master.OSK_Mode := 0;
    DriveExam.Master.ExamID := DriveExam.ExamID;
    DriveExam.Master.ChangeDesc := 'zmiana';
    DriveExam.Master.Changed := true;

    for D in DriveExam.Master.DriveExamDriverList do begin
      D.Id := 0;
      D.Changed := true;
    end;
    {$ENDIF}
  end;
end;

procedure TframeDriveExamWizardStep1.PrepareErrorList;
begin
  inherited;
  Errors.Add(gpExamPlace, 'Miejsce egazminu|Nale¿y wybraæ miejsce egzaminu!|0');
  Errors.Add(dtpExamDate, 'Data egazminu|Nale¿y wype³niæ datê egzaminu!|0');
  Errors.Add(dtpExamTime, 'Godzina egazminu|Nale¿y wype³niæ godzinê egazminu!|0');
  Errors.Add(edLecturer, 'Wyk³adowca/Instruktor|Nale¿y wybraæ Wyk³adowcê/Intruktora z odpowiednimi urprawnieniami!|0');
  Errors.Add(cbDriveExamType, 'Rodzaj egazminu|Firma nie ma uprawnieñ do prowadzenia egzaminu danej kategorii!!');
  Errors.Add(cbDriveExamStatus, 'Status egzaminu|Nale¿y wybraæ status egzaminu!|0')
end;

procedure TframeDriveExamWizardStep1.PrepareGUI;
begin
  inherited;
  TDBDriveExamType.ReadListFromDatabase(cbDriveExamType.Items, {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF});
  TDBDriveExamStatusActions.GetDriveExamStatus(cbDriveExamStatus.Items, {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF}, False);

  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.AddDriveExamDriverList;
var
  A : TDriveExamDriverList;
  B : TPerson;
begin
  B := TPerson.Create;
  B.PersonType_Id := ptStudent;
  try
    if B.UserInsert([False, true, 'Company_ID=' + IntToStr(DriveExam.Company_ID)]) then  begin
      A := TDriveExamDriverList.Create(DriveExam);
      A.Driver.ReadFromDatabase(B.Id);
      A.Changed := true;

      AddDriveExamDriverListItem(A);
      DriveExam.DriveExamDriverList.Add(A);
    end;
  finally
    B.Free;
  end;
end;

procedure TframeDriveExamWizardStep1.AddDriveExamDriverListItem(
  A: TDriveExamDriverList);
begin
  with lvDriveExamDriverList.Items.Add do
    begin
     Caption := A.Driver.FirstName;
     SubItems.Add(A.Driver.LastName);
     Data := A;
   end;
end;

procedure TframeDriveExamWizardStep1.AfterSaveInsertMode;
var
  Script : string;
  Params : string;
begin
  inherited;
  Script := '';
  Params := '';
  {$IFNDEF PORTALOSK}
  Params := Format('@Reference_Id=%d', [DriveExam.Id]);

  Script := 'exec [dbo].[LPC_AddDriveExamDriverListToChild] ' + Params;
  TDBTransActions.TransSimpleScript(Script, '',  {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF});
  {$ENDIF}
end;

procedure TframeDriveExamWizardStep1.btnAddDriverExamDriverListClick(
  Sender: TObject);
begin
  AddDriveExamDriverList;
  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.btnChoiceDriverClick(Sender: TObject);
var
  Driver_id : Integer;
begin
  Driver_id := DriveExam.Person.Id;
  if KMChoiceForms.ChoiceDriver(Driver_id, Integer(ptTrainer), 0, {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF}) then begin
    DriveExam.Person.ReadFromDatabase(Driver_id);
    DriveExam.Person.Id := Driver_id;
    DriverDisplay(DriveExam.Person);
  end
end;

procedure TframeDriveExamWizardStep1.btnChoiceDriverExamDriverListClick(
  Sender: TObject);
begin
  {$IFNDEF PORTALOSK}
  dmMainGlobal.TCPIPServerMethods.PrepareDrivers;
  {$ENDIF}
  ChoiceDriveExamDriverList;
  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.btnChoiceLecturerClick(Sender: TObject);
Var
  Driver_id : Integer;
  PersonType : TPersonType;
begin

  if rbLecturer.Checked then
    PersonType := ptLecturer
  else
  if rbTrainer.Checked then
    PersonType := ptTrainer
  else
    PersonType := ptTrainer;

  Driver_id := DriveExam.Person.Id;
  if KMChoiceForms.ChoiceDriver(Driver_id, Integer(PersonType), DriveExam.Company.Id,
       DriveExam.dmMain, nil, false, fUsePagination) then begin
    try
      Screen.Cursor := crHourGlass;
      DriveExam.Person.ReadFromDatabase(Driver_id);
      DriveExam.Person.Id := Driver_id;
      DriverDisplay(DriveExam.Person);
    finally
      Screen.Cursor := crDefault;
    end;
  end;

  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.btnChoicePlaceClick(Sender: TObject);
var
  PlaceId : Integer;
  OutArray : PVariant;
begin
  New(OutArray);
  try
    if KMChoiceForms.ChoiceCompanyAddress(PlaceId, DriveExam.Company.Id, 0, {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF}, OutArray) then  begin
      try
        Screen.Cursor := crHourGlass;
        DriveExam.Place.ReadFromDatabase(PlaceId);
        DriveExam.Address := VarArrayGet(OutArray^, [0]);
        DriveExam.ZipCode := VarArrayGet(OutArray^, [1]);

        edPlace.Text := DriveExam.Place.Name;
        edtAddress.Text := DriveExam.Address;
        edZipCode.Text := DriveExam.ZipCode;
      finally
        Screen.Cursor := crDefault;
      end;
    end;
  finally
    Dispose(OutArray);
  end;
end;

procedure TframeDriveExamWizardStep1.btnDeleteDriverExamDriverListClick(
  Sender: TObject);
begin
  DeleteDriveExamDriverList;
  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.btnDeleteLecturerClick(Sender: TObject);
begin
  if (MessageDlg('Usun¹æ wpis?', mtConfirmation, [mbYes, mbNo], 0) = mrYes) then
    begin
      DriveExam.Person.Id := 0;
      edLecturer.Text := '';
    end;

  ValidateWarnings;
end;

procedure TframeDriveExamWizardStep1.btnDeletePlaceClick(Sender: TObject);
begin
  if (MessageDlg('Usun¹æ wpis?', mtConfirmation, [mbYes, mbNo], 0) = mrYes) then
    begin
      DriveExam.Place.Id := 0;
      edPlace.Text := '';
      edtAddress.Text := '';
      edZipCode.Text := '';
    end;
end;

function TframeDriveExamWizardStep1.CanAddDriveExamDriverList(
  ADriverId: Integer): Boolean;
var D : TDriveExamDriverList;
begin
  Result := True;

  for D in DriveExam.DriveExamDriverList do
    if (not D.Deleted) and (D.Driver.Id = ADriverId) then begin
      Result := False;
      Break;
    end;
end;

procedure TframeDriveExamWizardStep1.cbDriveExamTypeChange(Sender: TObject);
var
  DictionaryDatabaseItem : TDriveExamType;
  IsDefaultDescription : boolean;
  i : integer;
begin
  inherited;

  IsDefaultDescription := false;
  for i := 0 to cbDriveExamType.Items.Count - 1 do begin
    DictionaryDatabaseItem := TDriveExamType(cbDriveExamType.Items.Objects[i]);
    if edtDescription.Text = DictionaryDatabaseItem.Description then begin
      IsDefaultDescription := true;
      break;
    end;
  end;

  DriveExam.DriveExamType.Id := GetListSelectedItemId(cbDriveExamType);
  DriveExam.DriveExamType.ReadFromDatabase(DriveExam.DriveExamType.Id);

  if (edtDescription.Text = '') or (IsDefaultDescription) then
    edtDescription.Text := DriveExam.DriveExamType.Description;

  ValidateWarnings;
end;

function TframeDriveExamWizardStep1.CheckLeadingPerson: Boolean;
var
  D : TPersonDocument;
  chkDriveTrainingType : Boolean;
  //chkCompany : Boolean;
  //chkUnemployed : Boolean;
begin
  chkDriveTrainingType := False;
  //chkCompany := False;
  //chkUnemployed := True;

  if DriveExam.Person.PersonDocumentList.Count = 0 then
    DriveExam.Person.ReadFromDatabase(DriveExam.Person.Id);

  for D in DriveExam.Person.PersonDocumentList do begin
    chkDriveTrainingType :=
       (D.PersonDocumentActionType_ID = DriveExam.DriveExamType.Id + 100)
       and (Int(D.Date) <= Int(dtpExamDate.Date))
       and ((Int(D.ValidTo) >= Int(dtpExamDate.Date)) or (Int(D.ValidTo) = 0));

    if chkDriveTrainingType then
      Break;
  end;

//nie sprawdzamy dat zatrudnienia instruktora/wyk³adowcy,
//tylko bierzemy pod uwagê daty uprawnieñ (kategorii)
//  for P in DriveExam.Person.PersonActionList do begin
//    chkCompany :=
//       (P.Company_ID = DriveExam.Company.ID)
//       and (Int(P.Date) <= Int(dtpExamDate.Date))
//       and ((Int(P.ValidTo) >= Int(dtpExamDate.Date)) or (Int(P.ValidTo) = 0));
//
//    if chkCompany then
//      Break;
//  end;
//
//  for P in DriveExam.Person.PersonActionList do begin
//    if P.Company_ID > 0 then
//    begin
//      chkUnemployed := False;
//      Break;
//    end;
//  end;

  Result := chkDriveTrainingType; // and (chkCompany or chkUnemployed);
end;

procedure TframeDriveExamWizardStep1.ChoiceDriveExamDriverList;
var
  A : TDriveExamDriverList;
  DriverIdList : TList;
  I : Integer;
begin
  //DriverIdList := TList.Create;
  DriverIdList := nil;
  try
    if KMChoiceForms.ChoiceDriver(DriverIdList, Integer(ptStudent), DriveExam.Company.Id,
         DriveExam.dmMain, nil, True, fUsePagination)
         and (DriverIdList.Count > 0) then
      try
        if Assigned(DriverIdList) then begin
          Screen.Cursor := crHourGlass;
          for I := 0 to DriverIdList.Count -1 do begin
            if not CanAddDriveExamDriverList(Integer(DriverIdList[I])) then
              Continue;

            A := TDriveExamDriverList.Create(DriveExam);
            A.Driver.ReadFromDatabase(Integer(DriverIdList[I]));
            A.Changed := true;

            AddDriveExamDriverListItem(A);
            DriveExam.DriveExamDriverList.Add(A);
          end;
        end;
      finally
        Screen.Cursor := crDefault;
      end;
  finally
    DriverIdList.Free;
  end;
end;

function  TframeDriveExamWizardStep1.CheckExamType: Boolean;
var
  CD : TCompanyDocument;
begin
  Result := false;
  for CD in DriveExam.Company.CompanyDocuments do begin
    if (CD.CompanyDocCategoryType_ID = DriveExam.DriveExamType.Id)
       and (Int(CD.Date) <= Int(dtpExamDate.Date))
       and ((Int(CD.ValidTo) >= Int(dtpExamDate.Date)) or (Int(CD.ValidTo) = 0)) then
     begin
       Result := True;
       Break;
     end;
  end;
end;

procedure TframeDriveExamWizardStep1.ClearUnwantedProperties;
begin
  inherited;
end;

constructor TframeDriveExamWizardStep1.Create(AOwner: TComponent);
begin
  inherited;
  StepShowCaption := False;
  {$IFDEF PORTALOSK}
  fUsePagination := True;
  {$ELSE}
  fUsePagination := False;
  {$ENDIF}
end;

procedure TframeDriveExamWizardStep1.DeleteDriveExamDriverList;
var
  A : TDriveExamDriverList;
begin
  if lvDriveExamDriverList.ItemIndex < 0 then
    Exit;

  if MsgAsk('Czy na pewno?') = ID_YES then
    begin
      A := TDriveExamDriverList(lvDriveExamDriverList.Items[lvDriveExamDriverList.ItemIndex].Data);
      A.Deleted := True;
      lvDriveExamDriverList.Items[lvDriveExamDriverList.ItemIndex].Delete;
    end;
end;

procedure TframeDriveExamWizardStep1.DriverDisplay(ADriver: TPerson);
begin
  with ADriver do
  if (FirstName <> '') and (LastName <> '') then
    edLecturer.Text := FirstName + ' ' + LastName
  else
    edLecturer.Text := '';
end;

procedure TframeDriveExamWizardStep1.FillDriveExamDriverList;
var
  I :integer;
begin
  for I := 0 to DriveExam.DriveExamDriverList.Count - 1 do
  with lvDriveExamDriverList.Items.Add do
    begin
     Caption := DriveExam.DriveExamDriverList[i].Driver.FirstName;
     SubItems.Add(DriveExam.DriveExamDriverList[i].Driver.LastName);

     Data := DriveExam.DriveExamDriverList[i];
   end;
end;

procedure TframeDriveExamWizardStep1.PrepareInterface(DatabaseItem: TDatabaseItem;
  AReadOnly: Boolean; AParams: array of Variant);
begin
  inherited;

  {$IFDEF PORTALOSK}
    lblDateInformed.Hide;
    dtpDateInformed.Hide;
  {$ELSE}
    chkSendData.Hide;
  {$ENDIF}

  rbLecturer.Checked := (DriveExam.Person.PersonType_ID in [ptDriver, ptLecturer]) or (DriveExam.Person.Id = 0);
  rbTrainer.Checked := DriveExam.Person.PersonType_ID = ptTrainer;

  FillControl(dtpExamDate, DriveExam.ExamDate);
  FillControl(dtpExamTime, DriveExam.ExamDate);
  FillControl(edtAddress, DriveExam.Address);
  FillControl(edtDescription, DriveExam.Description);
  FillControl(dtpDateInformed, DriveExam.DateInformed);
  FillControl(cbDriveExamType, DriveExam.DriveExamType.Id);
  FillControl(edPlace, DriveExam.Place.Name);
  FillControl(edZipCode, DriveExam.ZipCode);
  FillControl(cbDriveExamStatus, DriveExam.DriveExamStatus.Id);
  DriverDisplay(DriveExam.Person);

  FillDriveExamDriverList;
end;

procedure TframeDriveExamWizardStep1.SetReadOnlyPropertiesMode;
begin
  inherited;
  SetReadOnlyControl(dtpExamDate);
  SetReadOnlyControl(dtpExamTime);
  SetReadOnlyControl(edtAddress);
  SetReadOnlyControl(edtDescription);
  SetReadOnlyControl(dtpDateInformed);
  SetReadOnlyControl(cbDriveExamType);
  SetReadOnlyControl(edLecturer);
  SetReadOnlyControl(edPlace);
  SetReadOnlyControl(edZipCode);
  SetReadOnlyControl(rbLecturer);
  SetReadOnlyControl(rbTrainer);
  SetReadOnlyControl(cbDriveExamStatus);
  SetReadOnlyControl(btnChoiceDriverExamDriverList);
  SetReadOnlyControl(btnAddDriverExamDriverList);
  SetReadOnlyControl(btnDeleteDriverExamDriverList);
  btnChoiceLecturer.Enabled := false;
  btnChoicePlace.Enabled := false;
  btnDeletePlace.Enabled := false;
  btnDeleteLecturer.Enabled := false;
  chkSendData.Hide;
end;

procedure TframeDriveExamWizardStep1.SetReadOnlyEditMode;
begin
  inherited;
  SetReadOnlyControl(edLecturer);
  SetReadOnlyControl(edPlace);
  SetReadOnlyControl(edPlace);
  SetReadOnlyControl(edZipCode);
  SetReadOnlyControl(edtAddress);
end;

procedure TframeDriveExamWizardStep1.SetReadOnlyInsertMode;
begin
  inherited;
  SetReadOnlyEditMode;
end;

function TframeDriveExamWizardStep1.Validate: boolean;
begin
  CheckFieldValid(gpExamPlace, GetControlStringValue(edPlace) <> '');
  CheckFieldValid(dtpExamDate, GetControlDateTimeValue(dtpExamDate) > 0);
  CheckFieldValid(dtpExamTime, GetControlDateTimeValue(dtpExamTime) > 0);
  CheckFieldValid(cbDriveExamStatus, GetListSelectedItemId(cbDriveExamStatus) > 0);

  if edLecturer.Text <> '' then
    CheckFieldValid(edLecturer, CheckLeadingPerson)
  else
    CheckFieldValid(edLecturer, edLecturer.Text = '');

  //if GetListSelectedItemId(cbDriveExamType) > 0 then // PN: pole powinno byæ obowi¹zkowe
  CheckFieldValid(cbDriveExamType, CheckExamType);

  Result := inherited;
end;

procedure TframeDriveExamWizardStep1.ValidateWarnings;
var
  A : TDriveExamDriverList;
  DriveTrainingType : Integer;
begin
  with TfrmBaseWizard(wizard) do
  begin
    ClearMessages;

    if DriveExam.Person.Id = 0 then
      AddMessageWarning('Nie zosta³ wybrany instruktor/wyk³adowca!');

    for A in DriveExam.DriveExamDriverList do
    begin
      if A.Deleted or (DriveExam.DriveExamType.Id = 0) then
        Continue;

      DriveTrainingType := TDBDriveExamActions.DriverLastDriveTrainingId(A.Driver.Id, {$IFNDEF PORTALOSK} dmMainGlobal {$ELSE} dmMainOSK  {$ENDIF});

      if (DriveTrainingType <> DriveExam.DriveExamType.Id) then
        AddMessageWarning(Format('Kursant %s nie uczêszcza³ na kurs kategorii wybranej w egzaminie!', [A.Driver.FirstName + ' ' + A.Driver.LastName]));
    end;
  end;
end;

end.
