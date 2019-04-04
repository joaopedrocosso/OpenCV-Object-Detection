from threading import Thread 
import cv2 as cv

from imagelib import ktools
from exceptions.video_stream_exceptions import CannotOpenStreamError, StreamClosedError

class WebcamVideoStream:
	
	def __init__(self, src=0):
		
		# inicializa o streaming de video
		self.stream = cv.VideoCapture(src)
		if not self.stream.isOpened():
			raise CannotOpenStreamError('Nao foi possivel abrir video da webcam.')
		
		# frame inicializado com uma imagem preta
		self.frame = ktools.black_image(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT),
										self.stream.get(cv.CAP_PROP_FRAME_WIDTH))

		#Inicializando a variavel que indica a parada da thread
		self.stopped = False

	def start(self):
		#comeca a thread para ler os frames
		Thread(target=self.update, args=()).start()
		return self

	def update(self):

		#Manter o loop indefinidamente ate a thread parar
		while self.stream.isOpened():
			if self.stopped:
				break
			ret, frame = self.stream.read()
			if not ret:
				self.stop()
				raise StreamClosedError('Stream foi fechado.')
			self.frame = frame

		self.stream.release()
		if self.stopped:
			return

		self.stream.release()

	def read(self):
		#retorna a frame mais recente
		return self.frame

	def stop(self):
		self.stopped = True



#OBS: src pode variar entre int e string
#sendo string o path pro video