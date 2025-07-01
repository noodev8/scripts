-- ----------------------------------------------------------------
-- STEP 1: Remove deleted and expired products from sales
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE solddate < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM sales
WHERE groupid NOT IN (
    SELECT groupid FROM skusummary
);


-- ----------------------------------------------------------------
-- STEP 2: Exact matching via ordernum
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
-- STEP 3: Estimate remaining returns using skusummary and amzfeed
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
-- STEP 4: Delete any remaining returns with soldprice = 0
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE qty < 0
  AND soldprice = 0
  AND solddate >= CURRENT_DATE - INTERVAL '365 days';
