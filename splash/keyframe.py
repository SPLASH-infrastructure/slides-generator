from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import json
import os
from jinja2 import FileSystemLoader, Environment

def htmlToPNG(html, png, env):
    templateLoader = FileSystemLoader(searchpath=os.path.dirname(html))
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(os.path.basename(html))
    with open('./slides/.temp.html', 'w') as out_file:
        out_file.write(template.render(**env))
    os.system(f'wkhtmltoimage --enable-local-file-access --disable-smart-width --height 1080 --width 1960 ./slides/.temp.html {png}')
    return png

@dataclass
class KeyFrame:
    image: str # image path
    duration: int # in seconds

    @staticmethod
    def render_from_template(template: str, image: str, duration: int, env) -> 'KeyFrame':
        dirname = os.path.dirname(image)
        os.system(f'mkdir -p {dirname}')
        htmlToPNG(template, image, env)
        return KeyFrame(image=os.path.realpath(image), duration=duration)