from .environment import Environment as env_
from optparse import OptionParser
import sys, os
from app.config.main import Main as Config
from ConfigParser import ConfigParser
import logging
from logging.config import _create_formatters, _install_handlers, \
    _install_loggers

class Bootstrapper(object):
    '''
    classdocs
    '''
    DEFAULT_DATA_DIR = 'data'


    def __init__(self):
        '''
        Constructor
        '''
        self.detectExeBuild()
        self.detectAppDir()
        # Include paths
        sys.path.insert(0, env_.get('appDir'))
        sys.path.insert(0, os.path.join(env_.get('appDir'), 'library'))
        sys.path.insert(0, os.path.join(env_.get('appDir'), 'app', 'lib'))
        sys.path.insert(0, env_.get('dataDir'))
        from app.core.db import db
        self.parseOptions()
        self.interpretOptions()
        self.initDataDirs()
        self.loadConfig()
        self.initLogging()
        self.db = db.Database(os.path.join(env_.get('dataDir'), 'database.db'))

    def detectExeBuild(self):
        try:
            env_.frozen = sys.frozen
        except AttributeError:
            env_.frozen = False

    def detectAppDir(self):
        appdir = os.path.realpath(os.path.dirname(sys.argv[0]))
        if env_.get('frozen'):
            #path_base = os.environ['_MEIPASS2']
            appdir = os.path.dirname(sys.executable)
        env_._appDir = appdir

    def parseOptions(self):
        data_dir = os.path.join(env_.get('appDir'), self.__class__.DEFAULT_DATA_DIR)
        p = OptionParser()
        p.add_option('-d', action = "store_true",
                     dest = 'daemonize', help = "Run the server as a daemon")
        p.add_option('-q', '--quiet', action = "store_true",
                     dest = 'quiet', help = "Don't log to console")
        p.add_option('-p', '--pidfile',
                     dest = 'pidfile', default = None,
                     help = "Store the process id in the given file")
        p.add_option('-t', '--debug', action = "store_true",
                     dest = 'debug', help = "Run in debug mode")

        options, args = p.parse_args()

        if args.__len__() == 1:
            data_dir = args[0]
        elif args.__len__() > 1:
            print ('Invalid argument cound: [data directory]')
            sys.exit(1)
        #register path settings to env
        env_.setDataDir(data_dir) #creates if not exists

        env_._args = args
        env_._options = options

    def interpretOptions(self):
        if env_.get('options').quiet:
            env_._quiet = True
        if env_.get('options').daemonize:
            env_._daemonize = True
        if env_.get('options').debug:
            env_._debug = True


    def loadConfig(self):
        env_.cfg = Config()

    def initDataDirs(self):
        dirs = ('config', 'logs', 'cache', 'plugins')
        for dir in dirs:
            dir = os.path.join(env_.get('dataDir'), dir)
            if not os.path.isdir(dir):
                os.mkdir(dir)

        plugins = open(os.path.join(env_.get('dataDir'), '__init__.py'), 'w')
        plugins.close()
        plugins = open(os.path.join(env_.get('dataDir'), 'plugins', '__init__.py'), 'w')
        plugins.close()

    def initLogging(self):
        # Use logging root 
        logger = logging.getLogger()
        # Create formatter 
        formatter = logging.Formatter("%(message)s")

        # Create file logging 
        rfh = logging.handlers.RotatingFileHandler(\
            os.path.join(env_.get('dataDir'), 'log.txt'),
            maxBytes = 500000, backupCount = 5
        ) #rfh
        rfh.setLevel(logging.INFO)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)

        # Create console handler and set level to debug 
        if env_.get('debug'):
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            logger.addHandler(sh)







