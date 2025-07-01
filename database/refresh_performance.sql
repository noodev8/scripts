-- performance table:
--   segment: 'Winner' or 'Loser', based on profit threshold
--   fail_reason: reason for failing (if loser)
--   status: workflow tag (e.g. New, Fix planned, Active, Ignored, Waiting, Dropped, Promote)
--   notes: free text field for collaboration and explanation

WITH sales_summary AS (
    SELECT
        s.code,
        s.channel,
        ss.groupid,
        ss.brand,
        SUM(s.qty) AS net_qty,
        ROUND(
            SUM(
                CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                     ELSE s.soldprice * s.qty END
            ), 2
        ) AS net_revenue,
        ROUND(
            SUM(
                CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                     ELSE s.soldprice * s.qty END
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
        ROUND(
            (
                SUM(
                    CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                         ELSE s.soldprice * s.qty END
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
            ) / NULLIF(SUM(s.qty), 0), 2
        ) AS profit_per_unit
    FROM sales s
    JOIN skusummary ss ON s.groupid = ss.groupid
    WHERE s.solddate >= CURRENT_DATE - INTERVAL '365 days'
      AND s.soldprice > 0
    GROUP BY s.code, s.channel, ss.groupid, ss.brand
)
INSERT INTO performance (
    code, channel, groupid, brand,
    sold_qty, revenue, annual_profit, profit_per_unit,
    segment, fail_reason
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
        WHEN net_profit >= 100 THEN 'Winner'
        ELSE 'Loser'
    END AS segment,
    CASE
        WHEN net_profit < 0 THEN 'Negative profit'
        WHEN net_profit < 100 THEN 'Low profit'
        WHEN net_qty <= 0 THEN 'No sales'
        ELSE NULL
    END AS fail_reason
FROM sales_summary
ON CONFLICT (code, channel) DO UPDATE
SET
    groupid = EXCLUDED.groupid,
    brand = EXCLUDED.brand,
    sold_qty = EXCLUDED.sold_qty,
    revenue = EXCLUDED.revenue,
    annual_profit = EXCLUDED.annual_profit,
    profit_per_unit = EXCLUDED.profit_per_unit,
    segment = EXCLUDED.segment,
    fail_reason = EXCLUDED.fail_reason;
