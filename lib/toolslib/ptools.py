import cv2
import json
import base64

from datetime import datetime

def criarJSON(dados, frame, path="dados.json"):
	'''Cria um JSON com uma imagem.
	
	Parameters
	-----------
	dados : dict
		Texto a colocar no JSON.
	frame : numpy.ndarray
		Imagem a ser colocada no JSON.
	path : str, optional
		Diretório onde o JSON será salvo.
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
	
	Parameters
	-----------
	frame : numpy.ndarray
		Imagem a ser convertida para string.

	Returns
	--------
	str
		Imagem convertida em string base64.
	'''

	if frame is not None:
		_,buffer = cv2.imencode('.jpg', frame)
		frameString = base64.b64encode(buffer).decode('utf-8')
	else:
		frameString = ''

	return frameString