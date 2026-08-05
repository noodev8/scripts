# Returns

Books Shopify refunds back out of `sales` as negative rows, so unit counts and
profit reflect what customers actually kept.

Replaces the monthly PowerBuilder routine `of_shopifyitemreturn`, which read a
hand-exported `shopify item return.csv` from the Downloads folder. That export
is no longer needed — this reads the Shopify Refunds API directly.

## Run

```
python returns/sync_returns.py                     # rolling 30-day window
python returns/sync_returns.py --since 2026-06-03  # backfill from a date
python returns/sync_returns.py --dry-run           # report, write nothing
```

Scheduled — see `crontab.txt`. Works from any directory; the script anchors on
its own location, not the working directory.

## Why nothing else was already doing this

Worth knowing, because it looks like it should have been covered:

| | Does it handle returns? |
|---|---|
| `orders/update_orders.py` | No. Inserts a positive `sales` row when the order is created, never revisits it. |
| `bcweb-server/utils/orderSync.js` | No. Same insert-only logic. |
| `month-end/month-export.py` | Reads refunds from the Shopify API, but only to build the accountant's CSV. Never writes to the database. |

The sale was synced automatically; the un-sale was a manual monthly job. That
asymmetry is what this script closes.

## What it does

1. Fetches every order **updated** since the window start, with refunds
   attached. Keyed on `updated_at` rather than `created_at` because issuing a
   refund updates the order — that catches a July refund against a March order
   without a lookback window.
2. Flattens each refund into one record per refunded unit-line. Shipping-only
   refunds carry an empty `refund_line_items` and drop out, correctly: no goods
   came back.
3. Resolves `groupid` (`skumap`), title (`title`), brand (`skusummary`).
4. Writes the negative row, with `profit` = the original sale row's per-unit
   profit, negated — so a sale and its return net to ~zero.

**Pagination is followed via the `Link` header.** Don't remove it: a 30-day
window is already ~1,700 orders, which is seven pages. `update_orders.py` still
has the un-paginated version of this bug.

## The guard that matters

A reversal is only written when a **matching positive sale row exists and still
has unreversed units**.

Shopify refunds cover cancellations as well as returns, and `update_orders.py`
skips cancelled orders at insert time — so those orders were never booked as a
sale. Without the guard, a cancelled-before-shipping order books a negative row
against a sale that does not exist, inventing a loss out of nothing.

This is not hypothetical. The PowerBuilder routine had no such check, and there
are **16 such phantom return rows in `sales` today, totalling -£135.34** of
invented loss. The first backfill run skipped exactly 5 more (BC18655, BC18528,
BC18400, BC17936, BC17413 — all `cancel_reason: customer`, all unfulfilled).

The same check nets positive against negative rows, so a second refund against
an already-returned line cannot double-reverse it.

## Idempotency

`source_key` carries `SHP:R:<order>:<refund_line_item_id>` and the insert is
`ON CONFLICT (source_key) DO NOTHING`, against the existing
`uq_sales_source_key` unique index. Re-running any window is free. This is the
same mechanism Amazon imports use (`AMZ:O:<order>:<line>`).

`returnsaleid` also gets the refund line item id, for continuity with the rows
that already carry one.

## Overlap with `db-maint/clean_sales.sql` — deliberate

That script's steps 2–5 repair return rows that arrived with `soldprice = 0`
and recompute return profit weekly. This script writes a real price and profit
up front, so:

- steps 2–4 are no-ops for these rows (`soldprice > 0`), and
- step 5 is a self-healing backstop that normalises profit to the same formula.

Don't "fix" the duplication by removing either side. Step 5 recomputes from the
**current** `skusummary.cost`, so it can drift from the cost at time of sale —
pre-existing behaviour, and the reason this script reverses the original row
rather than recomputing.

Note: `clean_sales.sql`'s step 5 comment cites `bcweb docs/profit-model.md` and
`bcweb-server/utils/profit.js` as the source of truth. Neither file has ever
existed — the real paths are `orders/update_orders.py` `shopify_profit()` and
`bcweb-server/utils/shopifyProfit.js`.

## The refund haircut stays

The profit model's `/1.2` is a flat "cover refunds" cushion, and it is left in
deliberately — it keeps pricing viable when trading is hard. Return rows reverse
the original row's profit, so the haircut carries through unchanged rather than
being unwound.

The consequence, stated plainly so nobody rediscovers it as a bug: refunds are
charged to profit twice — once via the blanket haircut on every sale, and again
as the actual reversal. That is a margin-safety choice, not an accounting one.

## What it does not do

- **No stock movement.** The PowerBuilder routine never restocked either.
  A returned pair reaching the shelf is a physical goods-in decision.
- **Nothing for Amazon.** Amazon returns arrive through
  `bcweb-server/utils/amzImportApply.js`.
