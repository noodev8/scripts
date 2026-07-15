#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONE-TIME setup for updateimages.py's Google Drive upload.

updateimages.py uploads product images straight into brookfielduser1@gmail.com's
Google Drive so the nightly job can run headless on the VPS (no Drive-for-Desktop
synced folder required). It authenticates AS brookfielduser1 — not the
merchant-feed service account, not noodev8 — so the files are owned by
brookfielduser1.

It uses the NARROW "drive.file" scope on purpose: that scope needs no Google
verification and the login never expires, unlike full-Drive access (which
Google blocks for unverified apps and, in test mode, expires after 7 days).
The trade-off is that the app can only touch folders IT created — so this script
also creates a dedicated "images" folder and pins its id in .env.

This script does two things:
  1. Mints/refreshes drive_token.json (opens a browser for consent).
  2. Creates the app-owned images folder and writes DRIVE_IMAGES_FOLDER_ID to .env
     (only if it isn't already set and reachable).

Prerequisites (done once in the Google Cloud console, project
merchant-feed-api-462809):
  - Credentials -> Create OAuth client ID -> "Desktop app" -> download JSON,
    saved here as  drive_oauth_client.json.  (DONE)
  - Google Auth Platform -> Audience -> Publishing status: PUBLISH to Production.

Run it ON A MACHINE WITH A BROWSER (your desktop):

    python authorize_drive.py

A browser opens -> LOG IN AS brookfielduser1@gmail.com -> Allow. Because
drive.file is non-sensitive, there should be NO "unverified app" warning.

Afterwards it prints the new folder's id and where it is in Drive. Follow the
on-screen note to slot that folder into BrookfieldComfort/Working/assets/ so
PowerBuilder keeps reading it. Then copy drive_oauth_client.json, drive_token.json
and the updated .env to the VPS. All three are gitignored.
"""

import os
import re
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_FILE = os.path.join(SCRIPT_DIR, "drive_oauth_client.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "drive_token.json")
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_NAME = "images"


def get_creds():
    if not os.path.exists(CLIENT_FILE):
        print(f"ERROR: {CLIENT_FILE} not found.")
        print("Download the Desktop OAuth client JSON from the Cloud console and "
              "save it there. See the header of this file for steps.")
        sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        print("Existing token expired; refreshing...")
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print(f"Wrote {TOKEN_FILE}")
    return creds


def report_identity(service):
    """Print which Google account this token belongs to, as a sanity check."""
    try:
        about = service.about().get(fields="user(emailAddress,displayName)").execute()
        user = about.get("user", {})
        print(f"Authenticated as: {user.get('emailAddress')} ({user.get('displayName')})")
        if user.get("emailAddress", "").lower() != "brookfielduser1@gmail.com":
            print("  WARNING: expected brookfielduser1@gmail.com — re-run and pick "
                  "the right account.")
    except Exception as e:
        print(f"(could not verify identity: {e})")


def existing_folder_id():
    """Return DRIVE_IMAGES_FOLDER_ID from .env if present, else None."""
    load_dotenv(dotenv_path=ENV_FILE)
    return os.getenv("DRIVE_IMAGES_FOLDER_ID")


def folder_reachable(service, folder_id):
    try:
        meta = service.files().get(fileId=folder_id, fields="id, trashed").execute()
        return not meta.get("trashed")
    except Exception:
        return False


def create_images_folder(service):
    meta = service.files().create(
        body={"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
        fields="id, name").execute()
    return meta["id"]


def write_env_folder_id(folder_id):
    """Set/replace DRIVE_IMAGES_FOLDER_ID=... in .env, leaving the rest untouched."""
    line = f"DRIVE_IMAGES_FOLDER_ID={folder_id}\n"
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    if re.search(r"(?m)^DRIVE_IMAGES_FOLDER_ID=", content):
        content = re.sub(r"(?m)^DRIVE_IMAGES_FOLDER_ID=.*$", line.rstrip("\n"), content)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += line

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Set DRIVE_IMAGES_FOLDER_ID in {ENV_FILE}")


def main():
    creds = get_creds()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    report_identity(service)

    folder_id = existing_folder_id()
    if folder_id and folder_reachable(service, folder_id):
        print(f"\nImages folder already configured and reachable: id={folder_id}")
        print("Nothing else to do. Copy drive_oauth_client.json, drive_token.json "
              "and .env to the VPS.")
        return

    folder_id = create_images_folder(service)
    write_env_folder_id(folder_id)

    print("\n" + "=" * 68)
    print("Created an app-owned Drive folder named 'images'.")
    print(f"  Folder id : {folder_id}")
    print("  Location  : top level of brookfielduser1's My Drive (for now)")
    print("=" * 68)
    print(
        "\nONE manual step in the Drive web UI (as brookfielduser1), so\n"
        "PowerBuilder keeps finding the images at the old path:\n"
        "  1. Open Google Drive in a browser, logged in as brookfielduser1.\n"
        "  2. Move ALL existing image files from\n"
        "       My Drive/BrookfieldComfort/Working/assets/images\n"
        "     into the new 'images' folder now sitting at the top of My Drive.\n"
        "  3. Delete (or rename) the now-empty old 'images' folder, then move the\n"
        "     new 'images' folder into  My Drive/BrookfieldComfort/Working/assets/ .\n"
        "  (The app keeps access to this folder wherever you move it, because it\n"
        "   created it.)\n"
        "\nThen: python updateimages.py --dry-run   to verify.\n"
        "Finally copy drive_oauth_client.json, drive_token.json and .env to the VPS."
    )


if __name__ == "__main__":
    main()
