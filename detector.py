import numpy as np
import cv2
import time
import json
from lib import filtros
from lib.videoStream import VideoStream

#Carregando o json num dicionario
config = json.load(open("config.json"))

#Verificando se o programa conseguiu acesso a camera
cameraEncontrada = True
try:
    vs = VideoStream(config["idCam"],config["cameraType"],config["resolucao"],config["taxaDeQuadros"],config["cameraURL"],config["login"],config["password"]).start()
except ImportError as e:
    print "Erro: ",e.message
    print "#Se estiver usando uma webcam nao esqueca de alterar a opcao piCamera para false"
    cameraEncontrada = False

if cameraEncontrada:
    #Inicializando ferramentas de deteccao e configuracoes
    time.sleep(config["warmUpCamera"])
    bsMog = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    pessoas = [] #Pessoas atualmente na imagem
    idBase = 0 #id da pessoa (chave)
    tempoMaximo = config["tempoMaximoDeVidaPessoa"] #tempo para delecao de uma pessoa do vetor
    tempoDeConfirmacao = config["tempoParaConfirmarPessoa"] #Tempo minimo (em frames) para ser considerado, como pessoa, no contador
    tempoAposDifDetect = config["tempoAnaliseAposDiferencaDetectada"]
    tempoInicio = time.time() #Tempo de inicio do programa
    tempoDoUltimoMovimento = time.time()-tempoAposDifDetect*10
    frameAnterior = None #Usado no feature matching
    frameParaExibir = None #Usado para desenhar os quadrados de deteccao

    #Calculo do numero de pessoas, utilizado na criacao do JSON
    resultadoDaAnalise = {
        "nPessoasFrameAnterior":0,#numero de pessoas confirmadas no frame anterior
        "somatorioDaAnalise": 0,#A cada vez que o numero de pessoas muda, ele recebe o NumeroDePessoas
        "contadorDeMudancas": 0,#Conta quantas vezes o contador de pessoas mudou
    }


    print("Iniciando:")

    while (True): #Loop principal, leitura do stream de video
        try:
            originalFrame = vs.read() #recebe o frame
            if originalFrame is None:
                break
            if frameAnterior is None: #Usado apenas na primeira iteracao
                frameAnterior = originalFrame.copy()       
            
            tempoInicio = filtros.conferirTempo(tempoInicio,config,resultadoDaAnalise,originalFrame)
            resultadoDaAnalise = filtros.verificarIdadeDasPessoas(pessoas,resultadoDaAnalise)

            if (filtros.possoAnalisar(tempoDoUltimoMovimento,tempoAposDifDetect)):
                imagemFiltrada = filtros.aplicarFiltrosNoFrame(originalFrame,bsMog,config) 
                caixas = filtros.selecionandoContornos(imagemFiltrada, config)
                idBase = filtros.processarCaixas(caixas, pessoas, idBase, config)
                frameParaExibir = filtros.desenharQuadrados(caixas, originalFrame, config)
            else:
                tempoDoUltimoMovimento = filtros.verificarMudancaFundo(frameAnterior,originalFrame,tempoDoUltimoMovimento)
                frameParaExibir = originalFrame.copy()
            frameAnterior = originalFrame.copy() #Atualiza o frame anterior
            cv2.imshow('frame',frameParaExibir) #Exibir imagem
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"): # apertar "q" sai do loop
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


