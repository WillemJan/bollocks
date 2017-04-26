#!/usr/bin/env python2.7

import os
import sys
import time

import argparse
import ConfigParser
import StringIO
import threading

from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels

from json import load

from pyinotify import IN_CLOSE_WRITE
from pyinotify import Notifier
from pyinotify import ProcessEvent
from pyinotify import WatchManager

DEBUG = True

class Fader(threading.Thread):
    def __init__(self, pixels, led_map, color_to_rgb):
        threading.Thread.__init__(self, group=None, target=None, name=None, verbose=None)
        self.pixels = pixels
        self.led_map = led_map
        self.color_to_rgb = color_to_rgb

    def run(self):
        while True:
            for lednr in self.led_map.keys():
                r1, g1, b1 = self.led_map.get(lednr)[0]
                self.pixels.set_pixel_rgb(lednr,
                                          r1, g1, b1)
                self.pixels.show()
                old_map = self.led_map.get(lednr)[0]
                self.led_map[lednr][0] = self.led_map[lednr][1]
                self.led_map[lednr][1] = old_map

            time.sleep(0.001)

class Blinker(threading.Thread):
    def __init__(self, pixels, led_map, color_to_rgb):
        threading.Thread.__init__(self, group=None, target=None, name=None, verbose=None)
        self.pixels = pixels
        self.led_map = led_map
        self.color_to_rgb = color_to_rgb

    def run(self):
        while True:
            for lednr in self.led_map.keys():
                r1, g1, b1 = self.led_map.get(lednr)[0]
                if len(self.led_map.get(lednr)) == 3:
                    self.pixels.set_pixel_rgb(lednr,
                                              r1, g1, b1)
                    self.pixels.show()
                    self.led_map[lednr].append(0)
                else:
                    self.led_map[lednr][-1] += 1
                    if self.led_map[lednr][-1]*0.001 >= self.led_map[lednr][2]:
                        old_map = self.led_map.get(lednr)[0]
                        self.led_map[lednr][0] = self.led_map[lednr][1]
                        self.led_map[lednr][1] = old_map
                        self.led_map[lednr] = self.led_map[lednr][:-1]

            time.sleep(0.001)
             
class EventHandler(ProcessEvent):
    def __init__(self, set_color):
        ProcessEvent.__init__(self)
        self.set_color = set_color

    def process_IN_CLOSE_WRITE(self, event):
        try:
            lednr = int(event.pathname.split(os.sep)[-1][3:])
            with open(event.pathname) as fh:
                line = fh.readline().strip()
        except:
            return

        if line.find(',') > -1 and len(line.split(',')) == 6:
            colorname1 = line.split(',')[0]

            try:
                dim1 = float(line.split(',')[1])
            except:
                msg = 'Bollocks: '
                msg += 'Unable to parse led%i\n' % lednr
                sys.stderr.write(msg)
                dim1 = 100

            colorname2 = line.split(',')[2]

            try:
                dim2 = float(line.split(',')[3])
            except:
                msg = 'Bollocks: '
                msg += 'Unable to parse led%i\n' % lednr
                sys.stderr.write(msg)
                dim2 = 100

        
            mode = line.split(',')[4]
            if not mode in ["normal", "fade", "blink"]:
                mode = "normal"

            try:
                timer = float(line.split(',')[5])
            except:
                msg = 'Bollocks: '
                msg += 'Unable to parse led%i\n' % lednr
                sys.stderr.write(msg)
                timer = 1

            try:
                self.set_color(lednr,
                               colorname1,
                               dim1,
                               colorname2,
                               dim2,
                               mode,
                               timer)
            except Exception as error:
                print(error)


class Bollocks(object):
    COLORMAP = {}
    NUM_LEDS = 32
    SPI_DEVICE = 0
    SPI_PORT = 0

    def __init__(self):
        self.COLORMAP = self.load_colormap()
        config = self.load_config()
        self.NUM_LEDS = config.get('NUM_LEDS')
        self.SPI_DEVICE = config.get('SPI_DEVICE')
        self.SPI_PORT = config.get('SPI_PORT')

    def run(self, path_to_leddir):
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

        self.blinker = Blinker(self.pixels, {}, self.color_to_rgb)
        self.blinker.start()

        self.fader = Fader(self.pixels, {}, self.color_to_rgb)
        self.fader.start()

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
            colorname = colorname.replace('#', '')
            colorname = colorname.replace('0x', '')
            color = []
            color.append(int(colorname[0:2], 16))
            color.append(int(colorname[2:4], 16))
            color.append(int(colorname[4:6], 16))
        else:
            color = self.COLORMAP.get(colorname).get('rgb')
            color = list(int(i) for i in color.split(','))
            if color is None:
                msg = "led: %s: Failed to convert: %s,%s to rgb values.\n" % (
                        lednr, colorname, dim)
                sys.stderr.write(msg)
                color = [0, 0, 0]  # Default to off

        r = int(round((float(color[0]) / 100.0) * dim))
        g = int(round((float(color[2]) / 100.0) * dim))
        b = int(round((float(color[1]) / 100.0) * dim))
        return (r, g, b)

    def set_color(self, lednr, colorname1, dim1, colorname2, dim2, mode, timer):
        r1, g1, b1 = self.color_to_rgb(lednr, colorname1, dim1)
        r2, g2, b2 = self.color_to_rgb(lednr, colorname2, dim2)

        if DEBUG:
            print('Setting led: %i to %s (%i, %i, %i)' % (
                lednr, colorname1, r1, g1, b1))

        if mode == 'normal':
            self.pixels.set_pixel_rgb(lednr,
                                      r1, g1, b1)
            self.pixels.show()

            if lednr in self.blinker.led_map:
                self.blinker.led_map.pop(lednr)
            if lednr in self.fader.led_map:
                self.fader.led_map.pop(lednr)

        elif mode == 'blink':
            print('mode = blink')
            self.blinker.led_map[lednr] = [
                    [r1, g1, b1], [r2, g2, b2], timer]
            if lednr in self.fader.led_map:
                self.fader.led_map.pop(lednr)
        elif mode == 'fader':
            print('mode = fader')
            self.fader.led_map[lednr] = [
                    [r1, g1, b1], [r2, g2, b2], timer]
            if lednr in self.blinker.led_map:
                self.blinker.led_map.pop(lednr)

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
