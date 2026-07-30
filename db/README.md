# db/ — querying the production database

The front door for reading data out of `brookfield_prod`. **Start here** rather than
looking for a schema file or an MCP server; there is no schema file, and the Postgres
MCP was removed in Jul 2026 (see "Why no MCP" below).

## Ad-hoc queries

```bash
python db/query.py "SELECT count(*) FROM sales"
python db/query.py --file some_report.sql
python db/query.py --csv "SELECT code, qty FROM localstock WHERE qty > 0" > out.csv
echo "SELECT 1" | python db/query.py
```

- Runs inside a **READ ONLY transaction**. An UPDATE/DELETE/DROP fails with
  `cannot execute UPDATE in a read-only transaction` and exits non-zero. This is a
  guard against accidents, not a security boundary — the credentials in `.env` can
  still write, so anything that genuinely needs to write must not route through here.
- Prints the first `--max-rows` rows (default 200) and tells you on stderr when it
  truncated. `--max-rows 0` for everything.
- Credentials come from `logging_utils.get_db_config()`, which reads `.env` at the
  repo root — the same path every scheduled script uses.

**This is for interactive lookups.** Anything scheduled, repeated, or that writes should
be its own script in its own capability folder, connecting with `get_db_config()`
directly. `query.py` is deliberately not importable as a library.

## Finding your way around the schema

There is no schema doc — it would rot. Ask the database:

```bash
# tables
python db/query.py "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1"

# columns of one table
python db/query.py "SELECT column_name, data_type, is_nullable FROM information_schema.columns
                    WHERE table_name='skusummary' ORDER BY ordinal_position"

# row counts, roughly, without a full scan
python db/query.py "SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 20"
```

## Key tables

| table | what it holds |
|-------|---------------|
| `skusummary` | product master — cost, pricing, seasonality, `segment` |
| `sales` | historical sales transactions |
| `localstock` | current inventory levels |
| `skumap` | the full size universe per `groupid` |
| `title` | product names, in `title.shopifytitle`, keyed by `groupid` |
| `price_track` | price history and performance |
| `incoming_stock` | actual stock arrivals, with `arrival_date` |
| `birktracker` | Birkenstock forward orders and deliveries |

## Gotchas that will cost you an hour

**Never read from or write to a `_delete`-suffixed table.** Those are retired —
soft-deleted, pending a real drop.

**Never use `skusummary.stockvariants` or `skusummary.variants` in analysis.** Both are
stale: the legacy PowerBuilder app only writes them when a record is touched for other
reasons, and they are frequently NULL. Verified Apr 2026 — White Arizona BF Reg showed
`stockvariants=1` while `localstock` had all 8 sizes in stock, on a row untouched for 14
months. Wrong in both directions, and dividing by them produces nonsense like 114% size
coverage. If you find them in an existing SQL block anywhere in this repo, **that block is
wrong — rewrite it before running.**

Size questions instead:

| need | use |
|------|-----|
| sizes currently in stock per `groupid` | `localstock` where `ordernum='#FREE' AND deleted=0 AND qty>0`, `COUNT(DISTINCT code)` |
| total size universe (coverage denominator) | `skumap` where `deleted=0`, `COUNT(DISTINCT code) GROUP BY groupid`. **Not `localstock`** — it drops historical empty sizes and understates the universe |
| per-size quantities | `localstock` joined to `skumap` for size labels |

**`localstock` uses `deleted = 0`, not `deleted IS NULL`.**

**Product names are in `title.shopifytitle`.** `skusummary` has no `productname` column.

**Stock freshness: use `incoming_stock.arrival_date`, not `skusummary.created`** — styles
repeat across seasons, so `created` tells you about the style, not the stock.

## Why no MCP

A Postgres MCP server (`@modelcontextprotocol/server-postgres`) was used until Jul 2026 and
removed. Three reasons: the package was deprecated upstream and unmaintained; its config
lived in a gitignored `.mcp.json` that had to be hand-recreated per machine and kept going
missing; and it only ever worked inside an interactive Claude Code session, whereas
`query.py` works there, on the VPS, and under cron. A future AI session should use
`query.py` and should not reinstate an MCP server without asking.

If `query.py` is unavailable for some reason, `psql` works with the same `.env` credentials:

```bash
PGPASSWORD=... psql -h 217.154.35.5 -U brookfield_prod_user brookfield_prod -c "SELECT 1"
```

## Related

- `db-maint/` — scheduled maintenance: sales-table purge, nightly backup. Different job.
- `logging_utils.get_db_config()` at the repo root — the shared credential loader.
