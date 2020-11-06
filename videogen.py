import tempfile
import os
from jinja2 import FileSystemLoader, Environment
from scheduleloader import ConferenceEvent, ConferenceInfo



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
    htmlToPNG('./slides/empty-filler.html', image, { 'conference': conference })
    if not image_only: stillImageToVideo(image=image, video=f'{out}/filler.mp4', duration=duration)

# Generate videos from a timeslot
def generateVideoFromEvent(event: ConferenceEvent, duration, image_only=False):
    out = f'./out/{event.conference.subevent_id}/{event.event_id}'
    os.system(f'mkdir -p {out}')
    # Intro
    image = f'{out}/intro-000.png'
    htmlToPNG('./slides/intro-template.html', image, { 'event': event, 'time': '00:00' })
    if not image_only: stillImageToVideo(image=image, video=f'{out}/intro.mp4', duration=duration[0])
    # Q & A
    image = f'{out}/qa-000.png'
    htmlToPNG('./slides/qa-template.html', image, { 'event': event, 'time': '00:00' })
    if not image_only: stillImageToVideo(image=image, video=f'{out}/qa.mp4', duration=duration[1])
    # Exit
    image = f'{out}/exit-000.png'
    htmlToPNG('./slides/exit-template.html', image, { 'event': event, 'time': '00:00' })
    if not image_only: stillImageToVideo(image=image, video=f'{out}/exit.mp4', duration=duration[2])