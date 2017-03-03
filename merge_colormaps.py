#!/usr/bin/env python

from pprint import pprint
import simplejson

colormap = {}

def rgb_to_hex(rgbi):
    return "#" + "".join([
        hex(i)[-2:] for i in rgbi[:3]]).replace('x', '0')

def merge(d):
    for item in d:
        if not item in colormap:
            if not 'hex' in d.get(item):
                colormap[item] = {}
                hex_repr = rgb_to_hex(d.get(item))
                colormap[item]['hex'] = hex_repr
                colormap[item]['rgb'] = ",".join([str(i) for i in d.get(item)[:3]])
            else:
                colormap[item] = d.get(item)

for f in ['w3_colormap.json',
          'pygame_colormap.json']:
    with open(f, 'r') as fh:
        data = simplejson.load(fh)
        merge(data)

with open('colormap_out.json', 'w') as fh:
    simplejson.dump(colormap, fh)
