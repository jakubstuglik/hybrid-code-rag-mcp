object dmMain: TdmMain
  OldCreateOrder = False
  OnCreate = DataModuleCreate
  OnDestroy = DataModuleDestroy
  Height = 1326
  Width = 1287
  object cdsStoredProcCustom1: TClientDataSet
    Tag = 1
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom1'
    RemoteServer = DSProviderConnection
    Left = 165
    Top = 144
  end
  object cdsStoredProcCustom2: TClientDataSet
    Tag = 2
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom2'
    RemoteServer = DSProviderConnection
    Left = 165
    Top = 184
  end
  object cdsStoredProcCustom3: TClientDataSet
    Tag = 3
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom3'
    RemoteServer = DSProviderConnection
    Left = 165
    Top = 232
  end
  object SQLConnection: TSQLConnection
    DriverName = 'Datasnap'
    LoginPrompt = False
    Params.Strings = (
      'CommunicationProtocol=https'
      'HostName=localhost'
      'Port=211'
      'DatasnapContext=api/'
      
        'DriverAssemblyLoader=Borland.Data.TDBXClientDriverLoader,Borland' +
        '.Data.DbxClientDriver,Version=23.0.0.0,Culture=neutral,PublicKey' +
        'Token=91d62ebb5b0d1b1b'
      'DriverUnit=DBXDataSnap'
      'Filters={}'
      'CommunicationIPVersion=IP_IPv4')
    ValidatePeerCertificate = SQLConnectionValidatePeerCertificate
    Left = 37
    Top = 12
    UniqueId = '{247871FB-CA86-4219-889C-36E1CC981EAA}'
  end
  object DSProviderConnection: TDSProviderConnection
    ServerClassName = 'informicaapp'
    SQLConnection = SQLConnection
    Left = 61
    Top = 99
  end
  object cdsStoredProcAdmin_Log: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderADmin_Log'
    RemoteServer = DSProviderConnection
    Left = 577
    Top = 32
  end
  object cdsCommitAndResult: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsCommitAndResult'
    RemoteServer = DSProviderConnection
    Left = 193
    Top = 24
  end
  object cdsStoredProcBasicSearch: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBasicSearch'
    RemoteServer = DSProviderConnection
    Left = 280
    Top = 176
  end
  object cdsStoredProcProvinces: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderProvinces'
    RemoteServer = DSProviderConnection
    Left = 656
    Top = 231
  end
  object cdsStoredProcRoads: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRoads'
    RemoteServer = DSProviderConnection
    Left = 1184
    Top = 112
  end
  object cdsStoredProcPlaces: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPlaces'
    RemoteServer = DSProviderConnection
    Left = 381
    Top = 105
  end
  object cdsStoredProcCountries: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCountries'
    RemoteServer = DSProviderConnection
    Left = 600
    Top = 370
  end
  object cdsStoredProcDistricts: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderDistricts'
    RemoteServer = DSProviderConnection
    Left = 468
    Top = 60
  end
  object cdsStoredProcBoroughs: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBoroughs'
    RemoteServer = DSProviderConnection
    Left = 597
    Top = 183
  end
  object cdsStoredProcRoadPoints: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRoadPoints'
    RemoteServer = DSProviderConnection
    Left = 278
    Top = 233
  end
  object cdsBusStopStands: TClientDataSet
    Aggregates = <>
    FieldDefs = <>
    IndexDefs = <>
    Params = <>
    ProviderName = 'dsProviderBusStopStands'
    RemoteServer = DSProviderConnection
    StoreDefs = True
    Left = 258
    Top = 296
  end
  object cdsLineRoadPoints: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLineRoadPoints'
    RemoteServer = DSProviderConnection
    Left = 360
    Top = 809
  end
  object cdsCombustionStandards: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCombustionStandards'
    RemoteServer = DSProviderConnection
    Left = 169
    Top = 384
  end
  object cdsStoredProcRoadPointsType8: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRoadPointsType8'
    RemoteServer = DSProviderConnection
    Left = 235
    Top = 109
  end
  object cdsStoredProcBusPCNotUse: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusPCNotUse'
    RemoteServer = DSProviderConnection
    Left = 409
    Top = 605
  end
  object cdsStorProcTicketRegister4Buses2Assign: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegister4Buses2Assign'
    RemoteServer = DSProviderConnection
    Left = 510
    Top = 511
  end
  object cdsPersonHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPersonHistory'
    RemoteServer = DSProviderConnection
    Left = 693
    Top = 81
  end
  object cdsCompanyHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompanyHistory'
    RemoteServer = DSProviderConnection
    Left = 253
    Top = 609
  end
  object cdsStoredProcLPC_CompaniesByType: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLPC_CompaniesByType'
    RemoteServer = DSProviderConnection
    Left = 405
    Top = 155
  end
  object cdsStoredProcCompaniesWithoutHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompaniesWithOutHistory'
    RemoteServer = DSProviderConnection
    Left = 912
    Top = 26
  end
  object cdsStoredProcDriverGroups: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsDriverGroups'
    RemoteServer = DSProviderConnection
    Left = 824
    Top = 184
  end
  object cdsTicketRegisterCardNotAssigned: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegisterCardNotAssigned'
    RemoteServer = DSProviderConnection
    Left = 957
    Top = 312
  end
  object cdsStoredProcCompanies: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompanies'
    RemoteServer = DSProviderConnection
    Left = 673
    Top = 16
  end
  object cdsStorProcDriversWithoutTicketCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderDriverWithoutTicketCard'
    RemoteServer = DSProviderConnection
    Left = 721
    Top = 565
  end
  object cdsStoredProcAllCompanyHierarchy: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompany_GetAllCompanyHierarchy'
    RemoteServer = DSProviderConnection
    Left = 945
    Top = 112
  end
  object cdsStoredProcBusStops: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStops'
    RemoteServer = DSProviderConnection
    Left = 56
    Top = 368
  end
  object cdsStorProcAutoCashier: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsAutoCashier'
    RemoteServer = DSProviderConnection
    Left = 816
    Top = 435
  end
  object cdsTicketControlDev: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketControlDev'
    RemoteServer = DSProviderConnection
    Left = 821
    Top = 371
  end
  object cdsStoredProcEmCardLoader: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProvidercEmCardLoader'
    RemoteServer = DSProviderConnection
    Left = 753
    Top = 120
  end
  object cdsBusPCNotAssignedToDriver: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsBusPCNotAssignedToDriver'
    RemoteServer = DSProviderConnection
    Left = 968
    Top = 387
  end
  object cdsStoredProcCalendar: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCalendar'
    RemoteServer = DSProviderConnection
    Left = 421
    Top = 304
  end
  object cdsStoredProcRideDesignation: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRideDesignation'
    RemoteServer = DSProviderConnection
    Left = 418
    Top = 378
  end
  object cdsStoredProcPriceLists: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceLists'
    RemoteServer = DSProviderConnection
    Left = 94
    Top = 504
  end
  object cdsRideTypeCommunication: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideTypeCommunication'
    RemoteServer = DSProviderConnection
    Left = 91
    Top = 800
  end
  object cdsRideServiceType: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideServiceType'
    RemoteServer = DSProviderConnection
    Left = 236
    Top = 887
  end
  object cdsRideCommunicationNetwork: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideCommunicationNetwork'
    RemoteServer = DSProviderConnection
    Left = 96
    Top = 736
  end
  object cdsRideBusTableConfPrefSet: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideBusTableConfPrefSet'
    RemoteServer = DSProviderConnection
    Left = 81
    Top = 871
  end
  object cdsRideExpPrefSets: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideExportPrefSet'
    RemoteServer = DSProviderConnection
    Left = 241
    Top = 745
  end
  object cdsRideSalePrefSets: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideSalesPrefSet'
    RemoteServer = DSProviderConnection
    Left = 238
    Top = 819
  end
  object cdsTT_TimeTableGetAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProvider_TT_TimeTableGetAll'
    RemoteServer = DSProviderConnection
    Left = 712
    Top = 290
  end
  object cdsLine: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLine'
    RemoteServer = DSProviderConnection
    Left = 362
    Top = 751
  end
  object cdsRide: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_Ride'
    RemoteServer = DSProviderConnection
    Left = 473
    Top = 752
  end
  object cdsStoredProcTicketZoneBusStops: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketZoneBusStops'
    RemoteServer = DSProviderConnection
    Left = 416
    Top = 439
  end
  object cdsStoredProcFarePriceReductionCities: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionCities'
    RemoteServer = DSProviderConnection
    Left = 297
    Top = 65
  end
  object cdsStoredProcPriceBasicCitiesScales: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceBasicCitysScales'
    RemoteServer = DSProviderConnection
    Left = 403
    Top = 204
  end
  object cdsStoredProcPriceCitiesScales: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceCitiesScales'
    RemoteServer = DSProviderConnection
    Left = 532
    Top = 166
  end
  object cdsStoredProcTicketZones: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketZones'
    RemoteServer = DSProviderConnection
    Left = 836
    Top = 81
  end
  object cdsStoredProcPriceMonthTypes: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceMonthType'
    RemoteServer = DSProviderConnection
    Left = 520
    Top = 355
  end
  object cdsStoredProcPriceMonthScales: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceMonthScales'
    RemoteServer = DSProviderConnection
    Left = 432
    Top = 243
  end
  object cdsStoredProcPriceOnesScales: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceOnesScales'
    RemoteServer = DSProviderConnection
    Left = 560
    Top = 257
  end
  object cdsStoredProcPriceMonthCityScales: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPriceMonthCityScales'
    RemoteServer = DSProviderConnection
    Left = 592
    Top = 105
  end
  object cdsStoredProcFarePriceReductionMonthCities: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionMonthCities'
    RemoteServer = DSProviderConnection
    Left = 81
    Top = 589
  end
  object cdsStoredProcFarePriceMonthReductionAmounts: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePricemonthReductionAmounts'
    RemoteServer = DSProviderConnection
    Left = 31
    Top = 146
  end
  object cdsStoredProcFarePriceReductionAmountsNotUse: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionAmountsNotUse'
    RemoteServer = DSProviderConnection
    Left = 111
    Top = 50
  end
  object cdsStoredProcFarePriceReductionAmounts: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionAmounts'
    RemoteServer = DSProviderConnection
    Left = 31
    Top = 230
  end
  object cdsStoredProcFarePriceReductionRoundMethod: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionRoundMethod'
    RemoteServer = DSProviderConnection
    Left = 393
    Top = 17
  end
  object cdsStoredProcVatRates: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderVatRates'
    RemoteServer = DSProviderConnection
    Left = 545
    Top = 312
  end
  object cdsStoredProcCurrenciesHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCurrenciesHistory'
    RemoteServer = DSProviderConnection
    Left = 842
    Top = 568
  end
  object cdsStoredProcCurrencies: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCurrencies'
    RemoteServer = DSProviderConnection
    Left = 797
    Top = 489
  end
  object cdsStoredProcFarePriceReductionWorkers: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionWorkers'
    RemoteServer = DSProviderConnection
    Left = 77
    Top = 784
  end
  object cdsStoredProcFarePriceReductionAct: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionAct'
    RemoteServer = DSProviderConnection
    Left = 87
    Top = 659
  end
  object cdsStoredProcFarePriceReductionGroup: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionGroup'
    RemoteServer = DSProviderConnection
    Left = 399
    Top = 878
  end
  object cdsStoredProcPassanger: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPassanger'
    RemoteServer = DSProviderConnection
    Left = 686
    Top = 647
  end
  object cdsStoredProcEmCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderEmCard'
    RemoteServer = DSProviderConnection
    Left = 814
    Top = 639
  end
  object cdsStoredProcLine: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLine'
    RemoteServer = DSProviderConnection
    Left = 666
    Top = 498
  end
  object cdsStoredProcCompanyLine: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompanyLine'
    RemoteServer = DSProviderConnection
    Left = 968
    Top = 176
  end
  object cdsStorProcTicketRegister4Buses: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegister4Buses'
    RemoteServer = DSProviderConnection
    Left = 992
    Top = 608
  end
  object cdsStoredProcBusGroups: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusGroups'
    RemoteServer = DSProviderConnection
    Left = 252
    Top = 406
  end
  object cdsStoredProcDrivers: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsDrivers'
    RemoteServer = DSProviderConnection
    Left = 808
    Top = 246
  end
  object cdsStoredProcBuses: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBuses'
    RemoteServer = DSProviderConnection
    Left = 712
    Top = 191
  end
  object cdsStoredProcBusPCStatus: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsBusPCStatus'
    RemoteServer = DSProviderConnection
    Left = 712
    Top = 358
  end
  object cdsDISPFile: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderDISPFile'
    RemoteServer = DSProviderConnection
    Left = 1022
    Top = 542
  end
  object cdsStoredProcTicketRegisterCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegisterCard'
    RemoteServer = DSProviderConnection
    Left = 313
    Top = 662
  end
  object cdsStorProcLineRides: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLineRides'
    RemoteServer = DSProviderConnection
    Left = 1018
    Top = 666
  end
  object cdsStorProcLines2AssignFarePriceScale: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsLines2AssignFarePriceScale'
    RemoteServer = DSProviderConnection
    Left = 624
    Top = 736
  end
  object cdsDISP_BusRun_GetAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderDISP_BusRun_GetAll'
    RemoteServer = DSProviderConnection
    Left = 616
    Top = 808
  end
  object cdsFileXTicketRegister: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsFileXTicketRegister'
    RemoteServer = DSProviderConnection
    Left = 536
    Top = 880
  end
  object cdsStoredProcGovOffice: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderGovOffice'
    RemoteServer = DSProviderConnection
    Left = 793
    Top = 14
  end
  object cdsAdditionalFees: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsAdditionalFees'
    RemoteServer = DSProviderConnection
    Left = 752
    Top = 872
  end
  object cdsStoredProcHist: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderHist'
    RemoteServer = DSProviderConnection
    Left = 548
    Top = 618
  end
  object cdsDriverTicketRegPrefSet: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideExportPrefSet'
    RemoteServer = DSProviderConnection
    Left = 473
    Top = 681
  end
  object cdsAnalysisRJAGPS: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderAnalysisRJAGPS'
    RemoteServer = DSProviderConnection
    Left = 836
    Top = 725
  end
  object cdsStoredProcPLAN_BusRunResultAnalyze: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPLAN_BusRunResultAnalyze'
    RemoteServer = DSProviderConnection
    Left = 836
    Top = 725
  end
  object cdsStoredProcDriverTicketRegPrefSet: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPLAN_DriverTicketRegPrefSet'
    RemoteServer = DSProviderConnection
    Left = 836
    Top = 725
  end
  object cdsBusStandNamePrefSets: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_BusStandNamePrefSet'
    RemoteServer = DSProviderConnection
    Left = 342
    Top = 987
  end
  object cdsRideReductions: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsRideReductions'
    RemoteServer = DSProviderConnection
    Left = 918
    Top = 671
  end
  object cdsRideBusStops: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsRideBusStops'
    RemoteServer = DSProviderConnection
    Left = 576
    Top = 1040
  end
  object cdsStoredProcTicketRegPrefSet: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderMAT_TicketRegPrefSet'
    RemoteServer = DSProviderConnection
    Left = 836
    Top = 797
  end
  object cdsTicketRegisterHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegisterHistory'
    RemoteServer = DSProviderConnection
    Left = 205
    Top = 553
  end
  object cdsCashDeskSettings: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCashDeskSettings'
    RemoteServer = DSProviderConnection
    Left = 166
    Top = 979
  end
  object cdsStorProcTicketRegister4SaleDevices: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTicketRegister4SalesDevices'
    RemoteServer = DSProviderConnection
    Left = 601
    Top = 950
  end
  object cdsStoredProcCashDesks: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCashDesks'
    RemoteServer = DSProviderConnection
    Left = 782
    Top = 946
  end
  object cdsStoredProcLPC_Parameters: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLPC_Parameters'
    RemoteServer = DSProviderConnection
    Left = 573
    Top = 989
  end
  object cdsBusHistory: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusPC'
    RemoteServer = DSProviderConnection
    Left = 77
    Top = 965
  end
  object cdsStoredProcTechnicalRide: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTechnicalRide'
    RemoteServer = DSProviderConnection
    Left = 573
    Top = 455
  end
  object cdsStoredProcContractRide: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderContractRide'
    RemoteServer = DSProviderConnection
    Left = 317
    Top = 350
  end
  object cdsStoredProcPlacesForRide: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPlacesForRide'
    RemoteServer = DSProviderConnection
    Left = 445
    Top = 113
  end
  object cdsStoredProcCircuit: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCircuit'
    RemoteServer = DSProviderConnection
    Left = 317
    Top = 414
  end
  object cdsStoredProcPLAN_RideRoadPoints: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPLAN_RideRoadPoints'
    RemoteServer = DSProviderConnection
    Left = 906
    Top = 512
  end
  object cdsFileXTicketRegisterCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsFileXTicketRegisterCard'
    RemoteServer = DSProviderConnection
    Left = 936
    Top = 944
  end
  object cdsStoredProcAdminUserAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsAdminUserAll'
    RemoteServer = DSProviderConnection
    Left = 1016
    Top = 78
  end
  object cdsSalesReportOfTicketRegister: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsSalesReportOfTicketRegister'
    RemoteServer = DSProviderConnection
    Left = 912
    Top = 1064
  end
  object cdsSalesReportOfTicketRegisterCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsSalesReportOfTicketRegisterCard'
    RemoteServer = DSProviderConnection
    Left = 720
    Top = 1144
  end
  object cdsStoredProcPlacesPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPlacesPagination'
    RemoteServer = DSProviderConnection
    Left = 93
    Top = 183
  end
  object cdsStoredProcFreeEmCard: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFreeEmCard'
    RemoteServer = DSProviderConnection
    Left = 966
    Top = 879
  end
  object cdsChoiceBusStop: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dspChoiceBusStop'
    RemoteServer = DSProviderConnection
    Left = 317
    Top = 1089
  end
  object cdsChoiceCompany: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dspChoiceCompany'
    RemoteServer = DSProviderConnection
    Left = 422
    Top = 1081
  end
  object cdsStoredProcRoadsPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRoadsPagination'
    RemoteServer = DSProviderConnection
    Left = 1192
    Top = 208
  end
  object cdsStoredProcBusStopsPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopsPagination'
    RemoteServer = DSProviderConnection
    Left = 128
    Top = 368
  end
  object cdsStoredProcBusStopSelectAssignedOrderByName: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopSelectAssignedOrderByName'
    RemoteServer = DSProviderConnection
    Left = 749
    Top = 1040
  end
  object cdsCommunityPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsCommunityPagination'
    RemoteServer = DSProviderConnection
    Left = 389
    Top = 1689
  end
  object cdsStoredProcTimeTableResult: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTimeTableResult'
    RemoteServer = DSProviderConnection
    Left = 54
    Top = 1178
  end
  object cdsStoredProcBusStopTablePatternChoice: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopTablePatternChoice'
    RemoteServer = DSProviderConnection
    Left = 237
    Top = 1179
  end
  object cdsStoredProcBusStopTablePattern: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopTablePattern'
    RemoteServer = DSProviderConnection
    Left = 238
    Top = 1224
  end
  object cdsStoredProcAdmin_ReportResultWhereReportTypeId: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderAdmin_ReportResultWhereReportTypeId'
    RemoteServer = DSProviderConnection
    Left = 429
    Top = 1174
  end
  object cdsStoredProcTimeTable_IDDesc: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTimeTable_IDDesc'
    RemoteServer = DSProviderConnection
    Left = 54
    Top = 1234
  end
  object cdsStoredProcBusStopsDuplicatesPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopsPagination'
    RemoteServer = DSProviderConnection
    Left = 208
    Top = 480
  end
  object cdsStoredProcFarePriceReductionCommercial: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReductionCommercial'
    RemoteServer = DSProviderConnection
    Left = 175
    Top = 719
  end
  object cdsSalesReportPagination: TClientDataSet
    Aggregates = <>
    Params = <>
    RemoteServer = DSProviderConnection
    Left = 912
    Top = 1120
  end
  object cdsTrackingMS_AUTOOBSERWACJA: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTrackingMS_AUTOOBSERWACJA'
    RemoteServer = DSProviderConnection
    Left = 41
    Top = 440
  end
  object cdsTrackingBusListWithGPS: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTrackingBusListWithGPS'
    RemoteServer = DSProviderConnection
    Left = 41
    Top = 440
  end
  object cdsStoredProcRideForPair: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dspRideForPair'
    RemoteServer = DSProviderConnection
    Left = 837
    Top = 296
  end
  object cdsStoredProcAdmin_ReportDefWhereReportTypeId: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderAdmin_ReportDefWhereReportTypeId'
    RemoteServer = DSProviderConnection
    Left = 1005
    Top = 1182
  end
  object cdsStoredProcCustom4: TClientDataSet
    Tag = 4
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom4'
    RemoteServer = DSProviderConnection
    Left = 165
    Top = 280
  end
  object cdsStoredProcLineRoute: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLineRoute'
    RemoteServer = DSProviderConnection
    Left = 354
    Top = 546
  end
  object cdsStoredProcBusStopFeeInvoice_SelectAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopFeeInvoice_SelectAll'
    RemoteServer = DSProviderConnection
    Left = 509
    Top = 822
  end
  object cdsStoredProcFeeType_GetBusStopFee: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFeeType_GetBusStopFee'
    RemoteServer = DSProviderConnection
    Left = 981
    Top = 768
  end
  object cdsStoredProcBusStopCompanySelectAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopCompanySelectAll'
    RemoteServer = DSProviderConnection
    Left = 976
    Top = 462
  end
  object cdsStoredProcBusStopFeeList: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderBusStopFeeListPagination'
    RemoteServer = DSProviderConnection
    Left = 981
    Top = 1017
  end
  object cdsStoredProcTT_RideGetAllForCEDULA: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTT_RideGetAllForCEDULA'
    RemoteServer = DSProviderConnection
    Left = 1024
    Top = 248
  end
  object cdsRidePagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRidePagination'
    RemoteServer = DSProviderConnection
    Left = 473
    Top = 800
  end
  object cdsLinePagination: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dspLinePagination'
    RemoteServer = DSProviderConnection
    Left = 418
    Top = 751
  end
  object cdsStoredProcCashReport: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCashReport'
    RemoteServer = DSProviderConnection
    Left = 706
    Top = 434
  end
  object cdsStoredProcSalesReportNoCashReport: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderSalesReportNoCashReport'
    RemoteServer = DSProviderConnection
    Left = 806
    Top = 1002
  end
  object dsProviderFarePriceReduction_SelectAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReduction_GetAll'
    RemoteServer = DSProviderConnection
    Left = 503
    Top = 567
  end
  object cdsStoredProcFarePriceReduction_SelectAll: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderFarePriceReduction_SelectAll'
    RemoteServer = DSProviderConnection
    Left = 231
    Top = 719
  end
  object cdsStoredProcLPC_CompaniesByBusStopManager: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCompaniesByBusStopManager'
    RemoteServer = DSProviderConnection
    Left = 389
    Top = 1277
  end
  object cdsStoredProcDrivers1: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsDrivers1'
    RemoteServer = DSProviderConnection
    Left = 896
    Top = 238
  end
  object cdsStoredProcCustom5: TClientDataSet
    Tag = 5
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom5'
    RemoteServer = DSProviderConnection
    Left = 165
    Top = 328
  end
  object cdsStoredProcLineFeeDefinition: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderLineFeeDefinition'
    RemoteServer = DSProviderConnection
    Left = 1000
    Top = 136
  end
  object cdsStoredProcDriversChoice: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsDrivers'
    RemoteServer = DSProviderConnection
    Left = 752
    Top = 230
  end
  object cdsStoredProcPlacesForBusStop: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderPlacesForBusStop'
    RemoteServer = DSProviderConnection
    Left = 1165
    Top = 17
  end
  object cdsStoredProcRideGroup: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderRideGroups'
    RemoteServer = DSProviderConnection
    Left = 293
    Top = 462
  end
  object cdsStoredProcTask: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTask'
    RemoteServer = DSProviderConnection
    Left = 141
    Top = 454
  end
  object cdsStoredProcTaskGroup: TClientDataSet
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderTaskGroup'
    RemoteServer = DSProviderConnection
    Left = 117
    Top = 550
  end
  object cdsStoredProcCustom6: TClientDataSet
    Tag = 6
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom6'
    RemoteServer = DSProviderConnection
    Left = 93
    Top = 296
  end
  object cdsStoredProcCustom7: TClientDataSet
    Tag = 7
    Aggregates = <>
    Params = <>
    ProviderName = 'dsProviderCustom7'
    RemoteServer = DSProviderConnection
    Left = 37
    Top = 304
  end
end
