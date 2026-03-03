-- ========= Adjust only these =========
WITH params AS (
  SELECT
    360::int      AS sold_window_days,       -- e.g. 30, 60, 90, 180
    1000::numeric AS gross_profit_threshold, -- total gross profit over the window
    1::int       AS min_sold_qty            -- minimum qty sold in the window
),

shp AS (  -- sales in the window (exclude returns/zeros), qty-weighted price
  SELECT
    s.groupid,
    SUM(s.soldprice * s.qty)::numeric / NULLIF(SUM(s.qty),0) AS avg_sold_price,
    SUM(s.qty)                                  AS sold_qty_window,
    MAX(s.solddate)                              AS last_sold_date
  FROM public.sales s
  WHERE s.channel = 'SHP'
    AND s.qty > 0
    AND s.soldprice > 0
    AND s.solddate >= CURRENT_DATE - (SELECT sold_window_days FROM params) * INTERVAL '1 day'
  GROUP BY s.groupid
),

local_variant_stock AS (  -- local stock per variant (size)
  SELECT
    sm.groupid,
    sm.code,
    COALESCE(SUM(CASE
      WHEN ls.ordernum = '#FREE' AND ls.deleted = 0 THEN ls.qty
      ELSE 0
    END), 0) AS local_stock
  FROM public.skumap sm
  LEFT JOIN public.localstock ls ON ls.code = sm.code
  GROUP BY sm.groupid, sm.code
),

oos_groups AS (           -- groups with at least one missing size locally
  SELECT lvs.groupid, COUNT(*) AS oos_variant_count
  FROM local_variant_stock lvs
  WHERE lvs.local_stock = 0
  GROUP BY lvs.groupid
),

group_stock AS (          -- total current local stock per group
  SELECT lvs.groupid, SUM(lvs.local_stock) AS group_local_stock
  FROM local_variant_stock lvs
  GROUP BY lvs.groupid
),

metrics AS (              -- compute margins & totals once
  SELECT
    ss.groupid,
    ss.brand,
    t.shopifytitle AS title,
    (
      -- VAT adjustment disabled: divide by 1 (no change)
      shp.avg_sold_price - NULLIF(ss.cost,'')::numeric
    )                           AS unit_gross_profit_raw,
    shp.sold_qty_window,
    (
      shp.avg_sold_price - NULLIF(ss.cost,'')::numeric
    ) * shp.sold_qty_window     AS gross_profit_total_raw,
    shp.last_sold_date,
    og.oos_variant_count,
    COALESCE(gs.group_local_stock, 0) AS group_local_stock
  FROM public.skusummary ss
  JOIN shp           ON shp.groupid = ss.groupid                 -- ≥1 sale in window
  JOIN oos_groups og ON og.groupid = ss.groupid                  -- has missing sizes locally
  JOIN group_stock gs ON gs.groupid = ss.groupid                 -- group-level local stock
  LEFT JOIN public.title t ON t.groupid = ss.groupid
  WHERE ss.shopify = 1
    AND shp.sold_qty_window >= (SELECT min_sold_qty FROM params)
    AND ss.brand ILIKE 'Birkenstock'
    AND (ss.check_stock IS NULL OR ss.check_stock <= CURRENT_DATE) -- due for review
)

SELECT
  groupid,
  title,
  sold_qty_window                   AS sold_qty,
  ROUND(unit_gross_profit_raw, 2)   AS unit_gross_profit,
  ROUND(gross_profit_total_raw, 2)  AS gross_profit_total
FROM metrics
WHERE gross_profit_total_raw > (SELECT gross_profit_threshold FROM params)
ORDER BY gross_profit_total_raw DESC, sold_qty_window DESC, last_sold_date DESC;
