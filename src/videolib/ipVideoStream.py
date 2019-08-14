from .videoStreamCV import VideoStreamCV

class IPVideoStream(VideoStreamCV):

    '''Pega frames de um dispositivo IP.

    Parameters
    ----------
    src : str
        De onde pegar o vídeo. (Padrão=0)
    login, senha: str
        Se ambos forem disponibilizados, o endereço de src recebe
        esses valores. (Padrão=None)
    
    Raises
    -------
    CannotOpenStreamError
        Se não for possível abrir o stream.
    '''
    
    def __init__(self, src, login, senha):
        super().__init__(src, login, senha)