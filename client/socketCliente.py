import socket
import json

j = json.load(open("config.json"))
host = j["address"]
port = j["port"]
quantReq = j["listenQ"]
bufferSize = j["bufferSize"]

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criando o socket
clientsocket.connect((host,port))
print "Enviando mensagem ao servidor"
clientsocket.sendall("me manda o json!")
print "Aguardando resposta do servidor"
payload_string = clientsocket.recv(bufferSize)
payload = payload_string.split("#",1) #Separando a string em 2 tamanho e json (o pedaco que veio)
tamanhoQueFalta =(int)(payload[0]) - len(payload[1]) #tamanho total dos pacotes que faltam
data = payload[1] #Data eh o json que vai ser preenchido no loop
print "Total:",(int)(payload[0])
print "recebido:",len(payload[1])

while tamanhoQueFalta>0:
	temp=clientsocket.recv(bufferSize)
	tamanhoQueFalta-=len(temp)
	print "recebido+:",len(temp)
	data+=temp
print "Finalizado com :",tamanhoQueFalta,"pacotes restantes"
clientsocket.close()
#Recebendo o JSON
json_string = data.decode("utf-8")#Convertendo payload em string utf-8
jsonObj = json.loads(json_string)#converte a string em um objeto JSON

with open("dadosRecebidos.json","w") as f:
	json.dump(jsonObj,f)

