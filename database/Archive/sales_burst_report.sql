WITH shop_data AS (
  SELECT
    groupid,
    date,
    shopify_stock,
    shopify_sales,
    shopify_price,
    LAG(shopify_stock) OVER (PARTITION BY groupid ORDER BY date) AS prev_stock
  FROM price_track
  WHERE shopify_price IS NOT NULL
    AND date >= CURRENT_DATE - INTERVAL '14 days'
),
rolling_avg AS (
  SELECT *,
    ROUND(AVG(shopify_sales) OVER (
      PARTITION BY groupid ORDER BY date 
      ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ), 2) AS avg_recent_sales
  FROM shop_data
),
bursts AS (
  SELECT *,
    CASE
      WHEN shopify_sales >= 5 THEN 1
      WHEN shopify_sales BETWEEN 3 AND 4 AND COALESCE(avg_recent_sales, 0) < 1 THEN 2
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.3 THEN 3
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.5 THEN 4
      WHEN shopify_sales = 2 THEN 5
      ELSE NULL
    END AS status_code,
    CASE
      WHEN shopify_sales >= 5 THEN 'Raise Price – High Burst'
      WHEN shopify_sales BETWEEN 3 AND 4 AND COALESCE(avg_recent_sales, 0) < 1 THEN 'Raise Price – Burst'
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.3 THEN 'Raise Price – Medium (Strong)'
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.5 THEN 'Raise Price – Medium'
      WHEN shopify_sales = 2 THEN 'Raise Price – Low Burst'
      ELSE NULL
    END AS action
  FROM rolling_avg
  WHERE shopify_sales >= 2
    AND shopify_sales > 2 * COALESCE(avg_recent_sales, 0)
),
log_filtered AS (
  SELECT DISTINCT groupid
  FROM price_change_log
  WHERE change_date >= CURRENT_DATE - INTERVAL '10 days'
),
price_change_history AS (
  SELECT
    groupid,
    MAX(change_date) AS last_price_change_date,
    COUNT(*) AS total_price_changes_30d
  FROM price_change_log
  WHERE change_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY groupid
),
historical_sales AS (
  SELECT
    groupid,
    AVG(shopify_sales) AS avg_sales_14d,
    SUM(shopify_sales) AS total_sales_14d,
    COUNT(CASE WHEN shopify_sales > 0 THEN 1 END) AS days_with_sales_14d
  FROM price_track
  WHERE date >= CURRENT_DATE - INTERVAL '14 days'
    AND date < CURRENT_DATE - INTERVAL '1 day'  -- Exclude today
  GROUP BY groupid
),
final_bursts AS (
  SELECT
    b.*,
    CAST(ss.rrp AS NUMERIC) AS rrp,
    CAST(ss.cost AS NUMERIC) AS cost,
    ss.tax,
    ROUND(
      LEAST(
        CASE
          WHEN b.status_code = 1 THEN b.shopify_price * 1.05
          WHEN b.status_code = 2 THEN b.shopify_price * 1.02
          WHEN b.status_code = 3 THEN b.shopify_price * 1.03
          WHEN b.status_code = 4 THEN b.shopify_price * 1.02
          WHEN b.status_code = 5 THEN b.shopify_price * 1.01
          ELSE b.shopify_price
        END,
        CAST(ss.rrp AS NUMERIC)
      ), 2
    ) AS recommended_price,
    COALESCE(pch.last_price_change_date, DATE '1900-01-01') AS last_price_change_date,
    CURRENT_DATE - COALESCE(pch.last_price_change_date, DATE '1900-01-01') AS days_since_price_change,
    COALESCE(pch.total_price_changes_30d, 0) AS price_changes_30d,
    ROUND(hs.avg_sales_14d, 2) AS avg_sales_14d,
    COALESCE(hs.total_sales_14d, 0) AS total_sales_14d,
    COALESCE(hs.days_with_sales_14d, 0) AS days_with_sales_14d
  FROM bursts b
  LEFT JOIN log_filtered l ON b.groupid = l.groupid
  LEFT JOIN skusummary ss ON b.groupid = ss.groupid
  LEFT JOIN price_change_history pch ON b.groupid = pch.groupid
  LEFT JOIN historical_sales hs ON b.groupid = hs.groupid
  WHERE l.groupid IS NULL
    AND b.status_code IS NOT NULL
    AND b.status_code < 6
)

SELECT
  groupid,
  date,
  shopify_sales,
  avg_recent_sales,
  shopify_price,
  rrp,
  shopify_stock,
  prev_stock,
  action,
  status_code,
  recommended_price,
  ROUND(
    100 * (recommended_price - shopify_price) / shopify_price, 1
  ) AS price_change_percent,
  -- Profit impact calculations
  ROUND(
    CASE
      WHEN tax = 1 THEN (recommended_price / 1.2) - cost
      ELSE recommended_price - cost
    END, 2
  ) AS new_profit_per_unit,
  ROUND(
    CASE
      WHEN tax = 1 THEN (shopify_price / 1.2) - cost
      ELSE shopify_price - cost
    END, 2
  ) AS current_profit_per_unit,
  ROUND(
    CASE
      WHEN tax = 1 THEN ((recommended_price / 1.2) - cost) - ((shopify_price / 1.2) - cost)
      ELSE (recommended_price - cost) - (shopify_price - cost)
    END, 2
  ) AS profit_increase_per_unit,
  ROUND(
    (CASE
      WHEN tax = 1 THEN ((recommended_price / 1.2) - cost) - ((shopify_price / 1.2) - cost)
      ELSE (recommended_price - cost) - (shopify_price - cost)
    END) * shopify_stock, 2
  ) AS total_profit_impact,
  -- Price change history
  last_price_change_date,
  days_since_price_change,
  price_changes_30d,
  -- Historical sales trend
  avg_sales_14d,
  total_sales_14d,
  days_with_sales_14d,
  CASE
    WHEN avg_sales_14d > 1.5 THEN 'Strong Upward Trend'
    WHEN avg_sales_14d > 0.8 THEN 'Moderate Upward Trend'
    WHEN avg_sales_14d > 0.3 THEN 'Stable Sales'
    WHEN avg_sales_14d > 0 THEN 'Slow Sales'
    ELSE 'No Recent Sales'
  END AS sales_trend
FROM final_bursts
ORDER BY
  status_code,
  shopify_sales DESC,
  avg_recent_sales ASC,
  shopify_stock DESC;
