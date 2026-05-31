# ARIZONA-WHITE — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## The brick

The canonical White Birko-Flor pair:
- `0552681-ARIZONA` — Regular
- `0552683-ARIZONA` — Narrow

Channel: Shopify. A founding colour brick (May 2026).

**The White wrinkle.** White is the most code-fragmented colour. Two distinct
off-white shades — **White Eggshell** (`1027346`/`1027339`) and **Graceful Pearl
White** (`1009920`/`1009921`) — sit in ARIZONA-GENERAL, each with real residual
demand (~u20-30/yr) but neither at the £5k brick bar. They're the *same shoe class*
as this brick, so as they deplete their demand should flow to `0552681`/`0552683`
— make sure this brick has the stock depth to catch it. They will not earn their
own brick; they sell through. (If a genuinely new white shade ever clears £5k,
that's a new brick conversation.)

## The report — `size_availability.py`

```
python scale/arizona-white/size_availability.py
```

One row per EU size, Regular + Narrow side by side. Per fit:
- **Stk** in stock (`localstock`, `#FREE`, `deleted=0`) · **u30 / u14** units sold.
- **Inv** = `invoiced − arrived` — billed, not arrived. **Releasable now by paying the invoice** — the in-season lever ([[feedback_birk_ordering_cycle]]).
- **Wsh** = `requested − invoiced` — future-order wishlist, *not* imminent.

Size = the 2-digit `skumap.code` suffix (e.g. `...-37`), always euro by design.
We do not use `uksize`/`eurosize`.

## Read

White Reg core is stock-thin but carries a healthy **Inv** block (≈19 units
invoiced) — releasable for peak by paying the invoice. Cross-check against the
Eggshell/Pearl demand in GENERAL when judging how much depth to release.

## Defaults that still apply

- Default **Summary** (`../SEGMENT_REPORTS.md`) is the entry report; this is the drill.
- Notes in `segment_notes` (segment = `ARIZONA-WHITE`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace. Per-style action lives in *state*, not membership.
