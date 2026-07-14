# Birkenstock code naming: birktracker vs skusummary/skumap

## The problem

`birktracker.code` is typed in manually (or from a forward-order feed) up to
~6 months before a style actually arrives and gets set up in `skusummary`/
`skumap`. If whoever enters the forward order in `birktracker` doesn't guess
the exact short style name that will later be used in `skusummary.groupid`,
the two tables go out of sync on that style forever — even though it's the
same 7-digit Birkenstock code.

This matters at goods-in: any script matching `birktracker` codes against
`incoming_stock`/`skumap`/`skusummary` (e.g. `birk_check_combined.sql`) will
show a false "not arrived" shortfall for a style that actually arrived fine,
just under a differently-spelled code.

Example seen 2026-07:

| birktracker code | correct skusummary groupid |
|---|---|
| `1015487-Honolulu Essentials EVA Unisex-36` | `1015487-HONOLULU` |
| `1029356-Sydney Luxe Buckle Birko-Flor Women-37` | `1029356-SYDNEY` |

`birktracker` had the full descriptive Birkenstock style name; `skusummary`
uses Birkenstock's short style code (`HONOLULU`, `SYDNEY`), which is the
house convention everywhere else (`skumap.groupid`, `skusummary.groupid`).

## How to tell genuinely-new vs naming-mismatch

Compare on the **7-digit base code only** (the part before the first `-`),
ignoring everything after it:

```sql
-- Base codes in birktracker with NO match at all in skusummary -> genuinely new,
-- not yet set up (fine, will be filtered out at goods-in until added).
WITH bt AS (
  SELECT DISTINCT split_part(code, '-', 1) AS base_code FROM birktracker
),
ss AS (
  SELECT DISTINCT split_part(groupid, '-', 1) AS base_code FROM skusummary
)
SELECT bt.base_code
FROM bt
WHERE NOT EXISTS (SELECT 1 FROM ss WHERE ss.base_code = bt.base_code)
ORDER BY bt.base_code;
```

```sql
-- Base codes that DO exist in skusummary, but birktracker's naming
-- (base + style text, size stripped off) doesn't match skusummary.groupid
-- exactly -> naming mismatch, fixable in birktracker.
WITH bt AS (
  SELECT DISTINCT code,
    split_part(code, '-', 1) AS base_code,
    regexp_replace(code, '-[0-9]+$', '') AS bt_groupid   -- strip trailing size
  FROM birktracker
),
ss AS (
  SELECT DISTINCT groupid, split_part(groupid, '-', 1) AS base_code
  FROM skusummary
)
SELECT DISTINCT bt.bt_groupid AS birktracker_groupid, ss.groupid AS skusummary_groupid
FROM bt
JOIN ss ON ss.base_code = bt.base_code
WHERE bt.bt_groupid <> ss.groupid
ORDER BY bt.bt_groupid;
```

## Fixing a mismatch

Once a mismatch is confirmed, `birktracker` is the only table to fix (never
touch `skusummary`/`skumap` naming to match `birktracker` — those are the
source of truth). Rewrite `birktracker.code`, preserving the size suffix:

```sql
UPDATE birktracker
SET code = regexp_replace(code, '^1015487-Honolulu Essentials EVA Unisex-', '1015487-HONOLULU-')
WHERE code LIKE '1015487-Honolulu Essentials EVA Unisex-%';
```

See `birk_fix_code_naming.sql` for a worked example (includes a preview
`SELECT` to check old->new pairs before running the `UPDATE`).

## Note

This can't be prevented up front — the correct short style name isn't known
until the style is actually set up in `skusummary`, which can be months after
the forward order is logged in `birktracker`. Treat it as a periodic cleanup:
whenever running an arrivals check that shows unexpected shortfalls, run the
base-code comparison above before assuming stock is actually missing.
