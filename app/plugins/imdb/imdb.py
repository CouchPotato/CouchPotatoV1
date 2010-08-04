from app.lib.bones import PluginBones
from library.imdb import IMDb
from app.core import getLogger

log = getLogger(__name__)

class imdb(PluginBones):
    """Api for IMDB"""

    def postConstruct(self):
        #MovieBase.__init__(self, config)
        self._loadConfig(self.name)

        self._listen('findMovieInfo', self.find)


    def find(self, e, config):
        ''' Find movie by name '''

        q = e._input.get('q')
        limit = e._input.get('limit' , 8)

        log.info("IMDB - Searching for movie: " + q)

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
