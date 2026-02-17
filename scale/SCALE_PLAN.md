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

### Lever 3: Lunar/Amazon Expansion (Profit growth)
- Lunar is the #1 brand by profit with 40%+ margins
- St Ives model has loyal following
- **Actions:**
  - [ ] Identify top-performing Lunar styles and increase stock depth
  - [ ] Test broader Lunar range on Amazon
  - [ ] Evaluate Lunar on Shopify (cross-sell opportunity for Birkenstock buyers?)
  - [ ] Protect Amazon margin — don't race to bottom on pricing
- **Impact:** Every £10k of Lunar revenue = ~£4k GP vs £1.5k GP from Birkenstock

### Lever 4: Seasonal Smoothing (Off-season revenue)
- Nov–Feb currently does £8–16k/month vs £30–62k in peak
- Already improving YoY (+96% to +145% growth in off-season months)
- **Actions:**
  - [ ] Evaluate winter-focused brands/products (boots, slippers)
  - [ ] Birkenstock indoor/wool models for autumn/winter push
  - [ ] Amazon winter strategy (Lunar already has year-round styles?)
  - [ ] Adjust Google Ads strategy for winter — different keywords, different products

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

1. **Launch Birkenstock 90-day repurchase test** — Plan is ready, execute it
2. **Build monthly revenue dashboard** — Track progress against the milestones above
3. **Analyse top 20 SKUs by profit** — Know exactly which products to invest in
4. **Model ad spend scenarios** — What does ROAS look like at £25k, £35k, £50k annual spend?
5. **Map Lunar growth opportunity** — Which styles, which sizes, what's the stock investment needed?

---

## 8. Decision Log

| Date | Decision | Rationale | Review |
|------|----------|-----------|--------|
| 2026-02-16 | Google Ads daily budget £12 → £14 | Mid-Feb, impressions rising (2,310 on 15th). Baseline ROAS 13.5x. Small step to test before spring ramp. | Check w/c 24 Feb |
| 2026-02-16 | Klaviyo email playbook created | 3 campaign types: Repurchase (90-day), New Arrivals, Clearance. See `scale/KLAVIYO_EMAIL_PLAYBOOK.md` | Launch repurchase first |

---

## 9. Reference

- **Strategy docs:** `scale/` folder
- **DB schema:** `database/DB-Schema.sql`
- **Key tables:** `sales`, `skusummary`, `skumap`, `localstock`, `price_track`, `groupid_performance`, `google_stock_track`
- **Key view:** `shopify_health_check` (Shopify SKU-level health analysis)
- **Dashboard:** `bc_dashboard/Home.py` (Streamlit) - Pilot. Not really working. Remove from here.
- **Identity:** "High-efficiency distribution engine for brands that already dominate demand"
