object frameSFTPConn: TframeSFTPConn
  Left = 0
  Top = 0
  Width = 387
  Height = 180
  TabOrder = 0
  object PanLog: TPanel
    Left = 0
    Top = 0
    Width = 387
    Height = 152
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 0
    object Toolbar2: TToolBar
      Left = 0
      Top = 0
      Width = 387
      Height = 26
      ButtonHeight = 22
      ButtonWidth = 22
      Flat = True
      Images = imgListViews
      List = True
      ShowCaptions = True
      TabOrder = 0
      object tbSaveMess: TToolButton
        Left = 0
        Top = 0
        Caption = 'Save'
        ImageIndex = 0
        OnClick = tbSaveMessClick
      end
      object tbClear: TToolButton
        Left = 56
        Top = 0
        Caption = 'Clear'
        ImageIndex = 1
        OnClick = tbClearClick
      end
      object lPath: TLabel
        Left = 120
        Top = 4
        Width = 180
        Height = 18
        AutoSize = False
        Caption = ''
      end
      object LabCzas: TLabel
        Left = 310
        Top = 4
        Width = 70
        Height = 18
        Alignment = taRightJustify
        AutoSize = False
        Caption = ''
      end
    end
    object lvLog: TListView
      Left = 0
      Top = 26
      Width = 387
      Height = 126
      Align = alClient
      Columns = <
        item
          Caption = 'Timestamp'
          Width = 130
        end
        item
          Caption = 'Event'
          Width = 240
        end>
      ReadOnly = True
      RowSelect = True
      TabOrder = 1
      ViewStyle = vsReport
    end
  end
  object PB: TProgressBar
    Left = 0
    Top = 152
    Width = 387
    Height = 12
    Align = alBottom
    TabOrder = 1
  end
  object SB: TStatusBar
    Left = 0
    Top = 164
    Width = 387
    Height = 16
    Panels = <
      item
        Width = 80
      end
      item
        Width = 100
      end
      item
        Width = 100
      end
      item
        Width = 90
      end>
  end
  object MemoAck: TMemo
    Left = 0
    Top = 0
    Width = 387
    Height = 80
    Lines.Strings = (
      '')
    TabOrder = 2
    Visible = False
  end
  object imgListViews: TImageList
    ColorDepth = cd32Bit
    Left = 320
    Top = 140
    Bitmap = {
      4C000000010000001000100000000000}
  end
end
