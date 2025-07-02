SELECT
  groupid,
  COUNT(*) AS variant_count,
  SUM(sold_qty) AS total_sold_qty,
  ROUND(AVG(profit_per_unit), 2) AS avg_profit_per_unit,
  STRING_AGG(DISTINCT status, ', ') AS statuses,
  STRING_AGG(DISTINCT segment, ', ') AS segments,
  SUM(annual_profit) AS total_annual_profit
FROM performance
GROUP BY groupid
ORDER BY total_annual_profit DESC;
