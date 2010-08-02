import logging
from app.lib.plugin.bones import Bones
from library.imdb import IMDb

log = logging.getLogger(__name__)

class imdb(Bones):
    """Api for IMDB"""

    def postConstruct_(self):
        #MovieBase.__init__(self, config)
        self.loadConfig(self.name)


    def find(self, q, limit = 8, alternative = True):
        ''' Find movie by name '''

        log.info('IMDB - Searching for movie: %s', q)

        r = self.p.search_movie(q)

        return self.toResults(r, limit)

    def toResults(self, r, limit = 8, one = False):
        results = []

        if one:
            new = self.feedItem()
            new.imdb = 'tt' + r.movieID
            new.name = self.toSaveString(r['title'])
            new.year = r['year']

            return new
        else :
            nr = 0
            for movie in r:
                new = self.feedItem()
                new.imdb = 'tt' + movie.movieID
                new.name = self.toSaveString(movie['title'])
                new.year = movie['year']

                results.append(new)
                nr += 1
                if nr == limit:
                    break

            return results


    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''

        return []


    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''

        log.info('IMDB - Searching for movie: %s', str(id))

        r = self.p.get_movie(id.replace('tt', ''))
        return self.toResults(r, one = True)

    def getInfo(self):
        return {
                'name' : 'IMDB Proviver',
                'author' : 'Ruud & alshain',
                'version' : '0.1'
        }
