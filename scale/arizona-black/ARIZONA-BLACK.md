# ARIZONA-BLACK — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## The brick

The canonical Black Birko-Flor pair:
- `0051791-ARIZONA` — Regular (the range's volume leader, ~92 u/yr)
- `0051793-ARIZONA` — Narrow

Channel: Shopify. A founding colour brick (May 2026). **Not here, on purpose:**
the dead seasonal dupes (Metallic Black `1029233`/`1029224`, Vegan Black `1019115`)
and the Leopard "Leo Black" `1030498` all live in ARIZONA-GENERAL — they're not
the standard Black and won't pair with this brick.

## The report — `size_availability.py`

```
python scale/arizona-black/size_availability.py
```

One row per EU size, Regular + Narrow side by side. Per fit:
- **Stk** in stock (`localstock`, `#FREE`, `deleted=0`) · **u30 / u14** units sold.
- **Inv** = `invoiced − arrived` — billed, not arrived. **Releasable now by paying the invoice** — the in-season lever ([[feedback_birk_ordering_cycle]]).
- **Wsh** = `requested − invoiced` — future-order wishlist, *not* imminent.

Size = the 2-digit `skumap.code` suffix (e.g. `...-37`), always euro by design.
We do not use `uksize`/`eurosize`.

## Read

Sizes with `Stk 0` but `u30 > 0` are bleeding sales; check **Inv** for what's
releasable. Black currently carries no Inv (nothing invoiced to release) and a
large Wsh — its lever is the future order, not a mid-season release.

## Defaults that still apply

- Default **Summary** (`../SEGMENT_REPORTS.md`) is the entry report; this is the drill.
- Notes in `segment_notes` (segment = `ARIZONA-BLACK`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace. Per-style action lives in *state*, not membership.
