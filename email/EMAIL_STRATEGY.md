# Email Strategy — Brookfield Comfort

**Created:** 2026-03-28
**Last reviewed:** 2026-03-28
**Status:** Active — building the asset

---

## The Thesis

We spend money on Google Shopping to acquire Birkenstock customers. Email turns those one-time buyers into repeat customers — for free. Every repeat sale driven by email is one we didn't pay Google for.

**Google Shopping = renting customers. Email list = owning them.**

The goal: build the email list into a self-sustaining revenue channel that compounds over time as the list grows. Send as often as possible to maximise revenue and learning — frequency is governed by unsubscribe rate, not a fixed calendar.

---

## Current State — Snapshot (2026-03-28)

### Segments

| Segment | Type | Purpose |
|---------|------|---------|
| Birkenstock 6–12 months since purchase | Target | Recently lapsed — emailed in Campaigns 1 & 2 |
| Birkenstock 12–24 months since purchase | Target | Overdue buyers — Campaign 3 focus |
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

### Campaigns — Variation-Level Results

Full results tracked in the **Emails** tab of the Segments Google Sheet. Summary below.

| Campaign | Sender | Date | Click Rate | Orders | Revenue |
|----------|--------|------|-----------|--------|---------|
| Birkenstock 90 Days Round 1 Var A | Andreas | Feb 24 | **3.37%** | 1 | £69.55 |
| Birkenstock 90 Days Round 1 Var B | Andreas | Feb 24 | 2.21% | 0 | £0.00 |
| Martin birkenstock 90 Var A | Martin | Mar 10 | 1.60% | 0 | £0.00 |
| Martin birkenstock 90 Var B | Martin | Mar 10 | 0.60% | 0 | £0.00 |
| Andreas Birkenstock 2 Var A | Andreas | Mar 27 | 1.77% | 0 | £0.00 |
| Andreas Birkenstock 2 Var B | Andreas | Mar 27 | **4.44%** | 0 | £0.00 |
| Summer Birkenstock 2 | Summer | Mar 27 | 1.11% | 1 | £40.39 |
| martin birkenstock 90 2 | Martin | Mar 27 | 0.90% | 0 | £0.00 |
| **Campaign total** | | | | **2** | **£109.94** |

A/B testing discontinued from Campaign 3 onwards — one email per sender for cleaner tracking.

### Revenue Summary

| Source | Revenue (12mo) | Orders |
|--------|---------------|--------|
| Flows (automated) | £748.11 | 11 |
| Campaigns (manual) | £109.94 | 2 |
| **Total email revenue** | **£858.05** | **13** |
| **Klaviyo cost** | **~£480/yr** | |
| **Net after Klaviyo** | **~£378/yr** | |

Flows are carrying the economics right now. Campaigns are the growth lever.

---

## Targets

We focus on **one metric at a time**, in order. Each target has a threshold before we move to the next.

| Priority | Metric | Current Best | Target | Status |
|----------|--------|-------------|--------|--------|
| 1 | Open rate | 39.21% (Andreas Round 1 Var A) | >25% sustained | ACHIEVED |
| 2 | **Click rate** | **4.44% (Andreas Var B)** | **>3% sustained across team** | **IN PROGRESS** |
| 3 | Conversion rate | 0.22% (Summer Birk 2) | >1% | WATCHING (see design analysis) |
| 4 | List growth | ~1,352 reachable | 3,000+ | ONGOING |

---

## Send Cadence

**No fixed schedule. Send as often as the list will tolerate.**

The guardrail is **unsubscribe rate**, not a calendar:
- Current unsub rate: **under 0.7%** across all sends — healthy
- If unsub rate stays **under 1%**, the list is fine with the frequency
- If unsubs spike, pull back
- More sends = more revenue + more data to learn from

Preferred send window: Tuesday/Wednesday, 10–11am UK time (but not a rule).

---

## Campaign Approach

### Team Competition

Three people (Andreas, Summer, Martin) each own a third of the list. Each writes their own email. After each send, compare results and adopt what works. No more A/B testing — one email per person per campaign.

> **Update 2026-04-10:** Going forward this is a **two-person** competition — Andreas and Summer only. Martin has been moved to packing and is no longer writing campaigns. List splits 2 ways from Campaign 3 onwards.

### What We Know — Design Analysis (2026-03-28)

We compared the two most important emails: Andreas Var B (best CTR) vs Summer Birkenstock 2 (only sale).

**Andreas Var B (4.44% click rate, 0 orders):**
- Pure text — no images, no products, no prices
- Personal tone: "Hey Andreas", feels like a friend messaging
- Creates curiosity: "quietly dropped prices", "before sizes go"
- Single CTA: "VIEW LATEST BIRKENSTOCK"
- Click driven by **curiosity** — must click to see products

**Summer Birkenstock 2 (1.11% click rate, 1 order):**
- Full product catalogue — hero image, 6 products with photos, names, prices
- Crossed-out prices showing reductions
- Multiple "Shop now" buttons per product
- Branded layout with BC logo
- Email **is** the shop — browse before clicking

**The insight:** These are two different strategies:
- **Curiosity-driven** (Andreas) = maximises clicks but some are just browsing
- **Product-led** (Summer) = fewer clicks but pre-qualifies buyers, clicks convert

**For Campaign 3:** Consider a blend — Andreas's personal tone and urgency, with 1–2 hero products shown so people have a reason to click AND enough info to buy when they land.

Email designs are stored in `email/design/` with filenames matching campaign names.

### Campaign 3 Plan

- **Segment:** 12–24 month lapsed buyers only (~500 people)
- **Split:** Random 3-way list (Andreas, Summer, Martin — ~167 each)
- **Primary metric:** Click rate (target >3% for all senders)
- **Secondary metric:** Conversion/orders — watching whether design approach affects purchase
- **A/B testing:** No — one email per sender
- **Design guidance:** Team to review Andreas Var B design, consider blending curiosity + product approaches

### Learnings Log

| Learning | Evidence | Action |
|----------|----------|--------|
| Short curiosity subjects win clicks | Andreas 3.10% vs Martin 0.90% | Adopt short + curiosity approach |
| Long descriptive subjects get opens not clicks | Martin best open rate, worst click rate | Avoid over-selling in subject |
| Preview text matters | Andreas used it, Martin left blank | Always set preview text |
| Email design is the biggest lever | Same subject, Var B got 151% more clicks | Design matters more than subject line |
| Curiosity design = clicks, product design = conversions | Andreas 4.44% / 0 orders vs Summer 1.11% / 1 order | Blend both: personal tone + 1-2 hero products |
| Andreas is consistently the best performer | Avg 2.95% CTR vs Martin 1.03%, Summer 1.11% | Team should study his approach |

---

## Flow Strategy

Flows are the quiet earners. They run automatically and convert at much higher rates than campaigns.

| Flow | Status | Working? | Next Action |
|------|--------|----------|-------------|
| Abandoned Checkout | Live | Yes — 8% conv rate, £468/yr | Leave it. Review content quarterly |
| Browse Abandonment | Live | Yes — 3.1% conv rate, £72/yr | Leave it. Small volume but positive |
| Welcome Series | Not built | — | Build when list growth starts |
| Post-Purchase | Not built | — | Later — thank you + cross-sell |
| Win-Back | Not built | — | Later — automate what campaigns do manually |

---

## List Growth

The biggest multiplier. 4.44% of 225 people = 10 clicks. 4.44% of 5,000 = 222 clicks.

### Current Growth Sources
- Shopify checkout opt-in (primary)

### Growth Opportunities to Explore
- Site popup / flyout for email capture
- Post-purchase "get notified about sales" opt-in
- Google Shopping landing pages with email capture

---

## Economics — Is Klaviyo Worth It?

**Right now: marginally yes, because of flows.**

| | Annual |
|---|--------|
| Flow revenue | £748 |
| Campaign revenue (projected) | ~£480 (at current rate) |
| **Total projected** | **~£1,228** |
| Klaviyo cost | ~£480 |
| **Net** | **~£748** |

**The real ROI question:** What does it cost to acquire a Birkenstock customer through Google Shopping? If CAC is £5–10, every repeat email buyer saves that. 12 email-driven orders/year = £60–120 in saved acquisition costs on top of the margin.

---

## Tracking

- **Campaign results:** Tracked in the **Emails** tab of the Segments Google Sheet (live data from Klaviyo MCP)
- **Email designs:** Stored in `email/design/` — filenames match campaign names
- **Klaviyo MCP:** Connected and working (read-only). Can pull campaigns, flows, segments, metrics directly.

---

## Open Questions

1. What is the actual Google Shopping CAC for Birkenstock — needed for true ROI calculation
2. The Klaviyo timezone is set to US/Eastern — needs changing to Europe/London
3. Should Campaign 3 blend curiosity + product design, or test them as separate approaches?

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02 | Start Birkenstock repurchase campaigns | Birkenstock has highest repeat-buy potential |
| 2026-03 | Split campaigns 3 ways (team competition) | Learn faster through parallel experimentation |
| 2026-03-28 | Focus on click rate as primary target | Open rates already strong; clicks are the bottleneck |
| 2026-03-28 | Drop A/B testing from Campaign 3 | One email per sender = cleaner tracking |
| 2026-03-28 | Drop fixed 2-week cadence rule | Unsub rate is the guardrail, not a calendar. Send often, watch unsubs. |
| 2026-03-28 | Campaign 3 targets 12–24 month segment only | ~500 lapsed buyers, fresh audience, split 3 ways |
| 2026-03-28 | Design analysis: curiosity vs product-led | Both have value — blend for Campaign 3 |
