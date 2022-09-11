import threading
import socket
import json
from queue import Queue
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 30020
PORT2 = 30021

#========
"""
PORT is used : Sender -> QueueRecv
PORT2 is used by : QueueRecvClient <- Caster

sends json-parse-able data.
send may bnot blocked, while th reconnects..

#server socket is. occupies port, let it be longlife.
#server gets conn, connection of client, we can conn.recv kinds.

#client socket, better create newone, if new connection. seems better to not re-use or re-connect

when disconnected target, Errs, Reset Abort(more critical?)
#b'' is sent when socket connection is ended. filesend EOB?EOF

#server no limit. conn is just got, while client just connected and sends whatever it likes.
conn.close() like not that working, maybe.

"""


def send_dumps(sock, data, verbose=False):
    try:
        strdata = json.dumps(data)
        sock.sendall( strdata.encode() )
        print('sent',strdata) if verbose else 1
        return True
    except ConnectionResetError:
        print('send target disconnected:',sock.getsockname()) if verbose else 1
        return False
    except ConnectionAbortedError:
        print('server aborted :', sock.getsockname()) if verbose else 1
        return False
        #abortion is critical.. maybe banned. ..or not.

def recv_loads(sock, verbose = False):
    try:
        data = sock.recv(2**13)#12=4096
        assert(bool(data))#if not data:#also server disconnected. b''is no response.
        strdata = data.decode()
        parsed_data = json.loads(strdata)
        return parsed_data

    except AssertionError:
        print('recved empty.. seems disconn..') if verbose else 1
        return None
    except ConnectionResetError:
        print('recv target disconnected..') if verbose else 1        
        return None
    except json.decoder.JSONDecodeError:#print(strdata,'what')#["hello"]["hello"]
        print('json decode fail') if verbose else 1
        return {}
        #raise TypeError


def get_client(host, port, verbose):
    """client shall be replaced new connection.
    blocking until get connected"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect( (host,port) )
            break
        except ConnectionRefusedError:
            print('reconnecting..',port) if verbose else 1
            continue
    print('connected!',client_socket.getsockname() ) if verbose else 1
    return client_socket

def get_server(host, port, verbose):
    """blocking until get connected"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            server_socket.bind( (host,port) )#OSError: [WinError 10048]
            break
        except OSError as err:
            print(err) if verbose else 1
            if '10048' in str(err):
                raise Exception('PORT occupied already')
            break
    server_socket.listen()#0 is log. not max..
    return server_socket


def get_conn(server_socket, verbose):
    print('accepting..', server_socket.getsockname()) if verbose else 1
    conn, addr = server_socket.accept()
    print('client connected', addr) if verbose else 1
    return conn

def valid(sock, verbose):
    try:
        data = sock.recv(1024)
    #except ConnectionResetError:
    except:
        return False
    if 'id' in data.decode():        
        return True    
    return False




#======= this reconnects even server's state. if disconnected, recvs data=''.if fail connection,CRE.
#whatever, queue will get what's came from. recv halts, cpu power safe.

def server_recv_forever(host,port, valid_function=None, put_function=None, verbose=False):    
    if valid_function == None:
        valid_function = lambda sock,verbose:True
    if put_function == None:
        put_function = lambda data:print('put',data)

    server_socket = get_server(host,port,verbose)
    #pool_sema = threading.BoundedSemaphore(value=2)
    #pool_sema.acquire()        
    #pool_sema.release()
    
    def sock_to_queue(sock):
        while True:
            data = recv_loads(sock,verbose)
            if data == None:#connection error
                break
            put_function(data)
    
    while True:
        sock = get_conn(server_socket, verbose)#halt here

        valid = valid_function(sock, verbose)
        if valid:
            print(' VALID', sock.getpeername()) if verbose else 1
        else:
            print(' NOT valid', sock.getpeername()) if verbose else 1
            continue
        #seems this is garbage collected. 1s lieftime,,
        th = threading.Thread( target = sock_to_queue, args=[sock] )
        th.start()

#==================
def _test_server_without_class():
    th = threading.Thread( target = server_recv_forever, args=[HOST,PORT])
    th.start()
    
    print('main thread sleep')
    time.sleep(40)

#_test_server_without_class()





class QueueRecv:
    """open server socket, run thread, if new conn, put to queue."""
    def __init__(self, host=HOST, port=PORT, verbose=False):
        queue = Queue()
        def put_function(data):
            queue.put(data)
        #th = threading.Thread( target = server_recv_forever, args=[host,port, put_function, verbose])
        kwargs={'host':host,'port':port, 'put_function':put_function, 'verbose':verbose}
        th = threading.Thread( target = server_recv_forever, kwargs = kwargs)
        th.start()
        self.queue = queue

    def get_all(self):
        queue = self.queue
        while not queue.empty():
            yield queue.get()

#==================
def _qstest():
    q = QueueRecv(verbose = True)

    while True:
        for i in q.get_all():
            print(i)
        time.sleep(2)



#_qstest()



















#======================== client version




#===========client sender
class Sender:
    """threaded sender. reconnects, not blocking."""
    def __init__(self, host=HOST,port=PORT,verbose=False, reconnect=True):
        self._data = (host, port, verbose)
        self.sock = get_client(host,port,verbose)
        self.reconnect = reconnect

    def send(self, data):
        (host, port, verbose) = self._data
        if not send_dumps(self.sock,data,verbose):#connection failure
            if self.reconnect:
                #way1:blocking
                #self.sock = get_client(host,port,verbose)
                
                #way2:nonblocking                
                
                #2-1 this will change internal (temp) var, sock.
                #def newclient(sock):
                #    sock = get_client(host,port,verbose)                
                #2-2 this exactly changes the self.sock -> [?]
                def newclient():
                    self.sock = get_client(host,port,verbose)#here sock re-assigned! pointer.
                th = threading.Thread( target = newclient)
                th.start()


#class QueueSendClient: this queue.put() ..but since recv is always opened, queue delay happens.
#just use Sender, which is non-blocking. no need queue.

#Sender -> QueueRecv
#QueueRecvClient <- Caster
#... is Caster just Sender??
#Sender assumes target is. , even tmp. not accessable.
#however, Caster , If client disconnected, fine.
#...seems QueueRecv can be QueueSend..like. not queue however.

class Caster:
    """sends to all data! not reconnects. viewer may tell me!"""
    def __init__(self, host=HOST,port=PORT2, verbose=False):
        self.verbose = verbose        
        self.receivers = []
        self.server_socket = get_server(host,port,verbose)
        
        def recruit_forever():#maybe it will copy..if not arged?
            while True:
                sock = get_conn(self.server_socket, verbose)#halt here
                #if not valid(sock, verbose):
                #    continue
                self.receivers.append(sock)
        th = threading.Thread( target = recruit_forever)#about args, func not re-assignes,fine.
        th.start()

    def cast(self, data):
        """for send. requires thread?"""
        socks = self.receivers.copy()
        for sock in socks:#maybe thread safe iteration.
            success = send_dumps(sock, data, self.verbose)
            if not success:
                self.receivers.remove(sock)
                print('sock removed:',sock.getpeername())if self.verbose else 1


# class Receiver(QueueClient):
#     """gets bcasted data, via sim's hz."""
#     def __init__(self, host=HOST,port=PORT,verbose=False):
#         self.queue = QueueClient(host,port,verbose)
#...was the QueueRecvClient
#XXXXX below you not wanna use this.. QueueRecv and Sender is fine XXXXX.
#NO! it's for client. we need it.
def client_recv_forever(host,port, put_function=None, verbose=False):
    if put_function == None:
        put_function = lambda x:print('put',data)
    
    while True:
        sock = get_client(host,port, verbose)
        while True:
            data = recv_loads(sock, verbose)
            if data == None:
                break
            put_function(data)

#============
def _test_clinet_without_class():
    th = threading.Thread( target = client_recv_forever, args=[HOST,PORT])
    th.start()
    print('main thread sleep')
    time.sleep(40)

#_test_clinet_without_class()



#=================================
class QueueRecvClient:
    """open client socket, like QueueServer. """
    def __init__(self, host=HOST, port=PORT2, verbose=False):
        queue = Queue()
        def put_function(data):
            queue.put(data)

        #cs = ClientSocket(host,port,verbose)

        th = threading.Thread( target = client_recv_forever, args=[host,port, put_function, verbose])
        th.start()
        self.queue = queue

    def get_all(self):
        queue = self.queue
        while not queue.empty():
            yield queue.get()

#==================
def _qctest():
    q = QueueRecvClient(verbose = True)

    while True:
        for i in q.get_all():
            print(i)
        time.sleep(2)

#_qstest()

















def main():
    1
    #server_recv_forever(HOST,PORT, verbose = True)
    #_qstest()
    
    # c = Caster(verbose = True)
    # while True:
    #     c.cast(time.time())
    #     time.sleep(1)
if __name__ == '__main__':
    main()



















#===========================
#for history.


#portdog = Portdog(host,port, queue)#whatever connected, gets and puts to queue.

#finally!
#portqueue = PortQueue(host,port)
#portqueue.get_all()


# class PortQueue:
#     def __init__(self, host=HOST, port=PORT):
#         queue = Queue()
#         self.queue = queue
#         def putter(data):
#             queue.put(data)
        
#         thread_run(putter, host,port)
    
#     def get_all(self):
#         queue = self.queue
#         while not queue.empty():
#             yield queue.get()

# def pqtest():
#     a = PortQueue()
#     while True:
#         for i in a.get_all():
#             print(i)
#         time.sleep(1)


# 'accept'
#  'bind'
#  'close'
#  'connect'
#  'connect_ex'
#  'detach'
#  'dup'
#  'family'
#  'fileno'
#  'get_inheritable'
#  'getblocking'
#  'getpeername'
#  'getsockname'
#  'getsockopt'
#  'gettimeout'
#  'ioctl'
#  'listen'
#  'makefile'
#  'proto'
#  'recv'
#  'recv_into'
#  'recvfrom'
#  'recvfrom_into'
#  'send'
#  'sendall'
#  'sendfile'
#  'sendto'
#  'set_inheritable'
#  'setblocking'
#  'setsockopt'
#  'settimeout'
#  'share'
#  'shutdown'
#  'timeout'
#  'type'






#WE DON't UDP~! ha!
#https://stackoverflow.com/questions/47903/udp-vs-tcp-how-much-faster-is-it
# host,port = HOST,PORT
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# server_socket.bind( (host,port) )
# data,addr = server_socket.recvfrom(2**12)
# print(data,addr)


#we cant limit sock connections.
    #lets kick out, if not valid! or just let them send but never accept..
    #or first handshake protocol.. .. better kick out. guys, this time's pw is xxxx..
    #viewr sends input, with their host,port. sim creates Sender, sending draw to thm.
    #..or draw server. another one.
    #lets assume, port 20 is input. only input.
    #while port 21 is output, anyone who connects, will get the data, via sim rate.
    #..why didn't i? lets bcast, via port21, send only server.
    #no limit accept, we can even watch multi world, in same view!


#recv {1:1}{2:2} json parse err, we can }{.replace(),,but not do that much!



#print(addr)#('192.168.0.47', 3471)
#laddr=('192.168.0.47', 30020), raddr=('192.168.0.47', 2967)>









#==========bad design. assign happens unpredictable.
#===see client_recv_forever how it became clear.
#sock = get_client(host,port, verbose)
# while True:
#     try:
#         data = sock.recv(2**13)#12=4096
#     except ConnectionResetError:
#         print('server disconnected..') if verbose else 1
#         sock = get_client(host,port,verbose)
#         continue
#     if not data:#also server disconnected. b'' will no response. lets assume disconnected.
#         print('recved empty.. seemd disconn..') if verbose else 1
#         sock = get_client(host,port,verbose)
#         continue
#     strdata = data.decode()
#     #print(strdata,'what')#["hello"]["hello"]
#     try:
#         parsed_data = json.loads(strdata)
#     except json.decoder.JSONDecodeError:
#         print('seems the loop is too fast, and server resetted.') if verbose else 1
#         #raise TypeError
#         continue











#seems bad and data byte+btyte problem.
# class ServerSocket:
#     def __init__(self, host,port, verbose=False):
#         self.host = host
#         self.port = port
#         self.verbose = verbose
#         self.server = get_server(self.host,self.port,self.verbose)
#     def recv_loads(self):
#         sock = self.server
#         host = self.host
#         port = self.port
#         verbose = self.verbose

#         while True:        
#             try:
#                 data = sock.recv(2**13)
#             except ConnectionResetError:
#                 print('a client disconnected') if verbose else 1
#                 #sock = #we just finish here.. break ..no!
#                 sock = get_server(host,port,verbose)

#             if not data:#connection end
#                 print('a client connection end') if verbose else 1
#                 sock = get_server(host,port,verbose)
            
#             strdata = data.decode()        
#             try:
#                 parsed_data = json.loads(strdata)                
#             except json.decoder.JSONDecodeError:
#                 print('json decode failed:',data) if verbose else 1
#                 pass
#             break
        
#         self.server = sock
#         return parsed_data

# s = ServerSocket(HOST,PORT,True)
# while True:
#     data = s.recv_loads()
#     print(data)
#     time.sleep(2)




# class ClientSocket:
#     def __init__(self, host,port, verbose=False):
#         self.host = host
#         self.port = port
#         self.verbose = verbose
#         self.client = get_client(self.host,self.port,self.verbose)
#     def recv_loads(self):
#         sock = self.client
#         host = self.host
#         port = self.port
#         verbose = self.verbose

#         while True:
#             try:
#                 data = sock.recv(2**13)#12=4096
#             except ConnectionResetError:
#                 print('server disconnected..') if verbose else 1
#                 sock = get_client(host,port,verbose)
#                 continue
#             if not data:#also server disconnected. b'' will no response. lets assume disconnected.
#                 print('recved empty.. seemd disconn..') if verbose else 1
#                 sock = get_client(host,port,verbose)
#                 continue
#             strdata = data.decode()
#             #print(strdata,'what')#["hello"]["hello"]
#             try:
#                 parsed_data = json.loads(strdata)
#             except json.decoder.JSONDecodeError:
#                 print('seems the loop is too fast, and server resetted.') if verbose else 1
#                 #raise TypeError
#                 continue
#             break

#         self.client = sock
#         return parsed_data