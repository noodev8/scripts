+# MADRID-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Why this segment is different

10 groupids (Black / Brown / White × Regular / Narrow, plus EVA Black variants). Small enough that the standard per-SKU drill produces a 40-row size table where the signal gets lost — the questions are almost always at the style level, not the size level.

So MADRID-SEG borrows EVA's triage shape verbatim: one row per groupid, sorted to surface the styles where decisions are actually available.

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

The standard per-SKU drill from `../SEGMENT_REPORTS.md` is **not** the default drill for MADRID-SEG — the triage replaces it. Per-SKU is still available on request when a single groupid's size mix needs a closer look.

## How to read it

- **High Stock + low u14/u30** → stocked-but-dead. Price/listing work pays off here.
- **u14 ≈ u30** (i.e. doing all its work recently) → recent acceleration, defend the margin / check headroom.
- **u14 ≪ u30/2** → cooling. Check whether OOS-driven (Stock low) or demand-driven.
- **Low Stock + Inc > 0** → wait for Birk; no current decision.
- **Low Stock + Inc = 0** → sell-through tail; let it run out under category-boundary principle.

## Working rhythm

1. **Run the Summary**, present it, **stop**. End with single-line offer: *"If you want to drill, the next step for MADRID-SEG is the stock-availability triage."*
2. User decides whether to drill. Only run the triage when explicitly asked.
3. Discuss priority before listing decisions. Pick one or two rows per session.
4. Log decisions as `segment_notes` rows.

## Defaults that still apply

- 14d / 30d windows from `../SEGMENT_REPORTS.md`.
- Pace projection: Birkenstock 150-day peak (Mar-Jul).
- Notes stored in `segment_notes`, surface top 3 alongside the report on request.
- Category-boundary principle — every Madrid groupid stays in; per-style action carried by state.
