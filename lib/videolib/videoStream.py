from .ipVideoStream import IPVideoStream
from .webcamVideoStream import WebcamVideoStream
from .fileVideoStream import FileVideoStream

class VideoStream:

	def __init__(self, tipo, **keywords):

		'''Lê um vídeo de uma fonte.
		
		Parâmetros:
			tipo: Tipo de entrada. Pode ser 'picamera', 'ipcamera', 'webcam' e 'arquivo'.

			Se o tipo for 'picamera':
				'resolucao': Tupla que representa a resolução do vídeo. Ex.: (320, 240).
				'fps': Frames por segundo.
			Se o tipo for 'ipcamera':
				'cameraURL': Url da câmera.
				'login': Login da câmera.
				'senha': Senha da câmera.
			Se o tipo for 'webcam':
				'idCam' (padrão=0): Número da câmera.
			Se o tipo for 'arquivo':
				'arquivo': Caminho ao arquivo.

		Métodos:
			'start': Começa o stream. Retorna a si mesmo.
			'read': Retorna o frame atual do vídeo.
			'stop': Para o stream.
		'''
		
		if tipo == 'picamera':
			from .piVideoStream import PiVideoStream
			self.stream = PiVideoStream(keywords['resolucao'], keywords['fps'])
		elif tipo == 'ipcamera':
			self.stream = IPVideoStream(keywords['cameraURL'], keywords['login'], keywords['senha'])
		elif tipo == 'webcam':
			if 'idCam' not in keywords:
				keywords['idCam'] = 0
			self.stream = WebcamVideoStream(src=keywords['idCam'])
		elif tipo == 'arquivo':
			self.stream = FileVideoStream(src=keywords['arquivo'])
		else:
			raise ValueError('Tipo de camera invalido.')

	def start(self):
		return self.stream.start()

	def read(self):
		return self.stream.read()

	def stop(self):
		self.stream.stop()