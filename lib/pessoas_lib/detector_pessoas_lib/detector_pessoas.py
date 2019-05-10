import os

from .detector_pessoas_ssd import DetectorPessoasSSD
from .detector_pessoas_yolo import DetectorPessoasYolo

class DetectorPessoas:

	DEFAULT_PRECISAO_DETECCAO = 0.4
	DEFAULT_SUPRESSAO_DETECCAO = 0.3

	def __init__(self, path_modelo, tipo_modelo='yolo', precisao=DEFAULT_PRECISAO_DETECCAO,
				 supressao=DEFAULT_SUPRESSAO_DETECCAO):

		'''Detecta pessoas usando um modelo de deep learning.

		parâmetros:

			'path_modelo': Destino do modelo desejado.
			'tipo_modelo': Tipo do modelo. Pode ser 'yolo' ou 'ssd'
			'precisao': Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0.
			'supressao': Quão próximas as detecções de pessoas devem estar para serem
				consideradas as mesmas.

		Joga as excecoes:
			'ValueError': se o tipo do modelo e' invalido.
			Excecoes relacionadas ao OpenCV.
		'''

		if not os.path.isdir(path_modelo):
			path_modelo = os.path.join(os.getcwd(), path_modelo)

		path_modelo = os.path.abspath(path_modelo)

		if tipo_modelo == 'yolo':
			self.detector = DetectorPessoasYolo(path_modelo, precisao)
		elif tipo_modelo == 'ssd':
			self.detector = DetectorPessoasSSD(path_modelo, precisao)
		else:
			raise ValueError('Tipo do modelo invalido.')

	def detecta_pessoas(self, input_image, desenha_retangulos=True):

		return self.detector.detecta_pessoas(input_image, desenha_retangulos)
