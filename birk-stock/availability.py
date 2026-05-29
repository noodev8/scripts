"""Birkenstock stock-availability snapshot for Google Ads push/scale-back decisions.

See birk-stock/README.md for the full design.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from collections import defaultdict
from datetime import date
from logging_utils import get_db_config
from size_weights import WOMENS, MENS, curve_for

DEMAND_WINDOW_DAYS = 28
MOMENTUM_WINDOW_DAYS = 7
CHANNEL = 'SHP'
BRAND = 'Birkenstock'
TOP_N = 25
SNAPSHOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots.md')


def _pace_word(daily_recent, daily_28d):
    if daily_28d <= 0:
        return 'flat'
    r = daily_recent / daily_28d
    return 'accelerating' if r >= 1.25 else ('slowing' if r <= 0.75 else 'steady')


def write_snapshot(headline, total_u28, total_u7, counts, drags, headline_lenient, colour):
    """Append today's metrics block to snapshots.md, or overwrite an existing
    same-day block (one entry per day, latest run wins). Metrics only —
    judgment/context lines are not auto-written."""
    today = str(date.today())
    d28 = total_u28 / DEMAND_WINDOW_DAYS
    d7 = total_u7 / MOMENTUM_WINDOW_DAYS
    pace = _pace_word(d7, d28)

    def pct(b):
        return round(counts[b][0] / total_u28 * 100) if total_u28 else 0

    drag_parts = []
    for gid, u28, avail, lost in drags[:5]:
        style = gid.split('-', 1)[1].title() if '-' in gid else gid
        code = gid.split('-', 1)[0]
        col = colour.get(gid) or '-'
        drag_parts.append(f"{col} {style} {code} ({lost:.1f})")

    block = (
        f"## {today}\n\n"
        f"- **Headline:** {headline:.1f}%\n"
        f"- **READY-share of demand:** {pct('READY')}% ({counts['READY'][0]}u / {total_u28}u)\n"
        f"- **Status breakdown:** READY {pct('READY')}% / PARTIAL {pct('PARTIAL')}% / "
        f"THIN {pct('THIN')}% (by {DEMAND_WINDOW_DAYS}d units)\n"
        f"- **Volume:** {DEMAND_WINDOW_DAYS}d {total_u28}u (~{round(d28)}/d) -> "
        f"{MOMENTUM_WINDOW_DAYS}d {total_u7}u (~{round(d7)}/d) -> {pace}\n"
        f"- **Top 5 drags:** " + ", ".join(drag_parts) + "\n"
        f"- **Sensitivity (qty=1 full credit):** {headline_lenient:.1f}%"
    ).strip()

    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    idx = text.find('\n## ')
    if idx == -1:
        preamble = text.rstrip()
        blocks = []
    else:
        preamble = text[:idx].rstrip()
        blocks = ['## ' + b.strip() for b in text[idx:].split('\n## ') if b.strip()]

    replaced = False
    for i, b in enumerate(blocks):
        if b.startswith(f"## {today}"):
            blocks[i] = block
            replaced = True
            break
    if not replaced:
        blocks.append(block)

    out = preamble + '\n\n' + '\n\n'.join(blocks) + '\n'
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        f.write(out)

    print(f"\n[snapshot {'updated' if replaced else 'appended'}: {today}]")


def qty_credit(qty):
    if qty >= 2:
        return 1.0
    if qty == 1:
        return 0.5
    return 0.0


def main():
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()

    # Per (groupid, size): size universe (from skumap), FREE stock qty, 28d Shopify units
    cur.execute("""
        WITH birk AS (
            SELECT groupid, colour FROM skusummary WHERE brand = %s
        ),
        universe AS (
            SELECT sm.groupid,
                   (REGEXP_REPLACE(sm.code, '^.*-', ''))::int AS size
            FROM skumap sm
            JOIN birk b ON b.groupid = sm.groupid
            WHERE sm.deleted = 0 AND sm.code ~ '-[0-9]+$'
        ),
        stock AS (
            SELECT ls.groupid,
                   (REGEXP_REPLACE(ls.code, '^.*-', ''))::int AS size,
                   SUM(ls.qty) AS qty
            FROM localstock ls
            JOIN birk b ON b.groupid = ls.groupid
            WHERE ls.ordernum = '#FREE' AND ls.deleted = 0 AND ls.qty > 0
              AND ls.code ~ '-[0-9]+$'
            GROUP BY 1, 2
        ),
        s28 AS (
            SELECT s.groupid,
                   (REGEXP_REPLACE(s.code, '^.*-', ''))::int AS size,
                   SUM(s.qty) AS units
            FROM sales s
            JOIN birk b ON b.groupid = s.groupid
            WHERE s.channel = %s AND s.qty > 0
              AND s.solddate::date >= CURRENT_DATE - %s
              AND s.code ~ '-[0-9]+$'
            GROUP BY 1, 2
        )
        SELECT b.groupid, b.colour, u.size,
               COALESCE(st.qty, 0) AS stock_qty,
               COALESCE(s28.units, 0) AS units_28d
        FROM birk b
        JOIN universe u ON u.groupid = b.groupid
        LEFT JOIN stock st ON st.groupid = b.groupid AND st.size = u.size
        LEFT JOIN s28 ON s28.groupid = b.groupid AND s28.size = u.size
    """, (BRAND, CHANNEL, DEMAND_WINDOW_DAYS))

    rows = cur.fetchall()

    # Per-groupid 28d & 7d totals (independent: catches sales whose size isn't in current universe)
    cur.execute("""
        SELECT s.groupid,
               SUM(s.qty) AS u28,
               SUM(CASE WHEN s.solddate::date >= CURRENT_DATE - %s THEN s.qty ELSE 0 END) AS u7
        FROM sales s
        JOIN skusummary ss ON ss.groupid = s.groupid
        WHERE ss.brand = %s AND s.channel = %s AND s.qty > 0
          AND s.solddate::date >= CURRENT_DATE - %s
        GROUP BY 1
    """, (MOMENTUM_WINDOW_DAYS, BRAND, CHANNEL, DEMAND_WINDOW_DAYS))

    totals = {gid: (int(u28), int(u7)) for gid, u28, u7 in cur.fetchall()}

    conn.close()

    # Build per-groupid structures from the wide query
    universe = defaultdict(set)
    stock = defaultdict(dict)
    colour = {}

    for gid, col, size, stock_qty, _u28 in rows:
        universe[gid].add(size)
        if stock_qty > 0:
            stock[gid][size] = int(stock_qty)
        colour[gid] = col

    # Score each style: sum(curve_weight * qty_credit) over in-curve sizes
    score = {}
    for gid, sizes in universe.items():
        curve = curve_for(sizes)
        s = 0.0
        for sz, w in curve.items():
            s += w * qty_credit(stock[gid].get(sz, 0))
        score[gid] = s

    # Brand headline: demand-weighted by 28d units
    total_u28 = sum(t[0] for t in totals.values())
    total_u7 = sum(t[1] for t in totals.values())
    weighted = sum(totals[gid][0] * score.get(gid, 0.0) for gid in totals)
    headline = (weighted / total_u28 * 100.0) if total_u28 else 0.0

    # Curve split for context
    w_styles = sum(1 for gid in universe if curve_for(universe[gid]) is WOMENS)
    m_styles = sum(1 for gid in universe if curve_for(universe[gid]) is MENS)

    # Output
    print(f"=== Birkenstock stock availability  ({date.today()}) ===\n")
    print(f"Headline: {headline:.1f}%  (demand-weighted, units, last {DEMAND_WINDOW_DAYS}d)")
    print(f"Shopify units  last {DEMAND_WINDOW_DAYS}d: {total_u28:>4}   last {MOMENTUM_WINDOW_DAYS}d: {total_u7:>3}")
    print(f"Groupids:      {len(universe)} total  ({w_styles} women's-curve, {m_styles} men's-curve)\n")

    top = sorted(totals.items(), key=lambda kv: kv[1][0], reverse=True)[:TOP_N]
    print(f"Top {len(top)} groupids by {DEMAND_WINDOW_DAYS}d units:")
    header = f"{'#':>2}  {'GroupID':<24} {'Colour':<16} {'C':<2} {'Avail':>6} {'u28':>4} {'u7':>3} {'pace':>5}  Status"
    print(header)
    print("-" * len(header))
    for i, (gid, (u28, u7)) in enumerate(top, 1):
        curve_obj = curve_for(universe.get(gid, set()))
        c = 'W' if curve_obj is WOMENS else 'M'
        avail = score.get(gid, 0.0) * 100.0
        if u28 < 4:
            pace = '.'
        else:
            ratio = u7 / (u28 / 4.0)
            pace = 'up' if ratio >= 1.25 else ('down' if ratio <= 0.75 else 'flat')
        status = 'READY' if avail >= 70 else ('PARTIAL' if avail >= 40 else 'THIN')
        col = (colour.get(gid) or '-')[:16]
        print(f"{i:>2}  {gid:<24} {col:<16} {c:<2} {avail:>5.0f}% {u28:>4} {u7:>3} {pace:>5}  {status}")

    # Demand-weighted status breakdown (selling groupids only)
    def bucket(s): return 'READY' if s >= 70 else ('PARTIAL' if s >= 40 else 'THIN')
    counts = defaultdict(lambda: [0, 0])  # bucket -> [units, groupids]
    for gid, (u28, _) in totals.items():
        b = bucket(score.get(gid, 0.0) * 100.0)
        counts[b][0] += u28
        counts[b][1] += 1
    print(f"\nDemand by status (last {DEMAND_WINDOW_DAYS}d, selling groupids only):")
    for b in ('READY', 'PARTIAL', 'THIN'):
        u, n = counts[b]
        pct = (u / total_u28 * 100) if total_u28 else 0
        print(f"  {b:<8}: {u:>4}u ({pct:>4.0f}%)  on {n:>3} groupids")

    # Biggest drags: u28 * (1 - score) = expected lost units
    drags = sorted(
        ((gid, u28, score.get(gid, 0.0) * 100, u28 * (1 - score.get(gid, 0.0)))
         for gid, (u28, _) in totals.items()),
        key=lambda x: x[3], reverse=True
    )[:10]
    print(f"\nTop 10 biggest drags (lost demand units = u28 * (1 - avail)):")
    print(f"{'#':>2}  {'GroupID':<24} {'Colour':<16} {'Avail':>6} {'u28':>4} {'lost':>5}")
    for i, (gid, u28, avail, lost) in enumerate(drags, 1):
        col = (colour.get(gid) or '-')[:16]
        print(f"{i:>2}  {gid:<24} {col:<16} {avail:>5.0f}% {u28:>4} {lost:>5.1f}")

    # Sensitivity: qty=1 -> full credit (vs. default half)
    lenient = {}
    for gid, sizes in universe.items():
        curve = curve_for(sizes)
        lenient[gid] = sum(
            w * (1.0 if stock[gid].get(sz, 0) >= 1 else 0.0)
            for sz, w in curve.items()
        )
    headline_lenient = (
        sum(totals[gid][0] * lenient.get(gid, 0.0) for gid in totals) / total_u28 * 100
        if total_u28 else 0
    )
    print(f"\nSensitivity (qty=1 as full credit, not half): headline -> {headline_lenient:.1f}%")

    write_snapshot(headline, total_u28, total_u7, counts, drags, headline_lenient, colour)


if __name__ == '__main__':
    main()
