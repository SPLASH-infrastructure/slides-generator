import videogen
import scheduleloader
# from . import videogen

INTRO_LENGTH = 8
QA_LENGTH = 4
EXIT_LENGTH = 5

events = scheduleloader.parseSubEvent('./data/splash-schedule.xml', 'c49b3977-bf78-4796-930d-b360d8899600')
for i in range(len(events)):
    e = events[i]
    next_e = events[i + 1] if i < len(events) - 1 else None
    videogen.generateVideoFromEvent(event=e, duration=(INTRO_LENGTH, QA_LENGTH, EXIT_LENGTH), next_event=next_e)


# events = scheduleloader.parseSubEvent('./data/splash-schedule.xml', 'c49b3977-bf78-4796-930d-b360d8899600')
# for e in events:
#     videogen.generateVideoFromEvent(e, duration=INTRO_LENGTH)