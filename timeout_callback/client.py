from tnd import Loop

loop = Loop()

def callback(name):
    print 'callback %s' % name

loop.add_callback(callback, 'A')
loop.add_callback(callback, 'B')
loop.add_timeout_callback(2, callback, 'C timeout 2')
loop.add_timeout_callback(3, callback, 'D timeout 3')

loop.start()
