UPDATE winners w
SET target_stock = sub.suggested_target_stock
FROM (
  SELECT
    s.code,
    s.channel,
    CEIL(
      GREATEST(
        SUM(CASE WHEN s.solddate >= CURRENT_DATE - INTERVAL '60 days' THEN s.qty ELSE 0 END) / 60.0,
        SUM(CASE WHEN s.solddate >= CURRENT_DATE - INTERVAL '180 days' THEN s.qty ELSE 0 END) / 180.0
      ) * 14
    ) AS suggested_target_stock
  FROM sales s
  JOIN winners w2 ON w2.code = s.code AND w2.channel = s.channel
  GROUP BY s.code, s.channel
) sub
WHERE w.code = sub.code AND w.channel = sub.channel;
