# DB Maintenance

Database housekeeping: the weekly purge and the nightly backup. Both run
unattended on the VPS — see `crontab.txt` for schedules.

## Sales-table maintenance

```
python db-maint/clean_sales.py
```

Runs `clean_sales.sql`, which sits beside it. The two must stay in the same
folder — the script resolves the SQL relative to its own location.

What the SQL does:

- Purges old rows from `sales`, `bclog`, `stockorder` and `incoming_stock`
- Fixes returns that arrived with `soldprice = 0`
- Clears ghost rows from `orderstatus`

The delete windows are **deliberately tuned** — the 30-day `orderstatus` window
matches real supplier lead times (~10 days typical, 20 longest legitimate
arrival, 30 as ceiling plus buffer). Don't shorten them without understanding
why they're set where they are; the reasoning is in the SQL comments.

Failure is safe: a missing SQL file or any SQL error logs, rolls back and exits
1. Reaching `=== CLEAN SALES COMPLETED ===` means the transaction committed.

## Database backup

```
./db-maint/pg_backup.sh
```

Dumps `brookfield_prod` and `splitleague_prod` with `pg_dump -Fc`, gzips them,
and uploads to Google Drive (`ServerBackups`) via `rclone` under
brookfieldcomfort@gmail.com.

**Retention:** 3 days locally, unlimited on Drive via version history.

**Backups are written to `/apps/backups`, outside the git checkout.** They used
to go to `/apps/scripts/database`, which meant database dumps accumulating
inside a git repo — invisible to git (they're gitignored) but very much present
on disk. Changed Jul 2026. Backups are not source code and shouldn't live in a
checkout.

This is server-side only: it needs `sudo -u postgres`, `rclone` with the
`bcgoogle` remote configured, and the paths are absolute Linux paths. It won't
do anything useful on the laptop.
