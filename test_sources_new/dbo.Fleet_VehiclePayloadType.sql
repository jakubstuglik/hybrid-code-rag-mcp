-- ============================================================
-- Table: dbo.Fleet_VehiclePayloadType
-- Description: Lookup table for vehicle payload/cargo classifications
-- ============================================================

IF OBJECT_ID(N'dbo.Fleet_VehiclePayloadType', N'U') IS NOT NULL
    DROP TABLE dbo.Fleet_VehiclePayloadType
GO

CREATE TABLE dbo.Fleet_VehiclePayloadType
(
    PayloadTypeID       INT             NOT NULL IDENTITY(1,1),
    PayloadTypeName     NVARCHAR(100)   NOT NULL,
    MaxWeightKg         DECIMAL(10,2)   NULL,
    MaxVolumeM3         DECIMAL(8,3)    NULL,
    RequiresRefrigUnit  BIT             NOT NULL DEFAULT 0,
    HazmatClass         NVARCHAR(10)    NULL,
    IsActive            BIT             NOT NULL DEFAULT 1,
    SortOrder           INT             NOT NULL DEFAULT 0,
    CreatedAt           DATETIME        NOT NULL DEFAULT GETDATE(),

    CONSTRAINT PK_Fleet_VehiclePayloadType PRIMARY KEY CLUSTERED (PayloadTypeID),
    CONSTRAINT UQ_Fleet_VehiclePayloadType_Name UNIQUE (PayloadTypeName)
)
GO

CREATE INDEX IX_Fleet_VehiclePayloadType_IsActive
    ON dbo.Fleet_VehiclePayloadType (IsActive)
    INCLUDE (PayloadTypeName, MaxWeightKg)
GO
