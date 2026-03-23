# Shopify Performance Tracking

## How to measure
- Export the Shopify sold report CSV (same format as `Shopify-Sold-Export.csv`)
- The `profit` column is after ALL expenses (aggressive allocation)
- Give the CSV to Claude and ask to compare against baseline

## Baseline: 22 Feb – 23 Mar 2026 (30 days)

| Metric | Value |
|--------|-------|
| Units sold | 248 |
| Revenue | £13,293 |
| Operating profit | £1,573 |
| Overall margin | 11.8% |
| Avg selling price | £53.60 |
| Avg profit/unit | £6.34 |

### By brand
| Brand | Units | Revenue | Profit | Margin |
|-------|-------|---------|--------|--------|
| Birkenstock | 200 | £11,655 | £1,432 | 12.3% |
| Lunar | 36 | £1,077 | £124 | 11.5% |

### Profit bands
| Band | Units | % | Profit |
|------|-------|---|--------|
| Loss makers (<£0) | 34 | 14% | -£179 |
| Low profit (£0-5) | 75 | 30% | £240 |
| Mid profit (£5-15) | 119 | 48% | £1,190 |
| High profit (£15+) | 18 | 7% | £322 |

### Context
- Business made a £48k loss in the prior year
- This 30-day snapshot represents the turnaround to profitability
- 34 loss-making units are clearance stock being wound down
- Without clearance losses, margin on profitable lines is ~15%
- Google Ads running at 10x ROAS
- Birkenstock is 81% of volume and the profit engine
- Expect ROAS to drop towards 5x as ad spend scales — still profitable above ~3x at current margins
