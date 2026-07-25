# Images

Product image sync for the legacy PowerBuilder app, plus protection for extra
images added in the Shopify UI. Runs nightly on the VPS — see `crontab.txt`.

## Run

```
python images/updateimages.py                  # nightly default
python images/updateimages.py --limit 50       # last N products instead
python images/updateimages.py --dry-run
python images/updateimages.py --skip-shopify
```

## What it does

1. **Drive image sync** — downloads each product's main image from
   `images.brookfieldcomfort.com` and uploads it into brookfielduser1's Google
   Drive folder, which is what PowerBuilder displays. Uploading via the API
   means this runs headless on the VPS with no Drive-for-Desktop sync present.
2. **Shopify extra-image sync** — records images added directly in the Shopify
   UI into the `shopifyimages` table, so a bulk CSV product upload can't
   silently wipe them.

Default scope is products loaded to `skusummary` **today or yesterday**.

## Two gotchas that will cost you time

**Products can be silently skipped.** The nightly window keys off
`skusummary.created`, and the bcweb product-entry app (from ~17 Jul 2026) can
leave that NULL — those rows never appear in the window and their images are
never synced. Nothing errors. If images are missing for recent products, catch
up with `--limit N`, which ignores the date window.

**The Drive folder is pinned by id** in `.env` (`DRIVE_IMAGES_FOLDER_ID`). The
OAuth scope is `drive.file`, deliberately narrow so no Google verification is
needed — but it means the app can only see folders **it created**. Move,
recreate or replace that folder and the script loses access to it permanently;
you'd have to create a new one via the API and re-pin the id.

## Credentials

`authorize_drive.py` mints and refreshes `drive_token.json` — run it once,
logged in as **brookfielduser1@gmail.com**, then copy the token to the VPS.

```
python images/authorize_drive.py
```

Both scripts read credentials from the **repo root**, not this folder:
`drive_token.json`, `drive_oauth_client.json` and `.env`. All three are
gitignored and never committed, so `git pull` does not deploy them — they are
copied to the VPS by hand.

Note that both scripts *write* `drive_token.json` (on refresh) and
`authorize_drive.py` also writes `.env`. If you move this folder again, re-anchor
`REPO_ROOT`, not just the imports.

## When can this be deleted?

The script's own header answers this, and it's worth re-reading before assuming
it's permanent. Both jobs exist only while PowerBuilder is live **and** while we
still push product changes to Shopify by CSV upload. If PowerBuilder is retired,
job 1 is pointless — nothing else reads that Drive folder. If CSV uploads stop,
job 2 is pointless. If both, delete the script, its cron entry, the Drive folder
and the `.env` id.
