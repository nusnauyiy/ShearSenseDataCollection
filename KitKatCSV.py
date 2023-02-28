import csv
import traceback

import numpy as np
import serial
import time

from threading import Thread

from classifiers.Classifier import ThresholdClassifier
from settings import PORT, FILENAME, TIMESTAMP


Channels = 180
Taxels = 36
NumRowCol = 6
NumPads = 5
file_name = FILENAME + TIMESTAMP() + ".csv"

# **********************USER DEFINED VALUES END******************#

# value that are going to change
num = 0
dz = np.zeros(Channels)  # 3d z value. change relative to capacitance
pressure_vals = np.zeros(Taxels)

shear_vals_x = np.zeros(Taxels)
shear_vals_y = np.zeros(Taxels)
arrows = []

data = []
word = []

average = []


def serial_port_init():  # Serial port initializations
    ser = serial.Serial(
        port=PORT,
        baudrate=500000,
        timeout=None,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    ser.isOpen()
    return ser


def thread1():
    while True:  # this will not block other functions since it is on a different thread
        line = ser.readline()
        raw_count = []
        try:
            data = line.decode()
            word = data.split(",")
            if len(word) >= Channels + 1:  # discard faulty data
                for index in range(Channels):
                    try:
                        raw_count.append(float(word[index]))
                    except ValueError:
                        continue
                    finally:
                        pass
        except UnicodeDecodeError:
            pass
        finally:
            pass

        data_set = raw_count

        try:
            touched = classify_touch_no_touch(raw_count)
            data_set.insert(Channels + 1, int(touched))
            data_set.insert(0, time.time())

            with open(file_name, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
                writer.writerow(data_set)
        except:
            traceback.print_exc()
            continue


def classify_touch_no_touch(raw_count):
    classifier = ThresholdClassifier(threshold)
    return classifier.classify(raw_count)


if __name__ == "__main__":
    print("initializing serial port...")
    ser = serial_port_init()
    print("serial port initialized")
    # Initialize settings for plotting

    # define values for calculating average at the beginning
    index = 0
    i = 0
    count = 0
    input_val = np.zeros((100, Channels))
    average = np.zeros(Channels)

    print("calibrating serial data...")
    while index < 100:
        line = ser.readline()
        try:
            data = line.decode()
            word = data.split(",")
            len_word = len(word)
            count = count + 1
            if len_word >= Channels:  # check value
                for i in range(Channels):
                    input_val[index][i] = float(word[i])
                index = index + 1
        except:
            continue
    for i in range(Channels):
        total = 0
        for index in range(100):
            total = input_val[index][i] + total
        average_val = total / 100
        average[i] = average_val
        # min[i] = min_val
    threshold = average * 0.99
    print("serial data calibrated")

    thread = Thread(target=thread1)
    print("starting data collection... writing data to " + file_name)
    thread.start()
    time.sleep(0.01)

