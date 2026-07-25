# Orders

Shopify order synchronisation and pick allocation. This is the busiest live
process in the repo — it runs unattended several times a day (see `crontab.txt`)
and is also run by hand from the laptop.

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
