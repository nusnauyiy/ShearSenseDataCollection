import datetime
import random

PORT_FLAT = 'COM11'
PORT_PILLOW = 'COM6'
FOLDER = 'data'
#FILENAME = "Pilot-pillow-allgestures-not-covered-SS-DM-3"

FILENAME = "P18_3_0401 "
LABEL_LENGTH = 12.0

def TIMESTAMP():
    now = datetime.datetime.now()
    return now.strftime("%H_%M_%S")
