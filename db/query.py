#!/usr/bin/env python3
"""
Ad-hoc read-only query against the production database.

The front door for "just look something up" -- exploration, schema checks,
sanity-checking a number before acting on it. Scheduled jobs should keep
connecting directly with get_db_config(); this is for interactive use.

Every query runs inside a READ ONLY transaction, so an accidental
UPDATE/DELETE/DROP fails at the database rather than doing damage.

    python db/query.py "SELECT count(*) FROM sales"
    python db/query.py --file report.sql
    echo "SELECT 1" | python db/query.py
    python db/query.py --csv "SELECT code, qty FROM localstock" > out.csv

See db/README.md for the gotchas that will otherwise cost you an hour.
"""

import argparse
import csv
import os
import sys

import psycopg2

# Shared DB config lives at the repo root, one level up. Anchor on __file__ --
# cron runs with no cd, so a relative path resolves against the wrong home.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from logging_utils import get_db_config

DEFAULT_MAX_ROWS = 200


def render_table(columns, rows):
    """Fixed-width table. Readable in a terminal and stable enough to diff."""
    cells = [[("" if v is None else str(v)) for v in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in cells:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    out = [" | ".join(c.ljust(widths[i]) for i, c in enumerate(columns)).rstrip()]
    out.append("-+-".join("-" * w for w in widths))
    for row in cells:
        out.append(" | ".join(v.ljust(widths[i]) for i, v in enumerate(row)).rstrip())
    return "\n".join(out)


def read_sql(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            return handle.read()
    if args.sql:
        return " ".join(args.sql)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Run a read-only SQL query against the production database.",
    )
    parser.add_argument("sql", nargs="*", help="SQL to run. Quote it.")
    parser.add_argument("-f", "--file", help="Read SQL from a file instead.")
    parser.add_argument("--csv", action="store_true", help="Emit CSV instead of a table.")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help=f"Stop printing after N rows (default {DEFAULT_MAX_ROWS}). 0 for no limit.",
    )
    args = parser.parse_args()

    sql = read_sql(args).strip()
    if not sql:
        parser.error("no SQL given -- pass it as an argument, with --file, or on stdin")

    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        # Belt and braces: the session refuses writes, and so does the
        # transaction. Either alone would do; both means a stray commit path
        # cannot slip through.
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(sql)

            if cur.description is None:
                print(f"OK -- no rows returned ({cur.statusmessage}).")
                return 0

            columns = [d[0] for d in cur.description]
            rows = cur.fetchall()

        shown = rows if args.max_rows in (0, None) else rows[: args.max_rows]

        if args.csv:
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(columns)
            writer.writerows(shown)
        else:
            print(render_table(columns, shown))
            print(f"\n({len(rows)} row{'' if len(rows) == 1 else 's'})")

        if len(shown) < len(rows):
            print(
                f"-- showing first {len(shown)} of {len(rows)}; "
                f"raise --max-rows or add a LIMIT",
                file=sys.stderr,
            )
        return 0

    except psycopg2.Error as exc:
        # Includes the read-only rejection, which is the point: a write fails
        # here rather than succeeding quietly.
        print(f"Query failed: {str(exc).strip()}", file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
