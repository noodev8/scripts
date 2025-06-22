#!/usr/bin/env python3
"""
Sales Burst Report for Brookfield Comfort
Identifies products with sales bursts that may warrant price increases

USAGE:
python sales_burst_report.py                    # Generate report and log analysis
python sales_burst_report.py --help             # Show usage help

This script analyzes recent sales patterns to identify products experiencing
sales bursts that may indicate demand exceeding expectations, suggesting
potential for price increases.

The analysis considers:
- Recent sales volume vs historical average
- Stock levels and movement
- Exclusion of products with recent price changes (7 days)
- Priority ranking based on burst intensity

Results are logged and saved to a report file for manual review.
"""

import psycopg2
import sys
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, save_report_file, get_db_config

# --- CONFIGURATION ---
# Setup logging
SCRIPT_NAME = "sales_burst_report"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def get_sales_burst_analysis():
    """Execute the sales burst SQL analysis and return results"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Read the SQL file
        sql_file_path = os.path.join("database", "sales_burst_report.sql")
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries
        analysis_results = []
        for row in results:
            analysis_results.append(dict(zip(columns, row)))
        
        cur.close()
        conn.close()
        
        log(f"Sales burst analysis completed: {len(analysis_results)} products identified")
        return analysis_results
        
    except Exception as e:
        log(f"ERROR: Failed to execute sales burst analysis: {str(e)}")
        return []

def generate_report(analysis_results):
    """Generate detailed report of sales burst analysis"""
    report_content = []
    report_content.append("SALES BURST ANALYSIS REPORT")
    report_content.append("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    report_content.append("=" * 60)
    report_content.append("")
    
    if not analysis_results:
        report_content.append("No products with sales bursts identified.")
        report_content.append("")
        report_content.append("This could indicate:")
        report_content.append("- No significant sales spikes in recent period")
        report_content.append("- All products with bursts had recent price changes")
        report_content.append("- Current pricing is well-optimized")
        report_content.append("")
    else:
        # Summary by priority
        priority_summary = {}
        for item in analysis_results:
            status_code = item.get('status_code', 0)
            if status_code not in priority_summary:
                priority_summary[status_code] = []
            priority_summary[status_code].append(item)

        report_content.append("SUMMARY BY PRIORITY:")
        report_content.append("-" * 30)
        
        priority_names = {
            1: "High Burst (5+ sales)",
            2: "Burst (3-4 sales, low avg)",
            3: "Medium Strong (2 sales, very low avg)",
            4: "Medium (2 sales, low avg)",
            5: "Low Burst (2 sales)"
        }
        
        for priority in sorted(priority_summary.keys()):
            items = priority_summary[priority]
            name = priority_names.get(priority, f"Priority {priority}")
            report_content.append(f"Priority {priority} ({name}): {len(items)} products")

        report_content.append("")
        report_content.append("QUICK DECISION SUMMARY:")
        report_content.append("-" * 30)

        # One-line summary for each product, sorted by priority and profit impact
        all_items = []
        for priority in sorted(priority_summary.keys()):
            all_items.extend(priority_summary[priority])

        # Sort by priority first, then by total profit impact (descending)
        all_items.sort(key=lambda x: (x['status_code'], -float(x['total_profit_impact'])))

        for item in all_items:
            days_since = item['days_since_price_change']
            if days_since > 365:
                days_text = "Never changed"
            else:
                days_text = f"{days_since}d ago"

            profit_impact = f"£{item['total_profit_impact']}"
            stock_info = f"Stock: {item['shopify_stock']}"
            trend_short = item['sales_trend'].split()[0]  # Just "Strong", "Moderate", "Stable", "Slow", "No"

            report_content.append(f"  {item['groupid']}: £{item['shopify_price']} -> £{item['recommended_price']} "
                                f"({stock_info}, {trend_short} trend, +{profit_impact}, {days_text})")

        report_content.append("")
        report_content.append("=" * 60)
        report_content.append("")

        # Detailed listings by priority
        for priority in sorted(priority_summary.keys()):
            items = priority_summary[priority]
            name = priority_names.get(priority, f"Priority {priority}")

            report_content.append(f"PRIORITY {priority}: {name} ({len(items)} products)")
            report_content.append("-" * 50)

            for item in items:
                report_content.append(f"GroupID: {item['groupid']}")
                report_content.append(f"  Date: {item['date']}")
                report_content.append(f"  Current Sales: {item['shopify_sales']}")
                report_content.append(f"  Recent Average: {item['avg_recent_sales'] or 0:.2f}")
                report_content.append(f"  Sales Trend: {item['sales_trend']} (14d avg: {item['avg_sales_14d'] or 0:.1f})")
                report_content.append("")
                report_content.append(f"  PRICING:")
                report_content.append(f"    Current Price: £{item['shopify_price']}")
                report_content.append(f"    Recommended Price: £{item['recommended_price']}")
                report_content.append(f"    Price Increase: {item['price_change_percent']}%")
                if item['rrp']:
                    report_content.append(f"    RRP: £{item['rrp']}")
                report_content.append("")
                report_content.append(f"  PROFIT IMPACT:")
                report_content.append(f"    Current Profit/Unit: £{item['current_profit_per_unit']}")
                report_content.append(f"    New Profit/Unit: £{item['new_profit_per_unit']}")
                report_content.append(f"    Profit Increase/Unit: £{item['profit_increase_per_unit']}")
                report_content.append(f"    Total Profit Impact: £{item['total_profit_impact']} (based on {item['shopify_stock']} units)")
                report_content.append("")
                report_content.append(f"  STOCK & HISTORY:")
                report_content.append(f"    Current Stock: {item['shopify_stock']}")
                if item['prev_stock'] is not None:
                    report_content.append(f"    Previous Stock: {item['prev_stock']}")
                days_since = item['days_since_price_change']
                if days_since > 365:
                    report_content.append(f"    Last Price Change: Never recorded")
                else:
                    report_content.append(f"    Last Price Change: {days_since} days ago ({item['last_price_change_date']})")
                report_content.append(f"    Price Changes (30d): {item['price_changes_30d']}")
                report_content.append(f"    Sales History (14d): {item['total_sales_14d']} units over {item['days_with_sales_14d']} days")
                report_content.append("")
                report_content.append(f"  Action: {item['action']}")
                report_content.append("")
                report_content.append("-" * 60)
                report_content.append("")

            report_content.append("")

        # Analysis notes
        report_content.append("ANALYSIS NOTES:")
        report_content.append("-" * 20)
        report_content.append("• Products shown have NOT had price changes in the last 7 days")
        report_content.append("• Sales burst = current sales > 2x recent average AND >= 2 sales")
        report_content.append("• Recent average calculated from 3 days prior to 1 day prior")
        report_content.append("• Recommended prices are capped at RRP (never exceed manufacturer price)")
        report_content.append("• Price increases range from 1% (low burst) to 5% (high burst)")
        report_content.append("• Profit calculations account for VAT where applicable")
        report_content.append("• Total profit impact assumes all current stock sells at new price")
        report_content.append("• Sales trends based on 14-day historical average (excluding today)")
        report_content.append("• Consider stock levels, trends, and profit impact before applying changes")
        report_content.append("")

    # Save report to logs directory
    report_filename = save_report_file("sales_burst_report.txt", "\n".join(report_content))
    log(f"Report generated: {report_filename}")
    return report_filename

def show_help():
    """Display usage help"""
    help_text = """
SALES BURST REPORT SYSTEM
=========================

USAGE:
  python sales_burst_report.py                    # Generate report and log analysis
  python sales_burst_report.py --help             # Show this help

ANALYSIS CRITERIA:
  The script identifies products with sales bursts using these criteria:
  
  1. HIGH BURST (Priority 1):
     - 5+ sales in a single day (+5% price increase)
     - Immediate price increase consideration

  2. BURST (Priority 2):
     - 3-4 sales with recent average < 1 (+2% price increase)
     - Strong candidates for price increases

  3. MEDIUM STRONG (Priority 3):
     - 2 sales with very low average <= 0.3 (+3% price increase)

  4. MEDIUM (Priority 4):
     - 2 sales with low average <= 0.5 (+2% price increase)

  5. LOW BURST (Priority 5):
     - 2 sales with any average (+1% price increase)

EXCLUSIONS:
  - Products with price changes in last 7 days
  - Products not meeting minimum burst criteria (< 2 sales)
  - Products where recommended price would exceed RRP

OUTPUT FILES:
  - sales_burst_report.log                # Activity log
  - sales_burst_report.txt                # Detailed analysis report

NEXT STEPS:
  1. Review the generated report
  2. Consider stock levels and market conditions
  3. Manually apply price increases as appropriate
  4. Monitor results in subsequent reports
"""
    print(help_text)

def main():
    """Main execution function"""
    start_time = datetime.now()

    # Parse command line arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        show_help()
        return

    log(f"=== SALES BURST REPORT STARTED ===")
    log(f"Analyzing recent sales patterns for burst identification")

    # Get analysis results
    analysis_results = get_sales_burst_analysis()
    
    # Generate report
    report_file = generate_report(analysis_results)

    # Summary
    duration = datetime.now() - start_time
    duration_str = str(duration).split('.')[0]

    summary = f"COMPLETE - Products analyzed: {len(analysis_results)}, Duration: {duration_str}"
    log(summary)

    print(f"\nSales Burst Report Complete!")
    print(f"Products with sales bursts identified: {len(analysis_results)}")
    print(f"Report generated: {report_file}")
    print(f"Duration: {duration_str}")
    
    if analysis_results:
        print(f"\nNext steps:")
        print(f"1. Review {report_file} for detailed analysis")
        print(f"2. Consider price increases for identified products")
        print(f"3. Monitor stock levels before applying changes")
    else:
        print(f"\nNo sales bursts identified - current pricing appears well-optimized")

if __name__ == "__main__":
    main()
