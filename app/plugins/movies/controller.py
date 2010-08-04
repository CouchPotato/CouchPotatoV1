from app.core.environment import Environment as env_
from app.lib.bones import PluginController
from app.plugins.movies._tables import MovieTable
from sqlalchemy.sql.expression import or_, desc
import cherrypy

Db = env_.get('db').createSession()

class MovieController(PluginController):

    @cherrypy.expose
    def index(self):

        qMovie = Db.query(MovieTable)
        movies = qMovie.order_by(MovieTable.name).filter(or_(MovieTable.status == u'want', MovieTable.status == u'waiting')).all()
        snatched = qMovie.order_by(desc(MovieTable.dateChanged), MovieTable.name).filter_by(status = u'snatched').all()
        downloaded = qMovie.order_by(desc(MovieTable.dateChanged), MovieTable.name).filter_by(status = u'downloaded').all()

        return self.render('index.html', {
            'movies': movies,
            'snatched': snatched,
            'downloaded': downloaded
        })

    def search(self, query):

        movieInfo = self.plugin._fire('findMovieInfo', {'q' : query})
        print movieInfo.getResult()
