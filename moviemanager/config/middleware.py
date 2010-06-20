"""Pylons middleware initialization"""
from beaker.middleware import SessionMiddleware
from moviemanager.config.environment import load_environment
from moviemanager.model.meta import Session as Db, Base
from paste.cascade import Cascade
from paste.deploy.converters import asbool
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
from paste.auth.basic import AuthBasicHandler
import ConfigParser


def make_app(global_conf, full_stack = True, static_files = True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """

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
    parser = ConfigParser.RawConfigParser()
    parser.read(configfile)

    for section in ['Sabnzbd', 'TheMovieDB', 'NZBsorg']:
        config[section] = {}
        for option in parser.options(section):
            config[section][option] = parser.get(section, option)



    # Init db and create tables
    Base.metadata.create_all(bind = Db.bind)



    #cronjob thread
    from moviemanager.lib.cron import startNzbCron, NzbCron
    from moviemanager.lib.provider.nzbs import nzbs
    from moviemanager.lib.sabNzbd import sabNzbd

    #nzb search cron
    nzbCronJob = startNzbCron()
    nzbCronJob.provider = nzbs(config['NZBsorg'])
    nzbCronJob.sabNzbd = sabNzbd(config['Sabnzbd'])
    config['pylons.app_globals'].cron['nzb'] = nzbCronJob




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

class Auth():

    def __init__(self, username, password):
        self.u = username
        self.p = password

    def test(self, environ, username, password):
        if username == self.u and password == self.p:
            return True
        else:
            return False
