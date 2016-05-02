import select

class Loop(object):

    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERR = select.EPOLLERR | select.EPOLLHUP

    def __init__(self):
        self._impl = select.epoll()
        self._handlers = {}

    def add_handler(self, fd, handler, events):
        fd, obj = self.split_fd(fd)
        self._handlers[fd] = (obj, handler)
        self._impl.register(fd, events | self.ERR)

    def remove_handler(self, fd):
        fd, obj = self.split_fd(fd)
        self._handlers.pop(fd, None)
        self._impl.unregister(fd)

    def split_fd(self, fd):
        try:
            # file like object
            return fd.fileno(), fd
        except AttributeError:
            # file descriptor
            return fd, fd

    def start(self):
        while True:
            # return [(fd, events), (fd, events)] timeout in second
            event_pairs = self._impl.poll(0.1)
            for fd, events in event_pairs:
                fd_obj, handler_func = self._handlers[fd]
                handler_func(fd_obj, events)

