# Shopify Pricing Operating Model

> **Scope: Shopify only — pricing at `groupid` (style) level.**
> Amazon/SKU-level pricing is out of scope for this doc.
> **Status: building.** The anchor mechanic is being proven by hand (MD store)
> before it earns a database column. Disposition thresholds marked *(provisional)*
> are not house rules yet.

## Purpose

A systematic, auditable way to price every Shopify style we manage — never missing
an opportunity, without grinding equal time over styles that have no decision.
Every groupid's fate is **reason-coded**, so the owner can review the output and
catch an error without redoing the analysis.

---

## How work is triggered

**A human picks the segment.** You say *"price analyse SEGMENT X"* and we run the
pass over that segment. There is no automated "which segment is due today" queue.

We do **store the last date each segment was price-analysed** (the *Shopify Price*
column on the Segments tab of the tracker sheet
`1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0`). That date is a **memory aid** —
it tells you when you last looked so you can decide what's worth revisiting. It
does not decide the work for you.

---

## The Proven Price anchor

Every managed style has a **proven price** — the price at which it reliably sells
at acceptable margin. It is the anchor every pricing decision references. Turning
"should this go up?" into "is current price above or below the stored anchor?" is
what makes the pass auditable instead of opinion.

**One anchor per `groupid`.**

Lifecycle:
1. **Seed (once).** First time we analyse a groupid with no stored anchor, we
   compute it from history and **write it down**. (Exact derivation rule TBD —
   pinned when we first seed.)
2. **Reference.** Every later pass compares current price + recent demand *against
   the stored anchor*.
3. **Ratchet up.** Probe above the anchor; if the higher price holds (still selling
   at an acceptable rate), overwrite the anchor to the new proven level.
4. **Reset down.** If it stops selling at the anchor, test below; the anchor may
   move down. The anchor is not a floor or a target — it's the current best known
   truth, and it moves **deliberately**, never silently.

### The store

Lives in **`scale/proven_prices.md`** — a single flat table, one row per groupid:

| groupid | anchor | set_date | source | note |
|---|---:|---|---|---|

- `source` = `computed` (seeded from history) or `manual` (we set/ratcheted it).
- **No row / blank anchor = "compute on first analysis, then fill."**
- Ratcheting overwrites `anchor` + `set_date` + `note`. The store keeps only the
  **current** truth; if we find we miss the history of *how* an anchor moved, we
  add that later.

This MD is deliberately hand-inspectable. It will migrate to a DB column once the
mechanic is proven; nothing about the model depends on it staying an MD.

---

## The pass: one disposition per groupid

**Every groupid in the segment gets exactly one disposition, assigned by a rule,
with the numbers that triggered it shown. No groupid is silently skipped.** This
is the audit surface.

Order of the pass:
1. **Winners first** (sort u30 desc) — most £ at stake.
2. **Stocked-and-stalled next** — the recoverable-£ pile.
3. **Tail last** — quick cull/park calls.

Dispositions *(thresholds provisional until agreed)*:

| Code | Rule | Outcome |
|---|---|---|
| **RAISE** | stock > 0 **and** selling (u30 ≥ threshold) **and** current price ≤ anchor | price up — probe above anchor |
| **CUT** | stock > 0 **and** u30 = 0 **and** ≥ 30d live at this price **and** price > anchor | price down |
| **HOLD-recent** | price changed within last 30d | leave — already decided |
| **HOLD-steady** | selling at/near anchor, stock ok | leave — correctly priced |
| **WAIT-new** | stock landed within last 30d | no fair run yet |
| **WAIT-nostock** | sellable stock = 0 | nothing to price |
| **CULL** | stock > 0 **and** u90 = 0 **and** not on reorder | remove candidate |

- The two **action** codes (RAISE / CUT) are the work.
- The five **non-action** codes are the **owner's review surface**: scan them,
  challenge any label whose printed numbers don't support it. A mislabel can't
  hide because the rule and its inputs sit next to every row.

**Data sources (Shopify grain):**
- current price → `skusummary.shopifyprice`
- stock → `localstock` where `ordernum='#FREE' AND deleted=0`, summed per groupid
- u30 / u90 → `sales` where `qty>0 AND soldprice>0` over the window
- last change date → `price_change_log`
- anchor → `scale/proven_prices.md`

---

## The report

A new **Pricing Pass** report — a disposition table, one row per groupid, action
rows first. This is a *separate* report from the conclusion-free segment Summary;
its whole job is to print a disposition (a conclusion) with its inputs beside it.

Proposed columns:

| groupid | colour/fit | price | anchor | stock | u30 | u90 | last chg | **disposition** |
|---|---|---:|---:|---:|---:|---:|---|---|

Built fresh when we run the first pass — not a reshape of the existing Summary.

---

## The certificate: the date stamp

Completing a pass stamps *"SEGMENT · Shopify Price · date"* on the tracker — the
assertion *"I passed my eye over the whole category; the ones needing a move got
moved; the rest are correctly left."*

**"Seen" ≠ "individually deliberated."** Completeness is certified at the segment
level; effort is spent only on the action rows.

---

## Open threads

- **Anchor derivation rule** — the exact "compute the proven price from history"
  method. Pinned when we first seed.
- **Level-2 thresholds** — the RAISE "u30 ≥" bar, the "near anchor" tolerance, the
  30-day recent/new windows. Provisional above.
- **First dry-run** — run a real segment through the ruleset and produce the full
  disposition table: the honest check of whether it collapses to a handful of
  actions, and the first audit test.

## Related docs
- `scale/CLAUDE_CONTEXT.md` — scale/segment context (read first for segment work).
- `shopify-price/README.md` — the Shopify per-groupid deep-dive + apply flow.
- `scale/SEGMENT_REPORTS.md` — the conclusion-free segment Summary (separate from this).
