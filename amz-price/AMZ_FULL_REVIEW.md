# Full Segment Review — Procedure

**Scope:** the Amazon channel, one segment at a time. The 🟢/🟡/⚪ machinery here is generic; the *numbers* it tests against (floor, ceiling, step band) are read from the segment's row in `AMZ_PRODUCTS.md`. Don't reuse one segment's thresholds on another.

**Trigger:** user says **"full `<segment>` review"** — e.g. "full ives review", "full rieker review". `<segment>` resolves to one or more `skusummary.segment` values (IVES = the pair `IVES-WHITE` + `IVES-COLOUR`; most others are a single segment). If ambiguous, confirm which segment(s) before pulling data.

**Purpose:** one comprehensive pass across a segment in minimum user time — pull all data, auto-classify every SKU, present one dashboard, batch-apply. Replaces segment-by-segment manual forensics for routine reviews.

**When NOT to use this:** single-colour deep dives, exploratory questions, investigations of a specific issue → use the conversational flow in `AMZ_PRICING.md`.

---

## Step 0 — Load the segment's parameters

Before pulling data, read the segment's row in `AMZ_PRODUCTS.md` and pin its parameters for this run:

| Parameter | Meaning | IVES example |
|---|---|---|
| `{SEGMENTS}` | the `skusummary.segment` value(s) | `('IVES-WHITE','IVES-COLOUR')` |
| `{FLOOR}` | tidy-number floor below which a drop becomes a 🟡 judgment call | £35.99 |
| `{HARD_FLOOR}` | economic floor = cost + FBA + min margin (never price below) | ~low-£20s |
| `{CEILING}` | tested resistance price a creep must not cross without prior sales above it | £40.00 |
| `{STEP_BAND}` | price range where creeps use the small step | £38.50–£39.00 |
| `{RRP}` | upload-file max-price | £45.00 |

If a segment has **no tested ceiling yet**, there is no £-cross trigger — creeps run up toward RRP and the *first* stall becomes the discovered ceiling (record it back into the registry afterwards).

---

## Step 1 — Pull all data in one round of parallel queries

Substitute `{SEGMENTS}` throughout. (The old IVES-only version hardcoded `a.groupid LIKE 'FLE030-IVES-%'`; the segment join below replaces that and works for any segment.)

### A. Per-SKU state

```sql
WITH seg AS (
    SELECT groupid FROM skusummary WHERE segment IN {SEGMENTS}
),
sales_7d AS (
    SELECT code, SUM(CASE WHEN qty>0 THEN qty ELSE 0 END)::int AS sold_7d
    FROM sales WHERE channel='AMZ' AND solddate >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY code
),
sales_14d AS (
    SELECT code,
           SUM(CASE WHEN qty>0 THEN qty ELSE 0 END)::int AS sold_14d,
           SUM(CASE WHEN qty<0 THEN ABS(qty) ELSE 0 END)::int AS returns_14d,
           MAX(solddate) AS last_sold
    FROM sales WHERE channel='AMZ' AND solddate >= CURRENT_DATE - INTERVAL '14 days'
    GROUP BY code
),
last_change AS (
    SELECT DISTINCT ON (code)
        code, log_date, old_price, new_price,
        CASE WHEN new_price>old_price THEN 'creep'
             WHEN new_price<old_price THEN 'drop' ELSE 'flat' END AS last_direction
    FROM amz_price_log ORDER BY code, id DESC
),
sold_since_change AS (
    SELECT s.code, SUM(CASE WHEN s.qty>0 THEN s.qty ELSE 0 END)::int AS sold_post
    FROM sales s JOIN last_change lc ON s.code = lc.code
    WHERE s.channel='AMZ' AND s.solddate > lc.log_date
    GROUP BY s.code
)
SELECT
    a.code, a.groupid, sk.segment, a.sku AS amz_sku,
    NULLIF(a.amzprice,'')::numeric AS current_price,
    COALESCE(a.amzlive,0) AS fba_live,
    COALESCE(a.amztotal,0) AS fba_total,
    GREATEST(COALESCE(a.amztotal,0)-COALESCE(a.amzlive,0),0) AS fba_inbound,
    COALESCE(s7.sold_7d,0)  AS sold_7d,
    COALESCE(s14.sold_14d,0) AS sold_14d,
    COALESCE(s14.returns_14d,0) AS returns_14d,
    CASE WHEN COALESCE(s14.sold_14d,0)>0
         THEN ROUND(COALESCE(s14.returns_14d,0)::numeric / s14.sold_14d::numeric, 2)
         ELSE 0 END AS return_rate_14d,
    s14.last_sold,
    (CURRENT_DATE - s14.last_sold)::int AS days_since_sale,
    lc.log_date AS last_change_date,
    (CURRENT_DATE - lc.log_date)::int AS days_since_change,
    lc.last_direction, lc.old_price AS pre_change_price,
    COALESCE(scc.sold_post,0) AS sold_since_change
FROM amzfeed a
JOIN seg ON a.groupid = seg.groupid
LEFT JOIN skusummary sk ON a.groupid = sk.groupid
LEFT JOIN sales_7d  s7  ON a.code = s7.code
LEFT JOIN sales_14d s14 ON a.code = s14.code
LEFT JOIN last_change lc ON a.code = lc.code
LEFT JOIN sold_since_change scc ON a.code = scc.code
ORDER BY sk.segment, a.code;
```

### B. 6-week trend per colour/style

```sql
SELECT a.groupid,
       date_trunc('week', s.solddate)::date AS wk,
       SUM(CASE WHEN s.qty>0 THEN s.qty ELSE 0 END) AS units,
       SUM(CASE WHEN s.qty<0 THEN ABS(s.qty) ELSE 0 END) AS returns,
       ROUND(AVG(CASE WHEN s.qty>0 THEN s.soldprice END)::numeric,2) AS avg_price
FROM sales s
JOIN skusummary sk ON s.groupid = sk.groupid
WHERE s.channel='AMZ' AND sk.segment IN {SEGMENTS}
  AND s.solddate >= CURRENT_DATE - INTERVAL '6 weeks'
GROUP BY a.groupid, 2 ORDER BY a.groupid, 2 DESC;
```
*(alias `a` here is `s`/`sk`; keep the groupid grain so each colour/style shows separately.)*

### C. Log hygiene — detect phantoms (logged price ≠ live price)

```sql
WITH seg AS (SELECT groupid FROM skusummary WHERE segment IN {SEGMENTS}),
latest_log AS (
    SELECT DISTINCT ON (code) code, id, log_date
    FROM amz_price_log ORDER BY code, id DESC
),
phantom_candidates AS (
    SELECT l.id, l.code, l.log_date, l.new_price, l.old_price, LEFT(l.notes,50) AS notes
    FROM amz_price_log l JOIN latest_log ll ON l.code=ll.code AND l.log_date=ll.log_date
)
SELECT p.id, p.code, p.log_date, p.new_price AS logged_new_price,
       NULLIF(a.amzprice,'')::numeric AS live_price, p.notes
FROM phantom_candidates p
JOIN amzfeed a ON p.code = a.code
JOIN seg ON a.groupid = seg.groupid
WHERE p.log_date < CURRENT_DATE
  AND p.new_price != NULLIF(a.amzprice,'')::numeric
ORDER BY p.log_date DESC, p.code, p.id;
```

Any rows = logged price doesn't match live Amazon → likely a failed upload. List them up front and offer to clean.

---

## Step 2 — Classify every SKU into one of three tiers

### 🟢 ROUTINE (default "agree all" path)

All must be true:
- `days_since_change >= 3` (Amazon signal resolves fast — 3 days is a settled read)
- `return_rate_14d < 40%` (no returns crisis)
- not creeping into a stockout (`fba_live >= 3` for creeps)
- no judgment trigger (no `{CEILING}` cross, no sub-`{FLOOR}` drop, no stalling-creep pattern)

Then apply the rule-based recommendation:

**CREEP** if `sold_7d >= 3` AND `return_rate_14d < 20%` AND `fba_live >= 3`
- Step = **£0.30** if `current_price` in `{STEP_BAND}` OR `last_direction == 'creep'`
- Step = **£0.50** otherwise
- If proposed price > `{CEILING}` AND the SKU has no prior sales at ≥`{CEILING}` → move to 🟡

**DROP** if `days_since_sale >= 8` AND `fba_live >= 3`
- Step = £0.50 if 8–13 days dead
- Step = £1.00 if ≥14 days dead (aggressive)
- If proposed price < `{FLOOR}` → move to 🟡

**REVERT** if `last_direction == 'creep'` AND `sold_since_change == 0` AND `days_since_change >= 2`
- New price = `pre_change_price` (revert the failed creep)

### 🟡 JUDGMENT CALL (full detail, user reviews per SKU)

Any of:
- `return_rate_14d >= 40%` → price or sizing?
- both creep and drop rules fire → contradictory signals
- proposed price crosses `{CEILING}` without prior sales at/above it for that SKU
- proposed drop crosses `{FLOOR}`
- `fba_live <= 2` AND a creep would fire (creep into stockout)
- **stalling-creep pattern**: last direction was creep, `sold_since_change <= 2`, and the previous (lower) price had sustained velocity → pull the SKU's price history
- tail/low-volume SKUs dead `>= 14` days → aggressive drop, hold, or a colour-level issue?
- anything ambiguous → err to 🟡

For stalling-creep cases, include in the SKU block:
```sql
SELECT soldprice, COUNT(*) AS units, MIN(solddate) AS first, MAX(solddate) AS last
FROM sales WHERE channel='AMZ' AND code='{SKU}' AND qty>0
  AND solddate >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY soldprice ORDER BY soldprice;
```

### ⚪ HOLD (collapsed, one-liner per SKU)

Everything else. Reason codes:
- `OOS` — `fba_live == 0` AND `fba_inbound == 0`
- `STOCK_THIN` — `fba_live <= 2` with inbound flowing — wait for stock
- `JUST_CHANGED` — `days_since_change < 3`
- `AT_FLOOR` — at/near `{FLOOR}` with adequate velocity
- `STEADY` — `sold_7d` 1–2, no trigger
- `SETTLING` — recent change, moderate post-change velocity
- `PRODUCT_ISSUE` — elevated returns but below the 40% flag — watch-list

---

## Step 3 — Present one comprehensive dashboard

In order:

1. **Trend summary** — one table, one row per sub-segment (e.g. IVES-WHITE, IVES-COLOUR): last ~5 weeks units, returns (14d), one-line status.
2. **Log hygiene** — if phantoms detected, list code + logged vs live + date, ask "clean these in the same batch?" Otherwise "log clean."
3. **🟢 ROUTINE proposals** — one flat table: `Code | Cur | → | New | Step | Reason | Rule`. Sorted by segment then size. No prose.
4. **🟡 JUDGMENT CALLS** — per-SKU blocks: current state, the relevant data (incl. price-history for stalling creeps), the proposed action with rationale, and an explicit "I'd lean X, but here's why it's a call." Mark each `[CLAUDE DECISION]` so the user can scan them. (Inline-autopilot default — see modes below.)
5. **⚪ HOLDS** — grouped by reason code, count + code list per line.
6. **Final line:** "**Agree all routine + [N] judgment calls, adjust, or discuss?**"

---

## Step 4 — Apply in one batch

Once the user confirms:

1. **Append all approved rows** to `%USERPROFILE%\Downloads\AMZ-Price-Upload.txt` (current machine's profile) — format `{amzfeed.sku}\t{price}\t\t{RRP}`. Preserve any rows already in the file from earlier in the day.
2. **INSERT all approved changes** to `amz_price_log` with rationale in `notes` (one statement per change, single commit).
3. **If phantoms were approved for cleanup**, DELETE those rows.

> Never write to `amzfeed`. (See `AMZ_PRICING.md`.)

Then update the segment's **current-state line in `AMZ_PRODUCTS.md`** — one or two lines (resume-pointer discipline: not a session diary; the detail is already in `amz_price_log.notes`). Record any newly-discovered ceiling/floor for the segment. If a 🟡 pattern recurs across several reviews, raise promoting it to a 🟢 rule (or retuning a threshold) **with the user** — don't change behaviour silently.

### Modes

- **Inline-autopilot (default):** Claude states firm decisions on all 🟡 calls inline; user reads and batch-approves. Fastest; the norm when time is tight. Calibrated on IVES at 100% agreement (2026-04-21, 16/16).
- **Dialog:** Claude presents 🟡 as "I'd lean X, your call" and steps through. Use only when the user signals time ("let's go one by one", "I want to discuss these").

### Response patterns

- **"agree all"** → apply all routine + all judgment proposals as stated
- **"agree all routine, discuss X"** → apply routine, drop into conversation on X
- **"agree all except X" / "hold X"** → apply rest, skip X
- **"adjust X to Y"** → modify X, apply rest as stated
- **"stop" / "pause"** → nothing written, return to normal flow

---

## What this procedure does NOT do

- Single-segment exploratory deep-dives → conversational flow in `AMZ_PRICING.md`.
- Changing the rule thresholds themselves → conversation first, then update the registry/this doc.
- New SKU/colour launches or discontinuations → separate task.
- Anything off the Amazon channel.

## Notes for whoever picks this up next

- The goal is **minimum user time for equivalent quality**, not maximum agreement rate. If a routine recommendation feels wrong, move it to 🟡 — surfacing too many judgment calls beats too few.
- Always capture rationale in `amz_price_log.notes` at the moment of decision.
- The procedure is conservative by design. Pushing more into 🟢 is a user-approved change, not a unilateral one.
- This used to be IVES-only; it was generalised to any segment on 2026-06-19. If you hit a segment whose behaviour the thresholds don't fit, that's a registry/threshold conversation, not a reason to abandon the procedure.
