import cv2 as cv
import json
import base64

from datetime import datetime

def criarJSON(dados, frame, path="dados.json"):
	'''Cria um JSON com uma imagem.
	
	Parameters
	-----------
	dados : dict
		Campos do JSON.
	path : str, optional
		Diretório onde o JSON será salvo.
	'''

	with open(path, "w") as f:
		json.dump(dados,f)


def criaImagemString(imagem):
	'''Transforma uma imagem em uma string base64.
	
	Parameters
	-----------
	imagem : numpy.ndarray
		Imagem a ser convertida para string.

	Returns
	--------
	str
		Imagem convertida em string base64.
	'''

	if imagem is not None:
		_,buffer = cv.imencode('.jpg', framem)
		imagemString = base64.b64encode(buffer).decode('utf-8')
	else:
		imagemString = ''

	return imagemString