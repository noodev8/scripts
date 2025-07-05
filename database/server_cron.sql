0 1 * * * /apps/scripts/venv/bin/python /apps/scripts/price_track.py
0 2 * * * /apps/scripts/venv/bin/python /apps/scripts/price_update.py full --no-google
0 3 * * * /apps/scripts/venv/bin/python /apps/scripts/update_shopify_inventory.py
0 6 * * * /apps/scripts/venv/bin/python /apps/scripts/merchant_feed.py
0 10,13,14,22 * * * /apps/scripts/venv/bin/python /apps/scripts/update_orders2.py
0 2 * * * /apps/scripts/pg_backup.sh
0 5 * * 1 /apps/scripts/venv/bin/python /apps/scripts/refresh_groupid_perfromance.py
