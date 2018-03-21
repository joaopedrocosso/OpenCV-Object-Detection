import json
import base64

#Converte a string de image do JSON em uma imagem .jpg


#Recebendo e convertendo a imagem
j = json.load(open("dados.json"))
imagem = base64.b64decode(j["imagemDaSala"])
print "Tempo de analise:",j["tempoDeAnalise"],"segundos"
print "Numero de pessoas:",j["numeroAproxPessoas"]
#salvando
with open('imagem.jpg', 'wb') as f:
    f.write(imagem)