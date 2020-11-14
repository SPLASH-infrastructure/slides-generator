#!/usr/bin/env python3
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import json
import bisect
from . import data
SCHEDULE_FILE: str = "./data/splash-schedule.xml"
BREAKS_FILE: str = "./data/breaks.json"

with open(SCHEDULE_FILE) as fd:
    schedule = BeautifulSoup(fd.read(), "xml")

with open(BREAKS_FILE) as fd:
    breaks = json.load(fd)

sessions = []

def parse_chicago_time(date_raw, time_raw):
    # date: 2020/11/19
    # time: 22:00
    return datetime.strptime(f"{date_raw} {time_raw} -0600", "%Y/%m/%d %H:%M %z")

for session in schedule.event.find_all('subevent'):
    title = session.title.string
    track = session.tracks.track.string
    # The first time slot span the entire session
    timeslot = session.timeslot
    start_time = parse_chicago_time(timeslot.date.string, timeslot.start_time.string)
    end_time = parse_chicago_time(timeslot.date.string, timeslot.end_time.string)
    if end_time < start_time:
        # event goes into the next day
        end_time += timedelta(days=1)
    assert end_time > start_time
    sessions.append((
        int(start_time.timestamp()),
        int(end_time.timestamp()),
        title,
        track
    ))

sessions.sort(key=lambda x: (x[0], x[1])) # sort by start time and end time

BREAKS = {}
BREAK_KINDS = set()

for brk in breaks:
    start_time = brk[0]
    end_time = brk[1]
    # print(f"Break {start_time} {end_time}: ", end="")
    matches = []
    for s in sessions:
        if s[0] == start_time and s[1] == end_time:
            matches.append(s)
    if matches:
        for m in matches:
            BREAKS[data.CurrentTime.from_unix_timestamp(start_time, timedelta(hours=-6)).time] = m[3]
            BREAK_KINDS.add(m[3])
            # print('x ', data.CurrentTime.from_unix_timestamp(start_time, timedelta(hours=-6)), m[3])
            # print(f"[{m[3]}] {m[2]}, ", end=" ")
    else:
        # print('y ', data.CurrentTime.from_unix_timestamp(start_time, timedelta(hours=-6)), "Coffee break")
        BREAKS[data.CurrentTime.from_unix_timestamp(start_time, timedelta(hours=-6)).time] = "Coffee break"
        BREAK_KINDS.add("Coffee break")
        # print("Coffee break", end="")
    # print()
print(BREAK_KINDS)
# def get