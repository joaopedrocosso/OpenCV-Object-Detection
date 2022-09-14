# Referência:
# 	https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/
# 	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/

import os
import cv2 as cv
import numpy as np

from imagelib import ktools
from .detector_objetos_base import BaseDetectorObjetos, DEFAULT_PRECISAO_DETECCAO, DEFAULT_SUPRESSAO_DETECCAO

class DetectorObjetosYolo(BaseDetectorObjetos):

	'''Detecta objetos usando um modelo YOLO.

	Parameters
	-----------
	yolo_path : str
		Destino do modelo desejado.
	precisao_minima : float, optional
		Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0
		incl. (Padrão=0.5)
	supressao_caixas : float, optional
		Quão próximas as detecções de objetos devem estar para
		serem consideradas o mesmo objeto. Deve estar entre 0.0 e 1.0
		incl. (Padrão=0.5)

	Raises
	--------
	Exceções relacionadas ao OpenCV.
	'''

	_YOLO_ARQUIVO_PESOS = 'yolov3.weights'
	_YOLO_ARQUIVO_CONFIG = 'yolov3.cfg'
	_COCO_LABELS = 'coco.names'

	def __init__(
		self, yolo_path, rotulos=['person'], precisao_minima=DEFAULT_PRECISAO_DETECCAO,
		supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		super().__init__(precisao_minima, supressao_caixas)

		config_path = os.path.join(yolo_path, DetectorObjetosYolo._YOLO_ARQUIVO_CONFIG)
		pesos_path = os.path.join(yolo_path, DetectorObjetosYolo._YOLO_ARQUIVO_PESOS)
		self.net = cv.dnn.readNetFromDarknet(config_path, pesos_path)

		coco_labels_path = os.path.join(yolo_path, DetectorObjetosYolo._COCO_LABELS)
		with open(coco_labels_path, 'r') as coco_labels:
			self.todos_rotulos = coco_labels.read().strip().split("\n")
		self.rotulos_a_usar = rotulos
		'''
		Variáveis adicionadas:
		'''
		ln = self.net.getLayerNames()
		self.ln = []
		'''
		Código Anterior:
		self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
		Código modificado: 
		'''
		for i in self.net.getUnconnectedOutLayers():
			(self.ln).append(ln[i - 1])


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

		dados_relevantes = self._analisa_imagem(img)
		caixas_precisoes_rotulos = self._seleciona_objetos(img, dados_relevantes)
		return caixas_precisoes_rotulos

	def _analisa_imagem(self, img):
		'''Analiza uma imagem e retorna dados relevantes

		Parameters
		-----------
		img: numpy.ndarray de dimensões (n, m, 3)
			Imagem a ser analizada. (formato BGR)

		Returns
		--------
		dados_relevantes : [numpy.ndarray de floats, ...]
			Dados de análise da imagem.
		'''
		blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
		self.net.setInput(blob)
		return self.net.forward(self.ln)


	def _seleciona_objetos(self, img, dados_relevantes):
		'''Seleciona os objetos desejados em uma imagem.
		
		Parameters
		-----------
		img : numpy.ndarray de dimensões (n, m, 3)
			Imagem de onde serão selecionadas os objetos. (formato BGR)
		dados_relevantes
			Dados relevantes para o selecionamento de objetos.

		Returns
		--------
		caixas_precisoes_rotulos : {'rotulo':([(int, int, int, int), ...], [float, ...]), ...}
			Dicionário de tuplas para cada rótulo. Cada rótulo 
			disponível contém uma array de coordenadas (caixas) dos
			objetos e outra com suas respectivas probabilidades de 
			serem esse objeto.
		'''

		img_h, img_w = img.shape[:2]

		caixas_precisoes_rotulos = {rotulo:([], []) for rotulo in self.rotulos_a_usar}

		for output in dados_relevantes:
			for detection in output:

				scores = detection[5:]
				classID = np.argmax(scores)
				precisao = scores[classID]
				id_string = self.todos_rotulos[classID]

				# Nao registra se nao for objeto.
				if id_string not in self.rotulos_a_usar:
					continue

				# Nao registra se precisao for baixa.
				if precisao <= self.precisao_minima:
					continue

				box = detection[:4] * np.array([img_w, img_h, img_w, img_h])
				centro_x, centro_y, w, h = box.astype('int')

				x = int(centro_x - (w/2))
				y = int(centro_y - (h/2))

				caixas_precisoes_rotulos[id_string][0].append([x, y, int(w), int(h)])
				caixas_precisoes_rotulos[id_string][1].append(float(precisao))

		for rotulo in caixas_precisoes_rotulos:
			caixas_precisoes_rotulos[rotulo] = self._non_maxima_suppression(*caixas_precisoes_rotulos[rotulo])
		return caixas_precisoes_rotulos