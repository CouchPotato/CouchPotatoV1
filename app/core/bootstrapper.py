from .environment import Environment as env_
from optparse import OptionParser
import sys, os

class Bootstrapper(object):
    '''
    classdocs
    '''


    def __init__(self, config = 'data/config.ini'):
        '''
        Constructor
        '''
        self.detectExeBuild()
        self.detectRunDir()
        # Define path based on frozen state

        # Include paths
        sys.path.insert(0, env_.get('runDir'))
        sys.path.insert(0, os.path.join(env_.get('runDir'), 'library'))



    def detectExeBuild(self):
        try:
            env_.frozen = sys.frozen
        except AttributeError:
            env_.frozen = False

    def detectRunDir(self):
        rundir = os.path.dirname(os.path.abspath(__file__))
        if env_.get('frozen'):
            #path_base = os.environ['_MEIPASS2']
            rundir = os.path.dirname(sys.executable)
        env_._runDir = rundir

    def parseOptions(self):
        config = env_.get('defaultConfig')
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
            config = args[0]
        elif args.__len__() > 1:
            print ('Invalid argument cound: [config path]')
            sys.exit(1)
            env_.setBasePath(os.path.dirname(config))
            config_name = os.path.basename(config)




