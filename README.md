#svg2map
convert conditionally-styled SVG to raster map tiles. 

###huh?
* rip SVG layer out of the frontend 
* strip out anything you don't want
* add XML headers to the SVG data, save as a .svg
* get the lat/lng coordinate pair of the NW corner of your SVG bounding box
* modify the script to fit your data
* run script, get tiles 

###requirements
needs pycairo (`easy_install pycairo`) and the python bindings for librsvg (`sudo apt-get install python-rsvg`).

###todo
* render only a specified extent of the SVG
* some way to tie geojson, svg, and this script together without so much work on the part of the user
