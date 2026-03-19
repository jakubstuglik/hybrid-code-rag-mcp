object frameCoordEditor: TframeCoordEditor
  Left = 0
  Top = 0
  Width = 337
  Height = 111
  TabOrder = 0
  object lbLatitude: TLabel
    Left = 8
    Top = 8
    Width = 72
    Height = 13
    Caption = 'Latitude [#176]'
  end
  object lbLongitude: TLabel
    Left = 120
    Top = 8
    Width = 78
    Height = 13
    Caption = 'Longitude [#176]'
  end
  object lbAltitude: TLabel
    Left = 232
    Top = 8
    Width = 64
    Height = 13
    Caption = 'Altitude [m]'
  end
  object btnLatitude: TButton
    Left = 8
    Top = 72
    Width = 100
    Height = 25
    Caption = 'Pick Latitude'
    TabOrder = 0
    OnClick = btnLatitudeClick
  end
  object btnLongitude: TButton
    Left = 120
    Top = 72
    Width = 100
    Height = 25
    Caption = 'Pick Longitude'
    TabOrder = 1
    OnClick = btnLatitudeClick
  end
  object jvfsedLatitude: TJvSpinEdit
    Left = 8
    Top = 24
    Width = 100
    Height = 21
    Decimal = 13
    MaxValue = 90.000000000000000000
    MinValue = -90.000000000000000000
    TabOrder = 2
    Value = 0.000000000000000000
    ValueType = vtFloat
  end
  object jvfsedLongitude: TJvSpinEdit
    Left = 120
    Top = 24
    Width = 100
    Height = 21
    Decimal = 13
    MaxValue = 180.000000000000000000
    MinValue = -180.000000000000000000
    TabOrder = 3
    Value = 0.000000000000000000
    ValueType = vtFloat
  end
  object jvsedAltitude: TJvSpinEdit
    Left = 232
    Top = 24
    Width = 80
    Height = 21
    MaxValue = 10000.000000000000000000
    MinValue = 0.000000000000000000
    TabOrder = 4
    Value = 0.000000000000000000
  end
  object bitbtnClear: TBitBtn
    Left = 248
    Top = 72
    Width = 75
    Height = 25
    Caption = 'Clear'
    TabOrder = 5
    OnClick = bitbtnClearClick
    Glyph.Data = {
      36040000424D3604000000000000360000002800000010000000100000000100
      2000000000000004000000000000000000000000000000000000000000000000
      00000000}
  end
end
