#!/usr/bin/env python3
"""
Google Price Action Report (Grow / Protect modes)

Reads the data report CSV from google_price_check.py and produces a clean,
short list of recommended price changes based on a chosen strategy mode:

- Grow (default): Price aggressively to win clicks/sales (targets Google's suggested sale price)
- Protect: Price conservatively to increase margin (targets benchmark average)

Read-only: no database writes.
"""

import os
import sys
import glob
import argparse
import psycopg2
import pandas as pd
from datetime import datetime

# Add parent directory to path so we can import logging_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "google_price_action"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Directory where reports live (same as this script)
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# Guardrail constants (matches price_recommendation.py)
MINIMUM_MARGIN_MULTIPLIER = 1.10  # Cost * 1.10 minimum price floor


def find_latest_data_report():
    """Find the most recently modified price_report_*.csv."""
    files = glob.glob(os.path.join(REPORT_DIR, "price_report_*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def fetch_guardrail_data(groupids):
    """Fetch cost, tax, rrp, shopifyprice from skusummary and latest reason_notes from price_change_log."""
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT groupid, shopifyprice, cost, rrp, tax
            FROM skusummary
            WHERE groupid = ANY(%s)
        """, (list(groupids),))
        rows = cur.fetchall()
        cols = ['groupid', 'shopifyprice', 'cost', 'rrp', 'tax']
        df = pd.DataFrame(rows, columns=cols)
        for col in ['shopifyprice', 'cost', 'rrp', 'tax']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Fetch latest reason_notes per groupid
        cur.execute("""
            SELECT DISTINCT ON (groupid) groupid, reason_notes
            FROM price_change_log
            WHERE groupid = ANY(%s)
            ORDER BY groupid, change_date DESC, id DESC
        """, (list(groupids),))
        notes_rows = cur.fetchall()
        notes_df = pd.DataFrame(notes_rows, columns=['groupid', 'last_description'])

        # Fetch units sold in last 30 days per groupid
        cur.execute("""
            SELECT groupid, COALESCE(SUM(qty), 0) AS sold_30d
            FROM sales
            WHERE groupid = ANY(%s)
              AND solddate >= CURRENT_DATE - INTERVAL '30 days'
              AND channel = 'SHP'
            GROUP BY groupid
        """, (list(groupids),))
        sales_rows = cur.fetchall()
        sales_df = pd.DataFrame(sales_rows, columns=['groupid', 'sold_30d'])

        # Fetch total stock across all sizes per groupid
        cur.execute("""
            SELECT groupid, COALESCE(SUM(qty), 0) AS stock
            FROM localstock
            WHERE groupid = ANY(%s)
            GROUP BY groupid
        """, (list(groupids),))
        stock_rows = cur.fetchall()
        stock_df = pd.DataFrame(stock_rows, columns=['groupid', 'stock'])

        cur.close()

        df = df.set_index('groupid')
        if not notes_df.empty:
            df = df.join(notes_df.set_index('groupid'), how='left')
        else:
            df['last_description'] = None
        if not sales_df.empty:
            df = df.join(sales_df.set_index('groupid'), how='left')
        df['sold_30d'] = df.get('sold_30d', pd.Series(dtype='float')).fillna(0).astype(int)
        if not stock_df.empty:
            df = df.join(stock_df.set_index('groupid'), how='left')
        df['stock'] = df.get('stock', pd.Series(dtype='float')).fillna(0).astype(int)

        return df
    finally:
        conn.close()


def calc_margin(price, net_cost):
    """Calculate margin % given price and net cost."""
    if price and net_cost and price > 0:
        return round((price - net_cost) / price * 100, 1)
    return None


def build_action_report(report_df, guardrail_df, mode):
    """Build the action report for the given mode.

    Args:
        report_df: DataFrame from the data report CSV.
        guardrail_df: DataFrame indexed by groupid with cost/rrp/tax/shopifyprice.
        mode: 'grow' or 'protect'.

    Returns:
        DataFrame of actionable price changes.
    """
    rows = []

    for _, row in report_df.iterrows():
        gid = row['groupid']

        # Get guardrail data from DB (preferred source of truth for current price)
        if gid not in guardrail_df.index:
            continue
        g = guardrail_df.loc[gid]

        current_price = g['shopifyprice']
        cost = g['cost']
        rrp = g['rrp']
        tax = g['tax']

        if pd.isna(current_price) or pd.isna(cost):
            continue

        # Net cost: if tax=1, cost is VAT-inclusive -> divide by 1.2
        net_cost = cost / 1.2 if tax == 1 else cost

        # Determine raw target price based on mode
        if mode == 'grow':
            suggested = row.get('suggested_avg')
            benchmark = row.get('benchmark_avg')

            if pd.notna(suggested):
                raw_target = suggested
                source = "google_suggestion"
            elif pd.notna(benchmark):
                raw_target = benchmark
                source = "benchmark_fallback"
            else:
                continue  # No data to act on
        else:  # protect
            benchmark = row.get('benchmark_avg')
            if pd.isna(benchmark):
                continue  # No benchmark data
            raw_target = benchmark
            source = "benchmark"

        # Apply guardrails
        target = raw_target

        # Min margin floor
        min_price = net_cost * MINIMUM_MARGIN_MULTIPLIER
        if target < min_price:
            target = min_price

        # RRP ceiling
        if pd.notna(rrp) and target > rrp:
            target = rrp

        # Round to 2dp
        target = round(target, 2)

        # Direction check: Grow = decreases only, Protect = increases only
        if mode == 'grow' and target >= current_price:
            continue
        if mode == 'protect' and target <= current_price:
            continue

        # Skip no-change (within £0.01)
        if abs(target - current_price) < 0.01:
            continue

        change = round(target - current_price, 2)
        change_pct = round(change / current_price * 100, 1) if current_price > 0 else None

        margin_current = calc_margin(current_price, net_cost)
        margin_new = calc_margin(target, net_cost)

        # Use existing description from price_change_log, or generate a new one
        last_desc = g.get('last_description')
        if pd.notna(last_desc) and str(last_desc).strip():
            description = str(last_desc).strip()
        else:
            direction = "reduced" if change < 0 else "raised"
            source_label = source.replace("_", " ")
            description = f"{mode.capitalize()} mode: {direction} from {current_price:.2f} to {target:.2f} ({source_label})"

        rows.append({
            'groupid': gid,
            'new_price': target,
            'description': description,
            'brand': row.get('brand', ''),
            'title': row.get('title', ''),
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'margin_current': margin_current,
            'margin_new': margin_new,
            'sold_30d': g.get('sold_30d', 0),
            'stock': g.get('stock', 0),
        })

    action_df = pd.DataFrame(rows)

    if not action_df.empty:
        # Sort by magnitude of change_pct (largest opportunity first)
        action_df = action_df.sort_values('change_pct', key=abs, ascending=False).reset_index(drop=True)

    return action_df


def main():
    parser = argparse.ArgumentParser(description="Google Price Action Report")
    parser.add_argument('--protect', action='store_true', help="Use Protect mode (default is Grow)")
    args = parser.parse_args()

    mode = 'protect' if args.protect else 'grow'
    mode_label = mode.upper()

    log(f"=== GOOGLE PRICE ACTION REPORT ({mode_label}) STARTED ===")

    # Find latest data report
    data_file = find_latest_data_report()
    if not data_file:
        log("ERROR: No price_report_*.csv found. Run google_price_check.py first.")
        print("No data report found. Run google_price_check.py first.")
        return

    log(f"Data report: {os.path.basename(data_file)}")

    # Load data report
    report_df = pd.read_csv(data_file)
    log(f"Loaded {len(report_df)} groupids from data report")

    # Fetch guardrail data from DB
    log("Fetching guardrail data from database...")
    groupids = report_df['groupid'].tolist()
    guardrail_df = fetch_guardrail_data(groupids)
    log(f"Loaded guardrail data for {len(guardrail_df)} groupids")

    # Build action report
    action_df = build_action_report(report_df, guardrail_df, mode)

    # Save output CSV
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"price_action_{mode}_{date_str}.csv"
    output_path = os.path.join(REPORT_DIR, output_filename)
    action_df.to_csv(output_path, index=False)
    log(f"Action report saved: {output_path}")

    # Console summary
    total_reviewed = len(report_df)
    actionable = len(action_df)

    if actionable > 0:
        avg_change_pct = round(action_df['change_pct'].mean(), 1)
        avg_margin_impact = round(
            (action_df['margin_new'] - action_df['margin_current']).mean(), 1
        )
    else:
        avg_change_pct = 0.0
        avg_margin_impact = 0.0

    summary = (
        f"\n{'='*40}\n"
        f"GOOGLE PRICE ACTION REPORT ({mode_label})\n"
        f"{'='*40}\n"
        f"Products reviewed:  {total_reviewed:>6}\n"
        f"Actionable changes: {actionable:>6}\n"
        f"Avg price change:   {avg_change_pct:>5}%\n"
        f"Avg margin impact:  {avg_margin_impact:>5}pp\n"
        f"Output: {output_path}\n"
        f"{'='*40}"
    )
    print(summary)
    log(f"Report complete: {actionable} actionable changes from {total_reviewed} reviewed ({mode_label} mode)")
    log(f"=== GOOGLE PRICE ACTION REPORT ({mode_label}) FINISHED ===")


if __name__ == '__main__':
    main()
