#!/usr/bin/env python
import simplejson

with open('w3_colormap.json', 'r') as fh:
	fh = simplejson.load(fh)

c = {}

for item in fh:
	item = item.strip()
	if item.startswith('#'):
		c[colorname]['hex'] = item
	elif item[0].isdigit():
		c[colorname]['rgb'] = item
	else:
		colorname = item
		c[colorname] = {}

with open('w3_colormap1.json', 'w') as fh:
	simplejson.dump(c, fh)
