DELETE FROM localstock
WHERE ordernum IS NOT NULL
  AND ordernum LIKE 'BC%'
  AND ordernum NOT IN (
    SELECT DISTINCT ordernum FROM orderstatus
  );
