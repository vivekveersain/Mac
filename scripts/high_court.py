import requests
import json
import time
import os
from datetime import datetime, timedelta

HOME = os.environ.get("HOME")
DATA_DIR = f"{HOME}/data/"
ARCHIVE_FILE = f"{DATA_DIR}CWP_archive.json"

BASE_URL = "https://livedb9010.phhc.gov.in/cis_filing/public/judgmentDetails"


def get_api_url(case_no, case_year, case_type="CWP"):
    return f"{BASE_URL}/{case_no}/{case_year}/{case_type}?skip=0&limit=1000"


def get_case_key(case_no, case_year):
    return f"{case_no}_{case_year}"


def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_archive(data):
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fetch_orders(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://new.phhc.gov.in/",
        "Origin": "https://new.phhc.gov.in"
    }

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()


def generate_unique_id(order):
    return f"{order['case_no']}_{order['orderdate']}_{order['pdfname']}"

from postman import dispatch
def post(title, data, priority = "default", tags = "", link = None):
    dispatch("kaptaan_court", title, data, priority, tags, link)

def notify(order):
    # print("\nNew Order Found:")
    # print(json.dumps(order, indent=2))
    title = f'{order["case_type"]}/{order["case_no"]}/{order["case_year"]}'
    data = order['orderdate']
    link = order["order"]
    post(title, data, link = link)

def check_for_new_orders(case_no, case_year, case_type="CWP"):
    # print(f"\n[{datetime.now()}] Checking case {case_no}/{case_year}...")

    api_url = get_api_url(case_no, case_year, case_type)
    case_key = get_case_key(case_no, case_year)

    archive_data = load_archive()

    # Ensure case key exists
    if case_key not in archive_data:
        archive_data[case_key] = []

    existing_ids = set(archive_data[case_key])

    data = fetch_orders(api_url)
    new_found = False

    for order in data:
        oid = generate_unique_id(order)

        if oid not in existing_ids:
            notify(order)
            archive_data[case_key].append(oid)
            new_found = True

    if new_found:
        save_archive(archive_data)
        # print("Archive updated.")
    else:
        pass
        # print("No new orders.")

if __name__ == "__main__":
    cases = [
        {
            "CASE_NO": "39576",
            "CASE_YEAR": "2025",
            "CASE_TYPE": "CWP",
            "Details": "Sector 25 4M plots"
        },
        {
            "CASE_NO": "9278",
            "CASE_YEAR": "2020",
            "CASE_TYPE": "CWP",
            "Details": "600+ MO recruitment"
        },
        # {
        #     "CASE_NO": "20599",
        #     "CASE_YEAR": "2021",
        #     "CASE_TYPE": "CWP"
        # },
        {
            "CASE_NO": "28866",
            "CASE_YEAR": "2024",
            "CASE_TYPE": "CWP",
            "Details": "Rural quota in PG seats, gunjan nehra"
        }
        ]


    for case in cases:
        check_for_new_orders(
            case["CASE_NO"],
            case["CASE_YEAR"],
            case["CASE_TYPE"]
        )