# Google Ads Budget Review Process

**Created:** 2026-02-20
**Current budget:** £14/day
**Review cadence:** Weekly (every Monday or Tuesday)

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` table | Daily spend, clicks, impressions, Shopify sales, stock levels | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `localstock` table | Current warehouse stock by SKU (source of truth) | `SELECT groupid, SUM(qty) as units FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock' GROUP BY groupid ORDER BY units DESC;` |
| `adcost_summary_30.csv` | Raw Google Ads export (30-day daily breakdown) | Export from Google Ads, save to `google-ads-stocktrack/` folder |

**Note:** `localstock` is the source of truth for Birkenstock stock. Birkenstock is Shopify-only (not on Amazon), so no need to check `amzfeed`.

---

## Key Metrics

| Metric | Floor | Target | Ceiling | Source |
|--------|:-----:|:------:|:-------:|--------|
| ROAS | 5x (minimum profitable) | 7x+ | — | `google_stock_track` |
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

### 2. Check if budget is being hit

Look at `adcost_summary_30.csv` — how many days in the last 7 exceeded or came close to the daily budget? If 3+ days are within £1 of the cap, the budget is constraining.

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

## Decision Rules

### Increase budget (by £2 increments)

ALL of the following must be true:
- ROAS >= 7x for the last 7 days
- Average daily spend is within £1.50 of current budget (budget is constraining)
- Key Birkenstock models have stock (50+ total units across Bend/Milano/Arizona/Gizeh)
- We are in or approaching peak season (Mar-Jul) OR demand is clearly rising (impressions up week-on-week)

### Hold budget

Any of the following:
- ROAS is between 5x and 7x (profitable but not confidently so)
- Average daily spend is well below budget (Google isn't spending it — no point raising)
- Stock is low or patchy (< 50 units across key models)
- Recently changed budget (< 7 days since last change) — let it settle

### Decrease budget (by £2 increments)

Any of the following:
- ROAS < 5x for 2 consecutive weeks
- Stock is critically low (< 20 units across key models)
- Off-season (Nov-Jan) with low impressions and poor conversion

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

## Budget Change Log

| Date | Change | ROAS (7d) | Avg Daily Spend | Stock (units) | Rationale | Next Review |
|------|--------|:---------:|:---------------:|:-------------:|-----------|:-----------:|
| 2026-02-16 | £12 → £14 | 13.5x | ~£11.50 | ~2,100 | Mid-Feb, impressions rising. Small step before spring. | w/c 24 Feb |
| | | | | | | |

---

## Process for Claude Code Review

When asked to review the Google Ads budget:

1. Query `google_stock_track` for last 14 days (daily) and weekly aggregates
2. Query `localstock` for current Birkenstock stock levels (key models)
3. Check the latest `adcost_summary_30.csv` for days hitting the budget cap
4. Compare against the decision rules above
5. Make a recommendation: increase / hold / decrease with reasoning
6. If changing: update the Budget Change Log in this doc and the Decision Log in `scale/SCALE_PLAN.md`
