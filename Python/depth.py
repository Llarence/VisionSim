import PIL.Image
from transformers import pipeline
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Ideally everything should happen in the create and there should be no global changes, but a well
# There is probably a fix if needed
plt.ion()


def get_lim(pts):
    low = min(pts)
    high = max(pts)

    delta = max(high - low, 1)

    return low - (delta * 0.2), high + (delta * 0.2)


# Check this
def angle_diff(target, curr):
    return (target - curr + 180) % 360 - 180


class Depth():
    def __init__(self, size):
        self.target = (105, 113)

        self.fig, self.ax = plt.subplots()
        self.xs = [self.target[0]]
        self.ys = [self.target[1]]
        self.colors = ['blue']
        self.plot = self.ax.scatter(self.xs, self.ys, c=self.colors)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-base-hf', device='cuda')


    def onclick(self, event):
        self.target = (event.xdata, event.ydata)
        self.xs[0] = event.xdata
        self.ys[0] = event.ydata


    def to_depth(self, image):
        # Instead of using hugging face and PIL
        # The original repo should be used https://github.com/DepthAnything/Depth-Anything-V2/tree/main
        return np.array(self.pipe(PIL.Image.fromarray(image))['depth'].convert('L'))


    def update_graph(self, pose):
        self.xs.append(pose[0])
        self.ys.append(pose[1])
        self.colors.append('red')

        self.plot.set_offsets(np.c_[self.xs, self.ys])
        self.plot.set_color(self.colors)

        self.ax.set_xlim(*get_lim(self.xs))
        self.ax.set_ylim(*get_lim(self.ys))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def __call__(self, image, pose, time):
        depth =  self.to_depth(image)

        out = depth
        # Depth is relative so this comparison is maybe dubious
        out[out < 30] = 0
        out = out[1:] - out[:-1]
        out[out < 0] = 0

        out = cv2.dilate(out, np.ones((5, 5), np.uint8))

        bound1 = int(out.shape[0] / 3)
        bound2 = int(out.shape[0] * 2 / 3)

        left = np.mean(out[:, :bound1])
        middle = np.mean(out[:, bound1:bound2])
        right = np.mean(out[:, bound2:])

        delta = (self.target[0] - pose[0], self.target[1] - pose[1])
        delta_angle = angle_diff(np.rad2deg(np.arctan2(delta[1], delta[0])), 90 - pose[3])
        want_turn = -delta_angle / 90

        if right > 30 and middle > 30 and left > 30:
            forward = 0
            turn = 0
        else:
            forward = 1
            if want_turn > 0:
                if right < 30:
                    turn = want_turn
                else:
                    if middle < 30:
                        turn = 0
                    else:
                        turn = -1
            elif want_turn < 0:
                if left < 30:
                    turn = want_turn
                else:
                    if middle < 30:
                        turn = 0
                    else:
                        turn = 1
            else:
                if middle < 30:
                    turn = want_turn
                else:
                    if left > right:
                        turn = 1
                    else:
                        turn = -1

        cv2.imshow('Image', image)
        cv2.imshow('Depth', depth)
        cv2.imshow('Out', out)

        cv2.pollKey()

        self.update_graph(pose)

        return (forward, turn)
