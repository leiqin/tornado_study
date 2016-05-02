import contextlib
import functools

from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext, run_with_stack_context
from tornado import gen
from util import context_factory, another_context_factory

@gen.coroutine
def runA():
    print 'runA start'
    yield run_with_stack_context(StackContext(context_factory), 
            functools.partial(gen.sleep, 2))
    print 'runA end'

@gen.coroutine
def runB():
    print 'runB start'
    yield run_with_stack_context(StackContext(another_context_factory), 
            functools.partial(gen.sleep, 2))
    print 'runB end'

IOLoop.current().add_callback(runA)
#IOLoop.current().call_later(1, runB)

print 'loop start - - -'

IOLoop.current().start()
