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

ACTION_NAMES = {
    'DROP_TO_COST': "Liquidation (Cost + £0.01)",
    'DROP_40': "Critical Aging (40% reduction)",
    'DROP_30': "Serious Aging (30% reduction)",
    'DROP_20': "Aggressive Clearance (20% reduction)",
    'DROP_15': "Strong Signal (15% reduction)",
    'DROP_10': "Moderate Reduction (10% reduction)",
    'DROP_5': "Gentle Reduction (5% reduction)",
    'USE_LOWBENCH': "Market Benchmark Price",
    'MANUAL_REVIEW': "Manual Review Required",
    'HOLD': "Hold Current Price"
}

PRIORITY_ACTIONS = ['DROP_TO_COST', 'DROP_40', 'DROP_30', 'MANUAL_REVIEW']  # High priority actions for daily attention

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

    # Group by action
    by_action = {}

    for item in filtered_results:
        action = item.get('action', 'UNKNOWN')
        if action not in by_action:
            by_action[action] = []
        by_action[action].append(item)

    report_content.append("DAILY PRICE RECOMMENDATION REPORT")
    report_content.append("=" * 60)
    report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_content.append(f"Total Products Analyzed: {len(analysis_results)}")
    report_content.append(f"Products Needing Action: {len(filtered_results)}")
    report_content.append("")

    # Executive Summary
    report_content.append("EXECUTIVE SUMMARY")
    report_content.append("-" * 30)

    priority_count = 0

    for action in PRIORITY_ACTIONS:
        if action in by_action:
            items = by_action[action]
            priority_count += len(items)
            action_name = ACTION_NAMES.get(action, action)
            report_content.append(f"{action_name}: {len(items)} items")

    report_content.append(f"\nHIGH PRIORITY TOTAL: {priority_count} items")
    report_content.append("")
        
    if not summary_only:
        # Detailed breakdown by action
        report_content.append("DETAILED BREAKDOWN")
        report_content.append("=" * 60)
        report_content.append("")

        # Sort actions by priority (exclude HOLD from detailed view)
        action_priority = {
            'DROP_TO_COST': 1, 'DROP_40': 2, 'DROP_30': 3, 'MANUAL_REVIEW': 4,
            'DROP_20': 5, 'DROP_15': 6, 'USE_LOWBENCH': 7, 'DROP_10': 8, 'DROP_5': 9
        }

        # Filter out HOLD actions for detailed view
        actionable_items = {k: v for k, v in by_action.items() if k != 'HOLD'}
        sorted_actions = sorted(actionable_items.keys(), key=lambda x: action_priority.get(x, 99))

        for action in sorted_actions:
            items = actionable_items[action]
            action_name = ACTION_NAMES.get(action, action)

            report_content.append(f"{action_name.upper()} ({len(items)} items)")
            report_content.append("-" * 70)

            # Sort by days since last sold (descending) then by stock (descending)
            items_sorted = sorted(items, key=lambda x: (int(x['days_since_last_sold']), int(x['stock'])), reverse=True)

            for item in items_sorted[:15]:  # Top 15 per action
                current = float(item['current_price'])
                suggested = float(item['suggested_price'])
                stock = int(item['stock'])
                days_stale = item['days_since_last_sold']
                groupid = item['groupid']
                brand = item.get('brand', 'Unknown')
                category = item.get('pricing_category', 'Unknown')

                # Calculate percentage change
                pct_change = ((suggested - current) / current) * 100

                # Show category indicator
                cat_indicator = "Z" if category == "ZERO_SALES" else "H"

                report_content.append(f"  {groupid}: £{current:.2f} -> £{suggested:.2f} ({pct_change:+.1f}%) "
                                    f"[{cat_indicator}] (Stock: {stock}, {days_stale}d, {brand})")

            if len(items) > 15:
                report_content.append(f"  ... and {len(items) - 15} more items")

            report_content.append("")

    # Quick action commands and legend
    report_content.append("LEGEND")
    report_content.append("-" * 30)
    report_content.append("[Z] = Zero Sales Product (no sales in 90+ days)")
    report_content.append("[H] = Historical Sales Product (has sales in last 90 days)")
    report_content.append("")

    report_content.append("PRICING LOGIC APPLIED")
    report_content.append("-" * 30)
    report_content.append("This report uses the Brookfield Comfort Dynamic Pricing Logic v1.0")
    report_content.append("• Zero Sales: Time-based reductions based on aging and stock levels")
    report_content.append("• Historical Sales: Conservative reductions considering recent activity")
    report_content.append("• All prices respect cost floor (cost + £0.01 minimum)")
    report_content.append("• Manual Review: Conflicting signals require human judgment")
    report_content.append("")

    report_content.append("QUICK ACTION COMMANDS")
    report_content.append("-" * 30)
    report_content.append("To list all pending recommendations:")
    report_content.append("  python apply_price_changes.py --list-pending")
    report_content.append("\nTo apply individual changes:")
    report_content.append("  python apply_price_changes.py GROUPID NEW_PRICE \"REASON\"")
    report_content.append("\nTo apply specific action types (when bucket system is updated):")
    for action in PRIORITY_ACTIONS:
        if action in by_action:
            report_content.append(f"  # {ACTION_NAMES[action]}: {len(by_action[action])} items")

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
