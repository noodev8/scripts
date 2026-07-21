-- ================================================================
-- clean_sales.sql
-- Runs weekly via clean_sales.py (cron: Mondays 4am)
--
-- Jobs:
--   1. Purge old data from sales, bclog, stockorder, incoming_stock (3yr),
--      orderstatus_archive, orderstatus (stale Amazon orders), amz_price_log,
--      amzshipment_archive
--   2-3. Fix returns that arrived with soldprice = 0
--        (so GP/margin calculations aren't skewed)
--   4. Delete unresolvable returns
--   5. Recompute return profit (negated) now that prices are repaired
--   6. Refresh 365-day sales totals on skumap (amz365, shp365, cmb365)
--
-- Replaces the manual PowerBuilder cleanup process.
-- ================================================================


-- ----------------------------------------------------------------
-- STEP 1: Purge old data
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE solddate < CURRENT_DATE - INTERVAL '900 days';

DELETE FROM bclog
WHERE date < CURRENT_DATE - INTERVAL '180 days';

DELETE FROM stockorder
WHERE orderdate < CURRENT_DATE - INTERVAL '365 days';

-- incoming_stock is the durable "what actually arrived" ledger (1 row per
-- unit received at goods-in). Retention is 3 YEARS, not shorter, on purpose:
-- the deepest reader is MAX(arrival_date) per groupid ("days since last
-- landed") in scale/pricing_pass.py and scale/check_null_segment.sql. The
-- cutoff must clear the slowest real restock cadence or we delete a still-live
-- style's last-landed date and it reads as "never arrived". Slowest observed
-- cadence is ~18 months (data only spans back that far), so 3 years leaves a
-- year of headroom. Cost of keeping is negligible (~1.5 MB/yr). Do NOT shorten
-- below ~3 years without re-checking last-arrival reach for active groupids.
-- Keyed on arrival_date (the field those readers use) so semantics match.
DELETE FROM incoming_stock
WHERE arrival_date < CURRENT_DATE - INTERVAL '3 years';

DELETE FROM orderstatus_archive
WHERE archivedate < CURRENT_DATE - INTERVAL '180 days';

DELETE FROM amz_price_log
WHERE log_date < CURRENT_DATE - INTERVAL '365 days';

-- 60-day window: shipment manifests are only needed until the boxes
-- land in FBA and reconcile, which is always inside a month. After
-- that the Amazon reports are the source of truth, so anything older
-- than 60d is dead reference data.
DELETE FROM amzshipment_archive
WHERE created_at < CURRENT_DATE - INTERVAL '60 days';

-- 30-day window = real-world ceiling (20d longest legitimate arrival
-- observed) + 10d buffer. Typical supplier check-in is ~10 days, so
-- 30d is 3x typical / 1.5x worst-seen.
--
-- PB goods-in sorts orderstatus by createddate DESC (LIFO): real arrivals
-- consume the newest rows, so anything still arrived=0 at 30d is genuine
-- surplus/never-coming and safe to purge.
--
-- Edge case: if stock arrives after this purge, it has no orderstatus
-- row to consume, so PB sends it straight to localstock #FREE. Order
-- trail is lost but stock isn't — factored into future reorders via
-- normal stock-aware logic. Acceptable trade vs. keeping ghosts in
-- the PB Amazon Total report that would suppress legitimate reorders.
--
-- See database/stuck_supplier_orders.sql for the 21-day early-warning
-- report that surfaces candidates before this auto-purge fires.
DELETE FROM orderstatus
WHERE ordertype = 3
  AND arrived = 0
  AND createddate < CURRENT_DATE - INTERVAL '30 days';


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
-- STEP 5: Recompute return profit (negated)
--
-- Returns (qty < 0) are inserted with no profit, and steps 2-3 above
-- repair their soldprice AFTER the fact — so profit must be (re)computed
-- here, once the price is known. Stored as the NEGATIVE of the equivalent
-- sale's per-unit net profit, so a sale and its return net to ~zero.
--
-- Per-channel P&L model — the single source of truth is bcweb
-- docs/profit-model.md (mirrored in update_orders2.shopify_profit and
-- bcweb-server/utils/profit.js):
--   VAT    = sold / 6
--   Gross  = sold - VAT - cost
--   Profit = (Gross - Expenses) / 1.2
--   SHP Expenses = (0.30 + 2.9% of sold) + 1.00 packing + 3.44 Royal Mail
--   AMZ Expenses = 15% referral + fbafee + 2% of fbafee + 2% of referral
--                  + 0.33 storage + 1.00 DPD + 0.50 wages
--
-- Only rows with the inputs the formula needs are touched (SHP needs
-- skusummary.cost; AMZ also needs amzfeed.fbafee). Returns for deleted
-- products (no skusummary row) keep their existing estimated profit
-- rather than being reset to NULL. Idempotent — safe to re-run.
-- ----------------------------------------------------------------

-- Shopify returns
UPDATE sales s
SET profit = -1 * ROUND(
      ( (s.soldprice - s.soldprice / 6 - ss.cost::numeric)
        - (0.30 + 0.029 * s.soldprice + 1.00 + 3.44) ) / 1.2
    , 2)
FROM skusummary ss
WHERE s.channel = 'SHP'
  AND s.qty < 0
  AND s.soldprice > 0
  AND ss.groupid = s.groupid
  AND ss.cost ~ '^[0-9]*\.?[0-9]+$'
  AND ss.cost::numeric > 0;

-- Amazon returns
UPDATE sales s
SET profit = -1 * ROUND(
      ( (s.soldprice - s.soldprice / 6 - ss.cost::numeric)
        - ( 0.15 * s.soldprice
            + af.fbafee::numeric
            + 0.02 * af.fbafee::numeric
            + 0.02 * (0.15 * s.soldprice)
            + 0.33 + 1.00 + 0.50 ) ) / 1.2
    , 2)
FROM skusummary ss, amzfeed af
WHERE s.channel = 'AMZ'
  AND s.qty < 0
  AND s.soldprice > 0
  AND ss.groupid = s.groupid
  AND af.code = s.code
  AND ss.cost ~ '^[0-9]*\.?[0-9]+$' AND ss.cost::numeric > 0
  AND af.fbafee ~ '^[0-9]*\.?[0-9]+$' AND af.fbafee::numeric > 0;


-- ----------------------------------------------------------------
-- STEP 6: Update 365-day sales totals on skumap
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
