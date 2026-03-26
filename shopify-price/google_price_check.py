#!/usr/bin/env python3
"""
Google Price Check Report (Phase 1)
Parses the Google Merchant Center price benchmark CSV,
aggregates variant-level data to groupid level using click-weighted averages,
and outputs a summary report CSV.

Note: Sale price suggestions report was dropped (Mar 2026) — it only ever
recommends price decreases and optimises for Google's clicks, not our profit.
We now use the benchmark report only.

Read-only: no database writes.
"""

import os
import sys
import glob
import psycopg2
import pandas as pd
from datetime import datetime

# Add parent directory to path so we can import logging_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "google_price_check"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Directory where Google CSV reports live (same as this script)
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# Filename patterns
BENCHMARK_PATTERN = "Your most popular products with price benchmarks_*.csv"
# Sale price suggestions report dropped (Mar 2026) — see docstring


def find_latest_csv(pattern):
    """Find the most recently modified CSV matching the given glob pattern."""
    files = glob.glob(os.path.join(REPORT_DIR, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def parse_benchmark_csv(filepath):
    """Parse the price benchmark report (skip 2 header rows: title + date range)."""
    df = pd.read_csv(filepath, skiprows=2)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'Product ID': 'googleid',
        'Your price': 'our_price_google',
        'Benchmark': 'benchmark',
        'Clicks': 'clicks',
        'Price gap': 'price_gap',
        'Title': 'title',
        'Brand': 'brand_google',
    })
    # Keep only the columns we need
    cols = ['googleid', 'title', 'benchmark', 'clicks', 'our_price_google']
    df = df[[c for c in cols if c in df.columns]].copy()
    # Coerce numeric columns
    for col in ['benchmark', 'clicks', 'our_price_google']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def fetch_sku_data(db_config):
    """Fetch googleid -> groupid mapping and pricing context from DB (read-only)."""
    conn = psycopg2.connect(**db_config)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.googleid, m.groupid, m.code,
                   ss.shopifyprice, ss.cost, ss.rrp, ss.brand, ss.tax
            FROM skumap m
            JOIN skusummary ss ON m.groupid = ss.groupid
            WHERE m.googleid IS NOT NULL AND m.googleid != ''
        """)
        rows = cur.fetchall()
        cols = ['googleid', 'groupid', 'code', 'shopifyprice', 'cost', 'rrp', 'brand', 'tax']
        df = pd.DataFrame(rows, columns=cols)
        # Coerce numeric columns from DB
        for col in ['shopifyprice', 'cost', 'rrp', 'tax']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        cur.close()
        return df
    finally:
        conn.close()


def weighted_avg(values, weights):
    """Compute weighted average, handling zero/NaN weights."""
    mask = weights.notna() & values.notna() & (weights > 0)
    if mask.sum() == 0:
        return None
    return (values[mask] * weights[mask]).sum() / weights[mask].sum()


def build_report(benchmark_df, sku_df):
    """Aggregate Google benchmark data to groupid level and build the report."""

    # --- Merge benchmark data with SKU map ---
    if benchmark_df is not None and not benchmark_df.empty:
        bench = benchmark_df.merge(sku_df[['googleid', 'groupid']], on='googleid', how='inner')
    else:
        bench = pd.DataFrame(columns=['googleid', 'groupid', 'title', 'benchmark', 'clicks'])

    # --- Aggregate benchmark data per groupid ---
    bench_agg = {}
    if not bench.empty:
        for gid, grp in bench.groupby('groupid'):
            bench_agg[gid] = {
                'benchmark_avg': weighted_avg(grp['benchmark'], grp['clicks']),
                'benchmark_min': grp['benchmark'].min(),
                'benchmark_max': grp['benchmark'].max(),
                'benchmark_clicks': grp['clicks'].sum(),
                'title_bench': grp.iloc[0]['title'] if 'title' in grp.columns else None,
            }

    all_groupids = set(bench_agg.keys())

    # --- Build pricing context lookup (one row per groupid) ---
    pricing = sku_df.drop_duplicates(subset='groupid').set_index('groupid')

    # --- Count variants per groupid ---
    variant_counts = {}
    for gid in all_groupids:
        bench_ids = set(bench[bench['groupid'] == gid]['googleid']) if not bench.empty else set()
        variant_counts[gid] = len(bench_ids)

    # --- Assemble output rows ---
    rows = []
    for gid in sorted(all_groupids):
        b = bench_agg.get(gid, {})
        p = pricing.loc[gid] if gid in pricing.index else pd.Series()

        our_price = p.get('shopifyprice')
        cost = p.get('cost')
        rrp = p.get('rrp')
        brand = p.get('brand')

        # Cost is already ex-VAT in the database
        net_cost = cost

        title = b.get('title_bench') or ''

        # Margin calculation
        margin_current = None
        if our_price and net_cost and our_price > 0:
            margin_current = round((our_price - net_cost) / our_price * 100, 1)

        rows.append({
            'groupid': gid,
            'brand': brand,
            'title': title,
            'our_price': our_price,
            'cost': cost,
            'rrp': rrp,
            'benchmark_avg': round(b['benchmark_avg'], 2) if b.get('benchmark_avg') is not None else None,
            'benchmark_min': round(b['benchmark_min'], 2) if b.get('benchmark_min') is not None else None,
            'benchmark_max': round(b['benchmark_max'], 2) if b.get('benchmark_max') is not None else None,
            'benchmark_clicks': b.get('benchmark_clicks'),
            'sizes_in_report': variant_counts.get(gid, 0),
            'margin_at_current': margin_current,
        })

    return pd.DataFrame(rows)


def main():
    log("=== GOOGLE PRICE CHECK REPORT STARTED ===")

    # --- Find latest benchmark CSV ---
    bench_file = find_latest_csv(BENCHMARK_PATTERN)

    if not bench_file:
        log("ERROR: No Google benchmark CSV found in shopify-price/ directory.")
        print("No benchmark report found. Place the Google benchmark CSV in shopify-price/ and re-run.")
        return

    log(f"Benchmark file: {os.path.basename(bench_file)}")

    # --- Parse CSV ---
    benchmark_df = parse_benchmark_csv(bench_file)
    log(f"Benchmark report: {len(benchmark_df)} variant rows parsed")

    # --- Fetch DB data ---
    log("Fetching SKU data from database...")
    db_config = get_db_config()
    sku_df = fetch_sku_data(db_config)
    log(f"Loaded {len(sku_df)} googleid mappings from skumap")

    # --- Build report ---
    report_df = build_report(benchmark_df, sku_df)

    if report_df.empty:
        log("WARNING: No matching products found between Google reports and database.")
        print("No matching products found. Check that Product IDs match skumap.googleid.")
        return

    # --- Save output CSV ---
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"price_report_{date_str}.csv"
    output_path = os.path.join(REPORT_DIR, output_filename)
    report_df.to_csv(output_path, index=False)
    log(f"Report saved: {output_path}")

    # --- Console summary ---
    total = len(report_df)
    with_bench = report_df['benchmark_avg'].notna().sum()

    summary = (
        f"\n{'='*60}\n"
        f"GOOGLE PRICE CHECK SUMMARY\n"
        f"{'='*60}\n"
        f"Total groupids in report:    {total}\n"
        f"With benchmark data:         {with_bench}\n"
        f"Output: {output_path}\n"
        f"{'='*60}"
    )
    print(summary)
    log(f"Report complete: {total} groupids ({with_bench} with benchmarks)")
    log("=== GOOGLE PRICE CHECK REPORT FINISHED ===")


if __name__ == '__main__':
    main()
