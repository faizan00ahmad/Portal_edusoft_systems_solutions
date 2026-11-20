# Edusoft demo portal - extracted links

Source: http://demo1.edusoftsolutions.com/ (extracted 2026-11-17). HTTPS on this host fails with a certificate-name error; HTTP works.

## Web software

| # | Software | Category | Username | Password | URL | Status |
|---|---|---|---|---|---|---|
| 1 | EduBSSTD WEB Conversion (NEW) | Education | `admin` | `edu` | https://bsstdweb.mohdsajidhameed.com/ | 200 |
| 2 | EduCampusCore-ERP (NEW) | Education | `admin` | `edu123456789` | https://edusuit.mohdsajidhameed.com/ | 200 |
| 3 | EduCampus Finace And Accounts (NEW) | Education | `school` | `school` | https://poultry.mohdsajidhameed.com/ | 200 |
| 4 | Hospital Managment Information System (HMIS) | Hospital | `admin` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 5 | Poultry Business Soultions (ERP) | Business | `admin` | `edu` | https://poultry.mohdsajidhameed.com/ | 200 |
| 6 | Sanitary Management Software (ERP) | Business | `admin` | `8520` | https://sanitary.mohdsajidhameed.com/ | 200 |
| 7 | Electric Store Management Software (ERP) | Retail | `admin` | `8520` | https://electronics.mohdsajidhameed.com/ | 200 |
| 8 | Medical Lab & Diagnostic Center Management Software (ERP) | Hospital | `lab` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 9 | Hospital Patient Registration & Token Management System (ERP) | Hospital | `token` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 10 | Outpatient Department (OPD) Management System (ERP) | Hospital | `opd` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 11 | Smart Financial Accounts Management System (ERP) | Business | `accounts` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 12 | Employee & Payroll Management System (ERP) | Business | `hr` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 13 | Business Solutions Enterprise (ERP) | Business | `admin` | `8520` | https://edubsent.mohdsajidhameed.com/ | 200 |
| 14 | Pharmacy Management System (ERP) | Hospital | `pharmacy` | `edu` | https://hmis.mohdsajidhameed.com | 200 |
| 15 | Digital Invoicing Solution | Business | `admin` | `edu` | https://edudigitalinv.mohdsajidhameed.com/ | 200 |

## Android apps

| # | App | Username | Password | APK link | Status |
|---|---|---|---|---|---|
| 16 | Restaurant Manager App | `AHMAD` | `abc123` | http://demo1.edusoftsolutions.com/apk/Edu_Restarant1.37.apk | **404** |
| 17 | Bussiness Solution App | `admin` | `edu` | http://demo1.edusoftsolutions.com/apk/BusinessSolutionEmpire_1.17.apk | **404** |
| 18 | Electric Store App | `admin` | `edu` | http://demo1.edusoftsolutions.com/apk/major_electric_v4.0.18.apk | **404** |

## Issues found

- **All 3 APKs return 404** on demo1.edusoftsolutions.com (also not found on mohdsajidhameed.com). They need to be re-uploaded to `/apk/` before the download buttons work.
- **EduCampus Finace And Accounts** points to `poultry.mohdsajidhameed.com`, the same URL as Poultry ERP. Probably a copy-paste error.
- The 3 NEW items share a missing poster (`mohdimages/invoicing4.jpeg` returns 404) and have no description.
- 8 modules share `hmis.mohdsajidhameed.com` (HMIS, Lab, Token, OPD, Financial Accounts, Payroll, Pharmacy) and differ only by login.
- Typos in live names: Finace, Managment, Soultions, Bussiness.

## Contact

- Website: www.edusoftsolutions.com
- WhatsApp: +92 300 8489698
- Email: info@edusoftsolutions.com
