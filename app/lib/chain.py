class Chain(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.callbacks = {}
        self.configurations = {}
        self.index = -1

    def fire(self, event):
        """
        Execute all the callbacks 
        in the current chain with their associcated
        configuration and the event 
        """
        for callback, config in zip(self.callbacks.itervalues(), self.configurations.itervalues()):
            self._fire(event, callback, config)

    def _fire(self, event, callback, config):
        """
        Stub method that is only used internally
        to fire an event.
        """
        return callback(event, config)


    def add(self, callback, config):
        '''
        Registers a callback at the end of a event
        listening chain.
        
        You can store a configuration along
        with your callback. This allows for using
        the same callback method for a more dynamic
        callback solution.
        '''
        key = object()
        self.callbacks[key] = callback
        self.configurations[key] = config
        return key

    def remove(self, key):
        del self.listeners[key]
