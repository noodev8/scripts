# Email Strategy — Brookfield Comfort

**Created:** 2026-03-28
**Last reviewed:** 2026-03-28
**Status:** Active — building the asset

---

## The Thesis

We spend money on Google Shopping to acquire Birkenstock customers. Email turns those one-time buyers into repeat customers — for free. Every repeat sale driven by email is one we didn't pay Google for.

**Google Shopping = renting customers. Email list = owning them.**

The goal: build the email list into a self-sustaining revenue channel that compounds over time as the list grows.

---

## Current State — Snapshot (2026-03-28)

### Lists

| List | Size | Purpose |
|------|------|---------|
| Andreas | ~451 | Campaign split — team competition |
| Summer | ~453 | Campaign split — team competition |
| Martin | ~448 | Campaign split — team competition |
| **Total reachable** | **~1,352** | |

### Segments

| Segment | Type | Purpose |
|---------|------|---------|
| Birkenstock 6–12 months since purchase | Target | Primary campaign audience |
| Birkenstock 12–24 months since purchase | Target | Lapsed buyers — next focus |
| Birkenstock bought inside 6 months | Hold | Too recent — don't email yet |
| No orders for 2 years | Suppress | Too lapsed |
| No Birkenstock orders | Suppress | Not relevant |
| Suspected Bots | Suppress | Clean list |

### Flows (Automated — Always On)

| Flow | Status | Recipients (12mo) | Orders | Revenue | Conv Rate |
|------|--------|-------------------|--------|---------|-----------|
| Abandoned Checkout | Live | 87 | 7 | **£467.76** | 8.0% |
| Browse Abandonment | Live | 32 | 1 | **£72.45** | 3.1% |
| Other/archived flows | — | 112 | 3 | **£207.90** | 2.7% |
| **Flow total** | | **231** | **11** | **£748.11** | **4.8%** |

### Campaigns (Manual Sends)

| Campaign | Date | Recipients | Open Rate | Click Rate | Orders | Revenue |
|----------|------|-----------|-----------|------------|--------|---------|
| Martin birkenstock 90 | Mar 10 | 1,002 | 34.00% | 1.10% | 0 | £0.00 |
| Andreas Birkenstock 2 | Mar 27 | 451 | 27.49% | **3.10%** | 0 | £0.00 |
| Summer Birkenstock 2 | Mar 27 | 453 | 22.49% | 1.11% | 1 | £40.39 |
| Martin birkenstock 90 2 | Mar 27 | 448 | 28.99% | 0.90% | 0 | £0.00 |
| **Campaign total** | | | | | **1** | **£40.39** |

### Revenue Summary

| Source | Revenue (12mo) | Orders | Cost | Net |
|--------|---------------|--------|------|-----|
| Flows (automated) | £748.11 | 11 | £0 (always on) | £748.11 |
| Campaigns (manual) | £40.39 | 1 | Team time | £40.39 |
| **Total email revenue** | **£788.50** | **12** | | |
| **Klaviyo cost** | | | **~£480/yr** | |
| **Net after Klaviyo** | | | | **~£308/yr** |

Flows are carrying the economics right now. Campaigns are the growth lever.

---

## Targets

We focus on **one metric at a time**, in order. Each target has a threshold before we move to the next.

| Priority | Metric | Current Best | Target | Status |
|----------|--------|-------------|--------|--------|
| 1 | Open rate | 28.99% (Martin) | >25% sustained | ACHIEVED |
| 2 | **Click rate** | **3.10% (Andreas)** | **>3% sustained** | **IN PROGRESS** |
| 3 | Conversion rate | 0.22% (Summer) | >1% | NEXT |
| 4 | List growth | ~1,352 reachable | 3,000+ | ONGOING |

### Why This Order

- **Opens** prove the list is alive and recognises the brand. Done.
- **Clicks** prove the email content and offer are compelling. One person hit 3.1% — now everyone needs to.
- **Conversion** proves the full funnel works (email click → site → purchase). Can't optimise this until clicks are consistent.
- **List growth** is the multiplier on everything above. More people in the funnel = more revenue from the same effort.

---

## Campaign Approach

### Team Competition (Current)

Three people (Andreas, Summer, Martin) each own a third of the list. Each writes their own email — subject line, layout, product picks. After each send, compare results and adopt what works.

**Cadence:** Fortnightly, Tuesday/Wednesday, 10–11am UK time.

### What We Know So Far

| Learning | Evidence | Action |
|----------|----------|--------|
| Short curiosity subject lines win clicks | Andreas 3.10% vs Martin 0.90% | Adopt short + curiosity approach |
| Long descriptive subjects get opens but not clicks | Martin best open rate, worst click rate | Avoid over-selling in subject |
| Preview text matters | Andreas used it, Martin didn't | Always set preview text |
| The funnel can convert | Summer got a sale | Proof of concept — keep going |

### Campaign 3 Decision (Next Send)

Options:
- **A:** Full list again (~1,350) — everyone adopts Andreas's approach, iterate on click rate
- **B:** 12–24 month segment only (501) — test if lapsed buyers respond differently
- **C:** Split messaging by segment — different content for 6–12 vs 12–24 month

**Decision:** TBD — discuss next session

---

## Flow Strategy

Flows are the quiet earners. They run automatically and convert at much higher rates than campaigns because they catch people at the right moment.

| Flow | Status | Working? | Next Action |
|------|--------|----------|-------------|
| Abandoned Checkout | Live | Yes — 8% conv rate, £468/yr | Leave it. Review content quarterly |
| Browse Abandonment | Live | Yes — 3.1% conv rate, £72/yr | Leave it. Small volume but positive |
| Welcome Series | Not built | — | **Build this** — every new subscriber should get an intro sequence |
| Post-Purchase | Not built | — | Later — thank you + cross-sell after first order |
| Win-Back | Not built | — | Later — automate what campaigns are doing manually |

---

## List Growth

This is the biggest lever. All the optimisation in the world won't matter if we're emailing the same 1,350 people.

### Current Growth Sources
- Shopify checkout opt-in (primary)

### Growth Opportunities to Explore
- Site popup / flyout for email capture
- Post-purchase "get notified about sales" opt-in
- Google Shopping landing pages with email capture
- In-store sign-up (if applicable)

### Growth Target
| Milestone | List Size | Expected Campaign Revenue/mo | Why It Matters |
|-----------|-----------|------------------------------|----------------|
| Now | ~1,350 | ~£20 | Barely covers Klaviyo |
| Target 1 | 3,000 | ~£50–80 | Campaigns break even on their own |
| Target 2 | 5,000 | ~£100–150 | Email becomes a real channel |
| Target 3 | 10,000 | ~£250–400 | Meaningful % of total revenue |

*Estimates assume current conversion rates improve as we optimise.*

---

## Economics — Is Klaviyo Worth It?

**Right now: marginally yes, because of flows.**

| | Annual |
|---|--------|
| Flow revenue | £748 |
| Campaign revenue (projected, 24 sends/yr) | ~£480 (at current rate) |
| **Total projected** | **~£1,228** |
| Klaviyo cost | ~£480 |
| **Net** | **~£748** |

**At 3,000 subscribers:**
- Klaviyo cost rises to ~£600–720/yr
- But revenue scales with list size and improving conversion
- Flow revenue should grow proportionally with site traffic
- Campaign revenue grows with list size

**The real ROI question:** What does it cost to acquire a Birkenstock customer through Google Shopping? If CAC is £5–10, then every repeat email buyer saves that. 12 email-driven orders/year = £60–120 in saved acquisition costs on top of the margin.

---

## Review Cadence

- **After each campaign:** Update results in this doc, note what worked
- **Monthly:** Review flow performance, list growth, Klaviyo cost vs revenue
- **Quarterly:** Reassess strategy, targets, and whether Klaviyo is still justified

---

## Open Questions

1. What did Andreas do differently in his email to get 3.1% click rate?
2. Should Campaign 3 go to the full list or focus on the 12–24 month lapsed segment?
3. Is a Welcome Series flow worth building now, or wait until list growth is happening?
4. What is the actual Google Shopping CAC for Birkenstock — needed for the true ROI calculation
5. The Klaviyo timezone is set to US/Eastern — needs changing to Europe/London

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02 | Start Birkenstock repurchase campaigns | Birkenstock has highest repeat-buy potential |
| 2026-03 | Split campaigns 3 ways (team competition) | Learn faster through parallel experimentation |
| 2026-03-28 | Focus on click rate as primary target | Open rates already strong; clicks are the bottleneck |
| 2026-03-28 | Created this strategy doc | Need structured tracking alongside discussions |
