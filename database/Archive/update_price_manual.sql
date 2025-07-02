-- ==========================================
-- 1️⃣ Define your list of CODES to take
-- ==========================================
WITH selected_codes AS (
  SELECT unnest(ARRAY[
    'CODE1',
    'CODE2',
    'CODE3'
  ]) AS code
),

-- ==========================================
-- 2️⃣ Get unique groupids for those codes
-- ==========================================
selected_groupids AS (
  SELECT DISTINCT p.groupid
  FROM performance p
  JOIN selected_codes sc ON p.code = sc.code
  WHERE p.channel = 'SHP'
)

-- ==========================================
-- 3️⃣ Update skusummary for those groupids
-- ==========================================
UPDATE skusummary
SET
  shopifyprice = LEAST(ROUND(shopifyprice * 1.05, 2), rrp),
  shopifychange = 1
FROM selected_groupids sg
WHERE skusummary.groupid = sg.groupid;
