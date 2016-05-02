import select
import threading
import functools

class Loop(object):

    def __init__(self):
        self._impl = select.epoll()
        self._callbacks = []
        self._callbacks_lock = threading.Lock()

    def add_callback(self, callback, *args, **kwargs):
        with self._callbacks_lock:
            self._callbacks.append(functools.partial(callback, *args, **kwargs))

    def start(self):
        while True:
            event_pairs = self._impl.poll(0.1)
            with self._callbacks_lock:
                callbacks = self._callbacks
                self._callbacks = []

            for cb in callbacks:
                cb()
