import cv2 as cv
import threading
from threading import Thread 

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

	def __init__(self, src=0, atualiza_frames_auto=True):

		super().__init__()

		self.stream = cv.VideoCapture(src)
		if not self.stream.isOpened():
			raise CannotOpenStreamError('Não foi possível abrir vídeo da webcam.')

		self.dimensoes_frame = (self.stream.get(cv.CAP_PROP_FRAME_WIDTH),
								self.stream.get(cv.CAP_PROP_FRAME_HEIGHT))
		
		self.frame = ktools.black_image(*self.dimensoes_frame)
		
		self.stopped = False
		self.atualiza_frames_auto = atualiza_frames_auto

		# Só usado se 'atualiza_frames_auto' for False.
		self.threads_que_usaram_o_frame_atual = set()
		self.lock = threading.Lock()
	
	def restart(self):
		pass
		

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
			return self._read_compartilhado()
		except (StreamStoppedError, StreamClosedError):
			self.stop()
			raise

	def stop(self):
		'''Para de pegar frames do stream.'''
		self.stopped = True
		if not self.atualiza_frames_auto:
			self.stream.release()


	def _read_compartilhado(self):
		'''
		Lê um frame novo do arquivo, se a thread que chamou o método 
		já leu o último frame guardado, ou retorna o frame atual, se
		a thread ainda não o leu.

		Returns
		--------
		frame : numpy.ndarray
			Um frame.
		
		Raises
		-------
		StreamClosedError
			Se a fonte está inacessível ou se não foi possível ler um
			frame da fonte.
		StreamStoppedError
			Se a leitura já foi parada.
		'''
		thread_atual = threading.current_thread().name
		with self.lock:
			if thread_atual in self.threads_que_usaram_o_frame_atual:
				self.threads_que_usaram_o_frame_atual = set()
				try:
					self._update_once()
				except (StreamClosedError, StreamStoppedError):
					raise
			self.threads_que_usaram_o_frame_atual.add(thread_atual)
		return self.frame

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