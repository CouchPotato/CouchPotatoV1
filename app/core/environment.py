import logging
import os
import sys

log = logging.getLogger(__name__)

class Environment:
    _debug = True;
    _log = None
    _appDir = ""
    _dataDir = ""
    _options = None
    _args = None
    _quiet = False
    _version = '0.3.0'
    _build = 19
    _frozen = False
    _pluginMgr = None
    _baseUrl = 'http://localhost:8080'

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

    @staticmethod
    def detectExeBuild():
        try:
            Environment.frozen = sys.frozen
        except AttributeError:
            Environment.frozen = False

    @staticmethod
    def detectAppDir():
        appdir = os.path.realpath(os.path.dirname(sys.argv[0]))
        if Environment.get('frozen'):
            #path_base = os.environ['_MEIPASS2']
            appdir = os.path.dirname(sys.executable)
        Environment._appDir = appdir
    @staticmethod
    def registerPaths():
        sys.path.insert(0, Environment.get('appDir'))
        sys.path.insert(0, os.path.join(Environment.get('appDir'), 'library'))
        sys.path.insert(0, os.path.join(Environment.get('appDir'), 'app', 'lib'))

Environment.detectExeBuild()
Environment.detectAppDir()
Environment.registerPaths()

