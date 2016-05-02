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

def run():
    print 'run'

with StackContext(context_factory):
    Loop.current().add_callback(run)

print 'loop start - - -'

Loop.current().start()
