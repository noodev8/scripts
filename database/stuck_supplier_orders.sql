-- ================================================================
-- stuck_supplier_orders.sql
--
-- On-demand report: supplier orders that haven't arrived yet and
-- are old enough to be worth chasing or writing off.
--
-- WHEN TO USE THIS
--   Run ad-hoc when you're in "cleanup mode" and want to decide:
--     - Chase the supplier?
--     - Write it off mentally and reorder?
--     - Leave it (still within normal lead time)?
--
--   Typical trigger: you're about to reorder a SKU and want to
--   confirm whether the "on order" rows in orderstatus are real
--   incoming stock or ghosts that will never arrive.
--
-- WHY 12 DAYS
--   Typical supplier check-in is ~10 days. Past 12 days the row
--   is starting to look stale, and the auto-purge will fire at
--   30 days. This report surfaces rows in the 12-30 day window
--   so you can manually clear confirmed ghosts ahead of the
--   purge (e.g. before a reorder session) rather than wait for
--   Monday's cron.
--
--   Threshold is deliberately tight — the purge is aggressive
--   now, so the report only needs to flag the early-warning
--   window. If you find you're not running this in your normal
--   flow, consider dropping it; the 30-day auto-purge mostly
--   does the job on its own.
--
-- HOW IT RELATES TO THE PURGES
--   - clean_sales.sql (Mon 4am): deletes ordertype=3, arrived=0,
--     createddate < 30 days ago.
--   - update_orders2.py line 713: backstop, ordertype<>1 older
--     than 30 days, regardless of arrived flag.
--
--   Both purges use 30 days = 10-day typical lead + 20-day
--   longest legitimate arrival observed + buffer.
--
--   This report does NOT delete anything by default. It surfaces
--   rows so you can act on them before the 30-day purge tidies up.
--
-- WHAT IT SHOWS
--   - ordernum, code, supplier, days since created
--   - quantity still outstanding (requested - arrived units)
--   - whether the SKU currently has any local stock (#FREE)
--   - sorted oldest first so the most-likely-ghosts float up
--
-- IF YOU'RE LOOKING FOR SOMETHING SIMILAR
--   - "What's on order from supplier X?" → query orderstatus
--     directly with ordertype=3 AND arrived=0, no age filter
--   - "What arrived recently?" → use incoming_stock table
--   - "What's in transit from Birkenstock specifically?" →
--     birktracker table (see MEMORY.md)
-- ================================================================

SELECT
    os.ordernum,
    os.code,
    os.supplier,
    os.createddate::date                                AS ordered_on,
    (CURRENT_DATE - os.createddate::date)               AS days_old,
    os.qty                                              AS qty_ordered,
    COALESCE(ls.free_qty, 0)                            AS current_free_stock,
    CASE
        WHEN (CURRENT_DATE - os.createddate::date) >= 25 THEN 'GHOST - auto-purge imminent (30d)'
        WHEN (CURRENT_DATE - os.createddate::date) >= 20 THEN 'LATE - past longest legitimate arrival'
        ELSE                                                  'STALE - past typical 10d lead'
    END                                                 AS status
FROM orderstatus os
LEFT JOIN (
    SELECT code, SUM(qty) AS free_qty
    FROM localstock
    WHERE ordernum = '#FREE'
      AND deleted = 0
      AND qty > 0
    GROUP BY code
) ls ON ls.code = os.code
WHERE os.ordertype = 3
  AND COALESCE(os.arrived, 0) = 0
  AND os.createddate < CURRENT_DATE - INTERVAL '12 days'
ORDER BY os.createddate ASC, os.supplier, os.code;


-- ================================================================
-- STEP 2 (optional): Delete confirmed ghosts
--
-- Why this exists:
--   The PowerBuilder Amazon Total report sums orderstatus rows
--   to show "on order" quantities. As long as a ghost row sits in
--   orderstatus, it inflates that total and suppresses reorders —
--   you'll look at PB, see stock is "on the way," and skip the
--   reorder for something that's never coming.
--
--   Mental write-off doesn't fix this. The row has to be gone.
--
-- How to use:
--   1. Run the SELECT above.
--   2. Review the list. For each row, decide: chase supplier,
--      wait, or write off as a ghost.
--   3. To delete the ghosts, narrow the WHERE clause below to
--      JUST those rows (by ordernum + code, or by a tighter
--      day threshold) and uncomment the DELETE.
--
-- Safety:
--   - Wrap in a transaction so you can ROLLBACK if the row count
--     looks wrong.
--   - NEVER run the DELETE with only the 12-day filter — that
--     would nuke legitimately-in-transit stock. Always narrow it.
--   - The 30-day auto-purge in clean_sales.sql is the fallback
--     for rows you don't process here.
-- ================================================================

-- BEGIN;
--
-- DELETE FROM orderstatus
-- WHERE ordertype = 3
--   AND COALESCE(arrived, 0) = 0
--   AND createddate < CURRENT_DATE - INTERVAL '12 days'
--   -- ADD NARROWING CONDITIONS HERE, e.g.:
--   -- AND ordernum IN ('XXX', 'YYY')
--   -- AND code = 'ZZZ'
-- ;
--
-- -- Check the count looks right before committing:
-- -- COMMIT;
-- -- or ROLLBACK; if it doesn't
