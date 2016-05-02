import contextlib

from tnd import StackContext, Loop, wrap
from util import context_factory

def run():
    print 'run'

with StackContext(context_factory):
    Loop.current().add_callback(run)

print 'loop start - - -'

Loop.current().start()
