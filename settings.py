import datetime

PORT = '/dev/tty.usbmodem1303'
FOLDER = 'data'
FILENAME = "test"


def TIMESTAMP():
    now = datetime.datetime.now()
    return now.strftime("%m-%d %H:%M")
