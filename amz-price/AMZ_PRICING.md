# Amazon Pricing — Context

## Status

**Last session (2026-04-11):**
- IVES-WHITE follow-up. **Key finding: all WHITE sizes had been OOS**, which explains apparent velocity softness since Apr 3 — not a price problem. WHITE-06 (31 FBA) just landed, more inbound across the range.
- Aggregate trend: 40 → 37 → 30 /wk across wc Mar 23/29/Apr 5, avg price £37.85 → £38.12 → £38.06, profit £606 → £553 → £426. Most of the profit drop is stockouts + returns, not creeps breaking.
- 5 changes: creeps on 03/04/05/09, drop on 08.
  - WHITE-03 £38.50→£38.99 (tail size low-risk test)
  - WHITE-04 £37.49→£37.99 (last creep held 7/7d, matches old 06 price)
  - WHITE-05 £38.99→£39.49 (9/7d strong, 60 total stock — £39.99 ceiling established previously so stop there)
  - WHITE-08 £38.50→£37.99 (laggard 1/7d, find range)
  - WHITE-09 £38.50→£38.99 (tail size low-risk test)
- **Held:** WHITE-06 (just restocked, Apr 3 £37.99 creep untested under stock), WHITE-07 (softening, don't compound).
- Next: check creeps in 3–5 days once FBA stock is flowing. Main risk: WHITE-05 at £39.49 — watch closely, pull back to £38.99 if velocity breaks.

**Session (2026-04-03):**
- Full IVES portfolio review — 33 price changes across WHITE + all 9 colours.
- IVES-WHITE velocity sustained: 40/wk. Mar 23 creeps held. Range tightened to £37.49–£38.99.
- IVES-COLOUR: 28 changes. Creeps on strong sellers (BLACKSOLE-06 to £40.99, NAVY/GREY creeps). Aggressive drops on dead stock (NAVY-06 £40.49→£38.99, BLACK-05 £40.49→£38.99, BLACKSOLE/MIDBLUE-07 aggressive drops to find range).
- Key finding: £40+ kills velocity on most sizes — only BLACKSOLE-06 holds above £40.
- Larger FBA shipment in transit, reorder imminent. WHITE 04/06 OOS.
- Stone set to flat £36.99 as baseline for incoming stock.
- Created `amz_price_log` DB table — price changes now logged automatically.
- Next: check creeps hold in a few days, especially the aggressive drops on size 07s.

**Session (2026-03-23):**
- Reviewed all IVES colours one week after the Mar 16 price drops.
- IVES-WHITE exploded: 28 units w/c Mar 16 (up from 1–3/wk). Size 06 at £36.99 did 11 of those — star SKU.
- 17 price changes: 8 creeps up on strong sellers (£0.49–£1.50), 9 drops on dead stock.
- Key creeps: WHITE-06 £36.99→£37.49, NAVY-05 £36.99→£37.49, BLACKSOLE-06 £39.99→£40.49.
- Key drops: WHITE-07 £39.49→£37.99 (13 units dead), BLACKSOLE-04 £38.99→£37.49 (14 units dead).

**Session (2026-03-16):**
- Pulled AMZ sales, confirmed IVES dominates. Chose IVES-WHITE first.
- IVES-WHITE velocity had collapsed (7-9/week → 1-2/week). Dropped from £39.99 to £38.50 — 3 sales in 3 hours.
- Analysed IVES-COLOUR by size across all 9 colours. 28 price changes — drops on stale stock, creeps on strong sellers. Beige held (already healthy), Khaki held (new colour).

## Database

### Sales Query

Amazon sales use `channel = 'AMZ'` in the `sales` table.

```sql
SELECT solddate, ordernum, code, groupid, productname, brand,
       qty, soldprice, collectedvat, profit, discount, paytype
FROM sales
WHERE channel = 'AMZ'
  AND solddate >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY solddate DESC, ordernum
```

### Sales Table Columns

| Column | Type | Notes |
|--------|------|-------|
| id | integer | PK |
| code | varchar | SKU (includes size) |
| solddate | date | |
| groupid | varchar | Product group (no size) |
| ordernum | varchar | Amazon order number |
| ordertime | varchar | |
| qty | integer | Negative = return |
| soldprice | numeric | Sale price (0 on returns) |
| channel | varchar | `AMZ` for Amazon |
| paytype | varchar | Null for AMZ |
| collectedvat | numeric | Null for AMZ |
| productname | varchar | |
| returnsaleid | varchar | |
| brand | varchar | |
| profit | numeric | Negative on returns |
| discount | integer | % discount from reference price; null on returns |

### Amazon Stock & Pricing — amzfeed table

**Only FBA stock matters for Amazon pricing.** Local/warehouse stock is irrelevant here.

```sql
SELECT code, amzprice, fbafee, amzlive, amzsoldprice, amzsolddate
FROM amzfeed
WHERE groupid = '{GROUPID}'
ORDER BY code
```

| Column | Type | Notes |
|--------|------|-------|
| sku | varchar | Amazon SKU |
| fnsku | varchar | FBA identifier |
| groupid | varchar | Product group |
| code | varchar | Our SKU |
| fbafee | varchar | FBA fulfilment fee per unit |
| asin | varchar | Amazon product identifier |
| amzreturn | integer | Returns count |
| amzsold | integer | Total sold |
| amzsoldprice | varchar | Last sold price (ignore if null — use sales table instead) |
| amzsolddate | varchar | Last sold date YYYYMMDD (ignore if null — use sales table instead) |
| amzprice | varchar | **Our current Amazon listing price** |
| amztotal | integer | Total FBA stock (inc. inbound) |
| amzlive | integer | **FBA stock available to sell** |
| amzsold7 | integer | Sold in last 7 days |
| buybox | varchar | **IGNORE — not maintained** |

### Fields to ignore

- `amzfeed.buybox` — not updated, always shows 0.00. Do not use.
- `amzfeed.amzsoldprice` / `amzsolddate` — unreliable when null. Use the `sales` table to determine last sold date and price.
- `price_track` table — **Shopify only.** Do not use for Amazon analysis.

### Analysis Strategy — Detecting Stale Products

When a product looks healthy on surface data (e.g. good 30-day totals), drill into **weekly velocity** to spot slowdowns:

```sql
-- Weekly sales velocity
SELECT
  date_trunc('week', solddate)::date as week_start,
  SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END) as units_sold,
  SUM(CASE WHEN qty < 0 THEN ABS(qty) ELSE 0 END) as returns,
  ROUND(AVG(CASE WHEN qty > 0 THEN soldprice END)::numeric, 2) as avg_sold_price,
  ROUND(SUM(profit)::numeric, 2) as profit
FROM sales
WHERE channel = 'AMZ' AND groupid = '{GROUPID}'
  AND solddate >= CURRENT_DATE - INTERVAL '8 weeks'
GROUP BY date_trunc('week', solddate)
ORDER BY week_start DESC
```

Then cross-reference with `amzfeed.amzprice` to see current listing price vs what it was actually selling at.

**Important: always analyse at SKU (size) level, not just groupid.** On Amazon each size is its own SKU with its own price. A groupid can look healthy overall while individual sizes are dead. Break down sales, returns, last sold date, and stock per size code before making pricing decisions. Different sizes may need different prices.

### Pricing Decision Framework

When sales slow down on an item:

1. **Don't assume price isn't the problem.** Even if the slowdown started at the same price, the market may have moved (competitors dropped, new sellers appeared). A price test is the right response.
2. **Small drops matter on Amazon.** IVES-WHITE went from ~1/week at £39.99 to 3 sales in 3 hours at £38.50 (2026-03-16). A £1.49 drop (~3.7%) was enough to dramatically change velocity. Don't assume a drop needs to be large to have impact.
3. **Use profit per unit to set boundaries, not to decide the price.** Calculate the floor (cost + FBA fee + minimum acceptable margin), then test within the range. For IVES: cost £15.99 + FBA ~£3.03 = £19.02 floor before any margin.
4. **Monitor after every change.** Check daily sales for the first week after a price change. If velocity doesn't improve within a few days, consider a further drop.
5. **Don't sit and watch a decline.** If weekly velocity has dropped meaningfully (e.g. 50%+), act. Holding price while sales disappear loses more money than testing a lower price.
6. **Pricing is continuous.** Drop when sales slow, creep up when sales are strong — always trying to find the best profit at sustainable velocity. There is no "done".
7. **Always consider both directions.** When reviewing a colour/groupid, recommend creeps up on strong sellers (high velocity, low returns) as well as drops on stale stock. Don't default to only dropping prices.

### Applying Price Changes

Two steps: (1) generate upload file, (2) run `python amz-price/update_amz_price.py` to log the changes. The user then uploads the file to Amazon Seller Central.

**Important: do NOT update the `amzfeed` table.** `amzfeed` is refreshed every morning from real Amazon data, so any change we make is overwritten the next day — there is no point touching it. The script only writes to `amz_price_log`. This rule also applies to ad-hoc SQL: leave `amzfeed` alone, let the daily refresh handle it. In-session analysis between a price change and the next refresh will see stale prices on the affected SKUs — that's expected and acceptable.

#### 1. Generate the upload file

**Upload file: `C:\Users\UserPC\Downloads\AMZ-Price-Upload.txt`**. If the file exists, append new rows. If it doesn't exist, create it with a header row. The user deletes the file from Downloads after uploading to Amazon Seller Central.

Format is tab-separated:

```
sku	price	minimum-seller-allowed-price	maximum-seller-allowed-price
```

- **Use `amzfeed.sku`** for the SKU column — this is the Amazon SKU, NOT our `code`. They don't always match (e.g. code `FLE030-IVES-WHITE-05` → sku `AD-0XF8D-48L`).
- `maximum-seller-allowed-price` = RRP (e.g. 45.00 for IVES).
- `minimum-seller-allowed-price` can be left blank.
- The template file contains a sample row — **always remove it** when generating a new file.

#### 2. Log the changes

Run `python amz-price/update_amz_price.py` — it reads `AMZ-Price-Upload.txt` and inserts one row per actual price change into `amz_price_log`. Skips rows where the new price equals the current `amzfeed.amzprice` (idempotent — safe to re-run).

```sql
-- View recent price changes
SELECT log_date, code, old_price, new_price, notes
FROM amz_price_log
ORDER BY id DESC
LIMIT 20
```

The script does not capture reasoning/notes. Backfill notes with a one-shot SQL `UPDATE` after running the script, targeting the most recent NULL-notes row per code.

**Note:** Pre-2026-04-03 changes were tracked in a markdown table. Historical entries from Mar 16 and Mar 23 sessions are summarised in the Status section above.

## Segments

IVES products are split into eight segments (tracked in the Google Sheet segment tracker). Top AMZ performers broken out as standalone segments 2026-04-11/12.

| Segment | Styles | AMZ Rev 12m | AMZ Profit 12m | Notes |
|---------|--------|-------------|----------------|-------|
| IVES-WHITE | 1 (WHITE) | — | — | Standalone. Historically top AMZ seller. |
| IVES-BLACKSOLE | 1 (BLACKSOLE) | £16,907 | £6,103 | Top AMZ colour by units/revenue. Split out 2026-04-11. |
| IVES-NAVY-BLUE | 1 (NAVY-BLUE) | £16,277 | £6,293 | #2 AMZ colour. Split out 2026-04-11. |
| IVES-GREY | 1 (GREY) | £9,657 | £3,309 | Consistent, low returns. Split out 2026-04-12. |
| IVES-BEIGE | 1 (BEIGE) | £10,992 | £4,001 | Highest volume mid-tier. Split out 2026-04-12. |
| IVES-MIDBLUE | 1 (MIDBLUE) | £10,237 | £3,657 | Strong recent velocity. Split out 2026-04-12. |
| IVES-BLACK | 1 (BLACK) | £10,257 | £4,010 | Consistent seller, zero returns. Split out 2026-04-12. |
| IVES-COLOUR | 3 (RED, STONE, KHAKI) | — | — | Tail tier. Batch review. |

Segment is stored in `skusummary.segment`. All IVES groupids follow the pattern `FLE030-IVES-*`.

**Segment strategy:** Segments are "bricks" toward the £1m revenue target. The goal is as many segments as possible each making a decent profit. Top AMZ performers get standalone segments so they can be reviewed and grown individually rather than lost in a batch.

### IVES Product Reference

All variants share: **cost £15.99, RRP £45.00, Shopify price £32.00**

| GroupID | Colour | Segment |
|---------|--------|---------|
| FLE030-IVES-WHITE | White | IVES-WHITE |
| FLE030-IVES-BEIGE | Beige | IVES-BEIGE |
| FLE030-IVES-BLACK | Black | IVES-BLACK |
| FLE030-IVES-BLACKSOLE | Black (all black sole) | IVES-BLACKSOLE |
| FLE030-IVES-GREY | Grey | IVES-GREY |
| FLE030-IVES-MIDBLUE | Blue | IVES-MIDBLUE |
| FLE030-IVES-NAVY-BLUE | Navy | IVES-NAVY-BLUE |
| FLE030-IVES-KHAKI | Green | IVES-COLOUR |
| FLE030-IVES-RED | Red | IVES-COLOUR |
| FLE030-IVES-STONE | Beige | IVES-COLOUR |

## Google Sheets Access

Segment tracker sheet ID: `1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0`

```python
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('merchant-feed-api-462809-23c712978791.json', scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_key('1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0')
```

Service account file: `merchant-feed-api-462809-23c712978791.json` (repo root, gitignored).

## Session Flow

**Review order when doing a full AMZ pricing session:**

1. **IVES-WHITE** — top priority, always first. Standalone segment, per-size analysis.
2. **IVES-BLACKSOLE** — standalone segment, per-size analysis.
3. **IVES-NAVY-BLUE** — standalone segment, per-size analysis.
4. **IVES-GREY** — standalone segment, per-size analysis. Split out 2026-04-12.
5. **IVES-BEIGE** — standalone segment, per-size analysis. Split out 2026-04-12.
6. **IVES-MIDBLUE** — standalone segment, per-size analysis. Split out 2026-04-12.
7. **IVES-BLACK** — standalone segment, per-size analysis. Split out 2026-04-12.
8. **IVES-COLOUR** (batch of 3: RED, STONE, KHAKI) — start with a **summary dashboard** showing all 6 colours with key metrics (recent velocity, avg price, total stock, one-line status). Then ask whether to go colour-by-colour or batch-apply. Don't dump all 6 colours with size-level detail in one go.
5. **Other segments** (Charlotte test, Free Spirit, etc.) — only if time allows and user wants them.

**Session etiquette:**
- Short sessions preferred — user has limited time for AMZ reviews.
- Stock context matters: if a large FBA shipment is mid-flow, note it and consider whether signals are trustworthy before making changes. Stockouts look like softening velocity.
- Don't dump all data at once. Each segment = one clear table + recommendations, then wait for confirmation before moving on.
- Price changes log automatically via `update_amz_price.py` → `amz_price_log`. Backfill notes if the script didn't capture them (common pattern: inline SQL update after the main script).
- Finding new colours or dropping colours is a separate task from pricing — don't mix them into a pricing session.

## Auto-Pricing Plan

See `amz-price/AMZ_AUTO_PRICING_PLAN.md` for the automation roadmap. It captures the decision rules applied during manual sessions and defines the path from manual → dry-run → script → cron. Read it at the start of any pricing session and update the Observations Log after each session.

## Strategy

- Amazon and Shopify pricing are treated as completely separate — different customer base, different pricing strategy.
- **Priority 1:** Lunar St Ives (FLE030-IVES) is the core Amazon product. Keep it stocked and priced as efficiently as possible.
- **Priority 2:** Expand the range — grow sales on other items beyond IVES. Next candidates: Free Spirit brand, Lunar Charlotte sandals.
- **Price testing:** When sales stall, make a price change and monitor daily sales via the `sales` table to measure impact. Track what price was changed, when, and what happened.
