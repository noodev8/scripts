# Product Price Drop Analysis System

**Purpose:** Automated identification and pricing recommendations for stagnant inventory to optimize cash flow and reduce dead stock.

**Start Date:** 2025-06-22

> **Note:** This document explains the SQL logic. For definitive implementation details, refer to `product_price_drop.sql`.

---

## Overview

This system analyzes inventory performance and categorizes products into actionable buckets based on:
- Sales velocity (days since last sale)
- Stock levels
- Market positioning (vs competitor prices)
- Profit margins

Each product receives a bucket classification (1-7) with specific pricing recommendations that never drop below cost.

---

## Data Sources

| Field | Source Table | Description |
|-------|--------------|-------------|
| `groupid` | skusummary | Unique product identifier |
| `shopifyprice` | skusummary | Current retail price |
| `lowbench` | skusummary | Lowest competitor price (Google Shopping) |
| `cost` | skusummary | Internal cost per unit |
| `tax` | skusummary | VAT inclusion flag (1 = includes VAT) |
| `qty` | localstock | Current warehouse stock |
| `solddate` | sales | Most recent sale date per product |

---

## Bucket Classification System

### Priority Buckets (Immediate Action Required)

| Bucket | Category | Criteria | Price Reduction | Safety Floor |
|--------|----------|----------|-----------------|--------------|
| **1** | Dead Stock Deep-Clear | 180+ days no sales AND stock ≥ 10 | 35% off | MAX(new_price, cost + £1) |
| **2** | Market Mismatch | Price ≥ 110% of lowbench AND 30+ days stale | Set to 98% of lowbench | Never below cost |
| **3** | Stock-Heavy, No Benchmark | No lowbench data, stock ≥ 15, 30-179 days stale | 25% off | Never below cost |
| **4** | Low-Margin Risk | Margin < £15 AND 30+ days stale | Set to cost + £0.01 | Cost protection |
| **5** | Slow-Mover, Moderate Stock | Stock 5-14, 60+ days stale, margin ≥ £15 | 15% off or lowbench | MIN(lowbench, 85% price) |

### Monitoring Buckets

| Bucket | Category | Criteria | Action |
|--------|----------|----------|--------|
| **6** | Low-Stock or Recent | Stock ≤ 4 OR sold within 30 days | No price change |
| **7** | Early Warning | Stock ≥ 15, stale 30-59 days, fairly priced | 10% off (preventive) |

---

## Safety Features

- **Cost Protection:** All suggested prices are validated to be ≥ product cost
- **Precision:** All prices rounded to 2 decimal places
- **VAT Handling:** Margin calculations account for VAT-inclusive pricing
- **Never-Sold Handling:** Products with no sales history (9999 days) treated as dead stock

---

## Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `groupid` | VARCHAR | Product identifier |
| `current_price` | NUMERIC | Current Shopify price |
| `lowbench` | NUMERIC | Competitor benchmark price |
| `cost` | NUMERIC | Product cost |
| `stock` | INTEGER | Current inventory level |
| `days_since_last_sold` | INTEGER | Days since last sale (9999 = never) |
| `margin_value` | NUMERIC | Current profit per unit (£) |
| `bucket` | INTEGER | Classification bucket (1-7) |
| `bucket_reason` | TEXT | Human-readable explanation |
| `suggested_price` | NUMERIC | Recommended new price |

---

## Implementation Use Cases

### Automated Processing
- **Python Integration:** Feed bucket 1-5 products into automated price update scripts
- **Batch Processing:** Process all bucket 1-2 items for immediate markdown
- **Logging:** Record all price changes in `price_change_log` table

### Manual Review
- **Daily Dashboard:** Review bucket 1-3 items for manual approval
- **Weekly Analysis:** Monitor bucket 7 items for trend analysis
- **Exception Handling:** Manual override for seasonal or strategic items

### Safety Protocols
- **10-Day Window:** Implement delays for non-urgent buckets (3-7)
- **Approval Workflow:** Require manual confirmation for bucket 1-2 items
- **Rollback Capability:** Maintain price history for quick reversals

