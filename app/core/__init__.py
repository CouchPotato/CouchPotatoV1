from .environment import Environment as env_
from .bootstrapper import Bootstrapper as bootstrap
bootstrap()
import cherrypy
import logging
class getLogger(object):
    def __init__(self, name):
        self.name = name
    def debug(self, msg):
        return cherrypy.log(msg, self.name, logging.DEBUG)
    def info(self, msg):
        return cherrypy.log(msg, self.name, logging.INFO)
    def error(self, msg):
        return cherrypy.log(msg, self.logging.ERROR)

#from .frontend import Engine
import frontend


