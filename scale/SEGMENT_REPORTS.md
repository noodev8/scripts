# Segment Reports — Manager View

A reference for the data report shape per segment. Three named reports per segment — ask for them by name:

- **"[SEGMENT] Summary"** → manager report (this section's default template)
- **"[SEGMENT] SKU progress report"** → per-SKU drill (see Drill-downs)
- **"[SEGMENT] Daily detail"** → 30-day day-by-day with avg price, running stock and 7d avg (see Drill-downs)

Run only what's asked. Don't bundle them.

This doc covers **manager reports only** — the one-screen check that surfaces what's happening. Decisions (push, wait, intervene) are made in conversation between the user and Claude after reviewing the report. Segment owners (Summer etc.) manage their own deep analysis; that's their work, not what shows up here.

## Principles

- **What this report does:** surfaces the data. It does not draw a conclusion.
- **Default scan time: under 60 seconds.** Read the grid, then the price-trend line, then the note.
- **Default comparison is YoY same-window.** Last 14 days vs same 14 days last year — kills seasonality, exposes real change.
- **Two windows:** 30 days for the broader view, 14 days to catch recent inflections. The contrast between them is often the story.
- **No per-colour, per-size, per-listing drill.** That's owner-level analysis. Drill on request — not by default.
- **No stock dashboard.** Tracked separately. Don't repeat data that lives elsewhere.
- **Listings tracked indirectly.** If units hold YoY, listings are healthy. No separate listing column — units are the proxy.
- **Price tracked actively.** Price-trend line shows whether the owner is pushing within the recent window. This is operational work the manager wants visibility on without re-doing it.

---

## Default template

Used for any segment that has at least 12 months of history and is in season.

### Format

| Window | Units | Units/day | Avg price | Revenue | YoY units | YoY rev |
|---|---:|---:|---:|---:|---:|---:|
| Last 30 days | … | … | … | … | … | … |
| Last 14 days | … | … | … | … | … | … |

The **Units/day** column makes the two windows directly comparable — a higher 14-day rate vs the 30-day rate means recent acceleration; a lower one means cooling.

### What goes below the table

**The table is the report.** Below it, print at most one line: a drill offer if the segment's own folder (`scale/<slug>/`) defines a drill. Otherwise nothing.

Example: `If you want to drill, the next step for EVA-SEG is the stock-availability triage.`

### What does NOT go below the table

- **No pace projection, price-trend line, or shape line.** All derivable from the table — restating is noise.
- **No interpretive paragraph.** Do not write "the 14d is worse than the 30d", "cooling not recovering", "YoY is in -70% territory", etc.
- **No decisions or recommendations.** Push / hold / intervene calls come out of conversation, not the report.
- **No comparisons not already in the report** (e.g. last year's avg price, competitor prices, Google reco).
- **No recent owner note.** Available on request as a drill — do not pre-load it. If you think the note is critical to interpretation, you are wrong: the manager reads the table, decides whether to dig, then asks for whatever they need.

### Drill options

These are available on request after the Summary — do not pre-run them:

- **Recent owner notes** — last 3 from `segment_notes` for this segment.
- **Pace / price-trend / shape** — the lines that used to sit under the table, on request.
- **Segment-specific drill** — defined in the segment's own folder `scale/<slug>/<SEGMENT>.md` if one exists.
- **Standard per-SKU view** — from the Drill-downs section below.

This report will be read by managers reviewing staff progress — staff own the interpretation, the report is just the data.

### What the user is looking for in this report

When the Summary is on screen, the user is scanning for:

- **Are units up YoY?** Both windows. The 30d gives the broader read, the 14d catches recent inflections.
- **Is the 14d rate above or below the 30d rate?** Acceleration vs cooling — the most important single signal.
- **Is current avg price holding within the recent window?** (Price-trend line.)
- **Anything in the recent notes that changes interpretation?**

That's it. Don't pull comparisons that aren't in the report (e.g. last year's avg price). If the user wants something extra, they'll ask — and we'll add it as a column or a separate report rather than smuggling it into commentary.

---

## Owner notes

Not a forced field. The note exists for two reasons only:
1. **Explain a deliberate move** ("Pushed Brown to £71 last Tuesday")
2. **Flag something the data alone can't show** ("Amazon listing for Navy-Blue dropped from page 1 to page 2")

Routine weeks → blank note. Silence is a healthy signal.

If a segment has been weak for 2+ weeks, expect a note. Otherwise no expectation.

### Where notes live

Notes are stored in the `segment_notes` table:

| Column | Type | Purpose |
|---|---|---|
| `id` | serial PK | |
| `segment` | text | Matches `skusummary.segment` code (e.g. `IVES-WHITE`) |
| `note_date` | date | Date the note *applies to* (e.g. the day a price was pushed). Defaults to today. |
| `author` | text | Optional — who wrote it |
| `note` | text | Free text |
| `created_at` | timestamp | When the row was inserted |

When the user asks to log a note ("note for IVES-WHITE: …"), insert a row. When running a Summary report, pull the most recent ~3 notes for that segment and surface them alongside the report so context isn't lost between sessions.

```sql
SELECT note_date, author, note
FROM segment_notes
WHERE segment = 'IVES-WHITE'
ORDER BY note_date DESC, created_at DESC
LIMIT 3;
```

---

## Pace projection per segment family

| Family | Selling window | Days | Pace formula |
|---|---|---|---|
| Lunar (IVES, BLAZE) | Year-round, summer-leaning | 365 | rate × 365 |
| Birkenstock (Arizona, Bend, Milano, Gizeh, Eva, Mayari) | Mar–Jul peak | 150 | rate × 150 ≈ annual revenue |
| Zermatt (cork + shearling) | Year-round | 365 | rate × 365 |
| Rieker / Remonte Winter | Oct–Feb | 150 | rate × 150 |
| Rieker Summer | Mar–Sep | 210 | rate × 210 |
| Lake (winter slipper) | Sep–Feb | 180 | rate × 180 |
| UKD | Year-round | 365 | rate × 365 |

For peak segments, the off-season contributes near-zero, so the peak-season projection ≈ annual revenue. Annualising to 365 days for these segments produces inflated false-positives (a strong April rate looks like a year of strong months — it isn't).

## Segment-specific rules

A segment either uses the defaults in this doc, **or** it has its own self-contained folder. There is no middle tier.

- **Default segments:** no folder. They follow this doc entirely.
- **Override segments:** one flat folder per segment at `scale/<slug>/`, containing its `<SEGMENT>.md` (rules) plus any scripts it uses. **Each folder is self-contained — its scripts are its own copies, even where similar to another segment's.** Edit a segment's script freely; the blast radius is that one segment. The trade-off (accepted deliberately): fixes don't propagate — we fix the segment we're working on, and if a structural fix is ever needed it's a manual sweep across folders, never an assumed ripple. Scripts in other folders are a *library to crib from*, not shared dependencies — look in them, copy what's useful.

**Always check for `scale/<slug>/<SEGMENT>.md` before running a report.** If it exists, follow it; the defaults apply for anything it doesn't override.

Current override folders:
- `eva/` — Birkenstock EVA. Summary first; drill via stock-availability triage (`eva/stock_triage.py`) + `eva/google_compare.py`.
- `mayari/` — Birkenstock Mayari. Same two-step flow (`mayari/stock_triage.py`).
- `arizona-patent/` — Birkenstock Patent Arizona. Same two-step flow (`arizona-patent/stock_triage.py`).
- `arizona-black/`, `arizona-blue/`, `arizona-brown/`, `arizona-white/`, `arizona-taupe/` — Arizona Birko-Flor colour bricks (Reg+Nar pairs, May 2026). Drill = per-EU-size availability (`size_availability.py`) with the **Inv** (releasable) / **Wsh** (future) stock split.
- `arizona-general/` — Arizona monitor bucket. Drill = shade breakdown (`shade_breakdown.py`); shade-pairs ranked by demand, promote on judgment (no fixed revenue bar).
- `madrid/` — Birkenstock Madrid. Style-level triage (`madrid/stock_triage.py`).
- `milano/` — Birkenstock Milano (4-code brick: Brown + Black, each Reg/Nar). Two-drill chain: `size_availability.py` (one flat row per style/width) → `size_breakdown.py` (size-as-columns, cell = `u30(stk)`). **⭐ Preferred / latest report shape for Birkenstock** — short-named chain (Summary → drill 1 → drill 2) plus a single overwrite-only `## Status` block. Use as the reference when reworking other Birk segments; don't bulk-retrofit, adopt per-segment as each is revisited.
- `zermatt/` — Birkenstock Zermatt (cork + shearling). Triage with material column (`zermatt/stock_triage.py`).
- `ives-colour/` — multi-colour Amazon Ives. SKU report rolls up by colour (SQL inline in the md).
- `blaze/` — Amazon Blaze, demand-recovery. Amazon-flavoured stock triage (`blaze/stock_triage.py`).
- `rieker-sum/` — no YoY (no history); 12m baseline only.
- `rieker-win/`, `remonte-win/` — off-season Apr–Aug; reports resume in autumn.
- `free-spirit/` — investigation segment; absolute numbers, promote-or-cull at 90 days.

---

## Segments using the default template

Every segment NOT in the override-folder list above, i.e.:
- IVES-WHITE
- ARIZONA-LEATHER
- BEND-SEG, GIZEH-SEG, BIRK-OTHER
- LUNAR-GENERAL, LAKE-SEG, BLOCH-SEG, SKECHERS-SEG, STRIVE-SEG, UKD-SEG, ACCESSORY

---

## Drill-downs (on request only)

### Per-SKU view (standard drill from any segment)

The first drill from the manager report. Lists every SKU in the segment with current stock and recent units.

| Code | Stock | Units 14d | Units 30d |
|---|---:|---:|---:|

- **Code** comes from `skumap.code` (groupid is implicit in the code prefix, so no separate column).
- **Stock** source depends on the segment's channel:
  - **Amazon segments** (IVES, BLAZE, Rieker, Remonte) → `amzfeed.amzlive` joined on code. This is the live FBA figure that actually drives sales.
  - **Shopify segments** (Birkenstock family, etc.) → `localstock` where `ordernum='#FREE' AND deleted=0`, summed per code.
- **Units 14d / 30d** = `sales` where `qty>0 AND soldprice>0`, summed per code over the same windows as the manager report.
- Order rows by code (which sorts naturally by groupid then size).
- For multi-groupid segments, all groupids appear in one table — code prefix tells you which.

### Daily detail (30-day day-by-day)

Day-by-day view of the segment for the last 30 days. Shows whether momentum is building, where restocks landed, and how the stock position has flowed.

| Date | Units | Revenue | Avg | Incoming | 7d avg | Running |
|---|---:|---:|---:|---:|---:|---:|

- **Units / Revenue** — `sales` where `qty>0 AND soldprice>0`, grouped by `solddate::date` for the segment's groupids.
- **Avg** — `revenue / units` per day. Useful to the segment owner who is also responsible for pricing — shows whether the price they've set is holding up alongside volume. Ignore avg on low-unit days (1-3 units = noise).
- **Incoming** — `incoming_stock.quantity_added` summed by `arrival_date` for the segment's groupids. Don't filter by `target` or `workstation` — we want the broad in/out picture.
- **7d avg** — trailing 7-day average of units (current row + 6 preceding). First few rows use whatever days are available.
- **Running** — starts at 0 on day 1, then `previous + incoming - units` each day. Returns and pre-window stock are deliberately ignored — early-window negative values are expected and fine. This is a sell-through indicator, not a true stock count.
- Add a totals row at the bottom for Units, Revenue, Incoming.

```sql
WITH days AS (
  SELECT generate_series(<start>, <end>, INTERVAL '1 day')::date AS d
),
sold AS (
  SELECT solddate::date AS d, SUM(qty)::int AS units,
         ROUND(SUM(qty*soldprice)::numeric,2) AS revenue
  FROM sales
  WHERE groupid = ANY(<groupids>) AND qty>0 AND soldprice>0
    AND solddate::date BETWEEN <start> AND <end>
  GROUP BY 1
),
inc AS (
  SELECT arrival_date AS d, SUM(quantity_added)::int AS qty
  FROM incoming_stock
  WHERE groupid = ANY(<groupids>)
    AND arrival_date BETWEEN <start> AND <end>
  GROUP BY arrival_date
),
joined AS (
  SELECT d.d, COALESCE(s.units,0) AS units,
         COALESCE(s.revenue,0) AS revenue,
         COALESCE(i.qty,0) AS incoming
  FROM days d LEFT JOIN sold s ON s.d=d.d LEFT JOIN inc i ON i.d=d.d
)
SELECT d, units, revenue,
       CASE WHEN units > 0 THEN ROUND((revenue/units)::numeric,2) END AS avg_price,
       incoming,
       ROUND(AVG(units) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)::numeric,1) AS roll7,
       SUM(incoming - units) OVER (ORDER BY d ROWS UNBOUNDED PRECEDING) AS running
FROM joined ORDER BY d;
```

Note: `solddate` can bucket awkwardly across UTC midnight — combine any duplicate same-UK-day rows when displaying.

### Other drills (on request)

If a segment warrants a deeper look after reviewing the report, owner-level analysis is available on request:
- Per-colour / per-style breakdown
- Price headroom analysis
- Stock days of cover
- Listing health (Amazon segments)
