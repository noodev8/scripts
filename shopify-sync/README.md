# Shopify Sync

The nightly push from our database to Shopify — stock, titles —
plus the daily price/stock history snapshot. The three run unattended in one
overnight block; see `crontab.txt` for schedules.

The database is the master in every case. These scripts only push outward.

## The scripts

| Script | Does |
|---|---|
| `update_shopify_inventory.py` | Pushes stock levels |
| `update_shopify_titles.py` | Pushes product titles |
| `price_track.py` | Records daily price/stock/sales history into `price_track` |

They're independent — none imports another, and each can be run alone.

`price_track.py` is the odd one out: it doesn't push anything to Shopify, it
records history. It lives here because it runs in the same nightly block and
reads the same data.

## Run

```
python shopify-sync/update_shopify_inventory.py
python shopify-sync/update_shopify_titles.py --force # ignore sync status
python shopify-sync/price_track.py
```

## How a price reaches Shopify

**BCWEB pushes it, the moment it is set** (the Shopify pricing screens / W1 and Add / Modify →
`bcweb-server/utils/shopify.js`). There is no nightly price push any more: `price_update.py` and
`shopify-price/apply_prices.py` were retired on 2026-11-08 (both in `archive/`). Nothing sets
`skusummary.shopifychange = 1` now, so the flag is dead. A direct `UPDATE` of `shopifyprice`
still never reaches Shopify — set prices in BCWEB.

Drift between BCWEB and Shopify is checked by hand as a monthly task:
`node scripts/shopify-price-check.js` in `bcweb-server/` (`--fix` re-pushes the styles that differ).

## Paths

Each script anchors `.env` and `logging_utils` on the repo root, one level up.
Keep it that way if you add files here — cron runs with no `cd`, so anything
resolved against the working directory lands in the invoking user's home.
