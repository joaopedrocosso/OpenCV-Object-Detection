import numpy as np
import cv2
import time
import json
from lib import mytools
from lib.pessoa import Pessoa
from lib.videoStream import VideoStream


conf = json.load(open("config.json"))

vs = VideoStream(conf["idWebcam"],conf["piCamera"],conf["resolucao"],conf["taxaDeQuadros"]).start()
time.sleep(conf["tempoDeInicializacao"])

fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

# inicializando o HOG descriptor/detector pre-treinado de pessoas
hog = cv2.HOGDescriptor()
pessoas = [] #Pessoas atualmente na imagem
candidatos = [] #Candidatos a pessoas
idBase = 0 #id da pessoa
tempoMaximo = conf["tempoMaximoDeVida"] #tempo de duracao (em frames) de uma pessoa na tela
tempoMinimo = conf["tempoMinimoDeVida"] #Tempo minimo (em frames) para ser considerado no contador
nPessoasFrameAnterior = 0

while (True):

    originalFrame = vs.read() #recebe o frame
    if (originalFrame == None):
        break

    if nPessoasFrameAnterior != len(pessoas):
        nPessoasFrameAnterior = len(pessoas)
        print "numero de pessoas:",nPessoasFrameAnterior

    #Verificando a idade dos candidatos
    for c in candidatos:
        c.envelhece()
        if not c.vivo:
            indice = candidatos.index(c)
            candidatos.pop(indice)

    #Verificando a idade das pessoas
    for p in pessoas:
        p.envelhece()
        if not p.vivo:
            indice = pessoas.index(p)
            pessoas.pop(indice)


    #Essas razoes sao multiplicadas nas coordenadas para que os
    #quadrados fiquem no lugar certo no frame

    #mascara do backgroundsubtractor
    fgmask = fgbg.apply(originalFrame)

    #Aplicando um threshold para limitar aos movimentos mais importantes
    ret,thresh = cv2.threshold(fgmask,conf["deltaThreshold"],255,cv2.THRESH_BINARY)

    #Removo um pouco do noise criado pelo MOG2
    kernelOp = np.ones((3,3),np.uint8)#Kernel opening
    kernelCl = np.ones((11,11),np.uint8)#Kernel closing
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernelOp)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernelCl)

    #Depois de remover tudo o que poderia ser falso
    #Dilato o que pode ser verdadeiro para facilitar a deteccao

    #Dilato os brancos para serem melhor detectados
    #thresh = cv2.dilate(thresh, None, iterations=1)

    #Aplico um blur na imagem
    #thresh = cv2.bilateralFilter(thresh,11,17,17)#rever os parametros

    #Usar o contorno para achar os multiplos "borroes"
    #e guardar em contours
    img,contours,hie = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)


    #Verificar o tamanho das areas, se for menor ignorar.
    caixas = []
    for c in contours:
            # ignora os contornos menores que a area minima
            if cv2.contourArea(c) < conf["areaMinimaDeteccao"]:
                continue
            #Pega as coordenadas do contorno c
            M = cv2.moments(c) #Pegando o centro da imagem
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            (x, y, w, h) = cv2.boundingRect(c)
            novo = True
            existe = False #se ele pode sair dos candidatos
            candidatoPromovido = None #O candidato que passou para a lista de pessoas
            cv2.circle(originalFrame,(cx,cy), 5, (0,0,255), -1) #Desenha o centro de massa

            #Checando se a nova coordenada faz parte de algum candidato
            for i in candidatos:
                if (abs(x-i.x)<=w and abs(y-i.y)<=h):
                    novo = False #Esta muito perto de um quadrado anterior
                    i.atualiza(cx,cy)#Atualizo a posicao desse quadrado e saio
                    if i.confirmado: #Se ele foi confirmado e esta nos candidatos, eu vejo se ele ja existe nas pessoas
                        for p in pessoas:
                            if (abs(x-p.x)<=w and abs(y-p.y)<=h):
                                p.atualiza(cx,cy)#Se ele existe em pessoas eu atualizo a respectiva pessoa
                                indice = candidatos.index(i)
                                candidatos.pop(indice) #e deleto ele dos candidatos
                            else:
                                existe = True
                                candidatoPromovido = i
                    break
            #Checando se a nova coordenada faz parte das pessoas
            for p in pessoas:
                if (abs(x-p.x)<=w and abs(y-p.y)<=h):
                    novo = False
                    p.atualiza(cx,cy)

            #Se eh novo, entao eu crio um novo candidato
            if novo == True:
                p = Pessoa(idBase,cx,cy,tempoMinimo,tempoMaximo)
                candidatos.append(p)
                idBase+=1
            #Se ele foi confirmado E nao existia no vetor de pessoas    
            else: 
                if existe:
                    indice = candidatos.index(candidatoPromovido)
                    candidatos.pop(indice)#tiro ele dos candidatos
                    pessoas.append(candidatoPromovido)#e promovo ele para pessoas
                    
            caixas.append([x,y,w+x,h+y])


    #Transformo em um array do numpy para funcionar na non_max_supression
    caixas = np.array(caixas)

    #nonMaxSupression dos objetos
    caixas = mytools.non_max_supression(caixas,0.3)

    #Desenhando os quadrados
    #print "Objetos em movimento = ",len(caixas)
    for (startX, startY, endX, endY) in caixas:
            pXA = int(startX)
            pYA = int(startY)
            pXB = int(endX)
            pYB = int(endY)
            cv2.rectangle(originalFrame, (pXA, pYA), (pXB, pYB), (0, 0, 255), conf["espessuraDosQuadrados"])

    
    cv2.imshow('frame',originalFrame)

    # apertar "q" sai do loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
            break


cv2.destroyAllWindows()
vs.stop() #para o stream
