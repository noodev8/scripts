# Shopify Sync

The nightly push from our database to Shopify — prices, stock, titles, tags —
plus the daily price/stock history snapshot. All five run unattended in one
overnight block; see `crontab.txt` for schedules.

The database is the master in every case. These scripts only push outward.

## The five scripts

| Script | Does |
|---|---|
| `price_update.py` | Pushes prices to Shopify |
| `update_shopify_inventory.py` | Pushes stock levels |
| `update_shopify_titles.py` | Pushes product titles |
| `update_shopify_tags.py` | Pushes tags — full compare every run |
| `price_track.py` | Records daily price/stock/sales history into `price_track` |

They're independent — none imports another, and each can be run alone.

`price_track.py` is the odd one out: it doesn't push anything to Shopify, it
records history. It lives here because it runs in the same nightly block and
reads the same data.

## Run

```
python shopify-sync/price_update.py                  # changed rows only (default)
python shopify-sync/price_update.py full             # force a full update
python shopify-sync/price_update.py --groupid <id>   # one groupid
python shopify-sync/update_shopify_inventory.py
python shopify-sync/update_shopify_titles.py --force # ignore sync status
python shopify-sync/update_shopify_tags.py --dry-run # preview, change nothing
python shopify-sync/price_track.py
```

## How a price actually reaches Shopify

Worth knowing, because it's a two-step handshake and neither half is obvious:

1. A decided price is applied with `shopify-price/apply_prices.py`, which writes
   `skusummary.shopifyprice`, sets **`shopifychange = 1`**, sets the review date,
   and logs to `price_change_log`.
2. The nightly `price_update.py` selects `WHERE shopify = 1 AND shopifychange = 1`,
   pushes those to Shopify, and clears the flag.

**So a direct `UPDATE` of `shopifyprice` never reaches Shopify** — without the
flag, the sweep doesn't see it. Always go through `apply_prices.py`.

The same handshake is the safety net elsewhere: `amz-match/amz_match_sync.py`
pushes prices directly and, if that push fails, sets `shopifychange = 1` so this
sweep re-pushes it. Nobody watches an automated run, so the retry has to be
automatic.

`--no-google` on the cron lines is a **no-op**, kept only so existing cron
entries don't break. Google Merchant prices come from `merchant-feed/`.

## Paths

Each script anchors `.env` and `logging_utils` on the repo root, one level up.
Keep it that way if you add files here — cron runs with no `cd`, so anything
resolved against the working directory lands in the invoking user's home.
