import socket

from tnd import Loop, Future, coroutine

def fetch(callback=None):
    f = Future()
    if callback is not None:
        f.add_done_callback(lambda f: callback(f.result()))

    res = []
    def handler(fd_obj, events):
        if events & Loop.ERR:
            print 'handler has err [%s] ' % events
            Loop.current().remove_handler(fd_obj)
            fd_obj.close()
            f.set_result(''.join(res))
            return
        data = fd_obj.recv(1024)
        res.append(data)
        if not data:
            Loop.current().remove_handler(fd_obj)
            fd_obj.close()
            f.set_result(''.join(res))
            return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(('localhost', 6000))
    sock.setblocking(False)
    Loop.current().add_handler(sock, handler, Loop.READ)

    return f

@coroutine
def callback(name):
    result = yield fetch()
    print 'callback %s: %s' % (name, result)
    
Loop.current().add_callback(callback, 'A')
Loop.current().add_callback(callback, 'B')
Loop.current().add_callback(callback, 'C')

Loop.current().start()
