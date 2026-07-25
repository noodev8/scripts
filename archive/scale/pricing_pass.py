"""Shopify pricing pass — disposition table for one segment.

Assigns EVERY groupid in the segment exactly one disposition against its stored
Proven Price anchor (scale/proven_prices.md), using a deterministic first-match
rule. Nothing is skipped: the classifier is total, which is the no-miss guarantee.
See scale/PRICING_PROCESS.md.

Usage:  python scale/pricing_pass.py [SEGMENT]   (default EVA-SEG)

Rule (top-to-bottom, first match wins):
  1. sellable stock = 0                                  -> WAIT-nostock
  2. stock landed <= FAIR_RUN_DAYS and u10 < RAISE_MIN_U -> WAIT-new  (fresh AND quiet)
  3. price changed <= RECENT_CHANGE_DAYS                 -> HOLD-recent
  4. stock>0 and u90=0 and not on reorder                -> CULL
  5. stock>0 and u10=0 and price > anchor                -> CUT
  6. u10 >= RAISE_MIN_U and price <= anchor              -> RAISE
  7. otherwise                                           -> HOLD-steady
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

# ---- tunable windows (see PRICING_PROCESS.md "Open threads") ----
FAIR_RUN_DAYS      = 15   # WAIT-new: stock this fresh has had no fair run
RECENT_CHANGE_DAYS = 10   # HOLD-recent: a price this fresh was already decided
PRIO_WINDOW_DAYS   = 10   # demand signal used to prioritise + trigger RAISE
DEAD_DAYS          = 90   # CULL: no sale in this long = dead
RAISE_MIN_U        = 3    # RAISE: min units in the prio window to probe up  [SOFT]
ANCHOR_TOL         = 0.50 # pennies band that still counts as "at anchor"

SEG = sys.argv[1] if len(sys.argv) > 1 else 'EVA-SEG'
TODAY = date.today()
ANCHOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proven_prices.md')


def load_anchors():
    """Parse the anchor store MD table -> {groupid: anchor_float}."""
    anchors = {}
    with open(ANCHOR_FILE, encoding='utf-8') as f:
        for line in f:
            if not line.lstrip().startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 2:
                continue
            gid = cells[0]
            if '-' not in gid or gid.lower() == 'groupid':
                continue
            try:
                anchors[gid] = float(cells[1])
            except ValueError:
                continue
    return anchors


anchors = load_anchors()

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute("""
    WITH seg AS (
        SELECT groupid, colour, width, shopifyprice
        FROM skusummary WHERE segment = %s
    ),
    instock AS (
        SELECT sm.groupid, COALESCE(SUM(ls.qty),0)::int AS units
        FROM skumap sm
        JOIN seg ON seg.groupid = sm.groupid
        LEFT JOIN localstock ls
          ON ls.code = sm.code AND ls.ordernum='#FREE' AND ls.deleted=0
        WHERE sm.deleted = 0
        GROUP BY sm.groupid
    ),
    s_prio AS (
        SELECT groupid, SUM(qty)::int AS u
        FROM sales WHERE qty>0 AND soldprice>0 AND solddate::date >= %s
        GROUP BY groupid
    ),
    s_dead AS (
        SELECT groupid, SUM(qty)::int AS u
        FROM sales WHERE qty>0 AND soldprice>0 AND solddate::date >= %s
        GROUP BY groupid
    ),
    lastchg AS (
        SELECT groupid, MAX(change_date)::date AS d
        FROM price_change_log GROUP BY groupid
    ),
    landed AS (
        SELECT groupid, MAX(arrival_date)::date AS d
        FROM incoming_stock GROUP BY groupid
    ),
    reorder AS (
        SELECT SUBSTRING(code FROM '^[^-]+-[^-]+') AS groupid,
               SUM(GREATEST(requested - arrived, 0))::int AS pending
        FROM birktracker
        WHERE requested > arrived AND placedate IS NOT NULL
        GROUP BY 1
    )
    SELECT seg.groupid, seg.colour, seg.width, seg.shopifyprice,
           COALESCE(i.units,0)   AS stock,
           COALESCE(sp.u,0)      AS u_prio,
           COALESCE(sd.u,0)      AS u_dead,
           lc.d                  AS last_chg,
           ld.d                  AS landed,
           COALESCE(ro.pending,0) AS pending
    FROM seg
    LEFT JOIN instock i  ON i.groupid  = seg.groupid
    LEFT JOIN s_prio sp  ON sp.groupid = seg.groupid
    LEFT JOIN s_dead sd  ON sd.groupid = seg.groupid
    LEFT JOIN lastchg lc ON lc.groupid = seg.groupid
    LEFT JOIN landed ld  ON ld.groupid = seg.groupid
    LEFT JOIN reorder ro ON ro.groupid = seg.groupid
""", (SEG,
      TODAY - timedelta(days=PRIO_WINDOW_DAYS),
      TODAY - timedelta(days=DEAD_DAYS)))
rows = cur.fetchall()
conn.close()


def classify(price, anchor, stock, u_prio, u_dead, last_chg, landed, pending):
    days_since_chg = (TODAY - last_chg).days if last_chg else None
    days_since_landed = (TODAY - landed).days if landed else None
    above_anchor = anchor is not None and price > anchor + ANCHOR_TOL
    at_or_below  = anchor is not None and price <= anchor + ANCHOR_TOL

    if stock <= 0:
        return 'WAIT-nostock'
    if (days_since_landed is not None and days_since_landed <= FAIR_RUN_DAYS
            and u_prio < RAISE_MIN_U):
        return 'WAIT-new'  # fresh AND not yet selling = no fair read; hot fresh flows on
    if days_since_chg is not None and days_since_chg <= RECENT_CHANGE_DAYS:
        return 'HOLD-recent'
    if u_dead == 0 and pending == 0:
        return 'CULL'
    if u_prio == 0 and above_anchor:
        return 'CUT'
    if u_prio >= RAISE_MIN_U and at_or_below:
        return 'RAISE'
    return 'HOLD-steady'


items = []
for gid, col, wid, px, stock, u_prio, u_dead, last_chg, landed, pending in rows:
    try:
        price = float(px) if px not in (None, '') else 0.0
    except (TypeError, ValueError):
        price = 0.0
    anchor = anchors.get(gid)
    disp = classify(price, anchor, stock, u_prio, u_dead, last_chg, landed, pending)
    stake = round(u_prio * price)
    label = f"{(col or '-')}/{(wid or '-')[:3]}"
    days_chg = (TODAY - last_chg).days if last_chg else None
    items.append(dict(gid=gid, label=label, price=price, anchor=anchor, stock=stock,
                      u_prio=u_prio, u_dead=u_dead, days_chg=days_chg,
                      pending=pending, disp=disp, stake=stake))

ACTION = ['RAISE', 'CUT']
NONACTION = ['HOLD-steady', 'HOLD-recent', 'WAIT-new', 'WAIT-nostock', 'CULL']


def print_row(it):
    a = f"{it['anchor']:.0f}" if it['anchor'] is not None else '-'
    dc = str(it['days_chg']) if it['days_chg'] is not None else '-'
    pend = str(it['pending']) if it['pending'] else '-'
    print(f"  {it['gid']:<17} {it['label']:<16} {it['price']:>6.2f} {a:>5} "
          f"{it['stock']:>5} {it['u_prio']:>4} {it['u_dead']:>4} {dc:>5} {pend:>4} "
          f"{it['stake']:>5}  {it['disp']}")


hdr = (f"  {'groupid':<17} {'colour/fit':<16} {'price':>6} {'anch':>5} "
       f"{'stk':>5} {'u10':>4} {'u90':>4} {'chgd':>5} {'inc':>4} {'stake':>5}  disposition")

print(f"=== {SEG} pricing pass  ({TODAY}) ===")
print(f"windows: prio/RAISE={PRIO_WINDOW_DAYS}d (min {RAISE_MIN_U}u)  "
      f"fair-run={FAIR_RUN_DAYS}d  recent-change={RECENT_CHANGE_DAYS}d  dead={DEAD_DAYS}d\n")

# ---- action rows first, by stake desc ----
actions = sorted([i for i in items if i['disp'] in ACTION],
                 key=lambda x: -x['stake'])
print(f"ACTION  ({len(actions)})  -- the work, biggest stake first")
print(hdr)
for it in actions:
    print_row(it)

# ---- non-action, grouped by code, for the mislabel scan ----
print(f"\nSCAN  ({len(items)-len(actions)})  -- eyeball each bucket, challenge a wrong label")
for code in NONACTION:
    bucket = [i for i in items if i['disp'] == code]
    if not bucket:
        continue
    print(f"\n  [{code}]  {len(bucket)}")
    for it in sorted(bucket, key=lambda x: -x['stake']):
        print_row(it)

# ---- tally ----
print("\n--- tally ---")
for code in ACTION + NONACTION:
    n = len([i for i in items if i['disp'] == code])
    if n:
        print(f"  {code:<13} {n}")
print(f"  {'TOTAL':<13} {len(items)}")
