def process_arp_log(file_path):
    active_entries = {}
    with open(file_path) as f:
        for line in f.readlines():
            try:
                if "Starting ARP monitor with MAC lookup" in line: active_entries = {}
                if ">>" in line:
                    ip, name, mac = line.split()[2:5]
                    active_entries[mac] = line.strip()
                elif "<<" in line:
                    mac = line.split()[4]
                    active_entries.pop(mac, None)
                #print(line, active_entries)
            except: pass #print(line)
    print("\n".join(active_entries.values()))
    #return active_entries

process_arp_log('logs/network.log')
