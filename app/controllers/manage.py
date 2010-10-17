from app.config.cplog import CPLog
from app.controllers import BaseController
from app.lib.library import Library
import cherrypy
import json

log = CPLog(__name__)

class ManageController(BaseController):
    """ Go actions!, searching for trailer/subtitles etc """

    @cherrypy.tools.mako(filename = "manage/index.html")
    def index(self):

        return self.render({})

    @cherrypy.expose
    @cherrypy.tools.caching(delay = 3600)
    def movies(self):

        library = Library()
        library.noTables = True
        movies = library.getMovies()

        return json.dumps(movies)
