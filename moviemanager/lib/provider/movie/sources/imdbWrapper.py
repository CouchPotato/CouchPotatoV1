from moviemanager.lib.provider.movie.base import movieBase
from imdb import IMDb
import logging

log = logging.getLogger(__name__)

class imdbWrapper(movieBase):
    """Api for theMovieDb"""

    def __init__(self, config):
        log.info('Using IMDB provider.')

        self.p = IMDb()

    def find(self, q):
        ''' Find movie by name '''
        
        log.info('IMDB - Searching for movie: %s', q)

        r = self.p.search_movie(q)

        return self.toResults(r)
    
    def toResults(self, r):
        results = []

        for movie in r:
            new = self.feedItem()
            new.imdb = 'tt'+movie.movieID
            new.name = movie['title']
            new.year = movie['year']
            
            results.append(new)

        return results


    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''
        
        return []


    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''
        
        log.info('IMDB - Searching for movie: %s', str(id))
        
        r = self.p.get_movie(id.replace('tt',''))
        return self.toResults(r)
