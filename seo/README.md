# SEO — front door

Read this first for any SEO session.

## The goal

**Increase free clicks.** Be less dependent on Google Shopping. Paid is the
yardstick you hold it against, not the thing you score.

This is a 3 / 6 / 12-month game. SEO changes take 4–8 weeks to show. Nothing here
moves the P&L this quarter. Organic is ~10% of Google clicks and worth ~£1,300/
quarter at the paid CPC — doubling it is a good year's work and buys ~£5k/year.
The case for it: it is free, it compounds, and it does not stop when you stop
paying.

## The number

**Trailing 12-month clicks.** Everything else is diagnosis:

| Metric | Role |
|---|---|
| **Clicks, trailing 12m** | The scoreboard. Season-proof. Must go up. |
| Clicks, 7d / 28d | Breakage detection only. In July it is sandals, not progress. |
| Impressions | Are we shown at all? |
| Position | Are we shown where anyone looks? Not comparable across years. |
| CTR | Shown — but did they click? |

**Do not score on average position.** It averages across every query you appear
for, so ranking for one new obscure term at position 50 makes it look *worse*
while you gained ground. It punishes growth.

**Read position and CTR together or you learn nothing repeatable:**

| Position | CTR | Meaning |
|---|---|---|
| flat | flat | The change did nothing. |
| flat | up | Title/snippet worked — same slot, more clicks. |
| up | up | Google re-rated the page. The real win. |
| up | flat | Ranking for queries that aren't ours. |

## The curve

`weekly.py` prints CTR-vs-position, and it is the section that decides whether a
CTR play is worth doing. Reproduce it any time — it is computed live, nothing is
stored.

**How it works.** Every page with ≥250 impressions in the last 28d is bucketed by
average position (1-3, 3-5, 5-7, 7-9, 9-11, 11-14, 14-20, 20+). Each band's
**median** CTR is what a slot is worth on this site. A page is an opportunity
only if it sits below **its own band's median** — that is the `BELOW CURVE`
table, and the gap column is the clicks it would earn at median.

**Why medians and bands, not raw CTR.** Sorting pages by raw CTR just
re-discovers that low-ranked pages convert badly. It flags the size guide as the
top opportunity when at 0.49% against a 0.66% band median it is already almost
exactly where its rank says it should be. Band-relative scoring separates *ranks
badly* (a ranking job, or no job) from *ranks fine, earns badly* (a title job).
Median not mean, because one page at 8% CTR would drag a whole band.

**Reading it.**

- Bands marked *thin* have under 4 pages. Their median is noise — do not act on
  a gap measured against one other page.
- Position is GSC's average across every query the page appears for, so a page
  at "6.7" may be 3rd on a small query and 15th on a big one. The band is a
  prior, not a verdict — check query level before rewriting anything.
- **The total at the bottom is the point.** If the whole opportunity is small,
  the answer is that there is no CTR play, and the work is ranking or new pages.

## What we are trying to beat

**Trailing 12-month clicks. It must go up. Nothing else is the scoreboard.**
`weekly.py` prints it first.

A 12-month window holds every season exactly once, so it is season-neutral **by
construction** — the only way it moves is if something real changed. Its
month-on-month delta *is* the year-over-year delta for the month that just rolled
in, so it carries the same signal as "beat the same month last year" without the
noise of 12 disconnected readings. **One line, always comparable, no seasonal
adjustment to argue about.**

**Never judge on 7d or 28d.** Sandals peak in July, so `weekly.py` showing "+40%"
on 28d is the season recovering and means nothing. Those windows are for spotting
breakage, not progress.

**Where it stands, 2026-07-16 — falling, and the fall is accelerating:**

| Trailing 12m to | Clicks | Chg | Impressions |
|---|---|---|---|
| 2026-03 | 9,124 | — | 1,047,062 |
| 2026-04 | 9,093 | −31 | 1,020,756 |
| 2026-05 | 8,764 | **−329** | 966,635 |
| 2026-06 | **8,506** | **−258** | 897,498 |

**−6.8%.** Impressions −14% across the same window while CTR rose 0.87% → 0.95%.

### A fall is not automatically failure — read this before reacting to the chart

**We deliberately dropped a lot of products and specialised, and sales improved**
(owner, 2026-07-16). Fewer products means fewer pages, fewer impressions and
fewer clicks **by design**. Some of this decline is the price of a decision that
worked. Clicks punish that decision; the P&L does not.

The fall has at least three causes and **GSC cannot separate them**:

| Cause | Evidence | Ours? |
|---|---|---|
| Deliberate delisting | `products` clicks −31% YoY | Yes — and good |
| Informational bleed | size guide 475 → 220 while ranking *better* | No — headwind |
| Lost ground | `collections` −17% YoY, but CTR 0.51% → 1.27% | Unclear |

With no GA4 there is no conversion data to weigh these against revenue, so
**clicks stay the proxy while being a knowingly imperfect one**. Do not report the
trailing 12 falling as failure without saying which of the three it is — and if
you cannot say, say that.

**First target: stop the fall.** A flat trailing 12 is a win from here. Pages
built in July show up 4–8 weeks later, so the first honest reading is the trailing
12 to **Sept/Oct 2026**. Targets beyond "stop the fall" are deliberately not set
yet — see the priorities in State first.

## What we can actually change

Position, impressions and clicks are **outputs**. Google decides them. The only
levers in our control:

- page title and meta description (what shows in the result)
- the collection/page description text
- which products sit in a collection
- where we link to it from, and the anchor text

## Running a session

| Ask | Command |
|---|---|
| **Progress report + breakdown** | `python seo/weekly.py` — scoreboard, organic vs paid, site → type → page |
| **Are we up or down?** | `python seo/weekly.py --trend` — the chart: trailing 12 + every month GSC holds |
| **Collections and their SEO position** | `python seo/collections_seo.py` — every Shopify collection, its position and clicks |
| **What should we work on?** | `python seo/queries.py` — terms with volume and no page built for them |
| **What does this page rank for?** | `python seo/queries.py --page /collections/x` |
| **What ranks for this term?** | `python seo/queries.py --query "arizona birkenstock"` |

`weekly.py --type collections` narrows every section to one type. `--top N` sets
rows. `collections_seo.py --unranked` shows only collections earning nothing —
GSC alone can't tell you these exist, since it only returns pages that earned an
impression.

Windows differ by level on purpose: the site does ~230 clicks/week so 7d reads
cleanly, but a single page does ~6 clicks/week where 7d is pure noise. Page level
is 28d.

**Paid is an outline only, and organic share is context, not a target.** You own
the denominator: turn ad spend up and organic share falls even if SEO is winning.
Score on organic clicks. Two limits worth knowing — `google_campaign_daily` is
campaign-level (one campaign is ~96% of clicks), so paid can never be compared to
organic at page or query level; and it is a manual CSV import that lags GSC, so a
window marked partial is missing days, not losing traffic. Refresh via
`google-ads/how-to-run.md`.

## What we store

**Nothing.** GSC serves 16 months retroactively at any granularity, so any past
week is available on demand and no window ever closes on us. Storing it would
duplicate a better source.

The exception is `CHANGELOG.md` — what we changed, when, and what we expected.
GSC has 16 months of traffic and no idea what we did to cause it. Log the
expectation *before* the result is known.

**The scoreboard will force a second exception, and it is a real one.** A
trailing 12-month total needs 12 months to compute, so GSC's 16 months yield only
about **five** points — enough to see the current direction, never a multi-year
trend. Past 16 months GSC is not "a better source", it is *no* source, so storing
monthly totals would not duplicate anything. The fix is small: **one row per
month (month, clicks, impressions) — 12 rows a year**, backfilled once from GSC
while the window still reaches back. Not built yet; decide before the oldest
months age out, because once they do they are gone for good.

## What we know

Established 2026-07-16, against data, not assumption:

- **Average position ~11 is page two.** We are not being outranked so much as
  shown where nobody scrolls. Impressions are not the constraint — 262k of them
  produce ~3k clicks.
- **The pages rank for the right queries.** No relevance mismatch to fix (checked
  at query level on the top low-CTR pages).
- **The CTR ceiling is low, and it caps the whole title/meta play.** Measured
  2026-07-16 (see "The curve" below): ranking 5–7 earns ~1.8%, 7–11 earns ~0.7%.
  Everything below its own band's median, added up, is **~+89 clicks/28d — about
  8% of organic, and only if every gap closes perfectly.** Rewriting titles is
  not a plan; it is an afternoon for maybe 40 clicks. The money is in ranking or
  in new pages.
- **Indexing is settled.** Indexed pages earn, unindexed earn nothing (0 clicks
  across 21 pages). All earning collections are indexed. Not the constraint.
- **Traffic is extremely concentrated.** Top 3 pages are ~51% of clicks, top 20
  are ~78%. Those top three are a collection, the homepage and an info page — one
  of each type. The Birkenstock size guide alone is ~32% of site impressions,
  more than all 984 product pages combined, and converts worst of the three.
- **Specific, intent-led collections are the engine** — the original strategy was
  right. `birkenstock-slippers` (8 products) earns 111 clicks; the general
  `birkenstock-sandals` (136 products) ranks 2.5 and earns 64.
- **Aggregators are worthless.** `all`, `sandals`, `full-price` are near-supersets
  of collections Google already indexes. It declines to index them. Nothing lost.
- **Informational is bleeding; collections are winning.** May+Jun year over year:
  `pages` clicks **−46%** on only −14% impressions, while the collection
  `birkenstock-narrow-fit-sandals` **doubled, 172 → 333**. The size guide alone
  went **475 → 220 clicks while its rank improved 14.2 → 10.4** — same
  impressions, CTR halved 0.88% → 0.40%. Something now answers the question
  before the user reaches us; AI Overviews is the suspect but GSC cannot prove
  the mechanism. **That one page is close to our entire year-over-year decline.**
  The strategy conclusion is not "stop informational" — it is that collections
  are the engine and informational is a headwind we do not control.
- **Position is no longer comparable year over year.** If an AI Overview now sits
  atop a SERP, "position 10" in 2026 is further down the screen than "position 10"
  in 2025. The size guide ranking *better* while earning *half* is exactly that
  signature. Compare position within a period, never across years — and never
  conclude a page improved because its number fell.
- **Collections lost two-thirds of their impressions and it barely mattered.**
  May+Jun YoY: 220,008 → 72,582 impressions (−67%) for only −17% clicks, CTR
  0.51% → 1.27%. Junk impressions being stripped, not traffic lost. Do not raise
  an alarm about impressions without checking what happened to clicks.
- **Difficulty is competition, not our page.** Established three times over:
  `narrow` ranks 7 and `regular` has no searches at all; the size guide ranks 5 on
  a question nobody answers and 18 on `size chart` that everyone has; Goor ranks
  8.7 while Rieker ranks 37. Before assuming a page is weak, ask who else is
  fighting for the term. See "Future-proofing" under State.
- **Products are a long tail** — 984 pages at 0.5 clicks each. Only workable
  systematically, or not at all.
- **Blogs are dead** — 9 pages, 2 clicks, 2,005 impressions.
- **High CTR is not automatically headroom.** `birkenstock-sandals` ranks 2.2 at
  8.52% CTR on 352 impressions. It has already won; there is no volume behind the
  term. Check impressions before reading a good CTR as opportunity.
- **No conversion data exists.** No GA4. GSC stops at the click. Clicks are the
  honest proxy until someone wires up GA4.

## Ruled out (and why)

- **Internal links as a lever — unproven, not disproven.** GSC's `referringUrls`
  counts sitemaps, self-pagination and recommendation widgets as links. The top
  earner shows "1 referring URL" and it is its own `?page=2`. The field cannot
  answer whether links move rankings. Settling it needs a real crawl of the
  site's own `<a href>` map.
- **Orphan-fixing.** Same broken column. `birkenstock-milano` shows 0 referring
  URLs and earns 73 clicks.
- **Re-organising collections.** The intent-led structure is the thing that works.
  Re-organising trades accumulated authority for a hypothesis.
- **Ad conversion rates do not transfer.** Paid converts at 2.60% because it sits
  at the top with an image. You cannot inherit that by ranking 11th.

## Traps

- **Seasonality.** Sandals peak in July. Any before/after over the 4–8 weeks SEO
  takes will be swamped by season. Pilot on season-neutral pages and keep a
  control group you deliberately don't touch, so you measure against the site's
  trend rather than a page's past self.
- **Concentration.** One page is ~40% of collection traffic. Do not run
  experiments on `birkenstock-narrow-fit-sandals`.
- **Weekly page-level clicks are noise.** ~6 clicks/week on a typical page. Read
  28-day windows at page level, and trends not verdicts.

## Scripts

| Script | Does |
|---|---|
| `weekly.py` | **The report.** Organic vs paid, site → type → page, CTR curve. |
| `queries.py` | **The miner.** Finds the next task: volume with no page built for it. |
| `collections_seo.py` | Every Shopify collection with its GSC position and clicks. |
| `gsc_client.py` | GSC auth + `SITE_URL`. Uses the merchant-feed service account. |

**How `queries.py` finds work.** GSC is a mirror, not a market — it only reports
what we already appear for, so it is blind to greenfield and everything it finds
is proven demand on proven authority. It clusters queries by intent-carrying word
and, for each term with volume, asks whether any collection or info page is
*named* for it. When none is, Google does not decline to rank us — it scatters
the term across whatever product pages exist. **Volume + spread over many pages +
no page named for it = build the page.** That is exactly how Arizona was found:
2,446 impressions, 143 pages, no collection, 15 clicks. A term with volume, *few*
pages and no named page is a different thing — a ranking problem, not a missing
page. Query counts never sum to page totals; GSC anonymises rare queries (the
size guide names only 7,683 of its 23,371 impressions).

Nothing is scheduled — these are reports you read, not jobs that collect.

## State

### Next task — build `/collections/birkenstock-arizona`

Decided 2026-07-16. Arizona is the biggest seller and **has no collection page.**

**The evidence.** `arizona birkenstock` (443 impr) and `arizona birkenstock
womens` (371 impr) are browse queries. With no Arizona page to serve, Google
scatters them across ~43 individual colour/variant product pages at 1–29
impressions each, all earning **zero clicks**. Arizona demand totals **2,441
impressions / 28d and returns 15 clicks (0.61% CTR)**. The 3–5 position band on
this site earns ~1.97%.

**Expected: 30–50 clicks/28d.** Revised down from 40–60 on 2026-07-16 after
checking Milano, which is the template and the only real evidence we have:

| Milano — a style collection that works | |
|---|---|
| Impressions | 4,617 (more than Arizona's 2,446) |
| Clicks | 57, from **4 products** |
| Position | 8.4 — and **17.6** for `birkenstock milano` itself |
| CTR | 1.23% |

**Do not expect position 3–5.** The earlier 40–60 estimate applied the 3–5 band
median (1.97%) to Arizona's impressions; Milano shows a style collection settles
around 9th at ~1.2%. Arizona's current 2,446 impr at 1.23% is only ~30 clicks.
The upside above that is a collection earning *more* impressions than scattered
product pages do — Milano pulls 4,617 — which would put it near 50. Arizona is
also the most competitive style in the range, so it may land below Milano.

**The famine is chronic, which is the real argument.** 12 months of Arizona:
never above 26 clicks in a month, and *worsening* as impressions grow — Aug 2025
was 1,336 impr → 26 clicks (1.95%); Jun 2026 was 1,919 impr → 9 clicks (0.47%).
This is not a blip.

**Caveat, so the result is read honestly.** Many of those product-page rows sit at
*exactly* position 5.0, which reads as a product-carousel slot rather than 43 blue
links. Carousel impressions may never have been clickable, so treat the 2,441 as
a soft ceiling, not a pool sitting there waiting.

**Then, and only after:** `birkenstock-arizona-narrow-fit` as a filtered child.
Right pattern — narrow is the moat — but ~294 impr/28d, worth ~6 clicks. Nearly
free once the parent exists; not worth a standalone build.

**Not this:** a Regular page. Nobody searches "regular" — 32 queries, 118 impr,
2 clicks across every phrasing. It is the unmarked default, not an intent. Biggest
seller ≠ search demand.

Log the row in `CHANGELOG.md` on the day it ships, with the expectation above
copied across before the result is known.

### Second task — a page answering "why is there no Birkenstock size 6 UK?"

Decided 2026-07-16, after the Arizona page. **Do not start both at once** — one
change at a time or neither result is readable.

**The evidence.** ~750 impr/28d across every phrasing, and the generic size guide
already ranks **top-7 on almost all of them**:

| Query | Impr | Pos |
|---|---|---|
| why dont birkenstock do size 6 | 154 | 5.4 |
| birkenstock size 6 | 119 | 11.5 |
| why do birkenstock not do size 6 | 110 | 5.5 |
| do birkenstock do size 6 | 98 | 7.2 |
| why don't birkenstock do size 6 | 64 | 5.4 |
| why does birkenstock not have size 6 | 57 | 5.2 |
| birkenstock no size 6 | 51 | 6.5 |
| size 6 birkenstocks | 48 | 20.6 |
| do birkenstock do a size 6 | 46 | 5.0 |

`why don't birkenstock do size 6` earns **4.69% CTR** — near the best on the site.
A page ranking 5th *by accident*, on content that only mentions the answer in
passing, is the clearest signal available that a dedicated page would win.

**Expected.** 30–45 clicks/28d at a top-3 rank. 4–8 weeks.

**Kept at priority 2 on 2026-07-16 against the analysis, by the owner's call.**
The informational headwind below is real and was argued as a reason to demote
this. The counter, and it is a good one: **AI may cite it and send people our
way.** Being the page an Overview quotes is a position worth holding, and a
specific well-answered question is more citable than a generic size chart nobody
can differentiate. Cheap to try, ranks 5th already, small downside. Do not demote
it on the informational-decline argument alone — that argument was heard.

**Why a separate page and not more size-6 content inside the size guide.** A page
has **one title**, and the title is the lever. Searchers see `Birkenstock Size
Guide | Brookfield Comfort` against "why don't birkenstock do size 6" — it does
not look like an answer, which is why most phrasings convert at 0% while ranking
5th. An exact-match title cannot come from inside the size guide, whose title has
to be about size guides. Expanding inside improves the content and can never fix
the snippet.

**The risk, and the kill criterion.** The new page must beat *our own size guide*,
which already ranks ~5 with real authority. Google may keep serving the incumbent.
So: link the size guide to the new page with anchor text matching the question,
**measure the two as one cluster**, and if the new page has not overtaken the size
guide on size-6 queries within 8 weeks, fold the content back and stop. A new page
earning 30 clicks while the size guide loses 30 is a wash that reads like a win.

**Why this and not "blogs".** The 7 existing blog posts are dead (1 click, 149
impr) — that kills those 7 posts, not the format. The size guide is an *info* page
and holds 31% of site impressions. **Question-shaped Birkenstock content is what
ranks here.** Generic listicles are not the same thing and should not be inferred
from this.

**Intent is better than it looks.** Someone asking why there's no size 6 is
mid-purchase and confused about sizing, not browsing idly. Still informational —
and with no GA4 we cannot prove it converts. Clicks remain the proxy.

### Third task — `/collections/birkenstock-zermatt`

Decided 2026-07-16. Same shape as Arizona: a style with demand and no collection.
**Zermatt sells all year round** — the owner's read, and the data agrees.

`birkenstock zermatt` is **432 impr at position 6.1 earning 2 clicks**; the whole
term is 1,270 impr / 12 clicks / pos 6.6, best served by `birkenstock-slippers`.
A `zermatt-narrow` collection exists but takes ~7 impressions — Google does not
serve it. Ranking 6th already, with no page built, is the Arizona signal at a
better starting position.

**Expected: 15–25 clicks/28d.** Smaller than Arizona; it starts from a better rank
but has half the demand. Milano's ~1.2% remains the model.

**The step change nobody has explained.** Impressions went ~200/month → 1,089 in
Jan 2026 and have held ~1,400+ since, peaking in *spring*, not winter. Clicks
never moved (12–28/month throughout). A 7× impression rise with flat clicks is
not understood, and building for it without knowing why is a bet, not a plan.
Worth ten minutes with `--contains zermatt` over a 16-month window first.

### Future-proofing — the answer to "what after Birkenstock"

Recorded 2026-07-16. **Not current work.** This is the strategic answer to not
being stuck behind one brand for years, so it does not have to be re-derived.

**Diversification is available, and the demand is already arriving.** Non-brand
queries are **1,112 queries, 13,584 impr — 33% of all impressions — earning 62
clicks (11%)**. A third of our visibility is not Birkenstock and converts at
0.46%. The gap is pages and products, not authority.

**Difficulty is competition, not brand.** The third time this lesson has appeared
(after narrow-vs-regular and the size guide's head terms):

| | Impr/28d | Pos | Clicks | Read |
|---|---|---|---|---|
| Birkenstock | — | 6–9 | — | The moat |
| `goor` | 2,865 | 8.7 | 11 | Ranks. Obscure = winnable. |
| `cipriata` | 976 | 10.4 | 5 | Ranks. |
| `boulevard` | 786 | 8.5 | 3 | Ranks. |
| Rieker / Lunar / Roamers | — | 22–47 | ~0 | Everyone sells them. Not winnable. |

**Obscurity is itself a moat** — the same shape as the Birkenstock Amazon-ban,
just smaller. So the path is low-competition niches, **not** big brands. Do not
try to SEO our way into Rieker; that is what position 37 means.

**Birkenstock authority is downstream of the channel moat, not of any SEO work.**
Birkenstock is Amazon-banned, so its demand has nowhere online to go but search.
Rieker demand goes to Amazon, Schuh, rieker.com. This is why Shopify went 99%
Birkenstock — structural, not accidental.

**The economics — why this is worth anything at all.** Goor, Cipriata and
Boulevard are **UKD stock: much lower margin**. That does not sink it, it is the
whole point. At £0.45/click, a few pounds of margin needs a ~10%+ conversion rate
for paid to break even, and nothing converts at 10% — **paid can never work on
UKD**. Organic clicks are free, so any conversion is profit. **SEO is the only
acquisition channel that can ever work on low-margin stock.** Judge these pages
against zero, not against Birkenstock.

Scale check before anyone gets excited: those three footholds are ~4,627 impr
earning 19 clicks. At Milano's ~1.2% that is ~55 clicks/28d — a few extra sales a
month at low margin. Free and compounding, but small. Worth an hour each, not a
quarter.

**Velcro trainers — dropped 2026-07-16, do not revive.** `mens-velcro-trainers`
has **0 products and 4,338 impressions** at position 12–15, which looks like the
biggest non-Birkenstock opportunity on the site. It fails twice, independently:

1. **Trademark.** Velcro is a registered mark; the compliant terms are "riptape"
   or "hook and loop". The demand is entirely on the word we cannot use —
   `velcro` 3,578 impr vs **`riptape` 0**, `hook and loop` 76. Nobody searches the
   safe words; they are retailer jargon. SEO cannot route around this. Whether to
   use the mark anyway is a legal/brand call, not an SEO one.
2. **Economics.** UKD, "low profit, if any profit at all" (owner, 2026-07-16).
   Even free clicks cannot rescue a zero margin.

The empty collection is a live defect regardless — Google shows an empty page to
thousands a month. Fill it or delete it; do not leave it.

### Candidates behind the three priorities

Found by `queries.py` 2026-07-16. **The pattern generalises: a Birkenstock style
with demand and no collection.** Milano proves the model (4 products, 57 clicks).
Re-run the miner before picking these up — they are a queue, not a plan.

| Term | Impr/28d | Clicks | Pos | Pages | Note |
|---|---|---|---|---|---|
| `madrid` | 833 | 6 | 8.1 | 41 | Style, no collection. Same shape as Arizona. |
| `barbados` | 472 | 2 | 9.9 | 7 | Style, no collection. |

**`gizeh` is the counter-example.** It *has* a collection (22 products) and earns
0 clicks — but `birkenstock gizeh` is only 6 impressions, so its 950 are pure long
tail. A collection cannot rescue a term with no head demand. Check the head term
with `--query` before building.

### What the size guide taught us — resolved 2026-07-16

The old open question (23,371 impr but only 577 from `size guide` queries) is
answered: **it is a long-tail magnet.** 1,414 named queries, and query-level only
accounts for 7,683 of its 23,371 impressions — GSC anonymises the rest, so
**two-thirds of that page's traffic is from searches too rare to name.** Mostly
size conversion (`birkenstock 260`, `birkenstock size 40 in uk`).

**It is losing its own name:** `birkenstock size chart` (458 impr) ranks **18.6**,
`birkenstock size guide` (314) ranks **15.6**, `birkenstock sizing` (230) ranks
**22.5** — while the size-6 question in the same page ranks **5**. The whole
`size` cluster is 5,454 impr at position 14.5, the biggest on the site.

**This is competition, not dilution — retracted 2026-07-16.** It was first written
up as "two pages in one", implying that splitting the question out would free the
head terms. That is almost certainly wrong. The question ranks 5th because almost
nobody answers it; the head terms rank 15–22 because *everyone* has a size chart,
birkenstock.com included. **Same lesson as narrow vs regular: difficulty is about
competition, not about our page.** Do not expect the size-6 page to lift `size
chart`. Those head terms are contested and probably not winnable — no task here.
