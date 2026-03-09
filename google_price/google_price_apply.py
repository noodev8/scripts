#!/usr/bin/env python3
"""
Google Price Apply (Phase 3)

Reads an edited action report CSV and applies price changes to the database.
The nightly Shopify sync (price_update2.py) picks up rows where shopifychange=1.

Dry run by default — pass --confirm to apply changes.
"""

import os
import sys
import argparse
import psycopg2
import pandas as pd

# Add parent directory to path so we can import logging_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "google_price_apply"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Guardrail constants (matches price_recommendation.py)
MINIMUM_MARGIN_MULTIPLIER = 1.10

REQUIRED_COLUMNS = ['groupid', 'new_price', 'description']


def load_csv(filepath):
    """Load and validate the edited action report CSV.

    Returns (price_changes_df, all_rows_df):
        price_changes_df: rows with change=1 for price updates
        all_rows_df: all rows for description saving
    """
    df = pd.read_csv(filepath)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

    # All valid rows (for saving descriptions)
    all_rows = df[df['groupid'].notna()].copy()

    # Price changes: only rows explicitly flagged with change=1
    if 'change' in df.columns:
        changes = df[pd.to_numeric(df['change'], errors='coerce') == 1].copy()
    else:
        changes = df.copy()
    changes = changes[changes['groupid'].notna() & changes['new_price'].notna()].copy()
    changes['new_price'] = pd.to_numeric(changes['new_price'], errors='coerce')
    changes = changes[changes['new_price'].notna()]

    return changes, all_rows


def fetch_current_data(conn, groupids):
    """Fetch current shopifyprice, cost, and latest description from DB."""
    cur = conn.cursor()
    cur.execute("""
        SELECT groupid, shopifyprice, cost
        FROM skusummary
        WHERE groupid = ANY(%s)
    """, (list(groupids),))
    rows = cur.fetchall()
    result = {}
    for groupid, shopifyprice, cost in rows:
        result[groupid] = {
            'shopifyprice': float(shopifyprice) if shopifyprice is not None else None,
            'cost': float(cost) if cost is not None else None,
            'last_description': '',
        }

    # Fetch latest description per groupid from price_change_log
    cur.execute("""
        SELECT DISTINCT ON (groupid) groupid, reason_notes
        FROM price_change_log
        WHERE groupid = ANY(%s)
        ORDER BY groupid, change_date DESC, id DESC
    """, (list(groupids),))
    for groupid, reason_notes in cur.fetchall():
        if groupid in result:
            result[groupid]['last_description'] = str(reason_notes).strip() if reason_notes else ''

    cur.close()
    return result


def process_changes(csv_df, current_prices):
    """Evaluate each CSV row and categorise as apply, blocked, or skipped."""
    to_apply = []
    blocked = []
    skipped = []

    for _, row in csv_df.iterrows():
        gid = row['groupid']
        new_price = round(row['new_price'], 2)
        description = str(row.get('description', '')).strip()

        if gid not in current_prices:
            skipped.append((gid, 'not found in skusummary'))
            continue

        cp = current_prices[gid]
        old_price = cp['shopifyprice']
        cost = cp['cost']

        if old_price is None or cost is None:
            skipped.append((gid, 'missing price or cost'))
            continue

        # Skip no-change (within £0.01)
        if abs(new_price - old_price) < 0.01:
            skipped.append((gid, 'no change'))
            continue

        # Min margin guardrail (cost is already ex-VAT)
        min_price = round(cost * MINIMUM_MARGIN_MULTIPLIER, 2)
        if new_price < min_price:
            blocked.append((gid, old_price, new_price, min_price))
            continue

        to_apply.append({
            'groupid': gid,
            'old_price': old_price,
            'new_price': new_price,
            'description': description,
        })

    return to_apply, blocked, skipped


def apply_changes(conn, changes):
    """Write price changes to skusummary and price_change_log."""
    cur = conn.cursor()
    for ch in changes:
        cur.execute("""
            UPDATE skusummary
            SET shopifyprice = %s, shopifychange = 1
            WHERE groupid = %s
        """, (ch['new_price'], ch['groupid']))

        cur.execute("""
            INSERT INTO price_change_log
                (groupid, old_price, new_price, reason_code, reason_notes, changed_by, channel)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            ch['groupid'],
            ch['old_price'],
            ch['new_price'],
            'google_price',
            ch['description'],
            'google_price_action',
            'SHP',
        ))
    conn.commit()
    cur.close()


def save_descriptions(conn, all_rows_df, current_data, applied_groupids):
    """Save updated descriptions to price_change_log for rows where the note changed.

    Skips groupids that already got a price_change_log entry from apply_changes.
    Inserts a note-only entry (old_price = new_price = current price) so the
    description carries forward to the next Phase 2 run.
    """
    cur = conn.cursor()
    saved = []
    for _, row in all_rows_df.iterrows():
        gid = row['groupid']
        desc = str(row.get('description', '')).strip()

        # Skip if no description, not in DB, or already updated via price change
        if not desc or gid not in current_data or gid in applied_groupids:
            continue

        current_desc = current_data[gid].get('last_description', '')
        if desc == current_desc:
            continue  # No change

        current_price = current_data[gid]['shopifyprice']
        if current_price is None:
            continue

        cur.execute("""
            INSERT INTO price_change_log
                (groupid, old_price, new_price, reason_code, reason_notes, changed_by, channel)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (gid, current_price, current_price, 'google_price_note', desc, 'google_price_action', 'SHP'))
        saved.append(gid)

    conn.commit()
    cur.close()
    return saved


def print_summary(to_apply, blocked, skipped, confirm, saved_notes=None):
    """Print a human-readable summary to console."""
    mode_label = "GOOGLE PRICE APPLY" if confirm else "GOOGLE PRICE APPLY - DRY RUN"
    prefix = "Applied" if confirm else "Would update"

    print(f"\n{mode_label}")
    print("=" * 40)

    if to_apply:
        print(f"{prefix}: {len(to_apply)} prices")
        for ch in to_apply:
            desc_snippet = ch['description'][:50] if ch['description'] else ''
            print(f"  {ch['groupid']}: {ch['old_price']:.2f} -> {ch['new_price']:.2f}  \"{desc_snippet}\"")
    else:
        print(f"{prefix}: 0 prices")

    if blocked:
        print(f"Blocked: {len(blocked)} (below min margin)")
        for gid, old_p, new_p, min_p in blocked:
            print(f"  {gid}: {new_p:.2f} below floor {min_p:.2f}")

    if skipped:
        print(f"Skipped: {len(skipped)}")

    if saved_notes:
        print(f"Description updates saved: {len(saved_notes)}")

    if confirm and to_apply:
        print("Flagged for Shopify sync (shopifychange=1)")
    elif not confirm and to_apply:
        print("\nRun again with --confirm to apply.")

    print("=" * 40)


def main():
    parser = argparse.ArgumentParser(description="Apply Google price action changes to database")
    parser.add_argument('csv_file', help="Path to the edited action report CSV")
    parser.add_argument('--confirm', action='store_true', help="Apply changes (default is dry run)")
    args = parser.parse_args()

    csv_path = args.csv_file
    confirm = args.confirm

    log(f"=== GOOGLE PRICE APPLY {'CONFIRMED' if confirm else 'DRY RUN'} STARTED ===")
    log(f"CSV file: {csv_path}")

    if not os.path.isfile(csv_path):
        print(f"Error: file not found: {csv_path}")
        log(f"ERROR: file not found: {csv_path}")
        sys.exit(1)

    # Load and validate CSV
    try:
        csv_df, all_rows_df = load_csv(csv_path)
    except ValueError as e:
        print(f"Error: {e}")
        log(f"ERROR: {e}")
        sys.exit(1)

    log(f"Loaded {len(csv_df)} price change rows, {len(all_rows_df)} total rows from CSV")

    if csv_df.empty and all_rows_df.empty:
        print("No valid rows in CSV. Nothing to do.")
        log("No valid rows in CSV")
        return

    # Connect to DB and fetch current data (prices + descriptions)
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    try:
        all_groupids = all_rows_df['groupid'].tolist()
        current_data = fetch_current_data(conn, all_groupids)
        log(f"Fetched current data for {len(current_data)} groupids")

        # Process price changes (change=1 rows)
        to_apply, blocked, skipped = process_changes(csv_df, current_data)
        log(f"To apply: {len(to_apply)}, Blocked: {len(blocked)}, Skipped: {len(skipped)}")

        # Apply if confirmed
        applied_groupids = set()
        if confirm and to_apply:
            apply_changes(conn, to_apply)
            applied_groupids = {ch['groupid'] for ch in to_apply}
            log(f"Applied {len(to_apply)} price changes")
        elif confirm and not to_apply:
            log("Confirmed but nothing to apply")

        # Save description updates for ALL rows (including change=0)
        saved_notes = []
        if confirm:
            saved_notes = save_descriptions(conn, all_rows_df, current_data, applied_groupids)
            if saved_notes:
                log(f"Saved {len(saved_notes)} description updates")

        print_summary(to_apply, blocked, skipped, confirm, saved_notes)
    finally:
        conn.close()

    log(f"=== GOOGLE PRICE APPLY {'CONFIRMED' if confirm else 'DRY RUN'} FINISHED ===")


if __name__ == '__main__':
    main()
