#!/bin/bash

set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Creating backup in $BACKUP_DIR..."

# Database backup
docker-compose exec db pg_dump -U postgres taskmanager > $BACKUP_DIR/database.sql

# Redis backup
docker-compose exec redis redis-cli save
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_DIR/redis_dump.rdb

# Application files backup
tar -czf $BACKUP_DIR/uploads.tar.gz uploads/

echo "Backup completed in $BACKUP_DIR"
