# Missing Sizes

Amazon size-coverage gap report. Finds groupids that **are** on Amazon but are
missing sizes the brand normally carries — sizes we've never listed, not sizes
that are temporarily out of FBA stock.

Run on demand; nothing scheduled.

## Run

```
python missing-sizes/missing_sizes.py
python missing-sizes/missing_sizes.py --brand Strive
python missing-sizes/missing_sizes.py --segment STRIVE-SEG
```

Console output is one row per groupid with a gap: brand, groupid, colour,
segment, sizes currently listed on Amazon, sizes missing. Also written to
`missing_sizes.csv` (overwritten each run) alongside the script, with just
`groupid` and `missing_sizes` columns.

## How it decides what "the full range" is

This is the part worth understanding before trusting the output.

**`skumap` is not treated as the size universe.** A style bought in as a test
batch only ever gets SKUs created for the sizes ordered, so `skumap` under-states
the range for exactly the groupids the report is meant to catch.

Instead each brand's standard size sets are **inferred from what recurs** — the
exact size sets shared by two or more of that brand's groupids. Established sets
outvote one-off test batches.

Two deliberate refinements:

- **The recurring set is used exactly, not turned into a min-to-max range.**
  Brands routinely skip half sizes (Strive carries 4, 5, 6, 6.5, 7, 8 — no 4.5,
  5.5 or 7.5). Assuming a contiguous run would flag a false gap on every groupid.
- **A brand can have more than one set.** Rieker sells a women's line (~4–7.5)
  and a men's line (~7.5–11) under one brand, so each groupid is matched to
  whichever of its brand's sets it overlaps with most, rather than a single
  brand-wide range.

Brands with no recurring set at all — every groupid unique, or too few groupids
to establish a pattern — are skipped and listed separately rather than guessed at.

## Scope

Only groupids with at least one actual Amazon sale ever (`sales.channel = 'AMZ'`,
`qty > 0`) are reported: a listing that has never sold isn't worth filling out.

The report does **not** check warehouse stock and does **not** flag listed sizes
that are currently out of FBA stock — that's a restocking question, not a
coverage one.
