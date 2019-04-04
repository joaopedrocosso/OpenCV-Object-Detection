import cv2 as cv
from threading import Thread 

from exceptions.video_stream_exceptions import CannotOpenStreamError, StreamClosedError
from imagelib import ktools

class FileVideoStream:
	
	def __init__(self, src):

		if not isinstance(src, str):
			raise ValueError('"src" deve ser uma string.')

		#inicializa o streaming do arquivo de video
		self.stream = cv.VideoCapture(src)
		if not self.stream.isOpened():
			raise CannotOpenStreamError('Nao foi possivel abrir arquivo de video.')

		# frame inicializado com uma imagem preta
		self.frame = ktools.black_image(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT),
										self.stream.get(cv.CAP_PROP_FRAME_WIDTH))

		#Inicializando a variavel que indica a parada da thread
		self.stopped = False

	def start(self):
		#comeca a thread para ler os frames
		# Thread(target=self.update, args=()).start()
		return self

	def update(self):
		pass

	def read(self):

		if self.stopped:
			return
		ret, frame = self.stream.read()
		if not ret:
			self.stop()
			raise StreamClosedError('Stream foi fechado.')

		self.frame = frame
		return self.frame

	def stop(self):
		self.stopped = True
		self.stream.release()



#OBS: src pode variar entre int e string
#sendo string o path pro video