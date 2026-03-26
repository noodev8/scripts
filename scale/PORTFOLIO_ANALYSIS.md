# Portfolio Analysis — Reducing Ives Dependency

**Created:** 2026-03-06
**Context:** Ives is 60% of profit. Goal is to build a diversified portfolio of £5-10k GP contributors, not hunt for the next unicorn.

---

## The Problem

| | Revenue (12m) | Profit (12m) | Share of profit |
|---|---:|---:|---:|
| **Ives (all colours)** | £146,060 | £59,499 | **59.7%** |
| **Everything else** | £217,973 | £40,170 | 40.3% |
| **Total** | £364,033 | £99,669 | 100% |

One product line, one supplier, one brand = 60% of profit. The goal isn't to replace Ives — it's to grow the "everything else" so that Ives becomes 40% or less of profit, ideally under 35%.

**To get Ives to 40% of profit:** Total profit needs to reach ~£149k. That means finding ~£50k more GP from other segments. At £5-10k per segment, that's 5-10 new or expanded bricks.

---

## Current Segment Portfolio (12m GP)

| Segment | GP (12m) | Status |
|---------|-------:|--------|
| IVES-WHITE | £39k | Mature — near ceiling |
| IVES (colours) | £54k | Mature — near ceiling |
| BEND | £9.4k | Active — in target range |
| AZ-BF-REG | £8.7k | Active — in target range |
| MILANO | £7.9k | Active — in target range |
| RIEKER-WIN | £7.7k | Active — seasonal, winter |
| BIRK-EVA | £7.3k | Active — seasonal, summer |
| BLAZE | £7.0k | Active — needs restock |
| GIZEH | £5.9k | Active — in target range |
| AZ-BF-NAR | £3.6k | Below threshold — training segment |
| RIEKER-SUM | TBD | Placeholder — stock arriving |

**6 segments in the £5-10k range.** That's the sweet spot. The question: what else can join them?

---

## What's Unsegmented — The Data

Scanned all unsegmented groupids with sales in the last 12 months. Grouped by natural clusters:

| Potential segment | Styles | Units (12m) | Revenue | GP | Avg profit/sale | Channel |
|-------------------|-------:|------------:|--------:|---:|----------------:|---------|
| **REMONTE (winter)** | 4 | 39 | £3,049 | £1,104 | **£28.31** | Amazon |
| **Lunar Lake (winter slipper)** | 4 | 34 (AMZ) | £1,280 | £472 | £13.86 | Amazon |
| **Hotter Shake II** | 1 | 77 | £4,190 | £697 | £9.05 | Amazon |
| **Goor (formal shoes)** | 7 | 222 | £6,820 | £1,889 | £8.51 | Shopify |
| **Madrid BF** | ~5 useful | ~95 | £5,756 | £1,214 | ~£14 | Shopify |
| **Madrid EVA** | 4 | 91 | £2,892 | £588 | ~£6.50 | Shopify |
| **Arizona Patent** | 4 | 97 | £6,379 | £1,072 | ~£11 | Shopify |
| **Arizona Vegan** | 1 | 33 | £2,079 | £487 | £14.76 | Shopify |

**Honest assessment: None of these are at £5-10k GP today.** But some have clear paths to get there.

---

## Verdict on Each

### 1. REMONTE-WIN — PROMOTE to segment (High confidence)

**Current:** £1,104 GP from 4 styles, 39 units, Amazon only.
**Why it's exciting:** £28.31 average profit per sale — the highest of anything unsegmented. Only needs 180-350 units to hit £5-10k GP. Remonte is Rieker's sister brand (same parent company, same distributor, same 2-week lead time). You already know how to run this playbook from RIEKER-WIN.

| GroupID | Style | Units | GP | Avg profit/sale |
|---------|-------|------:|---:|----------------:|
| D0700-22 | Zip Boots Brown | 12 | £344 | £28.65 |
| D0772-15 | Ankle Boots Brown | 11 | £309 | £28.13 |
| R1402-16 | Ankle Boots Blue | 10 | £291 | £29.11 |
| D0772-52 | Ankle Boots Rose | 6 | £160 | £26.62 |

**Path to £5k GP:** This did £1.1k with zero active management and minimal stock. If managed like RIEKER-WIN (proper range selection, FBA stocking, mid-season reorder), £5k is very achievable next winter. Same seasonal cycle, same owner, same supplier.

**Action:** Fold into RIEKER-WIN owner's responsibility, or create REMONTE-WIN as a separate segment. Tag groupids in DB now.

---

### 2. RIEKER-SUM — Already a placeholder, fill it (High confidence)

**Current:** Stock arriving imminently. No sales data yet.
**Why it's exciting:** If RIEKER-WIN does £7.7k GP in a 5-month winter window, RIEKER-SUM should do similar or better in a longer summer window. Same economics (£28-31 cost, ~49% margin, 2-week reorder).

**Path to £5k GP:** Active management from day one. Tag, price, send to FBA, monitor weekly, reorder winners.

**Action:** Already documented in CORE_ACTIONS. Execute the plan.

---

### 3. Hotter Shake II — WATCH, not segment (Low confidence)

**Current:** 77 units, £697 GP, Amazon. One style.
**Why not a segment:** It's a single product. You can't build a delegatable segment around one SKU. The profit per sale (£9.05) is average. And Hotter as a brand — do they have more styles that would work? Unknown.

**What to do:** Keep selling it. Monitor. If you discover 3-4 more Hotter styles that work on Amazon, revisit. But don't build a segment around a single shoe.

---

### 4. Goor (formal shoes) — WATCH, probably CRAP (Low confidence)

**Current:** 7 styles, 222 units, £1,889 GP, Shopify only.
**The problem:** B710AP (the best one) hasn't sold since Nov 2025. These are budget formal shoes (£27-35 sell price) on Shopify — a completely different customer to your core. Low margin per unit. Shopify channel means fees eat into the already thin margins.

**What to do:** Let them sell passively. Don't invest time managing them. If B710AP comes back to life, reconsider. Not segment material.

---

### 5. Madrid BF — ABSORB into existing structure (Medium confidence)

**Current:** 2 decent styles (Black Regular £450 GP, White Regular £425 GP), rest is tail.
**The problem:** It's Shopify Birkenstock, so the off-season zero margin finding applies. 14 styles but only 2-3 are meaningful. Total GP of £1.2k isn't enough for a segment.

**What to do:** The top 2-3 Madrid BF styles should be priced and stocked like any Birkenstock segment during Mar-Jun. But they don't warrant their own segment. Consider whether they belong in a broader "Birkenstock Other" bucket or just stay unsegmented but actively priced.

---

### 6. Madrid EVA — ABSORB into BIRK-EVA (Medium confidence)

**Current:** 4 styles, £588 GP.
**What to do:** Add the 2 best Madrid EVA styles to the BIRK-EVA segment. Same cost base (£16.67), same pricing logic. Adds incremental GP to an existing brick without creating a new one.

| GroupID | Style | Units | GP |
|---------|-------|------:|---:|
| 0128183-MADRID | EVA Black Narrow | 32 | £258 |
| 0128163-MADRID | EVA White Narrow | 29 | £213 |

---

### 7. Arizona Patent — ABSORB into AZ-BF segments (Medium confidence)

**Current:** 4 styles, 97 units, £1,072 GP.
**What to do:** These are the same cost base (£37.50) as BF Arizona. The top 2 (Patent White 1005291 at £380 GP, Patent Sand 1005294 at £360 GP) should be folded into AZ-BF-REG or AZ-BF-NAR depending on width. Boosts those segments by ~£700+ each.

---

### 8. Lunar Lake — INVESTIGATE for next winter (Low-medium confidence)

**Current:** 4 colours, winter slipper, £472 GP on Amazon.
**Why interesting:** Same supplier dynamics as Ives (Lunar, 4-day lead time). Winter product — fills a seasonal gap. Low cost (£17.50).
**Why cautious:** Lunar winter books were a total failure. Slippers are different, but the winter Lunar track record is bad.

**What to do:** Don't build a segment. But keep selling on Amazon and track through next winter. If it grows to £1k+ GP with proper FBA stocking, promote.

---

## The Realistic Portfolio Growth Plan

### Quick wins (absorb into existing segments — next 2 weeks)

| Action | Estimated GP uplift | Effort |
|--------|-------------------:|--------|
| Add Madrid EVA to BIRK-EVA | +£400-500 | Tag in DB, add to segment doc |
| Add Arizona Patent to AZ-BF-REG/NAR | +£700-1,000 | Tag in DB, add to segment doc |
| Tag Remonte winter styles | Setup | Tag in DB |

**Total uplift to existing segments: ~£1.1-1.5k GP**

### New segments to build (next 6 months)

| Segment | Target GP | When | Confidence |
|---------|----------:|------|:----------:|
| RIEKER-SUM | £5-8k | Summer 2026 | Medium — stock in place but slow start, summer Rieker historically weak |
| REMONTE-WIN | £3-5k (year 1), £5-8k (year 2) | Winter 2026/27 | High |
| FREE-SPIRIT | £2-5k (year 1) | Summer 2026 | Medium — first sales promising (£27 GP/unit), FBA stock landing. Amazon only. |

### What this does to Ives dependency

| Scenario | Total GP | Ives share |
|----------|----------|:----------:|
| **Today** | £99.7k | **59.7%** |
| **+Absorb +RIEKER-SUM +REMONTE-WIN** | ~£112-120k | **50-53%** |
| **+Full RIEKER-SUM maturity +Remonte +one new brand** | ~£125-135k | **44-48%** |

Getting Ives under 50% of profit is achievable by end of 2026. Under 40% needs the new brand pipeline to deliver. Free Spirit Frisco is the first new brand to show live sales (Mar 2026) — if it scales, it becomes a meaningful brick.

---

## The Portfolio vs Unicorn Principle

The numbers confirm the approach: **don't look for another Ives. Build reliable £5-10k contributors.**

- Ives took years and luck to become what it is
- Every existing segment that's properly managed is already in or near the £5-10k range
- The unsegmented products aren't hidden unicorns — they're incremental contributors that need to be absorbed or built into new segments
- The biggest untapped opportunity is Remonte (same playbook as Rieker, proven economics, zero active management today)
- RIEKER-SUM has stock in place but summer Rieker has historically been weak — confidence downgraded from High to Medium (Mar 2026). Free Spirit Frisco is showing early promise as an alternative summer brick.

**Rule of thumb for new brand evaluation:** Can it produce 3-5 styles doing £1-2k GP each on Amazon, with short lead times? That's the bar. Not "can it be the next Ives" but "can it be another reliable brick."

---

## Reference

- Segment details: `scale/CORE_ACTIONS.md`
- Master plan: `scale/SCALE_PLAN.md`
- Meeting rules: `scale/MEETING_RULES.md`
