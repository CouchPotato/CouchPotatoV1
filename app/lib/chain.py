class Chain(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.listeners = {}
        self.index = -1

    def fire(self, event):
        for key, entry in self.listeners.iteritems():
            self._fire(event, entry['callback'], entry['config'])

    def _fire(self, event, callback, config):
        return callback(event, config)


    def add(self, callback, config):
        '''returns the key for removal'''
        key = object()
        self.listeners[key] = {'callback' : callback, 'config' : config}
        return key

    def remove(self, key):
        del self.listeners[key]
