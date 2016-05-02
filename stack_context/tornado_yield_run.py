import contextlib

from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from tornado import gen

@contextlib.contextmanager
def context_factory():
    try:
        i = context_factory._i
    except AttributeError:
        context_factory._i = 0
    context_factory._i += 1
    i = context_factory._i
    try:
        print 'enter context factory %s' % i
        yield
    finally:
        print 'exit context factory %s' % i

@contextlib.contextmanager
def another_context_factory():
    try:
        i = another_context_factory._i
    except AttributeError:
        another_context_factory._i = 0
    another_context_factory._i += 1
    i = another_context_factory._i
    try:
        print 'enter another context factory %s' % i
        yield
    finally:
        print 'exit another context factory %s' % i

@gen.coroutine
def runA():
    print 'runA start'
    with StackContext(context_factory):
        yield gen.sleep(2)
    print 'runA end'

@gen.coroutine
def runB():
    print 'runB start'
    with StackContext(another_context_factory):
        yield gen.sleep(2)
    print 'runB end'

IOLoop.current().add_callback(runA)
IOLoop.current().call_later(1, runB)

print 'loop start - - -'

IOLoop.current().start()
