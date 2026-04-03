# Amazon Pricing — Context

## Status

**Last session (2026-04-03):**
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

Three steps: (1) generate upload file, (2) run `python amz-price/update_amz_price.py` to update DB, (3) user uploads file to Amazon.

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
- Output file: save as `amz-price/AMZ-Price-Upload.txt` (or similar descriptive name).

#### 2. Update amzfeed in the database

After generating the upload file, update `amzfeed.amzprice` to reflect the new prices so that any analysis before the next morning feed refresh uses the correct price:

Run `python amz-price/update_amz_price.py` — it reads `AMZ-Price-Upload.txt` and updates `amzfeed.amzprice` for each SKU in the file.

**Note:** `amzfeed` is refreshed every morning from real Amazon data, so this update is temporary — it just keeps the DB accurate until the next refresh.

#### 3. Log the change

Price changes are logged automatically to the `amz_price_log` table when `update_amz_price.py` runs.

```sql
-- View recent price changes
SELECT log_date, code, old_price, new_price, notes
FROM amz_price_log
ORDER BY id DESC
LIMIT 20
```

**Note:** Pre-2026-04-03 changes were tracked in a markdown table. Historical entries from Mar 16 and Mar 23 sessions are summarised in the Status section above.

## Segments

IVES products are split into two segments (tracked in the Google Sheet segment tracker):

| Segment | Name | Styles | Revenue (12m) | GP (12m) |
|---------|------|--------|---------------|----------|
| IVES-COLOUR | Lunar Ives Colours | 7 | £79,000 | £54,000 |
| IVES-WHITE | Lunar Ives White | 1 | £57,000 | £39,000 |

Segment is stored in `skusummary.segment`. All IVES groupids follow the pattern `FLE030-IVES-*`.

### IVES Product Reference

All variants share: **cost £15.99, RRP £45.00, Shopify price £32.00**

| GroupID | Colour | Segment |
|---------|--------|---------|
| FLE030-IVES-WHITE | White | IVES-WHITE |
| FLE030-IVES-BEIGE | Beige | IVES-COLOUR |
| FLE030-IVES-BLACK | Black | IVES-COLOUR |
| FLE030-IVES-BLACKSOLE | Black (all black sole) | IVES-COLOUR |
| FLE030-IVES-GREY | Grey | IVES-COLOUR |
| FLE030-IVES-MIDBLUE | Blue | IVES-COLOUR |
| FLE030-IVES-NAVY-BLUE | Navy | IVES-COLOUR |
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

## Strategy

- Amazon and Shopify pricing are treated as completely separate — different customer base, different pricing strategy.
- **Priority 1:** Lunar St Ives (FLE030-IVES) is the core Amazon product. Keep it stocked and priced as efficiently as possible.
- **Priority 2:** Expand the range — grow sales on other items beyond IVES. Next candidates: Free Spirit brand, Lunar Charlotte sandals.
- **Price testing:** When sales stall, make a price change and monitor daily sales via the `sales` table to measure impact. Track what price was changed, when, and what happened.
