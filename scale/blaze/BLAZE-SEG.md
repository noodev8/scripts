# BLAZE-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default. This folder is self-contained — `stock_triage.py` is BLAZE's own copy (Amazon-flavoured); edit it freely without worrying about other segments.

## What this segment is

3 groupids — `JLH950-BLAZE-BLACK`, `JLH950-BLAZE-NAVY`, `JLH950-BLAZE-NUDE`. Lunar sandal, **Amazon / FBA only** (Birk-style Shopify reporting does not apply). Lunar's 4-day reorder lead time means stock is a *live lever*, not a 6-month forward commitment.

Demand-recovery segment: was once a strong seller around £35, fell back, currently ~£32.99 on Amazon. The manager question stays simple: **are units recovering or not?** The deeper question this folder answers: **is weakness demand or is it stock?**

## Summary — default template

Standard two-window YoY Summary from `../SEGMENT_REPORTS.md`. Pace family: Lunar, year-round, ×365. Present it, then **stop** and offer the triage:

> *"If you want to drill, the next step for BLAZE-SEG is the stock-availability triage."*

## Stock-availability triage (drill)

Script: `scale/blaze/stock_triage.py`. Run only when asked. One row per colour:

```
 #  GroupID            Colour    Px     Cov  FBA  u30  u14  Send  OOS(hot)
```

- **Px** — actual Amazon sell price (`amzfeed.amzprice`, averaged across sizes). Shopify list price printed below the table as a reference only.
- **Cov** — sizes live at FBA / total size universe (`skumap`, `deleted=0`). **Never** `skusummary.variants`/`stockvariants` (see top-level `CLAUDE.md`).
- **FBA** — total live FBA units (`amzfeed.amzlive`). This is what actually converts.
- **u30 / u14** — `sales`, `qty>0 AND soldprice>0`, windows from Summary.
- **Send** — warehouse `#FREE` units available to ship into FBA. With the 4-day lead, this is the immediate lever — especially where it overlaps an OOS-hot size.
- **OOS(hot)** — sizes that sold in the last 30d but are now **zero at FBA**. The demand the listing currently can't convert. This is the headline signal for this segment.

> Note: `amzfeed.buybox` is a **dead legacy column** — no longer maintained, slated for removal. Never use it in any BLAZE (or other) analysis.

Sort: `u30 DESC` so the strongest sellers surface first and any OOS-on-hot-size jumps out at the top.

## How to read it

- **High u30 + OOS(hot) populated** → demand is real but throttled by stockouts. If `Send > 0` on those sizes, shipping warehouse stock to FBA is the immediate fix. If `Send = 0`, it's a reorder (4-day Lunar lead).
- **High FBA + low u14/u30** → stocked but not converting. Price / listing question, not stock.

## Owner note

Per the BLAZE quirk: add **listing visibility** commentary in the `segment_notes` owner note when relevant. The manager view stays simple (units recovering or not); the listing colour lives in the note.

## Defaults that still apply

- 14d / 30d windows and YoY comparison from `../SEGMENT_REPORTS.md`.
- Pace projection: Lunar year-round ×365.
- Notes stored in `segment_notes`, surface top 3 on request.
- Category-boundary principle — all three colours stay in; per-style action carried by state.
