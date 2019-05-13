from threading import Thread 
import cv2 as cv

from imagelib import ktools
from .exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError
from . import auxiliares

class VideoStreamCV:
	
	def __init__(self, src=0, login=None, senha=None, atualiza_frames_auto=True):
		'''Pega frames de um dispositivo ou arquivo de vídeo.

		Parâmetros:
			'src': De onde pegar o vídeo. Pode ser um número ou uma string.
			'atualiza_frames_auto':
				Se 'True', os frames serão lidos em uma thread separada, automaticamente.
				Se 'False', a leitura é feita diretamente no método self.read().
			'login' e 'senha': Se ambos não forem 'None', o endereço de src recebe esses valores.
		
		Métodos:
			'start': Começa uma thread onde os frames serão lidos, se atualiza_frames_auto=True.
			'update': Lê frames da fonte até o stream ser fechado ou a leitura ser parada.
			'read': Lê o frame mais recente.
			'stop': Para a leitura.
		
		Levanta:
			'CannotOpenStreamError': Se não for possível abrir o stream.
		'''
		
		if login is not None and senha is not None:
			src = auxiliares.adiciona_autenticacao_url(src, login, senha)
		self.stream = cv.VideoCapture(src)
		if not self.stream.isOpened():
			raise CannotOpenStreamError('Não foi possível abrir vídeo da webcam.')
		
		# frame inicializado com uma imagem preta
		self.frame = ktools.black_image(self.stream.get(cv.CAP_PROP_FRAME_HEIGHT),
										self.stream.get(cv.CAP_PROP_FRAME_WIDTH))
		#Inicializando a variavel que indica a parada da thread
		self.stopped = False
		self.atualiza_frames_auto = atualiza_frames_auto

	def start(self):
		'''comeca a thread para ler os frames'''
		if self.atualiza_frames_auto:
			Thread(target=self.update, args=()).start()
		return self

	def update(self):
		'''Atualiza o frame mais recente em uma thread separada.'''
		while True:
			try:
				self._update_once()
			except (StreamStoppedError, StreamClosedError):
				break

	def read(self):
		'''Pega o frame mais recente do stream.

		Se o valor for atualizado automaticamente por self.update(), pega do
		self.frame(). Senão, pega direto da fonte.
		'''
		if self.stopped:
			raise StreamStoppedError('Leitura já parada.')
		
		if self.atualiza_frames_auto:
			return self.frame
		
		try:
			return self._update_once()
		except (StreamStoppedError, StreamClosedError):
			raise

	def stop(self):
		'''Para de pegar frames do stream.'''
		self.stopped = True
		if not self.atualiza_frames_auto:
			self.stream.release()

	def _update_once(self):
		'''Pega um frame do stream.
		
		Retorna o frame lido.

		Levanta StreamClosedError se a fonte está inacessível ou se não foi possível ler um frame da fonte.
		Levanta StreamStoppedError se a leitura já foi parada
		Em qualquer um dos casos, a leitura para e a fonte é liberada.
		'''
		if not self.stream.isOpened():
			self.stop()
			raise StreamClosedError('Stream fechado.')
		if self.stopped:
			self.stream.release()
			raise StreamStoppedError('Leitura já parada.')
		ret, frame = self.stream.read()
		if not ret:
			self.stop()
			raise StreamClosedError('Não foi possível ler frame do stream. Stream parado.')
		self.frame = frame
		return self.frame