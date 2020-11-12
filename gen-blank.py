#!/usr/bin/env python3

import splash
import argparse
from datetime import datetime
from splash.keyframe import KeyFrame

frame = KeyFrame.render_from_template('./slides/blank.html', './out/blank.png', 5, {})

splash.video.generateFromKeyFrames([frame], './out/blank.mp4')