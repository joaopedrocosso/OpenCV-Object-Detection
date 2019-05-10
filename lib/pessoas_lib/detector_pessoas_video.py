import time
import json
import cv2 as cv
import datetime
from threading import Thread

from imagelib import ktools
from imagelib.detector_movimento import DetectorMovimento
from videolib.videoStream import VideoStream
from pessoas_lib.detector_pessoas_lib.detector_pessoas import DetectorPessoas
from pessoas_lib.pessoas_historico import PessoasHistorico
from pessoas_lib.caixas_pessoas_lib.caixas_pessoas import CaixasPessoas
from exceptions.video_stream_exceptions import CannotOpenStreamError, StreamClosedError
from toolslib import ptools

class DetectorPessoasVideo:

    def __init__(self, mostrar_video=False, mostrar_precisao=False, destino_json='json/dados.json', tempo_atualizacao_json=60):

        self.mostrar_video = mostrar_video
        self.mostrar_precisao = mostrar_precisao
        self.destino_json = destino_json
        self.tempo_atualizacao_json = tempo_atualizacao_json

        self.detector_movimento = DetectorMovimento()

        self.pessoas_historico = PessoasHistorico()
        self.pessoas_registradas = CaixasPessoas()

        self.stopped = False

    def configura_video(self, tipo, **keywords):

        '''Configura a entrada de vídeo.

        Parâmetros:
            tipo: Tipo de entrada. Pode ser 'picamera', 'ipcamera', 'webcam' e 'arquivo'.

            Se o tipo for 'picamera':
                'resolucao': Tupla que representa a resolução do vídeo. Ex.: (320, 240).
                'fps': Frames por segundo.
            Se o tipo for 'ipcamera':
                'cameraURL': Url da câmera.
                'login': Login da câmera.
                'senha': Senha da câmera.
            Se o tipo for 'webcam':
                'idCam' (padrão=0): Número da câmera.
            Se o tipo for 'arquivo':
                'arquivo': Caminho ao arquivo.

        Métodos:
            'start': Começa o stream. Retorna a si mesmo.
            'read': Retorna o frame atual do vídeo.
            'stop': Para o stream.
        '''

        try:
            self.stream = VideoStream(tipo, **keywords)
        except (ImportError, CannotOpenStreamError) as e:
            raise

        # Para dar tempo de inicializar a câmera.
        time.sleep(2.0)

        return self

    def configura_detector(self, dir_modelo, tipo_modelo='yolo', precisao_deteccao=0.4):

        '''Detecta pessoas usando um modelo de deep learning.

        parâmetros:
            'dir_modelo': Destino do modelo desejado.
            'tipo_modelo' (padrão='yolo'): Tipo do modelo. Pode ser 'yolo' ou 'ssd'
            'precisao_deteccao' (padrão=0.4): Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0.

        Joga as exceções:
            'ValueError': se o tipo do modelo for inválido.
            Exceções relacionadas ao OpenCV.
        '''

        try:
            self.detectorPessoas = DetectorPessoas(
                dir_modelo, tipo_modelo=tipo_modelo, precisao=precisao_deteccao)
        except Exception as e:
            raise

        return self

    def start(self):
        Thread(target=self._rodar, args=()).start()
        return self

    def stop(self):
        self.stopped = True

    def pega_pessoas(self):
        return len(self.pessoas_registradas)

    def _rodar(self):

        self.stream.start()

        FRAMES_SEM_DETECCAO = 30
        MAX_LARGURA_FRAME = 700 # px
        TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO = 1.0 # segundo

        frames_desde_ultima_deteccao = 0

        while not self.stopped:

            try:
                frame = self.stream.read()
            except StreamClosedError as e:
                print(str(e))
                break

            #  Redimensiona imagem para diminuir os gastos de detecção de movimento.
            frame = ktools.resize(frame, min(MAX_LARGURA_FRAME, frame.shape[1]))

            '''# Se houver mudança no frame, tenta detecctar pessoas
            if self.detector_movimento.detectaMovimento(frame):
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
                
                old_time = time.time()
                
                try:
                    _, caixas_com_peso = self.detectorPessoas.detecta_pessoas(frame, desenha_retangulos=False)
                except Exception as e:
                    print('Erro de detecção:\n\t[{}]: {}'.format(type(e).__name__, str(e)))
                    break

                # Se o detector demorar muito, o registro não será muito útil.
                # Portanto, ele é zerado.
                if time.time()-old_time > TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO:
                    self.pessoas_registradas.reiniciar()
                caixas_com_peso = self.pessoas_registradas.atualizar(caixas_com_peso)
                
                new_frame = ktools.draw_rectangles(frame, rectangles_and_info=caixas_com_peso, write_weight=self.mostrar_precisao)

            else:
                new_frame, caixas_com_peso = frame, []

            # Salva o numero de pessoas registradas neste ciclo.
            self.pessoas_historico.atualiza_pessoa(len(caixas_com_peso))

            # Cria um novo arquivo JSON com dados referentes ao histórico.
            if self.pessoas_historico.checa_tempo_decorrido(self.tempo_atualizacao_json):
                self._cria_json_pessoa(*self.pessoas_historico.finaliza_pessoa(), frame, self.destino_json)

            if self.mostrar_video:
                k = ktools.show_image(new_frame, title='Detecção', wait_time=1, close_window=False)
                if k == ord('q'):
                    break

        # Clean-up.
        cv.destroyAllWindows()
        self.stream.stop()
        self.stop()


    def _cria_json_pessoa(self, media_pessoas, max_pessoas, min_pessoas, tempo_total,
                         frame, destino_json):

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
            pass#print('Nao foi possivel criar JSON.')
        else:
            pass#print('JSON criado com sucesso. {}'.format(datetime.datetime.now().strftime('%c')))

        print()