'''
Created on 31.07.2010

@author: Christian
'''

from app.lib.providers.providerInfo import ProviderInfo
from app.config.configSection import ConfigSection

class BasicProvider():
    providerInfo = ProviderInfo()
    type = 'movie'
    
    def __init__(self):
        self._className = self.__class__.__name__
        self.config = ConfigSection(self._className)
        self.initConfigSettings()
        self.initProviderInfo()
        pass
    
            
    def initConfigSettings(self):
        raise NotImplemented()
    
    def initProviderInfo(self):
        c = self.config
        pi = self.providerInfo
        pi.author   = c.get('author')
        pi.name     = c.get('name')
        pi.support  = c.get('support')
        pi.url      = c.get('url')
        pi.version  = c.get('version')