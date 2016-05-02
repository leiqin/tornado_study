from tnd import Loop, Future, coroutine

@coroutine
def after_2_seconds_then_dosomething(name):
    print 'after 2 second has result'
    yield Loop.current().sleep(2)
    print 'now do something'
    yield Loop.current().sleep(2)
    print 'now do another thing'
    raise StopIteration('Hello, I am %s' % name)

@coroutine
def callback(name):
    hello_str = yield after_2_seconds_then_dosomething(name)
    print 'callback: %s' % hello_str

Loop.current().add_callback(callback, 'A')

Loop.current().start()
