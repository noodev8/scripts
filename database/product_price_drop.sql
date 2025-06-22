WITH latest_sales AS (
  SELECT
    s.groupid,
    MAX(s.solddate) AS last_sold_date,
    COUNT(*) AS total_sales
  FROM sales s
  WHERE s.solddate >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY s.groupid
),

recent_sales AS (
  SELECT
    s.groupid,
    COUNT(*) AS recent_sales_count
  FROM sales s
  WHERE s.solddate >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY s.groupid
),

inventory_view AS (
  SELECT
    ss.groupid,
    ss.brand,
    ss.shopifyprice::NUMERIC AS current_price,
    ss.lowbench::NUMERIC AS lowbench,
    ss.cost::NUMERIC AS cost,
    ss.tax,
    ls.qty AS stock,
    COALESCE((CURRENT_DATE - ls_qty.last_sold_date), 9999) AS days_since_last_sold,
    COALESCE(ls_qty.total_sales, 0) AS total_sales_90d,
    COALESCE(rs.recent_sales_count, 0) AS recent_sales_30d,

    ROUND(
      CASE
        WHEN ss.tax = 1 THEN (ss.shopifyprice::NUMERIC / 1.2) - ss.cost::NUMERIC
        ELSE ss.shopifyprice::NUMERIC - ss.cost::NUMERIC
      END,
      2
    ) AS margin_value

  FROM skusummary ss
  LEFT JOIN latest_sales ls_qty ON ss.groupid = ls_qty.groupid
  LEFT JOIN recent_sales rs ON ss.groupid = rs.groupid
  LEFT JOIN (
    SELECT groupid, SUM(qty) AS qty
    FROM localstock
    WHERE deleted = 0
    GROUP BY groupid
  ) ls ON ss.groupid = ls.groupid
  WHERE ss.shopify = 1
)

SELECT
  brand,
  groupid,
  current_price,
  lowbench,
  cost,
  stock,
  days_since_last_sold,
  total_sales_90d,
  recent_sales_30d,
  margin_value,

  -- Pricing logic category
  CASE
    WHEN total_sales_90d = 0 THEN 'ZERO_SALES'
    WHEN total_sales_90d > 0 THEN 'HISTORICAL_SALES'
    ELSE 'UNKNOWN'
  END AS pricing_category,

  -- Action determination based on new logic
  CASE
    -- Zero Sales Products Logic (Section 1.1)
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 0 AND 13 THEN 'HOLD'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock >= 15 THEN 'DROP_10'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock BETWEEN 5 AND 14 THEN 'DROP_5'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock <= 4 THEN 'HOLD'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock >= 15 THEN 'DROP_20'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock BETWEEN 5 AND 14 THEN 'DROP_10'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock <= 4 THEN 'DROP_5'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock >= 15 THEN 'DROP_30'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock BETWEEN 5 AND 14 THEN 'DROP_20'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock <= 4 THEN 'DROP_10'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock >= 15 THEN 'DROP_40'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock BETWEEN 5 AND 14 THEN 'DROP_30'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock <= 4 THEN 'DROP_15'
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 90 THEN 'DROP_TO_COST'
    WHEN total_sales_90d = 0 AND lowbench IS NOT NULL THEN 'USE_LOWBENCH'

    -- Historical Sales Products Logic (Section 1.2)
    WHEN total_sales_90d > 0 AND days_since_last_sold < 30 THEN 'HOLD'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock <= 4 THEN 'DROP_5'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN 'DROP_5'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock >= 15 AND recent_sales_30d <= 2 THEN 'DROP_10'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock <= 4 AND recent_sales_30d <= 2 THEN 'DROP_5'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN 'DROP_10'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock >= 15 AND recent_sales_30d <= 2 THEN 'DROP_15'
    WHEN total_sales_90d > 0 AND days_since_last_sold >= 90 AND recent_sales_30d <= 2 THEN 'DROP_20'
    WHEN total_sales_90d > 0 AND recent_sales_30d >= 3 AND days_since_last_sold < 30 THEN 'MANUAL_REVIEW'

    ELSE 'HOLD'
  END AS action,

  -- Reason explanation
  CASE
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 0 AND 13 THEN 'Zero sales - Too early to react'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock >= 15 THEN 'Zero sales - High stock, moderate aging'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock BETWEEN 5 AND 14 THEN 'Zero sales - Medium stock, gentle reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock <= 4 THEN 'Zero sales - Low stock, maintain price'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock >= 15 THEN 'Zero sales - High stock, significant aging'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock BETWEEN 5 AND 14 THEN 'Zero sales - Medium stock, moderate reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock <= 4 THEN 'Zero sales - Low stock, gentle nudge'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock >= 15 THEN 'Zero sales - High stock, serious aging'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock BETWEEN 5 AND 14 THEN 'Zero sales - Medium stock, significant reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock <= 4 THEN 'Zero sales - Low stock, moderate reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock >= 15 THEN 'Zero sales - High stock, critical aging'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock BETWEEN 5 AND 14 THEN 'Zero sales - Medium stock, aggressive reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock <= 4 THEN 'Zero sales - Low stock, meaningful reduction'
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 90 THEN 'Zero sales - Liquidation mode'
    WHEN total_sales_90d = 0 AND lowbench IS NOT NULL THEN 'Zero sales - Use benchmark price'

    WHEN total_sales_90d > 0 AND days_since_last_sold < 30 THEN 'Historical sales - Recent activity, maintain price'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock <= 4 THEN 'Historical sales - Low stock cushion'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN 'Historical sales - Medium stock, gentle push'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock >= 15 AND recent_sales_30d <= 2 THEN 'Historical sales - High stock, clear signal'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock <= 4 AND recent_sales_30d <= 2 THEN 'Historical sales - Low stock, minimal reduction'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN 'Historical sales - Medium stock, moderate push'
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock >= 15 AND recent_sales_30d <= 2 THEN 'Historical sales - High stock, strong signal'
    WHEN total_sales_90d > 0 AND days_since_last_sold >= 90 AND recent_sales_30d <= 2 THEN 'Historical sales - Aggressive clearance'
    WHEN total_sales_90d > 0 AND recent_sales_30d >= 3 AND days_since_last_sold < 30 THEN 'Historical sales - Conflicting signals'

    ELSE 'No action needed'
  END AS reason,

  -- Calculate suggested price based on action
  ROUND(GREATEST(CASE
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock >= 15 THEN current_price * 0.90  -- DROP_10
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 14 AND 27 AND stock BETWEEN 5 AND 14 THEN current_price * 0.95  -- DROP_5
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock >= 15 THEN current_price * 0.80  -- DROP_20
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock BETWEEN 5 AND 14 THEN current_price * 0.90  -- DROP_10
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 28 AND 41 AND stock <= 4 THEN current_price * 0.95  -- DROP_5
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock >= 15 THEN current_price * 0.70  -- DROP_30
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock BETWEEN 5 AND 14 THEN current_price * 0.80  -- DROP_20
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 42 AND 55 AND stock <= 4 THEN current_price * 0.90  -- DROP_10
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock >= 15 THEN current_price * 0.60  -- DROP_40
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock BETWEEN 5 AND 14 THEN current_price * 0.70  -- DROP_30
    WHEN total_sales_90d = 0 AND days_since_last_sold BETWEEN 56 AND 89 AND stock <= 4 THEN current_price * 0.85  -- DROP_15
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 90 THEN cost + 0.01  -- DROP_TO_COST
    WHEN total_sales_90d = 0 AND lowbench IS NOT NULL THEN GREATEST(lowbench, cost + 0.01)  -- USE_LOWBENCH

    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock <= 4 THEN current_price * 0.95  -- DROP_5
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN current_price * 0.95  -- DROP_5
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 30 AND 59 AND stock >= 15 AND recent_sales_30d <= 2 THEN current_price * 0.90  -- DROP_10
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock <= 4 AND recent_sales_30d <= 2 THEN current_price * 0.95  -- DROP_5
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock BETWEEN 5 AND 14 AND recent_sales_30d <= 2 THEN current_price * 0.90  -- DROP_10
    WHEN total_sales_90d > 0 AND days_since_last_sold BETWEEN 60 AND 89 AND stock >= 15 AND recent_sales_30d <= 2 THEN current_price * 0.85  -- DROP_15
    WHEN total_sales_90d > 0 AND days_since_last_sold >= 90 AND recent_sales_30d <= 2 THEN current_price * 0.80  -- DROP_20

    ELSE current_price  -- HOLD or MANUAL_REVIEW
  END, cost + 0.01), 2) AS suggested_price

FROM inventory_view
WHERE stock > 0
  AND (
    -- Only show items that need action (not HOLD)
    (total_sales_90d = 0 AND days_since_last_sold >= 14) OR
    (total_sales_90d > 0 AND days_since_last_sold >= 30) OR
    (total_sales_90d > 0 AND recent_sales_30d >= 3 AND days_since_last_sold < 30)
  )
ORDER BY
  CASE
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 90 THEN 1  -- Liquidation priority
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 56 THEN 2  -- Critical aging
    WHEN total_sales_90d > 0 AND recent_sales_30d >= 3 THEN 3       -- Manual review needed
    WHEN total_sales_90d = 0 AND days_since_last_sold >= 42 THEN 4  -- Serious aging
    ELSE 5
  END,
  days_since_last_sold DESC,
  stock DESC;
