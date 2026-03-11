CREATE TABLE [dbo].[SLS_TicketPaymentTypeEMAR205]
(
[ID] [int] NOT NULL IDENTITY(1, 1),
[Ticket_ID] [bigint] NOT NULL,
[PaymentType_ID] [int] NOT NULL,
[Amount] [int] NOT NULL,
[CREATED] [dbo].[datetimenotnull] NOT NULL CONSTRAINT [SLS_TicketPaymentTypeEMAR205CREATED_def] DEFAULT (getdate()),
[MODIFIED] [dbo].[datetimenotnull] NOT NULL CONSTRAINT [SLS_TicketPaymentTypeEMAR205MODIFIED_def] DEFAULT (getdate())
)
GO
ALTER TABLE [dbo].[SLS_TicketPaymentTypeEMAR205] ADD CONSTRAINT [SLS_TicketPaymentTypeEMAR205ID_pk] PRIMARY KEY CLUSTERED  ([ID])
GO
CREATE NONCLUSTERED INDEX [SLS_TicketPaymentTypeEMAR205ID_TicketID_idx] ON [dbo].[SLS_TicketPaymentTypeEMAR205] ([Ticket_ID]) INCLUDE ([Amount], [PaymentType_ID])
GO
ALTER TABLE [dbo].[SLS_TicketPaymentTypeEMAR205] ADD CONSTRAINT [SLS_TicketPaymentTypeEMAR205_FK_SLS_PaymentType] FOREIGN KEY ([PaymentType_ID]) REFERENCES [dbo].[SLS_PaymentType] ([ID])
GO
ALTER TABLE [dbo].[SLS_TicketPaymentTypeEMAR205] ADD CONSTRAINT [SLS_TicketPaymentTypeEMAR205_FK_SLS_Ticket] FOREIGN KEY ([Ticket_ID]) REFERENCES [dbo].[SLS_Ticket] ([ID])
GO
