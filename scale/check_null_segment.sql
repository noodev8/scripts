-- NULL-segment review: lists groupids without a segment, sorted fresh-down.
-- Companion to triage.sql — triage scans segmented in-season groupids,
-- this scans the gap (NULL segment) so newly-arrived stock doesn't fall
-- through. Walk newest-arrival first during segment sessions and decide
-- per row: assign to a segment, mark CRAP, or leave NULL (dead long-tail).
--
-- Default scope: Birkenstock only (where the live pain is). Broaden the
-- brand filter in `gids` to include other brands when needed.
--
-- Flag column meaning (sort puts arrived items above not-yet-arrived):
--   FRESH       arrived ≤14 days ago                       => too early; watch
--   ASSIGN      arrived >14d, has stock, ≥2 sales in 28d   => move to a segment
--   COLD        arrived >14d, has stock, ≤1 sale in 28d    => CRAP candidate
--   INCOMING    on forward order in birktracker, no arrival yet => track arrival
--   QUIET       no stock, no recent activity               => leave NULL or kill

WITH ref AS (
  SELECT CURRENT_DATE AS today
),
gids AS (
  SELECT s.groupid, s.brand, s.colour,
         s.shopifyprice::numeric AS price,
         NULLIF(s.rrp,'')::numeric AS rrp
  FROM skusummary s
  WHERE s.segment IS NULL
    AND s.brand ILIKE 'birkenstock%'
),
arrival AS (
  SELECT groupid, MAX(arrival_date) AS last_arrival
  FROM incoming_stock
  WHERE groupid IN (SELECT groupid FROM gids)
  GROUP BY groupid
),
sales_28 AS (
  SELECT groupid, SUM(qty)::int AS units
  FROM sales, ref
  WHERE qty > 0 AND soldprice > 0
    AND solddate::date BETWEEN (ref.today - 28) AND ref.today
    AND groupid IN (SELECT groupid FROM gids)
  GROUP BY groupid
),
stock_now AS (
  SELECT m.groupid, SUM(ls.qty)::int AS stock
  FROM skumap m
  JOIN localstock ls ON ls.code = m.code
  WHERE ls.deleted = 0 AND ls.ordernum = '#FREE'
    AND m.groupid IN (SELECT groupid FROM gids)
  GROUP BY m.groupid
),
inbound AS (
  SELECT m.groupid,
         SUM(GREATEST(COALESCE(bt.requested,0) - COALESCE(bt.arrived,0), 0))::int AS units
  FROM birktracker bt
  JOIN skumap m ON m.code = bt.code
  WHERE m.groupid IN (SELECT groupid FROM gids)
  GROUP BY m.groupid
)
SELECT
  g.groupid,
  g.colour,
  LEFT(t.shopifytitle, 60)        AS title,
  ar.last_arrival,
  COALESCE(sn.stock, 0)           AS stock,
  COALESCE(ib.units, 0)           AS inbound,
  COALESCE(s28.units, 0)          AS u28,
  g.price,
  CASE
    WHEN ar.last_arrival IS NOT NULL
         AND ar.last_arrival >= (SELECT today FROM ref) - 14
      THEN 'FRESH'
    WHEN COALESCE(sn.stock,0) > 0 AND COALESCE(s28.units,0) >= 2
      THEN 'ASSIGN'
    WHEN COALESCE(sn.stock,0) > 0 AND COALESCE(s28.units,0) <= 1
      THEN 'COLD'
    WHEN ar.last_arrival IS NULL AND COALESCE(ib.units,0) > 0
      THEN 'INCOMING'
    ELSE 'QUIET'
  END                             AS flag
FROM gids g
LEFT JOIN arrival   ar  ON ar.groupid = g.groupid
LEFT JOIN sales_28  s28 ON s28.groupid = g.groupid
LEFT JOIN stock_now sn  ON sn.groupid = g.groupid
LEFT JOIN inbound   ib  ON ib.groupid = g.groupid
LEFT JOIN title     t   ON t.groupid = g.groupid
ORDER BY
  CASE WHEN ar.last_arrival IS NOT NULL THEN 0 ELSE 1 END,
  ar.last_arrival DESC NULLS LAST,
  COALESCE(s28.units, 0) DESC,
  g.groupid;
