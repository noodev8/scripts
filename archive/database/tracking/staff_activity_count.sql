-- STAFF ACTIVITY COUNT
SELECT
    changed_by,
    COUNT(*) AS num_price_changes
FROM price_change_log
WHERE change_date >= CURRENT_DATE - INTERVAL '7 days'
  AND changed_by IS NOT NULL
GROUP BY changed_by
ORDER BY num_price_changes DESC;
