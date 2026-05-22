# EVA-SEG — segment rules

Overrides to the defaults in `../SEGMENT_REPORTS.md`. Anything not listed here follows the default.

## Why this segment is different

23 styles split roughly into: a handful of active sellers, a stocked-but-dead middle, a sell-through tail. The standard **Summary** flags whether there's a problem worth attention — but it doesn't tell you *which* of the 23 styles to look at, and going SKU-by-SKU kills motivation.

So EVA-SEG uses a two-step flow:

1. **Summary** (default template from `../SEGMENT_REPORTS.md`) — the entry report. Run on request, then **stop**. Present the Summary and end with a single-line offer: *"If you want to drill, the next step for EVA-SEG is the stock-availability triage."* Do **not** auto-run the triage even if the Summary looks bad — the user decides whether to dig deeper.
2. **Stock-availability triage** — the segment-specific drill. Run only when the user explicitly asks for it. One row per groupid, sorted by total stock units DESC, so the items where there is most recoverable £ sit at the top and the stock-gutted decisions sit at the bottom. This narrows 23 styles into a small number of actual decisions.

The standard per-SKU drill from `../SEGMENT_REPORTS.md` is **not** the default drill for EVA-SEG — the triage replaces it. Per-SKU is still available on request when a single groupid needs a closer look.

## Stock-availability triage (drill)

Script: `scale/eva/stock_triage.py`. Output shape:

```
 #  GroupID                Colour/Fit             Px     Cov Stock  u30  u14  Inc
 1  0128221-GIZEH          White / Regular       £42   11/12    25    0    0    -
 ...
```

- **Px** — listed Shopify price (from `skusummary.shopifyprice`).
- **Cov** — sizes-in-stock / total-size-universe. **Use `skumap` for the universe denominator** — never `skusummary.variants`/`stockvariants` (stale, see top-level `CLAUDE.md`).
- **Stock** — total `localstock` units across all sizes, `ordernum='#FREE' AND deleted=0`.
- **u30 / u14** — units sold in last 30 / 14 days, `sales` with `qty>0 AND soldprice>0`. Avg-sold-price deliberately not shown at this level — drill on request when the listed vs actual gap matters.
- **Inc** — pending Birk units, `birktracker` summed as `SUM(GREATEST(requested-arrived, 0))` per groupid. Total only; due-month detail is a drill.

Sort: `Stock DESC, u30 DESC` so the items with most stock and most recent demand surface first.

## Triage philosophy

We landed on **one priority category, not seven**: *"Stocked + not moving in peak season"*. Other sub-rules we discussed (post-reprice slowing, listed-vs-actual gap, stock-gutted, tail, almost-empty) collapse into either the same action ("investigate price/listing"), no current decision available (Birk 6-month lead time), or self-resolving sell-through (category-boundary principle from `../CLAUDE_CONTEXT.md`).

**Upside-pricing is kept inside this same workflow.** A row like Green Nar selling 6u/30d at £39 while Google says £35 is a defend-the-margin decision, surfaced by the same report.

The high-stock end of the list is where price/listing work pays off. The low-stock end is where the decision is *drop further or wait for incoming* — the `Inc` column carries that.

## Working rhythm

1. **Run the Summary**, present it, **stop**. End with a single-line offer that the triage is the next-step drill. Do not run the triage yourself.
2. The user decides whether to drill. Only run the triage when they explicitly ask.
3. Once in the triage, discuss priority before listing decisions — the right call may not be top-down. Don't bulk-decide.
4. Pick one or two items per session, drill into them, log decisions as `segment_notes` rows.
5. Re-run the triage next session — most items won't have moved, so attention narrows naturally.

## When to drill — and what's available

The triage is the entry point. From it, drill on request:

- **Per-size view of a groupid** — sizes in stock, OOS-but-sold, recent units. Useful when the question is "is this row a price problem or a stock-coverage problem?".
- **Google sale-price comparison** — `scale/eva/google_compare.py [SEGMENT]`. Reads the latest "Sale price suggestions" CSV from `shopify-price/` (run `shopify-price/refresh_google_csvs.py` first if a fresh export is sitting in Downloads). Google often pushes lower than is correct; cross-check against actual sold avg before acting.
- **Listed-vs-actual sold price** — `sales` over the relevant window. Big gaps usually indicate a Shopify discount/sale flag — investigate the source, not the symptom.
- **Daily detail** — per-day units / incoming / running stock. See default template in `../SEGMENT_REPORTS.md`.

## Open items / parked threads

These came up during the 2026-05-20 session and weren't actioned. Pick up next time.

- **Incoming-vs-sales mismatches.** Madrid White Nar (#2: 22 stock, 0 sales, 38 incoming), Madrid Black Nar (#11: 13/0/46), Barbados Black (#10: 14/0/13). Already-placed Birk forward orders that look misaligned with current demand. Separate from pricing work — feeds into next-season order discipline.
- **The £45 Arizona Black Reg/Nar stall.** Listed £45 but actual sold averages are £42 and £39. There's a discount mechanism in play that explains the gap; need to find its source before deciding whether to drop listed prices or kill the discount.
- **0128221-GIZEH White Reg** (#1). 25 units, 11/12 coverage, zero sales 90 days, zero incoming, Google reco £35.81. Loudest single signal in the segment, no decision yet.

## Defaults that still apply

- 14d / 30d windows from `../SEGMENT_REPORTS.md`.
- Pace projection: Birkenstock 150-day peak (Mar-Jul).
- Notes stored in `segment_notes`, surface top 3 alongside the report.
- Per-style action lives in *state*, not in/out membership — losers exit by sell-through (category-boundary principle).
