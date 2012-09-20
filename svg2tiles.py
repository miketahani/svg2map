#!/usr/bin/python2.7
"""
split an svg into 256x256 tiles, save tiles according to slippy map convention
usage: chmod +wx <script>; ./<script> <svg file>
"""
import cairo
import rsvg
import sys
import os
import webbrowser
import shutil
from math import *

# following functions are by Oliver White, 2007:
def numTiles(z):
    return(pow(2,z))

def sec(x):
    return(1/cos(x))

def latlon2relativeXY(lat,lon):
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return(x,y)

def latlon2xy(lat,lon,z):
    n = numTiles(z)
    x,y = latlon2relativeXY(lat,lon)
    return(n*x, n*y)
  
def tileXY(lat, lon, z):
    x,y = latlon2xy(lat,lon,z)
    return(int(x),int(y))

SVG_INFILE = sys.argv[-1]   # i know...
LAT_START, LNG_START = (48.356249, -124.694824) # NW corner lat/lng of your svg layer
ZOOM_MIN, ZOOM_MAX = (11,12)
LAUNCH_WHEN_FINISHED = True # launch a webbrowser with the rendered tiles

"""
- Tiles are 256 x 256 pixel PNG files
- Each zoom level is a directory, each column is a subdirectory, and each tile 
  in that column is a file.
- Filename(url) format is /zoom/x/y.png
"""
tile_width, tile_height = (256, 256)

# the base directory where the tiles will go
base_dir = os.path.join("example", "output")
if os.path.exists(base_dir):
    shutil.rmtree(base_dir)
os.makedirs(base_dir)

print "[*] reading svg", SVG_INFILE, ":",
handler = rsvg.Handle(SVG_INFILE)
src = handler.props
print src.width, "x", src.height

scale_level = None
for zoom in xrange(ZOOM_MIN, ZOOM_MAX+1):
    if not scale_level:
        scale_level = 1.0
    else:
        scale_level *= 2.0

    zoomed_width = int(ceil(src.width * scale_level))
    zoomed_height = int(ceil(src.height * scale_level))

    # write the svg to a surface
    print "[*] creating cairo surface",
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, zoomed_width, zoomed_height)
    ctx = cairo.Context(img)
    # scale the SVG
    ctx.scale(scale_level, scale_level)
    print "... done"
    print "[*] rendering svg",
    handler.render_cairo(ctx)
    print "... done"

    tiles_x = int(ceil(float(zoomed_width) / tile_width))     # columns
    tiles_y = int(ceil(float(zoomed_height) / tile_height))   # rows

    print "[*] baking %d columns and %d rows, total of %d tiles" % (tiles_x, tiles_y, tiles_x*tiles_y)

    zoom_dir = os.path.join(base_dir, str(zoom))
    if not os.path.exists(zoom_dir):
        os.makedirs(zoom_dir)

    # calculate lat/lng + zoom -> row, col, and add those to the incrementors
    x,y = tileXY(LAT_START, LNG_START, zoom)
    column_start, row_start = (x,y)
    print "[-] (start) column %d, row %d" % (column_start, row_start)

    for column_iter in xrange(tiles_x):

        column = column_iter + column_start
        
        col_dir = os.path.join(zoom_dir, str(column))
        if not os.path.exists(col_dir):
            os.makedirs(col_dir)

        for row_iter in xrange(tiles_y):

            row = row_iter + row_start

            tile = cairo.ImageSurface(cairo.FORMAT_ARGB32, tile_width, tile_height)
            tilectx = cairo.Context(tile)

            # http://lists.cairographics.org/archives/cairo/2007-June/010877.html
            src_x, src_y, dest_x, dest_y = (tile_width*column_iter, tile_height*row_iter, 0, 0)
            tilectx.set_source_surface(img, dest_x-src_x, dest_y-src_y)
            tilectx.rectangle(dest_x, dest_y, tile_width, tile_height)
            tilectx.fill()

            # write rendered tile to png file
            tile_filename = os.path.join(col_dir, "%d.png" % row)
            tile.write_to_png(tile_filename)
            print "[*] wrote %s" % tile_filename

print "done"
if LAUNCH_WHEN_FINISHED:
    print "[*] launching browser"
    url = "http://localhost:8080/#%.2f/%.4f/%.4f" % (ZOOM_MIN, LAT_START, LNG_START)
    webbrowser.open_new(url)