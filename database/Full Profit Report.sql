-- By GROUPID
WITH params AS (
  SELECT 
    30 AS num_days,
    'SHP' AS target_channel,
    4 AS min_sold,
    'ALL' AS target_brand,
    'gross_profit_total' AS sort_by  -- Options: 'sold', 'margin_percent'
),
recent_sales AS (
  SELECT s.groupid, s.brand, s.soldprice, s.solddate, s.qty
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0  -- Exclude returns
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
),
latest_price_per_group AS (
  SELECT DISTINCT ON (s.groupid) s.groupid, s.soldprice
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0  -- Exclude returns
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
  ORDER BY s.groupid, s.solddate DESC
)
SELECT 
  rs.groupid,
  rs.brand,
  SUM(rs.qty) AS sold,
  lpg.soldprice AS latest_sold_price,
  CAST(ss.shopifyprice AS NUMERIC) AS current_shopify_price,
  CAST(ss.rrp AS NUMERIC) AS rrp,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN (lpg.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpg.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit,

  ROUND(
    SUM(rs.qty) * 
    CASE 
      WHEN ss.tax = 1 THEN (lpg.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpg.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit_total,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN 
        100 * ((lpg.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpg.soldprice / 1.2), 0)
      ELSE 
        100 * (lpg.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpg.soldprice, 0)
    END, 1
  ) AS margin_percent

FROM recent_sales rs
JOIN latest_price_per_group lpg ON rs.groupid = lpg.groupid
LEFT JOIN skusummary ss ON rs.groupid = ss.groupid
JOIN params p ON TRUE
GROUP BY rs.groupid, rs.brand, lpg.soldprice, ss.shopifyprice, ss.rrp, ss.tax, ss.cost, p.sort_by
HAVING SUM(rs.qty) >= (SELECT min_sold FROM params)
ORDER BY
  CASE 
    WHEN p.sort_by = 'gross_profit_total' THEN 
      SUM(rs.qty) * 
        CASE 
          WHEN ss.tax = 1 THEN (lpg.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
          ELSE lpg.soldprice - CAST(ss.cost AS NUMERIC)
        END
    WHEN p.sort_by = 'sold' THEN SUM(rs.qty)
    WHEN p.sort_by = 'margin_percent' THEN
      CASE 
        WHEN ss.tax = 1 THEN 
          100 * ((lpg.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpg.soldprice / 1.2), 0)
        ELSE 
          100 * (lpg.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpg.soldprice, 0)
      END
  END DESC;



-- By CODE
WITH params AS (
  SELECT 
    30 AS num_days,
    'SHP' AS target_channel,
    4 AS min_sold,
    'Lunar' AS target_brand,
    'gross_profit_total' AS sort_by
),
recent_sales AS (
  SELECT s.code, s.groupid, s.brand, s.soldprice, s.solddate, s.qty
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
),
latest_price_per_code AS (
  SELECT DISTINCT ON (s.code) s.code, s.soldprice
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
  ORDER BY s.code, s.solddate DESC
)
SELECT 
  rs.code,
  rs.brand,
  rs.groupid,
  SUM(rs.qty) AS sold,
  lpc.soldprice AS latest_sold_price,
  CAST(ss.shopifyprice AS NUMERIC) AS current_shopify_price,
  CAST(ss.rrp AS NUMERIC) AS rrp,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit,

  ROUND(
    SUM(rs.qty) * 
    CASE 
      WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit_total,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN 
        100 * ((lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpc.soldprice / 1.2), 0)
      ELSE 
        100 * (lpc.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpc.soldprice, 0)
    END, 1
  ) AS margin_percent

FROM recent_sales rs
JOIN latest_price_per_code lpc ON rs.code = lpc.code
LEFT JOIN skusummary ss ON rs.groupid = ss.groupid
JOIN params p ON TRUE
GROUP BY rs.code, rs.brand, rs.groupid, lpc.soldprice, ss.shopifyprice, ss.rrp, ss.tax, ss.cost, p.sort_by
HAVING SUM(rs.qty) >= (SELECT min_sold FROM params)
ORDER BY
  CASE 
    WHEN p.sort_by = 'gross_profit_total' THEN 
      SUM(rs.qty) * 
        CASE 
          WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
          ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
        END
    WHEN p.sort_by = 'sold' THEN SUM(rs.qty)
    WHEN p.sort_by = 'margin_percent' THEN
      CASE 
        WHEN ss.tax = 1 THEN 
          100 * ((lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpc.soldprice / 1.2), 0)
        ELSE 
          100 * (lpc.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpc.soldprice, 0)
      END
  END DESC;



-- Winners not in Winners table
WITH params AS (
  SELECT 
    30 AS num_days,
    'AMZ' AS target_channel,
    4 AS min_sold,
    'Lunar' AS target_brand,
    'gross_profit_total' AS sort_by
),
recent_sales AS (
  SELECT s.code, s.groupid, s.brand, s.soldprice, s.solddate, s.qty
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
),
latest_price_per_code AS (
  SELECT DISTINCT ON (s.code) s.code, s.soldprice
  FROM sales s
  JOIN params p ON TRUE
  WHERE s.channel = p.target_channel
    AND s.solddate >= CURRENT_DATE - INTERVAL '1 day' * p.num_days
    AND s.soldprice > 0
    AND (UPPER(p.target_brand) = 'ALL' OR UPPER(s.brand) = UPPER(p.target_brand))
  ORDER BY s.code, s.solddate DESC
)
SELECT 
  rs.code,
  rs.brand,
  rs.groupid,
  SUM(rs.qty) AS sold,
  lpc.soldprice AS latest_sold_price,
  CAST(ss.shopifyprice AS NUMERIC) AS current_shopify_price,
  CAST(ss.rrp AS NUMERIC) AS rrp,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit,

  ROUND(
    SUM(rs.qty) * 
    CASE 
      WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
      ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
    END, 2
  ) AS gross_profit_total,

  ROUND(
    CASE 
      WHEN ss.tax = 1 THEN 
        100 * ((lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpc.soldprice / 1.2), 0)
      ELSE 
        100 * (lpc.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpc.soldprice, 0)
    END, 1
  ) AS margin_percent

FROM recent_sales rs
JOIN latest_price_per_code lpc ON rs.code = lpc.code
LEFT JOIN skusummary ss ON rs.groupid = ss.groupid
LEFT JOIN winners w ON rs.code = w.code AND w.channel = (SELECT target_channel FROM params)
JOIN params p ON TRUE
WHERE w.code IS NULL  -- NOT in winners table
GROUP BY rs.code, rs.brand, rs.groupid, lpc.soldprice, ss.shopifyprice, ss.rrp, ss.tax, ss.cost, p.sort_by
HAVING SUM(rs.qty) >= (SELECT min_sold FROM params)
ORDER BY
  CASE 
    WHEN p.sort_by = 'gross_profit_total' THEN 
      SUM(rs.qty) * 
        CASE 
          WHEN ss.tax = 1 THEN (lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)
          ELSE lpc.soldprice - CAST(ss.cost AS NUMERIC)
        END
    WHEN p.sort_by = 'sold' THEN SUM(rs.qty)
    WHEN p.sort_by = 'margin_percent' THEN
      CASE 
        WHEN ss.tax = 1 THEN 
          100 * ((lpc.soldprice / 1.2) - CAST(ss.cost AS NUMERIC)) / NULLIF((lpc.soldprice / 1.2), 0)
        ELSE 
          100 * (lpc.soldprice - CAST(ss.cost AS NUMERIC)) / NULLIF(lpc.soldprice, 0)
      END
  END DESC;

