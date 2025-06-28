-- First, clear old losers data
DELETE FROM losers;

-- Now insert fresh diagnostic data
WITH sales_summary AS (

    SELECT
        s.code,
        s.channel,
        ss.groupid,
        ss.brand,

        -- Net quantity sold
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

        -- Net profit
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
            ), 2
        ) AS net_profit,

        -- Profit per unit
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

INSERT INTO losers (
    code,
    channel,
    groupid,
    brand,
    sold_qty,
    revenue,
    annual_profit,
    profit_per_unit,
    fail_reason
)
SELECT
    code,
    channel,
    groupid,
    brand,
    net_qty,
    net_revenue,
    net_profit,
    profit_per_unit,
    CASE
        WHEN net_profit < 0 THEN 'Negative profit'
        WHEN net_profit < 100 THEN 'Low profit'
        WHEN net_qty <= 0 THEN 'No sales'
        ELSE 'Unknown'
    END AS fail_reason
FROM sales_summary
WHERE net_profit < 100
ORDER BY net_profit ASC;
