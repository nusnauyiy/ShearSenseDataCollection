import random

import cv2
import numpy as np


class Participant:
    def __init__(self, pid, gestures):
        self.pid = pid
        self.gestures = gestures
        minmax = [
            {"min": 0, "max": 0},
            {"min": 0, "max": 0},
            {"min": 0, "max": 0}
        ]
        for g in gestures.values():
            for i in range(3):
                if g.minmaxvals[i]["max"] > minmax[i].get("max"):
                    minmax[i]["max"] = g.minmaxvals[i]["max"]
                if g.minmaxvals[i]["min"] < minmax[i]["min"]:
                    minmax[i]["min"] = g.minmaxvals[i]["min"]
        self.minmax = minmax


class Gesture:
    def __init__(self, timestamps, pressure, shear_x, shear_y, label):
        self.timestamps = timestamps
        self.pressure = pressure
        self.shear_x = shear_x
        self.shear_y = shear_y
        self.label = label
        self.combined_data = [np.dstack((self.pressure[i, :, :], self.shear_x[i, :, :], self.shear_y[i, :, :])) for i in
                              range(self.shear_y.shape[0])]
        self.minmaxvals = [{'max': np.max(arr), 'min': np.min(arr)} for arr in [pressure, shear_x, shear_y]]

    def chop(self, length=80, num_samples=100):
        adjusted_num_samples = min(num_samples, len(self.combined_data) - length)
        print(adjusted_num_samples)
        samples = random.sample(range(0, len(self.combined_data) - length), adjusted_num_samples)
        answer = []
        for s in samples:
            answer.append(self.combined_data[s:s + length])
        return answer
