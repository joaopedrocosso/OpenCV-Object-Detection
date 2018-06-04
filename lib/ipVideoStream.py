import base64
import time
import urllib2
import cv2
import numpy as np
from threading import Thread 

class IPVideoStream:
    def __init__(self,url,login,password):
        self.url = url
        self.login = login
        self.password = password
        auth_encoded = base64.encodestring('%s:%s' % (self.login, self.password))[:-1]
        self.req = urllib2.Request(self.url)
        self.req.add_header('Authorization', 'Basic %s' % auth_encoded)
        self.frame = self.read
        self.stopped = False
    def start(self):
        Thread(target=self.update,args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return 
            return self.frame
    def read(self):
        response = urllib2.urlopen(self.req)
        img_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
        self.frame = cv2.imdecode(img_array, 1)
        return self.frame
    def stop(self):
        self.stopped = True
