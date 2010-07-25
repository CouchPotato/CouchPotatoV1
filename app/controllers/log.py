from app.controllers import BaseController, url, redirect
from markupsafe import escape
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

        # Reverse
        f = open(fileAbs, 'r')
        lines = []
        for line in f.readlines():
            lines.insert(0, line)

        log = ''
        for line in lines:
            log += line

        return self.render({'file':filename, 'log':escape(log)})

    def clear(self):

        for root, subfiles, filenames in os.walk(logdir):
            log.debug(subfiles)
            for filename in filenames:
                file = os.path.join(root, filename)

                if file == logfile:
                    with open(logfile, 'w') as f:
                        f.write('')
                else:
                    os.remove(file)

        return redirect(url(controller = 'log', action = 'index'))
