# Order Status Process

> Internal technical reference. End-to-end supplier-restock lifecycle:
> **order placed → delivered → goods in → marked off**, plus **non-delivery
> handling** and the **goods-in scan decision logic**.
>
> Emphasis: interfaces, decision logic, timings.
>
> Every fact below is verified against source: the Python cron scripts in this repo
> and the PowerBuilder (PB) `of_scan` / goods-in-save / Amazon-pick handlers.

---

## 0. The core problem this documents

`orderstatus` is **one table doing three unrelated jobs**, keyed only by
`(ordernum, shopifysku)` and disambiguated *solely* by `ordertype`. It is not an
order ledger — it is a **transient work queue** that gets purged on timers. That is
why "did that restock ever arrive?" has no durable answer *in this table*.

| type | domain | direction | created by | how it ends |
|------|--------|-----------|------------|-------------|
| **1** | customer fulfilment | outbound → customer | `update_orders2.py` (Shopify sync) | archived when it leaves Shopify |
| **2** | inbound goods-in | supplier → local shelf | PB order screen, **1 row per unit** | goods-in scan → 30d purge |
| **3** | inbound goods-in | supplier → Amazon (C3-Amazon) | PB order screen, **1 row per unit** | goods-in scan → 7d purge after arrival |
| **5** | internal transfer *(LEGACY, dormant)* | local → Amazon | hidden PB button (uses `qty`) | never checked off → 30d purge |
| 6 | PFG pick *(dead, commented out)* | — | — | — |
| 0 | *not persisted* — transient scan-row class for "unmatched" | — | — | — |

Different keying conventions (per-unit vs aggregate `qty`), different creators,
different end-of-life rules — three queues sharing one shape.

### `qty` is a red herring (with one exception)
Types **2 and 3 write one row per physical unit** and ignore `qty`. Four units
ordered = four rows. `qty` is only meaningful on **legacy type-5** rows (aggregate
picked count). Never trust `orderstatus.qty` for inbound restocks.

---

## 1. Actors & interfaces

| Actor | Role | Interface |
|-------|------|-----------|
| Supplier | Fulfils (or doesn't) a restock | physical delivery only — no data link |
| PowerBuilder app | Places restock rows, runs goods-in scanning, "Amazon Total on order" report | direct DB writes to `orderstatus`, `localstock`, `incoming_stock`, `bclog`, `skumap` |
| `update_orders2.py` (~8×/day) | Syncs Shopify customer orders; runs the purges | INSERT type-1 rows; DELETE purges |
| `clean_sales.py` (Mon 03:00) | Weekly maintenance / purges | runs `database/clean_sales.sql` |
| Goods-in operator | Scans arriving units | PB goods-in screen |

### Tables and their durability
| Table | Meaning | Retention |
|-------|---------|-----------|
| `orderstatus` | **transient** work queue (types 1/2/3/5) | ~7–30 days |
| `stockorder` | **"what we ordered"** — durable ordered record | 365 days |
| `incoming_stock` | **"what actually arrived"** — append-only, 1 row/unit | 3 years (see §5) |
| `localstock` | physical free/allocated stock ledger | soft-delete then swept |
| `orderstatus_archive` | fulfilled customer orders | 365 days |
| `bclog` | goods-in activity log ('Goods In' section) | 180 days |

**Key architectural fact:** the truth of "ordered vs received" lives in
`stockorder` + `incoming_stock` (both durable). `orderstatus` — the thing PB and
operators actually watch — is the transient one.

### localstock allocation semantics
Allocation is carried on the localstock row, not in a separate order:
- `ordernum`: `#FREE` (free stock) · `BC…` (customer pick) · `AMZ-P…` (legacy Amazon pick)
- `allocated`: `amz` (bound for Amazon) · `unallocated` (general local)
- `location`: e.g. `C3-Amazon`, or the operator-selected shelf

Goods-in type-3 sets `allocated = amz` **directly at receipt** — this is what
superseded the legacy type-5 Amazon-pick button.

---

## 2. Happy path — restock ordered → arrives → marked off

1. **Order placed.** PB order screen writes **one `orderstatus` row per unit**
   (`ordertype = 2` local, or `3` Amazon; `arrived = 0`; supplier set) and the
   ordered record into `stockorder`. Type-3 rows now count toward PB's
   **"Amazon Total on order"** report → suppresses duplicate reorders while stock
   is "on the way."
2. **Supplier ships; box arrives.**
3. **Scan — `of_scan()`** (PB), per unit:
   - `wf_scan(value)` resolves barcode/FNSKU/SKU → `skumap.code`; no match → error row, stop.
   - Match priority (first hit wins), on `shopifysku = code AND arrived = 0`:
     - **`ordertype = 3` (Amazon)** → set `arrived=1`, `arriveddate=today`; if
       `ii_amazondirect=1`, push to Amazon check-in label so operator packs for FBA.
     - **`ordertype = 2` (local)** → set `arrived=1`, `arriveddate=today`.
     - **no match** → scan-row `ordertype = 0` (falls through to local at save).
   - *(The customer/type-1 block is commented out — goods-in no longer touches
     customer picks; `update_orders2.py` pick allocation handles those.)*
   - `arrived` is flipped **in the in-memory datastore**; committed to DB later by
     `wf_update_orderstatus` (a plain datawindow save).
4. **Save — goods-in-save** (PB), one `dbsaved=0` scan row per call, always **qty 1**:

   | scan `ordertype` | localstock write | `location` | `allocated` | `incoming_stock.target` |
   |---|---|---|---|---|
   | 1 (customer) | none (pick already aligned) | — | — | `Pick` |
   | 3 (Amazon) | insert `#FREE` | `C3-Amazon` | `amz` | `C3-Amazon` |
   | 2 or 0 (local/unmatched) | insert `#FREE` | operator dropdown | `unallocated` | that location |

   Then **always**: `INSERT incoming_stock` (qty 1, target, workstation) +
   `INSERT bclog` "Goods In {code} to {target}".
5. **Marked off.** 7 days after arrival, `update_orders2.py` purges the received row:
   `DELETE ... ordertype=3 AND arrived=1 AND arriveddate < CURRENT_DATE - 7d`.
   (7-day reconciliation window; replaced an old *instant* delete that erased the
   trail on receipt — the root cause of the historic #FREE-leak incident.)

---

## 3. Goods-in decision tree (scan + save)

```
scan value → UPPER, ignore blank → any error row? → block
  └─ wf_scan()  resolve barcode/FNSKU/SKU → skumap.code   (no match → error, stop)
       └─ match arrived=0 …
            ├─ ordertype=3 (AMAZON)  → arrived=1 → SAVE: localstock #FREE @C3-Amazon, allocated=amz
            │                                       + Amazon label if amazondirect
            ├─ ordertype=2 (LOCAL)   → arrived=1 → SAVE: localstock #FREE @operator-location, unallocated
            └─ no match (type 0)     →            SAVE: localstock #FREE @operator-location, unallocated
       … every branch also → INSERT incoming_stock (qty 1) + INSERT bclog 'Goods In'
```

### Two edges that fall out of this
- **Amazon-after-purge downgrade.** If a type-3 row was purged (>30d) *before* a late
  delivery, the scan finds no match → the unit is saved as `unallocated` local, **not**
  `C3-Amazon`/`amz`. Stock is banked; the FBA intent is silently lost. (This is exactly
  the #FREE-leak failure mode, now precisely located.)
- **Partials can't show in `orderstatus`.** `arrived` is a binary flag flipped on the
  *first* unit scanned. Order 4, receive 3 → the row still reads "arrived." The accurate
  count lives in `incoming_stock` (one row per unit received), never in `orderstatus`.

---

## 4. Non-delivery — *"we ordered a restock and it didn't arrive (supplier OOS)"*

1. Row sits `arrived = 0` forever — **no scan ever happens.**
2. While it sits, a type-3 row **inflates PB's "Amazon Total on order"** →
   **actively suppresses a reorder** (you see stock "incoming" and skip re-ordering
   something that's never coming).
3. Early warning is **manual only**: `database/stuck_supplier_orders.sql`, run ad-hoc,
   flags the **12–30 day** window as `STALE` (>12d) / `LATE` (>20d) / `GHOST` (>25d).
4. **Auto-purge at 30 days**, on every `update_orders2.py` run and weekly `clean_sales`:
   - `DELETE ... ordertype<>1 AND createddate < 30d` (backstop — sweeps 2/3/5)
   - `DELETE ... ordertype=3 AND arrived=0 AND createddate < 30d` (weekly, redundant)
5. **After purge the row is simply gone** — no alert, no re-order trigger. The
   suppression lifts silently and the SKU re-enters normal stock-aware reorder logic
   only *because stock is absent*, not because anything flagged the failed delivery.

**The gap.** An OOS no-show is invisible in the watched table. But the durable records
survive it:
- `stockorder` still says we ordered it (kept 365d).
- `incoming_stock` has **nothing** for that code (never receives a row).
- `orderstatus` row silently purged at 30d.

**The real detector is `stockorder` (ordered) vs `incoming_stock` (received) — but
nothing compares them automatically.** No standing reconciliation report exists (one
was considered and declined as too heavy). Detection today depends on running
`stuck_supplier_orders.sql` inside the 12–30d window, or noticing the SKU is short later.

---

## 5. Timings summary

| When | Job | Action |
|------|-----|--------|
| ~8×/day | `update_orders2.py` | sync type-1 in; purge received type-3 (>7d); 30d backstop (type≠1); batch='-1'; localstock sweeps |
| Mon 03:00 | `clean_sales.py` → `clean_sales.sql` | purge type-3 ghosts (>30d, redundant); `stockorder` >365d; `incoming_stock` >3yr; `orderstatus_archive` >365d; `bclog` >180d; `sales` >900d |
| On scan | PB goods-in | resolve → match (Amazon before Local) → flip `arrived` → localstock/`incoming_stock`/`bclog` |
| Ad-hoc | `stuck_supplier_orders.sql` | early-warning 12–30d; manual delete of confirmed ghosts |

**30 days** = ~10d typical supplier lead + 20d longest legitimate arrival observed +
buffer. Never shorten below lead time or in-transit stock strands into `#FREE`.
**7 days** = delivery + reconciliation window for received Amazon rows.

**`incoming_stock` = 3 years** (added to `clean_sales.sql`). The bound must clear the
deepest reader — `MAX(arrival_date)` per groupid ("days since last landed") in
`scale/pricing_pass.py` and `scale/check_null_segment.sql`. If the cutoff falls below
the slowest real restock cadence, a still-live style's last-landed date is deleted and
reads as "never arrived." Slowest observed cadence is ~18 months (the data only spans
that far), so 3 years leaves a year of headroom; storage cost is negligible (~1.5 MB/yr,
the whole table is ~2 MB at 18 months). The purge is a no-op until late 2027 (nothing is
older than 18 months yet). **Do not shorten below ~3 years** without re-checking
last-arrival reach for active groupids.

---

## 6. Legacy: type-5 Amazon Pick (dormant)

Agreed dead path — button no longer visible; documented so historical rows are
understood. Took existing `#FREE` local stock and re-designated it for Amazon:
consumed `#FREE` and re-wrote it as per-unit rows under `ordernum = AMZ-P-{ws}-{n}`,
wrote an `orderstatus` row (`ordertype=5`, `channel='MANUAL'`, aggregate `qty`), and
set `skumap.amzallow = today + 14` to admit the code to the Amazon feed for 14 days.
Superseded by `localstock.allocated = amz` set directly at goods-in. Never checked
off; ages out at the 30d backstop.

---

## Appendix — where each fact lives in source
- Purges: `update_orders2.py` (cleanup section, ~lines 723–763), `database/clean_sales.sql`.
- Goods-in scan/save/Amazon-pick: PB handlers (`of_scan`, goods-in-save, Amazon-pick button).
- Early warning: `database/stuck_supplier_orders.sql`.
- Schema: `database/DB-Schema.sql` (`orderstatus`, `stockorder`, `incoming_stock`, `bclog`, `localstock`).
