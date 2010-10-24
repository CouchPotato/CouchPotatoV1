from app.controllers.config import ConfigController
from app.controllers.cron import CronController
from app.controllers.feed import FeedController
from app.controllers.log import LogController
from app.controllers.movie import MovieController
from app.controllers.manage import ManageController
import cherrypy

def setup():
    mapper = cherrypy.dispatch.RoutesDispatcher()
    mapper.minimization = False
    mapper.explicit = False
    mapper.append_slash = True

    mapper.connect('main', '/', controller = MovieController(), action = 'index')

    for controller in [MovieController, FeedController, ConfigController, CronController, ManageController, LogController]:
        name = str(controller).split('.')[-2]
        mapper.connect(name, '/' + name + '/', controller = controller(), action = 'index')
        mapper.connect(name, '/' + name + '/:action/', controller = controller(), action = 'index')

    mapper.connect('userscript', '/CouchPotato.user.js', controller = ConfigController(), action = 'userscript')

    return mapper
