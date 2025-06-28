-- Top 50 close-to-winner products with correct stock level by channel
SELECT
    l.code,
    l.channel,
    l.brand,
    l.sold_qty,
    l.revenue,
    l.annual_profit,
    l.profit_per_unit,
    l.fail_reason,
    CASE
        WHEN l.channel = 'SHP' THEN COALESCE(ls.qty, 0)
        WHEN l.channel = 'AMZ' THEN COALESCE(af.amztotal, 0)
        ELSE 0
    END AS stock_level
FROM losers l
LEFT JOIN localstock ls
  ON l.code = ls.code
LEFT JOIN amzfeed af
  ON l.code = af.groupid
WHERE l.annual_profit BETWEEN 0 AND 100
ORDER BY l.annual_profit DESC
LIMIT 50;



-- Dead stock with correct stock level by channel
SELECT
    l.code,
    l.channel,
    l.brand,
    CASE
        WHEN l.channel = 'SHP' THEN COALESCE(ls.qty, 0)
        WHEN l.channel = 'AMZ' THEN COALESCE(af.amztotal, 0)
        ELSE 0
    END AS stock_level
FROM losers l
LEFT JOIN localstock ls
  ON l.code = ls.code
LEFT JOIN amzfeed af
  ON l.code = af.groupid
WHERE l.sold_qty = 0
ORDER BY l.brand, l.code;



-- Profit Holes with stock level by channel
SELECT
    l.code,
    l.channel,
    l.brand,
    l.sold_qty,
    l.annual_profit,
    CASE
        WHEN l.channel = 'SHP' THEN COALESCE(ls.qty, 0)
        WHEN l.channel = 'AMZ' THEN COALESCE(af.amztotal, 0)
        ELSE 0
    END AS stock_level
FROM losers l
LEFT JOIN localstock ls
  ON l.code = ls.code
LEFT JOIN amzfeed af
  ON l.code = af.groupid
WHERE l.annual_profit < 0
ORDER BY l.annual_profit ASC
LIMIT 20;
