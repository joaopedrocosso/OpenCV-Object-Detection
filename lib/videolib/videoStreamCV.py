from threading import Thread 
import cv2 as cv

from . import auxiliares
from .abstractVideoStream import AbstractVideoStream
from .exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError
from imagelib import ktools

class VideoStreamCV(AbstractVideoStream, Thread):
	
	'''Pega frames de um dispositivo ou arquivo de vídeo.

	Parameters
	----------
	src : str or int, optional
		De onde pegar o vídeo. (Padrão=0)
	login, senha: str, optional
		Se ambos forem disponibilizados, o endereço de src recebe
		esses valores. (Padrão=None)
	atualiza_frames_auto : bool, optional
		Se 'True', os frames serão lidos em uma thread separada,
		automaticamente. Se 'False', a leitura é feita diretamente
		no método self.read(). (Padrão=True)
	
	Raises
	-------
	CannotOpenStreamError
		Se não for possível abrir o stream.
	'''

	def __init__(self, src=0, login=None, senha=None, atualiza_frames_auto=True):

		super().__init__()
		
		if login is not None and senha is not None:
			src = auxiliares.adiciona_autenticacao_url(src, login, senha)
		self.stream = cv.VideoCapture(src)
		if not self.stream.isOpened():
			raise CannotOpenStreamError('Não foi possível abrir vídeo da webcam.')

		self.dimensoes_frame = (self.stream.get(cv.CAP_PROP_FRAME_WIDTH),
								self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))
		
		# frame inicializado com uma imagem preta
		self.frame = ktools.black_image(*self.dimensoes_frame)
		#Inicializando a variavel que indica a parada da thread
		self.stopped = False
		self.atualiza_frames_auto = atualiza_frames_auto

	def start(self):
		'''
		Começa a thread para ler os frames, se 'atualiza_frames_auto'
		for verdadeiro.

		Returns
		--------
		self
		'''
		if self.atualiza_frames_auto:
			super().start()
		return self

	def pega_dimensoes(self):
		'''Retorna as dimensões dos frames do vídeo
		Returns
		--------
		(int, int)
			Largura e altura, respectivamente.
		'''
		return self.dimensoes_frame

	def run(self):
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

		Returns
		-------
		frame : numpy.ndarray
			O último frame do stream.

		Raises
		------
		StreamStoppedError
			Se o stream já está parado.
		StreamClosedError
			Se o stream já está fechado.
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
		
		Returns
		-------
		frame : numpy.ndarray
			O último frame do stream.

		Raises
		------
		StreamClosedError
			Se a fonte está inacessível ou se não foi possível ler um
			frame da fonte.
		StreamStoppedError
			Se a leitura já foi parada.
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