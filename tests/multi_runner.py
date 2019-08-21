import time
import json
from datetime import datetime

from videolib.fileVideoStream import FileVideoStream
from deteccao_pessoas_lib.detector_pessoas import DEFAULT_PRECISAO_DETECCAO
from deteccao_pessoas_lib.detector_pessoas_video import DetectorPessoasVideo
from mqtt_lib.mqtt_publisher import MQTTPublisher
from imagelib import ktools
from toolslib import ptools

def main():
    pass


def processa_camera(comando):
    source, tipo = comando.strip().split(' ')


if __name__ == '__main__':
    main()