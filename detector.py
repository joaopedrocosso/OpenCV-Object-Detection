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
idBase = 0 #id da pessoa
tempoMaximo = conf["tempoMaximoDeVida"] #tempo de duracao de uma pessoa na tela

while (True):
        
        originalFrame = vs.read() #recebe o frame
        if (originalFrame == None):
        	break

        #O tamanho eh alterado para facilitar a deteccao
        #No final a imagem exibida eh a originalFrame
        frame = mytools.resize(originalFrame,width=400)

        #Calculo de escala da imagem resized para a do frame
        razao_x = originalFrame.shape[1]/frame.shape[1]
        razao_y = originalFrame.shape[0]/frame.shape[0]
        #Essas razoes sao multiplicadas nas coordenadas para que os
        #quadrados fiquem no lugar certo no frame

        #mascara do backgroundsubtractor
        fgmask = fgbg.apply(frame)

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
                for i in pessoas:
                    if (abs(x-i.x)<=w and abs(y-i.y)<=h):
                        novo = False #Esta muito perto de um quadrado anterior
                        i.atualiza(cx,cy)#Atualizo a posicao desse quadrado e saio
                        break
                if novo == True:#Se eh novo, entoa eu crio uma pessoa nova
                    p = Pessoa(idBase,cx,cy,tempoMaximo)
                    pessoas.append(p)
                    idBase+=1
                caixas.append([x,y,w+x,h+y])


        #Transformo em um array do numpy para funcionar na non_max_supression
        caixas = np.array(caixas)

        #nonMaxSupression dos objetos
        caixas = mytools.non_max_supression(caixas,0.3)

        #Desenhando os quadrados
        #print "Objetos em movimento = ",len(caixas)
        for (startX, startY, endX, endY) in caixas:
                pXA = int(startX*razao_x)
                pYA = int(startY*razao_y)
                pXB = int(razao_x*endX)
                pYB = int(razao_y*endY)
                cv2.rectangle(originalFrame, (pXA, pYA), (pXB, pYB), (0, 0, 255), conf["espessuraDosQuadrados"])

        #Deteccao opcional
        #Detectando pessoas na imagem original(funciona a parte da imagem alterada)
        '''
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        (rects,weights) = hog.detectMultiScale(frame, winStride=(4, 4),
                                                                padding=(8, 8), scale=1.05)

        rects = np.array([[x, y, (x + w), (y + h)] for (x, y, w, h) in rects])
        pick = mytools.non_max_supression(rects,0.65) #Para corrigir falsas deteccoes do HOG

        #Desenhando os quadrados
        print "Supostas pessoas = ",len(pick)
        pick = np.array([[int((x)*razao_x), int(y*razao_y), int(razao_x*(x + w)), int(razao_y*(y + h))] for (x, y, w, h) in pick])
        for (xA, yA, xB, yB) in pick:
                cv2.rectangle(originalFrame, (xA, yA), (xB, yB), (255, 255, 0), conf["espessuraDosQuadrados"])
        '''


        
        cv2.imshow('frame',originalFrame)

        # apertar "q" sai do loop
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
                break


cv2.destroyAllWindows()
vs.stop() #para o stream
