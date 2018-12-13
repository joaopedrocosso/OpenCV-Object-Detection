import numpy as np
import cv2
import time
from lib import mytools
from lib.pessoa import Pessoa

# Conjunto de funcoes utilizadas dentro do loop principal da camera com o objetivo de extrair os dados da imagem e processa-los 
# Atualizando a lista de Pessoas 


# se o tempo atingiu o tempo maximo da analise do video, pausar
# caso contrario, retorna o mesmo tempo que foi passado como parametro
def conferirTempo(tempoInicio,conf,analise,ultimoFrame):
    # Se ja esta na hora de dormir
    if (time.time() - tempoInicio >= conf["duracaoAnaliseSegundos"]):
        mytools.criarJSON(analise["somatorioDaAnalise"],analise["contadorDeMudancas"],ultimoFrame,conf["duracaoAnaliseSegundos"])
        print("JSON criado")
        print("Dormindo...")
        cv2.destroyAllWindows()
        time.sleep(conf["intervaloDescansoSegundos"]) # espera, em segundos, e recomeca
        print("Acordei")
        # Atualiza o tempo de inicio
        tempoInicio = time.time()
    return tempoInicio


# Atualiza os contadores e envelhece as pessoas da lista
def verificarIdadeDasPessoas(listaPessoas,analise):
    numeroAnteriorPessoas = analise["nPessoasFrameAnterior"]
    somatorio = analise["somatorioDaAnalise"]
    nMudancas = analise["contadorDeMudancas"]
    nPessoasNovo = 0
    for p in listaPessoas:
        if p.isConfirmado():
            nPessoasNovo+=1
    if nPessoasNovo != numeroAnteriorPessoas:
        # print "numero de pessoas:",numeroAnteriorPessoas
        numeroAnteriorPessoas = nPessoasNovo
        somatorio+=nPessoasNovo # atualizando o somatorio [verificar a formula]
        nMudancas+=1
    # Verificando/incrementando a idade as pessoas
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


# Utilizando diversas funcoes para filtrar o frame
def aplicarFiltrosNoFrame(frame,backgroundSub,conf):
    # mascara do backgroundsubtractor
    fgmask = backgroundSub.apply(frame)
    # Aplicando um threshold para limitar aos movimentos mais importantes
    _,frameAlterado = cv2.threshold(fgmask,conf["deltaThreshold"],255,cv2.THRESH_BINARY)
    # Removo um pouco do "noise" criado pelo MOG2
    kernelOp = np.ones((3,3),np.uint8)# Kernel opening
    kernelCl = np.ones((11,11),np.uint8)# Kernel closing
    frameAlterado = cv2.morphologyEx(frameAlterado, cv2.MORPH_CLOSE, kernelCl)
    frameAlterado = cv2.morphologyEx(frameAlterado, cv2.MORPH_OPEN, kernelOp)
    return frameAlterado


# Retorna as caixas encontradas pela funcao findContours() do OpenCV, aplicando
# a tecnica de non max suppression
def selecionandoContornos(frame,conf):
    caixas = []
    _,listaContornos,_ = cv2.findContours(frame,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for c in listaContornos:
            # ignora os contornos menores que a area minima
            areaQuadrado = cv2.contourArea(c)
            if areaQuadrado > conf["areaMinimaDeteccao"]:
                (x, y, w, h) = cv2.boundingRect(c)              
                caixas.append([x,y,w+x,h+y])
    # Transformo em um array do numpy para funcionar na non_max_supression
    caixas = np.array(caixas)
    # nonMaxSupression dos objetos (juntando caixas proximas)
    caixas = mytools.non_max_suppression(caixas,0.3)
    return caixas


# Verificar nas caixas encontradas, se alguma pessoa eh nova/velha e atualizar dados
def processarCaixas(caixas, listaPessoas, chaves, conf):
    # Adaptando as coordenadas do array para guarda-lo no objeto pessoa
    # para cada objeto detectado em caixas:
    for (startX,startY,endX,endY) in caixas:
        novo = True
        cx = endX-(endX-startX)/2#centro x
        cy = endY-(endY-startY)/2#centro y
        w = endX-startX#Largura
        h = endY-startY#altura
        # Checando se o novo objeto ja existe ou esta proximo de uma pessoa
        for p in listaPessoas:
            # Se esta muito perto, ele nao eh novo. Ele eh uma pessoa que andou
            if (abs(cx-p.x)<=w and abs(cy-p.y)<=h):
                novo = False
                # Atualiza a lista de posicoes da pessoa, incrementa o
                # numero de frames que apareceu e reseta a idade
                p.atualiza(cx,cy)
                break
        # Se eh novo, entao criar nova pessoa
        # e atualizar o contador de chaves(IDs)
        if novo == True:
            p = Pessoa(chaves,cx,cy,conf["tempoParaConfirmarPessoa"],conf["tempoMaximoDeVidaPessoa"])
            listaPessoas.append(p)
            chaves+=1
    return chaves


# Checa se houve alguma movimentacao recente
def verificarMudancaFundo(frameAnterior,frameAtual,tempoUltimoMovimento):
    orb = cv2.ORB_create()
    kp1,des1 = orb.detectAndCompute(frameAnterior,None)
    kp2,des2 = orb.detectAndCompute(frameAtual,None)
    
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1,des2)
    
    # analisando mudanca
    nMatches = len(matches)
    if nMatches<=430: # se mudou, atualiza o tempo de analise ativa (430 eh um valor temporario)
        return time.time() 
    else:
        return tempoUltimoMovimento

# Diz se o programa pode ou nao aplicar os filtros no frame para
# extracao dos dados
def possoAnalisar(tempoDoUltimoMovimento, tempoAposDifDetect):
    return time.time() - tempoDoUltimoMovimento < tempoAposDifDetect

# Desenhando os quadrados
def desenharQuadrados(quadrados,frame,conf):
    frameparaDesenho = frame.copy()
    for (startX, startY, endX, endY) in quadrados:
            pXA = int(startX)
            pYA = int(startY)
            pXB = int(endX)
            pYB = int(endY)
            cv2.rectangle(frameparaDesenho, (pXA, pYA), (pXB, pYB), (0, 0, 255), conf["espessuraDosQuadrados"])
    return frameparaDesenho
