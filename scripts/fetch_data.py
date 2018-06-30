#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, math, getopt, sys, time
from config_vars import *


""" stop generation of tiles and wait for all processes to finish """
def stop_rendering():
    command = 'touch ' + STOP_FILE;
    os.system(command);
    command = 'ps aux|grep generate_tile.py|grep -v grep|wc -l';
    nrThreads = int(os.popen(command).read());
    while (nrThreads > 1):
        time.sleep(10);
        nrThreads = int(os.popen(command).read());

""" restart the generation of tiles """
def restart_rendering():
    command = 'rm ' + STOP_FILE;
    os.system(command);


""" downloads a data file via wget and calls mapsplit to produce .osm.pbf input tiles from it """
def getData(filenameBase, url, mapsplitParams):
    stop_rendering();

    osmdump = '%s.osm.pbf' % filenameBase
    os.chdir(TILE_OUTPUT + '/dl/');
    command = 'wget -O %s %s' % (osmdump, url)
    print ("Fetching " + filenameBase + " data via:\n" + command);
    os.system(command)
    
    dir = os.getcwd()
    os.chdir(MAPSPLIT);
    command = './mapsplit -v -t -b=0.1 -c -f=%d %s -p=%s/%s.poly -d=/scratch/peda/input/lastchange_%s.txt %s %s'
    command = command % (NR_FILES, mapsplitParams, POLY_DIRECTORY, filenameBase, filenameBase, dir + '/' + osmdump, TILE_OUTPUT + '/dl/tiles_z13_');
    print ('Splitting ' + osmdump + ' into tiles via:\n' + command)
    os.system(command)

    # and finally copy let's copy the files back to our working directory..
    command = 'mv ' + TILE_OUTPUT + '/dl/tiles_* ' + TILE_OUTPUT;
    print ('Copy tile-files to working dir via:\n' + command)
    os.system(command)

    command = 'rm ' + osmdump;
    print ('Remove tilefile via:\n' + command)
    os.system(command);

    restart_rendering();


""" Fetch data for Germany from Geofabrik """
def getGermanyData():
    stop_rendering();

    osmfull = 'germany.osm.pbf'
    os.chdir(TILE_OUTPUT + '/dl/');
    command = 'wget -O %s "http://download.geofabrik.de/europe/germany-latest.osm.pbf"' % osmfull
    print ("Fetching germany data from geofabrik via:\n" + command);
    os.system(command)

    # Start with south germany...

    osmdump = 'germany_south.pbf'
    command = '/opt/osmosis/bin/osmosis --read-pbf %s --bounding-box top=50.2 left=6.0 bottom=47.1 right=13.9 --write-pbf %s'
    command = command % (osmfull, osmdump)
    print ('Cutting south germany via:\n' + command)
    os.system(command)

    dir = os.getcwd()
    os.chdir(MAPSPLIT);
    command = './mapsplit -v -t -b=0.1 -c -f=%d -s=100000000,25000000,450000 -p=%s/germany_south.poly -d=/scratch/peda/input/lastchange_germany_south.txt %s %s'
    command = command % (NR_FILES, POLY_DIRECTORY, dir + '/' + osmdump, TILE_OUTPUT + '/dl/tiles_z13_');
    print ('Splitting south germany into tiles via:\n' + command)
    os.system(command)

    command = 'mv ' + TILE_OUTPUT + '/dl/tiles_* ' + TILE_OUTPUT;
    print ('Copy tile-files to working dir via:\n' + command)
    os.system(command)

    command = 'rm ' + osmdump;
    print ('Remove tilefile via:\n' + command)
    os.system(command);

    # Continue with middle germany...

    osmdump = 'germany_middle.pbf'
    os.chdir(TILE_OUTPUT + '/dl/');
    command = '/opt/osmosis/bin/osmosis --read-pbf %s --bounding-box top=53.4 left=5.7 bottom=50.1 right=15.1 --write-pbf %s'
    command = command % (osmfull, osmdump)
    print ('Cutting middle germany via:\n' + command)
    os.system(command)

    dir = os.getcwd()
    os.chdir(MAPSPLIT);
    command = './mapsplit -v -t -b=0.1 -c -f=%d -s=160000000,40000000,450000 -p=%s/germany_middle.poly -d=/scratch/peda/input/lastchange_germany_middle.txt %s %s'
    command = command % (NR_FILES, POLY_DIRECTORY, dir + '/' + osmdump, TILE_OUTPUT + '/dl/tiles_z13_');
    print ('Splitting middle germany into tiles via:\n' + command)
    os.system(command)

    command = 'mv ' + TILE_OUTPUT + '/dl/tiles_* ' + TILE_OUTPUT;
    print ('Copy tile-files to working dir via:\n' + command)
    os.system(command)

    command = 'rm ' + osmdump;
    print ('Remove tilefile via:\n' + command)
    os.system(command);

    # Finally do north germany...

    osmdump = 'germany_north.pbf'
    os.chdir(TILE_OUTPUT + '/dl/');
    command = '/opt/osmosis/bin/osmosis --read-pbf %s --bounding-box top=55.2 left=6.1 bottom=53.1 right=14.5 --write-pbf %s'
    command = command % (osmfull, osmdump)
    print ('Cutting north germany via:\n' + command)
    os.system(command)

    dir = os.getcwd()
    os.chdir(MAPSPLIT);
    command = './mapsplit -v -t -b=0.1 -c -f=%d -s=100000000,20000000,450000  -p=%s/germany_north.poly -d=/scratch/peda/input/lastchange_germany_north.txt %s %s'
    command = command % (NR_FILES, POLY_DIRECTORY, dir + '/' + osmdump, TILE_OUTPUT + '/dl/tiles_z13_');
    print ('Splitting north germany into tiles via:\n' + command)
    os.system(command)

    command = 'mv ' + TILE_OUTPUT + '/dl/tiles_* ' + TILE_OUTPUT;
    print ('Copy tile-files to working dir via:\n' + command)
    os.system(command)

    command = 'rm ' + osmdump;
    print ('Remove tilefile via:\n' + command)
    os.system(command);
    
    # Finally remove full dump
    command = 'rm ' + osmfull;
    print ('Remove tilefile via:\n' + command)
    os.system(command);
    
    restart_rendering();


""" Fetch data for Switzerland from Geofabrik """
def getSwitzerlandData():
    getData("switzerland", "http://download.geofabrik.de/europe/switzerland-latest.osm.pbf", "--size=120000000,20000000,5000000");


""" Fetch data for Austria from Geofabrik """
def getAustriaData():
    getData("austria", "http://download.geofabrik.de/europe/austria-latest.osm.pbf", "--size=120000000,20000000,5000000");


""" Print usage informations """
def usage():
    print("generate_tile.py [-h|--help] [--fetch-[austria|switzerland|germany|all]]");


"""
 main
"""
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help', 'fetch-austria', 'fetch-switzerland', 'fetch-germany', 'fetch-all'])
    except getopt.GetoptError, err:
        sys.stderr.write(str(err) + '\n')
        sys.exit(1)

    for o,a in opts:
        if o in ('-h', '--help'):
            usage();
            sys.exit();
        elif o == '--fetch-austria':
            getAustriaData();
            sys.exit();
        elif o == '--fetch-switzerland':
            getSwitzerlandData();
            sys.exit();
        elif o == '--fetch-germany':
            getGermanyData();
            sys.exit();
        elif o == '--fetch-all':
            getAustriaData();
            getSwitzerlandData();
            getGermanyData();
            sys.exit();
    
    sys.stderr.write('No parameter recognized! Use --help for instructions.\n')
    sys.exit(2)

# call main...
main()
