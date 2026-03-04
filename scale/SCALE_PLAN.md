# Brookfield Comfort — Scale to £1M Plan

**Started:** February 2026
**Target:** £1M annual revenue within 3 years (by end of FY 2028/29)
**Approach:** Momentum-based, cash-flow-protected growth

---

## 1. Where We Are Now (Feb 2026)

| Metric | Value | Notes |
|--------|-------|-------|
| Trailing 12-month revenue | ~£310k | Feb '25 – Jan '26 |
| Peak month | £62k (May '25) | Birkenstock spring/summer season |
| Trough month | £8k (Jan '26) | Winter low |
| Shopify revenue (12m) | £158k | Birkenstock-led, Google Ads ROAS ~10x |
| Amazon revenue (12m) | £149k | Lunar-led, high margin |
| Shopify gross margin | ~14.7% | Birkenstock margins are thin |
| Amazon gross margin | ~41.5% | Lunar margins are strong |
| Total gross profit (12m) | ~£86k | |
| Monthly orders (avg) | ~600 | Peak: 1,501 (May '25) |

### Brand Breakdown (Last 12 Months)

| Brand | Revenue | Gross Profit | Margin | Channel |
|-------|---------|-------------|--------|---------|
| Lunar | £141k | £57k | 40.6% | Primarily Amazon |
| Birkenstock | £136k | £20k | 14.8% | Primarily Shopify |
| Rieker | £14k | £4k | 30.6% | Amazon |
| Other | £20k | £5k | ~25% | Mixed |

### Two Distinct Engines

1. **Shopify + Birkenstock + Google Ads** — Revenue engine. High ROAS (~10x), captures existing brand demand. Thin margins but reliable volume driver.
2. **Amazon + Lunar (St Ives)** — Profit engine. Strong margins (40%+), loyal repeat buyers, lower customer acquisition cost.

---

## 2. The £1M Path — Revenue Milestones

| Year | Target Revenue | Growth | Monthly Avg | Key Focus |
|------|---------------|--------|-------------|-----------|
| Year 0 (current) | £310k | baseline | £26k | Stabilise, protect profit |
| Year 1 (FY 26/27) | £500k | +61% | £42k | Scale proven winners, launch retention |
| Year 2 (FY 27/28) | £750k | +50% | £63k | Expand channels, deepen inventory |
| Year 3 (FY 28/29) | £1M+ | +33% | £83k | Full maturity, diversified revenue |

### Revenue must be profitable revenue

Scaling to £1M on Birkenstock alone would need ~£700k Birkenstock revenue at 15% margin = ~£105k GP.
Current mix (Lunar + Birkenstock) at £310k already generates £86k GP.
**Protecting and growing the Lunar/Amazon profit engine is as important as scaling Shopify/Birkenstock volume.**

### Reality Check: Where Does £1M Come From? (Feb 2026)

**Realistic ceiling from current operations (~£500-630k):**

| Source | Current | Realistic Growth Path | Year 2-3 Target |
|--------|--------:|:----------------------|----------------:|
| Birkenstock/Shopify | £136k | Google Ads scaling (ROAS 10x→5x with more volume), spring/summer push | £250-300k |
| Lunar/Amazon | £142k | Ives stock depth, Buy Box protection, new customer acquisition | £200-250k |
| Rieker/Winter/Other | £32k | Rieker range expansion on Amazon (2-week lead time, 33% margin). Birkenstock slippers not working — see section 8. | £50-80k |

This gets to **~£500-630k** by doing more of what already works. No new risk, just execution.

**The gap from £630k to £1M (~£350-400k) needs something new:**

1. **Expand Rieker range on Amazon** — most natural next move. Already proven at 33% margin, 2-week lead time. Currently 8 styles doing £5.2k GP. Previously stocked more styles but cut back. Revisit selectively using sales data — don't speculate, bring back styles with evidence. Amazon only — no Shopify.
2. **Deeper Birkenstock core on Shopify** — not more models, more stock depth on the proven 15. Width doesn't help (115 styles sold off-season at 0% margin). Depth on best sellers during peak = more revenue in the 3 months that actually make money.
3. **Lunar new style exploration (summer only)** — 4-day lead time makes testing cheap. But Ives is dominant and other styles have been losers. Test in summer when the customer base is buying. Never order winter Lunar books again. **Note (Mar 2026):** Ives appears to be approaching its ceiling — we're ordering as much as we can but volume is plateauing. This makes finding complementary brands more important for the next growth phase.
4. **Waldlaufer on Amazon** — similar demographic, worth evaluating when cash allows. Lower priority than Rieker.

**2026 is a stabilisation year.** Go deep on proven winners (Ives, Birkenstock core, Rieker). Turn a profit first. Expand cautiously when traction and cash allow — Rieker range expansion is the lowest-risk next step when ready. However, stabilisation doesn't mean closed to opportunity — always be investigating potential new brands and suppliers so we're not caught flat-footed when it's time to grow. Investigation is free; commitment is what costs money.

**Ruled out:** TikTok Shop (wrong demographic), Skechers (margins too thin, same problem as Birkenstock).

---

## 3. Growth Levers (Prioritised)

### Lever 1: Retention & Repeat Purchase (Low cost, high impact)
- Current repeat rate: 6.8%
- Target: 15% within 12 months
- **Actions:**
  - [ ] Birkenstock 90-day repurchase email (test plan ready)
  - [ ] Klaviyo brand-segmented lifecycle flows
  - [ ] Post-purchase education sequences
  - [ ] Seasonal drop alerts for previous buyers
  - [ ] Restock notifications by model and size
- **Impact estimate:** Doubling repeat rate from 7% to 14% on ~3,000 Shopify customers = ~210 additional orders = ~£12k additional revenue at minimal cost

### Lever 2: Google Ads Scaling (Proven, controlled)
- Current spend: ~£17k/year, ROAS 10x
- Significant headroom — even at 5x ROAS, ad spend is profitable
- **Actions:**
  - [ ] Incrementally increase daily budget, monitor ROAS weekly
  - [ ] Expand to broader Birkenstock terms where stock supports it
  - [ ] Seasonal budget acceleration (Mar–Jul) and pullback (Nov–Feb)
  - [ ] Track via `google_stock_track` table for spend/stock/sales correlation
- **Constraint:** Stock must be available before increasing spend
- **Budget review process:** See `google_ads/BUDGET_REVIEW_PROCESS.md`

### Lever 3: Lunar/Amazon Expansion (Profit growth)
- Lunar is the #1 brand by profit with 40%+ margins
- St Ives (Ives) is the proven winner — other styles tested and none come close
- **4-day lead time** — biggest strategic advantage in the business. React to demand, not forecast.
- **Actions:**
  - [ ] Maintain relentless Ives stock depth across all colourways — every stockout day is lost profit
  - [ ] Explore new Lunar styles **in summer only** when customer base is active (winter books were failures — cleared below cost)
  - [ ] Protect Amazon margin — don't race to bottom on pricing
- **Impact:** Every £10k of Lunar revenue = ~£4k GP vs £1.5k GP from Birkenstock
- **What didn't work:** Lunar winter ranges (total loss, cleared below cost). Don't repeat.

### Lever 4: Seasonal Smoothing (Off-season revenue)
- Nov–Feb currently does £8–16k/month vs £30–62k in peak
- Already improving YoY (+96% to +145% growth in off-season months)
- **Birkenstock off-season is structurally unprofitable** — 976 units Jul–Feb at 0% margin. See section 8. Birkenstock slippers (Zermatt) also failed. Don't chase winter Birkenstock revenue.
- **Lunar is profitable year-round** (37–43% margin even in winter) — Lunar IS the seasonal smoothing
- **Actions:**
  - [ ] Rieker range expansion on Amazon — 33% margin, 2-week lead time, proven at small scale. This is the lowest-risk winter revenue growth.
  - [ ] Maintain Lunar Ives stock through winter — it's the only brand making money Nov–Feb
  - [ ] Reduce Google Ads spend Nov–Feb (Birkenstock generates zero profit off-season anyway)
  - ~~Birkenstock indoor/wool models~~ — tested, doesn't work. Zermatt makes £0 or negative.
  - ~~Lunar winter books~~ — tested, total failure. Cleared below cost.

### Lever 5: Operational Efficiency (Protect cash flow)
- **Actions:**
  - [ ] Price optimisation engine already running — keep refining
  - [ ] Stock-aware pricing (don't sell cheap when running low)
  - [ ] Monitor inventory turnover by SKU and channel
  - [ ] Cash flow forecasting aligned with stock purchasing cycle

---

## 4. Key Constraints & Guardrails

1. **Cash flow comes first** — No growth initiative should strain working capital to breaking point
2. **Profit before revenue** — A £500k business at 25% margin is better than £750k at 10%
3. **Stock before spend** — Never increase ad spend without stock to fulfil
4. **Test before committing** — Every new initiative starts as a small test (e.g. the 90-day email)
5. **Seasonal awareness** — Plan stock and cash around the Birkenstock cycle

---

## 5. Metrics to Track

| Metric | Current | Year 1 Target | How Tracked |
|--------|---------|---------------|-------------|
| Monthly revenue | £26k avg | £42k avg | `sales` table |
| Gross profit margin (blended) | ~28% | 28%+ | `sales.profit` |
| Repeat purchase rate | 6.8% | 12%+ | Klaviyo / order analysis |
| Google Ads ROAS | 10x | 7x+ (with higher spend) | Google Ads / `google_stock_track` |
| Shopify orders/day | ~8 | ~15 | `sales` where channel='SHP' |
| Amazon orders/day | ~11 | ~15 | `sales` where channel='AMZ' |
| Average order value | ~£43 | £48+ | `sales` |
| Stock days cover | varies | 30+ days on top sellers | `shopify_health_check` view |
| Off-season monthly rev | £8–16k | £20k+ | `sales` by month |

---

## 6. Immediate Next Steps

1. ~~Launch Birkenstock 90-day repurchase test~~ — Email designed, sending w/c 17 Feb
2. ~~Analyse top SKUs by profit~~ — Done, see section 7
3. ~~Analyse Birkenstock off-season margin~~ — Done, see section 8. Structural 0% margin Jul–Feb confirmed.
4. **Model ad spend scenarios** — What does ROAS look like at £25k, £35k, £50k annual spend?
5. **Map Lunar growth opportunity** — Ives is the winner. Focus on stock depth, explore new styles in summer only (4-day lead time makes testing cheap)
6. **Rieker range expansion plan** — Review previously stocked styles, identify candidates for Amazon relaunch. 2-week lead time, 33% margin.
7. **Build monthly revenue dashboard** — Track progress against the milestones above
8. **Birkenstock ordering review (Sep/Oct)** — Use birkenstock-sales.csv report. Order depth on core 15, target sell-through by June/July. Don't over-order width.

---

## 7. Analysis — Top SKUs by Gross Profit (Last 12 Months)

**Run date:** 2026-02-17
**Source:** `sales` table (excluding returns), `localstock` (warehouse stock), `amzfeed.amzlive` (FBA stock). Check both `localstock` and `amzfeed` for full stock picture — most Lunar sells on Amazon so FBA stock is where the real numbers are.

### Top 25 by Gross Profit

| # | GroupID | Brand | Ch | Units | Revenue | GP | Margin |
|---|---------|-------|----|------:|--------:|---:|-------:|
| 1 | FLE030-IVES-WHITE | Lunar | AMZ | 1,266 | £50,561 | £21,877 | 43.3% |
| 2 | FLE030-IVES-NAVY-BLUE | Lunar | AMZ | 371 | £15,117 | £6,667 | 44.1% |
| 3 | FLE030-IVES-BLACKSOLE | Lunar | AMZ | 342 | £13,714 | £5,895 | 43.0% |
| 4 | FLE030-IVES-MIDBLUE | Lunar | AMZ | 239 | £9,428 | £4,041 | 42.9% |
| 5 | FLE030-IVES-BEIGE | Lunar | AMZ | 229 | £9,100 | £3,922 | 43.1% |
| 6 | FLE030-IVES-BLACK | Lunar | AMZ | 205 | £8,431 | £3,748 | 44.5% |
| 7 | FLE030-IVES-GREY | Lunar | AMZ | 190 | £7,463 | £3,199 | 42.9% |
| 8 | JLH950-BLAZE-NAVY | Lunar | AMZ | 140 | £4,894 | £2,272 | 46.4% |
| 9 | FLE030-IVES-RED | Lunar | AMZ | 102 | £3,684 | £1,439 | 39.1% |
| 10 | 1017723-BEND | Birkenstock | SHP | 53 | £5,694 | £1,320 | 23.2% |
| 11 | L7514-14 | Rieker | AMZ | 56 | £3,832 | £1,278 | 33.4% |
| 12 | JLH950-BLAZE-NUDE | Lunar | AMZ | 78 | £2,643 | £1,192 | 45.1% |
| 13 | 0034791-MILANO | Birkenstock | SHP | 59 | £4,271 | £1,082 | 25.3% |
| 14 | 72581-14 | Rieker | AMZ | 43 | £2,677 | £939 | 35.1% |
| 15 | 0034701-MILANO | Birkenstock | SHP | 56 | £4,307 | £921 | 21.4% |
| 16 | B710AP | Goor | SHP | 83 | £2,235 | £867 | 38.8% |
| 17 | 0034703-MILANO | Birkenstock | SHP | 35 | £2,548 | £711 | 27.9% |
| 18 | 1005299-GIZEH | Birkenstock | SHP | 39 | £2,863 | £638 | 22.3% |
| 19 | JLH950-BLAZE-BLACK | Lunar | AMZ | 39 | £1,361 | £632 | 46.4% |
| 20 | 0043691-GIZEH | Birkenstock | SHP | 41 | £2,798 | £601 | 21.5% |
| 21 | 45973-36 | Rieker | AMZ | 35 | £1,993 | £581 | 29.1% |
| 22 | 0051751-ARIZONA | Birkenstock | SHP | 52 | £3,380 | £573 | 17.0% |
| 23 | SHAKE-II-BLACK | Hotter | AMZ | 60 | £3,285 | £565 | 17.2% |
| 24 | 1017721-BEND | Birkenstock | SHP | 51 | £4,698 | £561 | 11.9% |
| 25 | 45973-00 | Rieker | AMZ | 27 | £1,726 | £557 | 32.2% |

### Summary by Brand

| Brand | GP (top 25) | Avg Margin | Key Takeaway |
|-------|-------------|-----------|--------------|
| Lunar (St Ives + Blaze) | ~£57k | 39–46% | Profit engine. 9 St Ives colourways + 3 Blaze = dominant |
| Birkenstock | ~£6.4k | 12–28% | Volume driver but thin margins. Bend best performer |
| Rieker | ~£2.8k | 29–35% | Solid margins, small volumes |
| Goor / Hotter | ~£1.4k | 17–39% | Minor contributors |

### Key Insight

Lunar generates ~8x the gross profit per SKU vs Birkenstock at ~3x the margin. The top single Lunar colourway (St Ives White, £21.9k GP) outearns the entire Birkenstock top 25 combined (~£6.4k). Birkenstock drives Shopify traffic and brand credibility; Lunar pays the bills.

**Action:** Protect Lunar stock depth at all costs. Any Lunar stockout is a direct hit to profit.

### Revenue vs Profit: Birkenstock vs Lunar (12 months)

**Run date:** 2026-02-17

| Brand | Revenue | GP | Margin |
|-------|--------:|---:|-------:|
| Birkenstock (all channels) | £136k | £20k | 14.6% |
| Lunar (all channels) | £142k | £57k | 43.4% |

Revenue is near-identical. Lunar generates ~3x the gross profit.

#### Monthly Breakdown

| Month | Birk Rev | Birk GP | Lunar Rev | Lunar GP |
|-------|--------:|--------:|----------:|---------:|
| Feb '25 | £411 | £141 | £2,449 | £1,072 |
| Mar '25 | £11,507 | £3,499 | £12,556 | £5,356 |
| Apr '25 | £12,896 | £3,153 | £17,232 | £7,476 |
| **May '25** | **£33,689** | **£9,032** | **£26,167** | **£11,091** |
| Jun '25 | £26,292 | £4,241 | £21,949 | £9,123 |
| Jul '25 | £16,014 | **-£157** | £17,997 | £7,451 |
| Aug '25 | £10,492 | £117 | £9,190 | £3,104 |
| Sep '25 | £6,346 | £104 | £8,223 | £2,947 |
| Oct '25 | £6,383 | £25 | £9,654 | £3,591 |
| Nov '25 | £4,185 | £27 | £5,758 | £2,177 |
| Dec '25 | £3,280 | £0 | £4,848 | £1,871 |
| Jan '26 | £2,681 | £17 | £3,249 | £1,247 |
| Feb '26 | £2,112 | £0 | £2,555 | £966 |

#### What This Means

- **Birkenstock has one strong GP month (May)** and one decent month (Mar). Jul onwards margins collapse to zero or negative.
- **Lunar is profitable every single month**, even in winter. Consistent £1–3.5k GP/month off-peak, £7–11k in peak.
- Birkenstock's role is **traffic and brand credibility** on Shopify — people search for it, land on the site. But it ties up cash and only delivers margin in a short spring window.
- **The risk is not Birkenstock itself — it's letting Birkenstock distract from Lunar.** Every pound of cash tied up in Birkenstock stock sitting through winter could be Lunar stock at 43% margin.

**Action:** Never let Lunar stock run low to fund Birkenstock. Birkenstock cash commitment should be seasonal and controlled.

### St Ives Repeat Purchase Analysis

**Run date:** 2026-02-17

| Metric | 12 months | 24 months |
|--------|----------:|----------:|
| Total St Ives customers | — | 428 |
| Repeat buyers | 7 | 11 |
| Repeat rate | — | 2.6% |

Extending from 12 to 24 months only added 4 repeat buyers. These customers are not coming back — it's not a timing issue, it's the nature of the purchase. St Ives is a ~£38 Amazon sandal bought by price-driven shoppers, not brand-loyal ones. They need sandals, they find ours, they buy once.

**What this means for strategy:**
- **No Lunar/St Ives repeat purchase email campaign** — the data says it won't work at 2.6%
- **Lunar growth = new customer acquisition, not retention** — win the Amazon listing, win new buyers
- **Protect Lunar by protecting the listing** — reviews, stock depth, pricing, Buy Box position. That's what drives volume.
- **Klaviyo repurchase efforts stay focused on Birkenstock** — higher price point, brand-conscious Shopify buyers, where loyalty has a realistic chance

---

## 8. Analysis — Birkenstock Off-Season Margin Problem (Mar 2026)

**Run date:** 2026-03-02
**Finding:** Birkenstock off-season (Jul–Feb) is structurally unprofitable. This is not a range width problem — it's a margin problem that affects all styles equally, including the core 15 best sellers.

### The Numbers

| Period | Styles sold | Units | Revenue | GP | Net margin |
|--------|------:|------:|--------:|---:|-------:|
| Peak (Mar–Jun 2025) | 92 | 1,545 | £94,970 | £22,771 | 24.0% |
| Off-season (Jul 2025–Feb 2026) | 115 | 976 | £64,699 | £290 | 0.4% |

Even restricting to only the core 15 best-selling styles:

| Off-season category | Styles | Units | Revenue | GP |
|---------------------|------:|------:|--------:|---:|
| Core 15 best sellers | 15 | 267 | £20,070 | £0 |
| Other 100 styles | 100 | 709 | £44,629 | £290 |

### Root Cause

Discounted selling prices cover product cost but after Shopify fees (~2%), payment processing (~2%), and shipping costs there is no margin left. During peak season, strong demand holds enough price headroom to absorb these costs. Off-season prices drop too low for the fixed per-transaction costs.

This is structural — narrowing the range to fewer styles would not fix it. The core 15 made exactly £0 GP off-season.

### Zermatt Slippers — Not Working

Birkenstock Zermatt slippers were positioned as winter seasonal smoothing products. The data shows they make zero or negative profit in both seasons:
- Zermatt 1014938: **-£354 GP** during peak (26 units clearing at a loss), £0 GP off-season
- Zermatt 1015092: £0 GP off-season despite 29 units sold

These are winter products that lose money even in winter. Reconsider stocking.

### Implications for 2026 Ordering

Heavier Birkenstock orders this year (to extend the selling season past June) carry a specific risk: any stock not sold by end of June will likely sell Jul–Feb at 0% margin. The ideal outcome is stock runs out in June/July, not stock sitting through winter.

**Key question for Sep/Oct ordering:** Can we order tighter quantities targeting sell-through by June/July rather than maximum range? The birkenstock-sales.csv report (£1k+ GP threshold, 360-day window) is the right tool — focus depth on the 15 proven styles, don't order the long tail.

### Lead Time Advantage — Use It

| Brand | Lead time | Implication |
|-------|-----------|-------------|
| Birkenstock | 6 months | Must bet in advance, high risk |
| Lunar (Ives) | **4 days** | React to demand, near-zero risk |
| Rieker | **2 weeks** | React to demand, low risk |

Lunar and Rieker's short lead times are the single biggest strategic advantage in the business. Every pound of growth investment should favour brands where you can respond to actual demand rather than forecast 6 months ahead.

### Lunar Context (Updated Mar 2026)

- Other Lunar styles tested — Ives remains the clear winner
- **Lunar winter books were total failures** — had to clear below cost at end of season. Do not repeat.
- Lunar style exploration should happen **in summer only**, when the customer base is active and testing risk is lowest
- Rieker expansion goes **Amazon only** — no Shopify

---

## 9. Open Consideration — Shopify as a Seasonal Channel (Mar 2026)

**Status:** Under review. No decision made yet.

Shopify is a Birkenstock shop. Last 6 weeks: Birkenstock was 88% of Shopify revenue (£7,309 of £8,306). Non-Birkenstock Shopify brands average ~£1,900/month — not viable as a standalone channel.

Monthly Birkenstock share of Shopify revenue ranges from 71% (Oct) to 93% (Jul), averaging ~85%. Remove Birkenstock and Shopify does ~£23k/year. That's not a business.

Combined with section 8's finding that Birkenstock makes £0 GP from July onwards, this means **Shopify as a channel generates meaningful profit only March–May/June**.

### Option: Treat Shopify + Google Ads as a seasonal operation

- **March–June:** Full Google Ads spend, active stock management, price engine running. This is where the ~£23k GP comes from.
- **July–February:** Cut Google Ads to minimal/zero. Store stays live but on autopilot. Accept ~£3–5k/month organic sales at zero margin — don't spend to drive them.
- **Saving:** Currently ~£16/day Google Ads. Pausing Jul–Feb saves ~£3,900/year in ad spend that was driving zero-margin sales anyway.
- **Risk:** Lose some brand visibility and search ranking continuity over winter. Harder to ramp back up in March? Needs testing.

### Alternative: Find something to sell on Shopify in winter

Nothing has worked so far. Non-Birkenstock brands (Lunar, Skechers, Goor, Roamers) do ~£160/week combined on Shopify. Birkenstock Zermatt slippers failed. Lunar winter books failed. The Shopify customer base searches for Birkenstock — they're not looking for other brands on this site.

### Decision needed

Is Shopify worth investing in year-round, or should it be treated as a 4-month Birkenstock engine with the rest of the year on autopilot? Come back to this after the 2026 spring season with data on whether heavier Birkenstock ordering extends the profitable window past June.

---

## 10. Brand Investigation Pipeline (Mar 2026)

Stabilisation year means no rushed commitments — but always be investigating so we're ready when growth demands it. Ives is approaching its volume ceiling, which makes this pipeline essential for the next phase.

**Principles:**
- Investigation costs nothing. Always be open to approaches from existing suppliers and potential new ones.
- Evaluate against proven benchmarks: Lunar (41% margin, 4-day lead), Rieker (31% margin, 2-week lead).
- Only commit when: margin is proven, lead time is short, and there's a clear gap being filled (not just duplicating what Ives already does).

### Under Investigation

| Brand | Distributor | Status | Why Interesting | Key Questions | Channel |
|-------|-----------|--------|-----------------|---------------|---------|
| **Free Spirit — Frisco** | West Midlands Shoe Company (WMSC), Uttoxeter. enquiries@wmsc.co.uk / 01889 561790 | Investigated Mar 2026 — wholesale price list obtained (SS25). Narrowed to Frisco only. | They approached us (2025). We have SS25 trade price list (`scale/Free Spirit Sterling with RRP.pdf`). Frisco is the standout: 164 Amazon reviews, 4.6–4.7 stars, best-seller in the range. Wholesale £20.95 (ex VAT), RRP £52.50, realistic Amazon sell £38–45. Gross margin 28–37% (same basis as all brands) — not Ives (43%) but solidly between Birkenstock (14%) and Rieker (31%). Ives is at ceiling so this is incremental summer volume in the same demographic. Pack sizes 8 or 12 pairs — low test cost (~£168 for 8 pairs). Also ask about autumn/winter range (boots/closed-toe) which could address the Oct–Feb gap. | Amazon |
| **Waldlaufer** | TBC | Not started | Similar demographic, mentioned in original plan. Lower priority than Rieker. | Wholesale terms, lead time, Amazon viability | Amazon |

### Ruled Out

| Brand | Why |
|-------|-----|
| Skechers | Margins too thin (~16.5%), same problem as Birkenstock |
| TikTok Shop | Wrong demographic |
| Lunar winter books | Total loss, cleared below cost |

### Amazon Price Research (Mar 2026)

Free Spirit styles are widely discounted below RRP on Amazon. Multiple sellers including potentially WMSC themselves (seller ID `A11TUGHSDV22PS`). Shoe Zone, Humphries also discount heavily. Cleveland worst affected (down to £25 on £57.50 RRP). Frisco holds up best at £35–48. This is a price-eroded market — don't expect to sell at RRP.

| Style | Wholesale (ex VAT) | RRP | Amazon Range | Gross Margin (same basis as all brands) |
|-------|----------:|----:|:-----------:|:------------------------:|
| **Frisco** | £20.95 | £52.50 | £35–48 | **28% at £38, 37% at £45** |
| Cleveland | £22.95 | £57.50 | £25–40 | Too eroded — prices near wholesale |
| Fairmont | £20.95 | £52.50 | £30–40 | ~19% at £35 |
| Wickford | £18.95 | £47.50 | ~£35 | ~23% |
| Juliet | £18.95 | £47.50 | £30–45 | Variable |

Margin note: calculated on same basis as all other brands (ex-VAT revenue minus cost, divided by inc-VAT sell price). For context: Ives = 43%, Rieker = 31%, Birkenstock = 14%. Frisco at realistic £38–45 sell = 28–37%, solidly between Birkenstock and Rieker.

**Conclusion:** Frisco is the only style worth testing. Best reviews (164, 4.6 stars), best price resilience, lowest risk.

### Next Actions
- [ ] Contact WMSC — confirm lead time, ask about autumn/winter range, confirm Amazon selling policy (are they competing on Amazon themselves?)
- [ ] If terms are right, test one pack of Frisco (8 or 12 pairs) on Amazon in summer

---

## 11. Decision Log

| Date | Decision | Rationale | Review |
|------|----------|-----------|--------|
| 2026-02-16 | Google Ads daily budget £12 → £14 | Mid-Feb, impressions rising (2,310 on 15th). Baseline ROAS 13.5x. Small step to test before spring ramp. | Check w/c 24 Feb |
| 2026-02-16 | Klaviyo email playbook created | 3 campaign types: Repurchase (90-day), New Arrivals, Clearance. See `scale/KLAVIYO_EMAIL_PLAYBOOK.md` | Launch repurchase first |
| 2026-02-17 | Simplified Klaviyo playbook to one campaign | Stripped back to 90-day Birkenstock non-buyer repurchase only. One segment, one email. Prove it works before adding complexity. | Review after first 2-3 sends |
| 2026-02-28 | Google Ads daily budget £14 → £16 | User-initiated increase. | — |
| 2026-03-02 | Birkenstock off-season confirmed as structural 0% margin | Analysis of Jul–Feb sales: 976 units, £65k revenue, £290 GP. Core 15 styles also £0 GP. Not a width problem — all styles affected equally. | Informs Sep/Oct ordering |
| 2026-03-02 | Zermatt slippers flagged as non-viable | Negative GP in peak, zero GP in winter. Winter product losing money in both seasons. | Review at next order |
| 2026-03-02 | Lunar winter books ruled out permanently | Cleared below cost. Only explore new Lunar styles in summer. | — |
| 2026-03-02 | Rieker confirmed Amazon-only expansion | 33% margin, 2-week lead time. No Shopify. | Expand when cash allows |
| 2026-03-03 | Google Ads hold at £16/day | ROAS 18.1x, all increase criteria met. Only 3 days at £16 — letting algorithm settle. £12→£14 transition was seamless (ROAS improved 11.7x→19.2x). | 7 Mar |
| 2026-03-03 | Ives ceiling acknowledged | Ordering as much as possible, lots of stock, but volume plateauing. Reinforces need to investigate complementary brands for next growth phase. | Ongoing |
| 2026-03-03 | Free Spirit investigated — narrowed to Frisco only | They approached us (2025). Obtained SS25 wholesale price list. Amazon price research shows most styles heavily discounted (Cleveland down to £25 on £57.50 RRP). Frisco holds up best: 164 reviews, 4.6 stars, £35–48 Amazon range, 28–37% gross margin (same basis as all brands). Between Birkenstock and Rieker. Not Ives, but adds incremental summer volume where Ives is capped. Also enquire about winter range. | Contact WMSC to confirm terms and lead time |

---

## 12. Reference

- **Strategy docs:** `scale/` folder
- **DB schema:** `database/DB-Schema.sql`
- **Key tables:** `sales`, `skusummary`, `skumap`, `localstock`, `price_track`, `groupid_performance`, `google_stock_track`
- **Key view:** `shopify_health_check` (Shopify SKU-level health analysis)
- **Dashboard:** `bc_dashboard/Home.py` (Streamlit) - Pilot. Not really working. Remove from here.
- **Identity:** "High-efficiency distribution engine for brands that already dominate demand"
