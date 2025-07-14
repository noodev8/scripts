#!/usr/bin/env python3
"""
Price Recommendation Engine
Generates optimal price recommendations for individual SKUs based on historical sales data and pricing strategy modes.

OBJECTIVE: Build a modular price recommendation engine that analyzes historical sales performance
by price point to determine optimal pricing for individual SKUs.

NEW LOGIC (Applied before mode logic):
1. IF next review date is available and not yet arrived → do nothing (return None)
2. IF no stock available in localstock table → do nothing (return None)
3. IF not sold in over 3 weeks → Drop by 5% as long as new price is more than 110% of cost price
   - SEASONAL LOGIC: For out-of-season items, apply smaller 2% reduction instead of 5%

MODES (Applied only if new logic conditions not met):
- Ignore: Return None immediately
- Steady: Find price with highest average daily gross profit
- Profit: Apply 2% uplift to Steady mode price
- Clearance: Find price with highest average units/day, with floor constraints

CONSTRAINTS:
- Never price below cost * 1.10 (10% minimum margin)
- All prices rounded to 2 decimal places
"""

import psycopg2
import pandas as pd
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "price_recommendation"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Configuration
PROFIT_MODE_UPLIFT = 0.02  # 2% uplift for Profit mode
CLEARANCE_REDUCTION = 0.05  # 5% reduction for Clearance mode when no sales history
MINIMUM_MARGIN_MULTIPLIER = 1.10  # Cost * 1.10 minimum price floor

def get_price_recommendation(groupid, mode=None, db_config=None, skip_review_date_check=False):
    """
    Generate optimal price recommendation for a SKU based on historical sales data and pricing strategy.

    NEW LOGIC:
    1. IF next review date is available and not yet arrived → do nothing (return None) [unless skip_review_date_check=True]
    2. IF no stock available in localstock table → do nothing (return None)
    3. IF not sold in over 3 weeks → Drop by 5% as long as new price is more than 110% of cost price
       - SEASONAL LOGIC: For out-of-season items, be more conservative with price drops (2% reduction)
    4. Otherwise, use existing mode logic

    Args:
        groupid (str): SKU identifier from skusummary table
        mode (str, optional): One of "Ignore", "Steady", "Profit", "Clearance" (case-sensitive)
                             Defaults to "Steady" if not provided
        db_config (dict, optional): Database connection parameters (if None, load from .env file)
        skip_review_date_check (bool, optional): If True, skip the next review date check
                                               Used for bulk updates to always calculate prices

    Returns:
        float: Recommended price rounded to 2 decimal places
        None: If mode is "Ignore", if groupid not found, or if next review date not yet arrived (when skip_review_date_check=False)

    Raises:
        ValueError: If mode is invalid
        Exception: For database connection issues or missing cost data
    """

    # Default to Steady mode if not provided
    if mode is None:
        mode = "Steady"
        log(f"No mode provided, defaulting to 'Steady' mode")

    # Validate mode
    valid_modes = ["Ignore", "Steady", "Profit", "Clearance"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Valid options: {', '.join(valid_modes)}")

    log(f"Price recommendation request - GroupID: {groupid}, Mode: {mode}")

    # Handle Ignore mode immediately
    if mode == "Ignore":
        log(f"Mode is 'Ignore' - returning None for {groupid}")
        return None

    conn = None
    try:
        # Get database connection
        if db_config is None:
            db_config = get_db_config()

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # STEP 1: Check if next review date exists and hasn't arrived yet (unless skipping this check)
        if not skip_review_date_check:
            cur.execute("""
                SELECT next_review_date
                FROM groupid_performance
                WHERE groupid = %s
            """, (groupid,))

            review_data = cur.fetchone()
            if review_data and review_data[0] is not None:
                next_review_date = review_data[0]
                from datetime import date
                if next_review_date > date.today():
                    log(f"Next review date ({next_review_date}) not yet arrived for {groupid} - no action needed")
                    return None

        # Get SKU basic data (cost, current price, and season)
        cur.execute("""
            SELECT cost::NUMERIC, shopifyprice::NUMERIC, season
            FROM skusummary
            WHERE groupid = %s
        """, (groupid,))

        sku_data = cur.fetchone()
        if not sku_data:
            log(f"WARNING: GroupID '{groupid}' not found in skusummary table")
            return None

        cost, current_price, season = sku_data
        if cost is None or cost <= 0:
            log(f"ERROR: Invalid or missing cost data for {groupid}")
            raise Exception(f"Invalid cost data for GroupID {groupid}")

        # Convert Decimal to float for calculations
        cost = float(cost)
        current_price = float(current_price) if current_price is not None else 0.0
        minimum_price = cost * MINIMUM_MARGIN_MULTIPLIER

        # Determine if item is out of season
        is_out_of_season = _is_out_of_season(season)
        season_status = "out-of-season" if is_out_of_season else "in-season"

        log(f"SKU data - Cost: £{cost:.2f}, Current Price: £{current_price:.2f}, Min Price: £{minimum_price:.2f}, Season: {season} ({season_status})")

        # STEP 2: Check stock levels - only adjust price if we have stock
        cur.execute("""
            SELECT COALESCE(SUM(qty), 0) as total_stock
            FROM localstock
            WHERE groupid = %s
                AND deleted IS DISTINCT FROM 1
        """, (groupid,))

        stock_data = cur.fetchone()
        total_stock = stock_data[0] if stock_data else 0

        if total_stock <= 0:
            log(f"No stock available for {groupid} (total stock: {total_stock}) - no price adjustment needed")
            return None

        log(f"Stock check passed - {total_stock} units in stock for {groupid}")

        # STEP 3: Check if no sales in over 3 weeks (21 days)
        cur.execute("""
            SELECT COUNT(*)
            FROM sales
            WHERE groupid = %s
                AND solddate >= CURRENT_DATE - INTERVAL '21 days'
                AND qty > 0
        """, (groupid,))

        recent_sales_count = cur.fetchone()[0]

        if recent_sales_count == 0:
            # No sales in 3 weeks - apply seasonal logic for price reduction
            if is_out_of_season:
                # For out-of-season items, be more conservative - only reduce if significantly above minimum
                conservative_threshold = minimum_price * 1.25  # 25% above minimum
                if current_price > conservative_threshold:
                    reduced_price = current_price * 0.98  # Smaller 2% reduction for out-of-season
                    reduced_price = max(reduced_price, minimum_price)
                    log(f"No sales in 3+ weeks for {groupid} (out-of-season {season}) - conservative 2% reduction from £{current_price:.2f} to £{reduced_price:.2f}")
                    return round(reduced_price, 2)
                else:
                    log(f"No sales in 3+ weeks for {groupid} (out-of-season {season}) but price £{current_price:.2f} not significantly above minimum £{minimum_price:.2f} - holding price")
                    return None
            else:
                # For in-season items, apply standard 5% reduction
                reduced_price = current_price * 0.95  # 5% reduction
                if reduced_price >= minimum_price:
                    log(f"No sales in 3+ weeks for {groupid} (in-season {season}) - standard 5% reduction from £{current_price:.2f} to £{reduced_price:.2f}")
                    return round(reduced_price, 2)
                else:
                    log(f"No sales in 3+ weeks for {groupid} (in-season {season}) but 5% reduction (£{reduced_price:.2f}) would go below minimum price (£{minimum_price:.2f}) - no change")
                    return None

        # STEP 4: If we reach here, there have been recent sales, so use existing mode logic
        log(f"Recent sales found for {groupid} ({recent_sales_count} sales in last 21 days) - proceeding with {mode} mode logic")

        # Get historical sales data by price point
        cur.execute("""
            SELECT
                shopify_price AS price,
                SUM(COALESCE(shopify_sales, 0)) AS total_units_sold,
                COUNT(DISTINCT date) AS days_recorded
            FROM price_track
            WHERE groupid = %s
                AND shopify_price IS NOT NULL
                AND shopify_price > 0
            GROUP BY shopify_price
            ORDER BY shopify_price
        """, (groupid,))

        price_history = cur.fetchall()
        log(f"Retrieved {len(price_history)} price points from historical data")

        # Convert to DataFrame for easier analysis
        if price_history:
            df = pd.DataFrame(price_history, columns=['price', 'total_units_sold', 'days_recorded'])
            # Convert price to float and calculate metrics
            df['price'] = df['price'].astype(float)
            df['avg_units_per_day'] = df['total_units_sold'] / df['days_recorded']
            df['margin_per_unit'] = df['price'] - cost
            df['avg_daily_gross_profit'] = df['avg_units_per_day'] * df['margin_per_unit']

            # Filter out negative margins for analysis
            profitable_df = df[df['margin_per_unit'] > 0].copy()
            log(f"Analysis data: {len(df)} total price points, {len(profitable_df)} profitable price points")
        else:
            df = pd.DataFrame()
            profitable_df = pd.DataFrame()
            log("No historical sales data found")

        # Calculate recommendation based on mode
        if mode == "Steady":
            recommendation = _calculate_steady_price(profitable_df, current_price, minimum_price, cost)

        elif mode == "Profit":
            steady_price = _calculate_steady_price(profitable_df, current_price, minimum_price, cost)
            if steady_price is not None:
                recommendation = steady_price * (1 + PROFIT_MODE_UPLIFT)
                recommendation = max(recommendation, minimum_price)  # Enforce minimum
                log(f"Profit mode: Steady price £{steady_price:.2f} + {PROFIT_MODE_UPLIFT*100}% uplift = £{recommendation:.2f}")
            else:
                recommendation = None

        elif mode == "Clearance":
            recommendation = _calculate_clearance_price(df, current_price, minimum_price, cost)

        # Round final recommendation and ensure it's a plain Python float
        if recommendation is not None:
            recommendation = float(round(recommendation, 2))
            log(f"Final recommendation for {groupid}: £{recommendation:.2f}")
        else:
            log(f"No recommendation generated for {groupid}")

        return recommendation
        
    except Exception as e:
        log(f"ERROR: Price recommendation failed for {groupid}: {str(e)}")
        raise
        
    finally:
        if conn:
            cur.close()
            conn.close()

def _is_out_of_season(season):
    """
    Determine if a product is currently out of season based on current date.

    Args:
        season (str): Season from skusummary table ("Winter", "Summer", "Any")

    Returns:
        bool: True if product is out of season, False otherwise
    """
    if season is None or season.upper() == "ANY":
        return False

    from datetime import date
    current_date = date.today()
    current_month = current_date.month

    # Define seasons by month (Northern Hemisphere)
    # Winter: December, January, February (months 12, 1, 2)
    # Summer: June, July, August (months 6, 7, 8)
    # Spring/Autumn are transition periods

    if season.upper() == "WINTER":
        # Winter items are in-season during Dec, Jan, Feb and transition months (Oct, Nov, Mar)
        in_season_months = [10, 11, 12, 1, 2, 3]
        return current_month not in in_season_months

    elif season.upper() == "SUMMER":
        # Summer items are in-season during Jun, Jul, Aug and transition months (Apr, May, Sep)
        in_season_months = [4, 5, 6, 7, 8, 9]
        return current_month not in in_season_months

    # Default to in-season for unknown seasons
    return False

def _calculate_steady_price(profitable_df, current_price, minimum_price, cost):
    """Calculate Steady mode price - highest average daily gross profit"""
    if profitable_df.empty:
        # No sales history - drop price slightly to try and generate a sale
        reduction_price = current_price * 0.98  # 2% reduction
        recommendation = max(reduction_price, minimum_price)
        log(f"Steady mode: No profitable sales history, reducing current price by 2% to £{recommendation:.2f}")
        return recommendation
    
    # Find price with highest average daily gross profit
    best_row = profitable_df.loc[profitable_df['avg_daily_gross_profit'].idxmax()]
    recommendation = float(best_row['price'])

    log(f"Steady mode: Best price £{recommendation:.2f} (avg daily profit: £{best_row['avg_daily_gross_profit']:.2f}, "
        f"avg units/day: {best_row['avg_units_per_day']:.2f})")

    return float(max(recommendation, minimum_price))

def _calculate_clearance_price(df, current_price, minimum_price, cost):
    """Calculate Clearance mode price - highest average units/day with floor constraints"""
    if df.empty:
        # No sales history - apply 5% reduction with floor constraint
        reduction_price = current_price * (1 - CLEARANCE_REDUCTION)
        recommendation = max(reduction_price, minimum_price)
        log(f"Clearance mode: No sales history, reducing current price by {CLEARANCE_REDUCTION*100}% to £{recommendation:.2f}")
        return recommendation
    
    # Find price with highest average units per day
    best_row = df.loc[df['avg_units_per_day'].idxmax()]
    recommendation = float(best_row['price'])

    # Always enforce minimum price floor for clearance
    recommendation = float(max(recommendation, minimum_price))

    log(f"Clearance mode: Best velocity price £{recommendation:.2f} (avg units/day: {best_row['avg_units_per_day']:.2f}, "
        f"total units: {best_row['total_units_sold']:.0f})")

    return recommendation

def update_all_recommended_prices(mode=None, db_config=None, limit=None):
    """
    Calculate and update recommended prices for all SHP channel items in groupid_performance table.

    Args:
        mode (str, optional): One of "Ignore", "Steady", "Profit", "Clearance" (case-sensitive)
                             Defaults to "Steady" if not provided
        db_config (dict, optional): Database connection parameters (if None, load from .env file)
        limit (int, optional): Limit the number of items to process (for testing)

    Returns:
        dict: Summary statistics of the update operation

    Note:
        Only processes items with channel = 'SHP' (Shopify). Amazon items are excluded.
        If no recommendation is generated, uses current shopifyprice from skusummary table.
    """

    # Default to Steady mode if not provided
    if mode is None:
        mode = "Steady"
        log(f"No mode provided for bulk update, defaulting to 'Steady' mode")

    # Validate mode
    valid_modes = ["Ignore", "Steady", "Profit", "Clearance"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Valid options: {', '.join(valid_modes)}")

    log(f"Starting bulk price recommendation update - Mode: {mode}")

    conn = None
    try:
        # Get database connection
        if db_config is None:
            db_config = get_db_config()

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Get all groupids from groupid_performance table (SHP channel only) that exist in skusummary
        if limit:
            cur.execute("""
                SELECT DISTINCT gp.groupid
                FROM groupid_performance gp
                INNER JOIN skusummary ss ON gp.groupid = ss.groupid
                WHERE gp.channel = 'SHP'
                ORDER BY gp.groupid
                LIMIT %s
            """, (limit,))
        else:
            cur.execute("""
                SELECT DISTINCT gp.groupid
                FROM groupid_performance gp
                INNER JOIN skusummary ss ON gp.groupid = ss.groupid
                WHERE gp.channel = 'SHP'
                ORDER BY gp.groupid
            """)

        all_groupids = [row[0] for row in cur.fetchall()]
        total_items = len(all_groupids)

        log(f"Found {total_items} unique SHP groupids (existing in skusummary) to process")

        # Track statistics
        stats = {
            'total_processed': 0,
            'recommendations_generated': 0,
            'current_price_used': 0,
            'no_price_set': 0,
            'errors': 0,
            'mode_used': mode
        }

        # Process each groupid with individual transaction handling
        for i, groupid in enumerate(all_groupids, 1):
            try:
                # Calculate recommended price (skip review date check for bulk updates)
                calculated_recommendation = get_price_recommendation(groupid, mode, db_config, skip_review_date_check=True)
                recommended_price = calculated_recommendation
                price_source = "calculated"

                # If no recommendation, try to use current shopifyprice
                if recommended_price is None:
                    try:
                        cur.execute("""
                            SELECT shopifyprice::NUMERIC
                            FROM skusummary
                            WHERE groupid = %s
                              AND shopifyprice IS NOT NULL
                              AND shopifyprice != ''
                              AND shopifyprice::NUMERIC > 0
                        """, (groupid,))

                        price_data = cur.fetchone()
                        if price_data:
                            current_price = float(price_data[0])
                            recommended_price = current_price
                            price_source = "current_price"
                            log(f"No recommendation for {groupid}, using current shopifyprice: £{current_price:.2f}")
                    except Exception as price_error:
                        log(f"Could not get current price for {groupid}: {str(price_error)} - skipping")
                        stats['errors'] += 1
                        continue

                # Update the groupid_performance table (SHP channel only)
                if recommended_price is not None:
                    cur.execute("""
                        UPDATE groupid_performance
                        SET recommended_price = %s
                        WHERE groupid = %s AND channel = 'SHP'
                    """, (recommended_price, groupid))

                    # Track statistics based on price source
                    if price_source == "calculated":
                        stats['recommendations_generated'] += 1
                        if i % 50 == 0:  # Log progress every 50 items
                            log(f"Progress: {i}/{total_items} - {groupid}: £{recommended_price:.2f} (calculated)")
                    else:
                        stats['current_price_used'] += 1
                        if i % 50 == 0:  # Log progress every 50 items
                            log(f"Progress: {i}/{total_items} - {groupid}: £{recommended_price:.2f} (current price)")
                else:
                    # Set recommended_price to NULL if no recommendation and no current price
                    cur.execute("""
                        UPDATE groupid_performance
                        SET recommended_price = NULL
                        WHERE groupid = %s AND channel = 'SHP'
                    """, (groupid,))
                    stats['no_price_set'] += 1

                    if i % 50 == 0:  # Log progress every 50 items
                        log(f"Progress: {i}/{total_items} - {groupid}: No price available")

                # Commit after each successful update to avoid transaction rollback issues
                conn.commit()
                stats['total_processed'] += 1

            except Exception as e:
                log(f"ERROR processing {groupid}: {str(e)}")
                # Rollback the failed transaction and continue with next item
                conn.rollback()
                stats['errors'] += 1
                continue

        log(f"Bulk update completed - Processed: {stats['total_processed']}, "
            f"Calculated recommendations: {stats['recommendations_generated']}, "
            f"Current prices used: {stats['current_price_used']}, "
            f"No price set: {stats['no_price_set']}, "
            f"Errors: {stats['errors']}")

        return stats

    except Exception as e:
        if conn:
            conn.rollback()
        log(f"ERROR: Bulk price recommendation update failed: {str(e)}")
        raise

    finally:
        if conn:
            cur.close()
            conn.close()

# Command line usage
if __name__ == "__main__":
    import sys

    # Check if command line arguments provided
    if len(sys.argv) >= 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        print("Price Recommendation Engine")
        print("=" * 50)
        print("Usage:")
        print("  python price_recommendation.py <GROUPID> [MODE]")
        print("  python price_recommendation.py --bulk [MODE] [--auto]")
        print("  python price_recommendation.py  (for interactive mode)")
        print("")
        print("Examples:")
        print("  python price_recommendation.py 0043691-GIZEH          # Uses default Steady mode")
        print("  python price_recommendation.py 0043691-GIZEH Steady")
        print("  python price_recommendation.py 1017723-BEND Profit")
        print("  python price_recommendation.py --bulk Steady          # Bulk update all groupids")
        print("  python price_recommendation.py --bulk --auto          # Auto mode for cron/scripts")
        print("")
        print("Modes: Ignore, Steady, Profit, Clearance (default: Steady)")
        print("")
        print("Bulk Mode:")
        print("  --bulk [MODE] [--auto]  Update recommended_price column for all SHP channel items")
        print("  --auto or --silent      Skip confirmation prompt (for automated execution)")
        sys.exit(0)
    elif len(sys.argv) >= 2 and sys.argv[1] == "--bulk":
        # Bulk update mode
        auto_mode = False
        mode = None

        # Parse arguments for bulk mode
        for arg in sys.argv[2:]:
            if arg == "--auto" or arg == "--silent":
                auto_mode = True
            elif arg in ["Ignore", "Steady", "Profit", "Clearance"]:
                mode = arg
            else:
                print(f"Error: Invalid argument '{arg}' for bulk mode.")
                print("Usage for bulk update:")
                print("  python price_recommendation.py --bulk [MODE] [--auto]")
                print("")
                print("Examples:")
                print("  python price_recommendation.py --bulk          # Uses default Steady mode")
                print("  python price_recommendation.py --bulk Steady")
                print("  python price_recommendation.py --bulk Profit --auto")
                print("  python price_recommendation.py --bulk --auto   # Auto mode with default Steady")
                print("")
                print("Modes: Ignore, Steady, Profit, Clearance (default: Steady)")
                print("Flags: --auto or --silent (skip confirmation prompt)")
                sys.exit(1)

        try:
            display_mode = mode if mode is not None else "Steady (default)"
            print(f"\nStarting bulk price recommendation update in {display_mode} mode...")
            print("This will update the recommended_price column for all SHP channel items in groupid_performance table.")

            # Confirm before proceeding (unless auto mode)
            if not auto_mode:
                confirm = input("\nProceed with bulk update? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("Bulk update cancelled.")
                    sys.exit(0)
            else:
                print("Running in auto mode - proceeding without confirmation...")

            stats = update_all_recommended_prices(mode)

            print(f"\n✓ Bulk update completed successfully!")
            print(f"  Total processed: {stats['total_processed']}")
            print(f"  Calculated recommendations: {stats['recommendations_generated']}")
            print(f"  Current prices used: {stats['current_price_used']}")
            print(f"  No price set: {stats['no_price_set']}")
            print(f"  Errors: {stats['errors']}")
            print(f"  Mode used: {stats['mode_used']}")

        except Exception as e:
            print(f"\n✗ Bulk update failed: {str(e)}")
            sys.exit(1)

    elif len(sys.argv) == 3:
        groupid = sys.argv[1]
        mode = sys.argv[2]
    elif len(sys.argv) == 2:
        # Only groupid provided, use default Steady mode
        groupid = sys.argv[1]
        mode = None  # Will default to Steady in the function
    elif len(sys.argv) == 1:
        # Interactive mode - ask for parameters
        print("Price Recommendation Engine")
        print("=" * 50)
        print("Choose operation:")
        print("1. Single GroupID recommendation")
        print("2. Bulk update all groupids in groupid_performance table")

        operation = input("\nEnter choice (1 or 2): ").strip()

        if operation == "2":
            # Bulk update mode
            print("\nAvailable modes:")
            print("1. Ignore   - Return None immediately")
            print("2. Steady   - Find price with highest average daily gross profit")
            print("3. Profit   - Apply 2% uplift to Steady mode price")
            print("4. Clearance - Find price with highest average units/day")

            mode_input = input("\nEnter mode (Ignore/Steady/Profit/Clearance) [default: Steady]: ").strip()
            if mode_input == "":
                mode = None  # Will default to Steady
            elif mode_input not in ["Ignore", "Steady", "Profit", "Clearance"]:
                print(f"Error: Invalid mode '{mode_input}'. Valid options: Ignore, Steady, Profit, Clearance")
                sys.exit(1)
            else:
                mode = mode_input

            try:
                display_mode = mode if mode is not None else "Steady (default)"
                print(f"\nStarting bulk price recommendation update in {display_mode} mode...")
                print("This will update the recommended_price column for all SHP channel items in groupid_performance table.")

                # Confirm before proceeding
                confirm = input("\nProceed with bulk update? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("Bulk update cancelled.")
                    sys.exit(0)

                stats = update_all_recommended_prices(mode)

                print(f"\n✓ Bulk update completed successfully!")
                print(f"  Total processed: {stats['total_processed']}")
                print(f"  Calculated recommendations: {stats['recommendations_generated']}")
                print(f"  Current prices used: {stats['current_price_used']}")
                print(f"  No price set: {stats['no_price_set']}")
                print(f"  Errors: {stats['errors']}")
                print(f"  Mode used: {stats['mode_used']}")

            except Exception as e:
                print(f"\n✗ Bulk update failed: {str(e)}")
                sys.exit(1)

        elif operation == "1":
            # Single GroupID mode
            groupid = input("Enter GroupID: ").strip()
            if not groupid:
                print("Error: GroupID is required")
                sys.exit(1)

            print("\nAvailable modes:")
            print("1. Ignore   - Return None immediately")
            print("2. Steady   - Find price with highest average daily gross profit")
            print("3. Profit   - Apply 2% uplift to Steady mode price")
            print("4. Clearance - Find price with highest average units/day")

            mode_input = input("\nEnter mode (Ignore/Steady/Profit/Clearance) [default: Steady]: ").strip()
            if mode_input == "":
                mode = None  # Will default to Steady
            elif mode_input not in ["Ignore", "Steady", "Profit", "Clearance"]:
                print(f"Error: Invalid mode '{mode_input}'. Valid options: Ignore, Steady, Profit, Clearance")
                sys.exit(1)
            else:
                mode = mode_input
        else:
            print("Error: Invalid choice. Please enter 1 or 2.")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python price_recommendation.py <GROUPID> [MODE]")
        print("  python price_recommendation.py --bulk [MODE] [--auto]")
        print("  python price_recommendation.py  (for interactive mode)")
        print("")
        print("Examples:")
        print("  python price_recommendation.py 0043691-GIZEH          # Uses default Steady mode")
        print("  python price_recommendation.py 0043691-GIZEH Steady")
        print("  python price_recommendation.py 1017723-BEND Profit")
        print("  python price_recommendation.py --bulk Steady          # Bulk update all groupids")
        print("  python price_recommendation.py --bulk --auto          # Auto mode for cron/scripts")
        print("")
        print("Modes: Ignore, Steady, Profit, Clearance (default: Steady)")
        print("Flags: --auto or --silent (skip confirmation for automated execution)")
        sys.exit(1)

    # Single GroupID processing (if not bulk mode)
    if 'groupid' in locals():
        try:
            display_mode = mode if mode is not None else "Steady (default)"
            print(f"\nProcessing: {groupid} in {display_mode} mode...")
            price = get_price_recommendation(groupid, mode)

            if price is not None:
                print(f"\n✓ Recommendation for {groupid} ({display_mode} mode): £{price:.2f}")
            else:
                print(f"\n• No recommendation for {groupid} ({display_mode} mode)")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            sys.exit(1)
