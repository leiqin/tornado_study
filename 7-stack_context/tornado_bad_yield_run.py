import contextlib

from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from tornado import gen
from util import context_factory, another_context_factory

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
#IOLoop.current().call_later(1, runB)

print 'loop start - - -'

IOLoop.current().start()
