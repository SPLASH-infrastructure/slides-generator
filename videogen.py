import tempfile
import os
import os.path
from datetime import timedelta, datetime
from jinja2 import FileSystemLoader, Environment
from scheduleloader import ConferenceEvent, ConferenceInfo, CurrentTime
from dataclasses import dataclass
from typing import List

def htmlToPNG(html, png, env):
    templateLoader = FileSystemLoader(searchpath=os.path.dirname(html))
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(os.path.basename(html))
    with open('./slides/.temp.html', 'w') as out_file:
        out_file.write(template.render(**env))
    os.system(f'wkhtmltoimage --enable-local-file-access --disable-smart-width --height 1080 --width 1960 ./slides/.temp.html {png}')
    return png

@dataclass
class Frame:
    image: str
    duration: int # seconds

    @staticmethod
    def render_from_template(template: str, image: str, duration: int, env) -> 'Frame':
        dirname = os.path.dirname(image)
        os.system(f'mkdir -p {dirname}')
        htmlToPNG(template, image, env)
        return Frame(image=os.path.realpath(image), duration=duration)

def stillImageToVideo(frames: List[Frame], video: str):
    ffconcat = os.path.join(os.path.dirname(video), 'in.ffconcat')
    ffconcat_content = 'ffconcat version 1.0\n'
    duration = 0
    for f in frames:
        duration += f.duration
        ffconcat_content += f'file {f.image}\nduration {f.duration}.0\n'
    with open(ffconcat, 'w') as f:
        f.write(ffconcat_content)
    os.system(f'ffmpeg -y -safe 0 -i {ffconcat} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t {duration} -pix_fmt yuv420p {video}')

def generateFillerVideoForOneBreak(room: str, start_time: str, duration_minutes=40):
    # A minute of clock-enabled frame for each 5 minutes
    for i in range(0, duration_minutes, 5):
        time = CurrentTime.parse(start_time, offset=timedelta(minutes=i))
        frame = Frame.render_from_template('./slides/empty-filler.html', f'./out/fillers/{room}/clock-{time.time_display}.png', 5, env={
            'conference': ConferenceInfo(subevent_id='', title=room, subevent_type='', room=room, date='', track=''),
            'time': time
        })
        stillImageToVideo(frames=[frame], video=f'./out/fillers/{room}/clock-{time.time_display}.mp4')
    # One still image video
    frame = Frame.render_from_template('./slides/empty-filler.html', f'./out/fillers/{room}/static-{start_time}.png', 5, env={
        'conference': ConferenceInfo(subevent_id='', title=room, subevent_type='', room=room, date='', track=''),
        'time': CurrentTime.parse(start_time),
        'no_clock': True,
    })
    stillImageToVideo(frames=[frame], video=f'./out/fillers/{room}/static-{start_time}.mp4')

def generateFillerVideos(room: str):
    # We have 12 breaks
    generateFillerVideoForOneBreak(room, '08:20')
    generateFillerVideoForOneBreak(room, '10:20')
    generateFillerVideoForOneBreak(room, '12:20')
    generateFillerVideoForOneBreak(room, '14:20')
    generateFillerVideoForOneBreak(room, '16:20')
    generateFillerVideoForOneBreak(room, '18:20')
    generateFillerVideoForOneBreak(room, '20:20')
    generateFillerVideoForOneBreak(room, '22:20')
    generateFillerVideoForOneBreak(room, '00:20')
    generateFillerVideoForOneBreak(room, '02:20')
    generateFillerVideoForOneBreak(room, '04:20')
    generateFillerVideoForOneBreak(room, '06:20')

def generate(template: str, outdir: str, image: str, video: str, duration: int, start_time: CurrentTime, env, image_only=False):
    frames = []
    counter = 0
    for i in range(0, duration, 60):
        time = start_time + timedelta(seconds=i)
        env['time'] = time
        imgname = f'{outdir}/{image}-{counter:03}.png'
        counter += 1
        htmlToPNG(template, imgname, env)
        d = 60 if i + 60 <= duration else duration - i
        frames.append(Frame(image=imgname, duration=d))
    if not image_only:
        stillImageToVideo(frames=frames, video=f'{outdir}/{video}')

# Generate videos from a timeslot
def generateVideoFromEvent(event: ConferenceEvent, duration, image_only=False):
    out = f'./out/{event.conference.subevent_id}/{event.event_id}'
    os.system(f'mkdir -p {out}')
    out = os.path.realpath(out)
    env = {
        'event': event, 'conference': event.conference
    }
    if event.is_prerecorded_talk:
        print(f">>> Pre-recorded Talk {event.event_id} " + event.start + " " + event.end)
        generate('./slides/intro-template.html', out, 'precorded-talk-intro', 'precorded-talk-intro.mp4', duration[0], image_only=image_only, start_time=CurrentTime.parse(event.start), env=env)
        generate('./slides/qa-template.html', out, 'precorded-talk-qa', 'precorded-talk-qa.mp4', duration[1], image_only=image_only, start_time=CurrentTime.parse(event.start), env=env)
        generate('./slides/exit-template.html', out, 'precorded-talk-exit', 'precorded-talk-exit.mp4', duration[2], image_only=image_only, start_time=CurrentTime.parse(event.start, offset=timedelta(seconds=duration[2])), env=env)
    elif event.is_live_talk:
        print(f">>> Live Talk {event.event_id} " + event.start + " " + event.end)
        generate('./slides/intro-template.html', out, 'live-intro', 'live-intro.mp4', duration[0], image_only=image_only, start_time=CurrentTime.parse(event.start), env=env)
        generate('./slides/exit-template.html', out, 'live-exit', 'live-exit.mp4', duration[2], image_only=image_only, start_time=CurrentTime.parse(event.start, offset=timedelta(seconds=duration[2])), env=env)
    elif event.is_keynote:
        print(f">>> Keynotes {event.event_id} " + event.start + " " + event.end)
        generate('./slides/intro-template.html', out, 'keynote-intro', 'keynote-intro.mp4', duration[0], image_only=image_only, start_time=CurrentTime.parse(event.start), env=env)
        generate('./slides/qa-break-template.html', out, 'keynote-qa', 'keynote-qa.mp4', duration[2], image_only=image_only, start_time=CurrentTime.parse(event.start, offset=timedelta(seconds=duration[2])), env=env)
    else:
        print(f'Unhandled: {event}')