# Referência:
# 	https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/
# 	https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/

import os
import cv2 as cv
import numpy as np

from .detector_pessoas_base import BaseDetectorPessoas, DEFAULT_PRECISAO_DETECCAO, DEFAULT_SUPRESSAO_DETECCAO

class DetectorPessoasYolo(BaseDetectorPessoas):

	'''Detecta pessoas usando um modelo YOLO.

	Parameters
	-----------
	yolo_path : str
		Destino do modelo desejado.
	precisao_minima : float, optional
		Quão precisa a detecção deve ser. Deve estar entre 0.0 e
		1.0 incl. (Padrão=Mesmo que o DetectorPessoasBase)
	supressao_caixas : float, optional
		Quão próximas as detecções de pessoas devem estar para
		serem consideradas as mesmas. Deve estar entre 0.0 e 1.0
		incl. (Padrão=Mesmo que o DetectorPessoasBase)

	Raises
	--------
	Exceções relacionadas ao OpenCV.
	'''

	_YOLO_ARQUIVO_PESOS = 'yolov3.weights'
	_YOLO_ARQUIVO_CONFIG = 'yolov3.cfg'

	def __init__(self, yolo_path, precisao_minima=DEFAULT_PRECISAO_DETECCAO,
				 supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		super().__init__(precisao_minima, supressao_caixas)

		config_path = os.path.join(yolo_path, DetectorPessoasYolo._YOLO_ARQUIVO_CONFIG)
		pesos_path = os.path.join(yolo_path, DetectorPessoasYolo._YOLO_ARQUIVO_PESOS)
		self.net = cv.dnn.readNetFromDarknet(config_path, pesos_path)

		self.ln = self.net.getLayerNames()
		self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]


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

		ID_PESSOA = 0

		img_h, img_w = img.shape[:2]

		caixas = []
		precisoes = []

		for output in dados_relevantes:
			for detection in output:

				scores = detection[5:]
				classID = np.argmax(scores)
				precisao = scores[classID]

				# Nao registra se nao for pessoa.
				if classID != ID_PESSOA:
					continue

				# Nao registra se precisao for baixa.
				if precisao <= self.precisao_minima:
					continue

				box = detection[:4] * np.array([img_w, img_h, img_w, img_h])
				centro_x, centro_y, w, h = box.astype('int')

				x = int(centro_x - (w/2))
				y = int(centro_y - (h/2))

				caixas.append([x, y, int(w), int(h)])
				precisoes.append(float(precisao))

		caixas, precisoes = self._non_maxima_suppression(caixas, precisoes)
		return caixas, precisoes