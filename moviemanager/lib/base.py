from moviemanager.lib.quality import Quality
from moviemanager.model.meta import Session
from pylons import config, tmpl_context as c
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render

cron = config.get('pylons.app_globals').cron

class BaseController(WSGIController):
    
    def setGlobals(self):
        c.qualityList = Quality().all()
        c.lastCheck = cron.get('nzb').lastCheck()
        c.nextCheck = cron.get('nzb').nextCheck()
        c.checking = cron.get('nzb').isChecking()

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            Session.remove()
