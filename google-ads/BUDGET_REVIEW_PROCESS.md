# Google Ads Budget Review Process

**Created:** 2026-02-20
**Current budget:** £38/day
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

## Baseline Conversion Rate (Monthly Health Check)

Daily conversion rates are noisy — at our volume (~76 clicks/day, ~9 units/day), a single multi-buy customer or a quiet afternoon can swing the day by 10 percentage points. Don't react to individual days. Instead, track the **baseline conversion rate** monthly.

### How to calculate it

1. Pull all daily conversion rates for the month (clicks → Shopify units)
2. Sort them lowest to highest
3. The **median** (middle value) is the baseline — half your days are above, half below. Unlike an average, one 22% spike day or one 3% crash day can't distort it.
4. The **baseline band** is the interquartile range (IQR) — the middle 50% of days. This is the range where "normal" days land.

```sql
-- Monthly baseline conversion rate (median + IQR)
SELECT
  TO_CHAR(snapshot_date, 'YYYY-MM') AS month,
  COUNT(*) AS days,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    GREATEST(shopify_units::integer, 0)::numeric / NULLIF(google_clicks, 0) * 100
  ), 1) AS median_conv_pct,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY
    GREATEST(shopify_units::integer, 0)::numeric / NULLIF(google_clicks, 0) * 100
  ), 1) AS q1_conv_pct,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY
    GREATEST(shopify_units::integer, 0)::numeric / NULLIF(google_clicks, 0) * 100
  ), 1) AS q3_conv_pct
FROM google_stock_track
WHERE google_clicks IS NOT NULL AND google_clicks > 0
  AND snapshot_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
GROUP BY TO_CHAR(snapshot_date, 'YYYY-MM')
ORDER BY 1;
```

### How to read it

- **Median rising month-over-month** (e.g. Feb 8% → Mar 12%) = business fundamentals improving, supports budget increases
- **Median stable** = steady state, budget decisions based on other factors (ROAS, impression share)
- **Median dropping** (e.g. 12% → 7%) = something structural has changed — investigate before increasing budget. Could be: price changes suppressing conversion, stock gaps, seasonal shift, or competitive pressure.

### March 2026 reference

- Median: **12.3%**
- Baseline band (IQR): **9.8% – 16.3%** (14 of 24 days)
- Outlier bad days (under 6%): 3 days — normal, always bounce back within 1-2 days
- Outlier great days (over 17%): 5 days — don't use these to justify decisions

At current volume, expect this pattern every month: ~3 bad days, ~3 great days, ~20 steady days in the baseline band. As budget scales and daily clicks increase, variance reduces naturally.

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
| 2026-03-25 | Hold at £26 | 24.3x | ~87% | £25.37 | 732 (segments), 18 READY | Holding to check price change impact: 7 Birkenstock increases on 23 Mar, conversion crashed to 4.8% on 24th. Need 2-3 days to confirm recovery. | 27-28 Mar |
| 2026-03-29 | Budget £26 → £32 | 20.6x | ~83% | £26.47 | 2,264 (18 READY) | Conversion recovered to baseline (12%+ on Mar 27-28). Price changes not suppressing. Budget constraining (spending to cap daily), imp share 80-85% (traffic missed). Algorithm already spending £28-30 on overspend days — £32 formalises that with small stretch. Spring peak, ROAS has huge headroom above 7x floor. | 3 Apr |
| 2026-04-03 | Budget £32 → £38 | 21.6x | ~83% | £30.63 | 2,248 (18 READY) | All 5 criteria met. ROAS 21.6x, budget constraining (3/7 days at cap, overspent to £39.68), imp share 82-85%, stock healthy. Algorithm absorbed £32 with zero efficiency loss. Conversion holding at 11.7% into April. £38 formalises what Google is already trying to spend on high-demand days. Effective midnight 3 Apr. | 8 Apr |

---

## Process for Claude Code Review

When asked to review the Google Ads budget:

**Important:** Do not run budget analysis on stale data. Check the latest `snapshot_date` with ad spend data first — if it is more than 2 days old, flag it and wait for user confirmation before proceeding.

1. Query `google_stock_track` for last 14 days (daily) and weekly aggregates — include `google_search_imp_share`
2. Run the ad-readiness query to check stock by style (READY / PARTIAL / THIN)
3. Check the latest `adcost_summary_30.csv` for days hitting the budget cap
4. Review impression share trend — is it dropping? (signals budget or tROAS constraint)
5. Compare against the decision rules above
6. Make a recommendation: increase / hold / decrease with reasoning
7. If changing: update the Budget & tROAS Change Log in this doc and the Decision Log in `scale/SCALE_PLAN.md`
