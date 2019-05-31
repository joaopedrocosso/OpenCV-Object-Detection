# Referência:
# 	https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/
# 	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/
#	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/

import cv2 as cv
from abc import ABC, abstractmethod

from imagelib import ktools

DEFAULT_PRECISAO_DETECCAO = 0.5
DEFAULT_SUPRESSAO_DETECCAO = 0.5

class BaseDetectorPessoas(ABC):

	'''Detecta pessoas usando um modelo de deep learning.

	Parameters
	-----------
	precisao_minima : float, optional
		Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0
		incl. (Padrão=0.5)
	supressao_caixas : float, optional
		Quão próximas as detecções de pessoas devem estar para
		serem consideradas as mesmas. Deve estar entre 0.0 e 1.0 incl.
		(Padrão=0.5)
	'''

	def __init__(self, precisao_minima=DEFAULT_PRECISAO_DETECCAO,
				 supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		self.precisao_minima = precisao_minima
		self.supressao_caixas = supressao_caixas


	def detecta_pessoas(self, img, desenha_retangulos=True):
		'''Detecta pessoas em uma imagem.

		Parameters
		-----------
		img : numpy.ndarray
			Imagem a ser analizada.
		desenha_retangulos : bool, optional
			Se deve retornar uma imagem com as pessoas enquadradas.
			(Padrão=True)
		
		Returns
		--------
		img : numpy.ndarray
			Imagem com as pessoas enquadradas, se 'desenha_retangulos'
			for True. Caso contrário, é a imagem original.
		caixas : [(int, int, int, int), ...]
			Caixas que representam pessosa em uma imagem. Cada tupla 
			é composta por (x, y, w, h), ou seja, as coordenadas x e y,
			a largura e a altura.
		precisoes : [float, ...]
			A probabilidade de cada caixa ser uma pessoa. Os valores 
			variam entre 0.0 e 1.0.
		'''

		dados_relevantes = self._analisa_imagem(img)

		caixas, precisoes = self._seleciona_pessoas(img, dados_relevantes)

		if desenha_retangulos:
			nova_img = ktools.draw_boxes(img, caixas, precisoes)
			return nova_img , caixas, precisoes
		else:
			return img, caixas, precisoes

	@abstractmethod
	def _analisa_imagem(self, img):
		'''Analiza uma imagem e retorna dados relevantes

		Parameters
		-----------
		img: numpy.ndarray de dimensões (n, m, 3)
			Imagem a ser analizada. (formato BGR)

		Returns
		--------
		dados_relevantes
			Dados de análise da imagem.
		'''
		pass

	@abstractmethod
	def _seleciona_pessoas(self, img, dados_relevantes):
		'''Seleciona as pessoas da imagem.
		
		Parameters
		-----------
		img : numpy.ndarray de dimensões (n, m, 3)
			Imagem de onde serão selecionadas as pessoas. (formato BGR)
		dados_relevantes
			Dados relevantes para o selecionamento de pessoas.

		Returns
		--------
		caixas : [(int, int, int, int), ...]
			Caixas que representam pessoas, na forma (x, y, w, h).
		precisoes : [float, ...]
			Precisões de cada caixa.
		'''
		pass

	def _non_maxima_suppression(self, caixas, precisoes):
		'''Remove caixas com baixa probabilidade de serem pessoas e funde caixas muito próximas.
		
		Parameters
		-----------
		caixas : [(int, int, int, int), ...]
			Caixas que representam pessoas, na forma (x, y, w, h).
		precisoes : [float, ...]
			Precisões de cada caixa.
		
		Returns
		--------
		caixas : [(int, int, int, int), ...]
			Caixas resultantes.
		precisoes : [float, ...]
			Precisões de cada caixa resultante.
		'''

		idxs = ktools.non_maxima_suppression(caixas, precisoes, self.precisao_minima, self.supressao_caixas)
		caixas = [caixas[i] for i in idxs]
		precisoes = [precisoes[i] for i in idxs]
		return caixas, precisoes