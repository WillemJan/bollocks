#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

entry_point = ("""
        [console_scripts]
        noise=Fe2.tools.alsa:noise
        mute=Fe2.tools.alsa:mute
""")

required = ['adafruit-gpio',
            'adafruit-ws2801',
            'simplejson',
            'pyinotify',
            'pep8',
            '']
setup(
    name='bollocks',
    version=1,
    description='Controll multicolor leds strips from SHM ',
    email='Willem Jan Faber <aloha@pruts.nl> Henri Aanstoot <fash@pruts.nl>',
    author='Henri Aanstoot, Willem Jan Faber',
    url='https://github.com/WillemJan/bollocks/',
    scripts=['statusscripts/cpuload.sh',
             'statusscripts/icinga.sh',
             'statusscripts/mode',
             'statusscripts/mode.readme',
             'statusscripts/network.sh',
             'statusscripts/random.sh'],
    package_dir={'bollocks': '.'},
    packages=['bollocks', 'bollocks'],
    install_requires=required,
    license='GPL-3.0',
    entry_points=entry_point,
)
