SELECT * FROM performance WHERE status = 'ASSIGNED' LIMIT 5
SELECT * from shopify_health_check WHERE status = 'NEW' LIMIT 5
SELECT * FROM performance WHERE status = 'ASSIGNED' AND owner = 'Andreas'
SELECT code, channel, brand,owner, status,notes,recommended_action FROM shopify_health_check WHERE status = 'ASSIGNED' AND owner = 'Andreas'

WITH to_assign AS (
  SELECT code, channel
  FROM shopify_health_check
  WHERE status = 'NEW'
  LIMIT 5
)
UPDATE performance
SET
  status = 'ASSIGNED',
  owner = 'Andreas'
FROM to_assign
WHERE performance.code = to_assign.code
  AND performance.channel = to_assign.channel;


