CREATE TABLE [dbo].[SLS_Ticket]
(
[ID] [bigint] NOT NULL IDENTITY(1, 1),
[SaleDate] [datetime] NOT NULL,
[SaleYear] [int] NOT NULL,
[SaleMonth] [int] NOT NULL,
[Company_ID] [int] NOT NULL,
[TicketType_ID] [int] NOT NULL,
[MonthTicketSaleOnBus] [bit] NULL,
[MonthTicketType] [int] NULL,
[TicketGenre_ID] [int] NULL,
[FiscalReport_ID] [int] NULL,
[TicketLayout_ID] [int] NULL,
[MonthTicketPriceComputingType_ID] [int] NULL,
[TicketNumberBM] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[TicketNumber] [int] NULL,
[PrintNumber] [int] NULL,
[ControlNumber] [nvarchar] (13) COLLATE Polish_CI_AS NULL,
[EPNumber] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[EPCode] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[EPDynamic] [bit] NULL,
[ValidFrom] [datetime] NULL,
[ValidTo] [datetime] NULL,
[TimeFrom] [time] (0) NULL,
[TimeTo] [time] (0) NULL,
[FarePriceReduction_ID] [int] NULL,
[ReductionName] [nvarchar] (30) COLLATE Polish_CI_AS NULL,
[ReductionPercentage] [int] NULL,
[ReductionRefund] [int] NULL,
[FarePrice_ID] [int] NULL,
[FarePriceAdditionalFee_ID] [int] NULL,
[FarePriceDiscount_ID] [int] NULL,
[PassangerNumber] [smallint] NULL,
[NormalPrice] [int] NULL,
[DiscountCharge] [int] NULL,
[ReductionValue] [int] NULL,
[AdditionalFeeCharge] [int] NULL,
[VatCode] [nvarchar] (1) COLLATE Polish_CI_AS NULL,
[VatAmount] [int] NULL,
[Price] [int] NULL,
[NormalPriceAbroad] [int] NULL,
[DiscountChargeAbroad] [int] NULL,
[ReductionValueAbroad] [int] NULL,
[AdditionalFeeChargeAbroad] [int] NULL,
[VatCodeAbroad] [nvarchar] (1) COLLATE Polish_CI_AS NULL,
[VatAmountAbroad] [int] NULL,
[PriceAbroad] [int] NULL,
[PriceSum] [int] NULL,
[EmployeeTicket] [tinyint] NOT NULL,
[AmountToPay] [int] NULL,
[Currency_ID] [int] NOT NULL,
[ExchangeRate] [decimal] (10, 7) NOT NULL,
[PaymentType_ID] [int] NOT NULL,
[EmCardSaveDate] [datetime] NULL,
[Emcard_ID] [int] NULL,
[EmCardChanged] [bit] NULL,
[Driver_ID] [int] NULL,
[PassangerFirstName] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[PassangerLastName] [nvarchar] (30) COLLATE Polish_CI_AS NULL,
[PassangerPESEL] [nvarchar] (11) COLLATE Polish_CI_AS NULL,
[PassangerIDCardNumber] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[PassangerAddress] [nvarchar] (200) COLLATE Polish_CI_AS NULL,
[PassangerReductionCardNumber] [nvarchar] (30) COLLATE Polish_CI_AS NULL,
[PassangerReductionCardValidDate] [datetime] NULL,
[RideNumber] [int] NULL,
[RideNumberDays] [int] NULL,
[SaleCharge] [int] NULL,
[TicketCancelled_ID] [bigint] NULL,
[TicketReturnAmount] [int] NULL,
[TicketChanged_ID] [bigint] NULL,
[EmCardTicketType_ID] [int] NULL,
[PreviousMultiRideTicket_ID] [bigint] NULL,
[PreviousMultiTicketRides] [int] NULL,
[PreviousMultiTicketRideValue] [int] NULL,
[LoyaltyFirstTicket_ID] [bigint] NULL,
[SumLoyaltyTicketDistance] [int] NULL,
[SumLoyaltyTicketPrice] [int] NULL,
[AdditionalText] [nvarchar] (40) COLLATE Polish_CI_AS NULL,
[GroupTicket_ID] [int] NULL,
[Printed] [int] NULL,
[TicketStatus] [int] NOT NULL CONSTRAINT [SLS_TicketStatus] DEFAULT ((0)),
[TicketGUID] [nvarchar] (50) COLLATE Polish_CI_AS NULL,
[CREATED] [dbo].[datetimenotnull] NOT NULL CONSTRAINT [SLS_TicketCREATED_def] DEFAULT (getdate()),
[MODIFIED] [dbo].[datetimenotnull] NOT NULL CONSTRAINT [SLS_TicketMODIFIED_def] DEFAULT (getdate()),
[CompanyGov_ID] [int] NULL,
[InterchangeTicket] [bit] NULL,
[AntennaConnection_Company_ID] [int] NULL,
[AntennaConnectionNumber] [smallint] NULL,
[MethodofCP_AntCon] [int] NULL,
[PriceRate_IT] [decimal] (9, 7) NULL,
[ReductionCode] [int] NULL,
[ReductionNumber] [int] NULL,
[FarePriceReductionGroup_ID] [int] NULL,
[ReductionRoundMethod_ID] [int] NULL,
[TicketPattern] [bit] NULL,
[MonthTicketAlgorithm] [nvarchar] (100) COLLATE Polish_CI_AS NULL,
[TicketCancelled_SaleDate] [datetime] NULL,
[SalesReport_ID] [int] NULL,
[TicketUpdate_ID] [bigint] NULL,
[KPDriverID] [int] NULL,
[QRCODE] [nvarchar] (250) COLLATE Polish_CI_AS NULL,
[OrygPaymentType_ID] [int] NULL,
[CityTicket_TariffNo] [int] NULL,
[CityTicket_PriceNo] [int] NULL,
[CityTicket_KPTariffID] [int] NULL,
[KPTerminalPaymentSuccess] [bit] NULL,
[BuyerNIP] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[PassengerNRPAS] [nvarchar] (20) COLLATE Polish_CI_AS NULL,
[TicketBeforeChangeEPCode] [nvarchar] (21) COLLATE Polish_CI_AS NULL,
[TicketAfterChangeEPCode] [nvarchar] (21) COLLATE Polish_CI_AS NULL,
[TicketBeforeChange_ID] [bigint] NULL,
[TicketAfterChange_ID] [bigint] NULL,
[TicketProlonged_ID] [bigint] NULL,
[TicketFiscalInnerId] [varchar] (18) COLLATE Polish_CI_AS NULL,
[EMKFromEP] [bit] NOT NULL CONSTRAINT [DF__SLS_Ticke__EMKFr__08F871E7] DEFAULT ((0)),
[WarehouseToBeProcessed] [bit] NOT NULL CONSTRAINT [SLS_TicketWarehouseToBeProcessed_def] DEFAULT ((1)),
[EPCardFromDWSQL] [bit] NOT NULL CONSTRAINT [SLS_EPCardFromDWSQL_def] DEFAULT ((0))
)
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_TicketID_pk] PRIMARY KEY CLUSTERED  ([ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_CompanyValidFromToEmCardTicketNumberBM_idx] ON [dbo].[SLS_Ticket] ([Company_ID], [ValidFrom], [ValidTo], [Emcard_ID], [TicketNumberBM])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_EmCardIDFiscalReportID_idx] ON [dbo].[SLS_Ticket] ([Emcard_ID]) INCLUDE ([FiscalReport_ID], [ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_FarePriceReduction_idx] ON [dbo].[SLS_Ticket] ([FarePriceReduction_ID], [TicketGenre_ID]) INCLUDE ([Company_ID], [ID], [ReductionCode], [SaleDate])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_FiscalReport_ID_idx] ON [dbo].[SLS_Ticket] ([FiscalReport_ID]) INCLUDE ([TicketGenre_ID], [TicketType_ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_SaleDateID_idx] ON [dbo].[SLS_Ticket] ([SaleDate]) INCLUDE ([ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_ReportTicketUpdateSaleDate_idx>] ON [dbo].[SLS_Ticket] ([SalesReport_ID], [TicketUpdate_ID], [SaleDate]) INCLUDE ([Company_ID], [FiscalReport_ID], [ID], [PriceSum])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_SalesReportTicketUpdateSaleDateTicketGenre_idx] ON [dbo].[SLS_Ticket] ([SalesReport_ID], [TicketUpdate_ID], [SaleDate], [TicketGenre_ID]) INCLUDE ([ID], [TicketCancelled_ID], [TicketType_ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_TicketCancelledID_idx] ON [dbo].[SLS_Ticket] ([TicketCancelled_ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_TicketNumberPrintNumberValidFromValidTo_idx] ON [dbo].[SLS_Ticket] ([TicketNumber], [PrintNumber], [ValidFrom], [ValidTo])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_TicketType_INCLUDED_idx] ON [dbo].[SLS_Ticket] ([TicketType_ID]) INCLUDE ([ID])
GO
CREATE NONCLUSTERED INDEX [SLS_Ticket_TicketUpdate_idx] ON [dbo].[SLS_Ticket] ([TicketUpdate_ID]) INCLUDE ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_ADMIN_Company] FOREIGN KEY ([Company_ID]) REFERENCES [dbo].[ADMIN_Company] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_ADMIN_CompanyAntennaConnection] FOREIGN KEY ([AntennaConnection_Company_ID]) REFERENCES [dbo].[ADMIN_Company] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_FiscalReport] FOREIGN KEY ([FiscalReport_ID]) REFERENCES [dbo].[SLS_FiscalReport] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_PLAN_Driver] FOREIGN KEY ([Driver_ID]) REFERENCES [dbo].[PLAN_Driver] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_EmCard] FOREIGN KEY ([Emcard_ID]) REFERENCES [dbo].[SLS_EmCard] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_EmCardTicketType] FOREIGN KEY ([EmCardTicketType_ID]) REFERENCES [dbo].[SLS_EmCardTicketType] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_GroupTicket] FOREIGN KEY ([GroupTicket_ID]) REFERENCES [dbo].[SLS_GroupTicket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_MonthTicketPriceComputingType] FOREIGN KEY ([MonthTicketPriceComputingType_ID]) REFERENCES [dbo].[SLS_MonthTicketPriceComputingType] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_PaymentType] FOREIGN KEY ([PaymentType_ID]) REFERENCES [dbo].[SLS_PaymentType] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_SalesReport] FOREIGN KEY ([SalesReport_ID]) REFERENCES [dbo].[SLS_SalesReport] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_Ticket] FOREIGN KEY ([TicketCancelled_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketCancelled] FOREIGN KEY ([TicketCancelled_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketChanged] FOREIGN KEY ([TicketChanged_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketGenre] FOREIGN KEY ([TicketGenre_ID]) REFERENCES [dbo].[SLS_TicketGenre] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketLoyaltyFirstTicket] FOREIGN KEY ([LoyaltyFirstTicket_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketPreviousMultiRideTicket] FOREIGN KEY ([PreviousMultiRideTicket_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketType] FOREIGN KEY ([TicketType_ID]) REFERENCES [dbo].[SLS_TicketType] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_SLS_TicketUpdate] FOREIGN KEY ([TicketUpdate_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_Currency] FOREIGN KEY ([Currency_ID]) REFERENCES [dbo].[TCK_Currency] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_FarePrice] FOREIGN KEY ([FarePrice_ID]) REFERENCES [dbo].[TCK_FarePrice] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_FarePriceAdditionalFee] FOREIGN KEY ([FarePriceAdditionalFee_ID]) REFERENCES [dbo].[TCK_FarePrice] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_FarePriceDiscount] FOREIGN KEY ([FarePriceDiscount_ID]) REFERENCES [dbo].[TCK_FarePrice] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_FarePriceReduction] FOREIGN KEY ([FarePriceReduction_ID]) REFERENCES [dbo].[TCK_FarePriceReduction] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_FarePriceReductionGroup] FOREIGN KEY ([FarePriceReductionGroup_ID]) REFERENCES [dbo].[TCK_FarePriceReductionGroup] ([ID])
GO
ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT [SLS_Ticket_FK_TCK_ReductionRoundMethod] FOREIGN KEY ([ReductionRoundMethod_ID]) REFERENCES [dbo].[TCK_ReductionRoundMethod] ([ID])
GO
EXEC sp_addextendedproperty N'MS_Description', N'Liczba pasażerów', 'SCHEMA', N'dbo', 'TABLE', N'SLS_Ticket', 'COLUMN', N'PassangerNumber'
GO
EXEC sp_addextendedproperty N'MS_Description', N'rodzaj biletu', 'SCHEMA', N'dbo', 'TABLE', N'SLS_Ticket', 'COLUMN', N'TicketType_ID'
GO
