import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

GENERATE_IMAGE_ONLY = os.getenv('IMAGE_ONLY') is not None
SKIP_EXISTING = os.getenv('SKIP_EXISTING') is not None

INTRO_SECONDS = 10
QA_TRANSITION_SECONDS = 10
OUTRO_SECONDS = 1

CARES = '''
    <h1>Announcements:</h1>
    <p>SIGPLAN CARES is a SIGPLAN committee composed of people for listening and helping to anyone who experiences or witnesses discrimination, harassment, or other ethical policy violations at SIGPLAN events or in the SIGPLAN publication process. The committee members may be sounding board for your and may provide advice on the steps necessary to have the matter further investigated by ACM. If you would like to learn more about CARES, chat about our mission, or ask questions about harassment, discrimination and related topics, please join us at one of three sessions at SPLASH. If you would like to speak privately to a CARES member, please feel free to email whomever you feel most comfortable communicating with. Our email addresses are listed on the CARES web page.</p>
'''

TUTORIAL = '''
    <h1>Announcements:</h1>
    <p>Don’t forget about the two ECOOP 2020 Tutorials that will happen on Friday 11/20! Feel free to register to receive more information and hands-on materials upfront: https://2020.ecoop.org/track/ecoop-2020-tutorials. --- The first tutorial (10am CET or 4pm CET) is about “Live and Exploratory Programming in Squeak/Smalltalk,” where we will talk about and discuss common programming scenarios in the realm of exploration and short feedback loops. --- The second tutorial (1pm CET or 7pm CET) is about “Polyglot Programming with GraalVM and TruffleSqueak,” where participants will learn about language interoperability, polyglot notebooks, and a polyglot programming system. --- Note that all materials will be made available to all attendees at SPLASH/ECOOP, too.</p>
'''

ANNOUNCEMENTS = {
    '02:20': CARES,
    '08:20': CARES,
    '14:20': CARES,
    '20:20': CARES,

    '10:20': TUTORIAL,
    '22:20': TUTORIAL,
    '16:20': TUTORIAL,
    '04:20': TUTORIAL,
}

def getAnnouncement(time: str) -> Optional[str]:
    return ANNOUNCEMENTS.get(time)

BREAKS = [
    '08:20', '20:20', # CARES
    '10:20', '22:20', # TUTORIAL
    '12:20', '00:20',
    '14:20', '02:20', # CARES
    '16:20', '04:20', # TUTORIAL
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