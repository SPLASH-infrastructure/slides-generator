#!/usr/bin/env python3

import splash
from splash.data import Stream
import argparse
from datetime import datetime


parser = argparse.ArgumentParser(description='Generate all filler videos')

parser.add_argument('--stream', type=str, help='Generate fillers only for the given stream. Must oe one of ["SPLASHI", "SPLASHII", "SPLASHIII"].')
parser.add_argument('--time', type=str, help='Generate fillers only for the given time. e.g. 16:20 (--stream must be specified)')
parser.add_argument('--start', type=str, help='Time range limits')
parser.add_argument('--end', type=str, help='Time range limits')

args = parser.parse_args()

# Load all breaks

breaks = splash.data.loadAllBreaks('./data/breaks.json')

# Filter events by arguments

if args.stream is not None:
    # Generate videos for the given stream
    breaks = [ b for b in breaks if b.stream.stream_id == args.stream ]
if args.time is not None:
    # Generate videos for the given start time
    breaks = [ b for b in breaks if b.start.time_display == args.time ]
if args.start is not None:
    start = datetime.strptime(args.start, '%y-%m-%d-%H:%M')
    # Generate videos for the given event id
    breaks = [ b for b in breaks if b.start.time >= start ]
if args.end is not None:
    end = datetime.strptime(args.end, '%y-%m-%d-%H:%M')
    # for e in events: print(e.start.time)
    # Generate videos for the given event id
    breaks = [ b for b in breaks if b.start.time < end ]

breaks = {
    f'{b.start.time_display} {b.end.time_display} {b.stream.stream_id}': b for b in breaks
}

breaks = [ v for v in breaks.values() ]

breaks = sorted(breaks, key=lambda e: e.start.time)

for b in breaks:
    print(b.start.time)
    splash.video.generateFillerVideoForBreak(b)
