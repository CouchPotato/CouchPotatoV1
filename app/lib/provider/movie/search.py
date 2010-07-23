from app.config.db import Session as Db, MovieExtra, Movie
from app.lib.provider.movie.sources.imdbWrapper import imdbWrapper
from app.lib.provider.movie.sources.theMovieDb import theMovieDb
from sqlalchemy.sql.expression import and_
import cherrypy
import os

class movieSearcher():

    sources = []
    limit = 8

    def __init__(self, config):

        self.config = config

        #config TheMovieDB
        self.theMovieDb = theMovieDb(config)
        self.sources.append(self.theMovieDb)

        #config imdb
        self.imdb = imdbWrapper(config)
        self.sources.append(self.imdb)

    def find(self, q):
        ''' Find movie by name '''

        q = unicode(q).lower()

        for source in self.sources:
            result = source.find(q, limit = 8)
            if result:
                results = []
                for r in result:
                    results.append(self.checkResult(r))
                return results

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

        movieId = movie.id
        theMovieDbId = movie.movieDb

        self.cacheExtra(theMovieDbId, overwrite)
        xmlFile = os.path.join(cherrypy.config.get('cachePath'), 'xml', str(theMovieDbId) + '.xml')
        if os.path.isfile(xmlFile):

            handle = open(xmlFile, 'r')
            movie = self.theMovieDb.getItems(handle, 'movies/movie')
            if not movie:
                return
            movie = movie[0]

            # rating
            rating = self.theMovieDb.gettextelement(movie, 'rating')
            self.saveExtra(movieId, 'rating', rating)

            overview = self.theMovieDb.gettextelement(movie, 'overview')
            if overview:
                overview = self.theMovieDb.toSaveString(overview)
                self.saveExtra(movieId, 'overview', overview)

            images = movie.findall('images/image')
            for image in images:
                if image.get('type') == 'poster' and image.get('size') == 'thumb':
                    imageFile = str(theMovieDbId) + '-' + image.get('type') + '-' + image.get('size') + '.jpg'
                    poster = self.theMovieDb.saveImage(image.get('url'), imageFile)
                    self.saveExtra(movieId, 'poster_thumb', poster)
                    break

            handle.close()

    def saveExtra(self, id, name, value):

        exists = Db.query(MovieExtra).filter(and_(MovieExtra.movieId == id, MovieExtra.name == name)).first()
        if exists:
            new = exists
        else:
            new = MovieExtra()
            Db.add(new)

        new.movieId = id
        new.name = name
        new.value = value
        Db.flush()

