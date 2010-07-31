from app.lib.qualities import Qualities
from library.minify import Minify
import cherrypy
import routes

def url(*args, **kwargs):
    host = 'http://' + cherrypy.request.headers.get('host')
    base = cherrypy.config.get('config').get('global', 'urlbase')
    base = host + '/' + base if base else host

    return cherrypy.url(routes.url_for(*args, **kwargs), base = base)

def redirect(url):
    raise cherrypy.HTTPRedirect(url)
