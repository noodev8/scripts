# Merchant Feed

Builds the Google Merchant Center product feed and uploads it.

`merchant_feed.py` pulls live product data from PostgreSQL, writes a TSV feed,
and pushes it to Google Merchant Center over SFTP. It runs unattended on the VPS
— see `crontab.txt` for the schedule.

## Run

```
python merchant-feed/merchant_feed.py
```

Works from any directory: the script resolves its own location, reaches back to
the repo root for `logging_utils`, and loads `.env` from there.

## Output

`GOOGLE-DATA-Merchant.txt` — the generated feed. It's written twice: once into
`merchant-feed/logs/` (the copy that gets uploaded) and once into this folder.
**It's a build artefact, not source** — it's overwritten on every run, so don't
edit it or treat its contents as a reference.

Logs go to `merchant-feed/logs/`, rotated into `merchant-feed/archive_logs/` —
this folder keeps its own, separate from the repo-root `logs/`.

## Descriptions

The `description` column is the product's Shopify description, cleaned to plain
text — but **only once someone has approved it**. Until then the feed sends the
title, as it always did. The nightly run never calls Shopify and never cleans
anything; it reads `shopify_description.description` and that's all.

Approval is a weekly review, done with Claude, using `descriptions.py`:

```
python merchant-feed/descriptions.py review           # fetch from Shopify, list new/changed
python merchant-feed/descriptions.py approve --all    # approve the whole list
python merchant-feed/descriptions.py approve <groupid> [<groupid> ...]
python merchant-feed/descriptions.py approve <groupid> --text "Hand-written text"
```

`review` fetches every product (two Shopify calls), cleans the HTML, and lists
feed products that are new or whose Shopify text has changed since approval.
Each proposal is in `merchant-feed/logs/description_review.md`, with any words
worth a second look (delivery, free, returns, sale, here...) flagged. Most flags
are harmless ("Free Spirit", "pressure-free cuff") — they're prompts, not errors.

Between reviews: a **new product** goes out with its title; an **edited
description** keeps going out as last approved until the next review picks up
the change.

Cleaning removes links and the navigation around them (width and colour pickers,
"CLICK HERE FOR MORE..."), delivery promises (Google rejects shipping claims in
descriptions), emoji, embedded CSS and images. **The "Stock Code: ..." line is
kept on purpose** — shoppers search by style code. Where little is left after
cleaning, the proposal is the title plus the stock code; better to fix those in
Shopify, which helps the website too.

## Product type and Google category

Same pattern as descriptions: reviewed with Claude, stored in
`merchant_product_type`, and simply read by the nightly feed. An unreviewed
product goes out with no `product_type` and category 187 (Shoes).

```
python merchant-feed/product_types.py review          # list new/changed proposals
python merchant-feed/product_types.py approve --all
python merchant-feed/product_types.py approve <groupid> --type "Home > ..." --category 209
```

Proposals come from `attributes.gender` and `attributes.producttype`, e.g.
`Home > Unisex > Footwear > Unisex Sandals` (plus "Wide Fit" when the title says
wide). Category is 187 (Shoes), except `Accessories`, which are all socks: 209.
A product comes back for review only if its proposal changes — fix the
`attributes` row and it will.

Run both reviews in the same session; they're independent.

## Configuration

Read from the root `.env`:

- `MERCHANT_SFTP_HOST`, `MERCHANT_SFTP_PORT` (default 19321),
  `MERCHANT_SFTP_USERNAME`, `MERCHANT_SFTP_PASSWORD`

If the SFTP credentials are missing the feed is still generated — only the
upload is skipped, and it says so rather than failing loudly. Worth knowing when
the feed looks stale on Google's side but the run looked fine.
