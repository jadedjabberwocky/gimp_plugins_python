#!/usr/bin/env python

# This plugin clones a path, for example a circle
# Every so often along another path

from gimpfu import *
import gimp

UNITS_PX=0
UNITS_MM=1
UNITS_INCHES=2
UNITS_COUNT=3
MM_PER_INCH=25.4

def add_path_to_path(new_path, clone_path, x, y):
    for clone_stroke in clone_path.strokes:
	(points,closed)=clone_stroke.points
        new_points=[]
        for i in range(0,len(points),6):
            xc1=points[i+0] + x
            yc1=points[i+1] + y
            xp0=points[i+2] + x
            yp0=points[i+3] + y
            xc2=points[i+4] + x
            yc2=points[i+5] + y
            new_points.extend([xc1, yc1, xp0, yp0, xc2, yc2])

        pdb.gimp_vectors_stroke_new_from_points(\
                new_path, \
                0, \
                len(new_points), \
                new_points, \
                closed)

def nmin(p1, p2):
    if p1==None:
        return p2
    if p2 < p1:
        return p2
    return p1

def nmax(p1, p2):
    if p1==None:
        return p2
    if p2 > p1:
        return p2
    return p1

def path_center(path):
    (x1, y1, x2, y2) = (None, None, None, None)
    for stroke in path.strokes:
	(points,closed)=stroke.points
        for i in range(0,len(points),6):
            xc1=points[i+0]
            yc1=points[i+1]
            xc2=points[i+4]
            yc2=points[i+5]

            x1 = nmin(x1, xc1)
            y1 = nmin(y1, yc1)
            x1 = nmin(x1, xc2)
            y1 = nmin(y1, yc2)

            x2 = nmax(x2, xc1)
            y2 = nmax(y2, yc1)
            x2 = nmax(x2, xc2)
            y2 = nmax(y2, yc2)

    return ((x1+x2) / 2, (y1+y2)/2)

def clone_path_along_path(\
    image, \
    drawable, \
    path_to_follow, \
    path_to_clone, \
    spacing, \
    units, \
    new_path_name):

    if path_to_follow==None:
        gimp.message("No path to follow")
        return 

    if not path_to_follow :
        gimp.message("No elements in path to follow")
        return

    if path_to_clone==None:
        gimp.message("No path to clone")
        return 

    if not path_to_clone :
        gimp.message("No elements in path to clone")
        return

    if new_path_name=="":
        new_path_name="%s-cloned" % path_to_clone.name

    # Check if new path exists
    for path in image.vectors:
        if path.name==new_path_name:
            gimp.message("Path \"%s\" already exists" % new_path_name)
            return

    new_path=pdb.gimp_vectors_new(image, new_path_name)
    new_path.visible=True
    pdb.gimp_image_add_vectors(image, new_path, 0)

    # Convert spacing from mm to px
    if units>UNITS_PX: 
        (xdpi, ydpi) = pdb.gimp_image_get_resolution(image)
        if units==UNITS_INCHES:
            # Inches to pixels
            spacing = xdpi * spacing
        elif units==UNITS_MM:
            # Millimeters to pixels
            spacing = (xdpi * spacing / MM_PER_INCH)

    # Get center of clone path
    (cx, cy) = path_center(path_to_clone)

    for follow_stroke in path_to_follow.strokes:
        # TODO: Figure out what .1 means
        length=follow_stroke.get_length(.1)

        if units==UNITS_COUNT:
            space=length/spacing
        else:
            space=spacing

	at=0
	while at < length:
		x,y,slope,valid=follow_stroke.get_point_at_dist(at,.1)
                add_path_to_path(new_path, path_to_clone, x-cx, y-cy)
                at=at+space

register(
    "clone_path_along_path",
    "Clones a path several times along another path",
    "Clones a path several times along another path",
    "Warren Hodgkinson",
    "Warren Hodgkinson",
    "2022",
    "<Image>/Filters/Paths/Clone path along path",
    "RGB*,GRAY*",
    [
        (PF_VECTORS, "refpath", "Path to follow", None),
        (PF_VECTORS, "clonepath", "Path to clone", None),
        (PF_FLOAT, "spacing", "Spacing between clones", 5),
        (PF_OPTION, "units", "Spacing units", 0, ["px", "mm", "inches", "count"]),
        (PF_STRING, "name", "Name of new path", ""),
    ],
    [],
    clone_path_along_path)

main()
