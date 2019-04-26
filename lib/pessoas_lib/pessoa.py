class Pessoa:
	
	def __init__(self, x, y, w, h, peso=None, minFramesParaConfirmar=5, maxTempoDesaparecida=20):

		# Levanta ValueError
		self.x, self.y, self.w, self.h = self._checaCoordenadasCaixa(x, y, w, h)
		self.peso = self._checaPeso(peso)

		self.tracks = [] #lista de pontos que a pessoa esteve
		
		self.tempoDesaparecida = 0

		try:
			self.maxTempoDesaparecida = int(maxTempoDesaparecida)
			self.minFramesParaConfirmar = int(minFramesParaConfirmar)

			if minFramesParaConfirmar < 0 or maxTempoDesaparecida < 0:
				raise ValueError()
		except ValueError:
			raise ValueError("'maxTempoDesaparecida' e 'minFramesParaConfirmar' devem ser inteiros positivos.")
		
		self.viva = True #Verdadeiro se o tempo desaparecido nao exceder o limite
		self.pessoaConfirmada = False #Se existiu por tempo suficiente.
		self.framesCount = 0
		
	
	def atualiza(self, x, y, w, h, peso=None):
		
		xAntigo, yAntigo = self.x, self.y

		# Levantam ValueError
		self.x, self.y, self.w, self.h = self._checaCoordenadasCaixa(x, y, w, h)
		self.peso = self._checaPeso(peso)
	
		#Guardando as coordenadas antigas
		self.tracks.append((xAntigo, yAntigo))
	
		self.tempoDesaparecida = 0
		self.framesCount += 1

		if self.framesCount > self.minFramesParaConfirmar:
			self.pessoaConfirmada = True #ela existe

	
	def getTracks(self):
    	#Retorna a lista de coordenadas em que essa pessoa apareceu
		return self.tracks


	def aumentaTempoDesaparecida(self):

		self.tempoDesaparecida += 1
		if self.tempoDesaparecida > self.maxTempoDesaparecida:
			self.viva = False


	def isViva(self):
		return self.viva
	def isConfirmada(self):
		return self.pessoaConfirmada

	def getCoordenadas(self):
		return (self.x, self.y)
	def getCaixa(self):
		return self.x, self.y, self.w, self.h
	def getCaixaComPeso(self):
		return getCaixa(), self.peso


	def __str__(self):

		return '(x={}, y={}), (w={}, h={}), peso={}, {} e {}'.format(
			self.x, self.y, self.w, self.h, self.peso,
			'viva' if self.viva else 'morta',
			'confirmada' if self.pessoaConfirmada else 'nao confirmada'
		)

	def _checaPeso(self, peso):

		if peso is not None:
			try:
				peso = float(peso)
			except ValueError:
				raise ValueError('Peso deve ser um numero real, ou None.')

			if peso < 0.0 or peso > 1.0:
				raise ValueError('Peso deve ser um numero entre 0.0 e 1.0.')

		return peso

	def _checaCoordenadasCaixa(self, x, y, w, h):
		
		try:
			x = int(x)
			y = int(y)
		except ValueError:
			raise ValueError('Posicao (x, y) devem ser (ou poder ser convertidos para) inteiros.')

		try:
			w = int(w)
			h = int(h)
		except ValueError:
			raise ValueError('Largura e altura devem ser (ou poder ser convertidos para) inteiros positivos.')

		return x, y, w, h