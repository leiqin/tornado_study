import select
import threading
import functools
import heapq
import time

class Future(object):

    def __init__(self):
        self._callbacks = []
        self._result = None
        self._done = False

    def done(self):
        return self._done

    def add_done_callback(self, callback):
        if self._done:
            callback(self)
        else:
            self._callbacks.append(callback)

    def set_result(self, result):
        self._result = result
        self._done = True
        for cb in self._callbacks:
            cb(self)

    def result(self):
        if self._done: 
            return self._result
        else:
            raise Exception("Future is not done")

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

    def sleep(self, second):
        f = Future()
        self.add_timeout_callback(second, lambda: f.set_result(None))
        return f

    def add_callback(self, callback, *args, **kwargs):
        with self._callbacks_lock:
            self._callbacks.append(functools.partial(callback, *args, **kwargs))

    def add_timeout_callback(self, timeout, callback, *args, **kwargs):
        call_at = time.time() + timeout
        tc = TimeoutCallback(call_at, functools.partial(callback, *args, **kwargs))
        heapq.heappush(self._timeout_callbacks, tc)

    def _run_callback(self, cb):
        cb()

    def add_future(self, future, callback):
        future.add_done_callback(callback)

    def start(self):
        while True:
            event_pairs = self._impl.poll(0.1)

            # callback
            with self._callbacks_lock:
                callbacks = self._callbacks
                self._callbacks = []
            for cb in callbacks:
                self._run_callback(cb)

            # timeout callback
            now = time.time()
            timeout_callbacks = []
            while self._timeout_callbacks and self._timeout_callbacks[0].call_at <= now:
                tb = heapq.heappop(self._timeout_callbacks)
                timeout_callbacks.append(tb.callback)
            for cb in timeout_callbacks:
                self._run_callback(cb)
