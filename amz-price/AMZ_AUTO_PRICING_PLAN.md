# Amazon Auto-Pricing — Plan & Rules

## Purpose

This document captures the pricing decision rules that Claude and the user apply during manual AMZ pricing sessions. The goal is to progressively automate these decisions:

1. **Now:** Manual sessions with Claude. This doc records the rules being applied.
2. **Next:** Claude runs a dry-run before each manual session. User compares dry-run vs manual decisions. Disagreements refine the rules.
3. **Then:** Python script implements the rules. Dry-run output reviewed by user before applying.
4. **Eventually:** Cron runs the script automatically for "vanilla" changes. User reviews a summary and can override. Manual review remains available at any time.

We are at **stage 1**. The doc evolves with each session.

---

## Scope

Auto-pricing is scoped by **product family**. Each family has its own rules because cost, FBA fees, price ceilings, and customer behaviour differ.

| Scope | Products | Status |
|-------|----------|--------|
| **IVES** | All FLE030-IVES-* groupids (10 colours, 8 segments) | Active — rules being captured |

Future scopes (not started): Free Spirit, Charlotte, Birkenstock, etc. Each will need its own rules section in this doc (or a separate doc if complex enough).

The dry-run script and any future automation take a `scope` parameter. Rules from one scope are never applied to another.

---

## Decision Framework

Every size-level SKU gets exactly one recommendation: **CREEP**, **DROP**, **HOLD**, or **FLAG** (needs human judgement).

### Inputs (per SKU)

All derivable from `sales` + `amzfeed` + `amz_price_log`:

| Input | Source | Notes |
|-------|--------|-------|
| `current_price` | `amzfeed.amzprice` | |
| `fba_live` | `amzfeed.amzlive` | Stock available to sell now |
| `fba_total` | `amzfeed.amztotal` | Includes inbound |
| `fba_inbound` | `amztotal - amzlive` | Derived |
| `sold_7d` | `sales` aggregation | Units sold, qty > 0 only |
| `sold_28d` | `sales` aggregation | |
| `returns_28d` | `sales` aggregation | qty < 0 |
| `return_rate` | `returns_28d / sold_28d` | 0 if no sales |
| `days_since_last_sale` | `sales` MAX(solddate) | NULL if never sold |
| `last_change_date` | `amz_price_log` | Most recent price change |
| `days_since_last_change` | Derived from above | |
| `last_change_direction` | `new_price - old_price` from log | Was it a creep or drop? |
| `cost` | `skusummary.cost` | £15.99 for all IVES |
| `fba_fee` | `amzfeed.fbafee` | ~£3.01-£3.09 |
| `rrp` | `skusummary.rrp` | £45.00 for all IVES |

### Price Boundaries

| Boundary | Value | Source |
|----------|-------|--------|
| **Floor** | cost + fba_fee + £1.00 margin | Hard floor — never go below |
| **Practical floor** | £35.99 | Lowest we've gone on IVES tail sizes |
| **Resistance zone** | £38.50–£39.00 | Many sizes stall here — observed across GREY, BEIGE |
| **£40 ceiling** | £40.00 | Most IVES colours die above £40. Exception: BLACKSOLE |
| **RRP cap** | £45.00 | Amazon max-seller-allowed-price |

### Standard Step Size

- **£0.50** for most moves
- **£1.00** for aggressive drops on dead stock (14+ days no sale)
- Never move more than £1.50 in a single session unless stock is critically stale

---

## Rules

### CREEP Rules

A SKU qualifies for a creep (price increase of £0.50) when:

| Rule | Condition | Confidence | Notes |
|------|-----------|------------|-------|
| **C1 — Strong velocity** | `sold_7d >= 3` AND `return_rate < 20%` AND `days_since_last_change >= 7` AND `fba_live >= 3` | High | The bread-and-butter creep. Velocity proves price is working. |
| **C2 — Star SKU** | `sold_28d >= 8` AND `return_rate == 0` AND `fba_live >= 5` | High | Zero returns + sustained volume = strong signal. |
| **C3 — OOS with inbound** | `fba_live == 0` AND `fba_inbound >= 3` AND velocity was strong before stockout (`sold_7d >= 3` in the week before OOS) | High | Don't wait for stock to land at a low price. Creep now so it's ready. |
| **C4 — Previous drop recovered** | Last change was a drop AND `sold_7d >= 2` AND `days_since_last_change >= 7` | Medium | The drop worked — start creeping back to find the ceiling. |

**Creep caps:**
- Do not creep above £40.00 unless the SKU has proven history above £40 (check `amz_price_log` for prior sales at £40+)
- BLACKSOLE is exempt from the £40 ceiling — it's the only IVES colour that sustains above £40
- Do not creep if `fba_live <= 2` AND `fba_inbound == 0` (don't price up into a stockout with no resupply)

### DROP Rules

A SKU qualifies for a drop when:

| Rule | Condition | Step | Confidence | Notes |
|------|-----------|------|------------|-------|
| **D1 — Stalled** | `days_since_last_sale >= 8` AND `fba_live >= 3` | £0.50 | High | Stock sitting idle = price too high. |
| **D2 — Dead** | `days_since_last_sale >= 14` AND `fba_live >= 3` | £1.00 | High | Stronger signal, bigger move. |
| **D3 — Resistance point** | Previous creep AND `sold_7d == 0` AND `days_since_last_change >= 5` | Revert to pre-creep price | High | The creep didn't work — undo it. |

**Drop floor:** Never drop below practical floor (£35.99) without flagging for human review.

### HOLD Rules

A SKU gets a HOLD when:

| Rule | Condition | Notes |
|------|-----------|-------|
| **H1 — OOS, no inbound** | `fba_live == 0` AND `fba_inbound == 0` | Nothing to sell, nothing to do. |
| **H2 — Low live stock** | `fba_live <= 2` AND `fba_inbound == 0` AND velocity is adequate | Don't creep into a stockout. Don't drop what's nearly gone. |
| **H3 — Too soon** | `days_since_last_change < 5` | Let the last change prove itself. |
| **H4 — Adequate velocity** | `sold_7d >= 1` AND `sold_7d <= 2` AND no red flags | Working but not exceptional. Don't touch. |
| **H5 — At baseline** | Already at flat baseline (e.g. Stone at £36.99) AND `sold_7d >= 1` | Ticking over at floor-ish price. No room to drop, not enough signal to creep. |

### FLAG Rules (needs human)

| Rule | Condition | Notes |
|------|-----------|-------|
| **F1 — High returns** | `return_rate >= 40%` | Likely a product/fit issue, not price. Don't auto-drop. |
| **F2 — Contradictory signals** | Qualifies for both CREEP and DROP rules | Shouldn't happen but catch it. |
| **F3 — Near floor** | Proposed drop would go below £35.99 | Human decides if we go lower or hold. |
| **F4 — Breaking £40 ceiling** | Proposed creep would go above £40 AND SKU has no history above £40 | Human decides if this colour can sustain it. |

---

## Rule Priority

When multiple rules match, apply in this order:
1. FLAG rules (always surface to human)
2. HOLD rules (safety first)
3. CREEP/DROP rules (action)

If a CREEP rule and a HOLD rule both match, HOLD wins. Human can override.

---

## Observations Log

Patterns observed during manual sessions that aren't yet codified as rules. These may become rules as more data confirms them.

### Session 2026-04-12 — Full IVES review (24 changes)

- **£38.50 resistance on GREY:** Both 04 and 05 stalled at £38.50. Reverted to £37.99. May be colour-specific or a general mid-range resistance point. Watch other colours at this price.
- **£39.99-£40.00 resistance on most colours:** KHAKI-05 dead at £39.99, KHAKI-08 dead at £39.99. Consistent with the established £40-kills-velocity finding. BLACKSOLE remains the exception.
- **Size 08 return problem:** BEIGE-08 (43% returns), MIDBLUE-08 (50% returns) — pattern across colours on size 08. Likely a fit issue at the extreme of the size range. Not a pricing problem — holding price is correct.
- **Size 07 often lags:** BLACK-07 (18 days dead), MIDBLUE-03 (18 days dead), NAVY-07 (8 days dead). Larger sizes tend to have lower velocity. May need structurally lower prices than core sizes (05/06).
- **BLACKSOLE-06 ceiling test:** Pushed to £41.49. If this holds, it's the highest-priced IVES SKU ever. Important data point for £40+ viability.
- **Creep OOS SKUs immediately:** Don't wait for inbound stock to land. If velocity was strong and stock ran out, the price was probably too low. Creep now. (User-confirmed principle.)

---

## Dry-Run Design (future)

### How it will work

1. Python script reads all IVES SKUs from `amzfeed` + `sales` + `amz_price_log`
2. Applies rules in priority order to each SKU
3. Outputs a table: `code | current_price | recommendation | new_price | rule_applied | confidence`
4. Saves output to `amz_price_dry_run` DB table (or CSV) with timestamp

### Calibration loop

1. Script generates dry-run recommendations
2. User and Claude do the manual session as normal
3. After manual session, compare:
   - **Agreements:** Rule worked. No action needed.
   - **Script recommended, human disagreed:** Why? Capture the reason. Refine the rule or add a new FLAG.
   - **Human changed, script said HOLD:** Missing rule. Add it.
4. Track agreement rate over sessions. Target: 95%+ before moving to stage 3.

### Dry-run output table — `amz_price_dry_run`

**Table created 2026-04-12.** Schema:

```sql
-- Already exists in the database
CREATE TABLE amz_price_dry_run (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL DEFAULT NOW(),
    run_id VARCHAR,           -- groups rows from same run, e.g. '2026-04-12-ives'
    scope VARCHAR NOT NULL DEFAULT 'IVES',  -- product family
    segment VARCHAR,          -- e.g. IVES-BLACKSOLE
    groupid VARCHAR,          -- e.g. FLE030-IVES-BLACKSOLE
    code VARCHAR NOT NULL,    -- e.g. FLE030-IVES-BLACKSOLE-06
    current_price NUMERIC,
    recommendation VARCHAR,   -- CREEP, DROP, HOLD, FLAG
    proposed_price NUMERIC,
    rule_applied VARCHAR,     -- e.g. C1, D2, H3
    confidence VARCHAR,       -- High, Medium, Low
    manual_decision VARCHAR,  -- filled in after manual session
    manual_price NUMERIC,
    agreed BOOLEAN,           -- did dry-run match manual?
    disagreement_reason TEXT  -- why not, if applicable
);
```

### Metrics to track

- **Agreement rate** per session (target: 95%+)
- **Agreement rate** by rule (which rules are reliable?)
- **False positives** — script recommended a change that human rejected
- **False negatives** — human made a change that script missed
- **Rule coverage** — % of manual decisions that match a defined rule

---

## Path to Automation

| Stage | Status | Gate to next stage |
|-------|--------|-------------------|
| 1. Manual sessions, doc captures rules | **Active** | Rules feel stable across 3+ sessions |
| 2. Dry-run before manual, compare after | Not started | Agreement rate 95%+ for 3 consecutive sessions |
| 3. Python script, human reviews before apply | Not started | Agreement rate 98%+ and no false positives on drops |
| 4. Cron, human reviews summary after | Not started | 5+ sessions with zero manual overrides |

**Non-negotiable:** User can trigger a full manual review at any time, at any stage. Automation supplements, never replaces, human judgement.

---

## Files & References

- `amz-price/AMZ_PRICING.md` — session history, DB schemas, segment definitions
- `amz-price/update_amz_price.py` — existing price change logger
- `amz_price_log` DB table — all historical price changes with notes
- Future: `amz_price_dry_run` DB table — dry-run vs manual comparison data
- Future: `amz-price/amz_auto_price.py` — the automation script
