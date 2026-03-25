# Google Ads Budget Review Process

**Created:** 2026-02-20
**Current budget:** £26/day
**Current tROAS:** 400%
**Review cadence:** As needed — review whenever there's enough new data to act on. No fixed schedule; increase as often as we can safely progress.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` table | Daily spend, clicks, impressions, Shopify sales, stock levels | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `localstock` table | Current warehouse stock by SKU (source of truth) | `SELECT groupid, SUM(qty) as units FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock' GROUP BY groupid ORDER BY units DESC;` |
| `adcost_summary_30.csv` | Raw Google Ads export (30-day daily breakdown) | Export from Google Ads, save to `google-ads/` folder |

**Note:** `localstock` is the source of truth for Birkenstock stock. Birkenstock is Shopify-only (not on Amazon), so no need to check `amzfeed`.

---

## Key Metrics

| Metric | Floor | Target | Ceiling | Source |
|--------|:-----:|:------:|:-------:|--------|
| ROAS | 5x (minimum profitable) | 7x+ | — | `google_stock_track` (shopify_sales / google_ad_spend) |
| Search impression share | — | 85%+ | — | `google_stock_track` (google_search_imp_share) |
| Daily spend vs budget | — | 80%+ of budget | Consistently hitting cap | `adcost_summary_30.csv` |
| Impressions trend | — | Week-on-week growth in spring | — | `google_stock_track` |
| Ad-ready styles (READY count) | 10+ styles | 15+ styles | — | Ad-readiness query (step 3) |
| THIN styles actively selling | 0 ideal | Flag for stock review | — | Ad-readiness query (sold_30d > 0 but THIN) |

---

## Weekly Review Checklist

### 1. Check ROAS (last 7 days vs prior 7 days)

```sql
WITH daily AS (
  SELECT snapshot_date, google_ad_spend::numeric as spend, shopify_sales::numeric as sales
  FROM google_stock_track WHERE google_ad_spend IS NOT NULL
)
SELECT
  'Last 7 days' as period,
  ROUND(SUM(spend), 2) as total_spend,
  ROUND(SUM(sales), 2) as total_sales,
  ROUND(SUM(sales) / NULLIF(SUM(spend), 0), 1) as roas,
  ROUND(AVG(spend), 2) as avg_daily_spend
FROM daily WHERE snapshot_date >= CURRENT_DATE - 7
UNION ALL
SELECT
  'Prior 7 days',
  ROUND(SUM(spend), 2),
  ROUND(SUM(sales), 2),
  ROUND(SUM(sales) / NULLIF(SUM(spend), 0), 1),
  ROUND(AVG(spend), 2)
FROM daily WHERE snapshot_date >= CURRENT_DATE - 14 AND snapshot_date < CURRENT_DATE - 7;
```

### 2. Check search impression share and budget pressure

```sql
SELECT snapshot_date, google_ad_spend, google_search_imp_share
FROM google_stock_track
WHERE google_ad_spend IS NOT NULL
ORDER BY snapshot_date DESC LIMIT 14;
```

**Reading impression share:**
- **85%+** — capturing most available traffic, budget is not limiting
- **70-85%** — missing some traffic, budget may be constraining
- **Below 70%** — significant traffic being missed, budget or tROAS is limiting

Also check `adcost_summary_30.csv` — how many days in the last 7 came close to the daily budget? If 3+ days are within £1 of the cap, the budget is constraining.

### 3. Check stock readiness (ad-readiness by style)

The question isn't "how many units do we have" but "how many styles can actually convert Google clicks right now?" A style with 50 units across all sizes will convert; a style with 5 units in odd sizes wastes ad spend.

Stock is checked via Birkenstock segments defined in `skusummary.segment`. Segments are the source of truth for core lines — see the Segments Google Sheet and `scale/CLAUDE_CONTEXT.md` for full context.

**Readiness levels:**
- **READY** — 70%+ size coverage AND 15+ units. Can fully convert traffic.
- **PARTIAL** — 40%+ coverage AND 5+ units. Some conversions but size gaps lose sales.
- **THIN** — Below thresholds. Mostly wasted clicks.

```sql
WITH current_stock AS (
  SELECT groupid,
    SUM(qty) as units,
    COUNT(DISTINCT code) as sizes_in_stock
  FROM localstock WHERE deleted = 0
  GROUP BY groupid
),
recent_sales AS (
  SELECT groupid,
    SUM(CASE WHEN solddate >= CURRENT_DATE - 30 THEN qty ELSE 0 END) as sold_30d
  FROM sales WHERE channel = 'SHP'
  GROUP BY groupid
)
SELECT
  ss.segment, ss.groupid, ss.colour,
  COALESCE(cs.units, 0) as stock_now,
  COALESCE(cs.sizes_in_stock, 0) as sizes_in_stock,
  ss.variants as total_sizes,
  ROUND(COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(ss.variants, 0) * 100, 0) as size_coverage_pct,
  COALESCE(rs.sold_30d, 0) as sold_30d,
  CASE
    WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(ss.variants, 0) >= 0.7
         AND COALESCE(cs.units, 0) >= 15 THEN 'READY'
    WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(ss.variants, 0) >= 0.4
         AND COALESCE(cs.units, 0) >= 5 THEN 'PARTIAL'
    ELSE 'THIN'
  END as ad_readiness
FROM skusummary ss
LEFT JOIN current_stock cs ON ss.groupid = cs.groupid
LEFT JOIN recent_sales rs ON ss.groupid = rs.groupid
WHERE ss.brand = 'Birkenstock' AND ss.segment IS NOT NULL AND ss.segment != 'CRAP'
  AND ss.shopify = 1 AND ss.googlestatus = 1
ORDER BY ad_readiness, sold_30d DESC;
```

**How to read the results for budget decisions:**
- Count the READY styles and their total units — this is your "convertible catalogue"
- THIN styles that are actively selling (sold_30d > 0) are wasting clicks — flag for stock review
- When a THIN style moves to READY (e.g. delivery arrives), that strengthens the case for a budget increase

### 4. Check stock trend

```sql
SELECT snapshot_date, live_stock_units, live_stock_value
FROM google_stock_track
ORDER BY snapshot_date DESC LIMIT 14;
```

---

## The Two Levers

### 1. Daily Budget
Controls **how much** Google can spend per day. Raising it allows more spend; lowering it caps spend.

### 2. Target ROAS (tROAS)
Controls **how aggressively** Google bids. Currently 400%.
- **Lowering tROAS** (e.g. 400% → 300%) = Google bids on more auctions, more volume, potentially lower efficiency
- **Raising tROAS** (e.g. 400% → 500%) = Google is pickier, less volume, higher efficiency

**Budget is the primary lever.** Only adjust one lever at a time so you can isolate what's driving the result.

### When to consider adjusting tROAS

tROAS should rarely need changing. The following are signals to look for, not rigid triggers — always use judgement based on the full picture.

- **Consider lowering tROAS** (e.g. 400% → 300%): Impression share is low, but spend isn't hitting the budget cap. This means Google can't find enough auctions at the current tROAS bar — lowering it unlocks more volume at slightly lower efficiency.
- **Consider raising tROAS** (e.g. 400% → 500%): ROAS is trending toward the 5x floor and you want to tighten efficiency, or stock is running low and you want to slow volume without cutting budget.
- **Leave it alone**: The algorithm is outperforming the target and budget is the clear constraint. Changing tROAS forces a new learning phase, so don't adjust it just because you can.

**Diagnosing which lever is the constraint:**

| Impression share | Spend vs budget | Constraint | Action |
|-----------------|----------------|------------|--------|
| Low (< 85%) | Hitting cap | Budget | Increase budget |
| Low (< 85%) | Below cap | tROAS | Consider lowering tROAS |
| High (85%+) | Below cap | Neither | Hold — capturing most demand |

---

## Decision Rules

**Important:** These are guidelines, not rigid rules. Each review should use judgement based on what the data is actually showing. Context matters — consider the ROAS trajectory, seasonal timing, and algorithm stability rather than applying thresholds mechanically.

### Increment sizing

- **Default: ~20% increases every 5 days** — percentage-based keeps steps proportional as budget grows. Review every 5 days during peak ramp (Mar–Jul). Round to nearest £1.
- **Hold or slow down** if ROAS drops below 7x, stock runs low, or the algorithm shows instability after an increase.
- **Speed up** (shorten to 4-day reviews) only if ROAS stays well above 10x and impression share is clearly constrained.

### Recommended ramp schedule (from 8 Mar at £18)

This is a guide, not a commitment. Each step requires the increase criteria to be met.

| Review date | Budget | Step | Cumulative |
|-------------|:------:|:----:|:----------:|
| 8 Mar | £18 | — | current |
| 13 Mar | £22 | +£4 | +22% |
| 18 Mar | £26 | +£4 | +44% |
| 23 Mar | £32 | +£6 | +78% |
| 28 Mar | £38 | +£6 | +111% |
| 2 Apr | £46 | +£8 | +156% |
| 7 Apr | £55 | +£9 | +206% |

At any step, if ROAS < 7x or stock drops below threshold, hold at current level until next review.

### Increase budget

ALL of the following must be true:
- ROAS >= 7x for the last 7 days
- Average daily spend is within £1.50 of current budget (budget is constraining)
- Search impression share dropping below 85% (traffic being missed)
- Majority of Birkenstock segment styles are READY (70%+ size coverage, 15+ units) — check ad-readiness query
- We are in or approaching peak season (Mar-Jul) OR demand is clearly rising (impressions up week-on-week)

### Hold budget

Any of the following:
- ROAS is between 5x and 7x (profitable but not confidently so)
- Average daily spend is well below budget (Google isn't spending it — no point raising)
- Search impression share is 85%+ (already capturing most traffic)
- Many segment styles are PARTIAL or THIN (poor size coverage — clicks won't convert)
- Recently changed budget and not yet enough data to assess the impact — let it settle

### Decrease budget

Any of the following:
- ROAS < 5x for 2 consecutive weeks
- Most segment styles are THIN — not enough convertible catalogue to justify spend
- Off-season (Nov-Jan) with low impressions and poor conversion

### Algorithm stability note

When the algorithm is on a good trajectory (ROAS improving week-on-week), favour smaller increments to avoid disrupting its learning. A steady upward path with £2 steps is better than a larger jump that causes the algorithm to re-learn and potentially lose days of efficiency.

---

## Seasonal Guidelines

| Period | Approach | Rationale |
|--------|----------|-----------|
| Nov-Jan | Pull back, hold or reduce | Off-season. Low demand for sandals. Protect cash. |
| Feb | Hold or cautious increase | Demand starts to wake up. Watch impressions. |
| Mar-Apr | Increase if ROAS holds | Spring ramp. Stock should be in. |
| May-Jul | Peak. Increase aggressively if ROAS > 5x | Highest demand. Maximise volume. |
| Aug-Sep | Start pulling back | Demand tailing off. Watch ROAS closely. |
| Oct | Reduce to winter baseline | Transition to off-season. |

---

## Budget & tROAS Change Log

| Date | Change | ROAS (7d) | Imp Share | Avg Daily Spend | Stock (units) | Rationale | Next Review |
|------|--------|:---------:|:---------:|:---------------:|:-------------:|-----------|:-----------:|
| 2026-02-16 | Budget £12 → £14 | 13.5x | ~86% | ~£11.50 | ~2,100 | Mid-Feb, impressions rising. Small step before spring. | w/c 24 Feb |
| 2026-02-20 | tROAS confirmed at 400% | 12.6x | ~90% | ~£13 | ~2,140 | Monitoring only. No change. | w/c 24 Feb |
| 2026-02-28 | Budget £14 → £16 | — | — | — | — | User-initiated increase. | w/c 2 Mar |
| 2026-03-03 | Hold at £16 | 18.1x | ~85% | £15.58 | 1,328 (163 key) | All increase criteria met but only 3 days at £16. Algorithm responding well — sales up, impressions up, ROAS strong. Let it settle, then decide. | 7 Mar |
| 2026-03-08 | Budget £16 → £18 | 19.3x | ~80% | £15.74 | 2,042 | All 5 increase criteria met. ROAS 19.3x (huge headroom), budget constraining (spending to cap daily), imp share ~80% (traffic missed), stock healthy at 2,042 units. March spring ramp. Moving to ~20% increments every 5 days through peak season. | 13 Mar |
| 2026-03-13 | Budget £18 → £22 | 27.1x | ~75% | £17.72 | 2,060 | Per ramp schedule. ROAS 27x, imp share dropping to ~70-75% (traffic being missed), stock healthy. | 18 Mar |
| 2026-03-20 | Budget £22 → £26 | 26.0x | ~77% | £22.35 | 2,292 (224 key) | All criteria met. ROAS 26x, budget constraining (spending to cap), imp share ~77% (traffic missed), stock healthy. Algorithm absorbed £22 cleanly — no efficiency loss. Per ramp schedule. | 25 Mar |
| 2026-03-25 | Hold at £26 | 24.3x | ~87% | £25.37 | 732 (segments), 18 READY | Increase criteria met on paper (ROAS 24x, budget constraining, 18 READY styles). Holding because: (1) Shopify prices adjusted on 23 Mar — 7 increases on Birkenstock best sellers (Gizeh +5%, Arizona +5%, Madrid +6%, Zermatt +7%). (2) Tue 24th conversion crashed to 4.8% (5 units on 104 clicks) vs 13.3% pre-change baseline. Need 2-3 days to confirm whether algorithm settles or prices are suppressing conversion. Also fixed: cron path broken since Mar 20 folder rename (google_ads → google-ads), 4 days backfilled. Stock query now uses ad-readiness (READY/PARTIAL/THIN). | Tonight or 27-28 Mar |
| | | | | | | | |

### Tonight's decision (25 Mar): Increase to £32 or hold?

**Benchmark: today's (25 Mar) conversion rate.**

Pre-change baseline (Mar 16-22): **13.3% conversion** (clicks → units), avg **12.9 units/day**, avg **£642 revenue/day**.

| Today's result | Signal | Action |
|---|---|---|
| **8+ units AND £400+ revenue** | Conversion recovering (10%+). Tuesday was a one-day blip, algorithm adjusting to new prices. | **Increase to £32 tonight** |
| **5-7 units OR £250-400 revenue** | Partial recovery. Not clear yet whether prices or just variance. | **Hold at £26, review Thu/Fri** |
| **< 5 units AND < £250 revenue** | Two bad days in a row. Price changes likely suppressing conversion. | **Hold at £26, review prices on Thu/Fri** |

Note: today already has 2 sales / £212 as of mid-morning, which is a stronger start than yesterday.

### Thu/Fri review (27-28 Mar): Price change impact check

Run these queries to isolate whether the price changes are helping or hurting:

**1. Conversion trend — has it recovered?**

```sql
SELECT snapshot_date, google_clicks,
  shopify_units::integer as units,
  ROUND(shopify_units::numeric / NULLIF(google_clicks, 0) * 100, 1) as conv_pct,
  shopify_sales::numeric as revenue,
  ROUND(shopify_sales::numeric / NULLIF(google_ad_spend::numeric, 0), 1) as roas
FROM google_stock_track
WHERE snapshot_date >= '2026-03-20'
ORDER BY snapshot_date;
```

**Benchmark:** conversion should be back to 10%+ by Thu. If still below 8% across Wed-Thu, the price increases are the likely cause.

**2. Which increased products are still selling?**

Check each product that was increased on 23 Mar — are they converting at the new price?

```sql
SELECT s.groupid, ss.colour,
  pcl.old_price, pcl.new_price,
  SUM(s.qty) as units_since_change,
  ROUND(AVG(s.soldprice)::numeric, 2) as avg_sold_price
FROM sales s
JOIN skusummary ss ON ss.groupid = s.groupid
JOIN price_change_log pcl ON pcl.groupid = s.groupid
  AND pcl.change_date = '2026-03-23' AND pcl.channel = 'SHP'
WHERE s.channel = 'SHP' AND s.solddate >= '2026-03-23' AND s.qty > 0
  AND pcl.new_price > pcl.old_price
GROUP BY s.groupid, ss.colour, pcl.old_price, pcl.new_price
ORDER BY units_since_change DESC;
```

**What to look for:**
- Products selling at the new price = increase is holding, keep it
- Products with zero sales since change but were selling before = price may be too high, consider reverting
- Cross-reference with the velocity-by-price data from the original drill-down

**3. Decision matrix for Thu/Fri:**

| Conversion recovered? | Increased products selling? | Action |
|---|---|---|
| Yes (10%+) | Yes | Price changes are fine. Increase budget to £32. |
| Yes (10%+) | Some not selling | Budget to £32, but revert the non-sellers to old price |
| No (< 8%) | Most not selling | Revert price increases first, then reassess budget |
| No (< 8%) | Yes, selling fine | Something else is off — check impression share, stock, competition |

---

## Process for Claude Code Review

When asked to review the Google Ads budget:

1. Query `google_stock_track` for last 14 days (daily) and weekly aggregates — include `google_search_imp_share`
2. Run the ad-readiness query to check stock by style (READY / PARTIAL / THIN)
3. Check the latest `adcost_summary_30.csv` for days hitting the budget cap
4. Review impression share trend — is it dropping? (signals budget or tROAS constraint)
5. Compare against the decision rules above
6. Make a recommendation: increase / hold / decrease with reasoning
7. If changing: update the Budget & tROAS Change Log in this doc and the Decision Log in `scale/SCALE_PLAN.md`
