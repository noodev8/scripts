# Sales Burst Alert System

**Purpose:** Automated detection of underpriced products selling faster than expected, enabling rapid price optimization to maximize profit margins.

**Start Date:** 2025-06-22

---

## System Overview

This system monitors daily sales velocity against historical patterns to identify pricing opportunities. When products sell significantly faster than their recent average, it suggests potential underpricing that should be corrected quickly.

### Key Features
- **Real-time Detection:** Analyzes last 14 days of sales data from `price_track` table
- **Smart Filtering:** Excludes products with recent price changes (7-day cooldown)
- **Priority Ranking:** Assigns status codes based on burst intensity
- **RRP Protection:** Prevents price increases above manufacturer's recommended retail price
- **Rolling Averages:** Uses 3-day historical average for baseline comparison

---

## Data Sources

| Field | Source Table | Description |
|-------|--------------|-------------|
| `groupid` | price_track | Product identifier |
| `date` | price_track | Daily tracking date |
| `shopify_stock` | price_track | Daily stock levels |
| `shopify_sales` | price_track | Daily units sold |
| `shopify_price` | price_track | Daily price point |
| `rrp` | skusummary | Manufacturer's recommended retail price |
| `change_date` | price_change_log | Recent price change dates (exclusion filter) |

---

## Alert Classification System

### High Priority Alerts (Immediate Action)

| Status | Category | Trigger Criteria | Recommended Action | Price Increase |
|--------|----------|------------------|-------------------|----------------|
| **1** | Hot - Major Burst | 5+ units sold in single day | Immediate price increase | +5% (cap at RRP) |
| **2** | Hot - Strong Burst | 3-4 units sold, recent avg < 1 | Same-day price increase | +2% (cap at RRP) |

### Medium Priority Alerts (Monitor/Consider)

| Status | Category | Trigger Criteria | Recommended Action | Price Increase |
|--------|----------|------------------|-------------------|----------------|
| **3** | Medium - Strong | 2 units sold, avg ≤ 0.3 | Review within 24h | +1-2% (cap at RRP) |
| **4** | Medium - Moderate | 2 units sold, avg ≤ 0.5 | Review within 48h | +1% (cap at RRP) |

> **Current Filter:** System shows only Status 1 and 2 for focused daily action.

---

## Detection Logic

### Burst Identification
```
Burst Condition = Daily Sales > (2 × Recent 3-Day Average)
AND Daily Sales ≥ 2 units
```

### Exclusion Rules
- Products with price changes in last 7 days (cooling-off period)
- Products with NULL price data
- Analysis limited to last 14 days of data

### Safety Mechanisms
- **RRP Ceiling:** New price never exceeds manufacturer's RRP
- **Cooldown Period:** 7-day exclusion after any price change
- **Minimum Threshold:** Only considers products selling 2+ units

---

## Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `groupid` | VARCHAR | Product identifier |
| `date` | DATE | Date of sales burst |
| `shopify_sales` | INTEGER | Units sold on burst day |
| `avg_recent_sales` | NUMERIC | 3-day rolling average |
| `shopify_price` | NUMERIC | Current selling price |
| `rrp` | NUMERIC | Maximum allowed price |
| `shopify_stock` | INTEGER | Current stock level |
| `prev_stock` | INTEGER | Previous day's stock |
| `action` | TEXT | Recommended action description |
| `status_code` | INTEGER | Priority level (1-4) |

---

## Implementation Workflows

### Automated Daily Process
1. **Morning Execution:** Run report at 9 AM daily
2. **Priority Processing:** Auto-process Status 1 items (if enabled)
3. **Alert Generation:** Send Status 2 items for manual review
4. **Logging:** Record all price changes in `price_change_log`

### Manual Review Process
1. **Review Report:** Check Status 1-2 items from overnight
2. **Validate Context:** Confirm stock levels and recent trends
3. **Apply Increases:** Update prices within RRP limits
4. **Document Changes:** Log reason and reviewer in database

### Safety Protocols
- **Manual Override:** Always allow manual rejection of suggestions
- **Stock Validation:** Ensure adequate stock before price increases
- **Trend Analysis:** Consider broader market conditions
- **Rollback Capability:** Maintain price history for quick reversals

---

## Price Change Logging

All price adjustments should be recorded using:

```sql
INSERT INTO price_change_log (groupid, old_price, new_price, reason, reviewed_by, change_date)
VALUES ('GROUPID_HERE', 72.00, 75.60, 'Sales Burst - Status 1', 'Andreas', CURRENT_DATE);
```

### Standard Reason Codes
- `'Sales Burst - Status 1'` - Major burst (5+ units)
- `'Sales Burst - Status 2'` - Strong burst (3-4 units)
- `'Sales Burst - Manual'` - Manual decision based on burst data
