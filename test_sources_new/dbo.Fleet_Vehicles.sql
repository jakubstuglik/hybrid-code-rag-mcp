-- ============================================================
-- Table: dbo.Fleet_Vehicles
-- Description: Core vehicle registry for the FleetOps platform
-- ============================================================

IF OBJECT_ID(N'dbo.Fleet_Vehicles', N'U') IS NOT NULL
    DROP TABLE dbo.Fleet_Vehicles
GO

CREATE TABLE dbo.Fleet_Vehicles
(
    VehicleID           INT             NOT NULL IDENTITY(1,1),
    RegistrationNo      NVARCHAR(20)    NOT NULL,
    VehicleType         NVARCHAR(50)    NOT NULL,
    BranchID            INT             NOT NULL,
    DriverID            INT             NULL,
    PayloadTypeID       INT             NULL,
    FuelType            NVARCHAR(20)    NOT NULL DEFAULT 'DIESEL',
    MaxPayloadKg        DECIMAL(10,2)   NULL,
    OdometerKm          DECIMAL(12,2)   NOT NULL DEFAULT 0,
    VIN                 NVARCHAR(17)    NULL,
    Make                NVARCHAR(50)    NULL,
    Model               NVARCHAR(50)    NULL,
    YearOfManufacture   SMALLINT        NULL,
    IsActive            BIT             NOT NULL DEFAULT 1,
    InsuranceExpiry     DATE            NULL,
    TechnicalInspExpiry DATE            NULL,
    Notes               NVARCHAR(500)   NULL,
    CreatedAt           DATETIME        NOT NULL DEFAULT GETDATE(),
    CreatedBy           NVARCHAR(50)    NOT NULL DEFAULT SYSTEM_USER,
    ModifiedAt          DATETIME        NULL,
    ModifiedBy          NVARCHAR(50)    NULL,

    CONSTRAINT PK_Fleet_Vehicles PRIMARY KEY CLUSTERED (VehicleID),
    CONSTRAINT UQ_Fleet_Vehicles_RegistrationNo UNIQUE (RegistrationNo),
    CONSTRAINT FK_Fleet_Vehicles_BranchID FOREIGN KEY (BranchID)
        REFERENCES dbo.Fleet_Branches (BranchID),
    CONSTRAINT FK_Fleet_Vehicles_DriverID FOREIGN KEY (DriverID)
        REFERENCES dbo.HR_Drivers (DriverID),
    CONSTRAINT FK_Fleet_Vehicles_PayloadTypeID FOREIGN KEY (PayloadTypeID)
        REFERENCES dbo.Fleet_VehiclePayloadType (PayloadTypeID)
)
GO

CREATE INDEX IX_Fleet_Vehicles_BranchID ON dbo.Fleet_Vehicles (BranchID)
GO

CREATE INDEX IX_Fleet_Vehicles_DriverID ON dbo.Fleet_Vehicles (DriverID)
GO

CREATE INDEX IX_Fleet_Vehicles_IsActive ON dbo.Fleet_Vehicles (IsActive)
    INCLUDE (RegistrationNo, VehicleType, BranchID)
GO
