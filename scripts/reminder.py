import json
import requests
from datetime import date, timedelta
import os
from postman import dispatch

HOME = os.environ.get("HOME")
DATA_DIR = f"{HOME}/data/"

TARGETS = [
    {"file": "court.json", "target_key": "case_number"},
    # {"file": "case2.json", "target_key": "case_id"}
]

def load_data(file):
    try:
        with open(DATA_DIR + file, "r") as f:
            local_data = json.load(f)
    except: 
        return {"next_action": f"{file} not found!"}
    return local_data

def find_tomorrow(local_data, target_key):
    tomorrow = str(date.today() + timedelta(days=1))
    temp_stack = []

    for key in local_data.keys():
        data = local_data[key]
        nxt_action = data["next_action"]
        if nxt_action == tomorrow:
            temp_stack.append({data[target_key] : data["details"]})
    return temp_stack

def compile_and_post(stack):
    text = "\n".join(
        f"{k}:{(' ' + v) if v else ''}"
        for d in stack
        for k, v in d.items()
    )
    post("Reminder for Tomorrow!", text)

def post(title, data, priority = "default", tags = "", link = None):
    # print("kaptaan_court", title, data, priority, tags, link)
    dispatch("kaptaan_court", title, data, priority, tags, link)

stack = [] # example stack = [{'CS - CIVIL SUIT/14/2025': ''}]
for target in TARGETS:
    file = target["file"]
    target_key = target["target_key"]
    # print(file)

    try:
        local_data = load_data(file)
        temp_stack = find_tomorrow(local_data, target_key)
        stack += temp_stack
    except:
        stack += [{"Error!":f"{file} not found."}]

# print(stack)
if len(stack) > 0 :
    compile_and_post(stack)