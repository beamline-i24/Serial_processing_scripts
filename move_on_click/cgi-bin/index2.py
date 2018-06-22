#!/bin/env dls-python
import cgi, json

from pkg_resources import require
require('cothread')
from cothread.catools import caget, caput

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
    mpp = 1.46
    print mpp
    width = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeX_RBV'))
    height = float(caget('BL24I-DI-OAV-01:CAM:MaxSizeY_RBV'))

    x_mv = x_pc * width * mpp
    y_mv = y_pc * height * mpp

    x = x_mv/1000.0
    y = y_mv/1000.0

    #caput('BL24I-AL-GUARD-01:X.VAL', caget('BL24I-AL-GUARD-01:X.RBV') + x)
    #caput('BL24I-AL-GUARD-01:Y.VAL',  caget('BL24I-AL-GUARD-01:Y.RBV')  - y)
    caput('ME14E-MO-CHIP-01:X.VAL', caget('ME14E-MO-CHIP-01:X.RBV') + x)
    caput('ME14E-MO-CHIP-01:Y.VAL',  caget('ME14E-MO-CHIP-01:Y.RBV')  - y)
    print 'OAV json dumps: ', json.dumps([x_mv, y_mv, x, y])

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
