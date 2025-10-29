#!/bin/bash

rm -rf /tmp/vitals
mkdir /tmp/vitals

tmp_file="/tmp/vitals/data.txt"
touch $tmp_file

degree_symbol="°C"
min=100    # Initial min value (arbitrary high value)
max=0      # Initial max value (arbitrary low value)
last_notification_time=0  # Initialize the last notification time

# Initialize the data file with a Temp line if it doesn't exist
if ! grep -q "Temp:" $tmp_file; then
    echo "Temp: [$min$degree_symbol-$max$degree_symbol]" > $tmp_file
fi

while true; do
    # Get the current temperature reading from vcgencmd
    temp_flag=0
    temp_str=$(vcgencmd measure_temp)
    temp=$(echo $temp_str | grep -oP '\d+\.\d+')

    # Update min and max temperatures using bc for floating-point comparison
    if (( $(echo "$temp < $min" | bc -l) )); then
        min=$temp
        temp_flag=1
    fi
    if (( $(echo "$temp > $max" | bc -l) )); then
        max=$temp
        temp_flag=1
    fi

    # If min or max was updated, replace or add the line in the file with the new values
    if [[ $temp_flag -eq 1 ]]; then
        sed -i "s/^Temp: \[.*\]/Temp: [$min$degree_symbol$C-$max$degree_symbol$C]/" $tmp_file
    fi

    # Check if temperature exceeds 55°C
    if (( $(echo "$temp > 55" | bc -l) )); then
        # Only fetch the current time after confirming the temperature is high
        current_time=$(date +%s)  # Get the current timestamp in seconds

        # Check if more than 30 seconds have passed since the last notification
        if [ "$((current_time - last_notification_time))" -ge 30 ]; then
            # Send notification and update last notification time
            curl -s -d "Overheating at $temp°C" ntfy.sh/kaptaan > /dev/null 2>&1
            last_notification_time=$current_time  # Update the timestamp of the last notification
        fi
    fi
    sleep 5
done
