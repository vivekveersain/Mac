from lxml import html
import requests
from datetime import date
import pickle
import copy
import os

local_data = {"HRJRA00000892025" : {"posts": [], "next_action":""},
              "HRJRA00000232025" : {"posts": [], "next_action":""},
              "HRJRA00007332024" : {"posts": [], "next_action":""}
              }

HOME = os.environ.get("HOME")
DATA_DIR = f"{HOME}/data/"
FILE = "court.pkl"

def post(title, data, priority = "default", tags = "", link = None):
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan_court",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)

def load_data(local_data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR + FILE, "rb") as f: new_local_data = pickle.load(f)
        local_data.update(new_local_data)
        #print("LOADED!!!")
    except:
        pass 
        #print("LOAD FAILED!!!")
    return local_data

def dump_data(local_data):
    #local_data = {"HRJRA00000892025" : {"posts": [], "next_action":""}}
    try:
        with open(DATA_DIR + FILE, "wb") as f: pickle.dump(local_data, f)
        #print("DUMPED!!!")
    except:
        pass
        #print("DUMP FAILED!!!")

def clean_dates(master_dict):
    for caption in master_dict.keys():
        for key in master_dict[caption]:
            if "Date" in key:
                try:
                    master_dict[caption][key] = ["-".join(x.split("-")[::-1]) for x in master_dict[caption][key]]
                except: pass
    return master_dict

def court_case(cino):
    url = "https://jhajjar.dcourts.gov.in/wp-admin/admin-ajax.php"
    payload = {
        "cino": cino,
        "action": "get_cnr_details",
        "es_ajax_request": "1"
    }
    #print(url, payload)

    response = requests.post(url, data=payload)
    #print(response)
    page = response.json()["data"]
    # Parse HTML
    tree = html.fromstring(page)

    # Select all tables with class 'data-table-1'
    tables = tree.xpath("//table[@class='data-table-1']")

    stacker = ""
    master_dict = {}
    for table in tables:
        caption = table.xpath(".//caption/text()")
        caption = caption[0] if caption else "No caption"
        #print(f"\n--- {caption} ---")
        stacker += f"\n--- {caption} ---\n"

        # Extract headers
        headers = [th.text_content().strip() for th in table.xpath(".//thead//th")]
        if headers:
            #print(headers)
            stacker += str(headers) + "\n"

        # Extract rows with text + links
        rows = []
        for row in table.xpath(".//tbody/tr"):
            cells = []
            for td in row.xpath("./td"):
                link = td.xpath(".//a/@href")
                if link:
                    cells.append({
                        "text": td.text_content().strip(),
                        "link": link[0]
                    })
                else:
                    cells.append(td.text_content().strip())
            rows.append(cells)

        for r in rows:
            #print(r)
            stacker += str(r) + "\n"
        #if caption == "Orders": rows = rows[:-1]
        #master_dict[caption] = {"headers": headers, "rows" : rows}
        master_dict[caption] = dict((head, [row[r] for row in rows ]) for r, head in enumerate(headers))

    master_dict = clean_dates(master_dict)
    return stacker, master_dict

def post_updates(master_dict):
    case_number = master_dict['Case Details']['Registration Number'][0]
    next_date = master_dict['Case Status']['Next Hearing Date'][0]
    order_date = master_dict['Orders']['Order Date'][-1]
    order_link = master_dict['Orders']['Order Details'][-1]["link"]

    master_text = format_case(master_dict)

    post(case_number, data = f"Next Hearing Date:{next_date}\nOrder Date:{order_date}\n\n\n{master_text}", link = order_link)

def next_action_logic(master_dict, posts):
    next_predicted_action = min(dt for dt in master_dict['Case History']['Hearing Date'] if dt not in master_dict['Orders']['Order Date'])
    new_orders = [r for r in master_dict['Orders']['Order Date'] if r not in posts]
    return next_predicted_action, new_orders

def format_case(master_dict):
    lines = []

    # Case Details
    lines.append("📂 CASE DETAILS")
    for key, value in master_dict.get('Case Details', {}).items():
        lines.append(f"{key}: {', '.join(value)}")
    lines.append("")

    # Case Status
    lines.append("📌 CASE STATUS")
    for key, value in master_dict.get('Case Status', {}).items():
        lines.append(f"{key}: {', '.join(value)}")
    lines.append("")

    # Acts
    lines.append("⚖️ ACTS")
    for key, value in master_dict.get('Acts', {}).items():
        lines.append(f"{key}: {', '.join(value)}")
    lines.append("")

    # Case History
    lines.append("📜 CASE HISTORY")
    history = master_dict.get('Case History', {})
    for i in range(len(history.get('Registration Number', []))):
        lines.append(f"{i+1}. Date: {history['Business On Date'][i]['text']}, "
                     f"Judge: {history['Judge'][i]}, "
                     f"Hearing Date: {history['Hearing Date'][i]}, "
                     f"Purpose: {history['Purpose of hearing'][i]}")
    lines.append("")

    # Orders
    lines.append("📝 ORDERS")
    orders = master_dict.get('Orders', {})
    for i in range(len(orders.get('Order Number', []))):
        order_detail = orders['Order Details'][i]['text']
        order_link = orders['Order Details'][i]['link']
        lines.append(f"{i+1}. Order No: {orders['Order Number'][i]}, Date: {orders['Order Date'][i]}, "
                     f"Details: {order_detail} ({order_link})")
    lines.append("")

    # Case Transfer Details
    lines.append("🔄 CASE TRANSFER DETAILS")
    transfer = master_dict.get('Case Transfer Details within Establishment', {})
    for i in range(len(transfer.get('Registration Number', []))):
        lines.append(f"Registration No: {transfer['Registration Number'][i]}, "
                     f"Transfer Date: {transfer['Transfer Date'][i]}, "
                     f"From: {transfer['From Court Number and Judge'][i]}, "
                     f"To: {transfer['To Court Number and Judge'][i]}")
    
    return "\n".join(lines)

today = str(date.today())

local_data = load_data(local_data)
old_copy = copy.deepcopy(local_data)

if True:
    for cino in local_data.keys():
        # print(cino)
        next_action = local_data[cino]["next_action"]
        if next_action <= today:
            try: 
                message, master_dict = court_case(cino)
            except: 
                print("Some Error")
                continue
            print(cino, next_action)
            next_action, new_orders = next_action_logic(master_dict, local_data[cino]["posts"])
            if new_orders: post_updates(master_dict)
            print(next_action)
            local_data[cino]["next_action"] = next_action
            local_data[cino]["posts"] += new_orders
    if local_data != old_copy:
        dump_data(local_data)
