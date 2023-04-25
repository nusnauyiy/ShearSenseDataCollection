from itertools import count
import numpy as np
import serial
import math
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import time

from threading import Thread
import csv

# **********************Global variables begin***************************#
# **********************USER DEFINED VALUES BEGIN******************#

 #limit of z axis from z_lim to -z_lim
#Channels = x_lim*y_lim # number of channels
file_path = "data\P13 -Mar28 12_33_29_FLAT.csv"
file_name = "P13 -Mar28 12_30_19_FLAT.csv"  

file =file_path # + file_name

Channels = 180
Taxels = 36
NumRowCol = 6
NumPads = 5 

#The amount of samples from the beginning of the data that are used to calculate the average
averageWindow = 50

#Playback speed
speedup = 1


# **********************USER DEFINED VALUES END******************#

# value that are going to change
dx = []  # 3d x value. does not change in our case
dy = []  # 3d y value. does not change in our case
current_dz = []
num = 0
dz = np.ones(Channels)  # 3d z value. change relative to capacitance
pressure_vals = np.zeros(Taxels)

shear_vals_x = np.zeros(Taxels)
shear_vals_y = np.zeros(Taxels)
arrows = []

data = []
word = []

average = np.zeros(Channels)



# **********************Global variables end***************************#



def calcAverage():
    global average
    averageCalcArray = np.zeros((averageWindow, Channels))

    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        rowNum = 0
        for row in reader:
            if len(row) == Channels + 1:
                averageCalcArray[rowNum] = row[1:]
                rowNum += 1
            if rowNum >= averageWindow:
                break

    average = sum(averageCalcArray, 0)/averageWindow


def thread1():
    global dz
    start = time.time()

    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        rownum = 0
        for row in reader:
            t = float(row[0])
            while(t > (time.time() - start)*speedup):
                time.sleep(0.01)
            dz = np.array(list(map(float, row[1:])))
            rownum += 1
    

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


     
def calcValues():
    global average, dz
    for taxel in range(Taxels):
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
        except Exception as e:
            print(e)
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
            
        except Exception as e:
            print(e)
            continue

        c2_new = dz[NumPads*taxel+2]
        c2_avg = average[NumPads*taxel+2]
        try:
            pressure_vals[taxel] = (c2_new-c2_avg)*2
        except Exception as e:
            print(e)
            continue

def plot_init():
    global heatmap, pressure_vals
    plt = pg.plot()
    heatmap.set_data(pressure_vals)
    plt.addItem(heatmap)


    for i in range(Taxels):
        a = pg.ArrowItem(tipAngle=80, baseAngle=5, tailWidth=10, pen='y', brush='b', pxMode=False)
        a.setPos(100 + 200*(i//NumRowCol), 700-200*(i%NumRowCol))
        arrows.append(a)
        plt.addItem(a)

    plt.setWindowTitle('Heatmap and shear display')
    plt.getPlotItem().hideAxis('bottom')
    plt.getPlotItem().hideAxis('left')




if __name__ == "__main__":


    # define values for calculating average at the beginning
    calcAverage()
    
    #average = [1620.000000,1684.000000,1707.000000,1674.000000,1613.000000,1961.000000,1633.000000,1680.000000,1665.000000,1647.000000,1658.000000,1696.000000,1709.000000,1689.000000,1695.000000,1662.000000,1701.000000,1712.000000,1701.000000,1724.000000,1733.000000,1775.000000,1788.000000,1779.000000,1782.000000,1787.000000,1785.000000,1806.000000,1836.000000,1884.000000,1625.000000,1693.000000,1702.000000,1658.000000,1637.000000,1655.000000,1647.000000,1682.000000,1661.000000,1642.000000,1632.000000,1687.000000,1692.000000,1648.000000,1679.000000,1684.000000,1712.000000,1729.000000,1719.000000,1728.000000,1749.000000,1794.000000,1806.000000,1792.000000,1797.000000,1803.000000,1817.000000,1835.000000,1845.000000,1909.000000,1586.000000,1671.000000,1680.000000,1656.000000,1610.000000,1618.000000,1634.000000,1605.000000,1642.000000,1626.000000,1629.000000,1659.000000,1681.000000,1685.000000,1670.000000,1663.000000,1705.000000,1722.000000,1711.000000,1722.000000,1731.000000,1780.000000,1789.000000,1773.000000,1785.000000,1790.000000,1815.000000,1829.000000,1826.000000,1900.000000,1623.000000,1685.000000,1700.000000,1672.000000,1656.000000,1661.000000,1633.000000,1682.000000,1670.000000,1637.000000,1636.000000,1680.000000,1689.000000,1680.000000,1666.000000,1667.000000,1706.000000,1730.000000,1712.000000,1721.000000,1728.000000,1780.000000,1791.000000,1777.000000,1785.000000,1783.000000,1746.000000,1826.000000,1836.000000,1853.000000,1617.000000,1679.000000,1703.000000,1673.000000,1646.000000,1609.000000,1637.000000,1693.000000,1684.000000,1648.000000,1656.000000,1675.000000,1682.000000,1704.000000,1647.000000,1672.000000,1674.000000,1711.000000,1722.000000,1675.000000,1692.000000,1772.000000,1784.000000,1781.000000,1770.000000,1780.000000,1803.000000,1819.000000,1827.000000,1877.000000,1614.000000,1695.000000,1697.000000,1661.000000,1652.000000,1659.000000,1664.000000,1690.000000,1678.000000,1653.000000,1663.000000,1703.000000,1707.000000,1700.000000,1678.000000,1677.000000,1708.000000,1730.000000,1724.000000,1707.000000,1727.000000,1780.000000,1788.000000,1773.000000,1766.000000,1770.000000,1807.000000,1806.000000,1813.000000,1786.000000]
    

    thread = Thread(target = thread1)
    thread.start()
    time.sleep(0.01)

    calcValues()
    plot_init()
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    pg.exec()