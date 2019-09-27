import time
import cv2 as cv
from threading import Thread
from collections import deque

from imagelib import ktools
from videolib.videoStream import VideoStream
from deteccao_objetos_lib.detector_movimento_cv import DetectorMovimentoCV as DetectorMovimento
from deteccao_pessoas_lib.detector_pessoas import DetectorPessoas
from deteccao_objetos_lib.caixas_objetos_lib.caixas_objetos import CaixasObjetos
from deteccao_pessoas_lib.pessoas_historico import PessoasHistorico
from videolib.abstractVideoStream import AbstractVideoStream
from videolib.exceptions import CannotOpenStreamError, StreamClosedError, StreamStoppedError
from toolslib.ktools import LoopPeriodControl

class DetectorPessoasVideo(Thread):

    '''Detecta pessoas em um vídeo em uma thread separada.

    Deve-se configurar o objeto chamando os métodos 'configura_video'
    ou 'recebe_video', para haver uma entrada de vídeo, e
    'configura_detector', para configurar o detector de pessoas.

    Parameters
    -----------
    max_tempo_sem_deteccao : float, optional
        Tempo máximo que se pode ficar usando métodos mais leves de
        detecção, ao invés do principal. Em casos em que o detector seja
        leve, o valor pode ser 0 (i.e. sempre detectar).
        Deve ser positivo ou zero. (Padrão=10)
    max_largura_frame : int, optional
        Se o frame do vídeo for maior que este valor, ele será
        redimensionado. Deve ser positivo. (Padrão=700)

    Raises
    ------
    ValueError
        Se um dos argumentos não atender às especificações.
    '''

    def __init__(self, max_tempo_sem_deteccao=10.0, max_largura_frame=700):

        super().__init__()
        
        if max_tempo_sem_deteccao < 0:
            raise ValueError(
                "'max_tempo_sem_deteccao' deve ser um número positivo.")
        if max_largura_frame <= 0:
            raise ValueError(
                "'max_largura_frame' deve ser um número positivo ou zero.")
        self.max_tempo_sem_deteccao = max_tempo_sem_deteccao
        self.max_largura_frame = max_largura_frame

        self.pessoas_historico = PessoasHistorico()
        self.pessoas_registradas = CaixasObjetos()

        self.frame = None
        self.stream = None
        self.detector_pessoas = None
        self.stopped = False
        self.stream_externo = False

        self.modo = ''

    def configura_video(self, tipo, tempo_dormir=2.0, **keywords):

        '''Configura a entrada de vídeo internamente.

        Parameters
        -----------
        tipo : {'picamera', 'ipcamera', 'webcam', 'arquivo'}
            Tipo da câmera.
        tempo_dormir : float, optional
            Tempo passado para 'time.sleep()'. Usado para permirir que
            a câmera tenha tempo de começar a enviar os frames.
        
        **kwargs
            resolucao : (int, int), optional
                Se 'picamera' foi escolhido.
                Tupla que representa a resolução do vídeo. Ex.: (320, 240).
            fps : int, optional
                Se 'picamera' foi escolhido.
                Frames por segundo.
            cameraURL : str, optional
                Se 'ipcamera' foi escolhido.
                Url da câmera.
            login: str, optional
                Se 'ipcamera' foi escolhido.
                Login da câmera.
            senha: str, optional
                Se 'ipcamera' foi escolhido.
                Senha da câmera.
            idCam : str or int, optional
                Se 'webcam' foi escolhido.
                Número da câmera. (padrão=0)
            arquivo : str, optional
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
        recebe_video : Para receber um leitor de vídeo de fora.
        '''
        try:
            self.stream = VideoStream(tipo, **keywords)
        except (ImportError, CannotOpenStreamError):
            raise
        self.stream_externo = False

        # Para dar tempo de inicializar a câmera.
        if tempo_dormir > 0:
            time.sleep(tempo_dormir)

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
        tipo_modelo : {'yolo'}, optional
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
            self.detector_pessoas = DetectorPessoas(
                dir_modelo, tipo_modelo=tipo_modelo, precisao=precisao_deteccao)
        except Exception:
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

        if self.stream is None or self.detector_pessoas is None:
            print('Erro: stream ou detector de pessoas não configurado.')
            return
        self.stream.start()
        time.sleep(2)
        
        detector_movimento = (
            DetectorMovimento(periodo_minimo=PERIODO_MINIMO)
            .recebe_video(self.stream)
            .start()
        )
        modo_deteccao = ModoDeteccao(
            detector_movimento, self.max_tempo_sem_deteccao
        )
        controla_periodo_loop = LoopPeriodControl(PERIODO_MINIMO)
        
        ERRO_LEITURA_MAXIMO = 3
        erro_leitura_counter = 0
        while not self.stopped:
            
            tempo_comeco_iteracao = time.time()
            try:
                frame = self.stream.read()
            except (StreamClosedError, StreamStoppedError) as e:
                if erro_leitura_counter < ERRO_LEITURA_MAXIMO:
                    #Adicionar método de reiniciar vídeo.
                    erro_leitura_counter += 1
                    continue
                print('Não foi possível ler frame.')
                break
            erro_leitura_counter = 0

            # Redimensiona imagem para diminuir os gastos de detecção 
            # de movimento.
            frame = self._frame_tamanho_maximo(frame)

            # Decide se o loop estará no modo 'detectando' ou 'parado'.
            modo = modo_deteccao.atualiza_modo()
            
            if modo == 'detectando':
                try:
                    caixas, pesos = self.detector_pessoas.detectar(frame)
                except Exception as e:
                    print('Erro de detecção:\n\t[{}]: {}'
                        .format(type(e).__name__, str(e)))
                    break
            else: #modo == 'parado':
                caixas, pesos = [], []

            # Se a iteração for muito lenta, reiniciar o registro.
            if time.time()-tempo_comeco_iteracao > MAX_TEMPO_ENTRE_REGISTROS:
                self.pessoas_registradas.reiniciar()

            caixas, pesos = self.pessoas_registradas.atualizar(
                caixas, pesos, caixas_paradas=(modo=='parado')
            )
            self.frame = frame.copy()
            self.modo = modo

            # Salva o numero de pessoas registradas neste ciclo.
            self.pessoas_historico.atualiza_periodo(len(caixas))
            # Período do loop >= 'PERIODO_MINIMO'.
            controla_periodo_loop.force_minimum_loop_period()

        detector_movimento.stop()
        if not self.stream_externo:
            self.stream.stop()
        self.stop()


    def pega_quantidade_pessoas(self):
        '''Retorna o número de pessoas registradas no momento.
        
        Returns
        -------
        int
        '''
        return len(self.pessoas_registradas)

    def pega_frame(self, mostrar_caixas=False, mostrar_precisao=False, mostrar_modo=False):
        '''Retorna o último frame analizado.
        
        Parameters
        -----------
        mostrar_caixas : bool, optional
            Se as caixas que representam as pessoas devem ser 
            desenhadas na tela. (Padrão=False)
        mostrar_precisao : bool, optional
            Se a precisão de detecção deve ser desenhada em cima das
            caixas. Se 'mostrar_caixas' for falso esta opção também
            será. (Padrão=False)
        mostrar_modo : bool,, optional
            Se o modo de detecção da última iteração deve ser escrito.
            (Padrão=False)

        Returns
        --------
        numpy.ndarray
            Frame a ser retornado. Antes de qualquer frame ser lido
            da fonte, retorna uma imagem preta de mesmas dimensões do
            vídeo.
        
        Raises
        ------
        RuntimeError
            Se o stream ainda não foi inicializado, pois é preciso ter
            a resolução do stream para poder gerar o frame preto.
        '''

        if self.frame is None:
            # Levanta RuntimeError
            return self.pega_frame_preto()
        
        frame = self.frame.copy()

        if mostrar_caixas:
            caixas, pesos = self.pessoas_registradas.pega_objetos()
            frame = self._desenha_caixas(frame, caixas, pesos, mostrar_precisao)
        if mostrar_modo:
            ktools.write(frame, self.modo, x=10, y=frame.shape[0]-10, outline=True)
        
        return frame

    def pega_frame_preto(self):
        '''Retorna um frame preto do tamanho da câmera.
        
        Returns
        --------
        numpy.ndarray
            Imagem preta na mesma resolução do vídeo ou da resolução
            máxima.
        
        Raises
        ------
        RuntimeError
            Se o stream ainda não foi inicializado, pois é preciso ter
            a resolução do stream para poder gerar o frame preto.
        '''

        if self.stream is None:
            raise RuntimeError('Stream ainda não foi inicializado.')
        return self._frame_tamanho_maximo(
                ktools.black_image(*self.stream.pega_dimensoes())
            )

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
    
    def _frame_tamanho_maximo(self, frame):
        '''Redimensiona o frame para a largura máxima, se necessário.'''
        if frame.shape[1] > self.max_largura_frame:
            return ktools.resize(frame, self.max_largura_frame)
        else:
            return frame.copy()
    
    def _desenha_caixas(self, frame, caixas, pesos, mostrar_precisao):
        pesos = ['{:.3f}'.format(p) for p in pesos]
        return ktools.draw_boxes(
            frame, boxes=caixas, infos=pesos, write_infos=mostrar_precisao)



class ModoDeteccao:

    '''Escolhe o modo de detecção de um loop em DeteccaoPessoasVideo.
    
    Parameters
    -----------
    detector_movimento : imagelib.detector_movimento.DetectorMovimento
        Objeto que detecta movimento em um vídeo. Assume-se que já 
        esteja configurado e iniciado.
    max_tempo_sem_deteccao : float
        Tempo máximo que se pode ficar usando métodos mais leves de
        detecção, ao invés do principal. Em casos em que o detector seja
        leve, o valor pode ser 0 (i.e. sempre detectar).
        Deve ser positivo ou zero.
    '''

    def __init__(self, detector_movimento, max_tempo_sem_deteccao):

        self.detector_movimento = detector_movimento
        self.max_tempo_sem_deteccao = max_tempo_sem_deteccao

        self.tempo_ultima_deteccao = time.time()-self.max_tempo_sem_deteccao

        self.historico_modo = Historico(['', ''], limite=2)
    
    def atualiza_modo(self):
        '''Atualiza o modo no qual a detecção se encontra.

        Returns
        --------
        novo_modo : str
        '''
        self.checagem_atual = time.time()

        penultimo_modo, ultimo_modo = self.historico_modo.pega_historico()

        teve_movimento = self.detector_movimento.houve_mudanca()
        sem_detectar_demais = self._esta_sem_detectar_demais()

        if ultimo_modo == 'detectando':
            if not teve_movimento and penultimo_modo == 'detectando':
                novo_modo = 'parado'
            else:
                novo_modo = 'detectando'
            
        elif ultimo_modo == 'parado':
            if teve_movimento or sem_detectar_demais:
                novo_modo = 'detectando'
            else:
                novo_modo = 'parado'
        else:
            novo_modo = 'detectando'
        
        if novo_modo == 'detectando':
            self.tempo_ultima_deteccao = time.time()

        self.historico_modo.adiciona(novo_modo)
        return novo_modo

    def mudou_modo(self):
        '''Retorna se o modo mudou ou não desde a última atualização.

        Returns
        --------
        bool
        '''
        penultimo_modo, ultimo_modo = self.historico_modo.pega_historico()
        return penultimo_modo != ultimo_modo
    
    def _esta_sem_detectar_demais(self):
        '''Retorna se o tempo sem detecção já passou do limite.'''
        return time.time()-self.tempo_ultima_deteccao >= self.max_tempo_sem_deteccao



class Historico:

    '''Cria um histórico com um número máximo de valores.

    Parameters
    ----------
    valores_iniciais : iterable, optional
        Valores iniciais da lista. Caso não seja fornecido, o histórico
        começará vazio.
    limite : int, optional
        O limite de elementos do histórico. Caso não seja fornecido ou
        seja None, o histórico será ilimitado.

    Raises
    ------
    ValueError
        Se o limite não for positivo.
    TypeError
        Se os parâmetros não tiverem os tipos corretos.

    '''

    def __init__(self, valores_iniciais=[], limite=None):
        # Levanta exceções.
        self._checa_parametros_init(valores_iniciais, limite)
        
        self.historico = deque(iterable=valores_iniciais, maxlen=limite)
    
    def adiciona(self, elemento):
        '''Adiciona novo elemento ao histórico.

        Parameters
        ----------
        elemento : object
            Novo elemento.
        '''
        self.historico.append(elemento)

    def pega_historico(self):
        '''Pega histórico completo.

        Returns
        -------
        iterator
        '''
        return iter(self)

    def __iter__(self):
        return iter(self.historico)
    
    def _checa_parametros_init(self, valores_iniciais, limite):
        '''Checa parâmetros da __init__ e levanta as exceções apropriadas.'''
        try:
            iter(valores_iniciais)
        except TypeError:
            raise TypeError("'valores_iniciais' não é iterável.")
        try:
            limite = int(limite)
        except ValueError:
            raise TypeError("'limite' deve ser inteiro ou convertível.")
        if limite <= 0:
            raise ValueError("'limite' deve ser positivo.")
