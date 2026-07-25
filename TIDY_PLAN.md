# Scripts Folder Tidy-Up — Working Plan

**Status:** agreed in principle 2026-07-25. **Nothing has been changed yet.**
This is a multi-session plan. Read it top to bottom before doing anything.

## Governing principle (owner, 2026-07-25)

**The dividing line is reversibility, not importance.** Move fast where a mistake
is undone in seconds; take care where it isn't.

### Tier 1 — Files in this repo: lean towards tidying

There is a lot of stale work here. The owner accepts that one or two things will
be moved out by mistake and brought back. Do not agonise, do not build elaborate
proof that something is unused before moving it. **Archive is a move, not a
delete** — it's tracked in git, recovery is one command, and that is the whole
point. This covers root clutter, the `database/` folder purge, and `sandpit/`.

### Tier 2 — Cron: always safe

Verify the path, batch the changes, re-pull the crontab from the VPS to confirm.
No speed here, ever.

### Tier 3 — Database tables: safe posture (owner, revised same day)

Initially we were going to rename-on-suspicion. Revised after two problems
surfaced: **renames don't reliably break loudly** (views and foreign keys follow
a rename silently), and **two consumers live outside this repo** (the legacy
PowerBuilder app and the `bcweb-server` Node app), so a repo grep proves nothing.
The "if it breaks we'll know" safety net doesn't hold.

So: check dependencies *before* renaming, work smallest-risk first, and leave
anything uncertain alone. The tables are small — `shopifysnapshot` is 8KB — so
there is no cost to keeping them. Detail in step 3B.

### How we work through this — one decision at a time

**Do not batch-guess.** Do not go away, decide a list of items, and come back
having moved them. The owner holds knowledge that is not in this repo and cannot
be derived from it — what `pickpin` is, what PowerBuilder still reads, what
`bcweb-server` touches, which processes are genuinely retired versus dormant.
Guessing at those wastes his time correcting rather than deciding.

**The format for every item, in every step:**

1. Present **one** item (or one tightly-related cluster, e.g. the six-file
   performance cluster in step 1).
2. Give the evidence in a line or two: what it is, what references it, what the
   stats say, what breaks if it's wrong.
3. Say what you'd do — a recommendation, not a decision.
4. **Stop. Wait for his judgement.** Then act on it, and move to the next item.

Record each answer in the decision ledger at the bottom of this file as you go,
so a later session doesn't reopen a settled question.

Tier-1 file moves (root clutter, `database/` purge, `sandpit/`) can be presented in
slightly larger groups since they're trivially reversible — but the owner still
calls each one. Tier-3 table renames are strictly one at a time.

**Hard rule:** no crontab edits without the owner confirming that specific step.
Eight live cron lines reference root-level scripts by path, and the VPS crontab
is authoritative (`crontab.txt` is a mirror — re-pull with
`ssh root@vps "crontab -l"` from **cmd** before touching it).

---

## Why we're doing this

The folder is an active, essential part of the business, and it's growing. It's
not a mess — 15 of 21 folders already have a front-door doc and that pattern
works. But three things have gone wrong:

1. **Root is a dumping ground.** 18 loose files mixing shared library code,
   live cron scripts, ad-hoc tools, and docs. No way to tell which is which.
2. **Docs have rotted where nothing checks them.** `CLAUDE.md`'s command list is
   wrong in 4 of 6 lines. `database/server_cron.sql` is a stale second copy of
   the crontab.
3. **One-off work has no bucket.** Barcodes, ID dumps in `docs/`, colleague
   scripts — useful work with nowhere to land, so it lands at root.

---

## The conventions we're settling on

### 1. A folder per capability

A *capability* is something you'd describe in a sentence ("month-end accounting
pack", "Shopify order sync"). One file or ten — it gets a folder.

Root holds only: shared infrastructure (`logging_utils.py`), the catalogue
(`INDEX.md`), and top-level docs (`CLAUDE.md`, `crontab.txt`).

### 2. Every capability folder gets a `.md`

Two-tier documentation, deliberately:

- **`INDEX.md` at root** — the quick lookup. One line per capability: what it is,
  how to run it, when it runs, where the detail lives. For glancing at.
- **The folder's `.md`** — the detail. How it works, why it's built that way,
  gotchas, what to check when it breaks. For when the one-liner isn't enough.

**This applies to new work too, including colleague contributions.** A script
arriving at root is the thing we're fixing: it goes in a folder, with a short
`.md` saying what it does and how to run it. The `.md` doesn't need to be long —
a paragraph and a usage line beats nothing, and it's what lets the next person
(or the next session) pick it up cold.

### 3. Ad-hoc work gets a bucket

Some work is genuinely one-off — barcodes, a quick ID comparison, a data pull for
a question. It's worth keeping (it's cheap to keep and occasionally you want it
back) but it isn't a capability and shouldn't dilute the index.

**Proposed: `sandpit/` at root**, one dated sub-folder per piece of work
(`sandpit/2026-07-barcodes/`). One line in `INDEX.md` for `sandpit/` as a whole, not
per item. Allowed to be untidy inside. Not something we maintain.

Candidates to move here on day one: `barcodes/`, and the loose ID dumps in
`docs/` (`before_ids.txt`, `today_ids.txt`, `missing_ids.txt`,
`day-before-1753.txt`, `today-1345.txt`, `missing_products_analysis.txt`).

**Name settled 2026-07-25: `sandpit/`.** Owner's choice. Minor caveat noted and
accepted — "sandpit" leans towards *experiment*, while some contents are finished
one-off deliverables (the barcodes). Doesn't matter in practice; it's memorable
and unambiguous within this repo.

### 4. Nothing gets deleted — it gets archived

`archive/` at root for anything retired. Cheap insurance, and it means the
triage conversation below doesn't need to be agonised over.

The database equivalent: **rename, don't drop.** See step 3B.

---

## STEP 1 — Archive triage (do this first, together)

**This is a conversation, not a task.** Work through the list with the owner and
mark each one. Do not move anything until the whole list is decided.

### RESOLVED 2026-07-25 — the performance/pricing cluster is dead, archive it

Owner confirmed: **none of these three run anymore, and the Streamlit dashboard
was retired.** This is corroborated in the repo — `shopify-price/STRATEGY.md:129`
already records that the refresh cron "died in Mar 2026 (its metrics are
frozen), so we don't build on it."

Archive together as one cluster:

| Item | Notes |
|---|---|
| `refresh_groupid_performance.py` | Ran 3 SQL scripts + updated recommended prices. |
| `refresh_performance_stock.py` | Refreshed stock qty in performance tables. |
| `price_recommendation.py` | 37KB legacy pricing engine (Steady/Profit/Clearance/Ignore). Superseded by `shopify-price/`. |
| `price_recommendation_rules.md` | Documents the above engine. |
| `database/refresh_perfomance.sql` | Only ever run by `refresh_groupid_performance.py`. |
| `database/weekly_snapshot.sql` | Same. |

**Verified safe:** nothing else in the repo reads `groupid_performance` — the
three scripts are a closed cluster.

**`database/clean_sales.sql` — do NOT sweep up with this cluster.** It was in the
same batch that `refresh_groupid_performance.py` ran, but it's independently used
by the live `clean_sales.py` cron job. It sits under tier 2 (cron) and is still
open for discussion — see the queue.

**The tables are a separate, undecided question.** This cluster archives the
*scripts*. Whether `groupid_performance` / `groupid_performance_week` themselves
stay, get renamed, or eventually go is still to be discussed — see the queue.

**Don't archive yet:** `database/view_groupid_performance.sql`,
`view_Performance_stats.sql`, `database/tracking/owner_level_summary.sql`,
`database/tracking/review_list.sql` all reference the table. These look like
hand-run queries rather than pipeline steps — check with the owner whether any
are still used before moving them.

### Straightforward archive candidates

| Item | Why |
|---|---|
| `database/server_cron.sql` | Stale duplicate of `crontab.txt`, diverged, contains a typo'd filename. Actively misleading — breaks the "crontab.txt is the single source of truth" rule. |
| `check_shopify_delete_stock.py` | Reads `shopify-delete.csv`, which no longer exists. Spent one-off from Jul 2025. |
| `ask-claude.txt` | Two lines of prompt text, untracked. Superseded by the Shopify Pricing section in `CLAUDE.md`. |

### Needs an owner decision

| Item | Question |
|---|---|
| `run_update_orders2.bat` / `run_picks_only.bat` | Windows launchers for `update_orders2.py`, which runs on the VPS via cron. Still used locally, or leftovers? |
| `birk_fix_code_naming.sql` + `BIRK_CODE_NAMING.md` | One-off fix (Jul 2026) or ongoing reference? |
| `postgres-mcp-windows-setup.md` | Setup done — keep as reference or archive? |
| `docs/` loose `.txt` files | The ID dumps → `sandpit/`. But `GOOGLE-DATA-Merchant.txt` and `HowTo Run Google Ads Update.txt` may be live reference — check before moving. |
| `discussion/` (1 file, Apr 2026) | Is this a live habit or an abandoned one? If abandoned, fold into `sandpit/`. |
| `brand-expansion-shortlist.md` | Live thinking or finished exercise? (Memory says the exercise concluded.) |

### Confirmed keep — do not touch

`logging_utils.py` (root, imported by ~25 scripts via `sys.path` inserts —
moving it breaks everything), `crontab.txt`, `CLAUDE.md`, `WAYS_OF_WORKING.md`,
all nine live cron scripts, `powerbuilder/` (legacy app still in use).

---

## STEP 2 — Fix the misinformation (zero risk, no moves)

Once triage is agreed:

1. **Rewrite `CLAUDE.md`'s "Common Commands" and "Architecture" sections.**
   Confirmed wrong, all four:
   - `merchant_feed.py` is at `merchant-feed/merchant_feed.py`
   - **Delete the whole "Dashboard Components" section** — the Streamlit
     dashboard (`bc_dashboard/`, `Home.py`, `Shopify_Health_Check.py`,
     `db_utils.py`) was retired and the folder no longer exists
   - **Delete the "Price Recommendation System" section** and the
     `price_recommendation.py` / `refresh_groupid_performance.py` command lines
     — archived per step 1. Shopify pricing is `shopify-price/STRATEGY.md`.
   - Drop `groupid_performance` from the "Database Schema" table, or mark it
     **frozen since Mar 2026**
2. **Fix `scale/SCALE_PLAN.md:229`** — still lists `groupid_performance` as a
   "key table" with no indication it's frozen. That's a live trap for any future
   session doing scale work.
3. **Archive `database/server_cron.sql`** so `crontab.txt` is unambiguously the
   only schedule reference.

---

## STEP 3A — Purge the `database/` folder (tidy-first applies)

`database/` holds 25 `.sql` files with no README and no way to tell live from
dead. Owner: *"we have scripts that I'm sure we don't use. I don't want them
there."*

**Approach — move fast, three buckets:**

| Bucket | Test | Action |
|---|---|---|
| **Pipeline** | Executed by a live script | Keep. Currently only `clean_sales.sql` (run by the `clean_sales.py` cron job). |
| **Reference** | Schema / documentation | Keep. `DB-Schema.sql`, `Product_Price_Flow.sql`. |
| **Everything else** | Hand-run queries, one-offs, unknowns | → `archive/database/`. |

`database/Archive/` (10 files) already exists as a de-facto archive — fold it
into the new top-level `archive/` rather than keeping two archive concepts.

Don't spend time proving each hand-run query is dead. If one is missed, it comes
back. **The only file needing genuine care is `clean_sales.sql`** — it's on cron.

Whatever survives gets a `database/README.md` saying what each remaining file is
and when it runs.

---

## STEP 3B — Soft-delete unused DB tables (owner's `_delete` convention)

Owner: rename unused tables with a delete postfix; if anything breaks, easy
revert; drop them for real down the line.

### Naming — use `_delete`, not `-delete`

A hyphen is not legal in an unquoted Postgres identifier. `groupid_performance-delete`
would need double-quoting in **every** query that ever touches it again, forever,
and any tool that doesn't quote it will throw a syntax error rather than a clean
"table not found". That turns a clear signal into a confusing one.

**Use `groupid_performance_delete`.** Same intent, no quoting tax, and it still
sorts next to the original in `\dt`. Log every rename with its date in
`archive/DB_RENAMES.md` so the revert is a lookup, not a memory test.

### Two traps that break the "if it breaks, we'll know" assumption

**1. Views and foreign keys follow a rename silently.** Postgres tracks
dependencies by OID, not by name — so a view over a renamed table keeps working
and quietly rewrites its own definition. Renaming will therefore *not* flush out
view dependencies. Check `pg_depend` / `information_schema.view_table_usage`
before renaming, not after.

**2. Two consumers live outside this repo.** A repo-wide grep proves nothing
about them:
- the **legacy PowerBuilder app** (`powerbuilder/`, still in use) issues literal
  SQL we cannot see here
- the **`bcweb-server` Node app** on the VPS (`/apps/production/bcweb-server`,
  referenced in `crontab.txt`)

Anything PowerBuilder might touch — the small lookup tables especially — is
higher risk than the grep suggests. Breakage may also surface as a *silent*
failure in a nightly job rather than an obvious error.

### Evidence — candidates from `pg_stat_user_tables` (read 2026-07-25)

`stats_reset` is NULL, so these counters cover a long window. Low numbers are
meaningful. **Note the read counts include our own MCP/catalog queries**, so
treat them as a floor, and no table shows zero reads.

| Table | Rows | Reads | Writes | Read |
|---|---|---|---|---|
| `shopifysnapshot` | 0 | 951 | **0** | Never written to, ever. Something still selects from it and always gets nothing. Strongest candidate. |
| `scratchpad_note` | 0 | 120 | 4 | Abandoned experiment. |
| `campaign` | 1 | 485 | 1 | Single row, written once. |
| `grouplabel` | 1 | 3578 | 1 | Lookup table, likely PowerBuilder. |
| `inivalues` | 2 | 424 | 2 | Config table, likely PowerBuilder. |
| `pickpin` | 2 | 449 | 2 | Likely PowerBuilder. |
| `shopprices` | 134 | 487 | 134 | Written once, never updated. Possibly superseded by `price_track`. |
| `offlinesold` | 37 | 507 | 37 | Written once. |
| `productlink` | 116 | 415 | 116 | Written once. |
| `category` / `producttype` | 3 / 5 | — | — | Lookup tables — check PowerBuilder first. |

### Required pre-check before ANY rename (safe posture)

Run for each candidate and record the result in `archive/DB_RENAMES.md`:

```sql
-- 1. What depends on this table (views, FKs, constraints)?
SELECT DISTINCT dependent_ns.nspname, dependent_view.relname
FROM pg_depend d
JOIN pg_rewrite r ON r.oid = d.objid
JOIN pg_class dependent_view ON dependent_view.oid = r.ev_class
JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
JOIN pg_class source ON source.oid = d.refobjid
WHERE source.relname = '<table>';

-- 2. Any foreign keys pointing at it?
SELECT conrelid::regclass AS from_table, conname
FROM pg_constraint
WHERE confrelid = '<table>'::regclass;
```

Then grep `powerbuilder/` and ask the owner whether the legacy app or
`bcweb-server` touches it. **If the answer is "not sure", leave it.** These
tables total a few hundred KB — keeping them costs nothing.

**Suggested order — stop at the first sign of a dependency:**

1. `shopifysnapshot`, `scratchpad_note` — empty, no data to lose. Start here.
2. The write-once tables (`campaign`, `offlinesold`, `productlink`, `shopprices`)
   — only after the pre-check is clean **and** the owner confirms.
3. The small lookup tables (`inivalues`, `pickpin`, `grouplabel`, `category`,
   `producttype`) — **leave alone for now.** Most likely PowerBuilder
   dependencies, smallest possible saving, worst failure mode.

Rename one at a time, not in a batch — a batch makes it impossible to tell which
rename caused a downstream failure.

**Do NOT rename yet:** `groupid_performance` and `groupid_performance_week`.
Frozen since Mar 2026, but they hold real historical data and the step-1 decision
was explicitly to archive the *scripts*, not touch the tables.

**Rename during a quiet window and watch the next nightly cron run** before doing
the next one. Most consumers here are overnight jobs — a break won't show up
immediately, which is exactly why these go one at a time.

---

## STEP 3C — Build `INDEX.md` + a checker (zero risk, no moves)

### `INDEX.md`

Root-level quick lookup. One row per capability. Proposed columns:

| Path | Domain | What it does | Run | Schedule | Detail |
|---|---|---|---|---|---|

**Domain** answers "is this all Brookfield?" — it mostly is, but not entirely:

- `BC-ops` — live Brookfield automation (cron scripts, feeds, syncs)
- `BC-analysis` — interactive/decision processes (`shopify-price/`, `amz-price/`,
  `scale/`, `seo/`, `google-ads/`, `birk-stock/`)
- `OFD` — Online Front Door, a **separate business** (`ofd/`)
- `Legacy` — `powerbuilder/`
- `Reference` — docs and material, not runnable (`database/`, `docs/`,
  `order-status-process/`, `barcodes/`)
- `Adhoc` — the bucket

Rules: **`Schedule` is derived from `crontab.txt`, never hand-typed** (that's how
`CLAUDE.md` rotted). `sandpit/` gets one row for the whole folder.

### `catalogue.py`

A small checker so the index can't silently go stale. It should verify:

- every path in `crontab.txt` exists on disk
- every `.py` at root or in a capability folder appears in `INDEX.md`
- every capability folder has a front-door `.md`
- flag files at root that aren't on the allowed-at-root list

Report only — it should never move or edit anything.

---

## STEP 4 — The folder moves (RISKY — crontab changes, do last, one batch)

Only after steps 1–3 are done and settled. **Do all crontab-affecting moves in a
single batch**, then one VPS crontab update, then re-pull to verify.

Proposed groupings (names not final):

| New folder | Contents | Crontab lines affected |
|---|---|---|
| `orders/` | `update_orders2.py` (+ `.bat` files if kept) | 3 |
| `shopify-sync/` | `price_update.py`, `price_track.py`, `update_shopify_inventory.py`, `update_shopify_titles.py`, `update_shopify_tags.py` | 6 |
| `month-end/` | `month-export.py`, `shopify_fees.py`, `stock_position.py` (they call each other) | 0 |
| `images/` | `updateimages.py`, `authorize_drive.py` | 1 |
| `db-maint/` | `clean_sales.py`, `pg_backup.sh` | 2 |
| `ukd/` | move `ukdfile.py` in (folder already exists) | 0 |
| `secrets/` | `client_secret.json`, `merchant-feed-api-*.json`, `drive_oauth_client.json`, `drive_token.json` | 0 (but `.env` paths / `authorize_drive.py` write path need checking) |

**Every moved script needs its `sys.path` insert checked** — scripts already in
folders reach back to root for `logging_utils` with
`sys.path.insert(0, <parent>)`. Newly-moved scripts will need the same, and
`month-export.py` imports `shopify_fees`/`stock_position` as siblings.

Each new folder gets its `.md` as part of the move, not afterwards.

### Also in step 4 (non-risky, can go first within it)

- Tighten `.gitignore`. It blanket-ignores `*.txt` and `*.csv`, then carves out
  `!crontab.txt` and `!discussion/**`. Any future `.txt` doc silently vanishes
  from git — that's why `ask-claude.txt` was never tracked. Narrow the blanket to
  the directories that actually produce data files.

---

## Decision ledger

Every item the owner rules on, recorded as we go. **Append, don't rewrite.** A
"keep" here is as valuable as an archive — it stops a later session reopening a
settled question.

Status values: `ARCHIVED` · `KEEP` · `RENAMED` · `LEAVE FOR NOW` · `PENDING`

| Date | Item | Decision | Note |
|---|---|---|---|
| 2026-07-25 | `refresh_groupid_performance.py`, `refresh_performance_stock.py`, `price_recommendation.py`, `price_recommendation_rules.md`, `database/refresh_perfomance.sql`, `database/weekly_snapshot.sql` | **ARCHIVE** (agreed, not yet moved) | Owner: none of these run anymore. Corroborated by `shopify-price/STRATEGY.md:129`. |
| 2026-07-25 | Streamlit dashboard (`bc_dashboard/`) | **RETIRED** | Owner confirmed. Folder already gone; remove the `CLAUDE.md` section. |
| 2026-07-25 | Bucket name | **`sandpit/`** | Owner's choice over `adhoc`/`workbench`/`scratch`. |

**Ledger discipline:** only the owner's rulings go in this table. An assistant
recommendation, however well-evidenced, stays in the open queue until he rules on
it. (Two rows were logged in error on 2026-07-25 — `groupid_performance` and
`clean_sales.sql` — and have been moved back to the queue below.)

### Open queue — to work through, one at a time

Ordered easiest-first. Each needs the owner's judgement, not a guess.

**Still to discuss — carried over from step 1, NOT decided:**
- **`groupid_performance` + `groupid_performance_week` (tables)** — frozen since
  Mar 2026, 305 and 14,350 rows, 216KB + 2.6MB. Their refresh scripts are being
  archived. Recommendation was keep-the-tables, but that's the owner's call: is
  the frozen history still worth querying, or does it go the way of the scripts?
- **`database/clean_sales.sql`** — this one is on cron (run by `clean_sales.py`),
  so it sits under **tier 2, not tier 1**. My "must stay" was a finding, not a
  decision. If the owner wants it changed or retired, that's a crontab-safety
  conversation, not a file move.

**Tier 1 — files (reversible, can group):**
- `database/server_cron.sql` — stale duplicate crontab, has a typo'd filename
- `check_shopify_delete_stock.py` — reads a CSV that no longer exists
- `ask-claude.txt` — two lines of prompt text, superseded by `CLAUDE.md`
- `barcodes/` + the loose `docs/*.txt` ID dumps → `sandpit/`
- `run_update_orders2.bat` / `run_picks_only.bat` — still used locally?
- `birk_fix_code_naming.sql` + `BIRK_CODE_NAMING.md` — one-off or reference?
- `postgres-mcp-windows-setup.md` — setup done; reference or archive?
- `discussion/` (1 file, Apr 2026) — live habit or abandoned?
- `brand-expansion-shortlist.md` — live thinking or finished exercise?
- `database/` bulk purge — 25 files, three buckets (step 3A)
- `docs/GOOGLE-DATA-Merchant.txt`, `docs/HowTo Run Google Ads Update.txt` — live reference?
- `database/view_groupid_performance.sql`, `view_Performance_stats.sql`, `database/tracking/owner_level_summary.sql`, `database/tracking/review_list.sql` — hand-run against frozen data?

**Tier 3 — tables (one at a time, pre-check first):**
- `shopifysnapshot` — 0 rows, **never written to**, 8KB
- `scratchpad_note` — 0 rows, abandoned experiment
- `campaign`, `offlinesold`, `productlink`, `shopprices` — write-once
- `inivalues`, `pickpin`, `grouplabel`, `category`, `producttype` — **owner knows
  what these are**; likely PowerBuilder. Recommendation is leave alone, but his call.

**Tier 2 — cron:** nothing until step 4, then one batch with full verification.

---

## When this is finished

Archive this file to `sandpit/` (or delete it) and fold the conventions — the
folder-per-capability rule, the folder `.md` requirement, the `sandpit/` bucket —
into `CLAUDE.md` so they survive as standing practice rather than a one-off
clean-up. Note that memory does not sync between the owner's two machines, so
conventions must live in the repo, not in memory.
