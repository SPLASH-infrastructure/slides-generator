from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import json
from . import config
from . import lookup_breaks
import copy
import xml.etree.ElementTree as ET

SCHEDULE_XML = ET.parse('./data/splash-schedule.xml')

# Local time for each local timezone
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
    def from_unix_timestamp(time: int, offset: timedelta = timedelta()) -> 'CurrentTime':
        return CurrentTime(time=datetime.utcfromtimestamp(time) + offset)

    @staticmethod
    def parse(time: str, offset: timedelta = timedelta()) -> 'CurrentTime':
        if len(time) == 5:
            return CurrentTime(time=datetime.strptime(time, '%H:%M') + offset)
        elif len(time) == 25:
            return CurrentTime(time=datetime.strptime(time, '%Y-%m-%dT%H:%M:%S-06:00') - timedelta(hours=6) + offset)
        else:
            assert False, "Error"

    @property
    def first_round_of_streaming(self) -> bool:
        return self.time.hour >= 7 and self.time.hour < 19

    @property
    def background_city(self) -> str:
        t = (self.time.hour, self.time.minute)
        if ( 7, 0) <= t and t < ( 9, 0): return 'Breakfast in Chicago'
        if ( 9, 0) <= t and t < (11, 0): return 'Breakfast in Seattle'
        if (11, 0) <= t and t < (13, 0): return 'Breakfast in Wellington'
        if (13, 0) <= t and t < (15, 0): return 'Cocktails in Paris'
        if (15, 0) <= t and t < (17, 0): return 'Breakfast in Seoul'
        if (17, 0) <= t and t < (19, 0): return 'Cocktails in Rio'
        if (19, 0) <= t and t < (21, 0): return 'Cocktails in New York'
        if (21, 0) <= t and t < (23, 0): return 'Lunch in Tokyo'
        if (23, 0) <= t or  t < ( 1, 0): return 'Breakfast in Paris'
        if ( 1, 0) <= t and t < ( 3, 0): return 'Cocktails in Sydney'
        if ( 3, 0) <= t and t < ( 5, 0): return 'Dinner in Beijing'
        if ( 5, 0) <= t and t < ( 7, 0): return 'Dinner in Delhi'
        assert False, "Unreachable"

    @property
    def background_image(self) -> str:
        t = (self.time.hour, self.time.minute)
        if ( 7, 0) <= t and t < ( 9, 0): return 'breakfast-in-chicago'
        if ( 9, 0) <= t and t < (11, 0): return 'breakfast-in-seattle'
        if (11, 0) <= t and t < (13, 0): return 'breakfast-in-wellington'
        if (13, 0) <= t and t < (15, 0): return 'cocktails-in-paris'
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
    def datetime_display(self) -> str:
        return self.time.strftime('%m-%d-%H_%M')

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

    def __add__(self, delta: timedelta) -> 'CurrentTime':
        return CurrentTime(time=self.time + delta)

    def __sub__(self, delta: timedelta) -> 'CurrentTime':
        return CurrentTime(time=self.time - delta)


@dataclass
class Stream:
    stream_id: str # One of SPLASHI, SPLASHII, SPLASHIII

    @property
    def name(self) -> str:
        if self.stream_id == 'SPLASHI': return 'SPLASH-I'
        if self.stream_id == 'SPLASHII': return 'SPLASH-II'
        if self.stream_id == 'SPLASHIII': return 'SPLASH-III'
        assert False, f'Invalid steam: {self.stream_id}'

@dataclass
class Event:
    name: str
    event_id: str
    stream: Stream
    start: CurrentTime
    end: CurrentTime
    recorded: Optional[str]
    recorded_duration: float
    authors: str
    has_transition: bool

    @property
    def is_prerecorded_talk(self) -> bool:
        return self.has_transition

    @property
    def prerecorded_talk_has_valid_duration(self) -> bool:
        return self.recorded_duration > 0

    @property
    def is_live_talk(self) -> bool:
        return not self.is_prerecorded_talk

    @property
    def authors_display(self) -> str:
        return self.authors
        # return ', '.join(f'{a[0]} {a[1]}' for a in self.authors)

    @property
    def first_round(self) -> bool:
        return self.start.first_round_of_streaming

    @property
    def is_last_event_before_break(self) -> bool:
        time = self.start.time_display
        if time in config.START_TIME_OF_LAST_EVENT_BEFORE_BREAK: return True
        global BREAKS
        if BREAKS is None:
            BREAKS = loadAllBreaks('data/breaks.json')
        for b in BREAKS:
            if b.stream.stream_id == self.stream.stream_id and self.end.time == b.start.time:
                return True
        return False

    @staticmethod
    def load(data) -> List['Event']:
        e1 = Event(
            name = data['title'],
            event_id = data['id'],
            stream = Stream(stream_id=data['room'][9:].replace('-', '')),
            start = CurrentTime.from_unix_timestamp(data['tstart'], timedelta(hours=-6)),
            end = CurrentTime.from_unix_timestamp(data['tend'], timedelta(hours=-6)),
            recorded = data['has_transition'],
            recorded_duration = data['recorded_duration'],
            authors = data['authors'],
            has_transition = data['has_transition'],
        )
        events = [ e1 ]
        for slot in SCHEDULE_XML.findall(f'*/timeslot'):
            eid = slot.find('event_id')
            if eid is not None and eid.text == e1.event_id:
                if slot.find('start_time').text != e1.start.time_display:
                    start = datetime.strptime(slot.find('date').text + ' ' + slot.find('start_time').text, '%Y/%m/%d %H:%M')
                    end = datetime.strptime(slot.find('end_date').text + ' ' + slot.find('end_time').text, '%Y/%m/%d %H:%M')
                    e2 = copy.deepcopy(e1)
                    e2.start.time = start
                    e2.end.time = end
                    events.append(e2)
        assert len(events) <= 2, events
        return events

EVENTS = None

def loadAllEvents(json_file: str = './data/transitions.json') -> List[Event]:
    assert json_file.endswith('transitions.json')
    global EVENTS
    if EVENTS is not None:
        return EVENTS
    with open(json_file) as f:
        data = json.load(f)
        results = []
        for e in data:
            results += Event.load(e)
        EVENTS = results
        return results

@dataclass
class Break:
    start: CurrentTime
    end: CurrentTime
    stream: Stream
    original_time_range: Tuple[int, int] = (0, 0)

    @property
    def message(self) -> Optional[str]:
        return None
        # return '''
        #     <h1>Note:</h1>
        #     <p>Some announcements here, or some explanations/notifications on demand.</p>
        # '''

    @property
    def is_coffee_break(self) -> bool:
        return self.start.time_display in config.BREAKS

    @property
    def break_kind(self) -> str:
        return lookup_breaks.BREAKS[self.start.time]

    @property
    def session_before_break(self) -> [Event]:
        assert self.is_coffee_break
        global EVENTS
        if EVENTS is None: loadAllEvents()
        assert EVENTS is not None
        session_start = self.start.time - timedelta(minutes=80)
        session_end = self.start.time
        results = [e for e in EVENTS if e.start.time >= session_start and e.start.time < session_end]
        return results

    @property
    def session_after_break(self) -> [Event]:
        assert self.is_coffee_break
        global EVENTS
        if EVENTS is None: loadAllEvents()
        assert EVENTS is not None
        session_start = self.end.time
        session_end = self.end.time + timedelta(minutes=80)
        return [e for e in EVENTS if e.start.time >= session_start and e.start.time < session_end]

BREAKS = None

def loadAllBreaks(json_file: str) -> List[Break]:
    with open(json_file) as f:
        data = json.load(f)
        results = []
        for a in data:
            start = CurrentTime.from_unix_timestamp(a[0], timedelta(hours=-6))
            end = CurrentTime.from_unix_timestamp(a[1], timedelta(hours=-6))
            streams = ['SPLASHI', 'SPLASHII', 'SPLASHIII']
            for e in a[3]:
                streams = [s for s in streams if s != e['stream']]
            for s in streams:
                results.append(Break(
                    start=start,
                    end=end,
                    stream=Stream(stream_id=s),
                    original_time_range=(a[0], a[1]),
                ))
        return results
