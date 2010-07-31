'''
Created on 31.07.2010

@author: Christian
'''
import logging
import os


class CouchPotato:
    _debugStatus = True;
    log = None
    _basePath = ""
    cfg = None
    options = None
    args = None
    @staticmethod
    def doDebug():
        return CouchPotato._debugStatus
    @staticmethod
    def setBasePath(base_path):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        CouchPotato._basePath = base_path
        
    @staticmethod
    def getBasePath():
        return CouchPotato._basePath