# Shopify Sync

Only `price_track.py` is left here: the daily price/stock/sales history snapshot into `price_track` (it records, it doesn't push).
See `crontab.txt` for its schedule.

**Nothing in this repo pushes to Shopify any more** (2026-11-08). BCWEB does it all:
- **prices and titles** — sent with every BCWEB product push (the pricing screens, Add / Modify); `price_update.py` and
  `update_shopify_titles.py` retired;
- **stock** — set at the end of every Update Orders run (button and cron), `bcweb-server/utils/shopifyStockSync.js`;
  `update_shopify_inventory.py` (3am) retired. Stock changed by hand in Shopify admin is overwritten — change it in BCWEB.
All three scripts are in `archive/shopify-sync/`.

## Run

```
python shopify-sync/price_track.py
```

## How a price reaches Shopify

**BCWEB pushes it, the moment it is set** (the Shopify pricing screens / W1 and Add / Modify →
`bcweb-server/utils/shopify.js`). There is no nightly price push any more: `price_update.py` and
`shopify-price/apply_prices.py` were retired on 2026-11-08 (both in `archive/`). Nothing sets
`skusummary.shopifychange = 1` now, so the flag is dead. A direct `UPDATE` of `shopifyprice`
still never reaches Shopify — set prices in BCWEB.

Titles are the same: BCWEB sends the title with every push, so `update_shopify_titles.py` was retired
on 2026-11-08 too (`archive/`).

Drift between BCWEB and Shopify (prices AND titles) is checked by hand as a monthly task:
`node scripts/shopify-price-check.js` in `bcweb-server/` (`--fix` re-pushes the styles that differ).

## Paths

Each script anchors `.env` and `logging_utils` on the repo root, one level up.
Keep it that way if you add files here — cron runs with no `cd`, so anything
resolved against the working directory lands in the invoking user's home.
