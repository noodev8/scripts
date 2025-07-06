-- STAFF ACTIVITY DETAIL
SELECT
    changed_by,
    change_date,
    groupid,
    old_price,
    new_price,
    reason_code,
    reason_notes
FROM price_change_log
WHERE change_date >= CURRENT_DATE - INTERVAL '7 days'
  AND changed_by IS NOT NULL
  AND changed_by = 'Summer'
ORDER BY changed_by, change_date DESC;
