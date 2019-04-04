class Pessoa:
	
	def __init__(self, i, x, y, w, h, peso=None, minFramesParaConfirmar=5, maxTempoDesaparecida=20):
		
		self.id = i #ID da pessoa

		# Levantam ValueError
		self.x, self.y, self.w, self.h = self._mudaCoordenadasDaCaixa(x, y, w, h)
		self.peso = self._mudaPeso(peso)

		self.tracks = [] #lista de pontos que a pessoa esteve
		
		self.tempoDesaparecida = 0

		try:
			self.maxTempoDesaparecida = int(maxTempoDesaparecida)
			self.minFramesParaConfirmar = int(minFramesParaConfirmar)

			if minFramesParaConfirmar < 0 or  maxTempoDesaparecida < 0:
				raise ValueError()
		except ValueError:
			raise ValueError("'maxTempoDesaparecida' e 'minFramesParaConfirmar' devem ser inteiros positivos.")
		
		self.viva = True #Verdadeiro se o tempo desaparecido nao exceder o limite
		self.pessoaConfirmada = False #Se existiu por tempo suficiente.
		self.framesCount = 0
		
	
	def atualiza(self, x, y, w, h, peso=None):
		
		xAntigo, yAntigo = self.x, self.y

		# Levantam ValueError
		self._mudaCoordenadasDaCaixa(x, y, w, h)
		self._mudaPeso(peso)

		#reseta a idade,incrementa o numero de frames em que apareceu e adiciona a nova posicao
		self.tempoDesaparecida = 0
		self.framesCount+=1 #Se passar do framesMin ele passa a ser considerado
	
		self.tracks.append((self.x,self.y))#Guardando as coordenadas antigas
	
		if self.framesCount > self.minFramesParaConfirmar:
			self.pessoaConfirmada = True #ela existe

	
	def getTracks(self):
    	#Retorna a lista de coordenadas em que essa pessoa apareceu
		return self.tracks

	def envelhece(self):
    
    	#Incrementa a idade e checa se ela ja morreu
		self.tempoDesaparecida+=1
		if self.tempoDesaparecida > self.maxTempoDesaparecida:
			self.viva = False


	def isViva(self):
		return self.viva
	def isConfirmada(self):
		return self.pessoaConfirmada


	def __str__(self):

		return '#{}: (x={}, y={}), (w={}, h={}), peso={}, {} e {}'.format(
			self.id, self.x, self.y, self.w, self.h, self.peso,
			'viva' if self.viva else 'morta',
			'confirmada' if self.pessoaConfirmada else 'nao confirmada'
		)

	def _mudaPeso(self, peso):

		if peso is not None:
			try:
				peso = float(peso)
			except ValueError:
				raise ValueError('Peso deve ser um numero real.')

			if peso < 0.0 or peso > 1.0:
				raise ValueError('Peso deve ser um numero entre 0.0 e 1.0.')

		self.peso = peso
		return peso

	def _mudaCoordenadasDaCaixa(self, x, y, w=None, h=None):
		
		try:
			self.x = int(x)
			self.y = int(y)
		except ValueError:
			raise ValueError('Posicao (x, y) deve ser composta de numeros (que possam ser convertidos para) inteiros.')

		if w is not None and h is not None:
			try:
				self.w = int(w)
				self.h = int(h)
				if w <= 0 or h <= 0:
					raise ValueError()
			except ValueError:
				raise ValueError('Largura e altura (w, h) devem ser numeros (que possam ser convertidos para) inteiros positivos.')
		else:
			try:
				self.w
				self.h
			except AttributeError:
				raise AttributeError('Valores de largura e altura devem ser fornecidos ao menos uma vez.')


		return x, y, w, h