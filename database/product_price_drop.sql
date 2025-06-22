WITH params AS (
  SELECT 'BIRKENSTOCK'::VARCHAR AS target_brand
),

latest_sales AS (
  SELECT 
    s.groupid,
    MAX(s.solddate) AS last_sold_date
  FROM sales s
  GROUP BY s.groupid
),

inventory_view AS (
  SELECT 
    ss.groupid,
    ss.shopifyprice::NUMERIC AS current_price,
    ss.lowbench::NUMERIC AS lowbench,
    ss.cost::NUMERIC AS cost,
    ss.tax,
    ls.qty AS stock,
    COALESCE((CURRENT_DATE - ls_qty.last_sold_date), 9999) AS days_since_last_sold,

    ROUND(
      CASE 
        WHEN ss.tax = 1 THEN (ss.shopifyprice::NUMERIC / 1.2) - ss.cost::NUMERIC
        ELSE ss.shopifyprice::NUMERIC - ss.cost::NUMERIC
      END,
      2
    ) AS margin_value

  FROM skusummary ss
  LEFT JOIN latest_sales ls_qty ON ss.groupid = ls_qty.groupid
  LEFT JOIN (
    SELECT groupid, SUM(qty) AS qty
    FROM localstock
    WHERE deleted = 0
    GROUP BY groupid
  ) ls ON ss.groupid = ls.groupid
)

SELECT 
  groupid,
  current_price,
  lowbench,
  cost,
  stock,
  days_since_last_sold,
  margin_value,

  CASE 
    WHEN (days_since_last_sold >= 180 OR days_since_last_sold = 9999) AND stock >= 10 THEN 1
    WHEN lowbench IS NOT NULL AND current_price >= lowbench * 1.10 AND days_since_last_sold >= 30 THEN 2
    WHEN lowbench IS NULL AND stock >= 15 AND days_since_last_sold BETWEEN 30 AND 179 THEN 3
    WHEN margin_value < 15 AND days_since_last_sold >= 30 THEN 4
    WHEN stock BETWEEN 5 AND 14 AND margin_value >= 15 AND days_since_last_sold >= 60 THEN 5
    WHEN stock <= 4 OR days_since_last_sold < 30 THEN 6
    WHEN stock >= 15 AND days_since_last_sold BETWEEN 30 AND 59 AND 
         (lowbench IS NULL OR current_price < lowbench * 1.10) THEN 7
    ELSE NULL
  END AS bucket,

  CASE 
    WHEN (days_since_last_sold >= 180 OR days_since_last_sold = 9999) AND stock >= 10 THEN 'Dead-stock: no sales in 6+ months, stock ≥ 10'
    WHEN lowbench IS NOT NULL AND current_price >= lowbench * 1.10 AND days_since_last_sold >= 30 THEN 'Market mismatch: overpriced vs lowbench and stale'
    WHEN lowbench IS NULL AND stock >= 15 AND days_since_last_sold BETWEEN 30 AND 179 THEN 'Stock-heavy, no market signal, and slow'
    WHEN margin_value < 15 AND days_since_last_sold >= 30 THEN 'Low-margin risk: under £15 per unit profit'
    WHEN stock BETWEEN 5 AND 14 AND margin_value >= 15 AND days_since_last_sold >= 60 THEN 'Slow-mover: moderate stock, stale, okay margin'
    WHEN stock <= 4 OR days_since_last_sold < 30 THEN 'Low-stock or recent: do nothing'
    WHEN stock >= 15 AND days_since_last_sold BETWEEN 30 AND 59 AND 
         (lowbench IS NULL OR current_price < lowbench * 1.10) THEN 'Early warning: heavy stock, sales slowing'
    ELSE NULL
  END AS bucket_reason,

  -- Suggested price, always validated to be >= cost
  ROUND(GREATEST(CASE 
    WHEN (days_since_last_sold >= 180 OR days_since_last_sold = 9999) AND stock >= 10 
         THEN GREATEST(current_price * 0.65, cost + 1)
    WHEN lowbench IS NOT NULL AND current_price >= lowbench * 1.10 AND days_since_last_sold >= 30 
         THEN lowbench * 0.98
    WHEN lowbench IS NULL AND stock >= 15 AND days_since_last_sold BETWEEN 30 AND 179 
         THEN current_price * 0.75
    WHEN margin_value < 15 AND days_since_last_sold >= 30 
         THEN cost + 0.01
    WHEN stock BETWEEN 5 AND 14 AND margin_value >= 15 AND days_since_last_sold >= 60 
         THEN COALESCE(LEAST(lowbench, current_price * 0.85), current_price * 0.85)
    WHEN stock >= 15 AND days_since_last_sold BETWEEN 30 AND 59 AND 
         (lowbench IS NULL OR current_price < lowbench * 1.10) 
         THEN current_price * 0.90
    ELSE NULL
  END, cost), 2) AS suggested_price

FROM inventory_view
WHERE stock > 0
ORDER BY bucket, days_since_last_sold DESC;
