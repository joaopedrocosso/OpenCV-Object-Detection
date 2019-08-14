import time
import threading

from .videoWriterCV import VideoWriterCV
from toolslib.ktools import LoopPeriodControl

class GuardaFramesPeriodo(threading.Thread):

    '''Guarda os frames de uma função fonte em um arquivo de vídeo.

    Parameters
    -----------
    nome_arquivo : str
        Nome do arquivo onde os frames serão salvos.
    source : object
        Uma entrada de vídeo 
    fps : int
        Frames por segundo que o vídeo deve ter. (Padrão=10)
    resolucao_video : (int, int)
        Resolução do vídeo (largura, altura). (Padrão=(640, 480))
    '''

    def __init__(self, nome_arquivo, source, fps=10, resolucao_video=(640, 480)):
        super().__init__()
        self.out = VideoWriterCV(nome_arquivo, fps=fps, resolucao_do_video=resolucao_video)
        self.fps = fps
        self.source = source
        self.stopped = False
    
    def start(self):
        '''Começa uma thread para guardar os frames.

        Returns
        --------
        self
        '''
        super().start()
        return self

    def run(self):
        '''
        Guarda os frames da função fonte no arquivo destino até que a
        thread seja parada ou que o objeto fonte levante alguma exceção.
        '''

        controle_loop = LoopPeriodControl(1/self.fps)
        while not self.stopped:
            try:
                frame = self.source.read()
            except:
                break
            self.out.atualizar(frame)
            controle_loop.force_minimum_loop_period()
        if not self.stopped:
            self.stop()
        self.out.fechar()
    
    def stop(self):
        '''Para a thread.'''
        self.stopped = True

