unit emar105.classes;

interface

uses
  classes,
  Windows,
  SysUtils,
  System.AnsiStrings,
  emar_base,
  emar_105,
  emar.base.classes,
  emar105.Struct,
  emar_consts,
  emar.usb.devices;

type

{$REGION ' Classes - forward declarations '}
  TEmar105_OIK    = class;
  TEmar105_Consts = class;
  { ---------------------------------------------------------------------------- }
  TEmar105_Company             = class; // 08
  TEmar105_CompanyList         = class;
  TEmar105_BusStop             = class; // 09
  TEmar105_BusStopList         = class;
  TEmar105_Ride                = class; // 10
  TEmar105_RideList            = class;
  TEmar105_RideRoute           = class; // 11
  TEmar105_RideRouteList       = class;
  TEmar105_RideTariff          = class; // 12
  TEmar105_RideTariffList      = class;
  TEmar105_RideReduction       = class; // 13
  TEmar105_RideReductionList   = class;
  TEmar105_Calendar            = class; // 14
  TEmar105_CalendarList        = class;
  TEmar105_RideDesignation     = class; // 15
  TEmar105_RideDesignationList = class;
  TEmar105_Tariff              = class; // 16
  TEmar105_TariffList          = class;
  TEmar105_Price               = class; // 17
  TEmar105_PriceList           = class;
  // TEmar105_PriceIndexes = class;                       // 18 i 19
  // TEmar105_FarePriceScaleZoneNumber = class;           // 20
  TEmar105_CurrencyExchange                    = class; // 21
  TEmar105_CurrencyExchangeList                = class;
  TEmar105_PaymentType                         = class; // 22
  TEmar105_PaymentTypeList                     = class;
  TEmar105_FarePriceReduction                  = class; // 23 i 44
  TEmar105_FarePriceReductionList              = class;
  TEmar105_Task                                = class; // 24
  TEmar105_TaskList                            = class;
  TEmar105_TaskPosition                        = class; // 25
  TEmar105_TaskPositionList                    = class;
  TEmar105_Line                                = class; // 26
  TEmar105_LineList                            = class;
  TEmar105_RideBonus                           = class; // 27
  TEmar105_RideBonusList                       = class;
  TEmar105_RideHandlingFee                     = class; // 28
  TEmar105_RideHandlingFeeList                 = class;
  TEmar105_AdditionalFee                       = class; // 29
  TEmar105_AdditionalFeeList                   = class;
  TEmar105_LuggageTariff                       = class; // 30
  TEmar105_LuggageTariffList                   = class;
  TEmar105_ReferenceRide                       = class; // 31
  TEmar105_ReferenceRideList                   = class;
  TEmar105_AcceptedTicketOwner                 = class; // 32
  TEmar105_AcceptedTicketOwnerList             = class;
  TEmar105_AcceptedTradeReliefCardOwner        = class; // 33
  TEmar105_AcceptedTradeReliefCardOwnerList    = class;
  TEmar105_ProprietaryMIFAREcard               = class; // 34
  TEmar105_ProprietaryMIFAREcardList           = class;
  TEmar105_RidesCityTariff                     = class; // 35
  TEmar105_RidesCityTariffList                 = class;
  TEmar105_CityTariffPrice                     = class; // 36
  TEmar105_CityTariffPriceList                 = class;
  TEmar105_LineRoute                           = class; // 37
  TEmar105_LineRouteList                       = class;
  TEmar105_LettersBusStopSideNumber            = class; // 38
  TEmar105_LettersBusStopSideNumberList        = class;
  TEmar105_ExchangeRateAfterChangeCurrency     = class; // 39
  TEmar105_ExchangeRateAfterChangeCurrencyList = class;
  TEmar105_TicketNextPeriod                    = class; // 40
  TEmar105_TicketNextPeriodList                = class;
  TEmar105_Shortcut                            = class; // 41
  TEmar105_ShortcutList                        = class;
  TEmar105_AcceptedInspectorsCompany           = class; // 42
  TEmar105_AcceptedInspectorsCompanyList       = class;
  TEmar105_ZoneNumber                          = class; // 43
  TEmar105_ZoneNumberList                      = class;
  TEmar105_ChargingTariff                      = class; // 45
  TEmar105_ChargingTariffList                  = class;
  TEmar105_ChargingTariffPrice                 = class; // 46
  TEmar105_ChargingTariffPriceList             = class;
  TEmar105_Driver                              = class; // 48
  TEmar105_DriverList                          = class;

{$ENDREGION}
{$REGION ' Dane wejściowe '}
{$REGION ' 03 - TEmar105_OIK '}

  TEmar105_OIK = class(TEmar_Oik, IEmar105_OIK)
  private
    fSalePrefSet:            IEmar_DriverSalePrefSet;
    fCardSerialNumber:       cardinal;
    fMaufactureDate:         string;
    fCardType:               string;
    fCardCapacityCode:       integer;
    fCardRegisterDate:       string;
    fNIP:                    string;
    fHeader1:                string;
    fHeader2:                string;
    fHeader3:                string;
    fHeader4:                string;
    fFooter1:                string;
    fFooter2:                string;
    fFooter3:                string;
    fDriverNumber:           cardinal;
    fDriverFirstName:        string;
    fDriverLastName:         string;
    fPIN:                    integer;
    fEmployeeStatus:         integer;
    fCardAssignDate:         string;
    fTimeTableFileName:      string;
    fTimeTableSaveFileDate:  string;
    fTimeTableSaveFileTime:  string;
    fReadyCode:              integer;
    fTaskReportFileName:     string;
    fStatesSaveDate:         string;
    fStatesSaveTime:         string;
    fCompanyCardOwner:       integer;
    fNextReportCode:         string;
    fReportFileNameAddStand: string;
    fBranchNumber:           integer;
    fTimeTableFileExt:       string;
    fStandAloneWorkMode:     boolean;
    fAddDataSaveDate:        string;
    fAddDataSaveTime:        string;
    fDDFileName:             string;
    fPZAddedCardCount:       integer;
    fPZDeletedCardCount:     integer;
    fPPAddedCardCount:       integer;
    fAddDataProgram:         string;
    fReadCardDate:           string;
    fReadCardTime:           string;
    fReadCardProgram:        string;
    { Property methods }
    function GetCardSerialNumber: cardinal; stdcall;
    function GetManufactureDate: pchar; stdcall;
    function GetCardType: pchar; stdcall;
    function GetCardCapacityCode: integer; stdcall;
    function GetCardRegisterDate: pchar; stdcall;
    function GetNIP: pchar; stdcall;
    function GetHeader1: pchar; stdcall;
    function GetHeader2: pchar; stdcall;
    function GetHeader3: pchar; stdcall;
    function GetHeader4: pchar; stdcall;
    function GetFooter1: pchar; stdcall;
    function GetFooter2: pchar; stdcall;
    function GetFooter3: pchar; stdcall;
    function GetDriverNumber: cardinal; stdcall;
    function GetDriverFirstName: pchar; stdcall;
    function GetDriverLastName: pchar; stdcall;
    function GetPIN: integer; stdcall;
    function GetEmployeeStatus: integer; stdcall;
    function GetCardAssignDate: pchar; stdcall;
    function GetTimeTableFileName: pchar; stdcall;
    function GetTimeTableSaveFileDate: pchar; stdcall;
    function GetTimeTableSaveFileTime: pchar; stdcall;
    function GetReadyCode: integer; stdcall;
    function GetTaskReportFileName: pchar; stdcall;
    function GetStatesSaveDate: pchar; stdcall;
    function GetStatesSaveTime: pchar; stdcall;
    function GetCompanyCardOwner: integer; stdcall;
    function GetNextReportCode: pchar; stdcall;
    function GetReportFileNameAddStand: pchar; stdcall;
    function GetBranchNumber: integer; stdcall;
    function GetTimeTableFileExt: pchar; stdcall;
    function GetStandAloneWorkMode: boolean; stdcall;
    function GetAddDataSaveDate: pchar; stdcall;
    function GetAddDataSaveTime: pchar; stdcall;
    function GetDDFileName: pchar; stdcall;
    function GetPZAddedCardCount: integer; stdcall;
    function GetPZDeletedCardCount: integer; stdcall;
    function GetPPAddedCardCount: integer; stdcall;
    function GetAddDataProgram: pchar; stdcall;
    function GetReadCardDate: pchar; stdcall;
    function GetReadCardTime: pchar; stdcall;
    function GetReadCardProgram: pchar; stdcall;
    procedure SetCardSerialNumber(const Value: cardinal); stdcall;
    procedure SetManufactureDate(const Value: pchar); stdcall;
    procedure SetCardType(const Value: pchar); stdcall;
    procedure SetCardCapacityCode(const Value: integer); stdcall;
    procedure SetCardRegisterDate(const Value: pchar); stdcall;
    procedure SetNIP(const Value: pchar); stdcall;
    procedure SetHeader1(const Value: pchar); stdcall;
    procedure SetHeader2(const Value: pchar); stdcall;
    procedure SetHeader3(const Value: pchar); stdcall;
    procedure SetHeader4(const Value: pchar); stdcall;
    procedure SetFooter1(const Value: pchar); stdcall;
    procedure SetFooter2(const Value: pchar); stdcall;
    procedure SetFooter3(const Value: pchar); stdcall;
    procedure SetDriverNumber(const Value: cardinal); stdcall;
    procedure SetDriverFirstName(const Value: pchar); stdcall;
    procedure SetDriverLastName(const Value: pchar); stdcall;
    procedure SetPIN(const Value: integer); stdcall;
    procedure SetEmployeeStatus(const Value: integer); stdcall;
    procedure SetCardAssignDate(const Value: pchar); stdcall;
    procedure SetTimeTableFileName(const Value: pchar); stdcall;
    procedure SetTimeTableSaveFileDate(const Value: pchar); stdcall;
    procedure SetTimeTableSaveFileTime(const Value: pchar); stdcall;
    procedure SetReadyCode(const Value: integer); stdcall;
    procedure SetTaskReportFileName(const Value: pchar); stdcall;
    procedure SetStatesSaveDate(const Value: pchar); stdcall;
    procedure SetStatesSaveTime(const Value: pchar); stdcall;
    procedure SetCompanyCardOwner(const Value: integer); stdcall;
    procedure SetNextReportCode(const Value: pchar); stdcall;
    procedure SetReportFileNameAddStand(const Value: pchar); stdcall;
    procedure SetBranchNumber(const Value: integer); stdcall;
    procedure SetTimeTableFileExt(const Value: pchar); stdcall;
    procedure SetStandAloneWorkMode(const Value: boolean); stdcall;
    procedure SetAddDataSaveDate(const Value: pchar); stdcall;
    procedure SetAddDataSaveTime(const Value: pchar); stdcall;
    procedure SetDDFileName(const Value: pchar); stdcall;
    procedure SetPZAddedCardCount(const Value: integer); stdcall;
    procedure SetPZDeletedCardCount(const Value: integer); stdcall;
    procedure SetPPAddedCardCount(const Value: integer); stdcall;
    procedure SetAddDataProgram(const Value: pchar); stdcall;
    procedure SetReadCardDate(const Value: pchar); stdcall;
    procedure SetReadCardTime(const Value: pchar); stdcall;
    procedure SetReadCardProgram(const Value: pchar); stdcall;
    function GetSalePrefSet: IEmar_DriverSalePrefSet; stdcall;
  protected
    procedure _Clear; override;
  public
    constructor Create(aOwner: TEmar_BaseFile; aId: integer); override;
    destructor Destroy; override;

    { Methods }
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure ForceUpdateFlash; stdcall;
    { Properties }
    /// <summary>
    /// SalePrefSet zawiera:
    /// <para>  - OIK.Status1, OIK.Status2, OIK.Status3, OIK.Status4</para>
    /// <para>  - OIK.O205_1, OIK.O205_2, OIK.O205_3, OIK.O205_4</para>
    /// <para>  - OIK maksymalna liczba pasażerów na bilecie zbiorowym (MaxPassengersOnGroupTicket)
    /// </summary>
    property SalePrefSet: IEmar_DriverSalePrefSet
      read   GetSalePrefSet;
    /// <summary>
    /// NumerFabrycznyKarty = longint
    /// na razie z Teksty.Tekst dla LP=8
    /// </summary>
    property CardSerialNumber: cardinal
      read   GetCardSerialNumber
      write  SetCardSerialNumber;
    /// <summary>
    /// DataProdukcji = record(Rok:integer; Mies:integer; Dzien:integer)
    /// na razie z Teksty.Tekst dla LP=9
    /// </summary>
    property ManufactureDate: pchar
      read   GetManufactureDate
      write  SetManufactureDate;
    /// <summary>
    /// TypKarty = array[0..2] of char („F8”)
    /// </summary>
    property CardType: pchar
      read   GetCardType
      write  SetCardType;
    /// <summary>
    /// KodPojemnościKarty = integer (15=2 MB)
    /// </summary>
    property CardCapacityCode: integer
      read   GetCardCapacityCode
      write  SetCardCapacityCode;
    /// <summary>
    /// DataRejestracjiKarty = record(Rok:integer; Mies:integer; Dzien:integer)
    /// na razie z Teksty.Tekst dla LP=10
    /// </summary>
    property CardRegisterDate: pchar
      read   GetCardRegisterDate
      write  SetCardRegisterDate;
    /// <summary>
    /// NIP = array[0..13] of char (999-99-99-999 lub 999-999-99-99 (separatorem może być znak spacji ‘ ‘) lub 9999999999) zakończony kodem #0. UWAGA: jeśli NIP ma mniej znaków niż 13, to po znaku #0 bufor jest wypełniony do końca kodami #255 ($ff).
    /// Firmy.NIP – firmy, dla której przygotowywany jest zbiór do bileterki
    /// </summary>
    property NIP: pchar
      read   GetNIP
      write  SetNIP;
    /// <summary>
    /// Nagłówek1  = array[0..32] of char   **) *)
    /// Teksty.Tekst (LP=1)
    /// </summary>
    property Header1: pchar
      read   GetHeader1
      write  SetHeader1;
    /// <summary>
    /// LP=2
    /// </summary>
    property Header2: pchar
      read   GetHeader2
      write  SetHeader2;
    /// <summary>
    /// LP=3
    /// </summary>
    property Header3: pchar
      read   GetHeader3
      write  SetHeader3;
    /// <summary>
    /// LP=4
    /// </summary>
    property Header4: pchar
      read   GetHeader4
      write  SetHeader4;
    /// <summary>
    /// Stopka1 = array[0..32] of char      **) *)
    /// Teksty.Tekst (LP=5)
    /// </summary>
    property Footer1: pchar
      read   GetFooter1
      write  SetFooter1;
    /// <summary>
    /// LP=6
    /// </summary>
    property Footer2: pchar
      read   GetFooter2
      write  SetFooter2;
    /// <summary>
    /// LP=7
    /// </summary>
    property Footer3: pchar
      read   GetFooter3
      write  SetFooter3;
    /// <summary>
    /// NumerKierowcy = longint
    /// Pracownicy.NR_SLUZB
    /// </summary>
    property DriverNumber: cardinal
      read   GetDriverNumber
      write  SetDriverNumber;
    /// <summary>
    /// Imie = array[0..20] of char
    /// Uwaga: uzupełnione spacjami z prawej do pełnej długości
    /// Pracownicy.IMIE
    /// </summary>
    property DriverFirstName: pchar
      read   GetDriverFirstName
      write  SetDriverFirstName;
    /// <summary>
    /// Nazwisko = array[0..30] of char
    /// Uwaga: uzupełnione spacjami z prawej do pełnej długości
    /// Pracownicy.NAZWISKO
    /// </summary>
    property DriverLastName: pchar
      read   GetDriverLastName
      write  SetDriverLastName;
    /// <summary>
    /// PIN = integer    Numer identyfikacyjny jest zawsze czterocyfrowy.
    /// chwilowo wpisywany przy wyborze pracownika
    /// </summary>
    property PIN: integer
      read   GetPIN
      write  SetPIN;
    /// <summary>
    /// StatusPracownika = integer : określa uprawnienia dostępu do funkcji menu bileterki
    /// Do karty mogą być zapisane dane pracowników o statusie:
    /// 1-administrator, 2-kierownik  - poziom uprawnień najwyższy,
    /// 4-dyspozytor, 6-kasjer rozliczający – poziom uprawnień średni,
    /// 7-kierowca, 8-kasjer biletowy – poziom uprawnień podstawowy
    /// </summary>
    property EmployeeStatus: integer
      read   GetEmployeeStatus
      write  SetEmployeeStatus;
    /// <summary>
    /// Data przypisania karty pracownikowi = record(Rok:integer; Mies:integer; Dzien:integer)
    /// </summary>
    property CardAssignDate: pchar
      read   GetCardAssignDate
      write  SetCardAssignDate;
    /// <summary>
    /// Nazwa zbioru z rozkładem jazdy zapisanego do karty (A80_rrrrmmdd_wwnn) = array[0..17] of char
    /// UWAGA: zapisana również w rekordzie OIK zbioru A80_
    /// </summary>
    property TimeTableFileName: pchar
      read   GetTimeTableFileName
      write  SetTimeTableFileName;
    property TimeTableSaveFileDate: pchar
      read   GetTimeTableSaveFileDate
      write  SetTimeTableSaveFileDate;
    /// <summary>
    /// Godzina zapisu do karty rozkładu jazdy
    /// </summary>
    property TimeTableSaveFileTime: pchar
      read   GetTimeTableSaveFileTime
      write  SetTimeTableSaveFileTime;
    /// <summary>
    /// Wskaźnik gotowości karty do pracy:
    /// $55 – bileterka może stosować kartę;
    /// inna wartość – praca z komputerem
    /// 80 ($50) – rozpoczęta rejestracja rozliczenia
    /// 81 ($51) – rozpoczęte kasowanie raportu
    /// 82 ($52) – rozpoczęte programowanie
    /// </summary>
    property ReadyCode: integer
      read   GetReadyCode
      write  SetReadyCode;
    /// <summary>
    /// Nazwa zbioru RZ i numer raportu zadaniowego
    /// RZrrrrmmssnnnnn, gdzie rrrr- rok, mm-miesiąc, ss-numer stanowiska, nnnnn-numer raportu zadaniowego, RZ=dzień rejestracji
    /// UWAGA: zapisywana jest do pliku przez funkcję rejestracji rozliczenia
    /// </summary>
    property TaskReportFileName: pchar
      read   GetTaskReportFileName
      write  SetTaskReportFileName;
    /// <summary>
    /// Data zapisu statusu do karty
    /// </summary>
    property StatesSaveDate: pchar
      read   GetStatesSaveDate
      write  SetStatesSaveDate;
    /// <summary>
    /// Godzina zapisu statusu do karty
    /// </summary>
    property StatesSaveTime: pchar
      read   GetStatesSaveTime
      write  SetStatesSaveTime;
    /// <summary>
    /// Numer firmy – właściciela karty
    /// </summary>
    property CompanyCardOwner: integer
      read   GetCompanyCardOwner
      write  SetCompanyCardOwner;
    /// <summary>
    /// Szyfr następnego raportu zapisywany przy rejestracji rozliczenia
    /// </summary>
    property NextReportCode: pchar
      read   GetNextReportCode
      write  SetNextReportCode;
    /// <summary>
    /// nazwa zbioru z raportem odczytanym na stanowisku do automatycznej rejestracji (rozliczarka)
    /// </summary>
    property ReportFileNameAddStand: pchar
      read   GetReportFileNameAddStand
      write  SetReportFileNameAddStand;
    /// <summary>
    /// Numer oddziału, do którego przypisana jest karta
    /// </summary>
    property BranchNumber: integer
      read   GetBranchNumber
      write  SetBranchNumber;
    /// <summary>
    /// Rozszerzenie nazwy zbioru z rozkładem jazdy zapisanego do karty (A80)
    /// </summary>
    property TimeTableFileExt: pchar
      read   GetTimeTableFileExt
      write  SetTimeTableFileExt;
    /// <summary>
    /// true - $FF – bileterka pracuje autonomicznie (domyślne)
    /// false - $55-bileterka jest podłączana do komputera pokładowego
    /// </summary>
    property StandAloneWorkMode: boolean
      read   GetStandAloneWorkMode
      write  SetStandAloneWorkMode;
    /// <summary>
    /// Data zapisu do karty danych dodatkowych
    /// </summary>
    property AddDataSaveDate: pchar
      read   GetAddDataSaveDate
      write  SetAddDataSaveDate;
    /// <summary>
    /// Godzina zapisu do karty danych dodatkowych
    /// </summary>
    property AddDataSaveTime: pchar
      read   GetAddDataSaveTime
      write  SetAddDataSaveTime;
    /// <summary>
    /// nazwa zbioru z danymi dodatkowymi lub $FF
    /// </summary>
    property DDFileName: pchar
      read   GetDDFileName
      write  SetDDFileName;
    /// <summary>
    /// liczba EM-kart dodanych do listy kart zastrzeżonych na podstawie danych z plików PZddddd.DAT (tylko Rozliczarka/Rozliczarka-wpłatomat)
    /// </summary>
    property PZAddedCardCount: integer
      read   GetPZAddedCardCount
      write  SetPZAddedCardCount;
    /// <summary>
    /// liczba EM-kart usuniętych z listy kart zastrzeżonych na podstawie danych z plików PZddddd.DAT (tylko Rozliczarka/Rozliczarka-wpłatomat)
    /// </summary>
    property PZDeletedCardCount: integer
      read   GetPZDeletedCardCount
      write  SetPZDeletedCardCount;
    /// <summary>
    /// liczba EM-kart dodanych do wykazu kart z kodami przedłużenia na podstawie danych z plików PPddddd.DAT (tylko Rozliczarka/Rozliczarka-wpłatomat)
    /// </summary>
    property PPAddedCardCount: integer
      read   GetPPAddedCardCount
      write  SetPPAddedCardCount;
    /// <summary>
    /// Array[0..10] of char – symbol i wersja programu, który zapisał dane do karty pamięci – wpisywany przed zapisem OIK do karty pamięci:
    ///   KK 1.nnx
    ///   PB 1.nnx
    ///   RWpl 1.nnx
    ///   Rozl 1.nnx
    ///   Inf 2.nn.m
    /// </summary>
    property AddDataProgram: pchar
      read   GetAddDataProgram
      write  SetAddDataProgram;
    /// <summary>
    /// Data odczytu zawartości karty
    /// </summary>
    property ReadCardDate: pchar
      read   GetReadCardDate
      write  SetReadCardDate;
    /// <summary>
    /// Godzina odczytu zawartości karty
    /// </summary>
    property ReadCardTime: pchar
      read   GetReadCardTime
      write  SetReadCardTime;
    /// <summary>
    /// symbol i wersja programu, który odczytał dane z karty pamięci – wpisywany przed zapisem OIK do pliku
    /// </summary>
    property ReadCardProgram: pchar
      read   GetReadCardProgram
      write  SetReadCardProgram;
  end;

{$ENDREGION}
{$REGION ' 07 - TEmar105_Consts '}

  TEmar105_Consts = class(TEmar_Consts, IEmar105_Consts)
  private
    fCalendarBegin:                 string;
    fCalendarEnd:                   string;
    fCalendarDayCount:              integer;
    fPTU1ValidFrom:                 string;
    fRatePTU1_A:                    integer;
    fRatePTU1_B:                    integer;
    fRatePTU1_C:                    integer;
    fRatePTU1_D:                    integer;
    fRatePTU1_E:                    integer;
    fRatePTU1_F:                    integer;
    fRatePTU1_G:                    integer;
    fPTU2ValidFrom:                 string;
    fRatePTU2_A:                    integer;
    fRatePTU2_B:                    integer;
    fRatePTU2_C:                    integer;
    fRatePTU2_D:                    integer;
    fRatePTU2_E:                    integer;
    fRatePTU2_F:                    integer;
    fRatePTU2_G:                    integer;
    fFirstWeekDay:                  integer;
    fMaxTicketPrice5:               cardinal;
    fMaxTicketPrice10:              cardinal;
    fRatePTU_N:                     integer;
    fTariffCurrencyCode:            string;
    fTariffCurrencyDateChange:      string;
    fTariffAfterChangeCurrencyCode: string;
    fBusStopCount:                  integer;
    fBusStopListDate:               string;
    fDayFileNumber:                 integer;
    fCurrencyValidFrom:             string;
    fCurrencyCode:                  string;
    fTransitionStartPeriod:         string;
    fTransitionEndPeriod:           string;
    fExchangeRatePLN:               longint;
    fNewCurrencyCode:               string;
    fExchangeRate:                  longint;
    fCurrencyDateChange:            string;
    fTimeChangeKind1:               integer;
    fTimeChangeFrom1:               string;
    fTimeChangeKind2:               integer;
    fTimeChangeFrom2:               string;
    fTimeChangeKind3:               integer;
    fTimeChangeFrom3:               string;
    fTimeChangeKind4:               integer;
    fTimeChangeFrom4:               string;
    fAddPageCount:                  integer;
    fSHA_Key:                       string;
    fIsMakeFileParams:              boolean;
    fBranchNumber:                  integer;
    fSaveAllRides:                  boolean;
    fSaveRidesWithoutBranch:        boolean;
    fBranchName:                    string;
    fOwnRidesOnly:                  boolean;
    fSaveAllLines:                  boolean;
    fSaveRideRoute:                 boolean;
    fConditionalBusStops:           boolean;
    fTariffDistance:                boolean;
    fCalcTariffDistance:            boolean;
    fRideOutsideBusStopNames:       integer;
    fSaveToTicketRegisterFrom:      string;
    fCalendarChangeCount:           integer;
    fCalendarDate1:                 string;
    fCalendarFormula1:              string;
    fCalendarDate2:                 string;
    fCalendarFormula2:              string;
    fCalendarDate3:                 string;
    fCalendarFormula3:              string;
    fCalendarDate4:                 string;
    fCalendarFormula4:              string;
    fCalendarDate5:                 string;
    fCalendarFormula5:              string;
    fCalendarDate6:                 string;
    fCalendarFormula6:              string;
    fCalendarDate7:                 string;
    fCalendarFormula7:              string;
    fCalendarDate8:                 string;
    fCalendarFormula8:              string;
    fCalendarDate9:                 string;
    fCalendarFormula9:              string;
    fProgramMaker:                  string;
    fProgramMakerVersion:           string;
    { Property methods }
    function GetCalendarBegin: pchar; stdcall;
    function GetCalendarEnd: pchar; stdcall;
    function GetCalendarDayCount: integer; stdcall;
    function GetPTU1ValidFrom: pchar; stdcall;
    function GetRatePTU1_A: integer; stdcall;
    function GetRatePTU1_B: integer; stdcall;
    function GetRatePTU1_C: integer; stdcall;
    function GetRatePTU1_D: integer; stdcall;
    function GetRatePTU1_E: integer; stdcall;
    function GetRatePTU1_F: integer; stdcall;
    function GetRatePTU1_G: integer; stdcall;
    function GetPTU2ValidFrom: pchar; stdcall;
    function GetRatePTU2_A: integer; stdcall;
    function GetRatePTU2_B: integer; stdcall;
    function GetRatePTU2_C: integer; stdcall;
    function GetRatePTU2_D: integer; stdcall;
    function GetRatePTU2_E: integer; stdcall;
    function GetRatePTU2_F: integer; stdcall;
    function GetRatePTU2_G: integer; stdcall;
    function GetFirstWeekDay: integer; stdcall;
    function GetMaxTicketPrice5: cardinal; stdcall;
    function GetMaxTicketPrice10: cardinal; stdcall;
    function GetRatePTU_N: integer; stdcall;
    function GetTariffCurrencyCode: pchar; stdcall;
    function GetTariffCurrencyDateChange: pchar; stdcall;
    function GetTariffAfterChangeCurrencyCode: pchar; stdcall;
    function GetBusStopCount: integer; stdcall;
    function GetBusStopListDate: pchar; stdcall;
    function GetDayFileNumber: integer; stdcall;
    function GetCurrencyValidFrom: pchar; stdcall;
    function GetCurrencyCode: pchar; stdcall;
    function GetTransitionStartPeriod: pchar; stdcall;
    function GetTransitionEndPeriod: pchar; stdcall;
    function GetExchangeRatePLN: cardinal; stdcall;
    function GetNewCurrencyCode: pchar; stdcall;
    function GetExchangeRate: cardinal; stdcall;
    function GetCurrencyDateChange: pchar; stdcall;
    function GetTimeChangeKind1: integer; stdcall;
    function GetTimeChangeFrom1: pchar; stdcall;
    function GetTimeChangeKind2: integer; stdcall;
    function GetTimeChangeFrom2: pchar; stdcall;
    function GetTimeChangeKind3: integer; stdcall;
    function GetTimeChangeFrom3: pchar; stdcall;
    function GetTimeChangeKind4: integer; stdcall;
    function GetTimeChangeFrom4: pchar; stdcall;
    function GetAddPageCount: integer; stdcall;
    function GetSHA_Key: pchar; stdcall;
    function GetIsMakeFileParams: boolean; stdcall;
    function GetBranchNumber: integer; stdcall;
    function GetSaveAllRides: boolean; stdcall;
    function GetSaveRidesWithoutBranch: boolean; stdcall;
    function GetBranchName: pchar; stdcall;
    function GetOwnRidesOnly: boolean; stdcall;
    function GetSaveAllLines: boolean; stdcall;
    function GetSaveRideRoute: boolean; stdcall;
    function GetConditionalBusStops: boolean; stdcall;
    function GetTariffDistance: boolean; stdcall;
    function GetCalcTariffDistance: boolean; stdcall;
    function GetRideOutsideBusStopNames: integer; stdcall;
    function GetSaveToTicketRegisterFrom: pchar; stdcall;
    function GetCalendarChangeCount: integer; stdcall;
    function GetCalendarDate1: pchar; stdcall;
    function GetCalendarFormula1: pchar; stdcall;
    function GetCalendarDate2: pchar; stdcall;
    function GetCalendarFormula2: pchar; stdcall;
    function GetCalendarDate3: pchar; stdcall;
    function GetCalendarFormula3: pchar; stdcall;
    function GetCalendarDate4: pchar; stdcall;
    function GetCalendarFormula4: pchar; stdcall;
    function GetCalendarDate5: pchar; stdcall;
    function GetCalendarFormula5: pchar; stdcall;
    function GetCalendarDate6: pchar; stdcall;
    function GetCalendarFormula6: pchar; stdcall;
    function GetCalendarDate7: pchar; stdcall;
    function GetCalendarFormula7: pchar; stdcall;
    function GetCalendarDate8: pchar; stdcall;
    function GetCalendarFormula8: pchar; stdcall;
    function GetCalendarDate9: pchar; stdcall;
    function GetCalendarFormula9: pchar; stdcall;
    function GetProgramMaker: pchar; stdcall;
    function GetProgramMakerVersion: pchar; stdcall;
    function GetFileVersion: integer; stdcall;
    procedure SetCalendarBegin(const Value: pchar); stdcall;
    procedure SetCalendarEnd(const Value: pchar); stdcall;
    procedure SetCalendarDayCount(const Value: integer); stdcall;
    procedure SetPTU1ValidFrom(const Value: pchar); stdcall;
    procedure SetRatePTU1_A(const Value: integer); stdcall;
    procedure SetRatePTU1_B(const Value: integer); stdcall;
    procedure SetRatePTU1_C(const Value: integer); stdcall;
    procedure SetRatePTU1_D(const Value: integer); stdcall;
    procedure SetRatePTU1_E(const Value: integer); stdcall;
    procedure SetRatePTU1_F(const Value: integer); stdcall;
    procedure SetRatePTU1_G(const Value: integer); stdcall;
    procedure SetPTU2ValidFrom(const Value: pchar); stdcall;
    procedure SetRatePTU2_A(const Value: integer); stdcall;
    procedure SetRatePTU2_B(const Value: integer); stdcall;
    procedure SetRatePTU2_C(const Value: integer); stdcall;
    procedure SetRatePTU2_D(const Value: integer); stdcall;
    procedure SetRatePTU2_E(const Value: integer); stdcall;
    procedure SetRatePTU2_F(const Value: integer); stdcall;
    procedure SetRatePTU2_G(const Value: integer); stdcall;
    procedure SetFirstWeekDay(const Value: integer); stdcall;
    procedure SetMaxTicketPrice5(const Value: cardinal); stdcall;
    procedure SetMaxTicketPrice10(const Value: cardinal); stdcall;
    procedure SetRatePTU_N(const Value: integer); stdcall;
    procedure SetTariffCurrencyCode(const Value: pchar); stdcall;
    procedure SetTariffCurrencyDateChange(const Value: pchar); stdcall;
    procedure SetTariffAfterChangeCurrencyCode(const Value: pchar); stdcall;
    procedure SetBusStopCount(const Value: integer); stdcall;
    procedure SetBusStopListDate(const Value: pchar); stdcall;
    procedure SetDayFileNumber(const Value: integer); stdcall;
    procedure SetCurrencyValidFrom(const Value: pchar); stdcall;
    procedure SetCurrencyCode(const Value: pchar); stdcall;
    procedure SetTransitionStartPeriod(const Value: pchar); stdcall;
    procedure SetTransitionEndPeriod(const Value: pchar); stdcall;
    procedure SetExchangeRatePLN(const Value: cardinal); stdcall;
    procedure SetNewCurrencyCode(const Value: pchar); stdcall;
    procedure SetExchangeRate(const Value: cardinal); stdcall;
    procedure SetCurrencyDateChange(const Value: pchar); stdcall;
    procedure SetTimeChangeKind1(const Value: integer); stdcall;
    procedure SetTimeChangeFrom1(const Value: pchar); stdcall;
    procedure SetTimeChangeKind2(const Value: integer); stdcall;
    procedure SetTimeChangeFrom2(const Value: pchar); stdcall;
    procedure SetTimeChangeKind3(const Value: integer); stdcall;
    procedure SetTimeChangeFrom3(const Value: pchar); stdcall;
    procedure SetTimeChangeKind4(const Value: integer); stdcall;
    procedure SetTimeChangeFrom4(const Value: pchar); stdcall;
    procedure SetAddPageCount(const Value: integer); stdcall;
    procedure SetSHA_Key(const Value: pchar); stdcall;
    procedure SetIsMakeFileParams(const Value: boolean); stdcall;
    procedure SetBranchNumber(const Value: integer); stdcall;
    procedure SetSaveAllRides(const Value: boolean); stdcall;
    procedure SetSaveRidesWithoutBranch(const Value: boolean); stdcall;
    procedure SetBranchName(const Value: pchar); stdcall;
    procedure SetOwnRidesOnly(const Value: boolean); stdcall;
    procedure SetSaveAllLines(const Value: boolean); stdcall;
    procedure SetSaveRideRoute(const Value: boolean); stdcall;
    procedure SetConditionalBusStops(const Value: boolean); stdcall;
    procedure SetTariffDistance(const Value: boolean); stdcall;
    procedure SetCalcTariffDistance(const Value: boolean); stdcall;
    procedure SetRideOutsideBusStopNames(const Value: integer); stdcall;
    procedure SetSaveToTicketRegisterFrom(const Value: pchar); stdcall;
    procedure SetCalendarChangeCount(const Value: integer); stdcall;
    procedure SetCalendarDate1(const Value: pchar); stdcall;
    procedure SetCalendarFormula1(const Value: pchar); stdcall;
    procedure SetCalendarDate2(const Value: pchar); stdcall;
    procedure SetCalendarFormula2(const Value: pchar); stdcall;
    procedure SetCalendarDate3(const Value: pchar); stdcall;
    procedure SetCalendarFormula3(const Value: pchar); stdcall;
    procedure SetCalendarDate4(const Value: pchar); stdcall;
    procedure SetCalendarFormula4(const Value: pchar); stdcall;
    procedure SetCalendarDate5(const Value: pchar); stdcall;
    procedure SetCalendarFormula5(const Value: pchar); stdcall;
    procedure SetCalendarDate6(const Value: pchar); stdcall;
    procedure SetCalendarFormula6(const Value: pchar); stdcall;
    procedure SetCalendarDate7(const Value: pchar); stdcall;
    procedure SetCalendarFormula7(const Value: pchar); stdcall;
    procedure SetCalendarDate8(const Value: pchar); stdcall;
    procedure SetCalendarFormula8(const Value: pchar); stdcall;
    procedure SetCalendarDate9(const Value: pchar); stdcall;
    procedure SetCalendarFormula9(const Value: pchar); stdcall;
    procedure SetProgramMaker(const Value: pchar); stdcall;
    procedure SetProgramMakerVersion(const Value: pchar); stdcall;
  protected
    procedure _Clear; override;
  public
    { Methods }
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    { Properties }
    /// <summary>
    /// PoczatekKalendarza = record(Rok:word; Mies:byte; Dzien:byte)
    /// </summary>
    property CalendarBegin: pchar
      read   GetCalendarBegin
      write  SetCalendarBegin;
    /// <summary>
    /// Koniec kalendarza = record(Rok:integer; Mies:integer; Dzien:integer)
    /// </summary>
    property CalendarEnd: pchar
      read   GetCalendarEnd
      write  SetCalendarEnd;
    /// <summary>
    /// Stałe PoczatekKalendarza oraz Koniec kalendarza wyznaczają okres ważności danych - bileterka
    /// umożliwia sprzedaż tylko w okresie wyznaczonym przez te daty z uwzględnieniem dat ważności kursów, taryf itp. Po dacie KoniecKalendarza
    /// wszystkie dane uzależnione czasowo uznawane są za ważne zawsze (codziennie).
    /// W przypadku przypisania do kursu kilku taryf wybierana jest pierwsza z nich.
    /// </summary>
    property CalendarDayCount: integer
      read   GetCalendarDayCount
      write  SetCalendarDayCount;
    /// <summary>
    /// DataWażnościStawekPTU1 = record(Rok:integer; Mies:integer; Dzien:integer)
    /// </summary>
    property PTU1ValidFrom: pchar
      read   GetPTU1ValidFrom
      write  SetPTU1ValidFrom;
    /// <summary>
    /// Zapisywana jest wartość stawki x 100
    /// Stawki nieaktywne: wpisana wartość = -1 ($FFFF);
    /// stawka zwolniona = 20000 (200%)
    /// </summary>
    property RatePTU1_A: integer
      read   GetRatePTU1_A
      write  SetRatePTU1_A;
    property RatePTU1_B: integer
      read   GetRatePTU1_B
      write  SetRatePTU1_B;
    property RatePTU1_C: integer
      read   GetRatePTU1_C
      write  SetRatePTU1_C;
    property RatePTU1_D: integer
      read   GetRatePTU1_D
      write  SetRatePTU1_D;
    property RatePTU1_E: integer
      read   GetRatePTU1_E
      write  SetRatePTU1_E;
    property RatePTU1_F: integer
      read   GetRatePTU1_F
      write  SetRatePTU1_F;
    property RatePTU1_G: integer
      read   GetRatePTU1_G
      write  SetRatePTU1_G;
    /// <summary>
    /// DataWażnościStawekPTU2 = record(Rok:integer; Mies:integer; Dzien:integer)
    /// Jeśli nie ma zmiany stawek PTU, to DataWażnościStawekPTU2:=(0,0,0)
    /// </summary>
    property PTU2ValidFrom: pchar
      read   GetPTU2ValidFrom
      write  SetPTU2ValidFrom;
    property RatePTU2_A: integer
      read   GetRatePTU2_A
      write  SetRatePTU2_A;
    property RatePTU2_B: integer
      read   GetRatePTU2_B
      write  SetRatePTU2_B;
    property RatePTU2_C: integer
      read   GetRatePTU2_C
      write  SetRatePTU2_C;
    property RatePTU2_D: integer
      read   GetRatePTU2_D
      write  SetRatePTU2_D;
    property RatePTU2_E: integer
      read   GetRatePTU2_E
      write  SetRatePTU2_E;
    property RatePTU2_F: integer
      read   GetRatePTU2_F
      write  SetRatePTU2_F;
    property RatePTU2_G: integer
      read   GetRatePTU2_G
      write  SetRatePTU2_G;
    /// <summary>
    /// Dzień tygodnia początku kalendarza: 0-poniedziałek, .. 6-niedziela, $FF-nie jest wpisany
    /// </summary>
    property FirstWeekDay: integer
      read   GetFirstWeekDay
      write  SetFirstWeekDay;
    /// <summary>
    /// max cena biletu ulgowego (grosze), dla której w przypadku, gdy Ulga.ZaokraglenieCeny=5 należy wykonać zaokrąglenie jest do 5 groszy
    /// </summary>
    property MaxTicketPrice5: cardinal
      read   GetMaxTicketPrice5
      write  SetMaxTicketPrice5;
    /// <summary>
    /// max cena biletu ulgowego (grosze), dla której w przypadku, gdy Ulga.ZaokraglenieCeny=5 należy wykonać zaokrąglenie jest do10 groszy ? powyżej tej granicy cena biletu zaokrąglana jest do 1 zł
    /// </summary>
    property MaxTicketPrice10: cardinal
      read   GetMaxTicketPrice10
      write  SetMaxTicketPrice10;
    /// <summary>
    /// StawkaN: integer = 30000 wartość wpisywana przy obliczeniach kodu kontrolnego biletu dla stawki ‘N’ (wartość nie podlega PTU)
    /// </summary>
    property RatePTU_N: integer
      read   GetRatePTU_N
      write  SetRatePTU_N;
    /// <summary>
    /// Oznaczenie waluty cennika: array[0..3] of char (PLN,EUR)
    /// </summary>
    property TariffCurrencyCode: pchar
      read   GetTariffCurrencyCode
      write  SetTariffCurrencyCode;
    /// <summary>
    /// Data zmiany waluty cennika = record(Rok:integer; Mies:integer; Dzien:integer) (kody FF jeśli waluta nie zmienia się)
    /// </summary>
    property TariffCurrencyDateChange: pchar
      read   GetTariffCurrencyDateChange
      write  SetTariffCurrencyDateChange;
    /// <summary>
    /// Oznaczenie waluty cennika po zmianie: array[0..3] of char (PLN,EUR) (FF-waluta cennika nie zmienia się)
    /// Tabela przeliczników walut po zmianie waluty cennika: 39
    /// UWAGA: w przypadku zmiany waluty cennika do tablicy 39 (kursy walut po zmianie waluty cennika)
    /// zapisywany jest dodatkowy komplet przeliczników na nową walutę, w której wyrażone są ceny w cenniku.
    /// Przygotowanie nowego zbioru po dacie zmiany waluty cennika powoduje zapis tylko jednej tabeli przeliczników walut.
    /// </summary>
    property TariffAfterChangeCurrencyCode: pchar
      read   GetTariffAfterChangeCurrencyCode
      write  SetTariffAfterChangeCurrencyCode;
    /// <summary>
    /// Liczba przystanków w tablicy Przystanki;
    /// jeżeli liczba przystanków = $FFFF,
    /// to informacja o liczbie przystanków nie została zapisana
    /// </summary>
    property BusStopCount: integer
      read   GetBusStopCount
      write  SetBusStopCount;
    /// <summary>
    /// Data pierwszego zapisu tablicy przystanków = record(Rok:integer; Mies:integer; Dzien:integer) (kody FF jeśli informacja o tablicy przystanków nie była zapisana)
    /// </summary>
    property BusStopListDate: pchar
      read   GetBusStopListDate
      write  SetBusStopListDate;
    /// <summary>
    /// Kolejny numer pliku przygotowany tego dnia, w którym po raz pierwszy została zapisana tablica przystanków o danej zawartości
    /// (kod FF jeśli informacja o tablicy przystanków nie była zapisana)
    /// UWAGA: informacja o tablicy przystanków zapisywana jest w celu sprawdzania, czy bileterka powinna przy
    /// rozpoczynaniu pracy z daną kartą pamięci przesyłać tablicę przystanków do kasowników (czytników biletów).
    /// Jeśli w kasownikach informacja o zawartości tablicy przystanków jest zgodna z zapisem w obszarze 76..82, to transmisja nie jest wykonywana.
    /// </summary>
    property DayFileNumber: integer
      read   GetDayFileNumber
      write  SetDayFileNumber;
    /// <summary>
    /// Data początku ważności waluty ewidencyjnej
    /// </summary>
    property CurrencyValidFrom: pchar
      read   GetCurrencyValidFrom
      write  SetCurrencyValidFrom;
    /// <summary>
    /// Oznaczenie waluty ewidencyjnej: array[0..3] of char (PLN,EUR) <- pole musi być wpisane zawsze
    /// </summary>
    property CurrencyCode: pchar
      read   GetCurrencyCode
      write  SetCurrencyCode;
    /// <summary>
    /// Data początku drukowania przelicznika PLN -> EUR
    /// </summary>
    property TransitionStartPeriod: pchar
      read   GetTransitionStartPeriod
      write  SetTransitionStartPeriod;
    /// <summary>
    /// Data końca drukowania przelicznika PLN -> EUR
    /// </summary>
    property TransitionEndPeriod: pchar
      read   GetTransitionEndPeriod
      write  SetTransitionEndPeriod;
    /// <summary>
    /// mnożnik do przeliczenia PLN na EUR (0-jeśli brak przelicznika).
    /// Zapisany z dokładnością do 6 miejsc po przecinku (x 1000000)
    /// </summary>
    property ExchangeRatePLN: cardinal
      read   GetExchangeRatePLN
      write  SetExchangeRatePLN;
    /// <summary>
    /// Oznaczenie waluty nowej (EUR)
    /// </summary>
    property NewCurrencyCode: pchar
      read   GetNewCurrencyCode
      write  SetNewCurrencyCode;
    /// <summary>
    /// mnożnik do przeliczenia EUR na PLN(0-jeśli brak przelicznika)
    /// Zapisany z dokładnością do 6 miejsc po przecinku (x 1000000)
    /// </summary>
    property ExchangeRate: cardinal
      read   GetExchangeRate
      write  SetExchangeRate;
    /// <summary>
    /// Data i godzina zmiany waluty ewidencyjnej
    /// </summary>
    property CurrencyDateChange: pchar
      read   GetCurrencyDateChange
      write  SetCurrencyDateChange;
    /// <summary>
    /// Rodzaj zmiany (integer): ‘L’-wprowadzenie czasu letnego, ‘Z’-odwołanie czasu letniego; $00-brak danych
    /// </summary>
    property TimeChangeKind1: integer
      read   GetTimeChangeKind1
      write  SetTimeChangeKind1;
    /// <summary>
    /// Data i godzina zmiany czasu. Pusto - brak danych
    /// </summary>
    property TimeChangeFrom1: pchar
      read   GetTimeChangeFrom1
      write  SetTimeChangeFrom1;
    property TimeChangeKind2: integer
      read   GetTimeChangeKind2
      write  SetTimeChangeKind2;
    property TimeChangeFrom2: pchar
      read   GetTimeChangeFrom2
      write  SetTimeChangeFrom2;
    property TimeChangeKind3: integer
      read   GetTimeChangeKind3
      write  SetTimeChangeKind3;
    property TimeChangeFrom3: pchar
      read   GetTimeChangeFrom3
      write  SetTimeChangeFrom3;
    property TimeChangeKind4: integer
      read   GetTimeChangeKind4
      write  SetTimeChangeKind4;
    property TimeChangeFrom4: pchar
      read   GetTimeChangeFrom4
      write  SetTimeChangeFrom4;
    /// <summary>
    /// ($FFFF)-brak dodanych stron;
    /// <$FFFF – liczba dodanych stron z wykazem plików tekstowych
    /// </summary>
    property AddPageCount: integer
      read   GetAddPageCount
      write  SetAddPageCount;
    /// <summary>
    /// Skrót SHA zawartości pliku (20 bajtów)
    /// </summary>
    property SHA_Key: pchar
      read   GetSHA_Key
      write  SetSHA_Key;
    /// <summary>
    /// Parametry przygotowania zbioru = integer: $AA-zapisane $FF-brak
    /// </summary>
    property IsMakeFileParams: boolean
      read   GetIsMakeFileParams
      write  SetIsMakeFileParams;
    /// <summary>
    /// Oddziały firmy = integer: 00-wszystkie, <>0-nr oddziału, dla którego przygotowany jest zbiór
    /// </summary>
    property BranchNumber: integer
      read   GetBranchNumber
      write  SetBranchNumber;
    /// <summary>
    /// true-zapis wszystkich kursów
    /// </summary>
    property SaveAllRides: boolean
      read   GetSaveAllRides
      write  SetSaveAllRides;
    /// <summary>
    /// true - zapis kursów bez oddziału
    /// </summary>
    property SaveRidesWithoutBranch: boolean
      read   GetSaveRidesWithoutBranch
      write  SetSaveRidesWithoutBranch;
    /// <summary>
    /// Nazwa oddziału
    /// </summary>
    property BranchName: pchar
      read   GetBranchName
      write  SetBranchName;
    /// <summary>
    /// Kursy obce: true-nie zapisywać, false-zapisywać
    /// </summary>
    property OwnRidesOnly: boolean
      read   GetOwnRidesOnly
      write  SetOwnRidesOnly;
    /// <summary>
    /// Zapis linie: true-wszystkie, false-wybrane
    /// </summary>
    property SaveAllLines: boolean
      read   GetSaveAllLines
      write  SetSaveAllLines;
    /// <summary>
    /// Zapis trasy: true-wg linii, false-wg kursu
    /// </summary>
    property SaveRideRoute: boolean
      read   GetSaveRideRoute
      write  SetSaveRideRoute;
    /// <summary>
    /// Przystanki warunkowe: true-zapisać, false-pomijać
    /// </summary>
    property ConditionalBusStops: boolean
      read   GetConditionalBusStops
      write  SetConditionalBusStops;
    /// <summary>
    /// Odległości taryfowe równe drogowym: true-obliczane, false-z bazy
    /// </summary>
    property TariffDistance: boolean
      read   GetTariffDistance
      write  SetTariffDistance;
    /// <summary>
    /// Odległości taryfowe równe drogowym - obliczane: true-zaokrąglane do km, false-mnożone x 10
    /// </summary>
    property CalcTariffDistance: boolean
      read   GetCalcTariffDistance
      write  SetCalcTariffDistance;
    /// <summary>
    /// Nazwy przystanków spoza kursu:
    /// $FF-nie dotyczy (zapis trasy wg kursu),
    /// $01-normalne,
    /// $00-POZA TRASĄ.
    /// </summary>
    property RideOutsideBusStopNames: integer
      read   GetRideOutsideBusStopNames
      write  SetRideOutsideBusStopNames;
    /// <summary>
    /// Zapis do bileterek od dnia
    /// </summary>
    property SaveToTicketRegisterFrom: pchar
      read   GetSaveToTicketRegisterFrom
      write  SetSaveToTicketRegisterFrom;
    /// <summary>
    /// Liczba dni wymiany kalendarza ($FF – nie ma wymiany kalendarzy)
    /// </summary>
    property CalendarChangeCount: integer
      read   GetCalendarChangeCount
      write  SetCalendarChangeCount;
    /// <summary>
    /// Data kalendarza - praktyczne nie zrozumiały i nieużywany przez użytkowników
    /// można wpisać do 9 dat, który na przyklad jakaś sobota autobus ma jechać jak w dzień roboczy
    /// Data kalendarza = tej soboty, a
    /// Wzór kalendarza = jakiś dzień roboczy
    /// 2016-09-30 - po konsultacji z EBO, tego w nowym programie nie robimy,
    /// ze względu na to, że użytkownicy w prawie tego nie używają.
    /// </summary>
    property CalendarDate1: pchar
      read   GetCalendarDate1
      write  SetCalendarDate1;
    /// <summary>
    /// Wzór kalendarza
    /// </summary>
    property CalendarFormula1: pchar
      read   GetCalendarFormula1
      write  SetCalendarFormula1;
    property CalendarDate2: pchar
      read   GetCalendarDate2
      write  SetCalendarDate2;
    property CalendarFormula2: pchar
      read   GetCalendarFormula2
      write  SetCalendarFormula2;
    property CalendarDate3: pchar
      read   GetCalendarDate3
      write  SetCalendarDate3;
    property CalendarFormula3: pchar
      read   GetCalendarFormula3
      write  SetCalendarFormula3;
    property CalendarDate4: pchar
      read   GetCalendarDate4
      write  SetCalendarDate4;
    property CalendarFormula4: pchar
      read   GetCalendarFormula4
      write  SetCalendarFormula4;
    property CalendarDate5: pchar
      read   GetCalendarDate5
      write  SetCalendarDate5;
    property CalendarFormula5: pchar
      read   GetCalendarFormula5
      write  SetCalendarFormula5;
    property CalendarDate6: pchar
      read   GetCalendarDate6
      write  SetCalendarDate6;
    property CalendarFormula6: pchar
      read   GetCalendarFormula6
      write  SetCalendarFormula6;
    property CalendarDate7: pchar
      read   GetCalendarDate7
      write  SetCalendarDate7;
    property CalendarFormula7: pchar
      read   GetCalendarFormula7
      write  SetCalendarFormula7;
    property CalendarDate8: pchar
      read   GetCalendarDate8
      write  SetCalendarDate8;
    property CalendarFormula8: pchar
      read   GetCalendarFormula8
      write  SetCalendarFormula8;
    property CalendarDate9: pchar
      read   GetCalendarDate9
      write  SetCalendarDate9;
    property CalendarFormula9: pchar
      read   GetCalendarFormula9
      write  SetCalendarFormula9;
    property ProgramMaker: pchar
      read   GetProgramMaker
      write  SetProgramMaker;
    property ProgramMakerVersion: pchar
      read   GetProgramMakerVersion
      write  SetProgramMakerVersion;
  end;

{$ENDREGION}
{$REGION ' 08 - TEmar105_Company '}

  TEmar105_Company = class(TEmar_Company)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_CompanyList = class(TEmar_CompanyList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 09 - TEmar105_BusStop '}

  TEmar105_BusStop = class(TEmar_BusStop)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_BusStopList = class(TEmar_BusStopList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 10 - TEmar105_Ride '}

  TEmar105_Ride = class(TEmar_Ride)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideList = class(TEmar_RideList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 11 - TEmar105_RideRoute '}

  TEmar105_RideRoute = class(TEmar_RideRoute)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideRouteList = class(TEmar_RideRouteList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RideRouteList; override;
  end;

{$ENDREGION}
{$REGION ' 12 - TEmar105_RideTariff '}

  TEmar105_RideTariff = class(TEmar_RideTariff)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideTariffList = class(TEmar_RideTariffList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RideTariffList; override;
  end;

{$ENDREGION}
{$REGION ' 13 - TEmar105_RideReduction '}

  TEmar105_RideReduction = class(TEmar_RideReduction)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideReductionList = class(TEmar_RideReductionList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RideReductionList; override;
  end;

{$ENDREGION}
{$REGION ' 14 - TEmar105_Calendar '}

  TEmar105_Calendar = class(TEmar_Calendar)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_CalendarList = class(TEmar_CalendarList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_CalendarList; override;
  end;

{$ENDREGION}
{$REGION ' 15 - TEmar105_RideDesignation '}

  TEmar105_RideDesignation = class(TEmar_RideDesignation)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideDesignationList = class(TEmar_RideDesignationList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 16 - TEmar105_Tariff '}

  TEmar105_Tariff = class(TEmar_Tariff)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_TariffList = class(TEmar_TariffList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 17 - TEmar105_Price '}

  TEmar105_Price = class(TEmar_Price)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_PriceList = class(TEmar_PriceList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
  // 18,19,20 - z klas podstawowych

{$REGION ' 21 - TEmar105_CurrencyExchange '}

  TEmar105_CurrencyExchange = class(TEmar_CurrencyExchange)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_CurrencyExchangeList = class(TEmar_CurrencyExchangeList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 22 - TEmar105_PaymentType '}

  TEmar105_PaymentType = class(TEmar_PaymentType)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_PaymentTypeList = class(TEmar_PaymentTypeList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 23 - TEmar105_FarePriceReduction '}

  TEmar105_FarePriceReduction = class(TEmar_FarePriceReduction)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_FarePriceReductionList = class(TEmar_FarePriceReductionList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 24 - TEmar105_Task '}

  TEmar105_Task = class(TEmar_Task)
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_TaskList = class(TEmar_TaskList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 25 - TEmar105_TaskPosition '}

  TEmar105_TaskPosition = class(TEmar_TaskPosition)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_TaskPositionList = class(TEmar_TaskPositionList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 26 - TEmar105_Line '}

  TEmar105_Line = class(TEmar_Line)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_LineList = class(TEmar_LineList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 27 - TEmar105_RideBonus '}

  TEmar105_RideBonus = class(TEmar_RideBonus)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideBonusList = class(TEmar_RideBonusList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RideBonusList; override;
  end;

{$ENDREGION}
{$REGION ' 28 - TEmar105_RideHandlingFee '}

  TEmar105_RideHandlingFee = class(TEmar_RideHandlingFee)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RideHandlingFeeList = class(TEmar_RideHandlingFeeList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RideHandlingFeeList; override;
  end;

{$ENDREGION}
{$REGION ' 29 - TEmar105_AdditionalFee '}

  TEmar105_AdditionalFee = class(TEmar_AdditionalFee)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_AdditionalFeeList = class(TEmar_AdditionalFeeList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 30 - TEmar105_LuggageTariff '}

  TEmar105_LuggageTariff = class(TEmar_LuggageTariff)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_LuggageTariffList = class(TEmar_LuggageTariffList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_LuggageTariffList; override;
  end;

{$ENDREGION}
{$REGION ' 31 - TEmar105_ReferenceRide '}

  TEmar105_ReferenceRide = class(TEmar_ReferenceRide)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ReferenceRideList = class(TEmar_ReferenceRideList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 32 - TEmar105_AcceptedTicketOwner '}

  TEmar105_AcceptedTicketOwner = class(TEmar_AcceptedTicketOwner)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_AcceptedTicketOwnerList = class(TEmar_AcceptedTicketOwnerList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 33 - TEmar105_AcceptedTradeReliefCardOwner '}

  TEmar105_AcceptedTradeReliefCardOwner = class(TEmar_AcceptedTradeReliefCardOwner)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_AcceptedTradeReliefCardOwnerList = class(TEmar_AcceptedTradeReliefCardOwnerList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 34 - TEmar105_ProprietaryMIFAREcard '}

  TEmar105_ProprietaryMIFAREcard = class(TEmar_ProprietaryMIFAREcard)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ProprietaryMIFAREcardList = class(TEmar_ProprietaryMIFAREcardList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 35 - TEmar105_RidesCityTariff '}

  TEmar105_RidesCityTariff = class(TEmar_RidesCityTariff)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_RidesCityTariffList = class(TEmar_RidesCityTariffList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_RidesCityTariffList; override;
  end;

{$ENDREGION}
{$REGION ' 36 - TEmar105_CityTariffPrice '}

  TEmar105_CityTariffPrice = class(TEmar_CityTariffPrice)
  protected
    function GetTicketValidation: integer; override; stdcall;
    function GetValidationByDay: boolean; override; stdcall;
    function GetValidationByDuration: boolean; override; stdcall;
    function GetValidationByText: boolean; override; stdcall;
    function GetValidationByTime: boolean; override; stdcall;
    procedure SetTicketValidation(const Value: integer); override; stdcall;
    procedure SetValidationByDay(const Value: boolean); override; stdcall;
    procedure SetValidationByDuration(const Value: boolean); override; stdcall;
    procedure SetValidationByText(const Value: boolean); override; stdcall;
    procedure SetValidationByTime(const Value: boolean); override; stdcall;
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_CityTariffPriceList = class(TEmar_CityTariffPriceList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 37 - TEmar105_LineRoute '}

  TEmar105_LineRoute = class(TEmar_LineRoute)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_LineRouteList = class(TEmar_LineRouteList)
  protected
    function _AddItem: IEmar_Interface; override;
    function _New: IEmar_LineRouteList; override;
  end;

{$ENDREGION}
{$REGION ' 38 - TEmar105_LettersBusStopSideNumber '}

  TEmar105_LettersBusStopSideNumber = class(TEmar_LettersBusStopSideNumber)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_LettersBusStopSideNumberList = class(TEmar_LettersBusStopSideNumberList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 39 - TEmar105_ExchangeRateAfterChangeCurrency '}

  TEmar105_ExchangeRateAfterChangeCurrency = class(TEmar_ExchangeRateAfterChangeCurrency)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ExchangeRateAfterChangeCurrencyList = class(TEmar_ExchangeRateAfterChangeCurrencyList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 40 - TEmar105_TicketNextPeriod '}

  TEmar105_TicketNextPeriod = class(TEmar_TicketNextPeriod)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_TicketNextPeriodList = class(TEmar_TicketNextPeriodList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 41 - TEmar105_Shortcut '}

  TEmar105_Shortcut = class(TEmar_Shortcut)
  public
    function FunctionName(): PChar; override;
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ShortcutList = class(TEmar_ShortcutList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 42 - TEmar105_AcceptedInspectorsCompany '}

  TEmar105_AcceptedInspectorsCompany = class(TEmar_AcceptedInspectorsCompany)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_AcceptedInspectorsCompanyList = class(TEmar_AcceptedInspectorsCompanyList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 43 - TEmar105_ZoneNumber '}

  TEmar105_ZoneNumber = class(TEmar_ZoneNumber)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ZoneNumberList = class(TEmar_ZoneNumberList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 44 - TEmar105_FarePriceReduction '}
  // jak 23 - Ulgi

{$ENDREGION}
{$REGION ' 45 - TEmar105_ChargingTariff '}

  TEmar105_ChargingTariff = class(TEmar_ChargingTariff)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ChargingTariffList = class(TEmar_ChargingTariffList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 46 - TEmar105_ChargingTariffPrice '}

  TEmar105_ChargingTariffPrice = class(TEmar_ChargingTariffPrice)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_ChargingTariffPriceList = class(TEmar_ChargingTariffPriceList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 47 - TEmar105_BusStopStand '}

  TEmar105_BusStopStand = class(TEmar_BusStopStand)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_BusStopStandList = class(TEmar_BusStopStandList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 48 - TEmar105_DriverList '}

  TEmar105_Driver = class(TEmar_Driver)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_DriverList = class(TEmar_DriverList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

{$ENDREGION}
{$REGION ' 51 - TEmar105_LineNumber '}

  TEmar105_LineNumber = class(TEmar_LineNumber)
  const
    RecordLength_v00        = 8;
    MaxLineNumberLength_v00 = 6;
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_LineNumberList = class(TEmar_LineNumberList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;
{$ENDREGION}
{$REGION ' 52 - TEmar205_Texts '}

  TEmar205_Texts = class(TEmar_Texts)
  private const
    __MAX_TEXT_LEN = 42;
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar205_TextsList = class(TEmar_TextsList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;
{$ENDREGION}
{$REGION ' 53 - TEmar205_Wifi '}

  TEmar205_Wifi = class(TEmar_Wifi)
  private
    function IPtoString(p: PByte): string;
    procedure StringToIP(p: PByte; IP: string);
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar205_WiFiList = class(TEmar_WifiList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;
{$ENDREGION}
{$ENDREGION}
{$REGION ' Dane raportu '}

  TEmar105_StartedRide = class(TEmar_StartedRide)
  public
    function RecordLength(aVer: byte = 0): integer; override;
    procedure LoadFromBuffer(aStream: TStream; aVer: byte = 0); override;
    procedure SaveToBuffer(aStream: TStream; aVer: byte = 0); override;
  end;

  TEmar105_StartedRideList = class(TEmar_StartedRideList)
  protected
    function _AddItem: IEmar_Interface; override;
  end;

  TEmar105_ReportEventList = class(TEmar_ReportEventList)
  protected
    function createItem(aKind: integer): IEmar_ReportEvent; override; stdcall;
  public
    function LoadFromStream(aStream: TStream): cardinal; override;
    function SaveToStream(aStream: TStream; aAtPage: integer = 0): cardinal; override;
  end;

{$REGION ' 101-00 '}

  TEmar105_ReportEvent_00 = class(TEmar_ReportEvent_00)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  public
  end;

{$ENDREGION}
{$REGION ' 101-01 '}

  TEmar105_ReportEvent_01 = class(TEmar_ReportEvent_01)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-02 '}

  TEmar105_ReportEvent_02 = class(TEmar_ReportEvent_02)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-03 '}

  TEmar105_ReportEvent_03 = class(TEmar_ReportEvent_03)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-04 '}

  TEmar105_ReportEvent_04 = class(TEmar_ReportEvent_04)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-05 '}

  TEmar105_ReportEvent_05 = class(TEmar_ReportEvent_05)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-06 '}

  TEmar105_ReportEvent_06 = class(TEmar_ReportEvent_06)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-07 '}

  TEmar105_ReportEvent_07 = class(TEmar_ReportEvent_07)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    // procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-08 '}

  TEmar105_ReportEvent_08 = class(TEmar_ReportEvent_08)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-09 '}

  TEmar105_ReportEvent_09 = class(TEmar_ReportEvent_09)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-10 '}

  TEmar105_ReportEvent_10 = class(TEmar_ReportEvent_10)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-11 '}

  TEmar105_ReportEvent_11 = class(TEmar_ReportEvent_11)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-12 '}

  TEmar105_ReportEvent_12 = class(TEmar_ReportEvent_12)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-13 '}

  TEmar105_ReportEvent_13 = class(TEmar_ReportEvent_13)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-14 '}

  TEmar105_ReportEvent_14 = class(TEmar_ReportEvent_14)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-15 '}

  TEmar105_ReportEvent_15 = class(TEmar_ReportEvent_15)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-16 '}

  TEmar105_ReportEvent_16 = class(TEmar_ReportEvent_16)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-17 '}

  TEmar105_ReportEvent_17 = class(TEmar_ReportEvent_17)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-18 '}

  TEmar105_ReportEvent_18 = class(TEmar_ReportEvent_18)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-19 '}

  TEmar105_ReportEvent_19 = class(TEmar_ReportEvent_19)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-20 '}

  TEmar105_ReportEvent_20 = class(TEmar_ReportEvent_20)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-21 '}

  TEmar105_ReportEvent_21 = class(TEmar_ReportEvent_21)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-22 '}

  TEmar105_ReportEvent_22 = class(TEmar_ReportEvent_22)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-23 '}

  TEmar105_ReportEvent_23 = class(TEmar_ReportEvent_23)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-24 '}

  TEmar105_ReportEvent_24 = class(TEmar_ReportEvent_24)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-25 '}

  TEmar105_ReportEvent_25 = class(TEmar_ReportEvent_25)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-26 '}

  TEmar105_ReportEvent_26 = class(TEmar_ReportEvent_26)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-27 '}

  TEmar105_ReportEvent_27 = class(TEmar_ReportEvent_27)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-28 '}

  TEmar105_ReportEvent_28 = class(TEmar_ReportEvent_28)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-29 '}

  TEmar105_ReportEvent_29 = class(TEmar_ReportEvent_29)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-30 '}

  TEmar105_ReportEvent_30 = class(TEmar_ReportEvent_30)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-31 '}

  TEmar105_ReportEvent_31 = class(TEmar_ReportEvent_31)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-32 '}

  TEmar105_ReportEvent_32 = class(TEmar_ReportEvent_32)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    function IsNotDuplicated: LongBool;

    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-33 '}

  TEmar105_ReportEvent_33 = class(TEmar_ReportEvent_33)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-34 '}

  TEmar105_ReportEvent_34 = class(TEmar_ReportEvent_34)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-35 '}

  TEmar105_ReportEvent_35 = class(TEmar_ReportEvent_35)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-36 '}

  TEmar105_ReportEvent_36 = class(TEmar_ReportEvent_36)
  private
    /// <summary>
    /// Przelicza ceny biletów GOTÓWKA - KARTA PŁATNICZA
    /// </summary>
    procedure _RecalculateTicketPrices();
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-37 '}

  TEmar105_ReportEvent_37 = class(TEmar_ReportEvent_37)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-38 '}

  TEmar105_ReportEvent_38 = class(TEmar_ReportEvent_38)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-40 '}

  TEmar105_ReportEvent_40 = class(TEmar_ReportEvent_40)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-41 '}

  TEmar105_ReportEvent_41 = class(TEmar_ReportEvent_41)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-42 '}

  TEmar105_ReportEvent_42 = class(TEmar_ReportEvent_42)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$REGION ' 101-43 '}

  TEmar105_ReportEvent_43 = class(TEmar_ReportEvent_43)
  protected
    procedure AllocDataMem; override;
    function GetDataLength: integer; override;
  public
    procedure GetFromData(aData: pointer = nil); override;
    procedure SetToData(aData: pointer = nil); override;
  end;

{$ENDREGION}
{$ENDREGION}
{$REGION ' TEmar105_File '}

  TEmar105_File = class(TEmar_BaseFile, IEmar105_File)
  private
    fUSBStream:                          TEmarFlashUSBStream;
    fUsbDevice:                          TEmarUSBDevice;
    fStream:                             TMemoryStream;
    fCalBegin, fCalEnd:                  string;
    fMaxTicketPrice5, fMaxTicketPrice10: Integer;
    fRatePTU1_A, fRatePTU1_B, fRatePTU1_C, fRatePTU1_D, fRatePTU1_E, fRatePTU1_F, fRatePTU1_G: Integer;
    fRatePTU2_A, fRatePTU2_B, fRatePTU2_C, fRatePTU2_D, fRatePTU2_E, fRatePTU2_F, fRatePTU2_G: Integer;
    fRatePTU_N: Integer;

    F_SavedReadyCode: Integer; // do przechowywania OIK.ReadyCode do zmiany
    F_IsEmar205:      Boolean;
    // do statusu bileterki pod czas odczytu raportu; UWAGA: zmienia się podz czas odczytu zdrazeń raportu
    F_Event01_TicketRegister: string; // logo bierzącej bileterki; UWAGA: zmienia się podz czas odczytu zdrazeń raportu
    F_Event01_LastTicketNumberHighPart: Byte;
    // zapamiętuje ze zdarzenia 01 starszy bajt do ostatniego biletu pod czas odczytu raportu; UWAGA: zmienia się podz czas odczytu zdrazeń raportu
    F_Event01_LastTicketNumber: Cardinal;
    // zapamiętuje ze zdarzenia 01 ostatni bilet pod czas odczytu raportu; UWAGA: zmienia się podz czas odczytu zdrazeń raportu
    { Property methods }
    function GetOik: IEmar105_OIK; stdcall;
    function GetConsts: IEmar105_Consts; stdcall;
    procedure StreamOnBeforePageRead(aSender: TObject; aPage: integer; var aBreak: LongBool);
    procedure StreamOnBeforePageWrite(aSender: TObject; aPage: integer; var aBreak: LongBool);
    procedure StreamOnBeforePageClear(aSender: TObject; aPage: integer; var aBreak: LongBool);
    procedure StreamOnBeforeBlockClear(aSender: TObject; aPage: integer; var aBreak: LongBool);
  protected
    function _GetCalendarBegin: pchar; override;
    function _GetCalendarEnd: pchar; override;
    function _GetMaxTicketPrice5: Integer; override;
    function _GetMaxTicketPrice10: Integer; override;
    function _GetRatePTU1_A: Integer; override;
    function _GetRatePTU1_B: Integer; override;
    function _GetRatePTU1_C: Integer; override;
    function _GetRatePTU1_D: Integer; override;
    function _GetRatePTU1_E: Integer; override;
    function _GetRatePTU1_F: Integer; override;
    function _GetRatePTU1_G: Integer; override;
    function _GetRatePTU2_A: Integer; override;
    function _GetRatePTU2_B: Integer; override;
    function _GetRatePTU2_C: Integer; override;
    function _GetRatePTU2_D: Integer; override;
    function _GetRatePTU2_E: Integer; override;
    function _GetRatePTU2_F: Integer; override;
    function _GetRatePTU2_G: Integer; override;
    function _GetRatePTU_N: Integer; override;
    function _GetCurrentRatePTU(ds: TDateTime; aIndex: integer): integer; override;
    procedure _Clear; override;
    function _RecordVersion(aFileVersion, aId: integer): integer; override;
    function SetOIKReadyCodeNextReportCode(aState: byte; aNextReportCode: PChar; aLoadFromCard: boolean): cardinal;
    function LoadAFileFromDevice: cardinal;
    function _LoadOtherParts(aStream: TStream): longword; override;
    function GetDevice00ReportCode(var aReportCode: pchar): longword;
    function GetDeviceCardSerialNumber(var aCardSerialNumber: Cardinal): LongWord;
    function _GetTicketNumberUsedHighPart(ATicketNumber: Word; AForcedIncrementationHighPart: Boolean): Cardinal;
    function _GetIsSimpleTicketWronglyPrinted(ATicketControlCode: String): Boolean;
    function _GetIsSimpleTicketWrong(AEventIndex: Integer): Boolean; override;
    procedure _SetTicketBuyerNIP(AEvent42Index: Integer); override;

    /// <summary>
    /// do przechowywania OIK.ReadyCode do zmiany; gdy 0 - RedyCode nie był jeszcze zmieniany
    /// </summary>
    property _SavedReadyCode: Integer
      read   F_SavedReadyCode
      write  F_SavedReadyCode;
  public
    constructor Create;
    destructor Destroy; override;
    { Methods }
    function SaveToFile(aFilePath: pchar; aVersion: integer; aSaveMode: integer): longword; override; stdcall;
    function DeviceClose(aLedsOff: boolean = false): longword; stdcall;
    function DeviceOpen(aDevicePath: pchar): longword; stdcall;
    function DeviceIsOpened: boolean; stdcall;
    /// <summary>
    ///   Read OIK.CardSerialNumber directly from the device, not earlier laoded data and stored in fUSBStream
    /// </summary>
    function DeviceIsDriverCard(aDriverCardSerialNo: pchar): longword; stdcall;
    function DeviceReadAll(aFileName: pchar): longword; override; stdcall;
    function DeviceIsReport(aBufferForTimeTableFileName: pchar; aBufferSize: longword): longword; override; stdcall;
    function DeviceGetReport(aA80FileName: PChar): longword; override; stdcall;
    function DeviceReportErase(aEraseExtraData: LongBool; aNextReportCode: pchar = nil): longword; override; stdcall;
    function DeviceWriteAll(aFileName: pchar; aParams: pointer): longword; override; stdcall;
    function DeviceWriteFile(aFileName: pchar; aParams: pointer): longword; override; stdcall;
    function DeviceChangeStatus(aParams: pointer): longword; override; stdcall;
    function DeviceSetReadBy(aParams: pointer): longword; override; stdcall;
    function DeviceUpdateAddData(aParams: pointer): longword; override; stdcall;
    /// <summary>
    ///   Read OIK.ReadyCode directly from the device, not earlier laoded data and stored in fUSBStream
    /// </summary>
    function DeviceReadyCode(): longword; override; stdcall;
    /// <summary>
    ///   Read OIK.MaufactureDate directly from the device, not earlier laoded data and stored in fUSBStream
    /// </summary>
    function DeviceManufactureDate(): PChar; override; stdcall;
    function DeviceRollbackReadyCode(): longword; override; stdcall;
    function DeviceBeginProgramming(aNextReportCode: PChar): LongWord; override; stdcall;
    function DeviceEndProgramming(): LongWord; override; stdcall;

    /// <summary>
    ///   Porównywanie raportów
    ///     aCompareReportFileName:        z tym raportem zamierzamy porównywać
    ///                                    (w Self też już jest odczytany raport Source)
    /// </summary>
    function CompareFile(aCompareReportFileName: PChar): LongWord; override; stdcall;

    function ReportCashValue(): LongWord; override; stdcall;
    { Properties }
    property OIK: IEmar105_OIK
      read   GetOik;
    property Consts: IEmar105_Consts
      read   GetConsts;
    property USBStream: TEmarFlashUSBStream
      read   fUSBStream;
  end;

function New_Emar105_File: IEmar105_File; stdcall;
function New_Emar105_File_With_Callback(aCallback: IEmar_Callback): IEmar105_File; stdcall;

{$ENDREGION}

implementation

uses
  Emar.LogFile,
  emar105.json.helpers,
  emar.Types;

resourcestring
  STR105_OLDFILEVERSION = 'Bileterka EMAR-105. Wersja zbioru jest przedawniona. Obsługiwane są wersje 6 i wyższe.';

const
  chNormalHeight = #3;
  chDoubleHeight = #4;
  chNormalWidth  = #1;
  chDoubleWidth  = #2;

function MaxHeaderFooterLength(aValue: string; aMaxLength: integer = 32): integer;
var
  i, c:       integer;
  inDblWidth: boolean;
begin
  Result := aMaxLength;
  if Result = 0 then Exit;
  inDblWidth := false;
  c := 0;
  for i := 1 to Length(aValue) do begin
    case aValue[i] of
    chNormalHeight, chDoubleHeight: Inc(c);
    chNormalWidth: begin
        inDblWidth := false;
        Inc(c);
      end;
    chDoubleWidth: begin
        inDblWidth := true;
        Inc(c);
      end;
  else begin
      Inc(c);
      if inDblWidth then Inc(c);
    end;
    end;
    if c > aMaxLength then Exit(i);
  end;
end;

function NormalizeHeaderFooterText(aValue: string; aMaxLength: integer = 32): string;
var
  ix: integer;
begin
  ix := MaxHeaderFooterLength(aValue, aMaxLength);
  Result := Copy(aValue, 1, ix);
end;

function ControlSymbolsToOIK(aValue: string; aMaxLength: integer = 32): ansistring;
begin
  aValue := StringReplace(aValue, '\4', #1, [rfReplaceAll]);
  aValue := StringReplace(aValue, '\3', #2, [rfReplaceAll]);
  aValue := StringReplace(aValue, '\1', #3, [rfReplaceAll]);
  aValue := StringReplace(aValue, '\2', #4, [rfReplaceAll]);
  Result := ansistring(NormalizeHeaderFooterText(aValue, aMaxLength).TrimRight());
end;

function ControlSymbolsToClass(s: string): string;
begin
  s := StringReplace(s, #1, '\4', [rfReplaceAll]);
  s := StringReplace(s, #2, '\3', [rfReplaceAll]);
  s := StringReplace(s, #3, '\1', [rfReplaceAll]);
  s := StringReplace(s, #4, '\2', [rfReplaceAll]);
  Result := s.TrimRight();
end;

{$REGION ' 03 - TEmar105_OIK '}

function TEmar105_OIK.GetCardSerialNumber: cardinal;
begin
  Result := fCardSerialNumber;
end;

function TEmar105_OIK.GetManufactureDate: pchar;
begin
  Result := pchar(fMaufactureDate);
end;

function TEmar105_OIK.GetCardType: pchar;
begin
  Result := pchar(fCardType);
end;

function TEmar105_OIK.GetCompanyCardOwner: integer;
begin
  Result := fCompanyCardOwner;
end;

function TEmar105_OIK.GetCardCapacityCode: integer;
begin
  Result := fCardCapacityCode;
end;

function TEmar105_OIK.GetCardRegisterDate: pchar;
begin
  Result := pchar(fCardRegisterDate);
end;

function TEmar105_OIK.GetNextReportCode: pchar;
begin
  Result := pchar(fNextReportCode);
end;

function TEmar105_OIK.GetNIP: pchar;
begin
  Result := pchar(fNIP);
end;

function TEmar105_OIK.GetHeader1: pchar;
begin
  Result := pchar(fHeader1);
end;

function TEmar105_OIK.GetHeader2: pchar;
begin
  Result := pchar(fHeader2);
end;

function TEmar105_OIK.GetHeader3: pchar;
begin
  Result := pchar(fHeader3);
end;

function TEmar105_OIK.GetHeader4: pchar;
begin
  Result := pchar(fHeader4);
end;

function TEmar105_OIK.GetFooter1: pchar;
begin
  Result := pchar(fFooter1);
end;

function TEmar105_OIK.GetFooter2: pchar;
begin
  Result := pchar(fFooter2);
end;

function TEmar105_OIK.GetFooter3: pchar;
begin
  Result := pchar(fFooter3);
end;

function TEmar105_OIK.GetDriverNumber: cardinal;
begin
  Result := fDriverNumber;
end;

function TEmar105_OIK.GetDDFileName: pchar;
begin
  Result := pchar(fDDFileName);
end;

function TEmar105_OIK.GetDriverFirstName: pchar;
begin
  Result := pchar(fDriverFirstName);
end;

function TEmar105_OIK.GetDriverLastName: pchar;
begin
  Result := pchar(fDriverLastName);
end;

function TEmar105_OIK.GetPIN: integer;
begin
  Result := fPIN;
end;

function TEmar105_OIK.GetPPAddedCardCount: integer;
begin
  Result := fPPAddedCardCount;
end;

function TEmar105_OIK.GetEmployeeStatus: integer;
begin
  Result := fEmployeeStatus;
end;

constructor TEmar105_OIK.Create(aOwner: TEmar_BaseFile; aId: integer);
begin
  inherited;
  fSalePrefSet := TEmar_DriverSalePrefSet.Create;
end;

destructor TEmar105_OIK.Destroy;
begin
  fSalePrefSet := nil;
  inherited;
end;

procedure TEmar105_OIK.ForceUpdateFlash;
var
  t: TEmar105_File;
begin
  Nr := 1;
  t := TEmar105_File(Owner);
  t.USBStream.Seek(fPageNr);
  SaveToBuffer(t.fUSBStream);
  t.fUSBStream.ForceUpdatePage(fPageNr);
  Nr := 2;
  t.USBStream.Seek(fPageNr);
  SaveToBuffer(t.fUSBStream);
  t.fUSBStream.ForceUpdatePage(fPageNr);
end;

function TEmar105_OIK.GetAddDataProgram: pchar;
begin
  Result := pchar(fAddDataProgram);
end;

function TEmar105_OIK.GetAddDataSaveDate: pchar;
begin
  Result := pchar(fAddDataSaveDate);
end;

function TEmar105_OIK.GetAddDataSaveTime: pchar;
begin
  Result := pchar(fAddDataSaveTime);
end;

function TEmar105_OIK.GetBranchNumber: integer;
begin
  Result := fBranchNumber;
end;

function TEmar105_OIK.GetCardAssignDate: pchar;
begin
  Result := pchar(fCardAssignDate);
end;

function TEmar105_OIK.GetTimeTableFileExt: pchar;
begin
  Result := pchar(fTimeTableFileExt);
end;

function TEmar105_OIK.GetTimeTableFileName: pchar;
begin
  Result := pchar(fTimeTableFileName);
end;

function TEmar105_OIK.GetTimeTableSaveFileDate: pchar;
begin
  Result := pchar(fTimeTableSaveFileDate);
end;

function TEmar105_OIK.GetTimeTableSaveFileTime: pchar;
begin
  Result := pchar(fTimeTableSaveFileTime);
end;

procedure TEmar105_OIK.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  p: PEmar105_OIK_v7;
  bIsEmar205Export: Boolean;
  i: Integer;
  sAFileName: String;
begin
  sAFileName := String(Owner.AFileName);
  bIsEmar205Export :=
    (sAFileName.Length > 8)
    and(
      (Copy(sAFileName, 1, 2).ToUpper = 'CE') // Emar205 CE report export file format (CE0_nnnnnn_sssssssssssss_xxxxxxxxxxxxxx.DAT)
      or
      (Copy(sAFileName, 1, 4).ToUpper = 'A80_') // Emar205 A80 export file format (A80_nnnn_xxxxxxxxxxxxxx.DAT)
      and(Copy(sAFileName, 9, 1).ToUpper = '_')
    );

  aStream.Seek(fPageNr * SizeOf(fPage), soFromBeginning);
  aStream.read(fPage, SizeOf(fPage));
  p := @fPage.aContent[0];
  fCardSerialNumber := CalcCardinal(p^.CardSerialNumber);
  fMaufactureDate := EmarDateToString(p^.ManufactureDate);
  fCardType := CopyLStr(p^.CardType, SizeOf(p^.CardType) - 1);
  fCardCapacityCode := p^.CardCapacityCode;
  fCardRegisterDate := EmarDateToString(p^.CardRegisterDate);
  fNIP := CopyLStr(p^.NIP, SizeOf(p^.NIP) - 1);
  fHeader1 := ControlSymbolsToClass(CopyLStr(p^.Header1, SizeOf(p^.Header1) - 1));
  fHeader2 := ControlSymbolsToClass(CopyLStr(p^.Header2, SizeOf(p^.Header2) - 1));
  fHeader3 := ControlSymbolsToClass(CopyLStr(p^.Header3, SizeOf(p^.Header3) - 1));
  fHeader4 := ControlSymbolsToClass(CopyLStr(p^.Header4, SizeOf(p^.Header4) - 1));
  fFooter1 := ControlSymbolsToClass(CopyLStr(p^.Footer1, SizeOf(p^.Footer1) - 1));
  fFooter2 := ControlSymbolsToClass(CopyLStr(p^.Footer2, SizeOf(p^.Footer2) - 1));
  fFooter3 := ControlSymbolsToClass(CopyLStr(p^.Footer3, SizeOf(p^.Footer3) - 1));
  fDriverNumber := CalcCardinal(p^.DriverNumber);
  fDriverFirstName := Trim(CopyLStr(p^.DriverFirstName, SizeOf(p^.DriverFirstName) - 1));
  fDriverLastName := Trim(CopyLStr(p^.DriverLastName, SizeOf(p^.DriverLastName) - 1));
  fPIN := CalcWord(p^.PIN);
  fEmployeeStatus := p^.EmployeeStatus;
  fCardAssignDate := EmarDateToString(p^.CardAssignDate);
  fTimeTableFileName := CopyLStr(p^.TimeTableFileName, SizeOf(p^.TimeTableFileName) - 1);
  fTimeTableSaveFileDate := EmarDateToString(p^.TimeTableSaveFileDate);
  fTimeTableSaveFileTime := EmarTimeToString(p^.TimeTableSaveFileTime);

  SalePrefSet.MaxPassengersOnGroupTicket := p^.MaxPassangerCountOnTicket;
  SalePrefSet.DaysBeforePrompt := p^.RemindsSettlementDayCount;
  fReadyCode := p^.ReadyCode;
  fTaskReportFileName := CopyLStr(p^.TaskReportFileName, SizeOf(p^.TaskReportFileName) - 1);
  fStatesSaveDate := EmarDateToString(p^.StatesSaveDate);
  fStatesSaveTime := EmarTimeToString(p^.StatesSaveTime);
  fCompanyCardOwner := CalcWord(p^.CompanyCardOwner);
  fNextReportCode := CopyLStr(p^.NextReportCode, SizeOf(p^.NextReportCode));
  SalePrefSet.DaysBeforeBlock := p^.BlockSaleDayCount;
  fReportFileNameAddStand := CopyLStr(p^.ReportFileNameAddStand, SizeOf(p^.ReportFileNameAddStand));
  fBranchNumber := p^.BranchNumber;
  fTimeTableFileExt := CopyLStr(p^.TimeTableFileExt, SizeOf(p^.TimeTableFileExt) - 1);
  fAddDataSaveDate := EmarDateToString(p^.AddDataSaveDate);
  fAddDataSaveTime := EmarTimeToString(p^.AddDataSaveTime);
  fDDFileName := CopyLStr(p^.DDFileName, SizeOf(p^.DDFileName) - 1);
  fPZAddedCardCount := CalcWord(p^.PZAddedCardCount);
  fPZDeletedCardCount := CalcWord(p^.PZDeletedCardCount);
  fPPAddedCardCount := CalcWord(p^.PPAddedCardCount);
  fAddDataProgram := CopyLStr(p^.AddDataProgram, SizeOf(p^.AddDataProgram));
  fReadCardDate := EmarDateToString(p^.ReadCardDate);
  fReadCardTime := EmarTimeToString(p^.ReadCardTime);
  fReadCardProgram := CopyLStr(p^.ReadCardProgram, SizeOf(p^.ReadCardProgram));

  SalePrefSet.CardStatus[1] := p^.Status1;
  SalePrefSet.CardStatus[2] := p^.Status2;
  SalePrefSet.CardStatus[3] := p^.Status3;
  SalePrefSet.CardStatus[4] := p^.Status4;

  SalePrefSet.Options205[1] := p^.Emar205Options_1;
  SalePrefSet.Options205[2] := p^.Emar205Options_2;
  SalePrefSet.Options205[3] := p^.Emar205Options_3;
  SalePrefSet.Options205[4] := p^.Emar205Options_4;

  if bIsEmar205Export then // A80 export file name
  begin
    {
      UWAGA! nazwę zbioru A8 lub DD w OIK zapisujemy pomiędzy bajtami:
      od 428 do 491 (w 427 FF) – począwszy od bajtu 428 uzupełnione do końca (od prawej) FF
    }
    sAFileName := '';
    i := 428;
    while (i < 492)and not(fPage.aContent[i] in [$0, $FF]) do
    begin
      sAFileName := sAFileName + CopyLStr(@fPage.aContent[i], 1);
      Inc(i);
    end;
    fTimeTableFileName := StringReplace(ExtractFileName(sAFileName), ExtractFileExt(sAFileName), '', []);
    fTimeTableFileExt := StringReplace(ExtractFileExt(sAFileName), '.', '', []);
    Owner.AFileName := PChar(sAFileName);
  end
  else
    Owner.AFileName := pchar(fTimeTableFileName + '.' + fTimeTableFileExt);
end;

function TEmar105_OIK.GetPZAddedCardCount: integer;
begin
  Result := fPZAddedCardCount;
end;

function TEmar105_OIK.GetPZDeletedCardCount: integer;
begin
  Result := fPZDeletedCardCount;
end;

function TEmar105_OIK.GetReadCardDate: pchar;
begin
  Result := pchar(fReadCardDate);
end;

function TEmar105_OIK.GetReadCardProgram: pchar;
begin
  Result := pchar(fReadCardProgram);
end;

function TEmar105_OIK.GetReadCardTime: pchar;
begin
  Result := pchar(fReadCardTime);
end;

function TEmar105_OIK.GetReadyCode: integer;
begin
  Result := fReadyCode;
end;

function TEmar105_OIK.GetReportFileNameAddStand: pchar;
begin
  Result := pchar(fReportFileNameAddStand);
end;

function TEmar105_OIK.GetSalePrefSet: IEmar_DriverSalePrefSet;
begin
  Result := fSalePrefSet;
end;

function TEmar105_OIK.GetStandAloneWorkMode: boolean;
begin
  Result := fStandAloneWorkMode;
end;

function TEmar105_OIK.GetStatesSaveDate: pchar;
begin
  Result := pchar(fStatesSaveDate);
end;

function TEmar105_OIK.GetStatesSaveTime: pchar;
begin
  Result := pchar(fStatesSaveTime);
end;

function TEmar105_OIK.GetTaskReportFileName: pchar;
begin
  Result := pchar(fTaskReportFileName);
end;

procedure TEmar105_OIK.SetCardSerialNumber(const Value: cardinal);
begin
  fCardSerialNumber := Value;
end;

procedure TEmar105_OIK.SetManufactureDate(const Value: pchar);
begin
  fMaufactureDate := Value;
end;

procedure TEmar105_OIK.SetCardType(const Value: pchar);
begin
  fCardType := Value;
end;

procedure TEmar105_OIK.SetCompanyCardOwner(const Value: integer);
begin
  fCompanyCardOwner := Value;
end;

procedure TEmar105_OIK.SetCardCapacityCode(const Value: integer);
begin
  fCardCapacityCode := Value;
end;

procedure TEmar105_OIK.SetCardRegisterDate(const Value: pchar);
begin
  fCardRegisterDate := Value;
end;

procedure TEmar105_OIK.SetNextReportCode(const Value: pchar);
begin
  fNextReportCode := Value;
end;

procedure TEmar105_OIK.SetNIP(const Value: pchar);
begin
  fNIP := Value;
end;

procedure TEmar105_OIK.SetHeader1(const Value: pchar);
begin
  fHeader1 := Value;
end;

procedure TEmar105_OIK.SetHeader2(const Value: pchar);
begin
  fHeader2 := Value;
end;

procedure TEmar105_OIK.SetHeader3(const Value: pchar);
begin
  fHeader3 := Value;
end;

procedure TEmar105_OIK.SetHeader4(const Value: pchar);
begin
  fHeader4 := Value;
end;

procedure TEmar105_OIK.SetFooter1(const Value: pchar);
begin
  fFooter1 := Value;
end;

procedure TEmar105_OIK.SetFooter2(const Value: pchar);
begin
  fFooter2 := Value;
end;

procedure TEmar105_OIK.SetFooter3(const Value: pchar);
begin
  fFooter3 := Value;
end;

procedure TEmar105_OIK.SetDriverNumber(const Value: cardinal);
begin
  fDriverNumber := Value;
end;

procedure TEmar105_OIK.SetDDFileName(const Value: pchar);
begin
  fDDFileName := Value;
end;

procedure TEmar105_OIK.SetDriverFirstName(const Value: pchar);
begin
  fDriverFirstName := Value;
end;

procedure TEmar105_OIK.SetDriverLastName(const Value: pchar);
begin
  fDriverLastName := Value;
end;

procedure TEmar105_OIK.SetPIN(const Value: integer);
begin
  fPIN := Value;
end;

procedure TEmar105_OIK.SetPPAddedCardCount(const Value: integer);
begin
  fPPAddedCardCount := Value;
end;

procedure TEmar105_OIK.SetEmployeeStatus(const Value: integer);
begin
  fEmployeeStatus := Value;
end;

procedure TEmar105_OIK.SaveToBuffer(aStream: TStream; aVer: byte);
var
  p: PEmar105_OIK_v7;
  s: AnsiString;
  iPos, iBranchNumber: Byte;
  sLastSavedFileNameUpper: AnsiString;
begin
  p := @fPage.aContent[0];
  FillChar(fPage.aContent, SizeOf(fPage.aContent), $FF);

  sLastSavedFileNameUpper := AnsiString(ExtractFileName(String(Owner.LastSavedFileName).ToUpper));

  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    if fCardType <> '' then begin
      p^.CardSerialNumber := CalcCardinal(fCardSerialNumber);
      DateToEmarDate(p^.ManufactureDate, fMaufactureDate);
      StrPLCopy(p^.CardType, ansistring(fCardType), SizeOf(p^.CardType) - 1);
      p^.CardCapacityCode := fCardCapacityCode;
      DateToEmarDate(p^.CardRegisterDate, fCardRegisterDate);
    end;
  end;
  if fNIP <> '' then StrPLCopy(p^.NIP, ansistring(fNIP), Length(Trim(fNIP)), True);
  // zakończony kodem #0. UWAGA: jeśli NIP ma mniej znaków niż 13, to po znaku #0 bufor jest wypełniony do końca kodami #255 ($ff).

  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    FillChar(p^.Header1, 4 * SizeOf(p^.Header1), 0);
    FillChar(p^.Footer1, 3 * SizeOf(p^.Footer1), 0);

    if fHeader1 <> '' then begin
      s := ControlSymbolsToOIK(fHeader1);
      StrPLCopy(p^.Header1, s, Length(s), True, #0);
    end;
    if fHeader2 <> '' then begin
      s := ControlSymbolsToOIK(fHeader2);
      StrPLCopy(p^.Header2, s, Length(s), True, #0);
    end;
    if fHeader3 <> '' then begin
      s := ControlSymbolsToOIK(fHeader3);
      StrPLCopy(p^.Header3, s, Length(s), True, #0);
    end;
    if fHeader4 <> '' then begin
      s := ControlSymbolsToOIK(fHeader4);
      StrPLCopy(p^.Header4, s, Length(s), True, #0);
    end;
    if fFooter1 <> '' then begin
      s := ControlSymbolsToOIK(fFooter1);
      StrPLCopy(p^.Footer1, s, Length(s), True, #0);
    end;
    if fFooter2 <> '' then begin
      s := ControlSymbolsToOIK(fFooter2);
      StrPLCopy(p^.Footer2, s, Length(s), True, #0);
    end;
    if fFooter3 <> '' then begin
      s := ControlSymbolsToOIK(fFooter3);
      StrPLCopy(p^.Footer3, s, Length(s), True, #0);
    end;
    if fDriverNumber > 0 then p^.DriverNumber := CalcCardinal(fDriverNumber);
    if fDriverFirstName <> '' then
        StrPLCopy(p^.DriverFirstName, ansistring(fDriverFirstName), SizeOf(p^.DriverFirstName) - 1);
    if fDriverLastName <> '' then
        StrPLCopy(p^.DriverLastName, ansistring(fDriverLastName), SizeOf(p^.DriverLastName) - 1);
    if fPin > 0 then p^.PIN := CalcWord(fPIN);
    p^.EmployeeStatus := byte(fEmployeeStatus and $FF);
    DateToEmarDate(p^.CardAssignDate, fCardAssignDate);
    if fTimeTableFileName <> '' then
        StrPLCopy(p^.TimeTableFileName, ansistring(fTimeTableFileName), SizeOf(p^.TimeTableFileName) - 1);
    DateToEmarDate(p^.TimeTableSaveFileDate, fTimeTableSaveFileDate);
    TimeToEmarTime(p^.TimeTableSaveFileTime, fTimeTableSaveFileTime);

    p^.MaxPassangerCountOnTicket := byte(SalePrefSet.MaxPassengersOnGroupTicket);
    p^.RemindsSettlementDayCount := byte(SalePrefSet.DaysBeforePrompt);
    p^.ReadyCode := fReadyCode;
    if fTaskReportFileName <> '' then
        StrPLCopy(p^.TaskReportFileName, ansistring(fTaskReportFileName), SizeOf(p^.TaskReportFileName) - 1, True);
    DateToEmarDate(p^.StatesSaveDate, fStatesSaveDate);
    TimeToEmarTime(p^.StatesSaveTime, fStatesSaveTime);
  end;
  p^.CompanyCardOwner := CalcWord(fCompanyCardOwner);
  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    if fNextReportCode <> '' then StrPLCopy(p^.NextReportCode, ansistring(fNextReportCode), SizeOf(p^.NextReportCode));
    p^.BlockSaleDayCount := byte(SalePrefSet.DaysBeforeBlock);
    if fReportFileNameAddStand <> '' then
        StrPLCopy(p^.ReportFileNameAddStand, ansistring(fReportFileNameAddStand), SizeOf(p^.ReportFileNameAddStand));
  end;
  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then
    p^.BranchNumber := fBranchNumber
  else
  begin
    iBranchNumber := $FF;
    iPos := Pos('.DAT', String(sLastSavedFileNameUpper));
    if iPos > 3 then
    begin
      // if file name ends with '_xx.DAT' - it means, xx is a department number
      if sLastSavedFileNameUpper[iPos - 3] = '_' then
        iBranchNumber := StrToIntDef(Copy(String(sLastSavedFileNameUpper), iPos - 2, 2), $FF);
    end;
    p^.BranchNumber := iBranchNumber;
  end;

  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    if fTimeTableFileExt <> '' then
        StrPLCopy(p^.TimeTableFileExt, ansistring(fTimeTableFileExt), SizeOf(p^.TimeTableFileExt) - 1);
    DateToEmarDate(p^.AddDataSaveDate, fAddDataSaveDate);
    TimeToEmarTime(p^.AddDataSaveTime, fAddDataSaveTime);
    if fDDFileName <> '' then StrPLCopy(p^.DDFileName, ansistring(fDDFileName), SizeOf(p^.DDFileName) - 1);
    p^.PZAddedCardCount := CalcWord(fPZAddedCardCount);
    p^.PZDeletedCardCount := CalcWord(fPZDeletedCardCount);
    p^.PPAddedCardCount := CalcWord(fPPAddedCardCount);
    if fAddDataProgram <> '' then StrPLCopy(p^.AddDataProgram, ansistring(fAddDataProgram), SizeOf(p^.AddDataProgram));
    DateToEmarDate(p^.ReadCardDate, fReadCardDate);
    TimeToEmarTime(p^.ReadCardTime, fReadCardTime);
    if fReadCardProgram <> '' then
        StrPLCopy(p^.ReadCardProgram, ansistring(fReadCardProgram), SizeOf(p^.ReadCardProgram));

    p^.Status1 := SalePrefSet.CardStatus[1];
    p^.Status2 := SalePrefSet.CardStatus[2];
    p^.Status3 := SalePrefSet.CardStatus[3];
    p^.Status4 := SalePrefSet.CardStatus[4];

    p^.Emar205Options_1 := SalePrefSet.Options205[1];
    p^.Emar205Options_2 := SalePrefSet.Options205[2];
    p^.Emar205Options_3 := SalePrefSet.Options205[3];
    p^.Emar205Options_4 := SalePrefSet.Options205[4];

    p^.XOR_CardNoAndDate := EmarXORSum(p^.CardSerialNumber, 12);
  end;
  p^.XOR_NIP := EmarXORSum(p^.NIP, SizeOf(p^.NIP));
  if not(SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    p^.XOR_Headers := EmarXORSum(p^.Header1, SizeOf(p^.Header1) * 4);
    p^.XOR_Footers := EmarXORSum(p^.Footer1, SizeOf(p^.Footer1) * 3);
    p^.XOR_PIN := EmarXORSum(p^.PIN, SizeOf(p^.PIN));
    p^.XOR_358 := EmarXORSum(p^.Status1, 4);
  end;

{$REGION '  A80 or DD0 export file name'}
  {
    UWAGA! nazwę zbioru A8 lub DD w OIK zapisujemy pomiędzy bajtami:
    od 428 do 491 (w 427 FF) – począwszy od bajtu 428 uzupełnione do końca (od prawej) FF
  }
  if SaveMode in [EMAR_SAVEMODE_FILE_A80_EXPORT, EMAR_SAVEMODE_FILE_DD0_EXPORT] then
    Move(sLastSavedFileNameUpper[1], fPage.aContent[428], Length(sLastSavedFileNameUpper));
{$ENDREGION}

  FillPageCtrlBytes(fPage, Id, fPageNr, $FFFF, $FFFF);
  Owner.AFileName := pchar(fTimeTableFileName + '.' + fTimeTableFileExt);
  if Assigned(aStream) then aStream.Write(fPage, SizeOf(fPage));
end;

procedure TEmar105_OIK.SetAddDataProgram(const Value: pchar);
begin
  fAddDataProgram := Value;
end;

procedure TEmar105_OIK.SetAddDataSaveDate(const Value: pchar);
begin
  fAddDataSaveDate := Value;
end;

procedure TEmar105_OIK.SetAddDataSaveTime(const Value: pchar);
begin
  fAddDataSaveTime := Value;
end;

procedure TEmar105_OIK.SetBranchNumber(const Value: integer);
begin
  fBranchNumber := Value;
end;

procedure TEmar105_OIK.SetCardAssignDate(const Value: pchar);
begin
  fCardAssignDate := Value;
end;

procedure TEmar105_OIK.SetTimeTableFileExt(const Value: pchar);
begin
  fTimeTableFileExt := Value;
end;

procedure TEmar105_OIK.SetTimeTableFileName(const Value: pchar);
var
  s, e: string;
begin
  s := Value;
  e := ExtractFileExt(s);
  if Length(e) = 4 then begin
    s := Copy(s, 1, Length(s) - 4);
    fTimeTableFileExt := Copy(e, 2, 3);
  end;
  fTimeTableFileName := s;
end;

procedure TEmar105_OIK.SetTimeTableSaveFileDate(const Value: pchar);
begin
  fTimeTableSaveFileDate := Value;
end;

procedure TEmar105_OIK.SetTimeTableSaveFileTime(const Value: pchar);
begin
  fTimeTableSaveFileTime := Value;
end;

procedure TEmar105_OIK._Clear;
begin
  TEmar_DriverSalePrefSet(FSalePrefSet).Clear;
  fCardSerialNumber := 0;
  fMaufactureDate := '';
  fCardType := '';
  fCardCapacityCode := 0;
  fCardRegisterDate := '';
  fNIP := '';
  fHeader1 := '';
  fHeader2 := '';
  fHeader3 := '';
  fHeader4 := '';
  fFooter1 := '';
  fFooter2 := '';
  fFooter3 := '';
  fDriverNumber := 0;
  fDriverFirstName := '';
  fDriverLastName := '';
  fPIN := 0;
  fEmployeeStatus := 0;
  fCardAssignDate := '';
  fTimeTableFileName := '';
  fTimeTableSaveFileDate := '';
  fTimeTableSaveFileTime := '';
  fReadyCode := 0;
  fTaskReportFileName := '';
  fStatesSaveDate := '';
  fStatesSaveTime := '';
  fCompanyCardOwner := 0;
  fNextReportCode := '';
  fReportFileNameAddStand := '';
  fBranchNumber := 0;
  fTimeTableFileExt := '';
  fStandAloneWorkMode := false;
  fAddDataSaveDate := '';
  fAddDataSaveTime := '';
  fDDFileName := '';
  fPZAddedCardCount := 0;
  fPZDeletedCardCount := 0;
  fPPAddedCardCount := 0;
  fAddDataProgram := '';
  fReadCardDate := '';
  fReadCardTime := '';
  fReadCardProgram := '';
end;

procedure TEmar105_OIK.SetPZAddedCardCount(const Value: integer);
begin
  fPZAddedCardCount := Value;
end;

procedure TEmar105_OIK.SetPZDeletedCardCount(const Value: integer);
begin
  fPZDeletedCardCount := Value;
end;

procedure TEmar105_OIK.SetReadCardDate(const Value: pchar);
begin
  fReadCardDate := Value;
end;

procedure TEmar105_OIK.SetReadCardProgram(const Value: pchar);
begin
  fReadCardProgram := Value;
end;

procedure TEmar105_OIK.SetReadCardTime(const Value: pchar);
begin
  fReadCardTime := Value;
end;

procedure TEmar105_OIK.SetReadyCode(const Value: integer);
begin
  fReadyCode := Value;
end;

procedure TEmar105_OIK.SetReportFileNameAddStand(const Value: pchar);
begin
  fReportFileNameAddStand := Value;
end;

procedure TEmar105_OIK.SetStandAloneWorkMode(const Value: boolean);
begin
  fStandAloneWorkMode := Value;
end;

procedure TEmar105_OIK.SetStatesSaveDate(const Value: pchar);
begin
  fStatesSaveDate := Value;
end;

procedure TEmar105_OIK.SetStatesSaveTime(const Value: pchar);
begin
  fStatesSaveTime := Value;
end;

procedure TEmar105_OIK.SetTaskReportFileName(const Value: pchar);
begin
  fTaskReportFileName := Value;
end;

{$ENDREGION}
{$REGION ' 07 - TEmar105_Consts '}

function TEmar105_Consts.GetCalendarBegin: pchar;
begin
  Result := pchar(fCalendarBegin);
end;

function TEmar105_Consts.GetCalendarEnd: pchar;
begin
  Result := pchar(fCalendarEnd);
end;

function TEmar105_Consts.GetCalendarDayCount: integer;
begin
  Result := fCalendarDayCount;
end;

function TEmar105_Consts.GetProgramMaker: pchar;
begin
  Result := pchar(fProgramMaker);
end;

function TEmar105_Consts.GetProgramMakerVersion: pchar;
begin
  Result := pchar(fProgramMakerVersion);
end;

function TEmar105_Consts.GetPTU1ValidFrom: pchar;
begin
  Result := pchar(fPTU1ValidFrom);
end;

function TEmar105_Consts.GetRatePTU1_A: integer;
begin
  Result := fRatePTU1_A;
end;

function TEmar105_Consts.GetRatePTU1_B: integer;
begin
  Result := fRatePTU1_B;
end;

function TEmar105_Consts.GetRatePTU1_C: integer;
begin
  Result := fRatePTU1_C;
end;

function TEmar105_Consts.GetRatePTU1_D: integer;
begin
  Result := fRatePTU1_D;
end;

function TEmar105_Consts.GetRatePTU1_E: integer;
begin
  Result := fRatePTU1_E;
end;

function TEmar105_Consts.GetRatePTU1_F: integer;
begin
  Result := fRatePTU1_F;
end;

function TEmar105_Consts.GetRatePTU1_G: integer;
begin
  Result := fRatePTU1_G;
end;

function TEmar105_Consts.GetPTU2ValidFrom: pchar;
begin
  Result := pchar(fPTU2ValidFrom);
end;

function TEmar105_Consts.GetRatePTU2_A: integer;
begin
  Result := fRatePTU2_A;
end;

function TEmar105_Consts.GetRatePTU2_B: integer;
begin
  Result := fRatePTU2_B;
end;

function TEmar105_Consts.GetRatePTU2_C: integer;
begin
  Result := fRatePTU2_C;
end;

function TEmar105_Consts.GetRatePTU2_D: integer;
begin
  Result := fRatePTU2_D;
end;

function TEmar105_Consts.GetRatePTU2_E: integer;
begin
  Result := fRatePTU2_E;
end;

function TEmar105_Consts.GetRatePTU2_F: integer;
begin
  Result := fRatePTU2_F;
end;

function TEmar105_Consts.GetRatePTU2_G: integer;
begin
  Result := fRatePTU2_G;
end;

function TEmar105_Consts.GetFileVersion: integer;
begin
  Result := Owner.Version;
end;

function TEmar105_Consts.GetFirstWeekDay: integer;
begin
  Result := fFirstWeekDay;
end;

function TEmar105_Consts.GetMaxTicketPrice5: cardinal;
begin
  Result := fMaxTicketPrice5;
end;

function TEmar105_Consts.GetMaxTicketPrice10: cardinal;
begin
  Result := fMaxTicketPrice10;
end;

function TEmar105_Consts.GetRatePTU_N: integer;
begin
  Result := fRatePTU_N;
end;

function TEmar105_Consts.GetTariffCurrencyCode: pchar;
begin
  Result := pchar(fTariffCurrencyCode);
end;

function TEmar105_Consts.GetTariffCurrencyDateChange: pchar;
begin
  Result := pchar(fTariffCurrencyDateChange);
end;

function TEmar105_Consts.GetTariffAfterChangeCurrencyCode: pchar;
begin
  Result := pchar(fTariffAfterChangeCurrencyCode);
end;

function TEmar105_Consts.GetBusStopCount: integer;
begin
  Result := fBusStopCount;
end;

function TEmar105_Consts.GetBusStopListDate: pchar;
begin
  Result := pchar(fBusStopListDate);
end;

function TEmar105_Consts.GetDayFileNumber: integer;
begin
  Result := fDayFileNumber;
end;

function TEmar105_Consts.GetCurrencyValidFrom: pchar;
begin
  Result := pchar(fCurrencyValidFrom);
end;

function TEmar105_Consts.GetCurrencyCode: pchar;
begin
  Result := pchar(fCurrencyCode);
end;

function TEmar105_Consts.GetTransitionStartPeriod: pchar;
begin
  Result := pchar(fTransitionStartPeriod);
end;

procedure TEmar105_Consts.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  p:      PEmar105_Consts_rec;
  ver, i: integer;
begin
  aStream.Seek(fPageNr * SizeOf(fPage), soFromBeginning);
  aStream.read(fPage, SizeOf(fPage));
  Clear;
  p := @fPage.aContent[0];
  ver := 0;
  if (p^.DBVer0 = 0) and (p^.DBVer1 = 1) and (p^.DBVer2 = 2) and (p^.DBVer3 = 3) and (p^.DBVer4 = 4) and (p^.DBVer6 = 6)
  then
    if p^.DBVer5 = 5 then begin
      if p^.DBVer7 = 7 then ver := 8
      else ver := 7;
    end
    else ver := 6;
  if ver > 0 then begin
    Owner.Version := ver;

    fCalendarBegin := EmarDateToString(p^.CalendarBegin);
    fCalendarEnd := EmarDateToString(p^.CalendarEnd);
    fCalendarDayCount := DaysBetween(fCalendarBegin, fCalendarEnd) + 1;
    fPTU1ValidFrom := EmarDateToString(p^.PTU1ValidFrom);
    fRatePTU1_A := CalcWord(p^.RatePTU1_A);
    fRatePTU1_B := CalcWord(p^.RatePTU1_B);
    fRatePTU1_C := CalcWord(p^.RatePTU1_C);
    fRatePTU1_D := CalcWord(p^.RatePTU1_D);
    fRatePTU1_E := CalcWord(p^.RatePTU1_E);
    fRatePTU1_F := CalcWord(p^.RatePTU1_F);
    fRatePTU1_G := CalcWord(p^.RatePTU1_G);

    fPTU2ValidFrom := EmarDateToString(p^.PTU2ValidFrom);
    fRatePTU2_A := CalcWord(p^.RatePTU2_A);
    fRatePTU2_B := CalcWord(p^.RatePTU2_B);
    fRatePTU2_C := CalcWord(p^.RatePTU2_C);
    fRatePTU2_D := CalcWord(p^.RatePTU2_D);
    fRatePTU2_E := CalcWord(p^.RatePTU2_E);
    fRatePTU2_F := CalcWord(p^.RatePTU2_F);
    fRatePTU2_G := CalcWord(p^.RatePTU2_G);

    fFirstWeekDay := p^.FirstWeekDay;
    fMaxTicketPrice5 := CalcCardinal(cardinal(p^.MaxTicketPrice5));
    fMaxTicketPrice10 := CalcCardinal(cardinal(p^.MaxTicketPrice10));
    fRatePTU_N := CalcWord(p^.RatePTU_N);
    fTariffCurrencyCode := CopyLStr(p^.TariffCurrencyCode, SizeOf(p^.TariffCurrencyCode) - 1);
    fTariffCurrencyDateChange := EmarDateToString(p^.TariffCurrencyDateChange);
    if fTariffCurrencyDateChange <> '' then
        fTariffAfterChangeCurrencyCode := CopyLStr(p^.TariffAfterChangeCurrencyCode,
        SizeOf(p^.TariffAfterChangeCurrencyCode) - 1);
    fBusStopCount := CalcWord(p^.BusStopCount);
    fBusStopListDate := EmarDateToString(p^.BusStopListDate);
    fDayFileNumber := p^.DayFileNumber;
    AddPageCount := CalcWord(p^.AddPageCount);
    fSHA_Key := '';
    for i := 0 to Length(p^.SHA_Key) - 1 do begin
      fSHA_Key := fSHA_Key + IntToHex(p^.SHA_Key[i], 2);
    end;
    if CompareText(fSHA_Key, StringOfChar('F', 40)) = 0 then fSHA_Key := '';

    fIsMakeFileParams := p^.IsMakeFileParams = $AA;

    if fIsMakeFileParams then begin
      fBranchNumber := p^.BranchNumber;

      fSaveRidesWithoutBranch := p^.State and $01 > 0;
      fSaveAllRides := p^.State and $02 > 0;

      fCalcTariffDistance := p^.SaveState and $04 > 0;
      fTariffDistance := p^.SaveState and $08 > 0;
      fConditionalBusStops := p^.SaveState and $10 > 0;
      fSaveAllLines := p^.SaveState and $20 > 0;
      fOwnRidesOnly := p^.SaveState and $40 > 0;
      fSaveRideRoute := p^.SaveState and $80 > 0;
    end;

    RideOutsideBusStopNames := p^.RideOutsideBusStopNames;
    fSaveToTicketRegisterFrom := EmarDateToString(p^.SaveToTicketRegisterFrom);

    if p^.CalendarChangeCount <> $FF then begin
      fCalendarChangeCount := p^.CalendarChangeCount;
      fCalendarDate1 := EmarDateToString(p^.CalendarDate1);
      fCalendarFormula1 := EmarDateToString(p^.CalendarFormula1);
      fCalendarDate2 := EmarDateToString(p^.CalendarDate2);
      fCalendarFormula2 := EmarDateToString(p^.CalendarFormula2);
      fCalendarDate3 := EmarDateToString(p^.CalendarDate3);
      fCalendarFormula3 := EmarDateToString(p^.CalendarFormula3);
      fCalendarDate4 := EmarDateToString(p^.CalendarDate4);
      fCalendarFormula4 := EmarDateToString(p^.CalendarFormula4);
      fCalendarDate5 := EmarDateToString(p^.CalendarDate5);
      fCalendarFormula4 := EmarDateToString(p^.CalendarFormula4);
      fCalendarDate6 := EmarDateToString(p^.CalendarDate6);
      fCalendarFormula6 := EmarDateToString(p^.CalendarFormula6);
      fCalendarDate7 := EmarDateToString(p^.CalendarDate7);
      fCalendarFormula7 := EmarDateToString(p^.CalendarFormula7);
      fCalendarDate8 := EmarDateToString(p^.CalendarDate8);
      fCalendarFormula8 := EmarDateToString(p^.CalendarFormula8);
      fCalendarDate9 := EmarDateToString(p^.CalendarDate9);
      fCalendarFormula9 := EmarDateToString(p^.CalendarFormula9);
    end;

    fProgramMaker := CopyLStr(p^.ProgramMaker, SizeOf(p^.ProgramMaker) - 1);
    if fProgramMaker = '' then
      fProgramMaker := 'I2.0'; // otherwise LineNumber error shall be occurred
    fProgramMakerVersion := CopyLStr(p^.ProgramMakerVersion, SizeOf(p^.ProgramMakerVersion) - 1);

    if ver >= 7 then begin
      fCurrencyValidFrom := EmarDateToString(p^.CurrencyValidFrom.rDate) + ' ' +
        EmarTimeToString(p^.CurrencyValidFrom.rTime);
      fCurrencyCode := CopyLStr(p^.CurrencyCode, SizeOf(p^.CurrencyCode) - 1);
      fTransitionStartPeriod := EmarDateToString(p^.TransitionStartPeriod);
      fTransitionEndPeriod := EmarDateToString(p^.TransitionEndPeriod);
      fExchangeRatePLN := 0;
      fExchangeRate := 0;
      fNewCurrencyCode := '';
      fCurrencyDateChange := EmarDateToString(p^.CurrencyDateChange.rDate);
      if fCurrencyDateChange <> '' then begin
        ExchangeRatePLN := CalcCardinal(p^.ExchangeRatePLN);
        fNewCurrencyCode := CopyLStr(p^.NewCurrencyCode, SizeOf(p^.NewCurrencyCode) - 1);
        fExchangeRate := integer(CalcCardinal(p^.ExchangeRate));
        fCurrencyDateChange := fCurrencyDateChange + ' ' + EmarTimeToString(p^.CurrencyDateChange.rTime);
      end;
      fTimeChangeKind1 := 0;
      fTimeChangeFrom1 := '';
      fTimeChangeKind2 := 0;
      fTimeChangeFrom2 := '';
      fTimeChangeKind3 := 0;
      fTimeChangeFrom3 := '';
      fTimeChangeKind4 := 0;
      fTimeChangeFrom4 := '';
      if p^.TimeChangeKind1 <> 0 then begin
        fTimeChangeKind1 := p^.TimeChangeKind1;
        fTimeChangeFrom1 := EmarDateToString(p^.TimeChangeFrom1.rDate) + ' ' +
          EmarTimeToString(p^.TimeChangeFrom1.rTime);
      end;
      if p^.TimeChangeKind2 <> 0 then begin
        fTimeChangeKind2 := p^.TimeChangeKind2;
        fTimeChangeFrom2 := EmarDateToString(p^.TimeChangeFrom2.rDate) + ' ' +
          EmarTimeToString(p^.TimeChangeFrom2.rTime);
      end;
      if p^.TimeChangeKind3 <> 0 then begin
        fTimeChangeKind3 := p^.TimeChangeKind3;
        fTimeChangeFrom3 := EmarDateToString(p^.TimeChangeFrom3.rDate) + ' ' +
          EmarTimeToString(p^.TimeChangeFrom3.rTime);
      end;
      if p^.TimeChangeKind4 <> 0 then begin
        fTimeChangeKind4 := p^.TimeChangeKind4;
        fTimeChangeFrom4 := EmarDateToString(p^.TimeChangeFrom4.rDate) + ' ' +
          EmarTimeToString(p^.TimeChangeFrom4.rTime);
      end;
    end;
  end
  else
    if not(Owner.IsEmar205OnlineReport() or Owner.IsEmar205OnlineDD0()) then // CE* online report has an empty CONSTS page
      raise EEmarFileVersion.Create(STR105_OLDFILEVERSION);
end;

function TEmar105_Consts.GetTransitionEndPeriod: pchar;
begin
  Result := pchar(fTransitionEndPeriod);
end;

function TEmar105_Consts.GetExchangeRatePLN: cardinal;
begin
  Result := fExchangeRatePLN;
end;

function TEmar105_Consts.GetNewCurrencyCode: pchar;
begin
  Result := pchar(fNewCurrencyCode);
end;

function TEmar105_Consts.GetExchangeRate: cardinal;
begin
  Result := fExchangeRate;
end;

function TEmar105_Consts.GetCurrencyDateChange: pchar;
begin
  Result := pchar(fCurrencyDateChange);
end;

function TEmar105_Consts.GetTimeChangeKind1: integer;
begin
  Result := fTimeChangeKind1;
end;

function TEmar105_Consts.GetTimeChangeFrom1: pchar;
begin
  Result := pchar(fTimeChangeFrom1);
end;

function TEmar105_Consts.GetTimeChangeKind2: integer;
begin
  Result := fTimeChangeKind2;
end;

function TEmar105_Consts.GetTimeChangeFrom2: pchar;
begin
  Result := pchar(fTimeChangeFrom2);
end;

function TEmar105_Consts.GetTimeChangeKind3: integer;
begin
  Result := fTimeChangeKind3;
end;

function TEmar105_Consts.GetTimeChangeFrom3: pchar;
begin
  Result := pchar(fTimeChangeFrom3);
end;

function TEmar105_Consts.GetTimeChangeKind4: integer;
begin
  Result := fTimeChangeKind4;
end;

function TEmar105_Consts.GetTimeChangeFrom4: pchar;
begin
  Result := pchar(fTimeChangeFrom4);
end;

function TEmar105_Consts.GetAddPageCount: integer;
begin
  Result := fAddPageCount;
end;

function TEmar105_Consts.GetSHA_Key: pchar;
begin
  Result := pchar(fSHA_Key);
end;

function TEmar105_Consts.GetIsMakeFileParams: boolean;
begin
  Result := fIsMakeFileParams;
end;

function TEmar105_Consts.GetBranchNumber: integer;
begin
  Result := fBranchNumber;
end;

function TEmar105_Consts.GetSaveAllRides: boolean;
begin
  Result := fSaveAllRides;
end;

function TEmar105_Consts.GetSaveRidesWithoutBranch: boolean;
begin
  Result := fSaveRidesWithoutBranch;
end;

function TEmar105_Consts.GetBranchName: pchar;
begin
  Result := pchar(fBranchName);
end;

function TEmar105_Consts.GetOwnRidesOnly: boolean;
begin
  Result := fOwnRidesOnly;
end;

function TEmar105_Consts.GetSaveAllLines: boolean;
begin
  Result := fSaveAllLines;
end;

function TEmar105_Consts.GetSaveRideRoute: boolean;
begin
  Result := fSaveRideRoute;
end;

function TEmar105_Consts.GetConditionalBusStops: boolean;
begin
  Result := fConditionalBusStops;
end;

function TEmar105_Consts.GetTariffDistance: boolean;
begin
  Result := fTariffDistance;
end;

function TEmar105_Consts.GetCalcTariffDistance: boolean;
begin
  Result := fCalcTariffDistance;
end;

function TEmar105_Consts.GetRideOutsideBusStopNames: integer;
begin
  Result := fRideOutsideBusStopNames;
end;

function TEmar105_Consts.GetSaveToTicketRegisterFrom: pchar;
begin
  Result := pchar(fSaveToTicketRegisterFrom);
end;

function TEmar105_Consts.GetCalendarChangeCount: integer;
begin
  Result := fCalendarChangeCount;
end;

function TEmar105_Consts.GetCalendarDate1: pchar;
begin
  Result := pchar(fCalendarDate1);
end;

function TEmar105_Consts.GetCalendarFormula1: pchar;
begin
  Result := pchar(fCalendarFormula1);
end;

function TEmar105_Consts.GetCalendarDate2: pchar;
begin
  Result := pchar(fCalendarDate2);
end;

function TEmar105_Consts.GetCalendarFormula2: pchar;
begin
  Result := pchar(fCalendarFormula2);
end;

function TEmar105_Consts.GetCalendarDate3: pchar;
begin
  Result := pchar(fCalendarDate3);
end;

function TEmar105_Consts.GetCalendarFormula3: pchar;
begin
  Result := pchar(fCalendarFormula3);
end;

function TEmar105_Consts.GetCalendarDate4: pchar;
begin
  Result := pchar(fCalendarDate4);
end;

function TEmar105_Consts.GetCalendarFormula4: pchar;
begin
  Result := pchar(fCalendarFormula4);
end;

function TEmar105_Consts.GetCalendarDate5: pchar;
begin
  Result := pchar(fCalendarDate5);
end;

function TEmar105_Consts.GetCalendarFormula5: pchar;
begin
  Result := pchar(fCalendarFormula5);
end;

function TEmar105_Consts.GetCalendarDate6: pchar;
begin
  Result := pchar(fCalendarDate6);
end;

function TEmar105_Consts.GetCalendarFormula6: pchar;
begin
  Result := pchar(fCalendarFormula6);
end;

function TEmar105_Consts.GetCalendarDate7: pchar;
begin
  Result := pchar(fCalendarDate7);
end;

function TEmar105_Consts.GetCalendarFormula7: pchar;
begin
  Result := pchar(fCalendarFormula7);
end;

function TEmar105_Consts.GetCalendarDate8: pchar;
begin
  Result := pchar(fCalendarDate8);
end;

function TEmar105_Consts.GetCalendarFormula8: pchar;
begin
  Result := pchar(fCalendarFormula8);
end;

function TEmar105_Consts.GetCalendarDate9: pchar;
begin
  Result := pchar(fCalendarDate9);
end;

function TEmar105_Consts.GetCalendarFormula9: pchar;
begin
  Result := pchar(fCalendarFormula9);
end;

procedure TEmar105_Consts.SetCalendarBegin(const Value: pchar);
begin
  fCalendarBegin := Value;
end;

procedure TEmar105_Consts.SetCalendarEnd(const Value: pchar);
begin
  fCalendarEnd := Value;
end;

procedure TEmar105_Consts.SetCalendarDayCount(const Value: integer);
begin
  fCalendarDayCount := Value;
end;

procedure TEmar105_Consts.SetProgramMaker(const Value: pchar);
begin
  fProgramMaker := AnsiUpperCase(Value);
end;

procedure TEmar105_Consts.SetProgramMakerVersion(const Value: pchar);
begin
  fProgramMakerVersion := Value;
end;

procedure TEmar105_Consts.SetPTU1ValidFrom(const Value: pchar);
begin
  fPTU1ValidFrom := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_A(const Value: integer);
begin
  fRatePTU1_A := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_B(const Value: integer);
begin
  fRatePTU1_B := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_C(const Value: integer);
begin
  fRatePTU1_C := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_D(const Value: integer);
begin
  fRatePTU1_D := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_E(const Value: integer);
begin
  fRatePTU1_E := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_F(const Value: integer);
begin
  fRatePTU1_F := Value;
end;

procedure TEmar105_Consts.SetRatePTU1_G(const Value: integer);
begin
  fRatePTU1_G := Value;
end;

procedure TEmar105_Consts.SetPTU2ValidFrom(const Value: pchar);
begin
  fPTU2ValidFrom := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_A(const Value: integer);
begin
  fRatePTU2_A := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_B(const Value: integer);
begin
  fRatePTU2_B := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_C(const Value: integer);
begin
  fRatePTU2_C := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_D(const Value: integer);
begin
  fRatePTU2_D := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_E(const Value: integer);
begin
  fRatePTU2_E := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_F(const Value: integer);
begin
  fRatePTU2_F := Value;
end;

procedure TEmar105_Consts.SetRatePTU2_G(const Value: integer);
begin
  fRatePTU2_G := Value;
end;

procedure TEmar105_Consts.SetFirstWeekDay(const Value: integer);
begin
  fFirstWeekDay := Value;
end;

procedure TEmar105_Consts.SetMaxTicketPrice5(const Value: cardinal);
begin
  fMaxTicketPrice5 := Value;
end;

procedure TEmar105_Consts.SetMaxTicketPrice10(const Value: cardinal);
begin
  fMaxTicketPrice10 := Value;
end;

procedure TEmar105_Consts.SetRatePTU_N(const Value: integer);
begin
  fRatePTU_N := Value;
end;

procedure TEmar105_Consts.SetTariffCurrencyCode(const Value: pchar);
begin
  fTariffCurrencyCode := Value;
end;

procedure TEmar105_Consts.SetTariffCurrencyDateChange(const Value: pchar);
begin
  fTariffCurrencyDateChange := Value;
end;

procedure TEmar105_Consts.SetTariffAfterChangeCurrencyCode(const Value: pchar);
begin
  fTariffAfterChangeCurrencyCode := Value;
end;

procedure TEmar105_Consts.SetBusStopCount(const Value: integer);
begin
  fBusStopCount := Value;
end;

procedure TEmar105_Consts.SetBusStopListDate(const Value: pchar);
begin
  fBusStopListDate := Value;
end;

procedure TEmar105_Consts.SetDayFileNumber(const Value: integer);
begin
  fDayFileNumber := Value;
end;

procedure TEmar105_Consts.SetCurrencyValidFrom(const Value: pchar);
begin
  fCurrencyValidFrom := Value;
end;

procedure TEmar105_Consts.SetCurrencyCode(const Value: pchar);
begin
  fCurrencyCode := Value;
end;

procedure TEmar105_Consts.SetTransitionStartPeriod(const Value: pchar);
begin
  fTransitionStartPeriod := Value;
end;

procedure TEmar105_Consts._Clear;
begin
  fCalendarBegin := '';
  fCalendarEnd := '';
  fCalendarDayCount := 0;
  fPTU1ValidFrom := '';
  fRatePTU1_A := 0;
  fRatePTU1_B := 0;
  fRatePTU1_C := 0;
  fRatePTU1_D := 0;
  fRatePTU1_E := 0;
  fRatePTU1_F := 0;
  fRatePTU1_G := 0;
  fPTU2ValidFrom := '';
  fRatePTU2_A := 0;
  fRatePTU2_B := 0;
  fRatePTU2_C := 0;
  fRatePTU2_D := 0;
  fRatePTU2_E := 0;
  fRatePTU2_F := 0;
  fRatePTU2_G := 0;
  fFirstWeekDay := 0;
  fMaxTicketPrice5 := 0;
  fMaxTicketPrice10 := 0;
  fRatePTU_N := 0;
  fTariffCurrencyCode := '';
  fTariffCurrencyDateChange := '';
  fTariffAfterChangeCurrencyCode := '';
  fBusStopCount := 0;
  fBusStopListDate := '';
  fDayFileNumber := 0;
  fCurrencyValidFrom := '';
  fCurrencyCode := '';
  fTransitionStartPeriod := '';
  fTransitionEndPeriod := '';
  fExchangeRatePLN := 0;
  fNewCurrencyCode := '';
  fExchangeRate := 0;
  fCurrencyDateChange := '';
  fTimeChangeKind1 := 0;
  fTimeChangeFrom1 := '';
  fTimeChangeKind2 := 0;
  fTimeChangeFrom2 := '';
  fTimeChangeKind3 := 0;
  fTimeChangeFrom3 := '';
  fTimeChangeKind4 := 0;
  fTimeChangeFrom4 := '';
  fAddPageCount := 0;
  fSHA_Key := '';
  fIsMakeFileParams := false;
  fBranchNumber := 0;
  fSaveAllRides := false;
  fSaveRidesWithoutBranch := false;
  fBranchName := '';
  fOwnRidesOnly := false;
  fSaveAllLines := false;
  fSaveRideRoute := false;
  fConditionalBusStops := false;
  fTariffDistance := false;
  fCalcTariffDistance := false;
  fRideOutsideBusStopNames := 0;
  fSaveToTicketRegisterFrom := '';
  fCalendarChangeCount := 0;
  fCalendarDate1 := '';
  fCalendarFormula1 := '';
  fCalendarDate2 := '';
  fCalendarFormula2 := '';
  fCalendarDate3 := '';
  fCalendarFormula3 := '';
  fCalendarDate4 := '';
  fCalendarFormula4 := '';
  fCalendarDate5 := '';
  fCalendarFormula5 := '';
  fCalendarDate6 := '';
  fCalendarFormula6 := '';
  fCalendarDate7 := '';
  fCalendarFormula7 := '';
  fCalendarDate8 := '';
  fCalendarFormula8 := '';
  fCalendarDate9 := '';
  fCalendarFormula9 := '';
end;

procedure TEmar105_Consts.SetTransitionEndPeriod(const Value: pchar);
begin
  fTransitionEndPeriod := Value;
end;

procedure TEmar105_Consts.SetExchangeRatePLN(const Value: cardinal);
begin
  fExchangeRatePLN := Value;
end;

procedure TEmar105_Consts.SetNewCurrencyCode(const Value: pchar);
begin
  fNewCurrencyCode := Value;
end;

procedure TEmar105_Consts.SetExchangeRate(const Value: cardinal);
begin
  fExchangeRate := Value;
end;

procedure TEmar105_Consts.SetCurrencyDateChange(const Value: pchar);
begin
  fCurrencyDateChange := Value;
end;

procedure TEmar105_Consts.SetTimeChangeKind1(const Value: integer);
begin
  fTimeChangeKind1 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeFrom1(const Value: pchar);
begin
  fTimeChangeFrom1 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeKind2(const Value: integer);
begin
  fTimeChangeKind2 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeFrom2(const Value: pchar);
begin
  fTimeChangeFrom2 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeKind3(const Value: integer);
begin
  fTimeChangeKind3 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeFrom3(const Value: pchar);
begin
  fTimeChangeFrom3 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeKind4(const Value: integer);
begin
  fTimeChangeKind4 := Value;
end;

procedure TEmar105_Consts.SetTimeChangeFrom4(const Value: pchar);
begin
  fTimeChangeFrom4 := Value;
end;

procedure TEmar105_Consts.SaveToBuffer(aStream: TStream; aVer: byte);
var
  p: PEmar105_Consts_rec;
  i: integer;
begin
  p := @fPage.aContent[0];
  FillChar(p^, SizeOf(p^), $FF);

  if not(SaveMode in [EMAR_SAVEMODE_FILE_DD0_EXPORT]) then // otherwise - $FF
  begin
    { wersja zbioru 6 }
    p^.DBVer0 := 0;
    p^.DBVer1 := 1;
    p^.DBVer2 := 2;
    p^.DBVer3 := 3;
    p^.DBVer4 := 4;
    p^.DBVer6 := 6;
    { wersja zbioru 7 }
    if aVer >= 7 then p^.DBVer5 := 5;
    { wersja zbioru 8 }
    if aVer >= 8 then p^.DBVer7 := 7;

    DateToEmarDate(p^.CalendarBegin, fCalendarBegin);
    DateToEmarDate(p^.CalendarEnd, fCalendarEnd);
    fCalendarDayCount := DaysBetween(fCalendarBegin, fCalendarEnd) + 1;
    p^.CalendarDayCount := CalcWord(word(fCalendarDayCount));
    DateToEmarDate(p^.PTU1ValidFrom, fPTU1ValidFrom);
    p^.RatePTU1_A := CalcWord(fRatePTU1_A);
    p^.RatePTU1_B := CalcWord(fRatePTU1_B);
    p^.RatePTU1_C := CalcWord(fRatePTU1_C);
    p^.RatePTU1_D := CalcWord(fRatePTU1_D);
    p^.RatePTU1_E := CalcWord(fRatePTU1_E);
    p^.RatePTU1_F := CalcWord(fRatePTU1_F);
    p^.RatePTU1_G := CalcWord(fRatePTU1_G);
    p^.XOR_PTU1 := EmarXORSum(p^.PTU1ValidFrom, SizeOf(p^.PTU1ValidFrom) + 7 * SizeOf(p^.RatePTU1_A));

    if fPTU2ValidFrom <> '' then begin
      DateToEmarDate(p^.PTU2ValidFrom, fPTU2ValidFrom);
      p^.RatePTU2_A := CalcWord(fRatePTU2_A);
      p^.RatePTU2_B := CalcWord(fRatePTU2_B);
      p^.RatePTU2_C := CalcWord(fRatePTU2_C);
      p^.RatePTU2_D := CalcWord(fRatePTU2_D);
      p^.RatePTU2_E := CalcWord(fRatePTU2_E);
      p^.RatePTU2_F := CalcWord(fRatePTU2_F);
      p^.RatePTU2_G := CalcWord(fRatePTU2_G);
    end
    else FillChar(p^.PTU2ValidFrom, SizeOf(p^.PTU2ValidFrom) + 7 * SizeOf(p^.RatePTU2_A), 0);
    p^.XOR_PTU2 := EmarXORSum(p^.PTU2ValidFrom, SizeOf(p^.PTU2ValidFrom) + 7 * SizeOf(p^.RatePTU2_A));

    p^.FirstWeekDay := byte(fFirstWeekDay);
    p^.MaxTicketPrice5 := CalcCardinal(cardinal(fMaxTicketPrice5));
    p^.MaxTicketPrice10 := CalcCardinal(cardinal(fMaxTicketPrice10));
    p^.RatePTU_N := CalcWord(30000);
    StrPLCopy(p^.TariffCurrencyCode, ansistring(fTariffCurrencyCode), SizeOf(p^.TariffCurrencyCode) - 1);
    if fTariffCurrencyDateChange <> '' then begin
      DateToEmarDate(p^.TariffCurrencyDateChange, fTariffCurrencyDateChange);
      StrPLCopy(p^.TariffAfterChangeCurrencyCode, ansistring(fTariffAfterChangeCurrencyCode),
        SizeOf(p^.TariffAfterChangeCurrencyCode) - 1);
    end;
    p^.BusStopCount := CalcWord(fBusStopCount);
    DateToEmarDate(p^.BusStopListDate, fBusStopListDate);
    p^.DayFileNumber := fDayFileNumber;

    p^.AddPageCount := CalcWord(fAddPageCount);
    if (fSHA_Key <> '') and (Length(fSHA_Key) = SizeOf(p^.SHA_Key)) then begin
      for i := 0 to SizeOf(p^.SHA_Key) - 1 do p^.SHA_Key[i] := StrToInt('$' + Copy(fSHA_Key, (i shl 1) + 1, 2));
    end;

    if fIsMakeFileParams then begin
      p^.IsMakeFileParams := $AA;
      p^.BranchNumber := byte(fBranchNumber and $FF);

      p^.State := 0;
      if fSaveRidesWithoutBranch then p^.State := p^.State or $01;
      if fSaveAllRides then p^.State := p^.State or $02;

      p^.SaveState := 0;
      if fCalcTariffDistance then p^.SaveState := p^.SaveState or $04;
      if fTariffDistance then p^.SaveState := p^.SaveState or $08;
      if fConditionalBusStops then p^.SaveState := p^.SaveState or $10;
      if fSaveAllLines then p^.SaveState := p^.SaveState or $20;
      if fOwnRidesOnly then p^.SaveState := p^.SaveState or $40;
      if fSaveRideRoute then p^.SaveState := p^.SaveState or $80;
    end;

    p^.RideOutsideBusStopNames := byte(fRideOutsideBusStopNames and $FF);
    if fSaveToTicketRegisterFrom <> '' then DateToEmarDate(p^.SaveToTicketRegisterFrom, fSaveToTicketRegisterFrom);

    if fCalendarChangeCount > 0 then begin
      p^.CalendarChangeCount := byte(fCalendarChangeCount and $FF);
      if fCalendarDate1 <> '' then DateToEmarDate(p^.CalendarDate1, fCalendarDate1);
      if fCalendarFormula1 <> '' then DateToEmarDate(p^.CalendarFormula1, fCalendarFormula1);

      if fCalendarDate2 <> '' then DateToEmarDate(p^.CalendarDate2, fCalendarDate2);
      if fCalendarFormula2 <> '' then DateToEmarDate(p^.CalendarFormula2, fCalendarFormula2);

      if fCalendarDate3 <> '' then DateToEmarDate(p^.CalendarDate3, fCalendarDate3);
      if fCalendarFormula3 <> '' then DateToEmarDate(p^.CalendarFormula3, fCalendarFormula3);

      if fCalendarDate4 <> '' then DateToEmarDate(p^.CalendarDate4, fCalendarDate4);
      if fCalendarFormula4 <> '' then DateToEmarDate(p^.CalendarFormula4, fCalendarFormula4);

      if fCalendarDate5 <> '' then DateToEmarDate(p^.CalendarDate5, fCalendarDate5);
      if fCalendarFormula5 <> '' then DateToEmarDate(p^.CalendarFormula5, fCalendarFormula5);

      if fCalendarDate6 <> '' then DateToEmarDate(p^.CalendarDate6, fCalendarDate6);
      if fCalendarFormula6 <> '' then DateToEmarDate(p^.CalendarFormula6, fCalendarFormula6);

      if fCalendarDate7 <> '' then DateToEmarDate(p^.CalendarDate7, fCalendarDate7);
      if fCalendarFormula7 <> '' then DateToEmarDate(p^.CalendarFormula7, fCalendarFormula7);

      if fCalendarDate8 <> '' then DateToEmarDate(p^.CalendarDate8, fCalendarDate8);
      if fCalendarFormula8 <> '' then DateToEmarDate(p^.CalendarFormula8, fCalendarFormula8);

      if fCalendarDate9 <> '' then DateToEmarDate(p^.CalendarDate9, fCalendarDate9);
      if fCalendarFormula9 <> '' then DateToEmarDate(p^.CalendarFormula9, fCalendarFormula9);
    end;

    if aVer >= 7 then begin
      DateTimeToEmarDateTime(p^.CurrencyValidFrom, fCurrencyValidFrom);
      StrPLCopy(p^.CurrencyCode, ansistring(fCurrencyCode), SizeOf(p^.CurrencyCode) - 1);
      p^.XOR_Currency := EmarXORSum(p^.CurrencyValidFrom, SizeOf(p^.CurrencyValidFrom) + SizeOf(p^.CurrencyCode));
      if fTransitionStartPeriod <> '' then DateToEmarDate(p^.TransitionStartPeriod, fTransitionStartPeriod)
      else FillChar(p^.TransitionStartPeriod, SizeOf(p^.TransitionStartPeriod), 0);
      if fTransitionEndPeriod <> '' then DateToEmarDate(p^.TransitionEndPeriod, fTransitionEndPeriod)
      else FillChar(p^.TransitionEndPeriod, SizeOf(p^.TransitionEndPeriod), 0);
      p^.ExchangeRatePLN := 0;
      p^.ExchangeRate := 0;
      FillChar(p^.NewCurrencyCode, SizeOf(p^.NewCurrencyCode), 0);
      FillChar(p^.OldCurrencyCode, SizeOf(p^.OldCurrencyCode), 0);
      FillChar(p^.CurrencyDateChange, SizeOf(p^.CurrencyDateChange), 0);
      FillChar(p^.AfterChangeCurrencyCode, SizeOf(p^.AfterChangeCurrencyCode), 0);
      if fNewCurrencyCode <> '' then begin
        p^.ExchangeRatePLN := CalcCardinal(cardinal(fExchangeRatePLN));
        StrPLCopy(p^.NewCurrencyCode, ansistring(fNewCurrencyCode), SizeOf(p^.NewCurrencyCode) - 1);
        p^.ExchangeRate := CalcCardinal(cardinal(fExchangeRate));
        StrPLCopy(p^.OldCurrencyCode, ansistring(fCurrencyCode), SizeOf(p^.OldCurrencyCode) - 1);
        DateTimeToEmarDateTime(p^.CurrencyDateChange, fCurrencyDateChange);
        StrPLCopy(p^.AfterChangeCurrencyCode, ansistring(fNewCurrencyCode), SizeOf(p^.AfterChangeCurrencyCode) - 1);
      end;
      p^.XOR_CurrencyChange := EmarXORSum(p^.CurrencyDateChange, SizeOf(p^.CurrencyDateChange) +
        SizeOf(p^.AfterChangeCurrencyCode));
      FillChar(p^.TimeChangeKind1, 4 * (SizeOf(p^.TimeChangeKind1) + SizeOf(p^.TimeChangeFrom1)), 0);
      if fTimeChangeKind1 <> 0 then begin
        p^.TimeChangeKind1 := byte(fTimeChangeKind1 and $FF);
        DateTimeToEmarDateTime(p^.TimeChangeFrom1, fTimeChangeFrom1);
      end;
      if fTimeChangeKind2 <> 0 then begin
        p^.TimeChangeKind2 := byte(fTimeChangeKind2 and $FF);
        DateTimeToEmarDateTime(p^.TimeChangeFrom2, fTimeChangeFrom2);
      end;
      if fTimeChangeKind3 <> 0 then begin
        p^.TimeChangeKind3 := byte(fTimeChangeKind3 and $FF);
        DateTimeToEmarDateTime(p^.TimeChangeFrom3, fTimeChangeFrom3);
      end;
      if fTimeChangeKind4 <> 0 then begin
        p^.TimeChangeKind4 := byte(fTimeChangeKind4 and $FF);
        DateTimeToEmarDateTime(p^.TimeChangeFrom4, fTimeChangeFrom4);
      end;
      FillChar(p^.ProgramMaker[0], SizeOf(p^.ProgramMaker), 0);
      FillChar(p^.ProgramMakerVersion[0], SizeOf(p^.ProgramMakerVersion), 0);
    end;

    if fProgramMaker <> '' then StrPLCopy(p^.ProgramMaker, AnsiString(Trim(fProgramMaker)), SizeOf(p^.ProgramMaker) - 1, True, #0);
    if fProgramMakerVersion <> '' then
      StrPLCopy(p^.ProgramMakerVersion, AnsiString(Trim(fProgramMakerVersion)), SizeOf(p^.ProgramMakerVersion) - 1, True, #0);
  end;
  FillPageCtrlBytes(fPage, Id, fPageNr, $FFFF, $FFFF);
  aStream.Write(fPage, SizeOf(fPage));
end;

procedure TEmar105_Consts.SetAddPageCount(const Value: integer);
begin
  fAddPageCount := Value;
end;

procedure TEmar105_Consts.SetSHA_Key(const Value: pchar);
begin
  fSHA_Key := Value;
end;

procedure TEmar105_Consts.SetIsMakeFileParams(const Value: boolean);
begin
  fIsMakeFileParams := Value;
end;

procedure TEmar105_Consts.SetBranchNumber(const Value: integer);
begin
  fBranchNumber := Value;
end;

procedure TEmar105_Consts.SetSaveAllRides(const Value: boolean);
begin
  fSaveAllRides := Value;
end;

procedure TEmar105_Consts.SetSaveRidesWithoutBranch(const Value: boolean);
begin
  fSaveRidesWithoutBranch := Value;
end;

procedure TEmar105_Consts.SetBranchName(const Value: pchar);
begin
  fBranchName := Value;
end;

procedure TEmar105_Consts.SetOwnRidesOnly(const Value: boolean);
begin
  fOwnRidesOnly := Value;
end;

procedure TEmar105_Consts.SetSaveAllLines(const Value: boolean);
begin
  fSaveAllLines := Value;
end;

procedure TEmar105_Consts.SetSaveRideRoute(const Value: boolean);
begin
  fSaveRideRoute := Value;
end;

procedure TEmar105_Consts.SetConditionalBusStops(const Value: boolean);
begin
  fConditionalBusStops := Value;
end;

procedure TEmar105_Consts.SetTariffDistance(const Value: boolean);
begin
  fTariffDistance := Value;
end;

procedure TEmar105_Consts.SetCalcTariffDistance(const Value: boolean);
begin
  fCalcTariffDistance := Value;
end;

procedure TEmar105_Consts.SetRideOutsideBusStopNames(const Value: integer);
begin
  fRideOutsideBusStopNames := Value;
end;

procedure TEmar105_Consts.SetSaveToTicketRegisterFrom(const Value: pchar);
begin
  fSaveToTicketRegisterFrom := Value;
end;

procedure TEmar105_Consts.SetCalendarChangeCount(const Value: integer);
begin
  fCalendarChangeCount := Value;
end;

procedure TEmar105_Consts.SetCalendarDate1(const Value: pchar);
begin
  fCalendarDate1 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula1(const Value: pchar);
begin
  fCalendarFormula1 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate2(const Value: pchar);
begin
  fCalendarDate2 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula2(const Value: pchar);
begin
  fCalendarFormula2 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate3(const Value: pchar);
begin
  fCalendarDate3 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula3(const Value: pchar);
begin
  fCalendarFormula3 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate4(const Value: pchar);
begin
  fCalendarDate4 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula4(const Value: pchar);
begin
  fCalendarFormula4 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate5(const Value: pchar);
begin
  fCalendarDate5 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula5(const Value: pchar);
begin
  fCalendarFormula5 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate6(const Value: pchar);
begin
  fCalendarDate6 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula6(const Value: pchar);
begin
  fCalendarFormula6 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate7(const Value: pchar);
begin
  fCalendarDate7 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula7(const Value: pchar);
begin
  fCalendarFormula7 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate8(const Value: pchar);
begin
  fCalendarDate8 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula8(const Value: pchar);
begin
  fCalendarFormula8 := Value;
end;

procedure TEmar105_Consts.SetCalendarDate9(const Value: pchar);
begin
  fCalendarDate9 := Value;
end;

procedure TEmar105_Consts.SetCalendarFormula9(const Value: pchar);
begin
  fCalendarFormula9 := Value;
end;

{$ENDREGION}
{$REGION ' 08 - TEmar105_Company '}

procedure TEmar105_Company.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Company_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, SizeOf(r0));
      Id := r0.Id;
      Number := CalcWord(r0.Number);
      name := CopyPStr(r0.name, SizeOf(r0.name) - 1);
      ShortName := CopyPStr(r0.ShortName, SizeOf(r0.ShortName) - 1);
    end;
  end;
end;

function TEmar105_Company.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_Company_v0);
end;

procedure TEmar105_Company.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Company_v0;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r0, SizeOf(r0), 0);
      r0.Id := 8;
      r0.Number := CalcWord(Number);
      if name <> '' then StrPLCopy(r0.name, ansistring(name), 60, true, #0);
      if ShortName <> '' then StrPLCopy(r0.ShortName, ansistring(ShortName), 4, true, #0);
      aStream.write(r0, SizeOf(r0));
    end;
  end;
end;

function TEmar105_CompanyList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Company.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 09 - TEmar105_BusStop '}

procedure TEmar105_BusStop.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_BusStop_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      Code := CalcCardinal(r1.Code);
      ShortName := CopyPStr(r1.ShortName, SizeOf(r1.ShortName));
      name := CopyPStr(r1.name, SizeOf(r1.Name));
      BusBoardName := CopyPStr(r1.BusBoardName, SizeOf(r1.BusBoardName));
    end;
  end;
end;

function TEmar105_BusStop.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_BusStop_v1);
end;

procedure TEmar105_BusStop.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_BusStop_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      r1.Code := CalcCardinal(Code);
      if ShortName <> '' then StrPLCopy(r1.ShortName, AnsiString(Copy(ShortName, 1, 10)), 10);
      if name <> '' then StrPLCopy(r1.Name, AnsiString(name), SizeOf(r1.Name) - 1, true, #0);
      if BusBoardName <> '' then
          StrPLCopy(r1.BusBoardName, AnsiString(BusBoardName), SizeOf(r1.BusBoardName) - 1, true, #0);
      aStream.Write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_BusStopList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_BusStop.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 10 - TEmar105_Ride '}

procedure TEmar105_Ride.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r6: TEmar105_Ride_v6;
  w:  word;
  s:  string;
begin
  FillChar(r6, SizeOf(r6), 0);
  case aVer of
  6: aStream.read(r6, SizeOf(TEmar105_Ride_v5));
  7, 8: aStream.read(r6, SizeOf(r6));
  end;
  case aVer of
  6, 7, 8: begin
      Id := r6.Id;
      CompanyIndex := r6.CompanyIndex - 1;
      Number := CalcWord(r6.Number);
      fsNumber := CopyLStr(r6.sNumber, 4);
      fiNumber := CopyLStr(r6.iNumber, 4);
      s := CopyLStr(@r6.Version, 1);
      if s <> '' then fVersion := s[1]
      else fVersion := #0;
      IndexOfCalendar := CalcWord(r6.IndexOfCalendar) - 1;
      IndexOfRoute := integer(CalcCardinal(r6.IndexOfRoute)) - 1;
      BusStopCount := r6.BusStopCount;
      DepartureTime := CalcWord(r6.DepartureTime);
      TimeOfArrival := CalcWord(r6.TimeOfArrival);
      IndexOfFirstBusStop := CalcWord(r6.IndexOfFirstBusStop) - 1;
      IndexOfLastBusStop := CalcWord(r6.IndexOfLastBusStop) - 1;
      StandArrival := CopyPStr(r6.StandArrival, 3);
      IndexOfDesignation[0] := r6.IndexOfDesignation[0] - 1;
      IndexOfDesignation[1] := r6.IndexOfDesignation[1] - 1;
      IndexOfDesignation[2] := r6.IndexOfDesignation[2] - 1;
      IndexOfDesignation[3] := r6.IndexOfDesignation[3] - 1;
      KindOfComunnication := CopyPStr(@r6.KindOfComunnication, 1);
      IndexOfVATRate := r6.IndexOfVATRate;
      IndexOfTariff := CalcWord(r6.IndexOfTariff) - 1;
      TariffCount := r6.TariffCount;
      PriceReductionCount := r6.PriceReductionCount;
      IndexOfPriceReduction := CalcWord(r6.IndexOfPriceReduction) - 1;
      BonusCount := r6.BonusCount;
      IndexOfBonus := CalcWord(r6.IndexOfBonus) - 1;
      FeeCount := r6.FeeCount;
      IndexOfFee := CalcWord(r6.IndexOfFee) - 1;
      BaggageTariffCount := r6.BaggageTariffCount;
      IndexOfBaggageTariff := CalcWord(r6.IndexOfBaggageTariff) - 1;
      BranchId := r6.BranchId;
      IndexOfLine := CalcWord(r6.IndexOfLine) - 1;
      Distance := CalcWord(r6.Distance) * 100;
      CityTariffCount := r6.CityTariffCount;
      IndexOfCityTariff := CalcWord(r6.IndexOfCityTariff) - 1;
      VATChangeBusStopIndex := r6.VATChangeBusStopIndex - 1;
      IndexOfFirstBusStopInLineRoute := r6.IndexOfFirstBusStopInLineRoute;
      EMCardEnable := (r6.State and $01) = 0;
      StatutoryRelief := (r6.State and $02) = 0;
      TradeConcessions := (r6.State and $04) = 0;
      DisccountReturnTicket := (r6.State and $08) > 0;
      DisccountGroupTicket := (r6.State and $10) > 0;
      CityCommunication := (r6.State and $20) > 0;
      InCountry := (r6.State and $40) = 0;
      Direction := (r6.State and $80) = 0;
      NetworkTickets := (r6.state_1 and $01) > 0;
      ZoneTickets := (r6.state_1 and $02) > 0;
      VATOrder := (r6.state_1 and $04) > 0;
      PrintArrivalTimeOnTicket := (r6.state_1 and $08) > 0;
      fTIA_State1 := r6.TIA_Status1;
      fTIA_State2 := r6.TIA_Status2;
      fTIA_State3 := r6.TIA_Status3;
      fTIA_State4 := r6.TIA_Status4;
      if aVer >= 7 then begin
        w := CalcWord(r6.ValidFromB);
        if (w > 0) and (w <> $FFFF) then ValidFrom := pchar(DateToStr(StrToDate(Date19880101) + w))
        else ValidFrom := '';
        w := CalcWord(r6.ValidToB);
        if (w > 0) and (w <> $FFFF) then ValidTo := pchar(DateToStr(StrToDate(Date19880101) + w))
        else ValidTo := '';
      end else begin
        w := CalcWord(r6.ValidFrom);
        if (w > 0) and (w <> $FFFF) then ValidFrom := pchar(DateToStr(StrToDate(Owner.CalendarBegin) + w))
        else ValidFrom := '';
        w := CalcWord(r6.ValidTo);
        if (w > 0) and (w <> $FFFF) then ValidTo := pchar(DateToStr(StrToDate(Owner.CalendarBegin) + w))
        else ValidTo := '';
      end;
    end;
  end;
end;

function TEmar105_Ride.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_Ride_v5);
  7, 8: Result := SizeOf(TEmar105_Ride_v6);
else Result := 0;
  end;
end;

procedure TEmar105_Ride.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r6: TEmar105_Ride_v6;
  s:  string;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r6, SizeOf(r6), 0);
      r6.Id := Id;
      r6.ID_8 := 8;
      r6.ID_9 := 9;
      r6.ID_11 := 11;
      r6.ID_12 := 12;
      r6.ID_13 := 13;
      r6.ID_14 := 14;
      r6.ID_15 := 15;
      r6.ID_26 := 26;
      r6.ID_27 := 27;
      r6.ID_28 := 28;
      r6.ID_30 := 30;
      r6.ID_35 := 35;

      r6.TIA_Status1 := $FF;
      r6.TIA_Status2 := $FF;
      r6.TIA_Status3 := $FF;
      r6.TIA_Status4 := $FF;

      r6.CompanyIndex := byte(CompanyIndex + 1);
      r6.Number := CalcWord(Number);
      if fsNumber <> '' then s := Format('%4s', [fsNumber])
      else s := '';
      if s <> '' then StrPLCopy(r6.sNumber, ansistring(s), 4, true, #0);
      if fVersion <> '' then r6.Version := ansichar(fVersion[1]);
      WriteValidFrom(r6.ValidFrom, Owner.CalendarBegin, ValidFrom);
      WriteValidTo(r6.ValidTo, Owner.CalendarBegin, ValidTo);
      r6.IndexOfCalendar := CalcWord(IndexOfCalendar + 1);
      r6.IndexOfRoute := CalcCardinal(IndexOfRoute + 1);
      r6.BusStopCount := byte(BusStopCount);
      r6.DepartureTime := CalcWord(word(DepartureTime));
      r6.TimeOfArrival := CalcWord(word(TimeOfArrival));
      r6.IndexOfFirstBusStop := CalcWord(IndexOfFirstBusStop + 1);
      r6.IndexOfLastBusStop := CalcWord(IndexOfLastBusStop + 1);
      if StandArrival <> '' then StrPLCopy(r6.StandArrival, ansistring(StandArrival), 3, True, #0);
      r6.IndexOfDesignation[0] := IndexOfDesignation[0] + 1;
      r6.IndexOfDesignation[1] := IndexOfDesignation[1] + 1;
      r6.IndexOfDesignation[2] := IndexOfDesignation[2] + 1;
      r6.IndexOfDesignation[3] := IndexOfDesignation[3] + 1;
      if fKindOfComunnication <> '' then r6.KindOfComunnication := ansichar(fKindOfComunnication[1]);
      r6.IndexOfVATRate := IndexOfVATRate;
      r6.IndexOfTariff := CalcWord(IndexOfTariff + 1);
      r6.TariffCount := TariffCount;
      r6.PriceReductionCount := PriceReductionCount;
      r6.IndexOfPriceReduction := CalcWord(word(IndexOfPriceReduction + 1));
      r6.BonusCount := BonusCount;
      r6.IndexOfBonus := CalcWord(IndexOfBonus + 1);
      r6.FeeCount := FeeCount;
      r6.IndexOfFee := CalcWord(IndexOfFee + 1);
      r6.BaggageTariffCount := BaggageTariffCount;
      r6.IndexOfBaggageTariff := CalcWord(IndexOfBaggageTariff + 1);
      r6.BranchId := BranchId;
      r6.IndexOfLine := CalcWord(IndexOfLine + 1);
      r6.Distance := CalcWord(Round(Distance / 100));
      r6.CityTariffCount := CityTariffCount;
      r6.IndexOfCityTariff := CalcWord(IndexOfCityTariff + 1);
      r6.VATChangeBusStopIndex := byte(VATChangeBusStopIndex + 1);
      r6.IndexOfFirstBusStopInLineRoute := byte(IndexOfFirstBusStopInLineRoute);
      StrPLCopy(r6.iNumber, ansistring(fiNumber), 4, True, #0);
      r6.TIA_Status1 := fTIA_State1;
      r6.TIA_Status2 := fTIA_State2;
      r6.TIA_Status3 := fTIA_State3;
      r6.TIA_Status4 := fTIA_State4;
      if not EMCardEnable then r6.State := r6.State or $01;
      if not StatutoryRelief then r6.State := r6.State or $02;
      if not TradeConcessions then r6.State := r6.State or $04;
      if DisccountReturnTicket then r6.State := r6.State or $08;
      if DisccountGroupTicket then r6.State := r6.State or $10;
      if CityCommunication then r6.State := r6.State or $20;
      if not InCountry then r6.State := r6.State or $40;
      if not Direction then r6.State := r6.State or $80;

      if NetworkTickets then r6.state_1 := r6.state_1 or $01;
      if ZoneTickets then r6.state_1 := r6.state_1 or $02;
      if VATOrder then r6.state_1 := r6.state_1 or $04;
      if PrintArrivalTimeOnTicket then r6.state_1 := r6.state_1 or $08;
      r6.XOR_Sum := EmarXORSum(r6.ID_8, SizeOf(r6) - 6);
      if aVer in [7, 8] then begin
        WriteValidFrom(r6.ValidFromB, Date19880101, ValidFrom);
        WriteValidTo(r6.ValidToB, Date19880101, ValidTo, 0);
        aStream.write(r6, SizeOf(r6));
      end
      else aStream.write(r6, SizeOf(TEmar105_Ride_v5));
    end;
  end;
end;

function TEmar105_RideList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Ride.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 11 - TEmar105_RideRoute '}

procedure TEmar105_RideRoute.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r3: TEmar105_RideRoute_v5;
  d1: word;
  ix: integer;
begin
  ix := Owner.Dir.IndexOf(Id);
  FillChar(r3, SizeOf(r3), $ff);
  case aVer of
  6: aStream.read(r3, SizeOf(TEmar105_RideRoute_v1));
  7, 8:
    if (ix >= 0)and(Owner.Dir.Items[ix].RecLength <= SizeOf(r3)) then
      aStream.read(r3, Owner.Dir.Items[ix].RecLength)
    else
      aStream.read(r3, SizeOf(r3));
  end;
  Id := r3.Id;
  IndexOfBusStop := CalcWord(r3.IndexOfBusStop) - 1;
  RideTime := CalcWord(r3.RideTime);
  StopTime := r3.StopTime;
  DepartureStandNumber := r3.DepartureStandNumber;

  IsFirstBusStopAfterBranch := (r3.State and $01) > 0;
  ReceiveSaleDiagram := (r3.State and $02) > 0;
  IsCountryBorder := (r3.State and $04) > 0;
  SkipBusStop := (r3.State and $08) > 0;
  ShowArrivalStand := (r3.State and $10) > 0;
  ShowDepartureStand := (r3.State and $20) > 0;
  IsConditional := (r3.State and $40) > 0;
  InBranch := (r3.State and $80) > 0;

  ShowOnInfoBoard := (r3.state2 and $01) > 0;
  EnableSaleToSkipedBusStop := (r3.state2 and $02) > 0;
  EndOfZone := (r3.state2 and $04) > 0;
  CurrentEndZone := (r3.state2 and $08) > 0;

  // if (r3.ArrivalStand[0]=#0) and (Owner.BusStopStandList.Count > 0) then begin
  // pStand := @r3.ArrivalStand[0];
  // IndexOfArrivalStand := CalcWord(pStand^.IndexOfStand) - 1;
  // end else
  ArrivalStand := CopyPStr(r3.ArrivalStand, 3, False);
  // if (r3.DepartureStand[0]=#0) and (Owner.BusStopStandList.Count > 0) then begin
  // pStand := @r3.DepartureStand[0];
  // IndexOfDepartureStand := CalcWord(pStand^.IndexOfStand) - 1;
  // end else
  DepartureStand := CopyPStr(r3.DepartureStand, 3, False);
  if IsFirstBusStopAfterBranch then begin
    d1 := CalcWord(r3.Distance);
    DistanceInShortcut := Hi(d1) * 100;
    Distance := Lo(d1) * 100;
    d1 := CalcWord(r3.FareDistance);
    FareDistanceInShortcut := Hi(d1) * 1000;
    FareDistance := Lo(d1) * 1000;
  end else begin
    Distance := CalcWord(r3.Distance) * 100;
    DistanceInShortcut := 0;
    FareDistance := CalcWord(r3.FareDistance) * 1000;
    FareDistanceInShortcut := 0;
  end;
  if aVer >= 7 then begin
    DepartureZone := CalcWord(r3.DepartureZone);
    ArrivalZone := CalcWord(r3.ArrivalZone);
    IndexOfBusStopInLine := r3.IndexOfBusStopInLine - 1;
  end;
  if (ix >= 0) and (Owner.Dir.Items[ix].Version >= 5) then begin
    if r3.ID_47 <> $FF then // nowa wersja rekordu DIR, stworzona na podstawie starej
    begin
      IndexOfArrivalStand := CalcWord(r3.IndexOfArrivalBusStand) - 1;
      IndexOfDepartureStand := CalcWord(r3.IndexOfDepartureBusStand) - 1;
    end; // inaczej zostaną -2
  end;
end;

function TEmar105_RideRoute.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_RideRoute_v1);
  7, 8: Result := SizeOf(TEmar105_RideRoute_v5);
else Result := 0;
  end;
end;

procedure TEmar105_RideRoute.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r3: TEmar105_RideRoute_v5;
  d1: word;
  ix: integer;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r3, SizeOf(r3), 0);
      r3.Id := Id;
      r3.ID_9 := 9;
      r3.IndexOfBusStop := CalcWord(IndexOfBusStop + 1);
      r3.RideTime := CalcWord(RideTime);
      r3.StopTime := StopTime;
      r3.DepartureStandNumber := DepartureStandNumber;
      if IsFirstBusStopAfterBranch or InBranch then begin
        d1 := word(Round(DistanceInShortcut / 100)) shl 8; // hi
        d1 := d1 or word(Round(Distance / 100));           // lo
        r3.Distance := CalcWord(d1);
        d1 := word(Round(FareDistanceInShortcut / 1000)) shl 8;
        d1 := d1 or word(Round(FareDistance / 1000));
        r3.FareDistance := CalcWord(d1);
      end else begin
        r3.Distance := CalcWord(Round(Distance / 100));
        r3.FareDistance := CalcWord(Round(FareDistance / 1000));
      end;
      if IsFirstBusStopAfterBranch then r3.State := r3.State or $01;
      if ReceiveSaleDiagram then r3.State := r3.State or $02;
      if IsCountryBorder then r3.State := r3.State or $04;
      if SkipBusStop then r3.State := r3.State or $08;
      if ShowArrivalStand then r3.State := r3.State or $10;
      if ShowDepartureStand then r3.State := r3.State or $20;
      if IsConditional then r3.State := r3.State or $40;
      if InBranch then r3.State := r3.State or $80;

      if ArrivalStand <> '' then StrPLCopy(r3.ArrivalStand, ansistring(ArrivalStand), 3, True)
      else FillChar(r3.ArrivalStand, 3, Ord(' '));

      if DepartureStand <> '' then StrPLCopy(r3.DepartureStand, ansistring(DepartureStand), 3, True)
      else FillChar(r3.DepartureStand, 3, Ord(' '));

      if ShowOnInfoBoard then r3.state2 := r3.state2 or $01;
      if EnableSaleToSkipedBusStop then r3.state2 := r3.state2 or $02;
      if EndOfZone then r3.state2 := r3.state2 or $04;
      if CurrentEndZone then r3.state2 := r3.state2 or $08;
      if aVer >= 7 then begin
        r3.DepartureZone := CalcWord(DepartureZone);
        r3.ArrivalZone := CalcWord(ArrivalZone);
        r3.IndexOfBusStopInLine := IndexOfBusStopInLine + 1;
        ix := Owner.Dir.IndexOf(Id);
        if (ix >= 0) and (Owner.Dir.Items[ix].Version >= 5) then begin
          if (Owner.Dir[ix].RecLength>=32) and ((IndexOfArrivalStand > - 2) or (IndexOfDepartureStand > - 2)) then begin
            r3.ID_47 := 47;
            if IndexOfArrivalStand > - 2 then r3.IndexOfArrivalBusStand := CalcWord(word(IndexOfArrivalStand + 1))
            else r3.IndexOfArrivalBusStand := 0;
            if IndexOfDepartureStand > - 2 then r3.IndexOfDepartureBusStand := CalcWord(word(IndexOfDepartureStand + 1))
            else r3.IndexOfDepartureBusStand := 0;
          end else begin
            r3.ID_47 := $FF;
            r3.IndexOfArrivalBusStand := $FFFF;
            r3.IndexOfDepartureBusStand := $FFFF;
          end;
          aStream.write(r3, Owner.Dir[ix].RecLength);
        end else
          aStream.write(r3, SizeOf(TEmar105_RideRoute_v5));
      end
      else aStream.write(r3, SizeOf(TEmar105_RideRoute_v1));
    end;
  end;
end;

function TEmar105_RideRouteList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideRoute.Create(Owner, Id);
end;

function TEmar105_RideRouteList._New;
begin
  Result := TEmar105_RideRouteList.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 12 - TEmar105_RideTariff '}

procedure TEmar105_RideTariff.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      IndexOfTariff := CalcWord(r1.IndexOfTariff) - 1;
      IndexOfFirstBusStopInRoute := r1.IndexOfFirstBusStopInRoute - 1;
      IndexOfLastBusStopInRoute := r1.IndexOfLastBusStopInRoute - 1;
      IndexOfCalendar := integer(CalcWord(r1.IndexOfCalendar) - 1);
      PriceTable := r1.PriceTable;
      FirstPriceIndex := integer(CalcCardinal(r1.FirstPriceIndex) - 1);
      TariffType := r1.TariffType;
    end;
  end;
end;

function TEmar105_RideTariff.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_RideTariff_v1);
end;

procedure TEmar105_RideTariff.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1.Id, SizeOf(r1), 0);
      r1.Id := Id;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r1.ID_16 := 16;
      r1.IndexOfTariff := CalcWord(word(IndexOfTariff + 1));
      r1.IndexOfFirstBusStopInRoute := byte(IndexOfFirstBusStopInRoute + 1);
      r1.IndexOfLastBusStopInRoute := byte(IndexOfLastBusStopInRoute + 1);
      r1.ID_14 := 14;
      r1.IndexOfCalendar := CalcWord(word(IndexOfCalendar + 1));
      r1.PriceTable := byte(PriceTable);
      r1.FirstPriceIndex := CalcCardinal(cardinal(FirstPriceIndex + 1));
      r1.TariffType := byte(TariffType);
      aStream.write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_RideTariffList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideTariff.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 13 - TEmar105_RideReduction '}

procedure TEmar105_RideReduction.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideReduction_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      lp := r1.lp;
      IndexOfReduction := r1.ReductionNumber - 1;
      IndexOfFirstBusStop := r1.IndexOfFirstBusStop - 1;
      IndexOfLastBusStop := r1.IndexOfLastBusStop - 1;
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      BonusCount := r1.BonusCount;
      IndexOfBonus := CalcWord(r1.IndexOfBonus) - 1;
      ReductionBinaryCode := r1.ReductionBinaryCode;
      ReductionBusStopNumber := r1.ReductionBusStopNumber - 1;
      SelectByEMCard := (r1.State and $01) > 0;
    end;
  end;
end;

function TEmar105_RideReduction.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_RideReduction_v1);
end;

procedure TEmar105_RideReduction.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideReduction_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1.Id, SizeOf(r1), 0);
      r1.Id := Id;
      r1.lp := byte(lp);
      r1.ID_23 := 23;
      r1.ReductionNumber := byte(IndexOfReduction + 1);
      r1.IndexOfFirstBusStop := byte(IndexOfFirstBusStop) + 1;
      r1.IndexOfLastBusStop := byte(IndexOfLastBusStop) + 1;
      r1.ID_14 := 14;
      r1.IndexOfCalendar := CalcWord(word(IndexOfCalendar + 1));
      r1.BonusCount := byte(BonusCount);
      if IndexOfBonus < 0 then r1.ID_27 := 0
      else r1.ID_27 := 27;
      r1.IndexOfBonus := CalcWord(word(IndexOfBonus + 1));
      r1.ReductionBinaryCode := byte(ReductionBinaryCode);
      r1.ReductionBusStopNumber := byte(ReductionBusStopNumber + 1);
      if SelectByEMCard then r1.State := r1.State or $01;
      aStream.write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_RideReductionList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideReduction.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 14 - TEmar105_Calendar '}

procedure TEmar105_Calendar.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Calendar_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, SizeOf(r0));
      Id := r0.Id;
      // fMonth := GetFlashCalendar(CalcCardinal(r0.Month));
      fMonth := r0.Month; // UWAGA! Little Endian !!!
    end;
  end;
end;

function TEmar105_Calendar.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_Calendar_v0);
end;

procedure TEmar105_Calendar.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Calendar_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      // r0.Month := CalcCardinal(SetFlashCalendar(fMonth));
      r0.Month := fMonth; // UWAGA! Little Endian !!!
      aStream.write(r0, SizeOf(r0));
    end;
  end;
end;

function TEmar105_CalendarList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Calendar.Create(Owner, Id);
end;

function TEmar105_CalendarList._New: IEmar_CalendarList;
begin
  Result := TEmar105_CalendarList.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 15 - TEmar105_RideDesignation '}

procedure TEmar105_RideDesignation.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_RideDesignation_v0;
  r1: TEmar105_RideDesignation_v1;
begin
  case aVer of
  6: begin
      aStream.read(r0, SizeOf(r0));
      Id := r0.Id;
      Tag := CopyPStr(r0.Tag, 3);
      Description := CopyPStr(r0.Description, SizeOf(r0.Description) - 1);
      IndexOfCalendar := CalcWord(r0.IndexOfCalendar) - 1;
      Kind := TEmarDesignationKind(r0.Kind);
    end;
  7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      Tag := CopyPStr(r1.Tag, 3);
      Description := CopyPStr(r1.Description, SizeOf(r1.Description) - 1);
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      Kind := TEmarDesignationKind(r1.Kind);
    end;
  end;
end;

function TEmar105_RideDesignation.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_RideDesignation_v0);
  7, 8: Result := SizeOf(TEmar105_RideDesignation_v1);
else Result := 0;
  end;
end;

procedure TEmar105_RideDesignation.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_RideDesignation_v0;
  r1: TEmar105_RideDesignation_v1;
  ixCal: integer;
begin
  if Kind = edkNone then ixCal := 0
  else ixCal := IndexOfCalendar + 1;

  case aVer of
  6: begin
      FillChar(r0, SizeOf(r0), 0);
      r0.Id := Id;
      StrPLCopy(r0.Tag, ansistring(Tag), 3, true, #0);
      StrPLCopy(r0.Description, ansistring(Description), SizeOf(r0.Description) - 1, true, #0);
      r0.ID_14 := 14;
      r0.IndexOfCalendar := CalcWord(word(ixCal));
      r0.Kind := byte(Kind);
      aStream.write(r0, SizeOf(r0));
    end;
  7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      StrPLCopy(r1.Tag, ansistring(Tag), 3, true, #0);
      StrPLCopy(r1.Description, ansistring(Description), SizeOf(r1.Description) - 1, true, #0);
      r1.ID_14 := 14;
      r1.IndexOfCalendar := CalcWord(word(ixCal));
      r1.Kind := byte(Kind);
      aStream.write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_RideDesignationList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideDesignation.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 16 - TEmar105_Tariff '}

procedure TEmar105_Tariff.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r2:      TEmar105_Tariff_v2;
  r, m, d: word;
  dValidFrom: TDateTime;
begin
  case aVer of
  6, 7, 8: begin
      if aVer = 6 then begin
        aStream.read(r2, SizeOf(TEmar105_Tariff_v1));
        r2.FeeCalculateMethod := 0;
      end
      else aStream.read(r2, SizeOf(TEmar105_Tariff_v2));
      Id := r2.Id;
      IndexOfCompany := r2.IndexOfCompany - 1;
      Number := r2.Number;
      Table := r2.Table;
      name := CopyPStr(r2.name, 10);
      Kind := r2.Kind;
      PriceCount := r2.PriceCount;
      IndexOfPrice := CalcWord(r2.IndexOfPrice) - 1;
      IndexOfVAT := r2.IndexOfVAT;
      IndexOfCurrency := r2.IndexOfCurrency - 1;
      IndexOfCalendar := CalcWord(r2.IndexOfCalendar) - 1;
      TableName := CopyPStr(r2.TableName, 10);
      r := CalcWord(r2.ValidFromB.wYear);
      m := r2.ValidFromB.bMonth;
      d := r2.ValidFromB.bDay;
      if not TryEncodeDate(r, m, d, dValidFrom) then
        dValidFrom := 0;
      ValidFrom := pchar(DateToStr(dValidFrom));
      IndexOfForeignVAT := r2.IndexOfForeignVAT;
      FeeCalculateMethod := TEmarFeeCalculateMethod(r2.FeeCalculateMethod);
    end;
  end;
end;

function TEmar105_Tariff.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_Tariff_v1);
  7, 8: Result := SizeOf(TEmar105_Tariff_v2);
else Result := 0;
  end;
end;

procedure TEmar105_Tariff.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r2:      TEmar105_Tariff_v2;
  r, m, d: word;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r2, SizeOf(r2), 0);
      r2.Id := Id;
      WriteValidFrom(r2.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r2.ID_8 := 8;
      r2.IndexOfCompany := byte(IndexOfCompany + 1);
      r2.Number := byte(Number);
      r2.Table := byte(Table);
      if name <> '' then StrPLCopy(r2.name, ansistring(name), 10, true, #0);
      r2.Kind := byte(Kind);
      r2.PriceCount := byte(PriceCount);
      if r2.Kind = 13 then r2.ID_17_36 := 36
      else r2.ID_17_36 := 17;
      r2.IndexOfPrice := CalcWord(word(IndexOfPrice + 1));
      r2.IndexOfVAT := byte(IndexOfVAT);
      r2.ID_21 := 21;
      r2.IndexOfCurrency := IndexOfCurrency + 1;
      r2.ID_14 := 14;
      r2.IndexOfCalendar := CalcWord(word(IndexOfCalendar + 1));
      if TableName <> '' then StrPLCopy(r2.TableName, ansistring(TableName), 10, true, #0);
      DecodeDate(StrToDate(ValidFrom), r, m, d);
      r2.ValidFromB.wYear := CalcWord(r);
      r2.ValidFromB.bMonth := byte(m);
      r2.ValidFromB.bDay := byte(d);
      r2.IndexOfForeignVAT := byte(IndexOfForeignVAT);
      r2.FeeCalculateMethod := byte(FeeCalculateMethod);
      if aVer = 6 then aStream.write(r2, SizeOf(TEmar105_Tariff_v1))
      else aStream.write(r2, SizeOf(TEmar105_Tariff_v2));
    end;
  end;
end;

function TEmar105_TariffList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Tariff.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 17 - TEmar105_Price '}

procedure TEmar105_Price.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Price_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, SizeOf(r0));
      Id := r0.Id;
      TariffNumber := r0.TariffNumber;
      PriceNumber := r0.PriceNumber;
      Zone := integer(CalcCardinal(r0.Zone));
      Price := integer(CalcCardinal(r0.Price));
      Increase := r0.Increase > 0;
    end;
  end;
end;

function TEmar105_Price.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_Price_v0);
end;

procedure TEmar105_Price.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Price_v0;
  p:  pByte;
  i:  integer;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r0, SizeOf(r0), $FF);
      r0.Id := Id;
      r0.TariffNumber := byte(TariffNumber);
      r0.PriceNumber := byte(PriceNumber);
      r0.Zone := CalcCardinal(cardinal(Zone));
      r0.Price := CalcCardinal(cardinal(Price));
      if Increase then r0.Increase := 1
      else r0.Increase := 0;
      r0.XOR_Sum := 0;
      p := @r0.TariffNumber;
      for i := 1 to 11 do begin
        r0.XOR_Sum := r0.XOR_Sum xor lo(i * p^);
        Inc(p);
      end;
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_PriceList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Price.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 21 - TEmar105_CurrencyExchange '}

procedure TEmar105_CurrencyExchange.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_CurrencyExchange_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      aStream.read(r1, RecordLength(aVer));
      Id := r1.Id;
      lp := r1.lp;
      Country := CopyPStr(r1.Country, SizeOf(r1.Country) - 1);
      Currency := CopyPStr(r1.Currency, SizeOf(r1.Currency) - 1);
      CountOfUnits := r1.CountOfUnits;
      ExchangeRateOfPLN := CalcCardinal(r1.ExchangeRateOfPLN);
      ExchangeRate := CalcCardinal(r1.ExchangeRate);
      ExchangeRateOfCurrency := CalcCardinal(r1.ExchangeRateOfCurrency);
    end;
  end;

end;

function TEmar105_CurrencyExchange.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_CurrencyExchange_v0);
  7, 8: Result := SizeOf(TEmar105_CurrencyExchange_v1);
else Result := 0;
  end;
end;

procedure TEmar105_CurrencyExchange.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_CurrencyExchange_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.lp := lp;
      StrPLCopy(r1.Country, ansistring(Country), SizeOf(r1.Country) - 1);
      StrPLCopy(r1.Currency, ansistring(Currency), SizeOf(r1.Currency) - 1);
      r1.CountOfUnits := CountOfUnits;
      r1.ExchangeRateOfPLN := CalcCardinal(ExchangeRateOfPLN);
      r1.ExchangeRate := CalcCardinal(ExchangeRate);
      r1.ExchangeRateOfCurrency := CalcCardinal(ExchangeRateOfCurrency);
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_CurrencyExchangeList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_CurrencyExchange.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 22 - TEmar105_PaymentType '}

procedure TEmar105_PaymentType.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_PaymentType_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, SizeOf(r0));
      Id := r0.Id;
      Nr := r0.Nr;
      PaymentType := CopyPStr(r0.PaymentType, SizeOf(r0.PaymentType) - 1);
    end;
  end;
end;

function TEmar105_PaymentType.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_PaymentType_v0);
end;

procedure TEmar105_PaymentType.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_PaymentType_v0;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r0, SizeOf(r0), 0);
      r0.Id := Id;
      r0.Nr := Nr;
      StrPLCopy(r0.PaymentType, ansistring(PaymentType), SizeOf(r0.PaymentType) - 1, true, #0);
      aStream.write(r0, SizeOf(r0));
    end;
  end;
end;

function TEmar105_PaymentTypeList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_PaymentType.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 23 - TEmar105_FarePriceReduction '}

procedure TEmar105_FarePriceReduction.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_FarePriceReduction_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      name := CopyPStr(r1.name, SizeOf(r1.name) - 1, False);
      ReductionAmount := r1.ReductionAmount;
      ReductionCode := r1.ReductionCode;
      Total := r1.Total;
      ReductionType := r1.ReductionType;
      ReductionPayer := r1.ReductionPayer;
      ReductionRoundMethod := r1.ReductionRoundMethod;
      TicketType := r1.TicketType;
      ReductionGroup := r1.ReductionGroup;
      ReductionNumber := r1.ReductionNumber;
      NumberInTicketRegister := r1.NumberInTicketRegister;
      CompanyGovCode := CopyPStr(r1.CompanyGovCode, SizeOf(CompanyGovCode) - 1);
      NrStawkaPTU := r1.NrStawkaPTU;
      ReductionCompanyINumber := CalcWord(r1.CompanyDefIndex);
      IgnoreForGov := (r1.State and $80) > 0;
      NoSeat := (r1.State and $40) > 0;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      ValidTo := pchar(ReadValidTo(r1.ValidTo, Owner.CalendarBegin, ''));
    end;
  end;
end;

function TEmar105_FarePriceReduction.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_FarePriceReduction_v1);
end;

procedure TEmar105_FarePriceReduction.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_FarePriceReduction_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      StrPLCopy(r1.name, ansistring(name), SizeOf(r1.name) - 1, True, ' ');
      r1.ReductionAmount := ReductionAmount;
      r1.ReductionCode := ReductionCode;
      r1.Total := Total;
      r1.ReductionType := byte(ReductionType);
      r1.ReductionPayer := byte(ReductionPayer);
      r1.ReductionRoundMethod := byte(ReductionRoundMethod);
      r1.TicketType := TicketType;
      r1.ReductionGroup := ReductionGroup;
      r1.ReductionNumber := ReductionNumber;
      r1.NumberInTicketRegister := NumberInTicketRegister;
      StrPLCopy(r1.CompanyGovCode, ansistring(CompanyGovCode), SizeOf(r1.CompanyGovCode) - 1, True, #0);
      r1.NrStawkaPTU := NrStawkaPTU;
      r1.CompanyDefIndex := CalcWord(ReductionCompanyINumber);
      if IgnoreForGov then r1.State := r1.State or $80;
      if NoSeat then r1.State := r1.State or $40;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      if ValidTo <> '' then WriteValidTo(r1.ValidTo, Owner.CalendarBegin, ValidTo)
      else r1.ValidTo := $FFFF;
      aStream.write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_FarePriceReductionList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_FarePriceReduction.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 24 - TEmar105_Task '}

procedure TEmar105_Task.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Task_v0;
begin
  aStream.read(r0, SizeOf(r0));
  Id := r0.Id;
  DateBegin := pchar(ReadValidFrom(r0.DateBegin, Owner.CalendarBegin));
  DateEnd := pchar(ReadValidFrom(r0.DateEnd, Owner.CalendarBegin));
  PositionCount := r0.PositionCount;
  IndexOfPosition := r0.IndexOfPosition - 1;
  Number := CopyPStr(r0.Number, SizeOf(r0.Number) - 1);
end;

function TEmar105_Task.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_Task_v0);
end;

procedure TEmar105_Task.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Task_v0;
begin
  FillChar(r0, SizeOf(r0), 0);
  r0.Id := Id;
  WriteValidFrom(r0.DateBegin, Owner.CalendarBegin, DateBegin);
  WriteValidTo(r0.DateEnd, Owner.CalendarBegin, DateEnd);
  r0.PositionCount := PositionCount;
  r0.ID_25 := 25;
  r0.IndexOfPosition := IndexOfPosition + 1;
  StrPLCopy(r0.Number, ansistring(Number), SizeOf(r0.Number) - 1, true, #0);
  aStream.write(r0, SizeOf(r0));
end;

function TEmar105_TaskList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Task.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 25 - TEmar105_TaskPosition '}

procedure TEmar105_TaskPosition.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_TaskPosition_v0;
begin
  aStream.read(r0, SizeOf(r0));
  Id := r0.Id;
  PositionType := r0.PositionType;
  DateTaken := pchar(ReadValidFrom(r0.DateTaken, Owner.CalendarBegin));
  TimeBegin := CalcWord(r0.TimeBegin);
  TimeEnd := CalcWord(r0.TimeEnd);
  RideNumber := CalcWord(r0.RideNumber);
  RidePage := CalcWord(r0.RidePage);
  RideOffset := CalcWord(r0.RideOffset);
  Description := CopyPStr(r0.Description, SizeOf(r0.Description) - 1);
  Relation := CopyPStr(r0.Relation, SizeOf(r0.Relation) - 1);
  Number := r0.Number;
end;

function TEmar105_TaskPosition.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_TaskPosition_v0);
end;

procedure TEmar105_TaskPosition.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_TaskPosition_v0;
begin
  FillChar(r0, SizeOf(r0), 0);
  r0.Id := Id;
  r0.PositionType := PositionType;
  WriteValidFrom(r0.DateTaken, Owner.CalendarBegin, DateTaken);
  r0.TimeBegin := CalcWord(TimeBegin);
  r0.TimeEnd := CalcWord(TimeEnd);
  r0.RideNumber := CalcWord(RideNumber);
  r0.RidePage := CalcWord(RidePage);
  r0.RideOffset := CalcWord(RideOffset);
  StrPLCopy(r0.Description, ansistring(Description), SizeOf(r0.Description) - 1, true, #0);
  StrPLCopy(r0.Relation, ansistring(Relation), SizeOf(r0.Relation) - 1, true, #0);
  r0.Number := Number;
  aStream.write(r0, SizeOf(r0));
end;

function TEmar105_TaskPositionList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_TaskPosition.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 26 - TEmar105_Line '}

procedure TEmar105_Line.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  rec:   TEmar105_Line_v2;
  eFile: TEmar105_File;
begin
  FillChar(rec, SizeOf(rec), $FF);
  aStream.Read(rec, RecordLength(aVer));
  Id := rec.Id;
  fIndexOfCompany := rec.IndexOfCompany - 1;
  LineNumberIndex := CalcCardinal(rec.LineNumber);
  eFile := TEmar105_File(Owner);
  if (string(eFile.Consts.ProgramMaker) = 'I2.0') and (LineNumberIndex <= Owner.LineNumberList.Count) then begin
    LineNumberIndex := LineNumberIndex - 1;
    if LineNumberIndex >= 0 then fLineNumber := Owner.LineNumberList[LineNumberIndex].LineNumber
    else fLineNumber := '??????';
  end
  else fLineNumber := UIntToStr(LineNumberIndex);
  fIndexOfFirstBusStop := CalcWord(rec.IndexOfFirstBusStop) - 1;
  fIndexOfLastBusStop := CalcWord(rec.IndexOfLastBusStop) - 1;
  fLineVariant := rec.LineVariant;
  fLineType := CopyPStr(@rec.LineType, 1);
  fIndexOfFirstRoutePoint := integer(CalcCardinal(rec.IndexOfFirstRoutePoint)) - 1;
  fBusStopCount := rec.BusStopCount;
  if aVer >= 7 then begin
    fValidFrom := pchar(ReadValidFrom(rec.ValidFromB, Date19880101));
    fValidTo := pchar(ReadValidTo(rec.ValidToB, Date19880101, ''));
    if aVer >= 8 then begin
      if rec.ServiceType[0] = #$ff then fServiceType := ''
      else fServiceType := CopyPStr(@rec.ServiceType, 2);
      if rec.GOVLineNumber[0] = #$ff then fGOVLineNumber := ''
      else fGOVLineNumber := CopyPStr(rec.GOVLineNumber, 20);
      fLastLinkedBusStopNumber := rec.LastLinkedBusStopNumber;
      if rec.LinkedServiceType[0] = #$ff then fLinkedServiceType := ''
      else fLinkedServiceType := CopyPStr(@rec.LinkedServiceType, 2);
      if rec.LinkedGOVLineNumber[0] = #$ff then fLinkedGOVLineNumber := ''
      else fLinkedGOVLineNumber := CopyPStr(rec.LinkedGOVLineNumber, 20);
    end;
  end else begin
    fValidFrom := pchar(ReadValidFrom(rec.ValidFrom, Owner.CalendarBegin));
    fValidTo := pchar(ReadValidTo(rec.ValidTo, Owner.CalendarBegin, ''));
  end;
end;

// !!! USE THIS FUNCTION FOR DATA READING ONLY !!!
function TEmar105_Line.RecordLength(aVer: byte): integer;
begin // stary program my błąd - od wersji zbioru 6 zapisywany rekordy długości wersji 8 (77 byte)
  // case aVer of
  // 6:
  // Result := SizeOf(TEmar105_Line_v0);
  // 7:
  // Result := SizeOf(TEmar105_Line_v1);
  // 8:
  // Result := SizeOf(TEmar105_Line_v2);
  // else
  // Result := 0;
  // end;
  Result := Owner.Dir.RecordLengthOf(Id);
  // AT: odczytujemy w długości rekordu która jest zapisana w Dir, a nie zgodnie z wersją
  if Result = 0 then
    case aVer of
    6: Result := SizeOf(TEmar105_Line_v0);
    7: Result := SizeOf(TEmar105_Line_v1);
    8: Result := SizeOf(TEmar105_Line_v2);
    end;
end;

procedure TEmar105_Line.SaveToBuffer(aStream: TStream; aVer: byte);
var
  iRecordLength: Integer;
  rec:           TEmar105_Line_v2;
  eFile:         TEmar105_File;
begin
  FillChar(rec, SizeOf(rec), $FF);
  rec.Id := Id;
  rec.ID_8 := 8;
  rec.ID_9 := 9;
  rec.ID_37 := 37;
  rec.IndexOfCompany := IndexOfCompany + 1;
  eFile := TEmar105_File(Owner);
  if string(eFile.Consts.ProgramMaker) = 'I2.0' then rec.LineNumber := CalcCardinal(LineNumberIndex + 1)
  else rec.LineNumber := CalcCardinal(StrToIntDef(LineNumber, 0));
  rec.IndexOfFirstBusStop := CalcWord(IndexOfFirstBusStop + 1);
  rec.IndexOfLastBusStop := CalcWord(IndexOfLastBusStop + 1);
  rec.LineVariant := fLineVariant;
  WriteValidFrom(rec.ValidFrom, Owner.CalendarBegin, ValidFrom);
  WriteValidTo(rec.ValidTo, Owner.CalendarBegin, ValidTo);
  if fLineType <> '' then rec.LineType := ansichar(fLineType[1])
  else if aVer >= 8 then rec.LineType := '1'
  else rec.LineType := 'Z';
  rec.IndexOfFirstRoutePoint := CalcCardinal(IndexOfFirstRoutePoint + 1);
  rec.BusStopCount := BusStopCount;
  if aVer >= 7 then begin
    WriteValidFrom(rec.ValidFromB, Date19880101, ValidFrom);
    WriteValidTo(rec.ValidToB, Date19880101, ValidTo, 0);
    if aVer >= 8 then begin
      if ServiceType <> '' then StrPLCopy(rec.ServiceType, ansistring(ServiceType), SizeOf(rec.ServiceType) - 1)
      else FillChar(rec.ServiceType, SizeOf(rec.ServiceType), 0);
      if GOVLineNumber <> '' then
          StrPLCopy(rec.GOVLineNumber, ansistring(GOVLineNumber), SizeOf(rec.GOVLineNumber) - 1, true, #0)
      else FillChar(rec.GOVLineNumber, SizeOf(rec.GOVLineNumber), 0);
      if LastLinkedBusStopNumber > 0 then rec.LastLinkedBusStopNumber := LastLinkedBusStopNumber;
      if LinkedServiceType <> '' then
          StrPLCopy(rec.LinkedServiceType, ansistring(LinkedServiceType), SizeOf(rec.LinkedServiceType) - 1)
      else FillChar(rec.LinkedServiceType, SizeOf(rec.LinkedServiceType), 0);
      if LinkedGOVLineNumber <> '' then
          StrPLCopy(rec.LinkedGOVLineNumber, ansistring(LinkedGOVLineNumber), SizeOf(rec.LinkedGOVLineNumber) -
          1, true, #0)
      else FillChar(rec.LinkedGOVLineNumber, SizeOf(rec.LinkedGOVLineNumber), 0);
    end;
  end;

  case aVer of
  6: iRecordLength := SizeOf(TEmar105_Line_v0);
  7: iRecordLength := SizeOf(TEmar105_Line_v1);
  8: iRecordLength := SizeOf(TEmar105_Line_v2);
else iRecordLength := 0;
  end;
  aStream.Write(rec, iRecordLength);
  // aStream.Write(rec, RecordLength(aVer));
end;

function TEmar105_LineList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Line.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 27 - TEmar105_RideBonus '}

procedure TEmar105_RideBonus.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideBonus_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      IndexOfTariff := CalcWord(r1.IndexOfTariff) - 1;
      IndexOfFirstBusStopInRoute := r1.IndexOfFirstBusStopInRoute - 1;
      IndexOfLastBusStopInRoute := r1.IndexOfLastBusStopInRoute - 1;
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      PriceTable := r1.PriceTable;
      FirstPriceIndex := integer(CalcCardinal(r1.FirstPriceIndex)) - 1;
      TariffType := r1.TariffType;
    end;
  end;
end;

function TEmar105_RideBonus.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_RideBonus_v1);
end;

procedure TEmar105_RideBonus.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideBonus_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.ID_14 := 14;
      r1.ID_16 := 16;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r1.IndexOfTariff := CalcWord(IndexOfTariff + 1);
      r1.IndexOfFirstBusStopInRoute := IndexOfFirstBusStopInRoute + 1;
      r1.IndexOfLastBusStopInRoute := IndexOfLastBusStopInRoute + 1;
      r1.IndexOfCalendar := CalcWord(IndexOfCalendar + 1);
      r1.PriceTable := PriceTable;
      r1.FirstPriceIndex := CalcCardinal(FirstPriceIndex + 1);
      r1.TariffType := TariffType;
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_RideBonusList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideBonus.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 28 - TEmar105_RideHandlingFee '}

procedure TEmar105_RideHandlingFee.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideHandlingFee_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      IndexOfTariff := CalcWord(r1.IndexOfTariff) - 1;
      IndexOfFirstBusStopInRoute := r1.IndexOfFirstBusStopInRoute - 1;
      IndexOfLastBusStopInRoute := r1.IndexOfLastBusStopInRoute - 1;
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      PriceTable := r1.PriceTable;
      FirstPriceIndex := integer(CalcCardinal(r1.FirstPriceIndex)) - 1;
      TariffType := r1.TariffType;
    end;
  end;
end;

function TEmar105_RideHandlingFee.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_RideHandlingFee_v1);
end;

procedure TEmar105_RideHandlingFee.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RideHandlingFee_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.ID_14 := 14;
      r1.ID_16 := 16;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r1.IndexOfTariff := CalcWord(IndexOfTariff + 1);
      r1.IndexOfFirstBusStopInRoute := IndexOfFirstBusStopInRoute + 1;
      r1.IndexOfLastBusStopInRoute := IndexOfLastBusStopInRoute + 1;
      r1.IndexOfCalendar := CalcWord(IndexOfCalendar + 1);
      r1.PriceTable := PriceTable;
      r1.FirstPriceIndex := CalcCardinal(FirstPriceIndex + 1);
      r1.TariffType := TariffType;
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_RideHandlingFeeList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RideHandlingFee.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 29 - TEmar105_AdditionalFee '}

procedure TEmar105_AdditionalFee.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_AdditionalFee_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, RecordLength(aVer));
      Id := r1.Id;
      LpBil := r1.LpBil;
      name := CopyPStr(r1.name, SizeOf(r1.name) - 1, False);
      PTU := r1.PTU;
      Price := CalcCardinal(r1.Price);
      StampDuty := CalcCardinal(r1.StampDuty);
      Group := r1.Group;
      GroupName := CopyPStr(r1.GroupName, SizeOf(r1.GroupName) - 1);
      ValidFrom := pchar(EmarDateToString(r1.ValidFromB));
      ValidTo := pchar(EmarDateToString(r1.ValidToB));
    end;
  end;
end;

function TEmar105_AdditionalFee.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_AdditionalFee_v1);
end;

procedure TEmar105_AdditionalFee.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_AdditionalFee_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      r1.LpBil := LpBil;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      StrPLCopy(r1.name, ansistring(name), SizeOf(r1.name) - 1);
      r1.PTU := PTU;
      r1.LRC := EmarLRCSum(r1.name, SizeOf(r1.name) + 1);
      r1.Price := CalcCardinal(Price);
      r1.StampDuty := CalcCardinal(StampDuty);
      r1.Group := Group;
      StrPLCopy(r1.GroupName, ansistring(GroupName), SizeOf(r1.GroupName) - 1);
      DateToEmarDate(r1.ValidFromB, ValidFrom);
      WriteValidTo(r1.ValidTo, Owner.CalendarBegin, ValidTo);
      DateToEmarDate(r1.ValidToB, ValidTo, 0);
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_AdditionalFeeList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_AdditionalFee.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 30 - TEmar105_LuggageTariff '}

procedure TEmar105_LuggageTariff.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_LuggageTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      IndexOfTariff := CalcWord(r1.IndexOfTariff) - 1;
      IndexOfFirstBusStopInRoute := r1.IndexOfFirstBusStopInRoute - 1;
      IndexOfLastBusStopInRoute := r1.IndexOfLastBusStopInRoute - 1;
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      PriceTable := r1.PriceTable;
      FirstPriceIndex := integer(CalcCardinal(r1.FirstPriceIndex)) - 1;
      TariffType := r1.TariffType;
    end;
  end;
end;

function TEmar105_LuggageTariff.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_LuggageTariff_v1);
end;

procedure TEmar105_LuggageTariff.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_LuggageTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.ID_14 := 14;
      r1.ID_16 := 16;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r1.IndexOfTariff := CalcWord(IndexOfTariff + 1);
      r1.IndexOfFirstBusStopInRoute := IndexOfFirstBusStopInRoute + 1;
      r1.IndexOfLastBusStopInRoute := IndexOfLastBusStopInRoute + 1;
      r1.IndexOfCalendar := CalcWord(IndexOfCalendar + 1);
      r1.PriceTable := PriceTable;
      r1.FirstPriceIndex := CalcCardinal(cardinal(FirstPriceIndex + 1));
      r1.TariffType := TariffType;
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_LuggageTariffList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_LuggageTariff.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 31 - TEmar105_ReferenceRide '}

procedure TEmar105_ReferenceRide.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ReferenceRide_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      RideNumber := CalcWord(r0.RideNumber);
      Departure := CalcWord(r0.Departure);
      PageNumber := CalcWord(r0.PageNumber);
      AdrressesOfBeginningRecord := CalcWord(r0.AdrressesOfBeginningRecord);
    end;
  end;
end;

function TEmar105_ReferenceRide.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_ReferenceRide_v0);
end;

procedure TEmar105_ReferenceRide.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ReferenceRide_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.RideNumber := CalcWord(RideNumber);
      r0.Departure := CalcWord(Departure);
      r0.PageNumber := CalcWord(PageNumber);
      r0.AdrressesOfBeginningRecord := CalcWord(AdrressesOfBeginningRecord);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ReferenceRideList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ReferenceRide.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 32 - TEmar105_AcceptedTicketOwner '}

procedure TEmar105_AcceptedTicketOwner.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_AcceptedTicketOwner_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, RecordLength(aVer));
      Id := r1.Id;
      CompanyNumber := CalcWord(r1.CompanyNumber);
      AllowedPasnersTravelWithTicketsNetCompany := (r1.State and $01) > 0;
    end;
  end;
end;

function TEmar105_AcceptedTicketOwner.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_AcceptedTicketOwner_v1);
end;

procedure TEmar105_AcceptedTicketOwner.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_AcceptedTicketOwner_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      r1.CompanyNumber := CalcWord(CompanyNumber);
      if AllowedPasnersTravelWithTicketsNetCompany then r1.State := r1.State or $01;
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_AcceptedTicketOwnerList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_AcceptedTicketOwner.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 33 - TEmar105_AcceptedTradeReliefCardOwner '}

procedure TEmar105_AcceptedTradeReliefCardOwner.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_AcceptedTradeReliefCardOwner_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      CompanyNumber := CalcWord(r0.CompanyNumber);
    end;
  end;
end;

function TEmar105_AcceptedTradeReliefCardOwner.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_AcceptedTradeReliefCardOwner_v0);
end;

procedure TEmar105_AcceptedTradeReliefCardOwner.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_AcceptedTradeReliefCardOwner_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.CompanyNumber := CalcWord(CompanyNumber);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_AcceptedTradeReliefCardOwnerList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_AcceptedTradeReliefCardOwner.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 34 - TEmar105_ProprietaryMIFAREcard '}

procedure TEmar105_ProprietaryMIFAREcard.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ProprietaryMIFAREcard_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      CardNumber := r0.CardNumber; // ATY 2017-07-19: CalcCardinal(r0.CardNumber);
    end;
  end;
end;

function TEmar105_ProprietaryMIFAREcard.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_ProprietaryMIFAREcard_v0);
end;

procedure TEmar105_ProprietaryMIFAREcard.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ProprietaryMIFAREcard_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.CardNumber := CardNumber; // ATY 2017-10-31: CalcCardinal(CardNumber);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ProprietaryMIFAREcardList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ProprietaryMIFAREcard.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 35 - TEmar105_RidesCityTariff '}

procedure TEmar105_RidesCityTariff.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RidesCityTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, SizeOf(r1));
      Id := r1.Id;
      ValidFrom := pchar(ReadValidFrom(r1.ValidFrom, Owner.CalendarBegin));
      IndexOfTariff := CalcWord(r1.IndexOfTariff) - 1;
      IndexOfFirstBusStopInRoute := r1.IndexOfFirstBusStopInRoute - 1;
      IndexOfLastBusStopInRoute := r1.IndexOfLastBusStopInRoute - 1;
      IndexOfCalendar := CalcWord(r1.IndexOfCalendar) - 1;
      PriceTable := r1.PriceTable;
      FirstPriceIndex := integer(CalcCardinal(r1.FirstPriceIndex)) - 1;
      TariffType := r1.TariffType;
    end;
  end;
end;

function TEmar105_RidesCityTariff.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_RidesCityTariff_v1);
end;

procedure TEmar105_RidesCityTariff.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_RidesCityTariff_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.ID_16 := 16;
      r1.ID_14 := 14;
      r1.PriceTable := 20;
      WriteValidFrom(r1.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r1.IndexOfTariff := CalcWord(IndexOfTariff + 1);
      r1.IndexOfFirstBusStopInRoute := IndexOfFirstBusStopInRoute + 1;
      r1.IndexOfLastBusStopInRoute := IndexOfLastBusStopInRoute + 1;
      r1.IndexOfCalendar := CalcWord(IndexOfCalendar + 1);
      r1.FirstPriceIndex := CalcCardinal(FirstPriceIndex + 1);
      r1.TariffType := TariffType;
      aStream.write(r1, SizeOf(r1));
    end;
  end;
end;

function TEmar105_RidesCityTariffList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_RidesCityTariff.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 36 - TEmar105_CityTariffPrice '}

function TEmar105_CityTariffPrice.GetTicketValidation: integer;
begin
  Result := fTicketValidation;
end;

function TEmar105_CityTariffPrice.GetValidationByDay: boolean;
begin
  Result := fValidationByDay;
end;

function TEmar105_CityTariffPrice.GetValidationByDuration: boolean;
begin
  Result := fValidationByDuration;
end;

function TEmar105_CityTariffPrice.GetValidationByText: boolean;
begin
  Result := fValidationByText;
end;

function TEmar105_CityTariffPrice.GetValidationByTime: boolean;
begin
  Result := fValidationByTime;
end;

procedure TEmar105_CityTariffPrice.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_CityTariffPrice_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0.Id, RecordLength(aVer));
      Id := r0.Id;
      FarePriceScaleNumber := r0.FarePriceScaleNumber;
      PriceNumber := r0.PriceNumber;
      TicketKind := r0.TicketKind;
      TicketValidation := r0.TicketValidation;
      ValidationSpecyfication := CopyPStr(r0.ValidationSpecyfication, SizeOf(r0.ValidationSpecyfication) - 1);
      DayLimit := r0.DayLimit;
      MinuteLimit := CalcWord(r0.MinuteLimit);
      ValidToHour := r0.ValidToHour;
      ValidToMinute := r0.ValidToMinute;
      RakeOff := CalcCardinal(r0.RakeOff);
      HandlingFee := CalcCardinal(r0.HandlingFee);
      Price := CalcCardinal(r0.Price);
      DescLimit := CopyPStr(r0.DescLimit, SizeOf(r0.DescLimit) - 1);
      ReductionAmount := CalcCardinal(r0.ReductionAmount);
      ReductionNameToPrint := CopyPStr(r0.ReductionNameToPrint, SizeOf(r0.ReductionNameToPrint) - 1);
      ReductionRatio := r0.ReductionRatio;
      ReductionBinnaryCode := r0.ReductionBinnaryCode;
      TotalTaskReport := r0.TotalTaskReport;
      ReductionType := r0.ReductionType;
      RoundPrice := r0.RoundPrice;
      TicketType := r0.TicketType;
      ReductionGroup := r0.ReductionGroup;
      OrderInReductionGroup := r0.OrderInReductionGroup;
      CompanyGovCode := CopyPStr(r0.CompanyGovCode, SizeOf(r0.CompanyGovCode) - 1);
      PTUNumber := r0.PTUNumber;
      ReductionCompany := CalcWord(r0.ReductionCompany);
      ReductionStatus := r0.ReductionStatus;
      TableNumber := r0.TableNumber;
      ValidFrom := pchar(ReadValidFrom(r0.ValidFrom, Owner.CalendarBegin));
      ValidTo := pchar(ReadValidTo(r0.ValidTo, Owner.CalendarBegin, ''));
    end;
  end;
end;

function TEmar105_CityTariffPrice.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_CityTariffPrice_v0);
end;

procedure TEmar105_CityTariffPrice.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_CityTariffPrice_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.OrderNumberInTicketRegister := 0;
      r0.FarePriceScaleNumber := FarePriceScaleNumber;
      r0.PriceNumber := PriceNumber;
      r0.TicketKind := TicketKind;
      r0.TicketValidation := TicketValidation;
      StrPLCopy(r0.ValidationSpecyfication, ansistring(ValidationSpecyfication),
        SizeOf(r0.ValidationSpecyfication) - 1);
      r0.DayLimit := DayLimit;
      r0.MinuteLimit := CalcWord(MinuteLimit);
      r0.ValidToHour := ValidToHour;
      r0.ValidToMinute := ValidToMinute;
      r0.RakeOff := CalcCardinal(RakeOff);
      r0.HandlingFee := CalcCardinal(HandlingFee);
      r0.Price := CalcCardinal(Price);
      StrPLCopy(r0.DescLimit, ansistring(DescLimit), SizeOf(r0.DescLimit) - 1);
      r0.ReductionAmount := CalcCardinal(ReductionAmount);
      StrPLCopy(r0.ReductionNameToPrint, ansistring(ReductionNameToPrint), SizeOf(r0.ReductionNameToPrint) - 1);
      r0.ReductionRatio := ReductionRatio;
      r0.ReductionBinnaryCode := ReductionBinnaryCode;
      r0.TotalTaskReport := TotalTaskReport;
      r0.ReductionType := ReductionType;
      r0.AdditionalFee := AdditionalFee;
      r0.RoundPrice := RoundPrice;
      r0.TicketType := TicketType;
      r0.ReductionGroup := ReductionGroup;
      r0.OrderInReductionGroup := OrderInReductionGroup;
      FillChar(r0.CompanyGovCode, SizeOf(r0.CompanyGovCode), 0);
      StrPLCopy(r0.CompanyGovCode, ansistring(CompanyGovCode), SizeOf(r0.CompanyGovCode) - 1);
      r0.PTUNumber := PTUNumber;
      r0.ReductionCompany := CalcWord(ReductionCompany);
      r0.ReductionStatus := ReductionStatus;
      r0.TableNumber := TableNumber;
      WriteValidFrom(r0.ValidFrom, Owner.CalendarBegin, ValidFrom);
      WriteValidTo(r0.ValidTo, Owner.CalendarBegin, ValidTo);
      r0.XOR_Sum := EmarXORSum(r0.FarePriceScaleNumber, SizeOf(r0) - 2);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

procedure TEmar105_CityTariffPrice.SetTicketValidation(const Value: integer);
begin
  fTicketValidation := Value;
  fValidationByDuration := (Value and $01) > 0;
  fValidationByTime := (Value and $02) > 0;
  fValidationByDay := (Value and $04) > 0;
  fValidationByText := (Value and $08) > 0;
end;

procedure TEmar105_CityTariffPrice.SetValidationByDay(const Value: boolean);
begin
  fValidationByDay := Value;
  if Value then begin
    fValidationByDuration := false;
    fValidationByTime := false;
    fValidationByText := false;
  end;
  if Value then fTicketValidation := $04;
end;

procedure TEmar105_CityTariffPrice.SetValidationByDuration(const Value: boolean);
begin
  fValidationByDuration := Value;
  if Value then begin
    fValidationByDay := false;
    fValidationByTime := false;
    fValidationByText := false;
  end;
  if Value then fTicketValidation := $01;
end;

procedure TEmar105_CityTariffPrice.SetValidationByText(const Value: boolean);
begin
  fValidationByText := Value;
  if Value then begin
    fValidationByDay := false;
    fValidationByDuration := false;
    fValidationByTime := false;
  end;
  if Value then fTicketValidation := $08;
end;

procedure TEmar105_CityTariffPrice.SetValidationByTime(const Value: boolean);
begin
  fValidationByTime := Value;
  if Value then begin
    fValidationByDay := false;
    fValidationByDuration := false;
    fValidationByText := false;
  end;
  if Value then fTicketValidation := $02;
end;

function TEmar105_CityTariffPriceList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_CityTariffPrice.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 37 - TEmar105_LineRoute '}

procedure TEmar105_LineRoute.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  rec: TEmar105_LineRoute_v0;
begin
  aStream.read(rec, RecordLength(aVer));
  Id := rec.Id;
  IndexOfBusStop := CalcWord(rec.IndexOfBusStopCode) - 1;
  Distance := integer(CalcCardinal(rec.Distance)) * 100;
  ReturnDistance := integer(CalcCardinal(rec.ReturnDistance)) * 100;
  BusStopStatus := rec.BusStopStatus;
end;

function TEmar105_LineRoute.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_LineRoute_v0);
end;

procedure TEmar105_LineRoute.SaveToBuffer(aStream: TStream; aVer: byte);
var
  rec: TEmar105_LineRoute_v0;
begin
  rec.Id := Id;
  rec.ID_9 := 9;
  rec.IndexOfBusStopCode := CalcWord(IndexOfBusStop + 1);
  rec.Distance := CalcCardinal(Round(Distance / 10) div 10);
  rec.ReturnDistance := CalcCardinal(Round(ReturnDistance / 10) div 10);
  rec.BusStopStatus := BusStopStatus;
  aStream.write(rec, RecordLength(aVer));
end;

function TEmar105_LineRouteList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_LineRoute.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 38 - TEmar105_LettersBusStopSideNumber '}

procedure TEmar105_LettersBusStopSideNumber.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_LettersBusStopSideNumber_v0;
  s:  string;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      Number := r0.Number;
      s := Trim(CopyLStr(r0.Letters, SizeOf(r0.Letters) - 1));
      Letters := pchar(s);
    end;
  end;
end;

function TEmar105_LettersBusStopSideNumber.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_LettersBusStopSideNumber_v0);
end;

procedure TEmar105_LettersBusStopSideNumber.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_LettersBusStopSideNumber_v0;
  s:  string;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.Number := Number;
      s := Format('%4s', [Letters]);
      StrPLCopy(r0.Letters, ansistring(s), SizeOf(r0.Letters) - 1, true, #0);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_LettersBusStopSideNumberList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_LettersBusStopSideNumber.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 39 - TEmar105_ExchangeRateAfterChangeCurrency '}

procedure TEmar105_ExchangeRateAfterChangeCurrency.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_ExchangeRateAfterChangeCurrency_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, RecordLength(aVer));
      Id := r1.Id;
      Number := r1.Number;
      Country := CopyPStr(r1.Country, SizeOf(r1.Country) - 1);
      Currency := CopyPStr(r1.Currency, SizeOf(r1.Currency) - 1);
      CurrencyUnit := r1.CurrencyUnit;
      ExchangeRateOfPLN := CalcCardinal(r1.ExchangeRateOfPLN);
      ExchangeRate := CalcCardinal(r1.ExchangeRate);
      if aVer >= 7 then ExchangeRateOfCurrency := CalcCardinal(r1.ExchangeRateOfCurrency)
      else ExchangeRateOfCurrency := 0;
    end;
  end;
end;

function TEmar105_ExchangeRateAfterChangeCurrency.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_ExchangeRateAfterChangeCurrency_v0);
  7, 8: Result := SizeOf(TEmar105_ExchangeRateAfterChangeCurrency_v1)
else Result := 0;
  end;
end;

procedure TEmar105_ExchangeRateAfterChangeCurrency.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_ExchangeRateAfterChangeCurrency_v1;
begin
  case aVer of
  6, 7, 8: begin
      r1.Id := Id;
      r1.Number := Number;
      StrPLCopy(r1.Country, ansistring(Country), SizeOf(r1.Country) - 1);
      StrPLCopy(r1.Currency, ansistring(Currency), SizeOf(r1.Currency) - 1);
      r1.CurrencyUnit := CurrencyUnit;
      r1.ExchangeRateOfPLN := CalcCardinal(ExchangeRateOfPLN);
      r1.ExchangeRate := CalcCardinal(ExchangeRate);
      if aVer >= 7 then r1.ExchangeRateOfCurrency := CalcCardinal(ExchangeRateOfCurrency);
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ExchangeRateAfterChangeCurrencyList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ExchangeRateAfterChangeCurrency.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 40 - TEmar105_TicketNextPeriod '}

procedure TEmar105_TicketNextPeriod.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r2: TEmar105_TicketNextPeriod_v2;
  pw: pWord;
  sk: byte;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r2, RecordLength(aVer));
      Id := r2.Id;
      CardNumber := r2.mifare_number; // ATY 2017-07-19: CalcCardinal(r2.mifare_number);
      Kind := byte(r2.Kind);
      case r2.Kind of
      0: begin
          TicketNumber := CopyPStr(r2.ticket_number, SizeOf(r2.ticket_number) - 1);
          ContinuedValidFrom := pchar(EmarDateToString(r2.valid_from_c));
          ContinuedValidTo := pchar(EmarDateToString(r2.valid_to_c));
          ControlCode := CalcCardinal(r2.control_code);
          ContinueType := 0;
          sk := EmarXORSum(r2.Id, 32);
          if (sk <> 0) and (r2.other[0] <> $FF) then begin
            ContinueNumber := r2.other[0];
            ContinueType := 1; // miesięczny
            if r2.other[1] <> $FF then begin
              if r2.other[2] = $FF then begin
                DayCountValid := r2.other[1];
                ContinueType := 2; // okresowy
              end else if r2.other[2] = $FD then begin
                RideCount := r2.other[1];
                ContinueType := 3; // wieloprzejazdowy
              end else begin
                pw := @r2.other[1];
                ValueCharging := CalcWord(pw^);
                ContinueType := 4; // okresowy przedpłacony
              end;
            end;
          end;
        end;
      1: begin
          ReliefBinaryCode := r2.binary_code;
          ReliefPercent := r2.relief_kind;
          ForeignTicket := r2.ticket_kind > 0;
          NumberOfVATRate1 := r2.vat_1;
          Price1 := CalcCardinal(r2.brutto_1);
          ReliefValue1 := CalcCardinal(r2.relief_1);
          NumberOfVATRate2 := r2.vat_2;
          Price2 := CalcCardinal(r2.brutto_2);
          ReliefValue2 := CalcCardinal(r2.relief_2);
          ContinuedValidTo := pchar(EmarDateToString(r2.pay_to));
        end;
      end;
      TicketNumberOnCard := CopyPStr(r2.card_ticket_number_p, SizeOf(r2.card_ticket_number_p) - 1);
    end;
  end;
end;

function TEmar105_TicketNextPeriod.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_TicketNextPeriod_v2);
end;

procedure TEmar105_TicketNextPeriod.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r2: TEmar105_TicketNextPeriod_v2;
  pw: pWord;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r2, SizeOf(r2), 0);
      r2.Id := Id;
      r2.mifare_number := CardNumber; // ATY 2017-07-19: CalcCardinal(CardNumber);
      r2.Kind := byte(Kind);
      case Kind of
      0: begin
          StrPLCopy(r2.ticket_number, ansistring(TicketNumber), SizeOf(r2.ticket_number) - 1, true, #0);
          DateToEmarDate(r2.valid_from_c, ContinuedValidFrom);
          DateToEmarDate(r2.valid_to_c, ContinuedValidTo);
          r2.control_code := CalcCardinal(ControlCode);
          FillChar(r2.other, SizeOf(r2.other), $FF);
          if aVer = 6 then ContinueType := 0;
          if ContinueType > 0 then r2.other[0] := ContinueNumber;
          case ContinueType of
          0: r2.other[2] := EmarXORSum(r2.Id, 31);
          1:; { nic }
          2: r2.other[1] := DayCountValid;
          3: begin
              r2.other[1] := RideCount;
              r2.other[2] := $FD;
            end;
          4: begin
              pw := @r2.other[1];
              pw^ := CalcWord(word(ValueCharging));
            end;
          end;
        end;
      1: begin
          r2.binary_code := byte(ReliefBinaryCode);
          r2.relief_kind := byte(ReliefPercent);
          if ForeignTicket then r2.ticket_kind := 1
          else r2.ticket_kind := 0;
          r2.vat_1 := byte(NumberOfVATRate1);
          r2.brutto_1 := CalcCardinal(cardinal(Price1));
          r2.relief_1 := CalcCardinal(cardinal(ReliefValue1));
          r2.vat_2 := byte(NumberOfVATRate2);
          if r2.ticket_kind = 1 then begin
            r2.brutto_2 := CalcCardinal(cardinal(Price2));
            r2.relief_2 := CalcCardinal(cardinal(ReliefValue2));
          end else begin
            r2.brutto_2 := $FFFFFFFF;
            r2.relief_2 := $FFFFFFFF;
          end;
          DateToEmarDate(r2.pay_to, ContinuedValidTo);
          r2.xor_sum1_p := EmarXORSum(r2.Id, 31);
        end;
      end;
      StrPLCopy(r2.card_ticket_number_p, ansistring(TicketNumberOnCard), SizeOf(r2.card_ticket_number_p) - 1, true, #0);
      r2.xor_sum2_p := EmarXORSum(r2.Id, SizeOf(r2) - 1);
      aStream.write(r2, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_TicketNextPeriodList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_TicketNextPeriod.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 41 - TEmar105_Shortcut '}

function TEmar105_Shortcut.FunctionName(): PChar;
type
  TSk = record
    Skrot: byte;
    Nrfunkcji: byte;
    Nazwa: string;
  end;

const
  MaxSkrot     = 99;
  MaxNrFunkcji = 28;
  DlgTblSkroty = 28;

//Tablica wartości domyślnych skrótów klawiszowych bileterki EMAR-105

  Skroty_EMAR105: array[1..DlgTblSkroty] of TSk =
  ((Skrot:  1; Nrfunkcji:  1; Nazwa: 'Raport dobowy'),
   (Skrot:  2; Nrfunkcji:  2; Nazwa: 'Raport miesięczny'),
   (Skrot:  3; Nrfunkcji:  3; Nazwa: 'Raport okresowy wg dat'),
   (Skrot:  4; Nrfunkcji:  4; Nazwa: 'Raport okresowy wg numerów'),
   (Skrot:  5; Nrfunkcji:  5; Nazwa: 'Raport okresowy sprzedaży'),
   (Skrot:  6; Nrfunkcji:  6; Nazwa: 'Raport niezerujący'),
   (Skrot:  7; Nrfunkcji:  7; Nazwa: 'Sprzedaż na następny okres biletu z EM-karty'),
   (Skrot:  8; Nrfunkcji:  8; Nazwa: 'Opłata dodatkowa'),
   (Skrot:  9; Nrfunkcji:  9; Nazwa: 'Wydruk kontrolny'),
   (Skrot: 10; Nrfunkcji: 10; Nazwa: 'Wpisanie numeru bocznego autobusu'),
   (Skrot: 11; Nrfunkcji: 11; Nazwa: 'Wybór kursu poza kalendarzem'),
   (Skrot: 12; Nrfunkcji: 12; Nazwa: 'Wybór kursu poza zadaniem'),
   (Skrot: 13; Nrfunkcji: 13; Nazwa: 'Raport kursów'),
   (Skrot: 14; Nrfunkcji: 14; Nazwa: 'Raport zadaniowy'),
   (Skrot: 15; Nrfunkcji: 15; Nazwa: 'Wyświetlenie stanu utargu'),
   (Skrot: 16; Nrfunkcji: 16; Nazwa: 'Wyświetlenie daty i czasu'),
   (Skrot: 17; Nrfunkcji: 17; Nazwa: 'Zmiana kodu PIN dostępu do menu bileterki'),
   (Skrot: 18; Nrfunkcji: 18; Nazwa: 'Włączenie/wyłączenie trybu SZYBKA SPRZEDAŻ'),
   (Skrot: 19; Nrfunkcji: 19; Nazwa: 'Czas na przystankach'),
   (Skrot: 20; Nrfunkcji: 20; Nazwa: 'Zmiana trybu wyłączania podświetlenia'),
   (Skrot: 21; Nrfunkcji: 21; Nazwa: 'Regulacja podświetlenia'),
   (Skrot: 22; Nrfunkcji: 22; Nazwa: 'Regulacja kontrastu'),
   (Skrot: 23; Nrfunkcji: 23; Nazwa: 'Zmiana trybu wyświetlania danych biletu miesięcznego'),
   (Skrot: 24; Nrfunkcji: 24; Nazwa: 'Testowanie czytnika EM-kart'),
   (Skrot: 25; Nrfunkcji: 25; Nazwa: 'Sprawdzenie numeru kontrolnego'),
   (Skrot: 26; Nrfunkcji: 26; Nazwa: 'Korekta czasu'),
   (Skrot: 27; Nrfunkcji: 27; Nazwa: 'Raport informacyjny'),
   (Skrot: 28; Nrfunkcji: 28; Nazwa: 'Raport miesięczny dopłat'));

{
  Pola Nrfunkcji oraz Nazwa nie mogą być zmieniane; do tablicy w przyszłości
  mogą zostać dodane nowe elementy.
  Pole Skrot może mieć wartość od 0 do 99 - może być zmieniane
  0-oznacza, że skrót nie jest zapisywany do bileterki,
  wartość 1-99 jest skrótem klawiaturowym uruchomienia funkcji menu z bileterki
  wywołanie w bileterce: nM (cyfra i klawisz 'M') lub nnM (dwie cyfry i 'M')

  Do bileterki zapisywane są skróty, które mają wartość > 0;
  dane zapisywane są w tablicy 41, uporządkowane w rosnącej
  kolejności pola Skrot

  Rekord 41
  ========================
  ID        : byte = 41
  KodSkrotu : byte = Skroty_EMAR105[i].Skrot
  NrFunkcji : byte = Skroty_EMAR105[i].Nrfunkcji
}

begin
  if (ShortcutCode >= 1)and(ShortcutCode <= DlgTblSkroty) then
    Result := PChar(Skroty_EMAR105[ShortcutCode].Nazwa)
  else
    Result := PChar('');
end;

procedure TEmar105_Shortcut.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Shortcut_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      ShortcutCode := r0.ShortcutCode;
      FunctionNumber := r0.FunctionNumber;
    end;
  end;
end;

function TEmar105_Shortcut.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_Shortcut_v0);
end;

procedure TEmar105_Shortcut.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_Shortcut_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.ShortcutCode := ShortcutCode;
      r0.FunctionNumber := FunctionNumber;
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ShortcutList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Shortcut.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 42 - TEmar105_AcceptedInspectorsCompany '}

procedure TEmar105_AcceptedInspectorsCompany.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_AcceptedInspectorsCompany_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      CompanyNumber := CalcWord(r0.CompanyNumber);
      CompanyName := CopyPStr(r0.CompanyName, SizeOf(r0.CompanyName) - 1);
    end;
  end;
end;

function TEmar105_AcceptedInspectorsCompany.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_AcceptedInspectorsCompany_v0);
end;

procedure TEmar105_AcceptedInspectorsCompany.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_AcceptedInspectorsCompany_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.CompanyNumber := CalcWord(CompanyNumber);
      StrPLCopy(r0.CompanyName, ansistring(CompanyName), SizeOf(r0.CompanyName) - 1, true, #0);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_AcceptedInspectorsCompanyList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_AcceptedInspectorsCompany.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 43 - TEmar105_ZoneNumber '}

procedure TEmar105_ZoneNumber.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_ZoneNumber_v1;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r1, RecordLength(aVer));
      Id := r1.Id;
      CompanyIndex := r1.CompanyIndex - 1;
      ZoneNumber := CalcWord(r1.ZoneNumber);
      ZoneName := CopyPStr(r1.ZoneName, SizeOf(r1.ZoneName) - 1);
      ZoneDesc := CopyPStr(r1.ZoneDesc, SizeOf(r1.ZoneDesc) - 1);
      PrintedName := CopyPStr(r1.PrintedName, SizeOf(r1.PrintedName) - 1);
      if aVer >= 7 then ZoneType := r1.ZoneType;
    end;
  end;
end;

function TEmar105_ZoneNumber.RecordLength(aVer: byte): integer;
begin
  case aVer of
  6: Result := SizeOf(TEmar105_ZoneNumber_v1) - 1;
else Result := SizeOf(TEmar105_ZoneNumber_v1);
  end;
end;

procedure TEmar105_ZoneNumber.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r1: TEmar105_ZoneNumber_v1;
begin
  case aVer of
  6, 7, 8: begin
      FillChar(r1, SizeOf(r1), 0);
      r1.Id := Id;
      r1.ID_8 := 8;
      r1.CompanyIndex := CompanyIndex + 1;
      r1.ZoneNumber := CalcWord(ZoneNumber);
      StrPLCopy(r1.ZoneName, ansistring(ZoneName), SizeOf(r1.ZoneName) - 1, true, #0);
      StrPLCopy(r1.ZoneDesc, ansistring(ZoneDesc), SizeOf(r1.ZoneDesc) - 1, true, #0);
      StrPLCopy(r1.PrintedName, ansistring(PrintedName), SizeOf(r1.PrintedName) - 1, true, #0);
      if aVer >= 7 then r1.ZoneType := ZoneType;
      aStream.write(r1, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ZoneNumberList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ZoneNumber.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 44 - TEmar105_FarePriceReduction '}
// jak 23 - Ulgi

{$ENDREGION}
{$REGION ' 45 - TEmar105_ChargingTariff '}

procedure TEmar105_ChargingTariff.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ChargingTariff_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      ValidFrom := pchar(ReadValidFrom(r0.ValidFrom, Owner.CalendarBegin));
      CompanyIndex := r0.CompanyIndex - 1;
      TariffNumber := r0.TariffNumber;
      TariffTable := r0.TariffTable;
      TariffType := r0.TariffType;
      PriceCount := r0.PriceCount;
      PriceIndex := r0.PriceIndex - 1;
      NumberOfVATRate := r0.NumberOfVATRate;
      CurrencyIndex := r0.CurrencyIndex - 1;
      CardValidDay := CalcWord(r0.CardValidDay);
      name := CopyPStr(r0.name, SizeOf(r0.name) - 1);
    end;
  end;
end;

function TEmar105_ChargingTariff.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_ChargingTariff_v0);
end;

procedure TEmar105_ChargingTariff.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ChargingTariff_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      WriteValidFrom(r0.ValidFrom, Owner.CalendarBegin, ValidFrom);
      r0.CompanyIndex := CompanyIndex + 1;
      r0.TariffNumber := TariffNumber;
      r0.TariffTable := TariffTable;
      r0.TariffType := TariffType;
      r0.PriceCount := PriceCount;
      r0.PriceIndex := PriceIndex + 1;
      r0.NumberOfVATRate := NumberOfVATRate;
      r0.CurrencyIndex := CurrencyIndex + 1;
      r0.CardValidDay := CalcWord(CardValidDay);
      StrPLCopy(r0.name, ansistring(name), SizeOf(r0.name) - 1, true, #0);
      DateToEmarDate(r0.ValidFromB, ValidFrom);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ChargingTariffList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ChargingTariff.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 46 - TEmar105_ChargingTariffPrice '}

procedure TEmar105_ChargingTariffPrice.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ChargingTariffPrice_v0;
begin
  case aVer of
  6, 7, 8: begin
      aStream.read(r0, RecordLength(aVer));
      Id := r0.Id;
      ValidPeriod := CalcWord(r0.ValidPeriod);
      Amount := CalcWord(r0.Amount);
      AmountForRides := CalcWord(r0.AmountForRides);
    end;
  end;
end;

function TEmar105_ChargingTariffPrice.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_ChargingTariffPrice_v0);
end;

procedure TEmar105_ChargingTariffPrice.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r0: TEmar105_ChargingTariffPrice_v0;
begin
  case aVer of
  6, 7, 8: begin
      r0.Id := Id;
      r0.ValidPeriod := CalcWord(ValidPeriod);
      r0.Amount := CalcWord(Amount);
      r0.AmountForRides := CalcWord(AmountForRides);
      r0.XOR_Sum := EmarXORSum(r0.Id, RecordLength(aVer) - 1);
      aStream.write(r0, RecordLength(aVer));
    end;
  end;
end;

function TEmar105_ChargingTariffPriceList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_ChargingTariffPrice.Create(Owner, Id);
end;
{$ENDREGION}
{$REGION ' 48 - TEmar105_DriverList '}

function TEmar105_Driver.RecordLength(aVer: byte = 0): integer;
begin
  Result := SizeOf(TEmar105_Driver_v0);
end;

procedure TEmar105_Driver.LoadFromBuffer(aStream: TStream; aVer: Byte);
var
  r0: TEmar105_Driver_v0;
begin
  aStream.read(r0, RecordLength(aVer));
  Id := r0.ID;
  Number := integer(CalcCardinal(r0.Number));
  FirstName := CopyPStr(r0.FirstName, SizeOf(r0.FirstName) - 1);
  LastName := CopyPStr(r0.LastName, SizeOf(r0.LastName) - 1);
  PIN := CalcWord(r0.PIN);
  SalePrefSet.MaxPassengersOnGroupTicket := r0.MaxPassengersOnGroupTicket;
  SalePrefSet.CardStatus[1] := r0.SaleOptions1;
  SalePrefSet.CardStatus[2] := r0.SaleOptions2;
  SalePrefSet.CardStatus[3] := r0.SaleOptions3;
  SalePrefSet.CardStatus[4] := r0.SaleOptions4;
  SalePrefSet.Options205[1] := r0.Emar205Options1;
  SalePrefSet.Options205[2] := r0.Emar205Options2;
  SalePrefSet.Options205[3] := r0.Emar205Options3;
  SalePrefSet.Options205[4] := r0.Emar205Options4;
//  SalePrefSet.EmployeeStatus := 7; // kierowca
  SalePrefSet.DaysBeforePrompt := r0.DaysBeforePrompt;
  SalePrefSet.DaysBeforeBlock := r0.DaysBeforeBlock;
end;

procedure TEmar105_Driver.SaveToBuffer(aStream: TStream; aVer: Byte);
var
  r0: TEmar105_Driver_v0;
begin
  r0.ID := Id;
  r0.Number := CalcCardinal(cardinal(Number));
  StrPLCopy(r0.FirstName, ansistring(FirstName), SizeOf(r0.FirstName) - 1, true, ' ');
  StrPLCopy(r0.LastName, ansistring(LastName), SizeOf(r0.LastName) - 1, true, ' ');
  r0.PIN := CalcWord(PIN);
  r0.XorPIN := EmarXORSum(r0.PIN, SizeOf(r0.PIN));
  r0.SaleOptions1 := SalePrefSet.CardStatus[1];
  r0.SaleOptions2 := SalePrefSet.CardStatus[2];
  r0.SaleOptions3 := SalePrefSet.CardStatus[3];
  r0.SaleOptions4 := SalePrefSet.CardStatus[4];
  r0.MaxPassengersOnGroupTicket := byte(SalePrefSet.MaxPassengersOnGroupTicket);
  r0.Emar205Options1 := SalePrefSet.Options205[1];
  r0.Emar205Options2 := SalePrefSet.Options205[2];
  r0.Emar205Options3 := SalePrefSet.Options205[3];
  r0.Emar205Options4 := SalePrefSet.Options205[4];
  r0.EmployeeStatus := 7; // kierowca
  r0.DaysBeforePrompt := SalePrefSet.DaysBeforePrompt;
  r0.DaysBeforeBlock := SalePrefSet.DaysBeforeBlock;
  r0.XorSum := EmarXORSum(r0.SaleOptions1, 12);
  aStream.write(r0, RecordLength(aVer));
end;

function TEmar105_DriverList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_Driver.Create(Owner, Id);
end;

{$ENDREGION}
{$REGION ' 51 - TEmar105_LineNumber'}

procedure TEmar105_LineNumber.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  a: array [0 .. RecordLength_v00 - 1] of ansichar;
begin
  aStream.Read(a[0], RecordLength_v00);
  LineNumber := CopyPStr(@a[1], MaxLineNumberLength_v00, false);
end;

function TEmar105_LineNumber.RecordLength(aVer: byte): integer;
begin
  Result := RecordLength_v00;
end;

procedure TEmar105_LineNumber.SaveToBuffer(aStream: TStream; aVer: byte);
var
  s: AnsiString;
  a: array [0 .. RecordLength_v00 - 1] of ansichar;
  i: integer;
begin
  s := AnsiString(LineNumber); // do A80 są zpisywane liczby konwetowane do stringa w prosty sposób
  FillChar(a, SizeOf(a), #0);
  a[0] := #51;
  for i := 1 to Length(s) do
    if i <= MaxLineNumberLength_v00 then a[i] := s[i]
    else break;
  aStream.write(a[0], RecordLength_v00);
end;

function TEmar105_LineNumberList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_LineNumber.Create(Owner, Id);
end;
{$ENDREGION}
{$REGION ' TEmar105_File '}

function New_Emar105_File: IEmar105_File; stdcall;
begin
  Result := TEmar105_File.Create;
end;

function New_Emar105_File_With_Callback(aCallback: IEmar_Callback): IEmar105_File; stdcall;
begin
  Result := TEmar105_File.Create;
  Result.Callback := aCallback;
end;

function TEmar105_File.CompareFile(aCompareReportFileName: PChar): LongWord;
var
  bIsWronglyPrinted: Boolean;
  bSourceIsEmar205, bFileIsEmar205: Boolean;
  _File: TEmar105_File; // raport, zamiast którego zamierzamy zapisać ten raport, co juz jest w Self
  _SourceEvent, _FileEvent: IEmar_ReportEvent;
  iSourceIdx: Integer; // dane, które chcemy zapisać
  iFileIdx: Integer; // dane, z którymi porównujemy
  iSourceDifferentEvents: Integer; // ile unikatowych zdarzeń w Source
//  iFileDifferentEvents: Integer; // ile unikatowych zdarzeń w File (aCompareReportFileName)
  iCompareDataLength: Integer;
//  d1, d2: PByte;
begin
  bSourceIsEmar205 := False;
  bFileIsEmar205 := False;
  _File := TEmar105_File.Create;
  try
    Result := _File.LoadFromFile(aCompareReportFileName);

    if Result = ERR_NO_ERROR then
    begin
{$REGION 'Core stage of the comparison - OIK and Const should be the same'}
      // compare OIK
      iCompareDataLength := 32; // compare just main information
      if EmarXORSum(TEmar105_OIK(OIK).Data^, iCompareDataLength) <>
        EmarXORSum(TEmar105_OIK(_File.OIK).Data^, iCompareDataLength) then
      begin
        Result := ERR_COMPARE_DIFFERENT;
        Exit; // totally different report
      end;

       // CE* online report has an empty CONSTS page
      if not IsEmar205OnlineReport() then
      begin
        // compare Const
        iCompareDataLength := TEmar105_Consts(Consts).DataLength; // size of one page
        if EmarXORSum(TEmar105_Consts(Consts).Data^, iCompareDataLength) <>
          EmarXORSum(TEmar105_Consts(_File.Consts).Data^, iCompareDataLength) then
        begin
          Result := ERR_COMPARE_DIFFERENT;
          Exit; // totally different report
        end;
      end;
{$ENDREGION}

{$REGION 'First stage of the comparison'}
      if Result = ERR_NO_ERROR then
      begin
        iSourceIdx := 0;
        iFileIdx := 0;
        while (iSourceIdx < ReportEventList.Count)or(iFileIdx < _File.ReportEventList.Count) do
        begin
{$REGION '          each stage common core part'}
          if iSourceIdx < ReportEventList.Count then
          begin
            _SourceEvent := ReportEventList[iSourceIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _SourceEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iSourceIdx);
              Continue;
            end;
          end
          else
            _SourceEvent := nil;

          if iFileIdx < _File.ReportEventList.Count then
          begin
            _FileEvent := _File.ReportEventList[iFileIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _FileEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iFileIdx);
              Continue;
            end;
          end
          else
            _FileEvent := nil;
{$ENDREGION '          each stage common core part'}

          if Assigned(_SourceEvent)
            and Assigned(_FileEvent)
            and(_SourceEvent.Kind = _FileEvent.Kind) then
          begin
            bIsWronglyPrinted := False;
            iCompareDataLength := TEmar_ReportEvent(_SourceEvent).DataLength;

            if _SourceEvent.Kind = 1 then
              bSourceIsEmar205 := Self.IsTicketRegisterEmar205(_SourceEvent.AsEvent_01.TicketRegister);
            if _FileEvent.Kind = 1 then
              bFileIsEmar205 := _File.IsTicketRegisterEmar205(_FileEvent.AsEvent_01.TicketRegister);

            // tickets
            if (_FileEvent.Kind in C_SET_OF_EMAR_TICKET_EVENTS)
              and bSourceIsEmar205 and bFileIsEmar205 then
            {$REGION 'Bilet sprzedany w Emar-205'}
            begin
              case _SourceEvent.Kind of
                13:
                  begin
                    // was WronglyPrinted ticket and now it's repaired in new file
                    if _FileEvent.AsEvent_13._IsWronglyPrinted and(not _SourceEvent.AsEvent_13._IsWronglyPrinted) then
                    begin
                      bIsWronglyPrinted := True;
                      iCompareDataLength := iCompareDataLength -
                        5{KodKBil} -
                        2{Puste} -
                        1{XOR};
                    end;
                  end;
                15:
                  begin
                    // was WronglyPrinted ticket and now it's repaired in new file
                    if _FileEvent.AsEvent_15._IsWronglyPrinted and(not _SourceEvent.AsEvent_15._IsWronglyPrinted) then
                    begin
                      bIsWronglyPrinted := True;
                      iCompareDataLength := iCompareDataLength -
                        5{KodKBil} -
                        1{XOR};
                    end;
                  end;
                16:
                  begin
                    // was WronglyPrinted ticket and now it's repaired in new file
                    if _FileEvent.AsEvent_16._IsWronglyPrinted and(not _SourceEvent.AsEvent_16._IsWronglyPrinted) then
                    begin
                      bIsWronglyPrinted := True;
                      iCompareDataLength := iCompareDataLength -
                        5{KodKBil} -
                        2{Puste} -
                        1{XOR};
                    end;
                  end;
                21:
                  begin
                    // was WronglyPrinted ticket and now it's repaired in new file
                    if _FileEvent.AsEvent_21._IsWronglyPrinted and(not _SourceEvent.AsEvent_21._IsWronglyPrinted) then
                    begin
                      bIsWronglyPrinted := True;
                      iCompareDataLength := iCompareDataLength -
                        5{KodKBil} -
                        1{Puste} -
                        1{XOR};
                    end;
                  end;
                30:
                  begin
                    // was WronglyPrinted ticket and now it's repaired in new file
                    if _FileEvent.AsEvent_30._IsWronglyPrinted and(not _SourceEvent.AsEvent_30._IsWronglyPrinted) then
                    begin
                      bIsWronglyPrinted := True;
                      iCompareDataLength := iCompareDataLength -
                        5{KodKBil} -
                        1{NrTarM} - // po prostu ofiara
                        1{NrCenyM} - // po prostu ofiara
                        1{XOR};
                    end;
                  end;
              end;
              if EmarXORSum(TEmar_ReportEvent(_SourceEvent).Data^, iCompareDataLength) =
                EmarXORSum(TEmar_ReportEvent(_FileEvent).Data^, iCompareDataLength) then
              begin
                if bIsWronglyPrinted then
                  Result := ERR_COMPARE_TICKET_WRONGLY_PRINTED
                else
                begin // are exactly the same events
                  Inc(iSourceIdx);
                  Inc(iFileIdx);
                  Continue;
                end;
              end
              else
              begin
                Result := ERR_COMPARE_DIFFERENT;
                Break;
              end;
            end {$ENDREGION}
            else
            begin
              if EmarXORSum(TEmar_ReportEvent(_SourceEvent).Data^, iCompareDataLength) =
                EmarXORSum(TEmar_ReportEvent(_FileEvent).Data^, iCompareDataLength) then
              begin // are exactly the same events
                Inc(iSourceIdx);
                Inc(iFileIdx);
                Continue;
              end
              else
              begin
                Result := ERR_COMPARE_DIFFERENT;
                Break;
              end;
            end;
          end
          else
          begin
            Result := ERR_COMPARE_DIFFERENT;
            Break; // exit from while; na tym poziomie uważane za różne raporty
          end;

          Inc(iSourceIdx);
          Inc(iFileIdx);
        end; // while
      end;
{$ENDREGION}

{$REGION 'Second stage of the comparison - assumes that files are checked as different in the first stage'}
      if Result = ERR_COMPARE_DIFFERENT then
      begin // sprawdzamy pod kątem tego, czy wyłącznie doszło kilku nowych zdarzeń; zmienione nie są brane pod uwage
//        // compare Const
//        //iCompareDataLength := TEmar105_Consts(Consts).DataLength; // size of one page
//        iCompareDataLength := 176;
//        if EmarXORSum(TEmar105_Consts(Consts).Data^, iCompareDataLength) <>
//          EmarXORSum(TEmar105_Consts(_File.Consts).Data^, iCompareDataLength) then
//        begin
//          Result := ERR_COMPARE_DIFFERENT;
//          Exit; // totally different report
//        end;
//
//{$REGION '        Niestety na końcu wersji programu I2.0 niepoprawnie zapisywała symbol 20 zamiast 00, w sumie 4 bajty CONST do ominięcia'}
//        d1 := TEmar105_Consts(Consts).Data;
//        d2 := TEmar105_Consts(_File.Consts).Data;
//        Inc(d1, iCompareDataLength + 4);
//        Inc(d2, iCompareDataLength + 4);
//        iCompareDataLength := TEmar105_Consts(Consts).DataLength - iCompareDataLength - 4 - 16; // - 16 bajt XOR line
//        if EmarXORSum(d1^, iCompareDataLength) <>
//          EmarXORSum(d2^, iCompareDataLength) then
//        begin
//          Result := ERR_COMPARE_DIFFERENT;
//          Exit; // totally different report
//        end;
//{$ENDREGION}

        iSourceIdx := 0;
        iFileIdx := 0;
        iSourceDifferentEvents := 0;
//        iFileDifferentEvents := 0;
        while (iSourceIdx < Self.ReportEventList.Count)or(iFileIdx < _File.ReportEventList.Count) do
        begin
{$REGION '          each stage common core part'}
          if iSourceIdx < Self.ReportEventList.Count then
          begin
            _SourceEvent := Self.ReportEventList[iSourceIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _SourceEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iSourceIdx);
              Continue;
            end;
          end
          else
            _SourceEvent := nil;

          if iFileIdx < _File.ReportEventList.Count then
          begin
            _FileEvent := _File.ReportEventList[iFileIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _FileEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iFileIdx);
              Continue;
            end;
          end
          else
            _FileEvent := nil;
{$ENDREGION '          each stage common core part'}

          if
            Assigned(_SourceEvent)
            and Assigned(_FileEvent)
            //and(_SourceEvent.Kind = _FileEvent.Kind)
          then
          begin
            iCompareDataLength := TEmar_ReportEvent(_FileEvent).DataLength;

            if
              (_SourceEvent.Kind <> _FileEvent.Kind)
              or
              (EmarXORSum(TEmar_ReportEvent(_SourceEvent).Data^, iCompareDataLength) <>
                EmarXORSum(TEmar_ReportEvent(_FileEvent).Data^, iCompareDataLength))
            then
              Inc(iSourceDifferentEvents)
            else
              Inc(iFileIdx);
          end
          else
            if not Assigned(_FileEvent) then
              Inc(iSourceDifferentEvents)
            else
              if not Assigned(_SourceEvent) then
                Break;
          {
          else
            Break}; // end of one of the reports
          Inc(iSourceIdx); // zawsze
        end;

        Result := ERR_COMPARE_DIFFERENT;
        if
          (Self.ReportEventList.Count > 0)
          and(_File.ReportEventList.Count > 0)
          and(_File.ReportEventList.Count < Self.ReportEventList.Count) // w _File mniej zdarżeń, niż w Self
        then
        begin // w istniejącym raporcie _File mniej zdarzeń, niz w tym, z którym porównujemy (Self)
          if
            (iSourceIdx = Self.ReportEventList.Count) // przeanalizowane wszystkie zdarzenia _File
            and(iFileIdx = _File.ReportEventList.Count) // przeanalizowane wszystkie zdarzenia Self
          then
          begin
            if iSourceDifferentEvents > 0 then // są nowe zdarzenia w _File
              Result := ERR_COMPARE_ADDED_EVENTS
            else
              if
                (Self.ReportEventList.Count = _File.ReportEventList.Count) // w Self mniej zdarżeń, niż w _File
                and(iSourceDifferentEvents = 0) // nie ma nowych zdarzeń w Self
              then
                Result := ERR_NO_ERROR;
          end;
        end
        else
          if
            (_File.ReportEventList.Count = Self.ReportEventList.Count) // w _File tyle samo zdarzeń co w Self
            and(iSourceDifferentEvents = 0) // nie ma nowych zdarzeń w Self
          then
            Result := ERR_NO_ERROR;
      end;
{$ENDREGION}

{$REGION 'Third stage of the comparison - different payment type'}
      if
        (
          (Result = ERR_COMPARE_DIFFERENT)
          or
          (Result = ERR_COMPARE_ADDED_EVENTS)
        )
        and Self.IsEmar205OnlineReport() // CE
//        and(not _File.IsReportEvent41) // nie ma zdarzenia #41
        and not( // na początku nie ma zdarzenia #41
          (_File.ReportEventList.Count > 0)and(_File.ReportEventList[0].Kind = 41)
          or(_File.ReportEventList.Count > 1)and(_File.ReportEventList[1].Kind = 41)
          or(_File.ReportEventList.Count > 2)and(_File.ReportEventList[2].Kind = 41)
          or(_File.ReportEventList.Count > 3)and(_File.ReportEventList[3].Kind = 41)
          or(_File.ReportEventList.Count > 4)and(_File.ReportEventList[4].Kind = 41)
        )
        and Self.IsReportEvent41 // dodano zdarzenie #41
      then
      begin
        iSourceIdx := 0;
        iFileIdx := 0;
        while (iSourceIdx < ReportEventList.Count)or(iFileIdx < _File.ReportEventList.Count) do
        begin
{$REGION '          each stage common core part'}
          if iSourceIdx < Self.ReportEventList.Count then
          begin
            _SourceEvent := Self.ReportEventList[iSourceIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _SourceEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iSourceIdx);
              Continue;
            end;
          end
          else
            _SourceEvent := nil;

          if iFileIdx < _File.ReportEventList.Count then
          begin
            _FileEvent := _File.ReportEventList[iFileIdx];
            {
              zdarzenie 11 'Wydruk raportu zadaniowego' - może być usunięte przy korekcie
            }
            if _FileEvent.Kind = EMAR_REPORT_EVENT_11 then
            begin
              Inc(iFileIdx);
              Continue;
            end;
          end
          else
            _FileEvent := nil;
{$ENDREGION '          each stage common core part'}

          if Assigned(_SourceEvent)and Assigned(_FileEvent) then
          begin
            // w przypadku dojścia zdarzenia #41, sprawdzamy jedynie zgodność biletów, reszta nie powinna
            if not(_SourceEvent.Kind in C_SET_OF_EMAR_TICKET_EVENTS) then
            begin
              Inc(iSourceIdx);
              Continue;
            end;
            if not(_FileEvent.Kind in C_SET_OF_EMAR_TICKET_EVENTS) then
            begin
              Inc(iFileIdx);
              Continue;
            end;

            if _SourceEvent.Kind = _FileEvent.Kind then
            begin
              iCompareDataLength := TEmar_ReportEvent(_FileEvent).DataLength;

              if
                (EmarXORSum(TEmar_ReportEvent(_SourceEvent).Data^, iCompareDataLength) <>
                  EmarXORSum(TEmar_ReportEvent(_FileEvent).Data^, iCompareDataLength))
              then
                Break;
            end
            else
              Break;
          end;

          Inc(iSourceIdx);
          Inc(iFileIdx);
        end;

        Result := ERR_COMPARE_CE_ADDED_IDENTIFY_EVENTS;
      end;
{$ENDREGION}
    end;
  finally
    FreeAndNil(_File);
  end;
end;

constructor TEmar105_File.Create;
begin
  inherited Create(true, EMAR_FILE_TYPE_EMAR105, LAST_FILE_VER_EMAR105);

  fCallback := nil;

  fFat := TEmar_Fat.Create(self, 1);
  fOik := TEmar105_OIK.Create(self, 3);
  fDir := TEmar_Dir.Create(self, 5);
  fConsts := TEmar105_Consts.Create(self, 7);

  fCompanyList := TEmar105_CompanyList.Create(self, 8);
  fBusStopList := TEmar105_BusStopList.Create(self, 9);
  fRideList := TEmar105_RideList.Create(self, 10);
  fRideRouteList := TEmar105_RideRouteList.Create(self, 11);
  fRideTariffList := TEmar105_RideTariffList.Create(self, 12);
  fRideReductionList := TEmar105_RideReductionList.Create(self, 13);
  fCalendarList := TEmar105_CalendarList.Create(self, 14);
  fRideDesignationList := TEmar105_RideDesignationList.Create(self, 15);
  fTariffList := TEmar105_TariffList.Create(self, 16);
  fPriceList := TEmar105_PriceList.Create(self, 17);
  fPriceIndexes1 := TEmar_PriceIndexes.Create(self, 18);
  fPriceIndexes2 := TEmar_PriceIndexes.Create(self, 19);
  fFarePriceScaleZoneNumbers := TEmar_FarePriceScaleZoneNumber.Create(self, 20);
  fCurrencyExchangeList := TEmar105_CurrencyExchangeList.Create(self, 21);
  fPaymentTypeList := TEmar105_PaymentTypeList.Create(self, 22);
  fFarePriceReductionList := TEmar105_FarePriceReductionList.Create(self, 23);
  fTaskList := TEmar105_TaskList.Create(self, 24);
  fTaskPositionList := TEmar105_TaskPositionList.Create(self, 25);
  fLineList := TEmar105_LineList.Create(self, 26);
  fRideBonusList := TEmar105_RideBonusList.Create(self, 27);
  fRideHandlingFeeList := TEmar105_RideHandlingFeeList.Create(self, 28);
  fAdditionalFeeList := TEmar105_AdditionalFeeList.Create(self, 29);
  fLuggageTariffList := TEmar105_LuggageTariffList.Create(self, 30);
  fReferenceRideList := TEmar105_ReferenceRideList.Create(self, 31);
  fAcceptedTicketOwnerList := TEmar105_AcceptedTicketOwnerList.Create(self, 32);
  fAcceptedTradeReliefCardOwnerList := TEmar105_AcceptedTradeReliefCardOwnerList.Create(self, 33);
  fProprietaryMIFAREcardList := TEmar105_ProprietaryMIFAREcardList.Create(self, 34);
  fRidesCityFarePriceScaleList := TEmar105_RidesCityTariffList.Create(self, 35);
  fPriceCityFarePriceScaleList := TEmar105_CityTariffPriceList.Create(self, 36);
  fLineRouteList := TEmar105_LineRouteList.Create(self, 37);
  fLettersBusStopSideNumberList := TEmar105_LettersBusStopSideNumberList.Create(self, 38);
  fExchangeRateAfterChangeCurrencyList := TEmar105_ExchangeRateAfterChangeCurrencyList.Create(self, 39);
  fTicketNextPeriodList := TEmar105_TicketNextPeriodList.Create(self, 40);
  fShortcutList := TEmar105_ShortcutList.Create(self, 41);
  fAcceptedInspectorsCompanyList := TEmar105_AcceptedInspectorsCompanyList.Create(self, 42);
  fZoneNumberList := TEmar105_ZoneNumberList.Create(self, 43);
  fMonthTicketReductionList := TEmar105_FarePriceReductionList.Create(self, 44);
  fChargingTariffList := TEmar105_ChargingTariffList.Create(self, 45);
  fChargingTariffPriceList := TEmar105_ChargingTariffPriceList.Create(self, 46);
  fBusStopStandList := TEmar105_BusStopStandList.Create(self, 47);
  fDriverList := TEmar105_DriverList.Create(self, 48);
  fLineNumberList := TEmar105_LineNumberList.Create(self, 51);
  fEmar205TextsList := TEmar205_TextsList.Create(Self, 52);
  fEmar205WifiList := TEmar205_WiFiList.Create(Self, 53);

  fReportStartedRides := TEmar105_StartedRideList.Create(self, 100);
  fReportList := TEmar105_ReportEventList.Create(self, 101);

  fUSBStream := TEmarFlashUSBStream.Create;
  fUSBStream.OnBeforePageRead := StreamOnBeforePageRead;
  fUSBStream.OnBeforePageWrite := StreamOnBeforePageWrite;
  fUSBStream.OnBeforePageClear := StreamOnBeforePageClear;
  fUSBStream.OnBeforeBlockClear := StreamOnBeforeBlockClear;

  fStream := TMemoryStream.Create;

  fUsbDevice := fUSBStream.USBDevice;

  fBAFile := TEmar_BA_File.Create(self, 0);
  fNAFile := TEmar_NA_File.Create(self, 0);
  fDriverBalancesFile := TEmar_DriverBalances_File.Create(self, 0);
  fCardsFile := TEmar_Cards_File.Create(self, 0);

  F_SavedReadyCode := 0; // nie był jeszcze zmieniany
end;

destructor TEmar105_File.Destroy;
begin
  fUsbDevice := nil;
  // fOik       := nil;
  // fConsts    := nil;
  // fBAFile := nil;
  FreeAndNil(fUSBStream);
  FreeAndNil(fStream);
  inherited Destroy;
end;

function TEmar105_File.LoadAFileFromDevice: cardinal;
begin
  Result := ERR_USER_TERMINATE;

  if fConsts.Required then TEmar_InterfacedObject(fConsts).LoadFromBuffer(fUSBStream);

  Fat.Nr := 1;
  Fat.LoadFromBuffer(fUSBStream);

  fOik.Number := 1;
  TEmar105_OIK(OIK).LoadFromBuffer(fUSBStream);

  Dir.Nr := 1;
  Dir.LoadFromBuffer(fUSBStream);

  if fBreak then Exit;

  // $11 = 17 - Ceny
  if fPriceList.Required then begin
    LoadList(fPriceList, fUSBStream);
    if fBreak then Exit;
  end;

  // $D = 13 - Ulgi kursów
  if fRideReductionList.Required then LoadList(fRideReductionList, fUSBStream);

  // $A = 10 - Kursy
  if fRideList.Required then begin
    LoadList(fRideList, fUSBStream);
    if fBreak then Exit;
  end;

  // $8 = 08 - Firmy
  if fCompanyList.Required then begin
    LoadList(fCompanyList, fUSBStream);
    if fBreak then Exit;
  end;

  // $9 = 09 - Przystanki
  if fBusStopList.Required then begin
    LoadList(fBusStopList, fUSBStream);
    if fBreak then Exit;
  end;
  // $2B = 47 - Słupki przystanków
  if fBusStopStandList.Required then begin
    LoadList(fBusStopStandList, fUSBStream);
    if fBreak then Exit;
  end;

  // $B = 11 - Trasy kursów
  if fRideRouteList.Required then begin
    LoadList(fRideRouteList, fUSBStream);
    if fBreak then Exit;
  end;

  // $C = 12 - Taryfy kursów
  if fRideTariffList.Required then begin
    LoadList(fRideTariffList, fUSBStream);
    if fBreak then Exit;
  end;

  // $E = 14 - Kalendarz
  if fCalendarList.Required then begin
    LoadList(fCalendarList, fUSBStream);
    fCalendarList.CalendarLength := MonthsCount(StrToDate(_GetCalendarBegin), StrToDate(_GetCalendarEnd)) + 1;
    if fBreak then Exit;
  end;

  // $F = 15 - Oznaczenia kursów
  if fRideDesignationList.Required then begin
    LoadList(fRideDesignationList, fUSBStream);
    if fBreak then Exit;
  end;

  // $10 = 16 - Taryfy
  if fTariffList.Required then begin
    LoadList(fTariffList, fUSBStream);
    if fBreak then Exit;
  end;

  // $12 = 18 - Indeksy cen dla cenników tabelowych typu 1 (max 15 cen w taryfie)
  if TEmar_PriceIndexes(fPriceIndexes1).Required then begin
    TEmar_PriceIndexes(fPriceIndexes1).LoadFromBuffer(fUSBStream, Version);
    if fBreak then Exit;
  end;

  // $13 = 19 - Indeksy cen dla cenników tabelowych typu 2 (max 255 cen w taryfie) (to samo co TEmar_PriceIndexes (18))
  if TEmar_PriceIndexes(fPriceIndexes2).Required then begin
    TEmar_PriceIndexes(fPriceIndexes2).LoadFromBuffer(fUSBStream, Version);
    if fBreak then Exit;
  end;

  // $14 = 20 - Numery stref dla taryf strefowych
  if TEmar_FarePriceScaleZoneNumber(fFarePriceScaleZoneNumbers).Required then begin
    TEmar_FarePriceScaleZoneNumber(fFarePriceScaleZoneNumbers).LoadFromBuffer(fUSBStream, Version);
    if fBreak then Exit;
  end;

  // $16 = 22 - Sposoby zapłaty
  if fPaymentTypeList.Required then begin
    LoadList(fPaymentTypeList, fUSBStream);
    if fBreak then Exit;
  end;

  // $17 = 23 - Ulgi
  if fFarePriceReductionList.Required then begin
    LoadList(fFarePriceReductionList, fUSBStream);
    if fBreak then Exit;
  end;

  // $33 = 51 - Numery linii - musi być odczytane przed liniami!!!
  if fLineNumberList.Required then begin
    LoadList(fLineNumberList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1A = 26 - Linie
  if fLineList.Required then begin
    LoadList(fLineList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1B = 27 - Bonifikaty kursów
  if fRideBonusList.Required then begin
    LoadList(fRideBonusList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1C = 28 - Opłaty manipulacyjne kursów
  if fRideHandlingFeeList.Required then begin
    LoadList(fRideHandlingFeeList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1D = 29 - Opłaty dodatkowe
  if fAdditionalFeeList.Required then begin
    LoadList(fAdditionalFeeList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1E = 30 - Taryfy bagażowe kursów
  if fLuggageTariffList.Required then begin
    LoadList(fLuggageTariffList, fUSBStream);
    if fBreak then Exit;
  end;

  // $23 = 35 - Taryfy miejskie kursów
  if fRidesCityFarePriceScaleList.Required then begin
    LoadList(fRidesCityFarePriceScaleList, fUSBStream);
    if fBreak then Exit;
  end;

  // $24 = 36 - Ceny taryfy miejskiej
  if fPriceCityFarePriceScaleList.Required then begin
    LoadList(fPriceCityFarePriceScaleList, fUSBStream);
    if fBreak then Exit;
  end;

  // $25 = 37 - Trasy linii
  if fLineRouteList.Required then begin
    LoadList(fLineRouteList, fUSBStream);
    if fBreak then Exit;
  end;

  // $26 = 38 - Litery numerów bocznych autobusów
  if fLettersBusStopSideNumberList.Required then begin
    LoadList(fLettersBusStopSideNumberList, fUSBStream);
    if fBreak then Exit;
  end;

  // $2B = 43 - Wykaz stref biletowych
  if fZoneNumberList.Required then begin
    LoadList(fZoneNumberList, fUSBStream);
    if fBreak then Exit;
  end;

  // $2C = 44 - Ulgi BM (jak 23 - Ulgi)
  if fMonthTicketReductionList.Required then begin
    LoadList(fMonthTicketReductionList, fUSBStream);
    if fBreak then Exit;
  end;

  // $2D = 45 - Taryfa doładowań EM-karty - realizacja odłożona
  if fChargingTariffList.Required then begin
    LoadList(fChargingTariffList, fUSBStream);
    if fBreak then Exit;
  end;

  // $2E = 46 - Ceny doładowań EM-karty - realizacja odłożona
  if fChargingTariffPriceList.Required then begin
    LoadList(fChargingTariffPriceList, fUSBStream);
    if fBreak then Exit;
  end;

  // $1F = 31 - Skorowidz kursów
  if fReferenceRideList.Required then begin
    LoadList(fReferenceRideList, fUSBStream);
    if fBreak then Exit;
  end;

  // dane dodatkowe
  // $15 = 21 - Przeliczniki walut – dane dodatkowe
  if fCurrencyExchangeList.Required then begin
    LoadList(fCurrencyExchangeList, fUSBStream);
    if fBreak then Exit;
  end;

  // $18 = 24 - Zadania – dane dodatkowe
  if fTaskList.Required then begin
    LoadList(fTaskList, fUSBStream);
    if fBreak then Exit;
  end;

  // $19 = 25 - Pozycje zadań – dane dodatkowe
  if fTaskPositionList.Required then begin
    LoadList(fTaskPositionList, fUSBStream);
    if fBreak then Exit;
  end;

  // $20 = 32 - Wykaz firm rozliczających przewozy pasażerów z biletami miesięcznymi – dane dodatkowe
  if fAcceptedTicketOwnerList.Required then begin
    LoadList(fAcceptedTicketOwnerList, fUSBStream);
    if fBreak then Exit;
  end;

  // $21 = 33 - Wykaz firm wydających akceptowane przez bileterkę karty pasażerów z ulgą handlową – dane dodatkowe
  if fAcceptedTradeReliefCardOwnerList.Required then begin
    LoadList(fAcceptedTradeReliefCardOwnerList, fUSBStream);
    if fBreak then Exit;
  end;

  // $22 = 34 - Wykaz zastrzeżonych kart MIFARE – dane dodatkowe
  if fProprietaryMIFAREcardList.Required then begin
    LoadList(fProprietaryMIFAREcardList, fUSBStream);
    if fBreak then Exit;
  end;

  // $27 = 39 - Przeliczniki walut po zmianie waluty cennika
  if fExchangeRateAfterChangeCurrencyList.Required then begin
    LoadList(fExchangeRateAfterChangeCurrencyList, fUSBStream);
    if fBreak then Exit;
  end;

  // $28 = 40 - Wykaz kart MIFARE z biletami do przedłużenia / sprzedaży na następny okres – dane dodatkowe
  if fTicketNextPeriodList.Required then begin
    LoadList(fTicketNextPeriodList, fUSBStream);
    if fBreak then Exit;
  end;

  // $29 = 41 - Wykaz skrótów klawiszowych do funkcji bileterki – dane dodatkowe
  if fShortcutList.Required then begin
    LoadList(fShortcutList, fUSBStream);
    if fBreak then Exit;
  end;

  // $2A = 42 - Wykaz firm wydających akceptowane przez bileterkę karty kontrolerów – dane dodatkowe
  if fAcceptedInspectorsCompanyList.Required then begin
    LoadList(fAcceptedInspectorsCompanyList, fUSBStream);
    if fBreak then Exit;
  end;

  // $30 = 48 - Kierowcy (solobus)
  if fDriverList.Required then begin
    LoadList(fDriverList, fUSBStream);
    if fBreak then Exit;
  end;

  Fat.Nr := 2;
  Fat.LoadFromBuffer(fUSBStream);
  if fBreak then Exit;

  Dir.Nr := 2;
  Dir.LoadFromBuffer(fUSBStream);
  if fBreak then Exit;

  Result := ERR_NO_ERROR;
end;

function TEmar105_File.ReportCashValue(): LongWord;
  function __isKARCurrency(ACurrencyExchange: IEmar_CurrencyExchange): Boolean;
  begin
    Result := False;
    if Assigned(ACurrencyExchange) then
      Result :=
        (ACurrencyExchange.ExchangeRate = 10000)
        and(
          (String(ACurrencyExchange.Currency).ToUpper() = C_CURRENCY_KAR_SYMBOL)
          or
          (String(ACurrencyExchange.Country).ToUpper() = C_CURRENCY_KAR_NAME)
        );
  end;

  function __isEmar105CardPayment(ATicketEvent: IEmar_ReportEvent; ATicketEventIndex: Integer): Boolean;
  var
    iRecordIndex, iIndexOfCurrency: Integer;
    relEvent_32: IEmar_ReportEvent_32;
  begin
    Result := False;
    iIndexOfCurrency := -1;
    if Assigned(ATicketEvent) then
    begin
      case ATicketEvent.Kind of
        13: iIndexOfCurrency := ATicketEvent.AsEvent_13.IndexOfCurrency;
        15: iIndexOfCurrency := ATicketEvent.AsEvent_15.IndexOfCurrency;
        16: iIndexOfCurrency := ATicketEvent.AsEvent_16.IndexOfCurrency;
        21: iIndexOfCurrency := ATicketEvent.AsEvent_21.IndexOfCurrency;
        30: iIndexOfCurrency := ATicketEvent.AsEvent_30.IndexOfCurrency;
        32:
          begin
            relEvent_32 := ATicketEvent.AsEvent_32;
            iRecordIndex := Succ(ATicketEventIndex);
            // po sprzedaży może iść rejestracja przejazdu
            if (iRecordIndex < Self.ReportEventList.Count)
              and(Self.ReportEventList.Items[iRecordIndex].Kind = 17) 
            then
              Inc(iRecordIndex);
            // błedów identyfikacji może być kilku
            while (iRecordIndex < Self.ReportEventList.Count)
              and(Self.ReportEventList.Items[iRecordIndex].Kind in
              [
                  33 // Rejestracja przejazdu z biletem miesięcznym (karta MIFARE) - błędy identyfikacji
                , 34 // Rejestracja przejazdu z biletem miesięcznym (karta MIFARE) - nieprawidłowe bilety
              ]) 
            do
              Inc(iRecordIndex);
            // jeśli kolejnym zdarzeniem jest 'Opłata dodatkowa' w walucie KAR \ 'KARTA PŁATNICZA' na dowolną kwote
            Exit(
              (iRecordIndex < Self.ReportEventList.Count)
              and(Self.ReportEventList.Items[iRecordIndex].Kind = 21) // opłata dodatkowa
              and __isEmar105CardPayment(Self.ReportEventList.Items[iRecordIndex], iRecordIndex) // w walucie KAR \ 'KARTA PŁATNICZA'
            );
          end;
      end;
      Result :=
        (iIndexOfCurrency > 0)
        and(iIndexOfCurrency < Self.CurrencyExchangeList.Count)
        and __isKARCurrency(Self.CurrencyExchangeList.Items[iIndexOfCurrency]);
    end;
  end;
var
  r1ok, r2ok, r3ok, bIsTicketRegisterEmar205: Boolean;
  lrek:             Integer;
  iRecord:          Integer;
  rel:              IEmar_ReportEvent;
  rel_01:           IEmar_ReportEvent_01;
begin
  Result := 0;

  if (Self.ReportEventList.Count > 0) and (Self.ReportEventList[0].Kind <> 0)
  // EMAR-205 – rekord występuje wyłącznie w raportach zapisywanych w kartach pamięci.
    or (Self.ReportEventList.Count > 1) and (Self.ReportEventList[0].Kind = 0) // jest raport
  then begin // uważamy, iż _NonCashInTicketPrice są przeliczone w odczycie zdarzenia #36 'zmiana sposobu zapłaty'
    iRecord := 0;

    while iRecord < Self.ReportEventList.Count do
    begin
      rel := Self.ReportEventList[iRecord];
      lrek := rel.ReportRecordCount;
      r1ok := (lrek > 0) and not rel.IsError(reErrorPartMissing1 or reErrorCheckSum1);
      r2ok := (lrek < 2) or (lrek > 1) and not rel.IsError(reErrorPartMissing2 or reErrorCheckSum2);
      r3ok := (lrek < 3) or (lrek > 2) and not rel.IsError(reErrorPartMissing3 or reErrorCheckSum3);
      if rel.Kind = 1 then
        rel_01 := rel.AsEvent_01;
      if Assigned(rel_01) and r1ok and r2ok and r3ok then // prawidłowe zdarzenie
      begin
        bIsTicketRegisterEmar205 := Self.IsTicketRegisterEmar205(rel_01.TicketRegister);
        case rel.Kind of
          13:
            begin
              if bIsTicketRegisterEmar205 and(not rel.AsEvent_13._IsWronglyPrinted)
                or
                (not bIsTicketRegisterEmar205)and(not rel.AsEvent_13._IsWrong)and(not __isEmar105CardPayment(rel, iRecord)) then
                Inc(Result, rel.AsEvent_13.TicketPrice - rel.AsEvent_13._NonCashInTicketPrice);
            end;
          15:
            begin
              if bIsTicketRegisterEmar205 and(not rel.AsEvent_15._IsWronglyPrinted)
                or
                (not bIsTicketRegisterEmar205)and(not rel.AsEvent_15._IsWrong)and(not __isEmar105CardPayment(rel, iRecord)) then
                Inc(Result, rel.AsEvent_15.TicketPrice - rel.AsEvent_15._NonCashInTicketPrice);
            end;
          16:
            begin
              if bIsTicketRegisterEmar205 and(not rel.AsEvent_16._IsWronglyPrinted)
                or
                (not bIsTicketRegisterEmar205)and(not rel.AsEvent_16._IsWrong)and(not __isEmar105CardPayment(rel, iRecord)) then
                Inc(Result, rel.AsEvent_16.TicketPrice - rel.AsEvent_16._NonCashInTicketPrice);
            end;
          21:
            begin
              if bIsTicketRegisterEmar205 and(not rel.AsEvent_21._IsWronglyPrinted)
                or
                (not bIsTicketRegisterEmar205)and(not rel.AsEvent_21._IsWrong)and(not __isEmar105CardPayment(rel, iRecord)) then
                Inc(Result, rel.AsEvent_21.Price       - rel.AsEvent_21._NonCashInTicketPrice);
            end;
          30:
            begin
              if bIsTicketRegisterEmar205 and(not rel.AsEvent_30._IsWronglyPrinted)
                or
                (not bIsTicketRegisterEmar205)and(not rel.AsEvent_30._IsWrong)and(not __isEmar105CardPayment(rel, iRecord)) then
                Inc(Result, rel.AsEvent_30.TicketPrice - rel.AsEvent_30._NonCashInTicketPrice);
            end;
          32:
            begin
              if (not rel.AsEvent_32.IsDuplicated)
                and(bIsTicketRegisterEmar205 or (not bIsTicketRegisterEmar205)and(not __isEmar105CardPayment(rel, iRecord))) then
              begin
                if rel.AsEvent_32.InCountry then
                  Inc(Result, rel.AsEvent_32.Brutto1 - rel.AsEvent_32.Reduce1 - rel.AsEvent_32._NonCashInTicketPrice)
                else
                  Inc(Result, rel.AsEvent_32.Brutto2 - rel.AsEvent_32.Reduce2 - rel.AsEvent_32._NonCashInTicketPrice);
              end;
            end;
        end;
      end;

      Inc(iRecord);
    end;
  end;
end;

function TEmar105_File._LoadOtherParts(aStream: TStream): longword;
begin
  // jeśli nie jest to zbiór A80, a jest C*.DAT lub K*.DAT,
  if Pos('A80', AnsiUpperCase(ExtractFileName(fFileName))) <> 1 then begin
    Result := TEmar105_ReportEventList(fReportList).LoadFromStream(aStream);
    if (Result = ERR_NO_ERROR) then
      if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_OIKReaded, 0) then begin
        Result := ERR_USER_TERMINATE;
        Exit;
      end;
  end
  else Result := ERR_NO_ERROR;
end;

function TEmar105_File.DeviceClose(aLedsOff: boolean = false): longword;
begin
  if fUsbDevice.IsOpened then Result := fUsbDevice.Close(aLedsOff)
  else Result := ERR_NO_ERROR;
end;

function TEmar105_File.DeviceGetReport(aA80FileName: PChar): longword;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        Result := ERR_USB_DEVICE_NO_MEMORY;
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_REGISTERING, nil, True);
          if Result <> ERR_NO_ERROR then Exit;

          if (aA80FileName = nil) or not FileExists(aA80FileName) then Result := LoadAFileFromDevice
          else begin
            Result := LoadFromFile(aA80FileName);
            if Result = ERR_NO_ERROR then begin
              Result := ERR_USER_TERMINATE;
              fUSBStream.Clear;
              // Odczyt FAT2 z karty
              Fat.Nr := 2;
              Fat.LoadFromBuffer(fUSBStream);
              if fBreak then Exit;

              Fat.Nr := 1;
              Dir.LoadFromBuffer(fUSBStream);
              if fBreak then Exit;

              // Odczyt danych dodatkowych z karty

              // $15 = 21 - Przeliczniki walut – dane dodatkowe
              if fCurrencyExchangeList.Required then begin
                LoadList(fCurrencyExchangeList, fUSBStream);
                if fBreak then Exit;
              end;

              // $18 = 24 - Zadania – dane dodatkowe
              if fTaskList.Required then begin
                LoadList(fTaskList, fUSBStream);
                if fBreak then Exit;
              end;

              // $19 = 25 - Pozycje zadań – dane dodatkowe
              if fTaskPositionList.Required then begin
                LoadList(fTaskPositionList, fUSBStream);
                if fBreak then Exit;
              end;

              // $20 = 32 - Wykaz firm rozliczających przewozy pasażerów z biletami miesięcznymi – dane dodatkowe
              if fAcceptedTicketOwnerList.Required then begin
                LoadList(fAcceptedTicketOwnerList, fUSBStream);
                if fBreak then Exit;
              end;

              // $21 = 33 - Wykaz firm wydających akceptowane przez bileterkę karty pasażerów z ulgą handlową – dane dodatkowe
              if fAcceptedTradeReliefCardOwnerList.Required then begin
                LoadList(fAcceptedTradeReliefCardOwnerList, fUSBStream);
                if fBreak then Exit;
              end;

              // $22 = 34 - Wykaz zastrzeżonych kart MIFARE – dane dodatkowe
              if fProprietaryMIFAREcardList.Required then begin
                LoadList(fProprietaryMIFAREcardList, fUSBStream);
                if fBreak then Exit;
              end;

              // $27 = 39 - Przeliczniki walut po zmianie waluty cennika
              if fExchangeRateAfterChangeCurrencyList.Required then begin
                LoadList(fExchangeRateAfterChangeCurrencyList, fUSBStream);
                if fBreak then Exit;
              end;

              // $28 = 40 - Wykaz kart MIFARE z biletami do przedłużenia / sprzedaży na następny okres – dane dodatkowe
              if fTicketNextPeriodList.Required then begin
                LoadList(fTicketNextPeriodList, fUSBStream);
                if fBreak then Exit;
              end;

              // $29 = 41 - Wykaz skrótów klawiszowych do funkcji bileterki – dane dodatkowe
              if fShortcutList.Required then begin
                LoadList(fShortcutList, fUSBStream);
                if fBreak then Exit;
              end;

              // $2A = 42 - Wykaz firm wydających akceptowane przez bileterkę karty kontrolerów – dane dodatkowe
              if fAcceptedInspectorsCompanyList.Required then begin
                LoadList(fAcceptedInspectorsCompanyList, fUSBStream);
                if fBreak then Exit;
              end;

              // $30 = 48 - Kierowcy (solobus)
              if fDriverList.Required then begin
                LoadList(fDriverList, fUSBStream);
                if fBreak then Exit;
              end;

              Result := ERR_NO_ERROR;
            end;

            if not Result = ERR_NO_ERROR then Exit;
          end;

          if fReportStartedRides.Required then begin
            LoadList(fReportStartedRides, fUSBStream);
            if fBreak then Exit;
          end;

          Result := TEmar105_ReportEventList(fReportList).LoadFromStream(fUSBStream);

          // callback aby sprawdzić numer karty i kierowcy
          if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_OIKReaded, 0) then begin
            Result := ERR_USER_TERMINATE;
            Exit;
          end;
        end;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceIsDriverCard(aDriverCardSerialNo: pchar): longword;
var
  s: string;
  iDeviceCardSerialNumber: Cardinal;
begin
  Result := GetDeviceCardSerialNumber(iDeviceCardSerialNumber);
  if Result = ERR_NO_ERROR then
  begin
    s := Format('%u', [iDeviceCardSerialNumber]);
    SysUtils.StrPCopy(aDriverCardSerialNo, s);
  end;
end;

function TEmar105_File.DeviceIsOpened: boolean;
begin
  Result := fUsbDevice.IsOpened;
end;

function TEmar105_File.DeviceIsReport(aBufferForTimeTableFileName: pchar; aBufferSize: longword): longword;
var
  lPage: integer;
  buff:  array of byte;
  s:     string;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          Result := ERR_USER_TERMINATE;
          fUSBStream.Clear;
          Fat.LoadFromBuffer(fUSBStream);
          if fBreak then Exit;
          lPage := Fat.IndexOfFirstPage(101);
          if lPage >= 0 then begin
            SetLength(buff, fUsbDevice.MemoryPageLength);
            fUSBStream.Seek(lPage);
            fUSBStream.read(buff[0], fUsbDevice.MemoryPageLength);
            if fBreak then Exit;
            if buff[39] <> $FF then begin
              TEmar105_OIK(fOik).Nr := 1;
              Result := fUSBStream.ReloadPageFromDevice(TEmar105_OIK(fOik).fPageNr); // OIK1    8
              if Result = ERR_NO_ERROR then
              begin
                TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
                if TEmar105_OIK(fOik).CardSerialNumber = $FFFFFFFF then
                begin
                  TEmar105_OIK(fOik).Nr := 2;
                  Result := fUSBStream.ReloadPageFromDevice(TEmar105_OIK(fOik).fPageNr); // OIK2 4087
                  if Result = ERR_NO_ERROR then
                  begin
                    TEmar105_OIK(fOik).Nr := 2;
                    TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
                    TEmar105_OIK(fOik).Nr := 1;
                  end;
                end;
              end;
              if fBreak then Exit;
              s := OIK.TimeTableFileName + '.' + OIK.TimeTableFileExt;
              if cardinal(Length(s)) < aBufferSize then begin
                StrPCopy(aBufferForTimeTableFileName, s);
                Result := ERR_NO_ERROR;
              end
              else Result := ERR_BUFFER_TOO_SMALL;
            end
            else Result := ERR_REPORT_NO_REPORT;
          end
          else Result := ERR_REPORT_NO_REPORT;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.GetDevice00ReportCode(var aReportCode: pchar): longword;
var
  lPage:       integer;
  buff:        array of byte;
  sReportCode: string;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          Result := ERR_USER_TERMINATE;
          fUSBStream.Clear;
          Fat.LoadFromBuffer(fUSBStream);
          if fBreak then Exit;
          lPage := Fat.IndexOfFirstPage(101);
          if lPage >= 0 then begin
            SetLength(buff, fUsbDevice.MemoryPageLength);
            fUSBStream.Seek(lPage);
            fUSBStream.Read(buff[0], fUsbDevice.MemoryPageLength);
            if fBreak then Exit;
            if buff[39] = $FF then Result := ERR_REPORT_NO_REPORT
            else Result := ERR_NO_ERROR;
            SetString(sReportCode, PAnsiChar(@buff[11]), 4);
            aReportCode := PChar(sReportCode);
          end
          else Result := ERR_REPORT_NO_REPORT;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.GetDeviceCardSerialNumber(var aCardSerialNumber: Cardinal): LongWord;
var
  lPage:       integer;
  buff:        array of byte;
  fs: TMemoryStream;
  fPage:     TEmarPage528;
  p: PEmar105_OIK_v7;
begin
  aCardSerialNumber := $FFFFFFFF;
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          Result := ERR_USER_TERMINATE;

          fUsbDevice.RedLED(True); // wait
          SetLength(buff, fUsbDevice.MemoryPageLength);
          fs := TMemoryStream.Create;
          try
            lPage := 8{OIK1};
            if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
            begin
              fs.write(buff[0], fUsbDevice.MemoryPageLength);
              if fs.Size > 0 then
              begin
                FillChar(fPage.aContent[0], 512, $FF);
                Move(buff[0], fPage.aContent[0], 512);

                p := @fPage.aContent[0];
                aCardSerialNumber := CalcCardinal(p^.CardSerialNumber);

                if (Result <> 0)and(aCardSerialNumber <> $FFFFFFFF) then
                  Result := ERR_NO_ERROR;
              end
              else // try to read from OIK2
              begin
                lPage := 4087{OIK2};
                if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
                begin
                  fs.write(buff[0], fUsbDevice.MemoryPageLength);
                  if fs.Size > 0 then
                  begin
                    FillChar(fPage.aContent[0], 512, $FF);
                    Move(buff[0], fPage.aContent[0], 512);

                    p := @fPage.aContent[0];
                    aCardSerialNumber := CalcCardinal(p^.CardSerialNumber);

                    if (Result <> 0)and(aCardSerialNumber <> $FFFFFFFF) then
                      Result := ERR_NO_ERROR;
                  end;
                end;
              end;
            end
            else begin
              fs.Size := 0;
              Result := ERR_USB_DEVICE_READ;
            end;
          finally
            buff := nil;
            fs.Free;
            fUsbDevice.RedLED(False); // wait
          end;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceOpen(aDevicePath: pchar): longword;
begin
  Result := fUsbDevice.Open(aDevicePath);
end;

function TEmar105_File.DeviceReadAll(aFileName: pchar): longword;
var
  fs:     TMemoryStream;
  buf:    array of byte;
  lBreak: LongBool;
  i:      integer;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_REGISTERING, nil, True);
          if Result <> ERR_NO_ERROR then Exit;

          fUsbDevice.RedLED(True); // wait
          SetLength(buf, fUsbDevice.MemoryPageLength);
          fs := TMemoryStream.Create;
          try
            for i := 0 to fUsbDevice.MemoryPageCount - 1 do begin
              lBreak := false;
              if Assigned(fCallback) then fCallback(self, EMAR105CallbackKind_PageRead, i, lBreak);
              if lBreak then begin
                Result := ERR_USER_TERMINATE;
                fs.Size := 0;
                Break;
              end else begin
                if fUsbDevice.PageRead(i, buf[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
                    fs.write(buf[0], fUsbDevice.MemoryPageLength)
                else begin
                  fs.Size := 0;
                  Result := ERR_USB_DEVICE_READ;
                end;
              end;
            end;
          finally
            buf := nil;
            if fs.Size > 0 then fs.SaveToFile(aFileName);
            fs.Free;
            fUsbDevice.RedLED(False); // wait
          end;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceReportErase(aEraseExtraData: LongBool; aNextReportCode: pchar): longword;
var
  fId:                                                set of byte;
  i, j, p, ix, minpage, maxpage, i100x101, iNotEmpty: integer;
  ev_00:                                              IEmar_ReportEvent_00;
  dNow:                                               TDateTime;
begin
  EmarLog('TEmar105_File.DeviceReportErase - start');
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      EmarLog('TEmar105_File.DeviceReportErase - GetDeviceParams');
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          fUsbDevice.RedLED(True); // wait
          EmarLog('TEmar105_File.DeviceReportErase - RedLed: On');
          try
            Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_ERASING, aNextReportCode, true);
            EmarLog('TEmar105_File.DeviceReportErase - set OIK.CardReadyCode to $51');
            if Result <> ERR_NO_ERROR then Exit;

            Fat.Nr := 2;
            Fat.LoadFromBuffer(fUSBStream);
            EmarLog('TEmar105_File.DeviceReportErase - Load FAT2');
            if fBreak then begin
              Result := ERR_USER_TERMINATE;
              EmarLog('TEmar105_File.DeviceReportErase - exit: ERR_USER_TERMINATE.');
              Exit;
            end;
            if aEraseExtraData then fId := C_SET_OF_ADD_DATA_TABLE_INDEXES + [100, 101]
            else fId := [100, 101];
            p := - 1;
            i100x101 := - 1;
            iNotEmpty := 10;
            for i := 11 to fUsbDevice.MemoryPageCount - 11 do
            begin
              if Fat.PageId[i] in fId then begin
                if p = - 1 then p := i;
                if Fat.PageId[i] in [100, 101] then i100x101 := i;
                if i100x101 <> - 1 then // dopóki nie znajdziemy
                    Break;
                if Fat.PageId[i] <> $FF then
                  iNotEmpty := i;
              end;
            end;
            // in case there was not either 100 and 101 pages
            if i100x101 = -1 then
            begin
              i100x101 := iNotEmpty + 1;
              Fat.PageId[i100x101] := 100;
              Fat.PageId[i100x101 + 1] := 101;
            end;

            while (p > 0) and (Result = ERR_NO_ERROR) do begin
              if (p mod integer(fUsbDevice.MemoryBlockPageCount) = 0) and
                (p + 8 < integer(fUsbDevice.MemoryPageCount - 10)) then begin
                EmarLog('TEmar105_File.DeviceReportErase - BlockClear: ' + IntToStr(p));
                if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_BlockClear, p) then begin
                  Result := ERR_USER_TERMINATE;
                  EmarLog('TEmar105_File.DeviceReportErase - exit: ERR_USER_TERMINATE.');
                  Exit;
                end;
                Result := fUsbDevice.BlockClear(p);
                Inc(p, fUsbDevice.MemoryBlockPageCount);
              end else begin
                EmarLog('TEmar105_File.DeviceReportErase - PageClear: ' + IntToStr(p));
                if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_PageClear, p) then begin
                  Result := ERR_USER_TERMINATE;
                  EmarLog('TEmar105_File.DeviceReportErase - exit: ERR_USER_TERMINATE.');
                  Exit;
                end;
                Result := fUsbDevice.PageClear(p);
                Inc(p);
              end;
              if (p >= integer(fUsbDevice.MemoryPageCount)) then Break;
            end;

            Fat.Nr := 1;
            Fat.LoadFromBuffer(fUSBStream);
            Dir.Nr := 1;
            Dir.LoadFromBuffer(fUSBStream);
            fUSBStream.SaveImmediately := False;
            if aEraseExtraData then begin
              EmarLog('TEmar105_File.DeviceReportErase - clear additional data');
              minpage := 4096;
              maxpage := 0;
              // Usuwanie z FAT i DIR wpisów danych dodatkowych i raportu (100,101)
              for i := 11 to 4085 do begin
                if Fat.PageId[i] in C_SET_OF_ADD_DATA_TABLE_INDEXES then begin
                  j := Dir.IndexOf(Fat.PageId[i]);
                  if j >= 0 then Dir.Delete(j);
                  if minpage > i then minpage := i;
                  if maxpage < i then maxpage := i;
                  Fat.PageId[i] := $FF;
                end;
              end;
              // czyszczenie zajmowanego miejsca przez stare DD na karcie
              i := (maxpage div 8 + 1) * 8;
              if i < 4086 then maxpage := i
              else Inc(maxpage);
              while ((minpage mod 8) <> 0) and (minpage < maxpage) do begin
                fUsbDevice.PageClear(minpage);
                Inc(minpage);
              end;
              while (minpage + 8 <= maxpage) do begin
                fUsbDevice.BlockClear(minpage);
                Inc(minpage, 8);
              end;
              while (minpage < maxpage) do begin
                fUsbDevice.PageClear(minpage);
                Inc(minpage);
              end;
            end;

            minpage := 4096;
            maxpage := 0;
            // Usuwanie z FAT i DIR wpisów danych dodatkowych i raportu (100,101)
            for i := 258 to 4085 do begin
              if Fat.PageId[i] in [100, 101] then begin
                j := Dir.IndexOf(Fat.PageId[i]);
                if j >= 0 then Dir.Delete(j);
                if minpage > i then minpage := i;
                if maxpage < i then maxpage := i;
                Fat.PageId[i] := $FF;
              end;
            end;
            // czyszczenie zajmowanego miejsca przez stare DD na karcie
            i := (maxpage div 8 + 1) * 8;
            if i < 4086 then maxpage := i
            else Inc(maxpage);
            while ((minpage mod 8) <> 0) and (minpage < maxpage) do begin
              fUsbDevice.PageClear(minpage);
              Inc(minpage);
            end;
            while (minpage + 8 <= maxpage) do begin
              fUsbDevice.BlockClear(minpage);
              Inc(minpage, 8);
            end;
            while (minpage < maxpage) do begin
              fUsbDevice.PageClear(minpage);
              Inc(minpage);
            end;

            // zawsze czyścimy zawartość stron 100-101 oraz ustawiamy tylko po jednej 100 i 101
            ix := Dir.IndexOf(100);
            if ix = - 1 then begin
              with Dir.AddItem(100) do begin
                FirstPage := i100x101;
                RecLength := 255;
                RecCount := 0;
                Version := _RecordVersion(Self.Version, Id);
              end;
            end
            else Dir[ix].FirstPage := i100x101;
            Fat.PageId[i100x101] := 100;
            ix := Dir.IndexOf(101);
            if ix = - 1 then begin
              with Dir.AddItem(101) do begin
                FirstPage := i100x101 + 1;
                RecLength := 39;
                RecCount := 0;
                Version := _RecordVersion(Self.Version, Id);
              end;
            end
            else Dir[ix].FirstPage := i100x101 + 1;
            Fat.PageId[i100x101 + 1] := 101;
            // 100-101

            // aktualizacja FAT1 i DIR1
            Fat.SaveToBuffer(fUSBStream);
            Dir.SaveToBuffer(fUSBStream);

            // aktualizacja FAT2 i DIR2
            Fat.Nr := 2;
            Fat.SaveToBuffer(fUSBStream);
            Dir.Nr := 2;
            Dir.SaveToBuffer(fUSBStream);

            fUSBStream.UpdateFlash;

            if { not aEraseExtraData and }Assigned(aNextReportCode) and (string(aNextReportCode) <> '') then begin
              EmarLog('TEmar105_File.DeviceReportErase - set first pages for $64 and $65, add record with VAT rates');
              Fat.Nr := 1;
              Fat.LoadFromBuffer(fUSBStream);
              Dir.Nr := 1;
              Dir.LoadFromBuffer(fUSBStream);
              TEmar105_Consts(Consts).LoadFromBuffer(fUSBStream);
              fUSBStream.Clear;
              fUSBStream.SaveImmediately := false;
              fReportStartedRides.Clear; // strona 100
              fReportList.Clear;         // strona 101
              ev_00 := fReportList.addItem(0) as IEmar_ReportEvent_00;
              dNow := Now();
              ev_00.EventDate := pchar(DateToStr(dNow));
              ev_00.EventTime := pchar(TimeToStr(dNow));
              ev_00.ReportCode := aNextReportCode;

              if (string(Consts.PTU2ValidFrom) <> '') and (StrToDate(Consts.PTU2ValidFrom) <= Int(dNow)) then begin
                ev_00.TaxRates[1] := Consts.RatePTU2_A;
                ev_00.TaxRates[2] := Consts.RatePTU2_B;
                ev_00.TaxRates[3] := Consts.RatePTU2_C;
                ev_00.TaxRates[4] := Consts.RatePTU2_D;
                ev_00.TaxRates[5] := Consts.RatePTU2_E;
                ev_00.TaxRates[6] := Consts.RatePTU2_F;
                ev_00.TaxRates[7] := Consts.RatePTU2_G;
              end else begin
                ev_00.TaxRates[1] := Consts.RatePTU1_A;
                ev_00.TaxRates[2] := Consts.RatePTU1_B;
                ev_00.TaxRates[3] := Consts.RatePTU1_C;
                ev_00.TaxRates[4] := Consts.RatePTU1_D;
                ev_00.TaxRates[5] := Consts.RatePTU1_E;
                ev_00.TaxRates[6] := Consts.RatePTU1_F;
                ev_00.TaxRates[7] := Consts.RatePTU1_G;
              end;
              ix := Dir.IndexOf(101);
              if ix = - 1 then begin
                Fat.PageId[i100x101 + 1] := $FF;
                TEmar105_ReportEventList(fReportList).SaveToStream(fUSBStream, i100x101 + 1);
              end else begin
                Fat.PageId[Dir[ix].FirstPage] := $FF;
                TEmar105_ReportEventList(fReportList).SaveToStream(fUSBStream, Dir[ix].FirstPage);
              end;
              Fat.SaveToBuffer(fUSBStream);
              Dir.SaveToBuffer(fUSBStream);
              Fat.Nr := 2;
              Dir.Nr := 2;
              Fat.SaveToBuffer(fUSBStream);
              Dir.SaveToBuffer(fUSBStream);
              // UWAGA: zostają śmieciowe strony 100 oraz 101
              fUSBStream.UpdateFlash;
            end;
            // Result := SetOIKCardState(EMAR105_CARD_READY_CODE_READY, true);
          finally
            fUsbDevice.RedLED(False); // wait
            EmarLog('TEmar105_File.DeviceReportErase - RedLed: off');
          end;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
  EmarLog(Format('TEmar105_File.DeviceReportErase - end. Result $%.8X (%d)',[Result, Result]));
end;

function TEmar105_File.DeviceWriteAll(aFileName: pchar; aParams: pointer): longword;
var
  fs: TMemoryStream;
  i:  integer;
  p:  pointer;
  pp: PEmarPage528;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          if FileExists(aFileName) then begin
            fs := TMemoryStream.Create;
            try
              fs.LoadFromFile(aFileName);
              if fs.Size = fUsbDevice.MemoryPageLength * fUsbDevice.MemoryPageCount then begin
                fBreak := false;
                for i := 0 to fUsbDevice.MemoryPageCount - 1 do begin
                  p := pointer(cardinal(fs.Memory) + cardinal(i) * fUsbDevice.MemoryPageLength);
                  StreamOnBeforePageWrite(USBStream, i, fBreak);
                  if fBreak then Break;
                  pp := p;
                  if (i > 4088) or (pp^.aContent[0] in [100, 101]) then
                      FillPageCtrlBytes(pp^, pp^.aContent[0], i, $FFFF, $FFFF);
                  Result := fUsbDevice.PageWrite(i, p^, fUsbDevice.MemoryPageLength);
                  if Result <> ERR_NO_ERROR then Exit;
                end;
                if fBreak then Result := ERR_USER_TERMINATE
                else Result := ERR_NO_ERROR;
              end
              else Result := ERR_INCORRECT_FILE;
            finally
              fs.Free;
            end;
          end
          else Result := ERR_FILE_NOT_FOUND;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceWriteFile(aFileName: pchar; aParams: pointer): longword;
var
  fn, fe:          string;
  ev_00:           IEmar_ReportEvent_00;
  pNextReportCode: PChar;
  dNow:            TDateTime;
  ix:              Integer;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          fUsbDevice.RedLED(True); // wait

          fUSBStream.Clear;
          fUSBStream.SaveImmediately := false;
          try
            Clear;
            Result := LoadFromFile(aFileName);
            if Result = ERR_NO_ERROR then begin
              TEmar105_OIK(OIK).Nr := 1;
              fUSBStream.Seek(TEmar105_OIK(OIK).fPageNr); // OIK1    8
              if Result = ERR_NO_ERROR then
              begin
                TEmar105_OIK(OIK).LoadFromBuffer(fUSBStream);
                if TEmar105_OIK(OIK).CardSerialNumber = $FFFFFFFF then
                begin
                  TEmar105_OIK(fOik).Nr := 2;
                  Result := fUSBStream.ReloadPageFromDevice(TEmar105_OIK(fOik).fPageNr); // OIK2 4087
                  if Result = ERR_NO_ERROR then
                  begin
                    TEmar105_OIK(OIK).Nr := 2;
                    TEmar105_OIK(OIK).LoadFromBuffer(fUSBStream);
                    TEmar105_OIK(OIK).Nr := 1;
                  end;
                end;
              end;
              pNextReportCode := TEmar105_OIK(OIK).NextReportCode;
              fBreak := false;

              fReportList.Clear;
              ev_00 := fReportList.addItem(0) as IEmar_ReportEvent_00;
              dNow := Now();
              ev_00.EventDate := pchar(DateToStr(dNow));
              ev_00.EventTime := pchar(TimeToStr(dNow));
              ev_00.ReportCode := pNextReportCode;

              if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_Prepare101Record, 0) then begin
                Result := ERR_USER_TERMINATE;
                Exit;
              end;
              // AT: Ewentualnie zostawiamy do tej pory dopóki nie zaimplementujemy funkcje DeviceChangeStatus
              if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_ChangeOIKStatuses, 0) then begin
                Result := ERR_USER_TERMINATE;
                Exit;
              end;
              if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_PrepareOIK, 0) then begin
                Result := ERR_USER_TERMINATE;
                Exit;
              end;
              if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_PrepareAddData, 0) then begin
                Result := ERR_USER_TERMINATE;
                Exit;
              end;
              fn := ExtractFileName(aFileName);
              fe := ExtractFileExt(fn); // zwraca rozszerzenie z kropką (np.: .DAT)
              if fe <> '' then begin
                fn := Copy(fn, 1, Length(fn) - Length(fe));
                Delete(fe, 1, 1); // usuwa kropki
              end;

              Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_PROGRAMMING, nil, false{!!!});
              if Result = ERR_NO_ERROR then begin
                fSaveMode := EMAR_SAVEMODE_PROGRAMMING;
                Result := SaveToStream(fUSBStream, Version);
                if Result = ERR_NO_ERROR then begin
                  Dir.Nr := 2;
                  Dir.SaveToBuffer(fUSBStream);
                  if fBreak then begin
                    Result := ERR_USER_TERMINATE;
                    Exit;
                  end;
                  Fat.Nr := 2;
                  Fat.SaveToBuffer(fUSBStream);
                  if fBreak then begin
                    Result := ERR_USER_TERMINATE;
                    Exit;
                  end;
                  // Zmieniamy nazwę zbioru wyłącznie po pełnym programowaniu karty
                  TEmar105_OIK(OIK).TimeTableFileName := pchar(fn);
                  TEmar105_OIK(OIK).TimeTableFileExt := pchar(fe);
                  TEmar105_OIK(OIK).TimeTableSaveFileDate := pchar(DateToStr(dNow));
                  TEmar105_OIK(OIK).TimeTableSaveFileTime := pchar(TimeToStr(dNow));

                  // status 85 - gotowa do pracy
                  TEmar105_OIK(OIK).ReadyCode := EMAR105_CARD_READY_CODE_READY;

                  TEmar105_OIK(OIK).Nr := 1;
                  USBStream.Seek(TEmar105_OIK(OIK).fPageNr);
                  TEmar105_OIK(OIK).SaveToBuffer(fUSBStream);

                  TEmar105_OIK(OIK).Nr := 2;
                  USBStream.Seek(TEmar105_OIK(OIK).fPageNr);
                  TEmar105_OIK(OIK).SaveToBuffer(fUSBStream);

                  TEmar105_OIK(OIK).Nr := 1;

                  if fReportList.Required and (fSaveMode <> EMAR_SAVEMODE_FILE_A) then begin
                    ix := Dir.IndexOf(101);
                    if ix > - 1 then begin
                      Fat.PageId[Dir[ix].FirstPage] := $FF;
                      TEmar105_ReportEventList(fReportList).SaveToStream(fUSBStream, Dir[ix].FirstPage);
                    end;
                  end;

                  fBreak := false;
                  fUSBStream.UpdateFlashAndClearNotUsedPages(9, 4086);
                  if fBreak then begin
                    Result := ERR_USER_TERMINATE;
                    Exit;
                  end;
                  // Result := SetOIKCardState(EMAR105_CARD_READY_CODE_READY, false);
                  Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_READY, nil, True);
                end;
              end;
            end;
          finally
            fUSBStream.SaveImmediately := false;
            fUsbDevice.RedLED(False); // wait
          end;
        end
        else Result := ERR_USB_DEVICE_NO_MEMORY;
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceChangeStatus(aParams: pointer): longword;
var
  iOldOIKNr: Byte;
begin
  Result := ERR_NO_ERROR;
  iOldOIKNr := TEmar105_OIK(fOik).Nr;
  try
    fUSBStream.Clear;
    EmarLog('TEmar105_File.DeviceChangeStatus nr 1 - BEFORE');
    TEmar105_OIK(fOik).Nr := 1;
    TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
    if TEmar105_OIK(fOik).CardSerialNumber = $FFFFFFFF then
    begin
      TEmar105_OIK(fOik).Nr := 2;
      TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
      TEmar105_OIK(fOik).Nr := 1;
    end;
    if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_PrepareOIK, 0) then begin
      Result := ERR_USER_TERMINATE;
      Exit;
    end;
    EmarLog('TEmar105_File.DeviceChangeStatus nr 1 - AFTER');
    fUSBStream.Seek(TEmar105_OIK(fOik).fPageNr);
    TEmar105_OIK(fOik).SaveToBuffer(fUSBStream);
    TEmar105_OIK(OIK).ForceUpdateFlash();
  finally
    TEmar105_OIK(fOik).Nr := iOldOIKNr;
  end;
end;

function TEmar105_File.DeviceSetReadBy(aParams: pointer): longword;
var
  iOldOIKNr: Byte;
begin
  Result := ERR_NO_ERROR;
  iOldOIKNr := TEmar105_OIK(fOik).Nr;
  try
    //fUSBStream.Clear;
    TEmar105_OIK(fOik).Nr := 1;
    fUSBStream.Seek(TEmar105_OIK(fOik).fPageNr);
    TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
    if TEmar105_OIK(fOik).CardSerialNumber = $FFFFFFFF then
    begin
      TEmar105_OIK(fOik).Nr := 2;
      TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
      TEmar105_OIK(fOik).Nr := 1;
    end;
    if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_SetOIKReadBy, 0) then begin
      Result := ERR_USER_TERMINATE;
      Exit;
    end;
    fUSBStream.Seek(TEmar105_OIK(fOik).fPageNr);
    TEmar105_OIK(fOik).SaveToBuffer(fUSBStream);
    TEmar105_OIK(OIK).ForceUpdateFlash();
  finally
    TEmar105_OIK(fOik).Nr := iOldOIKNr;
  end;
end;

function TEmar105_File.DeviceUpdateAddData(aParams: pointer): longword;
var
  i, j, minpage, maxpage: integer;
  dd:                     set of byte;
  ev_00:                  IEmar_ReportEvent_00;
  pNextReportCode:        PChar;
  dNow:                   TDateTime;
begin
  Result := ERR_USER_TERMINATE;

  fUSBStream.Clear;
  // odczyt FAT1 i DIR1
  Dir.Nr := 1;
  Dir.LoadFromBuffer(fUSBStream);
  Fat.Nr := 1;
  Fat.LoadFromBuffer(fUSBStream);
  TEmar105_Consts(fConsts).LoadFromBuffer(fUSBStream);

  TEmar105_OIK(OIK).Nr := 1;
  TEmar105_OIK(OIK).LoadFromBuffer(fUSBStream);
  pNextReportCode := TEmar105_OIK(OIK).NextReportCode;

  fReportList.Clear;
  ev_00 := fReportList.addItem(0) as IEmar_ReportEvent_00;
  dNow := Now();
  ev_00.EventDate := pchar(DateToStr(dNow));
  ev_00.EventTime := pchar(TimeToStr(dNow));
  ev_00.ReportCode := pNextReportCode;

  // odczyt danych z bazy
  if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_Prepare101Record, 0) then begin
    Result := ERR_USER_TERMINATE;
    Exit;
  end;
  // w EMAR105CallbackKind_PrepareAddData zmienia sie również OIK
  if DoCallbackAndBreakIfNeed(EMAR105CallbackKind_PrepareAddData, 0) then begin
    Result := ERR_USER_TERMINATE;
    Exit;
  end;

  minpage := 4096;
  maxpage := 0;
  dd := C_SET_OF_ADD_DATA_TABLE_INDEXES + [100, 101];
  // Usuwanie z FAT i DIR wpisy danych dodatkowych i raportu (100,101)
  for i := 11 to 4085 do begin
    if Fat.PageId[i] in dd then begin
      j := Dir.IndexOf(Fat.PageId[i]);
      if j >= 0 then Dir.Delete(j);
      if minpage > i then minpage := i;
      if maxpage < i then maxpage := i;
      Fat.PageId[i] := $FF;
    end;
  end;
  // czyścienie zajmowane miejsce przez stare DD w karcie
  i := (maxpage div 8 + 1) * 8;
  if i < 4086 then maxpage := i
  else Inc(maxpage);
  while ((minpage mod 8) <> 0) and (minpage < maxpage) do begin
    fUsbDevice.PageClear(minpage);
    Inc(minpage);
  end;
  while (minpage + 8 <= maxpage) do begin
    fUsbDevice.BlockClear(minpage);
    Inc(minpage, 8);
  end;
  while (minpage < maxpage) do begin
    fUsbDevice.PageClear(minpage);
    Inc(minpage);
  end;
  // zapis nowych DD do stream
  fUSBStream.SaveImmediately := false;
  fAtPageNumber := Fat.IndexOfFirstEmptyPage;
  fUSBStream.Seek(fAtPageNumber);
  // $15 = 21 - Przeliczniki walut – dane dodatkowe
  if fCurrencyExchangeList.Required then begin
    SaveList(fCurrencyExchangeList, fUSBStream);
    if fBreak then Exit;
  end;
  // $18 = 24 - Zadania – dane dodatkowe
  if fTaskList.Required then begin
    SaveList(fTaskList, fUSBStream);
    if fBreak then Exit;
  end;
  // $19 = 25 - Pozycje zadań – dane dodatkowe
  if fTaskPositionList.Required then begin
    SaveList(fTaskPositionList, fUSBStream);
    if fBreak then Exit;
  end;
  // $20 = 32 - Wykaz firm rozliczających przewozy pasażerów z biletami miesięcznymi – dane dodatkowe
  if fAcceptedTicketOwnerList.Required then begin
    SaveList(fAcceptedTicketOwnerList, fUSBStream);
    if fBreak then Exit;
  end;
  // $21 = 33 - Wykaz firm wydających akceptowane przez bileterkę karty pasażerów z ulgą handlową – dane dodatkowe
  if fAcceptedTradeReliefCardOwnerList.Required then begin
    SaveList(fAcceptedTradeReliefCardOwnerList, fUSBStream);
    if fBreak then Exit;
  end;
  // $22 = 34 - Wykaz zastrzeżonych kart MIFARE – dane dodatkowe
  if fProprietaryMIFAREcardList.Required then begin
    SaveList(fProprietaryMIFAREcardList, fUSBStream);
    if fBreak then Exit;
  end;
  // $27 = 39 - Przeliczniki walut po zmianie waluty cennika
  if fExchangeRateAfterChangeCurrencyList.Required then begin
    SaveList(fExchangeRateAfterChangeCurrencyList, fUSBStream);
    if fBreak then Exit;
  end;
  // $28 = 40 - Wykaz kart MIFARE z biletami do przedłużenia / sprzedaży na następny okres – dane dodatkowe
  if fTicketNextPeriodList.Required then begin
    SaveList(fTicketNextPeriodList, fUSBStream);
    if fBreak then Exit;
  end;
  // $29 = 41 - Wykaz skrótów klawiszowych do funkcji bileterki – dane dodatkowe
  if fShortcutList.Required then begin
    SaveList(fShortcutList, fUSBStream);
    if fBreak then Exit;
  end;
  // $2A = 42 - Wykaz firm wydających akceptowane przez bileterkę karty kontrolerów – dane dodatkowe
  if fAcceptedInspectorsCompanyList.Required then begin
    SaveList(fAcceptedInspectorsCompanyList, fUSBStream);
    if fBreak then Exit;
  end;
  // $30 = 48 - Kierowcy (solobus)
  // if fDriverList.Required then begin
  // SaveList(fDriverList, fUSBStream);
  // if fBreak then
  // Exit;
  // end;
  if fEmar205TextsList.Required then begin
    SaveList(fEmar205TextsList, fUSBStream);
    if fBreak then Exit;
  end;
  if fEmar205WifiList.Required then begin
    SaveList(fEmar205WifiList, fUSBStream);
    if fBreak then Exit;
  end;

  if fReportStartedRides.Required then begin
    // od początku nowego sektora w pamięci (EMAR-105, EMAR-205 ??, ..)
    fAtPageNumber := (fAtPageNumber shr 8 + 1) shl 8;
    SaveList(fReportStartedRides, fUSBStream);
    if fBreak then Exit;
  end;

  // Raport
  if fReportList.Required then TEmar_ReportEventList(fReportList).SaveToStream(fUSBStream, fAtPageNumber);

  // aktualizacja FAT1 i DIR1
  Fat.SaveToBuffer(fUSBStream);
  Dir.SaveToBuffer(fUSBStream);

  // aktualizacja FAT2 i DIR2
  Fat.Nr := 2;
  Fat.SaveToBuffer(fUSBStream);
  Dir.Nr := 2;
  Dir.SaveToBuffer(fUSBStream);

  // aktualizacja OIK1
  TEmar105_OIK(OIK).Nr := 1;
  fUSBStream.Seek(TEmar105_OIK(OIK).fPageNr);
  TEmar105_OIK(OIK).SaveToBuffer(fUSBStream);

  // aktualizacja OIK2
  TEmar105_OIK(OIK).Nr := 2;
  fUSBStream.Seek(TEmar105_OIK(OIK).fPageNr);
  TEmar105_OIK(OIK).SaveToBuffer(fUSBStream);

  TEmar105_OIK(OIK).Nr := 1;

  fUSBStream.UpdateFlash;

  Result := ERR_NO_ERROR;
end;

function TEmar105_File.DeviceReadyCode(): longword;
var
  lPage:       integer;
  buff:        array of byte;
  fs: TMemoryStream;
  fPage:     TEmarPage528;
  p: PEmar105_OIK_v7;
begin
  Result := 0;
  if fUsbDevice.IsOpened then
  begin
    if (fUsbDevice.GetDeviceParams = ERR_NO_ERROR)
      and(fUsbDevice.DeviceType = DevType_EMAR105)
      and(fUsbDevice.MemoryType = MemType_FLASH_2MB) then
    begin
      fUsbDevice.RedLED(True); // wait
      SetLength(buff, fUsbDevice.MemoryPageLength);
      fs := TMemoryStream.Create;
      try
        lPage := 8{OIK1};
        if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
        begin
          fs.write(buff[0], fUsbDevice.MemoryPageLength);
          if fs.Size > 0 then
          begin
            FillChar(fPage.aContent[0], 512, $FF);
            Move(buff[0], fPage.aContent[0], 512);

            p := @fPage.aContent[0];
            Result := p^.ReadyCode;
          end
          else // try to read from OIK2
          begin
            lPage := 4087{OIK2};
            if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
            begin
              fs.write(buff[0], fUsbDevice.MemoryPageLength);
              if fs.Size > 0 then
              begin
                FillChar(fPage.aContent[0], 512, $FF);
                Move(buff[0], fPage.aContent[0], 512);

                p := @fPage.aContent[0];
                Result := p^.ReadyCode;
              end;
            end;
          end;
        end
        else begin
          fs.Size := 0;
        end;
      finally
        buff := nil;
        fs.Free;
        fUsbDevice.RedLED(False); // wait
      end;
    end;
  end;
end;

function TEmar105_File.DeviceManufactureDate(): PChar;
var
  lPage:       integer;
  buff:        array of byte;
  fs: TMemoryStream;
  fPage:     TEmarPage528;
  p: PEmar105_OIK_v7;
begin
  Result := nil;
  if fUsbDevice.IsOpened then
  begin
    if (fUsbDevice.GetDeviceParams = ERR_NO_ERROR)
      and(fUsbDevice.DeviceType = DevType_EMAR105)
      and(fUsbDevice.MemoryType = MemType_FLASH_2MB) then
    begin
      fUsbDevice.RedLED(True); // wait
      SetLength(buff, fUsbDevice.MemoryPageLength);
      fs := TMemoryStream.Create;
      try
        lPage := 8{OIK1};
        if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
        begin
          fs.write(buff[0], fUsbDevice.MemoryPageLength);
          if fs.Size > 0 then
          begin
            FillChar(fPage.aContent[0], 512, $FF);
            Move(buff[0], fPage.aContent[0], 512);

            p := @fPage.aContent[0];
            Result := PChar(EmarDateToString(p^.ManufactureDate));
          end
          else // try to read from OIK2
          begin
            lPage := 4087{OIK2};
            if fUsbDevice.PageRead(lPage, buff[0], fUsbDevice.MemoryPageLength) = ERR_NO_ERROR then
            begin
              fs.write(buff[0], fUsbDevice.MemoryPageLength);
              if fs.Size > 0 then
              begin
                FillChar(fPage.aContent[0], 512, $FF);
                Move(buff[0], fPage.aContent[0], 512);

                p := @fPage.aContent[0];
                Result := PChar(EmarDateToString(p^.ManufactureDate));
              end;
            end;
          end;
        end
        else begin
          fs.Size := 0;
        end;
      finally
        buff := nil;
        fs.Free;
        fUsbDevice.RedLED(False); // wait
      end;
    end;
  end;
end;

function TEmar105_File.DeviceRollbackReadyCode(): longword;
begin
  if fUsbDevice.IsOpened then begin
    try
      Result := fUsbDevice.GetDeviceParams;
      if Result = ERR_NO_ERROR then begin
        Result := ERR_USB_DEVICE_NO_MEMORY;
        EmarLog(Format('TEmar105_File.DeviceRollbackReadyCode ReadyCode = %d', [Self.OIK.ReadyCode]));
        if (fUsbDevice.DeviceType = DevType_EMAR105) and (fUsbDevice.MemoryType = MemType_FLASH_2MB) then begin
          if _SavedReadyCode = 0 then // nie był zmieniany
              Result := ERR_NO_ERROR
          else Result := SetOIKReadyCodeNextReportCode(_SavedReadyCode, nil, True);
        end;
        EmarLog(Format('TEmar105_File.DeviceRollbackReadyCode ReadyCode = %d', [Self.OIK.ReadyCode]));
      end;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

function TEmar105_File.DeviceBeginProgramming(aNextReportCode: PChar): LongWord;
begin
  Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_PROGRAMMING, aNextReportCode, True);
end;

function TEmar105_File.DeviceEndProgramming(): LongWord;
begin
  Result := SetOIKReadyCodeNextReportCode(EMAR105_CARD_READY_CODE_READY, nil, True);
end;

function TEmar105_File._GetCalendarEnd: pchar;
begin
  if fCalEnd = '' then fCalEnd := Consts.CalendarEnd;
  Result := pchar(fCalEnd);
end;

function TEmar105_File._GetCurrentRatePTU(ds: TDateTime; aIndex: integer): integer;
begin
  if (Consts.PTU2ValidFrom <> '') and not (Int(StrToDate(Consts.PTU2ValidFrom)) > Int(ds)) then begin
    case aIndex of
    1: Result := _GetRatePTU2_A;
    2: Result := _GetRatePTU2_B;
    3: Result := _GetRatePTU2_C;
    4: Result := _GetRatePTU2_D;
    5: Result := _GetRatePTU2_E;
    6: Result := _GetRatePTU2_F;
    7: Result := _GetRatePTU2_G;
  else Result := fRatePTU_N;
    end;
  end else begin
    case aIndex of
    1: Result := _GetRatePTU1_A;
    2: Result := _GetRatePTU1_B;
    3: Result := _GetRatePTU1_C;
    4: Result := _GetRatePTU1_D;
    5: Result := _GetRatePTU1_E;
    6: Result := _GetRatePTU1_F;
    7: Result := _GetRatePTU1_G;
  else Result := fRatePTU_N;
    end;
  end;
end;

function TEmar105_File._GetMaxTicketPrice5: Integer;
begin
  if fMaxTicketPrice5 = 0 then fMaxTicketPrice5 := Consts.MaxTicketPrice5;
  Result := fMaxTicketPrice5;
end;

function TEmar105_File._GetRatePTU1_A: Integer;
begin
  if fRatePTU1_A = 0 then fRatePTU1_A := Consts.RatePTU1_A;
  Result := fRatePTU1_A;
end;

function TEmar105_File._GetRatePTU1_B: Integer;
begin
  if fRatePTU1_B = 0 then fRatePTU1_B := Consts.RatePTU1_B;
  Result := fRatePTU1_B;
end;

function TEmar105_File._GetRatePTU1_C: Integer;
begin
  if fRatePTU1_C = 0 then fRatePTU1_C := Consts.RatePTU1_C;
  Result := fRatePTU1_C;
end;

function TEmar105_File._GetRatePTU1_D: Integer;
begin
  if fRatePTU1_D = 0 then fRatePTU1_D := Consts.RatePTU1_D;
  Result := fRatePTU1_D;
end;

function TEmar105_File._GetRatePTU1_E: Integer;
begin
  if fRatePTU1_E = 0 then fRatePTU1_E := Consts.RatePTU1_E;
  Result := fRatePTU1_E;
end;

function TEmar105_File._GetRatePTU1_F: Integer;
begin
  if fRatePTU1_F = 0 then fRatePTU1_F := Consts.RatePTU1_F;
  Result := fRatePTU1_F;
end;

function TEmar105_File._GetRatePTU1_G: Integer;
begin
  if fRatePTU1_G = 0 then fRatePTU1_G := Consts.RatePTU1_G;
  Result := fRatePTU1_G;
end;

function TEmar105_File._GetRatePTU2_A: Integer;
begin
  if fRatePTU2_A = 0 then fRatePTU2_A := Consts.RatePTU2_A;
  Result := fRatePTU2_A;
end;

function TEmar105_File._GetRatePTU2_B: Integer;
begin
  if fRatePTU2_B = 0 then fRatePTU2_B := Consts.RatePTU2_B;
  Result := fRatePTU2_B;
end;

function TEmar105_File._GetRatePTU2_C: Integer;
begin
  if fRatePTU2_C = 0 then fRatePTU2_C := Consts.RatePTU2_C;
  Result := fRatePTU2_C;
end;

function TEmar105_File._GetRatePTU2_D: Integer;
begin
  if fRatePTU2_D = 0 then fRatePTU2_D := Consts.RatePTU2_D;
  Result := fRatePTU2_D;
end;

function TEmar105_File._GetRatePTU2_E: Integer;
begin
  if fRatePTU2_E = 0 then fRatePTU2_E := Consts.RatePTU2_E;
  Result := fRatePTU2_E;
end;

function TEmar105_File._GetRatePTU2_F: Integer;
begin
  if fRatePTU2_F = 0 then fRatePTU2_F := Consts.RatePTU2_F;
  Result := fRatePTU2_F;
end;

function TEmar105_File._GetRatePTU2_G: Integer;
begin
  if fRatePTU2_G = 0 then fRatePTU2_G := Consts.RatePTU2_G;
  Result := fRatePTU2_G;
end;

function TEmar105_File._GetRatePTU_N: Integer;
begin
  if fRatePTU_N = 0 then fRatePTU_N := Consts.RatePTU_N;
  Result := fRatePTU_N;
end;

function TEmar105_File._GetTicketNumberUsedHighPart(ATicketNumber: Word; AForcedIncrementationHighPart: Boolean)
  : Cardinal;
begin
  {
   F_Event01_LastTicketNumberHighPart już ma aktualną wartość
   liczy dla ostatniego zdarzenia identyfikacji bileterki lub sprzedaży kolejnego biletu
  }
  // warunek zwykle taki: Emar-205; numer biletu mniejszy od
  if AForcedIncrementationHighPart and (F_Event01_LastTicketNumberHighPart < $F) then // 15 - max value
  begin
    if IsTicketRegisterEmar205(PChar(F_Event01_TicketRegister)) // czy bierząca bileterka jest Emar-205
      and(F_Event01_LastTicketNumber mod $10000 > ATicketNumber)
      //E.B. 10.01.2022 - cofnięcie numeracji może być wynikiem błędu w raporcie
      // T11851: błedne działanie Bileterki Emar-205: w przypadku, gdy w wyniku jakiegoś błędu bileterki w raporcie wpisany jest numer biletu mniejszy od poprzedniego funkcja rejestracji automatycznie zwiększa numer biletu o wartość 65536.
      and(F_Event01_LastTicketNumber mod $10000 > 65500)and(ATicketNumber < 10)
    then
      Inc(F_Event01_LastTicketNumberHighPart);
    F_Event01_LastTicketNumber := F_Event01_LastTicketNumberHighPart * Succ($FFFF) + ATicketNumber;
  end;
  if (F_Event01_LastTicketNumberHighPart > 0) and (F_Event01_LastTicketNumberHighPart <= $F) then
      Result := F_Event01_LastTicketNumberHighPart * Succ($FFFF) + ATicketNumber
  else Result := ATicketNumber;
end;

function TEmar105_File._GetIsSimpleTicketWronglyPrinted(ATicketControlCode: String): Boolean;
begin
  Result := not(
    (ATicketControlCode = '')
    or(AnsiCompareStr(AnsiUpperCase(ATicketControlCode), 'FFFFFFFFFF') = 0) // 5 bajtów
    );
end;

function TEmar105_File._GetIsSimpleTicketWrong(AEventIndex: Integer): Boolean;
  function GetSimpleTicketNumber(ATicketEvent: IEmar_ReportEvent): Cardinal;
  begin
    case ATicketEvent.Kind of
      13: Result := ATicketEvent.AsEvent_13._TicketNumberUsedHighPart;
      15: Result := ATicketEvent.AsEvent_15._TicketNumberUsedHighPart;
      16: Result := ATicketEvent.AsEvent_16._TicketNumberUsedHighPart;
      21: Result := ATicketEvent.AsEvent_21._TicketNumberUsedHighPart;
      30: Result := ATicketEvent.AsEvent_30._TicketNumberUsedHighPart;
    else
      Result := 0;
    end;
  end;
var
  rel: IEmar_ReportEvent;
  bMemoryCleared: Boolean;
  sTicketRegisterZero: String;
  i: Integer;
  iTicketNumber: Cardinal;
begin
  Result := False;
  if (AEventIndex > -1)and(AEventIndex < Self.ReportEventList.Count) then
  begin
    rel := Self.ReportEventList[AEventIndex];
    //sprawdź czy nast. bilet powtórzony
    sTicketRegisterZero := F_Event01_TicketRegister;       //E.B. 20.06.2016
    iTicketNumber := GetSimpleTicketNumber(rel); //numer biletu
    i := Succ(AEventIndex);
    bMemoryCleared := False;
    while (i < Self.ReportEventList.Count) and not(Self.ReportEventList[i].Kind in C_SET_OF_EMAR_TICKET_EVENTS) do
    begin
      if Self.ReportEventList[i].ReportRecordCount = 1 then
      begin
        case Self.ReportEventList[i].Kind of
          1: begin
            sTicketRegisterZero := String(Self.ReportEventList[i].AsEvent_01.TicketRegister);
            if Self.ReportEventList[i].AsEvent_01.MemoryClearState = 0 then
            begin
              bMemoryCleared := True;
              Break;
            end;
          end;
          2: sTicketRegisterZero := String(Self.ReportEventList[i].AsEvent_02.TicketRegister);
          5: begin
            sTicketRegisterZero := String(Self.ReportEventList[i].AsEvent_05.TicketRegister);
            if Self.ReportEventList[i].AsEvent_05.MemoryClearState = 0 then
            begin
              bMemoryCleared := True;
              Break;
            end;
          end;
          22: sTicketRegisterZero := String(Self.ReportEventList[i].AsEvent_22.TicketRegister);
        end;
      end;
      Inc(i);
    end;
    if not bMemoryCleared then
      if (i < Self.ReportEventList.Count)
        and(sTicketRegisterZero = F_Event01_TicketRegister)
        and(GetSimpleTicketNumber(Self.ReportEventList[i]) = iTicketNumber) then
      begin
        Result := True;
      end;
  end;
end;

procedure TEmar105_File._SetTicketBuyerNIP(AEvent42Index: Integer);
  procedure SetNIPRelatedTicket(ATicketEvent: IEmar_ReportEvent; AEvent_42: IEmar_ReportEvent_42);
  begin
    if (AnsiCompareStr(ATicketEvent.EventDate, AEvent_42.EventDate) = 0)
      and(AnsiCompareStr(ATicketEvent.EventTime, AEvent_42.EventTime) = 0) then
    begin
      case ATicketEvent.Kind of
        13: if (ATicketEvent.AsEvent_13.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_13._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_13._BuyerNIP := AEvent_42.NIP;
        15: if (ATicketEvent.AsEvent_15.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_15._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_15._BuyerNIP := AEvent_42.NIP;
        16: if (ATicketEvent.AsEvent_16.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_16._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_16._BuyerNIP := AEvent_42.NIP;
        21: if (ATicketEvent.AsEvent_21.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_21._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_21._BuyerNIP := AEvent_42.NIP;
        30: if (ATicketEvent.AsEvent_30.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_30._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_30._BuyerNIP := AEvent_42.NIP;
        32: if (ATicketEvent.AsEvent_32.DocumentNumber = AEvent_42.DocumentNumber)
              and(ATicketEvent.AsEvent_32._TicketNumberUsedHighPart = AEvent_42._TicketNumberUsedHighPart) then
              ATicketEvent.AsEvent_32._BuyerNIP := AEvent_42.NIP;
      end;
    end;
  end;
const C_SupportedEventsID = [13, 15, 16, 21, 30, 32];
var
  iTicketEvent: Integer;
  relTicket: IEmar_ReportEvent;
  rel_42: IEmar_ReportEvent_42;
begin
  if (AEvent42Index > -1)and(AEvent42Index < Self.ReportEventList.Count)and F_IsEmar205 then
  begin
    rel_42 := Self.ReportEventList[AEvent42Index].AsEvent_42;
    if rel_42.Kind = 42 then
    begin
      relTicket := nil;
      // event #42 folows by ticket sale event or there could be max 1 extra event # 36 'zmiana sposobu zapłaty (EMAR-205)'
      iTicketEvent := Pred(AEvent42Index);
      if (iTicketEvent > -1)and(Self.ReportEventList[iTicketEvent].Kind in C_SupportedEventsID) then
        relTicket := Self.ReportEventList[iTicketEvent]
      else
        if Self.ReportEventList[iTicketEvent].Kind = 36 then
        begin
          iTicketEvent := Pred(Pred(AEvent42Index));
          if (iTicketEvent > -1)and(Self.ReportEventList[iTicketEvent].Kind in C_SupportedEventsID) then
            relTicket := Self.ReportEventList[iTicketEvent];
        end;
      if Assigned(relTicket) then
      begin
        SetNIPRelatedTicket(relTicket, rel_42);
      end;
    end;
  end;
end;

function TEmar105_File._GetMaxTicketPrice10: Integer;
begin
  if fMaxTicketPrice10 = 0 then fMaxTicketPrice10 := Consts.MaxTicketPrice10;
  Result := fMaxTicketPrice10;
end;

function TEmar105_File._RecordVersion(aFileVersion, aId: integer): integer;
begin
  Result := 0;
  case aId of
  9: Result := 1;
  10: case aFileVersion of
    6: Result := 5;
    7, 8: Result := 6;
    end;
  11: case aFileVersion of
    6: Result := 1;
    7: Result := 5;
    8: Result := 5;
    end;
  12: Result := 1;
  13: Result := 1;
  15: case aFileVersion of
    7, 8: Result := 1;
    end;
  16: case aFileVersion of
    6: Result := 1;
    7, 8: Result := 2;
    end;
  21: case aFileVersion of
    7, 8: Result := 1;
    end;
  23: Result := 1;
  26: case aFileVersion of
    7: Result := 1;
    8: Result := 2;
    end;
  27: Result := 1;
  28: Result := 1;
  29: Result := 1;
  30: Result := 1;
  32: Result := 1;
  35: Result := 1;
  36: Result := 1;
  39: case aFileVersion of
    7, 8: Result := 1;
    end;
  40: case aFileVersion of
    6: Result := 1;
    7, 8: Result := 2;
    end;
  43: case aFileVersion of
    7, 8: Result := 1;
    end;
  end;
end;

procedure TEmar105_File._Clear;
begin
  inherited;
  fCalBegin := '';
  fCalEnd := '';
  fMaxTicketPrice5 := 0;
  fMaxTicketPrice10 := 0;
  fRatePTU1_A := 0;
  fRatePTU1_B := 0;
  fRatePTU1_C := 0;
  fRatePTU1_D := 0;
  fRatePTU1_E := 0;
  fRatePTU1_F := 0;
  fRatePTU1_G := 0;
  fRatePTU2_A := 0;
  fRatePTU2_B := 0;
  fRatePTU2_C := 0;
  fRatePTU2_D := 0;
  fRatePTU2_E := 0;
  fRatePTU2_F := 0;
  fRatePTU2_G := 0;
  fRatePTU_N := 0;
  F_SavedReadyCode := 0;
end;

function TEmar105_File._GetCalendarBegin: pchar;
begin
  if fCalBegin = '' then fCalBegin := Consts.CalendarBegin;
  Result := pchar(fCalBegin);
end;

function TEmar105_File.GetConsts: IEmar105_Consts;
begin
  Result := fConsts as IEmar105_Consts;
end;

function TEmar105_File.GetOik: IEmar105_OIK;
begin
  Result := fOik as IEmar105_OIK;
end;

function TEmar105_File.SaveToFile(aFilePath: pchar; aVersion,
  aSaveMode: integer): longword;
begin
  fSaveMode := aSaveMode;
  if fSaveMode = EMAR_SAVEMODE_JSON_DD then begin
    fVersion := aVersion;
    AdditionalDataToJSON(aFilePath, false);
    Result := ERR_NO_ERROR;
  end else
    Result := inherited;
end;

function TEmar105_File.SetOIKReadyCodeNextReportCode(aState: byte; aNextReportCode: PChar; aLoadFromCard: boolean)
  : cardinal;
var
  p: Integer;
  iOldOIKNr: Byte;
  iReadyCode_OIK: Integer;
  cCardSerialNumber_OIK1: Cardinal;
begin
  if fUsbDevice.IsOpened then begin
    Result := ERR_USER_TERMINATE;
    iOldOIKNr := TEmar105_OIK(fOik).Nr;
    try
      EmarLog(Format('TEmar105_File.SetOIKReadyCodeNextReportCode ReadyCode = %d', [Self.OIK.ReadyCode]));
      TEmar105_OIK(fOik).Nr := 1;
      p := TEmar105_OIK(fOik).fPageNr;
      if aLoadFromCard then begin // be careful with this parameter; OIK could be rewritten
        Result := fUSBStream.ReloadPageFromDevice(p);
        if Result = ERR_NO_ERROR then begin
          //USBStream.Seek(p);
          TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
          if TEmar105_OIK(fOik).CardSerialNumber = $FFFFFFFF then
          begin
            TEmar105_OIK(fOik).Nr := 2;
            TEmar105_OIK(fOik).LoadFromBuffer(fUSBStream);
            TEmar105_OIK(fOik).Nr := 1;
          end;
        end;
        if fBreak then Exit;
      end;
      cCardSerialNumber_OIK1 := TEmar105_OIK(fOik).CardSerialNumber;
      iReadyCode_OIK := DeviceReadyCode;

      TEmar105_OIK(fOik).ReadyCode := aState;
      if Assigned(aNextReportCode) and (string(aNextReportCode) <> '') then
        TEmar105_OIK(fOik).NextReportCode := aNextReportCode;

      USBStream.Seek(p);
      TEmar105_OIK(fOik).SaveToBuffer(fUSBStream);
      TEmar105_OIK(OIK).ForceUpdateFlash();

      if _SavedReadyCode = 0 then
      begin
        if cCardSerialNumber_OIK1 <> $FFFFFFFF then
          _SavedReadyCode := iReadyCode_OIK; // zapamiętujemy
      end
      else
        if _SavedReadyCode = aState then
          _SavedReadyCode := 0;
      // karta będzie miała ten sam status, nie ma sensu przychowywać

      if fBreak then Exit;
      Result := ERR_NO_ERROR;
    finally
      TEmar105_OIK(fOik).Nr := iOldOIKNr;
    end;
  end
  else Result := ERR_USB_DEVICE_NOT_OPENED;
end;

procedure TEmar105_File.StreamOnBeforeBlockClear(aSender: TObject; aPage: integer; var aBreak: LongBool);
begin
  fBreak := false;
  if Assigned(fCallback) then fCallback(self, EMAR105CallbackKind_BlockClear, aPage, fBreak);
  aBreak := fBreak;
end;

procedure TEmar105_File.StreamOnBeforePageClear(aSender: TObject; aPage: integer; var aBreak: LongBool);
begin
  fBreak := false;
  if Assigned(fCallback) then fCallback(self, EMAR105CallbackKind_PageClear, aPage, fBreak);
  aBreak := fBreak;
end;

procedure TEmar105_File.StreamOnBeforePageRead(aSender: TObject; aPage: integer; var aBreak: LongBool);
begin
  fBreak := false;
  if Assigned(fCallback) then fCallback(self, EMAR105CallbackKind_PageRead, aPage, fBreak);
  aBreak := fBreak;
end;

procedure TEmar105_File.StreamOnBeforePageWrite(aSender: TObject; aPage: integer; var aBreak: LongBool);
begin
  fBreak := false;
  if Assigned(fCallback) then fCallback(self, EMAR105CallbackKind_PageWrite, aPage, fBreak);
  aBreak := fBreak;
end;

{$ENDREGION}
{ TEmar105_ReportEvent_00 }

procedure TEmar105_ReportEvent_00.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_00.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_00);
end;

procedure TEmar105_ReportEvent_00.GetFromData;
var
  p: PEmar105_ReportEvent_00;
  i: integer;
begin
  inherited;
  if fKind = 0 then begin
    p := pData;
    fReportCode := CopyLStr(p^.ReportCode, SizeOf(p^.ReportCode));
    for i := low(p^.TaxRates) to high(p^.TaxRates) do
      fTaxRates[i] := CalcWord(p^.TaxRates[i]);
    fTaxRatesChange := p^.TaxRatesChange;
    fErrorNo := 0;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_00.SetToData;
var
  p: PEmar105_ReportEvent_00;
  i: integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.ReportCode, ansistring(fReportCode), SizeOf(p^.ReportCode), true, #0);
    for i := low(p^.TaxRates) to high(p^.TaxRates) do p^.TaxRates[i] := CalcWord(fTaxRates[i]);
    p^.TaxRatesChange := fTaxRatesChange;
    p^.XorSum := EmarXORSum(p^, GetDataLength - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_01 }

procedure TEmar105_ReportEvent_01.AllocDataMem;
begin
  fDataRecCount := 4;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_01.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_01);
end;

procedure TEmar105_ReportEvent_01.GetFromData;
var
  p: PEmar105_ReportEvent_01;
  i: integer;
begin
  inherited;
  if fKind = 1 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2017-10-31 CalcCardinal(p^.CardNumber);
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fFiscalReportState := p^.FiscalReportState;
    fFiscalReportNumber := CalcWord(p^.FiscalReportNumber);
    fFirmwareVersion := p^.FirmwareVersion;
    fOperationKind := p^.Kind;
    // ATTENTION: When decode string below, calculate the first byte and the rest separately (f.e., A057BA7F28 => A0 + 57BA7F28)
    fFiscalReportCode := ArrayToHex(p^.FiscalReportCode, SizeOf(p^.FiscalReportCode));
    fTicketRegisterState := p^.TicketRegisterState;
    // 2
    fFiscalReportDate := EmarDateToString(p^.FiscalReportDate);
    fFiscalReportTime := EmarTimeToString(p^.FiscalReportTime);
    fTaxRatesIndex := p^.TaxRatesIndex;
    fMemoryClearState := p^.MemoryClearState;
    fMemoryClearCount := p^.MemoryClearCount;
    fLastPrintNumber := CalcCardinal(p^.LastPrintNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    fBrutto := CalcCardinal(p^.Brutto);
    fTicketCount := CalcWord(p^.TicketCount);
    fBusSideNumber := CopyLStr(p^.BusSideNumber, SizeOf(p^.BusSideNumber));
{$REGION '    remove not number chars}
    {
      Numer boczny autobusu (4 litery+8 cyfr)
      część literowa uzupełniona jest spacjami z lewej strony,
      jeśli cyfr mniej niż 8, to dalej $FF;
      jeśli brak numeru bocznego, to pole wypełnione kodami $FF
    }
    if Length(fBusSideNumber) > 4 then
    begin
      i := 5;
      while i <= Length(fBusSideNumber) do
      begin
        if CharInSet(fBusSideNumber[i], ['0'..'9'])  then
          Inc(i)
        else
          Delete(fBusSideNumber, i, 1);
      end;
    end;
{$ENDREGION}
    fLastTicketNumberHighPart := p^.LastTicketNumberHighPart;
    // 3
    for i := low(p^.NettoByTaxRate) to high(p^.NettoByTaxRate) do
        fNettoByTaxRate[i] := CalcCardinal(p^.NettoByTaxRate[i]);
    fCurrencyCode := CopyLStr(p^.CurrencyCode, SizeOf(p^.CurrencyCode));
    fCurrencySaveTime := EmarTimeToString(p^.CurrencySaveTime);
    // 4
    for i := low(p^.TaxAmount) to high(p^.TaxAmount) do fTaxAmount[i] := CalcCardinal(p^.TaxAmount[i]);
    fCurrencySaveDate := EmarDateToString(p^.CurrencySaveDate);
    fErrorNo := 0;
    //
    TEmar105_File(Owner).F_IsEmar205 := TEmar105_File(Owner).F_IsEmar205 and
      Owner.IsTicketRegisterEmar205(TicketRegister);
    TEmar105_File(Owner).F_Event01_TicketRegister := TicketRegister;
    TEmar105_File(Owner).F_Event01_LastTicketNumberHighPart := fLastTicketNumberHighPart;
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
    TEmar105_File(Owner).F_Event01_LastTicketNumber := FLastTicketNumberUsedHighPart;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_01.SetToData;
var
  p: PEmar105_ReportEvent_01;
  i: integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 4;
    p^.CardNumber := fCardNumber; // ATY 2017-10-31 CalcCardinal(fCardNumber);
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), False);
    p^.FiscalReportState := fFiscalReportState;
    p^.FiscalReportNumber := CalcWord(fFiscalReportNumber);
    p^.FirmwareVersion := fFirmwareVersion;
    p^.Kind := fOperationKind;
    HexToArray(p^.FiscalReportCode[0], SizeOf(p^.FiscalReportCode), fFiscalReportCode);
    p^.TicketRegisterState := fTicketRegisterState;
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    DateToEmarDate(p^.FiscalReportDate, fFiscalReportDate);
    TimeToEmarTime(p^.FiscalReportTime, fFiscalReportTime);
    p^.TaxRatesIndex := fTaxRatesIndex;
    p^.MemoryClearState := fMemoryClearState;
    p^.MemoryClearCount := fMemoryClearCount;
    p^.LastPrintNumber := CalcCardinal(fLastPrintNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.Brutto := CalcCardinal(fBrutto);
    p^.TicketCount := CalcWord(fTicketCount);
    StrPLCopy(p^.BusSideNumber, ansistring(fBusSideNumber), Length(fBusSideNumber), False); // !!! kończy się FFami
    p^.LastTicketNumberHighPart := fLastTicketNumberHighPart;
    // 3
    p^.rBegin3.Id := p^.rBegin1.Id;
    p^.rBegin3.Count := p^.rBegin1.Count;
    p^.rBegin3.Index := 3;
    for i := low(p^.NettoByTaxRate) to high(p^.NettoByTaxRate) do
        p^.NettoByTaxRate[i] := CalcCardinal(fNettoByTaxRate[i]);
    StrPLCopy(p^.CurrencyCode, ansistring(fCurrencyCode), SizeOf(p^.CurrencyCode) - 1, true, #0);
    TimeToEmarTime(p^.CurrencySaveTime, fCurrencySaveTime);
    // 4
    p^.rBegin4.Id := p^.rBegin1.Id;
    p^.rBegin4.Count := p^.rBegin1.Count;
    p^.rBegin4.Index := 4;
    for i := low(p^.TaxAmount) to high(p^.TaxAmount) do p^.TaxAmount[i] := CalcCardinal(fTaxAmount[i]);
    DateToEmarDate(p^.CurrencySaveDate, fCurrencySaveDate);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum4 := EmarXORSum(p^.rBegin4, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_02 }

procedure TEmar105_ReportEvent_02.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_02.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_02);
end;

procedure TEmar105_ReportEvent_02.GetFromData;
var
  p: PEmar105_ReportEvent_02;
begin
  inherited;
  if Kind = 2 then begin
    p := pData;
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fNewFiscalReportNumber := CalcWord(p^.NewFiscalReportNumber);
    fFiscalReportState := p^.FiscalReportState;
    fLastDocumentNumber := CalcCardinal(p^.LastDocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_02.SetToData;
var
  p: PEmar105_ReportEvent_02;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), False);
    p^.NewFiscalReportNumber := CalcWord(fNewFiscalReportNumber);
    p^.FiscalReportState := fFiscalReportState;
    p^.LastDocumentNumber := CalcCardinal(fLastDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_03 }

procedure TEmar105_ReportEvent_03.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_03.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_03);
end;

procedure TEmar105_ReportEvent_03.GetFromData;
var
  p: PEmar105_ReportEvent_03;
begin
  inherited;
  if Kind = 3 then begin
    p := pData;
    fHeaderChanged := (p^.Changed = 0);
    fFooterChanged := (p^.Changed = 1);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_03.SetToData;
var
  p: PEmar105_ReportEvent_03;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    if fHeaderChanged then p^.Changed := 0
    else p^.Changed := 1;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent04 }

procedure TEmar105_ReportEvent_04.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_04.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_04);
end;

procedure TEmar105_ReportEvent_04.GetFromData;
var
  p: PEmar105_ReportEvent_04;
  i: integer;
begin
  inherited;
  if Kind = 4 then begin
    p := pData;
    for i := low(p^.NewTaxRates) to high(p^.NewTaxRates) do fNewTaxRates[i] := CalcWord(p^.NewTaxRates[i]);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_04.SetToData;
var
  p: PEmar105_ReportEvent_04;
  i: integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    for i := low(p^.NewTaxRates) to high(p^.NewTaxRates) do p^.NewTaxRates[i] := CalcWord(fNewTaxRates[i]);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent05 }

procedure TEmar105_ReportEvent_05.AllocDataMem;
begin
  fDataRecCount := 4;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_05.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_05);
end;

procedure TEmar105_ReportEvent_05.GetFromData;
var
  p: PEmar105_ReportEvent_05;
  i: integer;
begin
  inherited;
  if Kind = 5 then begin
    p := pData;
    // 1
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fFiscalReportNumber := CalcWord(p^.FiscalReportNumber);
    fFiscalReportState := p^.FiscalReportState;
    fFiscalReportCode := ArrayToHex(p^.FiscalReportCode, SizeOf(p^.FiscalReportCode));
    // 2
    fTaxRatesIndex := p^.TaxRatesIndex;
    fMemoryClearState := p^.MemoryClearState;
    fMemoryClearCount := p^.MemoryClearCount;
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    fBrutto := CalcCardinal(p^.Brutto);
    fTicketCount := CalcWord(p^.TicketCount);
    fFirstBillDate := EmarDateToString(p^.FirstBillDate);
    fFirstBillTime := EmarTimeToString(p^.FirstBillTime);
    fLastBillDate := EmarDateToString(p^.LastBillDate);
    fLastBillTime := EmarTimeToString(p^.LastBillTime);
    // 3
    for i := low(p^.NettoByTaxRate) to high(p^.NettoByTaxRate) do
        fNettoByTaxRate[i] := CalcCardinal(p^.NettoByTaxRate[i]);
    fCurrencyCode := CopyLStr(p^.CurrencyCode, SizeOf(p^.CurrencyCode) - 1);
    fCurrencySaveTime := EmarTimeToString(p^.CurrencySaveTime);
    // 4
    for i := low(p^.TaxAmount) to high(p^.TaxAmount) do fTaxAmount[i] := CalcCardinal(p^.TaxAmount[i]);
    fCurrencySaveDate := EmarDateToString(p^.CurrencySaveDate);
    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber,
      False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_05.SetToData;
var
  p: PEmar105_ReportEvent_05;
  i: integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 4;
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), False);
    p^.FiscalReportNumber := CalcWord(fFiscalReportNumber);
    p^.FiscalReportState := fFiscalReportState;
    HexToArray(p^.FiscalReportCode, SizeOf(p^.FiscalReportCode), fFiscalReportCode);
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    p^.TaxRatesIndex := fTaxRatesIndex;
    p^.MemoryClearState := fMemoryClearState;
    p^.MemoryClearCount := fMemoryClearCount;
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.Brutto := CalcCardinal(fBrutto);
    p^.TicketCount := CalcWord(fTicketCount);
    DateToEmarDate(p^.FirstBillDate, fFirstBillDate);
    TimeToEmarTime(p^.FirstBillTime, fFirstBillTime);
    DateToEmarDate(p^.LastBillDate, fLastBillDate);
    TimeToEmarTime(p^.LastBillTime, fLastBillTime);
    // 3
    p^.rBegin3.Id := p^.rBegin1.Id;
    p^.rBegin3.Count := p^.rBegin1.Count;
    p^.rBegin3.Index := 3;
    for i := low(p^.NettoByTaxRate) to high(p^.NettoByTaxRate) do
        p^.NettoByTaxRate[i] := CalcCardinal(fNettoByTaxRate[i]);
    StrPLCopy(p^.CurrencyCode, ansistring(fCurrencyCode), SizeOf(p^.CurrencyCode) - 1, true, #0);
    TimeToEmarTime(p^.CurrencySaveTime, fCurrencySaveTime);
    // 4
    p^.rBegin4.Id := p^.rBegin1.Id;
    p^.rBegin4.Count := p^.rBegin1.Count;
    p^.rBegin4.Index := 4;
    for i := low(p^.TaxAmount) to high(p^.TaxAmount) do p^.TaxAmount[i] := CalcCardinal(fTaxAmount[i]);
    DateToEmarDate(p^.CurrencySaveDate, fCurrencySaveDate);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum4 := EmarXORSum(p^.rBegin4, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_06 }

procedure TEmar105_ReportEvent_06.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_06.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_06);
end;

procedure TEmar105_ReportEvent_06.GetFromData;
var
  p: PEmar105_ReportEvent_06;
begin
  inherited;
  if Kind = 6 then begin
    p := pData;
    fValid := p^.Valid
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_06.SetToData;
var
  p: PEmar105_ReportEvent_06;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.Valid := fValid;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_07 }

procedure TEmar105_ReportEvent_07.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_07.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_07);
end;

procedure TEmar105_ReportEvent_07.SetToData;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then
      PEmar105_ReportEvent_07(pData).XorSum1 := EmarXORSum(PEmar105_ReportEvent_07(pData).rBegin1,
      SizeOf(TEmar105_BaseReport_Rec) - 1);
end;

{ TEmar105_ReportEvent_08 }

procedure TEmar105_ReportEvent_08.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_08.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_08);
end;

procedure TEmar105_ReportEvent_08.GetFromData;
var
  p: PEmar105_ReportEvent_08;
begin
  inherited;
  if fKind = 8 then begin
    p := pData;
    fCounter := StrToIntDef(CopyLStr(p^.Counter, SizeOf(p^.Counter)), 0);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_08.SetToData;
var
  p: PEmar105_ReportEvent_08;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.Counter, ansistring(Format('%.7d', [fCounter])), SizeOf(p^.Counter), false, #0);
    p^.Empty1[0] := $FF; // StrPLCopy dodaje zawsze 0
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_09 }

procedure TEmar105_ReportEvent_09.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_09.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_09);
end;

procedure TEmar105_ReportEvent_09.GetFromData;
var
  p: PEmar105_ReportEvent_09;
begin
  inherited;
  if fKind = 9 then begin
    p := pData;
    fLitres := StrToIntDef(CopyLStr(p^.Liters, SizeOf(p^.Liters)), 0);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_09.SetToData;
var
  p: PEmar105_ReportEvent_09;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.Liters, ansistring(Format('%.7d', [fLitres])), SizeOf(p^.Liters), false);
    p^.Empty1[0] := $FF; // StrPLCopy dodaje zawsze 0
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_10 }

procedure TEmar105_ReportEvent_10.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_10.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_10);
end;

procedure TEmar105_ReportEvent_10.GetFromData;
var
  p: PEmar105_ReportEvent_10;
begin
  inherited;
  if fKind = 10 then begin
    p := pData;
    fTaskNumber := p^.TaskNumber;
    fTaskPosition := p^.TaskPosition;
    fReportRideIndex := CalcWord(p^.ReportRideIndex);
    fRideNumber := CalcWord(p^.RideNumber);
    fRidePage := CalcWord(p^.RidePage);
    fRideOffset := CalcWord(p^.RideOffset);
    fRideCode := CalcWord(p^.RideCode);
    fLastDocumentNumber := CalcCardinal(p^.LastDocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_10.SetToData;
var
  p: PEmar105_ReportEvent_10;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.TaskNumber := fTaskNumber;
    p^.TaskPosition := fTaskPosition;
    p^.ReportRideIndex := CalcWord(fReportRideIndex);
    p^.RideNumber := CalcWord(fRideNumber);
    p^.RidePage := CalcWord(fRidePage);
    p^.RideOffset := CalcWord(fRideOffset);
    p^.RideCode := CalcWord(fRideCode);
    p^.LastDocumentNumber := CalcCardinal(fLastDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_11 }

procedure TEmar105_ReportEvent_11.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_11.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_11);
end;

procedure TEmar105_ReportEvent_11.GetFromData;
var
  p: PEmar105_ReportEvent_11;
  CE0: Boolean;  //15.20.2021  raport z EMAR-205 bez karty pamięci
  j: Int64;
  pcBytes1, pcBytes2: PAnsiChar;
  tr: TEmarTimeTypeRec;
begin
  inherited;
  if fKind = 11 then begin
    p := pData;
    fRideCount := CalcWord(p^.RideCount);
    fAdditionalFeeCount := CalcCardinal(p^.AdditionalFeeCount);
    fAdditionalFeeAmount := CalcCardinal(p^.AdditionalFeeAmount);
    fTicketCount := CalcCardinal(p^.TicketCount);
    fTicketAmount := CalcCardinal(p^.TicketAmount);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    fFull := (p^.Full = 1);
    fForDay := (p^.ForDay = 1);
    fReportKind := p^.ReportKind;

    CE0 := Copy(String(TEmar105_File(Owner).OIK.TimeTableFileName), 9, 1) = '_';

    FReportPeriodDateBegin := '';
    FReportPeriodDateEnd := '';

    if CE0 and (fReportKind in [1,2]) then     //E.B. 15.10.2021
    begin
      pcBytes1   := @p.AdditionalFeeCount;
      pcBytes2   := @p.TicketCount;
      if (Ord(pcBytes1[0]) = 0) and (Ord(pcBytes2[0]) = 0) then   //podsumowanie; check first bytes only
      begin
        j := Int64(fAdditionalFeeAmount) + fTicketAmount;
        if (fAdditionalFeeAmount = High(Cardinal))or(fTicketAmount = High(Cardinal))or(j > 2147483647) then
        begin
          fAdditionalFeeAmount := 0;
          fAdditionalFeeCount := 0;
          fTicketAmount := 0;
          fTicketCount := 0;
        end;
      end
      else   //rozpoczęcie wydruku
      begin
        fAdditionalFeeCount := High(Cardinal); //-1;
        fAdditionalFeeAmount := 0;
        fTicketCount := High(Cardinal); //-1;
        fTicketAmount := 0;
        pcBytes1   := @p.AdditionalFeeAmount;
        tr.bHour   := Ord(pcBytes1[0]); // first byte
        tr.bMinute := Ord(pcBytes1[1]); // second byte
        tr.bSecond := Ord(pcBytes1[2]); // third byte
        FReportPeriodDateBegin := EmarDateToString(TEmarDateTypeRec(p^.AdditionalFeeCount)) + ' ' + EmarTimeToString(tr);
        pcBytes2   := @p.TicketAmount;
        tr.bHour   := Ord(pcBytes2[0]); // first byte
        tr.bMinute := Ord(pcBytes2[1]); // second byte
        tr.bSecond := Ord(pcBytes2[2]); // third byte
        FReportPeriodDateEnd := EmarDateToString(TEmarDateTypeRec(p^.TicketCount)) + ' ' + EmarTimeToString(tr);
      end;
    end
    else   //z zadania
    begin
      if fTicketCount = High(Cardinal) then
      begin
        fAdditionalFeeCount := High(Cardinal); //-1;
        fAdditionalFeeAmount := 0;
        fTicketCount := High(Cardinal); //-1;
        fTicketAmount := 0;
      end
      else  // podsumowanie
      begin
        j := Int64(fAdditionalFeeAmount) + fTicketAmount;
        if (fAdditionalFeeAmount = High(Cardinal))or(fTicketAmount = High(Cardinal))or(j > 2147483647) then
        begin
          fAdditionalFeeAmount := 0;
          fAdditionalFeeCount := 0;
          fTicketAmount := 0;
          fTicketCount := 0;
        end;
      end;
    end;

    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_11.SetToData;
var
  p: PEmar105_ReportEvent_11;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.RideCount := CalcWord(fRideCount);
    p^.AdditionalFeeCount := CalcCardinal(fAdditionalFeeCount);
    p^.AdditionalFeeAmount := CalcCardinal(fAdditionalFeeAmount);
    p^.TicketCount := CalcCardinal(fTicketCount);
    p^.TicketAmount := CalcCardinal(fTicketAmount);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    if fFull then p^.Full := 1
    else p^.Full := 0;
    if fForDay then p^.ForDay := 1
    else p^.ForDay := 0;
    p^.ReportKind := fReportKind;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_12 }

procedure TEmar105_ReportEvent_12.AllocDataMem;
begin
  fDataRecCount := 2;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_12.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_12);
end;

procedure TEmar105_ReportEvent_12.GetFromData;
var
  p: PEmar105_ReportEvent_12;
begin
  inherited;
  if fKind = 12 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2017-10-31 CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    fCardState := p^.CardState;
    fPermission := p^.Permission;
    fReturnTicketBonus := p^.ReturnTicketBonus;
    fReturnTicketValidDays := p^.ReturnTicketValidDays;
    fGroupPassangers1 := p^.GroupPassangers1;
    fGroupBonus1 := p^.GroupBonus1;
    fGroupPassangers2 := p^.GroupPassangers2;
    fGroupBonus2 := p^.GroupBonus2;
    fTicketOption := p^.TicketOption;
    fThintherDate := EmarDateToString(p^.ThintherDate);
    fThintherTime := EmarTimeToString(p^.ThintherTime);
    fCarrierCompany := CalcWord(p^.CarrierCompany);
    fThintherRideNumber := CalcWord(p^.ThintherRideNumber);
    // 2
    fLoyaltyProgramValidTo := EmarDateToString(p^.LoyaltyProgramValidTo);
    fTicketCount := p^.TicketCount;
    fFirstTicketSaleDate := EmarDateToString(p^.FirstTicketSaleDate);
    fDistance := CalcWord(p^.Distance);
    fTicketAmount := CalcCardinal(p^.TicketAmount);
    fReturnTicketBonus2 := p^.ReturnTicketBonus2;
    fReturnTicketDays2 := p^.ReturnTicketDays2;
    fReturnTicketBonus3 := p^.ReturnTicketBonus3;
    fReturnTicketDays3 := p^.ReturnTicketDays3;
    fReturnBonusValidTo := EmarDateToString(p^.ReturnBonusValidTo);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_12.SetToData;
var
  p: PEmar105_ReportEvent_12;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 2;
    p^.CardNumber := fCardNumber; // ATY 2017-10-31 CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.CardState := fCardState;
    p^.Permission := fPermission;
    p^.ReturnTicketBonus := fReturnTicketBonus;
    p^.ReturnTicketValidDays := fReturnTicketValidDays;
    p^.GroupPassangers1 := fGroupPassangers1;
    p^.GroupBonus1 := fGroupBonus1;
    p^.GroupPassangers2 := fGroupPassangers2;
    p^.GroupBonus2 := fGroupBonus2;
    p^.TicketOption := fTicketOption;
    DateToEmarDate(p^.ThintherDate, fThintherDate);
    TimeToEmarTime(p^.ThintherTime, fThintherTime);
    p^.CarrierCompany := CalcWord(fCarrierCompany);
    p^.ThintherRideNumber := CalcWord(fThintherRideNumber);
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    DateToEmarDate(p^.LoyaltyProgramValidTo, fLoyaltyProgramValidTo);
    p^.TicketCount := fTicketCount;
    DateToEmarDate(p^.FirstTicketSaleDate, fFirstTicketSaleDate);
    p^.Distance := CalcWord(fDistance);
    p^.TicketAmount := CalcCardinal(fTicketAmount);
    p^.ReturnTicketBonus2 := fReturnTicketBonus2;
    p^.ReturnTicketDays2 := fReturnTicketDays2;
    p^.ReturnTicketBonus3 := fReturnTicketBonus3;
    p^.ReturnTicketDays3 := fReturnTicketDays3;
    DateToEmarDate(p^.ReturnBonusValidTo, fReturnBonusValidTo);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_13 }

procedure TEmar105_ReportEvent_13.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_13.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_13);
end;

procedure TEmar105_ReportEvent_13.GetFromData;
var
  p: PEmar105_ReportEvent_13;
begin
  inherited;
  if fKind = 13 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fIndexOfPayType := p^.IndexOfPayType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fPassangerCount := p^.PassangerCount;
    fPaidAmound := CalcCardinal(p^.PaidAmound);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fIsCardRecord := p^.IsCardRecord = 1;
    fTicketCode := ArrayToHex(p^.TicketCode, SizeOf(p^.TicketCode), True);
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fTicketPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
    FIsWronglyPrinted := TEmar105_File(Owner)._GetIsSimpleTicketWronglyPrinted(fTicketCode);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_13.SetToData;
var
  p: PEmar105_ReportEvent_13;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.IndexOfPayType := fIndexOfPayType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    p^.PassangerCount := fPassangerCount;
    p^.PaidAmound := CalcCardinal(fPaidAmound);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    if fIsCardRecord then p^.IsCardRecord := 1;
    HexToArray(p^.TicketCode, SizeOf(p^.TicketCode), fTicketCode);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_14 }

procedure TEmar105_ReportEvent_14.AllocDataMem;
begin
  fDataRecCount := 2;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_14.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_14);
end;

procedure TEmar105_ReportEvent_14.GetFromData;
var
  p: PEmar105_ReportEvent_14;
begin
  inherited;
  if fKind = 14 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2017-10-31 CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    fCardState := p^.CardState;
    fPermission := p^.Permission;
    fReduceCode := p^.ReduceCode;
    fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument));
    fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    // 2
    fLoyaltyProgramValidTo := EmarDateToString(p^.LoyaltyProgramValidTo);
    fTicketCount := p^.TicketCount;
    fFirstTicketSaleDate := EmarDateToString(p^.FirstTicketSaleDate);
    fDistance := CalcWord(p^.Distance);
    fTicketAmount := CalcCardinal(p^.TicketAmount);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_14.SetToData;
var
  p: PEmar105_ReportEvent_14;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 2;
    p^.CardNumber := fCardNumber; // ATY 2017-10-31 CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.CardState := fCardState;
    p^.Permission := fPermission;
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument), true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    DateToEmarDate(p^.LoyaltyProgramValidTo, fLoyaltyProgramValidTo);
    p^.TicketCount := fTicketCount;
    DateToEmarDate(p^.FirstTicketSaleDate, fFirstTicketSaleDate);
    p^.Distance := CalcWord(fDistance);
    p^.TicketAmount := CalcCardinal(fTicketAmount);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_15 }

procedure TEmar105_ReportEvent_15.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_15.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_15);
end;

procedure TEmar105_ReportEvent_15.GetFromData;
var
  p: PEmar105_ReportEvent_15;
begin
  inherited;
  if fKind = 15 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fIndexOfPayType := p^.IndexOfPayType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fPassangerCount := p^.PassangerCount;
    fPaidAmound := CalcCardinal(p^.PaidAmound);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fIndexOfReduce := p^.IndexOfReduce;
    fReduceCode := p^.ReduceCode;
    fIsCardRecord := p^.IsCardRecord = 1;
    fTicketCode := ArrayToHex(p^.TicketCode, SizeOf(p^.TicketCode), True);
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fTicketPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
    FIsWronglyPrinted := TEmar105_File(Owner)._GetIsSimpleTicketWronglyPrinted(fTicketCode);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_15.SetToData;
var
  p: PEmar105_ReportEvent_15;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.IndexOfPayType := fIndexOfPayType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    p^.PassangerCount := fPassangerCount;
    p^.PaidAmound := CalcCardinal(fPaidAmound);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    p^.IndexOfReduce := fIndexOfReduce;
    p^.ReduceCode := fReduceCode;
    if fIsCardRecord then p^.IsCardRecord := 1;
    HexToArray(p^.TicketCode, SizeOf(p^.TicketCode), fTicketCode);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_16 }

procedure TEmar105_ReportEvent_16.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_16.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_16);
end;

procedure TEmar105_ReportEvent_16.GetFromData;
var
  p: PEmar105_ReportEvent_16;
begin
  inherited;
  if fKind = 16 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fIndexOfPayType := p^.IndexOfPayType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fBaggageCount := p^.BaggageCount;
    fPaidAmound := CalcCardinal(p^.PaidAmound);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fTicketCode := ArrayToHex(p^.TicketCode, SizeOf(p^.TicketCode), True);
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fTicketPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
    FIsWronglyPrinted := TEmar105_File(Owner)._GetIsSimpleTicketWronglyPrinted(fTicketCode);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_16.SetToData;
var
  p: PEmar105_ReportEvent_16;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.IndexOfPayType := fIndexOfPayType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    p^.BaggageCount := fBaggageCount;
    p^.PaidAmound := CalcCardinal(fPaidAmound);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    HexToArray(p^.TicketCode, SizeOf(p^.TicketCode), fTicketCode);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_17 }

procedure TEmar105_ReportEvent_17.AllocDataMem;
begin
  fDataRecCount := 3;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_17.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_17);
end;

procedure TEmar105_ReportEvent_17.GetFromData;
var
  p:  PEmar105_ReportEvent_17;
  pd: PEmarDateTypeRec;
begin
  inherited;
  if fKind = 17 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2016-07-26: CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    // zadanie 57699
    if p^.ReduceType in [1, 2, 4] then begin
      fReduceCode := p^.ReduceCode;
      fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument) - 1);
      fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    end else begin
      fReduceCode := 0;
      fReduceDocument := '';
      fReduceDocumentValidTo := '';
    end;
    fReduceType := p^.ReduceType;
    fRideRemaining := p^.RideRemaining;
    // 2
    fTicketType := p^.TicketType;
    fTicketKind := p^.TicketKind;
    fTicketRelations := p^.TicketRelations;
    fValidForRoute := p^.ValidForRoute;
    fTicketValidFrom := EmarDateToString(p^.TicketValidFrom);
    fTicketValidTo := EmarDateToString(p^.TicketValidTo);
    fTicketNumber := CopyLStr(p^.TicketNumber, SizeOf(p^.TicketNumber) - 1);
    fTicketSaleDate := EmarDateToString(p^.TicketSaleDate);
    fTicketSaleTime := EmarTimeToString(p^.TicketSaleTime);
    fPaidRides := p^.PaidRides;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    // 3
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fRideCompany := CalcWord(p^.RideCompany);
    fRideNumber := CalcWord(p^.RideNumber);
    fRideTicketRelation := p^.RideTicketRelation;
    fTicketNewValidTo := EmarDateToString(p^.TicketNewValidTo);
    fExtCode := p^.ExtCode;
    fExtCount := p^.ExtCount;

    // multi field
    if fExtCode > 1 then begin
      pd := @p^.MultiField;
      fTicketNewValidFrom := EmarDateToString(pd^);
    end
    else fCardControlCode := ArrayToHex(p^.MultiField, SizeOf(p^.MultiField));

    fControlCode := ArrayToHex(p^.ControlCode, SizeOf(p^.ControlCode));
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_17.SetToData;
var
  p:  PEmar105_ReportEvent_17;
  pd: PEmarDateTypeRec;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 3;
    p^.CardNumber := fCardNumber; // ATY 2016-07-26: CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument) - 1, true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    p^.ReduceType := fReduceType;
    p^.RideRemaining := fRideRemaining;
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    p^.TicketType := fTicketType;
    p^.TicketKind := fTicketKind;
    p^.TicketRelations := fTicketRelations;
    p^.ValidForRoute := fValidForRoute;
    DateToEmarDate(p^.TicketValidFrom, fTicketValidFrom);
    DateToEmarDate(p^.TicketValidTo, fTicketValidTo);
    StrPLCopy(p^.TicketNumber, ansistring(fTicketNumber), SizeOf(p^.TicketNumber) - 1, true, #0);
    DateToEmarDate(p^.TicketSaleDate, fTicketSaleDate);
    TimeToEmarTime(p^.TicketSaleTime, fTicketSaleTime);
    p^.PaidRides := fPaidRides;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    // 3
    p^.rBegin3.Id := p^.rBegin1.Id;
    p^.rBegin3.Count := p^.rBegin1.Count;
    p^.rBegin3.Index := 3;
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), true, #0);
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.RideCompany := CalcWord(fRideCompany);
    p^.RideNumber := CalcWord(fRideNumber);
    p^.RideTicketRelation := fRideTicketRelation;
    DateToEmarDate(p^.TicketNewValidTo, fTicketNewValidTo);
    p^.ExtCode := fExtCode;
    p^.ExtCount := fExtCount;
    // multi field
    if fExtCode > 1 then begin
      pd := @p^.MultiField;
      DateToEmarDate(pd^, fTicketNewValidFrom);
    end
    else HexToArray(p^.MultiField, SizeOf(p^.MultiField), fCardControlCode);
    HexToArray(p^.ControlCode, SizeOf(p^.ControlCode), fControlCode);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_18 }

procedure TEmar105_ReportEvent_18.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_18.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_18);
end;

procedure TEmar105_ReportEvent_18.GetFromData;
var
  p: PEmar105_ReportEvent_18;
begin
  inherited;
  if fKind = 18 then begin
    p := pData;
    fState := p^.State;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_18.SetToData;
var
  p: PEmar105_ReportEvent_18;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.State := fState;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_19 }

procedure TEmar105_ReportEvent_19.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_19.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_19);
end;

procedure TEmar105_ReportEvent_19.GetFromData;
var
  p: PEmar105_ReportEvent_19;
begin
  inherited;
  if fKind = 19 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fPassangerCount := p^.PassangerCount;
    fReduceCode := p^.ReduceCode;
    fCompany := CalcWord(p^.Company);
    fBusStopCodeFrom := CalcCardinal(p^.BusStopCodeFrom);
    fBusStopCodeTo := CalcCardinal(p^.BusStopCodeTo);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_19.SetToData;
var
  p: PEmar105_ReportEvent_19;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.PassangerCount := fPassangerCount;
    p^.ReduceCode := fReduceCode;
    p^.Company := CalcWord(fCompany);
    p^.BusStopCodeFrom := CalcCardinal(fBusStopCodeFrom);
    p^.BusStopCodeTo := CalcCardinal(fBusStopCodeTo);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_20 }

procedure TEmar105_ReportEvent_20.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_20.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_20);
end;

procedure TEmar105_ReportEvent_20.GetFromData;
var
  p: PEmar105_ReportEvent_20;
begin
  inherited;
  if fKind = 20 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    fPassangerCountInBus := p^.PassangerCountInBus;
    fPassangerCountWithMountTickets := p^.PassangerCountWithMountTickets;
    fInspectorCardNumber := p^.InspectorCardNumber; // ATY 2017-10-31: CalcCardinal(p^.InspectorCardNumber);
    fInspectorCompany := CalcWord(p^.InspectorCompany);
    fPrint := p^.Print = $FF;
    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_20.SetToData;
var
  p: PEmar105_ReportEvent_20;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.PassangerCountInBus := fPassangerCountInBus;
    p^.PassangerCountWithMountTickets := fPassangerCountWithMountTickets;
    p^.InspectorCardNumber := fInspectorCardNumber; // ATY 2017-10-31: CalcCardinal(fInspectorCardNumber);
    p^.InspectorCompany := CalcWord(fInspectorCompany);
    if fPrint then p^.Print := $FF
    else p^.Print := 0;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_21 }

procedure TEmar105_ReportEvent_21.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_21.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_21);
end;

procedure TEmar105_ReportEvent_21.GetFromData;
var
  p: PEmar105_ReportEvent_21;
begin
  inherited;
  if fKind = 21 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fIndexOfPayType := p^.IndexOfPayType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    fPrice := CalcCardinal(p^.Price);
    fCount := p^.Count;
    fPaidAmound := CalcCardinal(p^.PaidAmound);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fIndexOfAdditionFee := CalcWord(p^.IndexOfAdditionFee);
    fTicketCode        := ArrayToHex(p^.TicketCode, SizeOf(p^.TicketCode));
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
    FIsWronglyPrinted := TEmar105_File(Owner)._GetIsSimpleTicketWronglyPrinted(fTicketCode);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_21.SetToData;
var
  p: PEmar105_ReportEvent_21;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.IndexOfPayType := fIndexOfPayType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    p^.Price := CalcCardinal(fPrice);
    p^.Count := fCount;
    p^.PaidAmound := CalcCardinal(fPaidAmound);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    p^.IndexOfAdditionFee := CalcWord(fIndexOfAdditionFee);
    HexToArray(p^.TicketCode, SizeOf(p^.TicketCode), fTicketCode);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_22 }

procedure TEmar105_ReportEvent_22.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_22.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_22);
end;

procedure TEmar105_ReportEvent_22.GetFromData;
var
  p: PEmar105_ReportEvent_22;
begin
  inherited;
  if fKind = 22 then begin
    p := pData;
    fPowerOffDate := EmarDateToString(p^.PowerOffDate);
    fPowerOffTime := EmarTimeToString(p^.PowerOffTime);
    fOperation := p^.Operation;
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fFiscalReport := CalcWord(p^.FiscalReport);
    fTicketRegisterState := p^.TicketRegisterState;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_22.SetToData;
var
  p: PEmar105_ReportEvent_22;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    DateToEmarDate(p^.PowerOffDate, fPowerOffDate);
    TimeToEmarTime(p^.PowerOffTime, fPowerOffTime);
    p^.Operation := fOperation;
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), true, #0);
    p^.FiscalReport := CalcWord(fFiscalReport);
    p^.TicketRegisterState := fTicketRegisterState;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_23 }

procedure TEmar105_ReportEvent_23.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_23.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_23);
end;

procedure TEmar105_ReportEvent_23.GetFromData;
var
  p: PEmar105_ReportEvent_23;
begin
  inherited;
  if fKind = 23 then begin
    p := pData;
    fBusStop := p^.BusStop;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_23.SetToData;
var
  p: PEmar105_ReportEvent_23;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStop := fBusStop;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_24 }

procedure TEmar105_ReportEvent_24.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_24.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_24);
end;

procedure TEmar105_ReportEvent_24.GetFromData;
var
  p: PEmar105_ReportEvent_24;
begin
  inherited;
  if fKind = 24 then begin
    p := pData;
    fBusStop := p^.BusStop;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_24.SetToData;
var
  p: PEmar105_ReportEvent_24;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStop := fBusStop;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_25 }

procedure TEmar105_ReportEvent_25.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_25.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_25);
end;

procedure TEmar105_ReportEvent_25.GetFromData;
var
  p: PEmar105_ReportEvent_25;
begin
  inherited;
  if fKind = 25 then begin
    p := pData;
    fTimeAfterChange := EmarTimeToString(p^.TimeAfterChange);
    fTimeChangeKind := p^.Kind;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_25.SetToData;
var
  p: PEmar105_ReportEvent_25;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    TimeToEmarTime(p^.TimeAfterChange, fTimeAfterChange);
    p^.Kind := fTimeChangeKind;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_26 }

procedure TEmar105_ReportEvent_26.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_26.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_26);
end;

procedure TEmar105_ReportEvent_26.GetFromData;
var
  p: PEmar105_ReportEvent_26;
begin
  inherited;
  if fKind = 26 then begin
    p := pData;
    fTicketNumber := CalcWord(p^.TicketNumber);
    //
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_26.SetToData;
var
  p: PEmar105_ReportEvent_26;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.TicketNumber := CalcWord(fTicketNumber);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_27 }

procedure TEmar105_ReportEvent_27.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_27.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_25);
end;

procedure TEmar105_ReportEvent_27.GetFromData;
var
  p: PEmar105_ReportEvent_27;
  i: integer;
begin
  inherited;
  if fKind = 27 then begin
    p := pData;
    for i := low(fPrintedReportsWithoutCard) to high(fPrintedReportsWithoutCard) do
        fPrintedReportsWithoutCard[i] := p^.Numbers[i];
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_27.SetToData;
var
  p: PEmar105_ReportEvent_27;
  i: integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    for i := low(fPrintedReportsWithoutCard) to high(fPrintedReportsWithoutCard) do
        p^.Numbers[i] := fPrintedReportsWithoutCard[i];
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_28 }

procedure TEmar105_ReportEvent_28.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_28.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_28);
end;

procedure TEmar105_ReportEvent_28.GetFromData;
var
  p: PEmar105_ReportEvent_28;
begin
  inherited;
  if fKind = 28 then begin
    p := pData;
    fCodeKind := p^.Kind;
    fFiscalDocDate := EmarDateToString(p^.FiscalDocDate);
    fFiscalDocTime := EmarTimeToString(p^.FiscalDocTime);
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fValid := (p^.Valid = 0);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_28.SetToData;
var
  p: PEmar105_ReportEvent_28;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    DateToEmarDate(p^.FiscalDocDate, fFiscalDocDate);
    TimeToEmarTime(p^.FiscalDocTime, fFiscalDocTime);
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), true, #0);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    if fValid then p^.Valid := 0
    else p^.Valid := 1;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_29 }

procedure TEmar105_ReportEvent_29.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_29.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_29);
end;

procedure TEmar105_ReportEvent_29.GetFromData;
var
  p: PEmar105_ReportEvent_29;
begin
  inherited;
  if fKind = 29 then begin
    p := pData;
    fTaskNumber := p^.TaskNumber;
    fTaskPosition := p^.TaskPosition;
    fReportRideIndex := CalcWord(p^.ReportRideIndex);
    fRideNumber := CalcWord(p^.RideNumber);
    fRidePage := CalcWord(p^.RidePage);
    fRideOffset := CalcWord(p^.RideOffset);
    fRideCode := CalcWord(p^.RideCode);
    fLastDocumentNumber := CalcCardinal(p^.LastDocumentNumber);
    fLastTicketNumber := CalcWord(p^.LastTicketNumber);
    //
    FLastTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fLastTicketNumber, False);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_29.SetToData;
var
  p: PEmar105_ReportEvent_29;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.TaskNumber := fTaskNumber;
    p^.TaskPosition := fTaskPosition;
    p^.ReportRideIndex := CalcWord(fReportRideIndex);
    p^.RideNumber := CalcWord(fRideNumber);
    p^.RidePage := CalcWord(fRidePage);
    p^.RideOffset := CalcWord(fRideOffset);
    p^.RideCode := CalcWord(fRideCode);
    p^.LastDocumentNumber := CalcCardinal(fLastDocumentNumber);
    p^.LastTicketNumber := CalcWord(fLastTicketNumber);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_30 }

procedure TEmar105_ReportEvent_30.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_30.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_30);
end;

procedure TEmar105_ReportEvent_30.GetFromData;
var
  p: PEmar105_ReportEvent_30;
begin
  inherited;
  if fKind = 30 then begin
    p := pData;
    fBusStopStart := p^.BusStopStart;
    fTicketKind := p^.TicketKind;
    fIndexOfPayType := p^.IndexOfPayType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fPassangerCount := p^.PassangerCount;
    fPaidAmound := CalcCardinal(p^.PaidAmound);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fIsCardRecord := p^.IsCardRecord = 1;
    fTicketCode := ArrayToHex(p^.TicketCode, SizeOf(p^.TicketCode), True);
    fTariffOffset := p^.TariffOffset;
    fPriceNumber := p^.PriceNumber;
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fTicketPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
    FIsWronglyPrinted := TEmar105_File(Owner)._GetIsSimpleTicketWronglyPrinted(fTicketCode);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_30.SetToData;
var
  p: PEmar105_ReportEvent_30;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.BusStopStart := fBusStopStart;
    p^.TicketKind := fTicketKind;
    p^.IndexOfPayType := fIndexOfPayType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    p^.PassangerCount := fPassangerCount;
    p^.PaidAmound := CalcCardinal(fPaidAmound);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    if fIsCardRecord then p^.IsCardRecord := 1;
    HexToArray(p^.TicketCode, SizeOf(p^.TicketCode), fTicketCode);
    p^.TariffOffset := fTariffOffset;
    p^.PriceNumber := fPriceNumber;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_31 }

procedure TEmar105_ReportEvent_31.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_31.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_31);
end;

procedure TEmar105_ReportEvent_31.GetFromData;
var
  p: PEmar105_ReportEvent_31;
begin
  inherited;
  if fKind = 31 then begin
    p := pData;
    fBusSideNumber := CopyLStr(p^.BusSideNumber, SizeOf(p^.BusSideNumber));
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_31.SetToData;
var
  p: PEmar105_ReportEvent_31;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.BusSideNumber, ansistring(fBusSideNumber), SizeOf(p^.BusSideNumber), false, #0);
    p^.Empty1[0] := $FF;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_32 }

procedure TEmar105_ReportEvent_32.AllocDataMem;
begin
  fDataRecCount := 3;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_32.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_32);
end;

procedure TEmar105_ReportEvent_32.GetFromData;
var
  p: PEmar105_ReportEvent_32;
begin
  inherited;
  if fKind = 32 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2017-10-31 CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    fReduceCode := p^.ReduceCode;
    fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument) - 1);
    fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    fReduceType := p^.ReduceType;
    fIndexOfCurrency := p^.IndexOfCurrency;
    // Emar-105 - nie obsługuje tego pola  (wartość $FF); Emar-205 - wartość > 0 oznacza zapłatę w walucie obcej; 0=waluta ewidencyjna
    // 2
    fTicketType := p^.TicketType;
    fTicketKind := p^.TicketKind;
    fTicketRelations := p^.TicketRelations;
    fValidForRoute := p^.ValidForRoute;
    fTicketValidFrom := EmarDateToString(p^.TicketValidFrom);
    fTicketValidTo := EmarDateToString(p^.TicketValidTo);
    fCardTicketNumber := CopyLStr(p^.CardTicketNumber, SizeOf(p^.CardTicketNumber) - 1);
    fTicketNewValidTo := EmarDateToString(p^.TicketNewValidTo);
    fExtCode := p^.ExtCode;
    fExtCount := p^.ExtCount;
    fTicketNewValidFrom := EmarDateToString(p^.TicketNewValidFrom);
    fExtKind := p^.ExtKind;
    fIndexOfPayType := p^.IndexOfPayType;
    // 3
    fPaidRides := p^.PaidRides;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fInCountry := p^.InCountry = 0;
    fPTU1 := p^.PTU1;
    fBrutto1 := CalcCardinal(p^.Brutto1);
    fReduce1 := CalcCardinal(p^.Reduce1);
    fPTU2 := p^.PTU2;
    fBrutto2 := CalcCardinal(p^.Brutto2);
    fReduce2 := CalcCardinal(p^.Reduce2);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fControlCode    := ArrayToHex(p^.ControlCode, SizeOf(p^.ControlCode), True);
    // -------------------------------------------------------------------------
    Owner.IsReportEvent32 := True;
    {
     dla Emar-105 - zawsze GOTÓWKA; dla Emar-205 – wypełnia pole przy zapłacie bezgotówkowej:
     0-GOTÓWKA
     1-KARTA PŁATNICZA
    }
    if (not TEmar105_File(Owner).F_IsEmar205) or (fIndexOfPayType = 0) then FNonCashInTicketPrice := 0
    else FNonCashInTicketPrice := fTicketPrice;
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, True);
    FBuyerNIP := '';
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

function TEmar105_ReportEvent_32.IsNotDuplicated: LongBool;
var
  i: Integer;
begin
  i := Pred(Self.IndexInReportsList);
  // AT: zamienić na GetEmCardTicketProlongingID z SalesReport modula
  while i > 0 do begin
    if (TEmar105_File(Self.Owner).ReportEventList[i].Kind = 32) and
      (not TEmar105_File(Self.Owner).ReportEventList[i].IsError(reErrorPartMissing2 or reErrorCheckSum2))
    // rekord #2 jest poprawny
      and (not TEmar105_File(Self.Owner).ReportEventList[i].IsError(reErrorPartMissing3 or reErrorCheckSum3))
    // rekord #3 jest poprawny
      and (TEmar105_File(Self.Owner).ReportEventList[i].AsEvent_32.CardNumber = Self.CardNumber) and
      (string(TEmar105_File(Self.Owner).ReportEventList[i].AsEvent_32.CardTicketNumber) = string(Self.CardTicketNumber))
      and (TEmar105_File(Self.Owner).ReportEventList[i].AsEvent_32.ExtCount = Self.ExtCount) then Break
    else Dec(i);
  end;
  Result := i < 0; // nie został znaleziony
end;

procedure TEmar105_ReportEvent_32.SetToData;
var
  p: PEmar105_ReportEvent_32;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 3;
    p^.CardNumber := fCardNumber; // ATY 2017-10-31 CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument) - 1, true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    p^.ReduceType := fReduceType;
    p^.IndexOfCurrency := fIndexOfCurrency;
    // Emar-105 - nie obsługuje tego pola  (wartość $FF); Emar-205 - wartość > 0 oznacza zapłatę w walucie obcej; 0=waluta ewidencyjna

    // 2
    if not FFRecordsID[2] then begin
      p^.rBegin2.Id := p^.rBegin1.Id;
      p^.rBegin2.Count := p^.rBegin1.Count;
      p^.rBegin2.Index := 2;
      p^.TicketType := fTicketType;
      p^.TicketKind := fTicketKind;
      p^.TicketRelations := fTicketRelations;
      p^.ValidForRoute := fValidForRoute;
      DateToEmarDate(p^.TicketValidFrom, fTicketValidFrom);
      DateToEmarDate(p^.TicketValidTo, fTicketValidTo);
      StrPLCopy(p^.CardTicketNumber, ansistring(fCardTicketNumber), SizeOf(p^.CardTicketNumber) - 1, true, #0);
      DateToEmarDate(p^.TicketNewValidTo, fTicketNewValidTo);
      p^.ExtCode := fExtCode;
      p^.ExtCount := fExtCount;
      DateToEmarDate(p^.TicketNewValidFrom, fTicketNewValidFrom);
      p^.ExtKind := fExtKind;
      p^.IndexOfPayType := fIndexOfPayType;
    end;

    // 3
    if not FFRecordsID[3] then begin
      p^.rBegin3.Id := p^.rBegin1.Id;
      p^.rBegin3.Count := p^.rBegin1.Count;
      p^.rBegin3.Index := 3;
      p^.PaidRides := fPaidRides;
      p^.TicketPrice := CalcCardinal(fTicketPrice);
      if fInCountry then p^.InCountry := 0
      else p^.InCountry := 1;
      p^.PTU1 := fPTU1;
      p^.Brutto1 := CalcCardinal(fBrutto1);
      p^.Reduce1 := CalcCardinal(fReduce1);
      p^.PTU2 := fPTU2;
      p^.Brutto2 := CalcCardinal(fBrutto2);
      p^.Reduce2 := CalcCardinal(fReduce2);
      p^.DocumentNumber := CalcCardinal(fDocumentNumber);
      p^.TicketNumber := CalcWord(fTicketNumber);
      HexToArray(p^.ControlCode, SizeOf(p^.ControlCode), fControlCode);
    end;
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if (not FFRecordsID[2]) and (not IsError(reErrorPartMissing2 or reErrorCheckSum2)) then
    // nie przeliczamy gdy w pliku źródłowym był jakikolwiek błąd
        p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if (not FFRecordsID[3]) and (not IsError(reErrorPartMissing3 or reErrorCheckSum3)) then
    // nie przeliczamy gdy w pliku źródłowym był jakikolwiek błąd
        p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);

    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_33 }

procedure TEmar105_ReportEvent_33.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_33.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_33);
end;

procedure TEmar105_ReportEvent_33.GetFromData;
var
  p: PEmar105_ReportEvent_33;
begin
  inherited;
  if fKind = 33 then begin
    p := pData;
    fCardNumber := p^.CardNumber; // ATY 2016-08-05: CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    fReduceCode := p^.ReduceCode;
    fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument) - 1);
    fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    fReduceType := p^.ReduceType;
    fErrorCode := p^.ErrorCode;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_33.SetToData;
var
  p: PEmar105_ReportEvent_33;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.CardNumber := fCardNumber; // ATY 2016-08-05: CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument) - 1, true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    p^.ReduceType := fReduceType;
    p^.ErrorCode := fErrorCode;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_34 }

procedure TEmar105_ReportEvent_34.AllocDataMem;
begin
  fDataRecCount := 3;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_34.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_34);
end;

procedure TEmar105_ReportEvent_34.GetFromData;
var
  p:  PEmar105_ReportEvent_34;
  pd: PEmarDateTypeRec;
begin
  inherited;
  if fKind = 34 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2016-08-05: CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    // zadanie 57699
    if p^.ReduceType in [1, 2, 4] then begin
      fReduceCode := p^.ReduceCode;
      fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument) - 1);
      fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    end else begin
      fReduceCode := 0;
      fReduceDocument := '';
      fReduceDocumentValidTo := '';
    end;
    fReduceType := p^.ReduceType;
    fErrorCode := p^.ErrorCode;
    // 2
    fTicketType := p^.TicketType;
    fTicketKind := p^.TicketKind;
    fTicketRelations := p^.TicketRelations;
    fValidForRoute := p^.ValidForRoute;
    fTicketValidFrom := EmarDateToString(p^.TicketValidFrom);
    fTicketValidTo := EmarDateToString(p^.TicketValidTo);
    fTicketNumber := CopyLStr(p^.TicketNumber, SizeOf(p^.TicketNumber) - 1);
    fTicketSaleDate := EmarDateToString(p^.TicketSaleDate);
    fTicketSaleTime := EmarTimeToString(p^.TicketSaleTime);
    fExtCount := p^.ExtCount;
    fPaidRides := p^.PaidRides;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    // 3
    fTicketRegister := CopyLStr(p^.TicketRegister, SizeOf(p^.TicketRegister));
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
    fRideCompany := CalcWord(p^.RideCompany);
    fRideNumber := CalcWord(p^.RideNumber);
    fRideTicketRelation := p^.RideTicketRelation;
    fTicketNewValidTo := EmarDateToString(p^.TicketNewValidTo);
    fExtCode := p^.ExtCode;
    // multi field
    if fExtCode > 1 then begin
      pd := @p^.MultiField;
      fTicketNewValidFrom := EmarDateToString(pd^);
    end
    else fCardControlCode := ArrayToHex(p^.MultiField, SizeOf(p^.MultiField));
    // fControlCode       := ArrayToHex(p^.ControlCode, SizeOf(p^.ControlCode));
    fCardStates[1] := p^.CardStates[1];
    fCardStates[2] := p^.CardStates[2];
    fCardStates[3] := p^.CardStates[3];
    fExtErrorCode := p^.ExtErrorCode;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_34.SetToData;
var
  p:  PEmar105_ReportEvent_34;
  pd: PEmarDateTypeRec;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 3;
    p^.CardNumber := fCardNumber; // ATY 2016-08-05: CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument) - 1, true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    p^.ReduceType := fReduceType;
    p^.ErrorCode := fErrorCode;
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    p^.TicketType := fTicketType;
    p^.TicketKind := fTicketKind;
    p^.TicketRelations := fTicketRelations;
    p^.ValidForRoute := fValidForRoute;
    DateToEmarDate(p^.TicketValidFrom, fTicketValidFrom);
    DateToEmarDate(p^.TicketValidTo, fTicketValidTo);
    StrPLCopy(p^.TicketNumber, ansistring(fTicketNumber), SizeOf(p^.TicketNumber) - 1, true, #0);
    DateToEmarDate(p^.TicketSaleDate, fTicketSaleDate);
    TimeToEmarTime(p^.TicketSaleTime, fTicketSaleTime);
    p^.ExtCount := fExtCount;
    p^.PaidRides := fPaidRides;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    // 3
    p^.rBegin3.Id := p^.rBegin1.Id;
    p^.rBegin3.Count := p^.rBegin1.Count;
    p^.rBegin3.Index := 3;
    StrPLCopy(p^.TicketRegister, ansistring(fTicketRegister), SizeOf(p^.TicketRegister), true, #0);
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    p^.RideCompany := CalcWord(fRideCompany);
    p^.RideNumber := CalcWord(fRideNumber);
    p^.RideTicketRelation := fRideTicketRelation;
    DateToEmarDate(p^.TicketNewValidTo, fTicketNewValidTo);
    p^.ExtCode := fExtCode;
    // multi field
    if fExtCode > 1 then begin
      pd := @p^.MultiField;
      DateToEmarDate(pd^, fTicketNewValidFrom);
    end
    else HexToArray(p^.MultiField, SizeOf(p^.MultiField), fCardControlCode);
    // HexToArray(p^.ControlCode, SizeOf(p^.ControlCode), fControlCode);
    p^.CardStates[1] := fCardStates[1];
    p^.CardStates[2] := fCardStates[2];
    p^.CardStates[3] := fCardStates[3];
    p^.ExtErrorCode := fExtErrorCode;
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if (not FFRecordsID[2]) and (not IsError(reErrorPartMissing2 or reErrorCheckSum2)) then
    // nie przeliczamy gdy w pliku źródłowym był jakikolwiek błąd
        p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if (not FFRecordsID[3]) and (not IsError(reErrorPartMissing3 or reErrorCheckSum3)) then
    // nie przeliczamy gdy w pliku źródłowym był jakikolwiek błąd
        p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_35 }

procedure TEmar105_ReportEvent_35.AllocDataMem;
begin
  fDataRecCount := 3;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_35.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_35);
end;

procedure TEmar105_ReportEvent_35.GetFromData;
var
  p: PEmar105_ReportEvent_35;
begin
  inherited;
  if fKind = 35 then begin
    p := pData;
    // 1
    fCardNumber := p^.CardNumber; // ATY 2017-10-31 CalcCardinal(p^.CardNumber);
    fSaleCompany := CalcWord(p^.SaleCompany);
    fReduceCode := p^.ReduceCode;
    fReduceDocument := CopyLStr(p^.ReduceDocument, SizeOf(p^.ReduceDocument) - 1);
    fReduceDocumentValidTo := EmarDateToString(p^.ReduceDocumentValidTo);
    fReduceType := p^.ReduceType;
    fCardState3 := p^.CardState3;
    // 2
    fTicketType := p^.TicketType;
    fTicketKind := p^.TicketKind;
    fTicketRelations := p^.TicketRelations;
    fValidForRoute := p^.ValidForRoute;
    fTicketValidFrom := EmarDateToString(p^.TicketValidFrom);
    fTicketValidTo := EmarDateToString(p^.TicketValidTo);
    fCardTicketNumber := CopyLStr(p^.CardTicketNumber, SizeOf(p^.CardTicketNumber) - 1);
    fTicketNewValidTo := EmarDateToString(p^.TicketNewValidTo);
    fExtCode := p^.ExtCode;
    fExtCount := p^.ExtCount;
    fTicketNewValidFrom := EmarDateToString(p^.TicketNewValidFrom);
    // 3
    fPaidRides := p^.PaidRides;
    fTicketPrice := CalcCardinal(p^.TicketPrice);
    fInCountry := p^.InCountry = 0;
    fPTU1 := p^.PTU1;
    fBrutto1 := CalcCardinal(p^.Brutto1);
    fReduce1 := CalcCardinal(p^.Reduce1);
    fPTU2 := p^.PTU2;
    fBrutto2 := CalcCardinal(p^.Brutto2);
    fReduce2 := CalcCardinal(p^.Reduce2);
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fControlCode    := ArrayToHex(p^.ControlCode, SizeOf(p^.ControlCode), True);
    // -------------------------------------------------------------------------
    Owner.IsReportEvent35 := True;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_35.SetToData;
var
  p: PEmar105_ReportEvent_35;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 3;
    p^.CardNumber := fCardNumber; // ATY 2017-10-31 CalcCardinal(fCardNumber);
    p^.SaleCompany := CalcWord(fSaleCompany);
    p^.ReduceCode := fReduceCode;
    StrPLCopy(p^.ReduceDocument, ansistring(fReduceDocument), SizeOf(p^.ReduceDocument) - 1, true, #0);
    DateToEmarDate(p^.ReduceDocumentValidTo, fReduceDocumentValidTo);
    p^.ReduceType := fReduceType;
    p^.CardState3 := fCardState3;
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    p^.TicketType := fTicketType;
    p^.TicketKind := fTicketKind;
    p^.TicketRelations := fTicketRelations;
    p^.ValidForRoute := fValidForRoute;
    DateToEmarDate(p^.TicketValidFrom, fTicketValidFrom);
    DateToEmarDate(p^.TicketValidTo, fTicketValidTo);
    StrPLCopy(p^.CardTicketNumber, ansistring(fCardTicketNumber), SizeOf(p^.CardTicketNumber) - 1, true, #0);
    DateToEmarDate(p^.TicketNewValidTo, fTicketNewValidTo);
    p^.ExtCode := fExtCode;
    p^.ExtCount := fExtCount;
    DateToEmarDate(p^.TicketNewValidFrom, fTicketNewValidFrom);
    // 3
    p^.rBegin3.Id := p^.rBegin1.Id;
    p^.rBegin3.Count := p^.rBegin1.Count;
    p^.rBegin3.Index := 3;
    fPaidRides := fPaidRides;
    p^.TicketPrice := CalcCardinal(fTicketPrice);
    if fInCountry then p^.InCountry := 0
    else p^.InCountry := 1;
    p^.PTU1 := fPTU1;
    p^.Brutto1 := CalcCardinal(fBrutto1);
    p^.Reduce1 := CalcCardinal(fReduce1);
    p^.PTU2 := fPTU2;
    p^.Brutto2 := CalcCardinal(fBrutto2);
    p^.Reduce2 := CalcCardinal(fReduce2);
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
    HexToArray(p^.ControlCode, SizeOf(p^.ControlCode), fControlCode);
    // check sums
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum3 := EmarXORSum(p^.rBegin3, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_36 }

procedure TEmar105_ReportEvent_36._RecalculateTicketPrices();
  procedure _SetNonCashInTicketPrice(AEvent: IEmar_ReportEvent; ANonCashValue: Cardinal);
  begin
    case AEvent.Kind of
    13: AEvent.AsEvent_13._NonCashInTicketPrice := ANonCashValue;
    15: AEvent.AsEvent_15._NonCashInTicketPrice := ANonCashValue;
    16: AEvent.AsEvent_16._NonCashInTicketPrice := ANonCashValue;
    21: AEvent.AsEvent_21._NonCashInTicketPrice := ANonCashValue;
    30: AEvent.AsEvent_30._NonCashInTicketPrice := ANonCashValue;
    32: AEvent.AsEvent_32._NonCashInTicketPrice := ANonCashValue;
    end;
  end;

var
  r1ok, r2ok, r3ok:                                         Boolean;
  iRecord, lrek:                                            Integer;
  i36TicketsCash, i36TicketsNonCash, i36TicketsAmountToPay: Cardinal;
  i36TicketsCash_Tmp, i36TicketsNonCash_Tmp, i36TicketsAmountToPay_Tmp: Cardinal;
  i36TicketPrice{ , i36TicketPriceAbroad, i36Amount }: Cardinal;
  sTicketCurrency, s36CurrencyDefSymbol:               string;
  rel:                                                 IEmar_ReportEvent;

  _Emar_Currency_Ticket: IEmar_CurrencyExchange;
begin
  // przeliczane wyłącznie dla Emar-205
  if TEmar105_File(Owner).F_IsEmar205 then begin // musimy przeliczyć poprzednie bilety
    i36TicketsAmountToPay := Self.TicketAmount;
    case Self.PaidWithoutCash of
    1: // wpłata w walucie 1 jest bezgotówkowa
      begin
        if Currency2Amount = $FFFFFFFF then i36TicketsCash := - Self.Rest // ???
        else i36TicketsCash := Self.Currency2Amount - Self.Rest;
        i36TicketsNonCash := Self.Currency1Amount;
      end;
    2: // wpłata w walucie 2 jest bezgotówkowa
      begin
        i36TicketsCash := Self.Currency1Amount - Self.Rest;
        if Self.Currency2Amount = $FFFFFFFF then i36TicketsNonCash := 0
        else i36TicketsNonCash := Self.Currency2Amount;
      end;
    else // $FF-tylko gotówka
      begin
        if Self.Currency2Amount = $FFFFFFFF then i36TicketsCash := Self.Currency1Amount - Self.Rest
        else i36TicketsCash := Self.Currency1Amount + Self.Currency2Amount - Self.Rest;
        i36TicketsNonCash := 0;
      end;
    end;

    s36CurrencyDefSymbol := string(TEmar105_File(Owner).Consts.CurrencyCode);
    // AnsiUpperCase(TCurrency.GetDefaultSymbol(dmMain));
    i36TicketsCash_Tmp := i36TicketsCash;
    i36TicketsNonCash_Tmp := i36TicketsNonCash;
    i36TicketsAmountToPay_Tmp := i36TicketsAmountToPay;
    for iRecord := Pred(IndexInReportsList) downto 0 do begin
      rel := Self.Owner.ReportEventList.Items[iRecord];
      lrek := rel.ReportRecordCount;
      r1ok := (lrek > 0) and not rel.IsError(reErrorPartMissing1 or reErrorCheckSum1);
      r2ok := (lrek < 2) or (lrek > 1) and not rel.IsError(reErrorPartMissing2 or reErrorCheckSum2);
      r3ok := (lrek < 3) or (lrek > 2) and not rel.IsError(reErrorPartMissing3 or reErrorCheckSum3);

      if (not r1ok) or (not r2ok) or (not r3ok) then begin // ma błędy
        rel := nil;                                        // nie bilet
        i36TicketPrice := 0;
      end
      else
        case rel.Kind of
        13: begin
            if rel.AsEvent_13.IndexOfCurrency = 0 then sTicketCurrency := s36CurrencyDefSymbol
            else begin
              _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_13.IndexOfCurrency];
              sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
            end;
            i36TicketPrice := rel.AsEvent_13.TicketPrice;
          end;
        15: begin
            if rel.AsEvent_15.IndexOfCurrency = 0 then sTicketCurrency := s36CurrencyDefSymbol
            else begin
              _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_15.IndexOfCurrency];
              sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
            end;
            i36TicketPrice := rel.AsEvent_15.TicketPrice;
          end;
        16: begin
            if rel.AsEvent_16.IndexOfCurrency = 0 then sTicketCurrency := s36CurrencyDefSymbol
            else begin
              _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_16.IndexOfCurrency];
              sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
            end;
            i36TicketPrice := rel.AsEvent_16.TicketPrice;
          end;
        21: begin
            if rel.AsEvent_21.IndexOfCurrency = 0 then sTicketCurrency := s36CurrencyDefSymbol
            else begin
              _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_21.IndexOfCurrency];
              sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
            end;
            i36TicketPrice := rel.AsEvent_21.Price;
          end;
        30: begin
            if rel.AsEvent_30.IndexOfCurrency = 0 then sTicketCurrency := s36CurrencyDefSymbol
            else begin
              _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_30.IndexOfCurrency];
              sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
            end;
            i36TicketPrice := rel.AsEvent_30.TicketPrice;
          end;
        32: begin
            if not rel.AsEvent_32.IsDuplicated then begin
              if (rel.AsEvent_32.IndexOfCurrency = $FF) or (rel.AsEvent_32.IndexOfCurrency = 0) then
                  sTicketCurrency := s36CurrencyDefSymbol
              else begin
                _Emar_Currency_Ticket := Self.Owner.CurrencyExchangeList.Items[rel.AsEvent_32.IndexOfCurrency];
                sTicketCurrency := AnsiUpperCase(string(_Emar_Currency_Ticket.Currency));
              end;
              i36TicketPrice := rel.AsEvent_32.TicketPrice;
            end
            else // ignorujemy ten rekord, ponieważ jest on kopiją
            begin
              rel := nil; // nie bilet
              i36TicketPrice := 0;
            end;
          end;
        else
          begin
            rel := nil; // nie bilet
            i36TicketPrice := 0;
          end;
        end;

      if Assigned(rel) then
        if (Self.PaidWithoutCash = 1)                  // waluta 1 bezgotówkowa
          and (sTicketCurrency = s36CurrencyDefSymbol) // wpłata bezgotówkowa jest zawsze w walucie ewidencyjnej
          and (sTicketCurrency = AnsiUpperCase(string(Self.Currency1))) or (Self.PaidWithoutCash = 2)
        // AT: sprawdź dla waluty #2: waluta 2 bezgotówkowa
          and (sTicketCurrency = s36CurrencyDefSymbol) // wpłata bezgotówkowa jest zawsze w walucie ewidencyjnej
          and (sTicketCurrency = AnsiUpperCase(string(Self.Currency2))) then begin
          if i36TicketPrice <= i36TicketsNonCash_Tmp then begin
            _SetNonCashInTicketPrice(rel, i36TicketPrice); // karta płatnicza
            // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvCreditCard); // karta płatnicza
            // fr.TicketList[iRecord].PaymentType.Changed := False;
            // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
            //
            // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;

            Dec(i36TicketsNonCash_Tmp, i36TicketPrice);
          end
          else // mieszana
          begin
            if i36TicketsNonCash_Tmp > 0 then begin
              _SetNonCashInTicketPrice(rel, i36TicketsNonCash_Tmp); // Mieszana opłata
              // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvMixed); // Mieszana opłata
              // fr.TicketList[iRecord].PaymentType.Changed := False;
              // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
              // {$REGION           'Dodawanie podziału opłat'}
              // i36Amount := i36TicketsNonCash_Tmp;
              // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;
              // fr.TicketList[iRecord].AddTicketPaymentTypeEMAR205Values(Ord(ptvCreditCard), i36Amount); // karta płatnicza
              // {$ENDREGION}
              Dec(i36TicketPrice, i36TicketsNonCash_Tmp);
              i36TicketsNonCash_Tmp := 0;
            end else begin
              _SetNonCashInTicketPrice(rel, 0); // gotówka
              // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvCash); // gotówka
              // fr.TicketList[iRecord].PaymentType.Changed := False;
              // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
              //
              // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;
            end;

            if (i36TicketPrice > 0) and (i36TicketsCash_Tmp > 0) then begin
              if (i36TicketPrice <= i36TicketsCash_Tmp) then begin
                // i36Amount := i36TicketPrice;
                Dec(i36TicketsCash_Tmp, i36TicketPrice);
              end else begin
                // i36Amount := i36TicketsCash_Tmp;
                i36TicketsCash_Tmp := 0;
              end;
              // {$REGION           'Dodawanie podziału opłat'}
              // if fr.TicketList[iRecord].PaymentType.Id = Ord(ptvMixed) then // Mieszana opłata
              // fr.TicketList[iRecord].AddTicketPaymentTypeEMAR205Values(Ord(ptvCash), i36Amount); // gotówka
              // {$ENDREGION}
            end;
          end;
        end
        else // zapłata za bilet była bezgotówką, a teraz gotówka
        begin
          if i36TicketPrice <= i36TicketsCash_Tmp then begin
            _SetNonCashInTicketPrice(rel, 0); // gotówka
            // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvCash); // gotówka
            // fr.TicketList[iRecord].PaymentType.Changed := False;
            // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
            //
            // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;

            Dec(i36TicketsCash_Tmp, i36TicketPrice);
          end
          else // mieszana
          begin
            if i36TicketsCash_Tmp > 0 then begin
              _SetNonCashInTicketPrice(rel, i36TicketPrice - i36TicketsCash_Tmp); // Mieszana opłata
              // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvMixed); // Mieszana opłata
              // fr.TicketList[iRecord].PaymentType.Changed := False;
              // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
              // {$REGION             'Dodawanie podziału opłat'}
              // i36Amount := i36TicketsCash_Tmp;
              // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;
              // fr.TicketList[iRecord].AddTicketPaymentTypeEMAR205Values(Ord(ptvCash), i36Amount); // gotówka
              // {$ENDREGION}
              Dec(i36TicketPrice, i36TicketsCash_Tmp);
              i36TicketsCash_Tmp := 0;
            end else begin
              _SetNonCashInTicketPrice(rel, i36TicketPrice); // karta płatnicza
              // fr.TicketList[iRecord].PaymentType.Id := Ord(ptvCreditCard); // karta płatnicza
              // fr.TicketList[iRecord].PaymentType.Changed := False;
              // fr.TicketList[iRecord].PaymentType_ID := fr.TicketList[iRecord].PaymentType.Id;
              //
              // fr.TicketList[iRecord].TicketPaymentTypeEMAR205List.Clear;
            end;

            if (i36TicketPrice > 0) and (i36TicketsNonCash_Tmp > 0) then begin
              if (i36TicketPrice <= i36TicketsNonCash_Tmp) then begin
                // i36Amount := i36TicketPrice;
                Dec(i36TicketsNonCash_Tmp, i36TicketPrice);
              end else begin
                // i36Amount := i36TicketsNonCash_Tmp;
                i36TicketsNonCash_Tmp := 0;
              end;
              // {$REGION             'Dodawanie podziału opłat'}
              // if fr.TicketList[iRecord].PaymentType.Id = Ord(ptvMixed) then // Mieszana opłata
              // fr.TicketList[iRecord].AddTicketPaymentTypeEMAR205Values(Ord(ptvCreditCard), i36Amount); // karta płatnicza
              // {$ENDREGION}
            end;
          end;
        end;

      if (i36TicketsCash_Tmp = 0) and (i36TicketsNonCash_Tmp = 0) then Break;
    end;
    if (i36TicketsCash_Tmp <> 0) or (i36TicketsNonCash_Tmp <> 0) or (i36TicketsAmountToPay_Tmp <> 0) then begin
      // AddToDesc('Wpłaty w walutach obcych (EMAR-105) oraz zmiana sposobu zapłaty (EMAR-205): Nie zgadzają się ceny biletów', True);
      // Exit;
    end;
  end;
end;

procedure TEmar105_ReportEvent_36.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_36.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_36);
end;

procedure TEmar105_ReportEvent_36.GetFromData;
var
  p: PEmar105_ReportEvent_36;
begin
  inherited;
  if fKind = 36 then begin
    p := pData;
    fTicketAmount := CalcCardinal(p^.TicketAmount);
    fCurrencyTable := p^.CurrencyTable;
    fCurrency1 := CopyLStr(p^.Currency1, SizeOf(p^.Currency1) - 1);
    fCurrency1Amount := CalcCardinal(p^.Currency1Amount);
    fCurrency2 := CopyLStr(p^.Currency2, SizeOf(p^.Currency2) - 1);
    fCurrency2Amount := CalcCardinal(p^.Currency2Amount);
    fRest := CalcCardinal(p^.Rest);
    fRestCurrency := p^.RestCurrency;
    fPaidWithoutCash := p^.PaidWithoutCash;

    //
    _RecalculateTicketPrices();
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_36.SetToData;
var
  p: PEmar105_ReportEvent_36;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.TicketAmount := CalcCardinal(fTicketAmount);
    p^.CurrencyTable := CurrencyTable;
    StrPLCopy(p^.Currency1, ansistring(fCurrency1), SizeOf(p^.Currency1) - 1, true, #0);
    p^.Currency1Amount := CalcCardinal(fCurrency1Amount);
    StrPLCopy(p^.Currency2, ansistring(fCurrency2), SizeOf(p^.Currency2) - 1, true, #0);
    p^.Currency2Amount := CalcCardinal(fCurrency2Amount);
    p^.Rest := CalcCardinal(fRest);
    p^.RestCurrency := fRestCurrency;
    p^.PaidWithoutCash := fPaidWithoutCash;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_37 }

procedure TEmar105_ReportEvent_37.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_37.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_37);
end;

procedure TEmar105_ReportEvent_37.GetFromData;
var
  p: PEmar105_ReportEvent_37;
begin
  inherited;
  if fKind = 37 then begin
    p := pData;
    fDriverNumber := CalcCardinal(p^.DriverNumber);
    fCardNumber := CalcCardinal(p^.CardNumber);
    fTicketCount := CalcWord(p^.TicketCount);
    fTicketAmount := CalcWord(p^.TicketAmount);
    fAdditionalFeeCount := CalcWord(p^.AdditionalFeeCount);
    fAdditionalFeeAmount := CalcCardinal(p^.AdditionalFeeAmount);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_37.SetToData;
var
  p: PEmar105_ReportEvent_37;
  i: Integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    p^.DriverNumber := CalcCardinal(fDriverNumber);
    p^.CardNumber := CalcCardinal(fCardNumber);
    p^.TicketCount := CalcWord(fTicketCount);
    p^.TicketAmount := CalcWord(fTicketAmount);
    p^.AdditionalFeeCount := CalcWord(fAdditionalFeeCount);
    p^.AdditionalFeeAmount := CalcCardinal(fAdditionalFeeAmount);
    for i := 0 to Length(p^.Empty1) do p^.Empty1[i] := $FF;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_38 }

procedure TEmar105_ReportEvent_38.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_38.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_38);
end;

procedure TEmar105_ReportEvent_38.GetFromData;
var
  p: PEmar105_ReportEvent_38;
begin
  inherited;
  if fKind = 38 then begin
    p := pData;
    fCurrencyCode := CopyLStr(p^.CurrencyCode, SizeOf(p^.CurrencyCode) - 1);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_38.SetToData;
var
  p: PEmar105_ReportEvent_38;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.CurrencyCode, ansistring(fCurrencyCode), SizeOf(p^.CurrencyCode) - 1, true, #0);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_40 }

procedure TEmar105_ReportEvent_40.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_40.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_40);
end;

procedure TEmar105_ReportEvent_40.GetFromData(aData: pointer);
var
  p: PEmar105_ReportEvent_40;
begin
  inherited;
  if fKind = 40 then begin
    p := pData;
    fDDFileName := CopyLStr(p^.DDFileName, SizeOf(p^.DDFileName) - 1);
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_40.SetToData(aData: pointer);
var
  p: PEmar105_ReportEvent_40;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    StrPLCopy(p^.DDFileName, ansistring(fDDFileName), SizeOf(p^.DDFileName) - 1, true, #0);
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_41 }

procedure TEmar105_ReportEvent_41.AllocDataMem;
begin
  fDataRecCount := 2;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_41.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_41);
end;

procedure TEmar105_ReportEvent_41.GetFromData(aData: pointer);
var
  p: PEmar105_ReportEvent_41;
  i: integer;
  c: char;
begin
  inherited;
  if fKind = 41 then begin
    p := pData;
    fCompanyINumber := CalcWord(p^.CompanyINumber);
    fDeviceUniqueNumber := '';
    for i := low(p^.DeviceUniqueNumber) to high(p^.DeviceUniqueNumber) - 1 do
        fDeviceUniqueNumber := fDeviceUniqueNumber + IntToHex(p^.DeviceUniqueNumber[i], 2);
    if p^.BuildFirmwareVersion = $FF then
      fFirmwareVersion := Format('%u.%.2u', [p^.MajorFirmwareVersion, p^.MinorFirmwareVersion])
    else
      fFirmwareVersion := Format('%u.%.2u.%.2u', [p^.MajorFirmwareVersion, p^.MinorFirmwareVersion, p^.BuildFirmwareVersion]);
    fDeviceServiceNumber := CalcCardinal(p^.DeviceServiceNumber);
    fFiscalPrinterNumber := CopyLStr(p^.FiscalPrinterNumber, SizeOf(p^.FiscalPrinterNumber) - 1);
    for c := 'A' to 'G' do fTaxRates[c] := CalcWord(p^.TaxRates[c]);
    if (p^.FiscalPrinterMajorFirmwareVersion = $FF) and (p^.FiscalPrinterMinorFirmwareVersion = $FF) then begin
    // set v 1.00
      p^.FiscalPrinterMajorFirmwareVersion := 1;
      p^.FiscalPrinterMinorFirmwareVersion := 0;
    end;
    fFiscalPrinterFirmwareVersion := Format('%u.%.2u', [p^.FiscalPrinterMajorFirmwareVersion,
      p^.FiscalPrinterMinorFirmwareVersion]);
    // -------------------------------------------------------------------------
    Owner.IsReportEvent41 := True;
    TEmar105_File(Owner).F_IsEmar205 := True;
  end else begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_41.SetToData(aData: pointer);
var
  p:    PEmar105_ReportEvent_41;
  i, j, iPos1, iPos2: integer;
  c:    char;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then begin
    p := pData;
    // 1
    p^.rBegin1.Count := 2;
    p^.CompanyINumber := CalcWord(word(fCompanyINumber));
    FillChar(p^.DeviceUniqueNumber, SizeOf(p^.DeviceUniqueNumber), 0);
    i := 1;
    j := 0;
    while i < Length(fDeviceUniqueNumber) do begin
      p^.DeviceUniqueNumber[j] := StrToInt('$' + Copy(fDeviceUniqueNumber, i, 2));
      Inc(i, 2);
      Inc(j);
    end;
    iPos1 := Pos('.', fFirmwareVersion);
    if (fFirmwareVersion <> '')and(iPos1 > 0) then begin
      p^.MajorFirmwareVersion := StrToIntDef(Copy(fFirmwareVersion, 1, iPos1 - 1), 0);
      p^.MinorFirmwareVersion := StrToIntDef(Copy(fFirmwareVersion, iPos1 + 1, 2), 0);
      iPos2 := Pos('.', Copy(fFirmwareVersion, iPos1 + 1, Length(fFirmwareVersion) - iPos1)) + iPos1;
      if iPos2 > iPos1 then
        p^.BuildFirmwareVersion := StrToIntDef(Copy(fFirmwareVersion, iPos2 + 1, 2), 0); // $FF by default
    end else begin
      p^.MajorFirmwareVersion := 0;
      p^.MinorFirmwareVersion := 0;
    end;
    p^.DeviceServiceNumber := CalcCardinal(fDeviceServiceNumber);
    for i := 0 to Length(p^.Empty1) do p^.Empty1[i] := $FF;
    // 2
    p^.rBegin2.Id := p^.rBegin1.Id;
    p^.rBegin2.Count := p^.rBegin1.Count;
    p^.rBegin2.Index := 2;
    StrPLCopy(p^.FiscalPrinterNumber, ansistring(fFiscalPrinterNumber), SizeOf(p^.FiscalPrinterNumber) - 1, true, #0);
    for c := 'A' to 'G' do p^.TaxRates[c] := CalcWord(word(fTaxRates[c]));
    j := Pos('.', fFiscalPrinterFirmwareVersion);
    if (fFiscalPrinterFirmwareVersion <> '') and (j > 0) then begin
      p^.FiscalPrinterMajorFirmwareVersion := StrToIntDef(Copy(fFiscalPrinterFirmwareVersion, 1, j - 1), 0);
      p^.FiscalPrinterMinorFirmwareVersion := StrToIntDef(Copy(fFiscalPrinterFirmwareVersion, j + 1, 2), 0);
    end else begin
      p^.FiscalPrinterMajorFirmwareVersion := $FF;
      p^.FiscalPrinterMinorFirmwareVersion := $FF;
    end;
    for i := 0 to Length(p^.Empty2) do p^.Empty2[i] := $FF;
    // XOR
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    p^.XorSum2 := EmarXORSum(p^.rBegin2, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_42 }

procedure TEmar105_ReportEvent_42.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_42.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_42);
end;

procedure TEmar105_ReportEvent_42.GetFromData(aData: pointer);
var
  p: PEmar105_ReportEvent_42;
begin
  inherited;
  if fKind = 42 then
  begin
    p := pData;
    fDocumentNumber := CalcCardinal(p^.DocumentNumber);
    fTicketNumber := CalcWord(p^.TicketNumber);
    fNIP := CopyLStr(p^.NIP, SizeOf(p^.NIP) - 1);
    //
    FTicketNumberUsedHighPart := TEmar105_File(Owner)._GetTicketNumberUsedHighPart(fTicketNumber, False);
    TEmar105_File(Owner)._SetTicketBuyerNIP(IndexInReportsList);
  end
  else
  begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_42.SetToData(aData: pointer);
var
  p: PEmar105_ReportEvent_42;
  i: Integer;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then
  begin
    p := pData;
    p^.DocumentNumber := CalcCardinal(fDocumentNumber);
    p^.TicketNumber := CalcWord(fTicketNumber);
      // zakończony kodem #0. UWAGA: Jeśli wprowadzonych będzie mniej znaków NIP, niż 13, to pole do końca długości wypełniane jest kodami #0
    StrPLCopy(p^.NIP, AnsiString(fNIP), Length(Trim(fNIP)), True, #0);
    for i := 0 to Length(p^.Empty1) do p^.Empty1[i] := $FF;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEvent_43 }

procedure TEmar105_ReportEvent_43.AllocDataMem;
begin
  fDataRecCount := 1;
  GetMem(pData, GetDataLength);
end;

function TEmar105_ReportEvent_43.GetDataLength: integer;
begin
  Result := SizeOf(emar105.Struct.TEmar105_ReportEvent_43);
end;

procedure TEmar105_ReportEvent_43.GetFromData(aData: pointer);
var
  i: Byte;
  sHEXReversed: String;
  p: PEmar105_ReportEvent_43;
begin
  inherited;
  if fKind = 43 then
  begin
    p := pData;
    sHEXReversed := '';
    for i := High(p^.CardNumberZTM) downto Low(p^.CardNumberZTM) do
      sHEXReversed := sHEXReversed + IntToHex(p^.CardNumberZTM[i], 2);
    fCardNumberZTM := StrToInt64(HEXCodeToInt_DecodedFull(sHEXReversed));
    fTicketStatus := p^.TicketStatus;
    fServerStatus := p^.ServerStatus;
    fTicketValidTo := EmarDateToString(p^.TicketValidTo);
    fTicketZone := p^.TicketZone;
    fTicketName := CopyLStr(p^.TicketName, SizeOf(p^.TicketName));
    fBusStopStart := p^.BusStopStart;
    fBusStopEnd := p^.BusStopEnd;
  end
  else
  begin
    fErrorNo := errNoReportEventMishmash;
    AddError(reErrorByNumber);
  end;
end;

procedure TEmar105_ReportEvent_43.SetToData(aData: pointer);
var
  p: PEmar105_ReportEvent_43;
  i, j: Byte;
  sHEX: String;
begin
  inherited;
  if not IsError(reErrorNoMemoryAllocated) then
  begin
    p := pData;
    FillChar(p^.CardNumberZTM, SizeOf(p^.CardNumberZTM), 0);
    sHEX := IntToHex(fCardNumberZTM);
    i := Pred(Length(sHEX));
    j := 0;
    while (i > 0)and(j < SizeOf(p^.CardNumberZTM)) do
    begin
      p^.CardNumberZTM[j] := StrToInt('$' + Copy(sHEX, i, 2));
      Dec(i, 2);
      Inc(j);
    end;
    p^.TicketStatus := fTicketStatus;
    p^.ServerStatus := fServerStatus;
    DateToEmarDate(p^.TicketValidTo, fTicketValidTo);
    p^.TicketZone := fTicketZone;
    StrPLCopy(p^.TicketName, AnsiString(fTicketName), Length(Trim(fTicketName)), False, #0);
    p^.BusStopStart := fBusStopStart;
    p^.BusStopEnd := fBusStopEnd;
    for i := 0 to Length(p^.Empty1) do p^.Empty1[i] := $FF;
    p^.XorSum1 := EmarXORSum(p^.rBegin1, SizeOf(TEmar105_BaseReport_Rec) - 1);
    if Assigned(aData) then Move(pData^, aData^, GetDataLength);
  end;
end;

{ TEmar105_ReportEventList }

function TEmar105_ReportEventList.createItem(aKind: integer): IEmar_ReportEvent;
begin
  case aKind of
    0: Result := TEmar105_ReportEvent_00.Create(Owner, 101);
    1: Result := TEmar105_ReportEvent_01.Create(Owner, 101);
    2: Result := TEmar105_ReportEvent_02.Create(Owner, 101);
    3: Result := TEmar105_ReportEvent_03.Create(Owner, 101);
    4: Result := TEmar105_ReportEvent_04.Create(Owner, 101);
    5: Result := TEmar105_ReportEvent_05.Create(Owner, 101);
    6: Result := TEmar105_ReportEvent_06.Create(Owner, 101);
    7: Result := TEmar105_ReportEvent_07.Create(Owner, 101);
    8: Result := TEmar105_ReportEvent_08.Create(Owner, 101);
    9: Result := TEmar105_ReportEvent_09.Create(Owner, 101);
    10: Result := TEmar105_ReportEvent_10.Create(Owner, 101);
    11: Result := TEmar105_ReportEvent_11.Create(Owner, 101);
    12: Result := TEmar105_ReportEvent_12.Create(Owner, 101);
    13: Result := TEmar105_ReportEvent_13.Create(Owner, 101);
    14: Result := TEmar105_ReportEvent_14.Create(Owner, 101);
    15: Result := TEmar105_ReportEvent_15.Create(Owner, 101);
    16: Result := TEmar105_ReportEvent_16.Create(Owner, 101);
    17: Result := TEmar105_ReportEvent_17.Create(Owner, 101);
    18: Result := TEmar105_ReportEvent_18.Create(Owner, 101);
    19: Result := TEmar105_ReportEvent_19.Create(Owner, 101);
    20: Result := TEmar105_ReportEvent_20.Create(Owner, 101);
    21: Result := TEmar105_ReportEvent_21.Create(Owner, 101);
    22: Result := TEmar105_ReportEvent_22.Create(Owner, 101);
    23: Result := TEmar105_ReportEvent_23.Create(Owner, 101);
    24: Result := TEmar105_ReportEvent_24.Create(Owner, 101);
    25: Result := TEmar105_ReportEvent_25.Create(Owner, 101);
    26: Result := TEmar105_ReportEvent_26.Create(Owner, 101);
    27: Result := TEmar105_ReportEvent_27.Create(Owner, 101);
    28: Result := TEmar105_ReportEvent_28.Create(Owner, 101);
    29: Result := TEmar105_ReportEvent_29.Create(Owner, 101);
    30: Result := TEmar105_ReportEvent_30.Create(Owner, 101);
    31: Result := TEmar105_ReportEvent_31.Create(Owner, 101);
    32: Result := TEmar105_ReportEvent_32.Create(Owner, 101);
    33: Result := TEmar105_ReportEvent_33.Create(Owner, 101);
    34: Result := TEmar105_ReportEvent_34.Create(Owner, 101);
    35: Result := TEmar105_ReportEvent_35.Create(Owner, 101);
    36: Result := TEmar105_ReportEvent_36.Create(Owner, 101);
    37: Result := TEmar105_ReportEvent_37.Create(Owner, 101);
    38: Result := TEmar105_ReportEvent_38.Create(Owner, 101);
    // 39: Result := TEmar105_ReportEvent_39.Create(Owner, 101);
    40: Result := TEmar105_ReportEvent_40.Create(Owner, 101);
    41: Result := TEmar105_ReportEvent_41.Create(Owner, 101);
    42: Result := TEmar105_ReportEvent_42.Create(Owner, 101);
    43: Result := TEmar105_ReportEvent_43.Create(Owner, 101);
    255: Result := TEmar_ReportEvent_FF.Create(Owner, 101);
  else Result := nil;
  end;
  if Assigned(Result) then
    Result.Kind := aKind;
end;

function TEmar105_ReportEventList.LoadFromStream(aStream: TStream): cardinal;
var
  pRec, pFirstRec:                                    PEmar105_ReportEvent_Begin;
  lPage, i, j, iFF, iRecLength, iRecCount, iRecIndex: Integer;
  lPage528, lEventRecord:                             array of Byte;
  re:                                                 IEmar_ReportEvent;
  errEv:                                              IEmar_ReportEvent_FF;
begin
//  Result := ERR_INCORRECT_FILE;
  Clear;
  TEmar105_File(Owner).F_IsEmar205 := TEmar105_File(Owner).IsEmar205OnlineReport();
  TEmar105_File(Owner).F_Event01_TicketRegister := '';
  TEmar105_File(Owner).F_Event01_LastTicketNumberHighPart := $FF;
  TEmar105_File(Owner).F_Event01_LastTicketNumber := 0;
  pFirstRec := nil;
  lPage := Owner.Fat.IndexOfFirstPage(101);
  if lPage > 0 then begin
    i := Owner.Dir.IndexOf(101);
    if i < 0 then begin
      Result := ERR_REPORT_NO_DIR_RECORD;
      Exit;
    end;
    iRecLength := Owner.Dir[i].RecLength;
    // Maksymalnie 4 rekordy może mieć zdarzenie raportu
    SetLength(lEventRecord, iRecLength * 4);
    SetLength(lPage528, 528);
    FillChar(lEventRecord[0], Length(lEventRecord), $FF);
    iRecCount := 0;
    iRecIndex := 0;
    while lPage > 0 do
    try
      aStream.Seek(lPage * 528, soFromBeginning);
      if aStream.read(lPage528[0], 528) = 528 then begin
        i := 0;
        while (i < 512) do begin
          if (i + iRecLength) <= 512 then begin
            pRec := @lPage528[i];
            if
              (
                (pRec^.ID = $65) // strona ze zdarzeniami raportu
                and(pRec^.Count = $FF)and(pRec^.Index = $FF)
                or
                (pRec^.ID in [$00, $FF]) // śmieciowe rekordy
                and(pRec^.Count in [$00, $FF])and(pRec^.Index in [$00, $FF])
              )
              and (iRecIndex > - 1)
            then
            begin
              // pusty rekord - czasami bileterka mimo że jest jeszcze
              // miejsce na tej stronie, pomija ją i zapisuję na następną stronę
              // albo zapisuje stronę z 65 na początku a resztą - FF
              Inc(i, iRecLength);
              Continue;
            end;

            if (pRec^.ID <> $65) or (pRec^.Count = 0) or (pRec^.Count > 4) or (pRec^.Index = 0) or (pRec^.Index > 4) or
              ((pRec^.Index = 1) and (pRec^.EventID > EMAR105_MaxReportEventID)) or (pRec^.Count >= pRec^.Index) and
              (pRec^.Index > 1) and (pRec^.Index <= 4) and (lEventRecord[0] = $FF) // nie zapisano pierwszego rekordu
            then begin
              if (pRec^.Count <> 1) and (pRec^.Index = 1) and (pRec^.EventID <= EMAR105_MaxReportEventID) and
                not (pRec^.EventID in [1, 5, 12, 14, 17, 32, 34, 35, 39, 41]) then
              // pierwszy rekord ale nie wiadomo ile jest rekordów
              begin
                pRec^.Count := 1;
                lPage528[i + iRecLength - 1] := EmarXORSum(pRec^, iRecLength - 1);
                Dec(i, iRecLength);
                Dec(iRecIndex);
              end else begin
                errEv := addItem($FF) as IEmar_ReportEvent_FF;
                for j := 0 to iRecLength - 1 do errEv.Bytes[j] := lPage528[i + j];
              end;
            end else if (pRec^.ID = $65) and
              ((pRec^.Index in [2, 3, 4]) or ((pRec^.Index = 1) and not (pRec^.EventID > EMAR105_MaxReportEventID)))
            then begin
              if (not (Assigned(pFirstRec)) or (pFirstRec^.ID <> $65)) and (pRec^.Count = 1) and (pRec^.Index = 1) then
              begin
                TEmar_ReportEvent(addItem(pRec^.EventID)).GetFromData(pRec);
                if iRecCount > 0 then begin
                  FillChar(lEventRecord[0], Length(lEventRecord), $FF);
                  iRecCount := 0;
                end;
                if (pRec^.ID = $65)and(pRec^.Count = 1)and(pRec^.Index = 1) then
                  pFirstRec := nil; // zostaje wyczyszczony, gdy jedynie 1 rekord w zdarzeniu
              end else begin
                if pRec^.Index in [1 .. 4] then begin
                  pFirstRec := @lEventRecord[0];
                  if (pFirstRec^.ID <> $FF) and (iRecCount >= pRec^.Index)
                  // probujemy odczytać numer rekordu, którym już jest wypełniana tabela lEventRecord
                  then begin
                    // // nie ignorujemy rekord, gdy poprzednio mamy błędną identyfikację bileterki przed prawidłową identyfikacją
                    // if (pRec^.Index = 1)and not((pFirstRec^.EventID = 1)and(pRec^.EventID = 1)) then
                    // begin
                    // pFirstRec := @lEventRecord[0];
                    // TEmar_ReportEvent(addItem(pFirstRec^.EventID)).GetFromData(pFirstRec); // niepełny nie zapisany rekord
                    // end;
                    // // wypełniamy rekordy FFami
                    // FillChar(lEventRecord[0], Length(lEventRecord), $FF);
                    // iRecCount := 0;

                    // jeżeli pierwszy rekord zdarzenia #1, #5, #32 lub #34 jest w miare w porządku, zostawiamy
                    if (pFirstRec^.ID = $65)
                      and(
                        (pFirstRec^.Count = 4)and(pFirstRec^.Index = 1)and(pFirstRec^.EventID in [1, 5])
                        or
                        (pFirstRec^.Count = 3)and(pFirstRec^.Index = 1)and(pFirstRec^.EventID in [32, 34])
                         )
                      and(EmarXORSum(pFirstRec^, iRecLength - 1) = lEventRecord[iRecLength - 1]) // XOR
                    then begin
                      re := addItem(pFirstRec^.EventID) as IEmar_ReportEvent;
                      TEmar_ReportEvent(re).GetFromData(pFirstRec);
                      for iFF := 1 to 4 do re.FFRecordsID[iFF] := lEventRecord[(iFF - 1) * iRecLength] = $FF;
                      // TEmar_ReportEvent(addItem(pFirstRec^.EventID)).GetFromData(pFirstRec);
                    end else begin
                      errEv := addItem($FF) as IEmar_ReportEvent_FF;
                      for j := 0 to iRecLength - 1 do errEv.Bytes[j] := lEventRecord[j];

                      if lEventRecord[iRecLength] <> $FF then begin
                        errEv := addItem($FF) as IEmar_ReportEvent_FF;
                        for j := 0 to iRecLength - 1 do errEv.Bytes[j] := lEventRecord[iRecLength + j];
                      end;

                      if lEventRecord[2 * iRecLength] <> $FF then begin
                        errEv := addItem($FF) as IEmar_ReportEvent_FF;
                        for j := 0 to iRecLength - 1 do errEv.Bytes[j] := lEventRecord[2 * iRecLength + j];
                      end;

                      if lEventRecord[3 * iRecLength] <> $FF then begin
                        errEv := addItem($FF) as IEmar_ReportEvent_FF;
                        for j := 0 to iRecLength - 1 do errEv.Bytes[j] := lEventRecord[3 * iRecLength + j];
                      end;
                    end;

                    FillChar(lEventRecord[0], Length(lEventRecord), $FF);
                    iRecCount := 0;
                  end;

                  Inc(iRecCount);
                  Move(lPage528[i], lEventRecord[iRecLength * (pRec^.Index - 1)], iRecLength);
                  pFirstRec := @lEventRecord[0];
                  if iRecCount > 0 then begin
                    if (pFirstRec^.Count in [1 .. 4]) and (pFirstRec^.Index = 1) and (pFirstRec^.Count = pRec^.Index)
                    then begin
                      TEmar_ReportEvent(addItem(pFirstRec^.EventID)).GetFromData(pFirstRec);
                      FillChar(lEventRecord[0], Length(lEventRecord), $FF);
                      iRecCount := 0;
                    end else if pRec^.Index = 4 then begin
                      FillChar(lEventRecord[0], Length(lEventRecord), $FF);
                      iRecCount := 0;
                    end;
                  end;
                end;
              end;
            end;
            // if (((lPage528[i] = 101) and (lPage528[i + 2] = 1)) or (lPage528[i] <> 101)) and (lEventRecord[3] <> $FF) then begin
            // TEmar_ReportEvent(addItem(lEventRecord[3])).GetFromData(@lEventRecord[0]);
            // FillChar(lEventRecord[0], Length(lEventRecord), $FF);
            // if lPage528[i] = $FF then
            // Break;
            // end;
            // if (lPage528[i] = 101) then
            // Move(lPage528[i], lEventRecord[iRecLength * (lPage528[i + 2] - 1)], iRecLength);
            Inc(i, iRecLength);
            Inc(iRecIndex);
          end
          else // when report's records are separated by 2 different pages, so the next part is not in the read stream part (so 'if lPage528[i]=101 then' condition does not hire)
              Break; // to read the next page
        end;
      end else begin
        Result := ERR_USB_DEVICE_READ;
        Exit;
      end;
      lPage := Owner.Fat.NextPage(101, lPage);
    except
      raise;
    end;
    if iRecCount > 0 then begin
      pFirstRec := @lEventRecord[0];
      if (pFirstRec^.Count in [1 .. 4]) and (pFirstRec^.Index = 1) then
          TEmar_ReportEvent(addItem(pFirstRec^.EventID)).GetFromData(pFirstRec);
    end;
    // if lEventRecord[3] <> $FF then
    // TEmar_ReportEvent(addItem(lEventRecord[3])).GetFromData(@lEventRecord[0]);

    Result := ERR_NO_ERROR;
  end
  else Result := ERR_REPORT_NO_REPORT;
end;

function TEmar105_ReportEventList.SaveToStream(aStream: TStream; aAtPage: integer): cardinal;
var
  i, j, k, ix, cp, rc: integer;
  lPage528:            array of byte;
  pPage528:            PEmarPage528;
  lEventRecord:        array of byte;
  de:                  IEmar_DirEntry;
begin
  if Count > 0 then begin
    try
      cp := Owner.Fat.IndexOfFirstPage($FF, aAtPage);
      if cp < 0 then begin
        Result := ERR_USB_DEVICE_PAGE_RANGE;
        Exit;
      end;
      if (aAtPage > 1) and (cp < aAtPage) then cp := aAtPage;
      SetLength(lPage528, FLASH_528);
      FillChar(lPage528[0], FLASH_528, $FF);
      SetLength(lEventRecord, 39 * 4);
      pPage528 := @lPage528[0];
      ix := Owner.Dir.IndexOf(101);
      if ix < 0 then de := Owner.Dir.addItem(101)
      else de := Owner.Dir[ix];
      de.FirstPage := cp;
      de.RecLength := 39;
      ix := 0;
      rc := 0;
      for i := 0 to Count - 1 do begin
        k := TEmar_ReportEvent(Items[i]).ReportRecordCount;
        Inc(rc, k);
        if TEmar_ReportEvent(Items[i]).Kind = $FF then begin // zapisujemy błędny rekord FF długości 39 byte
          for j := 0 to 38 do lEventRecord[j] := TEmar_ReportEvent_FF(Items[i]).Bytes[j];
        end
        else TEmar_ReportEvent(Items[i]).SetToData(@lEventRecord[0]);
        j := 0;
        while j < k do begin
          if ix + 39 > 512 then begin
            if cp = de.FirstPage then FillPageCtrlBytes(pPage528^, 101, cp, $FFFF, cp + 1)
            else FillPageCtrlBytes(pPage528^, 101, cp, cp - 1, cp + 1);
            aStream.Seek(cp * FLASH_528, soFromBeginning);
            aStream.write(pPage528^, FLASH_528);
            FillChar(lPage528[0], FLASH_528, $FF);
            Owner.Fat.PageId[cp] := 101;
            Inc(cp);
            ix := 0;
          end;
          Move(lEventRecord[j * 39], lPage528[ix], 39);
          Inc(j);
          Inc(ix, 39);
        end;
      end;
      // zadanie 62561
      if cp = de.FirstPage then FillPageCtrlBytes(pPage528^, 101, cp, $FFFF, $FFFF)
      else FillPageCtrlBytes(pPage528^, 101, cp, cp - 1, $FFFF);
      aStream.Seek(cp * FLASH_528, soFromBeginning);
      aStream.write(pPage528^, FLASH_528);
      Owner.Fat.PageId[cp] := 101;
      de.RecCount := rc;
      Result := ERR_NO_ERROR;
    except
      Result := ERR_UNEXPECTED_ERROR;
    end;
  end
  else Result := ERR_NO_ERROR;
end;

{ TEmar105_StartedRideList }

function TEmar105_StartedRideList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_StartedRide.Create(Owner, Id);
end;

{ TEmar105_StartedRide }

procedure TEmar105_StartedRide.LoadFromBuffer(aStream: TStream; aVer: byte);
begin
  aStream.read(fData.aContent, RecordLength);
end;

function TEmar105_StartedRide.RecordLength(aVer: byte): integer;
begin
  Result := 512;
end;

procedure TEmar105_StartedRide.SaveToBuffer(aStream: TStream; aVer: byte);
begin
  aStream.write(fData, RecordLength)
end;

function TEmar105_LineRouteList._New: IEmar_LineRouteList;
begin
  Result := TEmar105_LineRouteList.Create(Owner, Id);
end;

function TEmar105_RideTariffList._New: IEmar_RideTariffList;
begin
  Result := TEmar105_RideTariffList.Create(Owner, Id) as IEmar_RideTariffList;
end;

function TEmar105_RideBonusList._New: IEmar_RideBonusList;
begin
  Result := TEmar105_RideBonusList.Create(Owner, Id) as IEmar_RideBonusList;
end;

function TEmar105_RideHandlingFeeList._New: IEmar_RideHandlingFeeList;
begin
  Result := TEmar105_RideHandlingFeeList.Create(Owner, Id) as IEmar_RideHandlingFeeList;
end;

function TEmar105_LuggageTariffList._New: IEmar_LuggageTariffList;
begin
  Result := TEmar105_LuggageTariffList.Create(Owner, Id) as IEmar_LuggageTariffList;
end;

function TEmar105_RidesCityTariffList._New: IEmar_RidesCityTariffList;
begin
  Result := TEmar105_RidesCityTariffList.Create(Owner, Id) as IEmar_RidesCityTariffList;
end;

function TEmar105_RideReductionList._New: IEmar_RideReductionList;
begin
  Result := TEmar105_RideReductionList.Create(Owner, Id) as IEmar_RideReductionList;
end;

{ TEmar105_BusStopStand }

procedure TEmar105_BusStopStand.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r: TEmar105_BusStopStand_v0;
begin
  aStream.read(r.ID, RecordLength(aVer));
  IndexOfBusStop := CalcWord(r.IndexOfBusStop) - 1;
  StandName := CopyPStr(r.StandName, SizeOf(r.StandName) - 1);
  Latitude := SmallInt(CalcWord(word(r.Latitude_Int))) + CalcCardinal(r.Latitude_Frac) / 1000000000;
  Longitude := SmallInt(CalcWord(word(r.Longitude_Int))) + CalcCardinal(r.Longitude_Frac) / 1000000000;
end;

function TEmar105_BusStopStand.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar105_BusStopStand_v0);
end;

procedure TEmar105_BusStopStand.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r: TEmar105_BusStopStand_v0;
begin
  r.ID := Id;
  r.ID_9 := 9;
  r.IndexOfBusStop := CalcWord(word(IndexOfBusStop + 1));
  StrPLCopy(r.StandName, ansistring(StandName), SizeOf(r.StandName) - 1, true, ' ');
  if Trunc(Longitude) = -1 then // deny saving $FF
    r.Longitude_Int := 0
  else
    r.Longitude_Int := SmallInt(CalcWord(Trunc(Longitude)));
  r.Longitude_Frac := CalcCardinal(Trunc(Frac(Longitude) * 1000000000));
  if Trunc(Latitude) = -1 then // deny saving $FF
    r.Latitude_Int := 0
  else
    r.Latitude_Int := SmallInt(CalcWord(Trunc(Latitude)));
  r.Latitude_Frac := CalcCardinal(Trunc(Frac(Latitude) * 1000000000));
  aStream.write(r, RecordLength(aVer));
end;

{ TEmar105_BusStopStandList }

function TEmar105_BusStopStandList._AddItem: IEmar_Interface;
begin
  Result := TEmar105_BusStopStand.Create(Owner, Id);
end;

{ TEmar205_Texts }

procedure TEmar205_Texts.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  p:    PEmar205_Texts_v0;
  page: array of byte;
begin
  SetLength(page, 512);
  FillChar(page[0], 512, $FF);
  aStream.Read(page[0], 512);
  p := @page[0];
  Headers[0] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Headers[0, 0], __MAX_TEXT_LEN)));
  Headers[1] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Headers[1, 0], __MAX_TEXT_LEN)));
  Headers[2] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Headers[2, 0], __MAX_TEXT_LEN)));
  Headers[3] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Headers[3, 0], __MAX_TEXT_LEN)));
  Headers[4] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Headers[4, 0], __MAX_TEXT_LEN)));
  Footers[0] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Footers[0, 0], __MAX_TEXT_LEN)));
  Footers[1] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Footers[1, 0], __MAX_TEXT_LEN)));
  Footers[2] := pchar(ControlSymbolsToClass(CopyLStr(@p^.Footers[2, 0], __MAX_TEXT_LEN)));
end;

function TEmar205_Texts.RecordLength(aVer: byte): integer;
begin
  Result := 255; // pełna strona - 512 bajtów
end;

procedure TEmar205_Texts.SaveToBuffer(aStream: TStream; aVer: byte);
var
  p:    PEmar205_Texts_v0;
  page: array of byte;
begin
  SetLength(page, 512);
  FillChar(page[0], 512, $FF);
  p := @page[0];
  p^.ID := Id;
  StrPLCopy(p^.Headers[0], ControlSymbolsToOIK(Headers[0], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, #0);
  StrPLCopy(p^.Headers[1], ControlSymbolsToOIK(Headers[1], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, #0);
  StrPLCopy(p^.Headers[2], ControlSymbolsToOIK(Headers[2], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, #0);
  StrPLCopy(p^.Headers[3], ControlSymbolsToOIK(Headers[3], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, #0);
  StrPLCopy(p^.Headers[4], ControlSymbolsToOIK(Headers[4], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, #0);

  p^.XorHeaders := EmarXORSum(p^.Headers[0], 5 * (__MAX_TEXT_LEN + 1));

  StrPLCopy(p^.Footers[0], ControlSymbolsToOIK(Footers[0], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, ' ');
  StrPLCopy(p^.Footers[1], ControlSymbolsToOIK(Footers[1], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, ' ');
  StrPLCopy(p^.Footers[2], ControlSymbolsToOIK(Footers[2], __MAX_TEXT_LEN), __MAX_TEXT_LEN, true, ' ');

  p^.XorFooters := EmarXORSum(p^.Footers[0], 3 * (__MAX_TEXT_LEN + 1));
  aStream.Write(page[0], 512);
end;

{ TEmar205_TextsList }

function TEmar205_TextsList._AddItem: IEmar_Interface;
begin
  Result := TEmar205_Texts.Create(Owner, Id);
end;

{ TEmar205_Wifi }

function TEmar205_Wifi.IPtoString(p: PByte): string;
begin
  if (p[0] + p[1] + p[2] + p[3] <> 0) then Result := Format('%d.%d.%d.%d', [p[0], p[1], p[2], p[3]])
  else Result := '';
end;

procedure TEmar205_Wifi.LoadFromBuffer(aStream: TStream; aVer: byte);
var
  r:     TEmar205_WiFi_v0;
  _pass: ansistring;
begin
  aStream.Read(r, RecordLength(aVer));
  SSID := CopyPStr(r.SSID, SizeOf(r.SSID) - 1);
  SetLength(_pass, 64);
  Move(r.Password[0], _pass[1], 64);
  Password := pchar(string(_pass));
  UseStaticAddress := r.UseStaticAddress = 1;
  IPAddress := pchar(IPtoString(@r.IP[0]));
  IPMask := pchar(IPtoString(@r.Mask[0]));
  Gateway := pchar(IPtoString(@r.Gateway[0]));
  UseOwnDNS := r.UseOwnDNS = 1;
  PrimaryDNS := pchar(IPtoString(@r.PrimaryDNS[0]));
  SecondaryDNS := pchar(IPtoString(@r.SecondaryDNS[0]));
end;

function TEmar205_Wifi.RecordLength(aVer: byte): integer;
begin
  Result := SizeOf(TEmar205_WiFi_v0);
end;

procedure TEmar205_Wifi.SaveToBuffer(aStream: TStream; aVer: byte);
var
  r:     TEmar205_WiFi_v0;
  _pass: string;
begin
  r.ID := Id;
  StrPLCopy(r.SSID, ansistring(SSID), SizeOf(r.SSID) - 1, true, #0);
  SetLength(_pass, 64);
  Move(Password^, _pass[1], 64 * SizeOf(char));
  StrPLCopy(r.Password, ansistring(_pass), SizeOf(r.Password), false, #0); // blowfish
  if UseStaticAddress then begin
    r.UseStaticAddress := 1;
    StringToIP(@r.IP[0], IPAddress);
    StringToIP(@r.Mask[0], IPMask);
    StringToIP(@r.Gateway[0], Gateway);
  end else begin
    r.UseStaticAddress := 0;
    StringToIP(@r.IP[0], '0.0.0.0');
    StringToIP(@r.Mask[0], '0.0.0.0');
    StringToIP(@r.Gateway[0], '0.0.0.0');
  end;
  if UseOwnDNS then begin
    r.UseOwnDNS := 1;
    StringToIP(@r.PrimaryDNS[0], PrimaryDNS);
    StringToIP(@r.SecondaryDNS[0], SecondaryDNS);
  end else begin
    r.UseOwnDNS := 0;
    StringToIP(@r.PrimaryDNS[0], '0.0.0.0');
    StringToIP(@r.SecondaryDNS[0], '0.0.0.0');
  end;
  aStream.Write(r, RecordLength(aVer));
end;

procedure TEmar205_Wifi.StringToIP(p: PByte; IP: string);
var
  d1, d2, d3, d4, ps: integer;
begin
  d1 := 0;
  d2 := 0;
  d3 := 0;
  d4 := 0;
  ps := Pos('.', IP);
  if ps > 0 then begin
    d1 := StrToIntDef(Copy(IP, 1, ps - 1), 0);
    Delete(IP, 1, ps);
  end;
  ps := Pos('.', IP);
  if ps > 0 then begin
    d2 := StrToIntDef(Copy(IP, 1, ps - 1), 0);
    Delete(IP, 1, ps);
  end;
  ps := Pos('.', IP);
  if ps > 0 then begin
    d3 := StrToIntDef(Copy(IP, 1, ps - 1), 0);
    Delete(IP, 1, ps);
  end;
  if IP <> '' then d4 := StrToIntDef(IP, 0);
  p^ := byte(d1);
  Inc(p);
  p^ := byte(d2);
  Inc(p);
  p^ := byte(d3);
  Inc(p);
  p^ := byte(d4);
end;

{ TEmar205_WiFiList }

function TEmar205_WiFiList._AddItem: IEmar_Interface;
begin
  Result := TEmar205_Wifi.Create(Owner, Id);
end;

end.
