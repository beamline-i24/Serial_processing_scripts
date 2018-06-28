#!/bin/env dls-python
import cgi, json
import pv
from ca import caget, caput

print "Content-type:application/json"
print

q = cgi.FieldStorage()
ty = q.getvalue('ty')
v = q.getvalue('val')

# OAV
if ty == 'oav':
    x_pc = float(q.getvalue('x'))
    y_pc = float(q.getvalue('y'))
    w = float(q.getvalue('w'))
    h = float(q.getvalue('h'))
    # Scale, in microns per pixel
    zoom = float(caget('BL24I-EA-OAV-01:FZOOM:ZOOMPOSCMD'))
    mppx = -1.862 #hardcode if zoom level approximation fails; use 0.874 for 3 etc
    mppy = -1.862
    if zoom == 1.0:
         mppx = -1.862
         mppy = -1.862
    elif zoom == 20.0:
         mppx = -1.138
         mppy = -1.138
    elif zoom == 30.0:
         mppx = -0.874
         mppy = -0.874
    elif zoom == 40.0:
         mppx = -0.682
         mppy = -0.682
    elif zoom == 50.0:
         mppx = -0.525
         mppy = -0.525
    elif zoom == 65.0:
         mppx = -0.354
         mppy = -0.354
    elif zoom == 80.0:
         mppx = -0.252
         mppy = -0.252
    elif zoom == 90.0:
         mppx = -0.195
         mppy = -0.195
    elif zoom == 100.0:
         mppx = -0.16
         mppy = -0.16
    #if x_pc < 0:    
    #    mppx = -0.874#-1.020#19.25 #zoom level 3 should be 0.874
    #else:
    #    mppx = -0.874#18.56#0.888
    #if y_pc < 0:
    #    mppy = -0.874#-0.780#19.0
    #else:
    #	mppy = -0.874#-0.615#16.20 
    width = float(caget('BL24I-DI-OAV-02:CAM:MaxSizeX_RBV'))#'ME14E-DI-CAM-02:CAM:MaxSizeX_RBV'))#
    height = float(caget('BL24I-DI-OAV-02:CAM:MaxSizeY_RBV'))#'ME14E-DI-CAM-02:CAM:MaxSizeY_RBV'))#

    x_mv = x_pc * width * mppx
    y_mv = y_pc * height * mppy

    x = x_mv/1000.0
    y = y_mv/1000.0

    caput(pv.me14e_stage_x + '.VAL', caget(pv.me14e_stage_x + '.RBV') - x)
    caput(pv.me14e_stage_y + '.VAL', caget(pv.me14e_stage_y + '.RBV') - y)
    print json.dumps([x_mv, y_mv, x, y, width, height])

#Crosshair
elif ty == 'centres':
    # Crosshair positions
    cx=float(q.getvalue('cx'))
    cy=float(q.getvalue('cy'))
    #cx = 646.0
    #cy = 482.0
    level = "1"

    width = float(caget('BL24I-DI-OAV-02:CAM:MaxSizeX_RBV'))#'ME14E-DI-CAM-02:CAM:MaxSizeX_RBV'))#'ME14E-DI-CAM-03:CAM:WidthMax_RBV'))#
    height = float(caget('BL24I-DI-OAV-02:CAM:MaxSizeY_RBV'))#'ME14E-DI-CAM-02:CAM:MaxSizeY_RBV'))#'ME14E-DI-CAM-03:CAM:HeightMax_RBV'))#
    print json.dumps([cx/width, cy/height, level])

exit()
