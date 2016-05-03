import socket
import functools

from tnd import Loop

loop = Loop()

def get_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(('localhost', 6000))
    sock.setblocking(False)
    return sock

def handler(name, fd_obj, events):
    if events & Loop.ERR:
        print 'handler %s has err [%s] * * * \n' % (name, events)
        loop.remove_handler(fd_obj)
        fd_obj.close()
        return
    data = fd_obj.recv(1024)
    print 'handler %s recv "%s"' % (name, data)
    if not data:
        print 'handler %s recv end - - - \n' % name
        loop.remove_handler(fd_obj)
        fd_obj.close()
        return

loop.add_handler(get_sock(), functools.partial(handler, 'A'), Loop.READ)
loop.add_handler(get_sock(), functools.partial(handler, 'B'), Loop.READ)
loop.add_handler(get_sock(), functools.partial(handler, 'C'), Loop.READ)

loop.start()
