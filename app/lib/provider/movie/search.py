from app.config.cplog import CPLog
from app.config.db import Session as Db, MovieExtra, Movie
from app.lib.provider.movie.sources.imdbWrapper import imdbWrapper
from app.lib.provider.movie.sources.theMovieDb import theMovieDb
from sqlalchemy.sql.expression import and_, or_
import cherrypy
import os

log = CPLog(__name__)

class movieSearcher():

    sources = []
    limit = 8

    def __init__(self, config):

        self.config = config

        # Config TheMovieDB
        self.theMovieDb = theMovieDb(self.config)
        self.sources.append(self.theMovieDb)

        # Config imdbWrapper
        self.imdb = imdbWrapper(self.config)
        self.sources.append(self.imdb)

        # Update the cache
        movies = Db.query(Movie).order_by(Movie.name).filter(or_(Movie.status == u'want', Movie.status == u'waiting')).all()
        for movie in movies:
            if not movie.extra:
                self.getExtraInfo(movie)

            # Fix db errors
            try:

                # Clear wrong value
                imdb_is_int = False
                try:
                    imdb_is_int = float(movie.imdb)
                except ValueError:
                    pass

                if not imdb_is_int and movie.imdb[:2] != 'tt':
                    movie.imdb = None
                    Db.flush()

                if movie.imdb and movie.imdb[:2] != 'tt':
                    movie.imdb = 'tt%s' % movie.imdb
                    Db.flush()
                elif not movie.imdb and movie.movieDb:
                    results = self.findById(movie.movieDb)
                    if results.get('imdb'):
                        movie.imdb = results.get('imdb')
                        Db.flush()

                if not movie.imdb:
                    log.error('Errors in your database, try and remove & re-add: %s' % movie.name)
            except:
                pass

    def find(self, q, limit = 8, alternative = True):
        ''' Find movie by name '''

        q = unicode(q).lower().strip()

        for source in self.sources:
            result = source.find(q, limit = limit, alternative = alternative)
            if result:
                results = []
                for r in result:
                    results.append(self.checkResult(r))

                return results if limit > 1 else results.pop(0)

        return []


    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''

        for source in self.sources:
            result = source.findById(id)
            if result:
                return self.checkResult(result)

        return []


    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''

        for source in self.sources:
            result = source.findByImdbId(id)
            if result:
                return self.checkResult(result)

        return []

    def checkResult(self, result):

        #do imdb search
        if not result.imdb:
            q = result.name;
            if result.year:
                q += ' (' + result.year + ')'
            r = self.imdb.find(q)
            if len(r) > 0:
                result.year = r[0].year
                result.imdb = r[0].imdb

        if not result.id:
            r = self.theMovieDb.findByImdbId(result.imdb)
            if r:
                result.id = r.id

        return result

    def cacheExtra(self, theMovieDbId, overwrite = False):
        xmlCache = os.path.join(cherrypy.config.get('cachePath'), 'xml')
        xmlFile = os.path.join(xmlCache, str(theMovieDbId) + '.xml')
        exists = os.path.isfile(xmlFile)

        if overwrite or not exists:
            xml = self.theMovieDb.getXML(theMovieDbId)

            if xml:
                # Make dir
                if not os.path.isdir(xmlCache):
                    os.mkdir(xmlCache)

                # Remove old
                if exists:
                    os.remove(xmlFile)

                # Write file
                with open(xmlFile, 'wb') as f:
                    f.write(xml.read())

    def getExtraInfo(self, movie, overwrite = False):

        if(type(movie) in [int, str, unicode]):
            movie = Db.query(Movie).filter_by(id = movie).one()

        # Try and update if no tmdbId
        if not movie.movieDb:
            result = self.theMovieDb.findByImdbId(movie.imdb)
            if result:
                movie.movieDb = result.id
                Db.flush()

        if not movie.movieDb:
            log.error('Search failed for "%s", no TheMovieDB id.' % movie.name)
            return

        movieId = movie.id
        theMovieDbId = movie.movieDb

        self.cacheExtra(theMovieDbId, overwrite)
        xmlFile = os.path.join(cherrypy.config.get('cachePath'), 'xml', str(theMovieDbId) + '.xml')
        if os.path.isfile(xmlFile):
            if overwrite:
                log.info('Getting extra movie info for %s.' % movie.name)

            handle = open(xmlFile, 'r')
            movieInfo = self.theMovieDb.getItems(handle, 'movies/movie')
            if not movieInfo:
                return
            movieInfo = movieInfo[0]

            # rating
            rating = self.theMovieDb.gettextelement(movieInfo, 'rating')
            self.saveExtra(movieId, 'rating', rating)

            overview = self.theMovieDb.gettextelement(movieInfo, 'overview')
            if overview:
                overview = self.theMovieDb.toSaveString(overview)
                self.saveExtra(movieId, 'overview', overview)

            hasPosterThumb = False

            images = movieInfo.findall('images/image')
            hasPosterCover = False
            hasPosterMid = False
            hasPosterThumb = False
            for image in images:
                imageFile = str(theMovieDbId) + '-' + image.get('type') + '-' + image.get('size') + '.jpg'
                if image.get('type') == 'poster' and image.get('size') == 'cover' and not hasPosterCover:
                    poster = self.theMovieDb.saveImage(image.get('url'), imageFile)
                    if poster: self.saveExtra(movieId, 'poster_cover', poster)
                    hasPosterCover = True
                if image.get('type') == 'poster' and image.get('size') == 'mid' and not hasPosterMid:
                    poster = self.theMovieDb.saveImage(image.get('url'), imageFile)
                    if poster: self.saveExtra(movieId, 'poster_mid', poster)
                    hasPosterMid = True
                if image.get('type') == 'poster' and image.get('size') == 'thumb' and not hasPosterThumb:
                    poster = self.theMovieDb.saveImage(image.get('url'), imageFile)
                    if poster: self.saveExtra(movieId, 'poster_thumb', poster)
                    hasPosterThumb = True

            handle.close()

    def saveExtra(self, id, name, value):

        exists = Db.query(MovieExtra).filter(and_(MovieExtra.movieId == id, MovieExtra.name == name)).first()
        if not exists:
            exists = MovieExtra()
            Db.add(exists)

        exists.movieId = id
        exists.name = name
        exists.value = value
        Db.flush()
