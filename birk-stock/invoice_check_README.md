# Birk-Track

Checks a Birkenstock delivery against its invoice: does what arrived (`incoming_stock`) match what was invoiced (`birktracker`)?

## Usage

Edit the `params` CTE at the top of `check_combined.sql`:
- `target_invoices` — invoice number(s) from `birktracker.invoicenum` (array, supports multiple invoices delivered together)
- `start_date` / `end_date` — the delivery date window to check `incoming_stock` against

Run it against the DB. Output is per-code `total_invoiced` vs `total_arrived` with a `shortfall` column, plus a `TOTAL` row.

## History
- 2026-07-14 — invoice `5290101345`
- 2026-07-17 — invoice `5290101607`
