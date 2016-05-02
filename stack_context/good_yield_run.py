import contextlib
import functools

from tnd import StackContext, Loop, coroutine, run_with_stack_context
from util import context_factory, another_context_factory

@coroutine
def runA():
    print 'runA start'
    yield run_with_stack_context(StackContext(context_factory), 
            functools.partial(Loop.current().sleep, 2))
    print 'runA end'

@coroutine
def runB():
    print 'runB start'
    yield run_with_stack_context(StackContext(another_context_factory), 
            functools.partial(Loop.current().sleep, 2))
    print 'runB end'

Loop.current().add_callback(runA)
#Loop.current().add_timeout_callback(1, runB)

print 'loop start - - -'

Loop.current().start()
