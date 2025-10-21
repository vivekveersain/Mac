#!/bin/bash

# Define your network subnet (e.g., 192.168.1)
SUBNET="192.168.1"
START=101
END=120

# Path to the .ips file (Make sure to adjust the path if it's different)
IPS_FILE="${HOME}/.ips"

# Function to get MAC address of an IP
get_mac_address() {
    local ip=$1
    mac=$(arp -n $ip | grep -i $ip | awk '{print $3}')
    echo $mac
}

# Read the IPS file into an associative array (MAC => Device Name)
declare -A devices
while IFS="=" read -r mac name; do
    # Remove any extra spaces
    mac=$(echo "$mac" | tr -d '[:space:]')
    name=$(echo "$name" | tr -d '[:space:]')
    devices["$mac"]="$name"
done < "$IPS_FILE"

# Track previously detected devices using an associative array
declare -A previous_devices

# Ping all IPs in the subnet and get MAC addresses
while true; do
    timestamp=$(date "+%Y.%m.%d %H:%M:%S")
    echo -ne "\r$timestamp Scanning... \r"
    current_devices=()

    for i in $(seq $START $END); do
        ip="$SUBNET.$i"

        # Ping IP to check if it is alive
        ping -c 1 -W 1 $ip >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            # If the IP responds, get its MAC address from ARP table
            mac=$(get_mac_address $ip)
            if [ -n "$mac" ]; then
                # Look up the MAC address in the devices array to find the name
                device_name="${devices[$mac]}"
                if [ -z "$device_name" ]; then
                    device_name="Unknown Device"
                fi
                
                # Check if this device was previously detected
                if [[ -z "${previous_devices[$mac]}" ]]; then
                    # New device detected
                    echo "$timestamp >> $ip $mac ($device_name)"
                fi

                # Mark this device as detected and add to current_devices list
                current_devices+=("$mac")
                previous_devices["$mac"]=1
            fi
        fi
    done

    # Check for devices that were previously detected but are no longer found
    for mac in "${!previous_devices[@]}"; do
        if [[ ! " ${current_devices[@]} " =~ " $mac " ]]; then
            # Device is no longer present, show exit message
            device_name="${devices[$mac]}"
            if [ -z "$device_name" ]; then
                device_name="Unknown Device"
            fi
            echo "$timestamp << $mac ($device_name)"
            # Remove device from the previously detected list
            unset previous_devices["$mac"]
        fi
    done

    # Optional: Sleep for a short period before scanning again (adjust the sleep time as needed)
    sleep 2
done
