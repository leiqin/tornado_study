import contextlib

from tnd import StackContext, Loop, coroutine
from util import context_factory, another_context_factory

@coroutine
def runA():
    print 'runA start'
    with StackContext(context_factory):
        yield Loop.current().sleep(2)
    print 'runA end'

@coroutine
def runB():
    print 'runB start'
    with StackContext(another_context_factory):
        yield Loop.current().sleep(2)
    print 'runB end'

Loop.current().add_callback(runA)
#Loop.current().add_timeout_callback(1, runB)

print 'loop start - - -'

Loop.current().start()
