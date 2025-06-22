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
      ELSE NULL
    END AS status_code,
    CASE
      WHEN shopify_sales >= 5 THEN 'Raise Price – Hot 🔴 (High Burst)'
      WHEN shopify_sales BETWEEN 3 AND 4 AND COALESCE(avg_recent_sales, 0) < 1 THEN 'Raise Price – Hot 🔴'
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.3 THEN 'Raise Price – Medium 🟠 (Strong)'
      WHEN shopify_sales = 2 AND COALESCE(avg_recent_sales, 0) <= 0.5 THEN 'Raise Price – Medium 🟠'
      ELSE NULL
    END AS action
  FROM rolling_avg
  WHERE shopify_sales >= 2
    AND shopify_sales > 2 * COALESCE(avg_recent_sales, 0)
),
log_filtered AS (
  SELECT DISTINCT groupid
  FROM price_change_log
  WHERE change_date >= CURRENT_DATE - INTERVAL '7 days'
)

SELECT
  b.groupid,
  b.date,
  b.shopify_sales,
  b.avg_recent_sales,
  b.shopify_price,
  CAST(ss.rrp AS NUMERIC) AS rrp,
  b.shopify_stock,
  b.prev_stock,
  b.action,
  b.status_code
FROM bursts b
LEFT JOIN log_filtered l ON b.groupid = l.groupid
LEFT JOIN skusummary ss ON b.groupid = ss.groupid
WHERE l.groupid IS NULL
  AND b.status_code IS NOT NULL
  AND b.status_code < 3  -- Only show top priorities
ORDER BY
  b.status_code,
  b.shopify_sales DESC,
  b.avg_recent_sales ASC,
  b.shopify_stock DESC;
