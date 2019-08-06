# Referência:
# 	https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/
# 	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/
#	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/

import cv2 as cv
from abc import ABC, abstractmethod

from imagelib import ktools

DEFAULT_PRECISAO_DETECCAO = 0.5
DEFAULT_SUPRESSAO_DETECCAO = 0.5

class BaseDetectorObjetos(ABC):

	'''Detecta objetos usando um modelo de deep learning.

	Parameters
	-----------
	precisao_minima : float, optional
		Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0
		incl. (Padrão=0.5)
	supressao_caixas : float, optional
		Quão próximas as detecções de objetos devem estar para
		serem consideradas as mesmas. Deve estar entre 0.0 e 1.0 incl.
		(Padrão=0.5)
	'''

	def __init__(self, precisao_minima=DEFAULT_PRECISAO_DETECCAO,
				 supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		self.precisao_minima = precisao_minima
		self.supressao_caixas = supressao_caixas

	@abstractmethod
	def detectar(self, img):
		'''Detecta objetos em uma imagem.

		Parameters
		-----------
		img : numpy.ndarray
			Imagem a ser analizada.
		
		Returns
		--------
		caixas_precisoes_rotulos : {'rotulo':([(int, int, int, int), ...], [float, ...]), ...}
			Dicionário de tuplas para cada rótulo. Cada rótulo 
			disponível contém uma array de coordenadas (caixas) dos
			objetos e outra com suas respectivas probabilidades de 
			serem esse objeto.
		'''
		pass

	def _non_maxima_suppression(self, caixas, precisoes):
		'''
		Remove caixas com baixa probabilidade de serem um dos 
		objetos desejados e funde caixas muito próximas.
		
		Parameters
		-----------
		caixas : [(int, int, int, int), ...]
			Caixas que representam objetos, na forma (x, y, w, h).
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