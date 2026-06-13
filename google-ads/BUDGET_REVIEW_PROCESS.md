# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

The whole process is three reads — **sales, cost, budget** — plus a record of recent changes. Everything below serves that. Keep it lean; if a section stops earning its place, cut it.

## Current State — updated 12 June 2026

- **Structure (single campaign since 14 May):** STANDARD Shopping, full catalogue incl. the 24 BIRK-WINNER styles. PMAX paused 14 May. IVES paused 9 May for the Amazon fair-pricing test; fold IVES SKUs back into STANDARD when that test ends, don't relaunch the standalone.
- **Active cap: £180/day (a ceiling, deliberately non-binding), STANDARD only** (set for 11 Jun). tROAS **600%** — raised from 500% on 10 Jun (third tROAS move: 400→500 on 8 Jun, 500→600 on 10 Jun). **Both held unchanged on 12 Jun** after 11 Jun (first day on this posture) resolved the bet cleanly — see the resolution + stick below.
- **Last change — 10 Jun, paired move set for 11 Jun: budget £120 → £180 (ceiling, not a target) + tROAS 500% → 600%, user-set.** Strategic flip from budget-target to **revenue-target** thinking. Trigger: the 10 Jun first day at £120/500% read ~**£126 spend / £1,006 rev / ~8.0x** — full cap spent (mild 5% smooth) but the *worst* ROAS of any £120-band day on record (norm 9–11x), and the marginal £17 over 9 Jun's £109 returned nothing. Two tROAS tests (400→500, then this) showed tROAS did **nothing** at £120 — because **budget binds first there, so the floor sits slack**. The reframe: £2k days are demand-*caught*, not budget-*bought* (every £1.9–2.6k day in the last 3 weeks came at £117–160 spend / 11–17x; the one £256 push got *less* rev at 7x). So budget's only job is **headroom to catch a big-pool day**, and tROAS's job is to **govern the normal days** so the loose ceiling doesn't bleed on junk. £180 = headroom to ride a big day to ~£2k; 600 = first real test of whether tROAS refuses junk *now that budget is loose* (6x floor cuts the ~5x marginal tail that tanked £140/£256). **Read each side separately:** budget = did we catch a big day; tROAS = did the normal days stay clean (~£120 at 10x) or bleed to £180 at <7x.
- **11 Jun resolved the bet (first day at £180/600):** £104 spend / £1,702 sales / **16.4x**, on an ordinary ~9k-impression pool. The £180 ceiling did **not** bind — the 600 floor held spend at £104 and refused the run-up — and it held at 16x with no junk tail. **This is the floor governing exactly as designed** (the predicted "£90–120 at ~10x", beaten on ROAS). No big-pool day landed, so the headroom-catch (ride a 14–18k day toward ~£2k) is still **untested** — a demand verdict on the day, not a strategy miss; the clean normal day cost nothing. 12 Jun read soft-but-clean on the partial (~£72 spend / £558 by 22:30 / ~7.75x), spend held low again.
- **Bias now (point-in-time):** hold 600 + £180. The 16x day is evidence the posture **works**, not that it's choking us. **Read spend as a pair with revenue, never as a level** — this is the stick: low spend + revenue holding = *efficiency* (the win under the revenue-target frame, be pleased); low spend + revenue *also* sliding = *throttle* (the only version worth acting on). Only spend **and** revenue dropping *together* over consecutive days warrants easing tROAS one rung to 550 (never skip to 500); a single low-spend day after a 16x day is not throttle. A merely-low spend total on its own is not a signal — the £180 is headroom, not a target to fill. Falling Full (45→38 this week) independently argues against adding volume. Re-read when the signal says, not on a clock.
- **Kill-trigger for the £120 test (decided in advance):** the only pattern that loses money fast is the 3-Jun signature — **over-cap front-load + conversions collapsing together** (spend racing past cap by mid-afternoon *and* CVR roughly halving toward ~4%). If both show by the user's mid-afternoon check, **cut the cap back to £100 the same day** — don't ride it to close. A merely *lower* ROAS (7–8x) with sensible pacing is **not** a kill — that's a normal result, read it in the morning.
- **Open flags:**
  - **tROAS now 600% (400→500 on 8 Jun, 500→600 on 10 Jun).** Key learning from the first two settings: **tROAS is slack while budget binds** — at £100–120 the budget cap is the constraint, so 400 vs 500 made no visible ROAS difference. tROAS only becomes the active lever at a *loose* budget (the £180 ceiling), where the floor decides how far Google reaches into the junk tail. 600% sets a 6x floor — above the ~5x marginal junk that tanked £140/£256, still below realized 8–10x blended, so it should cut the tail without choking winners. The £180/600 run is the first clean test of this.
  - **`troas` column now tracked (fixed 10 Jun).** Was a hardcoded `CURRENT_TROAS=400` never bumped — 8/9 Jun rows (true 500) were stamped 400; corrected to 500, and the constant is now 600. It's a *manual* field: bump line 42 of `update_google_stock_track.py` the same day you change tROAS in the UI (same discipline as the budget capture-before-act rule), or the per-day record drifts.
  - **tROAS controls quality, budget controls quantity — don't conflate them.** Spend going *over* the daily cap is Google smoothing (allowed up to ~2× the daily cap as long as the monthly average holds); it is **not** evidence the tROAS gate is weak. Counter-intuitively, a *stronger* tROAS holds spend *down* (it refuses sub-floor auctions); a *weak* one lets spend run on junk. So an over-cap day at high ROAS = gate working; over-cap at low ROAS = gate too weak (→ raise tROAS, don't cut budget); under-cap = gate throttling. Always judge the gate on **marginal ROAS, never on the spend total.**
  - **Conversion baseline:** Mar 12.1% → Apr 8.7% → May 7.4% median (June MTD 7.5%; recovered to ~9% in the 19–25 May window). Watch through the tROAS re-learn.

### Recent changes (replaces the old change log — keep last ~4, one line each)

| Date | Move | Why |
|------|------|-----|
| 2026-06-10 | STANDARD £120 → £180 (ceiling) **+ tROAS 500% → 600%** — **paired move, revenue-target flip, user-set** | 10 Jun first day at £120/500 read ~£126/£1,006/**~8x** — full cap but worst £120-band ROAS on record; marginal over 9 Jun's £109 returned nothing. Two tROAS tests (400→500, 500→600) confirmed tROAS is **slack while budget binds** at £120. Flipped to revenue-target: £2k days are demand-*caught* at £117–160 spend (not budget-bought — the £256 push got *less*), so budget = **headroom to catch a big-pool day**, tROAS = **governor** of normal days. £180 ceiling (non-binding) to ride a big day to ~£2k; 600 (6x floor) to refuse the ~5x junk now budget is loose. Judge on revenue caught + normal-day cleanliness, not spend. Don't react to day 1 (re-learn). Also fixed the stale `troas` column (was hardcoded 400; 8/9 Jun corrected to 500, constant now 600). |
| 2026-06-09 | STANDARD £100 → £120 (tROAS held 500%) — **light step into peak, user-set** | First day at £100/500% (9 Jun) resolved the bet: £1,062/£108 (~9.8x), **full cap spent at 10x, no junk** — cleanest "ran out of road" signal yet. Both guesses won (spend = user, revenue = Claude). Stepped to £120 — deliberately light, not the £150 a pure gate-test wants, because user isn't yet sold that 500% holds quality at a big jump. £120 cheaply re-asks "is there road above £108?"; £150 gate-test held for a later rung. Hold tROAS (mid-re-learn). Kill on the 3-Jun signature; judge marginal ROAS not the spend total. Caveat: a £143/3-item order on 9 Jun may be a try-and-return — nets 9 Jun toward ~£900/8.5x if it comes back. |
| 2026-06-08 | STANDARD £220 → £100 **+ tROAS 400% → 500%** — **paired reset, user-set** | 7 Jun £220 push spent £256 for £1,829 (7.1x blended, ~5.0x marginal) — diluted, didn't crater (CVR 7.3%→5.8%). Used the forced re-learn to make two changes at once: budget back to the proven £100 band (not £80 — avoids under-spend), and the **first tROAS move since Feb** (→500%) to gate quality before any future climb. Judge over 5–7 days (tROAS re-learn), not 24–48h. If 500% over-throttles, ease to 450%; if it holds 10x+ at £100, resume the steady £10 ladder under its protection. |
| 2026-06-04 | STANDARD £100 → £110 (tROAS 400%) — **cautious volume test** | £100 revert held; 4 Jun fully spent £100 for ~£1,948 SHP (~19x), first sign June demand may have firmed back toward late-May (25–27 May carried £150 at 11–19x). £10 step only — not a £140-style leap — to probe convertible headroom above £100. Judge on marginal ROAS in 24–48h, not imp share. Kill on the 3-Jun signature (over-cap front-load + conversions collapsing). |

> **Update this block whenever you change anything.** It is the single source of truth for "what's true today" and "what changed recently". Keep ~4 rows; git history holds anything older.

### custom_label_0 conventions

`skusummary.googlecampaign` populates `custom_label_0` in the merchant feed, scoping which styles a campaign targets.

| Label | Meaning |
|---|---|
| `BIRK-WINNER` | Manually-curated Birk winner styles, seeded 28 Apr 2026 (24 styles) |
| `NULL` | Everything else |

Maintenance is manual and ad-hoc — add/remove individual styles with one-off SQL when the curated set changes. No automated refresh.

> **Multiple campaigns later:** imp share is **not** summable across campaigns (different auction denominators) — read it per-campaign from `google_campaign_daily`, never `google_stock_track` (which goes NULL with 2+ campaigns by design). The rest of the setup you can work out from the ingestion code when the day comes.

---

## Data Sources

| Source | What it tells us | How to check |
|--------|-----------------|--------------|
| `google_stock_track` | Daily snapshot — ad spend, clicks, impressions, Shopify sales | `SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 14;` |
| `google_campaign_daily` | **Per-(date, campaign)** clicks/impressions/cost/imp-share, plus `lost_is_rank` / `lost_is_budget` (added 6 Jun 2026). Source of truth for any per-campaign read since 2026-05-04. | `SELECT * FROM google_campaign_daily WHERE snapshot_date >= CURRENT_DATE - 7 ORDER BY snapshot_date DESC, campaign;` |
| `adcost_summary_30.csv` | Raw Google Ads export (per-campaign, 30-day daily). Save to Downloads — script auto-moves and processes. | Export columns, in order: Day, Campaign, Clicks, Impr., Cost, Search impr. share, **Search lost IS (rank)**, **Search lost IS (budget)**. The two lost columns **must be appended at the end** — the parser validates/reads the first 7 by position and ignores trailing columns, so inserting them mid-list silently corrupts the read. The two lost columns are optional (older 7-col exports still parse). |

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
- **tROAS (currently 500%, raised from 400% on 8 Jun):** *Lower* when imp share <85% AND spend below cap (volume play). *Raise* when imp share 85%+ AND marginal ROAS <5x, or 7d ROAS sliding on a ramp (efficiency play). Move ≤25% at a time; one lever at a time; give it 5–7 days to re-learn. Don't move it just because you can.

### Lost impression share — rank vs budget (the tripwire)

`google_campaign_daily.lost_is_rank` / `lost_is_budget` split the impression share we *didn't* get. They answer the question imp share alone can't: are we missing demand because we **capped out** (budget) or because a competitor **outranked** us (rank/price)?

**Baseline established 6 Jun 2026 (May–early Jun STANDARD):** lost-to-rank is **~0% every normal day** (0.00–0.12%; only ever twitched to 1.18%, on the 29 May £204 blowout). **Essentially all** lost share is **budget**. Reads:

- **We are not in a rank/price war.** When STANDARD is in an auction it wins it. So missed demand is *not* a pricing problem and *not* bid-conservatism — which removes the case for touching tROAS to "bid harder" (there's no rank loss to recover).
- **`lost_is_budget` is available impressions, NOT available profit.** It is the exact metric that suckered the £140 raise. The ~10% budget-available headroom on normal days was field-tested: filling it (£140→3.4x, £204→6.7x at 96% imp share) converts **below the 5x floor**. Don't read a budget-lost % as money on the table — the marginal impression there is browse traffic.
- **`lost_is_budget` spikes on THIN days** (30 May 48%, 17–18 May 31%) because the *eligible pool shrank*, not because a goldmine opened. It co-moves inversely with imp share; on its own it's near-redundant with the imp share we already track.

**The tripwire is `lost_is_rank`, and its whole value is staying near zero.** If STANDARD `lost_is_rank` climbs (>~5% for 2+ days), a competitor has entered or our price has slipped — a *different* problem from a budget cap, and the lever is price/competitiveness, not budget. This is a background weekly glance, not a daily budget input. Quick check:

```sql
SELECT snapshot_date, search_imp_share, lost_is_rank, lost_is_budget
FROM google_campaign_daily
WHERE campaign = 'STANDARD' AND snapshot_date >= CURRENT_DATE - 14
ORDER BY snapshot_date DESC;
```

> **Why the ceiling floats (tied to this):** the budget level demand can fund tracks the *eligible-pool size*, not a fixed number. Normal early-Jun days run ~9–11k impressions → ceiling ~£110–130. Peak late-May days ran 14–18k → funded £150–165 at 10–17x. £180 is a **hot-day catch when the pool is big**, not a standing target to climb to. Keep budget uncapped enough to ride a big-pool day; don't set a high standing cap that buys the 3.4x tail on normal days.

### Stock availability (Birk core sizes) — a consideration, not a gate

`birk-stock/availability.py` gives one number: **Full** = Birk styles holding all three women's core sizes (38/39/40) in stock, out of every style whose grid offers those sizes. Run it for the live count. Full is the breadth of core-complete product ad spend can ride. It is a **confidence modifier on how hard to push**, never the go/no-go. The go/no-go stays imp share + ROAS.

- **A low Full and high ROAS are not a contradiction.** Full measures *range breadth*, not whether the traffic we buy can be fulfilled. tROAS already steers spend to the in-stock, converting styles; the not-Full stragglers don't draw spend. So a low Full at 11x ROAS → keep pushing; see how far imp share + ROAS let us go.
- **Why Full, not a coverage %.** A % hides scale and is contaminated by how many losers sit unpruned in the range. Full is absolute — it moves only when real sellable breadth moves. Read Full as the level; `Full %` (Full ÷ Styles) is just the trend.
- **Rising Full → more headroom** — add budget *if* imp share is short and ROAS healthy. Full only rises when a style gains its *last missing* core size, so a lift is real breadth (shoulder dumps don't fake it). One subtlety: Full also rises if a dead style is pruned out of the range — that's honest, but it's not new demand to buy, so don't read a prune-driven lift as room for more budget.
- **Falling Full → push efficiency, not volume.** As the core drains toward the next 6-month delivery, lean on tROAS (the quality throttle) over budget, and treat each step more cautiously — we're buying into thinning fulfillment.
- **It also drives pruning.** Not-Full styles with no demand are drop candidates (`availability.py --detail` lists them weakest-first); culling them is the owner's job over the 6-month wait.

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
