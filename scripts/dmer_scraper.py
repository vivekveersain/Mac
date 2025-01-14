import requests
from lxml import html
import pickle
import time

import os
os.chdir(os.path.expanduser("~") + "/storage/downloads/scripts/")
local_data_file = "dmer_scraper.pkl"

def post(title, data, priority = "default", tags = "", link = None):
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)

try:
    with open(local_data_file, "rb") as f: local_data = pickle.load(f)
except:
    post("DMER Scrapper", "Some problem in local read!")
    local_data = {}

flag = False
try:
    stack = local_data.get("1", []).copy()
    pinged_data = local_data.get("1", [])
    page = requests.get("https://dmer.haryana.gov.in/", verify=False)
    if page.ok:
        tree = html.fromstring(page.text)
        table = tree.xpath( "/html/body/section[3]/div/div/div[2]/div/div[1]/div/div/ul/li")

        for row in table[::-1]:
            element = row.findall(".//a")[0]
            date = row.findall(".//td[1]")[0].text_content().encode('latin-1', errors='ignore').decode()
            text = element.text.encode('latin-1', errors='ignore').decode()
            link = element.attrib["href"].encode('latin-1', errors='ignore').decode()
            unq = "> ".join([date, text, link])
            if unq not in pinged_data:
                flag = True
                post(date + "> " + text, text + "\n" + link + "\n\n"  + "https://dmer.haryana.gov.in/", link = link, priority="high")
                pinged_data = [unq] + pinged_data
            if flag: 
                local_data["1"] = pinged_data

except:
    post("DMER Scrapper", "Some problem in the first pass!")
    local_data["1"] = stack

try:
    pinged_data = local_data.get("2", 15)

    data = requests.get("https://hryapi.online-counselling.co.in/v1/api/notifications",
                            headers={
                                "Accept": "application/json",
                                "Accept-Encoding": "gzip, deflate, br, zstd",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Connection": "keep-alive",
                                "Content-Type": "application/json",
                                "DNT": "1",
                                "Origin": "https://hry.online-counselling.co.in",
                                "Priority": "u=4",
                                "Referer": "https://hry.online-counselling.co.in/",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-site",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
                            },
                            cookies={},
                            auth=(),
                        )
    
    if data.ok:
        data = data.json()

        for row in data["body"]["notice"][::-1]:
            if row["id"] > pinged_data:
                flag = True
                pinged_data = row["id"]
                title = row["publishDate"].encode('latin-1', errors='ignore').decode() + "> " + row["subject"].encode('latin-1', errors='ignore').decode()
                body = row["content"].encode('latin-1', errors='ignore').decode() + "\n\n" + str(row)
                link = row["extension"].encode('latin-1', errors='ignore').decode()
                post(title, body + "\n\n" + link + "\n\n"  + "https://dmer.haryana.gov.in/", link = link, priority="high")
                time.sleep(1)

        if flag: local_data["2"] = pinged_data
except Exception as e:
    post("DMER Scrapper", "Some problem in the second pass!\n%s \n %s" % (e, e.__doc__))

if flag:
    with open(local_data_file, "wb") as f: pickle.dump(local_data, f)

#post("Run complete", "Done!!!")
with open("last_run.txt", "a") as f: f.write(time.ctime() + "\n")
