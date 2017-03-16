#!/usr/bin/env python2.7

import os
import sys

import argparse
import ConfigParser

import StringIO

from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels

from simplejson import load

from pyinotify import IN_CLOSE_WRITE
from pyinotify import Notifier
from pyinotify import ProcessEvent
from pyinotify import WatchManager


DEBUG = True
SPI_DEVICE = 0
SPI_PORT = 0


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
    NUM_LEDS = 32
    led_map = {}

    def __init__(self):
        self.NUM_LEDS = self.load_config().get('NUM_LEDS')
        self.COLORMAP = self.load_colormap()

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
                    self.NUM_LEDS,
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

        msg = 'Bollocks: '
        msg += 'Starting bollocks v1'
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
        color1 = self.COLORMAP.get(colorname1).get('rgb')

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

    @staticmethod
    def load_config(config_file="bollocks.conf"):

        config = ConfigParser.RawConfigParser()
        msg = 'Unable to read or parse config file %s' % config_file

        try:
            raw_config = '[bollocks]\n'
            with open(config_file, 'r') as fh:
                raw_config += fh.read()
        except:
            sys.stderr.write(msg)
            sys.exit(-1)

        try:
            config.readfp(StringIO.StringIO(raw_config))
        except:
            sys.stderr.write(msg)
            sys.exit(-1)

        numleds = config.getint('bollocks', 'numleds')

        return dict({"NUM_LEDS": numleds})
        


    @staticmethod
    def load_colormap():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'colormap.json'), 'r') as fh:
            return(load(fh))


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
    parser.add_argument('--config',
                        default="bollocks.conf",
                        type=str,
                        help='Path to config file')
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
        msg = 'Bollocks: '
        if not os.path.isdir(args.path):
            msg += 'Could not open SHM path: %s \n' % args.path
            sys.stderr.write(str(msg))
            sys.exit(-1)
        if not os.path.isfile(args.config):
            msg += 'Could not read config file: %s \n' % args.path
            sys.stderr.write(str(msg))
            sys.exit(-1)

        main(args.path)
