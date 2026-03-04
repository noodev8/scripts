# Pricing Review — Unsegmented Items (Mar 2026)

**Date:** 2026-03-04
**Context:** Investigated all unsegmented groupids with stock to assess a blanket 10% price drop.
**Finding:** A blanket 10% drop is not appropriate. Items need different treatment by category.

---

## Segment Changes Made

- **MAYARI segment created** (5 groupids) — slots in 3rd best GP/unit across all Birkenstock segments at 14.49/unit. Above Gizeh (13.23) and both Arizona BF segments (7-9).
- Dead Mayari Browns (1029726, 1029811) left unsegmented — 22 units, 0 GP, dead stock.

---

## Items Resolved

| GroupID | Brand | Action | Reasoning |
|---------|-------|--------|-----------|
| Crocs 10001-001 | Crocs | Removed | Low margin, barely above cost |
| SHAKE-II-BLACK | Hotter | Do not restock | 9.62 GP/unit looks OK on paper but after FBA fees, packing, shipping and cash tied up on slow lead time, net profit is zero or negative |
| B710AP | Goor | Leave as is | UKD drop-ship, 25.50, sells ~165 units/year steadily. Quiet earner with no stock risk. Dont drop price. |
| M968BC | Goor | Leave as is | Same UKD setup, no stock, no harm |

---

## Blocked from 10% Drop (already at or below minimum margin)

These items CANNOT be dropped 10% — the guardrail (cost + 10%) blocks it. Some are already priced below minimum margin.

| GroupID | Brand | Current | Min Price | Stock | Notes |
|---------|-------|--------:|----------:|------:|-------|
| 1029671-PASADENA | Birkenstock | 70.00 | 71.04 | 11 | BELOW MIN MARGIN. Cost 64.58. Want gone — sell at whatever clears them. |
| 1030906-PASADENA | Birkenstock | 70.00 | 71.04 | 9 | Same. 20 Pasadena units total tying up ~1,300 in cash. |
| 1025583-UPPSALA | Birkenstock | 90.00 | 82.50 | 1 | Cost 75. At least sold 16 units at discount. 1 left, just shift it. |
| 1013070-ARIZONA | Birkenstock | 40.00 | 41.25 | 28 | BELOW MIN MARGIN. 28 units of dead stock. Needs price RAISED to 42+ or cleared. |
| 1027723-ARIZONA | Birkenstock | 40.00 | 38.96 | 7 | Near floor. Only 1 sale in 12m. |
| 1019115-ARIZONA | Birkenstock | 41.01 | 41.25 | 1 | Below min margin. 1 unit, just sell. |

---

## Leave Alone

| Category | Items | Reasoning |
|----------|------:|-----------|
| Socks | ~8 groupids | Tiny margins, tiny prices. 10% off a 12 item gains nothing. Leave as they are. |

---

## New Lunar Stock (not dead)

| GroupID | Brand | Stock | Notes |
|---------|-------|------:|-------|
| JLD102-JADEN-NAVY | Lunar | 12 | Just arrived. Fresh for spring. Do not discount. |
| JLD102-JADEN-WHITE | Lunar | 12 | Just arrived. Fresh for spring. Do not discount. |
| JLH356-DEANNAII-WT | Lunar | 12 | Check if new stock — may be same situation as Jaden |
| JLH587-JULES-BK | Lunar | 12 | Check if new stock — may be same situation as Jaden |
| JLH523-PARADISE-BK | Lunar | 12 | Check if new stock — may be same situation as Jaden |
| JLH331-MARIELLA-WHITE | Lunar | 5 | Check if new stock |
| FLN002-NATASHA | Lunar | 5 | Check if new stock |
| FLN038-ESTHER-BK | Lunar | 3 | Check if new stock |

---

## OK to Drop 10% (remaining unsegmented with stock)

These pass the margin guardrail and are not special cases. Mostly unsegmented Birkenstock (Madrid, Arizona variants) and misc brands. A 10% drop could help move stock ahead of spring.

**To apply:** Use the existing google_price_apply.py process:
1. Generate a CSV with groupid, new_price, description, change=1
2. Dry run: `python google_price/google_price_apply.py <csv> `
3. Apply: `python google_price/google_price_apply.py <csv> --confirm`
4. Nightly cron pushes to Shopify + Google Merchant

---

## How to Change Prices

Prices flow through the database:

1. Update `skusummary.shopifyprice` to the new price
2. Set `skusummary.shopifychange = 1`
3. Nightly cron (`price_update2.py`) pushes to Shopify and Google Merchant
4. Changes logged to `price_change_log`

**Guardrails (enforced by scripts):**
- Never below cost + 10% margin (`cost * 1.10`)
- Respect `minshopifyprice` floor
- Respect `maxshopifyprice` / `rrp` ceiling
- Skip items with `ignore_auto_price = 1`

**Quick segment query:**
```sql
SELECT s.groupid, s.colour, s.width, s.cost, s.rrp, s.shopifyprice,
       COALESCE(SUM(ls.qty), 0) AS stock
FROM skusummary s
LEFT JOIN localstock ls ON ls.groupid = s.groupid AND ls.deleted = 0
WHERE s.segment = 'SEGMENT_NAME_HERE'
GROUP BY s.groupid, s.colour, s.width, s.cost, s.rrp, s.shopifyprice
ORDER BY stock DESC
```
