WITH latest_snapshots AS (
    SELECT
        groupid,
        channel,
        owner,
        annual_profit,
        sold_qty,
        avg_profit_per_unit,
        avg_gross_margin,
        snapshot_date,
        ROW_NUMBER() OVER (
            PARTITION BY groupid, channel
            ORDER BY snapshot_date DESC
        ) AS row_num
    FROM groupid_performance_week
    WHERE owner IS NOT NULL
)

, latest AS (
    SELECT
        groupid,
        channel,
        owner,
        annual_profit,
        sold_qty,
        avg_profit_per_unit,
        avg_gross_margin
    FROM latest_snapshots
    WHERE row_num = 1
)

SELECT
    owner,
    COUNT(*) AS num_skus,
    ROUND(SUM(annual_profit), 2) AS total_annual_profit,
    SUM(sold_qty) AS total_sold_qty,
    ROUND(AVG(avg_profit_per_unit), 2) AS avg_profit_per_unit,
    ROUND(AVG(avg_gross_margin) * 100, 2) AS avg_margin_pct
FROM latest
GROUP BY owner
ORDER BY owner;
