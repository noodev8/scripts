"""
SEO: Google Search Console API client helper.

Uses the existing merchant-feed-api-462809 service account (already used for
the Merchant Center feed) with Search Console API access granted 2026-07-16.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(__file__)
KEY_PATH = os.path.join(SCRIPT_DIR, "..", "merchant-feed-api-462809-23c712978791.json")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# Update this if the verified property in Search Console differs
SITE_URL = "https://brookfieldcomfort.com/"


def get_service():
    creds = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds)


def list_verified_sites():
    service = get_service()
    return service.sites().list().execute()


if __name__ == "__main__":
    sites = list_verified_sites()
    print("Verified sites this service account can access:")
    for entry in sites.get("siteEntry", []):
        print(f"- {entry['siteUrl']}  (permission: {entry['permissionLevel']})")
