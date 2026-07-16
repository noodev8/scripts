# SEO — front door

Read this first for any SEO session.

## The goal

**Increase free clicks.** Be less dependent on Google Shopping.

This is a 3 / 6 / 12-month game, not a hunt for a win this week. SEO changes take
4–8 weeks to show. Nothing here is expected to move the P&L this quarter.

Scale, so nobody kids themselves (90 days to 2026-07-16):

| | Clicks | Impressions | CTR | Cost |
|---|---|---|---|---|
| **Organic** | 2,979 | 261,921 | 1.14% | £0 |
| **Paid** | 28,550 | 1,099,486 | 2.60% | £12,445 |

Organic is ~10% of Google clicks, worth ~£1,300/quarter at the £0.44 paid CPC.
Doubling it is a good year's work and buys ~£5k/year. The case for it is that it
is free, compounds, and does not stop when you stop paying.

## The number

**Clicks.** That is the target. Everything else is diagnosis:

| Metric | Role |
|---|---|
| **Clicks** | The target. The only one that is money. |
| Impressions | Diagnostic — are we being shown at all? |
| Position | Diagnostic — are we being shown where anyone looks? |
| CTR | Diagnostic — shown, but did they click? |

**Do not score on average position.** It is an average across every query you
appear for, so ranking for one new obscure term at position 50 makes it look
*worse* while you gained ground. It punishes growth.

**Read them together or you learn nothing repeatable:**

| Position | CTR | Meaning |
|---|---|---|
| flat | flat | The change did nothing. |
| flat | up | Title/snippet worked — same slot, more clicks. |
| up | up | Google re-rated the page. The real win. |
| up | flat | Ranking for queries that aren't ours. |

## What we can actually change

Position, impressions and clicks are all **outputs**. Google decides them. The
levers — the only things in our control — are:

- page title and meta description (what shows in the result)
- the collection/page description text
- which products sit in a collection
- where we link to it from, and the anchor text

## Structure

Site → type → page. `python weekly.py`.

| Level | Window | Why |
|---|---|---|
| Site | 7d vs prior 7d | ~232 clicks/week — week-over-week is readable |
| Type | 28d vs prior 28d | collections / homepage / products / pages / blogs |
| **Winners** | 28d vs prior 28d | **top pages by clicks, across all types, with cumulative %** |
| Most impr / worst CTR | 28d | shown but not clicked — the untapped end |

**Winners is cross-type on purpose.** Split by type, the picture is invisible:
the size guide out-earns nearly every collection but sits in a different
section. The top three pages are a collection, the homepage and an info page.

`--type collections` narrows every section to one type. `--top N` sets rows.

## What we store

**Nothing.** GSC serves 16 months retroactively at any granularity, so any past
week is available on demand and no window ever closes on us. If we ever want
history beyond 16 months, backfill once a year — the data is not going anywhere
before then. Storing it would duplicate a better source.

Changes we make are logged by hand in `CHANGELOG.md` — that is the one thing GSC
cannot give us. It has 16 months of traffic and no idea what we did to cause it.

## Baseline — 2026-07-16

Site: **2,979 clicks**, 261,921 impressions, 1.14% CTR, avg position 11.3.

| Type | Pages | Clicks | % | Impressions | CTR | Clicks/page |
|---|---|---|---|---|---|---|
| collections | 101 | 1,429 | 48% | 109,594 | 1.30% | 14.1 |
| homepage | 1 | 565 | 19% | 6,481 | 8.72% | 565 |
| products | 984 | 539 | 18% | 56,550 | 0.95% | 0.5 |
| pages | 11 | 444 | 15% | 87,277 | 0.51% | 40.4 |
| blogs | 9 | 2 | 0% | 2,005 | 0.10% | 0.2 |

**Traffic is extremely concentrated.** Three URLs hold ~47% of all impressions:

| Page | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| /pages/birkenstock-size-guide | 83,379 | 334 | 0.40% | 10.1 |
| /collections/birkenstock-narrow-fit-sandals | 27,752 | 523 | 1.88% | 7.8 |
| /collections/mens-goor | 12,737 | 74 | 0.58% | 8.5 |

The size guide alone is **32% of site impressions** — more than all 984 product
pages combined — and converts worst of the three.

On clicks the same concentration holds: the **top 3 pages are 51%** and the top
20 are **78%** (28d). Those top three are a collection, the homepage and an info
page — one of each type.

Not every high-CTR page is an opportunity: `birkenstock-sandals` ranks **2.2**
with **8.52% CTR** on 352 impressions. It has already won; there is no volume
behind the term. Check impressions before reading a good CTR as headroom.

## What we know

Established 2026-07-16, against data, not assumption:

- **Average position 11.3 is page two.** We are not being outranked so much as
  shown where nobody scrolls. Impressions are not the constraint — we have
  261,921 of them producing 2,979 clicks.
- **The pages rank for the right queries.** There is no relevance mismatch to fix
  (checked at query level on the top low-CTR pages).
- **CTR follows the normal position curve.** Where a page ranks 5–7 it converts
  3–6%; at 9–13 it converts 0.2–0.5%. No snippet catastrophe.
- **Indexing is binary and settled.** Indexed pages earn; unindexed earn nothing
  (0 clicks, 9 impressions across 21 pages). All 63 earning collections are
  indexed. Indexing is not the constraint.
- **Specific, intent-led collections are the engine** — the original strategy was
  right. `birkenstock-slippers` (8 products) earns 111 clicks; the general
  `birkenstock-sandals` (136 products) ranks 2.5 and earns 64.
- **Aggregators are worthless.** `all`, `sandals`, `full-price` are near-supersets
  of collections Google already indexes. It declines to index them, and even when
  general pages *are* indexed they earn little. Nothing lost.
- **Products are a long tail** — 984 pages at 0.5 clicks each. Not workable page
  by page; only systematically or not at all.
- **Blogs are dead** — 9 pages, 2 clicks, 2,005 impressions.
- **No conversion data exists.** No GA4, no analytics plumbing. GSC stops at the
  click. Clicks are the honest proxy until someone wires up GA4.

## Ruled out (and why)

- **Internal links as a lever — unproven, not disproven.** GSC's
  `referring_urls` counts sitemaps, self-pagination and product-recommendation
  widgets as links. Your top earner shows "1 referring URL" and it is its own
  `?page=2`. The field cannot answer whether links move rankings. Settling it
  needs a real crawl of the site's own `<a href>` map.
- **Orphan-fixing.** Built on the same broken column. `birkenstock-milano` shows
  0 referring URLs and earns 73 clicks. "0 refs" means Google's sample returned
  nothing, not that nothing links there.
- **Re-organising collections.** The original intent-led structure is the thing
  that works. Re-organising loses accumulated authority for a hypothesis.
- **Ad conversion rates do not transfer.** Paid converts at 2.60% because it sits
  at the top with an image. You cannot inherit that by ranking 11th.

## Traps

- **Seasonality.** Sandals peak in July. Any before/after over the 4–8 weeks SEO
  takes will be swamped by season. Pilot on season-neutral pages, and keep a
  control group of pages you deliberately don't touch, so you measure against the
  site's own trend rather than a page's past self.
- **Concentration.** 40% of collection traffic is one page. Do not run experiments
  on `birkenstock-narrow-fit-sandals`.
- **Weekly page-level clicks are noise.** ~6 clicks/week on a typical page. Read
  28-day windows at page level, and trends not verdicts.

## Scripts

| Script | Does |
|---|---|
| `weekly.py` | **The report.** Site → type → page, live from GSC. Stores nothing. |
| `gsc_client.py` | GSC auth + `SITE_URL`. Uses the merchant-feed service account. |
| `list_collections.py` | Shopify collections + product counts. |

Run: `python weekly.py`. Nothing is scheduled — this is a report you read, not a
job that collects. Everything it shows is retrievable at any time.

## State

Nothing is in flight. The work has not started — the focus decision comes next.
