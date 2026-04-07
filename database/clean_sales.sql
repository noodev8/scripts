-- ================================================================
-- clean_sales.sql
-- Runs weekly via clean_sales.py (cron: Mondays 4am)
--
-- Jobs:
--   1. Purge old data from sales, bclog, stockorder, orderstatus_archive,
--      orderstatus (stale Amazon orders), amz_price_log
--   2-3. Fix returns that arrived with soldprice = 0
--        (so GP/margin calculations aren't skewed)
--   4. Delete unresolvable returns
--   5. Refresh 365-day sales totals on skumap (amz365, shp365, cmb365)
--
-- Replaces the manual PowerBuilder cleanup process.
-- ================================================================


-- ----------------------------------------------------------------
-- STEP 1: Purge old data
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE solddate < CURRENT_DATE - INTERVAL '900 days';

DELETE FROM bclog
WHERE date < CURRENT_DATE - INTERVAL '30 days';

DELETE FROM stockorder
WHERE orderdate < CURRENT_DATE - INTERVAL '365 days';

DELETE FROM orderstatus_archive
WHERE archivedate < CURRENT_DATE - INTERVAL '365 days';

DELETE FROM amz_price_log
WHERE log_date < CURRENT_DATE - INTERVAL '365 days';

DELETE FROM orderstatus
WHERE ordertype = 3
  AND arrived = 0
  AND createddate < CURRENT_DATE - INTERVAL '9 days';


-- ----------------------------------------------------------------
-- STEP 2: Fix return prices — match by original order
--
-- Returns (qty < 0) sometimes arrive with soldprice = 0.
-- Find the original sale using ordernum + code + channel
-- and copy the soldprice across.
-- ----------------------------------------------------------------
WITH bad_returns AS (
    SELECT id, code, channel, ordernum
    FROM sales
    WHERE qty < 0
      AND soldprice = 0
      AND solddate >= CURRENT_DATE - INTERVAL '365 days'
),
matching_sales AS (
    SELECT DISTINCT ON (r.id)
        r.id AS return_id,
        s.soldprice
    FROM bad_returns r
    JOIN sales s
      ON r.ordernum = s.ordernum
     AND r.code = s.code
     AND r.channel = s.channel
    WHERE s.qty > 0
      AND s.soldprice > 0
      AND s.solddate >= CURRENT_DATE - INTERVAL '365 days'
    ORDER BY r.id, s.solddate DESC
)
UPDATE sales
SET soldprice = ms.soldprice
FROM matching_sales ms
WHERE sales.id = ms.return_id;


-- ----------------------------------------------------------------
-- STEP 3: Fix return prices — estimate from current price
--
-- For returns we couldn't match by order, use the current
-- Shopify or Amazon price as a best-guess estimate.
-- ----------------------------------------------------------------
UPDATE sales
SET soldprice = CASE
    WHEN channel = 'SHP' THEN CAST(ss.shopifyprice AS NUMERIC)
    WHEN channel = 'AMZ' THEN CAST(af.amzprice AS NUMERIC)
    ELSE NULL
END
FROM skusummary ss
LEFT JOIN amzfeed af ON ss.groupid = af.groupid
WHERE sales.groupid = ss.groupid
  AND sales.qty < 0
  AND sales.soldprice = 0
  AND sales.solddate >= CURRENT_DATE - INTERVAL '365 days';


-- ----------------------------------------------------------------
-- STEP 4: Delete unresolvable returns
--
-- Any returns still at soldprice = 0 after steps 2-3 can't be
-- fixed. Delete them so they don't drag down margin numbers.
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE qty < 0
  AND soldprice = 0
  AND solddate >= CURRENT_DATE - INTERVAL '365 days';


-- ----------------------------------------------------------------
-- STEP 5: Update 365-day sales totals on skumap
--
-- Refresh amz365, shp365, cmb365 columns with rolling 365-day
-- unit counts per channel. Runs after return-price fixes so
-- the totals reflect corrected data.
-- ----------------------------------------------------------------

-- Reset all values to zero
UPDATE skumap
SET amz365 = 0,
    shp365 = 0,
    cmb365 = 0;

-- Update with actual sales data for CM3, AMZ, and SHP
WITH cm3_sales AS (
    SELECT
        code,
        SUM(qty) AS total_qty_sold
    FROM sales
    WHERE channel = 'CM3'
      AND solddate >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY code
),
amz_sales AS (
    SELECT
        code,
        SUM(qty) AS total_qty_sold
    FROM sales
    WHERE channel = 'AMZ'
      AND solddate >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY code
),
shp_sales AS (
    SELECT
        code,
        SUM(qty) AS total_qty_sold
    FROM sales
    WHERE channel = 'SHP'
      AND solddate >= CURRENT_DATE - INTERVAL '365 days'
    GROUP BY code
),
combined_sales AS (
    SELECT
        COALESCE(cs.code, ams.code, ss.code) AS code,
        COALESCE(cs.total_qty_sold, 0) AS cmb365,
        COALESCE(ams.total_qty_sold, 0) AS amz365,
        COALESCE(ss.total_qty_sold, 0) AS shp365
    FROM cm3_sales cs
    FULL OUTER JOIN amz_sales ams ON cs.code = ams.code
    FULL OUTER JOIN shp_sales ss ON COALESCE(cs.code, ams.code) = ss.code
)
UPDATE skumap
SET cmb365 = COALESCE(cs.cmb365, 0),
    amz365 = COALESCE(cs.amz365, 0),
    shp365 = COALESCE(cs.shp365, 0)
FROM combined_sales cs
WHERE skumap.code = cs.code;
