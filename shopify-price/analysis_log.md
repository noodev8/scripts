# Shopify Price Analysis — Run Log

Tracks each Phase 1 run so we can see trends over time.

---

## 2026-04-04

| Metric | Value |
|---|---|
| Period | Last 30 days (2026-03-05 to 2026-04-04) |
| Products sold | 108 |
| Total units | 302 |
| Total revenue | £16,772.94 |
| Total net profit | £2,304.12 |
| Avg net profit/unit | £7.63 |
| Loss-making products | 16 (-£241) |
| Trend (14d vs prev 14d) | 10.6 units/day vs 10.3 — up 3% units, +13% revenue |

**Cost constants used:** Payment 2.9% + £0.30 | VAT 1/6 (where tax=1) | Wages £1.00 | Postage £3.44

**Google reports processed:** Benchmark (148 groupids) + Performance (124 groupids, 98 with both)

**Gear:** Steady

**Changes applied (6):**
- 0051701-ARIZONA: £65.50 → £68.00 (step toward summer sweet spot £73, selling 3/wk, 51 incoming)
- 0040791-MADRID: £59.50 → £62.00 (mirrors last year spring step-up, selling 3/wk, 24 stock)
- 0034701-MILANO: £68.21 → £80.00 (prep for 100 incoming, sold 8 at £90 RRP May 25, odd sizes left)
- 1029470-ARIZONA: £78.40 → £72.00 (decrease — stalling 0.3/wk for 8 months, proven 1.5/wk at £72)
- 0043661-GIZEH: £72.68 → £75.00 (performing 1.0/wk, best non-summer rate, step toward summer)
- 1005291-ARIZONA: £69.00 → £72.00 (proven year-round price, prep for 47 incoming)

**Products reviewed but no change:**
- 1015092-ZERMATT: Hold at £75 — slipper, not seasonal for spring. Revisit later.
- 1017721-BEND: Hold at £95 — only 19 days since change, spring building. Revisit in 2 weeks. May need to drop — lots of stock.
- 0051703-ARIZONA: Hold at £64.22 — at proven year-round price. May decrease into summer to replicate last year's 2.9/wk burst.

**15 candidates remaining from this session** — filtered list (14+ days, positive margin, headroom >£10). Pick up next session.

**Key observations:**
- All metrics up vs Mar 29: units +10%, revenue +13%, profit +17%. Pricing changes landing well.
- Profit growing faster than revenue — mix improving, not just chasing volume.
- Spring/summer lines picking up pace (Arizonas, Gizehs, Mayaris).
- Google ad budget increased to £38/day. ROAS still strong (10x+ even on quiet days).
- Process improvement: Google CSVs now picked up from Downloads folder (script updated). Doc updated to remind (not enforce) CSV download at session start.
- Discussion: auto-drill-down script to pre-calculate velocity-by-price and produce recommendations with confidence levels. Would reduce session time and enable staff to run sessions. Not yet built — revisit next session.

---

## 2026-03-29

| Metric | Value |
|---|---|
| Period | Last 30 days (2026-02-27 to 2026-03-29) |
| Products sold | 106 |
| Total units | 275 |
| Total revenue | £14,886.18 |
| Total net profit | £1,967.83 |
| Avg net profit/unit | £7.16 |
| Loss-making products | 17 |
| Trend (14d vs prev 14d) | 10.1 units/day vs 8.0 — up 26% |

**Cost constants used:** Payment 2.9% + £0.30 | VAT 1/6 (where tax=1) | Wages £1.00 | Postage £3.44

**Google reports processed:** Benchmark (1,260 variants → 149 groupids) + Performance (416 variants → 115 groupids, 96 with both)

**Changes applied (6):**
- 1029671-PASADENA: £70 → £66.50 (clearance — take loss, free space)
- 1030906-PASADENA: £70 → £66.50 (clearance — second colourway, same)
- 1017723-BEND: £104.95 → £108 (restore proven price — £104.95 drop was premature, spring building)
- 1017724-BEND: £95 → £94.50 (proven sweet spot from summer 25, weaker colourway)
- 1019152-ARIZONA: £35.19 → £36 (back to proven volume price — 24 sold at £36 Apr-Jun 25)
- 1027696-ARIZONA narrow: £59.34 → £64 (stop chasing regular width velocity, limited stock, no restock)

**Key observations:**
- Mar 23 (Mon) price changes caused a Tue dip (5 units) but this was normal Tuesday + mild Google learning phase. Recovered by Fri. Week overall was 34% above 8-week average.
- Performance report reinstated — now parsed in Phase 1 alongside benchmark. Shows Google's volume-optimised price per product.
- Guardrail (10% min margin) in apply script disabled for now — was blocking deliberate clearance decisions. Re-enable when auto-pricing goes live.
- "Sellable stock" concept documented — total stock can mislead when sizes are depleted. Drill-downs now check size distribution vs sales history.
- Report folder structure cleaned up — outputs go to `shopify-price/report/`, Google CSVs auto-deleted after processing.

**Products reviewed but no change:**
- 1017721-BEND: Hold at £95, only changed 2 weeks ago, sold one today. Revisit in 2 weeks.
- 0034791-MILANO: Hold at £72 — proven sweet spot (38 units at £72 last summer). 51 stock + 50 incoming = core summer line. Season hasn't started yet.
- 0034793-MILANO: Hold at £66.13 — 46 stock, zero sales. Watch when summer starts.

---

## 2026-03-23

| Metric | Value |
|---|---|
| Period | Last 30 days (2026-02-21 to 2026-03-23) |
| Products sold | 103 |
| Total units | 253 |
| Total revenue | £13,620.42 |
| Total net profit | £1,835.21 |
| Avg net profit/unit | £7.25 |
| Loss-making products | 18 |
| Products with stock | 92 |
| Products sold, no stock left | 11 |

**Cost constants used:** Payment 2.9% + £0.30 | VAT 1/6 (where tax=1) | Wages £1.00 | Postage £3.44

**Output:** `sales_analysis_30d.csv`

**Notes:**
- First run of new analysis process
- 18 loss-makers totalling ~£-248 in losses
- Worst: PASADENA 1029671 (-£13.02/unit, 5 sold = -£65), ARIZONA 1027723 (-£7.99/unit, 6 sold = -£48)
- Several loss-makers still have stock (PASADENA 7 units, FLORIDA 11 units)
