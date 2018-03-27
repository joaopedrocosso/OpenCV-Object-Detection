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
				print "recebido codigo:",msg
				mensagem = self.convertJsonToString(msg)
				string_tamanho =str(len(mensagem))+"#" #tamanho do arquivo
				print "enviando mensagem de tamanho:", string_tamanho
				payload = string_tamanho+mensagem
				self.socket.sendall(payload)
			except:
				print "Conexao encerrada de forma inesperada"
				break
		self.socket.close() #Importante sempre fechar o socket ativo!
		print "Finalizada conexao com o cliente ",self.address

	def convertJsonToString(self,payload):
		#Seleciona as informacoes pedidas do JSON e o transforma em string
		# 1-Quero 
		# 0-Nao quero
		#[[0]imagem][[1]numero de pessoas][[2]Tempo de analise]
		j = json.load(open("../dados.json"))
		if len(payload)>=3:
			if payload[0]=="0":
				del j["imagemDaSala"]
			if payload[1]=="0":
				del j["NumeroAproxPessoas"]
			if payload[2]=="0":
				del j["tempoDeAnalise"]
		jsonString = json.dumps(j) #converte o JSON em uma string
		return(jsonString)



