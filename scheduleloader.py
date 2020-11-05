import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import *


@dataclass
class ConferenceInfo:
    subevent_id: str
    title: str
    subevent_type: str
    room: str
    date: str
    track: str

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
    start: str
    end: str
    track: str
    authors: List[Tuple[str, str]]

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

def parseSubEvent(xml, subevent_id):
    tree = ET.parse(xml)
    root = tree.getroot()
    subevent = root.find(f"subevent[subevent_id='{subevent_id}']")
    conference = ConferenceInfo.parse(subevent)
    timeslots = []
    for timeslot in subevent.findall('timeslot'):
        e = ConferenceEvent.parse(timeslot, conference)
        if e is not None:
            timeslots.append(e)
    return timeslots

# print(parseSubEvent('./data/splash-schedule.xml', 'c49b3977-bf78-4796-930d-b360d8899600'))