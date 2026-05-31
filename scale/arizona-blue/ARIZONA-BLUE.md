# ARIZONA-BLUE — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## The brick

The canonical Blue Birko-Flor pair:
- `0051751-ARIZONA` — Regular (the **fastest riser** in the range — ~38 units in the last 30 days)
- `0051753-ARIZONA` — Narrow. **Null `width`** in skusummary, so its fit resolves
  from the title parse ("Narrow Fit"). It's a fresh restock listed at £85 and not
  yet moving — watch the price as much as the stock.

Channel: Shopify. A founding colour brick (May 2026), pulled out specifically
because it was surging unnoticed inside the old width buckets.

## The report — `size_availability.py`

```
python scale/arizona-blue/size_availability.py
```

One row per EU size, Regular + Narrow side by side. Per fit:
- **Stk** in stock (`localstock`, `#FREE`, `deleted=0`) · **u30 / u14** units sold.
- **Inv** = `invoiced − arrived` — billed, not arrived. **Releasable now by paying the invoice** — the in-season lever ([[feedback_birk_ordering_cycle]]).
- **Wsh** = `requested − invoiced` — future-order wishlist, *not* imminent.

Size = the 2-digit `skumap.code` suffix (e.g. `...-37`), always euro by design.
We do not use `uksize`/`eurosize`.

## Read

The Regular is the story — selling hard, stock thin on core sizes. Blue carries
no Inv right now, so peak depth depends on the future order (Wsh) landing, or on
holding price while stock lasts. The £85 Narrow is a pricing question first.

## Defaults that still apply

- Default **Summary** (`../SEGMENT_REPORTS.md`) is the entry report; this is the drill.
- Notes in `segment_notes` (segment = `ARIZONA-BLUE`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace. Per-style action lives in *state*, not membership.
