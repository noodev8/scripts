# Scale Context — Read This First

This file exists so any Claude Code instance (any machine) has the full context for scale work. It is the single source of truth — do not duplicate this info elsewhere.

## What Is Scale Work?

Brookfield Comfort is scaling from ~£500k to £1M revenue. The approach: build **isolated, delegatable segments (lego bricks)** — each with its own groupids, pricing strategy, stock approach, and metrics.

## Key Files (in this folder)

- `SCALE_PLAN.md` — Master strategy, established facts, decision log, brand pipeline
- `CORE_ACTIONS.md` — All active segments with groupids, data tables, actions, weekly routine, meeting prep query
- `PORTFOLIO_ANALYSIS.md` — Ives dependency analysis, unsegmented product assessment, portfolio growth plan
- `MEETING_RULES.md` — 5 rules for segment meetings
- `KLAVIYO_EMAIL_PLAYBOOK.md` — Single campaign: 90-day Birkenstock repurchase
- `triage.sql` — Single query that scans all in-season segments and flags groupids by priority (YOY_DROP / CLEAR_RISK / OOS_RUNNING / HARVEST / COOLING). Run ad hoc when delegating, or to find what to look at next. **Mention this proactively to the user at the start of any scale session** — they want to be reminded it exists.
- `check_null_segment.sql` — Companion to triage.sql for the gap it doesn't cover: groupids with NULL segment, sorted fresh-arrival-down. Flags FRESH / ASSIGN / COLD / INCOMING / QUIET. Run during segment sessions to make sure new arrivals don't fall through. Default scope: Birkenstock; broaden the brand filter when needed. **Mention proactively at scale sessions alongside triage.sql.**

## Google Sheets Integration

- **Segment tracker sheet ID**: `1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0`
- Uses `gspread` library with service account file: `merchant-feed-api-462809-23c712978791.json` (in repo root)
- Sheets API enabled on **merchant-feed-api** Google Cloud project (Brookfield Comfort account)
- Sheet owned by Noodev8, shared with service account as Editor
- **Prefer updating Google Sheet over local CSV/MD** for segment tracking
- Tabs: **Segments** (main tracker), **Log** (task tracking between user and Claude)

### Quick access pattern
```python
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('merchant-feed-api-462809-23c712978791.json', scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_key('1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0')
```

## How We Work

- Pull DB data, identify winners vs tail, build segment with groupids
- User makes all strategic decisions — we present data and options
- Segments designed to be delegatable to staff
- Each session: check progress, refine existing segments, add new ones
- Minimum segment threshold: £5k revenue potential
- 25 segments, no CRAP, no NULL (verified against DB May 2026). Every groupid allocated to a managed segment.
- "Everything in a segment, even if rubbish" — losers exit naturally via sell-through, not by living in CRAP
- £500k→£1M needs new bricks (new brands, range expansions)
- **Don't auto-log** to the Log tab — it has a different purpose (task tracking between user and Claude)

## Strategy — Non-Negotiables

- **Portfolio, not catalogue** — scale winners, drop losers quickly. Not about listing everything.
- **Birkenstock cannot sell on Amazon** — all Birk segments are Shopify-only
- **Tested and rejected**: OnBuy, social media channels — none profitable for this market
- **Business identity**: "Search engine for branded products at quality prices" — not a brand like NEXT
- Customers find us by searching for specific branded products at good prices (Google Shopping, SEO)
- **Growth comes from**: more winning styles (not more styles), new Amazon-friendly brands, stock depth on winners, pricing optimisation
- **Amazon segments**: Lunar (IVES, BLAZE), Rieker, Remonte only
- Top/tail discipline on every segment — find the winners, bin the rest
- Segment codes use `-SEG` suffix when not all items of that type are in the segment (e.g. BEND-SEG, GIZEH-SEG)

## Segment Naming in DB

DB tags (in `skusummary.segment`) must match sheet codes. Full list (25 segments, May 2026):

Birkenstock: ARIZONA-BF-NAR, ARIZONA-BF-REG, ARIZONA-PATENT-SEG, ARIZONA-LEATHER, GIZEH-SEG, MAYARI-SEG, MADRID-SEG, MILANO-SEG, BEND-SEG, ZERMATT-SEG, EVA-SEG, BIRK-OTHER (Florida/Pasadena/Uppsala oddballs)
Lunar: IVES-COLOUR, IVES-WHITE, BLAZE-SEG, LUNAR-GENERAL (everything non-Ives/non-Blaze)
Rieker / Remonte: RIEKER-WIN, RIEKER-SUM, REMONTE-WIN
Other brands: FREE-SPIRIT, LAKE-SEG, BLOCH-SEG, SKECHERS-SEG, STRIVE-SEG, UKD-SEG (low-cost supplier — Goor, Roamers, R21, Grafters, Scimitar, Cipriata)
Accessories: ACCESSORY (Birkenstock socks, Bloch bags)

## Segment Definition Principle — Category Boundary, Not Curated Shortlist

A segment is the **smallest container in which "what's going on?" can be answered without looking outside it**. If interpreting the segment requires the full-category view, the boundary is wrong.

- **In:** every groupid in the category, regardless of winner/loser status.
- **Out (CRAP):** only items not part of any category we manage.
- **Per-style action** (defend / scale / clear / salvage) is carried by state, not by membership. Don't use in/out as a winner/loser flag — losers exit naturally by selling through and not being reordered.
- **Why this matters:** curated-shortlist segments force constant re-litigation of the boundary as new arrivals come in, and you end up doing whole-category analysis anyway just to make the in/out call. Category-boundary segments stop that thrash.
- **Precondition before bulk-adding losers:** confirm `scale/segment_rules/` for that segment are reporting/advisory, not auto-driving price or ad spend on membership alone. If active, add the per-style state mechanism first.

Example: EVA-SEG holds all 29 EVA styles (Arizona + Gizeh + Barbados + Madrid), set 2026-05-10. Previously held only the 10 winners; the other 19 sat in CRAP and were re-evaluated every session.

## Database Query Patterns

### Standard segment analysis
1. Identify products: `title.shopifytitle ILIKE '%keyword%'` joined to `skusummary`
2. Sales performance: `sales` table — filter `qty > 0 AND soldprice > 0`, group by `groupid`
3. Seasonal split: `EXTRACT(MONTH FROM solddate) BETWEEN 3 AND 6` = Peak, else Off-season
4. GP calculation: `soldprice - cost` (cost is varchar in skusummary, cast with `NULLIF(ss.cost,'')::numeric`)
5. After-fees GP: `soldprice * 0.96 - cost` (~4% for Shopify fees + payment processing)
6. Current stock: `localstock` where `ordernum = '#FREE' AND deleted = 0`
7. FBA stock: `amzfeed` table, `amzlive` column (join on `amzfeed.code = skumap.code`)
8. Returns: `sales` where `qty < 0`

### List items in a segment
```sql
SELECT s.groupid, s.colour, s.width, s.cost, s.shopifyprice, s.rrp,
       COALESCE(st.qty, 0) AS stock
FROM skusummary s
LEFT JOIN (
    SELECT groupid, SUM(qty) AS qty
    FROM localstock
    GROUP BY groupid
) st ON st.groupid = s.groupid
WHERE s.segment = 'SEGMENT_CODE'
ORDER BY s.groupid;
```

### Key table relationships
- `sales.groupid` → `skusummary.groupid` → `title.groupid`
- `skumap.groupid` + `skumap.code` → `localstock.code`
- Channel codes: SHP = Shopify, AMZ = Amazon, CM3 = other marketplace

### Cost reference (common)
- Lunar Ives: £15.99
- Lunar Blaze: £12.99
- Arizona EVA: £20.83
- Birkenstock Birko-Flor (Arizona/Gizeh/Milano): £35.42–37.50
- Birkenstock Bend leather: £56.25
- Birkenstock Bend canvas: £52.08
- Rieker: £27.95–37.15

## Business Context

- Birkenstock: 6-month lead time. Orders already placed for current season.
- Lunar: 4-day lead time. Biggest advantage — react to demand, not forecast.
- Rieker: 2-week lead time. Low risk.
- Birkenstock off-season (Jul-Feb): structurally 0% margin EXCEPT Arizona EVA (low cost base).
- Shopify is effectively a Birkenstock shop. Non-Birk brands do ~£160/week combined on Shopify.
- Amazon is for Lunar, Rieker, Blaze. No Rieker on Shopify.

## Reorder Screen (PowerBuilder legacy)
- Only shows last 30 days of sales data
- Anything older than 30 days shows as "LAST SOLD: 365"
- If stock has been out, screen looks dead even when historical demand is strong
- Solution: restock at least 1 of each size to get data flowing, then use screen normally

## What's Still Queued
- New brand evaluation (Free Spirit Frisco, Waldlaufer, Rieker expansion)
