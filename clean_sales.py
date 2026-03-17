#!/usr/bin/env python3
"""
Weekly sales table maintenance.
Runs clean_sales.sql to:
  1. Delete sales older than 900 days
  2. Fix returns that arrived with soldprice = 0

Cron: 0 4 * * 1 /apps/scripts/venv/bin/python /apps/scripts/clean_sales.py
"""

import psycopg2
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config

SCRIPT_NAME = "clean_sales"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


def main():
    log("=== CLEAN SALES STARTED ===")
    start_time = datetime.now()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "database", "clean_sales.sql")

    try:
        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()
    except FileNotFoundError:
        log(f"ERROR: SQL file not found: {sql_path}")
        return 1

    conn = None
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(sql)
        conn.commit()

        duration = (datetime.now() - start_time).total_seconds()
        log(f"=== CLEAN SALES COMPLETED ({duration:.2f}s) ===")
        return 0

    except Exception as e:
        log(f"ERROR: {e}")
        if conn:
            conn.rollback()
        return 1

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    exit(main())
