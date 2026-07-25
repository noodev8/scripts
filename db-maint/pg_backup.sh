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
# EVERY step is checked and the script exits non-zero if anything fails, so
# cron reports it. Do not make this silent again: the Drive token expired in
# Apr 2026 and rclone's errors were ignored, so the script printed "Backup
# complete" every night for 109 days while nothing was reaching Drive.
#

set -u

BACKUP_DIR="/apps/backups"
REMOTE="bcgoogle:ServerBackups"
LOCAL_RETENTION_DAYS=3
REMOTE_RETENTION_DAYS=10
DATABASES="brookfield_prod splitleague_prod"

DATE=$(date +%Y-%m-%d)
failures=0

fail() {
    echo "ERROR: $*" >&2
    failures=$((failures + 1))
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
    exit 1
fi

echo "Backup complete for $DATE."
echo "  Local: $BACKUP_DIR/*_$DATE.dump.gz ($LOCAL_RETENTION_DAYS days)"
echo "  Drive: $REMOTE ($REMOTE_RETENTION_DAYS days)"
