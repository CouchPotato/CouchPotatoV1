import sys
import os
import traceback
import logging

import bootstrapper

import cherrypy
from cherrypy.process import plugins

import app
import app.config.render
from app.CouchPotato import CouchPotato as cp_
from app.config.db import initDb
from app.config.configApp import configApp
from app.config.routes import setup as Routes
from app.config.updater import Updater
from app.lib.cron import CronJobs

rundir = os.path.dirname(os.path.abspath(__file__))
try:
    frozen = sys.frozen
except AttributeError:
    frozen = False

# Define path based on frozen state
if frozen:
    #path_base = os.environ['_MEIPASS2']
    path_base = os.path.dirname(sys.executable)
else:
    path_base = rundir

# Include paths
sys.path.insert(0, path_base)
sys.path.insert(0, os.path.join(path_base, 'library'))

log = logging.getLogger(__name__)

# Use debug conf if available
def server_start():
    options = cp_.options
    args = cp_.args
    ca = cp_.cfg
    initDb()

    # Start threads
    myCrons = CronJobs(cherrypy.engine, ca)
    myCrons.subscribe()

    # Update script
    myUpdater = Updater(cherrypy.engine)
    myUpdater.subscribe()

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
            'cachePath':                        ca.get('paths', 'cache'),
            'frozen':                           frozen,

            # Global workers
            'config':                           ca,
            'updater':                          myUpdater,
            'cron':                             myCrons.threads,
            'searchers':                        myCrons.searchers,
            'flash':                            app.flash()
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
        pass

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
        log.info('Spawning server...')
        cherrypy.engine.start()
        log.info('Server running')
    except:
        log.info(traceback.format_exc())
        sys.exit(1)
    else:

        # Launch browser
        if ca.get('global', 'launchbrowser'):
            app.launchBrowser(ca.get('global', 'host'), ca.get('global', 'port'))

        cherrypy.engine.block()

if __name__ == '__main__':
    server_start()