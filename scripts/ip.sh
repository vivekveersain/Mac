#!/bin/bash

# Set the PATH variable explicitly
export PATH=$PATH:/usr/bin

# Define the file paths
ip_file="${HOME}/data/ip/ip.txt"
ip_log_file="${HOME}/data/ip/ip_ts.txt"

# Get the current IP
current_ip=$(curl -s https://ipwhois.app/json/ | grep -o '"ip":"[^"]*' | sed 's/"ip":"//')

# Read the stored IP from the file
stored_ip=$(cat "$ip_file")

# Compare current IP with stored IP
if [ "$current_ip" != "$stored_ip" ]; then
  # Send a notification via ntfy
  curl -s -d "IP Changed!" ntfy.sh/kaptaan_network > /dev/null 2>&1

  # Log the IP change with timestamp
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $current_ip" >> "$ip_log_file"

  # Update the stored IP in the file
  echo "$current_ip" > "$ip_file"
fi
