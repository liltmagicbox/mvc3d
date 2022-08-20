window.addEventListener("DOMContentLoaded", () => {
  const messages = document.createElement("ul");
  document.body.appendChild(messages);

  const websocket = new WebSocket("ws://liltbox.iptime.org:30020/");
  websocket.onmessage = ({ data }) => {
    const message = document.createElement("li");
    const content = document.createTextNode(data);
    message.appendChild(content);
    messages.appendChild(message);
  };

  function ham(){
    websocket.send(JSON.stringify( {action:'minus'} ) )
  }
  var button = document.getElementById('bb')
  button.addEventListener('click', ham)


  document.addEventListener('keydown', (event) => {
    const keyName = event.key;

    // if (keyName === 'Control') {
    //   // do not alert when only Control key is pressed.
    //   return;
    // }

    // if (event.ctrlKey) {
    //   // Even though event.key is not 'Control' (e.g., 'a' is pressed),
    //   // event.ctrlKey may be true if Ctrl key is pressed at the same time.
    //   alert(`Combination of ctrlKey + ${keyName}`);
    // }
    // else {
    //   alert(`Key pressed ${keyName}`);
    // }
    websocket.send( JSON.stringify( {key:keyName, time:Date.now()} ) )
  }, false);





});
