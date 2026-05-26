# birk-stock

Snapshot of Birkenstock stock health to decide whether to push or scale back Google Ads.

## Purpose

One question: **is the stock position strong enough to justify pushing ads right now?**

No point pushing traffic if the top sellers are out, or if the popular sizes are missing on the styles that are actually selling.

The metric doesn't need to be 100% correct — we want a position we can be **confident** about, not a perfect number.

## Scope

In scope:
- **Birkenstock brand only**, strict (`skusummary.brand = 'Birkenstock'` — verify exact string).
- **Stock = FREE rows in `localstock`**: `ordernum = '#FREE' AND deleted = 0 AND qty > 0`. Nothing else.
- Recent unit-level demand vs current size-level stock.
- A headline metric + breakdowns so the headline can be sanity-checked.

Out of scope (handle outside this process):
- **Seasonality** — interpret manually from the breakdowns.
- **Profit / margin** — keep/drop decisions live elsewhere.
- **Pipeline / Birktracker / in-transit** — not counted. Only what is physically FREE now. (May reintroduce Birktracker later as a separate "what's coming" view; not now.)
- **Channel split** — single combined view for v1.

## Core metric

**Demand-weighted availability, weighted by units.** Of the units we'd expect to sell over the recent window, what % can we actually fulfil from current FREE stock?

Roll-up: brand headline → style (groupid) → size within style.

### Settled parameters

- **Demand window**: 28d trailing for the score. Also compute 7d alongside as a "recent acceleration / deceleration" arrow per top style. Headline = 28d.
- **Weighting**: units sold.
- **Low-stock credit (per size)**: qty ≥ 2 = full, qty = 1 = half, qty = 0 = none.
- **Demand scope**: Shopify-only (`channel = 'SHP'`). Amazon has no Birk sales; CM3 (shop) is minimal — exclude.
- **Size weight within a style**: rules-based — see [Size weighting](#size-weighting) below.

## Breakdowns

1. **Style (groupid) traffic light** — top N groupids by recent units, each in-stock / partial / out. Sanity check against the headline.
2. **Size coverage within style** — score size availability weighted by which sizes actually sell on that style.

## Data sources

- **Demand** — `sales` table.
- **Current stock per size** — `localstock` where `ordernum = '#FREE' AND deleted = 0 AND qty > 0`, joined to `skumap` for size labels.
- **Brand filter** — `skusummary.brand = 'Birkenstock'`.

**Do NOT use:** `skusummary.stockvariants`, `skusummary.variants`, `skumap.shopifyprice`, `skusummary.ignore_auto_price`. All stale/legacy — see project CLAUDE.md.

## Size weighting

Two replacement curves, women's and men's, each summing to 1.0 across its defined sizes.

**Assignment rule (women's priority):** a groupid is classified women's if its size universe (from `skumap`) contains any size ≤ 37; otherwise men's. This correctly classifies pure women's grids (35–43) and unisex grids that include small sizes (e.g. Boston 36–46) as women's, and reserves the men's curve for men's-only grids (39–47).

Sizes present on a style but absent from its assigned curve contribute 0 to availability — accepted as a small distortion, revisit only if it skews real outputs.

Values and the `curve_for(size_universe)` helper live in `size_weights.py`.

## Cadence

Ad-hoc, on user request. No materialisation, no dashboard tile.

## Files

- `size_weights.py` — women's & men's size-weight curves + assignment helper.
