'''
Created on 31.07.2010

@author: Christian
'''

from app.config.configWrapper import ConfigWrapper

class ConfigSection(object):
    '''
    This wrapper provides easy access to a section in the configuration.
    '''

    def __init__(self, sectionName, aConfigWrapper):
        '''
        Will create the section if it does not yet exist.
        '''
        assert issubclass(aConfigWrapper.__class__, ConfigWrapper) or isinstance(aConfigWrapper, ConfigWrapper)
        self.configWrapper = aConfigWrapper
        self.sectionName = sectionName;
        self.configWrapper.addSection(self.sectionName)
        
    def set(self, option, value):
        return self.configWrapper.set(self.sectionName, option, value)
        
    def get(self, operation):
        return self.configWrapper.get(self.sectionName, operation)
    
    def setDefault(self, option, value):
        return self.configWrapper.setDefault(self.sectionName, option, value)
    