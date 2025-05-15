import os
import csv
import datetime
import requests
import msal

# List of tenants with secure placeholders (replace with secure vault retrieval in production)
tenants = [
    {
        "name": "Test B2C",
        "tenant_id": "Enter Tenant ID",
        "client_id": "Enter Client ID",
        "client_secret": "YOUR_SECRET_HERE"
    },
   
    # Add more tenants as needed...
]

# Settings
days_until_expiration = 90
today = datetime.datetime.now(datetime.timezone.utc)
output_dir = "C:\\Scripts"
os.makedirs(output_dir, exist_ok=True)

all_csv = os.path.join(output_dir, "AppCredsAll.csv")
expiring_csv = os.path.join(output_dir, "AppCredsExpiringSoon.csv")

all_credentials = []
expiring_credentials = []

def get_token(tenant_id, client_id, client_secret):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token.get("access_token")

def fetch_applications(token):
    url = "https://graph.microsoft.com/v1.0/applications?$top=999"
    headers = {"Authorization": f"Bearer {token}"}
    apps = []

    while url:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        apps.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

    return apps

def process_credentials(app, tenant_name, cred_type, creds):
    results = []
    for cred in creds:
        end_date = datetime.datetime.fromisoformat(cred["endDateTime"])
        days_remaining = (end_date - today).days
        status = "Expired" if days_remaining < 0 else "Valid"
        results.append({
            "TenantName": tenant_name,
            "AppDisplayName": app["displayName"],
            "AppId": app["appId"],
            "ObjectId": app["id"],
            "CredentialType": cred_type,
            "EndDate": cred["endDateTime"],
            "DaysRemaining": days_remaining,
            "Status": status
        })
    return results

for tenant in tenants:
    print(f"\n➡ Connecting to: {tenant['name']}")
    try:
        token = get_token(tenant["tenant_id"], tenant["client_id"], tenant["client_secret"])
        if not token:
            raise Exception("Token retrieval failed.")

        apps = fetch_applications(token)

        for app in apps:
            certs = process_credentials(app, tenant["name"], "Certificate", app.get("keyCredentials", []))
            secrets = process_credentials(app, tenant["name"], "ClientSecret", app.get("passwordCredentials", []))
            all_credentials.extend(certs + secrets)
            expiring_credentials.extend([c for c in certs + secrets if c["DaysRemaining"] <= days_until_expiration])

    except Exception as ex:
        print(f"❌ Failed to connect to {tenant['name']}: {ex}")

def export_csv(file_path, data, sort_keys):
    if data:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for row in sorted(data, key=lambda x: tuple(x[k] for k in sort_keys)):
                writer.writerow(row)

export_csv(all_csv, all_credentials, ["TenantName", "AppDisplayName", "CredentialType", "EndDate"])
export_csv(expiring_csv, expiring_credentials, ["TenantName", "DaysRemaining"])

print(f"\n📁 All credentials exported to:        {all_csv}")
print(f"⚠️  Expiring within {days_until_expiration} days: {expiring_csv}")
