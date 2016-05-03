from tnd import Loop

loop = Loop()

def callback(name):
    print 'callback %s' % name

loop.add_callback(callback, 'A')
loop.add_callback(callback, 'B')

loop.start()
