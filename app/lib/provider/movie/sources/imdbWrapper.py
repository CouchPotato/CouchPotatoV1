from app.lib.provider.movie.base import movieBase
from imdb import IMDb
import logging

log = logging.getLogger(__name__)

class imdbWrapper(movieBase):
    """Api for theMovieDb"""

    def __init__(self, config):
        log.info('Using IMDB provider.')

        self.config = config

        self.p = IMDb('mobile')

    def conf(self, option):
        return self.config.get('IMDB', option)

    def find(self, q, limit = 8):
        ''' Find movie by name '''

        log.info('IMDB - Searching for movie: %s', q)

        r = self.p.search_movie(q)

        return self.toResults(r, limit)

    def toResults(self, r, limit = 8, one = False):
        results = []

        if one:
            new = self.feedItem()
            new.imdb = 'tt' + r.movieID
            new.name = r['title']
            new.year = r['year']

            return new
        else :
            nr = 0
            for movie in r:
                new = self.feedItem()
                new.imdb = 'tt' + movie.movieID
                new.name = movie['title']
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
