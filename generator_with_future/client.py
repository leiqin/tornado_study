from tnd import Loop, Future, coroutine

loop = Loop()

@coroutine
def after_2_seconds_then_dosomething(name, loop):
    print 'after 2 second has result'
    yield loop.sleep(2)
    print 'now do something'
    raise StopIteration('Hello, I am %s' % name)

def callback(f):
    print 'callback: %s' % f.result()

f = after_2_seconds_then_dosomething('A', loop)
loop.add_future(f, callback)

loop.start()
