WITH daily AS (
  SELECT
    pt.shopify_price        AS price,
    SUM(pt.shopify_sales)   AS units_sold,
    COUNT(DISTINCT pt.date) AS days_recorded
  FROM price_track pt
  WHERE pt.groupid = '1017723-BEND'
    AND pt.shopify_sales IS NOT NULL
  GROUP BY pt.shopify_price
),
costs AS (
  SELECT
    ss.groupid,
    ss.cost::NUMERIC AS unit_cost
  FROM skusummary ss
  WHERE ss.groupid = '1017723-BEND'
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
