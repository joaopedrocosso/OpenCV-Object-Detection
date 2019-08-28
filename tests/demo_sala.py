import sys
from demo_base import executa_demo

channel=1
camera_personalizada = False
if len(sys.argv) >= 2:
    try:
        channel_arg = int(sys.argv[1])
        if 1 <= channel_arg <= 8:
            channel = channel_arg
            camera_personalizada = True
    except ValueError:
        print('Câmera inválida.')
if not camera_personalizada:
    print('Câmera padrão (1) selecionada.')

comandos_adicionais = ' '.join(sys.argv[2:])

executa_demo(
    '--ipcamera ' + 'rtsp://LCC:6023-FL%40b@152.92.234.55:554/h264/ch{channel}/main/av_stream'.format(channel=channel)
    + ' ' + '--topico-mqtt detector/camera-{:02d}'.format(channel) + ' ' + comandos_adicionais)