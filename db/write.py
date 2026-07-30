#!/usr/bin/env python3
"""
Ad-hoc WRITE against the production database.

Writing is allowed and expected -- this is not a locked door. The script exists so
writes happen the same way every time: in one transaction, with the affected row
count reported, and with a dry run available when you want to see the damage first.

    python db/write.py "UPDATE skusummary SET segment='IVES' WHERE groupid='X'"
    python db/write.py --dry-run "DELETE FROM price_track WHERE created < '2024-01-01'"
    python db/write.py --file migration.sql

Everything in one invocation runs in a single transaction and commits together, or
rolls back together if any statement fails. Reads still belong in query.py.

The one guard: an UPDATE or DELETE with no WHERE clause is refused unless you pass
--all-rows. That is the mistake worth catching; nothing else is in the way.

See db/README.md.
"""

import argparse
import os
import re
import sys

import psycopg2

# Shared DB config lives at the repo root, one level up. Anchor on __file__ --
# cron runs with no cd, so a relative path resolves against the wrong home.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from logging_utils import get_db_config

# Statements that change data and are near-always meant to be scoped.
UNSCOPED_RISK = re.compile(r"^\s*(update|delete)\s", re.IGNORECASE)


def split_statements(sql):
    """Split on semicolons that aren't inside quotes or dollar-quoted blocks."""
    statements, buf = [], []
    quote = None
    i = 0
    while i < len(sql):
        ch = sql[i]
        if quote:
            if ch == quote:
                quote = None
            buf.append(ch)
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == ";":
            statements.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    statements.append("".join(buf))
    return [s.strip() for s in statements if s.strip()]


def check_unscoped(statements, allow_all_rows):
    """Refuse an UPDATE/DELETE with no WHERE unless explicitly allowed."""
    if allow_all_rows:
        return None
    for stmt in statements:
        if UNSCOPED_RISK.match(stmt) and not re.search(r"\bwhere\b", stmt, re.IGNORECASE):
            verb = stmt.split()[0].upper()
            return (
                f"{verb} with no WHERE clause would affect every row:\n"
                f"  {stmt[:120]}\n"
                f"Add a WHERE, or pass --all-rows if that really is the intent."
            )
    return None


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
        description="Run write SQL against the production database, in one transaction.",
    )
    parser.add_argument("sql", nargs="*", help="SQL to run. Quote it.")
    parser.add_argument("-f", "--file", help="Read SQL from a file instead.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute, report row counts, then roll back. Nothing is kept.",
    )
    parser.add_argument(
        "--all-rows",
        action="store_true",
        help="Permit an UPDATE/DELETE with no WHERE clause.",
    )
    args = parser.parse_args()

    sql = read_sql(args).strip()
    if not sql:
        parser.error("no SQL given -- pass it as an argument, with --file, or on stdin")

    statements = split_statements(sql)
    problem = check_unscoped(statements, args.all_rows)
    if problem:
        print(f"Refused: {problem}", file=sys.stderr)
        return 2

    conn = None
    try:
        conn = psycopg2.connect(**get_db_config())
        conn.autocommit = False  # one transaction for the whole invocation
        total = 0
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
                affected = cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
                total += affected
                label = " ".join(stmt.split()[:6])
                print(f"{cur.statusmessage:<20} {affected:>7} row(s)  <- {label}")

        if args.dry_run:
            conn.rollback()
            print(f"\nDRY RUN -- rolled back. {total} row(s) would have changed.")
        else:
            conn.commit()
            print(f"\nCommitted. {total} row(s) changed.")
        return 0

    except psycopg2.Error as exc:
        if conn is not None:
            conn.rollback()
        print(f"\nFailed, rolled back -- nothing was changed.\n{str(exc).strip()}", file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
