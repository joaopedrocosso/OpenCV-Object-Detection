from .videoStreamCV import VideoStreamCV

class FileVideoStream(VideoStreamCV):
	
	def __init__(self, src):
		'''Abre um arquivo de vídeo.

		Função de conveniência para VideoStreamCV.

		Parâmetros:
			'src': De onde pegar o vídeo. Espera-se uma string.
		Métodos:
			'start': Começa uma thread onde os frames serão lidos, se atualiza_frames_auto=True.
			'update': Lê frames da fonte até o stream ser fechado ou a leitura ser parada.
			'read': Lê o frame mais recente.
			'stop': Para a leitura.
		'''

		super().__init__(src, atualiza_frames_auto=False)