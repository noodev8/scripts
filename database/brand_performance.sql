SELECT
  brand,
  channel,
  COUNT(*) AS total_skus,
  COUNT(*) FILTER (WHERE segment = 'Winner') AS winners,
  COUNT(*) FILTER (WHERE segment = 'Loser') AS losers,
  SUM(annual_profit) AS total_annual_profit,
  ROUND(AVG(profit_per_unit), 2) AS avg_profit_per_unit
FROM performance
WHERE channel = 'SHP'
GROUP BY brand, channel
ORDER BY total_annual_profit DESC;
