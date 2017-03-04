#!/usr/bin/env python2.7

import os
import sys

import argparse

from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels

from simplejson import load

from pyinotify import IN_CLOSE_WRITE
from pyinotify import Notifier
from pyinotify import ProcessEvent
from pyinotify import WatchManager


DEBUG = True
PIXEL_COUNT = 32
SPI_DEVICE = 0
SPI_PORT = 0


def load_colormap():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'colormap.json'), 'r') as fh:
        return(load(fh))


class EventHandler(ProcessEvent):
    def __init__(self, set_color):
        ProcessEvent.__init__(self)
        self.set_color = set_color

    def process_IN_CLOSE_WRITE(self, event):
        lednr = int(event.pathname.split(os.sep)[-1][3:])

        with open(event.pathname) as fh:
            line = fh.readline().strip()

        colorname1 = line.split(',')[0]
        dim1 = float(line.split(',')[1])

        self.set_color(lednr,
                       colorname1,
                       dim1)


class Bollocks(object):
    COLORMAP = {}
    led_map = {}

    def __init__(self):
        self.COLORMAP = load_colormap()

    def run(self, path_to_leddir):
        for led in sorted(os.listdir(path_to_leddir)):
            with open(path_to_leddir + os.sep + led) as fh:
                line = fh.readline().strip()
                step = False

                if line.count(',') > 1:
                    step = 0

                self.led_map[led] = {
                    'wanted': [fh.readline().strip()],
                    'r': 0,  # current r
                    'g': 0,  # current g
                    'b': 0,  # current b
                    'step': step,  # current step
                }

        self.path_to_leddir = path_to_leddir

        try:
            self.pixels = WS2801Pixels(
                    PIXEL_COUNT,
                    spi=SPI.SpiDev(
                        SPI_PORT, SPI_DEVICE))

        except Exception as e:
            msg = 'Bollocks: '
            msg += 'Unable to open SPI port: %i, device: %i\n' % (
                    SPI_PORT, SPI_DEVICE)
            sys.stderr.write(msg)
            sys.exit(-1)

        self.pixels.clear()
        self.pixels.show()

        print("Starting bollocks v1")
        self.watch_dir()

    def watch_dir(self):
        wm = WatchManager()
        handler = EventHandler(self.set_color)
        notifier = Notifier(wm, handler)

        wm.add_watch(self.path_to_leddir,
                     IN_CLOSE_WRITE,
                     rec=True)

        notifier.loop()

    def set_color(self, lednr, colorname1, dim1, *kwargs):
        color1 = self.COLORMAP.get(colorname1)

        if color1:
            r = int(round((float(color1[0]) / 100.0) * dim1))
            g = int(round((float(color1[2]) / 100.0) * dim1))
            b = int(round((float(color1[1]) / 100.0) * dim1))
        else:
            msg = 'Invalid colorname: "%s" for led: %i' % (colorname1, lednr)
            print(msg)
            return
        if DEBUG:
            print('Setting led: %i to %s (%i, %i, %i)' % (
                lednr, colorname1, r, g, b))

        self.pixels.set_pixel_rgb(lednr,
                                  r, g, b)
        self.pixels.show()


def main(path_to_leddir):
    bollocks = Bollocks()
    bollocks.run(path_to_leddir)


def test():
    """
    >>> path_to_leddir = '/led/'
    >>> bollocks = Bollocks()
    >>> print(bollocks.COLORMAP.get('cyan2'))
    {'rgb': '0,238,238', 'hex': '#00eeee'}
    """
    import doctest
    doctest.testmod(verbose=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bollocks book leds rock!')
    parser.add_argument('--leds',
                        default=32,
                        type=int,
                        help='Number of led\'s on strip')
    parser.add_argument('--path',
                        default='/led/',
                        type=str,
                        help='Path to SHM directory')
    parser.add_argument('--test',
                        action="store_true",
                        help='Run self test')
    args = parser.parse_args()

    if args.test:
        test()
    else:
        if os.path.isdir(args.path):
            main(args.path)
        else:
            msg = 'Bollocks: '
            msg += 'Could not open SHM: %s' % args.path
            sys.stderr.write(str(msg) + '\n')
            sys.exit(-1)
