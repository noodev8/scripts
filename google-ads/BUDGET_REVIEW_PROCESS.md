# Google Ads Budget Review Process

**Created:** 2026-02-20. **Cadence:** as needed — no fixed schedule.

The whole process is three reads — **sales, cost, budget** — plus a record of recent changes. Everything below serves that. Keep it lean; if a section stops earning its place, cut it.

## Current State — updated 7 July 2026

- **Structure (single campaign since 14 May):** STANDARD Shopping, full catalogue incl. the 24 BIRK-WINNER styles. PMAX paused 14 May. IVES paused 9 May for the Amazon fair-pricing test; fold IVES SKUs back into STANDARD when that test ends, don't relaunch the standalone.
- **Active settings: £300/day cap (effective 8 Jul, set late 7 Jul) + tROAS 600% (effective 6 Jul).** Cap raised to pre-position hot-day headroom for an incoming heatwave weekend — costless downside (the 600 floor self-caps soft days, so the extra only spends when a day clears ~6x). Budget path: £180→£200 (21 Jun) → £220 (23 Jun) → £240 (24 Jun) → £260 (25 Jun) → £280 (6 Jul) → £300 (8 Jul). tROAS path: 400→500 (8 Jun) → 600 (10 Jun) → 550 (13 Jun) → 600 (17 Jun) → 650 (30 Jun) → 600 (6 Jul, reverted). Per-move detail is in Recent changes below.
- **Posture: harvesting the last-peak heatwave with both levers pushed up-volume.** The 650 experiment (30 Jun–5 Jul) is closed: matched £260-cap windows showed 650 *cut ~13% of volume for zero efficiency gain* — 600-era and 650-era both ran ~9.5x ROAS at identical 7.3% conversion, and the ~£42/day the 650 floor refused was converting at **~8x** (above target). So the raise turned away profitable volume without improving realised ROAS. Reverting to the proven 600 floor reclaims that 8x tranche; it refuses sub-6x soft-day junk and **doesn't cost the hot days** (11 Jun ran 600 → 15.2x; 20 Jun → 10.3x; 21 Jun → 11.6x). Budget stepped to £300 (7 Jul, effective 8 Jul; smoothing ceiling ~£600) to pre-position hot-day headroom for an incoming heatwave weekend. **The £280 cap was proven non-binding first:** 7 Jul was a genuine hot day (£2,773 sales, best in the window, ~12x ROAS) and it still spent only £232 — under cap — so budget is *not* the constraint even on rich demand; the 600 floor cleared the good auctions at £232 and there was no above-floor volume left to buy. The £300 is therefore harvest insurance, not a response to a bind — costless on soft days (the 600 floor gates it, so the extra cap only spends when auctions clear ~6x). Normal days self-spend £125–150 regardless. Both levers moved together *deliberately* (breaking the one-lever rule) as a decided harvest, not a diagnostic — accept muddier attribution for this window.
- **Bias now (point-in-time):** ride the heatwave hard while stock holds; this is the last month of peak. **Full is healthy at 54/149 (36%) on 5 Jul** — held in the 50–59 band since the 20 Jun delivery (absolute count strong; % flat only because the universe grew 132→149). Breadth is *not* the constraint. 7 Jul (first 600-floor hot day at £280) ran ~12x on £2,773 sales yet stayed under cap at £232 — so the constraint is pool depth / conversion, not budget. The £300 cap is pre-positioned for the incoming heatwave weekend; if a weekend day *pins* £300 at 10x+ with imp share slipping, that's the first real budget-bound signal — step again then. If it never pins (likely, on today's evidence), the £300 simply sat there costing nothing. **The lever for the Aug–Oct taper is tROAS going back *up*** (tighten as the pool thins toward the next 6-month delivery) — not now. **Kill pattern (any cap):** the 3-Jun signature — over-cap front-load *and* CVR halving toward ~4% by mid-afternoon → cut cap the same day. A merely lower ROAS (7–8x) with sane pacing is **not** a kill.
- **Durable learnings (don't re-derive):**
  - **tROAS is slack while budget binds.** At a tight cap the budget is the constraint and tROAS moves do nothing visible; tROAS only becomes the active lever at a *loose* cap (the £180 ceiling), where the floor decides how far Google reaches into the pool. Corollary: a *stronger* tROAS holds spend *down* (refuses sub-floor auctions), a weaker one lets it run on junk — so over-cap at high ROAS = gate working; over-cap at low ROAS = gate too weak (raise tROAS, don't cut budget); under-cap = gate throttling. Judge the gate on **marginal ROAS, never the spend total** (smoothing allows up to ~2× the daily cap).
  - **A tROAS move below ~50pts is unreadable.** Daily ROAS swings ~5–15x, so a 10–20pt floor shift (0.1–0.2x) can't be told from noise and still costs a re-learn. Move in 50pt rungs, one lever at a time.
  - **`troas` column is schedule-driven.** When you change tROAS in the UI, append one `(effective_date, value)` row to `TROAS_SCHEDULE` near the top of `update_google_stock_track.py` — do **not** edit historical rows. Each day is stamped with the floor that was live *on that date*, so late-backfilling days (imp share lags 2–3 days) get the right value. The old single-constant approach mis-stamped late backfills — it tagged 25–29 Jun as 650 when they ran at 600 (found & fixed 5 Jul 2026; earlier 8/9 Jun drift was the same bug).
  - **Conversion baseline:** Mar 12.1% → Apr 8.7% → May 7.4% median (June MTD 7.5%; ~9% in the 19–25 May window). Daily is noise at ~76 clicks/day — track the monthly median.

### Recent changes (replaces the old change log — keep last ~4, one line each)

| Date | Move | Why |
|------|------|-----|
| 2026-07-07 | STANDARD budget £280 → £300 — **effective 8 Jul** | Pre-position hot-day headroom for an incoming heatwave weekend. £280 proven non-binding first: 7 Jul was the best sales day in the window (£2,773, ~12x) yet spent only £232 — under cap — so budget isn't the constraint even on rich demand. The 600 floor gates the extra cap, so soft days self-cap and the raise is costless downside ("nothing to lose"); it only spends if a weekend day clears ~6x. Smoothing ceiling → ~£600. |
| 2026-07-06 | tROAS 650% → 600% (reverted) — **effective 6 Jul** | The 650 experiment cost ~13% volume for zero efficiency gain: matched £260-cap windows both ran ~9.5x at 7.3% conv, and the spend 650 refused was converting ~8x. Reverting to the proven 600 floor reclaims that profitable tranche going into a heatwave with healthy stock (Full 54). Paired with the budget raise below — decided harvest, not diagnostic. |
| 2026-07-06 | STANDARD budget £260 → £280 (tROAS to 600) — **effective 6 Jul** | Harvest the last-peak heatwave: stock + momentum + healthy ROAS. Kept a gentle ~8% step (ceiling → ~£560) because both levers move together; plan to step up again in a couple of days, ready for next weekend. The 600 floor gates it — extra cap only spends when auctions clear ~6x, so soft days stay self-capped at £125–150. |
| 2026-06-30 | tROAS 600% → 650% (budget held £260) — **effective 30 Jun** | Still hot, strong demand, using all or most of the £260 cap. Raising tROAS to tighten the quality bar while the pool is deep — budget is the binding constraint, so the floor can do its job without costing reach. *(Reverted 6 Jul — see above; it cut volume without lifting ROAS.)* |
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
| `adcost_summary_30.csv` | Raw Google Ads export (per-campaign, 30-day daily). Save to Downloads — script auto-moves and processes. | Export columns, in order: Day, Campaign, Clicks, Impr., **Currency code**, Cost, Search impr. share, **Search lost IS (rank)**, **Search lost IS (budget)**. The parser validates/reads the first 7 by position (cost = col 6, imp share = col 7) and ignores trailing columns; the two lost columns **must be appended at the end** (they're optional — older exports without them still parse). **Imp-share lag:** Google finalises imp share / lost-IS ~2–3 days late — recent days export as `--` and load as NULL; they backfill on a later export. The current day is excluded from the export entirely. |

**Imp share source:** single-campaign imp share reads from `google_stock_track.google_search_imp_share`; the multi-campaign window 28 Apr – 13 May is NULL there — use `google_campaign_daily`.

### Data gotchas — read before trusting a number

- **Sales-date offset:** `sales.solddate` is a DATE but renders as `23:00 UTC previous day` under BST (`2026-05-18T23:00:00Z` **is 19 May**). Always `solddate::text` for daily figures; treat the latest date as partial (today, still filling). Misread twice on 19 May.
- **Snapshot sales lag:** `google_stock_track.shopify_sales` is captured at script-run time and undercounts late orders. For trends, join `google_stock_track` to `sales` on `solddate` instead.
- **Capture-before-act:** when the cap changes in the UI, add the Recent-changes row the same day even if reasoning is filled in later. (The £54→£60 ghost change came from skipping this.)
- **Multi-line single-customer orders, same style different sizes = likely try-and-return.** Net them down when reading a big AOV day. Example: 26 May £325 Bend order, sizes 40 + 41 + 41 of two similar styles — customer testing fit.

---

## The Decision Flow

Two levers: **daily budget** (how much Google can spend) and **tROAS** (how aggressively it bids). Pick the lever first, then size the move. Bias to push against: don't default to the budget lever out of habit — tROAS is the right tool as often as not.

### tROAS sets volume, demand sets efficiency (learned 14 Jun 2026)

The floor and the demand pool do **different jobs** — conflating them caused a week of arguing whether a spend lift was "the tROAS drop" or "the weather". It was both, doing different things:

- **tROAS controls VOLUME** — sessions, clicks, orders. Loosen it and Google enters more (and more marginal) auctions → more traffic; tighten it and it refuses the low-intent tail.
- **Demand controls EFFICIENCY** — conversion rate and ROAS. A pool converts at whatever intent it carries; the floor barely moves that. **Rich days hit 15–17x at any floor** (11 Jun 600→15.2x; 26 May 400→17.1x); **thin days crater at any floor** (3 Jun 400→3.4x; 12 Jun 600→5.1x). "ROAS = demand, not setting" — the great late-May days were 11–12% *conversion*, not the 400 floor (survivorship bias: 400 also produced the 3.4x worst day on record).
- **A higher floor is therefore free on a rich day** (rich traffic clears it) **and protects the thin days** (held 12 Jun to 5.1x where 400 let 3 Jun fall to 3.4x). Lowering the floor does **not** unlock more *good* demand — it buys more *low-intent* volume, which is why a loosened day looks "expensive" (more spend, lower ROAS).
- **Sessions can be bought; conversion is the honest demand tell.** A session surge at flat/low conversion (14 Jun: sessions +68% but orders only +41%, conversion 5.58%) is **bought volume, not a demand wave**. A real wave shows **conversion climbing**, not just sessions. To confirm sales are demand-real and not session-froth: hold the floor and look for *fewer sessions at similar sales* (= conversion rising).

**So picking the floor is a goal choice, not a quality fix:** volume / stock-clearance → looser (550 and below); efficiency / "stop the expense" → tighter (600+). You can't get both on the same day — that's the trade. And the real ceiling on harvesting demand is **fulfillment, not the floor** (Full at 38 and falling) — ads only harvest what you can ship.

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
- **tROAS:** *Lower* when imp share <85% AND spend below cap (volume play). *Raise* when imp share 85%+ AND marginal ROAS <5x, or 7d ROAS sliding on a ramp (efficiency play). Move ≤25% at a time; one lever at a time; give it 5–7 days to re-learn. Don't move it just because you can.

### Lost impression share — rank vs budget (the tripwire)

`google_campaign_daily.lost_is_rank` / `lost_is_budget` split the impression share we *didn't* get. They answer the question imp share alone can't: are we missing demand because we **capped out** (budget) or because a competitor **outranked** us (rank/price)?

**Baseline established 6 Jun 2026 (May–early Jun STANDARD):** lost-to-rank is **~0% every normal day** (0.00–0.12%; only ever twitched to 1.18%, on the 29 May £204 blowout). **Essentially all** lost share is **budget**. Reads:

- **We are not in a rank/price war.** When STANDARD is in an auction it wins it. So missed demand is *not* a pricing problem and *not* bid-conservatism — which removes the case for touching tROAS to "bid harder" (there's no rank loss to recover).
- **`lost_is_budget` is available impressions, NOT available profit.** It is the exact metric that suckered the £140 raise. The ~10% budget-available headroom on normal days was field-tested: filling it (£140→3.4x, £204→6.7x at 96% imp share) converts **below the 5x floor**. Don't read a budget-lost % as money on the table — the marginal impression there is browse traffic.
- **`lost_is_budget` spikes on THIN days** (30 May 48%, 17–18 May 31%) because the *eligible pool shrank*, not because a goldmine opened. It co-moves inversely with imp share; on its own it's near-redundant with the imp share we already track.

**The tripwire is `lost_is_rank`, and its whole value is staying near zero.** If STANDARD `lost_is_rank` climbs (>~5% for 2+ days), one of **three** things has happened — a competitor entered, our price slipped, **or we tightened tROAS**. The first two are a price/competitiveness problem; the third is self-inflicted and means nothing. Rule out the third before believing the first two. Quick check:

```sql
SELECT snapshot_date, search_imp_share, lost_is_rank, lost_is_budget
FROM google_campaign_daily
WHERE campaign = 'STANDARD' AND snapshot_date >= CURRENT_DATE - 14
ORDER BY snapshot_date DESC;
```

**A tighter tROAS manufactures rank-loss — it is not competition.** A higher floor makes Google *decline the marginal auctions it would have to bid up to win*; Google labels a declined auction as "lost to rank." So tightening the floor mechanically converts budget-loss into rank-loss with no competitor and no price change. **The tell is the composition flip:** when rank-loss rises *and `lost_is_budget` simultaneously collapses toward zero* on days you hold a tight floor, that's the gate working, not a rival. A *real* competitive loss shows rank-loss rising while budget-loss stays where it was. Worked example — 11–13 Jun 2026, held at tROAS 600 (the tightest floor in the window): lost-to-budget collapsed 21.4 → 4.3 → 0.2 → 0.0 while lost-to-rank rose 1.8 → 8.3 → 4.7 → 5.1, imp share never left 87–95%. The tripwire fired; cross-checks killed it — the price-benchmark scan (`shopify-price/portfolio_scan.py`) showed us *below* market on ~94% of clicked traffic, and the spike sat exactly on the tight-floor days. Self-inflicted, not a rank war.

> **Sequence to clear a `lost_is_rank` spike:** (1) did we raise tROAS in/just before the window, and did `lost_is_budget` fall toward zero as rank-loss rose? → floor artefact, ignore. (2) Run `portfolio_scan.py` — are we over benchmark on high-click styles? → real price slip. (3) Neither, and rank-loss persists at a *loose* floor with budget-loss flat? → genuine competitor entry, then it's a price/competitiveness problem. **Watch the lag:** Google finalises `lost_is_rank` ~2–3 days late (recent days load NULL), so don't close the read until the spike days have backfilled.

> **Why the ceiling floats (tied to this):** the budget level demand can fund tracks the *eligible-pool size*, not a fixed number. Normal early-Jun days run ~9–11k impressions → ceiling ~£110–130. Peak late-May days ran 14–18k → funded £150–165 at 10–17x. The cap is a **hot-day catch when the pool is big**, not a standing target to climb to. Keep budget uncapped enough to ride a big-pool day; don't set a high standing cap that buys the 3.4x tail on normal days.

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

**Analysis first, recommendation only on request.** The owner runs this daily and reads it himself. Default output is the *analysis* — the numbers, what they mean, the open question. Do **not** end every review with a recommendation or a "shall I change X?"; he'll ask when he wants one. A standing "hold" tacked onto each day is noise.

**Close the loop on yesterday — don't perpetually defer.** Because the review runs daily, today *is* the full picture for yesterday's partial. Lead with what yesterday's closed figures settled (was the last move wise? what did it teach?), rather than parking everything behind "let's see tomorrow." Deferring every read to the next day means we're never done.

**Recommendations are point-in-time, not plans.** When asked for one: write today's bias and the signals that would change it; don't bake future-step triggers into Current State ("push to £180 if X over 5 days"). The "no fixed learning window" rule applies to your own cadence too — if today's read says push, push; don't gate on a self-imposed N-day wait.

**Always read imp share — but never flag its lag as a reason to defer.** It's one of the three constraint numbers. Source is `google_campaign_daily` (per-campaign). Imp share and lost-IS always lag 2–3 days — the most recent days will always be NULL. This is normal and known; do not mention it as a gap or caveat. When NULL, infer from spend vs cap and ROAS (two consecutive over-cap days at ≥10x is a clear signal) and make the call. Never say "I'd like to wait for the data to backfill" — we make decisions on what we have.

**tROAS effective-date / stamp drift.** A tROAS change set end-of-day is effective the *next* day. The `troas` column is stamped at change-time, so the change-day row shows the **new** value but the day actually ran under the **old** floor — the first true day at a new tROAS is the day *after* the stamp. Account for this when attributing a day's result to a setting.

**Don't analyse stale data** — if the latest `snapshot_date` with ad spend is >2 days old, flag it and wait for confirmation.

1. Run the **Grid Snapshot** for the trend.
2. Read the **three constraint numbers** (imp share, spend vs cap, marginal ROAS).
3. Cross-reference the **Diagnostic table** — which lever is the constraint?
4. Present the analysis. Name the campaign. Offer a recommendation only if asked.
5. If a change is made: update **Current State** AND add a one-line row to **Recent changes**. That block is the only record — nothing is logged elsewhere.
