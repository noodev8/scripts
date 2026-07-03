# Proven Prices — Shopify anchor store

One row per managed `groupid`. The anchor is the price at which the style reliably
sells at acceptable margin — the reference every pricing decision is measured
against. See `scale/PRICING_PROCESS.md` for how it's used.

- **No row / blank anchor** = compute on first analysis, then fill this table.
- When we move the needle and it holds, we overwrite the anchor. The store keeps
  only the current truth, not the history of moves.
- Migrates to a DB column once the mechanic is proven; nothing depends on it
  staying an MD.

## EVA-SEG (seeded 2026-07-01)

| groupid | anchor | set_date | note |
|---|---:|---|---|
| 0129443-ARIZONA | 36 | 2026-07-01 | White / Nar |
| 1019152-ARIZONA | 36 | 2026-07-01 | Green / Nar |
| 1019051-ARIZONA | 36 | 2026-07-01 | Blue / Reg |
| 0128201-GIZEH | 36 | 2026-07-01 | Gizeh Black / Reg |
| 0129423-ARIZONA | 39 | 2026-07-01 | Black / Nar |
| 0128183-MADRID | 30 | 2026-07-01 | Madrid White / Nar |
| 0129421-ARIZONA | 39 | 2026-07-01 | Black / Reg |
| 1019094-ARIZONA | 40 | 2026-07-01 | Green / Reg |
| 0128163-MADRID | 32 | 2026-07-01 | Madrid Black / Nar |
| 1019142-ARIZONA | 36 | 2026-07-01 | Blue / Nar |
| 0128221-GIZEH | 35 | 2026-07-01 | Gizeh White / Reg |
| 0128161-MADRID | 32 | 2026-07-01 | Madrid Black / Reg |
| 1022466-ARIZONA | 37 | 2026-07-01 | Yellow / Nar |
| 1015398-BARBADOS | 32 | 2026-07-01 | Barbados Black / Reg |
| 1001497-ARIZONA | 39 | 2026-07-01 | Grey / Reg |
| 1030447-ARIZONA | 40 | 2026-07-01 | Taupe / Reg |
| 1014614-ARIZONA | 35 | 2026-07-01 | Pink |
| 1015399-BARBADOS | 32 | 2026-07-01 | Barbados White / Reg |
| 1015487-HONOLULU | 30 | 2026-07-01 | Honolulu Black |
| 1028566-BARBADOS | 32 | 2026-07-01 | Barbados Green / Reg |
| 0128181-MADRID | 32 | 2026-07-01 | Madrid White / Reg |
| 1027305-ARIZONA | 36 | 2026-07-01 | White / Reg |
| 1031278-GIZEH | 32 | 2026-07-01 | Gizeh White |
| 1026202-ARIZONA | 36 | 2026-07-01 | White / Reg |
| 1022433-ARIZONA | 32 | 2026-07-01 | Gold / Reg |
| 1001498-ARIZONA | 40 | 2026-07-01 | Grey / Nar |
| 1024691-ARIZONA | 32 | 2026-07-01 | Green |
| 1031318-HONOLULU | 40 | 2026-07-01 | Honolulu White |
| 1019143-GIZEH | 45 | 2026-07-01 | Gizeh Green |
| 1031340-ARIZONA | 50 | 2026-07-01 | Pink |
| 1032100-GIZEH | 45 | 2026-07-01 | Gizeh Pink |
