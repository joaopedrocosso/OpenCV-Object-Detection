import time
import cv2 as cv
from threading import Thread

from imagelib import ktools
from imagelib.detector_movimento import DetectorMovimento
from imagelib.rastreador import Rastreador
from videolib.videoStream import VideoStream
from pessoas_lib.detector_pessoas_lib.detector_pessoas import DetectorPessoas
from pessoas_lib.pessoas_historico import PessoasHistorico
from pessoas_lib.caixas_pessoas_lib.caixas_pessoas import CaixasPessoas
from videolib.abstractVideoStream import AbstractVideoStream
from videolib.exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError

class DetectorPessoasVideo(Thread):

    '''Detecta pessoas em um vídeo em uma thread separada.

    Deve-se configurar o objeto chamando os métodos 'configura_video'
    ou 'recebe_video', para haver uma entrada de vídeo, e
    'configura_detector', para configurar o detector de pessoas.

    Parameters
    -----------
    mostrar_caixas : bool, optional.
        Se o frame guardado deve conter as caixas em volta das pessoas
        (Padrão=False)
    mostrar_precisao : bool, optional.
        Se a precisão deve ser mostrada em cima da caixa. Se
        'mostrar_caixas' for 'False', a precisão não é mostrada.
        (Padrão=False)
    max_tempo_sem_deteccao : int, optional
        Tempo máximo que se pode identificar pessoas (ou sua ausência)
        por métodos que não sejam uma detecção (detector de movimento,
        rastreador, etc). Deve ser positivo ou zero. (Padrão=60)
    max_largura_frame : int, optional
        Se o frame do vídeo for maior que este valor, ele será
        redimensionado. Deve ser positivo. (Padrão=700)

    Raises
    ------
    ValueError
        Se um dos argumentos não atender às especificações.
    '''

    def __init__(self, mostrar_caixas=False, mostrar_precisao=False,
                 max_tempo_sem_deteccao=5, max_largura_frame=700):

        super().__init__()

        self.mostrar_caixas = mostrar_caixas
        self.mostrar_precisao = mostrar_precisao
        if max_tempo_sem_deteccao < 0:
            raise ValueError(
                "'max_tempo_sem_deteccao' deve ser um número positivo.")
        if max_largura_frame <= 0:
            raise ValueError(
                "'max_largura_frame' deve ser um número positivo ou zero.")
        self.max_tempo_sem_deteccao = max_tempo_sem_deteccao
        self.max_largura_frame = max_largura_frame

        self.pessoas_historico = PessoasHistorico()
        self.pessoas_registradas = CaixasPessoas()

        self.frame = None
        self.stream = None
        self.detectorPessoas = None
        self.stopped = False
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

    def run(self):
        '''Detecta pessoas em um vídeo.'''

        MAX_TEMPO_ENTRE_REGISTROS = 1.0 #segundo
        PERIODO_MINIMO = 0.7 #segundo
        MAX_TEMPO_PARADO = 20 #segundos

        if self.stream is None or self.detectorPessoas is None:
            print('Erro: stream ou detector de pessoas não configurado.')
            return
        self.stream.start()
        time.sleep(2)
        
        detector_movimento = (
            DetectorMovimento(periodo_minimo=PERIODO_MINIMO)
            .recebe_video(self.stream)
            .start()
        )
        rastreador = Rastreador()

        tempo_ultima_deteccao = time.time()-self.max_tempo_sem_deteccao
        tempo_em_que_parou = time.time()-MAX_TEMPO_PARADO
        ultimo_modo = ''

        while not self.stopped:

            tempo_comeco_iteracao = time.time()

            try:
                frame = self.stream.read()
            except (StreamClosedError, StreamStoppedError) as e:
                print(str(e))
                break

            # Redimensiona imagem para diminuir os gastos de detecção de 
            # movimento.
            frame = ktools.resize(frame, min(self.max_largura_frame, frame.shape[1]))

            # Se houver mudança no frame ou já passou do tempo limite
            # sem detecção, detectar pessoas.
            if (not detector_movimento.detecta_movimento(frame) 
                and time.time()-tempo_em_que_parou < MAX_TEMPO_PARADO):
                #
                modo = 'parado'
            elif time.time()-tempo_ultima_deteccao > self.max_tempo_sem_deteccao:
                modo = 'detectando'
            else:
                modo = 'rastreando'

            if modo == 'detectando':
                try:
                    _, caixas, pesos = self.detectorPessoas.detecta_pessoas(
                        frame, desenha_retangulos=False)
                except Exception as e:
                    print('Erro de detecção:\n\t[{}]: {}'
                        .format(type(e).__name__, str(e)))
                    break
                tempo_ultima_deteccao = time.time()
            elif modo == 'rastreando':
                if ultimo_modo != modo:
                    rastreador.reiniciar()
                    rastreador.adiciona_rastreadores(
                        frame,
                        self.pessoas_registradas.pega_pessoas(retorna_peso=False)
                    )
                caixas = rastreador.atualiza(frame)
                pesos = []
            elif modo == 'parado':
                if ultimo_modo != modo:
                    tempo_em_que_parou = time.time()
                caixas, pesos = [], []
                    
            # Se a iteração for muito lenta, reiniciar o registro.
            if time.time()-tempo_comeco_iteracao > MAX_TEMPO_ENTRE_REGISTROS:
                self.pessoas_registradas.reiniciar()

            caixas, pesos = self.pessoas_registradas.atualizar(
                caixas, pesos, caixas_paradas=(modo=='parado'))

            # Salva o numero de pessoas registradas neste ciclo.
            self.pessoas_historico.atualiza_periodo(len(caixas))

            if not self.mostrar_caixas:
                novo_frame = frame
            else:
                novo_frame = ktools.draw_boxes(
                frame, boxes=caixas, infos=pesos,
                write_infos=self.mostrar_precisao)
            ktools.write(novo_frame, modo, x=10, y=novo_frame.shape[0]-10,
                         outline=True)
            self.frame = novo_frame

            ultimo_modo = modo

            # Dormir de forma que o tempo do loop dê 'PERIODO_MINIMO'.
            tempo_iteracao = time.time() - tempo_comeco_iteracao
            print(tempo_iteracao)
            if tempo_iteracao <= PERIODO_MINIMO:
                time.sleep(PERIODO_MINIMO-tempo_iteracao)

        detector_movimento.stop()
        if not self.stream_externo:
            self.stream.stop()
        self.stop()


    def pega_pessoas(self):
        '''Retorna o número de pessoas registradas no momento.
        
        Returns
        -------
        int
        '''
        return len(self.pessoas_registradas)

    def pega_frame(self):
        '''Retorna o último frame analizado.
        
        Returns
        --------
        numpy.ndarray
            Frame a ser retornado. Antes de qualquer frame ser lido
            da fonte, retorna uma imagem preta de mesmas dimensões do
            vídeo.
        '''

        if self.frame is not None:
            return self.frame
        else:
            return ktools.black_image(*self.stream.pega_dimensoes())

    def pega_dados_periodo(self):
        '''Retorna dados coletados desde a última chamada (ou início).

        Returns
        --------
        media : float
            Média ponderada dos valores com o intervalo de tempo.
        max_valor : float
            Valor máximo recebido.
        min_valor : float
            Valor mínimo recebido.
        tempo_decorrido : float
            Tempo total decorrido.
        '''
        return self.pessoas_historico.finaliza_periodo()