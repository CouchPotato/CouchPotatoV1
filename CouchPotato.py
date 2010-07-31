import sys
import os

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

import traceback
import logging
import bootstrapper

import cherrypy
from cherrypy.process import plugins

import app
import app.config.render
from app.environment import Environment as _env
from app.config.db import initDb
from app.config.configApp import appConfig
from app.config.routes import setup as Routes
from app.config.updater import Updater
from app.lib.cron import CronJobs

log = logging.getLogger(__name__)

# Use debug conf if available
def server_start():

    initDb()

    # Start threads
    myCrons = CronJobs(cherrypy.engine, ca)
    myCrons.subscribe()

    # Update script
    myUpdater = Updater(cherrypy.engine)
    myUpdater.subscribe()


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
