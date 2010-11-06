from app.core import getLogger
from app.core import env_
from app.lib.bones import PluginController
from app.plugins.movies._tables import MovieTable
from sqlalchemy.sql.expression import or_, desc
import json

Db = env_.get('db').createSession()
log = getLogger(__name__)

class MovieController(PluginController):

    def index(self):

        qMovie = Db.query(MovieTable)
        wanted = qMovie.order_by(MovieTable.name).filter(or_(MovieTable.status == u'want', MovieTable.status == u'waiting')).all()
        snatched = qMovie.order_by(desc(MovieTable.dateChanged), MovieTable.name).filter_by(status = u'snatched').all()
        downloaded = qMovie.order_by(desc(MovieTable.dateChanged), MovieTable.name).filter_by(status = u'downloaded').all()

        return self.render('index.html', {
            'movies':{
                'wanted': wanted,
                'snatched': snatched,
                'downloaded': downloaded
            }
        })

    def search(self, **data):

        query = data.get('movie')
        chosen = data.get('result')
        results = []

        if chosen:
            movie = {
                'imdb': data.get('result'),
                'name': data.get('movie'),
                'year': data.get('year')
            }
            message = 'success' if self.add(movie) else 'failed'
        elif query:
            movieInfo = self.plugin._threadedWait('findMovie', q = query)
            results = movieInfo.getResultSet()
            if len(results) > 0:
                message = 'found %d items.' % len(results)
            else:
                message = 'nothing found'

        return json.dumps({
            'message': message,
            'results': results
        })

    def reload(self, id):

        self.plugin._threaded('movieReload')

    def add(self, movie):
        '''
        Add movie by imdbId
        '''

        exists = Db.query(MovieTable).filter_by(imdb = movie.get('imdb')).first()

        if exists:
            log.info('Movie already exists, do update.')
            new = exists
        else:
            new = MovieTable()
            Db.add(new)

        # Update the stuff
        new.status = u'want'
        new.name = movie.get('name')
        new.imdb = movie.get('imdb')
        new.year = movie.get('year')
        Db.flush()

        log.info('Added : %s' % movie.get('name'))

        self.plugin._threaded('getMovieInfo')

        return True

    def delete(self, id):

        movie = Db.query(MovieTable).filter_by(id = id).one()
        movie.status = u'want'
        Db.flush()

        log.info('Deleted : %s' % movie.get('name'))

        self.plugin._threaded('movieDelete')

