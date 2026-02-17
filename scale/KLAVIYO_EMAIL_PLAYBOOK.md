# Klaviyo Email Playbook — Brookfield Comfort

**Created:** February 2026
**Updated:** February 2026
**Goal:** Increase repeat purchase rate from 6.8% toward 15%
**Approach:** One core audience, content driven by stock, strict contact limits

---

## The Model

```
Check Stock → Decide What to Push → Build Email → Send to Eligible Segment
```

The content rotates based on stock. The audience is managed through a lifecycle that limits contact and removes non-buyers.

---

## Customer Lifecycle

A customer enters this lifecycle 90 days after their last Birkenstock purchase. They get a maximum of **3 emails**. If they don't buy, they rest for **150 days**. If the final attempt fails, they're removed.

```
DAY 0: Customer buys Birkenstock
  │
  │ (90 days, no repeat purchase)
  │
DAY 90: ──► ENTERS SEGMENT ("Fresh")
  │
  │ Email 1 (next scheduled send)
  │
  │ (2-3 weeks, no purchase)
  │
  │ Email 2
  │
  │ (2-3 weeks, no purchase)
  │
  │ Email 3 (final attempt)
  │
  │ (no purchase after Email 3)
  │
  ▼
EXHAUSTED ──► Suppress for 150 days
  │
  │ (150 days pass)
  │
  ▼
REACTIVATION ──► One final email
  │
  ├── Buys → back in the cycle (resets to Day 0)
  │
  └── Doesn't buy → REMOVE from list permanently
```

### Lifecycle Summary

| Stage | Condition | Action | Max Emails |
|-------|-----------|--------|------------|
| Fresh | 90+ days since purchase, 0 emails received | Send next campaign | — |
| Active | Received 1-2 emails, hasn't bought | Continue sending | — |
| Final | Received 3rd email, hasn't bought | Suppress | 3 total |
| Resting | Suppressed, 150-day cooldown | Do nothing | 0 |
| Reactivation | 150 days since suppression | One last attempt | 1 |
| Dead | Failed reactivation | Remove from list | 0 |

**If they buy at ANY stage** → they exit the lifecycle and re-enter 90 days later as "Fresh" again.

---

## Klaviyo Segment Setup

### Segment 1: "Birk — Eligible" (send targets)
- Placed Order containing "Birkenstock" at least once
- Placed Order zero times in the last 90 days
- Has received campaign tagged `birk-repurchase` fewer than 3 times
- NOT in list "Birk — Resting"
- NOT in list "Birk — Dead"
- Not suppressed

### List: "Birk — Resting"
- Customers who have received 3 emails with no purchase
- Added manually (or via Klaviyo flow) after 3rd email with no conversion
- **Review quarterly:** anyone who has been resting 150+ days → move to Segment 2

### Segment 2: "Birk — Reactivation"
- In list "Birk — Resting"
- Added to resting list 150+ days ago
- → Send one final email
- If no purchase within 14 days → move to "Birk — Dead"

### List: "Birk — Dead"
- Permanent removal — no further emails
- These customers are not worth the Klaviyo cost

---

## Content Types (same audience, different stock focus)

Every 1-2 weeks, check stock and pick one:

### Type A: Best Sellers / Repurchase Prompt

**When to use:** Default. When core styles are well stocked.

| Field | Value |
|-------|-------|
| Subject line A | "Birkenstock — Genuine. In Stock." |
| Subject line B | "Ready for another pair of Birkenstock?" |
| Content | Top 5 proven models currently in stock |
| Discount | None |
| Tone | Specialist, authorised supplier, clean |

**Product selection:** Milano, Arizona, Bend, Gizeh, + one seasonal — only include if stock is healthy.

---

### Type B: New Arrivals

**When to use:** When fresh stock lands — new styles, colourways, restocked sellers.

| Field | Value |
|-------|-------|
| Subject line A | "Just Landed — New Birkenstock for Spring/Summer" |
| Subject line B | "New Styles Now Available" |
| Content | 3–6 new/restocked products |
| Discount | None (new stock = full price) |
| Tone | "Just arrived" — factual, not hype |

**Product selection:** Based on what actually arrived. Prioritise best sellers restocked and new seasonal styles.

---

### Type C: Clearance / Last Pairs

**When to use:** End of season (Aug/Sep for summer). Not now — stock is being loaded for the season.

| Field | Value |
|-------|-------|
| Subject line A | "Last Pairs — Birkenstock" |
| Subject line B | "Final Stock — Selected Birkenstock Styles" |
| Content | 5–10 products with ~~original~~ → sale price AND sizes listed |
| Discount | Yes — 20–40% off RRP, always above cost |
| Tone | "Last pairs" — factual scarcity |

**Critical:** List available sizes explicitly. Don't waste clicks.
**Also:** Pause Google Ads on clearance products.

---

## Email Structure (all types)

1. **Header:** "Genuine Birkenstock. Fast UK Delivery."
2. **Intro:** 1–2 lines. What's in the email and why.
3. **Product grid:** 3–6 products (max 10 for clearance)
   - Product image
   - Model name
   - Price (or sale price for clearance)
   - Sizes available (clearance only)
   - "View Style" / "Shop Now" CTA
4. **Footer:** Genuine product, direct supply, fast dispatch, reviews

---

## Office Process — Quick Reference

### Every 2 weeks (Tuesday morning, 30 mins)

**1. Check stock — what Birkenstock needs pushing?**
- Any new deliveries landed? → Type B email (new arrivals)
- Core sellers well stocked? → Type A email (best sellers)
- End of season leftovers? → Type C email (clearance — later in year)
- Nothing worth pushing? → Skip. Don't send for the sake of it.

**2. Open Klaviyo — check "Birk — Eligible" segment**
- How many people in it?
- Worth sending? (if pool is tiny, wait)

**3. Build the email — 3-6 products from step 1**
- Drop into template
- Tag: `birk-repurchase`
- Target: "Birk — Eligible" only
- Schedule: 10:00-11:00am Tue or Wed

**4. Done.** Move on with your day.

### The following Tuesday (5 mins)

**5. Check results in Klaviyo** — opens, clicks, orders, revenue

**6. Log it** — quick note in decision log (SCALE_PLAN.md)

### Once a quarter — May, Aug, Nov, Feb (15 mins)

**7. Housekeeping in Klaviyo:**
- Anyone received 3 emails, no purchase? → Move to "Birk — Resting"
- Anyone resting 150+ days? → Send one reactivation email
- Anyone failed reactivation? → Move to "Birk — Dead"
- Check list health: Eligible vs Resting vs Dead

**Total time commitment: 30 mins fortnightly + 5 min review + 15 mins quarterly.**

---

## Send Rules

| Rule | Value |
|------|-------|
| Check stock | Every 1–2 weeks |
| Max emails per customer | 3 before suppression |
| Min gap between sends | 2 weeks |
| Send day | Tuesday or Wednesday |
| Send time | 10:00–11:00am |
| Suppression period | 150 days after 3rd email |
| Reactivation | 1 final email after 150 days |
| Permanent removal | If reactivation fails |
| Tag all campaigns | `birk-repurchase` (for tracking in Klaviyo) |

---

## Timing Example

For a customer who enters at Day 90:

| Week | Action | Notes |
|------|--------|-------|
| Week 1 | Email 1 | First contact — Type A, B, or C based on stock |
| Week 2 | — | No send. Monitor Email 1 results. |
| Week 3 | Email 2 | Different content/products if possible |
| Week 4 | — | No send. Monitor. |
| Week 5 | Email 3 (final) | Last chance before suppression |
| Week 6–26 | Suppressed | 150-day rest. No contact. |
| Week 27 | Reactivation email | One shot. Different subject line — "We miss you" or "Still looking for Birkenstock?" |
| Week 29 | Review | Bought → reset. Didn't buy → remove permanently. |

**Total contact over ~7 months:** 4 emails maximum.

---

## Weekly/Bi-Weekly Process

```
1. CHECK STOCK (every 1-2 weeks)
   [ ] What needs pushing? Best sellers, new arrivals, or clearance?
   [ ] Pick 3-6 products to feature

2. CHECK SEGMENT
   [ ] How many in "Birk — Eligible"?
   [ ] Anyone hitting 3 emails with no purchase? → Move to "Birk — Resting"

3. BUILD & SEND
   [ ] Build campaign in Klaviyo
   [ ] Tag: birk-repurchase
   [ ] Target: "Birk — Eligible" segment only
   [ ] Send: Tuesday/Wednesday, 10:00-11:00am

4. MEASURE (7 days later)
   [ ] Open rate, click rate, orders, revenue
   [ ] Log results in decision log (SCALE_PLAN.md)
   [ ] Anyone converted? They exit the lifecycle.

5. QUARTERLY HOUSEKEEPING
   [ ] Review "Birk — Resting" list
   [ ] Anyone 150+ days? → Send reactivation email
   [ ] Anyone failed reactivation? → Move to "Birk — Dead"
```

---

## Measurement

| Metric | Target | Notes |
|--------|--------|-------|
| Open rate | 30%+ | Brand recognition should drive this |
| Click-through rate | 3%+ | |
| Orders per campaign | Track absolute | |
| Revenue per campaign | Track absolute | |
| Revenue per recipient | £0.50+ | Adds up on 1,800 recipients |
| Unsubscribe rate | <0.5% per send | If higher, reduce frequency |
| Conversion by email # | Track | Does Email 1, 2, or 3 convert best? |
| Repeat purchase rate | 6.8% → 12%+ (Year 1) | Monthly in Klaviyo |
| List health | Track | Eligible pool size, resting, dead |

---

## What's Next

| # | Action | When |
|---|--------|------|
| 1 | Build segments in Klaviyo (Eligible, Resting, Dead) | Now |
| 2 | Send first campaign — Type A (best sellers) | This week or next |
| 3 | Monitor 7 days | Week after first send |
| 4 | Send Email 2 — different content | 2-3 weeks after first |
| 5 | Build the weekly stock check habit | Ongoing |
| 6 | First quarterly housekeeping | May 2026 |

---

## Future Expansion

Once this manual process is proven and generating revenue:
- **Automate in Klaviyo** — flow triggered at 90 days, 3-email sequence, auto-suppress
- **Lunar segment** — same lifecycle if Lunar moves to Shopify
- **Size-specific targeting** — email customers when their specific size restocks
- **Post-purchase education** — sizing guides, care tips (builds trust for next purchase)

Get the manual Birkenstock process working first. Automate later.
