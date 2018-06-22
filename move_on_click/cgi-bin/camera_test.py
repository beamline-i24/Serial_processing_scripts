import cv2
import urllib 
import numpy as np
from ca import caget, caput

camera='http://'+str(caget('ME14E-DI-CAM-01:MJPG:HOST_RBV'))+':'+str(caget('ME14E-DI-CAM-01:MJPG:HTTP_PORT_RBV'))+'/cam'+str(caget('ME14E-DI-CAM-01:MJPG:CLIENTS_RBV'))+'.mjpg.mjpg'
stream=urllib.urlopen(camera)
bytes=''
while True:
    bytes+=stream.read(1024)
    a = bytes.find('\xff\xd8')
    print a
    b = bytes.find('\xff\xd9')
    print b
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imshow(camera,i)
        if cv2.waitKey(1) ==27:
           exit(0)  
