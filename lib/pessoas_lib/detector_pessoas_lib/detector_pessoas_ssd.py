import os
import cv2 as cv
import numpy as np

from imagelib import ktools

class DetectorPessoasSSD:

	DEFAULT_PRECISAO_DETECCAO = 0.5
	DEFAULT_SUPRESSAO_DETECCAO = 0.5

	_RESINA_NET_ARQUIVO_MODEL = 'MobileNetSSD_deploy.caffemodel'
	_RESINA_NET_ARQUIVO_PROTOTXT = 'MobileNetSSD_deploy.prototxt'

	def __init__(self, mobile_ssd_path, precisao_minima=DEFAULT_PRECISAO_DETECCAO,
				 supressao_caixas=DEFAULT_SUPRESSAO_DETECCAO):

		prototxt = os.path.join(mobile_ssd_path, DetectorPessoasSSD._RESINA_NET_ARQUIVO_PROTOTXT)
		caffemodel = os.path.join(mobile_ssd_path, DetectorPessoasSSD._RESINA_NET_ARQUIVO_MODEL)
		self.net = cv.dnn.readNetFromCaffe(prototxt, caffemodel)

		self.precisao_minima = precisao_minima
		self.supressao_caixas = supressao_caixas


	def detecta_pessoas(self, img, desenha_retangulos=True):

		detections = self._analisa_imagem(img)

		caixas, precisoes = self._seleciona_pessoas(img, detections)
		caixas_com_peso = list(zip(caixas, precisoes))

		if desenha_retangulos:
			nova_img = ktools.draw_rectangles(img, caixas_com_peso)
			return nova_img, caixas_com_peso
		else:
			return img, caixas_com_peso


	def _analisa_imagem(self, img):

		blob = cv.dnn.blobFromImage(cv.resize(img, (300, 300)), 0.007843,
									(300, 300), 127.5)
		self.net.setInput(blob)
		return self.net.forward()


	_ID_PESSOA = 15

	def _seleciona_pessoas(self, img, detections):

		img_h, img_w = img.shape[:2]

		caixas = []
		precisoes = []

		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with the
			# prediction
			confidence = detections[0, 0, i, 2]
		 
			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence >= self.precisao_minima:
				# extract the index of the class label from the `detections`,
				# then compute the (x, y)-coordinates of the bounding box for
				# the object
				idx = int(detections[0, 0, i, 1])
				if idx != DetectorPessoasSSD._ID_PESSOA:
					continue
				box = detections[0, 0, i, 3:7] * np.array([img_w, img_h, img_w, img_h])
				startX, startY, endX, endY = box.astype("int")
				startX, startY, endX, endY = int(startX), int(startY), int(endX), int(endY)

				caixas.append([startX, startY, endX-startX, endY-startY])
				precisoes.append(float(confidence))

		#  Remove caixas com baixas probabilidades de serem pessoas e
		# funde caixas muito proximas.
		idxs = ktools.non_maxima_suppression(caixas, precisoes, self.precisao_minima, self.supressao_caixas)
		caixas = [caixas[i] for i in idxs]
		precisoes = [precisoes[i] for i in idxs]

		return caixas, precisoes
