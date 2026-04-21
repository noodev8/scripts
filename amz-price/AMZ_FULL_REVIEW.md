# Full IVES Review — Procedure

**Scope:** Amazon channel + IVES product family only. Rules and thresholds here are tuned to Amazon conversion sensitivity and IVES velocity patterns. **Other channels (Shopify, etc.) and other product families may need different rules — do not reuse this procedure outside Amazon/IVES without revisiting the thresholds.**

**Trigger:** user says **"full ives review"** (or close variant).

**Purpose:** single-session comprehensive pass across all 8 IVES segments. Replaces the segment-by-segment flow for weekly/biweekly reviews. Target: ~25 min for what previously took ~90 min.

**When NOT to use this:** single-colour deep dives, exploratory questions, investigations of a specific issue — use the normal conversational flow documented in `AMZ_PRICING.md`.

---

## Step 1 — Pull all data in one round of parallel queries

### A. Per-SKU state (all IVES)

```sql
WITH sales_7d AS (
    SELECT code, SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END)::int AS sold_7d
    FROM sales WHERE channel = 'AMZ' AND solddate >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY code
),
sales_14d AS (
    SELECT code,
           SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END)::int AS sold_14d,
           SUM(CASE WHEN qty < 0 THEN ABS(qty) ELSE 0 END)::int AS returns_14d,
           MAX(solddate) AS last_sold
    FROM sales WHERE channel = 'AMZ' AND solddate >= CURRENT_DATE - INTERVAL '14 days'
    GROUP BY code
),
last_change AS (
    SELECT DISTINCT ON (code)
        code, log_date, old_price, new_price,
        CASE WHEN new_price > old_price THEN 'creep'
             WHEN new_price < old_price THEN 'drop'
             ELSE 'flat' END AS last_direction
    FROM amz_price_log ORDER BY code, id DESC
),
sold_since_change AS (
    SELECT s.code, SUM(CASE WHEN s.qty > 0 THEN s.qty ELSE 0 END)::int AS sold_post
    FROM sales s JOIN last_change lc ON s.code = lc.code
    WHERE s.channel = 'AMZ' AND s.solddate > lc.log_date
    GROUP BY s.code
)
SELECT
    a.code, a.groupid, sk.segment, a.sku AS amz_sku,
    NULLIF(a.amzprice,'')::numeric AS current_price,
    COALESCE(a.amzlive,0) AS fba_live,
    COALESCE(a.amztotal,0) AS fba_total,
    GREATEST(COALESCE(a.amztotal,0) - COALESCE(a.amzlive,0), 0) AS fba_inbound,
    COALESCE(s7.sold_7d,0) AS sold_7d,
    COALESCE(s14.sold_14d,0) AS sold_14d,
    COALESCE(s14.returns_14d,0) AS returns_14d,
    CASE WHEN COALESCE(s14.sold_14d,0) > 0
         THEN ROUND(COALESCE(s14.returns_14d,0)::numeric / s14.sold_14d::numeric, 2)
         ELSE 0 END AS return_rate_14d,
    s14.last_sold,
    (CURRENT_DATE - s14.last_sold)::int AS days_since_sale,
    lc.log_date AS last_change_date,
    (CURRENT_DATE - lc.log_date)::int AS days_since_change,
    lc.last_direction, lc.old_price AS pre_change_price,
    COALESCE(scc.sold_post, 0) AS sold_since_change
FROM amzfeed a
LEFT JOIN skusummary sk ON a.groupid = sk.groupid
LEFT JOIN sales_7d  s7  ON a.code = s7.code
LEFT JOIN sales_14d s14 ON a.code = s14.code
LEFT JOIN last_change lc ON a.code = lc.code
LEFT JOIN sold_since_change scc ON a.code = scc.code
WHERE a.groupid LIKE 'FLE030-IVES-%'
ORDER BY sk.segment, a.code;
```

### B. 6-week trend per colour

```sql
SELECT groupid,
       date_trunc('week', solddate)::date AS wk,
       SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END) AS units,
       SUM(CASE WHEN qty < 0 THEN ABS(qty) ELSE 0 END) AS returns,
       ROUND(AVG(CASE WHEN qty > 0 THEN soldprice END)::numeric, 2) AS avg_price
FROM sales
WHERE channel = 'AMZ' AND groupid LIKE 'FLE030-IVES-%'
  AND solddate >= CURRENT_DATE - INTERVAL '6 weeks'
GROUP BY groupid, 2 ORDER BY groupid, 2 DESC;
```

### C. Log hygiene — detect phantoms

```sql
WITH latest_log AS (
    SELECT DISTINCT ON (code) code, id, log_date
    FROM amz_price_log ORDER BY code, id DESC
),
phantom_candidates AS (
    SELECT l.id, l.code, l.log_date, l.new_price, l.old_price, LEFT(l.notes, 50) AS notes
    FROM amz_price_log l
    JOIN latest_log ll ON l.code = ll.code AND l.log_date = ll.log_date
)
SELECT p.id, p.code, p.log_date, p.new_price AS logged_new_price,
       NULLIF(a.amzprice,'')::numeric AS live_price, p.notes
FROM phantom_candidates p
JOIN amzfeed a ON p.code = a.code
WHERE a.groupid LIKE 'FLE030-IVES-%'
  AND p.log_date < CURRENT_DATE
  AND p.new_price != NULLIF(a.amzprice,'')::numeric
ORDER BY p.log_date DESC, p.code, p.id;
```

If any rows return, these are entries where the logged price doesn't match what's actually live on Amazon → likely a failed upload. List them up front and offer to clean.

---

## Step 2 — Classify every SKU into one of three tiers

### 🟢 ROUTINE (default "agree all" path)

All must be true:
- `days_since_change >= 3` (Amazon signal resolves fast — 3 days is enough for a settled read)
- `return_rate_14d < 40%` (no returns crisis)
- Not creeping into a stockout (`fba_live >= 3` for creeps)
- No judgment trigger (no £40 cross, no sub-£35.99 drop, no "stalling creep" pattern)

Then apply rule-based recommendation:

**CREEP** if `sold_7d >= 3` AND `return_rate_14d < 20%` AND `fba_live >= 3`
- Step = **£0.30** if current_price in [£38.50, £39.00] OR `last_direction == 'creep'`
- Step = **£0.50** otherwise
- If proposed > £40 AND SKU has no prior sales at ≥£40 → move to 🟡 (F4 judgment)

**DROP** if `days_since_sale >= 8` AND `fba_live >= 3`
- Step = £0.50 if 8–13 days dead
- Step = £1.00 if ≥14 days dead (D2 aggressive)
- If proposed < £35.99 → move to 🟡 (F3 judgment)

**D3 REVERT** if `last_direction == 'creep'` AND `sold_since_change == 0` AND `days_since_change >= 2`
- New price = `pre_change_price` (revert the failed creep)

### 🟡 JUDGMENT CALL (full detail, user reviews per SKU)

Any of these triggers:
- `return_rate_14d >= 40%` → is this price or sizing?
- Both creep and drop rules fire simultaneously → contradictory signals
- Proposed price crosses £40 without prior sales at ≥£40 for that SKU
- Proposed drop crosses £35.99 floor
- `fba_live <= 2` AND creep would fire (creep into stockout)
- **Stalling creep pattern**: last direction was creep, `sold_since_change <= 2`, AND the SKU's price history shows the previous (lower) price had sustained velocity → pull price-history table for the SKU
- Tail colours (RED/STONE/KHAKI) with `days_since_sale >= 14` → aggressive drop, hold, or colour-level issue?
- Anything that feels ambiguous → err on side of 🟡

For stalling-creep cases, include a quick price-history query in the SKU's block:
```sql
SELECT soldprice, COUNT(*) AS units, MIN(solddate) AS first, MAX(solddate) AS last
FROM sales WHERE channel = 'AMZ' AND code = '{SKU}' AND qty > 0
  AND solddate >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY soldprice ORDER BY soldprice;
```

### ⚪ HOLD (collapsed, one-liner per SKU)

Everything else. Use these reason codes for the summary:
- `OOS` — `fba_live == 0` AND `fba_inbound == 0`
- `STOCK_THIN` — `fba_live <= 2` with inbound flowing — wait for stock
- `JUST_CHANGED` — `days_since_change < 3`
- `AT_FLOOR` — `current_price <= £36.00` with adequate velocity
- `STEADY` — `sold_7d` in 1–2, no trigger
- `SETTLING` — recent change, moderate velocity post-change
- `PRODUCT_ISSUE` — high returns but below 40% FLAG threshold (watch-list)

---

## Step 3 — Present one comprehensive dashboard

Required sections in order:

### 1. Trend summary

One table, 8 rows:

| Segment | wc MM/DD | wc MM/DD | wc MM/DD | wc MM/DD | wc MM/DD (partial) | Returns (14d) | One-line status |
|---------|----------|----------|----------|----------|-------------------|---------------|-----------------|

### 2. Log hygiene

If phantoms detected, list briefly with code + logged vs live price + date. Ask: "clean these in the same batch?" Otherwise state "log clean."

### 3. 🟢 ROUTINE proposals — one flat table across all segments

| Code | Cur | → | New | Step | Reason (one line) | Rule |
|------|-----|---|-----|------|-------------------|------|

Sorted by segment then size. No discussion text.

### 4. 🟡 JUDGMENT CALLS — per-SKU blocks

Each with: current state, the relevant data (including price-history table for stalling creeps), my proposed action with rationale, and explicitly "I'd lean X, but here's why it's a call" — the user's brain is needed here.

### 5. ⚪ HOLDS — grouped by reason code

```
OOS (3): WHITE-03, BEIGE-03, STONE-04
STOCK_THIN (5): ...
JUST_CHANGED (2): ...
AT_FLOOR (4): ...
STEADY (6): ...
SETTLING (3): ...
PRODUCT_ISSUE (4): NAVY-08 (50% ret), BEIGE-08 (67%), MIDBLUE-08 (50%), RED-08 (...)
```

### 6. Final line

> "**Agree all routine + [N] judgment calls, adjust, or discuss?**"

---

## Step 4 — Apply in one batch

Once the user has confirmed decisions:

### Writes (all in a single transaction)

1. Append all approved rows to `C:\Users\UserPC\Downloads\AMZ-Price-Upload.txt`. Format: `{amzfeed.sku}\t{price}\t\t45.00`. Preserve any existing rows from earlier in the day.
2. INSERT all approved changes to `amz_price_log` with rationale in `notes` (one statement per change, single commit).
3. If log phantoms were approved for cleanup, DELETE those rows.

### Docs

Update `AMZ_PRICING.md` Status section with a compact session summary:
- Date + "FULL IVES REVIEW" marker
- N changes total (X creeps / Y drops / Z reverts)
- One-line changes table grouped by segment
- Priority watches for next session (£40 tests, resistance-zone tests, aggressive drops to monitor)
- Any rule/observation refinements learned this session

### Response patterns

- **"agree all"** → apply all routine + all judgment call proposals as stated
- **"agree all routine, discuss X"** → apply routine, drop into conversation on X
- **"agree all except X"** / **"hold X"** → apply rest, skip X
- **"adjust X to Y"** → modify X per instruction, apply rest as stated
- **"stop" / "pause"** → nothing written, return to normal flow

---

## What this procedure does NOT do

- Single-segment or exploratory deep-dives → use normal flow in `AMZ_PRICING.md`
- Changing the rule thresholds themselves → conversation first, then doc update
- New SKU/colour launches or discontinuations → separate task
- Anything outside IVES → add separate procedure docs if scope expands

---

## Notes for whoever picks this up next

- The goal is **minimum user time for equivalent quality decisions**, not "maximum agreement rate." If a routine recommendation feels wrong, move it to 🟡 — better to surface too many judgment calls than too few.
- Always capture rationale in `amz_price_log.notes` at the moment of the decision. A colleague (or you in a week) will need the context to understand why.
- If something recurring shows up in judgment calls across multiple sessions, it might deserve promotion to a routine rule — or the rule thresholds might need tuning. Raise it with the user, don't silently change behaviour.
- The procedure is conservative by design. Pushing more into 🟢 is a user-approved change, not a unilateral one.
