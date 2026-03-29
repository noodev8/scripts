# Shopify Price Review — Plan

## Goal

Use our own sales data to identify Shopify pricing opportunities:
1. **Underpriced** — selling well, could tolerate a price increase
2. **Overpriced / stale** — not selling, price may need to come down to move stock

**Current stage: Human-in-the-loop.** All decisions are made by the user after reviewing the analysis and drill-downs. Claude presents data and recommendations, the user decides.

---

## Data Sources

All from PostgreSQL:

| Table | What we use |
|---|---|
| `sales` | Last 30 days: groupid, soldprice, qty, solddate, profit, discount, channel |
| `skusummary` | Current shopifyprice, cost, rrp, tax, season, min/maxshopifyprice, ignore_auto_price |
| `localstock` | Current stock by groupid (SUM qty WHERE deleted=0) |
| `price_change_log` | Recent price changes: old_price, new_price, change_date, reason_code |

---

## Cost Constants

These are flat-rate assumptions used in net profit calculations. Adjust here as costs change.

| Constant | Value | Notes |
|---|---|---|
| **Payment fee** | £0.30 + 2.9% of sold price | Shopify Payments standard rate. Formula: `0.30 + (0.029 * soldprice)` |
| **VAT** | soldprice / 6 | Only when `skusummary.tax = 1`. Equivalent to removing 20% VAT from gross price |
| **Wages / packing** | £1.00 per unit | Deliberately rounded up to give confidence in profit figures |
| **Postage (Royal Mail)** | £3.44 per unit | Average across ~527 items from Royal Mail invoices (see `Profit_Checker.xlsx`) |

### Net Profit Formula (per unit)

```
vat         = soldprice / 6              -- only if tax = 1, else 0
payment_fee = 0.30 + (0.029 * soldprice)
wages       = 1.00
postage     = 3.44
net_profit  = soldprice - vat - cost - payment_fee - wages - postage
```

---

## Phase 1 — Sales Analysis (read-only)

Pull 30-day Shopify sales aggregated to groupid level.

Output: `sales_analysis_30d.csv`, one row per groupid, sorted by units sold desc.

### Columns

| Column | Source | Description |
|---|---|---|
| groupid | sales | Product group identifier |
| brand | skusummary | Brand name |
| units_sold | sales | Total qty sold in period |
| revenue | sales | SUM(soldprice * qty) |
| avg_sold_price | sales | Weighted average price actually paid |
| distinct_orders | sales | Number of separate orders |
| net_profit_total | calculated | Total net profit after all costs (see Cost Constants) |
| net_profit_per_unit | calculated | Net profit per unit sold |
| current_price | skusummary.shopifyprice | Current Shopify price |
| cost | skusummary | Product cost |
| rrp | skusummary | Recommended retail price |
| season | skusummary | Winter/Summer/Any |
| stock | localstock | Current stock (SUM qty WHERE deleted=0) |
| margin_pct | calculated | Gross margin % at current price (VAT-adjusted) |
| net_profit_at_current | calculated | Net profit per unit if sold today at current price |
| incoming | birktracker | Incoming stock (SUM requested - arrived WHERE arrived=0), with due months |
| last_change_date | price_change_log | Date of most recent Shopify price change |
| last_old_price | price_change_log | Price before last change |
| last_new_price | price_change_log | Price after last change |
| last_notes | price_change_log | Reason notes from last change |
| changes_90d | price_change_log | Number of price changes in last 90 days |

### Summary Format

When presenting the analysis, always include these sections in this order:

#### 1. Overview
Table with: products sold, total units, revenue, net profit, avg net profit/unit, loss-making count and total.

#### 2. Top 5 Profit Earners
Sorted by net_profit_total DESC. Show: product, units, net profit, per unit, stock, headroom to RRP.

#### 3. Loss Makers
All products where net_profit_per_unit < 0, sorted by net_profit_total ASC (worst first). Show: product, units, net loss, per unit, stock, cost, price, last_notes.

#### 4. Price Increase Candidates (shown in summary)
Filter: units_sold >= 3, stock > 0, headroom_to_rrp > £15. Sorted by headroom DESC. Show: product, sold, price, RRP, net/unit, stock, incoming, days (days since last price change, number only), last_notes.

After presenting the summary, suggest: *"Want me to filter the increase candidates to 14+ days since last change?"*

#### 5. Price Increase Candidates — Filtered (on request)
Same as section 4 but with additional filter: days since last price change >= 14. This removes recently touched products and focuses on ones with enough data since the last move.

#### 6. Product Drill-Down (conversational, per product)

When the user picks a product from the candidates list, run this standard analysis:

**Step 1 — Full sales history + stock quality check**
Query ALL sales for the product (not just last 30 days). Also pull price_change_log for the full timeline.

**Stock quality check (always run during drill-down):**
Total stock can be misleading — 50 units means nothing if they're all size 36 and 47. Check stock vs sales by size:
```sql
-- Stock by size
SELECT code, SUM(qty) AS stock
FROM localstock
WHERE groupid = '{groupid}' AND deleted = 0 AND qty > 0
GROUP BY code ORDER BY code;

-- Which sizes actually sell (last 365 days)
SELECT REGEXP_REPLACE(code, '.*-', '') AS size, SUM(qty) AS units_sold
FROM sales
WHERE groupid = '{groupid}' AND channel = 'SHP' AND qty > 0
  AND solddate >= CURRENT_DATE - 365
GROUP BY REGEXP_REPLACE(code, '.*-', '')
ORDER BY units_sold DESC;
```

**Sellable stock** = stock in sizes that have sold at least 1 unit in the past year. Report both numbers:
- Total stock: X (all sizes)
- Sellable stock: Y (in sizes with proven demand)

If sellable stock is significantly lower than total stock, the product's real position is weaker than the headline number suggests. Decisions should be based on sellable stock, not total.

**Step 2 — Velocity by price point**
Group sales by the price they sold at (excluding returns, qty < 0). Present as a table:

| Price | Period | Net sales | Duration | Per week | Season |
|---|---|---|---|---|---|
| £XX | Mon–Mon YYYY | N | N weeks | N.N | Spring/Summer/etc |

This is the key table — it shows the proven sweet spot for each product.

**Step 3 — Compare recent velocity**
Zoom in on the last change specifically:
- Units per week at the old price vs units per week at the new price
- Did the price change affect the rate of sale, or is it roughly the same?

**Step 4 — Present the finding**
Use the velocity-by-price table to identify the sweet spot, then factor in:
- **Seasonality**: same product may sell differently in March vs July at the same price. Compare like-for-like seasons from last year where possible.
- **Incoming stock**: high incoming = core line, optimise for sustained volume at good margin. Zero incoming = clearance, different strategy.
- **Price jumps**: don't recommend jumps of more than ~£5 in one go. Step up gradually and revisit. The data from last year shows the trajectory — follow it.

Decision logic:
- If velocity is similar at both prices → the price isn't driving the sale. Recommend the higher price.
- If velocity dropped after an increase → the increase hurt. Consider reverting or meeting halfway.
- If velocity increased after a decrease → the drop worked. Hold or test a small increase to find the ceiling.
- If there's a clear sweet spot from last year's data → recommend that price.

**Step 5 — Action**
Present the recommendation with a specific price. Wait for the user's response:
- If they confirm ("yes", "do it", "go ahead", etc.) → **queue the change, don't apply yet**:
  1. Add to a pending changes list (groupid, new_price, notes)
  2. Mark the candidates table with `*` next to the line number
  3. Re-display the table and move to the next product
- If they disagree or want a different price → adjust and present again
- If they want to skip → move on, no mark on the table

**Step 6 — Batch Apply**
When the user is done reviewing ("apply", "done", "that's all", etc.):
1. Show the full list of pending changes for a final check
2. On confirmation, create a single nudge CSV with all changes
3. Run `google_price_apply.py` with `--confirm` to apply all at once
4. Delete the nudge CSV after successful apply
5. Show confirmation of what was applied

### SQL

```sql
WITH sales_30d AS (
    SELECT
        s.groupid,
        SUM(s.qty) AS units_sold,
        ROUND(SUM(s.soldprice * s.qty), 2) AS revenue,
        ROUND(SUM(s.soldprice * s.qty) / NULLIF(SUM(s.qty), 0), 2) AS avg_sold_price,
        COUNT(DISTINCT s.ordernum) AS distinct_orders,
        -- Net profit using cost constants (see Cost Constants section above)
        ROUND(SUM(
            s.qty * (
                s.soldprice
                - CASE WHEN sk2.tax = 1 THEN s.soldprice / 6.0 ELSE 0 END   -- VAT
                - sk2.cost::numeric                                           -- product cost
                - (0.30 + 0.029 * s.soldprice)                               -- payment fee
                - 1.00                                                        -- wages/packing
                - 3.44                                                        -- postage
            )
        ), 2) AS net_profit_total,
        ROUND(SUM(
            s.qty * (
                s.soldprice
                - CASE WHEN sk2.tax = 1 THEN s.soldprice / 6.0 ELSE 0 END
                - sk2.cost::numeric
                - (0.30 + 0.029 * s.soldprice)
                - 1.00
                - 3.44
            )
        ) / NULLIF(SUM(s.qty), 0), 2) AS net_profit_per_unit
    FROM sales s
    JOIN skusummary sk2 ON sk2.groupid = s.groupid
    WHERE s.channel = 'SHP'
      AND s.solddate >= CURRENT_DATE - 30
      AND s.qty > 0
    GROUP BY s.groupid
),
stock AS (
    SELECT groupid, SUM(qty) AS stock_qty
    FROM localstock
    WHERE deleted = 0
    GROUP BY groupid
),
last_change AS (
    SELECT DISTINCT ON (groupid)
        groupid,
        old_price AS last_old_price,
        new_price AS last_new_price,
        change_date AS last_change_date,
        reason_notes AS last_notes
    FROM price_change_log
    WHERE channel = 'SHP'
    ORDER BY groupid, change_date DESC, id DESC
),
change_count AS (
    SELECT groupid, COUNT(*) AS changes_90d
    FROM price_change_log
    WHERE channel = 'SHP'
      AND change_date >= CURRENT_DATE - 90
    GROUP BY groupid
),
incoming AS (
    -- birktracker: code = groupid-size, aggregate to groupid level
    -- incoming = requested where arrived = 0 (not yet received)
    SELECT
        REGEXP_REPLACE(code, '-[0-9]+$', '') AS groupid,
        SUM(requested) AS incoming_qty
    FROM birktracker
    WHERE arrived = 0 AND requested > 0
    GROUP BY REGEXP_REPLACE(code, '-[0-9]+$', '')
)
SELECT
    sa.groupid,
    sk.brand,
    sa.units_sold,
    sa.revenue,
    sa.avg_sold_price,
    sa.distinct_orders,
    sa.net_profit_total,
    sa.net_profit_per_unit,
    ROUND(sk.shopifyprice::numeric, 2) AS current_price,
    ROUND(sk.cost::numeric, 2) AS cost,
    ROUND(sk.rrp::numeric, 2) AS rrp,
    sk.season,
    COALESCE(st.stock_qty, 0) AS stock,
    COALESCE(inc.incoming_qty, 0) AS incoming,
    ROUND(
        CASE WHEN sk.tax = 1
            THEN (sk.shopifyprice::numeric / 1.2 - sk.cost::numeric)
                 / NULLIF(sk.shopifyprice::numeric / 1.2, 0) * 100
            ELSE (sk.shopifyprice::numeric - sk.cost::numeric)
                 / NULLIF(sk.shopifyprice::numeric, 0) * 100
        END, 1
    ) AS margin_pct,
    -- Net profit at CURRENT shopifyprice (what we'd make per unit if sold today)
    ROUND(
        sk.shopifyprice::numeric
        - CASE WHEN sk.tax = 1 THEN sk.shopifyprice::numeric / 6.0 ELSE 0 END
        - sk.cost::numeric
        - (0.30 + 0.029 * sk.shopifyprice::numeric)
        - 1.00
        - 3.44
    , 2) AS net_profit_at_current,
    lc.last_change_date,
    lc.last_old_price,
    lc.last_new_price,
    lc.last_notes,
    COALESCE(cc.changes_90d, 0) AS changes_90d
FROM sales_30d sa
JOIN skusummary sk ON sk.groupid = sa.groupid
LEFT JOIN stock st ON st.groupid = sa.groupid
LEFT JOIN incoming inc ON inc.groupid = sa.groupid
LEFT JOIN last_change lc ON lc.groupid = sa.groupid
LEFT JOIN change_count cc ON cc.groupid = sa.groupid
WHERE sk.ignore_auto_price IS DISTINCT FROM 1
ORDER BY sa.units_sold DESC;
```

**Note:** `sales.profit` column is not populated — net profit is calculated using the cost constants documented above. `tax` column removed (nearly all products are tax=1). `discount_pct` removed (all zeros in current data). `last_reason` (reason_code) replaced with `last_notes` (reason_notes) for more useful context.

---

## Phase 2 — Flag Opportunities

### 2a. Potentially Underpriced (candidates for increase)

Signals:
- Selling consistently (e.g. 3+ units in 30 days)
- Avg sold price is at or very close to shopifyprice (not discount-driven)
- Current price is well below RRP (headroom exists)
- Good stock levels (not about to run out)
- No recent price increase (avoid yo-yo pricing)
- Margin is already healthy but could be better

### 2b. Potentially Overpriced (candidates for decrease)

Signals:
- Low or zero sales despite having stock
- Price is above RRP or significantly above competitors (if benchmark data available)
- Stock is aging / seasonal risk
- Recent price increase that killed velocity
- High margin but no volume to show for it

### Output

Add columns to the Phase 1 report:
- `flag`: `increase` / `decrease` / `review` / `none`
- `flag_reason`: short text explaining why
- `suggested_price`: initial suggestion (guardrail-checked)
- `headroom_to_rrp`: gap between current price and RRP
- `margin_at_suggested`: what margin would look like at the suggested price

---

## Phase 3 — Human Review

- Export as CSV (same pattern as google_price process)
- Manual review: set `change=1` to accept, `change=0` to skip
- Add notes in description column
- Apply via `google_price_apply.py` (already handles guardrails and logging)

---

## Guardrails (same as existing)

- Never below cost + 10% margin
- Respect minshopifyprice / maxshopifyprice
- Respect RRP ceiling
- Skip ignore_auto_price = 1
- All changes logged to price_change_log
- **Max 3-4 price increases per batch.** Google Shopping (target ROAS) re-enters a learning phase after price increases — conversion rates dip for 1-3 days while the algorithm recalibrates bids to hit the ROAS target at the new prices. Confirmed 2026-03-23: batch of increases on Monday caused a noticeable Tuesday dip, recovery started Wednesday. Price *decreases* don't have this problem — Google rewards the higher conversion rate immediately. Wait for the campaign to stabilise before the next batch of increases.

---

## Roadmap

### Current: Human-in-the-loop (active)
- Run the analysis weekly/monthly
- Review summary, drill into candidates, make decisions
- Track progress via `analysis_log.md` — watch volume and net profit trend over time
- Build confidence that the velocity-by-price approach produces good decisions

### Future: Automation (NOT READY)
The long-term goal is for Claude to execute the full cycle autonomously — run the analysis, apply the drill-down logic, and make the price changes without human review. This is only viable once:
- [ ] We have several weeks/months of tracked results showing the process consistently improves profit
- [ ] The decision logic is proven — user is agreeing with recommendations the vast majority of the time
- [ ] Edge cases are understood (clearance vs core lines, seasonal transitions, new products)
- [ ] Guardrails are robust enough to prevent costly mistakes (max single change, min days between changes, etc.)

**Do not automate until explicitly approved.** The cost of a bad automated price change across many products is much higher than the cost of a manual review session.

---

## Relationship to Existing Tools

This is **complementary** to the Google price process:
- Google process uses **two reports**: the benchmark report (what competitors charge) and the performance/sale price suggestions report (Google's view on what prices drive the most sales)
- This process uses internal sales data (what's actually selling and at what margin)
- Both feed into the same apply pipeline and price_change_log
- Over time, could merge signals from both into a single review report
