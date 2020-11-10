#!/usr/bin/env python3

import splash
from splash.data import Stream
import argparse


parser = argparse.ArgumentParser(description='Generate all filler videos')

parser.add_argument('--stream', type=str, help='Generate fillers only for the given stream. Must oe one of ["OOPSLA", "Rebase", "SPLASH"].')
parser.add_argument('--time', type=str, help='Generate fillers only for the given time. e.g. 16:20 (--stream must be specified)')

args = parser.parse_args()

if args.stream is None:
    # Generate all fillers for all three streams
    for stream in ['OOPSLA', 'Rebase', 'SPLASH']:
        splash.video.generateFillerVideosForStream(stream=Stream.from_name(stream))
elif args.time is None:
    # Generate all fillers for the given stream
    splash.video.generateFillerVideosForStream(stream=Stream.from_name(args.stream))
else:
    # Generate filler for the given stream and time
    splash.video.generateFillerVideo(stream=Stream.from_name(args.stream), start_time=args.time)
