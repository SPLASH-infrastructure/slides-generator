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

for b in breaks:
    if b.is_coffee_break:
        assert len([x for x in breaks if x.start.time == b.start.time and x.stream.stream_id == 'SPLASHI']) == 1
        assert len([x for x in breaks if x.start.time == b.start.time and x.stream.stream_id == 'SPLASHII']) == 1
        assert len([x for x in breaks if x.start.time == b.start.time and x.stream.stream_id == 'SPLASHIII']) == 1

# Filter events by arguments

if args.stream is not None:
    # Generate videos for the given stream
    breaks = [ b for b in breaks if b.stream.stream_id == args.stream ]
if args.time is not None:
    start = datetime.strptime(args.time, '%y-%m-%d-%H:%M')
    # Generate videos for the given start time
    breaks = [ b for b in breaks if b.start.time == start ]
if args.start is not None:
    start = datetime.strptime(args.start, '%y-%m-%d-%H:%M')
    # Generate videos for the given event id
    breaks = [ b for b in breaks if b.start.time >= start ]
if args.end is not None:
    end = datetime.strptime(args.end, '%y-%m-%d-%H:%M')
    # for e in events: print(e.start.time)
    # Generate videos for the given event id
    breaks = [ b for b in breaks if b.start.time < end ]

breaks = sorted(breaks, key=lambda e: e.start.time)

for b in breaks:
    print(b.start.time, b.original_time_range, b.stream.stream_id)
    splash.video.generateFillerVideoForBreak(b)
