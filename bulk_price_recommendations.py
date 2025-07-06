#!/usr/bin/env python3
"""
Bulk Price Recommendations for Owner's SKUs
Generates price recommendations for all SKUs owned by a specific owner across all pricing modes.

OUTPUT: CSV file with current price, all mode recommendations, and key performance metrics
USAGE: python bulk_price_recommendations.py
"""

import psycopg2
import csv
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config, save_report_file
from price_recommendation import get_price_recommendation

# Setup logging
SCRIPT_NAME = "bulk_price_recommendations"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Configuration
OWNER_NAME = "Andreas"  # Change this to target different owners
PRICING_MODES = ["Steady", "Profit", "Clearance"]  # Ignore mode excluded as it returns None

def get_owner_skus(owner_name, db_config=None):
    """
    Get all GroupIDs owned by a specific owner from groupid_performance table.
    
    Args:
        owner_name (str): Owner name to filter by
        db_config (dict, optional): Database connection parameters
    
    Returns:
        list: List of tuples (groupid, brand, annual_profit, sold_qty, channel)
    """
    if db_config is None:
        db_config = get_db_config()
    
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    try:
        # Get SKUs owned by the specified owner with key performance metrics
        # Focus on Shopify channel (SHP) as that's where price recommendations apply
        cur.execute("""
            SELECT 
                gp.groupid,
                gp.brand,
                gp.annual_profit,
                gp.sold_qty,
                gp.avg_profit_per_unit,
                ROUND(gp.avg_gross_margin * 100, 2) AS margin_pct,
                ss.cost::NUMERIC AS cost,
                ss.shopifyprice::NUMERIC AS current_price,
                ss.lowbench::NUMERIC AS lowbench
            FROM groupid_performance gp
            JOIN skusummary ss ON gp.groupid = ss.groupid
            WHERE gp.owner = %s 
                AND gp.channel = 'SHP'
                AND ss.shopify = 1
            ORDER BY gp.annual_profit DESC
        """, (owner_name,))
        
        results = cur.fetchall()
        log(f"Retrieved {len(results)} SKUs for owner '{owner_name}'")
        return results
        
    finally:
        cur.close()
        conn.close()

def generate_bulk_recommendations(owner_name):
    """
    Generate price recommendations for all SKUs owned by a specific owner.
    
    Args:
        owner_name (str): Owner name to generate recommendations for
    
    Returns:
        str: Path to generated CSV file
    """
    log(f"=== BULK PRICE RECOMMENDATIONS FOR {owner_name} ===")
    
    # Get owner's SKUs
    sku_data = get_owner_skus(owner_name)
    
    if not sku_data:
        log(f"No SKUs found for owner '{owner_name}'")
        return None
    
    # Prepare CSV data
    csv_data = []
    csv_headers = [
        'GroupID', 'Brand', 'Current_Price', 'Cost', 'Min_Price', 'Lowbench',
        'Steady_Price', 'Profit_Price', 'Clearance_Price',
        'Annual_Profit', 'Sold_Qty', 'Avg_Profit_Per_Unit', 'Margin_Pct',
        'Steady_Change', 'Profit_Change', 'Clearance_Change',
        'Steady_Change_Pct', 'Profit_Change_Pct', 'Clearance_Change_Pct'
    ]
    
    processed_count = 0
    error_count = 0
    
    for sku in sku_data:
        groupid, brand, annual_profit, sold_qty, avg_profit_per_unit, margin_pct, cost, current_price, lowbench = sku
        
        try:
            # Convert to float for calculations
            cost = float(cost) if cost is not None else 0.0
            current_price = float(current_price) if current_price is not None else 0.0
            lowbench = float(lowbench) if lowbench is not None else None
            min_price = cost * 1.10  # 10% minimum margin
            
            # Get recommendations for each mode
            recommendations = {}
            for mode in PRICING_MODES:
                try:
                    price = get_price_recommendation(groupid, mode)
                    recommendations[mode] = price
                except Exception as e:
                    log(f"ERROR getting {mode} recommendation for {groupid}: {str(e)}")
                    recommendations[mode] = None
            
            # Calculate price changes
            steady_change = recommendations['Steady'] - current_price if recommendations['Steady'] else None
            profit_change = recommendations['Profit'] - current_price if recommendations['Profit'] else None
            clearance_change = recommendations['Clearance'] - current_price if recommendations['Clearance'] else None
            
            # Calculate percentage changes
            steady_change_pct = (steady_change / current_price * 100) if steady_change and current_price > 0 else None
            profit_change_pct = (profit_change / current_price * 100) if profit_change and current_price > 0 else None
            clearance_change_pct = (clearance_change / current_price * 100) if clearance_change and current_price > 0 else None
            
            # Build CSV row
            row = [
                groupid,
                brand or '',
                f"{current_price:.2f}" if current_price else '',
                f"{cost:.2f}" if cost else '',
                f"{min_price:.2f}" if min_price else '',
                f"{lowbench:.2f}" if lowbench else '',
                f"{recommendations['Steady']:.2f}" if recommendations['Steady'] else '',
                f"{recommendations['Profit']:.2f}" if recommendations['Profit'] else '',
                f"{recommendations['Clearance']:.2f}" if recommendations['Clearance'] else '',
                f"{annual_profit:.2f}" if annual_profit else '',
                str(sold_qty) if sold_qty else '',
                f"{avg_profit_per_unit:.2f}" if avg_profit_per_unit else '',
                f"{margin_pct:.1f}%" if margin_pct else '',
                f"{steady_change:+.2f}" if steady_change else '',
                f"{profit_change:+.2f}" if profit_change else '',
                f"{clearance_change:+.2f}" if clearance_change else '',
                f"{steady_change_pct:+.1f}%" if steady_change_pct else '',
                f"{profit_change_pct:+.1f}%" if profit_change_pct else '',
                f"{clearance_change_pct:+.1f}%" if clearance_change_pct else ''
            ]
            
            csv_data.append(row)
            processed_count += 1
            
            # Log progress every 50 SKUs
            if processed_count % 50 == 0:
                log(f"Processed {processed_count}/{len(sku_data)} SKUs...")
                
        except Exception as e:
            log(f"ERROR processing {groupid}: {str(e)}")
            error_count += 1
            continue
    
    # Generate CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"price_recommendations_{owner_name}_{timestamp}.csv"
    
    csv_content = []
    csv_content.append(','.join(csv_headers))
    for row in csv_data:
        csv_content.append(','.join(str(cell) for cell in row))
    
    csv_text = '\n'.join(csv_content)
    file_path = save_report_file(filename, csv_text)
    
    # Summary
    log(f"=== BULK RECOMMENDATIONS COMPLETED ===")
    log(f"Owner: {owner_name}")
    log(f"Total SKUs: {len(sku_data)}")
    log(f"Successfully processed: {processed_count}")
    log(f"Errors: {error_count}")
    log(f"CSV file saved: {file_path}")
    
    print(f"\nBulk Price Recommendations Complete!")
    print(f"Owner: {owner_name}")
    print(f"SKUs processed: {processed_count}/{len(sku_data)}")
    print(f"CSV file: {file_path}")
    
    if error_count > 0:
        print(f"Errors encountered: {error_count} (see log for details)")
    
    return file_path

def print_summary_stats(owner_name):
    """Print summary statistics for the owner's SKUs"""
    try:
        sku_data = get_owner_skus(owner_name)
        if not sku_data:
            print(f"No SKUs found for owner '{owner_name}'")
            return
        
        total_skus = len(sku_data)
        total_annual_profit = sum(float(sku[2]) for sku in sku_data if sku[2])
        total_sold_qty = sum(int(sku[3]) for sku in sku_data if sku[3])
        
        print(f"\n=== SUMMARY FOR {owner_name} ===")
        print(f"Total SKUs: {total_skus}")
        print(f"Total Annual Profit: £{total_annual_profit:,.2f}")
        print(f"Total Units Sold: {total_sold_qty:,}")
        print(f"Average Profit per SKU: £{total_annual_profit/total_skus:.2f}")
        
    except Exception as e:
        log(f"ERROR generating summary: {str(e)}")
        print(f"Error generating summary: {str(e)}")

# Main execution
if __name__ == "__main__":
    print(f"Bulk Price Recommendations Generator")
    print(f"Target Owner: {OWNER_NAME}")
    print(f"Pricing Modes: {', '.join(PRICING_MODES)}")
    print("=" * 50)
    
    # Show summary first
    print_summary_stats(OWNER_NAME)
    
    # Generate recommendations
    try:
        csv_file = generate_bulk_recommendations(OWNER_NAME)
        if csv_file:
            print(f"\nRecommendations saved to: {csv_file}")
            print("\nCSV Columns:")
            print("- Current_Price: Current Shopify price")
            print("- Steady/Profit/Clearance_Price: Recommended prices for each mode")
            print("- *_Change: Price difference (recommended - current)")
            print("- *_Change_Pct: Percentage change")
            print("- Lowbench: Competitor benchmark price")
            print("- Min_Price: Minimum allowed price (cost + 10%)")
    except Exception as e:
        log(f"FATAL ERROR: {str(e)}")
        print(f"Fatal error: {str(e)}")
