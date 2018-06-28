var ws = new WebSocket('ws://10.1.23.74:5555');

ws.onopen = function () {
	console.log('Websocket conectado ...')
	ws.send('1111')
}

ws.onmessage = function (ev) {
	try{
		decrypt = sjcl.decrypt("o3A2sdw74ApOIDsx45czz23",ev.data);
		payload = JSON.parse(decrypt);
		document.getElementById("data").innerHTML = payload.analiseFeitaEm;
		document.getElementById("duracao").innerHTML = payload.duracaoDaAnalise;
		document.getElementById("numerop").innerHTML = payload.numeroAproxPessoas;
		var stringBase64 = payload.imagemDaSala;
		var stringFinal = 'data:image/jpg;base64, '+stringBase64;
		document.getElementById("imagemSala").src = stringFinal;

	}
	catch(e){
		console.log("Arquivo invalido:");
		console.log(e.message);
	}
	ws.close();
}