-- 1) Report what you need to order and how many
SELECT
  code,
  brand,
  recommended_restock_qty AS qty_to_order
FROM shopify_health_check
WHERE owner                 = 'Andreas'
  AND status                = 'ASSIGNED'
  AND recommended_action    = 'Restock'
  AND recommended_restock_qty > 0;


-- 1) Update status with the order
UPDATE performance p
SET
  status       = 'NEW',
  status_date  = NOW(),
  notes        = sh.owner
               || ' - Restock order placed: '
               || sh.recommended_restock_qty
               || ' units.'
FROM shopify_health_check sh
WHERE p.code                  = sh.code
  AND sh.owner                = 'Andreas'
  AND sh.status               = 'ASSIGNED'
  AND sh.recommended_action   = 'Restock'
  AND sh.recommended_restock_qty > 0;
