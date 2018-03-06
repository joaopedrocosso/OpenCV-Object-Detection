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
tempoMaximo = conf["tempoMaximoDeVida"] #tempo para delecao de uma pessoa do vetor
tempoDeConfirmacao = conf["tempoDeConfirmacao"] #Tempo minimo (em frames) para ser considerado, como pessoa, no contador
nPessoasFrameAnterior = 0 #numero de pessoas confirmadas no frame anterior
tempoInicio = time.time() #Tempo de inicio do programa

#Calculo do numero de pessoas
somatorioDaAnalise = 0 #A cada vez que o numero de pessoas muda, ele recebe o tempoDePessoa*NumeroDePessoas
contadorDeMudancas = 0 #Conta quantas vezes o contador de pessoas mudou


print("Iniciando:")
while (True):

    #se o tempo atingiu o tempo maximo da analise do video, pausar
    if (time.time() - tempoInicio >= conf["duracaoAnaliseSegundos"]):
        #FAZER MEDIA DAS INFORMACOES E GUARDAR NUM JSON
        print("Numero aproximado de pessoas em: ",conf["duracaoAnaliseSegundos"],"segundos","=",somatorioDaAnalise/contadorDeMudancas)
        print("Dormindo...")
        cv2.destroyAllWindows()
        time.sleep(conf["intervaloDescansoSegundos"]) #espera, em segundos, e recomeca
        print("Acordei")
        tempoInicio = time.time()

    originalFrame = vs.read() #recebe o frame
    if (originalFrame == None):
        break

    #Le o numero de pessoas ativas e exibe
    nPessoasNovo = 0
    for p in pessoas:
        if p.isConfirmado():
            nPessoasNovo+=1

    if nPessoasNovo != nPessoasFrameAnterior:
        print "numero de pessoas:",nPessoasFrameAnterior
        nPessoasFrameAnterior = nPessoasNovo

        somatorioDaAnalise+=nPessoasNovo #atualizando o somatorio
        contadorDeMudancas+=1

    #Verificando/incrementando a idade as pessoas
    for p in pessoas:
        p.envelhece()
        if not p.isVivo():
            indice = pessoas.index(p)
            pessoas.pop(indice)

    #mascara do backgroundsubtractor
    fgmask = fgbg.apply(originalFrame)

    #Aplicando um threshold para limitar aos movimentos mais importantes
    ret,thresh = cv2.threshold(fgmask,conf["deltaThreshold"],255,cv2.THRESH_BINARY)

    #Removo um pouco do "noise" criado pelo MOG2
    kernelOp = np.ones((3,3),np.uint8)#Kernel opening
    kernelCl = np.ones((11,11),np.uint8)#Kernel closing
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernelOp)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernelCl)

    #Usar o contorno para achar os multiplos "borroes"
    #e guardar em contours
    img,contours,hie = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)


    #Verificar o tamanho das areas, se for menor ignorar.
    caixas = []
    for c in contours:
            # ignora os contornos menores que a area minima
            if cv2.contourArea(c) < conf["areaMinimaDeteccao"]:
                continue
            (x, y, w, h) = cv2.boundingRect(c)              
            caixas.append([x,y,w+x,h+y])


    #Transformo em um array do numpy para funcionar na non_max_supression
    caixas = np.array(caixas)

    #nonMaxSupression dos objetos
    caixas = mytools.non_max_supression(caixas,0.3)

    for (x,y,endX,endY) in caixas:
        novo = True
        cx = endX-(endX-x)/2#centro x
        cy = endY-(endY-y)/2#centro y
        w = endX-x#Largura
        h = endY-y#altura

        #Checando se a nova coordenada faz parte das pessoas
        for p in pessoas:
            cv2.circle(originalFrame,(cx,cy), 5, (0,0,255), -1) #Desenha o centro de massa
            #Se ele ja existe
            if (abs(x-p.x)<=w and abs(y-p.y)<=h):
                novo = False
                p.atualiza(cx,cy)#tambem atualiza o numero de frames que a pessoa apareceu
                break

        #Se eh novo, entao eu crio uma nova pessoa
        if novo == True:
            p = Pessoa(idBase,cx,cy,tempoDeConfirmacao,tempoMaximo)
            pessoas.append(p)
            idBase+=1



    #Desenhando os quadrados
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


