from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import json

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
        if self.stream_id == 'SPLASHI': return 'OOPSLA'
        if self.stream_id == 'SPLASHII': return 'Rebase'
        if self.stream_id == 'SPLASHIII': return 'SPLASH'
        assert False, f'Invalid steam: {self.stream_id}'

    @staticmethod
    def from_name(name: str) -> 'Stream':
        if name == 'OOPSLA': return Stream(stream_id='SPLASHI')
        if name == 'Rebase': return Stream(stream_id='SPLASHII')
        if name == 'SPLASH': return Stream(stream_id='SPLASHIII')
        assert False, f'Invalid name: {name}'

@dataclass
class Event:
    name: str
    event_id: str
    stream: Stream
    start: CurrentTime
    end: CurrentTime
    recorded: Optional[str]
    repeat: bool

    @property
    def is_prerecorded_talk(self) -> bool:
        return self.recorded is not None

    @property
    def is_live_talk(self) -> bool:
        return not self.is_prerecorded_talk

    @property
    def authors_display(self) -> str:
        return '[No Authors]'
        # return ', '.join(f'{a[0]} {a[1]}' for a in self.authors)

    @property
    def first_round(self) -> bool:
        return self.start.first_round_of_streaming

    @staticmethod
    def load(data) -> 'Event':
        return Event(
            name = data['name'],
            event_id = data['id'],
            stream = Stream(stream_id=data['stream']),
            start = CurrentTime.parse(data['tstart']),
            end = CurrentTime.parse(data['tend']),
            recorded = data['recorded'],
            repeat = data['repeat'],
        )

def loadAllEvents(json_file: str) -> List[Event]:
    with open(json_file) as f:
        data = json.load(f)
        results = []
        for events in data:
            for e in events[2]:
                results.append(Event.load(e))
        return results