import argparse
import time
import json
import random
import string
from datetime import datetime

from videolib.fileVideoStream import FileVideoStream
from deteccao_pessoas_lib.detector_pessoas import DEFAULT_PRECISAO_DETECCAO
from deteccao_pessoas_lib.detector_pessoas_video import DetectorPessoasVideo
from mqtt_lib.mqtt_publisher import MQTTPublisher
from imagelib import ktools
from toolslib import ptools

def main():

    camera, modelo_args, visualizacao_frames_args, video_info, resultados_info = pega_argumentos()

    print('\nIniciando reconhecimento de pessoas.')

    while True:
        retorno = detecta_na_camera(
            camera, modelo_args, visualizacao_frames_args, video_info,
            resultados_info)
        if retorno == 'q':
            break
        else: # retorno == nova_camera
            camera = retorno
            print('\nMudando para a câmera {camera}.'.format(camera=camera))
    
    ktools.destroy_all_windows()

    print('\nEncerrando o programa.')

def detecta_na_camera(numero_camera, modelo_args, visualizacao_frames_args,
                      video_info, resultados_info):
    '''Detecta pessoas em uma câmera específica.

    Returns
    -------
    int or str
        Número da próxima câmera a ser usada, ou 'q', para encerrar o 
        programa.
    '''
    url_camera = \
        'rtsp://LCC:6023-FL%40b@152.92.234.55:554/h264/ch{channel}/main/av_stream' \
        .format(channel=numero_camera)
    cam_args = {'cameraURL': url_camera, 'tipo': 'ipcamera'}

    detector = (
        DetectorPessoasVideo()
        .configura_video(**cam_args)
        .configura_detector(**modelo_args)
        .start()
    )

    publicador = MQTTPublisher(hostname='postman.cloudmqtt.com', porta=12909,
                               username='soizdkgg', password='2dxd4P_lG-PG')

    publicador.adicionar_topico('detector/camera-{}'.format(numero_camera))
    tempo = time.time()

    retorno = None
    while not detector.stopped:
        if video_info['mostrar_video']:
            frame = detector.pega_frame(**visualizacao_frames_args)
            k = ktools.show_image(frame, title='Detector', wait_time=1,
                                  close_window=False)
            k = chr(k)
            if k == 'p':
                visualizacao_frames_args['mostrar_precisao'] = \
                    not visualizacao_frames_args['mostrar_precisao']
            elif k == 'q':
                retorno = 'q'
                break
            elif k in string.digits[1:8+1] and k != str(numero_camera):
                retorno = int(k)
                break      

            if time.time()-tempo >= resultados_info['tempo_atualizacao_resultados']:
                try:
                    publicador.publish(cria_json_str(*detector.pega_dados_periodo()))
                except:
                    print('Erro ao enviar os dados ao broker.')
                tempo = time.time()
            time.sleep(0.7)

    # Tela não fica preta só com uma chamada. Então, fazemos 3.
    for _ in range(3):
        ktools.show_image(detector.pega_frame_preto(), title='Detector', wait_time=1, close_window=False)
    detector.stop()

    return retorno


def cria_json_str(media_pessoas, max_pessoas, min_pessoas, tempo_total, frame=None):
    '''Cria um JSON com os dados de pessoas.
    
    Parameters
    -----------
    media_pessoas : int
        Média de pessoas.
    max_pessoas : int
        Número máximo de pessoas registradas.
    min_pessoas : int
        Número mínimo de pessoas registradas.
    tempo_total : float
        Tempo total desde o registro da primeira pessoa na média.
    destino_json : str
        Onde guardar o JSON que será criado.
    frame : numpy.ndarray, optional
        Imagem do último frame lido. (Padrão=None)
    '''

    # print('\ncriando JSON...')
    json_dict = {
        'MediaPessoas':'{:.2f}'.format(media_pessoas),
        'MaximoPessoas':max_pessoas,
        'MinimoPessoas':min_pessoas,
        'TempoTotal':'{:.2f}'.format(tempo_total),
        'HorarioAnalise':str(datetime.now())
    }

    json_dict['UltimoFrameCapturado'] = \
        ptools.criaImagemString(frame) if frame is not None else ''

    return json.dumps(json_dict)


def pega_argumentos():
    '''
    Pega e processa alimentos.

    Se algum dos argumentos recebidos não seguir as especificações, o
    programa é fechado.

    Returns
    --------
    (int, dict, dict, dict, dict)
        Valores retormados pelas funções processa_argumentos_camera(), 
        processa_argumentos_modelo(), processa_argumentos_detector(),
        processa_argumentos_video(), processa_argumentos_resultados().
    '''

    args = checa_argumentos()
    camera = processa_argumentos_camera(args)
    modelo_args = processa_argumentos_modelo(args)
    visualizacao_frames_args = processa_visualizacao_frames(args)
    video_info = processa_argumentos_video(args)
    resultados_info = processa_argumentos_resultados(args)
    return camera, modelo_args, visualizacao_frames_args, video_info, resultados_info

def processa_argumentos_camera(args):
    '''Processa or argumentos relacionados à entrada de vídeo.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    int
        Número da câmera
    '''

    return args.camera

def processa_argumentos_modelo(args):
    '''Processa or argumentos relacionados ao modelo usado pelo detector.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    modelo_args : {str:str, str:str, str:float}
        Diretório do modelo a ser usado pelo detector, seu tipo e a 
        precisão da detecção.
    '''

    # Checa o modelo do detector (padrao=YOLO)
    if False:#args.modelo_ssd is not None:
        dir_modelo = args.modelo_ssd
        tipo_modelo = 'ssd'
    else:#elif args.modelo_yolo is not None:
        dir_modelo = args.modelo_yolo
        tipo_modelo = 'yolo'
    
    modelo_args = {'dir_modelo':dir_modelo, 'tipo_modelo':tipo_modelo,
                   'precisao_deteccao':args.precisao_deteccao}
    return modelo_args

def processa_visualizacao_frames(args):
    '''Processa or argumentos relacionados à visualização dos frames.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    visualizacao_frames_args : {str:bool, str:bool}
        Flags para mostrar as caixas em torno das pessoas detectadas e
        a probabilidade da caixa representar uma pessoa.
    '''
    visualizacao_frames_args = {
        'mostrar_caixas':args.mostrar_caixas,
        'mostrar_precisao':args.mostrar_precisao,
        'mostrar_modo':True
    }
    return visualizacao_frames_args

def processa_argumentos_video(args):
    '''Processa or argumentos relacionados à entrada de vídeo.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    video_info : {str:bool, str:bool, str:bool}
        Flags para abrir uma janela com o vídeo, mostrar caixas em 
        torno das pessoas detectadas e a probabilidade da caixa 
        representar uma pessoa.
    '''
    video_info = {
        'mostrar_video':args.mostrar_video,
        'salvar_em_arquivo':(args.salvar_video!=''),
        'arquivo_onde_salvar':args.salvar_video
    }
    return video_info

def processa_argumentos_resultados(args):
    '''Processa or argumentos relacionados aos resultados e sua transmissão.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    resultados_info : {str:int}
        Informação relacionada aos dados.
    '''
    resultados_info = {
        'tempo_atualizacao_resultados':args.tempo_atualizacao_resultados
    }
    return resultados_info


def checa_argumentos():
    '''
    Pega os argumentos do terminal e os organiza de forma estruturada.

    Fecha o programa caso algum critério não tenha sido atendido.
    
    Returns
    --------
    argparse.Namespace
        Argumentos recebidos.
    '''

    TEMPO_ATUALIZACAO_RESULTADOS = 60.0 # segundos
    #JSON_DEST_PATH = 'data/out.json'

    parser = argparse.ArgumentParser(
        description='Detecta pessoas em video e conta quantas tem em um periodo de tempo.')
    
    # Camera
    parser.add_argument('--camera', default=1, type=int, choices=range(1, 8+1),
                        metavar='[1-8]',
                        help='Escolhe a câmera que se quer visualizar inicialmente')


    # Modelo
    modelo_group = parser.add_mutually_exclusive_group(required=True)
    modelo_group.add_argument('--modelo-yolo', help='Diretorio modelos yolo')
    modelo_group.add_argument('--modelo-ssd', help='Diretorio modelos ssd')

    # JSON
    # parser.add_argument('--destino-json', default=JSON_DEST_PATH,
    #                     help='Onde o JSON contendo o output do programa sera guardado')
    parser.add_argument('--tempo-atualizacao-resultados', default=TEMPO_ATUALIZACAO_RESULTADOS, type=int,
                        help='Tempo de atualizacao dos resultados a um destino (em segundos)')

    # Video
    #parser.add_argument('--output-video', help='Diretorio para salvar video.')
    parser.add_argument('--mostrar-video', action='store_true',
                        help='Mostrar video convertido enquanto roda programa')
    parser.add_argument('--mostrar-caixas', action='store_true',
                        help='Mostrar caixas em volta das pessoas no vídeo.')
    parser.add_argument('--mostrar-precisao', action='store_true',
                        help='Mostrar precisão acima das caixas no vídeo.')
    parser.add_argument('--salvar-video', default='', type=str,
                        help='Salvar frames em um arquivo de vídeo.')

    parser.add_argument('--precisao-deteccao', type=float,
                        default=DEFAULT_PRECISAO_DETECCAO,
                        help='Precisao da deteccao de pessoas [0.0, 1.0]')

    args = parser.parse_args()

    # if args.webcam is not None and args.webcam < 0:
    #     parser.error('Index da webcam deve ser >= 0.')

    return args



if __name__ == '__main__':
    main()    