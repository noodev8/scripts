# Price Drop Automation System

**Automated price reduction system for stagnant inventory management**

## Overview

This system analyzes your inventory performance and provides automated price drop recommendations and execution. It follows your existing patterns for logging, safety, and API integration.

## System Components

### Core Scripts

1. **`price_drop_automation.py`** - Main automation engine
   - Monitors inventory and applies price changes
   - Configurable safety switches
   - Comprehensive logging

2. **`apply_price_changes.py`** - Manual price application tool
   - Apply individual price changes after review
   - Batch apply by bucket
   - List pending recommendations

3. **`daily_price_report.py`** - Daily report generator
   - Concise daily summaries
   - Priority highlighting
   - Quick action commands

4. **`price_drop_config.py`** - Centralized configuration
   - Safety switches
   - Bucket settings
   - Operational limits

### Supporting Files

- **`performance_reports/product_price_drop.sql`** - Core analysis query
- **`performance_reports/product_price_drop_explanation.md`** - Detailed documentation

## Quick Start

### 1. Initial Setup (Monitor Mode)
```bash
# Generate today's report (safe - no changes)
python daily_price_report.py

# Run analysis in monitor mode (safe - no changes)
python price_drop_automation.py

# List pending recommendations
python apply_price_changes.py --list-pending
```

### 2. Manual Price Changes (After Review)
```bash
# Apply specific price change
python apply_price_changes.py BIRK123 45.99 "Manual review - dead stock"

# Apply all bucket 1 recommendations (dead stock)
python apply_price_changes.py --bucket 1

# Apply all bucket 2 recommendations (market mismatch)
python apply_price_changes.py --bucket 2
```

### 3. Enable Automation (When Ready)
Edit `price_drop_config.py`:
```python
ENABLE_PRICE_DROPS = True        # Master switch
ENABLE_BUCKET_1_AUTO = True      # Dead stock automation
ENABLE_BUCKET_2_AUTO = True      # Market mismatch automation
```

Then run:
```bash
# Apply bucket 1 changes automatically
python price_drop_automation.py --apply-bucket-1

# Apply all enabled buckets automatically  
python price_drop_automation.py --apply-all
```

## Bucket System

### High Priority (Immediate Action)
- **Bucket 1: Dead Stock** - 180+ days no sales, stock ≥ 10 (35% reduction)
- **Bucket 2: Market Mismatch** - Overpriced vs competitors (set to 98% of lowbench)

### Medium Priority (24-48 hour review)
- **Bucket 3: Stock Heavy** - High stock, no benchmark (25% reduction)
- **Bucket 4: Low Margin** - Margin < £15 (set to cost + £0.01)

### Low Priority (Monitor)
- **Bucket 5: Slow Mover** - Moderate stock, stale (15% reduction)
- **Bucket 6: Low Stock/Recent** - No action needed
- **Bucket 7: Early Warning** - Preventive monitoring (10% reduction)

## Safety Features

### Built-in Protections
- **Cost Floor**: No price drops below product cost
- **Recent Change Cooldown**: 7-day exclusion after price changes
- **Daily Limits**: Maximum 50 changes per day
- **Master Switch**: `ENABLE_PRICE_DROPS` must be True
- **Individual Bucket Switches**: Each bucket can be enabled/disabled

### Logging & Tracking
- All changes logged to `price_change_log` database table
- Daily log files: `price_drop_YYYY-MM-DD.log`
- Manual change logs: `price_changes_manual_YYYY-MM-DD.log`
- Automatic log cleanup (7-day retention)

## Recommended Workflow

### Phase 1: Monitoring (Week 1-2)
1. Run `python daily_price_report.py` each morning
2. Review recommendations manually
3. Apply selective changes using `apply_price_changes.py`
4. Build confidence in the system

### Phase 2: Selective Automation (Week 3-4)
1. Enable Bucket 1 automation (dead stock only)
2. Keep Buckets 2-5 as manual review
3. Monitor results and adjust

### Phase 3: Full Automation (Month 2+)
1. Enable Buckets 1-2 for automation
2. Keep Buckets 3-5 as manual review
3. Focus on exception handling

## Daily Operations

### Morning Routine
```bash
# Generate daily report
python daily_price_report.py

# Review high priority items (Buckets 1-3)
python apply_price_changes.py --list-pending

# Apply dead stock changes (if confident)
python apply_price_changes.py --bucket 1
```

### Automated Scheduling (Crontab)
```bash
# Daily report at 8 AM
0 8 * * * cd /scripts && python daily_price_report.py

# Automated processing at 9 AM (when enabled)
0 9 * * * cd /scripts && python price_drop_automation.py --apply-all
```

## Configuration Options

Edit `price_drop_config.py` to adjust:

```python
# Safety limits
MAX_DAILY_CHANGES = 50           # Daily change limit
MIN_PRICE_CHANGE = 0.01          # Minimum change amount
RECENT_CHANGE_COOLDOWN = 7       # Days between changes

# Automation switches
ENABLE_PRICE_DROPS = False       # Master switch
ENABLE_BUCKET_1_AUTO = False     # Individual bucket switches
ENABLE_BUCKET_2_AUTO = False
# ... etc
```

## Integration

### Database Integration
- Uses existing `shopify_api.env` for credentials
- Logs to existing `price_change_log` table
- Integrates with `skusummary`, `sales`, `localstock` tables

### API Integration
- Uses existing Shopify API configuration
- Follows same rate limiting as `price_update.py`
- Same error handling patterns

### Logging Integration
- Matches existing log format from other scripts
- Same retention policy (7 days)
- Consistent timestamp format

## Troubleshooting

### Common Issues
1. **No recommendations**: Check if products have recent price changes
2. **API errors**: Verify `shopify_api.env` credentials
3. **Database errors**: Check database connectivity
4. **Permission errors**: Ensure script has write access for logs

### Log Files to Check
- `price_drop_YYYY-MM-DD.log` - Main automation log
- `price_changes_manual_YYYY-MM-DD.log` - Manual changes log
- `daily_price_report_YYYY-MM-DD.txt` - Daily reports

### Emergency Stop
Set `ENABLE_PRICE_DROPS = False` in `price_drop_config.py` to immediately disable all automation.

## Support Commands

```bash
# View current configuration
python price_drop_config.py

# Show help for any script
python price_drop_automation.py --help
python apply_price_changes.py --help

# Generate report only (no processing)
python price_drop_automation.py --report-only
```
