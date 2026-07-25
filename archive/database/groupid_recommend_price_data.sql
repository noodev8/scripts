-- Get price track list
SELECT groupid,date,brand,shopify_stock,
shopify_sales, shopify_avg_sold_price, shopify_price 
FROM price_track where groupid = '0043691-GIZEH'
ORDER BY date DESC

-- Get price track summary
WITH params AS (
  SELECT '0043691-GIZEH'::TEXT AS groupid
),
daily AS (
  SELECT
    pt.shopify_price        AS price,
    SUM(pt.shopify_sales)   AS units_sold,
    COUNT(DISTINCT pt.date) AS days_recorded
  FROM price_track pt
  JOIN params p ON pt.groupid = p.groupid
  WHERE pt.shopify_sales IS NOT NULL
  GROUP BY pt.shopify_price
),
costs AS (
  SELECT
    ss.groupid,
    ss.cost::NUMERIC AS unit_cost
  FROM skusummary ss
  JOIN params p ON ss.groupid = p.groupid
)
SELECT
  d.price,
  ROUND(d.units_sold::NUMERIC / d.days_recorded, 2)   AS avg_units_per_day,
  c.unit_cost,
  ROUND(d.price - c.unit_cost, 2)                     AS margin_per_unit,
  ROUND((d.units_sold::NUMERIC / d.days_recorded) * (d.price - c.unit_cost), 2)
                                                      AS avg_daily_gross_profit
FROM daily d
CROSS JOIN costs c
ORDER BY d.price;

-- get lowbench
select groupid,lowbench from skusummary where groupid = '0043691-GIZEH'


