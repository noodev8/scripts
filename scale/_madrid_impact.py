import sys
sys.path.insert(0, r'C:\scripts')
import psycopg2
from psycopg2.extras import RealDictCursor
from logging_utils import get_db_config

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor(cursor_factory=RealDictCursor)

cur.execute("SELECT groupid FROM skusummary WHERE segment ILIKE '%MADRID%' ORDER BY groupid;")
gids = [r['groupid'] for r in cur.fetchall()]
print("MADRID groupids:", gids)

# 1. Colleague's logged decision(s)
print("\n=== segment_notes (MADRID-SEG) ===")
cur.execute("""
    SELECT note_date, author, note, created_at
    FROM segment_notes WHERE segment ILIKE '%MADRID%'
    ORDER BY note_date DESC, created_at DESC;
""")
notes = cur.fetchall()
if not notes:
    print("  (none)")
for n in notes:
    print(f"  {n['note_date']} | {n['author']} | created {n['created_at']}")
    print(f"      {n['note']}")

# 2. price_track columns
cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='price_track' ORDER BY ordinal_position;
""")
cols = [r['column_name'] for r in cur.fetchall()]
print("\nprice_track columns:", cols)

# 3. Recent price_track rows for MADRID (try common date/price column names)
print("\n=== price_track recent (MADRID) ===")
try:
    cur.execute("""
        SELECT * FROM price_track
        WHERE groupid = ANY(%s)
        ORDER BY 1 DESC LIMIT 60;
    """, (gids,))
    rows = cur.fetchall()
    if rows:
        print("  cols:", list(rows[0].keys()))
        for r in rows[:60]:
            print("  ", dict(r))
    else:
        print("  (no rows for these groupids — checking by code)")
except Exception as e:
    print("  price_track query failed:", e)

cur.close(); conn.close()
