class VideoStreamError(Exception):
	
	'''Exceção genérica de erros em leitores de vídeo.

	Parameters
	-----------
	message : str, opcional
		Mensagem a imprimir. (Padrão='')
	*args
		Parâmetros adicionais para enviar à classe Exception.
	'''

	def __init__(self, message='', *args):
		super().__init__(message, *args)


class CannotOpenStreamError(VideoStreamError):

	'''Exceção para quando não é possível abrir um stream.

	Parameters
	-----------
	message : str, opcional
		Mensagem a imprimir. (Padrão='')
	*args
		Parâmetros adicionais para enviar à classe Exception.
	'''

	pass

class StreamClosedError(VideoStreamError):

	'''Exceção para quando o stream já foi fechado.

	Parameters
	-----------
	message : str, opcional
		Mensagem a imprimir. (Padrão='')
	*args
		Parâmetros adicionais para enviar à classe Exception.
	'''

	pass

class StreamStoppedError(VideoStreamError):

	'''Exceção para quando o stream já foi parado.

	Parameters
	-----------
	message : str, opcional
		Mensagem a imprimir. (Padrão='')
	*args
		Parâmetros adicionais para enviar à classe Exception.
	'''

	pass	