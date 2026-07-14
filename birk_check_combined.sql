-- Check Birkenstock arrivals for one or more invoices delivered together
-- Edit target_invoices / start_date / end_date below for future runs.
WITH params AS (
  SELECT
    ARRAY['5290101345']::text[] AS target_invoices,
    '2026-07-14'::date AS start_date,
    '2026-07-14'::date AS end_date
),
expected AS (
  SELECT
    b.code,
    SUM(b.invoiced) AS total_invoiced,
    MIN(TO_DATE(b.invoicedate, 'DD.MM.YYYY')) AS invoice_date
  FROM birktracker b
  JOIN params p
    ON b.invoicenum = ANY(p.target_invoices)
  GROUP BY b.code
),
actual AS (
  SELECT
    i.code,
    SUM(i.quantity_added) AS total_arrived
  FROM incoming_stock i
  JOIN skusummary s
    ON i.groupid = s.groupid
  JOIN params p
    ON TRUE
  WHERE s.brand = 'Birkenstock'
    AND i.created_at::date BETWEEN p.start_date AND p.end_date
    AND i.code IN (
      SELECT code
      FROM birktracker, params
      WHERE invoicenum = ANY(target_invoices)
    )
  GROUP BY i.code
),
final AS (
  SELECT
    e.code,
    e.total_invoiced,
    COALESCE(a.total_arrived, 0) AS total_arrived,
    (e.total_invoiced - COALESCE(a.total_arrived, 0)) AS shortfall
  FROM expected e
  LEFT JOIN actual a
    ON e.code = a.code

  UNION ALL

  SELECT
    'TOTAL' AS code,
    SUM(e.total_invoiced) AS total_invoiced,
    SUM(COALESCE(a.total_arrived, 0)) AS total_arrived,
    SUM(e.total_invoiced - COALESCE(a.total_arrived, 0)) AS shortfall
  FROM expected e
  LEFT JOIN actual a
    ON e.code = a.code
)
SELECT *
FROM final
ORDER BY
  CASE WHEN code = 'TOTAL' THEN 1 ELSE 0 END,
  shortfall DESC,
  code;
