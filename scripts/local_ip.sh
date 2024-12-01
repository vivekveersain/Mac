#!/bin/bash

# Get the current IP address
current_ip=$(ifconfig | grep -oP 'inet \K192\.168\.\d+\.\d+')

# Check if the local_ip.txt file exists
if [ ! -f local_ip.txt ]; then
    echo "local_ip.txt not found. Creating it with the current IP."
    echo "$current_ip" > local_ip.txt
    stored_ip='0.0.0.0'
else
    # Read the stored IP address from the file
    stored_ip=$(cat local_ip.txt)
fi

# Compare the current IP with the stored IP
if [ "$current_ip" != "$stored_ip" ]; then
    curl -d "IP changed: $current_ip" ntfy.sh/kaptaan
    echo "IP has changed: $current_ip"
    echo "$current_ip" > local_ip.txt  # Update the file with the new IP
else
    echo "IP has not changed: $stored_ip"
fi

