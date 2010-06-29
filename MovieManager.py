import sys
sys.path.insert(0, 'app')
sys.path.insert(0, 'library')

import logging.config
logging.config.fileConfig('logs/logging.conf')

from app.config.configApp import configApp
from app.config.routes import setup as Routes
from app.lib.cron import CronJobs
from cherrypy.lib.auth import check_auth
import cherrypy
import os

def clear_text(mypass):
    return mypass

def my_basic_auth(realm, users, encrypt = None):
    if check_auth(users, encrypt):
        return
    else:
        return

def start():

    config = os.path.join(os.path.dirname(__file__), 'config.ini')

    # Config app
    ca = configApp(config)

    # Start threads
    myCrons = CronJobs(cherrypy.engine, ca)
    myCrons.subscribe()

    cherrypy.config.update({
        'global': {
            'server.thread_pool':           int(ca.get('global', 'server.thread_pool')),
            'server.socket_port':           int(ca.get('global', 'port')),
            'server.socket_host':               ca.get('global', 'host'),
            'server.environment':               ca.get('global', 'server.environment'),
            'engine.autoreload_on':             ca.get('global', 'engine.autoreload_on'),
            'tools.mako.collection_size':   int(ca.get('global', 'tools.mako.collection_size')),
            'tools.mako.directories':           ca.get('global', 'tools.mako.directories'),
            'log.screen':                       False,

            #global workers
            'config':                           ca,
            'cron':                             myCrons.threads,
            'searchers':                        myCrons.searchers
        }
    })

    conf = {
        '/': {
            'request.dispatch': Routes(),
            'tools.sessions.on':  True,
            'tools.gzip.on': True
        },
        '/media':{
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.abspath(os.path.curdir),
            'tools.staticdir.dir': "media"
        }
    }

    # Don't use auth when password is empty
    if ca.get('global', 'password') != '':
        conf['/'].update({
            'tools.basic_auth.on': True,
            'tools.basic_auth.realm': 'Awesomeness',
            'tools.basic_auth.users': {ca.get('global', 'username'):ca.get('global', 'password')},
            'tools.basic_auth.encrypt': clear_text
        })
        cherrypy.tools.mybasic_auth = cherrypy.Tool('on_start_resource', my_basic_auth)

    app = cherrypy.tree.mount(None, config = conf)

    cherrypy.log.error_log.propagate = False
    cherrypy.log.access_log.propagate = False
    
    cherrypy.quickstart(app)

if __name__ == '__main__':
    start()
