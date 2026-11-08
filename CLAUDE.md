# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based e-commerce automation and analytics system for Brookfield Comfort, primarily focused on Shopify store management, pricing, and inventory tracking. The system includes:

- **Order Management**: Shopify order synchronization and pick allocation
- **Inventory Management**: Stock tracking and Shopify inventory updates
- **Google Merchant Feed**: Automated product feed generation for Google Shopping
- **Pricing**: Interactive review processes for Shopify and Amazon — see the Shopify Pricing and Amazon Pricing sections below

## Common Commands

### Running Scripts
- **Google Merchant feed**: NOT in this repo since 2026-11-08 — bcweb's `bcweb-server/scripts/merchant-feed.js --upload` (rules `utils/merchantFeed.js`). The description / product-type REVIEWS (`merchant-feed/descriptions.py`, `product_types.py`) are still here.
- **Inventory sync**: `python shopify-sync/update_shopify_inventory.py`
- **Shopify title sync**: `python shopify-sync/update_shopify_titles.py`
- **Daily price history**: `python shopify-sync/price_track.py`. (The Shopify price PUSH, `price_update.py`, was retired 2026-11-08 — BCWEB pushes prices live; the monthly drift check is bcweb's `bcweb-server/scripts/shopify-price-check.js`.)

Most of these run unattended on the VPS. **`crontab.txt` is the only place that
records what runs when** — it mirrors the server, which is authoritative. Never
restate a schedule anywhere else; it rots.

### Database Operations
- **Backup database**: `./db-maint/pg_backup.sh` (server-side only; writes to `/apps/backups`)
- **Sales-table maintenance**: `python db-maint/clean_sales.py` (runs `clean_sales.sql` alongside it)
- **All database access goes through `db/`** — `python db/query.py "SELECT ..."` to read,
  `python db/write.py "UPDATE ..."` to write. `db/README.md` is the front door. This is what
  "use the db process" or "use the db folder" refers to.
- **Writing to the database is allowed.** No approval ritual beyond agreeing what to change.
  `write.py` is transactional, has `--dry-run`, and refuses an unscoped UPDATE/DELETE.
- For schema, query the database directly (`information_schema`) rather than looking for a
  schema file — there isn't one, and it would rot. There is deliberately **no Postgres MCP**;
  don't reinstate one without asking. `db/README.md` explains why.

## Architecture & Key Components

### Core Scripts
- **Order sync is NOT in this repo** (since 2026-11-01). `orders/update_orders.py` was retired; Shopify, eBay and any future channel
  are read, booked and picked by bcweb — `bcweb-server/utils/orderSync.js` (the Update Orders button, and the cron line
  `scripts/order-sync.js` in `crontab.txt`). See `bcweb/docs/order-sync.md`. Don't add an order script here.
- **Google Merchant feed is NOT in this repo** (since 2026-11-08). `merchant-feed/merchant_feed.py` was retired to `archive/merchant-feed/`; the nightly feed is bcweb's `bcweb-server/scripts/merchant-feed.js` (cron line in `crontab.txt`). `merchant-feed/` keeps the descriptions / product-type review scripts, whose approved text and types the bcweb feed reads.
- **`logging_utils.py`**: Centralized logging and database configuration utilities. Lives at root and is imported by ~25 scripts via `sys.path` inserts — do not move it

### Database Schema
PostgreSQL database with key tables:
- `skusummary`: Product master data with cost, pricing, seasonality
- `sales`: Historical sales transactions
- `localstock`: Current inventory levels
- `price_track`: Price history and performance tracking

Tables suffixed `_delete` are retired — soft-deleted, pending a real drop. Never
read from or write to one.

### Configuration
- Environment variables stored in `.env` file (not in repository)
- Database configuration loaded via `logging_utils.get_db_config()`
- Shopify API tokens and Google service account credentials required
- UK timezone handling with automatic BST/GMT switching

### Logging
Centralized logging system:
- Logs stored in `logs/` directory
- Archived logs in `archive_logs/` with 1-day retention
- Each script has dedicated log file with timestamp rotation

## Important Implementation Notes

### Timezone Handling  
System operates in UK timezone with automatic BST/GMT detection:
- Order timestamps converted to UK time
- Performance calculations respect timezone differences
- Use `logging_utils.get_uk_time()` for consistent timestamps

### Database Connections
All scripts use `logging_utils.get_db_config()` for consistent database configuration. Connection parameters loaded from `.env` file with validation.

### Error Handling
Scripts include comprehensive error handling with detailed logging. Check log files in `logs/` directory for troubleshooting.

### Data Quality Caveats

#### NEVER use these fields in analysis queries

- **`skusummary.stockvariants`** — stale, not maintained on any schedule.
- **`skusummary.variants`** — same problem. Also frequently NULL.

These fields are written by the legacy PowerBuilder app only when a record is touched for other reasons. Verified Apr 2026: White Arizona BF Reg had `stockvariants=1` while localstock showed all 8 sizes in stock; the row hadn't been updated in 14 months. Can be wrong in either direction (stale-low or stale-high), and dividing by them produces nonsense like 114% size coverage or NULL-pushed-to-THIN classifications.

**If you find these fields in an existing SQL block, the block is wrong. Rewrite it before running.**

#### How to get size info correctly

| Need | Use |
|------|-----|
| Sizes currently in stock per groupid | `localstock` where `ordernum = '#FREE' AND deleted = 0 AND qty > 0`, `COUNT(DISTINCT code)` |
| Total size universe per groupid (denominator for coverage %) | `skumap` where `deleted = 0`, `COUNT(DISTINCT code) GROUP BY groupid`. **Do NOT use `localstock` for this** — it does not preserve historical empty sizes, so it under-states the universe (e.g. 14-size style may show only 4 codes if 10 sizes are currently out of stock). |
| Per-size stock quantities | `localstock` joined to `skumap` for size labels |

Never reach for `skusummary.variants` or `skusummary.stockvariants` in any query, even if a doc tells you to.

## Shopify Pricing
When asked to work on Shopify pricing ("pricing review", "let's do prices", "shopify price check", or similar), read `shopify-price/STRATEGY.md` first — it's the current strategy, built in stages: segment-first triage (Stage 1, `latest_sales.py`), single-groupid drill-down (Stage 2, `drill.py`), the review-date cooldown (`skusummary.next_shopify_price_review` / `review.py`), and applying a decided price — **in BCWEB** (the Shopify pricing screens / W1, which push to Shopify live; `apply_prices.py` was retired to `archive/shopify-price/` on 2026-11-08 — never write `shopifyprice` directly). Everything starts by filtering to a segment.

## Amazon Pricing
When asked to work on Amazon/FBA pricing ("amazon prices", "full ives review", "full rieker review", or any segment/brand on Amazon), read `amz-price/README.md` first — the front door and coverage map. The engine is brand-neutral and works for **any** segment we sell on Amazon, not just IVES: `AMZ_PRICING.md` (how it works), `AMZ_FULL_REVIEW.md` (the parameterised full-segment pass), `AMZ_PRODUCTS.md` (per-segment economics + state). No segment is "too small to manage" — thin segments sit on a longer cadence, not excluded.

## SEO
**SEO moved to bcweb on 2026-11-07** (owner: "move SEO work into this repo"). The reports are Node scripts in `bcweb-server/scripts/seo/` (`weekly.js`, `queries.js`, `collections.js`, `collection-priorities.js`, `product-priorities.js`, `page-history.js`, `organic-pages.js`, `link-check.js`), the docs (PLAN, README, CHANGELOG, PROGRESS) in bcweb's `docs/seo/`. Work there — read `docs/seo/PLAN.md` first. The Python folder is retired to `archive/seo/` (history only; don't run or extend it — its CHANGELOG / PLAN are frozen at 2026-11-07, the live copies are in bcweb).

## Scale Work
For scale/segment work, read `scale/CLAUDE_CONTEXT.md` first — it contains all context including strategy, Google Sheets access, DB query patterns, and segment naming conventions.

## How this folder is organised

Settled during the Jul 2026 tidy-up. `INDEX.md` is the lookup — one row per
capability, with the front-door doc for each. `python catalogue.py` checks the
index against reality and reports anything that has drifted.

**A folder per capability.** Anything you'd describe in a sentence ("Shopify
order sync", "month-end accounting pack") gets a folder, whether it's one file
or ten. Root holds only shared infrastructure — `logging_utils.py`,
`catalogue.py` — the top-level docs, and the credentials. **A new script does
not go at root.**

**Every capability folder gets a front-door `.md`.** What it does, how to run
it, and the gotchas that would otherwise cost the next person an hour. A
paragraph and a usage line beats nothing. This applies to colleague
contributions too.

**Anchor every path on `__file__`, never the working directory.** Cron runs
with no `cd`, so `os.path.join("logs", ...)` resolves against the invoking
user's home, not the repo. Scripts in a folder reach the root with
`REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`, then
`sys.path.insert(0, REPO_ROOT)` for `logging_utils` and the same for `.env`.
This has bitten twice: pick lists were silently written to `/root/logs` on the
VPS for months.

**Check exit codes in anything unattended.** `pg_backup.sh` ignored `rclone`'s
exit code and printed "Backup complete" for 109 days while nothing reached
Google Drive. If cron runs it, it must fail loudly and exit non-zero.

**Nothing is deleted for being old — it's archived.** `archive/` is a soft
delete: still in git, recovery is one `git mv`. Retired database tables get a
`_delete` suffix rather than a `DROP` (check `pg_depend` and `pg_constraint`
first — views and foreign keys follow a rename silently). Never read from or
write to a `_delete` table.

**Never point a live doc at `archive/`.** Archiving is a soft delete, not a
filing location. If archiving strands a reference, remove the reference or
inline the useful part.

**Never restate a schedule outside `crontab.txt`.** No clock times in
docstrings, READMEs or comments. `crontab.txt` mirrors the VPS, which is
authoritative — re-pull with `ssh root@vps "crontab -l"` before editing.

**Credentials live at the repo root**, beside `.env`: the Google OAuth and
service-account JSONs. All are gitignored, so `git pull` does not deploy them —
they are hand-copied to the VPS. A `secrets/` folder was considered and
rejected: it would only move files from one place git doesn't show to another,
while adding a manual server-side step whose failure mode is a 3am auth error.
`merchant-feed-api-*.json` is also shared by `merchant-feed/` and `scale/`.

**`.gitignore`'s blanket `*.txt` / `*.csv` is deliberate** — those are generated
data files. Be aware a new `.txt` doc will be invisible to git; write docs as
`.md`.

## Two machines — memory does not sync
The user runs Claude Code on two machines (`C:\Users\aandr\` and `C:\Users\UserPC\`). Auto-memory lives under each machine's local `.claude/projects/C--scripts/memory/` and is **not** synced between them — a memory written on one machine is invisible on the other. Treat memory as machine-local context, not global truth. When something is important enough to follow the user across machines, put it in a tracked doc (CLAUDE.md, scale/CLAUDE_CONTEXT.md, amz-price/AMZ_PRICING.md, etc.) — those are in the repo and shared.