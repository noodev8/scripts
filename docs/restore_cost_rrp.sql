-- SQL script to restore cost and rrp for 47 Birkenstock product groups
-- Generated from day-before-1753.txt on 06 Nov 2025 10:26:49
-- Run this on your VPS production database

BEGIN;

UPDATE skusummary SET cost = '16.67', rrp = '40.00' WHERE groupid = '0128163-MADRID';
UPDATE skusummary SET cost = '16.67', rrp = '40.00' WHERE groupid = '0128183-MADRID';
UPDATE skusummary SET cost = '16.67', rrp = '40.00' WHERE groupid = '1015398-BARBADOS';
UPDATE skusummary SET cost = '18.75', rrp = '45.00' WHERE groupid = '0128201-GIZEH';
UPDATE skusummary SET cost = '20.83', rrp = '45.00' WHERE groupid = '0129423-ARIZONA';
UPDATE skusummary SET cost = '20.83', rrp = '45.00' WHERE groupid = '0129443-ARIZONA';
UPDATE skusummary SET cost = '20.83', rrp = '45.00' WHERE groupid = '1019051-ARIZONA';
UPDATE skusummary SET cost = '20.83', rrp = '45.00' WHERE groupid = '1019142-ARIZONA';
UPDATE skusummary SET cost = '20.83', rrp = '45.00' WHERE groupid = '1019152-ARIZONA';
UPDATE skusummary SET cost = '25.00', rrp = '60.00' WHERE groupid = '1014938-ZERMATT';
UPDATE skusummary SET cost = '31.25', rrp = '75.00' WHERE groupid = '0040391-MADRID';
UPDATE skusummary SET cost = '31.25', rrp = '75.00' WHERE groupid = '0040731-MADRID';
UPDATE skusummary SET cost = '31.25', rrp = '75.00' WHERE groupid = '0040733-MADRID';
UPDATE skusummary SET cost = '31.25', rrp = '75.00' WHERE groupid = '0040791-MADRID';
UPDATE skusummary SET cost = '31.25', rrp = '75.00' WHERE groupid = '0040793-MADRID';
UPDATE skusummary SET cost = '35.42', rrp = '80.00' WHERE groupid = '0051701-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '80.00' WHERE groupid = '0051753-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '80.00' WHERE groupid = '0051791-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '80.00' WHERE groupid = '0552681-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '80.00' WHERE groupid = '0552683-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '0043691-GIZEH';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '0043693-GIZEH';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '0143621-GIZEH';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '0143623-GIZEH';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '0745531-GIZEH';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '1027720-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '1027721-ARIZONA';
UPDATE skusummary SET cost = '35.42', rrp = '85.00' WHERE groupid = '1029811-MAYARI';
UPDATE skusummary SET cost = '37.50', rrp = '85.00' WHERE groupid = '0043661-GIZEH';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '0034701-MILANO';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '0034703-MILANO';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '0034791-MILANO';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1005292-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1005293-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1005294-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1005299-GIZEH';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1005300-GIZEH';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1009921-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1013069-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1025006-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1025046-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1029439-ARIZONA';
UPDATE skusummary SET cost = '37.50', rrp = '90.00' WHERE groupid = '1029470-ARIZONA';
UPDATE skusummary SET cost = '56.25', rrp = '135.00' WHERE groupid = '1017721-BEND';
UPDATE skusummary SET cost = '56.25', rrp = '135.00' WHERE groupid = '1017722-BEND';
UPDATE skusummary SET cost = '56.25', rrp = '135.00' WHERE groupid = '1017723-BEND';
UPDATE skusummary SET cost = '56.25', rrp = '135.00' WHERE groupid = '1017724-BEND';

COMMIT;

-- Verify the update:
-- SELECT COUNT(*) FROM skusummary WHERE brand = 'Birkenstock' AND (cost IS NULL OR cost = '' OR rrp IS NULL OR rrp = '');
