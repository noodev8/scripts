# SEO Experiments — Progress Tracking

Three experiments launched 2026-07-17. **All closed 2026-10-20 (data to 2026-10-17):
Arizona failed, Madrid failed, size-6 blog worked and is kept.** No experiments are
live, and SEO is no longer actively worked (owner, 2026-10-20 — README, "Status").
The commands and tables below are the record, not a weekly job.

- **Arizona / Madrid — why they failed is now known:** almost all style-search
  impressions are the **free Shopping grid** (MERCHANT_LISTINGS), where a collection
  page cannot appear. README, "The real problem", has the split.
- **Size-6 — kept, not folded back.** The read due 2026-09-08 was taken 2026-10-20:
  position recovered to well under the ≤4.5 target and held, and the blog now beats
  the size guide on the question phrasings. Detail in the size-6 table below.

## Quick Check (run weekly — copy & paste these commands)

```bash
# Arizona: keyword cluster + collection page
python seo/queries.py --contains arizona | grep "^\"arizona\""
python seo/queries.py --page /collections/birkenstock-arizona | head -2

# Madrid: keyword cluster + collection page
python seo/queries.py --contains madrid | grep "^\"madrid\""
python seo/queries.py --page /collections/birkenstock-madrid | head -2

# Size Guide: overall page + specific size-6 term
python seo/queries.py --page /pages/birkenstock-size-guide | head -2
python seo/queries.py --query "why don't birkenstock do size 6" | grep "size-guide"
```

**For Size Guide size-6 section:** Run the second command, look for the size-guide row and copy clicks/position.

## Tracking Table

**For each experiment, run TWO queries and log BOTH:**
1. The keyword cluster (e.g., `--contains arizona`)
2. The collection page itself (e.g., `--page /collections/birkenstock-arizona`)

### Arizona Collection
**Baseline (before change):** Collection rank 4, **5 impr/28d**  
**What:** Linked to menu + Sandals. Watch for impressions to consolidate FROM scattered products TO the collection.

| Date | Keyword "arizona" (cluster) | /collections/arizona (page itself) | Direction |
|---|---|---|---|
| 2026-07-27 | 13 clicks, 2,457 impr | 0 clicks, 1 impr | ❌ Collection lost ground (5→1) |
| 2026-07-30 | 13 clicks, 2,457 impr | 0 clicks, 1 impr | ❌ Still flat |
| 2026-08-08 | 13 clicks, 2,457 impr | 0 clicks, 2 impr | ❌ **CLOSED — failed.** Cluster identical 3 checks running. `arizona birkenstock` pos 4.0 / 549 impr / 0 clicks; the product page `arizona-synthetic-sand` takes it instead at 40.91% CTR, pos 2.1 |
| 2026-10-17 | 1 click, 1,095 impr | 0 clicks, 2 impr | ❌ Still dead. **892 of the cluster's impressions are the free Shopping grid** (pos 2.1, 1 click): the "pos 1–3, 0 clicks" rows are grid tiles, one per size. Monthly: Sep 2025 583 impr / 8 clicks → Sep 2026 **4,872 / 2** |

### Madrid Collection
**Baseline (before change):** "Crawled, not indexed" in Shopify URL Inspection  
**What:** Same linking as Arizona. Watch for crawl-status flip + position improvement.

| Date | Keyword "madrid" (cluster) | /collections/madrid (page) | Direction |
|---|---|---|---|
| 2026-07-27 | 6 clicks, 733 impr | 0 clicks, 16 impr | ⚠️ Keyword cluster has clicks; page buried |
| 2026-07-30 | 6 clicks, 733 impr | 0 clicks, 16 impr | ⚠️ No movement |
| 2026-08-08 | 5 clicks, 620 impr | 0 clicks, 34 impr | ❌ **CLOSED — Gate 1 passed, Gate 2 failed.** Page now served (16→34 impr) but still 0 clicks, and the cluster *shrank*. `birkenstock women's madrid` pos 3.2 / 135 impr / 0 clicks |
| 2026-10-17 | 0 clicks, 105 impr | 0 clicks, 0 impr | ❌ Gone backwards — the page is no longer served at all. 72 of 98 classified impressions are the free Shopping grid. Monthly: Sep 2025 154 impr / 5 clicks → Sep 2026 822 / 2 |

### Size Guide — Size-6 Content
**Baseline (before change):** Size guide ranks top-7 on size-6 queries; content mentions it but title doesn't match.  
**What:** Added size-6 specific content to /pages/birkenstock-size-guide on 2026-07-17. Watch CTR on size-6 queries cluster.

| Date | /pages/birkenstock-size-guide overall | Size-6 queries only (CTR trend) | Direction |
|---|---|---|---|
| 2026-07-27 | 26 clicks, 7,602 impr (0.34% CTR) | ~6 clicks on size-6 queries, pos 5-11 | ✅ Size-6 content helping? |
| 2026-07-30 | — | — | — |
| 2026-08-08 | 72 clicks, 19,908 impr (0.36% CTR), pos 11.8 | Blog now a top-15 site page: 10 clicks, 1,008 impr, pos 5.4. Cluster 9 clicks, 1,088 impr | ✅ Working — ⚠️ but fold-back question open |
| 2026-10-17 | 16 clicks, 4,767 impr (0.34% CTR), pos 14.8 | Blog is the **#4 page on the site**: 21 clicks, 1,661 impr, **pos 4.0**. On the question phrasings it ranks **1.4–2.2**, size guide 5.1–6.5 | ✅ **CLOSED — works, kept.** Position held after the rewrite (no second decay), so the kill criterion is not met |

**Size-6 honest read, 2026-10-20 (data to 2026-10-17, 28d).** The blog has overtaken
the size guide on the questions it was built for:

| query | blog clicks / impr / pos | size guide impr / pos |
|---|---|---|
| `why dont birkenstock do size 6` | 2 / 46 / **1.5** | 37 / 6.5 |
| `why don't birkenstock do size 6` | 0 / 10 / **1.9** | 7 / 5.1 |
| `why do birkenstock not do size 6` | 0 / 19 / **1.5** | — |
| `why does birkenstock not have size 6` | 0 / 16 / **1.4** | — |
| `birkenstock size 6` | 0 / 55 / 5.0 | — |

Position target (≤4.5 and holding) met. Clicks, 21/28d, are just under the
25–35/28d hope, on page impressions (1,661/28d) slightly *above* the stub's July
rate (~1,400) — so the demand held into October and the rewrite lifted CTR
(~0.7% → 1.26%). (The per-query rows above name only 356 of those impressions; GSC
anonymises the rest.) Still an info page (~0.7% conversion), so its value is
visibility and AI citation, not sales.

**Size-6 detail, 2026-08-08.** The blog is earning from a standing start, but the
kill criterion is **not** met — on the top phrasing the size guide has retaken it:

| `why don't birkenstock do size 6` | clicks | impr | pos |
|---|---|---|---|
| /pages/birkenstock-size-guide | 1 | 102 | **5.1** |
| /blogs/…-uk-size-6-brookfield-comfort | 0 | 73 | **5.9** |

**Daily trend, blog only (2026-07-18 first day live → 2026-08-08).** Impressions
held flat at ~50/day for three weeks — the page is being served consistently. But
**position is drifting the wrong way** and clicks are thinning with it:

| Week live | avg impr/day | clicks | avg pos |
|---|---|---|---|
| 1 (07-18→07-24) | 46 | 5 | **4.9** |
| 2 (07-25→07-31) | 48 | 3 | **4.8** |
| 3 (08-01→08-06) | 58 | 2 | **6.4** |

10 clicks in 22 days live ≈ **12.7 clicks/28d run-rate, against a 30–45 target**,
and down from the ~19 run-rate at the day-10 interim. Impressions are *rising*
while position falls, so this is not a demand problem — it is slipping down the
page. (Ignore 08-07/08-08, 1–2 impr: GSC's last days are incomplete, not a cliff.)

**⚠️ Everything above is the STUB's performance (07-18 → 08-08).** Content
rewritten 2026-08-11 — treat 2026-08-11 as a new baseline and do not compare
post-rewrite numbers to the interim run-rates. Next read **2026-09-08**, on
**position** first.

At the day-10 interim the blog led 3.7 vs 5.7; it has since slipped behind. Both
pages still surface on the same queries, so they are **splitting the cluster, not
replacing it** — which is the condition the CHANGELOG says triggers folding the
content back into the size guide and retiring the blog. Call due **2026-08-14**.

## Decision Rule

- **Arizona/Madrid:** If clicks flat for 3+ weeks after Gate 1 (indexing) succeeds, pause.
  → *Both triggered 2026-08-08 and are closed.*
- **Size-6:** If page doesn't appear by week 2 (by ~Aug 14), check indexing status in GSC.
  → *It appeared immediately; the open question is fold-back, not indexing.*
  → *Fold-back answered 2026-10-20: no — the blog overtook the size guide and is kept.*
