# Amazon Pricing

The goal is simple: **find the best price for each Amazon SKU, and keep finding it as performance moves.** Price follows performance — creep up on strength, drop on dead stock — for **any brand or segment we sell on Amazon**, not one product family.

> Amazon = FBA only. Local/warehouse stock is irrelevant to Amazon pricing (that's `shopify-price/`). Amazon and Shopify are priced completely separately — different customers, different strategy.

## How a session works

There's no ritual. A session starts with the user saying what they want to look at — a colour, a segment, a brand, a single SKU, an ad-hoc question. Claude queries the database live and we discuss. Ask what they want; don't assume.

Two shapes of session:

- **Conversational** — single segment / colour / SKU, exploratory questions, investigations. The default. Documented in `AMZ_PRICING.md`.
- **Full segment review** — one comprehensive pass across a whole segment, auto-classified and batch-applied. Trigger: **"full `<segment>` review"** (e.g. "full ives review", "full rieker review"). Procedure in `AMZ_FULL_REVIEW.md`.

Everything durable lives in the database. Every price change goes to `amz_price_log` with rationale in `notes` — **don't keep markdown session journals.** This folder holds the engine and the per-segment registry, not a diary.

## The four docs

| File | What it is |
|---|---|
| `README.md` | This file — the front door and the coverage map. |
| `AMZ_PRICING.md` | **The engine.** Brand-neutral: philosophy, DB mechanics, the pricing decision framework, the carry-forward rules, how to apply & log. Read this for *how* Amazon pricing works here. |
| `AMZ_FULL_REVIEW.md` | **The procedure.** The parameterised full-segment review — pull data, classify 🟢/🟡/⚪, one dashboard, batch-apply. Takes a `{segment}` argument. |
| `AMZ_PRODUCTS.md` | **The registry.** Per-segment instance data: economics (cost / FBA fee / RRP / floor / ceiling), proven prices, and a short current-state note. This is where segment-specific knowledge lives — the engine reads its parameters from here. |
| `PROFIT_MODEL.md` | **The P&L.** How per-unit net profit is calculated — Shopify (locked, in code) and the fully-loaded Amazon stack (VAT + referral + FBA + DPD + wages + storage). Read before trusting `sales.profit` on AMZ (it's raw/unreliable) or building an `amazon_profit()`. |

## Coverage — segments under Amazon management

Every segment below is *managed* — the difference is **cadence**, not whether it earns attention. "Light" means a quick performance check on a longer cycle, **not** "ignore it". A thin segment that's being restocked and prepared per season still gets looked at.

| Segment | Brand(s) | ~Cost | ~RRP | ~FBA fee | Cadence |
|---|---|---|---|---|---|
| IVES-WHITE | Lunar | £15.99 | £45.00 | £3.06 | **Core** — first every session, per-size |
| IVES-COLOUR | Lunar | £15.99 | £45.00 | £3.06 | **Core** — 9 colours, reviewed together |
| LUNAR-GENERAL | Lunar | £13.21 | £39.70 | £3.01 | Active |
| BLAZE-SEG | Lunar | £12.99 | £39.00 | £3.09 | Active |
| LAKE-SEG | Lunar | £17.50 | £45.00 | £3.90 | Developing |
| RIEKER-SUM | Rieker | £28.12 | £65.38 | £3.21 | Developing — restock in progress |
| RIEKER-WIN | Rieker | £30.71 | £71.63 | £3.27 | Seasonal (winter) |
| UKD-SEG | Mod Comfys / Goor / Roamers | £15–23 | £39–60 | £3.2–3.4 | Watch |
| FREE-SPIRIT | Free Spirit | £21.52 | £59.99 | £3.21 | Light |
| STRIVE-SEG | Strive | £34.59 | £81.43 | £3.31 | Light |
| SKECHERS-SEG | Skechers | £35.84 | £75.54 | £3.34 | Light |
| REMONTE-WIN | Remonte | £34.63 | £81.00 | £3.27 | Seasonal (winter) |

Economics are per-segment averages — see `AMZ_PRODUCTS.md` for the exact figures, floors, ceilings, and current state per segment. Posture is a starting cadence the user can override any session.

**Live coverage snapshot** (run when you want current volumes — these move weekly, so they're not pinned in the doc):

```sql
SELECT sk.segment, sk.brand,
       SUM(CASE WHEN s.qty>0 THEN s.qty ELSE 0 END) AS units_90d,
       ROUND(SUM(s.profit)::numeric,0) AS profit_90d,
       MAX(s.solddate) AS last_sold
FROM sales s JOIN skusummary sk ON s.groupid = sk.groupid
WHERE s.channel='AMZ' AND s.solddate >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY sk.segment, sk.brand
ORDER BY profit_90d DESC;
```

## Strategy (the durable priorities)

1. **Priority 1 — IVES (FLE030).** The core Amazon product. Keep it stocked and priced as efficiently as possible. Volume-on-autopilot with a mature playbook.
2. **Priority 2 — broaden the engine.** Apply the same performance-driven pricing to every other segment we stock on Amazon. Each segment proves its own velocity — don't assume the IVES flywheel transfers (it's product-specific; see `AMZ_PRODUCTS.md` notes on UKD-SEG).
3. **No segment is "too small to manage."** Thin ≠ ignore. A segment being restocked and prepared for its season gets priced on the same principles; it just sits on a longer review cadence. Decisions about *what to stock or drop* are a separate task from pricing — don't fold range calls into a pricing session.
