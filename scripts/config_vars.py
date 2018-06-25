#!/usr/bin/python
# -*- coding: utf-8 -*-

STOP_FILE = '/tmp/stop_tilegen'
INPUT_DIR = '/home/osmuser/input/tiles/'
FINISHED_DIR = '/home/osmuser/input/old/'
MAX_THREADS = 3

GET_LIVE_DATA = False # should we get data via the osm api? (caution, this might get you blocked!)
KEEP_DATA = False     # should we keep temp data? usefull for debugging
HAVE_X = True         # do we have a X-server?
SCALE_IMAGES = False  # do we also calculate scaled tiles?
NATIVE_TILEGEN = True # use the c tilegenerator (instead of the convert based)
ROTATABLE_MAP = True  # if the map can be viewed from 4 cardinal directions

OSM2WORLD = "/scratch/peda/OSM2World/"
MAPSPLIT = "/scratch/peda/mapsplit/"
PNG_TILEGEN = "/scratch/peda/png_tilegen/"
TILE_OUTPUT = "/scratch/peda/input/tiles/"
RENDER_OUTPUT = "/scratch/peda/output/"
NR_FILES = 10000
ZOOM = 13

REMAINING_TILES = '/tmp/tiles_todo'
WEBSITE_ORDERS = '/tmp/orders'
