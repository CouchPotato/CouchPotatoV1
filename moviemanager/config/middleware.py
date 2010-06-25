"""Pylons middleware initialization"""
from beaker.middleware import SessionMiddleware
from moviemanager.config.configApp import configApp, Auth
from moviemanager.config.environment import load_environment
from moviemanager.lib.cronNzb import startNzbCron
from moviemanager.lib.cronRenamer import startRenamerCron
from moviemanager.lib.cronTrailer import startTrailerCron, trailerQueue
from moviemanager.lib.provider.movie.search import movieSearcher
from moviemanager.lib.provider.nzb.search import nzbSearcher
from moviemanager.lib.sabNzbd import sabNzbd
from moviemanager.model.meta import Session as Db, Base
from paste.auth.basic import AuthBasicHandler
from paste.cascade import Cascade
from paste.deploy.converters import asbool
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
import atexit
import logging
import os
import time

log = logging.getLogger(__name__)

def make_app(global_conf, full_stack = True, static_files = True, **app_conf):

    # Configure the Pylons environment
    config = load_environment(global_conf, app_conf)

    # Auth stuff
    auth = Auth(config.get('username'), config.get('password'))

    # The Pylons WSGI app
    ap = PylonsApp(config = config)
    app = AuthBasicHandler(ap, "Login", auth.test)

    # Routing/Session Middleware
    app = RoutesMiddleware(app, config['routes.map'], singleton = False)
    app = SessionMiddleware(app, config)


    # Get custom config section
    configfile = config['global_conf'].get('__file__')
    ca = configApp(configfile)
    config['pylons.app_globals'].config = ca

    # Init db and create tables
    Base.metadata.create_all(bind = Db.bind)

    #searchers
    nzbSearch = nzbSearcher(ca);
    movieSearch = movieSearcher(ca);
    config['pylons.app_globals'].searcher['nzb'] = nzbSearch
    config['pylons.app_globals'].searcher['movie'] = movieSearch

    #trailer cron
    trailerCronJob = startTrailerCron(ca)
    config['pylons.app_globals'].cron['trailer'] = trailerCronJob
    config['pylons.app_globals'].cron['trailerQueue'] = trailerQueue

    #nzb search cron
    nzbCronJob = startNzbCron()
    nzbCronJob.provider = nzbSearch
    nzbCronJob.sabNzbd = sabNzbd(ca)
    config['pylons.app_globals'].cron['nzb'] = nzbCronJob

    #renamer cron
    renamerCronJob = startRenamerCron(ca, config['pylons.app_globals'].searcher, trailerQueue)
    config['pylons.app_globals'].cron['renamer'] = renamerCronJob


    #when exit app and finish the running crons
    def exitApp():
        log.info('Starting shutdown.')
        nzbCronJob.quit()
        renamerCronJob.quit()
        trailerCronJob.quit()

        while not nzbCronJob.canShutdown() or not renamerCronJob.canShutdown() or not trailerCronJob.canShutdown():
            time.sleep(1)

        log.info('Shutdown successful.')
        os._exit(1)

    config['pylons.app_globals'].cron['quiter'] = exitApp
    atexit.register(exitApp)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])
    app.config = config


    return app
