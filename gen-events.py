#!/usr/bin/env python3

import splash
import argparse


parser = argparse.ArgumentParser(description='Generate all event splash videos')

parser.add_argument('--stream', type=str, help='Generate splash videos only for the given stream. Must oe one of ["OOPSLA", "Rebase", "SPLASH"].')
parser.add_argument('--event', type=str, help='Generate splash videos only for the given event-id. (--stream must be specified)')

args = parser.parse_args()

# Load all events

events = splash.data.loadAllEvents('./data/schedule.json')

print(len(events))
# Filter events by arguments

if args.stream is not None:
    # Generate videos for the given stream
    events = [ e for e in events if e.stream.name == args.stream ]
if args.event is not None:
    # Generate videos for the given event id
    events = [ e for e in events if e.event_id == args.event ]

# Generate
print(events)
for e in events:
    splash.video.generateVideoForEvent(e)
