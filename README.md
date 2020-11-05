# Design

1. Given a schedule file in XML format, and a subevent id
2. This script parses it, and extract all timeslots for this subevent id
3. For each timeslot, generate a Intro video, a QA video and an Exit video.
   1. _slides/*-template.html_ contains html templates for these three slides
   2. This python script renders the templates into still images
      * Render once for each _different_ video frame.
      * The only thing that can change is the clock image (or text). The clock changes every minute.
      * For video < 1min, we only need one frame (no clock updates)
      * For vidoe > 1min, we then need to render the template multiple times, one for each minute.
   3. Then the script generates slide videos from the images

# Install

MacOS: `bash ./setup-macos.h`
Ubuntu: `bash ./setup-linux.h`

# Run:

`python3 ./gen.py <subevent-id>`