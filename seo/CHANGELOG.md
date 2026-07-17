# SEO change log

What we changed, when, and what we expected. GSC has 16 months of traffic and no
idea what we did to cause it — this file is the other half.

Log the expectation *before* the result is known. In 6 weeks the season will
offer a story either way, and a prediction written afterwards is worthless.

| Date | URL | What changed | Expected | Outcome |
|---|---|---|---|---|
| 2026-07-17 | /collections/birkenstock-arizona | Found the collection already existed (70 products, ranks pos 4) but was linked from nowhere, earning only 5 impr/28d; a duplicate `birkenstock-arizona-1` created 2026-07-17 was resolved. Added to main menu, linked from `birkenstock-sandals`, narrow-fit removed from the result list. | This is a discovery fix, not a new page — impressions should climb sharply toward the ~2,441/28d already scattered across product pages, with clicks following at Milano's ~1.2% CTR (~30 clicks/28d) within 4-8 weeks. | |
| 2026-07-17 | /pages/birkenstock-size-6 | New page built and indexing requested. Answers "why doesn't Birkenstock make a UK size 6" directly, gives the EU39/EU40 conversion, links to the full size guide and to `birkenstock-arizona`. Size guide already ranks top-7 on most size-6 phrasings by accident (`why dont birkenstock do size 6` pos 5.4, 4.69% CTR on the top query) but with a title that doesn't match the question. | 30-45 clicks/28d at top-3 within 4-8 weeks. Kill criterion: must be measured as one cluster with the size guide, and must overtake it on size-6 queries within 8 weeks or the content gets folded back into the size guide and this page retired. | |
| 2026-07-17 | 8 thin/dead collections (see note) | Deleted `mens-velcro-trainers` (empty, 0 products), `rieker-summer-sandals-2025-clearance-sales`, `womens-work-shoes-1`, `kids-wedding-shoes`, `page-boy-wedding-shoes`, `mens-brown-shoes-for-wedding`, `mens-wedding-shoes`, `nhs-care` — all ≤4 products and ~0 clicks. Link-checked first (`link_check.py` crawl of collections+pages+blogs); the only 2 internal links (mens-trainers metafield → velcro; a blog post → mens-brown-wedding) were removed before deleting. No redirects — dead pages with no traffic or links to preserve, so a clean 404 is the correct signal (redirect ≠ SEO gain when there's no equity to pass). | Hygiene, not a traffic play — no click gain expected. Removes empty/thin pages from the index, frees crawl budget, tidies the site. The one thing to watch: no *ranked* page accidentally lost a link (checked — it didn't). | |
| 2026-07-17 | /collections/birkenstock-madrid | Existing collection (14 products) stuck at **"Crawled – currently not indexed"** (URL Inspection API; last crawl 2026-02-04), 0 impressions — Google saw it and declined to index. Deliberately given the **same treatment as Arizona** so the two can be compared: linked from the main menu, `birkenstock-sandals`, and the size guide (anchor "Birkenstock Madrid"); re-indexing requested in GSC. Demand: 818 impr/28d, browse-intent (women's, eva, narrow, brown, white), currently 6 clicks / 0.73% scattered across product pages. | **Gate 1 (indexed):** flip from crawled-not-indexed → indexed within ~1–2 weeks of the reindex request (Arizona did this). **Gate 2 (clicks):** if it ranks, impressions climb toward ~818, clicks at Milano's ~1.2% (~10–20/28d) by 4–8 weeks. **Honest risk:** indexed ≠ trafficked — gizeh/mayari/pasandena are indexed and earn ~0, so Gate 1 can pass while Gate 2 fails. Compare to Arizona **at equal age** (weeks-since-link), on **rate not raw clicks** (Arizona has ~3× the demand). | |
| | | | | |

<!--
Example:
| 2026-07-20 | /pages/birkenstock-size-guide | Rewrote title + meta description | CTR 0.49% -> 1.0%+ within 4-6 weeks; position unchanged | |
-->
