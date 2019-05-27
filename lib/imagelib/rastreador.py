import cv2 as cv

class Rastreador:
	
	'''Rastreia objetos em um vídeo.

	Parameters
	-----------
	tipo_rastreador : str, optional
		Tipos de rastreador. As opções são:
		'csrt',
		'kcf', (Padrão)
		'boosting',
		'mil',
		'tld',
		'medianflow',
		'mosse'.
	'''

	def __init__(self, tipo_rastreador='kcf'):
		self._reiniciar()
		self.tipo_rastreador = tipo_rastreador

	def _reiniciar(self):
		'''Reinicia os rastreadores.'''
		self.rastreadores = cv.MultiTracker_create()

	def adiciona_rastreadores(self, frame, caixas):
		'''Adiciona rastreadores.

		Parameters
		-----------
		frame : numpy.ndarray
			Frame do vídeo onde objetos estão sendo rastreados.
		caixas : [(int, int, int, int), ...]
			Caixas que representam os objetos a serem rastreados
			(x, y, largura, altura).
		'''
		tracker = OPENCV_OBJECT_TRACKERS[self.tipo_rastreador]()
		for caixa in caixas:
			self.rastreadores.add(tracker, frame, caixa)

	def atualiza(self, frame):
		sucesso, caixas = self.rastreadores.update(frame)
		return caixas


OPENCV_OBJECT_TRACKERS = {
	'csrt': cv.TrackerCSRT_create,
	'kcf': cv.TrackerKCF_create,
	'boosting': cv.TrackerBoosting_create,
	'mil': cv.TrackerMIL_create,
	'tld': cv.TrackerTLD_create,
	'medianflow': cv.TrackerMedianFlow_create,
	'mosse': cv.TrackerMOSSE_create
}