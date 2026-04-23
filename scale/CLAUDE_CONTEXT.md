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
- 17 segments + CRAP. 0 NULL remaining (all groupids allocated as of Mar 2026)
- CRAP: 166 groupids — pricing engine clears stock, revisit periodically
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

DB tags (in `skusummary.segment`) must match sheet codes. Key mappings:
IVES-COLOUR, BEND-SEG, MILANO-SEG, BLAZE-SEG, GIZEH-SEG, BIRK-EVA-SEG, AZ-PATENT-SEG, AZ-BF-NAR-SEG, LAKE-SEG, ZERMATT-SEG

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
