(date>>~/counter.txt; ping -q -c 1 192.168.1.102) || (termux-notification; termux-wifi-enable false; sleep 1; termux-wifi-enable true && date >> ~/ping.txt; sleep 60; curl -d "Local Host Down?" ntfy.sh/kaptaan; termux-notification)
#date>>~/counter.txt; termux-wifi-enable false; sleep 1; termux-wifi-enable true
