import os
import cv2 as cv
import numpy as np

from imagelib import ktools

class DetectorPessoasYolo:

	DEFAULT_PRECISAO_DETECCAO = 0.5
	DEFAULT_SUPRESSAO_DETECCAO = 0.5

	_YOLO_ARQUIVO_PESOS = 'yolov3.weights'
	_YOLO_ARQUIVO_CONFIG = 'yolov3.cfg'

	def __init__(self, yolo_path, precisao_minima=DEFAULT_PRECISAO_DETECCAO,
				 supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		config_path = os.path.join(yolo_path, DetectorPessoasYolo._YOLO_ARQUIVO_CONFIG)
		pesos_path = os.path.join(yolo_path, DetectorPessoasYolo._YOLO_ARQUIVO_PESOS)
		self.net = cv.dnn.readNetFromDarknet(config_path, pesos_path)

		self.ln = self.net.getLayerNames()
		self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

		self.precisao_minima = precisao_minima
		self.supressao_caixas = supressao_caixas


	def detecta_pessoas(self, img, desenha_retangulos=True):

		layer_outputs = self._analisa_imagem(img)

		caixas, precisoes = self._seleciona_pessoas(img, layer_outputs)

		nova_img = ktools.draw_rectangles(img, caixas, precisoes)

		caixas_com_peso = list(zip(caixas, precisoes))
		if desenha_retangulos:
			return nova_img, caixas_com_peso
		else:
			return img, caixas_com_peso


	def _analisa_imagem(self, img):

		blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
		self.net.setInput(blob)
		return self.net.forward(self.ln)


	_ID_PESSOA = 0

	def _seleciona_pessoas(self, img, layer_outputs):

		img_h, img_w = img.shape[:2]

		caixas = []
		precisoes = []

		for output in layer_outputs:
			for detection in output:

				scores = detection[5:]
				classID = np.argmax(scores)
				precisao = scores[classID]

				# Nao registra se nao for pessoa.
				if classID != DetectorPessoasYolo._ID_PESSOA:
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

		#  Remove caixas com baixas probabilidades de serem pessoas e
		# funde caixas muito proximas.
		idxs = ktools.non_maxima_suppression(caixas, precisoes, self.precisao_minima, self.supressao_caixas)
		caixas = [caixas[i] for i in idxs]
		precisoes = [precisoes[i] for i in idxs]

		return caixas, precisoes