#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Google Merchant Center feed for Brookfield Comfort.
Pulls live product data from PostgreSQL and outputs a TSV file.
"""

import os
import psycopg2
import pandas as pd
import paramiko
from datetime import datetime

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "77.68.13.150",
    "port": 5432,
    "user": "brookfield_prod_user",
    "password": "prodpw",
    "dbname": "brookfield_prod"
}

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = SCRIPT_DIR  # Save feed file in the same directory as the script
LOG_RETENTION_DAYS = 7


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


def cleanup_old_files(folder, days):
    now = datetime.now()
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if os.path.isfile(path) and fname.startswith("merchant_feed_"):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if (now - mtime).days > days:
                os.remove(path)


def determine_stock_availability(localstock_qty, localstock_deleted, amzlive, ukdstock):
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
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            sm.groupid, sm.shopifyprice, sm.imagename, sm.brand, sm.colour,
            sm.material, sm.cost, sm.rrp, sm.handle, sm.googlecampaign,
            a.gender, t.shopifytitle AS title,
            m.code, m.variantlink, m.uksize, m.ean,
            ls.qty as localstock_qty, ls.deleted as localstock_deleted,
            af.amzlive, uk.stock as ukdstock
        FROM skusummary sm
        JOIN skumap m ON sm.groupid = m.groupid
        LEFT JOIN attributes a ON a.groupid = sm.groupid
        LEFT JOIN title t ON t.groupid = sm.groupid
        LEFT JOIN localstock ls ON ls.code = m.code
        LEFT JOIN amzfeed af ON af.code = m.code
        LEFT JOIN ukdstock uk ON uk.code = m.code
        WHERE sm.googlestatus = 1 AND sm.shopify = 1 AND m.googlestatus = 1
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

            # 1. GTIN from skumap.ean, remove "B" at end
            raw_gtin = str(row["ean"]) if row["ean"] else ""
            gtin = raw_gtin.rstrip("B")

            # 2. Gender and age_group logic
            google_gender, age_group = determine_gender_and_age(gender)

            # 3. Material from skusummary.material (already in query)
            material = row["material"] if pd.notnull(row["material"]) else ""

            # 4. Size from skumap.uksize, strip " UK"
            uksize = str(row["uksize"]) if row["uksize"] else ""
            size = uksize.replace(" UK", "") if uksize else ""

            # 5. Price should be rrp from skusummary, sale_price should be shopifyprice
            price = f"{float(row['rrp']):.2f}" if pd.notnull(row["rrp"]) else ""
            sale_price = f"{float(row['shopifyprice']):.2f}" if pd.notnull(row["shopifyprice"]) else ""

            # 6. Check stock availability across multiple tables in priority order
            is_in_stock = determine_stock_availability(
                row["localstock_qty"],
                row["localstock_deleted"],
                row["amzlive"],
                row["ukdstock"]
            )
            availability = "in stock" if is_in_stock else "out of stock"

            feed_rows.append({
                "id": row["code"],
                "title": title,
                "description": title,
                "link": f"https://brookfieldcomfort.com/products/{handle}?variant={variant_id}",
                "image_link": f"https://images.brookfieldcomfort.com/{image_name}",
                "availability": availability,
                "cost_of_goods_sold": f"{float(row['cost']):.2f}" if pd.notnull(row["cost"]) else "",
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
    today_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_file = os.path.join(OUTPUT_FOLDER, f"GOOGLE-DATA-Merchant.txt")
    feed_df.to_csv(output_file, index=False, sep="\t")

    cur.close()
    conn.close()
    cleanup_old_files(OUTPUT_FOLDER, LOG_RETENTION_DAYS)
    print(f"✅ Feed file generated: {output_file}")


if __name__ == "__main__":
    generate_feed()


# --- FTP The File Across ---
SFTP_HOST = 'partnerupload.google.com'
SFTP_PORT = 19321
SFTP_USERNAME = 'mc-sftp-124941872'       # From Merchant Center
SFTP_PASSWORD = 'V[,:Ua1#2p'       # Generate in Merchant Center

# Use same folder and file name
LOCAL_FILE = os.path.join(OUTPUT_FOLDER, "GOOGLE-DATA-Merchant.txt")
REMOTE_FILE = "GOOGLE-DATA-Merchant.txt"

def upload_file_to_google():
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.put(LOCAL_FILE, REMOTE_FILE)
        print("✅ Upload to Google Merchant SFTP successful.")
    except Exception as e:
        print("❌ SFTP upload failed:", str(e))
    finally:
        if 'sftp' in locals(): sftp.close()
        if 'transport' in locals(): transport.close()

# Call this after your file is ready
upload_file_to_google()
