# Profit Model — Shopify & Amazon (per-unit net)

Quick reference so we don't re-derive this. Both models pivot on **`cost`** =
`skusummary.cost` (varchar, per-pair landed ex-VAT). Fix the cost, the profit
follows.

---

## Shopify — LOCKED (source of truth)

Defined in code: `update_orders2.py` → `shopify_profit(sold, cost)`, mirrored by
`bcweb-server` `shopifyProfit`. Written to `sales.profit` per unit at order-sync
(commit a7cf657). Do not re-invent — change the code, not this doc.

```
VAT      = sold / 6                    # UK VAT = 1/6 of VAT-inclusive price
Gross    = sold - VAT - cost
Expenses = (0.30 + 0.029*sold)         # Shopify Payments fee
         + 1.00                        # packing / wages
         + 3.44                        # Royal Mail
Profit   = (Gross - Expenses) / 1.2    # flat /1.2 "cover refunds" haircut
```

---

## Amazon — fully-loaded (CONFIRMED from Profit_Checker, Jul 2026)

`sales.profit` for `channel='AMZ'` is **raw and unreliable** — it overstates
badly (IVES raw ~£14 vs loaded ~£5.80; Skechers AMZ sums *negative*). The
pricing tools (`amz-price`) only use a contribution margin `price - cost -
fbafee` for floors/ceilings — that is NOT the P&L figure. Use the model below
for actual profit.

```
VAT        = sold / 6
Referral   = sold * 0.15               # Amazon referral fee, flat 15%
FBA        = amzfeed.fbafee            # per-SKU, already in DB
DigitalFBA = FBA * 0.02                # regulatory "digital services" surcharge
DigitalRef = Referral * 0.02           # same 2% surcharge on the referral fee
Storage    = 0.33                      # fixed per-unit assumption
DPD        = 1.00                      # inbound freight, fixed per-unit
Wages      = 0.50                      # pick/pack labour, fixed per-unit

Gross      = sold - VAT - cost
Expenses   = Referral + FBA + DigitalFBA + DigitalRef + Storage + DPD + Wages
Profit     = (Gross - Expenses) / 1.2  # same /1.2 refund haircut as Shopify
```

Worked example from the sheet (Sold £22.99, Cost £10.99, FBA £3.05):
VAT 3.83 · Referral 3.45 · Expenses 8.46 · Gross 8.17 · **Profit −£0.24**.

### Notes
- The `/1.2` haircut **does** apply to Amazon (verified: −0.24 only reconciles
  with it). Same haircut as Shopify.
- Storage / DPD / Wages are flat per-unit assumptions, not per-SKU — revisit if
  the owner re-costs logistics.
- **UKD cost rebate:** UKD-sourced products get a 3.75% rebate on cost
  (£0.41 on a £10.99 cost in the sheet). Apply to `cost` before the model for
  UKD-SEG only; ignore for other segments.

Next step → build `amazon_profit(sold, cost, fbafee)` and backfill
`sales.profit` for AMZ the same way Shopify was done (currently NOT in code).

---

## Next time we touch this
Skechers cost is being re-derived from invoices (Jul 2026). Recompute Shopify
`sales.profit` immediately once cost lands; Amazon waits on the model above.
