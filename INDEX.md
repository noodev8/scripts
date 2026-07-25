# INDEX

Quick lookup for everything in this folder. One row per capability — what it is,
how to run it, and where the detail lives.

**Schedules are not listed here.** `crontab.txt` is the only record of what runs
when, and it mirrors the VPS, which is authoritative. The `Cron` column below
says only *whether* something is scheduled, never at what time.

**Domains:** `BC-ops` live Brookfield automation · `BC-analysis` interactive
decision processes · `OFD` Online Front Door (a separate business) · `Reference`
docs and material, not runnable.

## Capability folders

| Path | Domain | What it does | Run | Cron | Detail |
|---|---|---|---|---|---|
| `amz-match/` | BC-ops | Syncs our SKUs against Amazon listings | `python amz-match/amz_match_sync.py` | yes | `README.md` |
| `amz-price/` | BC-analysis | Amazon/FBA pricing reviews, any segment | interactive | no | `README.md` |
| `amz-product/` | BC-ops | New-product loader for Amazon | `python amz-product/amz_upload.py` | no | `CLAUDE_CONTEXT.md`, `how-to-run.md` |
| `barcodes/` | Reference | Ad-hoc barcode generation on request | ask | no | `README.md` |
| `birk-stock/` | BC-analysis | Birkenstock core-size availability (the `Full` metric) | `python birk-stock/availability.py` | no | `README.md` |
| `db-maint/` | BC-ops | Weekly sales-table purge + nightly database backup | `python db-maint/clean_sales.py`, `./db-maint/pg_backup.sh` | yes | `README.md` |
| `docs/` | Reference | Reference material and setup notes | — | no | — |
| `email/` | BC-analysis | Klaviyo email strategy and campaigns | interactive | no | `EMAIL_STRATEGY.md` |
| `google-ads/` | BC-ops | Ads spend/stock tracking + budget reviews | `python google-ads/update_google_stock_track.py` | yes | `BUDGET_REVIEW_PROCESS.md`, `how-to-run.md` |
| `images/` | BC-ops | Product image sync to Drive (for PowerBuilder) + Shopify extra-image protection | `python images/updateimages.py` | yes | `README.md` |
| `merchant-feed/` | BC-ops | Google Merchant Center product feed | `python merchant-feed/merchant_feed.py` | yes | `README.md` |
| `missing-sizes/` | BC-analysis | Amazon size-coverage gap report | `python missing-sizes/missing_sizes.py` | no | `README.md` |
| `month-end/` | BC-ops | Month-end accounting pack: transaction CSV, fees, stock position | `python month-end/month-export.py` | no | `README.md` |
| `orders/` | BC-ops | Shopify order sync + pick allocation (`--picks` for picks only) | `python orders/update_orders.py` | yes | `README.md` |
| `ofd/` | OFD | Online Front Door — separate business | interactive | no | `BUSINESS_PLAN.md` |
| `scale/` | BC-analysis | Segment strategy, pricing process, brand expansion | interactive | no | `CLAUDE_CONTEXT.md` |
| `seo/` | BC-analysis | Organic clicks: collection/product priorities, experiments | `python seo/weekly.py` | no | `PLAN.md` |
| `shopify-price/` | BC-analysis | Shopify pricing reviews and price application | interactive | no | `STRATEGY.md` |
| `shopify-sync/` | BC-ops | Nightly push to Shopify: prices, stock, titles, tags + daily price history | `python shopify-sync/price_update.py` | yes | `README.md` |
| `ukd/` | BC-analysis | UKD supplier channel — session guide, no scripts | interactive | no | `README.md` |
| `archive/` | Reference | Retired files. Soft delete — never referenced from live docs or code | — | no | — |

## Root scripts

Every capability now lives in a folder. Root holds only shared infrastructure —
if you're about to add a script here, it wants a folder instead.

| File | Domain | What it does | Cron |
|---|---|---|---|
| `logging_utils.py` | BC-ops | Shared logging + DB config. **Imported by ~25 scripts via `sys.path` — do not move** | — |

## Root docs and config

| File | What it is |
|---|---|
| `CLAUDE.md` | Standing instructions — read first |
| `INDEX.md` | This file |
| `catalogue.py` | Checks this index against reality (`python catalogue.py`). Report only — never changes anything |
| `crontab.txt` | Mirror of the VPS crontab. **The only schedule reference** |
| `.env` | Credentials, not in git |
| `client_secret.json`, `drive_oauth_client.json`, `drive_token.json`, `merchant-feed-api-*.json` | Google service-account and OAuth credentials |

## Conventions

See **"How this folder is organised"** in `CLAUDE.md` — folder per capability,
a front-door `.md` for each, paths anchored on `__file__`, `archive/` as a soft
delete, and schedules only in `crontab.txt`.

Kept in one place deliberately: two copies of a rule is how the old docs rotted.

Run `python catalogue.py` to check this index against reality.
