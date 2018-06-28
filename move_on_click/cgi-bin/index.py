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
    # Scale, in microns per pixel
    mppx = 8.00
    mppy = -7.90 
    width = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeX_RBV'))
    height = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeY_RBV'))

    x_mv = x_pc * width * mppx
    y_mv = y_pc * height * mppy

    x = x_mv/1000.0
    y = y_mv/1000.0

    caput(pv.me14e_stage_x + '.VAL', caget(pv.me14e_stage_x + '.RBV') + x)
    caput(pv.me14e_stage_y + '.VAL', caget(pv.me14e_stage_y + '.RBV') - y)
    print json.dumps([x_mv, y_mv, x, y])

#Crosshair
elif ty == 'centres':
    # Crosshair positions
    cx = 515.0
    cy = 377.0
    level = "1"
    width = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeX_RBV'))
    height = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeY_RBV'))
    print json.dumps([cx/width, cy/height, level])

exit()
