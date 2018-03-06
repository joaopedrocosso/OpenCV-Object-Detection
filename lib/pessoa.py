class Pessoa:
	tracks = []
	def __init__(self,i,x,y,framesMin,idadeMax):
		self.id = i #ID da pessoa
		self.x = x
		self.y = y
		self.tracks = [] #lista de pontos que a pessoa esteve
		self.idade = 0 #Idade que incrementa a cada frame (nao importando se apareceu ou nao)
		self.idadeMax = idadeMax #Idade ateh ser deletado
		self.framesMin = framesMin #numero de frames(em que a pessoa apareceu) para ser considerado
		self.vivo = True #se o idade passou ou nao o idadeMax
		self.confirmado = False #Se ele existiu por tempo o suficiente para ser considerado
		self.framesCount = 0 #Numero de frames em que a pessoa APARECEU
		
	def atualiza(self,x,y):
		self.idade = 0
		self.framesCount+=1 #Se passar do framesMin ele passa a ser considerado
		self.tracks.append([self.x,self.y])#Guardando as coordenadas antigas
		self.x = x 
		self.y = y 
		if self.framesCount > self.framesMin:
			self.confirmado = True #ele existe

	def getTracks(self):
		return self.tracks

	def envelhece(self):
		self.idade+=1
		if self.idade > self.idadeMax:
			self.vivo = False
	def isVivo(self):
		return self.vivo
	def isConfirmado(self):
		return self.confirmado
