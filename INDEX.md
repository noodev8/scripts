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
| `docs/` | Reference | Reference material and setup notes | — | no | — |
| `email/` | BC-analysis | Klaviyo email strategy and campaigns | interactive | no | `EMAIL_STRATEGY.md` |
| `google-ads/` | BC-ops | Ads spend/stock tracking + budget reviews | `python google-ads/update_google_stock_track.py` | yes | `BUDGET_REVIEW_PROCESS.md`, `how-to-run.md` |
| `merchant-feed/` | BC-ops | Google Merchant Center product feed | `python merchant-feed/merchant_feed.py` | yes | `README.md` |
| `missing-sizes/` | BC-analysis | Amazon size-coverage gap report | `python missing-sizes/missing_sizes.py` | no | `README.md` |
| `month-end/` | BC-ops | Month-end accounting pack: transaction CSV, fees, stock position | `python month-end/month-export.py` | no | `README.md` |
| `ofd/` | OFD | Online Front Door — separate business | interactive | no | `BUSINESS_PLAN.md` |
| `scale/` | BC-analysis | Segment strategy, pricing process, brand expansion | interactive | no | `CLAUDE_CONTEXT.md` |
| `seo/` | BC-analysis | Organic clicks: collection/product priorities, experiments | `python seo/weekly.py` | no | `PLAN.md` |
| `shopify-price/` | BC-analysis | Shopify pricing reviews and price application | interactive | no | `STRATEGY.md` |
| `ukd/` | BC-analysis | UKD supplier channel — session guide, no scripts | interactive | no | `README.md` |
| `archive/` | Reference | Retired files. Soft delete — never referenced from live docs or code | — | no | — |

## Root scripts

Root holds shared infrastructure and the live cron scripts that haven't been
foldered yet.

| File | Domain | What it does | Cron |
|---|---|---|---|
| `logging_utils.py` | BC-ops | Shared logging + DB config. **Imported by ~25 scripts via `sys.path` — do not move** | — |
| `update_orders2.py` | BC-ops | Shopify order sync + pick allocation (`--picks` for picks only) | yes |
| `update_shopify_inventory.py` | BC-ops | Pushes stock levels to Shopify | yes |
| `update_shopify_titles.py` | BC-ops | Pushes product titles to Shopify | yes |
| `update_shopify_tags.py` | BC-ops | Pushes product tags to Shopify | yes |
| `price_update.py` | BC-ops | Pushes agreed prices to Shopify | yes |
| `price_track.py` | BC-ops | Records daily price/stock/sales history | yes |
| `updateimages.py` | BC-ops | Mirrors new product images into Google Drive | yes |
| `clean_sales.py` + `clean_sales.sql` | BC-ops | Sales/orderstatus table maintenance and purges | yes |
| `pg_backup.sh` | BC-ops | PostgreSQL backup | yes |
| `authorize_drive.py` | BC-ops | One-off Google Drive OAuth for `updateimages.py` | no |

## Root docs and config

| File | What it is |
|---|---|
| `CLAUDE.md` | Standing instructions — read first |
| `INDEX.md` | This file |
| `catalogue.py` | Checks this index against reality (`python catalogue.py`). Report only — never changes anything |
| `crontab.txt` | Mirror of the VPS crontab. **The only schedule reference** |
| `TIDY_PLAN.md` | Folder tidy-up, in progress |
| `.env` | Credentials, not in git |
| `client_secret.json`, `drive_oauth_client.json`, `drive_token.json`, `merchant-feed-api-*.json` | Google service-account and OAuth credentials |

## Conventions

- **A folder per capability.** Something you'd describe in a sentence gets a
  folder, whether it's one file or ten.
- **Every capability folder gets a front-door `.md`** saying what it does and how
  to run it. A paragraph and a usage line beats nothing.
- **Nothing is deleted for being old — it's archived.** `archive/` is a soft
  delete, tracked in git. Retired DB tables get a `_delete` suffix rather than a
  `DROP`.
- **Never point a live doc at `archive/`.** If archiving strands a reference,
  remove the reference.
- **Never restate a schedule** outside `crontab.txt`.
