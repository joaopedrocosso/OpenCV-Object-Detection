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
from videolib.abstractVideoStream import AbstractVideoStream
from videolib.exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError
from toolslib import ptools

class DetectorPessoasVideo(Thread):

    '''Detecta pessoas em um vídeo em uma thread separada.

    Deve-se configurar o objeto chamando os métodos 'configura_video'
    ou 'recebe_video', para haver uma entrada de vídeo, e
    'configura_detector', para configurar o detector de pessoas.

    Parameters
    -----------
    mostrar_video : bool, optional.
        Se o vídeo resultante com caixas em volta das pessoas deve
        ser mostrado em uma janela. (Padrão=False)
    mostrar_precisao : bool, optional.
        Se a precisão deve ser mostrada em cima da caixa.
        (Padrão=False)
    destino_json : str, optional.
        Onde o JSON com as estatísticas das pessoas deve ser
        guardado. (Padrão='json/dados.json')
    tempo_atualizacao_json : int, optional.
        Tempo entre atualizações do JSON. (Padrão=60)

    See Also
    ---------
    '''

    def __init__(self, mostrar_video=False, mostrar_precisao=False,
                 destino_json='json/dados.json', tempo_atualizacao_json=60):

        super().__init__()

        self.mostrar_video = mostrar_video
        self.mostrar_precisao = mostrar_precisao
        self.destino_json = destino_json
        self.tempo_atualizacao_json = tempo_atualizacao_json

        self.pessoas_historico = PessoasHistorico()
        self.pessoas_registradas = CaixasPessoas()

        self.stopped = False
        self.stream = None
        self.detectorPessoas = None
        self.stream_externo = False

    def configura_video(self, tipo, **keywords):

        '''Configura a entrada de vídeo internamente.

        Parameters
        -----------
        tipo : {'picamera', 'ipcamera', 'webcam', 'arquivo'}
        resolucao : (int, int)
            Se 'picamera' foi escolhido.
            Tupla que representa a resolução do vídeo. Ex.: (320, 240).
        fps : int
            Se 'picamera' foi escolhido.
            Frames por segundo.
        cameraURL : str
            Se 'ipcamera' foi escolhido.
            Url da câmera.
        login: str
            Se 'ipcamera' foi escolhido.
            Login da câmera.
        senha: str
            Se 'ipcamera' foi escolhido.
            Senha da câmera.
        idCam : str or int
            Se 'webcam' foi escolhido.
            Número da câmera. (padrão=0)
        arquivo : str
            Se 'arquivo' foi escolhido.
            Caminho ao arquivo.

        Returns
        -------
        self

        Raises
        -------
        CannotOpenStreamError
            Se não foi possível abrir o stream.

        See Also
        ---------
        usa_video_externo : Para receber um leitor de vídeo de fora.
        '''

        try:
            self.stream = VideoStream(tipo, **keywords)
        except (ImportError, CannotOpenStreamError) as e:
            raise
        self.stream_externo = False

        # Para dar tempo de inicializar a câmera.
        time.sleep(2.0)

        return self

    def recebe_video(self, stream):
        '''Configura a entrada de vídeo com um objeto externo.

        Parameters
        -----------
        stream : AbstractVideoStream
            Objeto de entrada de vídeo que herda de AbstractVideoStream.
        '''
        if not isinstance(stream, AbstractVideoStream):
            raise TypeError("Stream deve herdar de 'AbstractVideoStream'.")
        self.stream = stream
        self.stream_externo = True
        return self

    def configura_detector(self, dir_modelo, tipo_modelo='yolo',
                           precisao_deteccao=0.4):

        '''Detecta pessoas usando um modelo de deep learning.

        Parameters
        -----------
        dir_modelo : str
            Destino do modelo desejado.
        tipo_modelo : {'yolo', 'sdd'}, optional
            Tipo do modelo.
        precisao_deteccao: float
            Quão precisa a detecção deve ser. Deve estar entre
            0.0 e 1.0 inclusive. (padrão=0.4)
        
        Raises
        --------
        ValueError
            Se o tipo do modelo for inválido.
        Exceções relacionadas ao OpenCV.
        '''

        try:
            self.detectorPessoas = DetectorPessoas(
                dir_modelo, tipo_modelo=tipo_modelo, precisao=precisao_deteccao)
        except Exception as e:
            raise

        return self

    def start(self):
        '''Executa o código principal em uma nova thread.

        Returns
        --------
        self
        '''
        super().start()
        return self

    def stop(self):
        '''Finaliza a thread.'''
        self.stopped = True

    def pega_pessoas(self):
        '''Retorna o número de pessoas registradas no momento.
        
        Returns
        -------
        int
        '''
        return len(self.pessoas_registradas)

    def run(self):
        '''Detecta pessoas em um vídeo.'''

        TEMPO_SEM_DETECCAO = 60 # segundos
        MAX_LARGURA_FRAME = 700 # px
        TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO = 1.0 # segundo
        PERIODO_MINIMO = 0.7

        if self.stream is None or self.detectorPessoas is None:
            print('Erro: stream ou detector de pessoas não configurado.')
            return
        self.stream.start()
        
        detector_movimento = (
            DetectorMovimento(periodo_minimo=PERIODO_MINIMO)
            .recebe_video(self.stream)
            .start()
        )

        tempo_ultima_deteccao = time.time()-TEMPO_SEM_DETECCAO

        while not self.stopped:

            tempo_comeco_iteracao = time.time()

            try:
                frame = self.stream.read()
            except (StreamClosedError, StreamStoppedError) as e:
                print(str(e))
                break

            # Redimensiona imagem para diminuir os gastos de detecção de 
            # movimento.
            frame = ktools.resize(frame, min(MAX_LARGURA_FRAME, frame.shape[1]))

            # Se houver mudança no frame ou já passou do tempo limite
            # sem detecção, detectar pessoas.
            if (detector_movimento.detecta_movimento(frame)
                or time.time()-tempo_ultima_deteccao > TEMPO_SEM_DETECCAO):
                detectar_flag = True
                repetir_caixas = False
                tempo_ultima_deteccao = time.time()
            else:
                detectar_flag = False
                repetir_caixas = True

            if detectar_flag:
                try:
                    _, caixas_com_peso = self.detectorPessoas.detecta_pessoas(
                        frame, desenha_retangulos=False)
                except Exception as e:
                    print('Erro de detecção:\n\t[{}]: {}'
                        .format(type(e).__name__, str(e)))
                    break
            else:
                new_frame, caixas_com_peso = frame, []
                    
            # Se a iteração for muito lenta, reiniciar o rastreio.
            if time.time()-tempo_comeco_iteracao > TEMPO_MAXIMO_DETECCAO_COM_RASTREAMENTO:
                self.pessoas_registradas.reiniciar()
            caixas_com_peso = self.pessoas_registradas.atualizar(
                caixas_com_peso, caixas_paradas=repetir_caixas)

            new_frame = ktools.draw_rectangles(
                frame, rectangles_and_info=caixas_com_peso,
                write_weight=self.mostrar_precisao)

            # Salva o numero de pessoas registradas neste ciclo.
            self.pessoas_historico.atualiza_pessoa(len(caixas_com_peso))

            # Cria um novo arquivo JSON com dados referentes ao histórico.
            if (self.pessoas_historico.pega_tempo_decorrido()
                >= self.tempo_atualizacao_json):
                self._cria_json_pessoa(*self.pessoas_historico.finaliza_pessoa(),
                                       frame, self.destino_json)

            if self.mostrar_video:
                k = ktools.show_image(new_frame, title='Detecção', wait_time=1,
                                      close_window=False)
                if k == ord('q'):
                    break

            tempo_iteracao = time.time() - tempo_comeco_iteracao
            if tempo_iteracao <= PERIODO_MINIMO:
                time.sleep(PERIODO_MINIMO-tempo_iteracao)

        # Clean-up.
        cv.destroyAllWindows()
        if not self.stream_externo:
            self.stream.stop()
        self.stop()


    def _cria_json_pessoa(self, media_pessoas, max_pessoas, min_pessoas,
                          tempo_total, frame, destino_json):
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

        print()