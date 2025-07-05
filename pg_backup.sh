#!/bin/bash

BACKUP_DIR="/apps/scripts/database"
DATE=$(date +%Y-%m-%d)

# Make sure backup folder exists
mkdir -p "$BACKUP_DIR"

# Remove any old local backups so only today's will remain
rm -f "$BACKUP_DIR"/*

# List your production databases
DBS=("brookfield_prod" "splitleague_prod")

# Create fresh backups
for DB in "${DBS[@]}"; do
    echo "Backing up database: $DB"
    sudo -u postgres pg_dump -Fc "$DB" > "$BACKUP_DIR/${DB}_$DATE.dump"
done

# Compress all .dump files
gzip -f "$BACKUP_DIR"/*.dump

# Upload ONLY today's backups, replacing old Google Drive copies
rclone sync "$BACKUP_DIR/" bcgoogle:ServerBackups
