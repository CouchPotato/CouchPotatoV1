from app.core import getLogger
from app.lib.bones import PluginBones
from app.lib.rss import Rss
from library.imdb import IMDb
import uuid

log = getLogger(__name__)

class imdb(PluginBones, Rss):
    """API wrapper for IMDB"""

    def _identify(self):
        return uuid.UUID('56d34817-cd5f-473b-a7c4-d835e191a5ce')

    def postConstruct(self):
        #MovieBase.__init__(self, config)
        self._loadConfig(self.name)

        self.p = IMDb()

        self._listen('findMovieInfo', self.find)


    def find(self, e, config):
        ''' Find movie by name '''

        q = unicode(e._kwargs.get('q'))
        limit = e._kwargs.get('limit' , 8)

        log.info("IMDB - Searching for movie: " + q)

        searchResults = self.p.search_movie(q)
        results = self.toResults(searchResults, limit)

        # Add the results to the event item
        log.info('Found %s.' % results)
        e.addResults(results)

    def findById(self, id):
        ''' Find movie by TheMovieDB ID '''

        return []


    def findByImdbId(self, id):
        ''' Find movie by IMDB ID '''

        log.info('IMDB - Searching for movie: %s', str(id))

        searchResults = self.p.get_movie(id.replace('tt', ''))
        result = self.toResult(searchResults)

        log.info('Found %s.' % result)
        return result

    def toResults(self, results, limit = 8):
        limitedResults = results[:limit]
        return [self.toResult(movie) for movie in limitedResults]

    def toResult(self, r):

        new = self.feedItem()
        new.imdb = 'tt' + r.movieID
        new.name = r['title']
        new.year = r['year']

        return new

    def getInfo(self):
        return {
            'name' : 'IMDB Provider',
            'author' : 'Ruud & alshain',
            'version' : '0.1'
        }
