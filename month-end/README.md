# Month-End

The month-end accounting pack. One command produces everything the accounts need
for a given month.

Run on demand; nothing scheduled.

## Run

```
python month-end/month-export.py           # last month
python month-end/month-export.py 2026-03   # a specific month
```

That's the only entry point you normally need — it calls the other two scripts
itself.

## What you get

1. **`Shopify Transaction.csv` in Downloads** — matches the Shopify Admin
   *Analytics → Reports → Shopify Transaction* export, rebuilt from the Orders
   API.
2. **Shopify Payments + PayPal fee totals**, printed to console.
3. **Current stock position** — units and cost value, printed to console.

## The three scripts

| Script | Does |
|---|---|
| `month-export.py` | The entry point. Builds the transaction CSV, then calls the other two |
| `shopify_fees.py` | Shopify Payments fees via the Balance Transactions API, plus PayPal fees |
| `stock_position.py` | `#FREE` local stock + Amazon `amztotal`, valued at groupid cost |

Each also runs standalone (`python month-end/shopify_fees.py 2026-03`) if you only
want one part.

## PayPal fees — the manual step

`shopify_fees.py` only reports PayPal fees if a file named **exactly
`Download.CSV`** (the raw PayPal transaction export) is sitting in your Downloads
folder. Export it from PayPal first.

After processing it's renamed to `Download-done.CSV`, so a second run won't
double-count — and won't find it either. If you need to re-run, rename it back.

With no such file, the report prints *"PayPal fees not available in the results"*
and carries on. That's the failure mode to watch: the run looks fine and the
PayPal number is simply absent.

## Requirements

- `SHOPIFY_ACCESS_TOKEN` in the root `.env`, with the
  `read_shopify_payments_payouts` scope — without it the fees call fails while
  the rest still works.
- Database access via `logging_utils.get_db_config()` for the stock position.

All three reach back to the repo root for `logging_utils` and `.env` via a
`sys.path` insert. They must stay in the same folder as each other —
`month-export.py` imports the other two as siblings.
