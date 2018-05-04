const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:5556/');

ws.on('open', function open() {  
  console.log("test");
  ws.send("oi");
});

ws.on('message', function incoming(data) {
  console.log(data);
  ws.close();
});

