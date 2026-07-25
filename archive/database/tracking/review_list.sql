-- Which GROUPIDs do I need to review
SELECT
    groupid,
    brand,
    annual_profit,
    sold_qty,
    avg_profit_per_unit,
    ROUND(avg_gross_margin * 100, 2) AS margin_pct,
    next_review_date,
    owner
FROM groupid_performance
WHERE owner = 'Andreas'
  AND (next_review_date IS NULL OR next_review_date <= CURRENT_DATE)
ORDER BY annual_profit DESC;
