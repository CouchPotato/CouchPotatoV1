from app.controllers import BaseController
import cherrypy
import logging
import os.path

log = logging.getLogger(__name__)

class LogController(BaseController):
    """ Show some log stuff """

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "log/index.html")
    def index(self, **data):
        '''
        See latest log file
        '''

        file = 'MovieManager.log'
        fileAbs = os.path.join(os.path.abspath(os.path.curdir), 'logs', file)
        if data.get('nr') and int(data.get('nr')) > 0 and os.path.isfile(fileAbs + '.' + data.get('nr')):
            fileAbs += '.' + data.get('nr')
            file += '.' + data.get('nr')

        f = open(fileAbs, 'r')
        log = f.read().replace('\n', '<br />\n')

        return self.render({'file':file, 'log':log})
