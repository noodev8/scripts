# Skechers Review — Reorder Decision

**Prepared:** 2026-07-10 · **For:** Skechers supplier meeting (~Aug 2026)
**Question:** Should we reorder Skechers next year, and if so, which styles?
**Source:** `Skechers-Profit.csv` export + `sales`/`skusummary` DB comparison.

---

## Bottom line

**Skechers is one of only three loss-making brands we carry.** As run, the range made a
**£55 loss**; on the channels we'll actually have next year (Amazon + Shopify, no shop) it's
**−£330**. Every other brand we stock makes money per unit. **Recommendation: do not reorder the
range.** Either exit, or take the meeting purely to (a) test 4 salvage styles on shallow runs at a
strict price floor, or (b) negotiate a lower landed cost — nothing else makes Skechers competitive
for the capital it ties up.

---

## 1. The channel split is the whole story

The flat −£55 hides three very different channels:

| Channel | Units | Return % | Revenue | **Profit** | £/unit |
|---|---|---|---|---|---|
| **CM3 (physical shop)** | 28 | 0% | £1,623 | **+£275** | **+£9.82** |
| SHP (Shopify) | 43 | 5% | £2,294 | −£21 | −£0.50 |
| **AMZ (Amazon)** | 103 | 14% | £5,884 | **−£309** | **−£3.47** |

- The **shop** carries the entire brand — full price, zero returns, ~£10/pair.
- **Amazon** moves the most volume (60% of units) and manufactures the whole loss, at −£3.47/pair
  and 14% returns. This is the "drop price hard to fight the Amazon buybox" effect, quantified.
- **We are closing the shop next year.** That removes the only profitable channel and leaves the
  brand at **−£330** on Amazon + Shopify.

---

## 2. It's a colour/model discipline problem, not "Skechers is bad"

The same shoe wins in one colour and bleeds in another:

| Style | Winning colour | Losing colour |
|---|---|---|
| 124836 Go Walk Flex | **Rose +£58** (7% ret) | Navy-White **−£31** (22% ret) |
| 205334 Pollard Osgood | **Black +£41** (0% ret) | Coconut **−£15** (breakeven = RRP) |
| 232457 Summits | **Dk Navy +£32** (0% ret) | Black-CC **−£13** |
| 233103 Equalizer | *(none — drop model)* | Black −£39 **+** Navy −£100 = **−£139** |

The single biggest disaster is the **233103 Equalizer** (−£139, 31% returns on Navy) — a fit/sizing
problem no price fixes. Drop the whole model.

---

## 3. Without the shop, only 4 styles clear breakeven

On Amazon + Shopify only (our go-forward channels):

| Style | RRP | Sold | Ret% | Sold @ | Breakeven | **AMZ+SHP £** | Read |
|---|---|---|---|---|---|---|---|
| 205517-CDB Garza Rowan | 64* | 13 | 15% | £75 | £73 | **+£32** | only works because RRP is wrong |
| 232457-DKNV Summits Dk Navy | 57 | 7 | 0% | £54 | £52 | **+£13** | cleanest — real headroom, 0 returns |
| 205334-BBK Pollard Black | 95 | 13 | 0% | £70 | £70 | +£3 | thin, but 0 returns |
| 124836-ROS Go Walk Rose | 75 | 10 | 10% | £61 | £61 | +£1.5 | £14 headroom to lift with discipline |

Everything else loses money without the shop propping it up. Held to a **breakeven+£4 floor**, these
four project to roughly **+£150–180** on this demand — versus −£330 as run. That is the realistic
Skechers business next year: **4 styles, strict price, thin profit. Not a volume play.**

\* **RRP data error:** Garza Rowan's stated RRP (£64) is *below* its cost floor (£73) and it sold at
£78 — the RRP is wrong (real-world ~£80+). Same flag on Pollard Coconut. The Garza "win" is really
"we accidentally sold at the correct price." Wherever the RRP looked right, Amazon lost money.

---

## 4. Size runs for the 4 salvage styles

Samples are thin (~6–9 pairs/style/year), so these are **shape, not precision** — and a single
pair per size ≈ a whole year's demand. Order **shallow single-depth**; returns cluster on the
extremes, so a tight run cuts both cost and return risk.

**205517-CDB — Garza Rowan (Mens)** · 14 sold · core UK 9–11.5
```
 7.5  8   9  10  10.5  11   12      13
  1   1   2   2    2    2   2(-1r)  2(-1r)     ← both returns on the extremes (12,13)
```

**232457-DKNV — Summits Dk Navy (Mens)** · 10 sold · **0 returns anywhere**
```
  8   9  10  10.5  11  12  13
  1   1   2    2    1   2   1                  ← cleanest curve; safest to order deeper
```

**205334-BBK — Pollard Black (Mens)** · 15 sold · 0 returns
```
 7.5  8   9  10  10.5  11  11.5  12  13
  2   1   2   2    2    2    2    1   1        ← dead flat 7.5–11.5
```

**124836-ROS — Go Walk Rose (Womens)** · 14 sold · core UK 8–10
```
  7  7.5  8  8.5   9  9.5    10  10.5  11
  1   1   2   1    2   3(-1r) 2    1    1      ← centre 8–10, thin the ends
```

**Pattern:** mens core **UK 9–12**, womens **8–10**; returns on the size extremes. Order ~8–14
pairs/style/year — the market won't absorb more.

---

## 5. How Skechers compares to every other brand

Sales table, ~2 years, ranked by profit **per unit** (the fairest "worth the shelf" measure):

| Brand | Units | Profit/unit | Margin | Total profit |
|---|---|---|---|---|
| Strive | 47 | £12.92 | 16% | £413 |
| **Birkenstock** | 5,384 | **£9.63** | 15.6% | **£47,627** |
| Roamers | 67 | £9.68 | 20% | £523 |
| Remonte | 53 | £9.30 | 12% | £428 |
| Grafters | 20 | £7.38 | 22% | £133 |
| Free Spirit | 105 | £5.70 | 12% | £490 |
| Hotter † | 86 | £5.57 | 10% | £407 |
| **Lunar** | 7,747 | **£4.66** | 12.2% | **£31,655** |
| Rieker | 500 | £4.27 | 7.4% | £1,759 |
| Goor | 580 | £4.11 | 13% | £2,066 |
| Scimitar | 39 | £4.02 | 13% | £149 |
| Mod Comfys | 49 | £1.25 | 4% | £46 |
| Crocs | 84 | −£0.57 | −1.8% | −£43 |
| **Skechers** | **174** | **−£0.35** | **−0.6%** | **−£55** |
| Bloch | 334 | −£0.39 | −1.5% | −£124 |

Skechers ranks **14th of 15** on profit per unit — loss-making alongside only Crocs and Bloch.
Every other brand makes money, even the tiny ones (Grafters clears £7/unit on 20 pairs).

**The opportunity cost is the real argument.** Birkenstock returns **£9.63/pair at 15.6%**; Lunar
**£4.66 at 12%**. Every pound of capital and hour of attention on Skechers earns £0 — the same
effort in Birkenstock or Lunar compounds. The 4 salvage styles together might make ~£150/year;
that's **~16 Birkenstocks.**

† **Hotter caveat (verified 2026-07-10):** "Hotter" is *not a range* — it's one style,
**SHAKE-II-BLACK** (Shake II Mary Jane). Its `skusummary.cost` and `rrp` are **NULL**, and the
profit is a **flat modelled £5.19 on every £55 sale** (implied assumed cost ~£29), not live
settlement. The £5.57/unit is therefore **plausible but un-auditable**: if the true cost is even ~£5
higher, it's breakeven. Combined with a **15% return rate** on a single Mary Jane, treat Hotter as
"break-even-to-modest," not a robust earner. It is *not* in Skechers' loss-making territory, but it's
softer than the table suggests — the gut feeling that it's "worse" has merit.

---

## 6. Recommendation for the meeting

1. **Do not reorder the Skechers range.** It's a break-even-at-best line competing for capital
   against brands that pay 12–16%.
2. If keeping the relationship, go in to **exit or renegotiate**, not to buy a season:
   - **Test, don't commit:** order *only* the 4 clean styles (Go Walk Rose, Pollard Black, Summits
     Dk Navy, Garza Rowan) on shallow single-depth runs, hold a hard **breakeven+£4 floor**, and
     watch whether disciplined pricing flips them before ever committing to a range.
   - **Or use it for leverage:** lower cost, sale-or-return, or marketing support. At current landed
     cost we can't beat the Amazon buybox *and* profit — the only thing worth discussing is cost. If
     they won't move, the cash belongs in Birkenstock.

---

### Data caveats
- `sales.profit` is a **modelled** per-unit net (VAT + referral + FBA + cost), stamped per SKU — not
  live marketplace settlement. Directionally sound and consistent across brands, but not penny-exact.
- CM3 = physical shop (being closed next year); excluded from all go-forward projections.
- Return rows (qty = −1) are accounting reversals; treated as fit/demand-risk signal, not a precise £ drag.
- 10 non-Skechers rows were stripped from the original CSV before analysis.
