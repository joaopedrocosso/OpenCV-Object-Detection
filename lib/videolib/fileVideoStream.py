from .videoStreamCV import VideoStreamCV

class FileVideoStream(VideoStreamCV):
	
	'''Abre um arquivo de vídeo.

	Função de conveniência para VideoStreamCV.

	Parameters
	-----------
	src : str
		De onde pegar o vídeo. Espera-se uma string.
	
	See Also
	---------
	.videoStreamCV.VideoStreamCV
	'''

	def __init__(self, src):
		super().__init__(src, atualiza_frames_auto=False)