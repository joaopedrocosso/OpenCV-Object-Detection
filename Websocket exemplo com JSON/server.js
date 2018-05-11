const WebSocket = require('ws');
var fs = require('fs');//Leitor de arquivos, usado no json

var serverAdd = "10.1.23.66";
const wss = new WebSocket.Server({ port: 5555,host:serverAdd});
console.log("Host at: "+serverAdd);
const min=100;
const max=3000;
wss.on('connection', function connection(ws,req) {
  const ip = req.connection.remoteAddress;
  console.log("Conected to: "+ip);
  ws.on('message', function incoming(message) {
    console.log('received: %s', message);
    var j = JSON.parse(fs.readFileSync('./dados.json','utf8'));
    ws.send(JSON.stringify(j));
    ws.close();
  });
});

