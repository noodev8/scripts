# Merchant Feed — the reviews

**The feed itself moved to bcweb on 2026-11-08** (owner: the Python moves into BCWEB one script at a time). The nightly
Google Merchant Center feed is `bcweb-server/scripts/merchant-feed.js --upload`, its rules in
`bcweb-server/utils/merchantFeed.js` — the same file the Python built, compared line by line before the switch. The
Python `merchant_feed.py` is in `archive/merchant-feed/` (history only; don't run or extend it). The schedule is in
`crontab.txt`.

What stays here are the two REVIEWS, run with Claude when asked. Their approved results are stored in the database
(`shopify_description`, `merchant_product_type`) and the bcweb feed simply reads them.

## Descriptions

The `description` column is the product's Shopify description, cleaned to plain
text — but **only once someone has approved it**. Until then the feed sends the
title, as it always did. The nightly feed (bcweb) never calls Shopify and never cleans
anything; it reads `shopify_description.description` and that's all.

Approval is a review run when asked (roughly monthly), done with Claude — the
`/descriptions-review` skill in bcweb — using `descriptions.py`. The same approved
text is read by bcweb's eBay listing, so the review covers **every Shopify
product that is one of our styles**, not only Google-live ones (2026-11-03); the
feed still only sends Google-live products.

```
python merchant-feed/descriptions.py review           # fetch from Shopify, list new/changed
python merchant-feed/descriptions.py approve --all    # approve the whole list
python merchant-feed/descriptions.py approve <groupid> [<groupid> ...]
python merchant-feed/descriptions.py approve <groupid> --text "Hand-written text"
```

`review` fetches every product (two Shopify calls), cleans the HTML, and lists
products that are new or whose Shopify text has changed since approval.
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
