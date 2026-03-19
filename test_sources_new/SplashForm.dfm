object frmSplash: TfrmSplash
  Left = 0
  Top = 0
  BorderStyle = bsNone
  Caption = 'FleetOps'
  ClientHeight = 500
  ClientWidth = 660
  Color = clWhite
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
  object Image1: TImage
    Left = 0
    Top = 0
    Width = 660
    Height = 500
    Align = alClient
    Center = True
    Stretch = True
    Picture.Data = {
      07544269746D617000000000424D360000000000000036000000280000000100
      0000010000000100180000000000000000000000000000000000000000000000
      FFFFFF00}
  end
  object lblVersion: TLabel
    Left = 480
    Top = 460
    Width = 160
    Height = 30
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Version 1.0.0'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGray
    Font.Height = -11
    Font.Name = 'Segoe UI'
    Font.Style = []
    ParentFont = False
  end
  object lblStatus: TLabel
    Left = 20
    Top = 460
    Width = 300
    Height = 30
    AutoSize = False
    Caption = 'Loading...'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clGray
    Font.Height = -11
    Font.Name = 'Segoe UI'
    Font.Style = []
    ParentFont = False
  end
  object pbLoad: TProgressBar
    Left = 0
    Top = 490
    Width = 660
    Height = 10
    Align = alBottom
    TabOrder = 0
  end
end
