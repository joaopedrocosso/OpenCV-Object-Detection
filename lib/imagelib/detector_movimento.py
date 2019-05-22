import cv2 as cv
import numpy as np

class DetectorMovimento:

    '''Dececta movimento em um vídeo.
    
    Parameters
    -----------
    detectaSombras : bool, optional
        Se verdadeiro, ele marca sombras.
    '''

    def __init__(self, detectaSombras=True):

        self.subtractor = cv.createBackgroundSubtractorMOG2(
            detectShadows=detectaSombras)
        self.frame = None

    def detectaMovimento(self, frame, mudancaMinima=0.015):

        '''Checa se houve movimento no vídeo.

        Parameters
        -----------
        frame : numpy.ndarray
            Novo frame do vídeo.
        mudancaMinima : float, optional
            Valor mínimo para que um movimento tenha ocorrido.
            (0.0 <= 'mudancaMinima' <= 1.0) (Padrão=#####TODO)

        Returns
        --------
        bool
            Verdadeiro, se houve mudança, e falso, caso contrário.
        '''

        porcentagemMudanca = self._aplicarMascaraNew(frame)
        #print('>> {} || {}'.format(porcentagemMudanca, mudancaMinima))
        return (porcentagemMudanca >= mudancaMinima)

    def _aplicarMascaraNew(self, novo_frame):
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
        
        novo_frame = cv.GaussianBlur(novo_frame, (21, 21), 0)
        if self.frame is None:
            self.frame = novo_frame
            return 0

        if novo_frame.shape != self.frame.shape:
            raise ValueError(
                'Novo frame deve ter tamanho identico aos frames anteriores.')

        diff = cv.absdiff(self.frame, novo_frame)

        self.frame = novo_frame

        return diff.sum()/(255*diff.shape[0]*diff.shape[1])




    def _aplicarMascara(self, frame):
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
        _, frameAlterado = cv.threshold(fgmask, 127, 255, cv.THRESH_BINARY)
        
        # Removo um pouco do "noise" criado pelo MOG2
        kernelOp = np.ones((3,3),np.uint8)# Kernel opening
        kernelCl = np.ones((11,11),np.uint8)# Kernel closing
        frameAlterado = cv.morphologyEx(frameAlterado, cv.MORPH_OPEN, kernelOp)
        frameAlterado = cv.morphologyEx(frameAlterado, cv.MORPH_CLOSE, kernelCl)

        # Checa quantos pixels foram modificados
        flatFrame = frameAlterado.flatten()
        porcentagemMudanca = (flatFrame.sum()/255) / flatFrame.shape[0]

        return porcentagemMudanca