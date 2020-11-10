from .keyframe import KeyFrame
from typing import List
import os
from . import config
from datetime import timedelta
from .data import CurrentTime, Stream, Event



def generateFromKeyFrames(frames: List[KeyFrame], video: str):
    dirname = os.path.dirname(video)
    os.system(f'mkdir -p {dirname}')
    ffconcat = os.path.join(dirname, 'in.ffconcat')
    ffconcat_content = 'ffconcat version 1.0\n'
    duration = 0
    for f in frames:
        duration += f.duration
        ffconcat_content += f'file {f.image}\nduration {f.duration}.0\n'
    with open(ffconcat, 'w') as f:
        f.write(ffconcat_content)
    os.system(f'ffmpeg -y -safe 0 -i {ffconcat} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t {duration} -pix_fmt yuv420p {video}')


def __renderKeyFramesAndGenVideo(template: str, outdir: str, basename: str, duration: int, start_time: CurrentTime, env):
    frames = []
    counter = 0
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
    out = os.path.realpath(f'./out/{event.stream.name}')
    env = {
        'event': event,
        'stream': event.stream,
    }
    stream_round = 'A' if event.first_round else 'B'
    if event.is_prerecorded_talk:
        print(f">>> Pre-recorded Talk {event.event_id} " + event.start.time_display + " " + event.end.time_display)
        __renderKeyFramesAndGenVideo('./slides/intro-template.html', out, f'{event.event_id}-{stream_round}-intro', config.INTRO_SECONDS, start_time=event.start, env=env)
        __renderKeyFramesAndGenVideo('./slides/qa-template.html', out, f'{event.event_id}-{stream_round}-qa', config.QA_TRANSITION_SECONDS, start_time=event.start, env=env)
        __renderKeyFramesAndGenVideo('./slides/outro-template.html', out, f'{event.event_id}-{stream_round}-outro', config.OUTRO_SECONDS, start_time=event.start - timedelta(seconds=config.OUTRO_SECONDS), env=env)
    else:
        print(f">>> Live Talk or KeyNotes {event.event_id} " + event.start.time_display + " " + event.end.time_display)
        __renderKeyFramesAndGenVideo('./slides/intro-template.html', out, f'{event.event_id}-{stream_round}-intro', config.INTRO_SECONDS, start_time=event.start, env=env)
        __renderKeyFramesAndGenVideo('./slides/outro-template.html', out, f'{event.event_id}-{stream_round}-outro', config.OUTRO_SECONDS, start_time=event.start - timedelta(seconds=config.OUTRO_SECONDS), env=env)


def generateFillerVideo(stream: Stream, start_time: str):
    minutes = config.FILLER_MINUTES
    # A minute of clock-enabled frame for each 5 minutes
    for i in range(0, minutes, 5):
        time = CurrentTime.parse(start_time, offset=timedelta(minutes=i))
        frame = KeyFrame.render_from_template('./slides/empty-filler.html', f'./out/{stream.name}/fillers/clock-{time.time_display}.png', 5, env={
            'stream': stream,
            'time': time
        })
        generateFromKeyFrames(frames=[frame], video=f'./out/{stream.name}/fillers/clock-{time.time_display}.mp4')
    # One still image video
    frame = KeyFrame.render_from_template('./slides/empty-filler.html', f'./out/{stream.name}/fillers/static-{start_time}.png', 5, env={
        'stream': stream,
        'time': CurrentTime.parse(start_time),
        'no_clock': True,
    })
    generateFromKeyFrames(frames=[frame], video=f'./out/{stream.name}/fillers/static-{start_time}.mp4')

def generateFillerVideosForStream(stream: Stream):
    # We have 12 breaks
    generateFillerVideo(stream, '08:20')
    generateFillerVideo(stream, '10:20')
    generateFillerVideo(stream, '12:20')
    generateFillerVideo(stream, '14:20')
    generateFillerVideo(stream, '16:20')
    generateFillerVideo(stream, '18:20')
    generateFillerVideo(stream, '20:20')
    generateFillerVideo(stream, '22:20')
    generateFillerVideo(stream, '00:20')
    generateFillerVideo(stream, '02:20')
    generateFillerVideo(stream, '04:20')
    generateFillerVideo(stream, '06:20')