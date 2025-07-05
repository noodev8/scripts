/*
===================================================================
STEP 1: Refresh 'performance' table with 365 days of sales data
         Includes:
         - Net Revenue (ex-VAT)
         - Net Profit (after channel fees)
         - Profit per unit
         - Gross Margin (before channel fees)
===================================================================
*/

WITH sales_summary AS (

    SELECT
        s.code,
        s.channel,
        ss.groupid,
        ss.brand,

        -- Total quantity sold
        SUM(s.qty) AS net_qty,

        -- Net revenue (sold price excluding VAT)
        ROUND(
            SUM(
                CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                     ELSE s.soldprice * s.qty
                END
            ), 2
        ) AS net_revenue,

        -- Net profit: Revenue - Cost - Channel fees
        ROUND(
            SUM(
                CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
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

        -- Profit per unit sold
        ROUND(
            (
                SUM(
                    CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
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
            ) / NULLIF(SUM(s.qty), 0), 2
        ) AS profit_per_unit,

        -- NEW: Gross margin before channel fees (Revenue - Cost) / Revenue
        ROUND(
            (SUM(
                CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                     ELSE s.soldprice * s.qty
                END
            ) - SUM(COALESCE(ss.cost::NUMERIC, 0) * s.qty))
            / NULLIF(
                SUM(
                    CASE WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                         ELSE s.soldprice * s.qty
                    END
                ), 0
            ), 4
        ) AS gross_margin

    FROM sales s
    JOIN skusummary ss ON s.groupid = ss.groupid
    WHERE s.solddate >= CURRENT_DATE - INTERVAL '365 days'
      AND s.soldprice > 0
    GROUP BY s.code, s.channel, ss.groupid, ss.brand
)

-- Insert or update the performance table
INSERT INTO performance (
    code, channel, groupid, brand,
    sold_qty, revenue, annual_profit, profit_per_unit,
    gross_margin,
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
    gross_margin,
    NULL AS segment,
    NULL AS fail_reason
FROM sales_summary
ON CONFLICT (code, channel) DO UPDATE
SET
    groupid = EXCLUDED.groupid,
    brand = EXCLUDED.brand,
    sold_qty = EXCLUDED.sold_qty,
    revenue = EXCLUDED.revenue,
    annual_profit = EXCLUDED.annual_profit,
    profit_per_unit = EXCLUDED.profit_per_unit,
    gross_margin = EXCLUDED.gross_margin;


/*
===================================================================
STEP 2: Roll up to 'groupid_performance' table
         - Aggregate by groupid & channel
         - Includes new average gross margin
===================================================================
*/

WITH groupid_sales AS (
    SELECT
        groupid,
        channel,
        SUM(annual_profit) AS total_profit,
        SUM(sold_qty) AS total_sold_qty,
        ROUND(AVG(profit_per_unit), 2) AS avg_profit_per_unit,
        ROUND(AVG(gross_margin), 4) AS avg_gross_margin
    FROM performance
    GROUP BY groupid, channel
)

-- Insert or update group-level performance
INSERT INTO groupid_performance (
    groupid,
    channel,
    annual_profit,
    sold_qty,
    avg_profit_per_unit,
    avg_gross_margin,
    owner
)
SELECT
    groupid,
    channel,
    total_profit,
    total_sold_qty,
    avg_profit_per_unit,
    avg_gross_margin,
    NULL AS owner
FROM groupid_sales
ON CONFLICT (groupid, channel) DO UPDATE
SET
    annual_profit = EXCLUDED.annual_profit,
    sold_qty = EXCLUDED.sold_qty,
    avg_profit_per_unit = EXCLUDED.avg_profit_per_unit,
    avg_gross_margin = EXCLUDED.avg_gross_margin;
