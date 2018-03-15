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
				mensagem = self.convertJsonToString()
				string_tamanho =str(len(mensagem))+"#" #tamanho do arquivo
				print "enviando mensagem de tamanho:", string_tamanho
				payload = string_tamanho+mensagem
				self.socket.sendall(payload)
			except:
				print "Conexao encerrada de forma inesperada"
				break
		self.socket.close() #Importante sempre fechar o socket ativo!
		print "Finalizada conexao com o cliente ",self.address

	def convertJsonToString(self):
		j = json.load(open("../dados.json"))
		jsonString = json.dumps(j) #converte o JSON em uma string
		return(jsonString)
