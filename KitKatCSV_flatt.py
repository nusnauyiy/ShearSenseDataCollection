import csv
import traceback
from itertools import count
# import pandas as pd
import matplotlib.pyplot as plt
from pynput import keyboard
import numpy as np
import serial
import time
import math
from threading import Thread
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui, QtWidgets
from classifiers.Classifier import ThresholdClassifier
from settings import PORT_FLAT, FILENAME, TIMESTAMP, FOLDER, LABEL_LENGTH
import sys
from threading import Timer

Channels = 180
Taxels = 36
NumRowCol = 6
NumPads = 5
file_name = FOLDER + "/" + FILENAME + TIMESTAMP() + "_FLAT.csv"

# **********************USER DEFINED VALUES END******************#

# value that are going to change
dx = []  # 3d x value. does not change in our case
dy = []  # 3d y value. does not change in our case
current_dz = []
num = 0
dz = np.zeros(Channels)  # 3d z value. change relative to capacitance
pressure_vals = np.zeros(Taxels)

shear_vals_x = np.zeros(Taxels)
shear_vals_y = np.zeros(Taxels)
arrows = []

data = []
word = []

average = []

key_pressed = ''


def serial_port_init():  # Serial port initializations
    ser = serial.Serial(
        port=PORT_FLAT,
        baudrate=500000,
        timeout=None,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    ser.isOpen()
    return ser


def thread1():
    global word, current_dz, U, y1, y2

    def stop_label():
        global key_pressed
        print('{0} released'.format(key_pressed))
        key_pressed=''
        

    def on_press(key):
        pass

    def on_release(key):
        global key_pressed
        try:
            # nontimer keys
            if key.char.isalpha():
                print("pressed alpha key")
                print('{0} pressed'.format(key))
                key_pressed=key.char
                t = Timer(LABEL_LENGTH, stop_label)
                t.start()

            # timer keys
            if key.char.isdigit():
                print("pressed digit key")
                print('{0} pressed'.format(key))
                key_pressed=key.char
                t = Timer(4.0, stop_label)
                t.start()
            
        except:
            pass
        # key_pressed = ''

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    prev_touched = 0
    while True:  # this will not block other functions since it is on a different thread
        line = ser.readline()
        raw_count = []
        try:
            data = line.decode()
            word = data.split(",")
            index = 0
            if len(word) >= Channels + 1:  # discard faulty data
                for index in range(Channels):
                    try:
                        raw_count.append(float(word[index]))
                        dz[index] = float(word[index])#- offset_z
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
            if touched == 1 and prev_touched == 0:
                print("touched")
            if touched == 0 and prev_touched == 1:
                print("not touched")
            prev_touched = touched
            data_set.insert(Channels + 1, int(touched))
            data_set.insert(Channels + 2, 0 if key_pressed == '' else ord(key_pressed))
            data_set.insert(0, time.time())

            with open(file_name, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
                writer.writerow(data_set)
        except:
            traceback.print_exc()
            continue


def classify_touch_no_touch(raw_count):
    classifier = ThresholdClassifier(average)
    return classifier.classify(raw_count)


class HeatMap(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False

    def set_data(self, data):
        self.data = data 
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        for i in range(Taxels):
            row = i%NumRowCol
            col = i//NumRowCol
            a = self.data[i]
            x = max((400-abs(a))/400,0)
            p.setBrush(pg.mkBrush(255,153+102*x,255*x))
            p.drawRect(200*col, 600-200*row, 200, 200)
            
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())

#app = QtGui.QApplication([])
app = QtWidgets.QApplication([])
heatmap = HeatMap()

def arrowUpdate():
    global arrows, shear_vals_x, shear_vals_y, pressure_vals
    for i in range(Taxels):
        xlen = -shear_vals_x[i]*70/50
        ylen = -shear_vals_y[i]*70/50
        len = math.sqrt(math.pow(xlen, 2) + math.pow(ylen, 2))
        if len < 10:
            tlen = 0
            hlen = 0
        else:
            tlen = len - 10
            hlen = 20
        a = arrows[i]
        a.setPos(100 + 200*(i//NumRowCol) - xlen, 700-200*(i%NumRowCol) - ylen)
        a.setStyle(angle = math.degrees(math.atan2(ylen, xlen)), headLen = hlen, tailLen = tlen)


def update():
    global heatmap, pressure_vals
    calcValues()
    heatmap.set_data(pressure_vals)
    arrowUpdate()
    app.processEvents()  ## force complete redraw for every plot


     
def calcValues():
    global average, dz
    for taxel in range(0, Taxels):
        c0_new = dz[NumPads*taxel]
        c4_new = dz[NumPads*taxel+4]
        c0_avg = average[NumPads*taxel]
        c4_avg = average[NumPads*taxel+4]
        try:
            shear_vals_y[taxel] =  (c4_avg*c0_new - c0_avg*c4_new)/(c4_new+c0_new)*-1

            '''
            if (abs(c0_new-c0_avg)>=3.0 or abs(c4_new-c4_avg >= 3.0)):
                print(f"c0_new {c0_new} c0_avg {c0_avg} c4_new {c4_new} c4_avg {c4_avg}")
                print(f"{NumPads*taxel} {NumPads*taxel+4}")
            '''
        except:
            continue

        c1_new = dz[NumPads*taxel+1]
        c3_new = dz[NumPads*taxel+3] 
        c1_avg = average[NumPads*taxel+1] 
        c3_avg = average[NumPads*taxel+3]
        try:
            shear_vals_x[taxel] = (c3_avg*c1_new - c1_avg*c3_new)/(c3_new+c1_new)

            '''
            if (abs(c0_new-c0_avg)>=3.0 or abs(c4_new-c4_avg >= 3.0)):
                print(f"c1_new {c1_new} c1_avg {c1_avg} c3_new {c3_new} c3_avg {c3_avg}")
                print(f"{NumPads*taxel+1} {NumPads*taxel+3}")
            '''
            
        except:
            continue

        c2_new = dz[NumPads*taxel+2]
        c2_avg = average[NumPads*taxel+2]
        try:
            pressure_vals[taxel] = (c2_new-c2_avg)*2
        except:
            continue

def plot_init():
    global app, heatmap, pressure_vals
    plt = pg.plot()
    heatmap.set_data(pressure_vals)
    plt.addItem(heatmap)


    for i in range(Taxels):
        a = pg.ArrowItem(tipAngle=80, baseAngle=5, tailWidth=10, pen='y', brush='b', pxMode=False)
        a.setPos(100 + 200*(i//NumRowCol), 700-200*(i%NumRowCol))
        arrows.append(a)
        plt.addItem(a)

    plt.setWindowTitle('Heatmap and shear display FLAT')
    plt.getPlotItem().hideAxis('bottom')
    plt.getPlotItem().hideAxis('left')
    plt.setGeometry(100, 100, 1000,1000)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(200)

    


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
    print("serial data calibrated")

    channel_name = ['time (s)']
    for i in range (Channels):
        name = 'Channel'+str(i)
        channel_name.append(name)
    channel_name += ["touched", "label"]

    
    row1 = [0]
    row1.extend(average)
    row1.extend([0,0])
    start = time.time()
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL,delimiter=',')
        writer.writerow(channel_name)
        writer.writerow(row1)

    thread = Thread(target = thread1)
    print("starting data collection... writing data to " + file_name)
    
    thread.start()
    time.sleep(0.01)

    calcValues()
    plot_init()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
