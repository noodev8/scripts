# Birkenstock dependency — baseline, Aug 2026

Goal: **materially reduce Shopify's dependence on Birkenstock within 6–12 months.**
This is the starting line. Re-measure against it; don't re-derive it.

Published as an artifact: https://claude.ai/code/artifact/cd664dc3-fc12-4a97-89d4-67e44670d272
Republish by passing that URL — do not publish a fresh one, or the link goes stale on the
other machine. (Memory is machine-local; this line is the only cross-machine record of it.)

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
| **Padders and Caprice are being introduced.** Not yet in any figure here — add them to the focus group once they have stock and sales. | 27 Aug 2026 |
| **Goor is the first task.** See "Task 1 — Goor" below. | 27 Aug 2026 |
| **Aim new buying at £70+ retail.** Profit per pair is £3.10 under £40 against £14.83 at £70–90. Diversification means dearer product, not cheaper. See "Price band is the real lever". | 27 Aug 2026 |

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

## Task 1 — Goor

Goor is the first brand worked because it is the only focus brand that already wins on
Shopify, and because **its decline accounts for most of the problem this whole programme is
trying to solve.**

Seven styles, all supplier **UKD**, all segment **UKD-SEG**. Men's smart brogues and Oxfords
plus one boys' patent Oxford. Cost £13.98–£15.98, RRP £40.

### It hasn't underperformed — it has been switched off

| Shopify | prior 12m | last 12m | change |
|---|---|---|---|
| units | 359 | 68 | **−81%** |
| revenue | £11,269 | £2,214 | −80% |
| profit | £1,603 | £360 | **−78%** |
| profit per unit | £4.46 | £5.30 | +19% |

Note the last row. Per-unit economics **improved** — the ASP rose from £31.39 to £32.56 as
discounting stopped. This is not a brand losing its market. It is a brand that stopped being
supplied.

Put beside the headline decline: total non-Birkenstock Shopify profit fell £3,411 → £1,615,
a loss of £1,796. **Goor alone is £1,243 of that — 69% of the entire non-Birkenstock
collapse.** The monthly units tell it plainly: 34, 59, 44, 49 through late 2024, against 2,
2, 2, 7, 6, 9 through 2026.

### Why: there are 27 pairs in the building

| style | | sizes | in stock | units | coverage |
|---|---|---|---|---|---|
| M014A | Mens Brogue Oxford Black | 9 | 6 | 6 | 67% |
| B710AP | Boys Oxford Tie Patent Black | 11 | 6 | 10 | 55% |
| M710AP | Mens Patent Tuxedo Dress Shoe | 9 | 3 | 7 | 33% |
| M291AP | Mens Smart Oxford Tie Patent | 7 | 2 | 2 | 29% |
| M968BC | Mens Tan/Navy Brogue Oxford | 7 | 1 | 1 | 14% |
| M014B | Mens Brogue Oxford Brown | 9 | 1 | 1 | 11% |
| M410B | Mens 4-Eye Brogue Gibson Tan | 7 | **0** | **0** | **0%** |
| **total** | | **59** | **19** | **27** | **32%** |

£411 of stock at cost. M968BC is the best-selling men's style on Shopify and it is down to a
single pair in a single size. M410B is listed and completely unbuyable.

### The economics justify restocking it properly

At full RRP the two M014 styles return **£9.54 profit per pair** — against Birkenstock's
Shopify average of **£9.63**. Effectively identical earnings per pair, on stock costing
£15.98 instead of Birkenstock's ~£34.94 average. **The same capital works about twice as
hard in Goor**, and it is not seasonal — these are year-round occasion and formal shoes,
peaking around December and May rather than following the sandal cycle that concentrates
Birkenstock into Q2.

### Shopify is unambiguously the right channel for it

| channel | units | ASP | profit per unit |
|---|---|---|---|
| Shopify | 68 | £32.56 | **£5.30** |
| Amazon | 35 | £31.83 | **£0.74** |

Goor earns **seven times more per pair on Shopify than on Amazon**, and M410B actually loses
money on Amazon (−£0.76 per unit). This is the exact inverse of Ives — and it is why Goor
carries no cannibalisation risk. Pushing Goor on Shopify takes almost nothing off a channel
that barely profits from it.

### What to do

1. **Reorder from UKD across all seven styles**, to a full size run. This is the whole task —
   nothing else moves until it does. The same order can cover the parked UKD-SEG brands
   (Roamers, Grafters, Mod Comfys, Dek, R21, Cipriata, Scimitar).
2. **Assign Goor to Shopify** under the channel rule. Consider withdrawing M410B from Amazon
   rather than restocking it there.
3. **Hold RRP.** B710AP has been selling at £27.59 against a £30 list; at £30 it returns
   £4.51 a pair instead of £2.89 — **+56% per pair** for no volume risk worth the name, given
   it already sells at £30 today.
4. **Recovering the prior year's 359 units at today's £5.30 per unit is ~£1,900 of profit** —
   more than the entire current non-Birkenstock total of £1,615, from a brand we already
   stock, list and know how to sell.

## Price band is the real lever

Asked whether Goor is worth stocking at a £40 RRP when the ROAS is hard, and whether the aim
should be products with a £70+ AOV. The data says **the £70+ instinct is right, and by a much
wider margin than it looks.** Shopify, last 12 months, by selling price:

| price band | units | ASP | profit per unit | margin | break-even ROAS |
|---|---|---|---|---|---|
| under £40 | 1,122 | £33.19 | £3.10 | 9.3% | **10.7×** |
| £40–55 | 443 | £46.02 | £5.17 | 11.2% | 8.9× |
| £55–70 | 1,498 | £64.10 | £9.15 | 14.3% | 7.0× |
| **£70–90** | **1,020** | **£75.00** | **£14.83** | **19.8%** | **5.1×** |
| £90+ | 231 | £103.75 | £19.24 | 18.5% | 5.4× |

A £75 pair earns **nearly five times** the profit of a £33 pair. The cause is fixed cost per
order — 30p payment fee, £1.00 packing, £3.44 Royal Mail, £4.74 in total before the `/1.2`
haircut. At £33 that is 14% of the order; at £75 it is 6%. Cheap shoes are eaten by postage.

"Break-even ROAS" above is simply price ÷ profit — the return needed for an ad-funded sale to
wash its face. **Under £40 you need 10.7×; at £70–90 you need 5.1×.** That is the whole of
the ROAS problem, stated properly, and it is a structural fact about the price point rather
than anything to do with the brand.

**The strategic consequence is bigger than Goor.** The non-Birkenstock tail averages £35.22 —
squarely in the worst band on the table. Every diversification brand currently held sits in
the £3–5 per unit zone while Birkenstock sits at £9.63 and the £70–90 band sits at £14.83. So
**the way out of Birkenstock dependency is not cheaper brands, it is dearer ones.** Anything
bought to replace Birkenstock revenue should be aimed at £70+ retail, or it will need three
times the units to earn the same money and will never fund its own advertising.

## Should we still stock Goor?

**Yes — but as a non-paid line, at full RRP, and understood as a tidy-up rather than a
strategy.**

The case for:

- **It is the exception in its price band.** At the full £40 RRP, Goor returns £9.54 on a
  £15.98 cost — a 23.9% margin, against the 9.3% typical under £40. Its break-even ROAS is
  **4.2×, better than Birkenstock's own 6.4×**. The general rule about cheap product does not
  apply to Goor *at RRP*, because the cost price is unusually good.
- **The capital is trivial.** £411 on the shelf now; a full size run across seven styles is
  low four figures against £66,282 tied up in Birkenstock.
- **It is counter-seasonal.** December and May peaks land in the Q4/Q1 trough where
  Birkenstock does £13.7k and £20.8k against £103k in Q2. Overheads don't take the winter off.
- **No cannibalisation.** £5.30 per unit on Shopify against £0.74 on Amazon.

The case against, stated honestly:

- **It only works at RRP.** Discounted to the £27.59 it has actually been selling at, profit
  per pair falls to £2.89 and break-even ROAS rises to **9.5×** — unfundable. The margin is a
  price-discipline story, not a product story.
- **It is small.** Recovering last year's 359 units is ~£1,900 of profit. Worth having,
  nowhere near enough to move a 95.2% dependency.

**So: restock it, hold RRP with no discounting, and do not fund it from the Shopping campaign
at the blended 6× target** — at 6× a Goor sale at RRP is fine, but the same budget spent on a
£75 Birkenstock earns £14.83 instead of £9.54, so paid should follow the price band. Give
Goor organic, email and repeat traffic, where its 4.2× break-even makes it comfortably
profitable, and let it fill the winter trough.

Do the restock because it is cheap, quick and recovers a business we already had. Do **not**
treat it as the answer to the dependency — that has to come from £70+ product.

## Incoming: Padders and Caprice

Both are being introduced and appear in no figure in this document — neither brand exists in
`skusummary` yet. When they have stock and sales, add them to the focus group and re-baseline
that section.

Three things to settle before spend goes behind either, all following from the sections
above:

1. **Buy them at £70+ retail** if the range allows it. That is the band that earns £14.83 a
   pair and can carry its own advertising at 5.1×. A £40 introduction repeats the problem
   the rest of the tail already has.
2. **Assign each product a primary channel on profit per unit** before any campaign is built.
3. **Buy a full size run on fewer styles**, not a thin spread across many. The Goor position
   above — 27 pairs across seven styles, one at zero coverage — is what a thin spread looks
   like eighteen months later.

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
