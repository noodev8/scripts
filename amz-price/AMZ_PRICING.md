# Amazon Pricing — Context

## Quick reference

For a comprehensive pass across all 8 IVES segments in one session, trigger with **"full ives review"** — procedure is in `AMZ_FULL_REVIEW.md`. **Scope: Amazon + IVES only**; other channels/product families are not covered by that procedure. Normal conversational flow (single colour, ad-hoc questions, investigations) works as documented below.

## Status

> Session-by-session journals are **not** kept here — every price change is in the `amz_price_log` DB table with rationale in `notes` (query at the bottom of Database). This section holds only the **current state** and the **durable rules/observations** distilled from past sessions.

### WHITE creeps + £40 lesson (2026-06-11)

Off the May 25 record (132u/£1,960); 6/1 wk 68u, 6/8 wk pacing similar (~run-rate). The **£40 push on 05 backfired** — crossing to 40.09 (6/4 ladder) collapsed velocity, pulled back to 39.69 on 6/8; now settling. Applied **3 creeps**, everything else held:
- **WHITE-06 39.29→39.59** (+30p) — volume monster (22u/7d, 16% ret), deepest pile (107 live +49 inb).
- **WHITE-07 39.40→39.70** (+30p) — 11u/7d, returns settled to **3%** (size-7 fit watch now clean).
- **WHITE-09 38.90→39.20** (+30p) — scarce harvest, 7u/7d on only **5 live** (+9 inb).

Held: 05 (settling post-£40 revert @39.69), 04 (15u/7d but **37% returns** — fit issue, price is fine), 08 (cold @38.49, 0 sold since 6/8 drop), 03 (creep would round-trip to old 39.79 — slowest size, deep stock).

### WHITE step-up (2026-06-02)

WHITE still on a tear — **May 25 wk a fresh record: 132 units, £1,960 profit** (beat the prior ~£1,090 "recovered" peak). Demand is not the constraint; the gate is the price-held signal per size. Stacked another **+20p** on the four sizes that printed sales at their just-raised price: **04→39.09, 05→39.89, 06→39.09, 07→39.20**. Held **03** (£39.29 — slowest, deep stock, don't chase old 39.79) and **08/09** (£38.69 / £38.70 — no sale yet at their 05-31 raised price). All under Shopify £41.10. 07's returns settled to ~7% (14d) so it crept too — but the size-7 fit watch stays open.

### COLOUR review (2026-06-11)

Segment healthy — NAVY (21/7d, £607/14d), BEIGE, BLACKSOLE leading; MIDBLUE soft this week; tails (KHAKI/STONE/RED) ticking; BLACK the exit pile @31.99. Applied **5 creeps + 3 drops**:
- **Creeps (+30p):** NAVY-04→37.99, NAVY-05→39.19, BEIGE-04→37.49, BLACKSOLE-04→37.49, GREY-06→37.79.
- **Drops:** NAVY-03 38.49→37.99 (dead 13d), MIDBLUE-03 37.29→**36.29** (−£1, 0 sales/14d on 21 live; prior drop didn't revive), **BEIGE-05 40.29→39.99** (supplier-harvest stalled to 1/7d above £40 — pulled back under the ceiling).
- **£40 held as a ceiling:** NAVY-06 (39.79) and BEIGE-06 (39.80) sell well but were **held below £40** deliberately (WHITE-05 lesson). BLACKSOLE-05 held at 39.49 (round-trip to the 39.99 it was dropped from).
- **Left running:** BLACK exit @31.99 (~105u, ~8/wk — let run, £29.99 next if you want it gone), GREY-07 @35.49 (low-floor working, don't creep), STONE/KHAKI tail clears.

### COLOUR step-up (2026-06-02)

Broad surge held — **8 of 9 colours up** on the May 25 wk (NAVY 21/£322, MIDBLUE 19/£271, BEIGE 17/£246, GREY 16/£236 the standouts). Applied **6 creeps + a BLACK deeper clear**:
- **Creeps (+20p, price-held signal confirmed):** MIDBLUE-05→38.89, NAVY-05→38.69, GREY-05→38.19, BLACKSOLE-08→38.89 (scarce harvest), NAVY-07→37.19 (scarce harvest), BLACKSOLE-03→36.69 (scarce harvest).
- **BLACK deeper clear:** 04/05/06/08 **35.99→33.99** — the 05-29 clear to 35.99 wasn't moving the ~125-unit pile (~2u/wk). Still ~£12/unit; liberate it. 03/07 nearly gone, left at 35.99.
- **Clears confirmed working — left running:** STONE-04/06 @ 33.99 (04 down to 3 live), KHAKI @ 34.99, GREY-07 @ 35.49.

### Earlier context (carry-forward)

- **WHITE suppression episode (May) RESOLVED and fully recovered.** The May fair-pricing suppression was real (buy box genuinely lost on WHITE); the May 14 −50p across-band recompute trick worked. Recovery was **WHITE-only**; IVES-COLOUR sagged independently in parallel (not a portfolio-wide suspension).
- **BLACK = HARVEST-AND-EXIT** (decided 2026-05-29, deepened 2026-06-02). Velocity collapsed, ~125 units FBA, no reorders. Don't reopen active size-by-size management — just decide clear depth.
- **BEIGE-05 supplier-constrained harvest:** we hold stock early (less competition on this size) → real pricing power above £40. Crept £39.79→40.09→40.29 over late May. Harvest while it sells, pull straight back if it stalls.

### Priority watches (open)

**WHITE (from 2026-06-11):**
- **WHITE-05 (£39.69, settling)** — the engine; pulled back from the failed £40.09 push on 6/8. Let 39.69 re-establish velocity. If it stalls in a few days → 39.49. Big inbound (37) landing, cover fine. **£40 is a confirmed ceiling on this size — don't retest soon.**
- **WHITE-04 (£39.29) — returns watch, NOT price.** 15u/7d but **37% returns/14d**. Selling fine at price; don't creep into the returns. Fit/product issue — watch whether returns ease.
- **WHITE-08 (£38.49) — cold.** Dropped 6/8, 0 sold since. If still dead in a few days, next move is a real drop to ~37.99 (not a nudge).
- **WHITE-06 (£39.59), WHITE-07 (£39.70)** — crept 6/11; confirm the new price keeps selling before stacking again.
- **WHITE-09 (£39.20) — thin.** 5 live +9 inbound; confirm inbound lands before it empties. Harvest creep — fine to keep pushing if it holds.
- **WHITE-03 (£39.29)** — hold; don't chase the old 39.79 (round-trip).

**COLOUR (from 2026-06-11):**
- **Crept this round — confirm the new price sells before stacking:** NAVY-04 (£37.99), NAVY-05 (£39.19), BEIGE-04 (£37.49), BLACKSOLE-04 (£37.49), GREY-06 (£37.79).
- **BEIGE-05 (£39.99)** — pulled back under £40 after stalling at 40.29. Confirm velocity returns at 39.99; if still 1/wk the scarcity-pricing-power story is over, treat as a normal size.
- **MIDBLUE-03 (£36.29)** — deep drop on dead stock; did £1 finally move it? If still 0/wk, it's below the next test too — consider exit.
- **MIDBLUE soft this week** (8/7d vs 24/14d) — watch whether it's a blip or a fade; 05/06 were strong, slowed.
- **£40 ceiling holds:** NAVY-06 (39.79), BEIGE-06 (39.80) — strong sellers held below £40 on purpose. Don't auto-creep over.
- **BLACKSOLE-05 (£39.49)** — held; don't round-trip to the 39.99 it was dropped from.
- **BLACK exit pile (04/05/06/08 @ £31.99, ~105u)** — moving ~8/wk. Let run; £29.99 is the next step if you want it cleared faster.
- **GREY-07 (£35.49) & tail clears (STONE/KHAKI)** — low-floor working; don't creep, keep validating.
- **RED-05 (£35.99)** — deep-stock tail (20 live) gone quiet; revisit if still dead next session.

### Carry-forward rules

1. **The £35.99 "floor" is a soft convention, NOT economic.** Profit ≈ £14/unit at £35.99, still ≈ £12/unit at £33.99 (cost £15.99 + FBA ~£3; breakeven low-£20s). For genuinely **dead stock sitting on a pile**, clear aggressively to £33.99–£34.99. Don't sit on dead stock to protect a tidy number.
2. **Clear dead piles, harvest scarce sellers — even within one colour.** Dead size + stock pile → aggressive clear. Scarce-but-still-selling size → creep UP (harvest margin / slow burn), never dump.
3. **Supplier default: assume IVES colours are out at supplier now but replenishable later.** Don't ask the supplier-status question every colour. Don't fire-sale scarce *sellers*; DO clear genuinely dead piles. User flags individual exceptions.
4. **Don't round-trip.** Don't creep a working size back to the exact price it was deliberately dropped from. "Strong at price" ≠ "under-priced" — a creep needs a distinct justification (supply scarcity, never-touched default, near-OOS harvest), not just "it's selling."

### Observations to carry forward

- **Step up on the price-held signal, not a clock (the gate is "did it sell at the higher price?").** Amazon is a fast market — competing engines reprice hourly. On a **winning, well-stocked** product, the confirmation to creep again is simply that the *current* (just-raised) price is selling: multiple units sold at the new price within ~24h = step up again, same day if you like. Do **not** impose a multi-day cooling wait. The back-off signal is the *absence* of sales at the new price (a day or two of stall after a creep), not elapsed time. Retired the old ">5-day wait between stacked creeps" rule on 2026-05-31 — it was Shopify-brain caution that left margin on the table on a deep-stocked winner that had already sold 3 units at the higher price inside a day. (Still applies in the other direction: if a creep clearly *stalls* velocity, back it off — that's a price signal, the clock isn't.)
- **Supply-tighten posture:** when supply tightens on a single SKU/colour, bias creeps **larger on the volume sizes** (they move the burn-rate needle most), not uniform across the size range.
- **"£X.49 previously bombed" needs an OOS check.** If a prior price failure coincided with a stockout, it's not a clean price signal — retest that price once stock normalises (WHITE-05 £39.49 lesson).
- **Inline-autopilot batch-apply works** for IVES reviews (Claude states all 🟡 calls as firm decisions, user approves as a batch). Calibrated 2026-04-21 at 100% agreement; smoother and faster than per-🟡 dialogue.

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

Two things happen per change:

1. **Claude appends the row to the upload file** at `%USERPROFILE%\Downloads\AMZ-Price-Upload.txt` (for the user to upload to Amazon Seller Central). Use whichever user profile the current session is running under — the user has two machines (usernames `aandr` and `UserPC`) and both Downloads folders are valid.
2. **Claude INSERTs into `amz_price_log` immediately** with the rationale in the `notes` field, at the moment the change is agreed. The user doesn't need to run any script.

The user uploads the file to Seller Central whenever it suits them — the log is already written.

**Important: do NOT update the `amzfeed` table.** `amzfeed` is refreshed every morning from real Amazon data, so any change we make is overwritten the next day — there is no point touching it. Only `amz_price_log` gets written to. This rule also applies to ad-hoc SQL: leave `amzfeed` alone, let the daily refresh handle it. In-session analysis between a price change and the next refresh will see stale prices on the affected SKUs — that's expected and acceptable.

#### Upload file format

**Path: `%USERPROFILE%\Downloads\AMZ-Price-Upload.txt`** — resolve to the current machine's user profile (two valid values exist: `C:\Users\aandr\Downloads\...` and `C:\Users\UserPC\Downloads\...`). If the file exists, append new rows. If it doesn't exist, create it with a header row. The user deletes the file from Downloads after uploading to Amazon Seller Central.

Tab-separated:

```
sku	price	minimum-seller-allowed-price	maximum-seller-allowed-price
```

- **Use `amzfeed.sku`** for the SKU column — this is the Amazon SKU, NOT our `code`. They don't always match (e.g. code `FLE030-IVES-WHITE-05` → sku `AD-0XF8D-48L`).
- `maximum-seller-allowed-price` = RRP (e.g. 45.00 for IVES).
- `minimum-seller-allowed-price` can be left blank.

#### Logging the change

At agreement time, run:

```sql
INSERT INTO amz_price_log (code, old_price, new_price, notes)
VALUES ('FLE030-IVES-WHITE-04', 37.99, 38.29, '30p creep — strongest seller, ...')
```

`log_date` defaults to today. Capture the reasoning from the conversation in `notes` — don't leave it null.

```sql
-- View recent price changes
SELECT log_date, code, old_price, new_price, notes
FROM amz_price_log
ORDER BY id DESC
LIMIT 20
```

**Note:** Pre-2026-04-03 changes were tracked in a markdown table. Historical entries from Mar 16 and Mar 23 sessions are summarised in the Status section above.

## Segments

IVES products use two segments (tracked in the Google Sheet segment tracker).

| Segment | Styles | Notes |
|---------|--------|-------|
| IVES-WHITE | 1 (WHITE) | Standalone. Historically top AMZ seller. |
| IVES-COLOUR | 9 (all other colours) | All non-white colours reviewed together. |

Segment is stored in `skusummary.segment`. All IVES groupids follow the pattern `FLE030-IVES-*`.

Previously (2026-04-11/12) each colour had its own standalone segment. Consolidated back to IVES-COLOUR on 2026-04-21 as the per-colour breakdowns weren't being used.

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

## Session Flow

**Review order when doing a full AMZ pricing session:**

1. **IVES-WHITE** — top priority, always first. Standalone segment, per-size analysis.
2. **IVES-COLOUR** (all 9 non-white colours) — start with a **summary dashboard** showing all colours with key metrics (recent velocity, avg price, total stock, one-line status). Then ask whether to go colour-by-colour or batch-apply. Don't dump all colours with size-level detail in one go.
3. **Other segments** (Charlotte test, Free Spirit, etc.) — only if time allows and user wants them.

**Session etiquette:**
- Short sessions preferred — user has limited time for AMZ reviews.
- Stock context matters: if a large FBA shipment is mid-flow, note it and consider whether signals are trustworthy before making changes. Stockouts look like softening velocity.
- Don't dump all data at once. Each segment = one clear table + recommendations, then wait for confirmation before moving on.
- Price changes are logged to `amz_price_log` by Claude via direct INSERT at the moment they're agreed, with rationale in `notes`. No separate script to run.
- Finding new colours or dropping colours is a separate task from pricing — don't mix them into a pricing session.

## Strategy

- Amazon and Shopify pricing are treated as completely separate — different customer base, different pricing strategy.
- **Priority 1:** Lunar St Ives (FLE030-IVES) is the core Amazon product. Keep it stocked and priced as efficiently as possible.
- **Priority 2:** Expand the range — grow sales on other items beyond IVES. Next candidates: Free Spirit brand, Lunar Charlotte sandals.
- **Price testing:** When sales stall, make a price change and monitor daily sales via the `sales` table to measure impact. Track what price was changed, when, and what happened.
