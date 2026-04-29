import requests
import os

from caldav import DAVClient
from datetime import datetime, timedelta, UTC

import uuid

def dispatch(channel, title, message, priority="default", tags="", link=None):
    PLATFORM = os.getenv("PLATFORM")
    headers = {"Title": title, "Priority": priority}

    if tags:
        headers["Tags"] = tags
    if link:
        headers["Click"] = link

    requests.post(
        f"{PLATFORM}/{channel}",
        data=message.encode("utf-8", "ignore"),
        headers=headers
    )

def get_calendar(client, target_name="Upcoming"):
    principal = client.principal()
    calendars = principal.calendars()
    calendar = next(
        (c for c in calendars if c.get_display_name() == target_name),
        None
    )
    return calendar

def format_event(title="test2", due_date = "20260426", details =  "details and link"):
    uid = str(uuid.uuid4())
    now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    due_time = "090001"
    due_date = due_date.replace("-", "")
    alarm_date = (datetime.strptime(due_date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")

    event = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:+//IDN tasks.org//android-150204//EN
BEGIN:VTIMEZONE
TZID:Asia/Kolkata
BEGIN:STANDARD
DTSTART:19420515T000000
RDATE:19451015T000000
TZNAME:IST
TZOFFSETFROM:+0630
TZOFFSETTO:+0530
END:STANDARD
END:VTIMEZONE
BEGIN:VTODO
CREATED:{now}
LAST-MODIFIED:{now}
DESCRIPTION:{details}
DUE;TZID=Asia/Kolkata:{due_date}T{due_time}
PRIORITY:9
SUMMARY:{title}
UID:{uid}
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER;RELATED=END:PT0S
END:VALARM
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER;VALUE=DATE-TIME:{alarm_date}T153000Z
END:VALARM
END:VTODO
END:VCALENDAR"""
    return event

def create_event(calendar_name, title, due_date, details):
    client = DAVClient(
        "https://127.0.0.1:5232",
        username=os.environ["CALDAV_USER"],
        password=os.environ["CALDAV_PASS"],
        ssl_verify_cert=False
    )

    calendar = get_calendar(client, calendar_name)
    event = format_event(title, due_date, details)
    calendar.add_event(event)