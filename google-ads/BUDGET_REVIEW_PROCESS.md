# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

The whole process is four reads — **sales, cost, stock, budget** — plus a record of recent changes. Everything below serves that. Keep it lean; if a section stops earning its place, cut it.

## Current State — updated 30 May 2026

- **Structure (single campaign since 14 May):** STANDARD Shopping, full catalogue incl. the 24 BIRK-WINNER styles. PMAX paused 14 May. IVES paused 9 May for the Amazon fair-pricing test; fold IVES SKUs back into STANDARD when that test ends, don't relaunch the standalone.
- **Active cap: £100/day, STANDARD only.** tROAS **400%**, held since Feb.
- **Last change — 30 May, £180 → £100 (−44%):** The £180 step (set 28 May ~23:00) failed its first full-day read. 29 May ran £204 spend (Google hard at cap) for **+1 click** vs 28 May, CPC +28% (£0.37 → £0.48), conv 6.8% → 5.2%, ROAS 10x → 6.7x — **marginal ROAS on the £45 increment was negative.** Imp share had been pinned **88–90% for two weeks**, so there was no unserved demand to buy; the budget bought impressions that didn't click. Underlying demand was thinning independently of budget (daily gross £2,972 on 26 May → £1,367 on 29 May, all on the £150 cap) — heatwave subsiding, school resumes next week. (First instinct was £80; 30 May Saturday opened strong — 4 sales / £354 by 09:20 — so landed at £100, inside the proven-profitable £100–150 band rather than below it.)
- **Bias now (point-in-time, not a plan):** Let £100 run and re-read. If today closes 10x+, that's earned evidence to step toward £120–150 *tomorrow* — don't pre-buy on a strong Saturday morning (that's the £180 over-read). If it comes back soft, hold or trim. tROAS holds 400% — budget did the work; don't stack a second lever. Cut/step signals: ROAS, weather, conv% — re-read and decide, don't pre-commit to a number.
- **Ceiling is auction, not shelf (confirmed 29 May):** at 88–90% imp share, the wall is ~£150 — above it you own nearly all the demand Google can show, so budget buys impressions not clicks (£180: +£45 → +1 click). Stock is the *softer* constraint: READY 27 styles / 740 units is still weeks of depth, but pushing volume onto a thinning catalogue erodes conversion as clicks hit broken size grids. Not "out of stock" — out of auction first. The Apr–May expansion (£57/d 14.4x → £123/d 9.9x → £164/d 11x) was a demand event, now breaking.
- **Open flags:**
  - **tROAS has never moved — review it post-event.** Held 400% since Feb; every change for 6 weeks has been budget-only. Two things the constant hides: (1) the 400% target lets Google buy down to **4x marginal — one notch below our stated 5x floor**, which is exactly where the £180 junk spend lived; (2) in a *thinning* market a budget cap forces spend down the quality curve, whereas tROAS throttles on quality automatically — it's the lever built for the season we're entering. **Not a same-day move** (we just changed budget; tROAS needs a 5–7 day re-learn, and one lever at a time). Test signal: once budget settles, if average ROAS still runs 2–3x the target on a stable cap, raise 400% → 500% to align the bid target with the 5x floor.
  - **Stock-availability gate (first-class as of 30 May — see Sizing & rules):** `birk-stock` headline **44% / 24% READY-share, falling across all 3 reads** (49.6 → 44.8 → 44.2). Demand still elevated (7d ~32/d vs 28d ~21/d), so thin grids are biting *real* demand — a hard "don't scale budget" until a landed batch lifts the number. Drags are the Arizona mid-sizes (38–40); ~700u arrived across May but landed in shoulders, so the headline kept falling — **raw arrivals ≠ position lift; only the demand-weighted number counts.** THIN-selling is **not** waste: scarcity converts the last units at full price; low availability caps the *ceiling*, not today's spend.
  - **Conversion baseline:** Mar 12.1% → Apr 8.7% → May 7.4% median (recovered to ~9% in the 19–25 May window). Watch as the cap drops.

### Recent changes (replaces the old change log — keep last ~6, one line each)

| Date | Move | Why |
|------|------|-----|
| 2026-05-30 | STANDARD £180 → £100 (tROAS 400%) | £180 failed its first full day: 29 May ran £204 for +1 click vs 28 May, CPC +28%, conv 6.8%→5.2%, ROAS 10x→6.7x — marginal ROAS negative. Imp share pinned 88–90% (captured pool, no demand to buy above ~£150). Demand thinning independent of budget (gross £2,972 26 May → £1,367 29 May), heat subsiding + school back. Landed £100 not £80 as 30 May Saturday opened strong — inside the proven 10–13x band. |
| 2026-05-28 ~23:00 | STANDARD £150 → £180 (tROAS 400%) — **reverted 30 May** | Thesis was expanding pool / firming marginal ROAS. Wrong: at 88–90% imp share the increment bought impressions not clicks. Don't push budget above ~£150 at this tROAS. |
| 2026-05-23 ~13:00 | STANDARD £120 → £150 (tROAS 400%) | Second step same day — heatwave still running, signals green, riding the wave. Held 26 May: 5-day weekly ROAS 12.9x, conv% recovered to 9.4%, stock degraded as expected but rotation working. |
| 2026-05-23 | STANDARD £100 → £120 (tROAS 400%) | Heatwave. 4-day blended ROAS 13x at £100, imp share 91% on an *expanding* pool, Google overspending to £104/day. Ride the wave; cut sharply when heat breaks. |
| 2026-05-19 | STANDARD £72 → £100 (tROAS 400%) | True imp share ~78% not 86–93% (PMAX-inflated); ROAS ~12x; Google overspending £72. Ceiling ~£100. |
| 2026-05-14 (eve) | STANDARD £105 → £72 (same-day revert) | £105 step had violated "hold at 85%+ imp share"; reverted before midnight, no learning cost. |

> **Update this block whenever you change anything.** It is the single source of truth for "what's true today" and "what changed recently". There is no separate change log — git history holds anything older than the trail above.

### custom_label_0 conventions

`skusummary.googlecampaign` populates `custom_label_0` in the merchant feed, scoping which styles a campaign targets.

| Label | Meaning |
|---|---|
| `BIRK-WINNER` | READY Birk styles — manually curated, seeded 28 Apr 2026 (24 styles) |
| `NULL` | Everything else |

Maintenance is manual and ad-hoc — add/remove individual styles with one-off SQL when a style thins out or a delivery lands. No automated refresh.

### Adding a second campaign — read before acting (note added 1 Jun 2026)

> **DO NOT make any changes for this until you get explicit go-ahead that a second campaign has *actually* been created in Google Ads.** This is a forward note only. While the account is single-campaign, ignore it. Treating it as a to-do before the campaign exists will desync the doc from reality.

When a second campaign does go live, here's what was verified about the system (1 Jun 2026):

- **Ingestion code needs no change.** `update_google_stock_track.py` is already per-campaign aware. As long as the CSV export keeps the same columns (`Day, Campaign, Clicks, Impr., Currency code, Cost, Search impr. share`) and includes **all** campaigns, a new campaign just appears as new rows. `google_campaign_daily` upserts one row per `(date, campaign)` — the source of truth for per-campaign reads.
- **Do NOT combine impression share.** Summing/averaging imp share across campaigns is mathematically meaningless (different auction denominators). The code already handles this: `google_stock_track.google_search_imp_share` is written only when exactly one campaign reports that day, and goes **NULL** with 2+ campaigns *by design*. Read per-campaign imp share from `google_campaign_daily` instead. (The historical 28 Apr–13 May multi-campaign window is already frozen NULL there — same behaviour.)
- **Spend / clicks / impressions still sum fine** in `google_stock_track` — those aggregate correctly. Only imp share doesn't.
- **Process changes needed (in this doc) once it's live:**
  - Rewrite **Current State** from "single campaign" to describe both campaigns and which lever applies to which.
  - In the **Three-Grid / Diagnostic table**, read imp share **per-campaign from `google_campaign_daily`**, not `google_stock_track` (which will be NULL). Grids 1 & 2 (money/demand) still work on summed figures, but ROAS becomes *blended* across campaigns.
  - Add a new `custom_label_0` value for the new campaign and tag its styles via `skusummary.googlecampaign`.
- **The one genuine gap: per-campaign ROAS.** Sales aren't attributed by campaign today — `google_stock_track` ties total spend to total Shopify sales. With two campaigns on different style sets, blended ROAS hides which one performs. Attributing sales by `custom_label_0`/campaign would need new work. Only worth it if the second campaign targets a distinct style set you want to judge on its own.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` | Daily snapshot — spend, clicks, impressions, Shopify sales, stock, Birk ad-readiness counts | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `google_campaign_daily` | **Per-(date, campaign)** clicks/impressions/cost/imp-share. Source of truth for any per-campaign read since 2026-05-04. | `SELECT * FROM google_campaign_daily WHERE snapshot_date >= CURRENT_DATE - 7 ORDER BY snapshot_date DESC, campaign;` |
| `localstock` | Current warehouse stock by SKU — **source of truth for Birk stock** (Birk is Shopify-only, no `amzfeed` needed) | `SELECT groupid, SUM(qty) FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock' GROUP BY groupid;` |
| `adcost_summary_30.csv` | Raw Google Ads export (per-campaign, 30-day daily). Save to Downloads — script auto-moves and processes. | Export from Google Ads UI: Day, Campaign, Clicks, Impr., Cost, Search impr. share. |

**Birk ad-readiness columns** (`google_stock_track`, populated nightly): `birk_ready_styles` (READY count — the convertible-catalogue headline), `birk_ready_units` (depth), `birk_thin_selling_styles` (waste signal). Single-campaign imp share reads from `google_stock_track.google_search_imp_share`; the multi-campaign window 28 Apr – 13 May is NULL there — use `google_campaign_daily`.

### Data gotchas — read before trusting a number

- **Sales-date offset:** `sales.solddate` is a DATE but renders as `23:00 UTC previous day` under BST (`2026-05-18T23:00:00Z` **is 19 May**). Always `solddate::text` for daily figures; treat the latest date as partial (today, still filling). Misread twice on 19 May.
- **Snapshot sales lag:** `google_stock_track.shopify_sales` is captured at script-run time and undercounts late orders. For trends, join `google_stock_track` to `sales` on `solddate` instead.
- **Stock-units sanity:** before treating any stock delta as real, divide by burn (~15 Birk units/day). If burn can't explain it, the number is suspect — verify. Trend reads use `birk_ready_units`/`birk_ready_styles`; current total = `SUM(qty) FROM localstock WHERE deleted=0 AND brand='Birkenstock'`.
- **Capture-before-act:** when the cap changes in the UI, add the Recent-changes row the same day even if reasoning is filled in later. (The £54→£60 ghost change came from skipping this.)
- **Never** use `skusummary.variants` / `skusummary.stockvariants` — stale (see CLAUDE.md). Size universe from `skumap`, live stock from `localstock`.
- **THIN-status sales aren't waste.** Spot-checks of last-sales status mix repeatedly show THIN styles converting at full price — scarcity drives conversion when a customer lands on their size. Before reading a falling READY count as "engine drowning in broken pages", spot-check the actual recent-sales status mix. The doc's earlier "burns clicks on near-empty pages" framing was wrong.
- **Multi-line single-customer orders, same style different sizes = likely try-and-return.** Net them down when reading a big AOV day. Example: 26 May £325 Bend order, sizes 40 + 41 + 41 of two similar styles — customer testing fit.

---

## The Decision Flow

Two levers: **daily budget** (how much Google can spend) and **tROAS** (how aggressively it bids). Pick the lever first, then size the move. Bias to push against: nearly every change has moved budget and held tROAS at 400% — budget has done all the work even where tROAS was the right tool.

Three numbers tell you which lever is the constraint:
1. **Search impression share** — capturing demand, or missing it?
2. **Spend vs cap** — is Google trying to spend more than allowed?
3. **Marginal ROAS** — is the last bit of spend still above the 5x floor?

### Diagnostic table

| 7d ROAS | Imp share | Spend vs cap | Marginal ROAS | Action |
|---------|-----------|--------------|---------------|--------|
| ≥7x | **<85%** | At cap | ≥5x | **Raise budget** (~20% step) |
| ≥7x | **<85%** | **Below cap** | — | **Lower tROAS** — Google can't find auctions at current bar |
| ≥7x | **85%+** | At cap | ≥5x | **Hold** — capturing demand cleanly |
| ≥7x | **85%+** | At cap | **<5x** | **Raise tROAS** — ramp drift; force Google pickier |
| 5x–7x | — | — | — | Hold; run the Three-Grid to find the drag |
| **<5x** for 2 weeks | — | — | — | Decrease budget OR raise tROAS |

**Stock gate overrides this table for budget *increases*.** Every "raise budget" action above assumes stock can fulfil the extra clicks. Before any raise, check the `birk-stock` availability headline — low or falling holds budget regardless of the row (see Sizing & rules).

### Sizing & rules

- **Budget:** default ~20% step when criteria met, round to £1. Smaller (£2–4) when the algorithm is on a good trajectory. Hold/slow if ROAS <7x, stock thins, or instability after an increase. No fixed schedule — read signals, not dates.
- **tROAS (currently 400%):** *Lower* (→300%) when imp share <85% AND spend below cap (volume play). *Raise* (→500%) when imp share 85%+ AND marginal ROAS <5x, or 7d ROAS sliding on a ramp (efficiency play). One lever at a time; give it 5–7 days to re-learn. Don't move it just because you can.
- **Stock availability is a budget *gate*, not a lever (promoted 30 May).** The `birk-stock` demand-weighted availability headline sets the **budget ceiling**; ROAS sets profitability *up to* that ceiling. Apply it as a gate on budget *increases*:
  - Availability **low or falling** → **hold or cut, regardless of ROAS or imp share.** Extra clicks land on broken size grids and conversion erodes — this is what cratered the £180 day (headline was already falling 49.6 → 44.8 across that push).
  - Availability **risen on a landed batch** → ceiling can rise; size the step on ROAS/imp-share as usual.
  - Scarcity still converts the *last* units at full price at the current cap (THIN-selling isn't waste), so a low headline caps the **ceiling** — it does *not* force a cut below where you already sit profitably. Don't pull good spend; just don't *scale* into stock you can't fulfil.
  - **The ceiling only moves when the headline has *actually* risen** — not on a forecast of what's coming. The report (`python birk-stock/availability.py`) is run often/ad-hoc; read whatever the current headline says at any time. A lift typically shows up once a batch physically lands, but the trigger is the *number rising*, not the act of a delivery. Do **not** forecast incoming stock into the decision — Birkenstock may not ship it, or we may not expedite it. Birk orders are ~6 months ahead and can't be reactively pulled; **do not recommend "order more X".**

---

## Three-Grid Snapshot

Quick trend read across the last 3 weeks (three rolling 7-day windows). Run in order: **Money** → if ROAS dropping, **Demand** → if conversion dropping, **Stock**.

### Grid 1 — Money

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

Output: `Date range | Sales | Spend | ROAS`. Healthy ROAS ≥7x. Falling ROAS isn't bad on its own — it's the trigger to look at Grid 2. For more accurate sales, join to `sales` on `solddate` (snapshot-lag gotcha).

### Grid 2 — Demand

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

Output: `Date range | Clicks | Units | Conv % | Cost/click`. Clicks rising + conv % falling = conversion problem → Grid 3. CPC rising sharply = click-cost problem → likely raise tROAS.

### Grid 3 — Stock

Per-segment readiness today.

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

Output: `Segment | Styles | READY | PARTIAL | THIN | THIN-selling | Sold 30d`. PARTIAL on a high-volume segment = clicks landing on broken size grids. THIN-selling = clicks burned on near-empty pages. For per-style detail, drop the segment grouping and select `groupid, colour, sizes_in_stock, total_sizes` from the `readiness` CTE.

---

## Key Metrics

| Metric | Floor | Target | Source |
|--------|:-----:|:------:|--------|
| 7d ROAS | 5x | 7x+ | `google_stock_track` (or `sales` join) |
| Marginal ROAS (incremental new spend) | 5x | 8x+ | week-on-week delta |
| Search impression share | — | 85%+ | `google_campaign_daily` / `google_stock_track` |
| Daily spend vs cap | — | 80%+ of cap | `google_campaign_daily` |
| Ad-ready styles (READY count) | 10+ | 15+ | Grid 3 |
| THIN styles actively selling | 0 ideal | flag for stock review | Grid 3 |

### Baseline conversion (monthly health check)

Daily conversion is noise at ~76 clicks/day — track the **monthly median**, not days.

```sql
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

Median rising m-o-m = fundamentals improving (supports budget moves); dropping = something structural, investigate before raising budget. **Mar 2026 reference:** median 12.3%, IQR 9.8–16.3%.

---

## Seasonal Guidelines

| Period | Approach |
|--------|----------|
| Nov–Jan | Off-season. Pull back, hold or reduce. Protect cash. |
| Feb | Hold or cautious increase. Demand waking. |
| Mar–Apr | Increase if ROAS holds. Spring ramp. |
| May–Jul | Peak. Increase aggressively if ROAS > 5x. |
| Aug–Sep | Start pulling back. Watch ROAS closely. |
| Oct | Reduce to winter baseline. |

---

## Process for Claude Code Review

**Recommendations are point-in-time, not plans.** Each review is fresh. Don't bake future-step triggers into Current State ("push to £180 if X over 5 days"); write today's bias and the signals that would change it, then let the next review decide on the next review's data. The "no fixed learning window" rule applies to your own cadence too — if tomorrow's read says push, push; don't gate on a self-imposed N-day wait.

**Don't analyse stale data** — if the latest `snapshot_date` with ad spend is >2 days old, flag it and wait for confirmation.

1. Run the **Three-Grid Snapshot** for the trend.
2. Read the **three constraint numbers** (imp share, spend vs cap, marginal ROAS).
3. Run **Grid 3** if conversion is dragging.
4. **Run the `birk-stock` position report** (`python birk-stock/availability.py`) — or read the latest `snapshots.md` block and compare to the previous. The demand-weighted **availability headline is a gate, not just context** (see Sizing & rules): it sets the budget ceiling. Read direction of headline / READY-share and whether the top drags are the same styles run-after-run. **A low or falling headline holds/caps budget even if ROAS and imp share say push.** The report is run often, not only at review time — the green light to raise the ceiling is the headline having *actually* risen (read from landed stock), never a forecast of what's due.
5. Cross-reference the **Diagnostic table** — which lever is the constraint?
6. Recommend lever, direction, size, with reasoning. Name the campaign.
7. **Frame the recommendation against the summer window, not just ROAS.** Birk is a 6-month buy with a finite peak (May–Jul). Stock that doesn't move in the window sits for 2–3 months. Pushing volume to convert stock → cash while ROAS is comfortably profitable is a valid trade even when pure marginal-ROAS math says "hold". Cash released also funds the next allocation payment (see [Birk ordering cycle](../README) — payment timing is the short-term stock lever).
8. If changing: update **Current State** AND add a one-line row to **Recent changes**. That block is the only record — nothing is logged elsewhere.
