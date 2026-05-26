# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

The whole process is four reads — **sales, cost, stock, budget** — plus a record of recent changes. Everything below serves that. Keep it lean; if a section stops earning its place, cut it.

## Current State — updated 26 May 2026

- **Structure (single campaign since 14 May):** STANDARD Shopping, full catalogue incl. the 24 BIRK-WINNER styles. PMAX paused 14 May. IVES paused 9 May for the Amazon fair-pricing test; fold IVES SKUs back into STANDARD when that test ends, don't relaunch the standalone.
- **Active cap: £150/day, STANDARD only.** tROAS **400%**, held since Feb.
- **Latest read — 26 May, holding at £150:** 3 full days at £150 cap delivered weekly ROAS 11.7x on real sales (May 19–25 £913 spend / £10.6k sales). Marginal vs £100 cap = 6.8x — above the 5x floor, well below earlier steps. Imp share 88–90% (same as £100 cap) = auction pool is captured at this tROAS. Conv% recovered to 9%, CPC stable at £0.46. Decision: **hold** — signals don't justify another step *today*, but the next push is ROAS-gated, not stock-gated (see Next step).
- **Last change — 23 May ~13:00, £120 → £150 (+25%):** Continued heatwave ride. Same-day second step after the £100→£120 move earlier; signals still green, riding the wave per the no-fixed-learning-window rule.
- **Prior change — 23 May, £100 → £120 (+20%):** Heatwave demand event. 4-day read at £100 cap: blended ROAS ~13x, imp share 91% on an expanding pool, Google overspending £100→£104 every day. Marginal headroom massive.
- **No fixed learning window during a demand event.** Rationale: 5–7 day waits guard against compounding losses, not against responding to live demand. Cadence follows signal, not calendar — keep stepping budget up while signals stay green.
- **Google's own recommendations (noted 23 May, not actioned):** £300/day for +140 conv/wk; tROAS 710%. Not taking either — both are too aggressive to step into mid-wave without round-tripping.
- **Current bias (point-in-time, not a plan):**
  - Push-ready while ROAS stays strong; no fixed waiting window. Five days in this market can be too long — if a single read or two says push, push.
  - Stock recovery isn't a prerequisite. Google's feed may rotate clicks to in-stock alternatives as Arizona/Zermatt/Mayari thin out; headline ROAS is the truth-teller on whether that rotation is working.
  - Cut signals (any): ROAS slipping, weather breaking, conv% dropping. Don't pre-commit to a number — re-read and decide.
  - Don't gate a budget push on "wait for stock to return". Stock matters via ROAS, not as a separate veto. The summer window is finite (see step 7).
- **Open flags:**
  - **Feed-rotation hypothesis to validate:** as ARIZONA-BF-REG/ZERMATT/MAYARI THIN-selling counts climb, Google should naturally rotate clicks to MILANO/GIZEH/PATENT which are healthier. If ROAS holds through the supply degradation, the rotation is working. Watch for per-segment unit-share shifts in next reads.
  - **Diminishing returns curve to revisit post-event:** Apr 14–30 £57/d 14.4x → May 1–8 £89/d 11.8x → May 9–13 £123/d 9.9x → May 19–22 £105/d ~13x → May 23–25 £164/d 11.0x. The May rebound is demand-event, not a structural shift; re-read curve when heat breaks.
  - **Conversion baseline:** Mar 12.1% → Apr 8.7% → May 7.4% median (recovered to 9% in the May 19–25 window). Watch as £150 scales clicks.
  - **Birk stock degrading through the demand event:** 9 May 44 READY styles / 1,180 units → 25 May 31 styles / 850 units. -13 styles, -330 units in 16 days. THIN-selling 32→39. £15k Birk payment 26 May should release allocated stock — watch next snapshot. Not a budget veto (see Next step), but a quality-of-spend concern.

### Recent changes (replaces the old change log — keep last ~6, one line each)

| Date | Move | Why |
|------|------|-----|
| 2026-05-23 ~13:00 | STANDARD £120 → £150 (tROAS 400%) | Second step same day — heatwave still running, signals green, riding the wave. Read pending. |
| 2026-05-23 | STANDARD £100 → £120 (tROAS 400%) | Heatwave. 4-day blended ROAS 13x at £100, imp share 91% on an *expanding* pool, Google overspending to £104/day. Ride the wave; cut sharply when heat breaks. |
| 2026-05-19 | STANDARD £72 → £100 (tROAS 400%) | True imp share ~78% not 86–93% (PMAX-inflated); ROAS ~12x; Google overspending £72. Ceiling ~£100. |
| 2026-05-14 (eve) | STANDARD £105 → £72 (same-day revert) | £105 step had violated "hold at 85%+ imp share"; reverted before midnight, no learning cost. |
| 2026-05-14 | Consolidated to single STANDARD £105; PMAX + IVES paused | PMAX incremental ROAS 2–4x (Google attributed 7.28x was duplicated demand); IVES 3.27x below floor. |
| 2026-05-09 | PMAX £20→£40, STANDARD £60→£72 (combined → £117) | Peak-season push; PMAX imp share 41% the loudest constraint. |
| ~2026-04-28 | Split: STANDARD £60 + PMAX £20 + IVES £5 = £85 | Test per-lever optimisation vs single averaged cap (later reversed 14 May). |

> **Update this block whenever you change anything.** It is the single source of truth for "what's true today" and "what changed recently". There is no separate change log — git history holds anything older than the trail above.

### custom_label_0 conventions

`skusummary.googlecampaign` populates `custom_label_0` in the merchant feed, scoping which styles a campaign targets.

| Label | Meaning |
|---|---|
| `BIRK-WINNER` | READY Birk styles — manually curated, seeded 28 Apr 2026 (24 styles) |
| `NULL` | Everything else |

Maintenance is manual and ad-hoc — add/remove individual styles with one-off SQL when a style thins out or a delivery lands. No automated refresh.

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

### Sizing & rules

- **Budget:** default ~20% step when criteria met, round to £1. Smaller (£2–4) when the algorithm is on a good trajectory. Hold/slow if ROAS <7x, stock thins, or instability after an increase. No fixed schedule — read signals, not dates.
- **tROAS (currently 400%):** *Lower* (→300%) when imp share <85% AND spend below cap (volume play). *Raise* (→500%) when imp share 85%+ AND marginal ROAS <5x, or 7d ROAS sliding on a ramp (efficiency play). One lever at a time; give it 5–7 days to re-learn. Don't move it just because you can.
- **Stock is a fixed constraint, not a lever.** Birk orders are ~6 months ahead and can't be reactively pulled. If high-volume segments are PARTIAL/THIN, trim budget to where it stays efficient and surface the leak for the next buy. **Do not recommend "order more X".**

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
4. Read the latest entry in `birk-stock/snapshots.md` **and compare to the previous entry** — direction of headline / READY-share, and whether the top drags are the same styles run-after-run. **Learning phase: surface the read, don't gate decisions on it yet.** Treat it as context alongside the three constraint numbers, not as a fourth constraint.
5. Cross-reference the **Diagnostic table** — which lever is the constraint?
6. Recommend lever, direction, size, with reasoning. Name the campaign.
7. **Frame the recommendation against the summer window, not just ROAS.** Birk is a 6-month buy with a finite peak (May–Jul). Stock that doesn't move in the window sits for 2–3 months. Pushing volume to convert stock → cash while ROAS is comfortably profitable is a valid trade even when pure marginal-ROAS math says "hold". Cash released also funds the next allocation payment (see [Birk ordering cycle](../README) — payment timing is the short-term stock lever).
8. If changing: update **Current State** AND add a one-line row to **Recent changes**. That block is the only record — nothing is logged elsewhere.
