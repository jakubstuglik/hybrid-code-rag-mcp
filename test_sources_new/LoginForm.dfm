object frmLogin: TfrmLogin
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Login'
  ClientHeight = 340
  ClientWidth = 500
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Segoe UI'
  Font.Style = []
  OldCreateOrder = False
  Position = poScreenCenter
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object pLeft: TPanel
    Left = 0
    Top = 0
    Width = 160
    Height = 340
    Align = alLeft
    BevelOuter = bvNone
    Color = 3355443
    ParentBackground = False
    TabOrder = 0
    object imgLogin: TImage
      Left = 20
      Top = 80
      Width = 120
      Height = 120
      Center = True
      Picture.Data = {
        07544269746D617000000000424D360000000000000036000000280000000100
        0000010000000100180000000000000000000000000000000000000000000000
        FFFFFF00}
      Stretch = True
    end
  end
  object pClient: TPanel
    Left = 160
    Top = 0
    Width = 340
    Height = 340
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 1
    object lbUsername: TLabel
      Left = 24
      Top = 80
      Width = 55
      Height = 13
      Caption = 'Username'
    end
    object lbPassword: TLabel
      Left = 24
      Top = 140
      Width = 49
      Height = 13
      Caption = 'Password'
    end
    object cbLogin: TComboBox
      Left = 24
      Top = 96
      Width = 292
      Height = 21
      Sorted = True
      TabOrder = 0
      OnChange = cbLoginChange
    end
    object edPassword: TEdit
      Left = 24
      Top = 156
      Width = 292
      Height = 21
      PasswordChar = '*'
      TabOrder = 1
      OnKeyDown = edPasswordKeyDown
    end
    object bitbtnOk: TBitBtn
      Left = 120
      Top = 220
      Width = 100
      Height = 30
      Caption = 'OK'
      Default = True
      Kind = bkOK
      ModalResult = 1
      TabOrder = 2
      OnClick = bitbtnOkClick
      Glyph.Data = {
        36040000424D3604000000000000360000002800000010000000100000000100
        2000000000000004000000000000000000000000000000000000000000000000
        00000000}
    end
    object bitbtnCancel: TBitBtn
      Left = 232
      Top = 220
      Width = 84
      Height = 30
      Caption = 'Cancel'
      Kind = bkCancel
      ModalResult = 2
      TabOrder = 3
    end
    object pMsgBox: TPanel
      Left = 24
      Top = 268
      Width = 292
      Height = 48
      BevelOuter = bvNone
      Color = 15138796
      ParentBackground = False
      TabOrder = 4
      Visible = False
      object lMessage: TLabel
        Left = 8
        Top = 8
        Width = 276
        Height = 32
        AutoSize = False
        Caption = ''
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clMaroon
        Font.Height = -11
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        WordWrap = True
      end
    end
  end
end
