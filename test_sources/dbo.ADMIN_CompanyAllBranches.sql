
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
CREATE PROCEDURE dbo.ADMIN_CompanyAllBranches(
  @company_id INT )
AS
BEGIN
-- zwraca siedziba w pierwszym rekordzie i wszystkie oddziały firmy
SELECT c.ID
AS ID,
       vc.*,
       c.INumberBranch
FROM dbo.ADMIN_viewCompany
AS vc WITH ( nolock )
INNER JOIN
dbo.ADMIN_Company
AS c WITH ( nolock )
ON vc.Company_ID=c.ID
WHERE c.ID=@company_id
      AND vc.CompanyHierarchy_ID=1
      AND c.Deleted=0
      AND c.CompanyMaster_ID IS NULL
UNION
SELECT c.ID
AS ID,
       vc.*,
       c.INumberBranch
FROM dbo.ADMIN_viewCompany
AS vc WITH ( nolock )
INNER JOIN
dbo.ADMIN_Company
AS c WITH ( nolock )
ON vc.Company_ID=c.ID
WHERE vc.Parent_ID=@company_id
      AND vc.CompanyHierarchy_ID=2
      AND c.Deleted=0
      AND c.CompanyMaster_ID IS NULL;
END;
GO
