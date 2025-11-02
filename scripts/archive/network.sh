#!/bin/bash

send_ntfy() {
    message="$1"
    curl -s -d "$message" https://ntfy.sh/kaptaan_network >/dev/null
}

filter_logs_since() {
    last_run_time="$1"
    log_file="${HOME}/logs/network.log"
    latest_timestamp=$last_run_time
    r=0
    stack=""

    # Read the log file and filter the lines
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^[0-9]{4}\.[0-9]{2}\.[0-9]{2} ]]; then
            continue
        fi

        timestamp=$(echo "$line" | awk '{print $1 " " $2}')
        
        if [[ "$timestamp" > "$last_run_time" ]]; then
            line_no_mac=$(echo "$line" | sed 's/\(.*\) [^ ]*$/\1/')
            stack+="$line_no_mac"$'\n' 
            r=$((r + 1))
        fi
    done < "$log_file"

    if [[ -n "$stack" ]]; then
        temp_str=$(vcgencmd measure_temp)
        temp=$(echo $temp_str | grep -oP '\d+\.\d+')
        send_ntfy "$stack $temp°C"
    fi

    # Return the latest timestamp (which will be stored in last_run_time)
    latest_timestamp=$(date "+%Y.%m.%d %H:%M:%S")
    echo $latest_timestamp
}

SUBNET="192.168.1"
START=101
END=120
known_devices=""
SKIPS="a4lexiP
norueN
ijatiP
404-a4lexiP
sgniP-norueN
enohPi
daPi"

MAC_FILE="${HOME}/.ips"
last_md5=""
last_run_time=$(date -d "-3000 seconds" "+%Y.%m.%d %H:%M:%S")

echo "Starting ARP monitor with MAC lookup. Press Ctrl+C to stop."

first_run=1

# Start the initial timestamp for the next run of `filter_logs_since`
next_run_time=$(date -d "+300 seconds" "+%Y.%m.%d %H:%M:%S")

while true; do
    current_devices=""

    # Check if MACS was modified
    if [ -f "$MAC_FILE" ]; then
        md5=$(md5sum "$MAC_FILE" | awk '{print $1}')
        if [ "$md5" != "$last_md5" ]; then
            MAC_NAMES=$(cat "$MAC_FILE")
            last_md5="$md5"
        fi
    fi

    # Ping all IPs to populate ARP table
    i=$START
    while [ $i -le $END ]; do
        ping -c 1 -W 1 $SUBNET.$i >/dev/null 2>&1
        i=$((i + 1))
    done

    # Read ARP table into memory (only valid MACs)
    while read line; do
        ip=$(echo "$line" | awk '{print $1}')
        mac=$(echo "$line" | awk '{print $3}')
        case "$mac" in
            *:*) 
                if [ -z "$current_devices" ]; then
                    current_devices="$ip $mac"
                else
                    current_devices="$current_devices $ip $mac"
                fi
                ;;
        esac
    done <<EOF
$(arp -n)
EOF

    # Sort current_devices by IP numerically
    current_devices=$(echo "$current_devices" | awk '{print $1, $2}' | sort -t . -k3,3n -k4,4n)

    # Detect new devices
    echo "$current_devices" | while read line; do
        ip=$(echo "$line" | awk '{print $1}')
        mac=$(echo "$line" | awk '{print $2}')
        if ! echo "$known_devices" | grep -q "^$ip "; then
            # ping -c 1 -W 1 $ip >/dev/null 2>&1

            # Lookup MAC name
            name="$mac"
            for entry in $MAC_NAMES; do
                entry_mac=$(echo "$entry" | cut -d= -f1)
                entry_name=$(echo "$entry" | cut -d= -f2)
                if [ "$mac" = "$entry_mac" ]; then
                    name="$entry_name"
                fi
            done

            timestamp=$(date "+%Y.%m.%d %H:%M:%S")
            msg="$timestamp >> $ip $name"
            printf "%s %s\n" "$msg" "$mac"

            if echo "$SKIPS" | grep -Fxq "$name"; then
                continue   # skips this iteration
            fi
        fi
    done

    # Detect dropped devices (skip first run)
    if [ "$first_run" -ne 1 ]; then
        echo "$known_devices" | while read line; do
            ip=$(echo "$line" | awk '{print $1}')
            mac=$(echo "$line" | awk '{print $2}')

            # Lookup MAC name
            name="$mac"
            for entry in $MAC_NAMES; do
                entry_mac=$(echo "$entry" | cut -d= -f1)
                entry_name=$(echo "$entry" | cut -d= -f2)
                if [ "$mac" = "$entry_mac" ]; then
                    name="$entry_name"
                fi
            done

            if ! echo "$current_devices" | grep -q "^$ip "; then
                timestamp=$(date "+%Y.%m.%d %H:%M:%S")
                msg="$timestamp << $ip $name"
                printf "%s %s\n" "$msg" "$mac"
                if echo "$SKIPS" | grep -Fxq "$name"; then
                    continue   # skips this iteration
                fi
            fi
        done
    fi

    known_devices="$current_devices"
    first_run=0

    # Check if it's time to run `filter_logs_since`
    current_time=$(date "+%Y.%m.%d %H:%M:%S")
    if [[ "$current_time" > "$next_run_time" ]]; then
        # Run the function and update last_run_time
        last_run_time=$(filter_logs_since "$last_run_time")

        # Calculate next run time (add 300 seconds)
        next_run_time=$(date -d "+1800 seconds" "+%Y.%m.%d %H:%M:%S")
    fi

    # Continue without sleeping, just looping
done
