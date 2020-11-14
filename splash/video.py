from .keyframe import KeyFrame
from typing import List
import os
from . import config
from datetime import timedelta
from .data import CurrentTime, Stream, Event, Break
import copy


def generateFromKeyFrames(frames: List[KeyFrame], video: str):
    dirname = os.path.dirname(video)
    os.system(f'mkdir -p {dirname}')
    ffconcat = os.path.join(dirname, 'in.ffconcat')
    ffconcat_content = 'ffconcat version 1.0\n'
    duration = 0
    assert len(frames) == 1
    f = frames[0]
    os.system(f'ffmpeg -y -loop 1 -framerate 30 -i {f.image} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t {f.duration} -pix_fmt yuv420p {video}')
    assert os.path.exists(video)


def __renderKeyFramesAndGenVideo(template: str, outdir: str, basename: str, duration: int, start_time: CurrentTime, env):
    frames = []
    counter = 0
    if config.SKIP_EXISTING and os.path.exists(f'{outdir}/{basename}.mp4'):
        print(f'Skip: {outdir}/{basename}.mp4')
        return
    for i in range(0, duration, 60):
        time = start_time + timedelta(seconds=i)
        env['time'] = time
        counter += 1
        d = 60 if i + 60 <= duration else duration - i
        frame = KeyFrame.render_from_template(
            template=template,
            image=f'{outdir}/{basename}-{counter:03}.png',
            duration=d,
            env=env,
        )
        frames.append(frame)
    if not config.GENERATE_IMAGE_ONLY:
        generateFromKeyFrames(frames=frames, video=f'{outdir}/{basename}.mp4')



def generateVideoForEvent(event: Event):
    out = os.path.realpath(f'./out/{event.stream.stream_id}')
    env = {
        'event': event,
        'stream': event.stream,
    }
    stream_round = 'A' if event.first_round else 'B'
    if event.is_prerecorded_talk:
        print(f">>> Pre-recorded Talk {event.event_id} " + event.start.time_display + " " + event.end.time_display)
        __renderKeyFramesAndGenVideo('./slides/intro-template.html', out, f'{event.event_id}-{stream_round}-opening', config.INTRO_SECONDS, start_time=event.start, env=env)
        __renderKeyFramesAndGenVideo('./slides/outro-template.html', out, f'{event.event_id}-{stream_round}-closing', config.OUTRO_SECONDS, start_time=event.end - timedelta(seconds=config.OUTRO_SECONDS), env=env)
        env2 = copy.deepcopy(env)
        if event.is_prerecorded_talk and not event.prerecorded_talk_has_valid_duration:
            env2['no_clock'] = True
        __renderKeyFramesAndGenVideo('./slides/qa-template.html', out, f'{event.event_id}-{stream_round}-transition', config.QA_TRANSITION_SECONDS, start_time=event.start + timedelta(seconds=event.recorded_duration), env=env2)
    else:
        print(f">>> Live Talk or KeyNotes {event.event_id} " + event.start.time_display + " " + event.end.time_display)
        __renderKeyFramesAndGenVideo('./slides/intro-template.html', out, f'{event.event_id}-{stream_round}-opening', config.INTRO_SECONDS, start_time=event.start, env=env)
        __renderKeyFramesAndGenVideo('./slides/outro-template.html', out, f'{event.event_id}-{stream_round}-closing', config.OUTRO_SECONDS, start_time=event.end - timedelta(seconds=config.OUTRO_SECONDS), env=env)


def generateFillerVideoForBreak(b: Break):
    stream = b.stream
    start_time = b.start
    out_dir = f'./out/{stream.stream_id}/fillers'
    if config.SKIP_EXISTING and os.path.exists(f'{out_dir}/static-{start_time.time_display}.mp4'):
        print(f'Skip: {out_dir}/static-{start_time.time_display}.mp4')
        return
    minutes = int((b.end.time - start_time.time).total_seconds() / 60)
    # A minute of clock-enabled frame for each 5 minutes
    for i in range(0, minutes, 5):
        time = start_time + timedelta(minutes=i)
        frame = KeyFrame.render_from_template('./slides/empty-filler.html', f'{out_dir}/clock-{time.datetime_display}.png', 1, env={
            'stream': stream,
            'brk': b,
            'time': time
        })
        if not config.GENERATE_IMAGE_ONLY:
            generateFromKeyFrames(frames=[frame], video=f'{out_dir}/clock-{time.datetime_display}.mp4')
    # One still image video
    frame = KeyFrame.render_from_template('./slides/empty-filler.html', f'{out_dir}/static-{start_time.datetime_display}.png', 1, env={
        'stream': stream,
        'time': start_time,
        'brk': b,
        'no_clock': True,
    })
    if not config.GENERATE_IMAGE_ONLY:
        generateFromKeyFrames(frames=[frame], video=f'{out_dir}/static-{start_time.time_display}.mp4')
