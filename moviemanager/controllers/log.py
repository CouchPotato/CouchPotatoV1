from moviemanager.lib.base import BaseController, render
from pylons import request, config, tmpl_context as c
from webhelpers.html.builder import literal
import logging
import os

cron = config.get('pylons.app_globals').cron
log = logging.getLogger(__name__)

class LogController(BaseController):
    """ Show some log stuff """

    def __before__(self):
        self.setGlobals()

    def index(self):
        '''
        See latest log file
        '''

        c.file = 'MovieManager.log'
        fileAbs = os.path.join(os.path.abspath(os.path.curdir), 'logs', c.file)
        if request.params.get('nr') and int(request.params.get('nr')) > 0 and os.path.isfile(fileAbs+'.'+request.params.get('nr')):
            fileAbs += '.'+request.params.get('nr')
            c.file += '.'+request.params.get('nr')

        f = open(fileAbs, 'r')
        c.log = literal(f.read().replace('\n', '<br />\n'))

        return render('/log/index.html')
