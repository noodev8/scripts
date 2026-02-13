# Google Price Check Process

## Overview

This process uses Google Merchant Center price benchmark and sale suggestion reports to identify pricing opportunities, then optionally adjusts prices via the existing nightly Shopify sync.

The process is designed to be run manually with gaps between phases. Drop the Google CSV reports into `google_price/` and run the script when needed.

## How It Works (3 Phases)

### Phase 1: Data Report (`google_price_check.py`)
- Parse the Google CSV reports from `google_price/` folder
- Match Google `Product ID` to `skumap.googleid` in the database
- Join to `skusummary` to get current price, cost, RRP, season, margin info
- Aggregate variant-level data to groupid level using click-weighted averages
- Output: `price_report_YYYY-MM-DD.csv` (18 columns, full detail)
- No database changes

### Phase 2: Action Report (`google_price_action.py`)
- Reads the Phase 1 data report CSV
- Fetches guardrail data (cost, tax, rrp, shopifyprice) from `skusummary`
- Calculates target prices based on chosen mode:
  - **Grow** (default): Target = Google's suggested sale price (click-uplift-weighted). Falls back to benchmark avg if no suggestion. Only recommends **price decreases**.
  - **Protect** (`--protect`): Target = benchmark avg. Only recommends **price increases**.
- Applies guardrails: 10% min margin above cost (VAT-adjusted), RRP ceiling, round to 2dp
- Filters to actionable rows only (skips no-data, no-change, wrong direction)
- Output: `price_action_grow_YYYY-MM-DD.csv` or `price_action_protect_YYYY-MM-DD.csv` (10 columns: groupid, brand, title, current_price, new_price, change, change_pct, margin_current, margin_new, source)
- No database changes

### Phase 3: Apply (Future)
- Review the Phase 2 action report and decide which changes to accept
- Update `skusummary.shopifyprice` with the new price
- Set `skusummary.shopifychange = 1` to flag for the nightly sync
- Log the change to `price_change_log` table
- The existing `price_update2.py` nightly cron picks up `shopifychange = 1` and pushes to Shopify + Google Merchant

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
| `reason_code` | e.g. "google_benchmark" or "google_sale_suggestion" |
| `reason_notes` | Details from the Google report |
| `changed_by` | "google_price_check" |
| `channel` | "SHP" |

## Google Report Formats

### Report 1: Price Benchmarks
**Filename pattern**: `Your most popular products with price benchmarks_*.csv`
- 2 header rows before data (title + date range)
- Columns: Title, Brand, Product ID, Your price, Benchmark, Price gap, Clicks
- **Price gap** is negative when your price is below benchmark (room to raise)
- Price gap is positive when you're above benchmark

### Report 2: Sale Price Suggestions
**Filename pattern**: `Sale price suggestions with highest performance impact_*.csv`
- 1 header row before data (title)
- Columns: Product ID, Title, Brand, Category, Your price, Suggested price, Click uplift, Conversion uplift, Effectiveness

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
# 1. Drop Google CSV reports into google_price/ folder, then:
python google_price/google_price_check.py              # Phase 1: Data report (must run first)

# 2. Generate action report (reads Phase 1 output):
python google_price/google_price_action.py             # Phase 2: Grow mode (default) — price decreases
python google_price/google_price_action.py --protect   # Phase 2: Protect mode — price increases

# 3. Phase 3 (apply) not yet implemented
```
