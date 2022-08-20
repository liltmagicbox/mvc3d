var WS = null

const messages = document.createElement("ul");
document.body.appendChild(messages);

function connect(){
  console.log('connect begin')
  WS = new WebSocket("ws://localhost:30020/")
  
  WS.onclose = (event) => {
    connect()
  }

  WS.onmessage = ({ data }) => {
    const message = document.createElement("li");
    const content = document.createTextNode(data);
    message.appendChild(content);
    messages.appendChild(message);
  }
  
  document.addEventListener('keydown', (event) => {
    const keyName = event.key;
    WS.send( JSON.stringify( {key:keyName, time:Date.now()} ) )
  }, false);

}



window.addEventListener('load', function(event){
  connect()
  }
)
