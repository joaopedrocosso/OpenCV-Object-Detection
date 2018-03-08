from threading import Thread
import json

class Operator(Thread):
	def __init__(self,socket,address,buff=1024):
		Thread.__init__(self)
		self.socket = socket
		self.buff = buff
		self.address = address

	def run(self):
		while(True):
			try:
				msg = self.socket.recv(self.buff)
				if not msg:break
				print "recebido:",msg
				mensagem = self.convertJSON()
				self.socket.sendall(mensagem)
			except:
				print "Conexao encerrada de forma inesperada"
				break
		self.socket.close() #Importante sempre fechar o socket ativo!
		print "Finalizada conexao com o cliente ",self.address

	def convertJSON(self):
		j = json.load(open("../dados.json"))
		jsonString = json.dumps(j) #converte o JSON em uma string
		return(jsonString)
