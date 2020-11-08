import tempfile
import os
import os.path
from jinja2 import FileSystemLoader, Environment
from scheduleloader import ConferenceEvent, ConferenceInfo, CurrentTime


def htmlToPNG(html, png, env):
    templateLoader = FileSystemLoader(searchpath=os.path.dirname(html))
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(os.path.basename(html))
    with open('./slides/.temp.html', 'w') as out_file:
        out_file.write(template.render(**env))
    os.system(f'wkhtmltoimage --enable-local-file-access --disable-smart-width --height 1080 --width 1960 ./slides/.temp.html {png}')
    return png

def stillImageToVideo(image, video, duration):
    os.system(f'ffmpeg -y -loop 1 -framerate 30 -i {image} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" -g 60 -c:v libx264 -r 30 -t {duration} -pix_fmt yuv420p {video}')

def generateFillerVideo(conference: ConferenceInfo, duration, image_only=False):
    out = f'./out/{conference.subevent_id}'
    os.system(f'mkdir -p {out}')
    image = f'{out}/filler.png'
    htmlToPNG('./slides/empty-filler.html', image, { 'conference': conference, 'time': CurrentTime.parse('00:00') })
    if not image_only: stillImageToVideo(image=image, video=f'{out}/filler.mp4', duration=duration)

def genVideo(template, outdir, image, video, duration, env, image_only=False):
    htmlToPNG(template, f'{outdir}/{image}', env)
    if not image_only: stillImageToVideo(image=f'{outdir}/{image}', video=f'{outdir}/{video}', duration=duration)

# Generate videos from a timeslot
def generateVideoFromEvent(event: ConferenceEvent, duration, image_only=False):
    out = f'./out/{event.conference.subevent_id}/{event.event_id}'
    os.system(f'mkdir -p {out}')
    if event.is_prerecorded_talk:
        print(f">>> Pre-recorded Talk {event.event_id} " + event.start + " " + event.end)
        genVideo('./slides/intro-template.html', out, 'precorded-talk-intro-000.png', 'precorded-talk-intro.mp4', duration[0], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
        genVideo('./slides/qa-template.html', out, 'precorded-talk-qa-000.png', 'precorded-talk-qa.mp4', duration[1], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
        genVideo('./slides/exit-template.html', out, 'precorded-talk-exit-000.png', 'precorded-talk-exit.mp4', duration[2], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
    elif event.is_live_talk:
        print(f">>> Live Talk {event.event_id} " + event.start + " " + event.end)
        genVideo('./slides/intro-template.html', out, 'live-intro-000.png', 'live-intro.mp4', duration[0], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
        genVideo('./slides/exit-template.html', out, 'live-exit-000.png', 'live-exit.mp4', duration[1], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
    elif event.is_keynote:
        print(f">>> Keynotes {event.event_id} " + event.start + " " + event.end)
        genVideo('./slides/intro-template.html', out, 'keynote-intro-000.png', 'keynote-intro.mp4', duration[0], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
        genVideo('./slides/qa-break-template.html', out, 'keynote-qa-000.png', 'keynote-qa.mp4', duration[1], image_only=image_only, env={ 'event': event, 'conference': event.conference, 'time': CurrentTime.parse(event.start) })
    else:
        print(f'Unhandled: {event}')