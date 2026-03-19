
{*******************************************************************************************************************************}
{                                                                                                                               }
{                                                       XML Data Binding                                                        }
{                                                                                                                               }
{         Generated on: 2023-06-12 09:14:22                                                                                     }
{       Generated from: FleetOps\server\licence.xsd                                                                            }
{   Settings stored in: FleetOps\server\licence.xdb                                                                            }
{                                                                                                                               }
{*******************************************************************************************************************************}

unit DeviceLicence;

interface

uses xmldom, XMLDoc, XMLIntf;

type

{ Forward Decls }

  IXMLDeviceLicences = interface;
  IXMLDeviceLicences_licence = interface;
  IXMLDeviceLicences_licence_device = interface;
  IXMLDeviceLicences_licence_deviceList = interface;
  IXMLDeviceLicences_licence_maxvalues = interface;
  IXMLDeviceLicences_licence_maxvalues_maxvalue = interface;
  IXMLDeviceLicences_licence_parameters = interface;
  IXMLDeviceLicences_licence_parameters_parameter = interface;
  IXMLDeviceLicences_licence_modules = interface;
  IXMLDeviceLicences_licence_modules_module = interface;
  IXMLDeviceLicences_licence_privileges = interface;
  IXMLDeviceLicences_licence_privileges_user = interface;
  IXMLDeviceLicences_licence_privileges_user_application = interface;
  IXMLTprivilege = interface;

{ IXMLDeviceLicences }

  IXMLDeviceLicences = interface(IXMLNode)
    ['{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}']
    { Property Accessors }
    function Get_DefaultUser: UnicodeString;
    function Get_CompanyCode: UnicodeString;
    function Get_SerialNumber: UnicodeString;
    function Get_CompanyName: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_ContactEmail: UnicodeString;
    function Get_ContactPhone: UnicodeString;
    function Get_LicenceKey: UnicodeString;
    function Get_Licence: IXMLDeviceLicences_licence;
    procedure Set_DefaultUser(Value: UnicodeString);
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_SerialNumber(Value: UnicodeString);
    procedure Set_CompanyName(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_ContactEmail(Value: UnicodeString);
    procedure Set_ContactPhone(Value: UnicodeString);
    procedure Set_LicenceKey(Value: UnicodeString);
    { Methods & Properties }
    property DefaultUser: UnicodeString read Get_DefaultUser write Set_DefaultUser;
    property CompanyCode: UnicodeString read Get_CompanyCode write Set_CompanyCode;
    property SerialNumber: UnicodeString read Get_SerialNumber write Set_SerialNumber;
    property CompanyName: UnicodeString read Get_CompanyName write Set_CompanyName;
    property CompanyType: UnicodeString read Get_CompanyType write Set_CompanyType;
    property CompanyStatus: UnicodeString read Get_CompanyStatus write Set_CompanyStatus;
    property ContactEmail: UnicodeString read Get_ContactEmail write Set_ContactEmail;
    property ContactPhone: UnicodeString read Get_ContactPhone write Set_ContactPhone;
    property LicenceKey: UnicodeString read Get_LicenceKey write Set_LicenceKey;
    property Licence: IXMLDeviceLicences_licence read Get_Licence;
  end;

{ IXMLDeviceLicences_licence }

  IXMLDeviceLicences_licence = interface(IXMLNode)
    ['{B2C3D4E5-F6A7-8901-BCDE-F12345678901}']
    { Property Accessors }
    function Get_Number: Integer;
    function Get_User: UnicodeString;
    function Get_LicenceDate: UnicodeString;
    function Get_LicenceEndDate: UnicodeString;
    function Get_DeviceList: IXMLDeviceLicences_licence_deviceList;
    function Get_Maxvalues: IXMLDeviceLicences_licence_maxvalues;
    function Get_Parameters: IXMLDeviceLicences_licence_parameters;
    function Get_Modules: IXMLDeviceLicences_licence_modules;
    function Get_Privileges: IXMLDeviceLicences_licence_privileges;
    procedure Set_Number(Value: Integer);
    procedure Set_User(Value: UnicodeString);
    procedure Set_LicenceDate(Value: UnicodeString);
    procedure Set_LicenceEndDate(Value: UnicodeString);
    { Methods & Properties }
    property Number: Integer read Get_Number write Set_Number;
    property User: UnicodeString read Get_User write Set_User;
    property LicenceDate: UnicodeString read Get_LicenceDate write Set_LicenceDate;
    property LicenceEndDate: UnicodeString read Get_LicenceEndDate write Set_LicenceEndDate;
    property DeviceList: IXMLDeviceLicences_licence_deviceList read Get_DeviceList;
    property Maxvalues: IXMLDeviceLicences_licence_maxvalues read Get_Maxvalues;
    property Parameters: IXMLDeviceLicences_licence_parameters read Get_Parameters;
    property Modules: IXMLDeviceLicences_licence_modules read Get_Modules;
    property Privileges: IXMLDeviceLicences_licence_privileges read Get_Privileges;
  end;

{ IXMLDeviceLicences_licence_device }

  IXMLDeviceLicences_licence_device = interface(IXMLNode)
    ['{C3D4E5F6-A7B8-9012-CDEF-012345678902}']
    { Property Accessors }
    function Get_DeviceId: UnicodeString;
    function Get_DeviceType: UnicodeString;
    function Get_DeviceName: UnicodeString;
    procedure Set_DeviceId(Value: UnicodeString);
    procedure Set_DeviceType(Value: UnicodeString);
    procedure Set_DeviceName(Value: UnicodeString);
    { Methods & Properties }
    property DeviceId: UnicodeString read Get_DeviceId write Set_DeviceId;
    property DeviceType: UnicodeString read Get_DeviceType write Set_DeviceType;
    property DeviceName: UnicodeString read Get_DeviceName write Set_DeviceName;
  end;

{ IXMLDeviceLicences_licence_deviceList }

  IXMLDeviceLicences_licence_deviceList = interface(IXMLNodeCollection)
    ['{D4E5F6A7-B8C9-0123-DEF0-123456789003}']
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_device;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_device;
    function Get_Item(Index: Integer): IXMLDeviceLicences_licence_device;
    property Items[Index: Integer]: IXMLDeviceLicences_licence_device read Get_Item; default;
  end;

{ IXMLDeviceLicences_licence_maxvalues }

  IXMLDeviceLicences_licence_maxvalues = interface(IXMLNodeCollection)
    ['{E5F6A7B8-C9D0-1234-EF01-234567890004}']
    { Property Accessors }
    function Get_Maxvalue(Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_maxvalues_maxvalue;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
    property Maxvalue[Index: Integer]: IXMLDeviceLicences_licence_maxvalues_maxvalue read Get_Maxvalue; default;
  end;

{ IXMLDeviceLicences_licence_maxvalues_maxvalue }

  IXMLDeviceLicences_licence_maxvalues_maxvalue = interface(IXMLNode)
    ['{F6A7B8C9-D0E1-2345-F012-345678900005}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Value: Integer;
    function Get_FeatureCode: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
    procedure Set_FeatureCode(Value: UnicodeString);
    { Methods & Properties }
    property Name: UnicodeString read Get_Name write Set_Name;
    property Value: Integer read Get_Value write Set_Value;
    property FeatureCode: UnicodeString read Get_FeatureCode write Set_FeatureCode;
  end;

{ IXMLDeviceLicences_licence_parameters }

  IXMLDeviceLicences_licence_parameters = interface(IXMLNodeCollection)
    ['{A7B8C9D0-E1F2-3456-0123-456789000006}']
    { Property Accessors }
    function Get_Parameter(Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_parameters_parameter;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
    property Parameter[Index: Integer]: IXMLDeviceLicences_licence_parameters_parameter read Get_Parameter; default;
  end;

{ IXMLDeviceLicences_licence_parameters_parameter }

  IXMLDeviceLicences_licence_parameters_parameter = interface(IXMLNode)
    ['{B8C9D0E1-F2A3-4567-1234-567890000007}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Value: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: UnicodeString);
    { Methods & Properties }
    property Name: UnicodeString read Get_Name write Set_Name;
    property Value: UnicodeString read Get_Value write Set_Value;
  end;

{ IXMLDeviceLicences_licence_modules }

  IXMLDeviceLicences_licence_modules = interface(IXMLNode)
    ['{C9D0E1F2-A3B4-5678-2345-678900000008}']
    { Property Accessors }
    function Get_Module(Index: Integer): IXMLDeviceLicences_licence_modules_module;
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_modules_module;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_modules_module;
    property Module[Index: Integer]: IXMLDeviceLicences_licence_modules_module read Get_Module; default;
  end;

{ IXMLDeviceLicences_licence_modules_module }

  IXMLDeviceLicences_licence_modules_module = interface(IXMLNode)
    ['{D0E1F2A3-B4C5-6789-3456-789000000009}']
    { Property Accessors }
    function Get_Tag: Integer;
    function Get_ModuleName: UnicodeString;
    function Get_Enabled: Integer;
    function Get_ExpiryDate: UnicodeString;
    procedure Set_Tag(Value: Integer);
    procedure Set_ModuleName(Value: UnicodeString);
    procedure Set_Enabled(Value: Integer);
    procedure Set_ExpiryDate(Value: UnicodeString);
    { Methods & Properties }
    property Tag: Integer read Get_Tag write Set_Tag;
    property ModuleName: UnicodeString read Get_ModuleName write Set_ModuleName;
    property Enabled: Integer read Get_Enabled write Set_Enabled;
    property ExpiryDate: UnicodeString read Get_ExpiryDate write Set_ExpiryDate;
  end;

{ IXMLDeviceLicences_licence_privileges }

  IXMLDeviceLicences_licence_privileges = interface(IXMLNodeCollection)
    ['{E1F2A3B4-C5D6-7890-4567-890000000010}']
    { Property Accessors }
    function Get_User(Index: Integer): IXMLDeviceLicences_licence_privileges_user;
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_privileges_user;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user;
    property User[Index: Integer]: IXMLDeviceLicences_licence_privileges_user read Get_User; default;
  end;

{ IXMLDeviceLicences_licence_privileges_user }

  IXMLDeviceLicences_licence_privileges_user = interface(IXMLNodeCollection)
    ['{F2A3B4C5-D6E7-8901-5678-900000000011}']
    { Property Accessors }
    function Get_UserCode: UnicodeString;
    function Get_Application(Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
    procedure Set_UserCode(Value: UnicodeString);
    { Methods & Properties }
    function Add: IXMLDeviceLicences_licence_privileges_user_application;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
    property UserCode: UnicodeString read Get_UserCode write Set_UserCode;
    property Application[Index: Integer]: IXMLDeviceLicences_licence_privileges_user_application read Get_Application; default;
  end;

{ IXMLDeviceLicences_licence_privileges_user_application }

  IXMLDeviceLicences_licence_privileges_user_application = interface(IXMLNodeCollection)
    ['{A3B4C5D6-E7F8-9012-6789-000000000012}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Privilege(Index: Integer): IXMLTprivilege;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
    { Methods & Properties }
    function Add: IXMLTprivilege;
    function Insert(const Index: Integer): IXMLTprivilege;
    property Name: UnicodeString read Get_Name write Set_Name;
    property Id: Integer read Get_Id write Set_Id;
    property Privilege[Index: Integer]: IXMLTprivilege read Get_Privilege; default;
  end;

{ IXMLTprivilege }

  IXMLTprivilege = interface(IXMLNodeCollection)
    ['{B4C5D6E7-F8A9-0123-7890-000000000013}']
    { Property Accessors }
    function Get_Tag: Integer;
    function Get_Caption: UnicodeString;
    function Get_Privilege(Index: Integer): IXMLTprivilege;
    procedure Set_Tag(Value: Integer);
    procedure Set_Caption(Value: UnicodeString);
    { Methods & Properties }
    function Add: IXMLTprivilege;
    function Insert(const Index: Integer): IXMLTprivilege;
    property Tag: Integer read Get_Tag write Set_Tag;
    property Caption: UnicodeString read Get_Caption write Set_Caption;
    property Privilege[Index: Integer]: IXMLTprivilege read Get_Privilege; default;
  end;

{ Forward Decls }

  TXMLDeviceLicences = class;
  TXMLDeviceLicences_licence = class;
  TXMLDeviceLicences_licence_device = class;
  TXMLDeviceLicences_licence_deviceList = class;
  TXMLDeviceLicences_licence_maxvalues = class;
  TXMLDeviceLicences_licence_maxvalues_maxvalue = class;
  TXMLDeviceLicences_licence_parameters = class;
  TXMLDeviceLicences_licence_parameters_parameter = class;
  TXMLDeviceLicences_licence_modules = class;
  TXMLDeviceLicences_licence_modules_module = class;
  TXMLDeviceLicences_licence_privileges = class;
  TXMLDeviceLicences_licence_privileges_user = class;
  TXMLDeviceLicences_licence_privileges_user_application = class;
  TXMLTprivilege = class;

{ TXMLDeviceLicences }

  TXMLDeviceLicences = class(TXMLNode, IXMLDeviceLicences)
  protected
    { IXMLDeviceLicences }
    function Get_DefaultUser: UnicodeString;
    function Get_CompanyCode: UnicodeString;
    function Get_SerialNumber: UnicodeString;
    function Get_CompanyName: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_ContactEmail: UnicodeString;
    function Get_ContactPhone: UnicodeString;
    function Get_LicenceKey: UnicodeString;
    function Get_Licence: IXMLDeviceLicences_licence;
    procedure Set_DefaultUser(Value: UnicodeString);
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_SerialNumber(Value: UnicodeString);
    procedure Set_CompanyName(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_ContactEmail(Value: UnicodeString);
    procedure Set_ContactPhone(Value: UnicodeString);
    procedure Set_LicenceKey(Value: UnicodeString);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence }

  TXMLDeviceLicences_licence = class(TXMLNode, IXMLDeviceLicences_licence)
  private
    FDeviceList: IXMLDeviceLicences_licence_deviceList;
  protected
    { IXMLDeviceLicences_licence }
    function Get_Number: Integer;
    function Get_User: UnicodeString;
    function Get_LicenceDate: UnicodeString;
    function Get_LicenceEndDate: UnicodeString;
    function Get_DeviceList: IXMLDeviceLicences_licence_deviceList;
    function Get_Maxvalues: IXMLDeviceLicences_licence_maxvalues;
    function Get_Parameters: IXMLDeviceLicences_licence_parameters;
    function Get_Modules: IXMLDeviceLicences_licence_modules;
    function Get_Privileges: IXMLDeviceLicences_licence_privileges;
    procedure Set_Number(Value: Integer);
    procedure Set_User(Value: UnicodeString);
    procedure Set_LicenceDate(Value: UnicodeString);
    procedure Set_LicenceEndDate(Value: UnicodeString);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_device }

  TXMLDeviceLicences_licence_device = class(TXMLNode, IXMLDeviceLicences_licence_device)
  protected
    function Get_DeviceId: UnicodeString;
    function Get_DeviceType: UnicodeString;
    function Get_DeviceName: UnicodeString;
    procedure Set_DeviceId(Value: UnicodeString);
    procedure Set_DeviceType(Value: UnicodeString);
    procedure Set_DeviceName(Value: UnicodeString);
  end;

{ TXMLDeviceLicences_licence_deviceList }

  TXMLDeviceLicences_licence_deviceList = class(TXMLNodeCollection, IXMLDeviceLicences_licence_deviceList)
  protected
    function Add: IXMLDeviceLicences_licence_device;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_device;
    function Get_Item(Index: Integer): IXMLDeviceLicences_licence_device;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_maxvalues }

  TXMLDeviceLicences_licence_maxvalues = class(TXMLNodeCollection, IXMLDeviceLicences_licence_maxvalues)
  protected
    function Get_Maxvalue(Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
    function Add: IXMLDeviceLicences_licence_maxvalues_maxvalue;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_maxvalues_maxvalue }

  TXMLDeviceLicences_licence_maxvalues_maxvalue = class(TXMLNode, IXMLDeviceLicences_licence_maxvalues_maxvalue)
  protected
    function Get_Name: UnicodeString;
    function Get_Value: Integer;
    function Get_FeatureCode: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
    procedure Set_FeatureCode(Value: UnicodeString);
  end;

{ TXMLDeviceLicences_licence_parameters }

  TXMLDeviceLicences_licence_parameters = class(TXMLNodeCollection, IXMLDeviceLicences_licence_parameters)
  protected
    function Get_Parameter(Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
    function Add: IXMLDeviceLicences_licence_parameters_parameter;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_parameters_parameter }

  TXMLDeviceLicences_licence_parameters_parameter = class(TXMLNode, IXMLDeviceLicences_licence_parameters_parameter)
  protected
    function Get_Name: UnicodeString;
    function Get_Value: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: UnicodeString);
  end;

{ TXMLDeviceLicences_licence_modules }

  TXMLDeviceLicences_licence_modules = class(TXMLNodeCollection, IXMLDeviceLicences_licence_modules)
  protected
    function Get_Module(Index: Integer): IXMLDeviceLicences_licence_modules_module;
    function Add: IXMLDeviceLicences_licence_modules_module;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_modules_module;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_modules_module }

  TXMLDeviceLicences_licence_modules_module = class(TXMLNode, IXMLDeviceLicences_licence_modules_module)
  protected
    function Get_Tag: Integer;
    function Get_ModuleName: UnicodeString;
    function Get_Enabled: Integer;
    function Get_ExpiryDate: UnicodeString;
    procedure Set_Tag(Value: Integer);
    procedure Set_ModuleName(Value: UnicodeString);
    procedure Set_Enabled(Value: Integer);
    procedure Set_ExpiryDate(Value: UnicodeString);
  end;

{ TXMLDeviceLicences_licence_privileges }

  TXMLDeviceLicences_licence_privileges = class(TXMLNodeCollection, IXMLDeviceLicences_licence_privileges)
  protected
    function Get_User(Index: Integer): IXMLDeviceLicences_licence_privileges_user;
    function Add: IXMLDeviceLicences_licence_privileges_user;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_privileges_user }

  TXMLDeviceLicences_licence_privileges_user = class(TXMLNodeCollection, IXMLDeviceLicences_licence_privileges_user)
  protected
    function Get_UserCode: UnicodeString;
    function Get_Application(Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
    procedure Set_UserCode(Value: UnicodeString);
    function Add: IXMLDeviceLicences_licence_privileges_user_application;
    function Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLDeviceLicences_licence_privileges_user_application }

  TXMLDeviceLicences_licence_privileges_user_application = class(TXMLNodeCollection, IXMLDeviceLicences_licence_privileges_user_application)
  protected
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Privilege(Index: Integer): IXMLTprivilege;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
    function Add: IXMLTprivilege;
    function Insert(const Index: Integer): IXMLTprivilege;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLTprivilege }

  TXMLTprivilege = class(TXMLNodeCollection, IXMLTprivilege)
  protected
    function Get_Tag: Integer;
    function Get_Caption: UnicodeString;
    function Get_Privilege(Index: Integer): IXMLTprivilege;
    procedure Set_Tag(Value: Integer);
    procedure Set_Caption(Value: UnicodeString);
    function Add: IXMLTprivilege;
    function Insert(const Index: Integer): IXMLTprivilege;
  public
    procedure AfterConstruction; override;
  end;

{ Global Functions }

function GetDeviceLicences(Doc: IXMLDocument): IXMLDeviceLicences;
function LoadDeviceLicences(const FileName: string): IXMLDeviceLicences;
function NewDeviceLicences: IXMLDeviceLicences;

const
  TargetNamespace = '';

implementation

{ Global Functions }

function GetDeviceLicences(Doc: IXMLDocument): IXMLDeviceLicences;
begin
  Result := Doc.GetDocBinding('devicelicences', TXMLDeviceLicences, TargetNamespace) as IXMLDeviceLicences;
end;

function LoadDeviceLicences(const FileName: string): IXMLDeviceLicences;
begin
  Result := LoadXMLDocument(FileName).GetDocBinding('devicelicences', TXMLDeviceLicences, TargetNamespace) as IXMLDeviceLicences;
end;

function NewDeviceLicences: IXMLDeviceLicences;
begin
  Result := NewXMLDocument.GetDocBinding('devicelicences', TXMLDeviceLicences, TargetNamespace) as IXMLDeviceLicences;
end;

{ TXMLDeviceLicences }

procedure TXMLDeviceLicences.AfterConstruction;
begin
  RegisterChildNode('licence', TXMLDeviceLicences_licence);
  inherited;
end;

function TXMLDeviceLicences.Get_DefaultUser: UnicodeString;
begin
  Result := AttributeNodes['defaultuser'].Text;
end;

procedure TXMLDeviceLicences.Set_DefaultUser(Value: UnicodeString);
begin
  SetAttribute('defaultuser', Value);
end;

function TXMLDeviceLicences.Get_CompanyCode: UnicodeString;
begin
  Result := AttributeNodes['companycode'].Text;
end;

procedure TXMLDeviceLicences.Set_CompanyCode(Value: UnicodeString);
begin
  SetAttribute('companycode', Value);
end;

function TXMLDeviceLicences.Get_SerialNumber: UnicodeString;
begin
  Result := AttributeNodes['serialnumber'].Text;
end;

procedure TXMLDeviceLicences.Set_SerialNumber(Value: UnicodeString);
begin
  SetAttribute('serialnumber', Value);
end;

function TXMLDeviceLicences.Get_CompanyName: UnicodeString;
begin
  Result := AttributeNodes['companyname'].Text;
end;

procedure TXMLDeviceLicences.Set_CompanyName(Value: UnicodeString);
begin
  SetAttribute('companyname', Value);
end;

function TXMLDeviceLicences.Get_CompanyType: UnicodeString;
begin
  Result := AttributeNodes['companytype'].Text;
end;

procedure TXMLDeviceLicences.Set_CompanyType(Value: UnicodeString);
begin
  SetAttribute('companytype', Value);
end;

function TXMLDeviceLicences.Get_CompanyStatus: UnicodeString;
begin
  Result := AttributeNodes['companystatus'].Text;
end;

procedure TXMLDeviceLicences.Set_CompanyStatus(Value: UnicodeString);
begin
  SetAttribute('companystatus', Value);
end;

function TXMLDeviceLicences.Get_ContactEmail: UnicodeString;
begin
  try
    Result := AttributeNodes['contactemail'].Text;
  except
    Result := '';
  end;
end;

procedure TXMLDeviceLicences.Set_ContactEmail(Value: UnicodeString);
begin
  SetAttribute('contactemail', Value);
end;

function TXMLDeviceLicences.Get_ContactPhone: UnicodeString;
begin
  try
    Result := AttributeNodes['contactphone'].Text;
  except
    Result := '';
  end;
end;

procedure TXMLDeviceLicences.Set_ContactPhone(Value: UnicodeString);
begin
  SetAttribute('contactphone', Value);
end;

function TXMLDeviceLicences.Get_LicenceKey: UnicodeString;
begin
  Result := AttributeNodes['licencekey'].Text;
end;

procedure TXMLDeviceLicences.Set_LicenceKey(Value: UnicodeString);
begin
  SetAttribute('licencekey', Value);
end;

function TXMLDeviceLicences.Get_Licence: IXMLDeviceLicences_licence;
begin
  Result := ChildNodes['licence'] as IXMLDeviceLicences_licence;
end;

{ TXMLDeviceLicences_licence }

procedure TXMLDeviceLicences_licence.AfterConstruction;
begin
  RegisterChildNode('devicelist', TXMLDeviceLicences_licence_deviceList);
  RegisterChildNode('maxvalues', TXMLDeviceLicences_licence_maxvalues);
  RegisterChildNode('parameters', TXMLDeviceLicences_licence_parameters);
  RegisterChildNode('modules', TXMLDeviceLicences_licence_modules);
  RegisterChildNode('privileges', TXMLDeviceLicences_licence_privileges);
  FDeviceList := CreateCollection(TXMLDeviceLicences_licence_deviceList, IXMLDeviceLicences_licence_device, 'device') as IXMLDeviceLicences_licence_deviceList;
  inherited;
end;

function TXMLDeviceLicences_licence.Get_Number: Integer;
begin
  Result := AttributeNodes['number'].NodeValue;
end;

procedure TXMLDeviceLicences_licence.Set_Number(Value: Integer);
begin
  SetAttribute('number', Value);
end;

function TXMLDeviceLicences_licence.Get_User: UnicodeString;
begin
  Result := ChildNodes['user'].Text;
end;

procedure TXMLDeviceLicences_licence.Set_User(Value: UnicodeString);
begin
  ChildNodes['user'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence.Get_LicenceDate: UnicodeString;
begin
  Result := ChildNodes['licencedate'].Text;
end;

procedure TXMLDeviceLicences_licence.Set_LicenceDate(Value: UnicodeString);
begin
  ChildNodes['licencedate'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence.Get_LicenceEndDate: UnicodeString;
begin
  Result := ChildNodes['licenceenddate'].Text;
end;

procedure TXMLDeviceLicences_licence.Set_LicenceEndDate(Value: UnicodeString);
begin
  ChildNodes['licenceenddate'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence.Get_DeviceList: IXMLDeviceLicences_licence_deviceList;
begin
  Result := FDeviceList;
end;

function TXMLDeviceLicences_licence.Get_Maxvalues: IXMLDeviceLicences_licence_maxvalues;
begin
  Result := ChildNodes['maxvalues'] as IXMLDeviceLicences_licence_maxvalues;
end;

function TXMLDeviceLicences_licence.Get_Parameters: IXMLDeviceLicences_licence_parameters;
begin
  Result := ChildNodes['parameters'] as IXMLDeviceLicences_licence_parameters;
end;

function TXMLDeviceLicences_licence.Get_Modules: IXMLDeviceLicences_licence_modules;
begin
  Result := ChildNodes['modules'] as IXMLDeviceLicences_licence_modules;
end;

function TXMLDeviceLicences_licence.Get_Privileges: IXMLDeviceLicences_licence_privileges;
begin
  Result := ChildNodes['privileges'] as IXMLDeviceLicences_licence_privileges;
end;

{ TXMLDeviceLicences_licence_device }

function TXMLDeviceLicences_licence_device.Get_DeviceId: UnicodeString;
begin
  Result := AttributeNodes['deviceid'].Text;
end;

procedure TXMLDeviceLicences_licence_device.Set_DeviceId(Value: UnicodeString);
begin
  SetAttribute('deviceid', Value);
end;

function TXMLDeviceLicences_licence_device.Get_DeviceType: UnicodeString;
begin
  Result := ChildNodes['devicetype'].Text;
end;

procedure TXMLDeviceLicences_licence_device.Set_DeviceType(Value: UnicodeString);
begin
  ChildNodes['devicetype'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_device.Get_DeviceName: UnicodeString;
begin
  Result := ChildNodes['devicename'].Text;
end;

procedure TXMLDeviceLicences_licence_device.Set_DeviceName(Value: UnicodeString);
begin
  ChildNodes['devicename'].NodeValue := Value;
end;

{ TXMLDeviceLicences_licence_deviceList }

procedure TXMLDeviceLicences_licence_deviceList.AfterConstruction;
begin
  RegisterChildNode('device', TXMLDeviceLicences_licence_device);
  ItemTag := 'device';
  ItemInterface := IXMLDeviceLicences_licence_device;
  inherited;
end;

function TXMLDeviceLicences_licence_deviceList.Add: IXMLDeviceLicences_licence_device;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_device;
end;

function TXMLDeviceLicences_licence_deviceList.Insert(const Index: Integer): IXMLDeviceLicences_licence_device;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_device;
end;

function TXMLDeviceLicences_licence_deviceList.Get_Item(Index: Integer): IXMLDeviceLicences_licence_device;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_device;
end;

{ TXMLDeviceLicences_licence_maxvalues }

procedure TXMLDeviceLicences_licence_maxvalues.AfterConstruction;
begin
  RegisterChildNode('maxvalue', TXMLDeviceLicences_licence_maxvalues_maxvalue);
  ItemTag := 'maxvalue';
  ItemInterface := IXMLDeviceLicences_licence_maxvalues_maxvalue;
  inherited;
end;

function TXMLDeviceLicences_licence_maxvalues.Get_Maxvalue(Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_maxvalues_maxvalue;
end;

function TXMLDeviceLicences_licence_maxvalues.Add: IXMLDeviceLicences_licence_maxvalues_maxvalue;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_maxvalues_maxvalue;
end;

function TXMLDeviceLicences_licence_maxvalues.Insert(const Index: Integer): IXMLDeviceLicences_licence_maxvalues_maxvalue;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_maxvalues_maxvalue;
end;

{ TXMLDeviceLicences_licence_maxvalues_maxvalue }

function TXMLDeviceLicences_licence_maxvalues_maxvalue.Get_Name: UnicodeString;
begin
  Result := ChildNodes['name'].Text;
end;

procedure TXMLDeviceLicences_licence_maxvalues_maxvalue.Set_Name(Value: UnicodeString);
begin
  ChildNodes['name'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_maxvalues_maxvalue.Get_Value: Integer;
begin
  Result := ChildNodes['value'].NodeValue;
end;

procedure TXMLDeviceLicences_licence_maxvalues_maxvalue.Set_Value(Value: Integer);
begin
  ChildNodes['value'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_maxvalues_maxvalue.Get_FeatureCode: UnicodeString;
begin
  if AttributeNodes.FindNode('featurecode') <> nil then
    Result := AttributeNodes['featurecode'].Text
  else
    Result := '';
end;

procedure TXMLDeviceLicences_licence_maxvalues_maxvalue.Set_FeatureCode(Value: UnicodeString);
begin
  SetAttribute('featurecode', Value);
end;

{ TXMLDeviceLicences_licence_parameters }

procedure TXMLDeviceLicences_licence_parameters.AfterConstruction;
begin
  RegisterChildNode('parameter', TXMLDeviceLicences_licence_parameters_parameter);
  ItemTag := 'parameter';
  ItemInterface := IXMLDeviceLicences_licence_parameters_parameter;
  inherited;
end;

function TXMLDeviceLicences_licence_parameters.Get_Parameter(Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_parameters_parameter;
end;

function TXMLDeviceLicences_licence_parameters.Add: IXMLDeviceLicences_licence_parameters_parameter;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_parameters_parameter;
end;

function TXMLDeviceLicences_licence_parameters.Insert(const Index: Integer): IXMLDeviceLicences_licence_parameters_parameter;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_parameters_parameter;
end;

{ TXMLDeviceLicences_licence_parameters_parameter }

function TXMLDeviceLicences_licence_parameters_parameter.Get_Name: UnicodeString;
begin
  Result := ChildNodes['name'].Text;
end;

procedure TXMLDeviceLicences_licence_parameters_parameter.Set_Name(Value: UnicodeString);
begin
  ChildNodes['name'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_parameters_parameter.Get_Value: UnicodeString;
begin
  Result := ChildNodes['value'].Text;
end;

procedure TXMLDeviceLicences_licence_parameters_parameter.Set_Value(Value: UnicodeString);
begin
  ChildNodes['value'].NodeValue := Value;
end;

{ TXMLDeviceLicences_licence_modules }

procedure TXMLDeviceLicences_licence_modules.AfterConstruction;
begin
  RegisterChildNode('module', TXMLDeviceLicences_licence_modules_module);
  ItemTag := 'module';
  ItemInterface := IXMLDeviceLicences_licence_modules_module;
  inherited;
end;

function TXMLDeviceLicences_licence_modules.Get_Module(Index: Integer): IXMLDeviceLicences_licence_modules_module;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_modules_module;
end;

function TXMLDeviceLicences_licence_modules.Add: IXMLDeviceLicences_licence_modules_module;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_modules_module;
end;

function TXMLDeviceLicences_licence_modules.Insert(const Index: Integer): IXMLDeviceLicences_licence_modules_module;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_modules_module;
end;

{ TXMLDeviceLicences_licence_modules_module }

function TXMLDeviceLicences_licence_modules_module.Get_Tag: Integer;
begin
  Result := AttributeNodes['tag'].NodeValue;
end;

procedure TXMLDeviceLicences_licence_modules_module.Set_Tag(Value: Integer);
begin
  SetAttribute('tag', Value);
end;

function TXMLDeviceLicences_licence_modules_module.Get_ModuleName: UnicodeString;
begin
  Result := ChildNodes['modulename'].Text;
end;

procedure TXMLDeviceLicences_licence_modules_module.Set_ModuleName(Value: UnicodeString);
begin
  ChildNodes['modulename'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_modules_module.Get_Enabled: Integer;
begin
  Result := ChildNodes['enabled'].NodeValue;
end;

procedure TXMLDeviceLicences_licence_modules_module.Set_Enabled(Value: Integer);
begin
  ChildNodes['enabled'].NodeValue := Value;
end;

function TXMLDeviceLicences_licence_modules_module.Get_ExpiryDate: UnicodeString;
begin
  Result := ChildNodes['expirydate'].Text;
end;

procedure TXMLDeviceLicences_licence_modules_module.Set_ExpiryDate(Value: UnicodeString);
begin
  ChildNodes['expirydate'].NodeValue := Value;
end;

{ TXMLDeviceLicences_licence_privileges }

procedure TXMLDeviceLicences_licence_privileges.AfterConstruction;
begin
  RegisterChildNode('user', TXMLDeviceLicences_licence_privileges_user);
  ItemTag := 'user';
  ItemInterface := IXMLDeviceLicences_licence_privileges_user;
  inherited;
end;

function TXMLDeviceLicences_licence_privileges.Get_User(Index: Integer): IXMLDeviceLicences_licence_privileges_user;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_privileges_user;
end;

function TXMLDeviceLicences_licence_privileges.Add: IXMLDeviceLicences_licence_privileges_user;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_privileges_user;
end;

function TXMLDeviceLicences_licence_privileges.Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_privileges_user;
end;

{ TXMLDeviceLicences_licence_privileges_user }

procedure TXMLDeviceLicences_licence_privileges_user.AfterConstruction;
begin
  RegisterChildNode('application', TXMLDeviceLicences_licence_privileges_user_application);
  ItemTag := 'application';
  ItemInterface := IXMLDeviceLicences_licence_privileges_user_application;
  inherited;
end;

function TXMLDeviceLicences_licence_privileges_user.Get_UserCode: UnicodeString;
begin
  Result := AttributeNodes['usercode'].Text;
end;

procedure TXMLDeviceLicences_licence_privileges_user.Set_UserCode(Value: UnicodeString);
begin
  SetAttribute('usercode', Value);
end;

function TXMLDeviceLicences_licence_privileges_user.Get_Application(Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
begin
  Result := List[Index] as IXMLDeviceLicences_licence_privileges_user_application;
end;

function TXMLDeviceLicences_licence_privileges_user.Add: IXMLDeviceLicences_licence_privileges_user_application;
begin
  Result := AddItem(-1) as IXMLDeviceLicences_licence_privileges_user_application;
end;

function TXMLDeviceLicences_licence_privileges_user.Insert(const Index: Integer): IXMLDeviceLicences_licence_privileges_user_application;
begin
  Result := AddItem(Index) as IXMLDeviceLicences_licence_privileges_user_application;
end;

{ TXMLDeviceLicences_licence_privileges_user_application }

procedure TXMLDeviceLicences_licence_privileges_user_application.AfterConstruction;
begin
  RegisterChildNode('privilege', TXMLTprivilege);
  ItemTag := 'privilege';
  ItemInterface := IXMLTprivilege;
  inherited;
end;

function TXMLDeviceLicences_licence_privileges_user_application.Get_Name: UnicodeString;
begin
  Result := AttributeNodes['name'].Text;
end;

procedure TXMLDeviceLicences_licence_privileges_user_application.Set_Name(Value: UnicodeString);
begin
  SetAttribute('name', Value);
end;

function TXMLDeviceLicences_licence_privileges_user_application.Get_Id: Integer;
begin
  Result := AttributeNodes['id'].NodeValue;
end;

procedure TXMLDeviceLicences_licence_privileges_user_application.Set_Id(Value: Integer);
begin
  SetAttribute('id', Value);
end;

function TXMLDeviceLicences_licence_privileges_user_application.Get_Privilege(Index: Integer): IXMLTprivilege;
begin
  Result := List[Index] as IXMLTprivilege;
end;

function TXMLDeviceLicences_licence_privileges_user_application.Add: IXMLTprivilege;
begin
  Result := AddItem(-1) as IXMLTprivilege;
end;

function TXMLDeviceLicences_licence_privileges_user_application.Insert(const Index: Integer): IXMLTprivilege;
begin
  Result := AddItem(Index) as IXMLTprivilege;
end;

{ TXMLTprivilege }

procedure TXMLTprivilege.AfterConstruction;
begin
  RegisterChildNode('privilege', TXMLTprivilege);
  ItemTag := 'privilege';
  ItemInterface := IXMLTprivilege;
  inherited;
end;

function TXMLTprivilege.Get_Tag: Integer;
begin
  Result := AttributeNodes['tag'].NodeValue;
end;

procedure TXMLTprivilege.Set_Tag(Value: Integer);
begin
  SetAttribute('tag', Value);
end;

function TXMLTprivilege.Get_Caption: UnicodeString;
begin
  Result := ChildNodes['caption'].Text;
end;

procedure TXMLTprivilege.Set_Caption(Value: UnicodeString);
begin
  ChildNodes['caption'].NodeValue := Value;
end;

function TXMLTprivilege.Get_Privilege(Index: Integer): IXMLTprivilege;
begin
  Result := List[Index] as IXMLTprivilege;
end;

function TXMLTprivilege.Add: IXMLTprivilege;
begin
  Result := AddItem(-1) as IXMLTprivilege;
end;

function TXMLTprivilege.Insert(const Index: Integer): IXMLTprivilege;
begin
  Result := AddItem(Index) as IXMLTprivilege;
end;

end.
