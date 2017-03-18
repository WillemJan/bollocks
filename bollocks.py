#!/usr/bin/env python2.7

import os
import sys

import argparse
import ConfigParser

import StringIO

from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels

from json import load

from pyinotify import IN_CLOSE_WRITE
from pyinotify import Notifier
from pyinotify import ProcessEvent
from pyinotify import WatchManager


DEBUG = True


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
    SPI_DEVICE = 0
    SPI_PORT = 0

    led_map = {}

    def __init__(self):
        self.COLORMAP = self.load_colormap()
        config = self.load_config()
        self.NUM_LEDS = config.get('NUM_LEDS')
        self.SPI_DEVICE = config.get('SPI_DEVICE')
        self.SPI_PORT = config.get('SPI_PORT')

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
                        self.SPI_PORT, self.SPI_DEVICE))

        except Exception as e:
            msg = 'Bollocks: '
            msg += 'Unable to open SPI port: %i, device: %i\n' % (
                    self.SPI_PORT, self.SPI_DEVICE)
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

    def color_to_rgb(self, lednr, colorname, dim):
        if colorname.startswith('#') or colorname.startswith('0x'):
            colorname = colorname.replace('#','')
            colorname = colorname.replace('0x','')
            color = []
            color.append(int(colorname[0:2], 16))
            color.append(int(colorname[2:4], 16))
            color.append(int(colorname[4:6], 16))
        else:
            color = self.COLORMAP.get(colorname).get('rgb')
            color = list(int(i) for i in color.split(','))
            if color is None:
                msg = "led: %s: Failed to convert: %s,%s to rgb values." % (
                        lednr, colorname, dim)
                color = [0,0,0] # Default to off 

        r = int(round((float(color[0]) / 100.0) * dim))
        g = int(round((float(color[2]) / 100.0) * dim))
        b = int(round((float(color[1]) / 100.0) * dim))
        return (r, g, b)

    def set_color(self, lednr, colorname1, dim1, *kwargs):
        r, g, b = self.color_to_rgb(lednr, colorname1, dim1)
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
        spidevice = config.getint('bollocks', 'spidevice')
        spiport = config.getint('bollocks', 'spiport')

        return dict(
                {"NUM_LEDS": numleds,
                 "SPI_PORT": spiport,
                 "SPI_DEVICE": spidevice})

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
    >>> print(bollocks.COLORMAP.get('red'))
    {u'rgb': u'255,0,0', u'hex': u'#ff0000'}
    >>> print(bollocks.color_to_rgb(0, 'red', 100))
    (255, 0, 0)
    >>> print(bollocks.color_to_rgb(0, 'blue', 100))
    (0, 255, 0)
    >>> print(bollocks.color_to_rgb(0, 'green', 100))
    (0, 0, 255)
    >>> print(bollocks.color_to_rgb(0, 'red3', 100))
    (205, 0, 0)
    >>> print(bollocks.color_to_rgb(0, '#ff0000', 100))
    (255, 0, 0)
    >>> print(bollocks.SPI_DEVICE)
    0
    >>> print(bollocks.SPI_PORT)
    0
    >>> print(bollocks.NUM_LEDS)
    159
    """
    import doctest
    doctest.testmod(verbose=False)


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
