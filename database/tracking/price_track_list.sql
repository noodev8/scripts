SELECT groupid,date,brand,shopify_stock,
shopify_sales, shopify_avg_sold_price, shopify_price 
FROM price_track where groupid = '1017723-BEND'
ORDER BY date DESC
