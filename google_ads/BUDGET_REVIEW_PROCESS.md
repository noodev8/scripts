# Google Ads Budget Review Process

**Created:** 2026-02-20
**Current budget:** £16/day
**Current tROAS:** 400%
**Review cadence:** As needed — review whenever there's enough new data to act on. No fixed schedule; increase as often as we can safely progress.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` table | Daily spend, clicks, impressions, Shopify sales, stock levels | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `localstock` table | Current warehouse stock by SKU (source of truth) | `SELECT groupid, SUM(qty) as units FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock' GROUP BY groupid ORDER BY units DESC;` |
| `adcost_summary_30.csv` | Raw Google Ads export (30-day daily breakdown) | Export from Google Ads, save to `google_ads/` folder |

**Note:** `localstock` is the source of truth for Birkenstock stock. Birkenstock is Shopify-only (not on Amazon), so no need to check `amzfeed`.

---

## Key Metrics

| Metric | Floor | Target | Ceiling | Source |
|--------|:-----:|:------:|:-------:|--------|
| ROAS | 5x (minimum profitable) | 7x+ | — | `google_stock_track` (shopify_sales / google_ad_spend) |
| Search impression share | — | 85%+ | — | `google_stock_track` (google_search_imp_share) |
| Daily spend vs budget | — | 80%+ of budget | Consistently hitting cap | `adcost_summary_30.csv` |
| Impressions trend | — | Week-on-week growth in spring | — | `google_stock_track` |
| Birkenstock stock (total units) | 50+ units | 100+ units | — | `localstock` |
| Key model stock (Bend, Milano, Arizona, Gizeh) | Sizes in stock | Good size coverage | — | `localstock` |

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

### 3. Check stock levels

```sql
SELECT groupid, SUM(qty) as units, COUNT(DISTINCT code) as size_variants
FROM localstock
WHERE deleted = 0 AND brand = 'Birkenstock'
AND groupid IN ('1017723-BEND','1017721-BEND','0034791-MILANO','0034701-MILANO','0034703-MILANO','0051751-ARIZONA','1005299-GIZEH','0043691-GIZEH')
GROUP BY groupid
ORDER BY units DESC;
```

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

- **Default: £2 increments** — preferred when the algorithm is learning well and ROAS is improving. Small steps preserve algorithm stability and avoid resetting the learning phase.
- **£4 increments** may be appropriate when ROAS has significant headroom (e.g. 15x+ with a 5x floor), impression share is clearly constrained, and we are entering peak season. Use judgement — if in doubt, go with £2 and review sooner.

### Increase budget

ALL of the following must be true:
- ROAS >= 7x for the last 7 days
- Average daily spend is within £1.50 of current budget (budget is constraining)
- Search impression share dropping below 85% (traffic being missed)
- Key Birkenstock models have stock (50+ total units across Bend/Milano/Arizona/Gizeh)
- We are in or approaching peak season (Mar-Jul) OR demand is clearly rising (impressions up week-on-week)

### Hold budget

Any of the following:
- ROAS is between 5x and 7x (profitable but not confidently so)
- Average daily spend is well below budget (Google isn't spending it — no point raising)
- Search impression share is 85%+ (already capturing most traffic)
- Stock is low or patchy (< 50 units across key models)
- Recently changed budget and not yet enough data to assess the impact — let it settle

### Decrease budget

Any of the following:
- ROAS < 5x for 2 consecutive weeks
- Stock is critically low (< 20 units across key models)
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
| 2026-02-28 | Budget £14 → £16 | — | — | — | — | User-initiated increase. | — |
| | | | | | | | |

---

## Process for Claude Code Review

When asked to review the Google Ads budget:

1. Query `google_stock_track` for last 14 days (daily) and weekly aggregates — include `google_search_imp_share`
2. Query `localstock` for current Birkenstock stock levels (key models)
3. Check the latest `adcost_summary_30.csv` for days hitting the budget cap
4. Review impression share trend — is it dropping? (signals budget or tROAS constraint)
5. Compare against the decision rules above
6. Make a recommendation: increase / hold / decrease with reasoning
7. If changing: update the Budget & tROAS Change Log in this doc and the Decision Log in `scale/SCALE_PLAN.md`
