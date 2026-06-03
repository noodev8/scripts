"""Birkenstock core-size availability gauge for Google Ads push/scale-back decisions.

One question: how many styles can the core customer actually buy? Across EVERY
Birkenstock style whose grid offers the women's core sizes (38/39/40) — no sales
filter — we count the styles that hold ALL THREE core sizes in FREE stock ("Full").
Full is the decision number: the breadth of core-complete product ad spend can ride.

LOCKED OUTPUT — one at-a-glance table, one row per day:

  | Date | Full | Styles | Full % |

  - Full    : styles with all 3 core sizes (38/39/40) in FREE stock. The number you
              act on — push capacity. Any qty counts (1+1+1 is Full).
  - Styles  : total in-range styles (Birk grids offering 38/39/40). The ceiling.
  - Full %  : Full / Styles. Progress toward a fully stocked range; read as trend.

Partials (1-2 of 3) are a hidden bonus, not tracked here. Run with --detail for the
per-size breakdown (what's blocking Full) and the weakest-first prune list.

Run with --velocity to attach sales velocity to the Full styles (units 30d/90d/365d,
units/day, weeks of cover) — the pricing focus list: which core-complete styles are
actually selling and which are dead weight on full grids. All-channel sales.
See birk-stock/README.md for the full design.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from collections import defaultdict
from datetime import date
from logging_utils import get_db_config

CORE_SIZES = (38, 39, 40)   # women's core; men's-only grids are out (no 38)
BRAND = 'Birkenstock'
VELOCITY_WINDOWS = (30, 90, 365)   # trailing-day sales windows for --velocity
SNAPSHOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots.md')

# Snapshot table columns — metrics only.
COLS = ['Date', 'Full', 'Styles', 'Full %']


def _split(text):
    """Return (preamble, rows) for the snapshot table.
    preamble is the text before the table; rows is a list of dicts keyed by COLS."""
    pre_lines, rows = [], []
    seen_table = False
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith('|'):
            seen_table = True
            cells = [c.strip() for c in s.strip('|').split('|')]
            if cells and (cells[0] == 'Date' or set(cells[0]) <= set('-: ')):
                continue  # header or separator row
            rows.append({COLS[i]: (cells[i] if i < len(cells) else '') for i in range(len(COLS))})
        elif not seen_table:
            pre_lines.append(ln)
    return '\n'.join(pre_lines).rstrip(), rows


def _render_md(rows):
    header = '| ' + ' | '.join(COLS) + ' |'
    sep = '|' + '|'.join('---' for _ in COLS) + '|'
    body = ['| ' + ' | '.join(r.get(c, '') for c in COLS) + ' |' for r in rows]
    return '\n'.join([header, sep] + body)


def _render_ascii(rows):
    """Aligned ASCII table for the console."""
    widths = {c: max(len(c), *(len(r.get(c, '')) for r in rows)) for c in COLS} if rows \
        else {c: len(c) for c in COLS}
    line = lambda vals: '  ' + ' | '.join(v.rjust(widths[c]) for c, v in zip(COLS, vals))
    out = [line(COLS), '  ' + '-+-'.join('-' * widths[c] for c in COLS)]
    out += [line([r.get(c, '') for c in COLS]) for r in rows]
    return '\n'.join(out)


def write_snapshot(today, full, n_styles):
    """Upsert today's row into the snapshots.md table (latest run of the day wins)."""
    full_pct = round(full / n_styles * 100) if n_styles else 0
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    preamble, rows = _split(text)

    existed = today in {r['Date'] for r in rows}
    by_date = {r['Date']: r for r in rows}
    by_date[today] = {'Date': today, 'Full': str(full),
                      'Styles': str(n_styles), 'Full %': f"{full_pct}%"}
    ordered = [by_date[d] for d in sorted(by_date)]

    out = preamble + '\n\n' + _render_md(ordered) + '\n'
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f"\n[snapshot {'updated' if existed else 'appended'}: {today}]")


def print_recent(n=7):
    """Print the last n daily rows as an aligned console table (trend at a glance)."""
    try:
        with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
            _, rows = _split(f.read())
    except FileNotFoundError:
        return
    print(_render_ascii(rows[-n:]))


def print_velocity(cur, full, qty, colour):
    """Attach sales velocity to the Full styles — the pricing focus list.

    For every core-complete (Full) style: trailing units sold over each
    VELOCITY_WINDOWS span, 90-day units/day, and weeks of cover (total FREE
    stock / weekly rate). All-channel sales. Sorted fastest-first so the styles
    worth pricing attention sit at the top and the dead weight sinks.
    """
    if not full:
        print("\nNo Full styles to report velocity for.")
        return

    # Total FREE stock (all sizes, not just core) — the cover denominator.
    cur.execute("""SELECT groupid, SUM(qty) FROM localstock
        WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0 AND groupid = ANY(%s)
        GROUP BY groupid""", (full,))
    freestock = {g: int(q) for g, q in cur.fetchall()}

    units = {}  # window -> {groupid: units}
    for days in VELOCITY_WINDOWS:
        cur.execute("""SELECT groupid, SUM(qty) FROM sales
            WHERE groupid = ANY(%s) AND solddate >= CURRENT_DATE - (%s || ' days')::interval
            GROUP BY groupid""", (full, days))
        units[days] = {g: int(q or 0) for g, q in cur.fetchall()}

    rows = []
    for g in full:
        core = sum(qty[g].get(s, 0) for s in CORE_SIZES)
        free = freestock.get(g, 0)
        wins = [units[d].get(g, 0) for d in VELOCITY_WINDOWS]
        vel = units[90].get(g, 0) / 90.0 if 90 in units else 0.0
        wks = (free / (vel * 7)) if vel > 0 else None
        rows.append((g, colour.get(g) or '-', core, free, wins, vel, wks))
    rows.sort(key=lambda r: -r[5])  # velocity desc

    win_hdr = ' '.join(f"{str(d)+'d':>5}" for d in VELOCITY_WINDOWS)
    hdr = (f"\n{'#':>3}  {'GroupID':<22} {'Colour':<8} {'core':>4} {'free':>4} "
           f"{win_hdr} {'u/day':>6} {'wks':>4}")
    print("\nSales velocity for the Full styles (all-channel) - pricing focus list:")
    print(hdr)
    print("  " + "-" * (len(hdr) - 3))
    for i, (g, col, core, free, wins, vel, wks) in enumerate(rows, 1):
        ws = 'inf' if wks is None else f"{wks:.0f}"
        cells = ' '.join(f"{w:>5}" for w in wins)
        print(f"{i:>3}  {g:<22} {col[:8]:<8} {core:>4} {free:>4} "
              f"{cells} {vel:>6.2f} {ws:>4}")
    print("\n  u/day = 90d units / 90.  wks = total FREE stock / weekly rate "
          "(inf = no 90d sales).")


def main(detail=False, velocity=False):
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()

    # Every qualifying style + its FREE stock at each core size, in one pass.
    #   - brand Birkenstock
    #   - grid (skumap) offers ALL core sizes  -> drops men's-only grids (no 38)
    # No sales filter: the denominator is the whole Birk core-size range.
    core_list = ','.join(str(s) for s in CORE_SIZES)
    cur.execute(f"""
        WITH birk AS (
            SELECT groupid, colour FROM skusummary WHERE brand = %s
        ),
        grid AS (
            SELECT sm.groupid
            FROM skumap sm
            JOIN birk b ON b.groupid = sm.groupid
            WHERE sm.deleted = 0 AND sm.code ~ '-[0-9]+$'
              AND (REGEXP_REPLACE(sm.code, '^.*-', ''))::int IN ({core_list})
            GROUP BY sm.groupid
            HAVING COUNT(DISTINCT (REGEXP_REPLACE(sm.code, '^.*-', ''))::int) = {len(CORE_SIZES)}
        ),
        corestock AS (
            SELECT ls.groupid,
                   (REGEXP_REPLACE(ls.code, '^.*-', ''))::int AS size,
                   SUM(ls.qty) AS qty
            FROM localstock ls
            JOIN birk b ON b.groupid = ls.groupid
            WHERE ls.ordernum = '#FREE' AND ls.deleted = 0 AND ls.qty > 0
              AND ls.code ~ '-[0-9]+$'
              AND (REGEXP_REPLACE(ls.code, '^.*-', ''))::int IN ({core_list})
            GROUP BY 1, 2
        )
        SELECT b.groupid, b.colour, cs.size, COALESCE(cs.qty, 0)
        FROM birk b
        JOIN grid g ON g.groupid = b.groupid
        LEFT JOIN corestock cs ON cs.groupid = b.groupid
        ORDER BY b.groupid
    """, (BRAND,))

    rows = cur.fetchall()

    qty = defaultdict(dict)
    colour = {}
    for gid, col, size, q in rows:
        colour[gid] = col
        qty.setdefault(gid, {})
        if size is not None:
            qty[gid][int(size)] = int(q)

    styles = sorted(qty)
    n = len(styles)

    # Sizes in stock per style; Full = all 3.
    in_stock = {gid: sum(1 for s in CORE_SIZES if qty[gid].get(s, 0) > 0) for gid in styles}
    full_styles = [gid for gid in styles if in_stock[gid] == len(CORE_SIZES)]
    full = len(full_styles)

    today = str(date.today())
    write_snapshot(today, full, n)

    print(f"=== Birkenstock core-size availability ===\n")
    print_recent()

    if detail:
        # What's blocking Full: per-size in-stock share.
        print("\nPer-size (what's blocking Full):")
        for s in CORE_SIZES:
            cnt = sum(1 for gid in styles if qty[gid].get(s, 0) > 0)
            print(f"  {s}: {cnt:>3}/{n} in stock ({round(cnt / n * 100) if n else 0:>3}%)")

        # Not-Full styles, weakest first — the prune/restock shortlist.
        gaps = sorted((g for g in styles if in_stock[g] < len(CORE_SIZES)),
                      key=lambda g: (in_stock[g], sum(qty[g].values()), g))
        hdr = (f"\n{'#':>3}  {'GroupID':<24} {'Colour':<16} "
               + ' '.join(f"{str(s):>3}" for s in CORE_SIZES) + f" {'InStk':>5}")
        print(hdr)
        print("  " + "-" * (len(hdr) - 3))
        for i, gid in enumerate(gaps, 1):
            cells = ' '.join(f"{qty[gid].get(s, 0):>3}" for s in CORE_SIZES)
            col = (colour.get(gid) or '-')[:16]
            print(f"{i:>3}  {gid:<24} {col:<16} {cells}  {in_stock[gid]}/3")

    if velocity:
        print_velocity(cur, full_styles, qty, colour)

    conn.close()

    if not velocity:
        print("\n(run with --velocity for per-style sales velocity — the pricing focus list)")


if __name__ == '__main__':
    main(detail='--detail' in sys.argv, velocity='--velocity' in sys.argv)
