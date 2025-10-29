from concurrent.futures import ThreadPoolExecutor
from datetime import date
import os
import pickle
import time

from lxml import html

import requests

DUMP_DIR = "/home/vabarya/data/hsvp/"
TODAY=str(date.today())

#TODAY="2025-09-02"

def get_public_details(post_data, row = 0):

    detail_elements = ['PlotStatus', 'Cancelled', 'Mortgage', 'Resumed', 'BuildingPlanApproved'
                    , 'SanctionDate', 'AllotmentLetterMemoNumber', 'AllotmentDate', 'CourtCase'
                    , 'DefaultPayment', 'Constructed', 'FullyPaid']
    basic_elements = ['Zone', 'Estate Office', 'Urban Estate', 'Sector No.', 'Plot No.', 'Property Category',
                        'Sub Category', 'Allottee Name', "Mobile Number", "Aadhar Number", "Status"]
    

    out = requests.post("https://hsvphry.org.in/Pages/PlotStatusEnquiry", data = post_data, timeout=30)
    tree = html.fromstring(out.text)

    table = tree.xpath('//table[@id="ContentPlaceHolder1_gvPlotList"]')[0]

    data = dict((key, value) for key, value in zip(basic_elements, [r.text for r in table.findall(".//td")[row*11:]]))

    data.pop("Status")
    panel = tree.xpath('//div[@id="ContentPlaceHolder1_pnlPlotDetails"]')[0]

    details = dict((detail_elements[r], inpt.value) for r, inpt in enumerate(panel.findall(".//input")))
    data.update(details)
    return data

def initial_fetch(city, sector, plot_number, params):
    params["ctl00$ContentPlaceHolder1$cmbSectorID"] = sector
    params["ctl00$ContentPlaceHolder1$txtPlotNo"] = plot_number

    headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "Origin": "https://hsvphry.org.in",
        "Priority": "u=0, i",
        "Referer": "https://hsvphry.org.in/Pages/PlotStatusEnquiry",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "TE": "trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0"
    }

    url = "https://hsvphry.org.in/Pages/PlotStatusEnquiry"
    page = requests.post(url, headers = headers, data = params, timeout=30).text
    return page

def _get(city, sector, plot_number, params):
    P = plot_number[-1].upper() == "P"
    try: G = plot_number[-2].upper() == "G"
    except: G = False
    try: S = plot_number[-2].upper() == "S"
    except: S = False

    data = [False]
    text = initial_fetch(city, sector, plot_number, params)
    tree = html.fromstring(text)
    
    table = tree.xpath('//table[@id="ContentPlaceHolder1_gvPlotList"]')[0]
    data = [r.text for r in table.findall(".//td")]

    temp_stack = []
    master_details_stack = []

    if 'No Records Found..' == data[0]:
        try:
            if not P:
                plot_number = plot_number + "P"
                return _get(city, sector, plot_number, params)
            elif P and not G and not S:
                plot_number = plot_number.replace("P", "GP")
                return _get(city, sector, plot_number, params)
            elif P and G and not S:
                plot_number = plot_number.replace("GP", "SP")
                return _get(city, sector, plot_number, params)
        except: pass

    elif data[5] != "Residential":
        try:
            if not P:
                plot_number = plot_number + "P"
                temp_stack, master_details_stack = _get(city, sector, plot_number, params)
            elif P and not G and not S:
                plot_number = plot_number.replace("P", "GP")
                temp_stack, master_details_stack = _get(city, sector, plot_number, params)
            elif P and G and not S:
                plot_number = plot_number.replace("GP", "SP")
                temp_stack, master_details_stack = _get(city, sector, plot_number, params)
        except: pass

    try:
        if data[0]:
            row = 0
            for row in range(len(data)//11):
                line = data[row*11:(row+1)*11]
                if line[7] in ["\xa0", "", " "]: continue
                temp_stack.append(line)

                post_data = {}

                for r in tree.findall(".//input")[:-1]:
                    post_data[r.name] = r.value
                for r in tree.findall(".//select"): 
                    post_data[r.name] = r.value
                post_data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$gvPlotList$ctl0%d$lblStatus" % (row+2)
                
                post_data["__EVENTARGUMENT"] = ""# % row

                master_details = get_public_details(post_data, row)
                master_details_stack.append(master_details)
    except: pass
    return temp_stack, master_details_stack

def master(target):
    try: return _get(target[0], target[1], target[2], target[3])
    except: return master(target)

def get_parameter(urban_estate, r = 0):
    while r < 10:
        try:
            out = requests.get("https://hsvphry.org.in/Pages/PlotStatusEnquiry/", timeout=30)
            break
        except:
            r += 1
            print("Retrying...")

    tree = html.fromstring(out.text)

    data = {}

    for r in tree.findall(".//input")[:-1]: data[r.name] = r.value
    for r in tree.findall(".//select"): data[r.name] = r.value

    data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$cmbUrbanEstateCode"
    data["__EVENTARGUMENT"] = ""
    data["__LASTFOCUS"] = ""

    data["ctl00$ContentPlaceHolder1$cmbUrbanEstateCode"] = urban_estate.split("-")[0]
    data["ctl00$ContentPlaceHolder1$cmbSectorID"] = ""
    data["ctl00$ContentPlaceHolder1$txtPlotNo"] = ""

    out = requests.post("https://hsvphry.org.in/Pages/PlotStatusEnquiry", data = data, timeout=30)
    tree = html.fromstring(out.text)
    
    params = {}

    for r in tree.findall(".//input")[:-1]: params[r.name] = r.value
    for r in tree.findall(".//select"):  params[r.name] = r.value
    
    params["ctl00$ContentPlaceHolder1$btnSearch"] = "Search"
    params["__EVENTTARGET"] = ""
    params["__EVENTARGUMENT"] = ""
    params["__LASTFOCUS"] = ""
    
    return params

def get_existing_knowledge(city, sector):
    try:
        today = TODAY
        folder_path=DUMP_DIR+city+"/"+sector+"/"
        files = os.listdir(folder_path)
        last_file = folder_path+max([r for r in files if r[:-4] != today])
        with open(last_file, "rb") as f: data = pickle.load(f)
        return [r["Plot No."] for r in data]
    except: return []

def fetch(pool, city, sector, limit_proposal = 100, suff_list = [""]):
    today = TODAY
    plot_list = get_existing_knowledge(city, sector)

    targets = []

    limit = 1 + limit_proposal
    for plt in range(1, limit):
        for suff in suff_list:
            plot = suff+str(plt)
            if plot + "P" in plot_list or plot + "p" in plot_list: plot = plot + "P"
            elif plot + "GP" in plot_list or plot + "gp" in plot_list: plot = plot + "GP"
            elif plot + "SP" in plot_list or plot + "sp" in plot_list: plot = plot + "SP"
            targets.append(plot)

    params = get_parameter(city.split("-")[0])

    plots = [(city.split("-")[0], sector, str(r), params.copy()) for r in targets]

    temp_stack = []
    list_of_dicts = []

    total = len(plots)
    r = 0
    start = time.time()

    batches = pool.map(master, plots)
    for lines, master_details in batches:
        for line, master_details_dict in zip(lines, master_details):
            temp_stack.append(line)
            list_of_dicts.append(master_details_dict)
        r += 1
        elapsed = int(time.time() - start)
        print("\r%s / %s > %d/%d in %02d:%02d:%02d" % (city, sector, r, total, elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60), end = "")
    print("")

    if len(list_of_dicts) == 0:
        return None
    
    dump(today, city, sector, list_of_dicts)
    try: 
        #if sector in ["1", "25"]: compare(city, sector)
        compare(city, sector)
    except: pass
    return list_of_dicts

def dump(today, city, sector, list_of_dicts):
    folder_path=DUMP_DIR+city+"/"+sector+"/"
    os.makedirs(folder_path, exist_ok=True)
    file_name = folder_path + str(today) + ".pkl"
    with open(file_name, "wb") as file:
        pickle.dump(list_of_dicts, file)
    return True

def error_check():
    try:
        url = "https://hsvphry.org.in/Pages/PlotStatusEnquiry/"
        page = requests.get(url, timeout=30)
        if page.status_code != 200: return True
        tree = html.fromstring(page.text)
        title = tree.xpath("//title")[0].text
        if "error" in title.lower() or "unavailable" in title.lower(): return True
        else: return False
    except: return True

def to_currency(amount):
    amount_str = f"{amount:.2f}"
    if "." in amount_str:
        integer_part, decimal_part = amount_str.split(".")
        if decimal_part == "00": decimal_part = ""
    else:
        integer_part, decimal_part = amount_str, ""

    # Handle the first group (last 3 digits) and remaining digits in pairs
    n = len(integer_part)
    if n > 3:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        # Group remaining digits in pairs
        pairs = []
        while len(rest) > 2:
            pairs.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            pairs.insert(0, rest)
        integer_part = ",".join(pairs + [last3])
    if decimal_part: formatted = f"{integer_part}.{decimal_part}"
    else: formatted = f"{integer_part}"
    return formatted

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
    if len(data) == 0: return
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan_jack_sparrow_real_estate",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)
    
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

def comp_master(city, sector, latest_data, last_data):
    yesterday_lookup = create_lookup(last_data)
    today_lookup = create_lookup(latest_data)
    stacker = ""
    negs = ""
    # --- Compare data ---
    
    for plot_id, today_entry in today_lookup.items():
        item_ = ""
        negative = False
        yesterday_entry = yesterday_lookup.get(plot_id)
        if not yesterday_entry:
            #print(f"New plot added: {plot_id}")
            stacker += f"\n\nNew plot added: {plot_id} {today_entry['Allottee Name']} {today_entry['Sub Category']}"
            continue

        if sector not in ["1", "25"]: continue
        if sector == "1" and plot_id[2] not in ["2442", "116", "40P"]: continue
        
        # Check for changes
        changes = {}
        for key in today_entry:
            if today_entry[key] != yesterday_entry.get(key):
                changes[key] = {'yesterday': yesterday_entry.get(key), 'today': today_entry[key]}
        
        if changes:
            #print(f"{plot_id}:")
            plot_size = plot_id[4].split('(')[0].strip(' ')
            item_ += f"\n{plot_id[2]}/{plot_id[3][0]}@ {plot_size} >> {today_entry['Allottee Name']}\n"
            for r, (field, change) in enumerate(changes.items()):
                #print(f"    {field}: {change['yesterday']} -> {change['today']}")
                if field == "FullyPaid":
                    if change['yesterday'] < change['today']: 
                        negative = True
                    try: item_ += f"    {field}: {to_currency(change['yesterday'])} -> {to_currency(change['today'])}\n"
                    except: item_ += f"    {field}: {change['yesterday']} -> {change['today']}\n"
                else: item_ += f"    {field}: {change['yesterday']} -> {change['today']}\n"
            if plot_size == "4 Marla" and negative: continue
            if today_entry['PlotStatus'] != "Allotted" and r == 0: continue
            if negative: negs += item_
            else: stacker += item_
    stacker += negs
    if len(stacker) == 0 : return 
    #print(stacker.strip("\n"))
    post(city+ "/" + sector, stacker)

def clean_data(data):
    for i, r in enumerate(data):
        try: cost = int(float(r['FullyPaid']))
        except: cost = 0
        data[i]['FullyPaid'] = cost
    return data

def compare(city, sector):
    today = TODAY
    folder_path=DUMP_DIR+city+"/"+sector+"/"

    files = os.listdir(folder_path)
    last_file = folder_path+max([r for r in files if r[:-4] < today])
    latest_file = folder_path+today+".pkl"

    with open(last_file, "rb") as f: last_data = clean_data(pickle.load(f))
    with open(latest_file, "rb") as f: latest_data = clean_data(pickle.load(f))

    latest_data, changes = pull_unavailable_entries_from_history(latest_data, last_data)
    if changes: dump(today, city, sector, latest_data)
    comp_master(city, sector, latest_data, last_data)

if __name__ == '__main__':
    if error_check(): print("Site Not reachable!")
    else:
        core_count = 2
        master_dict = {"25": (750, [""])
                            , "27-28-26PI": (1600, ["G", ""])
                            , "27-28-26PII": (200, ["F", ""])
                            , "27-28-26PIII": (200, ["E", ""])
                            , "21P": (200, [""])
                            , "1": (3000, [""])
                            , "2P": (2250, [""])}
        #master_dict = {"25": (50*0,[""])}
        #master_dict = {}

        pool = ThreadPoolExecutor(max_workers=core_count)
        for sector in master_dict.keys():
            limit_proposal, suff_list = master_dict[sector]
            if limit_proposal > 0: out = fetch(pool, "UE018-Rohtak", sector, limit_proposal, suff_list)
        
        master_dict = {"JH6": (1440, [""])
                        , "9 Part-A": (250, [""])
                        , "9 Part-B": (1200, [""])}

        for sector in master_dict.keys():
            limit_proposal, suff_list = master_dict[sector]
            if limit_proposal > 0: out = fetch(pool, "UE031-Jhajjar", sector, limit_proposal, suff_list)