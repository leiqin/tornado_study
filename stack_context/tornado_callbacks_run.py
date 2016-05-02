import contextlib

from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from util import context_factory, another_context_factory

def runA():
    print 'runA start'
    with StackContext(another_context_factory):
        print 'runA with another'
        IOLoop.current().add_callback(runB)
    print 'runA end'

def runB():
    print 'runB'

with StackContext(context_factory):
    IOLoop.current().add_callback(runA)

print 'loop start - - -'

IOLoop.current().start()
