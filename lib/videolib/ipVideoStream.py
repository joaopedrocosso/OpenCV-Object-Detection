from .videoStreamCV import VideoStreamCV

class IPVideoStream(VideoStreamCV):
    
    def __init__(self, src, login, senha):
        '''Acessa um dispositivo de vídeo IP que precisa de login e senha.

        Função de conveniência para VideoStreamCV.

        Parâmetros:
            'src': De onde pegar o vídeo. Pode ser um número ou uma string.
            'login' e 'senha': Se ambos não forem 'None', o endereço de src recebe esses valores.
        Métodos:
            'start': Começa uma thread onde os frames serão lidos, se atualiza_frames_auto=True.
            'update': Lê frames da fonte até o stream ser fechado ou a leitura ser parada.
            'read': Lê o frame mais recente.
            'stop': Para a leitura.
        '''

        super().__init__(src, login, senha)