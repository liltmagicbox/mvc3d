import asyncio
import websockets

async def hello(websocket, path):
    print(websocket,path)
    print('hu')
    while True:
        try:
            name = await websocket.recv()
            print(f"< {name}")
        except websockets.ConnectionClosed:
            print(f"Terminated")
            break
    print('ha=closed')


def main():
    start_server = websockets.serve(hello, 'localhost', 30020)
    asyncio.get_event_loop().run_until_complete(start_server)    
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()