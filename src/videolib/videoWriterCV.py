import cv2 as cv
import numpy as np

'''
Notes
------
https://docs.opencv.org/3.4/dd/d9e/classcv_1_1VideoWriter.html
https://theailearner.com/2018/10/15/creating-video-from-images-using-opencv-python/
'''

class VideoWriterCV:

    '''Salva frames em um arquivo de vídeo.

    Parameters
    -----------
    nome_arquivo : str
        Nome do arquivo onde os frames serão salvos.
    fourcc : str
        Código fourcc referente a um tipo de encoding de vídeo.
        (Padrão='DIVX')
    fps : int
        Frames por segundo que o vídeo deve ter. (Padrão=15)
    resolucao_do_video : (int, int)
        Resolução do vídeo (largura, altura). (Padrão=(640, 480))
    colorido : bool
        Se for verdadeiro, espera-se frames coloridos. Caso contrário,
        espera-se frames em preto e branco.
    
    Raises
    -------
    ValueError
        Se o valor de fourcc não for uma string de 4 caracteres.
    '''

    def __init__(self, nome_arquivo, fourcc='DIVX', fps=15, resolucao_do_video=(640, 480), colorido=True):
        
        try:
            fourcc = cv.VideoWriter_fourcc(*'DIVX')
        except TypeError:
            raise ValueError('Código fourcc deve ser uma string de 4 caracteres.')

        self.out = cv.VideoWriter(nome_arquivo, fourcc, fps, resolucao_do_video, colorido)        

    def atualizar(self, frames):
        '''Adiciona um ou mais frames ao vídeo.

        Parameters
        -----------
        frames : numpy.ndarray or [numpy.ndarray, ...]
            Um ou mais frames para serem adicionados.
        '''
        
        if isinstance(frames, np.ndarray):
            frames = [frames]

        for frame in frames:
            self.out.write(frame)
    
    def fechar(self):
        '''Fecha o stream.'''
        self.out.release()

    
    
    