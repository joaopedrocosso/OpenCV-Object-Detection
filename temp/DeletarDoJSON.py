import json

with open("dados.json") as j:
	data = json.load(j)
	del data["imagemDaSala"]
with open("novosDados.json","w") as f:
	json.dump(data,f)


