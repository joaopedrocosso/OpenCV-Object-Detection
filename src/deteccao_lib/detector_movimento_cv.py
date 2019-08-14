import time
import cv2 as cv
import numpy as np
from threading import Thread

from videolib.abstractVideoStream import AbstractVideoStream
from videolib.exceptions import StreamClosedError, StreamStoppedError
from imagelib import ktools

class DetectorMovimentoCV(Thread):

    '''Detecta movimento em um vídeo.

    Deve-se chamar o método 'recebe_video' antes de rodar a thread.
    
    Parameters
    -----------
    detecta_sombras : bool, optional
        Se verdadeiro, ele marca sombras.
    mudanca_minima : float, optional
        Valor mínimo para que um movimento tenha ocorrido.
        (0.0 <= 'mudanca_minima' <= 1.0) (Padrão=0.001)
    periodo_minimo : float, optional
        Período mínimo por deteccção de movimento. (> 0.0) (Padrão=0.5)
    '''

    def __init__(self, detecta_sombras=True, mudanca_minima=0.001,
                 periodo_minimo=0.0, max_largura_frame=700):

        super().__init__()

        self.subtractor = cv.createBackgroundSubtractorMOG2(
            detectShadows=detecta_sombras)
        self.frame = None
        self.mudanca_minima = mudanca_minima
        self.periodo_minimo = periodo_minimo
        self.max_largura_frame = max_largura_frame
        
        self._houve_mudanca = False
        self.stopped = False
        self.stream = None
        self.porcentagem_ultimo_movimento = 0.0

    def recebe_video(self, stream):
        if not isinstance(stream, AbstractVideoStream):
            raise TypeError("Stream deve herdar de 'AbstractVideoStream'.")
        self.stream = stream
        return self

    def start(self):
        '''Começa a thread.
        
        Returns
        --------
        self
        '''
        super().start()
        return self

    def run(self):
        '''Detecta movimento uma vez a cada período.'''

        if self.stream is None:
            print('Erro: stream deve ser fornecido.')

        while not self.stopped:
            tempo_comeco_iteracao = time.time()

            try:
                frame = self.stream.read()
            except (StreamClosedError, StreamStoppedError) as e:
                print(str(e))
                break

            if frame.shape[1] > self.max_largura_frame:
                frame = ktools.resize(frame, self.max_largura_frame)

            self._houve_mudanca = self.detecta_movimento(frame)
            
            tempo_iteracao = time.time()-tempo_comeco_iteracao
            if tempo_iteracao < self.periodo_minimo:
                time.sleep(self.periodo_minimo-tempo_iteracao)

        self.stop()

    def stop(self):
        '''Para a thread.'''
        self.stopped = True

    def houve_mudanca(self):
        '''Retorna se houve algura mudança no vídeo.

        Returns
        --------
        bool
        '''
        return self._houve_mudanca

    def detecta_movimento(self, frame):
        '''Checa se houve movimento no vídeo.

        Parameters
        -----------
        frame : numpy.ndarray
            Novo frame do vídeo.

        Returns
        --------
        bool
            Verdadeiro, se houve mudança, e falso, caso contrário.
        '''

        porcentagem_mudanca = self._aplicar_mascara(frame)
        self.porcentagem_ultimo_movimento = porcentagem_mudanca
        #print('>> {} || {}'.format(porcentagem_mudanca, mudanca_minima))
        return (porcentagem_mudanca >= self.mudanca_minima)
    
    def pega_porcentagem_ultimo_movimento(self):
        '''Retorna a porcentagem de mudança do último movimento.
        
        Returns
        --------
        float
        '''
        return self.porcentagem_ultimo_movimento

    def _aplicar_mascara(self, frame):
        '''Retorna a taxa de mudança no vídeo.

        Parameters
        -----------
        novo_frame : numpy.ndarray
            Novo frame do vídeo

        Returns
        --------
        float
            Taxa de mudança entre 0.0 e 1.0, incl.
        '''
        
        # limpa pequenas mudancas da propria camera
        frame = cv.GaussianBlur(frame, (21, 21), 0)
        # mascara do backgroundsubtractor
        fgmask = self.subtractor.apply(frame)

        # Aplicando um threshold para limitar aos movimentos mais importantes
        _, frame_alterado = cv.threshold(fgmask, 127, 255, cv.THRESH_BINARY)
        
        # Removo um pouco do "noise" criado pelo MOG2
        kernel_op = np.ones((3,3),np.uint8)# Kernel opening
        kernel_cl = np.ones((11,11),np.uint8)# Kernel closing
        frame_alterado = cv.morphologyEx(frame_alterado, cv.MORPH_OPEN, kernel_op)
        frame_alterado = cv.morphologyEx(frame_alterado, cv.MORPH_CLOSE, kernel_cl)

        # Checa quantos pixels foram modificados
        flat_frame = frame_alterado.flatten()
        porcentagem_mudanca = (flat_frame.sum()/255) / flat_frame.shape[0]

        return porcentagem_mudanca