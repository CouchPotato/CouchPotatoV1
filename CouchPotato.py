import sys
import os

rundir = os.path.dirname(os.path.abspath(__file__))
try:
    frozen = sys.frozen
except AttributeError:
    frozen = False

# Define path based on frozen state
if frozen:
    path_base = os.environ['_MEIPASS2']
else:
    path_base = rundir
sys.path.append(os.path.join(path_base, 'library'))

# Use debug conf if available
import logging.config
logdir = os.path.join(rundir, 'logs')
if not os.path.isdir(logdir):
    os.mkdir(logdir)
debugconfig = os.path.join(path_base, 'debug.conf')
if os.path.isfile(debugconfig):
    logging.config.fileConfig(debugconfig)
    debug = True
else:
    debug = False
    logging.config.fileConfig(os.path.join(path_base, 'logging.conf'))

log = logging.getLogger(__name__)

# Create cache dir
cachedir = os.path.join(rundir, 'cache')
if not os.path.isdir(cachedir):
    os.mkdir(cachedir)

from app.config.db import initDb
from optparse import OptionParser
import app
from app.config.configApp import configApp
import app.config.render
from app.config.routes import setup as Routes
from app.lib.cron import CronJobs

import cherrypy
from cherrypy.process import plugins

def server_start():

    p = OptionParser()
    p.add_option('-d', action = "store_true",
                 dest = 'daemonize', help = "Run the server as a daemon")
    p.add_option('-q', '--quiet', action = "store_true",
                 dest = 'quiet', help = "Don't log to console")
    p.add_option('-p', '--pidfile',
                 dest = 'pidfile', default = None,
                 help = "Store the process id in the given file")

    options, args = p.parse_args()

    config = os.path.join(rundir, 'config.ini')

    # Config app
    ca = configApp(config)
    initDb()

    # Start threads
    myCrons = CronJobs(cherrypy.engine, ca, debug)
    myCrons.subscribe()

    # User config, use own stuff to prevent unexpected results
    cherrypy.config.update({
        'global': {
            'server.thread_pool':               10,
            'server.socket_port':           int(ca.get('global', 'port')),
            'server.socket_host':               ca.get('global', 'host'),
            'server.environment':               ca.get('global', 'server.environment'),
            'engine.autoreload_on':             ca.get('global', 'engine.autoreload_on') and not options.daemonize,
            'tools.mako.collection_size':       500,
            'tools.mako.directories':           os.path.join(path_base, 'app', 'views'),

            'basePath':                         path_base,
            'runPath':                          rundir,
            'debug':                            debug,

            # Global workers
            'config':                           ca,
            'cron':                             myCrons.threads,
            'searchers':                        myCrons.searchers
        }
    })

    # Static config
    conf = {
        '/': {
            'request.dispatch': Routes(),
            'tools.sessions.on':  True,
            'tools.sessions.timeout': 240,

            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/css', 'text/javascript', 'application/javascript']
        },
        '/media':{
            'tools.staticdir.on': True,
            'tools.staticdir.root': path_base,
            'tools.staticdir.dir': "media",
            'tools.expires.on': True,
            'tools.expires.secs': 3600 * 24 * 7
        },
        '/cache':{
            'tools.staticdir.on': True,
            'tools.staticdir.root': rundir,
            'tools.staticdir.dir': "cache",
            'tools.expires.on': True,
            'tools.expires.secs': 3600 * 24 * 7
        }
    }

    # Don't use auth when password is empty
    if ca.get('global', 'password') != '':
        conf['/'].update({
            'tools.basic_auth.on': True,
            'tools.basic_auth.realm': 'Awesomeness',
            'tools.basic_auth.users': {ca.get('global', 'username'):ca.get('global', 'password')},
            'tools.basic_auth.encrypt': app.clearAuthText
        })
        cherrypy.tools.mybasic_auth = cherrypy.Tool('on_start_resource', app.basicAuth)

    # I'll do my own logging, thanks!
    cherrypy.log.error_log.propagate = False
    cherrypy.log.access_log.propagate = False

    #No Root controller as we provided all our own.
    cherrypy.tree.mount(root = None, config = conf)

    # Stop logging
    if options.quiet:
        cherrypy.config.update({'log.screen': False})

    # Deamonize
    if options.daemonize:
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(cherrypy.engine).subscribe()

    # PIDfile
    if options.pidfile:
        plugins.PIDFile(cherrypy.engine, options.pidfile).subscribe()

    # Setup the signal handler
    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()


    ## start the app
    try:
        cherrypy.engine.start()
    except:
        sys.exit(1)
    else:

        # Launch browser
        if ca.get('global', 'launchbrowser'):
            app.launchBrowser(ca.get('global', 'host'), ca.get('global', 'port'))

        cherrypy.engine.block()


if __name__ == '__main__':
    server_start()
