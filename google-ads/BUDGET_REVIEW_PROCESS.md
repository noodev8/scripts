# Google Ads Budget Review Process

**Created:** 2026-02-20
**Review cadence:** As needed — review whenever there's enough new data to act on. No fixed schedule.

## Current State — updated 8 May 2026

- **Campaign structure (new — restructured ~28-29 Apr 2026):**
  - **Standard Shopping** — core campaign, holds the full catalogue including the winning Birks (which are also in PMAX). £72/day (raised from £60 — decided 8 May, midnight-effective so first full day at £72 is 9 May).
  - **PMAX (winning Birks)** — own campaign, duplicates the Birk SKUs that were performing in standard. £40/day (doubled — decided 8 May, midnight-effective so first full day at £40 is 9 May). Will re-enter learning phase.
  - **IVES Shopping** — own campaign, IVES SKUs only, removed from standard. £5/day.
  - **Combined daily cap: £117**
- **tROAS:** 400% on STANDARD. PMAX and IVES have no tROAS set — leaving the algorithm uncapped on those for now (Google's recommendation of 620% on PMAX is below historical 12–17x performance; setting it now would loosen efficiency).
- **Last review:** 8 May 2026 — STANDARD £60→£72; PMAX £20→£40; IVES held at £5; reverted IVES Shopify list prices (see IVES note below)
- **Next planned step:** re-evaluate STANDARD and PMAX ~Thu 15 May after 5–7 days at the new caps
- **Open flags:**
  - April conversion median 9.3% vs March 12.1% — still watching
  - **IVES Fair-Pricing concern (8 May):** Shopify list dropped to £28.99 ~5/6 May; AMZ daily IVES units dropped from ~28/day (late Apr) to ~14/day (4–7 May). Pattern fits Amazon's Marketplace Fair Pricing detection (Buy Box suppression on big external-price gaps). Reverted all 10 IVES groupids to pre-drop list prices on 8 May, with WHITE pushed up to £38.99 (236 AMZ units; protect Amazon channel). Watch AMZ recovery over 3–7 days.
  - Search impression share on standard will drop materially post-restructure (PMAX wins internal auctions on duplicated Birks; IVES gone from standard) — the metric is now reading a smaller competitive pool, not weakening demand. Don't compare standard's imp share pre/post-restructure.
- **Per-campaign data captured (added 2026-05-04):** `google_campaign_daily` table stores per-(date, campaign) clicks/impressions/cost/search_imp_share. Populated nightly from `adcost_summary_30.csv` (per-campaign export). `google_stock_track` ad columns continue to hold per-date sums; `google_search_imp_share` is frozen at historical values (no longer populated — aggregated metric ill-defined post-restructure). **Conversion data is still per-day only** — Google Ads conversion-by-campaign export not wired up; for ROAS attribution between standard/PMAX/IVES, paste the conversions report in chat.
- **Snapshot-sales-lag caveat:** `google_stock_track.shopify_sales` captures the day's sales at script-run time and can lag actual end-of-day total when late orders file after the snapshot. For trend reads, prefer joining `google_stock_track` to `sales` on `solddate` rather than using `shopify_sales` directly. (Discovered 30 Apr — Apr 29 stored £544 vs actual £920.)
- **Capture-before-act rule:** when the budget is changed in the UI, add a line to the change log the same day, even if rationale is filled in later. The £54→£60 ghost change happened because this didn't.

> **Update this block whenever you change anything below — including the change log.** It is the single source of truth for "what's true today".

### custom_label_0 conventions

`skusummary.googlecampaign` populates `custom_label_0` in the merchant feed. Used to scope which styles a campaign targets.

| Label | Meaning |
|---|---|
| `BIRK-WINNER` | READY Birk styles — manually curated, seeded 28 Apr 2026 from the readiness query (24 styles) |
| `NULL` | Everything else |

**Maintenance is manual and ad-hoc.** Add or remove individual styles with one-off SQL as needed (e.g. when a style thins out or a delivery lands). No automated refresh, no full rebuild rule yet — keep it deliberate while the campaign is finding its feet.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` table | Daily snapshot — spend (sum across campaigns), clicks (sum), impressions (sum), Shopify sales, stock levels, Birk ad-readiness counts | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `google_campaign_daily` table | **Per-(date, campaign)** — clicks, impressions, cost, search_imp_share. Source of truth for any per-campaign read since 2026-05-04. | `SELECT * FROM google_campaign_daily WHERE snapshot_date >= CURRENT_DATE - 7 ORDER BY snapshot_date DESC, campaign;` |
| `localstock` table | Current warehouse stock by SKU (source of truth) | `SELECT groupid, SUM(qty) as units FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock' GROUP BY groupid ORDER BY units DESC;` |
| `adcost_summary_30.csv` | Raw Google Ads export (per-campaign, 30-day daily breakdown). Save to Downloads — script auto-moves and processes. | Export from Google Ads UI with the per-campaign columns: Day, Campaign, Clicks, Impr., Cost, Search impr. share. |

**Birk ad-readiness columns in `google_stock_track`** (populated nightly from `update_google_stock_track.py`, definition matches step 3 below):
- `birk_ready_styles` — count of READY styles (≥70% size coverage AND ≥15 units). The convertible-catalogue headline. Watch for it ticking up when deliveries land.
- `birk_ready_units` — total stock units across READY styles. Depth check.
- `birk_thin_selling_styles` — count of THIN styles that sold ≥1 in last 30d. The waste signal — clicks paid for, sale missed.

For trend analysis, query the columns directly:
```sql
SELECT snapshot_date, birk_ready_styles, birk_ready_units, birk_thin_selling_styles
FROM google_stock_track
ORDER BY snapshot_date DESC LIMIT 14;
```
For per-style detail (which styles are THIN, which sizes missing) still use the standalone query in step 3.

**Note:** `localstock` is the source of truth for Birkenstock stock. Birkenstock is Shopify-only (not on Amazon), so no need to check `amzfeed`.

---

## Three-Grid Snapshot

The quick-read framework for "should I bump the budget?" Run these three grids in sequence. Each answers one question; together they decide hold / bump / pull back. Drill deeper using the Weekly Review Checklist below if a grid flags something.

### Order matters

1. **Money first** — is ROAS still healthy, and how is it trending?
2. **If ROAS is dropping → Demand** — is the cause click cost or conversion?
3. **If conversion is dropping → Stock** — can the catalogue actually convert what's arriving?

### Stock is a fixed constraint, not a lever

Birkenstock orders are placed **~6 months in advance** and cannot be reactively restocked to fix leaks. What's currently in the warehouse plus what's already on the way is the stock universe for the next several weeks. The job of the ad budget is to **match spend to the catalogue we have**, not to assume stock can be ordered to fit a budget plan.

Implication: if Stock shows persistent leaks (PARTIAL/THIN on top sellers) and they aren't appearing on incoming invoices, the right response is to **trim ad budget to where it stays efficient**, not to wait for restock that isn't coming. If £45/day produces the same revenue as £60/day, the cap should drop.

**Do not recommend "order more X" as an action.** Surface the leak so the user can factor it into the next 6-month buy, but adjust ad budget around current stock reality.

### Restructure context (post 28-29 Apr 2026)

The grids below aggregate across all three campaigns (Standard + PMAX + IVES). For per-campaign reads, use `google_campaign_daily` (populated nightly since 2026-05-04). Per-campaign **conversion** data is not yet captured — for ROAS attribution between standard / PMAX / IVES, paste the conversions report in chat.

Two reading rules while the new structure is bedding in:

1. **Don't aggregate `search_imp_share` across campaigns.** Read it per campaign from `google_campaign_daily`. The combined-imp-share metric isn't well-defined when each campaign competes in a different eligible-auction pool. `google_stock_track.google_search_imp_share` is frozen at historical (pre-restructure) values — new dates will be NULL.
2. **For sales totals, prefer `sales` table over `google_stock_track.shopify_sales`.** The stored column captures sales at script-run time and can lag end-of-day total — significant on days when the snapshot runs before all orders file. Join on `solddate = snapshot_date` for accurate ROAS reads.

The "Decrease budget" rule about THIN-selling styles applies catalogue-wide regardless of which campaign carries those SKUs.

### Grid 1 — Money

Three rolling 7-day windows. Shows ROAS direction across the last 3 weeks.

```sql
WITH d AS (
  SELECT snapshot_date,
         google_ad_spend::numeric AS spend,
         shopify_sales::numeric AS sales
  FROM google_stock_track
  WHERE snapshot_date >= CURRENT_DATE - 22 AND snapshot_date < CURRENT_DATE
    AND google_ad_spend IS NOT NULL
)
SELECT
  CASE
    WHEN snapshot_date >= CURRENT_DATE - 7 THEN 3
    WHEN snapshot_date >= CURRENT_DATE - 14 THEN 2
    ELSE 1
  END AS sort_key,
  CASE
    WHEN snapshot_date >= CURRENT_DATE - 7  THEN TO_CHAR(CURRENT_DATE - 7,  'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 1, 'Mon DD')
    WHEN snapshot_date >= CURRENT_DATE - 14 THEN TO_CHAR(CURRENT_DATE - 14, 'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 8, 'Mon DD')
    ELSE                                         TO_CHAR(CURRENT_DATE - 21, 'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 15,'Mon DD')
  END AS date_range,
  ROUND(SUM(sales), 0) AS sales,
  ROUND(SUM(spend), 0) AS spend,
  ROUND(SUM(sales) / NULLIF(SUM(spend), 0), 1) AS roas
FROM d
GROUP BY 1, 2
ORDER BY 1;
```

Output shape: `Date range | Sales | Spend | ROAS`. Healthy ROAS >7x. ROAS trending down ≠ bad on its own, but it's the trigger to look at Grid 2.

### Grid 2 — Demand

Same three windows. Tells you whether a falling ROAS is a click-cost problem (Google getting more expensive) or a conversion problem (clicks not buying).

```sql
WITH d AS (
  SELECT snapshot_date,
         google_ad_spend::numeric AS spend,
         google_clicks AS clicks,
         shopify_units AS units
  FROM google_stock_track
  WHERE snapshot_date >= CURRENT_DATE - 22 AND snapshot_date < CURRENT_DATE
    AND google_clicks IS NOT NULL
)
SELECT
  CASE
    WHEN snapshot_date >= CURRENT_DATE - 7 THEN 3
    WHEN snapshot_date >= CURRENT_DATE - 14 THEN 2
    ELSE 1
  END AS sort_key,
  CASE
    WHEN snapshot_date >= CURRENT_DATE - 7  THEN TO_CHAR(CURRENT_DATE - 7,  'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 1, 'Mon DD')
    WHEN snapshot_date >= CURRENT_DATE - 14 THEN TO_CHAR(CURRENT_DATE - 14, 'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 8, 'Mon DD')
    ELSE                                         TO_CHAR(CURRENT_DATE - 21, 'Mon DD') || '–' || TO_CHAR(CURRENT_DATE - 15,'Mon DD')
  END AS date_range,
  SUM(clicks) AS clicks,
  SUM(units) AS units,
  ROUND(SUM(units)::numeric / NULLIF(SUM(clicks), 0) * 100, 1) AS conv_pct,
  ROUND(SUM(spend) / NULLIF(SUM(clicks), 0), 2) AS cost_per_click
FROM d
GROUP BY 1, 2
ORDER BY 1;
```

Output shape: `Date range | Clicks | Units | Conv % | Cost/click`. If clicks rising and conv % falling = conversion problem → Grid 3. If CPC rising sharply = click-cost problem → check Google Ads UI for auction pressure.

### Grid 3 — Stock

Per-segment readiness today (single snapshot). Tells you whether the conversion drop has a stock cause and which segments are leaking.

```sql
WITH size_universe AS (
  SELECT groupid, COUNT(DISTINCT code) AS total_sizes
  FROM skumap WHERE deleted = 0 GROUP BY groupid
),
current_stock AS (
  SELECT groupid, SUM(qty) AS units, COUNT(DISTINCT code) AS sizes_in_stock
  FROM localstock WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0
  GROUP BY groupid
),
recent_sales AS (
  SELECT groupid,
    SUM(CASE WHEN solddate >= CURRENT_DATE - 30 THEN qty ELSE 0 END) AS sold_30d
  FROM sales WHERE channel = 'SHP' GROUP BY groupid
),
readiness AS (
  SELECT
    ss.segment, ss.groupid,
    COALESCE(rs.sold_30d, 0) AS sold_30d,
    CASE
      WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.7
           AND COALESCE(cs.units, 0) >= 15 THEN 'READY'
      WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.4
           AND COALESCE(cs.units, 0) >= 5 THEN 'PARTIAL'
      ELSE 'THIN'
    END AS status
  FROM skusummary ss
  LEFT JOIN size_universe su ON ss.groupid = su.groupid
  LEFT JOIN current_stock cs ON ss.groupid = cs.groupid
  LEFT JOIN recent_sales rs ON ss.groupid = rs.groupid
  WHERE ss.brand = 'Birkenstock' AND ss.segment IS NOT NULL AND ss.segment != 'CRAP'
    AND ss.shopify = 1 AND ss.googlestatus = 1
)
SELECT
  segment,
  COUNT(*) AS styles,
  SUM(CASE WHEN status='READY' THEN 1 ELSE 0 END) AS ready,
  SUM(CASE WHEN status='PARTIAL' THEN 1 ELSE 0 END) AS partial,
  SUM(CASE WHEN status='THIN' THEN 1 ELSE 0 END) AS thin,
  SUM(CASE WHEN status='THIN' AND sold_30d > 0 THEN 1 ELSE 0 END) AS thin_selling,
  SUM(sold_30d) AS sold_30d
FROM readiness
GROUP BY segment
ORDER BY sold_30d DESC;
```

Output shape: `Segment | Styles | READY | PARTIAL | THIN | THIN-selling | Sold 30d`. PARTIAL on a high-volume segment = clicks landing on broken size grids. THIN-selling = clicks being burned on near-empty pages.

**Once `birk_ready_styles` history accrues (~2 weeks from 2026-04-27)**, replace Grid 3 with the same 3-week trend shape as Money/Demand using the `google_stock_track` columns.

### Reading the three together

| Money | Demand | Stock | Read |
|---|---|---|---|
| ROAS healthy & flat/rising | — | — | Bump candidate |
| ROAS dropping | CPC stable, conv falling | High-volume segments PARTIAL/THIN | Hold — fix stock first |
| ROAS dropping | CPC rising | — | Click-cost issue, check tROAS / auction pressure |
| ROAS dropping | Conv stable, clicks falling | — | Demand softening — seasonal or competitive |
| ROAS approaching 5x | — | — | Pull back |

---

## Key Metrics

| Metric | Floor | Target | Ceiling | Source |
|--------|:-----:|:------:|:-------:|--------|
| ROAS | 5x (minimum profitable) | 7x+ | — | `google_stock_track` (shopify_sales / google_ad_spend) |
| Search impression share (per campaign) | — | 85%+ | — | `google_campaign_daily` (search_imp_share) |
| Daily spend vs cap (per campaign) | — | 80%+ of cap | Consistently hitting cap | `google_campaign_daily` (cost) |
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

Per-campaign — read directly from `google_campaign_daily` (source of truth since the per-campaign CSV format went live):

```sql
SELECT snapshot_date, campaign, cost, clicks, search_imp_share
FROM google_campaign_daily
WHERE snapshot_date >= CURRENT_DATE - 14
ORDER BY snapshot_date DESC, campaign;
```

`search_imp_share` is NULL when Google reports `< 10%` (campaign losing most auctions) or `--` (reporting lag — usually clears within 1-2 days).

**Reading impression share (per campaign):**
- **85%+** — capturing most available traffic, that campaign's budget is not limiting
- **70-85%** — missing some traffic, budget may be constraining
- **Below 70%** — significant traffic being missed, budget or tROAS is limiting on that campaign
- **NULL persistently (not lag)** — campaign at `<10%`. Either lift its cap or accept it's a niche role.

**Don't aggregate imp share across campaigns.** The combined-imp-share number isn't well-defined post-restructure (Google computes it per campaign against that campaign's eligible auction pool). `google_stock_track.google_search_imp_share` is frozen at its pre-restructure historical values; new dates will be NULL there. Use the per-campaign table.

**Cap pressure** — combine the spend column with the campaign's known daily cap:

```sql
SELECT campaign,
       ROUND(AVG(cost), 2) AS avg_daily_spend,
       SUM(CASE WHEN cost >= cap_minus_1 THEN 1 ELSE 0 END) AS days_at_cap
FROM (
  SELECT campaign, cost,
         CASE campaign
           WHEN 'STANDARD'    THEN 60 - 1
           WHEN 'BIRK-WINNER' THEN 20 - 1
           WHEN 'IVES'        THEN  5 - 1
         END AS cap_minus_1
  FROM google_campaign_daily
  WHERE snapshot_date >= CURRENT_DATE - 7
) d
GROUP BY campaign;
```

If a campaign shows 3+ of 7 days at/over its cap, that campaign's budget is constraining. Update the CASE arms when you change a daily cap (or move them to a `campaign_caps` table when there are more than three).

### 3. Check stock readiness (ad-readiness by style)

The question isn't "how many units do we have" but "how many styles can actually convert Google clicks right now?" A style with 50 units across all sizes will convert; a style with 5 units in odd sizes wastes ad spend.

Stock is checked via Birkenstock segments defined in `skusummary.segment`. Segments are the source of truth for core lines — see the Segments Google Sheet and `scale/CLAUDE_CONTEXT.md` for full context.

**Readiness levels:**
- **READY** — 70%+ size coverage AND 15+ units. Can fully convert traffic.
- **PARTIAL** — 40%+ coverage AND 5+ units. Some conversions but size gaps lose sales.
- **THIN** — Below thresholds. Mostly wasted clicks.

**IMPORTANT — do not use `skusummary.variants` or `skusummary.stockvariants`** as the size-universe denominator. Both fields are stale (see CLAUDE.md). The size universe comes from `skumap` (the master (groupid, code) catalogue, one row per size). Do NOT use `localstock` for the denominator either — it does not preserve historical empty sizes (e.g. a style with 14 sizes in skumap may only have 4 codes in localstock if 10 sizes are currently empty), so it under-states the universe.

```sql
WITH size_universe AS (
  -- Total sizes per groupid from skumap (master catalogue, deleted=0 excludes retired sizes).
  -- Source of truth for "how many sizes does this style have".
  SELECT groupid, COUNT(DISTINCT code) AS total_sizes
  FROM skumap
  WHERE deleted = 0
  GROUP BY groupid
),
current_stock AS (
  -- Live stock: sizes currently sellable (#FREE, not deleted, qty > 0).
  SELECT groupid,
    SUM(qty) as units,
    COUNT(DISTINCT code) as sizes_in_stock
  FROM localstock
  WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0
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
  COALESCE(su.total_sizes, 0) as total_sizes,
  ROUND(COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) * 100, 0) as size_coverage_pct,
  COALESCE(rs.sold_30d, 0) as sold_30d,
  CASE
    WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.7
         AND COALESCE(cs.units, 0) >= 15 THEN 'READY'
    WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.4
         AND COALESCE(cs.units, 0) >= 5 THEN 'PARTIAL'
    ELSE 'THIN'
  END as ad_readiness
FROM skusummary ss
LEFT JOIN size_universe su ON ss.groupid = su.groupid
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

### 20%-every-5-days projection (guide, not a plan)

This is what 20% steps look like if criteria hold every time. **Each session decides on the day** against decision rules and current data — these dates and amounts are not a commitment. Tick `[x]` when a step is taken; leave `[ ]` for future projections.

Projection from the current £60 cap (28 Apr 2026):

| Target date | Budget | +20% from | Status |
|-------------|:------:|:---------:|:------:|
| Sun 3 May | £72 | £60 | [ ] |
| Fri 8 May | £86 | £72 | [ ] |
| Wed 13 May | £103 | £86 | [ ] |
| Mon 18 May | £124 | £103 | [ ] |
| Sat 23 May | £149 | £124 | [ ] |
| Thu 28 May | £179 | £149 | [ ] |
| Tue 2 Jun | £215 | £179 | [ ] |
| Sun 7 Jun | £258 | £215 | [ ] |
| Fri 12 Jun | £310 | £258 | [ ] |

If ROAS dips, conversion stalls, or stock thins, the next-step decision skips or holds. Don't chase the dates.

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

Recent entries (last ~6 weeks) keep full rationale. Older entries collapsed to one-liners for scan speed — full rationale lives in git history.

### Archive: Feb–Mar 2026

| Date | Change | ROAS (7d) | Imp Share | Note |
|------|--------|:---------:|:---------:|------|
| 2026-02-16 | £12 → £14 | 13.5x | ~86% | Small step before spring. |
| 2026-02-20 | tROAS confirmed at 400% | 12.6x | ~90% | Monitoring only. |
| 2026-02-28 | £14 → £16 | — | — | User-initiated. |
| 2026-03-03 | Hold £16 | 18.1x | ~85% | Letting £16 settle. Algorithm responding well. |
| 2026-03-08 | £16 → £18 | 19.3x | ~80% | Spring ramp begins. ~20% steps every 5 days from here. |
| 2026-03-13 | £18 → £22 | 27.1x | ~75% | Per ramp. Imp share dropping. |
| 2026-03-20 | £22 → £26 | 26.0x | ~77% | Per ramp. Algorithm absorbed £22 cleanly. |
| 2026-03-25 | Hold £26 | 24.3x | ~87% | Hold to check Mar 23 Birk price-change impact (conv crashed 24th). |
| 2026-03-29 | £26 → £32 | 20.6x | ~83% | Conv recovered. Algorithm already overspending £26 cap. |

### Recent

| Date | Change | ROAS (7d) | Imp Share | Avg Daily Spend | Stock (units) | Rationale | Next Review |
|------|--------|:---------:|:---------:|:---------------:|:-------------:|-----------|:-----------:|
| 2026-04-03 | Budget £32 → £38 | 21.6x | ~83% | £30.63 | 2,248 (18 READY) | All 5 criteria met. ROAS 21.6x, budget constraining (3/7 days at cap, overspent to £39.68), imp share 82-85%, stock healthy. Algorithm absorbed £32 with zero efficiency loss. Conversion holding at 11.7% into April. £38 formalises what Google is already trying to spend on high-demand days. Effective midnight 3 Apr. | 8 Apr |
| 2026-04-10 | Budget £38 → £42 | 16.1x (post-Easter 18.7x) | 62-68% ↓ | £38.35 | 1,352 Birk local (17 READY, 454u) | Conservative +11% step vs schedule's +21%. Easter weekend (Apr 3-6) + 16 Birk price changes on Apr 5 confounded 4 days of conversion. Post-Easter days (Apr 7-9) ROAS 18.7x, conv recovering (Apr 8 = 11.6%). Imp share crashed to 62-68% — Google clearly has room. Smaller step protects algorithm while still riding the wave; gives clean diagnostic for next review. tROAS held at 400%. Effective immediately. | 15 Apr |
| 2026-04-17 | Budget £42 → £50 | 18.1x (last 7d), 17.0x (14d) | 73.9% avg 7d (67.1% on Apr 15) ↓ | £43.23 | 2,826 live units; ~20 READY Birk styles, 666u in READY across 7 segments | All 5 criteria met. ROAS 18.1x vs 7x floor (huge headroom). Imp share trending down 84→79→74% — budget constraining. Algorithm already overspent to £47.47/£47.66 on Sun 12/Mon 13 at 23.6x/16.0x ROAS — Google signalling it wants more. Behind ramp schedule (was due £55 on Apr 7; held cautious after post-Easter slowdown). Stock abundant: 2,826 live units, Birk burn 10.9/day. Weekly rev ramp confirmed: £5.8k (w/c Feb 9) → £11.3k (w/c Apr 6). +19% step, midnight-effective to give clean Sat (strongest weekday) as first full day. tROAS held at 400%. | ~22-23 Apr (Tue/Wed after full Sat/Sun data) |
| 2026-04-21 | Budget £50 → £54 | 15.4x (last 7d) | 87.5% (Apr 18, only £50-day with data) | £46.52 | 2,839 live units | Conservative +8% nudge. Google overspent £50 cap on both clean days (£59.10 Apr 18, £55.45 Apr 19) at 15.6x combined ROAS. £54 formalises what Google is already trying to spend — no algorithm re-learn risk. Midnight-effective so Tue 21 Apr is first full day. Per algorithm-stability guidance: smaller step preserves learning while still riding the wave. Leaves room for full +15-20% step to £60-62 in 3-5 days if ROAS holds. tROAS held at 400%. User has paid £7.5k Birk invoice — stock pipeline secured. | ~24-25 Apr |
| ~2026-04-22 (logged retrospectively 28 Apr) | Budget £54 → £60 | — | — | — | — | **Corrective entry — change made by user, not logged at the time.** User raised cap to £60 a day or two after the £54 step, after a strong Mon 20 Apr (£1,143 sales, 20u). Bigger step than the £54 recommendation; user informed Claude in another session but the log was never updated. Exact date unknown — spend pattern (Apr 22 onwards: £57, £52, £61, £59, £66, £61) fits a £60 cap (typical 0-10% Google flex) better than £54 (would imply 10-22% flex daily). Effective from ~Apr 22. tROAS held at 400%. | 28 Apr |
| 2026-04-28 | Hold at £60 | 13.4x (last 7d) | 71% avg 7d ↓ | £59.35 | 2,861 live; 20 READY (652u), 9 PARTIAL, 10 THIN | All 5 increase criteria met (ROAS 13.4x, spend at cap, imp share 71% trending down, 20 READY = best yet, peak season). HOLD because: £60 wasn't logged so this is effectively the first proper week at £60; April conv 9.3% vs March 12.1% — needs to confirm baseline; marginal week-on-week ROAS only 2x; 11 THIN-selling styles wasting clicks. Yesterday's good Monday is one data point. Stock action: flag THIN-selling Zermatt/Mayari for restock. | Sun 3 May (re-check vs £72 projection) |
| ~2026-04-28/29 | Campaign restructure: split into Standard £60 + PMAX £20 (winning Birks, duplicated) + IVES £5 = £85 combined | 13.7x (last 7d, actuals) | 71% (standard, last clean day Apr 28) | £66 (Apr 23-29 avg) | 2,861 live; 24 READY (759u, best yet), 6 THIN-selling | Hypothesis: split lets each lever optimise where intent is strongest rather than averaging across catalogue. PMAX captures branded/discovery on winners; IVES gets its own bidding logic; standard remains the core safety net. Spend +57% over 3 weeks delivered only +13% daily revenue (diminishing returns curve at single-cap level) — restructure aims to lift the conversion floor without raising overall cap. Effective ~28-29 Apr (exact date logged retrospectively — Apr 29 was the first day showing post-restructure spend pattern: £101.73 vs £60 standard cap, imp share collapsed to <10% on standard, both expected). tROAS held at 400% across all three. Per-campaign tracking deferred — will reassess after 7-10 days. | ~Mon 5 May |
| 2026-04-30 | Hold all three caps (£60/£20/£5 = £85) | 13.7x (last 7d, actuals from sales table) | n/a — metric unstable post-restructure | £66 avg 7d | 2,861 live; 24 READY, 6 THIN-selling | Restructure 1-2 days old. Apr 29 alone (first post-restructure day) ran £101.73 spend / £919.50 actual sales = 9x ROAS — within normal PMAX-launch flex against £85 cap. Revenue trend across 3 weeks is up (£800→£822→£903 daily) but spend +57% bought only +13% revenue → diminishing returns at single-cap level was the reason to restructure. Marginal ROAS 5.67x — above 5x floor but tight. Too early to read the new structure. Hold to give PMAX 5-7 days of learning. | Mon 5 May |
| 2026-05-09 (decided 8 May, midnight-effective) | PMAX (BIRK-WINNER) £20 → £40; STANDARD held £60; IVES held £5. Combined £85 → £105. | 11.8x (last 7d, sales-table joined) | STANDARD ~83% / PMAX ~41% / IVES ~23% | £88 avg 7d combined | 2,861 live; 23 READY (751u), 7 THIN-selling | All five increase criteria met. PMAX is the loudest constraint: imp share 41%, Google overspent to £33.59 on a single £20-cap day, 4/7 days at cap. 19/24 BIRK-WINNER styles converting on Shopify since 28 Apr launch (61 units / £3,785 revenue vs £196 spend — naive ROAS 19x). User-led aggressive step: doubling PMAX during peak season with stock at strongest-yet level (23 READY); accepting learning-phase re-entry. STANDARD held — already at ~83% imp share (close to target) and at £60 marginal headroom is smaller. IVES held at £5 budget; price action taken instead (see IVES Fair-Pricing flag in Current State). tROAS held at 400% on STANDARD; PMAX and IVES remain uncapped — not setting Google's 620% suggestion since historical ROAS 12–17x sits well above it. | ~Thu 15 May (after 5–7 days of PMAX learning at £40, first full day 9 May) |
| 2026-05-09 (decided 8 May, midnight-effective) | STANDARD £60 → £72 (+20%) — same session as PMAX bump above. Combined £105 → £117. | 9.7x–16.7x bounds (last 7d; STANDARD spend £435.14 vs non-IVES revenue £7,256 / non-PMAX-non-IVES revenue £4,218 — true ROAS likely 12–15x given PMAX only spent £196 over 10 days) | Daily series shows imp share collapsing inside last 7d: 91.6 / 86.0 / 86.4 / 88.8 / **70.0 / 73.4** / -- — last 3 days fell ~18 points, classic budget-constrained signal | £62.16 avg 7d, max £70.21 (Google overspent £60 cap by 17% on May 3) | 2,861 live; 23 READY (751u) — strongest yet | All five increase criteria met independent of PMAX context. ROAS deeply above 7x floor; Google demonstrated £70.21 day at £60 cap; imp share crash from 88% → 70% over May 4–6 is the budget-constraint signal; catalogue strength at peak. 20% step matches the standard ramp shape; £72 stays inside what Google has already shown it can spend. tROAS held at 400%. | ~Thu 15 May (alongside PMAX re-eval) |

---

## Process for Claude Code Review

When asked to review the Google Ads budget:

**Important:** Do not run budget analysis on stale data. Check the latest `snapshot_date` with ad spend data first — if it is more than 2 days old, flag it and wait for user confirmation before proceeding.

1. Query `google_stock_track` for last 14 days (daily) and weekly aggregates (spend, clicks, impressions, ad-readiness)
2. Query `google_campaign_daily` for per-campaign cost, clicks and `search_imp_share` (last 14 days). Use this — not `google_stock_track.google_search_imp_share` — for any imp share read.
3. Run the ad-readiness query to check stock by style (READY / PARTIAL / THIN)
4. Check per-campaign cap pressure (3+ of 7 days at/over a campaign's cap = constraining)
5. Review per-campaign impression share trend — is any campaign dropping? (signals budget or tROAS constraint on that specific campaign)
6. Compare against the decision rules above
7. Make a recommendation: increase / hold / decrease with reasoning — name the campaign(s) the change applies to
8. If changing: update the Current State block at the top AND add an entry to the Budget & tROAS Change Log in this doc. **Do not log budget changes in `scale/SCALE_PLAN.md`** — single source of truth lives here.
