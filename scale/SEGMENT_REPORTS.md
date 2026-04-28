# Segment Reports — Manager View

A reference for the data report shape per segment. Tell Claude **"give me the [SEGMENT] report"** and this is what to produce.

This doc covers **manager reports only** — the one-screen check that answers "are we on track, push or wait?" Segment owners (Summer etc.) manage their own deep analysis; that's their work, not what shows up here.

## Principles

- **One question this report answers:** Are we on track, and do I push or wait?
- **Default scan time: under 60 seconds.** Read the status flag first, the grid second, the note last.
- **Default comparison is YoY same-window.** Last 14 days vs same 14 days last year — kills seasonality, exposes real change.
- **Two windows:** 30 days for the broader view, 14 days to catch recent inflections. The contrast between them is often the story.
- **No per-colour, per-size, per-listing drill.** That's owner-level analysis. If the manager report flags ATTENTION, drill on request — not by default.
- **No stock dashboard.** Tracked separately. Don't repeat data that lives elsewhere.
- **Listings tracked indirectly.** If units hold YoY, listings are healthy. No separate listing column — units are the proxy. Listing problems surface as ATTENTION via collapsing units.
- **Price tracked actively.** Price-trend line shows whether Summer is pushing within the recent window. This is operational work the manager wants visibility on without re-doing it.

---

## Default template

Used for any segment that has at least 12 months of history and is in season.

### Format

| Window | Units | Units/day | Avg price | Revenue | YoY units | YoY rev | YoY avg price |
|---|---:|---:|---:|---:|---:|---:|---:|
| Last 30 days | … | … | … | … | … | … | … |
| Last 14 days | … | … | … | … | … | … | … |

The **Units/day** column makes the two windows directly comparable — a higher 14-day rate vs the 30-day rate means recent acceleration; a lower one means cooling.

**2026 pace:** rate × season-days = £X vs £target → on/ahead/behind. Use the season-length appropriate to the segment family (see table below). Don't naively annualise — peak segments overstate dramatically when projected across 12 months.

**Price trend (14d vs 30d):** climbing / holding / slipping (+/-£X) — visibility on whether active price work is happening within the recent window

**Status:** [PUSH / ON TRACK / WAIT / ATTENTION] — one-line reason

**Owner note (optional):** one line if there's something to flag. Skip if nothing.

---

## Status flag — how it's derived

Four states. The flag is a one-word answer to "what should I do?"

- **PUSH** — units up YoY *and* pace well above target.
  *Lean into momentum. More stock if available, more aggressive price, more attention. Defend the gains.*
- **ON TRACK** — units flat-to-up *and* pace at target.
  *Routine. No action needed. Most weeks land here.*
- **WAIT** — pace at target but underlying signal soft (e.g. price compressed, units flat-to-down despite favourable season).
  *Hold steady. Don't change strategy yet, but watch next 2 weeks.*
- **ATTENTION** — pace meaningfully behind target, or units down YoY by >15%.
  *This is the conversation trigger. Owner explains what they're seeing and what they're doing about it.*

A flag of ON TRACK or WAIT means no meeting time needed. Save discussion for PUSH (decisions about scale-up) and ATTENTION (problem solving).

---

## Owner notes

Not a forced field. The note exists for two reasons only:
1. **Explain a deliberate move** ("Pushed Brown to £71 last Tuesday")
2. **Flag something the data alone can't show** ("Amazon listing for Navy-Blue dropped from page 1 to page 2")

Routine weeks → blank note. Silence is a healthy signal.

If a segment has been ATTENTION for 2+ weeks, expect a note. Otherwise no expectation.

---

## Pace projection per segment family

| Family | Selling window | Days | Pace formula |
|---|---|---|---|
| Lunar (IVES, BLAZE) | Year-round, summer-leaning | 365 | rate × 365 |
| Birkenstock (Arizona, Bend, Milano, Gizeh, Eva, Mayari) | Mar–Jul peak | 150 | rate × 150 ≈ annual revenue |
| Zermatt cork | Mar–Jun peak | 150 | rate × 150 |
| Zermatt shearling | Jul–Feb peak | 210 | rate × 210 |
| Rieker / Remonte Winter | Oct–Feb | 150 | rate × 150 |
| Rieker Summer | Mar–Sep | 210 | rate × 210 |
| Lake (winter slipper) | Sep–Feb | 180 | rate × 180 |
| UKD | Year-round | 365 | rate × 365 |

For peak segments, the off-season contributes near-zero, so the peak-season projection ≈ annual revenue. Annualising to 365 days for these segments produces inflated false-positives (a strong April rate looks like a year of strong months — it isn't).

## Segment-specific exceptions

Most segments use the default template. A few don't fit and get a slightly different shape:

- **RIEKER-SUM** — no comparable history (didn't sell last year). Compare against current 12m baseline only, not YoY.
- **RIEKER-WIN, REMONTE-WIN** — off-season Apr–Aug. Skip until stock arrives in August. Reports resume in autumn.
- **BLAZE-SEG** — demand-recovery segment. Add buy box / listing visibility commentary in the owner note when relevant. Manager view stays simple: are units recovering or not?
- **FREE-SPIRIT** — investigation segment, very small numbers. Use absolute numbers not YoY (no history). Promote-or-cull check at 90 days.

---

## Segments using the default template

All except those listed above:
- IVES-WHITE, IVES-COLOUR
- ARIZONA-BF-REG, ARIZONA-BF-NAR, ARIZONA-PATENT-SEG
- BEND-SEG, MILANO-SEG, GIZEH-SEG, EVA-SEG, ZERMATT-SEG, MAYARI-SEG
- LAKE-SEG, UKD-SEG

---

## Drill-downs (on request only)

If the manager report flags **PUSH** or **ATTENTION**, the next layer of analysis is owner-level work. Available on request:
- Per-colour / per-style breakdown
- Price headroom analysis
- Stock days of cover
- Listing health (Amazon segments)

These are **not** in the default report. Ask for them when needed.
