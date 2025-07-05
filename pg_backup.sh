#!/bin/bash

BACKUP_DIR="/apps/scripts/database"

# Make sure the backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup..."

# Backup brookfield_prod
echo "Backing up brookfield_prod..."
sudo -u postgres pg_dump -Fc brookfield_prod > "$BACKUP_DIR/brookfield_backup.dump"
gzip -f "$BACKUP_DIR/brookfield_backup.dump"

# Backup splitleague_prod
echo "Backing up splitleague_prod..."
sudo -u postgres pg_dump -Fc splitleague_prod > "$BACKUP_DIR/splitleague_backup.dump"
gzip -f "$BACKUP_DIR/splitleague_backup.dump"

echo "Uploading to Google Drive..."

# Upload only these two backup files to Google Drive
rclone copy "$BACKUP_DIR/brookfield_backup.dump.gz" bcgoogle:ServerBackups
rclone copy "$BACKUP_DIR/splitleague_backup.dump.gz" bcgoogle:ServerBackups

echo "Backup complete."
