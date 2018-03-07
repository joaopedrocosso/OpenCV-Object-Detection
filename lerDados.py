import json
import base64

#Recebendo e convertendo a imagem
j = json.load(open("dados.json"))
imagem = base64.b64decode(j["imagemDaSala"])
#salvando
with open('imagem.jpg', 'wb') as f:
    f.write(imagem)