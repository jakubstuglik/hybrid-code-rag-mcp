unit AppConst;

interface

const
  // ── Application identity ─────────────────────────────────────────────────
  APP_NAME    = 'FleetOps';
  APP_VERSION = '4.2.1';
  APP_BUILD   = 20250115;
  APP_VENDOR  = 'FleetOps Pty Ltd';

  // ── Database settings ─────────────────────────────────────────────────────
  DB_DEFAULT_TIMEOUT      = 30;
  DB_MAX_CONNECTIONS      = 50;
  DB_COMMAND_TIMEOUT      = 120;
  DB_CONNECTION_RETRIES   = 3;
  DB_RETRY_DELAY_MS       = 2000;

  // ── API settings ──────────────────────────────────────────────────────────
  API_VERSION             = 'v3';
  API_DEFAULT_TIMEOUT_MS  = 30000;
  API_MAX_RETRIES         = 3;
  API_PAGE_SIZE_DEFAULT   = 50;
  API_PAGE_SIZE_MAX       = 500;

  // ── Cache settings ────────────────────────────────────────────────────────
  CACHE_DEFAULT_TTL_SECS  = 300;
  CACHE_MAX_ENTRIES       = 10000;
  CACHE_PRUNE_INTERVAL    = 60;

  // ── GPS constants ─────────────────────────────────────────────────────────
  GPS_EARTH_RADIUS_KM     = 6371.0;
  GPS_MAX_SPEED_KMPH      = 250;
  GPS_MIN_ACCURACY_M      = 50.0;
  GPS_STALE_THRESHOLD_MIN = 15;
  GPS_SPEEDING_MARGIN_KPH = 5;
  GPS_IDLE_SPEED_KPH      = 3.0;
  GPS_IDLE_TIMEOUT_MIN    = 5;

  // ── Job status codes ──────────────────────────────────────────────────────
  JOB_STATUS_SCHEDULED    = 1;
  JOB_STATUS_DISPATCHED   = 2;
  JOB_STATUS_IN_PROGRESS  = 3;
  JOB_STATUS_COMPLETED    = 4;
  JOB_STATUS_CANCELLED    = 5;
  JOB_STATUS_NO_SHOW      = 6;
  JOB_STATUS_EXCEPTION    = 7;
  JOB_STATUS_TRANSFERRED  = 8;

  // ── Vehicle status codes ──────────────────────────────────────────────────
  VEH_STATUS_AVAILABLE    = 1;
  VEH_STATUS_ON_TRIP      = 2;
  VEH_STATUS_IN_SERVICE   = 3;
  VEH_STATUS_OUT_OF_ORDER = 4;
  VEH_STATUS_DECOMMISSION = 5;
  VEH_STATUS_RESERVED     = 6;

  // ── Driver status codes ───────────────────────────────────────────────────
  DRV_STATUS_AVAILABLE    = 1;
  DRV_STATUS_ON_DUTY      = 2;
  DRV_STATUS_OFF_DUTY     = 3;
  DRV_STATUS_ON_LEAVE     = 4;
  DRV_STATUS_SUSPENDED    = 5;
  DRV_STATUS_RESIGNED     = 6;

  // ── Priority codes ────────────────────────────────────────────────────────
  PRIORITY_CRITICAL       = 1;
  PRIORITY_HIGH           = 2;
  PRIORITY_NORMAL         = 3;
  PRIORITY_LOW            = 4;
  PRIORITY_BULK           = 5;

  // ── Report type codes ─────────────────────────────────────────────────────
  REPORT_TYPE_VEHICLE_SUMMARY         = 1;
  REPORT_TYPE_VEHICLE_DETAIL          = 2;
  REPORT_TYPE_VEHICLE_MILEAGE         = 3;
  REPORT_TYPE_VEHICLE_SERVICE         = 4;
  REPORT_TYPE_VEHICLE_INSPECTION      = 5;
  REPORT_TYPE_VEHICLE_INSURANCE       = 6;
  REPORT_TYPE_VEHICLE_UTILISATION     = 7;
  REPORT_TYPE_VEHICLE_AGE             = 8;
  REPORT_TYPE_DRIVER_ACTIVITY         = 10;
  REPORT_TYPE_DRIVER_PAYROLL          = 11;
  REPORT_TYPE_DRIVER_HOURS            = 12;
  REPORT_TYPE_DRIVER_PERFORMANCE      = 13;
  REPORT_TYPE_DRIVER_LICENCE          = 14;
  REPORT_TYPE_DRIVER_ATTENDANCE       = 15;
  REPORT_TYPE_DRIVER_TRIPS            = 16;
  REPORT_TYPE_DRIVER_INFRINGEMENTS    = 17;
  REPORT_TYPE_JOB_DISPATCH            = 20;
  REPORT_TYPE_JOB_SUMMARY             = 21;
  REPORT_TYPE_JOB_PERFORMANCE         = 22;
  REPORT_TYPE_JOB_DELAY               = 23;
  REPORT_TYPE_JOB_CANCELLATIONS       = 24;
  REPORT_TYPE_JOB_COMPLETION          = 25;
  REPORT_TYPE_JOB_BY_ROUTE            = 26;
  REPORT_TYPE_JOB_BY_CUSTOMER         = 27;
  REPORT_TYPE_FUEL_USAGE              = 30;
  REPORT_TYPE_FUEL_COST               = 31;
  REPORT_TYPE_FUEL_EFFICIENCY         = 32;
  REPORT_TYPE_FUEL_BY_VEHICLE         = 33;
  REPORT_TYPE_FUEL_BY_DRIVER          = 34;
  REPORT_TYPE_FUEL_BY_DEPOT           = 35;
  REPORT_TYPE_FUEL_PRICE_HISTORY      = 36;
  REPORT_TYPE_CARBON_EMISSIONS        = 37;
  REPORT_TYPE_KPI_SUMMARY             = 40;
  REPORT_TYPE_KPI_TREND               = 41;
  REPORT_TYPE_KPI_BY_DRIVER           = 42;
  REPORT_TYPE_KPI_BY_DEPOT            = 43;
  REPORT_TYPE_OTP_REPORT              = 44;
  REPORT_TYPE_PUNCTUALITY             = 45;
  REPORT_TYPE_PAYROLL_SUMMARY         = 50;
  REPORT_TYPE_PAYROLL_DETAIL          = 51;
  REPORT_TYPE_TIMESHEET_SUMMARY       = 52;
  REPORT_TYPE_OVERTIME_SUMMARY        = 53;
  REPORT_TYPE_ALLOWANCE_SUMMARY       = 54;
  REPORT_TYPE_LEAVE_BALANCE           = 55;
  REPORT_TYPE_COMPLIANCE_LICENCE      = 60;
  REPORT_TYPE_COMPLIANCE_INSURANCE    = 61;
  REPORT_TYPE_COMPLIANCE_INSPECTION   = 62;
  REPORT_TYPE_COMPLIANCE_SERVICE      = 63;
  REPORT_TYPE_INCIDENT_LOG            = 64;
  REPORT_TYPE_INFRINGEMENT_LOG        = 65;
  REPORT_TYPE_INVOICE_SUMMARY         = 70;
  REPORT_TYPE_INVOICE_DETAIL          = 71;
  REPORT_TYPE_REVENUE_ANALYSIS        = 72;
  REPORT_TYPE_COST_ANALYSIS           = 73;
  REPORT_TYPE_PROFIT_MARGIN           = 74;
  REPORT_TYPE_DEBTOR_AGING            = 75;
  REPORT_TYPE_CONTRACT_SUMMARY        = 76;
  REPORT_TYPE_GPS_SPEEDING            = 80;
  REPORT_TYPE_GPS_GEOFENCE            = 81;
  REPORT_TYPE_GPS_IDLE_TIME           = 82;
  REPORT_TYPE_GPS_MILEAGE             = 83;
  REPORT_TYPE_GPS_ROUTE_DEVIATION     = 84;
  REPORT_TYPE_GPS_TRACKING_HISTORY    = 85;

  // ── Report format codes ───────────────────────────────────────────────────
  REPORT_FORMAT_PDF       = 1;
  REPORT_FORMAT_EXCEL     = 2;
  REPORT_FORMAT_CSV       = 3;
  REPORT_FORMAT_HTML      = 4;
  REPORT_FORMAT_XML       = 5;
  REPORT_FORMAT_JSON      = 6;
  REPORT_FORMAT_WORD      = 7;
  REPORT_FORMAT_TEXT      = 8;
  REPORT_FORMAT_PREVIEW   = 9;

  // ── Incident severity ─────────────────────────────────────────────────────
  INCIDENT_SEVERITY_MINOR    = 1;
  INCIDENT_SEVERITY_MODERATE = 2;
  INCIDENT_SEVERITY_SERIOUS  = 3;
  INCIDENT_SEVERITY_CRITICAL = 4;
  INCIDENT_SEVERITY_FATAL    = 5;

  // ── Alert type codes ──────────────────────────────────────────────────────
  ALERT_TYPE_SPEED            = 1;
  ALERT_TYPE_GEOFENCE_ENTER   = 2;
  ALERT_TYPE_GEOFENCE_EXIT    = 3;
  ALERT_TYPE_IDLE_TIMEOUT     = 4;
  ALERT_TYPE_DEVICE_OFFLINE   = 5;
  ALERT_TYPE_LOW_BATTERY      = 6;
  ALERT_TYPE_HARSH_BRAKING    = 7;
  ALERT_TYPE_HARSH_ACCEL      = 8;
  ALERT_TYPE_LICENCE_EXPIRY   = 9;
  ALERT_TYPE_SERVICE_DUE      = 10;
  ALERT_TYPE_INSURANCE_EXPIRY = 11;
  ALERT_TYPE_INSPECTION_DUE   = 12;
  ALERT_TYPE_JOB_LATE         = 13;
  ALERT_TYPE_JOB_NO_SHOW      = 14;
  ALERT_TYPE_FUEL_ANOMALY     = 15;
  ALERT_TYPE_BREAKDOWN        = 16;

  // ── Service interval defaults ─────────────────────────────────────────────
  SERVICE_INTERVAL_KM      = 10000.0;
  SERVICE_INTERVAL_DAYS    = 180;
  INSPECTION_INTERVAL_DAYS = 365;
  INSURANCE_WARNING_DAYS   = 30;
  LICENCE_WARNING_DAYS     = 60;

  // ── Pagination defaults ───────────────────────────────────────────────────
  PAGE_SIZE_SMALL   = 10;
  PAGE_SIZE_DEFAULT = 50;
  PAGE_SIZE_LARGE   = 200;
  PAGE_SIZE_MAX     = 1000;

  // ── Session / auth ────────────────────────────────────────────────────────
  SESSION_TIMEOUT_MINS      = 60;
  PASSWORD_MIN_LENGTH       = 8;
  PASSWORD_EXPIRY_DAYS      = 90;
  MAX_FAILED_LOGINS         = 5;
  LOCKOUT_DURATION_MINS     = 30;
  TOKEN_EXPIRY_HOURS        = 24;
  REFRESH_TOKEN_EXPIRY_DAYS = 30;

  // ── File / export paths ───────────────────────────────────────────────────
  EXPORT_PATH = 'exports\';
  REPORT_PATH = 'reports\';
  LOG_PATH    = 'logs\';
  TEMP_PATH   = 'temp\';
  UPLOAD_PATH = 'uploads\';
  BACKUP_PATH = 'backup\';

  // ── Max sizes ─────────────────────────────────────────────────────────────
  MAX_UPLOAD_SIZE_MB   = 50;
  MAX_EXPORT_ROWS      = 100000;
  MAX_LOG_FILE_SIZE_MB = 100;
  MAX_LOG_ROTATE_COUNT = 10;
  MAX_BATCH_SIZE       = 500;
  MAX_IMPORT_ROWS      = 50000;

  // ── Timeouts (milliseconds) ───────────────────────────────────────────────
  TIMEOUT_DB_CONNECT_MS = 10000;
  TIMEOUT_DB_COMMAND_MS = 120000;
  TIMEOUT_API_MS        = 30000;
  TIMEOUT_GPS_MS        = 5000;
  TIMEOUT_DEVICE_MS     = 15000;
  TIMEOUT_EXPORT_MS     = 300000;
  TIMEOUT_REPORT_MS     = 600000;

  // ── MQTT / messaging ──────────────────────────────────────────────────────
  MQTT_QOS_AT_MOST_ONCE   = 0;
  MQTT_QOS_AT_LEAST_ONCE  = 1;
  MQTT_QOS_EXACTLY_ONCE   = 2;
  MQTT_DEFAULT_PORT       = 1883;
  MQTT_SSL_PORT           = 8883;
  MQTT_KEEPALIVE_SECS     = 60;
  MQTT_RECONNECT_DELAY_MS = 5000;

  // ── Notification channels ─────────────────────────────────────────────────
  NOTIFY_CHANNEL_EMAIL   = 1;
  NOTIFY_CHANNEL_SMS     = 2;
  NOTIFY_CHANNEL_PUSH    = 3;
  NOTIFY_CHANNEL_WEBHOOK = 4;
  NOTIFY_CHANNEL_IN_APP  = 5;

  // ── User role codes ───────────────────────────────────────────────────────
  ROLE_SUPER_ADMIN = 1;
  ROLE_ADMIN       = 2;
  ROLE_MANAGER     = 3;
  ROLE_DISPATCHER  = 4;
  ROLE_DRIVER      = 5;
  ROLE_MECHANIC    = 6;
  ROLE_FINANCE     = 7;
  ROLE_READ_ONLY   = 8;

  // ── Depot / region codes ──────────────────────────────────────────────────
  DEPOT_ALL  = 0;
  REGION_ALL = 0;

  // ── Maintenance job types ─────────────────────────────────────────────────
  MAINT_TYPE_SERVICE    = 1;
  MAINT_TYPE_INSPECTION = 2;
  MAINT_TYPE_REPAIR     = 3;
  MAINT_TYPE_TYRE       = 4;
  MAINT_TYPE_BODY       = 5;
  MAINT_TYPE_ELECTRICAL = 6;
  MAINT_TYPE_AIRCON     = 7;

  // ── Odometer correction limits ────────────────────────────────────────────
  ODO_MAX_CORRECTION_KM  = 500;
  ODO_ROLLOVER_THRESHOLD = 999999;

  // ── Fuel card / transaction ───────────────────────────────────────────────
  FUEL_CARD_ACTIVE        = 1;
  FUEL_CARD_SUSPENDED     = 2;
  FUEL_CARD_CANCELLED     = 3;
  FUEL_TRANSACTION_CREDIT = 1;
  FUEL_TRANSACTION_DEBIT  = 2;

  // ── Geofence types ────────────────────────────────────────────────────────
  GEOFENCE_TYPE_CIRCLE   = 1;
  GEOFENCE_TYPE_POLYGON  = 2;
  GEOFENCE_TYPE_CORRIDOR = 3;

  // ── Route optimisation ────────────────────────────────────────────────────
  ROUTE_OPT_NONE     = 0;
  ROUTE_OPT_DISTANCE = 1;
  ROUTE_OPT_TIME     = 2;
  ROUTE_OPT_COST     = 3;

  // ── Map tile providers ────────────────────────────────────────────────────
  MAP_PROVIDER_OSM    = 1;
  MAP_PROVIDER_GOOGLE = 2;
  MAP_PROVIDER_BING   = 3;
  MAP_PROVIDER_HERE   = 4;

  // ── Default map zoom levels ───────────────────────────────────────────────
  MAP_ZOOM_CITY   = 12;
  MAP_ZOOM_SUBURB = 15;
  MAP_ZOOM_STREET = 17;
  MAP_ZOOM_MIN    = 3;
  MAP_ZOOM_MAX    = 19;

  // ── Audit action codes ────────────────────────────────────────────────────
  AUDIT_ACTION_CREATE   = 1;
  AUDIT_ACTION_UPDATE   = 2;
  AUDIT_ACTION_DELETE   = 3;
  AUDIT_ACTION_LOGIN    = 4;
  AUDIT_ACTION_LOGOUT   = 5;
  AUDIT_ACTION_EXPORT   = 6;
  AUDIT_ACTION_IMPORT   = 7;
  AUDIT_ACTION_APPROVE  = 8;
  AUDIT_ACTION_REJECT   = 9;
  AUDIT_ACTION_DISPATCH = 10;

  // ── Integration / webhook events ──────────────────────────────────────────
  WEBHOOK_EVENT_JOB_CREATE    = 'job.created';
  WEBHOOK_EVENT_JOB_UPDATE    = 'job.updated';
  WEBHOOK_EVENT_JOB_COMPLETE  = 'job.completed';
  WEBHOOK_EVENT_JOB_CANCEL    = 'job.cancelled';
  WEBHOOK_EVENT_GPS_ALERT     = 'gps.alert';
  WEBHOOK_EVENT_DEVICE_ONLINE = 'device.online';
  WEBHOOK_EVENT_DEVICE_OFFL   = 'device.offline';
  WEBHOOK_EVENT_MAINT_DUE     = 'maintenance.due';

  // ── File size helpers ─────────────────────────────────────────────────────
  CONST_1GB = 1073741824;
  CONST_1MB = 1048576;
  CONST_1KB = 1024;

  // ── Scheduling bitmasks ───────────────────────────────────────────────────
  SCHED_SUNDAY    = 1;
  SCHED_MONDAY    = 2;
  SCHED_TUESDAY   = 4;
  SCHED_WEDNESDAY = 8;
  SCHED_THURSDAY  = 16;
  SCHED_FRIDAY    = 32;
  SCHED_SATURDAY  = 64;
  SCHED_WEEKDAYS  = 62;    // Mon–Fri
  SCHED_WEEKEND   = 65;    // Sat+Sun
  SCHED_ALL_DAYS  = 127;

  // ── Document / attachment types ───────────────────────────────────────────
  DOC_TYPE_LICENCE      = 1;
  DOC_TYPE_INSURANCE    = 2;
  DOC_TYPE_REGISTRATION = 3;
  DOC_TYPE_INSPECTION   = 4;
  DOC_TYPE_INCIDENT     = 5;
  DOC_TYPE_INVOICE      = 6;
  DOC_TYPE_CONTRACT     = 7;
  DOC_TYPE_OTHER        = 99;

  // ── Currency / locale ─────────────────────────────────────────────────────
  DEFAULT_CURRENCY_CODE    = 'AUD';
  DEFAULT_CURRENCY_SYMBOL  = '$';
  DEFAULT_DATE_FORMAT      = 'dd/mm/yyyy';
  DEFAULT_TIME_FORMAT      = 'hh:nn:ss';
  DEFAULT_DATETIME_FORMAT  = 'dd/mm/yyyy hh:nn:ss';
  DEFAULT_DECIMAL_SEP      = '.';
  DEFAULT_THOUSAND_SEP     = ',';

  // ── Weight / dimension limits ─────────────────────────────────────────────
  MAX_PAYLOAD_KG         = 25000.0;
  MAX_VEHICLE_LENGTH_M   = 20.0;
  MAX_VEHICLE_WIDTH_M    = 2.5;
  MAX_VEHICLE_HEIGHT_M   = 4.3;

  // ── KPI thresholds ────────────────────────────────────────────────────────
  KPI_OTP_WARNING        = 85.0;    // On-time percentage warning
  KPI_OTP_CRITICAL       = 75.0;    // On-time percentage critical
  KPI_FUEL_WARNING       = 15.0;    // L/100km warning
  KPI_FUEL_CRITICAL      = 20.0;    // L/100km critical
  KPI_UTIL_WARNING       = 60.0;    // Utilisation % warning
  KPI_UTIL_CRITICAL      = 40.0;    // Utilisation % critical
  KPI_CANCEL_WARNING     = 5.0;     // Cancellation rate % warning
  KPI_CANCEL_CRITICAL    = 10.0;    // Cancellation rate % critical

resourcestring
  rsAppTitle              = 'FleetOps Fleet Management';
  rsAppCopyright          = 'Copyright 2025 FleetOps Pty Ltd';
  rsLoginTitle            = 'FleetOps Login';
  rsWelcome               = 'Welcome to FleetOps';
  rsLogout                = 'Logged out successfully';
  rsAccessDenied          = 'Access denied. Insufficient privileges.';
  rsSessionExpired        = 'Your session has expired. Please log in again.';
  rsPasswordExpired       = 'Your password has expired. Please change it.';
  rsAccountLocked         = 'Account locked due to too many failed login attempts.';
  rsInvalidCredentials    = 'Invalid username or password.';
  rsConnectionFailed      = 'Could not connect to the database. Please try again.';
  rsDataSaved             = 'Record saved successfully.';
  rsDataDeleted           = 'Record deleted successfully.';
  rsConfirmDelete         = 'Are you sure you want to delete this record?';
  rsValidationFailed      = 'Validation failed. Please correct the errors and try again.';
  rsRequiredField         = 'This field is required.';
  rsInvalidDate           = 'Invalid date format.';
  rsInvalidNumber         = 'Invalid number format.';
  rsValueTooSmall         = 'Value is below the minimum allowed.';
  rsValueTooLarge         = 'Value exceeds the maximum allowed.';
  rsJobDispatched         = 'Job dispatched successfully.';
  rsJobCompleted          = 'Job marked as completed.';
  rsJobCancelled          = 'Job has been cancelled.';
  rsDriverAssigned        = 'Driver assigned to job.';
  rsVehicleAssigned       = 'Vehicle assigned to job.';
  rsNoDriverAvailable     = 'No drivers are currently available.';
  rsNoVehicleAvailable    = 'No vehicles are currently available.';
  rsReportGenerating      = 'Generating report, please wait...';
  rsReportComplete        = 'Report generated successfully.';
  rsReportFailed          = 'Report generation failed.';
  rsExportComplete        = 'Export completed. File saved to: %s';
  rsEmailSent             = 'Report emailed to: %s';
  rsLicenceExpiring       = 'Driver licence expires in %d days: %s';
  rsLicenceExpired        = 'Driver licence has expired: %s';
  rsInsuranceExpiring     = 'Vehicle insurance expires in %d days: %s';
  rsInsuranceExpired      = 'Vehicle insurance has expired: %s';
  rsInspectionDue         = 'Vehicle inspection is due: %s';
  rsServiceDue            = 'Vehicle service is due: %s';
  rsServiceOverdue        = 'Vehicle service is overdue by %d days: %s';
  rsGpsSignalLost         = 'GPS signal lost for vehicle: %s';
  rsGpsSignalRestored     = 'GPS signal restored for vehicle: %s';
  rsSpeedingAlert         = 'Speeding alert: %s travelling at %d km/h in %d km/h zone';
  rsGeofenceBreached      = 'Geofence breach: %s entered restricted zone: %s';
  rsIdleTimeAlert         = 'Idle time alert: %s has been idle for %d minutes';
  rsDeviceOffline         = 'Device offline: %s has not reported for %d minutes';
  rsFuelAnomaly           = 'Fuel anomaly detected for vehicle: %s';
  rsInvoiceOverdue        = 'Invoice %s is overdue by %d days';
  rsContractExpiring      = 'Contract %s expires in %d days';
  rsKpiThresholdWarning   = 'KPI %s is below warning threshold: %.1f (target: %.1f)';
  rsKpiThresholdCritical  = 'KPI %s is below critical threshold: %.1f (target: %.1f)';
  rsBackupComplete        = 'Database backup completed successfully.';
  rsBackupFailed          = 'Database backup failed: %s';
  rsSyncComplete          = 'Data synchronisation completed. %d records updated.';
  rsSyncFailed            = 'Data synchronisation failed: %s';
  rsImportComplete        = 'Import completed. %d records imported, %d errors.';
  rsImportFailed          = 'Import failed: %s';
  rsFeatureNotLicensed    = 'This feature requires an upgrade to your licence.';
  rsMaintenanceMode       = 'The system is currently in maintenance mode.';
  rsNewVersionAvailable   = 'A new version of FleetOps is available: v%s';
  rsUpdateRequired        = 'A mandatory update is required. Please update before continuing.';
  rsHelpNotAvailable      = 'Help is not available for this topic.';
  rsDepotNotFound         = 'Depot not found: %s';
  rsDriverNotFound        = 'Driver not found: ID %d';
  rsVehicleNotFound       = 'Vehicle not found: ID %d';
  rsJobNotFound           = 'Job not found: ID %d';
  rsRouteNotFound         = 'Route not found: ID %d';
  rsGeofenceNotFound      = 'Geofence not found: ID %d';
  rsDuplicateRecord       = 'A duplicate record already exists.';
  rsRecordInUse           = 'This record is in use and cannot be deleted.';
  rsNoPermissionVehicle   = 'You do not have permission to access this vehicle.';
  rsNoPermissionDepot     = 'You do not have permission to access this depot.';
  rsNoPermissionReport    = 'You do not have permission to run this report.';
  rsGpsDeviceAdded        = 'GPS device registered: %s';
  rsGpsDeviceRemoved      = 'GPS device removed: %s';
  rsGeofenceCreated       = 'Geofence created: %s';
  rsGeofenceDeleted       = 'Geofence deleted: %s';
  rsScheduleCreated       = 'Report schedule created: %s';
  rsScheduleDeleted       = 'Report schedule deleted: %s';
  rsScheduleTriggered     = 'Scheduled report triggered: %s';
  rsAlertAcknowledged     = 'Alert acknowledged by %s at %s';
  rsAlertEscalated        = 'Alert escalated to %s';
  rsPasswordChanged       = 'Password changed successfully.';
  rsProfileUpdated        = 'Profile updated successfully.';
  rsTwoFactorEnabled      = 'Two-factor authentication enabled.';
  rsTwoFactorDisabled     = 'Two-factor authentication disabled.';
  rsApiKeyGenerated       = 'API key generated successfully.';
  rsApiKeyRevoked         = 'API key revoked.';
  rsWebhookRegistered     = 'Webhook registered: %s';
  rsWebhookDeleted        = 'Webhook deleted: %s';
  rsWebhookTestSent       = 'Webhook test payload sent to: %s';
  rsIntegrationConnected  = 'Integration connected: %s';
  rsIntegrationError      = 'Integration error (%s): %s';
  rsOdometerUpdated       = 'Odometer updated for vehicle %s: %d km';
  rsFuelFilled            = 'Fuel fill recorded: %s, %.1f L at $%.2f';
  rsMaintenanceLogged     = 'Maintenance logged for %s: %s';
  rsInspectionPassed      = 'Vehicle inspection passed: %s';
  rsInspectionFailed      = 'Vehicle inspection failed: %s (%d defects)';
  rsRouteCreated          = 'Route created: %s';
  rsRouteUpdated          = 'Route updated: %s';
  rsRouteDeleted          = 'Route deleted: %s';
  rsDriverCheckedIn       = 'Driver checked in: %s at %s';
  rsDriverCheckedOut      = 'Driver checked out: %s at %s';
  rsShiftStarted          = 'Shift started: %s';
  rsShiftEnded            = 'Shift ended: %s (%.1f hours)';
  rsBreakStarted          = 'Break started: %s';
  rsBreakEnded            = 'Break ended: %s (%.0f minutes)';
  rsIncidentReported      = 'Incident reported for %s: %s';
  rsIncidentUpdated       = 'Incident %d updated.';
  rsIncidentClosed        = 'Incident %d closed.';
  rsPayrollApproved       = 'Payroll approved for period: %s to %s';
  rsPayrollExported       = 'Payroll exported: %d records.';
  rsTimesheetSubmitted    = 'Timesheet submitted for %s.';
  rsLeaveApproved         = 'Leave request approved: %s (%d days).';
  rsLeaveRejected         = 'Leave request rejected: %s.';
  rsCustomerCreated       = 'Customer created: %s';
  rsCustomerUpdated       = 'Customer updated: %s';
  rsContractCreated       = 'Contract created: %s for %s';
  rsContractRenewed       = 'Contract renewed: %s (new expiry: %s)';
  rsInvoiceCreated        = 'Invoice created: %s for $%.2f';
  rsInvoiceSent           = 'Invoice sent: %s to %s';
  rsPaymentReceived       = 'Payment received: $%.2f for invoice %s';
  rsCreditNoteIssued      = 'Credit note issued: %s for $%.2f';
  rsDocumentUploaded      = 'Document uploaded: %s';
  rsDocumentDeleted       = 'Document deleted: %s';

implementation

end.
