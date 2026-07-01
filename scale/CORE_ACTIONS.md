# Core Actions — Brookfield Comfort

**Created:** 2026-03-03
**Model:** Isolated, delegatable segments. Each is a lego brick. Add more to scale.

## Current State — updated 28 Apr 2026

- **Active segments:** 14 (~£275k revenue, ~£158k GP combined)
- **Live tests:** Frisco (Amazon), RIEKER-SUM
- **Strategic context:** `scale/SCALE_PLAN.md` | **Manager report template:** `scale/SEGMENT_REPORTS.md`
- **Weekly routine:** bottom of this doc

> **Update this block whenever you change anything below.**

### How to read this doc

This is the **durable playbook** — strategy, economics, channel, seasonal cycle, stock rules and standing actions per segment. It deliberately holds **no sales/GP/stock numbers**: those decay. For live figures use the **Meeting Prep Query** (bottom) or the **Segments Google Sheet** (full overview with codes, channels, revenue, GP, status).

**Segment rules:** Keep segments under ~10 styles — more, split it. Fill blank slots until total revenue reaches £1M.

---

## IVES-WHITE / IVES: Lunar St Ives (Amazon)

**Strategy:** Stock depth. Never run out. This is the profit engine.
**Lead time:** 4 days | **Cost:** £12.50 | **Avg sell price:** ~£39–41 | **GP margin:** ~43% (after Amazon fees)
**Colourways (by GP):** White ≫ Navy Blue > Black Sole > Mid Blue > Beige > Grey > Black > Red. White is the monster.

### Actions

- [ ] Monitor FBA stock weekly — every stockout day is lost profit
- [ ] Reorder aggressively through summer. 4-day lead time = no excuse for stockouts
- [ ] White is the monster — always have depth on this
- [ ] Red is weakest of the 8 but still profitable — keep stocked, don't overcommit

---

## EVA-SEG: Birkenstock EVA (Shopify)

**Strategy:** Low-cost EVA across Arizona and Gizeh. Maximise price; low cost base = profitable even at discounts. If it grows, split by model.
**Lead time:** 6 months (ordered for 2026) | **Cost:** £18.75–20.83 | **RRP:** £45–50 | **Margin:** ~45–50%
EVA Black is 100% peak season (Mar–Jun). EVA White sells year-round.

### Arizona EVA — Top 5 pricing targets

| GroupID | Colour | Start price | Drop to if slow | Floor |
|---------|--------|:-----------:|:---------------:|:-----:|
| 0129423-ARIZONA | Black Narrow | £45 | £39 | £35 |
| 1019094-ARIZONA | Khaki Green Regular | £45 | £40 | £36 |
| 0129443-ARIZONA | White Narrow | £42 | £38 | £35 |
| 0129421-ARIZONA | Black Regular | £45 | £40 | £36 |
| 1019152-ARIZONA | Khaki Green Narrow | £42 | £38 | £35 |

### Actions

- [ ] Monitor weekly Mar–Jun: moving at these prices?
- [ ] If slow by late April, drop to the "drop to" column
- [ ] Gizeh EVA: same cost base, same logic — keep prices aligned with Arizona EVA
- [ ] Tail Arizona EVA colours (Gold, Rose Reptile, Eggshell, Popcorn): hold price as long as possible, discount from July to clear
- [ ] Do NOT reorder tail Arizona EVA colours next year. Top 5 only for 2027.

---

## BLAZE: Lunar Blaze (Amazon only)

**Strategy:** Demand recovery — stock is full but sales collapsed since May 2025 peak. The lever is Amazon listing health, pricing and visibility, **not** restocking.
**Lead time:** 4 days (same supplier as Ives) — irrelevant, stock is fine | **Cost:** £12.99 | **Avg sell price:** ~£32–35 | **Channel:** Amazon only
**Colours:** Navy (was dominant), Nude (seasonal tail), Black (smallest).

### Actions

- [ ] **Investigate the listing:** buy box %, ranking, reviews, competition — what changed since May 2025?
- [ ] **Pricing test:** is £32–35 still right? Has a competitor undercut?
- [ ] **Don't reorder.** Stock is full. Sell through what you have.
- [ ] If demand doesn't recover by end of peak (Aug 2026), consider clearance pricing
- [ ] Amazon-only — no Shopify, no shop floor

---

## RIEKER-WIN: Rieker Winter (Amazon)

**Strategy:** Brand ownership — rotating range. Owner selects, sells, clears, pre-orders. Defined by brand ownership, not fixed products; groupids change year to year.
**Lead time:** 2 weeks (in-season) | 6 months (pre-order) | **Cost:** £28–37 | **Avg sell price:** £50–68 | **Margin:** ~49%
**Season:** Oct–Feb | **DB flag:** `segment = 'RIEKER-WIN'`

### Owner's Seasonal Cycle

1. **Sep:** Winter order arrives → add to system, tag `RIEKER-WIN`, price, send to FBA
2. **Oct–Feb:** Sell. Monitor reorder screen. Best sellers → reorder mid-season (2-week lead). Introduce new styles if performing.
3. **Mar:** Season ends. Clear remaining stock — drop prices monthly until gone. Pre-order next winter range from Rieker catalogue using this season's data. (Historically ~Jun; 2026/27 batch placed Mar 2026.)

### Actions (season ending)

- [ ] Clear remaining winter stock at reduced prices
- [x] 2026/27 winter pre-order placed Mar 2026 — arriving ~Aug
- [ ] On arrival: tag, price, send proven winners to FBA. Pick further FBA candidates as Amazon ranking signals appear
- [ ] Amazon only. No Shopify.

---

## RIEKER-SUM: Rieker Summer

**Strategy:** Brand ownership — rotating range. Same model as RIEKER-WIN, summer catalogue.
**Channels:** Amazon is the core. Shopify listed but won't move much Rieker. Physical shop: keep 1 pair of each winning style on display (sells at RRP), bulk to FBA immediately — don't let shop stock hold back Amazon.
**Lead time:** 2 weeks (in-season) | 6 months (pre-order) | **Cost:** £26–29 | **Avg sell price:** ~£53 | **Margin:** ~49%
**Season:** Mar–Sep | **DB flag:** `segment = 'RIEKER-SUM'`

### Stock allocation rule (decided Mar 2026)

**Amazon first.** Last year Rieker stock sat in the shop while Amazon could have shifted it. A couple of shop sales shouldn't change the plan.

- On arrival: keep **1 pair per winning style** in the shop (RRP ~£67), **everything else straight to FBA** — don't wait
- Shopify price left to the pricing engine (won't sell much, no harm listed)
- Reorders follow the same rule: 1 for the shop, rest to FBA

### Owner's Seasonal Cycle

1. **Mar:** Summer order arrives → tag `RIEKER-SUM`, price, bulk to FBA (1 per style for shop)
2. **Mar–Sep:** Sell. Monitor reorder screen. Best sellers → reorder mid-season. Introduce new styles if performing.
3. **Oct:** Season ends. Clear remaining stock — drop prices monthly until gone.
4. **~Dec:** Pre-order next summer range using this season's data.

### How to tag new arrivals

```sql
-- Find untagged Rieker
SELECT groupid, shopifytitle FROM public.skusummary
WHERE brand ILIKE 'Rieker' AND segment IS NULL;

-- Tag them
UPDATE public.skusummary SET segment = 'RIEKER-SUM'
WHERE brand ILIKE 'Rieker' AND segment IS NULL;
```

### Actions

- [x] Tag all new groupids `RIEKER-SUM` (done Mar 2026)
- [x] Repriced all 4 Amazon groupids to £55 — profit marker price (Mar 2026)
- [ ] Send more stock to FBA from existing supply — no new buying until £55 test proves out
- [ ] Get remaining styles live on FBA
- [ ] Monitor sales at £55 — does buy box come and velocity hold?
- **No reorders until profitability confirmed at £55.** Early sales were losing money at £43–48.

---

## MILANO: Birkenstock Milano (Shopify)

**Strategy:** Price optimisation. Only 4 styles, all proven winners. Keep in stock, maximise price.
**Lead time:** 6 months (committed) | **Cost:** £37.50 | **RRP:** £90.00 | **Margin:** 49.1%
Dark Brown Regular sells at a premium to Black — price it accordingly. Highest GP-per-style in the Birk range. Sells year-round.

### Actions

- [ ] Check Shopify prices vs avg selling prices — room to push higher?
- [ ] Hold strong prices Mar–Jun, adjust if needed
- [ ] Dark Brown Regular is the premium — price above Black
- [ ] Keep all 4 in stock through summer

---

## BEND: Birkenstock Bend (Shopify)

**Strategy:** High-value trainer segment. White and Black Regular are the core; other colours secondary but profitable.
**Lead time:** 6 months (committed) | **Cost:** £52–56 | **RRP:** £125–135 | **Margin:** 44.5%
White Regular alone outperforms most entire Birk models; White + Black Regular = the bulk of segment GP. High RRP gives discount headroom. Premium customers, less price-sensitive (~£90–120 sell price).

### Actions

- [ ] White Regular is the star — never run out
- [ ] Black Regular is solid #2 — keep stocked
- [ ] Other colours profitable even with heavy discounting — don't cut, don't overcommit

---

## ARIZONA colour bricks + GENERAL (Shopify)

Birko-Flor Arizona, **re-cut May 2026** from the old width buckets (BF-REG/BF-NAR)
into performance **colour bricks** + a GENERAL monitor bucket. Each brick = the
canonical **Regular + Narrow pair only**. Seasonal dupes, material variants
(Vegan/Synthetics/Leopard), shade experiments (e.g. eggshell, new buckle colours)
and fresh arrivals live in **ARIZONA-GENERAL** and earn a brick when a **shade-pair**
reads as a sustained, dominant seller (human call off the demand ranking, no fixed
revenue bar). New codes always land in GENERAL first. Patent and Leather stay their
own segments.
**Lead time:** 6 months (committed) | **Cost:** £35.42 (some £37.50) | **RRP:** £80–90 | **Margin:** ~46%
Each brick has its own folder `scale/arizona-<colour>/` with the **size-availability**
report (`size_availability.py`) — per EU size, Reg+Nar, with the **Inv** (invoiced,
releasable now by paying the invoice) vs **Wsh** (future-order wishlist) split that
is the only in-season stock lever ([[feedback_birk_ordering_cycle]]).

### ARIZONA-BLACK — `0051791` Reg, `0051793` Nar
Volume leader (~92 u/yr Reg). No invoiced stock to release right now; lever is the future order.

### ARIZONA-BLUE — `0051751` Reg, `0051753` Nar
Fastest riser — split out because it was surging unseen in the old bucket. Narrow is a fresh £85 restock not moving (pricing question first); its `width` is null so fit resolves from the title.

### ARIZONA-BROWN — `0051701` Reg, `0051703` Nar
Premium price leader, sells year-round. Reg core stock-gutted but ~14 units invoiced/releasable for peak (invoice 5290099202, raised 27.05.2026).

### ARIZONA-WHITE — `0552681` Reg, `0552683` Nar
Most code-fragmented colour. Off-white shades (White Eggshell, Graceful Pearl) sit in GENERAL with real residual demand that should flow here as they deplete — keep brick depth up. ~19 units invoiced/releasable.

### ARIZONA-TAUPE — `1029470` Reg, `1029439` Nar
First promotion out of GENERAL (May 2026) on trajectory (~£4.4k trailing, a clear riser). Watch trailing revenue: a sustained fade is the relegation signal.

### ARIZONA-GENERAL — the monitor bucket (25 styles)
Scan, don't action. Report: `scale/arizona-general/shade_breakdown.py` (shade-pairs ranked by demand). Nearest promotion candidates: Stone Coin (~£2.8k), then the Eggshell/Pearl off-whites — none yet a dominant pair.

### Actions

- [ ] Brown: decide on releasing the invoiced core sizes for peak (the "6 weeks not 6 months" lever)
- [ ] Blue: price the £85 Narrow to move; protect the surging Regular's stock
- [ ] White: keep brick depth to absorb Eggshell/Pearl demand as the dupes deplete
- [ ] Taupe: confirm it holds above the relegation line
- [ ] GENERAL: occasional riser-sweep via `shade_breakdown.py` — promote a shade-pair when it's a clear, sustained riser

---

## GIZEH: Birkenstock Gizeh Regular (Shopify)

**Strategy:** Regular fit only. Price optimisation, keep top sellers stocked through summer.
**Lead time:** 6 months (committed) | **Cost:** £35.42–37.50 | **RRP:** £85–90 | **Margin:** ~48%
Two White Gizehs (Patent + Birko-Flor) both strong, not cannibalising. Patent Sand Brown and Vegan Pecan sell at full RRP — premium, low volume, leave them. Birko-Flor Blue is very peak-heavy (stock for spring, don't worry in winter). Birko-Flor White sells year-round.

### Actions

- [ ] Check Shopify prices vs avg — room to push Patent White and Birko-Flor White higher?
- [ ] Keep Birko-Flor Blue replenished for spring peak
- [ ] Hold strong prices Mar–Jun, adjust if needed
- [ ] Patent Sand Brown / Vegan Pecan at full RRP — leave them

---

## ZERMATT-SEG: Birkenstock Zermatt (Shopify)

**Strategy:** Winter slippers, two lines (cork latex + shearling). Regular fit only. Price optimisation, keep winners stocked.
**Lead time:** 6 months | **Cost:** £25 (cork) / £37.50 (shearling) | **RRP:** £60 / £90 | **Margin:** ~44–47%
**Season:** Year-round — cork peaks Mar–Jun, shearling peaks Jul–Feb | **DB flag:** `segment = 'ZERMATT-SEG'`

### Key Pricing

- Cork styles sell at **£48** — do not drop below £48
- Shearling styles sell at **£70–75** — higher cost base, strong margin

Narrow fits, Navy (high returns) and the low-volume shearling tail were dropped — only Regular fit in the segment.

### Actions

- [ ] Keep cork priced at £48 floor
- [ ] Light Grey cork (1015080) is the top seller — order depth for Sep, fill sizes 37–41 as priority
- [ ] Monitor Dark Anthracite cork (1014938) restock — strong seller, runs out
- [ ] Shearling order (Aug) committed — sell through winter, assess in spring

---

## REMONTE-WIN: Remonte Winter (Amazon)

**Strategy:** Sister brand to Rieker. Same supplier, 2-week lead, same seasonal cycle — manage alongside RIEKER-WIN. Highest per-unit economics of any unsegmented product (~£28 profit/sale); needs only ~180 units for £5k GP.
**Lead time:** 2 weeks (in-season) | 6 months (pre-order) | **Cost:** £34–38 | **Avg sell price:** £75–80 | **Margin:** ~49%
**Season:** Oct–Feb | **DB flag:** `segment = 'REMONTE-WIN'`

### Owner's Seasonal Cycle

Same as RIEKER-WIN: **Sep** order arrives → tag, price, FBA. **Oct–Feb** sell, monitor, reorder winners. **Mar** clear remaining, pre-order next range alongside Rieker.

### Actions

- [x] Tag all 4 groupids `REMONTE-WIN`
- [x] 2026/27 winter pre-order placed Mar 2026 — arriving ~Aug (alongside Rieker)
- [ ] FBA leftovers — leave in place for next season
- [ ] On arrival: tag, price, send proven winners to FBA
- [ ] Target: £5k GP for winter 2026/27
- [ ] Amazon only. Same owner as RIEKER-WIN.

---

## Segments not detailed here

Active in the DB, no detailed playbook yet:

- **ARIZONA-PATENT-SEG** (4 groupids) — own segment Mar 2026
- **FREE-SPIRIT** (3 groupids) — Amazon test, see `scale/SCALE_PLAN.md` §8
- **LAKE-SEG** (4 groupids) — winter slipper
- **MAYARI-SEG** (3 groupids)
- **UKD-SEG** (4 groupids) — see `ukd/README.md`

Add detailed playbooks here when active management warrants it.

**CRAP retired (May 2026):** every groupid lives in a managed segment regardless of winner/loser status — per-style action is carried by state inside a segment, not in/out membership. A `segment = 'CRAP'` filter in old queries is a no-op; remove it. Rationale in `CLAUDE_CONTEXT.md`.

**Brand pipeline:** see `scale/SCALE_PLAN.md` §8 (investigations, graduated segments, ruled-out options). Don't duplicate here.

---

## Meeting Prep Query

Run before any weekly or monthly meeting. Every segment's last 30 days vs the previous 30, with trend and current stock. **This replaces the static tables this doc used to carry — it's always current.**

```sql
WITH period AS (
  SELECT
    CURRENT_DATE - INTERVAL '30 days' AS last_start,
    CURRENT_DATE AS last_end,
    CURRENT_DATE - INTERVAL '60 days' AS prev_start,
    CURRENT_DATE - INTERVAL '30 days' AS prev_end
),
seg_sales AS (
  SELECT
    ss.segment,
    SUM(CASE WHEN s.solddate >= (SELECT last_start FROM period) THEN s.qty ELSE 0 END) AS units_last,
    SUM(CASE WHEN s.solddate >= (SELECT last_start FROM period) THEN s.soldprice * s.qty ELSE 0 END) AS rev_last,
    SUM(CASE WHEN s.solddate >= (SELECT last_start FROM period) THEN (s.soldprice - NULLIF(ss.cost,'')::numeric) * s.qty ELSE 0 END) AS gp_last,
    SUM(CASE WHEN s.solddate >= (SELECT prev_start FROM period) AND s.solddate < (SELECT prev_end FROM period) THEN s.qty ELSE 0 END) AS units_prev,
    SUM(CASE WHEN s.solddate >= (SELECT prev_start FROM period) AND s.solddate < (SELECT prev_end FROM period) THEN s.soldprice * s.qty ELSE 0 END) AS rev_prev,
    SUM(CASE WHEN s.solddate >= (SELECT prev_start FROM period) AND s.solddate < (SELECT prev_end FROM period) THEN (s.soldprice - NULLIF(ss.cost,'')::numeric) * s.qty ELSE 0 END) AS gp_prev
  FROM public.sales s
  JOIN public.skusummary ss ON ss.groupid = s.groupid
  WHERE ss.segment IS NOT NULL
    AND ss.segment != 'CRAP'
    AND s.qty > 0 AND s.soldprice > 0
    AND s.solddate >= (SELECT prev_start FROM period)
  GROUP BY ss.segment
),
seg_stock AS (
  SELECT
    ss.segment,
    SUM(CASE WHEN ls.ordernum = '#FREE' AND ls.deleted = 0 THEN ls.qty ELSE 0 END) AS local_stock,
    SUM(COALESCE(af.amzlive, 0)) AS fba_stock
  FROM public.skusummary ss
  JOIN public.skumap sm ON sm.groupid = ss.groupid
  LEFT JOIN public.localstock ls ON ls.code = sm.code
  LEFT JOIN public.amzfeed af ON af.code = sm.code
  WHERE ss.segment IS NOT NULL AND ss.segment != 'CRAP'
  GROUP BY ss.segment
)
SELECT
  COALESCE(s.segment, st.segment) AS segment,
  COALESCE(s.units_prev, 0) AS units_prev_30d,
  COALESCE(s.units_last, 0) AS units_last_30d,
  ROUND(COALESCE(s.gp_prev, 0)::numeric, 0) AS gp_prev_30d,
  ROUND(COALESCE(s.gp_last, 0)::numeric, 0) AS gp_last_30d,
  CASE
    WHEN COALESCE(s.gp_prev, 0) = 0 AND COALESCE(s.gp_last, 0) > 0 THEN 'NEW'
    WHEN COALESCE(s.gp_prev, 0) = 0 AND COALESCE(s.gp_last, 0) = 0 THEN 'IDLE'
    ELSE ROUND(((COALESCE(s.gp_last,0) - COALESCE(s.gp_prev,0)) / NULLIF(s.gp_prev,0) * 100)::numeric, 0) || '%'
  END AS trend,
  COALESCE(st.local_stock, 0) AS local_stock,
  COALESCE(st.fba_stock, 0) AS fba_stock
FROM seg_sales s
FULL OUTER JOIN seg_stock st ON st.segment = s.segment
ORDER BY COALESCE(s.gp_last, 0) DESC;
```

### How to read it

- **Trend +%** = GP growing vs previous 30d. Good. **-%** = dropping; challenge the owner: stock out? price too low? competition?
- **NEW** = no sales previous period, sales now (just started). **IDLE** = no sales either period (stock not arrived, or dead).
- **local_stock** = warehouse. **fba_stock** = live at Amazon FBA. Both at 0 with a dropping trend = about to run out, act now.
- Amazon segments (IVES, BLAZE, RIEKER, REMONTE) — fba_stock is what matters. Shopify segments (EVA-SEG, MILANO, BEND, ARIZONA, GIZEH, ZERMATT) — local_stock.
- **Seasonal:** Birk segments surge Mar–Jun, drop Jul–Feb; Rieker Winter is the opposite. Compare like-for-like months — a -30% on RIEKER-WIN in March is expected, not a problem.

---

## Weekly Routine (30 mins)

1. **Ives FBA stock check** — sizes running low? Reorder. (5 min)
2. **Blaze listing check** — buy box, price vs competitors, recent units. Demand-side, not stock. (5 min)
3. **Birkenstock EVA Shopify check** — Arizona top 5 + Gizeh EVA: selling at current prices? (5 min)
4. **Tail Arizona EVA** — selling? If not and past April, drop price. (5 min)
5. **Rieker Summer FBA check** — sell-through of new arrivals, reorder winners. (5 min)
6. **Rieker Winter clearance** — anything left? Drop price. (2 min)
7. **Birkenstock Shopify check** — Milano, Bend, Arizona BF Reg/Nar: stock and pricing. (5 min)
