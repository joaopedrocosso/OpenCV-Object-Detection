import numpy as np
import cv2
import time
import json
from lib import mytools
from lib.pessoa import Pessoa
from lib.videoStream import VideoStream


#----------------------------------------------------------------------Funcoes
#----------------------------------------------------------------------
#----------------------------------------------------------------------

def confereTempo(tempoInicio,jsonOb,analise,ultimoFrame):
    #Se ja esta na hora de dormir
    if (time.time() - tempoInicio >= jsonOb["duracaoAnaliseSegundos"]):
        mytools.criarJSON(analise["somatorioDaAnalise"],analise["contadorDeMudancas"],ultimoFrame,jsonOb["duracaoAnaliseSegundos"])
        print("JSON criado")
        print("Dormindo...")
        cv2.destroyAllWindows()
        time.sleep(jsonOb["intervaloDescansoSegundos"]) #espera, em segundos, e recomeca
        print("Acordei")
        #Atualiza o tempo de inicio e o retorna
        tempoInicio = time.time()
    return tempoInicio


def atualizaContadoresEnvelhecePessoas(listaPessoas,analise):
    #Atualizando o numero atual de pessoas na tela
    #OBS as declaracoes abaixo sao para melhorar a leitura do codigo
    numeroAnteriorPessoas = analise["nPessoasFrameAnterior"]
    somatorio = analise["somatorioDaAnalise"]
    nMudancas = analise["contadorDeMudancas"]
    nPessoasNovo = 0
    for p in listaPessoas:
        if p.isConfirmado():
            nPessoasNovo+=1
    if nPessoasNovo != numeroAnteriorPessoas:
        #print "numero de pessoas:",numeroAnteriorPessoas
        numeroAnteriorPessoas = nPessoasNovo
        somatorio+=nPessoasNovo #atualizando o somatorio
        nMudancas+=1
    #Verificando/incrementando a idade as pessoas
    for p in listaPessoas:
        p.envelhece()
        if not p.isVivo():
            indice = listaPessoas.index(p)
            listaPessoas.pop(indice)
    analiseNova = {
        "nPessoasFrameAnterior": numeroAnteriorPessoas,
        "somatorioDaAnalise": somatorio ,
        "contadorDeMudancas": nMudancas
    }
    return analiseNova


def filtrarImagem(frame,backgroundSub,jsonObj):
    #mascara do backgroundsubtractor
    fgmask = backgroundSub.apply(frame)
    #Aplicando um threshold para limitar aos movimentos mais importantes
    ret,thresh = cv2.threshold(fgmask,jsonObj["deltaThreshold"],255,cv2.THRESH_BINARY)
    #Removo um pouco do "noise" criado pelo MOG2
    kernelOp = np.ones((3,3),np.uint8)#Kernel opening
    kernelCl = np.ones((11,11),np.uint8)#Kernel closing
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernelOp)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernelCl)
    return thresh


def selecionandoContornos(listaPessoas,listaContornos,jsonObj,chaves):
    #Atualiza a lista de pessoas (acrescentando ou renovando)
    caixas = []
    for c in listaContornos:
            # ignora os contornos menores que a area minima
            areaQuadrado = cv2.contourArea(c)
            if areaQuadrado > jsonObj["areaMinimaDeteccao"]:
                (x, y, w, h) = cv2.boundingRect(c)              
                caixas.append([x,y,w+x,h+y])
    #Transformo em um array do numpy para funcionar na non_max_supression
    caixas = np.array(caixas)
    #nonMaxSupression dos objetos (juntando caixas proximas)
    caixas = mytools.non_max_suppression(caixas,0.3)
    #Adaptando as coordenadas do array para guarda-lo no objeto pessoa
    #para cada objeto detectado em caixas:
    for (x,y,endX,endY) in caixas:
        novo = True
        cx = endX-(endX-x)/2#centro x
        cy = endY-(endY-y)/2#centro y
        w = endX-x#Largura
        h = endY-y#altura
        #Checando se o novo objeto ja existe ou esta proximo de uma pessoa
        for p in listaPessoas:
            #Se esta muito perto, ele nao eh novo. Ele eh uma pessoa que andou
            if (abs(x-p.x)<=w and abs(y-p.y)<=h):
                novo = False
                #Atualiza a lista de posicoes da pessoa, incrementa o
                #numero de frames que apareceu e reseta a idade
                p.atualiza(cx,cy)
                break
        #Se eh novo, entao criar nova pessoa
        #e atualizar o contador de chaves(IDs)
        if novo == True:
            p = Pessoa(chaves,cx,cy,tempoDeConfirmacao,tempoMaximo)
            listaPessoas.append(p)
            chaves+=1
    return caixas,chaves



def verificarMudancaFundo(frameAnterior,frameAtual,tempoUltimoMovimento,matchesAntigos):
    orb = cv2.ORB_create()
    kp1,des1 = orb.detectAndCompute(frameAnterior,None)
    kp2,des2 = orb.detectAndCompute(frameAtual,None)
    
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1,des2)
    #analisando mudanca
    diff = abs(len(matches) - matchesAntigos)
    ##TODO Checar precisao (100)
    if diff>100: #se mudou, atualiza o tempo de analise ativa
        return len(matches),time.time() 
    else:
        return len(matches),tempoUltimoMovimento

def desenharQuadrados(quadrados,frame):
    #Desenhando os quadrados
    frameparaDesenho = frame.copy()
    for (startX, startY, endX, endY) in quadrados:
            pXA = int(startX)
            pYA = int(startY)
            pXB = int(endX)
            pYB = int(endY)
            cv2.rectangle(frameparaDesenho, (pXA, pYA), (pXB, pYB), (0, 0, 255), conf["espessuraDosQuadrados"])
    return frameparaDesenho
'''    
def verificarMudancaFundo(frameAnterior,frameAtual,tempoUltimoMovimento,matchesAntigos):
    sift = cv2.xfeatures2d.SIFT_create()
    #Encontrando keypoints de cada frame
    kp1, des1 = sift.detectAndCompute(frameAnterior,None)
    kp2, des2 = sift.detectAndCompute(frameAtual,None)

    #Parametros do detector FLANN
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50) #checks = numero de matchs

    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    diff = abs(len(matches) - matchesAntigos)
    if diff>100: #se mudou, atualiza o tempo de analise ativa
        return len(matches),time.time() 
    else:
        return len(matches),tempoUltimoMovimento
'''
#----------------------------------------------------------------------Programa principal
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#Carregando o json num dicionario
conf = json.load(open("config.json"))

#Verificando se o programa conseguiu acesso a camera
cameraEncontrada = True
try:
    vs = VideoStream(conf["idCam"],conf["cameraType"],conf["resolucao"],conf["taxaDeQuadros"],conf["cameraURL"],conf["login"],conf["password"]).start()
except ImportError as e:
    print "Erro: ",e.message
    print "#Se estiver usando uma webcam nao esqueca de alterar a opcao piCamera para false"
    cameraEncontrada = False

if cameraEncontrada:
    time.sleep(conf["warmUpCamera"])

    #Ferramentas de deteccao e configuracoes
    bsMog = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    pessoas = [] #Pessoas atualmente na imagem
    idBase = 0 #id da pessoa
    tempoMaximo = conf["tempoMaximoDeVidaPessoa"] #tempo para delecao de uma pessoa do vetor
    tempoDeConfirmacao = conf["tempoParaConfirmarPessoa"] #Tempo minimo (em frames) para ser considerado, como pessoa, no contador
    tempoAposDifDetect = conf["tempoAnaliseAposDiferencaDetectada"]
    tempoInicio = time.time() #Tempo de inicio do programa
    tempoDoUltimoMovimento = time.time()-tempoAposDifDetect*10
    oldFrame = None #Usado no feature matching
    frameParaExibir = None #Usado para desenhar os quadrados de deteccao
    oldMatches = 0 #Usado para comparar os features dos frames (numero de pontos que "bateram")

    #Calculo do numero de pessoas
    variaveisDeAnalise = {
        "nPessoasFrameAnterior":0,#numero de pessoas confirmadas no frame anterior
        "somatorioDaAnalise": 0,#A cada vez que o numero de pessoas muda, ele recebe o tempoDePessoa*NumeroDePessoas
        "contadorDeMudancas": 0,#Conta quantas vezes o contador de pessoas mudou
    }


    print("Iniciando:")#Loop principal, leitura do stream de video
    
    while (True):
        try:
            originalFrame = vs.read() #recebe o frame
            if originalFrame is None:
                break
            if oldFrame is None:
                oldFrame = originalFrame.copy()
    
            
            
            #se o tempo atingiu o tempo maximo da analise do video, pausar
            tempoInicio = confereTempo(tempoInicio,conf,variaveisDeAnalise,originalFrame)

            #Atualiza os contadores e envelhece as pessoas da lista
            variaveisDeAnalise = atualizaContadoresEnvelhecePessoas(pessoas,variaveisDeAnalise)

            if (time.time() - tempoDoUltimoMovimento < tempoAposDifDetect):
                
                #Utilizando diversas funcoes para filtrar a imagem
                imagemFiltrada = filtrarImagem(originalFrame,bsMog,conf) 

                #Usar o contorno para achar os multiplos "borroes" e guardar em uma lista de contornos
                img,contornos,hie = cv2.findContours(imagemFiltrada,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

                #Verifica se os objetos selecionados pela funcao findContours ja existem ou sao novos
                caixas,idBase = selecionandoContornos(pessoas,contornos,conf,idBase)

                #Marca as posicoes
                #frameParaExibir = desenharQuadrados(caixas,originalFrame)

            else:
                #checa se houve alguma movimentacao recente
                oldMatches,tempoDoUltimoMovimento = verificarMudancaFundo(oldFrame,originalFrame,tempoDoUltimoMovimento,oldMatches)
                frameParaExibir = originalFrame.copy()

            oldFrame = originalFrame.copy()
            #Exibir imagem
            #cv2.imshow('frame',frameParaExibir)

            # apertar "q" sai do loop
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                    break
        except TypeError as e:
            print "Erro: ",e.message
            print "Imagem invalida ou corrompida, encerrando o programa"
            break
        except KeyboardInterrupt as e:
            print "Erro: ",e.message
            print "Tecla de saida detectada, encerrando"
            break
        except Exception as e:
            print "Erro: ",e.message
            break


    cv2.destroyAllWindows()
    vs.stop() #para o stream


