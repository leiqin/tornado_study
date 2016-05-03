
from tnd import StackContext
from util import context_factory

def run():
    print 'run'

with StackContext(context_factory):
    run()
