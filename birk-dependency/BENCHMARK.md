# Birkenstock dependency — baseline, Aug 2026

Goal: **materially reduce Shopify's dependence on Birkenstock within 6–12 months.**
This is the starting line. Re-measure against it; don't re-derive it.

Baseline window: **27 Aug 2025 – 26 Aug 2026** (rolling 12 months).
Prior-year window: 27 Aug 2024 – 26 Aug 2025.
Source: `sales`, `channel='SHP'`. Sales history only reaches Aug 2024 (`db-maint/clean_sales.py`
purges older rows), so two full years is all the comparison there is.

## How these numbers are calculated

`sales.soldprice` and `sales.profit` are **per unit**, not line totals, and returns are
negative-`qty` rows with the profit already negated (`returns/sync_returns.py`). So:

| measure | expression |
|---|---|
| units | `sum(qty)` |
| revenue | `sum(qty * soldprice)` |
| profit | `sum(abs(qty) * profit)` |

`sum(profit)` alone under-counts multi-unit lines; `sum(qty*profit)` flips the sign on
returns and turns a refund into a gain. Use the table above or the figures will not tie.

All revenue is VAT-inclusive (that is what Shopify books). Profit is the owner's net model —
after VAT, cost, payment fee, packing, postage and the flat `/1.2` refund haircut.

## The headline

Shopify, last 12 months:

| | units | revenue | profit | margin | ASP |
|---|---|---|---|---|---|
| Birkenstock | 3,343 | £205,803 | £32,193 | 15.6% | £61.56 |
| Everything else | 429 | £15,108 | £1,615 | 10.7% | £35.22 |
| **Total** | **3,772** | **£220,912** | **£33,808** | **15.3%** | **£58.57** |

**Birkenstock is 93.2% of Shopify revenue and 95.2% of Shopify profit.**

That is the number to move. A useful 12-month target is a *profit* share in the low 80s —
which, at flat Birkenstock, means roughly tripling non-Birkenstock profit from £1.6k to ~£6k.

## It is getting worse, not better

Birkenstock share of Shopify revenue, by quarter:

| quarter | Birk £ | other £ | Birk % rev | Birk % profit |
|---|---|---|---|---|
| 2024-Q3 | 11,946 | 9,046 | 56.9% | 61.8% |
| 2024-Q4 | 4,296 | 8,017 | 34.9% | 36.9% |
| 2025-Q1 | 16,482 | 3,635 | 81.9% | 87.0% |
| 2025-Q2 | 72,994 | 7,606 | 90.6% | 93.2% |
| 2025-Q3 | 32,301 | 5,765 | 84.9% | 90.9% |
| 2025-Q4 | 13,698 | 4,615 | 74.8% | 81.3% |
| 2026-Q1 | 20,762 | 2,929 | 87.6% | 91.9% |
| 2026-Q2 | 103,116 | 3,663 | 96.6% | 97.8% |
| 2026-Q3* | 61,512 | 1,416 | 97.8% | 98.8% |

\* partial quarter, to 26 Aug 2026.

Read the **other £** column, not the percentage. Non-Birkenstock is not being crowded out by
Birkenstock growth — it is **shrinking in absolute terms**, from ~£9k a quarter two years ago
to £1.4k now. Year on year over the same window:

| | prior year | last year | change |
|---|---|---|---|
| Birkenstock revenue | £122,318 | £205,803 | **+68%** |
| Other revenue | £26,755 | £15,108 | **−44%** |
| Birkenstock profit | £19,850 | £32,193 | +62% |
| Other profit | £3,411 | £1,615 | **−53%** |

The dependency is rising from both ends. Any plan that only adds new brands, without
arresting the decline in the ones already listed, starts from behind.

## Four things worth knowing before planning

**1. The group is not dependent on Birkenstock — Shopify is.**

| channel | revenue | profit | Birkenstock |
|---|---|---|---|
| Shopify | £220,912 | £33,808 | 93% of revenue |
| Amazon | £195,943 | £20,060 | **£0 — none** |
| CM3 | £5,276 | £1,370 | — |

Amazon turns over £196k a year with no Birkenstock at all — £147,738 of it Lunar. Across the
whole business Birkenstock is ~49% of revenue. We already know how to sell non-Birkenstock
footwear profitably; we do not currently do it on our own site.

**2. Lunar is the obvious lever, and it is not a listing problem.**
40 of 42 Lunar styles are already `shopify=1`. Lunar did £147,738 on Amazon and £7,982 on
Shopify — a **19:1** split on the same stock. Whatever is wrong is demand, price, or size
depth, not catalogue coverage. Same shape for Rieker: 26/26 listed, £22,871 Amazon vs £1,533
Shopify.

**3. The stock is where the dependency actually lives.**

| | styles on Shopify | with any stock | units in stock | stock at cost |
|---|---|---|---|---|
| Birkenstock | 175 | 141 | 1,897 | **£66,282** |
| Other | 111 | 55 | 261 | £5,299 |

**92.6% of the working capital on the site is Birkenstock.** Half the non-Birkenstock
catalogue has no stock at all, and average size coverage on the non-Birkenstock styles is
**26.4%** against 45.0% for Birkenstock — only 16 of 111 non-Birk styles carry 70%+ of their
size run. A listing at 26% size coverage is close to unsellable. Reducing the dependency is a
buying decision before it is a marketing one, and it will move cash from a brand at 15.6%
margin into brands currently running at 12.4% (Lunar) and below.

(Coverage per `CLAUDE.md`: `skumap` for the size universe, `localstock` for what is in stock.
Never `skusummary.variants` / `stockvariants`.)

**4. There is no basket effect to lose — and no cross-sell happening either.**

| order type | orders | revenue | AOV |
|---|---|---|---|
| Birkenstock only | 3,631 | £236,810 | £65.22 |
| Non-Birkenstock only | 418 | £16,879 | £40.38 |
| Mixed | **3** | £439 | £146.34 |

Three mixed orders in twelve months. Good news: the non-Birkenstock business stands on its
own, so growing it does not risk a Birkenstock attach rate. Bad news: nothing on the site is
currently pulling a Birkenstock buyer toward anything else — and the mixed AOV of £146 hints
at what it would be worth if it did.

## Supporting detail

**Concentration inside the dependency** — Arizona alone is 42.6% of Birkenstock revenue, and
**39.6% of all Shopify revenue** from a single style. Top styles by revenue share of Birk:
Arizona 42.6%, Gizeh 13.6%, Bend 9.7%, Milano 9.2%, Madrid 8.3%, Zermatt 7.8%, Mayari 4.9%.
Everything else is under 1% each.

**Non-Birkenstock brands on Shopify, last 12 months:**

| brand | units | revenue | profit | margin |
|---|---|---|---|---|
| Lunar | 258 | £7,982 | £986 | 12.4% |
| Goor | 68 | £2,214 | £360 | 16.3% |
| Skechers | 40 | £2,154 | −£16 | −0.7% |
| Rieker | 34 | £1,533 | £75 | 4.9% |
| Roamers | 5 | £253 | £54 | 21.4% |
| Grafters | 5 | £174 | £38 | 21.6% |
| 10 others | 19 | £798 | £118 | — |

Skechers is selling at a loss and Rieker at 4.9% — thin enough that a Shopify pricing pass on
the non-Birkenstock tail (`shopify-price/STRATEGY.md`) is worth doing before any spend goes
behind these brands.

**Return rate** is not a differentiator: 12.7% of Birkenstock units, 11.2% of the rest.

## The metrics to track

Primary — one number, reviewed monthly on a rolling 12-month basis:

- **Birkenstock share of Shopify profit: 95.2% today.**

Secondary, because the primary can improve for the wrong reason (a bad Birkenstock season
flatters it without building anything):

| metric | baseline |
|---|---|
| Non-Birkenstock Shopify profit, rolling 12m | £1,615 |
| Non-Birkenstock Shopify revenue, rolling 12m | £15,108 |
| Non-Birkenstock share of Shopify stock at cost | 7.4% |
| Non-Birk styles with ≥70% size coverage | 16 of 111 |
| Arizona share of total Shopify revenue | 39.6% |
| Mixed-brand orders per year | 3 |

Track non-Birkenstock in **absolute pounds** alongside the share. If Birkenstock has a poor
summer, the share falls on its own and nothing has actually been fixed.
