import logging
import os

log = logging.getLogger(__name__)

class Environment:
    _debugStatus = True;
    _log = None
    _basePath = ""
    _cfg = None
    _options = None
    _args = None
    _quiet = False
    _version = '0.3.0'
    _build = 19
    _frozen = False
    _defaultConfig = 'data/config.ini'
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

    @staticmethod
    def get(attr):# default = None, set_non_existant = False):
        return getattr(Environment, '_' + attr)
