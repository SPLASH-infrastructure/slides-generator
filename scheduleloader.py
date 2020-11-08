import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

@dataclass
class LocalTime:
    name: str
    time: datetime

    @property
    def is_active(self) -> bool:
        return self.time.hour >= 7 and self.time.hour < 18

    @property
    def time_display(self) -> str:
        return self.time.strftime('%H:%M')

# The Chicago time for the current generated frame when it is live-streamed.
@dataclass
class CurrentTime:
    time: datetime

    @staticmethod
    def parse(time) -> 'CurrentTime':
        return CurrentTime(time=datetime.strptime(time, '%H:%M'))

    @property
    def first_round_of_streaming(self) -> bool:
        return self.time.hour >= 7 and self.time.hour < 19

    @property
    def background_city(self) -> str:
        t = (self.time.hour, self.time.minute)
        if ( 7, 0) <= t and t < ( 9, 0): return 'Chicago'
        if ( 9, 0) <= t and t < (11, 0): return 'Seattle'
        if (11, 0) <= t and t < (13, 0): return 'Wellington'
        if (13, 0) <= t and t < (15, 0): return 'Paris'
        if (15, 0) <= t and t < (17, 0): return 'Seoul'
        if (17, 0) <= t and t < (19, 0): return 'Rio'
        if (19, 0) <= t and t < (21, 0): return 'New York'
        if (21, 0) <= t and t < (23, 0): return 'Tokyo'
        if (23, 0) <= t or  t < ( 1, 0): return 'Paris'
        if ( 1, 0) <= t and t < ( 3, 0): return 'Sydney'
        if ( 3, 0) <= t and t < ( 5, 0): return 'Beijing'
        if ( 5, 0) <= t and t < ( 7, 0): return 'Delhi'
        assert False, "Unreachable"

    @property
    def background_image(self) -> str:
        t = (self.time.hour, self.time.minute)
        if ( 7, 0) <= t and t < ( 9, 0): return 'breakfast-in-chicago'
        if ( 9, 0) <= t and t < (11, 0): return 'breakfast-in-seattle'
        if (11, 0) <= t and t < (13, 0): return 'breakfast-in-wellington'
        if (13, 0) <= t and t < (15, 0): return 'cocktail-in-paris'
        if (15, 0) <= t and t < (17, 0): return 'breakfast-in-seoul'
        if (17, 0) <= t and t < (19, 0): return 'cocktails-in-rio'
        if (19, 0) <= t and t < (21, 0): return 'cocktails-in-new-york'
        if (21, 0) <= t and t < (23, 0): return 'lunch-in-tokyo'
        if (23, 0) <= t or  t < ( 1, 0): return 'breakfast-in-paris'
        if ( 1, 0) <= t and t < ( 3, 0): return 'cocktails-in-sydney'
        if ( 3, 0) <= t and t < ( 5, 0): return 'dinner-in-beijing'
        if ( 5, 0) <= t and t < ( 7, 0): return 'dinner-in-delhi'
        assert False, "Unreachable"

    @property
    def time_display(self) -> str:
        return self.time.strftime('%H:%M')

    @property
    def local_times(self) -> List[LocalTime]:
        return [
            LocalTime(name="SFO", time=self.time + timedelta(hours=-2)),
            LocalTime(name="CHI", time=self.time + timedelta(hours=0)),
            LocalTime(name="NYC", time=self.time + timedelta(hours=1)),
            LocalTime(name="RIO", time=self.time + timedelta(hours=3)),
            LocalTime(name="LON", time=self.time + timedelta(hours=6)),
            LocalTime(name="PAR", time=self.time + timedelta(hours=7)),
            LocalTime(name="TLV", time=self.time + timedelta(hours=8)),
            LocalTime(name="MOS", time=self.time + timedelta(hours=9)),
            LocalTime(name="DEL", time=self.time + timedelta(hours=11.5)),
            LocalTime(name="PEK", time=self.time + timedelta(hours=14)),
            LocalTime(name="TYO", time=self.time + timedelta(hours=15)),
            LocalTime(name="SYD", time=self.time + timedelta(hours=17)),
            LocalTime(name="AKL", time=self.time + timedelta(hours=19)),
        ]


@dataclass
class ConferenceInfo:
    subevent_id: str
    title: str
    subevent_type: str
    room: str
    date: str
    track: str

    @property
    def room_display(self) -> str:
        return self.room.replace('Online | ', '')

    @staticmethod
    def parse(timeslot) -> 'ConferenceInfo':
        return ConferenceInfo(
            subevent_id = timeslot.find('subevent_id').text,
            title = timeslot.find('title').text,
            room = timeslot.find('room').text,
            date = timeslot.find('date').text,
            subevent_type = timeslot.find('subevent_type').text,
            track = timeslot.find('tracks/track').text,
        )

@dataclass
class ConferenceEvent:
    conference: ConferenceInfo
    event_id: str
    title: str
    room: str
    track: str
    date: str
    start: str # Chicago time
    end: str # Chicago time
    track: str
    authors: List[Tuple[str, str]]

    @property
    def is_keynote(self) -> bool:
        return self.track == "Keynotes"

    @property
    def is_prerecorded_talk(self) -> bool:
        return self.room == "Online | Rebase"

    @property
    def is_live_talk(self) -> bool:
        return self.room == "Online | OOPSLA/ECOOP" \
            or (self.room == "Online | SPLASH" and self.track in [
                "SLE (Software Language Engineering) 2020",
                "GPCE 2020 - 19th International Conference on Generative Programming: Concepts & Experiences",
                "SAS 2020 - 27th Static Analysis Symposium",
                "Dynamic Languages Symposium",
                "SLE (Software Language Engineering) 2020",
                "OOPSLA",
                "Onward! Papers and Essays",
                "Onward! Essays and Papers",
                "ECOOP 2020",
            ])

    @property
    def authors_display(self) -> str:
        return ', '.join(f'{a[0]} {a[1]}' for a in self.authors)

    @staticmethod
    def parse(timeslot, conference) -> Optional['ConferenceEvent']:
        if timeslot.find('event_id') is None: return None
        return ConferenceEvent(
            conference = conference,
            event_id = timeslot.find('event_id').text,
            title = timeslot.find('title').text,
            room = timeslot.find('room').text,
            date = timeslot.find('date').text,
            start = timeslot.find('start_time').text,
            end = timeslot.find('end_time').text,
            track = timeslot.find('tracks/track').text,
            authors = [ (p.find('first_name').text, p.find('last_name').text) for p in timeslot.findall('persons/person')],
        )

def parseSubEvent(root, subevent_id):
    subevent = root.find(f"subevent[subevent_id='{subevent_id}']")
    conference = ConferenceInfo.parse(subevent)
    timeslots = []
    for timeslot in subevent.findall('timeslot'):
        e = ConferenceEvent.parse(timeslot, conference)
        if e is not None:
            timeslots.append(e)
    return conference, timeslots

def getAllSubEventIds(root):
    return [ e.find('subevent_id').text for e in root.findall(f"subevent") if e.find('subevent_id') is not None ]

def loadXML(xml):
    return ET.parse(xml).getroot()