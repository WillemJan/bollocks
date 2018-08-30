#!/usr/bin/env python3
import os
import time
import random
from pprint import pprint
import zmq
import threading
import numpy

from math import pi, sin, cos, tan

time_delta = 0

HOSTS = ["totem1", "kast1", "touch1", "slaap0"]

img_path = "/home/aloha/sshfs/kast1/home/pi/porn/landscapes/"

colormap = [
    "aliceblue",
    "blue",
    "blue1",
    "blue2",
    "blue3",
    "blue4",
    "blueviolet",
    "cadetblue",
    "cadetblue1",
    "cadetblue2",
    "cadetblue3",
    "cadetblue4",
    "cornflowerblue",
    "darkblue",
    "darkslateblue",
    "deepskyblue",
    "deepskyblue1",
    "deepskyblue2",
    "deepskyblue3",
    "deepskyblue4",
    "dodgerblue",
    "dodgerblue1",
    "dodgerblue2",
    "dodgerblue3",
    "dodgerblue4",
    "lightblue",
    "lightblue1",
    "lightblue2",
    "lightblue3",
    "lightblue4",
    "lightskyblue",
    "lightskyblue1",
    "lightskyblue2",
    "lightskyblue3",
    "lightskyblue4",
    "lightslateblue",
    "lightsteelblue",
    "lightsteelblue1",
    "lightsteelblue2",
    "lightsteelblue3",
    "lightsteelblue4",
    "mediumblue",
    "mediumslateblue",
    "midnightblue",
    "navyblue",
    "powderblue",
    "royalblue",
    "royalblue1",
    "royalblue2",
    "royalblue3",
    "royalblue4",
    "skyblue",
    "skyblue1",
    "skyblue2",
    "skyblue3",
    "skyblue4",
    "slateblue",
    "slateblue1",
    "slateblue2",
    "slateblue3",
    "slateblue4",
    "steelblue",
    "steelblue1",
    "steelblue2",
    "steelblue3",
    "steelblue4",
]


class ledstrip(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.zmq_socket = self.context.socket(zmq.PUSH)
        self.zmq_socket.connect("tcp://%s:4455" % host)
        self.state = {}
        self.send = False

    def run(self):
        while True:
            if self.send:
                self.zmq_socket.send_json(self.state)
                self.send = False
            time.sleep(0.01)


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def producer():
    r = random.random() * 255
    g = random.random() * 255
    b = random.random() * 255

    c1 = rgb_to_hex((int(r), int(g), int(b)))

    if random.random() > 0.5:
        r = random.random() * 255
    if random.random() > 0.5:
        g = random.random() * 255
    if random.random() > 0.5:
        b = random.random() * 255

    hosts = HOSTS
    t = []
    for h in hosts:
        led = ledstrip(h)
        t.append(led)
        led.daemon = True
        for i in range(40):
            if random.random() > 0.5:
                led.state[i] = [c1, str(i), 'green', '20', 'normal', '0.1']
        led.start()

    return t


t = producer()
colormap1 = []

for Freq in range(1, 2):
    Freq *= 0.1
    #print ("current freq", Freq)
    time_delta = 0

    k = (random.random() + 1) * 120
    while time_delta <= 20.0:
        w = 2*pi*Freq
        y = sin(w*time_delta)+2
        y1 = cos(w*time_delta)+2
        time_delta = time_delta + 0.1

        b = y * 120
        g = y1 * k
        r = b - 120
        colormap1.append(rgb_to_hex((int(r), int(g), int(b))))


while True:
    l = 0
    dim = False
    while True:
        for j in t:
            r = random.random()
            for i in range(64):
                if len(colormap1) > i + l:
                    if r > 0.5:
                        j.state[i] = [
                            colormap1[i+l], str(0.4 + (l/(i*10+1))), colormap1[i+l], str(l+10), 'normal', '0.05']
                    else:
                        j.state[i] = [
                            colormap1[i+l], str(0.4 + (l/(i*10+1))), colormap1[i+l], str(l+10), 'normal', '0.05']
                else:
                    dim = True
            j.send = True
        if dim:
            l -= 1
            if l == 0:
                dim = False
                colormap1 = []

                for Freq in range(1, 2):
                    Freq *= 0.1
                    #print ("current freq", Freq)
                    time_delta = 0

                    k = (random.random() + 1) * 120
                    while time_delta <= 20.0:
                        w = 2*pi*Freq
                        y = sin(w*time_delta)+2
                        y1 = cos(w*time_delta)+2
                        time_delta = time_delta + 0.1

                        b = y * 120
                        g = y1 * k
                        r = b - 120
                        colormap1.append(rgb_to_hex((int(r), int(g), int(b))))

        else:
            l += 1
        time.sleep(0.1)
