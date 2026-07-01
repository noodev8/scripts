# ARIZONA-GENERAL — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## What this segment is

The **minor league** for Birkenstock Arizona Birko-Flor. Every colour code that
isn't a brick lives here: seasonal re-code duplicates, material variants (Vegan,
Synthetics, Nubuck), shade experiments (eggshell, leopard, new buckle colours),
fresh-arrival stock, and the long tail.

It is a **monitor bucket, not a worklist.** You don't go code-by-code giving each
attention — you *scan* it for risers, the way LUNAR-GENERAL is scanned. Most of
what's in here will sell through and disappear, or sit at RRP until it does
something. That's fine.

The colour bricks (ARIZONA-BLACK / BLUE / BROWN / WHITE / TAUPE) are the major
league — proven Reg+Nar sellers, each its own focusable segment. GENERAL is
where everything else waits.

## Promotion / relegation — the whole point

- **Promotion unit = the shade-pair** (the Regular + Narrow of one shade, e.g.
  "Stone Coin Reg + Stone Coin Nar"). Not the `colour` field — that's too coarse
  (it lumps Eggshell + Pearl as "White", Stone Coin + Basalt + Concrete as "Grey").
- **Promote on judgment, not a number.** When a shade-pair reads as a coherent,
  live seller worth focusing on alone — top of the demand ranking, sustained not a
  blip — lift those two codes into a new `ARIZONA-<SHADE>` brick (give it the shade's
  marketing name, not the blunt colour — that's how TAUPE and the off-whites came up).
  There's no fixed revenue bar; you decide off the ranking.
- **Relegation** runs the other way: a brick that fades drops back here.
- **New codes always land here first** and earn their way out. Don't pre-judge a
  fresh arrival into a brick — let it show sustained demand first.

This is the safeguard against what happened pre-split: a riser (Blue) hiding inside
a big bucket, unseen. Scanning this report occasionally is how neglect stays
*deliberate* rather than *accidental*.

## The report — `shade_breakdown.py`

The standard report for this segment. **Replaces the default per-SKU drill.**

```
python scale/arizona-general/shade_breakdown.py
```

One row per code, **clustered by colour** (colours ordered by total demand, and
within a colour the busiest shade-pair first), so the promotion queue floats to
the top and a shade's Reg/Nar pair sit together.

Columns: Colour · Shade · Fit · GroupID · Px · Stk · u90 · u365 · Rev365.
- **Shade** is parsed from `title.shopifytitle` (the text between "… Sandals" and
  "Regular/Narrow Fit"). It's a *label* for reading the pairs by eye — naming isn't
  always clean (e.g. "Pecan" vs "Vegan Pecan" for the same colour), so trust the
  numbers, use the name to find the pair.
- **Stk** — `localstock` (`ordernum='#FREE' AND deleted=0`). **u90 / u365** —
  `sales`, `qty>0 AND soldprice>0`. **Rev365** — `SUM(qty*soldprice)` trailing 365.
- A **colour-level pulse** footer gives a coarse per-colour total. It is *not* the
  promotion unit — read the actual shade-pair off the rows.

### How to read it (under 60 seconds)

1. Top colour cluster = most live. Within it, top shade-pair = the candidate.
2. Add the pair's two Rev365 figures — a strong, sustained pair floating at the top
   is a brick conversation. Judge it off the ranking, not a fixed number.
3. Everything with Stk but u365≈0 (Concrete Grey, Sandcastle, Leo) is fresh RRP
   stock that hasn't moved — watch, don't action.

As of the May 2026 split, nothing here stands out as a brick candidate — Stone Coin
(~£2.8k trailing) and the off-whites (Eggshell ~£2.0k, Pearl ~£1.9k) lead but none is
a clear, dominant pair. So the correct state of this segment right now is **quiet**.

## Quirks worth knowing

- `skusummary.colour` is rough. "Faded Khaki" splits across Beige (Reg) and Green
  (Nar) because the colour field disagrees with itself — the shade name reveals it.
- Leopard `1030498` ("Leo Black") and Synthetics `1031495` ("Leo Pecan") are fashion
  one-offs parked here on purpose — not standard Black/Brown, won't pair with a brick.

## Defaults that still apply

- The default **Summary** (`../SEGMENT_REPORTS.md`) is still the entry report if asked
  for an "ARIZONA-GENERAL Summary". This breakdown is the *drill* — the natural next
  step, and the one that earns its keep here.
- Notes in `segment_notes` (segment = `ARIZONA-GENERAL`), top 3 on request.
- Birkenstock 150-day peak (Mar–Jul) pace.
- Per-style action lives in *state*, not in/out membership.
