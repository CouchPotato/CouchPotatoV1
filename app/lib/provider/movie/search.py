from app.lib.provider.movie.sources.theMovieDb import theMovieDb
from app.lib.provider.movie.sources.imdbWrapper import imdbWrapper

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

