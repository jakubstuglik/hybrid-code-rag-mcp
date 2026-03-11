inherited frameBusStandActionWizardStep1: TframeBusStandActionWizardStep1
  Width = 630
  Height = 358
  ExplicitWidth = 630
  ExplicitHeight = 358
  object lblName: TLabel
    Left = 0
    Top = 46
    Width = 120
    Height = 13
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Numer:'
  end
  object lblDescription: TLabel
    Left = 3
    Top = 73
    Width = 117
    Height = 13
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Uwagi:'
  end
  object lblDate: TLabel
    Left = 3
    Top = 100
    Width = 117
    Height = 13
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Data:'
  end
  object lblValidTo: TLabel
    Left = 3
    Top = 127
    Width = 117
    Height = 13
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Data wa'#380'no'#347'ci:'
  end
  object lblType: TLabel
    Left = 0
    Top = 19
    Width = 120
    Height = 13
    Alignment = taRightJustify
    AutoSize = False
    Caption = 'Typ:'
  end
  object edtName: TEdit
    Left = 121
    Top = 43
    Width = 221
    Height = 21
    TabOrder = 0
  end
  object edtDescription: TEdit
    Left = 121
    Top = 70
    Width = 445
    Height = 21
    TabOrder = 1
  end
  object dtpDate: TDateTimePicker
    Left = 121
    Top = 97
    Width = 101
    Height = 21
    Date = 41076.458061493060000000
    Time = 41076.458061493060000000
    TabOrder = 2
  end
  object dtpValidTo: TDateTimePicker
    Left = 121
    Top = 124
    Width = 101
    Height = 21
    Date = 41076.458061504630000000
    Time = 41076.458061504630000000
    ShowCheckbox = True
    Checked = False
    TabOrder = 3
  end
  object cbBusStandActionType: TComboBox
    Left = 121
    Top = 16
    Width = 221
    Height = 21
    Style = csDropDownList
    ParentShowHint = False
    ShowHint = True
    TabOrder = 4
  end
  object gbAdditionalActions: TGroupBox
    Left = 18
    Top = 146
    Width = 599
    Height = 198
    Caption = 'Konserwacja'
    TabOrder = 5
    object lvAction: TListView
      Left = 44
      Top = 15
      Width = 553
      Height = 181
      Align = alClient
      Columns = <
        item
          AutoSize = True
          Caption = 'Oznaczenie'
        end
        item
          Caption = 'Rodzaj'
          Width = 120
        end
        item
          Caption = 'Uwagi'
          Width = 120
        end
        item
          Caption = 'Data planowana'
          Width = 90
        end
        item
          Caption = 'Data wykonania'
          Width = 90
        end>
      GridLines = True
      ReadOnly = True
      RowSelect = True
      TabOrder = 0
      ViewStyle = vsReport
      OnEnter = lvActionEnter
      OnExit = lvActionExit
      OnSelectItem = lvActionSelectItem
    end
    object Panel2: TPanel
      Left = 2
      Top = 15
      Width = 42
      Height = 181
      Margins.Left = 5
      Margins.Top = 5
      Margins.Right = 5
      Margins.Bottom = 5
      Align = alLeft
      AutoSize = True
      BevelOuter = bvNone
      TabOrder = 1
      object ToolBar4: TToolBar
        AlignWithMargins = True
        Left = 5
        Top = 5
        Width = 32
        Height = 128
        Margins.Left = 5
        Margins.Top = 0
        Margins.Right = 5
        Margins.Bottom = 5
        Align = alNone
        AutoSize = True
        ButtonHeight = 32
        ButtonWidth = 32
        Caption = 'toolbarBase'
        DisabledImages = dmCommon.imglGlossaryBaseFrameDisable
        HotImages = dmCommon.imglGlossaryBaseFrameHot
        Images = dmCommon.imglGlossaryBaseFrame
        GradientDirection = gdHorizontal
        TabOrder = 0
        object btnAddDocumentAction: TToolButton
          Left = 0
          Top = 0
          Hint = 'Dodaj pozycj'#281
          ImageIndex = 5
          ParentShowHint = False
          Wrap = True
          ShowHint = True
          OnClick = btnAddDocumentActionClick
        end
        object btnDeleteDocumentAction: TToolButton
          Left = 0
          Top = 32
          Hint = 'Usu'#324' pozycj'#281
          ImageIndex = 6
          ParentShowHint = False
          Wrap = True
          ShowHint = True
          OnClick = btnDeleteDocumentActionClick
        end
        object btnEditDocumentAction: TToolButton
          Left = 0
          Top = 64
          Hint = 'Edytuj pozycj'#281
          ImageIndex = 7
          ParentShowHint = False
          Wrap = True
          ShowHint = True
          OnClick = btnEditDocumentActionClick
        end
        object btnPropertyDocumentAction: TToolButton
          Left = 0
          Top = 96
          Hint = 'W'#322'a'#347'ciwo'#347'ci pozycji'
          ImageIndex = 8
          ParentShowHint = False
          ShowHint = True
          OnClick = btnPropertyDocumentActionClick
        end
      end
    end
  end
end
