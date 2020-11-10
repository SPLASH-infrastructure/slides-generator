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
        * _unimplemented_
   3. Then the script generates slide videos from the images

# Install

MacOS: `bash ./setup-macos.h`

Ubuntu: `bash ./setup-linux.h`

# Run:

Generate splash videos:

* For all events in all streams: `./gen-events.py`
* For one stream: `./gen-events.py --steam=OOPSLA`
* For one event: `./gen-events.py --stream=OOPSLA --event=5d1aeb28-75c6-4924-8e7a-5cbbe33cfacd`

Generate fillers:

* For all streams: `./gen-fillers.py`
* For one stream: `./gen-fillers.py --stream=OOPSLA`
* For one break: `./gen-fillers.py --stream=OOPSLA --time=16:30`

# Outout

```
out/
    OOPSLA/
        fillers/
            clock-16:30.mp4
            clock-16:35.mp4
            ...
            clock-17:05.mp4
            static-16:30.mp4
        <event-id>-A-intro.mp4
        <event-id>-A-qa.mp4
        <event-id>-A-outro.mp4
        <event-id>-B-intro.mp4
        <event-id>-B-qa.mp4
        <event-id>-B-outro.mp4
```

`A` means this video is used for the first round of 12-hours streaming.

`B` means the second round of streaming.

# TODO

- [x] Keynotes get filtered out? (because no `event_id` present)
- [x] Styles
- [x] 12 Background images
- [x] Location name in top right corner
- [x] Display times for 13 different time zones
- [x] Top left corner: current stream
- [x] Better sponsor logos
- [ ] Display auther names
- [ ] Potential corner cases?
- [ ] Calculate time for qa-transition videos
- [ ] Output naming convention

_Low Priority:_

- [ ] Fade-in animation for outro videos
- [ ] High-resolution images
