# MAYARI-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Why this segment gets its own drill

Same shape of problem as EVA and Arizona Patent: a handful of active sellers, a stocked-but-quiet middle, a sell-through tail. Going SKU-by-SKU is wasted motion; the right entry point after the Summary is "which rows have stock to act on, and which are stock-gutted?".

Same two-step flow:

1. **Summary** (default template from `../SEGMENT_REPORTS.md`) — the entry report. Run on request, then **stop**. Present the Summary and end with a single-line offer: *"If you want to drill, the next step for MAYARI-SEG is the stock-availability triage."* Do **not** auto-run the triage even if the Summary looks bad.
2. **Stock-availability triage** — `python scale/mayari/stock_triage.py`. One row per groupid, sorted by total stock DESC then u30 DESC.

The standard per-SKU drill from `../SEGMENT_REPORTS.md` is **not** the default drill — the triage replaces it. Per-SKU still available on request for a single groupid.

## Stock-availability triage (drill)

Script: `scale/mayari/stock_triage.py`. Output shape:

```
 #  GroupID                Colour/Fit             Px     Cov Stock  u30  u14  Inc
 1  …
```

- **Px** — listed `skusummary.shopifyprice`.
- **Cov** — sizes-in-stock / total-size-universe. Universe from `skumap` (`deleted=0`). Never `skusummary.variants`/`stockvariants`.
- **Stock** — total `localstock` units across all sizes, `ordernum='#FREE' AND deleted=0`.
- **u30 / u14** — units in last 30 / 14 days, `sales` with `qty>0 AND soldprice>0`.
- **Inc** — pending Birk units from `birktracker`, `SUM(GREATEST(requested-arrived,0))`.

Sort: `Stock DESC, u30 DESC`.

## Triage philosophy

Same as EVA / Arizona Patent: one priority category, *"Stocked + not moving in peak season"*. High-stock end is where price/listing work pays off. Low-stock end is drop-further-or-wait, with the `Inc` column carrying the wait signal.

Mayari-specific watchouts: to be added once a few sessions reveal them.

## Working rhythm

1. Run the Summary, present it, stop. Offer the triage as the next step.
2. User decides whether to drill.
3. In the triage, pick one or two items per session; log decisions to `segment_notes`.
4. Re-run next session — most rows won't have moved, attention narrows.

## Defaults that still apply

- 14d / 30d windows from `../SEGMENT_REPORTS.md`.
- Pace projection: Birkenstock 150-day peak (Mar–Jul).
- Notes stored in `segment_notes`, surface top 3 alongside the report.
- Per-style action lives in *state*, not in/out membership.
