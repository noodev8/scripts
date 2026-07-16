# SEO — front door

Collection-page SEO for the Shopify store. Read this first for any SEO session.

## Strategy

**Winners first.** Effort goes to collections that already have product depth and
commercial intent, not to fixing every thin page. A collection with 175 products
and no traffic is a bigger prize than ten collections with 3 products each.

**The finding that drives the work: internal links.** Collections that nothing
links to are orphaned — Google may never discover them, and if it does, it treats
them as unimportant. Orphan status is the cheapest thing to fix and the most
likely to move the needle. `referring_url_count = 0` in the snapshot is the list.

**The measurement chain, in order:**

1. **Index state** — is the page known, crawled, indexed? *(stored)*
2. **Referring URLs** — does anything link to it? *(stored)*
3. **Impressions / position** — is it competing? *(live from GSC)*
4. **Clicks** — the outcome. *(live from GSC)*

Only 1 and 2 are snapshotted. 3 and 4 stay live from the Search Analytics API.

**Sequencing — this is what stops us fooling ourselves.** The chain runs: add
internal links → Google discovers → crawls → indexes → impressions appear →
position settles → clicks. That is realistically **4–8 weeks** before clicks mean
anything. Judged at two weeks, a working intervention looks like a failure.
Index state, by contrast, flips within days-to-weeks — which is why it's the
metric that tells us whether the change worked, long before traffic does.

## Why the table stores no traffic columns

Clicks/impressions/position are retrievable from the GSC Search Analytics API for
16 months at any granularity, so storing them duplicates a better source. Index
state is the opposite: the URL Inspection API is point-in-time only and Google
keeps no history, so *"when did this page get indexed?"* is unanswerable after the
fact unless we snapshot it ourselves.

An earlier `seo_collection_traffic` table stored a **90-day rolling aggregate**
against a point-in-time date, which smeared every window into every other and made
the table useless. It was deleted, never populated. Index state has no window at
all, so consecutive snapshots diff cleanly. **Do not re-add traffic columns here.**

## Process

**Snapshot: weekly cron on the VPS, unattended.** Not on request. The whole value
is an unbroken timeline — snapshots that only happen when someone thinks about SEO
cluster around sessions and leave gaps exactly where the index changes land.
Weekly is right: index state moves on days-to-weeks, so daily burns quota on noise
and monthly is too coarse to tie a `crawled → indexed` flip to the change that
caused it.

Cron line (see `crontab.txt`; server clock is GMT):

```
# 5:30 AM - Weekly SEO index-state snapshot (Mondays)
30 4 * * 1 /apps/scripts/venv/bin/python /apps/scripts/seo/snapshot_index_state.py
```

No `cd` needed — the script resolves its imports and `.env` from `__file__`, not
the cwd. Credentials are already on the VPS: `gsc_client.py` uses the same
`merchant-feed-api-462809` service account key that the nightly merchant feed uses.

**Run timing does not matter.** Rows are point-in-time and keyed on
`(handle, snapshot_date)`; nothing assumes even spacing, so an off-cycle or
repeated run costs nothing and there is no "out of sync" state to be in. (This is
exactly what the old rolling-window traffic table got wrong.)

**Analysis: on-demand, in session.** Ask questions, not for runs — *"what changed
since we added the links?"*, *"did sandals ever get indexed?"*. Claude queries the
table; it doesn't populate it. A snapshot taken mid-session is a redundant row.

**The one manual exception:** run a snapshot immediately after a batch of link
changes, so the before/after boundary is sharp rather than smeared across a weekly
cycle.

**Progress/status of any run:** `tail -f /apps/scripts/logs/snapshot_index_state.log`

## Caveat: inspecting a URL can cause Google to discover it

Two runs 10 minutes apart on 2026-07-16 saw `birkenstock-sydney` move from
`URL is unknown to Google` to `Discovered - currently not indexed` with no other
change. The URL Inspection API appears not to be purely passive — looking at a
page can register it.

So **`unknown → discovered` is not a win** and must not be attributed to
link-building; we probably caused it by measuring. The transitions that do mean
something (`crawled → indexed`) are unaffected.

## Scripts

| Script | Does |
|---|---|
| `snapshot_index_state.py` | Weekly snapshot → `seo_index_state`. Saves `index_state_<date>.json` before the DB write; `--load-from FILE` replays it into the DB without re-inspecting. |
| `create_seo_index_state_table.sql` | DDL for `seo_index_state`. |
| `collections_traffic.py` | Live clicks/impressions/position from GSC. Owns traffic; join to snapshots on `handle`. |
| `list_collections.py` | Shopify collections + product counts. |
| `gsc_client.py` | GSC auth + `SITE_URL`. |

Run: `python snapshot_index_state.py`. The API takes ~6s per URL, so 84
collections is a ~9 minute run. Progress echoes to the terminal when run by hand
and stays silent under cron (no TTY), so cron mails nothing; the log file has it
either way. Safe to re-run — the DB write is one commit at the end and the upsert
makes same-day repeats idempotent.

## State (2026-07-16)

**Baseline taken**, 84 collections, 0 errors:

| Coverage state | Count |
|---|---|
| Submitted and indexed | 63 |
| Crawled - currently not indexed | 17 |
| URL is unknown to Google | 2 |
| Discovered - currently not indexed | 2 |

**15 orphaned** (nothing links to them). Two distinct problems:

- *Orphaned AND not indexed* — `womens-rieker-sandals` (7 products, unknown),
  `birkenstock-sydney` (6, discovered). Invisible: nothing links to them, so
  Google never properly found them.
- *Orphaned but indexed anyway* — `lunar-flat-sandals` (13),
  `womens-footwear-for-hiking-walking` (6), `mens-wedding-shoes` (4),
  `mens-wide-shoes` (4), `birkenstock-milano` (4). Found via sitemap, but nothing
  on the site vouches for them.

Not yet in the VPS crontab.
