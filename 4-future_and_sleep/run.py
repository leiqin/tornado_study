from tnd import Loop, Future

loop = Loop()

def future_after_2_seconds(name, loop):
    f = Future()
    loop.add_timeout_callback(2, lambda: f.set_result('I am %s' % name))
    print 'after 2 second has result'
    return f

def callback(f):
    print 'callback: %s' % f.result()

f = future_after_2_seconds('A', loop)
f.add_done_callback(callback)

def callback_sleep(f):
    print 'callback after sleep'

f = loop.sleep(3)
loop.add_future(f, callback_sleep)

loop.start()
