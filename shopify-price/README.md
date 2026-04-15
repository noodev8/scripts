# Shopify Pricing

The goal is simple: **find the best price for each SKU.** This folder holds the minimum tooling to support that — nothing more.

## How a session works

There's no ritual. A session starts with the user saying what they want to look at — a specific product, recent sales, loss-makers, something flagged by Google, whatever. Claude queries the database live, reads any Google CSVs sitting in the Downloads folder if they're relevant, and we discuss.

**Standing defaults** (unless the user says otherwise):
- Local stock only — FBA is handled separately in `amz-price/`
- Exclude SKUs with `ignore_auto_price` set

Specific thresholds (how many days, how many sales, etc.) are decided per session — they change depending on what we're hunting for.

Claude keeps a running list of agreed changes in the conversation as we go. At the **end of the session**, Claude writes one CSV to `staging/` containing all the changes and applies it with `apply_prices.py` — no per-change files, no dry runs unless the user asks.

Everything after that lives in the database. The `price_change_log` table is the history — don't keep markdown logs of past sessions.

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
