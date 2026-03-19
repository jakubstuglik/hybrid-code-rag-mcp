unit JobWizardStep1;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  ComCtrls, Dialogs, WizardBaseFrame, StdCtrls, JobOrderClasses, VehicleClasses,
  Buttons, DriverClasses, RouteClasses, BaseWizard, DateTimePicker,
  System.UITypes;

type
  TframeJobWizardStep1 = class(TWizardBaseFrame)
    lblDescription: TLabel;
    edtDescription: TMemo;
    lblPickupDate: TLabel;
    dtpPickupDate: TDateTimePicker;
    lblPickupTime: TLabel;
    dtpPickupTime: TDateTimePicker;
    lblDeliveryDate: TLabel;
    dtpDeliveryDate: TDateTimePicker;
    lblJobType: TLabel;
    cbJobType: TComboBox;
    gpPickupAddress: TGroupBox;
    lblPickupStreet: TLabel;
    edPickupStreet: TEdit;
    lblPickupCity: TLabel;
    edPickupCity: TEdit;
    lblPickupPostCode: TLabel;
    edPickupPostCode: TEdit;
    btnChoosePickupAddress: TBitBtn;
    btnClearPickupAddress: TBitBtn;
    gpDeliveryAddress: TGroupBox;
    lblDeliveryStreet: TLabel;
    edDeliveryStreet: TEdit;
    lblDeliveryCity: TLabel;
    edDeliveryCity: TEdit;
    lblDeliveryPostCode: TLabel;
    edDeliveryPostCode: TEdit;
    btnChooseDeliveryAddress: TBitBtn;
    btnClearDeliveryAddress: TBitBtn;
    gbAssignedVehicle: TGroupBox;
    edVehiclePlate: TEdit;
    btnChooseVehicle: TBitBtn;
    btnClearVehicle: TBitBtn;
    gbAssignedDriver: TGroupBox;
    edDriverName: TEdit;
    btnChooseDriver: TBitBtn;
    btnClearDriver: TBitBtn;
    lblPayloadKg: TLabel;
    edPayloadKg: TEdit;
    lblCustomerRef: TLabel;
    edCustomerRef: TEdit;
    lblPriority: TLabel;
    cbPriority: TComboBox;
    lvAdditionalStops: TListView;
    btnAddStop: TBitBtn;
    btnRemoveStop: TBitBtn;
    chkRequiresSignature: TCheckBox;
    chkHazardousGoods: TCheckBox;
    procedure btnChooseVehicleClick(Sender: TObject);
    procedure btnClearVehicleClick(Sender: TObject);
    procedure btnChooseDriverClick(Sender: TObject);
    procedure btnClearDriverClick(Sender: TObject);
    procedure btnChoosePickupAddressClick(Sender: TObject);
    procedure btnClearPickupAddressClick(Sender: TObject);
    procedure btnChooseDeliveryAddressClick(Sender: TObject);
    procedure btnClearDeliveryAddressClick(Sender: TObject);
    procedure btnAddStopClick(Sender: TObject);
    procedure btnRemoveStopClick(Sender: TObject);
    procedure cbJobTypeChange(Sender: TObject);
  private
    FVehicleId: Integer;
    FDriverId: Integer;
    function GetJobOrder: TJobOrder;
    function CheckVehicleCapacity: Boolean;
    function CheckDriverAvailability: Boolean;
    procedure DisplayVehicle(AVehicle: TVehicleRecord);
    procedure DisplayDriver(ADriver: TDriverRecord);
    procedure AddAdditionalStop;
    procedure AddAdditionalStopItem(AStop: TRouteStop);
    procedure RemoveAdditionalStop;
    procedure FillAdditionalStopList;
    function CanAddStop(const AAddress: string): Boolean;
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
    procedure InitializeDatabaseItem(AParams: array of Variant); override;
    procedure PrepareInterface(DatabaseItem: TDatabaseItem; AReadOnly: Boolean;
      AParams: array of Variant); override;
    procedure GetValuesFromInterface(DatabaseItem: TDatabaseItem); override;
    function Validate: boolean; override;

    property JobOrder: TJobOrder read GetJobOrder;
  end;

implementation

{$R *.dfm}

uses Globals, DBClassesJobOrder, DBDictionaryClasses, ChoiceForms, MainDataMod,
     GlobalTypes, DBTransClasses, DriverClasses, VehicleClasses;

{ TframeJobWizardStep1 }

function TframeJobWizardStep1.GetJobOrder: TJobOrder;
begin
  Result := TJobOrder(DatabaseItem);
end;

procedure TframeJobWizardStep1.GetValuesFromInterface(DatabaseItem: TDatabaseItem);
begin
  inherited;
  JobOrder.PickupDate := GetControlDateTimeValue(dtpPickupDate);
  JobOrder.PickupDate := StrToDateTime(
    DateToStr(JobOrder.PickupDate) + ' ' +
    FormatDateTime('hh:mm:00', GetControlTimeValue(dtpPickupTime)));

  JobOrder.DeliveryDate := GetControlDateTimeValue(dtpDeliveryDate);
  JobOrder.Description  := GetControlStringValue(edtDescription);
  JobOrder.CustomerRef  := GetControlStringValue(edCustomerRef);
  JobOrder.PayloadKg    := StrToFloatDef(Trim(edPayloadKg.Text), 0);
  JobOrder.JobType.Id   := GetListSelectedItemId(cbJobType);
  JobOrder.Priority     := cbPriority.ItemIndex + 1;
  JobOrder.PickupStreet := GetControlStringValue(edPickupStreet);
  JobOrder.PickupCity   := GetControlStringValue(edPickupCity);
  JobOrder.PickupPostCode := GetControlStringValue(edPickupPostCode);
  JobOrder.DeliveryStreet := GetControlStringValue(edDeliveryStreet);
  JobOrder.DeliveryCity   := GetControlStringValue(edDeliveryCity);
  JobOrder.DeliveryPostCode := GetControlStringValue(edDeliveryPostCode);
  JobOrder.RequiresSignature := chkRequiresSignature.Checked;
  JobOrder.HazardousGoods    := chkHazardousGoods.Checked;
  JobOrder.VehicleId := FVehicleId;
  JobOrder.DriverId  := FDriverId;
  JobOrder.Changed := true;
end;

procedure TframeJobWizardStep1.InitializeDatabaseItem(AParams: array of Variant);
var
  V: TVehicleRecord;
  D: TDriverRecord;
begin
  inherited;
  if JobOrder.IsNew then
  begin
    JobOrder.DepotId  := dmFleet.GetDefaultDepotId;
    JobOrder.Priority := 2;  // Normal priority by default
    try
      Screen.Cursor := crHourGlass;
      // Pre-fill depot address as default pickup
      dmFleet.LoadDepotAddress(JobOrder.DepotId,
        JobOrder.PickupStreet, JobOrder.PickupCity, JobOrder.PickupPostCode);
    finally
      Screen.Cursor := crDefault;
    end;
  end
  else
  begin
    try
      Screen.Cursor := crHourGlass;
      JobOrder.ReadPickupFromDatabase;
      JobOrder.ReadDeliveryFromDatabase;

      if JobOrder.VehicleId > 0 then
      begin
        V := TVehicleRecord.Create;
        try
          V.ReadFromDatabase(JobOrder.VehicleId);
          DisplayVehicle(V);
          FVehicleId := V.VehicleId;
        finally
          V.Free;
        end;
      end;

      if JobOrder.DriverId > 0 then
      begin
        D := TDriverRecord.Create;
        try
          D.ReadFromDatabase(JobOrder.DriverId);
          DisplayDriver(D);
          FDriverId := D.DriverId;
        finally
          D.Free;
        end;
      end;

      JobOrder.ReadAdditionalStopsFromDatabase;
      JobOrder.ReadJobTypeFromDatabase;
    finally
      Screen.Cursor := crDefault;
    end;
  end;
end;

procedure TframeJobWizardStep1.PrepareErrorList;
begin
  inherited;
  Errors.Add(gpPickupAddress, 'Pickup Address|Please select or enter a pickup address.|0');
  Errors.Add(gpDeliveryAddress, 'Delivery Address|Please select or enter a delivery address.|0');
  Errors.Add(dtpPickupDate, 'Pickup Date|Please specify the pickup date and time.|0');
  Errors.Add(dtpDeliveryDate, 'Delivery Date|Delivery date must be after pickup date.|0');
  Errors.Add(cbJobType, 'Job Type|Please select a job type.|0');
  Errors.Add(edPayloadKg, 'Payload Weight|Payload exceeds the selected vehicle capacity.|0');
end;

procedure TframeJobWizardStep1.PrepareGUI;
begin
  inherited;
  TDBJobType.ReadListFromDatabase(cbJobType.Items, dmFleet);
  cbPriority.Items.Clear;
  cbPriority.Items.Add('Low');
  cbPriority.Items.Add('Normal');
  cbPriority.Items.Add('High');
  cbPriority.Items.Add('Urgent');
  cbPriority.ItemIndex := 1;

  ValidateWarnings;
end;

procedure TframeJobWizardStep1.AddAdditionalStop;
var
  Stop: TRouteStop;
  Addr: string;
begin
  Addr := '';
  if ChoiceForms.ChoiceAddress(Addr, 0, dmFleet) then
  begin
    if not CanAddStop(Addr) then
    begin
      ShowMessage('This address is already in the stop list.');
      Exit;
    end;
    Stop := TRouteStop.Create(JobOrder);
    Stop.Address := Addr;
    Stop.StopOrder := JobOrder.AdditionalStops.Count + 1;
    Stop.Changed := true;
    AddAdditionalStopItem(Stop);
    JobOrder.AdditionalStops.Add(Stop);
  end;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.AddAdditionalStopItem(AStop: TRouteStop);
begin
  with lvAdditionalStops.Items.Add do
  begin
    Caption := IntToStr(AStop.StopOrder);
    SubItems.Add(AStop.Address);
    Data := AStop;
  end;
end;

procedure TframeJobWizardStep1.AfterSaveInsertMode;
var
  Params: string;
begin
  inherited;
  Params := Format('@JobId=%d', [JobOrder.Id]);
  TDBTransActions.TransSimpleScript(
    'exec [dbo].[ORD_CreateJobOrder_PostProcess] ' + Params, '', dmFleet);
end;

procedure TframeJobWizardStep1.btnAddStopClick(Sender: TObject);
begin
  AddAdditionalStop;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.btnChooseVehicleClick(Sender: TObject);
var
  VehicleId: Integer;
begin
  VehicleId := FVehicleId;
  if ChoiceForms.ChoiceVehicle(VehicleId, dmFleet) then
  begin
    try
      Screen.Cursor := crHourGlass;
      var V := TVehicleRecord.Create;
      try
        V.ReadFromDatabase(VehicleId);
        DisplayVehicle(V);
        FVehicleId := VehicleId;
      finally
        V.Free;
      end;
    finally
      Screen.Cursor := crDefault;
    end;
  end;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.btnClearVehicleClick(Sender: TObject);
begin
  if MsgAsk('Clear vehicle assignment?') = ID_YES then
  begin
    FVehicleId := 0;
    edVehiclePlate.Text := '';
  end;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.btnChooseDriverClick(Sender: TObject);
var
  DriverId: Integer;
begin
  DriverId := FDriverId;
  if ChoiceForms.ChoiceDriver(DriverId, dmFleet) then
  begin
    try
      Screen.Cursor := crHourGlass;
      var D := TDriverRecord.Create;
      try
        D.ReadFromDatabase(DriverId);
        DisplayDriver(D);
        FDriverId := DriverId;
      finally
        D.Free;
      end;
    finally
      Screen.Cursor := crDefault;
    end;
  end;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.btnClearDriverClick(Sender: TObject);
begin
  if MsgAsk('Clear driver assignment?') = ID_YES then
  begin
    FDriverId := 0;
    edDriverName.Text := '';
  end;
  ValidateWarnings;
end;

procedure TframeJobWizardStep1.btnChoosePickupAddressClick(Sender: TObject);
var
  Addr, City, PostCode: string;
begin
  if ChoiceForms.ChoiceFullAddress(Addr, City, PostCode, dmFleet) then
  begin
    edPickupStreet.Text   := Addr;
    edPickupCity.Text     := City;
    edPickupPostCode.Text := PostCode;
  end;
end;

procedure TframeJobWizardStep1.btnClearPickupAddressClick(Sender: TObject);
begin
  if MsgAsk('Clear pickup address?') = ID_YES then
  begin
    edPickupStreet.Text   := '';
    edPickupCity.Text     := '';
    edPickupPostCode.Text := '';
  end;
end;

procedure TframeJobWizardStep1.btnChooseDeliveryAddressClick(Sender: TObject);
var
  Addr, City, PostCode: string;
begin
  if ChoiceForms.ChoiceFullAddress(Addr, City, PostCode, dmFleet) then
  begin
    edDeliveryStreet.Text   := Addr;
    edDeliveryCity.Text     := City;
    edDeliveryPostCode.Text := PostCode;
  end;
end;

procedure TframeJobWizardStep1.btnClearDeliveryAddressClick(Sender: TObject);
begin
  if MsgAsk('Clear delivery address?') = ID_YES then
  begin
    edDeliveryStreet.Text   := '';
    edDeliveryCity.Text     := '';
    edDeliveryPostCode.Text := '';
  end;
end;

procedure TframeJobWizardStep1.btnRemoveStopClick(Sender: TObject);
begin
  RemoveAdditionalStop;
  ValidateWarnings;
end;

function TframeJobWizardStep1.CanAddStop(const AAddress: string): Boolean;
var
  S: TRouteStop;
begin
  Result := True;
  for S in JobOrder.AdditionalStops do
    if (not S.Deleted) and SameText(S.Address, AAddress) then
    begin
      Result := False;
      Break;
    end;
end;

procedure TframeJobWizardStep1.cbJobTypeChange(Sender: TObject);
var
  JobType: TJobType;
  I: Integer;
begin
  inherited;
  JobOrder.JobType.Id := GetListSelectedItemId(cbJobType);
  JobOrder.JobType.ReadFromDatabase(JobOrder.JobType.Id);
  if edtDescription.Text = '' then
    edtDescription.Text := JobOrder.JobType.DefaultDescription;

  // Adjust hazardous goods checkbox visibility based on job type
  for I := 0 to cbJobType.Items.Count - 1 do
  begin
    JobType := TJobType(cbJobType.Items.Objects[I]);
    if JobType.Id = JobOrder.JobType.Id then
    begin
      chkHazardousGoods.Visible := JobType.AllowsHazardousGoods;
      Break;
    end;
  end;

  ValidateWarnings;
end;

function TframeJobWizardStep1.CheckVehicleCapacity: Boolean;
var
  Payload: Double;
  V: TVehicleRecord;
begin
  Result := True;
  if FVehicleId = 0 then
    Exit;

  Payload := StrToFloatDef(Trim(edPayloadKg.Text), 0);
  if Payload <= 0 then
    Exit;

  V := TVehicleRecord.Create;
  try
    V.ReadFromDatabase(FVehicleId);
    Result := (V.MaxPayloadKg = 0) or (Payload <= V.MaxPayloadKg);
  finally
    V.Free;
  end;
end;

function TframeJobWizardStep1.CheckDriverAvailability: Boolean;
var
  PickupDT, DeliveryDT: TDateTime;
begin
  Result := True;
  if FDriverId = 0 then
    Exit;

  PickupDT   := GetControlDateTimeValue(dtpPickupDate);
  DeliveryDT := GetControlDateTimeValue(dtpDeliveryDate);

  if (PickupDT <= 0) or (DeliveryDT <= 0) then
    Exit;

  Result := TDBDriverActions.IsDriverAvailable(FDriverId, PickupDT, DeliveryDT, dmFleet);
end;

procedure TframeJobWizardStep1.ClearUnwantedProperties;
begin
  inherited;
end;

constructor TframeJobWizardStep1.Create(AOwner: TComponent);
begin
  inherited;
  StepShowCaption := False;
  FVehicleId := 0;
  FDriverId  := 0;
end;

procedure TframeJobWizardStep1.RemoveAdditionalStop;
var
  S: TRouteStop;
begin
  if lvAdditionalStops.ItemIndex < 0 then
    Exit;

  if MsgAsk('Remove this stop?') = ID_YES then
  begin
    S := TRouteStop(lvAdditionalStops.Items[lvAdditionalStops.ItemIndex].Data);
    S.Deleted := True;
    lvAdditionalStops.Items[lvAdditionalStops.ItemIndex].Delete;
  end;
end;

procedure TframeJobWizardStep1.DisplayVehicle(AVehicle: TVehicleRecord);
begin
  if AVehicle.RegistrationPlate <> '' then
    edVehiclePlate.Text := AVehicle.RegistrationPlate + '  [' + AVehicle.Make + ' ' + AVehicle.Model + ']'
  else
    edVehiclePlate.Text := '';
end;

procedure TframeJobWizardStep1.DisplayDriver(ADriver: TDriverRecord);
begin
  if (ADriver.FirstName <> '') and (ADriver.LastName <> '') then
    edDriverName.Text := ADriver.FirstName + ' ' + ADriver.LastName +
                         '  (' + ADriver.EmployeeCode + ')'
  else
    edDriverName.Text := '';
end;

procedure TframeJobWizardStep1.FillAdditionalStopList;
var
  I: Integer;
begin
  for I := 0 to JobOrder.AdditionalStops.Count - 1 do
  with lvAdditionalStops.Items.Add do
  begin
    Caption := IntToStr(JobOrder.AdditionalStops[I].StopOrder);
    SubItems.Add(JobOrder.AdditionalStops[I].Address);
    Data := JobOrder.AdditionalStops[I];
  end;
end;

procedure TframeJobWizardStep1.PrepareInterface(DatabaseItem: TDatabaseItem;
  AReadOnly: Boolean; AParams: array of Variant);
begin
  inherited;

  FillControl(dtpPickupDate, JobOrder.PickupDate);
  FillControl(dtpPickupTime, JobOrder.PickupDate);
  FillControl(dtpDeliveryDate, JobOrder.DeliveryDate);
  FillControl(edtDescription, JobOrder.Description);
  FillControl(edCustomerRef, JobOrder.CustomerRef);
  FillControl(edPickupStreet, JobOrder.PickupStreet);
  FillControl(edPickupCity, JobOrder.PickupCity);
  FillControl(edPickupPostCode, JobOrder.PickupPostCode);
  FillControl(edDeliveryStreet, JobOrder.DeliveryStreet);
  FillControl(edDeliveryCity, JobOrder.DeliveryCity);
  FillControl(edDeliveryPostCode, JobOrder.DeliveryPostCode);
  FillControl(cbJobType, JobOrder.JobType.Id);
  edPayloadKg.Text := FormatFloat('0.##', JobOrder.PayloadKg);
  cbPriority.ItemIndex := JobOrder.Priority - 1;
  chkRequiresSignature.Checked := JobOrder.RequiresSignature;
  chkHazardousGoods.Checked    := JobOrder.HazardousGoods;

  FillAdditionalStopList;
end;

procedure TframeJobWizardStep1.SetReadOnlyPropertiesMode;
begin
  inherited;
  SetReadOnlyControl(dtpPickupDate);
  SetReadOnlyControl(dtpPickupTime);
  SetReadOnlyControl(dtpDeliveryDate);
  SetReadOnlyControl(edtDescription);
  SetReadOnlyControl(edCustomerRef);
  SetReadOnlyControl(edPickupStreet);
  SetReadOnlyControl(edPickupCity);
  SetReadOnlyControl(edPickupPostCode);
  SetReadOnlyControl(edDeliveryStreet);
  SetReadOnlyControl(edDeliveryCity);
  SetReadOnlyControl(edDeliveryPostCode);
  SetReadOnlyControl(cbJobType);
  SetReadOnlyControl(edPayloadKg);
  SetReadOnlyControl(cbPriority);
  SetReadOnlyControl(chkRequiresSignature);
  SetReadOnlyControl(chkHazardousGoods);
  SetReadOnlyControl(btnAddStop);
  SetReadOnlyControl(btnRemoveStop);
  btnChooseVehicle.Enabled    := False;
  btnClearVehicle.Enabled     := False;
  btnChooseDriver.Enabled     := False;
  btnClearDriver.Enabled      := False;
  btnChoosePickupAddress.Enabled   := False;
  btnClearPickupAddress.Enabled    := False;
  btnChooseDeliveryAddress.Enabled := False;
  btnClearDeliveryAddress.Enabled  := False;
end;

procedure TframeJobWizardStep1.SetReadOnlyEditMode;
begin
  inherited;
  SetReadOnlyControl(edVehiclePlate);
  SetReadOnlyControl(edDriverName);
end;

procedure TframeJobWizardStep1.SetReadOnlyInsertMode;
begin
  inherited;
  SetReadOnlyEditMode;
end;

function TframeJobWizardStep1.Validate: boolean;
var
  PickupDT, DeliveryDT: TDateTime;
begin
  PickupDT   := GetControlDateTimeValue(dtpPickupDate);
  DeliveryDT := GetControlDateTimeValue(dtpDeliveryDate);

  CheckFieldValid(gpPickupAddress,
    (Trim(edPickupStreet.Text) <> '') and (Trim(edPickupCity.Text) <> ''));
  CheckFieldValid(gpDeliveryAddress,
    (Trim(edDeliveryStreet.Text) <> '') and (Trim(edDeliveryCity.Text) <> ''));
  CheckFieldValid(dtpPickupDate, PickupDT > 0);
  CheckFieldValid(dtpDeliveryDate, (DeliveryDT > 0) and (DeliveryDT >= PickupDT));
  CheckFieldValid(cbJobType, GetListSelectedItemId(cbJobType) > 0);
  CheckFieldValid(edPayloadKg, CheckVehicleCapacity);

  Result := inherited;
end;

procedure TframeJobWizardStep1.ValidateWarnings;
begin
  with TfrmBaseWizard(wizard) do
  begin
    ClearMessages;

    if FVehicleId = 0 then
      AddMessageWarning('No vehicle assigned to this job.');

    if FDriverId = 0 then
      AddMessageWarning('No driver assigned to this job.');

    if (FVehicleId > 0) and (FDriverId > 0) and not CheckDriverAvailability then
      AddMessageWarning('Selected driver may not be available in the requested time window.');
  end;
end;

end.
