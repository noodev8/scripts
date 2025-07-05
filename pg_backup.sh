#!/bin/bash

BACKUP_DIR="/apps/scripts/database"
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUP_DIR"

# Explicitly list your production databases
DBS=("brookfield_prod" "splitleague_prod")

for DB in "${DBS[@]}"; do
    echo "Backing up database: $DB"
    sudo -u postgres pg_dump -Fc "$DB" > "$BACKUP_DIR/${DB}_$DATE.dump"
done

# Compress all .dump files
gzip -f $BACKUP_DIR/*.dump

# Delete backups older than 3 days
find "$BACKUP_DIR" -type f -mtime +3 -delete
