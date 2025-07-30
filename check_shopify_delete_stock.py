#!/usr/bin/env python3
"""
Check UKD stock levels for groupids in shopify-delete.csv
"""

import pandas as pd
import psycopg2
from logging_utils import get_db_config

def main():
    # Read the CSV file
    df = pd.read_csv('shopify-delete.csv')
    groupids = df['groupid'].tolist()

    print(f'Found {len(groupids)} groupids to check')
    print('Checking stock levels in ukdstock table...')

    # Connect to database
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Check stock for each groupid
    results = []
    for groupid in groupids:
        cur.execute('''
            SELECT groupid, SUM(stock) as total_stock
            FROM ukdstock
            WHERE groupid = %s
            GROUP BY groupid
        ''', (groupid,))
        
        stock_data = cur.fetchone()
        if stock_data:
            total_stock = stock_data[1]
            results.append({'groupid': groupid, 'ukd_stock': total_stock})
        else:
            results.append({'groupid': groupid, 'ukd_stock': 0})

    conn.close()

    # Create results dataframe and save
    results_df = pd.DataFrame(results)
    results_df.to_csv('shopify-delete-stock-check.csv', index=False)

    print('\nStock check complete! Results saved to shopify-delete-stock-check.csv')
    print('\nSummary:')
    print(f'Total items: {len(results_df)}')
    
    items_with_stock = results_df[results_df['ukd_stock'] > 0]
    items_no_stock = results_df[results_df['ukd_stock'] == 0]
    
    print(f'Items with stock > 0: {len(items_with_stock)}')
    print(f'Items with no stock: {len(items_no_stock)}')

    # Show items with stock
    if len(items_with_stock) > 0:
        print('\nItems with UKD stock:')
        print('GroupID | UKD Stock')
        print('--------|----------')
        for _, row in items_with_stock.iterrows():
            print(f'{row["groupid"]} | {row["ukd_stock"]}')
    else:
        print('\nNo items have UKD stock.')

if __name__ == "__main__":
    main()
