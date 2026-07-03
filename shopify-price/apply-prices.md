# Apply Prices

How to apply a batch of Shopify price changes via `apply_prices.py`.

## Steps

### 1. Create a CSV in `staging/`

```
groupid,new_price,review_days,description,change
1017721-BEND,95.00,14, ,1
0040791-MADRID,59.50,7, ,1
```

- **groupid**: product groupid from `skusummary`
- **new_price**: the new Shopify price
- **review_days**: **required on every price change.** Days from today until the style's
  next review — sets `skusummary.nextreviewdate`, which hides it from the Stage 1 triage
  until then. A change row with no valid positive `review_days` is **refused** (skipped with
  a reason), never applied without a cooldown. Pick per decision (e.g. 7 for a raise-probe,
  30 for a healthy "leave it").
- **description**: a note for `price_change_log`. Currently we run **without notes** — leave
  it blank (a single space keeps pandas from writing the literal `nan`). If used, it's the
  reason for *this* change only; don't copy previous notes forward (they're preserved as
  separate rows).
- **change**: `1` to apply, `0` to skip

### 2. Optional — read previous notes for context

Previous notes are kept as their own rows in `price_change_log`; you don't need to copy them forward. Read them if you want context for the decision:

```sql
SELECT change_date, old_price, new_price, reason_notes
FROM price_change_log
WHERE groupid IN ('your-groupid-here')
ORDER BY change_date DESC, id DESC;
```

### 3. Apply

```bash
python shopify-price/apply_prices.py shopify-price/staging/your_file.csv --confirm
```

Always run with `--confirm` — no dry-run-then-wait step. The CSV has already been agreed in conversation; running it is the apply. Updates `skusummary.shopifyprice`, sets `shopifychange=1` and `skusummary.nextreviewdate` (today + `review_days`, parking it out of the triage) in one write, and logs to `price_change_log`. The nightly Shopify sync (`price_update2.py`) pushes changes live.

Only run without `--confirm` if you explicitly want to sanity-check a CSV you didn't build in this session.

### 4. Clean up

Delete the CSV from `staging/` once applied — the database holds the record now.

## Safety

The script enforces nothing — every price is discussed with Claude before it's written. Dry run first if you want to sanity-check the CSV before applying.

## Verify

```sql
SELECT groupid, shopifyprice, shopifychange
FROM skusummary
WHERE groupid IN ('your-groupid-here');

SELECT groupid, old_price, new_price, reason_notes, change_date
FROM price_change_log
WHERE groupid IN ('your-groupid-here')
ORDER BY change_date DESC, id DESC;
```
