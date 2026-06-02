# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

The whole process is three reads — **sales, cost, budget** — plus a record of recent changes. Everything below serves that. Keep it lean; if a section stops earning its place, cut it.

## Current State — updated 2 June 2026

- **Structure (single campaign since 14 May):** STANDARD Shopping, full catalogue incl. the 24 BIRK-WINNER styles. PMAX paused 14 May. IVES paused 9 May for the Amazon fair-pricing test; fold IVES SKUs back into STANDARD when that test ends, don't relaunch the standalone.
- **Active cap: £140/day, STANDARD only.** tROAS **400%**, held since Feb.
- **Last change — 2 Jun, £100 → £140 (+40%):** £100 was leaving demand on the table. Imp share had collapsed to **52% (30 May)** vs 88–96% at the £150–180 caps, and raw impressions literally halved (£100 ≈ 8–9k/day vs £150–180 ≈ 15–18k) — Lost IS is **budget**, not rank (bids unchanged). Google overspending the cap every day it could (£120 on 1 Jun; £87 by 18:30 on 2 Jun, pacing ~£115). ROAS strong and stable: 7d **11.0x**, daily 9–16x at the £100 cap, three rolling weeks 10.8 / 11.7 / 11.0x. Marginal spend in the £100→£150 band is *proven* — it ran ~12x for six straight days (19–28 May) with conversion holding 7–12%. Laddered to £140 rather than straight to £150 to avoid a single-signal over-read (the discipline the £180 flop taught).
- **The £180 failure was an auction wall (re-diagnosed 2 Jun):** at 96% imp share the £45 increment bought ~3k extra impressions for **+1 click** — junk inventory Google scraped to spend the cap (we never even got the clicks). The real ceiling is the *convertible-demand pool*, ~£165 at this tROAS — above it, budget buys impressions, not clicks. **£165+ is the junk line — don't cross it.** (Daily gross stabilised ~£1,400 for 5 days to 1 Jun — the heat-spike unwind settled at a healthy baseline, not thinning further.)
- **Bias now (point-in-time, not a plan):** Let £140 run and watch closely. Step to £150 if it holds 10x+ with impressions climbing back toward 12k+ (imp share recovering). If ROAS drops under ~8x, conv under ~6%, or impressions don't recover, that's the new wall — hold/trim. £150 is the current step target; never cross £165 (the junk line). tROAS holds 400% — one lever at a time.
- **Open flags:**
  - **tROAS has never moved — review it post-event.** Held 400% since Feb; every change for 6 weeks has been budget-only. Two things the constant hides: (1) the 400% target lets Google buy down to **4x marginal — one notch below our stated 5x floor**, which is exactly where the £180 junk spend lived; (2) in a *thinning* market a budget cap forces spend down the quality curve, whereas tROAS throttles on quality automatically — it's the lever built for the season we're entering. **Not a same-day move** (we just changed budget; tROAS needs a 5–7 day re-learn, and one lever at a time). Test signal: once budget settles, if average ROAS still runs 2–3x the target on a stable cap, raise 400% → 500% to align the bid target with the 5x floor.
  - **Conversion baseline:** Mar 12.1% → Apr 8.7% → May 7.4% median (June MTD 7.5%; recovered to ~9% in the 19–25 May window). Watch as the cap rises.

### Recent changes (replaces the old change log — keep last ~4, one line each)

| Date | Move | Why |
|------|------|-----|
| 2026-06-02 | STANDARD £100 → £140 (tROAS 400%) | £100 left demand unserved: imp share 52% (30 May) vs 88–96% at £150–180, impressions halved (8–9k vs 15–18k), Google overspending cap (£120 1 Jun; £87 by 18:30 2 Jun). 7d ROAS 11x; £100→£150 band proven ~12x for 6 days (19–28 May). Re-diagnosed £180 as an auction wall (+1 click for +£45 at 96% IS). Laddered to £140 not £150 to avoid single-signal over-read; £165+ is the junk line. |
| 2026-05-30 | STANDARD £180 → £100 (tROAS 400%) | £180 failed its first full day: 29 May ran £204 for +1 click vs 28 May, CPC +28%, conv 6.8%→5.2%, ROAS 10x→6.7x — marginal ROAS negative. Imp share pinned 88–90% (captured pool, no demand to buy above ~£150). Demand thinning independent of budget (gross £2,972 26 May → £1,367 29 May), heat subsiding + school back. Landed £100 not £80 as 30 May Saturday opened strong — inside the proven 10–13x band. |
| 2026-05-28 ~23:00 | STANDARD £150 → £180 (tROAS 400%) — **reverted 30 May** | Thesis was expanding pool / firming marginal ROAS. Wrong: at 88–90% imp share the increment bought impressions not clicks. Don't push budget above ~£150 at this tROAS. |
| 2026-05-23 ~13:00 | STANDARD £120 → £150 (tROAS 400%) | Second step same day — heatwave still running, signals green, riding the wave. Held 26 May: 5-day weekly ROAS 12.9x, conv% recovered to 9.4%. |

> **Update this block whenever you change anything.** It is the single source of truth for "what's true today" and "what changed recently". Keep ~4 rows; git history holds anything older.

### custom_label_0 conventions

`skusummary.googlecampaign` populates `custom_label_0` in the merchant feed, scoping which styles a campaign targets.

| Label | Meaning |
|---|---|
| `BIRK-WINNER` | Manually-curated Birk winner styles, seeded 28 Apr 2026 (24 styles) |
| `NULL` | Everything else |

Maintenance is manual and ad-hoc — add/remove individual styles with one-off SQL when the curated set changes. No automated refresh.

### Adding a second campaign — read before acting (note added 1 Jun 2026)

> **DO NOT make any changes for this until you get explicit go-ahead that a second campaign has *actually* been created in Google Ads.** This is a forward note only. While the account is single-campaign, ignore it. Treating it as a to-do before the campaign exists will desync the doc from reality.

When a second campaign does go live, here's what was verified about the system (1 Jun 2026):

- **Ingestion code needs no change.** `update_google_stock_track.py` is already per-campaign aware. As long as the CSV export keeps the same columns (`Day, Campaign, Clicks, Impr., Currency code, Cost, Search impr. share`) and includes **all** campaigns, a new campaign just appears as new rows. `google_campaign_daily` upserts one row per `(date, campaign)` — the source of truth for per-campaign reads.
- **Do NOT combine impression share.** Summing/averaging imp share across campaigns is mathematically meaningless (different auction denominators). The code already handles this: `google_stock_track.google_search_imp_share` is written only when exactly one campaign reports that day, and goes **NULL** with 2+ campaigns *by design*. Read per-campaign imp share from `google_campaign_daily` instead. (The historical 28 Apr–13 May multi-campaign window is already frozen NULL there — same behaviour.)
- **Spend / clicks / impressions still sum fine** in `google_stock_track` — those aggregate correctly. Only imp share doesn't.
- **Process changes needed (in this doc) once it's live:**
  - Rewrite **Current State** from "single campaign" to describe both campaigns and which lever applies to which.
  - In the **Grid Snapshot / Diagnostic table**, read imp share **per-campaign from `google_campaign_daily`**, not `google_stock_track` (which will be NULL). Grids 1 & 2 (money/demand) still work on summed figures, but ROAS becomes *blended* across campaigns.
  - Add a new `custom_label_0` value for the new campaign and tag its styles via `skusummary.googlecampaign`.
- **The one genuine gap: per-campaign ROAS.** Sales aren't attributed by campaign today — `google_stock_track` ties total spend to total Shopify sales. With two campaigns on different style sets, blended ROAS hides which one performs. Attributing sales by `custom_label_0`/campaign would need new work. Only worth it if the second campaign targets a distinct style set you want to judge on its own.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` | Daily snapshot — ad spend, clicks, impressions, Shopify sales | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `google_campaign_daily` | **Per-(date, campaign)** clicks/impressions/cost/imp-share. Source of truth for any per-campaign read since 2026-05-04. | `SELECT * FROM google_campaign_daily WHERE snapshot_date >= CURRENT_DATE - 7 ORDER BY snapshot_date DESC, campaign;` |
| `adcost_summary_30.csv` | Raw Google Ads export (per-campaign, 30-day daily). Save to Downloads — script auto-moves and processes. | Export from Google Ads UI: Day, Campaign, Clicks, Impr., Cost, Search impr. share. |

**Imp share source:** single-campaign imp share reads from `google_stock_track.google_search_imp_share`; the multi-campaign window 28 Apr – 13 May is NULL there — use `google_campaign_daily`.

### Data gotchas — read before trusting a number

- **Sales-date offset:** `sales.solddate` is a DATE but renders as `23:00 UTC previous day` under BST (`2026-05-18T23:00:00Z` **is 19 May**). Always `solddate::text` for daily figures; treat the latest date as partial (today, still filling). Misread twice on 19 May.
- **Snapshot sales lag:** `google_stock_track.shopify_sales` is captured at script-run time and undercounts late orders. For trends, join `google_stock_track` to `sales` on `solddate` instead.
- **Capture-before-act:** when the cap changes in the UI, add the Recent-changes row the same day even if reasoning is filled in later. (The £54→£60 ghost change came from skipping this.)
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
| 5x–7x | — | — | — | Hold; run the grids to find the drag |
| **<5x** for 2 weeks | — | — | — | Decrease budget OR raise tROAS |

### Sizing & rules

- **Budget:** default ~20% step when criteria met, round to £1. Smaller (£2–4) when the algorithm is on a good trajectory. Hold/slow if ROAS <7x or instability after an increase. No fixed schedule — read signals, not dates.
- **tROAS (currently 400%):** *Lower* (→300%) when imp share <85% AND spend below cap (volume play). *Raise* (→500%) when imp share 85%+ AND marginal ROAS <5x, or 7d ROAS sliding on a ramp (efficiency play). One lever at a time; give it 5–7 days to re-learn. Don't move it just because you can.

### Stock availability (Birk core sizes) — a consideration, not a gate

`birk-stock/availability.py` gives one number: depth-weighted coverage of the women's core sizes (38/39/40) across every Birk style that should carry them (target 100%; today ~33%). It is a **confidence modifier on how hard to push**, never the go/no-go. The go/no-go stays imp share + ROAS.

- **A low number and high ROAS are not a contradiction.** The headline measures *range completeness*, not whether the traffic we buy can be fulfilled. tROAS already steers spend to the in-stock, converting styles; the empty stragglers drag the % but draw almost no spend. So 33% coverage at 11x ROAS → keep pushing; see how far imp share + ROAS let us go.
- **Rising coverage → more headroom** — add budget *if* imp share is short and ROAS healthy. The gauge only moves on core-size (38/39/40) arrivals, so a lift is a real lift (shoulder dumps don't fake it). **Caveat:** pruning dead styles also raises the number without adding demand — use the Full/Partial/Empty split to tell a *restock*-lift (new demand to buy) from a *prune*-lift (just honesty). Only the restock kind justifies more budget.
- **Falling coverage → push efficiency, not volume.** As the core drains toward the next 6-month delivery, lean on tROAS (the quality throttle) over budget, and treat each step more cautiously — we're buying into thinning fulfillment.
- **It also drives pruning.** Empty styles with no demand are drop candidates (`availability.py --detail` lists weakest-first); culling them is the owner's job over the 6-month wait and honestly lifts the number.

---

## Grid Snapshot

Quick trend read across the last 3 weeks (three rolling 7-day windows). Run in order: **Money** → if ROAS dropping, **Demand**.

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

Output: `Date range | Clicks | Units | Conv % | Cost/click`. Clicks rising + conv % falling = conversion problem. CPC rising sharply = click-cost problem → likely raise tROAS.

---

## Key Metrics

| Metric | Floor | Target | Source |
|--------|:-----:|:------:|--------|
| 7d ROAS | 5x | 7x+ | `google_stock_track` (or `sales` join) |
| Marginal ROAS (incremental new spend) | 5x | 8x+ | week-on-week delta |
| Search impression share | — | 85%+ | `google_campaign_daily` / `google_stock_track` |
| Daily spend vs cap | — | 80%+ of cap | `google_campaign_daily` |

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

1. Run the **Grid Snapshot** for the trend.
2. Read the **three constraint numbers** (imp share, spend vs cap, marginal ROAS).
3. Cross-reference the **Diagnostic table** — which lever is the constraint?
4. Recommend lever, direction, size, with reasoning. Name the campaign.
5. If changing: update **Current State** AND add a one-line row to **Recent changes**. That block is the only record — nothing is logged elsewhere.
