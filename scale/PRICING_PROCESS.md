# Pricing Operating Model — WORKING DRAFT

> **Status: DRAFT under active design (started 2026-07-01).** This captures a
> strategy discussion in progress. Sections marked **[DECIDED]** are settled;
> **[OPEN]** are still being worked out. Do not treat OPEN items as house rules
> yet. Continue the discussion from the "Where we're up to" section at the bottom.

## Purpose

A systematic, auditable way to price **every** SKU we manage — never missing an
opportunity, without grinding equal time over SKUs that have no decision. The
balance being struck is **time spent vs results achieved.**

The catalogue is worked in ~4-hour sessions. A staff member can own the work.
The owner (business) must be able to **review the output and catch an error**
without redoing it — so every SKU's fate is *reason-coded*, not asserted.

---

## The core idea: the Proven Price is the ANCHOR  [DECIDED in principle]

Every managed product has a **proven price** — the price at which it reliably
sells at acceptable margin. It is the anchor every decision references.

- **Proven Shopify Price — per `groupid`** (Shopify prices at style level).
- **Proven Amazon Price — per SKU / `code`** (Amazon prices at size level).

Lifecycle: **Identify → Monitor → Push up (sometimes down).**

1. **Identify** the proven price from history (lifetime dominant sold price +
   the reasoning already captured in `price_change_log` notes, e.g. "dropped to
   proven £36").
2. **Monitor** — every review compares current price + demand *against the anchor*.
3. **Push up** — probe above the anchor; if the higher price holds (still selling
   at acceptable rate), the anchor **ratchets up** to the new proven level.
4. **Come down** — if it stops selling at the anchor, test below; the anchor may
   **reset down**. The anchor is not a floor or a target — it's the current best
   known truth, and it moves.

This is what turns pricing from opinion into audit: RAISE/CUT decisions become
"current price vs stored anchor," which the owner can review by checking the
**anchor**, not by re-deriving the decision.

### DB design for the anchor  [OPEN]
Needs building. Candidate shapes to decide between:
- **Columns:** `skusummary.proven_shopify_price` (per groupid) +
  `skumap.proven_amz_price` (per code). Simplest; fits existing grain.
- **Dedicated table:** `proven_price(level, key, price, band_low, band_high,
  set_date, set_by, source_note)` — keeps history of how the anchor moved.
Open questions: do we store a single price or a low/high band? Do we keep anchor
history (when/why it ratcheted)? Who/what writes it — seeded once then hand-tuned,
or recomputed?

---

## Level 1 — The loop: which segment to work today  [DECIDED]

Pick an **action lane**: Shopify Price / Amazon Price / Remove.
Then pick the segment **most overdue against its own target cadence** for that lane.

`overdue = today − (last-done date in that lane's column on the Segments sheet)`

Target interval, weighted by revenue-at-stake  **[OPEN — intervals are proposed]**:

| Tier | 12m Revenue | Target interval |
|---|---|---|
| 1 | > £20k | ~3–4 weeks |
| 2 | £5k–£20k | ~6–8 weeks |
| 3 | < £5k | ~6 months |

- Blank date = never done = top of queue.
- `----` = lane doesn't apply to this segment (e.g. Birk has no Amazon lane), skip.
- Selection is mechanical → the owner can eyeball the sheet and confirm the pick.

**Tracker:** the **Segments** tab of the tracker sheet
(`1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0`) now carries three cadence columns
— **AMZ Price · Shopify Price · Remove** — each holding a last-done date. Managed
by hand for now; `refresh_segment_data.py` updates Styles/Revenue/GP/GP% only and
never touches these.

---

## Level 2 — The pass: what happens to each SKU in the segment  [DECIDED shape, thresholds OPEN]

**Every SKU in the segment gets exactly one disposition, assigned by a rule, with
the numbers that triggered it shown. No SKU is silently skipped.** This is the
audit surface.

Order of the pass:
1. **Winners first** (sort u30 desc) — most £ at stake.
2. **Stocked-and-stalled next** — the recoverable-£ pile.
3. **Tail last** — quick cull/park calls.

Dispositions (thresholds still to finalise):

| Code | Rule | Outcome |
|---|---|---|
| **RAISE** | stock > 0 **and** u30 ≥ threshold **and** current price ≤ proven anchor | price up (probe above anchor) |
| **CUT** | stock > 0 **and** u30 = 0 **and** live ≥ 30d at this price **and** price > anchor/Google | price down |
| **HOLD-recent** | price change within last 30d | leave — already decided |
| **HOLD-steady** | selling (u30 > 0) at/near anchor, stock ok | leave — correctly priced |
| **WAIT-new** | stock landed within last 30d | no fair run yet |
| **WAIT-nostock** | sellable stock = 0 | nothing to price (flag Remove lane) |
| **CULL** | stock > 0 **and** u90 = 0 **and** not on reorder | Remove candidate |

- The two **action** codes (RAISE/CUT) are the work.
- The five **non-action** codes are the **owner's review surface**: scan them, challenge
  any label whose printed numbers/dates don't support it. A mislabel can't hide
  because the rule and its inputs sit next to every row.

---

## Level 3 — The certificate: the date stamp  [DECIDED]

Stamping "SEGMENT · lane · date" asserts *"I passed my eye over the whole category;
the ones needing a move got moved; the rest are correctly left."*

**"Seen" ≠ "individually deliberated."** This is how we get the flat-SKU-list's
no-miss guarantee without its cost — completeness is certified at the segment
level, effort is spent only on the action rows.

---

## Why not a flat SKU round-robin?  [DECIDED — rejected as the primary structure]

Listing all SKUs and working one-by-one guarantees no-miss but spends **equal time
on every SKU** — ~90% of which have no decision on any given pass (EVA-SEG: 31 SKUs
→ ~3 live decisions). Segments give context (better + faster decisions),
delegability, and — via the report + disposition rules — a smaller judgment load.
A SKU-level "last touched" date may still exist as a **backstop audit** (catch a
quiet SKU the segment passes keep skipping), but it is not the driver.

---

## Where we're up to / open threads  [continue here]

- **[OPEN] Proven-price DB design** — columns vs table; single price vs band;
  keep anchor-move history?; seeding method.
- **[OPEN] Level-2 thresholds** — the "u30 ≥ threshold" for RAISE, the "near anchor"
  tolerance, the 30-day "recent"/"new"/"fair run" windows. Numbers not yet fixed.
- **[OPEN] Cadence intervals** — the tier table above is proposed, not agreed.
- **[OPEN] Report tooling** — the current EVA triage (`scale/eva/stock_triage.py`)
  sorts stock-DESC (a clearance lens). A pricing pass wants demand-sorted + a
  disposition column + grey-out of recently-touched. Decide whether to reshape the
  per-segment reports to emit the disposition table directly.
- **[OPEN] Do we still split EVA-SEG?** Parked — may not, now that the operating
  model (not segment size) is the real lever. Revisit once the process is defined.
- **[TEST PENDING] Run EVA-SEG through the Level-2 ruleset** and produce the full
  31-row disposition table — the honest check of whether it really collapses to ~3
  actions, and the first audit dry-run.

## Related docs
- `scale/CLAUDE_CONTEXT.md` — scale/segment context (read first for segment work).
- `shopify-price/README.md` — the Shopify per-groupid deep-dive + apply flow.
- `amz-price/AMZ_PRICING.md` — the Amazon pricing engine.
- `scale/SEGMENT_REPORTS.md` — per-segment report templates.
