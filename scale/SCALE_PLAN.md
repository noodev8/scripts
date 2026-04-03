# Brookfield Comfort — Scale to £1M Plan

**Started:** February 2026
**Target:** £1M annual revenue within 3 years (by end of FY 2028/29)
**Approach:** Momentum-based, cash-flow-protected growth

---

## Established Facts

These are confirmed by data analysis. Referenced throughout but stated only here.

- **Birkenstock off-season (Jul-Feb) is structurally 0% margin.** 976 units, £65k revenue, £290 GP. Applies equally to core 15 and long tail. Root cause: discounted prices cover product cost but not Shopify fees + payment processing + shipping. Not fixable by narrowing range.
- **Lunar winter books were total failures.** Cleared below cost. Never repeat.
- **Ives is approaching its volume ceiling.** We order as much as possible but volume is plateauing (Mar 2026).
- **Lunar 4-day lead time is the biggest strategic advantage.** React to demand, not forecast.
- **Rieker: 2-week lead time, ~49% margin, Amazon only.** Lowest-risk expansion route.
- **Shopify is a Birkenstock shop.** Non-Birk brands do ~£160/week combined. Remove Birkenstock and Shopify does ~£23k/year.
- **Shopify generates meaningful profit only Mar-Jun.** Combined with off-season 0% margin finding.

---

## 1. Where We Are Now (Feb 2026)

| Metric | Value | Notes |
|--------|-------|-------|
| Trailing 12-month revenue | ~£310k | Feb '25 - Jan '26 |
| Peak month | £62k (May '25) | Birkenstock spring/summer |
| Trough month | £8k (Jan '26) | Winter low |
| Shopify revenue (12m) | £158k | Birkenstock-led, Google Ads ROAS ~10x |
| Amazon revenue (12m) | £149k | Lunar-led, high margin |
| Total gross profit (12m) | ~£86k | |

### Two Distinct Engines

1. **Shopify + Birkenstock + Google Ads** — Revenue engine. High ROAS (~10x), thin margins (14.7%) but reliable volume.
2. **Amazon + Lunar** — Profit engine. 40%+ margins, lower acquisition cost. Pays the bills.

| Brand | Revenue | Gross Profit | Margin | Channel |
|-------|---------|-------------|--------|---------|
| Lunar | £141k | £57k | 40.6% | Primarily Amazon |
| Birkenstock | £136k | £20k | 14.8% | Primarily Shopify |
| Rieker | £14k | £4k | 30.6% | Amazon |
| Other | £20k | £5k | ~25% | Mixed |

---

## 2. The £1M Path

| Year | Target | Growth | Monthly Avg | Key Focus |
|------|--------|--------|-------------|-----------|
| Year 0 (current) | £310k | baseline | £26k | Stabilise, protect profit |
| Year 1 (FY 26/27) | £500k | +61% | £42k | Scale proven winners, launch retention |
| Year 2 (FY 27/28) | £750k | +50% | £63k | Expand channels, deepen inventory |
| Year 3 (FY 28/29) | £1M+ | +33% | £83k | Full maturity, diversified revenue |

### Where Does £1M Come From?

**Current operations can reach ~£500-630k:**

| Source | Current | Growth Path | Year 2-3 Target |
|--------|--------:|:------------|----------------:|
| Birkenstock/Shopify | £136k | Google Ads scaling, spring/summer push | £250-300k |
| Lunar/Amazon | £142k | Ives stock depth, Buy Box protection | £200-250k |
| Rieker/Other | £32k | Rieker range expansion on Amazon | £50-80k |

**The £630k-£1M gap (~£350-400k) needs new bricks:**

1. **Expand Rieker range on Amazon** — most natural next move. Bring back styles with evidence. Amazon only.
2. **Deeper Birkenstock core on Shopify** — depth on best sellers during peak, not more models.
3. **Lunar new style exploration (summer only)** — 4-day lead time makes testing cheap. But Ives is dominant.
4. **Waldlaufer on Amazon** — similar demographic, evaluate when cash allows.

**2026 is a stabilisation year.** Go deep on proven winners. Investigation is free; commitment costs money.

**Ruled out:** TikTok Shop (wrong demographic), Skechers (margins too thin).

---

## 3. Growth Levers (Prioritised)

### Lever 1: Retention & Repeat Purchase (Low cost, high impact)
- Current repeat rate: 6.8% | Target: 15% within 12 months
- Birkenstock 90-day repurchase email (see `scale/KLAVIYO_EMAIL_PLAYBOOK.md`)
- Klaviyo brand-segmented lifecycle flows, post-purchase education, seasonal alerts
- St Ives repeat rate is 2.6% over 24 months — no retention campaign for Lunar. Growth = new customer acquisition.
- **Impact:** Doubling repeat rate on ~3,000 Shopify customers = ~210 additional orders = ~£12k additional revenue

### Lever 2: Google Ads Scaling (Proven, controlled)
- Current spend: ~£17k/year, ROAS 10x. Headroom to 5x ROAS and still profitable.
- Incrementally increase daily budget, seasonal acceleration (Mar-Jul) and pullback (Nov-Feb)
- **Constraint:** Stock must be available before increasing spend
- **Budget review process:** See `google-ads/BUDGET_REVIEW_PROCESS.md`

### Lever 3: Lunar/Amazon Expansion (Profit growth)
- Maintain relentless Ives stock depth — every stockout day is lost profit
- Explore new styles in summer only when customer base is active
- Protect Amazon margin — don't race to bottom on pricing
- **Impact:** Every £10k Lunar revenue = ~£4k GP vs ~£1.5k GP from Birkenstock

### Lever 4: Seasonal Smoothing (Off-season revenue)
- Nov-Feb currently does £8-16k/month vs £30-62k in peak
- Lunar is profitable year-round (37-43% margin even in winter) — Lunar IS the seasonal smoothing
- Rieker range expansion is the lowest-risk winter revenue growth
- Reduce Google Ads spend Nov-Feb (Birkenstock generates zero profit off-season)

### Lever 5: Operational Efficiency (Protect cash flow)
- Price optimisation engine already running — keep refining
- Stock-aware pricing, inventory turnover monitoring, cash flow forecasting

---

## 4. Key Constraints

1. **Cash flow comes first** — No growth initiative should strain working capital
2. **Profit before revenue** — £500k at 25% margin beats £750k at 10%
3. **Stock before spend** — Never increase ad spend without stock to fulfil
4. **Test before committing** — Every new initiative starts as a small test
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
| Off-season monthly rev | £8-16k | £20k+ | `sales` by month |

---

## 6. Active Next Steps

1. **Model ad spend scenarios** — What does ROAS look like at £25k, £35k, £50k annual spend?
2. **Rieker range expansion plan** — Review previously stocked styles, identify candidates for Amazon relaunch.
3. **Birkenstock ordering review (Sep/Oct)** — Use birkenstock-sales.csv report. Order depth on core 15, target sell-through by June/July. Don't over-order width.

---

## 7. Shopify as a Seasonal Channel (Under Review)

Shopify is a Birkenstock shop (85% of Shopify revenue on average, ranging 71-93%).

### Option A: Treat Shopify + Google Ads as a seasonal operation
- **Mar-Jun:** Full Google Ads spend, active stock management, price engine running. This is where ~£23k GP comes from.
- **Jul-Feb:** Cut Google Ads to minimal/zero. Store on autopilot. Saves ~£3,900/year in ad spend driving zero-margin sales.
- **Risk:** Lose search ranking continuity. Harder to ramp in March? Needs testing.

### Option B: Find something to sell on Shopify in winter
- Nothing has worked so far. Lunar winter, non-Birk brands all failed.

**Decision needed** after 2026 spring season: does heavier Birkenstock ordering extend the profitable window past June?

---

## 8. Brand Investigation Pipeline

Always be investigating so we're ready when growth demands it. Ives approaching ceiling makes this essential.

**Principles:**
- Investigation costs nothing. Always be open.
- Evaluate against benchmarks: Lunar (41% margin, 4-day lead), Rieker (31% margin, 2-week lead).
- Only commit when: margin proven, lead time short, clear gap being filled.

### Active — Testing

| Brand | Status | Economics | Channel |
|-------|--------|-----------|---------|
| **Free Spirit Frisco** | **Live on Amazon FBA.** First sales 21 Mar 2026 (Navy + Smoke Grey, 1 unit each at ~£50). Segment: `FREE-SPIRIT`. 3 Frisco colours + 2 Cleveland stocked (8 units each). Only Frisco Navy and Smoke on Amazon FBA (partial sizes live, rest landing). Black not listed on Amazon. Cleveland not on Amazon. Shopify listed but no sales — Amazon only, same pattern as Rieker. Wholesale £20.95, selling ~£50, **~£27 GP/unit (~52% margin after fees)**. Distributor: WMSC, Uttoxeter. enquiries@wmsc.co.uk / 01889 561790 | Amazon |

### Under Investigation

| Brand | Status | Why Interesting | Channel |
|-------|--------|-----------------|---------|
| **Waldlaufer** | Not started | Similar demographic. Lower priority than Rieker. | Amazon |

### Ruled Out

| Brand | Why |
|-------|-----|
| Skechers | Margins too thin (~16.5%) |
| TikTok Shop | Wrong demographic |

### Next Actions
- [ ] Get full Frisco FBA stock landed (sizes 4, 6, 8 still in transit for Navy/Smoke)
- [ ] Monitor Frisco sell-through rate over Apr-May — target: 5+ units/colour/month
- [ ] Decide on Frisco Black for Amazon listing based on Navy/Smoke performance
- [ ] Cleveland — evaluate whether to list on Amazon or leave as Shopify-only test
- [ ] Ask WMSC about autumn/winter Free Spirit range if summer proves out

---

## 9. Decision Log

| Date | Decision | Rationale | Review |
|------|----------|-----------|--------|
| 2026-02-16 | Google Ads daily budget £12 -> £14 | Mid-Feb, impressions rising. Baseline ROAS 13.5x. | Check w/c 24 Feb |
| 2026-02-16 | Klaviyo email playbook created | See `scale/KLAVIYO_EMAIL_PLAYBOOK.md` | Launch repurchase first |
| 2026-02-17 | Simplified Klaviyo to one campaign | 90-day Birkenstock non-buyer repurchase only. Prove it first. | Review after 2-3 sends |
| 2026-02-28 | Google Ads daily budget £14 -> £16 | User-initiated increase. | - |
| 2026-03-02 | Birkenstock off-season confirmed 0% margin | See Established Facts. | Informs Sep/Oct ordering |
| 2026-03-02 | Lunar winter books ruled out permanently | See Established Facts. | - |
| 2026-03-02 | Rieker confirmed Amazon-only | See Established Facts. | Expand when cash allows |
| 2026-03-03 | Google Ads hold at £16/day | ROAS 18.1x. £12->£14 was seamless (11.7x->19.2x). Letting £16 settle. | 7 Mar |
| 2026-03-03 | Ives ceiling acknowledged | See Established Facts. | Ongoing |
| 2026-03-03 | Free Spirit narrowed to Frisco only | See section 8. | Contact WMSC |
| 2026-03-08 | Google Ads daily budget £16 → £18 | ROAS 19.3x, imp share ~80%, budget constraining, 2,042 stock units. Spring ramp. Switching to ~20% increments every 5 days. | Review 13 Mar |
| 2026-03-25 | Free Spirit Frisco promoted from investigation to active test | First 2 Amazon sales (21 Mar), £27 GP/unit. Stock sent to FBA, partial sizes live. Segment `FREE-SPIRIT` created. | Review end Apr |
| 2026-03-29 | Google Ads daily budget £26 → £32 | ROAS 20.6x, conversion recovered after Mar 23 price changes (12%+ on Mar 27-28). Budget constraining, imp share ~83%. Algorithm already hitting £28-30 on overspend days. | 3 Apr |

---

## 10. Reference

- **Segments & actions:** `scale/CORE_ACTIONS.md`
- **Portfolio analysis:** `scale/PORTFOLIO_ANALYSIS.md` — Ives dependency analysis, unsegmented product assessment, portfolio growth plan
- **Email playbook:** `scale/KLAVIYO_EMAIL_PLAYBOOK.md`
- **Meeting rules:** `scale/MEETING_RULES.md`
- **DB schema:** `database/DB-Schema.sql`
- **Key tables:** `sales`, `skusummary`, `skumap`, `localstock`, `price_track`, `groupid_performance`, `google_stock_track`
- **Key view:** `shopify_health_check`
- **Identity:** "High-efficiency distribution engine for brands that already dominate demand"
