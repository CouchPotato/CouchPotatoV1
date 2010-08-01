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

    def fire(self, event, data):
        for entry in self:
            self._fire(event, entry['callback'], entry['config'])

    def _fire(self, event, data, callback, config):
        callback(event, data, config)


    def __iter__(self):
        index = -1
        return self

    def next(self):
        if self.index >= self.listeners.__len__():
            raise StopIteration
        self.index += 1
        return self.listeners[self.index]


    def add(self, callback, config):
        '''returns the key for removal'''
        key = object()
        self.listeners.add(key, {'callback' : callback, 'config' : config})
        return key

    def remove(self, key):
        del self.listeners[key]
