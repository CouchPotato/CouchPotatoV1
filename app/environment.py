'''
Created on 31.07.2010

@author: Christian
'''
import logging
import os

class Environment:
    _debugStatus = True;
    log = None
    _basePath = ""
    cfg = None
    options = None
    args = None
    quiet = False
    version = '0.3.0'
    build = 19
    @staticmethod
    def doDebug():
        return Environment._debugStatus
    @staticmethod
    def setBasePath(base_path):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        Environment._basePath = base_path

    @staticmethod
    def getBasePath():
        return Environment._basePath

    @staticmethod
    def isQuiet():
        return Environment._quiet
options = _env.options
    args = cp_.args
    ca = cp_.cfg
