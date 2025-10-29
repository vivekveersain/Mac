#!/bin/bash

# Define the backup directory on your Raspberry Pi
BACKUP_DIR="/home/vabarya/backup"
DATE=$(date +%Y-%m-%d)
BACKUP_NAME="raspberry_pi_backup_$DATE.tar.gz"

# Define your Mac's SSH details
MAC_USER="your_mac_user"   # Replace with your Mac's username
MAC_HOST="your_mac_ip_or_hostname"  # Replace with your Mac's IP address or hostname
MAC_BACKUP_DIR="/path/to/mac/backup/directory"  # Replace with the directory where backups are stored on your Mac

# Step 1: Rsync backup from Mac to Raspberry Pi
echo "Transferring backup from Mac..."
rsync -avz $MAC_USER@$MAC_HOST:$MAC_BACKUP_DIR/ $BACKUP_DIR/

# Step 2: Restore Home Directory
echo "Restoring /home excluding /home/vabarya/data/TV..."
tar --exclude='/home/vabarya/data/TV' -xzf $BACKUP_DIR/$BACKUP_NAME -C /

# Step 3: Restore Cron Jobs
echo "Restoring cron jobs..."

# Extract cron jobs to the proper directories
tar -xzf $BACKUP_DIR/cron_backup_$DATE.tar.gz -C /

# For user-specific cron jobs, copy them back to /var/spool/cron/crontabs
echo "Restoring user cron jobs..."
cp -r /var/spool/cron/crontabs.bak/* /var/spool/cron/crontabs/

# Step 4: Restore System Configurations (e.g., /etc)
echo "Restoring /etc and service-related configurations..."
tar -xzf $BACKUP_DIR/etc_backup_$DATE.tar.gz -C /

# Step 5: Restore MiniDLNA Configurations
echo "Restoring MiniDLNA configurations..."
tar -xzf $BACKUP_DIR/minidlna_backup_$DATE.tar.gz -C /

# Step 6: Restore Syncthing Configurations
echo "Restoring Syncthing configurations..."
tar -xzf $BACKUP_DIR/syncthing_backup_$DATE.tar.gz -C /

# Step 7: Reload systemd and restart services if necessary
echo "Reloading systemd and restarting services..."

# Reload systemd to apply any new or restored services
sudo systemctl daemon-reload

# Restart MiniDLNA and Syncthing services
sudo systemctl restart minidlna
sudo systemctl restart syncthing@vabarya.service  # Replace with correct service if needed

# Clean up old backup files from Raspberry Pi
echo "Cleaning up local backup files..."
rm -rf $BACKUP_DIR/*

echo "Restore completed successfully!"
