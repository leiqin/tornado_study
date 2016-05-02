import select
import threading
import functools
import heapq
import time
import types
import sys

class Stack(threading.local):
    def __init__(self):
        self.contexts = (tuple(), None)
_state = Stack()

class StackContext(object):

    def __init__(self, context_factory):
        self.context_factory = context_factory
        self.contexts = []

    def enter(self):
        context = self.context_factory()
        self.contexts.append(context)
        context.__enter__()

    def exit(self, exc_type, exc_value, traceback):
        context = self.contexts.pop()
        context.__exit__(exc_type, exc_value, traceback)

    def __enter__(self):
        print 'enter stack context'
        self.old_contexts = _state.contexts
        self.new_contexts = (self.old_contexts[0] + (self,), self)
        _state.contexts = self.new_contexts
        try:
            self.enter()
        except:
            _state.contexts = self.old_contexts
            raise

    def __exit__(self, type, value, traceback):
        # return True to suppress the exception (prevent it from being propagated)
        print 'exit stack context'
        try:
            self.exit(type, value, traceback)
        finally:
            final_contexts = _state.contexts
            _state.contexts = self.old_contexts

            # Generator coroutines and with-statements with non-local
            # effects interact badly.  Check here for signs of
            # the stack getting out of sync.
            # Note that this check comes after restoring _state.context
            # so that if it fails things are left in a (relatively)
            # consistent state.
            print '* * * stack context inconsistency StackContext.__exit__ * * *'
            if final_contexts is not self.new_contexts:
                raise Exception(
                    'stack_context inconsistency (may be caused by yield '
                    'within a "with StackContext" block)')
            self.new_contexts = None

def wrap(func):
    if func is None or hasattr(func, '_wraped'):
        return func

    call_contexts = _state.contexts
    @functools.wraps(func)
    def wapper(*args, **kwargs):
        cur_contexts = _state.contexts
        try:
            _state.contexts = call_contexts

            contexts = call_contexts[0]
            for c in contexts:
                c.enter()

            exc = (None, None, None)
            try:
                func(*args, **kwargs)
            except:
                exc = sys.exc_info()

            last_i = len(contexts) - 1
            while last_i >= 0:
                c = contexts[last_i]
                c.exit(*exc)
                last_i -= 1
        finally:
            _state.contexts = cur_contexts
    
    wapper._wraped = True
    return wapper

        
def coroutine(func):
    @functools.wraps(func)
    def wapper(*args, **kwargs):
        f = Future()
        res = func(*args, **kwargs)
        if isinstance(res, types.GeneratorType):
            try:
                orig_stack_contexts = _state.contexts
                first_value = res.send(None)
                if orig_stack_contexts is not _state.contexts:
                    print '* * * stack context inconsistency coroutine.wapper * * *'
                    # not handle exception
                    raise Exception(
                                'stack_context inconsistency (probably caused '
                                'by yield within a "with StackContext" block)')
                _handle_generator(f, res, first_value)
            except StopIteration as e:
                f.set_result(e.message)
        else:
            f.set_result(res)
        return f
    return wapper

def _handle_generator(future, gen, last_value):
    if not isinstance(last_value, Future):
        raise Exception('generate value is not Future')
    def callback(gen_fu):
        try:
            orig_stack_contexts = _state.contexts
            next_value = gen.send(gen_fu.result())
            if orig_stack_contexts is not _state.contexts:
                print '* * * stack context inconsistency _handle_generator * * *'
                # not handle exception
                raise Exception(
                            'stack_context inconsistency (probably caused '
                            'by yield within a "with StackContext" block)')
            _handle_generator(future, gen, next_value)
        except StopIteration as e:
            future.set_result(e.message)
    last_value.add_done_callback(callback)

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

    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERR = select.EPOLLERR | select.EPOLLHUP

    _current = threading.local()

    def __init__(self):
        self._impl = select.epoll()
        self._handlers = {}
        self._callbacks = []
        self._callbacks_lock = threading.Lock()
        self._timeout_callbacks = []

    @staticmethod
    def current():
        try:
            return Loop._current.instance
        except AttributeError:
            Loop._current.instance = Loop()
            return Loop._current.instance

    def sleep(self, second):
        f = Future()
        self.add_timeout_callback(second, lambda: f.set_result(None))
        return f

    def add_handler(self, fd, handler, events):
        fd, obj = self.split_fd(fd)
        self._handlers[fd] = (obj, wrap(handler))
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

    def add_callback(self, callback, *args, **kwargs):
        with self._callbacks_lock:
            self._callbacks.append(functools.partial(wrap(callback), *args, **kwargs))

    def add_timeout_callback(self, timeout, callback, *args, **kwargs):
        call_at = time.time() + timeout
        tc = TimeoutCallback(call_at, functools.partial(wrap(callback), *args, **kwargs))
        heapq.heappush(self._timeout_callbacks, tc)

    def _run_callback(self, cb):
        cb()


    def add_future(self, future, callback):
        future.add_done_callback(lambda f: self.add_callback(wrap(callback), f))

    def start(self):
        while True:
            # return [(fd, events), (fd, events)] timeout in second
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

            # handler
            for fd, events in event_pairs:
                fd_obj, handler_func = self._handlers[fd]
                handler_func(fd_obj, events)

