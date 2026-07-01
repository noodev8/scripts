# New Product Loader — Project Handoff Spec

> Self-contained brief for the agent building the standalone Amazon new-product loader.
> Everything decided with the owner is captured here. This file lives in `C:\scripts\amz-product\`
> for now — **move it into the new app's own repo/folder** when you scaffold the project.

---

## 1. Purpose & scope

Load **new products into the database quickly, for Amazon**, replacing the slow PowerBuilder
(PB) data-entry path for this one job. Shopify-specific data is **not** captured here — it is
loaded later (back in PB or a future Shopify step).

Hard constraints / decisions already made:

- **Throwaway, standalone Python app.** Streamlit. Single file is fine. Its **own repo/folder**,
  not bolted onto the existing `C:\scripts` codebase. This is *not* the eventual PowerBuilder
  migration — it's a fast utility to buy time until volume justifies the bigger investment.
- **Amazon-only, established-listings-only.** We only load products **Amazon already lists**.
  Amazon matches our offer to an existing ASIN **by EAN**, and supplies the title, images,
  bullets and dimensions itself. So the loader does **not** need title/description/dimensions.
  The EAN is the single most important field.
- **Run locally first**, then move to the VPS (`77.68.13.150`, browser access for the office team) later.
- The loader **writes the DB rows + one image**. It does **not** push to Amazon. The existing,
  unchanged `amz_upload.py` remains the separate next step (see §7).

---

## 2. What the loader does, end to end

1. Operator fills a form: header fields (one per product/colour) + a size grid (one row per size).
2. Operator uploads **one image**.
3. On submit, inside one DB transaction:
   - Insert **one `skusummary` row** (PB-mirrored defaults — §4).
   - Insert **N `skumap` rows**, one per size (PB-mirrored defaults — §5).
4. Process the image: resize to **800×800**, save as **`{groupid}.jpg`** locally; SFTP to the image
   server and Google Drive copy are **stubbed placeholders for now** (creds come later) — §6.
5. Insert **one `title` row** (`shopifytitle = groupid`) — §9.
6. Operator then runs `amz_upload.py` as today (§7).

---

## 3. Minimum data the operator enters

### Header (per groupid / colour)
| Field | Required | Notes |
|---|---|---|
| groupid | ✅ | Upper-cased. Validate it does **not** already exist in `skusummary`. |
| brand | ✅ | Offer as dropdown of existing `skusummary.brand` values + free-text. |
| rrp | ✅ | Numeric > 0. Used as Amazon list price *and* your price by `amz_upload.py`. |
| cost | ✅ | Numeric > 0. Not needed to *list*, but painful to backfill — capture now. |
| colour | ✅ | |
| season | ✅ | Summer / Winter / Any. |
| tax | ✅ | Integer 0/1. Default **1** (most adult shoes are standard-VAT). Confirm per product. |

Optional header: `regular_groupid` / `narrow_groupid` (Birkenstock width pairing only — blank otherwise).

### Size grid (one row per size)
| Field | Required | Notes |
|---|---|---|
| euro size | ✅ | Drives the code: `code = {groupid}-{eurosize}` (e.g. `CASSIS-GOLD-38`). |
| size label | ✅ | The display string, e.g. `5 UK / 38 EU` (becomes part of `optionsize`). |
| uksize | ✅ | e.g. `5 UK`. |
| ean | ✅ | **The ASIN match key.** Numeric barcode, no `B` suffix (loader appends `B` — see §5). |
| cost | ✅ | Per-size cost (PB requires it; usually same across sizes). |
| barcode2 | ⬜ | Optional second barcode → `search2`. Blank for almost everything. |

Validation to mirror from PB: no spaces / `< >` in code; code not ending in `-`; no duplicate
code or barcode within the grid; rrp ≥ cost; size/uksize not blank or just "UK".

---

## 4. `skusummary` INSERT — PB-mirrored defaults (NEW path)

Mirror PB's new-product insert, with the deliberate deviations called out.

| Column | Value | Source / note |
|---|---|---|
| groupid | `UPPER(groupid)` | operator |
| created | now `YYYYMMDD HH:MM:SS` | timestamp |
| updated | now | timestamp |
| brand | brand | operator |
| colour | colour | operator |
| colourmap | colour | **same as colour** |
| supplier | brand→supplier lookup, else brand | see note ↓ |
| rrp | `format(rrp,'0.00')` | operator |
| cost | `format(cost,'0.00')` | operator |
| shopifyprice | `format(rrp,'0.00')` | PB defaults to rrp; harmless (shopify=0) |
| minshopifyprice | `0.00` | PB default |
| maxshopifyprice | `"RRP"` | **literal string `RRP`**, not a number |
| season | season | operator |
| tax | tax | operator. **Default 1** (standard VAT). Keep simple — no kids/zero-VAT logic; if a zero-VAT product is ever loaded the operator switches tax to 0 manually. |
| imagename | **`{groupid}.jpg`** | ⚠️ DEVIATION — PB uses operator filename; we standardise |
| shopify | **`0`** | ⚠️ DEVIATION — PB reads a checkbox; we force 0 (Amazon-only, Shopify later) |
| googlestatus | `1` | **PB default is 1** (see §8 reconciliation) |
| googlecampaign | `"standard"` | PB default |
| handle | `""` (empty) | ⚠️ DEVIATION — PB derives from title; deferred to Shopify enablement step (must be set then) |
| regular_groupid | birkregular or `""` | operator (Birk only) |
| narrow_groupid | birknarrow or `""` | operator (Birk only) |
| custom_label_0 | `"L4"` **only if** `UPPER(brand)='CROCS'` | PB special case |

**Supplier lookup:** PB maps brand→supplier from a brand reference list. There is no clean brand
table to rely on; simplest is `SELECT DISTINCT supplier FROM skusummary WHERE brand = :brand`
(take the most common), falling back to `supplier = brand`. Offer an override field.

---

## 5. `skumap` INSERT — PB-mirrored defaults (NEW path), one row per size

| Column | Value | Note |
|---|---|---|
| updated | now | |
| sku | `""` (empty) | **Leave blank** — `amz_upload.py` generates `code-YYMM` and writes it back |
| groupid | `UPPER(groupid)` | |
| code | `{groupid}-{eurosize}` | from grid |
| googleid | = code | **same as code** |
| optionsize | `str(100+rownum) + "--" + sizelabel` | e.g. row 1 → `101--5 UK / 38 EU`. Sequential by grid order. |
| uksize | uksize | from grid |
| ean | ean + `"B"` | ⚠️ **append literal `B`** (PB convention; `amz_upload.py` strips it). Blank stays blank. |
| search2 | barcode2 + `"B"` if present, else `""` | optional second barcode |
| supplier | = summary supplier | |
| cost | `format(cost,'0.00')` | |
| fba | `"2.24"` | PB reads `avgfbafee` from `brookfield.ini` (default 2.24). Make it a config constant. |
| amzprice | `format(rrp,'0.00')` | |
| amzmaxprice | `format(rrp,'0.00')` | |
| amzminprice | `format(rrp*0.20,'0.00')` | ⚠️ PB NEW path uses **0.20×rrp** (its update-path uses 0.70×). Looks loose vs the £35.99 soft floor — **confirm with owner**; mirror 0.20 unless told otherwise. |
| deleted | `0` | |
| googlestatus | `1` | PB default |
| googlecampaign | `"00"` | PB default (note: `"00"`, not `"standard"`) |
| status | `"0"` | PB NEW path uses `"0"`; `amz_upload.py` flips to `"1"` on upload |
| pricestatus | `0` | |
| amzperformance | `0` | |
| amz365 | `0` | |
| shp365 | `0` | |

---

## 6. Image pipeline

- Input: one uploaded image per product.
- Process: resize to **800×800** by **pad-on-white** (resize longest side, centre on an 800×800
  white canvas — keeps the whole product visible). Use Pillow. Save as **`{groupid}.jpg`** (JPEG).
- **Save locally** to a configurable output folder — this part works now.
- **SFTP upload and Google Drive copy are PLACEHOLDERS for the first build.** Creds come later.
  Implement them as clearly-marked stub functions (e.g. `upload_to_image_server(path)` /
  `copy_to_drive(path)`) that log "TODO: not yet configured" and no-op, so the rest of the flow
  runs end-to-end without them. Wire them up once the owner provides creds.
- When implemented:
  - **SFTP to the image server** that serves `https://images.brookfieldcomfort.com/{imagename}`
    (the "cone.com" host). `merchant_feed.py` only *references* this URL — it does **not** upload —
    so these credentials are **not yet in the repo**. Will need:
    `IMAGE_SFTP_HOST / PORT / USER / PASSWORD / REMOTE_PATH`.
  - **Copy to the Google Drive folder** the front-end reads (for eyeballing which product is which).
    A Google service-account JSON already exists in the main repo
    (`merchant-feed-api-462809-23c712978791.json`); reuse that pattern. Will need the **Drive folder ID**.
- The image is for human identification only — Amazon does not need it.

Reuse-from-existing-code pointers: `paramiko` SFTP usage in `C:\scripts\merchant-feed\merchant_feed.py`
(`upload_*` function ~line 244); DB config pattern via `logging_utils.get_db_config()` (this app is
standalone, so copy the connection approach rather than importing).

---

## 7. Hand-off to `amz_upload.py` (unchanged, separate step)

After rows + image are in, the operator runs the existing flow (`C:\scripts\amz-product\amz_upload.py`):
1. Put the new groupid(s) in `groupids.txt`.
2. `python amz_upload.py` → reads `skusummary` (brand, rrp) + `skumap` (code, ean), generates the
   SKU (`code-YYMM`) if blank, sets `skumap.status='1'`, and produces `AMZ-Upload.xlsm`.
3. Upload that Excel via Seller Central; convert to FBA manually if wanted.

The loader must therefore leave `skumap.sku` blank and `status='0'` so `amz_upload.py` behaves
exactly as it does for PB-created products. **Do not** duplicate the Amazon-upload logic in the
new app.

---

## 8. Inertness reconciliation (important)

Earlier in design we said "write `shopify=0` and `googlestatus=0`" to keep a bare Amazon row out
of the Shopify/Google feeds. The PB script shows the real default is **`googlestatus=1`**. Resolution:

- The **master switch is `shopify`**, not `googlestatus`. Both Google and Shopify outputs gate on
  `shopify=1`:
  - Merchant/Google feed (`merchant_feed.py`): `WHERE googlestatus=1 AND shopify=1 AND m.googlestatus=1`
  - Shopify price sync (`price_update.py`): `WHERE shopify=1`
- So with **`shopify=0`**, the product is inert to both feeds **regardless** of `googlestatus`.
- Therefore we **mirror PB (`googlestatus=1`)** and rely on `shopify=0` for inertness. This avoids
  diverging from PB-created rows. If the owner prefers belt-and-braces, `googlestatus=0` is also safe
  — flag it, don't silently choose.

`amz_upload.py` is independent of these flags (keys off EAN + the `amzfeed` table), so Amazon
visibility is unaffected.

---

## 9. `title` table INSERT (done here) + what's deferred

### `title` row — **created by the loader**, using groupid as a placeholder title
| Column | Value | Note |
|---|---|---|
| groupid | `UPPER(groupid)` | |
| updated | now | |
| shopifytitle | **`groupid`** | placeholder — real title set later by the standard Shopify process |
| googletitle | **`groupid`** | same |
| googletitleb | `"-"` | PB default |

(`last_shopify_sync` left null/unset.)

### Deferred to the standard Shopify process (loader does NOT write these)
- **`attributes` table** (`groupid`, `updated`, `gender`, `producttype`, `tag1`..`tag10`) — left
  entirely to the current standard Shopify process.
- **`skusummary.handle`** — PB derives a URL slug from the real title (lowercased, non-`[0-9a-z-]`→`-`,
  collapse `--`, uniqueness-checked). Left empty now; the Shopify enablement step must set it when
  `shopify` flips to 1, alongside the real title and attributes.

---

## 10. Config the new app needs (collect from owner)

- DB: host/port/name/user/password (same Postgres as `C:\scripts\.env`).
- Image server SFTP: `IMAGE_SFTP_HOST / PORT / USER / PASSWORD / REMOTE_PATH`.
- Google Drive: service-account JSON + target **folder ID**.
- `AVG_FBA_FEE` constant (default `2.24`).
- `amzminprice` multiplier = **0.20** (confirmed — keep it low).

## 11. Decisions locked (previously open)
1. Image resize: **pad-on-white** to 800×800. ✅
2. `amzminprice` = **0.20×rrp** — keep low, confirmed. ✅
3. `tax` default = **1** (standard VAT). No kids/zero-VAT handling; switch to 0 manually if ever needed. ✅
4. `title` row **is created now** with `shopifytitle = googletitle = groupid` (placeholder).
   `attributes` left to the standard Shopify process. ✅
5. Image SFTP + Drive copy = **placeholder stubs** in the first build; local save works. Creds later. ✅
