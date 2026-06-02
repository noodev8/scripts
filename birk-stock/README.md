# birk-stock

Snapshot of Birkenstock stock health to decide whether to push or scale back Google Ads.

## Purpose

One question: **is the stock position strong enough to justify pushing ads right now?**

No point pushing traffic if the women's core sizes (38/39/40) are missing across the Birkenstock range. We measure that directly — every style that *should* carry those sizes, scored on whether it actually does.

We want a position we can be **confident** about. Target is 100%: every in-range style holding its core sizes. Stragglers that sit empty are a signal to restock or to drop them from the range — not something to filter out of the number.

## Scope

In scope:
- **Birkenstock brand only**, strict (`skusummary.brand = 'Birkenstock'` — verify exact string).
- **Stock = FREE rows in `localstock`**: `ordernum = '#FREE' AND deleted = 0 AND qty > 0`. Nothing else.
- **Every** style whose grid offers 38/39/40 — no sales/demand filter.
- A headline metric + breakdowns so the headline can be sanity-checked.

Out of scope (handle outside this process):
- **Seasonality** — interpret manually from the breakdowns.
- **Profit / margin** — keep/drop decisions live elsewhere.
- **Pipeline / Birktracker / in-transit** — not counted. Only what is physically FREE now. (May reintroduce Birktracker later as a separate "what's coming" view; not now.)
- **Channel split** — single combined view for v1.

## Core metric (v1 — "can the core customer buy?")

**Core-size depth-coverage, equal weight per style. No sales filter.** Across *every* Birkenstock style whose grid offers the women's core sizes (38/39/40), what fraction of those core slots are stocked — credited gently by depth so a single unit (empties on the next sale) counts less than a real cushion?

One number, 0–100%. Roll-up: brand headline ← mean over all core slots ← per-style core grid.

**Target is 100%.** Every style in the range *should* hold its core sizes. A style sitting empty on 38/39/40 isn't noise to be filtered out — it's either a restock gap or a straggler that should be dropped from the range. That's the owner's call; the gauge's job is to surface it, not to hide it behind a demand filter. We deliberately do **not** weight by sales: a demand cut just flatters the number by ignoring the styles we've let go thin.

Designed (2 Jun 2026) to replace the earlier demand-weighted whole-grid metric + per-model size curves — dropped as over-engineered. ~10× simpler, fully explainable in one sentence.

### Settled parameters

- **Denominator (styles in scope)**: every Birkenstock style whose grid (`skumap`, `deleted = 0`) offers all of 38/39/40. **No sales/demand filter.** Requiring 38/39/40 in the grid drops men's-only grids (no 38). ~125 styles today.
- **Core sizes**: 38, 39, 40 (women's core).
- **Depth credit (per core size, from FREE stock qty)**: 0 → 0, 1 → 0.5, 2 → 0.8, 3+ → 1.0.
- **Per-style credit**: mean of its three core-slot credits.
- **Headline**: mean credit across all core slots (equal weight per style, since each contributes exactly 3 slots). Target 100%.

The honest signal this gives today (~33%): the core is genuinely thin across the range — lots of styles empty on 38/39/40 — so the number says "don't be over-confident pushing" until either stock fills in or the dead stragglers are pruned out of the range.

## Output — locked format

One at-a-glance table, **one row per day**:

| Date | 38 | 39 | 40 | Overall | Styles | Full | Partial | Empty |
|---|---|---|---|---|---|---|---|---|
| 2026-06-02 | 40% | 36% | 47% | 33% | 125 | 28 | 52 | 45 |

- **38 / 39 / 40** — % of in-range styles with that size in FREE stock (the per-size weak-spot read).
- **Overall** — the headline: depth-weighted core coverage, target 100% (see [Core metric](#core-metric-v1--can-the-core-customer-buy)).
- **Styles** — number of in-scope styles (Birk grids offering 38/39/40).
- **Full / Partial / Empty** — styles by how many core sizes are in stock: **Full** = all 3, **Partial** = 1–2, **Empty** = 0. (`Full + Partial + Empty = Styles`.)

The console prints the last ~7 days of this table (trend at a glance). `availability.py --detail` additionally prints the weakest-first per-style grid — the prune/restock shortlist — but that is off by default; the table is the whole result.

This is the only output. No status buckets, no drag list, no sparkline — locked 2 Jun 2026.

## Data sources

- **Size grid (denominator)** — `skumap` where `deleted = 0`; a style is in scope if its grid offers all of 38/39/40.
- **Current stock per size** — `localstock` where `ordernum = '#FREE' AND deleted = 0 AND qty > 0`, joined to `skumap` for size labels.
- **Brand filter** — `skusummary.brand = 'Birkenstock'`.
- **No `sales` query** — the gauge is sales-independent by design.

**Do NOT use:** `skusummary.stockvariants`, `skusummary.variants`, `skumap.shopifyprice`, `skusummary.ignore_auto_price`. All stale/legacy — see project CLAUDE.md.

## Size weighting

None. The earlier metric weighted each size within a style by a women's/men's replacement curve (`size_weights.py`, since deleted). v1 counts only the three core sizes, each equally.

## Cadence

Ad-hoc, on user request. No materialisation, no dashboard tile.

## Reading the table

- **Overall** is the one number — depth-weighted core coverage, target 100%. Read it as direction over time, not against a fixed cutoff.
- **38 / 39 / 40** show which size is the weak spot (e.g. today 39 is worst at 36%, 40 best at 47%).
- **Full / Partial / Empty** is the completeness split. A high Empty count is the prune-or-restock signal: those styles either need core stock or should be dropped from the range. Run `--detail` to see exactly which.

### How the number is used

It feeds Google Ads budget decisions as a **consideration, not a gate** — full principle in `google-ads/BUDGET_REVIEW_PROCESS.md` ("Stock availability (Birk core sizes)"). In short: it's a confidence modifier on *how hard* to push; the go/no-go stays imp share + ROAS. A low number and high ROAS aren't a contradiction — the headline is range completeness, not fulfillability of the traffic we buy, and spend self-steers to the in-stock styles. Rising coverage = more headroom to add budget (if imp share short, ROAS healthy); falling coverage = lean on tROAS and push more cautiously into thinning fulfillment. No fixed push/hold/pull thresholds.

### Snapshots

`availability.py` auto-writes one row per day to the table in `snapshots.md` (latest run of
the day overwrites that day's row). Metrics only — no commentary. Budget/ad decisions belong
in `google-ads/BUDGET_REVIEW_PROCESS.md`, not here.

## Files

- `availability.py` — ad-hoc core-size gauge. Run with `python birk-stock/availability.py`.
- `snapshots.md` — daily metrics log (auto-written, one block per day) for trend comparison.
