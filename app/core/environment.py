import logging
import os

log = logging.getLogger(__name__)

class Environment:
    _debugStatus = True;
    _log = None
    _appDir = ""
    _dataDir = ""
    _options = None
    _args = None
    _quiet = False
    _version = '0.3.0'
    _build = 19
    _frozen = False

    cfg = None
    @staticmethod
    def doDebug():
        return Environment._debugStatus
    @staticmethod
    def setDataDir(data_dir):
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        Environment._dataDir = data_dir

    @staticmethod
    def get(attr):# default = None, set_non_existant = False):
        return getattr(Environment, '_' + attr)
