#!/usr/bin/env python3
"""
Google Price Check Report (Phase 1)
Parses the Google Merchant Center price benchmark CSV and sale price
suggestions (performance) CSV, aggregates variant-level data to groupid
level using click-weighted averages, and outputs a summary report CSV.

The benchmark shows where we sit vs competitors; the performance report
shows Google's view on prices that drive the most sales — useful for
high-stock, end-of-season, or ramp-up scenarios.

Also pulls 30-day sales and current stock from the database so the
report doubles as a combined overview of all pricing signals.

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
PERFORMANCE_PATTERN = "Sale price suggestions with highest performance impact_*.csv"

# Effectiveness tier ordering (higher = better)
EFFECTIVENESS_RANK = {'High': 3, 'Medium': 2, 'Low': 1}


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


def parse_performance_csv(filepath):
    """Parse the sale price suggestions (performance) report (skip 1 title row)."""
    df = pd.read_csv(filepath, skiprows=1)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'Product ID': 'googleid',
        'Suggested price': 'performance_price',
        'Click uplift': 'click_uplift',
        'Conversion uplift': 'conversion_uplift',
        'Effectiveness': 'effectiveness',
    })
    cols = ['googleid', 'performance_price', 'click_uplift', 'conversion_uplift', 'effectiveness']
    df = df[[c for c in cols if c in df.columns]].copy()
    for col in ['performance_price', 'click_uplift', 'conversion_uplift']:
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


def fetch_sales_stock_data(db_config, groupids):
    """Fetch 30-day sales and current stock per groupid (read-only)."""
    conn = psycopg2.connect(**db_config)
    try:
        cur = conn.cursor()

        # 30-day Shopify sales
        cur.execute("""
            SELECT groupid, COALESCE(SUM(qty), 0) AS sold_30d
            FROM sales
            WHERE groupid = ANY(%s)
              AND channel = 'SHP'
              AND solddate >= CURRENT_DATE - 30
              AND qty > 0
            GROUP BY groupid
        """, (list(groupids),))
        sales_rows = cur.fetchall()
        sales_df = pd.DataFrame(sales_rows, columns=['groupid', 'sold_30d'])

        # Current stock (local warehouse)
        cur.execute("""
            SELECT groupid, COALESCE(SUM(qty), 0) AS stock
            FROM localstock
            WHERE groupid = ANY(%s) AND deleted = 0
            GROUP BY groupid
        """, (list(groupids),))
        stock_rows = cur.fetchall()
        stock_df = pd.DataFrame(stock_rows, columns=['groupid', 'stock'])

        cur.close()
        return sales_df, stock_df
    finally:
        conn.close()


def weighted_avg(values, weights):
    """Compute weighted average, handling zero/NaN weights."""
    mask = weights.notna() & values.notna() & (weights > 0)
    if mask.sum() == 0:
        return None
    return (values[mask] * weights[mask]).sum() / weights[mask].sum()


def best_effectiveness(series):
    """Return the highest effectiveness tier from a series of values."""
    ranked = series.dropna().map(EFFECTIVENESS_RANK)
    if ranked.empty:
        return None
    best_rank = ranked.max()
    for label, rank in EFFECTIVENESS_RANK.items():
        if rank == best_rank:
            return label
    return None


def build_report(benchmark_df, performance_df, sku_df, sales_df, stock_df):
    """Aggregate Google data to groupid level and build the combined report."""

    # --- Merge benchmark data with SKU map ---
    if benchmark_df is not None and not benchmark_df.empty:
        bench = benchmark_df.merge(sku_df[['googleid', 'groupid']], on='googleid', how='inner')
    else:
        bench = pd.DataFrame(columns=['googleid', 'groupid', 'title', 'benchmark', 'clicks'])

    # --- Merge performance data with SKU map ---
    if performance_df is not None and not performance_df.empty:
        perf = performance_df.merge(sku_df[['googleid', 'groupid']], on='googleid', how='inner')
        # Bring in benchmark clicks for weighting performance aggregation
        if not bench.empty:
            clicks_lookup = bench[['googleid', 'clicks']].drop_duplicates(subset='googleid')
            perf = perf.merge(clicks_lookup, on='googleid', how='left')
        else:
            perf['clicks'] = None
    else:
        perf = pd.DataFrame(columns=['googleid', 'groupid', 'performance_price',
                                     'click_uplift', 'conversion_uplift', 'effectiveness', 'clicks'])

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

    # --- Aggregate performance data per groupid ---
    perf_agg = {}
    if not perf.empty:
        for gid, grp in perf.groupby('groupid'):
            # Use benchmark clicks as weights if available, else simple average
            has_clicks = grp['clicks'].notna().any() and (grp['clicks'] > 0).any()
            if has_clicks:
                pp = weighted_avg(grp['performance_price'], grp['clicks'])
            else:
                pp = grp['performance_price'].mean()

            perf_agg[gid] = {
                'performance_price': round(pp, 2) if pp is not None else None,
                'click_uplift': round(grp['click_uplift'].mean(), 2) if grp['click_uplift'].notna().any() else None,
                'conversion_uplift': round(grp['conversion_uplift'].mean(), 2) if grp['conversion_uplift'].notna().any() else None,
                'effectiveness': best_effectiveness(grp['effectiveness']),
            }

    all_groupids = set(bench_agg.keys()) | set(perf_agg.keys())

    # --- Build lookups ---
    pricing = sku_df.drop_duplicates(subset='groupid').set_index('groupid')

    sales_lookup = {}
    if sales_df is not None and not sales_df.empty:
        sales_lookup = sales_df.set_index('groupid')['sold_30d'].to_dict()

    stock_lookup = {}
    if stock_df is not None and not stock_df.empty:
        stock_lookup = stock_df.set_index('groupid')['stock'].to_dict()

    # --- Count variants per groupid ---
    variant_counts = {}
    for gid in all_groupids:
        bench_ids = set(bench[bench['groupid'] == gid]['googleid']) if not bench.empty else set()
        perf_ids = set(perf[perf['groupid'] == gid]['googleid']) if not perf.empty else set()
        variant_counts[gid] = len(bench_ids | perf_ids)

    # --- Assemble output rows ---
    rows = []
    for gid in sorted(all_groupids):
        b = bench_agg.get(gid, {})
        pe = perf_agg.get(gid, {})
        p = pricing.loc[gid] if gid in pricing.index else pd.Series()

        our_price = p.get('shopifyprice')
        cost = p.get('cost')
        rrp = p.get('rrp')
        brand = p.get('brand')

        title = b.get('title_bench') or ''

        # Margin calculation (cost is already ex-VAT in the database)
        margin_current = None
        if our_price and cost and our_price > 0:
            margin_current = round((our_price - cost) / our_price * 100, 1)

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
            'performance_price': pe.get('performance_price'),
            'click_uplift': pe.get('click_uplift'),
            'conversion_uplift': pe.get('conversion_uplift'),
            'effectiveness': pe.get('effectiveness'),
            'stock': stock_lookup.get(gid, 0),
            'sold_30d': sales_lookup.get(gid, 0),
            'sizes_in_report': variant_counts.get(gid, 0),
            'margin_at_current': margin_current,
        })

    return pd.DataFrame(rows)


def main():
    log("=== GOOGLE PRICE CHECK REPORT STARTED ===")

    # --- Find latest CSVs ---
    bench_file = find_latest_csv(BENCHMARK_PATTERN)
    perf_file = find_latest_csv(PERFORMANCE_PATTERN)

    if not bench_file:
        log("ERROR: No Google benchmark CSV found in shopify-price/ directory.")
        print("No benchmark report found. Place the Google benchmark CSV in shopify-price/ and re-run.")
        return

    log(f"Benchmark file: {os.path.basename(bench_file)}")

    if perf_file:
        log(f"Performance file: {os.path.basename(perf_file)}")
    else:
        log("No performance CSV found — report will have benchmark data only.")

    # --- Parse CSVs ---
    benchmark_df = parse_benchmark_csv(bench_file)
    log(f"Benchmark report: {len(benchmark_df)} variant rows parsed")

    performance_df = None
    if perf_file:
        performance_df = parse_performance_csv(perf_file)
        log(f"Performance report: {len(performance_df)} variant rows parsed")

    # --- Fetch DB data ---
    log("Fetching SKU data from database...")
    db_config = get_db_config()
    sku_df = fetch_sku_data(db_config)
    log(f"Loaded {len(sku_df)} googleid mappings from skumap")

    # Get groupids that appear in either report
    matched_bench = set()
    if benchmark_df is not None and not benchmark_df.empty:
        merged = benchmark_df.merge(sku_df[['googleid', 'groupid']], on='googleid', how='inner')
        matched_bench = set(merged['groupid'])
    matched_perf = set()
    if performance_df is not None and not performance_df.empty:
        merged = performance_df.merge(sku_df[['googleid', 'groupid']], on='googleid', how='inner')
        matched_perf = set(merged['groupid'])
    all_matched = matched_bench | matched_perf

    # Fetch sales + stock for matched groupids
    sales_df, stock_df = fetch_sales_stock_data(db_config, all_matched) if all_matched else (None, None)

    # --- Build report ---
    report_df = build_report(benchmark_df, performance_df, sku_df, sales_df, stock_df)

    if report_df.empty:
        log("WARNING: No matching products found between Google reports and database.")
        print("No matching products found. Check that Product IDs match skumap.googleid.")
        return

    # --- Save output CSV (always overwrite latest in report/) ---
    report_subdir = os.path.join(REPORT_DIR, 'report')
    os.makedirs(report_subdir, exist_ok=True)
    output_path = os.path.join(report_subdir, 'price_report.csv')
    report_df.to_csv(output_path, index=False)
    log(f"Report saved: {output_path}")

    # --- Console summary ---
    total = len(report_df)
    with_bench = report_df['benchmark_avg'].notna().sum()
    with_perf = report_df['performance_price'].notna().sum()
    with_both = ((report_df['benchmark_avg'].notna()) & (report_df['performance_price'].notna())).sum()

    summary = (
        f"\n{'='*60}\n"
        f"GOOGLE PRICE CHECK SUMMARY\n"
        f"{'='*60}\n"
        f"Total groupids in report:    {total}\n"
        f"With benchmark data:         {with_bench}\n"
        f"With performance data:       {with_perf}\n"
        f"With both:                   {with_both}\n"
        f"Output: {output_path}\n"
        f"{'='*60}"
    )
    print(summary)
    log(f"Report complete: {total} groupids ({with_bench} benchmark, {with_perf} performance, {with_both} both)")

    # --- Clean up source CSVs (data is now in the report) ---
    for f in [bench_file, perf_file]:
        if f and os.path.exists(f):
            os.remove(f)
            log(f"Cleaned up: {os.path.basename(f)}")

    log("=== GOOGLE PRICE CHECK REPORT FINISHED ===")


if __name__ == '__main__':
    main()
