-- ============================================================
-- Script: import.Fleet_InitialData_Insert
-- Description: Inserts seed/initial data for FleetOps tables.
--              Run once on a fresh installation.
--              Safe to re-run (uses IF NOT EXISTS guards).
-- ============================================================

-- ── Vehicle Payload Types ──────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_VehiclePayloadType WHERE PayloadTypeName = 'Standard Cargo')
    INSERT INTO dbo.Fleet_VehiclePayloadType (PayloadTypeName, MaxWeightKg, MaxVolumeM3, SortOrder)
    VALUES ('Standard Cargo', 5000, 20, 10)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_VehiclePayloadType WHERE PayloadTypeName = 'Heavy Freight')
    INSERT INTO dbo.Fleet_VehiclePayloadType (PayloadTypeName, MaxWeightKg, MaxVolumeM3, SortOrder)
    VALUES ('Heavy Freight', 24000, 80, 20)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_VehiclePayloadType WHERE PayloadTypeName = 'Refrigerated')
    INSERT INTO dbo.Fleet_VehiclePayloadType (PayloadTypeName, MaxWeightKg, MaxVolumeM3, RequiresRefrigUnit, SortOrder)
    VALUES ('Refrigerated', 8000, 30, 1, 30)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_VehiclePayloadType WHERE PayloadTypeName = 'Hazardous Materials')
    INSERT INTO dbo.Fleet_VehiclePayloadType (PayloadTypeName, MaxWeightKg, HazmatClass, SortOrder)
    VALUES ('Hazardous Materials', 3000, 'ADR-3', 40)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_VehiclePayloadType WHERE PayloadTypeName = 'Passenger')
    INSERT INTO dbo.Fleet_VehiclePayloadType (PayloadTypeName, MaxWeightKg, SortOrder)
    VALUES ('Passenger', NULL, 50)
GO

-- ── Job Statuses ───────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.ORD_JobStatus WHERE JobStatusID = 1)
    INSERT INTO dbo.ORD_JobStatus (JobStatusID, StatusName, StatusColor, IsTerminal)
    VALUES (1, 'Pending', '#FFA500', 0)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ORD_JobStatus WHERE JobStatusID = 2)
    INSERT INTO dbo.ORD_JobStatus (JobStatusID, StatusName, StatusColor, IsTerminal)
    VALUES (2, 'In Progress', '#0080FF', 0)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ORD_JobStatus WHERE JobStatusID = 3)
    INSERT INTO dbo.ORD_JobStatus (JobStatusID, StatusName, StatusColor, IsTerminal)
    VALUES (3, 'Completed', '#00C000', 1)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ORD_JobStatus WHERE JobStatusID = 4)
    INSERT INTO dbo.ORD_JobStatus (JobStatusID, StatusName, StatusColor, IsTerminal)
    VALUES (4, 'Cancelled', '#808080', 1)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ORD_JobStatus WHERE JobStatusID = 5)
    INSERT INTO dbo.ORD_JobStatus (JobStatusID, StatusName, StatusColor, IsTerminal)
    VALUES (5, 'On Hold', '#FF4040', 0)
GO

-- ── Service Types ──────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.VEH_ServiceTypes WHERE ServiceTypeName = 'Oil Change')
    INSERT INTO dbo.VEH_ServiceTypes (ServiceTypeName, IsRecurring, RecurrenceDays, RecurrenceKm)
    VALUES ('Oil Change', 1, 180, 15000)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.VEH_ServiceTypes WHERE ServiceTypeName = 'Tyre Rotation')
    INSERT INTO dbo.VEH_ServiceTypes (ServiceTypeName, IsRecurring, RecurrenceDays, RecurrenceKm)
    VALUES ('Tyre Rotation', 1, 90, 10000)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.VEH_ServiceTypes WHERE ServiceTypeName = 'Annual Inspection')
    INSERT INTO dbo.VEH_ServiceTypes (ServiceTypeName, IsRecurring, RecurrenceDays, RecurrenceKm)
    VALUES ('Annual Inspection', 1, 365, NULL)
GO

IF NOT EXISTS (SELECT 1 FROM dbo.VEH_ServiceTypes WHERE ServiceTypeName = 'Brake Service')
    INSERT INTO dbo.VEH_ServiceTypes (ServiceTypeName, IsRecurring, RecurrenceDays, RecurrenceKm)
    VALUES ('Brake Service', 0, NULL, NULL)
GO

-- ── Default Branch ─────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.Fleet_Branches WHERE BranchCode = 'HQ')
    INSERT INTO dbo.Fleet_Branches (BranchCode, BranchName, Address, City, PostalCode, IsActive, SortOrder)
    VALUES ('HQ', 'Headquarters', '1 Fleet Street', 'Metropolis', '10001', 1, 1)
GO

-- ── Report Definitions ─────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.RPT_ReportDef WHERE ReportName = 'Driver Payroll by Trips')
    INSERT INTO dbo.RPT_ReportDef
        (ReportName, ReportType, ScheduleType, OutputFormat, IsActive, CreatedAt)
    VALUES
        ('Driver Payroll by Trips', 'PAYROLL', 'MONTHLY', 'PDF', 1, GETDATE())
GO

IF NOT EXISTS (SELECT 1 FROM dbo.RPT_ReportDef WHERE ReportName = 'List of Job Orders')
    INSERT INTO dbo.RPT_ReportDef
        (ReportName, ReportType, ScheduleType, OutputFormat, IsActive, CreatedAt)
    VALUES
        ('List of Job Orders', 'DISPATCH', 'DAILY', 'PDF', 1, GETDATE())
GO

IF NOT EXISTS (SELECT 1 FROM dbo.RPT_ReportDef WHERE ReportName = 'Payroll Summary')
    INSERT INTO dbo.RPT_ReportDef
        (ReportName, ReportType, ScheduleType, OutputFormat, IsActive, CreatedAt)
    VALUES
        ('Payroll Summary', 'PAYROLL', 'MONTHLY', 'XLSX', 1, GETDATE())
GO
