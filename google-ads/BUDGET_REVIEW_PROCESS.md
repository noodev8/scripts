# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

## Current State — updated 19 May 2026

- **Campaign structure (single campaign since 2026-05-14):**
  - **Standard Shopping** — core campaign, full catalogue including the BIRK-WINNER styles. **£100/day** (raised from £72 on 19 May 2026 — see change log).
  - **PMAX (BIRK-WINNER)** — **paused 14 May** after a 16-day test (28 Apr – 13 May). Google attributed 7.28x ROAS to PMAX (matched STANDARD), but cannibalization test (BIRK-WINNER styles +42% units post-launch vs OTHER Birks +30%) implied most PMAX revenue was duplicated from STANDARD. Operational simplicity outweighed the marginal incremental ROAS. The 24 BIRK-WINNER SKUs still carry the `custom_label_0 = BIRK-WINNER` label — STANDARD's Smart Bidding can use it as a signal without a separate campaign. Reactivate PMAX only for a specific reason (e.g. new product launch needing Display/YouTube reach for awareness).
  - **IVES Shopping** — **paused 9 May** for Amazon fair-pricing test. Independent finding (14 May): IVES ran at 3.27x ROAS over 30 days — below the 5x profit floor. When the AMZ test concludes, fold IVES SKUs back into STANDARD's catalogue rather than relaunching the standalone campaign.
  - **Active daily cap: £100 (STANDARD only)**
- **tROAS:** 400% on STANDARD. Held there since Feb. See decision flow for when to move it.
- **Last review:** 19 May 2026 — Planned diagnostic on STANDARD-only at £72. **Raised STANDARD £72 → £100 (+39%); tROAS held at 400%.** Key finding: the 14 May revert reasoned off a PMAX-inflated imp share — STANDARD's 86–93% during May 8–13 was measured on a *narrowed* auction pool (PMAX had carved out the 24 BIRK-WINNER styles). STANDARD-alone's true broad-catalogue imp share is ~78% (Apr 14–27 clean history ~77%; post-consolidation readings agree), which is the "<85%, budget-constrained" diagnostic row, not "hold". With 7d ROAS ~12x, Google overspending the £72 cap every post-consolidation day (£75–79), and stock stable/non-binding (~1,740 live, ~1,100 READY, flat since 14 May), all increase criteria are met. £100 is the defensible ceiling: imp-share capture math (~£97 for ~full IS), demonstrated combined-catalogue absorption (split era £117–123/d at 9.9x), and a blended-ROAS cushion that stays >9x even if incremental spend returns only 4x. +39% is justified as a consolidation re-absorbing demonstrated combined spend through one engine (cf. 14 May consolidation logic), not a ramp into the unknown; expected sunny-weekend demand is the cover for the learning-phase risk. tROAS 500% remains the next lever if Google under-fills £100.
- **Next planned step:** ~Mon 26 May — review STANDARD-only at £100 after 5–7 days of Smart Bidding learning (first full day 20 May). Watch: (1) **does Google fill the £100 cap?** Overspends/pins it → more headroom; under-fills → £100 is near the ceiling and the next lever is **tROAS, not budget**. (2) STANDARD imp share — expect it to climb from ~78% toward 85%+ as the larger cap captures missed auctions; stuck at ~78% with the cap under-filled = the tROAS-lower signal. (3) Marginal ROAS week-on-week vs the STANDARD-only £76/£903-day baseline — blended should hold >9x; if £100 drags blended toward 7x, pull back. (4) Conversion % as clicks scale (soft ~7–8% vs Mar 12% — see flag). Do not compound another budget change before this review unless ROAS breaks the 5x floor.
- **Open flags:**
  - **May drift signal — reframed 19 May:** The original flag read £72 as "the last cleanly-absorbed STANDARD level" off an 86–93% imp share. 19 May analysis showed that figure was **PMAX-pool-inflated** — STANDARD's auction base was narrowed while PMAX ran the 24 BIRK-WINNER styles, so the high IS was measured on a smaller pool. STANDARD-alone's genuine broad-catalogue imp share is ~78%, so £72 was budget-constrained, not cleanly absorbed. Acted on: raised to £100 on 19 May. Diminishing-returns curve still real (Apr 14–30 £57/d 14.4x → May 1–8 £89/d 11.8x → May 9–13 £123/d 9.9x) — track marginal ROAS at £100 per the next-review watch-list; flag closes if blended holds >9x.
  - **Conversion baseline drifting down:** Mar 12.1% → Apr 8.7% → May 7.1% (13 days). Real, not noise. Plausible cause: CRAP-retirement (commit `33121ae`, ~10 May) added 161 NULL/CRAP groupids into segments and into STANDARD's feed, diluting impression quality while Smart Bidding learns to deprioritise the weaker stuff. **19 May read:** 7-day-window conv 8.1% (Apr 28–May 4) → 6.9% (May 5–11) → 7.6% (May 12–18) — stabilising ~7–8%, well below Mar but not in free-fall. Watch as the £100 cap scales click volume.
  - **THIN-selling style count at record high:** ~32 styles selling with poor stock (19 May). **ZERMATT-SEG** worst offender (6 of 12 styles THIN-selling, 9 of 12 THIN overall). Burns clicks on near-empty pages. Flag for the next 6-month Birk buy — can't fix with budget; Smart Bidding deprioritises but doesn't eliminate the waste.
- **Per-campaign data captured (added 2026-05-04):** `google_campaign_daily` table stores per-(date, campaign) clicks/impressions/cost/search_imp_share. Populated nightly from `adcost_summary_30.csv`. Post-consolidation only STANDARD has active rows; PMAX/IVES historical rows remain for reference.
- **Snapshot-sales-lag caveat:** `google_stock_track.shopify_sales` captures the day's sales at script-run time and can lag actual end-of-day total when late orders file after the snapshot. For trend reads, prefer joining `google_stock_track` to `sales` on `solddate` rather than using `shopify_sales` directly. (Discovered 30 Apr — Apr 29 stored £544 vs actual £920.)
- **Sales-date rendering caveat:** `sales.solddate` is a DATE, but the SQL client renders it as a timestamp at `23:00 UTC of the previous day` under BST (e.g. `2026-05-18T23:00:00.000Z` **is 19 May**). Grouping or labelling by the raw rendered value shifts every day back by one and silently turns the incomplete current day into a fake "low day". **Always `solddate::text` in the SELECT for daily figures, and treat the latest date as partial (today, still filling).** Misread twice on 19 May 2026 — an £884 full day shown as a £395 "Monday low" that was actually the in-progress current day.
- **Capture-before-act rule:** when the budget is changed in the UI, add a line to the change log the same day, even if rationale is filled in later. The £54→£60 ghost change happened because this didn't.

> **Update this block whenever you change anything below — including the change log.** Single source of truth for "what's true today".

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

**Birk ad-readiness columns in `google_stock_track`** (populated nightly):
- `birk_ready_styles` — count of READY styles (≥70% size coverage AND ≥15 units). The convertible-catalogue headline.
- `birk_ready_units` — total stock units across READY styles. Depth check.
- `birk_thin_selling_styles` — count of THIN styles that sold ≥1 in last 30d. The waste signal.

**Imp share source after consolidation:** under single-campaign mode (from 14 May), `google_stock_track.google_search_imp_share` is the headline read again. Multi-campaign dates 28 Apr – 13 May are frozen NULL there — use `google_campaign_daily` for that window.

**`localstock` is source of truth for Birkenstock stock.** Birkenstock is Shopify-only (not on Amazon), so no need to check `amzfeed`.

**Do not trend the change-log "Stock (units)" column.** Those are ad-hoc one-off snapshots typed at review time, computed inconsistently between entries (some total-live, some READY-only, some carried over from a prior entry). The 14 May "3,288 live units" cannot be reconciled with 19 May's ~1,740 by sales (~15 Birk units/day → ~75 units over 5 days, not 1,500) — it was a bad/blended figure, never a real drop. Rules:
- **Trend reads:** use the nightly-populated `google_stock_track.birk_ready_units` / `birk_ready_styles` (1,093 on 14 May → 1,107 on 18 May = stable — the reality the "3,288" obscured).
- **Current total (one-off):** the only consistent definition is `SELECT SUM(qty) FROM localstock WHERE deleted = 0 AND brand = 'Birkenstock'` (≈1,740 on 19 May). The `#FREE`/skusummary-join variants agree to within ~10 units.
- **Sanity rule:** before treating any stock delta as real, divide it by burn rate. If ~15 units/day can't explain it, the *number* is suspect, not the stock — verify before building a recommendation on it.

---

## The Decision Flow

Two levers move the campaign: **daily budget** (how much Google can spend) and **tROAS** (how aggressively it bids). Pick the lever first, then size the move. Historical bias to push against: every change-log entry since Feb says *"tROAS held at 400%"* — the budget lever has been doing all the work, often where tROAS was the right tool.

### Read the constraint first

Three numbers tell you which lever is the constraint:

1. **Search impression share** — capturing demand, or missing it?
2. **Spend vs cap** — is Google trying to spend more than allowed?
3. **Marginal ROAS** — is the last bit of spend still returning above the 5x floor?

### Diagnostic table

| 7d ROAS | Imp share | Spend vs cap | Marginal ROAS | Constraint | Action |
|---------|-----------|--------------|---------------|------------|--------|
| ≥7x | **<85%** | At cap | ≥5x | **Budget** | Raise budget (~20% step) |
| ≥7x | **<85%** | **Below cap** | — | **tROAS** | **Lower tROAS** — Google can't find auctions at current bar |
| ≥7x | **85%+** | At cap | ≥5x | Neither | Hold — capturing demand cleanly |
| ≥7x | **85%+** | At cap | **<5x** | **tROAS** | **Raise tROAS** — ramp drift; force Google pickier |
| 5x–7x | — | — | — | Watch | Hold, run the Three-Grid to find what's dragging |
| **<5x** for 2 weeks | — | — | — | — | Decrease budget OR raise tROAS |

**The fourth row is the recovery move we missed in early May.** When STANDARD's imp share was 90–93% and we still pushed budget from £72 toward £105, the doc had no clear rule for "ramp drift while imp share is already maxed." That row is it.

### Budget — increment sizing

- Default **~20% step** when criteria are met. Round to nearest £1.
- **Smaller steps** (£2–4) when the algorithm is on a good trajectory — don't disrupt learning.
- **No fixed schedule.** A 20%-every-5-days *cadence* used to live in this doc; it was deleted in May 2026 because it encouraged chasing dates rather than reading signals.
- **Hold or slow** if ROAS drops below 7x, stock thins, or algorithm shows instability after an increase.

### tROAS — when to move it

Currently **400%**. Adjust when the diagnostic table points to tROAS:

- **Lower tROAS** (400→300%): imp share <85% AND spend below cap. Tells Google to bid in more auctions at lower efficiency. Volume play.
- **Raise tROAS** (400→500%): imp share 85%+ AND marginal ROAS <5x, OR 7d ROAS sliding on a ramp. Forces Google pickier inside its current auction pool. Efficiency play.
- **One lever at a time.** Give a tROAS change 5–7 days before judging — algorithm re-learns.
- Don't change tROAS just because you can. If the algorithm is outperforming the target and budget is the clear constraint, leave it alone.

### Stock is a fixed constraint, not a lever

Birkenstock orders are placed ~6 months in advance. Stock cannot be reactively pulled to fix ad leaks. If high-volume segments are PARTIAL/THIN, **trim ad budget to where it stays efficient** rather than waiting for restock. Surface the leak for the next 6-month buy, but adjust budget around current stock reality.

**Do not recommend "order more X" as an action.**

---

## Three-Grid Snapshot

Quick trend read across the last 3 weeks. Three rolling 7-day windows; together they answer "what changed."

### Order matters

1. **Money** — is ROAS healthy and how is it trending?
2. **If ROAS dropping → Demand** — click cost or conversion?
3. **If conversion dropping → Stock** — can the catalogue convert what's arriving?

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

Output: `Date range | Sales | Spend | ROAS`. Healthy ROAS ≥7x. Falling ROAS isn't bad on its own — it's the trigger to look at Grid 2.

**For more accurate sales:** join `google_stock_track` to the `sales` table on `solddate` instead of using `shopify_sales` directly (snapshot lag caveat above).

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

Output: `Date range | Clicks | Units | Conv % | Cost/click`. Clicks rising and conv % falling = conversion problem → Grid 3. CPC rising sharply = click-cost problem → likely raise tROAS to tighten.

### Grid 3 — Stock

Per-segment readiness today. **Do not use `skusummary.variants` or `skusummary.stockvariants`** — both stale (see CLAUDE.md). Size universe comes from `skumap`; live stock from `localstock`.

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

Output: `Segment | Styles | READY | PARTIAL | THIN | THIN-selling | Sold 30d`. PARTIAL on a high-volume segment = clicks landing on broken size grids. THIN-selling = clicks burned on near-empty pages.

For per-style detail (which sizes missing), drop the segment grouping and select `groupid, colour, sizes_in_stock, total_sizes` from the `readiness` CTE.

### Reading the three together

| Money | Demand | Stock | Read |
|---|---|---|---|
| ROAS healthy, imp share <85% | — | — | **Raise budget** |
| ROAS healthy, imp share 85%+ | Marginal ROAS <5x | — | **Raise tROAS** |
| ROAS dropping | CPC stable, conv falling | High-volume segments PARTIAL/THIN | Hold — fix stock first |
| ROAS dropping | CPC rising | — | Click-cost issue — **raise tROAS** |
| ROAS dropping | Conv stable, clicks falling | — | Demand softening — seasonal or competitive |
| ROAS approaching 5x | — | — | Pull back |

---

## Key Metrics

| Metric | Floor | Target | Ceiling | Source |
|--------|:-----:|:------:|:-------:|--------|
| 7d ROAS | 5x (minimum profitable) | 7x+ | — | `google_stock_track` (or `sales` join) |
| Marginal ROAS (incremental new-spend) | 5x | 8x+ | — | week-on-week delta from change log |
| Search impression share | — | 85%+ | — | `google_campaign_daily` / `google_stock_track` |
| Daily spend vs cap | — | 80%+ of cap | Consistently at cap | `google_campaign_daily` |
| Ad-ready styles (READY count) | 10+ | 15+ | — | Grid 3 |
| THIN styles actively selling | 0 ideal | Flag for stock review | — | Grid 3 (sold_30d > 0 but THIN) |

---

## Baseline conversion rate (monthly health check)

Daily conversion is noisy at our volume (~76 clicks/day). Don't react to individual days. Track the **monthly median** — half your days above, half below, immune to single-day spikes/crashes.

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

**How to read:** median rising month-over-month = fundamentals improving (supports budget moves); median dropping = something structural changed, investigate before raising budget. The IQR (Q1–Q3) is the band where normal days land.

**Mar 2026 reference:** median 12.3%, IQR 9.8–16.3%. Expect ~3 bad days, ~3 great days, ~20 baseline days per month at current volume.

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

## Process for Claude Code Review

When asked to review the Google Ads budget:

**Don't run analysis on stale data.** If the latest `snapshot_date` with ad spend is >2 days old, flag it and wait for user confirmation before proceeding.

1. Run the **Three-Grid Snapshot** for the trend read.
2. Read the **three constraint numbers** (imp share, spend vs cap, marginal ROAS) for current state.
3. Run **Grid 3 readiness** if conversion is dragging.
4. Cross-reference against the **diagnostic table** — which lever is the constraint?
5. Recommend: which lever, which direction, what size — with reasoning. Name the campaign.
6. If changing: update **Current State** at the top AND add a row to the **Change Log** below. Single source of truth lives here — do **not** log budget changes in `scale/SCALE_PLAN.md` or elsewhere.

---

## Budget & tROAS Change Log

Recent entries keep full rationale. Older entries collapsed to one-liners for scan speed — full rationale lives in git history.

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
| 2026-05-15 (decided 14 May, midnight-effective) | **Consolidated back to single STANDARD campaign.** PMAX paused, IVES kept paused. STANDARD £72 → £105 (+46%). Active cap £105 (single). | 10.2x (last 7d, sales-table joined) | STANDARD 90–93% (last 4 reported days); PMAX 62% avg | £119 combined avg 7d (STD £74 + PMAX £39 + IVES £0 paused) | 3,288 live units; 41 READY (1,124u), 30 THIN-selling (record high) | Triggered by Google Conversions-by-Campaign report (14 Apr – 13 May): PMAX £442 → £3,223 conv value → 7.28x ROAS, matched STANDARD's 7.28x. Cannibalization test (BIRK-WINNER +42% units post-launch vs OTHER Birks +30%, but −6.6pp revenue growth) implied most PMAX revenue was duplicated from STANDARD's eligible auctions. True incremental PMAX ROAS estimated 2–4x — well below Google's attributed 7.28x. IVES separately revealed 3.27x ROAS over 30 days (below floor) — confirms pausing was correct independent of the AMZ test. STANDARD-only at £105 absorbs roughly the freed PMAX budget while testing whether STANDARD's Smart Bidding can scale alone. +46% is large vs the 20% ramp shape, but total daily spend roughly unchanged from the £117 combined cap — it's a consolidation, not a true ramp step. PMAX's BIRK-WINNER `custom_label_0` retained as Smart Bidding signal inside STANDARD. tROAS held at 400%. Operational case: one ROAS, one imp share, one cap = clean ramp lever from here. | Mon 19 May |
| 2026-05-14 (evening, same-day revert) | **Reverted STANDARD £105 → £72.** PMAX kept paused, IVES kept paused. tROAS held at 400%. Active cap £72 (single). | 9.9x (May 9–13, sales-table read) | STANDARD 86–93% (May 1–10 reported days) | Recent STANDARD: £74/d May 9–13 | 3,288 live units; 41 READY, 30 THIN-selling | Reverted same day after diagnostic re-read against rewritten doc framework. The earlier £72→£105 step (logged just above) went against the doc's "Hold when imp share 85%+" rule — STANDARD was already at 86–93% imp share, which is the "capturing demand cleanly" row of the new diagnostic table, not "raise budget." Today's weak sales feel reinforced the gut check but the rules-based reason was sufficient on its own. Reverted *before* midnight so no full day was paced against £105 — Google never started learning a new cap, no churn cost. £72 is the last STANDARD level cleanly absorbed (May 9–13 STANDARD spent £74/d at 86–93% imp share). tROAS held at 400% as conservative single-lever revert; tROAS 400→500% available as the next experiment if marginal ROAS stays weak. Doc-rewrite note: this revert is the framework working as intended — the new diagnostic table surfaced a misread that the old multi-framework doc obscured. | Mon 19 May |
| 2026-05-19 (effective 19 May, user-set in UI) | **STANDARD £72 → £100 (+39%).** PMAX kept paused, IVES kept paused. tROAS held at 400%. Active cap £100 (single). | ~12x STANDARD-only (May 14–18, sales-joined); 11.3x trailing 7d incl. 2 split days | STANDARD ~78% true broad-catalogue level — the 86–93% logged pre-revert was **PMAX-pool-inflated** (narrowed auction base); post-consolidation 85.9 / 69.3 (May 15/16, others NULL) + Apr 14–27 clean history ~77% all agree ~78% | £76/d STANDARD-only (May 14–18); Google overspent the £72 cap every day (£75–79) | 1,740 live (canonical `localstock` SUM); 1,107 READY units / 39 styles — birk_ready stable 1,093→1,107 since 14 May (the "3,288" in the two entries above is a bad/blended figure, not a real level — see caveat) | Planned 19 May review. The 14 May revert had reasoned £72 was "cleanly absorbed" off an 86–93% imp share; 19 May analysis showed that was **PMAX-inflated** — STANDARD's auction pool was narrowed while PMAX carved out the 24 BIRK-WINNER styles, so the high IS sat on a smaller base. STANDARD-alone's true broad-catalogue IS is ~78% (Apr 14–27 clean history ~77%; post-consolidation readings agree) — the diagnostic table's "≥7x ROAS / <85% IS / at cap / marginal ≥5x → raise budget" row, not "hold". Spend-vs-cap corroborates independently: Google overspent £72 every post-consolidation day. Ceiling analysis put the defensible destination at ~£100: (a) imp-share capture math £76/0.78 ≈ £97 for ~full IS; (b) demonstrated combined-catalogue absorption — split era ran £117–123/d at 9.9x blended, STANDARD-alone hit £86.75 at 92% IS on 8 May; (c) blended-ROAS cushion stays >9x even if incremental spend returns only 4x; (d) stock non-binding (~1,740 live, ~1,100 READY, flat, 90+ days cover). Above ~£105 the lever flips to tROAS (Google under-fills). +39% exceeds the 20% comfort step but is justified as a **consolidation re-absorbing demonstrated combined spend through one engine** (same logic as the 14 May consolidation entry), not a ramp into the unknown; the expected sunny-weekend demand spike is the cover that makes the learning-phase risk acceptable. User-led aggressive step into peak season. Honest caveats: STANDARD-alone has never been tested above ~£87 solo — £100 is a well-justified experiment, not a proven-safe point; conversion soft ~7–8% vs Mar 12% — watch as clicks scale. Two data-hygiene fixes landed same session (change-log "Stock (units)" not trendable; `solddate` 23:00-UTC offset). | ~Mon 26 May (5–7 days learning at £100; first full day 20 May) |
