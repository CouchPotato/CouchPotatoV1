"""Pylons environment configuration"""
from mako.lookup import TemplateLookup
from moviemanager.config.routing import make_map
from moviemanager.model import init_model
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error
from sqlalchemy import engine_from_config
import moviemanager.lib.app_globals as app_globals
import moviemanager.lib.helpers
import os
from hashlib import sha1


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root = root,
                 controllers = os.path.join(root, 'controllers'),
                 static_files = os.path.join(root, 'public'),
                 templates = [os.path.join(root, 'templates')])

    #default config
    appdir = os.path.abspath(os.curdir)
    app_conf['cache_dir'] = appdir + '/cache'
    app_conf['sqlalchemy.url'] = 'sqlite:///' + appdir + '/data.db'
    app_conf['beaker.session.key'] = 'moviemanager'
    app_conf['beaker.session.secret'] = sha1(root).hexdigest()

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package = 'moviemanager', paths = paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = moviemanager.lib.helpers

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories = paths['templates'],
        error_handler = handle_mako_error,
        module_directory = os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding = 'utf-8', default_filters = ['escape'],
        imports = ['from webhelpers.html import escape'])

    # Setup the SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)

    return config
