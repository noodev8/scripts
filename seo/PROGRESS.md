# SEO Experiments — Progress Tracking

Three active experiments launched 2026-07-17. Track weekly with the command below.

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

### Madrid Collection
**Baseline (before change):** "Crawled, not indexed" in Shopify URL Inspection  
**What:** Same linking as Arizona. Watch for crawl-status flip + position improvement.

| Date | Keyword "madrid" (cluster) | /collections/madrid (page) | Direction |
|---|---|---|---|
| 2026-07-27 | 6 clicks, 733 impr | 0 clicks, 16 impr | ⚠️ Keyword cluster has clicks; page buried |
| 2026-07-30 | 6 clicks, 733 impr | 0 clicks, 16 impr | ⚠️ No movement |

### Size Guide — Size-6 Content
**Baseline (before change):** Size guide ranks top-7 on size-6 queries; content mentions it but title doesn't match.  
**What:** Added size-6 specific content to /pages/birkenstock-size-guide on 2026-07-17. Watch CTR on size-6 queries cluster.

| Date | /pages/birkenstock-size-guide overall | Size-6 queries only (CTR trend) | Direction |
|---|---|---|---|
| 2026-07-27 | 26 clicks, 7,602 impr (0.34% CTR) | ~6 clicks on size-6 queries, pos 5-11 | ✅ Size-6 content helping? |
| 2026-07-30 | — | — | — |

## Decision Rule

- **Arizona/Madrid:** If clicks flat for 3+ weeks after Gate 1 (indexing) succeeds, pause.
- **Size-6:** If page doesn't appear by week 2 (by ~Aug 14), check indexing status in GSC.
