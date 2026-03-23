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

# ============================================================
# AUTO-DECISION RULES
# ============================================================
# Pre-sorts rows into accept / reject / review to reduce manual
# review effort. These are GUIDANCE only — the human always has
# final say via the 'change' column.
#
# Adjust thresholds here as you learn what works.
# Claude Code: read this section to understand current rules.
# ============================================================

# -- Reject: high confidence these should NOT change --
REJECT_NO_STOCK = True                # Reject when stock = 0 (no point changing price)
REJECT_SELLING_MIN_SOLD = 2           # At least this many sold in 30d = "it's selling".
                                      # If selling, trust actual sales over Google — reject regardless of drop size.
                                      # (Validated 2026-03-09: every item with 2+ sold was rejected or price-increased by user)

# -- Increase: items selling well enough to test a higher price --
# When an item hits the "selling well" threshold, instead of just rejecting
# Google's decrease, suggest a modest increase. The logic: if it's selling
# at the current price, there may be room to push higher.
INCREASE_UPLIFT_PCT = 5               # Default uplift % to suggest (capped at RRP)
INCREASE_MIN_STOCK = 3                # Need at least this much stock to suggest increase
                                      # (low stock + selling = let it run, don't increase)

# -- Review: large drops that MIGHT be right but need a human eye --
REVIEW_LARGE_DROP_PCT = -20           # Drops bigger than this get flagged for review

# -- Accept: high confidence these are worth doing --
ACCEPT_MIN_STOCK = 5                  # Need at least this much stock to auto-accept
ACCEPT_MAX_SOLD_30D = 1              # "Not selling" means this many or fewer in 30d
ACCEPT_MAX_DROP_PCT = -15             # Modest drop = within this % (negative = decrease)

# -- Proven demand: block auto-accept if current price has strong track record --
ACCEPT_PROVEN_DEMAND_TOLERANCE = 0.05  # 5% price band (e.g. £64.00 and £64.22 = same price)
ACCEPT_PROVEN_DEMAND_MIN_SOLD = 10     # 10+ units sold at nearby price in 365d = proven demand → review


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

        # Fetch total stock across all sizes per groupid (local + FBA)
        cur.execute("""
            SELECT groupid, COALESCE(SUM(qty), 0) AS stock
            FROM localstock
            WHERE groupid = ANY(%s)
            GROUP BY groupid
        """, (list(groupids),))
        stock_rows = cur.fetchall()
        stock_df = pd.DataFrame(stock_rows, columns=['groupid', 'stock'])

        cur.execute("""
            SELECT groupid, COALESCE(SUM(amzlive), 0) AS fba_stock
            FROM amzfeed
            WHERE groupid = ANY(%s)
            GROUP BY groupid
        """, (list(groupids),))
        fba_rows = cur.fetchall()
        fba_df = pd.DataFrame(fba_rows, columns=['groupid', 'fba_stock'])

        # Historical sales near current price (proven demand check)
        cur.execute("""
            SELECT s.groupid, COALESCE(SUM(s.qty), 0) AS sold_near_price
            FROM sales s
            JOIN skusummary ss ON s.groupid = ss.groupid
            WHERE s.groupid = ANY(%s)
              AND s.channel = 'SHP'
              AND s.qty > 0
              AND s.solddate >= CURRENT_DATE - INTERVAL '365 days'
              AND ss.shopifyprice IS NOT NULL
              AND ss.shopifyprice::numeric > 0
              AND ABS(s.soldprice - ss.shopifyprice::numeric) / ss.shopifyprice::numeric <= %s
            GROUP BY s.groupid
        """, (list(groupids), ACCEPT_PROVEN_DEMAND_TOLERANCE))
        demand_rows = cur.fetchall()
        demand_df = pd.DataFrame(demand_rows, columns=['groupid', 'sold_near_price'])

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
        if not fba_df.empty:
            df = df.join(fba_df.set_index('groupid'), how='left')
        df['fba_stock'] = df.get('fba_stock', pd.Series(dtype='float')).fillna(0).astype(int)
        df['stock'] = df['stock'] + df['fba_stock']
        if not demand_df.empty:
            df = df.join(demand_df.set_index('groupid'), how='left')
        df['sold_near_price'] = df.get('sold_near_price', pd.Series(dtype='float')).fillna(0).astype(int)

        return df
    finally:
        conn.close()


def calc_margin(price, net_cost):
    """Calculate margin % given price and net cost."""
    if price and net_cost and price > 0:
        return round((price - net_cost) / price * 100, 1)
    return None


def apply_auto_rules(df):
    """Apply auto-decision rules to pre-sort rows into accept/reject/review/increase.

    Rules are evaluated top-to-bottom; first match wins.
    See the AUTO-DECISION RULES config block at the top of this file.

    For 'increase' candidates, new_price and change_pct are overridden with
    a suggested increase (capped at RRP).
    """
    decisions = []
    reasons = []
    price_overrides = {}  # row index -> new suggested increase price

    for idx, row in df.iterrows():
        stock = row.get('stock', 0)
        sold = row.get('sold_30d', 0)
        current_price = row['current_price']
        new_price = row['new_price']
        rrp = row.get('rrp', None)
        drop_pct = ((new_price - current_price) / current_price * 100) if current_price > 0 else 0

        # --- Reject: no stock ---
        if REJECT_NO_STOCK and stock == 0:
            decisions.append('reject')
            reasons.append('no stock')
            continue

        # --- Selling well: suggest increase or reject ---
        if sold >= REJECT_SELLING_MIN_SOLD:
            # Enough stock to sustain sales? Suggest an increase.
            if stock >= INCREASE_MIN_STOCK:
                increase_target = round(current_price * (1 + INCREASE_UPLIFT_PCT / 100), 2)
                # Cap at RRP
                if pd.notna(rrp) and rrp > 0:
                    if current_price >= rrp:
                        decisions.append('reject')
                        reasons.append(f'selling ({sold} sold 30d) but already at RRP')
                        continue
                    increase_target = min(increase_target, rrp)
                pct = round((increase_target - current_price) / current_price * 100, 1)
                price_overrides[idx] = increase_target
                decisions.append('increase')
                reasons.append(f'selling well ({sold} sold 30d, stock {stock}) — suggest +{pct}%')
            else:
                # Low stock + selling = let it run through, don't touch
                decisions.append('reject')
                reasons.append(f'selling ({sold} sold 30d), low stock ({stock}) — let it run')
            continue

        # --- Review: large drops ---
        if drop_pct <= REVIEW_LARGE_DROP_PCT:
            decisions.append('review')
            reasons.append(f'large drop ({drop_pct:.0f}%) — check if warranted')
            continue

        # --- Review: proven demand at current price (would otherwise auto-accept) ---
        sold_near = row.get('sold_near_price', 0)
        if (stock >= ACCEPT_MIN_STOCK and sold <= ACCEPT_MAX_SOLD_30D
                and drop_pct >= ACCEPT_MAX_DROP_PCT
                and sold_near >= ACCEPT_PROVEN_DEMAND_MIN_SOLD):
            decisions.append('review')
            reasons.append(f'proven demand ({sold_near} sold near current price in 365d) — seasonal lull?')
            continue

        # --- Accept: stock + not selling + modest drop ---
        if stock >= ACCEPT_MIN_STOCK and sold <= ACCEPT_MAX_SOLD_30D and drop_pct >= ACCEPT_MAX_DROP_PCT:
            decisions.append('accept')
            reasons.append(f'stock {stock}, {sold} sold 30d, modest drop ({drop_pct:.0f}%)')
            continue

        # --- Everything else → review ---
        decisions.append('review')
        reasons.append('mixed signals — needs human check')

    df.insert(1, 'auto_decision', decisions)
    df.insert(2, 'auto_reason', reasons)

    # Override new_price and change_pct for increase candidates
    for idx, price in price_overrides.items():
        df.at[idx, 'new_price'] = price
        current = df.at[idx, 'current_price']
        if current > 0:
            df.at[idx, 'change_pct'] = round((price - current) / current * 100, 1)

    return df


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

        # Cost is already ex-VAT in the database
        net_cost = cost

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
            'change': '',
            'new_price': target,
            'description': description,
            'brand': row.get('brand', ''),
            'title': row.get('title', ''),
            'current_price': current_price,
            'rrp': rrp if pd.notna(rrp) else '',
            'price_diff': change,
            'change_pct': change_pct,
            'margin_current': margin_current,
            'margin_new': margin_new,
            'sold_30d': g.get('sold_30d', 0),
            'stock': g.get('stock', 0),
            'sold_near_price': g.get('sold_near_price', 0),
        })

    action_df = pd.DataFrame(rows)

    if not action_df.empty:
        # Apply auto-decision rules
        action_df = apply_auto_rules(action_df)

        # Sort: accept first, then review, then reject — within each group by drop magnitude
        decision_order = {'increase': 0, 'accept': 1, 'review': 2, 'reject': 3}
        action_df['_sort'] = action_df['auto_decision'].map(decision_order)
        action_df = action_df.sort_values(['_sort', 'change_pct'], ascending=[True, True]).reset_index(drop=True)
        action_df = action_df.drop(columns=['_sort', 'price_diff', 'margin_current', 'margin_new'])

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

    # Auto-decision breakdown
    if not action_df.empty and 'auto_decision' in action_df.columns:
        counts = action_df['auto_decision'].value_counts()
        n_increase = counts.get('increase', 0)
        n_accept = counts.get('accept', 0)
        n_review = counts.get('review', 0)
        n_reject = counts.get('reject', 0)
    else:
        n_increase = n_accept = n_review = n_reject = 0

    summary = (
        f"\n{'='*40}\n"
        f"GOOGLE PRICE ACTION REPORT ({mode_label})\n"
        f"{'='*40}\n"
        f"Products reviewed:  {total_reviewed:>6}\n"
        f"Actionable changes: {actionable:>6}\n"
        f"  Auto-increase:    {n_increase:>6}\n"
        f"  Auto-accept:      {n_accept:>6}\n"
        f"  Needs review:     {n_review:>6}\n"
        f"  Auto-reject:      {n_reject:>6}\n"
        f"Output: {output_path}\n"
        f"{'='*40}"
    )
    print(summary)
    log(f"Report complete: {actionable} actionable ({n_increase} increase, {n_accept} accept, {n_review} review, {n_reject} reject) from {total_reviewed} reviewed ({mode_label} mode)")
    log(f"=== GOOGLE PRICE ACTION REPORT ({mode_label}) FINISHED ===")


if __name__ == '__main__':
    main()
