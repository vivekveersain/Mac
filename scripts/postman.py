import requests
import os

PLATFORM = os.getenv("PLATFORM")

def dispatch(channel, title, message, priority="default", tags="", link=None):
    headers = {"Title": title, "Priority": priority}

    if tags:
        headers["Tags"] = tags
    if link:
        headers["Click"] = link

    requests.post(
        f"{PLATFORM}/{channel}",
        data=message.encode("latin-1", "ignore"),
        headers=headers
    )