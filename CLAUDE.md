# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based e-commerce automation and analytics system for Brookfield Comfort, primarily focused on Shopify store management, price optimization, and inventory tracking. The system includes:

- **Price Recommendation Engine**: Intelligent pricing based on historical sales data and seasonal patterns
- **Order Management**: Shopify order synchronization and pick allocation 
- **Inventory Management**: Stock tracking and Shopify inventory updates
- **Google Merchant Feed**: Automated product feed generation for Google Shopping
- **Analytics Dashboard**: Streamlit-based internal reporting tool

## Common Commands

### Running Scripts
- **Order sync and pick allocation**: `python update_orders2.py` or use `run_update_orders2.bat`
- **Pick allocation only**: `python update_orders2.py --picks` or use `run_picks_only.bat`
- **Price recommendations**: `python price_recommendation.py`
- **Google Merchant feed**: `python merchant_feed.py`
- **Inventory sync**: `python update_shopify_inventory.py`
- **Performance refresh**: `python refresh_groupid_performance.py`

### Dashboard
- **Run Streamlit dashboard**: `streamlit run bc_dashboard/Home.py`

### Database Operations
- **Backup database**: `./pg_backup.sh` (PostgreSQL backup script)
- SQL scripts are located in `database/` directory for various operations

## Architecture & Key Components

### Core Scripts
- **`price_recommendation.py`**: Main pricing engine implementing multiple modes (Steady, Profit, Clearance, Ignore)
- **`update_orders2.py`**: Shopify order synchronization with timezone handling and pick allocation
- **`merchant_feed.py`**: Google Merchant Center feed generation with product categorization
- **`logging_utils.py`**: Centralized logging and database configuration utilities

### Price Recommendation System
The pricing engine uses historical sales data to optimize prices with these modes:
- **Steady** (default): Maximizes average daily gross profit
- **Profit**: Applies 2% uplift to Steady mode recommendations  
- **Clearance**: Maximizes units sold per day
- **Ignore**: No price recommendations

Key constraints: 10% minimum margin above cost, seasonal logic for out-of-season items, respect for RRP limits.

### Database Schema
PostgreSQL database with key tables:
- `skusummary`: Product master data with cost, pricing, seasonality
- `sales`: Historical sales transactions
- `localstock`: Current inventory levels
- `price_track`: Price history and performance tracking
- `groupid_performance`: Performance metrics and review scheduling

### Dashboard Components
Streamlit-based analytics dashboard (`bc_dashboard/`):
- **Home.py**: Main dashboard with overview statistics
- **Shopify_Health_Check.py**: Detailed SKU-level analysis
- **db_utils.py**: Database query utilities for dashboard

### Configuration
- Environment variables stored in `.env` file (not in repository)
- Database configuration loaded via `logging_utils.get_db_config()`
- Shopify API tokens and Google service account credentials required
- UK timezone handling with automatic BST/GMT switching

### Logging
Centralized logging system:
- Logs stored in `logs/` directory
- Archived logs in `archive_logs/` with 1-day retention
- Each script has dedicated log file with timestamp rotation

## Important Implementation Notes

### Seasonal Logic
Products have seasonal attributes (Winter/Summer/Any) affecting pricing strategies:
- Out-of-season items get different price reduction rules
- Stock-aware pricing (in-season requires stock, out-of-season can price without stock)
- Special "90% of RRP" rule for out-of-season items with no stock

### Timezone Handling  
System operates in UK timezone with automatic BST/GMT detection:
- Order timestamps converted to UK time
- Performance calculations respect timezone differences
- Use `logging_utils.get_uk_time()` for consistent timestamps

### Database Connections
All scripts use `logging_utils.get_db_config()` for consistent database configuration. Connection parameters loaded from `.env` file with validation.

### Error Handling
Scripts include comprehensive error handling with detailed logging. Check log files in `logs/` directory for troubleshooting.