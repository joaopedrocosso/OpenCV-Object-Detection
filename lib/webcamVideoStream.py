from threading import Thread 
import cv2


class WebcamVideoStream:
	def __init__(self,src=0):

		#inicializa o streaming de video e
		#le o primeiro frame
		self.stream = cv2.VideoCapture(src)
		(self.grabbed,self.frame) = self.stream.read()

		#Inicializando a variavel que indica a parada
		#da thread
		self.stopped = False

	def start(self):
		#comeca a thread para ler os frames
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		#Manter o loop indefinidamente ate a thread parar
		while True:
			if self.stopped:
				return
			(self.grabbed,self.frame) = self.stream.read()

	def read(self):
		#retorna a frame mais recente
		return self.frame

	def stop(self):
		self.stopped = True



#OBS: src pode variar entre int e string
		#sendo string o path pro video