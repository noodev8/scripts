#!/usr/bin/env python3
"""
Stock Update Script for Performance Tables
Updates stock quantities in both 'performance' and 'groupid_performance' tables
from current 'localstock' data.

This script is designed to run daily via cron to keep stock data current,
while the main performance refresh runs weekly.
"""

import psycopg2
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "refresh_performance_stock"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def update_performance_stock(cursor):
    """Update stock quantities in the performance table"""
    sql = """
    UPDATE performance
    SET stock = COALESCE(ls.stock_qty, 0)
    FROM (
        SELECT
            code,
            SUM(qty) AS stock_qty
        FROM localstock
        WHERE deleted IS DISTINCT FROM 1
        GROUP BY code
    ) ls
    WHERE performance.code = ls.code
      AND performance.channel = 'SHP';
    """
    
    try:
        log("Updating stock in performance table...")
        start_time = datetime.now()
        
        cursor.execute(sql)
        row_count = cursor.rowcount
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log(f"Performance table stock update completed - {row_count} rows updated")
        log(f"Execution time: {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        log(f"ERROR: Failed to update performance table stock: {str(e)}")
        return False

def update_groupid_performance_stock(cursor):
    """Update stock quantities in the groupid_performance table"""
    sql = """
    UPDATE groupid_performance
    SET stock = (
        SELECT SUM(COALESCE(ls.stock_qty, 0))
        FROM (
            SELECT
                code,
                groupid,
                SUM(qty) AS stock_qty
            FROM localstock
            WHERE deleted IS DISTINCT FROM 1
            GROUP BY code, groupid
        ) ls
        WHERE ls.groupid = groupid_performance.groupid
    )
    WHERE groupid_performance.channel = 'SHP';
    """
    
    try:
        log("Updating stock in groupid_performance table...")
        start_time = datetime.now()
        
        cursor.execute(sql)
        row_count = cursor.rowcount
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log(f"Groupid_performance table stock update completed - {row_count} rows updated")
        log(f"Execution time: {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        log(f"ERROR: Failed to update groupid_performance table stock: {str(e)}")
        return False

def main():
    """Main function to update stock in both performance tables"""
    log("=== PERFORMANCE STOCK UPDATE STARTED ===")
    start_time = datetime.now()
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        log("Connecting to database...")
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        log("Database connection established")
        
        # Update stock in both tables
        performance_success = update_performance_stock(cursor)
        groupid_success = update_groupid_performance_stock(cursor)
        
        if performance_success and groupid_success:
            # Commit all changes
            conn.commit()
            
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            log(f"=== PERFORMANCE STOCK UPDATE COMPLETED SUCCESSFULLY ===")
            log(f"Total execution time: {total_duration:.2f} seconds")
            return 0
        else:
            log("CRITICAL: Stock update failed, rolling back changes")
            conn.rollback()
            log("=== PERFORMANCE STOCK UPDATE FAILED ===")
            return 1
            
    except Exception as e:
        log(f"CRITICAL ERROR: Stock update failed: {str(e)}")
        if conn:
            try:
                conn.rollback()
                log("Database transaction rolled back")
            except:
                log("WARNING: Failed to rollback transaction")
        return 1
        
    finally:
        # Clean up database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        log("Database connection closed")

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)