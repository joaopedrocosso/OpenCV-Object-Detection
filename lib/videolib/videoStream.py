from .ipVideoStream import IPVideoStream
from .webcamVideoStream import WebcamVideoStream
from .fileVideoStream import FileVideoStream

class VideoStream:

	from .enums import Entrada as Tipo

	def __init__(self,idCam=0,resolucao=(320,240),fps=32,cameraURL="algumip",login="teste",senha="teste", tipo=Tipo.WEBCAM):
		
		if tipo == VideoStream.Tipo.PICAMERA:
			from .piVideoStream import PiVideoStream
			self.stream = PiVideoStream(resolution=resolucao, framerate=fps)
		elif tipo == VideoStream.Tipo.IPCAMERA:
			self.stream = IPVideoStream(cameraURL, login, senha)
		elif tipo == VideoStream.Tipo.WEBCAM:
			self.stream = WebcamVideoStream(src=idCam)
		elif tipo == VideoStream.Tipo.ARQUIVO:
			self.stream = FileVideoStream(src=idCam)
		else:
			raise ValueError('Tipo de camera invalido.')

	def start(self):
		return self.stream.start()

	def update(self):
		self.stream.update()

	def read(self):
		return self.stream.read()

	def stop(self):
		self.stream.stop()