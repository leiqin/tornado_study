import socket
import contextlib
import random
import thread
import time

def sendslow(conn, addr):
    print 'sendslow start', addr
    with contextlib.closing(conn):
        time.sleep(random.random())
        conn.sendall('I ')
        time.sleep(random.random())
        conn.sendall('am ')
        time.sleep(random.random())
        conn.sendall('a ')
        time.sleep(random.random())
        conn.sendall('slow ')
        time.sleep(random.random())
        conn.sendall('server ')
    print 'sendslow end', addr


def main():
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 6000               # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print 'Connected by', addr
        thread.start_new_thread(sendslow, (conn, addr))

if __name__ == '__main__':
    main()
