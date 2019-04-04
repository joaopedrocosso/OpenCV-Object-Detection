import cv2 as cv
from threading import Thread

from imagelib import ktools
from exceptions.video_stream_exceptions import CannotOpenStreamError, StreamClosedError
from . import auxiliares

class IPVideoStream:
    def __init__(self,url,login,password):
        
        self.url = url
        self.login = login
        self.password = password
        
        # Abre stream
        self.stream = cv.VideoCapture(auxiliares.adiciona_autenticacao_url(url, login, password))
        if not self.stream.isOpened():
            raise CannotOpenStreamError('Nao foi possivel abrir video da camera IP.')
        
        # frame inicializado com uma imagem preta
        self.frame = ktools.black_image(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT),
                                        self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
        
        #Inicializando a variavel que indica a parada da thread
        self.stopped = False
    
    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        
        while self.stream.isOpened():
            if self.stopped:
                break
            ret, frame = self.stream.read()
            if not ret:
                self.stop()
                raise StreamClosedError('Stream foi fechado.')
            self.frame = frame

        self.stream.release()

            
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True