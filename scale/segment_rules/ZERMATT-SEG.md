+# ZERMATT-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Why this segment is different

12 groupids covering two sub-families, distinguished by `skusummary.material`:

- **Cork Latex** (6 styles) — historically Mar-Jun peak, but Zermatt sells year-round in practice. Pace 365d.
- **Shearling** (6 styles) — historically Jul-Feb peak, also sells year-round. Pace 365d.

All ZERMATT-SEG groupids carry `season='Any'` — the cork/shearling distinction lives in `material`, **not** in `season`. Don't infer material from season.

Both materials live in one segment because the manager view of "is Zermatt working?" needs both visible. The material split matters at decision time (cork buyers ≠ shearling buyers), not at report time.

Per-SKU view at this scale produces a ~60-row size table that buries the signal. The questions are at the style level — which colour/width is moving, which is stocked-but-dead, which is OOS-and-incoming.

So ZERMATT-SEG uses EVA's triage shape: one row per groupid, sorted to surface the styles where decisions are actually available.

## Stock-availability triage (drill)

Same shape as `../eva/EVA-SEG.md`. Output:

```
 #  GroupID                Colour/Fit             Px     Cov Stock  u30  u14  Inc
```

- **Px** — `skusummary.shopifyprice`.
- **Cov** — sizes-in-stock / total-size-universe. Universe denominator from `skumap` where `deleted=0` (never `skusummary.variants`/`stockvariants` — see top-level `CLAUDE.md`).
- **Stock** — total `localstock` units across all sizes, `ordernum='#FREE' AND deleted=0`.
- **u30 / u14** — `sales` with `qty>0 AND soldprice>0`, windows from Summary.
- **Inc** — pending Birk units, `birktracker` summed as `SUM(GREATEST(requested-arrived, 0))` per groupid. Total only; due-month detail is a drill.

Sort: `Stock DESC, u30 DESC` — items with most stock and most recent demand surface first, stock-gutted decisions sit at the bottom.

Include material inline with Colour/Fit (e.g. `Grey / Regular · Cork`) so the cork/shearling split is visible without a separate table. Source from `skusummary.material`.

The standard per-SKU drill from `../SEGMENT_REPORTS.md` is **not** the default drill for ZERMATT-SEG — the triage replaces it. Per-SKU is still available on request when a single groupid's size mix needs a closer look.

## How to read it

- **High Stock + low u14/u30** → stocked-but-dead. Price/listing work pays off here. Use the material lens for context (a shearling style with no sales in May still warrants attention now that we treat Zermatt as year-round — don't dismiss it as off-season).
- **u14 ≈ u30** (i.e. doing all its work recently) → recent acceleration, check price headroom.
- **u14 ≪ u30/2** → cooling. Check whether OOS-driven (Stock low) or demand-driven.
- **Low Stock + Inc > 0** → wait for Birk; no current decision.
- **Low Stock + Inc = 0** → sell-through tail; let it run out under category-boundary principle.

## Working rhythm

1. **Run the Summary**, present it, **stop**. End with single-line offer: *"If you want to drill, the next step for ZERMATT-SEG is the stock-availability triage."*
2. User decides whether to drill. Only run the triage when explicitly asked.
3. Discuss priority before listing decisions. Pick one or two rows per session.
4. Log decisions as `segment_notes` rows.

## Defaults that still apply

- 14d / 30d windows from `../SEGMENT_REPORTS.md`.
- Pace projection: 365d year-round for both materials (matches `../SEGMENT_REPORTS.md`).
- Notes stored in `segment_notes`, surface top 3 alongside the report on request.
- Category-boundary principle — every Zermatt groupid stays in; per-style action carried by state.
