#!/usr/bin/python2.7
"""
split an svg into 256x256 tiles, save tiles according to slippy map convention
usage: chmod +wx <script>; ./<script> <svg file>
"""
import cairo
import rsvg
import sys
import math
import os
import tilenames

SVG_INFILE = sys.argv[-1]   # i know...
LAT_START, LNG_START = (48.806863, -124.628906) # NW corner lat/lng of your svg layer
ZOOM_MIN, ZOOM_MAX = (11,12)

print "[*] reading svg", SVG_INFILE, ":",
handler = rsvg.Handle(SVG_INFILE)
src = handler.props
print src.width, "x", src.height

"""
- Tiles are 256 x 256 pixel PNG files
- Each zoom level is a directory, each column is a subdirectory, and each tile 
  in that column is a file.
- Filename(url) format is /zoom/x/y.png
"""
tile_width, tile_height = (256, 256)
scale_level = None

for zoom in xrange(ZOOM_MIN, ZOOM_MAX+1):
    if not scale_level:
        scale_level = 1.0
    else:
        scale_level *= 2.0

    zoomed_width = int(math.ceil(src.width * scale_level))
    zoomed_height = int(math.ceil(src.height * scale_level))

    # write the svg to a surface
    print "[*] creating cairo surface",
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, zoomed_width, zoomed_height)
    ctx = cairo.Context(img)
    # scale the SVG
    ctx.scale(scale_level, scale_level)
    #img.write_to_png("img-rescaled-pre-render.png")
    print "... done"
    print "[*] rendering svg",
    handler.render_cairo(ctx)
    print "... done"
    #img.write_to_png("img-rescaled-post-render.png")

    tiles_x = int(math.ceil(float(zoomed_width) / tile_width))     # columns
    tiles_y = int(math.ceil(float(zoomed_height) / tile_height))   # rows

    print "[*] baking %d columns and %d rows, total of %d tiles" % (tiles_x, tiles_y, tiles_x*tiles_y)

    zoom_dir = os.path.join("output", str(zoom))
    if not os.path.exists(zoom_dir):
        os.makedirs(zoom_dir)

    # need to calculate lat/lng + zoom -> row, col, and add those to the incrementors
    # uncomment the following two lines to enable this functionality (broken):
    #x,y = tilenames.tileXY(LAT_START, LNG_START, zoom)
    #column_start, row_start = (x,y)
    # comment this line if the above two are uncommented:
    column_start, row_start = (0,0)

    for column in xrange(tiles_x):

        column += column_start
        
        col_dir = os.path.join(zoom_dir, str(column))
        if not os.path.exists(col_dir):
            os.makedirs(col_dir)

        for row in xrange(tiles_y):

            row += row_start

            tile = cairo.ImageSurface(cairo.FORMAT_ARGB32, tile_width, tile_height)
            tilectx = cairo.Context(tile)

            # http://lists.cairographics.org/archives/cairo/2007-June/010877.html
            src_x, src_y, dest_x, dest_y = (tile_width*column, tile_height*row, 0, 0)
            tilectx.set_source_surface(img, dest_x-src_x, dest_y-src_y)
            tilectx.rectangle(dest_x, dest_y, tile_width, tile_height)
            tilectx.fill()

            # write rendered tile to png file
            tile_filename = os.path.join(col_dir, "%d.png" % row)
            tile.write_to_png(tile_filename)
            print "[*] wrote %s" % tile_filename

print "done"
