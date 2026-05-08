# Refresh Pillars — Operating Procedure

Read this BEFORE doing any work on the `Pillar 2026` tab in the segment tracker sheet.

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

## Tab structure

Paired rows per pillar — current year on top, prior year directly below (italic).

| Row | Content |
|---|---|
| 1 | Headers |
| 2-3 | Birk-SHP (curr / prior) |
| 4-5 | IVES-AMZ |
| 6-7 | Rieker-AMZ |
| 8-9 | IVES-SHP |
| 10-11 | REMONTE-AMZ |
| 12-13 | Coverage (curr / prior) |
| 14 | Blank |
| 15 | `% of {prior year}` heatmap row |

| Col | Content |
|---|---|
| A | Pillar name (curr rows only) |
| B | Product / "Prior Yr" |
| C | Channel |
| D-O | Jan-Dec monthly revenue |
| P | YTD (Jan through last completed month) |
| Q | FY Prior total (prior rows only) |
| R | YTD YoY % (curr rows only) |

## Pillar definitions (DB filters)

These must match exactly when querying:

| Pillar | Filter |
|---|---|
| Birk-SHP | `brand='Birkenstock' AND channel='SHP'` |
| IVES-AMZ | `(UPPER(productname) LIKE '%IVES%' OR UPPER(groupid) LIKE '%IVES%') AND channel='AMZ'` |
| IVES-SHP | `(UPPER(productname) LIKE '%IVES%' OR UPPER(groupid) LIKE '%IVES%') AND channel='SHP'` |
| Rieker-AMZ | `brand='Rieker' AND channel='AMZ'` |
| REMONTE-AMZ | `brand='Remonte' AND channel='AMZ'` |

## Monthly refresh — run at end of each month

1. Identify the just-completed month (e.g., end of May → May is the new completed month).
2. Pull all 5 pillars' revenue for the just-completed month from the `sales` table.
3. Write the just-completed month's value into the curr row for each pillar (rows 2, 4, 6, 8, 10) and Coverage (row 12).
4. Recalculate YTD = sum of Jan through just-completed month for each curr row + Coverage. Write to column P.
5. Recalculate YTD YoY = (curr YTD / prior YTD same window) - 1. Write to column R.
   - Where prior YTD < ~£500 or = 0, write `—` instead (avoid meaningless huge percentages).
6. If a new month has begun (e.g., now in June), pull MTD for the new in-progress month and write to its column on curr rows.

The user handles re-applying the yellow "in progress" highlight when MTD shifts to a new month — do not touch formatting.

## "Update current month" — interim MTD refresh

User may ask mid-month, "update the current month."

1. Identify the in-progress month (today's month).
2. Pull MTD revenue (1st of current month → today, inclusive) for each pillar.
3. Write the MTD value into the in-progress month's column on each curr row + Coverage row.
4. **Do not** include the partial MTD in YTD or YoY — those remain through the last completed month.

## Year-end rollover (Dec 2026 → Jan 2027)

Collaborative — present full plan, get approval, then execute.

1. **Snapshot first.** Duplicate `Pillar 2026` as `Pillar 2026 (closed)` so the closed year is frozen.
2. **Rotate data.** On `Pillar 2026` (which becomes `Pillar 2027`):
   - Current curr rows (2026 actuals) become new prior rows.
   - New curr rows start blank for 2027.
   - YTD column resets to 0; YoY column resets to blank.
3. **Re-base heatmap.** Change `% of 2025` row label and values to `% of 2026` — use the just-closed year as the new seasonal template.
4. **Rename tab** from `Pillar 2026` to `Pillar 2027`.

## Adding / removing / promoting pillars

Structural change. Present plan first, do not auto-execute.

Promoting a probe from the `Experiments` tab:
- Insert new pair of rows (curr + prior) in the appropriate sort position.
- Pull prior year actuals from the `sales` table for the new pillar's filter.
- Recalculate Coverage row to include the new pillar.

Killing a pillar:
- User decides: delete rows entirely, or move to a "Retired" section.
- Recalculate Coverage.

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

Never use `ws.format`, `ws.clear`, or `batch_clear` on this tab.
