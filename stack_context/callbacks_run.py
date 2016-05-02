import contextlib

from tnd import StackContext, Loop, wrap

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

def runA():
    print 'runA'
    with StackContext(another_context_factory):
        Loop.current().add_callback(runB)

def runB():
    print 'runB'

with StackContext(context_factory):
    Loop.current().add_callback(runA)

print 'loop start - - -'

Loop.current().start()
