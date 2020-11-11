#!/usr/bin/env python3

import splash
import argparse
from datetime import datetime


parser = argparse.ArgumentParser(description='Generate all event splash videos')

parser.add_argument('--stream', type=str, help='Generate splash videos only for the given stream. Must oe one of ["OOPSLA", "Rebase", "SPLASH"].')
parser.add_argument('--event', type=str, help='Generate splash videos only for the given event-id. (--stream must be specified)')
parser.add_argument('--start', type=str, help='Time range limits')
parser.add_argument('--end', type=str, help='Time range limits')

args = parser.parse_args()

# Load all events

events = splash.data.loadAllEvents('./data/transitions.json')

print(len(events))
# Filter events by arguments

if args.stream is not None:
    # Generate videos for the given stream
    events = [ e for e in events if e.stream.stream_id == args.stream ]
if args.event is not None:
    # Generate videos for the given event id
    events = [ e for e in events if e.event_id == args.event ]
if args.start is not None:
    start = datetime.strptime(args.start, '%y-%m-%d-%H:%M')
    # Generate videos for the given event id
    events = [ e for e in events if e.start.time >= start ]
if args.end is not None:
    end = datetime.strptime(args.end, '%y-%m-%d-%H:%M')
    # for e in events: print(e.start.time)
    # Generate videos for the given event id
    events = [ e for e in events if e.end.time <= end ]

# Generate
# print(events)
for e in events:
    print(e.start.time, e.first_round, e.name)
    splash.video.generateVideoForEvent(e)

