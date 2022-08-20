window.addEventListener("DOMContentLoaded", () => {
  const messages = document.createElement("ul");
  document.body.appendChild(messages);

  const websocket = new WebSocket("ws://localhost:30020/");
  websocket.onmessage = ({ data }) => {
    const message = document.createElement("li");
    const content = document.createTextNode(data);
    message.appendChild(content);
    messages.appendChild(message);
  };

  websocket.onopen = (event) => {
    console.log('open',event)
  }

  websocket.onclose = (event) => {
    console.log('server disconnected',event)
  }
  websocket.onerror = (event) => {
    console.log('eeeeeed',event)
  }

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

//show_time.js:45 WebSocket is already in CLOSING or CLOSED state.





});
