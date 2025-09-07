import time
from datetime import date
import requests

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from lxml import html
import pickle
import locale
import os

DUMP_DIR = "/data/data/com.termux/files/home/storage/external-1/Data/HSVP/"

def create_lookup(data):
    lookup = {}
    for entry in data:
        plot_id = (
            entry['Urban Estate'],
            entry['Sector No.'], entry['Plot No.'],  entry['Property Category'],  entry['Sub Category']
        )
        lookup[plot_id] = entry
    return lookup

def post(title, data, priority = "default", tags = "", link = None):
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)

def comp_master(city, sector, latest_data, last_data):
    yesterday_lookup = create_lookup(last_data)
    today_lookup = create_lookup(latest_data)
    stacker = ""
    negs = ""
    # --- Compare data ---
    
    for plot_id, today_entry in today_lookup.items():
        if sector == "1" and plot_id[2] not in ["2442", "116", "40P"]: continue
        item_ = ""
        negative = False
        yesterday_entry = yesterday_lookup.get(plot_id)
        if not yesterday_entry:
            #print(f"New plot added: {plot_id}")
            stacker += f"\n\nNew plot added: {plot_id} {today_entry['Allottee Name']}"
            continue
        
        # Check for changes
        changes = {}
        for key in today_entry:
            if today_entry[key] != yesterday_entry.get(key):
                changes[key] = {'yesterday': yesterday_entry.get(key), 'today': today_entry[key]}
        
        if changes:
            #print(f"{plot_id}:")
            item_ += f"\n\n{plot_id[2:]} >> {today_entry['Allottee Name']}:\n"
            for field, change in changes.items():
                #print(f"    {field}: {change['yesterday']} -> {change['today']}")
                item_ += f"    {field}: {change['yesterday']} -> {change['today']}"
                if field == "FullyPaid" and int(float(change['yesterday'])) < int(float(change['today'])):
                    negative = True
            if negative: negs += item_
            else: stacker += item_
    stacker += negs
    print(stacker.strip("\n"))
    post(city+ "/" + sector, stacker)

def compare(city, sector):
    today = "2025-08-30"
    folder_path=DUMP_DIR+city+"/"+sector+"/"

    files = os.listdir(folder_path)
    last_file = folder_path+max([r for r in files if r[:-4] != today])
    latest_file = folder_path+today+".pkl"

    with open(last_file, "rb") as f: last_data = pickle.load(f)
    with open(latest_file, "rb") as f: latest_data = pickle.load(f)
    comp_master(city, sector, latest_data, last_data)

compare("UE018-Rohtak", "1")
