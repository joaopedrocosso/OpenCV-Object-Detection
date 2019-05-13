import argparse

from pessoas_lib.detector_pessoas_lib.detector_pessoas import DetectorPessoas
from pessoas_lib.detector_pessoas_video import DetectorPessoasVideo

def main():

    cam_args, modelo_args, detector_init_args = pega_argumentos()

    detector = (
        DetectorPessoasVideo(**detector_init_args)
        .configura_video(**cam_args)
        .configura_detector(**modelo_args)
        .start()
    )

    print('\nExecutando reconhecimento de pessoas.')

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
        'mostrar_video':args.mostrar_video, 'mostrar_precisao':args.mostrar_precisao,
        'destino_json':args.destino_json, 'tempo_atualizacao_json':args.atualizacao_json
    }

    return cam_args, modelo_args, detector_init_args


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
    parser.add_argument('--mostrar-precisao', action='store_true',
                        help='Mostrar precisão acima do retângulo no vídeo.')
    parser.add_argument('--precisao-deteccao', type=float,
                        default=DetectorPessoas.DEFAULT_PRECISAO_DETECCAO,
                        help='Precisao da deteccao de pessoas [0.0, 1.0]')

    args = parser.parse_args()

    if args.webcam is not None and args.webcam < 0:
        parser.error('Index da webcam deve ser >= 0.')

    return args



if __name__ == '__main__':
    main()    