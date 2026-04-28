# IVES-COLOUR — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Groupids

9 colours under one segment:
`FLE030-IVES-BEIGE`, `FLE030-IVES-BLACK`, `FLE030-IVES-BLACKSOLE`, `FLE030-IVES-GREY`, `FLE030-IVES-KHAKI`, `FLE030-IVES-MIDBLUE`, `FLE030-IVES-NAVY-BLUE`, `FLE030-IVES-RED`, `FLE030-IVES-STONE`

Channel: Amazon. Use `amzfeed.amzlive` for stock.

## SKU progress report — per-colour rollup (not per-code)

The default per-code SKU view is too wide (~53 rows). For IVES-COLOUR, roll up to colour:

| Colour | Sizes live | Stock | Units 14d | Units 30d | OOS sizes |
|---|---:|---:|---:|---:|---|

- **Sizes live** — count of distinct codes for the colour where `amzfeed.amzlive > 0`.
- **Stock** — sum of `amzfeed.amzlive` across all codes for the colour.
- **Units 14d / 30d** — sum of `sales.qty` (qty>0, soldprice>0) per groupid over the standard windows.
- **OOS sizes** — codes where `amzfeed.amzlive = 0` AND units_30d > 0 (i.e. sizes that *should* be selling but aren't in stock). Show size suffix only (e.g. "06, 07"). Dash if none.
- Add a totals row for Stock, Units 14d, Units 30d.
- Order rows alphabetically by colour.

Per-code drill is available on request when a specific colour needs a closer look.

```sql
WITH gids AS (SELECT groupid FROM skusummary WHERE segment='IVES-COLOUR'),
codes AS (
  SELECT DISTINCT sm.code, sm.groupid,
         REPLACE(sm.groupid, 'FLE030-IVES-', '') AS colour,
         RIGHT(sm.code, 2) AS size
  FROM skumap sm WHERE sm.groupid IN (SELECT groupid FROM gids) AND sm.deleted=0
),
stock AS (
  SELECT c.colour, c.code, c.size, COALESCE(a.amzlive,0) AS qty
  FROM codes c LEFT JOIN amzfeed a ON a.code=c.code
),
s14 AS (
  SELECT code, SUM(qty)::int AS u FROM sales
  WHERE groupid IN (SELECT groupid FROM gids) AND qty>0 AND soldprice>0
    AND solddate::date BETWEEN <l14_start> AND <l14_end>
  GROUP BY code
),
s30 AS (
  SELECT code, SUM(qty)::int AS u FROM sales
  WHERE groupid IN (SELECT groupid FROM gids) AND qty>0 AND soldprice>0
    AND solddate::date BETWEEN <l30_start> AND <l30_end>
  GROUP BY code
)
SELECT st.colour,
       SUM(CASE WHEN st.qty>0 THEN 1 ELSE 0 END) AS sizes_live,
       SUM(st.qty) AS stock,
       COALESCE(SUM(s14.u),0) AS units_14d,
       COALESCE(SUM(s30.u),0) AS units_30d,
       STRING_AGG(CASE WHEN st.qty=0 AND COALESCE(s30.u,0)>0 THEN st.size END, ', ' ORDER BY st.size) AS oos_sizes
FROM stock st
LEFT JOIN s14 ON s14.code=st.code
LEFT JOIN s30 ON s30.code=st.code
GROUP BY st.colour
ORDER BY st.colour;
```
