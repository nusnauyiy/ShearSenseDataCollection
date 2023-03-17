import datetime
import random

PORT = 'COM6'
FOLDER = 'data'
#FILENAME = "Pilot-pillow-allgestures-not-covered-SS-DM-3"
FILENAME = "P6_Mar16th2023_FLAT "
LABEL_LENGTH = 12.0

def TIMESTAMP():
    now = datetime.datetime.now()
    return now.strftime("%H_%M_%S")
