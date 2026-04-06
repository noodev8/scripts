# Google Price Check Process

## Overview

This process uses two Google Merchant Center reports — the **price benchmark** report and the **sale price suggestions (performance)** report — to identify pricing opportunities, then optionally adjusts prices via the existing nightly Shopify sync.

The process is designed to be run manually with gaps between phases. Download the Google CSVs to your **Downloads folder** — `google_price_check.py` picks them up from there and deletes them after processing.

> **Note (Mar 2026 — updated):** We use both Google reports. The **benchmark** report shows where we sit vs competitors — great for everyday pricing. The **sale price suggestions (performance)** report recommends prices that drive the most sales volume on Google Shopping. It tends to suggest lower prices, so it won't always suit us — but it's valuable when we *want* to ramp sales: high stock levels, end-of-season clearance, or products we want to push. The decision on whether to follow the performance suggestion for a given product is ours to make during review.

## How It Works (3 Phases)

### Phase 1: Data Report (`google_price_check.py`)
- Parse the Google benchmark CSV and sale price suggestions (performance) CSV from the **Downloads folder**
- Performance CSV is optional — report works with benchmark only but has fewer signals
- Match Google `Product ID` to `skumap.googleid` in the database
- Join to `skusummary` for current price, cost, RRP, margin info
- Pull 30-day sales and current stock from database (combined overview)
- Aggregate variant-level data to groupid level using click-weighted averages
- Performance prices weighted by benchmark clicks where available
- Output: `price_report_YYYY-MM-DD.csv` (18 columns):
  - groupid, brand, title, our_price, cost, rrp
  - benchmark_avg, benchmark_min, benchmark_max, benchmark_clicks
  - performance_price, click_uplift, conversion_uplift, effectiveness
  - stock, sold_30d, sizes_in_report, margin_at_current
- No database changes

### Phase 2: Action Report (`google_price_action.py`)
- Reads the Phase 1 data report CSV
- Fetches guardrail data (cost, tax, rrp, shopifyprice) from `skusummary`
- Calculates target prices based on chosen mode:
  - **Grow** (default): Target = benchmark average price. Only recommends **price decreases**. Can also incorporate Google's sale price suggestions for more aggressive pricing.
  - **Protect** (`--protect`): Target = benchmark avg. Only recommends **price increases**.
- Applies guardrails: 10% min margin above cost (VAT-adjusted), RRP ceiling, round to 2dp
- **Auto-decision rules** pre-sort each row into `accept` / `review` / `reject` / `increase`:
  - **Reject**: no stock, or selling well and Google wants an aggressive drop
  - **Increase**: selling well with stock — suggest +5% (capped at RRP)
  - **Accept**: has stock, low/no sales, modest drop (≤15%), AND no proven demand at current price
  - **Accept (performance-supported)**: drops of 15-25% upgraded from review → accept when the performance report independently agrees AND stock ≥ 5 AND not selling
  - **Review**: everything else (large drops, mixed signals, or proven demand — 10+ units sold within 5% of current price in last 365 days)
  - All auto_reason text includes the performance price when available, e.g. `(perf: £58.95)`
  - Rule thresholds are defined at the top of `google_price_action.py` — adjust there as needed
- Filters to actionable rows only (skips no-data, no-change, wrong direction)
- Output: `price_action_grow_YYYY-MM-DD.csv` or `price_action_protect_YYYY-MM-DD.csv` with columns: groupid, auto_decision, auto_reason, change, new_price, description, brand, title, current_price, rrp, performance_price, change_pct, sold_30d, stock, sold_near_price
- No database changes

### Phase 3: Apply (`google_price_apply.py`)
- Review the Phase 2 action report CSV and set `change=1` for rows to accept, `change=0` to skip
- Add notes in the `description` column to record your reasoning
- Run the apply script (dry run by default, `--confirm` to apply)
- Only processes rows where `change=1`
- Guardrail: blocks any price below cost + 10% margin
- Updates `skusummary.shopifyprice` and sets `shopifychange = 1`
- Logs each change to `price_change_log` (reason_code: `google_price`)
- The existing `price_update2.py` nightly cron picks up `shopifychange = 1` and pushes to Shopify + Google Merchant
- Edited CSVs are archived in `shopify-price/archive/` for future pattern analysis

## Key Database Mappings

### Google Report -> Database
```
Google CSV "Product ID"  -->  skumap.googleid
skumap.googleid          -->  skumap.groupid  -->  skusummary.groupid
```

### Relevant skusummary Fields
| Field | Purpose |
|-------|---------|
| `groupid` | Primary key, product group identifier |
| `shopifyprice` | Current Shopify selling price |
| `cost` | Product cost (for margin calculations) |
| `rrp` | Recommended retail price (price ceiling) |
| `tax` | 1 = VAT inclusive (divide by 1.2 for net) |
| `season` | Winter/Summer/Any |
| `shopifychange` | **Set to 1 to trigger nightly price sync** |
| `ignore_auto_price` | 1 = skip auto-pricing for this product |
| `minshopifyprice` | Price floor |
| `maxshopifyprice` | Price ceiling |

### Relevant skumap Fields
| Field | Purpose |
|-------|---------|
| `googleid` | Google Merchant product ID (matches CSV "Product ID") |
| `groupid` | Links variant to product group in skusummary |
| `code` | Internal SKU code |

### Price Change Logging (price_change_log table)
| Field | Purpose |
|-------|---------|
| `groupid` | Product group |
| `old_price` | Price before change |
| `new_price` | Price after change |
| `change_date` | Date of change |
| `reason_code` | `google_price` |
| `reason_notes` | Description/notes from the action report |
| `changed_by` | `google_price_action` |
| `channel` | "SHP" |

## Google Report Format

### Price Benchmarks
**Filename pattern**: `Your most popular products with price benchmarks_*.csv`
- 2 header rows before data (title + date range)
- Columns: Title, Brand, Product ID, Your price, Benchmark, Price gap, Clicks
- **Price gap** is negative when your price is below benchmark (room to raise)
- Price gap is positive when you're above benchmark

### Sale Price Suggestions (Performance Report)
**Filename pattern**: `Sale price suggestions with highest performance impact_*.csv`
- Google's recommendation for prices that maximise sales volume/clicks
- Tends to suggest lower prices — useful when we want to ramp sales (high stock, end-of-season, clearance)
- May drop below our ideal margin sweet spot — the decision to follow or ignore each suggestion is made during human review
- Download this alongside the benchmark report each time

## Existing Nightly Sync (price_update2.py)
- Runs as cron job
- Picks up all products where `skusummary.shopifychange = 1`
- Updates Shopify variant prices via GraphQL API
- Generates Google Merchant supplemental feed via SFTP
- Resets `shopifychange = 0` after successful update

## Safety Rules
- Never price below `skusummary.cost` + 10% margin
- Respect `skusummary.minshopifyprice` floor
- Respect `skusummary.maxshopifyprice` / `rrp` ceiling
- Skip products with `ignore_auto_price = 1`
- All changes logged to `price_change_log`

## How to Run
```
# 1. Drop both Google CSVs (benchmark + sale price suggestions) into shopify-price/ folder, then:
python shopify-price/google_price_check.py              # Phase 1: Data report (must run first)

# 2. Generate action report (reads Phase 1 output):
python shopify-price/google_price_action.py             # Phase 2: Grow mode (default) — price decreases
python shopify-price/google_price_action.py --protect   # Phase 2: Protect mode — price increases

# 3. Review the action report CSV — set change=1 to accept, change=0 to skip, add notes in description
# 4. Apply changes:
python shopify-price/google_price_apply.py shopify-price/price_action_grow_YYYY-MM-DD.csv            # Dry run (review only)
python shopify-price/google_price_apply.py shopify-price/price_action_grow_YYYY-MM-DD.csv --confirm  # Apply to database
```
