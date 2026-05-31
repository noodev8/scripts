# ARIZONA-BROWN — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## The brick

Two codes, the canonical Brown Birko-Flor pair:
- `0051701-ARIZONA` — Regular
- `0051703-ARIZONA` — Narrow

Channel: Shopify. One of the four founding colour bricks (with Black/Blue/White),
split out of the old ARIZONA-BF-REG/NAR in May 2026. Material variants (e.g. the
"Leo Pecan" Synthetics code) live in ARIZONA-GENERAL, not here.

## Why a size report, not a triage

A 2-code brick doesn't need a per-groupid triage (that's for many-style segments
like Patent). It needs the **per-size** picture, because the live question for a
winning colour is *"which sizes can I get back in stock for peak, and how fast?"*

Brown is the case in point: it sells ~15 Reg + ~18 Nar a month off almost no Reg
stock. The Regular core run (36–42) is stock-gutted — but the report shows that
stock isn't 6 months away.

## The report — `size_availability.py`

The brick drill. **Replaces the default per-SKU drill.**

```
python scale/arizona-brown/size_availability.py
```

One row per EU size, Regular and Narrow side by side. Columns per fit:

| Col | Meaning |
|---|---|
| **Stk** | in stock now — `localstock`, `ordernum='#FREE' AND deleted=0` |
| **u30 / u14** | units sold, 30d / 14d — `sales`, `qty>0 AND soldprice>0` |
| **Inv** | `invoiced − arrived` — billed but not yet received. **Releasable NOW by paying the outstanding invoice.** The in-season lever. |
| **Wsh** | `requested − invoiced` — on a future order, not yet billed. The 6-month wishlist. Aspirational — *not* imminent stock. |

Size = the 2-digit suffix on `skumap.code` (e.g. `...-37`), which is **always the
euro size by design**. We do not use `skumap.uksize` or `skumap.eurosize`.

### The Inv / Wish split is the whole point

This is the only place the in-season lever is visible. Per the standing rule
([[feedback_birk_ordering_cycle]]): Birkenstock is a 6-month cycle, so you can't
"reorder" mid-season — but you **can** pay an outstanding invoice to release stock
that's already been billed and allocated. **Inv** is that stock. **Wsh** is the
wishlist that won't help peak — don't plan around it.

### How to read it

1. Find sizes with `Stk 0` but `u30 > 0` — selling from nothing, losing sales.
2. Check their **Inv**. Units there = pay the invoice, get them back in weeks.
3. Sizes with only **Wsh** (no Inv) are the 6-month horizon — note, don't chase.
4. Core sizes (≈37–42) matter most; tail sizes can wait.

As of the May 2026 split: Reg core 36–42 is 0 stock but **2 units each invoiced**
(14 total, invoice raised 27.05.2026) — releasable for peak. Narrow core similar
(11 invoiced). That's the "6 weeks not 6 months" conversation in one screen.

## Cloning to the other bricks

Black / Blue / White / Taupe use the same shape. Copy this folder, change `SEG`,
adjust the md. Each is self-contained — fixes don't propagate (see
`../SEGMENT_REPORTS.md`). Watch BLUE: its Narrow code (`0051753`) has null
`width`, so the fit falls back to the title parse — verify it reads "Nar".

## Defaults that still apply

- Default **Summary** (`../SEGMENT_REPORTS.md`) is the entry report; this is the drill.
- Notes in `segment_notes` (segment = `ARIZONA-BROWN`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace.
- Per-style action lives in *state*, not in/out membership.
