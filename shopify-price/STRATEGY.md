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
- **Drop parked styles** — anything with a future `next_shopify_price_review` (see
  [Review / park](#review--park-the-cooldown)) is in cooldown and hidden, so a style we
  just decided on doesn't loop straight back.
- Return the **top 10 in-stock styles by units**.

**Columns:** `# · qty · groupid · stock`. The `#` is just a row number so a style can be
picked by number in conversation instead of pasting the groupid. Deliberately minimal — the `groupid` is the pick,
and all product detail (description, colour, size, price) is left to drill-down. We tried
showing `colour`/`width`, then the full `title`, then a `weeks_cover` figure, and pared
them all back: `skusummary.colour` is overloaded as a segmentation tag (Mocha filed under
"Brown") so it's ambiguous, the title is too much to scan, and weeks-cover wasn't getting
looked at. What's left is what actually gets read — how much it sold, which style, and how
much stock is left.
- `stock` = current sellable warehouse units (`localstock`, `#FREE`, not deleted). Never
  `skusummary.stockvariants` — that field is stale.

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

## Stage 2 — Drill-down (single groupid)

**What it answers:** for one style picked off the Stage 1 list, should we adjust its price?
The whole decision is one relationship — **the price we've charged vs how fast it sold, over
time** — so the page is built to make that visible without any maths or narration.

**The page (`drill.py <groupid>`):**

1. **Header** — a small vertical table of where we stand now: `now` (list price), `rrp`,
   `cost`, `stock` (total sellable units).
2. **Pricing timeline** — one row per distinct price we've sold at, **oldest era first**,
   showing the selling period and **raw units** sold at that price. A stall or an
   acceleration is then just the shape of the units column against the price column; the
   reader weighs it, the script doesn't editorialise.

**Deliberately raw units, not a rate.** We tried per-week pace, bars, and auto-takeaway
lines — all cut. The period is shown next to the units so the reader can judge the tempo
themselves. The point is that the operator reaches the call and can sanity-check it, not
that the tool hands down a verdict.

**Size is off by default** (`--sizes` to show the remaining-stock size curve). Size does
**not** set the price — it's a guardrail you consult before a *cut*, so you don't misread a
sold-out core (e.g. 38/39 gone) as dead demand. For a *raise* candidate it barely matters.

**One honest caveat when reading the timeline:** for seasonal Birkenstock, units rising as
price rose can be the **season arriving, not the price working**. The cleaner signal is a
price step where the tempo *held* (a rise with no slowdown) — that's the evidence for going
higher, not the raw "sold more at a higher price".

**Run it:**
```
python shopify-price/drill.py 0129443-ARIZONA
python shopify-price/drill.py 0129443-ARIZONA --sizes         # add size curve
python shopify-price/drill.py 0129443-ARIZONA --days 180      # widen price history
```
`--days` (pricing-history window) defaults to 90.

Once a price is decided, apply it via `apply-prices.md` / `apply_prices.py`.

---

## Review / park (the cooldown)

So the triage doesn't keep re-surfacing a style we've just handled, every decision sets a
**next review date**. Until that date passes, the style is hidden from Stage 1.

- **Where it lives:** `skusummary.next_shopify_price_review` (a `date`). We keep it on the live product
  master — the same table our scripts already read for price/cost/stock — not on
  `groupid_performance`. That table *does* have a `next_review_date` the old PowerBuilder
  front-end wrote, but its refreshing cron died in Mar 2026 (its metrics are frozen), so we
  don't build on it. The one live park was migrated onto `skusummary`.
- **On a price change:** required. `apply_prices.py` refuses a price change with no
  `review_days` — you must decide when to look again. It sets `next_shopify_price_review =
  today + review_days` as it applies the price.
- **On a "no change" or ad-hoc:** `python shopify-price/review.py <groupid> <days>` parks a
  style without changing its price.

There's no fixed cooldown — pick per decision (a raise-probe might be 7 days, a healthy
"leave it" 30). A parked style reappears in the triage automatically once the date passes.

**Session convention:** when proposing a price move, **propose the review window alongside
it** — one approval, not two. Never silently default it, never leave it for the user to
remember. Suggest a number with a one-line reason keyed to the move, and the user approves
or tweaks it:
- **raise-probe** (testing the ceiling) → short, ~7 days
- **cut to clear** → ~14 days
- **hold / healthy** → ~30 days

**Who's running it:** ask at the **start of the session** who's doing the pricing (default
`Andreas`) and pass it to `apply_prices.py --by <name>`. It's written to
`price_change_log.changed_by` — the same column the front-end fills with the user's name —
so tool changes and manual UI changes are attributable side by side. `reason_code` is left
NULL (we capture no reason).

---

## Stages to come

_(to be added as we design them)_
