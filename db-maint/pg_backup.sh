#!/bin/bash
#
# Database Backup Script
#
# Dumps brookfield_prod and splitleague_prod, gzips them, uploads to Google
# Drive (brookfieldcomfort@gmail.com), then prunes both copies.
#
#   Local:  /apps/backups          -- 3 days
#   Drive:  bcgoogle:ServerBackups -- 10 days
#
# Backups live outside the git checkout -- they are not source code.
#
# EVERY step is checked and the script exits non-zero if anything fails. Do not
# make this silent again: the Drive token expired in Apr 2026 and rclone's errors
# were ignored, so the script printed "Backup complete" every night for 109 days
# while nothing was reaching Drive.
#
# REPORTS TO BCLOG (2026-11-08): the crontab has no MAILTO, so cron's own failure
# mail went to a server mailbox nobody reads — a non-zero exit alone was still
# silent. Every run now ends with one bclog row in brookfield_prod (section
# 'Backup', workstation 'Scheduler'): "OK: ..." or "FAILED: ...". bcweb's
# dashboard reads it (GET /backup-last) and shows a warning when the last run
# failed or no good backup has been recorded for 2 days.
#

set -u

BACKUP_DIR="/apps/backups"
REMOTE="bcgoogle:ServerBackups"
LOCAL_RETENTION_DAYS=3
REMOTE_RETENTION_DAYS=10
DATABASES="brookfield_prod splitleague_prod"

DATE=$(date +%Y-%m-%d)
failures=0
first_error=""

fail() {
    echo "ERROR: $*" >&2
    failures=$((failures + 1))
    [ -z "$first_error" ] && first_error="$*"
}

# One bclog row for the dashboard warning. psql reads the SQL from stdin so the
# message goes in as a quoted variable (:'msg'), never pasted into the SQL. A
# failure to log is reported but never changes the backup's own result.
report() {
    if ! sudo -u postgres psql -d brookfield_prod -q -X -v ON_ERROR_STOP=1 -v msg="$1" >/dev/null <<'SQL'
INSERT INTO bclog (workstation, section, log, date, time, created_at)
VALUES ('Scheduler', 'Backup', left(:'msg', 250),
        (now() AT TIME ZONE 'Europe/London')::date,
        to_char(now() AT TIME ZONE 'Europe/London', 'HH24:MI'), now());
SQL
    then
        echo "WARNING: could not write the bclog row" >&2
    fi
}

mkdir -p "$BACKUP_DIR" || { echo "ERROR: cannot create $BACKUP_DIR" >&2; exit 1; }

echo "Starting backup for $DATE..."

for db in $DATABASES; do
    name="${db%_prod}"
    dump="$BACKUP_DIR/${name}_backup_$DATE.dump"

    echo "Backing up $db..."
    if ! sudo -u postgres pg_dump -Fc "$db" > "$dump"; then
        fail "pg_dump failed for $db"
        rm -f "$dump"
        continue
    fi

    # A failed dump can still leave a file behind -- an empty one is not a backup.
    if [ ! -s "$dump" ]; then
        fail "pg_dump produced an empty file for $db"
        rm -f "$dump"
        continue
    fi

    if ! gzip -f "$dump"; then
        fail "gzip failed for $db"
        continue
    fi

    echo "Uploading $(basename "$dump.gz")..."
    if ! rclone copy "$dump.gz" "$REMOTE"; then
        fail "upload failed for $db (local copy kept at $dump.gz)"
    fi
done

echo "Pruning local backups older than $LOCAL_RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*backup_*.dump.gz" -mtime +"$LOCAL_RETENTION_DAYS" -delete \
    || fail "local prune failed"

# --include keeps this to our own dump files: ServerBackups holds other things
# (an old database/Archive/*.sql copy) that must not be swept up.
echo "Pruning Drive backups older than $REMOTE_RETENTION_DAYS days..."
rclone delete "$REMOTE" --min-age "${REMOTE_RETENTION_DAYS}d" --include "*backup_*.dump.gz" \
    || fail "Drive prune failed"

if [ "$failures" -gt 0 ]; then
    echo "BACKUP FAILED: $failures error(s) above. Backup for $DATE is NOT safe." >&2
    report "FAILED: $failures error(s) - $first_error"
    exit 1
fi

report "OK: $DATABASES dumped and uploaded to Drive"

echo "Backup complete for $DATE."
echo "  Local: $BACKUP_DIR/*_$DATE.dump.gz ($LOCAL_RETENTION_DAYS days)"
echo "  Drive: $REMOTE ($REMOTE_RETENTION_DAYS days)"
