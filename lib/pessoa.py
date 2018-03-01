class Pessoa:
	tracks = []
	def __init__(self,i,x,y,framesMin,idadeMax):
		self.id = i #ID da pessoa
		self.x = x
		self.y = y
		self.tracks = []
		self.idade = 0
		self.idadeMax = idadeMax #Idade ate ser deletado
		self.framesMin = framesMin #numero de frames para ser considerado
		self.vivo = True
		self.confirmado = False #Se ele existiu por tempo o suficiente para ser considerado
		self.framesCount = 0
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

