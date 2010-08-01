import cherrypy
from cherrypy.process import plugins
from environment import Environment as env_
from app.core import getLogger
myCherry = None
import logging
log = getLogger(__name__)

class Bootstraper(object):
    '''
    Initializes the web user interface
    '''

    def __init__(self, name = None):
        '''
        Constructor
        '''
        self.config = {}
        self.routes = cherrypy.dispatch.RoutesDispatcher()

    def getConfig(self):
        pass

    def registerStaticDir(self, virtual, root, subfolder, expire = False):
        expire_on = False
        expire_secs = 0

        if expire is not False:
            try:
                expire_secs = int(expire)
                expire_on = True
            except:
                raise
        elif expire is True:
            raise ValueError('invalid expiration time')

        self.config.update({
            virtual:{
                'tools.staticdir.on': True,
                'tools.staticdir.dir': subfolder,
                'tools.staticdir.root' : root,
                'tools.expires.on': expire_on,
                'tools.expires.secs': expire_secs
            }
        })
    # end registerStaticDir

    def addRoute(self, route):
        try:
            self.routes.connect(route.name, route.route, route.controller)
        except:
            raise

    def addRoutes(self, routes):
        for route in routes:
            self.addRoute(route)

class Route(object):
    """
    provides means to register a custom controller with
    the frontend easily
    """
    _instances = 0
    def __init__(self, **kwargs):
        '''parameters: controller, name, route, action'''
        self.__class__._instances += 1
        if 'controller' not in kwargs:
            kwargs['controller'] = None
        if 'name' not in kwargs:
            kwargs['name'] = 'unknown-' \
                + str(self.__class__._instances)
        if 'route' not in kwargs:
            kwargs['route'] = None
        if 'action' not in kwargs:
            kwargs['action'] = 'index'

        #now assign kwargs to instance var
        self.name = kwargs['name']
        self.controller = kwargs['controller']
        self.route = kwargs['route']
        self.action = kwargs['action']


class Frontend(object):
    def __init__(self):
        pass

    def start(self):
        log.info('Starting web interface...')
        cherrypy.engine.start()
        log.info('Web interface running...')
        cherrypy.engine.block()
        log.info('Server terminated')
