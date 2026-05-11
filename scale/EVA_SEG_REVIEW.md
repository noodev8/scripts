# EVA-SEG Review — Week of 2026-05-11

Working doc for the EVA-SEG improvement task. Pulled 2026-05-11.

## Headline (manager Summary template)

| Window | Units | Units/day | Avg price | Revenue | YoY units | YoY rev |
|---|---:|---:|---:|---:|---:|---:|
| Last 30 days | 58 | 1.93 | £35.62 | £2,066 | **-47%** | -47% |
| Last 14 days | 29 | 2.07 | £35.34 | £1,025 | **-69%** | -69% |

- **Pace:** 1.93/day × 150 (Birk peak window) ≈ £10.3k season. Last year's same rate would have done ~£18k. Tracking ~£7-8k short.
- **Price trend (14d vs 30d):** holding (-£0.28).
- **Internal acceleration:** 14d rate slightly above 30d rate (2.07 vs 1.93) — segment isn't cooling against itself. The YoY hole is widening because we're now lapping last year's strongest weeks.

### Latest owner note (2026-05-04, Andreas)

Pushed Arizona EVA prices back to start (Black Reg/Black Nar/Khaki Reg £45, White Nar/Khaki Nar £42). Google benchmarks already 10–31% below market — softer YoY driven by **stock breadth**, not price. Black Reg said to be missing sizes 35-40 with no forward orders; Khaki Green Reg only size 41 in stock until July refill.

## Where the volume sits (30d, top 6 = 41 of 58 units)

| Groupid | Colour | Width | u30 | YoY | Stock | Inbound | Note |
|---|---|---|---:|---:|---:|---:|---|
| 0128201-GIZEH | Black | Reg | 11 | -15% | 21 | 49 | OOS_RUNNING — 1 running size at 0 |
| 0129443-ARIZONA | White | Nar | 7 | -36% | 21 | 52 | |
| 1019152-ARIZONA | Green | Nar | 7 | +133% | 15 | 30 | But 14d only 1 — COOLING |
| 1019051-ARIZONA | Blue | Reg | 6 | -65% | 10 | 42 | |
| 1019094-ARIZONA | Green | Reg | 5 | +400% | 3 | 8 | But 14d=0 — COOLING |
| 1030447-ARIZONA | Taupe | Reg | 5 | no hist | 3 | 0 | HARVEST candidate |

Remaining 23 styles share 17 units between them.

## Triage flags (14 of 29 groupids)

### YOY_DROP (8) — 30d < 70% of YoY same window

| Groupid | Colour | Width | Stock | Inbound | u30 | u30_yoy | Notes |
|---|---|---|---:|---:|---:|---:|---|
| 0129421-ARIZONA | Black | Reg | 18 | 0 | 1 | 9 | **6/6 sizes in stock per DB — conflicts with owner note** |
| 0129423-ARIZONA | Black | Nar | 21 | 39 | 3 | 12 | |
| 0129443-ARIZONA | White | Nar | 21 | 52 | 7 | 11 | |
| 1019051-ARIZONA | Blue | Reg | 10 | 42 | 6 | 17 | |
| 1019142-ARIZONA | Blue | Nar | 1 | 30 | 0 | 11 | |
| 0128183-MADRID | White | Nar | 0 | **60** | 0 | 6 | Biggest single inbound bet |
| 1014614-ARIZONA | Pink | Nar | 0 | 0 | 0 | 9 | Sell-through-and-exit |
| 1028566-BARBADOS | Green | Reg | 1 | 0 | 0 | 5 | Sell-through-and-exit |

### HARVEST (3) — selling at <85% RRP, no inbound, OOS running sizes → lift price

| Groupid | Colour | Width | Price | RRP | Stock | u30 | oos_running |
|---|---|---|---:|---:|---:|---:|---:|
| 0129441-ARIZONA | White | Reg | £35.50 | £50 | 0 | 3 | 4 |
| 1027305-ARIZONA | White | Reg | £42.00 | £50 | 1 | 3 | 3 |
| 1030447-ARIZONA | Taupe | Reg | £42.00 | £50 | 3 | 5 | 3 |

May 4 note says prices were pushed back up on EVA — verify these three were included.

### OOS_RUNNING (1) — real momentum, a running size at 0

- 0128201-GIZEH Black Reg — 11/30d, 49 inbound

### COOLING (2) — 14d rate < 50% of 30d rate

- 1019094-ARIZONA Green Reg — 5 in 30d but 0 in 14d (stock 3, 1/6 sizes)
- 1019152-ARIZONA Green Nar — 7 in 30d but 1 in 14d (stock 15, 7/7 sizes — so not size collapse here)

## Inbound exposure

~427 units inbound across 13 groupids. Birk lead time is 6 months — already locked in. Largest:

| Groupid | Colour/Width | Inbound | u30 | u30_yoy |
|---|---|---:|---:|---:|
| 0128183-MADRID | White Nar | 60 | 0 | 6 |
| 0129443-ARIZONA | White Nar | 52 | 7 | 11 |
| 0128201-GIZEH | Black Reg | 49 | 11 | 13 |
| 0128163-MADRID | Black Nar | 46 | 0 | 4 |
| 1019051-ARIZONA | Blue Reg | 42 | 6 | 17 |
| 0129423-ARIZONA | Black Nar | 39 | 3 | 12 |
| 1019152-ARIZONA | Green Nar | 30 | 7 | 3 |
| 1019142-ARIZONA | Blue Nar | 30 | 0 | 11 |
| 1015399-BARBADOS | White Reg | 18 | 0 | 0 |
| 1022466-ARIZONA | Yellow Nar | 18 | 0 | 0 |
| 1015398-BARBADOS | Black Reg | 13 | 1 | 1 |
| 1019094-ARIZONA | Green Reg | 8 | 5 | 1 |
| 0128161-MADRID | Black Reg | 5 | 3 | 0 |

## Strategy lens (from scale/CLAUDE_CONTEXT.md)

- Segment is a **category boundary**, not a winners list — was de-CRAP'd 2026-05-10, all 29 styles now in. Don't propose moving losers out.
- **Per-style state** carries action (defend / scale / clear / salvage), not segment membership.
- **Improvement levers**: pricing, stock breadth on winners, sell-through on losers. No new SKUs — 6-month Birk lead time, already committed.
- **EVA is strategically valuable** — cost £20.83 means it holds margin even off-season, the only Birk family that does.

## Things to consider (your call — not a plan)

1. **Resolve the Black Reg 0129421 contradiction first.** Owner note says missing 35-40, DB says 6/6 sizes in stock with 18 units. -89% YoY with full coverage and no inbound is a different problem than missing sizes. Cheapest to check, blocks other decisions.
2. **Inbound landing plan.** For the 6 biggest inbounds, agree price-on-arrival now rather than reacting. Big asymmetric risk: ~£20.83 cost on locked-in units that could sit through autumn.
3. **HARVEST trio.** Verify whether the May 4 price push covered 0129441 / 1027305 / 1030447. If not, lift to RRP-anchored — almost no stock to lose, cheap elasticity test.
4. **Green Arizonas cooling.** 1019094 has only 1/6 sizes in stock (likely cause). 1019152 has 7/7 in stock — so its 14d=1 is a real demand drop, not a stock collapse. Different problems.
5. **The 5 zero-stock-zero-inbound zeros** (Pink Nar, Barbados White, Yellow Nar, Barbados Pink, Taupe Nar) — leave to exit naturally per strategy.

## How to measure (going forward)

- **Weekly**: the Summary report above. One screen.
- **On request**: `python scale/eva_seg_grid_pull.py` → writes per-groupid grid to "EVA-SEG Grid" tab of the segment tracker (cost, margin, stock, weeks-cover, size coverage, dead sizes).
- **Ad hoc**: `scale/triage.sql` for what needs attention; log to `segment_notes` table to preserve context between sessions.
- **Don't smuggle off-template numbers into Summary commentary** — if a comparison matters, add it as a column.
