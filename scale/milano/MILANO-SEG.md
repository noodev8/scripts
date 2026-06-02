# MILANO-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Status — latest thoughts

> **One current status only.** Overwrite it, don't append a diary. Clear to "—"
> once the open item is closed. Tag who wrote it (Andreas / Summer / Claude).
> Durable history lives in `price_change_log` and `segment_notes`, not here —
> this block is just "where we are right now / what to check next".

**2026-06-02 (Claude/Andreas):** Whole segment stepped up into the 2025 peak
band — Brown Reg £72.99→**£78.99**, Black Reg £68.99→**£72.99**, Brown Nar
£71.99→**£74.99**, Black Nar £66.13→**£68.99**. **Check ~2026-06-09:** does the
14d units/day rate hold after a segment-wide rise? **Black Nar is the watch
line** (broke when pushed +5.8% four weeks ago) — if it stays firm, step it on
toward the proven £72. Clear this note once checked.

## The brick

Birkenstock Milano (back-strap Birko-Flor). Two colours, each with its sister
width pair (`…01` = Regular ↔ `…03` = Narrow). Four codes, nothing outside the
segment:

| Colour | Regular | Narrow |
|--------|---------|--------|
| Brown  | `0034701-MILANO` | `0034703-MILANO` |
| Black  | `0034791-MILANO` | `0034793-MILANO` |

Code convention: last digit `1` = Regular, `3` = Narrow; the `…7x` digit carries
the colour (`…70x` Brown, `…79x` Black). Documented here so the report doesn't
re-derive widths from the DB each run.

Channel: Shopify. Cost ~£35.42–37.50 (Birko-Flor). Birkenstock 150-day peak
(Mar–Jul) pace; off-season structurally ~0% margin.

## Drill chain

Three reports, stepped through in order. Each has a **short name** (what the user
asks for) and its **script**:

| Ask for | Script | What it is |
|---------|--------|------------|
| **"Summary"** | `summary.py` | Entry report — 30d/14d YoY check |
| **"drill 1"** | `size_availability.py` | Style/width — one flat row per style/width |
| **"drill 2"** | `size_breakdown.py` | By size — each style/width row broken down by EU size |

"drill 2" is the further drill behind "drill 1". When the user names one, run that
script; the whole chain lives in this folder so it's self-contained.

### Summary — `summary.py`

```
python scale/milano/summary.py
```

The default manager Summary (per `../SEGMENT_REPORTS.md`): 30d and 14d windows,
each with same-window YoY. The table is the report; `segment_notes` are an
on-request pull, not pre-loaded.

### Drill 1 — `size_availability.py`  (style/width)

```
python scale/milano/size_availability.py
```

One flat table, **one row per style/width** (Brown Regular, Brown Narrow, Black
Regular, Black Narrow) — no per-size breakdown. Columns:
- **Stk** in stock (`localstock`, `#FREE`, `deleted=0`) · **u30 / u14** units sold.
- **Wsh** = `requested − invoiced` — future-order wishlist, *not* imminent.

Read: a row with low **Stk** but healthy **u30** is stock-constrained, not weak
demand; **Wsh** shows what's stuck on the 6-month order cycle. Brown and Black
move differently and carry different incoming positions.

### Drill 2 — `size_breakdown.py`  (by size)

```
python scale/milano/size_breakdown.py
```

The further drill behind drill 1. **Size-as-columns**: one row per style/width,
one column per EU size — keeps the four-line spine and lets you scan a size
profile across all four at once. (Size-as-rows was tried and rejected — it breaks
the one-row-per-style/width spine.)

Each cell shows two metrics together, **locked default `u30(stk)`**:

    sold-30d ( in stock )      e.g.  9(3) = sold 9 in 30d, 3 left in stock

Demand leads the eye; stock cover sits in brackets. A cell like `9(3)` — high
sold, low stock — is an at-risk size about to gap out; `0(0)` on a size that
sells elsewhere is a stockout *suppressing* demand, not dead demand.

Other pairings (e.g. `stk(u30)`, or `u14`/`wsh`) are a one-line `PRIMARY` /
`BRACKET` switch at the top of the script — change, run, change back. The
default stays `u30(stk)`.

Size = the 2-digit `skumap.code` suffix (e.g. `…-37`), always euro by design.
We do not use `uksize`/`eurosize`.

## Defaults that still apply

- Notes in `segment_notes` (segment = `MILANO-SEG`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace. Per-style action lives in *state*, not membership.
