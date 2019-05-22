import os

from .detector_pessoas_ssd import DetectorPessoasSSD
from .detector_pessoas_yolo import DetectorPessoasYolo

DEFAULT_PRECISAO_DETECCAO = 0.4
DEFAULT_SUPRESSAO_DETECCAO = 0.3

class DetectorPessoas:

	'''Detecta pessoas usando um modelo de deep learning.

	Parameters
	-----------
	path_modelo : str
		Destino do modelo desejado.
	tipo_modelo : {'yolo', 'ssd'}. optional
		Tipo do modelo.
	precisao : float, optional
		Quão precisa a detecção deve ser. Deve estar entre 0.0 e 1.0 incl.
	supressao : float, optional
		Quão próximas as detecções de pessoas devem estar para
		serem consideradas as mesmas. Deve estar entre 0.0 e 1.0 incl.

	Raises
	-------
	ValueError
		Se o tipo do modelo for invalido.
	Exceções relacionadas ao OpenCV
	'''

	def __init__(self, path_modelo, tipo_modelo='yolo', precisao=DEFAULT_PRECISAO_DETECCAO,
				 supressao=DEFAULT_SUPRESSAO_DETECCAO):
		
		if not os.path.isdir(path_modelo):
			path_modelo = os.path.join(os.getcwd(), path_modelo)

		path_modelo = os.path.abspath(path_modelo)

		if tipo_modelo == 'yolo':
			self.detector = DetectorPessoasYolo(path_modelo, precisao, supressao)
		elif tipo_modelo == 'ssd':
			self.detector = DetectorPessoasSSD(path_modelo, precisao, supressao)
		else:
			raise ValueError('Tipo do modelo invalido.')

	def detecta_pessoas(self, input_image, desenha_retangulos=True):
		'''Detecta pessoas em uma imagem.

		Parameters
		-----------
		img : numpy.ndarray de dimensões (n, m, 3)
			Imagem a ser analizada. (formato BGR)
		desenha_retangulos : bool, optional
			Se deve retornar uma imagem com as pessoas enquadradas.
			(padrão=True)
		
		Returns
		--------
		img : numpy.ndarray
			Imagem com as pessoas enquadradas, se desenha_retangulos=True.
			Caso contrário, é a imagem original. (formato BGR)
		caixas_com_peso : ((int, int, int, int), float)
			Array de tuplas onde o primeiro elemento é uma 4-upla
			que representa uma caixa (x, y, w, h) e a segunda é a
			probabilidade da caixa representar uma pessoa.
		'''
		return self.detector.detecta_pessoas(input_image, desenha_retangulos)
