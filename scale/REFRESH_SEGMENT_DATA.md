# Refresh segment data (Segments sheet)

Trigger: *"check scale folder and recalculate segment data"* (or similar).

## Do this

```
python scale/refresh_segment_data.py
```

**One run updates every segment. Do not loop — the script handles all segments itself.**
Reading the result and relaying the one-line summary is all that's needed.

To preview without writing anything:

```
python scale/refresh_segment_data.py --dry-run
```

## What it does

- Reads the segment list **from the 'Segments' tab itself** (column `SEGMENT CODE`).
  Segment names are **not** in the script — never hardcode or maintain a list.
- For each segment, recomputes from the database over the **trailing 365 days**:
  | Column | Formula |
  |---|---|
  | `STYLES` | count of groupids in `skusummary` for that segment |
  | `REVENUE (12m)` | `SUM(qty * soldprice)` |
  | `GP (12m)` | `SUM(qty * (soldprice − cost))` |
  | `GP %` | `GP / REVENUE` |
- Writes those four columns back, located **by header name** (resilient to column moves).

## Guardrails (already built in)

- **Never touches** `SEGMENT NAME`, `OWNER`, `REVIEWED`, or the `HUMAN NOTES` column.
- A sheet code with **no matching DB segment** is left exactly as-is and named in a WARNING line.
- If a required header is missing, it **aborts** and prints the header row (fix the sheet, don't guess).

## Notes

- This is a **data refresh only** — it does **not** re-sort rows by revenue. If the tracker
  needs re-ranking afterwards, that's a separate step (ask).
- `REVIEWED` is the human's "when I last looked at this segment" log, not a data-freshness
  stamp — that's why the refresh leaves it alone.
- Method matches how the sheet's figures were originally computed (verified against
  Leather/Ives). GP is **gross** (`soldprice − cost`), no fee deduction.
