"""
SEO: the weekly report. Site -> type -> page, live from Search Console.

Target is clicks. Impressions and position are diagnostics: impressions say
whether we are shown at all, position whether we are shown anywhere anyone
looks, CTR whether being shown earned the click.

Stores nothing. GSC serves 16 months retroactively at any granularity, so any
past week is available on demand -- there is no window to miss and nothing to
snapshot. See README.md.

Windows differ by level on purpose. The site does ~230 clicks/week so 7d reads
cleanly; a single page does ~6 clicks/week, where 7d is pure noise. Page level
is 28d.

USAGE:
• python weekly.py
• python weekly.py --type collections    (drill into one type)
• python weekly.py --top 25              (rows per section)
"""

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from gsc_client import get_service, SITE_URL

GSC_LAG_DAYS = 3  # Search Console data is not complete for the last ~3 days
SITE_ROOT = SITE_URL.rstrip("/")


def classify(url):
    """Bucket a URL by page type. Order matters: /collections/ before the rest."""
    if "/collections/" in url:
        return "collections"
    if "/products/" in url:
        return "products"
    if url.rstrip("/") == SITE_ROOT:
        return "homepage"
    if "/pages/" in url:
        return "pages"
    if "/blogs/" in url:
        return "blogs"
    return "misc"


def query(service, start, end, dimensions=None):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "rowLimit": 25000,
    }
    if dimensions:
        body["dimensions"] = dimensions
    return service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute().get("rows", [])


def totals(rows):
    clicks = sum(r["clicks"] for r in rows)
    impr = sum(r["impressions"] for r in rows)
    # Position must be impression-weighted; a plain mean lets a page with 3
    # impressions at position 90 drag the whole site's number around.
    pos = sum(r["position"] * r["impressions"] for r in rows) / impr if impr else 0
    return clicks, impr, (clicks / impr * 100 if impr else 0), pos


def delta(now, prior):
    if not prior:
        return "  n/a"
    d = now - prior
    return f"{d:+5.0f}"


def pct_delta(now, prior):
    if not prior:
        return ""
    return f"({(now - prior) / prior * 100:+.0f}%)"


def short(url):
    u = url.replace(SITE_ROOT, "") or "/"
    return u[:52]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", help="drill into one type (collections/products/pages/blogs)")
    ap.add_argument("--top", type=int, default=15, help="rows per section (default 15)")
    args = ap.parse_args()

    service = get_service()
    end = datetime.date.today() - datetime.timedelta(days=GSC_LAG_DAYS)

    w1_start, w1_end = end - datetime.timedelta(days=6), end
    w0_start, w0_end = end - datetime.timedelta(days=13), end - datetime.timedelta(days=7)
    m1_start, m1_end = end - datetime.timedelta(days=27), end
    m0_start, m0_end = end - datetime.timedelta(days=55), end - datetime.timedelta(days=28)

    print(f"\nSEO WEEKLY - brookfieldcomfort.com - data to {end}\n")

    # ---- SITE: 7d vs prior 7d, 28d vs prior 28d ----
    print("=" * 74)
    print("SITE - target is clicks")
    print("=" * 74)
    print(f"  {'window':16} {'clicks':>7} {'chg':>7} {'impr':>9} {'CTR':>7} {'pos':>6}")
    periods = [
        ("last 7d", w1_start, w1_end),
        ("prior 7d", w0_start, w0_end),
        ("last 28d", m1_start, m1_end),
        ("prior 28d", m0_start, m0_end),
    ]
    site = {}
    for name, s, e in periods:
        site[name] = totals(query(service, s, e))
    for name, _, _ in periods:
        c, i, ctr, pos = site[name]
        prior = {"last 7d": "prior 7d", "last 28d": "prior 28d"}.get(name)
        d = delta(c, site[prior][0]) if prior else "     -"
        pd = pct_delta(c, site[prior][0]) if prior else ""
        print(f"  {name:16} {c:>7,.0f} {d:>7} {i:>9,.0f} {ctr:>6.2f}% {pos:>6.1f}  {pd}")

    # ---- BY TYPE: 28d vs prior 28d ----
    now_rows = query(service, m1_start, m1_end, ["page"])
    prior_rows = query(service, m0_start, m0_end, ["page"])

    def by_type(rows):
        out = {}
        for r in rows:
            out.setdefault(classify(r["keys"][0]), []).append(r)
        return out

    now_t, prior_t = by_type(now_rows), by_type(prior_rows)
    site_clicks = sum(r["clicks"] for r in now_rows)

    print()
    print("=" * 74)
    print("BY TYPE - 28d vs prior 28d")
    print("=" * 74)
    print(f"  {'type':12} {'pages':>6} {'clicks':>7} {'chg':>7} {'% site':>7} {'impr':>9} {'CTR':>7}")
    for t in sorted(now_t, key=lambda t: -sum(r["clicks"] for r in now_t[t])):
        c, i, ctr, _ = totals(now_t[t])
        pc = sum(r["clicks"] for r in prior_t.get(t, []))
        share = c / site_clicks * 100 if site_clicks else 0
        print(f"  {t:12} {len(now_t[t]):>6} {c:>7,.0f} {delta(c, pc):>7} "
              f"{share:>6.0f}% {i:>9,.0f} {ctr:>6.2f}%")

    # ---- PAGES ----
    types = [args.type] if args.type else ["collections", "pages", "products", "homepage", "blogs"]
    prior_by_url = {r["keys"][0]: r for r in prior_rows}

    for t in types:
        rows = now_t.get(t, [])
        if not rows:
            continue
        print()
        print("=" * 74)
        print(f"{t.upper()} - 28d, top {args.top} by clicks")
        print("=" * 74)
        print(f"  {'page':52} {'clicks':>6} {'chg':>6} {'impr':>8} {'CTR':>6} {'pos':>5}")
        for r in sorted(rows, key=lambda r: -r["clicks"])[:args.top]:
            p = prior_by_url.get(r["keys"][0])
            ctr = r["clicks"] / r["impressions"] * 100 if r["impressions"] else 0
            print(f"  {short(r['keys'][0]):52} {r['clicks']:>6,.0f} "
                  f"{delta(r['clicks'], p['clicks'] if p else 0):>6} "
                  f"{r['impressions']:>8,.0f} {ctr:>5.2f}% {r['position']:>5.1f}")

    # Biggest untapped: lots of impressions, nobody clicking.
    print()
    print("=" * 74)
    print("MOST IMPRESSIONS, WORST CTR - 28d, shown but not clicked")
    print("=" * 74)
    print(f"  {'page':52} {'clicks':>6} {'impr':>8} {'CTR':>6} {'pos':>5}")
    candidates = [r for r in now_rows if r["impressions"] >= 500]
    for r in sorted(candidates, key=lambda r: r["clicks"] / r["impressions"])[:args.top]:
        ctr = r["clicks"] / r["impressions"] * 100
        print(f"  {short(r['keys'][0]):52} {r['clicks']:>6,.0f} {r['impressions']:>8,.0f} "
              f"{ctr:>5.2f}% {r['position']:>5.1f}")
    print()


if __name__ == "__main__":
    main()
