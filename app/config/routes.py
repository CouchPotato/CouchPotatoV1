from app.controllers.config import ConfigController
from app.controllers.cron import CronController
from app.controllers.log import LogController
from app.controllers.movie import MovieController
from app.controllers.feed import FeedController
import cherrypy

def setup():
    mapper = cherrypy.dispatch.RoutesDispatcher()
    mapper.minimization = False
    mapper.explicit = False
    mapper.append_slash = True

    mapper.connect('main', '/', controller = MovieController(), action = 'index')

    mapper.connect('movie', '/movie/', controller = MovieController(), action = 'index')
    mapper.connect('movie', '/movie/:action/', controller = MovieController(), action = 'index')
    
    mapper.connect('cron', '/cron/', controller = CronController())
    mapper.connect('cron', '/cron/:action/', controller = CronController(), action = 'index')
    
    mapper.connect('config', '/config/', controller = ConfigController())
    mapper.connect('config', '/config/:action/', controller = ConfigController(), action = 'index')
    
    mapper.connect('userscript', '/CouchPotato.user.js', controller = ConfigController(), action = 'userscript')
    
    mapper.connect('log', '/log/', controller = LogController())
    mapper.connect('log', '/log/:action/', controller = LogController(), action = 'index')
    
    mapper.connect('feed', '/feed/', controller = FeedController())
    mapper.connect('feed', '/feed/:action/', controller = FeedController(), action = 'index')

    return mapper
