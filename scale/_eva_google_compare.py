"""Compare EVA-SEG prices vs Google's sale-price suggestions."""
import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config
from collections import defaultdict

CSV = r"C:\Users\aandr\Downloads\Sale price suggestions with highest performance impact_2026-05-20_13-39-04.csv"
TODAY = date(2026, 5, 20)
d30 = TODAY - timedelta(days=30)
d90 = TODAY - timedelta(days=90)

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()

# All EVA-SEG codes
cur.execute("""
    SELECT sm.code, sm.groupid, ss.colour, ss.width
    FROM skumap sm
    JOIN skusummary ss ON ss.groupid = sm.groupid
    WHERE ss.segment='EVA-SEG' AND sm.deleted=0
""")
eva_codes = {r[0]: (r[1], r[2], r[3]) for r in cur.fetchall()}

# Load Google CSV — skip 2 header lines
google = {}
with open(CSV, encoding='utf-8') as f:
    f.readline()  # title
    reader = csv.DictReader(f)
    for row in reader:
        pid = row['Product ID']
        if pid in eva_codes:
            google[pid] = {
                'your': float(row['Your price']),
                'sugg': float(row['Suggested price']),
                'effect': row['Effectiveness'],
                'click_uplift': float(row['Click uplift']),
                'conv_uplift': float(row['Conversion uplift']),
            }

print(f"Google CSV has {sum(1 for _ in open(CSV))-2} suggestions total; {len(google)} match EVA-SEG codes.\n")

# Per-groupid rollup of Google suggestions
by_group = defaultdict(list)
for code, g in google.items():
    gid = eva_codes[code][0]
    by_group[gid].append((code, g))

# Per-groupid avg sold price last 30d and last 90d
def avg_sold(gid, since):
    cur.execute("""
        SELECT COALESCE(SUM(qty*soldprice),0)::numeric, COALESCE(SUM(qty),0)::int
        FROM sales WHERE groupid=%s AND qty>0 AND soldprice>0
          AND solddate::date >= %s
    """, (gid, since))
    rev, u = cur.fetchone()
    return (float(rev)/u if u else None, u)

# Current shopifyprice and groupid meta
cur.execute("""
    SELECT groupid, colour, width, shopifyprice
    FROM skusummary WHERE segment='EVA-SEG'
""")
meta = {r[0]: r for r in cur.fetchall()}

# Build rollup rows
rows_out = []
for gid, items in by_group.items():
    n_codes = len(items)
    yours = [g['your'] for _, g in items]
    suggs = [g['sugg'] for _, g in items]
    avg_your = sum(yours)/len(yours)
    avg_sugg = sum(suggs)/len(suggs)
    avg30, u30 = avg_sold(gid, d30)
    avg90, u90 = avg_sold(gid, d90)
    m = meta.get(gid, (gid,'?','?',0))
    try:
        listed = float(m[3]) if m[3] not in (None,'') else 0
    except (TypeError, ValueError):
        listed = 0
    cw = f"{m[1] or '-'} / {m[2] or '-'}"
    rows_out.append({
        'gid': gid, 'cw': cw, 'listed': listed,
        'n': n_codes, 'avg_your': avg_your, 'avg_sugg': avg_sugg,
        'gap_pct': (avg_your - avg_sugg)/avg_your*100,
        'avg30': avg30, 'u30': u30, 'avg90': avg90, 'u90': u90,
    })

# Also list EVA codes NOT in Google CSV
covered_gids = set(by_group.keys())
not_in_g = sorted(g for g in {eva_codes[c][0] for c in eva_codes} if g not in covered_gids)

# Print
print(f"=== EVA-SEG vs Google sale-price suggestions ({TODAY}) ===\n")
print(f"{'GroupID':<22} {'Colour/Width':<22} {'Listed':>7} {'YourAvg':>8} {'Goog':>7} {'Gap%':>6} {'Sold30':>7} {'u30':>4} {'Sold90':>7} {'u90':>4}")
print("-" * 110)
for r in sorted(rows_out, key=lambda x: -x['u30'] if x['u30'] else 0):
    a30 = f"£{r['avg30']:.0f}" if r['avg30'] else '   -  '
    a90 = f"£{r['avg90']:.0f}" if r['avg90'] else '   -  '
    print(f"{r['gid']:<22} {r['cw']:<22} £{r['listed']:>5.0f} £{r['avg_your']:>6.2f} £{r['avg_sugg']:>5.2f} {r['gap_pct']:>5.1f}% {a30:>7} {r['u30']:>4} {a90:>7} {r['u90']:>4}")

print(f"\n--- {len(not_in_g)} EVA groupids with NO Google suggestion (Google sees price as fine or not enough data) ---")
for gid in not_in_g:
    m = meta.get(gid, (gid,'?','?',0))
    try:
        listed = float(m[3]) if m[3] not in (None,'') else 0
    except (TypeError, ValueError):
        listed = 0
    a30, u30 = avg_sold(gid, d30)
    a30s = f"£{a30:.0f}" if a30 else '-'
    print(f"  {gid:<22} {m[1] or '-':<14} / {m[2] or '-':<10} listed £{listed:>4.0f}  30d:{u30}u {a30s}")

conn.close()
