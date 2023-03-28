import cv2
import numpy as np

from model import Gesture

ascii_to_gesture = {
    109: "massage",
    114: "rub",
    100: "drag",
    115: "slide",
    112: "poke",
    97: "pat",
    101: "press",
    116: "tap",
    110: "pinch",
    107: "knead",
    119: "twist",
    111: "no",
    99: "constant",
    102: "fist",
    108: "type",
    104: "karate",
    103: "outward_caress",
    122: "scratch"
}

pressure_idx = list(filter(lambda n: n % 5 == 3, range(1, 181)))
shear_up_idx = list(filter(lambda n: n % 5 == 1, range(1, 181)))
shear_down_idx = list(filter(lambda n: n % 5 == 0, range(1, 181)))
shear_left_idx = list(filter(lambda n: n % 5 == 2, range(1, 181)))
shear_right_idx = list(filter(lambda n: n % 5 == 4, range(1, 181)))


def raw_data_to_gestures(df):
    all_avg = []

    def find_shear_x(l, r, l_avg, r_avg):
        return (l * r_avg - r * l_avg) / (l_avg + r_avg)

    def find_shear_y(u, d, u_avg, d_avg):
        return (u * d_avg - d * u_avg) / (u_avg + d_avg)

    def decompose_data(name, df, avg):
        # re-align time stamps to start at 0
        time_stamps = df.pop(df.columns[0]).to_numpy()
        time_stamps = time_stamps - time_stamps[0]

        # convert labels to respective gestures
        label = ascii_to_gesture[name]

        # extract specific channel data from each taxel

        raw_pressure = df[pressure_idx].to_numpy()
        avg_tile = np.tile(avg[pressure_idx], (raw_pressure.shape[0], 1))
        pressure = (raw_pressure - avg_tile) / avg_tile
        shear_up = df[shear_up_idx].to_numpy()
        shear_down = df[shear_down_idx].to_numpy()
        shear_left = df[shear_left_idx].to_numpy()
        shear_right = df[shear_right_idx].to_numpy()

        # calculate shear
        shear_y = np.zeros(shear_up.shape)
        shear_x = np.zeros(shear_up.shape)

        for i in range(0, shear_up.shape[0]):
            for j in range(0, 36):
                shear_y[i][j] = find_shear_y(shear_up[i][j], shear_down[i][j], avg[5 * j], avg[5 * j + 4])
                shear_x[i][j] = find_shear_x(shear_left[i][j], shear_right[i][j], avg[5 * j + 1], avg[5 * j + 3])

        # reshape and clean
        shear_y_3d = shear_y.reshape(shear_y.shape[0], 6, 6)
        shear_x_3d = shear_x.reshape(shear_y.shape[0], 6, 6)
        pressure_3d = pressure.reshape(shear_y.shape[0], 6, 6)

        shear_y_3d[np.where(np.isnan(shear_y_3d))] = 0
        shear_x_3d[np.where(np.isnan(shear_x_3d))] = 0
        pressure_3d[np.where(np.isnan(pressure_3d))] = 0

        return Gesture(time_stamps, pressure_3d, shear_x_3d, shear_y_3d, label)

    # average of the first 100 rows
    avg = df.iloc[0, 1:181].to_numpy()
    all_avg.append(avg)

    # remove unlablled data
    df = df[df[182] != 0]
    grouped_df = df.groupby(df.columns[-1])
    gestures = {}
    for name, group in grouped_df:
        try:
            gesture = decompose_data(name, group, avg)
            gestures[gesture.label] = gesture
        except Exception as e:
            print(e)
            pass

    return gestures, all_avg


def normalize(minmaxvals, arr):
    ret = arr.astype('float')
    for i in range(3):
        minval = minmaxvals[i]['min']
        maxval = minmaxvals[i]['max']
        if minval != maxval:
            ret[..., i] -= minval
            ret[..., i] *= (255.0 / (maxval - minval))
    return ret


def to_video(filename, arr, minmaxvals):
    width = 60
    height = 60

    # roughly, might be a little slower or faster
    fps = 40

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(f"{filename}.mp4", fourcc, float(fps), (width, height))

    for d in arr:
        img = normalize(minmaxvals, d).astype(np.uint8)
        img = img.repeat(10, 0).repeat(10, 1)
        video.write(img)
    video.release()
