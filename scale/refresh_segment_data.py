"""Refresh the Segments sheet's auto-computed columns from the DB.

ONE run does everything — no per-segment looping needed.

What it does:
  1. Reads every segment CODE from the 'Segments' tab (segments are NOT hardcoded
     here — they come from the sheet's 'SEGMENT CODE' column).
  2. Recomputes, per segment, from the DB over the trailing 365 days:
       STYLES       = count of groupids in skusummary for that segment
       REVENUE (12m)= SUM(qty * soldprice)
       GP (12m)     = SUM(qty * (soldprice - cost))
       GP %         = GP / REVENUE
  3. Writes those four columns back, matched by HEADER NAME (not fixed letters).

NEVER touches: SEGMENT NAME, OWNER, REVIEWED, or the HUMAN NOTES column.
A sheet code with no DB match is left exactly as-is (and reported).

Run (live):     python scale/refresh_segment_data.py
Run (preview):  python scale/refresh_segment_data.py --dry-run
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
import gspread
from datetime import date
from google.oauth2.service_account import Credentials
from logging_utils import get_db_config

DRY = '--dry-run' in sys.argv
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET_ID = '1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0'
TAB = 'Segments'
SA_FILE = os.path.join(REPO, 'merchant-feed-api-462809-23c712978791.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# --- 1. compute every segment's data from the DB in a single query ---
SQL = """
WITH cnt AS (
    SELECT segment, COUNT(*) AS styles
    FROM skusummary
    WHERE segment IS NOT NULL AND segment <> ''
    GROUP BY segment
),
sal AS (
    SELECT ss.segment,
           SUM(sa.qty * sa.soldprice) AS rev,
           SUM(sa.qty * (sa.soldprice - COALESCE(NULLIF(ss.cost,'')::numeric, 0))) AS gp
    FROM skusummary ss
    JOIN sales sa ON sa.groupid = ss.groupid
    WHERE sa.qty > 0 AND sa.soldprice > 0
      AND sa.solddate::date > current_date - 365
    GROUP BY ss.segment
)
SELECT c.segment, c.styles,
       COALESCE(ROUND(s.rev), 0)::bigint AS rev,
       COALESCE(ROUND(s.gp), 0)::bigint  AS gp
FROM cnt c
LEFT JOIN sal s ON s.segment = c.segment
"""
conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute(SQL)
db = {r[0]: (int(r[1]), int(r[2]), int(r[3])) for r in cur.fetchall()}
conn.close()

# --- 2. open the sheet; locate the four columns by header name ---
creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
ws = gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(TAB)
vals = ws.get_all_values()
header = [h.strip().upper() for h in vals[0]]


def col_of(*names):
    for i, h in enumerate(header):
        if h in names:
            return i
    raise SystemExit(f"ABORT: column {names} not found. Header row = {vals[0]}")


def col_letter(ci):           # 0-based index -> A1 column letters
    n, s = ci + 1, ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


c_code   = col_of('SEGMENT CODE')
c_styles = col_of('STYLES')
c_rev    = col_of('REVENUE (12M)')
c_gp     = col_of('GP (12M)')
c_pct    = col_of('GP %', 'GP%')

# --- 3. build one value-vector per column (keep existing where no DB match) ---
n = len(vals)
styles_v, rev_v, gp_v, pct_v = [], [], [], []
missing, preview = [], []
for r in range(1, n):                       # sheet rows 2..n
    row = vals[r]
    code = row[c_code].strip() if c_code < len(row) else ''
    cur_at = lambda ci: [row[ci]] if ci < len(row) else ['']
    if code and code in db:
        styles, rev, gp = db[code]
        pct = f"{100.0 * gp / rev:.2f}%" if rev else "0%"
        styles_v.append([styles]); rev_v.append([rev]); gp_v.append([gp]); pct_v.append([pct])
        preview.append((code, styles, rev, gp, pct))
    else:
        if code:
            missing.append(code)
        styles_v.append(cur_at(c_styles)); rev_v.append(cur_at(c_rev))
        gp_v.append(cur_at(c_gp)); pct_v.append(cur_at(c_pct))

updates = [
    {'range': f"{col_letter(c_styles)}2:{col_letter(c_styles)}{n}", 'values': styles_v},
    {'range': f"{col_letter(c_rev)}2:{col_letter(c_rev)}{n}",       'values': rev_v},
    {'range': f"{col_letter(c_gp)}2:{col_letter(c_gp)}{n}",         'values': gp_v},
    {'range': f"{col_letter(c_pct)}2:{col_letter(c_pct)}{n}",       'values': pct_v},
]

# --- 4. write (or preview) + concise report ---
print(f"Segment data refresh ({date.today()}){'  [DRY RUN — no write]' if DRY else ''}")
print(f"  segments on sheet: {n - 1} | recomputed from DB: {len(preview)} | no DB match: {len(missing)}")
if DRY:
    print(f"  {'CODE':<22}{'Styles':>7}{'Revenue':>10}{'GP':>9}{'GP%':>9}")
    for code, st, rev, gp, pct in preview:
        print(f"  {code:<22}{st:>7}{rev:>10}{gp:>9}{pct:>9}")
else:
    ws.batch_update(updates, value_input_option='USER_ENTERED')
    print("  wrote Styles / Revenue / GP / GP% (USER_ENTERED).")
print("  untouched: SEGMENT NAME, OWNER, REVIEWED, HUMAN NOTES.")
if missing:
    print(f"  WARNING: not found in DB, left as-is: {', '.join(missing)}")
