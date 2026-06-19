# Amazon Pricing — The Engine

How Amazon pricing works here, brand-neutral. This doc is the *engine*: the philosophy, the database mechanics, the decision framework, and the rules. It is deliberately free of product specifics — those live in `AMZ_PRODUCTS.md` (the per-segment registry). For the session entry point and the coverage map, see `README.md`. For the comprehensive single-segment pass, see `AMZ_FULL_REVIEW.md`.

> **Scope:** any brand/segment we sell on Amazon. Nothing here is IVES-only. Where a rule needs a number (a floor, a ceiling, a step), read it from the segment's row in `AMZ_PRODUCTS.md` — don't hardcode IVES figures onto another segment.

## Philosophy

- **Price follows performance, continuously.** Drop when sales slow, creep up when sales are strong — always hunting the best profit at a sustainable velocity. There is no "done".
- **Always consider both directions.** When reviewing a segment, look for creeps up on strong sellers (high velocity, low returns) as much as drops on stale stock. Don't default to only cutting.
- **Per-size, always.** On Amazon each size is its own SKU with its own price. A groupid can look healthy overall while individual sizes are dead. Break sales / returns / last-sold / stock down per size before deciding. Different sizes routinely need different prices.
- **Small drops matter.** A sub-£1 cut can dramatically change velocity (IVES went ~1/week at £39.99 → 3 sales in 3 hours at £38.50). A move doesn't need to be large to bite.
- **Don't sit and watch a decline.** If weekly velocity halves, act — test a lower price. Holding price while sales disappear loses more than testing down.
- **Each segment proves its own velocity.** Don't assume a flywheel from one product transfers to another just because both are on FBA (see UKD-SEG / M968BC in the registry). Sustained stock alone is not proof of demand.

## Database

### Sales (channel = 'AMZ')

```sql
SELECT solddate, ordernum, code, groupid, productname, brand,
       qty, soldprice, profit, discount
FROM sales
WHERE channel = 'AMZ'
  AND solddate >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY solddate DESC, ordernum;
```

| Column | Notes |
|--------|-------|
| code | SKU (includes size) |
| groupid | Product group (no size) |
| qty | Negative = return |
| soldprice | Sale price (0 on returns) |
| profit | Negative on returns |
| discount | % off reference price; null on returns |
| brand | Brand — use to scope by brand |
| paytype / collectedvat | Null for AMZ — ignore |

### Weekly velocity (spotting slowdowns under healthy-looking totals)

```sql
SELECT date_trunc('week', solddate)::date AS week_start,
       SUM(CASE WHEN qty>0 THEN qty ELSE 0 END) AS units_sold,
       SUM(CASE WHEN qty<0 THEN ABS(qty) ELSE 0 END) AS returns,
       ROUND(AVG(CASE WHEN qty>0 THEN soldprice END)::numeric,2) AS avg_sold_price,
       ROUND(SUM(profit)::numeric,2) AS profit
FROM sales
WHERE channel='AMZ' AND groupid = '{GROUPID}'
  AND solddate >= CURRENT_DATE - INTERVAL '8 weeks'
GROUP BY 1 ORDER BY 1 DESC;
```

Then cross-reference `amzfeed.amzprice` (current listing price) against what it was actually selling at.

### Stock & current price — `amzfeed` (FBA only)

**Only FBA stock matters for Amazon pricing.** Local/warehouse stock is irrelevant.

```sql
SELECT code, sku, amzprice, fbafee, amzlive, amztotal, amzsold7
FROM amzfeed
WHERE groupid = '{GROUPID}'
ORDER BY code;
```

| Column | Notes |
|--------|-------|
| sku | **Amazon SKU** — use this for the upload file, NOT our `code` (they differ, e.g. `FLE030-IVES-WHITE-05` → `AD-0XF8D-48L`) |
| code | Our SKU |
| amzprice | **Our current Amazon listing price** |
| fbafee | FBA fulfilment fee per unit |
| amzlive | **FBA stock available to sell** |
| amztotal | Total FBA stock (inc. inbound); `amztotal − amzlive` = inbound |
| amzsold7 | Sold last 7 days |

### Fields to ignore

- `amzfeed.buybox` — not maintained, always 0.00.
- `amzfeed.amzsoldprice` / `amzsolddate` — unreliable when null; use the `sales` table for last sold price/date.
- `price_track` table — **Shopify only.** Never use for Amazon analysis.

## Pricing decision framework

When sales slow on an item:

1. **Don't assume price isn't the problem.** Even if the slowdown began at the same price, the market may have moved (competitors dropped, new sellers appeared). A price test is the right response.
2. **Use profit-per-unit to set boundaries, not to pick the price.** Compute the floor (cost + FBA fee + minimum acceptable margin) from the segment's economics in the registry, then test within the range above it. Profit-per-unit tells you where you *can't* go, not where you *should*.
3. **Monitor after every change.** Check daily sales for the first few days after a change. If velocity doesn't improve, consider a further move.
4. **Step up on the price-held signal, not a clock.** Amazon is a fast market — competing engines reprice hourly. On a winning, well-stocked SKU the confirmation to creep again is simply that the *current* (just-raised) price is selling: a few units at the new price within ~24h = step again, same day if you like. The back-off signal is the *absence* of sales after a creep (a day or two of stall), not elapsed time. There is no mandatory cooling wait between stacked creeps on a deep-stocked winner. (Symmetric: if a creep clearly stalls velocity, back it off — that's a price signal; the clock isn't.)
5. **`£X.49 previously bombed` needs an OOS check.** If a prior price failure coincided with a stockout, it isn't a clean price signal — retest once stock normalises.

## Carry-forward rules

1. **Floors are economic, not cosmetic.** A "tidy" price (e.g. £35.99) is a soft convention, not a wall. The real floor is cost + FBA fee + minimum margin (low-£20s for IVES). For genuinely **dead stock sitting on a pile**, clear aggressively below the tidy number — don't protect a round figure while stock rots. The per-segment floor is in the registry.
2. **Clear dead piles, harvest scarce sellers — even within one colour.** Dead size + stock pile → aggressive clear. Scarce-but-still-selling size → creep UP (harvest margin / slow burn), never dump. The two can coexist in the same groupid.
3. **Don't round-trip.** Don't creep a working size back to the exact price it was deliberately dropped from. "Strong at price" ≠ "under-priced" — a creep needs a distinct justification (supply scarcity, a never-tested band, near-OOS harvest), not just "it's selling."
4. **Supply-tighten posture.** When supply tightens on a SKU/colour, bias creeps **larger on the volume sizes** (they move the burn-rate needle most), not uniformly across the range.
5. **Resistance ceilings are per-segment and discovered, not assumed.** A price that repeatedly stalls velocity is that segment's ceiling — record it in the registry and don't retest it soon after a failure. A segment with no tested ceiling yet has RRP as its only cap; discover its ceiling by creeping until velocity resists.
6. **FBA ≠ FBM competitors.** When competitors undercut on FBM and we're FBA/Prime, that's a different buyer — don't reflexively match down to an FBM price.

## Applying price changes

Two writes per change. **No script to run** — Claude does both at the moment the change is agreed.

1. **Append the row to the upload file** at `%USERPROFILE%\Downloads\AMZ-Price-Upload.txt` (the user uploads it to Seller Central when it suits them). Resolve `%USERPROFILE%` to the current machine — two valid values exist (`C:\Users\aandr\Downloads\...` and `C:\Users\UserPC\Downloads\...`). If the file exists, append; if not, create it with the header. The user deletes it after uploading.

   Tab-separated:
   ```
   sku	price	minimum-seller-allowed-price	maximum-seller-allowed-price
   ```
   - **Use `amzfeed.sku`** (the Amazon SKU), not our `code`.
   - `maximum-seller-allowed-price` = the segment's RRP (from the registry).
   - `minimum-seller-allowed-price` can be left blank.

2. **INSERT into `amz_price_log`** with the rationale in `notes`, at the moment the change is agreed:
   ```sql
   INSERT INTO amz_price_log (code, old_price, new_price, notes)
   VALUES ('FLE030-IVES-WHITE-04', 37.99, 38.29, '30p creep — strongest seller, sold 4u at 37.99 in 24h, 96 live');
   ```
   `log_date` defaults to today. Always capture the reasoning — a colleague (or you in a week) needs the context. Schema: `id, log_date, code, old_price, new_price, notes`.

   ```sql
   -- recent changes
   SELECT log_date, code, old_price, new_price, notes
   FROM amz_price_log ORDER BY id DESC LIMIT 20;
   ```

> **Never update `amzfeed`.** It is refreshed every morning from real Amazon data, so any write is overwritten next day. Only `amz_price_log` gets written. Between a change and the next refresh, in-session queries will see the stale old price on affected SKUs — expected and acceptable. This applies to ad-hoc SQL too: leave `amzfeed` alone.

Once a price is agreed in conversation, apply both writes straight away — don't pause to re-ask "shall I apply it?" The discussion is the decision (the user must still make the call; this only removes the redundant second confirmation).

## Session flow & etiquette

- **Short sessions preferred** — the user usually has limited time. One segment = one clear table + recommendations, then wait for confirmation before moving on. Don't dump all data at once.
- **Lead with the segment summary**, then drill. For a multi-colour/multi-style segment, open with a dashboard (per-colour/style: recent velocity, avg price, stock, one-line status) and ask whether to go item-by-item or batch-apply — don't dump size-level detail across the whole segment in one go.
- **Mind the stock context.** If a large FBA shipment is mid-flow, note it and weigh whether the signals are trustworthy before changing prices — stockouts look exactly like softening velocity.
- **Per-size, never just groupid** — restate from the philosophy because it's the most common mistake.
- **Range vs price are separate jobs.** Finding new colours/styles or dropping lines is not a pricing session — don't mix them in.
- **Mode** (for full reviews): default to **inline-autopilot** — Claude states firm decisions on judgment calls, user batch-approves. Switch to step-through dialog only when the user signals they have time ("let's go one by one"). See `AMZ_FULL_REVIEW.md`.

## When the IVES playbook was the only doc

This engine was distilled from ~3 months of IVES pricing (Mar–Jun 2026), which is why IVES is the most-developed entry in the registry. The mechanics here are general; the IVES-specific numbers (its £40 ceiling, its £35.99-area floor, its WHITE/COLOUR split) now live in `AMZ_PRODUCTS.md` like any other segment's. Pre-2026-04-03 changes predate `amz_price_log` and were tracked in markdown — that history is summarised in the registry, not here.
