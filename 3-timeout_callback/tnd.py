import select
import threading
import functools
import heapq
import time

@functools.total_ordering
class TimeoutCallback(object):

    def __init__(self, call_at, callback):
        self.call_at = call_at
        self.callback = callback

    def __lt__(self, other):
        return self.call_at < other.call_at

    def __eq__(self, other):
        return self.call_at == other.call_at

class Loop(object):

    def __init__(self):
        self._impl = select.epoll()
        self._callbacks = []
        self._callbacks_lock = threading.Lock()
        self._timeout_callbacks = []

    def add_callback(self, callback, *args, **kwargs):
        with self._callbacks_lock:
            self._callbacks.append(functools.partial(callback, *args, **kwargs))

    def add_timeout_callback(self, timeout, callback, *args, **kwargs):
        call_at = time.time() + timeout
        tc = TimeoutCallback(call_at, functools.partial(callback, *args, **kwargs))
        heapq.heappush(self._timeout_callbacks, tc)

    def start(self):
        while True:
            event_pairs = self._impl.poll(0.1)

            # callback
            with self._callbacks_lock:
                callbacks = self._callbacks
                self._callbacks = []
            for cb in callbacks:
                cb()

            # timeout callback
            now = time.time()
            timeout_callbacks = []
            while self._timeout_callbacks and self._timeout_callbacks[0].call_at <= now:
                tb = heapq.heappop(self._timeout_callbacks)
                timeout_callbacks.append(tb.callback)
            for cb in timeout_callbacks:
                cb()
