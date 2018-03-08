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
data = clientsocket.recv(bufferSize)
clientsocket.close()
#Recebendo o JSON
json_string = data.decode("utf-8")#Convertendo payload em string utf-8
jsonObj = json.loads(json_string)#converte a string em um objeto JSON

with open("dadosRecebidos.json","w") as f:
	json.dump(jsonObj,f)

