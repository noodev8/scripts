# Direct Price Change

How to manually nudge prices outside of the Google Price Check process (Phases 1-3).

## Steps

### 1. Create a CSV

Save a CSV in `google_price/` with these columns:

```
groupid,new_price,description,change
1017721-BEND,95.00,"Existing note. Your new note here",1
0040791-MADRID,59.50,"Existing note. Your new note here",1
```

- **groupid**: the product groupid from skusummary
- **new_price**: the new Shopify price
- **description**: keep the existing note from `price_change_log` and append your reason for the change
- **change**: set to `1` for rows you want to apply, `0` to skip

### 2. Check existing notes

Before writing your CSV, grab the latest notes so you can preserve them:

```sql
SELECT DISTINCT ON (groupid) groupid, reason_notes, new_price, change_date
FROM price_change_log
WHERE groupid IN ('your-groupid-here')
ORDER BY groupid, change_date DESC, id DESC;
```

### 3. Dry run

```bash
python google_price/google_price_apply.py google_price/your_file.csv
```

This shows what would change without touching the database. Check the output looks right.

### 4. Apply

```bash
python google_price/google_price_apply.py google_price/your_file.csv --confirm
```

This updates `skusummary.shopifyprice`, sets `shopifychange=1`, and logs to `price_change_log`. The nightly Shopify sync (`price_update2.py`) pushes changes live.

## Safety

- The script enforces a 10% minimum margin above cost — changes below that floor are blocked automatically.
- Always dry run first to catch any issues.

## Verify

After applying, check in pgAdmin:

```sql
SELECT groupid, shopifyprice, shopifychange
FROM skusummary
WHERE groupid IN ('your-groupid-here');

SELECT groupid, old_price, new_price, reason_notes, change_date
FROM price_change_log
WHERE groupid IN ('your-groupid-here')
ORDER BY change_date DESC, id DESC;
```
