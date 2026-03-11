{$WARNINGS ON}
{$HINTS ON}
{$WARN UNIT_PLATFORM OFF}
{$WARN SYMBOL_PLATFORM OFF}
unit KMFilesUtil;

interface

uses
  ComCtrls,
  Gauges,
  Windows, SysUtils, Classes, Forms;

const
  CONST_1GB = 1073741824;
  CONST_1MB = 1048576;
  CONST_1KB = 1024;

type
  TFindFileOption = (ffExtracExt = 1, ffExtractPath = 2);
  TFindFileOptions = Set Of TFindFileOption;

  TFindFilesRec = record
    TotalBytes: Int64;
  end;

  PFindFilesRec = ^TFindFilesRec;
{$REGION 'Documentation'}
  /// <summary>
  /// Usuwa wszystkie pliki z folderu starsze niż ileś godziń (aOlderThanHours)
  /// </summary>
  /// <param name="aFileMask">
  /// Nazwa folderu plus maska plików, które chcemy usunąć, np.:
  /// <para>c:\temp\*.* - usuwa wszystki pliki z folderu c:\temp.</para>
  /// <para>c:\temp\*.txt - usuwa wszystki pliki z folderu c:\temp, które mają rozszerzenie txt.</para>
  /// </param>
  /// <param name="aOlderThanHours">
  /// Określa o ile godziń plik musi być starszy niż beżącego czasu.
  /// </param>
  /// <param name="aFailOnError">
  /// TRUE - przeruwanie dalsze usuwanie plików przy napotkania błędu, FALSE - udzie dalej.
  /// </param>
  /// <returns>
  /// Ilość usuniętych plików
  /// </returns>
{$ENDREGION}

  TPurgeFileThread = class(TThread)
  private
    fFileMask: string;
    fOlderThanHours: cardinal;
    fFailOnError: boolean;
    fResult: integer;
  protected
    procedure Execute; override;
  public
    constructor Create(const aFileMask: string; aOlderThanHours: cardinal; aFailOnError: boolean = false);
    property Result: integer read fResult;
  end;
{$REGION 'Documentation'}
  /// <summary>
  /// Zwraca nazwę pliku opartą o wygenerowany GUID i folder tymczasowy użytkownika
  /// </summary>
  /// <param name="aExt">
  /// Opcjonalne rozszerzenie nazwy pliku, domyślnie .tmp
  /// Proszę pamiętać o podawaniu rozszerzenia Z KROPKĄ
  /// </param>
{$ENDREGION}

function GetGUIDTempFileName(AExt: String = '.tmp'): string;
{$REGION 'Documentation'}
/// <summary>
/// Do usuwania zawartości folderu
/// </summary>
/// <param name="aDirectory">
/// Usuwany folder
/// </param>
/// <param name="WithUI">
/// Czy pokazywać pasek postępu wbudowany w Windows towarzyszący usuwaniu plików. Domyślnie: True
/// </param>
/// <param name="WithConfirmation">
/// Czy wymagane jest potwierdzenie użytkownika (Windows). Domyślnie: False
/// </param>
/// <param name="PermanentDelete">
/// Jeśli ustawiony na False (domyślnie) - pliki są przenoszone do kosza. W przeciwnym wypadku są kasowane nieodwracalnie.
/// </param>
{$ENDREGION}
procedure ForceDeleteDir(aDirectory: string; WithUI: boolean = True; WithConfirmation: boolean = false; PermanentDelete: boolean = false);
{$REGION 'Documentation'}
/// <summary>
/// Usuwa plik, nawet gdy jest ReadOnly
/// </summary>
/// <param name="aFilePath">
/// Usuwany plik
/// </param>
{$ENDREGION}
function ForceDeleteFile(aFilePath: String): Boolean;
{$REGION 'Documentation'}
/// <summary>
/// Zwraca rozmiar pliku o nazwie AFullFileName w bajtach. Jesli plik nie istnieje zwraca -1
/// </summary>
/// <param name="AFullFileName">
/// Pełna nazwa pliku ze ścieżką
/// </param>
/// <returns>
/// FileSize (Int64) - rozmiar pliku
/// </returns>
/// <example>
/// <c>GetFileSize('c:\ciekawecotozaplik.zip')</c>
/// </example>
/// <remarks><c>GetFileSize('c:\ciekawecotozaplik.zip')</c> </remarks>
{$ENDREGION}
function GetFileSize(AFullFileName: string): Int64;
function GetFileDateTime(AFullFileName: string): TDateTime;
{$REGION 'Documentation'}
/// <summary>
/// Pozwala na wybór folderu. Folder musi istnieć.
/// Jeśli do procedury przekazany jest pusty string - ścieżka początkowa dialogu jest ustawiana
/// na folder dokumentów użytkownika Windows
/// </summary>
/// <param name="aDir">
/// Pełna nazwa ścieżki początkowej. W przypadku powodzenia zawiera nowo wybrany folder.
/// </param>
/// <param name="aCanCreateNewDir">
/// Parametr typu boolean wskazujący czy użytkownik może tworzyć nowe foldery. Domyślnie false.
/// </param>
/// <returns>
/// True gdy użytkownik dokonał wyboru.
/// </returns>
/// <example>
/// <c>SelectDir('c:\ciekawe\co\to\za\folder', True)</c>
/// </example>
{$ENDREGION}
function SelectDir(var aDir: String; ACanCreateNewDir: boolean = false): boolean;
{$REGION 'Documentation'}
/// <summary>
/// Sprawdza czy podany plik/folder jest na dysku "lokalnym".
/// </summary>
/// <param name="aFullFileName">
/// Pełna (z dyskiem) nazwa pliku/folderu którego lokalizacja jest sprawdzana.
/// Jesli to samo oznaczenie napędu musi być zakończone pathdelimiterem.
/// </param>
/// <returns>
/// True gdy folder/plik znajduje się na dysku "lokalnym", w przeciwnym przypadku
/// lub w przypadku błędu zwraca False.
/// </returns>
/// <example>
/// <c>if IsLocalFolder('p:\ciekawe\co\to\za\folder') then</c>
/// </example>
{$ENDREGION}
function IsDriveLocal(AFullFileName: string): boolean;
function FindFiles(const Path, Mask: string; IncludeSubDir: boolean; SL: TStringList; AOptions: TFindFileOptions = [];
  AFindFilesRec: PFindFilesRec = nil): integer;

/// <summary>
///   return true if filename Name matches Mask, which may have wildcard(s);
///   path allowed in Name string
///   multi masks separated by ';'
/// </summary>ary
function MatchesMask(Name, Mask : String): Boolean;

function FindFileName(const Path, Mask: string; var bFileName : String) : Boolean;
function FileExistsRecursive(AFilePath: String): Boolean;

procedure MakeTextFile(AFileName: String; AText: String); overload;
procedure MakeTextFile(AFileName: String; AStringList: TStringList); overload;
function TryLoadFile(AFileName: String; AList: TStringList): boolean;
function TrySaveToFile(AFileName: String; AList: TStringList): boolean;
function TryFileExists(Var AFileName: String): boolean;
function AppFullFileName(AFileName: String): String;
function ChangeFileNameIfExists(AFileName: String; APattern: String): String;
function RequiredFileWithName(AFileName: String; ABackupPattern: String = '[N]_[C4][E].bak'): boolean;
function GetTextFileCodePage(AFilePath: String): TEncoding;

function GetDirSize(ADirPath: string; AIncludeSubDir: boolean): Int64;
{$REGION 'Documentation'}
/// <summary>
/// Do zmiany nazwy pliku
/// </summary>
/// <param name="AFileName">
/// Nazwa pliku (może być pełna ścieżka)
/// </param>
/// <param name="ANewFileNamePattern">
/// Nowa nazwa pliku , można użyć %FILENAME%, wtedy podstawia nazwę pliku razem z rozszerzeniem, %NAME% bez rozszerzenia
/// </param>
/// <returns>
/// Nowa nazwa pliku (z pełną ścieżką)
/// </returns>
{$ENDREGION}
function ChangeFileName(AFileName: String; ANewFileNamePattern: String): String;
{$REGION 'Documentation'}
/// <summary>
/// Usuwa wszystkie pliki z folderu starsze niż ileś godzin (aOlderThanHours)
/// </summary>
/// <param name="aFileMask">
/// Nazwa folderu plus maska plików, które chcemy usunąć, np.:
/// <para>c:\temp\*.* - usuwa wszystki pliki z folderu c:\temp.</para>
/// <para>c:\temp\*.txt - usuwa wszystki pliki z folderu c:\temp, które mają rozszerzenie txt.</para>
/// </param>
/// <param name="aOlderThanHours">
/// Określa o ile godziń plik musi być starszy niż beżącego czasu.
/// </param>
/// <param name="aFailOnError">
/// TRUE - przeruwanie dalsze usuwanie plików przy napotkania błędu, FALSE - udzie dalej.
/// </param>
/// <returns>
/// Ilość usuniętych plików
/// </returns>
{$ENDREGION}
function PurgeFiles(const aFileMask: string; aOlderThanHours: cardinal; aFailOnError: boolean = false): integer;
{$REGION 'Documentation'}
/// <summary>
/// Funkcja callback do CopyFileEx
/// Kopiuje plik pokazując postęp
/// https://msdn.microsoft.com/en-us/library/aa363854(v=vs.85).aspx
/// </summary>
/// <param name="TotalFileSize">
/// Całkowity rozmiar pliku
/// </param>
/// <param name="TotalBytesTransferred">
/// Ilość skopiowanych bajtów
/// </param>
/// <param name="StreamSize">
/// Rozmiar strumienia
/// </param>
/// <param name="StreamBytesTransferred">
/// The total number of bytes in the current stream that have been transferred
/// from the source file to the destination file since the copy operation began.
/// </param>
/// <param name="dwStreamNumber">
/// A handle to the current stream. The first time CopyProgressRoutine is called, the stream number is 1.
/// </param>
/// <param name="dwCallbackReason">
/// The reason that CopyProgressRoutine was called. This parameter can be one of the following values:
/// <para>CALLBACK_CHUNK_FINISHED: 0x00000000 Another part of the data file was copied.</para>
/// <para>CALLBACK_STREAM_SWITCH: 0x00000001 Another stream was created and is about to be copied.
/// This is the callback reason given when the callback routine is first invoked.</para>
/// </param>
/// <param name="hSourceFile">
/// A handle to the source file.
/// </param>
/// <param name="hDestinationFile">
/// A handle to the destination file
/// </param>
/// <param name="AProgressbar">
/// Obiekt klasy TProgressBar(|ComCtrls), na którym będzie pokazywany postęp
/// </param>
/// <returns>
/// The CopyProgressRoutine function should return one of the following values.
/// <para>PROGRESS_CONTINUE: 0 Continue the copy operation.</para>
/// <para>PROGRESS_CANCEL: 1 Cancel the copy operation and delete the destination file.</para>
/// <para>PROGRESS_STOP: 2 Stop the copy operation. It can be restarted at a later time.</para>
/// <para>PROGRESS_QUIET: 3 Continue the copy operation, but stop invoking CopyProgressRoutine to report progress.</para>
/// </returns>
{$ENDREGION}
function CopyFileCallback(TotalFileSize, TotalBytesTransferred, StreamSize, StreamBytesTransferred: COMP; dwStreamNumber, dwCallbackReason: DWORD;
  hSourceFile, hDestinationFile: THandle; AProgressMeter: TObject): DWORD; stdcall;
/// <summary>
/// Removes ReadOnly attribute from the file
/// </summary>
procedure RemoveReadOnlyAttributeFromFile(AFilePath: String);
/// <summary>
/// Removes ReadOnly attribute from all files inside the directory; by default works recursively
/// </summary>
{$IFNDEF ISQLSCRIPTTOOL}
procedure RemoveReadOnlyAttributeFromDirectory(ADirectory: String);
{$ENDIF}
implementation

uses
{$WARN UNIT_PLATFORM OFF}
  FileCtrl
{$WARN UNIT_PLATFORM ON}
  , Dialogs
  , KMWinSysUtils
  , ShellApi
  , KMStrUtils
  {$IFNDEF ISQLSCRIPTTOOL}
  , KMUtils
  {$ENDIF}
  , StrUtilsEx
  , System.IOUtils
  , Math
  ;

{ -----------------------------------------------------------------------------
  Procedure: IsDriveLocal
  Author:    maciej.jablonski
  Date:      03-wrz-2014
  Arguments: AFullFileName: string
  Result:    boolean
  Sprawdza czy podany folder/plik znajduje sie na dysku lokalnym.
  Pełny opis w dokumentacji w nagłówku
  22-wrz-2014 Zmiana polegająca na dodaniu DRIVE_REMOVABLE do kategorii dysków lokalnych
  oraz IncludeTrailingPathDelimiter
  ----------------------------------------------------------------------------- }

function IsDriveLocal(AFullFileName: string): boolean;
begin
  Result := GetDriveType(PChar(IncludeTrailingPathDelimiter(ExtractFileDrive(AFullFileName)))) in [DRIVE_FIXED, DRIVE_REMOVABLE];
end;

{ -----------------------------------------------------------------------------
  Procedure: SelectDir
  Author:    maciej.jablonski
  Date:      03-wrz-2014
  Arguments: var aDir: String
  Result:    boolean
  "Ulepszona" wersja wyboru folderu
  Pełny opis w dokumentacji w nagłówku
  ----------------------------------------------------------------------------- }

function SelectDir(var aDir: String; ACanCreateNewDir: boolean = false): boolean;
var
  DirOpts: TSelectDirExtOpts;
begin
  // DirOpts := [sdNewUI];
  DirOpts := [sdShowShares];
  if ACanCreateNewDir then
    DirOpts := DirOpts + [sdNewFolder];
  // Po protestach supportu przywrócona "zwykła" wersja
  // if Win32MajorVersion >= 6 then // Lepsza wersja niz XP
  // begin
  // with TFileOpenDialog.Create(nil) do
  // try
  // Title := 'Wybierz folder:';
  // Options := [fdoPickFolders, fdoPathMustExist, fdoForceFileSystem]; // YMMV
  // OkButtonLabel := 'Wybierz';
  // DefaultFolder := aDir;
  // FileName := aDir;
  // Result := Execute;
  // if Result then
  // aDir := FileName;
  // finally
  // Free;
  // end
  // end
  // else
  Result := SelectDirectory('Wybierz folder', ExtractFileDrive(aDir), aDir, DirOpts);
  if Result and (Trim(aDir) <> '') then
    aDir := IncludeTrailingPathDelimiter(Trim(aDir));
end;

{ -----------------------------------------------------------------------------
  Procedure: ForceDeleteDir
  Author:    maciej.jablonski & dimitar.paperov ;)
  Date:      03-wrz-2014
  Arguments: aDirectory: string; WithUI: boolean = True; WithConfirmation: boolean = False; PermanentDelete: boolean = False
  Result:    None
  Dodatkowe info: http://stackoverflow.com/questions/5716666/delphi-delete-folder-with-content
  ----------------------------------------------------------------------------- }
procedure ForceDeleteDir(aDirectory: string; WithUI: boolean = True; WithConfirmation: boolean = false; PermanentDelete: boolean = false);
var
  ShOp: TSHFileOpStruct;
begin
  ShOp.Wnd := 0; // Application.Handle;
  ShOp.wFunc := FO_DELETE;
  ShOp.pFrom := PChar(aDirectory);
  ShOp.pTo := nil;
  if not WithUI then
    ShOp.fFlags := ShOp.fFlags or FOF_NO_UI;
  if not WithConfirmation then
    ShOp.fFlags := ShOp.fFlags or FOF_NOCONFIRMATION;
  if not PermanentDelete then
    ShOp.fFlags := ShOp.fFlags or FOF_ALLOWUNDO;
  SHFileOperation(ShOp);
end;

function ForceDeleteFile(aFilePath: String): Boolean;
begin
  RemoveReadOnlyAttributeFromFile(aFilePath);
  Result := SysUtils.DeleteFile(aFilePath);
end;

function AppFullFileName(AFileName: String): String;
begin
  Result := AppDir + AFileName
end;

function FindFiles(const Path, Mask: string; IncludeSubDir: boolean; SL: TStringList; AOptions: TFindFileOptions = [];
  AFindFilesRec: PFindFilesRec = nil): integer;
var
  FindResult: cardinal;
  _SR: TSearchRec;
  fn: string;
begin
  Result := 0;
  if Assigned(AFindFilesRec) then
    AFindFilesRec^.TotalBytes := 0;

  FindResult := FindFirst(IncludeTrailingPathDelimiter(Path) + Mask, faAnyFile - faDirectory, _SR);
  while FindResult = 0 do
  begin
    { do whatever you'd like to do with the files found }
    if Copy(_SR.Name, 1, 1) <> '.' then
    begin

      if ffExtracExt in AOptions then
        _SR.Name := ChangeFileExt(_SR.Name, '');

      if ffExtractPath in AOptions then
        fn := _SR.Name
      else
        fn := IncludeTrailingPathDelimiter(Path) + _SR.Name;
      // if (_SR.Attr and faDirectory) > 0  then fn := '['+fn+']';
      if Assigned(SL) then
        SL.Add(fn);
      Result := Result + 1;
      if Assigned(AFindFilesRec) then
        AFindFilesRec^.TotalBytes := AFindFilesRec^.TotalBytes + _SR.Size;
    end;

    FindResult := FindNext(_SR);
  end;
  { free memory }
  SysUtils.FindClose(_SR);

  if not IncludeSubDir then
    Exit;

  FindResult := FindFirst(IncludeTrailingPathDelimiter(Path) + '*.*', faDirectory, _SR);
  while FindResult = 0 do
  begin
    if (_SR.Name <> '.') and (_SR.Name <> '..') then
      Result := Result + FindFiles(IncludeTrailingPathDelimiter(Path) + _SR.Name + '\', Mask, True, SL, AOptions, AFindFilesRec);

    FindResult := FindNext(_SR);
  end;
  { free memory }
  SysUtils.FindClose(_SR);
end;

function MatchesMask(Name, Mask: String): Boolean;
  { return true if filename Name matches Mask, which may have wildcard(s);
    path allowed in Name string }
  function Match (AName, AMask: PChar): Boolean; forward;
  function MatchStar (StopChar: Char; AName, AMask: PChar): Boolean;
  begin
    while True do
    begin
      if AName^ = StopChar then
        break;
      if AName^ = #0 then begin
        Result:= False;
        exit;
        end;
      Inc(AName);
      end;
    Result := Match(AName, AMask);
  end;
  function MatchQuestion (AName, AMask: PChar): Boolean;
  begin
    if AName^ = #0 then
      Result := False
    else
    begin
      Inc(AName);
      Result := Match(AName, AMask);
    end;
  end;
  function Match (AName, AMask: PChar): Boolean;
  begin
    if AMask^ = #0 then
      { mask is null string }
      Result := AName^ = #0
    else if AMask^ = '*' then
      { mask starts with "*" wildcard }
      Result := MatchStar(AMask[1], AName, AMask + 1)
    else if AMask^ = '?' then
      { mask starts with "?" wildcard }
      Result := MatchQuestion(AName, AMask + 1)
    else if AName^ = #0 then
      { name is a null string }
      Result := AMask = #0
    else if AMask^ = AName^ then
      { starting chars match }
      Result := Match(AName + 1, AMask + 1)
    else
      { starting chars mismatch }
      Result := False;
  end;
var
  sMaskItem: String;
  sl: TStringList;
begin { MatchesMask }
  Result := False;
  sl := TStringList.Create;
  try
    sl.Delimiter := ';';
    sl.DelimitedText := Uppercase(Mask);
    for sMaskItem in sl do
      if not sMaskItem.IsEmpty then
        if Match(PChar(Uppercase(ExtractFileName(Name))), PChar(sMaskItem)) then
          Exit(True);
  finally
    FreeAndNil(sl);
  end;
end;

function FindFileName(const Path, Mask: string; var bFileName : String) : Boolean;
var
  _sl: TStringList;
begin
  _sl := TStringList.Create;
  try
     Result := FindFiles(Path, Mask ,false, _SL ) > 0;
     if Result then bFileName := _SL[0] else bFileName := '';
  finally
    _sl.Free;
  end;
end;

function FileExistsRecursive(AFilePath: String): Boolean;
// AFilePath must contain the full file's path
var
  iValidRes: Integer; {Findfirst returns '0' only if there was no error}
  searchResult: TSearchRec; {required by 'FindFirst and FindNext' functions }
  sDirPath, sFullName, sFileName: String;

  // searchResult does not return the full path in the name variable in the record,
  // so 'sDirPath' is used to store the full path name,
  // and 'sFullName' holds the Full Path Name plus the file name or filter spec
  // while 'sFileName' holds the filter or filename
begin
  Result := False;
  sDirPath := ExtractFilePath(AFilePath); // keep track of the path ie: c:\folder\
  if not System.SysUtils.DirectoryExists(sDirPath) then Exit; // Invalid directory then exit
  sFileName := ExtractFileName(AFilePath); // keep track of the name or filter
  iValidRes := System.SysUtils.FindFirst(AFilePath, faAnyFile, searchResult); // find first file
  try
    if (iValidRes = 0)and((searchResult.Attr and faDirectory) <> faDirectory) then // is a searching file
      Result := True
    else
    begin
      System.SysUtils.FindClose(searchResult);
      sFullName := IncludeTrailingPathDelimiter(sDirPath) + '*';
      iValidRes := System.SysUtils.FindFirst(sFullName, faAnyFile, searchResult);
      if iValidRes = 0 then
      repeat
        // find file in the directory
        if ((searchResult.Attr and faDirectory) = faDirectory)
          and(searchResult.Name <> '.')
          and(searchResult.Name <> '..')
        then
        begin
          sFullName := sDirPath + searchResult.Name;
          Result := FileExistsRecursive(sFullName + PathDelim + sFileName);
        end;
        iValidRes := System.SysUtils.FindNext(searchResult);
      until Result or(iValidRes <> 0);
    end;
  finally
    System.SysUtils.FindClose(searchResult);
  end;
end;

procedure MakeTextFile(AFileName: String; AStringList: TStringList);
Begin
  if not Assigned(AStringList) then
    Exit;

  if FileExists(AFileName) then
    if not DeleteFile(AFileName) then
      Exit;

  AStringList.SaveToFile(AFileName);
End;

procedure MakeTextFile(AFileName: String; AText: String);
Var
  _StringList: TStringList;
Begin
  _StringList := TStringList.Create;
  try
    _StringList.Add(AText);
    MakeTextFile(AFileName, _StringList);
  finally
    _StringList.Free;

  end;
End;

function TryLoadFile(AFileName: String; AList: TStringList): boolean;
Var
  s: String;
begin
  s := AFileName;
  Result := FileExists(s);
  If not Result then
  Begin
    s := AppFullFileName(AFileName);
    Result := FileExists(s);
  End;

  if Result then
    AList.LoadFromFile(s);
end;

function TryFileExists(Var AFileName: String): boolean;
Begin
  Result := FileExists(AFileName);
  if not Result then
  Begin
    Result := FileExists(AppFullFileName(AFileName));
    if Result then
      AFileName := AppFullFileName(AFileName)
  End;
End;

function TrySaveToFile(AFileName: String; AList: TStringList): boolean;
begin
  Result := false;
  if not Assigned(AList) then
    Exit;
  try
    AList.SaveToFile(AFileName);
    Result := True;
  except
    try
      AList.SaveToFile(AppFullFileName(AFileName));
      Result := True;
    except
    end;
  end;
end;

function GetDirSize(ADirPath: string; AIncludeSubDir: boolean): Int64;
var
  rec: TSearchRec;
  found: integer;
begin
  Result := 0;
  if ADirPath[Length(ADirPath)] <> '\' then
    ADirPath := ADirPath + '\';
  found := FindFirst(ADirPath + '*.*', faAnyFile, rec);
  while found = 0 do
  begin
    Inc(Result, rec.Size);
    if (rec.Attr and faDirectory > 0) and (rec.Name[1] <> '.') and (AIncludeSubDir = True) then
      Inc(Result, GetDirSize(ADirPath + rec.Name, True));
    found := FindNext(rec);
  end;
  FindClose(rec);
end;

// function ChangeFileNameIfExists( _fn, '[N][C4][E]' ) : String;
function ChangeFileNameIfExists(AFileName: String; APattern: String): String;
var
  _cnt, _cnt_pos, z: integer;
  s, _nfn, _t, _fn, _ext, _path: string;
Begin
  _cnt := 1;
  _path := IncludeTrailingPathDelimiter(ExtractFilePath(AFileName));
  _fn := ExtractFileName(AFileName);
  _ext := ExtractFileExt(_fn);
  _fn := ChangeFileExt(_fn, '');
  _nfn := StringReplace(APattern, '[N]', _fn, [rfReplaceAll]);
  _nfn := StringReplace(_nfn, '[E]', _ext, [rfReplaceAll]);
  RemoveStringFromTo(_nfn, '[C', ']', s, _cnt_pos);
  z := StrToIntDef(s, -1);
  if (_cnt_pos > 0) and (z > 0) then
  Begin
    // Delete(_nfn, _cnt_pos , 3 + Length(s) );
    _t := _nfn;
    Insert(LPad(IntToStr(_cnt), z, '0'), _t, _cnt_pos);
    while FileExists(_path + _t) do
    Begin
      Inc(_cnt);
      _t := _nfn;
      Insert(LPad(IntToStr(_cnt), z, '0'), _t, _cnt_pos);
    End;
    _nfn := _t;
  End;
  Result := _path + _nfn;
End;

function RequiredFileWithName(AFileName: String; ABackupPattern: String): boolean;
Var
  _NewFileName: String;
begin
  if FileExists(AFileName) then
  Begin
    _NewFileName := ChangeFileNameIfExists(AFileName, ABackupPattern);
    Result := MoveFile(PWideChar(AFileName), PWideChar(_NewFileName));
  End
  else
    Result := True;
end;

function GetTextFileCodePage(AFilePath: String): TEncoding;
  function BytesEqual(const B1, B2: TBytes): Boolean;
  var
    I: Integer;
  begin
    if Length(B1) <> Length(B2) then
    begin
      Result := False;
      Exit;
    end;

    Result := True;
    for I := 0 to High(B1) do
    begin
      if B1[I] <> B2[I] then
      begin
        Result := False;
        Exit;
      end;
    end;
  end;
var
  LStream: TFileStream;
  LBytes: TBytes;
  LPreamble: TBytes;
  LEncoding: TEncoding;
  // An array to hold the encodings we want to check for a BOM.
  // This avoids the call to the unavailable TEncoding.GetEncodings.
  EncodingsToCheck: TArray<TEncoding>;
begin
  // Default to the system's default ANSI encoding as a fallback.
  Result := TEncoding.ANSI;

  if not TFile.Exists(AFilePath) then
    Exit; // File doesn't exist, return the default.

  LStream := nil;
  try
    LStream := TFileStream.Create(AFilePath, fmOpenRead or fmShareDenyWrite);
    if LStream.Size = 0 then
      Exit; // Empty file, return the default.

    // --- Step 1: Check for a Byte Order Mark (BOM) ---
    // Manually create a list of common encodings to check.
    // This is the compatible way for older Delphi versions.
    EncodingsToCheck := [TEncoding.UTF8, TEncoding.Unicode, TEncoding.BigEndianUnicode];

    for LEncoding in EncodingsToCheck do
    begin
      LPreamble := LEncoding.GetPreamble;
      // We only check encodings that have a preamble.
      if Length(LPreamble) > 0 then
      begin
        if LStream.Size >= Length(LPreamble) then
        begin
          SetLength(LBytes, Length(LPreamble));
          LStream.Position := 0;
          LStream.ReadBuffer(LBytes, Length(LBytes));
          // Use our custom BytesEqual function for compatibility.
          if BytesEqual(LBytes, LPreamble) then
          begin
            Result := LEncoding;
            Exit;
          end;
        end;
      end;
    end;

    // --- Step 2: If no BOM, heuristically check for UTF-8 ---
    // Many text files are saved as UTF-8 without a BOM. We can test this by
    // checking if the file's byte sequence is valid according to UTF-8 rules.
    LStream.Position := 0;
    // Read a sample chunk from the beginning of the file (up to 4KB).
    SetLength(LBytes, Min(LStream.Size, 4096));
    LStream.ReadBuffer(LBytes, Length(LBytes));

    try
      // The GetString method will raise an exception if it encounters an
      // invalid byte sequence for the UTF-8 encoding.
      TEncoding.UTF8.GetString(LBytes);

      // If no exception was raised, the sequence is valid UTF-8.
      // We'll prefer UTF8 as the result, as it's a superset of ASCII.
      Result := TEncoding.UTF8;
      Exit;
    except
      // An exception means it's not a valid UTF-8 sequence, so we fall through
      // to the next step.
    end;

    // --- Step 3: Fallback to System ANSI Encoding ---
    // If no BOM was found and the content is not valid UTF-8, it is most
    // likely a legacy single-byte encoding. The safest guess in this case
    // is the system's default ANSI code page (e.g., 1250).
    Result := TEncoding.ANSI;

  finally
    LStream.Free;
  end;
end;

{ -----------------------------------------------------------------------------
  Procedure: GetFileSize
  Author:    maciej.jablonski
  Date:      12-sie-2014
  Arguments: AFullFileName: string
  Result:    UInt64
  Zwraca rozmiar pliku w bajtach. Jesli plik nie istnieje - zwraca -1
  2014-08-28: Dimitar Paperov - zmiana na wersję z dużymi plikami
  ----------------------------------------------------------------------------- }

function GetFileSize(AFullFileName: string): Int64;
// var
// sr: TSearchRec;
// begin
// Result := -1;
// try
// if FindFirst(AFullFileName, faAnyFile, sr)=0 then
// Result:= sr.Size
// finally
// SysUtils.FindClose(sr);
// end;
var
  info: TWin32FileAttributeData;
begin
  if GetFileAttributesEx(PWideChar(AFullFileName), GetFileExInfoStandard, @info) then
    Result := Int64(info.nFileSizeLow) or Int64(info.nFileSizeHigh shl 32)
  else
    Result := -1;
end;

function GetFileDateTime(AFullFileName: string): TDateTime;
  function _UTCFileTimeToLocalDateTime(const UTCFileTime: TFileTime): TDateTime;
  var
    UTCSystemTime, LocalSystemTime: TSystemTime;
  begin
    if not FileTimeToSystemTime(UTCFileTime, UTCSystemTime) then
      RaiseLastOSError;
    if not SystemTimeToTzSpecificLocalTime(nil, UTCSystemTime, LocalSystemTime) then
      RaiseLastOSError;
    Result := SystemTimeToDateTime(LocalSystemTime);
  end;
var
  TmpSearchRec: TSearchRec;
begin
  Result := 0;
  if FileExists(AFullFileName) then
    if FindFirst(AFullFileName, faAnyFile, TmpSearchRec) = 0 then
    try
      Result := _UTCFileTimeToLocalDateTime(TmpSearchRec.FindData.ftLastWriteTime);
    finally
      FindClose(TmpSearchRec);
    end;
end;

function ChangeFileName(AFileName: String; ANewFileNamePattern: String): String;
var
  _path: string;
  _filename: string;
  _name: string;
  _ext: string;
begin
  _path := ExtractFilePath(AFileName);
  _filename := ExtractFileName(AFileName);
  _name := ChangeFileExt(_filename, '');
  _ext := ExtractFileExt(AFileName);

  Result := StringReplace(ANewFileNamePattern, '%NAME%', _name, []);
  Result := StringReplace(Result, '%FILENAME%', _filename, []);
  Result := StringReplace(Result, '%EXT%', _ext, []);
  Result := StringReplace(Result, '%PATH%', IncludeTrailingPathDelimiter(_path), []);
end;

{ -----------------------------------------------------------------------------
  Procedure: GetGUIDTempFileName
  Author:    maciej.jablonski
  Date:      12-wrz-2014
  Arguments: AExt: String = 'tmp'
  Result:    string
  ----------------------------------------------------------------------------- }

function GetGUIDTempFileName(AExt: String = '.tmp'): string;
var
  g: TGUID;
begin
  CreateGUID(g);
  Result := IncludeTrailingPathDelimiter(TempDir) + GUIDToString(g) + AExt;
end;

{ -----------------------------------------------------------------------------
  Procedure: PurgeFiles
  Author:    dimitar.paperov
  Date:      17-wrz-2014
  ----------------------------------------------------------------------------- }
function PurgeFiles(const aFileMask: string; aOlderThanHours: cardinal; aFailOnError: boolean = false): integer;
var
  rDirInfo: TSearchRec;
  iResult, iError: integer;
  dtFileDate, dtNow, dtOlderThen: TDateTime;
  sFilePath, sErrMess: string;
begin
  iResult := 0;
  dtNow := Now;
  dtOlderThen := aOlderThanHours / 24;
  sFilePath := ExtractFilePath(aFileMask);
  iError := FindFirst(aFileMask, faAnyFile, rDirInfo);
  while iError = 0 do
  begin
    if (rDirInfo.Name <> '.') and (rDirInfo.Name <> '..') and (rDirInfo.Attr and faDirectory <> faDirectory) then
    begin
      dtFileDate := rDirInfo.TimeStamp;
      if dtNow - dtFileDate > dtOlderThen then
      begin
        if not DeleteFile(sFilePath + rDirInfo.Name) then
        begin
          if aFailOnError then
          begin
            sErrMess := 'PurgFiles - nie udana próba usunięcie pliku ' + #13#10 + sFilePath + rDirInfo.Name + #13#10#13#10 + SysErrorMessage(GetLastError);
            raise Exception.Create(sErrMess);
          end;
        end
        else
          Inc(iResult);
      end;
    end;
    iError := FindNext(rDirInfo);
  end;
  FindClose(rDirInfo);
  Result := iResult;
end;

{ TPurgeFileThread }

constructor TPurgeFileThread.Create(const aFileMask: string; aOlderThanHours: cardinal; aFailOnError: boolean);
begin
  inherited Create(True);
  fFileMask := aFileMask;
  fOlderThanHours := aOlderThanHours;
  fFailOnError := aFailOnError;
  FreeOnTerminate := false;
end;

procedure TPurgeFileThread.Execute;
var
  rDirInfo: TSearchRec;
  iResult, iError: integer;
  dtFileDate, dtNow, dtOlderThen: TDateTime;
  sFilePath, sErrMess: string;
begin
  iResult := 0;
  fResult := 0;
  dtNow := Now;
  dtOlderThen := fOlderThanHours / 24;
  sFilePath := ExtractFilePath(fFileMask);
  iError := FindFirst(fFileMask, faAnyFile, rDirInfo);
  while not Terminated and (iError = 0) do
  begin
    if (rDirInfo.Name <> '.') and (rDirInfo.Name <> '..') and (rDirInfo.Attr and faDirectory <> faDirectory) then
    begin
      dtFileDate := rDirInfo.TimeStamp;
      if dtNow - dtFileDate > dtOlderThen then
      begin
        if not DeleteFile(sFilePath + rDirInfo.Name) then
        begin
          if fFailOnError then
          begin
            sErrMess := 'PurgFiles - nieudana próba usunięcie pliku ' + #13#10 + sFilePath + rDirInfo.Name + #13#10#13#10 + SysErrorMessage(GetLastError);
            raise Exception.Create(sErrMess);
          end;
        end
        else
          Inc(iResult);
      end;
    end;
    iError := FindNext(rDirInfo);
  end;
  FindClose(rDirInfo);
  fResult := iResult;
end;

function CopyFileCallback(TotalFileSize, TotalBytesTransferred, StreamSize, StreamBytesTransferred: COMP; dwStreamNumber, dwCallbackReason: DWORD;
  hSourceFile, hDestinationFile: THandle; AProgressMeter: TObject): DWORD; stdcall;
var
  progress: integer;
begin
  progress := Round(TotalBytesTransferred / TotalFileSize * 100);
  if Assigned(AProgressMeter) then
    if AProgressMeter is TProgressBar then
      TProgressBar(AProgressMeter).Position := progress
    else if AProgressMeter is TGauge then
      TGauge(AProgressMeter).progress := progress;
  Result := PROGRESS_CONTINUE;
end;

procedure RemoveReadOnlyAttributeFromFile(AFilePath: String);
begin
  if TFile.Exists(AFilePath) then
    TFile.SetAttributes(AFilePath, TFile.GetAttributes(AFilePath) - [TFileAttribute.faReadOnly]);
end;

{$IFNDEF ISQLSCRIPTTOOL}
procedure RemoveReadOnlyAttributeFromDirectory(ADirectory: String);
var
  sFilePath: string;
begin
  if KMUtils.FolderExists(ADirectory) then
    for sFilePath in TDirectory.GetFiles(ADirectory, '*', TSearchOption.soAllDirectories) do
      RemoveReadOnlyAttributeFromFile(sFilePath);
end;
{$ENDIF}

end.
