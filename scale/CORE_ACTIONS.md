# Core Actions — Brookfield Comfort

**Created:** 2026-03-03
**Model:** Isolated, delegatable segments. Each is a lego brick. Add more to scale.

## Current State — updated 28 Apr 2026

- **Active segments:** 14 (~£275k revenue, ~£158k GP combined)
- **Recent absorptions:** Madrid EVA → EVA-SEG, Arizona Patent → ARIZONA-BF-REG/NAR, REMONTE-WIN promoted from investigation
- **Live tests:** Frisco (Amazon, first sales Mar 2026), RIEKER-SUM (slow start at £55)
- **Strategic context:** `scale/SCALE_PLAN.md` (current state, levers, brand pipeline)
- **Manager report template:** `scale/SEGMENT_REPORTS.md`
- **Weekly routine:** bottom of this doc

> **Update this block whenever you change anything below.**

### Segment Map

**See the Segments Google Sheet** — full segment overview with codes, channels, revenue, GP, and status.

**Minimum to qualify as a segment: £5k+ revenue.** Below that, nobody owns it.
**Keep segments under ~10 styles.** More than that — split it.
**Target: fill blank slots until total revenue reaches £1M.**

---

## IVES-WHITE / IVES: Lunar St Ives (Amazon)

**Strategy:** Stock depth. Never run out. This is the profit engine.
**Lead time:** 4 days
**Cost:** £12.50 | **Avg sell price:** ~£39–41 | **GP margin:** ~43% (after Amazon fees)

### Core Colourways (ordered by GP)

| GroupID | Colour | Units (12m) | Revenue | GP | Last sale |
|---------|--------|------------:|--------:|---:|-----------|
| FLE030-IVES-WHITE | White | 1,425 | £56,864 | £39,051 | 2 Mar |
| FLE030-IVES-NAVY-BLUE | Navy Blue | 412 | £16,780 | £11,630 | 2 Mar |
| FLE030-IVES-BLACKSOLE | Black Sole | 409 | £16,309 | £11,197 | 1 Mar |
| FLE030-IVES-MIDBLUE | Mid Blue | 279 | £11,016 | £7,528 | 27 Feb |
| FLE030-IVES-BEIGE | Beige | 272 | £10,801 | £7,401 | 2 Mar |
| FLE030-IVES-GREY | Grey | 249 | £9,746 | £6,634 | 2 Mar |
| FLE030-IVES-BLACK | Black | 231 | £9,484 | £6,597 | 27 Feb |
| FLE030-IVES-RED | Red | 126 | £4,548 | £2,973 | 30 Jan |

**Total 12m GP: £93,012** from 8 colourways.

### Actions

- [ ] Monitor FBA stock weekly — every stockout day is lost profit
- [ ] Reorder aggressively through summer. 4-day lead time = no excuse for stockouts
- [ ] White is the monster (£39k GP) — always have depth on this
- [ ] Red is weakest of the 8 but still £3k GP — keep stocked but don't overcommit

---

## EVA-SEG: Birkenstock EVA (Shopify)

**Strategy:** Low-cost EVA products across Arizona and Gizeh. Same mindset — maximise price, low cost base means profitable even at discounts. If the segment grows, split by model.
**Lead time:** 6 months (already ordered for 2026)
**Cost:** £18.75–20.83 | **RRP:** £45–50 | **Margin at target prices:** ~45–50%

### Arizona EVA — Top 5

| GroupID | Colour | Start price | Drop to if slow | Floor |
|---------|--------|:-----------:|:---------------:|:-----:|
| 0129423-ARIZONA | Black Narrow | £45 | £39 | £35 |
| 1019094-ARIZONA | Khaki Green Regular | £45 | £40 | £36 |
| 0129443-ARIZONA | White Narrow | £42 | £38 | £35 |
| 0129421-ARIZONA | Black Regular | £45 | £40 | £36 |
| 1019152-ARIZONA | Khaki Green Narrow | £42 | £38 | £35 |

Pricing data per colourway is in the table above.

### Gizeh EVA

| GroupID | Style | Units (12m) | GP | Avg price | Cost | Stock |
|---------|-------|------------:|---:|----------:|-----:|------:|
| 0128201-GIZEH | EVA Black Regular | 35 | £627 | £36.67 | £18.75 | 1 |
| 0128221-GIZEH | EVA White Regular | 16 | £368 | £41.78 | £18.75 | 25 |

EVA Black is 100% peak season (Mar–Jun). EVA White sells year-round.

### Actions

- [x] Set Arizona EVA opening prices (done 3 Mar — all bumped up)
- [ ] Monitor weekly through Mar–Jun: are they moving at these prices?
- [ ] If slow by late April, drop to "drop to" column
- [ ] Gizeh EVA: check prices align with Arizona EVA strategy. Same cost base, same logic.
- [ ] Tail Arizona EVA colours (Gold, Rose Reptile, Eggshell, Popcorn): hold price as long as possible, then discount from July to clear
- [ ] Do NOT reorder tail Arizona EVA colours next year. Top 5 only for 2027.

---

## BLAZE: Lunar Blaze (Amazon only)

**Strategy:** Demand recovery — stock is full but sales have collapsed since May 2025 peak. The lever is Amazon listing health, pricing, and visibility, not restocking.
**Lead time:** 4 days (same supplier as Ives) — irrelevant right now, stock is fine
**Cost:** £12.99 | **Avg sell price:** ~£32-35 | **Channel:** Amazon only

### Trajectory

Peak was May 2025 (81 units). Apr 2026 = 9 units despite peak season starting. 2026 YTD running ~80% below 2025. This is a demand problem, not a supply one.

### 3 Colours (12m)

| GroupID | Colour | Notes |
|---------|--------|-------|
| JLH950-BLAZE-NAVY | Navy | Dominant in 2025, slowed sharply 2026 |
| JLH950-BLAZE-NUDE | Nude | Tail of seasonal demand |
| JLH950-BLAZE-BLACK | Black | Smallest, struggling |

### Actions

- [ ] **Investigate the listing:** buy box %, ranking, reviews, competition — what changed since May 2025?
- [ ] **Pricing test:** is £32-35 still right? Has a competitor undercut?
- [ ] **Don't reorder.** Stock is full. Sell through what you have.
- [ ] If demand doesn't recover by end of peak (Aug 2026), consider clearance pricing
- [ ] Treat as Amazon-only — no Shopify, no shop floor

---

## RIEKER-WIN: Rieker Winter (Amazon)

**Strategy:** Brand ownership — rotating range. Owner selects, sells, clears, and pre-orders.
**Lead time:** 2 weeks (in-season reorder) | 6 months (pre-order)
**Cost:** £28–37 | **Avg sell price:** £50–68 | **Margin:** ~49%
**Selling season:** Oct–Feb
**DB flag:** `segment = 'RIEKER-WIN'` — applied to all winter Rieker groupids

### How Rieker differs from other segments

Rieker rotates its catalogue each season. The groupids change year to year. This segment is defined by **brand ownership**, not fixed products. The owner manages whatever winter Rieker stock is current.

### Current Winter Styles (2025/26 season)

| GroupID | Style | Units (12m) | GP | Margin | Last sale |
|---------|-------|------------:|---:|-------:|-----------|
| L7514-14 | Fleece Zip Boots Navy | 84 | £2,875 | 50.0% | 28 Feb |
| 72581-14 | Fleece Lined Boots Blue | 52 | £1,675 | 51.7% | 29 Jan |
| 45973-00 | Elasticated Shoes Black | 38 | £1,197 | 50.5% | 26 Feb |
| 45973-36 | Elasticated Trainer Red | 42 | £1,093 | 46.0% | 15 Feb |
| 72581-54 | Ankle Boots Green | 16 | £428 | 47.1% | 12 Feb |
| 74260-25 | Lined Ankle Boots Brown | 13 | £405 | 47.5% | 31 Dec |
| 03354-26 | Extra Width Shoes Brown (Mens) | 12 | £251 | 42.0% | 21 Feb |
| Y0783-00 | Velvet Fur Boots Black | 10 | £226 | 44.0% | 28 Dec |
| 14621-00 | Elasticated Shoes Black (Mens) | 6 | £151 | 40.4% | 24 Jan |
| 14621-24 | Elasticated Shoes Brown (Mens) | 1 | £50 | 57.3% | 14 Jan |
| 48954-00 | Extra Wide Touch Shoes | 1 | £37 | 57.0% | 13 Dec |

**Total 12m GP: £7,700** from 11 styles. Top 4 = £6.2k (80%).

### Owner's Seasonal Cycle

1. **Sep:** Winter order arrives → add to system, tag `RIEKER-WIN`, price, send to FBA
2. **Oct–Feb:** Sell. Monitor reorder screen. Best sellers → reorder mid-season (2-week lead time). Introduce new styles if performing well.
3. **Mar:** Season ends. Clear remaining stock — drop prices monthly until gone. Pre-order next winter range from Rieker catalogue, using this season's sales data. (Pre-order timing was historically ~Jun but 2026/27 batch was placed in Mar 2026.)

### Actions (current — season ending)

- [ ] Clear remaining winter stock at reduced prices
- [x] 2026/27 winter pre-order placed Mar 2026 — arriving ~Aug
- [ ] On arrival: tag, price, send proven winners to FBA. Pick further FBA candidates as Amazon ranking signals appear through the season
- [ ] Amazon only. No Shopify.

---

## RIEKER-SUM: Rieker Summer

**Strategy:** Brand ownership — rotating range. Same model as RIEKER-WIN but for summer catalogue.
**Channels:** Amazon is the core channel. Shopify listed but won't move much Rieker. Physical shop: keep 1 pair of each winning style on display (sells at RRP), but send the bulk to FBA immediately — don't let shop stock hold back Amazon.
**Lead time:** 2 weeks (in-season reorder) | 6 months (pre-order)
**Cost:** £26–29 | **Avg sell price:** ~£53 | **Margin:** ~49%
**Selling season:** Mar–Sep
**DB flag:** `segment = 'RIEKER-SUM'` — applied to all summer Rieker groupids

### Current Summer Styles (tagged Mar 2026)

| GroupID | Colour | Cost | Stock | Sales | Channel |
|---------|--------|------|-------|-------|---------|
| 64870-14 | Blue | £27.95 | 15 | — | On FBA (not live yet) |
| 64870-81 | White | £27.95 | 12 | — | FBA (2 sizes live) |
| 65918-52 | Green | £25.90 | 15 | — | Not on Amazon yet |
| 659C7-16 | Blue | £27.95 | 14 | 1 unit | CM3 (physical shop) |
| M1655-14 | Blue | £28.80 | 9 | 2 units | 1 AMZ, 1 CM3 |
| M1655-54 | Green | £28.80 | 10 | 4 units | 4 AMZ |

Previous summer style (cleared): N42T0-14 — 17 units, £322 GP.

**Totals (as of Mar 2026):** 6 styles, 7 units sold, £368 revenue, £152 GP. Season just starting.

### Stock allocation rule (decided Mar 2026)

**Amazon first.** Last year Rieker stock sat in the shop doing nothing while Amazon could have shifted it. The shop sold some at RRP but held back the channel that actually moves volume. A couple of shop sales shouldn't change the plan.

- When stock arrives: keep **1 pair per winning style** in the shop (sells at RRP, £67 — good margin if it goes)
- Send **everything else straight to FBA** — don't wait
- Shopify price left to pricing engine — it won't sell much Rieker but no harm having it listed
- If a reorder comes in, same rule: 1 for the shop, rest to FBA

### Owner's Seasonal Cycle

1. **Mar:** Summer order arrives → add to system, tag `RIEKER-SUM`, price, send bulk to FBA (keep 1 per style for shop)
2. **Mar–Sep:** Sell. Monitor reorder screen. Best sellers → reorder mid-season (2-week lead time). Introduce new styles if performing well.
3. **Oct:** Season ends. Clear remaining stock — drop prices monthly until gone.
4. **~Dec:** Pre-order next summer range from Rieker catalogue, using this season's sales data.

### How to tag new arrivals

When new summer Rieker groupids appear in skusummary:

```sql
-- Find untagged Rieker
SELECT groupid, shopifytitle FROM public.skusummary
WHERE brand ILIKE 'Rieker' AND segment IS NULL;

-- Tag them
UPDATE public.skusummary SET segment = 'RIEKER-SUM'
WHERE brand ILIKE 'Rieker' AND segment IS NULL;
```

### Actions (current — season starting)

- [x] Tag all new groupids as `RIEKER-SUM` in database (done Mar 2026)
- [x] Repriced all 4 Amazon groupids to £55 (was £43-57) — profit marker price (Mar 2026)
- [ ] Send more stock to FBA from existing supply — no new buying until £55 price test proves out
- [ ] Get remaining styles live on FBA (64870-14, 65918-52, 659C7-16 need attention)
- [ ] Monitor sales at £55 — does buy box come and does velocity hold?
- **No reorders until profitability confirmed at £55.** Early sales were losing money at £43-48.

---

## MILANO: Birkenstock Milano (Shopify)

**Strategy:** Price optimisation. Only 4 styles, all proven winners. Keep in stock, maximise price.
**Lead time:** 6 months (stock already committed)
**Cost:** £37.50 | **RRP:** £90.00 | **Margin:** 49.1%

### All 4 Styles (every one is a winner)

| GroupID | Style | Units (12m) | Revenue | GP | Avg price | Last sale |
|---------|-------|------------:|--------:|---:|----------:|-----------|
| 0034701-MILANO | Dark Brown Regular | 63 | £4,859 | £2,497 | £77.13 | 21 Feb |
| 0034791-MILANO | Black Regular | 72 | £5,191 | £2,491 | £72.10 | 3 Mar |
| 0034703-MILANO | Dark Brown Narrow | 42 | £3,060 | £1,485 | £72.86 | 27 Oct |
| 0034793-MILANO | Black Narrow | 41 | £2,939 | £1,402 | £71.68 | 5 Feb |

**Total 12m GP: £7,875** from just 4 styles. £1,969 GP per style — highest in the Birkenstock range.

### Actions

- [ ] Check current Shopify prices against avg selling prices — room to push higher?
- [ ] Same approach as Arizona EVA: hold strong prices Mar–Jun, adjust if needed
- [ ] Dark Brown Regular sells at £77 avg vs £72 for Black — DB is the premium, price accordingly
- [ ] Keep all 4 in stock through summer. These sell year-round (last sales all recent)

---

## BEND: Birkenstock Bend (Shopify)

**Strategy:** High-value trainer segment. White and Black are the core. Other colours are secondary but still profitable.
**Lead time:** 6 months (stock already committed)
**Cost:** £52–56 | **RRP:** £125–135 | **Margin:** 44.5%

### All 8 Styles

| GroupID | Style | Units (12m) | Revenue | GP | Avg price | Last sale |
|---------|-------|------------:|--------:|---:|----------:|-----------|
| 1017723-BEND | White Regular | 64 | £6,891 | £3,291 | £107.68 | 24 Feb |
| 1017721-BEND | Black Regular | 63 | £5,799 | £2,255 | £92.11 | 26 Feb |
| 1017724-BEND | White Narrow | 32 | £3,099 | £1,299 | £96.86 | 10 Feb |
| 1019163-BEND | Sandcastle Regular | 23 | £2,178 | £980 | £94.70 | 13 Feb |
| 1019180-BEND | Midnight Blue Regular | 12 | £1,440 | £815 | £120.00 | 12 Dec |
| 1017722-BEND | Black Narrow | 11 | £1,138 | £519 | £103.45 | 28 Oct |
| 1019723-BEND | Midnight Blue Narrow | 5 | £443 | £183 | £88.67 | 20 Feb |
| 1019717-BEND | Sandcastle Narrow | 2 | £172 | £68 | £86.10 | 25 Feb |

**Total 12m GP: £9,411** from 8 styles.

### Key Insight

White Regular alone (£3.3k GP) outperforms most entire Birkenstock models. White + Black in Regular fit = £5.5k GP from 2 styles. Narrow fits and other colours add incremental GP but won't make or break the range.

### Actions

- [ ] White Regular is the star — never run out
- [ ] Black Regular is solid #2 — keep stocked
- [ ] Other colours profitable even with heavy discounting (high RRP gives headroom). No need to cut, but don't overcommit
- [ ] Highest price point in the range (~£90–120 sell price) — premium customers, less price-sensitive

---

## ARIZONA-BF-REG: Arizona Birko-Flor Regular (Shopify)

**Strategy:** Stock and price all Regular fits. Owner manages this in isolation.
**Lead time:** 6 months (stock already committed)
**Cost:** £35.42 | **RRP:** £80–85 | **Margin:** ~46%
### All Regular Styles

| GroupID | Colour | Units (12m) | Revenue | GP | Avg price | Last sale |
|---------|--------|------------:|--------:|---:|----------:|-----------|
| 0051701-ARIZONA | Dark Brown | 52 | £3,782 | £1,940 | £72.72 | 31 Dec |
| 0051751-ARIZONA | Blue | 63 | £4,106 | £1,875 | £65.18 | 28 Feb |
| 0051791-ARIZONA | Black | 58 | £3,810 | £1,756 | £65.70 | 5 Jan |
| 0552681-ARIZONA | White | 39 | £2,500 | £1,118 | £64.09 | 25 Jul |
| 1029470-ARIZONA | Graceful Taupe | 26 | £1,925 | £1,004 | £74.03 | 23 Feb |
| 1027720-ARIZONA | Stone Coin | 36 | £2,226 | £951 | £61.83 | 26 Nov |
| 1027721-ARIZONA | New Beige | 9 | £612 | £293 | £68.00 | 12 Jul |
| 1009920-ARIZONA | Pearl White | 7 | £515 | £267 | £73.60 | 28 Feb |
| 1019662-ARIZONA | Light Rose | 5 | £420 | £243 | £84.00 | 24 Dec |
| 1027346-ARIZONA | Eggshell | 7 | £455 | £207 | £65.00 | 19 Feb |

**Total: 10 styles, 302 units, £18,351 revenue, £8,654 GP**

### Actions

- [ ] Top 6 colours (Dark Brown → Stone Coin): keep fully stocked, optimise prices
- [ ] Bottom 4 (New Beige, Pearl White, Light Rose, Eggshell): sell what's there, don't restock unless they surprise
- [ ] Dark Brown sells at highest avg price (£72.72) — price accordingly
- [ ] White last sold Jul '25 — stock issue? Check and fix for spring.

---

## ARIZONA-BF-NAR: Arizona Birko-Flor Narrow (Shopify)

**Strategy:** Stock and price all Narrow fits. Owner manages this in isolation.
**Lead time:** 6 months (stock already committed)
**Cost:** £35.42 | **RRP:** £80–85 | **Margin:** ~46%
### All Narrow Styles

| GroupID | Colour | Units (12m) | Revenue | GP | Avg price | Last sale |
|---------|--------|------------:|--------:|---:|----------:|-----------|
| 0051703-ARIZONA | Dark Brown | 43 | £2,687 | £1,164 | £62.49 | 17 Feb |
| 0552683-ARIZONA | White | 28 | £1,828 | £836 | £65.29 | 28 Feb |
| 1029439-ARIZONA | Graceful Taupe | 17 | £1,190 | £588 | £70.00 | 21 Sep |
| 0051793-ARIZONA | Black | 18 | £1,186 | £549 | £65.92 | 3 Mar |
| 1027696-ARIZONA | Stone Coin | 15 | £997 | £466 | £66.45 | 14 Nov |
| 1009921-ARIZONA | Pearl White | 12 | £846 | £421 | £70.50 | 3 Sep |
| 1025046-ARIZONA | Pecan (Vegan) | 10 | £756 | £402 | £75.62 | 10 Aug |
| 1019635-ARIZONA | Light Rose | 5 | £404 | £226 | £80.70 | 21 Nov |
| 1027339-ARIZONA | Eggshell | 7 | £455 | £207 | £65.00 | 22 Oct |
| 1029224-ARIZONA | Metallic Black | 4 | £300 | £158 | £74.88 | 2 Nov |

**Total: 10 styles, 159 units, £7,962 revenue, £3,567 GP**

### Why This Works for a Junior

- Low cost of mistakes — £35.42 per unit, worst case is a slow seller at £50 that still makes money
- Same decisions as any segment: what's selling, what needs a price change, what to reorder
- Clear data to work from — if a colour isn't selling, don't reorder. Simple.
- Blue Narrow (`0051753-ARIZONA`) exists but has zero sales — a test for the owner to investigate

### Actions

- [ ] Top 5 (Dark Brown → Stone Coin): stock and monitor
- [ ] Bottom 5: sell through, reorder only if selling
- [ ] Blue Narrow has no sales — seed with light stock to test? Owner's call.
- [ ] Good training segment: learn stock management and pricing with low risk

---

## GIZEH: Birkenstock Gizeh Regular (Shopify)

**Strategy:** Regular fit only. Price optimisation, keep top sellers stocked through summer.
**Lead time:** 6 months (stock already committed)
**Cost:** £35.42–37.50 | **RRP:** £85–90 | **Margin:** ~48%

### All 7 Styles

| GroupID | Style | Units (12m) | Revenue | GP | Avg price | Stock | Last sale |
|---------|-------|------------:|--------:|---:|----------:|------:|-----------|
| 1005299-GIZEH | Patent White | 46 | £3,388 | £1,663 | £73.65 | 30 | 28 Feb |
| 0745531-GIZEH | Birko-Flor White | 39 | £2,937 | £1,555 | £75.29 | 17 | 18 Oct |
| 0043691-GIZEH | Birko-Flor Black | 42 | £2,866 | £1,378 | £68.23 | 12 | 22 Feb |
| 0043661-GIZEH | Patent Black | 28 | £2,005 | £955 | £71.60 | 18 | 24 Feb |
| 0143621-GIZEH | Birko-Flor Blue | 28 | £1,926 | £934 | £68.78 | 3 | 7 Dec |
| 1013075-GIZEH | Patent Sand Brown | 12 | £1,020 | £570 | £85.00 | 14 | 15 Nov |
| 1025062-GIZEH | Vegan Pecan Brown | 9 | £786 | £449 | £87.33 | 16 | 13 Dec |

**Total 12m GP: £5,918** from 7 styles. Top 3 = £4.6k (78%).

### Key Observations

- Two White Gizehs (Patent + Birko-Flor) both strong — different finishes, not cannibalising
- Patent Sand Brown and Vegan Pecan sell at full RRP (£85–87) — premium colours, low volume but high margin
- Birko-Flor Blue is very peak-heavy (26 of 28 units Mar–Jun) — stock it for spring, don't worry if it's quiet in winter
- Birko-Flor White sells nearly evenly across seasons (20 peak / 19 off) — keep stocked year-round

### Actions

- [ ] Check current Shopify prices vs avg selling prices — room to push Patent White and Birko-Flor White higher?
- [ ] Birko-Flor Blue only 3 stock — needs replenishing for spring peak
- [ ] Hold strong prices Mar–Jun, adjust if needed
- [ ] Patent Sand Brown and Vegan Pecan at full RRP — leave them, they sell at premium

---

## ZERMATT-SEG: Birkenstock Zermatt (Shopify)

**Strategy:** Winter slippers, two product lines (cork latex + shearling). Regular fit only. Price optimisation, keep winners stocked.
**Lead time:** 6 months
**Cost:** £25 (cork) / £37.50 (shearling) | **RRP:** £60 / £90 | **Margin:** ~44–47%
**Selling season:** Year-round — cork peaks Mar–Jun, shearling peaks Jul–Feb
**DB flag:** `segment = 'ZERMATT-SEG'`

### All 5 Styles

| GroupID | Style | Cost | Units (12m) | Revenue | GP | Avg price | Stock | Last sale |
|---------|-------|-----:|------------:|--------:|---:|----------:|------:|-----------|
| 1015080-ZERMATT | Light Grey Reg (cork) | £25 | 76 | £3,661 | £1,615 | £48 | 17 | 9 Mar |
| 1015092-ZERMATT | Light Grey Reg (shearling) | £37.50 | 33 | £2,492 | £1,155 | £75 | 15 | 9 Mar |
| 1014938-ZERMATT | Dark Anthracite Reg (cork) | £25 | 42 | £2,190 | £1,052 | £52 | 0 | Dec '25 |
| 1016570-ZERMATT | Mocha Brown Reg (shearling) | £37.50 | 18 | £1,377 | £647 | £76 | 1 | Dec '25 |
| 1015090-ZERMATT | Dark Anthracite Reg (shearling) | £37.50 | 15 | £1,173 | £563 | £78 | 3 | Feb '26 |

**Total 12m GP: £5,032** from 5 styles. All Regular fit.

### Key Pricing

- Cork styles sell at **£48** (66% of 1015080 sales at this price). Do not drop below £48.
- Shearling styles sell at **£70–75**. Higher cost base but strong margin.

### Stock Pipeline

- **1014938** (Dark Anthracite cork): 0 stock but 60 on order across 4 deliveries (Mar–Aug)
- **1015080** (Light Grey cork): 17 stock + 6 on order (Feb). Ordering more for Sep delivery — top seller needs depth
- **1015092** (Light Grey shearling): 15 stock + 40 on order (Jul–Aug)
- **1016570** (Mocha Brown shearling): 1 stock + 29 on order (Aug)
- **1015090** (Dark Anthracite shearling): 3 stock + 1 on order (Jul)

### What was dropped

Narrow fits, Navy (high return rates), and low-volume shearling tail — all stay in CRAP. Only Regular fit in the segment.

### Actions

- [ ] Price 1015080 back to £48 (was dropped to £40 in error)
- [ ] Order 1015080 cork for Sep delivery — fill sizes 37–41 as priority
- [ ] Monitor 1014938 restock (Mar delivery first) — was out of stock, strong seller
- [ ] Shearling order (Aug) is committed — sell through winter, assess in spring

---

## CRAP — Retired (May 2026)

CRAP was a clearance bucket for tail styles. As of May 2026 it has been retired: every groupid lives in a managed segment, regardless of winner/loser status. The rationale is in `CLAUDE_CONTEXT.md` (Segment Definition Principle — Category Boundary, Not Curated Shortlist): per-style action (defend / scale / clear / salvage) is carried by **state inside a segment**, not by in/out membership. Losers exit naturally by selling through and not being reordered.

If you find a `segment = 'CRAP'` filter in older queries it's now a no-op (no rows match) and can be removed.

---

## REMONTE-WIN: Remonte Winter (Amazon)

**Strategy:** Sister brand to Rieker. Same supplier, same 2-week lead time, same seasonal cycle. Manage alongside RIEKER-WIN.
**Lead time:** 2 weeks (in-season reorder) | 6 months (pre-order)
**Cost:** £34-38 | **Avg sell price:** £75-80 | **Margin:** ~49%
**Selling season:** Oct-Feb
**DB flag:** `segment = 'REMONTE-WIN'`

### Why this is a segment

£28 average profit per sale — the highest per-unit economics of any unsegmented product. Only needs ~180 units to hit £5k GP. Currently doing £972 GP from 35 net units with zero active management.

### Current Winter Styles (2025/26 season)

| GroupID | Style | Net Units | GP | Avg profit/sale | FBA Stock | Last sale |
|---------|-------|----------:|---:|----------------:|----------:|-----------|
| D0700-22 | Zip Shoes Brown | 12 | £310 | £28 | 7 | 23 Mar |
| D0772-15 | Zip Boots Blue | 10 | £288 | £29 | 0 | 12 Jan |
| R1402-16 | Zip Shoes Blue | 9 | £291 | £32 | 6 | 17 Feb |
| D0772-52 | Zip Up Boots Green | 4 | £83 | £21 | 0 | 16 Feb |

**Total season GP: £972** from 35 net units across 4 styles. 13 units remain at FBA. All Amazon.

### Owner's Seasonal Cycle

Same as RIEKER-WIN:
1. **Sep:** Winter order arrives — tag `REMONTE-WIN`, price, send to FBA
2. **Oct-Feb:** Sell. Monitor. Reorder winners (2-week lead time).
3. **Mar:** Clear remaining stock at reduced prices. Pre-order next winter range alongside Rieker. (2026/27 batch was placed in Mar 2026 — historically the timing varied.)

### Actions

- [x] Tag all 4 groupids as `REMONTE-WIN` in database
- [x] 2026/27 winter pre-order placed Mar 2026 — arriving ~Aug (alongside Rieker)
- [ ] 13 units remain at FBA (7x D0700-22, 6x R1402-16) — leave in place for next season
- [ ] On arrival: tag, price, send proven winners to FBA. Pick further FBA candidates as Amazon ranking signals appear through the season
- [ ] Target: £5k GP for winter 2026/27 season
- [ ] Amazon only. Same owner as RIEKER-WIN.

---

## Segments not detailed here

Active segments tracked in the DB but without a detailed section in this doc:

- **ARIZONA-PATENT-SEG** (4 groupids) — given its own segment Mar 2026 rather than absorbed into ARIZONA-BF-REG/NAR
- **FREE-SPIRIT** (3 groupids) — Amazon test, see `scale/SCALE_PLAN.md` §8
- **LAKE-SEG** (4 groupids) — winter slipper
- **MAYARI-SEG** (3 groupids)
- **UKD-SEG** (4 groupids) — see `ukd/README.md`

Add detailed playbooks here when active management warrants it.

## Brand pipeline

See `scale/SCALE_PLAN.md` §8 for current investigations, graduated segments, and ruled-out options. Don't duplicate here.

---

## Meeting Prep Query

Run this before any weekly or monthly meeting. Shows every segment's last 30 days vs the previous 30 days, with trend and current stock.

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

- **Trend +%** = GP growing vs previous 30 days. Good.
- **Trend -%** = GP dropping. Challenge the owner: stock out? Price too low? Competition?
- **NEW** = no sales in previous period, sales now. Segment just started.
- **IDLE** = no sales in either period. Stock not arrived? Or dead?
- **local_stock** = warehouse stock. **fba_stock** = live at Amazon FBA.
- Both at 0 with a dropping trend = about to run out. Act now.
- Amazon segments (IVES, BLAZE, RIEKER) — fba_stock is what matters. Local stock is what's waiting to be sent.
- Shopify segments (EVA-SEG, MILANO, BEND, etc.) — local_stock is what matters.

### Seasonal context

Expect Birkenstock segments (EVA-SEG, MILANO, BEND, ARIZONA-BF-REG, ARIZONA-BF-NAR, GIZEH) to surge Mar–Jun and drop Jul–Feb. Rieker Winter is the opposite. Compare like-for-like months for a fair read — don't panic about a -30% trend on RIEKER-WIN in March, that's expected.

---

## Weekly Routine (30 mins)

1. **Ives FBA stock check** — any sizes running low? Reorder. (5 mins)
2. **Blaze listing check** — buy box, price vs competitors, recent units sold. Demand-side, not stock. (5 mins)
3. **Birkenstock EVA Shopify check** — Arizona top 5 + Gizeh EVA: selling at current prices? Adjust if needed. (5 mins)
4. **Tail Arizona EVA** — selling? If not and it's past April, drop price. (5 mins)
5. **Rieker Summer FBA check** — monitor sell-through of new arrivals, reorder winners. (5 mins)
6. **Rieker Winter clearance** — anything left? Drop price. (2 mins)
7. **Birkenstock Shopify check** — Milano, Bend, Arizona BF Regular/Narrow: stock levels and pricing. (5 mins)
