#!/bin/bash

# Define log file paths
COUNTER_FILE=~/counter.txt
PING_FILE=~/ping.txt

# IP of the host to ping
HOST="192.168.1.102"

# Function to log the current date to a file
log_date() {
    echo "$(date)" >> "$1"
}

# Function to perform ping check
ping_host() {
    ping -q -c 1 "$HOST"
}

# Function to reset Wi-Fi (turn off and on)
reset_wifi() {
    termux-wifi-enable false
    sleep 1
    termux-wifi-enable true
}

# Function to send a notification via Termux
send_notification() {
    termux-notification
}

# Function to send a notification to ntfy.sh
send_ntfy_alert() {
    curl -d "Local Host Down?" ntfy.sh/kaptaan
}

# Perform the ping and handle the outcome
log_date "$COUNTER_FILE"
ping_host || {
    # If ping fails, handle the failure
    send_notification
    reset_wifi
    log_date "$PING_FILE"
    sleep 60
    send_ntfy_alert
    send_notification
}
