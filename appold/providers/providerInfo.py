'''
Created on 31.07.2010

@author: Christian
'''

class ProviderInfo(object):
    '''
    A basic object to pass information about
    a provider to the Application
    '''
    name = 'unknown'
    version = 'unknown'
    author = 'unknown'
    support = 'unknown'
    url = 'unknown'

    def __init__(self):
        '''
        Constructor
        '''
