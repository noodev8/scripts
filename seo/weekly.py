"""
SEO: the progress report. Organic vs paid, then site -> type -> page.

Target is clicks, measured against paid. Impressions and position are
diagnostics: impressions say whether we are shown at all, position whether we
are shown anywhere anyone looks, CTR whether being shown earned the click.

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
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from gsc_client import get_service, SITE_URL

GSC_LAG_DAYS = 3  # Search Console data is not complete for the last ~3 days
SITE_ROOT = SITE_URL.rstrip("/")

# CTR-vs-position curve. Bands are narrow low down (where CTR moves fast) and
# wide further out (where it is flat and pages are few). MIN_IMPR keeps pages
# with a handful of impressions from setting a band's median on noise.
BANDS = [(1, 3), (3, 5), (5, 7), (7, 9), (9, 11), (11, 14), (14, 20), (20, 100)]
MIN_IMPR = 250


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


def band_of(position):
    for lo, hi in BANDS:
        if lo <= position < hi:
            return f"{lo}-{hi}"
    return None


def short(url, width=52):
    u = url.replace(SITE_ROOT, "") or "/"
    return u[:width]


def paid(start, end):
    """Paid clicks for a date range, plus how many days of the range have data.

    google_campaign_daily is a manual CSV import and lags GSC, so a window can be
    partly empty. The day count lets the caller mark the number partial rather
    than show missing days as a fall in paid traffic.
    """
    import psycopg2
    from logging_utils import get_db_config

    with psycopg2.connect(**get_db_config()) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(clicks), 0), COUNT(DISTINCT snapshot_date)
            FROM google_campaign_daily
            WHERE snapshot_date BETWEEN %s AND %s
            """,
            (start, end),
        )
        return cur.fetchone()


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

    print(f"\nSEO PROGRESS - brookfieldcomfort.com - data to {end}\n")

    # ---- SITE: 7d vs prior 7d, 28d vs prior 28d ----
    print("=" * 74)
    print("ORGANIC - target is clicks")
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

    # ---- PAID: outline only ----
    # Deliberately thin. Paid is campaign-level (one campaign is ~96% of clicks)
    # so it cannot be joined to organic at page or query level -- totals is the
    # only honest comparison available, and share is context, not a target: the
    # denominator is ad budget, so share falls when spend rises even if SEO won.
    print()
    print("=" * 74)
    print("VS PAID - context, not a target (share falls when ad spend rises)")
    print("=" * 74)
    try:
        for name in ("last 28d", "prior 28d"):
            s, e = [(s, e) for n, s, e in periods if n == name][0]
            p, days, = paid(s, e)
            org = site[name][0]
            share = org / (org + p) * 100 if org + p else 0
            partial = "  (paid partial)" if days < 28 else ""
            print(f"  {name:12} organic {org:>6,.0f}   paid {p:>7,.0f}   "
                  f"organic {share:>4.0f}%{partial}")
    except Exception as e:
        print(f"  Paid data unavailable ({e}). Refresh via google-ads/how-to-run.md.")

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

    # ---- WINNERS: the pages carrying the site, across every type ----
    # Split by type this is invisible: the size guide out-earns nearly every
    # collection, but sits in a different section. Cumulative % is here because
    # the concentration is the story -- a handful of URLs are the whole site.
    prior_by_url = {r["keys"][0]: r for r in prior_rows}
    pool = now_t.get(args.type, []) if args.type else now_rows
    label = f"{args.type.upper()} " if args.type else ""

    print()
    print("=" * 74)
    print(f"{label}WINNERS - top {args.top} pages by clicks, 28d")
    print("=" * 74)
    print(f"  {'#':>2} {'page':44} {'type':11} {'clicks':>6} {'chg':>6} "
          f"{'impr':>8} {'CTR':>6} {'pos':>5} {'cum':>5}")
    running = 0
    pool_clicks = sum(r["clicks"] for r in pool)
    for n, r in enumerate(sorted(pool, key=lambda r: -r["clicks"])[:args.top], 1):
        p = prior_by_url.get(r["keys"][0])
        ctr = r["clicks"] / r["impressions"] * 100 if r["impressions"] else 0
        running += r["clicks"]
        cum = running / pool_clicks * 100 if pool_clicks else 0
        print(f"  {n:>2} {short(r['keys'][0], 44):44} {classify(r['keys'][0]):11} "
              f"{r['clicks']:>6,.0f} {delta(r['clicks'], p['clicks'] if p else 0):>6} "
              f"{r['impressions']:>8,.0f} {ctr:>5.2f}% {r['position']:>5.1f} {cum:>4.0f}%")

    # ---- CTR VS POSITION: what a slot is worth, and who is short of it ----
    # Ranking pages by raw CTR is a trap: it just re-discovers that low-ranked
    # pages convert badly, and puts the size guide top as if a title rewrite
    # would fix a page that is already exactly where its rank says it should be.
    # Scoring each page against its OWN band's median separates "ranks badly"
    # from "ranks fine, earns badly" -- only the second is a title/snippet job.
    curve = {}
    for r in now_rows:
        if r["impressions"] < MIN_IMPR:
            continue
        band = band_of(r["position"])
        if band:
            curve.setdefault(band, []).append(r["clicks"] / r["impressions"] * 100)

    print()
    print("=" * 74)
    print(f"CTR VS POSITION - 28d, pages >= {MIN_IMPR} impressions")
    print("=" * 74)
    print(f"  {'position':10} {'pages':>6} {'median CTR':>11}")
    for lo, hi in BANDS:
        band = f"{lo}-{hi}"
        if band in curve:
            n = len(curve[band])
            thin = "   (thin - treat as noise)" if n < 4 else ""
            print(f"  {band:10} {n:>6} {statistics.median(curve[band]):>10.2f}%{thin}")

    # Below their own band = the whole realistic title/meta opportunity. The
    # total is printed because it is the point: if it is small, the CTR play is
    # not a plan and the work is ranking or new pages instead.
    pool = now_t.get(args.type, []) if args.type else now_rows
    short_of = []
    for r in pool:
        if r["impressions"] < MIN_IMPR:
            continue
        band = band_of(r["position"])
        if not band or band not in curve:
            continue
        ctr, med = r["clicks"] / r["impressions"] * 100, statistics.median(curve[band])
        if ctr < med:
            short_of.append((r, ctr, med, (med - ctr) / 100 * r["impressions"]))

    print()
    print("=" * 74)
    print(f"{label}BELOW CURVE - ranks fine, earns badly. The title/meta job.")
    print("=" * 74)
    print(f"  {'page':44} {'impr':>7} {'CTR':>6} {'med':>6} {'pos':>5} {'gap':>6}")
    for r, ctr, med, gap in sorted(short_of, key=lambda x: -x[3])[:args.top]:
        print(f"  {short(r['keys'][0], 44):44} {r['impressions']:>7,.0f} {ctr:>5.2f}% "
              f"{med:>5.2f}% {r['position']:>5.1f} {gap:>+6.0f}")
    total = sum(g for _, _, _, g in short_of)
    base = sum(r["clicks"] for r in pool)
    print(f"\n  Whole opportunity: {total:+,.0f} clicks/28d if every gap closed to "
          f"median ({total / base * 100:+.0f}% on {base:,.0f}).")
    print("  Curve is site-wide for sample size; the list above respects --type.\n")


if __name__ == "__main__":
    main()
