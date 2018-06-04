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
        bytes = ''
        #A url da camera IP envia o fluxo de video .mjpeg
        ipStream = urllib2.urlopen(self.req)
        while True:
            if self.stopped:
                return
            bytes+=ipStream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True
