"""
T
"""
import cherrypy
from cherrypy.process import plugins

myCherry = None

class Bootstraper(object):
    '''
    Initializes the web user interface
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.config = {}

    def getConfig(self):
        pass

    def registerStaticDir(self, virtual, actual, expire = False):
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
                'tools.staticdir.root': _env.getBasePath(),
                'tools.staticdir.dir': actual,
                'tools.expires.on': expire_on,
                'tools.expires.secs': expire_secs
            }
        })
    # end registerStaticDir






class Frontend(object):
    pass
