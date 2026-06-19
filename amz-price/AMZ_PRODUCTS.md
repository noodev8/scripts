# Amazon Pricing — Segment Registry

Per-segment instance data for the engine in `AMZ_PRICING.md`. The engine and the full-review procedure are brand-neutral; **this file is where the numbers and the segment-specific knowledge live.** When a rule needs a floor, a ceiling, or a step band, read it from here.

> **Economics below are per-segment averages** pulled 2026-06-19. They're good enough to set floors and frame a decision — but before a *final* price on a specific groupid, check that groupid's exact `cost`/`rrp` in `skusummary` and its `fbafee` in `amzfeed` (styles within a segment vary, especially Rieker).
>
> **State notes are short by design** — a resume pointer, not a session diary. The full rationale for every change is in `amz_price_log.notes`. Reset a state line when it's stale; don't append a log.

## Quick parameters

`hard floor` = cost + FBA fee (breakeven before margin) — **never price below it.** `working floor` = the lowest price we actually use (tidy-number convention or a proven clear price). `ceiling` = a *discovered* resistance price a creep shouldn't cross without prior sales above it; "—" = none found yet, RRP is the only cap.

| Segment | `segment` value(s) | ~Cost | ~FBA | RRP | Hard floor | Working floor | Ceiling | Step band |
|---|---|--:|--:|--:|--:|--:|--:|--|
| IVES-WHITE | `IVES-WHITE` | 15.99 | 3.06 | 45.00 | ~19.05 | 35.99 (soft) | **40.00** | 38.50–39.00 |
| IVES-COLOUR | `IVES-COLOUR` | 15.99 | 3.06 | 45.00 | ~19.05 | 35.99 (soft) | **40.00** | 38.50–39.00 |
| LUNAR-GENERAL | `LUNAR-GENERAL` | 13.21 | 3.01 | 39.70 | ~16.22 | — | — | discover |
| BLAZE-SEG | `BLAZE-SEG` | 12.99 | 3.09 | 39.00 | ~16.08 | — | — | discover |
| LAKE-SEG | `LAKE-SEG` | 17.50 | 3.90 | 45.00 | ~21.40 | — | — | discover |
| RIEKER-SUM | `RIEKER-SUM` | 28.12 | 3.21 | 65.38 | ~31.33 | — | — | discover |
| RIEKER-WIN | `RIEKER-WIN` | 30.71 | 3.27 | 71.63 | ~33.98 | — | — | discover |
| UKD-SEG | `UKD-SEG` | 15–23 | 3.2–3.4 | 39–60 | per style | per style | per style | discover |
| FREE-SPIRIT | `FREE-SPIRIT` | 21.52 | 3.21 | 59.99 | ~24.73 | — | — | discover |
| STRIVE-SEG | `STRIVE-SEG` | 34.59 | 3.31 | 81.43 | ~37.90 | — | — | discover |
| SKECHERS-SEG | `SKECHERS-SEG` | 35.84 | 3.34 | 75.54 | ~39.18 | — | — | discover |
| REMONTE-WIN | `REMONTE-WIN` | 34.63 | 3.27 | 81.00 | ~37.90 | — | — | discover |

For most non-IVES segments the ceiling/step band are not yet discovered — that's expected. Creep up from strength and the first sustained stall *is* the ceiling; record it here when found.

---

## IVES (Lunar — `FLE030-IVES-*`) — Priority 1, the core

The most-developed segment; ~3 months of dense pricing history. Two sub-segments reviewed as the IVES pair.

**Shared economics:** cost £15.99, FBA ~£3.06, RRP £45.00. Hard floor ~£19.05; the **£35.99 working floor is a soft convention, not economic** — profit is still ~£12/unit at £33.99, so clear genuinely dead piles below it. **£40.00 is a confirmed velocity ceiling** (the £40.09 push on WHITE-05 collapsed velocity, June; don't retest soon after a failure).

| GroupID | Colour | Sub-segment |
|---|---|---|
| FLE030-IVES-WHITE | White | IVES-WHITE |
| FLE030-IVES-BEIGE / -STONE | Beige / Beige | IVES-COLOUR |
| FLE030-IVES-BLACK / -BLACKSOLE | Black / all-black-sole | IVES-COLOUR |
| FLE030-IVES-GREY | Grey | IVES-COLOUR |
| FLE030-IVES-MIDBLUE / -NAVY-BLUE | Blue / Navy | IVES-COLOUR |
| FLE030-IVES-KHAKI | Green | IVES-COLOUR |
| FLE030-IVES-RED | Red | IVES-COLOUR |

**Durable observations**
- **WHITE is the engine** — May 25 wk was a record (132u / £1,960 profit). Demand is rarely the constraint; the gate is the price-held signal per size.
- **BLACK = harvest-and-exit** (decided 2026-05-29). Velocity collapsed, deep FBA pile, no reorders — manage clear depth only, don't reopen size-by-size.
- **WHITE-04 returns are a fit/product issue, not price** — sells fine at price with ~37% returns/14d; don't creep into the returns, watch whether they ease.
- **BEIGE-05 supplier-constrained harvest** — we hold this size early (less competition) → real pricing power, crept above £40 in late May; harvest while it sells, pull straight back if it stalls.
- **WHITE-05 £39.49 lesson** — a prior failure at that price coincided with a stockout; retest suspect prices once stock normalises (the OOS-check rule).

**Current state (as of 2026-06-11 — refresh on next review)**
- WHITE: 05 settling @39.69 (pulled back from failed £40.09); 06 @39.59, 07 @39.70, 09 @39.20 crept; 08 cold @38.49 (next move a real drop ~37.99 if still dead); 03 hold @39.29; 04 returns-watch @39.29.
- COLOUR: NAVY / BEIGE / BLACKSOLE leading; £40 held as ceiling on NAVY-06 (39.79) & BEIGE-06 (39.80) on purpose; BLACK exit pile @31.99 (~105u, ~8/wk; £29.99 next if you want it gone); MIDBLUE soft; tails (RED/STONE/KHAKI) on low-floor clears.

---

## RIEKER (Rieker) — developing, restock in progress

Actively restocked and prepared per season — **managed, not delegated.** Summer (`RIEKER-SUM`) and Winter (`RIEKER-WIN`) are separate segments; winter is out of season now and mostly OOS on FBA.

**Economics:** higher cost/RRP than IVES and varies a lot by style — **always check the specific groupid.** SUM avg cost £28.12 / RRP £65.38 / hard floor ~£31.33; WIN avg cost £30.71 / RRP £71.63 / hard floor ~£33.98.

**Durable observations**
- **WHITE punches above its colourway here** — 64870 colour **81 (WHITE)** sells at/near full RRP while sister colour 14 is weaker (see WHITE note below). Weight WHITE when judging which Rieker colours to keep/push.
- Pricing leverage only exists where there's **live FBA stock** — much of the Rieker catalogue is OOS, so "neglect" here is often a replenishment gap, not a pricing one. Flag the stock side, price what's stocked.

**Current state (RIEKER-SUM, as of 2026-06-19 — entry point for the restart)**
Actionable (stock + velocity): **65918-90** (Elasticated Sandal, best-stocked + selling), **64870-14** (Touch-Close, top seller), **46778-64** (Slingback Heeled, best 90d seller but thin FBA), **M1655-54** (Hook & Loop, has stock but stalled ~3wk — price test candidate). Thin/scarce: 64870-81 (WHITE, low FBA), 659C7-16/-24, M1655-14. No tested ceiling yet — creep the live sellers from strength to discover it.

---

## UKD-SEG (Mod Comfys / Goor / Roamers) — Amazon-only, watch

Mixed-brand segment. Economics vary by brand — Mod Comfys ~£15.45 cost / £38.95 RRP, Goor ~£15.79 / £40.00, Roamers ~£22.95 / £60.00.

**L662 Mod Comfys (Softie Leather; colours E=Pistachio, G=White, NC=Navy; sizes 3–8) — RRP £38.95, cost £15.45.**
- **Proven price £31.95 is a valid terminal state** — the user explicitly wants volume + low-effort fulfilment over fatter margin (easy £1+/unit at steady velocity beats £2.74/unit at ~zero). **Default: stay at £31.95, do NOT auto-creep.**
- **£33.95 has been tested and FAILED** (concluded 18 May 2026): 1 sale + 2 returns in 17 days with 18 units in stock → stockout ruled out, clean elasticity signal; the +6–9% push killed velocity. Don't retest without reason.
- A single small creep (£32.49) from strength stays an *optional* lever if the user later wants margin and accepts velocity risk — never ladder down, never creep by reflex.
- Competitors at £29.99 are **FBM**; we're FBA/Prime — different buyer, do **not** match down.

**M968BC Mod Comfys — FBA-flywheel does NOT transfer.** On FBA with continuous stock it produced only ~2 Amazon sales over 9 weeks (Mar–early May 2026). The IVES steady-trickle is product-specific (search demand / listing strength / price band / brand pull), not a generic property of being on FBA. Don't lean on the IVES analogy when judging restock/expansion for UKD-SEG (or any new line) — each product must prove its own velocity; sustained stock alone isn't enough.

---

## Other Lunar segments — active / developing

- **LUNAR-GENERAL** (`JLH*` etc.) — active; ~90 logged changes. Cost ~£13.21 / RRP ~£39.70 / hard floor ~£16.22. No tested ceiling recorded; manage per the engine.
- **BLAZE-SEG** — cost ~£12.99 / RRP ~£39.00 / hard floor ~£16.08.
- **LAKE-SEG** — cost ~£17.50 / RRP ~£45.00 / hard floor ~£21.40; developing.

No durable per-style notes yet — add them here as state accrues.

---

## Light-cadence segments

A quick performance check on a longer cycle. Managed, not ignored — promote to a fuller section once one earns regular attention.

- **FREE-SPIRIT** (Free Spirit) — cost ~£21.52 / RRP ~£59.99 / hard floor ~£24.73.
- **STRIVE-SEG** (Strive) — cost ~£34.59 / RRP ~£81.43 / hard floor ~£37.90. Thin margins — watch the floor.
- **SKECHERS-SEG** (Skechers) — cost ~£35.84 / RRP ~£75.54 / hard floor ~£39.18. Very thin headroom above floor.
- **REMONTE-WIN** (Remonte) — cost ~£34.63 / RRP ~£81.00 / hard floor ~£37.90; seasonal (winter).

---

## Cross-cutting: WHITE is a strong colour

WHITE consistently outsells other colourways across brands/styles on Amazon — IVES-WHITE is the top AMZ seller; Rieker 64870-81 (WHITE) sells at full RRP while sister colours lag; L662 colour G is White. **Weight WHITE favourably** when deciding which colours to push, keep, or reorder into a segment — it carries a positive prior. Still check the specific line's economics; the prior informs, it doesn't decide.
