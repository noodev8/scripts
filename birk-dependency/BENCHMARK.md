# Birkenstock dependency — baseline, Aug 2026

Goal: **materially reduce Shopify's dependence on Birkenstock within 6–12 months.**
This is the starting line. Re-measure against it; don't re-derive it.

Baseline window: **27 Aug 2025 – 26 Aug 2026** (rolling 12 months).
Prior-year window: 27 Aug 2024 – 26 Aug 2025.
Source: `sales`, `channel='SHP'`. Sales history only reaches Aug 2024 (`db-maint/clean_sales.py`
purges older rows), so two full years is all the comparison there is.

## Decisions on file

Scope calls made by Andreas, recorded here rather than in per-machine memory so they travel
between the two machines. Anything below is settled unless he reopens it.

| Decision | Date |
|---|---|
| **Measure at brand level only.** Birkenstock is Birkenstock — no style-level split (Arizona, Gizeh…). It measures a risk he isn't managing. | 27 Aug 2026 |
| **Mixed-brand orders / basket composition is not a metric.** Cross-sell isn't a lever being pulled. | 27 Aug 2026 |
| **The focus brands are Lunar, Goor, Rieker and Remonte.** These are what the next months are spent on. | 27 Aug 2026 |
| **Skechers is being exited** — ignore it in readings, don't price it, don't buy it. | 27 Aug 2026 |
| **Roamers and Grafters are parked** — not a focus, folded into "other brands". | 27 Aug 2026 |
| **Every product gets an assigned channel.** Shopify and Amazon compete for the same demand — pulling one up pulls the other down. No plan may assume a Shopify gain is incremental. See "Channel assignment" below. | 27 Aug 2026 |

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

## The four focus brands

Lunar, Goor, Rieker and Remonte are where the next months go. Together they are **78% of
non-Birkenstock Shopify revenue and 89% of its profit** — so the programme does not depend on
finding new brands, it depends on these four working.

| brand | units | revenue | profit | margin |
|---|---|---|---|---|
| Lunar | 258 | £7,982 | £986 | 12.4% |
| Goor | 68 | £2,214 | £360 | 16.3% |
| Rieker | 34 | £1,533 | £75 | 4.9% |
| Remonte | 2 | £118 | £14 | 11.5% |
| **Focus four** | **362** | **£11,847** | **£1,435** | **12.1%** |
| Skechers *(exiting)* | 40 | £2,154 | −£16 | −0.7% |
| Other brands *(parked — incl. Roamers, Grafters)* | 27 | £1,107 | £196 | 17.7% |
| **Non-Birkenstock total** | **429** | **£15,108** | **£1,615** | **10.7%** |

Skechers is excluded from every target below — it is on the way out and its −£16 shouldn't
flatter or drag the numbers either way.

### Where each one stands

**Shopify against Amazon, same stock, last 12 months:**

| brand | Shopify | Amazon | Shopify as % of the pair |
|---|---|---|---|
| Lunar | £7,982 | £147,738 | 5.1% |
| Rieker | £1,533 | £22,871 | 6.3% |
| Remonte | £118 | £3,277 | 3.5% |
| Goor | £2,214 | £1,114 | 66.5% |

Lunar, Rieker and Remonte all sell 15–30× better on Amazon than on our own site.

**Do not read that gap as £150k of headroom.** It is the same demand, and the two channels
compete for it — see "Channel assignment" below, where the Ives episode is costed. **Goor is
the exception and the useful counter-example:** it already does better on Shopify than on
Amazon, and at 16.3% it is the highest-margin brand of the four.

## Channel assignment

**Shopify and Amazon are not additive. Pulling demand to one pulls it off the other, and the
Amazon side does not simply bounce back.**

This is settled by evidence, not theory. Lunar's Shopify price was cut to £29.99 on the
reasoning that our own fees could absorb it, against £38 on Amazon where the fees are much
higher. A separate Google campaign was then pointed at the St Ives segment. Shopify sales
rose. Within days Amazon sales for Ives collapsed, and it took weeks of work to recover.

Ives, monthly, by channel:

| month | Shopify units | Shopify profit | Amazon units | Amazon profit |
|---|---|---|---|---|
| Jun 2025 | 32 | £100 | 474 | £2,451 |
| Jul 2025 | 25 | £97 | 390 | £2,048 |
| **Aug 2025** | **51** | **£198** | **162** | **£833** |
| Sep 2025 | 36 | £172 | 156 | £805 |
| Oct 2025 | 41 | £187 | 205 | £1,051 |
| Nov 2025 | 16 | £74 | 120 | £610 |
| … | | | | |
| Mar 2026 | 27 | £107 | 279 | £1,176 |
| Apr 2026 | 21 | £108 | 518 | £2,180 |
| May 2026 | 11 | £16 | 635 | £2,685 |

In the month Shopify doubled — 25 units to 51, **+£101 of profit** — Amazon fell 390 units to
162, **−£1,215 of profit**. The trade was roughly **twelve pounds lost for every pound
gained**, and Amazon stayed depressed for six months; it did not regain April's level until
Apr 2026.

Some of that August step is seasonal, but not most of it. The prior year's same step was
Aug 129 → Sep 112 units, a 13% decline. This one was 390 → 162, a 58% decline, in the month
the campaign ran.

### Why the Shopify price cut didn't pay

The cut to £29.99 was made because our own fees are lower. Over the last 12 months, they
cancel out almost exactly:

| channel | units | ASP | profit per unit | margin |
|---|---|---|---|---|
| Amazon | 3,483 | £38.46 | **£4.32** | 11.2% |
| Shopify | 183 | £32.30 | **£4.37** | 13.5% |

**Five pence a pair.** The lower fee was handed straight to the customer in the lower price,
so Shopify has no per-unit advantage on Ives at all — while Amazon carries 19× the volume.
Moving a sale from Amazon to Shopify earns nothing extra, and risks the Amazon rank and
velocity that produced the volume in the first place. That is the worst possible trade.

### The rule this sets

1. **Assign a primary channel per product before spending anything on it.** Decide, then
   price and promote for that channel only.
2. **Decide it on profit per unit, not on fee percentage.** Fees only matter after price. A
   lower fee handed to the customer is not a saving.
3. **Never treat a Shopify gain as incremental** unless the Amazon line for the same product
   has been checked over the following weeks. Judge any Shopify push on the *pair*.
4. **Where Amazon is the assigned channel, hold the Shopify price at or above Amazon's** so
   the site doesn't undercut the channel doing the volume.
5. **Goor is the shape to look for** — products that do better on Shopify than Amazon are
   where Shopify growth is genuinely free of this trade-off.

Reducing Birkenstock dependency therefore cannot mean "move Lunar to Shopify". It means
finding and buying volume that Shopify can win *without* taking it off Amazon — Goor-shaped
products, and stock in sizes we currently cannot sell at all.

**And what's actually on the shelf:**

| brand | styles live | with stock | units | at cost | avg size cover | ≥70% cover |
|---|---|---|---|---|---|---|
| Lunar | 40 | 28 | 121 | £1,772 | 32.8% | 4 of 40 |
| Rieker | 26 | **7** | 52 | £1,681 | 23.1% | 6 of 26 |
| Remonte | 5 | 3 | 12 | £441 | 40.0% | 1 of 5 |
| Goor | 7 | 6 | 27 | £411 | 29.8% | 0 of 7 |
| **Focus four** | **78** | **44** | **212** | **£4,305** | — | **11 of 78** |

This is the binding constraint. Nineteen of Rieker's 26 live styles have no stock at all, and
across the four only 11 of 78 styles carry 70% or more of their size run. It is not a
listings problem — everything is already live on Shopify. **Buying has to move before
anything else will.**

## The reframe: the business isn't Birk-dependent, the website is

| channel | revenue | profit | Birkenstock |
|---|---|---|---|
| Shopify | £220,912 | £33,808 | 93% of revenue |
| Amazon | £195,943 | £20,060 | **£0 — none** |
| CM3 | £5,276 | £1,370 | — |
| **All channels** | **£422,131** | **£55,238** | **49% of revenue** |

Amazon turns over £196k a year with no Birkenstock at all. Across the whole business
Birkenstock is ~49% of revenue. We already know how to sell non-Birkenstock footwear
profitably; we do not currently do it on our own site.

## The stock is where the dependency lives

| | styles on Shopify | with any stock | units in stock | stock at cost |
|---|---|---|---|---|
| Birkenstock | 175 | 141 | 1,897 | **£66,282** |
| Other | 111 | 55 | 261 | £5,299 |

**92.6% of the working capital on the site is Birkenstock.** Half the non-Birkenstock
catalogue has no stock at all, and average size coverage on those styles is **26.4%** against
45.0% for Birkenstock. A listing at 26% size coverage is close to unsellable. Reducing the
dependency is a buying decision before it is a marketing one, and it will move cash from a
brand at 15.6% margin into brands currently running at 12.1% across the focus four.

(Coverage per `CLAUDE.md`: `skumap` for the size universe, `localstock` for what is in stock.
Never `skusummary.variants` / `stockvariants`.)

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
| **Focus-four Shopify profit, rolling 12m** | **£1,435** |
| **Focus-four Shopify revenue, rolling 12m** | **£11,847** |
| Focus-four styles with ≥70% size coverage | 11 of 78 |
| Focus-four stock at cost | £4,305 |
| Non-Birkenstock share of Shopify stock at cost | 7.4% |
| **Focus-four Amazon profit, rolling 12m — the guard rail** | **£18,496** |

That last line is the one that stops this programme doing harm. Focus-brand profit on Amazon
is £18,496 against £1,435 on Shopify — thirteen times larger. Any Shopify gain bought by a
fall in that number is a loss, and it will not show up in the primary metric at all. Read the
two together, every month.

Track non-Birkenstock in **absolute pounds** alongside the share. If Birkenstock has a poor
summer, the share falls on its own and nothing has actually been fixed.

Skechers is excluded from the focus-four lines by definition; as it winds down it will drag
the whole-tail lines slightly, which is expected and not a signal.
