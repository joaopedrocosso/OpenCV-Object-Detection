from .videoStreamCV import VideoStreamCV

class WebcamVideoStream(VideoStreamCV):
	
	def __init__(self, src=0):
		'''Abre webcam ou outro dispositivo de vídeo desprotegido.

		Função de conveniência para VideoStreamCV.

		Parâmetros:
			'src': De onde pegar o vídeo. Pode ser um número ou uma string.
		Métodos:
			'start': Começa uma thread onde os frames serão lidos, se atualiza_frames_auto=True.
			'update': Lê frames da fonte até o stream ser fechado ou a leitura ser parada.
			'read': Lê o frame mais recente.
			'stop': Para a leitura.
		'''

		super().__init__(src)
