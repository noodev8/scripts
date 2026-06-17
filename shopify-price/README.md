# Shopify Pricing

The goal is simple: **find the best price for each SKU.** This folder holds the minimum tooling to support that — nothing more.

## How a session works

There's no ritual. A session starts with the user saying what they want to look at — a specific product, recent sales, loss-makers, something flagged by Google, whatever. Claude queries the database live, reads any Google CSVs sitting in the Downloads folder if they're relevant, and we discuss.

**Standing defaults** (unless the user says otherwise):
- Local stock only — FBA is handled separately in `amz-price/`
- **Birkenstock never goes to Amazon FBA** — it's not allowed. Don't suggest FBA as a remedy for slow-moving Birkenstock lines.

> The `ignore_auto_price` flag on `skusummary` is **legacy and no longer used anywhere**. Do not filter on it in any session.

Specific thresholds (how many days, how many sales, etc.) are decided per session — they change depending on what we're hunting for.

Claude keeps a running list of agreed changes in the conversation as we go. At the **end of the session**, Claude writes one CSV to `staging/` containing all the changes and applies it with `apply_prices.py` — no per-change files, no dry runs unless the user asks.

Everything after that lives in the database. The `price_change_log` table is the history — don't keep markdown logs of past sessions.

## GroupID deep-dive

When the user names a specific groupid and wants to decide a price, produce all of the blocks below before recommending anything. They should appear roughly in this order and each one should be a tight table — no prose between them unless a pattern jumps out. One groupid at a time, never batched.

1. **Header** — `skusummary` row: colour, width, season, current `shopifyprice`, `cost`, `rrp`, `minshopifyprice`, `maxshopifyprice`. Shows the bounds the decision has to live inside.
2. **Weekly grid, last ~14 weeks** — one row per ISO week: week start, list price at end of week (from `price_change_log` latest `new_price` on or before the week), units sold (`sales` channel='SHP'), avg sold price. Exposes the most recent trajectory and any current stall.
3. **YoY same-period grid** — same shape as (2), but for the matching calendar weeks of the previous year. Lets us see whether a quiet patch is seasonal noise or a real change. Note: `price_change_log` may not cover periods older than ~9 months, so list price for older weeks often has to be inferred from `avg_sold`.
4. **Price change log** — every `price_change_log` row for the groupid where `channel='SHP'`, with `change_date`, `old_price`, `new_price`, `reason_code`, `reason_notes`. The notes explain past reasoning and are usually the most informative block on this page.
5. **Stock by size** — pivot from `localstock` (`COALESCE(deleted,0)=0`, `qty>0`), grouped by the size suffix of `code`. Shows whether a size curve gap is secretly blocking sales.
6. **Incoming history** — `incoming_stock` rows for the groupid, newest first: `arrival_date`, `code`, `quantity_added`. Tells us when the current pile actually landed — fresh stock behaves differently to stock that's been sitting through the season.
7. **Google opinion** — at the start of every deep-dive, run `python shopify-price/refresh_google_csvs.py` to pull any fresh Google Merchant CSVs out of Downloads into this folder (it keeps only the latest of each type). Then read the two CSVs from `shopify-price/`: `Your most popular products with price benchmarks_*.csv` and `Sale price suggestions with highest performance impact_*.csv`. If either contains rows for the groupid (keyed by per-size Product IDs like `GROUPID-SIZE`), include them as a block: per-size benchmark vs our price and click count from the benchmark file, and per-size suggested price with effectiveness / click uplift / conversion uplift from the sale-price file. If neither file has matches, just say so and skip this block — it's a signal, not a blocker. Note the file date when citing — a benchmark from 8 weeks ago is weaker evidence than one from yesterday.

After these blocks, summarise the read in 3–5 lines and propose a single price move. Don't split into multiple options unless the picture is genuinely ambiguous.

## Portfolio scan (whole-catalogue competitive view)

The deep-dive above is per-groupid. When the question is *"how do our prices sit as a whole vs the market?"* — usually triggered by Google Ads showing we're losing to competition — use `portfolio_scan.py` instead. It rolls both Google CSVs up to groupid level and joins them to the live DB, so you get one screen across the catalogue rather than going product-by-product.

It reads the **two Google docs together**, because they do different jobs:

- **Benchmark doc** (`Your most popular products with price benchmarks`) — where our price sits vs Google's competitive benchmark. The diagnostic. `gap%` **> 0 = we're above benchmark** (pricier than the field); **< 0 = cheaper**.
- **Sale-price suggestions doc** (`...highest performance impact`) — Google's *aggressive* "cut to here and you'll move volume" price, with an Effectiveness rating (High/Medium/Low). The provocation. **Take with a pinch of salt** — it optimises clicks/conversions, not our margin — but it's directionally useful and shows up as `gSugg`/`cut%`/`eff`.

Join key: Google `Product ID` == `skumap.googleid` (exact match, no normalisation). `clk` is click-weighted so the rollup reflects where traffic actually is. `net%` is net margin at the current price using the cost constants below; the saved CSV also has net margin at Google's suggested price, so you can see the profit cost of chasing the aggressive number.

```
python shopify-price/refresh_google_csvs.py     # pull latest CSVs first
python shopify-price/portfolio_scan.py          # default: OVER-benchmark + high clicks (the bleed list)
python shopify-price/portfolio_scan.py --under  # UNDER benchmark (margin possibly left on the table)
python shopify-price/portfolio_scan.py --all --min-clicks 0   # everything
```

The default lens is the "losing to competition" list: priced above benchmark, sorted by clicks. If that lens comes back nearly empty, that's a real result — it means price competitiveness is *not* the problem and the Ads symptom is coming from somewhere else (rank/budget/impression share). The full per-groupid table is always written to `portfolio_scan_<date>.csv` (gitignored) for drill-down. Anything the scan flags is then a candidate for the per-groupid deep-dive above.

## What's here

| File | Purpose |
|---|---|
| `apply_prices.py` | Reads a CSV of price changes and writes them to the database. Dry-run by default. |
| `apply-prices.md` | How to use `apply_prices.py` — CSV format, commands, verification SQL. |
| `refresh_google_csvs.py` | Pulls fresh Google Merchant CSVs from Downloads into this folder; keeps only the latest of each type. |
| `portfolio_scan.py` | Whole-catalogue competitive triage: both Google CSVs rolled up to groupid, joined to live DB. |
| `staging/` | Where CSVs of pending changes live before they're applied. Delete them once applied. |
| `README.md` | This file. |

| File | Purpose |
|---|---|
| `apply_prices.py` | Reads a CSV of price changes and writes them to the database. Dry-run by default. |
| `apply-prices.md` | How to use `apply_prices.py` — CSV format, commands, verification SQL. |
| `refresh_google_csvs.py` | Pulls fresh Google Merchant CSVs from Downloads into this folder; keeps only the latest of each type. |
| `staging/` | Where CSVs of pending changes live before they're applied. Delete them once applied. |
| `README.md` | This file. |

## Data sources (all live, all in the DB)

| Table | What it tells us |
|---|---|
| `sales` (channel='SHP') | What actually sold, at what price, when |
| `skusummary` | Current price, cost, RRP, season, min/max bounds, ignore flag |
| `localstock` | Warehouse stock by size |
| `amzfeed` | FBA stock |
| `price_change_log` | Every Shopify price change with reason notes and date |
| `incoming_stock` | Historical stock arrivals — when each size actually landed |
| `birktracker` | Incoming stock (requested but not yet arrived) |

## Google reports (optional context)

Two CSVs can be downloaded from Google Merchant Center:

- **Price benchmark** — where our prices sit vs competitors
- **Sale price suggestions (performance)** — Google's view on prices that would drive more volume

Workflow: download whenever you want fresh data (lands in Downloads). At the start of any deep-dive Claude runs `refresh_google_csvs.py`, which moves the newest copy of each type into `shopify-price/` and deletes older same-type files so we keep only the latest. The CSVs are `.gitignore`d so they never enter the repo.

They're optional. If neither file has matches for the groupid, the session continues using Shopify data only.

## Cost constants (for net profit calculations)

| Cost | Value |
|---|---|
| Payment fee | £0.30 + 2.9% of price |
| VAT | price / 6 (when `tax = 1`) |
| Wages/packing | £1.00 per unit |
| Postage | £3.44 per unit |

```
net_profit = soldprice - vat - cost - payment_fee - wages - postage
```
