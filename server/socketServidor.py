import socket
import json
from ServThread import Operator

j = json.load(open("config.json"))
host = j["address"]
port = j["port"]
quantReq = j["listenQ"]
bufferSize = j["bufferSize"]

print "Iniciando servidor em ",host,"-porta:",port
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Criando o socket
serversocket.bind((host, port)) #Ligando a um endereco
serversocket.listen(quantReq)  #Colocando o socket em modo passivo!!!
						#O parametro eh a quantidade maxima para a fila de requisicoes

#Loop principal do servidor
print "Servidor criado com sucesso"
while True:
    #Client socket eh o socket ativo que pode ser usado para as operacoes
    (clientsocket, address) = serversocket.accept()
    print "Conectado a ",address
    conec = Operator(clientsocket,address,bufferSize)
    conec.start()

    
