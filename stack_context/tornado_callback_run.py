import contextlib

from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from util import context_factory

def run():
    print 'run'

with StackContext(context_factory):
    IOLoop.current().add_callback(run)

print 'loop start - - -'

IOLoop.current().start()
