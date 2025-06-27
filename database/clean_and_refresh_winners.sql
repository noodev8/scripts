-- ----------------------------------------------------------------
-- STEP 1: Exact matching via ordernum
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
-- STEP 2: Estimate remaining returns using skusummary and amzfeed
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
-- STEP 3: Delete any remaining returns with soldprice = 0
-- ----------------------------------------------------------------
DELETE FROM sales
WHERE qty < 0
  AND soldprice = 0
  AND solddate >= CURRENT_DATE - INTERVAL '365 days';


-- ----------------------------------------------------------------
-- STEP 4: Refresh Winners Table
-- ----------------------------------------------------------------
DELETE FROM winners;

WITH sales_summary AS (

    SELECT
        s.code,
        s.channel,
        ss.groupid,
        ss.brand,

        -- Net quantity sold (returns as negative)
        SUM(s.qty) AS net_qty,

        -- Net revenue excluding VAT
        ROUND(
            SUM(
                CASE 
                    WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                    ELSE s.soldprice * s.qty
                END
            ), 2
        ) AS net_revenue,

        -- Net profit = Revenue - Cost - Channel-specific expenses
        ROUND(
            SUM(
                CASE 
                    WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                    ELSE s.soldprice * s.qty
                END
            )
            - SUM(COALESCE(ss.cost::NUMERIC, 0) * s.qty)
            - SUM(
                CASE
                    WHEN s.channel = 'AMZ' THEN (
                        -- AMZ channel expenses per unit
                        0.15 * s.soldprice
                        + 3.05
                        + 0.02 * 3.05
                        + 0.02 * (0.15 * s.soldprice)
                        + 0.33
                        + 1
                        + 0.5
                    ) * ABS(s.qty)

                    WHEN s.channel = 'SHP' THEN (
                        -- SHP channel expenses per unit
                        0.3
                        + 0.029 * s.soldprice
                        + 0.5
                        + 3.44
                    ) * ABS(s.qty)

                    ELSE 0
                END
            ), 2
        ) AS net_profit,

        -- Average profit per unit sold
        ROUND(
            (
                SUM(
                    CASE 
                        WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                        ELSE s.soldprice * s.qty
                    END
                )
                - SUM(COALESCE(ss.cost::NUMERIC, 0) * s.qty)
                - SUM(
                    CASE
                        WHEN s.channel = 'AMZ' THEN (
                            0.15 * s.soldprice
                            + 3.05
                            + 0.02 * 3.05
                            + 0.02 * (0.15 * s.soldprice)
                            + 0.33
                            + 1
                            + 0.5
                        ) * ABS(s.qty)

                        WHEN s.channel = 'SHP' THEN (
                            0.3
                            + 0.029 * s.soldprice
                            + 0.5
                            + 3.44
                        ) * ABS(s.qty)

                        ELSE 0
                    END
                )
            ) / NULLIF(SUM(s.qty), 0)
        , 2) AS profit_per_unit

    FROM sales s
    JOIN skusummary ss ON s.groupid = ss.groupid
    WHERE s.solddate >= CURRENT_DATE - INTERVAL '365 days'
      AND s.soldprice > 0
    GROUP BY s.code, s.channel, ss.groupid, ss.brand

)

INSERT INTO winners (
    code,
    channel,
    groupid,
    brand,
    sold_qty,
    revenue,
    annual_profit,
    profit_per_unit
)
SELECT
    code,
    channel,
    groupid,
    brand,
    net_qty,
    net_revenue,
    net_profit,
    profit_per_unit
FROM sales_summary
WHERE net_profit >= 100
ORDER BY net_profit DESC;
