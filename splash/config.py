import os

GENERATE_IMAGE_ONLY = os.getenv('IMAGE_ONLY') is not None

INTRO_SECONDS = 5
QA_TRANSITION_SECONDS = 5
OUTRO_SECONDS = 5



BREAKS = [
    '08:20', '20:20',
    '10:20', '22:20',
    '12:20', '00:20',
    '14:20', '02:20',
    '16:20', '04:20',
    '18:20', '06:20',
]

START_TIME_OF_LAST_EVENT_BEFORE_BREAK = [
    '07:20', '19:20',
    '10:00', '22:00',
    '12:00', '00:00',
    '14:00', '02:00',
    '16:00', '04:00',
    '18:00', '06:00',
]