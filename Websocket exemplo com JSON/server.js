const WebSocket = require('ws');

var fs = require('fs');//Leitor de arquivos, usado no json

const wss = new WebSocket.Server({ port: 5555 });
const min=100;
const max=3000;
wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(message) {
    console.log('received: %s', message);

    var j = JSON.parse(fs.readFileSync('./data.json','utf8'));
    ws.send(JSON.stringify(j.chave1));
  });
});

