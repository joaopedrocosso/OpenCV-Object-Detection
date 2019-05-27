import cv2 as cv
from threading import Thread
from abc import ABC, abstractmethod

from imagelib import ktools
from .exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError
from . import auxiliares

class AbstractVideoStream(ABC):
	
	'''Classe abstrada para criação 
	
	Raises
	-------
	CannotOpenStreamError
		Se não for possível abrir o stream.
	'''

	@abstractmethod
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
		pass

	@abstractmethod
	def stop(self):
		'''Para de pegar frames do stream.'''
		pass

	@abstractmethod
	def pega_dimensoes(self):
		'''Retorna as dimensões dos frames do vídeo
		Returns
		--------
		(int, int)
		'''
		pass