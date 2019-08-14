from .videoStreamCV import VideoStreamCV

class WebcamVideoStream(VideoStreamCV):
	
	'''Pega frames de um dispositivo IP.

    Parameters
    ----------
    src : int or str, optional
        De onde pegar o vídeo. (Padrão=0)
    
    Raises
    -------
    CannotOpenStreamError
        Se não for possível abrir o stream.
    '''

	def __init__(self, src=0):
		super().__init__(src)
