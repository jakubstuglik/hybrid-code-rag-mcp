inherited frmMain: TfrmMain
  Left = 0
  Top = 0
  Caption = 'FleetOps - Fleet Management'
  ClientHeight = 768
  ClientWidth = 1366
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Segoe UI'
  Font.Style = []
  OldCreateOrder = False
  Position = poScreenCenter
  WindowState = wsMaximized
  OnClose = FormClose
  OnCreate = FormCreate
  OnDestroy = FormDestroy
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object pMainPanel: TPanel
    Left = 0
    Top = 0
    Width = 1366
    Height = 768
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 0
    object jvstbarMain: TJvStatusBar
      Left = 0
      Top = 749
      Width = 1366
      Height = 19
      Panels = <
        item
          Text = 'Ready'
          Width = 200
        end
        item
          Text = ''
          Width = 300
        end
        item
          Alignment = taCenter
          Text = ''
          Width = 80
        end
        item
          Alignment = taRightJustify
          Text = ''
          Width = 150
        end>
      object cbIdle: TCheckBox
        Left = 1200
        Top = 2
        Width = 155
        Height = 15
        Caption = 'Auto-logout in 30:00'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -9
        Font.Name = 'Segoe UI'
        Font.Style = []
        ParentFont = False
        TabOrder = 0
        OnClick = cbIdleClick
      end
    end
    object actmenubarMain: TActionMainMenuBar
      Left = 0
      Top = 0
      Width = 1366
      Height = 22
      ActionManager = actmgrMain
      ColorMap.HighlightColor = 15395562
      ColorMap.BtnSelectedColor = clBtnFace
      ColorMap.UnusedColor = 15395562
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -11
      Font.Name = 'Segoe UI'
      Font.Style = []
      Spacing = 0
    end
    object toolbarMain: TToolBar
      Left = 0
      Top = 22
      Width = 1366
      Height = 52
      AutoSize = True
      ButtonHeight = 24
      ButtonWidth = 72
      Caption = 'toolbarMain'
      EdgeBorders = [ebTop, ebBottom]
      Flat = True
      Images = imglLargeActDis
      ShowCaptions = True
      TabOrder = 1
      object ToolButton1: TToolButton
        Left = 0
        Top = 0
        Action = actVehicles
      end
      object ToolButton2: TToolButton
        Left = 72
        Top = 0
        Action = actDrivers
      end
      object ToolButton3: TToolButton
        Left = 144
        Top = 0
        Action = actJobs
      end
      object ToolButton4: TToolButton
        Left = 216
        Top = 0
        Action = actDispatch
      end
      object ToolButton5: TToolButton
        Left = 288
        Top = 0
        Style = tbsSeparator
        Width = 8
      end
      object ToolButton6: TToolButton
        Left = 296
        Top = 0
        Action = actReports
      end
      object ToolButton7: TToolButton
        Left = 368
        Top = 0
        Action = actScheduler
      end
      object ToolButton8: TToolButton
        Left = 440
        Top = 0
        Style = tbsSeparator
        Width = 8
      end
      object ToolButton9: TToolButton
        Left = 448
        Top = 0
        Action = actSettings
      end
      object ToolButton10: TToolButton
        Left = 520
        Top = 0
        Action = actHelp
      end
    end
    object pctrlMain: TPageControl
      Left = 0
      Top = 74
      Width = 1366
      Height = 675
      ActivePage = tsVehicles
      Align = alClient
      TabOrder = 2
      object tsVehicles: TTabSheet
        Caption = 'Vehicles'
        TabVisible = False
      end
      object tsDrivers: TTabSheet
        Caption = 'Drivers'
        TabVisible = False
      end
      object tsJobs: TTabSheet
        Caption = 'Jobs'
        TabVisible = False
      end
      object tsDispatch: TTabSheet
        Caption = 'Dispatch'
        TabVisible = False
      end
      object tsReports: TTabSheet
        Caption = 'Reports'
        TabVisible = False
      end
      object tsScheduler: TTabSheet
        Caption = 'Scheduler'
        TabVisible = False
      end
      object tsFuelRecords: TTabSheet
        Caption = 'Fuel Records'
        TabVisible = False
      end
      object tsServiceRecords: TTabSheet
        Caption = 'Service Records'
        TabVisible = False
      end
      object tsSettings: TTabSheet
        Caption = 'Settings'
        TabVisible = False
      end
      object tsAdmin: TTabSheet
        Caption = 'Administration'
        TabVisible = False
      end
    end
    object pFloatingPanel: TPanel
      Left = 800
      Top = 400
      Width = 400
      Height = 300
      BevelOuter = bvNone
      TabOrder = 3
      Visible = False
    end
  end
  object actmgrMain: TActionManager
    ActionBars = <
      item
        Items = <
          item
            Caption = '&File'
            Items = <
              item
                Action = actLogin
              end
              item
                Action = actLogout
              end
              item
                Caption = '-'
              end
              item
                Action = actExit
              end>
          end
          item
            Caption = '&Views'
            Items = <
              item
                Action = actVehicles
              end
              item
                Action = actDrivers
              end
              item
                Action = actJobs
              end
              item
                Action = actDispatch
              end>
          end
          item
            Caption = '&Help'
            Items = <
              item
                Action = actAbout
              end>
          end>
        ActionBar = actmenubarMain
      end>
    Images = imglLargeActDis
    Left = 32
    Top = 400
    object actLogin: TAction
      Category = 'File'
      Caption = 'Login'
      OnExecute = actLoginExecute
    end
    object actLogout: TAction
      Category = 'File'
      Caption = 'Logout'
      OnExecute = actLogoutExecute
    end
    object actExit: TAction
      Category = 'File'
      Caption = 'Exit'
      OnExecute = actExitExecute
    end
    object actVehicles: TAction
      Category = 'Views'
      Caption = 'Vehicles'
      Hint = 'Vehicle registry'
      ImageIndex = 0
      OnExecute = actVehiclesExecute
    end
    object actDrivers: TAction
      Category = 'Views'
      Caption = 'Drivers'
      Hint = 'Driver registry'
      ImageIndex = 1
      OnExecute = actDriversExecute
    end
    object actJobs: TAction
      Category = 'Views'
      Caption = 'Jobs'
      Hint = 'Job orders'
      ImageIndex = 2
      OnExecute = actJobsExecute
    end
    object actDispatch: TAction
      Category = 'Views'
      Caption = 'Dispatch'
      Hint = 'Dispatch console'
      ImageIndex = 3
      OnExecute = actDispatchExecute
    end
    object actReports: TAction
      Category = 'Views'
      Caption = 'Reports'
      Hint = 'Run reports'
      ImageIndex = 4
      OnExecute = actReportsExecute
    end
    object actScheduler: TAction
      Category = 'Views'
      Caption = 'Scheduler'
      Hint = 'Report scheduler'
      ImageIndex = 5
      OnExecute = actSchedulerExecute
    end
    object actSettings: TAction
      Category = 'Views'
      Caption = 'Settings'
      Hint = 'Application settings'
      ImageIndex = 6
      OnExecute = actSettingsExecute
    end
    object actAbout: TAction
      Category = 'Help'
      Caption = 'About FleetOps'
      OnExecute = actAboutExecute
    end
    object actHelp: TAction
      Category = 'Help'
      Caption = 'Help'
      ImageIndex = 7
      OnExecute = actHelpExecute
    end
  end
  object tmrLive: TTimer
    Enabled = False
    Interval = 1000
    OnTimer = tmrLiveTimer
    Left = 32
    Top = 440
  end
  object tmrIdle: TTimer
    Enabled = False
    Interval = 60000
    OnTimer = tmrIdleTimer
    Left = 32
    Top = 480
  end
  object tmrLogout: TTimer
    Enabled = False
    Interval = 1000
    OnTimer = tmrLogoutTimer
    Left = 32
    Top = 520
  end
  object imglErrorHint: TImageList
    ColorDepth = cd32Bit
    Left = 120
    Top = 440
  end
  object imglLargeActDis: TImageList
    ColorDepth = cd32Bit
    Height = 32
    Width = 32
    Left = 120
    Top = 480
    Bitmap = {
      4C000000010000002000200000000000}
  end
end
