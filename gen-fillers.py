#!/usr/bin/env python3

import splash
from splash.data import Stream
import argparse


parser = argparse.ArgumentParser(description='Generate all filler videos')

parser.add_argument('--stream', type=str, help='Generate fillers only for the given stream. Must oe one of ["OOPSLA", "Rebase", "SPLASH"].')
parser.add_argument('--time', type=str, help='Generate fillers only for the given time. e.g. 16:20 (--stream must be specified)')

args = parser.parse_args()

# Load all breaks

breaks = splash.data.loadAllBreaks('./data/breaks.json')

# Filter events by arguments

if args.stream is not None:
    # Generate videos for the given stream
    breaks = [ b for b in breaks if b.stream.name == args.stream ]
if args.time is not None:
    # Generate videos for the given start time
    breaks = [ b for b in breaks if b.start.time_display == args.time ]

breaks = {
    f'{b.start.time_display} {b.end.time_display} {b.stream.stream_id}': b for b in breaks
}

breaks = [ v for v in breaks.values() ]

for b in breaks:
    splash.video.generateFillerVideoForBreak(b)
