'''
Created on 31.07.2010

@author: Christian
'''

class ProviderManager(object):
    '''
    classdocs
    '''


    def __init__(self, path):
        '''
        Constructor
        '''
        self.basePath = path;
        self.providerModules = dict()
        self.providers = dict()
    
    
    def loadProvider(self, name):
        fully_qualified_name = self.basePath# + "." + "name";
        m = __import__(fully_qualified_name);
        self.providerModules[name] = m
        providerClass = getattr(module, name)
        providers = providerClass(self)
        
        