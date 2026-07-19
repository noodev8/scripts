# Shopify products with only one image

**Run:** 2026-07-19 · **Source:** live Shopify Admin GraphQL (product-level `images`, first 20)
**Script:** `python seo/find_single_image_groupids.py` · raw data: `seo/single_image_groupids.csv`

## Headline

- **273** active Shopify handles checked (`skusummary.shopify = 1`).
- **66** groupids (24%) have **fewer than 2 images** — every one of them has **exactly 1**.
- **Zero** products are missing their main image, so this is purely a *no secondary/gallery shot* gap, not a broken-listing gap.

A single-image PDP is weaker for both conversion and SEO (fewer image assets to rank in Google Images / Shopping, less on-page richness). Adding alt shots is a low-risk content win.

## Where it clusters

Heavily Birkenstock. Arizona alone is ~30% of the list; Birk styles together are ~40 of the 66.

| Style | Count |
|---|---:|
| ARIZONA | 20 |
| ZERMATT | 6 |
| MADRID | 5 |
| GIZEH | 5 |
| IVES | 4 |
| BEND | 3 |
| BLAZE | 3 |
| BARBADOS | 2 |
| HONOLULU | 2 |
| MAYARI / SYDNEY | 1 each |
| Rieker (14450, 17659 ×2) | 3 |
| Free Spirit (Cleveland, Fairmont) | 2 |
| Goor (B710AP, M410B, M968BC) | 3 |
| Strive (Capri 4, Talia) | 2 |
| Lunar (Evie, Renoir, Cluster) | 3 |
| Roamers (M404A) | 1 |

## Full list

| groupid | images | handle |
|---|---:|---|
| 0040301-MADRID | 1 | birkenstock-madrid-sandals-patent-black-regular-fit-0040301-madrid |
| 0040731-MADRID | 1 | birkenstock-madrid-sandals-birko-flor-white-40731 |
| 0051191-ARIZONA | 1 | birkenstock-arizona-two-strap-natural-leather-sandals-regular-width-black-0051191-arizona |
| 0051703-ARIZONA | 1 | birkenstock-arizona-sandals-dark-brown-0051703 |
| 0051753-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-blue-narrow-fit-0051753-arizona |
| 0051791-ARIZONA | 1 | birkenstock-arizona-sandals-birko-flor-black-51791 |
| 0071793-MAYARI | 1 | unisex-birkenstock-mayari-sandals-black-narrow-fit-71793 |
| 0128161-MADRID | 1 | birkenstock-madrid-eva-sandals-black-regular-fit-0128161-madrid |
| 0128163-MADRID | 1 | birkenstock-madrid-eva-sandals-black-narrow-fit-0128163-madrid |
| 0128183-MADRID | 1 | unisex-birkenstock-madrid-eva-sandals-white-128183 |
| 0128221-GIZEH | 1 | birkenstock-gizeh-eva-sandals-white-regular-fit-0128221-gizeh |
| 0129423-ARIZONA | 1 | unisex-birkenstock-arizona-eva-sandals-black-narrow-fit-129423 |
| 0143621-GIZEH | 1 | birkenstock-adult-gizeh-birko-flor-sandals-blue-143621 |
| 1001498-ARIZONA | 1 | birkenstock-arizona-eva-sandals-anthracite-dark-grey-narrow-fit-1001498-arizona |
| 1005293-ARIZONA | 1 | birkenstock-arizona-sandals-birko-flor-patent-white-1005293 |
| 1009920-ARIZONA | 1 | birkenstock-arizona-sandals-birko-flor-graceful-pearl-white-regular-fit-1009920-arizona |
| 1015084-ZERMATT | 1 | birkenstock-zermatt-cork-latex-slippers-grey-regular-fit-1015084-zermatt |
| 1015092-ZERMATT | 1 | birkenstock-zermatt-shearling-felt-slippers-grey-regular-fit-1015092-zermatt |
| 1015398-BARBADOS | 1 | birkenstock-barbados-eva-slide-on-sandals-black-regular-fit-1015398-barbados |
| 1015399-BARBADOS | 1 | birkenstock-barbados-eva-slide-on-sandals-white-regular-fit-1015399-barbados |
| 1015487-HONOLULU | 1 | birkenstock-honolulu-eva-sandals-black-regular-fit-1015487-honolulu |
| 1016145-GIZEH | 1 | birkenstock-gizeh-sandals-taupe-narrow-fit-1016145-gizeh |
| 1016570-ZERMATT | 1 | birkenstock-zermatt-slippers-shearling-lined-grey-regular-fit-1016570-zermatt |
| 1016571-ZERMATT | 1 | birkenstock-shearling-lined-zermatt-slippers-grey-narrow-fit-1016571-zermatt |
| 1017519-ZERMATT | 1 | birkenstock-zermatt-cork-latex-slippers-navy-regular-fit-1017519-zermatt |
| 1017523-ZERMATT | 1 | birkenstock-zermatt-cork-latex-slippers-navy-narrow-fit-1017523-zermatt |
| 1017721-BEND | 1 | birkenstock-bend-low-leather-trainers-regular-fit-black-1017721-bend |
| 1019051-ARIZONA | 1 | birkenstock-arizona-eva-sandals-navy-blue-regular-fit-1019051-arizona |
| 1019142-ARIZONA | 1 | birkenstock-arizona-eva-sandals-narrow-fit-blue-1019142-arizona |
| 1019143-GIZEH | 1 | birkenstock-gizeh-eva-sandals-green-regular-fit-1019143-gizeh |
| 1019152-ARIZONA | 1 | birkenstock-arizona-eva-sandals-khaki-green-narrow-fit-1019152-arizona |
| 1027704-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-faded-khaki-regular-fit-1027704-arizona |
| 1027720-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-stone-coin-regular-fit-1027720-arizona |
| 1029170-ARIZONA | 1 | birkenstock-arizona-sandals-latte-cream-regular-fit-1029170-arizona |
| 1029356-SYDNEY | 1 | birkenstock-sydney-cushion-buckle-sandals-taupe-regular-fit-1029356-sydney |
| 1030590-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-concrete-grey-regular-fit-1030590-arizona |
| 1031278-GIZEH | 1 | birkenstock-gizeh-eva-sandals-eggshell-regular-fit-1031278-gizeh |
| 1031318-HONOLULU | 1 | birkenstock-honolulu-eva-sandals-eggshell-regular-fit-1031318-honolulu |
| 1031340-ARIZONA | 1 | birkenstock-arizona-eva-sandals-pink-clay-narrow-fit-1031340-arizona |
| 1031458-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-basalt-grey-1031458-arizona |
| 1031500-ARIZONA | 1 | birkenstock-arizona-birko-flor-sandals-basalt-grey-narrow-fit-1031500-arizona |
| 1031532-BEND | 1 | birkenstock-bend-tabacco-brown-narrow-fit-1031532-bend |
| 1031551-BEND | 1 | birkenstock-bend-tabacco-brown-leather-regular-fit-1031551-bend |
| 1032019-ARIZONA | 1 | birkenstock-arizona-sandals-grey-taupe-regular-fit-1032019-arizona |
| 1032070-ARIZONA | 1 | birkenstock-arizona-birkibuc-sandals-grey-taupe-narrow-fit-1032070-arizona |
| 14450-16 | 1 | mens-rieker-trainers-blue-14450-16 |
| 17659-00 | 1 | mens-rieker-shoes-black-17659-00 |
| 17659-23 | 1 | mens-rieker-wide-fit-shoes-brown-17659-23 |
| 40501-CLEVELAND-NAVY | 1 | womens-free-spirit-cleveland-walking-sandals-navy-40501-cleveland-navy |
| 41323-FAIRMONT2-NAVY | 1 | womens-free-spirit-fairmont-sandals-navy-41323-fairmont2-navy |
| B710AP | 1 | goor-oxford-tie-shoe-black-b710ap |
| CAPRI4-BLACK | 1 | womens-strive-capri-4-sandals-black-capri4-black |
| FLE030-IVES-BEIGE | 1 | st-ives-leather-plimsoll-lunar-shoes-beige-fle030-bg |
| FLE030-IVES-BLACK | 1 | st-ives-leather-plimsoll-lunar-shoes-black-fle030-bk |
| FLE030-IVES-NAVY-BLUE | 1 | lunar-ives-womens-casual-trainers-navy-ives-navy |
| FLE030-IVES-RED | 1 | st-ives-leather-plimsoll-lunar-shoes-red-fle030-rd |
| FLEO50-EVIE-WHITE | 1 | womens-lunar-evie-shoes-white-fleo50-evie-white |
| JLH276-RENOIR-BLACK | 1 | womens-lunar-renoir-sandals-black-jlh276-renoir-black |
| JLH358-CLUSTER-WHITE | 1 | womens-lunar-cluster-wedge-sandals-white-jlh358-cluster-white |
| JLH950-BLAZE-PEWTER | 1 | womens-lunar-blaze-sandal-heel-t-bar-pewter-jlh950-blaze-pewter |
| JLH950-BLAZE-ROSE | 1 | lunar-womens-blaze-sandal-patent-heel-t-bar-rose-jlh950-blaze-rose |
| JLH950-BLAZE-WHITE | 1 | lunar-womens-blaze-sandal-patent-heel-t-bar-white-jlh950-blaze-white |
| M404A | 1 | roamers-wide-touch-shoes-black-m404a |
| M410B | 1 | goor-4-eye-brogue-gibson-shoe-tan-m410b |
| M968BC | 1 | goor-5-eye-brogue-oxford-shoes-blue-m968bc |
| TALIA-LATTE | 1 | womens-strive-talia-shoes-latte-talia-latte |

## Notes / caveats

- Counts are **product-level** images (Shopify `product.images`, first 20). Variant-only images not attached at product level aren't counted — which is the gap you'd want surfaced anyway.
- This is authoritative (live API), not the `shopifyimages` DB table (which only holds handles the nightly `updateimages.py` job has touched).
- Re-run any time: `python seo/find_single_image_groupids.py --csv seo/single_image_groupids.csv`. Use `--min 3` to widen the threshold.
