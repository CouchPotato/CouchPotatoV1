from moviemanager.lib.base import BaseController, render
from moviemanager.lib.provider.theMovieDb import theMovieDb
from moviemanager.model import Movie, RenameHistory
from moviemanager.model.meta import Session as Db
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
import datetime
import logging
import time

cron = config.get('pylons.app_globals').cron
log = logging.getLogger(__name__)

class MovieController(BaseController):

    def __before__(self):
        self.setGlobals()

        self.qMovie = Db.query(Movie)
        #self.qRename = Db.query(RenameHistory)
        #self.qFeed = Db.query(Feed)


    def index(self):
        '''
        Show all wanted, snatched, downloaded movies
        '''

        c.movies = self.qMovie.order_by(Movie.name).filter_by(status = u'want')
        c.snatched = self.qMovie.order_by(Movie.name).filter_by(status = u'snatched')
        c.downloaded = self.qMovie.order_by(Movie.name).filter_by(status = u'downloaded')

        return render('/movie/index.html')


    def delete(self, id):
        '''
        Mark movie as deleted
        '''

        movie = self.qMovie.filter_by(id = id).one()

        #delete feeds
        [Db.delete(x) for x in movie.Feeds]

        #set status
        movie.status = u'deleted'

        Db.commit()

        return redirect(url(controller = 'movie', action = 'index'))


    def downloaded(self, id):
        '''
        Mark movie as downloaded
        '''

        movie = self.qMovie.filter_by(id = id).one()

        #delete feeds
        [Db.delete(x) for x in movie.Feeds]

        #set status
        movie.status = u'downloaded'

        Db.commit()

        return redirect(url(controller = 'movie', action = 'index'))


    def reAdd(self, id):
        '''
        Re-add movie and force search
        '''

        movie = self.qMovie.filter_by(id = id).one()

        #set status
        movie.status = u'want'

        Db.commit()

        #gogo find nzb for added movie via Cron
        cron.get('nzb')._searchNzb(movie)

        return redirect(url(controller = 'movie', action = 'index'))


    def search(self):
        '''
        Search for added movie. 
        Add if only 1 is found
        '''

        c.quality = request.params['quality']
        c.movie = request.params['movie']
        log.info('Searching for: %s', c.movie)

        provider = theMovieDb(config.get('TheMovieDB'))

        if request.params.get('add'):
            result = provider.findById(request.params['movie'])
            
            if result.year != 'None' or request.params.get('year'):
                self._addMovie(result, c.quality, request.params.get('year'))
                return redirect(url(controller = 'movie', action = 'index'))

        c.results = provider.find(c.movie)

        return render('/movie/search.html')


    def imdbAdd(self, id):
        '''
        Add movie by imdbId
        '''

        c.id = id
        c.success = False

        c.result = self.qMovie.filter_by(imdb = id, status = u'want').first()
        if c.result:
            c.success = True

        if request.params.get('add'):
            provider = theMovieDb(config.get('TheMovieDB'))
            c.result = provider.findByImdbId(id)

            self._addMovie(c.result, request.params['quality'], request.params.get('year'))
            log.info('Added : %s', c.result.name)
            c.success = True

        return render('/movie/imdbAdd.html')


    def _addMovie(self, movie, quality, year = None):
        log.info('Adding movie to database: %s', movie.name)

        exists = self.qMovie.filter_by(movieDb = movie.id).first()
        if exists:
            log.error('Movie already exists.')
            new = exists
        else:
            new = Movie()
            Db.add(new)

        new.status = u'want'
        new.name = movie.name
        new.imdb = movie.imdb
        new.movieDb = movie.id
        new.quality = quality

        if year and movie.year == 'None':
            new.year = year
        else:
            new.year = movie.year
        Db.commit()

        #gogo find nzb for added movie via Cron
        cron.get('nzb')._searchNzb(new)

