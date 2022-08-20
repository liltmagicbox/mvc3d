import websocket
import time

#https://websocket-client.readthedocs.io/en/latest/examples.html#dispatching-multiple-websocketapps
#timeout whatever serverconnection fails, happend..maybe.

def once():
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.
    ws.send("Hello, Server")
#print(ws.recv())
#ws.close()



def app_listen():
    def on_message(wsapp, message):
        print(message)

    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    wsapp.run_forever()

def app_echo():
    print('runningforerver')
    def on_message(wsapp, message):
        wsapp.send('echo'+message)
        print(message)

    websocket.setdefaulttimeout(2)#if connection failed, next, without error.
    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    wsapp.run_forever()
    print('done')

def main():
    once()
    #time.sleep(5)#this really keeps socket connected
    #app_echo()    

if __name__ == '__main__':
    main()