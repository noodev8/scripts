"""Birkenstock core-size availability gauge for Google Ads push/scale-back decisions.

One question: can the core customer buy? Across EVERY Birkenstock style whose grid
offers the women's core sizes (38/39/40) — no sales filter — we score each style on
whether it actually holds those sizes, credited gently by stock depth. Target 100%;
thin stragglers drag it down and are the owner's to prune.

LOCKED OUTPUT — one at-a-glance table, one row per day:

  | Date | 38 | 39 | 40 | Overall | Styles | Full | Partial | Empty |

  - 38 / 39 / 40 : % of in-range styles with that size in FREE stock.
  - Overall      : depth-weighted core coverage (the headline; target 100%).
                   Per slot: qty 0->0, 1->0.5, 2->0.8, 3+->1.0; per style = mean of
                   its 3 core slots; Overall = mean across all styles.
  - Full / Partial / Empty : styles by how many core sizes are in stock (3 / 1-2 / 0).

Run with --detail to also print the weakest-first per-style grid (the prune list).
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
SNAPSHOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots.md')

# Snapshot table columns — metrics only.
COLS = ['Date', '38', '39', '40', 'Overall', 'Styles', 'Full', 'Partial', 'Empty']


def depth_credit(qty):
    """Gentle depth tiers: a single unit empties on the next sale (half credit);
    3+ means we can push into the size (full credit)."""
    if qty >= 3:
        return 1.0
    if qty == 2:
        return 0.8
    if qty == 1:
        return 0.5
    return 0.0


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


def write_snapshot(today, pct, overall, n_styles, full, partial, empty):
    """Upsert today's row into the snapshots.md table (latest run of the day wins)."""
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    preamble, rows = _split(text)

    existed = today in {r['Date'] for r in rows}
    by_date = {r['Date']: r for r in rows}
    by_date[today] = {
        'Date': today,
        '38': f"{pct[38]}%", '39': f"{pct[39]}%", '40': f"{pct[40]}%",
        'Overall': f"{round(overall)}%", 'Styles': str(n_styles),
        'Full': str(full), 'Partial': str(partial), 'Empty': str(empty),
    }
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


def main(detail=False):
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
    conn.close()

    qty = defaultdict(dict)
    colour = {}
    for gid, col, size, q in rows:
        colour[gid] = col
        qty.setdefault(gid, {})
        if size is not None:
            qty[gid][int(size)] = int(q)

    styles = sorted(qty)
    n = len(styles)

    # Per-style core credit; Overall = mean across styles.
    credit = {gid: sum(depth_credit(qty[gid].get(s, 0)) for s in CORE_SIZES) / len(CORE_SIZES)
              for gid in styles}
    overall = (sum(credit.values()) / n * 100.0) if n else 0.0

    # Per-size in-stock share.
    pct = {}
    for s in CORE_SIZES:
        in_stock = sum(1 for gid in styles if qty[gid].get(s, 0) > 0)
        pct[s] = round(in_stock / n * 100) if n else 0

    # Completeness bands: styles by # of core sizes in stock.
    full = partial = empty = 0
    for gid in styles:
        c = sum(1 for s in CORE_SIZES if qty[gid].get(s, 0) > 0)
        if c == len(CORE_SIZES):
            full += 1
        elif c == 0:
            empty += 1
        else:
            partial += 1

    today = str(date.today())
    write_snapshot(today, pct, overall, n, full, partial, empty)

    print(f"=== Birkenstock core-size availability ===\n")
    print_recent()

    if detail:
        # Weakest coverage first — the prune/restock shortlist.
        gaps = sorted(styles, key=lambda g: (credit[g], g))
        hdr = (f"\n{'#':>3}  {'GroupID':<24} {'Colour':<16} "
               + ' '.join(f"{str(s):>3}" for s in CORE_SIZES) + f" {'Core%':>6}")
        print(hdr)
        print("  " + "-" * (len(hdr) - 3))
        for i, gid in enumerate(gaps, 1):
            cells = ' '.join(f"{qty[gid].get(s, 0):>3}" for s in CORE_SIZES)
            col = (colour.get(gid) or '-')[:16]
            print(f"{i:>3}  {gid:<24} {col:<16} {cells} {credit[gid] * 100:>5.0f}%")


if __name__ == '__main__':
    main(detail='--detail' in sys.argv)
