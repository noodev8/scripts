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
from logging_utils import manage_log_files, create_logger, save_report_file, get_db_config

# Setup logging
SCRIPT_NAME = "merchant_feed"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


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


# Cleanup function removed - handled by shared logging system


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
            # Only process rows with valid GTIN (exactly 13 characters)
            if not (gtin and len(gtin) == 13 and gtin.isdigit()):
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

    # Save the feed to logs directory
    feed_content = feed_df.to_csv(index=False, sep="\t")
    output_file = save_report_file("GOOGLE-DATA-Merchant.txt", feed_content)

    cur.close()
    conn.close()

    log(f"=== MERCHANT FEED GENERATION STARTED ===")
    log(f"Feed file generated: {output_file}")
    log(f"Total products in feed: {len(feed_df)}")
    log(f"=== MERCHANT FEED GENERATION COMPLETED ===")
    print(f"Feed file generated: {output_file}")


if __name__ == "__main__":
    generate_feed()


# --- FTP The File Across ---
SFTP_HOST = 'partnerupload.google.com'
SFTP_PORT = 19321
SFTP_USERNAME = 'mc-sftp-124941872'       # From Merchant Center
SFTP_PASSWORD = 'V[,:Ua1#2p'       # Generate in Merchant Center

def upload_file_to_google():
    """Upload the generated feed file to Google Merchant Center via SFTP"""
    from logging_utils import get_logs_directory

    logs_dir = get_logs_directory()
    local_file = os.path.join(logs_dir, "GOOGLE-DATA-Merchant.txt")
    remote_file = "GOOGLE-DATA-Merchant.txt"

    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
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

# Call this after your file is ready
upload_file_to_google()
