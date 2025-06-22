#!/usr/bin/env python3
"""
Daily Price Drop Report Generator
Generates a concise daily report of price drop recommendations

USAGE:
python daily_price_report.py                # Generate today's report
python daily_price_report.py --email        # Generate and email report (future)
python daily_price_report.py --summary      # Generate summary only
"""

import psycopg2
import sys
import os
from datetime import datetime, date
from logging_utils import manage_log_files, create_logger, save_report_file, get_db_config

BUCKET_NAMES = {
    1: "Dead Stock (180+ days)",
    2: "Market Mismatch", 
    3: "Stock Heavy",
    4: "Low Margin",
    5: "Slow Mover",
    6: "Low Stock/Recent",
    7: "Early Warning"
}

PRIORITY_BUCKETS = [1, 2, 3]  # High priority buckets for daily attention

# Setup logging
SCRIPT_NAME = "daily_price_report"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def get_price_analysis():
    """Get price drop analysis results"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        sql_file_path = os.path.join("database", "product_price_drop.sql")
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        analysis_results = []
        for row in results:
            analysis_results.append(dict(zip(columns, row)))
        
        cur.close()
        conn.close()

        log(f"Price analysis completed: {len(analysis_results)} products analyzed")
        return analysis_results

    except Exception as e:
        log(f"ERROR: Failed to get analysis: {str(e)}")
        print(f"ERROR: Failed to get analysis: {str(e)}")
        return []

def filter_recent_changes(analysis_results):
    """Filter out products with recent price changes"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        filtered_results = []
        for item in analysis_results:
            groupid = item['groupid']
            
            # Check for recent changes
            cur.execute("""
                SELECT COUNT(*) FROM price_change_log 
                WHERE groupid = %s AND change_date >= CURRENT_DATE - INTERVAL '7 days'
            """, (groupid,))
            
            recent_changes = cur.fetchone()[0]
            if recent_changes == 0:
                filtered_results.append(item)
        
        cur.close()
        conn.close()
        
        return filtered_results
        
    except Exception as e:
        print(f"ERROR: Failed to filter recent changes: {str(e)}")
        return analysis_results

def generate_daily_report(analysis_results, summary_only=False):
    """Generate daily report"""
    report_content = []
    
    # Filter out recent changes
    filtered_results = filter_recent_changes(analysis_results)
    
    # Group by bucket
    by_bucket = {}

    for item in filtered_results:
        bucket = item.get('bucket')
        if bucket:
            if bucket not in by_bucket:
                by_bucket[bucket] = []
            by_bucket[bucket].append(item)
    
    report_content.append("DAILY PRICE DROP REPORT")
    report_content.append("=" * 50)
    report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_content.append(f"Total Products Analyzed: {len(analysis_results)}")
    report_content.append(f"Products Needing Action: {len(filtered_results)}")
    report_content.append("")

    # Executive Summary
    report_content.append("EXECUTIVE SUMMARY")
    report_content.append("-" * 30)

    priority_count = 0

    for bucket in PRIORITY_BUCKETS:
        if bucket in by_bucket:
            items = by_bucket[bucket]
            priority_count += len(items)
            report_content.append(f"Bucket {bucket} ({BUCKET_NAMES[bucket]}): {len(items)} items")

    report_content.append(f"\nHIGH PRIORITY TOTAL: {priority_count} items")
    report_content.append("")
        
    if not summary_only:
        # Detailed breakdown by bucket
        report_content.append("DETAILED BREAKDOWN")
        report_content.append("=" * 50)
        report_content.append("")

        for bucket in sorted(by_bucket.keys()):
            items = by_bucket[bucket]
            bucket_name = BUCKET_NAMES.get(bucket, f"Bucket {bucket}")

            report_content.append(f"BUCKET {bucket}: {bucket_name} ({len(items)} items)")
            report_content.append("-" * 60)

            # Sort by stock level (descending) to prioritize high-stock items
            items_sorted = sorted(items, key=lambda x: int(x['stock']), reverse=True)

            for item in items_sorted[:10]:  # Top 10 per bucket
                current = float(item['current_price'])
                suggested = float(item['suggested_price'])
                stock = int(item['stock'])
                days_stale = item['days_since_last_sold']
                groupid = item['groupid']
                brand = item.get('brand', 'Unknown')

                report_content.append(f"  {groupid}: £{current:.2f} -> £{suggested:.2f} (Stock: {stock}, Stale: {days_stale} days, {brand})")

            if len(items) > 10:
                report_content.append(f"  ... and {len(items) - 10} more items")

            report_content.append("")

    # Quick action commands
    report_content.append("QUICK ACTION COMMANDS")
    report_content.append("-" * 30)
    report_content.append("To apply all changes for a bucket:")
    for bucket in PRIORITY_BUCKETS:
        if bucket in by_bucket:
            report_content.append(f"  python apply_price_changes.py --bucket {bucket}")

    report_content.append("\nTo list all pending recommendations:")
    report_content.append("  python apply_price_changes.py --list-pending")
    report_content.append("\nTo apply individual changes:")
    report_content.append("  python apply_price_changes.py GROUPID NEW_PRICE \"REASON\"")

    # Save report to logs directory
    report_filename = save_report_file("daily_price_report.txt", "\n".join(report_content))
    return report_filename, len(filtered_results), priority_count

def generate_summary_email_text(report_filename, total_items, priority_items):
    """Generate summary text suitable for email"""
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Extract just the filename from the full path for display
    report_display_name = os.path.basename(report_filename)

    summary = f"""
DAILY PRICE DROP SUMMARY - {date_str}

Total items needing price drops: {total_items}
High priority items (Buckets 1-3): {priority_items}

Quick Actions:
- Review high priority items first (Buckets 1-3)
- Use: python apply_price_changes.py --bucket 1
- Full report: logs/{report_display_name}

Generated at {datetime.now().strftime('%H:%M')}
"""
    return summary

def main():
    """Main execution function"""
    args = sys.argv[1:]

    summary_only = "--summary" in args
    email_mode = "--email" in args

    log("=== DAILY PRICE REPORT STARTED ===")
    print(f"Generating daily price drop report...")

    # Get analysis
    analysis_results = get_price_analysis()
    if not analysis_results:
        log("ERROR: No analysis results obtained")
        print("ERROR: No analysis results obtained")
        return
    
    # Generate report
    report_filename, total_items, priority_items = generate_daily_report(
        analysis_results, summary_only
    )

    log(f"Report generated: {report_filename}")
    log(f"Total items: {total_items}, Priority items: {priority_items}")

    print(f"Report generated: {report_filename}")
    print(f"Total items: {total_items}")
    print(f"Priority items: {priority_items}")

    # Generate summary
    summary = generate_summary_email_text(report_filename, total_items, priority_items)
    print("\nSUMMARY:")
    print(summary)

    if email_mode:
        log("Email mode requested but not yet implemented")
        print("Email functionality not yet implemented")
        # Future: Send email with summary and attach full report

    # Save summary to logs folder
    summary_filename = save_report_file("daily_summary.txt", summary)

    log(f"Summary saved: {os.path.basename(summary_filename)}")
    log("=== DAILY PRICE REPORT COMPLETED ===")
    print(f"Summary saved: {summary_filename}")

if __name__ == "__main__":
    main()
