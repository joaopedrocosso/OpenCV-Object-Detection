class Pessoa:
	tracks = []
	def __init__(self,i,x,y,idadeMax):
		self.id = i #ID da pessoa
		self.x = x
		self.y = y
		self.tracks = []
		self.idade = 0
		self.idadeMax = idadeMax
	def atualiza(self,x,y):
		self.age = 0
		self.tracks.append([self.x,self.y])#Guardando as coordenadas antigas
		self.x = x 
		self.y = y 
	def getTracks(self):
		return self.tracks
