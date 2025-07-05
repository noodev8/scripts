SELECT *
FROM groupid_performance
WHERE owner = 'Andreas'
  AND (
    next_review_date <= CURRENT_DATE
    OR next_review_date IS NULL
  );

SELECT * 
FROM groupid_performance
WHERE owner = 'Andreas'
  AND next_review_date > CURRENT_DATE;

