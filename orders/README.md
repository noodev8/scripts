# Orders

Shopify order synchronisation and pick allocation. This is the busiest live
process in the repo — it runs unattended several times a day (see `crontab.txt`)
and is also run by hand from the laptop.

> ## ⚠️ This logic exists in two places. Change both, or neither.
>
> Since **2026-07-28** the same pipeline also runs inside BCWEB:
>
> | | Where | Trigger |
> |---|---|---|
> | 1 | `C:\scripts\orders\update_orders.py` (this file) | cron — `crontab.txt` |
> | 2 | `C:\bcweb\bcweb-server\utils\orderSync.js` | the **Sync orders** button on BCWEB → Analytics → Sales (`POST /order-sync`) |
>
> **Both are live.** The cron was *not* switched off. They write the same rows in
> the same tables — `orderstatus`, `orderstatus_archive`, `sales`, `localstock` —
> and are expected to produce the same outcome.
>
> A change made in one and not the other does not fail loudly. It produces a
> database where some rows followed one set of rules and some followed the other,
> with nothing recording which. That already happened once on the Amazon side
> with `sales.profit`.
>
> The profit formula is duplicated a second time:
> `shopify_profit()` ↔ `C:\bcweb\bcweb-server\utils\shopifyProfit.js`.
>
> Full behaviour inventory and every deliberate divergence:
> **`C:\bcweb\docs\order-sync-port.md`**.
>
> ### Things the Node port fixed that this script still does
>
> None are urgent, but know them before you assume the two agree exactly:
>
> - **No pagination.** `limit=250`, no `Link` follow. Past 250 open unfulfilled
>   orders the fetch truncates — and the archive step then archives every order it
>   didn't see, because absence from the fetched list is how archiving is decided.
> - **Re-seen orders re-book their sale.** Archive → Shopify hands the order back →
>   a fresh `sales` row. 38 duplicate rows in the live table today.
> - **`batch::int` raises** on a blank or non-numeric `batch`, taking the whole run
>   down with only "Unexpected error" in the log.
> - **The split-row `localstock` id is random with no collision guard.** One clash
>   is a unique violation that unwinds the entire run.
> - **Two lines of the same SKU in one order**: the second line's quantity and its
>   sale row are dropped (the `orderstatus` PK is `(ordernum, shopifysku)`).
>
> Also worth knowing: `safe()` type-checks for `str`, so `shippingcost` — passed as
> a float — is written as `''` on **every** row. The port reproduces that
> deliberately rather than diverging.

## Run

From the repo root:

```
python orders/update_orders.py           # full sync, then pick allocation
python orders/update_orders.py --picks   # pick allocation only
```

Works from any directory — the script anchors on its own location, not the
working directory.

## What a full run does

1. **Order sync** — fetches unfulfilled orders from the Shopify Orders API and
   writes them into `orderstatus`. Both `paid` and `partially_refunded` orders
   are accepted (the latter covers refunded shipping).
2. **Archive** — orders no longer present in Shopify are archived out of
   `orderstatus`, and done picks are cleared from `localstock`.
3. **Pick allocation** — allocates picks against available stock, setting
   `orderdate` and `localstock` on the allocated row so the same order can't be
   picked twice. Partial allocations are logged as warnings.
4. **Cleanup** — prunes old `orderstatus` and `localstock` rows.

`--picks` skips step 1 and runs allocation against whatever is already in
`orderstatus`.

## Pick lists

Every allocated pick is appended to a CSV under `logs/picklist_archive/` at the
repo root, named `YYYYMMDD-HH-MM-PickList.csv`. Picks allocated in the same
minute share a file, and a run that allocates nothing creates no file.

**Retention is 100 files, not 100 days** — despite what the function's docstring
says, there is no date logic. Once the folder reaches 100, the oldest are deleted
so that 100 remain. Files are ordered by `os.path.getctime`, which on Linux is
the inode-change time — so moving files into this folder makes them look new and
will confuse the pruning. Don't.

## Paths

`REPO_ROOT` is derived from `__file__`, one level up from this folder, and
everything hangs off it: `.env`, `logging_utils`, and `logs/`.

This matters because **cron runs with no `cd`**. Anything resolved relative to
the working directory lands in the invoking user's home instead — which is
exactly what used to happen: pick lists were being written to `/root/logs/` on
the VPS while the normal log went to `/apps/scripts/logs/`. Fixed Jul 2026. If
you add a new file path here, anchor it on `REPO_ROOT`.
