import time
from datetime import date
import requests

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from lxml import html
import pickle
import os

DUMP_DIR = "./HSVP/"

def dump(today, city, sector, list_of_dicts):
    print("dumping...")
    folder_path=DUMP_DIR+city+"/"+sector+"/"
    os.makedirs(folder_path, exist_ok=True)
    file_name = folder_path + str(today) + ".pkl"
    with open(file_name, "wb") as file:
        pickle.dump(list_of_dicts, file)
    return True

def clean_data(data):
    for i, r in enumerate(data):
        try: cost = int(float(r['FullyPaid']))
        except: cost = 0
        data[i]['FullyPaid'] = cost
    return data

def pull_unavailable_entries_from_history(latest_data, last_data):
    changes = False
    try:
        latest_plots = [line["Plot No."] for line in latest_data]

        update_entries = []
        for line in last_data:
            if line["Plot No."] not in latest_plots:
                update_entries.append(line)
                changes = True

        latest_data += update_entries
    except: pass
    return latest_data, changes

def compare(city, sector):
    today = "2025-09-01"
    folder_path=DUMP_DIR+city+"/"+sector+"/"

    files = os.listdir(folder_path)
    last_file = folder_path+max([r for r in files if r[:-4] < today])
    latest_file = folder_path+today+".pkl"

    with open(last_file, "rb") as f: last_data = clean_data(pickle.load(f))
    with open(latest_file, "rb") as f: latest_data = clean_data(pickle.load(f))
    latest_data, changes = pull_unavailable_entries_from_history(latest_data, last_data)
    if changes: dump(today, city, sector, latest_data)

def post(a, b):
    print(a, b)

def create_lookup(data):
    lookup = {}
    for entry in data:
        plot_id = (
            entry['Urban Estate'],
            entry['Sector No.'], entry['Plot No.'],  entry['Property Category'],  entry['Sub Category']
        )
        lookup[plot_id] = entry
    return lookup

def test(x):
    return x**2

compare("UE018-Rohtak","25")