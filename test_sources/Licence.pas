
{*******************************************************************************************************************************}
{                                                                                                                               }
{                                                       XML Data Binding                                                        }
{                                                                                                                               }
{         Generated on: 2012-03-05 12:06:39                                                                                     }
{       Generated from: C:\Users\adam\Documents\RAD Studio\Projects\Informica\CityCard\delphi_src\DataSnapServer\_bin\lic.xsd   }
{   Settings stored in: C:\Users\adam\Documents\RAD Studio\Projects\Informica\CityCard\delphi_src\DataSnapServer\_bin\lic.xdb   }
{                                                                                                                               }
{*******************************************************************************************************************************}

unit Licence;

interface

uses xmldom, XMLDoc, XMLIntf;

type

{ Forward Decls }

  IXMLLicences = interface;
  IXMLLicences_licence = interface;
  IXMLLicences_licence_UserForisKM = interface;
  IXMLLicences_licence_useradd = interface;
  IXMLLicences_licence_useraddList = interface;
  IXMLLicences_licence_useradd_usercode = interface;
  IXMLLicences_licence_maxvalues = interface;
  IXMLLicences_licence_maxvalues_maxvalue = interface;
  IXMLLicences_licence_maxvalues_maxvalue_app_ids = interface;
  IXMLLicences_licence_parameters = interface;
  IXMLLicences_licence_parameters_parameter = interface;
  IXMLLicences_licence_modsavailability = interface;
  IXMLLicences_licence_modsavailability_apps = interface;
  IXMLLicences_licence_modsavailability_apps_app = interface;
  IXMLLicences_licence_modsavailability_apps_app_mods = interface;
  IXMLLicences_licence_modsavailability_apps_app_mods_mod = interface;
  IXMLLicences_licence_privilages = interface;
  IXMLLicences_licence_privilages_user = interface;
  IXMLLicences_licence_privilages_user_application = interface;
  IXMLTprivilage = interface;

{ IXMLLicences }

  IXMLLicences = interface(IXMLNode)
    ['{B4F26D2E-56D3-47EC-B8A0-D755637EFA23}']
    { Property Accessors }
    function Get_Defaultuser: UnicodeString;
    function Get_CompanyCode: UnicodeString;
    function Get_INumber: UnicodeString;
    function Get_Name: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_TarifLimit: UnicodeString;
    function Get_NIP: UnicodeString;
    function Get_Street: UnicodeString;
    function Get_PostCode: UnicodeString;
    function Get_PlaceID: UnicodeString;
    function Get_PlaceSymbol: UnicodeString;
    function Get_Country: UnicodeString;
    function Get_Licence: IXMLLicences_licence;
    procedure Set_Defaultuser(Value: UnicodeString);
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_INumber(Value: UnicodeString);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_TarifLimit(Value: UnicodeString);
    procedure Set_NIP(Value: UnicodeString);
    procedure Set_Street(Value: UnicodeString);
    procedure Set_PostCode(Value: UnicodeString);
    procedure Set_PlaceID(Value: UnicodeString);
    procedure Set_PlaceSymbol(Value: UnicodeString);
    procedure Set_Country(Value: UnicodeString);
    { Methods & Properties }
    property Defaultuser: UnicodeString read Get_Defaultuser write Set_Defaultuser;
    property CompanyCode: UnicodeString read Get_CompanyCode write Set_CompanyCode;
    property INumber: UnicodeString read Get_INumber write Set_INumber;
    property Name: UnicodeString read Get_Name write Set_Name;
    property CompanyType: UnicodeString read Get_CompanyType write Set_CompanyType;
    property CompanyStatus: UnicodeString read Get_CompanyStatus write Set_CompanyStatus;
    property TarifLimit: UnicodeString read Get_TarifLimit write Set_TarifLimit;
    property NIP: UnicodeString read Get_NIP write Set_NIP;
    property Street: UnicodeString read Get_Street write Set_Street;
    property PostCode: UnicodeString read Get_PostCode write Set_PostCode;
    property PlaceID: UnicodeString read Get_PlaceID write Set_PlaceID;
    property PlaceSymbol: UnicodeString read Get_PlaceSymbol write Set_PlaceSymbol;
    property Country: UnicodeString read Get_Country write Set_Country;
    property Licence: IXMLLicences_licence read Get_Licence;
  end;

{ IXMLLicences_licence }

  IXMLLicences_licence = interface(IXMLNode)
    ['{4300DD5C-E57D-4695-BD47-411FEFC0D357}']
    { Property Accessors }
    function Get_Number: Integer;
    function Get_UserForisKM: IXMLLicences_licence_UserForisKM; /////
    function Get_UserForisKMCode: UnicodeString; ///
    function Get_User: UnicodeString;
    function Get_Licencedate: UnicodeString;
    function Get_Licenceenddate: UnicodeString;
    function Get_Useradd: IXMLLicences_licence_useraddList;
    function Get_Maxvalues: IXMLLicences_licence_maxvalues;
    function Get_Parameters: IXMLLicences_licence_parameters;
    function Get_Modsavailability: IXMLLicences_licence_modsavailability;
    function Get_Privilages: IXMLLicences_licence_privilages;
    procedure Set_Number(Value: Integer);
    procedure Set_User(Value: UnicodeString);
    procedure Set_UserForisKMCode(Value: UnicodeString); ////
    procedure Set_Licencedate(Value: UnicodeString);
    procedure Set_Licenceenddate(Value: UnicodeString);
    { Methods & Properties }
    property Number: Integer read Get_Number write Set_Number;
    property User: UnicodeString read Get_User write Set_User;
    property UserForisKMCode: UnicodeString read Get_UserForisKMCode write Set_UserForisKMCode;
    property Licencedate: UnicodeString read Get_Licencedate write Set_Licencedate;
    property Licenceenddate: UnicodeString read Get_Licenceenddate write Set_Licenceenddate;
    property Useradd: IXMLLicences_licence_useraddList read Get_Useradd;
    property Maxvalues: IXMLLicences_licence_maxvalues read Get_Maxvalues;
    property Parameters: IXMLLicences_licence_parameters read Get_Parameters;
    property Modsavailability: IXMLLicences_licence_modsavailability read Get_Modsavailability;
    property Privilages: IXMLLicences_licence_privilages read Get_Privilages;
    property UserForisKM: IXMLLicences_licence_UserForisKM read Get_UserForisKM;
  end;

{ IXMLLicences_licence_UserForisKM }
  IXMLLicences_licence_UserForisKM = interface(IXMLNode)
    ['{B4F26D2E-56D3-47EC-B8A0-D755637EFA23}']
    { Property Accessors }
    function Get_CompanyCode: UnicodeString;
    function Get_INumber: UnicodeString;
    function Get_Name: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_NIP: UnicodeString;
    function Get_Street: UnicodeString;
    function Get_PostCode: UnicodeString;
    function Get_PlaceID: UnicodeString;
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_INumber(Value: UnicodeString);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_NIP(Value: UnicodeString);
    procedure Set_Street(Value: UnicodeString);
    procedure Set_PostCode(Value: UnicodeString);
    procedure Set_PlaceID(Value: UnicodeString);
    { Methods & Properties }
    property CompanyCode: UnicodeString read Get_CompanyCode write Set_CompanyCode;
    property INumber: UnicodeString read Get_INumber write Set_INumber;
    property Name: UnicodeString read Get_Name write Set_Name;
    property CompanyType: UnicodeString read Get_CompanyType write Set_CompanyType;
    property CompanyStatus: UnicodeString read Get_CompanyStatus write Set_CompanyStatus;
    property NIP: UnicodeString read Get_NIP write Set_NIP;
    property Street: UnicodeString read Get_Street write Set_Street;
    property PostCode: UnicodeString read Get_PostCode write Set_PostCode;
    property PlaceID: UnicodeString read Get_PlaceID write Set_PlaceID;
  end;

{ IXMLLicences_licence_useradd }

  IXMLLicences_licence_useradd = interface(IXMLNodeCollection)
    ['{AC1432CA-E464-4E06-A569-327C69D0ED80}']
    { Property Accessors }
    function Get_Usercode(Index: Integer): IXMLLicences_licence_useradd_usercode;
    { Methods & Properties }
    function Add: IXMLLicences_licence_useradd_usercode;
    function Insert(const Index: Integer): IXMLLicences_licence_useradd_usercode;
    property Usercode[Index: Integer]: IXMLLicences_licence_useradd_usercode read Get_Usercode; default;
  end;

{ IXMLLicences_licence_useraddList }

  IXMLLicences_licence_useraddList = interface(IXMLNodeCollection)
    ['{B98C85BE-0AD5-496F-A2A7-E88FD228418B}']
    { Methods & Properties }
    function Add: IXMLLicences_licence_useradd;
    function Insert(const Index: Integer): IXMLLicences_licence_useradd;

    function Get_Item(Index: Integer): IXMLLicences_licence_useradd;
    property Items[Index: Integer]: IXMLLicences_licence_useradd read Get_Item; default;
  end;

{ IXMLLicences_licence_useradd_usercode }

  IXMLLicences_licence_useradd_usercode = interface(IXMLNode)
    ['{F6B3039A-B132-4E05-ACF7-CE2AB1C34793}']
  end;

{ IXMLLicences_licence_maxvalues }

  IXMLLicences_licence_maxvalues = interface(IXMLNodeCollection)
    ['{CC96AE49-E055-4CCF-8D01-A75907F1240C}']
    { Property Accessors }
    function Get_Maxvalue(Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
    { Methods & Properties }
    function Add: IXMLLicences_licence_maxvalues_maxvalue;
    function Insert(const Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
    property Maxvalue[Index: Integer]: IXMLLicences_licence_maxvalues_maxvalue read Get_Maxvalue; default;
  end;

{ IXMLLicences_licence_maxvalues_maxvalue }

  IXMLLicences_licence_maxvalues_maxvalue = interface(IXMLNode)
    ['{591C45BF-949A-4942-982A-6DFE784F8FDF}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_ClassName: UnicodeString;
    function Get_Value: Integer;
    function Get_App_ids: IXMLLicences_licence_maxvalues_maxvalue_app_ids;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_ClassName(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
    { Methods & Properties }
    property Name: UnicodeString read Get_Name write Set_Name;
    property ClassName: UnicodeString read Get_ClassName write Set_ClassName;
    property Value: Integer read Get_Value write Set_Value;
    property App_ids: IXMLLicences_licence_maxvalues_maxvalue_app_ids read Get_App_ids;
  end;

{ IXMLLicences_licence_maxvalues_maxvalue_app_ids }

  IXMLLicences_licence_maxvalues_maxvalue_app_ids = interface(IXMLNodeCollection)
    ['{5106A600-63B3-4E14-950B-7385A5786625}']
    { Property Accessors }
    function Get_App_id(Index: Integer): Integer;
    { Methods & Properties }
    function Add(const App_id: Integer): IXMLNode;
    function Insert(const Index: Integer; const App_id: Integer): IXMLNode;
    property App_id[Index: Integer]: Integer read Get_App_id; default;
  end;

{ IXMLLicences_licence_parameters }

  IXMLLicences_licence_parameters = interface(IXMLNodeCollection)
    ['{12E68500-F025-4AE7-AB74-3658DD69BD91}']
    { Property Accessors }
    function Get_Parameter(Index: Integer): IXMLLicences_licence_parameters_parameter;
    { Methods & Properties }
    function Add: IXMLLicences_licence_parameters_parameter;
    function Insert(const Index: Integer): IXMLLicences_licence_parameters_parameter;
    property Parameter[Index: Integer]: IXMLLicences_licence_parameters_parameter read Get_Parameter; default;
  end;

{ IXMLLicences_licence_parameters_parameter }

  IXMLLicences_licence_parameters_parameter = interface(IXMLNode)
    ['{3EF29C18-5341-4992-93E7-3AA21AE4916B}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Value: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: UnicodeString);
    { Methods & Properties }
    property Name: UnicodeString read Get_Name write Set_Name;
    property Value: UnicodeString read Get_Value write Set_Value;
  end;

{ IXMLLicences_licence_modsavailability }

  IXMLLicences_licence_modsavailability = interface(IXMLNode)
    ['{FBC2B28C-7516-43CB-BC12-62C31FA49E6E}']
    { Property Accessors }
    function Get_Apps: IXMLLicences_licence_modsavailability_apps;
    { Methods & Properties }
    property Apps: IXMLLicences_licence_modsavailability_apps read Get_Apps;
  end;

{ IXMLLicences_licence_modsavailability_apps }

  IXMLLicences_licence_modsavailability_apps = interface(IXMLNodeCollection)
    ['{C92D3AE4-EB83-466F-BAFE-698B1E3AFA6C}']
    { Property Accessors }
    function Get_App(Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
    { Methods & Properties }
    function Add: IXMLLicences_licence_modsavailability_apps_app;
    function Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
    property App[Index: Integer]: IXMLLicences_licence_modsavailability_apps_app read Get_App; default;
  end;

{ IXMLLicences_licence_modsavailability_apps_app }

  IXMLLicences_licence_modsavailability_apps_app = interface(IXMLNode)
    ['{9E767854-EEFA-409B-A7E4-1F17CB6131FC}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Mods: IXMLLicences_licence_modsavailability_apps_app_mods;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
    { Methods & Properties }
    property Name: UnicodeString read Get_Name write Set_Name;
    property Id: Integer read Get_Id write Set_Id;
    property Mods: IXMLLicences_licence_modsavailability_apps_app_mods read Get_Mods;
  end;

{ IXMLLicences_licence_modsavailability_apps_app_mods }

  IXMLLicences_licence_modsavailability_apps_app_mods = interface(IXMLNodeCollection)
    ['{84CE6281-36C1-4BA0-8207-83A4F0EC52FA}']
    { Property Accessors }
    function Get_Mod_(Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
    { Methods & Properties }
    function Add: IXMLLicences_licence_modsavailability_apps_app_mods_mod;
    function Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
    property Mod_[Index: Integer]: IXMLLicences_licence_modsavailability_apps_app_mods_mod read Get_Mod_; default;
  end;

{ IXMLLicences_licence_modsavailability_apps_app_mods_mod }

  IXMLLicences_licence_modsavailability_apps_app_mods_mod = interface(IXMLNode)
    ['{FBC100E2-59E7-4D4C-A3F6-130454F5E303}']
    { Property Accessors }
    function Get_Tag: Integer;
    function Get_Name: UnicodeString;
    function Get_Value: Integer;
    function Get_Tempdate: UnicodeString;
    function Get_Tempvalue: UnicodeString;
    procedure Set_Tag(Value: Integer);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
    procedure Set_Tempdate(Value: UnicodeString);
    procedure Set_Tempvalue(Value: UnicodeString);
    { Methods & Properties }
    property Tag: Integer read Get_Tag write Set_Tag;
    property Name: UnicodeString read Get_Name write Set_Name;
    property Value: Integer read Get_Value write Set_Value;
    property Tempdate: UnicodeString read Get_Tempdate write Set_Tempdate;
    property Tempvalue: UnicodeString read Get_Tempvalue write Set_Tempvalue;
  end;

{ IXMLLicences_licence_privilages }

  IXMLLicences_licence_privilages = interface(IXMLNodeCollection)
    ['{667946E6-0982-4E6A-803E-FAE24EA5C292}']
    { Property Accessors }
    function Get_User(Index: Integer): IXMLLicences_licence_privilages_user;
    { Methods & Properties }
    function Add: IXMLLicences_licence_privilages_user;
    function Insert(const Index: Integer): IXMLLicences_licence_privilages_user;
    property User[Index: Integer]: IXMLLicences_licence_privilages_user read Get_User; default;
  end;

{ IXMLLicences_licence_privilages_user }

  IXMLLicences_licence_privilages_user = interface(IXMLNodeCollection)
    ['{83F7F0B8-7A7E-407C-813B-D7D456013851}']
    { Property Accessors }
    function Get_CompanyCode: UnicodeString;
    function Get_Application(Index: Integer): IXMLLicences_licence_privilages_user_application;
    procedure Set_CompanyCode(Value: UnicodeString);
    { Methods & Properties }
    function Add: IXMLLicences_licence_privilages_user_application;
    function Insert(const Index: Integer): IXMLLicences_licence_privilages_user_application;
    property CompanyCode: UnicodeString read Get_CompanyCode write Set_CompanyCode;
    property Application[Index: Integer]: IXMLLicences_licence_privilages_user_application read Get_Application; default;
  end;

{ IXMLLicences_licence_privilages_user_application }

  IXMLLicences_licence_privilages_user_application = interface(IXMLNodeCollection)
    ['{46F5E8BA-E88E-4A2B-A0FE-97A3144BB775}']
    { Property Accessors }
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Privilage(Index: Integer): IXMLTprivilage;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
    { Methods & Properties }
    function Add: IXMLTprivilage;
    function Insert(const Index: Integer): IXMLTprivilage;
    property Name: UnicodeString read Get_Name write Set_Name;
    property Id: Integer read Get_Id write Set_Id;
    property Privilage[Index: Integer]: IXMLTprivilage read Get_Privilage; default;
  end;

{ IXMLTprivilage }

  IXMLTprivilage = interface(IXMLNodeCollection)
    ['{58BF747D-9772-42C7-BA26-34979326E2FA}']
    { Property Accessors }
    function Get_Tag: Integer;
    function Get_Caption: UnicodeString;
    function Get_Privilage(Index: Integer): IXMLTprivilage;
    procedure Set_Tag(Value: Integer);
    procedure Set_Caption(Value: UnicodeString);
    { Methods & Properties }
    function Add: IXMLTprivilage;
    function Insert(const Index: Integer): IXMLTprivilage;
    property Tag: Integer read Get_Tag write Set_Tag;
    property Caption: UnicodeString read Get_Caption write Set_Caption;
    property Privilage[Index: Integer]: IXMLTprivilage read Get_Privilage; default;
  end;

{ Forward Decls }

  TXMLLicences = class;
  TXMLLicences_licence = class;
  TXMLLicences_licence_UserForisKM = class;
  TXMLLicences_licence_useradd = class;
  TXMLLicences_licence_useraddList = class;
  TXMLLicences_licence_useradd_usercode = class;
  TXMLLicences_licence_maxvalues = class;
  TXMLLicences_licence_maxvalues_maxvalue = class;
  TXMLLicences_licence_maxvalues_maxvalue_app_ids = class;
  TXMLLicences_licence_parameters = class;
  TXMLLicences_licence_parameters_parameter = class;
  TXMLLicences_licence_modsavailability = class;
  TXMLLicences_licence_modsavailability_apps = class;
  TXMLLicences_licence_modsavailability_apps_app = class;
  TXMLLicences_licence_modsavailability_apps_app_mods = class;
  TXMLLicences_licence_modsavailability_apps_app_mods_mod = class;
  TXMLLicences_licence_privilages = class;
  TXMLLicences_licence_privilages_user = class;
  TXMLLicences_licence_privilages_user_application = class;
  TXMLTprivilage = class;

{ TXMLLicences }

  TXMLLicences = class(TXMLNode, IXMLLicences)
  protected
    { IXMLLicences }
    function Get_Defaultuser: UnicodeString;
    function Get_CompanyCode: UnicodeString;
    function Get_INumber: UnicodeString;
    function Get_Name: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_TarifLimit: UnicodeString;
    function Get_NIP: UnicodeString;
    function Get_Street: UnicodeString;
    function Get_PostCode: UnicodeString;
    function Get_PlaceID: UnicodeString;
    function Get_PlaceSymbol: UnicodeString;
    function Get_Country: UnicodeString;
    function Get_Licence: IXMLLicences_licence;
    procedure Set_Defaultuser(Value: UnicodeString);
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_INumber(Value: UnicodeString);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_TarifLimit(Value: UnicodeString);
    procedure Set_NIP(Value: UnicodeString);
    procedure Set_Street(Value: UnicodeString);
    procedure Set_PostCode(Value: UnicodeString);
    procedure Set_PlaceID(Value: UnicodeString);
    procedure Set_PlaceSymbol(Value: UnicodeString);
    procedure Set_Country(Value: UnicodeString);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence }

  TXMLLicences_licence = class(TXMLNode, IXMLLicences_licence)
  private
    FUseradd: IXMLLicences_licence_useraddList;
  protected
    { IXMLLicences_licence }
    function Get_Number: Integer;
    function Get_User: UnicodeString;
    function Get_UserForisKMCode: UnicodeString;
    function Get_UserForisKM: IXMLLicences_licence_UserForisKM;
    function Get_Licencedate: UnicodeString;
    function Get_Licenceenddate: UnicodeString;
    function Get_Useradd: IXMLLicences_licence_useraddList;
    function Get_Maxvalues: IXMLLicences_licence_maxvalues;
    function Get_Parameters: IXMLLicences_licence_parameters;
    function Get_Modsavailability: IXMLLicences_licence_modsavailability;
    function Get_Privilages: IXMLLicences_licence_privilages;
    procedure Set_Number(Value: Integer);
    procedure Set_User(Value: UnicodeString);
    procedure Set_UserForisKMCode(Value: UnicodeString);
    procedure Set_Licencedate(Value: UnicodeString);
    procedure Set_Licenceenddate(Value: UnicodeString);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_UserForisKM }
  TXMLLicences_licence_UserForisKM = class(TXMLNode, IXMLLicences_licence_UserForisKM)
  protected
    { IXMLLicences_licence_UserForisKM }
    function Get_CompanyCode: UnicodeString;
    function Get_INumber: UnicodeString;
    function Get_Name: UnicodeString;
    function Get_CompanyType: UnicodeString;
    function Get_CompanyStatus: UnicodeString;
    function Get_NIP: UnicodeString;
    function Get_Street: UnicodeString;
    function Get_PostCode: UnicodeString;
    function Get_PlaceID: UnicodeString;
    procedure Set_CompanyCode(Value: UnicodeString);
    procedure Set_INumber(Value: UnicodeString);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_CompanyType(Value: UnicodeString);
    procedure Set_CompanyStatus(Value: UnicodeString);
    procedure Set_NIP(Value: UnicodeString);
    procedure Set_Street(Value: UnicodeString);
    procedure Set_PostCode(Value: UnicodeString);
    procedure Set_PlaceID(Value: UnicodeString);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_useradd }

  TXMLLicences_licence_useradd = class(TXMLNodeCollection, IXMLLicences_licence_useradd)
  protected
    { IXMLLicences_licence_useradd }
    function Get_Usercode(Index: Integer): IXMLLicences_licence_useradd_usercode;
    function Add: IXMLLicences_licence_useradd_usercode;
    function Insert(const Index: Integer): IXMLLicences_licence_useradd_usercode;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_useraddList }

  TXMLLicences_licence_useraddList = class(TXMLNodeCollection, IXMLLicences_licence_useraddList)
  protected
    { IXMLLicences_licence_useraddList }
    function Add: IXMLLicences_licence_useradd;
    function Insert(const Index: Integer): IXMLLicences_licence_useradd;

    function Get_Item(Index: Integer): IXMLLicences_licence_useradd;
  end;

{ TXMLLicences_licence_useradd_usercode }

  TXMLLicences_licence_useradd_usercode = class(TXMLNode, IXMLLicences_licence_useradd_usercode)
  protected
    { IXMLLicences_licence_useradd_usercode }
  end;

{ TXMLLicences_licence_maxvalues }

  TXMLLicences_licence_maxvalues = class(TXMLNodeCollection, IXMLLicences_licence_maxvalues)
  protected
    { IXMLLicences_licence_maxvalues }
    function Get_Maxvalue(Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
    function Add: IXMLLicences_licence_maxvalues_maxvalue;
    function Insert(const Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_maxvalues_maxvalue }

  TXMLLicences_licence_maxvalues_maxvalue = class(TXMLNode, IXMLLicences_licence_maxvalues_maxvalue)
  protected
    { IXMLLicences_licence_maxvalues_maxvalue }
    function Get_Name: UnicodeString;
    function Get_ClassName: UnicodeString;
    function Get_Value: Integer;
    function Get_App_ids: IXMLLicences_licence_maxvalues_maxvalue_app_ids;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_ClassName(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_maxvalues_maxvalue_app_ids }

  TXMLLicences_licence_maxvalues_maxvalue_app_ids = class(TXMLNodeCollection, IXMLLicences_licence_maxvalues_maxvalue_app_ids)
  protected
    { IXMLLicences_licence_maxvalues_maxvalue_app_ids }
    function Get_App_id(Index: Integer): Integer;
    function Add(const App_id: Integer): IXMLNode;
    function Insert(const Index: Integer; const App_id: Integer): IXMLNode;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_parameters }

  TXMLLicences_licence_parameters = class(TXMLNodeCollection, IXMLLicences_licence_parameters)
  protected
    { IXMLLicences_licence_parameters }
    function Get_Parameter(Index: Integer): IXMLLicences_licence_parameters_parameter;
    function Add: IXMLLicences_licence_parameters_parameter;
    function Insert(const Index: Integer): IXMLLicences_licence_parameters_parameter;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_parameters_parameter }

  TXMLLicences_licence_parameters_parameter = class(TXMLNode, IXMLLicences_licence_parameters_parameter)
  protected
    { IXMLLicences_licence_parameters_parameter }
    function Get_Name: UnicodeString;
    function Get_Value: UnicodeString;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: UnicodeString);
  end;

{ TXMLLicences_licence_modsavailability }

  TXMLLicences_licence_modsavailability = class(TXMLNode, IXMLLicences_licence_modsavailability)
  protected
    { IXMLLicences_licence_modsavailability }
    function Get_Apps: IXMLLicences_licence_modsavailability_apps;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_modsavailability_apps }

  TXMLLicences_licence_modsavailability_apps = class(TXMLNodeCollection, IXMLLicences_licence_modsavailability_apps)
  protected
    { IXMLLicences_licence_modsavailability_apps }
    function Get_App(Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
    function Add: IXMLLicences_licence_modsavailability_apps_app;
    function Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_modsavailability_apps_app }

  TXMLLicences_licence_modsavailability_apps_app = class(TXMLNode, IXMLLicences_licence_modsavailability_apps_app)
  protected
    { IXMLLicences_licence_modsavailability_apps_app }
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Mods: IXMLLicences_licence_modsavailability_apps_app_mods;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_modsavailability_apps_app_mods }

  TXMLLicences_licence_modsavailability_apps_app_mods = class(TXMLNodeCollection, IXMLLicences_licence_modsavailability_apps_app_mods)
  protected
    { IXMLLicences_licence_modsavailability_apps_app_mods }
    function Get_Mod_(Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
    function Add: IXMLLicences_licence_modsavailability_apps_app_mods_mod;
    function Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_modsavailability_apps_app_mods_mod }

  TXMLLicences_licence_modsavailability_apps_app_mods_mod = class(TXMLNode, IXMLLicences_licence_modsavailability_apps_app_mods_mod)
  protected
    { IXMLLicences_licence_modsavailability_apps_app_mods_mod }
    function Get_Tag: Integer;
    function Get_Name: UnicodeString;
    function Get_Value: Integer;
    function Get_Tempdate: UnicodeString;
    function Get_Tempvalue: UnicodeString;
    procedure Set_Tag(Value: Integer);
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Value(Value: Integer);
    procedure Set_Tempdate(Value: UnicodeString);
    procedure Set_Tempvalue(Value: UnicodeString);
  end;

{ TXMLLicences_licence_privilages }

  TXMLLicences_licence_privilages = class(TXMLNodeCollection, IXMLLicences_licence_privilages)
  protected
    { IXMLLicences_licence_privilages }
    function Get_User(Index: Integer): IXMLLicences_licence_privilages_user;
    function Add: IXMLLicences_licence_privilages_user;
    function Insert(const Index: Integer): IXMLLicences_licence_privilages_user;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_privilages_user }

  TXMLLicences_licence_privilages_user = class(TXMLNodeCollection, IXMLLicences_licence_privilages_user)
  protected
    { IXMLLicences_licence_privilages_user }
    function Get_CompanyCode: UnicodeString;
    function Get_Application(Index: Integer): IXMLLicences_licence_privilages_user_application;
    procedure Set_CompanyCode(Value: UnicodeString);
    function Add: IXMLLicences_licence_privilages_user_application;
    function Insert(const Index: Integer): IXMLLicences_licence_privilages_user_application;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLLicences_licence_privilages_user_application }

  TXMLLicences_licence_privilages_user_application = class(TXMLNodeCollection, IXMLLicences_licence_privilages_user_application)
  protected
    { IXMLLicences_licence_privilages_user_application }
    function Get_Name: UnicodeString;
    function Get_Id: Integer;
    function Get_Privilage(Index: Integer): IXMLTprivilage;
    procedure Set_Name(Value: UnicodeString);
    procedure Set_Id(Value: Integer);
    function Add: IXMLTprivilage;
    function Insert(const Index: Integer): IXMLTprivilage;
  public
    procedure AfterConstruction; override;
  end;

{ TXMLTprivilage }

  TXMLTprivilage = class(TXMLNodeCollection, IXMLTprivilage)
  protected
    { IXMLTprivilage }
    function Get_Tag: Integer;
    function Get_Caption: UnicodeString;
    function Get_Privilage(Index: Integer): IXMLTprivilage;
    procedure Set_Tag(Value: Integer);
    procedure Set_Caption(Value: UnicodeString);
    function Add: IXMLTprivilage;
    function Insert(const Index: Integer): IXMLTprivilage;
  public
    procedure AfterConstruction; override;
  end;

{ Global Functions }

function Getlicences(Doc: IXMLDocument): IXMLLicences;
function Loadlicences(const FileName: string): IXMLLicences;
function Newlicences: IXMLLicences;

const
  TargetNamespace = '';

implementation

{ Global Functions }

function Getlicences(Doc: IXMLDocument): IXMLLicences;
begin
  Result := Doc.GetDocBinding('licences', TXMLLicences, TargetNamespace) as IXMLLicences;
end;

function Loadlicences(const FileName: string): IXMLLicences;
begin
  Result := LoadXMLDocument(FileName).GetDocBinding('licences', TXMLLicences, TargetNamespace) as IXMLLicences;
end;

function Newlicences: IXMLLicences;
begin
  Result := NewXMLDocument.GetDocBinding('licences', TXMLLicences, TargetNamespace) as IXMLLicences;
end;

{ TXMLLicences }

procedure TXMLLicences.AfterConstruction;
begin
  RegisterChildNode('licence', TXMLLicences_licence);
  inherited;
end;

function TXMLLicences.Get_Defaultuser: UnicodeString;
begin
  Result := AttributeNodes['defaultuser'].Text;
end;

procedure TXMLLicences.Set_Defaultuser(Value: UnicodeString);
begin
  SetAttribute('defaultuser', Value);
end;

function TXMLLicences.Get_CompanyCode: UnicodeString;
begin
  Result := AttributeNodes['CompanyCode'].Text;
end;

procedure TXMLLicences.Set_CompanyCode(Value: UnicodeString);
begin
  SetAttribute('CompanyCode', Value);
end;

function TXMLLicences.Get_INumber: UnicodeString;
begin
  Result := AttributeNodes['INumber'].Text;
end;

procedure TXMLLicences.Set_INumber(Value: UnicodeString);
begin
  SetAttribute('INumber', Value);
end;

function TXMLLicences.Get_Name: UnicodeString;
begin
  Result := AttributeNodes['Name'].Text;
end;

procedure TXMLLicences.Set_Name(Value: UnicodeString);
begin
  SetAttribute('Name', Value);
end;

function TXMLLicences.Get_CompanyType: UnicodeString;
begin
  Result := AttributeNodes['CompanyType'].Text;
end;

function TXMLLicences.Get_Country: UnicodeString;
begin
  try
    Result := AttributeNodes['Country'].Text;
  except
    Result := '';
  end;
end;

procedure TXMLLicences.Set_CompanyType(Value: UnicodeString);
begin
  SetAttribute('CompanyType', Value);
end;

procedure TXMLLicences.Set_Country(Value: UnicodeString);
begin
  try
    SetAttribute('Country', Value);
  except
  end;
end;

function TXMLLicences.Get_CompanyStatus: UnicodeString;
begin
  Result := AttributeNodes['CompanyStatus'].Text;
end;

function TXMLLicences.Get_TarifLimit: UnicodeString;
begin
  Result := AttributeNodes['TarifLimit'].Text;
end;

procedure TXMLLicences.Set_CompanyStatus(Value: UnicodeString);
begin
  SetAttribute('CompanyStatus', Value);
end;

procedure TXMLLicences.Set_TarifLimit(Value: UnicodeString);
begin
  SetAttribute('TarifLimit', Value);
end;

function TXMLLicences.Get_NIP: UnicodeString;
begin
  Result := AttributeNodes['NIP'].Text;
end;

procedure TXMLLicences.Set_NIP(Value: UnicodeString);
begin
  SetAttribute('NIP', Value);
end;

function TXMLLicences.Get_Street: UnicodeString;
begin
  Result := AttributeNodes['Street'].Text;
end;

procedure TXMLLicences.Set_Street(Value: UnicodeString);
begin
  SetAttribute('Street', Value);
end;

function TXMLLicences.Get_PostCode: UnicodeString;
begin
  Result := AttributeNodes['PostCode'].Text;
end;

procedure TXMLLicences.Set_PostCode(Value: UnicodeString);
begin
  SetAttribute('PostCode', Value);
end;

function TXMLLicences.Get_PlaceID: UnicodeString;
begin
  Result := AttributeNodes['PlaceID'].Text;
end;

function TXMLLicences.Get_PlaceSymbol: UnicodeString;
begin
  try
    Result := AttributeNodes['PlaceSymbol'].Text;
  except
    Result := '';
  end;
end;

procedure TXMLLicences.Set_PlaceID(Value: UnicodeString);
begin
  SetAttribute('PlaceID', Value);
end;

procedure TXMLLicences.Set_PlaceSymbol(Value: UnicodeString);
begin
  try
    SetAttribute('PlaceSymbol', Value);
  except
  end;
end;

function TXMLLicences.Get_Licence: IXMLLicences_licence;
begin
  Result := ChildNodes['licence'] as IXMLLicences_licence;
end;

{ TXMLLicences_licence }

procedure TXMLLicences_licence.AfterConstruction;
begin
  RegisterChildNode('useradd', TXMLLicences_licence_useradd);
  RegisterChildNode('maxvalues', TXMLLicences_licence_maxvalues);
  RegisterChildNode('parameters', TXMLLicences_licence_parameters);
  RegisterChildNode('modsavailability', TXMLLicences_licence_modsavailability);
  RegisterChildNode('privilages', TXMLLicences_licence_privilages);
  FUseradd := CreateCollection(TXMLLicences_licence_useraddList, IXMLLicences_licence_useradd, 'useradd') as IXMLLicences_licence_useraddList;
  inherited;
end;

function TXMLLicences_licence.Get_Number: Integer;
begin
  Result := AttributeNodes['number'].NodeValue;
end;

procedure TXMLLicences_licence.Set_Number(Value: Integer);
begin
  SetAttribute('number', Value);
end;

function TXMLLicences_licence.Get_User: UnicodeString;
begin
  Result := ChildNodes['user'].Text;
end;

procedure TXMLLicences_licence.Set_User(Value: UnicodeString);
begin
  ChildNodes['user'].NodeValue := Value;
end;

function TXMLLicences_licence.Get_UserForisKM: IXMLLicences_licence_UserForisKM;
begin
  Result := ChildNodes['userforiskm'] as IXMLLicences_licence_UserForisKM;
end;

function TXMLLicences_licence.Get_UserForisKMCode: UnicodeString;
begin
  Result := ChildNodes['userforiskm'].Text;
end;

procedure TXMLLicences_licence.Set_UserForisKMCode(Value: UnicodeString);
begin
  ChildNodes['userforiskm'].NodeValue := Value;
end;

function TXMLLicences_licence.Get_Licencedate: UnicodeString;
begin
  Result := ChildNodes['licencedate'].Text;
end;

procedure TXMLLicences_licence.Set_Licencedate(Value: UnicodeString);
begin
  ChildNodes['licencedate'].NodeValue := Value;
end;

function TXMLLicences_licence.Get_Licenceenddate: UnicodeString;
begin
  Result := ChildNodes['licenceenddate'].Text;
end;

procedure TXMLLicences_licence.Set_Licenceenddate(Value: UnicodeString);
begin
  ChildNodes['licenceenddate'].NodeValue := Value;
end;

function TXMLLicences_licence.Get_Useradd: IXMLLicences_licence_useraddList;
begin
  Result := FUseradd;
end;

function TXMLLicences_licence.Get_Maxvalues: IXMLLicences_licence_maxvalues;
begin
  Result := ChildNodes['maxvalues'] as IXMLLicences_licence_maxvalues;
end;

function TXMLLicences_licence.Get_Parameters: IXMLLicences_licence_parameters;
begin
  Result := ChildNodes['parameters'] as IXMLLicences_licence_parameters;
end;

function TXMLLicences_licence.Get_Modsavailability: IXMLLicences_licence_modsavailability;
begin
  Result := ChildNodes['modsavailability'] as IXMLLicences_licence_modsavailability;
end;

function TXMLLicences_licence.Get_Privilages: IXMLLicences_licence_privilages;
begin
  Result := ChildNodes['privilages'] as IXMLLicences_licence_privilages;
end;

{ TXMLLicences_licence_useradd }

procedure TXMLLicences_licence_useradd.AfterConstruction;
begin
  RegisterChildNode('usercode', TXMLLicences_licence_useradd_usercode);
  ItemTag := 'usercode';
  ItemInterface := IXMLLicences_licence_useradd_usercode;
  inherited;
end;

function TXMLLicences_licence_useradd.Get_Usercode(Index: Integer): IXMLLicences_licence_useradd_usercode;
begin
  Result := List[Index] as IXMLLicences_licence_useradd_usercode;
end;

function TXMLLicences_licence_useradd.Add: IXMLLicences_licence_useradd_usercode;
begin
  Result := AddItem(-1) as IXMLLicences_licence_useradd_usercode;
end;

function TXMLLicences_licence_useradd.Insert(const Index: Integer): IXMLLicences_licence_useradd_usercode;
begin
  Result := AddItem(Index) as IXMLLicences_licence_useradd_usercode;
end;

{ TXMLLicences_licence_useraddList }

function TXMLLicences_licence_useraddList.Add: IXMLLicences_licence_useradd;
begin
  Result := AddItem(-1) as IXMLLicences_licence_useradd;
end;

function TXMLLicences_licence_useraddList.Insert(const Index: Integer): IXMLLicences_licence_useradd;
begin
  Result := AddItem(Index) as IXMLLicences_licence_useradd;
end;

function TXMLLicences_licence_useraddList.Get_Item(Index: Integer): IXMLLicences_licence_useradd;
begin
  Result := List[Index] as IXMLLicences_licence_useradd;
end;

{ TXMLLicences_licence_useradd_usercode }

{ TXMLLicences_licence_maxvalues }

procedure TXMLLicences_licence_maxvalues.AfterConstruction;
begin
  RegisterChildNode('maxvalue', TXMLLicences_licence_maxvalues_maxvalue);
  ItemTag := 'maxvalue';
  ItemInterface := IXMLLicences_licence_maxvalues_maxvalue;
  inherited;
end;

function TXMLLicences_licence_maxvalues.Get_Maxvalue(Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
begin
  Result := List[Index] as IXMLLicences_licence_maxvalues_maxvalue;
end;

function TXMLLicences_licence_maxvalues.Add: IXMLLicences_licence_maxvalues_maxvalue;
begin
  Result := AddItem(-1) as IXMLLicences_licence_maxvalues_maxvalue;
end;

function TXMLLicences_licence_maxvalues.Insert(const Index: Integer): IXMLLicences_licence_maxvalues_maxvalue;
begin
  Result := AddItem(Index) as IXMLLicences_licence_maxvalues_maxvalue;
end;

{ TXMLLicences_licence_maxvalues_maxvalue }

procedure TXMLLicences_licence_maxvalues_maxvalue.AfterConstruction;
begin
  RegisterChildNode('app_ids', TXMLLicences_licence_maxvalues_maxvalue_app_ids);
  inherited;
end;

function TXMLLicences_licence_maxvalues_maxvalue.Get_Name: UnicodeString;
begin
  Result := ChildNodes['name'].Text;
end;

function TXMLLicences_licence_maxvalues_maxvalue.Get_ClassName: UnicodeString;
begin
  if AttributeNodes.FindNode('classname') <> nil then
    Result :=  AttributeNodes['classname'].Text
  else
    Result := '';
end;

procedure TXMLLicences_licence_maxvalues_maxvalue.Set_ClassName(Value: UnicodeString);
begin
  SetAttribute('classname', Value);
end;

procedure TXMLLicences_licence_maxvalues_maxvalue.Set_Name(Value: UnicodeString);
begin
  ChildNodes['name'].NodeValue := Value;
end;

function TXMLLicences_licence_maxvalues_maxvalue.Get_Value: Integer;
begin
  Result := ChildNodes['value'].NodeValue;
end;

procedure TXMLLicences_licence_maxvalues_maxvalue.Set_Value(Value: Integer);
begin
  ChildNodes['value'].NodeValue := Value;
end;

function TXMLLicences_licence_maxvalues_maxvalue.Get_App_ids: IXMLLicences_licence_maxvalues_maxvalue_app_ids;
begin
  Result := ChildNodes['app_ids'] as IXMLLicences_licence_maxvalues_maxvalue_app_ids;
end;

{ TXMLLicences_licence_maxvalues_maxvalue_app_ids }

procedure TXMLLicences_licence_maxvalues_maxvalue_app_ids.AfterConstruction;
begin
  ItemTag := 'app_id';
  ItemInterface := IXMLNode;
  inherited;
end;

function TXMLLicences_licence_maxvalues_maxvalue_app_ids.Get_App_id(Index: Integer): Integer;
begin
  Result := List[Index].NodeValue;
end;

function TXMLLicences_licence_maxvalues_maxvalue_app_ids.Add(const App_id: Integer): IXMLNode;
begin
  Result := AddItem(-1);
  Result.NodeValue := App_id;
end;

function TXMLLicences_licence_maxvalues_maxvalue_app_ids.Insert(const Index: Integer; const App_id: Integer): IXMLNode;
begin
  Result := AddItem(Index);
  Result.NodeValue := App_id;
end;

{ TXMLLicences_licence_parameters }

procedure TXMLLicences_licence_parameters.AfterConstruction;
begin
  RegisterChildNode('parameter', TXMLLicences_licence_parameters_parameter);
  ItemTag := 'parameter';
  ItemInterface := IXMLLicences_licence_parameters_parameter;
  inherited;
end;

function TXMLLicences_licence_parameters.Get_Parameter(Index: Integer): IXMLLicences_licence_parameters_parameter;
begin
  Result := List[Index] as IXMLLicences_licence_parameters_parameter;
end;

function TXMLLicences_licence_parameters.Add: IXMLLicences_licence_parameters_parameter;
begin
  Result := AddItem(-1) as IXMLLicences_licence_parameters_parameter;
end;

function TXMLLicences_licence_parameters.Insert(const Index: Integer): IXMLLicences_licence_parameters_parameter;
begin
  Result := AddItem(Index) as IXMLLicences_licence_parameters_parameter;
end;

{ TXMLLicences_licence_parameters_parameter }

function TXMLLicences_licence_parameters_parameter.Get_Name: UnicodeString;
begin
  Result := ChildNodes['name'].Text;
end;

procedure TXMLLicences_licence_parameters_parameter.Set_Name(Value: UnicodeString);
begin
  ChildNodes['name'].NodeValue := Value;
end;

function TXMLLicences_licence_parameters_parameter.Get_Value: UnicodeString;
begin
  Result := ChildNodes['value'].Text;
end;

procedure TXMLLicences_licence_parameters_parameter.Set_Value(Value: UnicodeString);
begin
  ChildNodes['value'].NodeValue := Value;
end;

{ TXMLLicences_licence_modsavailability }

procedure TXMLLicences_licence_modsavailability.AfterConstruction;
begin
  RegisterChildNode('apps', TXMLLicences_licence_modsavailability_apps);
  inherited;
end;

function TXMLLicences_licence_modsavailability.Get_Apps: IXMLLicences_licence_modsavailability_apps;
begin
  Result := ChildNodes['apps'] as IXMLLicences_licence_modsavailability_apps;
end;

{ TXMLLicences_licence_modsavailability_apps }

procedure TXMLLicences_licence_modsavailability_apps.AfterConstruction;
begin
  RegisterChildNode('app', TXMLLicences_licence_modsavailability_apps_app);
  ItemTag := 'app';
  ItemInterface := IXMLLicences_licence_modsavailability_apps_app;
  inherited;
end;

function TXMLLicences_licence_modsavailability_apps.Get_App(Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
begin
  Result := List[Index] as IXMLLicences_licence_modsavailability_apps_app;
end;

function TXMLLicences_licence_modsavailability_apps.Add: IXMLLicences_licence_modsavailability_apps_app;
begin
  Result := AddItem(-1) as IXMLLicences_licence_modsavailability_apps_app;
end;

function TXMLLicences_licence_modsavailability_apps.Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app;
begin
  Result := AddItem(Index) as IXMLLicences_licence_modsavailability_apps_app;
end;

{ TXMLLicences_licence_modsavailability_apps_app }

procedure TXMLLicences_licence_modsavailability_apps_app.AfterConstruction;
begin
  RegisterChildNode('mods', TXMLLicences_licence_modsavailability_apps_app_mods);
  inherited;
end;

function TXMLLicences_licence_modsavailability_apps_app.Get_Name: UnicodeString;
begin
  Result := AttributeNodes['name'].Text;
end;

procedure TXMLLicences_licence_modsavailability_apps_app.Set_Name(Value: UnicodeString);
begin
  SetAttribute('name', Value);
end;

function TXMLLicences_licence_modsavailability_apps_app.Get_Id: Integer;
begin
  Result := AttributeNodes['id'].NodeValue;
end;

procedure TXMLLicences_licence_modsavailability_apps_app.Set_Id(Value: Integer);
begin
  SetAttribute('id', Value);
end;

function TXMLLicences_licence_modsavailability_apps_app.Get_Mods: IXMLLicences_licence_modsavailability_apps_app_mods;
begin
  Result := ChildNodes['mods'] as IXMLLicences_licence_modsavailability_apps_app_mods;
end;

{ TXMLLicences_licence_modsavailability_apps_app_mods }

procedure TXMLLicences_licence_modsavailability_apps_app_mods.AfterConstruction;
begin
  RegisterChildNode('mod', TXMLLicences_licence_modsavailability_apps_app_mods_mod);
  ItemTag := 'mod';
  ItemInterface := IXMLLicences_licence_modsavailability_apps_app_mods_mod;
  inherited;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods.Get_Mod_(Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
begin
  Result := List[Index] as IXMLLicences_licence_modsavailability_apps_app_mods_mod;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods.Add: IXMLLicences_licence_modsavailability_apps_app_mods_mod;
begin
  Result := AddItem(-1) as IXMLLicences_licence_modsavailability_apps_app_mods_mod;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods.Insert(const Index: Integer): IXMLLicences_licence_modsavailability_apps_app_mods_mod;
begin
  Result := AddItem(Index) as IXMLLicences_licence_modsavailability_apps_app_mods_mod;
end;

{ TXMLLicences_licence_modsavailability_apps_app_mods_mod }

function TXMLLicences_licence_modsavailability_apps_app_mods_mod.Get_Tag: Integer;
begin
  Result := AttributeNodes['tag'].NodeValue;
end;

procedure TXMLLicences_licence_modsavailability_apps_app_mods_mod.Set_Tag(Value: Integer);
begin
  SetAttribute('tag', Value);
end;

function TXMLLicences_licence_modsavailability_apps_app_mods_mod.Get_Name: UnicodeString;
begin
  Result := ChildNodes['name'].Text;
end;

procedure TXMLLicences_licence_modsavailability_apps_app_mods_mod.Set_Name(Value: UnicodeString);
begin
  ChildNodes['name'].NodeValue := Value;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods_mod.Get_Value: Integer;
begin
  Result := ChildNodes['value'].NodeValue;
end;

procedure TXMLLicences_licence_modsavailability_apps_app_mods_mod.Set_Value(Value: Integer);
begin
  ChildNodes['value'].NodeValue := Value;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods_mod.Get_Tempdate: UnicodeString;
begin
  Result := ChildNodes['tempdate'].Text;
end;

procedure TXMLLicences_licence_modsavailability_apps_app_mods_mod.Set_Tempdate(Value: UnicodeString);
begin
  ChildNodes['tempdate'].NodeValue := Value;
end;

function TXMLLicences_licence_modsavailability_apps_app_mods_mod.Get_Tempvalue: UnicodeString;
begin
  Result := ChildNodes['tempvalue'].Text;
end;

procedure TXMLLicences_licence_modsavailability_apps_app_mods_mod.Set_Tempvalue(Value: UnicodeString);
begin
  ChildNodes['tempvalue'].NodeValue := Value;
end;

{ TXMLLicences_licence_privilages }

procedure TXMLLicences_licence_privilages.AfterConstruction;
begin
  RegisterChildNode('user', TXMLLicences_licence_privilages_user);
  ItemTag := 'user';
  ItemInterface := IXMLLicences_licence_privilages_user;
  inherited;
end;

function TXMLLicences_licence_privilages.Get_User(Index: Integer): IXMLLicences_licence_privilages_user;
begin
  Result := List[Index] as IXMLLicences_licence_privilages_user;
end;

function TXMLLicences_licence_privilages.Add: IXMLLicences_licence_privilages_user;
begin
  Result := AddItem(-1) as IXMLLicences_licence_privilages_user;
end;

function TXMLLicences_licence_privilages.Insert(const Index: Integer): IXMLLicences_licence_privilages_user;
begin
  Result := AddItem(Index) as IXMLLicences_licence_privilages_user;
end;

{ TXMLLicences_licence_privilages_user }

procedure TXMLLicences_licence_privilages_user.AfterConstruction;
begin
  RegisterChildNode('application', TXMLLicences_licence_privilages_user_application);
  ItemTag := 'application';
  ItemInterface := IXMLLicences_licence_privilages_user_application;
  inherited;
end;

function TXMLLicences_licence_privilages_user.Get_CompanyCode: UnicodeString;
begin
  Result := AttributeNodes['companycode'].Text;
end;

procedure TXMLLicences_licence_privilages_user.Set_CompanyCode(Value: UnicodeString);
begin
  SetAttribute('companycode', Value);
end;

function TXMLLicences_licence_privilages_user.Get_Application(Index: Integer): IXMLLicences_licence_privilages_user_application;
begin
  Result := List[Index] as IXMLLicences_licence_privilages_user_application;
end;

function TXMLLicences_licence_privilages_user.Add: IXMLLicences_licence_privilages_user_application;
begin
  Result := AddItem(-1) as IXMLLicences_licence_privilages_user_application;
end;

function TXMLLicences_licence_privilages_user.Insert(const Index: Integer): IXMLLicences_licence_privilages_user_application;
begin
  Result := AddItem(Index) as IXMLLicences_licence_privilages_user_application;
end;

{ TXMLLicences_licence_privilages_user_application }

procedure TXMLLicences_licence_privilages_user_application.AfterConstruction;
begin
  RegisterChildNode('privilage', TXMLTprivilage);
  ItemTag := 'privilage';
  ItemInterface := IXMLTprivilage;
  inherited;
end;

function TXMLLicences_licence_privilages_user_application.Get_Name: UnicodeString;
begin
  Result := AttributeNodes['name'].Text;
end;

procedure TXMLLicences_licence_privilages_user_application.Set_Name(Value: UnicodeString);
begin
  SetAttribute('name', Value);
end;

function TXMLLicences_licence_privilages_user_application.Get_Id: Integer;
begin
  Result := AttributeNodes['id'].NodeValue;
end;

procedure TXMLLicences_licence_privilages_user_application.Set_Id(Value: Integer);
begin
  SetAttribute('id', Value);
end;

function TXMLLicences_licence_privilages_user_application.Get_Privilage(Index: Integer): IXMLTprivilage;
begin
  Result := List[Index] as IXMLTprivilage;
end;

function TXMLLicences_licence_privilages_user_application.Add: IXMLTprivilage;
begin
  Result := AddItem(-1) as IXMLTprivilage;
end;

function TXMLLicences_licence_privilages_user_application.Insert(const Index: Integer): IXMLTprivilage;
begin
  Result := AddItem(Index) as IXMLTprivilage;
end;

{ TXMLTprivilage }

procedure TXMLTprivilage.AfterConstruction;
begin
  RegisterChildNode('privilage', TXMLTprivilage);
  ItemTag := 'privilage';
  ItemInterface := IXMLTprivilage;
  inherited;
end;

function TXMLTprivilage.Get_Tag: Integer;
begin
  Result := AttributeNodes['tag'].NodeValue;
end;

procedure TXMLTprivilage.Set_Tag(Value: Integer);
begin
  SetAttribute('tag', Value);
end;

function TXMLTprivilage.Get_Caption: UnicodeString;
begin
  Result := AttributeNodes['caption'].Text;
end;

procedure TXMLTprivilage.Set_Caption(Value: UnicodeString);
begin
  SetAttribute('caption', Value);
end;

function TXMLTprivilage.Get_Privilage(Index: Integer): IXMLTprivilage;
begin
  Result := List[Index] as IXMLTprivilage;
end;

function TXMLTprivilage.Add: IXMLTprivilage;
begin
  Result := AddItem(-1) as IXMLTprivilage;
end;

function TXMLTprivilage.Insert(const Index: Integer): IXMLTprivilage;
begin
  Result := AddItem(Index) as IXMLTprivilage;
end;

{ TXMLLicences_licence_UserForisKM }
procedure TXMLLicences_licence_UserForisKM.AfterConstruction;
begin
  RegisterChildNode('userforiskm', TXMLLicences_licence_UserForisKM);
  inherited;
end;

function TXMLLicences_licence_UserForisKM.Get_CompanyCode: UnicodeString;
begin
  Result := AttributeNodes['CompanyCode'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_CompanyCode(Value: UnicodeString);
begin
  SetAttribute('CompanyCode', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_INumber: UnicodeString;
begin
  Result := AttributeNodes['INumber'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_INumber(Value: UnicodeString);
begin
  SetAttribute('INumber', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_Name: UnicodeString;
begin
  Result := AttributeNodes['Name'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_Name(Value: UnicodeString);
begin
  SetAttribute('Name', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_CompanyType: UnicodeString;
begin
  Result := AttributeNodes['CompanyType'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_CompanyType(Value: UnicodeString);
begin
  SetAttribute('CompanyType', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_CompanyStatus: UnicodeString;
begin
  Result := AttributeNodes['CompanyStatus'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_CompanyStatus(Value: UnicodeString);
begin
  SetAttribute('CompanyStatus', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_NIP: UnicodeString;
begin
  Result := AttributeNodes['NIP'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_NIP(Value: UnicodeString);
begin
  SetAttribute('NIP', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_Street: UnicodeString;
begin
  Result := AttributeNodes['Street'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_Street(Value: UnicodeString);
begin
  SetAttribute('Street', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_PostCode: UnicodeString;
begin
  Result := AttributeNodes['PostCode'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_PostCode(Value: UnicodeString);
begin
  SetAttribute('PostCode', Value);
end;

function TXMLLicences_licence_UserForisKM.Get_PlaceID: UnicodeString;
begin
  Result := AttributeNodes['PlaceID'].Text;
end;

procedure TXMLLicences_licence_UserForisKM.Set_PlaceID(Value: UnicodeString);
begin
  SetAttribute('PlaceID', Value);
end;

end.