#!/bin/bash

DOMAIN=$1

# --- Detect VPN interface ---
#VPN_INTERFACE=$(ifconfig | awk '/utun|tap|tun[0-9]/{print $1}' | sed 's/://g' | head -n 1)
VPN_INTERFACE=$(ifconfig | awk '/ppp[0-9]/{print $1}' | sed 's/://g' | head -n 1)
if [ -z "$VPN_INTERFACE" ]; then
    echo "Error: No VPN interface found."
    exit 1
fi

# --- Detect VPN gateway ---
VPN_GATEWAY=$(netstat -rn | awk -v iface="$VPN_INTERFACE" '$0 ~ iface && $2 != "link#" {print $2; exit}')
if [ -z "$VPN_GATEWAY" ]; then
    echo "Error: Could not determine VPN gateway for $VPN_INTERFACE"
    exit 1
fi

echo "VPN interface: $VPN_INTERFACE"
echo "VPN gateway: $VPN_GATEWAY"

# --- Resolve IPv4 addresses (strip carriage returns) ---
IP_LIST=$(dig +short A "$DOMAIN" | tr -d '\r')
if [ -z "$IP_LIST" ] || [[ "$IP_LIST" == *"connection timed out"* ]]; then
    echo "Error: Could not resolve $DOMAIN to IPv4 addresses."
    if [ "$DOMAIN" = "hsvphry.org.in" ] ; then
        IP_LIST="115.245.85.202"
    else
        echo "Exiting..."
        exit 1
    fi

fi
echo "IPs: $IP_LIST"

# --- Add routes ---
for IP in $IP_LIST; do
    sudo route delete -interface "$IP" "$VPN_INTERFACE" >/dev/null 2>&1
    sudo route -n add -interface "$IP" "$VPN_INTERFACE"
    #echo "Routing $IP for $DOMAIN through VPN."
done
echo "Re-Routed!"