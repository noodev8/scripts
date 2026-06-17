#!/usr/bin/env python3
"""
Portfolio Scan — competitive pricing triage across the whole catalogue.

Reads the two Google Merchant CSVs (already pulled into this folder by
refresh_google_csvs.py) and rolls them up to groupid level, joined to the live
DB, so we get a one-screen view of where we sit vs the market instead of going
product-by-product.

Two Google signals, doing different jobs:
  * Benchmark file ("Your most popular products with price benchmarks") —
    where our price sits vs Google's competitive benchmark. The diagnostic.
    Price gap > 0  => we are ABOVE benchmark (pricier than competitors).
  * Sale-price suggestions ("...highest performance impact") — Google's
    aggressive "cut to here and you'll move volume" price, with an
    Effectiveness rating. The provocation — take with a pinch of salt because
    it optimises clicks/conversions, not our margin.

Default lens (what this prints): OVER-BENCHMARK + HIGH CLICKS first — the
styles we're paying Ads traffic for while priced above the market. That's the
"losing to competition" bleed list.

Join: Google "Product ID" == skumap.googleid (exact, no normalisation needed).
       skumap.googleid -> skumap.groupid -> skusummary (price/cost/bounds).

Usage:
    python shopify-price/portfolio_scan.py                 # over-benchmark lens
    python shopify-price/portfolio_scan.py --min-clicks 30
    python shopify-price/portfolio_scan.py --under         # under-benchmark (margin left on table)
    python shopify-price/portfolio_scan.py --all           # every matched groupid, no gap filter

Reads live data only. Writes nothing to the DB. Saves a full CSV alongside the
inputs (portfolio_scan_<date-of-benchmark-file>.csv, gitignored).
"""

import os
import sys
import glob
import argparse
import psycopg2
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

HERE = os.path.dirname(os.path.abspath(__file__))

BENCH_GLOB = "Your most popular products with price benchmarks_*.csv"
SUGG_GLOB = "Sale price suggestions with highest performance impact_*.csv"

EFF_RANK = {"High": 3, "Medium": 2, "Low": 1}

# Net-profit cost constants (see README "Cost constants").
WAGES = 1.00
POSTAGE = 3.44


def latest(pattern):
    files = glob.glob(os.path.join(HERE, pattern))
    if not files:
        sys.exit(f"No file matching '{pattern}' in {HERE}. "
                 f"Run refresh_google_csvs.py first.")
    return max(files, key=os.path.getmtime)


def net_margin_pct(price, cost, tax):
    """Net profit as % of price, using README cost constants."""
    if price is None or price <= 0 or cost is None:
        return None
    vat = price / 6 if tax == 1 else 0.0
    payment_fee = 0.30 + 0.029 * price
    net = price - vat - float(cost) - payment_fee - WAGES - POSTAGE
    return 100.0 * net / price


def load_benchmark(path):
    # First two lines are title + time period; header is line 3.
    df = pd.read_csv(path, skiprows=2)
    df = df.rename(columns={
        "Product ID": "googleid", "Your price": "your_price",
        "Benchmark": "benchmark", "Price gap": "gap", "Clicks": "clicks",
    })
    df["googleid"] = df["googleid"].astype(str).str.strip()
    for c in ("your_price", "benchmark", "gap", "clicks"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["your_price", "benchmark", "clicks"])


def load_suggestions(path):
    # One title line ("Name: ...") before the header.
    df = pd.read_csv(path, skiprows=1, encoding="utf-8-sig")
    df = df.rename(columns={
        "Product ID": "googleid", "Your price": "your_price",
        "Suggested price": "suggested_price", "Effectiveness": "effectiveness",
    })
    df["googleid"] = df["googleid"].astype(str).str.strip()
    for c in ("your_price", "suggested_price"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["eff_rank"] = df["effectiveness"].map(EFF_RANK).fillna(0)
    return df.dropna(subset=["suggested_price"])


def load_db():
    conn = psycopg2.connect(**get_db_config())
    try:
        skumap = pd.read_sql(
            "SELECT googleid, groupid FROM skumap "
            "WHERE deleted=0 AND googleid IS NOT NULL", conn)
        sku = pd.read_sql(
            "SELECT groupid, brand, shopifyprice, cost, rrp, "
            "minshopifyprice, maxshopifyprice, season, tax "
            "FROM skusummary", conn)
    finally:
        conn.close()
    skumap["googleid"] = skumap["googleid"].astype(str).str.strip()
    for c in ("shopifyprice", "cost", "rrp", "minshopifyprice", "maxshopifyprice"):
        sku[c] = pd.to_numeric(sku[c], errors="coerce")
    return skumap, sku


def main():
    ap = argparse.ArgumentParser(description="Competitive pricing triage.")
    ap.add_argument("--min-clicks", type=int, default=20,
                    help="Min total clicks for a groupid to show (default 20).")
    ap.add_argument("--under", action="store_true",
                    help="Show UNDER-benchmark (cheaper than market) instead.")
    ap.add_argument("--all", action="store_true",
                    help="No gap filter — every matched groupid.")
    ap.add_argument("--top", type=int, default=40,
                    help="Rows to print (default 40). CSV always has all.")
    args = ap.parse_args()

    bench_path = latest(BENCH_GLOB)
    sugg_path = latest(SUGG_GLOB)
    print(f"Benchmark   : {os.path.basename(bench_path)}")
    print(f"Suggestions : {os.path.basename(sugg_path)}\n")

    bench = load_benchmark(bench_path)
    sugg = load_suggestions(sugg_path)
    skumap, sku = load_db()

    g2group = dict(zip(skumap["googleid"], skumap["groupid"]))

    # --- Benchmark rollup to groupid (click-weighted) ---
    bench["groupid"] = bench["googleid"].map(g2group)
    matched = bench["groupid"].notna()
    unmatched_clicks = int(bench.loc[~matched, "clicks"].sum())
    b = bench[matched].copy()
    b["w_price"] = b["your_price"] * b["clicks"]
    b["w_bench"] = b["benchmark"] * b["clicks"]
    grp = b.groupby("groupid").agg(
        clicks=("clicks", "sum"),
        wp=("w_price", "sum"),
        wb=("w_bench", "sum"),
        sizes=("googleid", "count"),
    ).reset_index()
    grp["our_price"] = grp["wp"] / grp["clicks"]
    grp["bench"] = grp["wb"] / grp["clicks"]
    grp["gap_pct"] = 100.0 * (grp["our_price"] - grp["bench"]) / grp["bench"]

    # --- Suggestions rollup to groupid ---
    sugg["groupid"] = sugg["googleid"].map(g2group)
    s = sugg[sugg["groupid"].notna()].copy()
    sg = s.groupby("groupid").agg(
        n_sugg=("suggested_price", "count"),
        sugg_price=("suggested_price", "mean"),
        sugg_yourprice=("your_price", "mean"),
        best_eff=("eff_rank", "max"),
        n_high=("eff_rank", lambda x: int((x == 3).sum())),
    ).reset_index()
    rank2eff = {3: "High", 2: "Medium", 1: "Low", 0: "-"}
    sg["best_eff"] = sg["best_eff"].map(rank2eff)
    sg["sugg_cut_pct"] = 100.0 * (1 - sg["sugg_price"] / sg["sugg_yourprice"])

    # --- Join everything ---
    out = grp.merge(sg, on="groupid", how="left").merge(sku, on="groupid", how="left")
    out["net_now_pct"] = out.apply(
        lambda r: net_margin_pct(r["shopifyprice"], r["cost"], r["tax"]), axis=1)
    out["net_sugg_pct"] = out.apply(
        lambda r: net_margin_pct(r["sugg_price"], r["cost"], r["tax"]), axis=1)

    # --- Lens ---
    if args.all:
        view, title = out, "ALL matched groupids"
    elif args.under:
        view = out[out["gap_pct"] < 0]
        title = "UNDER benchmark (cheaper than market — margin may be on table)"
    else:
        view = out[out["gap_pct"] > 0]
        title = "OVER benchmark + high clicks (losing to competition)"

    view = view[view["clicks"] >= args.min_clicks].sort_values(
        "clicks", ascending=False)

    # --- Print ---
    print(f"Lens: {title}")
    print(f"Min clicks: {args.min_clicks}   |   "
          f"matched groupids: {out['groupid'].nunique()}   |   "
          f"unmatched clicks (no googleid->groupid): {unmatched_clicks}\n")

    hdr = (f"{'groupid':22} {'brand':12} {'clk':>5} {'our':>7} {'bench':>7} "
           f"{'gap%':>6} {'now':>7} {'net%':>6} {'gSugg':>7} {'cut%':>6} "
           f"{'eff':>6} {'season':>7}")
    print(hdr)
    print("-" * len(hdr))

    def f(v, dp=2):
        return "" if pd.isna(v) else f"{v:.{dp}f}"

    for _, r in view.head(args.top).iterrows():
        print(f"{str(r['groupid'])[:22]:22} {str(r['brand'])[:12]:12} "
              f"{int(r['clicks']):>5} {f(r['our_price']):>7} {f(r['bench']):>7} "
              f"{f(r['gap_pct'],1):>6} {f(r['shopifyprice']):>7} "
              f"{f(r['net_now_pct'],1):>6} {f(r['sugg_price']):>7} "
              f"{f(r['sugg_cut_pct'],1):>6} {str(r['best_eff']) if pd.notna(r['best_eff']) else '-':>6} "
              f"{str(r['season']) if pd.notna(r['season']) else '-':>7}")

    shown = min(len(view), args.top)
    print(f"\nShowing {shown} of {len(view)} groupids in this lens.")

    # --- Save full CSV ---
    cols = ["groupid", "brand", "season", "clicks", "sizes", "our_price",
            "bench", "gap_pct", "shopifyprice", "cost", "minshopifyprice",
            "maxshopifyprice", "rrp", "net_now_pct", "n_sugg", "sugg_price",
            "sugg_cut_pct", "best_eff", "n_high", "net_sugg_pct"]
    tag = os.path.basename(bench_path).replace(
        "Your most popular products with price benchmarks_", "").replace(".csv", "")
    out_path = os.path.join(HERE, f"portfolio_scan_{tag}.csv")
    out.sort_values("clicks", ascending=False)[cols].to_csv(out_path, index=False)
    print(f"Full table (all lenses) saved: {os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
