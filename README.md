# azure-app-cred-monitor
# 🔐 Azure App Credential Expiration Checker (Multi-Tenant)

This Python script audits Azure Active Directory (AAD) **Application Registrations** across **multiple tenants**, identifying and exporting **expiring Client Secrets and Certificates**.

## 🚀 Features

- ✅ Authenticates using **Microsoft Graph API + client credentials**
- 🔍 Checks **Certificates** and **Client Secrets** for all registered apps
- 📆 Flags credentials expiring within **90 days**
- 📁 Outputs:
  - `AppCredsAll.csv` – Full list of credentials
  - `AppCredsExpiringSoon.csv` – Credentials expiring within 90 days
- 📤 Easily extendable for **email alerts, dashboards, or automation**

---

## 🛠️ Prerequisites

- Python 3.10+
- Register an **App Registration** per tenant with:
  - `Application.Read.All`
  - `Directory.Read.All`
- Install required modules:

```bash
pip install msal requests
