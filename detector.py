import argparse
import time

from videolib.fileVideoStream import FileVideoStream
from pessoas_lib.detector_pessoas_lib.detector_pessoas import DetectorPessoas, DEFAULT_PRECISAO_DETECCAO
from pessoas_lib.detector_pessoas_video import DetectorPessoasVideo
from imagelib import ktools
from toolslib import ptools

def main():
    cam_args, modelo_args, detector_init_args, mostrar_video = pega_argumentos()

    detector = (
        DetectorPessoasVideo(**detector_init_args)
        #.configura_video(**cam_args)
        .configura_detector(**modelo_args)
        #.start()
    )
    detector.recebe_video(FileVideoStream('../detector-itens/videos/03.mp4'))
    detector.start()

    print('\nExecutando reconhecimento de pessoas.')
            

    while not detector.stopped:
        if mostrar_video:
            k = ktools.show_image(detector.pega_frame(), title='Detector',
                                  wait_time=1, close_window=False)
            if chr(k) == 'q':
                break
            time.sleep(0.5)
    detector.stop()
    ktools.destroy_all_windows()




def cria_json_pessoa(media_pessoas, max_pessoas, min_pessoas, tempo_total,
                     frame, destino_json):
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
    frame : numpy.ndarray
        Imagem do último frame lido.
    destino_json : str
        Onde guardar o JSON que será criado.
    '''

    #print('\ncriando JSON...')
    texto_dict = {
        'MediaPessoas':media_pessoas,
        'MaximoPessoas':max_pessoas,
        'MinimoPessoas':min_pessoas,
        'TempoTotal':'{:.2f}'.format(tempo_total)
    }

    try:
        ptools.criarJSON(texto_dict, frame, destino_json)
    except Exception:
        #print('Nao foi possivel criar JSON.')
        pass
    else:
        #print('JSON criado com sucesso. {}'
        #.format(datetime.datetime.now().strftime('%c')))
        pass

    #print()



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
            tipo_camera = 'ipcamera'
        elif args.nvidia_cam:
            json_path = JSON_NVIDIA_CAM_PATH
            tipo_camera = 'nvidia'
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
        tipo_camera = 'webcam'
    elif args.arquivo_video is not None:
        cam_args = {'arquivo': args.arquivo_video}
        tipo_camera = 'arquivo'

    # Checa o modelo do detector (padrao=YOLO)
    if args.modelo_ssd is not None:
        dir_modelo = args.modelo_ssd
        tipo_modelo = 'ssd'
    elif args.modelo_yolo is not None:
        dir_modelo = args.modelo_yolo
        tipo_modelo = 'yolo'

    cam_args['tipo'] = tipo_camera
    modelo_args = {'dir_modelo':dir_modelo, 'tipo_modelo':tipo_modelo,
                   'precisao_deteccao':args.precisao_deteccao}
    detector_init_args = {
        'mostrar_caixas':args.mostrar_caixas,
        'mostrar_precisao':args.mostrar_precisao,
    }

    return cam_args, modelo_args, detector_init_args, args.mostrar_video


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
    parser.add_argument('--atualizacao-json', default=TEMPO_ATUALIZACAO_JSON, type=int,
                        help='Tempo de atualizacao do JSON (em segundos)')

    # Video
    #parser.add_argument('--output-video', help='Diretorio para salvar video.')
    parser.add_argument('--mostrar-video', action='store_true',
                        help='Mostrar video convertido enquanto roda programa')
    parser.add_argument('--mostrar-caixas', action='store_true',
                        help='Mostrar caixas em volta das pessoas no vídeo.')
    parser.add_argument('--mostrar-precisao', action='store_true',
                        help='Mostrar precisão acima das caixas no vídeo.')
    parser.add_argument('--precisao-deteccao', type=float,
                        default=DEFAULT_PRECISAO_DETECCAO,
                        help='Precisao da deteccao de pessoas [0.0, 1.0]')

    args = parser.parse_args()

    if args.webcam is not None and args.webcam < 0:
        parser.error('Index da webcam deve ser >= 0.')

    return args



if __name__ == '__main__':
    main()    