# Shopify Pricing — Strategy

The old process was cleared out deliberately (see git history if you ever want it back).
This is the rebuild, assembled in **stages**. Each stage is a labelled, self-contained
lens; later stages build on earlier ones. Nothing here is a ritual — it's the set of
tools/views we've agreed so far.

**Everything starts by filtering to a SEGMENT.** A segment is `skusummary.segment`
(e.g. `EVA-SEG`). The full segment list lives in `scale/CLAUDE_CONTEXT.md`. We never look
at the catalogue as a whole for pricing — we look at one segment at a time.

The technical path for *applying* a decided price is unchanged: `apply-prices.md` +
`apply_prices.py`. This file is about *deciding*.

## Key constraint — no restock for Birkenstock

**Birkenstock cannot be re-ordered on demand.** We order it ~6 months in advance, so the
stock we hold this season is all we get — there is no "sold out → order more" lever.
**This applies to Birkenstock only**; other brands can be restocked. But Birkenstock is
**~95% of Shopify sales**, so in practice this constraint governs almost everything here.

The consequence shapes the whole strategy: **the job is to squeeze as much profit as
possible out of the stock we already hold.** That reframes what stock signals mean —
notably, a fast-selling style with thin cover is *not* a restock flag (we can't restock),
it's a **price-up / harvest** candidate: it will sell through regardless, so keeping it
cheap just leaves margin on the table.

---

## Stage 1 — Latest Sales

**What it answers:** which in-stock styles has this segment sold recently, and how much
runway is left on each? A sanity-triage shortlist — the ~10 styles worth drilling into.
**The only decision at this stage is which styles to drill down on** — no price calls
here. The actual pricing signals (size curve, price, dates, margin) come on drill-down.

**The rule:**
- Filter to one **segment**.
- **Shopify only** (`sales.channel = 'SHP'`), positive sales only (`qty > 0`, `soldprice > 0`).
- Look inside a **30-day window** (the pool).
- **One row per groupid** — not per sale line. `qty` = **units** sold in the window
  (`SUM(qty)`), so a style that sold repeatedly stands out.
- **Drop styles with 0 current stock** — nothing to price and (for Birkenstock) no
  restock lever, so they'd just be noise. The limit tops the list back up to 10.
- Return the **top 10 in-stock styles by units**.

**Columns:** `qty · groupid · colour · width · stock · weeks_cover`.
- `stock` = current sellable warehouse units (`localstock`, `#FREE`, not deleted). Never
  `skusummary.stockvariants` — that field is stale.
- `weeks_cover` = `stock ÷ weekly run-rate`. At current pace, roughly how long until it's
  gone. Read it with the [no-restock constraint](#key-constraint--no-restock-for-birkenstock):
  **thin cover on a fast seller is a harvest / price-up signal, not a restock flag.**

**What we deliberately ignore here:** size, date, price (they vary across a style's sales
— derived on drill-down), and **incoming/allocated stock** (deferred to a later stage; a
style at 0 *current* stock with stock landing is not truly dead, but we don't model that yet).

Ordering: **units desc** (strongest sellers first); ties broken by most recent sale.

**Run it:**
```
python shopify-price/latest_sales.py EVA-SEG
python shopify-price/latest_sales.py EVA-SEG --days 30 --limit 10   # explicit defaults
```
Segment defaults to `EVA-SEG`; `--days` defaults to 30; `--limit` defaults to 10.

---

## Stages to come

_(to be added as we design them)_
