# Merchant Feed

Builds the Google Merchant Center product feed and uploads it.

`merchant_feed.py` pulls live product data from PostgreSQL, writes a TSV feed,
and pushes it to Google Merchant Center over SFTP. It runs unattended on the VPS
— see `crontab.txt` for the schedule.

## Run

```
python merchant-feed/merchant_feed.py
```

Works from any directory: the script resolves its own location, reaches back to
the repo root for `logging_utils`, and loads `.env` from there.

## Output

`GOOGLE-DATA-Merchant.txt` — the generated feed. It's written twice: once into
`merchant-feed/logs/` (the copy that gets uploaded) and once into this folder.
**It's a build artefact, not source** — it's overwritten on every run, so don't
edit it or treat its contents as a reference.

Logs go to `merchant-feed/logs/`, rotated into `merchant-feed/archive_logs/` —
this folder keeps its own, separate from the repo-root `logs/`.

## Configuration

Read from the root `.env`:

- `MERCHANT_SFTP_HOST`, `MERCHANT_SFTP_PORT` (default 19321),
  `MERCHANT_SFTP_USERNAME`, `MERCHANT_SFTP_PASSWORD`

If the SFTP credentials are missing the feed is still generated — only the
upload is skipped, and it says so rather than failing loudly. Worth knowing when
the feed looks stale on Google's side but the run looked fine.
