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

        c.movies = self.qMovie.filter_by(status = u'want')
        c.snatched = self.qMovie.filter_by(status = u'snatched')
        c.downloaded = self.qMovie.filter_by(status = u'downloaded')

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
            self._addMovie(result, c.quality)
            return redirect(url(controller = 'movie', action = 'index'))

        c.results = provider.find(c.movie)

        #redirect if none found
        if len(c.results) == 0:
            log.info('No movies found.')
            return redirect(url(controller = 'movie', action = 'add'))

        return render('/movie/search.html')


    def getNzb(self, id):

        c.movie = self.qMovie.filter_by(id = id).one()
        c.results = c.movie.Feeds

        return render('/movie/nzbs.html')


    def _addMovie(self, movie, quality):
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
        new.year = movie.year
        Db.commit()

        #gogo find nzb for added movie via Cron
        cron.get('nzb')._searchNzb(new)

