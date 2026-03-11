
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO
--select * from ADMIN_Company where CompanyCode='P0211011'
CREATE procedure [import].[LPC_LicenceFeeStartData2Insert]
@CompanyID int
as
begin
--declare @CompanyID int
--set @CompanyID = 274

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(31,  1,'opłata za wykonywanie transportu drogowego taksówką',180,13,NULL,7,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat, obszar gminy',3,31,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),20000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(32,  1,'opłata za wykonywanie transportu drogowego taksówką',360,13,NULL,7,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat, obszar gminy',3,32,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),25000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(33,  1,'opłata za wykonywanie transportu drogowego taksówką',600,13,NULL,7,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat, obszar gminy',3,33,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),30000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(34,  1,'opłata za wykonywanie transportu drogowego taksówką',180,13,NULL,8,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat, obszar gmin sąsiadujących',3,34,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),28000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(35,  1,'opłata za wykonywanie transportu drogowego taksówką',360,13,NULL,8,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat, obszar gmin sąsiadujących',3,35,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),35000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(36,  1,'opłata za wykonywanie transportu drogowego taksówką',600,13,NULL,8,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat, obszar gmin sąsiadujących',3,36,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),40000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(37,  1,'opłata za wykonywanie transportu drogowego taksówką',180,13,NULL,9,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat, obszar miasta stołecznego Warszawy',3,37,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),32000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(38,  1,'opłata za wykonywanie transportu drogowego taksówką',360,13,NULL,9,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat, obszar miasta stołecznego Warszawy',3,38,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),38000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(39,  1,'opłata za wykonywanie transportu drogowego taksówką',600,13,NULL,9,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat, obszar miasta stołecznego Warszawy',3,39,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),45000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(40,  1,'opłata za licencję na samochód od 7 do 9 osób',180,17,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat',3,40,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),70000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(41,  1,'opłata za licencję na samochód od 7 do 9 osób',360,17,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat',3,41,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),80000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(42,  1,'opłata za licencję na samochód od 7 do 9 osób',600,17,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat',3,42,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),90000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(43,  1,'opłata za licencję na pośrednictwo przy przewozie rzeczy',180,16,7,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat',3,43,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),80000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(44,  1,'opłata za licencję na pośrednictwo przy przewozie rzeczy',360,16,7,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat',3,44,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),90000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(45,  1,'opłata za licencję na pośrednictwo przy przewozie rzeczy',600,16,7,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat',3,45,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),100000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(46,  1,'opłata za zezwolenie na wykonywanie zawodu przewoźnika drogowego',180,14,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('bezterminowo',3,46,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),100000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(47,  1,'opłata za zezwolenie na wykonywanie zawodu przewoźnika drogowego',180,15,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('bezterminowo',3,47,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),100000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(48,  1,'opłata za licencję na samochód osobowy',180,18,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('od 2 do 15 lat',3,48,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),70000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(49,  1,'opłata za licencję na samochód osobowy',360,18,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 15 do 30 lat',3,49,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),80000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')

set identity_insert [dbo].[LPC_LicenceFeeType] on
INSERT INTO [dbo].[LPC_LicenceFeeType]
	([ID],[ApplicationType_ID],[Description],[Month],[LicenceGroup_ID],[LicenceCategory_ID],[LicenceArea_ID],[LegalBasis_ID],[CREATED],[MODIFIED])
VALUES --1-nowa licencja
	(50,  1,'opłata za licencję na samochód osobowy',600,18,NULL,NULL,4,'2000-01-01','2000-01-01')
set identity_insert [dbo].[LPC_LicenceFeeType] off
INSERT INTO [dbo].[ADMIN_FeeType]
	([Name],[FeeType],[Reference_ID],[READONLY],[CREATED],[MODIFIED])
VALUES-- FeeType: 2-LPC_PermissionFeeType, 3-LPC_LicenceFeeType, 4-LPC_CertificateFeeType, 5-LPC_CompanyControlPenaltyFeeType, 6-LPC_PermissionConfirmFeeType, 7-LPC_CertificatePTFeeType
	('powyżej 30 do 50 lat',3,50,  1,'2000-01-01','2000-01-01')
INSERT INTO [dbo].[ADMIN_FeeTypeValidity]
	([FeeType_ID],[FeeAmount],[VatRate_ID],[Company_ID],[ValidFrom],[ValidTo],[Currency_ID],[CREATED],[MODIFIED])
VALUES
	(SCOPE_IDENTITY(),90000,  NULL,@CompanyID,'2013-08-01',NULL,1,'2000-01-01','2000-01-01')
end
GO
