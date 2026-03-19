-- ============================================================
-- Procedure: dbo.ADMIN_AllBranches
-- Description: Returns all branches, optionally filtered by active status.
--              Used by branch selection dropdowns across the application.
-- ============================================================

IF OBJECT_ID(N'dbo.ADMIN_AllBranches', N'P') IS NOT NULL
    DROP PROCEDURE dbo.ADMIN_AllBranches
GO

CREATE PROCEDURE dbo.ADMIN_AllBranches
    @IncludeInactive BIT = 0
AS
BEGIN
    SET NOCOUNT ON

    SELECT
        b.BranchID,
        b.BranchCode,
        b.BranchName,
        b.Address,
        b.City,
        b.PostalCode,
        b.Phone,
        b.Email,
        b.ManagerName,
        b.IsActive,
        b.SortOrder,
        -- Aggregate stats
        COUNT(DISTINCT v.VehicleID)     AS VehicleCount,
        COUNT(DISTINCT d.DriverID)      AS DriverCount
    FROM
        dbo.Fleet_Branches b
        LEFT JOIN dbo.Fleet_Vehicles v
            ON v.BranchID = b.BranchID AND v.IsActive = 1
        LEFT JOIN dbo.HR_Drivers d
            ON d.BranchID = b.BranchID AND d.IsActive = 1
    WHERE
        (@IncludeInactive = 1 OR b.IsActive = 1)
    GROUP BY
        b.BranchID, b.BranchCode, b.BranchName, b.Address,
        b.City, b.PostalCode, b.Phone, b.Email,
        b.ManagerName, b.IsActive, b.SortOrder
    ORDER BY
        b.SortOrder, b.BranchName

    SET NOCOUNT OFF
END
GO
