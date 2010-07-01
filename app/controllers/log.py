from app.controllers import BaseController
import cherrypy
import logging
import os
from string import ascii_letters, digits
import unicodedata

log = logging.getLogger(__name__)
file = 'MovieManager.log'
logfile = os.path.join(os.path.abspath(os.path.curdir), 'logs', file)

class LogController(BaseController):
    """ Show some log stuff """

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "log/index.html")
    def index(self, **data):
        '''
        See latest log file
        '''

        file = 'MovieManager.log'
        fileAbs = logfile
        if data.get('nr') and int(data.get('nr')) > 0 and os.path.isfile(fileAbs + '.' + data.get('nr')):
            fileAbs += '.' + data.get('nr')
            file += '.' + data.get('nr')

        f = open(fileAbs, 'r')
        log = f.read().replace('\n', '<br />\n')

        return self.render({'file':file, 'log':self.toSafeString(log)})
    
    def toSafeString(self, string):
        safe_chars = ascii_letters + digits + '_ </\>[]-&?=.,;:+!@#$%^&*()\'"'
        return ''.join([char if char in safe_chars else '' for char in string])
