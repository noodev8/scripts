# Apply Prices

How to apply a batch of Shopify price changes via `apply_prices.py`.

## Steps

### 1. Create a CSV in `staging/`

```
groupid,new_price,description,change
1017721-BEND,95.00,"Existing note. Your new note here",1
0040791-MADRID,59.50,"Existing note. Your new note here",1
```

- **groupid**: product groupid from `skusummary`
- **new_price**: the new Shopify price
- **description**: keep the existing note from `price_change_log` and append your reason for the change
- **change**: `1` to apply, `0` to skip (rows with `0` can still carry a description forward as a note-only entry)

### 2. Check existing notes first

So you can preserve them:

```sql
SELECT DISTINCT ON (groupid) groupid, reason_notes, new_price, change_date
FROM price_change_log
WHERE groupid IN ('your-groupid-here')
ORDER BY groupid, change_date DESC, id DESC;
```

### 3. Dry run

```bash
python shopify-price/apply_prices.py shopify-price/staging/your_file.csv
```

Shows what would change without touching the database.

### 4. Apply

```bash
python shopify-price/apply_prices.py shopify-price/staging/your_file.csv --confirm
```

Updates `skusummary.shopifyprice`, sets `shopifychange=1`, and logs to `price_change_log`. The nightly Shopify sync (`price_update2.py`) pushes changes live.

### 5. Clean up

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
