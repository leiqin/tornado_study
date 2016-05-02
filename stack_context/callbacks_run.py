import contextlib

from tnd import StackContext, Loop, wrap
from util import context_factory, another_context_factory

def runA():
    print 'runA start'
    with StackContext(another_context_factory):
        print 'runA with another'
        Loop.current().add_callback(runB)
    print 'runA end'


def runB():
    print 'runB'

with StackContext(context_factory):
    Loop.current().add_callback(runA)

print 'loop start - - -'

Loop.current().start()
