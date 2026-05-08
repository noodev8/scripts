# Refresh Pillars — Operating Procedure

Read this BEFORE doing any work on the `Pillar 2026` tab in the segment tracker sheet.

**The sheet itself is the source of truth for the current pillar list, row positions, and DB filters.** Read the tab first to see what pillars exist today and where they live — do not rely on a list in this doc.

## Critical constraints

- **DO NOT change colours, fonts, borders, or any formatting.** The user has redesigned the tab's visual style and you must not overwrite it.
- Only update cell **values**.
- **NEVER call** `ws.format()`, `ws.batch_clear()`, `ws.clear()`, or delete-and-rewrite the tab.
- `ws.update(values=..., range_name=...)` is safe — it only writes values, leaves formatting alone.
- Structural changes (year rollover, adding/removing pillars) are **collaborative**. Present a plan, get explicit approval, then execute.

## Sheet location

- Sheet ID: `1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0`
- Active tab: `Pillar 2026`
- Backup tab (do not touch): `Pillar` — old trailing-12-month view, kept as reference
- Credentials: `merchant-feed-api-462809-23c712978791.json` (repo root)
- See `scale/CLAUDE_CONTEXT.md` for the standard gspread access pattern.

## Tab layout (general)

Paired rows per pillar — current year on top, prior year directly below (italic). A `Coverage` pair sums all pillars. A blank row separates the heatmap. The `% of {prior year}` row sits at the bottom.

Read the tab to confirm exact row positions before writing — they shift when pillars are added or removed.

| Col | Content |
|---|---|
| A | Pillar name (curr rows only) |
| B | Product |
| C | Channel |
| D-O | Jan-Dec monthly revenue |
| P | YTD (Jan through last completed month) |
| Q | FY prior total (prior rows only) |
| R | YTD YoY % (curr rows only) |

## Pillar filters

The exact DB filter for each pillar lives implicitly in the sheet (Pillar name + Channel columns). Confirm the filter with the user when refreshing — pillars get re-scoped (e.g. all-channels → Amazon-only) and a list in this doc would go stale.

## Monthly refresh — run at end of each month

1. Identify the just-completed month (e.g., end of May → May is the new completed month).
2. Read the tab to identify the active pillars and their row positions.
3. Pull each pillar's revenue for the just-completed month from the `sales` table.
4. Write the just-completed month's value into each pillar's curr row and the Coverage curr row.
5. Recalculate YTD = sum of Jan through just-completed month for each curr row + Coverage. Write to column P.
6. Recalculate YTD YoY = (curr YTD / prior YTD same window) - 1. Write to column R.
   - Where prior YTD < ~£500 or = 0, write `—` instead (avoid meaningless huge percentages).
7. If a new month has begun (e.g., now in June), pull MTD for the new in-progress month and write to its column on curr rows.

The user handles re-applying the yellow "in progress" highlight when MTD shifts to a new month — do not touch formatting.

## "Update current month" — interim MTD refresh

User may ask mid-month, "update the current month."

1. Identify the in-progress month (today's month).
2. Pull MTD revenue (1st of current month → today, inclusive) for each pillar.
3. Write the MTD value into the in-progress month's column on each curr row + Coverage row.
4. **Do not** include the partial MTD in YTD or YoY — those remain through the last completed month.

## Year-end rollover (Dec → Jan)

Collaborative — present full plan, get approval, then execute.

1. **Snapshot first.** Duplicate the active tab as `Pillar {year} (closed)` so the closed year is frozen.
2. **Rotate data.** On the active tab (renamed to next year):
   - Current curr rows (closed-year actuals) become new prior rows.
   - New curr rows start blank.
   - YTD column resets to 0; YoY column resets to blank.
3. **Re-base heatmap.** Change `% of {prev year}` row label and values to `% of {just-closed year}` — use the just-closed year as the new seasonal template.
4. **Rename tab** to the new year.

## Adding / removing / re-scoping pillars

Structural change. Present plan first, do not auto-execute.

- **Adding** (e.g. promoting a probe from the `Experiments` tab): insert a new curr/prior pair in sort position; pull prior-year actuals for the new filter; recalculate Coverage.
- **Removing**: delete rows entirely, or move to a "Retired" section. Recalculate Coverage.
- **Re-scoping** (e.g. switching a pillar from all-channels to Amazon-only): re-pull both curr-year and prior-year monthly numbers under the new filter; update Channel cell; recalculate Coverage and the `% of {prior year}` heatmap.

## Reference — query and write skeletons

Query template (single month for one pillar):

```python
cur.execute("""
    SELECT SUM(soldprice * qty)
    FROM sales
    WHERE solddate >= %s AND solddate < %s
      AND brand = 'Birkenstock' AND channel = 'SHP'
""", (month_start, month_end))
```

Safe write (values only, no formatting):

```python
ws.update(values=[[value]], range_name='H2')   # one cell
ws.update(values=[[v1, v2, v3]], range_name='D2:F2')   # row segment
```

When writing YTD YoY, use `raw=True` (or `value_input_option='RAW'`) for string values like `+25%` — `USER_ENTERED` parses the `%` and stores `0.25`.

Never use `ws.format`, `ws.clear`, or `batch_clear` on this tab.
