#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, math, getopt, sys, time
from config_vars import *


""" calculate lon value based on tile's x coord (and optional zoom) """
def tile2lon(x, zoom=ZOOM):
    return (x / 2.0**zoom)*360.0-180.0;

""" calculate lat value based on tile's y coord (and optional zoom) """
def tile2lat(y, zoom=ZOOM):
    n = math.pi-2*math.pi*y/(2**zoom)
    return (180/math.pi*math.atan(0.5*(math.e**(n)-math.e**(-n))));

def getfile(tileDir, outputDir, zoom, x, y):
    file = tileDir + outputDir + '/' + str(zoom) + '/' + str(x) + '/' + str(y) + '.png';
    if os.path.exists(file):
        return file;
    else:
        return tileDir + 'white.png';


""" generate the tiles for the different zooms """
def generateTiles(tileImg, x, y, tilesDir, outputDir, direction = 'n'):
    tmp = tilesDir + 'tmp/';
    tmpFile = tmp + 'resized_%d_%d.png' % (x, y);

    zoom = ZOOM
    img_size = 2**zoom;
    img_count = 2**(18-zoom);

    if NATIVE_TILEGEN:
        
        command = 'time -pv ' + PNG_TILEGEN + "packed_tilegen %s %s %d %d " + direction;
        command = command % (tileImg, tilesDir + outputDir + '/', x, y);
        print(command);
        os.system(command);
        zoom = 8;

    else:

        while True:
        
            command = 'convert -resize %dx%d -crop 256x256 %s %s' % (img_size, img_size, tileImg, tmpFile)
            print(command);
            os.system(command);

            # special handling in case of zoom 13
            if zoom+5 == 13:
                destDir = tilesDir + outputDir + '/' + str(zoom+5) + '/' + str(x) + '/'
                os.system('mkdir -p ' + destDir);
                os.rename(tmpFile, destDir + str(y) + '.png');
                break;

            # handling for other zoom levels
            i = 0;
            for iy in range(0, img_count):
                destY = y * img_count + iy;
                for ix in range(0, img_count):
                    destX = x * img_count + ix;
                    destDir = tilesDir + outputDir + '/' + str(zoom+5) + '/' + str(destX) + '/'
                    srcImg = 'resized_%d_%d-%d.png' % (x, y, i);
                
                    os.system('mkdir -p ' + destDir);
                    os.rename(tmp + srcImg, destDir + str(destY) + '.png');
                
                    i = i+1;
        
            # prepare for next zoom level run
            img_size = img_size/2;
            img_count = img_count/2;
            zoom = zoom - 1;

    # now we still need to make lower zoom levels by pasting images together...
    print(tilesDir);
    print(outputDir);
    print(tileImg);
    print("TODO: Level <13")
    print(zoom)

    if ROTATABLE_MAP:
        if direction == 'e':
            tmp = x
            x = y
            y = (2<<12) - 1 - tmp
        elif direction == 's':
            x = (2<<12) - 1 - x
            y = (2<<12) - 1 - y
        elif direction == 'w':
            tmp = x
            x = (2<<12) - 1 - y
            y = tmp

    while True:
        x = x / 2;
        y = y / 2;
        zoom = zoom - 1;

        b1 = getfile(tilesDir, outputDir, zoom+6, 2*x, 2*y);
        b2 = getfile(tilesDir, outputDir, zoom+6, 2*x+1, 2*y);
        b3 = getfile(tilesDir, outputDir, zoom+6, 2*x, 2*y+1);
        b4 = getfile(tilesDir, outputDir, zoom+6, 2*x+1, 2*y+1);
        outfile = tilesDir + outputDir + '/' + str(zoom+5) + '/' + str(x) + '/';
        os.system('mkdir -p ' + outfile);
        outfile = outfile + str(y) + '.png';

        command = 'montage %s %s %s %s -tile 2x2 -geometry 128x64 %s' % (b1, b2, b3, b4, outfile);
        print('combining images: ' + command);
        os.system(command);

        if zoom+5 == 4:
            break;


""" Print usage informations """
def usage():
    print("generate_tile.py [-h|--help] <tileX@zoom13> <tileY@zoom13>");


"""
 main
"""
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError, err:
        sys.stderr.write(str(err) + '\n')
        sys.exit(1)

    for o,a in opts:
        if o in ('-h', '--help'):
            usage();
            sys.exit();
            
    #actual tile code...

    if len(args) < 2:
        sys.stderr.write('Supply at least tile coordinates!\n')
        sys.exit(2)

    #parentDir = os.getcwd();
    parentDir = RENDER_OUTPUT
    #os.chdir(parentDir + '/tmp/');
    os.chdir('/tmp/');

    x = int(args[0]);
    y = int(args[1]);

    if len(args) == 3:
        osmfile = args[2];
    else:
        minlon = tile2lon(x);
        maxlon = tile2lon(x+1);
        minlat = tile2lat(y+1);
        maxlat = tile2lat(y);

        enlargelon = 0.1*(maxlon-minlon);
        enlargelat = 0.1*(maxlat-minlat);

        minlon -= enlargelon;
        maxlon += enlargelon;
        minlat -= enlargelat;
        maxlat += enlargelat;

        if GET_LIVE_DATA:
            # fetch data
            osmfile = 'data_%d_%d.osm' % (x, y);
            #command = 'wget -O %s "http://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f"';
            #command = 'wget -O %s "http://open.mapquestapi.com/xapi/api/0.6/map?bbox=%f,%f,%f,%f"';
            command = 'wget -O %s "http://www.overpass-api.de/api/xapi?map?bbox=%f,%f,%f,%f[@meta]"';
            command = command % (osmfile, minlon, minlat, maxlon, maxlat);
            print ("Fetching live data from server via:\n" + command);
            os.system(command)

            #fixing missing bounds in overpass api
            sedcommand = "sed -i '/^<osm/a <bounds minlon=\"%f\" minlat=\"%f\" maxlon=\"%f\" maxlat=\"%f\"/>' %s"
            sedcommand = sedcommand % (minlon, minlat, maxlon, maxlat, osmfile)
            os.system(sedcommand)

        else:
            osmdump = 'bayern.osm.pbf'
            osmfile = 'data_%d_%d.osm' % (x, y);
            command = 'osmosis --read-pbf file="%s" --bounding-box top=%f left=%f bottom=%f right=%f completeWays=yes --write-xml file="%s"'
            command = command % (osmdump, maxlat, minlon, minlat, maxlon, osmfile);
            print ("Cutting out wanted tile via:\n" + command);
            os.system(command)

        osmfile = os.getcwd() + '/data_%d_%d.osm' % (x, y);

    ogloutput = os.getcwd() + '/ogltile_%d_%d.png' % (x, y);
    params = '/tmp/logs/params_%d_%d.txt' % (x, y);
    outfile = os.getcwd() + '/%%s_ogltile_%d_%d.ppm' % (x, y);
    povoutput = os.getcwd() + '/povtile_%d_%d.png' % (x, y);
    povfile = os.getcwd() + '/tile_%d_%d.pov' % (x, y);
    logfile = '/tmp/logs/performancetable';

    # create the logfile dir
    os.system('mkdir /tmp/logs')

    if ROTATABLE_MAP:
        paramfile = open(params, 'w')
        content = '--config osm2world.config -i ' + osmfile + ' -o ' + outfile + ' --resolution 8192,4096 ' \
            ' --oview.tiles %d,%d,%d --oview.from %s --performancePrint --performanceTable %s'
        print >> paramfile, (content % ('n', ZOOM, x, y, 'S', logfile))
        print >> paramfile, (content % ('s', ZOOM, x, y, 'N', logfile))
        print >> paramfile, (content % ('w', ZOOM, x, y, 'E', logfile))
        print >> paramfile, (content % ('e', ZOOM, x, y, 'W', logfile))
        paramfile.close()

    # first let's run osm2world...
    os.chdir(OSM2WORLD + 'build/');
    if ROTATABLE_MAP:
        command = 'time -pv ./osm2world.sh --parameterFile ' + params
    else:
        command = 'time -pv ./osm2world.sh --config osm2world.config -i %s ' \
            ' -o %s %s --resolution 8192,4096 --oview.tiles %d,%d,%d --performancePrint --performanceTable %s '
        command = command % (osmfile, ogloutput, povfile, ZOOM, x, y, logfile);

    if not HAVE_X:
        testCommand = 'ps aux|grep Xvfb|grep -v grep|wc -l';
        if int(os.popen(testCommand).read()) == 0:
                xvfbCommand = 'Xvfb -screen 0 1024x768x24 &';
                os.system(xvfbCommand);
        command = 'DISPLAY=:0 ' + command;
    print("Running osm2world for pov and opengl via:\n" + command);
    os.system(command)

    # then start povray to do the rest...
    #command = 'povray +W8192 +H8192 +B100 +A +FN -D "+I%s" + "+O%s"'
    #command = command % (povfile, povoutput);
    #print("Running povray for png output via:\n" + command);
    #os.system(command)

    # and finally generate the tiles...

    if ROTATABLE_MAP:
        generateTiles(outfile % 'n', x, y, parentDir + '/tiles/', 'n/', 'n')
        generateTiles(outfile % 's', x, y, parentDir + '/tiles/', 's/', 's')
        generateTiles(outfile % 'w', x, y, parentDir + '/tiles/', 'w/', 'w')
        generateTiles(outfile % 'e', x, y, parentDir + '/tiles/', 'e/', 'e')
    else:
        generateTiles(ogloutput, x, y, parentDir + '/tiles/', 'ogltiles/')
    #generateTiles(povoutput, x, y, parentDir + '/tiles/', 'povtiles/')

    if SCALE_IMAGES:
        # TODO: rerun with scaled tiles
        print("TODO: SCALE IMAGES AND RERUN GENERATETILES!")
        sys.exit();
    
    # cleanup
    if not KEEP_DATA:
        if ROTATABLE_MAP:
            ogloutput = (outfile % 'n')
            ogloutput += ' ' + (outfile % 's')
            ogloutput += ' ' + (outfile % 'w')
            ogloutput += ' ' + (outfile % 'e')
        command = 'rm %s %s %s' % (ogloutput, povoutput, povfile);
        print ("Going to clean up and remove temptiles:\n" + command);
        os.system(command);

# call main...
main()
