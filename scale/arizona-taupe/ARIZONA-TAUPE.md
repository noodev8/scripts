# ARIZONA-TAUPE — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## The brick

The Graceful Taupe Birko-Flor pair:
- `1029470-ARIZONA` — Regular
- `1029439-ARIZONA` — Narrow

Channel: Shopify. **The first promotion** out of ARIZONA-GENERAL (May 2026),
lifted on trajectory: ~£4.4k trailing revenue with ~31 of 61 annual units in the
last 90 days — a clear rising pair. Promoted on judgment, not a threshold cross —
so the standing question for this brick is *"is it still a live, coherent seller,
or has it faded enough to relegate back to GENERAL?"*

## The report — `size_availability.py`

```
python scale/arizona-taupe/size_availability.py
```

One row per EU size, Regular + Narrow side by side. Per fit:
- **Stk** in stock (`localstock`, `#FREE`, `deleted=0`) · **u30 / u14** units sold.
- **Inv** = `invoiced − arrived` — billed, not arrived. **Releasable now by paying the invoice** — the in-season lever ([[feedback_birk_ordering_cycle]]).
- **Wsh** = `requested − invoiced` — future-order wishlist, *not* imminent.

Size = the 2-digit `skumap.code` suffix (e.g. `...-37`), always euro by design.
We do not use `uksize`/`eurosize`.

## Read

Stock-thin both fits, all incoming is **Wsh** (future order) — no Inv to release,
so no in-season lever right now. Demand depends on what's already on the shelf.
Watch the trailing revenue: a fade back below ~£4k is the relegation signal.

## Defaults that still apply

- Default **Summary** (`../SEGMENT_REPORTS.md`) is the entry report; this is the drill.
- Notes in `segment_notes` (segment = `ARIZONA-TAUPE`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace. Per-style action lives in *state*, not membership.
