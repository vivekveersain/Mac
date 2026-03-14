import requests
from lxml import html

# import pandas as pd
import pickle
import time
from os.path import expanduser

import subprocess
import json

class Postman:
    def __init__(self):
        self.site_available = False
        headers={
            "Accept": "text/html, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "DNT": "1",
            "Origin": "https://hsvpauction.procure247.com",
            "Referer": "https://hsvpauction.procure247.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
            "X-CSRF-TOKEN": "2650d789-f1f8-41ac-90cb-6a6647a164fe",
            "X-Requested-With": "XMLHttpRequest"}
        cookies={}
        new_headers = self.get_headers()

        headers["X-CSRF-TOKEN"] = new_headers["x-csrf-token"]
        cookies["JSESSIONID"] = new_headers["cookie"].split("=")[-1]
        self.headers = headers
        self.cookies = cookies
        #self.process_headers(headers)

    def process_headers(self, headers):
        key, value = headers.pop("cookie").split("=")
        cookies = {key: value}
        self.headers = headers
        self.cookies = cookies

    def get_headers(self):
        # print("Getting headers...\r", end="")
        r = 0
        while True:
            if r > 10: break
            try:
                out = subprocess.check_output(
                    ["node", expanduser("~")+"/xtras/node/capture.js"]
                )
                data = json.loads(out.decode())
                if "x-csrf-token" in data:
                    self.site_available = True
                    return data
            except Exception as e:
                # # print(e, e.__doc__)
                pass
            r += 1
            time.sleep(1)
    
    def get_last_block(self, page):
        blocks = get_blocks(1, 1)
        for block in blocks:
            data = basic_details(block)
            last_fetch = int(data["id"].split(":")[-1].strip(" "))
            return data, last_fetch
    
        # print("## > Could NOT read blocks!")
        return {}, 0
    
    def get_page(self, url, data = None, mthd = "get", n = 1, pg = 1):
        page = requests.request(mthd, url,
            data=data,
            headers=self.headers,
            cookies=self.cookies,
            auth=(),
        )
        return page
    
    def get_page_(self, url, data = None, mthd = "get", n = None, pg = None):
        return get_page(url, data, mthd, n, pg)

def get_blocks(n = 1000, pg = 1):
    url = "https://hsvpauction.procure247.com/eprocure/ajax/search-auction"
    data='keywrdSearch=&strDate=&location=&farmerName=&moduleType=2&searchType=2&lstType=1&deptID=&totalPages=&xStatus=7&verField=&perPage=%d&currentPage=%d' % (n, pg)
    
    page = postman.get_page(url = url, data = data, mthd = "post", n = n, pg = pg)
    #page = get_page(n, pg)
    tree = html.fromstring(page.text)
    blocks = tree.xpath('//div[@class="eproc-listing-main"]')
    if len(blocks) == 0: blocks = tree.xpath('//div[@class="listing-content"]')
    return blocks

def basic_details(block):
    _id = block.xpath('.//div[@class="index"]/label')[0].text

    brief = block.xpath('.//div[@class="brief"]/p/a')[0]
    link_to_details = brief.attrib["href"]
    brief_text = brief.text

    try:
        loc_data= [r.text_content() for r in block.xpath('.//div[@class="ref-dept"]/div/span')]
        dept = loc_data[0]
        city = loc_data[-1]
    except: dept = city = "X"

    start_date = block.xpath('.//span[@class="start-date"]')[0].text.split("  ")[-1].strip("\t\r\n ")
    end_date = block.xpath('.//span[@class="end-date"]')[0].text.split("  ")[-1].strip("\t\r\n ")

    data = {"id":_id, "link_to_details":link_to_details, "brief_text":brief_text, "dept":dept, "city":city, "start_date":start_date, "end_date":end_date}
    data = dict((key.strip("\t\r\n "), data[key].strip("\t\r\n ")) for key in data.keys())
    return data

def site_available():
    return postman.site_available

def local_read():
    file_name = expanduser("~")+"/data/hsvp/auctions.pkl"
    try: 
        with open(file_name, "rb") as f: last_local = pickle.load(f)
    except: last_local = 0
    return int(last_local)

def last_available():
    blocks = get_blocks(1, 1)
    for block in blocks:
        data = basic_details(block)
        last_fetch = int(data["id"].split(":")[-1].strip(" "))
        return data, last_fetch
    
    # print("## > Could NOT read blocks!")
    return {}, 0

def dump_data(now_available):
    file_name = expanduser("~")+"/data/hsvp/auctions.pkl"
    with open(file_name, "wb") as f: pickle.dump(str(now_available), f)

def post(title, data, priority = "default", tags = "", link = None):
    if len(data) == 0: return
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan_jack_sparrow_real_estate",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)

def master_function(city, sectors):
    if site_available():
        l_avail_data, now_available = last_available()
        last_pull = local_read()
        new_blocks = now_available - last_pull
        if new_blocks > 0: 
            dump_data(now_available)
            post("New Auctions Available!", str(new_blocks) + " new auctions found!!")
        # else: 
        #     post("No Auctions Available!", str(new_blocks) + " new auctions found!!")
    else:
        pass
        # print("Site NOT available!!!")



interested_auction = "rohtak:25,27"

city, sectors = interested_auction.split(":")
sectors = sectors.split(",")

postman = Postman()
final_df = master_function(city, sectors)