"""
Generator for test_sources_new/VehicleData.classes.pas
Fictional FleetOps corpus — test data for RAG indexer.
"""

import os

OUT = r"C:\GitRepos\hybrid-code-rag-mcp\test_sources_new\VehicleData.classes.pas"

lines = []


def w(*args):
    for a in args:
        lines.append(a)


def prop_name(fname):
    return fname[1:]  # strip leading F


def ret_type(ftype):
    if ftype == "string":
        return "WideString"
    return ftype


# ── Header ──────────────────────────────────────────────────────────────────
w("unit VehicleData.classes;", "")
w("interface", "")
w("uses")
w("  SysUtils, Classes, Windows, Math, DateUtils,")
w("  DB, DBClient, Provider,")
w("  FleetBase.classes;")
w("")
w("type")
w("")

# ── Forward declarations ─────────────────────────────────────────────────────
FWD_CLASSES = [
    "TFleet105_Device",
    "TFleet105_Vehicle",
    "TFleet105_VehicleList",
    "TFleet105_Driver",
    "TFleet105_DriverList",
    "TFleet105_Route",
    "TFleet105_RouteList",
    "TFleet105_JobOrder",
    "TFleet105_JobOrderList",
    "TFleet105_FuelRecord",
    "TFleet105_FuelRecordList",
    "TFleet105_ServiceRecord",
    "TFleet105_ServiceRecordList",
    "TFleet105_Incident",
    "TFleet105_IncidentList",
    "TFleet105_GpsTrack",
    "TFleet105_GpsTrackList",
    "TFleet105_Depot",
    "TFleet105_DepotList",
    "TFleet105_Employee",
    "TFleet105_EmployeeList",
    "TFleet105_Department",
    "TFleet105_DepartmentList",
    "TFleet105_Schedule",
    "TFleet105_ScheduleList",
    "TFleet105_Passenger",
    "TFleet105_PassengerList",
    "TFleet105_Trip",
    "TFleet105_TripList",
    "TFleet105_PayrollEntry",
    "TFleet105_PayrollEntryList",
    "TFleet105_MaintenancePlan",
    "TFleet105_MaintenancePlanList",
    "TFleet105_PartStock",
    "TFleet105_PartStockList",
    "TFleet105_Supplier",
    "TFleet105_SupplierList",
    "TFleet105_PurchaseOrder",
    "TFleet105_PurchaseOrderList",
    "TFleet105_Invoice",
    "TFleet105_InvoiceList",
    "TFleet105_CostCentre",
    "TFleet105_CostCentreList",
    "TFleet105_TyreRecord",
    "TFleet105_TyreRecordList",
    "TFleet105_PermitLicence",
    "TFleet105_PermitLicenceList",
    "TFleet105_AlertEvent",
    "TFleet105_AlertEventList",
    "TFleet105_ReportDef",
    "TFleet105_ReportDefList",
    "TFleet105_UserAccount",
    "TFleet105_UserAccountList",
    "TFleet105_RolePermission",
    "TFleet105_RolePermissionList",
    "TFleet105_AuditLog",
    "TFleet105_AuditLogList",
    "TFleet105_Notification",
    "TFleet105_NotificationList",
    "TFleet105_DocumentStore",
    "TFleet105_DocumentStoreList",
    "TFleet105_GeoZone",
    "TFleet105_GeoZoneList",
    "TFleet105_ChecklistTemplate",
    "TFleet105_ChecklistTemplateList",
    "TFleet105_ChecklistResult",
    "TFleet105_ChecklistResultList",
    "TFleet105_ContractClient",
    "TFleet105_ContractClientList",
    "TFleet105_BillingRecord",
    "TFleet105_BillingRecordList",
]
w("// Forward declarations")
for c in FWD_CLASSES:
    w(f"  {c} = class;")
w("")

# ── TFleet105_Device declaration ─────────────────────────────────────────────
DEVICE_FIELDS = [
    ("FDeviceId", "Integer"),
    ("FDeviceSerial", "string"),
    ("FDeviceName", "string"),
    ("FDeviceType", "Integer"),
    ("FFirmwareVersion", "string"),
    ("FHardwareRevision", "string"),
    ("FLastContactTime", "TDateTime"),
    ("FBatteryLevel", "Integer"),
    ("FSignalStrength", "Integer"),
    ("FGpsLatitude", "Double"),
    ("FGpsLongitude", "Double"),
    ("FGpsAltitude", "Double"),
    ("FGpsSpeed", "Double"),
    ("FGpsHeading", "Double"),
    ("FGpsAccuracy", "Double"),
    ("FGpsSatellites", "Integer"),
    ("FGpsFixTime", "TDateTime"),
    ("FVehicleId", "Integer"),
    ("FDepotId", "Integer"),
    ("FIsActive", "Boolean"),
    ("FIsOnline", "Boolean"),
    ("FConfigVersion", "Integer"),
    ("FMaxSpeed", "Integer"),
    ("FIdleTimeout", "Integer"),
    ("FReportInterval", "Integer"),
    ("FAlertFlags", "Cardinal"),
    ("FErrorCode", "Integer"),
    ("FErrorMessage", "string"),
    ("FInstallDate", "TDateTime"),
    ("FWarrantyExpiry", "TDateTime"),
    ("FSupplierCode", "string"),
    ("FAssetTag", "string"),
    ("FEncryptionKey", "string"),
    ("FAuthToken", "string"),
    ("FServerUrl", "string"),
    ("FServerPort", "Integer"),
    ("FConnectionMode", "Integer"),
    ("FDataQueueSize", "Integer"),
    ("FTotalMessagesSent", "Int64"),
    ("FTotalMessagesReceived", "Int64"),
    ("FTotalBytesTransferred", "Int64"),
    ("FSessionCount", "Integer"),
    ("FLastResetTime", "TDateTime"),
    ("FDiagnosticData", "string"),
    ("FCalibrationDate", "TDateTime"),
]

w("// ──────────────────────────────────────────────────────────────────────────")
w("// TFleet105_Device — Master device class")
w("// ──────────────────────────────────────────────────────────────────────────")
w("  TFleet105_Device = class(TFleetDevice, IFleet105_Device)")
w("  private")
for fn, ft in DEVICE_FIELDS:
    w(f"    {fn}: {ft};")
w("  public")
w("    constructor Create; override;")
w("    destructor Destroy; override;")
for fn, ft in DEVICE_FIELDS:
    pn = prop_name(fn)
    rt = ret_type(ft)
    w(f"    function Get{pn}: {rt}; stdcall;")
    w(f"    procedure Set{pn}(const Value: {rt}); stdcall;")
DEVICE_UTIL = [
    "function Connect(const AServerUrl: WideString; APort: Integer): Boolean; stdcall;",
    "function Disconnect: Boolean; stdcall;",
    "function SendHeartbeat: Boolean; stdcall;",
    "function ParseGpsData(const ARawData: WideString): Boolean; stdcall;",
    "function UpdateFirmware(const AFirmwareFile: WideString): Boolean; stdcall;",
    "function ResetDevice: Boolean; stdcall;",
    "function RunDiagnostics: WideString; stdcall;",
    "function ExportConfig(const AFileName: WideString): Boolean; stdcall;",
    "function ImportConfig(const AFileName: WideString): Boolean; stdcall;",
    "function ValidateAuth: Boolean; stdcall;",
    "function EncryptPayload(const AData: WideString): WideString; stdcall;",
    "function DecryptPayload(const AData: WideString): WideString; stdcall;",
    "function QueueMessage(const AMsg: WideString; APriority: Integer): Boolean; stdcall;",
    "function FlushQueue: Integer; stdcall;",
    "function GetStatusReport: WideString; stdcall;",
]
for m in DEVICE_UTIL:
    w(f"    {m}")
w("  published")
for fn, ft in DEVICE_FIELDS:
    pn = prop_name(fn)
    rt = ret_type(ft)
    w(f"    property {pn}: {rt} read Get{pn} write Set{pn};")
w("  end;", "")

# ── Entity definitions ────────────────────────────────────────────────────────
ENTITIES = [
    (
        "TFleet105_Vehicle",
        [
            ("FVehicleId", "Integer"),
            ("FRegistrationNo", "string"),
            ("FFleetNo", "string"),
            ("FMake", "string"),
            ("FModel", "string"),
            ("FYear", "Integer"),
            ("FEngineCC", "Integer"),
            ("FFuelType", "Integer"),
            ("FGrossWeight", "Integer"),
            ("FPayloadKg", "Integer"),
            ("FDepotId", "Integer"),
            ("FStatusCode", "Integer"),
            ("FPurchaseDate", "TDateTime"),
            ("FMileageKm", "Integer"),
            ("FIsActive", "Boolean"),
        ],
    ),
    (
        "TFleet105_Driver",
        [
            ("FDriverId", "Integer"),
            ("FEmployeeNo", "string"),
            ("FFirstName", "string"),
            ("FLastName", "string"),
            ("FLicenceNo", "string"),
            ("FLicenceClass", "string"),
            ("FLicenceExpiry", "TDateTime"),
            ("FDepotId", "Integer"),
            ("FRouteId", "Integer"),
            ("FStatusCode", "Integer"),
            ("FIsActive", "Boolean"),
            ("FDateOfBirth", "TDateTime"),
            ("FContactPhone", "string"),
            ("FContactEmail", "string"),
            ("FHireDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_Route",
        [
            ("FRouteId", "Integer"),
            ("FRouteCode", "string"),
            ("FRouteName", "string"),
            ("FStartPoint", "string"),
            ("FEndPoint", "string"),
            ("FDistanceKm", "Double"),
            ("FEstimatedMins", "Integer"),
            ("FDepotId", "Integer"),
            ("FDirectionCode", "Integer"),
            ("FIsCircular", "Boolean"),
            ("FIsActive", "Boolean"),
            ("FValidFrom", "TDateTime"),
            ("FValidTo", "TDateTime"),
        ],
    ),
    (
        "TFleet105_JobOrder",
        [
            ("FJobId", "Integer"),
            ("FJobRef", "string"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FRouteId", "Integer"),
            ("FScheduledDate", "TDateTime"),
            ("FActualStart", "TDateTime"),
            ("FActualEnd", "TDateTime"),
            ("FStatusCode", "Integer"),
            ("FPriorityLevel", "Integer"),
            ("FPassengerCount", "Integer"),
            ("FPayloadKg", "Integer"),
            ("FNoteText", "string"),
            ("FCreatedBy", "Integer"),
            ("FCreatedDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_FuelRecord",
        [
            ("FFuelId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FFuelDate", "TDateTime"),
            ("FLitres", "Double"),
            ("FCostPerLitre", "Double"),
            ("FTotalCost", "Double"),
            ("FOdometerKm", "Integer"),
            ("FDepotId", "Integer"),
            ("FFuelTypeCode", "Integer"),
            ("FReceiptNo", "string"),
            ("FApprovedBy", "Integer"),
        ],
    ),
    (
        "TFleet105_ServiceRecord",
        [
            ("FServiceId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FServiceDate", "TDateTime"),
            ("FServiceType", "Integer"),
            ("FOdometerKm", "Integer"),
            ("FTechnicianId", "Integer"),
            ("FLabourCost", "Double"),
            ("FPartsCost", "Double"),
            ("FTotalCost", "Double"),
            ("FNextServiceKm", "Integer"),
            ("FNextServiceDate", "TDateTime"),
            ("FWorkOrder", "string"),
            ("FNotes", "string"),
        ],
    ),
    (
        "TFleet105_Incident",
        [
            ("FIncidentId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FIncidentDate", "TDateTime"),
            ("FIncidentType", "Integer"),
            ("FSeverityCode", "Integer"),
            ("FLocationDesc", "string"),
            ("FDescription", "string"),
            ("FInjuryCount", "Integer"),
            ("FDamageCost", "Double"),
            ("FReportedBy", "Integer"),
            ("FResolvedDate", "TDateTime"),
            ("FIsResolved", "Boolean"),
        ],
    ),
    (
        "TFleet105_GpsTrack",
        [
            ("FTrackId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDeviceId", "Integer"),
            ("FTrackDate", "TDateTime"),
            ("FLatitude", "Double"),
            ("FLongitude", "Double"),
            ("FAltitude", "Double"),
            ("FSpeedKph", "Double"),
            ("FHeading", "Double"),
            ("FAccuracy", "Double"),
            ("FSatellites", "Integer"),
            ("FEventCode", "Integer"),
        ],
    ),
    (
        "TFleet105_Depot",
        [
            ("FDepotId", "Integer"),
            ("FDepotCode", "string"),
            ("FDepotName", "string"),
            ("FAddress", "string"),
            ("FCity", "string"),
            ("FPostCode", "string"),
            ("FPhone", "string"),
            ("FManagerId", "Integer"),
            ("FCapacityVehicles", "Integer"),
            ("FCapacityDrivers", "Integer"),
            ("FIsActive", "Boolean"),
            ("FOpenTime", "string"),
            ("FCloseTime", "string"),
        ],
    ),
    (
        "TFleet105_Employee",
        [
            ("FEmpId", "Integer"),
            ("FEmpNo", "string"),
            ("FFirstName", "string"),
            ("FLastName", "string"),
            ("FJobTitle", "string"),
            ("FDepartmentId", "Integer"),
            ("FDepotId", "Integer"),
            ("FHireDate", "TDateTime"),
            ("FTermDate", "TDateTime"),
            ("FSalary", "Double"),
            ("FIsActive", "Boolean"),
            ("FEmail", "string"),
            ("FPhone", "string"),
            ("FManagerId", "Integer"),
        ],
    ),
    (
        "TFleet105_Department",
        [
            ("FDeptId", "Integer"),
            ("FDeptCode", "string"),
            ("FDeptName", "string"),
            ("FManagerId", "Integer"),
            ("FCostCentre", "string"),
            ("FParentDeptId", "Integer"),
            ("FIsActive", "Boolean"),
            ("FHeadCount", "Integer"),
            ("FBudgetYear", "Integer"),
            ("FAnnualBudget", "Double"),
        ],
    ),
    (
        "TFleet105_Schedule",
        [
            ("FScheduleId", "Integer"),
            ("FRouteId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FDayOfWeek", "Integer"),
            ("FDepartureTime", "string"),
            ("FArrivalTime", "string"),
            ("FFrequencyMins", "Integer"),
            ("FValidFrom", "TDateTime"),
            ("FValidTo", "TDateTime"),
            ("FIsActive", "Boolean"),
            ("FSeasonCode", "Integer"),
        ],
    ),
    (
        "TFleet105_Passenger",
        [
            ("FPassId", "Integer"),
            ("FCardNo", "string"),
            ("FFirstName", "string"),
            ("FLastName", "string"),
            ("FDateOfBirth", "TDateTime"),
            ("FCardExpiry", "TDateTime"),
            ("FBalanceCents", "Integer"),
            ("FDiscountCode", "Integer"),
            ("FIsBlacklisted", "Boolean"),
            ("FLastTripDate", "TDateTime"),
            ("FTripCount", "Integer"),
            ("FDepotId", "Integer"),
        ],
    ),
    (
        "TFleet105_Trip",
        [
            ("FTripId", "Integer"),
            ("FJobId", "Integer"),
            ("FRouteId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FStartTime", "TDateTime"),
            ("FEndTime", "TDateTime"),
            ("FStartOdometer", "Integer"),
            ("FEndOdometer", "Integer"),
            ("FPassengerCount", "Integer"),
            ("FDelayMins", "Integer"),
            ("FStatusCode", "Integer"),
            ("FCancellationCode", "Integer"),
        ],
    ),
    (
        "TFleet105_PayrollEntry",
        [
            ("FPayId", "Integer"),
            ("FDriverId", "Integer"),
            ("FPeriodStart", "TDateTime"),
            ("FPeriodEnd", "TDateTime"),
            ("FTripCount", "Integer"),
            ("FTotalHours", "Double"),
            ("FBasicPay", "Double"),
            ("FOvertimePay", "Double"),
            ("FAllowancePay", "Double"),
            ("FDeductionTotal", "Double"),
            ("FNetPay", "Double"),
            ("FPaymentDate", "TDateTime"),
            ("FIsApproved", "Boolean"),
            ("FApprovedBy", "Integer"),
        ],
    ),
    (
        "TFleet105_MaintenancePlan",
        [
            ("FPlanId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FServiceType", "Integer"),
            ("FIntervalKm", "Integer"),
            ("FIntervalDays", "Integer"),
            ("FLastDoneKm", "Integer"),
            ("FLastDoneDate", "TDateTime"),
            ("FNextDueKm", "Integer"),
            ("FNextDueDate", "TDateTime"),
            ("FIsActive", "Boolean"),
            ("FPriority", "Integer"),
            ("FAssignedTech", "Integer"),
        ],
    ),
    (
        "TFleet105_PartStock",
        [
            ("FPartId", "Integer"),
            ("FPartNo", "string"),
            ("FDescription", "string"),
            ("FCategory", "Integer"),
            ("FUnitCost", "Double"),
            ("FStockQty", "Integer"),
            ("FReorderLevel", "Integer"),
            ("FReorderQty", "Integer"),
            ("FDepotId", "Integer"),
            ("FSupplierId", "Integer"),
            ("FIsObsolete", "Boolean"),
            ("FLastOrderDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_Supplier",
        [
            ("FSupplierId", "Integer"),
            ("FSupplierCode", "string"),
            ("FCompanyName", "string"),
            ("FContactName", "string"),
            ("FPhone", "string"),
            ("FEmail", "string"),
            ("FAddress", "string"),
            ("FCity", "string"),
            ("FPostCode", "string"),
            ("FPayTermsDays", "Integer"),
            ("FIsActive", "Boolean"),
            ("FRatingScore", "Integer"),
        ],
    ),
    (
        "TFleet105_PurchaseOrder",
        [
            ("FPoId", "Integer"),
            ("FPoNumber", "string"),
            ("FSupplierId", "Integer"),
            ("FOrderDate", "TDateTime"),
            ("FDeliveryDate", "TDateTime"),
            ("FDepotId", "Integer"),
            ("FTotalValue", "Double"),
            ("FStatusCode", "Integer"),
            ("FCreatedBy", "Integer"),
            ("FApprovedBy", "Integer"),
            ("FNotes", "string"),
            ("FIsUrgent", "Boolean"),
        ],
    ),
    (
        "TFleet105_Invoice",
        [
            ("FInvId", "Integer"),
            ("FInvNumber", "string"),
            ("FSupplierId", "Integer"),
            ("FPoId", "Integer"),
            ("FInvDate", "TDateTime"),
            ("FDueDate", "TDateTime"),
            ("FNetAmount", "Double"),
            ("FTaxAmount", "Double"),
            ("FTotalAmount", "Double"),
            ("FStatusCode", "Integer"),
            ("FPaidDate", "TDateTime"),
            ("FPaidAmount", "Double"),
            ("FIsReconciled", "Boolean"),
        ],
    ),
    (
        "TFleet105_CostCentre",
        [
            ("FCcId", "Integer"),
            ("FCcCode", "string"),
            ("FCcName", "string"),
            ("FDepotId", "Integer"),
            ("FManagerId", "Integer"),
            ("FBudgetYear", "Integer"),
            ("FAnnualBudget", "Double"),
            ("FSpentToDate", "Double"),
            ("FForecastTotal", "Double"),
            ("FIsActive", "Boolean"),
            ("FParentCcId", "Integer"),
        ],
    ),
    (
        "TFleet105_TyreRecord",
        [
            ("FTyreId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FPosition", "Integer"),
            ("FBrand", "string"),
            ("FSize", "string"),
            ("FFitDate", "TDateTime"),
            ("FOdometerFit", "Integer"),
            ("FRemoveDate", "TDateTime"),
            ("FOdometerRemove", "Integer"),
            ("FTreadDepthMm", "Double"),
            ("FIsRetread", "Boolean"),
            ("FConditionCode", "Integer"),
        ],
    ),
    (
        "TFleet105_PermitLicence",
        [
            ("FPermitId", "Integer"),
            ("FEntityType", "Integer"),
            ("FEntityId", "Integer"),
            ("FPermitType", "Integer"),
            ("FPermitNo", "string"),
            ("FIssuedBy", "string"),
            ("FIssueDate", "TDateTime"),
            ("FExpiryDate", "TDateTime"),
            ("FIssuedTo", "string"),
            ("FStatusCode", "Integer"),
            ("FNotes", "string"),
            ("FRenewalReminderDays", "Integer"),
        ],
    ),
    (
        "TFleet105_AlertEvent",
        [
            ("FAlertId", "Integer"),
            ("FDeviceId", "Integer"),
            ("FVehicleId", "Integer"),
            ("FDriverId", "Integer"),
            ("FAlertTime", "TDateTime"),
            ("FAlertType", "Integer"),
            ("FSeverityCode", "Integer"),
            ("FDescription", "string"),
            ("FLatitude", "Double"),
            ("FLongitude", "Double"),
            ("FSpeedKph", "Double"),
            ("FIsAcknowledged", "Boolean"),
            ("FAcknowledgedBy", "Integer"),
            ("FAcknowledgedTime", "TDateTime"),
        ],
    ),
    (
        "TFleet105_ReportDef",
        [
            ("FReportId", "Integer"),
            ("FReportCode", "string"),
            ("FReportName", "string"),
            ("FReportType", "Integer"),
            ("FCategoryCode", "Integer"),
            ("FQueryText", "string"),
            ("FParamList", "string"),
            ("FColumnList", "string"),
            ("FSortOrder", "string"),
            ("FIsActive", "Boolean"),
            ("FCreatedBy", "Integer"),
            ("FLastModified", "TDateTime"),
        ],
    ),
    (
        "TFleet105_UserAccount",
        [
            ("FUserId", "Integer"),
            ("FUserName", "string"),
            ("FPasswordHash", "string"),
            ("FFullName", "string"),
            ("FEmail", "string"),
            ("FRoleId", "Integer"),
            ("FDepotId", "Integer"),
            ("FIsActive", "Boolean"),
            ("FLastLogin", "TDateTime"),
            ("FFailedAttempts", "Integer"),
            ("FIsLocked", "Boolean"),
            ("FCreatedDate", "TDateTime"),
            ("FForceReset", "Boolean"),
        ],
    ),
    (
        "TFleet105_RolePermission",
        [
            ("FRoleId", "Integer"),
            ("FRoleName", "string"),
            ("FDescription", "string"),
            ("FIsAdmin", "Boolean"),
            ("FCanViewReports", "Boolean"),
            ("FCanEditVehicles", "Boolean"),
            ("FCanEditDrivers", "Boolean"),
            ("FCanApprovePayroll", "Boolean"),
            ("FCanManageUsers", "Boolean"),
            ("FCanViewCosts", "Boolean"),
            ("FIsActive", "Boolean"),
            ("FCreatedDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_AuditLog",
        [
            ("FAuditId", "Int64"),
            ("FUserId", "Integer"),
            ("FTableName", "string"),
            ("FRecordId", "Integer"),
            ("FActionCode", "Integer"),
            ("FActionTime", "TDateTime"),
            ("FOldValues", "string"),
            ("FNewValues", "string"),
            ("FIpAddress", "string"),
            ("FSessionId", "string"),
            ("FIsSuccessful", "Boolean"),
        ],
    ),
    (
        "TFleet105_Notification",
        [
            ("FNotifId", "Integer"),
            ("FUserId", "Integer"),
            ("FNotifType", "Integer"),
            ("FSubject", "string"),
            ("FMessageText", "string"),
            ("FCreatedDate", "TDateTime"),
            ("FReadDate", "TDateTime"),
            ("FIsRead", "Boolean"),
            ("FPriority", "Integer"),
            ("FRelatedTable", "string"),
            ("FRelatedId", "Integer"),
            ("FExpiryDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_DocumentStore",
        [
            ("FDocId", "Integer"),
            ("FEntityType", "Integer"),
            ("FEntityId", "Integer"),
            ("FDocType", "Integer"),
            ("FDocTitle", "string"),
            ("FFileName", "string"),
            ("FFilePath", "string"),
            ("FFileSizeKb", "Integer"),
            ("FMimeType", "string"),
            ("FUploadedBy", "Integer"),
            ("FUploadDate", "TDateTime"),
            ("FIsArchived", "Boolean"),
            ("FExpiryDate", "TDateTime"),
        ],
    ),
    (
        "TFleet105_GeoZone",
        [
            ("FZoneId", "Integer"),
            ("FZoneName", "string"),
            ("FZoneType", "Integer"),
            ("FCentreLatitude", "Double"),
            ("FCentreLongitude", "Double"),
            ("FRadiusMetres", "Integer"),
            ("FPolygonPoints", "string"),
            ("FDepotId", "Integer"),
            ("FSpeedLimitKph", "Integer"),
            ("FIsActive", "Boolean"),
            ("FValidFrom", "TDateTime"),
            ("FValidTo", "TDateTime"),
        ],
    ),
    (
        "TFleet105_ChecklistTemplate",
        [
            ("FTemplateId", "Integer"),
            ("FTemplateName", "string"),
            ("FChecklistType", "Integer"),
            ("FEntityType", "Integer"),
            ("FItemCount", "Integer"),
            ("FIsActive", "Boolean"),
            ("FVersion", "Integer"),
            ("FCreatedBy", "Integer"),
            ("FCreatedDate", "TDateTime"),
            ("FApprovedBy", "Integer"),
            ("FNotes", "string"),
        ],
    ),
    (
        "TFleet105_ChecklistResult",
        [
            ("FResultId", "Integer"),
            ("FTemplateId", "Integer"),
            ("FEntityId", "Integer"),
            ("FCompletedBy", "Integer"),
            ("FCompletedDate", "TDateTime"),
            ("FOverallResult", "Integer"),
            ("FFailCount", "Integer"),
            ("FPassCount", "Integer"),
            ("FSkipCount", "Integer"),
            ("FNotes", "string"),
            ("FVehicleId", "Integer"),
            ("FOdometerKm", "Integer"),
        ],
    ),
    (
        "TFleet105_ContractClient",
        [
            ("FClientId", "Integer"),
            ("FClientCode", "string"),
            ("FClientName", "string"),
            ("FContactName", "string"),
            ("FPhone", "string"),
            ("FEmail", "string"),
            ("FAddress", "string"),
            ("FCity", "string"),
            ("FContractStart", "TDateTime"),
            ("FContractEnd", "TDateTime"),
            ("FIsActive", "Boolean"),
            ("FDiscountPct", "Double"),
            ("FCreditLimit", "Double"),
            ("FPayTermsDays", "Integer"),
        ],
    ),
    (
        "TFleet105_BillingRecord",
        [
            ("FBillId", "Integer"),
            ("FClientId", "Integer"),
            ("FPeriodStart", "TDateTime"),
            ("FPeriodEnd", "TDateTime"),
            ("FTripCount", "Integer"),
            ("FTotalKm", "Double"),
            ("FBaseAmount", "Double"),
            ("FFuelSurcharge", "Double"),
            ("FTaxAmount", "Double"),
            ("FTotalAmount", "Double"),
            ("FStatusCode", "Integer"),
            ("FInvoiceDate", "TDateTime"),
            ("FPaidDate", "TDateTime"),
            ("FIsExported", "Boolean"),
        ],
    ),
]


# ── Generate interface declarations for all entities ─────────────────────────
def decl_entity(cls, fields):
    w(f"// ──────────────────────────────────────────────────────────────────────────")
    w(f"// {cls}")
    w(f"// ──────────────────────────────────────────────────────────────────────────")
    w(f"  {cls} = class(TFleetBaseEntity)")
    w("  private")
    for fn, ft in fields:
        w(f"    {fn}: {ft};")
    w("  public")
    w("    constructor Create; override;")
    w("    destructor Destroy; override;")
    w("    procedure Clear; override;")
    w(f"    procedure Assign(Source: {cls});")
    w("    function Validate: Boolean; override;")
    w("    function ToDelimitedString(const ADelim: WideString): WideString;")
    for fn, ft in fields:
        pn = prop_name(fn)
        rt = ret_type(ft)
        w(f"    function Get{pn}: {rt}; stdcall;")
        w(f"    procedure Set{pn}(const Value: {rt}); stdcall;")
    w("  published")
    for fn, ft in fields:
        pn = prop_name(fn)
        rt = ret_type(ft)
        w(f"    property {pn}: {rt} read Get{pn} write Set{pn};")
    w("  end;", "")


def decl_list(list_cls, item_cls):
    w(f"  {list_cls} = class(TFleetBaseList)")
    w("  private")
    w(f"    function GetItem(Index: Integer): {item_cls};")
    w("  public")
    w("    constructor Create; override;")
    w("    destructor Destroy; override;")
    w(f"    function Add: {item_cls};")
    w("    procedure Delete(Index: Integer); override;")
    w(f"    function FindById(const AId: Integer): {item_cls};")
    w(f"    function FindByCode(const ACode: WideString): {item_cls};")
    w("    function SortByName: Integer;")
    w("    function FilterByDepot(ADepotId: Integer): Integer;")
    w("    function ToDataSet(ADataSet: TClientDataSet): Integer;")
    w("    function LoadFromDataSet(ADataSet: TClientDataSet): Integer;")
    w("    function ExportCSV(const AFileName: WideString): Boolean;")
    w(f"    property Items[Index: Integer]: {item_cls} read GetItem; default;")
    w("  end;", "")


for cls, fields in ENTITIES:
    decl_entity(cls, fields)
    decl_list(cls + "List", cls)

# ── Implementation section ────────────────────────────────────────────────────
w("implementation", "")

# ── TFleet105_Device implementation ──────────────────────────────────────────
w("// ═══════════════════════════════════════════════════════════════════════════")
w("// TFleet105_Device")
w("// ═══════════════════════════════════════════════════════════════════════════")
w("")
w("constructor TFleet105_Device.Create;")
w("begin")
w("  inherited Create;")
w("  // Inicjalizacja pól urządzenia")
for fn, ft in DEVICE_FIELDS:
    if ft in ("Integer", "Cardinal"):
        w(f"  {fn} := 0;")
    elif ft == "Int64":
        w(f"  {fn} := 0;")
    elif ft == "Double":
        w(f"  {fn} := 0.0;")
    elif ft == "Boolean":
        w(f"  {fn} := False;")
    elif ft == "TDateTime":
        w(f"  {fn} := 0;")
    else:
        w(f"  {fn} := '';")
w("  FServerPort := 8080;")
w("  FMaxSpeed := 120;")
w("  FIdleTimeout := 300;")
w("  FReportInterval := 60;")
w("  FConfigVersion := 1;")
w("end;", "")

w("destructor TFleet105_Device.Destroy;")
w("begin")
w("  // Zwolnienie zasobów urządzenia")
w("  FEncryptionKey := '';")
w("  FAuthToken := '';")
w("  FDiagnosticData := '';")
w("  inherited Destroy;")
w("end;", "")

for fn, ft in DEVICE_FIELDS:
    pn = prop_name(fn)
    rt = ret_type(ft)
    w(f"function TFleet105_Device.Get{pn}: {rt};")
    w("begin")
    w(f"  // Pobierz {pn}")
    w(f"  Result := {fn};")
    w("end;", "")
    w(f"procedure TFleet105_Device.Set{pn}(const Value: {rt});")
    w("begin")
    w(f"  // Ustaw {pn}")
    w(f"  {fn} := Value;")
    w("end;", "")

w(
    "function TFleet105_Device.Connect(const AServerUrl: WideString; APort: Integer): Boolean;"
)
w("begin")
w("  // Nawiąż połączenie z serwerem FleetOps")
w("  FServerUrl := AServerUrl;")
w("  FServerPort := APort;")
w("  FConnectionMode := 1;")
w("  FIsOnline := True;")
w("  FLastContactTime := Now;")
w("  Inc(FSessionCount);")
w("  FErrorCode := 0;")
w("  FErrorMessage := '';")
w("  Result := FIsOnline;")
w("end;", "")

w("function TFleet105_Device.Disconnect: Boolean;")
w("begin")
w("  // Rozłącz urządzenie od serwera")
w("  FIsOnline := False;")
w("  FConnectionMode := 0;")
w("  FLastContactTime := Now;")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.SendHeartbeat: Boolean;")
w("begin")
w("  // Wyślij sygnał heartbeat do serwera")
w("  if not FIsOnline then")
w("  begin")
w("    FErrorMessage := 'Cannot send heartbeat: device not online';")
w("    Result := False;")
w("    Exit;")
w("  end;")
w("  FLastContactTime := Now;")
w("  Inc(FTotalMessagesSent);")
w("  Inc(FTotalBytesTransferred, 64);")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.ParseGpsData(const ARawData: WideString): Boolean;")
w("begin")
w("  // Parsuj dane GPS z formatu NMEA/binary")
w("  Result := False;")
w("  if Length(ARawData) < 10 then")
w("  begin")
w("    FErrorMessage := 'GPS data too short to parse';")
w("    Exit;")
w("  end;")
w("  FGpsFixTime := Now;")
w("  FGpsSatellites := 8;")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.UpdateFirmware(const AFirmwareFile: WideString): Boolean;")
w("begin")
w("  // Aktualizuj oprogramowanie układowe urządzenia")
w("  if not FIsOnline then")
w("  begin")
w("    FErrorMessage := 'Device not online - cannot update firmware';")
w("    Result := False;")
w("    Exit;")
w("  end;")
w("  if AFirmwareFile = '' then")
w("  begin")
w("    FErrorMessage := 'Firmware file path not specified';")
w("    Result := False;")
w("    Exit;")
w("  end;")
w("  Inc(FConfigVersion);")
w("  FFirmwareVersion := 'UPDATING';")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.ResetDevice: Boolean;")
w("begin")
w("  // Zresetuj urządzenie do domyślnych ustawień fabrycznych")
w("  FErrorCode := 0;")
w("  FErrorMessage := '';")
w("  FAlertFlags := 0;")
w("  FDataQueueSize := 0;")
w("  FLastResetTime := Now;")
w("  FIsOnline := False;")
w("  FConnectionMode := 0;")
w("  FGpsLatitude := 0.0;")
w("  FGpsLongitude := 0.0;")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.RunDiagnostics: WideString;")
w("begin")
w("  // Uruchom pełną diagnostykę urządzenia")
w("  Result := Format('[FleetOps Diagnostics] DeviceId=%d Serial=%s Online=%s ' +")
w("    'Battery=%d%% Signal=%d%% GPS=(%.6f,%.6f) Altitude=%.1fm Speed=%.1fkph ' +")
w("    'Firmware=%s Hardware=%s Config=%d Queue=%d Sent=%d Recv=%d Bytes=%d',")
w("    [FDeviceId, FDeviceSerial, BoolToStr(FIsOnline, True),")
w("     FBatteryLevel, FSignalStrength, FGpsLatitude, FGpsLongitude,")
w("     FGpsAltitude, FGpsSpeed, FFirmwareVersion, FHardwareRevision,")
w("     FConfigVersion, FDataQueueSize, FTotalMessagesSent,")
w("     FTotalMessagesReceived, FTotalBytesTransferred]);")
w("end;", "")

w("function TFleet105_Device.ExportConfig(const AFileName: WideString): Boolean;")
w("begin")
w("  // Eksportuj konfigurację urządzenia do pliku INI/XML")
w("  Result := False;")
w("  if AFileName = '' then Exit;")
w("  try")
w("    // Real implementation: write to TIniFile or XML document")
w("    Result := True;")
w("  except")
w("    on E: Exception do")
w("      FErrorMessage := 'ExportConfig failed: ' + E.Message;")
w("  end;")
w("end;", "")

w("function TFleet105_Device.ImportConfig(const AFileName: WideString): Boolean;")
w("begin")
w("  // Importuj konfigurację urządzenia z pliku")
w("  Result := False;")
w("  if AFileName = '' then Exit;")
w("  try")
w("    Inc(FConfigVersion);")
w("    Result := True;")
w("  except")
w("    on E: Exception do")
w("      FErrorMessage := 'ImportConfig failed: ' + E.Message;")
w("  end;")
w("end;", "")

w("function TFleet105_Device.ValidateAuth: Boolean;")
w("begin")
w("  // Sprawdź poprawność tokena autoryzacji")
w("  Result := (FAuthToken <> '') and (Length(FAuthToken) >= 32);")
w("  if not Result then")
w("    FErrorMessage := 'Authentication token invalid or expired';")
w("end;", "")

w("function TFleet105_Device.EncryptPayload(const AData: WideString): WideString;")
w("begin")
w("  // Zaszyfruj ładunek danych do transmisji")
w("  if FEncryptionKey = '' then")
w("  begin")
w("    Result := AData;")
w("    Exit;")
w("  end;")
w("  // Placeholder: real implementation would use AES-256-CBC")
w("  Result := AData;")
w("end;", "")

w("function TFleet105_Device.DecryptPayload(const AData: WideString): WideString;")
w("begin")
w("  // Odszyfruj odebrany ładunek danych")
w("  if FEncryptionKey = '' then")
w("  begin")
w("    Result := AData;")
w("    Exit;")
w("  end;")
w("  // Placeholder: real implementation would use AES-256-CBC")
w("  Result := AData;")
w("end;", "")

w(
    "function TFleet105_Device.QueueMessage(const AMsg: WideString; APriority: Integer): Boolean;"
)
w("begin")
w("  // Dodaj wiadomość do kolejki wysyłki z priorytetem")
w("  if FDataQueueSize >= 1000 then")
w("  begin")
w("    FErrorMessage := 'Message queue capacity exceeded (max 1000)';")
w("    Result := False;")
w("    Exit;")
w("  end;")
w("  Inc(FDataQueueSize);")
w("  Result := True;")
w("end;", "")

w("function TFleet105_Device.FlushQueue: Integer;")
w("begin")
w("  // Opróżnij kolejkę wiadomości — wyślij wszystkie oczekujące")
w("  Result := FDataQueueSize;")
w("  if FDataQueueSize > 0 then")
w("  begin")
w("    Inc(FTotalMessagesSent, FDataQueueSize);")
w("    Inc(FTotalBytesTransferred, Int64(FDataQueueSize) * 256);")
w("    FDataQueueSize := 0;")
w("    FLastContactTime := Now;")
w("  end;")
w("end;", "")

w("function TFleet105_Device.GetStatusReport: WideString;")
w("begin")
w("  // Zwróć pełny raport statusu urządzenia")
w("  Result := Format('[Status] ID:%d Serial:%s Name:%s Online:%s Battery:%d%% ' +")
w("    'Signal:%d%% GPS:(%.6f,%.6f,%.1fm) Speed:%.1fkph Heading:%.1f ' +")
w("    'Firmware:%s Hardware:%s ConfigVer:%d MaxSpeed:%d ' +")
w("    'Queued:%d Sent:%d Recv:%d Bytes:%d Sessions:%d',")
w("    [FDeviceId, FDeviceSerial, FDeviceName, BoolToStr(FIsOnline,True),")
w("     FBatteryLevel, FSignalStrength, FGpsLatitude, FGpsLongitude, FGpsAltitude,")
w("     FGpsSpeed, FGpsHeading, FFirmwareVersion, FHardwareRevision, FConfigVersion,")
w("     FMaxSpeed, FDataQueueSize, FTotalMessagesSent, FTotalMessagesReceived,")
w("     FTotalBytesTransferred, FSessionCount]);")
w("end;", "")


# ── Entity implementations ────────────────────────────────────────────────────
def impl_entity(cls, fields):
    w(f"// ═══════════════════════════════════════════════════════════════════════════")
    w(f"// {cls}")
    w(f"// ═══════════════════════════════════════════════════════════════════════════")
    w("")
    w(f"constructor {cls}.Create;")
    w("begin")
    w("  inherited Create;")
    w("  // Inicjalizacja pól")
    for fn, ft in fields:
        if ft in ("Integer", "Cardinal"):
            w(f"  {fn} := 0;")
        elif ft == "Int64":
            w(f"  {fn} := 0;")
        elif ft == "Double":
            w(f"  {fn} := 0.0;")
        elif ft == "Boolean":
            w(f"  {fn} := False;")
        elif ft == "TDateTime":
            w(f"  {fn} := 0;")
        else:
            w(f"  {fn} := '';")
    w("end;", "")

    w(f"destructor {cls}.Destroy;")
    w("begin")
    w("  // Zwolnij zasoby")
    w("  inherited Destroy;")
    w("end;", "")

    w(f"procedure {cls}.Clear;")
    w("begin")
    w("  inherited Clear;")
    for fn, ft in fields:
        if ft in ("Integer", "Cardinal"):
            w(f"  {fn} := 0;")
        elif ft == "Int64":
            w(f"  {fn} := 0;")
        elif ft == "Double":
            w(f"  {fn} := 0.0;")
        elif ft == "Boolean":
            w(f"  {fn} := False;")
        elif ft == "TDateTime":
            w(f"  {fn} := 0;")
        else:
            w(f"  {fn} := '';")
    w("end;", "")

    w(f"procedure {cls}.Assign(Source: {cls});")
    w("begin")
    w("  if not Assigned(Source) then Exit;")
    w("  // Kopiuj wszystkie pola ze źródłowego obiektu")
    for fn, ft in fields:
        w(f"  {fn} := Source.{fn};")
    w("end;", "")

    w(f"function {cls}.Validate: Boolean;")
    w("begin")
    w("  // Sprawdź poprawność danych encji")
    if fields:
        w(f"  Result := ({fields[0][0]} >= 0);")
    else:
        w("  Result := True;")
    w("end;", "")

    w(f"function {cls}.ToDelimitedString(const ADelim: WideString): WideString;")
    w("var")
    w("  LParts: TStringList;")
    w("begin")
    w("  // Zwróć dane encji jako łańcuch rozdzielony separatorem")
    w("  LParts := TStringList.Create;")
    w("  try")
    for fn, ft in fields:
        if ft == "string":
            w(f"    LParts.Add({fn});")
        elif ft in ("Integer", "Cardinal"):
            w(f"    LParts.Add(IntToStr({fn}));")
        elif ft == "Int64":
            w(f"    LParts.Add(IntToStr({fn}));")
        elif ft == "Double":
            w(f"    LParts.Add(FloatToStr({fn}));")
        elif ft == "Boolean":
            w(f"    LParts.Add(BoolToStr({fn}, True));")
        elif ft == "TDateTime":
            w(f"    LParts.Add(DateTimeToStr({fn}));")
        else:
            w(f"    LParts.Add({fn});")
    w("    Result := LParts.CommaText;")
    w("  finally")
    w("    LParts.Free;")
    w("  end;")
    w("end;", "")

    for fn, ft in fields:
        pn = prop_name(fn)
        rt = ret_type(ft)
        w(f"function {cls}.Get{pn}: {rt};")
        w("begin")
        w(f"  // Pobierz wartość pola {pn}")
        w(f"  Result := {fn};")
        w("end;", "")
        w(f"procedure {cls}.Set{pn}(const Value: {rt});")
        w("begin")
        w(f"  // Ustaw wartość pola {pn}")
        w(f"  {fn} := Value;")
        w("end;", "")


def impl_list(list_cls, item_cls):
    w(f"// ── {list_cls} ──")
    w(f"constructor {list_cls}.Create;")
    w("begin")
    w("  inherited Create;")
    w("  FOwnsObjects := True;")
    w("end;", "")

    w(f"destructor {list_cls}.Destroy;")
    w("begin")
    w("  inherited Destroy;")
    w("end;", "")

    w(f"function {list_cls}.GetItem(Index: Integer): {item_cls};")
    w("begin")
    w(f"  Result := {item_cls}(FList[Index]);")
    w("end;", "")

    w(f"function {list_cls}.Add: {item_cls};")
    w("begin")
    w("  // Dodaj nowy element do listy")
    w(f"  Result := {item_cls}.Create;")
    w("  FList.Add(Result);")
    w("end;", "")

    w(f"procedure {list_cls}.Delete(Index: Integer);")
    w("begin")
    w("  // Usuń element z listy")
    w("  if (Index < 0) or (Index >= FList.Count) then Exit;")
    w("  if FOwnsObjects then")
    w("    TObject(FList[Index]).Free;")
    w("  FList.Delete(Index);")
    w("end;", "")

    w(f"function {list_cls}.FindById(const AId: Integer): {item_cls};")
    w("var")
    w("  I: Integer;")
    w("  LItem: " + item_cls + ";")
    w("begin")
    w("  // Wyszukaj element po identyfikatorze")
    w("  Result := nil;")
    w("  for I := 0 to FList.Count - 1 do")
    w("  begin")
    w("    LItem := GetItem(I);")
    w("    if Assigned(LItem) then")
    w("      if LItem.EntityId = AId then")
    w("      begin")
    w("        Result := LItem;")
    w("        Exit;")
    w("      end;")
    w("  end;")
    w("end;", "")

    w(f"function {list_cls}.FindByCode(const ACode: WideString): {item_cls};")
    w("var")
    w("  I: Integer;")
    w("begin")
    w("  // Wyszukaj element po kodzie/nazwie")
    w("  Result := nil;")
    w("  for I := 0 to FList.Count - 1 do")
    w("  begin")
    w("    if GetItem(I).EntityCode = ACode then")
    w("    begin")
    w("      Result := GetItem(I);")
    w("      Exit;")
    w("    end;")
    w("  end;")
    w("end;", "")

    w(f"function {list_cls}.SortByName: Integer;")
    w("begin")
    w("  // Sortuj elementy listy według nazwy")
    w("  Result := FList.Count;")
    w("  FSorted := True;")
    w("end;", "")

    w(f"function {list_cls}.FilterByDepot(ADepotId: Integer): Integer;")
    w("begin")
    w("  // Filtruj elementy listy według depozytu")
    w("  FFilterActive := True;")
    w("  Result := FList.Count;")
    w("end;", "")

    w(f"function {list_cls}.ToDataSet(ADataSet: TClientDataSet): Integer;")
    w("var")
    w("  I: Integer;")
    w("begin")
    w("  // Eksportuj listę do zbioru danych TClientDataSet")
    w("  Result := 0;")
    w("  if not Assigned(ADataSet) then Exit;")
    w("  ADataSet.EmptyDataSet;")
    w("  for I := 0 to FList.Count - 1 do")
    w("  begin")
    w("    ADataSet.Append;")
    w("    // Field mapping would occur here")
    w("    ADataSet.Post;")
    w("    Inc(Result);")
    w("  end;")
    w("end;", "")

    w(f"function {list_cls}.LoadFromDataSet(ADataSet: TClientDataSet): Integer;")
    w("var")
    w(f"  LItem: {item_cls};")
    w("begin")
    w("  // Wczytaj listę ze zbioru danych TClientDataSet")
    w("  Result := 0;")
    w("  if not Assigned(ADataSet) then Exit;")
    w("  if ADataSet.IsEmpty then Exit;")
    w("  ADataSet.First;")
    w("  while not ADataSet.Eof do")
    w("  begin")
    w("    LItem := Add;")
    w("    // LItem.LoadFromDataSet(ADataSet) would map fields")
    w("    ADataSet.Next;")
    w("    Inc(Result);")
    w("  end;")
    w("end;", "")

    w(f"function {list_cls}.ExportCSV(const AFileName: WideString): Boolean;")
    w("var")
    w("  LFile: TextFile;")
    w("  I: Integer;")
    w("begin")
    w("  // Eksportuj listę do pliku CSV")
    w("  Result := False;")
    w("  if AFileName = '' then Exit;")
    w("  AssignFile(LFile, AFileName);")
    w("  try")
    w("    Rewrite(LFile);")
    w("    try")
    w("      for I := 0 to FList.Count - 1 do")
    w("        WriteLn(LFile, GetItem(I).ToDelimitedString(','));")
    w("      Result := True;")
    w("    finally")
    w("      CloseFile(LFile);")
    w("    end;")
    w("  except")
    w("    Result := False;")
    w("  end;")
    w("end;", "")


for cls, fields in ENTITIES:
    impl_entity(cls, fields)
    impl_list(cls + "List", cls)

# ── Footer ────────────────────────────────────────────────────────────────────
w("initialization")
w("  // Inicjalizacja modułu VehicleData.classes")
w("  // Module VehicleData.classes initialized on startup")
w("")
w("finalization")
w("  // Zwolnienie zasobów modułu VehicleData.classes")
w("  // Release resources on shutdown")
w("")
w("end.")

content = "\n".join(lines) + "\n"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Written: {len(lines)} lines")
