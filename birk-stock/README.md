# birk-stock

Snapshot of Birkenstock stock health to decide whether to push or scale back Google Ads.

## Purpose

One question: **how many styles can the core customer actually buy right now?**

No point pushing traffic onto styles that are missing the women's core sizes (38/39/40). So we count the styles that hold all three — **Full** — across the whole Birkenstock range. Full is the breadth of core-complete product ad spend can ride; it's the number we push or pull against.

We want a position we can be **confident** about. Target: grow Full toward the full range. Styles that aren't Full are a signal to restock or to drop them from the range — not something to filter out of the number.

## Scope

In scope:
- **Birkenstock brand only**, strict (`skusummary.brand = 'Birkenstock'` — verify exact string).
- **Stock = FREE rows in `localstock`**: `ordernum = '#FREE' AND deleted = 0 AND qty > 0`. Nothing else.
- **Every** style whose grid offers 38/39/40 — no sales/demand filter.
- The **Full** count + (under `--detail`) breakdowns so it can be sanity-checked.

Out of scope (handle outside this process):
- **Seasonality** — interpret manually from the breakdowns.
- **Profit / margin** — keep/drop decisions live elsewhere.
- **Pipeline / Birktracker / in-transit** — not counted. Only what is physically FREE now. (May reintroduce Birktracker later as a separate "what's coming" view; not now.)
- **Channel split** — single combined view for v1.

## Core metric — Full count

**Full = styles with all three core sizes (38/39/40) in FREE stock.** No sales filter, no depth weighting, no partial credit. Any quantity counts — 1+1+1 is Full. It's the breadth of *core-complete* product: how many styles ad spend can confidently ride right now.

Why Full and not a coverage %: a percentage is a ratio, so it hides scale — "33% of 125 styles" and "33% of 10 styles" are wildly different push positions but read the same. Worse, a coverage % is contaminated by the denominator: dumping more dead styles into the range craters the % while real ad capacity is unchanged. **Full is absolute** — it moves only when real sellable breadth moves, and is immune to how aggressively the range has been pruned. (Decided 2 Jun 2026, after trying a demand-weighted whole-grid metric, then a depth-weighted coverage %, then settling here.)

**Target: grow Full toward Styles** (every in-range style core-complete). A style not Full is either a restock gap or a straggler to drop — the owner's call.

### Settled parameters

- **Denominator (`Styles`)**: every Birkenstock style whose grid (`skumap`, `deleted = 0`) offers all of 38/39/40. **No sales/demand filter.** Requiring 38/39/40 in the grid drops men's-only grids (no 38). ~125 styles today.
- **Core sizes**: 38, 39, 40 (women's core).
- **Full**: a style counts if all three core sizes have FREE qty > 0 (any amount).
- **Full %**: Full ÷ Styles — progress toward a fully stocked range; read as trend, not as the decision number.
- **Partials (1–2 of 3)**: a hidden bonus — real sellable breadth, but not tracked in the headline. Decisions ride on Full only.

The honest signal today: **28 Full of 125 (22%)** — core-complete breadth is thin, so don't be over-confident pushing until Full climbs (stock landing in the core, or dead stragglers pruned out of the range).

## Output — locked format

One at-a-glance table, **one row per day**:

| Date | Full | Styles | Full % |
|---|---|---|---|
| 2026-06-02 | 28 | 125 | 22% |

- **Full** — the decision number: styles with all 3 core sizes in stock (push capacity).
- **Styles** — total in-range styles (Birk grids offering 38/39/40); the ceiling.
- **Full %** — Full ÷ Styles; progress toward a fully stocked range, read as trend.

The console prints the last ~7 days of this table (trend at a glance). `availability.py --detail` additionally prints the per-size breakdown (what's blocking Full) and the not-Full styles weakest-first (the prune/restock shortlist) — off by default; the table is the whole result.

**Presenting the run in chat:** when the owner asks for a birk-stock run, render the result back as a **markdown grid** (the Date/Full/Styles/Full % table), not raw console text. A clean grid is the expected format every time.

This is the only output. No depth weighting, no status buckets, no per-size in the headline — locked 2 Jun 2026.

## Data sources

- **Size grid (denominator)** — `skumap` where `deleted = 0`; a style is in scope if its grid offers all of 38/39/40.
- **Current stock per size** — `localstock` where `ordernum = '#FREE' AND deleted = 0 AND qty > 0`, joined to `skumap` for size labels.
- **Brand filter** — `skusummary.brand = 'Birkenstock'`.
- **No `sales` query** — the gauge is sales-independent by design.

**Do NOT use:** `skusummary.stockvariants`, `skusummary.variants`, `skumap.shopifyprice`, `skusummary.ignore_auto_price`. All stale/legacy — see project CLAUDE.md.

## Size / depth weighting

None. Full is a plain count — all three core sizes present, any quantity. No per-size curves, no depth tiers. (Both were tried and dropped; an earlier `size_weights.py` is deleted.) The depth nuance — a 1+1+1 style empties fast — is accepted as a known limitation: it still counts as Full, and partials below it are an untracked bonus.

## Cadence

Ad-hoc, on user request. No materialisation, no dashboard tile.

## Reading the table

- **Full** is the decision number. Read it as a level *and* a direction: a high/rising Full means more core-complete breadth to push spend into; low/falling means less. Read it together with **Styles** — Full's ceiling.
- **Full %** is the trend gauge (progress toward a fully stocked range), not the decision driver. Don't read it alone: scale lives in Full, not the ratio.
- To improve Full, run `--detail`: the per-size lines show which size is most often the blocker, and the not-Full list (weakest first) is the prune/restock shortlist.

### How the number is used

It feeds Google Ads budget decisions as a **consideration, not a gate** — full principle in `google-ads/BUDGET_REVIEW_PROCESS.md` ("Stock availability (Birk core sizes)"). In short: Full is a confidence modifier on *how hard* to push; the go/no-go stays imp share + ROAS. A low Full and high ROAS aren't a contradiction — Full is range breadth, not fulfillability of the traffic we buy, and spend self-steers to the in-stock styles. Rising Full = more headroom to add budget (if imp share short, ROAS healthy); falling Full = lean on tROAS and push more cautiously into thinning fulfillment. No fixed push/hold/pull thresholds.

### Snapshots

`availability.py` auto-writes one row per day to the table in `snapshots.md` (latest run of
the day overwrites that day's row). Metrics only — no commentary. Budget/ad decisions belong
in `google-ads/BUDGET_REVIEW_PROCESS.md`, not here.

## Velocity (`--velocity`) — the pricing focus list

`availability.py --velocity` keeps the locked headline table, then attaches **sales
velocity to the Full styles only** — the list of styles you can actually act on for
pricing. For each Full style: trailing units sold over 30d / 90d / 365d, 90-day
**units/day**, and **weeks of cover** (total FREE stock ÷ weekly rate; `inf` = no 90d
sales). Sorted fastest-first, so the styles worth pricing attention sit at the top and
the dead weight (full grids, ~0 sales) sinks to the bottom.

This is the lens for "what should I focus pricing on?": the top of the list is where
demand is real (watch the low weeks-of-cover ones for restock before pushing spend); the
bottom is the prune/clear shortlist — core-complete styles tying up the Full count without
earning it.

Channel: sales are **all-channel by design, and that's correct here** — Birkenstock is
**not sold on Amazon** (not permitted), so all-channel is effectively Shopify + the
physical shop, with no Amazon contamination. Keeping it all-channel deliberately covers
the shop alongside the website. No channel split needed. Velocity is **not** part of the
locked Full gauge; it's an opt-in companion view and is **not** written to `snapshots.md`.

## Files

- `availability.py` — ad-hoc Full-count gauge. Run with `python birk-stock/availability.py` (`--detail` for per-size + prune list; `--velocity` for the per-style sales-velocity pricing focus list).
- `snapshots.md` — daily metrics log (auto-written, one row per day) for trend comparison. Velocity is **not** logged here.
