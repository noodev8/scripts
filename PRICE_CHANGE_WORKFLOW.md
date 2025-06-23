# Brookfield Comfort Price Change Workflow

## Overview
This workflow provides manual approval control over all price changes, combining both price drops and sales burst increases into a single CSV for review and approval.

## Scripts

### 1. `generate_price_change.py`
**Purpose**: Generates a CSV file with all recommended price changes
**Combines**:
- Price drop recommendations (conservative logic)
- Sales burst price increases

**Usage**:
```bash
python generate_price_change.py
```

**Output**:
- CSV file: `price_changes.csv` (overwrites each time)
- Contains all recommendations with empty 'approve' column
- Excludes items with no actual price change

### 2. `apply_price_change.py`
**Purpose**: Applies approved price changes to Shopify, Google, and database
**Requirements**:
- Existing `price_update.py` script (handles Shopify and Google APIs)
- CSV file with approved changes (approve column = '1')

**Usage**:
```bash
python apply_price_change.py [price_changes.csv]
```
(If no filename provided, defaults to `price_changes.csv`)

## Workflow Steps

### Step 1: Generate Recommendations
```bash
python generate_price_change.py
```
This creates `price_changes.csv` with all price change recommendations.

**Note**: Items marked with `ignore_auto_price = 1` in the database will be automatically excluded from recommendations.

### Step 2: Review and Approve
1. Open `price_changes.csv` in Excel or spreadsheet application
2. Review each recommendation:
   - Check current vs suggested price
   - Review the reason/logic
   - Consider stock levels and benchmark prices
3. Choose your action for each item:
   - Enter `1` in the 'approve' column to approve the price change
   - Enter `x` or `X` in the 'approve' column to mark item to ignore future auto pricing
   - Leave blank to skip (no action taken)
4. Save the file

**Ignore Auto Pricing**: When you mark an item with 'x' or 'X', it will:
- Set `ignore_auto_price = 1` in the database for that product
- Exclude the item from all future price change recommendations
- Allow manual price management without automated interference

### Step 3: Apply Changes
```bash
python apply_price_change.py
```
This will:
- Process approved price changes (approve = '1')
- Process ignore flags (approve = 'x' or 'X')
- Update prices in Shopify and Google (via price_update.py)
- Update prices in local database
- Set ignore_auto_price flags in database
- Log all changes to price_change_log table
- Generate results file

## CSV Columns

| Column | Description |
|--------|-------------|
| approve | **Enter '1' to approve, 'x' or 'X' to ignore auto pricing** |
| groupid | Product group ID |
| brand | Product brand |
| current_price | Current selling price |
| suggested_price | Recommended new price |
| change_amount | Price change amount (£) |
| change_percent | Price change percentage |
| change_type | PRICE_DROP or PRICE_INCREASE |
| action | Specific action type |
| reason | Explanation for the change |
| stock | Current stock level |
| days_since_last_sold | Days since last sale (for drops) |
| lowbench | Google benchmark price (if available) |
| cost | Product cost |
| margin_impact | Impact on profit margin |

## Safety Features

### Built-in Protections
- **10-day cooling period**: No changes if price changed in last 10 days
- **Cost floor**: Never price below cost + £0.01
- **RRP ceiling**: Price increases never exceed manufacturer RRP
- **Benchmark protection**: Within 90 days, never go below Google benchmark

### Conservative Logic
- **Maximum 10% reduction** per change for price drops
- **Gentle increases**: 1-5% for sales bursts
- **Stock-aware**: Considers inventory levels
- **Time-sensitive**: Accounts for product aging

## Configuration Requirements

### Database Configuration
Ensure `.env` file contains:
```
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### API Configuration
Ensure your existing `price_update.py` script is properly configured with:
- Shopify API credentials
- Google Merchant Center service account
- All necessary environment files

## Monitoring and Logs

### Log Files
- `logs/generate_price_changes.log` - Generation activity
- `logs/apply_bulk_price_changes.log` - Application activity
- `price_update_results_YYYYMMDD_HHMM.txt` - Results summary

### Database Tracking
All changes are logged in the `price_change_log` table with:
- groupid, old_price, new_price, change_date, reason, change_type

## Migration from Old Scripts

### Scripts to Remove from VPS
- `daily_price_report.py`
- `sales_burst_report.py`
- Any cron jobs running these scripts

### New Local Workflow
1. Run `generate_price_changes.py` locally on Windows
2. Review CSV in Excel
3. Run `apply_bulk_price_changes.py` to apply changes
4. Monitor results and logs

This gives you complete control over the automation process while maintaining all the intelligent pricing logic.
