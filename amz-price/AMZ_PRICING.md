# Amazon Pricing — Context

## Quick reference

For a comprehensive pass across all 8 IVES segments in one session, trigger with **"full ives review"** — procedure is in `AMZ_FULL_REVIEW.md`. **Scope: Amazon + IVES only**; other channels/product families are not covered by that procedure. Normal conversational flow (single colour, ad-hoc questions, investigations) works as documented below.

## Status

**Session (2026-04-30) — IVES-COLOUR batch (19 changes: 11 creeps / 6 drops / 2 reverts):**

Followed the WHITE supply-defensive session in the same sitting. No supplier squeeze on COLOUR — standard rules. Batch-apply mode (option 2): inline-autopilot with all 19 calls stated as decisions, user approved as a batch.

**Changes by colour:**

| Colour | # | Changes |
|---------|---|---------|
| BEIGE | 3 | 03 £39.00→£38.00 ↓ (£1 aggressive, 14d+ dead), 06 £39.30→£39.60 ↑, 07 £39.49→£38.99 ↓ |
| BLACK | 1 | 05 £39.29→£39.59 ↑ |
| BLACKSOLE | 3 | 03 £36.99→£36.49 ↓, 04 £37.49→£37.99 ↑, **05 £40.09→£39.79 ↓ (£40 BREACH REVERT — Apr 21 watch fired: 9d, 1 sold, 60% returns)** |
| GREY | 3 | 04 £37.99→£38.49 ↑, 05 £37.49→£37.99 ↑, 06 £36.99→£37.49 ↑ — drops worked, surge wc 4/27 (~24/wk pace) |
| KHAKI | 1 | 05 £38.99→£39.29 ↑ |
| MIDBLUE | 3 | 05 £38.29→£38.59 ↑, 06 £38.50→£38.80 ↑ (7 in 7d strongest signal), **07 £37.79→£37.49 ↓ (stalling-creep revert — 2 in 13d post-creep)** |
| NAVY-BLUE | 2 | 04 £36.99→£37.49 ↑, 07 £36.99→£37.49 ↑ |
| RED | 1 | 04 £36.99→£36.49 ↓ |
| STONE | 2 | 04 £36.99→£35.99 ↓ (to floor), 05 £36.99→£36.49 ↓ |

**🟡 Held this session (9 SKUs — judgment-call holds):**
- **Don't-cross-£40:** BLACK-06 (£39.79), NAVY-06 (£39.79), MIDBLUE-04 (£39.99) — all working at sub-£40 levels, no need to test ceiling
- **Above-£40 already working:** BLACKSOLE-06 at £40.99 (27d, 8 sold post-creep) — 50% returns is small-sample noise, leave it
- **At floor:** BLACK-07, NAVY-09 — drops would breach £35.99
- **Returns small-sample noise:** BEIGE-04, KHAKI-07, STONE-07 — all 50-100% returns on 1-2 events, just settle

**Priority watches for next review (~3-5 days):**
- **GREY-04/05/06 at £38.49/£37.99/£37.49** — three-way creep test on the surging colour. If all hold, GREY is finding its new range.
- **MIDBLUE-06 at £38.80** — strongest creep signal of the batch (7 in 7d). Confirm holds.
- **BLACKSOLE-05 at £39.79** — post-revert recovery test. Should restore £39.79 velocity.
- **MIDBLUE-07 at £37.49** — revert recovery. Should restore prior 5/7d velocity.
- **NAVY-04/07 at £37.49** — matched-pair recovery test (both crept by 50p from £36.99).

**Observation:** Batch-apply with inline decisions for IVES-COLOUR worked smoothly even outside the formal "full ives review" trigger — supports the broader inline-autopilot pattern.

---

**Session (2026-04-30) — IVES-WHITE only, supply-defensive push (6 changes, all creeps / 1 hold):**

**Trigger:** Lunar tightening on White only — 92 backorder delayed 2 weeks, more coming after but pipeline uncertain. User wants creeps biased larger to slow demand without killing momentum.

**Demand context:** 14d units +202% YoY (43 → 130). 7d run-rate 12.5/day vs 14d 9.29/day — still accelerating. Apr 21 creeps every size sold post-creep, including £39+ barrier on size 05.

**Changes (push-harder posture, 50–70p creeps where data supported it, 30p where flagged):**
- WHITE-03 £39.29→£39.79 ↑ (+50p, tail size, 0% returns)
- **WHITE-04 £38.59→£39.29 ↑ (+70p)** — 0 local backup, 16 in 9d. Stock-pressure size, match 06 level
- **WHITE-05 £39.49→£39.99 ↑ (+50p)** — round-number test, **stops short of £40** per user's prior-stall history
- **WHITE-06 £38.59→£39.29 ↑ (+70p)** — the lever. 30 in 9d, 88 FBA, 3% returns
- WHITE-07 £38.80→£39.10 ↑ (+30p, held back due to 23% returns on small sample)
- WHITE-08 £38.49→£38.99 ↑ (+50p, FBA thin)
- WHITE-09 HOLD — 40% returns = fit issue, tail size

**Priority watches for next review (~4-5 days, user wants sooner than 13d):**
- **WHITE-04 and WHITE-06 at £39.29** — matched-pair test on the volume sizes. Both holding = new floor. Split = colour/size demand differential.
- **WHITE-05 at £39.99** — round-number gate. If dead 3-4d, revert to £39.79 (still above prior).
- **WHITE-07 at £39.10** — confirm 23% returns is small-sample noise.

**Observation to carry forward:** When supply tightens on a single SKU/colour, creep posture should bias larger on the volume sizes (they move the burn-rate needle most), not uniform across the size range.

---

**Session (2026-04-21) — FULL IVES REVIEW — inline-autopilot experiment (16 changes, 9 creeps / 6 drops / 1 revert):**

**Experiment:** Ran full review with Claude's 🟡 decisions stated inline as firm calls (not "over to you"). User reviewed independently. **100% agreement — all 16 Claude decisions approved as-is, no adjustments.** First calibration data point.

**Changes by segment:**

| Segment | # | Changes |
|---------|---|---------|
| WHITE | 5 | 03 £38.99→£39.29 ↑, 04 £38.29→£38.59 ↑, 06 £38.29→£38.59 ↑, 07 £38.50→£38.80 ↑, 08 £37.99→£38.49 ↑ (all creeps — WHITE still accelerating, wc 4/13 = 48 units) |
| BEIGE | 1 | 06 £39.00→£39.30 ↑ |
| BLACK | 2 | 04 £37.49→£36.99 ↓ (**stalling-creep revert** — £36.99 sustained 6 in 25d, £37.49 only 1 in 9d), 05 £38.99→£39.29 ↑ |
| BLACKSOLE | 3 | 03 £37.49→£36.99 ↓ (12d dead), 05 £39.79→£40.09 ↑ (**£40 breach test** — strong £39.99 precedent with 14 net-sold Jan-Mar), 07 £37.49→£37.99 ↑ |
| GREY | 1 | 05 £37.99→£37.49 ↓ |
| KHAKI | 2 | 04 £36.99→£36.49 ↓, 07 £38.50→£38.00 ↓ |
| MIDBLUE | 1 | 08 £36.99→£36.49 ↓ |
| NAVY-BLUE | 1 | 03 £38.99→£38.49 ↓ |

**Priority watches for next session (~3-5 days):**
- **BLACKSOLE-05 at £40.09** — £40 breach. Live stock thin (4). If dead in 4d, revert to £39.79. If sells through, investigate re-stocking priority.
- **BLACK-04 at £36.99** — stalling-creep revert. Should restore £36.99 velocity pattern (~1.7/wk historically).
- **WHITE-05 at £39.49** (carried over) — £39+ ceiling retest still running.
- **WHITE all creeps (03/04/06/07/08)** — aggregate segment acceleration, watching whether the whole band can hold £0.30 higher.
- **STONE** — still blocked on stock (04/08 OOS, no inbound).

**Held 🟡 items (9) — worth re-checking next session:**
- MIDBLUE-07, NAVY-05, NAVY-06 — potential stalling-creep but dSC too early (4-9d) and/or preP not actually sustained. Revisit at dSC≥8 with clearer signal.
- WHITE-09, NAVY-09, GREY-08 — tail-size return-rate flags; classed as fit/product issues, not pricing.
- BEIGE-07 — 50% rr on 2 events = noise; price is working.
- KHAKI-08, RED-05 — tail colour/size, just dropped, at/near floor. Re-check in 4-5d.

**Experiment observation:** The inline-autopilot shape (Claude decides everything, user approves batch) was notably faster than the per-🟡 dialogue pattern, and agreement was total. Worth another 2-3 runs before considering any rule changes — 1 data point is not a trend. Classified SKUs split 14 🟢 / 11 🟡 / 31 ⚪.

---

**Session (2026-04-21) — priority-watch follow-up (4 changes, 1 creep / 3 reverts):**

4-day follow-up on 2026-04-17 priority watches. Clean outcomes — two framework-validating results:

- **WHITE-05 £39.19 → £39.49 ↑** — £39+ barrier test **held**. 5 units in 3d at £39.19 (accelerating vs £38.99 run-rate). Retesting prior £39.49 ceiling (was previously bombed during an OOS period, so the ceiling may have been a stock artefact, not a price one). Stock plentiful (68 FBA).
- **MIDBLUE-04 £40.29 → £39.99 ↓** — £40 breakout test **failed** (0 in 4d). Reverted to £39.99 (8 units over 23d sustained).
- **BEIGE-04 £37.79 → £37.49 ↓** — stalling-creep revert. £37.49 had 5 units in 7d pre-creep, £37.79 got 0 in 4d. D3 rule textbook case.
- **NAVY-04 £37.49 → £36.99 ↓** — £37.49 (already itself a revert) not holding either. Market drift down; £36.99 previously sold 3 in 3d.

**Priority watches for next session (~3-5 days):**
- **WHITE-05 at £39.49** — the big one. If it holds this time, the ceiling moves. If dead in 3-4d, back to £39.19.
- **NAVY-04 at £36.99** — if still dead at proven level, the colour has a demand problem, not a price one.
- **BEIGE-04 at £37.49** — confirm revert holds; if it does, that's the clean sustained level.
- **STONE** — still blocked on stock. 04/08 OOS with 0 inbound. Flag when new FBA lands.

**Held:** STONE (all, stock-thin). All other SKUs not on the watch-list were touched on Apr 17 and remain settling.

**Observation to carry forward:** The "£X.49 previously bombed" heuristic needs an OOS-check caveat. WHITE-05's £39.49 in Apr was during a known stockout period — not a clean price signal. When previous price failures coincide with stock issues, retest once stock normalises.

**Session (2026-04-17) — FULL IVES REVIEW (20 changes across all 8 segments, 9 creeps / 11 drops):**

**Hypotheses codified this session:**
- **30p creeps** replace the old 50p default when current price is in the resistance zone (£38.50–£39.00) or when the last move was a successive creep. 50p overshot WHITE-05 at £39.49 (6d follow-up: 0 sales).
- **£40 is not a hard ceiling** on any colour — treat as per-SKU data-driven. MIDBLUE-04 has 8 units sustained at £39.99 over 23 days, crept to £40.29 today to test the boundary.
- **Log hygiene fix:** Claude now INSERTs into `amz_price_log` directly at agreement time (with rationale in `notes`) instead of batch-running a script. `update_amz_price.py` deleted.
- **Phantom Apr 12 log entries** cleaned for BLACKSOLE (8 rows), GREY (8 rows), BEIGE (2 rows) — these were `update_amz_price.py` runs that were never actually uploaded to Amazon. MIDBLUE and BLACK Apr 11 changes WERE uploaded (matched amzfeed).

**Changes by segment:**

| Segment | # | Changes |
|---------|---|---------|
| WHITE | 4 | 04 £37.99→£38.29 ↑, 05 £39.49→£39.19 ↓ (£39 barrier test at 20p above last winning), 06 £37.99→£38.29 ↑, 09 £38.99→£38.50 ↓ |
| BLACKSOLE | 2 | 04 £37.99→£37.49 ↓ (revert failed creep), 05 £39.49→£39.79 ↑ |
| NAVY-BLUE | 2 | 04 £38.49→£37.49 ↓ (**£1 deeper revert** — price-by-price history showed £37.49 was the last sustained price; £37.99 only got 2 hot days then dead), 06 £39.49→£39.79 ↑ |
| GREY | 3 | All drops (04/05 £38.50→£37.99, 06 £37.49→£36.99) — softening trend + Apr 11 planned drops never uploaded |
| BEIGE | 1 | 04 £37.49→£37.79 ↑ (strong signal — 5 sold in 7d at new price) |
| MIDBLUE | 4 | 03 £38.99→£37.99 ↓ (aggressive, 18d dead), **04 £39.99→£40.29 ↑ (£40 breakout test)**, 05 £37.99→£38.29 ↑, 07 £37.49→£37.79 ↑ |
| BLACK | 1 | 06 £39.49→£39.79 ↑ (0 returns across weeks — protect star, single test) |
| IVES-COLOUR | 3 | KHAKI-06 £37.49→£36.49 (29d dead), KHAKI-08 £38.50→£37.49 (23d dead), RED-05 £36.99→£35.99 (25d dead, to floor) |

**Priority watches for next session (~3-5 days):**
- **WHITE-05 at £39.19** — the £39+ barrier test. If dead, drop to £38.99.
- **MIDBLUE-04 at £40.29** — £40 breakout. If dead in 3-4 days, pull back to £39.99.
- **STONE (all 5 SKUs)** — 6 sold in partial week at £36.99 with 0 returns, stock too thin to price up this session. Once stock flows, test £37.49 creep.
- **BEIGE-04 at £37.79** — aggressive profit test, creep again if holds.
- **NAVY-04 at £37.49** — is this the real price? £37.99 broke, watching recovery.

**Held across all segments:** Softening-trend SKUs (WHITE-07), high-return sizing issues (NAVY-08/09, BEIGE-08, MIDBLUE-08 — all 40-67% return rates — product/fit, not price), OOS SKUs (WHITE none, BLACK-03, STONE-04/08, RED-08), already-at-floor SKUs.

**Session stats:** 20 changes, 9 creeps / 11 drops, net price delta −£5.12 across all SKUs (mix of small creeps and bigger aggressive drops on dead stock).

**Session (2026-04-11):**
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
- Observation (not a rule): £40+ felt sensitive on several colours during that session. BLACKSOLE-06 held above £40. Any SKU can be tested above £40 based on its own velocity data — don't treat this as a blanket ceiling.
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
