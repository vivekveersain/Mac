#!/bin/sh

min=100
max=0
last_notification_time=0  # Variable to store the timestamp of the last notification

# Directly use the degree symbol (°) by using printf with UTF-8 encoded characters
degree_symbol="°"

while true; do
    # Get the temperature reading from vcgencmd
    temp_str=$(vcgencmd measure_temp)
    
    # Extract the numeric temperature value
    temp=$(echo "$temp_str" | grep -oP '\d+' | head -1)

    # Update min and max temperatures
    if [ "$temp" -lt "$min" ]; then
        min=$temp
    fi

    if [ "$temp" -gt "$max" ]; then
        max=$temp
    fi

    # If temperature exceeds 55°C and the last notification was more than 10 seconds ago
    current_time=$(date +%s)  # Get the current timestamp in seconds
    if [ "$temp" -gt 55 ] && [ "$((current_time - last_notification_time))" -ge 30 ]; then
        # Send notification and update last notification time
        curl -s -d "Overheating at $temp°C" ntfy.sh/kaptaan > /dev/null 2>&1
        last_notification_time=$current_time  # Update the timestamp of the last notification
    fi

    # Clear the line completely by padding it with enough spaces
    printf "\r%s | Current: %s%sC | Min: %s%sC | Max: %s%sC" "$(date '+%H:%M:%S')" "$temp" "$degree_symbol" "$min" "$degree_symbol" "$max" "$degree_symbol"

    # Wait for 1 second before the next reading
    sleep 5
done
