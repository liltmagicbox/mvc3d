import websocket
import time

#https://websocket-client.readthedocs.io/en/latest/examples.html#dispatching-multiple-websocketapps
#timeout whatever serverconnection fails, happend..maybe.

import threading

def once(msg='default message'):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.    
    ws.send(msg)    

def app_echo():
    print('runningforerver')
    def on_message(wsapp, message):
        wsapp.send('echo'+message)
        print(message)

    websocket.setdefaulttimeout(2)#if connection failed, next, without error.
    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    wsapp.run_forever()
    print('done')


#once()
#app_echo()







def sender(ws, msg='default message'):
    #ws = websocket.WebSocket()
    ws.send(msg)   

ws = websocket.WebSocket()
ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.    

th = threading.Thread( target =sender , args=[ws,'new th message'])
th.start()
th.join()
#time.sleep(1)


