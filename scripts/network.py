import subprocess
import os
from datetime import datetime
import time
import requests

SUBNET = "192.168.1"
START = 101
END = 120
MAC_FILE = os.path.expanduser("~/.ips")
MD5_HASH = ""
MACS = {}
IP_TAGS = {}

known_devices = set()
start_time = time.time() - 1750
PING_STACK = []

def load_mac_names(MD5_HASH):
    """Load MAC names from the MAC file."""
    if os.path.exists(MAC_FILE):
        md5 = subprocess.check_output(["md5sum", MAC_FILE]).decode("utf-8").splitlines()[0].split(" ")[0]
        if md5 == MD5_HASH: return MACS, MD5_HASH

        with open(MAC_FILE, "r") as f:
            macs = dict(row.strip("\n").split("=") for row in f.readlines())
            MD5_HASH = md5
            return macs, MD5_HASH
    return {}

def ping_devices(START, END):
    """Ping all devices in the range to update ARP table."""
    for i in range(START, END + 1):
        subprocess.run(["ping", "-c", "1", "-W", "1", f"{SUBNET}.{i}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_arp():
    arp_output = subprocess.check_output(["arp", "-n"]).decode("utf-8").splitlines()
    # rows = [[r for r in row.split(" ") if r != ""] for row in arp_output[1:]]
    # ip_to_mac = dict((r[0], r[2]) for r in rows if ":" in r[2])
    ip_to_mac = dict((row[33:50], row[:15].strip()) for row in arp_output[1:] if row[33:45] != "(incomplete)")
    return ip_to_mac

def investigate(arp_output, known_devices):
    current_devices = set(arp_output.keys())
    new_devices = current_devices - known_devices
    lost_devices = known_devices - current_devices
    return new_devices, lost_devices, current_devices

def postman(PING_STACK):
    if PING_STACK:
        try:
            vcgencmd_output = subprocess.check_output(["vcgencmd", "measure_temp"])
            degree = vcgencmd_output.decode().strip().replace("temp=", "").replace("'C", "°C")
        except: degree = ""

        message = "\n".join([" ".join(row[:-1]) for row in PING_STACK]) + "\n\n" + degree
        url = "https://ntfy.sh/kaptaan_network"
        requests.post(url, data=message.encode("utf-8"), timeout=10)

while True:
    MACS, MD5_HASH = load_mac_names(MD5_HASH)
    ping_devices(START, END)
    
    arp_output = read_arp()

    # Format the datetime in the desired format
    now = datetime.now()
    formatted_datetime = now.strftime("%Y.%m.%d %H:%M:%S")
    new_devices, lost_devices, known_devices = investigate(arp_output, known_devices)

    for device in new_devices:
        print(formatted_datetime, ">>", arp_output[device], MACS.get(device, device), device)
        row = [formatted_datetime, ">>", arp_output[device], MACS.get(device, device), device]
        IP_TAGS[device] = arp_output[device]
        PING_STACK.append(row)
    for device in lost_devices:
        print(formatted_datetime, "<<", IP_TAGS[device], MACS.get(device, device), device)
        row = [formatted_datetime, "<<", IP_TAGS[device], MACS.get(device, device), device]
        PING_STACK.append(row)

    if time.time() - start_time > 1800:
        postman(PING_STACK)
        start_time = time.time()
        PING_STACK = []