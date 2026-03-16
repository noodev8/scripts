#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Google Merchant Center feed for Brookfield Comfort.
Pulls live product data from PostgreSQL and outputs a TSV file.
"""

import os
import sys
import psycopg2
import pandas as pd
import paramiko
from datetime import datetime

# Add parent directory to path so we can import shared logging_utils
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))
from dotenv import load_dotenv
from logging_utils import get_db_config, get_uk_time

# Load .env from scripts root
load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, "..", ".env"))

# Local logs/output directories within merchant-feed/
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
ARCHIVE_DIR = os.path.join(SCRIPT_DIR, "archive_logs")
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

SCRIPT_NAME = "merchant_feed"


def log(message):
    """Log to local merchant-feed/logs/ directory"""
    uk_time = get_uk_time()
    tz_name = uk_time.strftime('%Z')
    timestamp = uk_time.strftime(f'%Y-%m-%d %H:%M:%S {tz_name}')
    log_entry = f"{timestamp}  {message}\n"

    with open(os.path.join(LOGS_DIR, f"{SCRIPT_NAME}.log"), "a", encoding="utf-8") as f:
        f.write(log_entry)


def save_local_report(filename, content):
    """Save report file to local merchant-feed/logs/ directory"""
    file_path = os.path.join(LOGS_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


def determine_gender_and_age(gender):
    """
    Determine Google gender and age_group based on attributes.gender
    Returns tuple: (google_gender, age_group)
    """
    if not gender:
        return "", "adult"

    gender_upper = gender.strip().upper()

    if gender_upper == "WOMENS":
        return "female", "adult"
    elif gender_upper == "GIRLS":
        return "female", "kids"
    elif gender_upper == "MENS":
        return "male", "adult"
    elif gender_upper == "BOYS":
        return "male", "kids"
    else:
        # Default for unisex or unknown
        return "unisex", "adult"


def determine_product_type(gender, titledetail):
    if not gender:
        return ""
    gender_upper = gender.strip().upper()
    title_upper = titledetail.strip().upper() if titledetail else ""

    if gender_upper == "UNISEX":
        return "Home > Womens > Footwear"
    if gender_upper == "WOMENS":
        if "SANDAL" in title_upper:
            return "Home > Womens > Footwear > Womens Sandals"
        if "SLIPPER" in title_upper:
            return "Home > Womens > Footwear > Womens Slippers"
        if "TRAINER" in title_upper:
            return "Home > Womens > Footwear > Womens Trainers"
        return "Home > Womens > Footwear"
    if gender_upper == "MENS":
        if "WIDE" in title_upper:
            return "Home > Womens > Footwear > Mens Wide Fit"
        return "Home > Mens > Footwear"
    return ""



def determine_stock_availability(localstock_qty, localstock_deleted, amzlive, ukdstock, code=None):
    """
    Determine stock availability based on priority:
    1. localstock (qty > 0 and deleted = 0)
    2. amzfeed (amzlive > 0)
    3. ukdstock (stock > 0)
    Returns True if in stock, False if out of stock
    """
    # Priority 1: Check localstock
    if localstock_qty and localstock_deleted == 0 and localstock_qty > 0:
        return True

    # Priority 2: Check amzfeed
    if amzlive and amzlive > 0:
        return True

    # Priority 3: Check ukdstock
    if ukdstock and ukdstock > 0:
        return True

    return False


def generate_feed():
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            sm.groupid, sm.shopifyprice, sm.imagename, sm.brand, sm.colour,
            sm.material, sm.cost, sm.rrp, sm.handle, sm.googlecampaign,
            a.gender, t.shopifytitle AS title,
            m.code, m.variantlink, m.uksize, m.ean, m.googleid,
            COALESCE(SUM(CASE WHEN ls.deleted = 0 THEN ls.qty ELSE 0 END), 0) as localstock_qty,
            CASE WHEN COUNT(CASE WHEN ls.deleted = 0 THEN 1 END) > 0 THEN 0 ELSE 1 END as localstock_deleted,
            af.amzlive, uk.stock as ukdstock
        FROM skusummary sm
        JOIN skumap m ON sm.groupid = m.groupid
        LEFT JOIN attributes a ON a.groupid = sm.groupid
        LEFT JOIN title t ON t.groupid = sm.groupid
        LEFT JOIN localstock ls ON ls.code = m.code
        LEFT JOIN amzfeed af ON af.code = m.code
        LEFT JOIN ukdstock uk ON uk.code = m.code
        WHERE sm.googlestatus = 1 AND sm.shopify = 1 AND m.googlestatus = 1
        GROUP BY sm.groupid, sm.shopifyprice, sm.imagename, sm.brand, sm.colour,
                 sm.material, sm.cost, sm.rrp, sm.handle, sm.googlecampaign,
                 a.gender, t.shopifytitle, m.code, m.variantlink, m.uksize, m.ean, m.googleid,
                 af.amzlive, uk.stock
    """)

    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=colnames)

    feed_rows = []

    for _, row in df.iterrows():
        try:
            variant_id = str(row["variantlink"]).rstrip("V")
            handle = row["handle"]
            image_name = row["imagename"]
            title = row["title"]
            gender = row["gender"]
            product_type = determine_product_type(gender, title)

            # 1. GTIN from skumap.ean, remove "B" at end, validate length
            raw_gtin = str(row["ean"]) if row["ean"] else ""
            gtin = raw_gtin.rstrip("B")
            # Only process rows with valid GTIN (12 or 13 characters)
            if not (gtin and len(gtin) in [12, 13] and gtin.isdigit()):
                continue  # Skip this row entirely

            # 2. Gender and age_group logic
            google_gender, age_group = determine_gender_and_age(gender)

            # 3. Material from skusummary.material (already in query)
            material = row["material"] if pd.notnull(row["material"]) else ""

            # 4. Size from skumap.uksize, strip " UK"
            uksize = str(row["uksize"]) if row["uksize"] else ""
            size = uksize.replace(" UK", "") if uksize else ""

            # 5. Price should be rrp from skusummary, sale_price should be shopifyprice
            price = f"{float(row['rrp']):.2f} GBP" if pd.notnull(row["rrp"]) else ""
            sale_price = f"{float(row['shopifyprice']):.2f} GBP" if pd.notnull(row["shopifyprice"]) else ""

            # 6. Check stock availability across multiple tables in priority order
            is_in_stock = determine_stock_availability(
                row["localstock_qty"],
                row["localstock_deleted"],
                row["amzlive"],
                row["ukdstock"]
            )
            availability = "in stock" if is_in_stock else "out of stock"

            feed_rows.append({
                "id": row["googleid"],
                "title": title,
                "description": title,
                "link": f"https://brookfieldcomfort.com/products/{handle}?variant={variant_id}",
                "image_link": f"https://images.brookfieldcomfort.com/{image_name}",
                "availability": availability,
                "cost_of_goods_sold": f"{float(row['cost']):.2f} GBP" if pd.notnull(row["cost"]) else "",
                "price": price,
                "sale_price": sale_price,
                "google_product_category": 187,
                "product_type": product_type,
                "brand": row["brand"],
                "gtin": gtin,
                "condition": "new",
                "age_group": age_group,
                "colour": row["colour"],
                "gender": google_gender,
                "material": material,
                "size": size,
                "size_system": "UK",
                "item_group_id": row["groupid"],
                "custom_label_0": row["googlecampaign"],
                "custom_label_1": row["groupid"]
            })
        except Exception:
            continue  # Skip malformed rows silently in final version

    feed_df = pd.DataFrame(feed_rows)

    # Save the feed to local logs directory
    feed_content = feed_df.to_csv(index=False, sep="\t")
    output_file = save_local_report("GOOGLE-DATA-Merchant.txt", feed_content)

    # Also save a copy in the merchant-feed root for easy access
    with open(os.path.join(SCRIPT_DIR, "GOOGLE-DATA-Merchant.txt"), "w", encoding="utf-8") as f:
        f.write(feed_content)

    cur.close()
    conn.close()

    log(f"=== MERCHANT FEED GENERATION STARTED ===")
    log(f"Feed file generated: {output_file}")
    log(f"Total products in feed: {len(feed_df)}")
    log(f"=== MERCHANT FEED GENERATION COMPLETED ===")
    print(f"Feed file generated: {output_file}")


def upload_file_to_google():
    """Upload the generated feed file to Google Merchant Center via SFTP"""
    sftp_host = os.getenv('MERCHANT_SFTP_HOST')
    sftp_port = int(os.getenv('MERCHANT_SFTP_PORT', 19321))
    sftp_username = os.getenv('MERCHANT_SFTP_USERNAME')
    sftp_password = os.getenv('MERCHANT_SFTP_PASSWORD')

    if not all([sftp_host, sftp_username, sftp_password]):
        print("SFTP credentials missing from .env file")
        return

    local_file = os.path.join(LOGS_DIR, "GOOGLE-DATA-Merchant.txt")
    remote_file = "GOOGLE-DATA-Merchant.txt"

    try:
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.put(local_file, remote_file)
        log("Upload to Google Merchant SFTP successful")
        print("Upload to Google Merchant SFTP successful.")
    except Exception as e:
        log(f"SFTP upload failed: {str(e)}")
        print("SFTP upload failed:", str(e))
    finally:
        if 'sftp' in locals(): sftp.close()
        if 'transport' in locals(): transport.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Google Merchant Center feed")
    parser.add_argument("--upload", action="store_true", help="Upload feed to Google via SFTP after generation")
    args = parser.parse_args()

    generate_feed()

    if args.upload:
        upload_file_to_google()
    else:
        print("Feed generated. Run with --upload to send to Google SFTP.")
