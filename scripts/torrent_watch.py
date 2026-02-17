#!/usr/bin/env python3

import requests
import pandas as pd
import os
import time

pd.set_option('display.float_format', '{:.2f}'.format)

def search(name, must = [], skip = [], min_size = 1, min_seeds = 30 ):
    print(name, must, skip, min_size, min_seeds)
    low_q = ["CAM", "HDTS", "HD.TS", "HD-TS", "HD TS", "900MB", "DVDSCR", "HDRIP", "DVDRIP", "HDTV", "HD.TV", "HD-TV"
    ,"1600MB", "HD TV"] + skip
    results = requests.get('https://apibay.org/q.php',params={'q':name})
    if int(results.status_code) == 200:
        results = results.json()
        stack = []
        df = pd.DataFrame()
        for result in results:
            if any(flag.upper() in result["name"].upper() for flag in low_q): continue
            if all(flag.upper() in result["name"].upper() for flag in must): stack.append(result)
        if len(stack) > 0:
            df = df.from_dict(stack)
            df["GB"] = df["size"].astype("int")/(1024**3)
            df = df[(df.GB > min_size) & ((df.seeders + df.leechers).astype("int") >= min_seeds)]
            if df.shape[0] > 0:
                print(df["name"].iloc[0])
                notify(name, "Torrent might be available")
                time.sleep(5)
        return df
    else:
        notify("Torrent ERROR!!", results.status_code)

def notify(title, text, tags = [], priority = "default", link = None):
    # os.system("""
    #           osascript -e 'display notification "{}" with title "{}"'
    #           """.format(text, title))
    # print(f"==> {text} <> {title}")
    title = title.replace("\r", "").replace("\t", "").replace("\n", "")
    data = text.replace("\r", "").replace("\t", "")
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    response = requests.post("https://ntfy.sh/kaptaan",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)
    print(f"==> {title} <> {data} <> {response.text}")

def master(targets):
    for key in targets:
        df = search(key, *targets.get(key, [1, 30]))
        if df is None: break
    else:
        pass
        # notify("Torrent Watch!", "Run Complete")

targets = {
          "Subedaar" : [],
          "Ikkis" : [["2026"]],
          "Border 2" : [["2026"], ["Hunters"]],
          "The Odyssey": [["2026"]],
          "The Social Reckoning": [],
          "Jumanji": [["2026"]],
          "Avengers: Doomsday": [["2026"]],
          }
master(targets)
