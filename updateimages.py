#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync product images for the newest skusummary rows into the Google Drive
assets/images folder used by the new web app, ahead of full PowerBuilder
replacement.

Reads C:/brookfieldcomfort/brookfield.ini for the "dropbox" path, checks the
last N (default 50) products loaded to skusummary, and downloads any missing
main image from https://images.brookfieldcomfort.com/{imagename} into
{dropbox}\\assets\\images\\.

Run ad-hoc: python sync_images_to_drive.py [--limit 50] [--dry-run]
"""

import os
import sys
import argparse
import requests
import psycopg2

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from dotenv import load_dotenv
from logging_utils import get_db_config, get_uk_time

load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, ".env"))

LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

SCRIPT_NAME = "sync_images_to_drive"
INI_PATH = r"C:\brookfieldcomfort\brookfield.ini"
IMAGE_BASE_URL = "https://images.brookfieldcomfort.com/"


def log(message):
    uk_time = get_uk_time()
    tz_name = uk_time.strftime('%Z')
    timestamp = uk_time.strftime(f'%Y-%m-%d %H:%M:%S {tz_name}')
    line = f"{timestamp}  {message}"
    print(line)
    with open(os.path.join(LOGS_DIR, f"{SCRIPT_NAME}.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_dropbox_path():
    """Parse the 'dropbox=' line out of brookfield.ini (plain key=value, no section headers)."""
    if not os.path.exists(INI_PATH):
        raise FileNotFoundError(f"Could not find {INI_PATH}")

    with open(INI_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("dropbox="):
                return line.split("=", 1)[1].strip()

    raise ValueError(f"No 'dropbox=' line found in {INI_PATH}")


def get_recent_images(limit):
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT groupid, imagename, created
        FROM skusummary
        WHERE imagename IS NOT NULL AND imagename != ''
        ORDER BY created DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def sync_images(limit=50, dry_run=False):
    dropbox_path = get_dropbox_path()
    images_dir = os.path.join(dropbox_path, "assets", "images")

    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Images folder not found: {images_dir}")

    rows = get_recent_images(limit)
    log(f"=== IMAGE SYNC STARTED (checking last {limit} new products) ===")
    log(f"Target folder: {images_dir}")

    checked = 0
    already_present = 0
    downloaded = 0
    failed = 0

    for groupid, imagename, created in rows:
        checked += 1
        local_path = os.path.join(images_dir, imagename)

        if os.path.exists(local_path):
            already_present += 1
            continue

        if dry_run:
            log(f"[DRY RUN] Would download {imagename} (groupid={groupid}, created={created})")
            downloaded += 1
            continue

        url = IMAGE_BASE_URL + imagename
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(resp.content)
            downloaded += 1
            log(f"Downloaded {imagename} (groupid={groupid})")
        except Exception as e:
            failed += 1
            log(f"FAILED {imagename} (groupid={groupid}): {e}")

    log(f"Checked: {checked}, already present: {already_present}, downloaded: {downloaded}, failed: {failed}")
    log("=== IMAGE SYNC COMPLETED ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync missing product images to Google Drive assets folder")
    parser.add_argument("--limit", type=int, default=50, help="Number of most recently created skusummary rows to check (default 50)")
    parser.add_argument("--dry-run", action="store_true", help="List what would be downloaded without downloading")
    args = parser.parse_args()

    sync_images(limit=args.limit, dry_run=args.dry_run)
