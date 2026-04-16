# Shopify Pricing

The goal is simple: **find the best price for each SKU.** This folder holds the minimum tooling to support that — nothing more.

## How a session works

There's no ritual. A session starts with the user saying what they want to look at — a specific product, recent sales, loss-makers, something flagged by Google, whatever. Claude queries the database live, reads any Google CSVs sitting in the Downloads folder if they're relevant, and we discuss.

**Standing defaults** (unless the user says otherwise):
- Local stock only — FBA is handled separately in `amz-price/`
- Skip anything with a Shopify price change in the last 7 days (check `price_change_log` where `channel='SHP'`) — don't re-churn recent decisions
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
7. **Google opinion** — at the start of every deep-dive, check `C:\Users\UserPC\Downloads\` for the two Google CSVs (`Your most popular products with price benchmarks_*.csv` and `Sale price suggestions with highest performance impact_*.csv`). If either is present and contains rows for the groupid (keyed by per-size Product IDs like `GROUPID-SIZE`), include them as a block: per-size benchmark vs our price and click count from the benchmark file, and per-size suggested price with effectiveness / click uplift / conversion uplift from the sale-price file. If neither file is present, just say so and skip this block — it's a signal, not a blocker.

After these blocks, summarise the read in 3–5 lines and propose a single price move. Don't split into multiple options unless the picture is genuinely ambiguous.

## What's here

| File | Purpose |
|---|---|
| `apply_prices.py` | The only script. Reads a CSV of price changes and writes them to the database. Dry-run by default. |
| `apply-prices.md` | How to use `apply_prices.py` — CSV format, commands, verification SQL. |
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

Two CSVs can be downloaded from Google Merchant Center and dropped in the Downloads folder:

- **Price benchmark** — where our prices sit vs competitors
- **Sale price suggestions (performance)** — Google's view on prices that would drive more volume

They're optional. If they're there, Claude will read them when relevant. If they're not, the session continues using Shopify data only. Neither report is needed to make a decision — they're just one more signal.

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
