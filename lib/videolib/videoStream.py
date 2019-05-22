from .ipVideoStream import IPVideoStream
from .webcamVideoStream import WebcamVideoStream
from .fileVideoStream import FileVideoStream

class VideoStream:

	def __init__(self, tipo, **keywords):

		'''Lê um vídeo de uma fonte.

		Interface entre os objetos de leitura de vídeo e o usuário.
		
		Parameters
		-----------
		tipo : {'picamera', 'ipcamera', 'webcam' e 'arquivo'}
			Tipo de leitor de vídeo. Dependo do tipo escolhido, certos
			argumentos são obrigatórios.

			Se for 'picamera', os atributos 'resolucao' e 'fps' devem
			ser fornecidos.

			Se for 'ipcamera', os atributos 'cameaURL', 'login' e
			'senha' devem ser fornecidos.

			Se for 'webcam', o atributo 'idCam' deve ser fornecido.
			Se for 'arquivo', o atributo 'arquivo' deve ser fornecido.

		resolucao : 'tuple' ['int'], optional
			2-upla que representa a resolução do vídeo.
		fps : int, optional
			Frames por segundo.
		cameraURL : str, optional
			Url ou IP da câmera.
		login : str, optional
			Login da câmera.
		senha : str, optional
			Senha da câmera.
		idCam : int, optional
			Número da câmera. (padrão=0)
		arquivo : str
			Caminho ao arquivo.

		Raises
		-------
		CannotOpenStreamError
			Se não for possível abrir o stream.
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
		'''Pega o frame mais recente do stream.

		Returns
		--------
		self
		'''
		return self.stream.start()

	def read(self):
		'''Atualiza o frame mais recente em uma thread separada.

		Returns
		--------
		self
		'''
		return self.stream.read()

	def stop(self):
		'''Para de pegar frames do stream.'''
		self.stream.stop()