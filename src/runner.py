import argparse
import time
import json
import random
from datetime import datetime

from videolib.fileVideoStream import FileVideoStream
from deteccao_pessoas_lib.detector_pessoas import DEFAULT_PRECISAO_DETECCAO
from deteccao_pessoas_lib.detector_pessoas_video import DetectorPessoasVideo
from mqtt_lib.mqtt_publisher import MQTTPublisher
from imagelib import ktools
from toolslib import ptools

def main():

    cam_args, modelo_args, visualizacao_frames_args, video_info, resultados_info = pega_argumentos()

    detector = (
        DetectorPessoasVideo()
        .configura_video(**cam_args)
        .configura_detector(**modelo_args)
        .start()
    )

    publicador = MQTTPublisher(hostname='postman.cloudmqtt.com', porta=12909,
                               username='soizdkgg', password='2dxd4P_lG-PG')

    publicador.adicionar_topico(resultados_info['topico_mqtt'])

    print('\nExecutando reconhecimento de pessoas.')

    tempo = time.time()
    
    while not detector.stopped:
        if video_info['mostrar_video']:
            frame = detector.pega_frame(**visualizacao_frames_args)
            k = ktools.show_image(frame, title='Detector', wait_time=1,
                                  close_window=False)
            if chr(k) == 'q':
                break
            elif chr(k) == 'p':
                visualizacao_frames_args['mostrar_precisao'] = \
                    not visualizacao_frames_args['mostrar_precisao']

            if time.time()-tempo >= resultados_info['tempo_atualizacao_resultados']:
                publicador.publish(cria_json_str(*detector.pega_dados_periodo()))
                tempo = time.time()
            time.sleep(0.7)
    detector.stop()
    ktools.destroy_all_windows()



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
    (dict, dict, dict, dict, dict)
        Valores retormados pelas funções processa_argumentos_camera(), 
        processa_argumentos_modelo(), processa_argumentos_detector(),
        processa_argumentos_video(), processa_argumentos_resultados().
    '''

    args = checa_argumentos()
    cam_args = processa_argumentos_camera(args)
    modelo_args = processa_argumentos_modelo(args)
    visualizacao_frames_args = processa_visualizacao_frames(args)
    video_info = processa_argumentos_video(args)
    resultados_info = processa_argumentos_resultados(args)
    return cam_args, modelo_args, visualizacao_frames_args, video_info, resultados_info

def processa_argumentos_camera(args):
    '''Processa or argumentos relacionados à entrada de vídeo.

    Parameters
    -----------
    args
        Argumentos recebidos.
    
    Returns
    --------
    detector_init_info : dict
        Valores do dicionário dependem do tipo de entrada escolhido.

        Se for webcam:
            {'idCam': (int) id da câmera, 'tipo_camera': 'webcam'}

        Se for arquivo:
            {'arquivo': (str) 'caminho/para/arquivo', 'tipo_camera': 'arquivo'}

        Se for ipcamera:
            {(itens do json)..., 'tipo_camera': 'ipcamera'}

        Se for a câmera da nvidia:
            {(itens do json)..., 'tipo_camera': 'nvidia_cam'}
    '''

    #JSON_PICAMERA_PATH = 'data/config-picamera.json'
    #JSON_IPCAMERA_PATH = 'data/config-ipcamera.json'
    JSON_NVIDIA_CAM_PATH = 'data/config-nvidia.json'

    if args.nvidia_cam:
        tipo_camera = 'nvidia'
        '''if args.picamera:
            json_path = JSON_PICAMERA_PATH
            tipo_camera = VideoStream.Tipo.PICAMERA'''
        try:
            cam_args = json.load(open(JSON_NVIDIA_CAM_PATH))
        except (json.JSONDecodeError, OSError) as e:
            mensagem = 'Nao foi possivel carregar JSON' if isinstance(e, OSError) else 'JSON invalido'
            print('{}. Trocando para webcam...'.format(mensagem))
            args.webcam = 0

    # Checa outras fontes, caso contrario.
    if args.webcam is not None:
        cam_args = {'idCam': args.webcam}
        tipo_camera = 'webcam'
    elif args.ipcamera is not None:
        cam_args = {'cameraURL': args.ipcamera}
        tipo_camera = 'ipcamera'
    elif args.arquivo_video is not None:
        cam_args = {'arquivo': args.arquivo_video}
        tipo_camera = 'arquivo'
    
    cam_args['tipo'] = tipo_camera

    return cam_args

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
        'topico_mqtt':args.topico_mqtt if args.topico_mqtt != '' \
            else 'detector/camera-'+str(random.randint(10, 1500)),
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
    camera_group = parser.add_mutually_exclusive_group(required=True)
    #camera_group.add_argument('--picamera', help='Carrega dados do JSON expecifico.', action='store_true')
    camera_group.add_argument('--ipcamera', type=str,
                              help='Conecta ao endereço específico.')
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
    # parser.add_argument('--destino-json', default=JSON_DEST_PATH,
    #                     help='Onde o JSON contendo o output do programa sera guardado')
    parser.add_argument('--topico-mqtt', default='', type=str,
                        help='Caso os dados sejam salvos em um servidor mqtt, '
                             'este será o seu tópico. '
                             '(Padrão=detector/camera-<número aleatório>)')
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