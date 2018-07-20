import cv2
import numpy as np
import json
import base64 #para conversao da imagem em uma string de 64 bits
from datetime import datetime

#Cria o arquivo .json
def criarJSON(somatorio,nMudancas,frameCapturado,tempoDeAnalise):
	buffer = "imagem"
	framestring = ""
	horarioDaAnalise = str(datetime.now())
	if frameCapturado is not None:
		retval,buffer = cv2.imencode('.jpg', frameCapturado)
		frameString = base64.b64encode(buffer)
	media = 0
	if nMudancas != 0:
		media = somatorio/nMudancas
	
	dados = {
		"numeroAproxPessoas": media,
		"duracaoDaAnalise":tempoDeAnalise,
		"imagemDaSala": frameString,
		"analiseFeitaEm": horarioDaAnalise
	}
	with open("dados.json","w") as f:
		json.dump(dados,f)


#Metodo de Felzenszwalb et al
#Junta os quadrados que se sobrepoem em um e retorna a lista
def non_max_suppression(boxes,overlapThresh=0.3):
	# se nao tem quadrados, retorna lista vazia
	if len(boxes) == 0:
		return []

	# Converte os valores para float, caso sejam inteiros
	if boxes.dtype.kind == "i":
		boxes = boxes.astype("float")

	# Lista de indices selecionados
	pick = []

	# Pego as coordenadas dos quadrados
	#O valor depois da "," eh o indice do valor na tupla
	x1 = boxes[:,0]
	y1 = boxes[:,1]
	x2 = boxes[:,2]
	y2 = boxes[:,3]

	#Calculo a area dos quadrados e dou um sort pela
	#coordenada Y do lado direito inferior
	area = (x2 - x1 + 1) * (y2 - y1 + 1)
	idxs = np.argsort(y2)


	while len(idxs) > 0:

		#Remove o ultimo valor da lista idxs e adiciona a "pick"
		last = len(idxs) - 1
		i = idxs[last]
		pick.append(i)

		# find the largest (x, y) coordinates for the start of
		# the bounding box and the smallest (x, y) coordinates
		# for the end of the bounding box
		xx1 = np.maximum(x1[i], x1[idxs[:last]])
		yy1 = np.maximum(y1[i], y1[idxs[:last]])
		xx2 = np.minimum(x2[i], x2[idxs[:last]])
		yy2 = np.minimum(y2[i], y2[idxs[:last]])

		# compute the width and height of the bounding box
		w = np.maximum(0, xx2 - xx1 + 1)
		h = np.maximum(0, yy2 - yy1 + 1)

		# compute the ratio of overlap
		overlap = (w * h) / area[idxs[:last]]

		# delete all indexes from the index list that have
		idxs = np.delete(idxs, np.concatenate(([last],
			np.where(overlap > overlapThresh)[0])))

	#Retorno os quadrados selecionados no "pick" nao esquecendo
	#de convertelos para int
	return boxes[pick].astype("int")

