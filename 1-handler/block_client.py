import socket
import contextlib

def get_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(('localhost', 6000))
    return sock

def handler(name, sock):
    with contextlib.closing(sock):
        while True:
            data = sock.recv(1024)
            print 'handler %s recv [%s]' % (name, data)
            if not data:
                print 'handler %s recv end - - - \n' % name
                break

handler('A', get_sock())
handler('B', get_sock())
