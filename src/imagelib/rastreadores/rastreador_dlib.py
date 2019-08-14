import dlib

class RastreadorDlib:
	
	'''Rastreia objetos em um vídeo.'''

	def __init__(self):
		self.reiniciar()

	def reiniciar(self):
		'''Reinicia os rastreadores.'''
		self.trackers = []

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
		for caixa in caixas:
			rect = dlib.rectangle(*self._converte_para_caixa_dlib(caixa))
			tracker = dlib.correlation_tracker()
			tracker.start_track(frame, rect)
			self.trackers.append(tracker)

	def atualiza(self, frame):
		'''Atualiza os rastreadores.

		Parameters
		-----------
		frame : numpy.ndarray
			Novo frame do vídeo.

		Returns
		--------
		[(int, int, int, int), ...]
			Caixas com as novas posições dos rastreadores.
		'''
		caixas = []
		for tracker in self.trackers:
			caixa = self._atualiza_rastreador_individual(tracker, frame)
			caixas.append(caixa)
		return caixas
	

	def _atualiza_rastreador_individual(self, rastreador, frame):
		'''Atualiza o rastreador de um objeto específico.

		Parameters
		-----------
		rastreador : dlib.correlation_tracker
			O rastreador a ser atualizado.
		frame : numpy.ndarray
			Novo frame do vídeo.
		
		Returns
		---------
		(int, int, int, int)
			Caixa com as novas coordenadas do rastreador. Representa 
			as coordenadas x e y do topo esquerdo, a largura e a altura.
		'''
		rastreador.update(frame)
		pos = rastreador.get_position()
		x_comeco = int(pos.left())
		y_comeco = int(pos.top())
		w = int(pos.width())
		h = int(pos.height())
		return x_comeco, y_comeco, w, h
	
	def _converte_para_caixa_dlib(self, caixa):
		'''Converte a caixa do formato do projeto para o do Dlib.

		Parameters
		-----------
		caixa : (int, int, int, int)
			Caixa que representa as coordenadas x e y do topo esquerdo
			da caixa, a largura e a altura.
		
		Returns
		-----------
		(int, int, int, int)
			Caixa que representa as coordenadas x e y do topo direito
			e as coordenadas x e y do fundo direito.
		'''
		x_comeco, y_comeco, w, h = caixa
		return x_comeco, y_comeco, x_comeco+w, y_comeco+h
	
	def _converte_para_caixa_padrao(self, caixa):
		'''Converte a caixa do formato do Dlib para o do projeto.

		Parameters
		-----------
		caixa : (int, int, int, int)
			Caixa que representa as coordenadas x e y do topo direito
			e as coordenadas x e y do fundo direito.
		
		Returns
		-----------
		(int, int, int, int)
			Caixa que representa as coordenadas x e y do topo esquerdo
			da caixa, a largura e a altura.
		'''
		x_comeco, y_comeco, x_fim, y_fim = caixa
		return x_comeco, y_comeco, x_fim-x_comeco, y_fim-y_comeco