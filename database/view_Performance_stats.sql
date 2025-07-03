SELECT
    owner,
    segment,
    COUNT(*) AS count_of_products,
    SUM(annual_profit) AS total_annual_profit,
    SUM(sold_qty) AS total_units_sold,
    ROUND(AVG(avg_profit_per_unit), 2) AS avg_profit_per_unit
FROM groupid_performance
WHERE channel = 'SHP'
  AND owner IS NOT NULL
GROUP BY owner, segment
ORDER BY owner, segment;
