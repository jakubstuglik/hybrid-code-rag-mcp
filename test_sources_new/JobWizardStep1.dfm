inherited frameJobWizardStep1: TframeJobWizardStep1
  Width = 630
  Height = 358
  ExplicitWidth = 630
  ExplicitHeight = 358
  object lbJobType: TLabel
    Left = 8
    Top = 8
    Width = 49
    Height = 13
    Caption = 'Job Type'
  end
  object lbJobNumber: TLabel
    Left = 200
    Top = 8
    Width = 62
    Height = 13
    Caption = 'Job Number'
  end
  object lbNotes: TLabel
    Left = 8
    Top = 68
    Width = 30
    Height = 13
    Caption = 'Notes'
  end
  object lbScheduledDate: TLabel
    Left = 200
    Top = 68
    Width = 80
    Height = 13
    Caption = 'Scheduled Date'
  end
  object lbValidTo: TLabel
    Left = 400
    Top = 68
    Width = 37
    Height = 13
    Caption = 'Valid To'
  end
  object cbJobType: TComboBox
    Left = 8
    Top = 24
    Width = 180
    Height = 21
    Style = csDropDownList
    TabOrder = 0
  end
  object edtJobNumber: TEdit
    Left = 200
    Top = 24
    Width = 180
    Height = 21
    TabOrder = 1
  end
  object edtNotes: TEdit
    Left = 8
    Top = 84
    Width = 180
    Height = 21
    TabOrder = 2
  end
  object dtpScheduledDate: TDateTimePicker
    Left = 200
    Top = 84
    Width = 180
    Height = 21
    Date = 45000.000000000000000000
    Time = 45000.000000000000000000
    TabOrder = 3
  end
  object dtpValidTo: TDateTimePicker
    Left = 400
    Top = 84
    Width = 180
    Height = 21
    Date = 45000.000000000000000000
    ShowCheckbox = True
    Time = 45000.000000000000000000
    TabOrder = 4
  end
  object gbAdditionalStops: TGroupBox
    Left = 8
    Top = 120
    Width = 610
    Height = 220
    Caption = 'Additional Stops'
    TabOrder = 5
    object lvStops: TListView
      Left = 8
      Top = 48
      Width = 594
      Height = 160
      Columns = <
        item
          Caption = 'Stop'
          Width = 50
        end
        item
          Caption = 'Address'
          Width = 240
        end
        item
          Caption = 'ETA'
          Width = 100
        end
        item
          Caption = 'ATA'
          Width = 100
        end>
      ReadOnly = False
      RowSelect = True
      TabOrder = 0
      ViewStyle = vsReport
    end
    object ToolBar4: TToolBar
      Left = 8
      Top = 16
      Width = 594
      Height = 26
      ButtonHeight = 22
      ButtonWidth = 22
      Caption = 'ToolBar4'
      Flat = True
      Images = dmFleet.imglGlossaryBaseFrame
      List = True
      ShowCaptions = True
      TabOrder = 1
      object tbAddStop: TToolButton
        Left = 0
        Top = 0
        Caption = 'Add'
        ImageIndex = 0
        OnClick = tbAddStopClick
      end
      object tbDeleteStop: TToolButton
        Left = 44
        Top = 0
        Caption = 'Delete'
        ImageIndex = 1
        OnClick = tbDeleteStopClick
      end
      object tbEditStop: TToolButton
        Left = 100
        Top = 0
        Caption = 'Edit'
        ImageIndex = 2
        OnClick = tbEditStopClick
      end
    end
  end
end
