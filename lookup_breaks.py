#!/usr/bin/env python3
from bs4 import BeautifulSoup
from datetime import timezone, datetime, timedelta
import json

UTC = timezone(timedelta())


class Session:
    def __init__(self,date, start,end,track, title, room):
        self.start = Session.parse_chicago_time(date, start)
        self.end = Session.parse_chicago_time(date, end)
        if self.end < self.start:
            self.end += timedelta(days=1)
        self.track = track
        self.title = title
        self.room = Session.canonical_room(room)

    @staticmethod
    def canonical_room(room):
        # "Online | SPLASH-II" into "SPLASHII"
        return "".join(room.split()[-1].split("-"))

    @staticmethod
    def parse_chicago_time(date_raw, time_raw) -> datetime:
        # date: 2020/11/19
        # time: 22:00
        return datetime.strptime(
            f"{date_raw} {time_raw} -0600",
            "%Y/%m/%d %H:%M %z"
        ).astimezone(UTC)

    def __str__(self) -> str:
        return f"[{self.room}] {self.track}\n\t{self.title}\n\t{self.start}~{self.end}"

class Break:
    def __init__(self, start, end, streams):
        self.start = Break.from_utc_timestamp(start)
        self.end = Break.from_utc_timestamp(end)
        self.streams = streams
        self.streams.sort()

    @staticmethod
    def from_utc_timestamp(epoch):
        return datetime.fromtimestamp(epoch).astimezone(UTC)

def load_data():
    SCHEDULE_FILE: str = "./data/splash-schedule.xml"
    BREAKS_FILE: str = "./data/breaks.json"

    with open(SCHEDULE_FILE) as fd:
        schedule = BeautifulSoup(fd.read(), "xml")

    with open(BREAKS_FILE) as fd:
        breaks = json.load(fd)

    return schedule, breaks

def parse_schedule(schedule):
    sessions = []

    for session in schedule.event.find_all('subevent'):
        # The first time slot span the entire session
        timeslot = session.timeslot
        session = Session(
            timeslot.date.string,
            timeslot.start_time.string,
            timeslot.end_time.string,
            session.tracks.track.string,
            session.title.string,
            session.timeslot.room.string
        )
        sessions.append(session)
    return sessions

def parse_breaks(breaks):
    results = []
    for b in breaks:
        results.append(Break(b[0], b[1], b[2]))
    return results

def print_csv(sessions, breaks):
    print("start_time,end_time,streams,type")
    for b in breaks:
        streams = "/".join(b.streams)
        print(f"{b.start},{b.end},{streams},", end="")
        matches = []
        for s in sessions:
            if s.start == b.start and s.end == b.end:
                matches.append(s)
        if matches:        
            for m in matches:
                print(f"{m.title}/", end="")
            print()
            continue
        # Coffee break following
        print("Coffee after ", end="")
        for s in sessions:
            if s.room in b.streams and s.end == b.start:
                print(f"{s.title}/", end="")
        print()

def main():
    schedule, raw_breaks = load_data()
    sessions = parse_schedule(schedule)
    breaks = parse_breaks(raw_breaks)
    print_csv(sessions, breaks)

if __name__ == "__main__":
    main()