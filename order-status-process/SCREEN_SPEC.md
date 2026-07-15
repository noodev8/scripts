# Spec: "Expected to Arrive" — supplier-order management screen

**Audience:** the engineer/AI building this in our Next.js app.
**Nature of this doc:** problem + data + a suggested direction. Implementation,
UI, query strategy, and framework choices are **yours** — this does not
prescribe them. Where it says "suggested", treat it as a starting point, not a
requirement. You are expected to find the best solution in your own codebase.

---

## 1. The problem, in plain terms

When we reorder stock, the reorder screen shows a running total of what's
**already on the way** from suppliers, so we don't re-buy something that's
incoming. That "expected to arrive" total is only as good as the underlying
supplier-order rows — and those rows drift out of sync with reality:

- **Ghosts inflate it.** A supplier is out of stock and the order never comes,
  but the row sits there looking like incoming stock — so we *skip a reorder we
  should have made*. The row is only auto-deleted after 30 days, silently, with
  no notification.
- **Partial / wrong-channel orders distort it.** We might order 4 and only 2
  ever ship; or we ordered it as Amazon-bound when it should now go to local
  stock (or vice-versa).

The net effect: **what's live in stock is easy to see and trust; what's
*expected to arrive* is not.** There's no place for a human to look at the
outstanding supplier orders, see the full story of each, and correct it.

**Goal:** a screen where an operator can view every outstanding supplier order
with enough context to judge it, and take a couple of simple corrective actions
so the "expected to arrive" total becomes trustworthy.

This is explicitly **not** a rebuild of the ordering/goods-in system (that works
and stays as-is). It's a management/visibility layer over data we already hold.

---

## 2. What the operator needs to see (suggested content, not layout)

One line per outstanding supplier order (see §3 for how rows map to orders),
each showing the whole story so the decision is obvious at a glance:

| Field | Meaning / why it matters |
|---|---|
| Supplier | who to chase |
| Product code + style/description | what it is |
| Destination: **Amazon** or **Local** | which total it feeds |
| Date ordered + **days waiting** | the ghost signal — old = suspect |
| **Units still outstanding** | the number currently inflating the total |
| Units already arrived | partial-delivery picture |
| **Current free/live stock now** | "do we even still need this?" |
| Recent actual arrivals for this code | proof of what has physically landed lately |

The intelligence is in **joining these together**, not in new data. A good line
lets the operator think: *"ordered 4 from X, 26 days ago, 1 arrived, 3 still
'expected', and we already hold 5 free — these 3 are ghosts, remove them."*

---

## 3. Data model — the tables involved

All of this lives in our shared PostgreSQL database. **Read these carefully —
there are non-obvious conventions that will bite you if you assume the normal
thing.**

### `orderstatus` — the live work queue (this is what you read + write)
The table the reorder total is built from. Primary key: `(ordernum, shopifysku)`.
Relevant columns:

- `shopifysku` — the product code (this is the code, despite the name).
- `supplier`
- `ordertype` (integer) — **this is everything.** Meanings:
  - `1` = customer order (Shopify sale). **Never touch these.**
  - `2` = supplier restock bound for **local stock**.
  - `3` = supplier restock bound for **Amazon**.
  - `5` = legacy internal transfer, dormant — ignore.
- `arrived` (0/1) and `arriveddate` — set when a unit is scanned in at goods-in.
- `createddate` — when the order was placed (use for "days waiting").
- `qty` — **IGNORE THIS FIELD. It is a red herring** (see gotchas below).
- `channel`, `title`, etc. — descriptive.

**Outstanding supplier orders = `ordertype IN (2,3) AND arrived = 0`.** That set
is what the screen manages.

#### Critical gotchas about `orderstatus`
- **One row per physical unit, NOT per quantity.** If we order 4 units, there
  are 4 separate rows, each representing one unit. `qty` is not maintained for
  these and must not be used. To count "how many units expected", **count the
  rows** (`arrived = 0`), don't sum `qty`.
- **`arrived` is a per-unit binary flag.** With one row per unit this is fine at
  the total level — arrived units simply drop out of the `arrived = 0` set.
- Rows are transient: an automated job already deletes `arrived=0` supplier rows
  after 30 days. Your screen accelerates that cleanup manually; it doesn't
  replace the job.

### `stockorder` — durable record of "what we ordered" (read-only context)
Kept 365 days. Columns: `code`, `orderdate`, `groupid`, `qty`, `cost`. Useful if
you want to show/reconcile ordered-vs-arrived, but not required for v1.

### `incoming_stock` — durable record of "what actually arrived" (read-only)
Append-only, **one row per unit received**, kept 3 years. Columns: `code`,
`groupid`, `arrival_date`, `quantity_added` (always 1), `created_at`, `target`
(where it was routed, e.g. `C3-Amazon` or a shelf location), `workstation`.
This is the source of truth for "what has physically landed" — use it for the
"recent arrivals" and "already arrived" context.

### `localstock` — live stock ledger (read-only context)
- `code`, `groupid`, `qty`, `location`
- `ordernum` — `#FREE` means free/unallocated live stock.
- `allocated` — `amz` (bound for Amazon) or `unallocated`.
- `deleted` — soft-delete flag.
- **Current free live stock for a code = rows where `ordernum = '#FREE' AND
  deleted = 0 AND qty > 0`** (sum `qty`, or count rows).

### `skumap` / `skusummary` — product reference (read-only)
- `skumap`: maps `code` ↔ `groupid`, holds size info.
- `skusummary`: product master — `groupid`, `brand`, `supplier`, etc.
- **Do NOT use `skusummary.stockvariants` or `skusummary.variants`** for any
  stock/size count — they are stale and unreliable. Derive stock from
  `localstock` and size universe from `skumap` if you ever need them.

---

## 4. The actions (the only write surface)

Keep this minimal — the value is in the presentation, not in workflow.

1. **Remove (write off) — per unit.** Delete outstanding rows for a line so the
   total corrects. Must support removing *some* of N (e.g. supplier confirms
   only 2 of 4 are coming → remove 2, keep 2), not just all-or-nothing.
   - Deleting `orderstatus` rows is acceptable and correct — the durable trail
     lives in `stockorder`/`incoming_stock`, so nothing important is lost.
   - **Safety rail: only ever delete rows where `ordertype IN (2,3) AND
     arrived = 0`.** Never delete `ordertype = 1` (customer orders) or
     `arrived = 1` rows.
2. **Switch destination Amazon ↔ Local** (optional for v1). Flip `ordertype`
   between `3` and `2` for a line. Doesn't change *whether* it's expected, just
   *which channel total* it counts toward.

No other state. Specifically **no "confirm/keep" flag** — a decided non-goal.

---

## 5. Constraints & things to preserve

- **Don't change the goods-in / ordering machinery.** Other processes write to
  `orderstatus` continuously (goods-in scanning flips `arrived`, order placement
  inserts rows). Your screen must tolerate concurrent changes and read fresh.
- **Respect the ordertype safety rail above** on every write.
- Assume the automated 30-day purge still runs; your screen is the manual
  fast-path, not a replacement.

---

## 6. One thing to verify before building on it

The whole screen's value assumes the **reorder "on order" total counts only
`arrived = 0` supplier rows.** Please confirm how that total is currently
computed. If it counts `arrived = 0` only, these actions are sufficient and
partial/received deliveries already fall out correctly. If it counts *all* rows
regardless of `arrived`, flag it — that's a separate accuracy issue to settle
first.

---

## 7. Non-goals (out of scope)

- Full PO-aware rebuild of the order/goods-in system.
- Any "confirm it's still coming" state or flag.
- Amazon inbound-shipment reconciliation (a separate, accepted quirk).
- Touching customer orders (`ordertype = 1`) in any way.

---

## 8. Your task

Design and build the screen and its read/write queries in our Next.js app and
stack, following the data conventions above. Choose the UI, the query approach,
the grouping of per-unit rows into readable lines, and how deletes/edits are
confirmed and (if you think it's warranted) logged. Surface anything in §6 or
the gotchas in §3 that turns out differently from described.
