# Klaviyo Email Playbook — Brookfield Comfort

**Created:** February 2026
**Updated:** February 2026
**Status:** Manual — one campaign only

---

## The One Campaign: Birkenstock 90-Day Repurchase

Customers who bought Birkenstock 90+ days ago and haven't bought again get one email featuring in-stock best sellers.

That's it. One segment, one email, one goal: get the second purchase.

---

## Klaviyo Segment

**Name:** "Birk — 90 Day Non Buyers"

**Conditions:**
- Placed Order containing "Birkenstock" at least once
- Last Birkenstock order was 90+ days ago
- Has NOT placed any order in the last 90 days
- Not suppressed / unsubscribed

---

## The Email

| Field | Value |
|-------|-------|
| Subject line | "Ready for another pair of Birkenstock?" |
| Content | Top 5 in-stock best sellers (Milano, Arizona, Bend, Gizeh + 1 seasonal) |
| Discount | None |
| Tone | Specialist, authorised supplier, clean |
| Tag | `birk-repurchase` |
| Send day | Tuesday or Wednesday |
| Send time | 10:00–11:00am |

### Email Structure

1. **Header:** "Genuine Birkenstock. Fast UK Delivery."
2. **Intro:** 1–2 lines. Short and direct.
3. **Product grid:** 5 products — image, model name, price, "Shop Now" CTA
4. **Footer:** Genuine product, direct supply, fast dispatch

---

## Process (Every 2 Weeks, ~20 mins)

1. Check "Birk — 90 Day Non Buyers" segment size in Klaviyo
2. If big enough to be worth sending → check which best sellers are in stock
3. Build email with 5 in-stock products
4. Tag `birk-repurchase`, target segment, schedule for Tue/Wed 10am
5. Done

### One Week Later (~5 mins)

- Check results: opens, clicks, orders, revenue
- Log in decision log below

---

## Results Log

| Date | Segment Size | Opens | Clicks | Orders | Revenue | Notes |
|------|-------------|-------|--------|--------|---------|-------|
| | | | | | | |

---

## Rules

- One email per customer per cycle (no follow-ups yet)
- Minimum 2 weeks between sends to the segment
- Don't send if segment is tiny or stock is poor
- If a customer buys, they exit the segment automatically (90-day clock resets)

---

## Future (only after this is proven)

- Add a second follow-up email for non-responders
- Test different subject lines
- Automate via Klaviyo flow
- Expand to other brands if repeat purchase data supports it
