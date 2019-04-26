import time
import json
import sys
import argparse
import cv2 as cv
import os
import datetime

from imagelib import ktools, ptools
from imagelib.detector_movimento import DetectorMovimento
from videolib.videoStream import VideoStream
from pessoas_lib.detector_pessoas_lib.detector_pessoas import DetectorPessoas
from pessoas_lib.pessoas_historico import PessoasHistorico
from pessoas_lib.caixas_pessoas_lib import CaixasPessoas
from exceptions.video_stream_exceptions import CannotOpenStreamError, StreamClosedError

def main():

    TEMPO_CARREGAR_CAMERA = 2.0 # segundos
    FRAMES_SEM_DETECCAO = 30
    MAX_LARGURA_FRAME = 700 # px
    TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO = 1.0 # segundo

    (cam_args, mostrar_video, precisao_deteccao, destino_json,
        tempo_atualizacao_json, modelo_dir, modelo_tipo) = pega_argumentos()

    try:
        detectorPessoas = DetectorPessoas(modelo_dir, tipo_modelo=modelo_tipo, 
                                          precisao=precisao_deteccao)
    except Exception as e:
        sys.exit(str(e))

    detector_movimento = DetectorMovimento()

    # Carrega video da fonte escolhida.
    try:
        vs = VideoStream(**cam_args).start()
    except (ImportError, CannotOpenStreamError) as e:
        sys.exit('Erro: '+str(e))

    # Para dar tempo de inicializar camera
    time.sleep(TEMPO_CARREGAR_CAMERA)

    pessoas_historico = PessoasHistorico()
    pessoas_registradas = Pessoas(precisaoMinima=precisao_deteccao)

    frames_desde_ultima_deteccao = 0

    #  Le um frame da fonte, detecta e rastreia pessoas e salva os
    # dados em um JSON.
    while True:

        # Le frame.
        try:
            frame = vs.read()
        except (StreamClosedError, Exception) as e:
            print('Erro de leitura do video: ' + str(e))
            break

        #  Redimensiona imagem para diminuir os gastos de deteccao de movimento e
        # de deteccao de pessoas, se YOLO nao for usado.
        frame = ktools.resize(frame, min(MAX_LARGURA_FRAME, frame.shape[1]))

        '''# Se houver mudanca no frame, tenta detecctar pessoas
        if detector_movimento.detectaMovimento(frame):
            detectar_flag = True
            frames_desde_ultima_deteccao = 0
        # Continuar detectando pessoas por um periodo de tempo sem movimento.
        elif frames_desde_ultima_deteccao < FRAMES_SEM_DETECCAO:
            detectar_flag = True
            frames_desde_ultima_deteccao += 1
        # Depois desse periodo, parar de tentar detectar pessoas
        else:
            detectar_flag = False'''
        
        detectar_flag = True

        if detectar_flag:
            
            # Detecta pessoas
            old_time = time.time()
            try:
                #  Nao desenha os retangulos na imagem pois o
                # rastreador pode ter mais caixas.
                _, caixas_com_peso = detectorPessoas.detecta_pessoas(frame, desenha_retangulos=False)
            except Exception as e:
                print('Erro de deteccao:\n\t[{}]: {}'.format(type(e).__name__, str(e)))
                break

            #  Se o detector tiver demorado muito, o rastreamento de 
            # objetos nao vai funcionar e, portanto, o rastreamento e
            # zerado.
            #  O rastreamento e usado para compensar pelo fato de que
            # o detector nao reconhecera o mesmo objeto em todas as
            # deteccoes.
            if time.time()-old_time > TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO:
                pessoas_registradas.reiniciar()
            caixas_com_peso = pessoas_registradas.atualizar(caixas_com_peso)


            new_frame = ktools.draw_rectangles(frame, rectangles_and_info=caixas_com_peso)

        else:
            new_frame, caixas_com_peso = frame, []

        # Salva o numero de pessoas registradas neste ciclo.
        #pessoas_historico.atualiza_pessoa(pessoas_registradas.pegaNumeroPessoas()) Soh quando o rastreador funcionar
        pessoas_historico.atualiza_pessoa(len(caixas_com_peso))

        # Cria um novo arquivo JSON com dados referente ao historico.
        if pessoas_historico.checa_tempo_decorrido(tempo_atualizacao_json):
            cria_json_pessoa(*pessoas_historico.finaliza_pessoa(), frame, destino_json)

        if mostrar_video:
            k = ktools.show_image(new_frame, title='Detection', wait_time=1,
                                  close_window=False)
            if k == ord('q'):
                break

    # Clean-up.
    cv.destroyAllWindows()
    vs.stop()


def cria_json_pessoa(media_pessoas, max_pessoas, min_pessoas, tempo_total,
                     frame, destino_json):

    print('\ncriando JSON...')
    texto_dict = {
        'MediaPessoas':media_pessoas,
        'MaximoPessoas':max_pessoas,
        'MinimoPessoas':min_pessoas,
        'TempoTotal':'{:.2f}'.format(tempo_total)
    }

    try:
        ptools.criarJSON(texto_dict, frame, destino_json)
    except Exception:
        print('Nao foi possivel criar JSON.')
    else:
        print('JSON criado com sucesso. {}'.format(datetime.datetime.now().strftime('%c')))

    print()


def pega_argumentos():

    return processa_argumentos(checa_argumentos())


def processa_argumentos(args):

    JSON_PICAMERA_PATH = 'json/config-picamera.json'
    JSON_IPCAMERA_PATH = 'json/config-ipcamera.json'
    JSON_NVIDIA_CAM_PATH = 'json/config-nvidia.json'

    # Checa se o usuario quer ler de fontes configuradas em JSONs
    if args.webcam is None and args.arquivo_video is None:
        json_path = ''
        if args.ipcamera:
            json_path = JSON_IPCAMERA_PATH
            tipo_camera = VideoStream.Tipo.IPCAMERA
        elif args.nvidia_cam:
            json_path = JSON_NVIDIA_CAM_PATH
            tipo_camera = VideoStream.Tipo.WEBCAM
        '''if args.picamera:
            json_path = JSON_PICAMERA_PATH
            tipo_camera = VideoStream.Tipo.PICAMERA'''

        try:
            cam_args = json.load(open(json_path))
        except (json.JSONDecodeError, OSError) as e:
            mensagem = 'Nao foi possivel carregar JSON' if isinstance(e, OSError) else 'JSON invalido'
            print('{}. Trocando para webcam...'.format(mensagem))
            args.webcam = 0

    # Checa outras fontes, caso contrario.
    if args.webcam is not None:
        cam_args = {'idCam': args.webcam}
        tipo_camera = VideoStream.Tipo.WEBCAM
    elif args.arquivo_video is not None:
        cam_args = {'idCam': args.arquivo_video}
        tipo_camera = VideoStream.Tipo.ARQUIVO

    # Checa o modelo do detector (padrao=YOLO)
    if args.modelo_ssd is not None:
        modelo_dir = args.modelo_ssd
        modelo_tipo = 'ssd'
    elif args.modelo_yolo is not None:
        modelo_dir = args.modelo_yolo
        modelo_tipo = 'yolo'
    cam_args['tipo'] = tipo_camera

    return (cam_args, args.mostrar_video, args.precisao_deteccao, args.destino_json,
            args.atualizacao_json, modelo_dir, modelo_tipo)


def checa_argumentos():

    TEMPO_ATUALIZACAO_JSON = 60.0 # segundos
    JSON_DEST_PATH = 'json/dados.json'

    parser = argparse.ArgumentParser(
        description='Detecta pessoas em video e conta quantas tem em um periodo de tempo.')
    
    # Camera
    camera_group = parser.add_mutually_exclusive_group(required=True)
    #camera_group.add_argument('--picamera', help='Carrega dados do JSON expecifico.', action='store_true')
    camera_group.add_argument('--ipcamera', action='store_true',
                              help='Carrega dados do JSON expecifico')
    camera_group.add_argument('--nvidia-cam', action='store_true',
                              help='Carrega arquivo da camera da nvidia')
    camera_group.add_argument('--webcam', type=int,
                              help='Carrega webcam de numero "x"')
    camera_group.add_argument('--arquivo-video', help='Carrega arquivo em ARQUIVO')


    # Modelo
    modelo_group = parser.add_mutually_exclusive_group(required=True)
    modelo_group.add_argument('--modelo-yolo', help='Diretorio modelos yolo')
    modelo_group.add_argument('--modelo-ssd', help='Diretorio modelos ssd')

    # JSON
    parser.add_argument('--destino-json', default=JSON_DEST_PATH,
                        help='Onde o JSON contendo o output do programa sera guardado')
    parser.add_argument('--atualizacao-json', default=TEMPO_ATUALIZACAO_JSON,
                        help='Tempo de atualizacao do JSON (em segundos)')

    # Video
    #parser.add_argument('--output-video', help='Diretorio para salvar video.')
    parser.add_argument('--mostrar-video', action='store_true',
                        help='Mostrar video convertido enquanto roda programa')
    parser.add_argument('--precisao-deteccao', type=float,
                        default=DetectorPessoas.DEFAULT_PRECISAO_DETECCAO,
                        help='Precisao da deteccao de pessoas [0.0, 1.0]')

    args = parser.parse_args()

    if args.webcam is not None and args.webcam < 0:
        parser.error('Index da webcam deve ser >= 0.')

    return args



if __name__ == '__main__':
    main()    