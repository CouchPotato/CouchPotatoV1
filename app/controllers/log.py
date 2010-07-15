from app.controllers import BaseController, url, redirect
from string import ascii_letters, digits
import cherrypy
import logging
import os

log = logging.getLogger(__name__)
file = 'CouchPotato.log'
logdir = os.path.join(os.path.abspath(os.path.curdir), 'logs')
logfile = os.path.join(logdir, file)

class LogController(BaseController):
    """ Show some log stuff """

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "log/index.html")
    def index(self, **data):
        '''
        See latest log file
        '''

        fileAbs = logfile
        filename = file
        if data.get('nr') and int(data.get('nr')) > 0 and os.path.isfile(fileAbs + '.' + data.get('nr')):
            fileAbs += '.' + data.get('nr')
            filename += '.' + data.get('nr')

        f = open(fileAbs, 'r')
        log = f.read()

        return self.render({'file':filename, 'log':self.toSafeString(log)})

    def clear(self):

        for root, subfiles, filenames in os.walk(logdir):
            for filename in filenames:
                file = os.path.join(root, filename)

                if file == logfile:
                    with open(logfile, 'w') as f:
                        f.write('')
                else:
                    os.remove(file)

        return redirect(url(controller = 'log', action = 'index'))


    def toSafeString(self, string):
        safe_chars = ascii_letters + digits + '_ </\>[]-&?=.,;:+!@#$%^&*()\'"{}\n\t'
        return ''.join([char if char in safe_chars else '' for char in string])
