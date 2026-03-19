{$WARNINGS ON}
{$HINTS ON}
{$WARN UNIT_PLATFORM OFF}
{$WARN SYMBOL_PLATFORM OFF}
unit FileUtils;

// ============================================================================
// FileUtils.pas  –  File system utility functions for FleetOps
// Flat function library organised into regions.
// ============================================================================

interface

uses
  Windows, SysUtils, Classes, IOUtils, Math,
  System.Generics.Collections, System.Hash;

const
  CONST_1GB = 1073741824;
  CONST_1MB = 1048576;
  CONST_1KB = 1024;

// ── File Search ───────────────────────────────────────────────────────────────

function FindFiles(const ADir, AMask: string; ARecurse: Boolean;
  AList: TStringList): Integer;

function FindFilesOlderThan(const ADir: string; ADays: Integer;
  AList: TStringList): Integer;

function FindFilesLargerThan(const ADir: string; ASizeBytes: Int64;
  AList: TStringList): Integer;

function FindFilesByPattern(const ADir: string;
  const APatterns: array of string; AList: TStringList): Integer;

function FileExists2(const APath: string): Boolean;

function DirectoryExists2(const APath: string): Boolean;

function GetNewestFile(const ADir, AMask: string): string;

function GetOldestFile(const ADir, AMask: string): string;

function CountFiles(const ADir, AMask: string; ARecurse: Boolean): Integer;

function GetDirectorySize(const ADir: string): Int64;

// ── File Operations ───────────────────────────────────────────────────────────

function CopyFile2(const ASrc, ADst: string; AOverwrite: Boolean): Boolean;

function MoveFile2(const ASrc, ADst: string): Boolean;

function DeleteFile2(const APath: string): Boolean;

function DeleteOldFiles(const ADir: string; ADays: Integer): Integer;

procedure PurgeOldFiles(const ADir: string; AMaxAgeDays: Integer;
  ARecurse: Boolean);

function SafeDeleteFile(const APath: string): Boolean;

function BackupFile(const APath: string; const ABackupDir: string): string;

function RotateFile(const APath: string; AMaxBackups: Integer): Boolean;

function TruncateFile(const APath: string; AMaxBytes: Int64): Boolean;

function CreateDirectoryTree(const APath: string): Boolean;

function EmptyDirectory(const ADir: string; ARecurse: Boolean): Integer;

// ── File Reading / Writing ────────────────────────────────────────────────────

function ReadTextFile(const APath: string; out AContent: string): Boolean;

function WriteTextFile(const APath, AContent: string; AAppend: Boolean): Boolean;

function ReadLines(const APath: string; ALines: TStringList): Boolean;

function WriteLines(const APath: string; ALines: TStringList;
  AAppend: Boolean): Boolean;

function AppendLine(const APath, ALine: string): Boolean;

function ReadBinaryFile(const APath: string; out AData: TBytes): Boolean;

function WriteBinaryFile(const APath: string; const AData: TBytes): Boolean;

function ReadFirstNBytes(const APath: string; ACount: Integer): TBytes;

function GetFileEncoding(const APath: string): string;

function ConvertFileEncoding(const APath, AFromEnc, AToEnc: string): Boolean;

// ── Path Utilities ────────────────────────────────────────────────────────────

function NormalisePath(const APath: string): string;

function JoinPath(const AParts: array of string): string;

function GetRelativePath(const ABase, ATarget: string): string;

function GetAbsolutePath(const ARelative, ABase: string): string;

function SanitiseFilename(const AName: string): string;

function MakeUniqueFilename(const APath: string): string;

function GetFileExtension(const APath: string): string;

function ChangeFileExtension2(const APath, ANewExt: string): string;

function GetFileBaseName(const APath: string): string;

function GetParentDir(const APath: string): string;

function EnsureTrailingSlash(const APath: string): string;

function RemoveTrailingSlash(const APath: string): string;

// ── File Information ──────────────────────────────────────────────────────────

function GetFileSize2(const APath: string): Int64;

function GetFileCreatedDate(const APath: string): TDateTime;

function GetFileModifiedDate(const APath: string): TDateTime;

function GetFileOwner(const APath: string): string;

function IsFileReadOnly(const APath: string): Boolean;

function IsFileHidden(const APath: string): Boolean;

function IsFileOlderThan(const APath: string; ADays: Integer): Boolean;

function GetFileMd5(const APath: string): string;

function GetFileCrc32(const APath: string): Cardinal;

function FilesAreIdentical(const APath1, APath2: string): Boolean;

function GetDriveSpaceFree(const ADrive: string): Int64;

function GetDriveSpaceTotal(const ADrive: string): Int64;

// ── CSV Utilities ─────────────────────────────────────────────────────────────

function ParseCsvLine(const ALine: string; ADelimiter: Char): TStringList;

function BuildCsvLine(AFields: TStringList; ADelimiter: Char): string;

function ReadCsvFile(const APath: string;
  AData: TList<TStringList>; AHasHeader: Boolean): Integer;

function WriteCsvFile(const APath: string;
  AHeaders: TStringList; AData: TList<TStringList>): Boolean;

function QuoteCsvField(const AValue: string): string;

function UnquoteCsvField(const AValue: string): string;

// ── ZIP / Archive Utilities ───────────────────────────────────────────────────

function CompressFile(const ASrc, ADst: string): Boolean;

function DecompressFile(const ASrc, ADst: string): Boolean;

function AddToZip(const AZipPath, AFilePath, AEntryName: string): Boolean;

function ExtractFromZip(const AZipPath, AEntryName, ADestDir: string): Boolean;

function ListZipContents(const AZipPath: string; AList: TStringList): Integer;

// ── Temp File Utilities ───────────────────────────────────────────────────────

function GetTempFileName2(const APrefix, AExt: string): string;

function GetTempDir2: string;

procedure CleanTempFiles(const APrefix: string; AMaxAgeHours: Integer);

function CreateTempDir(const APrefix: string): string;

// ── Legacy helpers (from original FileUtils) ──────────────────────────────────

function  GetFileAgeHours(const aFileName: string): Double;
function  FormatFileSize(ABytes: Int64): string;
function  EnsurePathExists(const APath: string): Boolean;
function  MoveFileToArchive(const AFileName, AArchivePath: string;
            ACreateSubdirByDate: Boolean = True): Boolean;
function  IsFileLocked(const AFileName: string): Boolean;
procedure CopyFolderContents(const ASourceDir, ADestDir: string;
            ARecursive: Boolean = True);
function  GetDiskFreeSpaceGB(const ADrivePath: string): Double;

implementation

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'File Search'}
// ════════════════════════════════════════════════════════════════════════════

function FindFiles(const ADir, AMask: string; ARecurse: Boolean;
  AList: TStringList): Integer;
var
  sr: TSearchRec;
  dir: string;
begin
  Result := 0;
  dir    := IncludeTrailingPathDelimiter(ADir);

  // Enumerate matching files
  if FindFirst(dir + AMask, faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      AList.Add(dir + sr.Name);
      Inc(Result);
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;

  // Recurse into subdirectories
  if ARecurse then
  begin
    if FindFirst(dir + '*', faDirectory, sr) = 0 then
    try
      repeat
        if (sr.Name <> '.') and (sr.Name <> '..') and
           ((sr.Attr and faDirectory) <> 0) then
          Result := Result + FindFiles(dir + sr.Name, AMask, True, AList);
      until FindNext(sr) <> 0;
    finally
      FindClose(sr);
    end;
  end;
end;

function FindFilesOlderThan(const ADir: string; ADays: Integer;
  AList: TStringList): Integer;
var
  sr: TSearchRec;
  dir, fullPath: string;
  threshold: TDateTime;
begin
  Result    := 0;
  dir       := IncludeTrailingPathDelimiter(ADir);
  threshold := Now - ADays;

  if FindFirst(dir + '*', faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      fullPath := dir + sr.Name;
      if FileDateToDateTime(FileAge(fullPath)) < threshold then
      begin
        AList.Add(fullPath);
        Inc(Result);
      end;
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

function FindFilesLargerThan(const ADir: string; ASizeBytes: Int64;
  AList: TStringList): Integer;
var
  sr: TSearchRec;
  dir, fullPath: string;
  fileSize: Int64;
begin
  Result := 0;
  dir    := IncludeTrailingPathDelimiter(ADir);

  if FindFirst(dir + '*', faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      fullPath := dir + sr.Name;
      fileSize := Int64(sr.FindData.nFileSizeHigh) shl 32
                + Int64(sr.FindData.nFileSizeLow);
      if fileSize > ASizeBytes then
      begin
        AList.Add(fullPath);
        Inc(Result);
      end;
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

function FindFilesByPattern(const ADir: string;
  const APatterns: array of string; AList: TStringList): Integer;
var
  i: Integer;
  temp: TStringList;
begin
  Result := 0;
  temp   := TStringList.Create;
  try
    for i := Low(APatterns) to High(APatterns) do
    begin
      temp.Clear;
      Result := Result + FindFiles(ADir, APatterns[i], False, temp);
      AList.AddStrings(temp);
    end;
  finally
    temp.Free;
  end;
end;

function FileExists2(const APath: string): Boolean;
begin
  Result := SysUtils.FileExists(APath);
end;

function DirectoryExists2(const APath: string): Boolean;
begin
  Result := SysUtils.DirectoryExists(APath);
end;

function GetNewestFile(const ADir, AMask: string): string;
var
  sr: TSearchRec;
  dir, bestPath: string;
  bestAge, curAge: TDateTime;
begin
  Result   := '';
  bestPath := '';
  bestAge  := 0;
  dir      := IncludeTrailingPathDelimiter(ADir);

  if FindFirst(dir + AMask, faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      curAge := FileDateToDateTime(FileAge(dir + sr.Name));
      if curAge > bestAge then
      begin
        bestAge  := curAge;
        bestPath := dir + sr.Name;
      end;
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;

  Result := bestPath;
end;

function GetOldestFile(const ADir, AMask: string): string;
var
  sr: TSearchRec;
  dir, bestPath: string;
  bestAge, curAge: TDateTime;
begin
  Result   := '';
  bestPath := '';
  bestAge  := MaxDouble;
  dir      := IncludeTrailingPathDelimiter(ADir);

  if FindFirst(dir + AMask, faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      curAge := FileDateToDateTime(FileAge(dir + sr.Name));
      if curAge < bestAge then
      begin
        bestAge  := curAge;
        bestPath := dir + sr.Name;
      end;
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;

  Result := bestPath;
end;

function CountFiles(const ADir, AMask: string; ARecurse: Boolean): Integer;
var
  list: TStringList;
begin
  list := TStringList.Create;
  try
    Result := FindFiles(ADir, AMask, ARecurse, list);
  finally
    list.Free;
  end;
end;

function GetDirectorySize(const ADir: string): Int64;
var
  sr: TSearchRec;
  dir: string;
begin
  Result := 0;
  dir    := IncludeTrailingPathDelimiter(ADir);

  if FindFirst(dir + '*', faAnyFile, sr) = 0 then
  try
    repeat
      if (sr.Name = '.') or (sr.Name = '..') then Continue;
      if (sr.Attr and faDirectory) <> 0 then
        Result := Result + GetDirectorySize(dir + sr.Name)
      else
        Result := Result + Int64(sr.FindData.nFileSizeHigh) shl 32
                         + Int64(sr.FindData.nFileSizeLow);
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'File Operations'}
// ════════════════════════════════════════════════════════════════════════════

function CopyFile2(const ASrc, ADst: string; AOverwrite: Boolean): Boolean;
begin
  if not AOverwrite and FileExists(ADst) then
  begin
    Result := False;
    Exit;
  end;
  ForceDirectories(ExtractFilePath(ADst));
  Result := Windows.CopyFile(PChar(ASrc), PChar(ADst), not AOverwrite);
end;

function MoveFile2(const ASrc, ADst: string): Boolean;
begin
  ForceDirectories(ExtractFilePath(ADst));
  if FileExists(ADst) then
    SysUtils.DeleteFile(ADst);
  Result := Windows.MoveFile(PChar(ASrc), PChar(ADst));
end;

function DeleteFile2(const APath: string): Boolean;
begin
  Result := SysUtils.DeleteFile(APath);
end;

function DeleteOldFiles(const ADir: string; ADays: Integer): Integer;
var
  list: TStringList;
  i: Integer;
begin
  Result := 0;
  list   := TStringList.Create;
  try
    FindFilesOlderThan(ADir, ADays, list);
    for i := 0 to list.Count - 1 do
      if SafeDeleteFile(list[i]) then
        Inc(Result);
  finally
    list.Free;
  end;
end;

procedure PurgeOldFiles(const ADir: string; AMaxAgeDays: Integer;
  ARecurse: Boolean);
var
  sr: TSearchRec;
  dir, fullPath: string;
  threshold: TDateTime;
begin
  dir       := IncludeTrailingPathDelimiter(ADir);
  threshold := Now - AMaxAgeDays;

  if FindFirst(dir + '*', faAnyFile, sr) = 0 then
  try
    repeat
      if (sr.Name = '.') or (sr.Name = '..') then Continue;
      fullPath := dir + sr.Name;
      if (sr.Attr and faDirectory) <> 0 then
      begin
        if ARecurse then
          PurgeOldFiles(fullPath, AMaxAgeDays, True);
      end
      else
      begin
        if FileDateToDateTime(FileAge(fullPath)) < threshold then
          SafeDeleteFile(fullPath);
      end;
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

function SafeDeleteFile(const APath: string): Boolean;
var
  h: THandle;
begin
  Result := False;
  if not FileExists(APath) then Exit;
  // Check file is not locked
  h := CreateFile(PChar(APath), GENERIC_READ or GENERIC_WRITE,
    0, nil, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
  if h = INVALID_HANDLE_VALUE then Exit;
  CloseHandle(h);
  Result := SysUtils.DeleteFile(APath);
end;

function BackupFile(const APath: string; const ABackupDir: string): string;
var
  destDir, destFile, stamp, ext, base: string;
begin
  Result  := '';
  if not FileExists(APath) then Exit;

  stamp   := FormatDateTime('YYYYMMDD_HHNNSS', Now);
  ext     := ExtractFileExt(APath);
  base    := ChangeFileExt(ExtractFileName(APath), '');
  destDir := IncludeTrailingPathDelimiter(ABackupDir);

  if not ForceDirectories(destDir) then Exit;

  destFile := destDir + base + '_' + stamp + ext;
  if CopyFile2(APath, destFile, True) then
    Result := destFile;
end;

function RotateFile(const APath: string; AMaxBackups: Integer): Boolean;
var
  i: Integer;
  older, newer: string;
begin
  Result := False;
  if not FileExists(APath) then Exit;

  // Shift existing backups: .4 -> .5, .3 -> .4, etc.
  for i := AMaxBackups - 1 downto 1 do
  begin
    older := APath + '.' + IntToStr(i + 1);
    newer := APath + '.' + IntToStr(i);
    if FileExists(newer) then
    begin
      if FileExists(older) then SysUtils.DeleteFile(older);
      Windows.MoveFile(PChar(newer), PChar(older));
    end;
  end;

  // Move current to .1
  if FileExists(APath + '.1') then
    SysUtils.DeleteFile(APath + '.1');
  Result := Windows.MoveFile(PChar(APath), PChar(APath + '.1'));
end;

function TruncateFile(const APath: string; AMaxBytes: Int64): Boolean;
var
  fs: TFileStream;
begin
  Result := False;
  if not FileExists(APath) then Exit;
  if GetFileSize2(APath) <= AMaxBytes then
  begin
    Result := True;
    Exit;
  end;
  try
    fs := TFileStream.Create(APath, fmOpenWrite or fmShareDenyWrite);
    try
      fs.Size := AMaxBytes;
      Result  := True;
    finally
      fs.Free;
    end;
  except
    Result := False;
  end;
end;

function CreateDirectoryTree(const APath: string): Boolean;
begin
  Result := ForceDirectories(APath);
end;

function EmptyDirectory(const ADir: string; ARecurse: Boolean): Integer;
var
  sr: TSearchRec;
  dir, fullPath: string;
begin
  Result := 0;
  dir    := IncludeTrailingPathDelimiter(ADir);

  if FindFirst(dir + '*', faAnyFile, sr) = 0 then
  try
    repeat
      if (sr.Name = '.') or (sr.Name = '..') then Continue;
      fullPath := dir + sr.Name;
      if (sr.Attr and faDirectory) <> 0 then
      begin
        if ARecurse then
          Result := Result + EmptyDirectory(fullPath, True);
        RemoveDir(fullPath);
      end
      else if SafeDeleteFile(fullPath) then
        Inc(Result);
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'File Reading/Writing'}
// ════════════════════════════════════════════════════════════════════════════

function ReadTextFile(const APath: string; out AContent: string): Boolean;
var
  sl: TStringList;
begin
  Result := False;
  if not FileExists(APath) then Exit;
  sl := TStringList.Create;
  try
    sl.LoadFromFile(APath, TEncoding.UTF8);
    AContent := sl.Text;
    Result   := True;
  except
    AContent := '';
  end;
  sl.Free;
end;

function WriteTextFile(const APath, AContent: string;
  AAppend: Boolean): Boolean;
var
  sl: TStringList;
  existing: string;
begin
  Result := False;
  try
    ForceDirectories(ExtractFilePath(APath));
    sl := TStringList.Create;
    try
      if AAppend and FileExists(APath) then
        sl.LoadFromFile(APath, TEncoding.UTF8);
      if AContent <> '' then
        sl.Text := sl.Text + AContent;
      sl.SaveToFile(APath, TEncoding.UTF8);
      Result := True;
    finally
      sl.Free;
    end;
  except
    Result := False;
  end;
  existing := ''; // suppress unused hint
end;

function ReadLines(const APath: string; ALines: TStringList): Boolean;
begin
  Result := False;
  if not FileExists(APath) then Exit;
  try
    ALines.LoadFromFile(APath, TEncoding.UTF8);
    Result := True;
  except
    Result := False;
  end;
end;

function WriteLines(const APath: string; ALines: TStringList;
  AAppend: Boolean): Boolean;
var
  existing: TStringList;
begin
  Result := False;
  try
    ForceDirectories(ExtractFilePath(APath));
    if AAppend and FileExists(APath) then
    begin
      existing := TStringList.Create;
      try
        existing.LoadFromFile(APath, TEncoding.UTF8);
        existing.AddStrings(ALines);
        existing.SaveToFile(APath, TEncoding.UTF8);
      finally
        existing.Free;
      end;
    end
    else
      ALines.SaveToFile(APath, TEncoding.UTF8);
    Result := True;
  except
    Result := False;
  end;
end;

function AppendLine(const APath, ALine: string): Boolean;
var
  fs: TFileStream;
  bytes: TBytes;
  line: string;
begin
  Result := False;
  try
    ForceDirectories(ExtractFilePath(APath));
    line  := ALine + sLineBreak;
    bytes := TEncoding.UTF8.GetBytes(line);
    fs    := TFileStream.Create(APath,
      IfThen(FileExists(APath), fmOpenWrite, fmCreate) or fmShareDenyWrite);
    try
      fs.Seek(0, soEnd);
      fs.WriteBuffer(bytes[0], Length(bytes));
      Result := True;
    finally
      fs.Free;
    end;
  except
    Result := False;
  end;
end;

function ReadBinaryFile(const APath: string; out AData: TBytes): Boolean;
var
  fs: TFileStream;
begin
  Result := False;
  AData  := nil;
  if not FileExists(APath) then Exit;
  try
    fs := TFileStream.Create(APath, fmOpenRead or fmShareDenyNone);
    try
      SetLength(AData, fs.Size);
      if fs.Size > 0 then
        fs.ReadBuffer(AData[0], fs.Size);
      Result := True;
    finally
      fs.Free;
    end;
  except
    AData := nil;
  end;
end;

function WriteBinaryFile(const APath: string; const AData: TBytes): Boolean;
var
  fs: TFileStream;
begin
  Result := False;
  try
    ForceDirectories(ExtractFilePath(APath));
    fs := TFileStream.Create(APath, fmCreate or fmShareDenyWrite);
    try
      if Length(AData) > 0 then
        fs.WriteBuffer(AData[0], Length(AData));
      Result := True;
    finally
      fs.Free;
    end;
  except
    Result := False;
  end;
end;

function ReadFirstNBytes(const APath: string; ACount: Integer): TBytes;
var
  fs: TFileStream;
  toRead: Integer;
begin
  Result := nil;
  if not FileExists(APath) then Exit;
  try
    fs     := TFileStream.Create(APath, fmOpenRead or fmShareDenyNone);
    toRead := Min(ACount, fs.Size);
    try
      SetLength(Result, toRead);
      if toRead > 0 then
        fs.ReadBuffer(Result[0], toRead);
    finally
      fs.Free;
    end;
  except
    Result := nil;
  end;
end;

function GetFileEncoding(const APath: string): string;
var
  bom: TBytes;
begin
  Result := 'ANSI';
  bom    := ReadFirstNBytes(APath, 4);
  if Length(bom) >= 3 then
  begin
    if (bom[0] = $EF) and (bom[1] = $BB) and (bom[2] = $BF) then
    begin
      Result := 'UTF-8';
      Exit;
    end;
  end;
  if Length(bom) >= 2 then
  begin
    if (bom[0] = $FF) and (bom[1] = $FE) then
    begin
      Result := 'UTF-16LE';
      Exit;
    end;
    if (bom[0] = $FE) and (bom[1] = $FF) then
    begin
      Result := 'UTF-16BE';
      Exit;
    end;
  end;
end;

function ConvertFileEncoding(const APath, AFromEnc, AToEnc: string): Boolean;
var
  srcEnc, dstEnc: TEncoding;
  raw: TBytes;
  content: string;
begin
  Result := False;
  if not ReadBinaryFile(APath, raw) then Exit;
  try
    if SameText(AFromEnc, 'UTF-8') then srcEnc := TEncoding.UTF8
    else if SameText(AFromEnc, 'UTF-16LE') then srcEnc := TEncoding.Unicode
    else srcEnc := TEncoding.Default;

    if SameText(AToEnc, 'UTF-8') then dstEnc := TEncoding.UTF8
    else if SameText(AToEnc, 'UTF-16LE') then dstEnc := TEncoding.Unicode
    else dstEnc := TEncoding.Default;

    content := srcEnc.GetString(raw);
    raw     := dstEnc.GetBytes(content);
    Result  := WriteBinaryFile(APath, raw);
  except
    Result := False;
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'Path Utilities'}
// ════════════════════════════════════════════════════════════════════════════

function NormalisePath(const APath: string): string;
begin
  Result := StringReplace(APath, '/', '\', [rfReplaceAll]);
  while Pos('\\', Result) > 0 do
    Result := StringReplace(Result, '\\', '\', [rfReplaceAll]);
end;

function JoinPath(const AParts: array of string): string;
var
  i: Integer;
begin
  Result := '';
  for i := Low(AParts) to High(AParts) do
  begin
    if Result = '' then
      Result := AParts[i]
    else
      Result := IncludeTrailingPathDelimiter(Result) + AParts[i];
  end;
  Result := NormalisePath(Result);
end;

function GetRelativePath(const ABase, ATarget: string): string;
var
  base, target: string;
  i, commonLen: Integer;
  dotDots: string;
begin
  base   := IncludeTrailingPathDelimiter(ExpandFileName(ABase));
  target := ExpandFileName(ATarget);
  commonLen := 0;

  for i := 1 to Min(Length(base), Length(target)) do
    if SameText(base[i], target[i]) then
      commonLen := i
    else
      Break;

  // Count directory separators after common prefix in base
  dotDots := '';
  for i := commonLen + 1 to Length(base) do
    if base[i] = '\' then
      dotDots := dotDots + '..\';

  Result := dotDots + Copy(target, commonLen + 1, MaxInt);
  if Result = '' then Result := '.';
end;

function GetAbsolutePath(const ARelative, ABase: string): string;
begin
  if TPath.IsPathRooted(ARelative) then
    Result := ARelative
  else
    Result := ExpandFileName(
      IncludeTrailingPathDelimiter(ABase) + ARelative);
end;

function SanitiseFilename(const AName: string): string;
const
  INVALID_CHARS = '/\:*?"<>|';
var
  i: Integer;
begin
  Result := AName;
  for i := 1 to Length(INVALID_CHARS) do
    Result := StringReplace(Result, INVALID_CHARS[i], '_', [rfReplaceAll]);
  Result := Trim(Result);
  // Remove leading/trailing dots
  while (Length(Result) > 0) and (Result[1] = '.') do
    Delete(Result, 1, 1);
  while (Length(Result) > 0) and (Result[Length(Result)] = '.') do
    Delete(Result, Length(Result), 1);
end;

function MakeUniqueFilename(const APath: string): string;
var
  base, ext, dir: string;
  counter: Integer;
begin
  if not FileExists(APath) then
  begin
    Result := APath;
    Exit;
  end;
  dir     := ExtractFilePath(APath);
  base    := ChangeFileExt(ExtractFileName(APath), '');
  ext     := ExtractFileExt(APath);
  counter := 1;
  repeat
    Result := dir + base + '_' + IntToStr(counter) + ext;
    Inc(counter);
  until not FileExists(Result);
end;

function GetFileExtension(const APath: string): string;
begin
  Result := LowerCase(ExtractFileExt(APath));
end;

function ChangeFileExtension2(const APath, ANewExt: string): string;
begin
  Result := ChangeFileExt(APath, ANewExt);
end;

function GetFileBaseName(const APath: string): string;
begin
  Result := ChangeFileExt(ExtractFileName(APath), '');
end;

function GetParentDir(const APath: string): string;
begin
  Result := ExcludeTrailingPathDelimiter(
    ExtractFilePath(ExcludeTrailingPathDelimiter(APath)));
end;

function EnsureTrailingSlash(const APath: string): string;
begin
  Result := IncludeTrailingPathDelimiter(APath);
end;

function RemoveTrailingSlash(const APath: string): string;
begin
  Result := ExcludeTrailingPathDelimiter(APath);
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'File Information'}
// ════════════════════════════════════════════════════════════════════════════

function GetFileSize2(const APath: string): Int64;
var
  sr: TSearchRec;
begin
  Result := -1;
  if FindFirst(APath, faAnyFile, sr) = 0 then
  begin
    Result := Int64(sr.FindData.nFileSizeHigh) shl 32
            + Int64(sr.FindData.nFileSizeLow);
    FindClose(sr);
  end;
end;

function GetFileCreatedDate(const APath: string): TDateTime;
var
  sr: TSearchRec;
begin
  Result := 0;
  if FindFirst(APath, faAnyFile, sr) = 0 then
  begin
    Result := FileTimeToDateTime(sr.FindData.ftCreationTime);
    FindClose(sr);
  end;
end;

function GetFileModifiedDate(const APath: string): TDateTime;
begin
  Result := FileDateToDateTime(FileAge(APath));
end;

function GetFileOwner(const APath: string): string;
var
  sd: PSecurityDescriptor;
  owner: PSID;
  defaulted: BOOL;
  name, domain: array[0..255] of Char;
  nameLen, domainLen: DWORD;
  sidType: SID_NAME_USE;
begin
  Result := '';
  if not GetFileSecurity(PChar(APath), OWNER_SECURITY_INFORMATION,
    nil, 0, PDWORD(@nameLen)) then ;
  sd := GetMemory(nameLen);
  try
    if GetFileSecurity(PChar(APath), OWNER_SECURITY_INFORMATION,
      sd, nameLen, PDWORD(@nameLen)) then
    begin
      if GetSecurityDescriptorOwner(sd, owner, defaulted) then
      begin
        nameLen   := 255;
        domainLen := 255;
        if LookupAccountSid(nil, owner, name, nameLen, domain, domainLen, sidType) then
          Result := string(domain) + '\' + string(name);
      end;
    end;
  finally
    FreeMemory(sd);
  end;
end;

function IsFileReadOnly(const APath: string): Boolean;
begin
  Result := (GetFileAttributes(PChar(APath)) and FILE_ATTRIBUTE_READONLY) <> 0;
end;

function IsFileHidden(const APath: string): Boolean;
begin
  Result := (GetFileAttributes(PChar(APath)) and FILE_ATTRIBUTE_HIDDEN) <> 0;
end;

function IsFileOlderThan(const APath: string; ADays: Integer): Boolean;
var
  modified: TDateTime;
begin
  modified := GetFileModifiedDate(APath);
  Result   := (modified > 0) and ((Now - modified) > ADays);
end;

function GetFileMd5(const APath: string): string;
var
  data: TBytes;
begin
  Result := '';
  if not ReadBinaryFile(APath, data) then Exit;
  if Length(data) = 0 then Exit;
  Result := THashMD5.GetHashStringFromBytes(data);
end;

function GetFileCrc32(const APath: string): Cardinal;
var
  fs: TFileStream;
  buf: array[0..65535] of Byte;
  read: Integer;
  crc: Cardinal;
  i: Integer;
  poly: Cardinal;
const
  POLY = $EDB88320;
begin
  Result := 0;
  if not FileExists(APath) then Exit;

  // Build CRC32 table on-the-fly for one byte
  crc  := $FFFFFFFF;
  poly := POLY;

  fs := TFileStream.Create(APath, fmOpenRead or fmShareDenyNone);
  try
    repeat
      read := fs.Read(buf, SizeOf(buf));
      for i := 0 to read - 1 do
      begin
        crc := crc xor buf[i];
        for var b := 0 to 7 do
          if (crc and 1) <> 0 then
            crc := (crc shr 1) xor poly
          else
            crc := crc shr 1;
      end;
    until read = 0;
  finally
    fs.Free;
  end;
  Result := crc xor $FFFFFFFF;
end;

function FilesAreIdentical(const APath1, APath2: string): Boolean;
var
  size1, size2: Int64;
  fs1, fs2: TFileStream;
  buf1, buf2: array[0..65535] of Byte;
  read1, read2: Integer;
begin
  Result := False;
  size1  := GetFileSize2(APath1);
  size2  := GetFileSize2(APath2);
  if size1 <> size2 then Exit;
  if size1 = 0 then
  begin
    Result := True;
    Exit;
  end;

  fs1 := TFileStream.Create(APath1, fmOpenRead or fmShareDenyNone);
  fs2 := TFileStream.Create(APath2, fmOpenRead or fmShareDenyNone);
  try
    repeat
      read1 := fs1.Read(buf1, SizeOf(buf1));
      read2 := fs2.Read(buf2, SizeOf(buf2));
      if read1 <> read2 then Exit;
      if not CompareMem(@buf1, @buf2, read1) then Exit;
    until read1 = 0;
    Result := True;
  finally
    fs1.Free;
    fs2.Free;
  end;
end;

function GetDriveSpaceFree(const ADrive: string): Int64;
var
  freeToCaller, total, free: Int64;
begin
  Result := 0;
  if GetDiskFreeSpaceEx(PChar(ADrive),
    ULARGE_INTEGER(freeToCaller),
    ULARGE_INTEGER(total),
    @ULARGE_INTEGER(free)) then
    Result := free;
end;

function GetDriveSpaceTotal(const ADrive: string): Int64;
var
  freeToCaller, total, free: Int64;
begin
  Result := 0;
  if GetDiskFreeSpaceEx(PChar(ADrive),
    ULARGE_INTEGER(freeToCaller),
    ULARGE_INTEGER(total),
    @ULARGE_INTEGER(free)) then
    Result := total;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'CSV Utilities'}
// ════════════════════════════════════════════════════════════════════════════

function ParseCsvLine(const ALine: string; ADelimiter: Char): TStringList;
var
  i: Integer;
  inQuotes: Boolean;
  current: string;
  ch: Char;
begin
  Result   := TStringList.Create;
  inQuotes := False;
  current  := '';

  for i := 1 to Length(ALine) do
  begin
    ch := ALine[i];
    if ch = '"' then
    begin
      if inQuotes and (i < Length(ALine)) and (ALine[i + 1] = '"') then
        current := current + '"'   // escaped quote
      else
        inQuotes := not inQuotes;
    end
    else if (ch = ADelimiter) and not inQuotes then
    begin
      Result.Add(current);
      current := '';
    end
    else
      current := current + ch;
  end;
  Result.Add(current);
end;

function BuildCsvLine(AFields: TStringList; ADelimiter: Char): string;
var
  i: Integer;
  sb: TStringBuilder;
begin
  sb := TStringBuilder.Create;
  try
    for i := 0 to AFields.Count - 1 do
    begin
      if i > 0 then sb.Append(ADelimiter);
      sb.Append(QuoteCsvField(AFields[i]));
    end;
    Result := sb.ToString;
  finally
    sb.Free;
  end;
end;

function ReadCsvFile(const APath: string;
  AData: TList<TStringList>; AHasHeader: Boolean): Integer;
var
  lines, fields: TStringList;
  i: Integer;
begin
  Result := 0;
  lines  := TStringList.Create;
  try
    if not ReadLines(APath, lines) then Exit;
    for i := IfThen(AHasHeader, 1, 0) to lines.Count - 1 do
    begin
      if Trim(lines[i]) = '' then Continue;
      fields := ParseCsvLine(lines[i], ',');
      AData.Add(fields);
      Inc(Result);
    end;
  finally
    lines.Free;
  end;
end;

function WriteCsvFile(const APath: string;
  AHeaders: TStringList; AData: TList<TStringList>): Boolean;
var
  lines: TStringList;
  i: Integer;
begin
  Result := False;
  lines  := TStringList.Create;
  try
    if Assigned(AHeaders) and (AHeaders.Count > 0) then
      lines.Add(BuildCsvLine(AHeaders, ','));
    for i := 0 to AData.Count - 1 do
      lines.Add(BuildCsvLine(AData[i], ','));
    Result := WriteLines(APath, lines, False);
  finally
    lines.Free;
  end;
end;

function QuoteCsvField(const AValue: string): string;
var
  needsQuoting: Boolean;
begin
  needsQuoting := (Pos(',', AValue) > 0) or (Pos('"', AValue) > 0)
               or (Pos(#10, AValue) > 0) or (Pos(#13, AValue) > 0);
  if needsQuoting then
    Result := '"' + StringReplace(AValue, '"', '""', [rfReplaceAll]) + '"'
  else
    Result := AValue;
end;

function UnquoteCsvField(const AValue: string): string;
begin
  Result := AValue;
  if (Length(Result) >= 2) and (Result[1] = '"') and
     (Result[Length(Result)] = '"') then
  begin
    Result := Copy(Result, 2, Length(Result) - 2);
    Result := StringReplace(Result, '""', '"', [rfReplaceAll]);
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'ZIP/Archive Utilities'}
// ════════════════════════════════════════════════════════════════════════════

function CompressFile(const ASrc, ADst: string): Boolean;
var
  zip: TZipFile;
begin
  Result := False;
  if not FileExists(ASrc) then Exit;
  try
    ForceDirectories(ExtractFilePath(ADst));
    zip := TZipFile.Create;
    try
      zip.Open(ADst, zmWrite);
      zip.Add(ASrc, ExtractFileName(ASrc));
      zip.Close;
      Result := True;
    finally
      zip.Free;
    end;
  except
    Result := False;
  end;
end;

function DecompressFile(const ASrc, ADst: string): Boolean;
var
  zip: TZipFile;
begin
  Result := False;
  if not FileExists(ASrc) then Exit;
  try
    ForceDirectories(ADst);
    zip := TZipFile.Create;
    try
      zip.Open(ASrc, zmRead);
      zip.ExtractAll(ADst);
      zip.Close;
      Result := True;
    finally
      zip.Free;
    end;
  except
    Result := False;
  end;
end;

function AddToZip(const AZipPath, AFilePath, AEntryName: string): Boolean;
var
  zip: TZipFile;
  mode: TZipMode;
begin
  Result := False;
  if not FileExists(AFilePath) then Exit;
  try
    mode := IfThen(FileExists(AZipPath), zmReadWrite, zmWrite);
    zip  := TZipFile.Create;
    try
      zip.Open(AZipPath, mode);
      zip.Add(AFilePath, AEntryName);
      zip.Close;
      Result := True;
    finally
      zip.Free;
    end;
  except
    Result := False;
  end;
end;

function ExtractFromZip(const AZipPath, AEntryName, ADestDir: string): Boolean;
var
  zip: TZipFile;
begin
  Result := False;
  if not FileExists(AZipPath) then Exit;
  try
    ForceDirectories(ADestDir);
    zip := TZipFile.Create;
    try
      zip.Open(AZipPath, zmRead);
      zip.Extract(AEntryName, ADestDir);
      zip.Close;
      Result := True;
    finally
      zip.Free;
    end;
  except
    Result := False;
  end;
end;

function ListZipContents(const AZipPath: string; AList: TStringList): Integer;
var
  zip: TZipFile;
  i: Integer;
begin
  Result := 0;
  if not FileExists(AZipPath) then Exit;
  try
    zip := TZipFile.Create;
    try
      zip.Open(AZipPath, zmRead);
      for i := 0 to zip.FileCount - 1 do
      begin
        AList.Add(zip.FileName[i]);
        Inc(Result);
      end;
      zip.Close;
    finally
      zip.Free;
    end;
  except
    Result := 0;
  end;
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'Temp File Utilities'}
// ════════════════════════════════════════════════════════════════════════════

function GetTempDir2: string;
begin
  Result := IncludeTrailingPathDelimiter(TPath.GetTempPath);
end;

function GetTempFileName2(const APrefix, AExt: string): string;
var
  stamp: string;
  counter: Integer;
begin
  stamp   := FormatDateTime('YYYYMMDD_HHNNSS', Now);
  counter := 0;
  repeat
    if counter = 0 then
      Result := GetTempDir2 + APrefix + '_' + stamp + AExt
    else
      Result := GetTempDir2 + APrefix + '_' + stamp + '_' +
                IntToStr(counter) + AExt;
    Inc(counter);
  until not FileExists(Result);
end;

procedure CleanTempFiles(const APrefix: string; AMaxAgeHours: Integer);
var
  sr: TSearchRec;
  dir, fullPath: string;
  threshold: TDateTime;
begin
  dir       := GetTempDir2;
  threshold := Now - (AMaxAgeHours / 24.0);

  if FindFirst(dir + APrefix + '*', faAnyFile - faDirectory, sr) = 0 then
  try
    repeat
      fullPath := dir + sr.Name;
      if FileDateToDateTime(FileAge(fullPath)) < threshold then
        SafeDeleteFile(fullPath);
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

function CreateTempDir(const APrefix: string): string;
var
  stamp: string;
  counter: Integer;
begin
  stamp   := FormatDateTime('YYYYMMDD_HHNNSS', Now);
  counter := 0;
  repeat
    if counter = 0 then
      Result := GetTempDir2 + APrefix + '_' + stamp
    else
      Result := GetTempDir2 + APrefix + '_' + stamp + '_' + IntToStr(counter);
    Inc(counter);
  until not DirectoryExists(Result);
  ForceDirectories(Result);
end;

// ════════════════════════════════════════════════════════════════════════════
// {$REGION 'Legacy helpers (from original FileUtils)'}
// ════════════════════════════════════════════════════════════════════════════

function GetFileAgeHours(const aFileName: string): Double;
var
  age: TDateTime;
begin
  age    := FileDateToDateTime(FileAge(aFileName));
  Result := (Now - age) * 24;
end;

function FormatFileSize(ABytes: Int64): string;
begin
  if ABytes >= CONST_1GB then
    Result := Format('%.2f GB', [ABytes / CONST_1GB])
  else if ABytes >= CONST_1MB then
    Result := Format('%.2f MB', [ABytes / CONST_1MB])
  else if ABytes >= CONST_1KB then
    Result := Format('%.2f KB', [ABytes / CONST_1KB])
  else
    Result := IntToStr(ABytes) + ' bytes';
end;

function EnsurePathExists(const APath: string): Boolean;
begin
  Result := ForceDirectories(APath);
end;

function MoveFileToArchive(const AFileName, AArchivePath: string;
  ACreateSubdirByDate: Boolean): Boolean;
var
  destDir, destFile: string;
begin
  destDir := AArchivePath;
  if ACreateSubdirByDate then
    destDir := IncludeTrailingPathDelimiter(AArchivePath) +
               FormatDateTime('YYYY-MM-DD', Now);

  EnsurePathExists(destDir);
  destFile := IncludeTrailingPathDelimiter(destDir) + ExtractFileName(AFileName);
  Result   := Windows.MoveFile(PChar(AFileName), PChar(destFile));
end;

function IsFileLocked(const AFileName: string): Boolean;
var
  h: THandle;
begin
  h := CreateFile(PChar(AFileName), GENERIC_READ or GENERIC_WRITE, 0, nil,
    OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
  Result := (h = INVALID_HANDLE_VALUE);
  if not Result then
    CloseHandle(h);
end;

procedure CopyFolderContents(const ASourceDir, ADestDir: string;
  ARecursive: Boolean);
var
  sr: TSearchRec;
  srcFile, destFile: string;
  src: string;
begin
  src := IncludeTrailingPathDelimiter(ASourceDir);
  EnsurePathExists(ADestDir);

  if FindFirst(src + '*', faAnyFile, sr) = 0 then
  try
    repeat
      if sr.Name[1] = '.' then Continue;
      srcFile  := src + sr.Name;
      destFile := IncludeTrailingPathDelimiter(ADestDir) + sr.Name;
      if (sr.Attr and faDirectory) > 0 then
      begin
        if ARecursive then
          CopyFolderContents(srcFile, destFile, True);
      end
      else
        Windows.CopyFile(PChar(srcFile), PChar(destFile), False);
    until FindNext(sr) <> 0;
  finally
    FindClose(sr);
  end;
end;

function GetDiskFreeSpaceGB(const ADrivePath: string): Double;
var
  freeBytesToCaller, totalBytes, freeBytes: Int64;
begin
  Result := 0;
  if GetDiskFreeSpaceEx(PChar(ADrivePath),
    ULARGE_INTEGER(freeBytesToCaller),
    ULARGE_INTEGER(totalBytes),
    @ULARGE_INTEGER(freeBytes)) then
    Result := freeBytes / CONST_1GB;
end;

end.
