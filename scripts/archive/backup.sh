#!/bin/bash

# Define the backup directory on your Raspberry Pi
BACKUP_DIR="/home/vabarya/backup/"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_NAME="raspberry_pi_backup_$DATE.tar.gz"

# Define your Mac's SSH details
MAC_USER="vabarya"   # Replace with your Mac's username
MAC_HOST="192.168.1.101"  # Replace with your Mac's IP address or hostname
MAC_BACKUP_DIR="/Users/vabarya/Downloads/"  # Replace with the directory where you want to store backups on your Mac

# Create the backup directory on your Raspberry Pi (if it doesn't exist)
mkdir -p $BACKUP_DIR

# Step 1: Backup Home Directory (Exclude /home/vabarya/data/TV)
echo "Backing up /home excluding /home/vabarya/data/TV..."
tar --exclude='/home/vabarya/data/TV' --exclude='/home/vabarya/backup' -czf $BACKUP_DIR/$BACKUP_NAME /home/vabarya

# Step 2: Backup Cron Jobs
echo "Backing up cron jobs..."
tar -czf $BACKUP_DIR/cron_backup_$DATE.tar.gz /var/spool/cron/crontabs /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly

# Step 3: Backup System Config (e.g., /etc) and Services
echo "Backing up /etc and service-related configurations..."
tar -czf $BACKUP_DIR/etc_backup_$DATE.tar.gz /etc/

# Step 4: Backup MiniDLNA Configurations
echo "Backing up MiniDLNA configurations..."
tar -czf $BACKUP_DIR/minidlna_backup_$DATE.tar.gz /etc/minidlna.conf /var/lib/minidlna/

# Step 5: Backup Syncthing Configurations
echo "Backing up Syncthing configurations..."
tar -czf $BACKUP_DIR/syncthing_backup_$DATE.tar.gz /home/vabarya/.config/syncthing/

# Step 6: Rsync backup to your Mac
echo "Transferring backup to Mac..."
rsync -avz $BACKUP_DIR/ $MAC_USER@$MAC_HOST:$MAC_BACKUP_DIR/

# Clean up old backup files on Raspberry Pi
echo "Cleaning up local backup files..."
#rm -rf $BACKUP_DIR/*

echo "Backup completed and transferred to Mac!"
