#!/usr/bin/env python3
"""
Brookfield Comfort Price Change Generator
Combines price drop and sales burst analysis into a single CSV for manual approval.
"""

import sys
import os
import psycopg2
import csv
from datetime import datetime
from logging_utils import get_db_config, create_logger

# Setup logging
log = create_logger("generate_price_changes")

def get_price_drop_analysis():
    """Get price drop recommendations using the conservative logic"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Load the price drop SQL
        sql_file_path = os.path.join('database', 'product_price_drop.sql')
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries
        price_drops = []
        for row in results:
            item = dict(zip(columns, row))
            # Only include items that need action (not HOLD)
            if item.get('action') != 'HOLD':
                item['change_type'] = 'PRICE_DROP'
                price_drops.append(item)
        
        cur.close()
        conn.close()
        
        log(f"Price drop analysis: {len(price_drops)} items need action")
        return price_drops
        
    except Exception as e:
        log(f"ERROR: Failed to get price drop analysis: {str(e)}")
        return []

def get_sales_burst_analysis():
    """Get sales burst recommendations"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Load the sales burst SQL
        sql_file_path = os.path.join('database', 'sales_burst_report.sql')
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries
        sales_bursts = []
        for row in results:
            item = dict(zip(columns, row))
            item['change_type'] = 'PRICE_INCREASE'

            # Map sales burst fields to match price drop structure
            item['current_price'] = item.get('shopify_price', 0)
            item['suggested_price'] = item.get('recommended_price', 0)

            # Clean up action name - remove special characters and emojis
            raw_action = item.get('action', 'UNKNOWN')
            clean_action = (raw_action.replace(' ', '_')
                                    .replace('–', '-')
                                    .replace('—', '-')
                                    .replace('â€"', '-')
                                    .replace('Ã¢â‚¬â€œ', '-')
                                    .encode('ascii', 'ignore')
                                    .decode('ascii'))

            item['action'] = f"INCREASE_{clean_action}"
            item['reason'] = f"Sales burst: {clean_action} - {item.get('shopify_sales', 0)} sales today"
            item['stock'] = item.get('shopify_stock', 0)
            item['days_since_last_sold'] = ''  # Not applicable for sales bursts
            item['lowbench'] = ''  # Not applicable for sales bursts

            # Get cost and brand from database
            try:
                db_config = get_db_config()
                conn = psycopg2.connect(**db_config)
                cur = conn.cursor()
                cur.execute("SELECT cost, brand FROM skusummary WHERE groupid = %s", (item['groupid'],))
                result = cur.fetchone()
                if result:
                    item['cost'] = result[0]
                    item['brand'] = result[1]
                else:
                    item['cost'] = 0
                    item['brand'] = 'Unknown'
                cur.close()
                conn.close()
            except:
                item['cost'] = 0
                item['brand'] = 'Unknown'

            sales_bursts.append(item)
        
        cur.close()
        conn.close()
        
        log(f"Sales burst analysis: {len(sales_bursts)} items need action")
        return sales_bursts
        
    except Exception as e:
        log(f"ERROR: Failed to get sales burst analysis: {str(e)}")
        return []

def filter_recent_changes(analysis_results):
    """Filter out products with recent price changes (10-day lock)"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        filtered_results = []
        for item in analysis_results:
            groupid = item['groupid']
            
            # Check for recent changes (10-day lock period)
            cur.execute("""
                SELECT COUNT(*) FROM price_change_log 
                WHERE groupid = %s AND change_date >= CURRENT_DATE - INTERVAL '10 days'
            """, (groupid,))
            
            recent_changes = cur.fetchone()[0]
            if recent_changes == 0:
                filtered_results.append(item)
        
        cur.close()
        conn.close()
        
        log(f"Filtered out {len(analysis_results) - len(filtered_results)} items with recent changes")
        return filtered_results
        
    except Exception as e:
        log(f"ERROR: Failed to filter recent changes: {str(e)}")
        return analysis_results

def generate_csv_report(all_changes):
    """Generate CSV file with all price change recommendations"""
    if not all_changes:
        print("No price changes to recommend")
        return None

    # Use simple filename (no timestamp)
    filename = "price_changes.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV columns
            fieldnames = [
                'approve',           # Empty column for user to enter 1
                'groupid',
                'brand',
                'current_price',
                'suggested_price',
                'change_amount',
                'change_percent',
                'change_type',
                'action',
                'reason',
                'stock',
                'days_since_last_sold',
                'lowbench',
                'cost',
                'margin_impact'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in all_changes:
                current = float(item.get('current_price', 0))
                suggested = float(item.get('suggested_price', current))
                change_amount = suggested - current
                change_percent = (change_amount / current * 100) if current > 0 else 0

                # Skip items with no actual price change
                if abs(change_amount) < 0.01:  # Less than 1 penny change
                    continue

                # Calculate margin impact
                cost = float(item.get('cost', 0))
                current_margin = current - cost
                new_margin = suggested - cost
                margin_impact = new_margin - current_margin
                
                row = {
                    'approve': '',  # Empty for user input
                    'groupid': item.get('groupid', ''),
                    'brand': item.get('brand', ''),
                    'current_price': f"{current:.2f}",
                    'suggested_price': f"{suggested:.2f}",
                    'change_amount': f"{change_amount:+.2f}",
                    'change_percent': f"{change_percent:+.1f}%",
                    'change_type': item.get('change_type', ''),
                    'action': item.get('action', ''),
                    'reason': item.get('reason', ''),
                    'stock': item.get('stock', ''),
                    'days_since_last_sold': item.get('days_since_last_sold', ''),
                    'lowbench': f"{float(item.get('lowbench', 0)):.2f}" if item.get('lowbench') else '',
                    'cost': f"{cost:.2f}",
                    'margin_impact': f"{margin_impact:+.2f}"
                }
                writer.writerow(row)
        
        log(f"CSV report generated: {filename}")
        return filename
        
    except Exception as e:
        log(f"ERROR: Failed to generate CSV: {str(e)}")
        return None

def main():
    """Main execution function"""
    log("=== PRICE CHANGE GENERATOR STARTED ===")
    print("Generating price change recommendations...")
    
    # Get both types of analysis
    price_drops = get_price_drop_analysis()
    sales_bursts = get_sales_burst_analysis()
    
    # Combine all changes
    all_changes = price_drops + sales_bursts
    
    if not all_changes:
        print("No price changes recommended")
        log("No price changes recommended")
        return
    
    # Filter out recent changes
    filtered_changes = filter_recent_changes(all_changes)
    
    # Sort by priority (price increases first, then by change amount)
    def sort_priority(item):
        if item['change_type'] == 'PRICE_INCREASE':
            return (0, -float(item.get('suggested_price', 0)))  # Increases first, highest first
        else:
            current = float(item.get('current_price', 0))
            suggested = float(item.get('suggested_price', current))
            change_percent = abs((suggested - current) / current * 100) if current > 0 else 0
            return (1, -change_percent)  # Drops second, largest drops first
    
    filtered_changes.sort(key=sort_priority)
    
    # Generate CSV
    csv_filename = generate_csv_report(filtered_changes)
    
    if csv_filename:
        print(f"\nPrice change recommendations generated: {csv_filename}")
        print(f"Total recommendations: {len(filtered_changes)}")
        
        # Summary by type
        price_drops_count = len([x for x in filtered_changes if x['change_type'] == 'PRICE_DROP'])
        price_increases_count = len([x for x in filtered_changes if x['change_type'] == 'PRICE_INCREASE'])
        
        print(f"  - Price drops: {price_drops_count}")
        print(f"  - Price increases: {price_increases_count}")
        print(f"\nTo approve changes:")
        print(f"1. Open {csv_filename} in Excel/spreadsheet")
        print(f"2. Enter '1' in the 'approve' column for items you want to change")
        print(f"3. Save the file")
        print(f"4. Run: python apply_price_change.py")
        
        log(f"Generated {len(filtered_changes)} recommendations ({price_drops_count} drops, {price_increases_count} increases)")
    else:
        print("ERROR: Failed to generate CSV file")
    
    log("=== PRICE CHANGE GENERATOR COMPLETED ===")

if __name__ == "__main__":
    main()
