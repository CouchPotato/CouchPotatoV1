from app.config.db import Session as Db, Movie, QualityTemplate, MovieQueue
from app.controllers import BaseController, url, redirect
from sqlalchemy.sql.expression import or_, desc
import cherrypy
import logging

log = logging.getLogger(__name__)

qMovie = Db.query(Movie)

class MovieController(BaseController):

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "movie/index.html")
    def index(self):
        '''
        Show all wanted, snatched, downloaded movies
        '''

        movies = qMovie.order_by(Movie.name).filter(or_(Movie.status == u'want', Movie.status == u'waiting')).all()
        snatched = qMovie.order_by(desc(Movie.dateChanged), Movie.name).filter_by(status = u'snatched').all()
        downloaded = qMovie.order_by(desc(Movie.dateChanged), Movie.name).filter_by(status = u'downloaded').all()

        return self.render({'movies': movies, 'snatched':snatched, 'downloaded':downloaded})


    @cherrypy.expose
    def delete(self, id):
        '''
        Mark movie as deleted
        '''

        movie = qMovie.filter_by(id = id).one()

        #set status
        movie.status = u'deleted'
        Db.flush()

        #return redirect(url(controller = 'movie', action = 'index'))


    @cherrypy.expose
    def downloaded(self, id):
        '''
        Mark movie as downloaded
        '''

        movie = qMovie.filter_by(id = id).one()

        #set status
        movie.status = u'downloaded'
        Db.flush()

        return redirect(url(controller = 'movie', action = 'index'))


    @cherrypy.expose
    def reAdd(self, id):
        '''
        Re-add movie and force search
        '''

        movie = qMovie.filter_by(id = id).one()

        for x in movie.queue:
            x.completed = False

        #set status
        movie.status = u'want'
        Db.flush()

        #gogo find nzb for added movie via Cron
        self.cron.get('yarr').forceCheck(movie)
        self.searchers.get('etaQueue').put(movie)

        return redirect(url(controller = 'movie', action = 'index'))

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "movie/add.html")
    def add(self):

        return self.render({})

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "movie/search.html")
    def search(self, **data):
        '''
        Search for added movie. 
        Add if only 1 is found
        '''
        moviename = data.get('moviename')
        movienr = data.get('movienr')
        quality = data.get('quality')
        year = data.get('year')

        if data.get('add'):
            results = cherrypy.session.get('searchresults')
            if not results:
                log.error('Researching for results..')
                results = self.searchers.get('movie').find(moviename)
            result = results[int(movienr)]

            if year:
                result.year = year

            if result.year == 'None':
                return self.render({'error': 'year'})
            else:
                self._addMovie(result, quality)
                return redirect(url(controller = 'movie', action = 'index'))
        else:
            results = self.searchers.get('movie').find(moviename)
            cherrypy.session['searchresults'] = results

        return self.render({'moviename':moviename, 'results': results, 'quality':quality})

    @cherrypy.expose
    @cherrypy.tools.mako(filename = "movie/imdbAdd.html")
    def imdbAdd(self, **data):
        '''
        Add movie by imdbId
        '''

        id = data.get('id')
        success = False

        result = qMovie.filter_by(imdb = id, status = u'want').first()
        if result:
            success = True

        if data.get('add'):
            result = self.searchers.get('movie').findByImdbId(id)

            self._addMovie(result, data.get('quality'), data.get('year'))
            log.info('Added : %s', result.name)
            success = True

        return self.render({'id':id, 'result':result, 'success':success, 'year':data.get('year')})

    @cherrypy.expose
    def updateInfo(self):

        movies = qMovie.order_by(Movie.name).filter(or_(Movie.status == u'want', Movie.status == u'waiting')).all()
        for movie in movies:
            self.searchers.get('movie').getExtraInfo(movie)

        return redirect(cherrypy.request.headers.get('referer'))

    def _addMovie(self, movie, quality, year = None):
        log.info('Adding movie to database: %s', movie.name)

        if movie.id:
            exists = qMovie.filter_by(movieDb = movie.id).first()
        else:
            exists = qMovie.filter_by(imdb = movie.imdb).first()

        if exists:
            log.info('Movie already exists, do update.')

            # Delete old qualities
            for x in exists.queue:
                x.active = False

            new = exists
        else:
            new = Movie()
            Db.add(new)

        # Update the stuff
        new.status = u'want'
        new.name = movie.name
        new.imdb = movie.imdb
        new.movieDb = movie.id
        new.quality = quality

        # Year from custom input
        if year and movie.year == 'None':
            new.year = year
        else:
            new.year = movie.year
        Db.flush()

        # Add qualities to the queue
        quality = Db.query(QualityTemplate).filter_by(id = quality).one()
        for type in quality.types:
            queue = MovieQueue()
            queue.qualityType = type.type
            queue.movieId = new.id
            queue.order = type.order
            queue.active = True
            queue.completed = False
            queue.waitFor = 0 if type.markComplete else quality.waitFor
            queue.markComplete = type.markComplete
            Db.add(queue)
            Db.flush()

        #Get xml from themoviedb and save to cache
        self.searchers.get('movie').getExtraInfo(new, overwrite = True)

        #gogo find nzb for added movie via Cron
        self.cron.get('yarr').forceCheck(new)
        self.searchers.get('etaQueue').put(new)
