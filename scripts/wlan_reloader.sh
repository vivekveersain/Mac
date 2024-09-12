ping -q -c 1 192.168.1.102 || (termux-wifi-enable false; sleep 1; termux-wifi-enable true && date >> ~/ping.txt)
