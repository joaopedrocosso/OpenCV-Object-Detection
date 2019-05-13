import cv2
import numpy as np
import json
import base64 #para conversao da imagem em uma string de 64 bits
from datetime import datetime

def criarJSON(dados, frame, path="dados.json"):
	'''Cria um JSON com uma imagem.
	
	Parâmetros:
		'dados': (dict) texto a colocar no JSON.
		'frame': (numpy.ndarray) imagem a ser colocada no JSON.
		'path': (str) diretório onde o JSON será salvo.
	'''

	dados = dados.copy()

	horarioDaAnalise = str(datetime.now())
	frameString = criaFrameString(frame)
	
	dados['UltimoFrameCapturado'] = frameString
	dados['HorarioAnalise'] = horarioDaAnalise

	with open(path, "w") as f:
		json.dump(dados,f)

def criaFrameString(frame):
	'''Transforma uma imagem em uma string base64.
	
	Parâmetros:
		'frame': (numpy.ndarray) Imagem a ser convertida para string.

	Retorno:
		Imagem convertida em string base64.
	'''

	if frame is not None:
		_,buffer = cv2.imencode('.jpg', frame)
		frameString = base64.b64encode(buffer).decode('utf-8')
	else:
		frameString = ''

	return frameString