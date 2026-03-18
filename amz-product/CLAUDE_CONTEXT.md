# Amazon Product Upload - Context

## What this does
Generates an Excel file (AMZ-Upload.xlsm) for uploading products to Amazon Seller Central.
Amazon requires the SHOES.xlsm category template format — flat file (.txt) uploads use the
old Inventory Loader parser which doesn't support product-level fields like brand.

## How it works
1. Operator puts GROUPID(s) in `groupids.txt` (one per line)
2. Runs `python amz_upload.py`
3. Script reads from database (skusummary for brand/rrp, skumap for variants/EANs)
4. Copies `SHOES.xlsm` template → `AMZ-Upload.xlsm` with data injected
5. Operator uploads `AMZ-Upload.xlsm` via Amazon Seller Central

## Upload path in Seller Central
Upload via the page that shows "Accepted file formats: Excel, TSV" with File Type
dropdown. NOT the "Add Products via Upload" catalogue page — same upload page that
accepts Inventory Loader files, but choosing the Excel format.

## Why not flat file?
Amazon's flat file upload uses the Inventory Loader parser which only recognises old-style
column headers (sku, price, item-condition). The new template uses API-style attribute names
(contribution_sku#1.value, etc). The Inventory Loader rejects these. The Excel (.xlsm)
upload works because the template contains embedded settings that tell Amazon which parser
to use.

## Template columns (SHOES.xlsm)
| Excel Col | Index (0-based) | Field | Value |
|-----------|----------------|-------|-------|
| A | 0 | SKU | From skumap.sku or generated (code-YYMM) |
| B | 1 | Product Type | Always `SHOES` |
| C | 2 | Listing Action | Always `partial_update` |
| H | 7 | Brand Name | From skusummary.brand |
| I | 8 | Product Id Type | Always `EAN` |
| J | 9 | Product Id | From skumap.ean (B suffix stripped) |
| FL | 167 | Item Condition | Always `New` |
| FN | 169 | List Price with Tax | From skusummary.rrp |
| GK | 192 | Fulfillment Channel Code (UK) | Always `AMAZON_EU` |
| GP | 197 | Your Price GBP (Sell on Amazon, UK) | Set to RRP |

Data rows start at **row 7** in the Template sheet (rows 1-6 are settings/headers/examples).

## SKU generation logic
- If `skumap.sku` is populated → use it as-is
- If empty → generate from `skumap.code` + `-YYMM` (current year+month)

## EAN handling
skumap.ean has a trailing `B` suffix (for Excel display). Script strips it.

## Database tables
- **skusummary**: One row per GROUPID (colour of a style). Has `brand`, `rrp`.
- **skumap**: One row per size variant. Has `sku`, `code`, `ean`, `groupid`. Filter `deleted = 0`.
- Join on `groupid`.

## Key discovery (March 2026)
Amazon is migrating templates. Old Inventory Loader format still works for basic offer
creation but cannot set `brand`. The SHOES category template (.xlsm) with `partial_update`
listing action successfully sets brand and price on existing ASINs (tested 5/5 success,
zero errors).
