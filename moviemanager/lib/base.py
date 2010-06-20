"""The base Controller API

Provides the BaseController class for subclassing.
"""
from moviemanager.lib.quality import Quality
from moviemanager.model.meta import Session
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            Session.remove()
