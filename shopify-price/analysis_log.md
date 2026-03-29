# Shopify Price Analysis — Run Log

Tracks each Phase 1 run so we can see trends over time.

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
