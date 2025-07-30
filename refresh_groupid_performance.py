#!/usr/bin/env python3
"""
Database Maintenance Script
Runs 3 SQL scripts in order, then updates price recommendations:
1. clean_sales.sql - Remove deleted/expired products and fix return prices
2. refresh_perfomance.sql - Refresh performance and groupid_performance tables
3. weekly_snapshot.sql - Create weekly snapshot in groupid_performance_week
4. Update recommended prices for all SHP channel items

This script is designed to run via cron on the server.
"""

import psycopg2
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config
from price_recommendation import update_all_recommended_prices

# Setup logging
SCRIPT_NAME = "refresh_groupid_perfromance"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def read_sql_file(filename):
    """Read SQL file content from database folder"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(script_dir, "database", filename)
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        log(f"ERROR: SQL file not found: {sql_file_path}")
        raise
    except Exception as e:
        log(f"ERROR: Failed to read SQL file {filename}: {str(e)}")
        raise

def execute_sql_script(cursor, sql_content, script_name):
    """Execute SQL script content with error handling"""
    try:
        log(f"Executing {script_name}...")
        start_time = datetime.now()
        
        # Execute the SQL content
        cursor.execute(sql_content)
        
        # Get row count if available
        try:
            row_count = cursor.rowcount
            if row_count >= 0:
                log(f"{script_name} completed - {row_count} rows affected")
            else:
                log(f"{script_name} completed successfully")
        except:
            log(f"{script_name} completed successfully")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        log(f"{script_name} execution time: {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        log(f"ERROR: Failed to execute {script_name}: {str(e)}")
        return False

def main():
    """Main function to run all database maintenance scripts"""
    log("=== DATABASE MAINTENANCE STARTED ===")
    start_time = datetime.now()
    
    # Define the SQL scripts to run in order
    sql_scripts = [
        ("clean_sales.sql", "Sales Data Cleanup"),
        ("refresh_perfomance.sql", "Performance Tables Refresh"),
        ("weekly_snapshot.sql", "Weekly Performance Snapshot")
    ]
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        log("Connecting to database...")
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        log("Database connection established")
        
        # Execute each SQL script in order
        all_successful = True
        
        for sql_file, description in sql_scripts:
            log(f"--- Starting: {description} ---")
            
            # Read SQL file content
            try:
                sql_content = read_sql_file(sql_file)
            except Exception:
                log(f"CRITICAL: Cannot read {sql_file}, stopping execution")
                all_successful = False
                break
            
            # Execute the SQL script
            success = execute_sql_script(cursor, sql_content, description)
            
            if success:
                # Commit after each successful script
                conn.commit()
                log(f"--- Completed: {description} ---")
            else:
                log(f"CRITICAL: {description} failed, rolling back and stopping")
                conn.rollback()
                all_successful = False
                break
        
        # Step 4: Update recommended prices for all SHP channel items
        if all_successful:
            log("--- Starting: Price Recommendations Update ---")
            try:
                stats = update_all_recommended_prices(mode="Steady", db_config=db_config)
                log(f"Price recommendations completed - Processed: {stats['total_processed']}, "
                    f"Calculated: {stats['recommendations_generated']}, "
                    f"Current prices used: {stats['current_price_used']}, "
                    f"No price set: {stats['no_price_set']}, "
                    f"Errors: {stats['errors']}")
                log("--- Completed: Price Recommendations Update ---")
            except Exception as e:
                log(f"WARNING: Price recommendations update failed: {str(e)}")
                # Don't fail the entire process for price recommendation errors
                log("Continuing despite price recommendation errors...")

        # Final status
        if all_successful:
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            log(f"=== DATABASE MAINTENANCE COMPLETED SUCCESSFULLY ===")
            log(f"Total execution time: {total_duration:.2f} seconds")
        else:
            log("=== DATABASE MAINTENANCE FAILED ===")
            return 1
            
    except Exception as e:
        log(f"CRITICAL ERROR: Database maintenance failed: {str(e)}")
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
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
