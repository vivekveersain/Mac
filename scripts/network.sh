#!/bin/sh

send_ntfy() {
    message="$1"
    curl -s -d "$message" https://ntfy.sh/kaptaan_network >/dev/null
}

SUBNET="192.168.1"
START=101
END=120

known_devices=""

SKIPS="a4lexiP
norueN
ijatiP
404-a4lexiP
sgniP-norueN"

MAC_FILE=".ips"
last_md5=""

echo "Starting ARP monitor with MAC lookup. Press Ctrl+C to stop."

first_run=1

while true; do
    # printf "\rScanning...\033[K"
    all_msgs=""

    current_devices=""

    # Check if MACS was modified
    if [ -f "$MAC_FILE" ]; then
        md5=$(md5sum "$MAC_FILE" | awk '{print $1}')
        if [ "$md5" != "$last_md5" ]; then
            MAC_NAMES=$(cat "$MAC_FILE")
            last_md5="$md5"
            printf "Reloaded!\n"
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
                    current_devices="$current_devices
$ip $mac"
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
            ping -c 1 -W 1 $ip >/dev/null 2>&1

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
            printf "\r\033[K%s %s\n" "$msg" "$mac"

            if echo "$SKIPS" | grep -Fxq "$name"; then
                continue   # skips this iteration
            fi
            send_ntfy "$msg"

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
                printf "\r\033[K%s %s\n" "$msg" "$mac"
                if echo "$SKIPS" | grep -Fxq "$name"; then
                    continue   # skips this iteration
                fi
                send_ntfy "$msg"
            fi
        done
    fi

    known_devices="$current_devices"
    first_run=0

    # Sleep 2 minutes with interactive countdown
    sleep_seconds=10
    while [ $sleep_seconds -gt 0 ]; do
        # printf "\rSleeping %ds…\033[K" $sleep_seconds
        sleep 1
        sleep_seconds=$((sleep_seconds - 1))
    done
    printf "\r"
done
