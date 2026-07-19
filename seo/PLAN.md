# SEO — the plan (how we operate)

The operating doc. Read this to know **what we do and what to work on next**.
`README.md` is the background reference (the goal, the scoreboard, what we know,
what's ruled out). `CHANGELOG.md` logs every change + expectation + outcome. The
current work lists are the auto-generated `collection_priorities.md` /
`product_priorities.md`.

## The goal, in one line

More **free** clicks from Google, so we lean less on paid. It's free, it compounds,
and it doesn't stop when you stop paying. (Full philosophy: README.)

## The framework — the grid

Every opportunity is a **page type × a search intent**. The wins are on the diagonal:

| | Browse intent ("birkenstock milano") | Product intent ("milano dark brown") |
|---|---|---|
| **Collection** | ✅ **traffic play** — build/rank the collection | — mismatch |
| **Product page** | ❌ **the Bend mirage** — don't | ✅ **value play** — improve the product page |

**Match the page to the intent.** Browse demand → a collection. Product demand → a
product page. The classic mistake is aiming a product page at browse demand (the
Bend: 728 impressions of "birkenstock trainers", zero sales).

## Two lists (they rank differently on purpose)

Collections are **traffic-constrained** (lots of browse search — are we capturing
it?). Products are **value-constrained** (product search is uniformly low — so a
page built once earns for years, and we build them for the products worth it).

| | Collections | Products |
|---|---|---|
| Script | `collection_priorities.py` | `product_priorities.py` |
| Output file | `collection_priorities.md` | `product_priorities.md` |
| Ranked by | browse **demand** not captured | **value** (proven organic £, then units×margin) |
| Scope | all collections | Birkenstock only (Shopify-win; parked brands excluded) |

**You decide what's worth working** — the list ranks demand/value, it does not judge
a collection out (e.g. high-traffic low-margin Goor stays on it; that's your call).

**Review cooldown** — mark something worked or dismissed and it drops off for a period:
```
python seo/collection_priorities.py --review <handle> --days 90 --note "why"
python seo/product_priorities.py    --review <handle> --days 90 --note "why"
```
`--all` shows snoozed rows. State lives in `*_reviews.json` (in the repo, so it
syncs across both machines).

## The two recipes (what "the work" actually is)

**Collection work** (browse demand → capture it):
1. If no page exists, build it. If it exists but is stuck ("crawled – not indexed"),
   the fix is discovery, not content.
2. Link it from the **menu + parent collection + a high-authority page** (the size
   guide is the most-linked page on the site).
3. Title + description match the browse terms — find them with
   `python seo/queries.py --page /collections/<handle>`, or size a specific term with
   `--query "<term>"` / `--contains <word>`.
4. Request re-indexing in GSC (URL Inspection → Request Indexing).

**Product work** (product demand → capture + convert):
1. **Find the terms:** `python seo/queries.py --page /products/<handle>` — it lists
   every term the page already ranks for, with impressions and position. Target the
   ones with real impressions but a **poor position (page 2)**. The top query also
   shows the *language people actually use* (e.g. "two strap", not "Arizona"). Note:
   GSC only shows terms you already appear for — greenfield keywords are the parked
   Keyword Planner job.
2. Weave those terms into the **description** — natural copy, not stuffing. Keep the
   **title clean** (it's what shoppers see; the ranking lever is content + links, not
   a stuffed title).
3. Link to it from its **own collection** (highest-authority, most relevant link),
   then related-product blocks.
4. Log it + measure against an untouched **control** (sandals are seasonal — a
   control separates your work from July).

## How to run it (the loop)

1. **Monthly:** run both reports, open the two `.md` lists.
2. **Weekly hour:** take the top *unreviewed* row (alternate collection / product so
   products aren't starved by bigger collection numbers), do the recipe, mark it reviewed.
3. **Log** each in `CHANGELOG.md` with the expected result *before* you know it.
4. **Read the result at 4–8 weeks** vs the control.

## What we measure (the scoreboard)

- **Monthly:** trailing-12 organic clicks (`weekly.py`) + organic revenue (`ga4_client.py`).
- **Per changed page:** impressions → position → clicks, in that order (that's the
  order they move; a new page shows impressions weeks before clicks).
- **Two scoreboards, never merged:** SEO = free clicks; the business = the P&L. Free
  clicks don't have to prove ROI — that's a paid problem.

## Current experiments (live)

- **Arizona vs Madrid** — do internal links get a stuck collection *indexed* (Gate 1,
  ~1–2 wks) and then *earning clicks* (Gate 2, 4–8 wks)? Both linked 2026-07-17.
  First honest read **~2026-08-14**. Compare at equal age, on rate not raw clicks
  (Arizona ~2,441 impr vs Madrid ~818).
- **Size-6 page** — informational page test, same window.
- **Product recipe** — first test not started. Candidate: `arizona-white-patent`
  (190 impr, 25% conversion, ranks 8.4 — enough traffic to read a signal).

## Settled — don't re-litigate

- **Both types earn independently.** Collections win browse traffic; product pages win
  a smaller, high-converting product-intent stream (GA4: Milano products sold £442/90d
  from their *own* direct organic landings — the collection did **not** feed them).
- **Head terms aren't ours** — Milano ranks 17, Gizeh 23 on the bare brand terms. That's
  competition, not a fixable page. We win the specific and the long tail.
- **Indexed ≠ trafficked** (gizeh is indexed, earns ~0). **Visibility ≠ value** (the size
  guide is max-linked, ranks, and is hollow — 0.49% CTR).
- **Rank by value, not impressions** — Goor was a high-traffic, low-margin trap.
- **Google Ads** — parked. Light UI exports (Keyword Planner / Auction Insights) when we
  need to triage a term; wire the API only if it becomes frequent.

## Decision rule

Prove on the pilot, then invest more **targeted** time. Getting a page indexed is cheap;
earning clicks is the bar. Never scale an unproven fix.
