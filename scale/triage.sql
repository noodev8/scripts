-- Segment triage: scans all in-season segments and flags groupids that need attention.
-- Run weekly or fortnightly. Each row gets ONE primary flag (the most urgent).
--
-- Flags (priority order):
--   YOY_DROP     30d units < 70% of YoY same window (and YoY had ≥5)        => investigate
--   CLEAR_RISK   ≥30 in stock + ≥10 inbound + 30d sold <3                   => prevent dead pile
--   OOS_RUNNING  ≥1 running size at 0 stock AND 30d sold ≥6 (real momentum) => price up or chase stock
--   HARVEST      30d sold ≥3, no inbound, price <85% of RRP                 => lift price
--   COOLING      14d rate < 50% of 30d rate (and 30d ≥5)                    => watch
--   OK           none of the above
--
-- Stock = local #FREE + FBA (amzfeed.amzlive). OOS check uses combined per-size stock.
-- Excludes off-season segments (RIEKER-WIN, REMONTE-WIN) and CRAP.
-- Adjust the in_season_segments CTE seasonally.

WITH ref AS (
  SELECT CURRENT_DATE AS today
),
in_season_segments AS (
  SELECT unnest(ARRAY[
    'IVES-WHITE','IVES-COLOUR',
    'BEND-SEG','MILANO-SEG','GIZEH-SEG','EVA-SEG','MAYARI-SEG',
    'ARIZONA-PATENT-SEG','ARIZONA-BF-NAR','ARIZONA-BF-REG',
    'LAKE-SEG','ZERMATT-SEG',
    'BLAZE-SEG','UKD-SEG','RIEKER-SUM','FREE-SPIRIT'
  ]) AS segment
),
gids AS (
  SELECT s.groupid, s.segment, s.colour,
         s.shopifyprice::numeric AS price,
         NULLIF(s.rrp,'')::numeric AS rrp
  FROM skusummary s
  WHERE s.segment IN (SELECT segment FROM in_season_segments)
),
sales_30 AS (
  SELECT groupid, SUM(qty)::int AS units
  FROM sales, ref
  WHERE qty>0 AND soldprice>0
    AND solddate::date BETWEEN (ref.today - 30) AND ref.today
    AND groupid IN (SELECT groupid FROM gids)
  GROUP BY groupid
),
sales_14 AS (
  SELECT groupid, SUM(qty)::int AS units
  FROM sales, ref
  WHERE qty>0 AND soldprice>0
    AND solddate::date BETWEEN (ref.today - 14) AND ref.today
    AND groupid IN (SELECT groupid FROM gids)
  GROUP BY groupid
),
sales_yoy_30 AS (
  SELECT groupid, SUM(qty)::int AS units
  FROM sales, ref
  WHERE qty>0 AND soldprice>0
    AND solddate::date BETWEEN (ref.today - 365 - 30) AND (ref.today - 365)
    AND groupid IN (SELECT groupid FROM gids)
  GROUP BY groupid
),
stock_by_code AS (
  -- Per-code total: local #FREE + FBA amzlive. Used for both totals and OOS check.
  SELECT m.groupid, m.code,
         COALESCE(ls.qty,0) + COALESCE(af.amzlive,0) AS qty
  FROM skumap m
  LEFT JOIN (
    SELECT code, SUM(qty)::int AS qty FROM localstock
    WHERE deleted=0 AND ordernum='#FREE' GROUP BY code
  ) ls ON ls.code=m.code
  LEFT JOIN amzfeed af ON af.code=m.code
  WHERE m.deleted=0
    AND m.groupid IN (SELECT groupid FROM gids)
),
stock_now AS (
  SELECT groupid, SUM(qty)::int AS stock
  FROM stock_by_code
  GROUP BY groupid
),
inbound AS (
  SELECT m.groupid,
         SUM(GREATEST(COALESCE(bt.requested,0) - COALESCE(bt.arrived,0), 0))::int AS units
  FROM birktracker bt
  JOIN skumap m ON m.code=bt.code
  WHERE m.groupid IN (SELECT groupid FROM gids)
  GROUP BY m.groupid
),
running_sizes AS (
  -- Sizes that have sold ≥1 unit in the last 90d
  SELECT DISTINCT m.groupid, m.code
  FROM skumap m
  JOIN sales s ON s.code=m.code, ref
  WHERE s.qty>0 AND s.soldprice>0
    AND s.solddate::date >= (ref.today - 90)
    AND m.groupid IN (SELECT groupid FROM gids)
),
running_oos AS (
  -- How many running sizes are now stocked at zero (local + FBA combined)
  SELECT rs.groupid,
         COUNT(*) FILTER (WHERE COALESCE(sbc.qty,0) = 0) AS oos_running
  FROM running_sizes rs
  LEFT JOIN stock_by_code sbc ON sbc.code=rs.code
  GROUP BY rs.groupid
),
notes AS (
  SELECT DISTINCT ON (segment) segment, note_date, note
  FROM segment_notes ORDER BY segment, note_date DESC, created_at DESC
)
SELECT
  g.segment,
  g.groupid,
  g.colour,
  g.price,
  COALESCE(sn.stock, 0)            AS stock,
  COALESCE(ib.units, 0)            AS inbound,
  COALESCE(s30.units, 0)           AS u30,
  COALESCE(s14.units, 0)           AS u14,
  COALESCE(yoy30.units, 0)         AS u30_yoy,
  CASE WHEN COALESCE(yoy30.units,0) > 0
    THEN ROUND((COALESCE(s30.units,0) - yoy30.units) * 100.0 / yoy30.units, 0)
    ELSE NULL END                  AS yoy_pct,
  COALESCE(roos.oos_running, 0)    AS oos_running,
  CASE
    WHEN COALESCE(yoy30.units,0) >= 5
         AND COALESCE(s30.units,0) < yoy30.units * 0.7
      THEN 'YOY_DROP'
    WHEN COALESCE(sn.stock,0) >= 30 AND COALESCE(ib.units,0) >= 10
         AND COALESCE(s30.units,0) < 3
      THEN 'CLEAR_RISK'
    WHEN COALESCE(roos.oos_running,0) >= 1 AND COALESCE(s30.units,0) >= 6
      THEN 'OOS_RUNNING'
    WHEN COALESCE(s30.units,0) >= 3
         AND COALESCE(ib.units,0) = 0
         AND g.rrp IS NOT NULL AND g.price < g.rrp * 0.85
      THEN 'HARVEST'
    WHEN COALESCE(s30.units,0) >= 5
         AND COALESCE(s14.units,0) * 30.0 / 14.0 < COALESCE(s30.units,0) * 0.5
      THEN 'COOLING'
    ELSE 'OK'
  END                              AS flag,
  n.note_date                      AS last_note_date,
  LEFT(n.note, 80)                 AS last_note_snippet
FROM gids g
LEFT JOIN sales_30  s30   ON s30.groupid=g.groupid
LEFT JOIN sales_14  s14   ON s14.groupid=g.groupid
LEFT JOIN sales_yoy_30 yoy30 ON yoy30.groupid=g.groupid
LEFT JOIN stock_now sn    ON sn.groupid=g.groupid
LEFT JOIN inbound   ib    ON ib.groupid=g.groupid
LEFT JOIN running_oos roos ON roos.groupid=g.groupid
LEFT JOIN notes     n     ON n.segment=g.segment
ORDER BY
  CASE
    WHEN COALESCE(yoy30.units,0) >= 5 AND COALESCE(s30.units,0) < yoy30.units * 0.7 THEN 1
    WHEN COALESCE(sn.stock,0) >= 30 AND COALESCE(ib.units,0) >= 10 AND COALESCE(s30.units,0) < 3 THEN 2
    WHEN COALESCE(roos.oos_running,0) >= 1 AND COALESCE(s30.units,0) >= 6 THEN 3
    WHEN COALESCE(s30.units,0) >= 3 AND COALESCE(ib.units,0) = 0
         AND g.rrp IS NOT NULL AND g.price < g.rrp * 0.85 THEN 4
    WHEN COALESCE(s30.units,0) >= 5
         AND COALESCE(s14.units,0) * 30.0 / 14.0 < COALESCE(s30.units,0) * 0.5 THEN 5
    ELSE 9
  END,
  g.segment, g.groupid;
