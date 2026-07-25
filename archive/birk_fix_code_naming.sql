-- Fix birktracker.code naming mismatches vs skusummary.groupid
-- These 5 groupids use a long descriptive style name in birktracker
-- instead of the short style name used everywhere else (skusummary/skumap),
-- which causes false "not arrived" shortfalls when matching against incoming_stock.
--
-- Review the SELECT preview below before running the UPDATE.

-- Preview: rows that will change
SELECT code,
       regexp_replace(code, '^1015487-Honolulu Essentials EVA Unisex-', '1015487-HONOLULU-') AS new_code
FROM birktracker WHERE code LIKE '1015487-Honolulu Essentials EVA Unisex-%'
UNION ALL
SELECT code,
       regexp_replace(code, '^1031318-Honolulu Essentials EVA Unisex-', '1031318-HONOLULU-')
FROM birktracker WHERE code LIKE '1031318-Honolulu Essentials EVA Unisex-%'
UNION ALL
SELECT code,
       regexp_replace(code, '^1029356-Sydney Luxe Buckle Birko-Flor Women-', '1029356-SYDNEY-')
FROM birktracker WHERE code LIKE '1029356-Sydney Luxe Buckle Birko-Flor Women-%'
UNION ALL
SELECT code,
       regexp_replace(code, '^1029463-Sydney Luxe Buckle Birko-Flor Women-', '1029463-SYDNEY-')
FROM birktracker WHERE code LIKE '1029463-Sydney Luxe Buckle Birko-Flor Women-%'
UNION ALL
SELECT code,
       regexp_replace(code, '^1031695-Sydney Luxe Buckle Birko-Flor Women-', '1031695-SYDNEY-')
FROM birktracker WHERE code LIKE '1031695-Sydney Luxe Buckle Birko-Flor Women-%';

-- Actual update (run after reviewing the preview above)
UPDATE birktracker
SET code = regexp_replace(code, '^1015487-Honolulu Essentials EVA Unisex-', '1015487-HONOLULU-')
WHERE code LIKE '1015487-Honolulu Essentials EVA Unisex-%';

UPDATE birktracker
SET code = regexp_replace(code, '^1031318-Honolulu Essentials EVA Unisex-', '1031318-HONOLULU-')
WHERE code LIKE '1031318-Honolulu Essentials EVA Unisex-%';

UPDATE birktracker
SET code = regexp_replace(code, '^1029356-Sydney Luxe Buckle Birko-Flor Women-', '1029356-SYDNEY-')
WHERE code LIKE '1029356-Sydney Luxe Buckle Birko-Flor Women-%';

UPDATE birktracker
SET code = regexp_replace(code, '^1029463-Sydney Luxe Buckle Birko-Flor Women-', '1029463-SYDNEY-')
WHERE code LIKE '1029463-Sydney Luxe Buckle Birko-Flor Women-%';

UPDATE birktracker
SET code = regexp_replace(code, '^1031695-Sydney Luxe Buckle Birko-Flor Women-', '1031695-SYDNEY-')
WHERE code LIKE '1031695-Sydney Luxe Buckle Birko-Flor Women-%';
