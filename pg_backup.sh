#!/bin/bash
#
# Database Backup Script
# Backs up to: Google Drive > ServerBackups folder
# Google Account: brookfieldcomfort@gmail.com
# Local retention: 3 days
# Google Drive retention: Unlimited (version history)
#

BACKUP_DIR="/apps/scripts/database"
DATE=$(date +%Y-%m-%d)

# Make sure the backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup for $DATE..."

# Backup brookfield_prod
echo "Backing up brookfield_prod..."
sudo -u postgres pg_dump -Fc brookfield_prod > "$BACKUP_DIR/brookfield_backup_$DATE.dump"
gzip -f "$BACKUP_DIR/brookfield_backup_$DATE.dump"

# Backup splitleague_prod
echo "Backing up splitleague_prod..."
sudo -u postgres pg_dump -Fc splitleague_prod > "$BACKUP_DIR/splitleague_backup_$DATE.dump"
gzip -f "$BACKUP_DIR/splitleague_backup_$DATE.dump"

echo "Uploading to Google Drive..."

# Upload both backup files to Google Drive (with dates)
rclone copy "$BACKUP_DIR/brookfield_backup_$DATE.dump.gz" bcgoogle:ServerBackups
rclone copy "$BACKUP_DIR/splitleague_backup_$DATE.dump.gz" bcgoogle:ServerBackups

echo "Cleaning up old local backups (keeping last 3 days)..."

# Delete local backups older than 3 days
find "$BACKUP_DIR" -name "*backup_*.dump.gz" -mtime +3 -delete

echo "Backup complete. Local backup: $BACKUP_DIR/*_$DATE.dump.gz"
