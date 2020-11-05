import videogen
import scheduleloader
import sys
import getopt

INTRO_LENGTH = 8
QA_LENGTH = 4
EXIT_LENGTH = 5

SCHEDULE_XML = './data/splash-schedule.xml'

xml = scheduleloader.loadXML(SCHEDULE_XML)

def generateSubEvent(subevent_id):
    events = scheduleloader.parseSubEvent(xml, subevent_id)
    for i in range(len(events)):
        e = events[i]
        next_e = events[i + 1] if i < len(events) - 1 else None
        videogen.generateVideoFromEvent(event=e, duration=(INTRO_LENGTH, QA_LENGTH, EXIT_LENGTH), next_event=next_e)

def printHelp():
    print('Usage:')
    print()
    print('Generate videos for all subevents:')
    print('    python3 ./gen.py')
    print()
    print('Generate videos for one subevent:')
    print('    python3 ./gen.py --subevent=c49b3977-bf78-4796-930d-b360d8899600')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h', [ 'subevent=' ])
except getopt.GetoptError:
    printHelp()
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        printHelp()
        sys.exit()

for opt, arg in opts:
    if opt == '--subevent':
        generateSubEvent(arg)
        sys.exit()

for subevent in scheduleloader.getAllSubEventIds(xml):
    generateSubEvent(subevent)

# events = scheduleloader.parseSubEvent('./data/splash-schedule.xml', 'c49b3977-bf78-4796-930d-b360d8899600')
# for e in events:
#     videogen.generateVideoFromEvent(e, duration=INTRO_LENGTH)