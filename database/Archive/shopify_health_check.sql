CREATE OR REPLACE VIEW shopify_health_check AS

WITH
-- ==========================================
-- SALES, STOCK, PRICE CTEs
-- ==========================================

sales_30d AS (
  SELECT
    code,
    SUM(qty) AS sales_30d,
    ROUND(AVG(soldprice), 2) AS avg_price_30d
  FROM sales
  WHERE channel = 'SHP'
    AND solddate >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY code
),

sales_90d AS (
  SELECT
    code,
    SUM(qty) AS sales_90d
  FROM sales
  WHERE channel = 'SHP'
    AND solddate >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY code
),

local_stock AS (
  SELECT
    code,
    SUM(qty) AS local_stock
  FROM localstock
  WHERE deleted = 0
  GROUP BY code
),

ukd_stock AS (
  SELECT
    code,
    SUM(stock) AS ukd_stock
  FROM ukdstock
  GROUP BY code
),

shopify_price AS (
  SELECT
    groupid,
    shopifyprice AS shopifyprice_current,
    rrp
  FROM skusummary
),

-- ==========================================
-- HEALTH CHECK BUILD
-- ==========================================
health_check AS (
  SELECT
    p.code,
    p.channel,
    p.groupid,
    p.brand,
    p.owner,
    p.status,
    p.last_reviewed,
    p.notes,
    p.sold_qty,
    p.annual_profit,
    p.profit_per_unit,
    p.segment,

    COALESCE(ls.local_stock, 0) AS local_stock,
    COALESCE(us.ukd_stock, 0) AS ukd_stock,
    COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0) AS total_stock,

    sp.shopifyprice_current,
    sp.rrp,
    COALESCE(s30.sales_30d, 0) AS sales_30d,
    COALESCE(s90.sales_90d, 0) AS sales_90d,
    ROUND(COALESCE(s30.sales_30d, 0) / 30.0, 2) AS sales_velocity_per_day,
    ROUND(
      CASE 
        WHEN COALESCE(s30.sales_30d, 0) = 0 THEN 0
        ELSE (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) / (s30.sales_30d / 30.0)
      END, 2
    ) AS days_of_stock_left,

    (COALESCE(s90.sales_90d, 0) = 0) AS no_sales_90d_flag,
    (COALESCE(s30.sales_30d, 0) < (COALESCE(s90.sales_90d, 0) / 3.0)) AS sales_slowdown_flag,
    (NULLIF(sp.shopifyprice_current, '')::NUMERIC > (COALESCE(s30.avg_price_30d, 0) * 1.10)) AS price_check_flag,
    (
      p.segment = 'Winner'
      AND COALESCE(s90.sales_90d, 0) = 0
      AND (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) > 0
    ) AS overstock_flag,

    -- ==========================================
    -- FINAL RECOMMENDED ACTION
    -- ==========================================
    CASE
      WHEN (
        p.segment = 'Winner'
        AND p.brand IN ('Birkenstock', 'Skechers', 'Rieker')
        AND (
          (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0) < 5)
          OR (
            (COALESCE(s30.sales_30d, 0) / 30.0) > 0
            AND ROUND(
              CASE 
                WHEN COALESCE(s30.sales_30d, 0) = 0 THEN 0
                ELSE (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) / (s30.sales_30d / 30.0)
              END, 2) < 14
          )
        )
      ) THEN 'Price Too Low'

      WHEN (
        p.segment = 'Winner'
        AND (
          (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0) < 5)
          OR (
            (COALESCE(s30.sales_30d, 0) / 30.0) > 0
            AND ROUND(
              CASE 
                WHEN COALESCE(s30.sales_30d, 0) = 0 THEN 0
                ELSE (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) / (s30.sales_30d / 30.0)
              END, 2) < 14
          )
        )
      ) THEN 'Restock'

      WHEN (
        p.segment = 'Winner'
        AND NULLIF(sp.shopifyprice_current, '')::NUMERIC > (COALESCE(s30.avg_price_30d, 0) * 1.10)
      ) THEN 'Price Too High'

      WHEN (
        p.segment = 'Winner'
        AND COALESCE(s90.sales_90d, 0) = 0
        AND (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) > 0
      ) THEN 'Stock Not Moving'

      WHEN (
        p.segment = 'Winner'
        AND COALESCE(s90.sales_90d, 0) = 0
      ) THEN 'No Sales 90d'

      WHEN (
        p.segment = 'Winner'
        AND (COALESCE(s30.sales_30d, 0) < (COALESCE(s90.sales_90d, 0) / 3.0))
      ) THEN 'Sales Dropping'

      WHEN (
        p.segment = 'Loser'
        AND p.annual_profit < 0
      ) THEN 'Discontinue'

      WHEN (
        p.segment = 'Loser'
        AND p.profit_per_unit < 2
        AND p.sold_qty >= 20
      ) THEN 'Review Cost / Price'

      WHEN (
        p.segment = 'Loser'
        AND COALESCE(s90.sales_90d, 0) = 0
      ) THEN 'Clearance'

      WHEN (
        p.segment = 'Loser'
        AND (
          (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0) < 5)
          OR (
            (COALESCE(s30.sales_30d, 0) / 30.0) > 0
            AND ROUND(
              CASE 
                WHEN COALESCE(s30.sales_30d, 0) = 0 THEN 0
                ELSE (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) / (s30.sales_30d / 30.0)
              END, 2) < 14
          )
        )
      ) THEN 'Price Too Low'

      WHEN (
        p.segment = 'Loser'
        AND COALESCE(s90.sales_90d, 0) = 0
        AND (COALESCE(ls.local_stock, 0) + COALESCE(us.ukd_stock, 0)) > 0
      ) THEN 'Stock Not Moving'

      WHEN (
        p.segment = 'Loser'
        AND (COALESCE(s30.sales_30d, 0) < (COALESCE(s90.sales_90d, 0) / 3.0))
      ) THEN 'Sales Dropping'

      ELSE 'OK'
    END AS recommended_action

  FROM performance p
  LEFT JOIN local_stock ls ON p.code = ls.code
  LEFT JOIN ukd_stock us ON p.code = us.code
  LEFT JOIN shopify_price sp ON p.groupid = sp.groupid
  LEFT JOIN sales_30d s30 ON p.code = s30.code
  LEFT JOIN sales_90d s90 ON p.code = s90.code
  WHERE p.channel = 'SHP'
)

SELECT *
FROM health_check;
