unit ResourceStrings;

interface

const
{$REGION '  UWAGA! Nie przenosić tej sekcji do resourcestring, ponieważ muszą być NIE przetłumaczone'}
  _CAPT_SETTINGS_BASIC = 'Podstawowe';
  _CAPT_SETTINGS_Import = 'Import';
  _CAPT_TERRITORIAL = 'Podział terytorialny';
  _CAPT_ORG_DEV = 'Firmy i urzędy';
  _CAPT_CAL_DEV = 'Kalendarz i oznaczenia';
  _CAPT_ROAD_DEV = 'Elementy tras';
  _CAPT_ROUTE_PARAMS = 'Parametry';
  _CAPT_ROUTE_TIMETABLE = 'Rozkłady jazdy';
  _CAPT_ROUTE = 'Trasy';
  _CAPT_ROUTE_TARIF = 'Przypisanie taryf';
  _CAPT_BusStopManager_DEV = 'Zarządzanie przystankami';
  _CAPT_ROUTE_PRINT_TIMETABLE = 'Wydruki RJA';
  _CAPT_PRICESCALE_DEV = 'Cenniki';
  _CAPT_TARIF_DEV = 'Taryfy';
  _CAPT_REDUCTIONS_DEV = 'Ulgi';
//  _CAPT_TICKETONEAMOUNTREDUCTION_DEV = 'Ulgi kwotowe';
//  _CAPT_BASICPRICESCALE_DEV = 'Wzory biletów miejskich';
  _CAPT_TICKETZONE_DEV = 'Strefy biletowe';
  _CAPT_REDUCTION_NUMBERING_DEV = 'Kolejność ulg';
  _CAPT_REDUCTION_PRICE_DEV = 'Przypisanie taryf i ulg';
  _CAPT_Cashiers_DEV = 'Kasjerzy (Dworzec)';
  _CAPT_Drivers_DEV = 'Kierowcy';
  _CAPT_GroupDrivers_DEV = 'Grupy kierowców i kasjerów';
  _CAPT_BUSSES_DEV = 'Pojazdy';
  _CAPT_BUSVEHICAL_DEV = 'Autobusy i pojazdy';
  _CAPT_BUSVEHICAL_PARUS = 'Autobusy';
  _CAPT_BUSGROUPS_DEV = 'Marki i modele';
  _CAPT_BUSGROUPS_PARUS = 'Grupy autobusów';
  _CAPT_CEDULY = 'Ceduły';
  _CAPT_CEDULY_TICKETS = 'Bilety';
  _CAPT_SALEDEVICES_DEV = 'Urządzenia';
  _CAPT_ZbioryDanych_DEV = 'Zbiory danych';
  _CAPT_TRP_DEV = 'Programowanie bileterek';
  _CAPT_REPORTS_DEV = 'Zestawienia i raporty';
  _CAPT_DATA_TICKETREGISTER = 'Dane dla bileterki';
  _CAPT_Passengers_DEV= 'Pasażerowie';
  _CAPT_Date_DEV= 'Dane';
  _CAPT_SaleReports_DEV= 'Raporty sprzedażowe';
  _CAPT_SaleRegister_DEV= 'Rejestracja rozliczeń';
  _CAPT_SaleAnalysis_DEV= 'Analizy sprzedaży';
  _CAPT_TransportAnalysis_DEV= 'Analizy przewozów';
  _CAPT_TimelinessAnalysis_DEV= 'Analizy punktualności';
  _CAPT_IncInspection_DEV= 'Nadzór ruchu';
  _CAPT_RoudInspection_DEV= 'Przebiegi jazd';
  _CAPT_PersonGroupType_DEV = 'Typy grup mieszkańców';
  _CAPT_PersonGroup_DEV = 'Grupy mieszkańców';
  _CAPT_PersonGroup_MEMBERS = 'Lista mieszkańców przypisanych do grupy';
  _CAPT_TICKETS_CANCELLATION = 'Bilet do anulowania';
  _CAPT_SALE = 'Sprzedaż';
  _CAPT_COORDINATION_BUSSTOP_PLATES = 'Tabliczki przystankowe';
  _CAPT_COORDINATION_RJA_TABLE = 'Tabele RJA';
  _CAPT_COORDINATION_INFO_DATA = 'Eksporty danych';
  _CAPT_COORDINATION_TIME_TABLE = 'Rozkłady jazdy';
  _CAPT_COORDINATION_EPodroznik = 'e-podróżnik';
  _CAPT_Task = 'Zadania';
  _CAPT_REPORTS = 'Raporty';
  _CAPT_REGISTERS = 'Rejestry';

   //////////////////////////// Karta Miejska ///////////////////////////////////
  _CAPT_CITYCARD_MIESZKANCY = 'Karty i mieszkańcy';
  _CAPT_CITYCARD_URZADZENIA = 'Urządzenia weryfikujące';
  _CAPT_CITYCARD_RAPORTY = 'Raporty';
  _CAPT_CITYCARD_SETTINGS = 'Podstawowe';
  _CAPT_CITYCARD_LOJALNOSCIOWY = 'Program lojalnościowy';
{$ENDREGION}

resourcestring
  RS_YES = 'Tak';
  RS_NO = 'Nie';
  RS_FREE = 'wolny';
  RS_OK = 'OK';
  RS_CANCEL = 'Anuluj';
  RS_SELECT = 'Wybierz';
  RS_FROM = 'z';
  RS_TO = 'do';
  RS_ADD = 'dodaj';
  
  RS_RECORD_INSERTED = 'Dodano nowy rekord!';
  RS_RECORD_EDITED = 'Zaktualizowano rekord!';
  RS_RECORD_NOT_DELETED = 'Rekord nie może zostać usunięty!';

  RS_DRIVER_CHOICE = 'Wybierz kierowcę';
  RS_DRIVER = 'Kierowcy';
  RS_DRIVERREMOVE = 'Usunąć przypisanie kierowcy?';
  RS_COMPANYREMOVE = 'Usunąć przypisanie firmy?';
  RS_DRIVER_DRIVERSBALANCES = 'Salda kierowców i kasjerów na koniec dnia';

  RS_IDENTICAL_FILES = 'Pliki są identyczne';
  RS_FMT_FILES = 'pliki (*.%s)|*.%s';
  RS_FMT_PA_FILES = 'pliki ze zmianami cen biletów EM-Kartowych z Dworca (PA*.DAT)|PA*.DAT';

  INFORMICA_PHONE = '534-181-823';
  INFORMICA_EMAIL = 'informica@informica.pl';

  MAIN_MISS_CONFIG =
    'Brak pliku konfiguracyjnego lub wykryto błędne dane zapisane w pliku konfiguracyjnym!';

  RS_LICENCES = 'Licencje';
  RS_LPC_PARAMETERS = 'Parametry';
  RS_PLANParameters = 'Planowanie - parametry';
  RS_TicketRegisterSettigns = 'Kasa fiskalna - parametry połączenia';

  _LOGGED_USER = 'Użytkownik: %s';
  _ASK_USER_PASSWORD = 'PODAJ NAZWĘ UŻYTKOWNIKA I HASŁO!';
  _VERSION = 'wersja';
  RS_LIC_ERR = 'Bład licencji programu!';
  RS_LIC_ERR_READ = 'Bład odczytu licencji programu!';
  RS_LIC_ENDDATEWARNING = 'Za %d dzień/dni skończy się ważność licencji';
  RS_LIC_NOENDDATE1 = 'BEZTERMINOWA';
  RS_LIC_NOENDDATE2 = 'BEZTERMINOWO';
  RS_LIC_UNAVAIBLE = 'NIEDOSTĘPNY';
  RS_LIC_MAXVALUEREACHED = 'Osiągnięto maksimum';
  RS_LIC_OVERMAXVALUE = 'Przekroczono';
  RS_LIC_ENDDATEPASSED = 'TERMIN MINĄŁ';
  RS_DATEFORMAT = 'yyyy-MM-dd';
  RS_DAY = 'Dzień';
  RS_MONTH = 'Miesiąc';
  RS_YEAR = 'Rok';
  RS_UNDEFINED = 'nie określono';
  RS_BRAK = 'brak';
  RS_BRAK_POWIAZANIA = 'brak powiązania';
  RS_NOT_SCRAPPED = 'niezezłomowany';

  rsFunctionalityDisabled = 'Funkcja niedostępna.';
  rsFunctionalityNameDisabled = 'Funkcja "%s" niedostępna.';
  rsUserPrivilagesToLow = 'Brak uprawnień do uruchomienia opcji!';
  rsFunctionlityNotDefined = 'Funkcja nie została zdefiniowana!';

  RF_FMT_FOLDER_IS_NOT_WRITABLE = 'Brak możliwości zapisu plików do "%s".';
  RF_FMT_NO_MORE_FREE_SPACE = 'Brak miejsca na dysku %s:\';
  RF_FMT_FILE_IS_EMPTY = 'Plik "%s" jest pusty.';

  ITEM_CHOICE = '_wybierz';
  ITEM_ALL = '_wszystkie';
  DEL_REC = 'Usunąć wpis?';
  DEL_NO_SELECTED_POSITION = 'Wskaż pozycję na liście !';

  COPY_REC = 'Skopiować pozycję?';
  DEL_SELECTEDRECS = 'Usunąć zaznaczone wpisy?';
  DEL_ALLRECS = 'Usunąć wszystkie wpisy?';

  CAP_SAVE_ON_LOCAL_DRIVE = 'Zapisz na dysku lokalnym';
  CAP_SAVE_TO_ROZLICZARKA_WPLATOMAT_FOLDERS = 'Zapisz do folderów rozliczarek/wpłatomatów';
  CAP_SAVE_TO_DWORZECSQL_FOLDER = 'Zapisz do folderu zapisu danych do Dworca (param.rej.)';
  CAP_SEND_A8x_EXPORT_FILE = 'Wyślij zbiór on-line do bileterek EMAR-205';
  CAP_SAVE_A8x_EXPORT_FILE = 'Zapisz zbiór on-line na dysku lokalnym';

  RS_INF_SaveOk_Rozliczarek_Wplatomat = 'Plik został zapisany do wszystkich stanowisk rozliczarek / wpłatomatów.';
  RS_WAR_No_Rozliczarek_Wplatomat = 'Brak wpisanych folderów zapisu pliku do rozliczarek / wpłatomatów w parametrach rejestracji raportów.';

  RS_INF_SaveOk_DworzecSQL = 'Plik został zapisany do folderu zapisu danych do Dworca (param.rej.)';
  RS_WAR_No_DworzecSQL = 'Brak wpisanego folderu zapisu danych do Dworca (param.rej.)';

  RS_INF_SaveOk_Rozliczarek_Wplatomat_Export = 'Plik został zapisany do wszystkich folderów eksportu danych rozliczarek / wpłatomatów.';
  RS_WAR_No_Rozliczarek_Wplatomat_Export = 'W parametrach rejestracji nie został zdefiniowany żaden folder eksportu danych do rozliczarek / wpłatomatów!';
  RS_ERR_Rozliczarek_Wplatomat_Export = 'Plik nie został zapisany do zdefiniowanych folderów eksportu danych rozliczarek / wpłatomatów.';

  RS_INF_SaveOk_BA_NA_Export = 'Plik został zapisany do folderu eksportu danych biletów EM-Kartowych sprzedanych na następny okres w autobusie, do przesłania do dworca (pliki BA oraz NA).';
  RS_INF_SaveOk_BA_NA_ExportFew = 'Pliki zostały zapisane do folderu eksportu danych biletów EM-Kartowych sprzedanych na następny okres w autobusie, do przesłania do dworca (pliki BA oraz NA).';
  RS_WAR_No_BA_NA_Export = 'W parametrach rejestracji nie został zdefiniowany folder eksportu danych biletów EM-Kartowych sprzedanych na następny okres w autobusie, do przesłania do dworca (pliki BA oraz NA)!';
  RS_WAR_Nothing_To_Export = 'Brak danych do wyeksportowania!';
  RS_ERR_BA_NA_Export = 'Plik nie został zapisany do zdefiniowanego folderu eksportu danych biletów EM-Kartowych sprzedanych na następny okres w autobusie, do przesłania do dworca (pliki BA oraz NA).';

  RS_ERR_A80A6DFileOnly = 'Tylko pliki do bileterki Emar-105/205 można zapisać do stanowisk rozliczarek / wpłatomatów oraz plik do sprzedaży (A6D) można zapisać do folderu zapisu danych do Dworca (param.rej.)';
  RS_ERR_A80File_Save_To_Rozliczarek_Wplatomat = 'Plik nie został zapisany do wszystkich stanowisk rozliczarek / wpłatomatów.';
  RS_ERR_A6DFile_Save_To_DworzecSQL = 'Plik nie został zapisany do folderu zapisu danych do Dworca (param.rej.).';
  RS_WAR_A80ExportFileEmarOnly = 'Tylko na podstawie pliku do bileterki Emar-105/205 można wygenerować zbiór do wysyłania';
  RS_WAR_A80ExportFileMainCompanyOnly = 'Tylko na podstawie pliku do bileterki Emar-105/205 firmy głównej można wygenerować zbiór do wysyłania';
  RS_WAR_A80ExportFileWasNotGeneratedYet = 'Zbiór on-line nie został jeszcze przygotowany.'#13#10'Zbiór można będzie zapisać po jego przygotowaniu.';
  RS_WAR_A80ExportFileWasNotGenerated = 'Zbiór on-line nie został przygotowany.'#13#10'Na dysk lokalny można zapisać tylko zbiory on-line, które były przygotowane i wysłane na serwer.';
  RS_INF_A80ExportFileConfirmation_PART1 = 'Aktualny zbiór on-line to: %s. W parametrach rejestracji zbiór wysyłania on-line to: %s. Nowe zbiory wysyłane są na serwer automatycznie, jeśli ustawione jest wysyłanie ostatnio przygotowanego zbioru.';
  RS_INF_A80ExportFileConfirmation_PART2 = 'Wysłanie spowoduje ustawienie wybranego zbioru %s jako zbioru wysyłania w parametrach. Czy na pewno chcesz zamienić zbiór na serwerze i w parametrach?';
  RS_ERR_LoadAttachmentFromServer = 'Błąd odczytu pliku z bazy.';
  RS_ERR_FMT_LoadAttachmentFromServer = 'Błąd odczytu pliku %s z bazy.';
  RS_ERR_IsNotValidClass =
    'BŁĄD: $s - klasa w parametrze AOwner nie jest typu %s';
  RS_ERR_FieldNotNull = 'Pole "%s" nie może być puste.';
  RS_Err_LogIndexOutOfRangeWithMax = 'indeks poza zakresem %d (< %d)!';
  RS_Err_IndexOutOfRangeWithMax = '%s.%s: indeks poza zakresem %d (< %d)!';
  RS_Err_LogUnknownClassTObjecList = 'nieznana klasa listy generycznej (TObjecList) dla indeksu %d!';
  RS_Err_UnknownClassTObjecList = '%s.%s: nieznana clasa listy generycznej dla indeksu %d!';
  RS_Err_ClassMethodExceptionMessage = '%s.%s: %s!';
  RS_Err_ClassMethodExceptionMessageWithStep = '%s.%s at "%s": %s!';
  RS_Err_OwnerClassMismatched = 'The owner class mismatched!';
  RS_ERR_ErrorInFile = 'Błąd w pliku %s';
  RS_ERR_ErrorInData = 'Błąd w danych';
  RS_PART_OF_REMOTE_SQL_ERROR_CODE_50000 = 'SQL Error Code: 50000';

  RS_WAR_NIPsAreDifferent = 'NIP firmy w bazie różni się od NIP-u w pliku licencji!'
    + #13#10'Popraw NIP dla firmy "%s"'
    + #13#10'lub skontaktuj się z Teroplanem, żeby wyjaśnić zaistniałą sytuację.';
  
  ERR_ObjectIsNotValidClass = 'BŁĄD: %s - podany parametr nie jest %s.';
  ERR_ObjectIsReadOnly = 'BŁĄD: %s - objekt %s nie można zmieniać.';
  ERR_ObjectInvalideFrameEditor = 'BŁĄD: %s: Niepoprawa forma do edycji obiektu DatabaseItem.';
  ERR_LibraryLoading = 'Nie udało się załadować bibliotekę.';

  SImplementationDiscardError = 'No implementation for method %s in %s';
  SAssignSourceTargetClassTypeError = 'The source and the target object class type are diffrent (%s.assign)';
  SUnassignedProperty = 'The unassigned property %s in %s';



  ERR_ALL = 'Operacja nie powiodła się z powodu nieznanego błędu!';

  EDITORS_CAPTION_ADD = 'Dodanie...';
  EDITORS_CAPTION_EDIT = 'Edycja...';
  EDITORS_CAPTION_PREP = 'Właściwości...';
  EDITORS_CAPTION_COPY = 'Kopiuj...';
  EDITORS_CAPTION_BEFORE_CLOSE = 'Wszystkie niezapisane zmiany zostaną utracone!'#13#10'Zamknąć edytor?';
  CAP_CLOSE = 'Zamknij';

  EDITORS_CAPTION_APPLICANT = 'Wnioskodawca';

  RS_PLACE_CHOICE = 'Wybierz miejscowość';
  RS_TICKETREGISTERCARD_CHOICE = 'Wybierz kartę pamięci';
  RS_TICKETREGISTERCARD = 'Karty pamięci bileterek';
  RS_TICKETREGISTERCARDPREFSET = 'Parametry bileterek';
  RS_DRIVERTICKETREGISTERCARDPREFSET = 'Parametry sprzedaży';
  RS_PLACE = 'Miejsowości';
  RS_DESIGNATION_CHOICE = 'Wybierz oznaczenie';
  RS_DESIGNATION = 'Oznaczenia';
  RS_COMPANY_CHOICE = 'Wybierz firmę';
  RS_COMPANY = 'Firmy';
  RS_COMPANY_HASCHILDREN = 'Firma posiada oddziały i nie może być usunięta!';
  RS_COMPANY_ISINLINEORRIDES = 'Odział przypisany jest do linii lub kursów i nie może być usunięty!';

  RS_GROUP_TYPE_CHOICE = 'Wybierz typ grupę';
  RS_GROUP_CHOICE = 'Wybierz grupę';
  RS_GROUP_DESCRIPTION = 'Opis Grupy';
  RS_GROUPS = 'Grupy';
  RS_CHOICE_REGISTRATION_DATE = 'Wybierz dzień rejestracji raportów zadaniowych';
  RS_CHOICE_REGISTRATION_PERIOD = 'Wybierz okres rejestracji raportów zadaniowych';
  RS_CHOICE_DRIVER_BALANCES_DATE = 'Wybierz dzień aktualności sald kierowców i kasjerów';

  ERR_PLACE_DEL =
    'Miejscowość jest wykorzystywana w bazie! Nie można usunąć.';
  ERR_SALESREPORT_DEL = 'Nie można usunąć raportu.';
  RS_SALESREPORT_SETDELETED_QUESTION = 'Czy oznaczyć ten raport jako usunięty?';
  RS_SALESREPORT_CORRECT_BEFORE_DELETE_QUESTION = 'Uwaga! Usunięcie raportu jest nieodwracalne! Czy na pewno usunąć?';
  RS_SALESREPORT_IN_STACK_BEFORE_DELETE_QUESTION = 'Uwaga! Usunięcie raportu z kolejki jest nieodwracalne! Czy kontynuować?';

  CAP_PASSANGERS = 'Pasażerowie';
  CAP_FileXTicketRegister = 'Zaprogramowane bileterki';
  CAP_FileXSolobus        = 'Programowane bileterki SoloBus';
  CAP_FileXEmar105        = 'Program. bileterki Emar-105/Kompatyb.';
  CAP_FileXEmar205        = 'Program. bileterki Emar-205';
  CAP_FileXEmar105Card        = 'Program. karty bileterki Emar-105/Kompatyb.';
  CAP_FileXEmar205Card        = 'Program. Komputer pokładowy.';
  CAP_SalesReports = 'Raporty zadaniowe';
  CAP_SalesReportsCancelled = 'Anulowane raporty zadaniowe';

  RS_RIDETIME = 'czas jazdy';
  RS_FAREDISTANCE = 'odległość taryfowa';
  RS_ROADDISTANCE = 'odległość drogowa';
  RS_ROAD_CATEGORY = 'Kategoria';
  RS_ROAD_CLASS = 'Klasa';

  { Driver }
  CAP_DriverDOCUMENT = 'Dokument';
  CAP_DriverCategory = 'Kategoria';
  CAP_DriverAction = 'Czynność';
  CAP_PersonWorkHistory = 'Zatrudnienie';
  CAP_PersonOSKHistory = 'OSK';
  CAP_PersonReductions = 'Ulgi';
  CAP_Driver = 'Kierowca';
  CAP_Group = 'Grupa';
  CAP_GroupName = 'Nazwa grupy';
  CAP_LocationIdentifier = 'Identyfikator lokalizacji';
  CAP_Trainer = 'Instruktor';
  CAP_Examiner = 'Egzaminator';
  CAP_Lecturer = 'Wykładowca';
  CAP_Student = 'Kursant';
  CAP_Diagnostician = 'Diagnosta';
  CAP_Handicapped = 'Osoba niepełnosprawna';
  CAP_Manager = 'Zarząd/Właściciel';
  CAP_Controller = 'Kontroler';
  CAP_User = 'Użytkownik';
  CAP_CHANGE_USER = 'Zmiana użytkownika';
  CAP_DriverRehab = 'Kierowca oś. rehablilitacji';
  CAP_TransportManager = 'Zarządzający transportem';
  CAP_CityPerson = 'Mieszkaniec';
  CAP_Applicant = 'Wnioskodawca';
  CAP_RODO = 'Usunięto dane osobowe';
  CAP_NotCityPerson = 'Odmowa wydania karty';
  CAP_Passanger = 'Pasażer';
  CAP_Tickets = 'Bilety';
  CAP_TicketsZones = 'Strefy biletowe';
  CAP_Cashier = 'Kasjer';
  CAP_Driver_Number = 'Numer pracownika'; //T24663
  CAP_Driver_IDNumberHRSystem = 'Numer w syst. HR';  //T24663
  CAP_TicketValue = 'Wartość sprz.';
  CAP_CashValue = 'Utarg got.';
  CAP_NoCashValue = 'Utarg bezgot.';
  CAP_Deduction = 'Odliczenie';
  CAP_Advance = 'Zaliczka';
  CAP_Return = 'Zwrot';
  CAP_Amount = 'Kwota';
  CAP_DateOfPaymentOrReturn = 'Data wpłaty/zwrotu';
  CAP_PaymentType = 'Sposób wpłaty';
  CAP_Employee = 'Pracownik';
  CAP_Employees = 'Pracownicy';
  CAP_RKUtarg = 'Numer RK - utarg';
  CAP_RKWplata = 'Numer RK - wpłata';
  CAP_Wplata = 'Wpłata';
  CAP_Carrier = 'Przewoźnik';

  //CAP_NUMEDBUS = 'Kolejność ulg w bileterkach autobusowych i komputerze pokładowym e-podróżnik';
  CAP_NUMEDBUS = 'Kolejność ulg w bileterkach autobusowych'; //T19847
  CAP_NUMEDSTAT = 'Kolejność ulg w bileterkach stacjonarnych';
  CAP_NUMEDCARD = 'Kolejność ulg';
  CAP_NUMEDRELIEFTICKET = 'Kolejność ulg w ulgach biletow';

  CAPT_Cashiers_DEV = 'Kasjerzy (Dworzec)';
  CAPT_Drivers_DEV = 'Kierowcy';
  CAPT_GroupDrivers_DEV = 'Grupy kierowców i kasjerów';
  CAPT_BUSSES_DEV = 'Pojazdy';
  CAPT_BUSVEHICAL_DEV = 'Autobusy i pojazdy';
  CAPT_BUSVEHICAL_PARUS = 'Autobusy';
  CAPT_BUSGROUPS_DEV = 'Marki i modele';
  CAPT_BUSGROUPS_PARUS = 'Grupy autobusów';
  CAPT_CEDULY = 'Ceduły';
  CAPT_CEDULY_TICKETS = 'Bilety';
  CAPT_SALEDEVICES_DEV = 'Urządzenia';
  CAPT_ZbioryDanych_DEV = 'Zbiory danych';
  CAPT_TRP_DEV = 'Programowanie bileterek';
  CAPT_REPORTS_DEV = 'Zestawienia i raporty';
  CAPT_DATA_TICKETREGISTER = 'Dane dla bileterki';
  CAPT_Passengers_DEV= 'Pasażerowie';
  CAPT_Date_DEV= 'Dane';
  CAPT_SaleReports_DEV= 'Raporty sprzedażowe';
  CAPT_SaleRegister_DEV= 'Rejestracja rozliczeń';
  CAPT_SaleAnalysis_DEV= 'Analizy sprzedaży';
  CAPT_TransportAnalysis_DEV= 'Analizy przewozów';
  CAPT_TimelinessAnalysis_DEV= 'Analizy punktualności';
  CAPT_IncInspection_DEV= 'Nadzór ruchu';
  CAPT_RoudInspection_DEV= 'Przebiegi jazd';
  CAPT_PersonGroupType_DEV = 'Typy grup mieszkańców';
  CAPT_PersonGroup_DEV = 'Grupy mieszkańców';
  CAPT_BusStopManager_DEV = 'Zarządzanie przystankami';
  CAPT_TICKETS_CANCELLATION = 'Bilet do anulowania';
  CAPT_AUTO_REGISTRATION_LONG = 'Automatyczna rejestracja';

  CAPT_Task = 'Zadania';
  CAPT_TaskGroup = 'Grupy zadań';

  CAP_Name = 'Nazwa';
  CAP_Description = 'Opis';

  CAP_BusGroup = 'Marki i modele';
  CAP_PersonGroupType = 'Typ Grupy';
  CAP_PersonGroupCount = 'Liczność';
  CAP_PersonGroup = 'Grupa';
  CAP_PersonGroupActive = 'Aktywna';
  CAP_DRIVERS = 'Kierowcy';
  CAP_TRAINERS = 'Instruktorzy';
  CAP_LECTURERS = 'Wykładowcy';
  CAP_EXAMINERS = 'Egzaminatorzy';
  CAP_STUDENTS = 'Kursanci';
  CAP_Handicappeds = 'Osoby niepełnosprawne';
  CAP_Managers = 'Zarządcy/Właściciele';
  CAP_Diagnosticians = 'Diagności';
  CAP_Cashiers = 'Kasjerzy';
  CAP_Controllers = 'Kontrolerzy';
  CAP_Users = 'Użytkownicy';
  CAP_DriversRehab = 'Kierowcy oś. rehablilitacji';
  CAP_TransportManagers = 'Zarządzający transportem';
  CAP_DISPFile = 'Zbiór danych dla urządzeń';
  CAP_DISPFileKPEP = 'Zbiór danych do e-podróżnik i Bileterki e-podróżnik';
  CAP_DISPFileRJA = 'Zbiór danych - Informica/Foris';
  CAP_DISPFileINF = 'Zbiór danych - systemy zewnętrzne';
  RS_File = 'Zbiór danych';

  CAP_DISPFileSoloBus = 'Zbiory danych dla bileterki SoloBus';
  CAP_DISPFileEmar105 = 'Zbiory danych dla bileterek';//'Zbiory danych dla bileterki Emar-105';
  CAP_DISPFileEmar205 = 'Zbiory danych dla bileterki Emar-205';

  CAP_COMBUSTIONSTANDARD = 'Normy paliwowe';
  CAP_CashDeskSettings = 'Ustawienia kas biletowych';
  CAP_Unknown = 'Nieznany';
  CAP_REFUEL = 'Tankowanie';

  CAP_SalesReport = 'Raport sprzedaży';
  CAP_ReportNumber = 'Numer raportu';
  CAP_ReportFileName = 'Plik z raportem';
  CAP_UserStationNumber = 'Stanowisko';
  CAP_RegistrationDate = 'Data rejestracji';
  CAP_RegistrationYear = 'Rok rejestracji';
  CAP_RegistrationMonth = 'Miesiąc rejestracji';
  CAP_FirstName = 'Imię';
  CAP_LastName = 'Nazwisko';
  CAP_WorkerNumber = 'Nr prac.';
  CAP_Deficiency = 'Niedobór';
  CAP_Surplus = 'Nadwyżka';
  CAP_PostCode = 'Kod pocztowy';
  CAP_Address = 'Adres';
  CAP_PassangerNumber = 'Numer pasażera';
  CAP_PESEL = 'PESEL';
  CAP_PassangerCompanyName = 'Firma pasażera';
  C_TXT_FAILURES = 'Awarie';
  C_TXT_FAILURES_DELETED = 'Usunięte awarie';
  C_TXT_MISSING_RECEIPTS = 'Braki paragonów';
  C_TXT_NO_TAKINGS_IN_SALESREPORT = 'Brak utargu w RK';
  C_TXT_NO_PAYMENTS_IN_SALESREPORT = 'Brak informacji o wpłacie w RK';
  C_TXT_NO_CASHIER_OR_DRIVER = 'Brak kasjera/kierowcy';
  C_TXT_REGISTRATION_YEAR_MONTH = 'Rok oraz miesiąc rejestracji';
  C_TXT_REPORT_TYPES = 'Typy raportów';
  CAP_CASH_REPORTS = 'Raporty kasowe';
  CAP_CASH_REPORT_CLOSE = 'Zamknięcie reportu kasowego';
  CAP_CASH_REPORT_SPLIT_AMOUNT = 'Rozbij wpłatę / rozbij utarg';
  CAP_Reason = 'Powód';
  CAP_SaleDate_Date = 'Data sprzedaży';
  CAP_Ticket_ValidFrom = 'Data ważności od';
  CAP_Ticket_ValidTo = 'Data ważności do';
  CAP_Ticket_TicketType_Name = 'Typ biletu';
  CAP_Ticket_GenreName = 'Rodzaj biletu';
  CAP_BusStop_NameFrom = 'Nazwa przystanku początkowego';
  CAP_BusStop_NameTo = 'Nazwa przystanku końcowego';

  CAP_RZNumber = 'Numer RZ';
  CAP_RZUser = 'Użytkownik rejestrujący RZ';
  CAP_RZFielOrygName = 'Zbiór z rozkładem';

  CAP_UploadDescription = 'Typ przejazdu';
  RS_SKIPPED_TICKETS = 'Bilety pominięte w analizach';
  C_TXT_QUESTION_CREATE_CASHREPORT = 'Brak otwartego raportu kasowego w dniu dzisiejszym.'#13#10 +
    'Czy otworzyć raport kasowy z dzisiejszą datą?';
  C_FMT_IMPORTANT_DRIVER_FOR_PAYMENT = 'Dla wprowadzanie wpłaty w wysokości %.2f zł powinien być wybrany kierowca.';

  CAP_LineRideTicketPools = 'Pule biletów kursów dla linii';

  CAP_FileWithTheReport = 'Plik z raportem';
  CAP_WaitingOrIncorrect = 'Czeka/Błąd';
  CAP_LastTransactionDateSaldoZero = 'Liczba dni od kiedy saldo jest niezerowe';
  CAP_DateOfLastPayment = 'Data ostatniej wpłaty';

  RS_VEHICLES_BUSES = 'Autobusy';
  RS_VEHICLES_OTHERS = 'Inne pojazdy';
  RS_VEHICLES_TAXIS = 'Taksówki';
  RS_VEHICLES_TRUCK = 'Ciężarówki';
  RS_VEHICLES_OSK = 'Pojazdy OSK';
  RS_VEHICLES_TOWED = 'Pojazdy holowane';
  RS_VEHICLES_LPC = 'Pojazdy';
  RS_VEHICLES_REHAB = 'Pojazdy oś. rehabilitacji';

  RS_VEHICLE_BUS = 'Autobus';
  RS_VEHICLE_OTHER = 'Inny pojazd';
  RS_VEHICLE_TAXI = 'Taksówka';
  RS_VEHICLE_TRUCK = 'Ciężarówka';
  RS_VEHICLE_OSK = 'Pojazd OSK';
  RS_VEHICLE_TOWED = 'Pojazd holowany';
  RS_VEHICLE_LPC = 'Pojazd';
  RS_VEHICLE_REHAB = 'Pojazd oś. rehabilitacji';
  RS_BUSSTAND = 'Przystanek komunikacyjny';
  RS_BUSSTAND_CHOICE = 'Wybierz przystanek komunikacyjny...';


  RS_BUS_GROUP_CHOICE = 'Wybierz markę / model';
  RS_BUS_GROUP = 'Marka / Model';
  RS_ROADPOINT_CHOICE = 'Wybierz miejsce postoju';
  RS_ROADPOINT = 'Miejsca postoju';
  RS_BUSPC_CHOICE = 'Wybierz komputer pokładowy';
  RS_BUSPC_MOBILE_CHOICE = 'Wybierz urządzenie mobilne';
  RS_TICKETREGISTER_CHOICE = 'Wybierz bileterkę';
  RS_BUSPC = 'Komputery pokładowe';
  RS_MOBILES = 'Urządzenia mobilne';
  RS_MOBILE = 'Urządzenie mobilne';
  RS_SMARTPHONE = 'Smartfon';
  RS_TICKETREGISTER = 'Bileterki';
  RS_COMBUSTIONSTANDARDS = 'Normy paliwowe';
  RS_COMBUSTIONSTANDARD_CHOICE = 'Wybierz normę paliwową';

  RS_ERR_BCNotSaved =
    'Dane komputera pokładowego autobusu nie zostały zapisane.';
  RS_ERR_BGNotSaved = 'Dane marki i modelu autobusu nie zostały zapisane.';
  RS_ERR_BusTypeNotSaved = 'Typ autobusu nie został zapisany.';

  RS_F_TYPE = 'Typ';
  RS_F_BRAND = 'Marka / Model';

  CAP_BUSDOCUMENT = 'Dokument';
//  RS_BUSPCHISTORY = 'Komputer pokładowy';

  { Payments }
  RS_paymentByCash = 'gotówka';
  RS_paymentByCashFlow = 'przelew';
  RS_paymentByCreditCard = 'karta płatnicza';
  RS_paymentByCheck = 'czek';
  RS_paymentByVoucher = 'bon';

  RS_paymentByCard ='Bezgot.-karta';
  RS_paymentByTransfer='Bezgot.-przelew';
  RS_paymentByDifferent='Bezgot.-inne';

  RS_NOT_RETURNED = 'niezwrócone';

  _PASSANGER = 'Pasażerowie';
  _EMCARD = 'EM-Karty';
  _EMCARDXPASSANGER = 'Zarejestrowane EM-Karty';
  _EMCARD_RIDES = 'Przejazdy z wybraną EM-Kartą';
  _EMCARD_RIDES_PRICE_COMPUTE = 'Historia sprzedaży, przejazdów i zmian';

  //_EMCARD_DEPOSIT = 'Kaucje za EM-Karty';
  _EMCARD_DEPOSIT = 'Kaucja za wydanie karty zbliżeniowej';
  _EMCARD_TICKET_PRICE_CHANGED = 'Zmiany cen biletów EM-Kartowych z dworca';
  _EMCARD_NUMBER = 'Nr EM-Karty';
  _EMCARD_NUMBER_DRIVER = 'Karta nr %d, %s %s';
  _DISPFile = 'Pliki danych';
  _EMCARD_HISTORY = 'Historia sprzedaży na wybraną EM-Kartę';
  _EMCARD_TICKET_PRICE_CHANGES_HISTORY = 'Zmienione ceny biletów';
  _EMCARD_EMCARD_SALE_LOCKED_PAFILE_FMT = 'Sprzedaż zablokowana w pliku %s';
  _EMCARD_FIRSTTICKET_SALEDATE = 'Data sprzedaży pierwszego biletu';
  _EMCARD_FIRSTTICKET_NUMBER = 'Numer pierwszego biletu';
  _EMCARD_TICKET_NEW_DATE_FROM = 'Nowa data od biletu';
  _EMCARD_TICKET_NEW_DATE_To = 'Nowa data do biletu';

  RS_F_ALL = 'wszystkie';

  RS_LIC_MAXCONNECTIONS =
    'Osiągnięto dopuszczalną liczbę połączeń do serwera z licencji';
  RS_LIC_DRIVERS_OUT_OF_MAXVALUE = 'Została osiągnięta maksymalna liczba kierowców z licencji.'#13#10 +
    'Usuń niepotrzebnych kierowców lub skontaktuj się z Informicą.';
  RS_LIC_MAXBUSNO_OUT_OF_MAXVALUE = 'Została osiągnięta maksymalna liczba autobusów oraz pojazdów z licencji.'#13#10 +
    'Usuń niepotrzebne autobusy czy pojazdy lub skontaktuj się z Informicą.';

  RS_DS_MAX_CONNECTION_REACHED = 'Osiągnięto maksymalną liczbę połączeń do usługi dostępu do bazy danych (%d/%d)!';
  RS_DS_MAX_CONNECTION_CONTACT = 'Skontaktuj się z sprzedawcą oprogramowania w celu wykupienia dodatkowych licencji.';
  RS_DS_NEW_CONNECTION = 'Nowe połączenie: %s';
  RS_DS_ADMIN_CONNECTION = 'Połączenie administracyjne';
  RS_DS_REST_CONNECTION = 'Połączenie REST';
  RS_DS_CONNECTED_WITH = 'Połączony z: %s';

  RS_DSSERVER_DISPLAY_NAME = 'Serwer Informica';

  RS_IAUTSERVER_DISPLAY_NAME = 'Serwer automatyzacji Informica';
  RS_IAUTSERVER_IS_WORKING = 'Usługa serwer automatyzacji Informica działa poprawnie';
  RS_IAUTSERVER_IS_NOT_WORKING = 'Usługa serwer automatyzacji Informica jest wyłączona. Raporty nie będą rejestrowane!'#13#10'Kliknij, żeby uruchomić usługę';
  RS_IAUTSERVER_HAS_REPORTS_WITH_ERRORS = 'Są błędy przy automatycznej rejestracji!'#13#10'Kliknij i sprawdź raporty, które spowodowały błędy!';

//  _CAPT_ROAD_DEV = 'Elementy tras';
  _CAPT_TERR_DEV = 'Podział terytorialny';
  _CAPT_GOV_DEV = 'Urzędy';
//  _CAPT_CAL_DEV = 'Kalendarz i oznaczenia';
  _CAPT_EXPIRY = 'Umorzenia, wygaśnięcia...';
  _CAPT_APP_FORM = 'Formularze wniosków';
//  _CAPT_ORG_DEV = 'Firmy i urzędy';
//  _CAPT_TERRITORIAL = 'Podział terytorialny';
  _CAPT_ORG_PARUS = 'Urzędy';
//  _CAPT_LICENCES = 'Licencje';
  _CAPT_OPTIONS = 'Opcje';
  _CAPT_FEE = 'Opłaty';
//  _CAPT_SETTINGS_BASIC = 'Podstawowe';
//  _CAPT_SETTINGS_Import = 'Import';
  _CAPT_SETTINGS_ImportExport = 'Import i Eksport';
  _CAPT_SETTINGS_ImportData = 'Import danych';
  _CAPT_SETTINGS_IMPORTFROMFILE = 'Import z pliku';
  //
  _PREPARE_INTERFACE = 'Ładowanie interfejsu...';
  _LOG_PROC_RUN = 'Uruchamianie funkcji';
  _LOG_VIEW_RUN = 'Wybranie widoku';
  _LOG_DICT_RUN = 'Uruchamianie słownika';
  _LOG_BUTTON_RUN = 'Nacisnięcie przycisku edycyjnego';
  _LOG_PASS_CHANGE = 'Zmieniono hasło użytkownikowi: %s';
  _LOG_PASS = 'Zmiana hasła';

  _LOG_USR_GROUP_ADD = 'Dodanie grupy';
  _LOG_USR_ADD = 'Dodanie użytkownika';
  _LOG_USR_NEW = 'Dodano: %s';
  _LOG_USR_DEL = 'Usunięto użytkownika';
  _LOG_USR_GROUP_DEL = 'Usunięto grupę';
  _LOG_USR_GROUP_EDIT = 'Edycja grupy';
  _LOG_USR_EDIT = 'Edycja użytkownika';
  _LOG_USR_ED_CHANGES = 'Zmieniono %s z %s na %s';
  _LOG_USR_ED_CHANGES_PRIV = 'Zmieniono uprawnienia użytkownika %s';
  _LOG_USR_GR_ED_CHANGES_PRIV = 'Zmieniono uprawnienia grupy %s';

  _HTTP_USER = 'Login PortalOSK';
  _HTTP_USERS = 'Loginy PortalOSK';

  _LOG_APP = 'Aplikacja';
  _LIC_ERR = 'Bład licencji programu!';

  stHISTORY = 'Historia';
  stUSER = 'Użytkownik';
  stDATE = 'Data zmiany';
  stKIND = 'Rodzaj zmiany';
  _COMPANIES = 'Przewoźnicy';
  _COMPANIES_PRZED = 'Przedsiębiorcy';
  _OSK = 'OSK';
  _PARKING = 'Parkingi';
  _HolCompany = 'Firmy holujące';
  _DIAGNOSTIC = 'Stacje diagnostyczne';
  _ANOTHERCOMPANIES = 'Inne';

  CAP_ROADPOINT = 'Punkt drogowy';
  CAP_ROAD = 'Droga';
  RS_F_ROAD = 'Drogi';
  RS_F_TERRITORIAL = 'Podział terytorialny';
  RS_KATYGORY_NULL = '_brak';

  ERR_ROAD_INS_1 = 'Wartość pola ''Numer'' nie może być pusta!';
  ERR_ROAD_INS_2 = 'Wartość pola ''Nazwa'' nie może być pusta!';
  ERR_ROAD_INS_3 = 'Wartość pola ''Numer'' musi być unikatowa!';
  ERR_ROAD_INS_4 = 'Wartość pola ''Typ'' nie może być pusta!';

  ERR_ROADPOINT_INS_1 = 'Wartość pola ''Nazwa'' nie może być pusta!';
  ERR_ROADPOINT_INS_2 = 'Wartość pola ''Typ'' nie może być pusta!';
  ERR_ROADPOINT_DEL =
    'Pozycja nie może być usunięta z powodu występujących zależności.';

  CAP_ATTRSTAND = 'Atrybut stanowiska';

  CAP_COUNTRY = 'Kraj';
  CAP_PROVINCE = 'Województwo';
  CAP_DISTRICT = 'Powiat';
  CAP_BOROUGH = 'Gmina';
  CAP_PLACE = 'Miejscowość';

  CAP_CashDepositMachinesGLOBE = 'Wpłatomaty';
  CAP_CashDepositMachineGLOBE = 'Wpłatomat';
  CAP_DeviceOfAccounting = 'Rozliczarka';
  CAP_DevicesOfAccounting = 'Rozliczarki';
  CAP_StationReaders = 'Czytniki dworcowe EM-Kart';
  CAP_StationReader = 'Czytnik dworcowy EM-Kart';
  CAP_ChargeTerminal = 'Terminal doładowań';
  CAP_ChargeTerminals = 'Terminale doładowań';
  CAP_EmCardLoader = 'Programatory EM-kart';
  CAP_BusRuns = 'Przejazdy';
  CAP_BusRun = 'Przejazd';

  RS_TICKETOFFICE_CHOICE = 'Wybierz kasę biletową';
  CAP_TICKETOFFICES = 'Kasy biletowe';
  MSG_REMOVE_TICKETOFFICES =
    'Czy na pewno chcesz usunąć przypisaną kasę biletową do bileterki?';
  MSG_CONFIRMATION_OF_EDITING_DELETED_PERSON = 'Edycja spowoduje przywrócenie skasowanej osoby. Czy chcesz kontynuować?';
  MSG_CONFIRMATION_OF_EDITING_DELETED_BUS = 'Edycja spowoduje przywrócenie skasowanego autobusu\pojazdu. Czy chcesz kontynuować?';
  MSG_CONFIRMATION_OF_EDITING_DELETED_TIMETABLE = 'Edycja spowoduje przywrócenie skasowanego rozkładu. Czy chcesz kontynuować?';

  MSG_CONFIRM_CORRECT_ROUTE_DISTANCES = 'Funkcja zmodyfikuje odległości taryfowe ' +
    'na podstawie odległości drogowych zaokrąglonych do pełnych kilometrów.' +
    #13'Potwierdź wykonanie funkcji.'#13#10'Tak - dla aktywnej trasy; Wszyskie - dla wszystkich tras tej linii';
  MSG_CONFIRM_CORRECT_ROUTE_DISTANCES_FOR_RIDE = 'Funkcja zmodyfikuje odległości taryfowe ' +
    'na podstawie odległości drogowych zaokrąglonych do pełnych kilometrów.' +
    #13'Potwierdź wykonanie funkcji.';
  MSG_QUESTION_SAVE_CHANGES = 'Zapisać zmiany?';
  MSG_QUESTION_CONTINUE = 'Czy chcesz kontynuować?';
  MSG_WARNING_FIX_OR_CANCEL = 'Uzupełnij dane lub anuluj zmiany';

  CAP_EMAR_CKM100 = 'Emar CKM-100';
  CAP_TicketControlDev = 'Czytnik kontrolera';
  CAP_TicketControlDevs = 'Czytniki kontrolera';

  YOUARELOGOUT = 'Zostałeś wylogowany!';
  YOUARESHOUTDOWN = 'Twoja aplikacja została zamknięta przez administratora!';
//  IDLETIME =        'Czas do automatycznego wylogowania: %s';
  AUTOLOGOUT = 'Automatyczne wylogowanie.';
  SECTOAUTOLOGOUT = 'Czas do automatycznego wylogowania: %s';
  FROMIP = 'From IP address: %s';

  _CONNECT_ERR = 'Brak połączenia z serwerem!';

  _LICC_ERR_CO =
    'Plik licencji jest przypisany do innej firmy! Skontaktuj się z administratorem.';
  _LICC_ERR_FILE =
    'Nie można odczytać licencji z bazy! Skontaktuj się z administratorem.';

  CAP_TicketRegisterCard = 'Karta pamięci bileterki';

  ADMINLOGPROCNAME_PINCHANGE = 'PIN_Change';

  CAP_TicketRegisterTypeBusEmar = 'Bileterka autobusowa EMAR-105';
  CAP_TicketRegisterTypeBuses = 'Bileterki autobusowe';
//  CAP_TicketRegisterTypeBusSolobus = 'Bileterka autobusowa SOLOBUS';
  CAP_TicketRegisterTypeBusEmar305 = 'Bileterka autobusowa EMAR-305';
  CAP_TicketRegisterTypeBusEmar205 = 'Bileterka autobusowa EMAR-205';
//  CAP_TicketRegisterTypeBusesEmar205 = 'Bileterki autobusowe EMAR-205';

  CAP_TicketRegisterTypeSaleDevice = 'Bileterka dworcowa';
  CAP_TicketRegisterTypeSaleDevices = 'Bileterki dworcowe';

  CAP_LINE = 'Linia';
  CAP_LINE_NAME = 'Nazwa linii';
  CAP_RIDE_NUMBER = 'Numer kursu';
  CAP_RIDE_DATE = 'Data przejazdu';
  CAP_RideRelationship = 'Relacja kursu';

  _CALENDAR = 'Kalendarz';
  _RIDEDES = 'Oznaczenia kursów';
  C_FMT_DATA_FROM_TO = 'od %s do %s';
  DefaultParameterSetTEMPLTE = '[ZESTAW]: od [DATAOD] do [DATADO]. [NAZWA]';
{$region 'Lines'}
        LINES_CopyLinesResult_ToCopy = 'Kursów do skopiowania';
        LINES_CopyLinesResult_Copied = 'Kursów skopiowanych';
        LINES_CopyLinesResult_VariantsChanged = 'W tym zmieniono numer wariantu kursu';
{$endregion}

{$region 'Rides'}
    RIDES_RaidPair_WarrningPattern = 'UWAGA! Kursy sparowane muszą mieć ten sam kalendarz dni wykonywania! Upewnij się, że sparowany kurs ma przypisane te same oznaczenia definicji dni wykonywania co kurs edytowany: %s.';
{$endregion}

{$region 'LineEditorFrame'}
  RES_LINE_EDITOR_MSG_QUESTION_CONFIRM_DELETE =
    'Potwierdzasz usunięcie wpisu ?';
  RES_LINE_EDITOR_MSG_QUESTION_CONFIRM_DELETE_BRANCH =
    'Podwierdź usunięcie odgałęzienia niepłatnego';
  RES_LINE_EDITOR_MSG_QUESTION_CONFIRM_REPLACE =
    'Potwierdzasz zastąpienie przystanku z trasy TAM i trasy POWRÓT ?';
  RES_LINE_EDITOR_MSG_QUESTION_CONFIRM_DEL_BUSSTOPS_ROADPOINTS =
    'Potwierdzasz usunięcie przystanków / punktów drogowych z trasy ?';
  RES_LINE_EDITOR_MSG_QUESTION_CONFIRM_DEL_ROADPOINT_IN_OPPOSITE_ROUTE =
    'Czy usunąć %s: "%s" również z trasy w przeciwnym kierunku ?';
  RES_LINE_EDITOR_CAN_NOT_REPLACE_BUSSTOPS = 'Nie można zastąpić przystanków.';
  RES_LINE_EDITOR_CAN_NOT_REPLACE_ROADPOINT =
    'Nie można zastąpić punktu drogowego.';
  RES_LINE_EDITOR_LINEROUTE_STATUS_ERROR =
    'Trasa jest zawieszona lub zlikwidowana.';
  RES_LINE_EDITOR_LINEROUTE_CAN_ADD_REMOVE_POINTS =
    'Są kursy na tej trasie linii, które znajdują się w zbiorze lub dla których została zarejestrowana sprzedaż.';
  RES_LINE_EDITOR_ACHTUNG = 'UWAGA';
  RES_LINE_EDITOR_CAN_NOT_INSERT_THE_SAME_ROUTEPOINT =
    'Nie można dodawać tego samego punktu drogowego obok siebie w trasie linii.';
  RES_LINE_EDITOR_ADD_NEW_EMPTY_ROUTE = 'Dodaj nową pustą trasę: ';
  RES_LINE_EDITOR_LINE_SERVICE =
    'Aby wybrać ten rodzaj usługi typ linii musi być "komunikacja zamknięta".';
  RES_LINE_EDITOR_CHOOSE_COMPANY =
    'Aby dodać zezwolenie najpierw wybierz firmę!';
  RES_LINE_EDITOR_DEL_ROUTE = 'Usuwanie trasy linii';
  RES_LINE_EDITOR_CHANGE_STATUS_ROUTE = 'Zmiana statusu trasy linii';
  RES_LINE_EDITOR_COPY_ROUTE = 'Kopiowanie trasy linii';
  RES_LINE_EDITOR_SELECTED_ROUTE = 'Wybrana trasa: ';
  RES_LINE_EDITOR_SELECTED_ROUTE_ERROR = 'Zaznacz trasę';
  RES_LINE_EDITOR_WHOLE_LINE_VARIANT = 'Cały wariant linii';
  RES_LINE_EDITOR_ROUTE_THERE = 'Trasę TAM';
  RES_LINE_EDITOR_ROUTE_RETURN = 'Trasę POWRÓT';
  RES_LINE_EDITOR_ALL_ROUTES = 'Wszystkie trasy linii';
  RES_LINE_EDITOR_CHANGE_RIDES_STATUS = 'Zmień statusy kursów na wskazany, niezależnie od aktualnych statusów kursów'+
                                          #13#10+'(nie dotyczy kursów zlikwidowanych).';
  RES_LINE_EDITOR_BTN_OK = 'wykonaj';
  RES_LINE_EDITOR_BTN_CANCEL = 'anuluj';
  RES_LINE_EDITOR_RECALCULATE_FOREIGN_PRICES =
    'Czy przeliczyć podział cen w taryfie zagranicznej?';

  RES_LINE_EDITOR_ROUTE_NOT_THERE = ' nie jest trasą TAM.';
  RES_LINE_EDITOR_ROUTE_HAVE_RETURN = ' już ma trasę POWRÓT.';
  RES_LINE_EDITOR_ROUTE_MUST_HAVE_START_END_BUSSSTOP =
    'Trasa musi się rozpoczynać i kończyć przystankiem.';
  RES_LINE_EDITOR_ROUTE_EMPTY_EXISTS =
    'Jest już pusta trasa. Uzupełnij w niej dane i dodaj nową pustą trasę';
  RES_LINE_EDITOR_CREATING_RETURN_ROUTE = 'Tworzenie trasy powrotnej';
  RES_LINE_EDITOR_BASED_ON_ROUTE_THERE = 'powrót na podstawie trasy TAM';
  RES_LINE_EDITOR_EMPTY_BACK_ROUTE = 'pusta trasa powrotna';
  RES_LINE_EDITOR_CAN_NOT_COPY_RETURN_ROUTE =
    'Nie można kopiować trasy POWRÓT bez trasy TAM.';
  RES_LINE_EDITOR_ROUTE_USED_CAN_NOT_DELETE =
    'Trasa jest używana i nie można jej usunąć.';

  RES_LINE_EDITOR_ERROR_edCompany =
    'Firma|Należy określić firmę właściciel linii.|0';
  RES_LINE_EDITOR_ERROR_edName = 'Nazwa linii|Pole nie może być puste.|0';
  RES_LINE_EDITOR_ERROR_edProvince =
    'Województwo|Należy określić wojewódzwto, do którego jest przypisana linia.|0';
  RES_LINE_EDITOR_ERROR_edLineNumber =
    'Numer|Pole nie może być puste. Zakres od 1 do 999999.|0';
  RES_LINE_EDITOR_ERROR_dtpValidFrom =
    'Ważna od|Pokrywające się okresy ważności linii lub przeszła data.|0';
  RES_LINE_EDITOR_ERROR_dtpValidFrom_CanEdit =
    'Ważna od|Linia jest w zbiorze lub istnieje sprzedaż.|0';
  RES_LINE_EDITOR_ERROR_dtpValidTo =
    'Ważna do|Data końcu ważności linii nie może być wcześniejsza niż data początku jej ważności lub przeszła data.|0';

  RES_LINE_EDITOR_CAN_NOT_ADD_BRANCH_UNPAID_HERE =
    'Nie można dodać odgałęzienia niepłatnego w tym miejscu.';
  RES_LINE_EDITOR_ADD_BRANCH_UNPAID = 'Dodaj odgałęzienie niepłatne';
  RES_LINE_EDITOR_EDIT_BRANCH_UNPAID = 'Edytuj odgałęzienie niepłatne';

  RES_LINE_EDITOR_ENTER_CORRECT_TARIFF_DISTANCE =
    'Wpisz prawidłową odległość taryfową';
  RES_LINE_EDITOR_RIDES_EXISTS_WITH_DATA =
    'Są kursy na tej trasie linii, które znajdują się w zbiorze lub dla których została zarejestrowana sprzedaż.';
  RES_LINE_EDITOR_ROUTE_CAN_NOT_EDIT = 'Trasy nie można edytować.';
  RES_LINE_EDITOR_ROUTE_CAN_NOT_ADD_DEL_ROADPOINTS =
    'Nie można dodawać ani usuwać przystanków / punktów drogowych.';
  RES_LINE_EDITOR_RIDES_EXISTS = 'Są kursy na tej trasie linii.';

  RES_LINE_EDITOR_ERRORS_IN_MESSAGE_WINDOW = 'Są błędy w okienku z komunikatami.';
  RES_LINE_EDITOR_ADD_BUSSTOPS_CONFIRMATION = 'Czy dodać przystanki dodane do tras linii również do tras kursów?';

  RES_LINE_EDITOR_CHOOSE_PERMISSION = 'Wybierz zezwolenie';
  RES_LINE_EDITOR_LINE_ROUTE = 'Trasa linii';
  RES_LINE_EDITOR_ALL_ROUTES_CHOOSEN = 'wszystkie trasy - wybrano ';
  RES_LINE_EDITOR_LINEVARIANT_FORMAT = 'wariant %d, kierunek %s - %s';

  RES_LINE_EDITOR_ERROR_BUSSTOPS_REPEATED_ON_BEGINNIING_OF_ROUTE = 'Trasa nie może zacznać się dwoma takimi samymi przystankami.';
  RES_LINE_EDITOR_ERROR_BUSSTOPS_REPEATED_ON_THE_END_OF_ROUTE = 'Trasa nie może kończyć się dwoma takimi samymi przystankami.';
  RES_LINE_EDITOR_ERROR_BUSSTOPS_REPETITIONS_EXCEEDED = '[%s] Taki sam przystanek nie może występować więcej niż %d razy z rzędu.';
  RES_LINE_EDITOR_ERROR_BUSSTANDS_REPETITIONS_EXCEEDED = '[%s] To samo stanowisko nie może występować %d razy z rzędu.';
  //RES_LINE_EDITOR_ERROR_BUSSTOPS_REPETITION_DISTANCE_TO_HIGH = '[%s] Dystans między sąsiednimi identycznymi przystankami musi wynosić 0.';
  RES_LINE_EDITOR_ERROR_BUSSTOPS_REPETITION_DISTANCE_TO_HIGH = '[%s] Dystans, czas przejazdu i postoju między sąsiednimi identycznymi przystankami musi wynosić 0.';

  RES_LINE_EDITOR_ERROR_DISTANCES_FORMAT =
    'Odległość pomiędzy przystankami %s i %s w trasie jest różna niż wynikająca z kilometraża drogi dla tych przystanków!';
  RES_LINE_EDITOR_ERROR_NO_ROUTE_THERE_FORMAT = '%sBrak trasy tam.';
  RES_LINE_EDITOR_ERROR_NO_ROUTE_RETURN_FORMAT = '%sBrak trasy powrotnej.';
  RES_LINE_EDITOR_ERROR_NOT_CORRECT_BUSSTOP_TYPE_FORMAT =
    '%sUwaga: niepoprawny typ przystanku "%s" dla linii autobusowej!';
  RES_LINE_EDITOR_ERROR_NOT_CORRECT_BUSSTOPS_LINE_NO_PUBLIC_FORMAT =
    '%sUwaga: linia nie jest użyteczności publicznej, a zawiera przystanki tylko dla operatora!';
  RES_LINE_EDITOR_ERROR_NOT_CORRECT_ORGANIZER_LINE_NO_PUBLIC_FORMAT =
    '%sUwaga: linia nie jest użyteczności publicznej, a jest określony organizator przewozów!';
  RES_LINE_EDITOR_ERROR_NOT_CORRECT_NO_ORGANIZER_LINE_PUBLIC_FORMAT =
    '%sUwaga: linia jest użyteczności publicznej, a nie jest określony organizator przewozów!';
  RES_LINE_EDITOR_ERROR_LINE_HAVE_NOT_CORRECT_BUSSTOPS_FOR_SPECIAL_COMUNICATION_FORMAT =
    '%sUwaga: linia zawiera przystanki, które nie powinny być wykorzystywane w komunikacji regularnej specjalnej!';

  RES_LINE_EDITOR_ERROR_LINE_HAVE_CITY_BUSSTOPS_FORMAT =
    '%sUwaga: linia zawiera przystanki z ograniczeniem do linii miejskich!';
  RES_LINE_EDITOR_ERROR_LINE_HAVE_COMMUNITY_BUSSTOPS_FORMAT =
    '%sUwaga: linia zawiera przystanki z ograniczeniem do linii powiatowych lub gminnych!';
  RES_LINE_EDITOR_ERROR_LINE_HAVE_DIFFERENT_DISTANCES_FORMAT =
    '%sUwaga: Kilometraż drogowy różni się od kilometraża taryfowego. Użyj przycisku "Odległości taryfowe równe drogowym"';
  RES_LINE_EDITOR_ERROR_LINE_HAVE_OVER_50KM_ROUTE =
    'przynajmniej jedna z tras linii jest dłuższa niż 50km.';
  RES_LINE_EDITOR_ERROR_ROUTE_NO_PROVINCE_BORDER =
    'Brak punktu drogowego typu "Granica województwa" między przystankami "';
  RES_LINE_EDITOR_PROHIBITED_CHANGE_LINE_TYPE =
    'Zabroniona zmiana typu linii z powodu przypisanych taryf.';
  RES_LINE_EDITOR_LINE_TYPE_SHOULD_BE_INTERNATIONAL =
    'Typ linii powinien być "linia międzynarodowa".';
  RES_LINE_EDITOR_ERROR_ROUTE_ALL_BUSSTOPS_IN_ONE_COUNTRY =
    'Linia międzynarodowa - wszystkie przystanki w trasach linii leżą w jednym państwie.';
  RES_LINE_EDITOR_INFO_MAX_LINE_COUNT_IN_PERIOD =
    'Została osiągnięta maksymalna liczba linii, które można wprowadzić w okresie ';

  RES_LINE_EDITOR_ERROR_ROUTE_START_END_MUST_BUSSTOPS =
    'Początek i koniec trasy muszą być przystankami.';
  RES_LINE_EDITOR_ERROR_ROUTE_MUST_HAVE_TWO_BUSSTOPS =
    'Każda trasa musi zawierać przynajmniej dwa przystanki.';
  RES_LINE_EDITOR_ERROR_ROUTE_NO_POINT_COUNTRY_BORDER =
    'Brak punktu drogowego typu "Granica państwa" między przystankami "';
  RES_LINE_EDITOR_ERROR_ROUTE_TWO_SHARED_BUSSTOPS_IN_THE_SAME_DIRECTION =
    'W każdej trasie linii w tym samym kierunku muszą być co najmniej 2 przystanki wspólne.';
  RES_LINE_EDITOR_ERROR_ROUTE_LINEVARIANT = 'Jest już trasa z numerem wariantu: ';
  RES_LINE_EDITOR_ERROR_ROUTE_LINEVARIANT_WRONG = 'Wariant trasy musi być liczbą w zakresie od 0 do 99';
  //RES_LINE_EDITOR_ERROR_ROUTE_MORE_ONE_LINEVARIANT =
  //  'Jest już więcej niż jedna trasa z z numerem wariantu: ';
  RES_LINE_EDITOR_ERROR_DELETING_BUSSTOP_WILL_BREAK_RIDEROUTES =
    'Usunięcie wybranych przystanków nie jest możliwe, ponieważ te kursy miałyby mniej niż 2 przystanki: %s.';

  RES_LINE_EDITOR_ERROR_OVER_125_POINTS =
    'Uwaga trasa ma ponad 125 przystanków! '+
    'Mogą występować problemy ze sprzedażą biletów na kursach tej trasy '+
    'na niektórych modelach bileterek EMAR-105. Jeśli to możliwe, podziel trasę na krótsze trasy.';


  RES_LINE_EDITOR_CAP_LineNumberFromLine = 'Aktualnie przypisana linia';
  RES_LINE_EDITOR_CAP_DocNumber = 'Numer dokumentu';
  RES_LINE_EDITOR_CAP_DocTypeName = 'Typ dokumentu';
  RES_LINE_EDITOR_CAP_FirstValidFrom = 'Pierwsze ważny od';
  RES_LINE_EDITOR_CAP_ValidFrom = 'Ważny od';
  RES_LINE_EDITOR_CAP_ValidTo = 'Ważny do';
  RES_LINE_EDITOR_CAP_CopyNumber = 'Liczba wypisów';
  RES_LINE_EDITOR_CAP_LineNumber = 'Nr ew. linii';
  RES_LINE_EDITOR_CAP_LineDesc = 'Przebieg linii';
  RES_LINE_EDITOR_CAP_SignNumber = 'Numer sprawy';
  RES_LINE_EDITOR_CAP_ApplicationNumber = 'Numer wniosku';
  RES_LINE_EDITOR_CAP_ApplicationDate = 'Data wniosku';
  RES_LINE_EDITOR_CAP_ApplicationStatus = 'Status sprawy';

  RES_LINE_EDITOR_AND = 'i';
{$endregion}


//  _CAPT_SALE = 'Sprzedaż';

//  _CAPT_ROUTE_PARAMS = 'Parametry';
//  _CAPT_ROUTE_TARIF = 'Przypisanie taryf';
//  _CAPT_ROUTE_TIMETABLE = 'Rozkłady jazdy';
//  _CAPT_ROUTE = 'Trasy';
//  _CAPT_ROUTE_PRINT_TIMETABLE = 'Wydruki RJA';

  _ROAD = 'Drogi';
  _ROADPOINT = 'Punkty drogowe';
  _BUSSTOP = 'Rejestr przystanków';
  _FSDTECHRIDE = 'Jazdy techniczne';
  _FSDCNTRRIDE = 'Zlecenia turystyczne';
  _FSDCNCIRCUIT = 'Obiegi';
  _FSDCNRIDEGROUP = 'Obiegi (grupy kursów)';
  _FSDBUSLINES = 'Linie';
  _RIDEEXPPREF = 'Parametry kursów - eksporty / wydruki';
  _RIDESALEPREF = 'Parametry kursów - sprzedaż';
  _BUSSTANDNAMEPREF = 'Konfiguracja przystanku';
  _REPORTS = 'Raporty';
  _RIDEBASTABLEPREF = 'Parametry kursów - tablice kierunkowe';
  _RIDETYPECOMM = 'Rodzaje komunikacji';
  _RIDECOMNET = 'Sieci komunikacyjne';
  _RIDESERVTYPE = 'Rodzaje kursów';
  _RIDE = 'Kursy';
  _TIMETABLE = 'Rozkłady jazdy';
  _TIMETABLEONE = 'Rozkład jazdy';
  _RJA_TABLE = 'Definicje tabel';
  //_PLATE_PRINT = 'Drukowanie tabliczek';
  _RJA_TABLE_PRINT = 'Drukowanie tabel RJA';
  //_RJA_TABLE_DEF = 'Nag│ˇwki RJA';
  _DRIVER_TICKET_SALE_PREF_SET = 'Parametry sprzedaży przez kierowcę';
  _LINE_FEE_DEFINITION = 'Stawki za wozokilometr';


  CAP_BUSSTOP = 'Przystanek';
  CAP_BUSSTOPS = 'Przystanki';
  CAP_BUSSTOPTYPE = 'Domyślne czasy obsługi';

  CAP_BUSPCGROUP = 'Uprawnienia urządzeń';
  CAP_BUSPCMOBILE = 'Urządzenie';


  RS_MAIN_COMPANY = 'Firma główna';
  RS_DEPARTMENT = 'Oddział';

  { Szablony wiadomości tagi i opis }
  TAG_PRACOWNIK   = '%PRACOWNIK%';
  DESC_PRACOWNIK  = 'Imię i nazwisko zalogowanego pracownika.';

  TAG_M_IMIE      = '%MIESZKANIEC_IMIĘ%';
  DESC_M_IMIE     = 'Imię mieszkańca.';

  TAG_M_NAZW      = '%MIESZKANIEC_NAZWISKO%';
  DESC_M_NAZW     = 'Nazwisko mieszkańca.';

  TAG_LKOB        = '%LISTA_KART_ODBIÓR_START%';
  TAG_LKOE        = '%LISTA_KART_ODBIÓR_KONIEC%';
  DESC_LKO        = 'Lista kart do odbioru. Powtarzany jest tekst mędzy znacznykami.';

  TAG_KO_NUMER    = '%KARTA_ODBIÓR_NUMER%';
  DESC_KO_NUMER   = 'Numer karty.';

  TAG_KO_BARCODE  = '%KARTA_ODBIÓR_KOD_KRESKOWY%';
  DESC_KO_BARCODE = 'Kod kreskowy wydrukowany na karcie.';

  TAG_KO_WAZNADO  = '%KARTA_ODBIÓR_WAŻNA_DO%';
  DESC_KO_WAZNADO = 'Ostatni dzień ważności karty.';

  TAG_LKWB        = '%LISTA_KART_WAŻNOŚĆ_START%';
  TAG_LKWE        = '%LISTA_KART_WAŻNOŚĆ_KONIEC%';
  DESC_LKW        = 'Lista kart nieważnych lub ze zbliżającym się koniec ważności. Powtarzany jest tekst mędzy znacznykami.';

  TAG_KW_NUMER    = '%KARTA_WAŻNOŚĆ_NUMER%';
  DESC_KW_NUMER   = 'Numer karty.';

  TAG_KW_BARCODE  = '%KARTA_WAŻNOŚĆ_KOD_KRESKOWY%';
  DESC_KW_BARCODE = 'Kod kreskowy wydrukowany na karcie.';

  TAG_KW_WAZNADO  = '%KARTA_WAŻNOŚĆ_WAŻNA_DO%';
  DESC_KW_WAZNADO = 'Ostatni dzień ważności karty.';

  TAG_LUB         = '%LISTA_ULG_START%';
  TAG_LUE         = '%LISTA_ULG_KONIEC%';
  DESC_LUB        = 'Lista ulg. Powtarzany jest tekst mędzy znacznykami.';

  TAG_U_NAZWA     = '%ULGA_NAZWA%';
  DESC_U_NAZWA    = 'Nazwa ulgi.';

  TAG_U_WAZNADO   = '%ULGA_WAŻNA_DO%';
  DESC_U_WAZNADO  = 'Ostatni dzień ważności ulgi.';

  HTML_TMP_CardNotFound              = 'Brak przypisanych kart do wybranego mieszkańca.';
  HTML_TMP_ReductionNotFound         = 'Brak przypisanych ulg do wybranego mieszkańca.';
  HTML_TMP_NoCardToDelivery          = 'Brak kart do obioru.';
  HTML_TMP_NoEndingCardValidity      = 'Brak nieważnych kart lub karty ze zbliżającym się końcem ważności.';
  HTML_TMP_NoEndingReductionValidity = 'Brak nieważnych ulg lub ulgi ze zbliżającym się końcem ważności.';

  PAGINATION_RECORDS_COUNT = 'Rekordów: ';

  // paramerty rejestracji
  REGISTER_PARAM_MSG_DIRECTORY_NOT_EXISTS = 'Folder z raportami do rejestracji z dworca i z plików wskazuje nieistniejący folder. Ustaw poprawną ścieżkę w Parametrach rejestracji.'#13#10 +
    'Czy chcesz wybrać plik z wybranego folderu?';
  REGISTER_PARAM_MSG_WRONG_SETTLEMENT = 'Niepoprawny folder do pobierania plików z rozliczarki\wpłatomatu!'#13#10 +
    'Sprawdź ścieżkę "Folder z raportami z bileterek z wybranej rozliczarki\wpłatomatu" w Parametry rejestracji dla wybranej rozliczarki\wpłatomatu.';
  REGISTER_FILES_MSG_EMPTY_FOLDER = 'W folderze "%s" brak plików do zarejestrowania';
  REGISTER_FILES_MSG_EMPTY_FOLDERS = 'W folderach brak plików do zarejestrowania';

  // Emar105, przebieg zadania
//  TASK_REPORT_NUMBER_EMPTY = 'RAPORT ZADANIOWY NUMER: %%TASK_REPORT_NUMBER%%';
  TASK_REPORT_MISSING_EVENT1 = '*Brak zdarzenia identyfikacji bileterki';
  TASK_REPORT_NUMBER = 'RAPORT ZADANIOWY NUMER: %s';
  TASK_REPORT_REG_DATETIME = 'Data rejestracji: %s';
  TASK_REPORT_TASK_COMPANY = 'Firma, w której wykonano zadanie: %d';
  TASK_REPORT_DRIVER_FULLNAME = 'Kierowca: %d %s %s';
  TASK_REPORT_CARD_NUMBER = 'Karta pamięci: %d';
  TASK_REPORT_FILE_NAME = 'Zbiór z rozkładem jazdy: %s';
  TASK_REPORT_TITLES = 'DATA        GODZINA   RODZAJ ZAPISU';
  TASK_REPORT_CODE = 'Szyfr raportu %s';
  TASK_REPORT_FISCAL_CASH = 'Kasa:  %s Program sterujący w wersji 1.%.2d';
  TASK_REPORT_FISCAL_CASH_41 = 'Kasa:  %s';
  TASK_REPORT_FISCAL_CASH_INCORRECT_IDENTIFY_41 = 'Kasa:  %s  numer unikatowy niezgodny z wpisem identyfikacji bileterki';
  TASK_REPORT_NOT_FISCAL_CASH = 'Kasa:  %s  nieufiskalniona Program sterujący w wersji 1.%.2d';
  TASK_REPORT_NOT_FISCAL_CASH_41 = 'Kasa:  %s  nieufiskalniona';
  TASK_REPORT_NOT_FISCAL_CASH_INCORRECT_IDENTIFY_41 = 'Kasa:  %s  nieufiskalniona  numer unikatowy niezgodny z wpisem identyfikacji bileterki';
  TASK_REPORT_WRONG_FISCAL_CODE = '*Brak lub nieprawidłowy numer unikatowy bileterki';
  TASK_REPORT_FISCAL_START_WITH_POWER_OFF = 'Włożenie karty przy wyłączonym zasilaniu';
  TASK_REPORT_FISCAL_START_WITH_POWER_ON = 'Włożenie karty przy włączonym zasilaniu';
  TASK_REPORT_DRIVER_REIDENTEFICATION = 'Ponowna identyfikacja karty kierowcy';
  TASK_REPORT_INCORRECT_FISCAL_RECORD = 'Niepełny wpis identyfikacji bileterki';
  TASK_REPORT_INCORRECT_DATA = '- nieprawidłowe dane';
  TASK_REPORT_RAM_DISRUPTION = 'Prawdopodobne zakłócenie RAM bileterki';
  TASK_REPORT_PAYMENT_METHOD_CHANGE = 'Zmiana sposobu zapłaty';
  TASK_REPORT_DRIVER_LOGOUT = 'Wylogowanie kierowcy';

  TASK_REPORT_CANCEL_REG_DATETIME = 'Data anulowania biletów: %s     Godzina rozpoczęcia raportu: %s';
  TASK_REPORT_CANCEL_CASHIER = 'Kasjer: %d %s';
  TASK_REPORT_CANCEL_A80_NAME = 'Nazwa zbioru z rozkładem jazdy przy sprzedaży biletów: %s';
  TASK_REPORT_CANCEL_TICKET_NUMBER = 'Anulowanie biletu nr %d';
  TASK_REPORT_CANCEL_TICKET_SALE_DATE = 'Sprzedanego %s %s';
  TASK_REPORT_CANCEL_BY_DRIVER = 'przez kierowcę nr %d';
  TASK_REPORT_CANCEL_TICKET_REGISTER = 'bileterka %s';
  TASK_REPORT_CANCEL_FISCAL_REPORT = 'RF %d';
  TASK_REPORT_CANCEL_TICKET_AMOUNTS = 'Wartość biletu: %9f %s  Wartość zwrotu: %9f %s';
  TASK_REPORT_CANCEL_TICKET_AMOUNT_TO_PAY = 'Kwota do zapłaty: %.2f %s Zwrot kwoty do zapłaty: %.2f %s';
  TASK_REPORT_CANCEL_EMCARD_NOT_REGISTERED = 'EM-karta nie została zastrzeżona';
  TASK_REPORT_CANCEL_EMCARD_REGISTATION_DATE = 'EM-karta została zastrzeżona w dniu %s';
  TASK_REPORT_CANCEL_CLOSE_TIME = 'Godzina zamknięcia zadania: %s';
  TASK_REPORT_CANCEL_TICKETS_COUNT = 'Liczba anulowanych biletów: %d';
  TASK_REPORT_CANCEL_TICKETS_AMOUNT = 'Suma wartości anulowanych biletów: %.2f %s';
  TASK_REPORT_CANCEL_TICKETS_RETURN_AMOUNT = 'Suma wartości zwrotu biletów: %.2f %s';
  TASK_REPORT_DISPOSABLE = 'jednorazowy';
  TASK_REPORT_PERIODIC = 'okresowy';
  TASK_REPORT_MONTHLY = 'miesięczny';
  TASK_REPORT_MULTI_PASSAGE = 'wieloprzejazdowy';
  TASK_REPORT_NETWORK = 'sieciowy';
  TASK_REPORT_NORMAL = 'normalny';
  TASK_REPORT_REDUCED = 'ulgowy';
  TASK_REPORT_SCHOOL = 'szkolny';
  TASK_REPORT_LUGGAGE = 'bagażowy';
  TASK_REPORT_WORKER_NORMAL = 'pracowniczy normalny';

  SALES_REPORT_MSG_SAVED = 'Raport został zarejestrowany poprawnie.'; // gdy Status=4
  SALES_REPORTS_MSG_SAVED = '%d raportów zostało zarejestrowanych poprawnie.'; // gdy Status=4
  SALES_REPORT_MSG_SAVED_WITH_ERRORS = 'Raport ma błędy i nie został zarejestrowany poprawnie!'; // gdy Status=1
  SALES_REPORTS_MSG_SAVED_WITH_ERRORS = '%d raportów mają błędy i nie zostały zarejestrowane poprawnie!'; // gdy Status=1
  SALES_REPORT_MSG_DID_NOT_SAVE = 'Raport nie został zarejestrowany.';
  SALES_REPORTS_MSG_DID_NOT_SAVE = '%d raportów nie zostało zarejestrowanych.';
  SALES_REPORTS_MSG_AFTER_BREAK_PRESSED = '%d pozostało do zarejestrowania.';
  SALES_REPORT_MSG_ALREADY_SAVED = 'Raport jest już zarejestrowany: %s';
  SALES_REPORTS_MSG_PASS_FILES = 'Pliki poniżej zostały pominięte przy rejestracji:';
  SALES_REPORT_MSG_EMPTY_CARD_PROGRAMMING = 'Karta nie zawiera danych do rejestracji, potwierdź programowanie karty zbiorem %s';

  SALES_REPORT_CAP_SETTLEMENTS_REGISTRATION = 'Rejestracja rozliczeń';
  SALES_REPORT_CAP_FISCAL_REPORTS = 'Raporty fiskalne';
  SALES_REPORT_CAP_TICKETS = 'Bilety';

  SALES_REPORT_CAP_FR_UNIQUE_NUMBER = 'Nr unikatowy';
  SALES_REPORT_CAP_FR_NUMBER = 'Nr raportu fiskalnego';
  SALES_REPORT_CAP_FR_OPEN_DATE = 'Data otw.';
  SALES_REPORT_CAP_FR_CLOSE_DATE = 'Data zam.';
  SALES_REPORT_CAP_FR_TICKETS_COUNT = 'L. bil.';
  SALES_REPORT_CAP_FR_CLOSED_TICKETS_COUNT = 'L. bil. zam.';
  SALES_REPORT_CAP_FR_BRUTTO = 'Brutto';
  SALES_REPORT_CAP_FR_CLOSED_BRUTTO = 'Brutto zam.';
  SALES_REPORT_CAP_FR_VAT = 'Stawka VAT';
  SALES_REPORT_CAP_FR_VAT_Sum = 'PTU';
  SALES_REPORT_CAP_FR_CLOSED_VAT_Sum = 'PTU zam.';
  SALES_REPORT_CAP_FR_SALES = 'Netto';
  SALES_REPORT_CAP_FR_CLOSED_SALES = 'Netto zam.';
  SALES_REPORT_CAP_FR_CLOSED_DOC_NUMBER = 'Nr dok. zam.';
  SALES_REPORT_CAP_FR_CLOSED_TICKET_NUMBER = 'Nr bil. zam.';
  SALES_REPORT_CAP_FR_LAST_SALE_DATE = 'Data ost. sprz.';
  SALES_REPORT_CAP_FR_LAST_TICKET_NUMBER = 'Nr ost. bil.';

  SALES_REPORT_CAP_TICKETS_SALE_DATETIME = 'Data i godz. sprz.';
  SALES_REPORT_CAP_TICKETS_SALE_DATE = 'Data sprz.';
  SALES_REPORT_CAP_TICKETS_SALE_TIME = 'Godz. sprz.';
  SALES_REPORT_CAP_TICKETS_SALE_YEAR = 'Rok';
  SALES_REPORT_CAP_TICKETS_SALE_MONTH = 'Miesiąc';

  SALES_REPORT_CAP_TICKETS_OWNER_COMPANY = 'Fir. przew.';
  SALES_REPORT_CAP_TICKETS_RIDE_COMPANY = 'Fir. kursu';
  SALES_REPORT_CAP_TICKETS_RIDE_COMPANY_NAME = 'Nazwa przew.';
  SALES_REPORT_CAP_TICKETS_SALE_COMPANY = 'Fir. sprz.';
  SALES_REPORT_CAP_TICKETS_SALE_COMPANY_NAME = 'Nazwa sprz.';
  SALES_REPORT_CAP_TICKETS_GOV_COMPANY_NAME = 'Nazwa organizatora';
	SALES_REPORT_CAP_TICKETS_GOV_COMPANY = 'Org. przew.';

  SALES_REPORT_CAP_TICKETS_RIDE = 'Kurs';
  SALES_REPORT_CAP_TICKETS_RIDE_NUMBER_VARIANT_VALIDFROM = 'Numer kursu/wariant kursu/ważny od';
  SALES_REPORT_CAP_TICKETS_RIDE_VARIANT = 'Wariant kursu';
  SALES_REPORT_CAP_TICKETS_RIDE_VALID_FROM = 'Kurs ważny od';
  SALES_REPORT_CAP_TICKETS_START_TIME = 'G. odj.';
  SALES_REPORT_CAP_TICKETS_START_TIME_RIDE = 'G. rozp. kursu';
  SALES_REPORT_CAP_TICKETS_START_TIME_BUSSTOP = 'G. odj. od przystanku';
  SALES_REPORT_CAP_TICKETS_STOP_TIME =  'G. prz.';
  SALES_REPORT_CAP_TICKETS_START_BUSSTOP = 'Od przystanku';
  SALES_REPORT_CAP_TICKETS_END_BUSSTOP = 'Do przystanku';
  SALES_REPORT_CAP_TICKETS_START_BUSSTOP_CODE = 'Kod przyst od';
  SALES_REPORT_CAP_TICKETS_END_BUSSTOP_CODE = 'Kod przyst do';
  SALES_REPORT_CAP_RECEIPT = 'Artykuł';

  SALES_REPORT_CAP_TICKETS_PASSANGERS_COUNT = 'L. pas. / ilość';
  SALES_REPORT_CAP_TICKETS_BUYER_NIP = 'NIP Nabywcy';
  SALES_REPORT_CAP_TICKETS_PRICE_SUM = 'Wartość';

  SALES_REPORT_CAP_TICKETS_PRICE_SUM_CASH = 'W tym gotówka';
  SALES_REPORT_CAP_TICKETS_PRICE_SUM_NO_CASH = 'W tym bezgotówkowo';

  SALES_REPORT_CAP_TICKETS_PRICE_SUM_ONE = 'Wartość 1 bil.';
  SALES_REPORT_CAP_TICKETS_AMOUNT_TO_PAY = 'Do zapł.';
  SALES_REPORT_CAP_TICKETS_ROAD_DISTANCE = 'Odl.';
  SALES_REPORT_CAP_TICKETS_TICKET_TYPE = 'Typ bil.';
  SALES_REPORT_CAP_TICKETS_TICKET_GENRE = 'Rodz. bil.';
  SALES_REPORT_CAP_TICKETS_PAYMENT_TYPE = 'Rodzaj płatności';
  SALES_REPORT_CAP_TICKETS_EP_CONTROL_CODE = 'Kod biletu EP';
  SALES_REPORT_CAP_TICKETS_EP_NUMBER = 'Numer biletu EP';
  SALES_REPORT_CAP_TICKETS_BEFORE_CHANGE_EP_CONTROL_CODE = 'Bilet przed przes.';
  SALES_REPORT_CAP_TICKETS_AFTER_CHANGE_EP_CONTROL_CODE = 'Bilet po przes.';
  SALES_REPORT_CAP_TICKETS_MONTH_TICKET_TYPE = 'Rodz. BM';
  SALES_REPORT_CAP_TICKETS_FARE_PRICE_REDUCTION_TYPE = 'Typ ulgi';
  SALES_REPORT_CAP_TICKETS_FARE_PRICE_REDUCTION_NAME = 'Uprawnienie';
  SALES_REPORT_CAP_TICKETS_FARE_PRICE_REDUCTION_PERCENTAGE = 'Zniżka %';
  SALES_REPORT_CAP_TICKETS_FARE_PRICE_REDUCTION_REFUND = 'Dopłata';
  SALES_REPORT_CAP_TICKETS_FARE_PRICE_REDUCTION_VALUE = 'Kwota dop.';
  SALES_REPORT_CAP_TICKETS_RIDE_TYPE_COMMUNICATION = 'Rodzaj komunikacji';
  SALES_REPORT_CAP_TICKETS_IS_LINE_FOREIGN = 'Zagr.';

  SALES_REPORT_CAP_TICKETS_LINE_NUMBER = 'Numer linii';
  SALES_REPORT_CAP_TICKETS_LINE_NUMBER_AND_VALIDFROM = 'Numer linii/ważna od';
  SALES_REPORT_CAP_TICKETS_LINE_VARIANT = 'Wariant linii';
  SALES_REPORT_CAP_TICKETS_LINE_NAME = 'Nazwa linii';

  SALES_REPORT_CAP_TICKETS_LINE2 = 'Linia po przes.';
  SALES_REPORT_CAP_TICKETS_LINE_VARIANT2 = 'War po przes.';
  SALES_REPORT_CAP_TICKETS_LINE_NAME2 = 'Nazwa linii po przesiadce';

  SALES_REPORT_CAP_TICKETS_FISCAL_LOGO = 'Bileterka';
  SALES_REPORT_CAP_TICKETS_FISCAL_REPORT = 'Numer RF';
  SALES_REPORT_CAP_TICKETS_SALES_REPORTNUMBER = 'Nr RZ';
  SALES_REPORT_CAP_TICKETS_SALES_REPORTTYPE = 'Typ RZ';
  SALES_REPORT_CAP_TICKETS_SALES_REPORTDATE = 'Data rej. RZ';

  SALES_REPORT_CAP_TICKETS_DOC_NUMBER = 'Nr dok.';
  SALES_REPORT_CAP_TICKETS_TICKET_ORDER = 'Nr k.bil.';
  SALES_REPORT_CAP_TICKETS_TICKET_NUMBER = 'Nr biletu';
  SALES_REPORT_CAP_TICKETS_CARD_NUMBER = 'Nr karty';
  SALES_REPORT_CAP_TICKETS_VALID_FROM = 'Bilet ważny od';
  SALES_REPORT_CAP_TICKETS_VALID_TO   = 'Bilet ważny do';

  SALES_REPORT_CAP_TICKETS_VatAmount1 = 'St.Ptu1';
  SALES_REPORT_CAP_TICKETS_PTU1       = 'Kw.Ptu1';
  SALES_REPORT_CAP_TICKETS_Netto1     = 'Netto1';

  SALES_REPORT_CAP_TICKETS_VatAmount2 = 'St.Ptu2';
  SALES_REPORT_CAP_TICKETS_PTU2       = 'Kw.Ptu2';
  SALES_REPORT_CAP_TICKETS_Netto2     = 'Netto2';
  SALES_REPORT_CAP_TICKETS_CURRENCY_NAME = 'Waluta';
  SALES_REPORT_CAP_TICKETS_SELLER_NAME = 'Kierowca / kasjer';


  SALES_REPORT_MSG_ROUTE_NOT_EXISTS = 'Dla firmy "%s" kurs %d (wariant %s, ważny od %s) nie został znaleziony';
  SALES_REPORT_MSG_COMPANY_OF_ROUTE_NOT_EXISTS = 'Brak przewoźnika o numerze: %d';
  SALES_REPORT_MSG_TAX_NOT_EXISTS = 'Stawka VAT (index=%d) nie została znaleziona';
  SALES_REPORT_MSG_FARE_PRICE_REDUCTION_NOT_EXISTS = 'Ulga "%s" (z kodem %d) nie została znaleziona';
  SALES_REPORT_MSG_COMPANY_NOT_EXISTS = 'Firma z kodem %d nie została znaleziona';
  SALES_REPORT_MSG_FIRSTTICKET_NOT_EXISTS = 'Ostatni bilet sprzedany na EM-Kartę %u albo wzór biletu nie został znaleziony';
  SALES_REPORT_MSG_PROLONGEDTICKET_NOT_EXISTS = 'Przedłużony bilet na EM-Kartę %u nie został znaleziony';
  SALES_REPORT_MSG_REDUCTION_NOT_EXISTS = 'Zniżka z kodem %d nie została znaleziona';
  SALES_REPORT_MSG_EMCARD_NOT_SAVED = 'Nowa karta %d nie została zapisana';
  SALES_REPORT_MSG_TICKETREGISTER_NOT_REGISTERED = 'Bileterka %s nie jest zarejestrowana';
  SALES_REPORT_MSG_TICKETREGISTER_NOT_FISCAL = 'Bileterka %s nie jest ufiskalniona';
  SALES_REPORT_MSG_TICKETREGISTER_OUT_OF_MAXVALUE = 'Bileterka %s nie została dodana. Została osiągnięta maksymalna liczba bileterek z licencji.';
  SALES_REPORT_MSG_TICKETREGISTER_NOT_SAVED = 'Bileterka %s nie została dodana.';
  SALES_REPORT_MSG_TICKETREGISTERCARD_NOT_PROGRAMMED = 'Karta pamięci %s nie została zaprogramowana.';
  SALES_REPORT_MSG_TICKETREGISTER_IS_NOT_IN_USE = 'Bileterka %s nie jest używana.';
  SALES_REPORT_MSG_TICKETREGISTER_IS_SCRAPPED = 'Bileterka %s jest zezłomowana.';
  SALES_REPORT_MSG_TICKETREGISTER_IS_BLANK = 'Puste logo bileterki.';
  SALES_REPORT_MSG_EMCARD_TICKET_PROLONGING = 'Brak wpisu w liście EM kart do przedłużenia w autobusie.'#13#10'Karta nr: %d;'#13#10'Bilet nr: %s;'#13#10'Liczba okresów przedłużenia ważności biletu: %d';
  SALES_REPORT_MSG_REPLACED_REPORT_WITH_ERROR_ON_SERVER = 'Raport %s czeka na zarejestrowanie na liście automatycznej rejestracji. Raport został podmieniony.';

  SALES_REPORT_MSG_BUSPC_NOT_REGISTERED = 'Komputer Pokładowy %s nie jest zarejestrowany';
  SALES_REPORT_MSG_BUSPC_OUT_OF_MAXVALUE = 'Komputer Pokładowy %s nie został dodany. Została osiągnięta maksymalna liczba Komputerów Pokładowych z licencji.';
  SALES_REPORT_MSG_BUSPC_NOT_SAVED = 'Komputer Pokładowy %s nie został dodany.';

  REGISTRATION_PARAMS_LAST_FILE_GENERATED = 'Ostatnio przygotowane';
  REGISTRATION_PARAMS_FILE_IN_PREPARATION = 'W trakcie przygotowania';
  REGISTRATION_PARAMS_SETTLMENT           = 'Wpłatomat';
  REGISTRATION_PARAMS_CASHDEPOSIT         = 'Rozliczarka';
  REGISTRATION_PARAMS_SELECT_FOLDER       = 'Wybierz katalog';
  REGISTRATION_PARAMS_ERR_EMPTY_FOLDER    = 'Folder|Pole nie może być puste|0';
  REGISTRATION_PARAMS_ERR_COLLECTION      = 'Data ważności zbioru już minęła';
  REGISTRATION_PARAMS_NOT_MORE_THAN_FMT   = 'Wprowadzona wartość pola nie może być większa od %d.';
  REGISTRATION_PARAMS_NOT_LESS_THAN_FMT   = 'Wprowadzona wartość pola nie może być mniejsza od %d.';
  REGISTRATION_FILE_READ_MESSAGE          = 'Odczyt danych do rejestracji z pliku %s (%d / %d).';
  REGISTRATION_FILE_WRITE_MESSAGE         = 'Zapis danych do rejestracji z pliku %s (%d / %d).';
  REGISTRATION_FILE_UPDATE_MESSAGE        = 'Odnawianie danych w pliku po rejestracji %s (%d / %d).';
  REGISTRATION_FILE_ZIPPING_MESSAGE       = 'Pakowanie raportu do wysyłania.';
  REGISTRATION_FILE_SENDING_MESSAGE       = 'Wysyłanie raportu na serwer zdalny.';
  REGISTRATION_FILE_SENDING_ERROR         = 'Wystąpił błąd pod czas wysyłania raportu na serwer zdalny';
  REGISTRATION_FILE_SENT_MESSAGE          = 'Raport został wysłany na serwer zdalny.';
  REGISTRATION_FILES_ZIPPING_MESSAGE      = 'Pakowanie raportów do wysyłania.';
  REGISTRATION_FILES_SENDING_MESSAGE      = 'Wysyłanie raportów na serwer zdalny.';
  REGISTRATION_FILES_SENDING_ERROR        = 'Wystąpił błąd pod czas wysyłania raportów na serwer zdalny';
  REGISTRATION_FILES_SENT_MESSAGE         = 'Raporty zostały wysłane na serwer zdalny.';

  REGISTRATION_CARD_READ_MESSAGE        = 'Odczyt danych do rejestracji z karty.';
  REGISTRATION_CARD_WRITE_MESSAGE       = 'Zapis danych do rejestracji z karty.';
  REGISTRATION_CARD_PROGRAMMING_MESSAGE = 'Programowanie karty.';
  REGISTRATION_CARD_WRITE_TAKINGS_MESSAGE = 'Wprowadzanie wpłaty.';

  SALES_REPORT_CAP_DOWNLOAD_FILE_C = 'Pobierz plik raportu na dysk lokalny';
  SALES_REPORT_CAP_SEND_FILE_C = 'Wyślij plik raportu do Informica';
  SALES_REPORT_CAP_CREATE_FILE_DD = 'Zapisz plik danych dodatkowych do bileterki EMAR-105/205 i wyślij do rozliczarek/wpłatomatów';
  SALES_REPORT_CAP_SAVE_FILES_BA = 'Zapisz plik z informacją o biletach okresowych sprzedanych/przedłużonych w autobusie dla Dworca (BA)';
  SALES_REPORT_CAP_LOAD_FILES_BA = 'Zapisz pliki generowane automatycznie z informacją o biletach okresowych sprzedanych/przedłużonych w autobusie dla Dworca (BA)';
  SALES_REPORT_CAP_SAVE_FILES_NA = 'Zapisz plik z nieprzedłużonymi/niesprzedanymi biletami na następny okres w autobusie dla Dworca (NA)';
  SALES_REPORT_CAP_SAVE_FILES_DRIVER_BALANCES = 'Zapisz plik sald kierowców do wpłatomatów';
  SALES_REPORT_CAP_CHANGE_DRIVER_OR_CASHIER = 'Zmiana kierowcy/kasjera';
  SALES_REPORT_CAP_DELETE_ERROR_FILE = 'Przenieś raport do listy raportów, oczekujących na rejestrację';
  SALES_REPORT_CAP_EXTEND_NR = 'Nr przedłużenia';
  SALES_REPORT_CAP_PRICE = 'Cena';
  SALES_REPORT_CAP_NEXT_VALIDITY_DATE  = 'Następny okres ważności';
  SALES_REPORT_CAP_PATTERN_TICKET = 'Bilety sprzed. na EM-Kartę w autobusie czekające na rejestrację-brak bil. wz.';
  SALES_REPORT_CAP_EMCARDS_RIDES_WAITING = 'Przejazdy na EM-Kartę czekające na rejestrację - brak bil. wz.';
  SALES_REPORT_CAP_TASK_REPORTS_OF_SELECTION = 'Drukuj Raport zadaniowy.';
  SALES_REPORT_CAP_PRINT_TICKET_DUPLICATE = 'Drukuj duplikat biletu.';
  SALES_REPORT_CAP_TICKET_REGISTERS_LIFE = 'Pozostała liczba raportów bileterek';

  SALES_REPORT_CAP_TICKET_CHANGE_PAYMENTTYPE = 'Zmiana rodzaju płatności';
  SALES_REPORT_CAP_TICKET_ONE_CHANGE_PAYMENTTYPE = 'zmień dla wybranego biletu';
  SALES_REPORT_CAP_TICKET_MULTI_CHANGE_PAYMENTTYPE = 'zmiana dla wielu biletów';

  RS_Emar105BlockClear = 'Kasowanie bloku %d';
  RS_Emar105PageClear = 'Kasowanie strony %d';
  RS_Emar105PageWrite = 'Zapis strony %d';
  RS_Emar105PageRead = 'Odczyt strony %d';
  RS_Emar105Prepare101Record = 'Zapisywanie stawek VAT';
  RS_Emar105PrepareOIK = 'Przygotowanie OIK';
  RS_Emar105ChangeOIKStatuses = 'Zapisywanie statusów OIK';
  RS_Emar105SetOIKReadBy = 'Zapisywanie daty odczytu raportu z karty pamięci';
  RS_Emar105PrepareAddData = 'Przygotowanie danych dodatkowych';
  RS_Emar105OIKReaded = 'Sprawdzanie stanu karty i kierowcy';
  RS_Emar105ChoiceDriver = 'Wybierz kierowcę';
  RS_SalesReportRegistry = 'Rejestracja nowego rozliczenia';
  RS_TicketRegisterCardRegistry = 'Rejestracja karty pamięci';
  RS_Emar105DeviceSaveError = 'Błąd odczytu karty.';
  RS_Emar105DeviceSaveCardServerError = 'Błąd przesyłania obrazu karty pamięci na serwer.';
  RS_Emar105NewCardHasReportError = 'Karta nr %s zawiera raport do rozliczenia.'#13#10'Proszę rozliczyć kartę pamięci.';
  RS_Emar105RegistrationCardScrapDateError = 'Karta nr %u jest zezłomowana.';
  RS_Emar105RegistrationCardBlockedError = 'Karta nr %u jest zablokowana.';
  RS_Emar105RegistrationCardError = 'Karta nr %u nie jest zarejestrowana.';
  RS_Emar105RegistrationCardErrorAndCopy = 'Karta nr %u nie jest zarejestrowana.'#13#10 +
    'Jej zawartość zostanie zapisana do pliku %s.'#13#10'Raport w karcie został skasowany.';
  RS_Emar105CardHasNotDriverError = 'Karta pamięci nr %s nie ma przypisanego kierowce.';
  RS_Emar105CardDeletedDriverError = 'Kierowca przypisany do karty pamięci nr %s jest usunięty.';
  RS_Emar105CardIsNotInDeviceError = 'Brak karty pamięci.';
  RS_Emar105CardReaderNotFoundError = 'Brak czytnika karty pamięci.';
  RS_Emar105CardIsNotOpenError = 'Nieudana próba otwarcia czytnika karty pamięci.';
  RS_Emar105CardReaderIsBusyError = 'Czytnik karty pamięci jest zajęty';
  RS_Emar105CardReaderOpenUnexpectError = 'Dostęp do czytnika karty pamięci - niespodziewany błąd.';
  RS_Emar105CardIsNotReadyForProgramming = 'Karta pamięci nie gotowa do pracy.';
  RS_Emar105RegistrationCardReportError = 'Karta pamięci nr %u nie zawiera danych do rejestracji.'#13#10 +
    'Jej zawartość została zapisana do pliku %s.';
  RS_Emar105RegistrationWFileHasError = 'Plik %s zawiera informację o błędzie do wydruku – wpłata zabroniona';
  RS_Emar105RegistrationCardReadAndProgrammed =
    'Zawartość karty pamięci nr %u została odczytana, a karta zaprogramowana i jest gotowa do dalszej pracy.';
  RS_Emar105RegistrationCardReadAndProgrammedAndSend =
    'Zawartość karty pamięci nr %u została odczytana, a karta zaprogramowana i jest gotowa do dalszej pracy.'#13#10#13#10 +
    'Kierowca:'#13#10 +
      '%30s %s'#13#10#13#10 +
    'Saldo kierowcy przed rozliczanym RZ:'#13#10 +
      '%90.2f zł.'#13#10 +
    'Utarg gotówkowy w raporcie kierowcy wynosi:'#13#10 +
      '%90.2f zł.'#13#10 +
    'Saldo kierowcy po rozliczeniu RZ:'#13#10 +
      '%90.2f zł.';
  RS_Emar105RegistrationCardReadAndReProgrammed =
    'Karta pamięci nr %u nie była gotowa do pracy.'#13#10 +
    'Mimo to, zawartość karty została odczytana, a karta zaprogramowana i jest gotowa do dalszej pracy.';
//  RS_Emar105RegistrationCardReadAndProgrammed_ChangedPaymentType = '(UWAGA! W raporcie są zmiany sposobu płatności!)';
  RS_Emar105RegistrationDriverSelectionError = 'Kierowca nie został wybrany.';
  RS_Emar105MissingRegistrationFileError = 'Brak informacji o zbiorze z rozkładem jazdy (A80) w raporcie zadaniowym.'#13#10 +
    'Raport należałoby naprawić.';
  RS_Emar105RegistrationFileALoadingError = 'Błąd odczytu pliku z rozkładem jazdy - %s';
  RS_Emar105RegistrationFileANotExistsError = 'Brak pliku z rozkładem jazdy - %s';
  RS_Emar105ReportIsAlreadyRegistered = 'Zbiór %s z danymi z karty pamięci nr %u '#13#10 +
    'zawiera raport rejestrowany %s na stanowisku %s. Numer RZ: %s';
  RS_Emar205ReportOnlineIsAlreadyRegistered = 'Zbiór %s zawiera raport rejestrowany %s na stanowisku %s. Numer RZ: %s';
  RS_Emar105ReportQuestionToBeRegisteredNewTickets = 'Dorejestrować brakujące bilety (%d)?';
  RS_ReportIsAlreadyRegistered = 'Zbiór %s zawiera raport rejestrowany %s na stanowisku %s. Numer RZ: %s';
  RS_ReportIsDifferentThanRegistered = 'Zbiór %s identyfikowany przez algorytm porównawczy jako odmienny od raportu %s zarejestrowanego na stanowisku %s. Numer RZ: %s';
  RS_Emar105ReportIsEmpty = 'Zbiór %s z danymi z karty pamięci nr %u nie zawiera raportu do rejestracji%s';
  RS_Emar105FileDeleted = '; zbiór usunięto';
  RS_Emar105ReportCopyFolderIsSource = 'Folder, z którego raport jest odczytywany: %s'#13#10 +
        'jest jednocześnie folderem do zapisu kopii raportów.'#13#10 +
        'Plik z raportem po rejestracji nie zostanie skasowany.';
  RS_Emar105NotFoundA80 = 'Brak domyślnego zbioru do programowania kart pamięci do bileterek.'#13#10'Proszę przygotować zbiór z rozkładem jazdy.';
  RS_Emar105ReplacedCardDuringProgramming = 'Zmiana karty pamięci podczas programowania (z %s na %s).';
  RS_SalesReportIsBroken = 'Raport z pliku %s jest błędny, usuń go lub zamień na poprawiony.';
  RS_SEARCH_HELP = 'Szukanie we wskazanej kolumnie.'#13#10+
    'WYBÓR KOLUMNY:'#13#10+
    '- kliknąć w dowolne pole z danymi.'#13#10+
    'DODATKOWE OPCJE:'#13#10+
    '- szukanie dokładne: wartość poprzedzona znakiem "="'#13#10+
    '- szukanie wartości mniejszych: wartość poprzedzona znakiem "<"'#13#10 +
    '- szukanie wartości większych: wartość poprzedzona znakiem ">"';
  RS_SEARCH_HELP_ADD = #13#10'- szukanie wartości zaczynające się z: wartość poprzedzona znakiem "*"';
  RS_Emar105_ADDED_EVENT0 = 'Zostało dodane zdarzenie "Szyfr raportu"';

  RS_DUO_IGNORED_LINE =
     'Wszystkie kursy linii numer %s (ważna od %s) zostały pominięte! '
    +'Linie z literami w numerze są zapisywane do zbioru od wersji 10.';
  RS_ERR_NEWER_REPORT_VERSION = 'Raport jest w nowszej wersji niż obsługiwany przez program. Zaktualizuj program!';
  RS_ERR_NO_S_SECTION = 'Błąd: brak podsumowania sprzedaży kasjera!'#13#10'Raport %s nie jest zakończony - należy go odtworzyć w programie BM.';
  RS_ERR_CARD_FILE_FOLDER_DOESNT_EXIST = 'Folder do zapisywania raportów z karty pamięci nie jest zdefiniowany lub nie istnieje!';
  RS_FMT_ERR_CARD_FILE_MORE_THAN_99 = 'Nastąpiło przekręcanie ilości plików dla karty pamięci %d w dniu %s-%s-%s';
  RS_FMT_ERR_CARD_FILE_EXISTS = 'Raport "%s" z karty pamięci już został odczytany.'#13#10'Należy go przesłać na serwer do rejestracji. Po czym ponownie odczytać zawartość karty pamięci.';
  RS_FMT_PROCESSTASKS_REPORT_WAIT_TO_REGISTER_ON_SERVER = 'Raport %s czeka na rejestrację na serwerze (automatyczna rejestracja)...';
  RS_FMT_TASKS_REPORT_WAIT_TO_REGISTER_ON_SERVER = 'Rejestracja raportu %s (automatyczna rejestracja) nie została dokończona';

{$REGION 'from the SalesReport.Utils unit'}
  __rsUnrecVATCode = 'VATCodeToIndex: Unrecognized the VAT code "%s" (not found in the VAT table codes)!';
  __rsUnrecVATIndex = 'VATIndexToChar: Unrecognized the VAT index "%d" (not found in the VAT table codes)!';
  __rsEvt01State_ZlyZegar = 'zły zegar';
  __rsEvt01State_ZlyTotalizer = 'zły totalizer';
  __rsEvt01State_NoErrors = 'nie ma błędów';
  __rsEvt01mcsUnfiscaled = 'nieufiskalniona';
  __rsEvt01mcsReseted = 'jest zerowanie';
  __rsEvt01mcsNoReseted = 'nie było zerowania';
  __rsRtcvNormal = 'Zwykła';
  __rsRtcvAccelerated = 'Przyspieszona';
  __rsRtcvHasty = 'Pospieszna';
  __rsRtcvExpress = 'Ekspresowa';
  __rsRtcvCity = 'Miejska';
  __rsRtcvInternational = 'Międzynarodowa';
  __rsRtcvRemained = 'Pozostała';

  __rsEvt01srfOpen = 'otwarty';
  __rsEvt01srfClose = 'zamknięty';
  __rsEvt01srfUnknown = '?';

  __rsEvt01opPower = 'Zasilanie';
  __rsEvt01opPowerAndInsertCard = 'Karta włożona przy włączonym zasilaniu';
  __rsEvt01opCardInit = 'Inicjacja karty';
  __rsEvt01opUnknwown = '?';
{$ENDREGION}

{$REGION 'from the SalesReport.Classes unit'}
  C_W_FILE_SEC_ZBIOR = 'ZBIÓR: ';
  C_W_FILE_SEC_NRKARTY = 'NUMER KARTY: ';
  C_W_FILE_SEC_NRKIER = 'NUMER KIEROWCY: ';
  C_W_FILE_SEC_BILETY = 'BILETY: ';
  C_W_FILE_SEC_UTARG = 'UTARG: ';
  C_W_FILE_SEC_WPLATA = 'WPŁATA: ';
  C_W_FILE_SEC_BANKNOTY = 'BANKNOTY:';
  C_W_FILE_SEC_MONETY = 'MONETY:';
  C_W_FILE_SEC_DATA = 'DGW: ';
  C_W_FILE_SEC_IMIE = 'IMIĘ: ';
  C_W_FILE_SEC_NAZWISKO = 'NAZWISKO: ';
  C_W_FILE_SEC_RZ = 'RAPORT ZADANIOWY';
  C_W_FILE_SEC_BRAK =  'BRAK RAPORTU';
  C_W_FILE_SEC_ERROR = 'BŁĄD';

  C_TXT_REPORT = 'Raport';
  C_TXT_NON_FISCAL = 'nieufiskalniona';
  C_TXT_COURSE_IS_NOT_RECORDED = '*Brak wpisu wyboru kursu';
  C_TXT_PERIODIC_COMMA = 'Okresowy,';
  C_TXT_PERIODIC_REDUCTION_COMMA = 'Okresowy ulgowy,';
  C_TXT_MONTHLY_COMMA = 'Miesięczny,';
  C_TXT_MONTHLY_SCHOOL_COMMA = 'Miesięczny szkolny,';
  C_TXT_REDUCED_COMMA = 'ulgowy,';
  C_TXT_LABOR_COMMA = 'pracowniczy,';
  C_FMT_EM_CARD_TICKER_MULTIPLE_COLON = 'Wieloprzejazdowy - liczba przejazdów: %d,';
  C_TXT_NETWORK = 'Sieciowy';
  C_TXT_EM_CARD_TICKET_TYPE_COURSE = ' na kurs';
  C_TXT_EM_CARD_TICKET_TYPE_RELATION = ' na relację';
  C_TXT_EM_CARD_TICKET_TYPE_HOURS_INTERVAL = ' na przedział godzin';
  C_TXT_EM_CARD_TICKET_OVERFLOW_RIDES = 'EM-karta ma wpisaną za dużą liczbę przejazdów';
  C_FMT_EM_CARD_TICKET_ROUTE_AND_RELATIONSHIP = 'Trasa nr: %d, Relacja biletu: ';
  C_TXT_ONE_WAY = 'TAM';
  C_TXT_ONE_WAY_CHANGE_TRAIN = 'TAM po przesiadce';
  C_TXT_RETURN = 'POWRÓT';
  C_TXT_RETURN_CHANGE_TRAIN = 'POWRÓT po przesiadce';
  C_FMT_EM_CARD_TICKET_RIDES_TO_USE_COUNT = 'Liczba przejazdów do wykorzystania .: %d';
  C_TXT_REDUCTION = 'Ulga';
  C_TXT_REDUCTION_STATUTORY = 'Ulga ustawowa ';
  C_TXT_REDUCTION_TRADE = 'Ulga handlowa ';
  C_TXT_TICKET_LABOR = 'Bilet pracowniczy ';
  C_FMT_DOCUMENT_NUMBER = ' Numer dokumentu: %s';
  C_TXT_DASH_VALID_ALWAYS = ' - ważny bezterminowo';
  C_FMT_DASH_VALID_TO = ' - ważny do %s';
  C_FMT_EM_CARD_TICKET_PAY_DATE_USHERETTE_PRICE = 'Data sprzedaży: %s  Bileterka: %s  Cena: %.2f';
  C_TXT_INCORRECT_BUSSTOP_INDEX = ' *nieprawidłowy indeks przystanku w tablicy Ap';
  C_TXT_INCORRECT_EM_CARD_NUMBER = 'Błędny numer EM-karty';
  C_FMT_EM_CARD_NUMBER = 'EM-karta nr: %u';
  C_TXT_EM_CARD_PARTIALLY_READ_DATA = 'Dane odczytane z EM-Karty są niepełne - odczyt został pominięty';
  C_TXT_EM_CARD_INCORRECT_READ_DATA = 'Dane odczytane z EM-Karty są nieprawidłowe - odczyt został pominięty';
  C_FMT_INCORRECT_USHERETTE_UNIGUE_NUMBER = ' *Nieprawidłowy numer unikatowy bileterki: %s';
  C_TXT_INCORRECT_PROCESS_TASKS_RECORD = '*Niezidentyfikowany wpis w raporcie z przebiegu pracy';
  C_TXT_NONE_USHERETTE_IDENTYFICATION = '*Brak identyfikacji bileterki, automatyczna korekta niemożliwa';
  C_TXT_PARTIALLY_USHERETTE_IDENTYFICATION_WRITE = 'Niepełny wpis identyfikacji bileterki';
  C_TXT_DASH_INCORRECT_DATA = '- nieprawidłowe dane';
  C_TXT_USHERETTE_RAM_DISRUPTION = 'Prawdopodobne zakłócenie RAM bileterki';
  C_TXT_CORRECTION_NONE_USHERETTE_IDENTYFICATION = 'korekta braku identyfikacji bileterki';
  C_TXT_FISCAL_REPORT_NUMBER = 'raport fiskalny nr:';
  C_TXT_OPENED = 'otwarty';
  C_TXT_LAST_FISCAL_REPORT_NUMBER = 'ostatni raport fiskalny nr:';
  C_TXT_CLOSED = 'zamknięty';
  C_TXT_CLOSED_NON_FISCAL_REPORT = 'zamknięty raport niefiskalny';
  C_TXT_DASH_INCORRECT_FISCAL_REPORT_DATE = '- nieprawidłowa data raportu fiskalnego';
  C_TXT_FISCAL_REPORT_CLOSING_INCORRECT_VALUES = 'Nieprawidłowe wartości zamknięcia raportu fiskalnego';
  C_TXT_INCORRECT_VALUE_USHERETTE_IDENTYFICATION_WRITING = 'Nieprawidłowe dane wpisu identyfikacji bileterki';
  C_TXT_RAM_ZEROING_NUMBER = 'wystąpiło zerowanie RAM nr:';
  C_TXT_RAM_ZEROING_WITHOUT_SALE = 'zerowanie bez sprzedaży';
  C_TXT_LAST_DOCUMENT_NUMBER_FULL = 'numer ostatniego dokumentu:';
  C_TXT_LAST_TICKET_NUMBER = 'numer ostatniego biletu:';
  C_FMT_FIRST_BILL_DATETIME = 'rozpoczęcie sprzedaży: %s  %s';
  C_FMT_LAST_BILL_DATETIME = 'zakończenie sprzedaży: %s  %s';
  C_TXT_NET_TAX_GROSS_HEADER = 'NETTO       PTU    BRUTTO';
  C_TXT_RATE = 'STAWKA';
  C_TXT_TOTAL_TICKETS_COUNT = 'ogółem - liczba biletów:';
  C_TXT_VALUE = 'wartość:';
  C_TXT_FISCAL_REPORT_CONTROL_NUMBER = 'Numer kontrolny raportu fiskalnego: ';
  C_FMT_CADASTRAL_CURRENCY_WRITE_DATE_CURRENCY = 'Waluta ewidencyjna: %s  Zapis waluty: %s';
  C_FMT_BUS_SIDE_NUMBER_WRITING = 'Wpisany numer boczny autobusu: %s';
  C_TXT_CASH_DESK = 'Kasa:';
  C_TXT_NUMBER = 'nr:';
  C_TXT_TICKETS_HEADER_TEXT_CHANGING = 'Zmiana tekstu nagłówka biletów';
  C_TXT_TICKETS_FOOTER_TEXT_CHANGING = 'Zmiana tekstu stopki biletów';
  C_TXT_FIRED = 'zwolniona';
  C_TXT_USHERETTE_FISCALIZATION = 'UFISKALNIENIE BILETERKI';
  C_FMR_RAM_ZEROING_NUMBER = 'ZEROWANIE RAM BILETERKI - numer zerowania: %d';
  C_TXT_NO_OPENING_FISCAL_REPORT = '*Brak otwarcia raportu fiskalnego';
  C_TXT_FISCAL_REPORT = 'Raport fiskalny';
  C_TXT_PARTIALLY_FISCAL_REPORT_CLOSING_WRITE = 'Niepełny wpis zamknięcia raportu fiskalnego';
  C_TXT_ZEROING_FISCAL_REPORT_INCORRECT_VALUES = 'Wyzerowano nieprawidłowe wartości zamknięcia raportu fiskalnego';
  C_FMT_CANCELED_TICKETS_PRICES_ERRORS = 'Anulowano błędy niezgodności cen biletów od początku dnia %s';
  C_FMT_COURSE_DOCUMENT_BILET = 'szyfr kursu: %s   nr ost. dokumentu:  %s   nr ost. biletu:  %s';
  C_TXT_COURSE_NOT_FOUND = 'Nie znaleziono kursu';
  C_TXT_DASH_FULLY = '- pełny';
  C_TXT_DASH_SHORTLY = '- skrócony';
  C_TXT_DASH_DAILY = '- dzienny';
  C_TXT_DASH_FROM_TASK = '- z zadania';
  C_TXT_DASH_FROM_CURRENT_DAY = '- z dnia bieżącego';
  C_TXT_DASH_FOR_PERIOD = '- za okres';
  C_TXT_DASH_START_PRINTING = '- rozpoczęcie drukowania';
  C_TXT_DASH_END_PRINTING = '- zakończenie drukowania';
  C_TXT_TICKETS_COUNT = 'Bilety           - liczba:';
  C_TXT_ADDITIONAL_PAYMENTS_COUNT = 'Opłaty dodatkowe - liczba:';
  C_TXT_ADDITIONAL_PAYMENTS_CAPTION = 'Opłaty dodatkowe (towary)';
  C_TXT_DOCUMENTS_NUMBER = 'numer dokumentu:';
  C_FMT_PASSANGER_COUNT = 'liczba pasażerów: %d';
  C_FMT_SUM_TO_PAY = 'wartość: %9f do zapłaty: %9f';
  C_FMT_INCORRECT_TICKET_RELATIONSHIP = '* Nieprawidłowa informacja o relacji biletu (%d/%d)';
  C_FMT_TICKET_CONTROL_CODE = 'Numer kontrolny biletu: %s';
  C_FMT_CANCELED_EM_CARD_RIDE_REGISTERING = 'rejestracja przejazdu z EM-kartą nr: %u anulowana, zapis biletu do EM-karty nie został wykonany';
  C_FMT_EM_CARD_AND_COMPANY = 'EM-karta nr: %s wydana przez firmę nr: %4d';
  C_FMT_EM_CARD_TICKET_PROLONGING_NR = 'EM-karta nr: %s bilet %s przedłużenie nr %d';
  C_FMT_TICKET_AND_VALIDITY_DATES = 'Bilet nr: %s ważny od %s do %s';
  C_TXT_REGISTERED_RIDE_AND_BUSTSTOP_NOT_EXISTS = 'Zarejestrowany przejazd do przystanku nieistniejącego w trasie kursu.';
  C_FMT_INCORRECT_TICKETS_COMPANY_NUMBER = 'Błędny numer firmy - sprzedawcy biletu %d';
  C_FMT_INCORRECT_TICKETS_NUMBER = 'Błędny numer biletu %s';
  C_FMT_INCORRECT_UNIQUE_USHERETTE_NUMBER = 'Błędny numer unikatowy bileterki sprzedawcy %s';
  C_FMT_INCORRECT_TICKETS_SALE_DATE = 'Błędna data sprzedaży biletu %s';
  C_FMT_INCORRECT_TICKETS_TYPE = 'Błędny typ biletu %d';
  C_FMT_INCORRECT_REDUCTION_TYPE = 'Błędny typ ulgi %d';
  C_FMT_INCORRECT_TICKETS_KIND = 'Błędny rodzaj biletu %d';
  C_FMT_INCORRECT_TICKETS_AMOUNT = 'Błędna wartość biletu %d';
  C_FMT_EM_CARD_NUMBER_TEMPLATE = 'Bilet nr: %s   Wzór biletu zapisany w EM-karcie';
  C_FMT_EM_CARD_NUMBER_FROM_BUS_AND_VALIDITY_TO = 'Bilet nr: %s   Ważny do %s (zakup w autobusie)';
  C_FMT_EM_CARD_NUMBER_FROM_BUS_AND_VALIDITY_DATES = 'Bilet nr: %s   Ważny od %s do %s (zakup w autobusie)';
  C_FMT_TICKETS_VALIDITY_EXTENDS_TO = 'Ważność biletu przedłużona do:  %s';
  C_TXT_BASED_ON_TICKETS_PRINT = 'na podstawie kodu z wydruku biletu';
  C_TXT_BASED_ON_CODE_FROM_DRIVERS_CARD = 'na podstawie kodu zapisanego w karcie kierowcy';
  C_FMT_TICKETS_VALIDITY_PERIOD_EXTENDED = 'Okres ważności biletu przedłużony do:         %s';
  C_TXT_BASED_ON_PRINT_CODE = 'na podstawie kodu z wydruku (dozwolone przedłużenia z przerwami)';
  C_TXT_NO_TICKETS_VALIDITY_EXTENDING_INFORMATION = '*brak informacji o sposobie przedłużenia ważności biletu';
  C_TXT_EXTENDING_OPERATION_DURING_RIDE = 'Operacja przedłużenia ważności została wykonana przy rejestracji bieżącego przejazdu';
  C_FMT_NEW_TICKETS_CONTROL_CODE = 'Kod kontrolny nowego biletu..:   %s';
  C_TXT_TICKET_REPEAT_WRITING = 'powtórzony zapis biletu w raporcie - zapis pominięty';
  C_TXT_RECEIPT_WRONGLY_PRINTED = 'Paragon nie został zapisany w pamięci fiskalnej - zapis pominięty';
  C_TXT_TICKET_WRONGLY_PRINTED = 'Bilet nie został zapisany w pamięci fiskalnej - zapis pominięty';
  C_TXT_EM_CARD_TICKET_SELLING_CANCELLATION = 'sprzedaż anulowana, zapis biletu do EM-karty nie został wykonany';
  C_FMT_COURSE_NUMBER = 'Kurs: %s';
  C_FMT_RIDE_RELATIONSHIP_DASH = 'relacja przejazdu: %s -';
  C_TXT_ATTENTION_NO_TICKETS_PROLONGING_INFORMATION = 'Uwaga: informacja o przedłużeniu ważności biletu prawdopodobnie nie została wpisana do EM-karty';
  C_TXT_ATTENTION_NO_RIDE_WITH_EM_CARD_INFORMATION = 'Uwaga: informacja o rejestracji przejazdu prawdopodobnie nie została wpisana do EM-karty';
  C_TXT_EM_CARD_WAS_TOO_EARLY_REMOVED_FROM_READER = 'Powtórzony odczyt - EM-karta została zbyt wcześnie zdjęta z czytnika';
  C_TXT_POWER_ON_AND_LAST_POWER_OFF = 'Włączenie zasilania; ostatnie wyłączenie: ';
  C_TXT_UNKNOWN = 'nieznane';
  C_FMT_DRIVERS_NOT_EXISTS = 'Brak w bazie kierowcy %s %s o numerze %d';
  C_TXT_DRIVERS_CARD_INSERTION = 'Włożenie karty kierowcy';
  C_TXT_DRIVERS_CARD_VERIFICATION = 'Weryfikacja karty kierowcy';
  C_TXT_NO_BUSSTOP_INFORMATION = '- brak informacji o przystanku';
  C_FMT_BY_DECOMPOSITION = '%s (wg rozkładu: %s)';
  C_FMT_ARRIVAL_TIME_BY_DECOMPOSITION = '%s  godzina przyjazdu wg rozkładu: %s (%d)';
  C_TXT_LAST_DOCUMENT_NUMBER = 'nr ost. dokumentu:';
  C_TXT_INCORRECT_TICKET_NUMBER_IGNORED_RECORD = 'nieprawidłowy numer EM-karty, wpis zignorowano';
  C_FMT_RELEASED_BY_COMPANY_NUMBER = '%s wydanej przez firmę nr: %4d';
  C_FMT_REDUCTION_DOCUMENT = 'Numer dokumentu potwierdzającego uprawnienie do ulgi: %s';
  C_TXT_REDUCTION_DOCUMENT_IS_VALID_INDEFINITELY = 'Dokument ważny bezterminowo';
  C_FMT_REDUCTION_DOCUMENT_VALID_TO = 'Dokument ważny do %s';
  C_FMT_BUYER_NIP = 'NIP nabywcy: %s';
  C_FMT_ERROR_CODE = 'Kod błędu %d';
  C_FMT_MISSING_RECEIPT = ' brak paragonu fiskalnego nr %.6d';
  C_FMT_MISSING_RECEIPTS = ' brak paragonów fiskalnych o numerach %.6d - %.6d';
  C_FMT_MISSING_RECEIPT_DUO = 'nieprawidłowa numeracja paragonów fiskalnych; bieżący: %.5d poprzedni: %.5d';
  C_TXT_MISSING_COURSE = '*Brak wybranego kursu';
  C_TXT_INCOMPATIBLE_OPENEDAND_CLOSED_COURSES = '*Numer zakończonego kursu niezgodny z otwartym kursem';
  C_FMT_TICKETS_COUNT_PRICE_TO_PAY = 'liczba %s wartość: %6.2f do zapłaty: %6.2f';
  C_FMT_TICKETS_LESS_ZERO = '*Liczba %s <= 0';
  C_TXT_CONVERSION_OF_DEBT = 'Przeliczenie należności';
  C_FMT_CHANGED_PAYMENT_TYPE = 'zmieniony sposób zapłaty: %s';
  C_TXT_CURRENCY = 'Waluta:  ';
  C_FMT_DISTANCE_KM_IN_PARENTHESES = '(%.1fkm)';
  C_FMT_RECEIPT_PRICE_TO_PAY = '%-20s wartość: %7.2f do zapłaty: %7.2f';
  C_FMT_CONTROL_CODE_OF_ADDITIONAL_PAYMENT = 'Numer kontrolny opłaty dodatkowej: %s';
  C_TXT_MISSING_PTU = ' *brak stawek PTU';
  C_TXT_MISSING_OPEN_FISCAL_REPORT = ' *Brak wpisu otwarcia raportu fiskalnego';
  C_FMT_BEGIN_DAY_PRICES_ERRORS_CANCELLED = 'Anulowano błędy niezgodności cen biletów od początku zadania';
  C_FMT_BEGIN_DAY_PRICES_ERRORS_CANCELLED_WITH_DAY = 'Anulowano błędy niezgodności cen biletów od początku dnia %s';
  C_FMT_INCORRECT_TICKETS_SUM_IN_PRINT_RZ = 'Suma wartości biletów: %.2f niezgodna z wydrukiem raportu zadaniowego (liczba biletów: %d)';
  C_TXT_PRINTING_ERR_CRASH = ' awaria mechanizmu;';
  C_TXT_PRINTING_ERR_LOW_TEMPERATURE = ' temperatura za niska;';
  C_TXT_PRINTING_ERR_HIGH_TEMPERATURE = ' temperatura za wysoka;';
  C_TXT_PRINTING_ERR_LOW_VOLTAGE = ' napięcie za niskie;';
  C_TXT_PRINTING_ERR_HIGH_VOLTAGE = ' napięcie za wysokie;';
  C_TXT_PRINTING_ERR_NO_PAPER_COPY = ' brak papieru - kopia;';
  C_TXT_PRINTING_ERR_NO_PAPER_ORIGINAL = ' brak papieru - oryginał;';
  C_TXT_PRINTING_ERR_OFFSET_STRIP = ' odsunięta listwa;';
  C_FMT_TIME_CORRECTION = '==> po korekcie: %s';
  C_TXT_PRINTING_WITHOUT_CARD_DAILY = 'dobowy';
  C_TXT_PRINTING_WITHOUT_CARD_MONTHLY = 'miesięczny';
  C_TXT_PRINTING_WITHOUT_CARD_PERIODIC_BY_DATE = 'okresowy wg dat';
  C_TXT_PRINTING_WITHOUT_CARD_PERIODIC_BY_NUMBER = 'okresowy wg nr';
  C_TXT_PRINTING_WITHOUT_CARD_NOT_RESET = 'niezerujący';
  C_TXT_PRINTING_WITHOUT_CARD_COURSES = 'kursów';
  C_TXT_PRINTING_WITHOUT_CARD_INFORMATIVE = 'informacyjny';
  C_TXT_ERR_FISCALREPORT_NOT_DEFINED = 'Raport fiskalny nie został zainicjalizowany';
  C_TXT_ERR_RIDE_NOT_DEFINED = 'Brak kursu';
  C_TXT_ERR_EMCARD_DIFFERENT_COMPANIES = 'Nie zgadzają się firmy w bilecie wzorcowym oraz w zdarzeniu "Zakup w autobusie biletu miesięcznego / okresowego na następny okres".';
  C_TXT_ERR_EMCARD_TICKETREGISTER_DIFFERENT_COMPANIES = 'Firma przewożąca musi być właścicielem bileterki.';
  C_TXT_INCORRECT_TICKET_PAY_TYPE_INDEX = ' *nieprawidłowy numer sposobu zapłaty w zapisie biletu';
  C_TXT_INCORRECT_TICKET_CURRENCY_INDEX = ' *nieprawidłowy numer waluty w zapisie biletu';
  C_FMT_CURRENCY_NOT_FOUND = 'Waluta %s nie została znaleziona.';
  C_TXT_EMPTY_CURRENCY_SYMBOL = 'Pusty symbol waluty.';
  C_FMT_NOT_SUPPORTED_EVENT = 'Nieobsłużone zdarzenie %d.';

  /// <summary>
  ///  *nieprawidłowe dane w sekcji (%s) -
  /// </summary>
resourcestring
  C_FMT_INCORRECT_DATA_IN_SECTION_DUO = ' *nieprawidłowe dane w sekcji (%s) - ';

  C_TXT_REGISTRATION_ERR_TICKETS_WITH_WRONG_PRICES = 'UWAGA: raport zawiera bilety, których wartość jest niezgodna z cennikiem.';
  C_TXT_REGISTRATION_ERR_TICKETS_WITH_WRONG_PRICES_CNT = 'Liczba biletów niezgodnych z cennikiem: %d';
  C_TXT_REGISTRATION_ERR_AFTER_RF_CLOSE = 'Po rejestracji raportu zadaniowego zawierającego wpis zamknięcia raportu fiskalnego';
  C_TXT_REGISTRATION_ERR_CHECK_TICKET_PRICES = 'należy sprawdzić zgodność sumy wartości biletów z sumą zapisaną do pamięci fiskalnej.';
  C_TXT_REGISTRATION_ERR_CANCEL_TICKETS = 'Bilety z nieprawidłowymi wartościami można anulować przy pomocy funkcji "Anulowanie biletów"';

  C_TXT_REGISTRATION_IS_NOT_POSSIBLE = '*w raporcie są błędy uniemożliwiające jego rejestrację';
  C_TXT_REGISTRATION_ERROR_PLACE = '*miejsca błędów opisane są komunikatami zaczynającymi się od znaku [*]';
  C_TXT_REGISTRATION_ERROR_DESCRIPTION = '*wiersze z opisem błędów można wyszukać w przebiegu zadania przy pomocy funkcji "Szukaj w tekście..."';

  C_MSG_FILE_NOT_FOUND = 'Plik nie został znaleziony.';
  C_FMT_FILE_NOT_FOUND = 'Plik %s nie został znaleziony.';
  C_MSG_USB_DEVICE_NOT_FOUND = 'Brak podłączonego czytnika kart pamięci';
  C_MSG_USB_DEVICE_NO_MEMORY = 'Brak karty pamięci w czytniku';
  C_MSG_NO_REPORT_IN_CARD = 'Karta pamięci nr %.6u nie zawiera danych do rejestracji.';
  C_MSG_USB_DEVICE_IS_BUSY = 'Czytnik kart pamięci kierowców jest zajęty przez inny program.';
  C_MSG_DIR_NOT_FOUND = 'Strona DIR nie znaleziona w pliku.';
  C_MSG_REGISTRATION_USER_TERMINATE = 'Rejestracja raportu została zawieszona przez użytkownika.';
  C_MSG_INCORRECT_FILE_READING_ERROR = 'Błędna zawartość pliku %s';
  C_MSG_INCORRECT_FILE_READING_ERROR_FROM_SERVER = 'Błędna zawartość pliku %s odczytanego z serwera.';
  C_MSG_INCORRECT_FILE_NAME = 'Błędna nazwa pliku %s';
  C_MSG_UNKNOWN_READING_ERROR = 'Niezdefiniowany kod błędu przy odczycie pliku.';
  C_TXT_COUNTER = 'stan licznika:';
  C_FMT_KILOMETRS = '%d km.';
  C_TXT_AMOUNT_OF_FUEL = 'ilość zatankowanego paliwa:';
  C_FMT_LITERS = '%.1f l.';
  C_FMT_WRONG_RECORDS_SEQUENCE = 'Nieprawidłowa kolejność rekordów: %d, %d';
  C_FMT_INCOMPLETE_RECORD_ENTRY = 'Niepełny wpis w raporcie. Rekord %d';
  C_FMT_RECORD_CHECKSUM_ERROR = '*Błąd sumy kontrolnej. Rekord: %d';
  C_FMT_LIKELY_RECORD_KIND = '*Prawdopodobny rodzaj rekordu: %d';
  C_FMT_RECORD_STRUCTURE_ERROR = '*Błędna struktura. Rekord: %d';

  C_FMT_FARE_PRICE_REDUCTION = 'Dla firmy "%s" ulga "%s" z kodem %d nie została znaleziona';

  C_FMT_EMCARD_TICKET_PROLONGING_CARD_NOT_EXISTS = 'brak danych EM-karty %u w wykazie biletów do sprzedaży w autobusie';
  C_FMT_EMCARD_TICKET_PROLONGING_TICKET_NOT_EXISTS = 'brak danych biletu %s w wykazie biletów do sprzedaży w autobusie';
  C_FMT_EMCARD_TICKET_PROLONGING_LAST_TICKET = 'w wykazie EM-karta nr %s ma wpisany bilet %s ważny od %s do %s sprzedany %s';
  C_FMT_EMCARD_TICKET_PROLONGING_EXTCOUNT_NOT_EXISTS = 'brak rekordu z LOKRP=%d biletu %s w wykazie biletów do sprzedaży w autobusie';
  C_FMT_EMCARD_TICKET_PROLONGING_LAST_TICKET_VALID = 'ważny od %s do %s';
  C_FMT_EMCARD_TICKET_PROLONGING = 'Przedłużenie nr %d na okres od %s do %s';

  C_TXT_LOCATIONIDENTIFIER_ADDITIONAL_INFO = 'Przy dodawaniu folderu w programie Synchronizacja raportów użyj identyfikator lokalizacji przypisany do wybranego użytkownika, żeby rejestrować na niego raporty.';

  C_TXT_REGISTERS = 'Rejestry';
  C_TXT_CORRECT = 'poprawny';
  C_TXT_INCORRECT = 'nieprawidłowy';
{$ENDREGION}

  C_TXT_ERROR_CashReport_FK_User = 'Błąd podczas próby rejestracji z aplikacji Synchronizacja Raportów - nieprawidłowy identyfikator lokalizacji!'
      + #13#10'Pobierz raport i zarejestruj go ponownie z pliku (błędny raport należy usunąć z kolejki).'
      + #13#10'Popraw numer identyfikatora lokalizacji, żeby rozwiązać problem w przyszłości.'
      + #13#10'Lista identyfikatorów lokalizacji znajduje się w parametrach rejestracji.';

  RS_FAREPRICESCALE_READERROR = 'Błąd odczytu taryfy z bazy.';

  C_REPORT_TITLE_LIST_OF_CASH_REPORTS = 'Sprawozdanie kasowe';
  C_REPORT_TITLE_LIST_OF_CASH_REPORTS_OF_EMPLOYEES = 'Rozliczenie pracowników';
  C_REPORT_TITLE_LIST_OF_CASH_REPORTS_REG_OF_RECEIPTS = 'Rejestr wpływów';
  C_REPORT_TITLE_LIST_OF_CASH_REPORTS_OF_PAYMENTS = 'Zestawienie wpłat kierowców/kasjerów';
  C_REPORT_TITLE_LIST_OF_CASH_REPORTS_UNSETTLED_SR = 'Nierozliczone Raporty Zadaniowe';
  C_TXT_PREPARED = 'Sporządził';
  C_TXT_ACCEPTED = 'Zatwierdził';
  C_TXT_CHECKED = 'Sprawdził';
  C_TXT_DATE = 'Data';
  C_TXT_SIGN = 'Podpis';
  C_TXT_From = 'Od';
  C_TXT_To = 'Do';
  C_TXT_Wait = 'Czeka';
  C_TXT_Error = 'Błąd';

  RS_BUSSTOP_UN_AUTO = '(nadaj automatycznie)';
  RS_BUSSTOP_UN_ERR = 'Nazwa stanowiska nie może być pusta!';

  RS_DRIVER_IDNUMBER_VALIDATE_ERROR = 'Numer pracownika|Pole nie może być puste i wprowadzona wartość musi być unikatowa i większa od zera.|0';

  RS_ROADPOINT_TYPE_0001 = 'Punkt na drodze';
  RS_ROADPOINT_TYPE_0002 = 'Stacja benzynowa';
  RS_ROADPOINT_TYPE_0003 = 'Parking';
  RS_ROADPOINT_TYPE_0004 = 'Bramka na autostradzie';
  RS_ROADPOINT_TYPE_0005 = 'Zmiana kierowcy';
  RS_ROADPOINT_TYPE_0006 = 'Granica państwa';
  RS_ROADPOINT_TYPE_0007 = 'Stanowisko';
  RS_ROADPOINT_TYPE_0008 = 'Miejsce postoju';
  RS_ROADPOINT_TYPE_0009 = 'Granica województwa';
  RS_ROADPOINT_TYPE_0018 = 'Granica powiatu';
  RS_ROADPOINT_TYPE_0019 = 'Granica gminy';
  RS_ROADPOINT_TYPE_0030 = 'Miejsce wydawania kart';
  RS_ROADPOINT_TYPE_NA   = 'Punkt drogowy - nieznany typ';

  RS_INFO_REDUCTION_ORDER = 'Wejdź w Cenniki -> Ulgi -> Kolejność w %s i ustaw numerację ulg.';
  RS_INFO_REDUCTION_A80   = 'bil. autobusowych';
  RS_INFO_REDUCTION_A6D   = 'bil. stacjonarnych';


function RoutePointTypeDesc(aId: integer): string;

implementation

function RoutePointTypeDesc(aId: integer): string;
begin
  case aId of
     1: Result := RS_ROADPOINT_TYPE_0001;
     2: Result := RS_ROADPOINT_TYPE_0002;
     3: Result := RS_ROADPOINT_TYPE_0003;
     4: Result := RS_ROADPOINT_TYPE_0004;
     5: Result := RS_ROADPOINT_TYPE_0005;
     6: Result := RS_ROADPOINT_TYPE_0006;
     7: Result := RS_ROADPOINT_TYPE_0007;
     8: Result := RS_ROADPOINT_TYPE_0008;
     9: Result := RS_ROADPOINT_TYPE_0009;
    18: Result := RS_ROADPOINT_TYPE_0018;
    19: Result := RS_ROADPOINT_TYPE_0019;
    30: Result := RS_ROADPOINT_TYPE_0030;
  else
    Result := RS_ROADPOINT_TYPE_NA;
  end;
end;

end.
