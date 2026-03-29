# Pricing Strategy — Brookfield Comfort (Shopify)

> **Start here.** This document explains how the pricing tools fit together and when to use each one.
> For detailed process steps, see the individual docs linked below.

---

## Starting a Pricing Session

**User says:** "pricing review", "let's do prices", "shopify price check", "run the pricing analysis", or similar.

**Claude does:**

### Step 1 — Refresh & Present (always, every session)

1. Run the 30-day Shopify sales analysis SQL (from [SHOPIFY_PRICE_PLAN.md](SHOPIFY_PRICE_PLAN.md))
2. Check for Google CSVs in `shopify-price/` (benchmark + performance)
3. Present the standard summary:
   - **Overview table**: products sold, units, revenue, net profit, loss-making count
   - **Trend**: last 14 days vs previous 14 days (units/day, revenue/day) — are we up or down?
   - **Daily breakdown**: last 7-10 days with day-of-week, to spot dips or patterns
   - **Top 5 profit earners** (net_profit_total DESC)
   - **Loss makers** (net_profit_per_unit < 0)
   - **Google CSVs**: note if they're present and how fresh they are
4. Present any observations: seasonal trends, learning-phase dips, recent price change impact

### Step 2 — Choose a Gear

Ask: *"Which gear? **Push** (drive volume), **Steady** (optimise), or **Conserve** (protect margins)? Or name a product to drill into."*

If the user isn't sure, help them decide based on the data just presented — stock levels, profit trend, cash flow comments, time of year.

### Step 3 — Run the Gear

**Push:**
- Ensure Google CSVs are present (both benchmark + performance)
- Run Google Phase 1 (`google_price_check.py`) — generates data report with benchmark + performance prices
- Run Phase 2 Grow mode (`google_price_action.py`) — but with performance-aware rules (accept more aggressive drops on high-stock items)
- Present the action report grouped by auto-decision
- Focus attention on: high stock + low sales + performance suggestion available

**Steady:**
- Run Google Phase 1 if CSVs present
- Run Phase 2 in both modes: Grow (decreases) + Protect (increases)
- Present increase candidates from Shopify analysis (filtered to 14+ days since last change)
- Use benchmark as primary target, show performance price as reference
- Offer drill-down on any product the user wants to investigate

**Conserve:**
- Run Google Phase 2 Protect mode only (increases)
- Present Shopify analysis increase candidates (selling well, headroom to RRP)
- Ignore performance suggestions
- Only recommend decreases if stock is truly aging with zero sales

**Surgical (user names a product):**
- Follow the drill-down process in [SHOPIFY_PRICE_PLAN.md](SHOPIFY_PRICE_PLAN.md) Phase 2, Step 1-5
- Show velocity by price point, seasonal comparison, stock context
- Present finding with a specific price recommendation
- Queue the change if user confirms

### Step 4 — Review & Apply

- Present all recommended changes for final review
- User confirms → apply via `google_price_apply.py --confirm`
- Log results to `analysis_log.md`
- Remind about Google learning phase if increases were made (check daily for 3-5 days)

### Step 5 — Between Sessions

If the user comes back in a few days asking "how are the prices doing?" or "did the changes work?":
- Re-run the sales analysis
- Compare to the previous session's numbers (from analysis_log.md)
- Show daily sales around the date changes were applied
- Highlight any products that improved or worsened

---

## The Lever

Pricing is a lever. The goal is always the **optimum price for whatever we're trying to achieve right now**. That changes — sometimes we need cash flow, sometimes we protect margins, sometimes we push a specific product. The tools give us data; we (human + AI) make the call.

### Three Gears

| Gear | When | Goal | Primary Data Source |
|------|------|------|---------------------|
| **Push** | Cash flow needed, high stock, end-of-season, want to grow | Maximise sales volume | Google Performance report + stock levels |
| **Steady** | Normal trading, balanced approach | Optimise profit per product | Google Benchmark + Shopify sales analysis |
| **Conserve** | Stock is lean, margins matter, extracting value | Protect and increase margins | Shopify sales analysis + Benchmark Protect mode |

You can also go **Surgical** — focus on one product at a time using the drill-down analysis. This isn't a separate gear; it's zooming in on any gear.

**Right now there is no automation switching gears.** The human decides which gear based on the business situation (stock levels, cash flow, season, market conditions). Over time the AI can recommend which gear to use, then eventually switch on its own — but not yet.

---

## The Tools

### 1. Shopify Sales Analysis
**What:** 30-day sales data from our own transactions. Units, revenue, net profit per product, stock, price change history, velocity by price point.

**Good for:** Understanding what's actually happening. Finding loss-makers. Finding products with headroom to increase. Drill-down into individual product pricing history.

**When to use:** Every session. This is your baseline — run it first regardless of which gear you're in.

**Process:** See [SHOPIFY_PRICE_PLAN.md](SHOPIFY_PRICE_PLAN.md) for full SQL, summary format, and drill-down steps.

### 2. Google Benchmark Report
**What:** Where our prices sit vs competitors across Google Shopping. Shows benchmark average price, price gap, and click volume per product.

**Good for:** Competitive positioning. Finding products where we're significantly above or below the market. Two modes:
- **Grow mode** — identifies products where we're above benchmark (price decrease candidates)
- **Protect mode** — identifies products where we're below benchmark (price increase candidates)

**When to use:** When you want to check competitive positioning. Especially useful in Steady and Conserve gears.

**Process:** See [GOOGLE_PRICE_PROCESS.md](GOOGLE_PRICE_PROCESS.md) for full pipeline (Phase 1-3).

### 3. Google Performance Report (Sale Price Suggestions)
**What:** Google's view on what prices would drive the most sales volume and clicks on Google Shopping. Shows a suggested price per product with expected click uplift and conversion uplift.

**Good for:** When you want to push sales. The suggestions tend to be lower than current prices — Google is optimising for its own click/conversion metrics, not our profit. But that's exactly what you want when the goal is volume.

**When to use:** Push gear — especially for high-stock items, end-of-season clearance, or products you want to ramp. Also useful as a reference point in Steady gear (shows how far below current price you'd need to go to significantly boost volume).

**Key characteristics:**
- Almost always suggests price decreases (Google wants volume)
- Click/conversion uplift percentages show expected impact
- Effectiveness rating: High / Medium / Low
- May suggest prices below our ideal margin — **that's our call during review**

**Process:** Downloaded alongside benchmark. Incorporated into Phase 1 report as additional columns.

### 4. Combined Overview (Phase 1 Data Report)
**What:** The Phase 1 output (`price_report_YYYY-MM-DD.csv`) now includes all signals per product in one file: current price, cost, RRP, benchmark price, performance price, click/conversion uplift, effectiveness, 30d sales, stock, margin.

**Good for:** Quick scan. Spotting opportunities at a glance. Seeing where the price signals agree or diverge.

**When to use:** Anytime. Run Phase 1 and open the CSV. Especially useful for a general health check or when deciding which gear to be in.

**Process:** Run `google_price_check.py` with both CSVs in the folder. Output is 18 columns per groupid.

### 5. Direct Price Change
**What:** Manual CSV-based price change for specific products. Bypasses the analysis pipeline — just set a price and apply.

**Good for:** Quick surgical changes. Reacting to something you've spotted. Testing a specific price.

**Process:** See [direct-price-change.md](direct-price-change.md).

---

## Process Flow

```
1. ASSESS — Where are we?
   ├── Run Shopify Sales Analysis (fresh 30d data)
   ├── Download both Google CSVs (benchmark + performance)
   └── Check stock levels, cash position, season

2. DECIDE — Which gear?
   ├── Cash tight / stock high / end of season → Push
   ├── Normal trading / balanced → Steady
   └── Stock lean / margins thin → Conserve

3. ANALYSE — Use the right tools for the gear
   │
   ├── PUSH
   │   ├── Run Google Phase 1 (includes performance prices)
   │   ├── Focus on products with: high stock + low/no sales + performance suggestion
   │   ├── Run Grow mode — consider performance price as target for high-stock items
   │   └── Accept more aggressive drops than you would in Steady
   │
   ├── STEADY
   │   ├── Run Google Phase 1 + Phase 2 (Grow + Protect)
   │   ├── Use benchmark as the primary target
   │   ├── Reference performance price but don't chase it by default
   │   ├── Review Shopify analysis increase candidates (14+ days since last change)
   │   └── Drill into specific products where signals conflict
   │
   └── CONSERVE
       ├── Run Google Phase 2 Protect mode only
       ├── Focus on increase candidates from Shopify analysis
       ├── Ignore performance suggestions (they always say drop)
       └── Only decrease if a product is truly dead and stock is aging

4. REVIEW — Human (or AI with rules) decides per product
   ├── Auto-decision rules pre-sort: accept / review / reject / increase
   ├── Human reviews "review" items, overrides as needed
   ├── Mark change=1 to accept, change=0 to skip
   └── Add notes explaining reasoning (builds the training data)

5. APPLY — Execute changes
   ├── Dry run first: python google_price_apply.py <file>.csv
   ├── Apply: python google_price_apply.py <file>.csv --confirm
   └── Nightly sync pushes to Shopify + Google Merchant

6. MONITOR — Did it work?
   ├── Check daily sales for 3-5 days (Google learning phase on increases)
   ├── Re-run Shopify analysis next week to compare
   └── Log results in analysis_log.md
```

---

## Auto-Decision Rules

The AI pre-sorts recommendations into categories to reduce manual review. These rules evolve as we learn what works. The human always has final say.

**Current rules** (defined in `google_price_action.py`):

| Decision | Rule | Reasoning |
|----------|------|-----------|
| **Reject** | Stock = 0 | No point changing price with nothing to sell |
| **Reject** | 2+ sold in 30d, low stock | Selling fine, low stock = let it run |
| **Increase** | 2+ sold in 30d, stock >= 3 | Selling well with stock = room to test higher (+5%) |
| **Review** | Drop > 20% | Large drop might be right but needs human eyes |
| **Review** | 10+ sold near current price in 365d | Proven demand at this price — seasonal lull? |
| **Accept** | Stock >= 5, sold <= 1, drop <= 15% | Has stock, not selling, modest drop |
| **Review** | Everything else | Mixed signals — human decides |

**Performance-aware rules** (implemented):
- All auto_reason text includes the performance price when available, e.g. `(perf: £58.95)`
- Drops of 15-25% that would normally go to "review" are upgraded to "accept" when the performance report independently agrees AND stock >= 5 AND item isn't selling AND no proven demand — this is the borderline tiebreaker

**Planned enhancements** (to be built as we learn):
- Factor in net profit per unit (protect high-margin products even if they match accept rules)
- Factor in seasonality (out-of-season = different thresholds)
- Factor in **sellable stock** not just total stock (stock in sizes that have sold in the past year — fringe sizes with no sales history shouldn't count toward stock-based decisions)
- Factor in stock age / incoming stock (heavy stock = more aggressive)
- Factor in price change history (avoid yo-yo — reject if changed < 14 days ago)
- Gear-aware rules (Push mode accepts more aggressively, Conserve mode rejects more)

---

## Guardrails (Always Apply, All Gears)

These are hard limits that never get overridden:

1. **Never below cost + 10% margin** (after VAT adjustment)
2. **Never above RRP**
3. **Respect min/max price bounds** (skusummary.minshopifyprice / maxshopifyprice)
4. **Skip ignore_auto_price = 1 products**
5. **Max 3-4 price increases per batch** — Google Shopping learning phase causes 1-3 day dip after increases. Decreases recover immediately.
6. **14+ days between changes on same product** — avoids yo-yo pricing, gives data time to emerge
7. **All changes logged** to price_change_log with reason notes
8. **Use sellable stock, not total stock** — stock in sizes with zero sales in the past year is dead weight, not inventory. During drill-downs always check size distribution vs sales history. Auto-rules currently use total stock; sellable stock is a planned enhancement

---

## Cost Constants (Shopify Net Profit)

Used in all profit calculations. Update here if costs change.

| Cost | Value | Notes |
|------|-------|-------|
| Payment fee | £0.30 + 2.9% of price | Shopify Payments |
| VAT | price / 6 | Only when tax = 1 |
| Wages/packing | £1.00 per unit | Rounded up for confidence |
| Postage | £3.44 per unit | Royal Mail average |

```
net_profit = soldprice - VAT - cost - payment_fee - wages - postage
```

---

## Key Data Sources

| Source | Table | What It Tells Us | Freshness |
|--------|-------|-----------------|-----------|
| Our sales | `sales` (channel='SHP') | What actually sold, at what price, net profit | Live |
| Current prices | `skusummary.shopifyprice` | What we're charging right now | Live |
| Warehouse stock | `localstock` | How much we have | Live |
| Amazon stock | `amzfeed.amzlive` | FBA inventory | Live |
| Price history | `price_change_log` | Every change with reason, date, who | Live |
| Performance metrics | `groupid_performance` | Annual profit, margin, recommended price | Weekly refresh |
| Daily snapshots | `price_track` | Historical price/stock/sales per day | Nightly |
| Google benchmark | CSV download | Competitor prices | Manual download |
| Google performance | CSV download | Google's volume-optimised price suggestions | Manual download |

---

## Document Map

| Document | What It Covers |
|----------|---------------|
| **This file** (PRICING_STRATEGY.md) | High-level strategy, which tool when, gears, flow |
| [SHOPIFY_PRICE_PLAN.md](SHOPIFY_PRICE_PLAN.md) | Shopify sales analysis process, SQL, drill-down steps |
| [GOOGLE_PRICE_PROCESS.md](GOOGLE_PRICE_PROCESS.md) | Google report pipeline (Phase 1-3), auto-decision rules |
| [direct-price-change.md](direct-price-change.md) | Manual one-off price changes |
| [analysis_log.md](analysis_log.md) | Historical analysis runs and results |

---

## How the AI Learns

Every time we review recommendations and accept/reject/modify them, the notes we add become training data. Over time:

1. **Rules get refined** — thresholds adjusted based on what we actually accept vs reject
2. **New rules emerge** — patterns in our decisions that can be codified
3. **Confidence grows** — more auto-accepts, fewer reviews needed
4. **Eventually: autonomous** — AI runs the full cycle, human spot-checks

We're currently in the **human-in-the-loop** phase. The AI proposes, the human decides, and the decisions feed back into better rules.
