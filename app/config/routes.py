from app.controllers.config import ConfigController
from app.controllers.cron import CronController
from app.controllers.feed import FeedController
from app.controllers.log import LogController
from app.controllers.movie import MovieController
import cherrypy

def setup():
    mapper = cherrypy.dispatch.RoutesDispatcher()
    mapper.minimization = False
    mapper.explicit = False
    mapper.append_slash = True

    mapper.connect('main', '/', MovieController(), action = 'index')

    mapper.connect('movie', '/movie/', MovieController(), action = 'index')
    mapper.connect('movie', '/movie/:action/', MovieController(), action = 'index')

    mapper.connect('cron', '/cron/', CronController())
    mapper.connect('cron', '/cron/:action/', CronController(), action = 'index')

    mapper.connect('config', '/config/', ConfigController())
    mapper.connect('config', '/config/:action/', ConfigController(), action = 'index')

    mapper.connect('userscript', '/CouchPotato.user.js', ConfigController(), action = 'userscript')

    mapper.connect('log', '/log/', controller = LogController())
    mapper.connect('log', '/log/:action/', LogController(), action = 'index')

    mapper.connect('feed', '/feed/', FeedController())
    mapper.connect('feed', '/feed/:action/', FeedController(), action = 'index')

    return mapper
