"""
SEO: organic revenue by landing page (GA4).

The page-level answer to "do intent-rich pages convert better?" -- the question
weekly.py's click counts cannot reach. For organic-search sessions only, this
shows where visitors land, whether they buy, and what a session is worth.

Fits the operating model: page first, then the number. Here the number is money,
not clicks -- but only because the visit was FREE. See seo/README.md for why free
clicks do not need to prove ROI; this just tells us which free pages to spend
effort on.

Caveats (seo/README.md): GA4 undercounts absolute revenue -- read the split and
the per-session RANK, not the pounds. "Organic Search" still folds in brand
searches the page did not earn.

USAGE:
• python organic_pages.py                (last 90 days, top 25)
• python organic_pages.py --days 28 --top 40
• python organic_pages.py --channel "Organic Shopping"
"""

import argparse
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")  # £ in a Windows console
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ga4_client import run_report

CHANNEL_DIM = "sessionDefaultChannelGroup"


def classify(path):
    if "/collections/" in path:
        return "collection"
    if "/products/" in path:
        return "product"
    if path.rstrip("/") in ("", "/"):
        return "home"
    if "/pages/" in path:
        return "info"
    if "/blogs/" in path:
        return "blog"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90, help="lookback window (default 90)")
    ap.add_argument("--top", type=int, default=25, help="rows (default 25)")
    ap.add_argument("--channel", default="Organic Search",
                    help='GA4 channel group (default "Organic Search")')
    args = ap.parse_args()

    rows = run_report(
        ["landingPage"],
        ["sessions", "ecommercePurchases", "totalRevenue"],
        f"{args.days}daysAgo", "yesterday",
        filter_dim=CHANNEL_DIM, filter_value=args.channel,
        order_metric="totalRevenue",
    )

    tot_s = sum(r["sessions"] for r in rows)
    tot_p = sum(r["ecommercePurchases"] for r in rows)
    tot_r = sum(r["totalRevenue"] for r in rows)

    print(f"\nORGANIC REVENUE BY PAGE - '{args.channel}' - last {args.days}d")
    print(f"{len(rows)} landing pages, {tot_s:,.0f} sessions, "
          f"{tot_p:,.0f} purchases, £{tot_r:,.0f} revenue "
          f"(conv {tot_p / tot_s * 100 if tot_s else 0:.2f}%, "
          f"£{tot_r / tot_s if tot_s else 0:.2f}/session)\n")
    print(f"  {'landing page':46} {'type':10} {'sess':>5} {'buys':>5} "
          f"{'conv%':>6} {'revenue':>9} {'£/sess':>7}")
    print("  " + "-" * 98)

    for r in rows[:args.top]:
        path = r["landingPage"] or "(not set)"
        s, p, rev = r["sessions"], r["ecommercePurchases"], r["totalRevenue"]
        conv = p / s * 100 if s else 0
        per = rev / s if s else 0
        print(f"  {path[:46]:46} {classify(path):10} {s:>5,.0f} {p:>5,.0f} "
              f"{conv:>5.1f}% {rev:>8,.0f} {per:>7.2f}")

    # Roll up by page type: the actual answer to "do intent-rich pages convert?"
    types = {}
    for r in rows:
        t = classify(r["landingPage"] or "")
        a = types.setdefault(t, [0, 0, 0.0])
        a[0] += r["sessions"]; a[1] += r["ecommercePurchases"]; a[2] += r["totalRevenue"]

    print("\n  BY TYPE - does intent convert?")
    print(f"  {'type':10} {'sess':>6} {'buys':>5} {'conv%':>6} {'revenue':>9} {'£/sess':>7}")
    for t in sorted(types, key=lambda t: -types[t][2]):
        s, p, rev = types[t]
        conv = p / s * 100 if s else 0
        per = rev / s if s else 0
        print(f"  {t:10} {s:>6,.0f} {p:>5,.0f} {conv:>5.1f}% {rev:>8,.0f} {per:>7.2f}")
    print()


if __name__ == "__main__":
    main()
